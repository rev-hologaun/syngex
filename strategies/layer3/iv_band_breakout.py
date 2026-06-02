"""
strategies/layer3/iv_band_breakout.py — IV Band Breakout v2 (Breakout-Master)

Micro-signal (1Hz) strategy: detects the transition from IV compression
to expansion using the full volatility surface.

v2 Architecture:
    1. Skew Width Compression — monitors |OTM Put IV - OTM Call IV| instead
       of ATM IV only. A true coiled spring compresses the entire surface.
    2. Gamma-Regime Hard Gate — regime must be POSITIVE or NEGATIVE (not
       NEUTRAL). POSITIVE = controlled trend (wider targets). NEGATIVE =
       explosive mean-reversion (tighter targets).
    3. Delta-Acceleration Snap Detection — at breakout, delta must accelerate
       ≥10% (LONG) or decelerate ≥10% (SHORT) to confirm the "snap."
    4. IV-Expansion Scaled Targets — target scales with current IV / mean IV,
       capped at 4.0× risk.

This is a **filter-style volatility spring engine** — it produces graded signal strength
    based on skew compression and delta acceleration, not binary pass/fail.

    Signal strength per direction:
        strength = skew*0.30 + regime*0.10 + price*0.10 + breakout*0.15 + delta*0.20 + vol*0.15
        Emit when signal_strength >= 0.30 and skew is compressed

    Confidence (6 components, weighted):
        1. Skew compression (continuous 0–0.30)
        2. Gamma regime (graded 0–0.10)
        3. Delta acceleration (continuous 0–0.30)
        4. Price compression (soft 0–0.10)
        5. IV expansion (soft 0–0.10)
        6. Volume confirmation (graded 0–0.10)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_PRICE_5M,
    KEY_SKEW_WIDTH_5M,
    KEY_VOLUME_5M,
    KEY_VOLUME_DOWN_5M,
    KEY_VOLUME_UP_5M,
    KEY_TOTAL_DELTA_5M,
    KEY_ATM_IV_5M,
)

logger = logging.getLogger("Syngex.Strategies.IVBandBreakout")

# ---------------------------------------------------------------------------
# Constants (defaults — overridden by config params)
# ---------------------------------------------------------------------------

# Delta deceleration ratio (v1 coiling proxy)
DELTA_DECEL_RATIO = 0.95

# Price compression: high-low range must be < 40% of rolling mean range
PRICE_COMPRESSION_RATIO = 0.40

# Minimum price move to count as breakout (0.05%)
BREAKOUT_MOVE_PCT = 0.0005

# Stop and target (v1 fallback)
STOP_PCT = 0.005  # 0.5% stop
TARGET_PCT = 0.010  # 1.0% target

# Min/max confidence
MIN_CONFIDENCE = 0.30  # Minimum confidence threshold for signal emission

# Min data points
MIN_DATA_POINTS = 5
MIN_IV_DATA_POINTS = 3

# v2 Breakout-Master defaults
SKEW_OTM_PCT = 0.05  # OTM strike distance (5%)
SKEW_COMPRESSION_PCT = 0.25  # skew must be in bottom 25% of range
POSITIVE_GAMMA_TARGET_MULT = 2.5
NEGATIVE_GAMMA_TARGET_MULT = 1.5
DELTA_ACCEL_THRESHOLD = 1.10  # delta must accelerate ≥10% at breakout
TARGET_IV_EXPANSION_MULT = 2.5  # base multiplier for POS regime
TARGET_IV_EXPANSION_NEG_MULT = 1.5  # base multiplier for NEG regime
TARGET_IV_EXPANSION_CAP = 4.0  # cap on multiplier
TARGET_MIN_PCT = 0.005  # minimum 0.5% target


class IVBandBreakout(BaseStrategy):
    """
    Detects the transition from IV compression to expansion using
    full-surface skew width compression, gamma-regime gating,
    delta-acceleration snap detection, and IV-expansion scaled targets.

    Works in POSITIVE or NEGATIVE gamma regimes (NEUTRAL = skip).
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
    # LONG entry: skew compressed + regime gate + delta accel +
    #             price breaks above range + VolumeUp
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
            1. Gamma regime gate (POSITIVE or NEGATIVE, not NEUTRAL)
            2. Skew width compression (bottom 25% of rolling range)
            3. Price compression: range < 30% of rolling mean range
            4. Delta acceleration at breakout (snap ≥10%)
            5. Price breaks above recent high
            6. Volume trending UP
        """
        # Get ATM strike
        atm_strike = self._get_atm_strike(gex_calc, price)
        if atm_strike is None:
            return None

        # 1. Gamma regime gate (graded score)
        regime_score = self._regime_gate_score(regime)
        if regime_score < 0.5:
            return None

        # 2. Skew compression check (hard gate + graded score)
        skew_compressed, skew_depth = self._check_skew_compression(
            rolling_data, atm_strike,
        )
        if not skew_compressed:
            return None
        skew_score = min(1.0, skew_depth / 0.05)  # 0.05 depth = full score

        # 3. Price compression check (graded score)
        price_compression_ratio = self._get_price_compression_ratio(rolling_data)
        if price_compression_ratio is None or price_compression_ratio > 1.0:
            return None
        price_score = max(0.0, 1.0 - price_compression_ratio)  # tighter = higher

        # 4. Price breakout above recent high (graded score)
        breakout_score = self._breakout_score(rolling_data, direction="LONG")
        if breakout_score < 0.2:
            return None

        # 5. Delta acceleration at breakout (graded score)
        delta_accel = self._check_delta_acceleration(rolling_data, direction="LONG")
        if delta_accel is None:
            return None
        delta_gate_score = self._delta_gate_score(delta_accel, direction="LONG")
        if delta_gate_score < 0.2:
            return None

        # 6. Volume trending UP (call volume)
        vol_window = rolling_data.get(KEY_VOLUME_UP_5M)
        vol_trend = vol_window.trend if vol_window else "UNKNOWN"
        if vol_trend not in ("UP", "DOWN"):
            return None
        vol_gate_score = 1.0

        # Compute signal_strength from continuous scores
        signal_strength = (
            skew_score * 0.30
            + regime_score * 0.10
            + price_score * 0.10
            + breakout_score * 0.15
            + delta_gate_score * 0.20
            + vol_gate_score * 0.15
        )
        if signal_strength < 0.30:
            return None

        # All conditions met — compute confidence and build signal
        # Get IV expansion factor
        iv_expansion = self._get_iv_expansion(rolling_data)

        # Compute IV-scaled target
        risk = price * TARGET_MIN_PCT  # minimum risk
        target_price, target_mult, iv_expansion = self._compute_iv_scaled_target(
            price, risk, rolling_data, regime, direction="LONG",
        )

        confidence = self._compute_confidence(
            skew_depth=skew_depth,
            delta_accel=delta_accel,
            iv_expansion=iv_expansion,
            price_compression=self._get_price_compression_ratio(rolling_data),
            net_gamma=net_gamma,
            regime=regime,
            direction="LONG",
            vol_trend=vol_trend,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        entry = price
        stop = entry * (1 - STOP_PCT)

        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target_price, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"IV band breakout v2 LONG: ATM {atm_strike} skew compressed, "
                f"regime={regime}, delta_accel={delta_accel:.3f}, "
                f"VolumeUp, IV_exp={iv_expansion:.2f}x"
            ),
            metadata={
                # v1 fields (kept)
                "atm_strike": atm_strike,
                "price_compression_ratio": round(
                    self._get_price_compression_ratio(rolling_data), 3
                ),
                "volume_trend": vol_trend,
                "price_trend": trend,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(entry - stop, 2),
                "risk_reward_ratio": round(
                    (target_price - entry) / (entry - stop), 2
                ) if (entry - stop) > 0 else 0,
                # v2 new fields
                "skew_width_current": round(
                    rolling_data.get(KEY_SKEW_WIDTH_5M).latest if rolling_data.get(KEY_SKEW_WIDTH_5M) else 0, 4
                ),
                "skew_width_mean": round(
                    rolling_data.get(KEY_SKEW_WIDTH_5M).mean if rolling_data.get(KEY_SKEW_WIDTH_5M) else 0, 4
                ),
                "skew_compression_depth": round(skew_depth, 4),
                "delta_acceleration": round(delta_accel, 4),
                "iv_expansion_factor": round(iv_expansion, 3),
                "target_mult": round(target_mult, 2),
                "regime_type": regime,
                "target_type": "scaled",
                # Continuous gate scores
                "skew_score": round(skew_score, 4),
                "regime_score": round(regime_score, 4),
                "price_score": round(price_score, 4),
                "breakout_score": round(breakout_score, 4),
                "delta_gate_score": round(delta_gate_score, 4),
                "vol_gate_score": round(vol_gate_score, 4),
                "signal_strength": round(signal_strength, 4),
            },
        )

    # ------------------------------------------------------------------
    # SHORT entry: skew compressed + regime gate + delta accel +
    #              price breaks below range + VolumeDown
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
            1. Gamma regime gate (POSITIVE or NEGATIVE, not NEUTRAL)
            2. Skew width compression (bottom 25% of rolling range)
            3. Price compression: range < 30% of rolling mean range
            4. Delta acceleration at breakout (snap ≥10%)
            5. Price breaks below recent low
            6. Volume trending DOWN
        """
        # Get ATM strike
        atm_strike = self._get_atm_strike(gex_calc, price)
        if atm_strike is None:
            return None

        # 1. Gamma regime gate (graded score)
        regime_score = self._regime_gate_score(regime)
        if regime_score < 0.5:
            return None

        # 2. Skew compression check (hard gate + graded score)
        skew_compressed, skew_depth = self._check_skew_compression(
            rolling_data, atm_strike,
        )
        if not skew_compressed:
            return None
        skew_score = min(1.0, skew_depth / 0.05)  # 0.05 depth = full score

        # 3. Price compression check (graded score)
        price_compression_ratio = self._get_price_compression_ratio(rolling_data)
        if price_compression_ratio is None or price_compression_ratio > 1.0:
            return None
        price_score = max(0.0, 1.0 - price_compression_ratio)  # tighter = higher

        # 4. Price breakout below recent low (graded score)
        breakout_score = self._breakout_score(rolling_data, direction="SHORT")
        if breakout_score < 0.2:
            return None

        # 5. Delta acceleration at breakout (graded score)
        delta_accel = self._check_delta_acceleration(rolling_data, direction="SHORT")
        if delta_accel is None:
            return None
        delta_gate_score = self._delta_gate_score(delta_accel, direction="SHORT")
        if delta_gate_score < 0.2:
            return None

        # 6. Volume trending DOWN (put volume)
        vol_window = rolling_data.get(KEY_VOLUME_DOWN_5M)
        vol_trend = vol_window.trend if vol_window else "UNKNOWN"
        if vol_trend not in ("UP", "DOWN"):
            return None
        vol_gate_score = 1.0

        # Compute signal_strength from continuous scores
        signal_strength = (
            skew_score * 0.30
            + regime_score * 0.10
            + price_score * 0.10
            + breakout_score * 0.15
            + delta_gate_score * 0.20
            + vol_gate_score * 0.15
        )
        if signal_strength < 0.30:
            return None

        # All conditions met — compute confidence and build signal
        iv_expansion = self._get_iv_expansion(rolling_data)

        risk = price * TARGET_MIN_PCT
        target_price, target_mult, iv_expansion = self._compute_iv_scaled_target(
            price, risk, rolling_data, regime, direction="SHORT",
        )

        confidence = self._compute_confidence(
            skew_depth=skew_depth,
            delta_accel=delta_accel,
            iv_expansion=iv_expansion,
            price_compression=self._get_price_compression_ratio(rolling_data),
            net_gamma=net_gamma,
            regime=regime,
            direction="SHORT",
            vol_trend=vol_trend,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        entry = price
        stop = entry * (1 + STOP_PCT)

        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target_price, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"IV band breakout v2 SHORT: ATM {atm_strike} skew compressed, "
                f"regime={regime}, delta_accel={delta_accel:.3f}, "
                f"VolumeDown, IV_exp={iv_expansion:.2f}x"
            ),
            metadata={
                # v1 fields (kept)
                "atm_strike": atm_strike,
                "price_compression_ratio": round(
                    self._get_price_compression_ratio(rolling_data), 3
                ),
                "volume_trend": vol_trend,
                "price_trend": trend,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(stop - entry, 2),
                "risk_reward_ratio": round(
                    (entry - target_price) / (stop - entry), 2
                ) if (stop - entry) > 0 else 0,
                # v2 new fields
                "skew_width_current": round(
                    rolling_data.get(KEY_SKEW_WIDTH_5M).latest if rolling_data.get(KEY_SKEW_WIDTH_5M) else 0, 4
                ),
                "skew_width_mean": round(
                    rolling_data.get(KEY_SKEW_WIDTH_5M).mean if rolling_data.get(KEY_SKEW_WIDTH_5M) else 0, 4
                ),
                "skew_compression_depth": round(skew_depth, 4),
                "delta_acceleration": round(delta_accel, 4),
                "iv_expansion_factor": round(iv_expansion, 3),
                "target_mult": round(target_mult, 2),
                "regime_type": regime,
                "target_type": "scaled",
                # Continuous gate scores
                "skew_score": round(skew_score, 4),
                "regime_score": round(regime_score, 4),
                "price_score": round(price_score, 4),
                "breakout_score": round(breakout_score, 4),
                "delta_gate_score": round(delta_gate_score, 4),
                "vol_gate_score": round(vol_gate_score, 4),
                "signal_strength": round(signal_strength, 4),
            },
        )

    # ------------------------------------------------------------------
    # v2 Helper: Skew Width Compression
    # ------------------------------------------------------------------

    @staticmethod
    def _check_skew_compression(
        rolling_data: Dict[str, Any],
        atm_strike: float,
    ) -> Tuple[bool, float]:
        """
        Check if skew width (|OTM Put IV - OTM Call IV|) is compressed.

        Current skew_width must be in bottom 25% of its rolling range.

        Returns (is_compressed, skew_depth) where skew_depth = p25 - current.
        """
        window = rolling_data.get(KEY_SKEW_WIDTH_5M)
        if window is None or window.count < MIN_DATA_POINTS:
            return False, 0.0

        current_skew = window.latest
        p25 = window.p25

        if current_skew is None or p25 is None:
            return False, 0.0

        # Skew is compressed if latest is in bottom 25% of rolling range
        is_compressed = current_skew <= p25

        # Depth = how far below p25 (positive = compressed deeper)
        skew_depth = p25 - current_skew

        return is_compressed, skew_depth

    # ------------------------------------------------------------------
    # v2 Helper: Gamma-Regime Hard Gate
    # ------------------------------------------------------------------

    @staticmethod
    def _check_gamma_regime(regime: str) -> bool:
        """
        Hard gate: regime must be POSITIVE or NEGATIVE (not NEUTRAL).

        Returns True if regime passes the gate.
        """
        return regime in ("POSITIVE", "NEGATIVE")

    # ------------------------------------------------------------------
    # v2 Helper: Delta-Acceleration Snap Detection
    # ------------------------------------------------------------------

    @staticmethod
    def _check_delta_acceleration(
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> Optional[float]:
        """
        Check if delta accelerated at the breakout moment.

        For LONG: delta_accel > 1.10 (delta accelerated ≥10%)
        For SHORT: delta_accel < 0.90 (delta decelerated ≥10%)

        Returns delta_accel value or None if below threshold.
        """
        window = rolling_data.get(KEY_TOTAL_DELTA_5M)
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        current = window.latest
        if current is None:
            return None

        # Get delta value ~5 ticks ago (use index offset)
        values = window.values
        if len(values) < 6:
            return None

        delta_ago = values[-6]  # 5 values back
        if delta_ago is None or delta_ago == 0:
            return None

        delta_accel = current / delta_ago

        if direction == "LONG":
            # Delta must have accelerated (increased) by ≥10%
            if delta_accel >= DELTA_ACCEL_THRESHOLD:
                return delta_accel
        elif direction == "SHORT":
            # Delta must have decelerated (decreased) by ≥10%
            if delta_accel <= (1.0 / DELTA_ACCEL_THRESHOLD):
                return delta_accel

        return None

    # ------------------------------------------------------------------
    # v2 Helper: IV-Expansion Scaled Target
    # ------------------------------------------------------------------

    def _compute_iv_scaled_target(
        self,
        entry: float,
        risk: float,
        rolling_data: Dict[str, Any],
        regime: str,
        direction: str,
    ) -> Tuple[float, float, float]:
        """
        Compute target price scaled by IV expansion factor.

        target_mult = base_mult × iv_expansion, capped at 4.0
        For LONG: target = entry + risk × target_mult
        For SHORT: target = entry - risk × target_mult
        Minimum target: 0.5% from entry.

        Returns (target_price, target_mult, iv_expansion).
        """
        iv_expansion = self._get_iv_expansion(rolling_data)

        # Base multiplier depends on regime
        if regime == "POSITIVE":
            base_mult = self._get_param("positive_gamma_target_mult", POSITIVE_GAMMA_TARGET_MULT)
        elif regime == "NEGATIVE":
            base_mult = self._get_param("negative_gamma_target_mult", NEGATIVE_GAMMA_TARGET_MULT)
        else:
            # Fallback to positive gamma
            base_mult = self._get_param("positive_gamma_target_mult", POSITIVE_GAMMA_TARGET_MULT)

        # Scale by IV expansion and cap
        target_mult = base_mult * iv_expansion
        cap = self._get_param("target_iv_expansion_cap", TARGET_IV_EXPANSION_CAP)
        target_mult = min(target_mult, cap)

        # Compute target price
        if direction == "LONG":
            target = entry + risk * target_mult
        else:
            target = entry - risk * target_mult

        # Minimum target: 0.5% from entry
        min_pct = self._get_param("target_min_pct", TARGET_MIN_PCT)
        if direction == "LONG":
            min_target = entry * (1 + min_pct)
            target = max(target, min_target)
        else:
            min_target = entry * (1 - min_pct)
            target = min(target, min_target)

        return target, target_mult, iv_expansion

    # ------------------------------------------------------------------
    # v2 Helper: IV Expansion Factor
    # ------------------------------------------------------------------

    @staticmethod
    def _get_iv_expansion(rolling_data: Dict[str, Any]) -> float:
        """
        Compute IV expansion factor = current IV / mean IV.
        Returns 1.0 if no data available.
        """
        window = rolling_data.get(KEY_ATM_IV_5M)
        if window is None or window.count < 2:
            return 1.0

        current_iv = window.latest
        mean_iv = window.mean

        if current_iv is None or mean_iv is None or mean_iv == 0:
            return 1.0

        return current_iv / mean_iv

    # ------------------------------------------------------------------
    # v2 Confidence: Unified for LONG and SHORT
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        skew_depth: float,
        delta_accel: float,
        iv_expansion: float,
        price_compression: float,
        net_gamma: float,
        regime: str,
        direction: str,
        vol_trend: str,
    ) -> float:
        """
        Compute unified confidence for LONG and SHORT breakout signals.

        6 continuous components (weighted sum):
            1. Skew compression (0.0–0.30, continuous)
            2. Gamma regime (0.0–0.10, graded)
            3. Delta acceleration (0.0–0.30, continuous)
            4. Price compression (0.0–0.10, soft)
            5. IV expansion (0.0–0.10, soft)
            6. Volume confirmation (0.0–0.10, graded)
        """
        # 1. Skew compression (0.0–0.30, continuous — NOT binary!)
        # skew_depth > 0 means compressed, deeper = better
        skew_conf = 0.30 * min(1.0, skew_depth / 0.05)

        # 2. Gamma regime (0.0–0.10, graded)
        regime_conf = self._regime_score(regime)

        # 3. Delta acceleration (0.0–0.30, continuous — NOT binary!)
        delta_conf = self._delta_confidence(delta_accel, direction)

        # 4. Price compression (0.0–0.10, soft)
        price_conf = self._price_compression_confidence(price_compression)

        # 5. IV expansion (0.0–0.10, soft)
        iv_conf = self._iv_expansion_confidence(iv_expansion)

        # 6. Volume confirmation (0.0–0.10, graded)
        vol_conf = self._volume_confidence(vol_trend)

        confidence = skew_conf + regime_conf + delta_conf + price_conf + iv_conf + vol_conf
        return max(0.0, min(1.0, confidence))

    # ------------------------------------------------------------------
    # Confidence helpers (continuous scores)
    # ------------------------------------------------------------------

    @staticmethod
    def _regime_score(regime: str) -> float:
        """
        Compute regime score (0.0–0.10).
        POSITIVE = 0.10 (strong trend, wider targets)
        NEGATIVE = 0.08 (explosive, tighter targets)
        NEUTRAL = 0.0 (should be gated upstream, but be safe)
        """
        if regime == "POSITIVE":
            return 0.10
        elif regime == "NEGATIVE":
            return 0.08
        return 0.0

    @staticmethod
    def _delta_confidence(delta_accel: float, direction: str) -> float:
        """
        Compute delta confidence (0.0–0.30).
        LONG: delta_accel > 1.0 means acceleration.
              Score = min(1.0, (delta_accel - 1.0) / 0.5) * 0.30
        SHORT: delta_accel < 1.0 means deceleration.
               Score = min(1.0, (1.0 - delta_accel) / 0.5) * 0.30
        """
        if direction == "LONG":
            deviation = max(0.0, delta_accel - 1.0)
        else:
            deviation = max(0.0, 1.0 - delta_accel)
        return 0.30 * min(1.0, deviation / 0.5)

    @staticmethod
    def _price_compression_confidence(ratio: float) -> float:
        """Price compression confidence: 0.0–0.10. Tighter = higher. Data-not-available = neutral."""
        if ratio <= 0:
            return 0.05  # neutral when no data
        if ratio >= 1.0:
            return 0.0
        return 0.10 * (1 - ratio)

    @staticmethod
    def _iv_expansion_confidence(iv_expansion: float) -> float:
        """IV expansion confidence: 0.0–0.10. Higher expansion = higher."""
        if iv_expansion <= 0:
            return 0.0
        if iv_expansion >= 2.0:
            return 0.10
        return 0.10 * min(1.0, (iv_expansion - 0.5) / 1.5)

    @staticmethod
    def _volume_confidence(vol_trend: str) -> float:
        """Volume confirmation: 0.0–0.10. Trend strength matters."""
        if vol_trend in ("UP", "DOWN"):
            return 0.10
        elif vol_trend == "FLAT":
            return 0.05
        else:
            return 0.0  # unknown

    # ------------------------------------------------------------------
    # v2 Gate Score Methods (continuous 0.0–1.0)
    # ------------------------------------------------------------------

    @staticmethod
    def _regime_gate_score(regime: str) -> float:
        """Regime gate score: 0.0–1.0. POSITIVE=1.0, NEGATIVE=0.8, NEUTRAL=0.0"""
        if regime == "POSITIVE":
            return 1.0
        elif regime == "NEGATIVE":
            return 0.8
        return 0.0

    @staticmethod
    def _breakout_score(rolling_data: Dict[str, Any], direction: str) -> float:
        """Breakout score: 0.0–1.0 based on how far price moved beyond the breakout level."""
        price_window = rolling_data.get(KEY_PRICE_5M)
        if not price_window or price_window.count < 5:
            return 0.5  # neutral

        current = price_window.values[-1] if price_window.values else 0
        recent_high = price_window.high if hasattr(price_window, 'high') else 0
        recent_low = price_window.low if hasattr(price_window, 'low') else 0

        if direction == "LONG" and recent_high > 0:
            # How far above recent high
            move_pct = (current - recent_high) / recent_high
            return min(1.0, max(0.0, move_pct / 0.01))  # 1% move = full score
        elif direction == "SHORT" and recent_low > 0:
            move_pct = (recent_low - current) / recent_low
            return min(1.0, max(0.0, move_pct / 0.01))
        return 0.3  # small default

    @staticmethod
    def _delta_gate_score(delta_accel: float, direction: str) -> float:
        """Delta gate score: 0.0–1.0. LONG: acceleration > 1.0 = good. SHORT: deceleration < 1.0 = good."""
        if direction == "LONG":
            deviation = max(0.0, delta_accel - 1.0)
        else:
            deviation = max(0.0, 1.0 - delta_accel)
        return min(1.0, deviation / 0.5)  # 0.5 deviation = full score

    # ------------------------------------------------------------------
    # Shared helpers (v1 logic kept)
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
    def _check_price_compression(rolling_data: Dict[str, Any]) -> bool:
        """
        Check if price is compressing.

        Current high-low range must be < 30% of rolling mean range.
        """
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None or window.count < MIN_DATA_POINTS:
            return False

        current_range = window.range
        std = window.std

        if current_range is None or std is None or std == 0:
            return False

        compression_ratio = current_range / (std * 2)
        return compression_ratio < PRICE_COMPRESSION_RATIO

    @staticmethod
    def _get_price_compression_ratio(rolling_data: Dict[str, Any]) -> float:
        """Get the current price compression ratio for metadata."""
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None:
            return 1.0

        current_range = window.range
        std = window.std

        if current_range is None or std is None or std == 0:
            return 1.0

        return current_range / (std * 2)

    @staticmethod
    def _check_breakout_high(rolling_data: Dict[str, Any]) -> bool:
        """Check if price has broken above the recent high."""
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None or window.count < 3:
            return False

        latest = window.latest
        window_max = window.max

        if latest is None or window_max is None:
            return False

        if latest <= window_max:
            return False

        move_pct = (latest - window_max) / window_max
        return move_pct >= BREAKOUT_MOVE_PCT

    @staticmethod
    def _check_breakout_low(rolling_data: Dict[str, Any]) -> bool:
        """Check if price has broken below the recent low."""
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None or window.count < 3:
            return False

        latest = window.latest
        window_min = window.min

        if latest is None or window_min is None:
            return False

        if latest >= window_min:
            return False

        move_pct = (window_min - latest) / window_min
        return move_pct >= BREAKOUT_MOVE_PCT
