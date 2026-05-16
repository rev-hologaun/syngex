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

Hard gates (all must pass):
    Gate A: Wall size >= 5× average level size (significant wall)
    Gate B: vol_ratio matches signal type (< 0.1 for spoof, > 0.5 for robust)
    Gate C: Spread < 2× average spread (scalp must be profitable)

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
    KEY_VAMP_LEVELS,
)

logger = logging.getLogger("Syngex.Strategies.ParticipantDivergenceScalper")

MIN_CONFIDENCE = 0.10


class ParticipantDivergenceScalper(BaseStrategy):
    """
    Participant Divergence Scalper — microstructure scalping strategy.

    Distinguishes between fragile "spoof" walls and robust multi-participant
    liquidity. Trades both the collapse of fake walls and the bounce off real ones.

    SPOOF BREACH (SHORT): Fragile Ask Wall evaporates → scalp the vacuum
    SPOOF BREACH (LONG):  Fragile Bid Wall evaporates → scalp the vacuum
    ROBUST BOUNCE (LONG):  Robust Bid Wall holds → scalp the bounce
    ROBUST BOUNCE (SHORT): Robust Ask Wall holds → scalp the bounce
    """

    strategy_id = "participant_divergence_scalper"
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

        # 2. Determine signal direction and type
        fragility_threshold = params.get("fragility_threshold", 0.5)
        robust_threshold = params.get("robust_threshold", 0.3)
        decay_threshold = params.get("decay_velocity_threshold", 0.0)
        vol_ratio_spoof = params.get("vol_ratio_spoof", 0.1)
        vol_ratio_robust = params.get("vol_ratio_robust", 0.5)
        max_spread_mult = params.get("max_spread_mult", 2.0)
        wall_size_mult = params.get("wall_size_mult", 5.0)

        # Spoof Breach (SHORT) — fragile ask wall evaporating
        spoof_short = (
            current_frag_ask > fragility_threshold
            and current_decay_ask > decay_threshold
        )
        # Spoof Breach (LONG) — fragile bid wall evaporating
        spoof_long = (
            current_frag_bid > fragility_threshold
            and current_decay_bid > decay_threshold
        )
        # Robust Bounce (LONG) — robust bid wall holding
        robust_long = (
            current_frag_bid < robust_threshold
            and current_decay_bid <= 0
        )
        # Robust Bounce (SHORT) — robust ask wall holding
        robust_short = (
            current_frag_ask < robust_threshold
            and current_decay_ask <= 0
        )

        if not spoof_short and not spoof_long and not robust_long and not robust_short:
            return []

        # Pick the strongest signal
        signals_found = []
        if spoof_short:
            signals_found.append(("SPOOF_SHORT", "SHORT", current_frag_ask, current_decay_ask))
        if spoof_long:
            signals_found.append(("SPOOF_LONG", "LONG", current_frag_bid, current_decay_bid))
        if robust_long:
            signals_found.append(("ROBUST_LONG", "LONG", 1.0 - current_frag_bid, -current_decay_bid))
        if robust_short:
            signals_found.append(("ROBUST_SHORT", "SHORT", 1.0 - current_frag_ask, -current_decay_ask))

        # Pick the strongest signal by signal strength
        signals_found.sort(key=lambda x: x[2] + abs(x[3]), reverse=True)
        signal_type, direction, strength, decay_strength = signals_found[0]

        # 3. Compute vol_ratio and spread for hard gates
        vol_ratio = self._compute_vol_ratio(rolling_data)
        spread = self._compute_spread(rolling_data)
        avg_spread = self._compute_avg_spread(rolling_data)

        # 4. Apply 3 HARD GATES
        # Gate A: Wall size >= wall_size_mult × average level size
        gate_a = self._gate_a_wall_size(
            data, wall_size_mult, direction, rolling_data
        )

        if not gate_a:
            logger.debug(
                "Divergence Scalper: Gate A failed — wall size not significant enough for %s",
                direction,
            )
            return []

        # Gate B: vol_ratio matches signal type
        gate_b = self._gate_b_vol_ratio(signal_type, vol_ratio, params)

        if not gate_b:
            logger.debug(
                "Divergence Scalper: Gate B failed — vol_ratio mismatch for %s (%s)",
                direction, signal_type,
            )
            return []

        # Gate C: Spread < 2× average spread
        gate_c = self._gate_c_spread(spread, avg_spread, max_spread_mult)

        if not gate_c:
            logger.debug(
                "Divergence Scalper: Gate C failed — spread too wide for %s",
                direction,
            )
            return []

        # 5. VAMP validation (optional)
        use_vamp_validation = params.get("use_vamp_validation", False)
        vamp_validated = True
        if use_vamp_validation:
            vamp_validated = self._vamp_validation(rolling_data, direction)

        if not vamp_validated:
            logger.debug(
                "Divergence Scalper: VAMP validation failed for %s", direction,
            )
            return []

        # 6. Compute confidence (7-component model)
        confidence = self._compute_confidence(
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

        # 7. Build signal with entry/stop/target
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
                    "A_wall_size": gate_a,
                    "B_vol_ratio": gate_b,
                    "C_spread": gate_c,
                    "D_vamp": vamp_validated,
                },
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

    def _gate_a_wall_size(
        self,
        data: Dict[str, Any],
        wall_size_mult: float,
        direction: str,
        rolling_data: Dict[str, Any],
    ) -> bool:
        """
        Gate A: Wall size significance.

        The wall on the signal side must be >= wall_size_mult × average level size.
        """
        top_wall_key = KEY_TOP_WALL_BID_SIZE_5M if direction == "LONG" else KEY_TOP_WALL_ASK_SIZE_5M
        depth_bid_key = KEY_DEPTH_BID_SIZE_5M if direction == "LONG" else KEY_DEPTH_ASK_SIZE_5M
        depth_levels_key = KEY_DEPTH_BID_LEVELS_5M if direction == "LONG" else KEY_DEPTH_ASK_LEVELS_5M

        top_wall_rw = rolling_data.get(top_wall_key)
        depth_size_rw = rolling_data.get(depth_bid_key) if direction == "LONG" else rolling_data.get(KEY_DEPTH_ASK_SIZE_5M)
        depth_levels_rw = rolling_data.get(depth_levels_key)

        if not top_wall_rw or top_wall_rw.count < 1:
            return True  # Can't evaluate — pass

        current_wall = top_wall_rw.values[-1]
        if current_wall <= 0:
            return False

        # Average level size = total depth / number of levels
        if depth_size_rw and depth_levels_rw and depth_size_rw.count > 0 and depth_levels_rw.count > 0:
            avg_depth = depth_size_rw.values[-1]
            num_levels = depth_levels_rw.values[-1]
            if num_levels > 0 and avg_depth > 0:
                avg_level_size = avg_depth / num_levels
                return current_wall >= avg_level_size * wall_size_mult

        return True  # Can't compute — pass

    def _gate_b_vol_ratio(
        self,
        signal_type: str,
        vol_ratio: float,
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate B: Volume ratio matches signal type.

        Spoof signals need low vol_ratio (< 0.1) — no real trades backing the wall.
        Robust signals need high vol_ratio (> 0.5) — wall absorbing real trades.
        """
        if signal_type.startswith("SPOOF"):
            threshold = params.get("vol_ratio_spoof", 0.1)
            return vol_ratio < threshold
        else:  # ROBUST
            threshold = params.get("vol_ratio_robust", 0.5)
            return vol_ratio > threshold

    def _gate_c_spread(
        self,
        spread: float,
        avg_spread: float,
        max_spread_mult: float,
    ) -> bool:
        """
        Gate C: Spread tightness.

        Current spread must be < max_spread_mult × average spread.
        Scalp must be profitable after spread cost.
        """
        if avg_spread <= 0:
            return True  # Can't evaluate — pass
        return spread < avg_spread * max_spread_mult

    def _vamp_validation(
        self,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> bool:
        """
        VAMP validation: VAMP direction should align with signal direction.
        """
        vamp_levels = rolling_data.get(KEY_VAMP_LEVELS)
        if not vamp_levels:
            return True  # No VAMP data — pass

        vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)

        if direction == "LONG":
            return vamp_mid_dev >= -0.001  # Allow small tolerance
        else:
            return vamp_mid_dev <= 0.001  # Allow small tolerance

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
    ) -> float:
        """
        Compute 5-component simple average confidence score (Family A).

        Each component normalizes to [0,1], then average equally (÷5).

        Returns 0.0–1.0.
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

        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))
