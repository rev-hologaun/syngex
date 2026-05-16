"""
strategies/layer1/gex_divergence.py — GEX Divergence

Finding exhaustion by comparing price trend vs. GEX trend.
If Price ↑ but Total GEX ↓ (walls evaporating), the trend is losing
structural support and is likely to reverse.

Concept:
    Gamma walls provide structural support for price trends.
    When price trends but GEX trends in the opposite direction,
    the structural foundation is eroding — the trend is exhausted.

    Bearish divergence: price UP + GEX DOWN → fade (SHORT)
    Bullish divergence: price DOWN + GEX UP → fade (LONG)

Logic:
    1. Track price trend via rolling window slope
    2. Track GEX trend via rolling net_gamma window
    3. Divergence = slopes have opposite signs AND both exceed threshold
    4. OHLC confirmation: last candle must align with the fade direction

Entry:
    - Bearish divergence + confirming candle → SHORT
    - Bullish divergence + confirming candle → LONG

Exit:
    - Stop: 0.5% from entry
    - Target: 1.5× risk (1:1.5 RR)

Confidence factors:
    - Magnitude of price slope vs GEX slope (larger divergence = higher confidence)
    - Wall strength at divergence point (strong walls = bigger reversal)
    - Regime alignment
    - Confirmation candle strength
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_PRICE_30M, KEY_NET_GAMMA_5M

logger = logging.getLogger("Syngex.Strategies.GEXDivergence")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DIVERGENCE_MIN_SLOPE = 0.0005   # Minimum slope magnitude (0.05% — catches subtler divergences)
DIVERGENCE_WINDOW = 30           # Number of points for slope calculation
CONFIRMATION_CANDLE_PCT = 0.002  # 0.2% candle for confirmation
MIN_CONFIDENCE = 0.10            # Minimum confidence to emit signal (relaxed for v2 Structural-Decay)
STOP_PCT = 0.005                 # 0.5% stop
TARGET_RISK_MULT = 1.5           # 1.5× risk for target
MIN_DATA_POINTS = 15             # Minimum data points for slope calculation
MIN_TOTAL_GEX = 1000000.0        # 1M — minimum GEX wall strength

# v2 Structural-Decay params
ACCEL_WINDOW_SHORT = 10
ACCEL_WINDOW_LONG = 30
ACCEL_MIN_GAMMA = 0.0003
ACCEL_MIN_PRICE = 0.0002
WALL_PROXIMITY_PCT = 0.005
WALL_PROXIMITY_BONUS = 0.15
LIQUIDITY_DECAY_THRESHOLD = 0.3
REGIME_INTENSITY_THRESHOLD = 500000
STRONG_REGIME_CONF_BONUS = 0.1


class GEXDivergence(BaseStrategy):
    """
    GEX Divergence strategy: fade exhausted trends via price/GEX slope divergence.

    When price trends in one direction but GEX trends the other,
    the structural support for the trend is evaporating. Fade the move.

    Regime is a soft confidence factor (not a hard gate): aligned regimes
    boost confidence, misaligned regimes reduce it but do not block signals.

    Requires rolling "price" and "net_gamma" windows in rolling_data.
    """

    strategy_id = "gex_divergence"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate price/GEX divergence and return fade signals.

        Returns empty list when divergence is not detected or data
        is insufficient.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        regime = data.get("regime", "")

        # Get price rolling window
        price_window = self._get_price_window(rolling_data)
        if price_window is None or price_window.count < MIN_DATA_POINTS:
            return []

        # Get net_gamma rolling window — this is critical
        gamma_window = self._get_gamma_window(rolling_data)
        if gamma_window is None or gamma_window.count < MIN_DATA_POINTS:
            return []  # No gamma data — skip gracefully

        # Calculate slopes
        price_slope = self._calculate_slope(price_window)
        gamma_slope = self._calculate_slope(gamma_window)

        if price_slope is None or gamma_slope is None:
            return []

        # === v2: Acceleration (2nd derivative) check ===
        price_accel = self._calculate_acceleration(price_window, ACCEL_WINDOW_SHORT, ACCEL_WINDOW_LONG)
        gamma_accel = self._calculate_acceleration(gamma_window, ACCEL_WINDOW_SHORT, ACCEL_WINDOW_LONG)
        if price_accel is None or gamma_accel is None:
            return []
        if abs(price_accel["acceleration"]) < ACCEL_MIN_PRICE:
            return []
        if abs(gamma_accel["acceleration"]) < ACCEL_MIN_GAMMA:
            return []

        # Check for divergence: slopes must have opposite signs
        if (price_slope > 0 and gamma_slope > 0) or \
           (price_slope < 0 and gamma_slope < 0):
            return []  # Same direction — no divergence

        # Both slopes must exceed minimum magnitude
        if abs(price_slope) < DIVERGENCE_MIN_SLOPE:
            return []
        if abs(gamma_slope) < DIVERGENCE_MIN_SLOPE:
            return []

        # Determine divergence type
        if price_slope > 0 and gamma_slope < 0:
            # Bearish divergence: price up, GEX down → SHORT
            divergence_type = "bearish"
        else:
            # Bullish divergence: price down, GEX up → LONG
            divergence_type = "bullish"

        # === v2: Liquidity decay filter (hard gate) ===
        depth_snapshot = data.get("depth_snapshot")
        if not self._check_liquidity_decay(depth_snapshot, divergence_type):
            return []

        # Regime alignment: soft confidence factor, not a hard gate.
        regime_misaligned = False
        if divergence_type == "bullish" and regime != "POSITIVE":
            regime_misaligned = True
        if divergence_type == "bearish" and regime != "NEGATIVE":
            regime_misaligned = True

        # === v2: Wall proximity and regime intensity ===
        wall_bonus = self._check_wall_proximity(gex_calc, underlying_price, divergence_type)
        regime_intensity = self._compute_regime_intensity(gex_calc, divergence_type)

        # Get confirmation from last price movement
        price_change = self._get_price_change(price_window)
        confirmed = self._check_confirmation(price_change, divergence_type)
        if not confirmed:
            return []  # No confirmation candle

        # Compute confidence
        confidence = self._compute_confidence(
            price_slope, gamma_slope, divergence_type,
            price_window, gamma_window, regime, confirmed,
            regime_misaligned,
            price_accel=price_accel,
            gamma_accel=gamma_accel,
            wall_bonus=wall_bonus,
            regime_intensity=regime_intensity,
        )
        if confidence < MIN_CONFIDENCE:
            return []

        # GEX wall strength gate: divergence on thin walls is worthless
        try:
            summary = gex_calc.get_summary()
            net_gamma_val = summary.get("net_gamma", 0.0)
            if abs(net_gamma_val) < MIN_TOTAL_GEX:
                return []  # GEX walls too weak for a reliable signal
        except Exception:
            return []  # Can't assess GEX strength — skip

        # Build signal
        if divergence_type == "bearish":
            direction = Direction.SHORT
            stop = underlying_price * (1 + STOP_PCT)
            target = underlying_price * (1 - STOP_PCT * TARGET_RISK_MULT)
            reason_suffix = "price rising but GEX walls evaporating"
        else:
            direction = Direction.LONG
            stop = underlying_price * (1 - STOP_PCT)
            target = underlying_price * (1 + STOP_PCT * TARGET_RISK_MULT)
            reason_suffix = "price falling but GEX walls strengthening"

        risk = abs(underlying_price - stop)
        reward = abs(target - underlying_price)

        return [Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=underlying_price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"GEX divergence ({divergence_type}): {reason_suffix}, "
                   f"price_slope={price_slope:.4f}, gamma_slope={gamma_slope:.4f}, "
                   f"regime={regime}",
            metadata={
                "divergence_type": divergence_type,
                "price_slope": round(price_slope, 6),
                "gamma_slope": round(gamma_slope, 6),
                "price_window_count": price_window.count,
                "gamma_window_count": gamma_window.count,
                "trend": price_window.trend if price_window else "UNKNOWN",
                "regime": regime,
                "risk": round(risk, 2),
                "reward": round(reward, 2),
                "risk_reward_ratio": round(reward / risk, 2) if risk > 0 else 0,
                # v2 Structural-Decay fields
                "price_acceleration": round(price_accel["acceleration"], 6) if price_accel else None,
                "gamma_acceleration": round(gamma_accel["acceleration"], 6) if gamma_accel else None,
                "wall_proximity_bonus": round(wall_bonus, 4),
                "regime_intensity_bonus": round(regime_intensity, 4),
            },
        )]

    # ------------------------------------------------------------------
    # Slope calculation
    # ------------------------------------------------------------------

    def _calculate_slope(self, window: Any) -> Optional[float]:
        """
        Calculate the slope of a rolling window using first and last values.

        Slope = (last - first) / first as a percentage.
        Returns None if insufficient data.
        """
        if window.count < 5:
            return None

        first_val = window.values[0] if window.values else None
        last_val = window.values[-1] if window.values else None

        if first_val is None or last_val is None or first_val == 0:
            return None

        slope = (last_val - first_val) / abs(first_val)
        return slope

    # ------------------------------------------------------------------
    # Acceleration (2nd derivative)
    # ------------------------------------------------------------------

    def _calculate_acceleration(self, window: Any, short_window: int, long_window: int) -> Optional[Dict[str, float]]:
        """Calculate acceleration (2nd derivative) for a rolling window."""
        if window.count < long_window or not window.values:
            return None
        values = window.values
        if len(values) < long_window:
            return None
        short_vals = values[-short_window:]
        if len(short_vals) < 3 or short_vals[0] == 0:
            return None
        short_slope = (short_vals[-1] - short_vals[0]) / abs(short_vals[0])
        if values[0] == 0:
            return None
        long_slope = (values[-1] - values[0]) / abs(values[0])
        accel = short_slope - long_slope
        return {"slope_short": short_slope, "slope_long": long_slope, "acceleration": accel}

    # ------------------------------------------------------------------
    # Wall proximity check
    # ------------------------------------------------------------------

    def _check_wall_proximity(self, gex_calc: Any, price: float, divergence_type: str) -> float:
        """Check if price is near a major gamma wall in divergence direction."""
        try:
            walls = gex_calc.get_gamma_walls(threshold=500_000)
        except Exception:
            return 0.0
        if not walls:
            return 0.0
        min_dist_pct = float('inf')
        for wall in walls:
            wall_strike = wall.get("strike", 0)
            if wall_strike <= 0:
                continue
            if divergence_type == "bearish":
                if wall_strike > price:
                    dist_pct = abs(wall_strike - price) / price
                    min_dist_pct = min(min_dist_pct, dist_pct)
            else:
                if wall_strike < price:
                    dist_pct = abs(wall_strike - price) / price
                    min_dist_pct = min(min_dist_pct, dist_pct)
        if min_dist_pct == float('inf') or min_dist_pct > WALL_PROXIMITY_PCT:
            return 0.0
        proximity_ratio = 1.0 - (min_dist_pct / WALL_PROXIMITY_PCT)
        return WALL_PROXIMITY_BONUS * proximity_ratio

    # ------------------------------------------------------------------
    # Liquidity decay check
    # ------------------------------------------------------------------

    def _check_liquidity_decay(self, depth_snapshot: Optional[Dict[str, Any]], divergence_type: str) -> bool:
        """Check if liquidity decay supports divergence signal."""
        if not depth_snapshot:
            return True
        bid_depth = depth_snapshot.get("bid_size", {}).get("current", 0)
        ask_depth = depth_snapshot.get("ask_size", {}).get("current", 0)
        if bid_depth <= 0 and ask_depth <= 0:
            return True
        if divergence_type == "bearish":
            if ask_depth > 0:
                return (bid_depth / ask_depth) < (1.0 + LIQUIDITY_DECAY_THRESHOLD)
            return True
        else:
            if bid_depth > 0:
                return (ask_depth / bid_depth) < (1.0 + LIQUIDITY_DECAY_THRESHOLD)
            return True

    # ------------------------------------------------------------------
    # Regime intensity
    # ------------------------------------------------------------------

    def _compute_regime_intensity(self, gex_calc: Any, divergence_type: str) -> float:
        """Compute regime intensity bonus based on |net_gamma| magnitude."""
        try:
            net_gamma = gex_calc.get_net_gamma()
        except Exception:
            return 0.0
        if net_gamma is None:
            return 0.0
        abs_gamma = abs(net_gamma)
        if abs_gamma < REGIME_INTENSITY_THRESHOLD:
            return 0.0
        ratio = min(1.0, abs_gamma / (REGIME_INTENSITY_THRESHOLD * 2))
        return STRONG_REGIME_CONF_BONUS * ratio

    # ------------------------------------------------------------------
    # Price change detection
    # ------------------------------------------------------------------

    def _get_price_change(self, window: Any) -> Optional[float]:
        """Get the recent price change from the window."""
        values = window.values
        if len(values) < 2:
            return None
        # Use last few values for recent change
        recent = values[-min(5, len(values)):]
        if len(recent) < 2:
            return None
        return (recent[-1] - recent[0]) / abs(recent[0])

    # ------------------------------------------------------------------
    # Confirmation check
    # ------------------------------------------------------------------

    def _check_confirmation(
        self,
        price_change: Optional[float],
        divergence_type: str,
    ) -> bool:
        """
        Check if the latest price movement confirms the divergence signal.

        For bearish divergence (SHORT): price should be declining or flat.
        For bullish divergence (LONG): price should be rising or flat.
        """
        if price_change is None:
            return True  # No change data — allow signal

        if divergence_type == "bearish":
            # Price should not be strongly rising
            # Allow small upticks (noise) but reject strong rallies
            return price_change < CONFIRMATION_CANDLE_PCT * 3
        else:
            # Price should not be strongly falling
            return price_change > -CONFIRMATION_CANDLE_PCT * 3

    # ------------------------------------------------------------------
    # Confidence computation
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        price_slope: float,
        gamma_slope: float,
        divergence_type: str,
        price_window: Any,
        gamma_window: Any,
        regime: str,
        confirmed: bool,
        regime_misaligned: bool = False,
        price_accel: Optional[Dict] = None,
        gamma_accel: Optional[Dict] = None,
        wall_bonus: float = 0.0,
        regime_intensity: float = 0.0,
    ) -> float:
        """
        Compute divergence signal confidence with v2 Structural-Decay integration.

        7-component formula (v2):

            1. Price slope: abs(price_slope) in [0, 0.01], higher = higher confidence.
            2. Gamma slope: abs(gamma_slope) in [0, 0.01], higher = higher confidence.
            3. Balance (slope ratio): min(|price|, |gamma|) / max(|price|, |gamma|) in [0, 1].
            4. Data quality: min(window counts) in [MIN_DATA_POINTS, MIN_DATA_POINTS+100].
            5. Regime alignment: 1.0 if aligned, 0.5 if not.
            6. Wall proximity bonus: [0, 0.15] — price near gamma wall in divergence direction.
            7. Regime intensity bonus: [0, 0.10] — |net_gamma| magnitude bonus.

        Returns 0.0–1.0.
        """
        # 1. Price slope: abs in [0, 0.01]
        norm_price = min(1.0, abs(price_slope) / 0.01)

        # 2. Gamma slope: abs in [0, 0.01]
        norm_gamma = min(1.0, abs(gamma_slope) / 0.01)

        # 3. Balance: slope ratio in [0, 1]
        max_slope = max(abs(price_slope), abs(gamma_slope))
        norm_balance = (
            min(abs(price_slope), abs(gamma_slope)) / max_slope
            if max_slope > 0
            else 0.0
        )

        # 4. Data quality: window count in [MIN_DATA_POINTS, MIN_DATA_POINTS+100]
        min_count = min(price_window.count, gamma_window.count)
        norm_data = (
            (min_count - MIN_DATA_POINTS) / 100.0
            if 100.0 != 0
            else 1.0
        )
        norm_data = min(1.0, max(0.0, norm_data))

        # 5. Regime alignment: 1.0 if aligned, 0.5 if not
        if not regime_misaligned:
            norm_regime = 1.0
        else:
            norm_regime = 0.5

        # 6. Wall proximity bonus: already [0, 0.15]
        norm_wall = wall_bonus

        # 7. Regime intensity bonus: already [0, 0.10]
        norm_regime_intensity = regime_intensity

        # Updated 7-component formula (v2 Structural-Decay integration):
        confidence = (norm_price + norm_gamma + norm_balance + norm_data + norm_regime + norm_wall + norm_regime_intensity) / 7.0

        return min(1.0, max(0.0, confidence))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_price_window(
        self, rolling_data: Dict[str, Any]
    ) -> Optional[Any]:
        """Get the best available price rolling window."""
        for key in (KEY_PRICE_5M, KEY_PRICE_30M):
            rw = rolling_data.get(key)
            if rw is not None and rw.count >= MIN_DATA_POINTS:
                return rw
        return None

    def _get_gamma_window(
        self, rolling_data: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Get the net_gamma rolling window.

        This is critical for the divergence strategy. If not present,
        the strategy cannot function — return None to skip.
        """
        for key in (KEY_NET_GAMMA_5M,):
            rw = rolling_data.get(key)
            if rw is not None and rw.count >= MIN_DATA_POINTS:
                return rw
        return None
