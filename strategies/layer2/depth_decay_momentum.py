"""
strategies/layer2/depth_decay_momentum.py — Depth Decay Momentum

Liquidity evaporation detection strategy (bidirectional).
Detects when liquidity is pulled (not consumed by trades) from one side of the book.
When ask-side depth drops 15%+ in 30s without corresponding trade volume,
sellers are exiting → bullish. When bid-side depth drops similarly → bearish.

LONG: Ask-side depth evaporating (ask ROC < -threshold) → bullish
SHORT: Bid-side depth evaporating (bid ROC < -threshold) → bearish

Hard gates (all must pass):
    Gate A: Top 5 depth >= min_top5_depth (magnitude gate)
    Gate B: Participant consistency (evaporating levels have few participants)
    Gate C: Volume/depth ratio < max_vol_ratio (evaporated, not consumed)

Confidence model (7 components):
    1. Depth decay magnitude      (0.0–0.25) — |ROC| scaled
    2. Volume/depth ratio strength (0.0–0.20) — lower ratio = higher confidence
    3. Top-level concentration    (0.0–0.15) — how much decay is in top 5 vs total
    4. Participant consistency     (0.0–0.10) — few participants = single-player pull
    5. VAMP directional alignment (0.0–0.10) — VAMP bias matches decay direction
    6. Overall depth magnitude     (0.0–0.10) — deeper book = more meaningful
    7. GEX regime alignment        (0.0–0.10) — decay direction matches GEX bias
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_DEPTH_DECAY_BID_5M,
    KEY_DEPTH_DECAY_ASK_5M,
    KEY_DEPTH_TOP5_BID_5M,
    KEY_DEPTH_TOP5_ASK_5M,
    KEY_DEPTH_VOL_RATIO_5M,
)

logger = logging.getLogger("Syngex.Strategies.DepthDecayMomentum")


class DepthDecayMomentum(BaseStrategy):
    """
    Depth Decay Momentum strategy — liquidity evaporation detection.

    Detects when liquidity is pulled (not consumed by trades) from one side
    of the order book. When ask-side depth drops significantly without
    corresponding trade volume, sellers are exiting → bullish signal.
    When bid-side depth drops similarly → bearish signal.
    """

    strategy_id = "depth_decay_momentum"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for depth decay momentum signal.

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

        # 1. Get depth ROC from rolling windows
        min_data_points = params.get("min_depth_decay_data_points", 10)
        bid_decay = rolling_data.get(KEY_DEPTH_DECAY_BID_5M)
        ask_decay = rolling_data.get(KEY_DEPTH_DECAY_ASK_5M)

        if not bid_decay or bid_decay.count < min_data_points:
            return []
        if not ask_decay or ask_decay.count < min_data_points:
            return []

        current_bid_roc = bid_decay.values[-1]
        current_ask_roc = ask_decay.values[-1]

        # 2. Get top-5 depth from rolling windows
        top5_bid = rolling_data.get(KEY_DEPTH_TOP5_BID_5M)
        top5_ask = rolling_data.get(KEY_DEPTH_TOP5_ASK_5M)

        # 3. Get volume/depth ratio from rolling window
        vol_ratio_window = rolling_data.get(KEY_DEPTH_VOL_RATIO_5M)

        # 4. Determine signal direction
        depth_decay_threshold = params.get("depth_decay_threshold", 0.15)

        ask_evaporating = current_ask_roc < -depth_decay_threshold
        bid_evaporating = current_bid_roc < -depth_decay_threshold

        if not ask_evaporating and not bid_evaporating:
            return []

        # Only emit one signal per evaluation (LONG or SHORT, not both)
        if ask_evaporating and bid_evaporating:
            # Both sides evaporating equally — no directional signal
            return []

        direction = "LONG" if ask_evaporating else "SHORT"

        # 5. Apply 3 HARD GATES
        # Gate A: Magnitude — top 5 levels must have meaningful depth
        min_top5_depth = params.get("min_top5_depth", 100)
        gate_a = True
        if direction == "LONG" and top5_ask and top5_ask.count > 0:
            gate_a = top5_ask.values[-1] >= min_top5_depth
        elif direction == "SHORT" and top5_bid and top5_bid.count > 0:
            gate_a = top5_bid.values[-1] >= min_top5_depth

        if not gate_a:
            logger.debug(
                "Depth Decay: Gate A failed — top5 %s depth %.0f < %.0f",
                "ask" if direction == "LONG" else "bid",
                (top5_ask.values[-1] if top5_ask and top5_ask.count > 0 else 0),
                min_top5_depth,
            )
            return []

        # Gate B: Participant consistency
        # Evaporating levels should have few participants (single-player pull)
        max_evap_participants = params.get("max_evap_participants", 2)
        depth_snapshot = data.get("depth_snapshot")
        gate_b = True
        if depth_snapshot:
            # Check avg/max participants from depth_agg data
            if direction == "LONG":
                # Ask-side evaporation — check ask participants
                ask_max = depth_snapshot.get("ask_max_participants", 0)
                ask_avg = depth_snapshot.get("ask_avg_participants", 0)
                gate_b = ask_max <= max_evap_participants or ask_avg <= max_evap_participants
            else:
                # Bid-side evaporation — check bid participants
                bid_max = depth_snapshot.get("bid_max_participants", 0)
                bid_avg = depth_snapshot.get("bid_avg_participants", 0)
                gate_b = bid_max <= max_evap_participants or bid_avg <= max_evap_participants

        if not gate_b:
            logger.debug(
                "Depth Decay: Gate B failed — participant count too high for %s",
                direction,
            )
            return []

        # Gate C: Volume/depth ratio
        # Low ratio (< max_vol_ratio) = liquidity evaporated (not consumed)
        max_vol_ratio = params.get("max_vol_ratio", 0.2)
        gate_c = True
        if vol_ratio_window and vol_ratio_window.count > 0:
            current_vol_ratio = vol_ratio_window.values[-1]
            gate_c = current_vol_ratio < max_vol_ratio

        if not gate_c:
            logger.debug(
                "Depth Decay: Gate C failed — vol/depth ratio %.4f >= %.2f",
                vol_ratio_window.values[-1] if vol_ratio_window and vol_ratio_window.count > 0 else 0,
                max_vol_ratio,
            )
            return []

        # 6. Optional VAMP directional bias check
        use_vamp_bias = params.get("use_vamp_bias", True)
        vamp_bias_aligned = True
        if use_vamp_bias:
            vamp_levels = rolling_data.get("vamp_levels")
            if vamp_levels:
                vamp_mid_dev = vamp_levels.get("mid_price", 0)
                # VAMP > mid → book is bid-weighted → supports ask-side evaporation (bullish)
                # VAMP < mid → book is ask-weighted → supports bid-side evaporation (bearish)
                if direction == "LONG":
                    # Ask-side evaporation is bullish; VAMP should be bid-weighted (> 0)
                    vamp_bias_aligned = vamp_mid_dev >= 0
                else:
                    # Bid-side evaporation is bearish; VAMP should be ask-weighted (< 0)
                    vamp_bias_aligned = vamp_mid_dev <= 0

        if not vamp_bias_aligned:
            logger.debug(
                "Depth Decay: VAMP bias misaligned for %s (mid_dev=%.6f)",
                direction, vamp_mid_dev,
            )
            return []

        # 7. Compute confidence (7-component model)
        confidence = self._compute_confidence(
            current_bid_roc, current_ask_roc, direction,
            top5_bid, top5_ask, vol_ratio_window,
            depth_snapshot, rolling_data,
            direction, regime, gex_calc,
        )

        min_confidence = params.get("min_confidence", 0.40)
        max_confidence = params.get("max_confidence", 0.90)
        confidence = max(min_confidence, min(confidence, max_confidence))

        if confidence < min_confidence:
            return []

        # 8. Build signal with entry/stop/target
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

        decay_roc = current_ask_roc if direction == "LONG" else current_bid_roc
        vol_ratio = vol_ratio_window.values[-1] if vol_ratio_window and vol_ratio_window.count > 0 else 0.0

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Depth decay {direction}: ROC={decay_roc:.4f} "
                f"({decay_roc*100:.2f}%), vol/depth ratio={vol_ratio:.4f}"
            ),
            metadata={
                "direction": direction,
                "bid_roc": round(current_bid_roc, 6),
                "ask_roc": round(current_ask_roc, 6),
                "decay_roc": round(decay_roc, 6),
                "decay_roc_pct": round(decay_roc * 100, 4),
                "vol_depth_ratio": round(vol_ratio, 4),
                "gates": {
                    "A_magnitude": gate_a,
                    "B_participants": gate_b,
                    "C_vol_ratio": gate_c,
                    "D_vamp_bias": vamp_bias_aligned,
                },
                "depth_snapshot": {
                    "bid_avg_participants": depth_snapshot.get("bid_avg_participants", 0) if depth_snapshot else None,
                    "ask_avg_participants": depth_snapshot.get("ask_avg_participants", 0) if depth_snapshot else None,
                    "bid_max_participants": depth_snapshot.get("bid_max_participants", 0) if depth_snapshot else None,
                    "ask_max_participants": depth_snapshot.get("ask_max_participants", 0) if depth_snapshot else None,
                },
                "regime": regime,
            },
        )]

    def _compute_confidence(
        self,
        bid_roc: float,
        ask_roc: float,
        direction: str,
        top5_bid: Any,
        top5_ask: Any,
        vol_ratio_window: Any,
        depth_snapshot: Optional[Dict[str, Any]],
        rolling_data: Dict[str, Any],
        _direction: str,  # noqa: ARG002 — used for clarity
        regime: str,
        gex_calc: Any,
    ) -> float:
        """
        Compute 7-component confidence score.

        Returns 0.0–1.0.
        """
        params = self._params

        # Direction-specific ROC
        decay_roc = ask_roc if direction == "LONG" else bid_roc
        decay_magnitude = abs(decay_roc)

        # 1. Depth decay magnitude (0.0–0.25)
        # |ROC| scaled linearly; at threshold = ~0.12, at 3× threshold = 0.25
        depth_decay_threshold = params.get("depth_decay_threshold", 0.15)
        conf_decay = min(0.25, 0.12 * (decay_magnitude / depth_decay_threshold)) if depth_decay_threshold > 0 else 0.0

        # 2. Volume/depth ratio strength (0.0–0.20)
        # Lower ratio = higher confidence (evaporated not consumed)
        max_vol_ratio = params.get("max_vol_ratio", 0.2)
        conf_vol_ratio = 0.0
        if vol_ratio_window and vol_ratio_window.count > 0:
            current_vol_ratio = vol_ratio_window.values[-1]
            # At 0 ratio = 0.20, at threshold = 0.0
            conf_vol_ratio = 0.20 * max(0.0, 1.0 - current_vol_ratio / max_vol_ratio)

        # 3. Top-level concentration (0.0–0.15)
        # How much decay is concentrated in top 5 vs total depth
        conf_concentration = 0.05  # baseline
        market_depth = rolling_data.get("market_depth_agg", {})
        bid_levels = market_depth.get("bid_levels", [])
        ask_levels = market_depth.get("ask_levels", [])
        total_bid_depth = sum(l["size"] for l in bid_levels)
        total_ask_depth = sum(l["size"] for l in ask_levels)
        if direction == "LONG" and total_ask_depth > 0:
            top5_ask_depth = sum(l["size"] for l in ask_levels[:5])
            concentration = top5_ask_depth / total_ask_depth
            conf_concentration = 0.05 + 0.10 * concentration
        elif direction == "SHORT" and total_bid_depth > 0:
            top5_bid_depth = sum(l["size"] for l in bid_levels[:5])
            concentration = top5_bid_depth / total_bid_depth
            conf_concentration = 0.05 + 0.10 * concentration

        # 4. Participant consistency (0.0–0.10)
        # Few participants = single-player pull = higher confidence
        max_evap_participants = params.get("max_evap_participants", 2)
        conf_participants = 0.05  # baseline
        if depth_snapshot:
            if direction == "LONG":
                avg_participants = depth_snapshot.get("ask_avg_participants", 0)
            else:
                avg_participants = depth_snapshot.get("bid_avg_participants", 0)
            if avg_participants <= max_evap_participants:
                conf_participants = 0.10
            elif avg_participants <= max_evap_participants * 2:
                conf_participants = 0.07

        # 5. VAMP directional alignment (0.0–0.10)
        # VAMP bias matches decay direction
        conf_vamp = 0.05  # baseline
        use_vamp_bias = params.get("use_vamp_bias", True)
        if use_vamp_bias:
            vamp_levels = rolling_data.get("vamp_levels")
            if vamp_levels:
                vamp_mid_dev = vamp_levels.get("mid_price", 0)
                if direction == "LONG" and vamp_mid_dev >= 0:
                    conf_vamp = 0.10
                elif direction == "SHORT" and vamp_mid_dev <= 0:
                    conf_vamp = 0.10
                elif vamp_mid_dev != 0:
                    # Partial alignment based on magnitude
                    conf_vamp = 0.05 + 0.05 * min(1.0, abs(vamp_mid_dev) / 0.001)

        # 6. Overall depth magnitude (0.0–0.10)
        # Deeper book = more meaningful signal
        conf_depth = 0.05  # baseline
        if direction == "LONG" and top5_ask and top5_ask.count > 0:
            top5_depth = top5_ask.values[-1]
            min_top5 = params.get("min_top5_depth", 100)
            conf_depth = 0.05 + 0.05 * min(1.0, top5_depth / (min_top5 * 3))
        elif direction == "SHORT" and top5_bid and top5_bid.count > 0:
            top5_depth = top5_bid.values[-1]
            min_top5 = params.get("min_top5_depth", 100)
            conf_depth = 0.05 + 0.05 * min(1.0, top5_depth / (min_top5 * 3))

        # 7. GEX regime alignment (0.0–0.10)
        # Decay direction matches GEX bias
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
            conf_decay + conf_vol_ratio + conf_concentration +
            conf_participants + conf_vamp + conf_depth + conf_gex
        )
        return min(1.0, max(0.0, confidence))
