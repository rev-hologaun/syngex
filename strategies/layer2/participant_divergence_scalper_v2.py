"""
strategies/layer2/participant_divergence_scalper.py — Participant Divergence Scalper

Microstructure scalping strategy that distinguishes between fragile "spoof" walls
and robust multi-participant liquidity.

Core concept: Spoof walls have massive size but few participants (1 player).
Robust walls have massive size AND many participants across multiple exchanges.

We trade both:
- The collapse of fake walls (spoof breach)
- The bounce off real ones (robust bounce)

Signal types:
    SPOOF BREACH (SHORT): Fragile Ask Wall evaporates → scalp the vacuum
    SPOOF BREACH (LONG):  Fragile Bid Wall evaporates → scalp the vacuum
    ROBUST BOUNCE (LONG):  Robust Bid Wall holds → scalp the bounce
    ROBUST BOUNCE (SHORT): Robust Ask Wall holds → scalp the bounce

This is a **filter-style microstructure engine** — it produces graded signal strength
based on wall fragility/decay, not binary pass/fail.

Signal strength per type:
    strength = fragility_component + decay_component (continuous 0–1)
    signal_strength = strength*0.6 + wall*0.15 + vol*0.15 + spread*0.10 + vamp*0.05
    Emit when signal_strength >= 0.30 and fragility_strength >= 0.2

Confidence model (7 components, sum to 1.0):
    1. Fragility strength        (0.0–0.30)
    2. Decay velocity            (0.0–0.20)
    3. Wall size significance    (0.0–0.15)
    4. Volume confirmation       (0.0–0.10)
    5. Spread tightness          (0.0–0.10)
    6. VAMP validation           (0.0–0.10)
    7. GEX regime alignment      (0.0–0.10)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

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
    KEY_VAMP_LEVELS,
)

logger = logging.getLogger("Syngex.Strategies.ParticipantDivergenceScalperV2")

MIN_CONFIDENCE = 0.05


class ParticipantDivergenceScalperV2(BaseStrategy):
    """
    Participant Divergence Scalper — microstructure scalping strategy.

    Distinguishes between fragile "spoof" walls and robust multi-participant
    liquidity. Trades both the collapse of fake walls and the bounce off real ones.

    SPOOF BREACH (SHORT): Fragile Ask Wall evaporates → scalp the vacuum
    SPOOF BREACH (LONG):  Fragile Bid Wall evaporates → scalp the vacuum
    ROBUST BOUNCE (LONG):  Robust Bid Wall holds → scalp the bounce
    ROBUST BOUNCE (SHORT): Robust Ask Wall holds → scalp the bounce
    """

    strategy_id = "participant_divergence_scalper_v2"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for participant divergence signal.

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

        # 1. Get fragility and decay from rolling windows
        fragility_window = params.get("fragility_window", 5)
        min_frag_data = params.get("min_frag_data_points", 10)

        frag_bid_window = rolling_data.get(KEY_FRAGILITY_BID_5M)
        frag_ask_window = rolling_data.get(KEY_FRAGILITY_ASK_5M)
        decay_bid_window = rolling_data.get(KEY_DECAY_VELOCITY_BID_5M)
        decay_ask_window = rolling_data.get(KEY_DECAY_VELOCITY_ASK_5M)

        if not frag_bid_window or frag_bid_window.count < min_frag_data:
            return []
        if not frag_ask_window or frag_ask_window.count < min_frag_data:
            return []
        if not decay_bid_window or decay_bid_window.count < 5:
            return []
        if not decay_ask_window or decay_ask_window.count < 5:
            return []

        current_frag_bid = frag_bid_window.values[-1]
        current_frag_ask = frag_ask_window.values[-1]
        current_decay_bid = decay_bid_window.values[-1]
        current_decay_ask = decay_ask_window.values[-1]

        # 2. Determine signal direction and type (continuous filter-style)
        fragility_threshold = params.get("fragility_threshold", 0.5)
        robust_threshold = params.get("robust_threshold", 0.3)
        decay_threshold = params.get("decay_velocity_threshold", 0.0)
        max_spread_mult = params.get("max_spread_mult", 2.0)
        wall_size_mult = params.get("wall_size_mult", 5.0)

        # Compute continuous strength for each of the 4 signal types
        # Spoof SHORT: fragile ask wall (high frag_ask, positive decay)
        spoof_short_strength = 0.0
        if current_frag_ask > robust_threshold and current_decay_ask > decay_threshold:
            # Strength grows as frag_ask increases above robust_threshold
            spoof_short_strength = (current_frag_ask - robust_threshold) / (fragility_threshold - robust_threshold)
            # Decay penalty: lower decay = weaker signal
            spoof_short_strength *= min(1.0, current_decay_ask / max(0.01, abs(current_decay_ask)))

        # Spoof LONG: fragile bid wall
        spoof_long_strength = 0.0
        if current_frag_bid > robust_threshold and current_decay_bid > decay_threshold:
            spoof_long_strength = (current_frag_bid - robust_threshold) / (fragility_threshold - robust_threshold)
            spoof_long_strength *= min(1.0, current_decay_bid / max(0.01, abs(current_decay_bid)))

        # Robust LONG: robust bid wall (low frag_bid, negative/neutral decay)
        robust_long_strength = 0.0
        if current_frag_bid < fragility_threshold and current_decay_bid <= 0:
            robust_long_strength = (fragility_threshold - current_frag_bid) / (fragility_threshold - robust_threshold)
            robust_long_strength *= min(1.0, abs(current_decay_bid) / 0.01)  # normalize decay magnitude

        # Robust SHORT: robust ask wall
        robust_short_strength = 0.0
        if current_frag_ask < fragility_threshold and current_decay_ask <= 0:
            robust_short_strength = (fragility_threshold - current_frag_ask) / (fragility_threshold - robust_threshold)
            robust_short_strength *= min(1.0, abs(current_decay_ask) / 0.01)

        # Find the strongest signal
        candidates = [
            ("SPOOF_SHORT", "SHORT", spoof_short_strength, current_decay_ask),
            ("SPOOF_LONG", "LONG", spoof_long_strength, current_decay_bid),
            ("ROBUST_LONG", "LONG", robust_long_strength, -current_decay_bid),
            ("ROBUST_SHORT", "SHORT", robust_short_strength, -current_decay_ask),
        ]
        candidates.sort(key=lambda x: x[2], reverse=True)
        signal_type, direction, strength, decay_strength = candidates[0]

        # Emit only if strongest signal exceeds minimum strength
        if strength < 0.2:
            return []

        # 3. Compute vol_ratio and spread for soft scores
        vol_ratio = self._compute_vol_ratio(rolling_data)
        spread = self._compute_spread(rolling_data)
        avg_spread = self._compute_avg_spread(rolling_data)

        # 4. Compute soft gate scores (continuous 0.0–1.0)
        wall_score = self._gate_a_wall_score(
            data, direction, rolling_data
        )
        vol_score = self._gate_b_vol_score(signal_type, vol_ratio)
        spread_score = self._gate_c_spread_score(spread, avg_spread)

        # 5. Compute weighted signal_strength from all components
        signal_strength = (
            strength * 0.6
            + wall_score * 0.15
            + vol_score * 0.15
            + spread_score * 0.10
        )

        if signal_strength < 0.40:
            logger.debug(
                "Divergence Scalper: signal_strength %.3f below threshold 0.40 for %s (%s) — "
                "wall=%.2f vol=%.2f spread=%.2f",
                signal_strength, direction, signal_type,
                wall_score, vol_score, spread_score,
            )
            return []

        # 6. VAMP validation (soft bonus, not a hard gate)
        use_vamp_validation = params.get("use_vamp_validation", False)
        vamp_score = 0.5  # neutral default
        if use_vamp_validation:
            vamp_score = self._vamp_validation(rolling_data, direction)
            if vamp_score < 0.2:
                logger.warning(
                    "Divergence Scalper: VAMP score %.3f below 0.2 for %s (%s) — "
                    "allowing signal with warning",
                    vamp_score, direction, signal_type,
                )
        signal_strength += vamp_score * 0.05

        # 7. Compute confidence (7-component model)
        confidence, conf_breakdown = self._compute_confidence(
            signal_type, direction,
            current_frag_bid, current_frag_ask,
            current_decay_bid, current_decay_ask,
            vol_ratio, spread, avg_spread,
            rolling_data, data, params,
            regime, gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 8. Build signal with entry/stop/target
        stop_pct = params.get("stop_pct", 0.003)
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
                f"{signal_type} {direction}: frag={current_frag_bid:.3f}/{current_frag_ask:.3f} "
                f"decay={current_decay_bid:+.4f}/{current_decay_ask:+.4f}"
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
                    "A_wall_size": round(wall_score, 4),
                    "B_vol_ratio": round(vol_score, 4),
                    "C_spread": round(spread_score, 4),
                    "D_vamp": round(vamp_score, 3),
                },
                "confidence_breakdown": conf_breakdown,
                "signal_strength": round(signal_strength, 4),
                "regime": regime,
            },
        )]

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

    def _gate_a_wall_score(
        self,
        data: Dict[str, Any],
        direction: str,
        rolling_data: Dict[str, Any],
    ) -> float:
        """
        Gate A: Wall size score (0.0–1.0).

        Computes wall_ratio = current_wall / avg_level_size.
        Returns min(1.0, wall_ratio / 10.0) — scales 0→1 as wall grows from 0→10× average.
        Returns 0.5 (neutral) if data unavailable.
        """
        top_wall_key = KEY_TOP_WALL_BID_SIZE_5M if direction == "LONG" else KEY_TOP_WALL_ASK_SIZE_5M
        depth_size_key = KEY_DEPTH_BID_SIZE_5M if direction == "LONG" else KEY_DEPTH_ASK_SIZE_5M
        depth_levels_key = KEY_DEPTH_BID_LEVELS_5M if direction == "LONG" else KEY_DEPTH_ASK_LEVELS_5M

        top_wall_rw = rolling_data.get(top_wall_key)
        depth_size_rw = rolling_data.get(depth_size_key)
        depth_levels_rw = rolling_data.get(depth_levels_key)

        if not top_wall_rw or top_wall_rw.count < 1:
            return 0.5  # Can't evaluate — neutral

        current_wall = top_wall_rw.values[-1]
        if current_wall <= 0:
            return 0.0

        # Average level size = total depth / number of levels
        if depth_size_rw and depth_levels_rw and depth_size_rw.count > 0 and depth_levels_rw.count > 0:
            avg_depth = depth_size_rw.values[-1]
            num_levels = depth_levels_rw.values[-1]
            if num_levels > 0 and avg_depth > 0:
                avg_level_size = avg_depth / num_levels
                wall_ratio = current_wall / avg_level_size if avg_level_size > 0 else 1.0
                return min(1.0, wall_ratio / 10.0)

        return 0.5  # Can't compute — neutral

    def _gate_b_vol_score(
        self,
        signal_type: str,
        vol_ratio: float,
    ) -> float:
        """
        Gate B: Volume ratio score (0.0–1.0).

        For SPOOF signals: low vol is good → vol_score = max(0.0, 1.0 - vol_ratio / 0.5)
          vol_ratio=0.0 → 1.0, vol_ratio=0.5 → 0.0
        For ROBUST signals: high vol is good → vol_score = min(1.0, vol_ratio / 1.5)
          vol_ratio=0.0 → 0.0, vol_ratio=1.5 → 1.0
        Clamped to [0.0, 1.0].
        """
        if signal_type.startswith("SPOOF"):
            vol_score = max(0.0, 1.0 - vol_ratio / 0.5)
        else:  # ROBUST
            vol_score = min(1.0, vol_ratio / 1.5)
        return vol_score

    def _gate_c_spread_score(
        self,
        spread: float,
        avg_spread: float,
    ) -> float:
        """
        Gate C: Spread tightness score (0.0–1.0).

        spread_ratio = spread / avg_spread
        spread_score = max(0.0, 1.0 - (spread_ratio - 1.0) / 2.0)
          spread_ratio=1.0 → 1.0, spread_ratio=3.0 → 0.0
        Returns 0.5 (neutral) if avg_spread <= 0.
        """
        if avg_spread <= 0:
            return 0.5  # Can't evaluate — neutral
        spread_ratio = spread / avg_spread
        spread_score = max(0.0, 1.0 - (spread_ratio - 1.0) / 2.0)
        return spread_score

    def _vamp_validation(
        self,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> float:
        """
        VAMP validation score (0.0–1.0).

        Returns a continuous score based on VAMP mid-deviation alignment
        with signal direction. 0.5 = neutral, 1.0 = perfect alignment.
        """
        vamp_levels = rolling_data.get(KEY_VAMP_LEVELS)
        if not vamp_levels:
            return 0.5  # neutral — no VAMP data

        vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)

        if direction == "LONG":
            return max(0.0, min(1.0, 0.5 + vamp_mid_dev * 200))
        else:
            return max(0.0, min(1.0, 0.5 - vamp_mid_dev * 200))

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
        data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
        gex_calc: Any,
        depth_score: Optional[float] = None,
    ) -> tuple:
        """
        Compute 7-component weighted confidence score.

        Components:
            c1: Fragility strength        (weight 0.25)
            c2: Decay velocity            (weight 0.15)
            c3: Wall size significance    (weight 0.10)
            c4: Volume confirmation       (weight 0.10)
            c5: Spread tightness          (weight 0.10)
            c6: VAMP alignment            (weight 0.10)
            c7: GEX regime alignment      (weight 0.15)

        Returns (confidence: float, breakdown: dict).
        """
        def normalize(val: float, vmin: float, vmax: float) -> float:
            return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

        fragility_threshold = params.get("fragility_threshold", 0.5)
        robust_threshold = params.get("robust_threshold", 0.3)

        # Select frag/decay based on signal type and direction
        if signal_type.startswith("SPOOF"):
            frag = frag_ask if direction == "SHORT" else frag_bid
            decay = decay_ask if direction == "SHORT" else decay_bid
        else:
            frag = frag_bid if direction == "LONG" else frag_ask
            decay = decay_bid if direction == "LONG" else decay_ask

        # 1. Fragility strength: frag from fragility_threshold→1.0 (SPOOF) or 0→robust_threshold (ROBUST)
        if signal_type.startswith("SPOOF"):
            c1 = normalize(frag, fragility_threshold, 1.0)
        else:
            c1 = 1.0 - normalize(frag, 0.0, robust_threshold)

        # 2. Decay velocity: abs(decay) from 0→0.5, higher = higher
        c2 = normalize(abs(decay), 0.0, 0.5)

        # 3. Wall size significance: wall_ratio from 5→10, higher = higher
        top_wall_key = KEY_TOP_WALL_BID_SIZE_5M if direction == "LONG" else KEY_TOP_WALL_ASK_SIZE_5M
        depth_size_key = KEY_DEPTH_BID_SIZE_5M if direction == "LONG" else KEY_DEPTH_ASK_SIZE_5M
        depth_levels_key = KEY_DEPTH_BID_LEVELS_5M if direction == "LONG" else KEY_DEPTH_ASK_LEVELS_5M
        wall_ratio = 1.0
        top_wall_rw = rolling_data.get(top_wall_key)
        depth_size_rw = rolling_data.get(depth_size_key)
        depth_levels_rw = rolling_data.get(depth_levels_key)
        if top_wall_rw and depth_size_rw and depth_levels_rw and top_wall_rw.count > 0 and depth_size_rw.count > 0 and depth_levels_rw.count > 0:
            current_wall = top_wall_rw.values[-1]
            avg_depth = depth_size_rw.values[-1]
            num_levels = depth_levels_rw.values[-1]
            if num_levels > 0 and avg_depth > 0:
                avg_level_size = avg_depth / num_levels
                wall_ratio = current_wall / avg_level_size if avg_level_size > 0 else 1
        c3 = normalize(wall_ratio, 5.0, 10.0)

        # 4. Volume confirmation: vol_ratio from 0→2.0, higher = higher
        c4 = normalize(vol_ratio, 0.0, 2.0)

        # 5. Spread stability: spread_ratio from 0→1.5, lower = more stable, invert
        spread_ratio = spread / avg_spread if avg_spread > 0 else 1.0
        c5 = 1.0 - normalize(spread_ratio, 0.0, 1.5)

        # 6. VAMP alignment (weight 0.10)
        vamp_levels = rolling_data.get(KEY_VAMP_LEVELS)
        if vamp_levels:
            vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)
            if direction == "LONG":
                c6 = max(0.0, min(1.0, 0.5 + vamp_mid_dev * 200))
            else:
                c6 = max(0.0, min(1.0, 0.5 - vamp_mid_dev * 200))
        else:
            c6 = 0.5

        # 7. GEX regime alignment (weight 0.15)
        try:
            net_gamma = 0.0
            if gex_calc and hasattr(gex_calc, "get_normalized_net_gamma"):
                net_gamma = gex_calc.get_normalized_net_gamma()
            if direction == "LONG":
                if net_gamma > 0.01:
                    c7 = 1.0
                elif net_gamma < -0.01:
                    c7 = 0.2
                else:
                    c7 = 0.5
            else:
                if net_gamma < -0.01:
                    c7 = 1.0
                elif net_gamma > 0.01:
                    c7 = 0.2
                else:
                    c7 = 0.5
        except Exception:
            c7 = 0.5

        confidence = (
            c1 * 0.25 + c2 * 0.15 + c3 * 0.10 + c4 * 0.10
            + c5 * 0.10 + c6 * 0.10 + c7 * 0.15
        )
        breakdown = {
            "c1_fragility": round(c1, 3),
            "c2_decay": round(c2, 3),
            "c3_wall": round(c3, 3),
            "c4_volume": round(c4, 3),
            "c5_spread": round(c5, 3),
            "c6_vamp": round(c6, 3),
            "c7_gex": round(c7, 3),
        }
        return min(1.0, max(0.0, confidence)), breakdown
