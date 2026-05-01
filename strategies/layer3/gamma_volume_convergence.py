"""
strategies/layer3/gamma_volume_convergence.py — Gamma-Volume Convergence (GVC)

Micro-signal (1Hz) strategy: detects ignition signals where gamma/delta spikes
at specific strikes coincide with volume surges.

Logic:
    - Monitor ATM strike for simultaneous delta + gamma acceleration
    - Volume confirmation required (VolumeUp or VolumeDown)
    - Positive gamma regime required
    - Quick scalp: 5–15 min holds, 1:2 risk/reward

Entry:
    - LONG:  delta ↑ + gamma ↑ + VolumeUp spike + price rising
    - SHORT: delta ↓ + gamma ↑ + VolumeDown spike + price falling

Confidence factors:
    - Delta acceleration rate
    - Gamma spike magnitude
    - Volume spike magnitude
    - Regime alignment
    - Proximity to gamma wall
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.GammaVolumeConvergence")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Delta acceleration threshold: current total_delta must exceed rolling avg
# by this ratio (15% above rolling average)
DELTA_ACCEL_RATIO = 1.15

# Gamma spike threshold: current total_gamma must exceed rolling avg by
# this ratio (20% above rolling average)
GAMMA_SPIKE_RATIO = 1.20

# Volume spike threshold: current volume must exceed rolling avg by this
# ratio (20% above rolling average)
VOLUME_SPIKE_RATIO = 1.20

# Stop loss: 0.5% against entry
STOP_PCT = 0.005

# Take profit: 1.0% from entry (2:1 risk/reward)
TARGET_PCT = 0.010

# Minimum confidence to emit a signal
MIN_CONFIDENCE = 0.35

# Maximum confidence — micro-signals shouldn't carry max conviction
MAX_CONFIDENCE = 0.90

# Minimum data points in rolling windows before trusting signals
MIN_DATA_POINTS = 3

# Price trend confirmation thresholds (over 5m window)
PRICE_UP_THRESHOLD = 0.001       # 0.1% rise over 5m window
PRICE_DOWN_THRESHOLD = -0.001    # 0.1% drop over 5m window


class GammaVolumeConvergence(BaseStrategy):
    """
    Detects gamma/volume ignition signals.

    When delta and gamma spike simultaneously at the ATM strike AND
    volume confirms (VolumeUp or VolumeDown), that's the exact moment
    dealers are aggressively re-hedging — the ignition point for a
    gamma squeeze.

    In a positive gamma regime:
        - LONG:  accelerating delta + spiking gamma + VolumeUp + price rising
        - SHORT: accelerating delta down + spiking gamma + VolumeDown + price falling

    Exits are quick: 0.5% stop, 1.0% target, 5–15 min hold window.
    """

    strategy_id = "gamma_volume_convergence"
    layer = "layer3"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for gamma-volume convergence signals.

        Returns empty list when no ignition signal is detected.
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

        # Positive gamma regime required for both sides
        if regime != "POSITIVE":
            return []

        # Must have positive net gamma
        if net_gamma <= 0:
            return []

        signals: List[Signal] = []

        # Check LONG ignition
        long_sig = self._check_long(
            underlying_price, gex_calc, rolling_data, net_gamma, regime,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT ignition
        short_sig = self._check_short(
            underlying_price, gex_calc, rolling_data, net_gamma, regime,
        )
        if short_sig:
            signals.append(short_sig)

        return signals

    # ------------------------------------------------------------------
    # LONG entry: delta ↑ + gamma ↑ + VolumeUp + price rising
    # ------------------------------------------------------------------

    def _check_long(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
    ) -> Optional[Signal]:
        """
        Evaluate LONG ignition signal.

        Conditions:
            1. Net Gamma > 0 (already checked in evaluate)
            2. ATM delta accelerating (≥15% above rolling avg)
            3. ATM gamma spiking (≥20% above rolling avg)
            4. VolumeUp spiking (≥20% above rolling avg)
            5. Price trending UP over 5m window
        """
        # Get ATM strike
        atm_strike = self._get_atm_strike(gex_calc, price)
        if atm_strike is None:
            return None

        # Check delta acceleration
        delta_accel = self._check_delta_acceleration(rolling_data)
        if delta_accel is None or delta_accel < DELTA_ACCEL_RATIO:
            return None

        # Check gamma spike
        gamma_spike = self._check_gamma_spike(rolling_data)
        if gamma_spike is None or gamma_spike < GAMMA_SPIKE_RATIO:
            return None

        # Check VolumeUp spike
        if not self._check_volume_spike(rolling_data, "volume_up_5m"):
            return None

        # Check price trend is UP
        if self._check_price_trend(rolling_data) != "UP":
            return None

        # All conditions met — compute confidence and build signal
        confidence = self._compute_confidence(
            price, atm_strike, delta_accel, gamma_spike,
            rolling_data, "LONG", net_gamma, gex_calc,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal with quick-scalp parameters
        entry = price
        stop = entry * (1 - STOP_PCT)
        target = entry * (1 + TARGET_PCT)

        # Get wall proximity for metadata
        walls = self._safe_get_walls(gex_calc)
        call_wall_above = self._nearest_wall_above(walls, price)

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"GVC ignition: ATM {atm_strike} delta x{delta_accel:.1f}, "
                f"gamma x{gamma_spike:.1f}, VolumeUp spike, price UP"
            ),
            metadata={
                "atm_strike": atm_strike,
                "delta_acceleration_ratio": round(delta_accel, 3),
                "gamma_spike_ratio": round(gamma_spike, 3),
                "volume_up_spike": True,
                "price_trend": "UP",
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "call_wall_above": call_wall_above["strike"] if call_wall_above else None,
                "distance_to_call_wall_pct": (
                    round((call_wall_above["strike"] - price) / price, 4)
                    if call_wall_above else None
                ),
                "risk": round(entry - stop, 2),
                "risk_reward_ratio": round(
                    (target - entry) / (entry - stop), 2
                ) if (entry - stop) > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # SHORT entry: delta ↓ + gamma ↑ + VolumeDown + price falling
    # ------------------------------------------------------------------

    def _check_short(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
    ) -> Optional[Signal]:
        """
        Evaluate SHORT ignition signal.

        Conditions:
            1. Net Gamma > 0 (already checked in evaluate)
            2. ATM delta accelerating downward (ratio < 0.85)
            3. ATM gamma spiking (≥20% above rolling avg)
            4. VolumeDown spiking (≥20% above rolling avg)
            5. Price trending DOWN over 5m window
        """
        # Get ATM strike
        atm_strike = self._get_atm_strike(gex_calc, price)
        if atm_strike is None:
            return None

        # Check delta acceleration (looking for downward acceleration)
        delta_accel = self._check_delta_acceleration(rolling_data)
        if delta_accel is None:
            return None
        # For SHORT, we want delta accelerating downward:
        # ratio < 0.85 means delta dropped by 15%+ below rolling avg
        if delta_accel >= 0.85:
            return None

        # Check gamma spike (same for both directions)
        gamma_spike = self._check_gamma_spike(rolling_data)
        if gamma_spike is None or gamma_spike < GAMMA_SPIKE_RATIO:
            return None

        # Check VolumeDown spike
        if not self._check_volume_spike(rolling_data, "volume_down_5m"):
            return None

        # Check price trend is DOWN
        if self._check_price_trend(rolling_data) != "DOWN":
            return None

        # All conditions met — compute confidence and build signal
        confidence = self._compute_confidence(
            price, atm_strike, delta_accel, gamma_spike,
            rolling_data, "SHORT", net_gamma, gex_calc,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal with quick-scalp parameters
        entry = price
        stop = entry * (1 + STOP_PCT)
        target = entry * (1 - TARGET_PCT)

        # Get wall proximity for metadata
        walls = self._safe_get_walls(gex_calc)
        put_wall_below = self._nearest_wall_below(walls, price)

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"GVC ignition fade: ATM {atm_strike} delta ↓, "
                f"gamma x{gamma_spike:.1f}, VolumeDown spike, price DOWN"
            ),
            metadata={
                "atm_strike": atm_strike,
                "delta_acceleration_ratio": round(delta_accel, 3),
                "gamma_spike_ratio": round(gamma_spike, 3),
                "volume_down_spike": True,
                "price_trend": "DOWN",
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "put_wall_below": put_wall_below["strike"] if put_wall_below else None,
                "distance_to_put_wall_pct": (
                    round((price - put_wall_below["strike"]) / price, 4)
                    if put_wall_below else None
                ),
                "risk": round(stop - entry, 2),
                "risk_reward_ratio": round(
                    (entry - target) / (stop - entry), 2
                ) if (stop - entry) > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_atm_strike(gex_calc: Any, price: float) -> Optional[float]:
        """Get the nearest ATM strike from the GEX calculator."""
        try:
            return gex_calc.get_atm_strike(price)
        except Exception as exc:
            logger.debug("GVC: failed to get ATM strike: %s", exc)
            return None

    @staticmethod
    def _safe_get_walls(gex_calc: Any) -> List[Dict[str, Any]]:
        """Safely retrieve gamma walls, returning empty list on error."""
        try:
            return gex_calc.get_gamma_walls(threshold=500_000)
        except Exception as exc:
            logger.debug("GVC: failed to get gamma walls: %s", exc)
            return []

    @staticmethod
    def _check_delta_acceleration(
        rolling_data: Dict[str, Any],
    ) -> Optional[float]:
        """
        Check delta acceleration by comparing current total_delta
        to its rolling average.

        Returns ratio of current to rolling avg.
            > 1.0 = accelerating upward
            < 1.0 = accelerating downward
            None  = insufficient data
        """
        window = rolling_data.get("total_delta_5m")
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        rolling_avg = window.mean
        if rolling_avg is None or rolling_avg == 0:
            return None

        current = window.latest
        if current is None:
            return None

        return current / rolling_avg

    @staticmethod
    def _check_gamma_spike(rolling_data: Dict[str, Any]) -> Optional[float]:
        """
        Check gamma spike by comparing current total_gamma
        to its rolling average.

        Returns ratio of current to rolling avg.
            > 1.0 = spiking upward
            None  = insufficient data
        """
        window = rolling_data.get("total_gamma_5m")
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        rolling_avg = window.mean
        if rolling_avg is None or rolling_avg == 0:
            return None

        current = window.latest
        if current is None:
            return None

        return current / rolling_avg

    @staticmethod
    def _check_volume_spike(
        rolling_data: Dict[str, Any],
        key: str,
    ) -> bool:
        """
        Check if the specified volume window is spiking above
        its rolling average.

        Args:
            key: Rolling window key (e.g. "volume_up_5m", "volume_down_5m")
        """
        window = rolling_data.get(key)
        if window is None or window.count < MIN_DATA_POINTS:
            return False

        current = window.latest
        avg = window.mean
        if current is None or avg is None or avg == 0:
            return False

        return current > avg * VOLUME_SPIKE_RATIO

    @staticmethod
    def _check_price_trend(rolling_data: Dict[str, Any]) -> str:
        """
        Check price trend from the rolling window.

        Returns "UP", "DOWN", or "FLAT".
        """
        window = rolling_data.get("price_5m")
        if window is None:
            return "FLAT"

        # Use the trend property from RollingWindow
        trend = window.trend
        if trend != "FLAT":
            return trend

        # Fallback: check change_pct directly
        if window.change_pct is not None:
            if window.change_pct > PRICE_UP_THRESHOLD:
                return "UP"
            elif window.change_pct < PRICE_DOWN_THRESHOLD:
                return "DOWN"

        return "FLAT"

    def _compute_confidence(
        self,
        price: float,
        atm_strike: float,
        delta_accel: float,
        gamma_spike: float,
        rolling_data: Dict[str, Any],
        direction: str,
        net_gamma: float,
        gex_calc: Any,
    ) -> float:
        """
        Combine all factors into a single confidence score.

        Factors:
            1. Delta acceleration magnitude  (0.20–0.30)
            2. Gamma spike magnitude          (0.20–0.30)
            3. Volume spike confirmation      (0.10–0.15)
            4. Regime alignment               (0.10–0.15)
            5. Proximity to gamma wall        (0.05–0.10)

        Returns 0.0–MAX_CONFIDENCE.
        """
        # 1. Delta acceleration component (0.20–0.30)
        if delta_accel >= 1.0:
            # Upward acceleration (LONG)
            delta_conf = 0.20 + 0.10 * min(1.0, (delta_accel - 1.0) / 1.0)
        else:
            # Downward acceleration (SHORT)
            deviation = 1.0 - delta_accel
            delta_conf = 0.20 + 0.10 * min(1.0, deviation / 0.30)

        # 2. Gamma spike component (0.20–0.30)
        gamma_conf = 0.20 + 0.10 * min(1.0, (gamma_spike - 1.0) / 1.0)

        # 3. Volume spike component (0.10–0.15)
        vol_key = (
            "volume_up_5m" if direction == "LONG" else "volume_down_5m"
        )
        vol_window = rolling_data.get(vol_key)
        if (
            vol_window is not None
            and vol_window.latest is not None
            and vol_window.mean is not None
            and vol_window.mean != 0
        ):
            vol_ratio = vol_window.latest / vol_window.mean
            vol_conf = 0.10 + 0.05 * min(1.0, (vol_ratio - 1.0) / 1.0)
        else:
            vol_conf = 0.10  # baseline if volume data insufficient

        # 4. Regime alignment (0.10–0.15)
        # Stronger net_gamma = higher confidence
        regime_conf = 0.10 + 0.05 * min(1.0, abs(net_gamma) / 5_000_000)

        # 5. Proximity to gamma wall (0.05–0.10)
        wall_conf = self._wall_proximity_confidence(price, direction, gex_calc)

        # Normalize each component to [0,1] and average
        norm_delta = (delta_conf - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_gamma = (gamma_conf - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_vol = (vol_conf - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        norm_regime = (regime_conf - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        norm_wall = (wall_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        confidence = (norm_delta + norm_gamma + norm_vol + norm_regime + norm_wall) / 5.0
        return min(MAX_CONFIDENCE, max(0.0, confidence))

    def _wall_proximity_confidence(
        self,
        price: float,
        direction: str,
        gex_calc: Any,
    ) -> float:
        """
        Compute confidence bonus from proximity to relevant gamma wall.

        For LONG:  closer to call wall above = higher confidence.
        For SHORT: closer to put wall below = higher confidence.
        """
        walls = self._safe_get_walls(gex_calc)
        if not walls:
            return 0.05  # baseline when no walls

        if direction == "LONG":
            wall = self._nearest_wall_above(walls, price)
        else:
            wall = self._nearest_wall_below(walls, price)

        if wall is None:
            return 0.05  # baseline when no relevant wall

        wall_strike = wall["strike"]
        distance_pct = abs(wall_strike - price) / price

        # Closer = higher confidence (0.05–0.10)
        # At 0% distance = 0.10, at 2% distance = 0.05
        if distance_pct <= 0:
            return 0.10
        elif distance_pct >= 0.02:
            return 0.05
        else:
            return 0.10 - 0.05 * (distance_pct / 0.02)

    @staticmethod
    def _nearest_wall_above(
        walls: List[Dict[str, Any]], price: float,
    ) -> Optional[Dict[str, Any]]:
        """Find the nearest gamma wall above the current price."""
        above = [w for w in walls if w["strike"] > price]
        if not above:
            return None
        return min(above, key=lambda w: w["strike"])

    @staticmethod
    def _nearest_wall_below(
        walls: List[Dict[str, Any]], price: float,
    ) -> Optional[Dict[str, Any]]:
        """Find the nearest gamma wall below the current price."""
        below = [w for w in walls if w["strike"] < price]
        if not below:
            return None
        return max(below, key=lambda w: w["strike"])
