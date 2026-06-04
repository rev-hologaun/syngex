"""
strategies/layer2/participant_diversity_conviction.py — Participant Diversity Conviction

Measures institutional conviction by analyzing:
1. Intra-Level Diversity — num_participants per price level (from depth_quotes L2 data)
2. Inter-Exchange Diversity — unique exchanges contributing to a price level

A wall with 4 participants across 3 exchanges = high conviction (institutional).
A wall with 1 participant = likely spoofed.

This is a **filter-style conviction engine** — it produces graded signal strength
rather than binary pass/fail. Other strategies handle price confirmation; this
strategy answers "how much conviction is there?" and emits a signal when
signal_strength >= 0.35.

LONG:  signal_strength >= 0.35 based on participant/exchange diversity
SHORT: signal_strength >= 0.35 based on participant/exchange diversity

Exit: conviction_score drops < 0.4 OR stop-loss hit
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_BID_PARTICIPANTS_5M,
    KEY_ASK_PARTICIPANTS_5M,
    KEY_BID_EXCHANGES_5M,
    KEY_ASK_EXCHANGES_5M,
    KEY_CONVICT_SCORE_5M,
    KEY_VOLUME_5M,
    KEY_VAMP_LEVELS,
)

logger = logging.getLogger("Syngex.Strategies.ParticipantDiversityConviction")

MIN_CONFIDENCE = 0.20


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))


class ParticipantDiversityConviction(BaseStrategy):
    """
    Participant Diversity Conviction strategy — institutional conviction filter.

    Produces a graded signal strength based on order book wall quality:
    multiple participants and multiple exchanges indicate genuine institutional
    interest vs single-player spoofed walls.

    This is a **filter-style** strategy: it measures conviction, not breakout.
    Price confirmation is handled by other strategies.

    Signal strength per direction:
        base_strength = min(participant_score, exchange_score) * 0.5
        strength += conviction_score * 0.5
        strength += size_score * 0.1
        Signal emitted when strength >= 0.35

    participant_score = min(1.0, participants / 5.0)
    exchange_score    = min(1.0, exchanges / 4.0)
    conviction_score  = 0.6 * participant_score + 0.4 * exchange_score
    size_score        = min(1.0, current_size / (avg_size * 1.5))
    """

    strategy_id = "participant_diversity_conviction"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for participant diversity conviction signal.

        Produces a graded signal strength based on participant/exchange diversity.
        Emits a LONG or SHORT signal when the stronger direction reaches
        signal_strength >= 0.35, or empty list when no direction qualifies.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params
        gex_calc = data.get("gex_calculator")
        regime = data.get("regime", "")

        # 1. Get participant/exchange data from rolling windows
        min_data_points = params.get("min_data_points", 5)
        bid_participants_window = rolling_data.get(KEY_BID_PARTICIPANTS_5M)
        ask_participants_window = rolling_data.get(KEY_ASK_PARTICIPANTS_5M)
        bid_exchanges_window = rolling_data.get(KEY_BID_EXCHANGES_5M)
        ask_exchanges_window = rolling_data.get(KEY_ASK_EXCHANGES_5M)
        conviction_window = rolling_data.get(KEY_CONVICT_SCORE_5M)

        if not bid_participants_window or bid_participants_window.count < min_data_points:
            return []
        if not ask_participants_window or ask_participants_window.count < min_data_points:
            return []
        if not bid_exchanges_window or bid_exchanges_window.count < min_data_points:
            return []
        if not ask_exchanges_window or ask_exchanges_window.count < min_data_points:
            return []

        current_bid_participants = bid_participants_window.values[-1]
        current_ask_participants = ask_participants_window.values[-1]
        current_bid_exchanges = bid_exchanges_window.values[-1]
        current_ask_exchanges = ask_exchanges_window.values[-1]
        current_conviction = conviction_window.values[-1] if conviction_window else 0.0

        # 2. Compute soft scores per side
        # Participant score: graded 0→1 as participants grow to 5.0
        bid_participant_score = min(1.0, current_bid_participants / 5.0)
        ask_participant_score = min(1.0, current_ask_participants / 5.0)

        # Exchange score: graded 0→1 as exchanges grow to 4.0
        bid_exchange_score = min(1.0, current_bid_exchanges / 4.0)
        ask_exchange_score = min(1.0, current_ask_exchanges / 4.0)

        # Conviction score: weighted harmonic mean (0.6 participant + 0.4 exchange)
        # Prevents one weak dimension from completely killing the signal
        bid_conviction = 0.6 * bid_participant_score + 0.4 * bid_exchange_score
        ask_conviction = 0.6 * ask_participant_score + 0.4 * ask_exchange_score

        # 3. Compute soft Gate C size scores for both directions
        long_size_score = self._gate_c_size_score_for_direction(rolling_data, "LONG")
        short_size_score = self._gate_c_size_score_for_direction(rolling_data, "SHORT")

        # 4. Compute graded signal strength per direction
        long_strength = (
            min(bid_participant_score, bid_exchange_score) * 0.5
            + bid_conviction * 0.5
            + long_size_score * 0.1
        )
        short_strength = (
            min(ask_participant_score, ask_exchange_score) * 0.5
            + ask_conviction * 0.5
            + short_size_score * 0.1
        )

        # VAMP score (float 0–1) — used as soft bonus, not hard gate
        vamp_score = self._vamp_validation(rolling_data, "LONG") if long_strength >= short_strength else self._vamp_validation(rolling_data, "SHORT")

        # Threshold for emitting a signal (down from effective ~0.7 of old binary system)
        signal_threshold = params.get("signal_threshold", 0.35)

        if long_strength < signal_threshold and short_strength < signal_threshold:
            return []

        # Only emit one signal per evaluation — pick the stronger direction
        if long_strength >= short_strength:
            direction = "LONG"
            size_score = long_size_score
        else:
            direction = "SHORT"
            size_score = short_size_score

        # 5. VAMP validation — soft bonus, not hard gate
        vamp_validated = vamp_score
        if vamp_score < 0.2:
            logger.warning(
                "Participant Conviction: VAMP score low (%.3f) for %s — allowing signal",
                vamp_score, direction,
            )
        if direction == "LONG":
            long_strength += vamp_score * 0.05
        else:
            short_strength += vamp_score * 0.05

        # 6. Compute confidence (7-component model)
        confidence, conf_breakdown = self._compute_confidence(
            bid_participants=current_bid_participants,
            ask_participants=current_ask_participants,
            bid_exchanges=current_bid_exchanges,
            ask_exchanges=current_ask_exchanges,
            bid_conviction=bid_conviction,
            ask_conviction=ask_conviction,
            conviction=current_conviction,
            direction=direction,
            rolling_data=rolling_data,
            data=data, params=params, regime=regime, gex_calc=gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 7. Build signal with entry/stop/target
        price = data.get("current_price", underlying_price)
        if price <= 0:
            price = underlying_price

        stop_pct = params.get("stop_pct", 0.008)
        target_risk_mult = params.get("target_risk_mult", 2.0)

        entry = price
        stop_distance = entry * stop_pct

        if direction == "LONG":
            stop = entry - stop_distance
            target = entry + (stop_distance * target_risk_mult)
        else:
            stop = entry + stop_distance
            target = entry - (stop_distance * target_risk_mult)

        direction_enum = Direction.LONG if direction == "LONG" else Direction.SHORT

        conviction_pct = (bid_conviction if direction == "LONG" else ask_conviction)

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Participant conviction {direction}: "
                f"participants={current_bid_participants if direction == 'LONG' else current_ask_participants:.1f}, "
                f"exchanges={current_bid_exchanges if direction == 'LONG' else current_ask_exchanges:.0f}, "
                f"conviction={conviction_pct:.3f}, "
                f"strength={long_strength if direction == 'LONG' else short_strength:.3f}"
            ),
            metadata={
                "direction": direction,
                "bid_participants": round(current_bid_participants, 2),
                "ask_participants": round(current_ask_participants, 2),
                "bid_exchanges": round(current_bid_exchanges, 2),
                "ask_exchanges": round(current_ask_exchanges, 2),
                "bid_participant_score": round(bid_participant_score, 4),
                "ask_participant_score": round(ask_participant_score, 4),
                "bid_exchange_score": round(bid_exchange_score, 4),
                "ask_exchange_score": round(ask_exchange_score, 4),
                "bid_conviction": round(bid_conviction, 4),
                "ask_conviction": round(ask_conviction, 4),
                "long_strength": round(long_strength, 4),
                "short_strength": round(short_strength, 4),
                "size_score": round(size_score, 4),
                "gates": {
                    "A_participant_score": round(
                        bid_participant_score if direction == "LONG" else ask_participant_score, 4
                    ),
                    "B_exchange_score": round(
                        bid_exchange_score if direction == "LONG" else ask_exchange_score, 4
                    ),
                    "C_size_ratio": round(size_score, 4),
                    "D_vamp": round(vamp_validated, 3),
                },
                "regime": regime,
                "confidence_breakdown": conf_breakdown,
            },
        )]

    def _gate_c_size_score_for_direction(
        self,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> float:
        """
        Gate C: Soft size ratio score for a specific direction.

        Returns min(1.0, current_size / (avg_size * 1.5)).
        """
        depth_bid_window = rolling_data.get("depth_bid_size_5m")
        depth_ask_window = rolling_data.get("depth_ask_size_5m")

        if direction == "LONG":
            window = depth_bid_window
        else:
            window = depth_ask_window

        if window and window.count > 0:
            current = window.latest
            avg = window.mean
            if current is not None and avg is not None and avg > 0:
                return min(1.0, current / (avg * 1.5))

        # No depth data — return 0 (no size bonus)
        return 0.0

    def _vamp_validation(
        self,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> float:
        """
        VAMP validation score: returns a float 0.0–1.0.

        Positive vamp_mid_dev = bid-weighted = good for LONG.
        Negative vamp_mid_dev = ask-weighted = good for SHORT.

        Returns a soft score used as a signal strength bonus (not a hard gate).
        """
        vamp_levels = rolling_data.get(KEY_VAMP_LEVELS)
        if not vamp_levels:
            return 0.5  # neutral when no data

        vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)

        if direction == "LONG":
            # positive vamp_mid_dev = bid-weighted = good for LONG
            return max(0.0, min(1.0, 0.5 + vamp_mid_dev * 200))
        else:
            # negative vamp_mid_dev = ask-weighted = good for SHORT
            return max(0.0, min(1.0, 0.5 - vamp_mid_dev * 200))

    def _compute_confidence(
        self, bid_participants, ask_participants, bid_exchanges, ask_exchanges,
        bid_conviction, ask_conviction, conviction, direction, rolling_data,
        data, params, regime, gex_calc, depth_score=None,
    ):
        """Combine all factors into a single confidence score — 7 components, weighted average.

        Returns (confidence: float, breakdown: dict) — confidence is 0.0–1.0.
        """
        max_participants_norm = params.get("max_participants_norm", 5.0)
        max_exchanges_norm = params.get("max_exchanges_norm", 4.0)

        # Direction-specific values
        if direction == "LONG":
            participants = bid_participants
            exchanges = bid_exchanges
            conviction_score = bid_conviction
        else:
            participants = ask_participants
            exchanges = ask_exchanges
            conviction_score = ask_conviction

        # c1: Participant diversity (weight 0.15)
        c1 = normalize(participants, 0.0, max_participants_norm)

        # c2: Exchange diversity (weight 0.10)
        c2 = normalize(exchanges, 0.0, max_exchanges_norm)

        # c3: Conviction magnitude — lower baseline 0.3 (weight 0.25)
        c3 = normalize(conviction_score, 0.3, 1.0)

        # c4: Conviction ROC — abs(roc) from 0→0.3, higher = higher (weight 0.10)
        roc = 0.0
        conviction_window = rolling_data.get(KEY_CONVICT_SCORE_5M)
        if conviction_window and conviction_window.count >= 5 and conviction_window.values[-5] > 0:
            roc = (conviction_score - conviction_window.values[-5]) / conviction_window.values[-5]
        c4 = normalize(abs(roc), 0.0, 0.3)

        # c5: Volume confirmation — vol_ratio from 0→2.0, higher = higher (weight 0.10)
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        vol_ratio = 1.0
        if volume_window and volume_window.count > 0 and volume_window.mean > 0:
            vol_ratio = volume_window.latest / volume_window.mean
        c5 = normalize(vol_ratio, 0.0, 2.0)

        # c6: Regime alignment (weight 0.15)
        regime = str(regime).lower() if regime else ""
        if "trend" in regime:
            c6 = 0.7
        elif "rang" in regime:
            c6 = 0.4
        else:
            c6 = 0.4

        # c7: GEX alignment (weight 0.15)
        try:
            net_gamma = 0.0
            if gex_calc and isinstance(gex_calc, dict):
                net_gamma = gex_calc.get("net_gamma", 0.0)
            if direction == "LONG":
                if net_gamma > 0.01:
                    c7 = 1.0
                elif net_gamma < -0.01:
                    c7 = 0.2
                else:
                    c7 = 0.5
            else:  # SHORT
                if net_gamma < -0.01:
                    c7 = 1.0
                elif net_gamma > 0.01:
                    c7 = 0.2
                else:
                    c7 = 0.5
        except Exception:
            c7 = 0.5

        # Weighted average
        confidence = (
            c1 * 0.15 +
            c2 * 0.10 +
            c3 * 0.25 +
            c4 * 0.10 +
            c5 * 0.10 +
            c6 * 0.15 +
            c7 * 0.15
        )
        confidence = min(1.0, max(0.0, confidence))

        breakdown = {
            "c1_participant": round(c1, 3),
            "c2_exchange": round(c2, 3),
            "c3_conviction": round(c3, 3),
            "c4_roc": round(c4, 3),
            "c5_volume": round(c5, 3),
            "c6_regime": round(c6, 3),
            "c7_gex": round(c7, 3),
        }
        return confidence, breakdown
