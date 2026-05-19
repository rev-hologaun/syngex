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
from strategies.utils import normalize_confidence

logger = logging.getLogger("Syngex.Strategies.ExtrinsicIntrinsicFlow")

# ---------------------------------------------------------------------------
# Default constants (can be overridden via params)
# ---------------------------------------------------------------------------

DEFAULT_EXTRINSIC_EXPANSION_THRESHOLD = 0.03    # 3% expansion
DEFAULT_EXTRINSIC_COLLAPSE_THRESHOLD = 0.10     # 10% collapse
DEFAULT_VOLUME_SPIKE_RATIO = 1.30               # 130% of avg (1.3×)
DEFAULT_MIN_NET_GAMMA = 500000.0
DEFAULT_STOP_PCT = 0.005                        # 0.5% stop
DEFAULT_TARGET_PCT = 0.008                      # 0.8% target (1.6:1 R:R)
DEFAULT_MIN_CONFIDENCE = 0.25
DEFAULT_MAX_CONFIDENCE = 0.80                   # v2 cap
DEFAULT_MIN_DATA_POINTS = 5

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

    def __init__(self, calculator, params: Optional[Dict[str, Any]] = None):
        super().__init__(calculator)
        self._params = params or {}

    def _apply_params(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply params to data dict and return updated data."""
        data["extrinsic_expansion_threshold"] = self._params.get("extrinsic_expansion_threshold", DEFAULT_EXTRINSIC_EXPANSION_THRESHOLD)
        data["extrinsic_collapse_threshold"] = self._params.get("extrinsic_collapse_threshold", DEFAULT_EXTRINSIC_COLLAPSE_THRESHOLD)
        data["volume_spike_ratio"] = self._params.get("volume_spike_ratio", DEFAULT_VOLUME_SPIKE_RATIO)
        data["min_net_gamma"] = self._params.get("min_net_gamma", DEFAULT_MIN_NET_GAMMA)
        data["stop_pct"] = self._params.get("stop_pct", DEFAULT_STOP_PCT)
        data["target_pct"] = self._params.get("target_pct", DEFAULT_TARGET_PCT)
        data["min_confidence"] = self._params.get("min_confidence", DEFAULT_MIN_CONFIDENCE)
        data["max_confidence"] = self._params.get("max_confidence", DEFAULT_MAX_CONFIDENCE)
        data["min_data_points"] = self._params.get("min_data_points", DEFAULT_MIN_DATA_POINTS)
        return data

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return extrinsic/intrinsic flow signals.

        Returns empty list when no conviction signal is detected.
        """
        # Apply params to data
        data = self._apply_params(data)

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
        if net_gamma < data.get("min_net_gamma", DEFAULT_MIN_NET_GAMMA):
            return []

        # --- Use main.py's populated extrinsic window ---
        extrinsic_window = rolling_data.get(KEY_EXTRINSIC_PROXY_5M)
        if extrinsic_window is None:
            return []
        if extrinsic_window.count < data.get("min_data_points", DEFAULT_MIN_DATA_POINTS):
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
        if volume_up_5m.count < data.get("min_data_points", DEFAULT_MIN_DATA_POINTS) or volume_down_5m.count < data.get("min_data_points", DEFAULT_MIN_DATA_POINTS):
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
        if extrinsic_change_pct < data.get("extrinsic_expansion_threshold", DEFAULT_EXTRINSIC_EXPANSION_THRESHOLD):
            return None

        # Volume must be spiking
        if vol_ratio is None or vol_ratio < data.get("volume_spike_ratio", DEFAULT_VOLUME_SPIKE_RATIO):
            return None

        # Volume trend must confirm bullish direction
        if vol_trend not in ["UP"]:
            return None

        # Compute confidence
        confidence = self._compute_long_confidence(
            extrinsic_change_pct, vol_ratio, vol_trend,
            net_gamma, price, data,
        )

        if confidence < data.get("min_confidence", DEFAULT_MIN_CONFIDENCE):
            return None

        # Extract trend from price window for metadata
        rolling_data = data.get("rolling_data", {})
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        # Build signal
        stop_pct = data.get("stop_pct", DEFAULT_STOP_PCT)
        target_pct = data.get("target_pct", DEFAULT_TARGET_PCT)
        stop = price * (1 - stop_pct)
        target = price * (1 + target_pct)

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
        if extrinsic_change_pct < data.get("extrinsic_expansion_threshold", DEFAULT_EXTRINSIC_EXPANSION_THRESHOLD):
            return None

        # Volume must be spiking
        if vol_ratio is None or vol_ratio < data.get("volume_spike_ratio", DEFAULT_VOLUME_SPIKE_RATIO):
            return None

        # Volume trend must confirm bearish direction
        if vol_trend not in ["DOWN"]:
            return None

        # Compute confidence
        confidence = self._compute_short_confidence(
            extrinsic_change_pct, vol_ratio, vol_trend,
            net_gamma, price, data,
        )

        if confidence < data.get("min_confidence", DEFAULT_MIN_CONFIDENCE):
            return None

        # Extract trend from price window for metadata
        rolling_data = data.get("rolling_data", {})
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        # Build signal
        stop_pct = data.get("stop_pct", DEFAULT_STOP_PCT)
        target_pct = data.get("target_pct", DEFAULT_TARGET_PCT)
        stop = price * (1 + stop_pct)
        target = price * (1 - target_pct)

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
                "stop_pct": data.get("stop_pct", DEFAULT_STOP_PCT),
                "target_pct": data.get("target_pct", DEFAULT_TARGET_PCT),
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
        if extrinsic_change_pct > -data.get("extrinsic_collapse_threshold", DEFAULT_EXTRINSIC_COLLAPSE_THRESHOLD):
            return None

        # Volume must be declining or flat
        if vol_trend not in ["DOWN", "FLAT"]:
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
            net_gamma, price, data,
        )

        if confidence < data.get("min_confidence", DEFAULT_MIN_CONFIDENCE):
            return None

        # Extract trend from price window for metadata
        rolling_data = data.get("rolling_data", {})
        price_window = rolling_data.get(KEY_VOLUME_UP_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        # Build signal
        stop_pct = data.get("stop_pct", DEFAULT_STOP_PCT)
        target_pct = data.get("target_pct", DEFAULT_TARGET_PCT)
        if fade_direction == Direction.LONG:
            stop = price * (1 + stop_pct)
            target = price * (1 + target_pct)
        else:
            stop = price * (1 - stop_pct)
            target = price * (1 - target_pct)

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
                "stop_pct": data.get("stop_pct", DEFAULT_STOP_PCT),
                "target_pct": data.get("target_pct", DEFAULT_TARGET_PCT),
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
        data: Dict[str, Any],
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
        exp_threshold = data.get("extrinsic_expansion_threshold", DEFAULT_EXTRINSIC_EXPANSION_THRESHOLD)
        exp_scaled = min(1.0, (extrinsic_change_pct - exp_threshold)
                         / (exp_threshold * 3))
        exp_component = 0.20 + 0.10 * exp_scaled

        # 2. Volume spike magnitude (0.20–0.25)
        #    1.5× = baseline, 3×+ = max weight
        vol_spike = data.get("volume_spike_ratio", DEFAULT_VOLUME_SPIKE_RATIO)
        vol_scaled = min(1.0, (vol_ratio - vol_spike)
                         / (vol_spike))
        vol_component = 0.20 + 0.05 * vol_scaled

        # 3. Volume direction alignment (0.10–0.15)
        #    UP trend = confirmed bullish
        if vol_trend == "UP":
            vol_dir_component = 0.15
        else:
            vol_dir_component = 0.05

        # 4. Net gamma strength (0.15–0.20)
        #    Higher positive gamma = stronger positive regime
        min_gamma = data.get("min_net_gamma", DEFAULT_MIN_NET_GAMMA)
        gamma_scaled = min(1.0, net_gamma / (min_gamma * 4))
        gamma_component = 0.15 + 0.05 * gamma_scaled

        # Normalize each component to [0,1] and average
        norm_exp = normalize_confidence(exp_component, 0.20, 0.30)
        norm_vol = normalize_confidence(vol_component, 0.20, 0.25)
        norm_vol_dir = normalize_confidence(vol_dir_component, 0.05, 0.15)
        norm_gamma = normalize_confidence(gamma_component, 0.15, 0.20)
        confidence = (norm_exp + norm_vol + norm_vol_dir + norm_gamma) / 4.0

        max_conf = data.get("max_confidence", DEFAULT_MAX_CONFIDENCE)
        return min(max_conf, max(0.0, confidence))

    def _compute_short_confidence(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        price: float,
        data: Dict[str, Any],
    ) -> float:
        """
        Compute confidence for SHORT (extrinsic expansion + bearish volume).

        Same factors as LONG but for bearish direction.
        """
        # 1. Extrinsic expansion magnitude (0.20–0.30)
        exp_threshold = data.get("extrinsic_expansion_threshold", DEFAULT_EXTRINSIC_EXPANSION_THRESHOLD)
        exp_scaled = min(1.0, (extrinsic_change_pct - exp_threshold)
                         / (exp_threshold * 3))
        exp_component = 0.20 + 0.10 * exp_scaled

        # 2. Volume spike magnitude (0.20–0.25)
        vol_spike = data.get("volume_spike_ratio", DEFAULT_VOLUME_SPIKE_RATIO)
        vol_scaled = min(1.0, (vol_ratio - vol_spike)
                         / (vol_spike))
        vol_component = 0.20 + 0.05 * vol_scaled

        # 3. Volume direction alignment (0.10–0.15)
        if vol_trend == "DOWN":
            vol_dir_component = 0.15
        else:
            vol_dir_component = 0.05

        # 4. Net gamma strength (0.15–0.20)
        min_gamma = data.get("min_net_gamma", DEFAULT_MIN_NET_GAMMA)
        gamma_scaled = min(1.0, net_gamma / (min_gamma * 4))
        gamma_component = 0.15 + 0.05 * gamma_scaled

        # Normalize each component to [0,1] and average
        norm_exp = normalize_confidence(exp_component, 0.20, 0.30)
        norm_vol = normalize_confidence(vol_component, 0.20, 0.25)
        norm_vol_dir = normalize_confidence(vol_dir_component, 0.05, 0.15)
        norm_gamma = normalize_confidence(gamma_component, 0.15, 0.20)
        confidence = (norm_exp + norm_vol + norm_vol_dir + norm_gamma) / 4.0

        max_conf = data.get("max_confidence", DEFAULT_MAX_CONFIDENCE)
        return min(max_conf, max(0.0, confidence))

    def _compute_fade_confidence(
        self,
        extrinsic_change_pct: float,
        vol_ratio: float,
        vol_trend: str,
        net_gamma: float,
        price: float,
        data: Dict[str, Any],
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
        collapse_threshold = data.get("extrinsic_collapse_threshold", DEFAULT_EXTRINSIC_COLLAPSE_THRESHOLD)
        collapse_magnitude = abs(extrinsic_change_pct)
        collapse_scaled = min(1.0, (collapse_magnitude - collapse_threshold)
                              / (collapse_threshold * 1.5))
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
        min_gamma = data.get("min_net_gamma", DEFAULT_MIN_NET_GAMMA)
        gamma_scaled = min(1.0, net_gamma / (min_gamma * 4))
        gamma_component = 0.15 + 0.05 * gamma_scaled

        # Normalize each component to [0,1] and average
        norm_collapse = normalize_confidence(collapse_component, 0.25, 0.35)
        norm_vol_decline = normalize_confidence(vol_decline_component, 0.15, 0.20)
        norm_vol_dir = normalize_confidence(vol_dir_component, 0.05, 0.15)
        norm_gamma = normalize_confidence(gamma_component, 0.15, 0.20)
        confidence = (norm_collapse + norm_vol_decline + norm_vol_dir + norm_gamma) / 4.0

        max_conf = data.get("max_confidence", DEFAULT_MAX_CONFIDENCE)
        return min(max_conf, max(0.0, confidence))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------


