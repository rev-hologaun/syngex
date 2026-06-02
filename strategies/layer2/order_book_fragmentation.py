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

This is a **filter-style structural integrity engine** — it produces graded signal strength
based on wall fragility and decay, not binary pass/fail.

Signal strength per type:
    strength = fragility_component + decay_component (continuous 0–1)
    signal_strength = strength * 0.5 + wall * 0.15 + void * 0.15 + vol * 0.10 + spread * 0.10
    Emit when signal_strength >= 0.28 and fragility_strength >= 0.2

Confidence model (6 components, sum to 1.0):
    1. Fragility magnitude        (0.0–0.30)
    2. Decay velocity             (0.0–0.20)
    3. Wall significance          (0.0–0.10)
    4. VAMP validation            (0.0–0.10)
    5. Volume confirmation        (0.0–0.10)
    6. Spread tightness           (0.0–0.20)
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

MIN_CONFIDENCE = 0.25


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))


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
        or empty list when scores are too low or no clear signal.
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

        # 2. Determine signal direction and type (continuous strengths)
        frag_threshold = params.get("frag_threshold", 0.5)
        decay_threshold = params.get("decay_threshold", -0.1)
        robust_threshold = params.get("robust_threshold", 0.3)

        # Compute continuous strength for each of the 4 signal types
        # Spoof LONG: fragile ask wall (high frag_ask, decay < threshold)
        spoof_long_strength = 0.0
        if current_frag_ask > robust_threshold and current_decay_ask < decay_threshold:
            spoof_long_strength = (current_frag_ask - robust_threshold) / (frag_threshold - robust_threshold)
            # Decay urgency: more negative decay = stronger signal
            decay_magnitude = abs(current_decay_ask)
            spoof_long_strength *= min(1.0, decay_magnitude / max(0.01, abs(decay_threshold)))

        # Spoof SHORT: fragile bid wall
        spoof_short_strength = 0.0
        if current_frag_bid > robust_threshold and current_decay_bid < decay_threshold:
            spoof_short_strength = (current_frag_bid - robust_threshold) / (frag_threshold - robust_threshold)
            decay_magnitude = abs(current_decay_bid)
            spoof_short_strength *= min(1.0, decay_magnitude / max(0.01, abs(decay_threshold)))

        # Robust LONG: robust bid wall (low frag_bid, decay > threshold)
        robust_long_strength = 0.0
        if current_frag_bid < frag_threshold and current_decay_bid > decay_threshold:
            robust_long_strength = (frag_threshold - current_frag_bid) / (frag_threshold - robust_threshold)
            decay_magnitude = abs(current_decay_bid)
            robust_long_strength *= min(1.0, decay_magnitude / max(0.01, abs(decay_threshold)))

        # Robust SHORT: robust ask wall
        robust_short_strength = 0.0
        if current_frag_ask < frag_threshold and current_decay_ask > decay_threshold:
            robust_short_strength = (frag_threshold - current_frag_ask) / (frag_threshold - robust_threshold)
            decay_magnitude = abs(current_decay_ask)
            robust_short_strength *= min(1.0, decay_magnitude / max(0.01, abs(decay_threshold)))

        # Find the strongest signal
        candidates = [
            ("SPOOF_LONG", "LONG", spoof_long_strength, current_decay_ask),
            ("SPOOF_SHORT", "SHORT", spoof_short_strength, current_decay_bid),
            ("ROBUST_LONG", "LONG", robust_long_strength, current_decay_bid),
            ("ROBUST_SHORT", "SHORT", robust_short_strength, current_decay_ask),
        ]
        candidates.sort(key=lambda x: x[2], reverse=True)
        signal_type, direction, strength, decay_strength = candidates[0]

        # Emit only if strongest signal exceeds minimum strength
        if strength < 0.2:
            return []

        # 3. Compute vol_ratio, spread, and avg_wall_size for scoring
        vol_ratio = self._compute_vol_ratio(rolling_data)
        spread = self._compute_spread(rolling_data)
        avg_spread = self._compute_avg_spread(rolling_data)
        avg_wall_size = self._compute_avg_wall_size(rolling_data)

        # 4. Compute soft scores (replaces hard gates)
        wall_score = self._gate_a_wall_score(direction, avg_wall_size, rolling_data)
        void_score = self._gate_b_void_score(signal_type, direction, rolling_data)
        vol_score = self._gate_c_vol_score(signal_type, vol_ratio)
        spread_score = self._gate_d_spread_score(spread, avg_spread)

        # 5. Combine into signal_strength
        signal_strength = (
            strength * 0.5
            + wall_score * 0.15
            + void_score * 0.15
            + vol_score * 0.10
            + spread_score * 0.10
        )

        if signal_strength < 0.28:
            logger.debug(
                "OB Fragmentation: signal_strength %.4f below threshold 0.28 for %s (%s)",
                signal_strength, direction, signal_type,
            )
            return []

        # 6. Compute confidence (6-component model)
        confidence, conf_breakdown = self._compute_confidence(
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
                "signal_strength": round(signal_strength, 4),
                "wall_score": round(wall_score, 4),
                "void_score": round(void_score, 4),
                "vol_score": round(vol_score, 4),
                "spread_score": round(spread_score, 4),
                "confidence_breakdown": conf_breakdown,
            },
        )]

    # ------------------------------------------------------------------
    # Gate helpers
    # ------------------------------------------------------------------

    def _gate_a_wall_score(
        self,
        direction: str,
        avg_wall_size: float,
        rolling_data: Dict[str, Any],
    ) -> float:
        """
        Gate A: Wall significance score (0.0–1.0).

        Scales from 0→1 as the wall grows from 0→10× the average level size.
        Returns 0.5 (neutral) when data is unavailable.
        """
        if avg_wall_size <= 0:
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

        wall_ratio = current_wall / avg_wall_size
        return min(1.0, wall_ratio / 10.0)

    def _gate_b_void_score(
        self,
        signal_type: str,
        direction: str,
        rolling_data: Dict[str, Any],
    ) -> float:
        """
        Gate B: VAMP void score (0.0–1.0).

        VAMP deviation confirms price is moving into the vacuum (spoof breach)
        or approaching the wall (robust bounce). Returns 0.5 (neutral) when
        no VAMP data is available.
        """
        vamp_mid_dev_window = rolling_data.get(KEY_VAMP_MID_DEV_5M)
        if not vamp_mid_dev_window or vamp_mid_dev_window.count < 1:
            return 0.5  # neutral when no data

        vamp_mid_dev = vamp_mid_dev_window.values[-1]

        if signal_type.startswith("SPOOF"):
            # Spoof: price moving into vacuum
            if direction == "LONG":
                # positive vamp_mid_dev = price moving up = good for LONG spoof
                return max(0.0, min(1.0, 0.5 + vamp_mid_dev * 500))
            else:
                # negative vamp_mid_dev = price moving down = good for SHORT spoof
                return max(0.0, min(1.0, 0.5 - vamp_mid_dev * 500))
        else:
            # Robust: price approaching wall
            if direction == "LONG":
                # negative vamp_mid_dev = price near bid wall = good for ROBUST LONG
                return max(0.0, min(1.0, 0.5 - vamp_mid_dev * 500))
            else:
                # positive vamp_mid_dev = price near ask wall = good for ROBUST SHORT
                return max(0.0, min(1.0, 0.5 + vamp_mid_dev * 500))

    def _gate_c_vol_score(
        self,
        signal_type: str,
        vol_ratio: float,
    ) -> float:
        """
        Gate C: Volume/depth ratio score (0.0–1.0).

        Low vol is good for spoof (vol_ratio=0.0 → score=1.0).
        High vol is good for robust (vol_ratio=1.5 → score=1.0).
        """
        if signal_type.startswith("SPOOF"):
            # Low vol is good for spoof → vol_score = max(0.0, 1.0 - vol_ratio / 0.5)
            # vol_ratio=0.0 → 1.0, vol_ratio=0.5 → 0.0
            return max(0.0, 1.0 - vol_ratio / 0.5)
        else:
            # High vol is good for robust → vol_score = min(1.0, vol_ratio / 1.5)
            # vol_ratio=0.0 → 0.0, vol_ratio=1.5 → 1.0
            return min(1.0, vol_ratio / 1.5)

    def _gate_d_spread_score(
        self,
        spread: float,
        avg_spread: float,
    ) -> float:
        """
        Gate D: Spread tightness score (0.0–1.0).

        Tighter spread → higher score. Returns 0.5 (neutral) when
        average spread can't be computed.
        """
        if avg_spread <= 0:
            return 0.5  # neutral
        spread_ratio = spread / avg_spread
        # spread_score = max(0.0, 1.0 - (spread_ratio - 1.0) / 2.0)
        #   spread_ratio=1.0 → 1.0, spread_ratio=3.0 → 0.0
        return max(0.0, 1.0 - (spread_ratio - 1.0) / 2.0)

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
        self, signal_type, direction, frag_bid, frag_ask, decay_bid, decay_ask,
        vol_ratio, spread, avg_spread, rolling_data, params, avg_wall_size,
        depth_score=None,
    ):
        """Combine all factors into a single confidence score — 6 weighted components.

        Returns (confidence: float, breakdown: dict) with breakdown containing
        c1_fragility, c2_decay, c3_wall, c4_vamp, c5_volume, c6_spread.
        """
        frag_threshold = params.get("frag_threshold", 0.5)

        # Select frag/decay based on signal type and direction
        if signal_type.startswith("SPOOF"):
            frag = frag_ask if direction == "LONG" else frag_bid
            decay = decay_ask if direction == "LONG" else decay_bid
        else:
            frag = frag_bid if direction == "LONG" else frag_ask
            decay = decay_bid if direction == "LONG" else decay_bid

        # 1. Fragility magnitude: frag from frag_threshold→1.0 (SPOOF) or 0→frag_threshold (ROBUST)
        if signal_type.startswith("SPOOF"):
            c1 = normalize(frag, frag_threshold, 1.0)
        else:
            c1 = 1.0 - normalize(frag, 0.0, frag_threshold)

        # 2. Decay velocity: abs(decay) from 0→0.5, higher = higher
        c2 = normalize(abs(decay), 0.0, 0.5)

        # 3. Wall significance: wall_ratio from 3→10, higher = higher
        wall_ratio = 1.0
        if avg_wall_size > 0:
            top_wall_key = KEY_TOP_WALL_BID_SIZE_5M if direction == "LONG" else KEY_TOP_WALL_ASK_SIZE_5M
            top_wall_rw = rolling_data.get(top_wall_key)
            if top_wall_rw and top_wall_rw.count > 0:
                current_wall = top_wall_rw.values[-1]
                if current_wall > 0:
                    wall_ratio = current_wall / avg_wall_size
        c3 = normalize(wall_ratio, 3.0, 10.0)

        # 4. VAMP validation: vamp_mid_dev from -0.001→0.001, alignment = 1 if matches
        vamp_mid_dev_window = rolling_data.get(KEY_VAMP_MID_DEV_5M)
        if vamp_mid_dev_window and vamp_mid_dev_window.count >= 1:
            vamp_mid_dev = vamp_mid_dev_window.values[-1]
            if signal_type.startswith("SPOOF"):
                if direction == "LONG":
                    c4 = max(0.0, min(1.0, 0.5 + vamp_mid_dev * 500))
                else:
                    c4 = max(0.0, min(1.0, 0.5 - vamp_mid_dev * 500))
            else:
                if direction == "LONG":
                    c4 = max(0.0, min(1.0, 0.5 - vamp_mid_dev * 500))
                else:
                    c4 = max(0.0, min(1.0, 0.5 + vamp_mid_dev * 500))
        else:
            c4 = 0.5

        # 5. Volume confirmation: vol_ratio from 0→2.0, higher = higher
        c5 = normalize(vol_ratio, 0.0, 2.0)

        # 6. Spread tightness: spread ratio to avg spread, tighter = higher
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        if spread_window and spread_window.count > 0 and spread_window.mean > 0:
            spread_ratio = spread / spread_window.mean
            c6 = max(0.0, 1.0 - (spread_ratio - 1.0) / 2.0)
        else:
            c6 = 0.5

        # Weighted average
        confidence = (c1 * 0.30 + c2 * 0.20 + c3 * 0.10 + c4 * 0.10 + c5 * 0.10 + c6 * 0.20)
        breakdown = {
            "c1_fragility": round(c1, 3),
            "c2_decay": round(c2, 3),
            "c3_wall": round(c3, 3),
            "c4_vamp": round(c4, 3),
            "c5_volume": round(c5, 3),
            "c6_spread": round(c6, 3),
        }
        return min(1.0, max(0.0, confidence)), breakdown