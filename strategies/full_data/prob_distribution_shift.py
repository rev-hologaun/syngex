"""
strategies/full_data/prob_distribution_shift.py — Prob Distribution Shift

Full-data (v2) strategy: leading indicator that detects when the full
probability distribution shifts before price moves.

Logic:
    - Calculate Probability Momentum = Σ(ΔProbITM_i × ΔStrike_i) across all strikes
    - Use delta as proxy for ProbabilityITM (delta ≈ ProbITM)
    - For each strike: contribution = net_delta × |strike - ATM_strike|
    - Sum all contributions → total probability momentum
    - Entry when momentum > 2σ of rolling average for 3+ consecutive evaluations
    - Positive momentum = mass shifting right (bullish)
    - Negative momentum = mass shifting left (bearish)

Entry (LONG):
    - ProbMomentum > +2σ of rolling avg for 3+ consecutive evaluations
    - Volume not declining (FLAT or UP)
    - Net gamma positive

Entry (SHORT):
    - ProbMomentum < -2σ of rolling avg for 3+ consecutive evaluations
    - Volume not rising (FLAT or DOWN)
    - Net gamma positive

Confidence factors:
    - Z-score (how many σ away from mean)
    - Duration of shift (more consecutive = higher confidence)
    - Volume confirmation
    - Net gamma strength
    - Breadth of shift (more strikes contributing)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_window import RollingWindow
from strategies.rolling_keys import KEY_PROB_MOMENTUM_5M, KEY_CONSEC_LONG, KEY_CONSEC_SHORT, KEY_VOLUME_5M

logger = logging.getLogger("Syngex.Strategies.ProbDistributionShift")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Z-score threshold for significant shift
Z_SCORE_THRESHOLD = 2.0             # 2 standard deviations

# Minimum consecutive same-direction signals
MIN_CONSECUTIVE_SIGNALS = 3         # 3 consecutive evaluations

# Min net gamma for positive regime
MIN_NET_GAMMA = 5000.0

# Stop and target
STOP_PCT = 0.005                    # 0.5% stop
TARGET_PCT = 0.008                  # 0.8% target (1.6:1 R:R)

# Min confidence
MIN_CONFIDENCE = 0.35
MAX_CONFIDENCE = 0.80               # v2 cap

# Min strikes with data
MIN_STRIKES_WITH_DATA = 5           # Need at least 5 strikes for distribution

# Min data points for rolling stats
MIN_DATA_POINTS = 10                # Need more data for z-score calculation

# Rolling window size for momentum tracking (count-based, ~30s at 1Hz)
MOMENTUM_WINDOW_SIZE = 30

# Volume filter
VOLUME_TREND_ALLOWED_LONG = ["FLAT", "UP"]
VOLUME_TREND_ALLOWED_SHORT = ["FLAT", "DOWN"]

# Contribution threshold: strikes contributing > this % of total momentum count
CONTRIBUTION_THRESHOLD = 0.05       # 5% of total momentum


class ProbDistributionShift(BaseStrategy):
    """
    Prob Distribution Shift — Full-data (v2) leading indicator.

    Detects when the full probability distribution across all strikes shifts
    asymmetrically before the underlying price reacts. Uses delta as a proxy
    for ProbabilityITM and calculates a weighted momentum across the entire
    options chain.

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

        # --- Ensure rolling window exists ---
        if KEY_PROB_MOMENTUM_5M not in rolling_data:
            rolling_data[KEY_PROB_MOMENTUM_5M] = RollingWindow(
                window_type="count",
                window_size=MOMENTUM_WINDOW_SIZE,
            )

        momentum_window: RollingWindow = rolling_data[KEY_PROB_MOMENTUM_5M]
        momentum_window.push(momentum, data.get("timestamp"))

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

        # --- Compute confidence ---
        confidence = self._compute_confidence(
            z_score,
            abs(z_score),
            consec_long if signal_direction == Direction.LONG else consec_short,
            vol_trend,
            net_gamma,
            momentum,
            greeks_summary,
        )

        if confidence < MIN_CONFIDENCE:
            return []

        # --- Build signal ---
        stop, target = self._build_exit(signal_direction, underlying_price)

        direction_label = "bullish" if signal_direction == Direction.LONG else "bearish"
        sign = "+" if signal_direction == Direction.LONG else ""

        return [Signal(
            direction=signal_direction,
            confidence=round(confidence, 3),
            entry=underlying_price,
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
                "net_gamma": round(net_gamma, 2),
                "regime": data.get("regime", "UNKNOWN"),
                "momentum_window_count": momentum_window.count,
                "momentum_window_mean": round(momentum_window.mean, 4)
                    if momentum_window.mean is not None else None,
                "momentum_window_std": round(momentum_window.std, 4)
                    if momentum_window.std is not None else None,
                "stop_pct": STOP_PCT,
                "target_pct": TARGET_PCT,
                "risk_reward_ratio": round(
                    abs(target - underlying_price) / abs(stop - underlying_price), 2
                ),
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

                call_delta = strike_data.get("call_delta", 0.0)
                put_delta = strike_data.get("put_delta", 0.0)
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

    def _build_exit(
        self,
        direction: Direction,
        price: float,
    ) -> tuple[float, float]:
        """
        Build stop and target levels.

        Stop: 0.5% against entry.
        Target: 0.8% in direction of trade (1.6:1 R:R).
        """
        if direction == Direction.LONG:
            stop = price * (1 - STOP_PCT)
            target = price * (1 + TARGET_PCT)
        else:
            stop = price * (1 + STOP_PCT)
            target = price * (1 - TARGET_PCT)

        return stop, target

    # ------------------------------------------------------------------
    # Confidence scoring
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        z_score: float,
        abs_z: float,
        consecutive_count: int,
        vol_trend: str,
        net_gamma: float,
        momentum: float,
        greeks_summary: Dict[str, Any],
    ) -> float:
        """
        Compute confidence for a distribution-shift signal.

        Factors (each 0–1, capped at MAX_CONFIDENCE):
        1. Z-score magnitude (0.20–0.30) — how many σ from mean
        2. Duration of shift (0.15–0.20) — consecutive same-direction signals
        3. Volume confirmation (0.10–0.15) — aligned with direction
        4. Net gamma strength (0.10–0.15) — positive regime quality
        5. Breadth of shift (0.10–0.15) — more strikes contributing
        """
        # 1. Z-score component (0.20–0.30)
        #    2σ = baseline, 4σ+ = max weight
        z_scaled = min(1.0, (abs_z - Z_SCORE_THRESHOLD) / Z_SCORE_THRESHOLD)
        z_component = 0.20 + 0.10 * z_scaled

        # 2. Duration component (0.15–0.20)
        #    MIN_CONSECUTIVE_SIGNALS = baseline, 6+ = max weight
        dur_scaled = min(
            1.0,
            (consecutive_count - MIN_CONSECUTIVE_SIGNALS)
            / (MIN_CONSECUTIVE_SIGNALS + 2)
        )
        dur_component = 0.15 + 0.05 * max(0, dur_scaled)

        # 3. Volume confirmation (0.10–0.15)
        #    Aligned volume trend = stronger signal
        if vol_trend == "UP":
            vol_component = 0.15  # Strong confirmation
        elif vol_trend == "FLAT":
            vol_component = 0.12  # Moderate
        else:
            vol_component = 0.08  # Weak

        # 4. Net gamma strength (0.10–0.15)
        #    Higher positive gamma = stronger positive regime
        gamma_scaled = min(1.0, net_gamma / (MIN_NET_GAMMA * 4))
        gamma_component = 0.10 + 0.05 * gamma_scaled

        # 5. Breadth of shift (0.10–0.15)
        #    Count strikes contributing > 5% of total momentum
        total_abs_momentum = abs(momentum) if momentum != 0 else 1.0
        breadth = 0
        for strike_str, strike_data in greeks_summary.items():
            try:
                strike = float(strike_str)
            except (ValueError, TypeError):
                continue
            call_delta = strike_data.get("call_delta", 0.0)
            put_delta = strike_data.get("put_delta", 0.0)
            net_delta = call_delta - put_delta
            if call_delta == 0 and put_delta == 0:
                continue
            distance = strike - self._atm_strike(greeks_summary)
            contribution = abs(net_delta * distance)
            if contribution > CONTRIBUTION_THRESHOLD * total_abs_momentum:
                breadth += 1

        # Normalize: 5 strikes = baseline, 15+ = max weight
        breadth_scaled = min(1.0, (breadth - MIN_STRIKES_WITH_DATA) / 10)
        breadth_component = 0.10 + 0.05 * max(0, breadth_scaled)

        # Normalize each component to [0,1] and average
        norm_z = (z_component - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_dur = (dur_component - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_vol = (vol_component - 0.08) / (0.15 - 0.08) if 0.15 != 0.08 else 1.0
        norm_gamma = (gamma_component - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        norm_breadth = (breadth_component - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        confidence = (norm_z + norm_dur + norm_vol + norm_gamma + norm_breadth) / 5.0

        return min(MAX_CONFIDENCE, max(0.0, confidence))

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
