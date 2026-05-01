"""
strategies/full_data/iv_skew_squeeze.py — IV Skew Squeeze

Full-data (v2) strategy: trades IV skew extremes. When the options market
is pricing in extreme fear (negative skew) or euphoria (positive skew)
but price isn't actually moving in that direction, the skew is likely
to normalize — trade the reversal.

Logic:
    - Calculate IV Skew = avg_call_iv - avg_put_iv across the chain
    - Extreme positive skew (>0.30) + price stable + net gamma positive → SHORT
      (euphoria: calls are expensive but price isn't breaking out)
    - Extreme negative skew (<-0.10) + price stable + net gamma positive → LONG
      (panic: puts are expensive but price isn't breaking down)
    - Skew normalization confirms the trade (skew moving toward zero)
    - Net gamma positive required for stability

Entry (LONG — panic overblown):
    - Skew < -0.10 (puts more expensive — bearish fear)
    - Price stable (not breaking down)
    - Net gamma positive (stable environment)
    - Volume not spiking down (no actual selling pressure)
    - Skew starting to normalize (current > rolling avg — fear easing)

Entry (SHORT — euphoria overblown):
    - Skew > 0.30 (calls more expensive — bullish euphoria)
    - Price stable (not breaking out)
    - Net gamma positive (stable environment)
    - Volume not spiking up (no actual buying pressure)
    - Skew starting to normalize (current < rolling avg — euphoria easing)

Confidence factors:
    - Skew extremity (how far from zero)
    - Price stability (stable = higher conviction)
    - Skew normalization (moving toward zero = confirmation)
    - Volume alignment (no opposite volume spike)
    - Net gamma strength
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_window import RollingWindow

logger = logging.getLogger("Syngex.Strategies.IVSkewSqueeze")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# IV Skew thresholds
SKEW_EXTREME_POSITIVE = 0.30       # Calls 30%+ more expensive (euphoria)
SKEW_EXTREME_NEGATIVE = -0.10      # Puts more expensive (panic)

# Price stability: price change must be < this % over 5m
PRICE_STABLE_THRESHOLD = 0.005     # 0.5% change max

# Min net gamma for positive regime confirmation
MIN_NET_GAMMA = 5000.0

# Stop and target
STOP_PCT = 0.005                   # 0.5% stop
TARGET_PCT = 0.008                 # 0.8% target (1.6:1 R:R)

# Min confidence
MIN_CONFIDENCE = 0.35
MAX_CONFIDENCE = 0.80              # v2 strategies cap

# Min data points
MIN_DATA_POINTS = 5                # Need data for basic checks
MIN_SKEW_DATA_POINTS = 10          # Minimum for skew rolling window

# Volume spike check
VOLUME_SPIKE_THRESHOLD = 1.5       # Volume > 1.5× avg = spike

# Skew window key (per-strategy state in rolling_data)
SKEW_WINDOW_KEY = "iv_skew_5m"
SKEW_WINDOW_SIZE = 1800            # 30-minute time-based window


class IVSkewSqueeze(BaseStrategy):
    """
    IV Skew Squeeze — Full-data (v2) strategy.

    Trades mean-reversion of IV skew extremes. When the options market
    prices in extreme fear or euphoria but price isn't actually moving
    in that direction, the skew is likely to normalize.

    Positive skew (calls > puts) → bullish euphoria → fade with SHORT
    Negative skew (puts > calls) → bearish panic → fade with LONG
    """

    strategy_id = "iv_skew_squeeze"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return skew-squeeze signals.

        Returns empty list when no skew extreme is detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0.0)

        # --- Ensure skew rolling window exists ---
        if SKEW_WINDOW_KEY not in rolling_data:
            rolling_data[SKEW_WINDOW_KEY] = RollingWindow(
                window_type="time",
                window_size=SKEW_WINDOW_SIZE,
            )

        skew_window = rolling_data[SKEW_WINDOW_KEY]

        # --- Compute current IV skew ---
        try:
            current_skew = gex_calc.get_iv_skew()
        except Exception:
            return []

        if current_skew is None:
            return []

        # Push skew to rolling window for trend tracking
        skew_window.push(current_skew, data.get("timestamp"))

        # Check minimum data points
        if skew_window.count < MIN_SKEW_DATA_POINTS:
            return []

        # --- Get price data ---
        price_window = rolling_data.get("price_5m")
        if price_window is None or price_window.count < MIN_DATA_POINTS:
            return []

        price_change_pct = price_window.change_pct
        if price_change_pct is None:
            return []

        # --- Get volume data ---
        volume_window = rolling_data.get("volume_5m")
        if volume_window is None or volume_window.count < MIN_DATA_POINTS:
            return []

        # --- Get net gamma ---
        if net_gamma < MIN_NET_GAMMA:
            return []

        # --- Check for LONG (panic overblown) ---
        long_sig = self._check_long(
            current_skew, skew_window, price_window, volume_window,
            underlying_price, net_gamma, data,
        )

        # --- Check for SHORT (euphoria overblown) ---
        short_sig = self._check_short(
            current_skew, skew_window, price_window, volume_window,
            underlying_price, net_gamma, data,
        )

        signals: List[Signal] = []
        if long_sig:
            signals.append(long_sig)
        if short_sig:
            signals.append(short_sig)

        return signals

    # ------------------------------------------------------------------
    # LONG: Panic overblown (negative skew extreme)
    # ------------------------------------------------------------------

    def _check_long(
        self,
        current_skew: float,
        skew_window: RollingWindow,
        price_window: RollingWindow,
        volume_window: RollingWindow,
        price: float,
        net_gamma: float,
        data: Dict[str, Any],
    ) -> Optional[Signal]:
        """
        Detect panic overblown: negative skew extreme + price stable.

        Negative skew = puts more expensive than calls = market pricing in panic.
        If price isn't actually breaking down, the panic is likely overblown
        and skew will normalize (move toward zero from negative), pulling price up.
        """
        # Skew must be extremely negative (panic)
        if current_skew >= SKEW_EXTREME_NEGATIVE:
            return None

        # Price must NOT be breaking down — stable or rising
        price_change = price_window.change_pct
        if price_change is None:
            return None
        if price_change < -PRICE_STABLE_THRESHOLD:
            # Price is actually breaking down — panic may be justified
            return None

        # Volume must NOT be spiking on the downside
        if not self._volume_not_spiking(volume_window, current_skew, price_change):
            return None

        # Skew normalization: fear must be easing
        # For negative skew, easing means current > rolling avg (less negative)
        rolling_avg_skew = skew_window.mean
        if rolling_avg_skew is None:
            return None

        if current_skew >= rolling_avg_skew:
            # Skew is not normalizing (not moving toward zero)
            # For negative skew: current should be > avg (less negative = easing)
            return None

        # All conditions met — compute confidence
        confidence = self._compute_long_confidence(
            current_skew, price_change, rolling_avg_skew,
            volume_window, net_gamma, price,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        stop = price * (1 - STOP_PCT)
        target = price * (1 + TARGET_PCT)

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Negative skew extreme ({current_skew:.3f}) + price stable "
                f"({price_change:+.2%}) + net gamma {net_gamma:.0f} + "
                f"skew easing (avg={rolling_avg_skew:.3f})"
            ),
            metadata={
                "skew_value": round(current_skew, 4),
                "skew_rolling_avg": round(rolling_avg_skew, 4),
                "skew_direction": "NEGATIVE",
                "price_change_pct": round(price_change, 4),
                "net_gamma": round(net_gamma, 2),
                "volume_ratio": self._get_volume_ratio(volume_window),
                "skew_normalizing": True,
                "stop_pct": STOP_PCT,
                "target_pct": TARGET_PCT,
                "risk_reward_ratio": round(abs(target - price) / (price - stop), 2)
                    if (price - stop) > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # SHORT: Euphoria overblown (positive skew extreme)
    # ------------------------------------------------------------------

    def _check_short(
        self,
        current_skew: float,
        skew_window: RollingWindow,
        price_window: RollingWindow,
        volume_window: RollingWindow,
        price: float,
        net_gamma: float,
        data: Dict[str, Any],
    ) -> Optional[Signal]:
        """
        Detect euphoria overblown: positive skew extreme + price stable.

        Positive skew = calls more expensive than puts = market pricing in euphoria.
        If price isn't actually breaking out, the euphoria is likely overblown
        and skew will normalize (move toward zero from positive), pulling price down.
        """
        # Skew must be extremely positive (euphoria)
        if current_skew <= SKEW_EXTREME_POSITIVE:
            return None

        # Price must NOT be breaking out — stable or falling
        price_change = price_window.change_pct
        if price_change is None:
            return None
        if price_change > PRICE_STABLE_THRESHOLD:
            # Price is actually breaking out — euphoria may be justified
            return None

        # Volume must NOT be spiking on the upside
        if not self._volume_not_spiking(volume_window, current_skew, price_change):
            return None

        # Skew normalization: euphoria must be easing
        # For positive skew, easing means current < rolling avg (less positive)
        rolling_avg_skew = skew_window.mean
        if rolling_avg_skew is None:
            return None

        if current_skew >= rolling_avg_skew:
            # Skew is not normalizing (not moving toward zero)
            # For positive skew: current should be < avg (less positive = easing)
            return None

        # All conditions met — compute confidence
        confidence = self._compute_short_confidence(
            current_skew, price_change, rolling_avg_skew,
            volume_window, net_gamma, price,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        stop = price * (1 + STOP_PCT)
        target = price * (1 - TARGET_PCT)

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Positive skew extreme ({current_skew:.3f}) + price stable "
                f"({price_change:+.2%}) + net gamma {net_gamma:.0f} + "
                f"skew easing (avg={rolling_avg_skew:.3f})"
            ),
            metadata={
                "skew_value": round(current_skew, 4),
                "skew_rolling_avg": round(rolling_avg_skew, 4),
                "skew_direction": "POSITIVE",
                "price_change_pct": round(price_change, 4),
                "net_gamma": round(net_gamma, 2),
                "volume_ratio": self._get_volume_ratio(volume_window),
                "skew_normalizing": True,
                "stop_pct": STOP_PCT,
                "target_pct": TARGET_PCT,
                "risk_reward_ratio": round(abs(target - price) / (stop - price), 2)
                    if (stop - price) > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _volume_not_spiking(
        self,
        volume_window: RollingWindow,
        current_skew: float,
        price_change: float,
    ) -> bool:
        """
        Check that volume is NOT spiking in the direction of the skew.

        For negative skew (panic): don't want volume spike on the downside.
        For positive skew (euphoria): don't want volume spike on the upside.
        """
        if volume_window.count < 2:
            return True  # Not enough data to determine

        current_vol = volume_window.latest
        avg_vol = volume_window.mean

        if current_vol is None or avg_vol is None or avg_vol == 0:
            return True

        ratio = current_vol / avg_vol

        if current_skew < 0:
            # Negative skew (panic) — check for volume spike on downside
            if price_change < -PRICE_STABLE_THRESHOLD and ratio > VOLUME_SPIKE_THRESHOLD:
                return False
        else:
            # Positive skew (euphoria) — check for volume spike on upside
            if price_change > PRICE_STABLE_THRESHOLD and ratio > VOLUME_SPIKE_THRESHOLD:
                return False

        # Overall volume spike check regardless of direction
        if ratio > VOLUME_SPIKE_THRESHOLD:
            return False

        return True

    def _get_volume_ratio(self, volume_window: RollingWindow) -> Optional[float]:
        """Get current volume / rolling average volume ratio."""
        if volume_window.count < 2:
            return None
        current = volume_window.latest
        avg = volume_window.mean
        if current is None or avg is None or avg == 0:
            return None
        return round(current / avg, 2)

    def _compute_long_confidence(
        self,
        current_skew: float,
        price_change: float,
        rolling_avg_skew: float,
        volume_window: RollingWindow,
        net_gamma: float,
        price: float,
    ) -> float:
        """
        Compute confidence for LONG (panic overblown) signal.

        Factors:
            1. Skew extremity — how far below SKEW_EXTREME_NEGATIVE
            2. Price stability — how flat price is
            3. Skew normalization — how much skew has eased from avg
            4. Volume alignment — no volume spike
            5. Net gamma strength — stronger positive gamma = higher confidence
        """
        # 1. Skew extremity (0.15–0.25)
        #    Skew < -0.10 is the threshold; deeper = higher confidence
        skew_magnitude = abs(current_skew)
        # Normalize: -0.10 = 0.3, -0.30 = 0.6, -0.50+ = 1.0
        skew_conf = min(1.0, (skew_magnitude - 0.10) / 0.40)
        skew_component = 0.15 + 0.10 * skew_conf

        # 2. Price stability (0.15–0.25)
        #    Price change closer to 0 = more stable = higher confidence
        stability = 1.0 - min(1.0, abs(price_change) / PRICE_STABLE_THRESHOLD)
        stability_component = 0.15 + 0.10 * stability

        # 3. Skew normalization (0.15–0.20)
        #    How much skew has eased from rolling average
        skew_ease = rolling_avg_skew - current_skew  # Should be positive for negative skew
        # Normalize: 0 = no easing, 0.10+ = strong easing
        norm_conf = min(1.0, skew_ease / 0.10)
        norm_component = 0.15 + 0.05 * norm_conf

        # 4. Volume alignment (0.10–0.15)
        vol_ratio = self._get_volume_ratio(volume_window)
        if vol_ratio is not None:
            # No spike = good (ratio close to 1.0)
            vol_stability = 1.0 - min(1.0, max(0, (vol_ratio - 1.0) / (VOLUME_SPIKE_THRESHOLD - 1.0)))
            vol_component = 0.10 + 0.05 * vol_stability
        else:
            vol_component = 0.10  # Neutral if no volume data

        # 5. Net gamma strength (0.15–0.15)
        #    Higher net gamma = more stable environment
        gamma_conf = min(1.0, net_gamma / 500000.0)
        gamma_component = 0.10 + 0.10 * gamma_conf

        # Normalize each component to [0,1] and average
        norm_skew = (skew_component - 0.15) / (0.25 - 0.15) if 0.25 != 0.15 else 1.0
        norm_stability = (stability_component - 0.15) / (0.25 - 0.15) if 0.25 != 0.15 else 1.0
        norm_norm = (norm_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_vol = (vol_component - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        norm_gamma = (gamma_component - 0.10) / (0.20 - 0.10) if 0.20 != 0.10 else 1.0
        confidence = (norm_skew + norm_stability + norm_norm + norm_vol + norm_gamma) / 5.0

        return min(MAX_CONFIDENCE, max(0.0, confidence))

    def _compute_short_confidence(
        self,
        current_skew: float,
        price_change: float,
        rolling_avg_skew: float,
        volume_window: RollingWindow,
        net_gamma: float,
        price: float,
    ) -> float:
        """
        Compute confidence for SHORT (euphoria overblown) signal.

        Factors:
            1. Skew extremity — how far above SKEW_EXTREME_POSITIVE
            2. Price stability — how flat price is
            3. Skew normalization — how much skew has eased from avg
            4. Volume alignment — no volume spike
            5. Net gamma strength — stronger positive gamma = higher confidence
        """
        # 1. Skew extremity (0.15–0.25)
        #    Skew > 0.30 is the threshold; higher = higher confidence
        skew_magnitude = abs(current_skew)
        # Normalize: 0.30 = 0.3, 0.50 = 0.6, 0.70+ = 1.0
        skew_conf = min(1.0, (skew_magnitude - 0.30) / 0.40)
        skew_component = 0.15 + 0.10 * skew_conf

        # 2. Price stability (0.15–0.25)
        stability = 1.0 - min(1.0, abs(price_change) / PRICE_STABLE_THRESHOLD)
        stability_component = 0.15 + 0.10 * stability

        # 3. Skew normalization (0.15–0.20)
        skew_ease = current_skew - rolling_avg_skew  # Should be positive for positive skew
        norm_conf = min(1.0, skew_ease / 0.10)
        norm_component = 0.15 + 0.05 * norm_conf

        # 4. Volume alignment (0.10–0.15)
        vol_ratio = self._get_volume_ratio(volume_window)
        if vol_ratio is not None:
            vol_stability = 1.0 - min(1.0, max(0, (vol_ratio - 1.0) / (VOLUME_SPIKE_THRESHOLD - 1.0)))
            vol_component = 0.10 + 0.05 * vol_stability
        else:
            vol_component = 0.10

        # 5. Net gamma strength (0.15–0.15)
        gamma_conf = min(1.0, net_gamma / 500000.0)
        gamma_component = 0.10 + 0.10 * gamma_conf

        # Normalize each component to [0,1] and average
        norm_skew = (skew_component - 0.15) / (0.25 - 0.15) if 0.25 != 0.15 else 1.0
        norm_stability = (stability_component - 0.15) / (0.25 - 0.15) if 0.25 != 0.15 else 1.0
        norm_norm = (norm_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_vol = (vol_component - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        norm_gamma = (gamma_component - 0.10) / (0.20 - 0.10) if 0.20 != 0.10 else 1.0
        confidence = (norm_skew + norm_stability + norm_norm + norm_vol + norm_gamma) / 5.0

        return min(MAX_CONFIDENCE, max(0.0, confidence))
