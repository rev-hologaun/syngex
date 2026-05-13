"""
strategies/layer2/participant_diversity_conviction.py — Participant Diversity Conviction

Measures institutional conviction by analyzing:
1. Intra-Level Diversity — num_participants per price level (from depth_quotes L2 data)
2. Inter-Exchange Diversity — unique exchanges contributing to a price level

A wall with 4 participants across 3 exchanges = high conviction (institutional).
A wall with 1 participant = likely spoofed.

LONG:  avg_bid_participants >= 3.0 AND bid_exchanges >= 2 AND conviction_score > 0.7
       AND price breakout above recent high

SHORT: avg_ask_participants >= 3.0 AND ask_exchanges >= 2 AND conviction_score > 0.7
       AND price breakdown below recent low

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
)

logger = logging.getLogger("Syngex.Strategies.ParticipantDiversityConviction")

MIN_CONFIDENCE = 0.30


class ParticipantDiversityConviction(BaseStrategy):
    """
    Participant Diversity Conviction strategy — institutional conviction engine.

    Measures whether order book walls are supported by genuine institutional
    participants (multiple participants, multiple exchanges) vs single-player
    spoofed walls.

    LONG:  avg_bid_participants >= 3.0 AND bid_exchanges >= 2 AND conviction_score > 0.7
           AND price breakout above recent high

    SHORT: avg_ask_participants >= 3.0 AND ask_exchanges >= 2 AND conviction_score > 0.7
           AND price breakdown below recent low

    Exit: conviction_score drops < 0.4 OR stop-loss hit
    """

    strategy_id = "participant_diversity_conviction"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for participant diversity conviction signal.

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

        # 1. Get participant/exchange data from rolling windows
        min_data_points = params.get("min_data_points", 10)
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

        # 2. Compute conviction scores per side
        max_participants_norm = params.get("max_participants_norm", 5.0)
        max_exchanges_norm = params.get("max_exchanges_norm", 4.0)

        bid_participant_score = min(1.0, current_bid_participants / max_participants_norm)
        bid_exchange_score = min(1.0, current_bid_exchanges / max_exchanges_norm)
        bid_conviction = bid_participant_score * bid_exchange_score

        ask_participant_score = min(1.0, current_ask_participants / max_participants_norm)
        ask_exchange_score = min(1.0, current_ask_exchanges / max_exchanges_norm)
        ask_conviction = ask_participant_score * ask_exchange_score

        # 3. Determine signal direction
        min_participants = params.get("min_participants", 3.0)
        min_exchanges = params.get("min_exchanges", 2)
        conviction_threshold = params.get("conviction_threshold", 0.7)

        long_signal = (
            current_bid_participants >= min_participants
            and current_bid_exchanges >= min_exchanges
            and bid_conviction > conviction_threshold
        )
        short_signal = (
            current_ask_participants >= min_participants
            and current_ask_exchanges >= min_exchanges
            and ask_conviction > conviction_threshold
        )

        if not long_signal and not short_signal:
            return []

        # Only emit one signal per evaluation
        if long_signal and short_signal:
            long_strength = bid_conviction - conviction_threshold
            short_strength = ask_conviction - conviction_threshold
            direction = "LONG" if long_strength >= short_strength else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 4. Price action confirmation (breakout/breakdown)
        price = data.get("current_price", underlying_price)
        if price <= 0:
            price = underlying_price

        recent_high = data.get("recent_high", 0)
        recent_low = data.get("recent_low", 0)

        if direction == "LONG" and recent_high <= 0:
            # No recent high data — skip price confirmation
            logger.debug("Participant Conviction: No recent high data, skipping price confirmation for LONG")
            return []
        if direction == "SHORT" and recent_low <= 0:
            logger.debug("Participant Conviction: No recent low data, skipping price confirmation for SHORT")
            return []

        if direction == "LONG" and price <= recent_high:
            return []
        if direction == "SHORT" and price >= recent_low:
            return []

        # 5. Apply 3 HARD GATES
        # Gate A: avg_participants >= min_participants (already checked above)
        # Gate B: num_exchanges >= min_exchanges (already checked above)
        # Gate C: current_size >= min_size_ratio × MA(size)

        min_size_ratio = params.get("min_size_ratio", 0.5)
        gate_c = self._gate_c_size_ratio(rolling_data, direction, min_size_ratio)

        if not gate_c:
            logger.debug(
                "Participant Conviction: Gate C failed — size below MA for %s",
                direction,
            )
            return []

        # 6. VAMP validation (optional)
        use_vamp_validation = params.get("use_vamp_validation", True)
        vamp_validated = True
        if use_vamp_validation:
            vamp_validated = self._vamp_validation(rolling_data, direction)

        if not vamp_validated:
            logger.debug(
                "Participant Conviction: VAMP validation failed for %s", direction,
            )
            return []

        # 7. Compute confidence (7-component model)
        confidence = self._compute_confidence(
            bid_participants=current_bid_participants,
            ask_participants=current_ask_participants,
            bid_exchanges=current_bid_exchanges,
            ask_exchanges=current_ask_exchanges,
            bid_conviction=bid_conviction,
            ask_conviction=ask_conviction,
            conviction=current_conviction,
            direction=direction,
            rolling_data=rolling_data,
            data=data,
            params=params,
            regime=regime,
            gex_calc=gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 8. Build signal with entry/stop/target
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
                f"conviction={conviction_pct:.3f}"
            ),
            metadata={
                "direction": direction,
                "bid_participants": round(current_bid_participants, 2),
                "ask_participants": round(current_ask_participants, 2),
                "bid_exchanges": round(current_bid_exchanges, 2),
                "ask_exchanges": round(current_ask_exchanges, 2),
                "bid_conviction": round(bid_conviction, 4),
                "ask_conviction": round(ask_conviction, 4),
                "gates": {
                    "A_participants": True,
                    "B_exchanges": True,
                    "C_size_ratio": gate_c,
                    "D_vamp": vamp_validated,
                },
                "regime": regime,
            },
        )]

    def _gate_c_size_ratio(
        self,
        rolling_data: Dict[str, Any],
        direction: str,
        min_ratio: float,
    ) -> bool:
        """
        Gate C: Size ratio check.

        Current depth size on the signal side should be at least min_ratio × MA(size).
        This filters out flash walls that appear strong momentarily but are
        below historical average depth.
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
                return current >= avg * min_ratio

        # No depth data — pass gate (can't evaluate)
        return True

    def _vamp_validation(
        self,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> bool:
        """
        VAMP validation: VAMP direction should align with signal direction.

        If VAMP is bid-weighted, LONG signals are more credible.
        If VAMP is ask-weighted, SHORT signals are more credible.
        """
        vamp_levels = rolling_data.get("vamp_levels")
        if not vamp_levels:
            return True  # No VAMP data — pass

        vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)

        if direction == "LONG":
            return vamp_mid_dev >= -0.001  # Allow small tolerance
        else:
            return vamp_mid_dev <= 0.001  # Allow small tolerance

    def _compute_confidence(
        self,
        bid_participants: float,
        ask_participants: float,
        bid_exchanges: float,
        ask_exchanges: float,
        bid_conviction: float,
        ask_conviction: float,
        conviction: float,
        direction: str,
        rolling_data: Dict[str, Any],
        data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
        gex_calc: Any,
    ) -> float:
        """
        Compute 7-component confidence score.

        Returns 0.0–1.0.
        """
        max_participants_norm = params.get("max_participants_norm", 5.0)
        max_exchanges_norm = params.get("max_exchanges_norm", 4.0)
        conviction_threshold = params.get("conviction_threshold", 0.7)

        # Direction-specific values
        if direction == "LONG":
            participants = bid_participants
            exchanges = bid_exchanges
            conviction_score = bid_conviction
        else:
            participants = ask_participants
            exchanges = ask_exchanges
            conviction_score = ask_conviction

        # 1. Participant score (0.0–0.25)
        # How diverse the participants are
        conf_participants = 0.0
        participant_score = min(1.0, participants / max_participants_norm)
        # At threshold = baseline, above = bonus
        min_participants = params.get("min_participants", 3.0)
        if participants >= min_participants:
            # Scale: at min_participants = 0.15, at max_participants_norm = 0.25
            conf_participants = 0.15 + 0.10 * min(
                1.0, (participants - min_participants) / (max_participants_norm - min_participants)
            )
        else:
            conf_participants = 0.05 * (participants / min_participants)

        # 2. Exchange score (0.0–0.20)
        # How many exchanges contribute
        conf_exchanges = 0.0
        exchange_score = min(1.0, exchanges / max_exchanges_norm)
        min_exchanges = params.get("min_exchanges", 2)
        if exchanges >= min_exchanges:
            # Scale: at min_exchanges = 0.10, at max_exchanges_norm = 0.20
            conf_exchanges = 0.10 + 0.10 * min(
                1.0, (exchanges - min_exchanges) / (max_exchanges_norm - min_exchanges)
            )
        else:
            conf_exchanges = 0.05 * (exchanges / min_exchanges) if min_exchanges > 0 else 0.0

        # 3. Score magnitude (0.0–0.15)
        # Conviction score vs threshold
        conf_magnitude = 0.0
        if conviction_score > conviction_threshold:
            # Scale: at threshold = 0.08, at 1.0 = 0.15
            conf_magnitude = 0.08 + 0.07 * min(
                1.0, (conviction_score - conviction_threshold) / (1.0 - conviction_threshold)
            )
        elif conviction_score > conviction_threshold * 0.8:
            conf_magnitude = 0.03

        # 4. Score ROC (0.0–0.10)
        # Conviction rising or falling
        conf_roc = 0.0
        conviction_window = rolling_data.get(KEY_CONVICT_SCORE_5M)
        if conviction_window and conviction_window.count >= 5:
            past_conviction = conviction_window.values[-5]
            if past_conviction > 0:
                roc = (conviction_score - past_conviction) / past_conviction
                if direction == "LONG" and roc > 0:
                    conf_roc = min(0.10, 0.10 * min(1.0, roc / 0.3))
                elif direction == "SHORT" and roc < 0:
                    conf_roc = min(0.10, 0.10 * min(1.0, abs(roc) / 0.3))

        # 5. Size correlation (0.0–0.10)
        # Depth size consistent with history
        conf_size = 0.0
        min_size_ratio = params.get("min_size_ratio", 0.5)
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
                size_ratio = current / avg
                # Scale: at min_size_ratio = 0.05, at 1.5× avg = 0.10
                conf_size = 0.05 + 0.05 * min(1.0, (size_ratio - min_size_ratio) / (1.5 - min_size_ratio))

        # 6. VAMP validation (0.0–0.10)
        # VAMP direction aligns with signal
        conf_vamp = 0.05  # baseline
        vamp_levels = rolling_data.get("vamp_levels")
        if vamp_levels:
            vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)
            if direction == "LONG" and vamp_mid_dev >= 0:
                conf_vamp = 0.10
            elif direction == "SHORT" and vamp_mid_dev <= 0:
                conf_vamp = 0.10
            elif abs(vamp_mid_dev) < 0.0005:
                conf_vamp = 0.08

        # 7. GEX regime alignment (0.0–0.10)
        # Signal direction matches GEX bias
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
            conf_participants + conf_exchanges +
            conf_magnitude + conf_roc +
            conf_size + conf_vamp + conf_gex
        )
        return min(1.0, max(0.0, confidence))
