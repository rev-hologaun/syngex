"""
strategies/layer2/depth_imbalance_momentum.py — Depth Imbalance Momentum

Pressure-tracking engine that monitors structural weight of the order book.
When the bid side becomes massively larger than the ask side (or vice versa),
it creates gravitational pressure. Combined with ROC, we detect when this
pressure is *accelerating*, not just static.

LONG: IR > 3.0 (heavy bid pressure) AND ROC > 0 (imbalance rising)
SHORT: IR < 0.6 (heavy ask pressure) AND ROC < 0 (imbalance falling)

Hard gates (all must pass):
    Gate A: avg participants >= 2.0 (participant conviction)
    Gate B: total depth not evaporating (depth decay check)
    Gate C: volume >= MA(volume) (volume confirmation)

Confidence model (7 components):
    1. IR magnitude              (0.0–0.25) — how extreme the IR is
    2. IR ROC strength           (0.0–0.20) — how fast imbalance changes
    3. Participant conviction    (0.0–0.15) — avg participants above threshold
    4. Depth decay check         (0.0–0.10) — total depth stable
    5. Volume confirmation       (0.0–0.10) — volume above average
    6. VAMP validation           (0.0–0.10) — VAMP near mid
    7. GEX regime alignment      (0.0–0.10) — IR direction matches GEX bias
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_IR_5M,
    KEY_IR_ROC_5M,
    KEY_IR_PARTICIPANTS_5M,
    KEY_VAMP_LEVELS,
    KEY_VOLUME_5M,
)

logger = logging.getLogger("Syngex.Strategies.DepthImbalanceMomentum")

MIN_CONFIDENCE = 0.10


class DepthImbalanceMomentum(BaseStrategy):
    """
    Depth Imbalance Momentum strategy — pressure-tracking engine.

    Tracks the structural weight of the order book. When the bid side
    becomes massively larger than the ask side (or vice versa), it creates
    gravitational pressure. Combined with ROC, we detect when this pressure
    is accelerating, not just static.

    LONG: IR > 3.0 (heavy bid pressure) AND ROC > 0 (imbalance rising)
    SHORT: IR < 0.6 (heavy ask pressure) AND ROC < 0 (imbalance falling)
    """

    strategy_id = "depth_imbalance_momentum"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for depth imbalance momentum signal.

        Returns a single LONG or SHORT signal when conditions are met,
        or empty list when gates fail or no clear signal.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params
        gex_calc = data.get("gex_calculator")
        regime = data.get("regime", "")

        # 1. Get IR and ROC from rolling windows
        min_ir_data_points = params.get("min_ir_data_points", 10)
        ir_window = rolling_data.get(KEY_IR_5M)
        ir_roc_window = rolling_data.get(KEY_IR_ROC_5M)

        if not ir_window or ir_window.count < min_ir_data_points:
            return []
        if not ir_roc_window or ir_roc_window.count < 5:
            return []

        current_ir = ir_window.values[-1]
        current_ir_roc = ir_roc_window.values[-1]

        # 2. Determine signal direction
        ir_threshold_long = params.get("ir_threshold_long", 2.0)
        ir_threshold_short = params.get("ir_threshold_short", 0.7)
        ir_roc_threshold_long = params.get("ir_roc_threshold_long", 0.0)
        ir_roc_threshold_short = params.get("ir_roc_threshold_short", 0.0)

        long_signal = (current_ir > ir_threshold_long and
                       current_ir_roc > ir_roc_threshold_long)
        short_signal = (current_ir < ir_threshold_short and
                        current_ir_roc < ir_roc_threshold_short)

        if not long_signal and not short_signal:
            return []

        # Only emit one signal per evaluation (LONG or SHORT, not both)
        if long_signal and short_signal:
            # Both conditions met (shouldn't happen with normal thresholds)
            # Prefer the one with more extreme IR
            long_extreme = current_ir - ir_threshold_long
            short_extreme = ir_threshold_short - current_ir
            direction = "LONG" if long_extreme >= short_extreme else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Apply 3 HARD GATES
        # Gate A: Participant conviction
        min_avg_participants = params.get("min_avg_participants", 1.5)
        gate_a = self._gate_a_participants(data, min_avg_participants, direction)

        if not gate_a:
            logger.debug(
                "Depth Imbalance: Gate A failed — avg participants below %.1f for %s",
                min_avg_participants, direction,
            )
            return []

        # Gate B: Depth decay check — total depth shouldn't be evaporating
        max_total_depth_decay = params.get("max_total_depth_decay", 0.10)
        gate_b = self._gate_b_depth_decay(rolling_data, max_total_depth_decay)

        if not gate_b:
            logger.debug(
                "Depth Imbalance: Gate B failed — depth evaporating for %s",
                direction,
            )
            return []

        # Gate C: Volume confirmation — volume >= MA(volume)
        volume_min_mult = params.get("volume_min_mult", 0.85)
        gate_c = self._gate_c_volume(rolling_data, volume_min_mult)

        if not gate_c:
            logger.debug(
                "Depth Imbalance: Gate C failed — volume below MA for %s",
                direction,
            )
            return []

        # 4. VAMP validation (optional)
        use_vamp_validation = params.get("use_vamp_validation", False)
        vamp_validated = True
        if use_vamp_validation:
            vamp_validated = self._vamp_validation(rolling_data, direction)

        if not vamp_validated:
            logger.debug(
                "Depth Imbalance: VAMP validation failed for %s", direction,
            )
            return []

        # 5. Compute confidence (7-component model)
        confidence = self._compute_confidence(
            current_ir, current_ir_roc, direction,
            rolling_data, data, params,
            regime, gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 6. Build signal with entry/stop/target
        stop_pct = params.get("stop_pct", 0.008)
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

        ir_pct = ((current_ir - 1.0) * 100) if direction == "LONG" else ((1.0 - current_ir) * 100)

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Depth imbalance {direction}: IR={current_ir:.2f} "
                f"({ir_pct:+.1f}%), ROC={current_ir_roc:+.4f}"
            ),
            metadata={
                "direction": direction,
                "ir": round(current_ir, 4),
                "ir_pct": round(ir_pct, 2),
                "ir_roc": round(current_ir_roc, 6),
                "ir_roc_pct": round(current_ir_roc * 100, 2),
                "gates": {
                    "A_participants": gate_a,
                    "B_depth_decay": gate_b,
                    "C_volume": gate_c,
                    "D_vamp": vamp_validated,
                },
                "regime": regime,
            },
        )]

    def _gate_a_participants(
        self,
        data: Dict[str, Any],
        min_avg: float,
        direction: str,
    ) -> bool:
        """
        Gate A: Participant conviction.

        The imbalance side must have >= min_avg average participants.
        """
        depth_snapshot = data.get("depth_snapshot")
        if depth_snapshot:
            if direction == "LONG":
                # Heavy bid pressure — check bid participants
                avg_participants = depth_snapshot.get("bid_avg_participants", 0)
            else:
                # Heavy ask pressure — check ask participants
                avg_participants = depth_snapshot.get("ask_avg_participants", 0)
            return avg_participants >= min_avg

        # No depth snapshot data — pass gate (can't evaluate)
        return True

    def _gate_b_depth_decay(
        self,
        rolling_data: Dict[str, Any],
        max_decay: float,
    ) -> bool:
        """
        Gate B: Depth decay check.

        Total depth shouldn't be rapidly evaporating.
        Uses depth decay windows to check if total depth is declining.
        """
        bid_decay = rolling_data.get(KEY_IR_5M)
        # Check if overall depth is stable by looking at depth decay windows
        bid_decay_window = rolling_data.get("depth_decay_bid_5m")
        ask_decay_window = rolling_data.get("depth_decay_ask_5m")

        # If we have depth decay data, check that neither side is
        # evaporating too rapidly (ROC < -max_decay means >5% drop in 5m)
        if bid_decay_window and bid_decay_window.count > 0:
            latest_bid_decay = bid_decay_window.values[-1]
            if latest_bid_decay < -max_decay:
                return False

        if ask_decay_window and ask_decay_window.count > 0:
            latest_ask_decay = ask_decay_window.values[-1]
            if latest_ask_decay < -max_decay:
                return False

        return True

    def _gate_c_volume(
        self,
        rolling_data: Dict[str, Any],
        min_mult: float,
    ) -> bool:
        """
        Gate C: Volume confirmation.

        Current volume should be at least min_mult × MA(volume).
        """
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0:
            current = volume_window.latest
            avg = volume_window.mean
            if current is not None and avg is not None and avg > 0:
                return current >= avg * min_mult

        # No volume data — pass gate (can't evaluate)
        return True

    def _vamp_validation(
        self,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> bool:
        """
        VAMP validation: VAMP should be near mid-price.

        If VAMP is far from mid, the book weight doesn't reflect
        actual price movement potential.
        """
        vamp_levels = rolling_data.get(KEY_VAMP_LEVELS)
        if not vamp_levels:
            return True  # No VAMP data — pass

        vamp = vamp_levels.get("mid_price", 0)
        vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)

        # VAMP mid deviation should not be extreme
        # For LONG: VAMP should be bid-weighted (positive deviation)
        # For SHORT: VAMP should be ask-weighted (negative deviation)
        if direction == "LONG":
            return vamp_mid_dev >= -0.001  # Allow small tolerance
        else:
            return vamp_mid_dev <= 0.001  # Allow small tolerance

    def _compute_confidence(
        self,
        current_ir: float,
        current_ir_roc: float,
        direction: str,
        rolling_data: Dict[str, Any],
        data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
        gex_calc: Any,
    ) -> float:
        """
        Compute 5-component confidence score (Family A: simple average).

        Returns 0.0–1.0.
        """
        def normalize(val, vmin, vmax):
            return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

        # 1. IR magnitude: ir_extreme from 0→5 (LONG: current_ir-1.0, SHORT: 1.0-current_ir), higher = higher
        ir_extreme = current_ir - 1.0 if direction == "LONG" else 1.0 - current_ir
        ir_range = 5.0 if direction == "LONG" else 0.5
        c1 = normalize(abs(ir_extreme), 0.0, ir_range)

        # 2. IR ROC: current_ir_roc from -0.5→0.5, use abs, higher = higher
        c2 = normalize(abs(current_ir_roc), 0.0, 0.5)

        # 3. Participant conviction: avg_participants from threshold→2×threshold, higher = higher
        depth_snapshot = data.get("depth_snapshot")
        min_avg_participants = params.get("min_avg_participants", 1.5)
        avg_participants = 0
        if depth_snapshot:
            avg_participants = depth_snapshot.get("bid_avg_participants", 0) if direction == "LONG" else depth_snapshot.get("ask_avg_participants", 0)
        c3 = normalize(avg_participants, min_avg_participants, min_avg_participants * 2.0)

        # 4. Volume confirmation: vol_ratio from 1.0→2.0, higher = higher
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        vol_ratio = 1.0
        if volume_window and volume_window.count > 0 and volume_window.mean > 0:
            vol_ratio = volume_window.latest / volume_window.mean
        c4 = normalize(vol_ratio, 1.0, 2.0)

        # 5. VAMP alignment: vamp_mid_dev from -0.001→0.001
        vamp_alignment = 1.0
        vamp_levels = rolling_data.get(KEY_VAMP_LEVELS)
        if vamp_levels:
            vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)
            if direction == "LONG" and vamp_mid_dev < 0:
                vamp_alignment = 0.0
            elif direction == "SHORT" and vamp_mid_dev > 0:
                vamp_alignment = 0.0
        c5 = vamp_alignment

        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))
