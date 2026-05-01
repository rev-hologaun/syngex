"""
strategies/layer1/gamma_wall_bounce.py — Gamma Wall Bounce

Mean-reversion strategy: trade the rejection at high-GEX gamma walls.

Logic:
    - Call walls (positive GEX) act as resistance — dealers sell rallies
    - Put walls (negative GEX) act as support — dealers buy dips
    - When price approaches within 0.5% of a wall and shows rejection,
      trade the bounce back toward the center

Entry:
    - Call wall at resistance → SHORT
    - Put wall at support → LONG

Exit:
    - Stop: 0.4% past the wall
    - Target: midpoint between walls or 1.5× risk

Confidence factors:
    - Wall proximity (closer = higher confidence)
    - Wall strength (higher |GEX| = higher confidence)
    - Regime alignment (positive regime favors call-wall shorts)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.GammaWallBounce")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WALL_PROXIMITY_PCT = 0.005       # 0.5% — how close price must be to wall
STOP_PAST_WALL_PCT = 0.004       # 0.4% — stop beyond the wall
TARGET_RISK_MULT = 1.5           # 1.5× risk for target
MIN_WALL_GEX = 500000            # Minimum |GEX| to consider a wall
MIN_CONFIDENCE = 0.35            # Minimum confidence to emit signal
MAX_CONFIDENCE = 0.85            # Hard cap — wall bounce alone can't be max conviction


class GammaWallBounce(BaseStrategy):
    """
    Mean-reversion strategy trading bounces off gamma walls.

    Call walls repel price downward (dealer hedging sells rallies).
    Put walls repel price upward (dealer hedging buys dips).
    """

    strategy_id = "gamma_wall_bounce"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return bounce signals.

        Returns empty list when no wall rejection is detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        # Get walls above and below price
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
        if not walls:
            return []

        price_above_walls = [w for w in walls if w["strike"] > underlying_price]
        price_below_walls = [w for w in walls if w["strike"] < underlying_price]

        signals: List[Signal] = []

        # Check call walls above price → potential SHORT bounce
        for wall in price_above_walls:
            sig = self._check_call_wall(wall, underlying_price, walls)
            if sig:
                signals.append(sig)

        # Check put walls below price → potential LONG bounce
        for wall in price_below_walls:
            sig = self._check_put_wall(wall, underlying_price, walls)
            if sig:
                signals.append(sig)

        return signals

    # ------------------------------------------------------------------
    # Call wall: price approaches from below → SHORT
    # ------------------------------------------------------------------

    def _check_call_wall(
        self,
        wall: Dict[str, Any],
        price: float,
        all_walls: List[Dict[str, Any]],
    ) -> Optional[Signal]:
        """
        Evaluate a call wall for SHORT bounce opportunity.

        Call wall = positive net_gamma → acts as resistance.
        We want price approaching from below and showing rejection.
        """
        wall_strike = wall["strike"]
        wall_gex = wall["gex"]

        # Check proximity: price must be within WALL_PROXIMITY_PCT below wall
        distance_pct = (wall_strike - price) / price
        if distance_pct < 0:
            # Price already above the wall — no bounce setup
            return None
        if distance_pct > WALL_PROXIMITY_PCT:
            # Too far from wall
            return None

        # Check rejection: price should be in lower part of recent range
        # Use rolling window if available, otherwise rely on proximity
        rejection_score = self._rejection_score(wall, price, all_walls)
        if rejection_score < 0.5:
            return None

        # Calculate confidence
        confidence = self._compute_confidence(
            distance_pct, wall_gex, rejection_score, "call"
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        stop = wall_strike * (1 + STOP_PAST_WALL_PCT)
        risk = stop - price
        target = price - (risk * TARGET_RISK_MULT)

        # Also consider midpoint to next wall as target
        target = self._better_target(price, target, stop, all_walls, "call")

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Call wall at {wall_strike} rejected price, GEX={wall_gex:.0f}, "
                   f"distance={distance_pct:.2%}",
            metadata={
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_side": "call",
                "distance_to_wall_pct": round(distance_pct, 4),
                "rejection_score": round(rejection_score, 3),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2) if risk > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # Put wall: price approaches from above → LONG
    # ------------------------------------------------------------------

    def _check_put_wall(
        self,
        wall: Dict[str, Any],
        price: float,
        all_walls: List[Dict[str, Any]],
    ) -> Optional[Signal]:
        """
        Evaluate a put wall for LONG bounce opportunity.

        Put wall = negative net_gamma → acts as support.
        We want price approaching from above and showing rejection.
        """
        wall_strike = wall["strike"]
        wall_gex = wall["gex"]

        # Check proximity: price must be within WALL_PROXIMITY_PCT above wall
        distance_pct = (price - wall_strike) / price
        if distance_pct < 0:
            # Price already below the wall
            return None
        if distance_pct > WALL_PROXIMITY_PCT:
            return None

        rejection_score = self._rejection_score(wall, price, all_walls)
        if rejection_score < 0.5:
            return None

        confidence = self._compute_confidence(
            distance_pct, abs(wall_gex), rejection_score, "put"
        )
        if confidence < MIN_CONFIDENCE:
            return None

        stop = wall_strike * (1 - STOP_PAST_WALL_PCT)
        risk = price - stop
        target = price + (risk * TARGET_RISK_MULT)

        target = self._better_target(price, target, stop, all_walls, "put")

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Put wall at {wall_strike} supported price, GEX={abs(wall_gex):.0f}, "
                   f"distance={distance_pct:.2%}",
            metadata={
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_side": "put",
                "distance_to_wall_pct": round(distance_pct, 4),
                "rejection_score": round(rejection_score, 3),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2) if risk > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _rejection_score(
        self,
        wall: Dict[str, Any],
        price: float,
        all_walls: List[Dict[str, Any]],
    ) -> float:
        """
        Score how strongly price is being rejected at a wall.

        1.0 = strong rejection (price well below wall for call, above for put)
        0.0 = no rejection (price right at wall)
        """
        wall_strike = wall["strike"]
        distance_pct = abs(wall_strike - price) / price

        # Base score from proximity: closer to wall = better rejection setup
        # But not too close — we want some room between price and wall
        if distance_pct < 0.0005:
            # Price essentially AT the wall — could be breakout, not bounce
            return 0.3
        elif distance_pct < WALL_PROXIMITY_PCT:
            # In the rejection zone
            return 0.5 + 0.5 * (1 - distance_pct / WALL_PROXIMITY_PCT)
        else:
            return 0.0

    def _compute_confidence(
        self,
        distance_pct: float,
        gex_magnitude: float,
        rejection_score: float,
        side: str,
    ) -> float:
        """
        Combine proximity, wall strength, and rejection into confidence.

        Returns 0.0–1.0.
        """
        # Proximity component: closer = higher confidence (0.3–0.5)
        proximity_conf = 0.3 + 0.2 * (1 - distance_pct / WALL_PROXIMITY_PCT)

        # Wall strength component: higher GEX = higher confidence (0.2–0.3)
        # Normalize: 500k = low, 5M+ = high
        strength_conf = 0.2 + 0.3 * min(1.0, gex_magnitude / 5_000_000)

        # Rejection component: 0.2–0.3
        rejection_conf = 0.2 + 0.1 * rejection_score

        # Normalize each component to [0,1] and average
        norm_prox = (proximity_conf - 0.3) / (0.5 - 0.3) if 0.5 != 0.3 else 1.0
        norm_strength = (strength_conf - 0.2) / (0.5 - 0.2) if 0.5 != 0.2 else 1.0
        norm_reject = (rejection_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0
        confidence = (norm_prox + norm_strength + norm_reject) / 3.0
        return min(MAX_CONFIDENCE, max(0.0, confidence))

    def _better_target(
        self,
        price: float,
        risk_target: float,
        stop: float,
        walls: List[Dict[str, Any]],
        side: str,
    ) -> float:
        """
        Choose between risk-based target and wall-midpoint target.

        For SHORT: pick the lower of risk target and midpoint below.
        For LONG: pick the higher of risk target and midpoint above.
        """
        if side == "call":
            # Find nearest wall below price
            below = [w for w in walls if w["strike"] < price]
            if below:
                nearest_below = max(w["strike"] for w in below)
                midpoint = (price + nearest_below) / 2
                # For SHORT, target should be below midpoint
                return min(risk_target, midpoint)
            return risk_target
        else:
            # Find nearest wall above price
            above = [w for w in walls if w["strike"] > price]
            if above:
                nearest_above = min(w["strike"] for w in above)
                midpoint = (price + nearest_above) / 2
                # For LONG, target should be above midpoint
                return max(risk_target, midpoint)
            return risk_target
