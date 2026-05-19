"""
strategies/full_data/prob_weighted_magnet.py — Prob-Weighted Magnet

Full-data (v2) strategy: uses ProbabilityITM + OI to detect stealth
accumulation before price reacts. When smart money is positioning at
specific strikes (high OI + rising delta/ProbITM) but price hasn't
moved yet, enter anticipatory positions.

Logic:
    - Scan strikes below/above price for high OI + rising delta
    - Price must be consolidating (narrow range, declining volume)
    - Net gamma positive required
    - Enter before price slices through the strike
    - Target = strike level

Entry (LONG):
    - Strikes below price with high OI + rising delta
    - Price consolidating + volume flat/declining
    - Net gamma positive

Entry (SHORT):
    - Strikes above price with high OI + falling delta
    - Price consolidating + volume flat/declining
    - Net gamma positive

Confidence factors:
    - OI concentration (higher = higher confidence)
    - Delta acceleration rate
    - Price consolidation tightness
    - Volume profile (declining = accumulation signal)
    - Distance to target strike

⚠️ **Open Interest Limitation**:
This strategy uses OI concentration thresholds (MIN_OI_CONCENTRATION = 2.0)
to filter qualifying strikes. The OI values are **relative** (1.0 per message)
because the TradeStation SSE stream greeks format does not include Open Interest.

**Impact**:
- MIN_OI_CONCENTRATION threshold (2.0) is in relative units, not contract counts
- Strikes with "high OI" are identified by relative activity levels
- Absolute OI thresholds would require REST API OI fetches

**Why It Still Works**:
The strategy combines **ProbabilityITM** (from stream greeks) with **relative OI**
to detect accumulation. Even with relative OI, strikes showing both high activity
(gamma/delta from stream) AND high ProbabilityITM indicate smart money positioning.
The relative OI serves as a proxy for "activity concentration" rather than exact
contract counts.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_window import RollingWindow
from strategies.rolling_keys import KEY_PRICE_5M, KEY_PRICE_30M, KEY_VOLUME_5M

logger = logging.getLogger("Syngex.Strategies.ProbWeightedMagnet")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default parameter values - can be overridden via self._params

# OI concentration threshold (relative units)
DEFAULT_MIN_OI_CONCENTRATION = 2.0          # Minimum total OI at a strike

# Price consolidation: 5m range must be < this % of 30m range
DEFAULT_CONSOLIDATION_RATIO = 0.50          # 50%

# Delta acceleration: delta change must exceed this ratio
DEFAULT_DELTA_ACCEL_RATIO = 1.05            # 5% change in delta

# Min net gamma for positive regime
DEFAULT_MIN_NET_GAMMA = 500000.0

# Stop and target
DEFAULT_STOP_PCT = 0.005                    # 0.5% stop
DEFAULT_TARGET_RISK_MULT = 1.5              # 1.5× risk for target

# Min confidence
DEFAULT_MIN_CONFIDENCE = 0.25
DEFAULT_MAX_CONFIDENCE = 0.80               # v2 cap

# Min data points
DEFAULT_MIN_DATA_POINTS = 3

# Volume trend check — these qualify as "no breakout yet"
DEFAULT_VALID_VOLUME_TRENDS = ("FLAT", "DOWN")


class ProbWeightedMagnet(BaseStrategy):
    """
    Prob-Weighted Magnet — Full-data (v2) strategy.

    Detects stealth accumulation by scanning the options chain for strikes
    where smart money is positioning (high OI + rising delta/ProbITM) while
    the underlying price consolidates. Enters anticipatory positions before
    price slices through the magnet strike.

    This is a slower strategy (15–45 min holds) — don't expect rapid signals.
    """

    strategy_id = "prob_weighted_magnet"
    layer = "full_data"

    def __init__(self):
        """Initialize strategy with configurable parameters."""
        super().__init__()
        self._params = {
            'min_oi_concentration': DEFAULT_MIN_OI_CONCENTRATION,
            'consolidation_ratio': DEFAULT_CONSOLIDATION_RATIO,
            'delta_accel_ratio': DEFAULT_DELTA_ACCEL_RATIO,
            'min_net_gamma': DEFAULT_MIN_NET_GAMMA,
            'stop_pct': DEFAULT_STOP_PCT,
            'target_risk_mult': DEFAULT_TARGET_RISK_MULT,
            'min_confidence': DEFAULT_MIN_CONFIDENCE,
            'max_confidence': DEFAULT_MAX_CONFIDENCE,
            'min_data_points': DEFAULT_MIN_DATA_POINTS,
            'valid_volume_trends': DEFAULT_VALID_VOLUME_TRENDS,
        }

    def _apply_params(self, data: Dict[str, Any]) -> None:
        """Apply parameter overrides from data dict if present."""
        if 'params' in data:
            self._params.update(data['params'])

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return magnet signals.

        Returns empty list when no stealth accumulation is detected.
        """
        # Apply parameter overrides
        self._apply_params(data)
        
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
        min_data_points = self._params.get('min_data_points', DEFAULT_MIN_DATA_POINTS)
        price_5m = rolling_data.get(KEY_PRICE_5M)
        price_30m = rolling_data.get(KEY_PRICE_30M)
        if price_5m is None or price_30m is None:
            return []
        if price_5m.count < min_data_points or price_30m.count < min_data_points:
            return []

        # Consolidation: 5m range must be < 40% of 30m range
        range_5m = price_5m.range
        range_30m = price_30m.range
        if range_5m is None or range_30m is None or range_30m == 0:
            return []
        consolidation_ratio = range_5m / range_30m
        min_data_points = self._params.get('min_data_points', DEFAULT_MIN_DATA_POINTS)
        consolidation_ratio_param = self._params.get('consolidation_ratio', DEFAULT_CONSOLIDATION_RATIO)
        if consolidation_ratio >= consolidation_ratio_param:
            # Price not consolidating — could be a breakout already
            return []

        # --- Volume check ---
        volume_5m = rolling_data.get(KEY_VOLUME_5M)
        if volume_5m is None or volume_5m.count < min_data_points:
            return []
        vol_trend = volume_5m.trend
        valid_volume_trends = self._params.get('valid_volume_trends', DEFAULT_VALID_VOLUME_TRENDS)
        if vol_trend not in valid_volume_trends:
            # Volume spiking up = breakout in progress, not accumulation
            return []

        # --- Net gamma check ---
        min_net_gamma = self._params.get('min_net_gamma', DEFAULT_MIN_NET_GAMMA)
        if net_gamma < min_net_gamma:
            return []

        # --- Scan for magnet strikes ---
        signals: List[Signal] = []

        long_sig = self._check_long(
            greeks_summary, underlying_price, net_gamma,
            consolidation_ratio, vol_trend, price_30m, data,
        )
        short_sig = self._check_short(
            greeks_summary, underlying_price, net_gamma,
            consolidation_ratio, vol_trend, price_30m, data,
        )

        if long_sig:
            signals.append(long_sig)
        if short_sig:
            signals.append(short_sig)

        return signals

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
    ) -> Optional[Signal]:
        """
        Detect stealth accumulation below price.

        Find strikes BELOW current price where:
        - Delta is rising (ProbITM proxy increasing)
        - OI concentration is high
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

        # Compute confidence
        confidence = self._compute_confidence(
            target, qualifying, price, net_gamma,
            consolidation_ratio, vol_trend, price_30m,
        )

        min_confidence = self._params.get('min_confidence', DEFAULT_MIN_CONFIDENCE)
        if confidence < min_confidence:
            return None

        # Build signal
        stop_pct = self._params.get('stop_pct', DEFAULT_STOP_PCT)
        target_risk_mult = self._params.get('target_risk_mult', DEFAULT_TARGET_RISK_MULT)
        stop = price * (1 - stop_pct)
        risk = price - stop
        target_price = price + (risk * target_risk_mult)

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target_price, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Stealth accumulation below price: magnet at {target_strike} "
                f"(OI={target['total_oi']:.0f}, delta={target['net_delta']:.2f}), "
                f"consolidation={consolidation_ratio:.2%}, vol={vol_trend}"
            ),
            metadata={
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
                "stop_pct": stop_pct,
                "target_risk_mult": target_risk_mult,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target_price - price) / risk, 2)
                    if risk > 0 else 0,
                "trend": price_30m.trend if price_30m else "UNKNOWN",
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
    ) -> Optional[Signal]:
        """
        Detect stealth distribution above price.

        Find strikes ABOVE current price where:
        - Delta is falling (ProbITM proxy decreasing)
        - OI concentration is high
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
            min_oi_concentration = self._params.get('min_oi_concentration', DEFAULT_MIN_OI_CONCENTRATION)
            if total_oi < min_oi_concentration:
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

        # Compute confidence
        confidence = self._compute_confidence(
            target, qualifying, price, net_gamma,
            consolidation_ratio, vol_trend, price_30m,
        )

        min_confidence = self._params.get('min_confidence', DEFAULT_MIN_CONFIDENCE)
        if confidence < min_confidence:
            return None

        # Build signal
        stop_pct = self._params.get('stop_pct', DEFAULT_STOP_PCT)
        target_risk_mult = self._params.get('target_risk_mult', DEFAULT_TARGET_RISK_MULT)
        stop = price * (1 + stop_pct)
        risk = stop - price
        target_price = price - (risk * target_risk_mult)

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target_price, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Stealth distribution above price: magnet at {target_strike} "
                f"(OI={target['total_oi']:.0f}, delta={target['net_delta']:.2f}), "
                f"consolidation={consolidation_ratio:.2%}, vol={vol_trend}"
            ),
            metadata={
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
                "stop_pct": stop_pct,
                "target_risk_mult": target_risk_mult,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target_price - price) / risk, 2)
                    if risk > 0 else 0,
                "trend": price_30m.trend if price_30m else "UNKNOWN",
            },
        )

    # ------------------------------------------------------------------
    # Confidence scoring
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        target: Dict[str, Any],
        qualifying: List[Dict[str, Any]],
        price: float,
        net_gamma: float,
        consolidation_ratio: float,
        vol_trend: str,
        price_30m: RollingWindow,
    ) -> float:
        """
        Compute confidence for a magnet signal.

        Factors (each 0–1, weighted):
        1. OI concentration at target strike (0.20–0.30)
        2. Delta acceleration rate (0.15–0.25)
        3. Price consolidation tightness (0.15–0.20)
        4. Volume profile (0.10–0.15)
        5. Distance to target (0.10–0.15)
        """
        total_oi = target["total_oi"]
        net_delta = target["net_delta"]
        distance_pct = target["distance_pct"]
        
        # Get parameters
        min_oi_concentration = self._params.get('min_oi_concentration', DEFAULT_MIN_OI_CONCENTRATION)
        delta_accel_ratio = self._params.get('delta_accel_ratio', DEFAULT_DELTA_ACCEL_RATIO)
        consolidation_ratio_param = self._params.get('consolidation_ratio', DEFAULT_CONSOLIDATION_RATIO)
        max_confidence = self._params.get('max_confidence', DEFAULT_MAX_CONFIDENCE)

        # 1. OI concentration (0.20–0.30)
        #    Normalize against max OI in qualifying set
        # Scale: min_oi_concentration = baseline, 10× that = full weight
        oi_scaled = min(1.0, (total_oi - min_oi_concentration) / (min_oi_concentration * 9))
        oi_component = 0.20 + 0.10 * oi_scaled

        # 2. Delta acceleration (0.15–0.25)
        #    Higher net_delta at the strike = stronger signal
        #    Normalize: delta > 0.5 = strong, > 0.1 = moderate
        delta_scaled = min(1.0, net_delta / 0.5)
        # Also factor in acceleration relative to other qualifying strikes
        if len(qualifying) > 1:
            avg_delta = sum(s["net_delta"] for s in qualifying) / len(qualifying)
            accel_ratio = net_delta / avg_delta if avg_delta > 0 else 1.0
            accel_scaled = min(1.0, (accel_ratio - 1.0) / (delta_accel_ratio - 1.0 + 0.5))
            delta_component = 0.15 + 0.10 * min(1.0, (delta_scaled + accel_scaled) / 2)
        else:
            delta_component = 0.15 + 0.10 * delta_scaled

        # 3. Price consolidation tightness (0.15–0.20)
        #    Tighter consolidation = more coiled = higher confidence
        #    consolidation_ratio < consolidation_ratio_param required; closer to 0 = tighter
        cons_scaled = 1.0 - (consolidation_ratio / consolidation_ratio_param)
        cons_component = 0.15 + 0.05 * max(0, cons_scaled)

        # 4. Volume profile (0.10–0.15)
        #    DOWN volume = accumulation signal (stronger)
        #    FLAT = moderate accumulation
        if vol_trend == "DOWN":
            vol_component = 0.15  # Strong accumulation signal
        elif vol_trend == "FLAT":
            vol_component = 0.12  # Moderate
        else:
            vol_component = 0.05  # Shouldn't reach here

        # 5. Distance to target (0.10–0.15)
        #    Closer target = higher probability of reaching
        #    Normalize: 0.5% = full weight, 3%+ = minimal
        dist_scaled = 1.0 - min(1.0, distance_pct / 0.03)
        dist_component = 0.10 + 0.05 * max(0, dist_scaled)

        confidence = (
            oi_component
            + delta_component
            + cons_component
            + vol_component
            + dist_component
        )

        return min(max_confidence, max(0.0, confidence))
