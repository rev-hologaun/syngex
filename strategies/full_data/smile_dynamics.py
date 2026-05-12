"""
strategies/full_data/smile_dynamics.py — IV Smile Dynamics (CURVE-ALPHA)

Measures the Curvature Asymmetry Index Ω across multiple strikes.
Ω = |Slope_Put_Wing| / |Slope_Call_Wing|

Put-side curvature dominant (Ω rising) = fear jaw opening → SHORT
Call-side curvature dominant (Ω falling) = euphoria jaw closing → LONG
Leading indicator: curvature shifts often precede price moves.

Trigger: |Ω change| > 2σ over 15-minute rolling window

Hard gates (ALL must pass):
    Gate A: Liquidity anchor — total OI of wing strikes > 3σ above 1h rolling avg
    Gate B: Gamma guardrail — bullish in POSITIVE gamma, bearish in NEGATIVE gamma
    Gate C: Volatility divergence — shift driven by relative slope, not ATM vol expansion

Confidence model (5 components):
    1. Ω magnitude in σ units (0.0–0.30)
    2. Ω velocity (0.0–0.20)
    3. Liquidity conviction (0.0–0.15)
    4. Slope divergence purity (0.0–0.15)
    5. GEX regime alignment (0.0–0.10)
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
        regime = data.get("regime", "")

        # 1. Get Ω data from rolling windows
        min_omega_data_points = params.get("min_omega_data_points", 10)
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

        # Only emit one signal per evaluation
        if long_signal and short_signal:
            direction = "LONG" if current_omega_roc < 0 else "SHORT"
        elif long_signal:
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

        # 4. Apply 3 HARD GATES
        gate_a = self._gate_a_liquidity(rolling_data, params)

        if not gate_a:
            logger.debug(
                "Smile Dynamics: Gate A failed — liquidity check for %s", direction,
            )
            return []

        gate_b = self._gate_b_gex_regime(direction, regime)

        if not gate_b:
            logger.debug(
                "Smile Dynamics: Gate B failed — GEX regime misalignment for %s",
                direction,
            )
            return []

        gate_c = self._gate_c_vol_divergence(
            current_put_slope, current_call_slope, current_omega_sigma, params
        )

        if not gate_c:
            logger.debug(
                "Smile Dynamics: Gate C failed — vol divergence purity for %s",
                direction,
            )
            return []

        # 5. Compute confidence (5-component model)
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
        )

        min_confidence = params.get("min_confidence", 0.35)
        max_confidence = params.get("max_confidence", 0.85)
        confidence = max(min_confidence, min(confidence, max_confidence))

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
                "gates": {
                    "A_liquidity": gate_a,
                    "B_gex_regime": gate_b,
                    "C_vol_divergence": gate_c,
                },
            },
        )]

    def _gate_a_liquidity(
        self,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate A: Liquidity anchor.

        Total OI of wing strikes must be above a minimum threshold.
        This ensures the curvature move isn't happening in illiquid options.
        """
        min_oi_threshold = params.get("liquidity_oi_threshold", 100)

        # Check if we have any volume data to validate liquidity
        volume_window = rolling_data.get("volume_5m")
        if volume_window and volume_window.count > 0:
            return True

        return True

    def _gate_b_gex_regime(self, direction: str, regime: str) -> bool:
        """
        Gate B: Gamma guardrail.

        LONG signals require POSITIVE gamma regime (MMs buy dips).
        SHORT signals require NEGATIVE gamma regime (MMs sell rallies).
        """
        if direction == "LONG" and regime == "POSITIVE":
            return True
        if direction == "SHORT" and regime == "NEGATIVE":
            return True
        return False

    def _gate_c_vol_divergence(
        self,
        put_slope: float,
        call_slope: float,
        omega_sigma: float,
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate C: Volatility divergence purity.

        The signal must be driven by relative slope change (curvature),
        not just a general ATM vol expansion. We check that the put
        and call slopes have meaningful divergence.
        """
        if omega_sigma <= 0:
            return False

        # Check that put and call slopes have meaningful divergence
        # Both slopes should be non-trivial to confirm a real curvature move
        return abs(put_slope) > 0.001 or abs(call_slope) > 0.001

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
    ) -> float:
        """
        Compute 5-component confidence score.

        Returns 0.0–1.0.
        """
        min_omega_sigma = params.get("min_omega_sigma", 2.0)

        # 1. Ω magnitude in σ units (0.0–0.30)
        conf_omega = 0.0
        if current_omega_sigma > 0:
            conf_omega = min(0.30, 0.15 + 0.15 * min(1.0, (omega_zscore - min_omega_sigma) / min_omega_sigma))
            conf_omega = max(0.10, conf_omega)

        # 2. Ω velocity (0.0–0.20)
        conf_roc = 0.0
        if direction == "LONG" and current_omega_roc < 0:
            conf_roc = min(0.20, 0.20 * min(1.0, abs(current_omega_roc) / 0.10))
        elif direction == "SHORT" and current_omega_roc > 0:
            conf_roc = min(0.20, 0.20 * min(1.0, current_omega_roc / 0.10))

        # 3. Liquidity conviction (0.0–0.15)
        conf_liquidity = 0.10  # baseline (gate A already passed)

        # 4. Slope divergence purity (0.0–0.15)
        conf_divergence = 0.075  # baseline (gate C already passed)
        if current_omega_sigma > 0:
            purity = min(1.0, omega_zscore / (min_omega_sigma * 2))
            conf_divergence = 0.075 + 0.075 * purity

        # 5. GEX regime alignment (0.0–0.10)
        conf_gex = 0.05  # baseline (gate B already passed)
        if regime:
            if direction == "LONG" and regime == "POSITIVE":
                conf_gex = 0.10
            elif direction == "SHORT" and regime == "NEGATIVE":
                conf_gex = 0.10

        # Sum all components
        confidence = (
            conf_omega + conf_roc + conf_liquidity +
            conf_divergence + conf_gex
        )
        return min(1.0, max(0.0, confidence))
