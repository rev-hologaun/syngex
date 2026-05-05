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
from strategies.rolling_keys import (
    KEY_PRICE_5M,
    KEY_VOLUME_DOWN_5M,
    KEY_VOLUME_UP_5M,
)

logger = logging.getLogger("Syngex.Strategies.GammaSqueeze")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIN_ATR_PCT = 0.003           # 0.3% — max range for pin detection
WALL_PROXIMITY_PCT = 0.003    # 0.3% — price must be near wall for breakout
VOLUME_SURGE_MULT = 1.5       # 1.5× average volume = confirmation
MIN_WALL_GEX = 500000         # Minimum |GEX| for wall consideration
MIN_CONFIDENCE = 0.25         # Minimum confidence to emit signal
TARGET_RISK_MULT = 2.0        # 2× risk for squeeze targets
MIN_MASSIVE_WALL_GEX = 5_000_000  # Fallback threshold for POSITIVE regime filter


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

        # Check for wall breakout — LONG (call wall)
        long_breakout = self._detect_breakout(
            underlying_price, net_gamma, rolling_data, gex_calc, direction=Direction.LONG
        )
        if long_breakout:
            # Regime filter for LONG
            if not self._regime_passes(regime, long_breakout["wall_gex"], gex_calc):
                return []
            sig = self._enter_squeeze(long_breakout, underlying_price, net_gamma, regime, rolling_data)
            if sig:
                signals.append(sig)

        # Check for wall breakout — SHORT (put wall)
        short_breakout = self._detect_breakout(
            underlying_price, net_gamma, rolling_data, gex_calc, direction=Direction.SHORT
        )
        if short_breakout:
            # Regime filter for SHORT
            if not self._regime_passes(regime, short_breakout["wall_gex"], gex_calc):
                return []
            sig = self._enter_squeeze(short_breakout, underlying_price, net_gamma, regime, rolling_data)
            if sig:
                signals.append(sig)

        if is_pin:
            # Pin detected but no breakout yet — no signal (wait for breakout)
            pass

        return signals

    def _regime_passes(self, regime: str, wall_gex: float, gex_calc: Any) -> bool:
        """
        Regime-aware filter for squeeze signals.

        NEGATIVE regime: fire freely — squeezes amplify in negative gamma.
        POSITIVE regime: only fire if wall GEX is MASSIVE (>95th percentile).
        Unknown/empty: fire freely (conservative default).
        """
        if not regime:
            return True  # Unknown → fire freely

        if regime == "NEGATIVE":
            return True  # Fire freely in negative gamma

        if regime == "POSITIVE":
            # Get all walls and compute 95th percentile
            walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
            if walls:
                gex_values = [abs(w["gex"]) for w in walls]
                gex_values.sort()
                p95_idx = max(0, int(len(gex_values) * 0.95) - 1)
                p95_gex = gex_values[p95_idx]
                if abs(wall_gex) >= p95_gex:
                    return True  # Wall is massive enough
            # Fallback: use fixed threshold
            return abs(wall_gex) >= MIN_MASSIVE_WALL_GEX

        # Unknown regime → fire freely
        return True

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
        price_window = rolling_data.get(KEY_PRICE_5M)
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
        direction: Optional[Direction] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Detect breakout through a gamma wall.

        Args:
            direction: If set, only check for that direction.
                       None = check both LONG and SHORT.

        Returns dict with breakout info or None.
        """
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
        if not walls:
            return None

        price_window = rolling_data.get(KEY_PRICE_5M)

        if direction is None or direction == Direction.LONG:
            result = self._evaluate_long_squeeze(
                price, rolling_data, gex_calc, price_window
            )
            if result:
                return result

        if direction is None or direction == Direction.SHORT:
            result = self._evaluate_short_squeeze(
                price, rolling_data, gex_calc, price_window
            )
            if result:
                return result

        return None

    def _evaluate_long_squeeze(
        self,
        price: float,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        price_window: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate LONG squeeze: breakout above call wall.

        Conditions:
            1. Price near a call wall (WALL_PROXIMITY_PCT)
            2. Price sustained beyond the wall (last 2 ticks above)
            3. Volume surge confirmation
        """
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
        if not walls:
            return None

        for wall in walls:
            if wall["side"] != "call":
                continue

            wall_strike = wall["strike"]
            wall_gex = wall["gex"]

            # Price must be within WALL_PROXIMITY_PCT of wall
            distance_pct = abs(price - wall_strike) / price
            if distance_pct > WALL_PROXIMITY_PCT:
                continue

            # Sustain filter: price must be > wall_strike for last 2 data points
            if not self._is_sustained(price_window, wall_strike, above=True):
                continue

            # Volume surge confirmation
            vol_window = rolling_data.get(KEY_VOLUME_UP_5M)
            if vol_window is not None:
                current_vol = vol_window.latest
                rolling_avg = vol_window.mean
                if current_vol is not None and rolling_avg is not None and rolling_avg > 0:
                    if current_vol / rolling_avg < VOLUME_SURGE_MULT:
                        continue  # insufficient volume surge

            return {
                "direction": Direction.LONG,
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_side": "call",
                "type": "call_wall_breakout",
            }

        return None

    def _evaluate_short_squeeze(
        self,
        price: float,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        price_window: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate SHORT squeeze: breakdown below put wall.

        Mirror of _evaluate_long_squeeze with direction reversed.

        Conditions:
            1. Price near a put wall (WALL_PROXIMITY_PCT)
            2. Price sustained below the wall (last 2 ticks below)
            3. Volume surge confirmation
        """
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
        if not walls:
            return None

        for wall in walls:
            if wall["side"] != "put":
                continue

            wall_strike = wall["strike"]
            wall_gex = wall["gex"]

            # Price must be within WALL_PROXIMITY_PCT of wall
            distance_pct = abs(price - wall_strike) / price
            if distance_pct > WALL_PROXIMITY_PCT:
                continue

            # Sustain filter: price must be < wall_strike for last 2 data points
            if not self._is_sustained(price_window, wall_strike, above=False):
                continue

            # Volume surge confirmation for SHORT
            vol_window = rolling_data.get(KEY_VOLUME_DOWN_5M)
            if vol_window is not None:
                current_vol = vol_window.latest
                rolling_avg = vol_window.mean
                if current_vol is not None and rolling_avg is not None and rolling_avg > 0:
                    if current_vol / rolling_avg < VOLUME_SURGE_MULT:
                        continue  # insufficient volume surge

            return {
                "direction": Direction.SHORT,
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_side": "put",
                "type": "put_wall_breakout",
            }

        return None

    def _is_sustained(
        self,
        price_window: Any,
        wall_strike: float,
        above: bool,
    ) -> bool:
        """
        Check if price has stayed beyond the wall for 2+ consecutive ticks.

        Args:
            price_window: Rolling price window with prices list.
            wall_strike: The gamma wall strike to check against.
            above: True = check price > wall_strike (LONG),
                   False = check price < wall_strike (SHORT).

        Returns True if sustained, False if just crossed (only 1 tick beyond).
        """
        if price_window is None:
            return True  # No price data — don't block

        prices = getattr(price_window, "prices", None)
        if prices is None:
            return True  # No prices list — don't block

        # Need at least 2 data points to check sustain
        if len(prices) < 2:
            return True

        # Check last 2 data points
        if above:
            # LONG: last 2 prices must be > wall_strike
            return prices[-1] > wall_strike and prices[-2] > wall_strike
        else:
            # SHORT: last 2 prices must be < wall_strike
            return prices[-1] < wall_strike and prices[-2] < wall_strike

    # ------------------------------------------------------------------
    # Enter Squeeze
    # ------------------------------------------------------------------

    def _enter_squeeze(
        self,
        breakout: Dict[str, Any],
        price: float,
        net_gamma: float,
        regime: str,
        rolling_data: Optional[Dict[str, Any]] = None,
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

        # Net gamma direction alignment
        if direction == Direction.LONG and net_gamma <= 0:
            return None  # Long signal but dealers not buying
        if direction == Direction.SHORT and net_gamma >= 0:
            return None  # Short signal but dealers not selling

        if direction == Direction.LONG:
            stop = price * 0.99  # 1% below entry
            risk = abs(price - stop)
            target = price + (risk * TARGET_RISK_MULT)
        else:
            stop = price * 1.01  # 1% above entry
            risk = abs(price - stop)
            target = price - (risk * TARGET_RISK_MULT)

        if risk <= 0:
            return None

        # Confidence: wall strength + net gamma + volume confirmation
        confidence = self._squeeze_confidence(
            wall_gex, net_gamma, price, risk, breakout
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Get trend info
        price_window = rolling_data.get(KEY_PRICE_5M) if rolling_data else None

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
                "trend": price_window.trend if price_window else "UNKNOWN",
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

        # Normalize each component to [0,1] and average
        norm_wall = (wall_conf - 0.2) / (0.35 - 0.2) if 0.35 != 0.2 else 1.0
        norm_gamma = (gamma_conf - 0.2) / (0.35 - 0.2) if 0.35 != 0.2 else 1.0
        norm_risk = (risk_conf - 0.15) / (0.25 - 0.15) if 0.25 != 0.15 else 1.0
        norm_vol = (volume_conf - 0.1) / (0.15 - 0.1) if 0.15 != 0.1 else 1.0
        return min(1.0, max(0.0, (norm_wall + norm_gamma + norm_risk + norm_vol) / 4.0))
