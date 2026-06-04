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
    4. Apply 3 graded gates (volume spike, participant diversity, spread stability)
    5. Compute 7-component confidence score
    6. Emit LONG or SHORT signal with entry/stop/target

Confidence factors (7 components, simple average):
    1. OBI magnitude              (abs(OBI) normalized 0→1)
    2. AF magnitude               (abs(AF) normalized 0→1)
    3. OBI × AF confluence        (abs(OBI×AF) normalized 0→1)
    4. Gate A: Volume spike       (graded gate score 0→1)
    5. Gate B: Participant diversity (graded gate score 0→1)
    6. Gate C: Spread stability   (graded gate score 0→1)
    7. GEX regime alignment       (1.0 if aligned, 0.5 neutral, 0.0 opposed)
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

# Throttle info-level logging to once per N evaluation cycles
_eval_counter = 0
_EVAL_THROTTLE = 100


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
        min_confidence = params.get("min_confidence", 0.20)
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

        global _eval_counter
        _eval_counter += 1

        # --- 3. Master trigger: OBI × AF ---
        obi_threshold = params.get("obi_threshold", 0.60)
        af_threshold = params.get("af_threshold", 0.40)
        min_obi_points = params.get("min_obi_data_points", 10)
        min_af_points = params.get("min_af_data_points", 5)

        if obi_window.count < min_obi_points:
            return []
        if af_window.count < min_af_points:
            return []

        # Combined score approach: OBI and AF agree on direction
        combined = abs(current_obi) + abs(current_af)
        combined_threshold = obi_threshold + af_threshold  # 0.60 + 0.40 = 1.0

        direction = None
        if combined > combined_threshold:
            direction = "LONG" if current_obi > 0 else "SHORT"
        elif combined > combined_threshold * 0.85:
            # Near-miss zone: both components must be contributing,
            # just short of full combined threshold
            min_obi_fallback = obi_threshold * 0.60
            min_af_fallback = af_threshold * 0.60
            if (abs(current_obi) > min_obi_fallback
                    and abs(current_af) > min_af_fallback
                    and current_obi * current_af > 0):
                direction = "LONG" if current_obi > 0 else "SHORT"

        if direction is None:
            logger.debug(
                "OBI_AF master: OBI=%.3f AF=%.3f combined=%.3f | no direction",
                current_obi, current_af, combined,
            )
            return []

        # --- 4. Evaluate gates (now returns scores, not bools) ---
        gate_a_score, gate_b_score, gate_c_score = self._evaluate_gates(
            data, rolling_data, params, direction,
        )

        # --- 5. Compute confidence (8-component model) ---
        confidence = self._compute_confidence(
            current_obi, current_af, data, rolling_data, params,
            direction, regime, gex_calc,
            gate_a_score, gate_b_score, gate_c_score,
        )

        if confidence < min_confidence:
            logger.warning(
                "OBI_AF confidence below threshold: %.2f < %.2f",
                confidence, min_confidence,
            )
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

        if _eval_counter % _EVAL_THROTTLE == 0:
            logger.info(
                "OBI_AF SIGNAL: %s confidence=%.2f direction=%s OBI=%.3f AF=%.3f",
                "LONG" if direction == "LONG" else "SHORT", confidence,
                direction, current_obi, current_af,
            )

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
                    "A_volume_spike": round(gate_a_score, 3),
                    "B_participant_diversity": round(gate_b_score, 3),
                    "C_spread_stability": round(gate_c_score, 3),
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
        Evaluate gates and return confidence scores (0.0–1.0) for each.
        """
        # --- Gate A: Volume score ---
        trade_size_mult = params.get("volume_spike_mult", 1.5)
        trade_size_window = rolling_data.get(KEY_TRADE_SIZE_5M)
        gate_a_score = 1.0
        if trade_size_window and trade_size_window.count > 0:
            avg_trade_size = sum(trade_size_window.values) / len(trade_size_window.values)
            depth_snapshot = data.get("depth_snapshot", {})
            latest_trade_size = depth_snapshot.get("last_size", 0)
            if avg_trade_size > 0 and latest_trade_size > 0:
                trade_size_ratio = latest_trade_size / avg_trade_size
                if trade_size_ratio >= trade_size_mult:
                    gate_a_score = 1.0
                elif trade_size_ratio >= 1.0:
                    gate_a_score = trade_size_ratio / trade_size_mult
                else:
                    gate_a_score = 0.0

        # --- Gate B: Participant score ---
        min_avg_participants = params.get("min_avg_participants", 1.0)
        gate_b_score = 1.0
        depth_snapshot = data.get("depth_snapshot", {})
        bid_avg = depth_snapshot.get("bid_avg_participants", 0)
        ask_avg = depth_snapshot.get("ask_avg_participants", 0)
        if bid_avg > 0 or ask_avg > 0:
            avg_participants = (bid_avg + ask_avg) / 2
            if avg_participants >= min_avg_participants:
                gate_b_score = 1.0
            else:
                gate_b_score = avg_participants / min_avg_participants

        # --- Gate C: Spread score (0.0 on extreme widening) ---
        max_spread_mult = params.get("max_spread_multiplier", 1.5)
        gate_c_score = 1.0
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        if spread_window and spread_window.count > 0:
            ma_spread = spread_window.mean or 0
            current_spread = depth_snapshot.get("spread", 0)
            if ma_spread > 0:
                spread_ratio = current_spread / ma_spread
                if spread_ratio <= 1.0:
                    gate_c_score = 1.0
                elif spread_ratio <= max_spread_mult:
                    gate_c_score = 1.0 - (spread_ratio - 1.0) / max_spread_mult * 0.5
                else:
                    gate_c_score = 0.0

        return gate_a_score, gate_b_score, gate_c_score

    def _gex_regime_alignment(
        self, regime: str, gex_calc: Any, direction: str,
    ) -> float:
        """Determine if GEX regime supports the signal direction.

        Returns:
            1.0 — regime aligns with signal (bullish regime for LONG, bearish for SHORT)
            0.5 — neutral/mixed/insufficient data
            0.0 — regime opposes signal
        """
        if gex_calc is None:
            return 0.5  # No GEX data → neutral

        # Use get_net_gamma() to determine the actual GEX bias direction.
        # Positive net gamma → positive GEX regime (bullish bias: dealers buy dips)
        # Negative net gamma → negative GEX regime (bearish bias: dealers sell dips)
        net_gamma = gex_calc.get_net_gamma()

        if net_gamma > 0:
            # Positive GEX regime: supports LONG (buy dips), opposes SHORT
            return 1.0 if direction == "LONG" else 0.0
        elif net_gamma < 0:
            # Negative GEX regime: supports SHORT (sell dips), opposes LONG
            return 1.0 if direction == "SHORT" else 0.0
        else:
            # Neutral/mixed GEX — no clear bias
            return 0.5

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
        gate_a_score: float = 1.0,
        gate_b_score: float = 1.0,
        gate_c_score: float = 1.0,
    ) -> float:
        """
        Compute 7-component simple average confidence score.

        Each component normalizes to [0,1], then average equally (÷7).
        Gates are graded scores — no double-counting of volume/participant
        data that gates already cover, spread is now included.

        Components:
            c1: OBI magnitude (abs(OBI) normalized 0→1)
            c2: AF magnitude (abs(AF) normalized 0→1)
            c3: OBI×AF confluence (abs(product) normalized 0→1)
            c4: Gate A (volume spike graded score 0→1)
            c5: Gate B (participant diversity graded score 0→1)
            c6: Gate C (spread stability graded score 0→1)
            c7: GEX regime alignment (1.0=aligned, 0.5=neutral, 0.0=opposed)

        Returns 0.0–1.0.
        """
        def normalize(val: float, vmin: float, vmax: float) -> float:
            return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

        # 1. OBI magnitude: abs(current_obi) from 0→1.0, higher = higher
        c1 = normalize(abs(current_obi), 0.0, 1.0)

        # 2. AF magnitude: abs(current_af) from 0→1.0, higher = higher
        c2 = normalize(abs(current_af), 0.0, 1.0)

        # 3. OBI×AF confluence: abs(product) from 0→1.0, higher = higher
        obi_af_product = current_obi * current_af
        obi_af_mag = abs(obi_af_product)
        c3 = normalize(obi_af_mag, 0.0, 1.0)

        # 4. Gate A: Volume spike graded score (reuses gate_a_score)
        c4 = gate_a_score

        # 5. Gate B: Participant diversity graded score (reuses gate_b_score)
        c5 = gate_b_score

        # 6. Gate C: Spread stability graded score (reuses gate_c_score)
        c6 = gate_c_score

        # 7. GEX regime alignment — does the GEX bias support this signal?
        #    POSITIVE regime (dealers buy dips, sell rallies): LONG aligns, SHORT opposes
        #    NEGATIVE regime (dealers sell dips, buy rallies): SHORT aligns, LONG opposes
        #    Use gex_calc.get_net_gamma() as ground truth for regime direction
        c7 = self._gex_regime_alignment(regime, gex_calc, direction)

        confidence = (c1 + c2 + c3 + c4 + c5 + c6 + c7) / 7.0
        confidence = min(1.0, max(0.0, confidence))

        global _eval_counter
        if _eval_counter % _EVAL_THROTTLE == 0:
            logger.info(
                "OBI_AF confidence: c1(obi)=%.2f c2(af)=%.2f c3(confluence)=%.2f c4(gate_a_vol)=%.2f c5(gate_b_part)=%.2f c6(gate_c_spread)=%.2f c7(gex)=%.2f | final=%.2f",
                c1, c2, c3, c4, c5, c6, c7, confidence,
            )

        return confidence
