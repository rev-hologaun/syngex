"""
strategies/layer2/vamp_momentum.py — VAMP Momentum

Volume-Adjusted Mid-Price Momentum strategy (bidirectional).
Detects microstructure momentum via volume-weighted center of gravity
from the top 10 bid/ask levels. When VAMP deviates from the simple
mid-price, it reveals when the book is bid-weighted or ask-weighted —
often before L1 price reacts.

LONG: Δ_VAMP > +threshold AND ROC(VAMP) > 0
SHORT: Δ_VAMP < -threshold AND ROC(VAMP) < 0

Hard gates (all must pass):
    Gate A: Avg participants over top 10 >= min_avg_participants
    Gate B: Σ size(top 10) > MA(total depth, 60s) × 1.2
    Gate C: Current spread < MA(spread, 5m)

Confidence model (7 components):
    1. VAMP deviation magnitude     (0.0–0.25)
    2. VAMP ROC strength            (0.0–0.20)
    3. Participant conviction       (0.0–0.15)
    4. Liquidity density            (0.0–0.15)
    5. Spread stability             (0.0–0.10)
    6. GEX regime alignment         (0.0–0.10)
    7. Depth level quality           (0.0–0.05)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_VAMP_5M,
    KEY_VAMP_LEVELS,
    KEY_VAMP_MID_DEV_5M,
    KEY_VAMP_ROC_5M,
    KEY_VAMP_PARTICIPANTS_5M,
    KEY_VAMP_DEPTH_DENSITY_5M,
    KEY_DEPTH_SPREAD_5M,
)

logger = logging.getLogger("Syngex.Strategies.VampMomentum")

MIN_CONFIDENCE = 0.15


class VampMomentum(BaseStrategy):
    """
    Volume-Adjusted Mid-Price Momentum strategy.

    Computes VAMP = Σ(price × size) / Σ(size) over top 10 levels.
    When VAMP deviates from mid-price, it reveals bid/ask weight bias.

    LONG: Book is bid-weighted (VAMP > mid) with rising momentum
    SHORT: Book is ask-weighted (VAMP < mid) with falling momentum
    """

    strategy_id = "vamp_momentum"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for VAMP momentum signal.

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

        # 1. Get VAMP levels from rolling_data
        vamp_levels = rolling_data.get(KEY_VAMP_LEVELS)
        if vamp_levels is None:
            return []

        bid_levels = vamp_levels.get("bid_levels", [])
        ask_levels = vamp_levels.get("ask_levels", [])
        mid_price = vamp_levels.get("mid_price", 0)
        spread = vamp_levels.get("spread", 0)

        if not bid_levels and not ask_levels:
            return []

        # 2. Compute VAMP
        bid_weighted = sum(l["price"] * l["size"] for l in bid_levels)
        bid_total = sum(l["size"] for l in bid_levels)
        ask_weighted = sum(l["price"] * l["size"] for l in ask_levels)
        ask_total = sum(l["size"] for l in ask_levels)
        total_weighted = bid_weighted + ask_weighted
        total_size = bid_total + ask_total

        if total_size > 0 and mid_price > 0:
            vamp = total_weighted / total_size
            vamp_mid_dev = (vamp - mid_price) / mid_price
        else:
            vamp = mid_price
            vamp_mid_dev = 0

        # 3. Get rolling window values
        vamp_history = rolling_data.get(KEY_VAMP_5M)
        vamp_mid_dev_history = rolling_data.get(KEY_VAMP_MID_DEV_5M)
        vamp_roc_history = rolling_data.get(KEY_VAMP_ROC_5M)
        participants_history = rolling_data.get(KEY_VAMP_PARTICIPANTS_5M)
        depth_density_history = rolling_data.get(KEY_VAMP_DEPTH_DENSITY_5M)

        # Current values
        current_vamp_dev = vamp_mid_dev
        current_total_size = total_size
        current_spread = spread

        # ROC from rolling window
        vamp_roc_window = params.get("vamp_roc_window", 5)
        vamp_roc = 0.0
        if vamp_history and vamp_history.count >= vamp_roc_window:
            current_vamp = vamp_history.values[-1]
            past_vamp = vamp_history.values[-vamp_roc_window]
            vamp_roc = (current_vamp - past_vamp) / past_vamp if past_vamp != 0 else 0.0

        # Participants
        avg_participants = 0.0
        if participants_history and participants_history.count > 0:
            avg_participants = participants_history.latest or 0.0
        else:
            # Fallback: compute from current levels
            total_participants = sum(
                l.get("participants", 1) for l in bid_levels + ask_levels
            )
            n_levels = len(bid_levels) + len(ask_levels)
            avg_participants = total_participants / n_levels if n_levels > 0 else 0.0

        # 4. Apply 3 HARD GATES
        # Gate A: Participant conviction
        min_avg_participants = params.get("min_avg_participants", 1.5)
        gate_a = avg_participants >= min_avg_participants

        # Gate B: Liquidity density
        liquidity_density_min_mult = params.get("liquidity_density_min_mult", 1.2)
        depth_ma_window = params.get("depth_ma_window_seconds", 60)
        gate_b = True
        if depth_density_history and depth_density_history.count > 0:
            ma_depth = depth_density_history.mean or 0
            if ma_depth > 0:
                gate_b = current_total_size > ma_depth * liquidity_density_min_mult

        # Gate C: Spread stability
        spread_stability_ma_seconds = params.get("spread_stability_ma_seconds", 300)
        gate_c = True
        spread_ma_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        if spread_ma_window and spread_ma_window.count > 0:
            ma_spread = spread_ma_window.mean or 0
            if ma_spread > 0:
                gate_c = current_spread < ma_spread

        all_gates_pass = gate_a and gate_b and gate_c
        if not all_gates_pass:
            return []

        # 5. Signal direction check
        vamp_mid_dev_threshold = params.get("vamp_mid_dev_threshold", 0.0005)
        vamp_roc_threshold = params.get("vamp_roc_threshold", 0.0)

        direction = None
        if vamp_mid_dev > vamp_mid_dev_threshold and vamp_roc > vamp_roc_threshold:
            direction = "LONG"
        elif vamp_mid_dev < -vamp_mid_dev_threshold and vamp_roc < vamp_roc_threshold:
            direction = "SHORT"

        if direction is None:
            return []

        # 6. Compute confidence (7-component model)
        confidence = self._compute_confidence(
            vamp_mid_dev, vamp_roc, avg_participants,
            current_total_size, depth_density_history,
            current_spread, spread_ma_window,
            direction, regime, gex_calc,
            bid_levels, ask_levels,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 7. Build signal with entry/stop/target
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
                f"VAMP momentum: Δ_VAMP={vamp_mid_dev:.4f} ({vamp_mid_dev*100:.3f}%), "
                f"ROC={vamp_roc:.4f}, direction={direction}"
            ),
            metadata={
                "direction": direction,
                "vamp": round(vamp, 4),
                "mid_price": round(mid_price, 2),
                "vamp_mid_dev": round(vamp_mid_dev, 6),
                "vamp_mid_dev_pct": round(vamp_mid_dev * 100, 4),
                "vamp_roc": round(vamp_roc, 6),
                "avg_participants": round(avg_participants, 2),
                "total_size": round(current_total_size, 2),
                "spread": round(current_spread, 4),
                "gates": {
                    "A_participants": gate_a,
                    "B_liquidity_density": gate_b,
                    "C_spread_stability": gate_c,
                },
                "bid_levels_count": len(bid_levels),
                "ask_levels_count": len(ask_levels),
            },
        )]

    def _compute_confidence(
        self,
        vamp_mid_dev: float,
        vamp_roc: float,
        avg_participants: float,
        current_total_size: float,
        depth_density_history: Any,
        current_spread: float,
        spread_ma_window: Any,
        direction: str,
        regime: str,
        gex_calc: Any,
        bid_levels: List[Dict[str, Any]],
        ask_levels: List[Dict[str, Any]],
        depth_score: Optional[float] = None,
    ) -> float:
        """
        Compute 5-component simple average confidence score (Family A).

        Each component normalizes to [0,1], then average equally (÷5).

        Returns 0.0–1.0.
        """
        def normalize(val: float, vmin: float, vmax: float) -> float:
            return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

        params = self._params

        # 1. VAMP deviation: abs(vamp_mid_dev) from 0→0.0025 (threshold=0.0005, 5x=0.0025), higher = higher
        dev_threshold = params.get("vamp_mid_dev_threshold", 0.0005)
        c1 = normalize(abs(vamp_mid_dev), 0.0, dev_threshold * 5.0)

        # 2. VAMP ROC: abs(vamp_roc) from 0→0.01, aligned = 1.0, misaligned = 0.25
        roc_magnitude = abs(vamp_roc)
        roc_aligned = (vamp_roc > 0 if direction == "LONG" else vamp_roc < 0)
        if roc_aligned:
            c2 = normalize(roc_magnitude, 0.0, 0.01)
        else:
            c2 = 0.25  # baseline for misaligned

        # 3. Participant conviction: avg_participants from min_participants→2×min_participants, higher = higher
        min_participants = params.get("min_avg_participants", 1.5)
        c3 = normalize(avg_participants, min_participants, min_participants * 2.0)

        # 4. Liquidity density: density_ratio from 0→2.0, higher = higher
        density_ratio = 0.0
        if depth_density_history and depth_density_history.count > 0:
            ma_depth = depth_density_history.mean or 0
            if ma_depth > 0:
                density_ratio = current_total_size / ma_depth
        c4 = normalize(density_ratio, 0.0, 2.0)

        # 5. Spread stability: spread_ratio from 0→1.0, lower = more stable, invert
        spread_ratio = 1.0
        if spread_ma_window and spread_ma_window.count > 0:
            ma_spread = spread_ma_window.mean or 0
            if ma_spread > 0:
                spread_ratio = current_spread / ma_spread
        c5 = 1.0 - normalize(spread_ratio, 0.0, 1.0)

        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))
