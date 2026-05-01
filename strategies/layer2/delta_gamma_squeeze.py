"""
strategies/layer2/delta_gamma_squeeze.py — Delta-Gamma Squeeze

Extreme momentum entry strategy. Detects when price is being pushed toward
a Call Wall while delta at that strike accelerates non-linearly — a classic
gamma squeeze setup where dealers must buy the underlying to hedge.

Logic:
    1. Find nearest Call Wall above price
    2. Check if delta at that strike is accelerating (current > rolling avg)
    3. Check for volume spike on the breakout candle
    4. Enter LONG when all conditions align

Exit: When delta plateaus or IV spikes (overextended squeeze)

Confidence factors:
    - Proximity to call wall (closer = stronger squeeze)
    - Delta acceleration rate (faster = more urgency)
    - Volume spike magnitude
    - Regime alignment (POSITIVE regime amplifies squeeze)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.DeltaGammaSqueeze")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# How close price must be to call wall (as fraction of price)
CALL_WALL_PROXIMITY_PCT = 0.02        # 2% (was 1.5%) — wider wall proximity

# Minimum delta acceleration ratio: current delta must exceed rolling avg by this
DELTA_ACCEL_RATIO = 1.15              # 15% above rolling avg (was 25%)

# Volume spike threshold: current volume must exceed rolling avg by this
VOLUME_SPIKE_RATIO = 1.2              # 20% above rolling avg (was 40%)

# Minimum wall GEX to consider
MIN_WALL_GEX = 500000

# Price must be above rolling mean for squeeze confirmation
PRICE_ABOVE_MEAN_CONFIDENCE = 0.55    # Price in upper half of 5m window

# Min rolling window data points required
MIN_DATA_POINTS = 3                   # Fewer points needed (was 5)

# Stop and target parameters
STOP_BELOW_WALL_PCT = 0.008           # 0.8% below entry
TARGET_RISK_MULT = 2.0                # 2× risk for target


class DeltaGammaSqueeze(BaseStrategy):
    """
    Detects gamma squeeze setups: price approaching a Call Wall
    with accelerating delta and volume spike.

    A gamma squeeze occurs when dealers selling calls must buy the
    underlying to hedge, pushing price higher, which forces more
    hedging — a self-reinforcing loop.
    """

    strategy_id = "delta_gamma_squeeze"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for gamma squeeze setup.

        Returns empty list when conditions not met.
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

        # Get call walls above price
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
        call_walls_above = [
            w for w in walls
            if w["side"] == "call" and w["strike"] > underlying_price
        ]

        if not call_walls_above:
            return []

        # Sort by proximity — nearest wall first
        call_walls_above.sort(
            key=lambda w: (w["strike"] - underlying_price) / underlying_price
        )

        nearest_wall = call_walls_above[0]
        return self._evaluate_squeeze(
            nearest_wall, underlying_price, gex_calc,
            rolling_data, net_gamma, regime,
        )

    def _evaluate_squeeze(
        self,
        wall: Dict[str, Any],
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
    ) -> List[Signal]:
        """Evaluate a specific call wall for squeeze setup."""
        wall_strike = wall["strike"]
        wall_gex = wall["gex"]

        # Check proximity to wall
        distance_pct = (wall_strike - price) / price
        if distance_pct > CALL_WALL_PROXIMITY_PCT:
            logger.debug(
                "Squeeze: price %.2f too far from wall %.2f (dist=%.2f%%)",
                price, wall_strike, distance_pct * 100,
            )
            return []
        if distance_pct < 0:
            # Price already above wall — squeeze may have already fired
            return []

        # Check delta acceleration at wall strike
        delta_data = gex_calc.get_delta_by_strike(wall_strike)
        call_delta = delta_data.get("call_delta", 0)

        accel_ratio = self._check_delta_acceleration(
            call_delta, rolling_data, wall_strike, "calls",
        )
        if accel_ratio is None or accel_ratio < DELTA_ACCEL_RATIO:
            logger.debug(
                "Squeeze: no delta acceleration at %.2f (ratio=%.2f)",
                wall_strike, accel_ratio or 0,
            )
            return []

        # Check volume spike
        vol_spike = self._check_volume_spike(rolling_data)

        # Check price momentum — price should be rising
        price_trend = self._check_price_momentum(rolling_data)

        # Combine confidence factors
        confidence = self._compute_confidence(
            distance_pct, accel_ratio, vol_spike, price_trend,
            wall_gex, regime, net_gamma,
        )
        if confidence < 0.35:
            return []

        # Build signal
        entry = price
        stop = entry * (1 - STOP_BELOW_WALL_PCT)
        risk = entry - stop
        target = entry + (risk * TARGET_RISK_MULT)

        return [Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Gamma squeeze: price approaching call wall at {wall_strike} "
                f"with accelerating delta (x{accel_ratio:.1f}) and "
                f"{'volume spike' if vol_spike else 'strong momentum'}"
            ),
            metadata={
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "distance_to_wall_pct": round(distance_pct, 4),
                "delta_acceleration_ratio": round(accel_ratio, 3),
                "current_call_delta": round(call_delta, 2),
                "volume_spike": vol_spike,
                "price_momentum": price_trend,
                "regime": regime,
                "net_gamma": round(net_gamma, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round((target - entry) / risk, 2) if risk > 0 else 0,
            },
        )]

    def _check_delta_acceleration(
        self,
        current_delta: float,
        rolling_data: Dict[str, Any],
        strike: float,
        side: str,
    ) -> Optional[float]:
        """
        Check if delta at a strike is accelerating.

        Compares current delta to rolling average. Returns ratio of
        current to rolling avg. > 1.0 means accelerating.
        """
        key = f"delta_{side}_5m"
        window = rolling_data.get(key)
        if window is None or window.count < MIN_DATA_POINTS:
            # Fallback: use total_delta rolling window
            window = rolling_data.get("total_delta_5m")
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        rolling_avg = window.mean
        if rolling_avg is None or rolling_avg == 0:
            return None

        return current_delta / rolling_avg

    def _check_volume_spike(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if volume is spiking above rolling average."""
        window = rolling_data.get("volume_5m")
        if window is None or window.count < 3:
            return False

        current = window.latest
        avg = window.mean
        if current is None or avg is None or avg == 0:
            return False

        return current > avg * VOLUME_SPIKE_RATIO

    def _check_price_momentum(self, rolling_data: Dict[str, Any]) -> str:
        """Check price momentum from rolling window."""
        window = rolling_data.get("price_5m")
        if window is None:
            return "FLAT"
        return window.trend

    def _compute_confidence(
        self,
        distance_pct: float,
        accel_ratio: float,
        vol_spike: bool,
        price_trend: str,
        wall_gex: float,
        regime: str,
        net_gamma: float,
    ) -> float:
        """
        Combine all factors into a single confidence score.

        Returns 0.0–1.0.
        """
        # 1. Proximity to wall (0.25–0.35)
        # Closer = higher confidence
        proximity_conf = 0.25 + 0.10 * (1 - distance_pct / CALL_WALL_PROXIMITY_PCT)

        # 2. Delta acceleration (0.20–0.30)
        # Higher ratio = more urgency
        accel_conf = 0.20 + 0.10 * min(1.0, (accel_ratio - 1.0) / 1.0)

        # 3. Volume spike (0.05–0.10)
        vol_conf = 0.10 if vol_spike else 0.05

        # 4. Price momentum (0.05–0.10)
        momentum_conf = 0.10 if price_trend == "UP" else 0.05

        # 5. Regime alignment (0.0–0.10)
        regime_conf = 0.10 if regime == "POSITIVE" else 0.0

        # 6. Wall strength (0.0–0.05)
        wall_conf = 0.05 * min(1.0, abs(wall_gex) / 5_000_000)

        # Normalize each component to [0,1] and average
        norm_prox = (proximity_conf - 0.25) / (0.35 - 0.25) if 0.35 != 0.25 else 1.0
        norm_accel = (accel_conf - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_vol = (vol_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_mom = (momentum_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_regime = regime_conf / 0.10 if 0.10 != 0 else 0.0
        norm_wall = wall_conf / 0.05 if 0.05 != 0 else 0.0
        confidence = (norm_prox + norm_accel + norm_vol + norm_mom + norm_regime + norm_wall) / 6.0
        return min(1.0, max(0.0, confidence))
