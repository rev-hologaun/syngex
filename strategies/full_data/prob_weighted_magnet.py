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

Confidence factors (7 components):
    1. OI concentration (soft — 0.10–0.15)
    2. Delta acceleration (hard gate — 0.0 or 0.20–0.30)
    3. Liquidity vacuum (hard gate — 0.0 or 0.15–0.20)
    4. Skew convergence (hard gate — 0.0 or 0.15–0.20)
    5. Consolidation tightness (soft — 0.10–0.15)
    6. Volume profile (soft — 0.05–0.10)
    7. Distance to target (soft — 0.05–0.10)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_window import RollingWindow
from strategies.rolling_keys import (
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
MIN_CONFIDENCE = 0.30

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
        net_gamma = data.get("net_gamma", 0.0)
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
        if consolidation_ratio >= CONSOLIDATION_RATIO:
            # Price not consolidating — could be a breakout already
            return []

        # --- Volume check ---
        volume_5m = rolling_data.get(KEY_VOLUME_5M)
        if volume_5m is None or volume_5m.count < MIN_DATA_POINTS:
            return []
        vol_trend = volume_5m.trend
        if vol_trend not in VALID_VOLUME_TRENDS:
            # Volume spiking up = breakout in progress, not accumulation
            return []

        # --- Net gamma check ---
        if net_gamma < MIN_NET_GAMMA:
            return []

        # --- Scan for magnet strikes ---
        signals: List[Signal] = []

        long_sig = self._check_long(
            greeks_summary, underlying_price, net_gamma,
            consolidation_ratio, vol_trend, price_30m, data, rolling_data, gex_calc,
        )
        short_sig = self._check_short(
            greeks_summary, underlying_price, net_gamma,
            consolidation_ratio, vol_trend, price_30m, data, rolling_data, gex_calc,
        )

        if long_sig:
            signals.append(long_sig)
        if short_sig:
            signals.append(short_sig)

        return signals

    # ------------------------------------------------------------------
    # v2 helper: Delta acceleration check
    # ------------------------------------------------------------------

    def _check_delta_acceleration(
        self, gex_calc: Any, magnet_strike: float, direction: str,
        rolling_data: Dict[str, Any],
    ) -> Optional[float]:
        """
        Check if delta at the magnet strike is accelerating.

        Returns delta_roc if acceleration confirmed, None otherwise.

        For LONG: delta_roc > 0.05 (delta accelerating up ≥5%)
        For SHORT: delta_roc < -0.05 (delta accelerating down ≥5%)
        """
        try:
            current_delta = gex_calc.get_delta_by_strike(magnet_strike)
            current_delta = current_delta.get("net_delta", 0.0) if isinstance(current_delta, dict) else 0.0
        except Exception:
            return None

        mag_window = rolling_data.get(KEY_MAGNET_DELTA_5M)
        if mag_window is None or mag_window.count < 5:
            return None  # Not enough data yet

        delta_5_ago = mag_window.values[-5] if len(mag_window.values) >= 5 else None
        if delta_5_ago is None or abs(delta_5_ago) < 1e-10:
            return None

        delta_roc = (current_delta - delta_5_ago) / abs(delta_5_ago)

        if direction == "LONG":
            if delta_roc > DELTA_ROC_THRESHOLD:
                return delta_roc
        else:  # SHORT
            if delta_roc < -DELTA_ROC_THRESHOLD:
                return delta_roc

        return None

    # ------------------------------------------------------------------
    # v2 helper: Liquidity vacuum check
    # ------------------------------------------------------------------

    def _check_liquidity_vacuum(
        self, data: Dict[str, Any], price: float, direction: str,
    ) -> bool:
        """
        Check if order book has thin liquidity on the breakout side.

        For LONG magnet: ask side should be thin (easy to break up)
        For SHORT magnet: bid side should be thin (easy to break down)

        Returns True if vacuum confirmed (thin side), False otherwise.
        """
        depth = data.get("market_depth_agg", {})
        if not depth:
            return True  # No depth data = pass (backwards compat)

        bids = depth.get("bids", [])
        asks = depth.get("asks", [])

        # Sum depth within ±0.2% of price
        bid_total = sum(b["size"] for b in bids if abs(b["price"] - price) / price < 0.002)
        ask_total = sum(a["size"] for a in asks if abs(a["price"] - price) / price < 0.002)

        if direction == "LONG":
            # For bullish magnet: ask side should be thin (easy to break up)
            if ask_total == 0:
                return True  # Free run — no asks
            ratio = ask_total / bid_total if bid_total > 0 else 0
            return ratio < LIQUIDITY_VACUUM_RATIO
        else:
            # For bearish magnet: bid side should be thin (easy to break down)
            if bid_total == 0:
                return True  # Free run — no bids
            ratio = bid_total / ask_total if ask_total > 0 else 0
            return ratio < LIQUIDITY_VACUUM_RATIO

    # ------------------------------------------------------------------
    # v2 helper: Skew convergence check
    # ------------------------------------------------------------------

    def _check_skew_convergence(
        self, rolling_data: Dict[str, Any], direction: str,
    ) -> bool:
        """
        Check if IV skew is normalizing toward the magnet direction.

        For LONG (bullish magnet): current_skew > avg_skew
            (skew normalizing from negative toward zero)
        For SHORT (bearish magnet): current_skew < avg_skew
            (skew normalizing from positive toward zero)

        Returns True if converging, False otherwise.
        """
        skew_window = rolling_data.get(KEY_IV_SKEW_5M)
        if skew_window is None or skew_window.count < 5:
            return True  # No skew data = pass (backwards compat)

        current_skew = skew_window.latest
        avg_skew = skew_window.mean
        if current_skew is None or avg_skew is None or abs(avg_skew) < 1e-10:
            return True

        if direction == "LONG":
            # Bullish magnet: skew should normalize from negative toward zero
            # current_skew should be > avg_skew (less negative)
            return current_skew > avg_skew
        else:
            # Bearish magnet: skew should normalize from positive toward zero
            # current_skew should be < avg_skew (less positive)
            return current_skew < avg_skew

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
    # v2 helper: Confidence scoring (7 components)
    # ------------------------------------------------------------------

    def _compute_confidence_v2(
        self,
        target: Dict[str, Any],
        qualifying: List[Dict[str, Any]],
        price: float,
        consolidation_ratio: float,
        vol_trend: str,
        delta_roc: Optional[float],
        liquidity_vacuum: bool,
        skew_converging: bool,
        depth_score=None,
    ) -> float:
        """
        Compute confidence for a magnet signal (Family A — 5 components).

        5 components, simple average:
            1. OI concentration (total_oi/max_oi, 0→1)
            2. Delta acceleration (abs delta_roc, 0→0.3)
            3. Liquidity vacuum (bool → 0 or 1)
            4. Consolidation tightness (consolidation_ratio, 0→1)
            5. Distance to target (inverted, 0→0.05)
        """
        # 1. OI concentration: total_oi/max_oi, 0→1
        total_oi = target["total_oi"]
        max_oi = max(s["total_oi"] for s in qualifying) if qualifying else total_oi
        oi_ratio = total_oi / max_oi if max_oi > 0 else 1.0
        c1 = normalize(oi_ratio, 0.0, 1.0)
        # 2. Delta acceleration: delta_roc from -0.3 to 0.3, use abs
        abs_d = abs(delta_roc) if delta_roc is not None else 0.0
        c2 = normalize(abs_d, 0.0, 0.3)
        # 3. Liquidity vacuum: bool → 0 or 1
        c3 = 1.0 if liquidity_vacuum else 0.0
        # 4. Consolidation tightness: consolidation_ratio 0→1, higher = tighter = higher
        c4 = normalize(consolidation_ratio, 0.0, 1.0)
        # 5. Distance to target: distance_pct 0→0.05, closer = higher, invert
        distance_pct = target["distance_pct"]
        c5 = 1.0 - normalize(distance_pct, 0.0, 0.05)
        confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
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

        # === v2 Hard Gates ===

        # 1. Delta acceleration check
        delta_roc = self._check_delta_acceleration(gex_calc, target_strike, "LONG", rolling_data)
        if delta_roc is None:
            return None  # Hard gate: delta not accelerating

        # 2. Liquidity vacuum check
        liquidity_vacuum = self._check_liquidity_vacuum(data, price, "LONG")
        if not liquidity_vacuum:
            return None  # Hard gate: no vacuum on ask side

        # 3. Skew convergence check
        skew_converging = self._check_skew_convergence(rolling_data, "LONG")
        if not skew_converging:
            return None  # Hard gate: skew not converging

        # === v2 Confidence scoring ===
        confidence = self._compute_confidence_v2(
            target, qualifying, price,
            consolidation_ratio, vol_trend,
            delta_roc, liquidity_vacuum, skew_converging,
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
        depth = data.get("market_depth_agg", {})
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
                f"(delta_roc={delta_roc:+.1%}, OI={target['total_oi']:.0f}), "
                f"liquidity_vacuum={liquidity_vacuum}, skew_converging={skew_converging}, "
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
                "delta_roc": round(delta_roc, 4),
                "liquidity_vacuum_ratio": round(vacuum_ratio, 3),
                "skew_roc": round(skew_roc, 4),
                "gamma_at_magnet": round(gamma_scale - 1.0, 4),  # raw gamma approx
                "gamma_scale": round(gamma_scale, 2),
                "target_mult": round(target_mult, 2),
                "skew_converging": skew_converging,
                "liquidity_vacuum": liquidity_vacuum,
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

        # === v2 Hard Gates ===

        # 1. Delta acceleration check
        delta_roc = self._check_delta_acceleration(gex_calc, target_strike, "SHORT", rolling_data)
        if delta_roc is None:
            return None  # Hard gate: delta not accelerating

        # 2. Liquidity vacuum check
        liquidity_vacuum = self._check_liquidity_vacuum(data, price, "SHORT")
        if not liquidity_vacuum:
            return None  # Hard gate: no vacuum on bid side

        # 3. Skew convergence check
        skew_converging = self._check_skew_convergence(rolling_data, "SHORT")
        if not skew_converging:
            return None  # Hard gate: skew not converging

        # === v2 Confidence scoring ===
        confidence = self._compute_confidence_v2(
            target, qualifying, price,
            consolidation_ratio, vol_trend,
            delta_roc, liquidity_vacuum, skew_converging,
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
        depth = data.get("market_depth_agg", {})
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
                f"(delta_roc={delta_roc:+.1%}, OI={target['total_oi']:.0f}), "
                f"liquidity_vacuum={liquidity_vacuum}, skew_converging={skew_converging}, "
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
                "delta_roc": round(delta_roc, 4),
                "liquidity_vacuum_ratio": round(vacuum_ratio, 3),
                "skew_roc": round(skew_roc, 4),
                "gamma_at_magnet": round(gamma_scale - 1.0, 4),  # raw gamma approx
                "gamma_scale": round(gamma_scale, 2),
                "target_mult": round(target_mult, 2),
                "skew_converging": skew_converging,
                "liquidity_vacuum": liquidity_vacuum,
            },
        )
