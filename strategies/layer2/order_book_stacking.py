"""
strategies/layer2/order_book_stacking.py — Order Book Stacking

Structural concentration strategy that detects anomalous order book walls
using Stack Intensity Score (SIS). A "stack" is a level whose size
significantly exceeds the recent average level size.

Core concept:
    Detects large order concentrations ("stacks") at specific price levels
    that act as hidden support/resistance. A stack is anomalous when its
    size significantly exceeds the recent average level size.

    STACK_BOUNCE_LONG:  Massive bid stack holds → scalp the bounce
    STACK_BREACH_SHORT: Massive ask stack eaten → scalp the breakout
    STACK_BOUNCE_SHORT: Massive ask stack holds → scalp the rejection
    STACK_BREACH_LONG:  Massive bid stack evaporates → scalp the breakdown

Signal types:
    STACK_BOUNCE_LONG:  Mean reversion bounce off bid stack
    STACK_BREACH_SHORT: Momentum breakout as ask stack eaten
    STACK_BOUNCE_SHORT: Mean reversion rejection off ask stack
    STACK_BREACH_LONG:  Momentum breakdown as bid stack evaporates

This is a **filter-style structural concentration engine** — it produces graded signal strength
based on SIS magnitude and ROC direction, not binary pass/fail.

Signal strength per type:
    strength = sis_component + roc_component (continuous 0–1)
    signal_strength = strength * 0.5 + mag * 0.15 + parts * 0.15 + vol * 0.10 + spread * 0.10
    Emit when signal_strength >= 0.25 and sis_strength >= 0.15

Confidence model (5 components, weighted sum to 1.0):
    1. SIS intensity        (weight 0.35)
    2. ROC magnitude        (weight 0.25)
    3. Volume confirmation  (weight 0.15)
    4. Spread tightness     (weight 0.10)
    5. Participant diversity (weight 0.15)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_DEPTH_BID_LEVEL_AVG_5M,  # stores median level size (robust to outliers)
    KEY_DEPTH_ASK_LEVEL_AVG_5M,  # stores median level size (robust to outliers)
    KEY_SIS_BID_5M,
    KEY_SIS_ASK_5M,
    KEY_SIS_BID_ROC_5M,
    KEY_SIS_ASK_ROC_5M,
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_ASK_SIZE_5M,
    KEY_DEPTH_BID_LEVELS_5M,
    KEY_DEPTH_ASK_LEVELS_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_VOLUME_5M,
    KEY_TOP_WALL_BID_SIZE_5M,
    KEY_TOP_WALL_ASK_SIZE_5M,
    KEY_BID_PARTICIPANTS_5M,
    KEY_ASK_PARTICIPANTS_5M,
)


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

logger = logging.getLogger("Syngex.Strategies.OrderBookStacking")

MIN_CONFIDENCE = 0.05


class OrderBookStacking(BaseStrategy):
    """
    Order Book Stacking — structural concentration strategy.

    Detects anomalous order book walls using Stack Intensity Score (SIS).
    Trades both the bounce off real stacks and the breakout when they collapse.

    STACK_BOUNCE_LONG:  Massive bid stack holds → scalp the bounce
    STACK_BREACH_SHORT: Massive ask stack eaten → scalp the breakout
    STACK_BOUNCE_SHORT: Massive ask stack holds → scalp the rejection
    STACK_BREACH_LONG:  Massive bid stack evaporates → scalp the breakdown
    """

    strategy_id = "order_book_stacking"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for order book stacking signal.

        Returns a single LONG or SHORT signal when conditions are met,
        or empty list when gates fail or no clear signal.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params

        # 1. Get SIS and decay from rolling windows
        sis_bid_window = rolling_data.get(KEY_SIS_BID_5M)
        sis_ask_window = rolling_data.get(KEY_SIS_ASK_5M)
        sis_bid_roc_window = rolling_data.get(KEY_SIS_BID_ROC_5M)
        sis_ask_roc_window = rolling_data.get(KEY_SIS_ASK_ROC_5M)

        min_data = params.get("min_data_points", 5)
        if not sis_bid_window or sis_bid_window.count < min_data:
            return []
        if not sis_ask_window or sis_ask_window.count < min_data:
            return []
        if not sis_bid_roc_window or sis_bid_roc_window.count < 5:
            return []
        if not sis_ask_roc_window or sis_ask_roc_window.count < 5:
            return []

        current_sis_bid = sis_bid_window.values[-1]
        current_sis_ask = sis_ask_window.values[-1]
        current_bid_roc = sis_bid_roc_window.values[-1]
        current_ask_roc = sis_ask_roc_window.values[-1]

        # 2. Compute continuous strength for each of the 4 signal types
        sis_threshold = params.get("sis_threshold", 2.0)
        roc_threshold = params.get("roc_threshold", -0.3)
        moderate_threshold = params.get("moderate_threshold", 1.0)

        # STACK_BOUNCE_LONG — massive bid stack holding (high SIS, neutral/positive ROC)
        stack_bounce_long_strength = 0.0
        if current_sis_bid > moderate_threshold and current_bid_roc >= roc_threshold:
            # Strength proportional to how much SIS exceeds moderate threshold
            stack_bounce_long_strength = (current_sis_bid - moderate_threshold) / (sis_threshold - moderate_threshold)
            # ROC bonus: positive ROC (stack building) = stronger bounce
            if current_bid_roc > 0:
                stack_bounce_long_strength *= min(1.0, current_bid_roc / 0.5)

        # STACK_BREACH_SHORT — massive ask stack being eaten (high SIS, negative ROC)
        stack_breach_short_strength = 0.0
        if current_sis_ask > moderate_threshold and current_ask_roc < roc_threshold:
            stack_breach_short_strength = (current_sis_ask - moderate_threshold) / (sis_threshold - moderate_threshold)
            # ROC urgency: more negative ROC = stronger breach
            roc_magnitude = abs(current_ask_roc)
            stack_breach_short_strength *= min(1.0, roc_magnitude / max(0.01, abs(roc_threshold)))

        # STACK_BOUNCE_SHORT — massive ask stack holding
        stack_bounce_short_strength = 0.0
        if current_sis_ask > moderate_threshold and current_ask_roc >= roc_threshold:
            stack_bounce_short_strength = (current_sis_ask - moderate_threshold) / (sis_threshold - moderate_threshold)
            if current_ask_roc > 0:
                stack_bounce_short_strength *= min(1.0, current_ask_roc / 0.5)

        # STACK_BREACH_LONG — massive bid stack evaporating
        stack_breach_long_strength = 0.0
        if current_sis_bid > moderate_threshold and current_bid_roc < roc_threshold:
            stack_breach_long_strength = (current_sis_bid - moderate_threshold) / (sis_threshold - moderate_threshold)
            roc_magnitude = abs(current_bid_roc)
            stack_breach_long_strength *= min(1.0, roc_magnitude / max(0.01, abs(roc_threshold)))

        # Find the strongest signal
        candidates = [
            ("STACK_BOUNCE_LONG", "LONG", stack_bounce_long_strength, 0.0),
            ("STACK_BREACH_SHORT", "SHORT", stack_breach_short_strength, abs(current_ask_roc)),
            ("STACK_BOUNCE_SHORT", "SHORT", stack_bounce_short_strength, 0.0),
            ("STACK_BREACH_LONG", "LONG", stack_breach_long_strength, abs(current_bid_roc)),
        ]
        candidates.sort(key=lambda x: x[2], reverse=True)
        signal_type, direction, strength, roc_strength = candidates[0]

        # Emit only if strongest signal exceeds minimum strength
        if strength < 0.15:
            return []

        # 3. Compute vol_ratio, spread, and stack significance for gates
        vol_ratio = self._compute_vol_ratio(rolling_data)
        spread = self._compute_spread(rolling_data)
        avg_spread = self._compute_avg_spread(rolling_data)
        avg_level_size = self._compute_avg_level_size(rolling_data)

        # 5. Extract regime and gex_calc from data for confidence model
        regime = data.get("regime", "neutral")
        gex_calc = data.get("gex_calculator", {})

        # 6. Compute soft gate scores (replaces hard gates)
        mag_score = self._gate_a_magnitude_score(
            direction, avg_level_size, rolling_data
        )
        part_score = self._gate_b_participants_score(
            direction, rolling_data
        )
        vol_score = self._gate_c_vol_score(signal_type, vol_ratio)
        spread_score = self._gate_d_spread_score(spread, avg_spread)

        # Combine into signal_strength
        signal_strength = (
            strength * 0.5
            + mag_score * 0.15
            + part_score * 0.15
            + vol_score * 0.10
            + spread_score * 0.10
        )

        # Emit when signal_strength >= threshold
        if signal_strength < 0.15:
            logger.debug(
                "Stacking: signal_strength %.3f below threshold for %s (%s)",
                signal_strength, direction, signal_type,
            )
            return []

        # 7. Compute confidence (5-component model)
        confidence, conf_breakdown = self._compute_confidence(
            signal_type, direction,
            current_sis_bid, current_sis_ask,
            current_bid_roc, current_ask_roc,
            vol_ratio, spread, avg_spread,
            rolling_data, data, params, regime, gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        confidence = max(min_confidence, confidence)

        # 8. Build signal with entry/stop/target
        stop_pct = params.get("stop_pct", 0.003)
        target_risk_mult = params.get("target_risk_mult", 3.0)

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
                f"{signal_type} {direction}: sis_bid={current_sis_bid:.2f} "
                f"sis_ask={current_sis_ask:.2f} "
                f"bid_roc={current_bid_roc:+.4f} "
                f"ask_roc={current_ask_roc:+.4f}"
            ),
            metadata={
                "signal_type": signal_type,
                "direction": direction,
                "strength": round(strength, 4),
                "roc_strength": round(roc_strength, 4),
                "signal_strength": round(signal_strength, 4),
                "sis_bid": round(current_sis_bid, 4),
                "sis_ask": round(current_sis_ask, 4),
                "bid_roc": round(current_bid_roc, 6),
                "ask_roc": round(current_ask_roc, 6),
                "vol_ratio": round(vol_ratio, 4),
                "spread": round(spread, 4),
                "avg_spread": round(avg_spread, 4),
                "magnitude_score": round(mag_score, 4),
                "participants_score": round(part_score, 4),
                "volume_score": round(vol_score, 4),
                "spread_score": round(spread_score, 4),
                "conf_breakdown": conf_breakdown,
                "regime": regime,
            },
        )]

    # ------------------------------------------------------------------
    # Gate helpers (soft scores)
    # ------------------------------------------------------------------

    def _gate_a_magnitude_score(
        self,
        direction: str,
        avg_level_size: float,
        rolling_data: Dict[str, Any],
    ) -> float:
        """
        Gate A: Magnitude score (soft).

        Returns a float 0.0–1.0 based on how large the wall is
        relative to the average level size.
        """
        if avg_level_size <= 0:
            return 0.5  # Can't compute — neutral

        top_wall_key = (
            KEY_TOP_WALL_BID_SIZE_5M if direction == "LONG" else KEY_TOP_WALL_ASK_SIZE_5M
        )
        top_wall_rw = rolling_data.get(top_wall_key)

        if not top_wall_rw or top_wall_rw.count < 1:
            return 0.5  # Can't evaluate — neutral

        current_wall = top_wall_rw.values[-1]
        if current_wall <= 0:
            return 0.0

        wall_ratio = current_wall / avg_level_size
        return min(1.0, wall_ratio / 10.0)

    def _gate_b_participants_score(
        self,
        direction: str,
        rolling_data: Dict[str, Any],
    ) -> float:
        """
        Gate B: Participant score (soft).

        Returns a float 0.0–1.0 based on unique participant count.
        """
        bid_participants_window = rolling_data.get(KEY_BID_PARTICIPANTS_5M)
        ask_participants_window = rolling_data.get(KEY_ASK_PARTICIPANTS_5M)

        if direction == "LONG":
            window = bid_participants_window
        else:
            window = ask_participants_window

        if not window or window.count < 1:
            return 0.5  # Can't evaluate — neutral

        current_participants = window.values[-1]
        return min(1.0, current_participants / 10.0)

    def _gate_c_vol_score(
        self,
        signal_type: str,
        vol_ratio: float,
    ) -> float:
        """
        Gate C: Volume score (soft).

        For breach signals: volume/depth ratio indicates real consumption.
        For bounce signals: no volume requirement.
        """
        if signal_type.startswith("STACK_BREACH"):
            return min(1.0, vol_ratio / 1.0)
        else:
            return 1.0

    def _gate_d_spread_score(
        self,
        spread: float,
        avg_spread: float,
    ) -> float:
        """
        Gate D: Spread score (soft).

        Returns a float 0.0–1.0 based on current vs average spread.
        Lower spread ratio = higher score.
        """
        if avg_spread <= 0:
            return 0.5
        spread_ratio = spread / avg_spread
        return max(0.0, 1.0 - (spread_ratio - 1.0) / 2.0)

    # ------------------------------------------------------------------
    # Metric helpers
    # ------------------------------------------------------------------

    def _compute_vol_ratio(self, rolling_data: Dict[str, Any]) -> float:
        """
        Compute volume ratio: current volume / average volume.
        """
        vol_window = rolling_data.get(KEY_VOLUME_5M)
        if vol_window and vol_window.count > 0:
            current = vol_window.latest
            avg = vol_window.mean
            if current is not None and avg is not None and avg > 0:
                return current / avg
        return 0.5  # Neutral default

    def _compute_spread(self, rolling_data: Dict[str, Any]) -> float:
        """Get current spread from rolling data."""
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        if spread_window and spread_window.count > 0:
            return spread_window.values[-1]
        return 0.0

    def _compute_avg_spread(self, rolling_data: Dict[str, Any]) -> float:
        """Get average spread from rolling data."""
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        if spread_window and spread_window.count > 0:
            return sum(spread_window.values) / len(spread_window.values)
        return 0.0

    def _compute_avg_level_size(self, rolling_data: Dict[str, Any]) -> float:
        """
        Compute median level size = total depth / number of levels.
        Uses bid side as the reference. Median is more robust than mean
        against outlier levels that could skew the average.

        Returns 0.0 if data is insufficient.
        """
        depth_bid_size = rolling_data.get(KEY_DEPTH_BID_SIZE_5M)
        depth_bid_levels = rolling_data.get(KEY_DEPTH_BID_LEVELS_5M)

        if (depth_bid_size and depth_bid_size.count > 0
                and depth_bid_levels and depth_bid_levels.count > 0):
            total_bid = depth_bid_size.values[-1]
            num_levels = depth_bid_levels.values[-1]
            # Minimum level count check: need at least 3 levels for stable median
            if num_levels < 3 or total_bid <= 0:
                return 0.0
            return total_bid / num_levels

        return 0.0  # Can't compute

    # ------------------------------------------------------------------
    # Confidence model (5 components, weighted sum to 1.0)
    # ------------------------------------------------------------------

    def _compute_confidence(
        self, signal_type, direction, sis_bid, sis_ask, bid_roc, ask_roc,
        vol_ratio, spread, avg_spread, rolling_data, data, params, regime,
        gex_calc, depth_score=None,
    ):
        """Combine all factors into a single confidence score — 5 weighted components.

        Returns (confidence: float, breakdown: dict).
        """
        # Direction-specific values
        if direction == "LONG":
            sis = sis_bid
            roc = bid_roc
        else:
            sis = sis_ask
            roc = ask_roc

        # c1: SIS intensity (weight 0.35) — main anchor
        c1 = min(1.0, sis / 8.0)  # scales 0→1 as SIS grows from 0→8

        # c2: ROC magnitude (weight 0.25) — urgency of stack change
        c2 = min(1.0, abs(roc) / 2.0)  # scales 0→1 as |ROC| grows from 0→2

        # c3: Volume confirmation (weight 0.15)
        c3 = normalize(vol_ratio, 0.0, 2.0)

        # c4: Spread tightness (weight 0.10)
        if avg_spread > 0:
            spread_ratio = spread / avg_spread
            c4 = max(0.0, 1.0 - (spread_ratio - 1.0) / 2.0)
        else:
            c4 = 0.5

        # c5: Participant diversity (weight 0.15)
        bid_part_window = rolling_data.get(KEY_BID_PARTICIPANTS_5M)
        ask_part_window = rolling_data.get(KEY_ASK_PARTICIPANTS_5M)
        if direction == "LONG":
            part_window = bid_part_window
        else:
            part_window = ask_part_window

        if part_window and part_window.count >= 1:
            current_parts = part_window.values[-1]
            c5 = min(1.0, current_parts / 10.0)  # scales 0→1 as participants grow from 0→10
        else:
            c5 = 0.5  # neutral when no data

        # Weighted average
        confidence = (c1 * 0.35 + c2 * 0.25 + c3 * 0.15 + c4 * 0.10 + c5 * 0.15)
        breakdown = {
            "c1_sis": round(c1, 3),
            "c2_roc": round(c2, 3),
            "c3_volume": round(c3, 3),
            "c4_spread": round(c4, 3),
            "c5_participants": round(c5, 3),
        }
        return min(1.0, max(0.0, confidence)), breakdown
