"""
strategies/full_data/prob_weighted_magnet.py — Prob-Weighted Magnet v2 (Velocity-Magnet)

Full-data strategy: uses ProbabilityITM + OI to detect stealth
accumulation before price reacts. Upgraded with velocity-magnet detection:

  - Delta acceleration (ROC) replaces static delta threshold
  - Liquidity vacuum confirms consolidation via order book depth
  - Skew convergence cross-references IV surface tilting
  - Gamma-weighted targets scale with magnet strength

Entry (LONG):
    - Strikes below price with high OI + rising delta (delta ROC > 5%)
    - Liquidity vacuum on ask side (thin asks = easy to break up)
    - Skew normalizing from negative toward zero
    - Price consolidating + volume flat/declining
    - Net gamma positive

Entry (SHORT):
    - Strikes above price with high OI + falling delta (delta ROC < -5%)
    - Liquidity vacuum on bid side (thin bids = easy to break down)
    - Skew normalizing from positive toward zero
    - Price consolidating + volume flat/declining
    - Net gamma positive

Confidence factors (10 components, simple average):
    Pre-gate scores (computed in evaluate, always available):
    1. OI concentration (0–1, total_oi/max_oi)
    2. Consolidation score (0–1, tighter = higher)
    3. Volume score (0–1, FLAT=1.0, DOWN=0.8, UP=0.2, SPIKE=0.0)
    4. Gamma score (0–1, higher net_gamma = higher)

    Post-gate scores (computed per-strike in _check_long/_check_short):
    5. Delta score (0–1, smoothed delta ROC)
    6. Liquidity score (0–1, liquidity vacuum ratio)
    7. Skew score (0–1, skew convergence magnitude)

    Structural scores (always computed):
    8. Distance to target (0–1, closer = higher)
    9. Consolidation ratio (0–1, tighter = higher)
    10. Net delta magnitude (0–1, abs(delta_roc) normalized)

    Formula: confidence = (c1 + c2 + ... + c10) / 10.0
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_window import RollingWindow
from strategies.rolling_keys import (
    KEY_MARKET_DEPTH_AGG,
    KEY_PRICE_5M,
    KEY_PRICE_30M,
    KEY_VOLUME_5M,
    KEY_IV_SKEW_5M,
    KEY_MAGNET_DELTA_5M,
)

logger = logging.getLogger("Syngex.Strategies.ProbWeightedMagnet")


def normalize(val: float, vmin: float, vmax: float) -> float:
    """Normalize a value to [0, 1] given a min/max range."""
    if vmax == vmin:
        return 0.5
    return max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# OI concentration threshold (relative units)
MIN_OI_CONCENTRATION = 2.0          # Minimum total OI at a strike

# Price consolidation: 5m range must be < this % of 30m range
CONSOLIDATION_RATIO = 0.50          # 50%

# Delta acceleration: delta change must exceed this ratio
DELTA_ACCEL_RATIO = 1.05            # 5% change in delta

# Min net gamma for positive regime
MIN_NET_GAMMA = 500000.0

# Stop and target
STOP_PCT = 0.005                    # 0.5% stop
TARGET_RISK_MULT = 1.5              # 1.5× risk for target (v1 fallback)

# Min confidence — raised from 0.25 to 0.35 for v2 hard gates
MIN_CONFIDENCE = 0.20

# Min data points
MIN_DATA_POINTS = 3

# Volume trend check — these qualify as "no breakout yet"
VALID_VOLUME_TRENDS = ("FLAT", "DOWN")

# v2 Velocity-Magnet parameters
DELTA_ROC_THRESHOLD = 0.05          # 5% ROC for delta acceleration
LIQUIDITY_VACUUM_RATIO = 0.30       # bid/ask ratio for vacuum check
GAMMA_SCALE_BASE = 2.0              # gamma value for 2.0× target scaling
TARGET_MULT_CAP = 3.0               # max target multiplier
TARGET_MIN_PCT = 0.005              # minimum 0.5% target


class ProbWeightedMagnet(BaseStrategy):
    """
    Prob-Weighted Magnet — Full-data (v2) Velocity-Magnet strategy.

    Detects stealth accumulation by scanning the options chain for strikes
    where smart money is positioning (high OI + rising delta/ProbITM) while
    the underlying price consolidates. Upgraded with:

    - Delta acceleration (ROC) — signals momentum before price moves
    - Liquidity vacuum — confirms consolidation via order book depth
    - Skew convergence — cross-references IV surface tilting
    - Gamma-weighted targets — scales with magnet strength

    This is a slower strategy (15–45 min holds) — don't expect rapid signals.
    """

    strategy_id = "prob_weighted_magnet"
    layer = "full_data"

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return magnet signals.

        Returns empty list when no stealth accumulation is detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma_normalized", 0.0)
        greeks_summary = data.get("greeks_summary", {})

        # --- Validate data ---
        if not greeks_summary:
            return []

        # --- Price consolidation check ---
        price_5m = rolling_data.get(KEY_PRICE_5M)
        price_30m = rolling_data.get(KEY_PRICE_30M)
        if price_5m is None or price_30m is None:
            return []
        if price_5m.count < MIN_DATA_POINTS or price_30m.count < MIN_DATA_POINTS:
            return []

        # Consolidation: 5m range must be < 40% of 30m range
        range_5m = price_5m.range
        range_30m = price_30m.range
        if range_5m is None or range_30m is None or range_30m == 0:
            return []
        consolidation_ratio = range_5m / range_30m
        # Soft score: tighter consolidation = higher score
        # 0.0 ratio → 1.0 score (perfect consolidation), 1.0+ ratio → 0.0
        consol_score = 1.0 - normalize(consolidation_ratio, 0.0, 1.0)

        # --- Volume check ---
        volume_5m = rolling_data.get(KEY_VOLUME_5M)
        if volume_5m is None or volume_5m.count < MIN_DATA_POINTS:
            return []
        vol_trend = volume_5m.trend
        # Soft score: FLAT best, DOWN close, UP penalized, SPIKE worst
        vol_trend_scores = {"FLAT": 1.0, "DOWN": 0.8, "UP": 0.2, "SPIKE": 0.0, "UNKNOWN": 0.5}
        vol_score = vol_trend_scores.get(vol_trend, 0.5)

        # --- Net gamma soft score ---
        # Soft score: 0 at 0 gamma, 0.5 at MIN_NET_GAMMA, 1.0 at 2×MIN_NET_GAMMA
        if net_gamma < 0:
            gamma_score = 0.0
        else:
            gamma_score = min(1.0, net_gamma / (MIN_NET_GAMMA * 2))

        # --- Scan for magnet strikes ---
        signals: List[Signal] = []

        long_sig = self._check_long(
            greeks_summary, underlying_price, net_gamma,
            consolidation_ratio, vol_trend, price_30m, data, rolling_data, gex_calc,
            consol_score, vol_score, gamma_score,
        )
        short_sig = self._check_short(
            greeks_summary, underlying_price, net_gamma,
            consolidation_ratio, vol_trend, price_30m, data, rolling_data, gex_calc,
            consol_score, vol_score, gamma_score,
        )

        if long_sig:
            signals.append(long_sig)
        if short_sig:
            signals.append(short_sig)

        return signals

    # ------------------------------------------------------------------
    # v2 helper: Delta acceleration score
    # ------------------------------------------------------------------

    def _score_delta_acceleration(
        self, gex_calc: Any, magnet_strike: float, direction: str,
        rolling_data: Dict[str, Any],
    ) -> float:
        """
        Score delta acceleration at the magnet strike on [0.0, 1.0].

        For LONG: higher delta_roc = higher score
        For SHORT: lower (more negative) delta_roc = higher score
        """
        try:
            current_delta = gex_calc.get_delta_by_strike(magnet_strike)
            current_delta = current_delta.get("net_delta", 0.0) if isinstance(current_delta, dict) else 0.0
        except Exception:
            return 0.0

        mag_window = rolling_data.get(KEY_MAGNET_DELTA_5M)
        if mag_window is None or mag_window.count < 5:
            return 0.0  # Not enough data yet

        delta_5_ago = mag_window.values[-5] if len(mag_window.values) >= 5 else None
        if delta_5_ago is None or abs(delta_5_ago) < 1e-10:
            return 0.0

        delta_roc = (current_delta - delta_5_ago) / abs(delta_5_ago)

        if direction == "LONG":
            if delta_roc > 0.05:
                return min(1.0, delta_roc / 0.30)
            elif delta_roc > 0.0:
                # Right direction but below threshold — partial score
                return delta_roc / 0.30
            else:
                # Wrong direction
                return 0.0
        else:  # SHORT
            if delta_roc < -0.05:
                return min(1.0, abs(delta_roc) / 0.30)
            elif delta_roc < 0.0:
                # Right direction but below threshold — partial score
                return abs(delta_roc) / 0.30
            else:
                # Wrong direction
                return 0.0

    # ------------------------------------------------------------------
    # v2 helper: Liquidity vacuum score
    # ------------------------------------------------------------------

    def _score_liquidity_vacuum(
        self, data: Dict[str, Any], price: float, direction: str,
    ) -> float:
        """
        Score liquidity vacuum on the breakout side on [0.0, 1.0].

        For LONG magnet: thin ask side = higher score
        For SHORT magnet: thin bid side = higher score

        0.0 = no vacuum (thick liquidity), 1.0 = free run (no liquidity)
        """
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        if not depth:
            return 0.5  # No depth data = neutral (backwards compat)

        bids = depth.get("bids", [])
        asks = depth.get("asks", [])

        # Sum depth within ±0.2% of price
        bid_total = sum(b["size"] for b in bids if abs(b["price"] - price) / price < 0.002)
        ask_total = sum(a["size"] for a in asks if abs(a["price"] - price) / price < 0.002)

        if direction == "LONG":
            # For bullish magnet: ask side should be thin (easy to break up)
            if ask_total == 0:
                return 1.0  # Free run — no asks
            ratio = ask_total / bid_total if bid_total > 0 else 0
        else:
            # For bearish magnet: bid side should be thin (easy to break down)
            if bid_total == 0:
                return 1.0  # Free run — no bids
            ratio = bid_total / ask_total if ask_total > 0 else 0

        # ratio 0.0 → 1.0 (perfect vacuum), ratio 0.5 → 0.0 (no vacuum), >0.5 → 0.0
        return max(0.0, 1.0 - normalize(ratio, 0.0, 0.5))

    # ------------------------------------------------------------------
    # v2 helper: Skew convergence score
    # ------------------------------------------------------------------

    def _score_skew_convergence(
        self, rolling_data: Dict[str, Any], direction: str,
    ) -> float:
        """
        Score IV skew convergence on [0.0, 1.0].

        For LONG (bullish magnet): current_skew > avg_skew
            (skew normalizing from negative toward zero)
        For SHORT (bearish magnet): current_skew < avg_skew
            (skew normalizing from positive toward zero)

        0.0 = no convergence, 1.0 = strong convergence
        """
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        if skew_window is None or skew_window.count < 5:
            return 0.5  # No skew data = neutral (backwards compat)

        current_skew = skew_window.latest
        avg_skew = skew_window.mean
        if current_skew is None or avg_skew is None or abs(avg_skew) < 1e-10:
            return 0.5

        if direction == "LONG":
            # Bullish magnet: skew should normalize from negative toward zero
            # current_skew should be > avg_skew (less negative)
            diff = current_skew - avg_skew
        else:
            # Bearish magnet: skew should normalize from positive toward zero
            # current_skew should be < avg_skew (less positive)
            diff = avg_skew - current_skew

        # Scale: diff 0.0 → 0.0, diff 0.05 → 1.0
        return min(1.0, max(0.0, diff / 0.05))

    # ------------------------------------------------------------------
    # v2 helper: Gamma-weighted target
    # ------------------------------------------------------------------

    def _compute_gamma_weighted_target(
        self, entry: float, risk: float, magnet_strike: float,
        gex_calc: Any, direction: str,
    ) -> Tuple[float, float, float]:
        """
        Compute gamma-weighted target price.

        Higher gamma at the magnet strike = wider target (more dealer hedging pressure).

        Returns (target_price, target_mult, gamma_scale).
        """
        try:
            gamma_at_strike = gex_calc.get_strike_net_gamma(magnet_strike)
        except Exception:
            gamma_at_strike = 0.0

        # Gamma scale: abs(0.5) → 1.25×, abs(2.0+) → 2.0×
        abs_gamma = abs(gamma_at_strike)
        gamma_scale = min(2.0, 1.0 + abs_gamma / GAMMA_SCALE_BASE)

        target_mult = 1.5 * gamma_scale
        target_mult = min(TARGET_MULT_CAP, target_mult)  # Cap at TARGET_MULT_CAP×

        if direction == "LONG":
            target = entry + (risk * target_mult)
        else:
            target = entry - (risk * target_mult)

        # Minimum TARGET_MIN_PCT target
        min_target = entry * TARGET_MIN_PCT
        if direction == "LONG":
            target = max(target, entry + min_target)
        else:
            target = min(target, entry - min_target)

        return target, target_mult, gamma_scale

    # ------------------------------------------------------------------
    # v2 helper: Confidence scoring (10 components)
    # ------------------------------------------------------------------

    def _compute_confidence_v2(
        self,
        target: Dict[str, Any],
        qualifying: List[Dict[str, Any]],
        price: float,
        consolidation_ratio: float,
        vol_trend: str,
        delta_roc: Optional[float] = None,
        liquidity_vacuum: bool = True,
        skew_converging: bool = True,
        depth_score=None,
        # New soft scores
        consolidation_score: float = 0.5,
        vol_score: float = 0.5,
        gamma_score: float = 0.5,
        delta_score: float = 0.0,
        liquidity_score: float = 0.5,
        skew_score: float = 0.5,
    ) -> float:
        """
        Compute confidence for a magnet signal (10 components, simple average).

        Pre-gate scores (from evaluate):
            1. OI concentration (total_oi/max_oi, 0→1)
            2. Consolidation score (0→1, tighter = higher)
            3. Volume score (0→1, FLAT=1.0, DOWN=0.8, UP=0.2, SPIKE=0.0)
            4. Gamma score (0→1, higher net_gamma = higher)

        Post-gate scores (from _check_long/_check_short):
            5. Delta score (0→1, smoothed delta ROC)
            6. Liquidity score (0→1, liquidity vacuum ratio)
            7. Skew score (0→1, skew convergence magnitude)

        Structural scores:
            8. Distance to target (0→1, closer = higher)
            9. Consolidation ratio (0→1, tighter = higher)
            10. Net delta magnitude (0→1, abs(delta_roc) normalized)

        Formula: confidence = (c1 + c2 + ... + c10) / 10.0
        """
        # 1. OI concentration: total_oi/max_oi, 0→1
        total_oi = target["total_oi"]
        max_oi = max(s["total_oi"] for s in qualifying) if qualifying else total_oi
        oi_ratio = total_oi / max_oi if max_oi > 0 else 1.0
        c1 = normalize(oi_ratio, 0.0, 1.0)

        # 2. Consolidation score (pre-gate): tighter = higher
        c2 = consolidation_score

        # 3. Volume score (pre-gate): FLAT=1.0, DOWN=0.8, UP=0.2, SPIKE=0.0
        c3 = vol_score

        # 4. Gamma score (pre-gate): higher net_gamma = higher
        c4 = gamma_score

        # 5. Delta score (post-gate): smoothed delta ROC
        c5 = delta_score

        # 6. Liquidity score (post-gate): liquidity vacuum ratio
        c6 = liquidity_score

        # 7. Skew score (post-gate): skew convergence magnitude
        c7 = skew_score

        # 8. Distance to target: distance_pct 0→0.05, closer = higher, invert
        distance_pct = target["distance_pct"]
        c8 = 1.0 - normalize(distance_pct, 0.0, 0.05)

        # 9. Consolidation ratio: 0→1, tighter = higher
        c9 = normalize(consolidation_ratio, 0.0, 1.0)

        # 10. Net delta magnitude: abs(delta_roc) normalized to 0→0.3 range
        abs_d = abs(delta_roc) if delta_roc is not None else 0.0
        c10 = normalize(abs_d, 0.0, 0.3)

        confidence = (c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10) / 10.0
        return min(1.0, max(0.0, confidence))

    # ------------------------------------------------------------------
    # LONG: Stealth accumulation below price
    # ------------------------------------------------------------------

    def _check_long(
        self,
        greeks_summary: Dict[str, Any],
        price: float,
        net_gamma: float,
        consolidation_ratio: float,
        vol_trend: str,
        price_30m: RollingWindow,
        data: Dict[str, Any],
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        consol_score: float = 0.0,
        vol_score: float = 0.5,
        gamma_score: float = 0.0,
    ) -> Optional[Signal]:
        """
        Detect stealth accumulation below price.

        Find strikes BELOW current price where:
        - Delta is accelerating up (delta ROC > 5%)
        - OI concentration is high
        - Liquidity vacuum on ask side
        - Skew converging (normalizing from negative)
        - Price is consolidating
        - Volume is flat or declining
        """
        # Collect qualifying strikes below price
        qualifying: List[Dict[str, Any]] = []

        for strike_str, strike_data in greeks_summary.items():
            try:
                strike = float(strike_str)
            except (ValueError, TypeError):
                continue

            # Must be below current price
            if strike >= price:
                continue

            # OI concentration check
            call_oi = strike_data.get("call_oi", 0)
            put_oi = strike_data.get("put_oi", 0)
            total_oi = call_oi + put_oi
            if total_oi < MIN_OI_CONCENTRATION:
                continue

            # Delta as ProbITM proxy — for calls below price,
            # rising call delta = rising ProbITM = accumulation
            call_delta = strike_data.get("call_delta_sum", 0)
            put_delta = strike_data.get("put_delta_sum", 0)

            # Use net delta magnitude as the delta proxy
            net_delta = abs(call_delta - put_delta)
            if net_delta <= 0:
                continue

            qualifying.append({
                "strike": strike,
                "total_oi": total_oi,
                "call_oi": call_oi,
                "put_oi": put_oi,
                "call_delta": call_delta,
                "put_delta": put_delta,
                "net_delta": net_delta,
                "distance_pct": (price - strike) / price,
            })

        if not qualifying:
            return None

        # Pick the strike with highest OI as the magnet target
        target = max(qualifying, key=lambda s: s["total_oi"])
        target_strike = target["strike"]

        # === v2 Soft Scores ===

        # 1. Delta acceleration score
        delta_score = self._score_delta_acceleration(gex_calc, target_strike, "LONG", rolling_data)

        # 2. Liquidity vacuum score
        liquidity_score = self._score_liquidity_vacuum(data, price, "LONG")

        # 3. Skew convergence score
        skew_score = self._score_skew_convergence(rolling_data, "LONG")

        # === v2 Confidence scoring (10 components) ===
        confidence = self._compute_confidence_v2(
            target, qualifying, price,
            consolidation_ratio, vol_trend,
            delta_score, liquidity_score, skew_score,
            consolidation_score=consol_score, vol_score=vol_score,
            gamma_score=gamma_score, delta_score=delta_score,
            liquidity_score=liquidity_score, skew_score=skew_score,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # === v2 Gamma-weighted target ===
        stop = price * (1 - STOP_PCT)
        risk = price - stop
        target_price, target_mult, gamma_scale = self._compute_gamma_weighted_target(
            price, risk, target_strike, gex_calc, "LONG",
        )

        # Compute skew ROC for metadata
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        skew_roc = 0.0
        if skew_window is not None and skew_window.count >= 2:
            first_skew = skew_window.values[0]
            if abs(first_skew) > 0:
                skew_roc = (skew_window.latest - first_skew) / abs(first_skew)

        # Compute liquidity vacuum ratio for metadata
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        vacuum_ratio = 0.0
        if depth:
            bids = depth.get("bids", [])
            asks = depth.get("asks", [])
            bid_total = sum(b["size"] for b in bids if abs(b["price"] - price) / price < 0.002)
            ask_total = sum(a["size"] for a in asks if abs(a["price"] - price) / price < 0.002)
            if bid_total > 0:
                vacuum_ratio = ask_total / bid_total

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target_price, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Velocity-Magnet LONG: delta accelerating at {target_strike} "
                f"(delta_roc={delta_score:+.1%}, OI={target['total_oi']:.0f}), "
                f"liquidity_vacuum={liquidity_score}, skew_converging={skew_score}, "
                f"delta_score={delta_score:.2f}, liq_score={liquidity_score:.2f}, skew_score={skew_score:.2f}, "
                f"consolidation={consolidation_ratio:.2%}, vol={vol_trend}"
            ),
            metadata={
                # === v1 fields (kept) ===
                "magnet_strike": target_strike,
                "oi_concentration": round(target["total_oi"], 2),
                "call_oi": round(target["call_oi"], 2),
                "put_oi": round(target["put_oi"], 2),
                "call_delta": round(target["call_delta"], 4),
                "put_delta": round(target["put_delta"], 4),
                "net_delta": round(target["net_delta"], 4),
                "distance_to_magnet_pct": round(target["distance_pct"], 4),
                "consolidation_ratio": round(consolidation_ratio, 4),
                "volume_trend": vol_trend,
                "net_gamma": round(net_gamma, 2),
                "qualifying_strikes": len(qualifying),
                "stop_pct": STOP_PCT,
                "target_risk_mult": round(target_mult, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target_price - price) / risk, 2)
                    if risk > 0 else 0,
                "trend": price_30m.trend if price_30m else "UNKNOWN",

                # === v2 new fields ===
                "delta_roc": round(delta_score, 4),
                "liquidity_vacuum_ratio": round(vacuum_ratio, 3),
                "skew_roc": round(skew_roc, 4),
                "gamma_at_magnet": round(gamma_scale - 1.0, 4),  # raw gamma approx
                "gamma_scale": round(gamma_scale, 2),
                "target_mult": round(target_mult, 2),
                "skew_converging": skew_score,
                "liquidity_vacuum": liquidity_score,

                # === v2 soft scores ===
                "delta_score": round(delta_score, 3),
                "liquidity_score": round(liquidity_score, 3),
                "skew_score": round(skew_score, 3),
            },
        )

    # ------------------------------------------------------------------
    # SHORT: Stealth distribution above price
    # ------------------------------------------------------------------

    def _check_short(
        self,
        greeks_summary: Dict[str, Any],
        price: float,
        net_gamma: float,
        consolidation_ratio: float,
        vol_trend: str,
        price_30m: RollingWindow,
        data: Dict[str, Any],
        rolling_data: Dict[str, Any],
        gex_calc: Any,
        consol_score: float = 0.0,
        vol_score: float = 0.5,
        gamma_score: float = 0.0,
    ) -> Optional[Signal]:
        """
        Detect stealth distribution above price.

        Find strikes ABOVE current price where:
        - Delta is falling (delta ROC < -5%)
        - OI concentration is high
        - Liquidity vacuum on bid side
        - Skew converging (normalizing from positive)
        - Price is consolidating
        - Volume is flat or declining
        """
        # Collect qualifying strikes above price
        qualifying: List[Dict[str, Any]] = []

        for strike_str, strike_data in greeks_summary.items():
            try:
                strike = float(strike_str)
            except (ValueError, TypeError):
                continue

            # Must be above current price
            if strike <= price:
                continue

            # OI concentration check
            call_oi = strike_data.get("call_oi", 0)
            put_oi = strike_data.get("put_oi", 0)
            total_oi = call_oi + put_oi
            if total_oi < MIN_OI_CONCENTRATION:
                continue

            # For puts above price, falling put delta = ProbITM falling = distribution
            call_delta = strike_data.get("call_delta_sum", 0)
            put_delta = strike_data.get("put_delta_sum", 0)

            # Use net delta magnitude as the delta proxy
            net_delta = abs(call_delta - put_delta)
            if net_delta <= 0:
                continue

            qualifying.append({
                "strike": strike,
                "total_oi": total_oi,
                "call_oi": call_oi,
                "put_oi": put_oi,
                "call_delta": call_delta,
                "put_delta": put_delta,
                "net_delta": net_delta,
                "distance_pct": (strike - price) / price,
            })

        if not qualifying:
            return None

        # Pick the strike with highest OI as the magnet target
        target = max(qualifying, key=lambda s: s["total_oi"])
        target_strike = target["strike"]

        # === v2 Soft Scores ===

        # 1. Delta acceleration score
        delta_score = self._score_delta_acceleration(gex_calc, target_strike, "SHORT", rolling_data)

        # 2. Liquidity vacuum score
        liquidity_score = self._score_liquidity_vacuum(data, price, "SHORT")

        # 3. Skew convergence score
        skew_score = self._score_skew_convergence(rolling_data, "SHORT")

        # === v2 Confidence scoring (10 components) ===
        confidence = self._compute_confidence_v2(
            target, qualifying, price,
            consolidation_ratio, vol_trend,
            delta_score, liquidity_score, skew_score,
            consolidation_score=consol_score, vol_score=vol_score,
            gamma_score=gamma_score, delta_score=delta_score,
            liquidity_score=liquidity_score, skew_score=skew_score,
        )

        if confidence < MIN_CONFIDENCE:
            return None

        # === v2 Gamma-weighted target ===
        stop = price * (1 + STOP_PCT)
        risk = stop - price
        target_price, target_mult, gamma_scale = self._compute_gamma_weighted_target(
            price, risk, target_strike, gex_calc, "SHORT",
        )

        # Compute skew ROC for metadata
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        skew_roc = 0.0
        if skew_window is not None and skew_window.count >= 2:
            first_skew = skew_window.values[0]
            if abs(first_skew) > 0:
                skew_roc = (skew_window.latest - first_skew) / abs(first_skew)

        # Compute liquidity vacuum ratio for metadata
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        vacuum_ratio = 0.0
        if depth:
            bids = depth.get("bids", [])
            asks = depth.get("asks", [])
            bid_total = sum(b["size"] for b in bids if abs(b["price"] - price) / price < 0.002)
            ask_total = sum(a["size"] for a in asks if abs(a["price"] - price) / price < 0.002)
            if ask_total > 0:
                vacuum_ratio = bid_total / ask_total

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target_price, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Velocity-Magnet SHORT: delta accelerating at {target_strike} "
                f"(delta_roc={delta_score:+.1%}, OI={target['total_oi']:.0f}), "
                f"liquidity_vacuum={liquidity_score}, skew_converging={skew_score}, "
                f"delta_score={delta_score:.2f}, liq_score={liquidity_score:.2f}, skew_score={skew_score:.2f}, "
                f"consolidation={consolidation_ratio:.2%}, vol={vol_trend}"
            ),
            metadata={
                # === v1 fields (kept) ===
                "magnet_strike": target_strike,
                "oi_concentration": round(target["total_oi"], 2),
                "call_oi": round(target["call_oi"], 2),
                "put_oi": round(target["put_oi"], 2),
                "call_delta": round(target["call_delta"], 4),
                "put_delta": round(target["put_delta"], 4),
                "net_delta": round(target["net_delta"], 4),
                "distance_to_magnet_pct": round(target["distance_pct"], 4),
                "consolidation_ratio": round(consolidation_ratio, 4),
                "volume_trend": vol_trend,
                "net_gamma": round(net_gamma, 2),
                "qualifying_strikes": len(qualifying),
                "stop_pct": STOP_PCT,
                "target_risk_mult": round(target_mult, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target_price - price) / risk, 2)
                    if risk > 0 else 0,
                "trend": price_30m.trend if price_30m else "UNKNOWN",

                # === v2 new fields ===
                "delta_roc": round(delta_score, 4),
                "liquidity_vacuum_ratio": round(vacuum_ratio, 3),
                "skew_roc": round(skew_roc, 4),
                "gamma_at_magnet": round(gamma_scale - 1.0, 4),  # raw gamma approx
                "gamma_scale": round(gamma_scale, 2),
                "target_mult": round(target_mult, 2),
                "skew_converging": skew_score,
                "liquidity_vacuum": liquidity_score,

                # === v2 soft scores ===
                "delta_score": round(delta_score, 3),
                "liquidity_score": round(liquidity_score, 3),
                "skew_score": round(skew_score, 3),
            },
        )
