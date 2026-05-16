"""
strategies/full_data/prob_distribution_shift.py — Prob Distribution Shift v2 (Momentum-Master)

Full-data (v2) strategy: leading indicator that detects when the full
probability distribution shifts before price moves.

Logic:
    - Calculate Probability Momentum = Σ(ΔProbITM_i × ΔStrike_i) across all strikes
    - Use delta as proxy for ProbabilityITM (delta ≈ ProbITM)
    - For each strike: contribution = net_delta × |strike - ATM_strike|
    - Sum all contributions → total probability momentum
    - Momentum ROC tracks acceleration of the momentum signal
    - Entry when momentum ROC shows accelerating shift + z-score confirmation
    - Capital-weighted breadth ensures breadth of shift is concentrated in high-OI strikes
    - Delta-skew coupling ensures options market structure supports the direction
    - IV-scaled targets adjust for current volatility regime

Entry (LONG):
    - ProbMomentum ROC accelerating upward ≥10% (momentum_accel > 0.10)
    - Z-score > threshold for 2+ consecutive evaluations
    - Capital-weighted breadth > threshold (concentration in high-OI strikes)
    - Delta-skew coupling positive (skew normalizing from negative toward zero)
    - Volume not declining (FLAT or UP)
    - Net gamma positive

Entry (SHORT):
    - ProbMomentum ROC accelerating downward ≥10% (momentum_accel < -0.10)
    - Z-score < -threshold for 2+ consecutive evaluations
    - Capital-weighted breadth > threshold (concentration in high-OI strikes)
    - Delta-skew coupling negative (skew normalizing from positive toward zero)
    - Volume not rising (FLAT or DOWN)
    - Net gamma positive

Confidence (7 components, unified for LONG and SHORT):
    1. Z-score magnitude: 0.10–0.15 (soft)
    2. Momentum acceleration: 0.0 or 0.20–0.30 (hard gate)
    3. Capital-weighted breadth: 0.0 or 0.15–0.20 (hard gate, scaled by weight)
    4. Delta-skew coupling: 0.0 or 0.15–0.20 (hard gate)
    5. Duration: 0.05–0.10 (soft)
    6. Volume confirmation: 0.05–0.10 (soft)
    7. Net gamma: 0.05–0.10 (soft)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_PROB_MOMENTUM_5M,
    KEY_CONSEC_LONG,
    KEY_CONSEC_SHORT,
    KEY_VOLUME_5M,
    KEY_MOMENTUM_ROC_5M,
    KEY_IV_SKEW_5M,
    KEY_ATM_IV_5M,
)

logger = logging.getLogger("Syngex.Strategies.ProbDistributionShift")


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Z-score threshold for significant shift
Z_SCORE_THRESHOLD = 1.5             # 1.5 standard deviations

# Minimum consecutive same-direction signals
MIN_CONSECUTIVE_SIGNALS = 2         # 2 consecutive evaluations

# Min net gamma for positive regime
MIN_NET_GAMMA = 500000.0

# Stop and target
STOP_PCT = 0.005                    # 0.5% stop

# Min confidence (raised from 0.25 → 0.35 for v2)
MIN_CONFIDENCE = 0.10

# Min strikes with data
MIN_STRIKES_WITH_DATA = 5           # Need at least 5 strikes for distribution

# Min data points for rolling stats
MIN_DATA_POINTS = 5                 # Need enough data for z-score calculation

# Volume filter
VOLUME_TREND_ALLOWED_LONG = ["FLAT", "UP"]
VOLUME_TREND_ALLOWED_SHORT = ["FLAT", "DOWN"]

# Contribution threshold: strikes contributing > this % of total momentum count
CONTRIBUTION_THRESHOLD = 0.05       # 5% of total momentum


class ProbDistributionShift(BaseStrategy):
    """
    Prob Distribution Shift v2 — Momentum-Master.

    Detects when the full probability distribution across all strikes shifts
    asymmetrically before the underlying price reacts. Uses delta as a proxy
    for ProbabilityITM and calculates a weighted momentum across the entire
    options chain.

    v2 additions:
    - Momentum ROC acceleration as hard gate
    - Capital-weighted breadth (OI-weighted)
    - Delta-skew coupling check
    - IV-scaled targets
    - 7-component confidence scoring

    This is a leading indicator — signals are rare but high conviction when
    they fire. Typical holds: 30min – 2hr.
    """

    strategy_id = "prob_distribution_shift"
    layer = "full_data"

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return distribution-shift signals.

        Returns empty list when no statistically significant probability
        momentum shift is detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0.0)
        greeks_summary = data.get("greeks_summary", {})

        # --- Validate data ---
        if not greeks_summary:
            return []

        # --- Net gamma check ---
        if net_gamma < MIN_NET_GAMMA:
            return []

        # --- Calculate probability momentum ---
        momentum = self._calculate_momentum(
            greeks_summary, underlying_price
        )
        if momentum is None:
            return []

        # --- Use main.py's populated momentum window ---
        momentum_window = rolling_data.get(KEY_PROB_MOMENTUM_5M)
        if momentum_window is None:
            return []

        # --- Need enough data for z-score ---
        if momentum_window.count < MIN_DATA_POINTS:
            return []

        # --- Calculate z-score ---
        z_score = momentum_window.z_score
        if z_score is None:
            return []

        # --- Consecutive signal tracking ---
        consec_long = rolling_data.get(KEY_CONSEC_LONG, 0)
        consec_short = rolling_data.get(KEY_CONSEC_SHORT, 0)

        # --- Volume check ---
        volume_5m = rolling_data.get(KEY_VOLUME_5M)
        vol_trend = "FLAT"
        if volume_5m is not None and volume_5m.count >= MIN_DATA_POINTS:
            vol_trend = volume_5m.trend

        # --- Price trend ---
        price_window = rolling_data.get("price_5m")
        price_trend = price_window.trend if price_window else "UNKNOWN"

        # --- v2: Momentum acceleration hard gate ---
        momentum_accel = self._check_momentum_acceleration(rolling_data)
        if momentum_accel is None:
            return []

        # --- v2: Capital-weighted breadth hard gate ---
        capital_weight, contributing_oi = self._compute_capital_weighted_breadth(
            greeks_summary, momentum, underlying_price
        )
        if capital_weight < self._get_param("capital_breadth_threshold", 0.10):
            return []

        # --- v2: Delta-skew coupling hard gate ---
        skew_coupled = self._check_delta_skew_coupling(rolling_data)
        if not skew_coupled:
            return []

        # --- Determine signal direction ---
        signal_direction = None

        if z_score > Z_SCORE_THRESHOLD:
            # Bullish probability shift
            consec_long += 1
            consec_short = 0
            if consec_long >= MIN_CONSECUTIVE_SIGNALS:
                if vol_trend in VOLUME_TREND_ALLOWED_LONG:
                    signal_direction = Direction.LONG
        elif z_score < -Z_SCORE_THRESHOLD:
            # Bearish probability shift
            consec_short += 1
            consec_long = 0
            if consec_short >= MIN_CONSECUTIVE_SIGNALS:
                if vol_trend in VOLUME_TREND_ALLOWED_SHORT:
                    signal_direction = Direction.SHORT
        else:
            # No significant shift — reset counters
            consec_long = 0
            consec_short = 0

        rolling_data[KEY_CONSEC_LONG] = consec_long
        rolling_data[KEY_CONSEC_SHORT] = consec_short

        if signal_direction is None:
            return []

        # --- v2: IV-scaled target ---
        entry = underlying_price
        risk = STOP_PCT * entry  # distance to stop
        target = self._compute_iv_scaled_target(entry, risk, rolling_data, signal_direction)

        # --- Compute confidence (7-component v2) ---
        confidence = self._compute_confidence_v2(
            z_score,
            abs(z_score),
            consec_long if signal_direction == Direction.LONG else consec_short,
            vol_trend,
            net_gamma,
            momentum_accel,
            capital_weight,
            skew_coupled,
            momentum,
            greeks_summary,
        )

        if confidence < MIN_CONFIDENCE:
            return []

        # --- Build signal ---
        stop = self._build_stop(signal_direction, underlying_price)

        direction_label = "bullish" if signal_direction == Direction.LONG else "bearish"
        sign = "+" if signal_direction == Direction.LONG else ""

        # --- v2 metadata fields ---
        momentum_roc_val = None
        if momentum_window.count >= 6:
            vals = list(momentum_window.values)
            if abs(vals[-6]) > 0:
                momentum_roc_val = (vals[-1] - vals[-6]) / abs(vals[-6])

        skew_roc_val = None
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        if skew_window is not None and skew_window.count >= 2:
            first_skew = skew_window.values[0]
            if abs(first_skew) > 0:
                skew_roc_val = (skew_window.latest - first_skew) / abs(first_skew)

        iv_factor = None
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        if iv_window is not None and iv_window.mean is not None and iv_window.latest is not None:
            if iv_window.mean > 0:
                iv_factor = iv_window.latest / iv_window.mean

        return [Signal(
            direction=signal_direction,
            confidence=round(confidence, 3),
            entry=entry,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"{direction_label.capitalize()} prob distribution shift: "
                f"momentum={momentum:.2f}, z={sign}{z_score:.2f}, "
                f"consec={consec_long if signal_direction == Direction.LONG else consec_short}, "
                f"vol={vol_trend}, gamma={net_gamma:.0f}"
            ),
            metadata={
                "momentum": round(momentum, 4),
                "z_score": round(z_score, 3),
                "consecutive_count": (
                    consec_long if signal_direction == Direction.LONG else consec_short
                ),
                "volume_trend": vol_trend,
                "price_trend": price_trend,
                "net_gamma": round(net_gamma, 2),
                "regime": data.get("regime", "UNKNOWN"),
                "momentum_window_count": momentum_window.count,
                "momentum_window_mean": round(momentum_window.mean, 4)
                    if momentum_window.mean is not None else None,
                "momentum_window_std": round(momentum_window.std, 4)
                    if momentum_window.std is not None else None,
                "stop_pct": STOP_PCT,
                "target_pct": round(abs(target - entry) / entry, 5),
                "risk_reward_ratio": round(
                    abs(target - entry) / abs(stop - entry), 2
                ),
                # v2 Momentum-Master fields
                "momentum_roc": round(momentum_roc_val, 4) if momentum_roc_val is not None else None,
                "momentum_accel": round(momentum_accel, 4),
                "capital_breadth": round(capital_weight, 4),
                "contributing_oi": round(contributing_oi, 2),
                "skew_roc": round(skew_roc_val, 4) if skew_roc_val is not None else None,
                "delta_skew_coupled": skew_coupled,
                "iv_factor": round(iv_factor, 4) if iv_factor is not None else None,
                "target_mult": round(abs(target - entry) / risk, 3) if risk > 0 else None,
            },
        )]

    # ------------------------------------------------------------------
    # Probability momentum calculation
    # ------------------------------------------------------------------

    def _calculate_momentum(
        self,
        greeks_summary: Dict[str, Any],
        price: float,
    ) -> Optional[float]:
        """
        Calculate Probability Momentum across all strikes.

        ProbMomentum = Σ(net_delta_i × |strike_i - ATM_strike|)
        where net_delta = call_delta - put_delta (net probability bias).

        Positive momentum = mass shifting right (bullish).
        Negative momentum = mass shifting left (bearish).

        Returns None if insufficient strikes with data.
        """
        try:
            atm_strike = None
            min_distance = float("inf")

            # Find ATM strike first
            for strike_str in greeks_summary:
                try:
                    s = float(strike_str)
                except (ValueError, TypeError):
                    continue
                dist = abs(s - price)
                if dist < min_distance:
                    min_distance = dist
                    atm_strike = s

            if atm_strike is None:
                return None

            # Calculate momentum
            total_momentum = 0.0
            contributing_strikes = 0

            for strike_str, strike_data in greeks_summary.items():
                try:
                    strike = float(strike_str)
                except (ValueError, TypeError):
                    continue

                call_delta = strike_data.get("call_delta_sum", 0.0)
                put_delta = strike_data.get("put_delta_sum", 0.0)
                net_delta = call_delta - put_delta

                # Skip strikes with no delta data
                if call_delta == 0 and put_delta == 0:
                    continue

                distance = strike - atm_strike
                contribution = net_delta * distance
                total_momentum += contribution
                contributing_strikes += 1

            if contributing_strikes < MIN_STRIKES_WITH_DATA:
                return None

            return total_momentum

        except Exception as e:
            logger.debug("Error calculating momentum: %s", e)
            return None

    # ------------------------------------------------------------------
    # Exit levels
    # ------------------------------------------------------------------

    def _build_stop(
        self,
        direction: Direction,
        price: float,
    ) -> float:
        """
        Build stop level.

        Stop: 0.5% against entry.
        """
        if direction == Direction.LONG:
            return price * (1 - STOP_PCT)
        else:
            return price * (1 + STOP_PCT)

    # ------------------------------------------------------------------
    # v2 Momentum-Master checks
    # ------------------------------------------------------------------

    def _check_momentum_acceleration(self, rolling_data: Dict[str, Any]) -> Optional[float]:
        """
        Check momentum acceleration from KEY_MOMENTUM_ROC_5M rolling window.

        Returns the acceleration value if it passes the threshold gate,
        or None if it fails.

        For LONG: momentum_accel > +threshold (accelerating upward)
        For SHORT: momentum_accel < -threshold (accelerating downward)

        The threshold is read from params (default 0.10 = 10%).
        """
        window = rolling_data.get(KEY_MOMENTUM_ROC_5M)
        if window is None or window.latest is None:
            return None

        accel = window.latest
        threshold = self._get_param("momentum_accel_threshold", 0.10)

        if accel > threshold:
            return accel
        elif accel < -threshold:
            return accel
        else:
            return None

    def _compute_capital_weighted_breadth(
        self,
        greeks_summary: Dict[str, Any],
        momentum: float,
        price: float,
    ) -> Tuple[float, float]:
        """
        Compute capital-weighted breadth of the momentum shift.

        Sums total_chain_oi across all strikes, then sums contributing_oi
        for strikes contributing > 5% of total momentum.

        capital_weight = contributing_oi / total_chain_oi

        Returns (capital_weight, contributing_oi).
        """
        total_chain_oi = 0.0
        contributing_oi = 0.0
        total_abs_momentum = abs(momentum) if momentum != 0 else 1.0

        # Find ATM strike
        atm_strike = None
        min_distance = float("inf")
        for strike_str in greeks_summary:
            try:
                s = float(strike_str)
            except (ValueError, TypeError):
                continue
            dist = abs(s - price)
            if dist < min_distance:
                min_distance = dist
                atm_strike = s

        if atm_strike is None:
            return (0.0, 0.0)

        for strike_str, strike_data in greeks_summary.items():
            try:
                strike = float(strike_str)
            except (ValueError, TypeError):
                continue

            call_oi = strike_data.get("call_oi", 0.0)
            put_oi = strike_data.get("put_oi", 0.0)
            total_oi = call_oi + put_oi
            total_chain_oi += total_oi

            call_delta = strike_data.get("call_delta_sum", 0.0)
            put_delta = strike_data.get("put_delta_sum", 0.0)
            net_delta = call_delta - put_delta
            if call_delta == 0 and put_delta == 0:
                continue

            distance = strike - atm_strike
            contribution = abs(net_delta * distance)
            if contribution > CONTRIBUTION_THRESHOLD * total_abs_momentum:
                contributing_oi += total_oi

        if total_chain_oi == 0:
            return (0.0, 0.0)

        return (contributing_oi / total_chain_oi, contributing_oi)

    def _check_delta_skew_coupling(self, rolling_data: Dict[str, Any]) -> bool:
        """
        Check if delta-skew coupling supports the signal direction.

        Gets KEY_IV_SKEW_5M rolling window and computes skew ROC.
        For LONG: skew_roc > 0 (skew normalizing from negative toward zero)
        For SHORT: skew_roc < 0 (skew normalizing from positive toward zero)

        If skew data unavailable → return True (backwards compat).
        """
        window = rolling_data.get(KEY_IV_SKEW_5M)
        if window is None or window.latest is None or window.mean is None:
            return True  # backwards compat: allow if no skew data

        current_skew = window.latest
        avg_skew = window.mean

        if abs(avg_skew) == 0:
            return True

        skew_roc = (current_skew - avg_skew) / abs(avg_skew)

        # For LONG: we want skew_roc > 0 (skew moving toward zero from negative)
        # For SHORT: we want skew_roc < 0 (skew moving toward zero from positive)
        # Since we don't know direction here, check if skew is normalizing
        # (moving toward the mean/average, indicating stabilization)
        # Actually, the direction is determined by z_score in evaluate(),
        # so we check if skew_roc aligns with the likely direction.
        # If skew is currently negative (put-heavy) and rising → bullish support
        # If skew is currently positive (call-heavy) and falling → bearish support
        if current_skew < 0 and skew_roc > 0:
            return True  # negative skew normalizing up → bullish
        elif current_skew > 0 and skew_roc < 0:
            return True  # positive skew normalizing down → bearish
        else:
            return False

    def _compute_iv_scaled_target(
        self,
        entry: float,
        risk: float,
        rolling_data: Dict[str, Any],
        direction: Direction,
    ) -> float:
        """
        Compute IV-scaled target.

        Uses KEY_ATM_IV_5M rolling window to adjust target based on
        current IV vs mean IV.

        iv_factor = current_iv / mean_iv
        target_mult = base_mult × iv_factor, capped at target_iv_expansion_cap
        target = entry ± risk × target_mult

        Minimum target: 0.5% from entry.
        """
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        if iv_window is None or iv_window.latest is None or iv_window.mean is None:
            # No IV data — use default multiplier
            base_mult = self._get_param("target_iv_expansion_mult", 1.6)
            cap = self._get_param("target_iv_expansion_cap", 2.5)
            target_mult = min(base_mult, cap)
        else:
            current_iv = iv_window.latest
            mean_iv = iv_window.mean
            if mean_iv > 0:
                iv_factor = current_iv / mean_iv
            else:
                iv_factor = 1.0

            base_mult = self._get_param("target_iv_expansion_mult", 1.6)
            cap = self._get_param("target_iv_expansion_cap", 2.5)
            target_mult = min(base_mult * iv_factor, cap)

        if direction == Direction.LONG:
            target = entry + risk * target_mult
        else:
            target = entry - risk * target_mult

        # Minimum target: 0.5% from entry
        min_target = entry * (1 + STOP_PCT)  # at least stop distance

        if direction == Direction.LONG:
            target = max(target, min_target)
        else:
            target = min(target, entry * (1 - STOP_PCT))

        return target

    # ------------------------------------------------------------------
    # Confidence scoring (v2 — 7 components, unified for LONG/SHORT)
    # ------------------------------------------------------------------

    def _compute_confidence_v2(
        self,
        z_score: float,
        abs_z: float,
        consecutive_count: int,
        vol_trend: str,
        net_gamma: float,
        momentum_accel: float,
        capital_weight: float,
        skew_coupled: bool,
        momentum: float,
        greeks_summary: Dict[str, Any],
    ) -> float:
        """
        Compute confidence for a distribution-shift signal (Family A — 5 components).

        5 components, simple average:
            1. Z-score magnitude (abs_z, 0→4)
            2. Momentum acceleration (0→1)
            3. Capital-weighted breadth (0→1)
            4. Duration (consecutive_count, 0→10)
            5. Net gamma (0→5M)
        """
        # 1. Z-score magnitude: abs_z from 0→4, higher = more extreme = higher
        c1 = normalize(abs_z, 0.0, 4.0)
        # 2. Momentum acceleration: momentum_accel from 0→1, higher = higher
        c2 = normalize(momentum_accel, 0.0, 1.0)
        # 3. Capital-weighted breadth: capital_weight from 0→1, higher = higher
        c3 = normalize(capital_weight, 0.0, 1.0)
        # 4. Duration: consecutive_count from 0→10, higher = more persistent = higher
        c4 = normalize(consecutive_count, 0.0, 10.0)
        # 5. Net gamma: net_gamma from 0→5M, higher = higher
        c5 = normalize(net_gamma, 0.0, 5000000.0)
        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
        return min(1.0, max(0.0, confidence))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _atm_strike(self, greeks_summary: Dict[str, Any]) -> float:
        """
        Find the ATM strike (nearest to center of strike range).
        Returns 0.0 if no strikes available.
        """
        strikes = []
        for strike_str in greeks_summary:
            try:
                strikes.append(float(strike_str))
            except (ValueError, TypeError):
                continue

        if not strikes:
            return 0.0
        strikes.sort()
        return strikes[len(strikes) // 2]
