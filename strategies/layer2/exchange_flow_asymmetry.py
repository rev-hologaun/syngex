"""
strategies/layer2/exchange_flow_asymmetry.py — Exchange Flow Asymmetry

Venue-signature tracking strategy. MEMX is the home of institutional
accumulation (heavy bid-side liquidity). BATS is the epicenter of momentum
sweeps. By tracking signature deviation — when a venue's behavior diverges
from its own historical baseline — we detect genuine flow shifts.

LONG: MEMX ESI > 0.8 + ROC > 0 + volume spike + baseline deviation > 0.15
      AND cross-venue confluence AND book alignment AND spread check

SHORT: BATS ESI < -0.8 + ROC < 0 + volume spike + baseline deviation < -0.15
       AND cross-venue confluence AND book alignment AND spread check

Hard gates (all must pass):
    Gate A: Cross-Venue Confluence — at least one other exchange (EDGX, ARCA)
            shows non-trivial movement. Prevents ghost orders.
    Gate B: Total Book Alignment — OBI (overall bid/ask imbalance) moves in
            the same direction as the venue ESI.
    Gate C: Volume Threshold — venue volume > 1.5× its 5-minute moving average.

Confidence model (5 components, sum to 1.0):
    1. ESI magnitude              (0.0–0.30) — how extreme the venue imbalance is
    2. Baseline deviation         (0.0–0.25) — z-score of deviation from 1h baseline
    3. Volume confirmation        (0.0–0.20) — volume ratio above 1.5×
    4. Book alignment             (0.0–0.15) — OBI direction matches venue ESI direction
    5. Cross-venue confluence     (0.0–0.10) — other exchanges also participating
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_ESI_MEMX_5M,
    KEY_ESI_MEMX_ROC_5M,
    KEY_ESI_BATS_5M,
    KEY_ESI_BATS_ROC_5M,
    KEY_MEMX_VOL_RATIO_5M,
    KEY_BATS_VOL_RATIO_5M,
    KEY_ESI_BASELINE_MEMX_1H,
    KEY_ESI_BASELINE_BATS_1H,
    KEY_DEPTH_SPREAD_5M,
    KEY_OBI_5M,
)

logger = logging.getLogger("Syngex.Strategies.ExchangeFlowAsymmetry")


class ExchangeFlowAsymmetry(BaseStrategy):
    """
    Exchange Flow Asymmetry strategy — venue-signature tracking.

    Tracks venue-specific ESI (Effective Spread Imbalance) on MEMX and BATS.
    When a venue's ESI diverges significantly from its 1-hour baseline
    while volume spikes, it signals genuine flow-driven movement.

    LONG: MEMX ESI > 0.8 + ROC > 0 + volume spike + baseline deviation
    SHORT: BATS ESI < -0.8 + ROC < 0 + volume spike + baseline deviation
    """

    strategy_id = "exchange_flow_asymmetry"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for exchange flow asymmetry signal.

        Returns a single LONG or SHORT signal when conditions are met,
        or empty list when gates fail or no clear signal.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params

        # 1. Get ESI and related metrics from rolling windows
        min_data_points = params.get("min_data_points", 10)

        esi_memx_window = rolling_data.get(KEY_ESI_MEMX_5M)
        esi_memx_roc_window = rolling_data.get(KEY_ESI_MEMX_ROC_5M)
        esi_bats_window = rolling_data.get(KEY_ESI_BATS_5M)
        esi_bats_roc_window = rolling_data.get(KEY_ESI_BATS_ROC_5M)
        memx_vol_ratio_window = rolling_data.get(KEY_MEMX_VOL_RATIO_5M)
        bats_vol_ratio_window = rolling_data.get(KEY_BATS_VOL_RATIO_5M)
        baseline_memx_window = rolling_data.get(KEY_ESI_BASELINE_MEMX_1H)
        baseline_bats_window = rolling_data.get(KEY_ESI_BASELINE_BATS_1H)

        if not esi_memx_window or esi_memx_window.count < min_data_points:
            return []
        if not esi_bats_window or esi_bats_window.count < min_data_points:
            return []
        if not esi_memx_roc_window or esi_memx_roc_window.count < 5:
            return []
        if not esi_bats_roc_window or esi_bats_roc_window.count < 5:
            return []

        current_esi_memx = esi_memx_window.values[-1]
        current_esi_memx_roc = esi_memx_roc_window.values[-1]
        current_esi_bats = esi_bats_window.values[-1]
        current_esi_bats_roc = esi_bats_roc_window.values[-1]

        current_memx_vol_ratio = (
            memx_vol_ratio_window.values[-1]
            if memx_vol_ratio_window and memx_vol_ratio_window.count > 0
            else 0.0
        )
        current_bats_vol_ratio = (
            bats_vol_ratio_window.values[-1]
            if bats_vol_ratio_window and bats_vol_ratio_window.count > 0
            else 0.0
        )

        current_baseline_memx = (
            baseline_memx_window.values[-1]
            if baseline_memx_window and baseline_memx_window.count > 0
            else 0.0
        )
        current_baseline_bats = (
            baseline_bats_window.values[-1]
            if baseline_bats_window and baseline_bats_window.count > 0
            else 0.0
        )

        memx_deviation = current_esi_memx - current_baseline_memx
        bats_deviation = current_esi_bats - current_baseline_bats

        # 2. OBI for book alignment (Gate B)
        obi_window = rolling_data.get(KEY_OBI_5M)
        current_obi = (
            obi_window.values[-1]
            if obi_window and obi_window.count > 0
            else 0.0
        )

        # 3. Exchange sizes for cross-venue confluence (Gate A)
        exchange_data = data.get("exchange_data", {})
        exchange_bid_sizes = exchange_data.get("bid_sizes", {})
        exchange_ask_sizes = exchange_data.get("ask_sizes", {})
        edgx_bid = exchange_bid_sizes.get("EDGX", 0)
        edgx_ask = exchange_ask_sizes.get("EDGX", 0)
        arca_bid = exchange_ask_sizes.get("ARCA", 0)
        arca_ask = exchange_ask_sizes.get("ARCA", 0)

        # 4. Determine signal direction
        esi_threshold = params.get("esi_threshold", 0.8)
        memx_deviation_threshold = params.get("memx_deviation_threshold", 0.15)
        bats_deviation_threshold = params.get("bats_deviation_threshold", -0.15)
        volume_ratio_threshold = params.get("volume_ratio_threshold", 1.5)

        long_signal = (
            current_esi_memx > esi_threshold
            and current_esi_memx_roc > 0
            and current_memx_vol_ratio > volume_ratio_threshold
            and memx_deviation > memx_deviation_threshold
        )
        short_signal = (
            current_esi_bats < -esi_threshold
            and current_esi_bats_roc < 0
            and current_bats_vol_ratio > volume_ratio_threshold
            and bats_deviation < bats_deviation_threshold
        )

        if not long_signal and not short_signal:
            return []

        # Only emit one signal per evaluation (LONG or SHORT, not both)
        if long_signal and short_signal:
            long_strength = current_esi_memx - esi_threshold
            short_strength = -esi_threshold - current_esi_bats
            direction = "LONG" if long_strength >= short_strength else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 5. Apply 3 HARD GATES
        gate_a = self._gate_a_cross_venue(
            direction, exchange_bid_sizes, exchange_ask_sizes, data
        )
        if not gate_a:
            logger.debug(
                "Flow Asymmetry: Gate A failed — no cross-venue confluence for %s",
                direction,
            )
            return []

        gate_b = self._gate_b_book_alignment(
            direction, current_obi, current_esi_memx, current_esi_bats
        )
        if not gate_b:
            logger.debug(
                "Flow Asymmetry: Gate B failed — book misalignment for %s",
                direction,
            )
            return []

        gate_c = self._gate_c_volume(
            direction, current_memx_vol_ratio, current_bats_vol_ratio
        )
        if not gate_c:
            logger.debug(
                "Flow Asymmetry: Gate C failed — volume below threshold for %s",
                direction,
            )
            return []

        gate_d = self._gate_d_spread(rolling_data, params)
        if not gate_d:
            logger.debug(
                "Flow Asymmetry: Gate D failed — spread too wide for %s",
                direction,
            )
            return []

        # 6. Compute confidence (5-component model)
        confidence = self._compute_confidence(
            direction,
            current_esi_memx,
            current_esi_bats,
            memx_deviation,
            bats_deviation,
            current_memx_vol_ratio,
            current_bats_vol_ratio,
            current_obi,
            exchange_bid_sizes,
            exchange_ask_sizes,
            data,
            params,
        )

        min_confidence = params.get("min_confidence", 0.50)
        max_confidence = params.get("max_confidence", 0.95)
        confidence = max(min_confidence, min(confidence, max_confidence))

        if confidence < min_confidence:
            return []

        # 7. Build signal with entry/stop/target
        stop_pct = params.get("stop_pct", 0.008)
        target_risk_mult = params.get("target_risk_mult", 2.5)

        entry = underlying_price
        stop_distance = entry * stop_pct

        if direction == "LONG":
            stop = entry - stop_distance
            target = entry + (stop_distance * target_risk_mult)
        else:
            stop = entry + stop_distance
            target = entry - (stop_distance * target_risk_mult)

        direction_enum = Direction.LONG if direction == "LONG" else Direction.SHORT

        if direction == "LONG":
            esi_pct = ((current_esi_memx - 0.0) * 100)
            reason = (
                f"MEMX accumulation {direction}: ESI={current_esi_memx:.3f} "
                f"({esi_pct:+.1f}%), dev={memx_deviation:+.3f}, "
                f"vol_ratio={current_memx_vol_ratio:.2f}×"
            )
        else:
            esi_pct = ((0.0 - current_esi_bats) * 100)
            reason = (
                f"BATS sweep {direction}: ESI={current_esi_bats:.3f} "
                f"({esi_pct:+.1f}%), dev={bats_deviation:+.3f}, "
                f"vol_ratio={current_bats_vol_ratio:.2f}×"
            )

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=reason,
            metadata={
                "direction": direction,
                "esi_memx": round(current_esi_memx, 4),
                "esi_memx_roc": round(current_esi_memx_roc, 6),
                "esi_bats": round(current_esi_bats, 4),
                "esi_bats_roc": round(current_esi_bats_roc, 6),
                "memx_deviation": round(memx_deviation, 4),
                "bats_deviation": round(bats_deviation, 4),
                "memx_vol_ratio": round(current_memx_vol_ratio, 4),
                "bats_vol_ratio": round(current_bats_vol_ratio, 4),
                "obi": round(current_obi, 4),
                "gates": {
                    "A_cross_venue": gate_a,
                    "B_book_alignment": gate_b,
                    "C_volume": gate_c,
                    "D_spread": gate_d,
                },
            },
        )]

    def _gate_a_cross_venue(
        self,
        direction: str,
        exchange_bid_sizes: Dict[str, int],
        exchange_ask_sizes: Dict[str, int],
        data: Dict[str, Any],
    ) -> bool:
        """
        Gate A: Cross-Venue Confluence.

        At least one other exchange (EDGX, ARCA) shows non-trivial movement.
        Prevents ghost orders on a single venue.
        """
        # The primary venue depends on signal direction
        primary_venue = "MEMX" if direction == "LONG" else "BATS"
        # Check other exchanges for meaningful participation
        other_exchanges = ["EDGX", "ARCA", "IEX", "EDGA", "BYX", "BZX"]
        participating = 0

        for exch in other_exchanges:
            bid = exchange_bid_sizes.get(exch, 0)
            ask = exchange_ask_sizes.get(exch, 0)
            if (bid + ask) > 0:
                participating += 1

        return participating >= 1

    def _gate_b_book_alignment(
        self,
        direction: str,
        obi: float,
        esi_memx: float,
        esi_bats: float,
    ) -> bool:
        """
        Gate B: Total Book Alignment.

        OBI (overall bid/ask imbalance) moves in the same direction as the
        venue ESI. Confirms the venue signal aligns with the broader book.
        """
        if direction == "LONG":
            # Both OBI and MEMX ESI should be positive
            return obi > 0 and esi_memx > 0
        else:
            # Both OBI and BATS ESI should be negative
            return obi < 0 and esi_bats < 0

    def _gate_c_volume(
        self,
        direction: str,
        memx_vol_ratio: float,
        bats_vol_ratio: float,
    ) -> bool:
        """
        Gate C: Volume Threshold.

        Venue volume > 1.5× its 5-minute moving average.
        """
        if direction == "LONG":
            return memx_vol_ratio > 1.5
        else:
            return bats_vol_ratio > 1.5

    def _gate_d_spread(
        self,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate D: Spread check.

        Current spread must be less than max_spread_mult × average spread
        to ensure the scalp is profitable after transaction costs.
        """
        max_spread_mult = params.get("max_spread_mult", 2.0)
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        if spread_window and spread_window.count > 0:
            current_spread = spread_window.latest
            avg_spread = spread_window.mean
            if current_spread is not None and avg_spread is not None and avg_spread > 0:
                return current_spread < max_spread_mult * avg_spread
        return True  # No spread data — pass gate

    def _compute_confidence(
        self,
        direction: str,
        current_esi_memx: float,
        current_esi_bats: float,
        memx_deviation: float,
        bats_deviation: float,
        current_memx_vol_ratio: float,
        current_bats_vol_ratio: float,
        current_obi: float,
        exchange_bid_sizes: Dict[str, int],
        exchange_ask_sizes: Dict[str, int],
        data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> float:
        """
        Compute 5-component confidence score.

        Returns 0.0–1.0.
        """
        esi_threshold = params.get("esi_threshold", 0.8)
        volume_ratio_threshold = params.get("volume_ratio_threshold", 1.5)

        if direction == "LONG":
            venue_esi = current_esi_memx
            venue_deviation = memx_deviation
            venue_vol_ratio = current_memx_vol_ratio
        else:
            venue_esi = current_esi_bats
            venue_deviation = bats_deviation
            venue_vol_ratio = current_bats_vol_ratio

        # 1. ESI magnitude (0.0–0.30)
        # How extreme the venue imbalance is
        conf_esi = 0.0
        if direction == "LONG" and venue_esi > 0:
            conf_esi = min(0.30, 0.30 * min(1.0, venue_esi / 1.0))
        elif direction == "SHORT" and venue_esi < 0:
            conf_esi = min(0.30, 0.30 * min(1.0, abs(venue_esi) / 1.0))

        # 2. Baseline deviation (0.0–0.25)
        # Z-score style: how far deviation is from zero
        conf_deviation = 0.0
        if direction == "LONG" and venue_deviation > 0:
            conf_deviation = min(0.25, 0.25 * min(1.0, venue_deviation / 0.3))
        elif direction == "SHORT" and venue_deviation < 0:
            conf_deviation = min(0.25, 0.25 * min(1.0, abs(venue_deviation) / 0.3))

        # 3. Volume confirmation (0.0–0.20)
        # Volume ratio above 1.5×
        conf_volume = 0.0
        if venue_vol_ratio > volume_ratio_threshold:
            conf_volume = min(
                0.20,
                0.20 * min(1.0, (venue_vol_ratio - volume_ratio_threshold) / 1.5 + 0.5),
            )

        # 4. Book alignment (0.0–0.15)
        # OBI direction matches venue ESI direction
        conf_alignment = 0.0
        if direction == "LONG" and current_obi > 0 and venue_esi > 0:
            conf_alignment = min(0.15, 0.15 * min(1.0, abs(current_obi) / 0.5))
        elif direction == "SHORT" and current_obi < 0 and venue_esi < 0:
            conf_alignment = min(0.15, 0.15 * min(1.0, abs(current_obi) / 0.5))

        # 5. Cross-venue confluence (0.0–0.10)
        # Other exchanges also participating
        conf_confluence = 0.0
        other_exchanges = ["EDGX", "ARCA", "IEX", "EDGA", "BYX", "BZX"]
        participating = 0
        for exch in other_exchanges:
            bid = exchange_bid_sizes.get(exch, 0)
            ask = exchange_ask_sizes.get(exch, 0)
            if (bid + ask) > 0:
                participating += 1
        conf_confluence = min(0.10, 0.10 * min(1.0, participating / 2.0))

        confidence = (
            conf_esi + conf_deviation + conf_volume +
            conf_alignment + conf_confluence
        )
        return min(1.0, max(0.0, confidence))
