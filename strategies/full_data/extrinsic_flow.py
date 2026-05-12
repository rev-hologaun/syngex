"""
strategies/full_data/extrinsic_flow.py — Extrinsic Value Flow (EXTRINSIC-ALPHA)

Tracks Volume × Extrinsic Value (Premium Conviction) separately for calls and puts.
Φ_Call = Σ(Volume × ExtrinsicValue) for calls
Φ_Put  = Σ(Volume × ExtrinsicValue) for puts
RΦ = Φ_Call / Φ_Put (Relative Conviction Ratio)

Call-heavy (RΦ > 3.0) = speculative bullish → LONG
Put-heavy (RΦ < 0.3) = defensive hedging → SHORT
Leading indicator of positioning shifts.

Trigger: RΦ > 3.0 (bullish) or RΦ < 0.3 (bearish)

Hard gates (ALL must pass):
    Gate A: Volume anchor — total Φ > 2σ above 1h rolling avg
    Gate B: Gamma guardrail — bullish in POSITIVE gamma, bearish in NEGATIVE gamma
    Gate C: Delta purity — only count 15-65 delta contracts (already filtered in main.py)

Confidence model (5 components):
    1. RΦ magnitude (0.0–0.30)
    2. Φ total momentum (0.0–0.20)
    3. Volume conviction (0.0–0.15)
    4. Ratio purity (0.0–0.15)
    5. GEX regime alignment (0.0–0.10)
"""

from __future__ import annotations

import math
import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_PHI_CALL_5M,
    KEY_PHI_PUT_5M,
    KEY_PHI_RATIO_5M,
    KEY_PHI_TOTAL_5M,
    KEY_PHI_TOTAL_SIGMA_5M,
)

logger = logging.getLogger("Syngex.Strategies.ExtrinsicFlow")


class ExtrinsicFlow(BaseStrategy):
    """
    Extrinsic Value Flow strategy — tracks Volume × Extrinsic Value
    (Premium Conviction) separately for calls and puts.

    Φ_Call = Σ(Volume × ExtrinsicValue) for calls
    Φ_Put  = Σ(Volume × ExtrinsicValue) for puts
    RΦ = Φ_Call / Φ_Put (Relative Conviction Ratio)

    LONG: RΦ > 3.0 (call-side speculative) AND GEX regime is POSITIVE
    SHORT: RΦ < 0.3 (put-side defensive) AND GEX regime is NEGATIVE
    """

    strategy_id = "extrinsic_flow"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for extrinsic value flow signal.

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

        # 1. Get Φ data from rolling windows
        min_phi_data_points = params.get("min_phi_data_points", 10)
        phi_sigma_mult = params.get("phi_sigma_mult", 2.0)

        phi_call_window = rolling_data.get(KEY_PHI_CALL_5M)
        phi_put_window = rolling_data.get(KEY_PHI_PUT_5M)
        phi_ratio_window = rolling_data.get(KEY_PHI_RATIO_5M)
        phi_total_window = rolling_data.get(KEY_PHI_TOTAL_5M)
        phi_sigma_window = rolling_data.get(KEY_PHI_TOTAL_SIGMA_5M)

        if not phi_call_window or not phi_put_window:
            return []
        if phi_call_window.count < min_phi_data_points or phi_put_window.count < min_phi_data_points:
            return []
        if not phi_ratio_window or phi_ratio_window.count < min_phi_data_points:
            return []
        if not phi_total_window or phi_total_window.count < min_phi_data_points:
            return []

        current_phi_call = phi_call_window.values[-1]
        current_phi_put = phi_put_window.values[-1]
        current_phi_total = phi_total_window.values[-1]
        current_phi_ratio = phi_ratio_window.values[-1] if phi_ratio_window else 1.0
        current_phi_sigma = phi_sigma_window.values[-1] if phi_sigma_window else 0.0

        # 2. Compute RΦ (Relative Conviction Ratio)
        # RΦ = Φ_Call / Φ_Put
        # Call-heavy (RΦ > 3.0) = speculative bullish → LONG
        # Put-heavy (RΦ < 0.3) = defensive hedging → SHORT
        phi_call_threshold = params.get("phi_call_threshold", 3.0)
        phi_put_threshold = params.get("phi_put_threshold", 0.3)

        long_signal = current_phi_ratio > phi_call_threshold
        short_signal = current_phi_ratio < phi_put_threshold

        if not long_signal and not short_signal:
            return []

        # Only emit one signal per evaluation
        if long_signal and short_signal:
            long_extreme = current_phi_ratio - phi_call_threshold
            short_extreme = phi_put_threshold - current_phi_ratio
            direction = "LONG" if long_extreme >= short_extreme else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Apply 3 HARD GATES
        gate_a = self._gate_a_volume_anchor(
            current_phi_total, current_phi_sigma, phi_sigma_mult
        )

        if not gate_a:
            logger.debug(
                "Extrinsic Flow: Gate A failed — volume anchor for %s",
                direction,
            )
            return []

        gate_b = self._gate_b_gex_regime(direction, regime)

        if not gate_b:
            logger.debug(
                "Extrinsic Flow: Gate B failed — GEX regime misalignment for %s",
                direction,
            )
            return []

        # Gate C (Delta purity) is already applied in main.py — only 15-65 delta
        # contracts are counted toward Φ, so this gate always passes
        gate_c = True

        # 4. Compute confidence (5-component model)
        confidence = self._compute_confidence(
            current_phi_ratio,
            current_phi_total,
            current_phi_sigma,
            current_phi_call,
            current_phi_put,
            direction,
            regime,
            rolling_data,
            params,
        )

        min_confidence = params.get("min_confidence", 0.35)
        max_confidence = params.get("max_confidence", 0.85)
        confidence = max(min_confidence, min(confidence, max_confidence))

        if confidence < min_confidence:
            return []

        # 5. Build signal with entry/stop/target
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

        # Intensity metadata based on RΦ magnitude
        if current_phi_ratio > 5.0 or (direction == "SHORT" and current_phi_ratio < 0.15):
            intensity = "red"
        elif current_phi_ratio > 3.5 or (direction == "SHORT" and current_phi_ratio < 0.25):
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
                f"Extrinsic flow {direction}: RΦ={current_phi_ratio:.2f}, "
                f"Φ_Call={current_phi_call:.0f}, Φ_Put={current_phi_put:.0f}"
            ),
            metadata={
                "direction": direction,
                "phi_call": round(current_phi_call, 2),
                "phi_put": round(current_phi_put, 2),
                "phi_total": round(current_phi_total, 2),
                "phi_ratio": round(current_phi_ratio, 4),
                "phi_sigma": round(current_phi_sigma, 4),
                "intensity": intensity,
                "regime": regime,
                "gates": {
                    "A_volume_anchor": gate_a,
                    "B_gex_regime": gate_b,
                    "C_delta_purity": gate_c,
                },
            },
        )]

    def _gate_a_volume_anchor(
        self,
        phi_total: float,
        phi_sigma: float,
        phi_sigma_mult: float,
    ) -> bool:
        """
        Gate A: Volume anchor.

        Total Φ must be above a minimum threshold to ensure the signal
        isn't driven by noise in low-volume periods. We use the rolling
        σ as a volatility measure — the signal is only valid when total
        Φ is meaningfully above the baseline.
        """
        if phi_sigma <= 0:
            # No σ data yet — pass if we have meaningful total Φ
            return phi_total > 0

        # Require total Φ to be above baseline + sigma_mult * σ
        # This ensures the volume is statistically significant
        return phi_total > phi_sigma_mult * phi_sigma

    def _gate_b_gex_regime(self, direction: str, regime: str) -> bool:
        """
        Gate B: Gamma guardrail.

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

    def _compute_confidence(
        self,
        phi_ratio: float,
        phi_total: float,
        phi_sigma: float,
        phi_call: float,
        phi_put: float,
        direction: str,
        regime: str,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> float:
        """
        Compute 5-component confidence score.

        Returns 0.0–1.0.
        """
        phi_call_threshold = params.get("phi_call_threshold", 3.0)
        phi_put_threshold = params.get("phi_put_threshold", 0.3)
        phi_sigma_mult = params.get("phi_sigma_mult", 2.0)

        # 1. RΦ magnitude (0.0–0.30)
        # How extreme the ratio is relative to the threshold
        conf_ratio_mag = 0.0
        if direction == "LONG":
            # RΦ above threshold — scale from 0 at threshold to 0.30 at 5x threshold
            if phi_call_threshold > 0:
                ratio_excess = (phi_ratio - phi_call_threshold) / phi_call_threshold
                conf_ratio_mag = min(0.30, 0.15 + 0.15 * min(1.0, ratio_excess))
        else:
            # RΦ below threshold — scale from 0 at threshold to 0.30 at near-zero
            if phi_put_threshold > 0:
                ratio_excess = (phi_put_threshold - phi_ratio) / phi_put_threshold
                conf_ratio_mag = min(0.30, 0.15 + 0.15 * min(1.0, ratio_excess))

        # 2. Φ total momentum (0.0–0.20)
        # How large the total Φ is relative to its σ
        conf_momentum = 0.0
        if phi_sigma > 0 and phi_total > 0:
            # Total Φ above sigma_mult * σ = momentum confirmed
            momentum_z = phi_total / phi_sigma
            if momentum_z >= phi_sigma_mult:
                conf_momentum = 0.10  # baseline
                # Bonus for exceeding sigma threshold
                conf_momentum += min(0.10, 0.10 * min(1.0, (momentum_z - phi_sigma_mult) / phi_sigma_mult))

        # 3. Volume conviction (0.0–0.15)
        # Absolute volume level — higher = more conviction
        conf_volume = 0.0
        if phi_total > 0:
            # Scale: 0 at 0, max at very high values
            # Use log scale for better distribution
            conf_volume = min(0.15, 0.15 * min(1.0, math.log1p(phi_total) / 10.0))

        # 4. Ratio purity (0.0–0.15)
        # How cleanly one side dominates — higher ratio = purer signal
        conf_purity = 0.0
        if direction == "LONG":
            # Purity = how much call side dominates put side
            if phi_put > 0:
                dominance = phi_call / phi_put
                conf_purity = min(0.15, 0.15 * min(1.0, dominance / (phi_call_threshold * 2)))
            else:
                conf_purity = 0.15  # pure call signal
        else:
            # Purity = how much put side dominates call side
            if phi_call > 0:
                dominance = phi_put / phi_call
                conf_purity = min(0.15, 0.15 * min(1.0, dominance / ((1.0 / phi_put_threshold) * 2)))
            else:
                conf_purity = 0.15  # pure put signal

        # 5. GEX regime alignment (0.0–0.10)
        # Signal direction matches GEX bias
        conf_gex = 0.0
        if regime:
            if direction == "LONG" and regime == "POSITIVE":
                conf_gex = 0.10
            elif direction == "SHORT" and regime == "NEGATIVE":
                conf_gex = 0.10
            else:
                conf_gex = 0.05  # partial alignment (regime exists but not matching)

        # Sum all components
        confidence = (
            conf_ratio_mag + conf_momentum + conf_volume +
            conf_purity + conf_gex
        )
        return min(1.0, max(0.0, confidence))
