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
WALL_PROXIMITY_PCT = 0.03             # 3% (was 2%) — wider wall proximity

# Minimum delta acceleration ratio: current delta must exceed rolling avg by this
DELTA_ACCEL_RATIO = 1.10              # 10% above rolling avg (was 15%)

# Volume spike threshold: current volume must exceed rolling avg by this
VOLUME_SPIKE_RATIO = 1.20             # 20% above rolling avg

# Minimum wall GEX to consider
MIN_WALL_GEX = 500000

# Price must be above rolling mean for squeeze confirmation
PRICE_ABOVE_MEAN_CONFIDENCE = 0.55    # Price in upper half of 5m window

# Min rolling window data points required
MIN_DATA_POINTS = 3                   # Fewer points needed (was 5)

# Minimum confidence threshold
MIN_CONFIDENCE = 0.25

# Stop and target parameters
STOP_BELOW_WALL_PCT = 0.008           # 0.8% below entry
TARGET_RISK_MULT = 2.0                # 2× risk for target

# v2 Gamma-Velocity params
GEX_ACCEL_RATIO = 1.10
DELTA_ACCEL_MIN = 1.05
GEX_ACCEL_MIN = 1.05
LIQUIDITY_VACUUM_DEPTH_RATIO = 0.8
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

        # === v2: GEX acceleration hard gate ===
        gex_accel = self._check_gex_acceleration(rolling_data)
        if gex_accel is None or gex_accel < GEX_ACCEL_MIN:
            logger.debug(
                "Squeeze v2: no GEX acceleration at %.2f (ratio=%.2f)",
                wall_strike, gex_accel or 0,
            )
            return None

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
                f"{'volume spike' if vol_spike else 'strong momentum'}"
            ),
            metadata={
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "distance_to_wall_pct": round(distance_pct, 4),
                "delta_acceleration_ratio": round(accel_ratio, 3),
                "direction": direction,
                "current_delta": round(wall_delta, 2),
                "volume_spike": vol_spike,
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

    def _check_volume_spike(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if volume is spiking above rolling average."""
        window = rolling_data.get(KEY_VOLUME_5M)
        if window is None or window.count < 3:
            return False

        current = window.latest
        avg = window.mean
        if current is None or avg is None or avg == 0:
            return False

        return current > avg * VOLUME_SPIKE_RATIO

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
        vol_spike: bool,
        price_trend: str,
        wall_gex: float,
        regime: str,
        net_gamma: float,
        direction: str,  # "LONG" or "SHORT"
        gex_accel: Optional[float] = None,
        iv_roc: Optional[float] = None,
        iv_roc_bonus: float = 0.0,
    ) -> float:
        """Combine all factors into a single confidence score — 8 components (was 6).

        Returns 0.0–1.0.
        """
        # 1. Proximity to wall (0.25–0.35)
        # Closer = higher confidence
        proximity_conf = 0.25 + 0.10 * (1 - distance_pct / WALL_PROXIMITY_PCT)

        # 2. Delta acceleration (0.20–0.30)
        # Higher ratio = more urgency
        accel_conf = 0.20 + 0.10 * min(1.0, (accel_ratio - 1.0) / 1.0)

        # 3. Volume spike (0.05–0.10)
        vol_conf = 0.10 if vol_spike else 0.05

        # 4. Price momentum (0.05–0.10)
        # LONG needs UP, SHORT needs DOWN
        if direction == "LONG":
            momentum_conf = 0.10 if price_trend == "UP" else 0.05
        else:
            momentum_conf = 0.10 if price_trend == "DOWN" else 0.05

        # 5. Regime alignment (0.05–0.10)
        # LONG prefers POSITIVE, SHORT prefers NEGATIVE
        # NEUTRAL/UNKNOWN gets partial 0.05 boost (was 0.0)
        if direction == "LONG":
            regime_conf = 0.10 if regime == "POSITIVE" else 0.05
        else:
            regime_conf = 0.10 if regime == "NEGATIVE" else 0.05

        # 6. Wall strength (0.0–0.05)
        wall_conf = 0.05 * min(1.0, abs(wall_gex) / 5_000_000)

        # 7. GEX acceleration (0.05–0.10)
        if gex_accel is not None:
            gex_conf = 0.05 + 0.05 * min(1.0, (gex_accel - 1.0) / 0.5)
        else:
            gex_conf = 0.05

        # 8. IV ROC bonus (0.0–0.08)
        iv_conf = iv_roc_bonus

        # Normalize each component to [0,1] and average
        norm_prox = (proximity_conf - 0.25) / (0.35 - 0.25) if 0.35 != 0.25 else 1.0
        norm_accel = (accel_conf - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_vol = (vol_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_mom = (momentum_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_regime = (regime_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_wall = wall_conf / 0.05 if 0.05 != 0 else 0.0
        norm_gex = (gex_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_iv = iv_conf / IV_CONF_BONUS if IV_CONF_BONUS != 0 else 0.0
        confidence = (norm_prox + norm_accel + norm_vol + norm_mom + norm_regime + norm_wall + norm_gex + norm_iv) / 8.0
        return min(1.0, max(0.0, confidence))
