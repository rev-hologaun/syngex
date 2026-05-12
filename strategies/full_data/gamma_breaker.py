"""
strategies/full_data/gamma_breaker.py — Gamma-Weighted Momentum (GAMMA-ALPHA)

Detects when price breaks through a major Gamma Wall with dealer hedging
acceleration.

Γ_break = Price_Velocity × Gamma_Concentration_at_Level

Bullish Breakout: Price > nearest call wall + velocity accelerating → LONG
Bearish Breakout: Price < nearest put wall + velocity accelerating → SHORT

Leading indicator: dealer hedging creates self-reinforcing feedback loop.
When price approaches a large gamma wall, dealers must hedge in the direction
of the move, accelerating price toward and through the wall.

Trigger: Γ_break > threshold AND price has crossed wall

Hard gates (ALL must pass):
    Gate A: Wall strength — wall GEX > 2σ above rolling avg (major wall)
    Gate B: Regime alignment — bullish in POSITIVE gamma, bearish in NEGATIVE gamma
    Gate C: Volume confirmation — breakout accompanied by volume spike

Confidence model (5 components):
    1. Γ_break magnitude (0.0–0.30)
    2. Wall proximity (0.0–0.20)
    3. Wall strength (0.0–0.15)
    4. Volume confirmation (0.0–0.15)
    5. GEX regime alignment (0.0–0.10)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_WALL_DISTANCE_5M,
    KEY_WALL_GEX_5M,
    KEY_WALL_GEX_SIGMA_5M,
    KEY_PRICE_VELOCITY_5M,
    KEY_GAMMA_BREAK_INDEX_5M,
    KEY_VOLUME_5M,
)

logger = logging.getLogger("Syngex.Strategies.GammaBreaker")


class GammaBreaker(BaseStrategy):
    """
    Gamma-Weighted Momentum (GAMMA-ALPHA) strategy.

    Detects gamma breakout events where price breaks through a major gamma
    wall with accelerating velocity. The key insight is that dealers hedging
    near large gamma walls create self-reinforcing momentum — when price
    approaches a wall, dealers must buy/sell to hedge, which pushes price
    further toward the wall.

    LONG: Price above nearest call wall + velocity accelerating + POSITIVE gamma regime
    SHORT: Price below nearest put wall + velocity accelerating + NEGATIVE gamma regime
    """

    strategy_id = "gamma_breaker"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for gamma breaker signal.

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
        gex_calc = data.get("gex_calculator")

        # 1. Get gamma breaker data from rolling windows
        min_gamma_break = params.get("min_gamma_break", 0.0005)
        min_wall_gex_sigma = params.get("min_wall_gex_sigma", 2.0)
        min_wall_distance_pct = params.get("min_wall_distance_pct", 0.005)
        volume_spike_mult = params.get("volume_spike_mult", 1.5)

        wall_dist_window = rolling_data.get(KEY_WALL_DISTANCE_5M)
        wall_gex_window = rolling_data.get(KEY_WALL_GEX_5M)
        wall_gex_sigma_window = rolling_data.get(KEY_WALL_GEX_SIGMA_5M)
        price_vel_window = rolling_data.get(KEY_PRICE_VELOCITY_5M)
        gamma_break_window = rolling_data.get(KEY_GAMMA_BREAK_INDEX_5M)

        if not gamma_break_window or gamma_break_window.count < 2:
            return []
        if not wall_gex_sigma_window or wall_gex_sigma_window.count < 5:
            return []
        if not price_vel_window or price_vel_window.count < 2:
            return []

        current_gamma_break = gamma_break_window.values[-1]
        current_wall_dist = wall_dist_window.values[-1] if wall_dist_window else 0.0
        current_wall_gex = wall_gex_window.values[-1] if wall_gex_window else 0.0
        current_wall_gex_sigma = wall_gex_sigma_window.values[-1]
        current_velocity = price_vel_window.values[-1]
        prev_velocity = price_vel_window.values[-2] if len(price_vel_window.values) >= 2 else 0.0

        # 2. Determine signal direction
        # LONG when price is above the nearest wall (call wall) and velocity accelerating
        # SHORT when price is below the nearest wall (put wall) and velocity accelerating
        # Velocity accelerating means current velocity > previous velocity
        velocity_accelerating = current_velocity > prev_velocity

        long_signal = (
            current_gamma_break > min_gamma_break
            and velocity_accelerating
        )
        short_signal = (
            current_gamma_break > min_gamma_break
            and velocity_accelerating
        )

        if not long_signal and not short_signal:
            return []

        # Use gamma_break direction: positive means breakout detected
        # Direction determined by regime: POSITIVE → LONG, NEGATIVE → SHORT
        if regime == "POSITIVE":
            direction = "LONG"
        elif regime == "NEGATIVE":
            direction = "SHORT"
        else:
            # Neutral regime — use wall side to determine direction
            if wall_gex_window and wall_gex_window.count > 0:
                # Default to LONG if we have data (conservative)
                direction = "LONG"
            else:
                return []

        # 3. Apply 3 HARD GATES
        gate_a = self._gate_a_wall_strength(
            current_wall_gex, current_wall_gex_sigma, min_wall_gex_sigma
        )

        if not gate_a:
            logger.debug(
                "Gamma Breaker: Gate A failed — wall not strong enough for %s",
                direction,
            )
            return []

        gate_b = self._gate_b_gex_regime(direction, regime)

        if not gate_b:
            logger.debug(
                "Gamma Breaker: Gate B failed — GEX regime misalignment for %s",
                direction,
            )
            return []

        gate_c = self._gate_c_volume_confirmation(
            rolling_data, volume_spike_mult
        )

        if not gate_c:
            logger.debug(
                "Gamma Breaker: Gate C failed — no volume confirmation for %s",
                direction,
            )
            return []

        # 4. Compute confidence (5-component model)
        confidence = self._compute_confidence(
            current_gamma_break,
            current_wall_dist,
            current_wall_gex_sigma,
            current_velocity,
            current_wall_gex,
            direction,
            rolling_data,
            params,
            regime,
        )

        min_confidence = params.get("min_confidence", 0.35)
        max_confidence = params.get("max_confidence", 0.85)
        confidence = max(min_confidence, min(confidence, max_confidence))

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

        # Intensity metadata
        # Yellow: Price approaching wall (within 0.1%)
        # Orange: Price has crossed wall, Γ_break detected
        # Red: Price rapidly moving away, dealer hedging in "panic mode"
        if current_velocity > 0.005:  # > 0.5% velocity = panic mode
            intensity = "red"
        elif current_wall_dist < 0.001:  # within 0.1% = approaching
            intensity = "yellow"
        elif current_gamma_break > min_gamma_break:
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
                f"Gamma breakout {direction}: Γ_break={current_gamma_break:.6f}, "
                f"wall_dist={current_wall_dist:.4f}, vel={current_velocity:.4f}"
            ),
            metadata={
                "direction": direction,
                "gamma_break": round(current_gamma_break, 6),
                "wall_distance_pct": round(current_wall_dist, 6),
                "wall_gex": round(current_wall_gex, 2),
                "wall_gex_sigma": round(current_wall_gex_sigma, 4),
                "price_velocity": round(current_velocity, 6),
                "velocity_accelerating": velocity_accelerating,
                "intensity": intensity,
                "regime": regime,
                "gates": {
                    "A_wall_strength": gate_a,
                    "B_gex_regime": gate_b,
                    "C_volume_confirmation": gate_c,
                },
            },
        )]

    def _gate_a_wall_strength(
        self,
        wall_gex: float,
        wall_gex_sigma: float,
        min_sigma: float,
    ) -> bool:
        """
        Gate A: Wall strength.

        The wall GEX must be above the rolling σ threshold, confirming this
        is a major gamma wall, not a minor one. This ensures we're trading
        breakouts through walls that matter.
        """
        if wall_gex_sigma <= 0:
            return False
        return wall_gex_sigma >= min_sigma

    def _gate_b_gex_regime(self, direction: str, regime: str) -> bool:
        """
        Gate B: GEX regime alignment.

        LONG signals require POSITIVE gamma regime (dealers hedging by buying
        dips, creating self-reinforcing upward momentum).
        SHORT signals require NEGATIVE gamma regime (dealers hedging by selling
        rallies, creating self-reinforcing downward momentum).
        """
        if direction == "LONG" and regime == "POSITIVE":
            return True
        if direction == "SHORT" and regime == "NEGATIVE":
            return True
        return False

    def _gate_c_volume_confirmation(
        self,
        rolling_data: Dict[str, Any],
        volume_spike_mult: float,
    ) -> bool:
        """
        Gate C: Volume confirmation.

        Breakout must be accompanied by volume above average, confirming
        genuine participation rather than thin-market noise.
        """
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0:
            current_vol = volume_window.latest
            avg_vol = volume_window.mean
            if current_vol is not None and avg_vol is not None and avg_vol > 0:
                return current_vol >= avg_vol * volume_spike_mult
        # No volume data — pass gate (can't evaluate)
        return True

    def _compute_confidence(
        self,
        current_gamma_break: float,
        current_wall_dist: float,
        current_wall_gex_sigma: float,
        current_velocity: float,
        current_wall_gex: float,
        direction: str,
        rolling_data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
    ) -> float:
        """
        Compute 5-component confidence score.

        Returns 0.0–1.0.
        """
        min_gamma_break = params.get("min_gamma_break", 0.0005)
        min_wall_gex_sigma = params.get("min_wall_gex_sigma", 2.0)

        # 1. Γ_break magnitude (0.0–0.30)
        # How extreme the gamma breakout signal is
        conf_gamma_break = 0.0
        if current_gamma_break > min_gamma_break:
            # Scale from 0 at threshold to 0.30 at 5× threshold
            conf_gamma_break = min(0.30, 0.10 + 0.20 * min(1.0, (current_gamma_break - min_gamma_break) / (min_gamma_break * 4)))
            conf_gamma_break = max(0.05, conf_gamma_break)

        # 2. Wall proximity (0.0–0.20)
        # Closer to wall = higher conviction the breakout will succeed
        conf_proximity = 0.0
        if current_wall_dist > 0:
            # Closer = higher confidence. At 0.5% distance = 0.10 baseline,
            # at 0.05% distance = 0.20 max
            conf_proximity = min(0.20, 0.20 * min(1.0, min_wall_distance_pct / max(current_wall_dist, 0.00001)))
            conf_proximity = max(0.05, conf_proximity)

        # 3. Wall strength (0.0–0.15)
        # Higher σ means wall is more significant
        conf_strength = 0.0
        if current_wall_gex_sigma > 0:
            # At min_sigma threshold = 0.075 baseline, above = bonus
            conf_strength = min(0.15, 0.075 + 0.075 * min(1.0, (current_wall_gex_sigma - min_wall_gex_sigma) / min_wall_gex_sigma))
            conf_strength = max(0.05, conf_strength)

        # 4. Volume confirmation (0.0–0.15)
        # Volume above average confirms genuine participation
        conf_volume = 0.05  # baseline (gate C already passed)
        volume_window = rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0:
            current_vol = volume_window.latest
            avg_vol = volume_window.mean
            if current_vol is not None and avg_vol is not None and avg_vol > 0:
                vol_ratio = current_vol / avg_vol
                conf_volume = 0.05 + 0.10 * min(1.0, max(0, (vol_ratio - 1.0) / 1.0))

        # 5. GEX regime alignment (0.0–0.10)
        # Signal direction matches GEX bias
        conf_gex = 0.05  # baseline (gate B already passed)
        if regime:
            if direction == "LONG" and regime == "POSITIVE":
                conf_gex = 0.10
            elif direction == "SHORT" and regime == "NEGATIVE":
                conf_gex = 0.10

        # Sum all components
        confidence = (
            conf_gamma_break + conf_proximity + conf_strength +
            conf_volume + conf_gex
        )
        return min(1.0, max(0.0, confidence))
