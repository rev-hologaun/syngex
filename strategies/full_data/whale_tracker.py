"""
strategies/full_data/whale_tracker.py — Whale Tracker (CONCENTRATION-ALPHA)

Detects institutional "whale" orders by analyzing size concentration ratio.
Ω_conc = biggest_size / smallest_size at best price levels.

Bullish: Ω_conc > 5σ AND num_participants ≤ 2 AND bid-side concentration → LONG
Bearish: Ω_conc > 5σ AND num_participants ≤ 2 AND ask-side concentration → SHORT
Filters out retail "noise" by requiring low participant count at large orders.

Trigger: Concentration ratio > 5σ above rolling avg AND num_participants ≤ 2

Hard gates (ALL must pass):
    Gate A: Whale threshold — biggest_size > 5σ above rolling avg
    Gate B: Single-entity filter — num_participants ≤ 2 at concentrated level
    Gate C: Gamma coincidence — concentration near gamma wall (optional, highest conviction)

Confidence model (5 components):
    1. Concentration magnitude (0.0–0.30) — Ω_conc in σ units
    2. Participant conviction (0.0–0.20) — low participant count = high conviction
    3. Size anomaly (0.0–0.15) — biggest_size > 3σ above avg
    4. Gamma coincidence (0.0–0.10) — concentration near gamma wall
    5. GEX regime alignment (0.0–0.10) — signal direction matches GEX bias
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_BIGGEST_SIZE_5M,
    KEY_SMALLEST_SIZE_5M,
    KEY_CONCENTRATION_RATIO_5M,
    KEY_CONCENTRATION_SIGMA_5M,
    KEY_NUM_PARTICIPANTS_5M,
)

logger = logging.getLogger("Syngex.Strategies.WhaleTracker")


class WhaleTracker(BaseStrategy):
    """
    Whale Tracker strategy — detects institutional "whale" orders via
    size concentration ratio at best price levels.

    Ω_conc = biggest_size / smallest_size at the best N price levels.
    A high ratio means one participant is placing a very large order while
    others are small — classic whale signature.

    LONG: bid-side concentration > 5σ AND num_participants ≤ 2
          AND GEX regime is POSITIVE
    SHORT: ask-side concentration > 5σ AND num_participants ≤ 2
           AND GEX regime is NEGATIVE
    """

    strategy_id = "whale_tracker"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for whale concentration signal.

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

        # 1. Get concentration data from rolling windows
        min_conc_data_points = params.get("min_conc_sigma", 5.0)
        max_participants = params.get("max_participants", 2)
        min_biggest_size_sigma = params.get("min_biggest_size_sigma", 3.0)

        biggest_window = rolling_data.get(KEY_BIGGEST_SIZE_5M)
        smallest_window = rolling_data.get(KEY_SMALLEST_SIZE_5M)
        conc_ratio_window = rolling_data.get(KEY_CONCENTRATION_RATIO_5M)
        conc_sigma_window = rolling_data.get(KEY_CONCENTRATION_SIGMA_5M)
        participants_window = rolling_data.get(KEY_NUM_PARTICIPANTS_5M)

        # Need enough data for meaningful statistics
        if not conc_ratio_window or conc_ratio_window.count < 10:
            return []
        if not conc_sigma_window or conc_sigma_window.count < 5:
            return []
        if not biggest_window or biggest_window.count < 10:
            return []

        current_conc_ratio = conc_ratio_window.values[-1]
        current_conc_sigma = conc_sigma_window.values[-1] if conc_sigma_window else 0.0
        current_biggest = biggest_window.values[-1] if biggest_window else 0
        current_smallest = smallest_window.values[-1] if smallest_window else 0
        current_participants = (
            participants_window.values[-1] if participants_window else 0
        )

        # 2. Determine signal direction based on which side is more concentrated
        # Extract side info from the last depth aggregate if available
        depth_data = rolling_data.get("market_depth_agg", {})
        bid_levels = depth_data.get("bid_levels", [])
        ask_levels = depth_data.get("ask_levels", [])

        # Compute per-side concentration from latest depth
        bid_conc_ratio = self._compute_side_concentration(bid_levels)
        ask_conc_ratio = self._compute_side_concentration(ask_levels)

        if bid_conc_ratio <= 0 and ask_conc_ratio <= 0:
            return []

        long_signal = bid_conc_ratio > ask_conc_ratio
        short_signal = ask_conc_ratio > bid_conc_ratio

        if not long_signal and not short_signal:
            return []

        if long_signal and short_signal:
            direction = "LONG" if bid_conc_ratio >= ask_conc_ratio else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Check if concentration exceeds σ threshold
        if current_conc_sigma <= 0:
            return []

        conc_zscore = current_conc_ratio / current_conc_sigma

        min_conc_sigma_threshold = params.get("min_conc_sigma", 5.0)
        if conc_zscore < min_conc_sigma_threshold:
            logger.debug(
                "Whale Tracker: Conc z-score %.1f below threshold %.1f for %s",
                conc_zscore, min_conc_sigma_threshold, direction,
            )
            return []

        # 4. Apply 3 HARD GATES
        gate_a = self._gate_a_whale_threshold(
            current_biggest, biggest_window, min_biggest_size_sigma
        )

        if not gate_a:
            logger.debug(
                "Whale Tracker: Gate A failed — biggest_size not extreme enough for %s",
                direction,
            )
            return []

        gate_b = self._gate_b_single_entity(
            current_participants, max_participants, direction
        )

        if not gate_b:
            logger.debug(
                "Whale Tracker: Gate B failed — too many participants for %s",
                direction,
            )
            return []

        gate_c = self._gate_c_gex_regime(direction, regime)

        if not gate_c:
            logger.debug(
                "Whale Tracker: Gate C failed — GEX regime misalignment for %s",
                direction,
            )
            return []

        # 5. Compute confidence (5-component model)
        confidence = self._compute_confidence(
            current_conc_ratio,
            current_conc_sigma,
            conc_zscore,
            current_biggest,
            biggest_window,
            current_participants,
            direction,
            params,
            regime,
            gex_calc,
            data,
        )

        min_confidence = params.get("min_confidence", 0.35)
        max_confidence = params.get("max_confidence", 0.85)
        confidence = max(min_confidence, min(confidence, max_confidence))

        if confidence < min_confidence:
            return []

        # 6. Build signal with entry/stop/target
        stop_pct = params.get("stop_pct", 0.005)
        target_risk_mult = params.get("target_risk_mult", 2.0)

        entry = underlying_price
        stop_distance = entry * stop_pct

        if direction == "LONG":
            stop = entry - stop_distance
            target = entry + (stop_distance * target_risk_mult)
        else:
            stop = entry + stop_distance
            target = entry - (stop_distance * target_risk_mult)

        direction_enum = Direction.LONG if direction == "LONG" else Direction.SHORT

        # Intensity metadata based on σ level
        if conc_zscore > 10.0:
            intensity = "red"
        elif conc_zscore > 5.0:
            intensity = "orange"
        else:
            intensity = "yellow"

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Whale concentration {direction}: Ω={current_conc_ratio:.1f}, "
                f"z={conc_zscore:.1f}σ, participants={current_participants}"
            ),
            metadata={
                "direction": direction,
                "conc_ratio": round(current_conc_ratio, 4),
                "conc_sigma": round(current_conc_sigma, 6),
                "conc_zscore": round(conc_zscore, 2),
                "biggest_size": round(current_biggest, 2),
                "smallest_size": round(current_smallest, 2),
                "num_participants": round(current_participants, 2),
                "intensity": intensity,
                "regime": regime,
                "gates": {
                    "A_whale_threshold": gate_a,
                    "B_single_entity": gate_b,
                    "C_gex_regime": gate_c,
                },
            },
        )]

    def _compute_side_concentration(self, levels: List[Dict[str, Any]]) -> float:
        """
        Compute concentration ratio for one side of the book.
        Ω = max_size / min_size among non-zero levels.
        """
        sizes = [
            int(l.get("size", 0))
            for l in levels
            if int(l.get("size", 0)) > 0
        ]
        if not sizes or len(sizes) < 2:
            return 0.0
        return max(sizes) / min(sizes)

    def _gate_a_whale_threshold(
        self,
        current_biggest: float,
        biggest_window: Any,
        min_biggest_size_sigma: float,
    ) -> bool:
        """
        Gate A: Whale threshold.

        The biggest size must be meaningfully above the rolling average.
        We check that the biggest size is > min_biggest_size_sigma σ above
        the rolling mean of biggest sizes.
        """
        if not biggest_window or biggest_window.count < 10:
            return False

        mean_biggest = biggest_window.mean
        sigma_biggest = biggest_window.std if hasattr(biggest_window, 'std') else 0

        if sigma_biggest <= 0 or mean_biggest <= 0:
            return False

        zscore = (current_biggest - mean_biggest) / sigma_biggest
        return zscore >= min_biggest_size_sigma

    def _gate_b_single_entity(
        self,
        current_participants: float,
        max_participants: int,
        direction: str,
    ) -> bool:
        """
        Gate B: Single-entity filter.

        Low participant count at the concentrated level means a single
        entity (institution) is behind the order, not retail fragmentation.
        """
        return current_participants <= max_participants

    def _gate_c_gex_regime(
        self,
        direction: str,
        regime: str,
    ) -> bool:
        """
        Gate C: GEX regime alignment.

        LONG signals require POSITIVE gamma regime (market makers hedging
        by buying dips, supporting the long thesis).
        SHORT signals require NEGATIVE gamma regime (market makers hedging
        by selling rallies, supporting the short thesis).
        """
        if direction == "LONG" and regime == "POSITIVE":
            return True
        if direction == "SHORT" and regime == "NEGATIVE":
            return True
        return False

    def _compute_confidence(
        self,
        current_conc_ratio: float,
        current_conc_sigma: float,
        conc_zscore: float,
        current_biggest: float,
        biggest_window: Any,
        current_participants: float,
        direction: str,
        params: Dict[str, Any],
        regime: str,
        gex_calc: Any,
        data: Dict[str, Any],
    ) -> float:
        """
        Compute 5-component confidence score.

        Returns 0.0–1.0.
        """
        min_conc_sigma_threshold = params.get("min_conc_sigma", 5.0)
        max_participants = params.get("max_participants", 2)

        # 1. Concentration magnitude (0.0–0.30)
        # How many σ the concentration ratio is — higher = more conviction
        conf_conc = 0.0
        if current_conc_sigma > 0:
            # Scale: at threshold = baseline 0.15, above = bonus
            conf_conc = min(
                0.30,
                0.15 + 0.15 * min(
                    1.0,
                    (conc_zscore - min_conc_sigma_threshold)
                    / min_conc_sigma_threshold,
                ),
            )
            conf_conc = max(0.10, conf_conc)

        # 2. Participant conviction (0.0–0.20)
        # Fewer participants = higher conviction (single entity)
        conf_participants = 0.0
        if current_participants <= 1:
            conf_participants = 0.20
        elif current_participants <= max_participants:
            # Linear interpolation: 2 participants = baseline, 1 = max
            conf_participants = 0.10 + 0.10 * (
                1.0 - (current_participants - 1) / max(1, max_participants - 1)
            )
        else:
            # More than max — should have been filtered by gate B
            conf_participants = 0.0

        # 3. Size anomaly (0.0–0.15)
        # Biggest size > 3σ above rolling average
        conf_size = 0.0
        if biggest_window and biggest_window.count >= 10:
            mean_biggest = biggest_window.mean
            sigma_biggest = biggest_window.std if hasattr(biggest_window, 'std') else 0
            if sigma_biggest > 0 and mean_biggest > 0:
                size_zscore = (current_biggest - mean_biggest) / sigma_biggest
                conf_size = min(
                    0.15,
                    0.05 + 0.10 * min(1.0, max(0, (size_zscore - 3.0) / 2.0)),
                )

        # 4. Gamma coincidence (0.0–0.10)
        # Concentration near a gamma wall = highest conviction
        # (We check if there's a gamma wall nearby)
        conf_gamma = 0.05  # baseline (gate C already passed)
        wall_distance = data.get("wall_distance", float('inf'))
        gamma_wall_gex = params.get("gamma_wall_gex", 0)
        if gamma_wall_gex > 0 and wall_distance < 0.01:
            conf_gamma = 0.10

        # 5. GEX regime alignment (0.0–0.10)
        # Signal direction matches GEX bias
        conf_gex = 0.05  # baseline (gate C already passed)
        if gex_calc and regime:
            net_gamma = (
                gex_calc.get_net_gamma()
                if hasattr(gex_calc, "get_net_gamma")
                else 0
            )
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
            conf_conc + conf_participants + conf_size +
            conf_gamma + conf_gex
        )
        return min(1.0, max(0.0, confidence))
