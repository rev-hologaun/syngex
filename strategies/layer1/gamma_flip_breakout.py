"""
strategies/layer1/gamma_flip_breakout.py — Gamma Flip Breakout (v2: Regime-Boundary)

Trade the regime boundary defined by the gamma flip point.

Logic:
    - Above the flip zone: positive gamma regime → fade breakouts (mean reversion)
    - Below the flip zone: negative gamma regime → trade breakouts (momentum)
    - Inside the flip zone: transition zone (higher confirmation required)
    - The flip point itself is the regime boundary

Entry:
    - Above flip zone: fade (SHORT on rallies, LONG on dips)
    - Below flip zone: breakout direction (LONG on breakouts, SHORT on breakdowns)

Exit:
    - Stop: other side of flip zone or regime-adjusted ATR
    - Target: next gamma wall (1:2.5 risk-reward)

Confidence factors:
    - Distance from flip zone (closer = higher confidence)
    - Regime strength (stronger gamma = higher confidence)
    - Wall proximity (closer wall = better target)
    - Regime confirmation (delta density + IV skew)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_IV_SKEW_5M

logger = logging.getLogger("Syngex.Strategies.GammaFlipBreakout")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FLIP_PROXIMITY_PCT = 0.025      # 2.5% — price must be within this of flip
FLIP_ZONE_PCT = 0.015           # 1.5% — the transition zone around flip
STOP_OTHER_SIDE_PCT = 0.01      # 1% — stop on other side of flip
ATR_MULT = 1.5                   # 1.5× rolling range as ATR proxy
TARGET_RR = 2.5                  # 1:2.5 risk-reward minimum
MIN_CONFIDENCE = 0.65            # Minimum confidence to emit signal
MIN_GAMMA_STRENGTH = 100000      # Minimum |net_gamma| for regime confidence

# Regime-adjusted stop multipliers
NEGATIVE_GAMMA_STOP_MULT = 2.5   # Wider stops in negative gamma (more noise)
POSITIVE_GAMMA_STOP_MULT = 0.75  # Tighter stops in positive gamma (less noise)


class GammaFlipBreakout(BaseStrategy):
    """
    Trade the gamma flip regime boundary.

    Above flip: positive gamma → mean-reverting, fade breakouts.
    Below flip: negative gamma → momentum, trade breakouts.
    """

    strategy_id = "gamma_flip_breakout"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return flip breakout signals.

        Uses the gamma flip point as the regime boundary. If no flip
        point exists (e.g. pure positive/negative regime), falls back
        to the ATM strike as a regime boundary proxy.

        Returns empty list when no flip point or ATM strike exists,
        or when other conditions are not met.
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

        # Require sufficient gamma strength for meaningful regime
        if abs(net_gamma) < 200000:
            return []

        # Get the flip zone (v2: zone instead of single point)
        flip_lower, flip_upper, flip_mid = self._get_flip_zone(gex_calc, underlying_price)
        if flip_mid is None:
            return []  # No data at all

        # Regime confirmation score (delta density + IV skew)
        confirmation = self._check_regime_confirmation(
            underlying_price, flip_mid, net_gamma, gex_calc, rolling_data
        )

        signals: List[Signal] = []

        if underlying_price > flip_upper:
            # Positive gamma regime → fade breakouts
            sig = self._fade_above_flip(
                flip_lower, flip_upper, flip_mid,
                underlying_price, net_gamma, regime, rolling_data, gex_calc,
                confirmation,
            )
            if sig:
                signals.append(sig)
        elif underlying_price < flip_lower:
            # Negative gamma regime → breakout trades
            sig = self._breakout_below_flip(
                flip_lower, flip_upper, flip_mid,
                underlying_price, net_gamma, regime, rolling_data, gex_calc,
                confirmation,
            )
            if sig:
                signals.append(sig)
        else:
            # Inside flip zone — transition zone, higher bar
            # Still allow trades but with stricter confirmation
            if confirmation < 0.4:
                return []
            # Use same logic but with tighter proximity check
            if underlying_price > flip_mid:
                sig = self._fade_above_flip(
                    flip_lower, flip_upper, flip_mid,
                    underlying_price, net_gamma, regime, rolling_data, gex_calc,
                    confirmation,
                )
            else:
                sig = self._breakout_below_flip(
                    flip_lower, flip_upper, flip_mid,
                    underlying_price, net_gamma, regime, rolling_data, gex_calc,
                    confirmation,
                )
            if sig:
                signals.append(sig)

        return signals

    # ------------------------------------------------------------------
    # New v2: Flip Zone
    # ------------------------------------------------------------------

    def _get_flip_zone(self, gex_calc: Any, price: float) -> Tuple[float, float, float]:
        """Return (flip_lower, flip_upper, flip_mid).

        flip_mid = gamma flip or ATM fallback.
        flip_lower/upper = mid ± FLIP_ZONE_PCT.
        Returns (None, None, None) if no data available.
        """
        flip_mid = gex_calc.get_gamma_flip()
        if flip_mid is None:
            flip_mid = gex_calc.get_atm_strike(price)
        if flip_mid is None or flip_mid <= 0:
            return None, None, None

        zone_half = flip_mid * FLIP_ZONE_PCT
        return (flip_mid - zone_half, flip_mid + zone_half, flip_mid)

    # ------------------------------------------------------------------
    # New v2: Regime Confirmation
    # ------------------------------------------------------------------

    def _check_regime_confirmation(
        self,
        price: float,
        flip_mid: float,
        net_gamma: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
    ) -> float:
        """Score how strongly the regime change is confirmed (0.0–1.0).

        Components:
            - Delta density at flip strike (0.4 weight)
            - IV skew from rolling data (0.3 weight)
            - Net gamma magnitude (0.3 weight)
        """
        # 1. Delta density at flip strike (structural change)
        flip_density = 0.0
        try:
            flip_density = gex_calc.get_delta_density(flip_mid)
        except Exception:
            flip_density = 0.0
        density_score = min(1.0, flip_density / 2.0)  # 2.0+ density = max

        # 2. IV skew from rolling data (market pricing in regime shift)
        iv_skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        skew_score = 0.5  # neutral
        if iv_skew_window and iv_skew_window.latest is not None:
            skew = iv_skew_window.latest
            if net_gamma > 0:
                # Positive gamma regime: positive skew confirms
                skew_score = 0.5 + 0.3 * min(1.0, skew)
            else:
                # Negative gamma regime: negative skew confirms
                skew_score = 0.5 + 0.3 * min(1.0, -skew)

        # 3. Net gamma magnitude (regime strength)
        gamma_score = min(1.0, abs(net_gamma) / 1_000_000)

        return round(0.4 * density_score + 0.3 * skew_score + 0.3 * gamma_score, 3)

    # ------------------------------------------------------------------
    # New v2: Liquidity-Weighted Target
    # ------------------------------------------------------------------

    def _find_target_wall(self, gex_calc: Any, price: float, direction: str) -> Optional[Dict[str, Any]]:
        """Find next high-conviction wall in target direction.

        Uses get_wall_classifications() and filters to only "wall" type,
        excluding ghosts and magnets.

        Args:
            direction: "long" (above price) or "short" (below price)
        """
        try:
            walls = gex_calc.get_wall_classifications(threshold=MIN_GAMMA_STRENGTH)
        except Exception:
            return None

        # Filter: only "wall" classification, not ghost
        valid = [
            w for w in walls
            if w.get("classification") == "wall"
            and not w.get("is_ghost", False)
        ]

        if direction == "long":
            above = [w for w in valid if w["strike"] > price]
            return min(above, key=lambda w: w["strike"]) if above else None
        else:
            below = [w for w in valid if w["strike"] < price]
            return max(below, key=lambda w: w["strike"]) if below else None

    # ------------------------------------------------------------------
    # Above flip: fade breakouts (positive gamma regime)
    # ------------------------------------------------------------------

    def _fade_above_flip(
        self,
        flip_lower: float,
        flip_upper: float,
        flip_mid: float,
        price: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        confirmation_score: float = 0.5,
    ) -> Optional[Signal]:
        """
        Above flip: positive gamma → price tends to revert.
        SHORT on rallies toward flip, LONG on dips away from flip.

        Uses POSITIVE_GAMMA_STOP_MULT (0.75) for tighter stops.
        """
        distance_pct = (price - flip_upper) / flip_upper
        if distance_pct > FLIP_PROXIMITY_PCT:
            # Too far from flip zone — not a fade setup
            return None

        # Get ATR proxy from rolling window
        atr = self._atrs(rolling_data, price)

        # Determine direction based on recent price action
        price_window = rolling_data.get(KEY_PRICE_5M)
        zs = price_window.z_score if price_window else None

        if zs is not None and zs > 0.3:
            # Price is above its rolling mean → SHORT fade
            return self._short_fade(
                flip_mid, price, atr, net_gamma, regime,
                rolling_data, gex_calc, confirmation_score,
            )
        elif zs is not None and zs < -0.3:
            # Price is below its rolling mean → LONG fade
            return self._long_fade(
                flip_mid, price, atr, net_gamma, regime,
                rolling_data, gex_calc, confirmation_score,
            )

        return None

    def _short_fade(
        self,
        flip_mid: float,
        price: float,
        atr: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        confirmation_score: float = 0.5,
    ) -> Optional[Signal]:
        """SHORT fade: price rallied toward flip, expect rejection."""
        # Stop: above price or other side of flip zone, whichever is closer
        stop_mult = POSITIVE_GAMMA_STOP_MULT  # 0.75 — tighter in positive gamma
        stop = max(price * (1 + stop_mult * STOP_OTHER_SIDE_PCT), flip_mid * (1 + STOP_OTHER_SIDE_PCT))
        risk = stop - price
        if risk <= 0:
            return None

        # Target: next gamma wall below or 1:2.5 RR
        wall = self._find_target_wall(gex_calc, price, "short")
        if wall:
            target = max(price - (risk * TARGET_RR), wall["strike"])
        else:
            target = price - (risk * TARGET_RR)

        confidence = self._fade_confidence(
            risk, price, net_gamma, regime, "short",
            flip_mid, confirmation_score,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Fade SHORT above flip zone {flip_mid:.2f}, price={price:.2f}, "
                   f"positive gamma regime, RR={abs(target - price) / risk:.1f}",
            metadata={
                "flip_mid": flip_mid,
                "flip_zone_lower": round(flip_mid * (1 - FLIP_ZONE_PCT), 2),
                "flip_zone_upper": round(flip_mid * (1 + FLIP_ZONE_PCT), 2),
                "distance_from_flip_pct": round((price - flip_mid) / price, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "atr": round(atr, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
                "confirmation_score": round(confirmation_score, 3),
                "trend": price_window.trend if price_window else "UNKNOWN",
            },
        )

    def _long_fade(
        self,
        flip_mid: float,
        price: float,
        atr: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        confirmation_score: float = 0.5,
    ) -> Optional[Signal]:
        """LONG fade: price dipped away from flip, expect bounce back."""
        # Stop: below price or other side of flip zone
        stop_mult = POSITIVE_GAMMA_STOP_MULT  # 0.75 — tighter in positive gamma
        stop = min(price * (1 - stop_mult * STOP_OTHER_SIDE_PCT), flip_mid * (1 - STOP_OTHER_SIDE_PCT))
        risk = price - stop
        if risk <= 0:
            return None

        wall = self._find_target_wall(gex_calc, price, "long")
        if wall:
            target = min(price + (risk * TARGET_RR), wall["strike"])
        else:
            target = price + (risk * TARGET_RR)

        confidence = self._fade_confidence(
            risk, price, net_gamma, regime, "long",
            flip_mid, confirmation_score,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Fade LONG above flip zone {flip_mid:.2f}, price={price:.2f}, "
                   f"positive gamma regime, RR={abs(target - price) / risk:.1f}",
            metadata={
                "flip_mid": flip_mid,
                "flip_zone_lower": round(flip_mid * (1 - FLIP_ZONE_PCT), 2),
                "flip_zone_upper": round(flip_mid * (1 + FLIP_ZONE_PCT), 2),
                "distance_from_flip_pct": round((price - flip_mid) / price, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "atr": round(atr, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
                "confirmation_score": round(confirmation_score, 3),
                "trend": price_window.trend if price_window else "UNKNOWN",
            },
        )

    # ------------------------------------------------------------------
    # Below flip: breakout trades (negative gamma regime)
    # ------------------------------------------------------------------

    def _breakout_below_flip(
        self,
        flip_lower: float,
        flip_upper: float,
        flip_mid: float,
        price: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        confirmation_score: float = 0.5,
    ) -> Optional[Signal]:
        """
        Below flip: negative gamma → momentum dominates.
        LONG on breakouts above flip, SHORT on breakdowns below flip.

        Uses NEGATIVE_GAMMA_STOP_MULT (2.5) for wider stops.
        """
        distance_pct = (flip_lower - price) / flip_lower
        if distance_pct > FLIP_PROXIMITY_PCT:
            # Too far from flip zone — not a breakout setup
            return None

        atr = self._atrs(rolling_data, price)

        # Check price action for breakout direction
        price_window = rolling_data.get(KEY_PRICE_5M)
        zs = price_window.z_score if price_window else None

        if zs is not None and zs > 0.3:
            # Price trending up toward flip → LONG breakout
            return self._long_breakout(
                flip_mid, price, atr, net_gamma, regime,
                rolling_data, gex_calc, confirmation_score,
            )
        elif zs is not None and zs < -0.3:
            # Price trending down away from flip → SHORT breakout
            return self._short_breakout(
                flip_mid, price, atr, net_gamma, regime,
                rolling_data, gex_calc, confirmation_score,
            )

        return None

    def _long_breakout(
        self,
        flip_mid: float,
        price: float,
        atr: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        confirmation_score: float = 0.5,
    ) -> Optional[Signal]:
        """LONG breakout: price approaching flip from below, expect momentum."""
        # Stop: below flip zone or 1.5× ATR below entry
        stop_mult = NEGATIVE_GAMMA_STOP_MULT  # 2.5 — wider in negative gamma
        stop = max(flip_mid * (1 - STOP_OTHER_SIDE_PCT), price * (1 - ATR_MULT * atr / price))
        risk = price - stop
        if risk <= 0:
            return None

        # Target: next gamma wall above or 1:2.5 RR
        wall = self._find_target_wall(gex_calc, price, "long")
        if wall:
            target = min(price + (risk * TARGET_RR), wall["strike"])
        else:
            target = price + (risk * TARGET_RR)

        confidence = self._breakout_confidence(
            risk, price, net_gamma, regime, "long",
            flip_mid, confirmation_score,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Breakout LONG below flip zone {flip_mid:.2f}, price={price:.2f}, "
                   f"negative gamma regime, RR={abs(target - price) / risk:.1f}",
            metadata={
                "flip_mid": flip_mid,
                "flip_zone_lower": round(flip_mid * (1 - FLIP_ZONE_PCT), 2),
                "flip_zone_upper": round(flip_mid * (1 + FLIP_ZONE_PCT), 2),
                "distance_from_flip_pct": round((flip_mid - price) / price, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "atr": round(atr, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
                "confirmation_score": round(confirmation_score, 3),
                "trend": price_window.trend if price_window else "UNKNOWN",
            },
        )

    def _short_breakout(
        self,
        flip_mid: float,
        price: float,
        atr: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        confirmation_score: float = 0.5,
    ) -> Optional[Signal]:
        """SHORT breakout: price moving away from flip downward."""
        # Stop: above flip zone or 1.5× ATR above entry
        stop_mult = NEGATIVE_GAMMA_STOP_MULT  # 2.5 — wider in negative gamma
        stop = min(flip_mid * (1 + STOP_OTHER_SIDE_PCT), price * (1 + ATR_MULT * atr / price))
        risk = stop - price
        if risk <= 0:
            return None

        wall = self._find_target_wall(gex_calc, price, "short")
        if wall:
            target = max(price - (risk * TARGET_RR), wall["strike"])
        else:
            target = price - (risk * TARGET_RR)

        confidence = self._breakout_confidence(
            risk, price, net_gamma, regime, "short",
            flip_mid, confirmation_score,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Breakout SHORT below flip zone {flip_mid:.2f}, price={price:.2f}, "
                   f"negative gamma regime, RR={abs(target - price) / risk:.1f}",
            metadata={
                "flip_mid": flip_mid,
                "flip_zone_lower": round(flip_mid * (1 - FLIP_ZONE_PCT), 2),
                "flip_zone_upper": round(flip_mid * (1 + FLIP_ZONE_PCT), 2),
                "distance_from_flip_pct": round((flip_mid - price) / price, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "atr": round(atr, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
                "confirmation_score": round(confirmation_score, 3),
                "trend": price_window.trend if price_window else "UNKNOWN",
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _atrs(self, rolling_data: Dict[str, Any], price: float) -> float:
        """
        Estimate ATR from rolling window range.

        Returns ATR as a dollar amount.
        """
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window and price_window.range is not None:
            return price_window.range
        # Fallback: 0.5% of price
        return price * 0.005

    def _fade_confidence(
        self,
        risk: float,
        price: float,
        net_gamma: float,
        regime: str,
        side: str,
        flip_mid: float = 0.0,
        confirmation_score: float = 0.5,
    ) -> float:
        """Confidence for fade signals (above flip).

        v2 additions:
            - confirmation_score component (0.1–0.2 weight)
            - distance-from-flip-zone component (0.05–0.15 weight)
        """
        # 1. Risk/reward: tighter risk = higher confidence (0.2–0.3)
        risk_conf = 0.2 + 0.1 * min(1.0, 0.005 / (risk / price))

        # 2. Gamma strength: stronger positive gamma = better fade (0.2–0.3)
        gamma_conf = 0.2 + 0.3 * min(1.0, net_gamma / 1_000_000)

        # 3. Regime alignment (0.2–0.3)
        regime_conf = 0.3 if regime == "POSITIVE" else 0.15

        # 4. Wall proximity bonus (0.1–0.2)
        wall_conf = 0.1 + 0.1 * min(1.0, abs(net_gamma) / 500_000)

        # 5. NEW: Regime confirmation (0.1–0.2)
        confirmation_conf = 0.1 + 0.1 * confirmation_score

        # 6. NEW: Distance from flip zone (0.05–0.15)
        if flip_mid > 0 and price > 0:
            distance_pct = abs(price - flip_mid) / price
            dist_conf = 0.05 + 0.1 * min(1.0, 1.0 - (distance_pct / FLIP_ZONE_PCT))
        else:
            dist_conf = 0.05  # neutral if no flip_mid

        # Normalize each component to [0,1] and average
        norm_risk = (risk_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0
        norm_gamma = (gamma_conf - 0.2) / (0.5 - 0.2) if 0.5 != 0.2 else 1.0
        norm_regime = (regime_conf - 0.15) / (0.3 - 0.15) if 0.3 != 0.15 else 1.0
        norm_wall = (wall_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        norm_confirm = (confirmation_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        norm_dist = (dist_conf - 0.05) / (0.15 - 0.05) if 0.15 != 0.05 else 1.0

        return min(1.0, max(0.0, (norm_risk + norm_gamma + norm_regime + norm_wall + norm_confirm + norm_dist) / 6.0))

    def _breakout_confidence(
        self,
        risk: float,
        price: float,
        net_gamma: float,
        regime: str,
        side: str,
        flip_mid: float = 0.0,
        confirmation_score: float = 0.5,
    ) -> float:
        """Confidence for breakout signals (below flip).

        v2 additions:
            - confirmation_score component (0.1–0.2 weight)
            - distance-from-flip-zone component (0.05–0.15 weight)
        """
        # 1. Risk/reward: wider risk = higher confidence for breakouts (0.2–0.3)
        risk_conf = 0.2 + 0.1 * min(1.0, (risk / price) / 0.01)

        # 2. Gamma strength: stronger negative gamma = better breakout (0.2–0.3)
        gamma_conf = 0.2 + 0.3 * min(1.0, abs(net_gamma) / 1_000_000)

        # 3. Regime alignment (0.2–0.3)
        regime_conf = 0.3 if regime == "NEGATIVE" else 0.15

        # 4. Wall proximity bonus (0.1–0.2)
        wall_conf = 0.1 + 0.1 * min(1.0, abs(net_gamma) / 500_000)

        # 5. NEW: Regime confirmation (0.1–0.2)
        confirmation_conf = 0.1 + 0.1 * confirmation_score

        # 6. NEW: Distance from flip zone (0.05–0.15)
        if flip_mid > 0 and price > 0:
            distance_pct = abs(price - flip_mid) / price
            dist_conf = 0.05 + 0.1 * min(1.0, 1.0 - (distance_pct / FLIP_ZONE_PCT))
        else:
            dist_conf = 0.05  # neutral if no flip_mid

        # Normalize each component to [0,1] and average
        norm_risk = (risk_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0
        norm_gamma = (gamma_conf - 0.2) / (0.5 - 0.2) if 0.5 != 0.2 else 1.0
        norm_regime = (regime_conf - 0.15) / (0.3 - 0.15) if 0.3 != 0.15 else 1.0
        norm_wall = (wall_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        norm_confirm = (confirmation_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        norm_dist = (dist_conf - 0.05) / (0.15 - 0.05) if 0.15 != 0.05 else 1.0

        return min(1.0, max(0.0, (norm_risk + norm_gamma + norm_regime + norm_wall + norm_confirm + norm_dist) / 6.0))
