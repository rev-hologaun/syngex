"""
strategies/layer2/exchange_flow_imbalance.py — Exchange Flow Imbalance

Venue-specific order book imbalance strategy. MEMX and BATS are aggressive
execution venues — HFTs and institutional algos sweep there. IEX has a speed
bump and is known for passive, intent-driven liquidity.

Core insight: By tracking venue-specific bid/ask imbalance (VSI) on aggressor
venues (MEMX + BATS), we detect when aggressive flow is driving directional
pressure. The IEX intent score filters out passive-venue games, and venue
concentration confirms that aggressor venues are the ones driving the move.

LONG: Aggressor VSI > 0.3 (heavy bid pressure)
      AND VSI ROC > 0 (imbalance accelerating)
      AND IEX intent low (not a passive venue game)
      AND venue concentration high (aggressors driving the move)

SHORT: Aggressor VSI < -0.3 (heavy ask pressure)
       AND VSI ROC < 0 (imbalance accelerating down)
       AND IEX intent low (not a passive venue game)
       AND venue concentration high (aggressors driving the move)

Hard gates (all must pass):
    Gate A: abs(aggressor_vsi) > vsi_threshold — clear directional pressure
    Gate B: iex_intent_score < iex_threshold — not a passive venue game
    Gate C: venue_concentration > concentration_threshold — aggressor venues driving
    Gate D: spread < max_spread_mult × avg_spread — scalp must be profitable

Confidence model (7 components):
    1. VSI magnitude              (0.0–0.25) — how extreme the VSI is
    2. VSI velocity               (0.0–0.20) — how fast imbalance changes
    3. IEX intent suppression     (0.0–0.15) — low IEX = high conviction
    4. Venue concentration        (0.0–0.10) — what fraction of book imbalance
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
    KEY_AGGRESSOR_VSI_5M,
    KEY_AGGRESSOR_VSI_ROC_5M,
    KEY_IEX_INTENT_SCORE_5M,
    KEY_MEMX_VSI_5M,
    KEY_BATS_VSI_5M,
    KEY_VENUE_CONCENTRATION_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_VOLUME_5M,
)

logger = logging.getLogger("Syngex.Strategies.ExchangeFlowImbalance")


class ExchangeFlowImbalance(BaseStrategy):
    """
    Exchange Flow Imbalance strategy — venue-specific order book analysis.

    Tracks bid/ask ratio specifically on aggressive execution venues (MEMX, BATS)
    combined as an "aggressor book." When the bid/ask ratio on aggressor venues
    becomes extreme and is rising, it signals genuine directional flow.

    LONG: Aggressor VSI > 0.3 AND VSI ROC > 0 AND IEX intent low AND venue concentration high
    SHORT: Aggressor VSI < -0.3 AND VSI ROC < 0 AND IEX intent low AND venue concentration high
    """

    strategy_id = "exchange_flow_imbalance"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for exchange flow imbalance signal.

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

        # 1. Get VSI and related metrics from rolling windows
        min_vsi_data_points = params.get("min_vsi_data_points", 10)
        aggressor_vsi_window = rolling_data.get(KEY_AGGRESSOR_VSI_5M)
        aggressor_vsi_roc_window = rolling_data.get(KEY_AGGRESSOR_VSI_ROC_5M)
        iex_intent_window = rolling_data.get(KEY_IEX_INTENT_SCORE_5M)
        memx_vsi_window = rolling_data.get(KEY_MEMX_VSI_5M)
        bats_vsi_window = rolling_data.get(KEY_BATS_VSI_5M)
        venue_conc_window = rolling_data.get(KEY_VENUE_CONCENTRATION_5M)

        if not aggressor_vsi_window or aggressor_vsi_window.count < min_vsi_data_points:
            return []
        if not aggressor_vsi_roc_window or aggressor_vsi_roc_window.count < 5:
            return []

        current_aggressor_vsi = aggressor_vsi_window.values[-1]
        current_aggressor_vsi_roc = aggressor_vsi_roc_window.values[-1]
        current_iex_intent = iex_intent_window.values[-1] if iex_intent_window else 0.0
        current_memx_vsi = memx_vsi_window.values[-1] if memx_vsi_window else 0.0
        current_bats_vsi = bats_vsi_window.values[-1] if bats_vsi_window else 0.0
        current_venue_conc = venue_conc_window.values[-1] if venue_conc_window else 0.0

        # 2. Determine signal direction
        vsi_threshold = params.get("vsi_threshold", 0.3)
        vsi_roc_threshold = params.get("vsi_roc_threshold", 0.0)
        iex_intent_threshold = params.get("iex_intent_threshold", 0.15)
        venue_conc_threshold = params.get("venue_concentration_threshold", 0.3)

        long_signal = (
            current_aggressor_vsi > vsi_threshold
            and current_aggressor_vsi_roc > vsi_roc_threshold
        )
        short_signal = (
            current_aggressor_vsi < -vsi_threshold
            and current_aggressor_vsi_roc < vsi_roc_threshold
        )

        if not long_signal and not short_signal:
            return []

        # Only emit one signal per evaluation (LONG or SHORT, not both)
        if long_signal and short_signal:
            long_extreme = current_aggressor_vsi - vsi_threshold
            short_extreme = -vsi_threshold - current_aggressor_vsi
            direction = "LONG" if long_extreme >= short_extreme else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Apply 4 HARD GATES
        gate_a = self._gate_a_vsi(current_aggressor_vsi, vsi_threshold)

        if not gate_a:
            logger.debug(
                "Flow Imbalance: Gate A failed — VSI not extreme enough for %s",
                direction,
            )
            return []

        gate_b = self._gate_b_iex_intent(current_iex_intent, iex_intent_threshold)

        if not gate_b:
            logger.debug(
                "Flow Imbalance: Gate B failed — IEX intent too high for %s",
                direction,
            )
            return []

        gate_c = self._gate_c_venue_concentration(
            current_venue_conc, venue_conc_threshold
        )

        if not gate_c:
            logger.debug(
                "Flow Imbalance: Gate C failed — venue concentration too low for %s",
                direction,
            )
            return []

        gate_d = self._gate_d_spread(rolling_data, params)

        if not gate_d:
            logger.debug(
                "Flow Imbalance: Gate D failed — spread too wide for %s",
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
                "Flow Imbalance: VAMP validation failed for %s", direction,
            )
            return []

        # 5. Compute confidence (7-component model)
        confidence = self._compute_confidence(
            current_aggressor_vsi,
            current_aggressor_vsi_roc,
            current_iex_intent,
            current_venue_conc,
            direction,
            rolling_data,
            data,
            params,
            regime,
            gex_calc,
        )

        min_confidence = params.get("min_confidence", 0.40)
        max_confidence = params.get("max_confidence", 0.95)
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

        vsi_pct = (
            ((current_aggressor_vsi - 0.0) * 100)
            if direction == "LONG"
            else ((0.0 - current_aggressor_vsi) * 100)
        )

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Flow imbalance {direction}: AggVSI={current_aggressor_vsi:.3f} "
                f"({vsi_pct:+.1f}%), ROC={current_aggressor_vsi_roc:+.4f}"
            ),
            metadata={
                "direction": direction,
                "aggressor_vsi": round(current_aggressor_vsi, 4),
                "aggressor_vsi_pct": round(vsi_pct, 2),
                "aggressor_vsi_roc": round(current_aggressor_vsi_roc, 6),
                "aggressor_vsi_roc_pct": round(current_aggressor_vsi_roc * 100, 2),
                "memx_vsi": round(current_memx_vsi, 4),
                "bats_vsi": round(current_bats_vsi, 4),
                "iex_intent": round(current_iex_intent, 4),
                "venue_concentration": round(current_venue_conc, 4),
                "gates": {
                    "A_vsi": gate_a,
                    "B_iex_intent": gate_b,
                    "C_venue_concentration": gate_c,
                    "D_spread": gate_d,
                    "D_vamp": vamp_validated,
                },
                "regime": regime,
            },
        )]

    def _gate_a_vsi(self, aggressor_vsi: float, vsi_threshold: float) -> bool:
        """
        Gate A: VSI magnitude.

        The absolute value of aggressor VSI must exceed the threshold,
        indicating clear directional pressure on aggressive venues.
        """
        return abs(aggressor_vsi) > vsi_threshold

    def _gate_b_iex_intent(
        self,
        iex_intent: float,
        iex_threshold: float,
    ) -> bool:
        """
        Gate B: IEX intent suppression.

        IEX intent score must be below threshold — high IEX intent
        means passive/spoofed liquidity, not genuine aggressive flow.
        """
        return iex_intent < iex_threshold

    def _gate_c_venue_concentration(
        self,
        venue_concentration: float,
        concentration_threshold: float,
    ) -> bool:
        """
        Gate C: Venue concentration.

        The fraction of total book imbalance that comes from aggressor venues
        (MEMX + BATS) must exceed the threshold, confirming that aggressive
        venues are driving the move, not passive venues.
        """
        return venue_concentration > concentration_threshold

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

        # No spread data — pass gate (can't evaluate)
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
        current_aggressor_vsi: float,
        current_aggressor_vsi_roc: float,
        current_iex_intent: float,
        current_venue_conc: float,
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
        vsi_threshold = params.get("vsi_threshold", 0.3)
        iex_intent_threshold = params.get("iex_intent_threshold", 0.15)
        venue_conc_threshold = params.get("venue_concentration_threshold", 0.3)

        # 1. VSI magnitude (0.0–0.25)
        # How extreme the VSI is — at threshold = baseline, above = bonus
        conf_vsi = 0.0
        if direction == "LONG" and current_aggressor_vsi > 0:
            # VSI > 0.3 = strong; scale from 0 at VSI=0 to 0.25 at VSI=0.8+
            conf_vsi = min(0.25, 0.25 * min(1.0, current_aggressor_vsi / 0.8))
        elif direction == "SHORT" and current_aggressor_vsi < 0:
            # VSI < -0.3 = strong; scale from 0 at VSI=0 to 0.25 at VSI=-0.8+
            conf_vsi = min(0.25, 0.25 * min(1.0, abs(current_aggressor_vsi) / 0.8))

        # 2. VSI velocity (0.0–0.20)
        # How fast the imbalance is changing
        conf_roc = 0.0
        if direction == "LONG" and current_aggressor_vsi_roc > 0:
            conf_roc = min(0.20, 0.20 * min(1.0, current_aggressor_vsi_roc / 0.5))
        elif direction == "SHORT" and current_aggressor_vsi_roc < 0:
            conf_roc = min(0.20, 0.20 * min(1.0, abs(current_aggressor_vsi_roc) / 0.5))

        # 3. IEX intent suppression (0.0–0.15)
        # Low IEX intent = high conviction (genuine flow on aggressive venues)
        conf_iex = 0.05  # baseline (gate B already passed)
        if current_iex_intent <= iex_intent_threshold * 0.5:
            conf_iex = 0.15
        elif current_iex_intent < iex_intent_threshold:
            conf_iex = 0.05 + 0.10 * (
                1.0 - current_iex_intent / iex_intent_threshold
            )

        # 4. Venue concentration (0.0–0.10)
        # Higher concentration = more conviction that aggressors are driving
        conf_conc = 0.05  # baseline (gate C already passed)
        if current_venue_conc > venue_conc_threshold:
            conf_conc = 0.05 + 0.05 * min(
                1.0, (current_venue_conc - venue_conc_threshold) / venue_conc_threshold
            )

        # 5. Volume confirmation (0.0–0.10)
        # Volume above average
        conf_volume = 0.05  # baseline
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0:
            current_vol = volume_window.latest
            avg_vol = volume_window.mean
            if current_vol is not None and avg_vol is not None and avg_vol > 0:
                vol_ratio = current_vol / avg_vol
                conf_volume = 0.05 + 0.05 * min(1.0, max(0, (vol_ratio - 0.8) / 0.8))

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
            conf_vsi + conf_roc + conf_iex + conf_conc +
            conf_volume + conf_vamp + conf_gex
        )
        return min(1.0, max(0.0, confidence))
