"""
strategies/full_data/extrinsic_intrinsic_flow.py — Extrinsic/Intrinsic Flow v2
"Conviction-Master" upgrade

Full-data (v2) strategy: tracks conviction through extrinsic value flow.
Extrinsic value expansion = new money entering the market with conviction.
Collapse = money leaving.

v2 Conviction-Master changes:
    - Extrinsic acceleration gate (hard gate: 0.20–0.30 confidence)
    - Aggressor volume gate (hard gate: 0.15–0.20 confidence)
    - Delta-skew coupling gate (hard gate: 0.15–0.20 confidence)
    - IV-scaled targets (dynamic based on ATM IV regime)
    - 7-component confidence unified for all signal types
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

Confidence factors (v2 — 7 components, unified):
    1. Extrinsic magnitude: 0.05–0.10 (soft)
    2. Extrinsic acceleration: 0.0 or 0.20–0.30 (hard gate)
    3. Aggressor volume: 0.0 or 0.15–0.20 (hard gate)
    4. Delta-skew coupling: 0.0 or 0.15–0.20 (hard gate)
    5. Volume spike: 0.05–0.10 (soft)
    6. Volume direction: 0.05–0.10 (soft)
    7. Net gamma: 0.05–0.10 (soft)
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

# Extrinsic expansion threshold: current > rolling avg by this %
EXTRINSIC_EXPANSION_THRESHOLD = 0.03    # 3% expansion

# Extrinsic collapse threshold: current < rolling avg by this %
EXTRINSIC_COLLAPSE_THRESHOLD = 0.10     # 10% collapse

# Volume spike threshold for new money
VOLUME_SPIKE_RATIO = 1.30               # 130% of avg (1.3×)

# Min net gamma for positive regime — read from config, default 5000

# Stop and target
STOP_PCT = 0.005                        # 0.5% stop

# Min confidence — raised from 0.25 to 0.35 (v2 Conviction-Master)
MIN_CONFIDENCE = 0.10

# Min data points — need more data for extrinsic tracking
MIN_DATA_POINTS = 5

# Volume trend filters
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
    - Extrinsic acceleration gate (must be accelerating in signal direction)
    - Aggressor volume gate (market depth confirms aggressive side)
    - Delta-skew coupling gate (IV skew normalizing in signal direction)
    - IV-scaled targets (dynamic based on ATM IV regime)

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
        net_gamma = data.get("net_gamma", 0.0)
        self._min_net_gamma = self._params.get("min_net_gamma", 5000.0)
        greeks_summary = data.get("greeks_summary", {})

        # --- Validate data ---
        if not greeks_summary:
            return []

        # --- Net gamma check ---
        if net_gamma < self._min_net_gamma:
            return []

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

        # --- Determine signal type ---
        signals: List[Signal] = []

        # Check LONG (extrinsic expansion + bullish volume)
        long_sig = self._check_long(
            extrinsic_change_pct, vol_ratio, vol_trend,
            underlying_price, net_gamma, data,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT (extrinsic expansion + bearish volume)
        short_sig = self._check_short(
            extrinsic_change_pct, vol_ratio, vol_trend,
            underlying_price, net_gamma, data,
        )
        if short_sig:
            signals.append(short_sig)

        # Check FADE (extrinsic collapse)
        fade_sig = self._check_fade(
            extrinsic_change_pct, vol_ratio, vol_trend,
            underlying_price, net_gamma, data,
        )
        if fade_sig:
            signals.append(fade_sig)

        return signals

    # ------------------------------------------------------------------
    # v2 Conviction-Master: Hard gates
    # ------------------------------------------------------------------

    def _check_extrinsic_acceleration(
        self, rolling_data: Dict[str, Any], signal_type: str,
    ) -> Optional[float]:
        """
        Check extrinsic acceleration as a hard gate.

        For expansion signals: extrinsic_accel > 0.10 (accelerating upward ≥10%)
        For collapse/fade signals: extrinsic_accel < -0.10 (accelerating downward ≥10%)

        Returns extrinsic_accel value if gate passes, None otherwise.
        """
        window = rolling_data.get(KEY_EXTRINSIC_ROC_5M)
        if window is None or window.latest is None:
            return None

        extrinsic_accel = window.latest

        if signal_type == "expansion":
            if extrinsic_accel > 0.10:
                return extrinsic_accel
        elif signal_type in ("collapse", "fade"):
            if extrinsic_accel < -0.10:
                return extrinsic_accel

        return None

    def _check_aggressor_volume(
        self, data: Dict[str, Any], direction: str,
    ) -> bool:
        """
        Check aggressor volume from market depth as a hard gate.

        For LONG: ask_total / (bid_total + ask_total) > 0.55 (aggressive buying)
        For SHORT: bid_total / (bid_total + ask_total) > 0.55 (aggressive selling)
        For FADE: any direction acceptable

        Returns True if gate passes, False otherwise.
        Returns True if depth data unavailable (backwards compat).
        """
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        bids = depth.get("bids", [])
        asks = depth.get("asks", [])

        if not bids and not asks:
            return True  # No depth data — backwards compat

        bid_total = sum(b.get("size", 0) for b in bids)
        ask_total = sum(a.get("size", 0) for a in asks)
        total = bid_total + ask_total

        if total == 0:
            return True

        if direction == "LONG":
            # Aggressive buying: asks are being hit
            return ask_total / total > 0.55
        elif direction == "SHORT":
            # Aggressive selling: bids are being hit
            return bid_total / total > 0.55
        elif direction == "FADE":
            # Any direction acceptable for fade
            return True

        return True

    def _check_delta_skew_coupling(
        self, rolling_data: Dict[str, Any], signal_type: str,
    ) -> bool:
        """
        Check delta-skew coupling as a hard gate.

        Skew normalizing from negative toward zero = bullish
        Skew normalizing from positive toward zero = bearish

        For LONG: skew_roc > 0 (skew normalizing from negative toward zero)
        For SHORT: skew_roc < 0 (skew normalizing from positive toward zero)
        For FADE: always True (skew direction doesn't matter)

        Returns True if gate passes, False otherwise.
        Returns True if skew data unavailable (backwards compat).
        """
        window = rolling_data.get(KEY_IV_SKEW_5M)
        if window is None or window.latest is None or window.mean is None:
            return True  # No skew data — backwards compat

        current_skew = window.latest
        avg_skew = window.mean

        if abs(avg_skew) == 0:
            return True

        skew_roc = (current_skew - avg_skew) / abs(avg_skew)

        if signal_type == "expansion":
            return skew_roc > 0  # Skew normalizing from negative toward zero
        elif signal_type in ("collapse", "fade"):
            # For collapse: skew direction doesn't matter as much
            # but we still want some coupling — allow both directions
            return True  # Fade signals don't require skew coupling
        elif signal_type == "short":
            return skew_roc < 0  # Skew normalizing from positive toward zero

        return True

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
    # v2 Conviction-Master: Unified 7-component confidence
    # ------------------------------------------------------------------

    def _compute_confidence_v2(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        signal_type: str,
        extrinsic_accel: Optional[float],
        aggressor_ratio: Optional[float],
        skew_coupled: bool,
    ) -> float:
        """
        Compute confidence using 5 unified components for all signal types (Family A).

        5 components, simple average:
            1. Extrinsic magnitude (abs change, 0→0.10)
            2. Extrinsic acceleration (0→1)
            3. Aggressor volume (0→1)
            4. Volume spike (vol_ratio, 0→2)
            5. Net gamma (0→5M)
        """
        # 1. Extrinsic magnitude: extrinsic_change_pct from 0→0.10, use abs
        abs_change = abs(extrinsic_change_pct)
        c1 = normalize(abs_change, 0.0, 0.10)
        # 2. Extrinsic acceleration: extrinsic_accel from 0→1, higher = higher
        c2 = normalize(extrinsic_accel, 0.0, 1.0) if extrinsic_accel is not None else 0.5
        # 3. Aggressor volume: aggressor_ratio from 0→1, higher = higher
        c3 = normalize(aggressor_ratio, 0.0, 1.0) if aggressor_ratio is not None else 0.5
        # 4. Volume spike: vol_ratio from 0→2, higher = higher
        c4 = normalize(vol_ratio, 0.0, 2.0)
        # 5. Net gamma: net_gamma from 0→5M, higher = higher
        c5 = normalize(net_gamma, 0.0, 5000000.0)
        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
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
    ) -> Optional[Signal]:
        """
        Detect extrinsic expansion with bullish conviction.

        New money entering with bullish conviction:
        - Extrinsic value expanding >5% above rolling avg
        - Volume spiking >50% above avg
        - Volume trend is UP
        - Net gamma positive
        - v2: Extrinsic accelerating upward, aggressive buying, skew coupling
        """
        rolling_data = data.get("rolling_data", {})

        # Extrinsic must be expanding
        if extrinsic_change_pct < EXTRINSIC_EXPANSION_THRESHOLD:
            return None

        # Volume must be spiking
        if vol_ratio is None or vol_ratio < VOLUME_SPIKE_RATIO:
            return None

        # Volume trend must confirm bullish direction
        if vol_trend not in VALID_VOLUME_TREND_LONG:
            return None

        # --- v2 Conviction-Master: Hard gates ---
        # 1. Extrinsic acceleration gate
        extrinsic_accel = self._check_extrinsic_acceleration(rolling_data, "expansion")
        if extrinsic_accel is None:
            return None

        # 2. Aggressor volume gate
        aggressor_pass = self._check_aggressor_volume(data, "LONG")
        if not aggressor_pass:
            return None

        # 3. Delta-skew coupling gate
        skew_coupled = self._check_delta_skew_coupling(rolling_data, "expansion")
        if not skew_coupled:
            return None

        # Compute aggressor ratio for confidence scaling
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

        # Compute confidence
        confidence = self._compute_confidence_v2(
            extrinsic_change_pct, vol_ratio, vol_trend,
            net_gamma, "expansion", extrinsic_accel,
            aggressor_ratio, skew_coupled,
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
                "iv_factor": round(iv_factor, 4) if iv_factor else None,
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
    ) -> Optional[Signal]:
        """
        Detect extrinsic expansion with bearish conviction.

        New money entering with bearish conviction:
        - Extrinsic value expanding >5% above rolling avg
        - Volume spiking >50% above avg
        - Volume trend is DOWN
        - Net gamma positive
        - v2: Extrinsic accelerating upward, aggressive selling, skew coupling
        """
        rolling_data = data.get("rolling_data", {})

        # Extrinsic must be expanding
        if extrinsic_change_pct < EXTRINSIC_EXPANSION_THRESHOLD:
            return None

        # Volume must be spiking
        if vol_ratio is None or vol_ratio < VOLUME_SPIKE_RATIO:
            return None

        # Volume trend must confirm bearish direction
        if vol_trend not in VALID_VOLUME_TREND_SHORT:
            return None

        # --- v2 Conviction-Master: Hard gates ---
        # 1. Extrinsic acceleration gate
        extrinsic_accel = self._check_extrinsic_acceleration(rolling_data, "expansion")
        if extrinsic_accel is None:
            return None

        # 2. Aggressor volume gate
        aggressor_pass = self._check_aggressor_volume(data, "SHORT")
        if not aggressor_pass:
            return None

        # 3. Delta-skew coupling gate
        skew_coupled = self._check_delta_skew_coupling(rolling_data, "short")
        if not skew_coupled:
            return None

        # Compute aggressor ratio for confidence scaling
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

        # Compute confidence
        confidence = self._compute_confidence_v2(
            extrinsic_change_pct, vol_ratio, vol_trend,
            net_gamma, "short", extrinsic_accel,
            aggressor_ratio, skew_coupled,
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
                "iv_factor": round(iv_factor, 4) if iv_factor else None,
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
    ) -> Optional[Signal]:
        """
        Detect extrinsic collapse → fade the previous trend.

        Money leaving the market:
        - Extrinsic value collapsing >10% below rolling avg
        - Volume declining or flat
        - Net gamma positive (range environment)
        - Fade the previous trend direction

        Fade direction is determined by the volume trend:
        - If volume was UP → fade LONG (go SHORT)
        - If volume was FLAT → fade based on recent price momentum
        - v2: Extrinsic accelerating downward, skew coupling not required
        """
        rolling_data = data.get("rolling_data", {})

        # Extrinsic must be collapsing
        if extrinsic_change_pct > -EXTRINSIC_COLLAPSE_THRESHOLD:
            return None

        # Volume must be declining or flat
        if vol_trend not in VALID_VOLUME_TREND_FADE:
            return None

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

        # --- v2 Conviction-Master: Hard gates ---
        # 1. Extrinsic acceleration gate
        extrinsic_accel = self._check_extrinsic_acceleration(rolling_data, "collapse")
        if extrinsic_accel is None:
            return None

        # 2. Aggressor volume gate — not required for fade
        # 3. Delta-skew coupling gate — not required for fade

        # Compute aggressor ratio for confidence scaling (use available depth)
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

        # Compute confidence
        confidence = self._compute_confidence_v2(
            extrinsic_change_pct, vol_ratio, vol_trend,
            net_gamma, "collapse", extrinsic_accel,
            aggressor_ratio, True,  # skew_coupled = True for fade
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
                "iv_factor": round(iv_factor, 4) if iv_factor else None,
                "target_mult": round(abs(target - price) / risk, 2) if risk > 0 else None,
                "stop_pct": STOP_PCT,
                "target_pct": round(abs(target - price) / price, 4),
                "risk_reward_ratio": round(
                    abs(target - price) / abs(stop - price), 2
                ),
            },
        )

    # ------------------------------------------------------------------
    # Legacy confidence methods (kept for backwards compat)
    # ------------------------------------------------------------------

    def _compute_long_confidence(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        price: float,
    ) -> float:
        """Legacy LONG confidence — kept for backwards compat."""
        # 1. Extrinsic expansion magnitude (0.20–0.30)
        exp_scaled = min(1.0, (extrinsic_change_pct - EXTRINSIC_EXPANSION_THRESHOLD)
                         / (EXTRINSIC_EXPANSION_THRESHOLD * 3))
        exp_component = 0.20 + 0.10 * exp_scaled

        # 2. Volume spike magnitude (0.20–0.25)
        vol_scaled = min(1.0, (vol_ratio - VOLUME_SPIKE_RATIO)
                         / (VOLUME_SPIKE_RATIO))
        vol_component = 0.20 + 0.05 * vol_scaled

        # 3. Volume direction alignment (0.10–0.15)
        if vol_trend == "UP":
            vol_dir_component = 0.15
        else:
            vol_dir_component = 0.05

        # 4. Net gamma strength (0.15–0.20)
        gamma_scaled = min(1.0, net_gamma / (MIN_NET_GAMMA * 4))
        gamma_component = 0.15 + 0.05 * gamma_scaled

        # Normalize each component to [0,1] and average
        norm_exp = (exp_component - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_vol = (vol_component - 0.20) / (0.25 - 0.20) if 0.25 != 0.20 else 1.0
        norm_vol_dir = (vol_dir_component - 0.05) / (0.15 - 0.05) if 0.15 != 0.05 else 1.0
        norm_gamma = (gamma_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        confidence = (norm_exp + norm_vol + norm_vol_dir + norm_gamma) / 4.0

        return max(0.0, confidence)

    def _compute_short_confidence(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        price: float,
    ) -> float:
        """Legacy SHORT confidence — kept for backwards compat."""
        # 1. Extrinsic expansion magnitude (0.20–0.30)
        exp_scaled = min(1.0, (extrinsic_change_pct - EXTRINSIC_EXPANSION_THRESHOLD)
                         / (EXTRINSIC_EXPANSION_THRESHOLD * 3))
        exp_component = 0.20 + 0.10 * exp_scaled

        # 2. Volume spike magnitude (0.20–0.25)
        vol_scaled = min(1.0, (vol_ratio - VOLUME_SPIKE_RATIO)
                         / (VOLUME_SPIKE_RATIO))
        vol_component = 0.20 + 0.05 * vol_scaled

        # 3. Volume direction alignment (0.10–0.15)
        if vol_trend == "DOWN":
            vol_dir_component = 0.15
        else:
            vol_dir_component = 0.05

        # 4. Net gamma strength (0.15–0.20)
        gamma_scaled = min(1.0, net_gamma / (MIN_NET_GAMMA * 4))
        gamma_component = 0.15 + 0.05 * gamma_scaled

        # Normalize each component to [0,1] and average
        norm_exp = (exp_component - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_vol = (vol_component - 0.20) / (0.25 - 0.20) if 0.25 != 0.20 else 1.0
        norm_vol_dir = (vol_dir_component - 0.05) / (0.15 - 0.05) if 0.15 != 0.05 else 1.0
        norm_gamma = (gamma_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        confidence = (norm_exp + norm_vol + norm_vol_dir + norm_gamma) / 4.0

        return max(0.0, confidence)

    def _compute_fade_confidence(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        price: float,
    ) -> float:
        """Legacy FADE confidence — kept for backwards compat."""
        # 1. Extrinsic collapse magnitude (0.25–0.35)
        collapse_magnitude = abs(extrinsic_change_pct)
        collapse_scaled = min(1.0, (collapse_magnitude - EXTRINSIC_COLLAPSE_THRESHOLD)
                              / (EXTRINSIC_COLLAPSE_THRESHOLD * 1.5))
        collapse_component = 0.25 + 0.10 * collapse_scaled

        # 2. Volume decline (0.15–0.20)
        if vol_ratio is not None and vol_ratio > 0:
            vol_decline = 1.0 - min(1.0, vol_ratio)
            vol_decline_component = 0.15 + 0.05 * vol_decline
        else:
            vol_decline_component = 0.15

        # 3. Volume trend alignment (0.10–0.15)
        if vol_trend == "DOWN":
            vol_dir_component = 0.15
        elif vol_trend == "FLAT":
            vol_dir_component = 0.12
        else:
            vol_dir_component = 0.05

        # 4. Net gamma strength (0.15–0.20)
        gamma_scaled = min(1.0, net_gamma / (MIN_NET_GAMMA * 4))
        gamma_component = 0.15 + 0.05 * gamma_scaled

        # Normalize each component to [0,1] and average
        norm_collapse = (collapse_component - 0.25) / (0.35 - 0.25) if 0.35 != 0.25 else 1.0
        norm_vol_decline = (vol_decline_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_vol_dir = (vol_dir_component - 0.05) / (0.15 - 0.05) if 0.15 != 0.05 else 1.0
        norm_gamma = (gamma_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        confidence = (norm_collapse + norm_vol_decline + norm_vol_dir + norm_gamma) / 4.0

        return max(0.0, confidence)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
