"""
strategies/full_data/skew_dynamics.py — IV Skew Dynamics (SKEW-ALPHA)

Tracks how the volatility smile changes over time via the Skewness Coefficient Ψ.
Ψ = (IV_Put_Wing - IV_Call_Wing) / IV_ATM

Steepening skew (Ψ rising) = rising fear → SHORT
Flattening skew (Ψ falling) = complacency → LONG

4 soft scores (no hard gates):
    A: Liquidity — combined OI + volume of wing strikes above rolling 1h threshold
    B: GEX regime alignment — directional alignment with gamma regime
    C: IV divergence purity — signal driven by relative IV change, not ATM vol spike
    D: Z-score significance — magnitude of Ψ move in σ units

Confidence model (10 components):
    1. Ψ magnitude (0.0–5.0 range)
    2. Ψ velocity (ROC, 0.0–0.1 range)
    3. Ψ sigma significance (0.0–5.0 range)
    4. Put slope (0.0–0.5 range)
    5. Call slope (0.0–0.5 range)
    6. Liquidity score
    7. GEX regime score
    8. IV divergence purity score
    9. Z-score significance score
    10. Direction-specific score (long or short, whichever is higher)

Direction selected by highest direction score (not binary ROC check).
"""

from __future__ import annotations

import math
import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_SKEW_PSI_5M,
    KEY_SKEW_PSI_ROC_5M,
    KEY_SKEW_PSI_SIGMA_5M,
)

logger = logging.getLogger("Syngex.Strategies.SkewDynamics")


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))


MIN_CONFIDENCE = 0.0


class SkewDynamics(BaseStrategy):
    """
    IV Skew Dynamics strategy — tracks volatility smile changes via Ψ.

    Ψ (Skewness Coefficient) = (IV_Put_Wing - IV_Call_Wing) / IV_ATM

    A rising Ψ means the put wing is expanding relative to the call wing,
    signaling rising fear (fear of downside). A falling Ψ means the put wing
    is compressing relative to the call wing, signaling complacency.

    LONG: Ψ falling (flattening skew) AND GEX regime is POSITIVE
    SHORT: Ψ rising (steepening skew) AND GEX regime is NEGATIVE
    """

    strategy_id = "skew_dynamics"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for IV skew dynamics signal.

        Returns a single LONG or SHORT signal when conditions are met,
        or empty list when gates fail or no clear signal.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params
        regime = data.get("regime", "")

        # 1. Get Ψ data from rolling windows
        min_psi_data_points = params.get("min_psi_data_points", 5)
        min_psi_sigma = params.get("min_psi_sigma", 2.0)

        psi_window = rolling_data.get(KEY_SKEW_PSI_5M)
        psi_roc_window = rolling_data.get(KEY_SKEW_PSI_ROC_5M)
        psi_sigma_window = rolling_data.get(KEY_SKEW_PSI_SIGMA_5M)

        if not psi_window or psi_window.count < min_psi_data_points:
            return []
        if not psi_sigma_window or psi_sigma_window.count < min_psi_data_points:
            return []

        current_psi = psi_window.values[-1]
        current_psi_sigma = psi_sigma_window.values[-1] if psi_sigma_window else 0.0
        current_psi_roc = psi_roc_window.values[-1] if psi_roc_window else 0.0

        # 2. Validate sigma and compute soft scores
        if current_psi_sigma <= 0:
            return []

        psi_zscore = abs(current_psi_roc) / current_psi_sigma
        zscore_score = min(1.0, psi_zscore / 4.0)  # 2σ=0.5, 4σ=1.0

        # Soft direction scores from ROC (negative ROC → long, positive → short)
        long_score = max(0.0, -current_psi_roc)
        short_score = max(0.0, current_psi_roc)
        long_dir_score = min(1.0, long_score / 0.10)
        short_dir_score = min(1.0, short_score / 0.10)

        # Determine direction from soft scores
        if long_dir_score >= short_dir_score:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Compute soft scores (replaces hard gates)
        liquidity_score = self._score_liquidity(rolling_data, params)
        regime_score = self._score_gex_regime(direction, regime)
        iv_purity_score = self._score_iv_divergence(
            current_psi, current_psi_sigma, params
        )

        # 5. Compute confidence (10-component model)
        confidence = self._compute_confidence(
            current_psi,
            current_psi_roc,
            current_psi_sigma,
            psi_zscore,
            direction,
            rolling_data,
            params,
            regime,
            liquidity_score=liquidity_score,
            regime_score=regime_score,
            iv_purity_score=iv_purity_score,
            zscore_score=zscore_score,
            long_dir_score=long_dir_score,
            short_dir_score=short_dir_score,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 6. Build signal with entry/stop/target
        stop_pct = params.get("stop_pct", 0.005)
        target_risk_mult = params.get("target_risk_mult", 2.0)

        entry = underlying_price
        stop_distance = entry * stop_pct

        if direction == "LONG":
            stop = entry - stop_distance
            target = entry + (stop_distance * target_risk_mult)
        else:
            stop = entry + stop_distance
            target = entry - (stop_distance * target_risk_mult)

        direction_enum = Direction.LONG if direction == "LONG" else Direction.SHORT

        # Intensity metadata based on σ level
        if psi_zscore > 3.0:
            intensity = "red"
        elif psi_zscore > 2.0:
            intensity = "orange"
        else:
            intensity = "yellow"

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Skew dynamics {direction}: Ψ={current_psi:.4f}, "
                f"ROC={current_psi_roc:+.4f}, z={psi_zscore:.1f}σ"
            ),
            metadata={
                "direction": direction,
                "psi": round(current_psi, 6),
                "psi_roc": round(current_psi_roc, 6),
                "psi_sigma": round(current_psi_sigma, 6),
                "psi_zscore": round(psi_zscore, 2),
                "intensity": intensity,
                "regime": regime,
                "gates": {
                    "A_liquidity": round(liquidity_score, 3),
                    "B_gex_regime": round(regime_score, 3),
                    "C_iv_divergence": round(iv_purity_score, 3),
                    "D_zscore": round(zscore_score, 3),
                },
                "long_dir_score": round(long_dir_score, 3),
                "short_dir_score": round(short_dir_score, 3),
            },
        )]

    def _score_liquidity(
        self,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> float:
        """
        Soft score for liquidity (0.0–1.0).

        Scales by 5m volume: 10k+ volume → 1.0, below that scales linearly,
        insufficient data → 0.5, no data → 0.0.
        """
        volume_window = rolling_data.get("volume_5m")
        if not volume_window or volume_window.count == 0:
            return 0.0

        if volume_window.count < 5:
            return 0.5

        latest = volume_window.values[-1]
        if latest <= 0:
            return 0.0

        return min(1.0, latest / 10000.0)

    def _score_gex_regime(self, direction: str, regime: str) -> float:
        """
        Soft score for GEX regime alignment (0.0–1.0).

        Full score (1.0) when direction aligns with regime.
        Partial score (0.3) on mismatch.
        Neutral (0.5) when regime is unknown.
        """
        if direction == "LONG" and regime == "POSITIVE":
            return 1.0
        if direction == "SHORT" and regime == "NEGATIVE":
            return 1.0
        if direction == "LONG" and regime == "NEGATIVE":
            return 0.3
        if direction == "SHORT" and regime == "POSITIVE":
            return 0.3
        # regime is empty or unknown
        return 0.5

    def _score_iv_divergence(
        self,
        psi: float,
        psi_sigma: float,
        params: Dict[str, Any],
    ) -> float:
        """
        Soft score for IV divergence purity (0.0–1.0).

        Scales linearly by |ψ| up to 0.10, confirming the signal is
        skew-driven rather than just a vol-level move.
        """
        if psi_sigma <= 0:
            return 0.0

        magnitude = abs(psi)
        return min(1.0, magnitude / 0.10)

    def _compute_confidence(
        self,
        current_psi: float,
        current_psi_roc: float,
        current_psi_sigma: float,
        psi_zscore: float,
        direction: str,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
        liquidity_score: float = 0.0,
        regime_score: float = 0.0,
        iv_purity_score: float = 0.0,
        zscore_score: float = 0.0,
        long_dir_score: float = 0.0,
        short_dir_score: float = 0.0,
    ) -> float:
        """
        Compute 10-component confidence score.

        Components:
            c1: Ψ magnitude (0.0–5.0 range)
            c2: Ψ velocity / ROC (0.0–0.1 range)
            c3: Ψ sigma significance (0.0–5.0 range)
            c4: Put slope (0.0–0.5 range)
            c5: Call slope (0.0–0.5 range)
            c6: Liquidity score
            c7: GEX regime score
            c8: IV divergence purity score
            c9: Z-score significance score
            c10: Direction-specific score (long or short)

        Returns 0.0–1.0.
        """
        # 1. Ψ magnitude: current_psi from 0→5, higher = higher
        c1 = normalize(current_psi, 0.0, 5.0)
        # 2. Ψ velocity: current_psi_roc from -0.1 to 0.1, use abs
        c2 = normalize(abs(current_psi_roc), 0.0, 0.1)
        # 3. Ψ sigma significance: current_psi_sigma from 0→5, higher = higher
        c3 = normalize(current_psi_sigma, 0.0, 5.0)
        # 4. Put slope: direction-specific, normalize to [0,1]
        put_slope = rolling_data.get("put_slope", 0.0)
        c4 = normalize(abs(put_slope), 0.0, 0.5)
        # 5. Call slope: direction-specific, normalize to [0,1]
        call_slope = rolling_data.get("call_slope", 0.0)
        c5 = normalize(abs(call_slope), 0.0, 0.5)
        # 6–10: soft scores (passed in)
        c6 = liquidity_score
        c7 = regime_score
        c8 = iv_purity_score
        c9 = zscore_score
        c10 = long_dir_score if direction == "LONG" else short_dir_score
        confidence = (c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10) / 10.0
        return min(1.0, max(0.0, confidence))
