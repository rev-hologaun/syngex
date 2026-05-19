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
from typing import Any, Dict, List

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M, KEY_PRICE_30M

logger = logging.getLogger("Syngex.Strategies.GEXImbalance")

# ---------------------------------------------------------------------------
# Default Fallback Constants
# These are used ONLY if config/strategies.yaml is missing values.
# The actual values should be configured in strategies.yaml under
# layer1.gex_imbalance.params
# ---------------------------------------------------------------------------

DEFAULT_PUT_HEAVY_RATIO = 0.5        # < 0.5 → long bias
DEFAULT_CALL_HEAVY_RATIO = 0.65      # > 0.65 → short bias
DEFAULT_STRONG_PUT_RATIO = 0.25      # very strong long signal
DEFAULT_STRONG_CALL_RATIO = 0.75     # very strong short signal
DEFAULT_MIN_MESSAGES = 20            # minimum data points for signal quality
DEFAULT_STOP_VOL_MULT = 2.5          # stop = 2.5x rolling price std dev
DEFAULT_TARGET_RISK_MULT = 1.5       # target = 1.5x stop distance
DEFAULT_MIN_CONFIDENCE = 0.55        # Minimum confidence to emit signal


class GEXImbalance(BaseStrategy):
    """
    GEX Imbalance strategy: trade dealer hedging bias from call/put gamma ratio.

    Call-heavy GEX → dealers short hedge → price pressure down.
    Put-heavy GEX → dealers buy hedge → price pressure up.
    """

    strategy_id = "gex_imbalance"
    layer = "layer1"



    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate GEX imbalance and return directional signals.

        Returns empty list when ratio is neutral or data is insufficient.
        """
        # Apply config params from data dict
        self._apply_params(data)

        # Extract params with fallback defaults
        put_heavy_ratio = self._params.get('put_heavy_ratio', DEFAULT_PUT_HEAVY_RATIO)
        call_heavy_ratio = self._params.get('call_heavy_ratio', DEFAULT_CALL_HEAVY_RATIO)
        strong_put_ratio = self._params.get('strong_put_ratio', DEFAULT_STRONG_PUT_RATIO)
        strong_call_ratio = self._params.get('strong_call_ratio', DEFAULT_STRONG_CALL_RATIO)
        min_messages = self._params.get('min_messages', DEFAULT_MIN_MESSAGES)
        stop_vol_mult = self._params.get('stop_vol_mult', DEFAULT_STOP_VOL_MULT)
        target_risk_mult = self._params.get('target_risk_mult', DEFAULT_TARGET_RISK_MULT)
        min_confidence = self._params.get('min_confidence', DEFAULT_MIN_CONFIDENCE)

        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        regime = data.get("regime", "")
        summary = gex_calc.get_summary()
        total_msgs = summary.get("total_messages", 0)

        # Require minimum data quality
        if total_msgs < min_messages:
            return []

        # Calculate call and put GEX from greeks summary
        call_gex, put_gex = self._calculate_gex_split(gex_calc)
        if call_gex + put_gex == 0:
            return []

        ratio = call_gex / put_gex if put_gex > 0 else 0.0

        # Determine bias direction
        bias, bias_strength = self._classify_bias(ratio, call_gex, put_gex, put_heavy_ratio, call_heavy_ratio, strong_put_ratio, strong_call_ratio)
        if bias is None:
            return []  # Neutral zone — no signal

        # VWAP trend confirmation
        vwap_confirmed = self._check_vwap_trend(
            underlying_price, rolling_data, bias
        )
        if not vwap_confirmed:
            return []  # No trend confirmation — skip

        # Regime alignment — soft confidence factor (no hard gates)

        # Compute confidence
        confidence = self._compute_confidence(
            ratio, bias_strength, bias, regime, total_msgs, vwap_confirmed,
            put_heavy_ratio, call_heavy_ratio, strong_put_ratio, strong_call_ratio
        )
        if confidence < min_confidence:
            return []

        # Build volatility-based stop/target
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window and price_window.count >= 10 and price_window.std is not None:
            vol = price_window.std
            if vol > 0:
                stop_distance = vol * stop_vol_mult
            else:
                stop_distance = underlying_price * 0.005  # fallback: 0.5%
        else:
            stop_distance = underlying_price * 0.005  # fallback: 0.5%

        if bias == "LONG":
            stop = underlying_price - stop_distance
            target = underlying_price + stop_distance * target_risk_mult
            direction = Direction.LONG
            side_label = "put-heavy"
        else:
            stop = underlying_price + stop_distance
            target = underlying_price - stop_distance * target_risk_mult
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
        self, ratio: float, call_gex: float, put_gex: float,
        put_heavy_ratio: float, call_heavy_ratio: float,
        strong_put_ratio: float, strong_call_ratio: float
    ) -> tuple:
        """
        Classify the GEX imbalance into LONG bias, SHORT bias, or neutral.

        Returns (bias, strength) where bias is "LONG", "SHORT", or None.
        Strength is 0.0–1.0 indicating how extreme the imbalance is.
        """
        if put_gex == 0 and call_gex == 0:
            return (None, 0.0)

        # Put-heavy → LONG bias
        if ratio < put_heavy_ratio:
            # Strength: how far below threshold
            strength = min(1.0, (put_heavy_ratio - ratio) / put_heavy_ratio)
            return ("LONG", strength)

        # Call-heavy → SHORT bias
        if ratio > call_heavy_ratio:
            # Normalize against realistic upper bound (3.0 = calls 3x puts)
            strength = min(1.0, (ratio - call_heavy_ratio) / (3.0 - call_heavy_ratio))
            return ("SHORT", strength)

        # Neutral zone
        return (None, 0.0)

    # ------------------------------------------------------------------
    # VWAP trend confirmation
    # ------------------------------------------------------------------

    def _check_vwap_trend(
        self, price: float, rolling_data: Dict[str, Any], bias: str
    ) -> bool:
        """
        Confirm the signal with VWAP trend.

        For LONG signals: price should be above VWAP (rolling mean).
        For SHORT signals: price should be below VWAP (rolling mean).

        Checks multiple rolling windows for confirmation.
        """
        # Check "price" window (generic) or "price_5m" / "price_30m"
        price_window = None
        for key in (KEY_PRICE_5M, KEY_PRICE_30M):
            rw = rolling_data.get(key)
            if rw and rw.count >= 5:
                price_window = rw
                break

        if price_window is None:
            return False

        mean = price_window.mean
        if mean is None or mean <= 0:
            return False

        if bias == "LONG":
            # Put-heavy in a dip (price below VWAP) = mean reversion LONG
            return price < mean
        else:
            # Call-heavy above VWAP = trend continuation SHORT
            return price > mean

    # ------------------------------------------------------------------
    # Confidence computation
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        ratio: float,
        bias_strength: float,
        bias: str,
        regime: str,
        total_msgs: int,
        vwap_confirmed: bool,
        put_heavy_ratio: float,
        call_heavy_ratio: float,
        strong_put_ratio: float,
        strong_call_ratio: float,
    ) -> float:
        """
        Combine ratio extremity, regime alignment, and data quality into confidence.

        Returns 0.0–1.0.
        """
        # Ratio extremity: how far from neutral (0.4–0.6)
        # Strong signals (near 0 or 1) get higher confidence
        if ratio < put_heavy_ratio:
            # Put-heavy: closer to 0 = stronger
            if ratio <= strong_put_ratio:
                ratio_conf = 0.8
            else:
                ratio_conf = 0.4 + 0.4 * (1 - ratio / put_heavy_ratio)
        elif ratio > call_heavy_ratio:
            # Call-heavy: higher ratio = stronger (normalize against 3.0 upper bound)
            if ratio >= strong_call_ratio * 3:  # ~2.25 → strong
                ratio_conf = 0.8
            else:
                ratio_conf = 0.4 + 0.4 * min(1.0, (ratio - call_heavy_ratio) / (3.0 - call_heavy_ratio))
        else:
            ratio_conf = 0.0

        # Regime alignment bonus (bias-aware: +0.15 aligned, -0.10 misaligned)
        regime_bonus = 0.0
        if bias == "LONG" and regime == "POSITIVE":
            regime_bonus = 0.15  # Aligned: put-heavy + positive regime
        elif bias == "SHORT" and regime == "NEGATIVE":
            regime_bonus = 0.15  # Aligned: call-heavy + negative regime
        elif bias == "LONG" and regime == "NEGATIVE":
            regime_bonus = -0.10  # Misaligned: penalize but don't block
        elif bias == "SHORT" and regime == "POSITIVE":
            regime_bonus = -0.10  # Misaligned: penalize but don't block

        # Data freshness bonus (0.0–0.1)
        msg_conf = min(0.1, total_msgs / 10000)

        # VWAP confirmation bonus (0.0–0.1)
        vwap_bonus = 0.1 if vwap_confirmed else 0.0

        # Normalize each component to [0,1] and average
        norm_ratio = (ratio_conf - 0.4) / (0.8 - 0.4) if 0.8 != 0.4 else 1.0
        norm_regime = (regime_bonus + 0.10) / 0.25 if 0.25 != 0 else 0.0  # shift [-0.10, +0.15] → [0, 1]
        norm_msg = msg_conf / 0.1 if 0.1 != 0 else 0.0
        norm_vwap = vwap_bonus / 0.1 if 0.1 != 0 else 0.0
        confidence = (norm_ratio + norm_regime + norm_msg + norm_vwap) / 4.0
        return min(1.0, max(0.0, confidence))
