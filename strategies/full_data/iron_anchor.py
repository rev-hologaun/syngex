"""
strategies/full_data/iron_anchor.py — Iron Anchor (CONFLUENCE-ALPHA)

Detects when a Gamma Wall aligns with a Liquidity Wall within $1.00.
Ω_conf = |Price_GammaWall - Price_LiquidityWall|

Bullish Reversal: Bid Liquidity Wall near Put Wall → LONG (mean reversion)
Bearish Reversal: Ask Liquidity Wall near Call Wall → SHORT (mean reversion)
Highest conviction mean reversion signal — dual confirmation.

Trigger: Ω_conf < $1.00 AND price approaching AND velocity decreasing

Hard gates (ALL must pass):
    Gate A: Weight check — liquidity wall size > 3σ above rolling avg
    Gate B: Gamma density — gamma wall must be significant (not minor outlier)
    Gate C: Exhaustion — price velocity decreasing as approaching confluence

Confidence model (5 components):
    1. Confluence proximity (0.0–0.30) — tighter Ω_conf = higher confidence
    2. Liquidity weight (0.0–0.20) — heavier wall = more conviction
    3. Gamma density (0.0–0.15) — thicker wall = more structural support
    4. Exhaustion signal (0.0–0.15) — velocity dying = better entry
    5. GEX regime alignment (0.0–0.10) — signal direction matches GEX bias
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_CONFLUENCE_PROX_5M,
    KEY_CONFLUENCE_SIGNAL_5M,
    KEY_LIQUIDITY_WALL_SIZE_5M,
    KEY_LIQUIDITY_WALL_SIGMA_5M,
    KEY_PRICE_VELOCITY_5M,
)

logger = logging.getLogger("Syngex.Strategies.IronAnchor")


class IronAnchor(BaseStrategy):
    """
    Iron Anchor strategy — detects Gamma/Liquidity wall confluence.

    When a Gamma Wall (major options strike with high GEX) aligns with a
    Liquidity Wall (large bid/ask depth) within a tight proximity threshold,
    it creates a high-conviction mean reversion signal.

    LONG: Bid Liquidity Wall near Put Wall (bullish reversal)
          AND velocity decreasing AND GEX regime POSITIVE
    SHORT: Ask Liquidity Wall near Call Wall (bearish reversal)
           AND velocity decreasing AND GEX regime NEGATIVE
    """

    strategy_id = "iron_anchor"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for Iron Anchor confluence signal.

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

        # 1. Get confluence metrics from rolling windows
        min_data_points = params.get("min_data_points", 10)
        max_confluence_distance = params.get("max_confluence_distance", 1.0)
        min_liq_wall_sigma = params.get("min_liq_wall_sigma", 3.0)
        min_gamma_wall_gex = params.get("min_gamma_wall_gex", 500000)
        exhaustion_velocity_mult = params.get("exhaustion_velocity_mult", 0.8)

        prox_window = rolling_data.get(KEY_CONFLUENCE_PROX_5M)
        signal_window = rolling_data.get(KEY_CONFLUENCE_SIGNAL_5M)
        liq_size_window = rolling_data.get(KEY_LIQUIDITY_WALL_SIZE_5M)
        liq_sigma_window = rolling_data.get(KEY_LIQUIDITY_WALL_SIGMA_5M)
        velocity_window = rolling_data.get(KEY_PRICE_VELOCITY_5M)

        # Need sufficient data for all windows
        if not prox_window or prox_window.count < min_data_points:
            return []
        if not signal_window or signal_window.count < min_data_points:
            return []
        if not liq_size_window or liq_size_window.count < min_data_points:
            return []

        current_prox = prox_window.values[-1]
        current_signal = signal_window.values[-1]
        current_liq_size = liq_size_window.values[-1]
        current_liq_sigma = liq_sigma_window.values[-1] if liq_sigma_window else 0.0

        # Current velocity (latest value)
        current_velocity = velocity_window.values[-1] if velocity_window else 0.0

        # Average velocity (mean of window) for exhaustion check
        avg_velocity = velocity_window.mean if velocity_window else 0.0

        # 2. Determine signal direction from confluence signal
        # Signal +1 = bullish (bid wall near put wall) → LONG
        # Signal -1 = bearish (ask wall near call wall) → SHORT
        long_signal = current_signal > 0
        short_signal = current_signal < 0

        if not long_signal and not short_signal:
            return []

        # Only emit one signal per evaluation
        if long_signal and short_signal:
            # Both can't be true simultaneously; pick based on proximity
            direction = "LONG" if current_signal > 0 else "SHORT"
        elif long_signal:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 3. Check confluence proximity threshold
        if current_prox > max_confluence_distance:
            logger.debug(
                "Iron Anchor: Confluence proximity %.2f exceeds %.1f for %s",
                current_prox, max_confluence_distance, direction,
            )
            return []

        # 4. Apply 3 HARD GATES
        gate_a = self._gate_a_liq_weight(
            current_liq_size, current_liq_sigma, min_liq_wall_sigma, liq_size_window
        )

        if not gate_a:
            logger.debug(
                "Iron Anchor: Gate A failed — liquidity weight check for %s", direction,
            )
            return []

        gate_b = self._gate_b_gamma_density(
            gex_calc, regime, direction, min_gamma_wall_gex
        )

        if not gate_b:
            logger.debug(
                "Iron Anchor: Gate B failed — gamma density check for %s", direction,
            )
            return []

        gate_c = self._gate_c_exhaustion(
            current_velocity, avg_velocity, exhaustion_velocity_mult
        )

        if not gate_c:
            logger.debug(
                "Iron Anchor: Gate C failed — exhaustion check for %s", direction,
            )
            return []

        # 5. Compute confidence (5-component model)
        confidence = self._compute_confidence(
            current_prox,
            current_liq_size,
            current_liq_sigma,
            current_velocity,
            avg_velocity,
            direction,
            regime,
            gex_calc,
            params,
        )

        min_confidence = params.get("min_confidence", 0.35)
        max_confidence = params.get("max_confidence", 0.85)
        confidence = max(min_confidence, min(confidence, max_confidence))

        if confidence < min_confidence:
            return []

        # 6. Build signal with entry/stop/target
        stop_pct = params.get("stop_pct", 0.008)
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

        # Intensity metadata based on confluence proximity
        if current_prox < 0.10:
            intensity = "red"
        elif current_prox < 0.50:
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
                f"Iron Anchor {direction}: Ω_conf=${current_prox:.2f}, "
                f"liq_size={current_liq_size:.0f}"
            ),
            metadata={
                "direction": direction,
                "confluence_proximity": round(current_prox, 4),
                "liq_wall_size": round(current_liq_size, 0),
                "liq_wall_sigma": round(current_liq_sigma, 4),
                "velocity": round(current_velocity, 6),
                "avg_velocity": round(avg_velocity, 6),
                "intensity": intensity,
                "regime": regime,
                "gates": {
                    "A_liq_weight": gate_a,
                    "B_gamma_density": gate_b,
                    "C_exhaustion": gate_c,
                },
            },
        )]

    def _gate_a_liq_weight(
        self,
        liq_size: float,
        liq_sigma: float,
        min_sigma: float,
        liq_size_window: Any,
    ) -> bool:
        """
        Gate A: Liquidity weight check.

        The liquidity wall size must be > min_sigma standard deviations above
        the rolling average, confirming it's a significant structural wall
        rather than normal order book noise.
        """
        if liq_sigma <= 0:
            return False

        if liq_size_window is None or liq_size_window.count < 5:
            return False

        mean_size = liq_size_window.mean
        if mean_size <= 0:
            return False

        threshold = mean_size + min_sigma * liq_sigma
        return liq_size > threshold

    def _gate_b_gamma_density(
        self,
        gex_calc: Any,
        regime: str,
        direction: str,
        min_gamma_wall_gex: float,
    ) -> bool:
        """
        Gate B: Gamma density and GEX regime alignment.

        The gamma wall must be significant (not a minor outlier), and the
        signal direction must align with the GEX regime:
        - LONG requires POSITIVE gamma regime
        - SHORT requires NEGATIVE gamma regime
        """
        if not regime:
            return False

        # GEX regime alignment — same pattern as other full_data strategies
        if direction == "LONG" and regime != "POSITIVE":
            return False
        if direction == "SHORT" and regime != "NEGATIVE":
            return False

        # Check that the gamma wall is significant
        if gex_calc and hasattr(gex_calc, "get_gamma_walls"):
            walls = gex_calc.get_gamma_walls(threshold=min_gamma_wall_gex)
            if not walls:
                return False

        return True

    def _gate_c_exhaustion(
        self,
        current_velocity: float,
        avg_velocity: float,
        velocity_mult: float,
    ) -> bool:
        """
        Gate C: Exhaustion signal.

        Price velocity must be decreasing as approaching confluence,
        confirming the market is running out of momentum. Current velocity
        should be below the rolling average (velocity dying).
        """
        if avg_velocity <= 0:
            return True  # No velocity data — pass (can't evaluate)

        # Current velocity should be decreasing relative to average
        return current_velocity < avg_velocity * velocity_mult

    def _compute_confidence(
        self,
        current_prox: float,
        current_liq_size: float,
        current_liq_sigma: float,
        current_velocity: float,
        avg_velocity: float,
        direction: str,
        regime: str,
        gex_calc: Any,
        params: Dict[str, Any],
    ) -> float:
        """
        Compute 5-component confidence score.

        Returns 0.0–1.0.
        """
        max_confluence_distance = params.get("max_confluence_distance", 1.0)
        min_liq_wall_sigma = params.get("min_liq_wall_sigma", 3.0)

        # 1. Confluence proximity (0.0–0.30)
        # Tighter Ω_conf = higher confidence
        conf_prox = 0.0
        if current_prox >= 0 and max_confluence_distance > 0:
            # At threshold distance = 0.05 baseline, at 0 = max
            proximity_ratio = 1.0 - (current_prox / max_confluence_distance)
            proximity_ratio = max(0.0, min(1.0, proximity_ratio))
            conf_prox = 0.05 + 0.25 * proximity_ratio

        # 2. Liquidity weight (0.0–0.20)
        # Heavier wall = more conviction
        conf_liq = 0.05  # baseline (gate A already passed)
        if current_liq_sigma > 0:
            sigma_ratio = min(1.0, current_liq_sigma / (min_liq_wall_sigma * 2))
            conf_liq = 0.05 + 0.15 * sigma_ratio

        # 3. Gamma density (0.0–0.15)
        # Thicker wall = more structural support
        conf_gamma = 0.075  # baseline (gate B already passed)
        if gex_calc and hasattr(gex_calc, "get_gamma_walls"):
            walls = gex_calc.get_gamma_walls(threshold=params.get("min_gamma_wall_gex", 500000))
            if walls:
                # More walls in the vicinity = higher density
                total_gex = sum(abs(w.get("gex", 0)) for w in walls)
                if total_gex > 0:
                    density_score = min(1.0, total_gex / 10000000)  # normalize
                    conf_gamma = 0.075 + 0.075 * density_score

        # 4. Exhaustion signal (0.0–0.15)
        # Velocity dying = better entry
        conf_exhaust = 0.05  # baseline (gate C already passed)
        if avg_velocity > 0:
            exhaustion_ratio = 1.0 - (current_velocity / avg_velocity)
            exhaustion_ratio = max(0.0, min(1.0, exhaustion_ratio))
            conf_exhaust = 0.05 + 0.10 * exhaustion_ratio

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
            conf_prox + conf_liq + conf_gamma +
            conf_exhaust + conf_gex
        )
        return min(1.0, max(0.0, confidence))
