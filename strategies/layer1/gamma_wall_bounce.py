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
import time
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M
from strategies.volume_filter import VolumeFilter

logger = logging.getLogger("Syngex.Strategies.GammaWallBounce")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WALL_PROXIMITY_PCT = 0.005       # 0.5% — how close price must be to wall
STOP_PAST_WALL_PCT = 0.004       # 0.4% — stop beyond the wall
TARGET_RISK_MULT = 1.5           # 1.5× risk for target
MIN_WALL_GEX = 500000            # Minimum |GEX| to consider a wall
MIN_CONFIDENCE = 0.25            # Minimum confidence to emit signal
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

        rolling_data = data.get("rolling_data")

        # Global volume filter — wall bounce is mean-reversion, needs volume conviction
        vol_check = VolumeFilter.evaluate(rolling_data, MIN_CONFIDENCE)
        if not vol_check["recommended"]:
            return []

        # Get walls above and below price — use classification to filter magnets
        walls = gex_calc.get_wall_classifications(threshold=MIN_WALL_GEX)
        # Filter out magnets and ghosts — gamma_wall_bounce only trades actual walls
        walls = [w for w in walls if w.get("classification") == "wall"]
        if not walls:
            return []

        ts = data.get("timestamp", time.time())

        price_above_walls = [w for w in walls if w["strike"] > underlying_price]
        price_below_walls = [w for w in walls if w["strike"] < underlying_price]

        signals: List[Signal] = []

        # Check call walls above price → potential SHORT bounce
        for wall in price_above_walls:
            sig = self._check_call_wall(wall, underlying_price, walls, rolling_data,
                                        data.get("regime", ""), data)
            if sig:
                signals.append(sig)

        # Check put walls below price → potential LONG bounce
        for wall in price_below_walls:
            sig = self._check_put_wall(wall, underlying_price, walls, rolling_data,
                                       data.get("regime", ""), data)
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
        rolling_data: Dict[str, Any] = None,
        regime: str = "",
        data: Dict[str, Any] = None,
    ) -> Optional[Signal]:
        """
        Evaluate a call wall for SHORT bounce opportunity.

        Call wall = positive net_gamma → acts as resistance.
        We want price approaching from below and showing rejection.
        """
        wall_strike = wall["strike"]
        wall_gex = wall["gex"]

        # Extract gex_calc from data dict
        gex_calc = data.get("gex_calculator") if data else None

        # Freshness check — skip ghost walls
        if wall.get("is_ghost", False):
            return None

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
        rejection_score = self._rejection_score(wall, price, all_walls, rolling_data)
        if rejection_score < 0.6:
            return None

        # Check velocity: if price is crossing the wall at high speed,
        # the wall is permeable — skip the signal
        if not self._check_velocity(price, wall_strike, rolling_data, "call"):
            return None

        # Get trend from rolling data
        pw = rolling_data.get(KEY_PRICE_5M) if rolling_data else None
        trend = pw.trend if pw else "UNKNOWN"

        # ── NEW: Liquidity decay check ──
        depth_snapshot = data.get("depth_snapshot")
        if depth_snapshot and not self._check_liquidity_decay(wall, depth_snapshot):
            logger.debug("Call wall at %s: liquidity decay detected, skipping",
                         wall_strike)
            return None

        # ── NEW: Liquidity validation ──
        liq_score = 0.5  # default neutral
        if depth_snapshot:
            liq_score = self._check_liquidity_validation(wall, price, depth_snapshot)
            if liq_score < 0.25:
                logger.debug("Call wall at %s: insufficient liquidity validation "
                             "(score=%.2f), skipping", wall_strike, liq_score)
                return None

        # ── NEW: Vol support score ──
        vol_score = 0.5  # default neutral
        if depth_snapshot:
            vol_score = self._compute_vol_support_score(wall, gex_calc, price)

        # Calculate confidence
        confidence = self._compute_confidence(
            distance_pct, wall_gex, rejection_score, "call", regime,
            depth_snapshot=depth_snapshot, liq_score=liq_score, vol_score=vol_score,
            gex_calc=gex_calc, price=price,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        stop = wall_strike * (1 + STOP_PAST_WALL_PCT)
        risk = stop - price
        target = price - (risk * TARGET_RISK_MULT)

        # Also consider midpoint to next wall as target
        target = self._better_target(price, target, stop, all_walls, "call")

        # Depth snapshot helpers for metadata
        depth_bid_current = 0
        depth_ask_current = 0
        depth_spread_current = 0.0
        if depth_snapshot:
            depth_bid_current = depth_snapshot.get("bid_size", {}).get("current", 0)
            depth_ask_current = depth_snapshot.get("ask_size", {}).get("current", 0)
            depth_spread_current = depth_snapshot.get("spread", {}).get("current", 0.0)

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
                "regime": regime,
                "trend": trend,
                "liquidity_validation_score": round(liq_score, 3),
                "vol_support_score": round(vol_score, 3),
                "depth_bid_size": depth_bid_current,
                "depth_ask_size": depth_ask_current,
                "depth_spread": round(depth_spread_current, 4),
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
        rolling_data: Dict[str, Any] = None,
        regime: str = "",
        data: Dict[str, Any] = None,
    ) -> Optional[Signal]:
        """
        Evaluate a put wall for LONG bounce opportunity.

        Put wall = negative net_gamma → acts as support.
        We want price approaching from above and showing rejection.
        """
        wall_strike = wall["strike"]
        wall_gex = wall["gex"]

        # Extract gex_calc from data dict
        gex_calc = data.get("gex_calculator") if data else None

        # Freshness check — skip ghost walls
        if wall.get("is_ghost", False):
            return None

        # Check proximity: price must be within WALL_PROXIMITY_PCT above wall
        distance_pct = (price - wall_strike) / price
        if distance_pct < 0:
            # Price already below the wall
            return None
        if distance_pct > WALL_PROXIMITY_PCT:
            return None

        rejection_score = self._rejection_score(wall, price, all_walls, rolling_data)
        if rejection_score < 0.6:
            return None

        # Check velocity: if price is crossing the wall at high speed,
        # the wall is permeable — skip the signal
        if not self._check_velocity(price, wall_strike, rolling_data, "put"):
            return None

        # Get trend from rolling data
        pw = rolling_data.get(KEY_PRICE_5M) if rolling_data else None
        trend = pw.trend if pw else "UNKNOWN"

        # ── NEW: Liquidity decay check ──
        depth_snapshot = data.get("depth_snapshot")
        if depth_snapshot and not self._check_liquidity_decay(wall, depth_snapshot):
            logger.debug("Put wall at %s: liquidity decay detected, skipping",
                         wall_strike)
            return None

        # ── NEW: Liquidity validation ──
        liq_score = 0.5  # default neutral
        if depth_snapshot:
            liq_score = self._check_liquidity_validation(wall, price, depth_snapshot)
            if liq_score < 0.25:
                logger.debug("Put wall at %s: insufficient liquidity validation "
                             "(score=%.2f), skipping", wall_strike, liq_score)
                return None

        # ── NEW: Vol support score ──
        vol_score = 0.5  # default neutral
        if depth_snapshot:
            vol_score = self._compute_vol_support_score(wall, gex_calc, price)

        confidence = self._compute_confidence(
            distance_pct, abs(wall_gex), rejection_score, "put", regime,
            depth_snapshot=depth_snapshot, liq_score=liq_score, vol_score=vol_score,
            gex_calc=gex_calc, price=price,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        stop = wall_strike * (1 - STOP_PAST_WALL_PCT)
        risk = price - stop
        target = price + (risk * TARGET_RISK_MULT)

        target = self._better_target(price, target, stop, all_walls, "put")

        # Depth snapshot helpers for metadata
        depth_bid_current = 0
        depth_ask_current = 0
        depth_spread_current = 0.0
        if depth_snapshot:
            depth_bid_current = depth_snapshot.get("bid_size", {}).get("current", 0)
            depth_ask_current = depth_snapshot.get("ask_size", {}).get("current", 0)
            depth_spread_current = depth_snapshot.get("spread", {}).get("current", 0.0)

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
                "regime": regime,
                "trend": trend,
                "liquidity_validation_score": round(liq_score, 3),
                "vol_support_score": round(vol_score, 3),
                "depth_bid_size": depth_bid_current,
                "depth_ask_size": depth_ask_current,
                "depth_spread": round(depth_spread_current, 4),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _check_velocity(
        self,
        price: float,
        wall_strike: float,
        rolling_data: Dict[str, Any] = None,
        wall_side: str = "",
    ) -> bool:
        """
        Check if price is approaching wall at high velocity.
        If velocity is too high, the wall is being pierced, not rejected.
        Returns True if velocity is acceptable (low enough for bounce), False if too high.
        """
        pw = rolling_data.get(KEY_PRICE_5M) if rolling_data else None
        if pw is None or pw.count < 3:
            return True  # No data, assume acceptable

        recent = pw.values[-3:]
        if len(recent) < 2:
            return True

        # Calculate velocity: price change per tick as % of price
        tick_velocity = abs(recent[-1] - recent[0]) / abs(recent[0])

        # If velocity > 0.5% per tick, wall is being pierced
        VELOCITY_THRESHOLD = 0.005
        if tick_velocity > VELOCITY_THRESHOLD:
            return False

        return True

    def _rejection_score(
        self,
        wall: Dict[str, Any],
        price: float,
        all_walls: List[Dict[str, Any]],
        rolling_data: Dict[str, Any] = None,
    ) -> float:
        """Score how strongly price is being rejected at a wall.
        Uses actual price momentum: price moving AWAY from wall = strong rejection."""
        wall_strike = wall["strike"]
        distance_pct = abs(wall_strike - price) / price
        if distance_pct < 0.0005:
            base_score = 0.3
        elif distance_pct < WALL_PROXIMITY_PCT:
            base_score = 0.5 + 0.5 * (1 - distance_pct / WALL_PROXIMITY_PCT)
        else:
            return 0.0
        if rolling_data:
            from strategies.rolling_keys import KEY_PRICE_5M, KEY_TOTAL_GAMMA_5M
            pw = rolling_data.get(KEY_PRICE_5M)
            if pw and pw.count >= 3:
                recent = pw.values[-min(3, len(pw.values)):]
                if len(recent) >= 2:
                    price_change = (recent[-1] - recent[0]) / abs(recent[0])
                    if wall_strike > price:
                        momentum_score = max(-1.0, min(0.0, price_change * 100))
                    else:
                        momentum_score = max(0.0, min(1.0, price_change * 100))
                    base_score *= (1 + momentum_score)
            gw = rolling_data.get(KEY_TOTAL_GAMMA_5M)
            if gw and gw.count >= 3:
                recent_g = gw.values[-3:]
                gamma_trend = recent_g[-1] - recent_g[0]
                if abs(gamma_trend) > 200000:
                    base_score *= 0.7
        return max(0.0, min(1.0, base_score))

    def _compute_confidence(
        self,
        distance_pct: float,
        gex_magnitude: float,
        rejection_score: float,
        side: str,
        regime: str = "",
        depth_snapshot: Optional[Dict[str, Any]] = None,
        liq_score: float = 0.5,
        vol_score: float = 0.5,
        gex_calc: Any = None,
        price: float = 0.0,
    ) -> float:
        """
        Combine proximity, wall strength, rejection, liquidity validation,
        and vol support into confidence.

        Returns 0.0–1.0.
        """
        # Proximity component: closer = higher confidence (0.3–0.5)
        proximity_conf = 0.3 + 0.2 * (1 - distance_pct / WALL_PROXIMITY_PCT)

        # Wall strength component: higher GEX = higher confidence (0.2–0.3)
        # Normalize: 500k = low, 5M+ = high
        strength_conf = 0.2 + 0.3 * min(1.0, gex_magnitude / 5_000_000)

        # Rejection component: 0.2–0.3
        rejection_conf = 0.2 + 0.1 * rejection_score

        # Normalize each component to [0,1]
        norm_prox = (proximity_conf - 0.3) / (0.5 - 0.3) if 0.5 != 0.3 else 1.0
        norm_strength = (strength_conf - 0.2) / (0.5 - 0.2) if 0.5 != 0.2 else 1.0
        norm_reject = (rejection_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0

        # Regime component
        regime_bonus = 0.0
        if side == "call" and regime == "POSITIVE":
            regime_bonus = 0.15  # dealers sell rallies in positive regime
        elif side == "put" and regime == "NEGATIVE":
            regime_bonus = 0.15  # dealers buy dips in negative regime
        elif regime_bonus == 0:
            regime_bonus = -0.10  # misaligned regime — still fire but penalize
        norm_regime = regime_bonus / 0.15 if regime_bonus > 0 else 0.0

        # Liquidity validation component: 0.0–0.2 weight
        norm_liquidity = liq_score

        # Vol support component: 0.0–0.15 weight
        norm_vol_support = vol_score

        # Weighted average with depth-aware components
        confidence = (
            0.25 * norm_prox +
            0.21 * norm_strength +
            0.18 * norm_reject +
            0.15 * norm_regime +
            0.12 * norm_liquidity +
            0.09 * norm_vol_support
        )
        return min(MAX_CONFIDENCE, max(0.0, confidence))

    # ------------------------------------------------------------------
    # Depth-aware helpers
    # ------------------------------------------------------------------

    def _check_liquidity_validation(
        self, wall: Dict[str, Any], price: float, depth_snapshot: Optional[Dict[str, Any]]
    ) -> float:
        """Score how well liquidity validates a wall (0.0–1.0).

        A true wall bounce should show:
        - Increasing bid size (for call walls = resistance, MMs selling)
        - Increasing ask size (for put walls = support, MMs buying)
        - Tightening spread as price approaches the wall

        Returns 0.5 (neutral) if depth_snapshot is None.
        """
        if depth_snapshot is None:
            return 0.5
        wall_side = wall.get("side", "call")

        # Check spread behavior: tightening = support building
        spread_data = depth_snapshot.get("spread", {})
        current_spread = spread_data.get("current", 0)
        mean_spread = spread_data.get("mean", 0)

        spread_tightening = 0.0
        if mean_spread > 0 and current_spread < mean_spread:
            spread_tightening = min(1.0, (mean_spread - current_spread) / mean_spread)

        # Check depth on the relevant side
        bid_data = depth_snapshot.get("bid_size", {})
        ask_data = depth_snapshot.get("ask_size", {})

        current_bid = bid_data.get("current", 0)
        current_ask = ask_data.get("current", 0)
        mean_bid = bid_data.get("mean", 0)
        mean_ask = ask_data.get("mean", 0)

        # For call wall (resistance): need strong ASK side (MMs selling)
        # For put wall (support): need strong BID side (MMs buying)
        if wall_side == "call":
            depth_ratio = current_ask / mean_ask if mean_ask > 0 else 1.0
        else:
            depth_ratio = current_bid / mean_bid if mean_bid > 0 else 1.0

        # Weighted combination: 40% spread tightening, 60% depth ratio
        score = 0.4 * spread_tightening + 0.6 * min(1.0, depth_ratio)
        return round(score, 3)

    def _check_liquidity_decay(
        self, wall: Dict[str, Any], depth_snapshot: Optional[Dict[str, Any]]
    ) -> bool:
        """Returns True if decay is acceptable (wall intact), False if wall is being eaten.

        Returns True (intact) if depth_snapshot is None.
        """
        if depth_snapshot is None:
            return True
        wall_side = wall.get("side", "call")

        bid_data = depth_snapshot.get("bid_size", {})
        ask_data = depth_snapshot.get("ask_size", {})

        current_bid = bid_data.get("current", 0)
        current_ask = ask_data.get("current", 0)
        mean_bid = bid_data.get("mean", 0)
        mean_ask = ask_data.get("mean", 0)

        # For call wall: check ASK decay (MMs need to defend the wall)
        # For put wall: check BID decay
        if wall_side == "call":
            decay = 1.0 - (current_ask / mean_ask) if mean_ask > 0 else 0.0
        else:
            decay = 1.0 - (current_bid / mean_bid) if mean_bid > 0 else 0.0

        # If more than 40% of liquidity gone, wall is permeable
        return decay <= 0.40

    def _compute_vol_support_score(
        self, wall: Dict[str, Any], gex_calc: Any, price: float
    ) -> float:
        """Score wall strength based on IV at wall strike vs ATM IV.

        IV premium at wall = active hedging = strong wall.

        Returns 0.5 (neutral) if gex_calc is None.
        """
        if gex_calc is None:
            return 0.5
        wall_strike = wall.get("strike", 0)

        wall_iv = gex_calc.get_iv_by_strike(wall_strike)
        if wall_iv is None:
            return 0.5  # no IV data

        atm_strike = gex_calc.get_atm_strike(price)
        atm_iv = gex_calc.get_iv_by_strike(atm_strike) if atm_strike else None

        if atm_iv is None or atm_iv <= 0:
            return 0.5  # no ATM IV

        # IV premium at wall = active hedging = strong wall
        iv_premium = (wall_iv - atm_iv) / atm_iv

        # Score: premium > 0 means active hedging at wall
        score = 0.5 + 0.5 * min(1.0, max(-1.0, iv_premium))
        return round(score, 3)

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
