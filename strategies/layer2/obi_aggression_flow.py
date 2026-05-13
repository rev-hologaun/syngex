"""
strategies/layer2/obi_aggression_flow.py — OBI + Aggression Flow

Order Book Imbalance + Aggressive Trade Flow strategy (bidirectional).
Detects high-conviction entries when passive order book skew and active
trade execution agree on direction — filters out spoofing and passive
walls that never get tested.

LONG: OBI > 0.75 (bid-heavy book) AND AF > 0.5 (buy aggression)
SHORT: OBI < -0.75 (ask-heavy book) AND AF < -0.5 (sell aggression)

Logic:
    1. Compute OBI = (bid_size - ask_size) / total_depth from depth_agg
    2. Compute AF = (buy_vol - sell_vol) / total_aggressive from quotes
    3. Master trigger: OBI and AF agree on direction with sufficient magnitude
    4. Apply 3 hard gates (volume spike, participant diversity, spread stability)
    5. Compute 7-component confidence score
    6. Emit LONG or SHORT signal with entry/stop/target

Confidence factors (7 components):
    1. OBI magnitude              (0.0–0.25)
    2. AF magnitude               (0.0–0.25)
    3. OBI × AF confluence        (0.0–0.15)
    4. Volume spike strength      (0.0–0.10)
    5. Participant diversity      (0.0–0.10)
    6. Spread stability           (0.0–0.05)
    7. GEX regime alignment       (0.0–0.10)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_OBI_5M,
    KEY_AF_5M,
    KEY_TRADE_SIZE_5M,
    KEY_DEPTH_SPREAD_5M,
)

logger = logging.getLogger("Syngex.Strategies.ObiAggressionFlow")

MIN_CONFIDENCE = 0.30


class ObiAggressionFlow(BaseStrategy):
    """
    OBI + Aggression Flow strategy.

    Combines Order Book Imbalance (passive book skew) with Aggression Flow
    (active trade execution) to detect high-conviction entries. Only enters
    when BOTH the passive book AND active trades agree on direction.
    """

    strategy_id = "obi_aggression_flow"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for OBI + Aggression Flow signal.

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

        # --- 1. Get OBI from rolling window ---
        obi_window = rolling_data.get(KEY_OBI_5M)
        if obi_window is None or obi_window.count < 1:
            return []
        current_obi = obi_window.values[-1]

        # --- 2. Get AF from rolling window ---
        af_window = rolling_data.get(KEY_AF_5M)
        if af_window is None or af_window.count < 1:
            return []
        current_af = af_window.values[-1]

        # --- 3. Master trigger: OBI × AF ---
        obi_threshold = params.get("obi_threshold", 0.75)
        af_threshold = params.get("af_threshold", 0.5)
        min_obi_points = params.get("min_obi_data_points", 10)
        min_af_points = params.get("min_af_data_points", 5)

        if obi_window.count < min_obi_points:
            return []
        if af_window.count < min_af_points:
            return []

        # LONG: OBI > threshold AND AF > threshold
        # SHORT: OBI < -threshold AND AF < -threshold
        direction = None
        if current_obi > obi_threshold and current_af > af_threshold:
            direction = "LONG"
        elif current_obi < -obi_threshold and current_af < -af_threshold:
            direction = "SHORT"

        if direction is None:
            return []

        # --- 4. Apply 3 HARD GATES ---
        gate_a, gate_b, gate_c = self._evaluate_gates(
            data, rolling_data, params, direction,
        )

        if not (gate_a and gate_b and gate_c):
            logger.debug(
                "OBI AF gate fail: direction=%s gates=[A=%s B=%s C=%s]",
                direction, gate_a, gate_b, gate_c,
            )
            return []

        # --- 5. Compute confidence (7-component model) ---
        confidence = self._compute_confidence(
            current_obi, current_af, data, rolling_data, params,
            direction, regime, gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # --- 6. Build signal with entry/stop/target ---
        stop_pct = params.get("stop_pct", 0.005)
        target_risk_mult = params.get("target_risk_mult", 1.5)

        entry = underlying_price
        stop_distance = entry * stop_pct

        if direction == "LONG":
            stop = entry - stop_distance
            target = entry + (stop_distance * target_risk_mult)
        else:
            stop = entry + stop_distance
            target = entry - (stop_distance * target_risk_mult)

        direction_enum = Direction.LONG if direction == "LONG" else Direction.SHORT

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"OBI+AF: OBI={current_obi:.3f}, AF={current_af:.3f}, "
                f"direction={direction}, conf={confidence:.2f}"
            ),
            metadata={
                "direction": direction,
                "obi": round(current_obi, 4),
                "af": round(current_af, 4),
                "obi_af_product": round(current_obi * current_af, 4),
                "gates": {
                    "A_volume_spike": gate_a,
                    "B_participant_diversity": gate_b,
                    "C_spread_stability": gate_c,
                },
                "regime": regime,
                "risk": round(stop_distance, 4),
                "risk_reward_ratio": round(
                    abs(target - entry) / stop_distance, 2
                ) if stop_distance > 0 else 0,
            },
        )]

    def _evaluate_gates(
        self,
        data: Dict[str, Any],
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
        direction: str,
    ) -> tuple:
        """
        Evaluate the 3 hard gates. All must pass for signal emission.

        Gate A: Latest trade size > volume_spike_mult × MA(trade_size)
        Gate B: Avg participants > min_avg_participants
        Gate C: Current spread < max_spread_multiplier × MA(spread)
        """
        # --- Gate A: Volume threshold ---
        trade_size_mult = params.get("volume_spike_mult", 2.0)
        trade_size_window = rolling_data.get(KEY_TRADE_SIZE_5M)
        gate_a = True
        if trade_size_window and trade_size_window.count > 0:
            avg_trade_size = sum(trade_size_window.values) / len(
                trade_size_window.values
            )
            # Get latest trade size from depth snapshot or quotes
            depth_snapshot = data.get("depth_snapshot", {})
            latest_trade_size = depth_snapshot.get("last_size", 0)
            if avg_trade_size > 0:
                gate_a = latest_trade_size > avg_trade_size * trade_size_mult

        # --- Gate B: Participant diversity ---
        min_avg_participants = params.get("min_avg_participants", 1.0)
        gate_b = True
        depth_snapshot = data.get("depth_snapshot", {})
        bid_avg = depth_snapshot.get("bid_avg_participants", 0)
        ask_avg = depth_snapshot.get("ask_avg_participants", 0)
        if bid_avg > 0 or ask_avg > 0:
            avg_participants = (bid_avg + ask_avg) / 2
            gate_b = avg_participants >= min_avg_participants

        # --- Gate C: Spread stability ---
        max_spread_mult = params.get("max_spread_multiplier", 1.5)
        gate_c = True
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        if spread_window and spread_window.count > 0:
            ma_spread = spread_window.mean or 0
            current_spread = depth_snapshot.get("spread", 0)
            if ma_spread > 0:
                gate_c = current_spread < ma_spread * max_spread_mult

        return gate_a, gate_b, gate_c

    def _compute_confidence(
        self,
        current_obi: float,
        current_af: float,
        data: Dict[str, Any],
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
        direction: str,
        regime: str,
        gex_calc: Any,
    ) -> float:
        """
        Compute 7-component confidence score.

        Returns 0.0–1.0.
        """
        # --- 1. OBI magnitude (0.0–0.25) ---
        # |OBI| scaled linearly; at threshold = ~0.15, at 1.0 = 0.25
        obi_threshold = params.get("obi_threshold", 0.75)
        obi_mag = abs(current_obi)
        conf_obi = min(0.25, 0.15 * (obi_mag / obi_threshold) if obi_threshold > 0 else 0.0)

        # --- 2. AF magnitude (0.0–0.25) ---
        # |AF| scaled linearly; at threshold = ~0.15, at 1.0 = 0.25
        af_threshold = params.get("af_threshold", 0.5)
        af_mag = abs(current_af)
        conf_af = min(0.25, 0.15 * (af_mag / af_threshold) if af_threshold > 0 else 0.0)

        # --- 3. OBI × AF confluence (0.0–0.15) ---
        # Product magnitude, direction-aligned
        obi_af_product = current_obi * current_af
        obi_af_mag = abs(obi_af_product)
        conf_confluence = min(0.15, 0.10 * (obi_af_mag / 0.375) if obi_af_mag > 0 else 0.0)
        # Bonus if direction-aligned (both positive for LONG, both negative for SHORT)
        if (direction == "LONG" and obi_af_product > 0) or (
            direction == "SHORT" and obi_af_product > 0
        ):
            conf_confluence = min(0.15, conf_confluence + 0.05)

        # --- 4. Volume spike strength (0.0–0.10) ---
        trade_size_mult = params.get("volume_spike_mult", 2.0)
        trade_size_window = rolling_data.get(KEY_TRADE_SIZE_5M)
        conf_volume = 0.0
        if trade_size_window and trade_size_window.count > 0:
            avg_trade_size = sum(trade_size_window.values) / len(
                trade_size_window.values
            )
            depth_snapshot = data.get("depth_snapshot", {})
            latest_trade_size = depth_snapshot.get("last_size", 0)
            if avg_trade_size > 0:
                ratio = latest_trade_size / avg_trade_size
                conf_volume = min(0.10, 0.05 * (ratio / trade_size_mult))

        # --- 5. Participant diversity (0.0–0.10) ---
        min_avg_participants = params.get("min_avg_participants", 1.0)
        depth_snapshot = data.get("depth_snapshot", {})
        bid_avg = depth_snapshot.get("bid_avg_participants", 0)
        ask_avg = depth_snapshot.get("ask_avg_participants", 0)
        conf_participants = 0.0
        if bid_avg > 0 or ask_avg > 0:
            avg_participants = (bid_avg + ask_avg) / 2
            if min_avg_participants > 0:
                conf_participants = min(
                    0.10,
                    0.05 * (avg_participants / min_avg_participants),
                )

        # --- 6. Spread stability (0.0–0.05) ---
        max_spread_mult = params.get("max_spread_multiplier", 1.5)
        conf_spread = 0.0
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        if spread_window and spread_window.count > 0:
            ma_spread = spread_window.mean or 0
            current_spread = depth_snapshot.get("spread", 0)
            if ma_spread > 0:
                spread_ratio = current_spread / ma_spread
                if spread_ratio < max_spread_mult:
                    # How much below MA threshold? Closer to 0 = more stable
                    conf_spread = min(
                        0.05,
                        0.03 * (1.0 - (spread_ratio / max_spread_mult)),
                    )

        # --- 7. GEX regime alignment (0.0–0.10) ---
        # OBI direction matches GEX bias
        conf_gex = 0.05  # baseline
        if gex_calc and regime:
            try:
                net_gamma = gex_calc.get_net_gamma() if hasattr(
                    gex_calc, "get_net_gamma"
                ) else 0
            except Exception:
                net_gamma = 0
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
            conf_obi + conf_af + conf_confluence + conf_volume
            + conf_participants + conf_spread + conf_gex
        )
        return min(1.0, max(0.0, confidence))
