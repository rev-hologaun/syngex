"""
strategies/layer3/iv_band_breakout.py — IV Band Breakout

Micro-signal (1Hz) strategy: detects the transition from IV compression
to expansion. When IV is in the bottom 25% of its 30m range, price is
compressing, and delta is decelerating (proxy for theta coiling), a
breakout is imminent.

Logic:
    - Monitor ATM strike for IV compression (bottom 25% of 30m range)
    - Price compression (narrow range relative to rolling average)
    - Delta deceleration while gamma is high (coiled spring proxy)
    - Trade the breakout direction when price slices through range

Entry:
    - LONG:  IV compressed + price compression + delta coiling +
             price breaks above range + VolumeUp + delta turning positive
    - SHORT: IV compressed + price compression + delta coiling +
             price breaks below range + VolumeDown + delta turning negative

Confidence factors:
    - IV compression depth (how far below p25 — deeper = higher confidence)
    - Price compression tightness (tighter range = more coiled)
    - Delta extremity (how much below rolling avg — coiling signal)
    - Volume confirmation (strong volume trend)
    - Regime alignment (positive gamma = higher confidence)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_VOLUME_5M, KEY_TOTAL_DELTA_5M

logger = logging.getLogger("Syngex.Strategies.IVBandBreakout")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Delta acceleration threshold: current delta must be below rolling avg
# by this ratio (< 1.0 means deceleration = coiling signal)
DELTA_DECEL_RATIO = 0.98  # Delta must be below rolling avg

# IV compression: IV must be in bottom 25% of its 30m range
# (checked via RollingWindow.is_in_bottom_quartile)

# Price compression: high-low range must be < 30% of rolling mean range
PRICE_COMPRESSION_RATIO = 0.30

# Minimum price move to count as breakout (0.05%)
BREAKOUT_MOVE_PCT = 0.0005

# Volume confirmation
VOLUME_TREND_REQUIRED = True

# Stop and target
STOP_PCT = 0.005              # 0.5% stop
TARGET_PCT = 0.010            # 1.0% target (2:1 R:R)

# Min confidence
MIN_CONFIDENCE = 0.35
MAX_CONFIDENCE = 0.85         # Micro-signal cap

# Min data points
MIN_DATA_POINTS = 5           # Need enough data for stats
MIN_IV_DATA_POINTS = 3        # Minimum for IV window


class IVBandBreakout(BaseStrategy):
    """
    Detects the transition from IV compression to expansion.

    When IV is compressed (bottom 25% of 30m range), price is coiling
    (narrow range), and delta is decelerating while gamma is high
    (coiled spring proxy), a breakout is imminent.

    In a positive gamma regime:
        - LONG:  IV compressed + price compression + delta coiling +
                 price breaks above range + VolumeUp + delta turning positive
        - SHORT: IV compressed + price compression + delta coiling +
                 price breaks below range + VolumeDown + delta turning negative

    Exits: 0.5% stop, 1.0% target (2:1 R:R).
    """

    strategy_id = "iv_band_breakout"
    layer = "layer3"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for IV band breakout signals.

        Returns empty list when no compression-to-expansion transition
        is detected.
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

        # Positive gamma regime required — stable environment
        if regime != "POSITIVE":
            return []

        # Must have positive net gamma
        if net_gamma <= 0:
            return []

        signals: List[Signal] = []

        # Check LONG breakout
        long_sig = self._check_long(
            underlying_price, gex_calc, rolling_data, net_gamma, regime,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT breakout
        short_sig = self._check_short(
            underlying_price, gex_calc, rolling_data, net_gamma, regime,
        )
        if short_sig:
            signals.append(short_sig)

        return signals

    # ------------------------------------------------------------------
    # LONG entry: IV compressed + price compression + delta coiling +
    #             price breaks above range + VolumeUp + delta turning positive
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
        Evaluate LONG breakout signal.

        Conditions:
            1. Net Gamma > 0 (already checked in evaluate)
            2. ATM strike IV in bottom 25% of 30m range (compression)
            3. Price compression: range < 30% of rolling mean range
            4. Delta deceleration (proxy for theta coiling)
            5. Price breaks above recent high
            6. Volume trending UP
            7. Delta at ATM turning positive
        """
        # Get ATM strike
        atm_strike = self._get_atm_strike(gex_calc, price)
        if atm_strike is None:
            return None

        # 1. IV compression check
        iv_compressed, iv_depth = self._check_iv_compression(
            rolling_data, atm_strike,
        )
        if not iv_compressed:
            return None

        # 2. Price compression check
        if not self._check_price_compression(rolling_data):
            return None

        # 3. Delta coiling check (proxy for theta decay)
        delta_decel = self._check_delta_coiling(rolling_data)
        if delta_decel is None or delta_decel >= DELTA_DECEL_RATIO:
            return None

        # 4. Price breakout above recent high
        if not self._check_breakout_high(rolling_data):
            return None

        # 5. Volume trending UP
        vol_trend = self._get_volume_trend(rolling_data)
        if vol_trend != "UP":
            return None

        # 6. Delta at ATM turning positive
        if not self._check_atm_delta_positive(gex_calc, atm_strike):
            return None

        # All conditions met — compute confidence and build signal
        confidence = self._compute_long_confidence(
            iv_depth, rolling_data, delta_decel, vol_trend, net_gamma,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        entry = price
        stop = entry * (1 - STOP_PCT)
        target = entry * (1 + TARGET_PCT)

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"IV band breakout LONG: ATM {atm_strike} IV compressed, "
                f"price coiling, delta decel x{delta_decel:.3f}, "
                f"VolumeUp, delta turning positive"
            ),
            metadata={
                "atm_strike": atm_strike,
                "iv_compression_depth": round(iv_depth, 4),
                "price_compression_ratio": round(self._get_price_compression_ratio(rolling_data), 3),
                "delta_deceleration_ratio": round(delta_decel, 3),
                "volume_trend": vol_trend,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "stop": round(stop, 2),
                "target": round(target, 2),
                "risk": round(entry - stop, 2),
                "risk_reward_ratio": round(
                    (target - entry) / (entry - stop), 2
                ) if (entry - stop) > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # SHORT entry: IV compressed + price compression + delta coiling +
    #              price breaks below range + VolumeDown + delta turning negative
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
        Evaluate SHORT breakout signal.

        Conditions:
            1. Net Gamma > 0 (already checked in evaluate)
            2. ATM strike IV in bottom 25% of 30m range (compression)
            3. Price compression: range < 30% of rolling mean range
            4. Delta deceleration (proxy for theta coiling)
            5. Price breaks below recent low
            6. Volume trending DOWN
            7. Delta at ATM turning negative
        """
        # Get ATM strike
        atm_strike = self._get_atm_strike(gex_calc, price)
        if atm_strike is None:
            return None

        # 1. IV compression check
        iv_compressed, iv_depth = self._check_iv_compression(
            rolling_data, atm_strike,
        )
        if not iv_compressed:
            return None

        # 2. Price compression check
        if not self._check_price_compression(rolling_data):
            return None

        # 3. Delta coiling check (proxy for theta decay)
        delta_decel = self._check_delta_coiling(rolling_data)
        if delta_decel is None or delta_decel >= DELTA_DECEL_RATIO:
            return None

        # 4. Price breakout below recent low
        if not self._check_breakout_low(rolling_data):
            return None

        # 5. Volume trending DOWN
        vol_trend = self._get_volume_trend(rolling_data)
        if vol_trend != "DOWN":
            return None

        # 6. Delta at ATM turning negative
        if not self._check_atm_delta_negative(gex_calc, atm_strike):
            return None

        # All conditions met — compute confidence and build signal
        confidence = self._compute_short_confidence(
            iv_depth, rolling_data, delta_decel, vol_trend, net_gamma,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        entry = price
        stop = entry * (1 + STOP_PCT)
        target = entry * (1 - TARGET_PCT)

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"IV band breakout SHORT: ATM {atm_strike} IV compressed, "
                f"price coiling, delta decel x{delta_decel:.3f}, "
                f"VolumeDown, delta turning negative"
            ),
            metadata={
                "atm_strike": atm_strike,
                "iv_compression_depth": round(iv_depth, 4),
                "price_compression_ratio": round(self._get_price_compression_ratio(rolling_data), 3),
                "delta_deceleration_ratio": round(delta_decel, 3),
                "volume_trend": vol_trend,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "stop": round(stop, 2),
                "target": round(target, 2),
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
            logger.debug("IVBandBreakout: failed to get ATM strike: %s", exc)
            return None

    @staticmethod
    def _check_iv_compression(
        rolling_data: Dict[str, Any],
        atm_strike: float,
    ) -> tuple[bool, float]:
        """
        Check if IV at the ATM strike is in the bottom 25% of its 30m range.

        Returns (is_compressed, depth) where depth is how far below p25
        the current IV sits. Positive depth = compressed.
        """
        key = f"iv_{atm_strike}_5m"
        iv_window = rolling_data.get(key)
        if iv_window is None or iv_window.count < MIN_IV_DATA_POINTS:
            return False, 0.0

        iv_latest = iv_window.latest
        iv_p25 = iv_window.p25

        if iv_latest is None or iv_p25 is None:
            return False, 0.0

        # IV is compressed if latest is at or below p25
        is_compressed = iv_latest <= iv_p25

        # Depth = how far below p25 (positive = compressed deeper)
        depth = iv_p25 - iv_latest

        return is_compressed, depth

    @staticmethod
    def _check_price_compression(rolling_data: Dict[str, Any]) -> bool:
        """
        Check if price is compressing.

        Current high-low range must be < 30% of the rolling mean range.
        Tighter range = more coiled = higher breakout probability.
        """
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None or window.count < MIN_DATA_POINTS:
            return False

        current_range = window.range
        mean_range = window.mean

        if current_range is None or mean_range is None or mean_range == 0:
            return False

        compression_ratio = current_range / mean_range
        return compression_ratio < PRICE_COMPRESSION_RATIO

    @staticmethod
    def _get_price_compression_ratio(rolling_data: Dict[str, Any]) -> float:
        """Get the current price compression ratio for metadata."""
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None:
            return 1.0

        current_range = window.range
        mean_range = window.mean

        if current_range is None or mean_range is None or mean_range == 0:
            return 1.0

        return current_range / mean_range

    @staticmethod
    def _check_delta_coiling(
        rolling_data: Dict[str, Any],
    ) -> Optional[float]:
        """
        Check if delta is decelerating (coiling proxy for theta).

        When delta is declining while gamma is high, that's the coiling
        signal — the spring is tightening.

        Returns ratio of current delta to rolling avg.
            < 1.0 = decelerating (coiling)
            >= 1.0 = not coiling
        """
        window = rolling_data.get(KEY_TOTAL_DELTA_5M)
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
    def _check_breakout_high(rolling_data: Dict[str, Any]) -> bool:
        """
        Check if price has broken above the recent high.

        Latest price must be above the rolling window max by at least
        BREAKOUT_MOVE_PCT.
        """
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None or window.count < 3:
            return False

        latest = window.latest
        window_max = window.max

        if latest is None or window_max is None:
            return False

        # Price must be above the recent high
        if latest <= window_max:
            return False

        # Must have moved enough to count as breakout
        move_pct = (latest - window_max) / window_max
        return move_pct >= BREAKOUT_MOVE_PCT

    @staticmethod
    def _check_breakout_low(rolling_data: Dict[str, Any]) -> bool:
        """
        Check if price has broken below the recent low.

        Latest price must be below the rolling window min by at least
        BREAKOUT_MOVE_PCT.
        """
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None or window.count < 3:
            return False

        latest = window.latest
        window_min = window.min

        if latest is None or window_min is None:
            return False

        # Price must be below the recent low
        if latest >= window_min:
            return False

        # Must have moved enough to count as breakout
        move_pct = (window_min - latest) / window_min
        return move_pct >= BREAKOUT_MOVE_PCT

    @staticmethod
    def _get_volume_trend(rolling_data: Dict[str, Any]) -> str:
        """Get the volume trend direction from the rolling window."""
        window = rolling_data.get(KEY_VOLUME_5M)
        if window is None:
            return "FLAT"
        return window.trend

    @staticmethod
    def _check_atm_delta_positive(gex_calc: Any, atm_strike: float) -> bool:
        """
        Check if net delta at the ATM strike is positive.

        Net delta > 0 means delta is turning positive.
        """
        try:
            delta_data = gex_calc.get_delta_by_strike(atm_strike)
            net_delta = delta_data.get("net_delta", 0)
            return net_delta > 0
        except Exception as exc:
            logger.debug("IVBandBreakout: failed to check ATM delta: %s", exc)
            return False

    @staticmethod
    def _check_atm_delta_negative(gex_calc: Any, atm_strike: float) -> bool:
        """
        Check if net delta at the ATM strike is negative.

        Net delta < 0 means delta is turning negative.
        """
        try:
            delta_data = gex_calc.get_delta_by_strike(atm_strike)
            net_delta = delta_data.get("net_delta", 0)
            return net_delta < 0
        except Exception as exc:
            logger.debug("IVBandBreakout: failed to check ATM delta: %s", exc)
            return False

    def _compute_long_confidence(
        self,
        iv_depth: float,
        rolling_data: Dict[str, Any],
        delta_decel: float,
        vol_trend: str,
        net_gamma: float,
    ) -> float:
        """
        Compute confidence for LONG breakout signal.

        Factors:
            1. IV compression depth     (0.30–0.45)
            2. Price compression tightness (0.05–0.15)
            3. Delta deceleration       (0.05–0.10)
            4. Volume confirmation      (0.05–0.10)
            5. Regime alignment         (0.0–0.10)

        Returns 0.0–MAX_CONFIDENCE.
        """
        # 1. IV compression depth (0.30–0.45)
        # Deeper compression = higher confidence
        iv_conf = 0.30 + 0.15 * min(1.0, iv_depth / 0.20)

        # 2. Price compression tightness (0.05–0.15)
        # Tighter range = more coiled = higher confidence
        ratio = self._get_price_compression_ratio(rolling_data)
        compression_conf = 0.15 * (1 - ratio)  # lower ratio = higher conf

        # 3. Delta deceleration (0.05–0.10)
        # More negative ratio = more coiling = higher confidence
        deviation = max(0, DELTA_DECEL_RATIO - delta_decel)
        delta_conf = 0.05 + 0.05 * min(1.0, deviation / DELTA_DECEL_RATIO)

        # 4. Volume confirmation (0.05–0.10)
        vol_conf = 0.10 if vol_trend == "UP" else 0.05

        # 5. Regime alignment (0.0–0.10)
        # Positive gamma regime adds confidence
        regime_conf = 0.10

        # Normalize each component to [0,1] and average
        norm_iv = (iv_conf - 0.30) / (0.45 - 0.30) if 0.45 != 0.30 else 1.0
        norm_comp = compression_conf / 0.15 if 0.15 != 0 else 0.0
        norm_delta = (delta_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_vol = (vol_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_regime = regime_conf / 0.10 if 0.10 != 0 else 0.0
        confidence = (norm_iv + norm_comp + norm_delta + norm_vol + norm_regime) / 5.0
        return min(MAX_CONFIDENCE, max(0.0, confidence))

    def _compute_short_confidence(
        self,
        iv_depth: float,
        rolling_data: Dict[str, Any],
        delta_decel: float,
        vol_trend: str,
        net_gamma: float,
    ) -> float:
        """
        Compute confidence for SHORT breakout signal.

        Same factors as LONG but with SHORT-specific volume check.

        Factors:
            1. IV compression depth     (0.30–0.45)
            2. Price compression tightness (0.05–0.15)
            3. Delta deceleration       (0.05–0.10)
            4. Volume confirmation      (0.05–0.10)
            5. Regime alignment         (0.0–0.10)

        Returns 0.0–MAX_CONFIDENCE.
        """
        # 1. IV compression depth (0.30–0.45)
        iv_conf = 0.30 + 0.15 * min(1.0, iv_depth / 0.20)

        # 2. Price compression tightness (0.05–0.15)
        ratio = self._get_price_compression_ratio(rolling_data)
        compression_conf = 0.15 * (1 - ratio)

        # 3. Delta deceleration (0.05–0.10)
        deviation = max(0, DELTA_DECEL_RATIO - delta_decel)
        delta_conf = 0.05 + 0.05 * min(1.0, deviation / DELTA_DECEL_RATIO)

        # 4. Volume confirmation (0.05–0.10)
        vol_conf = 0.10 if vol_trend == "DOWN" else 0.05

        # 5. Regime alignment (0.0–0.10)
        regime_conf = 0.10

        # Normalize each component to [0,1] and average
        norm_iv = (iv_conf - 0.30) / (0.45 - 0.30) if 0.45 != 0.30 else 1.0
        norm_comp = compression_conf / 0.15 if 0.15 != 0 else 0.0
        norm_delta = (delta_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_vol = (vol_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_regime = regime_conf / 0.10 if 0.10 != 0 else 0.0
        confidence = (norm_iv + norm_comp + norm_delta + norm_vol + norm_regime) / 5.0
        return min(MAX_CONFIDENCE, max(0.0, confidence))
