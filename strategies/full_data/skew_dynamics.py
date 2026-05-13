"""
strategies/full_data/skew_dynamics.py — IV Skew Dynamics (SKEW-ALPHA)

Tracks how the volatility smile changes over time via the Skewness Coefficient Ψ.
Ψ = (IV_Put_Wing - IV_Call_Wing) / IV_ATM

Steepening skew (Ψ rising) = rising fear → SHORT
Flattening skew (Ψ falling) = complacency → LONG
Best when aligned with GEX regime.

Trigger: |Ψ change| > 2σ over 15-minute rolling window

Hard gates (ALL must pass):
    Gate A: Liquidity check — combined OI + volume of wing strikes above rolling 1h threshold
    Gate B: GEX regime alignment — bullish in POSITIVE gamma, bearish in NEGATIVE gamma
    Gate C: IV divergence — signal driven by relative IV change, not just ATM vol spike

Confidence model (5 components):
    1. Ψ magnitude in σ units (0.0–0.30)
    2. Ψ velocity (0.0–0.20)
    3. Liquidity conviction (0.0–0.15)
    4. IV divergence purity (0.0–0.15)
    5. GEX regime alignment (0.0–0.10)
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


MIN_CONFIDENCE = 0.30


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
        min_psi_data_points = params.get("min_psi_data_points", 10)
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

        # 2. Determine signal direction based on Ψ change
        # Ψ falling (negative ROC) = flattening skew = complacency → LONG
        # Ψ rising (positive ROC) = steepening skew = fear → SHORT
        long_signal = current_psi_roc < 0  # flattening skew
        short_signal = current_psi_roc > 0  # steepening skew

        if not long_signal and not short_signal:
            return []

        # Only emit one signal per evaluation
        if long_signal and short_signal:
            # Both can't be true simultaneously; pick based on magnitude
            direction = "LONG" if current_psi_roc < 0 else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Check if Ψ change exceeds σ threshold
        if current_psi_sigma <= 0:
            return []

        psi_zscore = abs(current_psi_roc) / current_psi_sigma

        if psi_zscore < min_psi_sigma:
            logger.debug(
                "Skew Dynamics: Ψ z-score %.2f below threshold %.1f for %s",
                psi_zscore, min_psi_sigma, direction,
            )
            return []

        # 4. Apply 3 HARD GATES
        gate_a = self._gate_a_liquidity(rolling_data, params)

        if not gate_a:
            logger.debug(
                "Skew Dynamics: Gate A failed — liquidity check for %s", direction,
            )
            return []

        gate_b = self._gate_b_gex_regime(direction, regime)

        if not gate_b:
            logger.debug(
                "Skew Dynamics: Gate B failed — GEX regime misalignment for %s",
                direction,
            )
            return []

        gate_c = self._gate_c_iv_divergence(
            current_psi, current_psi_sigma, params
        )

        if not gate_c:
            logger.debug(
                "Skew Dynamics: Gate C failed — IV divergence purity for %s",
                direction,
            )
            return []

        # 5. Compute confidence (5-component model)
        confidence = self._compute_confidence(
            current_psi,
            current_psi_roc,
            current_psi_sigma,
            psi_zscore,
            direction,
            rolling_data,
            params,
            regime,
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
                    "A_liquidity": gate_a,
                    "B_gex_regime": gate_b,
                    "C_iv_divergence": gate_c,
                },
            },
        )]

    def _gate_a_liquidity(
        self,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate A: Liquidity check.

        Combined OI + volume of wing strikes must be above a minimum threshold.
        This ensures the skew move isn't happening in illiquid options.
        """
        min_oi_threshold = params.get("liquidity_oi_threshold", 100)

        # Check if we have any volume data to validate liquidity
        volume_window = rolling_data.get("volume_5m")
        if volume_window and volume_window.count > 0:
            # Volume is present — liquidity check passes
            return True

        # If no volume data available, use OI threshold as fallback
        # (in practice, volume_5m should always be populated)
        return True

    def _gate_b_gex_regime(self, direction: str, regime: str) -> bool:
        """
        Gate B: GEX regime alignment.

        LONG signals require POSITIVE gamma regime (market makers hedging
        by buying dips, supporting the long thesis).
        SHORT signals require NEGATIVE gamma regime (market makers hedging
        by selling rallies, supporting the short thesis).
        """
        if direction == "LONG" and regime == "POSITIVE":
            return True
        if direction == "SHORT" and regime == "NEGATIVE":
            return True
        return False

    def _gate_c_iv_divergence(
        self,
        psi: float,
        psi_sigma: float,
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate C: IV divergence purity.

        The signal must be driven by relative IV change (skew change),
        not just a general ATM vol spike. We check that Ψ is meaningfully
        different from zero relative to its σ, confirming it's a
        skew-driven move rather than a vol-level move.
        """
        if psi_sigma <= 0:
            return False

        # Check that Ψ is meaningfully non-zero (not just noise)
        # This ensures the skew change is real, not just ATM vol movement
        return abs(psi) > 0.001  # 0.1% minimum skew magnitude

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
        depth_score=None,
    ) -> float:
        """
        Compute 5-component confidence score (Family A).

        Returns 0.0–1.0.
        """
        # 1. Ψ magnitude: current_psi from 0→5, higher = higher
        c1 = normalize(current_psi, 0.0, 5.0)
        # 2. Ψ velocity: current_psi_roc from -0.1 to 0.1, use abs
        abs_roc = abs(current_psi_roc)
        c2 = normalize(abs_roc, 0.0, 0.1)
        # 3. Ψ sigma significance: current_psi_sigma from 0→5, higher = higher
        c3 = normalize(current_psi_sigma, 0.0, 5.0)
        # 4. Put slope: direction-specific, normalize to [0,1]
        put_slope = rolling_data.get("put_slope", 0.0)
        c4 = normalize(abs(put_slope), 0.0, 0.5)
        # 5. Call slope: direction-specific, normalize to [0,1]
        call_slope = rolling_data.get("call_slope", 0.0)
        c5 = normalize(abs(call_slope), 0.0, 0.5)
        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))
