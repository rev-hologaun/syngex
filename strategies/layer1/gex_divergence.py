"""
strategies/layer1/gex_divergence.py — GEX Divergence

Finding exhaustion by comparing price trend vs. GEX trend.
If Price ↑ but Total GEX ↓ (walls evaporating), the trend is losing
structural support and is likely to reverse.

Concept:
    Gamma walls provide structural support for price trends.
    When price trends but GEX trends in the opposite direction,
    the structural foundation is eroding — the trend is exhausted.

    Bearish divergence: price UP + GEX DOWN → fade (SHORT)
    Bullish divergence: price DOWN + GEX UP → fade (LONG)

Logic:
    1. Track price trend via rolling window slope
    2. Track GEX trend via rolling net_gamma window
    3. Divergence = slopes have opposite signs AND both exceed threshold
    4. OHLC confirmation: last candle must align with the fade direction

Entry:
    - Bearish divergence + confirming candle → SHORT
    - Bullish divergence + confirming candle → LONG

Exit:
    - Stop: 0.5% from entry
    - Target: 1.5× risk (1:1.5 RR)

Confidence factors:
    - Magnitude of price slope vs GEX slope (larger divergence = higher confidence)
    - Wall strength at divergence point (strong walls = bigger reversal)
    - Regime alignment
    - Confirmation candle strength
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_PRICE_30M, KEY_NET_GAMMA_5M

logger = logging.getLogger("Syngex.Strategies.GEXDivergence")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DIVERGENCE_MIN_SLOPE = 0.0005   # Minimum slope magnitude (0.05% — catches subtler divergences)
DIVERGENCE_WINDOW = 30           # Number of points for slope calculation
CONFIRMATION_CANDLE_PCT = 0.002  # 0.2% candle for confirmation
MIN_CONFIDENCE = 0.25            # Minimum confidence to emit signal
STOP_PCT = 0.005                 # 0.5% stop
TARGET_RISK_MULT = 1.5           # 1.5× risk for target
MIN_DATA_POINTS = 15             # Minimum data points for slope calculation
MIN_TOTAL_GEX = 1000000.0        # 1M — minimum GEX wall strength


class GEXDivergence(BaseStrategy):
    """
    GEX Divergence strategy: fade exhausted trends via price/GEX slope divergence.

    When price trends in one direction but GEX trends the other,
    the structural support for the trend is evaporating. Fade the move.

    Regime is a soft confidence factor (not a hard gate): aligned regimes
    boost confidence, misaligned regimes reduce it but do not block signals.

    Requires rolling "price" and "net_gamma" windows in rolling_data.
    """

    strategy_id = "gex_divergence"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate price/GEX divergence and return fade signals.

        Returns empty list when divergence is not detected or data
        is insufficient.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        regime = data.get("regime", "")

        # Get price rolling window
        price_window = self._get_price_window(rolling_data)
        if price_window is None or price_window.count < MIN_DATA_POINTS:
            return []

        # Get net_gamma rolling window — this is critical
        gamma_window = self._get_gamma_window(rolling_data)
        if gamma_window is None or gamma_window.count < MIN_DATA_POINTS:
            return []  # No gamma data — skip gracefully

        # Calculate slopes
        price_slope = self._calculate_slope(price_window)
        gamma_slope = self._calculate_slope(gamma_window)

        if price_slope is None or gamma_slope is None:
            return []

        # Check for divergence: slopes must have opposite signs
        if (price_slope > 0 and gamma_slope > 0) or \
           (price_slope < 0 and gamma_slope < 0):
            return []  # Same direction — no divergence

        # Both slopes must exceed minimum magnitude
        if abs(price_slope) < DIVERGENCE_MIN_SLOPE:
            return []
        if abs(gamma_slope) < DIVERGENCE_MIN_SLOPE:
            return []

        # Determine divergence type
        if price_slope > 0 and gamma_slope < 0:
            # Bearish divergence: price up, GEX down → SHORT
            divergence_type = "bearish"
        else:
            # Bullish divergence: price down, GEX up → LONG
            divergence_type = "bullish"

        # Regime alignment: soft confidence factor, not a hard gate.
        regime_misaligned = False
        if divergence_type == "bullish" and regime != "POSITIVE":
            regime_misaligned = True
        if divergence_type == "bearish" and regime != "NEGATIVE":
            regime_misaligned = True

        # Get confirmation from last price movement
        price_change = self._get_price_change(price_window)
        confirmed = self._check_confirmation(price_change, divergence_type)
        if not confirmed:
            return []  # No confirmation candle

        # Compute confidence
        confidence = self._compute_confidence(
            price_slope, gamma_slope, divergence_type,
            price_window, gamma_window, regime, confirmed,
            regime_misaligned
        )
        if confidence < MIN_CONFIDENCE:
            return []

        # GEX wall strength gate: divergence on thin walls is worthless
        try:
            summary = gex_calc.get_summary()
            net_gamma_val = summary.get("net_gamma", 0.0)
            if abs(net_gamma_val) < MIN_TOTAL_GEX:
                return []  # GEX walls too weak for a reliable signal
        except Exception:
            return []  # Can't assess GEX strength — skip

        # Build signal
        if divergence_type == "bearish":
            direction = Direction.SHORT
            stop = underlying_price * (1 + STOP_PCT)
            target = underlying_price * (1 - STOP_PCT * TARGET_RISK_MULT)
            reason_suffix = "price rising but GEX walls evaporating"
        else:
            direction = Direction.LONG
            stop = underlying_price * (1 - STOP_PCT)
            target = underlying_price * (1 + STOP_PCT * TARGET_RISK_MULT)
            reason_suffix = "price falling but GEX walls strengthening"

        risk = abs(underlying_price - stop)
        reward = abs(target - underlying_price)

        return [Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=underlying_price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"GEX divergence ({divergence_type}): {reason_suffix}, "
                   f"price_slope={price_slope:.4f}, gamma_slope={gamma_slope:.4f}, "
                   f"regime={regime}",
            metadata={
                "divergence_type": divergence_type,
                "price_slope": round(price_slope, 6),
                "gamma_slope": round(gamma_slope, 6),
                "price_window_count": price_window.count,
                "gamma_window_count": gamma_window.count,
                "trend": price_window.trend if price_window else "UNKNOWN",
                "regime": regime,
                "risk": round(risk, 2),
                "reward": round(reward, 2),
                "risk_reward_ratio": round(reward / risk, 2) if risk > 0 else 0,
            },
        )]

    # ------------------------------------------------------------------
    # Slope calculation
    # ------------------------------------------------------------------

    def _calculate_slope(self, window: Any) -> Optional[float]:
        """
        Calculate the slope of a rolling window using first and last values.

        Slope = (last - first) / first as a percentage.
        Returns None if insufficient data.
        """
        if window.count < 5:
            return None

        first_val = window.values[0] if window.values else None
        last_val = window.values[-1] if window.values else None

        if first_val is None or last_val is None or first_val == 0:
            return None

        slope = (last_val - first_val) / abs(first_val)
        return slope

    # ------------------------------------------------------------------
    # Price change detection
    # ------------------------------------------------------------------

    def _get_price_change(self, window: Any) -> Optional[float]:
        """Get the recent price change from the window."""
        values = window.values
        if len(values) < 2:
            return None
        # Use last few values for recent change
        recent = values[-min(5, len(values)):]
        if len(recent) < 2:
            return None
        return (recent[-1] - recent[0]) / abs(recent[0])

    # ------------------------------------------------------------------
    # Confirmation check
    # ------------------------------------------------------------------

    def _check_confirmation(
        self,
        price_change: Optional[float],
        divergence_type: str,
    ) -> bool:
        """
        Check if the latest price movement confirms the divergence signal.

        For bearish divergence (SHORT): price should be declining or flat.
        For bullish divergence (LONG): price should be rising or flat.
        """
        if price_change is None:
            return True  # No change data — allow signal

        if divergence_type == "bearish":
            # Price should not be strongly rising
            # Allow small upticks (noise) but reject strong rallies
            return price_change < CONFIRMATION_CANDLE_PCT * 3
        else:
            # Price should not be strongly falling
            return price_change > -CONFIRMATION_CANDLE_PCT * 3

    # ------------------------------------------------------------------
    # Confidence computation
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        price_slope: float,
        gamma_slope: float,
        divergence_type: str,
        price_window: Any,
        gamma_window: Any,
        regime: str,
        confirmed: bool,
        regime_misaligned: bool = False,
    ) -> float:
        """
        Compute divergence signal confidence.

        Factors:
        - Price slope magnitude: larger trend = bigger reversal potential (0.2–0.3)
        - Gamma slope magnitude: larger GEX shift = stronger structural change (0.2–0.3)
        - Slope ratio: balanced divergence = higher confidence (0.1–0.15)
        - Data quality: more points = more reliable (0.05–0.1)
        - Regime alignment: aligned regime adds bonus; misaligned zeroes it out
          but does not block the signal (regime is a soft confidence factor)
        """
        # Price slope confidence
        price_conf = 0.15 + 0.15 * min(1.0, abs(price_slope) / 0.01)

        # Gamma slope confidence
        gamma_conf = 0.15 + 0.15 * min(1.0, abs(gamma_slope) / 0.01)

        # Slope balance: if both slopes are similarly strong, divergence is cleaner
        slope_ratio = min(abs(price_slope), abs(gamma_slope)) / \
                      max(abs(price_slope), abs(gamma_slope)) if max(
                          abs(price_slope), abs(gamma_slope)) > 0 else 0
        balance_conf = 0.1 + 0.05 * slope_ratio

        # Data quality
        min_count = min(price_window.count, gamma_window.count)
        data_conf = min(0.1, (min_count - MIN_DATA_POINTS) / 100)

        # Regime alignment: soft bonus when aligned, zero when misaligned
        regime_conf = 0.0
        if not regime_misaligned:
            if divergence_type == "bullish" and regime == "POSITIVE":
                regime_conf = 0.1
            elif divergence_type == "bearish" and regime == "NEGATIVE":
                regime_conf = 0.1

        # Normalize each component to [0,1] and average
        norm_price = (price_conf - 0.15) / (0.3 - 0.15) if 0.3 != 0.15 else 1.0
        norm_gamma = (gamma_conf - 0.15) / (0.3 - 0.15) if 0.3 != 0.15 else 1.0
        norm_balance = (balance_conf - 0.1) / (0.15 - 0.1) if 0.15 != 0.1 else 1.0
        norm_data = data_conf / 0.1 if 0.1 != 0 else 0.0
        norm_regime = regime_conf / 0.1 if 0.1 != 0 else 0.0
        confidence = (norm_price + norm_gamma + norm_balance + norm_data + norm_regime) / 5.0
        return min(1.0, max(0.0, confidence))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_price_window(
        self, rolling_data: Dict[str, Any]
    ) -> Optional[Any]:
        """Get the best available price rolling window."""
        for key in (KEY_PRICE_5M, KEY_PRICE_30M):
            rw = rolling_data.get(key)
            if rw is not None and rw.count >= MIN_DATA_POINTS:
                return rw
        return None

    def _get_gamma_window(
        self, rolling_data: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Get the net_gamma rolling window.

        This is critical for the divergence strategy. If not present,
        the strategy cannot function — return None to skip.
        """
        for key in (KEY_NET_GAMMA_5M,):
            rw = rolling_data.get(key)
            if rw is not None and rw.count >= MIN_DATA_POINTS:
                return rw
        return None
