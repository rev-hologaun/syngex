"""
strategies/layer2/delta_iv_divergence.py — Delta-IV Divergence

Detects sentiment shifts where delta and IV diverge:
- LONG: delta rising + IV falling → bullish accumulation
- SHORT: delta falling + IV rising → bearish positioning

The divergence between conviction (delta) and fear (IV) signals
smart money positioning before the crowd catches on.

Logic:
    LONG:
        1. ATM delta trend is UP (bullish conviction building)
        2. ATM IV trend is DOWN (fear decreasing)
        3. Divergence = smart money buying while fear is low
        4. Enter LONG for mean-reversion upward move

    SHORT:
        1. ATM delta trend is DOWN (bearish conviction building)
        2. ATM IV trend is UP (fear increasing)
        3. Divergence = smart money shorting while fear is high
        4. Enter SHORT for mean-reversion downward move

Confidence factors:
    - Divergence strength (how opposite the trends are)
    - Data quality (more points = more reliable)
    - Gamma context (strong gamma supports the move)
    - Regime alignment (direction-aware)
    - Trend momentum (how strong each trend is individually)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_ATM_DELTA_5M, KEY_ATM_IV_5M

logger = logging.getLogger("Syngex.Strategies.DeltaIVDivergence")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Min data points for both delta and IV windows
MIN_DATA_POINTS = 5

# Minimum divergence strength (combined z-score magnitude)
MIN_DIVERSION_STRENGTH = 0.3

# Minimum confidence to emit a signal
MIN_CONFIDENCE = 0.35

# Stop distance
STOP_PCT = 0.008  # 0.8%

# Target: 2x risk
TARGET_RISK_MULT = 2.0


class DeltaIVDivergence(BaseStrategy):
    """
    Detects delta-IV divergence for sentiment shift signals.

    LONG: delta rising + IV falling → bullish accumulation
    SHORT: delta falling + IV rising → bearish positioning
    """

    strategy_id = "delta_iv_divergence"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """Evaluate current state for delta-IV divergence."""
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")

        signals: List[Signal] = []

        # Check LONG setup: delta UP + IV DOWN
        long_sig = self._check_divergence(
            rolling_data, underlying_price, net_gamma, regime, "LONG",
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT setup: delta DOWN + IV UP
        short_sig = self._check_divergence(
            rolling_data, underlying_price, net_gamma, regime, "SHORT",
        )
        if short_sig:
            signals.append(short_sig)

        return signals

    def _check_divergence(
        self,
        rolling_data: Dict[str, Any],
        price: float,
        net_gamma: float,
        regime: str,
        direction: str,  # "LONG" or "SHORT"
    ) -> Optional[Signal]:
        """Check for delta-IV divergence and return signal or None."""
        delta_window = rolling_data.get(KEY_ATM_DELTA_5M)
        iv_window = rolling_data.get(KEY_ATM_IV_5M)

        # Both windows need sufficient data
        if delta_window is None or iv_window is None:
            return None
        if delta_window.count < MIN_DATA_POINTS or iv_window.count < MIN_DATA_POINTS:
            return None

        # Check trend alignment
        delta_trend = delta_window.trend  # "UP", "DOWN", or "FLAT"
        iv_trend = iv_window.trend

        if direction == "LONG":
            # LONG: delta UP + IV DOWN
            if delta_trend != "UP" or iv_trend != "DOWN":
                return None
        else:
            # SHORT: delta DOWN + IV UP
            if delta_trend != "DOWN" or iv_trend != "UP":
                return None

        # Compute divergence strength from z-scores
        delta_z = delta_window.z_score or 0.0
        iv_z = iv_window.z_score or 0.0

        if direction == "LONG":
            # LONG: delta z should be positive, iv z should be negative
            divergence_strength = min(delta_z, abs(iv_z)) / 2.0
        else:
            # SHORT: delta z should be negative, iv z should be positive
            divergence_strength = min(abs(delta_z), iv_z) / 2.0

        divergence_strength = max(0.0, divergence_strength)
        if divergence_strength < MIN_DIVERSION_STRENGTH:
            return None

        # Compute confidence
        confidence = self._compute_confidence(
            divergence_strength, delta_z, iv_z,
            net_gamma, regime, direction,
            delta_window, iv_window,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        entry = price
        # LONG: stop below entry, target above. SHORT: stop above entry, target below.
        reverse = 1 if direction == "LONG" else -1
        stop = entry * (1 - STOP_PCT * reverse)  # LONG: below, SHORT: above
        risk = abs(entry - stop)
        target = entry + (risk * TARGET_RISK_MULT * reverse)  # LONG: above, SHORT: below

        return Signal(
            direction=Direction.LONG if direction == "LONG" else Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Delta-IV divergence: delta {delta_trend} + IV {iv_trend} "
                f"({divergence_strength:.2f} strength) — {direction} signal"
            ),
            metadata={
                "direction": direction,
                "delta_trend": delta_trend,
                "iv_trend": iv_trend,
                "divergence_strength": round(divergence_strength, 3),
                "delta_z": round(delta_z, 3),
                "iv_z": round(iv_z, 3),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
            },
        )

    def _compute_confidence(
        self,
        divergence_strength: float,
        delta_z: float,
        iv_z: float,
        net_gamma: float,
        regime: str,
        direction: str,
        delta_window: Any,
        iv_window: Any,
    ) -> float:
        """
        Combine divergence factors into confidence score.
        Returns 0.0–1.0.
        """
        # 1. Divergence strength (0.20–0.30)
        div_conf = 0.20 + 0.10 * min(1.0, divergence_strength / 2.0)

        # 2. Data quality (0.10–0.15)
        min_count = min(delta_window.count, iv_window.count)
        data_conf = 0.10 + 0.05 * min(1.0, (min_count - MIN_DATA_POINTS) / 10.0)

        # 3. Gamma context (0.10–0.15)
        # Strong gamma supports the move (both directions)
        gamma_conf = 0.10 + 0.05 * min(1.0, abs(net_gamma) / 1000000)

        # 4. Regime alignment (0.05–0.10) — direction-aware
        if direction == "LONG":
            regime_conf = 0.10 if regime == "POSITIVE" else 0.05
        else:
            regime_conf = 0.10 if regime == "NEGATIVE" else 0.05

        # 5. Trend momentum (0.10–0.15) — both trends should be strong
        trend_momentum = min(abs(delta_z), abs(iv_z)) / 2.0
        momentum_conf = 0.10 + 0.05 * min(1.0, trend_momentum / 2.0)

        # Normalize each component to [0,1] and average
        norm_div = (div_conf - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_data = (data_conf - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        norm_gamma = (gamma_conf - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        norm_regime = (regime_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_momentum = (momentum_conf - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0

        confidence = (norm_div + norm_data + norm_gamma + norm_regime + norm_momentum) / 5.0
        return min(1.0, max(0.0, confidence))
