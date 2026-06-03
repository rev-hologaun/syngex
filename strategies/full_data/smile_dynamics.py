"""
strategies/full_data/smile_dynamics.py — IV Smile Dynamics (CURVE-ALPHA)

Measures the Curvature Asymmetry Index Ω across multiple strikes.
Ω = |Slope_Put_Wing| / |Slope_Call_Wing|

Put-side curvature dominant (Ω rising) = fear jaw opening → SHORT
Call-side curvature dominant (Ω falling) = euphoria jaw closing → LONG
Leading indicator: curvature shifts often precede price moves.

Trigger: |Ω change| > 2σ over 15-minute rolling window

4 soft scores (ALL contribute to confidence, 0.0–1.0):
    Score A: Liquidity — recent 5m volume, normalized to 10k ceiling
    Score B: GEX regime — alignment between direction and gamma regime
    Score C: Vol divergence — slope magnitude relative to 0.10 ceiling
    Score D: Z-score — Ω ROC significance in σ units

Direction selection: LONG if long_dir_score >= short_dir_score, else SHORT.
Each direction score combines ROC magnitude with regime alignment.

10-component confidence model (each component 0.0–1.0, averaged):
    1. Ω magnitude (normalized 0→5)
    2. Ω velocity (normalized abs ROC, 0→0.1)
    3. Ω sigma significance (normalized 0→5)
    4. Put slope magnitude (normalized 0→0.5)
    5. Call slope magnitude (normalized 0→0.5)
    6. Liquidity score (soft gate A)
    7. GEX regime score (soft gate B)
    8. Vol divergence score (soft gate C)
    9. Z-score significance (soft gate D)
    10. Direction score (direction-specific: long or short)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_CURVE_OMEGA_5M,
    KEY_CURVE_OMEGA_ROC_5M,
    KEY_CURVE_OMEGA_SIGMA_5M,
    KEY_PUT_SLOPE_5M,
    KEY_CALL_SLOPE_5M,
)

logger = logging.getLogger("Syngex.Strategies.SmileDynamics")


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))


MIN_CONFIDENCE = 0.0


class SmileDynamics(BaseStrategy):
    """
    IV Smile Dynamics strategy — tracks curvature asymmetry via Ω.

    Ω (Curvature Asymmetry Index) = |Slope_Put_Wing| / |Slope_Call_Wing|

    Put-side curvature dominant (Ω rising) = fear jaw opening → SHORT
    Call-side curvature dominant (Ω falling) = euphoria jaw closing → LONG

    LONG: Ω falling (flattening smile) AND GEX regime is POSITIVE
    SHORT: Ω rising (opening smile) AND GEX regime is NEGATIVE
    """

    strategy_id = "smile_dynamics"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for IV smile dynamics signal.

        Returns a single LONG or SHORT signal when conditions are met,
        or empty list when gates fail or no clear signal.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params

        regime_soft = params.get("regime_soft", True)
        regime = data.get("regime", "")

        # 1. Get Ω data from rolling windows
        min_omega_data_points = params.get("min_omega_data_points", 5)
        min_omega_sigma = params.get("min_omega_sigma", 2.0)

        omega_window = rolling_data.get(KEY_CURVE_OMEGA_5M)
        omega_roc_window = rolling_data.get(KEY_CURVE_OMEGA_ROC_5M)
        omega_sigma_window = rolling_data.get(KEY_CURVE_OMEGA_SIGMA_5M)
        put_slope_window = rolling_data.get(KEY_PUT_SLOPE_5M)
        call_slope_window = rolling_data.get(KEY_CALL_SLOPE_5M)

        if not omega_window or omega_window.count < min_omega_data_points:
            return []
        if not omega_sigma_window or omega_sigma_window.count < min_omega_data_points:
            return []

        current_omega = omega_window.values[-1]
        current_omega_sigma = omega_sigma_window.values[-1] if omega_sigma_window else 0.0
        current_omega_roc = omega_roc_window.values[-1] if omega_roc_window else 0.0
        current_put_slope = put_slope_window.values[-1] if put_slope_window else 0.0
        current_call_slope = call_slope_window.values[-1] if call_slope_window else 0.0

        # 2. Determine signal direction based on Ω change
        # Ω falling (negative ROC) = call-side dominant / smile flattening → LONG
        # Ω rising (positive ROC) = put-side dominant / jaw opening → SHORT
        long_signal = current_omega_roc < 0
        short_signal = current_omega_roc > 0

        if not long_signal and not short_signal:
            return []

        # Compute direction scores to select the stronger direction
        long_dir_score = self._score_direction(
            current_omega_roc, "LONG", regime, params,
        )
        short_dir_score = self._score_direction(
            current_omega_roc, "SHORT", regime, params,
        )

        if long_dir_score >= short_dir_score:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Check if Ω change exceeds σ threshold
        if current_omega_sigma <= 0:
            return []

        omega_zscore = abs(current_omega_roc) / current_omega_sigma

        if omega_zscore < min_omega_sigma:
            logger.debug(
                "Smile Dynamics: Ω z-score %.2f below threshold %.1f for %s",
                omega_zscore, min_omega_sigma, direction,
            )
            return []

        # 4. Compute soft gate scores (0.0–1.0)
        liquidity_score = self._score_liquidity(rolling_data, params)
        regime_score = self._score_gex_regime(direction, regime)
        vol_div_score = self._score_vol_divergence(
            current_put_slope, current_call_slope, current_omega_sigma, params
        )

        # 5. Compute confidence (10-component model)
        confidence = self._compute_confidence(
            current_omega,
            current_omega_roc,
            current_omega_sigma,
            omega_zscore,
            current_put_slope,
            current_call_slope,
            direction,
            rolling_data,
            params,
            regime,
            liquidity_score=liquidity_score,
            regime_score=regime_score,
            vol_div_score=vol_div_score,
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
        if omega_zscore > 3.0:
            intensity = "red"
        elif omega_zscore > 2.0:
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
                f"Smile dynamics {direction}: Ω={current_omega:.4f}, "
                f"ROC={current_omega_roc:+.4f}, z={omega_zscore:.1f}σ"
            ),
            metadata={
                "direction": direction,
                "omega": round(current_omega, 6),
                "omega_roc": round(current_omega_roc, 6),
                "omega_sigma": round(current_omega_sigma, 6),
                "omega_zscore": round(omega_zscore, 2),
                "put_slope": round(current_put_slope, 6),
                "call_slope": round(current_call_slope, 6),
                "intensity": intensity,
                "regime": regime,
                "long_dir_score": round(long_dir_score, 3),
                "short_dir_score": round(short_dir_score, 3),
                "gates": {
                    "A_liquidity": round(liquidity_score, 3),
                    "B_gex_regime": round(regime_score, 3),
                    "C_vol_divergence": round(vol_div_score, 3),
                    "D_zscore": round(zscore_score, 3),
                },
            },
        )]

    def _score_liquidity(
        self,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> float:
        """
        Score A: Liquidity score (0.0–1.0).

        Based on recent 5m volume — higher volume = higher confidence.
        """
        volume_window = rolling_data.get("volume_5m")
        if not volume_window:
            return 0.0
        if volume_window.count < 5:
            return 0.5
        latest = volume_window.values[-1]
        if latest > 0:
            return min(1.0, latest / 10000.0)
        return 0.0

    def _score_gex_regime(self, direction: str, regime: str) -> float:
        """
        Score B: GEX regime alignment score (0.0–1.0).

        Perfect alignment = 1.0, mismatch = 0.3, unknown = 0.5.
        """
        if direction == "LONG" and regime == "POSITIVE":
            return 1.0
        if direction == "SHORT" and regime == "NEGATIVE":
            return 1.0
        if direction == "LONG" and regime == "NEGATIVE":
            return 0.3
        if direction == "SHORT" and regime == "POSITIVE":
            return 0.3
        # regime is empty/unknown
        return 0.5

    def _score_vol_divergence(
        self,
        put_slope: float,
        call_slope: float,
        omega_sigma: float,
        params: Dict[str, Any],
    ) -> float:
        """
        Score C: Volatility divergence score (0.0–1.0).

        Measures how much the put/call slope divergence contributes to
        the signal. Normalized by a 0.10 ceiling.
        """
        if omega_sigma <= 0:
            return 0.0
        magnitude = max(abs(put_slope), abs(call_slope))
        return min(1.0, magnitude / 0.10)

    def _compute_confidence(
        self,
        current_omega: float,
        current_omega_roc: float,
        current_omega_sigma: float,
        omega_zscore: float,
        current_put_slope: float,
        current_call_slope: float,
        direction: str,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
        liquidity_score: float = 0.0,
        regime_score: float = 0.0,
        vol_div_score: float = 0.0,
        zscore_score: float = 0.0,
        long_dir_score: float = 0.0,
        short_dir_score: float = 0.0,
    ) -> float:
        """
        Compute 10-component confidence score.

        Components 1-5: raw market data metrics (normalized to 0-1)
        Components 6-9: soft gate scores (already 0-1)
        Component 10: direction-specific score (long or short)

        Returns 0.0–1.0.
        """
        # 1. Ω magnitude: higher = more curvature asymmetry
        c1 = normalize(current_omega, 0.0, 5.0)
        # 2. Ω velocity: use abs — magnitude of change matters
        c2 = normalize(abs(current_omega_roc), 0.0, 0.1)
        # 3. Ω sigma significance: higher = more statistically notable
        c3 = normalize(current_omega_sigma, 0.0, 5.0)
        # 4. Put slope magnitude
        c4 = normalize(abs(current_put_slope), 0.0, 0.5)
        # 5. Call slope magnitude
        c5 = normalize(abs(current_call_slope), 0.0, 0.5)
        # 6. Liquidity soft gate
        c6 = liquidity_score
        # 7. GEX regime soft gate (replaces broken regime mismatch penalty)
        c7 = regime_score
        # 8. Vol divergence soft gate
        c8 = vol_div_score
        # 9. Z-score significance soft gate
        c9 = zscore_score
        # 10. Direction-specific score
        c10 = long_dir_score if direction == "LONG" else short_dir_score

        confidence = (c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10) / 10.0
        return min(1.0, max(0.0, confidence))

    def _score_direction(
        self,
        current_omega_roc: float,
        direction: str,
        regime: str,
        params: Dict[str, Any],
    ) -> float:
        """
        Score the strength of a directional bias.

        Combines ROC magnitude (primary signal) with regime alignment
        (secondary signal) to produce a 0.0–1.0 score.

        LONG: negative ROC (smile flattening) with positive GEX regime
        SHORT: positive ROC (jaw opening) with negative GEX regime
        """
        # ROC magnitude as primary signal (0.0–1.0)
        roc_mag = abs(current_omega_roc)
        roc_score = normalize(roc_mag, 0.0, 0.1)

        # Regime alignment as secondary signal (0.3–1.0)
        regime_aligned = (
            (direction == "LONG" and regime == "POSITIVE")
            or (direction == "SHORT" and regime == "NEGATIVE")
        )
        regime_factor = 1.0 if regime_aligned else 0.3

        return roc_score * regime_factor
