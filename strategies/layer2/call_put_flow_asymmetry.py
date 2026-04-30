"""
strategies/layer2/call_put_flow_asymmetry.py — Call/Put Flow Asymmetry

Real-time call vs put flow bias detection. Measures the asymmetric
pressure between call and put buying/selling through a composite
flow score that weights volume, gamma, and delta.

Logic:
    FlowScore = (Call_Vol × Call_Gamma × Call_Delta) / (Put_Vol × Put_Gamma × Put_Delta)

    LONG when Call Score >> Put Score + call IV < put IV (calls undervalued)
    SHORT when Put Score >> Call Score + put IV < call IV (puts undervalued)

Confidence factors:
    - Flow score magnitude (larger asymmetry = stronger signal)
    - IV skew alignment (IV should favor the direction)
    - Volume dominance (VolumeUp on the dominant side)
    - Bid/ask size ratio (larger bid side = conviction)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.CallPutFlowAsymmetry")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Flow score threshold: call score must exceed put score by this ratio
FLOW_THRESHOLD = 1.5                # Call Score > 1.5× Put Score

# Minimum greeks data points for aggregation
MIN_GREEKS_POINTS = 3

# IV skew threshold: call IV must be below put IV by this amount
IV_SKEW_THRESHOLD = 0.03            # 3% IV difference

# Minimum confidence to emit
MIN_CONFIDENCE = 0.35

# Stop and target
STOP_PCT = 0.006                    # 0.6% stop
TARGET_RISK_MULT = 2.0              # 2× risk target


class CallPutFlowAsymmetry(BaseStrategy):
    """
    Detects real-time call vs put flow imbalance.

    When call flow significantly outweighs put flow (or vice versa),
    it signals directional conviction from market participants.
    Combined with IV skew analysis, this reveals smart money positioning.
    """

    strategy_id = "call_put_flow_asymmetry"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for flow asymmetry.

        Returns empty list when no significant asymmetry detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")

        # Calculate aggregated call and put flow scores
        call_score, put_score = self._calculate_flow_scores(gex_calc)

        if call_score is None or put_score is None:
            return []

        # Calculate flow ratio
        if put_score == 0:
            flow_ratio = float("inf") if call_score > 0 else 0
        else:
            flow_ratio = call_score / put_score

        # Determine dominant side
        if flow_ratio >= FLOW_THRESHOLD:
            # Call dominant → LONG
            return self._evaluate_call_dominant(
                call_score, put_score, flow_ratio,
                underlying_price, gex_calc, rolling_data,
                net_gamma, regime,
            )
        elif flow_ratio <= 1.0 / FLOW_THRESHOLD:
            # Put dominant → SHORT
            return self._evaluate_put_dominant(
                call_score, put_score, flow_ratio,
                underlying_price, gex_calc, rolling_data,
                net_gamma, regime,
            )

        return []

    def _calculate_flow_scores(
        self,
        gex_calc: Any,
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Calculate composite flow scores for calls and puts.

        Uses aggregated greeks summary: FlowScore = Σ(OI × Gamma × |Delta|)
        across all strikes.

        Returns (call_score, put_score) or (None, None) if insufficient data.
        """
        summary = gex_calc.get_greeks_summary()
        if not summary:
            return None, None

        total_call_score = 0.0
        total_put_score = 0.0
        call_points = 0
        put_points = 0

        for strike_data in summary.values():
            # Calls: use call_gamma_oi as proxy for volume
            call_oi = strike_data.get("call_oi", 0)
            call_gamma = strike_data.get("call_gamma", 0)
            call_delta = abs(strike_data.get("call_delta_sum", 0))
            if call_oi > 0 and call_gamma > 0 and call_delta > 0.01:
                total_call_score += call_oi * call_gamma * call_delta
                call_points += 1

            # Puts
            put_oi = strike_data.get("put_oi", 0)
            put_gamma = strike_data.get("put_gamma", 0)
            put_delta = abs(strike_data.get("put_delta_sum", 0))
            if put_oi > 0 and put_gamma > 0 and put_delta > 0.01:
                total_put_score += put_oi * put_gamma * put_delta
                put_points += 1

        if call_points < MIN_GREEKS_POINTS or put_points < MIN_GREEKS_POINTS:
            return None, None

        return total_call_score, total_put_score

    def _evaluate_call_dominant(
        self,
        call_score: float,
        put_score: float,
        flow_ratio: float,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
    ) -> List[Signal]:
        """Evaluate call-dominant flow for LONG signal."""
        # Check IV skew: call IV should be lower than put IV
        iv_skew = gex_calc.get_iv_skew()

        # For call-dominant, we want call IV < put IV (iv_skew > 0)
        iv_aligned = iv_skew > IV_SKEW_THRESHOLD if iv_skew is not None else False

        # Check volume dominance
        vol_up = self._check_volume_up(rolling_data)

        confidence = self._compute_confidence(
            flow_ratio, iv_aligned, vol_up, net_gamma, regime,
        )
        if confidence < MIN_CONFIDENCE:
            return []

        # Build signal
        entry = price
        stop = entry * (1 - STOP_PCT)
        risk = entry - stop
        target = entry + (risk * TARGET_RISK_MULT)

        return [Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Call flow dominant (ratio={flow_ratio:.1f}×): "
                f"call score {call_score:.0f} vs put {put_score:.0f}"
                f"{' + IV skew favors calls' if iv_aligned else ''}"
            ),
            metadata={
                "call_flow_score": round(call_score, 2),
                "put_flow_score": round(put_score, 2),
                "flow_ratio": round(flow_ratio, 3),
                "iv_skew": round(iv_skew, 4) if iv_skew is not None else None,
                "iv_aligned": iv_aligned,
                "volume_up": vol_up,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round((target - entry) / risk, 2) if risk > 0 else 0,
            },
        )]

    def _evaluate_put_dominant(
        self,
        call_score: float,
        put_score: float,
        flow_ratio: float,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
    ) -> List[Signal]:
        """Evaluate put-dominant flow for SHORT signal."""
        # Check IV skew: put IV should be lower than call IV
        iv_skew = gex_calc.get_iv_skew()

        # For put-dominant, we want put IV < call IV (iv_skew < 0)
        iv_aligned = iv_skew < -IV_SKEW_THRESHOLD if iv_skew is not None else False

        # Check volume down (volume spike on selling)
        vol_down = self._check_volume_down(rolling_data)

        confidence = self._compute_confidence(
            1.0 / flow_ratio if flow_ratio > 0 else float("inf"),
            iv_aligned, vol_down, net_gamma, regime,
        )
        if confidence < MIN_CONFIDENCE:
            return []

        # Build signal
        entry = price
        stop = entry * (1 + STOP_PCT)
        risk = stop - entry
        target = entry - (risk * TARGET_RISK_MULT)

        return [Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Put flow dominant (ratio={flow_ratio:.2f}×): "
                f"put score {put_score:.0f} vs call {call_score:.0f}"
                f"{' + IV skew favors puts' if iv_aligned else ''}"
            ),
            metadata={
                "call_flow_score": round(call_score, 2),
                "put_flow_score": round(put_score, 2),
                "flow_ratio": round(flow_ratio, 3),
                "iv_skew": round(iv_skew, 4) if iv_skew is not None else None,
                "iv_aligned": iv_aligned,
                "volume_down": vol_down,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
            },
        )]

    def _check_volume_up(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if volume is trending up."""
        window = rolling_data.get("volume_5m")
        if window is None or window.count < 3:
            return False
        return window.trend == "UP"

    def _check_volume_down(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if volume is trending down."""
        window = rolling_data.get("volume_5m")
        if window is None or window.count < 3:
            return False
        return window.trend == "DOWN"

    def _compute_confidence(
        self,
        flow_ratio: float,
        iv_aligned: bool,
        vol_aligned: bool,
        net_gamma: float,
        regime: str,
    ) -> float:
        """
        Combine flow asymmetry factors into confidence.

        Returns 0.0–1.0.
        """
        # 1. Flow ratio magnitude (0.25–0.35)
        # Higher ratio = stronger asymmetry
        log_ratio = min(flow_ratio, 10.0)  # Cap for normalization
        ratio_conf = 0.25 + 0.10 * min(1.0, (log_ratio - 1.5) / 8.5)

        # 2. IV skew alignment (0.15–0.20)
        iv_conf = 0.20 if iv_aligned else 0.05

        # 3. Volume alignment (0.10–0.15)
        vol_conf = 0.15 if vol_aligned else 0.05

        # 4. Regime alignment (0.05–0.10)
        regime_conf = 0.10 if regime == "POSITIVE" else 0.05

        # 5. Net gamma context (0.0–0.05)
        gamma_conf = 0.05 if abs(net_gamma) > 500000 else 0.0

        confidence = ratio_conf + iv_conf + vol_conf + regime_conf + gamma_conf
        return min(1.0, max(0.0, confidence))
