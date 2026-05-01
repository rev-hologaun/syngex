"""
strategies/layer1/vol_compression_range.py — Vol Compression Range

In a "Long Gamma" (positive) regime, market makers' hedging dampens
volatility — price oscillates in a narrow range. This strategy scalps
the range edges: buy the dip at support, sell the rip at resistance.

Concept:
    Positive gamma = dealer hedging absorbs volatility.
    Price bounces between put-wall support and call-wall resistance.
    Trade the bounces, not the breaks.

Logic:
    1. Must be in POSITIVE gamma regime
    2. Price must be in a narrow range (0.5% max range)
    3. Detect compression via rolling window statistics
    4. Trade range edges:
       - Near rolling max + call wall above → SHORT (sell the rip)
       - Near rolling min + put wall below → LONG (buy the dip)

Exit:
    - Stop: 0.3% past range edge (tight stops for scalping)
    - Target: 1.5× risk (mean-reversion target)

Confidence factors:
    - Positive gamma regime (required)
    - Range tightness (tighter = higher confidence)
    - Wall proximity (walls at range edges = stronger rejection)
    - Message count (more data = more reliable range)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.VolCompressionRange")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COMPRESSION_PCT = 0.005       # 0.5% max range for compression
MIN_RANGE_BARS = 20           # Minimum data points in rolling window
WALL_EDGE_PROXIMITY = 0.004   # 0.4% from wall for edge trade
MIN_CONFIDENCE = 0.40         # Minimum confidence to emit signal
STOP_PCT = 0.003              # 0.3% stop (tight for scalping)
TARGET_RISK_MULT = 1.5        # 1.5× risk for target
STD_THRESHOLD = 0.002         # Max std of price for compression


class VolCompressionRange(BaseStrategy):
    """
    Vol Compression Range strategy: scalp range edges in positive gamma.

    In long gamma regimes, dealer hedging dampens volatility and creates
    mean-reverting ranges. Trade the edges: long at put-wall support,
    short at call-wall resistance.
    """

    strategy_id = "vol_compression_range"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate range compression and return edge signals.

        Returns empty list when not in positive gamma regime or no
        compression detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        regime = data.get("regime", "")

        # Must be positive gamma regime
        if regime != "POSITIVE":
            return []

        # Get the best price rolling window
        price_window = self._get_price_window(rolling_data)
        if price_window is None or price_window.count < MIN_RANGE_BARS:
            return []

        # Check for compression
        is_compressed = self._check_compression(price_window, underlying_price)
        if not is_compressed:
            return []

        signals: List[Signal] = []

        # Check range edges
        if price_window.max is not None:
            sig = self._check_upper_edge(
                price_window, underlying_price, gex_calc, regime
            )
            if sig:
                signals.append(sig)

        if price_window.min is not None:
            sig = self._check_lower_edge(
                price_window, underlying_price, gex_calc, regime
            )
            if sig:
                signals.append(sig)

        return signals

    # ------------------------------------------------------------------
    # Compression detection
    # ------------------------------------------------------------------

    def _check_compression(
        self,
        price_window: Any,
        price: float,
    ) -> bool:
        """
        Check if price is in a compressed range.

        Two criteria (either one suffices):
        1. Range (max - min) < COMPRESSION_PCT of price
        2. Rolling std < STD_THRESHOLD
        """
        # Range check
        rng = price_window.range
        if rng is not None and rng / price <= COMPRESSION_PCT:
            return True

        # Std check
        std = price_window.std
        if std is not None and std / price <= STD_THRESHOLD:
            return True

        return False

    # ------------------------------------------------------------------
    # Upper edge: price near rolling max + call wall above → SHORT
    # ------------------------------------------------------------------

    def _check_upper_edge(
        self,
        price_window: Any,
        price: float,
        gex_calc: Any,
        regime: str,
    ) -> Optional[Signal]:
        """
        Check if price is near the upper edge of the range with a call wall.

        Price near rolling max + call wall above = SHORT (sell the rip).
        """
        if price_window.max is None:
            return None

        max_price = price_window.max
        rng = price_window.range
        if rng is None or rng == 0:
            return None

        # Price should be in upper half of range
        position_in_range = (price - price_window.min) / rng
        if position_in_range < 0.6:
            return None  # Not near upper edge

        # Find nearest call wall above price
        walls = gex_calc.get_gamma_walls(threshold=500_000)
        call_walls = [w for w in walls if w["strike"] > price and w["side"] == "call"]
        if not call_walls:
            return None

        nearest_wall = min(call_walls, key=lambda w: w["strike"])
        wall_distance = (nearest_wall["strike"] - price) / price

        if wall_distance > WALL_EDGE_PROXIMITY:
            return None  # Wall too far

        # Compute confidence
        confidence = self._edge_confidence(
            position_in_range, wall_distance, nearest_wall["gex"],
            rng / price, price_window.count, "short"
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Stop above the wall (range edge)
        stop = nearest_wall["strike"] * (1 + STOP_PCT)
        risk = stop - price
        target = price - risk * TARGET_RISK_MULT
        if risk <= 0:
            return None

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Range SHORT: price near upper edge, call wall at "
                   f"{nearest_wall['strike']:.0f}, range={rng/price:.2%}",
            metadata={
                "edge": "upper",
                "call_wall_strike": nearest_wall["strike"],
                "call_wall_gex": nearest_wall["gex"],
                "wall_distance_pct": round(wall_distance, 4),
                "position_in_range": round(position_in_range, 3),
                "range_pct": round(rng / price, 4),
                "price_window_count": price_window.count,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    # ------------------------------------------------------------------
    # Lower edge: price near rolling min + put wall below → LONG
    # ------------------------------------------------------------------

    def _check_lower_edge(
        self,
        price_window: Any,
        price: float,
        gex_calc: Any,
        regime: str,
    ) -> Optional[Signal]:
        """
        Check if price is near the lower edge of the range with a put wall.

        Price near rolling min + put wall below = LONG (buy the dip).
        """
        if price_window.min is None:
            return None

        min_price = price_window.min
        rng = price_window.range
        if rng is None or rng == 0:
            return None

        # Price should be in lower half of range
        position_in_range = (price - price_window.min) / rng
        if position_in_range > 0.4:
            return None  # Not near lower edge

        # Find nearest put wall below price
        walls = gex_calc.get_gamma_walls(threshold=500_000)
        put_walls = [w for w in walls if w["strike"] < price and w["side"] == "put"]
        if not put_walls:
            return None

        nearest_wall = max(put_walls, key=lambda w: w["strike"])
        wall_distance = (price - nearest_wall["strike"]) / price

        if wall_distance > WALL_EDGE_PROXIMITY:
            return None  # Wall too far

        # Compute confidence
        confidence = self._edge_confidence(
            position_in_range, wall_distance, nearest_wall["gex"],
            rng / price, price_window.count, "long"
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Stop below the wall (range edge)
        stop = nearest_wall["strike"] * (1 - STOP_PCT)
        risk = price - stop
        target = price + risk * TARGET_RISK_MULT
        if risk <= 0:
            return None

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Range LONG: price near lower edge, put wall at "
                   f"{nearest_wall['strike']:.0f}, range={rng/price:.2%}",
            metadata={
                "edge": "lower",
                "put_wall_strike": nearest_wall["strike"],
                "put_wall_gex": nearest_wall["gex"],
                "wall_distance_pct": round(wall_distance, 4),
                "position_in_range": round(position_in_range, 3),
                "range_pct": round(rng / price, 4),
                "price_window_count": price_window.count,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _edge_confidence(
        self,
        position_in_range: float,
        wall_distance: float,
        wall_gex: float,
        range_pct: float,
        window_count: int,
        direction: str,
    ) -> float:
        """
        Compute confidence for a range edge signal.

        Factors:
        - Position in range: closer to edge = higher confidence (0.2–0.3)
        - Wall proximity: closer = higher confidence (0.2–0.3)
        - Range tightness: tighter = higher confidence (0.1–0.2)
        - Wall strength: higher |GEX| = higher confidence (0.1–0.2)
        - Data quality: more points = higher confidence (0.0–0.1)
        - Regime alignment: positive regime = required, bonus if confirmed (0.1)
        """
        # Position confidence: how close to edge
        if direction == "short":
            edge_proximity = 1.0 - position_in_range  # Closer to 1.0 = higher
        else:
            edge_proximity = position_in_range  # Closer to 0.0 = higher

        position_conf = 0.2 + 0.1 * edge_proximity

        # Wall proximity: closer to wall = higher confidence
        wall_conf = 0.2 + 0.1 * (1 - wall_distance / WALL_EDGE_PROXIMITY)

        # Range tightness: tighter range = higher confidence
        tightness_conf = 0.1 + 0.1 * max(0, 1 - range_pct / COMPRESSION_PCT)

        # Wall strength
        strength_conf = 0.1 + 0.1 * min(1.0, abs(wall_gex) / 5_000_000)

        # Data quality
        data_conf = min(0.1, window_count / 200)

        # Regime bonus (positive gamma regime already required)
        regime_conf = 0.1

        # Normalize each component to [0,1] and average
        norm_pos = (position_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0
        norm_wall = (wall_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0
        norm_tight = (tightness_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        norm_strength = (strength_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        norm_data = data_conf / 0.1 if 0.1 != 0 else 0.0
        norm_regime = regime_conf / 0.1 if 0.1 != 0 else 0.0
        confidence = (norm_pos + norm_wall + norm_tight + norm_strength + norm_data + norm_regime) / 6.0
        return min(1.0, max(0.0, confidence))

    def _get_price_window(
        self, rolling_data: Dict[str, Any]
    ) -> Optional[Any]:
        """Get the best available price rolling window."""
        for key in ("price", "price_5m", "price_30m"):
            rw = rolling_data.get(key)
            if rw is not None and rw.count >= MIN_RANGE_BARS:
                return rw
        return None
