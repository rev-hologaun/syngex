"""
strategies/layer2/iv_gex_divergence.py — IV-GEX Divergence v2 "Volatility-Snap"

Volatility mean reversion strategy (bidirectional). Detects when price
is at an extreme relative to its recent range while implied volatility
is diverging and net gamma is strongly directional.

v2 upgrades (Volatility-Snap):
    - IV Skew Gradient: OTM-vs-ATM IV gap widening (tail risk detector)
    - Gamma Density Gradient: declining gamma density (structural snap)
    - Volume-Weighted IV: conviction filter via log(volume)
    - Wall-Based Stops: dynamic stops beyond nearest gamma wall

LONG: Price at low, IV expanding, negative gamma → mean-reversion long
SHORT: Price at high, IV crashing, positive gamma → mean-reversion short

Logic:
    SHORT (price at high):
        1. Price at high: latest price >= p60 of 30m rolling window
        2. IV crashing: ATM IV below rolling average threshold
        3. IV skew accelerating: OTM put IV rising faster than ATM IV
        4. Gamma density declining: price moving into unstable zone
        5. Gamma direction: positive gamma contributes to confidence
        6. Combined: short the underlying (confidence ≥ MIN_CONFIDENCE)

    LONG (price at low):
        1. Price at low: latest price <= p40 of 30m rolling window
        2. IV expanding: ATM IV above rolling average threshold
        3. IV skew accelerating: OTM call IV rising faster than ATM IV
        4. Gamma density declining: price moving into unstable zone
        5. Gamma direction: negative gamma contributes to confidence
        6. Combined: long the underlying (confidence ≥ MIN_CONFIDENCE)

Exit: At major Gamma Wall or when IV stabilizes

Confidence factors (10 components, simple average):
    1. Price extremeness          (0.0–1.0 normalized) — from price_percentile threshold→1.0
    2. Net gamma magnitude        (0.0–1.0 normalized) — from abs(net_gamma) 0→5M
    3. Wall proximity             (0.0–1.0 normalized) — from wall GEX 0→5M
    4. Volume conviction          (0.0–1.0 normalized) — from total_volume 0→100k
    5. Regime alignment           (0.0–1.0 normalized) — from regime intensity 0.05→0.15
    6. IV crash/expand score      (0.0–1.0) — from _check_iv_crashing/_check_iv_expanding
    7. IV skew ROC score          (0.0–1.0 normalized) — from skew_roc 0→0.20
    8. IV skew acceleration       (0.0–1.0) — from _score_iv_skew_acceleration
    9. Gamma density decline      (0.0–1.0) — from _score_gamma_density_decline
    10. Gamma direction           (0.0–1.0) — from normalized net gamma direction

    MIN_CONFIDENCE = 0.20 (signals below this are suppressed)
"""

from __future__ import annotations

import math
import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_PRICE_30M,
    KEY_IV_SKEW_GRADIENT_5M,
    KEY_GAMMA_DENSITY_5M,
)

logger = logging.getLogger("Syngex.Strategies.IVGEXDivergence")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Price must be at or above this percentile of 30m window
PRICE_PERCENTILE_THRESHOLD = 0.60     # p60 — price in top 40% of range

# Min data points for price window
MIN_PRICE_POINTS = 10

# Min data points for IV window
MIN_IV_POINTS = 5

# Min positive net gamma threshold (cumulative — used for sign detection only)
MIN_POSITIVE_GAMMA = 200000           # $200k net gamma (cumulative, sign detection)

# Min positive normalized net gamma threshold (per-message average)
MIN_POSITIVE_NORMALIZED_GAMMA = 5.0   # normalized gamma threshold for signal trigger

# IV decline threshold: IV at ATM must be below rolling avg by this ratio
IV_DECLINE_RATIO = 0.85             # IV below 85% of rolling avg

# Stop and target
STOP_PCT = 0.006                      # 0.6% fallback stop
TARGET_RISK_MULT = 1.5                # 1.5× risk toward mean

# Min confidence threshold for signal emission
MIN_CONFIDENCE = 0.20

# v2 Volatility-Snap parameters
IV_SKEW_OTM_PCT = 0.05              # 5% OTM for skew calculation
IV_SKEW_ROC_WINDOW = 5              # ticks for skew ROC
IV_SKEW_ROC_THRESHOLD = 0.05        # skew must have risen ≥5%

GAMMA_DENSITY_WINDOW_PCT = 0.01     # ±1% window for gamma density
GAMMA_DENSITY_DECLINE_THRESHOLD = 0.85  # density must decline ≥15%

IV_VOLUME_MIN = 100                   # min volume to consider IV meaningful

WALL_STOP_BUFFER_PCT = 0.002        # 0.2% buffer beyond wall
WALL_STOP_MAX_DISTANCE_PCT = 0.02   # max distance to nearest wall (2%)
FALLBACK_STOP_PCT = 0.006           # fallback if no wall nearby


class IVGEXDivergence(BaseStrategy):
    """
    Detects IV-GEX divergence for bidirectional mean-reversion signals.

    v2: Uses IV skew gradient (tail risk), gamma density gradient
    (structural snap), volume-weighted IV (conviction), and
    wall-based stops (dynamic risk).
    """

    strategy_id = "iv_gex_divergence"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for IV-GEX divergence v2.

        Returns signals list — may contain SHORT, LONG, both, or empty.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma_normalized", 0)
        regime = data.get("regime", "")
        greeks_summary = data.get("greeks_summary", gex_calc.get_greeks_summary() or {})

        signals: List[Signal] = []

        # --- Evaluate SHORT and LONG independently ---
        signals.extend(
            self._evaluate_short(
                gex_calc, rolling_data, net_gamma, regime, greeks_summary,
                underlying_price,
            ),
        )
        signals.extend(
            self._evaluate_long(
                gex_calc, rolling_data, net_gamma, regime, greeks_summary,
                underlying_price,
            ),
        )

        return signals

    def _evaluate_short(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
        greeks_summary: Dict[str, Any],
        underlying_price: float,
    ) -> List[Signal]:
        """Evaluate SHORT direction independently.
        Returns list of signals (may be empty).
        """
        signals: List[Signal] = []
        price_high = self._check_price_high(rolling_data)
        if price_high <= 0:
            return signals

        iv_crashing, iv_atm, iv_crash_score = self._check_iv_crashing(
            gex_calc, rolling_data, underlying_price,
        )
        normalized_gamma = gex_calc.get_normalized_net_gamma()
        if not iv_crashing:
            return signals

        # Soft gamma direction score: positive gamma contributes, negative = 0
        gamma_dir_score = max(0.0, min(1.0, normalized_gamma / 10.0))

        skew_score = self._score_iv_skew_acceleration(
            gex_calc, rolling_data, underlying_price, "SHORT",
        )

        density_score = self._score_gamma_density_decline(
            gex_calc, rolling_data, underlying_price,
        )

        walls = gex_calc.get_gamma_walls(threshold=500000)
        wall_above = None
        for wall in walls:
            if wall["strike"] > underlying_price and wall["side"] == "call":
                wall_above = wall
                break

        stop_price, stop_type = self._compute_wall_based_stop(
            underlying_price, "SHORT", gex_calc,
        )

        iv_skew, iv_skew_roc = self._get_skew_data(
            gex_calc, rolling_data, underlying_price, "SHORT",
        )
        confidence = self._compute_confidence_v2(
            price_high, net_gamma, wall_above, regime,
            underlying_price, greeks_summary,
            iv_score=iv_crash_score,
            skew_roc=iv_skew_roc,
            skew_score=skew_score,
            density_score=density_score,
            gamma_dir_score=gamma_dir_score,
        )

        if confidence >= MIN_CONFIDENCE:
            gamma_density_current, gamma_density_mean, gamma_density_decline_pct = (
                self._get_gamma_density_data(rolling_data)
            )
            conviction_iv, option_volume = self._get_conviction_data(
                greeks_summary, underlying_price, "SHORT",
            )
            regime_intensity = self._regime_intensity(net_gamma)

            sig = self._build_signal_v2(
                signal_type="SHORT",
                price=underlying_price,
                confidence=confidence,
                net_gamma=net_gamma,
                iv_atm=iv_atm,
                iv_decline=iv_crash_score,
                iv_crash_score=iv_crash_score,
                wall=wall_above,
                regime=regime,
                rolling_data=rolling_data,
                price_percentile=price_high,
                stop_price=stop_price,
                stop_type=stop_type,
                iv_skew=iv_skew,
                iv_skew_roc=iv_skew_roc,
                gamma_density_current=gamma_density_current,
                gamma_density_mean=gamma_density_mean,
                gamma_density_decline_pct=gamma_density_decline_pct,
                conviction_iv=conviction_iv,
                option_volume=option_volume,
                regime_intensity=regime_intensity,
            )
            if sig:
                signals.append(sig)

        return signals

    def _evaluate_long(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
        greeks_summary: Dict[str, Any],
        underlying_price: float,
    ) -> List[Signal]:
        """Evaluate LONG direction independently.
        Returns list of signals (may be empty).
        """
        signals: List[Signal] = []
        price_low = self._check_price_low(rolling_data)
        if price_low <= 0:
            return signals

        iv_expanding, iv_atm, iv_expand_score = self._check_iv_expanding(
            gex_calc, rolling_data, underlying_price,
        )
        normalized_gamma = gex_calc.get_normalized_net_gamma()
        if not iv_expanding:
            return signals

        # Soft gamma direction score: negative gamma contributes, positive = 0
        gamma_dir_score = max(0.0, min(1.0, -normalized_gamma / 10.0))

        skew_score = self._score_iv_skew_acceleration(
            gex_calc, rolling_data, underlying_price, "LONG",
        )

        density_score = self._score_gamma_density_decline(
            gex_calc, rolling_data, underlying_price,
        )

        walls = gex_calc.get_gamma_walls(threshold=500000)
        wall_below = None
        for wall in walls:
            if wall["strike"] < underlying_price and wall["side"] == "put":
                wall_below = wall
                break

        stop_price, stop_type = self._compute_wall_based_stop(
            underlying_price, "LONG", gex_calc,
        )

        iv_skew, iv_skew_roc = self._get_skew_data(
            gex_calc, rolling_data, underlying_price, "LONG",
        )
        confidence = self._compute_confidence_v2(
            price_low, net_gamma, wall_below, regime,
            underlying_price, greeks_summary,
            iv_score=iv_expand_score,
            skew_roc=iv_skew_roc,
            skew_score=skew_score,
            density_score=density_score,
            gamma_dir_score=gamma_dir_score,
        )

        if confidence >= MIN_CONFIDENCE:
            gamma_density_current, gamma_density_mean, gamma_density_decline_pct = (
                self._get_gamma_density_data(rolling_data)
            )
            conviction_iv, option_volume = self._get_conviction_data(
                greeks_summary, underlying_price, "LONG",
            )
            regime_intensity = self._regime_intensity(net_gamma)

            sig = self._build_signal_v2(
                signal_type="LONG",
                price=underlying_price,
                confidence=confidence,
                net_gamma=net_gamma,
                iv_atm=iv_atm,
                iv_decline=iv_expand_score,
                iv_crash_score=iv_expand_score,
                wall=wall_below,
                regime=regime,
                rolling_data=rolling_data,
                price_percentile=1.0 - price_low,
                stop_price=stop_price,
                stop_type=stop_type,
                iv_skew=iv_skew,
                iv_skew_roc=iv_skew_roc,
                gamma_density_current=gamma_density_current,
                gamma_density_mean=gamma_density_mean,
                gamma_density_decline_pct=gamma_density_decline_pct,
                conviction_iv=conviction_iv,
                option_volume=option_volume,
                regime_intensity=regime_intensity,
            )
            if sig:
                signals.append(sig)

        return signals

    # ------------------------------------------------------------------
    # v1 checks (kept for backwards compat)
    # ------------------------------------------------------------------

    def _check_price_high(self, rolling_data: Dict[str, Any]) -> float:
        """Check if price is at a high in the 30m rolling window."""
        window = rolling_data.get(KEY_PRICE_30M)
        if window is None or window.count < MIN_PRICE_POINTS:
            return 0.0
        latest = window.latest
        if latest is None:
            return 0.0
        percentile = window.percentile_rank(latest)
        if percentile is None:
            return 0.0
        if percentile >= PRICE_PERCENTILE_THRESHOLD:
            return percentile
        return 0.0

    def _check_price_low(self, rolling_data: Dict[str, Any]) -> float:
        """Check if price is at a low in the 30m rolling window."""
        window = rolling_data.get(KEY_PRICE_30M)
        if window is None or window.count < MIN_PRICE_POINTS:
            return 0.0
        latest = window.latest
        if latest is None:
            return 0.0
        percentile = window.percentile_rank(latest)
        if percentile is None:
            return 0.0
        if percentile <= (1.0 - PRICE_PERCENTILE_THRESHOLD):
            return 1.0 - percentile
        return 0.0

    def _check_iv_crashing(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        price: float,
    ) -> tuple:
        """Check if IV is crashing at the nearest ATM strike.
        Returns (is_crashing: bool, iv_atm: float, decline_score: float).
        decline_score is 0.0-1.0 based on how far below rolling avg.
        """
        atm_strike = self._find_atm_strike(gex_calc, price)
        if atm_strike is None:
            return False, 0.0, 0.0
        current_iv = gex_calc.get_iv_by_strike(atm_strike)
        if current_iv is None:
            return False, 0.0, 0.0
        iv_window = rolling_data.get(f"iv_{atm_strike}_5m")
        if iv_window is None or iv_window.count < MIN_IV_POINTS:
            return False, 0.0, 0.0
        latest = iv_window.latest
        avg = iv_window.mean
        if latest is None or avg is None or avg == 0:
            return False, 0.0, 0.0
        decline = 1.0 - (latest / avg)
        is_crashing = latest < avg * IV_DECLINE_RATIO
        max_decline = 1.0 - IV_DECLINE_RATIO
        decline_score = decline / max_decline if max_decline > 0 else 0.0
        decline_score = max(0.0, min(1.0, decline_score))
        return is_crashing, current_iv, decline_score

    def _check_iv_expanding(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        price: float,
    ) -> tuple:
        """Check if IV is expanding at the nearest ATM strike.
        Returns (is_expanding: bool, iv_atm: float, expand_score: float).
        expand_score is 0.0-1.0 based on how far above rolling avg.
        """
        atm_strike = self._find_atm_strike(gex_calc, price)
        if atm_strike is None:
            return False, 0.0, 0.0
        current_iv = gex_calc.get_iv_by_strike(atm_strike)
        if current_iv is None:
            return False, 0.0, 0.0
        iv_window = rolling_data.get(f"iv_{atm_strike}_5m")
        if iv_window is None or iv_window.count < MIN_IV_POINTS:
            return False, 0.0, 0.0
        latest = iv_window.latest
        avg = iv_window.mean
        if latest is None or avg is None or avg == 0:
            return False, 0.0, 0.0
        expansion = (latest / avg) - 1.0
        is_expanding = latest > avg / IV_DECLINE_RATIO
        threshold_expansion = (1.0 / IV_DECLINE_RATIO) - 1.0
        expand_score = expansion / (threshold_expansion * 2) if threshold_expansion > 0 else 0.0
        expand_score = max(0.0, min(1.0, expand_score))
        return is_expanding, current_iv, expand_score

    def _find_atm_strike(self, gex_calc: Any, price: float) -> Optional[float]:
        """Find the nearest strike in the gamma ladder to the current price."""
        return gex_calc.get_atm_strike(price)

    # ------------------------------------------------------------------
    # v2: IV Skew Acceleration
    # ------------------------------------------------------------------

    def _score_iv_skew_acceleration(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        price: float,
        signal_type: str,
    ) -> float:
        """
        Score IV skew acceleration on a 0.0–1.0 scale.

        Always uses OTM Put skew (strike below ATM) regardless of signal direction.
        Returns 0.0 if skew ROC <= 0, otherwise min(1.0, skew_roc / 0.20).
        """
        atm_strike = gex_calc.get_atm_strike(price)
        if atm_strike is None:
            return 0.0

        # Get current ATM IV
        atm_iv = gex_calc.get_iv_by_strike(atm_strike)
        if atm_iv is None or atm_iv <= 0:
            return 0.0

        # OTM Put skew: strike below ATM (always use put skew regardless of signal direction)
        otm_strike = atm_strike * (1.0 - IV_SKEW_OTM_PCT)

        otm_iv = gex_calc.get_iv_by_strike(otm_strike)
        if otm_iv is None or otm_iv <= 0:
            return 0.0

        # Current skew
        current_skew = otm_iv - atm_iv

        # Read skew from rolling window
        skew_window = rolling_data.get(KEY_IV_SKEW_GRADIENT_5M)
        if skew_window is None or skew_window.count < IV_SKEW_ROC_WINDOW:
            return 0.0

        # Get skew value from ~5 ticks ago
        skew_history = skew_window.values
        if len(skew_history) < IV_SKEW_ROC_WINDOW + 1:
            return 0.0

        skew_old = skew_history[-(IV_SKEW_ROC_WINDOW + 1)]
        if skew_old is None or skew_old == 0:
            return 0.0

        # Compute ROC
        skew_roc = (current_skew - skew_old) / abs(skew_old)

        # Soft score: 0.0 if skew moving wrong direction, otherwise normalize
        if skew_roc <= 0:
            return 0.0
        return min(1.0, skew_roc / 0.20)

    def _get_skew_data(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        price: float,
        signal_type: str,
    ) -> tuple[float, float]:
        """Get current skew and skew ROC for metadata."""
        atm_strike = gex_calc.get_atm_strike(price)
        if atm_strike is None:
            return 0.0, 0.0

        atm_iv = gex_calc.get_iv_by_strike(atm_strike)
        if atm_iv is None or atm_iv <= 0:
            return 0.0, 0.0

        # Always use put skew (strike below ATM)
        otm_strike = atm_strike * (1.0 - IV_SKEW_OTM_PCT)

        otm_iv = gex_calc.get_iv_by_strike(otm_strike)
        if otm_iv is None or otm_iv <= 0:
            return 0.0, 0.0

        current_skew = otm_iv - atm_iv

        skew_window = rolling_data.get(KEY_IV_SKEW_GRADIENT_5M)
        skew_roc = 0.0
        if skew_window is not None and skew_window.count >= IV_SKEW_ROC_WINDOW + 1:
            skew_history = skew_window.values
            if len(skew_history) >= IV_SKEW_ROC_WINDOW + 1:
                skew_old = skew_history[-(IV_SKEW_ROC_WINDOW + 1)]
                if skew_old is not None and skew_old != 0:
                    skew_roc = (current_skew - skew_old) / abs(skew_old)

        return current_skew, skew_roc

    # ------------------------------------------------------------------
    # v2: Gamma Density Gradient
    # ------------------------------------------------------------------

    def _score_gamma_density_decline(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        price: float,
    ) -> float:
        """
        Score gamma density decline on a 0.0–1.0 scale.

        Normalizes the decline relative to rolling mean:
        - 50% decline → 1.0
        - 25% decline → 0.5
        - 0% decline → 0.0

        Returns 0.0 if rolling_mean is None or zero.
        """
        greeks_summary = gex_calc.get_greeks_summary()
        if not greeks_summary:
            return 0.0

        # Compute current gamma density
        current_density = self._compute_gamma_density(greeks_summary, price)

        # Read gamma density from rolling window
        density_window = rolling_data.get(KEY_GAMMA_DENSITY_5M)
        if density_window is None or density_window.count < 5:
            return 0.0

        rolling_mean = density_window.mean
        if rolling_mean is None or rolling_mean == 0:
            return 0.0

        # Normalize the decline percentage
        decline_pct = 1.0 - (current_density / rolling_mean)
        decline_pct = max(0.0, decline_pct)  # cap at 0.0 if negative
        score = min(1.0, decline_pct / 0.50)  # 50% decline → 1.0
        return score

    def _compute_gamma_density(
        self,
        greeks_summary: Dict[str, Any],
        price: float,
    ) -> float:
        """Sum of |gamma| for strikes within ±1% of price."""
        density = 0.0
        for strike_str, strike_data in greeks_summary.items():
            try:
                strike = float(strike_str)
            except (ValueError, TypeError):
                continue
            distance = abs(strike - price) / price
            if distance <= GAMMA_DENSITY_WINDOW_PCT:
                call_gamma = strike_data.get("call_gamma", 0.0)
                put_gamma = strike_data.get("put_gamma", 0.0)
                density += abs(call_gamma) + abs(put_gamma)
        return density

    def _get_gamma_density_data(
        self,
        rolling_data: Dict[str, Any],
    ) -> tuple[float, float, float]:
        """Get gamma density current, mean, and decline pct for metadata."""
        density_window = rolling_data.get(KEY_GAMMA_DENSITY_5M)
        if density_window is None:
            return 0.0, 0.0, 0.0

        current = density_window.latest or 0.0
        mean_val = density_window.mean or 0.0
        decline_pct = 0.0
        if mean_val > 0:
            decline_pct = 1.0 - (current / mean_val)
        return current, mean_val, decline_pct

    # ------------------------------------------------------------------
    # v2: Volume-Weighted IV (Conviction)
    # ------------------------------------------------------------------

    def _compute_conviction_iv(self, iv_change: float, volume: int) -> float:
        """
        Weight IV change by log(volume) for conviction.

        If volume < IV_VOLUME_MIN → return 0.0 (insufficient conviction).
        """
        if volume < IV_VOLUME_MIN:
            return 0.0
        return iv_change * math.log(volume + 1)

    def _get_conviction_data(
        self,
        greeks_summary: Dict[str, Any],
        price: float,
        signal_type: str,
    ) -> tuple[float, int]:
        """Get conviction_iv and option_volume for metadata."""
        atm_strike = None
        # Find ATM strike from greeks_summary keys
        best_dist = float("inf")
        for strike_str in greeks_summary:
            try:
                strike = float(strike_str)
                dist = abs(strike - price)
                if dist < best_dist:
                    best_dist = dist
                    atm_strike = strike
            except (ValueError, TypeError):
                continue

        if atm_strike is None:
            return 0.0, 0

        strike_data = greeks_summary.get(str(atm_strike), {})
        if signal_type == "SHORT":
            volume = strike_data.get("put_volume", 0)
        else:
            volume = strike_data.get("call_volume", 0)

        # Use a placeholder IV change — we don't have the exact iv_change here,
        # but we use the raw volume for the metadata field
        return 0.0, volume

    # ------------------------------------------------------------------
    # v2: Wall-Based Stops
    # ------------------------------------------------------------------

    def _compute_wall_based_stop(
        self,
        price: float,
        signal_type: str,
        gex_calc: Any,
    ) -> tuple[float, str]:
        """
        Compute dynamic stop based on nearest gamma wall.

        For SHORT: stop just beyond nearest call wall above price.
        For LONG: stop just beyond nearest put wall below price.

        Returns (stop_price, stop_type) where stop_type is "wall" or "fixed".
        """
        walls = gex_calc.get_gamma_walls(threshold=500000)

        if signal_type == "SHORT":
            # Find nearest call wall above price within max distance
            best_wall = None
            best_dist = float("inf")
            for wall in walls:
                if wall["side"] == "call" and wall["strike"] > price:
                    dist = (wall["strike"] - price) / price
                    if dist <= WALL_STOP_MAX_DISTANCE_PCT and dist < best_dist:
                        best_dist = dist
                        best_wall = wall

            if best_wall is not None:
                stop = best_wall["strike"] * (1.0 + WALL_STOP_BUFFER_PCT)
                return stop, "wall"
            else:
                return price * (1.0 + FALLBACK_STOP_PCT), "fixed"
        else:  # LONG
            # Find nearest put wall below price within max distance
            best_wall = None
            best_dist = float("inf")
            for wall in walls:
                if wall["side"] == "put" and wall["strike"] < price:
                    dist = (price - wall["strike"]) / price
                    if dist <= WALL_STOP_MAX_DISTANCE_PCT and dist < best_dist:
                        best_dist = dist
                        best_wall = wall

            if best_wall is not None:
                stop = best_wall["strike"] * (1.0 - WALL_STOP_BUFFER_PCT)
                return stop, "wall"
            else:
                return price * (1.0 - FALLBACK_STOP_PCT), "fixed"

    # ------------------------------------------------------------------
    # v2: Confidence Computation (10 components)
    # ------------------------------------------------------------------

    def _compute_confidence_v2(
        self,
        price_percentile: float,
        net_gamma: float,
        wall: Optional[Dict[str, Any]],
        regime: str,
        price: float,
        greeks_summary: Dict[str, Any],
        iv_score: float = 0.0,
        skew_roc: float = 0.0,
        skew_score: float = 0.0,
        density_score: float = 0.0,
        gamma_dir_score: float = 0.0,
    ) -> float:
        """Combine all factors into confidence score (Family A simple average).
        10 components, each normalized to 0.0-1.0.
        """
        def normalize(val, vmin, vmax):
            return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

        # 1. Price extremeness: price_percentile from threshold→1.0
        c1 = normalize(price_percentile, PRICE_PERCENTILE_THRESHOLD, 1.0)

        # 2. Net gamma magnitude: abs(net_gamma) from 0→5M
        c2 = normalize(abs(net_gamma), 0.0, 5000000.0)

        # 3. Wall proximity: wall GEX from 0→5M
        wall_gex = 0.0
        if wall:
            wall_gex = abs(wall.get("gex", 0))
        c3 = normalize(wall_gex, 0.0, 5000000.0)

        # 4. Volume conviction: total_volume from 0→100k
        total_volume = 0.0
        if greeks_summary:
            for strike_data in greeks_summary.values():
                call_vol = strike_data.get("call_volume", 0)
                put_vol = strike_data.get("put_volume", 0)
                total_volume += call_vol + put_vol
        c4 = normalize(total_volume, 0.0, 100000.0)

        # 5. Regime alignment: normalize regime intensity 0.05→0.15
        regime_intensity = 0.0
        if regime:
            if regime == "NEGATIVE":
                regime_intensity = 0.15
            elif regime == "POSITIVE":
                regime_intensity = 0.10
            else:
                regime_intensity = 0.05
        c5 = normalize(regime_intensity, 0.05, 0.15)

        # 6. IV crash/expand score (from _check_iv_crashing/_check_iv_expanding)
        c6 = iv_score

        # 7. IV skew ROC score (normalize from 0→0.20)
        c7 = min(1.0, skew_roc / 0.20)

        # 8. IV skew acceleration score (from _score_iv_skew_acceleration)
        c8 = skew_score

        # 9. Gamma density decline score (from _score_gamma_density_decline)
        c9 = density_score

        # 10. Gamma direction score (from normalized net gamma)
        c10 = gamma_dir_score

        confidence = (c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10) / 10.0
        return min(1.0, max(0.0, confidence))

    def _price_extremeness_confidence(self, price_percentile: float) -> float:
        """Price extremeness: 0.0–0.15."""
        # price_percentile is 0.75 at p25, 1.0 at p0 for LONG
        # or 0.70 at p70, 1.0 at p100 for SHORT
        if price_percentile <= 0:
            return 0.0
        # Scale: 0.75 → 0.0, 1.0 → 0.15
        return min(0.15, max(0.0, 0.15 * (price_percentile - 0.75) / (1.0 - 0.75)))

    def _conviction_iv_confidence(
        self,
        greeks_summary: Dict[str, Any],
        price: float,
    ) -> float:
        """Volume-weighted IV: 0.0–0.10."""
        # Find ATM strike and get volume
        best_dist = float("inf")
        atm_volume = 0
        for strike_str, strike_data in greeks_summary.items():
            try:
                strike = float(strike_str)
                dist = abs(strike - price)
                if dist < best_dist:
                    best_dist = dist
                    total_vol = (
                        strike_data.get("call_volume", 0)
                        + strike_data.get("put_volume", 0)
                    )
                    atm_volume = total_vol
            except (ValueError, TypeError):
                continue

        if atm_volume < IV_VOLUME_MIN:
            return 0.0

        # Scale: log volume → confidence
        log_vol = math.log(atm_volume + 1)
        # Normalize: log(100) ≈ 4.6 → 0.0, log(100000) ≈ 11.5 → 0.10
        conf = 0.10 * min(1.0, (log_vol - math.log(IV_VOLUME_MIN + 1))
                          / (math.log(100000) - math.log(IV_VOLUME_MIN + 1)))
        return min(0.10, max(0.0, conf))

    def _gamma_magnitude_confidence(self, net_gamma: float) -> float:
        """Net gamma magnitude: 0.0–0.10."""
        abs_gamma = abs(net_gamma)
        # Scale: 0 → 0.0, 5M → 0.10
        return min(0.10, 0.10 * min(1.0, abs_gamma / 5_000_000))

    def _wall_proximity_confidence(
        self,
        wall: Optional[Dict[str, Any]],
    ) -> float:
        """Wall proximity: 0.0–0.10."""
        if wall is None:
            return 0.0
        # Near wall = higher confidence
        return 0.10

    def _regime_intensity_confidence(self, net_gamma: float) -> float:
        """Regime intensity: 0.05–0.15 based on gamma magnitude."""
        abs_gamma = abs(net_gamma)
        # Scale: 0 → 0.05, 5M → 0.15
        return 0.05 + 0.10 * min(1.0, abs_gamma / 5_000_000)

    def _regime_intensity(self, net_gamma: float) -> float:
        """Regime intensity value for metadata (same logic as above)."""
        abs_gamma = abs(net_gamma)
        return round(0.05 + 0.10 * min(1.0, abs_gamma / 5_000_000), 3)

    # ------------------------------------------------------------------
    # v2: Signal Builder
    # ------------------------------------------------------------------

    def _build_signal_v2(
        self,
        signal_type: str,
        price: float,
        confidence: float,
        net_gamma: float,
        iv_atm: Optional[float],
        iv_decline: float,
        iv_crash_score: float = 0.0,
        wall: Optional[Dict[str, Any]] = None,
        regime: str = "",
        rolling_data: Dict[str, Any] = None,
        price_percentile: Optional[float] = None,
        stop_price: float = 0.0,
        stop_type: str = "",
        iv_skew: float = 0.0,
        iv_skew_roc: float = 0.0,
        gamma_density_current: float = 0.0,
        gamma_density_mean: float = 0.0,
        gamma_density_decline_pct: float = 0.0,
        conviction_iv: float = 0.0,
        option_volume: int = 0,
        regime_intensity: float = 0.0,
    ) -> Optional[Signal]:
        """Build a Signal object with v2 metadata."""
        entry = price

        if signal_type == "SHORT":
            risk = stop_price - entry
            price_window = rolling_data.get(KEY_PRICE_30M)
            rolling_mean = price_window.mean if price_window else entry
            target = entry - (entry - rolling_mean) * TARGET_RISK_MULT
            target = max(target, stop_price - risk * 0.1)

            wall_info = ""
            if wall:
                wall_info = f" | nearest call wall at {wall['strike']}"

            price_window = rolling_data.get(KEY_PRICE_30M)
            trend = price_window.trend if price_window else "UNKNOWN"

            return Signal(
                direction=Direction.SHORT,
                confidence=round(confidence, 3),
                entry=round(entry, 2),
                stop=round(stop_price, 2),
                target=round(target, 2),
                strategy_id=self.strategy_id,
                reason=(
                    f"IV-GEX divergence v2: price at high + IV skew accel "
                    f"(Δ{iv_decline:.1%}) + positive gamma {net_gamma:.0f}"
                    f" | stop:{stop_type}@{stop_price:.2f}{wall_info}"
                ),
                metadata={
                    # v1 fields (kept)
                    "price_percentile": round(price_percentile, 3) if price_percentile is not None else None,
                    "iv_atm": round(iv_atm, 4) if iv_atm else None,
                    "iv_decline_pct": round(iv_decline, 4),
                    "iv_crash_score": round(iv_crash_score, 3),
                    "net_gamma": round(net_gamma, 2),
                    "wall_above_strike": wall["strike"] if wall else None,
                    "wall_above_gex": wall["gex"] if wall else None,
                    "regime": regime,
                    "trend": trend,
                    "risk": round(risk, 2),
                    "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
                    # v2 new fields
                    "iv_skew": round(iv_skew, 4),
                    "iv_skew_roc": round(iv_skew_roc, 4),
                    "gamma_density_current": round(gamma_density_current, 2),
                    "gamma_density_mean": round(gamma_density_mean, 2),
                    "gamma_density_decline_pct": round(gamma_density_decline_pct, 4),
                    "conviction_iv": round(conviction_iv, 4),
                    "option_volume": option_volume,
                    "stop_type": stop_type,
                    "stop_wall_strike": wall["strike"] if wall else None,
                    "regime_intensity": round(regime_intensity, 3),
                },
            )
        else:  # LONG
            risk = entry - stop_price
            price_window = rolling_data.get(KEY_PRICE_30M)
            rolling_mean = price_window.mean if price_window else entry
            target = entry + (rolling_mean - entry) * TARGET_RISK_MULT
            target = min(target, stop_price + risk * 0.1)

            wall_info = ""
            if wall:
                wall_info = f" | nearest put wall at {wall['strike']}"

            price_window = rolling_data.get(KEY_PRICE_30M)
            trend = price_window.trend if price_window else "UNKNOWN"

            return Signal(
                direction=Direction.LONG,
                confidence=round(confidence, 3),
                entry=round(entry, 2),
                stop=round(stop_price, 2),
                target=round(target, 2),
                strategy_id=self.strategy_id,
                reason=(
                    f"IV-GEX divergence v2: price at low + IV skew accel "
                    f"(Δ{iv_decline:.1%}) + negative gamma {net_gamma:.0f}"
                    f" | stop:{stop_type}@{stop_price:.2f}{wall_info}"
                ),
                metadata={
                    # v1 fields (kept)
                    "price_percentile": round(price_percentile, 3) if price_percentile is not None else None,
                    "iv_atm": round(iv_atm, 4) if iv_atm else None,
                    "iv_decline_pct": round(iv_decline, 4),
                    "iv_crash_score": round(iv_crash_score, 3),
                    "net_gamma": round(net_gamma, 2),
                    "wall_below_strike": wall["strike"] if wall else None,
                    "wall_below_gex": wall["gex"] if wall else None,
                    "regime": regime,
                    "trend": trend,
                    "risk": round(risk, 2),
                    "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
                    # v2 new fields
                    "iv_skew": round(iv_skew, 4),
                    "iv_skew_roc": round(iv_skew_roc, 4),
                    "gamma_density_current": round(gamma_density_current, 2),
                    "gamma_density_mean": round(gamma_density_mean, 2),
                    "gamma_density_decline_pct": round(gamma_density_decline_pct, 4),
                    "conviction_iv": round(conviction_iv, 4),
                    "option_volume": option_volume,
                    "stop_type": stop_type,
                    "stop_wall_strike": wall["strike"] if wall else None,
                    "regime_intensity": round(regime_intensity, 3),
                },
            )
