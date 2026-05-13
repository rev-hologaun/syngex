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

Hard gates (all must pass):
    Gate A: Stack size >= 3× average level size (significant stack)
    Gate B: >= 2 unique participants (anti-spoof)
    Gate C: Volume/depth ratio confirms real consumption for breach signals

Confidence model (5 components, sum to 1.0):
    1. Stack intensity magnitude    (0.0–0.35)
    2. Stack decay velocity         (0.0–0.25)
    3. Participant diversity        (0.0–0.15)
    4. Volume confirmation          (0.0–0.15)
    5. Spread tightness             (0.0–0.10)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_DEPTH_BID_LEVEL_AVG_5M,
    KEY_DEPTH_ASK_LEVEL_AVG_5M,
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

MIN_CONFIDENCE = 0.15


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

        min_data = params.get("min_data_points", 10)
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

        # 2. Determine signal direction and type
        sis_threshold = params.get("sis_threshold", 4.0)
        magnitude_factor = params.get("magnitude_factor", 3.0)
        min_participants = params.get("min_participants", 2)
        price_tolerance = params.get("price_tolerance", 0.001)
        roc_threshold = params.get("roc_threshold", -0.5)

        # Stack Bounce LONG — massive bid stack holding
        stack_bounce_long = current_sis_bid > sis_threshold

        # Stack Breach SHORT — massive ask stack being eaten
        stack_breach_short = (
            current_sis_ask > sis_threshold
            and current_ask_roc < roc_threshold
        )

        # Stack Bounce SHORT — massive ask stack holding
        stack_bounce_short = current_sis_ask > sis_threshold

        # Stack Breach LONG — massive bid stack evaporating
        stack_breach_long = (
            current_sis_bid > sis_threshold
            and current_bid_roc < roc_threshold
        )

        if not stack_bounce_long and not stack_breach_short and not stack_bounce_short and not stack_breach_long:
            return []

        # 3. Compute vol_ratio, spread, and stack significance for gates
        vol_ratio = self._compute_vol_ratio(rolling_data)
        spread = self._compute_spread(rolling_data)
        avg_spread = self._compute_avg_spread(rolling_data)
        avg_level_size = self._compute_avg_level_size(rolling_data)

        # 4. Build candidate signals and pick the strongest
        candidates = []

        if stack_bounce_long:
            candidates.append(("STACK_BOUNCE_LONG", "LONG", current_sis_bid, 0.0))
        if stack_breach_short:
            candidates.append(("STACK_BREACH_SHORT", "SHORT", current_sis_ask, abs(current_ask_roc)))
        if stack_bounce_short:
            candidates.append(("STACK_BOUNCE_SHORT", "SHORT", current_sis_ask, 0.0))
        if stack_breach_long:
            candidates.append(("STACK_BREACH_LONG", "LONG", current_sis_bid, abs(current_bid_roc)))

        if not candidates:
            return []

        # Pick the strongest signal by combined strength
        candidates.sort(key=lambda x: x[2] + x[3], reverse=True)
        signal_type, direction, strength, roc_strength = candidates[0]

        # 5. Apply HARD GATES
        # Gate A: Magnitude — stack must be >= 3× average level size
        gate_a = self._gate_a_magnitude(
            direction, magnitude_factor, avg_level_size, rolling_data
        )
        if not gate_a:
            logger.debug(
                "Stacking: Gate A failed — stack not significant enough for %s",
                direction,
            )
            return []

        # Gate B: Participant gate — >= 2 unique participants
        gate_b = self._gate_b_participants(
            direction, min_participants, rolling_data
        )
        if not gate_b:
            logger.debug(
                "Stacking: Gate B failed — insufficient participants for %s (%s)",
                direction, signal_type,
            )
            return []

        # Gate C: Volume/depth ratio for breach signals
        gate_c = self._gate_c_vol_depth(signal_type, vol_ratio, params)
        if not gate_c:
            logger.debug(
                "Stacking: Gate C failed — vol/depth mismatch for %s (%s)",
                direction, signal_type,
            )
            return []

        # Gate D: Spread tightness
        gate_d = self._gate_d_spread(spread, avg_spread, params)
        if not gate_d:
            logger.debug(
                "Stacking: Gate D failed — spread too wide for %s",
                direction,
            )
            return []

        # 6. Compute confidence (5-component model)
        confidence = self._compute_confidence(
            signal_type, direction,
            current_sis_bid, current_sis_ask,
            current_bid_roc, current_ask_roc,
            vol_ratio, spread, avg_spread,
            rolling_data, data, params, regime, gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 7. Build signal with entry/stop/target
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
                "sis_bid": round(current_sis_bid, 4),
                "sis_ask": round(current_sis_ask, 4),
                "bid_roc": round(current_bid_roc, 6),
                "ask_roc": round(current_ask_roc, 6),
                "vol_ratio": round(vol_ratio, 4),
                "spread": round(spread, 4),
                "avg_spread": round(avg_spread, 4),
                "gates": {
                    "A_magnitude": gate_a,
                    "B_participants": gate_b,
                    "C_vol_depth": gate_c,
                    "D_spread": gate_d,
                },
            },
        )]

    # ------------------------------------------------------------------
    # Gate helpers
    # ------------------------------------------------------------------

    def _gate_a_magnitude(
        self,
        direction: str,
        magnitude_factor: float,
        avg_level_size: float,
        rolling_data: Dict[str, Any],
    ) -> bool:
        """
        Gate A: Stack magnitude.

        The stack on the signal side must be >= magnitude_factor ×
        average level size. Ensures we're looking at a real stack, not noise.
        """
        if avg_level_size <= 0:
            return True  # Can't compute — pass

        top_wall_key = (
            KEY_TOP_WALL_BID_SIZE_5M if direction == "LONG" else KEY_TOP_WALL_ASK_SIZE_5M
        )
        top_wall_rw = rolling_data.get(top_wall_key)

        if not top_wall_rw or top_wall_rw.count < 1:
            return True  # Can't evaluate — pass

        current_wall = top_wall_rw.values[-1]
        if current_wall <= 0:
            return False

        return current_wall >= avg_level_size * magnitude_factor

    def _gate_b_participants(
        self,
        direction: str,
        min_participants: int,
        rolling_data: Dict[str, Any],
    ) -> bool:
        """
        Gate B: Participant diversity.

        The stack must have >= min_participants unique participants
        to avoid single-player spoofing.
        """
        bid_participants_window = rolling_data.get(KEY_BID_PARTICIPANTS_5M)
        ask_participants_window = rolling_data.get(KEY_ASK_PARTICIPANTS_5M)

        if direction == "LONG":
            window = bid_participants_window
        else:
            window = ask_participants_window

        if not window or window.count < 1:
            return True  # Can't evaluate — pass

        current_participants = window.values[-1]
        return current_participants >= min_participants

    def _gate_c_vol_depth(
        self,
        signal_type: str,
        vol_ratio: float,
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate C: Volume/depth ratio.

        For breach signals: confirm volume/depth ratio indicates real
        consumption, not just evaporation.
        """
        if signal_type.startswith("STACK_BREACH"):
            # Breach signals: need evidence of real volume consumption
            threshold = params.get("vol_ratio_breach", 0.15)
            return vol_ratio >= threshold
        else:
            # Bounce signals: no volume requirement needed
            return True

    def _gate_d_spread(
        self,
        spread: float,
        avg_spread: float,
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate D: Spread tightness.

        Current spread must be < max_spread_mult × average spread.
        """
        max_spread_mult = params.get("max_spread_mult", 2.0)
        if avg_spread <= 0:
            return True  # Can't evaluate — pass
        return spread < avg_spread * max_spread_mult

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
        Compute average level size = total depth / number of levels.
        Uses bid side as the reference.
        """
        depth_bid_size = rolling_data.get(KEY_DEPTH_BID_SIZE_5M)
        depth_bid_levels = rolling_data.get(KEY_DEPTH_BID_LEVELS_5M)

        if (depth_bid_size and depth_bid_size.count > 0
                and depth_bid_levels and depth_bid_levels.count > 0):
            total_bid = depth_bid_size.values[-1]
            num_levels = depth_bid_levels.values[-1]
            if num_levels > 0 and total_bid > 0:
                return total_bid / num_levels

        return 0.0  # Can't compute

    # ------------------------------------------------------------------
    # Confidence model (5 components, sum to 1.0)
    # ------------------------------------------------------------------

    def _compute_confidence(
        self, signal_type, direction, sis_bid, sis_ask, bid_roc, ask_roc,
        vol_ratio, spread, avg_spread, rolling_data, data, params, regime,
        gex_calc, depth_score=None,
    ):
        """Combine all factors into a single confidence score — 5 components.

        Returns 0.0–1.0.
        """
        intensity_threshold = params.get("intensity_threshold", 0.5)

        # Select based on signal type and direction
        if signal_type.startswith("SPOOF"):
            intensity = top_wall_size
            decay_val = decay
        else:
            intensity = avg_level_size / top_wall_size if top_wall_size > 0 else 1.0
            decay_val = decay

        # 1. Intensity: intensity from threshold→2.0, higher = higher
        c1 = normalize(intensity, intensity_threshold, 2.0)

        # 2. Decay: abs(decay_val) from 0→0.5, higher = higher
        c2 = normalize(abs(decay_val), 0.0, 0.5)

        # 3. Wall significance: wall_ratio from 1→10, higher = higher
        wall_ratio = top_wall_size / avg_level_size if avg_level_size > 0 else 1.0
        c3 = normalize(wall_ratio, 1.0, 10.0)

        # 4. Volume: vol_ratio from 0→2.0, higher = higher
        c4 = normalize(vol_ratio, 0.0, 2.0)

        # 5. Spread stability: spread_ratio from 0→1.5, lower = more stable, invert
        spread_ratio = spread / avg_spread if avg_spread > 0 else 1.0
        c5 = 1.0 - normalize(spread_ratio, 0.0, 1.5)

        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))