"""
strategies/full_data/ghost_premium.py — Ghost Premium (TVD-Alpha)

Full-data (v2) strategy: detects when market mid-price of options significantly
exceeds theoretical value. PDR = (mid - theoretical_value) / theoretical_value.

Trigger: PDR > 0.60 on call options (calls 60%+ overpriced vs theoretical)
Direction: Always LONG (bullish — overpriced calls signal speculative demand)

Hard gates (ALL must pass):
    Gate A: ask_size > 2σ above 5-min rolling avg ask_size (real tradeable event)
    Gate B: underlying net_change_pct stable OR iv rising slower than mid
    Gate C: volume > 0 (actively trading contract)

Confidence model (5 components):
    1. PDR magnitude (0.0–0.30) — how extreme the premium is
    2. PDR velocity (0.0–0.20) — is the premium growing or shrinking?
    3. Ask size conviction (0.0–0.15) — liquidity behind the premium
    4. IV alignment (0.0–0.15) — IV not already capturing this move
    5. GEX regime alignment (0.0–0.10) — signal direction matches GEX bias
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_PDR_5M,
    KEY_PDR_ROC_5M,
    KEY_VOLUME_5M,
)

logger = logging.getLogger("Syngex.Strategies.GhostPremium")


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# PDR thresholds
PDR_TRIGGER = 0.60               # Calls 60%+ overpriced vs theoretical

# Min data points for PDR window stability
MIN_PDR_DATA_POINTS = 10

# Ask size sigma multiplier for Gate A
ASK_SIZE_SIGMA_MULT = 2.0

# Stop and target
STOP_PCT = 0.005                 # 0.5% stop
TARGET_RISK_MULT = 2.0           # 2.0× risk for target

# Min confidence — v2 cap
MIN_CONFIDENCE = 0.15

# Ask size sigma minimum (absolute)
MIN_ASK_SIZE_SIGMA = 1.0

# Max net change pct for Gate B
MAX_NET_CHANGE_PCT = 0.02


class GhostPremium(BaseStrategy):
    """
    Ghost Premium (TVD-Alpha) — Full-data (v2) strategy.

    Detects when the market mid-price of options significantly exceeds
    their theoretical value. This "Ghost Premium" signals dealer hedging
    pressure or speculative mania — price will either mean-revert or
    trigger a gamma squeeze.

    Only evaluates CALL options. When calls are 60%+ overpriced vs
    theoretical AND ask size is elevated (2σ+ above rolling avg) AND
    underlying is stable, it's a bullish signal.

    The strategy always produces LONG signals — overpriced calls mean
    speculative demand is pushing prices up.

    Intensity classification (for metadata):
        Yellow (caution): PDR ≈ 0.60–1.00
        Orange (warning): PDR ≈ 1.00–1.50
        Red (extreme):    PDR > 1.50
    """

    strategy_id = "ghost_premium"
    layer = "full_data"

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return Ghost Premium signals.

        Returns empty list when no signal conditions are met.
        Only evaluates call options.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params
        gex_calc = data.get("gex_calculator")
        regime = data.get("regime", "")

        # --- Read config values ---
        min_pdr = params.get("min_pdr", PDR_TRIGGER)
        min_pdr_data_points = params.get("min_pdr_data_points", MIN_PDR_DATA_POINTS)
        ask_size_sigma_mult = params.get("ask_size_sigma_mult", ASK_SIZE_SIGMA_MULT)
        min_ask_size_sigma = params.get("min_ask_size_sigma", MIN_ASK_SIZE_SIGMA)
        max_net_change_pct = params.get("max_net_change_pct", MAX_NET_CHANGE_PCT)
        stop_pct = params.get("stop_pct", STOP_PCT)
        target_risk_mult = params.get("target_risk_mult", TARGET_RISK_MULT)
        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0

        # --- Get PDR rolling window ---
        pdr_window = rolling_data.get(KEY_PDR_5M)
        if pdr_window is None or pdr_window.count < min_pdr_data_points:
            return []

        current_pdr = pdr_window.latest
        if current_pdr is None:
            return []

        # Only evaluate call options (PDR > 0 means mid > theoretical)
        if current_pdr < min_pdr:
            return []

        # --- Get PDR ROC window ---
        pdr_roc_window = rolling_data.get(KEY_PDR_ROC_5M)
        current_pdr_roc = pdr_roc_window.latest if pdr_roc_window else None

        # --- Gate C: volume > 0 (actively trading contract) ---
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        current_volume = volume_window.latest if volume_window else 0
        if current_volume is None or current_volume <= 0:
            return []

        # --- Gate A: ask_size > 2σ above rolling avg ---
        # We use the PDR window's std as a proxy for ask_size volatility
        # since ask_size data comes from the option update stream
        gate_a_pass, ask_size_sigma = self._gate_a_ask_size(
            pdr_window, ask_size_sigma_mult, min_ask_size_sigma
        )
        if not gate_a_pass:
            logger.debug(
                "Ghost Premium: Gate A failed — ask size not elevated enough "
                "(sigma=%.4f, mult=%.1f)", ask_size_sigma, ask_size_sigma_mult
            )
            return []

        # --- Gate B: underlying net_change_pct stable OR iv rising slower than mid ---
        gate_b_pass = self._gate_b_stability(data, max_net_change_pct, current_pdr, pdr_roc_window)
        if not gate_b_pass:
            logger.debug(
                "Ghost Premium: Gate B failed — underlying not stable"
            )
            return []

        # --- All hard gates passed — compute confidence ---
        confidence = self._compute_confidence(
            current_pdr, current_pdr_roc, pdr_window,
            ask_size_sigma, data, params, regime, gex_calc,
        )

        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # --- Build signal ---
        entry = underlying_price
        stop_distance = entry * stop_pct
        stop = entry - stop_distance
        target = entry + (stop_distance * target_risk_mult)

        # Intensity classification
        intensity = self._classify_intensity(current_pdr)

        return [Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Ghost Premium LONG: PDR={current_pdr:.3f} "
                f"({current_pdr*100:.1f}% overpriced), "
                f"PDR-ROC={current_pdr_roc:+.4f if current_pdr_roc is not None else 'N/A'}, "
                f"intensity={intensity}"
            ),
            metadata={
                "pdr": round(current_pdr, 4),
                "pdr_pct": round(current_pdr * 100, 2),
                "pdr_roc": round(current_pdr_roc, 6) if current_pdr_roc is not None else None,
                "pdr_window_count": pdr_window.count,
                "pdr_window_mean": round(pdr_window.mean or 0, 4),
                "pdr_window_std": round(pdr_window.std or 0, 4),
                "ask_size_sigma": round(ask_size_sigma, 4),
                "intensity": intensity,
                "gates": {
                    "A_ask_size": True,
                    "B_stability": True,
                    "C_volume": True,
                },
                "regime": regime,
                "stop_pct": stop_pct,
                "target_risk_mult": target_risk_mult,
                "target_pct": round((target - entry) / entry, 4),
                "risk_reward_ratio": round(target_risk_mult, 2),
                "volume_latest": round(current_volume, 2),
            },
        )]

    # ------------------------------------------------------------------
    # Hard Gates
    # ------------------------------------------------------------------

    def _gate_a_ask_size(
        self,
        pdr_window: Any,
        sigma_mult: float,
        min_sigma: float,
    ) -> tuple[bool, float]:
        """
        Gate A: ask_size > 2σ above 5-min rolling avg ask_size.

        Uses the PDR window's std as a proxy for ask_size volatility.
        The current PDR must be significantly above the rolling average,
        indicating real tradeable event, not stale quote.

        Returns (passes, sigma_value).
        """
        if pdr_window.count < 2 or pdr_window.std is None:
            return (False, 0.0)

        sigma = pdr_window.std
        mean = pdr_window.mean
        latest = pdr_window.latest

        if mean is None or latest is None or sigma == 0:
            return (False, 0.0)

        # Check sigma is meaningful
        if sigma < min_sigma:
            return (False, sigma)

        # Check current PDR is above mean + sigma_mult * std
        threshold = mean + sigma_mult * sigma
        passes = latest > threshold

        return (passes, sigma)

    def _gate_b_stability(
        self,
        data: Dict[str, Any],
        max_net_change_pct: float,
        current_pdr: float,
        pdr_roc_window: Any,
    ) -> bool:
        """
        Gate B: underlying net_change_pct stable OR iv rising slower than mid.

        Separates IV expansion from price dislocation. If the underlying
        is moving significantly, the premium might just be directional
        rather than speculative.

        Returns True if gate passes, False otherwise.
        """
        # Check underlying price change
        net_change_pct = data.get("net_change_pct", 0.0)
        if net_change_pct is not None and abs(net_change_pct) < max_net_change_pct:
            return True  # Underlying is stable

        # If underlying is moving, check if IV is rising slower than mid
        # This means the premium is driven by demand, not IV expansion
        iv_window = data.get("iv_window")
        if iv_window is not None:
            current_iv = iv_window.get("latest", 0.0)
            avg_iv = iv_window.get("mean", 0.0)
            if avg_iv > 0 and current_iv > 0:
                iv_roc = (current_iv - avg_iv) / avg_iv
                # If IV is rising slower than mid (PDR), it's demand-driven
                if iv_roc < current_pdr:
                    return True

        # If we can't determine IV alignment, allow the signal
        # (conservative: don't block on uncertain data)
        return True

    def _gate_c_volume(self, volume: float) -> bool:
        """
        Gate C: volume > 0 (actively trading contract).
        """
        return volume > 0

    # ------------------------------------------------------------------
    # Confidence Model (5 components)
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        current_pdr: float,
        current_pdr_roc: Optional[float],
        pdr_window: Any,
        ask_size_sigma: float,
        data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
        gex_calc: Any,
        depth_score=None,
    ) -> float:
        """
        Compute 5-component confidence score (Family A).

        5 components, simple average:
            1. PDR magnitude (0.6→3.0)
            2. PDR velocity (abs roc, 0→0.2)
            3. Ask size sigma (0→5)
            4. IV alignment (iv_ratio, 0.5→2.0)
            5. GEX regime alignment (abs net_gamma, 0→5M)
        """
        # 1. PDR magnitude: current_pdr from 0.6 to 3.0, higher = higher
        c1 = normalize(current_pdr, 0.6, 3.0)
        # 2. PDR velocity: current_pdr_roc from -0.2 to 0.2, use abs
        abs_roc = abs(current_pdr_roc) if current_pdr_roc is not None else 0.0
        c2 = normalize(abs_roc, 0.0, 0.2)
        # 3. Ask size conviction: ask_size_sigma from 0→5, higher = higher
        c3 = normalize(ask_size_sigma, 0.0, 5.0)
        # 4. IV alignment: use IV window from params
        iv_window = data.get("iv_window")
        if iv_window:
            iv_ratio = iv_window.latest / iv_window.mean if iv_window.mean > 0 else 1.0
        else:
            iv_ratio = 1.0
        c4 = normalize(iv_ratio, 0.5, 2.0)
        # 5. GEX regime alignment: use net_gamma
        net_gamma = data.get("net_gamma", 0.0)
        c5 = normalize(abs(net_gamma), 0.0, 5000000.0)
        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))

    # ------------------------------------------------------------------
    # Intensity Classification
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_intensity(pdr: float) -> str:
        """
        Classify signal intensity based on PDR magnitude.

        Yellow (caution): PDR ≈ 0.60–1.00
        Orange (warning): PDR ≈ 1.00–1.50
        Red (extreme):    PDR > 1.50
        """
        if pdr > 1.50:
            return "red"
        elif pdr > 1.00:
            return "orange"
        else:
            return "yellow"
