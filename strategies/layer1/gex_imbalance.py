"""
strategies/layer1/gex_imbalance.py — GEX Imbalance

Call/Put GEX ratio reveals dealer bias independent of price action.

When options are structured such that calls dominate gamma, dealers must
short the underlying to hedge, creating a SHORT bias. Conversely, when
puts dominate, dealers must buy the underlying, creating a LONG bias.

Logic:
    - Calculate call GEX (sum of positive gamma per strike)
    - Calculate put GEX (sum of absolute negative gamma per strike)
    - Ratio = call_gex / put_gex
    - Put-heavy (ratio < 0.4): dealers buy to hedge → LONG bias
    - Call-heavy (ratio > 0.6): dealers short to hedge → SHORT bias
    - Neutral (0.4–0.6): no signal
    - Trade with VWAP trend confirmation

Entry:
    - Put-heavy + price above VWAP → LONG
    - Call-heavy + price below VWAP → SHORT

Exit:
    - Stop: 1% from entry
    - Target: 1.5% from entry (1:1.5 RR)

Confidence factors:
    - How extreme the ratio is (closer to 0 = higher long confidence;
      higher values beyond 1.0 = higher short confidence)
    - Regime alignment (positive regime + put-heavy = stronger long signal)
    - Data freshness (more messages = higher confidence)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_PRICE_30M

logger = logging.getLogger("Syngex.Strategies.GEXImbalance")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PUT_HEAVY_RATIO = 0.5        # < 0.5 → long bias
CALL_HEAVY_RATIO = 0.65      # > 0.65 → short bias
STRONG_PUT_RATIO = 0.25      # very strong long signal
STRONG_CALL_RATIO = 0.75     # very strong short signal
MIN_MESSAGES = 20            # minimum data points for signal quality
STOP_VOL_MULT = 2.5          # stop = 2.5x rolling price std dev
TARGET_RISK_MULT = 1.5       # target = 1.5x stop distance
MIN_CONFIDENCE = 0.55        # Minimum confidence to emit signal

# v2 Imbalance-Velocity constants
RATIO_ROC_WINDOW = 5         # Number of ticks back for ROC
RATIO_ROC_THRESHOLD = 0.10   # Minimum ROC to trigger (10% change)
REGIME_GAMMA_THRESHOLD = 500000
VWAP_DEVIATION_MIN_STD = 1.5


class GEXImbalance(BaseStrategy):
    """
    GEX Imbalance strategy: trade dealer hedging bias from call/put gamma ratio.

    Call-heavy GEX → dealers short hedge → price pressure down.
    Put-heavy GEX → dealers buy hedge → price pressure up.
    """

    strategy_id = "gex_imbalance"
    layer = "layer1"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._ratio_history: list = []  # List of (timestamp, ratio) tuples, capped at 20

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate GEX imbalance and return directional signals.

        Returns empty list when ratio is neutral or data is insufficient.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        ts = data.get("timestamp", time.time())
        symbol = data.get("symbol", "")

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        regime = data.get("regime", "")
        summary = gex_calc.get_summary()
        total_msgs = summary.get("total_messages", 0)

        # Require minimum data quality
        if total_msgs < MIN_MESSAGES:
            return []

        # Calculate call and put GEX from greeks summary
        call_gex, put_gex = self._calculate_gex_split(gex_calc)
        if call_gex + put_gex == 0:
            return []

        ratio = call_gex / put_gex if put_gex > 0 else 0.0

        # Determine bias direction
        bias, bias_strength = self._classify_bias(ratio, call_gex, put_gex)
        if bias is None:
            return []  # Neutral zone — no signal

        # Depth snapshot
        depth_snapshot = data.get("depth_snapshot")

        # Net gamma for regime intensity
        net_gamma = gex_calc.get_net_gamma()

        # Update ratio history for ROC
        self._update_ratio_history(ratio, ts)
        roc = self._get_ratio_roc()

        # ROC gating: velocity must align with bias direction
        if roc is not None:
            if bias == "LONG" and roc >= -RATIO_ROC_THRESHOLD:
                return []  # ROC not negative enough for LONG
            if bias == "SHORT" and roc <= RATIO_ROC_THRESHOLD:
                return []  # ROC not positive enough for SHORT

        # Depth alignment check
        depth_alignment = self._check_depth_alignment(bias, depth_snapshot)
        if depth_alignment is not None and depth_alignment < 0.4:
            return []  # Liquidity doesn't support bias

        # VWAP deviation check (distance-based)
        vwap_dev = self._check_vwap_deviation(underlying_price, rolling_data, bias)
        if vwap_dev is None or vwap_dev < VWAP_DEVIATION_MIN_STD:
            return []  # Not sufficiently deviated from VWAP

        # Regime intensity
        regime_intensity = self._compute_regime_intensity(regime, net_gamma, bias)

        # Compute confidence with 6-component scoring
        confidence = self._compute_confidence_v2(
            ratio, bias_strength, bias, regime_intensity, total_msgs,
            vwap_dev, roc, depth_alignment
        )
        if confidence < MIN_CONFIDENCE:
            return []

        # Build volatility-based stop/target
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window and price_window.count >= 10 and price_window.std is not None:
            vol = price_window.std
            if vol > 0:
                stop_distance = vol * STOP_VOL_MULT
            else:
                stop_distance = underlying_price * 0.005  # fallback: 0.5%
        else:
            stop_distance = underlying_price * 0.005  # fallback: 0.5%

        if bias == "LONG":
            stop = underlying_price - stop_distance
            target = underlying_price + stop_distance * TARGET_RISK_MULT
            direction = Direction.LONG
            side_label = "put-heavy"
        else:
            stop = underlying_price + stop_distance
            target = underlying_price - stop_distance * TARGET_RISK_MULT
            direction = Direction.SHORT
            side_label = "call-heavy"

        risk = abs(underlying_price - stop)
        reward = abs(target - underlying_price)

        # Add trend to metadata
        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        return [Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=underlying_price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"GEX {side_label}: call/put ratio={ratio:.3f}, "
                   f"call_gex={call_gex:.0f}, put_gex={put_gex:.0f}, "
                   f"regime={regime}",
            metadata={
                "ratio": round(ratio, 4),
                "call_gex": round(call_gex, 2),
                "put_gex": round(put_gex, 2),
                "bias": bias,
                "bias_strength": round(bias_strength, 3),
                "regime": regime,
                "trend": trend,
                "total_messages": total_msgs,
                "risk": round(risk, 2),
                "reward": round(reward, 2),
                "risk_reward_ratio": round(reward / risk, 2) if risk > 0 else 0,
            },
        )]

    # ------------------------------------------------------------------
    # GEX split calculation
    # ------------------------------------------------------------------

    def _calculate_gex_split(
        self, gex_calc: Any
    ) -> tuple:
        """
        Calculate total call GEX and put GEX from the greeks summary.

        Call gamma = positive gamma, Put gamma = absolute negative gamma.
        Returns (call_gex, put_gex) as floats.
        """
        greeks = gex_calc.get_greeks_summary()
        if not greeks:
            return (0.0, 0.0)

        call_gex = 0.0
        put_gex = 0.0

        for strike, bucket in greeks.items():
            net_gamma = bucket.get("net_gamma", 0.0)
            if net_gamma > 0:
                call_gex += net_gamma
            else:
                put_gex += abs(net_gamma)

        return (call_gex, put_gex)

    # ------------------------------------------------------------------
    # Bias classification
    # ------------------------------------------------------------------

    def _classify_bias(
        self, ratio: float, call_gex: float, put_gex: float
    ) -> tuple:
        """
        Classify the GEX imbalance into LONG bias, SHORT bias, or neutral.

        Returns (bias, strength) where bias is "LONG", "SHORT", or None.
        Strength is 0.0–1.0 indicating how extreme the imbalance is.
        """
        if put_gex == 0 and call_gex == 0:
            return (None, 0.0)

        # Put-heavy → LONG bias
        if ratio < PUT_HEAVY_RATIO:
            # Strength: how far below threshold
            strength = min(1.0, (PUT_HEAVY_RATIO - ratio) / PUT_HEAVY_RATIO)
            return ("LONG", strength)

        # Call-heavy → SHORT bias
        if ratio > CALL_HEAVY_RATIO:
            # Normalize against realistic upper bound (3.0 = calls 3x puts)
            strength = min(1.0, (ratio - CALL_HEAVY_RATIO) / (3.0 - CALL_HEAVY_RATIO))
            return ("SHORT", strength)

        # Neutral zone
        return (None, 0.0)

    # ------------------------------------------------------------------
    # GEX Velocity (ROC of Ratio)
    # ------------------------------------------------------------------

    def _update_ratio_history(self, ratio: float, ts: float) -> None:
        """Append (ts, ratio) to history, capped at 20 entries."""
        self._ratio_history.append((ts, ratio))
        if len(self._ratio_history) > 20:
            self._ratio_history.pop(0)

    def _get_ratio_roc(self) -> Optional[float]:
        """Rate-of-change of ratio over RATIO_ROC_WINDOW ticks."""
        if len(self._ratio_history) < RATIO_ROC_WINDOW + 1:
            return None
        recent = self._ratio_history[-1][1]
        older = self._ratio_history[-(RATIO_ROC_WINDOW + 1)][1]
        if older == 0:
            return 0.0
        return (recent - older) / abs(older)

    # ------------------------------------------------------------------
    # Liquidity Imbalance (Depth Alignment)
    # ------------------------------------------------------------------

    def _check_depth_alignment(self, bias: str, depth_snapshot: Optional[Dict]) -> Optional[float]:
        """Check if order book depth supports the bias direction."""
        if not depth_snapshot:
            return None
        bid_size = depth_snapshot.get("total_bid_size", 0)
        ask_size = depth_snapshot.get("total_ask_size", 0)
        total = bid_size + ask_size
        if total == 0:
            return None
        if bias == "LONG":
            return bid_size / total
        else:
            return ask_size / total

    # ------------------------------------------------------------------
    # Regime-Volatility Scaling
    # ------------------------------------------------------------------

    def _compute_regime_intensity(self, regime: str, net_gamma: float, bias: str) -> float:
        """Compute regime intensity factor based on gamma regime and bias alignment."""
        if bias == "LONG" and regime == "POSITIVE":
            base = 0.15
        elif bias == "SHORT" and regime == "NEGATIVE":
            base = 0.15
        elif bias == "LONG" and regime == "NEGATIVE":
            base = -0.10
        elif bias == "SHORT" and regime == "POSITIVE":
            base = -0.10
        else:
            base = 0.0
        intensity = min(1.0, abs(net_gamma) / REGIME_GAMMA_THRESHOLD)
        return base * intensity

    # ------------------------------------------------------------------
    # VWAP Deviation (Distance-Based)
    # ------------------------------------------------------------------

    def _check_vwap_deviation(self, price: float, rolling_data: Dict[str, Any], bias: str) -> Optional[float]:
        """Check price deviation from rolling mean in std-dev units.

        LONG: price must be below mean (mean reversion buy).
        SHORT: price must be above mean (mean reversion sell).
        """
        price_window = None
        for key in (KEY_PRICE_5M, KEY_PRICE_30M):
            rw = rolling_data.get(key)
            if rw and rw.count >= 5:
                price_window = rw
                break
        if price_window is None or price_window.mean is None or price_window.std is None:
            return None
        mean = price_window.mean
        std = price_window.std
        if std <= 0:
            return None
        deviation = (price - mean) / std
        if bias == "LONG":
            if deviation > 0:
                return None
            return round(abs(deviation), 3)
        else:
            if deviation < 0:
                return None
            return round(deviation, 3)

    # ------------------------------------------------------------------
    # 6-Component Confidence Scoring (v2)
    # ------------------------------------------------------------------

    def _compute_confidence_v2(
        self, ratio: float, bias_strength: float, bias: str,
        regime_intensity: float, total_msgs: int,
        vwap_dev: Optional[float], roc: Optional[float],
        depth_alignment: Optional[float],
    ) -> float:
        """Combine 6 components into a normalized confidence score [0, 1]."""
        # 1. Ratio extremity (0.15–0.25)
        if ratio < PUT_HEAVY_RATIO:
            if ratio <= STRONG_PUT_RATIO:
                ratio_conf = 0.25
            else:
                ratio_conf = 0.15 + 0.10 * (1 - ratio / PUT_HEAVY_RATIO)
        elif ratio > CALL_HEAVY_RATIO:
            if ratio >= STRONG_CALL_RATIO:
                ratio_conf = 0.25
            else:
                ratio_conf = 0.15 + 0.10 * min(1.0, (ratio - CALL_HEAVY_RATIO) / (STRONG_CALL_RATIO - CALL_HEAVY_RATIO))
        else:
            ratio_conf = 0.15  # neutral zone — baseline

        # 2. Bias strength (0.1–0.15)
        bias_conf = 0.1 + 0.05 * bias_strength

        # 3. Regime intensity (0.05–0.2) — magnitude-scaled
        regime_conf = 0.05 + 0.15 * min(1.0, abs(regime_intensity) / 0.15) if regime_intensity else 0.05

        # 4. ROC (0.05–0.15) — velocity confirmation
        if roc is not None:
            roc_conf = 0.05 + 0.10 * min(1.0, abs(roc) / RATIO_ROC_THRESHOLD)
        else:
            roc_conf = 0.05  # insufficient history → baseline

        # 5. Depth alignment (0.05–0.15)
        if depth_alignment is not None:
            depth_conf = 0.05 + 0.10 * depth_alignment
        else:
            depth_conf = 0.10  # no depth data → neutral (0.5 maps to 0.10)

        # 6. VWAP deviation (0.05–0.15)
        if vwap_dev is not None:
            vwap_conf = 0.05 + 0.10 * min(1.0, vwap_dev / 3.0)
        else:
            vwap_conf = 0.05  # no data → baseline

        return min(1.0, max(0.0, (ratio_conf + bias_conf + regime_conf + roc_conf + depth_conf + vwap_conf) / 6.0))
