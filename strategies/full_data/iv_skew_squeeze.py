"""
strategies/full_data/iv_skew_squeeze.py — IV Skew Squeeze v2 (Skew-Velocity)

Full-data (v2) strategy: trades IV skew extremes with velocity confirmation.
When the options market is pricing in extreme fear (negative skew) or euphoria
(positive skew) but price isn't actually moving in that direction, the skew
is likely to normalize — trade the reversal.

v2 upgrades (Skew-Velocity):
    1. Skew Acceleration (ROC) — signal only valid when skew rapidly collapses toward zero
    2. Volume-Weighted Stability — stability on high volume = true conviction
    3. Delta-Skew Convergence — delta flow must align with skew normalization
    4. IV-Expansion Scaled Targets — dynamic exit based on IV expansion factor

Logic:
    - Calculate IV Skew = avg_call_iv - avg_put_iv across the chain
    - Extreme positive skew (>0.20) + price stable + net gamma positive → SHORT
      (euphoria: calls are expensive but price isn't breaking out)
    - Extreme negative skew (<-0.07) + price stable + net gamma positive → LONG
      (panic: puts are expensive but price isn't breaking down)
    - Skew normalization confirms the trade (skew moving toward zero)
    - Net gamma positive required for stability

Confidence factors (6 components, unified for LONG and SHORT):
    1. Skew acceleration (hard gate, 0.20–0.30) — skew ROC toward zero
    2. Volume-weighted stability (hard gate, 0.15–0.25) — price stable on meaningful volume
    3. Delta-skew convergence (hard gate, 0.15–0.20) — delta flow aligns with skew
    4. Skew extremity (soft, 0.10–0.15) — how far from zero
    5. Volume alignment (soft, 0.05–0.10) — no opposite volume spike
    6. Net gamma strength (soft, 0.05–0.10) — stable environment
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_window import RollingWindow
from strategies.rolling_keys import (
    KEY_PRICE_5M,
    KEY_VOLUME_5M,
    KEY_IV_SKEW_5M,
    KEY_SKEW_ROC_5M,
    KEY_DELTA_ROC_5M,
    KEY_ATM_IV_5M,
)

logger = logging.getLogger("Syngex.Strategies.IVSkewSqueeze")


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# IV Skew thresholds
SKEW_EXTREME_POSITIVE = 0.20       # Calls 20%+ more expensive (euphoria)
SKEW_EXTREME_NEGATIVE = -0.07      # Puts 7%+ more expensive (panic)

# Price stability: price change must be < this % over 5m
PRICE_STABLE_THRESHOLD = 0.005     # 0.5% change max

# Min net gamma for positive regime confirmation
MIN_NET_GAMMA = 500000.0  # 500k — matches other strategies' thresholds

# Stop and target
STOP_PCT = 0.005                   # 0.5% stop
TARGET_PCT = 0.008                 # 0.8% target (1.6:1 R:R)

# Min confidence — raised from 0.25 to 0.35 for v2
MIN_CONFIDENCE = 0.30

# Min data points
MIN_DATA_POINTS = 5                # Need data for basic checks
MIN_SKEW_DATA_POINTS = 5           # Minimum for skew rolling window

# Volume spike check
VOLUME_SPIKE_THRESHOLD = 1.5       # Volume > 1.5× avg = spike

# v2 Skew-Velocity params
SKEW_ROC_THRESHOLD = 0.05          # 5% ROC for skew acceleration
VOL_WEIGHTED_STABILITY_MIN = 0.50  # min conviction stability
VOL_FRAGILE_THRESHOLD = 0.30       # volume < 30% avg = fragile
DELTA_ROC_THRESHOLD = 0.05         # 5% ROC for delta confirmation
TARGET_IV_EXPANSION_MULT = 1.6     # base multiplier for IV-scaled target
TARGET_IV_EXPANSION_CAP = 2.0      # cap on target multiplier
TARGET_MIN_PCT = 0.005             # minimum target 0.5%


class IVSkewSqueeze(BaseStrategy):
    """
    IV Skew Squeeze v2 — Skew-Velocity upgrade.

    Trades mean-reversion of IV skew extremes with velocity confirmation.
    When the options market prices in extreme fear or euphoria but price
    isn't actually moving in that direction, the skew is likely to normalize.

    v2 upgrades:
        - Skew ROC acceleration (leading indicator)
        - Volume-weighted stability (conviction filter)
        - Delta-skew convergence (confirmation)
        - IV-expansion scaled targets (dynamic exit)

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

        # --- Use main.py's populated skew window ---
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        if skew_window is None:
            return []

        # --- Compute current IV skew ---
        try:
            current_skew = gex_calc.get_iv_skew()
        except Exception:
            return []

        if current_skew is None:
            return []

        # Check minimum data points
        if skew_window.count < MIN_SKEW_DATA_POINTS:
            return []

        # --- Get price data ---
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window is None or price_window.count < MIN_DATA_POINTS:
            return []

        price_change_pct = price_window.change_pct
        if price_change_pct is None:
            return []

        # --- Get volume data ---
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window is None or volume_window.count < MIN_DATA_POINTS:
            return []

        # --- Get net gamma ---
        if net_gamma < MIN_NET_GAMMA:
            return []

        # --- Check for LONG (panic overblown) ---
        long_sig = self._check_long(
            current_skew, skew_window, price_window, volume_window,
            rolling_data, underlying_price, net_gamma, data,
        )

        # --- Check for SHORT (euphoria overblown) ---
        short_sig = self._check_short(
            current_skew, skew_window, price_window, volume_window,
            rolling_data, underlying_price, net_gamma, data,
        )

        signals: List[Signal] = []
        if long_sig:
            signals.append(long_sig)
        if short_sig:
            signals.append(short_sig)

        return signals

    # ------------------------------------------------------------------
    # Skew-Velocity Hard Gates
    # ------------------------------------------------------------------

    def _check_skew_acceleration(
        self,
        skew_roc_window: Optional[RollingWindow],
        direction: str,
    ) -> Optional[float]:
        """
        Check skew acceleration (ROC) toward zero.

        For LONG (negative skew): skew_roc > 0.05 (skew accelerating toward zero
        from negative side — becoming less negative)
        For SHORT (positive skew): skew_roc < -0.05 (skew accelerating toward zero
        from positive side — becoming less positive)

        Returns skew_roc value if passes threshold, None otherwise.
        """
        if skew_roc_window is None or skew_roc_window.count < 1:
            return None

        skew_roc = skew_roc_window.latest
        if skew_roc is None:
            return None

        if direction == Direction.LONG:
            # Negative skew normalizing: skew becomes less negative → positive ROC
            if skew_roc > SKEW_ROC_THRESHOLD:
                return skew_roc
        else:
            # Positive skew normalizing: skew becomes less positive → negative ROC
            if skew_roc < -SKEW_ROC_THRESHOLD:
                return skew_roc

        return None

    def _check_volume_weighted_stability(
        self,
        price_window: RollingWindow,
        volume_window: RollingWindow,
        direction: str,
    ) -> Tuple[bool, float]:
        """
        Check volume-weighted stability.

        Price stable on high volume = true conviction.
        Price stable on low volume = fragile equilibrium.

        Returns (passes, conviction_stability).
        """
        price_change = abs(price_window.change_pct or 0)
        price_stability = 1.0 - min(1.0, price_change / PRICE_STABLE_THRESHOLD)

        # Volume intensity
        current_vol = volume_window.latest
        avg_vol = volume_window.mean
        if current_vol is None or avg_vol is None or avg_vol == 0:
            return (False, 0.0)

        vol_ratio = current_vol / avg_vol

        # Extremely low volume = fragile stability
        if vol_ratio < VOL_FRAGILE_THRESHOLD:
            return (False, 0.0)

        conviction_stability = price_stability / vol_ratio

        # Hard gate: conviction_stability > 0.50
        if conviction_stability < VOL_WEIGHTED_STABILITY_MIN:
            return (False, 0.0)

        return (True, conviction_stability)

    def _check_delta_skew_convergence(
        self,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> Optional[float]:
        """
        Check delta-skew convergence.

        For LONG (negative skew normalizing): delta should be turning positive
        (delta_roc > 0).
        For SHORT (positive skew normalizing): delta should be turning negative
        (delta_roc < 0).

        Returns delta_roc value if passes, None otherwise.
        """
        delta_roc_window = rolling_data.get(KEY_DELTA_ROC_5M)
        if delta_roc_window is None or delta_roc_window.count < 1:
            return None

        delta_roc = delta_roc_window.latest
        if delta_roc is None:
            return None

        if direction == Direction.LONG:
            # Negative skew normalizing → delta should turn positive
            if delta_roc > DELTA_ROC_THRESHOLD:
                return delta_roc
        else:
            # Positive skew normalizing → delta should turn negative
            if delta_roc < -DELTA_ROC_THRESHOLD:
                return delta_roc

        return None

    def _compute_iv_scaled_target(
        self,
        entry: float,
        risk: float,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> float:
        """
        Compute IV-expansion scaled target.

        target = entry ± risk * TARGET_IV_EXPANSION_MULT * iv_factor
        where iv_factor = current_iv / mean_iv, capped at TARGET_IV_EXPANSION_CAP.
        Minimum target: 0.5% from entry.
        """
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        if iv_window is not None and iv_window.count >= 2:
            current_iv = iv_window.latest or 0.0
            mean_iv = iv_window.mean or 0.0
            if current_iv > 0 and mean_iv > 0:
                iv_factor = current_iv / mean_iv
            else:
                iv_factor = 1.0
        else:
            iv_factor = 1.0

        base_mult = TARGET_IV_EXPANSION_MULT
        target_mult = base_mult * iv_factor
        target_mult = min(target_mult, TARGET_IV_EXPANSION_CAP)

        if direction == Direction.LONG:
            target = entry + risk * target_mult
        else:
            target = entry - risk * target_mult

        # Minimum target: 0.5% from entry
        min_distance = entry * TARGET_MIN_PCT
        if direction == Direction.LONG:
            target = max(target, entry + min_distance)
        else:
            target = min(target, entry - min_distance)

        return target

    # ------------------------------------------------------------------
    # Confidence Components (v2 — unified for LONG and SHORT)
    # ------------------------------------------------------------------

    def _skew_accel_confidence(self, skew_roc: float, direction: str) -> float:
        """
        Skew acceleration confidence (hard gate, 0.0 or 0.20–0.30).
        Scaled by |roc|.
        """
        if skew_roc is None:
            return 0.0

        abs_roc = abs(skew_roc)
        # Scale: 0.05 → 0.20, 0.50+ → 0.30
        scale = min(1.0, (abs_roc - SKEW_ROC_THRESHOLD) / (0.50 - SKEW_ROC_THRESHOLD))
        return 0.20 + 0.10 * scale

    def _vol_weighted_stability_confidence(self, conviction_stability: float) -> float:
        """
        Volume-weighted stability confidence (hard gate, 0.0 or 0.15–0.25).
        Scaled by conviction.
        """
        if conviction_stability < VOL_WEIGHTED_STABILITY_MIN:
            return 0.0

        # Scale: 0.50 → 0.15, 2.0+ → 0.25
        scale = min(1.0, (conviction_stability - VOL_WEIGHTED_STABILITY_MIN)
                     / (2.0 - VOL_WEIGHTED_STABILITY_MIN))
        return 0.15 + 0.10 * scale

    def _delta_skew_convergence_confidence(self, delta_roc: float, direction: str) -> float:
        """
        Delta-skew convergence confidence (hard gate, 0.0 or 0.15–0.20).
        Scaled by |delta_roc|.
        """
        if delta_roc is None:
            return 0.0

        abs_dr = abs(delta_roc)
        # Scale: 0.05 → 0.15, 0.50+ → 0.20
        scale = min(1.0, (abs_dr - DELTA_ROC_THRESHOLD) / (0.50 - DELTA_ROC_THRESHOLD))
        return 0.15 + 0.05 * scale

    def _skew_extremity_confidence(self, current_skew: float, direction: str) -> float:
        """
        Skew extremity confidence (soft, 0.10–0.15).
        How far from zero was the original skew.
        """
        if direction == Direction.LONG:
            # Negative skew: magnitude beyond -0.07
            magnitude = abs(current_skew)
            if magnitude <= 0.07:
                return 0.10
            # -0.07 → 0.10, -0.27 → 0.15
            scale = min(1.0, (magnitude - 0.07) / 0.20)
        else:
            # Positive skew: magnitude beyond 0.20
            magnitude = abs(current_skew)
            if magnitude <= 0.20:
                return 0.10
            # 0.20 → 0.10, 0.40 → 0.15
            scale = min(1.0, (magnitude - 0.20) / 0.20)

        return 0.10 + 0.05 * scale

    def _volume_alignment_confidence(self, volume_ratio: Optional[float]) -> float:
        """
        Volume alignment confidence (soft, 0.05–0.10).
        No opposite volume spike.
        """
        if volume_ratio is None:
            return 0.075  # Neutral

        # No spike = good (ratio close to 1.0)
        if volume_ratio <= 1.0:
            return 0.10  # No spike at all
        # Above 1.0, penalize
        excess = (volume_ratio - 1.0) / (VOLUME_SPIKE_THRESHOLD - 1.0)
        return max(0.05, 0.10 - 0.05 * excess)

    def _gamma_strength_confidence(self, net_gamma: float) -> float:
        """
        Net gamma strength confidence (soft, 0.05–0.10).
        Stable environment.
        """
        if net_gamma < MIN_NET_GAMMA:
            return 0.05  # Below threshold
        # Scale: MIN_NET_GAMMA → 0.05, 2× → 0.10
        scale = min(1.0, net_gamma / (MIN_NET_GAMMA * 2))
        return 0.05 + 0.05 * scale

    def _compute_confidence_v2(
        self,
        current_skew: float,
        skew_roc: Optional[float],
        conviction_stability: float,
        delta_roc: Optional[float],
        volume_ratio: Optional[float],
        net_gamma: float,
        direction: str,
        depth_score=None,
    ) -> float:
        """
        Compute unified confidence for LONG and SHORT signals (Family A).

        5 components, simple average:
            1. Skew acceleration (abs skew_roc, 0→0.2)
            2. Volume stability (conviction_stability, 0→1)
            3. Delta-skew convergence (inverted abs delta_roc, 0→0.2)
            4. Skew extremity (current_skew, 0→10)
            5. Net gamma (0→5M)
        """
        # 1. Skew acceleration: skew_roc from -0.2 to 0.2, use abs for magnitude
        abs_roc = abs(skew_roc) if skew_roc is not None else 0.0
        c1 = normalize(abs_roc, 0.0, 0.2)
        # 2. Volume stability: conviction_stability 0→1, higher = more stable = higher
        c2 = normalize(conviction_stability, 0.0, 1.0)
        # 3. Delta-skew convergence: delta_roc from -0.2 to 0.2, invert for convergence
        abs_d = abs(delta_roc) if delta_roc is not None else 0.0
        c3 = 1.0 - normalize(abs_d, 0.0, 0.2)
        # 4. Skew extremity: current_skew 0→10, higher = more extreme = higher
        c4 = normalize(current_skew, 0.0, 10.0)
        # 5. Net gamma: net_gamma 0→5M, higher = higher
        c5 = normalize(net_gamma, 0.0, 5000000.0)
        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))

    # ------------------------------------------------------------------
    # LONG: Panic overblown (negative skew extreme)
    # ------------------------------------------------------------------

    def _check_long(
        self,
        current_skew: float,
        skew_window: RollingWindow,
        price_window: RollingWindow,
        volume_window: RollingWindow,
        rolling_data: Dict[str, Any],
        price: float,
        net_gamma: float,
        data: Dict[str, Any],
    ) -> Optional[Signal]:
        """
        Detect panic overblown: negative skew extreme + price stable + velocity confirmation.
        """
        # Skew must be extremely negative (panic)
        if current_skew >= SKEW_EXTREME_NEGATIVE:
            return None

        # Price must NOT be breaking down — stable or rising
        price_change = price_window.change_pct
        if price_change is None:
            return None
        if price_change < -PRICE_STABLE_THRESHOLD:
            return None

        # --- v2 Hard Gate 1: Skew acceleration ---
        skew_roc_window = rolling_data.get(KEY_SKEW_ROC_5M)
        skew_roc = self._check_skew_acceleration(skew_roc_window, Direction.LONG)
        if skew_roc is None:
            return None

        # --- v2 Hard Gate 2: Volume-weighted stability ---
        vol_passes, conviction_stability = self._check_volume_weighted_stability(
            price_window, volume_window, Direction.LONG
        )
        if not vol_passes:
            return None

        # --- v2 Hard Gate 3: Delta-skew convergence ---
        delta_roc = self._check_delta_skew_convergence(rolling_data, Direction.LONG)
        if delta_roc is None:
            return None

        # All hard gates passed — compute confidence
        volume_ratio = self._get_volume_ratio(volume_window)
        confidence = self._compute_confidence_v2(
            current_skew, skew_roc, conviction_stability,
            delta_roc, volume_ratio, net_gamma, Direction.LONG,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Compute IV-scaled target
        risk = price * STOP_PCT
        target = self._compute_iv_scaled_target(price, risk, rolling_data, Direction.LONG)

        # Get IV factor for metadata
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        iv_factor = 1.0
        if iv_window is not None and iv_window.count >= 2:
            current_iv = iv_window.latest or 0.0
            mean_iv = iv_window.mean or 0.0
            if current_iv > 0 and mean_iv > 0:
                iv_factor = current_iv / mean_iv
        target_mult = min(TARGET_IV_EXPANSION_MULT * iv_factor, TARGET_IV_EXPANSION_CAP)

        rolling_data_meta = data.get("rolling_data", {})
        price_window_meta = rolling_data_meta.get(KEY_PRICE_5M)
        trend = price_window_meta.trend if price_window_meta else "UNKNOWN"

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(price * (1 - STOP_PCT), 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Negative skew extreme ({current_skew:.3f}) + skew accel "
                f"(roc={skew_roc:+.3f}) + vol-stability ({conviction_stability:.2f}) + "
                f"delta convergence (delta_roc={delta_roc:+.3f})"
            ),
            metadata={
                # v1 fields
                "skew_value": round(current_skew, 4),
                "skew_rolling_avg": round(skew_window.mean or 0, 4),
                "skew_direction": "NEGATIVE",
                "price_change_pct": round(price_change, 4),
                "net_gamma": round(net_gamma, 2),
                "volume_ratio": volume_ratio,
                "skew_normalizing": True,
                "stop_pct": STOP_PCT,
                "target_pct": round(abs(target - price) / price, 4),
                "risk_reward_ratio": round(abs(target - price) / (price * STOP_PCT), 2)
                    if (price * STOP_PCT) > 0 else 0,
                "trend": trend,
                # v2 new fields
                "skew_roc": round(skew_roc, 4),
                "conviction_stability": round(conviction_stability, 3),
                "delta_roc": round(delta_roc, 4),
                "delta_skew_converging": True,
                "iv_factor": round(iv_factor, 3),
                "target_mult": round(target_mult, 2),
                "vol_intensity": round(volume_ratio or 0, 2),
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
        rolling_data: Dict[str, Any],
        price: float,
        net_gamma: float,
        data: Dict[str, Any],
    ) -> Optional[Signal]:
        """
        Detect euphoria overblown: positive skew extreme + price stable + velocity confirmation.
        """
        # Skew must be extremely positive (euphoria)
        if current_skew <= SKEW_EXTREME_POSITIVE:
            return None

        # Price must NOT be breaking out — stable or falling
        price_change = price_window.change_pct
        if price_change is None:
            return None
        if price_change > PRICE_STABLE_THRESHOLD:
            return None

        # --- v2 Hard Gate 1: Skew acceleration ---
        skew_roc_window = rolling_data.get(KEY_SKEW_ROC_5M)
        skew_roc = self._check_skew_acceleration(skew_roc_window, Direction.SHORT)
        if skew_roc is None:
            return None

        # --- v2 Hard Gate 2: Volume-weighted stability ---
        vol_passes, conviction_stability = self._check_volume_weighted_stability(
            price_window, volume_window, Direction.SHORT
        )
        if not vol_passes:
            return None

        # --- v2 Hard Gate 3: Delta-skew convergence ---
        delta_roc = self._check_delta_skew_convergence(rolling_data, Direction.SHORT)
        if delta_roc is None:
            return None

        # All hard gates passed — compute confidence
        volume_ratio = self._get_volume_ratio(volume_window)
        confidence = self._compute_confidence_v2(
            current_skew, skew_roc, conviction_stability,
            delta_roc, volume_ratio, net_gamma, Direction.SHORT,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Compute IV-scaled target
        risk = price * STOP_PCT
        target = self._compute_iv_scaled_target(price, risk, rolling_data, Direction.SHORT)

        # Get IV factor for metadata
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        iv_factor = 1.0
        if iv_window is not None and iv_window.count >= 2:
            current_iv = iv_window.latest or 0.0
            mean_iv = iv_window.mean or 0.0
            if current_iv > 0 and mean_iv > 0:
                iv_factor = current_iv / mean_iv
        target_mult = min(TARGET_IV_EXPANSION_MULT * iv_factor, TARGET_IV_EXPANSION_CAP)

        rolling_data_meta = data.get("rolling_data", {})
        price_window_meta = rolling_data_meta.get(KEY_PRICE_5M)
        trend = price_window_meta.trend if price_window_meta else "UNKNOWN"

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(price * (1 + STOP_PCT), 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Positive skew extreme ({current_skew:.3f}) + skew accel "
                f"(roc={skew_roc:+.3f}) + vol-stability ({conviction_stability:.2f}) + "
                f"delta convergence (delta_roc={delta_roc:+.3f})"
            ),
            metadata={
                # v1 fields
                "skew_value": round(current_skew, 4),
                "skew_rolling_avg": round(skew_window.mean or 0, 4),
                "skew_direction": "POSITIVE",
                "price_change_pct": round(price_change, 4),
                "net_gamma": round(net_gamma, 2),
                "volume_ratio": volume_ratio,
                "skew_normalizing": True,
                "stop_pct": STOP_PCT,
                "target_pct": round(abs(target - price) / price, 4),
                "risk_reward_ratio": round(abs(target - price) / (price * STOP_PCT), 2)
                    if (price * STOP_PCT) > 0 else 0,
                "trend": trend,
                # v2 new fields
                "skew_roc": round(skew_roc, 4),
                "conviction_stability": round(conviction_stability, 3),
                "delta_roc": round(delta_roc, 4),
                "delta_skew_converging": True,
                "iv_factor": round(iv_factor, 3),
                "target_mult": round(target_mult, 2),
                "vol_intensity": round(volume_ratio or 0, 2),
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
        Legacy volume spike check (kept for backwards compat).
        Not used in v2 — replaced by _check_volume_weighted_stability.
        """
        if volume_window.count < 2:
            return True

        current_vol = volume_window.latest
        avg_vol = volume_window.mean

        if current_vol is None or avg_vol is None or avg_vol == 0:
            return True

        ratio = current_vol / avg_vol

        if current_skew < 0:
            if price_change < -PRICE_STABLE_THRESHOLD and ratio > VOLUME_SPIKE_THRESHOLD:
                return False
        else:
            if price_change > PRICE_STABLE_THRESHOLD and ratio > VOLUME_SPIKE_THRESHOLD:
                return False

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
