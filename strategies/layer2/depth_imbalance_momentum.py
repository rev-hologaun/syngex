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
    KEY_VOLUME_5M,
)

logger = logging.getLogger("Syngex.Strategies.DepthImbalanceMomentum")

MIN_CONFIDENCE = 0.30


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
        ir_threshold_long = params.get("ir_threshold_long", 3.0)
        ir_threshold_short = params.get("ir_threshold_short", 0.6)
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
        min_avg_participants = params.get("min_avg_participants", 2.0)
        gate_a = self._gate_a_participants(data, min_avg_participants, direction)

        if not gate_a:
            logger.debug(
                "Depth Imbalance: Gate A failed — avg participants below %.1f for %s",
                min_avg_participants, direction,
            )
            return []

        # Gate B: Depth decay check — total depth shouldn't be evaporating
        max_total_depth_decay = params.get("max_total_depth_decay", 0.05)
        gate_b = self._gate_b_depth_decay(rolling_data, max_total_depth_decay)

        if not gate_b:
            logger.debug(
                "Depth Imbalance: Gate B failed — depth evaporating for %s",
                direction,
            )
            return []

        # Gate C: Volume confirmation — volume >= MA(volume)
        volume_min_mult = params.get("volume_min_mult", 1.0)
        gate_c = self._gate_c_volume(rolling_data, volume_min_mult)

        if not gate_c:
            logger.debug(
                "Depth Imbalance: Gate C failed — volume below MA for %s",
                direction,
            )
            return []

        # 4. VAMP validation (optional)
        use_vamp_validation = params.get("use_vamp_validation", True)
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
        vamp_levels = rolling_data.get("vamp_levels")
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
        Compute 7-component confidence score.

        Returns 0.0–1.0.
        """
        # Direction-specific IR for scoring
        if direction == "LONG":
            ir_extreme = current_ir - 1.0  # How far above 1.0
        else:
            ir_extreme = 1.0 - current_ir  # How far below 1.0

        # 1. IR magnitude (0.0–0.25)
        # How extreme the IR is — at threshold = baseline, above = bonus
        ir_threshold = params.get("ir_threshold_long", 3.0) if direction == "LONG" else params.get("ir_threshold_short", 0.6)
        conf_ir = 0.0
        if direction == "LONG":
            # IR > 3.0 = strong; scale from 0 at IR=1.0 to 0.25 at IR=6.0+
            if current_ir > 1.0:
                conf_ir = min(0.25, 0.25 * min(1.0, (current_ir - 1.0) / 5.0))
        else:
            # IR < 0.6 = strong; scale from 0 at IR=1.0 to 0.25 at IR=0.1
            if current_ir < 1.0:
                conf_ir = min(0.25, 0.25 * min(1.0, (1.0 - current_ir) / 0.5))

        # 2. IR ROC strength (0.0–0.20)
        # How fast the imbalance is changing
        conf_roc = 0.0
        if direction == "LONG" and current_ir_roc > 0:
            conf_roc = min(0.20, 0.20 * min(1.0, current_ir_roc / 0.5))
        elif direction == "SHORT" and current_ir_roc < 0:
            conf_roc = min(0.20, 0.20 * min(1.0, abs(current_ir_roc) / 0.5))

        # 3. Participant conviction (0.0–0.15)
        # Avg participants above threshold
        min_avg_participants = params.get("min_avg_participants", 2.0)
        conf_participants = 0.05  # baseline (gate A already passed)
        depth_snapshot = data.get("depth_snapshot")
        if depth_snapshot:
            if direction == "LONG":
                avg_participants = depth_snapshot.get("bid_avg_participants", 0)
            else:
                avg_participants = depth_snapshot.get("ask_avg_participants", 0)
            # Scale: at threshold = 0.10, at 2× threshold = 0.15
            if avg_participants > min_avg_participants:
                conf_participants = 0.10 + 0.05 * min(
                    1.0, (avg_participants - min_avg_participants) / min_avg_participants
                )

        # 4. Depth decay check (0.0–0.10)
        # Total depth stable (not evaporating)
        max_total_depth_decay = params.get("max_total_depth_decay", 0.05)
        conf_depth = 0.05  # baseline (gate B already passed)
        bid_decay_window = rolling_data.get("depth_decay_bid_5m")
        ask_decay_window = rolling_data.get("depth_decay_ask_5m")
        if bid_decay_window and bid_decay_window.count > 0:
            latest_bid_decay = bid_decay_window.values[-1]
            if latest_bid_decay >= -max_total_depth_decay * 0.5:
                conf_depth = 0.10
            elif latest_bid_decay < -max_total_depth_decay:
                conf_depth = 0.02
        if ask_decay_window and ask_decay_window.count > 0:
            latest_ask_decay = ask_decay_window.values[-1]
            if latest_ask_decay >= -max_total_depth_decay * 0.5:
                conf_depth = max(conf_depth, 0.10)
            elif latest_ask_decay < -max_total_depth_decay:
                conf_depth = min(conf_depth, 0.02)

        # 5. Volume confirmation (0.0–0.10)
        # Volume above average
        volume_min_mult = params.get("volume_min_mult", 1.0)
        conf_volume = 0.05  # baseline (gate C already passed)
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0:
            current_vol = volume_window.latest
            avg_vol = volume_window.mean
            if current_vol is not None and avg_vol is not None and avg_vol > 0:
                vol_ratio = current_vol / avg_vol
                conf_volume = 0.05 + 0.05 * min(1.0, (vol_ratio - volume_min_mult) / volume_min_mult)

        # 6. VAMP validation (0.0–0.10)
        # VAMP near mid (not divergent)
        conf_vamp = 0.05  # baseline (validation already passed)
        vamp_levels = rolling_data.get("vamp_levels")
        if vamp_levels:
            vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)
            if direction == "LONG" and vamp_mid_dev >= 0:
                conf_vamp = 0.10
            elif direction == "SHORT" and vamp_mid_dev <= 0:
                conf_vamp = 0.10
            elif abs(vamp_mid_dev) < 0.0005:
                conf_vamp = 0.08

        # 7. GEX regime alignment (0.0–0.10)
        # IR direction matches GEX bias
        conf_gex = 0.05  # baseline
        if gex_calc and regime:
            net_gamma = gex_calc.get_net_gamma() if hasattr(gex_calc, "get_net_gamma") else 0
            if direction == "LONG" and net_gamma > 0:
                conf_gex = 0.10
            elif direction == "SHORT" and net_gamma < 0:
                conf_gex = 0.10
            elif regime in ("POSITIVE", "NEGATIVE"):
                if direction == "LONG" and regime == "POSITIVE":
                    conf_gex = 0.08
                elif direction == "SHORT" and regime == "NEGATIVE":
                    conf_gex = 0.08

        # Sum all components
        confidence = (
            conf_ir + conf_roc + conf_participants +
            conf_depth + conf_volume + conf_vamp + conf_gex
        )
        return min(1.0, max(0.0, confidence))
