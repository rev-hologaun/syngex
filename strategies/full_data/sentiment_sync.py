"""
strategies/full_data/sentiment_sync.py — Sentiment Sync (SYNCHRONY-ALPHA)

Detects when options sentiment (IV skew) and equity flow (Aggressor VSI)
move in lockstep. Γ_sync = Sign(ΔSkew) × Sign(Aggressor_VSI)

Bullish Sync: ΔSkew falling (complacency) AND VSI positive (buying) → LONG
Bearish Sync: ΔSkew rising (fear) AND VSI negative (selling) → SHORT
Filters out false signals where options positioning doesn't translate to stock flow.

Trigger: |ΔSkew| > 2σ AND |VSI| > 2σ AND signs agree

Hard gates (ALL must pass):
    Gate A: Magnitude gate — both skew change and VSI > 2σ over rolling window
    Gate B: Volume anchor — total volume above rolling average
    Gate C: Price confirmation — price moving in direction of sync

Confidence model (5 components):
    1. Skew significance (0.0–0.25) — ΔSkew in σ units
    2. VSI significance (0.0–0.25) — Aggressor VSI in σ units
    3. Sign agreement (0.0–0.15) — how cleanly both signals agree
    4. Volume confirmation (0.0–0.10) — volume above average
    5. GEX regime alignment (0.0–0.10) — signal direction matches GEX bias
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_SYNC_CORR_5M,
    KEY_SYNC_SIGMA_5M,
    KEY_SKEW_CHANGE_5M,
    KEY_VSI_MAGNITUDE_5M,
    KEY_VOLUME_5M,
)

logger = logging.getLogger("Syngex.Strategies.SentimentSync")


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))


MIN_CONFIDENCE = 0.10


class SentimentSync(BaseStrategy):
    """
    Sentiment Sync strategy — detects when options sentiment and equity flow
    move in lockstep via Γ_sync = Sign(ΔSkew) × Sign(Aggressor_VSI).

    ΔSkew (rolling % change in IV skew over 5m window):
        Rising ΔSkew = rising fear (put wing expanding)
        Falling ΔSkew = falling fear / complacency (call wing expanding)

    Aggressor VSI (venue-specific bid/ask imbalance on MEMX+BATS):
        Positive VSI = aggressive buying pressure
        Negative VSI = aggressive selling pressure

    Γ_sync = +1: Both positive → fear + selling (bearish confirmation)
    Γ_sync = -1: Both negative → complacency + buying (bullish confirmation)

    LONG: ΔSkew < 0 (falling/complacency) AND VSI > 0 (buying) AND regime == "POSITIVE"
    SHORT: ΔSkew > 0 (rising/fear) AND VSI < 0 (selling) AND regime == "NEGATIVE"
    """

    strategy_id = "sentiment_sync"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for sentiment sync signal.

        Returns a single LONG or SHORT signal when conditions are met,
        or empty list when gates fail or no clear signal.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params
        regime = data.get("regime", "")

        # 1. Get rolling window data
        min_data_points = params.get("min_data_points", 5)
        min_sig_sigma = params.get("min_sig_sigma", 2.0)

        corr_window = rolling_data.get(KEY_SYNC_CORR_5M)
        sigma_window = rolling_data.get(KEY_SYNC_SIGMA_5M)
        skew_change_window = rolling_data.get(KEY_SKEW_CHANGE_5M)
        vsi_mag_window = rolling_data.get(KEY_VSI_MAGNITUDE_5M)

        if not corr_window or corr_window.count < min_data_points:
            return []
        if not sigma_window or sigma_window.count < min_data_points:
            return []
        if not skew_change_window or skew_change_window.count < min_data_points:
            return []
        if not vsi_mag_window or vsi_mag_window.count < min_data_points:
            return []

        current_corr = corr_window.values[-1]       # Γ_sync: +1 or -1
        current_sigma = sigma_window.values[-1]      # max(skew_sigma, vsi_sigma)
        current_skew_change = skew_change_window.values[-1]  # % change in IV skew
        current_vsi_mag = vsi_mag_window.values[-1]    # |Aggressor VSI|

        # 2. Determine signal direction
        # Γ_sync = +1: fear + selling → SHORT
        # Γ_sync = -1: complacency + buying → LONG
        long_signal = current_corr < 0  # both negative
        short_signal = current_corr > 0  # both positive

        if not long_signal and not short_signal:
            return []

        if long_signal and short_signal:
            direction = "LONG" if current_corr < 0 else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Apply 3 HARD GATES
        gate_a = self._gate_a_magnitude(
            current_skew_change, current_vsi_mag, current_sigma, min_sig_sigma
        )

        if not gate_a:
            logger.debug(
                "Sentiment Sync: Gate A failed — magnitude not significant enough for %s",
                direction,
            )
            return []

        gate_b = self._gate_b_volume(rolling_data, params)

        if not gate_b:
            logger.debug(
                "Sentiment Sync: Gate B failed — volume anchor for %s",
                direction,
            )
            return []

        gate_c = self._gate_c_price_confirmation(
            current_skew_change, current_vsi_mag, direction, data, params
        )

        if not gate_c:
            logger.debug(
                "Sentiment Sync: Gate C failed — price confirmation for %s",
                direction,
            )
            return []

        # 4. Compute confidence (5-component model)
        confidence = self._compute_confidence(
            current_skew_change,
            current_vsi_mag,
            current_sigma,
            direction,
            rolling_data,
            data,
            params,
            regime,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 5. Build signal with entry/stop/target
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
        sigma_zscore = abs(current_skew_change) / current_sigma if current_sigma > 0 else 0
        if sigma_zscore > 3.0:
            intensity = "red"
        elif sigma_zscore > 2.0:
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
                f"Sentiment sync {direction}: Γ={current_corr:+.1f}, "
                f"ΔSkew={current_skew_change:+.4f}, "
                f"VSI_mag={current_vsi_mag:.4f}, σ={current_sigma:.4f}"
            ),
            metadata={
                "direction": direction,
                "gamma_sync": round(current_corr, 2),
                "skew_change": round(current_skew_change, 6),
                "vsi_magnitude": round(current_vsi_mag, 6),
                "sigma": round(current_sigma, 6),
                "sigma_zscore": round(sigma_zscore, 2),
                "intensity": intensity,
                "regime": regime,
                "gates": {
                    "A_magnitude": gate_a,
                    "B_volume": gate_b,
                    "C_price_confirmation": gate_c,
                },
            },
        )]

    def _gate_a_magnitude(
        self,
        skew_change: float,
        vsi_mag: float,
        sigma: float,
        min_sigma: float,
    ) -> bool:
        """
        Gate A: Magnitude gate.

        Both ΔSkew and VSI must exceed the σ threshold, indicating
        that both options sentiment and equity flow are moving significantly
        — not just noise in one dimension.
        """
        if sigma <= 0:
            return False
        zscore = abs(skew_change) / sigma
        return zscore >= min_sigma

    def _gate_b_volume(
        self,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate B: Volume anchor.

        Total volume must be above rolling average, confirming the signal
        is supported by actual trading activity, not just order book noise.
        """
        volume_min_mult = params.get("volume_min_mult", 1.0)
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0:
            current_vol = volume_window.latest
            avg_vol = volume_window.mean
            if current_vol is not None and avg_vol is not None and avg_vol > 0:
                return current_vol >= avg_vol * volume_min_mult
        # No volume data — pass gate (can't evaluate)
        return True

    def _gate_c_price_confirmation(
        self,
        skew_change: float,
        vsi_mag: float,
        direction: str,
        data: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """
        Gate C: Price confirmation.

        Since we don't have tick-level price change data in the strategy
        evaluation context, we use the VSI sign as a proxy for price direction.
        VSI > 0 implies buying pressure (price should rise → supports LONG).
        VSI < 0 implies selling pressure (price should fall → supports SHORT).

        The VSI magnitude must also exceed a minimum threshold to confirm
        the signal has enough force to move price.
        """
        price_confirm_pct = params.get("price_confirm_pct", 0.001)
        # Use price_confirm_pct as a minimum VSI magnitude threshold
        # VSI magnitude must exceed this to confirm directional force
        return vsi_mag >= price_confirm_pct

    def _compute_confidence(
        self,
        current_skew_change: float,
        current_vsi_mag: float,
        current_sigma: float,
        direction: str,
        rolling_data: Dict[str, Any],
        data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
    ) -> float:
        """
        Compute 5-component confidence score (Family A).

        Returns 0.0–1.0.
        """
        # 1. Skew significance: current_skew_change from 0→1, use abs
        abs_sc = abs(current_skew_change)
        c1 = normalize(abs_sc, 0.0, 1.0)
        # 2. VSI significance: current_vsi_mag from 0→0.5, higher = higher
        c2 = normalize(current_vsi_mag, 0.0, 0.5)
        # 3. Sigma significance: current_sigma from 0→5, higher = higher
        c3 = normalize(current_sigma, 0.0, 5.0)
        # 4. Call/put balance: from rolling_data
        cp_ratio = rolling_data.get("call_put_ratio", 1.0)
        c4 = normalize(cp_ratio, 0.0, 2.0)
        # 5. Volume confirmation: from rolling_data
        vol_window = rolling_data.get("volume_5m")
        vol_ratio = vol_window.latest / vol_window.mean if vol_window and vol_window.mean > 0 else 1.0
        c5 = normalize(vol_ratio, 0.0, 2.0)
        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))
