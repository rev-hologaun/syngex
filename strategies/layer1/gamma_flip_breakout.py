"""
strategies/layer1/gamma_flip_breakout.py — Gamma Flip Breakout

Trade the regime boundary defined by the gamma flip point.

Logic:
    - Above the flip: positive gamma regime → fade breakouts (mean reversion)
    - Below the flip: negative gamma regime → trade breakouts (momentum)
    - The flip point itself is the regime boundary

Entry:
    - Above flip: fade (SHORT on rallies, LONG on dips)
    - Below flip: breakout direction (LONG on breakouts, SHORT on breakdowns)

Exit:
    - Stop: other side of flip or 1.5× ATR (rolling range as proxy)
    - Target: next gamma wall (1:2.5 risk-reward)

Confidence factors:
    - Distance from flip (closer = higher confidence)
    - Regime strength (stronger gamma = higher confidence)
    - Wall proximity (closer wall = better target)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M

logger = logging.getLogger("Syngex.Strategies.GammaFlipBreakout")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FLIP_PROXIMITY_PCT = 0.025      # 2.5% — price must be within this of flip
STOP_OTHER_SIDE_PCT = 0.01      # 1% — stop on other side of flip
ATR_MULT = 1.5                   # 1.5× rolling range as ATR proxy
TARGET_RR = 2.5                  # 1:2.5 risk-reward minimum
MIN_CONFIDENCE = 0.35            # Minimum confidence to emit signal
MIN_GAMMA_STRENGTH = 100000      # Minimum |net_gamma| for regime confidence


class GammaFlipBreakout(BaseStrategy):
    """
    Trade the gamma flip regime boundary.

    Above flip: positive gamma → mean-reverting, fade breakouts.
    Below flip: negative gamma → momentum, trade breakouts.
    """

    strategy_id = "gamma_flip_breakout"
    layer = "layer1"
    _last_signal_time: Dict[str, float] = {}

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return flip breakout signals.

        Returns empty list when no flip point exists or conditions
        are not met.
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

        # Get the gamma flip point
        flip_strike = gex_calc.get_gamma_flip()
        if flip_strike is None:
            return []

        # Per-symbol cooldown (10 minutes)
        ts = data.get("timestamp", time.time())
        symbol = data.get("symbol", "")
        if symbol and symbol in self._last_signal_time:
            if ts - self._last_signal_time[symbol] < 600:
                return []

        signals: List[Signal] = []

        if underlying_price > flip_strike:
            # Above flip: positive gamma regime → fade breakouts
            sig = self._fade_above_flip(
                flip_strike, underlying_price, net_gamma, regime, rolling_data, gex_calc
            )
            if sig:
                signals.append(sig)
        elif underlying_price < flip_strike:
            # Below flip: negative gamma regime → breakout trades
            sig = self._breakout_below_flip(
                flip_strike, underlying_price, net_gamma, regime, rolling_data, gex_calc
            )
            if sig:
                signals.append(sig)

        if symbol:
            self._last_signal_time[symbol] = ts

        return signals

    # ------------------------------------------------------------------
    # Above flip: fade breakouts (positive gamma regime)
    # ------------------------------------------------------------------

    def _fade_above_flip(
        self,
        flip_strike: float,
        price: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
    ) -> Optional[Signal]:
        """
        Above flip: positive gamma → price tends to revert.
        SHORT on rallies toward flip, LONG on dips away from flip.
        """
        distance_pct = (price - flip_strike) / flip_strike
        if distance_pct > FLIP_PROXIMITY_PCT:
            # Too far from flip — not a fade setup
            return None

        # Get ATR proxy from rolling window
        atr = self._atrs(rolling_data, price)

        # Determine direction based on recent price action
        # If price is trending UP (z_score positive) → SHORT fade
        # If price is trending DOWN (z_score negative) → LONG fade
        price_window = rolling_data.get(KEY_PRICE_5M)
        zs = price_window.z_score if price_window else None

        if zs is not None and zs > 0.3:
            # Price is above its rolling mean → SHORT fade
            return self._short_fade(flip_strike, price, atr, net_gamma, regime, gex_calc)
        elif zs is not None and zs < -0.3:
            # Price is below its rolling mean → LONG fade
            return self._long_fade(flip_strike, price, atr, net_gamma, regime, gex_calc)

        return None

    def _short_fade(
        self,
        flip_strike: float,
        price: float,
        atr: float,
        net_gamma: float,
        regime: str,
        gex_calc: Any,
    ) -> Optional[Signal]:
        """SHORT fade: price rallied toward flip, expect rejection."""
        # Stop: above price or other side of flip, whichever is closer
        stop = max(price * 1.003, flip_strike * (1 + STOP_OTHER_SIDE_PCT))
        risk = stop - price
        if risk <= 0:
            return None

        # Target: next gamma wall below or 1:2.5 RR
        walls = gex_calc.get_gamma_walls(threshold=MIN_GAMMA_STRENGTH)
        below_walls = [w for w in walls if w["strike"] < price]
        if below_walls:
            nearest_below = max(w["strike"] for w in below_walls)
            target = max(price - (risk * TARGET_RR), nearest_below)
        else:
            target = price - (risk * TARGET_RR)

        confidence = self._fade_confidence(risk, price, net_gamma, regime, "short")
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Fade SHORT above flip {flip_strike:.2f}, price={price:.2f}, "
                   f"positive gamma regime, RR={abs(target - price) / risk:.1f}",
            metadata={
                "flip_strike": flip_strike,
                "distance_from_flip_pct": round((price - flip_strike) / price, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "atr": round(atr, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    def _long_fade(
        self,
        flip_strike: float,
        price: float,
        atr: float,
        net_gamma: float,
        regime: str,
        gex_calc: Any,
    ) -> Optional[Signal]:
        """LONG fade: price dipped away from flip, expect bounce back."""
        # Stop: below price or other side of flip
        stop = min(price * 0.997, flip_strike * (1 - STOP_OTHER_SIDE_PCT))
        risk = price - stop
        if risk <= 0:
            return None

        walls = gex_calc.get_gamma_walls(threshold=MIN_GAMMA_STRENGTH)
        above_walls = [w for w in walls if w["strike"] > price]
        if above_walls:
            nearest_above = min(w["strike"] for w in above_walls)
            target = min(price + (risk * TARGET_RR), nearest_above)
        else:
            target = price + (risk * TARGET_RR)

        confidence = self._fade_confidence(risk, price, net_gamma, regime, "long")
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Fade LONG above flip {flip_strike:.2f}, price={price:.2f}, "
                   f"positive gamma regime, RR={abs(target - price) / risk:.1f}",
            metadata={
                "flip_strike": flip_strike,
                "distance_from_flip_pct": round((price - flip_strike) / price, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "atr": round(atr, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    # ------------------------------------------------------------------
    # Below flip: breakout trades (negative gamma regime)
    # ------------------------------------------------------------------

    def _breakout_below_flip(
        self,
        flip_strike: float,
        price: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
    ) -> Optional[Signal]:
        """
        Below flip: negative gamma → momentum dominates.
        LONG on breakouts above flip, SHORT on breakdowns below flip.
        """
        distance_pct = (flip_strike - price) / flip_strike
        if distance_pct > FLIP_PROXIMITY_PCT:
            # Too far from flip — not a breakout setup
            return None

        atr = self._atrs(rolling_data, price)

        # Check price action for breakout direction
        price_window = rolling_data.get(KEY_PRICE_5M)
        zs = price_window.z_score if price_window else None

        if zs is not None and zs > 0.3:
            # Price trending up toward flip → LONG breakout
            return self._long_breakout(flip_strike, price, atr, net_gamma, regime, gex_calc)
        elif zs is not None and zs < -0.3:
            # Price trending down away from flip → SHORT breakout
            return self._short_breakout(flip_strike, price, atr, net_gamma, regime, gex_calc)

        return None

    def _long_breakout(
        self,
        flip_strike: float,
        price: float,
        atr: float,
        net_gamma: float,
        regime: str,
        gex_calc: Any,
    ) -> Optional[Signal]:
        """LONG breakout: price approaching flip from below, expect momentum."""
        # Stop: below flip or 1.5× ATR below entry
        stop = max(flip_strike * (1 - STOP_OTHER_SIDE_PCT), price * (1 - ATR_MULT * atr / price))
        risk = price - stop
        if risk <= 0:
            return None

        # Target: next gamma wall above or 1:2.5 RR
        walls = gex_calc.get_gamma_walls(threshold=MIN_GAMMA_STRENGTH)
        above_walls = [w for w in walls if w["strike"] > price]
        if above_walls:
            nearest_above = min(w["strike"] for w in above_walls)
            target = min(price + (risk * TARGET_RR), nearest_above)
        else:
            target = price + (risk * TARGET_RR)

        confidence = self._breakout_confidence(risk, price, net_gamma, regime, "long")
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Breakout LONG below flip {flip_strike:.2f}, price={price:.2f}, "
                   f"negative gamma regime, RR={abs(target - price) / risk:.1f}",
            metadata={
                "flip_strike": flip_strike,
                "distance_from_flip_pct": round((flip_strike - price) / price, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "atr": round(atr, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    def _short_breakout(
        self,
        flip_strike: float,
        price: float,
        atr: float,
        net_gamma: float,
        regime: str,
        gex_calc: Any,
    ) -> Optional[Signal]:
        """SHORT breakout: price moving away from flip downward."""
        stop = min(flip_strike * (1 + STOP_OTHER_SIDE_PCT), price * (1 + ATR_MULT * atr / price))
        risk = stop - price
        if risk <= 0:
            return None

        walls = gex_calc.get_gamma_walls(threshold=MIN_GAMMA_STRENGTH)
        below_walls = [w for w in walls if w["strike"] < price]
        if below_walls:
            nearest_below = max(w["strike"] for w in below_walls)
            target = max(price - (risk * TARGET_RR), nearest_below)
        else:
            target = price - (risk * TARGET_RR)

        confidence = self._breakout_confidence(risk, price, net_gamma, regime, "short")
        if confidence < MIN_CONFIDENCE:
            return None

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Breakout SHORT below flip {flip_strike:.2f}, price={price:.2f}, "
                   f"negative gamma regime, RR={abs(target - price) / risk:.1f}",
            metadata={
                "flip_strike": flip_strike,
                "distance_from_flip_pct": round((flip_strike - price) / price, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "atr": round(atr, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
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
    ) -> float:
        """Confidence for fade signals (above flip)."""
        # Risk/reward: tighter risk = higher confidence (0.2–0.3)
        rr = TARGET_RR
        risk_conf = 0.2 + 0.1 * min(1.0, 0.005 / (risk / price))

        # Gamma strength: stronger positive gamma = better fade (0.2–0.3)
        gamma_conf = 0.2 + 0.3 * min(1.0, net_gamma / 1_000_000)

        # Regime alignment (0.2–0.3)
        regime_conf = 0.3 if regime == "POSITIVE" else 0.15

        # Wall proximity bonus (0.1–0.2)
        wall_conf = 0.1 + 0.1 * min(1.0, abs(net_gamma) / 500_000)

        # Normalize each component to [0,1] and average
        norm_risk = (risk_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0
        norm_gamma = (gamma_conf - 0.2) / (0.5 - 0.2) if 0.5 != 0.2 else 1.0
        norm_regime = (regime_conf - 0.15) / (0.3 - 0.15) if 0.3 != 0.15 else 1.0
        norm_wall = (wall_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        return min(1.0, max(0.0, (norm_risk + norm_gamma + norm_regime + norm_wall) / 4.0))

    def _breakout_confidence(
        self,
        risk: float,
        price: float,
        net_gamma: float,
        regime: str,
        side: str,
    ) -> float:
        """Confidence for breakout signals (below flip)."""
        # Risk/reward: wider risk = higher confidence for breakouts (0.2–0.3)
        risk_conf = 0.2 + 0.1 * min(1.0, (risk / price) / 0.01)

        # Gamma strength: stronger negative gamma = better breakout (0.2–0.3)
        gamma_conf = 0.2 + 0.3 * min(1.0, abs(net_gamma) / 1_000_000)

        # Regime alignment (0.2–0.3)
        regime_conf = 0.3 if regime == "NEGATIVE" else 0.15

        # Wall proximity bonus (0.1–0.2)
        wall_conf = 0.1 + 0.1 * min(1.0, abs(net_gamma) / 500_000)

        # Normalize each component to [0,1] and average
        norm_risk = (risk_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0
        norm_gamma = (gamma_conf - 0.2) / (0.5 - 0.2) if 0.5 != 0.2 else 1.0
        norm_regime = (regime_conf - 0.15) / (0.3 - 0.15) if 0.3 != 0.15 else 1.0
        norm_wall = (wall_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        return min(1.0, max(0.0, (norm_risk + norm_gamma + norm_regime + norm_wall) / 4.0))
