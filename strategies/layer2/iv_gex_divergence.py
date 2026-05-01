"""
strategies/layer2/iv_gex_divergence.py — IV-GEX Divergence

Volatility mean reversion strategy. Detects when price is at a high
relative to its recent range while implied volatility is crashing
and net gamma is strongly positive — a classic "picking up pennies
in front of a steamroller" warning.

Logic:
    1. Price at high: latest price >= p75 of 30m rolling window
    2. IV crashing: IV at nearest ATM strike declining over recent window
    3. Net Gamma strongly positive: net_gamma > threshold
    4. Combined: short the underlying (or buy puts)

Exit: At major Gamma Wall or when IV stabilizes

Confidence factors:
    - How high price is in the rolling range
    - Rate of IV decline
    - Magnitude of positive net gamma
    - Proximity to gamma walls
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.IVGEXDivergence")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Price must be at or above this percentile of 30m window
PRICE_PERCENTILE_THRESHOLD = 0.75     # p75 — price in top 25% of range

# Min data points for price window
MIN_PRICE_POINTS = 10

# Min data points for IV window
MIN_IV_POINTS = 5

# Min positive net gamma threshold
MIN_POSITIVE_GAMMA = 500000           # $500k net gamma

# IV decline threshold: IV must be below rolling avg by this ratio
IV_DECLINE_RATIO = 0.95             # IV below 95% of rolling avg

# Stop and target
STOP_PCT = 0.006                      # 0.6% stop
TARGET_RISK_MULT = 1.5                # 1.5× risk toward mean

# Max confidence cap
MAX_CONFIDENCE = 0.95


class IVGEXDivergence(BaseStrategy):
    """
    Detects IV-GEX divergence for mean-reversion shorts.

    When price is elevated, IV is collapsing, and gamma is strongly
    positive, dealers are long gamma and must sell rallies — a
    powerful mean-reversion signal.
    """

    strategy_id = "iv_gex_divergence"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for IV-GEX divergence.

        Returns empty list when conditions not met.
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

        # 1. Check if price is at a high in the 30m window
        price_high = self._check_price_high(rolling_data)
        if not price_high:
            return []

        # 2. Check if IV is crashing at ATM
        iv_crashing, iv_atm, iv_decline = self._check_iv_crashing(
            gex_calc, rolling_data, underlying_price,
        )
        if not iv_crashing:
            return []

        # 3. Check net gamma is strongly positive
        if net_gamma < MIN_POSITIVE_GAMMA:
            return []

        # 4. Find nearest gamma wall above price (exit reference)
        walls = gex_calc.get_gamma_walls(threshold=500000)
        wall_above = None
        for wall in walls:
            if wall["strike"] > underlying_price and wall["side"] == "call":
                wall_above = wall
                break

        # 5. Compute confidence
        confidence = self._compute_confidence(
            price_high, iv_decline, net_gamma,
            wall_above, regime,
        )
        if confidence < 0.35:
            return []

        # 6. Build signal
        entry = underlying_price
        stop = entry * (1 + STOP_PCT)
        risk = stop - entry

        # Target: toward rolling mean
        price_window = rolling_data.get("price_30m")
        rolling_mean = price_window.mean if price_window else entry
        target = entry - (entry - rolling_mean) * TARGET_RISK_MULT
        target = max(target, stop - risk * 0.1)  # At least a little room

        wall_info = ""
        if wall_above:
            wall_info = f" | nearest call wall at {wall_above['strike']}"

        return [Signal(
            direction=Direction.SHORT,
            confidence=round(min(confidence, MAX_CONFIDENCE), 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"IV-GEX divergence: price at high + IV crashing "
                f"(Δ{iv_decline:.1%}) + positive gamma {net_gamma:.0f}"
                f"{wall_info}"
            ),
            metadata={
                "price_percentile": round(price_high, 3),
                "iv_atm": round(iv_atm, 4) if iv_atm else None,
                "iv_decline_pct": round(iv_decline, 4),
                "net_gamma": round(net_gamma, 2),
                "wall_above_strike": wall_above["strike"] if wall_above else None,
                "wall_above_gex": wall_above["gex"] if wall_above else None,
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
            },
        )]

    def _check_price_high(self, rolling_data: Dict[str, Any]) -> float:
        """
        Check if price is at a high in the 30m rolling window.

        Returns the percentile rank of current price in the window,
        or 0.0 if conditions not met.
        """
        window = rolling_data.get("price_30m")
        if window is None or window.count < MIN_PRICE_POINTS:
            return 0.0

        latest = window.latest
        if latest is None:
            return 0.0

        percentile = window.percentile_rank(latest)
        if percentile is None:
            return 0.0

        # Price must be in top 25% of range
        if percentile >= PRICE_PERCENTILE_THRESHOLD:
            return percentile

        return 0.0

    def _check_iv_crashing(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        price: float,
    ) -> tuple[bool, Optional[float], float]:
        """
        Check if IV is crashing at the nearest ATM strike.

        Returns (is_crashing, atm_iv, iv_decline_pct).
        """
        # Find ATM strike
        atm_strike = self._find_atm_strike(gex_calc, price)
        if atm_strike is None:
            return False, None, 0.0

        # Get current IV at ATM
        current_iv = gex_calc.get_iv_by_strike(atm_strike)
        if current_iv is None:
            return False, None, 0.0

        # Check IV rolling window
        iv_window = rolling_data.get(f"iv_{atm_strike}_5m")
        if iv_window is None or iv_window.count < MIN_IV_POINTS:
            # Fallback: use total_delta window as proxy for IV trend
            # (IV often correlates with total_delta direction)
            delta_window = rolling_data.get("total_delta_5m")
            if delta_window is None or delta_window.count < MIN_IV_POINTS:
                return False, None, 0.0

            # Use delta decline as IV proxy
            latest = delta_window.latest
            avg = delta_window.mean
            if latest is None or avg is None or avg == 0:
                return False, None, 0.0

            decline = 1.0 - (latest / avg)
            return latest < avg * IV_DECLINE_RATIO, current_iv, decline

        latest = iv_window.latest
        avg = iv_window.mean
        if latest is None or avg is None or avg == 0:
            return False, None, 0.0

        decline = 1.0 - (latest / avg)
        is_crashing = latest < avg * IV_DECLINE_RATIO

        return is_crashing, current_iv, decline

    def _find_atm_strike(self, gex_calc: Any, price: float) -> Optional[float]:
        """Find the nearest strike in the gamma ladder to the current price."""
        return gex_calc.get_atm_strike(price)

    def _compute_confidence(
        self,
        price_percentile: float,
        iv_decline: float,
        net_gamma: float,
        wall_above: Optional[Dict[str, Any]],
        regime: str,
    ) -> float:
        """
        Combine all factors into confidence score.

        Returns 0.0–1.0.
        """
        # 1. Price percentile (0.20–0.30)
        # Higher in range = stronger overextension
        pct_conf = 0.20 + 0.10 * min(1.0, (price_percentile - 0.75) / 0.25)

        # 2. IV decline magnitude (0.20–0.25)
        iv_conf = 0.20 + 0.05 * min(1.0, iv_decline / 0.15)

        # 3. Net gamma magnitude (0.15–0.20)
        gamma_conf = 0.15 + 0.05 * min(1.0, net_gamma / 5_000_000)

        # 4. Wall proximity (0.05–0.10)
        wall_conf = 0.0
        if wall_above:
            # Closer wall = stronger exit signal = higher confidence
            wall_conf = 0.10

        # 5. Regime alignment (0.05–0.10)
        # Short signals are more reliable in positive gamma regime
        regime_conf = 0.10 if regime == "POSITIVE" else 0.05

        # Normalize each component to [0,1] and average
        norm_pct = (pct_conf - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_iv = (iv_conf - 0.20) / (0.25 - 0.20) if 0.25 != 0.20 else 1.0
        norm_gamma = (gamma_conf - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_wall = wall_conf / 0.10 if 0.10 != 0 else 0.0
        norm_regime = (regime_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        confidence = (norm_pct + norm_iv + norm_gamma + norm_wall + norm_regime) / 5.0
        return min(MAX_CONFIDENCE, max(0.0, confidence))
