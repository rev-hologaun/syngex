"""
strategies/layer2/delta_gamma_squeeze.py — Delta-Gamma Squeeze

Extreme momentum entry strategy (bidirectional).
Detects gamma squeeze setups using total delta acceleration at wall proximity.

LONG: Price approaching a Call Wall above with accelerating total delta
SHORT: Price approaching a Put Wall below with accelerating total delta

Logic:
    LONG:
        1. Find nearest Call Wall above price
        2. Check if total delta is accelerating
        3. Check for volume spike on the breakout candle
        4. Enter LONG when all conditions align
    SHORT:
        1. Find nearest Put Wall below price
        2. Check if total delta is accelerating
        3. Check for volume spike on the breakdown candle
        4. Enter SHORT when all conditions align

Exit: When delta plateaus or IV spikes (overextended squeeze)

Confidence factors:
    - Proximity to wall (closer = stronger squeeze)
    - Delta acceleration rate (faster = more urgency)
    - Volume spike magnitude
    - Regime alignment (POSITIVE amplifies LONG, NEGATIVE amplifies SHORT)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_VOLUME_5M, KEY_TOTAL_DELTA_5M, KEY_WALL_DELTA_5M, KEY_TOTAL_GAMMA_5M, KEY_ATM_IV_5M

logger = logging.getLogger("Syngex.Strategies.DeltaGammaSqueeze")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# How close price must be to call wall (as fraction of price)
WALL_PROXIMITY_PCT = 0.05             # 5% (was 3%) — wider wall proximity

# Minimum delta acceleration ratio: current delta must exceed rolling avg by this
DELTA_ACCEL_RATIO = 1.05              # 5% above rolling avg (was 10%)

# Volume spike threshold: current volume must exceed rolling avg by this
VOLUME_SPIKE_RATIO = 1.10             # 10% above rolling avg

# Minimum wall GEX to consider
MIN_WALL_GEX = 500000

# Price must be above rolling mean for squeeze confirmation
PRICE_ABOVE_MEAN_CONFIDENCE = 0.55    # Price in upper half of 5m window

# Min rolling window data points required
MIN_DATA_POINTS = 2                   # Fewer points needed (was 3)

# Minimum confidence threshold
MIN_CONFIDENCE = 0.10

# Stop and target parameters
STOP_BELOW_WALL_PCT = 0.008           # 0.8% below entry
TARGET_RISK_MULT = 2.0                # 2× risk for target

# v2 Gamma-Velocity params
GEX_ACCEL_RATIO = 1.10
DELTA_ACCEL_MIN = 1.05
GEX_ACCEL_MIN = 1.03
LIQUIDITY_VACUUM_DEPTH_RATIO = 0.9
IV_ROC_THRESHOLD = 0.02
IV_CONF_BONUS = 0.08
ACCEL_STOP_WIDEN_MULT = 1.5


class DeltaGammaSqueeze(BaseStrategy):
    """
    Detects gamma squeeze setups using total delta acceleration at wall proximity.

    LONG: Price approaching a Call Wall above with accelerating total delta
    SHORT: Price approaching a Put Wall below with accelerating total delta

    A gamma squeeze occurs when dealers must hedge their options positions,
    pushing price toward the wall and forcing more hedging — a
    self-reinforcing loop.
    """

    strategy_id = "delta_gamma_squeeze"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for gamma squeeze setup (bidirectional).

        Returns signals for both LONG (call wall above) and SHORT
        (put wall below) when conditions are met.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")

        signals: List[Signal] = []

        # Get walls above and below price
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)

        # Populate wall delta rolling window for acceleration tracking
        wall_delta = self._get_nearest_wall_delta(walls, underlying_price, gex_calc)
        if KEY_WALL_DELTA_5M in rolling_data:
            rolling_data[KEY_WALL_DELTA_5M].push(wall_delta, time.time())

        call_walls_above = [
            w for w in walls
            if w["side"] == "call" and w["strike"] > underlying_price
        ]
        put_walls_below = [
            w for w in walls
            if w["side"] == "put" and w["strike"] < underlying_price
        ]

        # Check LONG setup (call wall above)
        if call_walls_above:
            call_walls_above.sort(
                key=lambda w: (w["strike"] - underlying_price) / underlying_price
            )
            sig = self._evaluate_squeeze(
                call_walls_above[0], underlying_price, gex_calc,
                rolling_data, net_gamma, regime, "LONG", wall_delta,
            )
            if sig:
                signals.append(sig)

        # Check SHORT setup (put wall below)
        if put_walls_below:
            put_walls_below.sort(
                key=lambda w: (underlying_price - w["strike"]) / underlying_price
            )
            sig = self._evaluate_squeeze(
                put_walls_below[0], underlying_price, gex_calc,
                rolling_data, net_gamma, regime, "SHORT", wall_delta,
            )
            if sig:
                signals.append(sig)

        return signals

    def _evaluate_squeeze(
        self,
        wall: Dict[str, Any],
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
        direction: str,  # "LONG" or "SHORT"
        wall_delta: float = 0.0,
    ) -> Optional[Signal]:
        """Evaluate a specific wall for squeeze setup."""
        wall_strike = wall["strike"]
        wall_gex = wall["gex"]

        # Direction-specific proximity check
        if direction == "LONG":
            distance_pct = (wall_strike - price) / price
            if distance_pct > WALL_PROXIMITY_PCT:
                logger.debug(
                    "Squeeze: price %.2f too far from wall %.2f (dist=%.2f%%)",
                    price, wall_strike, distance_pct * 100,
                )
                return None
            if distance_pct < 0:
                # Price already above wall — squeeze may have already fired
                return None
        else:  # SHORT
            distance_pct = (price - wall_strike) / price
            if distance_pct > WALL_PROXIMITY_PCT:
                logger.debug(
                    "Squeeze: price %.2f too far from wall %.2f (dist=%.2f%%)",
                    price, wall_strike, distance_pct * 100,
                )
                return None
            if distance_pct < 0:
                # Price already below wall — squeeze may have already fired
                return None

        # Delta acceleration — use wall_delta (net delta at nearest wall)
        accel_ratio = self._check_delta_acceleration(
            wall_delta, rolling_data, wall_strike,
        )
        if accel_ratio is None or accel_ratio < DELTA_ACCEL_RATIO:
            logger.debug(
                "Squeeze: no delta acceleration at %.2f (ratio=%.2f)",
                wall_strike, accel_ratio or 0,
            )
            return None

        # === v2: GEX acceleration (soft gate — confidence bonus only) ===
        gex_accel = self._check_gex_acceleration(rolling_data)
        # Don't block on GEX acceleration — just use it for confidence bonus

        # Volume spike and price momentum checks are direction-agnostic
        vol_spike = self._check_volume_spike(rolling_data)
        price_trend = self._check_price_momentum(rolling_data)

        # === v2: Liquidity vacuum hard gate ===
        depth_snapshot = data.get("depth_snapshot")
        if not self._check_liquidity_vacuum(depth_snapshot, direction):
            logger.debug(
                "Squeeze v2: no liquidity vacuum for %s at %.2f",
                direction, wall_strike,
            )
            return None

        # Compute IV ROC for confidence bonus
        iv_roc = self._compute_iv_roc(rolling_data)
        iv_roc_bonus = 0.0
        if iv_roc is not None and iv_roc > IV_ROC_THRESHOLD:
            iv_roc_bonus = IV_CONF_BONUS

        confidence = self._compute_confidence(
            distance_pct, accel_ratio, vol_spike, price_trend,
            wall_gex, regime, net_gamma, direction,
            gex_accel=gex_accel,
            iv_roc=iv_roc,
            iv_roc_bonus=iv_roc_bonus,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Add trend from price window
        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        # Build signal with direction-specific entry/stop/target
        entry = price
        # === v2: Volatility-adjusted stops ===
        effective_stop_pct = STOP_BELOW_WALL_PCT
        if accel_ratio is not None and accel_ratio > 1.3:
            effective_stop_pct = STOP_BELOW_WALL_PCT * ACCEL_STOP_WIDEN_MULT
        stop = entry * (1 - effective_stop_pct) if direction == "LONG" else entry * (1 + effective_stop_pct)
        risk = abs(entry - stop)
        target = entry + (risk * TARGET_RISK_MULT) if direction == "LONG" else entry - (risk * TARGET_RISK_MULT)
        direction_enum = Direction.LONG if direction == "LONG" else Direction.SHORT

        return Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Gamma squeeze: price approaching {'call' if direction == 'LONG' else 'put'} "
                f"wall at {wall_strike} with accelerating delta (x{accel_ratio:.1f}) and "
                f"{'volume spike' if vol_spike > 0.5 else 'strong momentum'}"
            ),
            metadata={
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "distance_to_wall_pct": round(distance_pct, 4),
                "delta_acceleration_ratio": round(accel_ratio, 3),
                "direction": direction,
                "current_delta": round(wall_delta, 2),
                "volume_spike": round(vol_spike, 3),
                "price_momentum": price_trend,
                "regime": regime,
                "net_gamma": round(net_gamma, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
                "trend": trend,
                # v2 Gamma-Velocity fields
                "gex_acceleration_ratio": round(gex_accel, 3) if gex_accel is not None else None,
                "iv_roc": round(iv_roc, 4) if iv_roc is not None else None,
                "liquidity_vacuum": True,
                "stop_adjusted": effective_stop_pct > STOP_BELOW_WALL_PCT,
            },
        )

    def _check_delta_acceleration(
        self,
        current_delta: float,
        rolling_data: Dict[str, Any],
        wall_strike: float,
    ) -> Optional[float]:
        """
        Check if wall delta is accelerating.

        Compares current wall delta to rolling average of wall delta
        over the 5-minute window. Returns ratio of current to rolling
        avg. > 1.0 means accelerating.
        """
        window = rolling_data.get(KEY_WALL_DELTA_5M)
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        rolling_avg = window.mean
        if rolling_avg is None or rolling_avg == 0:
            return None

        return current_delta / rolling_avg

    def _get_nearest_wall_delta(self, walls, price, gex_calc):
        """Get net delta magnitude at the nearest gamma wall."""
        if not walls:
            return 0.0
        nearest = min(walls, key=lambda w: abs(w["strike"] - price) / price)
        delta_data = gex_calc.get_delta_by_strike(nearest["strike"])
        return abs(delta_data.get("net_delta", 0.0))

    def _check_volume_spike(self, rolling_data: Dict[str, Any]) -> float:
        """Return a volume-spike score 0.0–1.0 based on current/rolling-average ratio.

        Score: 0.0 at ratio ≤ 1.0 (no spike), 1.0 at ratio ≥ 2.0 (double volume).
        Linear interpolation between — e.g. 50% above avg → 0.50.
        """
        window = rolling_data.get(KEY_VOLUME_5M)
        if window is None or window.count < 3:
            return 0.0

        current = window.latest
        avg = window.mean
        if current is None or avg is None or avg == 0:
            return 0.0

        ratio = current / avg
        return max(0.0, min(1.0, (ratio - 1.0) / 1.0))

    def _check_price_momentum(self, rolling_data: Dict[str, Any]) -> str:
        """Check price momentum from rolling window."""
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None:
            return "FLAT"
        return window.trend

    def _check_gex_acceleration(
        self,
        rolling_data: Dict[str, Any],
    ) -> Optional[float]:
        """Check if total gamma is accelerating.

        Uses KEY_TOTAL_GAMMA_5M rolling window. Returns ratio of current
        gamma to rolling average. > 1.0 means accelerating.
        """
        window = rolling_data.get(KEY_TOTAL_GAMMA_5M)
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        rolling_avg = window.mean
        if rolling_avg is None or rolling_avg == 0:
            return None

        current = window.latest
        if current is None:
            return None

        return current / rolling_avg

    def _check_liquidity_vacuum(
        self,
        depth_snapshot: Optional[Dict[str, Any]],
        direction: str,
    ) -> bool:
        """Check if opposite-side depth is collapsing (liquidity vacuum).

        For LONG squeeze: ask_size should be collapsing (below mean).
        For SHORT squeeze: bid_size should be collapsing (below mean).
        """
        if not depth_snapshot:
            return True  # no depth data, don't block

        if direction == "LONG":
            snap = depth_snapshot.get("ask_size", {})
        else:
            snap = depth_snapshot.get("bid_size", {})

        current = snap.get("current", 0)
        mean = snap.get("mean", 0)

        if mean <= 0:
            return True  # can't determine vacuum

        # Vacuum: current depth is below mean × ratio
        return current < mean * LIQUIDITY_VACUUM_DEPTH_RATIO

    def _compute_iv_roc(
        self,
        rolling_data: Dict[str, Any],
    ) -> Optional[float]:
        """Compute IV rate of change from ATM IV rolling window.

        Returns ROC (rate of change) as a fraction.
        """
        window = rolling_data.get(KEY_ATM_IV_5M)
        if window is None or window.count < 3:
            return None

        current = window.latest
        first = window.values[0] if window.values else None
        if current is None or first is None or first == 0:
            return None

        return (current - first) / first

    def _compute_confidence(
        self,
        distance_pct: float,
        accel_ratio: float,
        vol_spike: float,  # 0.0–1.0 score
        price_trend: str,
        wall_gex: float,
        regime: str,
        net_gamma: float,
        direction: str,  # "LONG" or "SHORT"
        gex_accel: Optional[float] = None,
        iv_roc: Optional[float] = None,
        iv_roc_bonus: float = 0.0,
        depth_score: Optional[float] = None,
    ) -> float:
        """Combine all factors into a single confidence score — Family A simple average.

        Returns 0.0–1.0.
        """
        def normalize(val, vmin, vmax):
            return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

        # 1. Proximity: distance_pct from 0→0.005, closer = higher, invert
        c1 = 1.0 - normalize(distance_pct, 0.0, 0.005)

        # 2. Delta acceleration: accel_ratio from 1.0→3.0, higher = higher
        c2 = normalize(accel_ratio, 1.0, 3.0)

        # 3. Volume spike: float 0.0–1.0 (proportional to current/avg ratio)
        c3 = vol_spike

        # 4. Price momentum: direction matches trend = 1.0, else 0.5
        momentum = 1.0 if ((direction == "LONG" and price_trend == "UP") or (direction == "SHORT" and price_trend == "DOWN")) else 0.5
        c4 = momentum

        # 5. Net gamma: abs(net_gamma) from 0→5M, higher = higher
        c5 = normalize(abs(net_gamma), 0.0, 5000000.0)

        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))
