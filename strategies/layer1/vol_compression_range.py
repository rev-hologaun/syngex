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
    - IV compression (low skew std = true compression)
    - Delta density (hard walls get higher confidence)
    - Order book depth (adequate liquidity at edge required)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_PRICE_5M, KEY_PRICE_30M, KEY_VOLUME_5M,
    KEY_IV_SKEW_5M,
    KEY_DEPTH_BID_SIZE_5M, KEY_DEPTH_ASK_SIZE_5M,
)
from strategies.volume_filter import VolumeFilter

logger = logging.getLogger("Syngex.Strategies.VolCompressionRange")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COMPRESSION_PCT = 0.003                          # 0.3% max range for compression
MIN_RANGE_BARS = 20                              # Minimum data points in rolling window
WALL_EDGE_PROXIMITY = 0.004                      # 0.4% from wall for edge trade
MIN_CONFIDENCE = 0.30                            # Minimum confidence to emit signal
STOP_PCT = 0.006                                 # 0.6% stop (wider for scalping)
TARGET_RISK_MULT = 1.5                           # 1.5× risk for target
STD_THRESHOLD = 0.002                            # Max std of price for compression
IV_COMPRESSION_STD_THRESHOLD = 0.03              # Max rolling std of IV skew for compression
DEPTH_SPIKE_THRESHOLD = 1.3                      # Current depth >= 1.3x rolling avg for edge validation
REGIME_GAMMA_INTENSITY_THRESHOLD = 500000        # |net_gamma| for strong regime
NEGATIVE_REGIME_STOP_MULT = 1.5                  # Wider stops (fallback, strategy requires POSITIVE)
POSITIVE_REGIME_TIGHT_STOP_MULT = 0.7            # Tighter stops in strong positive gamma


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

        ts = data.get("timestamp", time.time())
        symbol = data.get("symbol", "")

        depth_snapshot = data.get("depth_snapshot")

        # Volume confirmation filter
        vol_filter = VolumeFilter.evaluate(rolling_data, MIN_CONFIDENCE)
        if not vol_filter["recommended"]:
            return []

        # Get the best price rolling window
        price_window = self._get_price_window(rolling_data)
        if price_window is None or price_window.count < MIN_RANGE_BARS:
            return []

        # Check for compression
        is_compressed = self._check_compression(price_window, underlying_price, rolling_data)
        if not is_compressed:
            return []

        signals: List[Signal] = []

        # Check range edges
        if price_window.max is not None:
            sig = self._check_upper_edge(
                price_window, underlying_price, gex_calc, regime,
                depth_snapshot, rolling_data
            )
            if sig:
                signals.append(sig)

        if price_window.min is not None:
            sig = self._check_lower_edge(
                price_window, underlying_price, gex_calc, regime,
                depth_snapshot, rolling_data
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
        rolling_data: Dict[str, Any],
    ) -> bool:
        """Check if price AND IV are in a compressed state.

        Two criteria (both must pass):
        1. Price range < COMPRESSION_PCT OR rolling std < STD_THRESHOLD
        2. IV is also compressed (via skew rolling std)
        """
        # Price compression (existing logic)
        rng = price_window.range
        if rng is not None and rng / price <= COMPRESSION_PCT:
            price_compressed = True
        else:
            std = price_window.std
            price_compressed = std is not None and std / price <= STD_THRESHOLD

        if not price_compressed:
            return False

        # IV compression (new)
        return self._check_iv_compression(rolling_data)

    def _check_iv_compression(self, rolling_data: Dict[str, Any]) -> bool:
        """Check if IV is also compressed (not just price).

        Uses rolling std of IV skew as a proxy for IV volatility.
        Low skew std = IV is stable = true compression.
        Graceful: returns True if no IV data (don't block on missing data).
        """
        iv_skew_rw = rolling_data.get(KEY_IV_SKEW_5M)
        if iv_skew_rw is None or iv_skew_rw.count < 10:
            return True
        if iv_skew_rw.std is None or iv_skew_rw.std <= 0:
            return True
        return iv_skew_rw.std <= IV_COMPRESSION_STD_THRESHOLD

    def _check_edge_liquidity(
        self,
        edge: str,
        depth_snapshot: Optional[Dict[str, Any]],
        rolling_data: Dict[str, Any],
    ) -> bool:
        """Check if order book depth at the edge shows adequate liquidity.

        edge: 'upper' (ask side) or 'lower' (bid side)
        Graceful: returns True if no depth data (don't block on missing data).
        """
        if not depth_snapshot:
            return True

        if edge == "upper":
            depth_key = "ask_size"
            rolling_key = KEY_DEPTH_ASK_SIZE_5M
        else:
            depth_key = "bid_size"
            rolling_key = KEY_DEPTH_BID_SIZE_5M

        depth_info = depth_snapshot.get(depth_key)
        if not depth_info:
            return True

        current_depth = depth_info.get("current", 0)
        if current_depth <= 0:
            return True

        depth_rw = rolling_data.get(rolling_key)
        if depth_rw is None or depth_rw.count < 10 or depth_rw.mean is None:
            return True

        avg_depth = depth_rw.mean
        if avg_depth <= 0:
            return True

        return current_depth >= avg_depth * DEPTH_SPIKE_THRESHOLD

    def _compute_regime_stop_mult(self, gex_calc: Any, regime: str) -> float:
        """Compute regime-adjusted stop multiplier.

        Strong positive gamma → tighter stops (0.7x).
        Weak/no gamma → wider stops (1.0x).
        """
        if regime != "POSITIVE":
            return NEGATIVE_REGIME_STOP_MULT

        net_gamma = gex_calc.get_net_gamma()
        if net_gamma is None:
            return 1.0

        abs_gamma = abs(net_gamma)
        if abs_gamma >= REGIME_GAMMA_INTENSITY_THRESHOLD:
            return POSITIVE_REGIME_TIGHT_STOP_MULT

        # Linear interpolation between 1.0 (at 0) and 0.7 (at threshold)
        ratio = abs_gamma / REGIME_GAMMA_INTENSITY_THRESHOLD
        return 1.0 - (1.0 - POSITIVE_REGIME_TIGHT_STOP_MULT) * ratio

    def _compute_wall_delta_density(
        self,
        gex_calc: Any,
        strike: float,
    ) -> float:
        """Compute delta density for a specific wall strike.

        High delta density = wall has real delta concentration = 'hard wall.'
        Graceful: returns 0.0 if no delta data available.
        """
        delta_data = gex_calc.get_delta_by_strike(strike)
        if not delta_data:
            return 0.0

        call_count = delta_data.get("call_count", 0)
        put_count = delta_data.get("put_count", 0)
        total_count = call_count + put_count

        if total_count == 0:
            return 0.0

        net_delta = abs(delta_data.get("net_delta", 0.0))
        density = net_delta / total_count
        return min(1.0, density / 10.0)

    # ------------------------------------------------------------------
    # Upper edge: price near rolling max + call wall above → SHORT
    # ------------------------------------------------------------------

    def _check_upper_edge(
        self,
        price_window: Any,
        price: float,
        gex_calc: Any,
        regime: str,
        depth_snapshot: Optional[Dict[str, Any]],
        rolling_data: Dict[str, Any],
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

        # === Liquidity check at edge (hard gate) ===
        if not self._check_edge_liquidity("upper", depth_snapshot, rolling_data):
            return None  # Thin book at edge — skip

        # === Delta density for wall weighting ===
        delta_density = self._compute_wall_delta_density(gex_calc, nearest_wall["strike"])

        # === Regime-adjusted stop ===
        stop_mult = self._compute_regime_stop_mult(gex_calc, regime)
        stop = nearest_wall["strike"] * (1 + STOP_PCT * stop_mult)
        risk = stop - price
        target = price - risk * TARGET_RISK_MULT
        if risk <= 0:
            return None

        # === Updated confidence with new factors ===
        confidence = self._edge_confidence(
            position_in_range, wall_distance, nearest_wall["gex"],
            rng / price, price_window.count, "short",
            is_put_wall=False,
            iv_compressed=self._check_iv_compression(rolling_data),
            delta_density=delta_density,
            regime_stop_mult=stop_mult,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        trend = price_window.trend if price_window else "UNKNOWN"

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
                "regime": regime,
                "trend": trend,
                "delta_density": round(delta_density, 4),
                "stop_mult": round(stop_mult, 4),
                "iv_compressed": self._check_iv_compression(rolling_data),
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
        depth_snapshot: Optional[Dict[str, Any]],
        rolling_data: Dict[str, Any],
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

        # Find nearest wall below price (any type; put walls get bonus)
        walls = gex_calc.get_gamma_walls(threshold=500_000)
        any_walls_below = [w for w in walls if w["strike"] < price]
        if not any_walls_below:
            return None

        nearest_wall = max(any_walls_below, key=lambda w: w["strike"])
        is_put_wall = nearest_wall.get("side") == "put"
        wall_distance = (price - nearest_wall["strike"]) / price

        if wall_distance > WALL_EDGE_PROXIMITY:
            return None  # Wall too far

        # === Liquidity check at edge (hard gate) ===
        if not self._check_edge_liquidity("lower", depth_snapshot, rolling_data):
            return None  # Thin book at edge — skip

        # === Delta density for wall weighting ===
        delta_density = self._compute_wall_delta_density(gex_calc, nearest_wall["strike"])

        # === Regime-adjusted stop ===
        stop_mult = self._compute_regime_stop_mult(gex_calc, regime)
        stop = nearest_wall["strike"] * (1 - STOP_PCT * stop_mult)
        risk = price - stop
        target = price + risk * TARGET_RISK_MULT
        if risk <= 0:
            return None

        # === Updated confidence with new factors ===
        confidence = self._edge_confidence(
            position_in_range, wall_distance, nearest_wall["gex"],
            rng / price, price_window.count, "long",
            is_put_wall=is_put_wall,
            iv_compressed=self._check_iv_compression(rolling_data),
            delta_density=delta_density,
            regime_stop_mult=stop_mult,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        trend = price_window.trend if price_window else "UNKNOWN"

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Range LONG: price near lower edge, wall at "
                   f"{nearest_wall['strike']:.0f}, range={rng/price:.2%}",
            metadata={
                "edge": "lower",
                "wall_strike": nearest_wall["strike"],
                "wall_gex": nearest_wall["gex"],
                "wall_side": nearest_wall.get("side", "unknown"),
                "is_put_wall": is_put_wall,
                "wall_distance_pct": round(wall_distance, 4),
                "position_in_range": round(position_in_range, 3),
                "range_pct": round(rng / price, 4),
                "price_window_count": price_window.count,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
                "regime": regime,
                "trend": trend,
                "delta_density": round(delta_density, 4),
                "stop_mult": round(stop_mult, 4),
                "iv_compressed": self._check_iv_compression(rolling_data),
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
        is_put_wall: bool = False,
        iv_compressed: bool = True,
        delta_density: float = 0.0,
        regime_stop_mult: float = 1.0,
        depth_score: Optional[float] = None,
    ) -> float:
        """
        Compute confidence for a range edge signal.

        Family A — simple average of 5 normalized components:

            1. Position in range: 0–1, closer to edge = higher.
            2. Wall proximity: wall_distance in [0, WALL_EDGE_PROXIMITY], closer = higher.
            3. Range tightness: range_pct in [0, COMPRESSION_PCT], tighter = higher.
            4. Wall strength: abs(wall_gex) in [0, 5_000_000], higher = higher.
            5. Data quality: window_count in [0, 200], more = higher.

        Future (Phase 5):
            depth_score: if provided, used as 6th component.

        Returns 0.0–1.0.
        """
        # 1. Position in range: closer to edge = higher
        if direction == "short":
            norm_pos = 1.0 - position_in_range
        else:
            norm_pos = position_in_range

        # 2. Wall proximity: closer = higher, range [0, WALL_EDGE_PROXIMITY]
        norm_wall = (
            1.0 - (wall_distance / WALL_EDGE_PROXIMITY)
            if WALL_EDGE_PROXIMITY > 0
            else 1.0
        )

        # 3. Range tightness: tighter = higher, range [0, COMPRESSION_PCT]
        norm_tight = max(0.0, 1.0 - (range_pct / COMPRESSION_PCT)) if COMPRESSION_PCT > 0 else 1.0

        # 4. Wall strength: higher GEX = higher, range [0, 5_000_000]
        norm_strength = min(1.0, abs(wall_gex) / 5_000_000)

        # 5. Data quality: more data = higher, range [0, 200]
        norm_data = min(1.0, window_count / 200.0)

        confidence = (norm_pos + norm_wall + norm_tight + norm_strength + norm_data) / 5.0

        return min(1.0, max(0.0, confidence))

    def _get_price_window(
        self, rolling_data: Dict[str, Any]
    ) -> Optional[Any]:
        """Get the best available price rolling window."""
        for key in (KEY_PRICE_5M, KEY_PRICE_30M):
            rw = rolling_data.get(key)
            if rw is not None and rw.count >= MIN_RANGE_BARS:
                return rw
        return None
