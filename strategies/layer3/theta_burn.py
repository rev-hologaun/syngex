"""
strategies/layer3/theta_burn.py — Theta-Burn Scalp (The Pinning Effect)

Micro-signal (1Hz) strategy: exploits the pinning effect in high-gamma,
high-theta environments. Price oscillates between gamma walls as dealers
continuously hedge counter-cyclically.

Logic:
    - Strongly positive gamma regime required (MIN_NET_GAMMA threshold)
    - High aggregate theta (time decay accelerates range compression)
    - Price oscillating in narrow range between gamma walls
    - Sell rips at Call Walls, buy dips at Put Walls
    - Very quick targets (0.2-0.4%)

Entry:
    - LONG: buy dips at Put Wall + rejection signal + narrow range
    - SHORT: sell rips at Call Wall + rejection signal + narrow range

Exit:
    - Quick targets: 0.2-0.4% from entry
    - Stop: 0.3% beyond the wall
    - Time hold: 3-8 min max
    - Exit if IV expands (range breaking)

Confidence factors:
    - Gamma strength (stronger = higher)
    - Wall proximity (closer = higher)
    - Range narrowness (tighter = higher)
    - Rejection signal strength
    - Time of day (midday lull bonus)
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_PRICE_30M, KEY_VOLUME_5M

logger = logging.getLogger("Syngex.Strategies.ThetaBurn")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Net gamma must be strongly positive (threshold to avoid weak signals)
MIN_NET_GAMMA = 5000.0

# Wall proximity for bounce trades
WALL_PROXIMITY_PCT = 0.005  # 0.5%

# Stop loss: beyond the wall
STOP_PAST_WALL_PCT = 0.003  # 0.3% beyond the wall

# Quick targets: 0.2-0.4% from entry
MIN_TARGET_PCT = 0.002      # 0.2% min target
MAX_TARGET_PCT = 0.004      # 0.4% max target

# Range narrowness: 5m range must be < this % of 30m range
RANGE_NARROWNESS_RATIO = 0.40  # 40%

# Rejection signal thresholds
DIVERGENCE_VOLUME_THRESHOLD = 0.80  # Volume < 80% of avg = declining

# Min confidence
MIN_CONFIDENCE = 0.25
MAX_CONFIDENCE = 0.80  # Micro-signal cap, lower for pin trades

# Min data points
MIN_DATA_POINTS = 3

# Midday lull window in UTC (11:30-14:30 ET = 16:30-19:30 UTC)
# Using LA timezone (PDT = UTC-7), so 11:30-14:30 ET = 18:30-21:30 UTC
# But we use UTC timestamps directly: 16:30-19:30 UTC
MIDNIGHT_UTC_START = 16.5   # 16:30 UTC
MIDNIGHT_UTC_END = 19.5     # 19:30 UTC

# Gamma strength normalization for confidence
GAMMA_STRENGTH_HIGH = 1_000_000.0  # Above this = max gamma strength bonus


class ThetaBurn(BaseStrategy):
    """
    Exploits the pinning effect in high-gamma environments.

    When gamma is strongly positive, market makers hedge counter-cyclically:
    buying dips (at Put Walls) and selling rallies (at Call Walls). This
    creates a "pinning" effect where price oscillates between gamma walls.

    We trade these bounces with very quick targets (0.2-0.4%) since the
    pinning effect is range-bound — walls can and do break.

    In a POSITIVE gamma regime with strongly positive net gamma:
        LONG:  buy dips at Put Walls (below price)
        SHORT: sell rips at Call Walls (above price)

    Exits are quick: 0.2-0.4% targets, 0.3% stop beyond wall, 3-8 min hold.
    """

    strategy_id = "theta_burn"
    layer = "layer3"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for theta-burn pinning signals.

        Returns empty list when no pinning setup is detected.
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
        timestamp = data.get("timestamp", 0)

        # Must be POSITIVE gamma regime
        if regime != "POSITIVE":
            return []

        # Net gamma must be strongly positive
        if net_gamma < MIN_NET_GAMMA:
            return []

        # Validate rolling data availability
        price_5m = rolling_data.get(KEY_PRICE_5M)
        price_30m = rolling_data.get(KEY_PRICE_30M)
        volume_5m = rolling_data.get(KEY_VOLUME_5M)

        if (
            price_5m is None
            or price_30m is None
            or volume_5m is None
        ):
            return []

        if (
            price_5m.count < MIN_DATA_POINTS
            or price_30m.count < MIN_DATA_POINTS
            or volume_5m.count < MIN_DATA_POINTS
        ):
            return []

        # Check range narrowness: 5m range must be < 30% of 30m range
        range_ratio = self._check_range_narrowness(price_5m, price_30m)
        if range_ratio is None or range_ratio >= RANGE_NARROWNESS_RATIO:
            # Range not compressed enough — no pinning effect
            return []

        signals: List[Signal] = []

        # Get gamma walls
        walls = self._safe_get_walls(gex_calc)
        if not walls:
            return []

        # Check LONG (buy dips at Put Walls below price)
        long_sig = self._check_put_wall(
            underlying_price, gex_calc, rolling_data,
            net_gamma, walls, timestamp, range_ratio,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT (sell rips at Call Walls above price)
        short_sig = self._check_call_wall(
            underlying_price, gex_calc, rolling_data,
            net_gamma, walls, timestamp, range_ratio,
        )
        if short_sig:
            signals.append(short_sig)

        return signals

    # ------------------------------------------------------------------
    # LONG: Buy dips at Put Walls
    # ------------------------------------------------------------------

    def _check_put_wall(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        walls: List[Dict[str, Any]],
        timestamp: float,
        range_ratio: float,
    ) -> Optional[Signal]:
        """
        Evaluate Put Walls for LONG bounce opportunity.

        Put wall = negative net_gamma → acts as support.
        We want price approaching from above and showing rejection.
        """
        # Find Put Walls below price (negative gamma)
        put_walls = [
            w for w in walls
            if w["strike"] < price and w.get("side") == "put"
        ]
        if not put_walls:
            # Fallback: treat negative net_gamma walls as put walls
            put_walls = [
                w for w in walls
                if w["strike"] < price and w.get("net_gamma", 0) < 0
            ]
        if not put_walls:
            return None

        # Find the nearest Put Wall below price
        nearest_wall = max(put_walls, key=lambda w: w["strike"])
        wall_strike = nearest_wall["strike"]
        wall_gex = nearest_wall.get("gex", 0)
        wall_net_gamma = nearest_wall.get("net_gamma", 0)

        # Check proximity: price must be within WALL_PROXIMITY_PCT above wall
        distance_pct = (price - wall_strike) / price
        if distance_pct < 0 or distance_pct > WALL_PROXIMITY_PCT:
            return None

        # Check rejection signal
        rejection_score, rejection_type = self._check_rejection(
            rolling_data, "LONG", wall_strike,
        )
        if rejection_score < 0.3:
            return None

        # Compute confidence
        confidence = self._compute_confidence(
            price, wall_strike, wall_gex, wall_net_gamma,
            distance_pct, rejection_score, rejection_type,
            range_ratio, timestamp, "LONG",
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        entry = price
        stop = wall_strike * (1 - STOP_PAST_WALL_PCT)
        risk = entry - stop

        # Target: midpoint between wall and next wall above (or ATM)
        target = self._compute_bounce_target(
            wall_strike, walls, price, "above", risk,
        )

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Theta-Burn LONG: Put wall at {wall_strike} supported, "
                f"GEX={wall_gex:.0f}, range_ratio={range_ratio:.2f}, "
                f"{rejection_type}"
            ),
            metadata={
                "wall_type": "put",
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_net_gamma": wall_net_gamma,
                "distance_to_wall_pct": round(distance_pct, 4),
                "rejection_type": rejection_type,
                "rejection_score": round(rejection_score, 3),
                "range_ratio": round(range_ratio, 3),
                "net_gamma": round(net_gamma, 2),
                "regime": "POSITIVE",
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (target - entry) / risk, 2
                ) if risk > 0 else 0,
                "trend": trend,
            },
        )

    # ------------------------------------------------------------------
    # SHORT: Sell rips at Call Walls
    # ------------------------------------------------------------------

    def _check_call_wall(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        walls: List[Dict[str, Any]],
        timestamp: float,
        range_ratio: float,
    ) -> Optional[Signal]:
        """
        Evaluate Call Walls for SHORT bounce opportunity.

        Call wall = positive net_gamma → acts as resistance.
        We want price approaching from below and showing rejection.
        """
        # Find Call Walls above price (positive gamma)
        call_walls = [
            w for w in walls
            if w["strike"] > price and w.get("side") == "call"
        ]
        if not call_walls:
            # Fallback: treat positive net_gamma walls as call walls
            call_walls = [
                w for w in walls
                if w["strike"] > price and w.get("net_gamma", 0) > 0
            ]
        if not call_walls:
            return None

        # Find the nearest Call Wall above price
        nearest_wall = min(call_walls, key=lambda w: w["strike"])
        wall_strike = nearest_wall["strike"]
        wall_gex = nearest_wall.get("gex", 0)
        wall_net_gamma = nearest_wall.get("net_gamma", 0)

        # Check proximity: price must be within WALL_PROXIMITY_PCT below wall
        distance_pct = (wall_strike - price) / price
        if distance_pct < 0 or distance_pct > WALL_PROXIMITY_PCT:
            return None

        # Check rejection signal
        rejection_score, rejection_type = self._check_rejection(
            rolling_data, "SHORT", wall_strike,
        )
        if rejection_score < 0.3:
            return None

        # Compute confidence
        confidence = self._compute_confidence(
            price, wall_strike, wall_gex, wall_net_gamma,
            distance_pct, rejection_score, rejection_type,
            range_ratio, timestamp, "SHORT",
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        entry = price
        stop = wall_strike * (1 + STOP_PAST_WALL_PCT)
        risk = stop - entry

        # Target: midpoint between wall and next wall below (or ATM)
        target = self._compute_bounce_target(
            wall_strike, walls, price, "below", risk,
        )

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Theta-Burn SHORT: Call wall at {wall_strike} rejected, "
                f"GEX={wall_gex:.0f}, range_ratio={range_ratio:.2f}, "
                f"{rejection_type}"
            ),
            metadata={
                "wall_type": "call",
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_net_gamma": wall_net_gamma,
                "distance_to_wall_pct": round(distance_pct, 4),
                "rejection_type": rejection_type,
                "rejection_score": round(rejection_score, 3),
                "range_ratio": round(range_ratio, 3),
                "net_gamma": round(net_gamma, 2),
                "regime": "POSITIVE",
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (entry - target) / risk, 2
                ) if risk > 0 else 0,
                "trend": trend,
            },
        )

    # ------------------------------------------------------------------
    # Rejection Signal Detection
    # ------------------------------------------------------------------

    @staticmethod
    def _check_rejection(
        rolling_data: Dict[str, Any],
        direction: str,
        wall_strike: float,
    ) -> tuple[float, str]:
        """
        Check for rejection signals at a wall.

        Returns (score, type) where score is 0.0-1.0 and type is a string
        describing the rejection pattern.

        Three types of rejection (any one qualifies):
            1. Volume divergence: volume declining as price approaches wall
            2. Price position: price in lower/upper quartile of recent range
            3. Candle pattern: bullish/bearish candle (close > open or close < open)
        """
        price_window = rolling_data.get(KEY_PRICE_5M)
        vol_window = rolling_data.get(KEY_VOLUME_5M)

        if price_window is None or vol_window is None:
            return 0.0, "none"

        latest = price_window.latest
        if latest is None:
            return 0.0, "none"

        scores: List[tuple[float, str]] = []

        # Check 1: Volume divergence
        vol_score = ThetaBurn._check_volume_divergence(
            price_window, vol_window, wall_strike, direction,
        )
        if vol_score is not None:
            scores.append((vol_score, "volume_divergence"))

        # Check 2: Price position in range
        pos_score = ThetaBurn._check_price_position(
            price_window, direction,
        )
        if pos_score is not None:
            scores.append((pos_score, "price_position"))

        # Check 3: Candle pattern
        candle_score = ThetaBurn._check_candle_pattern(
            price_window, direction,
        )
        if candle_score is not None:
            scores.append((candle_score, "candle_pattern"))

        if not scores:
            return 0.0, "none"

        # Return the strongest rejection signal
        scores.sort(key=lambda x: x[0], reverse=True)
        best_score, best_type = scores[0]

        # Boost score if multiple signals confirm
        if len(scores) >= 2:
            best_score = min(1.0, best_score + 0.1)

        return best_score, best_type

    @staticmethod
    def _check_volume_divergence(
        price_window: Any,
        vol_window: Any,
        wall_strike: float,
        direction: str,
    ) -> Optional[float]:
        """
        Volume divergence: price near wall but volume declining.

        For LONG (Put Wall): price made a lower low near wall
        but volume is declining = selling exhaustion.

        For SHORT (Call Wall): price made a higher high near wall
        but volume is declining = buying exhaustion.
        """
        latest = price_window.latest
        window_min = price_window.min
        window_max = price_window.max
        vol_latest = vol_window.latest
        vol_avg = vol_window.mean

        if latest is None or vol_latest is None or vol_avg is None or vol_avg == 0:
            return None

        # Price must be near the wall
        proximity = abs(latest - wall_strike) / wall_strike
        if proximity > WALL_PROXIMITY_PCT * 2:
            return None

        # Volume declining vs rolling average
        vol_ratio = vol_latest / vol_avg
        if vol_ratio >= DIVERGENCE_VOLUME_THRESHOLD:
            return None

        # Score: lower volume = stronger divergence signal
        score = 0.4 + 0.5 * (1.0 - vol_ratio / DIVERGENCE_VOLUME_THRESHOLD)
        return min(1.0, score)

    @staticmethod
    def _check_price_position(
        price_window: Any,
        direction: str,
    ) -> Optional[float]:
        """
        Price position in recent range.

        For LONG: price in lower quartile (p25) of 5m range.
        For SHORT: price in upper quartile (p75) of 5m range.
        """
        latest = price_window.latest

        if direction == "LONG":
            p25 = price_window.p25
            if p25 is None or latest is None:
                return None
            if latest > p25:
                return None
            # Score: how far below p25?
            window_min = price_window.min
            if window_min is None or window_min == latest:
                return 0.5
            score = 0.4 + 0.5 * (p25 - latest) / (p25 - window_min)
            return min(1.0, score)
        else:
            p75 = price_window.p75
            if p75 is None or latest is None:
                return None
            if latest < p75:
                return None
            # Score: how far above p75?
            window_max = price_window.max
            if window_max is None or window_max == latest:
                return 0.5
            score = 0.4 + 0.5 * (latest - p75) / (window_max - p75)
            return min(1.0, score)

    @staticmethod
    def _check_candle_pattern(
        price_window: Any,
        direction: str,
    ) -> Optional[float]:
        """
        Candlestick pattern: close > open for bullish, close < open for bearish.

        Approximation:
            close = latest price
            open = rolling mean of the window
            upper wick = max - close
            lower wick = close - min
        """
        latest = price_window.latest
        window_max = price_window.max
        window_min = price_window.min
        open_price = price_window.mean

        if (
            latest is None
            or window_max is None
            or window_min is None
            or open_price is None
            or open_price == 0
        ):
            return None

        if direction == "LONG":
            # Bullish: close > open
            if latest <= open_price:
                return None
            # Upper wick should be smaller than lower wick (strong buy)
            upper_wick = window_max - latest
            lower_wick = latest - window_min
            if lower_wick <= 0:
                return 0.4  # Baseline for bullish candle
            # Score: longer lower wick = stronger rejection of lower prices
            wick_ratio = lower_wick / (upper_wick + lower_wick)
            return 0.4 + 0.4 * wick_ratio
        else:
            # Bearish: close < open
            if latest >= open_price:
                return None
            upper_wick = window_max - latest
            lower_wick = latest - window_min
            if upper_wick <= 0:
                return 0.4  # Baseline for bearish candle
            wick_ratio = upper_wick / (upper_wick + lower_wick)
            return 0.4 + 0.4 * wick_ratio

    # ------------------------------------------------------------------
    # Range Narrowness Check
    # ------------------------------------------------------------------

    @staticmethod
    def _check_range_narrowness(
        price_5m: Any,
        price_30m: Any,
    ) -> Optional[float]:
        """
        Check if the 5m range is compressed relative to the 30m range.

        Returns the ratio of 5m range / 30m range.
        Returns None if either range is zero or insufficient data.
        """
        range_5m = price_5m.range
        range_30m = price_30m.range

        if range_5m is None or range_30m is None:
            return None
        if range_30m <= 0:
            return None

        return range_5m / range_30m

    # ------------------------------------------------------------------
    # Confidence Computation
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        price: float,
        wall_strike: float,
        wall_gex: float,
        wall_net_gamma: float,
        distance_pct: float,
        rejection_score: float,
        rejection_type: str,
        range_ratio: float,
        timestamp: float,
        direction: str,
    ) -> float:
        """
        Combine all factors into a single confidence score.

        Factors:
            1. Gamma strength (0.15–0.25) — stronger positive gamma = higher
            2. Wall proximity (0.15–0.25) — closer to wall = higher
            3. Range narrowness (0.10–0.15) — tighter range = higher pinning
            4. Rejection signal (0.15–0.20) — divergence > candle pattern
            5. Time of day (0.05–0.10) — midday lull bonus for range trades

        Returns 0.0–MAX_CONFIDENCE (0.80).
        """
        # 1. Gamma strength component (0.15–0.25)
        # Use absolute net_gamma as proxy for gamma strength
        gamma_strength = abs(wall_net_gamma) if wall_net_gamma != 0 else abs(wall_gex)
        gamma_conf = 0.15 + 0.10 * min(1.0, gamma_strength / GAMMA_STRENGTH_HIGH)

        # 2. Wall proximity component (0.15–0.25)
        # At 0% distance = 0.25, at WALL_PROXIMITY_PCT = 0.15
        if distance_pct <= 0:
            prox_conf = 0.25
        elif distance_pct >= WALL_PROXIMITY_PCT:
            prox_conf = 0.15
        else:
            prox_conf = 0.25 - 0.10 * (distance_pct / WALL_PROXIMITY_PCT)

        # 3. Range narrowness component (0.10–0.15)
        # Tighter range (lower ratio) = stronger pinning effect
        if range_ratio <= 0:
            nar_conf = 0.15
        elif range_ratio >= RANGE_NARROWNESS_RATIO:
            nar_conf = 0.10
        else:
            nar_conf = 0.15 - 0.05 * (range_ratio / RANGE_NARROWNESS_RATIO)

        # 4. Rejection signal component (0.15–0.20)
        # Volume divergence > price position > candle pattern
        type_bonus = {
            "volume_divergence": 0.05,
            "price_position": 0.03,
            "candle_pattern": 0.00,
        }
        type_score = type_bonus.get(rejection_type, 0.0)
        rejection_conf = 0.15 + 0.05 * rejection_score + type_score

        # 5. Time of day component (0.05–0.10)
        # Midday lull 11:30-14:30 ET = 16:30-19:30 UTC
        tod_conf = self._time_of_day_confidence(timestamp)

        # Normalize each component to [0,1] and average
        norm_gamma = (gamma_conf - 0.15) / (0.25 - 0.15) if 0.25 != 0.15 else 1.0
        norm_prox = (prox_conf - 0.15) / (0.25 - 0.15) if 0.25 != 0.15 else 1.0
        norm_nar = (nar_conf - 0.10) / (0.15 - 0.10) if 0.15 != 0.10 else 1.0
        norm_reject = (rejection_conf - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_tod = (tod_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        confidence = (norm_gamma + norm_prox + norm_nar + norm_reject + norm_tod) / 5.0
        return min(MAX_CONFIDENCE, max(MIN_CONFIDENCE, confidence))

    @staticmethod
    def _time_of_day_confidence(timestamp: float) -> float:
        """
        Compute confidence bonus from time of day.

        Midday lull (11:30-14:30 ET = 16:30-19:30 UTC) favors range trades.
        Returns 0.05 (off-hours) or 0.10 (midday lull).
        """
        if timestamp <= 0:
            return 0.05  # Default baseline if timestamp unavailable

        # Extract UTC hour from Unix timestamp
        utc_hour = (timestamp % 86400) / 3600

        if MIDNIGHT_UTC_START <= utc_hour <= MIDNIGHT_UTC_END:
            return 0.10  # Midday lull bonus
        return 0.05  # Off-hours baseline

    # ------------------------------------------------------------------
    # Target Computation
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_bounce_target(
        wall_strike: float,
        walls: List[Dict[str, Any]],
        price: float,
        direction: str,
        risk: float,
    ) -> float:
        """
        Compute bounce target.

        For LONG (bounce off Put below): target = midpoint between
            the Put wall and the next wall above (or ATM).

        For SHORT (bounce off Call above): target = midpoint between
            the Call wall and the next wall below (or ATM).

        Falls back to risk-based target (0.2-0.4%) if no next wall found.
        """
        if direction == "above":
            # Find nearest wall above the Put wall
            candidates = [w for w in walls if w["strike"] > wall_strike]
            if candidates:
                next_wall = min(candidates, key=lambda w: w["strike"])
                midpoint = (wall_strike + next_wall["strike"]) / 2
                # Ensure target is above price
                target = max(price + (price * MIN_TARGET_PCT), midpoint)
                # Cap at MAX_TARGET_PCT
                max_target = price * (1 + MAX_TARGET_PCT)
                return min(target, max_target)
        else:
            # Find nearest wall below the Call wall
            candidates = [w for w in walls if w["strike"] < wall_strike]
            if candidates:
                next_wall = max(candidates, key=lambda w: w["strike"])
                midpoint = (wall_strike + next_wall["strike"]) / 2
                # Ensure target is below price
                target = min(price - (price * MIN_TARGET_PCT), midpoint)
                # Cap at MAX_TARGET_PCT
                min_target = price * (1 - MAX_TARGET_PCT)
                return max(target, min_target)

        # Fallback: use risk-based target (0.2-0.4% from entry)
        if risk <= 0:
            return price

        if direction == "above":
            target = price + risk
            max_target = price * (1 + MAX_TARGET_PCT)
            return max(price + (price * MIN_TARGET_PCT), min(target, max_target))
        else:
            target = price - risk
            min_target = price * (1 - MAX_TARGET_PCT)
            return min(price - (price * MIN_TARGET_PCT), max(target, min_target))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_get_walls(gex_calc: Any) -> List[Dict[str, Any]]:
        """Safely retrieve gamma walls, returning empty list on error."""
        try:
            return gex_calc.get_gamma_walls(threshold=MIN_NET_GAMMA)
        except Exception as exc:
            logger.debug("ThetaBurn: failed to get gamma walls: %s", exc)
            return []
