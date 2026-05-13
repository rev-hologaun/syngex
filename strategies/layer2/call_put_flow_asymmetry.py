"""
strategies/layer2/call_put_flow_asymmetry.py — Call/Put Flow Asymmetry v2 (Flow-Velocity)

Real-time call vs put flow bias detection with Flow-Velocity upgrades.

Measures the asymmetric pressure between call and put buying/selling through a
composite flow score that weights volume, gamma, and delta.

v2 Flow-Velocity adds:
    - Flow Acceleration (ROC): Detects when imbalance is SPIKING, not just present
    - Flow Breadth: Ensures flow is broad-based across strikes, not single-strike noise
    - Regime-Adaptive Scaling: Scales confidence by gamma magnitude
    - Wall Proximity Bonus: Bonus when flow occurs near major gamma walls

Logic:
    FlowScore = (Call_Vol × Call_Gamma × Call_Delta) / (Put_Vol × Put_Gamma × Put_Delta)

    LONG when Call Score >> Put Score + call IV < put IV (calls undervalued)
    SHORT when Put Score >> Call Score + put IV < call IV (puts undervalued)

Confidence factors (7 components):
    1. Flow ratio magnitude (0.0–0.15) — larger asymmetry = stronger signal
    2. Flow acceleration (0.0 or 0.20 hard gate) — ratio must be rising/falling fast
    3. Flow breadth (0.0 or 0.15 hard gate) — must be broad-based across strikes
    4. IV skew alignment (0.0–0.15 soft) — IV should favor the direction
    5. Volume alignment (0.0–0.10 soft) — volume dominance on the side
    6. Regime intensity (0.0–0.10 soft) — gamma magnitude scales conviction
    7. Wall proximity bonus (+0.0 to +0.10) — bonus near gamma walls
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_FLOW_RATIO_5M,
    KEY_VOLUME_5M,
    KEY_VOLUME_UP_5M,
    KEY_VOLUME_DOWN_5M,
)

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

# Minimum confidence to emit (v2: raised from 0.35)
MIN_CONFIDENCE = 0.15

# Stop and target
STOP_PCT = 0.006                    # 0.6% stop
TARGET_RISK_MULT = 2.0              # 2× risk target


class CallPutFlowAsymmetry(BaseStrategy):
    """
    Detects real-time call vs put flow imbalance with Flow-Velocity v2.

    When call flow significantly outweighs put flow (or vice versa),
    it signals directional conviction from market participants.
    Combined with IV skew analysis, this reveals smart money positioning.

    v2 Flow-Velocity upgrades:
        - Flow ROC acceleration detects when imbalance is SPIKING
        - Flow breadth ensures broad-based conviction, not single-strike noise
        - Regime-adaptive scaling by gamma magnitude
        - Wall proximity bonus near major gamma walls
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
        greeks_summary = data.get("greeks_summary", {})

        # Calculate aggregated call and put flow scores + breadth metrics
        call_score, put_score, flow_breadth, active_call_strikes, active_put_strikes, total_active_strikes = self._calculate_flow_scores(
            gex_calc, greeks_summary
        )

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
                net_gamma, regime, flow_breadth,
                active_call_strikes, active_put_strikes, total_active_strikes,
            )
        elif flow_ratio <= 1.0 / FLOW_THRESHOLD:
            # Put dominant → SHORT
            return self._evaluate_put_dominant(
                call_score, put_score, flow_ratio,
                underlying_price, gex_calc, rolling_data,
                net_gamma, regime, flow_breadth,
                active_call_strikes, active_put_strikes, total_active_strikes,
            )

        return []

    def _calculate_flow_scores(
        self,
        gex_calc: Any,
        greeks_summary: Dict[str, Any],
    ) -> Tuple[Optional[float], Optional[float], Optional[float], int, int, int]:
        """
        Calculate composite flow scores for calls and puts.

        Uses aggregated greeks summary: FlowScore = Σ(OI × Gamma × |Delta|)
        across all strikes.

        Also computes flow breadth metrics:
            - active_strikes: strikes with OI > 0 AND gamma > 0
            - total_strikes: strikes with any OI > 0

        Returns (call_score, put_score, flow_breadth, active_call_strikes,
                 active_put_strikes, total_active_strikes) or (None, None, None, 0, 0, 0)
        if insufficient data.
        """
        if not greeks_summary:
            return None, None, None, 0, 0, 0

        total_call_score = 0.0
        total_put_score = 0.0
        call_points = 0
        put_points = 0
        active_call_strikes = 0
        active_put_strikes = 0
        total_active_strikes = 0

        for strike_str, strike_data in greeks_summary.items():
            # Calls: use call_gamma_oi as proxy for volume
            call_oi = strike_data.get("call_oi", 0)
            call_gamma = strike_data.get("call_gamma", 0)
            call_delta = abs(strike_data.get("call_delta_sum", 0))
            if call_oi > 0 and call_gamma > 0 and call_delta > 0.01:
                total_call_score += call_oi * call_gamma * call_delta
                call_points += 1
                active_call_strikes += 1

            # Puts
            put_oi = strike_data.get("put_oi", 0)
            put_gamma = strike_data.get("put_gamma", 0)
            put_delta = abs(strike_data.get("put_delta_sum", 0))
            if put_oi > 0 and put_gamma > 0 and put_delta > 0.01:
                total_put_score += put_oi * put_gamma * put_delta
                put_points += 1
                active_put_strikes += 1

            # Track total active strikes (any OI > 0)
            if call_oi > 0 or put_oi > 0:
                total_active_strikes += 1

        if call_points < MIN_GREEKS_POINTS or put_points < MIN_GREEKS_POINTS:
            return None, None, None, 0, 0, 0

        # Compute flow breadth
        flow_breadth = None
        if total_active_strikes > 0:
            flow_breadth = (active_call_strikes + active_put_strikes) / total_active_strikes

        return total_call_score, total_put_score, flow_breadth, active_call_strikes, active_put_strikes, total_active_strikes

    def _check_flow_acceleration(
        self,
        rolling_data: Dict[str, Any],
        flow_ratio: float,
        direction: str,
    ) -> bool:
        """
        Check if flow ratio is accelerating (rate-of-change detection).

        Reads KEY_FLOW_RATIO_5M rolling window and computes ROC over
        the last 5 data points.

        For call-dominant (LONG): ROC > 0.20 (ratio rising ≥20%)
        For put-dominant (SHORT): ROC < -0.20 (ratio falling ≥20%)

        Returns True if acceleration gate passes, False otherwise.
        """
        window = rolling_data.get(KEY_FLOW_RATIO_5M)
        if window is None or window.count < 5:
            return False

        try:
            values = window.values
            if len(values) < 5:
                return False

            current = values[-1]
            value_5_ago = values[-5]

            if value_5_ago == 0:
                return False

            flow_roc = (current - value_5_ago) / value_5_ago

            if direction == "LONG":
                # Call-dominant: ratio should be rising
                return flow_roc > 0.20
            else:
                # Put-dominant: ratio should be falling
                return flow_roc < -0.20
        except (IndexError, TypeError):
            return False

    def _check_flow_breadth(
        self,
        flow_breadth: Optional[float],
    ) -> bool:
        """
        Check if flow is broad-based across strikes.

        Hard gate: breadth > 0.30 (at least 30% of strikes participating)

        Returns True if breadth gate passes, False otherwise.
        """
        if flow_breadth is None:
            return False
        return flow_breadth > 0.30

    def _compute_regime_intensity(self, net_gamma: float) -> float:
        """
        Compute regime intensity multiplier based on net gamma magnitude.

        abs(net_gamma) < 200000 → 0.8  (low gamma = less conviction)
        abs(net_gamma) > 500000 → 1.3  (high gamma = explosive)
        otherwise → 1.0  (baseline)
        """
        abs_gamma = abs(net_gamma)
        if abs_gamma < 200000:
            return 0.8
        elif abs_gamma > 500000:
            return 1.3
        return 1.0

    def _check_wall_proximity(
        self,
        gex_calc: Any,
        price: float,
        direction: str,
    ) -> Tuple[float, float, str]:
        """
        Check proximity to gamma walls and return bonus + metadata.

        Gets gamma walls via gex_calc.get_gamma_walls(threshold=500_000).
        For call-dominant: checks nearest call wall above price.
        For put-dominant: checks nearest put wall below price.
        If distance < 0.5% of price → returns bonus.

        Returns (bonus, distance_pct, nearest_wall_type).
        """
        try:
            walls = gex_calc.get_gamma_walls(threshold=500_000)
            if not walls:
                return 0.0, 0.0, ""

            nearest_wall = None
            min_dist = float("inf")

            for wall in walls:
                wall_side = wall.get("side", "").upper()
                wall_strike = wall.get("strike", 0)

                if direction == "LONG" and wall_side == "CALL":
                    # Call-dominant: look for call wall ABOVE price
                    if wall_strike > price:
                        dist = abs(wall_strike - price) / price
                        if dist < min_dist:
                            min_dist = dist
                            nearest_wall = wall
                elif direction == "SHORT" and wall_side == "PUT":
                    # Put-dominant: look for put wall BELOW price
                    if wall_strike < price:
                        dist = abs(wall_strike - price) / price
                        if dist < min_dist:
                            min_dist = dist
                            nearest_wall = wall

            if nearest_wall is None:
                return 0.0, 0.0, ""

            wall_type = nearest_wall.get("side", "").lower()
            wall_dist_pct = min_dist

            # Within 0.5% proximity → bonus
            if wall_dist_pct < 0.005:
                return 0.10, wall_dist_pct, wall_type

            return 0.0, wall_dist_pct, wall_type
        except Exception:
            return 0.0, 0.0, ""

    def _compute_confidence(
        self,
        flow_ratio: float,
        flow_roc: bool,
        flow_breadth: bool,
        iv_aligned: bool,
        vol_aligned: bool,
        net_gamma: float,
        regime: str,
        direction: str,
        gex_calc: Any,
        price: float,
    ) -> float:
        """
        Combine flow asymmetry factors into confidence (v2 Flow-Velocity).

        7 components:
            1. Flow ratio magnitude: 0.0–0.15 (soft)
            2. Flow acceleration: 0.0 or 0.20 (hard gate)
            3. Flow breadth: 0.0 or 0.15 (hard gate)
            4. IV skew alignment: 0.0–0.15 (soft)
            5. Volume alignment: 0.0–0.10 (soft)
            6. Regime intensity: 0.0–0.10 (soft)
            7. Wall proximity bonus: +0.0 to +0.10 (bonus)

        Returns 0.0–1.0.
        """
        # 1. Flow ratio magnitude (0.0–0.15)
        ratio_conf = self._ratio_confidence(flow_ratio)

        # 2. Flow acceleration (hard gate — 0.0 or 0.20)
        accel_conf = 0.20 if flow_roc else 0.0

        # 3. Flow breadth (hard gate — 0.0 or 0.15)
        breadth_conf = 0.15 if flow_breadth else 0.0

        # 4. IV skew alignment (soft — 0.0–0.15)
        iv_conf = 0.15 if iv_aligned else 0.0

        # 5. Volume alignment (soft — 0.0–0.10)
        vol_conf = 0.10 if vol_aligned else 0.0

        # 6. Regime intensity (soft — 0.0–0.10)
        regime_mult = self._compute_regime_intensity(net_gamma)
        regime_conf = 0.025 + 0.075 * (regime_mult - 0.8) / (1.3 - 0.8)

        confidence = ratio_conf + accel_conf + breadth_conf + iv_conf + vol_conf + regime_conf

        # 7. Wall proximity bonus (+0.0 to +0.10)
        wall_bonus, wall_dist_pct, wall_type = self._check_wall_proximity(
            gex_calc, price, direction
        )
        confidence += wall_bonus

        return min(1.0, max(0.0, confidence))

    def _ratio_confidence(self, flow_ratio: float) -> float:
        """
        Compute confidence component from flow ratio magnitude.

        Uses logarithmic scaling:
            ratio = threshold → 0.0
            ratio = 10.0 → 0.15

        Handles both call-dominant (ratio > 1) and put-dominant cases.
        """
        # Normalize: for put-dominant, invert the ratio
        if flow_ratio < 1.0:
            normalized = 1.0 / flow_ratio if flow_ratio > 0 else 10.0
        else:
            normalized = flow_ratio

        # Logarithmic scaling from threshold to 10.0
        log_ratio = min(normalized, 10.0)
        return 0.15 * min(1.0, (log_ratio - FLOW_THRESHOLD) / (10.0 - FLOW_THRESHOLD))

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
        flow_breadth: Optional[float],
        active_call_strikes: int,
        active_put_strikes: int,
        total_active_strikes: int,
    ) -> List[Signal]:
        """Evaluate call-dominant flow for LONG signal."""
        # Check IV skew: call IV should be lower than put IV
        iv_skew = gex_calc.get_iv_skew()

        # For call-dominant, we want call IV < put IV (iv_skew > 0)
        iv_aligned = iv_skew > IV_SKEW_THRESHOLD if iv_skew is not None else False

        # Check volume dominance
        vol_up = self._check_volume_up(rolling_data)

        # Flow acceleration hard gate
        flow_roc = self._check_flow_acceleration(rolling_data, flow_ratio, "LONG")

        # Flow breadth hard gate
        breadth_pass = self._check_flow_breadth(flow_breadth)

        if not flow_roc or not breadth_pass:
            return []

        confidence = self._compute_confidence(
            flow_ratio, flow_roc, breadth_pass,
            iv_aligned, vol_up, net_gamma, regime, "LONG",
            gex_calc, price,
        )
        if confidence < MIN_CONFIDENCE:
            return []

        # Compute metadata values
        wall_bonus, wall_dist_pct, wall_type = self._check_wall_proximity(
            gex_calc, price, "LONG"
        )
        regime_mult = self._compute_regime_intensity(net_gamma)

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
                # === v1 fields (kept) ===
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

                # === v2 new fields ===
                "flow_roc": round((flow_ratio - self._get_flow_ratio_5_ago(rolling_data)) / max(self._get_flow_ratio_5_ago(rolling_data), 0.001), 4) if self._has_flow_history(rolling_data) else None,
                "flow_roc_window": 5,
                "flow_breadth": round(flow_breadth, 3) if flow_breadth is not None else None,
                "active_call_strikes": active_call_strikes,
                "active_put_strikes": active_put_strikes,
                "total_active_strikes": total_active_strikes,
                "gamma_intensity": round(abs(net_gamma) / 1_000_000, 3),
                "regime_mult": round(regime_mult, 2),
                "wall_proximity_pct": round(wall_dist_pct, 4),
                "nearest_wall_type": wall_type if wall_type else None,
                "wall_proximity_bonus": wall_bonus,
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
        flow_breadth: Optional[float],
        active_call_strikes: int,
        active_put_strikes: int,
        total_active_strikes: int,
    ) -> List[Signal]:
        """Evaluate put-dominant flow for SHORT signal."""
        # Check IV skew: put IV should be lower than call IV
        iv_skew = gex_calc.get_iv_skew()

        # For put-dominant, we want put IV < call IV (iv_skew > 0 means call IV > put IV)
        iv_aligned = iv_skew > IV_SKEW_THRESHOLD if iv_skew is not None else False

        # Check volume down (volume spike on selling)
        vol_down = self._check_volume_down(rolling_data)

        # Flow acceleration hard gate
        flow_roc = self._check_flow_acceleration(rolling_data, flow_ratio, "SHORT")

        # Flow breadth hard gate
        breadth_pass = self._check_flow_breadth(flow_breadth)

        if not flow_roc or not breadth_pass:
            return []

        confidence = self._compute_confidence(
            flow_ratio, flow_roc, breadth_pass,
            iv_aligned, vol_down, net_gamma, regime, "SHORT",
            gex_calc, price,
        )
        if confidence < MIN_CONFIDENCE:
            return []

        # Compute metadata values
        wall_bonus, wall_dist_pct, wall_type = self._check_wall_proximity(
            gex_calc, price, "SHORT"
        )
        regime_mult = self._compute_regime_intensity(net_gamma)

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
                # === v1 fields (kept) ===
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

                # === v2 new fields ===
                "flow_roc": round((flow_ratio - self._get_flow_ratio_5_ago(rolling_data)) / max(self._get_flow_ratio_5_ago(rolling_data), 0.001), 4) if self._has_flow_history(rolling_data) else None,
                "flow_roc_window": 5,
                "flow_breadth": round(flow_breadth, 3) if flow_breadth is not None else None,
                "active_call_strikes": active_call_strikes,
                "active_put_strikes": active_put_strikes,
                "total_active_strikes": total_active_strikes,
                "gamma_intensity": round(abs(net_gamma) / 1_000_000, 3),
                "regime_mult": round(regime_mult, 2),
                "wall_proximity_pct": round(wall_dist_pct, 4),
                "nearest_wall_type": wall_type if wall_type else None,
                "wall_proximity_bonus": wall_bonus,
            },
        )]

    def _check_volume_up(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if call volume is trending up."""
        window = rolling_data.get(KEY_VOLUME_UP_5M)
        if window is None or window.count < 3:
            return False
        return window.trend == "UP"

    def _check_volume_down(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if put volume is trending down."""
        window = rolling_data.get(KEY_VOLUME_DOWN_5M)
        if window is None or window.count < 3:
            return False
        return window.trend == "DOWN"

    def _has_flow_history(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if flow ratio rolling window has enough history."""
        window = rolling_data.get(KEY_FLOW_RATIO_5M)
        return window is not None and window.count >= 5

    def _get_flow_ratio_5_ago(self, rolling_data: Dict[str, Any]) -> float:
        """Get flow ratio value from 5 data points ago."""
        window = rolling_data.get(KEY_FLOW_RATIO_5M)
        if window is None or window.count < 5:
            return 0.0
        values = window.values
        if len(values) < 5:
            return 0.0
        return values[-5]
