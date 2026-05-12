"""
strategies/layer2/delta_volume_exhaustion.py — Delta-Volume Exhaustion v2

Trend reversal strategy via weakening conviction. Detects when a strong
trending move is losing steam: delta declining while liquidity evaporates.
Classic exhaustion signal — the trend is running out of fuel.

Logic:
    1. Detect strong trend (UP or DOWN) in 5m window
    2. Confirm delta is declining from rolling average
    3. Confirm liquidity vacuum (depth bid/ask ratio stabilized + spread widening)
    4. Enter in OPPOSITE direction of the exhausted trend

Exit:
    - Stop: beyond the recent swing high/low
    - Target: regime-adaptive mean reversion to rolling average

Confidence factors (v2 — 6 components):
    - Trend strength (0.0–0.20) — soft
    - Delta decline (hard gate)
    - Liquidity vacuum (hard gate) — replaces volume decline
    - IV acceleration (-0.05 to +0.15) — soft
    - Regime alignment (0.0–0.10) — soft
    - Wall proximity bonus (0.0–0.10) — bonus

Min confidence: 0.35 (raised from 0.25)
"""

from __future__ import annotations

import logging
import statistics
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_DEPTH_ASK_SIZE_5M,
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_IV_SKEW_5M,
    KEY_PRICE_5M,
    KEY_TOTAL_DELTA_5M,
)

logger = logging.getLogger("Syngex.Strategies.DeltaVolumeExhaustion")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Min data points for trend detection
MIN_TREND_POINTS = 5

# Min data points for delta/volume rolling windows
MIN_GREEKS_POINTS = 5

# Delta must be below rolling avg by this ratio
DELTA_DECLINE_RATIO = 0.95            # Delta below 95% of rolling avg (was 90%)

# Trend must be sustained for this many points
MIN_TREND_DURATION = 2                # At least 2 candles in trend (was 3)

# Stop distance
STOP_PCT = 0.008                      # 0.8% beyond swing

# Minimum confidence to emit a signal
MIN_CONFIDENCE = 0.35                 # Min confidence threshold (raised from 0.25)

# Target: mean reversion to rolling average
MEAN_REVERSION_MULT = 1.0             # 1.0× distance — target is the rolling mean

# --- v2 Exhaustion-Master params ---
# Liquidity vacuum
LIQUIDITY_VACUUM_RATIO_STABILITY = 0.15   # ratio must be within 15% of rolling mean
LIQUIDITY_VACUUM_SPREAD_WIDEN_MULT = 1.2  # spread must be > 1.2× rolling mean

# IV acceleration
IV_ACCEL_WINDOW = 5                         # window for IV ROC calculation
IV_ACCEL_BONUS = 0.15                       # confidence bonus when IV aligns
IV_ACCEL_PENALTY = -0.05                    # confidence penalty when IV opposes

# Wall proximity
WALL_PROXIMITY_PCT = 0.003                # within 0.3% of wall
WALL_PROXIMITY_BONUS = 0.10               # confidence bonus

# Regime-adaptive targets
NEGATIVE_GAMMA_TARGET_MULT = 1.5          # NEG regime: let it run
POSITIVE_GAMMA_TARGET_MULT = 0.8          # POS regime: quick profits
NEUTRAL_GAMMA_TARGET_MULT = 1.0           # baseline
GAMMA_INTENSITY_THRESHOLD = 500000        # threshold for regime classification


class DeltaVolumeExhaustion(BaseStrategy):
    """
    Detects trend exhaustion via declining delta + liquidity vacuum.

    When a strong trend loses delta conviction and liquidity evaporates,
    the move is likely exhausted. Enter in the opposite direction
    for a mean-reversion fade.

    v2 upgrades:
        - Liquidity vacuum replaces volume decline (depth-based)
        - IV acceleration bonus for blow-off/capitulation detection
        - Gamma wall proximity bonus for structural confirmation
        - Regime-adaptive target scaling (NEG/POS/NEUTRAL gamma)
    """

    strategy_id = "delta_volume_exhaustion"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for exhaustion setup.

        Args:
            data: Dict containing:
                - underlying_price: Current price of the underlying
                - rolling_data: Rolling window data (price, delta, depth, IV)
                - greeks_summary: Per-strike greeks summary
                - net_gamma: Current net gamma
                - regime: Regime string ("NEGATIVE", "POSITIVE", "NEUTRAL")
                - gex_calculator: Optional GEX calculator for wall proximity
                - depth_snapshot: Optional depth snapshot with bid/ask sizes

        Returns:
            List of Signal objects (empty when no exhaustion detected).
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        rolling_data = data.get("rolling_data", {})
        greeks_summary = data.get("greeks_summary", {})
        # Compute total delta from per-strike summary
        total_delta = sum(
            v.get("net_delta", 0) for v in greeks_summary.values()
        ) if isinstance(greeks_summary, dict) else 0
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")
        gex_calc = data.get("gex_calculator")
        depth_snapshot = data.get("depth_snapshot")

        signals: List[Signal] = []

        # Check for exhausted UP trend → enter SHORT
        up_sig = self._check_exhaustion(
            rolling_data, greeks_summary, underlying_price,
            total_delta, "UP", net_gamma, regime,
            gex_calc=gex_calc, depth_snapshot=depth_snapshot,
        )
        if up_sig:
            signals.append(up_sig)

        # Check for exhausted DOWN trend → enter LONG
        down_sig = self._check_exhaustion(
            rolling_data, greeks_summary, underlying_price,
            total_delta, "DOWN", net_gamma, regime,
            gex_calc=gex_calc, depth_snapshot=depth_snapshot,
        )
        if down_sig:
            signals.append(down_sig)

        return signals

    def _check_exhaustion(
        self,
        rolling_data: Dict[str, Any],
        greeks_summary: Dict[str, Any],
        price: float,
        total_delta: float,
        trend_direction: str,
        net_gamma: float,
        regime: str,
        gex_calc: Optional[Any] = None,
        depth_snapshot: Optional[Dict[str, Any]] = None,
    ) -> Optional[Signal]:
        """
        Check for exhaustion in a specific trend direction.

        Args:
            trend_direction: "UP" or "DOWN"
            gex_calc: Optional GEX calculator for wall proximity checks
            depth_snapshot: Optional depth snapshot for liquidity vacuum
        """
        # 1. Check price trend
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window is None or price_window.count < MIN_TREND_POINTS:
            return None

        if price_window.trend != trend_direction:
            return None

        # Check trend duration: need sustained movement
        trend_strength = self._trend_strength(price_window)
        if trend_strength < 0.5:
            return None

        # 2. Check delta decline (hard gate)
        delta_decline = self._check_delta_decline(rolling_data, total_delta)
        if not delta_decline:
            return None

        # 3. Check liquidity vacuum (hard gate) — replaces volume decline
        liq_vacuum, bid_ask_ratio, current_spread, mean_spread = (
            self._check_liquidity_vacuum(rolling_data, depth_snapshot)
        )
        if not liq_vacuum:
            return None

        # 4. Compute confidence (v2 — 6 components)
        confidence = self._compute_confidence(
            trend_strength, delta_decline, liq_vacuum,
            net_gamma, regime, trend_direction,
            rolling_data=rolling_data,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # 5. Build signal
        entry = price
        reverse = -1 if trend_direction == "UP" else 1

        # Stop: beyond recent swing
        swing_pct = STOP_PCT
        stop = entry * (1 + swing_pct * reverse)
        risk = abs(entry - stop)

        # Target: regime-adaptive mean reversion
        rolling_mean = price_window.mean or entry
        regime_target_mult = self._compute_regime_target_mult(
            net_gamma, regime
        )
        target = entry + (rolling_mean - entry) * regime_target_mult
        target = max(target, stop + risk * 0.1)  # At least a little room

        direction = Direction.SHORT if trend_direction == "UP" else Direction.LONG
        reason = (
            f"{trend_direction} trend exhausted: delta declining "
            f"(below avg) + liquidity vacuum — fade the move"
        )

        # Wall proximity (bonus, not a gate)
        wall_dist_pct, nearest_wall_type, wall_proximity_bonus = (
            self._check_wall_proximity(
                price, trend_direction, gex_calc
            )
        )

        return Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=reason,
            metadata={
                # === v1 fields (kept) ===
                "exhausted_trend": trend_direction,
                "trend_strength": round(trend_strength, 3),
                "total_delta": round(total_delta, 2),
                "delta_decline": delta_decline,

                # === v2 new fields ===
                "liquidity_vacuum": liq_vacuum,
                "depth_bid_ask_ratio": round(bid_ask_ratio, 3),
                "depth_spread_current": round(current_spread, 4),
                "depth_spread_mean": round(mean_spread, 4),
                "spread_widening_mult": round(
                    current_spread / mean_spread, 2
                ) if mean_spread else 0,
                "iv_acceleration": round(
                    self._compute_iv_acceleration(rolling_data, trend_direction), 4
                ),
                "iv_accel_aligned": self._check_iv_accel_aligned(
                    rolling_data, trend_direction
                ),
                "wall_proximity_pct": round(wall_dist_pct, 4),
                "nearest_wall_type": nearest_wall_type,
                "wall_proximity_bonus": wall_proximity_bonus,
                "regime": regime,
                "regime_target_mult": regime_target_mult,
                "net_gamma": round(net_gamma, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    abs(target - entry) / risk, 2
                ) if risk > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # Hard Gate: Liquidity Vacuum Detection
    # ------------------------------------------------------------------

    def _check_liquidity_vacuum(
        self,
        rolling_data: Dict[str, Any],
        depth_snapshot: Optional[Dict[str, Any]],
    ) -> tuple[bool, float, float, float]:
        """
        Check for liquidity vacuum via depth snapshot analysis.

        Detects pre-reversal order book thinning:
        1. Bid/ask ratio has stabilized (within 15% of rolling mean)
        2. Spread has widened (> 1.2× rolling mean)

        Both conditions must be met (hard gate).

        Args:
            rolling_data: Rolling window data with depth keys
            depth_snapshot: Depth snapshot with bid_size/ask_size/spread

        Returns:
            Tuple of (liq_vacuum_detected, bid_ask_ratio, current_spread, mean_spread)
        """
        # Get current bid/ask sizes from depth_snapshot
        if depth_snapshot is None:
            return False, 0.0, 0.0, 0.0

        bid_current = depth_snapshot.get("bid_size", {}).get("current", 0)
        ask_current = depth_snapshot.get("ask_size", {}).get("current", 0)

        if ask_current <= 0:
            return False, 0.0, 0.0, 0.0

        bid_ask_ratio = bid_current / ask_current

        # Get rolling means from depth rolling windows
        bid_window = rolling_data.get(KEY_DEPTH_BID_SIZE_5M)
        ask_window = rolling_data.get(KEY_DEPTH_ASK_SIZE_5M)
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)

        bid_mean = bid_window.mean if bid_window else None
        ask_mean = ask_window.mean if ask_window else None
        mean_spread = spread_window.mean if spread_window else None
        current_spread = (
            depth_snapshot.get("spread", {}).get("current", 0)
        )

        # Condition 1: Bid/ask ratio is within 15% of rolling mean ratio
        if bid_mean and ask_mean and ask_mean > 0:
            mean_ratio = bid_mean / ask_mean
            if mean_ratio > 0:
                ratio_deviation = abs(bid_ask_ratio - mean_ratio) / mean_ratio
                ratio_stable = ratio_deviation <= LIQUIDITY_VACUUM_RATIO_STABILITY
            else:
                ratio_stable = False
        else:
            # No rolling data — can't confirm stabilization
            return False, bid_ask_ratio, current_spread, mean_spread or 0.0

        # Condition 2: Spread has widened > 1.2× rolling mean
        if mean_spread and mean_spread > 0:
            spread_widened = (
                current_spread > mean_spread * LIQUIDITY_VACUUM_SPREAD_WIDEN_MULT
            )
        else:
            spread_widened = False

        liq_vacuum = ratio_stable and spread_widened
        return liq_vacuum, bid_ask_ratio, current_spread, mean_spread or 0.0

    # ------------------------------------------------------------------
    # Soft Factor: IV Acceleration
    # ------------------------------------------------------------------

    def _compute_iv_acceleration(
        self, rolling_data: Dict[str, Any], trend_direction: str
    ) -> float:
        """
        Compute IV acceleration score for confidence adjustment.

        For exhausted UP trends: IV should be rising (fear building)
        For exhausted DOWN trends: IV should still be elevated (panic subsiding)

        Args:
            rolling_data: Rolling window data with IV skew window
            trend_direction: "UP" or "DOWN"

        Returns:
            IV acceleration score: +0.15 (aligned), -0.05 (opposing), or 0.0
        """
        window = rolling_data.get(KEY_IV_SKEW_5M)
        if window is None or window.count < IV_ACCEL_WINDOW:
            return 0.0

        values = list(window.values)
        if len(values) < IV_ACCEL_WINDOW:
            return 0.0

        # Compute ROC over last IV_ACCEL_WINDOW points
        old_val = values[0]
        new_val = values[-1]

        if old_val == 0:
            return 0.0

        iv_roc = (new_val - old_val) / abs(old_val)

        # For exhausted UP: IV should be rising (positive ROC)
        # For exhausted DOWN: IV should still be elevated (positive ROC)
        if iv_roc > 0:
            return IV_ACCEL_BONUS
        else:
            return IV_ACCEL_PENALTY

    def _check_iv_accel_aligned(
        self, rolling_data: Dict[str, Any], trend_direction: str
    ) -> bool:
        """Check if IV acceleration aligns with expected exhaustion pattern."""
        score = self._compute_iv_acceleration(rolling_data, trend_direction)
        return score > 0

    # ------------------------------------------------------------------
    # Bonus: Gamma Wall Proximity
    # ------------------------------------------------------------------

    def _check_wall_proximity(
        self,
        price: float,
        trend_direction: str,
        gex_calc: Optional[Any],
    ) -> tuple[float, Optional[str], float]:
        """
        Check proximity to gamma walls for confidence bonus.

        Direction-aware: call wall for exhausted UP, put wall for exhausted DOWN.

        Args:
            price: Current underlying price
            trend_direction: "UP" or "DOWN"
            gex_calc: GEX calculator with get_gamma_walls() method

        Returns:
            Tuple of (distance_pct, nearest_wall_type, proximity_bonus)
        """
        if gex_calc is None:
            return 0.0, None, 0.0

        try:
            walls = gex_calc.get_gamma_walls(threshold=GAMMA_INTENSITY_THRESHOLD)
        except Exception:
            return 0.0, None, 0.0

        if not walls:
            return 0.0, None, 0.0

        nearest_type = None
        nearest_dist = float("inf")

        for wall in walls:
            wall_strike = wall.get("strike", 0)
            wall_type = wall.get("type", "")  # "call" or "put"
            wall_dist_pct = abs(wall_strike - price) / price if price > 0 else float("inf")

            # Direction-aware: call wall for exhausted UP, put wall for exhausted DOWN
            if trend_direction == "UP" and wall_type == "call":
                if wall_dist_pct < nearest_dist:
                    nearest_dist = wall_dist_pct
                    nearest_type = "call"
            elif trend_direction == "DOWN" and wall_type == "put":
                if wall_dist_pct < nearest_dist:
                    nearest_dist = wall_dist_pct
                    nearest_type = "put"

        if nearest_dist <= WALL_PROXIMITY_PCT:
            return nearest_dist, nearest_type, WALL_PROXIMITY_BONUS
        else:
            return nearest_dist, nearest_type, 0.0

    # ------------------------------------------------------------------
    # Regime-Adaptive Target Scaling
    # ------------------------------------------------------------------

    def _compute_regime_target_mult(
        self, net_gamma: float, regime: str
    ) -> float:
        """
        Compute target multiplier based on regime intensity.

        Args:
            net_gamma: Current net gamma value
            regime: Regime string ("NEGATIVE", "POSITIVE", "NEUTRAL")

        Returns:
            Target multiplier (0.8–1.5)
        """
        if regime == "NEGATIVE":
            return NEGATIVE_GAMMA_TARGET_MULT
        elif regime == "POSITIVE":
            return POSITIVE_GAMMA_TARGET_MULT
        else:
            return NEUTRAL_GAMMA_TARGET_MULT

    # ------------------------------------------------------------------
    # Confidence Computation (v2 — 6 components)
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        trend_strength: float,
        delta_decline: bool,
        liquidity_vacuum: bool,
        net_gamma: float,
        regime: str,
        trend_direction: str,
        rolling_data: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Combine all v2 factors into confidence score.

        6 components:
            1. Trend strength: 0.0–0.20 (soft)
            2. Delta decline: 0.0 or 0.20 (hard gate)
            3. Liquidity vacuum: 0.0 or 0.25 (hard gate)
            4. IV acceleration: -0.05 to +0.15 (soft)
            5. Regime alignment: 0.0–0.10 (soft)
            6. Wall proximity: +0.0 to +0.10 (bonus)

        Args:
            trend_strength: Score from _trend_strength (0.0–1.0)
            delta_decline: Hard gate result
            liquidity_vacuum: Hard gate result
            net_gamma: Current net gamma
            regime: Regime string
            trend_direction: "UP" or "DOWN"
            rolling_data: Rolling window data for IV acceleration

        Returns:
            Confidence score 0.0–1.0
        """
        # 1. Trend strength (0.0–0.20)
        trend_conf = 0.10 + 0.10 * trend_strength

        # 2. Delta decline (hard gate — 0.0 or 0.20)
        delta_conf = 0.20 if delta_decline else 0.0

        # 3. Liquidity vacuum (hard gate — 0.0 or 0.25)
        liq_conf = 0.25 if liquidity_vacuum else 0.0

        # 4. IV acceleration (soft — -0.05 to +0.15)
        iv_conf = 0.0
        if rolling_data:
            iv_conf = self._compute_iv_acceleration(
                rolling_data, trend_direction
            )

        # 5. Regime alignment (soft — 0.0 to 0.10)
        regime_conf = self._regime_alignment(
            regime, net_gamma, trend_direction
        )

        # 6. Wall proximity bonus (already added via _check_wall_proximity
        #    in _check_exhaustion — not included here)

        confidence = (
            trend_conf + delta_conf + liq_conf + iv_conf + regime_conf
        )
        return min(1.0, max(0.0, confidence))

    def _regime_alignment(
        self, regime: str, net_gamma: float, trend_direction: str
    ) -> float:
        """
        Compute regime alignment score.

        Exhaustion signals are stronger when the regime supports mean
        reversion:
        - NEGATIVE gamma: supports reversal (high vol, fast moves)
        - POSITIVE gamma: supports mean reversion (low vol, slow moves)

        Args:
            regime: Current regime string
            net_gamma: Current net gamma
            trend_direction: "UP" or "DOWN"

        Returns:
            Alignment score 0.0–0.10
        """
        if regime == "NEGATIVE":
            return 0.10
        elif regime == "POSITIVE":
            return 0.10
        else:
            return 0.05

    # ------------------------------------------------------------------
    # v1 Helpers (kept for compatibility)
    # ------------------------------------------------------------------

    def _trend_strength(self, window: Any) -> float:
        """
        Score trend strength based on first-half vs second-half mean difference.

        Returns 0.0–1.0. Higher = stronger, more sustained trend.
        Direction-agnostic (works for both UP and DOWN trends).
        """
        if window.count < MIN_TREND_POINTS:
            return 0.0

        vals = list(window.values)
        half = len(vals) // 2
        first_half = statistics.mean(vals[:half])
        second_half = statistics.mean(vals[half:])
        diff = abs(second_half - first_half)
        std = window.std

        if std is None or std == 0:
            return 0.0

        # Normalize by std (same approach window.trend uses internally)
        strength = min(1.0, max(0.0, 0.3 + (diff / std) / 4.0))

        # Bonus for longer sustained trends
        duration_bonus = min(0.15, (window.count - MIN_TREND_POINTS) * 0.03)
        strength = min(1.0, strength + duration_bonus)

        return strength

    def _check_delta_decline(
        self,
        rolling_data: Dict[str, Any],
        current_delta: float,
    ) -> bool:
        """Check if total delta is declining below rolling average."""
        window = rolling_data.get(KEY_TOTAL_DELTA_5M)
        if window is None or window.count < MIN_GREEKS_POINTS:
            return False

        avg = window.mean
        if avg is None or avg == 0:
            return False

        # Delta should be declining: current below rolling avg
        # Account for sign: for positive delta, current < avg means declining
        # For negative delta, current > avg (less negative) means declining
        if abs(current_delta) < abs(avg * DELTA_DECLINE_RATIO):
            return False

        # Direction check: delta should be moving toward zero (weakening)
        if abs(current_delta) > abs(avg):
            return False

        return True
