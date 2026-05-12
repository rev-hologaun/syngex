"""
strategies/layer1/gamma_squeeze.py — Gamma Squeeze / Wall-Breaker v2 (Squeeze-Force)

Pin detection + breakout through gamma wall with depth-aware liquidity vacuum detection.

Logic:
    1. Pin detection: narrow range (ATR < 0.3%), positive net gamma,
       price trapped between gamma walls with high delta density
    2. Breakout candle: price closes beyond a gamma wall with volume
       confirmation + liquidity vacuum (depth collapse)
    3. Enter squeeze in breakout direction — dealer hedging accelerates
       the move as net gamma flips

Entry:
    - LONG squeeze: breakout above call wall with volume + ask_size collapse
    - SHORT squeeze: breakdown below put wall with volume + bid_size collapse

Exit:
    - Stop: liquidity-aware placement behind the nearest wall
    - Target: 2× risk (squeezes run hard)

Confidence factors:
    - Pin duration (longer pin = higher confidence)
    - Wall strength (IV premium + GEX magnitude + classification)
    - Liquidity vacuum (depth collapse = acceleration potential)
    - Net gamma at breakout (positive = acceleration)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.volume_filter import VolumeFilter
from strategies.rolling_keys import (
    KEY_PRICE_5M,
    KEY_VOLUME_DOWN_5M,
    KEY_VOLUME_UP_5M,
    KEY_DEPTH_BID_SIZE_ROLLING,
    KEY_DEPTH_ASK_SIZE_ROLLING,
)

logger = logging.getLogger("Syngex.Strategies.GammaSqueeze")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIN_MAX_RANGE_PCT = 0.003     # 0.3% — max rolling range for pin detection
WALL_PROXIMITY_PCT = 0.003    # 0.3% — price must be near wall for breakout
VOLUME_SURGE_MULT = 1.5       # 1.5× average volume = confirmation
MIN_WALL_GEX = 500000         # Minimum |GEX| for wall consideration
MIN_CONFIDENCE = 0.50         # was 0.25
TARGET_RISK_MULT = 2.0        # 2× risk for squeeze targets
MIN_MASSIVE_WALL_GEX = 5_000_000  # Fallback threshold for POSITIVE regime filter


class GammaSqueeze(BaseStrategy):
    """
    Pin detection + wall-breakout squeeze strategy (v2 Squeeze-Force).

    When price is pinned between walls with positive gamma,
    a breakout through a wall triggers dealer hedging acceleration.
    Enhanced with depth-aware liquidity vacuum detection,
    IV-based wall strength scoring, and delta density pin validation.
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

        # Extract depth snapshot for liquidity vacuum detection
        depth_snapshot = data.get("depth_snapshot")

        # Global volume confirmation filter
        vol_check = VolumeFilter.evaluate(rolling_data, MIN_CONFIDENCE)
        if not vol_check["recommended"]:
            return []

        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")

        signals: List[Signal] = []

        # Check for pin setup
        is_pin = self._is_pin(underlying_price, net_gamma, rolling_data, gex_calc)

        # Check for wall breakout — LONG (call wall)
        long_breakout = self._detect_breakout(
            underlying_price, net_gamma, rolling_data, gex_calc,
            depth_snapshot=depth_snapshot, direction=Direction.LONG
        )
        if long_breakout:
            # Regime filter for LONG
            if not self._regime_passes(regime, long_breakout["wall_gex"], gex_calc):
                return []
            sig = self._enter_squeeze(
                long_breakout, underlying_price, net_gamma, regime,
                rolling_data, depth_snapshot=depth_snapshot
            )
            if sig:
                signals.append(sig)

        # Check for wall breakout — SHORT (put wall)
        short_breakout = self._detect_breakout(
            underlying_price, net_gamma, rolling_data, gex_calc,
            depth_snapshot=depth_snapshot, direction=Direction.SHORT
        )
        if short_breakout:
            # Regime filter for SHORT
            if not self._regime_passes(regime, short_breakout["wall_gex"], gex_calc):
                return []
            sig = self._enter_squeeze(
                short_breakout, underlying_price, net_gamma, regime,
                rolling_data, depth_snapshot=depth_snapshot
            )
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
            3. Price between walls with high delta density at both
        """
        # Condition 1: Narrow range
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window is None or price_window.range is None:
            return False

        atr_pct = price_window.range / price
        if atr_pct > PIN_MAX_RANGE_PCT:
            return False

        # Condition 2: Positive net gamma
        if net_gamma <= 0:
            return False

        # Condition 3: Price between walls with high delta density
        # Get walls via get_wall_classifications and filter to "wall" type only
        walls = gex_calc.get_wall_classifications(threshold=MIN_WALL_GEX)
        walls = [w for w in walls if w.get("classification") == "wall"]

        above_walls = [w for w in walls if w["strike"] > price]
        below_walls = [w for w in walls if w["strike"] < price]

        # Must have at least one wall on each side
        if not (above_walls and below_walls):
            return False

        # Check delta density at nearest walls — high density = loaded spring
        nearest_above = min(above_walls, key=lambda w: w["strike"])
        nearest_below = max(below_walls, key=lambda w: w["strike"])

        density_above = gex_calc.get_delta_density(nearest_above["strike"])
        density_below = gex_calc.get_delta_density(nearest_below["strike"])

        # High density at walls = loaded spring
        return density_above > 0.3 and density_below > 0.3

    # ------------------------------------------------------------------
    # Breakout Detection
    # ------------------------------------------------------------------

    def _detect_breakout(
        self,
        price: float,
        net_gamma: float,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        depth_snapshot: Optional[Dict[str, Any]] = None,
        direction: Optional[Direction] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Detect breakout through a gamma wall.

        Args:
            direction: If set, only check for that direction.
                       None = check both LONG and SHORT.
            depth_snapshot: Optional depth data for liquidity vacuum detection.

        Returns dict with breakout info or None.
        """
        walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
        if not walls:
            return None

        price_window = rolling_data.get(KEY_PRICE_5M)

        if direction is None or direction == Direction.LONG:
            result = self._evaluate_long_squeeze(
                price, rolling_data, gex_calc, price_window, depth_snapshot
            )
            if result:
                return result

        if direction is None or direction == Direction.SHORT:
            result = self._evaluate_short_squeeze(
                price, rolling_data, gex_calc, price_window, depth_snapshot
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
        depth_snapshot: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate LONG squeeze: breakout above call wall.

        Conditions:
            1. Price near a call wall (WALL_PROXIMITY_PCT)
            2. Price sustained beyond the wall (last 2 ticks above)
            3. Liquidity vacuum on ask side (depth collapse)
            4. Wall strength above minimum threshold
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

            # Liquidity vacuum check (replaces volume surge)
            liquidity_vacuum = self._detect_liquidity_vacuum(
                "LONG", wall_strike, depth_snapshot
            )
            if liquidity_vacuum < 0.2:
                continue  # No vacuum = no acceleration potential

            # Wall strength computation
            wall_strength = self._compute_wall_strength(wall, gex_calc, price)

            return {
                "direction": Direction.LONG,
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_side": "call",
                "type": "call_wall_breakout",
                "liquidity_vacuum": liquidity_vacuum,
                "wall_strength": wall_strength,
            }

        return None

    def _evaluate_short_squeeze(
        self,
        price: float,
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        price_window: Any,
        depth_snapshot: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate SHORT squeeze: breakdown below put wall.

        Mirror of _evaluate_long_squeeze with direction reversed.

        Conditions:
            1. Price near a put wall (WALL_PROXIMITY_PCT)
            2. Price sustained below the wall (last 2 ticks below)
            3. Liquidity vacuum on bid side (depth collapse)
            4. Wall strength above minimum threshold
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

            # Liquidity vacuum check (replaces volume surge)
            liquidity_vacuum = self._detect_liquidity_vacuum(
                "SHORT", wall_strike, depth_snapshot
            )
            if liquidity_vacuum < 0.2:
                continue  # No vacuum = no acceleration potential

            # Wall strength computation
            wall_strength = self._compute_wall_strength(wall, gex_calc, price)

            return {
                "direction": Direction.SHORT,
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_side": "put",
                "type": "put_wall_breakout",
                "liquidity_vacuum": liquidity_vacuum,
                "wall_strength": wall_strength,
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
            price_window: Rolling price window with .values attribute.
            wall_strike: The gamma wall strike to check against.
            above: True = check price > wall_strike (LONG),
                   False = check price < wall_strike (SHORT).

        Returns True if sustained, False if just crossed (only 1 tick beyond).
        """
        if price_window is None:
            return True  # No price data — don't block

        values = getattr(price_window, "values", None)
        if values is None:
            return True  # No values — don't block

        # Need at least 2 data points to check sustain
        if len(values) < 2:
            return True

        # Check last 2 data points
        if above:
            # LONG: last 2 prices must be > wall_strike
            return values[-1] > wall_strike and values[-2] > wall_strike
        else:
            # SHORT: last 2 prices must be < wall_strike
            return values[-1] < wall_strike and values[-2] < wall_strike

    # ------------------------------------------------------------------
    # Liquidity Vacuum Detection (NEW)
    # ------------------------------------------------------------------

    def _detect_liquidity_vacuum(
        self,
        direction: str,
        wall_strike: float,
        depth_snapshot: Optional[Dict[str, Any]],
    ) -> float:
        """
        Score liquidity vacuum on breakout side (0.0=none, 1.0=strong vacuum).

        For LONG squeeze: check ASK side (we want asks collapsing = easy to move up)
        For SHORT squeeze: check BID side (we want bids collapsing = easy to move down)

        Score = 0.7 * size_collapse + 0.3 * spread_widening

        Returns 0.0-1.0. Returns 0.0 if no depth data (graceful degradation).
        """
        if not depth_snapshot:
            return 0.0

        # For LONG squeeze: check ASK side (market makers pulling asks)
        # For SHORT squeeze: check BID side (market makers pulling bids)
        if direction == "LONG":
            size_data = depth_snapshot.get("ask_size", {})
        else:
            size_data = depth_snapshot.get("bid_size", {})

        current = size_data.get("current", 0) if size_data else 0
        mean = size_data.get("mean", 0) if size_data else 0

        if mean <= 0:
            return 0.0

        # Size collapse ratio: how much has size dropped from its mean
        collapse_ratio = 1.0 - (current / mean)

        # Spread widening confirms liquidity stress
        spread_data = depth_snapshot.get("spread", {})
        current_spread = spread_data.get("current", 0) if spread_data else 0
        mean_spread = spread_data.get("mean", 0) if spread_data else 0

        spread_widening = 0.0
        if mean_spread > 0 and current_spread > mean_spread:
            spread_widening = min(1.0, (current_spread - mean_spread) / mean_spread)

        # Combined score: 70% size collapse + 30% spread widening
        score = 0.7 * min(1.0, collapse_ratio) + 0.3 * spread_widening
        return round(score, 3)

    # ------------------------------------------------------------------
    # Wall Strength Computation (NEW)
    # ------------------------------------------------------------------

    def _compute_wall_strength(
        self, wall: Dict[str, Any], gex_calc: Any, price: float
    ) -> float:
        """
        Score wall strength for squeeze potential (0.0-1.0).

        IV component: (wall_iv - atm_iv) / atm_iv → score 0.5-0.8
        GEX component: abs(gex) / 5M → score 0.5-1.0
        Classification bonus: 1.0 if "wall", 0.0 if "magnet"

        Returns: 0.4*iv + 0.4*gex + 0.2*classification
        """
        wall_strike = wall["strike"]

        # IV component: high IV at wall = active hedging = bigger squeeze
        wall_iv = gex_calc.get_iv_by_strike(wall_strike)
        atm_strike = gex_calc.get_atm_strike(price) if price > 0 else None
        atm_iv = gex_calc.get_iv_by_strike(atm_strike) if atm_strike else None

        iv_score = 0.5
        if wall_iv and atm_iv and atm_iv > 0:
            iv_premium = (wall_iv - atm_iv) / atm_iv
            iv_score = 0.5 + 0.3 * min(1.0, max(-1.0, iv_premium))

        # GEX component: higher GEX = bigger potential
        gex_score = 0.5 + 0.5 * min(1.0, abs(wall.get("gex", 0)) / 5_000_000)

        # Classification bonus: only trade "wall" type
        classification_bonus = 1.0 if wall.get("classification") == "wall" else 0.0

        return round(0.4 * iv_score + 0.4 * gex_score + 0.2 * classification_bonus, 3)

    # ------------------------------------------------------------------
    # Liquidity-Aware Stop Placement (NEW)
    # ------------------------------------------------------------------

    def _liquidity_aware_stop(
        self,
        price: float,
        wall_strike: float,
        depth_snapshot: Optional[Dict[str, Any]],
        direction: str,
    ) -> float:
        """
        Place stop behind the nearest liquidity wall.

        For LONG: stop below wall (0.3-0.5% below)
        For SHORT: stop above wall (0.3-0.5% above)
        Tighter when depth shows strong support on that side.

        Returns a price (stop level).
        """
        if direction == "long":
            # Stop below wall, but not below next bid wall
            base_stop = wall_strike * 0.995  # 0.5% below wall
            # If depth shows strong bid support below, we can be tighter
            if depth_snapshot:
                bid_size = depth_snapshot.get("bid_size", {}).get("current", 0)
                if bid_size > 0:
                    # Strong bid support = can place tighter
                    return wall_strike * 0.997  # 0.3% below wall
            return base_stop
        else:
            # SHORT: stop above wall
            base_stop = wall_strike * 1.005
            if depth_snapshot:
                ask_size = depth_snapshot.get("ask_size", {}).get("current", 0)
                if ask_size > 0:
                    # Strong ask support = can place tighter
                    return wall_strike * 1.003
            return base_stop

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
        depth_snapshot: Optional[Dict[str, Any]] = None,
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

        # Liquidity-aware stop placement (replaces fixed 1% stops)
        stop = self._liquidity_aware_stop(
            price, wall_strike, depth_snapshot,
            "long" if direction == Direction.LONG else "short"
        )

        risk = abs(price - stop)
        target = price + (risk * TARGET_RISK_MULT) if direction == Direction.LONG else price - (risk * TARGET_RISK_MULT)

        if risk <= 0:
            return None

        # Confidence: wall strength + net gamma + volume confirmation
        # Pass depth_snapshot and wall_strength to _squeeze_confidence
        liquidity_vacuum = breakout.get("liquidity_vacuum", 0.0)
        wall_strength = breakout.get("wall_strength", 0.5)

        confidence = self._squeeze_confidence(
            wall_gex, net_gamma, price, risk, breakout,
            depth_snapshot=depth_snapshot,
            wall_strength=wall_strength,
            liquidity_vacuum=liquidity_vacuum,
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
                "liquidity_vacuum": round(liquidity_vacuum, 3),
                "wall_strength": round(wall_strength, 3),
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
        depth_snapshot: Optional[Dict[str, Any]] = None,
        wall_strength: float = 0.5,
        liquidity_vacuum: float = 0.0,
    ) -> float:
        """
        Confidence for squeeze trade (v2 with depth-aware components).

        Higher when:
            - Wall GEX is massive (bigger squeeze potential)
            - Net gamma is positive (dealer acceleration)
            - Risk is tight (clean breakout)
            - Liquidity vacuum is strong (depth collapse)
            - Wall has high IV strength (active hedging)
        """
        # Existing: wall strength (GEX)
        wall_conf = 0.2 + 0.15 * min(1.0, abs(wall_gex) / 5_000_000)

        # Existing: net gamma
        gamma_conf = 0.2 + 0.15 * min(1.0, net_gamma / 500_000)

        # Existing: risk tightness
        risk_pct = risk / price
        risk_conf = 0.15 + 0.1 * min(1.0, 0.005 / max(risk_pct, 0.001))

        # NEW: Liquidity vacuum score (0.1-0.2 weight)
        vacuum_conf = 0.1 + 0.1 * liquidity_vacuum

        # NEW: Wall IV strength (0.05-0.1 weight)
        iv_conf = 0.05 + 0.05 * wall_strength

        # Normalize each component to [0,1] and average
        norm_wall = (wall_conf - 0.2) / (0.35 - 0.2) if 0.35 != 0.2 else 1.0
        norm_gamma = (gamma_conf - 0.2) / (0.35 - 0.2) if 0.35 != 0.2 else 1.0
        norm_risk = (risk_conf - 0.15) / (0.25 - 0.15) if 0.25 != 0.15 else 1.0
        norm_vacuum = (vacuum_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        norm_iv = (iv_conf - 0.05) / (0.1 - 0.05) if 0.1 != 0.05 else 1.0

        return min(1.0, max(0.0, (norm_wall + norm_gamma + norm_risk + norm_vacuum + norm_iv) / 5.0))
