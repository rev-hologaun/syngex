"""
strategies/full_data/extrinsic_intrinsic_flow.py — Extrinsic/Intrinsic Flow v2
"Conviction-Master" upgrade

Full-data (v2) strategy: tracks conviction through extrinsic value flow.
Extrinsic value expansion = new money entering the market with conviction.
Collapse = money leaving.

v2 Conviction-Master changes:
    - Extrinsic acceleration soft score (0.0–1.0, replaces hard gate)
    - Aggressor volume soft score (0.0–1.0, replaces hard gate)
    - Delta-skew coupling soft score (0.0–1.0, replaces hard gate)
    - IV-scaled targets (dynamic based on ATM IV regime)
    - 10-component confidence unified for all signal types
    - MIN_CONFIDENCE raised from 0.25 → 0.35

Logic:
    - Track extrinsic value proxy (abs(net_delta) × abs(net_gamma)) across the chain
    - Expansion: extrinsic +5% in 5min + volume >150% avg + directional volume
    - Collapse: extrinsic dropping + volume declining → fade remaining momentum
    - Theoretical vs market: if available, cheap calls = bullish, expensive puts = bearish
    - Tracks conviction, not just direction

Entry (LONG — extrinsic expansion + bullish volume):
    - Extrinsic expanding >5% + volume spiking >50% + VolumeUp trend
    - Net gamma positive

Entry (SHORT — extrinsic expansion + bearish volume):
    - Extrinsic expanding >5% + volume spiking >50% + VolumeDown trend
    - Net gamma positive

Entry (FADE — extrinsic collapse):
    - Extrinsic collapsing >10% + volume declining
    - Net gamma positive (range environment)
    - Fade the previous trend

Confidence factors (v2 — 10 equal-weight components, simple average):
    Pre-gate scores (4):
        1. Extrinsic score: magnitude of extrinsic change (0→1)
        2. Volume spike score: vol_ratio / 3.0 (0→1)
        3. Volume trend score: UP/DOWN=1.0, SPIKE=0.8, FLAT=0.5 (0→1)
        4. Gamma score: net_gamma / (min_net_gamma × 2) (0→1)
    Post-gate scores (3):
        5. Acceleration score: extrinsic ROC directional (0→1)
        6. Aggressor score: market depth aggressor ratio (0→1)
        7. Skew score: delta-skew coupling (0→1)
    Structural scores (3):
        8. Extrinsic magnitude: abs(extrinsic_change_pct) / 0.10 (0→1)
        9. Volume spike: vol_ratio / 2.0 (0→1)
        10. Net gamma: min(1.0, abs(net_gamma) / 2_000) (0→1)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_EXTRINSIC_PROXY_5M,
    KEY_EXTRINSIC_ROC_5M,
    KEY_IV_SKEW_5M,
    KEY_ATM_IV_5M,
    KEY_VOLUME_UP_5M,
    KEY_VOLUME_DOWN_5M,
    KEY_MARKET_DEPTH_AGG,
)

logger = logging.getLogger("Syngex.Strategies.ExtrinsicIntrinsicFlow")


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Stop and target
STOP_PCT = 0.005                        # 0.5% stop

# Min confidence — raised from 0.25 to 0.35 (v2 Conviction-Master)
MIN_CONFIDENCE = 0.35

# Min data points — need more data for extrinsic tracking
MIN_DATA_POINTS = 5

# Legacy constants — kept for backwards-compat confidence methods
EXTRINSIC_EXPANSION_THRESHOLD = 0.03    # 3% expansion
EXTRINSIC_COLLAPSE_THRESHOLD = 0.10     # 10% collapse
VOLUME_SPIKE_RATIO = 1.30               # 130% of avg (1.3×)
MIN_NET_GAMMA = 5000.0
VALID_VOLUME_TREND_LONG = ["UP"]
VALID_VOLUME_TREND_SHORT = ["DOWN"]
VALID_VOLUME_TREND_FADE = ["DOWN", "FLAT"]


class ExtrinsicIntrinsicFlow(BaseStrategy):
    """
    Extrinsic/Intrinsic Flow — Full-data (v2) conviction-tracking strategy.

    Tracks conviction through extrinsic value flow across the entire options
    chain. Uses delta × gamma as a proxy for extrinsic value since actual
    extrinsic values aren't tracked in _StrikeBucket.

    When extrinsic value expands rapidly (+5% in 5min) AND volume confirms
    (volume > 150% of avg) AND there's directional volume confirmation,
    that's new money entering with conviction — enter in the volume direction.

    When extrinsic value collapses (-10% from avg) AND volume declines,
    that's money leaving — fade the remaining momentum.

    v2 Conviction-Master adds:
    - Extrinsic acceleration soft score (accelerating in signal direction)
    - Aggressor volume soft score (market depth confirms aggressive side)
    - Delta-skew coupling soft score (IV skew normalizing in signal direction)
    - IV-scaled targets (dynamic based on ATM IV regime)
    - 10 equal-weight confidence components (4 pre-gate + 3 post-gate + 3 structural)

    This is a conviction-tracking strategy (15min–3hr holds) — signals are
    meaningful but not rapid-fire.
    """

    strategy_id = "extrinsic_intrinsic_flow"
    layer = "full_data"

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return extrinsic/intrinsic flow signals.

        Returns empty list when no conviction signal is detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma_normalized", 0.0)
        self._min_net_gamma = self._params.get("min_net_gamma", 5000.0)
        greeks_summary = data.get("greeks_summary", {})

        # --- Validate data ---
        if not greeks_summary:
            return []

        # --- Net gamma soft score ---
        if net_gamma < 0:
            gamma_score = 0.0
        else:
            gamma_score = min(1.0, max(0.0, net_gamma / (self._min_net_gamma * 2)))

        # --- Use main.py's populated extrinsic window ---
        extrinsic_window = rolling_data.get(KEY_EXTRINSIC_PROXY_5M)
        if extrinsic_window is None:
            return []
        if extrinsic_window.count < MIN_DATA_POINTS:
            return []

        extrinsic_mean = extrinsic_window.mean
        if extrinsic_mean is None or extrinsic_mean == 0:
            return []

        current_extrinsic = extrinsic_window.latest
        if current_extrinsic is None:
            return []

        # --- Compute extrinsic change % ---
        extrinsic_change_pct = (current_extrinsic - extrinsic_mean) / extrinsic_mean

        # --- Extrinsic change soft score ---
        extrinsic_score = min(1.0, max(0.0, abs(extrinsic_change_pct) / 0.15))

        # --- Directional volume check ---
        volume_up_5m = rolling_data.get(KEY_VOLUME_UP_5M)
        volume_down_5m = rolling_data.get(KEY_VOLUME_DOWN_5M)
        if volume_up_5m is None or volume_down_5m is None:
            return []
        if volume_up_5m.count < MIN_DATA_POINTS or volume_down_5m.count < MIN_DATA_POINTS:
            return []

        # Volume spike ratio: compare latest to rolling mean
        vol_ratio = None
        vol_trend = "FLAT"
        if volume_up_5m.mean is not None and volume_up_5m.mean > 0:
            vol_ratio = volume_up_5m.latest / volume_up_5m.mean if volume_up_5m.latest is not None else 1.0
        vol_trend = volume_up_5m.trend if volume_up_5m.trend else "FLAT"

        # --- Volume spike soft score ---
        vol_spike_score = min(1.0, max(0.0, (vol_ratio or 0.0) / 3.0))

        # --- Volume trend soft score ---
        vol_trend_scores = {"UP": 1.0, "DOWN": 1.0, "FLAT": 0.5, "SPIKE": 0.8, "UNKNOWN": 0.5}
        vol_trend_score = vol_trend_scores.get(vol_trend, 0.5)

        # --- Determine signal type ---
        signals: List[Signal] = []

        # Check LONG (extrinsic expansion + bullish volume)
        long_sig = self._check_long(
            extrinsic_change_pct, vol_ratio, vol_trend,
            underlying_price, net_gamma, data,
            gamma_score, extrinsic_score, vol_spike_score, vol_trend_score,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT (extrinsic expansion + bearish volume)
        short_sig = self._check_short(
            extrinsic_change_pct, vol_ratio, vol_trend,
            underlying_price, net_gamma, data,
            gamma_score, extrinsic_score, vol_spike_score, vol_trend_score,
        )
        if short_sig:
            signals.append(short_sig)

        # Check FADE (extrinsic collapse)
        fade_sig = self._check_fade(
            extrinsic_change_pct, vol_ratio, vol_trend,
            underlying_price, net_gamma, data,
            gamma_score, extrinsic_score, vol_spike_score, vol_trend_score,
        )
        if fade_sig:
            signals.append(fade_sig)

        return signals

    # ------------------------------------------------------------------
    # v2 Conviction-Master: Soft scores (post-gates)
    # ------------------------------------------------------------------

    def _score_extrinsic_acceleration(
        self, rolling_data: Dict[str, Any], signal_type: str,
    ) -> float:
        """
        Score extrinsic acceleration as a soft score (0.0–1.0).

        For expansion signals: positive accel = good, higher = higher score
        For collapse/fade signals: negative accel = good, more negative = higher score

        Returns a float 0.0–1.0.
        """
        window = rolling_data.get(KEY_EXTRINSIC_ROC_5M)
        if window is None or window.latest is None:
            return 0.0

        accel = window.latest

        if signal_type == "expansion":
            if accel > 0.10:
                return min(1.0, accel / 0.30)
            elif accel > 0:
                return accel / 0.30 * 0.5
            else:
                return 0.0
        elif signal_type in ("collapse", "fade"):
            if accel < -0.10:
                return min(1.0, abs(accel) / 0.30)
            elif accel < 0:
                return min(1.0, abs(accel) / 0.30)
            else:
                return 0.0

        return 0.0

    def _score_aggressor_volume(
        self, data: Dict[str, Any], direction: str,
    ) -> float:
        """
        Score aggressor volume from market depth (0.0–1.0).

        For LONG: ask-heavy = good (aggressive buying)
        For SHORT: bid-heavy = good (aggressive selling)
        For FADE: any direction acceptable → 1.0

        Returns a float 0.0–1.0.
        """
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        bids = depth.get("bids", [])
        asks = depth.get("asks", [])

        if not bids and not asks:
            return 0.5  # No depth data — neutral

        bid_total = sum(b.get("size", 0) for b in bids)
        ask_total = sum(a.get("size", 0) for a in asks)
        total = bid_total + ask_total

        if total == 0:
            return 0.5

        if direction == "LONG":
            ratio = ask_total / total
            return normalize(ratio, 0.5, 1.0)
        elif direction == "SHORT":
            ratio = bid_total / total
            return normalize(ratio, 0.5, 1.0)
        elif direction == "FADE":
            return 1.0  # Any direction acceptable

        return 0.5

    def _score_delta_skew_coupling(
        self, rolling_data: Dict[str, Any], signal_type: str,
    ) -> float:
        """
        Score delta-skew coupling (0.0–1.0).

        Skew normalizing from negative toward zero = bullish
        Skew normalizing from positive toward zero = bearish

        For LONG: positive skew_roc = good
        For SHORT: negative skew_roc = good
        For FADE: any direction acceptable → 1.0

        Returns a float 0.0–1.0.
        """
        window = rolling_data.get(KEY_IV_SKEW_5M)
        if window is None or window.latest is None or window.mean is None:
            return 0.5  # No skew data — neutral

        current_skew = window.latest
        avg_skew = window.mean

        if abs(avg_skew) == 0:
            return 0.5

        skew_roc = (current_skew - avg_skew) / abs(avg_skew)

        if signal_type == "expansion":
            return normalize(skew_roc, 0.0, 0.10)
        elif signal_type == "short":
            return normalize(-skew_roc, 0.0, 0.10)
        elif signal_type in ("collapse", "fade"):
            return 1.0  # Fade signals don't require skew coupling

        return 0.5

    # ------------------------------------------------------------------
    # v2 Conviction-Master: IV-scaled targets
    # ------------------------------------------------------------------

    def _compute_iv_scaled_target(
        self, entry: float, risk: float, rolling_data: Dict[str, Any],
        signal_type: str,
    ) -> float:
        """
        Compute IV-scaled target based on ATM IV regime.

        Higher IV → wider targets (more room to move).
        Lower IV → tighter targets (less room to move).

        For expansion: base_mult = 1.6
        For fade: base_mult = 1.2

        target_mult = base_mult × iv_factor, capped at 2.5
        """
        window = rolling_data.get(KEY_ATM_IV_5M)
        if window is None or window.latest is None or window.mean is None:
            # No IV data — use default multiplier
            base_mult = 1.6 if signal_type == "expansion" else 1.2
            target_mult = base_mult
        else:
            current_iv = window.latest
            mean_iv = window.mean
            iv_factor = current_iv / mean_iv if mean_iv > 0 else 1.0

            base_mult = 1.6 if signal_type == "expansion" else 1.2
            target_mult = base_mult * iv_factor

        # Cap at 2.5
        target_mult = min(target_mult, 2.5)

        if signal_type == "expansion":
            # LONG: target = entry + risk × target_mult
            target = entry + risk * target_mult
        else:
            # SHORT or FADE: target = entry - risk × target_mult
            target = entry - risk * target_mult

        # Minimum target: 0.5% from entry
        min_target = entry * (1 + 0.005) if signal_type == "expansion" else entry * (1 - 0.005)
        if signal_type == "expansion":
            target = max(target, min_target)
        else:
            target = min(target, min_target)

        return target

    # ------------------------------------------------------------------
    # v2 Conviction-Master: Unified 10-component confidence
    # ------------------------------------------------------------------

    def _compute_confidence_v2(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        signal_type: str,
        extrinsic_accel: Optional[float] = None,
        aggressor_ratio: Optional[float] = None,
        skew_coupled: bool = False,
        depth_score=None,
        # New soft scores (pre-gate)
        extrinsic_score: float = 0.0,
        vol_spike_score: float = 0.0,
        vol_trend_score: float = 0.5,
        gamma_score: float = 0.5,
        # New soft scores (post-gate)
        accel_score: float = 0.0,
        aggressor_score: float = 0.5,
        skew_score: float = 0.5,
    ) -> float:
        """
        Compute confidence using 10 equal-weight components for all signal types.

        10 components, simple average (all 0→1):
            1.  Extrinsic score: magnitude of extrinsic change (pre-gate)
            2.  Volume spike score: vol_ratio / 3.0 (pre-gate)
            3.  Volume trend score: UP/DOWN=1.0, SPIKE=0.8, FLAT=0.5 (pre-gate)
            4.  Gamma score: net_gamma / (min_net_gamma × 2) (pre-gate)
            5.  Acceleration score: extrinsic ROC directional (post-gate)
            6.  Aggressor score: market depth aggressor ratio (post-gate)
            7.  Skew score: delta-skew coupling (post-gate)
            8.  Extrinsic magnitude: abs(extrinsic_change_pct) / 0.10 (structural)
            9.  Volume spike: vol_ratio / 2.0 (structural)
            10. Net gamma: min(1.0, abs(net_gamma) / 2_000) (structural)
        """
        # 1.  Extrinsic score (pre-gate)
        c1 = extrinsic_score
        # 2.  Volume spike score (pre-gate)
        c2 = vol_spike_score
        # 3.  Volume trend score (pre-gate)
        c3 = vol_trend_score
        # 4.  Gamma score (pre-gate)
        c4 = gamma_score
        # 5.  Acceleration score (post-gate)
        c5 = accel_score
        # 6.  Aggressor score (post-gate)
        c6 = aggressor_score
        # 7.  Skew score (post-gate)
        c7 = skew_score
        # 8.  Extrinsic magnitude (structural)
        c8 = normalize(abs(extrinsic_change_pct), 0.0, 0.10)
        # 9.  Volume spike (structural)
        c9 = normalize(vol_ratio or 1.0, 0.0, 2.0)
        # 10. Net gamma (structural)
        c10 = min(1.0, abs(net_gamma) / 2000.0)
        confidence = (c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10) / 10.0
        return min(1.0, max(0.0, confidence))

    # ------------------------------------------------------------------
    # LONG: Extrinsic expansion + bullish volume
    # ------------------------------------------------------------------

    def _check_long(
        self,
        extrinsic_change_pct: float,
        vol_ratio: Optional[float],
        vol_trend: str,
        price: float,
        net_gamma: float,
        data: Dict[str, Any],
        gamma_score: float = 0.0,
        extrinsic_score: float = 0.0,
        vol_spike_score: float = 0.0,
        vol_trend_score: float = 0.0,
    ) -> Optional[Signal]:
        """
        Detect extrinsic expansion with bullish conviction.

        New money entering with bullish conviction:
        - Extrinsic value expanding
        - Volume spiking
        - Volume trend is UP
        - Net gamma positive
        - v2: Extrinsic accelerating upward, aggressive buying, skew coupling
        """
        # Defensive: bail on None params to prevent f-string crashes
        if extrinsic_change_pct is None or vol_ratio is None:
            return None

        rolling_data = data.get("rolling_data", {})

        # Direction selection: use soft scores instead of hard gates
        if extrinsic_change_pct <= 0:
            return None
        if vol_trend != "UP":
            return None
        direction_score = extrinsic_score * gamma_score * vol_trend_score

        # --- v2 Conviction-Master: Soft scores ---
        # Extrinsic acceleration (for metadata + confidence)
        extrinsic_accel = 0.0
        roc_window = rolling_data.get(KEY_EXTRINSIC_ROC_5M)
        if roc_window and roc_window.latest is not None:
            extrinsic_accel = roc_window.latest

        # 1. Extrinsic acceleration score
        accel_score = self._score_extrinsic_acceleration(rolling_data, "expansion")

        # 2. Aggressor volume score
        aggressor_score = self._score_aggressor_volume(data, "LONG")

        # 3. Delta-skew coupling score
        skew_score = self._score_delta_skew_coupling(rolling_data, "expansion")

        # Compute aggressor ratio for metadata
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        bids = depth.get("bids", [])
        asks = depth.get("asks", [])
        aggressor_ratio = None
        if bids or asks:
            bid_total = sum(b.get("size", 0) for b in bids)
            ask_total = sum(a.get("size", 0) for a in asks)
            total = bid_total + ask_total
            if total > 0:
                aggressor_ratio = ask_total / total  # Ask-heavy = aggressive buying

        # Compute confidence — 10 equal-weight components
        confidence = self._compute_confidence_v2(
            extrinsic_change_pct=extrinsic_change_pct,
            vol_ratio=vol_ratio,
            vol_trend=vol_trend,
            net_gamma=net_gamma,
            signal_type="expansion",
            extrinsic_accel=extrinsic_accel,
            aggressor_ratio=aggressor_ratio,
            skew_coupled=False,
            extrinsic_score=extrinsic_score,
            vol_spike_score=vol_spike_score,
            vol_trend_score=vol_trend_score,
            gamma_score=gamma_score,
            accel_score=accel_score,
            aggressor_score=aggressor_score,
            skew_score=skew_score,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Compute IV-scaled target
        risk = price * STOP_PCT
        target = self._compute_iv_scaled_target(price, risk, rolling_data, "expansion")

        # Extract trend from price window for metadata
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        # Compute skew_roc for metadata
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        skew_roc = None
        if skew_window and skew_window.latest and skew_window.mean and abs(skew_window.mean) > 0:
            skew_roc = (skew_window.latest - skew_window.mean) / abs(skew_window.mean)

        # Compute iv_factor for metadata
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        iv_factor = None
        if iv_window and iv_window.latest and iv_window.mean and iv_window.mean > 0:
            iv_factor = iv_window.latest / iv_window.mean

        # Build signal
        stop = price * (1 - STOP_PCT)

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Extrinsic expansion + bullish conviction: "
                f"extrinsic +{extrinsic_change_pct:.1%}, vol {vol_ratio:.1f}×, "
                f"trend={vol_trend}, gamma={net_gamma:.0f}"
            ),
            metadata={
                "signal_type": "expansion",
                "extrinsic_change_pct": round(extrinsic_change_pct, 4),
                "extrinsic_roc": round(extrinsic_accel, 4),
                "extrinsic_accel": round(extrinsic_accel, 4),
                "volume_ratio": round(vol_ratio, 2),
                "volume_trend": vol_trend,
                "trend": trend,
                "net_gamma": round(net_gamma, 2),
                "aggressor_ratio": round(aggressor_ratio, 4) if aggressor_ratio else None,
                "skew_roc": round(skew_roc, 4) if skew_roc else None,
                "delta_skew_coupled": skew_coupled,
                "accel_score": round(accel_score, 3),
                "aggressor_score": round(aggressor_score, 3),
                "skew_score": round(skew_score, 3),
                "iv_factor": round(iv_factor, 4) if iv_factor else None,
                "gamma_score": round(gamma_score, 3),
                "extrinsic_score": round(extrinsic_score, 3),
                "vol_spike_score": round(vol_spike_score, 3),
                "vol_trend_score": round(vol_trend_score, 3),
                "direction_score": round(direction_score, 4),
                "target_mult": round(target / (price * STOP_PCT), 2) if risk > 0 else None,
                "stop_pct": STOP_PCT,
                "target_pct": round((target - price) / price, 4),
                "risk_reward_ratio": round(
                    abs(target - price) / (price - stop), 2
                ),
            },
        )

    # ------------------------------------------------------------------
    # SHORT: Extrinsic expansion + bearish volume
    # ------------------------------------------------------------------

    def _check_short(
        self,
        extrinsic_change_pct: float,
        vol_ratio: Optional[float],
        vol_trend: str,
        price: float,
        net_gamma: float,
        data: Dict[str, Any],
        gamma_score: float = 0.0,
        extrinsic_score: float = 0.0,
        vol_spike_score: float = 0.0,
        vol_trend_score: float = 0.0,
    ) -> Optional[Signal]:
        """
        Detect extrinsic expansion with bearish conviction.

        New money entering with bearish conviction:
        - Extrinsic value expanding
        - Volume spiking
        - Volume trend is DOWN
        - Net gamma positive
        - v2: Extrinsic accelerating upward, aggressive selling, skew coupling
        """
        # Defensive: bail on None params to prevent f-string crashes
        if extrinsic_change_pct is None or vol_ratio is None:
            return None

        rolling_data = data.get("rolling_data", {})

        # Direction selection: use soft scores instead of hard gates
        if extrinsic_change_pct <= 0:
            return None
        if vol_trend != "DOWN":
            return None
        direction_score = extrinsic_score * gamma_score * vol_trend_score

        # --- v2 Conviction-Master: Soft scores ---
        # Extrinsic acceleration (for metadata + confidence)
        extrinsic_accel = 0.0
        roc_window = rolling_data.get(KEY_EXTRINSIC_ROC_5M)
        if roc_window and roc_window.latest is not None:
            extrinsic_accel = roc_window.latest

        # 1. Extrinsic acceleration score
        accel_score = self._score_extrinsic_acceleration(rolling_data, "short")

        # 2. Aggressor volume score
        aggressor_score = self._score_aggressor_volume(data, "SHORT")

        # 3. Delta-skew coupling score
        skew_score = self._score_delta_skew_coupling(rolling_data, "short")

        # Compute aggressor ratio for metadata
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        bids = depth.get("bids", [])
        asks = depth.get("asks", [])
        aggressor_ratio = None
        if bids or asks:
            bid_total = sum(b.get("size", 0) for b in bids)
            ask_total = sum(a.get("size", 0) for a in asks)
            total = bid_total + ask_total
            if total > 0:
                aggressor_ratio = bid_total / total  # Bid-heavy = aggressive selling

        # Compute confidence — 10 equal-weight components
        confidence = self._compute_confidence_v2(
            extrinsic_change_pct=extrinsic_change_pct,
            vol_ratio=vol_ratio,
            vol_trend=vol_trend,
            net_gamma=net_gamma,
            signal_type="short",
            extrinsic_accel=extrinsic_accel,
            aggressor_ratio=aggressor_ratio,
            skew_coupled=False,
            extrinsic_score=extrinsic_score,
            vol_spike_score=vol_spike_score,
            vol_trend_score=vol_trend_score,
            gamma_score=gamma_score,
            accel_score=accel_score,
            aggressor_score=aggressor_score,
            skew_score=skew_score,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Compute IV-scaled target
        risk = price * STOP_PCT
        target = self._compute_iv_scaled_target(price, risk, rolling_data, "short")

        # Extract trend from price window for metadata
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        # Compute skew_roc for metadata
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        skew_roc = None
        if skew_window and skew_window.latest and skew_window.mean and abs(skew_window.mean) > 0:
            skew_roc = (skew_window.latest - skew_window.mean) / abs(skew_window.mean)

        # Compute iv_factor for metadata
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        iv_factor = None
        if iv_window and iv_window.latest and iv_window.mean and iv_window.mean > 0:
            iv_factor = iv_window.latest / iv_window.mean

        # Build signal
        stop = price * (1 + STOP_PCT)

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Extrinsic expansion + bearish conviction: "
                f"extrinsic +{extrinsic_change_pct:.1%}, vol {vol_ratio:.1f}×, "
                f"trend={vol_trend}, gamma={net_gamma:.0f}"
            ),
            metadata={
                "signal_type": "short",
                "extrinsic_change_pct": round(extrinsic_change_pct, 4),
                "extrinsic_roc": round(extrinsic_accel, 4),
                "extrinsic_accel": round(extrinsic_accel, 4),
                "volume_ratio": round(vol_ratio, 2),
                "volume_trend": vol_trend,
                "trend": trend,
                "net_gamma": round(net_gamma, 2),
                "aggressor_ratio": round(aggressor_ratio, 4) if aggressor_ratio else None,
                "skew_roc": round(skew_roc, 4) if skew_roc else None,
                "delta_skew_coupled": skew_coupled,
                "accel_score": round(accel_score, 3),
                "aggressor_score": round(aggressor_score, 3),
                "skew_score": round(skew_score, 3),
                "iv_factor": round(iv_factor, 4) if iv_factor else None,
                "gamma_score": round(gamma_score, 3),
                "extrinsic_score": round(extrinsic_score, 3),
                "vol_spike_score": round(vol_spike_score, 3),
                "vol_trend_score": round(vol_trend_score, 3),
                "direction_score": round(direction_score, 4),
                "target_mult": round((price - target) / (price * STOP_PCT), 2) if risk > 0 else None,
                "stop_pct": STOP_PCT,
                "target_pct": round((price - target) / price, 4),
                "risk_reward_ratio": round(
                    abs(target - price) / (stop - price), 2
                ),
            },
        )

    # ------------------------------------------------------------------
    # FADE: Extrinsic collapse
    # ------------------------------------------------------------------

    def _check_fade(
        self,
        extrinsic_change_pct: float,
        vol_ratio: Optional[float],
        vol_trend: str,
        price: float,
        net_gamma: float,
        data: Dict[str, Any],
        gamma_score: float = 0.0,
        extrinsic_score: float = 0.0,
        vol_spike_score: float = 0.0,
        vol_trend_score: float = 0.0,
    ) -> Optional[Signal]:
        """
        Detect extrinsic collapse → fade the previous trend.

        Money leaving the market:
        - Extrinsic value collapsing
        - Volume declining or flat
        - Net gamma positive (range environment)
        - Fade the previous trend direction

        Fade direction is determined by the volume trend:
        - If volume was UP → fade LONG (go SHORT)
        - If volume was FLAT → fade based on recent price momentum
        - v2: Extrinsic accelerating downward, skew coupling not required
        """
        # Defensive: bail on None params to prevent f-string crashes
        if extrinsic_change_pct is None or vol_ratio is None:
            return None

        rolling_data = data.get("rolling_data", {})

        # Direction selection: use soft scores instead of hard gates
        if extrinsic_change_pct >= 0:
            return None
        if vol_trend not in ("DOWN", "FLAT"):
            return None
        direction_score = extrinsic_score * gamma_score

        # Determine fade direction
        if vol_trend == "DOWN":
            # Volume declining from a downtrend → fade SHORT (go LONG)
            fade_direction = Direction.LONG
            fade_signal_type = "expansion"  # For IV-scaled target
        elif vol_trend == "FLAT":
            # Volume flat during collapse → check recent price momentum
            price_5m = rolling_data.get("price_5m")
            if price_5m is not None and price_5m.change_pct is not None:
                if price_5m.change_pct > 0:
                    fade_direction = Direction.SHORT  # Price was up → fade
                    fade_signal_type = "expansion"
                else:
                    fade_direction = Direction.LONG   # Price was down → fade
                    fade_signal_type = "expansion"
            else:
                fade_direction = Direction.LONG  # Default: fade down
                fade_signal_type = "expansion"
        else:
            return None

        # --- v2 Conviction-Master: Soft scores ---
        # Extrinsic acceleration (for metadata + confidence)
        extrinsic_accel = 0.0
        roc_window = rolling_data.get(KEY_EXTRINSIC_ROC_5M)
        if roc_window and roc_window.latest is not None:
            extrinsic_accel = roc_window.latest

        # 1. Extrinsic acceleration score
        accel_score = self._score_extrinsic_acceleration(rolling_data, "collapse")

        # 2. Aggressor volume score — any direction acceptable for fade
        aggressor_score = self._score_aggressor_volume(data, "FADE")

        # 3. Delta-skew coupling score — any direction acceptable for fade
        skew_score = self._score_delta_skew_coupling(rolling_data, "fade")

        # Compute aggressor ratio for metadata (use available depth)
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        bids = depth.get("bids", [])
        asks = depth.get("asks", [])
        aggressor_ratio = None
        if bids or asks:
            bid_total = sum(b.get("size", 0) for b in bids)
            ask_total = sum(a.get("size", 0) for a in asks)
            total = bid_total + ask_total
            if total > 0:
                aggressor_ratio = max(bid_total / total, ask_total / total)

        # Compute confidence — 10 equal-weight components
        confidence = self._compute_confidence_v2(
            extrinsic_change_pct=extrinsic_change_pct,
            vol_ratio=vol_ratio,
            vol_trend=vol_trend,
            net_gamma=net_gamma,
            signal_type="collapse",
            extrinsic_accel=extrinsic_accel,
            aggressor_ratio=aggressor_ratio,
            skew_coupled=False,
            extrinsic_score=extrinsic_score,
            vol_spike_score=vol_spike_score,
            vol_trend_score=vol_trend_score,
            gamma_score=gamma_score,
            accel_score=accel_score,
            aggressor_score=aggressor_score,
            skew_score=skew_score,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Compute IV-scaled target (fade uses base_mult = 1.2)
        risk = price * STOP_PCT
        target = self._compute_iv_scaled_target(price, risk, rolling_data, "fade")

        # Extract trend from price window for metadata
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        # Compute skew_roc for metadata
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        skew_roc = None
        if skew_window and skew_window.latest and skew_window.mean and abs(skew_window.mean) > 0:
            skew_roc = (skew_window.latest - skew_window.mean) / abs(skew_window.mean)

        # Compute iv_factor for metadata
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        iv_factor = None
        if iv_window and iv_window.latest and iv_window.mean and iv_window.mean > 0:
            iv_factor = iv_window.latest / iv_window.mean

        # Build signal
        if fade_direction == Direction.LONG:
            stop = price * (1 + STOP_PCT)
        else:
            stop = price * (1 - STOP_PCT)

        return Signal(
            direction=fade_direction,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Extrinsic collapse → fade: "
                f"extrinsic {extrinsic_change_pct:.1%}, vol {vol_ratio:.1f}×, "
                f"trend={vol_trend}, gamma={net_gamma:.0f}"
            ),
            metadata={
                "signal_type": "collapse",
                "extrinsic_change_pct": round(extrinsic_change_pct, 4),
                "extrinsic_roc": round(extrinsic_accel, 4),
                "extrinsic_accel": round(extrinsic_accel, 4),
                "volume_ratio": round(vol_ratio, 2),
                "volume_trend": vol_trend,
                "trend": trend,
                "fade_direction": fade_direction.value,
                "net_gamma": round(net_gamma, 2),
                "aggressor_ratio": round(aggressor_ratio, 4) if aggressor_ratio else None,
                "skew_roc": round(skew_roc, 4) if skew_roc else None,
                "delta_skew_coupled": True,
                "accel_score": round(accel_score, 3),
                "aggressor_score": round(aggressor_score, 3),
                "skew_score": round(skew_score, 3),
                "iv_factor": round(iv_factor, 4) if iv_factor else None,
                "gamma_score": round(gamma_score, 3),
                "extrinsic_score": round(extrinsic_score, 3),
                "vol_spike_score": round(vol_spike_score, 3),
                "vol_trend_score": round(vol_trend_score, 3),
                "direction_score": round(direction_score, 4),
                "target_mult": round(abs(target - price) / risk, 2) if risk > 0 else None,
                "stop_pct": STOP_PCT,
                "target_pct": round(abs(target - price) / price, 4),
                "risk_reward_ratio": round(
                    abs(target - price) / abs(stop - price), 2
                ),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
