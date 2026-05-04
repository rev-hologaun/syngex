"""
strategies/layer2/iv_gex_divergence.py — IV-GEX Divergence

Volatility mean reversion strategy (bidirectional). Detects when price
is at an extreme relative to its recent range while implied volatility
is diverging and net gamma is strongly directional.

LONG: Price at low, IV expanding, negative gamma → mean-reversion long
SHORT: Price at high, IV crashing, positive gamma → mean-reversion short

Logic:
    SHORT (price at high):
        1. Price at high: latest price >= p75 of 30m rolling window
        2. IV crashing: IV at nearest ATM strike declining over recent window
        3. Net Gamma strongly positive: net_gamma > threshold
        4. Combined: short the underlying

    LONG (price at low):
        1. Price at low: latest price <= p25 of 30m rolling window
        2. IV expanding: IV at nearest ATM strike rising over recent window
        3. Net Gamma strongly negative: net_gamma < -threshold
        4. Combined: long the underlying

Exit: At major Gamma Wall or when IV stabilizes

Confidence factors:
    - How extreme price is in the rolling range
    - Rate of IV change (crash or expand)
    - Magnitude of net gamma
    - Proximity to gamma walls
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_30M, KEY_TOTAL_DELTA_5M

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
    Detects IV-GEX divergence for bidirectional mean-reversion signals.

    When price is elevated, IV is collapsing, and gamma is strongly
    positive → SHORT (price at high, IV crashing, positive gamma).

    When price is depressed, IV is expanding, and gamma is strongly
    negative → LONG (price at low, IV expanding, negative gamma).
    """

    strategy_id = "iv_gex_divergence"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for IV-GEX divergence.

        Returns signals list — may contain SHORT, LONG, both, or empty.
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

        # --- SHORT check: price at high, IV crashing, positive gamma ---
        price_high = self._check_price_high(rolling_data)
        if price_high > 0:
            iv_crashing, iv_atm, iv_decline = self._check_iv_crashing(
                gex_calc, rolling_data, underlying_price,
            )
            if iv_crashing and net_gamma > MIN_POSITIVE_GAMMA:
                walls = gex_calc.get_gamma_walls(threshold=500000)
                wall_above = None
                for wall in walls:
                    if wall["strike"] > underlying_price and wall["side"] == "call":
                        wall_above = wall
                        break

                confidence = self._compute_confidence(
                    price_high, iv_decline, net_gamma,
                    wall_above, regime, "SHORT",
                )
                if confidence >= 0.35:
                    sig = self._build_signal(
                        signal_type="SHORT",
                        price=underlying_price,
                        confidence=confidence,
                        net_gamma=net_gamma,
                        iv_atm=iv_atm,
                        iv_decline=iv_decline,
                        wall=wall_above,
                        regime=regime,
                        rolling_data=rolling_data,
                    )
                    if sig:
                        signals.append(sig)

        # --- LONG check: price at low, IV expanding, negative gamma ---
        price_low = self._check_price_low(rolling_data)
        if price_low > 0:
            iv_expanding, iv_atm, iv_expand = self._check_iv_expanding(
                gex_calc, rolling_data, underlying_price,
            )
            if iv_expanding and net_gamma < -MIN_POSITIVE_GAMMA:
                walls = gex_calc.get_gamma_walls(threshold=500000)
                wall_below = None
                for wall in walls:
                    if wall["strike"] < underlying_price and wall["side"] == "put":
                        wall_below = wall
                        break

                confidence = self._compute_confidence(
                    price_low, iv_expand, net_gamma,
                    wall_below, regime, "LONG",
                )
                if confidence >= 0.35:
                    sig = self._build_signal(
                        signal_type="LONG",
                        price=underlying_price,
                        confidence=confidence,
                        net_gamma=net_gamma,
                        iv_atm=iv_atm,
                        iv_decline=iv_expand,
                        wall=wall_below,
                        regime=regime,
                        rolling_data=rolling_data,
                    )
                    if sig:
                        signals.append(sig)

        return signals

    def _check_price_high(self, rolling_data: Dict[str, Any]) -> float:
        """
        Check if price is at a high in the 30m rolling window.

        Returns the percentile rank of current price in the window,
        or 0.0 if conditions not met.
        """
        window = rolling_data.get(KEY_PRICE_30M)
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

    def _check_price_low(self, rolling_data: Dict[str, Any]) -> float:
        """
        Check if price is at a low in the 30m rolling window.

        Returns the inverse percentile rank (0-1, where 1 = bottom 25%),
        or 0.0 if conditions not met.
        """
        window = rolling_data.get(KEY_PRICE_30M)
        if window is None or window.count < MIN_PRICE_POINTS:
            return 0.0

        latest = window.latest
        if latest is None:
            return 0.0

        percentile = window.percentile_rank(latest)
        if percentile is None:
            return 0.0

        # Price must be in bottom 25% of range (percentile <= 0.25)
        if percentile <= (1.0 - PRICE_PERCENTILE_THRESHOLD):  # <= 0.25
            # Return "lowness" score — 0.25 at p25, 1.0 at p0
            return 1.0 - percentile  # 0.75 at p25, 1.0 at p0

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
            delta_window = rolling_data.get(KEY_TOTAL_DELTA_5M)
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

    def _check_iv_expanding(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        price: float,
    ) -> tuple[bool, Optional[float], float]:
        """
        Check if IV is expanding at the nearest ATM strike.

        Returns (is_expanding, atm_iv, iv_expansion_pct).
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
            delta_window = rolling_data.get(KEY_TOTAL_DELTA_5M)
            if delta_window is None or delta_window.count < MIN_IV_POINTS:
                return False, None, 0.0

            latest = delta_window.latest
            avg = delta_window.mean
            if latest is None or avg is None or avg == 0:
                return False, None, 0.0

            expansion = (latest / avg) - 1.0
            return latest > avg / IV_DECLINE_RATIO, current_iv, expansion

        latest = iv_window.latest
        avg = iv_window.mean
        if latest is None or avg is None or avg == 0:
            return False, None, 0.0

        expansion = (latest / avg) - 1.0
        # IV expanding: latest above rolling avg by inverse of decline ratio
        is_expanding = latest > avg / IV_DECLINE_RATIO

        return is_expanding, current_iv, expansion

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
        signal_type: str,  # "LONG" or "SHORT"
    ) -> float:
        """
        Combine all factors into confidence score.

        Returns 0.0–1.0.
        """
        # 1. Price extremeness (0.20–0.30)
        if signal_type == "SHORT":
            # Higher in range = stronger overextension
            pct_conf = 0.20 + 0.10 * min(1.0, (price_percentile - 0.75) / 0.25)
        else:
            # Lower in range = stronger overextension
            pct_conf = 0.20 + 0.10 * min(1.0, (price_percentile - 0.75) / 0.25)

        # 2. IV change magnitude (0.20–0.25)
        iv_conf = 0.20 + 0.05 * min(1.0, iv_decline / 0.15)

        # 3. Net gamma magnitude (0.15–0.20)
        gamma_conf = 0.15 + 0.05 * min(1.0, abs(net_gamma) / 5_000_000)

        # 4. Wall proximity (0.05–0.10)
        wall_conf = 0.10 if wall_above else 0.0

        # 5. Regime alignment (0.05–0.10)
        if signal_type == "SHORT":
            regime_conf = 0.10 if regime == "POSITIVE" else 0.05
        else:
            regime_conf = 0.10 if regime == "NEGATIVE" else 0.05

        # Normalize each component to [0,1] and average
        norm_pct = (pct_conf - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_iv = (iv_conf - 0.20) / (0.25 - 0.20) if 0.25 != 0.20 else 1.0
        norm_gamma = (gamma_conf - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_wall = wall_conf / 0.10 if 0.10 != 0 else 0.0
        norm_regime = (regime_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        confidence = (norm_pct + norm_iv + norm_gamma + norm_wall + norm_regime) / 5.0
        return min(MAX_CONFIDENCE, max(0.0, confidence))

    def _build_signal(
        self,
        signal_type: str,
        price: float,
        confidence: float,
        net_gamma: float,
        iv_atm: Optional[float],
        iv_decline: float,
        wall: Optional[Dict[str, Any]],
        regime: str,
        rolling_data: Dict[str, Any],
    ) -> Optional[Signal]:
        """Build a Signal object for LONG or SHORT divergence."""
        entry = price

        if signal_type == "SHORT":
            stop = entry * (1 + STOP_PCT)
            risk = stop - entry
            price_window = rolling_data.get(KEY_PRICE_30M)
            rolling_mean = price_window.mean if price_window else entry
            target = entry - (entry - rolling_mean) * TARGET_RISK_MULT
            target = max(target, stop - risk * 0.1)

            wall_info = ""
            if wall:
                wall_info = f" | nearest call wall at {wall['strike']}"

            return Signal(
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
                    "price_percentile": round(1.0 - iv_decline, 3),
                    "iv_atm": round(iv_atm, 4) if iv_atm else None,
                    "iv_decline_pct": round(iv_decline, 4),
                    "net_gamma": round(net_gamma, 2),
                    "wall_above_strike": wall["strike"] if wall else None,
                    "wall_above_gex": wall["gex"] if wall else None,
                    "regime": regime,
                    "risk": round(risk, 2),
                    "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
                },
            )
        else:  # LONG
            stop = entry * (1 - STOP_PCT)
            risk = entry - stop
            price_window = rolling_data.get(KEY_PRICE_30M)
            rolling_mean = price_window.mean if price_window else entry
            target = entry + (rolling_mean - entry) * TARGET_RISK_MULT
            target = min(target, stop + risk * 0.1)

            wall_info = ""
            if wall:
                wall_info = f" | nearest put wall at {wall['strike']}"

            return Signal(
                direction=Direction.LONG,
                confidence=round(min(confidence, MAX_CONFIDENCE), 3),
                entry=round(entry, 2),
                stop=round(stop, 2),
                target=round(target, 2),
                strategy_id=self.strategy_id,
                reason=(
                    f"IV-GEX divergence: price at low + IV expanding "
                    f"(Δ{iv_decline:.1%}) + negative gamma {net_gamma:.0f}"
                    f"{wall_info}"
                ),
                metadata={
                    "price_percentile": round(iv_decline, 3),
                    "iv_atm": round(iv_atm, 4) if iv_atm else None,
                    "iv_decline_pct": round(iv_decline, 4),
                    "net_gamma": round(net_gamma, 2),
                    "wall_below_strike": wall["strike"] if wall else None,
                    "wall_below_gex": wall["gex"] if wall else None,
                    "regime": regime,
                    "risk": round(risk, 2),
                    "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
                },
            )
