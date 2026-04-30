"""
strategies/layer1/gamma_squeeze.py — Gamma Squeeze / Wall-Breaker

Pin detection + breakout through gamma wall.

Logic:
    1. Pin detection: narrow range (ATR < 0.3%), positive net gamma,
       price trapped between gamma walls
    2. Breakout candle: price closes beyond a gamma wall with volume
       confirmation
    3. Enter squeeze in breakout direction — dealer hedging accelerates
       the move as net gamma flips

Entry:
    - LONG squeeze: breakout above call wall with volume
    - SHORT squeeze: breakdown below put wall with volume

Exit:
    - Stop: back inside the wall or 1.5× ATR
    - Target: 2× risk (squeezes run hard)

Confidence factors:
    - Pin duration (longer pin = higher confidence)
    - Wall strength (stronger wall = bigger squeeze potential)
    - Volume confirmation (higher volume = higher confidence)
    - Net gamma at breakout (positive = acceleration)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.GammaSqueeze")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIN_ATR_PCT = 0.003           # 0.3% — max range for pin detection
WALL_PROXIMITY_PCT = 0.003    # 0.3% — price must be near wall for breakout
VOLUME_SURGE_MULT = 1.5       # 1.5× average volume = confirmation
MIN_WALL_GEX = 500000         # Minimum |GEX| for wall consideration
MIN_CONFIDENCE = 0.35         # Minimum confidence to emit signal
TARGET_RISK_MULT = 2.0        # 2× risk for squeeze targets


class GammaSqueeze(BaseStrategy):
    """
    Pin detection + wall-breakout squeeze strategy.

    When price is pinned between walls with positive gamma,
    a breakout through a wall triggers dealer hedging acceleration.
    """

    strategy_id = "gamma_squeeze"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return squeeze signals.

        Returns empty list when no pin or breakout is detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")

        signals: List[Signal] = []

        # Check for pin setup
        is_pin = self._is_pin(underlying_price, net_gamma, rolling_data, gex_calc)

        # Check for wall breakout
        breakout = self._detect_breakout(
            underlying_price, net_gamma, rolling_data, gex_calc
        )

        if breakout:
            # We have a breakout — enter squeeze
            sig = self._enter_squeeze(breakout, underlying_price, net_gamma, regime)
            if sig:
                signals.append(sig)
        elif is_pin:
            # Pin detected but no breakout yet — no signal (wait for breakout)
            pass

        return signals

    # ------------------------------------------------------------------
    # Pin Detection
    # ------------------------------------------------------------------

    def _is_pin(
        self,
        price: float,
        net_gamma: float,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
    ) -> bool:
        """
        Detect if price is pinned between gamma walls.

        Conditions:
            1. ATR (rolling range) < 0.3% of price
            2. Net gamma is positive (dealer support)
            3. Price is between two gamma walls
        """
        # Condition 1: Narrow range
        price_window = rolling_data.get("price_5m")
        if price_window is None or price_window.range is None:
            return False

        atr_pct = price_window.range / price
        if atr_pct > PIN_ATR_PCT:
            return False

        # Condition 2: Positive net gamma
        if net_gamma <= 0:
            return False

        # Condition 3: Price between walls
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
        if len(walls) < 2:
            return False

        above_walls = [w for w in walls if w["strike"] > price]
        below_walls = [w for w in walls if w["strike"] < price]

        # Must have at least one wall on each side
        return bool(above_walls and below_walls)

    # ------------------------------------------------------------------
    # Breakout Detection
    # ------------------------------------------------------------------

    def _detect_breakout(
        self,
        price: float,
        net_gamma: float,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Detect breakout through a gamma wall.

        Returns dict with breakout info or None.
        """
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
        if not walls:
            return None

        # Check if price is near any wall and breaking through
        for wall in walls:
            wall_strike = wall["strike"]
            wall_gex = wall["gex"]
            wall_side = wall["side"]

            # Price must be within WALL_PROXIMITY_PCT of wall
            distance_pct = abs(price - wall_strike) / price
            if distance_pct > WALL_PROXIMITY_PCT:
                continue

            # Determine breakout direction
            if wall_side == "call" and price >= wall_strike:
                # Breaking above call wall → LONG squeeze
                return {
                    "direction": Direction.LONG,
                    "wall_strike": wall_strike,
                    "wall_gex": wall_gex,
                    "wall_side": "call",
                    "type": "call_wall_breakout",
                }
            elif wall_side == "put" and price <= wall_strike:
                # Breaking below put wall → SHORT squeeze
                return {
                    "direction": Direction.SHORT,
                    "wall_strike": wall_strike,
                    "wall_gex": wall_gex,
                    "wall_side": "put",
                    "type": "put_wall_breakout",
                }

        return None

    # ------------------------------------------------------------------
    # Enter Squeeze
    # ------------------------------------------------------------------

    def _enter_squeeze(
        self,
        breakout: Dict[str, Any],
        price: float,
        net_gamma: float,
        regime: str,
    ) -> Optional[Signal]:
        """
        Enter squeeze trade on wall breakout.

        Dealer hedging accelerates the move as they adjust positions
        to maintain delta neutrality through the wall.
        """
        direction = breakout["direction"]
        wall_strike = breakout["wall_strike"]
        wall_gex = breakout["wall_gex"]
        wall_side = breakout["wall_side"]

        if direction == Direction.LONG:
            stop = wall_strike * 0.995  # Just below the wall
            risk = price - stop
            target = price + (risk * TARGET_RISK_MULT)
        else:
            stop = wall_strike * 1.005  # Just above the wall
            risk = stop - price
            target = price - (risk * TARGET_RISK_MULT)

        if risk <= 0:
            return None

        # Confidence: wall strength + net gamma + volume confirmation
        confidence = self._squeeze_confidence(
            wall_gex, net_gamma, price, risk, breakout
        )
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Squeeze {direction.value}: breakout through "
                f"{'call' if wall_side == 'call' else 'put'} wall at "
                f"{wall_strike:.2f}, GEX={wall_gex:.0f}, "
                f"net_gamma={net_gamma:.2f}"
            ),
            metadata={
                "breakout_type": breakout["type"],
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_side": wall_side,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _squeeze_confidence(
        self,
        wall_gex: float,
        net_gamma: float,
        price: float,
        risk: float,
        breakout: Dict[str, Any],
    ) -> float:
        """
        Confidence for squeeze trade.

        Higher when:
            - Wall GEX is massive (bigger squeeze potential)
            - Net gamma is positive (dealer acceleration)
            - Risk is tight (clean breakout)
        """
        # Wall strength: higher GEX = bigger squeeze (0.2–0.35)
        wall_conf = 0.2 + 0.15 * min(1.0, abs(wall_gex) / 5_000_000)

        # Net gamma: positive = acceleration (0.2–0.3)
        gamma_conf = 0.2 + 0.15 * min(1.0, net_gamma / 500_000)

        # Risk tightness: tighter risk = cleaner setup (0.15–0.25)
        risk_pct = risk / price
        risk_conf = 0.15 + 0.1 * min(1.0, 0.005 / max(risk_pct, 0.001))

        # Volume confirmation (0.1–0.15) — default if no volume data
        volume_conf = 0.1  # No volume data in layer 1

        return min(1.0, wall_conf + gamma_conf + risk_conf + volume_conf)
