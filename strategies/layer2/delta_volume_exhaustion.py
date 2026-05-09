"""
strategies/layer2/delta_volume_exhaustion.py — Delta-Volume Exhaustion

Trend reversal strategy via weakening conviction. Detects when a strong
trending move is losing steam: delta declining while volume dries up.
Classic exhaustion signal — the trend is running out of fuel.

Logic:
    1. Detect strong trend (UP or DOWN) in 5m window
    2. Confirm delta is declining from rolling average
    3. Confirm volume is declining from rolling average
    4. Enter in OPPOSITE direction of the exhausted trend

Exit:
    - Stop: beyond the recent swing high/low
    - Target: mean reversion to rolling average

Confidence factors:
    - Trend strength (stronger trend = more dramatic reversal)
    - Rate of delta decline (faster decline = more exhaustion)
    - Rate of volume decline (drier volume = less conviction)
    - Number of consecutive candles in trend
"""

from __future__ import annotations

import logging
import statistics
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_TOTAL_DELTA_5M, KEY_VOLUME_5M

logger = logging.getLogger("Syngex.Strategies.DeltaVolumeExhaustion")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Min data points for trend detection
MIN_TREND_POINTS = 5

# Min data points for delta/volume rolling windows
MIN_GREEKS_POINTS = 5

# Delta must be below rolling avg by this ratio
DELTA_DECLINE_RATIO = 0.95            # Delta below 95% of rolling avg (was 90%)

# Volume must be below rolling avg by this ratio
VOLUME_DECLINE_RATIO = 0.90           # Volume below 90% of rolling avg (was 85%)

# Trend must be sustained for this many points
MIN_TREND_DURATION = 2                # At least 2 candles in trend (was 3)

# Stop distance
STOP_PCT = 0.008                      # 0.8% beyond swing

# Minimum confidence to emit a signal
MIN_CONFIDENCE = 0.25                 # Min confidence threshold (was 0.35)

# Target: mean reversion to rolling average
MEAN_REVERSION_MULT = 1.0             # 1.0× distance — target is the rolling mean


class DeltaVolumeExhaustion(BaseStrategy):
    """
    Detects trend exhaustion via declining delta + declining volume.

    When a strong trend loses delta conviction and volume dries up,
    the move is likely exhausted. Enter in the opposite direction
    for a mean-reversion fade.
    """

    strategy_id = "delta_volume_exhaustion"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for exhaustion setup.

        Returns empty list when no exhaustion detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        rolling_data = data.get("rolling_data", {})
        greeks_summary = data.get("greeks_summary", {})  # {strike: {net_delta, ...}}
        # Compute total delta from per-strike summary
        total_delta = sum(
            v.get("net_delta", 0) for v in greeks_summary.values()
        ) if isinstance(greeks_summary, dict) else 0
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")

        signals: List[Signal] = []

        # Check for exhausted UP trend → enter SHORT
        up_sig = self._check_exhaustion(
            rolling_data, greeks_summary, underlying_price,
            total_delta, "UP", net_gamma, regime,
        )
        if up_sig:
            signals.append(up_sig)

        # Check for exhausted DOWN trend → enter LONG
        down_sig = self._check_exhaustion(
            rolling_data, greeks_summary, underlying_price,
            total_delta, "DOWN", net_gamma, regime,
        )
        if down_sig:
            signals.append(down_sig)

        return signals

    def _check_exhaustion(
        self,
        rolling_data: Dict[str, Any],
        greeks_summary: Dict[str, Any],
        price: float,
        total_delta: float,
        trend_direction: str,
        net_gamma: float,
        regime: str,
    ) -> Optional[Signal]:
        """
        Check for exhaustion in a specific trend direction.

        Args:
            trend_direction: "UP" or "DOWN"
        """
        # 1. Check price trend
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window is None or price_window.count < MIN_TREND_POINTS:
            return None

        if price_window.trend != trend_direction:
            return None

        # Check trend duration: need sustained movement
        trend_strength = self._trend_strength(price_window)
        if trend_strength < 0.5:
            return None

        # 2. Check delta decline
        delta_decline = self._check_delta_decline(rolling_data, total_delta)
        if not delta_decline:
            return None

        # 3. Check volume decline
        vol_decline = self._check_volume_decline(rolling_data)
        if not vol_decline:
            return None

        # 4. Compute confidence
        confidence = self._compute_confidence(
            trend_strength, delta_decline, vol_decline,
            net_gamma, regime, trend_direction,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # 5. Build signal
        entry = price
        reverse = -1 if trend_direction == "UP" else 1

        # Stop: beyond recent swing
        swing_pct = STOP_PCT
        stop = entry * (1 + swing_pct * reverse)
        risk = abs(entry - stop)

        # Target: toward rolling mean
        rolling_mean = price_window.mean or entry
        target = entry + (rolling_mean - entry) * MEAN_REVERSION_MULT
        target = max(target, stop + risk * 0.1)  # At least a little room

        direction = Direction.SHORT if trend_direction == "UP" else Direction.LONG
        reason = (
            f"{trend_direction} trend exhausted: delta declining "
            f"(below avg) + volume drying up — fade the move"
        )

        return Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=reason,
            metadata={
                "exhausted_trend": trend_direction,
                "trend_strength": round(trend_strength, 3),
                "total_delta": round(total_delta, 2),
                "delta_decline": delta_decline,
                "volume_decline": vol_decline,
                "rolling_mean": round(rolling_mean, 2) if rolling_mean else None,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "price_trend": price_window.trend if price_window else "UNKNOWN",
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
            },
        )

    def _trend_strength(self, window: Any) -> float:
        """
        Score trend strength based on first-half vs second-half mean difference.

        Returns 0.0–1.0. Higher = stronger, more sustained trend.
        Direction-agnostic (works for both UP and DOWN trends).
        """
        if window.count < MIN_TREND_POINTS:
            return 0.0

        vals = list(window.values)
        half = len(vals) // 2
        first_half = statistics.mean(vals[:half])
        second_half = statistics.mean(vals[half:])
        diff = abs(second_half - first_half)
        std = window.std

        if std is None or std == 0:
            return 0.0

        # Normalize by std (same approach window.trend uses internally)
        strength = min(1.0, max(0.0, 0.3 + (diff / std) / 4.0))

        # Bonus for longer sustained trends
        duration_bonus = min(0.15, (window.count - MIN_TREND_POINTS) * 0.03)
        strength = min(1.0, strength + duration_bonus)

        return strength

    def _check_delta_decline(
        self,
        rolling_data: Dict[str, Any],
        current_delta: float,
    ) -> bool:
        """Check if total delta is declining below rolling average."""
        window = rolling_data.get(KEY_TOTAL_DELTA_5M)
        if window is None or window.count < MIN_GREEKS_POINTS:
            return False

        avg = window.mean
        if avg is None or avg == 0:
            return False

        # Delta should be declining: current below rolling avg
        # Account for sign: for positive delta, current < avg means declining
        # For negative delta, current > avg (less negative) means declining
        if abs(current_delta) < abs(avg * DELTA_DECLINE_RATIO):
            return False

        # Direction check: delta should be moving toward zero (weakening)
        if abs(current_delta) > abs(avg):
            return False

        return True

    def _check_volume_decline(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if volume is declining below rolling average."""
        window = rolling_data.get(KEY_VOLUME_5M)
        if window is None or window.count < MIN_GREEKS_POINTS:
            return False

        latest = window.latest
        avg = window.mean
        if latest is None or avg is None or avg == 0:
            return False

        return latest < avg * VOLUME_DECLINE_RATIO

    def _compute_confidence(
        self,
        trend_strength: float,
        delta_decline: bool,
        vol_decline: bool,
        net_gamma: float,
        regime: str,
        trend_direction: str,
    ) -> float:
        """
        Combine all factors into confidence score.

        Returns 0.0–1.0.
        """
        # 1. Trend strength (0.25–0.35)
        trend_conf = 0.25 + 0.10 * trend_strength

        # 2. Delta decline confirmation (0.20–0.25)
        delta_conf = 0.25 if delta_decline else 0.0

        # 3. Volume decline confirmation (0.15–0.20)
        vol_conf = 0.20 if vol_decline else 0.0

        # 4. Regime alignment (0.0–0.10)
        # Exhaustion signals are stronger in strong regimes
        # Direction-aware regime alignment
        if trend_direction == "UP":
            regime_conf = 0.10 if regime == "NEGATIVE" else 0.05
        else:
            regime_conf = 0.10 if regime == "POSITIVE" else 0.05

        # 5. Net gamma context (0.0–0.10)
        # Use abs(net_gamma) — both positive and negative gamma support mean reversion
        gamma_conf = 0.05 + 0.05 * min(1.0, abs(net_gamma) / 1000000)

        # Normalize each component to [0,1] and average
        norm_trend = (trend_conf - 0.25) / (0.35 - 0.25) if 0.35 != 0.25 else 1.0
        norm_delta = delta_conf / 0.25 if 0.25 != 0 else 0.0
        norm_vol = vol_conf / 0.20 if 0.20 != 0 else 0.0
        norm_regime = (regime_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_gamma = (gamma_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        confidence = (norm_trend + norm_delta + norm_vol + norm_regime + norm_gamma) / 5.0
        return min(1.0, max(0.0, confidence))
