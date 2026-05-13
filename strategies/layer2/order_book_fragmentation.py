"""
strategies/layer2/order_book_fragmentation.py — Order Book Fragmentation

Structural integrity strategy that distinguishes between fragile "spoof" walls
(massive size, few participants) and robust "anchor" walls (massive size, many
participants across multiple exchanges).

Core concept:
    Fragile ask walls evaporating = bullish breakout (fake resistance gone)
    Fragile bid walls evaporating = bearish breakdown (fake support gone)
    Robust bid walls holding = bullish bounce (real support)
    Robust ask walls holding = bearish rejection (real resistance)

Signal types:
    SPOOF BREACH LONG:  Fragile Ask Wall evaporates → breakout
    SPOOF BREACH SHORT: Fragile Bid Wall evaporates → breakdown
    ROBUST BOUNCE LONG:  Robust Bid Wall holds → bounce
    ROBUST BOUNCE SHORT: Robust Ask Wall holds → rejection

Hard gates (all must pass):
    Gate A: Wall size >= 3× average level size (significant wall)
    Gate B: VAMP deviation confirms price movement (the "Void" check)
    Gate C: Volume/depth ratio matches signal type (low for spoof, high for robust)

Confidence model (6 components, sum to 1.0):
    1. Fragility magnitude        (0.0–0.30)
    2. Decay velocity             (0.0–0.25)
    3. Wall significance          (0.0–0.15)
    4. VAMP validation            (0.0–0.15)
    5. Volume confirmation        (0.0–0.10)
    6. Spread tightness           (0.0–0.05)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_FRAGILITY_BID_5M,
    KEY_FRAGILITY_ASK_5M,
    KEY_DECAY_VELOCITY_BID_5M,
    KEY_DECAY_VELOCITY_ASK_5M,
    KEY_TOP_WALL_BID_SIZE_5M,
    KEY_TOP_WALL_ASK_SIZE_5M,
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_ASK_SIZE_5M,
    KEY_DEPTH_BID_LEVELS_5M,
    KEY_DEPTH_ASK_LEVELS_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_VOLUME_5M,
    KEY_VAMP_5M,
    KEY_VAMP_MID_DEV_5M,
    KEY_VAMP_ROC_5M,
)

logger = logging.getLogger("Syngex.Strategies.OrderBookFragmentation")

MIN_CONFIDENCE = 0.30


class OrderBookFragmentation(BaseStrategy):
    """
    Order Book Fragmentation — structural integrity strategy.

    Distinguishes between fragile "spoof" walls and robust "anchor" walls.
    Trades both the collapse of fake walls (spoof breach) and the bounce
    off real ones (robust bounce).

    SPOOF BREACH LONG:  Fragile Ask Wall evaporates → breakout
    SPOOF BREACH SHORT: Fragile Bid Wall evaporates → breakdown
    ROBUST BOUNCE LONG:  Robust Bid Wall holds → bounce
    ROBUST BOUNCE SHORT: Robust Ask Wall holds → rejection
    """

    strategy_id = "order_book_fragmentation"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for order book fragmentation signal.

        Returns a single LONG or SHORT signal when conditions are met,
        or empty list when gates fail or no clear signal.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params

        # 1. Get fragility and decay from rolling windows
        frag_bid_window = rolling_data.get(KEY_FRAGILITY_BID_5M)
        frag_ask_window = rolling_data.get(KEY_FRAGILITY_ASK_5M)
        decay_bid_window = rolling_data.get(KEY_DECAY_VELOCITY_BID_5M)
        decay_ask_window = rolling_data.get(KEY_DECAY_VELOCITY_ASK_5M)

        if not frag_bid_window or frag_bid_window.count < 5:
            return []
        if not frag_ask_window or frag_ask_window.count < 5:
            return []
        if not decay_bid_window or decay_bid_window.count < 5:
            return []
        if not decay_ask_window or decay_ask_window.count < 5:
            return []

        current_frag_bid = frag_bid_window.values[-1]
        current_frag_ask = frag_ask_window.values[-1]
        current_decay_bid = decay_bid_window.values[-1]
        current_decay_ask = decay_ask_window.values[-1]

        # 2. Determine signal direction and type
        frag_threshold = params.get("frag_threshold", 0.5)
        decay_threshold = params.get("decay_threshold", -0.1)
        wall_significance_mult = params.get("wall_significance_mult", 3.0)
        price_proximity_pct = params.get("price_proximity_pct", 0.001)
        vol_ratio_spoof = params.get("vol_ratio_spoof", 0.1)
        vol_ratio_robust = params.get("vol_ratio_robust", 0.5)
        max_spread_mult = params.get("max_spread_mult", 2.0)

        # Spoof Breach LONG — fragile ask wall evaporating
        spoof_long = (
            current_frag_ask > frag_threshold
            and current_decay_ask < decay_threshold
        )
        # Spoof Breach SHORT — fragile bid wall evaporating
        spoof_short = (
            current_frag_bid > frag_threshold
            and current_decay_bid < decay_threshold
        )
        # Robust Bounce LONG — robust bid wall holding
        robust_long = (
            current_frag_bid < frag_threshold
            and current_decay_bid > decay_threshold
        )
        # Robust Bounce SHORT — robust ask wall holding
        robust_short = (
            current_frag_ask < frag_threshold
            and current_decay_ask > decay_threshold
        )

        if not spoof_long and not spoof_short and not robust_long and not robust_short:
            return []

        # 3. Compute vol_ratio, spread, and wall significance for gates
        vol_ratio = self._compute_vol_ratio(rolling_data)
        spread = self._compute_spread(rolling_data)
        avg_spread = self._compute_avg_spread(rolling_data)
        avg_wall_size = self._compute_avg_wall_size(rolling_data)

        # 4. Build candidate signals and pick the strongest
        candidates = []

        if spoof_long:
            candidates.append(("SPOOF_LONG", "LONG", current_frag_ask, current_decay_ask))
        if spoof_short:
            candidates.append(("SPOOF_SHORT", "SHORT", current_frag_bid, current_decay_bid))
        if robust_long:
            candidates.append(("ROBUST_LONG", "LONG", 1.0 - current_frag_bid, current_decay_bid))
        if robust_short:
            candidates.append(("ROBUST_SHORT", "SHORT", 1.0 - current_frag_ask, current_decay_ask))

        if not candidates:
            return []

        # Pick the strongest signal by combined strength
        candidates.sort(key=lambda x: x[2] + abs(x[3]), reverse=True)
        signal_type, direction, strength, decay_strength = candidates[0]

        # 5. Apply HARD GATES
        # Gate A: Wall significance
        gate_a = self._gate_a_wall_significance(
            direction, wall_significance_mult, avg_wall_size, rolling_data
        )
        if not gate_a:
            logger.debug(
                "OB Fragmentation: Gate A failed — wall not significant enough for %s",
                direction,
            )
            return []

        # Gate B: The "Void" Check — VAMP deviation confirms price movement
        gate_b = self._gate_b_void_check(signal_type, direction, rolling_data)
        if not gate_b:
            logger.debug(
                "OB Fragmentation: Gate B failed — VAMP void check for %s (%s)",
                direction, signal_type,
            )
            return []

        # Gate C: Volume/depth ratio
        gate_c = self._gate_c_vol_depth(signal_type, vol_ratio, params)
        if not gate_c:
            logger.debug(
                "OB Fragmentation: Gate C failed — vol/depth mismatch for %s (%s)",
                direction, signal_type,
            )
            return []

        # Gate D: Spread tightness
        gate_d = self._gate_d_spread(spread, avg_spread, max_spread_mult)
        if not gate_d:
            logger.debug(
                "OB Fragmentation: Gate D failed — spread too wide for %s",
                direction,
            )
            return []

        # 6. Compute confidence (6-component model)
        confidence = self._compute_confidence(
            signal_type, direction,
            current_frag_bid, current_frag_ask,
            current_decay_bid, current_decay_ask,
            vol_ratio, spread, avg_spread,
            rolling_data, params, avg_wall_size,
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
                f"{signal_type} {direction}: frag_bid={current_frag_bid:.3f} "
                f"frag_ask={current_frag_ask:.3f} "
                f"decay_bid={current_decay_bid:+.4f} "
                f"decay_ask={current_decay_ask:+.4f}"
            ),
            metadata={
                "signal_type": signal_type,
                "direction": direction,
                "fragility_bid": round(current_frag_bid, 4),
                "fragility_ask": round(current_frag_ask, 4),
                "decay_bid": round(current_decay_bid, 6),
                "decay_ask": round(current_decay_ask, 6),
                "vol_ratio": round(vol_ratio, 4),
                "spread": round(spread, 4),
                "avg_spread": round(avg_spread, 4),
                "gates": {
                    "A_wall_significance": gate_a,
                    "B_void_check": gate_b,
                    "C_vol_depth": gate_c,
                    "D_spread": gate_d,
                },
            },
        )]

    # ------------------------------------------------------------------
    # Gate helpers
    # ------------------------------------------------------------------

    def _gate_a_wall_significance(
        self,
        direction: str,
        wall_significance_mult: float,
        avg_wall_size: float,
        rolling_data: Dict[str, Any],
    ) -> bool:
        """
        Gate A: Wall significance.

        The wall on the signal side must be >= wall_significance_mult ×
        average level size. Ensures we're looking at a real wall, not noise.
        """
        if avg_wall_size <= 0:
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

        return current_wall >= avg_wall_size * wall_significance_mult

    def _gate_b_void_check(
        self,
        signal_type: str,
        direction: str,
        rolling_data: Dict[str, Any],
    ) -> bool:
        """
        Gate B: The "Void" Check.

        VAMP deviation confirms price is moving into the vacuum (spoof breach)
        or approaching the wall (robust bounce).
        """
        vamp_mid_dev_window = rolling_data.get(KEY_VAMP_MID_DEV_5M)
        if not vamp_mid_dev_window or vamp_mid_dev_window.count < 1:
            return True  # No VAMP data — pass

        vamp_mid_dev = vamp_mid_dev_window.values[-1]

        if signal_type.startswith("SPOOF"):
            # Spoof breach: VAMP should confirm price moving into the vacuum
            # LONG spoof: price moving up into evaporated ask wall
            # SHORT spoof: price moving down into evaporated bid wall
            if direction == "LONG":
                return vamp_mid_dev >= -0.001  # Allow small tolerance
            else:
                return vamp_mid_dev <= 0.001
        else:
            # Robust bounce: VAMP should confirm price approaching the wall
            if direction == "LONG":
                return vamp_mid_dev <= 0.001  # Price near bid wall
            else:
                return vamp_mid_dev >= -0.001

    def _gate_c_vol_depth(
        self,
        signal_type: str,
        vol_ratio: float,
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate C: Volume/depth ratio.

        Low ratio (< 0.1) for spoof breach — liquidity evaporated, not consumed.
        High ratio (> 0.5) for robust bounce — wall being consumed but holding.
        """
        if signal_type.startswith("SPOOF"):
            threshold = params.get("vol_ratio_spoof", 0.1)
            return vol_ratio < threshold
        else:  # ROBUST
            threshold = params.get("vol_ratio_robust", 0.5)
            return vol_ratio > threshold

    def _gate_d_spread(
        self,
        spread: float,
        avg_spread: float,
        max_spread_mult: float,
    ) -> bool:
        """
        Gate D: Spread tightness.

        Current spread must be < max_spread_mult × average spread.
        Scalp must be profitable after spread cost.
        """
        if avg_spread <= 0:
            return True  # Can't evaluate — pass
        return spread < avg_spread * max_spread_mult

    # ------------------------------------------------------------------
    # Metric helpers
    # ------------------------------------------------------------------

    def _compute_vol_ratio(self, rolling_data: Dict[str, Any]) -> float:
        """
        Compute volume ratio: current volume / average volume.
        Low ratio (< 0.1) indicates spoof (no real trades).
        High ratio (> 0.5) indicates real wall absorbing trades.
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

    def _compute_avg_wall_size(self, rolling_data: Dict[str, Any]) -> float:
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
    # Confidence model (6 components, sum to 1.0)
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        signal_type: str,
        direction: str,
        frag_bid: float,
        frag_ask: float,
        decay_bid: float,
        decay_ask: float,
        vol_ratio: float,
        spread: float,
        avg_spread: float,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
        avg_wall_size: float,
    ) -> float:
        """
        Compute 6-component confidence score.

        Returns 0.0–1.0.
        """
        frag_threshold = params.get("frag_threshold", 0.5)
        decay_threshold = params.get("decay_threshold", -0.1)

        # Select the relevant fragility/decay based on signal type and direction
        if signal_type.startswith("SPOOF"):
            frag = frag_ask if direction == "LONG" else frag_bid
            decay = decay_ask if direction == "LONG" else decay_bid
        else:  # ROBUST
            frag = frag_bid if direction == "LONG" else frag_ask
            decay = decay_bid if direction == "LONG" else decay_ask

        # 1. Fragility magnitude (0.0–0.30)
        # How extreme the fragility is — at threshold = baseline, above/below = bonus
        conf_frag = 0.0
        if signal_type.startswith("SPOOF"):
            # Higher fragility = stronger signal (wall is fake)
            if frag > frag_threshold:
                conf_frag = min(0.30, 0.30 * min(1.0, (frag - frag_threshold) / (1.0 - frag_threshold) + 0.5))
        else:
            # Lower fragility = stronger signal (wall is robust)
            if frag < frag_threshold:
                conf_frag = min(0.30, 0.30 * min(1.0, (frag_threshold - frag) / frag_threshold + 0.5))

        # 2. Decay velocity (0.0–0.25)
        # How fast the wall is evaporating (spoof) or holding (robust)
        conf_decay = 0.0
        if signal_type.startswith("SPOOF"):
            # Negative decay = wall evaporating
            if decay < decay_threshold:
                # More negative = stronger signal
                conf_decay = min(0.25, 0.25 * min(1.0, abs(decay - decay_threshold) / abs(decay_threshold) + 0.5))
        else:
            # Positive decay = wall growing/stable
            if decay > decay_threshold:
                conf_decay = min(0.25, 0.25 * min(1.0, decay / abs(decay_threshold) + 0.5))

        # 3. Wall significance (0.0–0.15)
        # How significant the wall is relative to average level size
        conf_wall = 0.05  # baseline (gate A already passed)
        if avg_wall_size > 0:
            top_wall_key = (
                KEY_TOP_WALL_BID_SIZE_5M if direction == "LONG" else KEY_TOP_WALL_ASK_SIZE_5M
            )
            top_wall_rw = rolling_data.get(top_wall_key)
            if top_wall_rw and top_wall_rw.count > 0:
                current_wall = top_wall_rw.values[-1]
                if current_wall > 0:
                    wall_ratio = current_wall / avg_wall_size
                    # Scale: at 3× = baseline, at 10× = max
                    conf_wall = 0.05 + 0.10 * min(1.0, (wall_ratio - 3.0) / 7.0)

        # 4. VAMP validation (0.0–0.15)
        # VAMP direction confirms the signal
        conf_vamp = 0.05  # baseline (gate B already passed)
        vamp_mid_dev_window = rolling_data.get(KEY_VAMP_MID_DEV_5M)
        if vamp_mid_dev_window and vamp_mid_dev_window.count > 0:
            vamp_mid_dev = vamp_mid_dev_window.values[-1]
            if signal_type.startswith("SPOOF"):
                if direction == "LONG" and vamp_mid_dev > 0:
                    conf_vamp = 0.15
                elif direction == "SHORT" and vamp_mid_dev < 0:
                    conf_vamp = 0.15
                elif abs(vamp_mid_dev) < 0.0005:
                    conf_vamp = 0.10
            else:
                if direction == "LONG" and vamp_mid_dev <= 0:
                    conf_vamp = 0.15
                elif direction == "SHORT" and vamp_mid_dev >= 0:
                    conf_vamp = 0.15
                elif abs(vamp_mid_dev) < 0.0005:
                    conf_vamp = 0.10

        # 5. Volume confirmation (0.0–0.10)
        # Volume/depth ratio matches signal type
        conf_volume = 0.05  # baseline (gate C already passed)
        if signal_type.startswith("SPOOF"):
            vol_threshold = params.get("vol_ratio_spoof", 0.1)
            if vol_ratio < vol_threshold:
                conf_volume = 0.05 + 0.05 * min(1.0, (vol_threshold - vol_ratio) / vol_threshold)
        else:
            vol_threshold = params.get("vol_ratio_robust", 0.5)
            if vol_ratio > vol_threshold:
                conf_volume = 0.05 + 0.05 * min(1.0, (vol_ratio - vol_threshold) / vol_threshold)

        # 6. Spread tightness (0.0–0.05)
        # Spread tight relative to average
        conf_spread = 0.025  # baseline (gate D already passed)
        if avg_spread > 0 and spread > 0:
            spread_ratio = spread / avg_spread
            if spread_ratio <= 1.0:
                conf_spread = 0.05
            elif spread_ratio < 2.0:
                conf_spread = 0.025 + 0.025 * (2.0 - spread_ratio)

        # Sum all components
        confidence = (
            conf_frag + conf_decay + conf_wall +
            conf_vamp + conf_volume + conf_spread
        )
        return min(1.0, max(0.0, confidence))
