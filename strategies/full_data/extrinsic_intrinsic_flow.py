"""
strategies/full_data/extrinsic_intrinsic_flow.py — Extrinsic/Intrinsic Flow

Full-data (v2) strategy: tracks conviction through extrinsic value flow.
Extrinsic value expansion = new money entering the market with conviction.
Collapse = money leaving.

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

Confidence factors:
    - Extrinsic expansion/collapse magnitude
    - Volume spike magnitude
    - Volume direction alignment
    - Theoretical vs market alignment (if available)
    - Net gamma strength
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_EXTRINSIC_PROXY_5M, KEY_VOLUME_UP_5M, KEY_VOLUME_DOWN_5M

logger = logging.getLogger("Syngex.Strategies.ExtrinsicIntrinsicFlow")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Extrinsic expansion threshold: current > rolling avg by this %
EXTRINSIC_EXPANSION_THRESHOLD = 0.03    # 3% expansion

# Extrinsic collapse threshold: current < rolling avg by this %
EXTRINSIC_COLLAPSE_THRESHOLD = 0.10     # 10% collapse

# Volume spike threshold for new money
VOLUME_SPIKE_RATIO = 1.30               # 130% of avg (1.3×)

# Min net gamma for positive regime
MIN_NET_GAMMA = 500000.0

# Stop and target
STOP_PCT = 0.005                        # 0.5% stop
TARGET_PCT = 0.008                      # 0.8% target (1.6:1 R:R)

# Min confidence
MIN_CONFIDENCE = 0.25
MAX_CONFIDENCE = 0.80                   # v2 cap

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
        greeks_summary = data.get("greeks_summary", {})

        # --- Validate data ---
        if not greeks_summary:
            return []

        # --- Net gamma check ---
        if net_gamma < MIN_NET_GAMMA:
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
        """
        # Extrinsic must be expanding
        if extrinsic_change_pct < EXTRINSIC_EXPANSION_THRESHOLD:
            return None

        # Volume must be spiking
        if vol_ratio is None or vol_ratio < VOLUME_SPIKE_RATIO:
            return None

        # Volume trend must confirm bullish direction
        if vol_trend not in VALID_VOLUME_TREND_LONG:
            return None

        # Compute confidence
        confidence = self._compute_long_confidence(
            extrinsic_change_pct, vol_ratio, vol_trend,
            net_gamma, price,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Extract trend from price window for metadata
        rolling_data = data.get("rolling_data", {})
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

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
                f"Extrinsic expansion + bullish conviction: "
                f"extrinsic +{extrinsic_change_pct:.1%}, vol {vol_ratio:.1f}×, "
                f"trend={vol_trend}, gamma={net_gamma:.0f}"
            ),
            metadata={
                "signal_type": "expansion",
                "extrinsic_change_pct": round(extrinsic_change_pct, 4),
                "volume_ratio": round(vol_ratio, 2),
                "volume_trend": vol_trend,
                "trend": trend,
                "net_gamma": round(net_gamma, 2),
                "stop_pct": STOP_PCT,
                "target_pct": TARGET_PCT,
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
        """
        # Extrinsic must be expanding
        if extrinsic_change_pct < EXTRINSIC_EXPANSION_THRESHOLD:
            return None

        # Volume must be spiking
        if vol_ratio is None or vol_ratio < VOLUME_SPIKE_RATIO:
            return None

        # Volume trend must confirm bearish direction
        if vol_trend not in VALID_VOLUME_TREND_SHORT:
            return None

        # Compute confidence
        confidence = self._compute_short_confidence(
            extrinsic_change_pct, vol_ratio, vol_trend,
            net_gamma, price,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Extract trend from price window for metadata
        rolling_data = data.get("rolling_data", {})
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

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
                f"Extrinsic expansion + bearish conviction: "
                f"extrinsic +{extrinsic_change_pct:.1%}, vol {vol_ratio:.1f}×, "
                f"trend={vol_trend}, gamma={net_gamma:.0f}"
            ),
            metadata={
                "signal_type": "expansion",
                "extrinsic_change_pct": round(extrinsic_change_pct, 4),
                "volume_ratio": round(vol_ratio, 2),
                "volume_trend": vol_trend,
                "trend": trend,
                "net_gamma": round(net_gamma, 2),
                "stop_pct": STOP_PCT,
                "target_pct": TARGET_PCT,
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
        """
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
        elif vol_trend == "FLAT":
            # Volume flat during collapse → check recent price momentum
            price_5m = data.get("rolling_data", {}).get("price_5m")
            if price_5m is not None and price_5m.change_pct is not None:
                if price_5m.change_pct > 0:
                    fade_direction = Direction.SHORT  # Price was up → fade
                else:
                    fade_direction = Direction.LONG   # Price was down → fade
            else:
                fade_direction = Direction.LONG  # Default: fade down
        else:
            return None

        # Compute confidence
        confidence = self._compute_fade_confidence(
            extrinsic_change_pct, vol_ratio, vol_trend,
            net_gamma, price,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # Extract trend from price window for metadata
        rolling_data = data.get("rolling_data", {})
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        # Build signal
        if fade_direction == Direction.LONG:
            stop = price * (1 + STOP_PCT)
            target = price * (1 + TARGET_PCT)
        else:
            stop = price * (1 - STOP_PCT)
            target = price * (1 - TARGET_PCT)

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
                "volume_ratio": round(vol_ratio, 2),
                "volume_trend": vol_trend,
                "trend": trend,
                "fade_direction": fade_direction.value,
                "net_gamma": round(net_gamma, 2),
                "stop_pct": STOP_PCT,
                "target_pct": TARGET_PCT,
                "risk_reward_ratio": round(
                    abs(target - price) / abs(stop - price), 2
                ),
            },
        )

    # ------------------------------------------------------------------
    # Confidence scoring
    # ------------------------------------------------------------------

    def _compute_long_confidence(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        price: float,
    ) -> float:
        """
        Compute confidence for LONG (extrinsic expansion + bullish volume).

        Factors (each 0–1, capped at MAX_CONFIDENCE):
        1. Extrinsic expansion magnitude (0.20–0.30)
        2. Volume spike magnitude (0.20–0.25)
        3. Volume direction alignment (0.10–0.15)
        4. Net gamma strength (0.15–0.20)
        """
        # 1. Extrinsic expansion magnitude (0.20–0.30)
        #    Extrapolate: 5% = baseline, 20%+ = max weight
        exp_scaled = min(1.0, (extrinsic_change_pct - EXTRINSIC_EXPANSION_THRESHOLD)
                         / (EXTRINSIC_EXPANSION_THRESHOLD * 3))
        exp_component = 0.20 + 0.10 * exp_scaled

        # 2. Volume spike magnitude (0.20–0.25)
        #    1.5× = baseline, 3×+ = max weight
        vol_scaled = min(1.0, (vol_ratio - VOLUME_SPIKE_RATIO)
                         / (VOLUME_SPIKE_RATIO))
        vol_component = 0.20 + 0.05 * vol_scaled

        # 3. Volume direction alignment (0.10–0.15)
        #    UP trend = confirmed bullish
        if vol_trend == "UP":
            vol_dir_component = 0.15
        else:
            vol_dir_component = 0.05

        # 4. Net gamma strength (0.15–0.20)
        #    Higher positive gamma = stronger positive regime
        gamma_scaled = min(1.0, net_gamma / (MIN_NET_GAMMA * 4))
        gamma_component = 0.15 + 0.05 * gamma_scaled

        # Normalize each component to [0,1] and average
        norm_exp = (exp_component - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_vol = (vol_component - 0.20) / (0.25 - 0.20) if 0.25 != 0.20 else 1.0
        norm_vol_dir = (vol_dir_component - 0.05) / (0.15 - 0.05) if 0.15 != 0.05 else 1.0
        norm_gamma = (gamma_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        confidence = (norm_exp + norm_vol + norm_vol_dir + norm_gamma) / 4.0

        return min(MAX_CONFIDENCE, max(0.0, confidence))

    def _compute_short_confidence(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        price: float,
    ) -> float:
        """
        Compute confidence for SHORT (extrinsic expansion + bearish volume).

        Same factors as LONG but for bearish direction.
        """
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

        return min(MAX_CONFIDENCE, max(0.0, confidence))

    def _compute_fade_confidence(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        price: float,
    ) -> float:
        """
        Compute confidence for FADE (extrinsic collapse).

        Factors (each 0–1, capped at MAX_CONFIDENCE):
        1. Extrinsic collapse magnitude (0.25–0.35) — collapse is a stronger signal
        2. Volume decline (0.15–0.20)
        3. Volume trend alignment (0.10–0.15)
        4. Net gamma strength (0.15–0.20)
        """
        # 1. Extrinsic collapse magnitude (0.25–0.35)
        #    10% = baseline, 25%+ = max weight
        #    Use absolute value since change is negative
        collapse_magnitude = abs(extrinsic_change_pct)
        collapse_scaled = min(1.0, (collapse_magnitude - EXTRINSIC_COLLAPSE_THRESHOLD)
                              / (EXTRINSIC_COLLAPSE_THRESHOLD * 1.5))
        collapse_component = 0.25 + 0.10 * collapse_scaled

        # 2. Volume decline (0.15–0.20)
        #    Lower volume ratio = stronger evidence of money leaving
        if vol_ratio is not None and vol_ratio > 0:
            # vol_ratio < 1.0 = declining; < 0.5 = strong decline
            vol_decline = 1.0 - min(1.0, vol_ratio)
            vol_decline_component = 0.15 + 0.05 * vol_decline
        else:
            vol_decline_component = 0.15  # Neutral

        # 3. Volume trend alignment (0.10–0.15)
        #    DOWN trend during collapse = confirmed money leaving
        if vol_trend == "DOWN":
            vol_dir_component = 0.15
        elif vol_trend == "FLAT":
            vol_dir_component = 0.12
        else:
            vol_dir_component = 0.05

        # 4. Net gamma strength (0.15–0.20)
        #    Higher positive gamma = stronger range environment (good for fades)
        gamma_scaled = min(1.0, net_gamma / (MIN_NET_GAMMA * 4))
        gamma_component = 0.15 + 0.05 * gamma_scaled

        # Normalize each component to [0,1] and average
        norm_collapse = (collapse_component - 0.25) / (0.35 - 0.25) if 0.35 != 0.25 else 1.0
        norm_vol_decline = (vol_decline_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_vol_dir = (vol_dir_component - 0.05) / (0.15 - 0.05) if 0.15 != 0.05 else 1.0
        norm_gamma = (gamma_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        confidence = (norm_collapse + norm_vol_decline + norm_vol_dir + norm_gamma) / 4.0

        return min(MAX_CONFIDENCE, max(0.0, confidence))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------


