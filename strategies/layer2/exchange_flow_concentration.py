"""
strategies/layer2/exchange_flow_concentration.py — Exchange Flow Concentration

Venue-specific flow concentration strategy. MEMX and BATS are aggressive
execution venues — HFTs and institutional algos sweep there. IEX has a speed
bump and is known for passive, intent-driven liquidity.

Core insight: A surge in bid/ask ratio specifically on MEMX or BATS signals
aggressive directional flow. An IEX intent score filters out spoofed walls.

LONG: VSI_COMBINED > 2.0 (heavy bid pressure on aggressive venues)
      AND VSI_ROC > 0 (imbalance rising)

SHORT: VSI_COMBINED < 0.5 (heavy ask pressure on aggressive venues)
       AND VSI_ROC < 0 (imbalance falling)

Hard gates (all must pass):
    Gate A: signal_venue_size / total_depth >= 0.15 (exchange dominance)
    Gate B: iex_intent <= 0.35 (not spoofed)
    Gate C: current_vol >= avg_vol * 0.8 (volume confirmation)

Confidence model (7 components):
    1. VSI magnitude              (0.0–0.25) — how extreme the VSI is
    2. VSI ROC strength           (0.0–0.20) — how fast imbalance changes
    3. Exchange dominance         (0.0–0.15) — what % of total book is on signal venue
    4. IEX intent clean           (0.0–0.10) — low IEX = high conviction
    5. Volume confirmation        (0.0–0.10) — volume above average
    6. VAMP validation            (0.0–0.10) — VAMP direction aligns with signal
    7. GEX regime alignment       (0.0–0.10) — signal direction matches GEX bias
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_VSI_COMBINED_5M,
    KEY_VSI_ROC_5M,
    KEY_IEX_INTENT_5M,
    KEY_VOLUME_5M,
)

logger = logging.getLogger("Syngex.Strategies.ExchangeFlowConcentration")

MIN_CONFIDENCE = 0.30


class ExchangeFlowConcentration(BaseStrategy):
    """
    Exchange Flow Concentration strategy — venue-specific flow analysis.

    Tracks bid/ask ratio specifically on aggressive execution venues (MEMX, BATS)
    and uses IEX intent as a spoofing filter. When the bid/ask ratio on aggressive
    venues becomes extreme and is rising, it signals genuine directional flow.

    LONG: VSI_COMBINED > 2.0 (heavy bid pressure on aggressive venues)
          AND VSI_ROC > 0 (imbalance rising)

    SHORT: VSI_COMBINED < 0.5 (heavy ask pressure on aggressive venues)
           AND VSI_ROC < 0 (imbalance falling)
    """

    strategy_id = "exchange_flow_concentration"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for exchange flow concentration signal.

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

        # 1. Get VSI and IEX intent from rolling windows
        min_vsi_data_points = params.get("min_vsi_data_points", 10)
        vsi_window = rolling_data.get(KEY_VSI_COMBINED_5M)
        vsi_roc_window = rolling_data.get(KEY_VSI_ROC_5M)
        iex_intent_window = rolling_data.get(KEY_IEX_INTENT_5M)

        if not vsi_window or vsi_window.count < min_vsi_data_points:
            return []
        if not vsi_roc_window or vsi_roc_window.count < 5:
            return []

        current_vsi = vsi_window.values[-1]
        current_vsi_roc = vsi_roc_window.values[-1]
        current_iex_intent = iex_intent_window.values[-1] if iex_intent_window else 0.0

        # 2. Determine signal direction
        vsi_threshold_long = params.get("vsi_threshold_long", 2.0)
        vsi_threshold_short = params.get("vsi_threshold_short", 0.5)
        vsi_roc_threshold_long = params.get("vsi_roc_threshold_long", 0.0)
        vsi_roc_threshold_short = params.get("vsi_roc_threshold_short", 0.0)

        long_signal = (current_vsi > vsi_threshold_long and
                       current_vsi_roc > vsi_roc_threshold_long)
        short_signal = (current_vsi < vsi_threshold_short and
                        current_vsi_roc < vsi_roc_threshold_short)

        if not long_signal and not short_signal:
            return []

        # Only emit one signal per evaluation (LONG or SHORT, not both)
        if long_signal and short_signal:
            long_extreme = current_vsi - vsi_threshold_long
            short_extreme = vsi_threshold_short - current_vsi
            direction = "LONG" if long_extreme >= short_extreme else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Apply 3 HARD GATES
        gate_a = self._gate_a_exchange_dominance(data, params, direction)

        if not gate_a:
            logger.debug(
                "Exchange Flow: Gate A failed — exchange dominance below threshold for %s",
                direction,
            )
            return []

        gate_b = self._gate_b_iex_intent(current_iex_intent, params)

        if not gate_b:
            logger.debug(
                "Exchange Flow: Gate B failed — IEX intent too high for %s",
                direction,
            )
            return []

        gate_c = self._gate_c_volume(rolling_data, params)

        if not gate_c:
            logger.debug(
                "Exchange Flow: Gate C failed — volume below MA for %s",
                direction,
            )
            return []

        # 4. VAMP validation (optional)
        use_vamp_validation = params.get("use_vamp_validation", True)
        vamp_validated = True
        if use_vamp_validation:
            vamp_validated = self._vamp_validation(rolling_data, direction)

        if not vamp_validated:
            logger.debug(
                "Exchange Flow: VAMP validation failed for %s", direction,
            )
            return []

        # 5. Compute confidence (7-component model)
        confidence = self._compute_confidence(
            current_vsi, current_vsi_roc, current_iex_intent, direction,
            rolling_data, data, params,
            regime, gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 6. Build signal with entry/stop/target
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

        vsi_pct = ((current_vsi - 1.0) * 100) if direction == "LONG" else ((1.0 - current_vsi) * 100)

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Exchange flow {direction}: VSI={current_vsi:.2f} "
                f"({vsi_pct:+.1f}%), ROC={current_vsi_roc:+.4f}"
            ),
            metadata={
                "direction": direction,
                "vsi": round(current_vsi, 4),
                "vsi_pct": round(vsi_pct, 2),
                "vsi_roc": round(current_vsi_roc, 6),
                "vsi_roc_pct": round(current_vsi_roc * 100, 2),
                "iex_intent": round(current_iex_intent, 4),
                "gates": {
                    "A_exchange_dominance": gate_a,
                    "B_iex_intent": gate_b,
                    "C_volume": gate_c,
                    "D_vamp": vamp_validated,
                },
                "regime": regime,
            },
        )]

    def _gate_a_exchange_dominance(
        self,
        data: Dict[str, Any],
        params: Dict[str, Any],
        direction: str,
    ) -> bool:
        """
        Gate A: Exchange dominance.

        The venue-specific bid+ask (MEMX or BATS) must account for >= 15%
        of total book depth on the signal side.
        """
        depth_snapshot = data.get("depth_snapshot")
        if not depth_snapshot:
            # No depth snapshot — check rolling data for exchange sizes
            exchange_sizes = data.get("exchange_sizes")
            if not exchange_sizes:
                return True  # Can't evaluate — pass
        else:
            exchange_sizes = depth_snapshot.get("exchange_sizes")
            if not exchange_sizes:
                return True

        total_depth = depth_snapshot.get("total_depth", 0)
        if total_depth <= 0:
            return True

        min_dominance = params.get("min_exchange_dominance", 0.15)

        if direction == "LONG":
            signal_venue_size = exchange_sizes.get("memx_bid", 0) + exchange_sizes.get("bats_bid", 0)
        else:
            signal_venue_size = exchange_sizes.get("memx_ask", 0) + exchange_sizes.get("bats_ask", 0)

        dominance = signal_venue_size / total_depth
        return dominance >= min_dominance

    def _gate_b_iex_intent(
        self,
        iex_intent: float,
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate B: IEX intent filter.

        IEX intent score must be below threshold — high IEX intent
        means passive/spoofed liquidity, not genuine flow.
        """
        max_iex_intent = params.get("max_iex_intent", 0.35)
        return iex_intent <= max_iex_intent

    def _gate_c_volume(
        self,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate C: Volume confirmation.

        Current volume should be at least volume_min_mult × MA(volume).
        """
        volume_min_mult = params.get("volume_min_mult", 0.8)
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0:
            current_vol = volume_window.latest
            avg_vol = volume_window.mean
            if current_vol is not None and avg_vol is not None and avg_vol > 0:
                return current_vol >= avg_vol * volume_min_mult

        # No volume data — pass gate (can't evaluate)
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
        current_vsi: float,
        current_vsi_roc: float,
        current_iex_intent: float,
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
        # 1. VSI magnitude (0.0–0.25)
        # How extreme the VSI is — at threshold = baseline, above = bonus
        vsi_threshold = params.get("vsi_threshold_long", 2.0) if direction == "LONG" else params.get("vsi_threshold_short", 0.5)
        conf_vsi = 0.0
        if direction == "LONG":
            # VSI > 2.0 = strong; scale from 0 at VSI=1.0 to 0.25 at VSI=4.0+
            if current_vsi > 1.0:
                conf_vsi = min(0.25, 0.25 * min(1.0, (current_vsi - 1.0) / 3.0))
        else:
            # VSI < 0.5 = strong; scale from 0 at VSI=1.0 to 0.25 at VSI=0.1
            if current_vsi < 1.0:
                conf_vsi = min(0.25, 0.25 * min(1.0, (1.0 - current_vsi) / 0.4))

        # 2. VSI ROC strength (0.0–0.20)
        # How fast the imbalance is changing
        conf_roc = 0.0
        if direction == "LONG" and current_vsi_roc > 0:
            conf_roc = min(0.20, 0.20 * min(1.0, current_vsi_roc / 0.5))
        elif direction == "SHORT" and current_vsi_roc < 0:
            conf_roc = min(0.20, 0.20 * min(1.0, abs(current_vsi_roc) / 0.5))

        # 3. Exchange dominance (0.0–0.15)
        # What % of total book is on the signal venue
        min_dominance = params.get("min_exchange_dominance", 0.15)
        conf_dominance = 0.05  # baseline (gate A already passed)
        exchange_sizes = data.get("exchange_sizes")
        depth_snapshot = data.get("depth_snapshot")
        if exchange_sizes:
            total_depth = depth_snapshot.get("total_depth", 0) if depth_snapshot else 0
        elif depth_snapshot:
            total_depth = depth_snapshot.get("total_depth", 0)
        else:
            total_depth = 0

        if total_depth > 0 and exchange_sizes:
            if direction == "LONG":
                signal_venue_size = exchange_sizes.get("memx_bid", 0) + exchange_sizes.get("bats_bid", 0)
            else:
                signal_venue_size = exchange_sizes.get("memx_ask", 0) + exchange_sizes.get("bats_ask", 0)
            dominance = signal_venue_size / total_depth
            # Scale: at threshold = 0.10, at 2× threshold = 0.15
            if dominance > min_dominance:
                conf_dominance = 0.10 + 0.05 * min(
                    1.0, (dominance - min_dominance) / min_dominance
                )

        # 4. IEX intent clean (0.0–0.10)
        # Low IEX intent = high conviction (genuine flow on aggressive venues)
        max_iex_intent = params.get("max_iex_intent", 0.35)
        conf_iex = 0.05  # baseline (gate B already passed)
        if current_iex_intent <= max_iex_intent * 0.5:
            conf_iex = 0.10
        elif current_iex_intent <= max_iex_intent:
            conf_iex = 0.05 + 0.05 * (1.0 - current_iex_intent / max_iex_intent)

        # 5. Volume confirmation (0.0–0.10)
        # Volume above average
        volume_min_mult = params.get("volume_min_mult", 0.8)
        conf_volume = 0.05  # baseline (gate C already passed)
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0:
            current_vol = volume_window.latest
            avg_vol = volume_window.mean
            if current_vol is not None and avg_vol is not None and avg_vol > 0:
                vol_ratio = current_vol / avg_vol
                conf_volume = 0.05 + 0.05 * min(
                    1.0, (vol_ratio - volume_min_mult) / volume_min_mult
                )

        # 6. VAMP validation (0.0–0.10)
        # VAMP direction aligns with signal
        conf_vamp = 0.05  # baseline (validation already passed)
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
            conf_vsi + conf_roc + conf_dominance +
            conf_iex + conf_volume + conf_vamp + conf_gex
        )
        return min(1.0, max(0.0, confidence))
