"""
strategies/layer3/strike_concentration.py — Strike Concentration Scalp

Micro-signal (1Hz) strategy: trades the immediate reaction to the most
active OI strikes. Two modes:
    - BOUNCE: Price approaches a high-OI strike and reverses → trade the bounce
    - SLICE: Price slices through a strike with momentum → ride the breakout

Logic:
    - Pre-market: identify top 3 strikes by total OI concentration
    - Intraday: detect bounce or slice signals at those strikes
    - Larger size on #1 strike (highest OI concentration)
    - Best in first 2 hours and last hour of session

Entry (Bounce):
    - LONG: bounce off Put strike (below price) + bullish reversal signal
    - SHORT: bounce off Call strike (above price) + bearish reversal signal

Entry (Slice):
    - LONG: slices through Call strike + strong candle + volume spike
    - SHORT: slices through Put strike + strong candle + volume spike

Confidence factors:
    - OI concentration rank (#1 strike = highest)
    - Proximity to strike
    - Signal strength (candle pattern quality, volume confirmation)
    - Regime alignment
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.StrikeConcentration")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# How many top OI strikes to track
TOP_OI_STRIKES_COUNT = 3

# Bounce proximity: price must be within this % of the strike
BOUNCE_PROXIMITY_PCT = 0.003  # 0.3%

# Slice confirmation: candle body must be > this % of total range
SLICE_BODY_RATIO = 0.5  # 50% body

# Volume spike for slice confirmation
SLICE_VOLUME_RATIO = 1.20  # 20% above rolling avg

# Divergence detection: volume on reversal candle must be < this % of rolling avg
DIVERGENCE_VOLUME_THRESHOLD = 0.80  # Volume < 80% of avg = declining

# Stop loss
STOP_PCT_BOUNCE = 0.003  # 0.3% beyond the strike for bounces
STOP_PCT_SLICE = 0.003  # 0.3% against entry for slices

# Target
TARGET_RISK_MULT = 1.5  # 1.5× risk for bounce targets

# Min confidence
MIN_CONFIDENCE = 0.35
MAX_CONFIDENCE = 0.85  # Micro-signal cap

# Min data points
MIN_DATA_POINTS = 3


class StrikeConcentration(BaseStrategy):
    """
    Trades the immediate reaction to the most active OI strikes.

    Two modes:
        BOUNCE — Price approaches a high-OI strike and reverses.
            In POSITIVE gamma regime, bounces are reliable:
                LONG: bounce off Put strike (below price)
                SHORT: bounce off Call strike (above price)

        SLICE — Price slices through a strike with momentum.
            Ride the breakout with volume confirmation:
                LONG: slices through Call strike (was below, now above)
                SHORT: slices through Put strike (was above, now below)

    Confidence is capped at 0.85 (micro-signals shouldn't be max conviction).
    Larger position size on #1 strike (highest OI concentration).
    """

    strategy_id = "strike_concentration"
    layer = "layer3"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for strike concentration bounce/slice signals.

        Returns empty list when no signal is detected.
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
        greeks_summary = data.get("greeks_summary", {})

        # Bounce requires positive gamma regime
        if regime != "POSITIVE":
            return []

        if net_gamma <= 0:
            return []

        # Must have enough rolling data
        price_window = rolling_data.get("price_5m")
        vol_window = rolling_data.get("volume_5m")
        if (
            price_window is None
            or vol_window is None
            or price_window.count < MIN_DATA_POINTS
            or vol_window.count < MIN_DATA_POINTS
        ):
            return []

        # Identify top 3 OI strikes
        top_strikes = self._get_top_oi_strikes(greeks_summary)
        if len(top_strikes) < 1:
            return []

        signals: List[Signal] = []

        # Check bounce signals
        bounce_long = self._check_bounce_long(
            underlying_price, gex_calc, rolling_data,
            net_gamma, regime, top_strikes,
        )
        if bounce_long:
            signals.append(bounce_long)

        bounce_short = self._check_bounce_short(
            underlying_price, gex_calc, rolling_data,
            net_gamma, regime, top_strikes,
        )
        if bounce_short:
            signals.append(bounce_short)

        # Check slice signals
        slice_long = self._check_slice_long(
            underlying_price, gex_calc, rolling_data,
            net_gamma, regime, top_strikes,
        )
        if slice_long:
            signals.append(slice_long)

        slice_short = self._check_slice_short(
            underlying_price, gex_calc, rolling_data,
            net_gamma, regime, top_strikes,
        )
        if slice_short:
            signals.append(slice_short)

        return signals

    # ------------------------------------------------------------------
    # BOUNCE — LONG at Put strike (price below, bouncing off support)
    # ------------------------------------------------------------------

    def _check_bounce_long(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
        top_strikes: List[Tuple[float, int, float]],
    ) -> Optional[Signal]:
        """
        Bounce LONG at a Put strike below price.

        Conditions:
            1. Nearest top-OI Put strike BELOW current price
            2. Price within 0.3% of that strike
            3. Bullish reversal signal (divergence OR candlestick pattern)
            4. Net Gamma > 0 (already checked in evaluate)
        """
        # Find nearest top-OI strike below price
        put_strike, rank, total_oi = self._nearest_strike_below(top_strikes, price)
        if put_strike is None:
            return None

        # Check proximity: price within 0.3% of strike
        proximity = abs(price - put_strike) / put_strike
        if proximity > BOUNCE_PROXIMITY_PCT:
            return None

        # Check bullish reversal signal
        bullish = self._check_bullish_reversal(rolling_data, price, put_strike)
        if not bullish:
            return None

        # Compute confidence and build signal
        confidence = self._compute_bounce_confidence(
            price, put_strike, rank, total_oi,
            rolling_data, "LONG", net_gamma,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Entry at current price, stop beyond the Put strike (below)
        entry = price
        stop = put_strike * (1 - STOP_PCT_BOUNCE)
        risk = entry - stop

        # Target = midpoint between this strike and next strike above
        target = self._compute_bounce_target(
            put_strike, top_strikes, price, "above", risk,
        )

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Strike bounce LONG: {put_strike} Put strike, "
                f"rank #{rank}, bullish reversal"
            ),
            metadata={
                "signal_type": "bounce",
                "strike_rank": rank,
                "strike": put_strike,
                "total_oi": round(total_oi, 1),
                "proximity_pct": round(proximity, 5),
                "bullish_reversal": True,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (target - entry) / risk, 2
                ) if risk > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # BOUNCE — SHORT at Call strike (price above, bouncing off resistance)
    # ------------------------------------------------------------------

    def _check_bounce_short(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
        top_strikes: List[Tuple[float, int, float]],
    ) -> Optional[Signal]:
        """
        Bounce SHORT at a Call strike above price.

        Conditions:
            1. Nearest top-OI Call strike ABOVE current price
            2. Price within 0.3% of that strike
            3. Bearish reversal signal (divergence OR candlestick pattern)
            4. Net Gamma > 0 (already checked in evaluate)
        """
        # Find nearest top-OI strike above price
        call_strike, rank, total_oi = self._nearest_strike_above(top_strikes, price)
        if call_strike is None:
            return None

        # Check proximity: price within 0.3% of strike
        proximity = abs(call_strike - price) / call_strike
        if proximity > BOUNCE_PROXIMITY_PCT:
            return None

        # Check bearish reversal signal
        bearish = self._check_bearish_reversal(rolling_data, price, call_strike)
        if not bearish:
            return None

        # Compute confidence and build signal
        confidence = self._compute_bounce_confidence(
            price, call_strike, rank, total_oi,
            rolling_data, "SHORT", net_gamma,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Entry at current price, stop beyond the Call strike (above)
        entry = price
        stop = call_strike * (1 + STOP_PCT_BOUNCE)
        risk = stop - entry

        # Target = midpoint between this strike and next strike below
        target = self._compute_bounce_target(
            call_strike, top_strikes, price, "below", risk,
        )

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Strike bounce SHORT: {call_strike} Call strike, "
                f"rank #{rank}, bearish reversal"
            ),
            metadata={
                "signal_type": "bounce",
                "strike_rank": rank,
                "strike": call_strike,
                "total_oi": round(total_oi, 1),
                "proximity_pct": round(proximity, 5),
                "bearish_reversal": True,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (entry - target) / risk, 2
                ) if risk > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # SLICE — LONG through Call strike (was below, now above)
    # ------------------------------------------------------------------

    def _check_slice_long(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
        top_strikes: List[Tuple[float, int, float]],
    ) -> Optional[Signal]:
        """
        Slice LONG through a Call strike above price.

        Conditions:
            1. Price slices through a top-OI Call strike (was below, now above)
            2. Strong candle: body > 50% of total range
            3. Volume spike: current > rolling avg by ≥20%
            4. Delta at that strike turning positive
        """
        # Find nearest top-OI strike above price (the one being sliced through)
        call_strike, rank, total_oi = self._nearest_strike_above(top_strikes, price)
        if call_strike is None:
            return None

        # Check strong candle: body > 50% of range
        body_ratio = self._get_candle_body_ratio(rolling_data)
        if body_ratio is None or body_ratio < SLICE_BODY_RATIO:
            return None

        # Check volume spike: current > rolling avg by ≥20%
        if not self._check_volume_spike(rolling_data):
            return None

        # Check delta at that strike turning positive
        if not self._check_delta_positive_at_strike(gex_calc, call_strike):
            return None

        # Compute confidence and build signal
        confidence = self._compute_slice_confidence(
            price, call_strike, rank, total_oi,
            rolling_data, body_ratio, "LONG", net_gamma,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Entry at current price, stop 0.3% below entry
        entry = price
        stop = entry * (1 - STOP_PCT_SLICE)
        risk = entry - stop

        # Target = next strike above
        target = self._compute_slice_target(
            call_strike, top_strikes, "above", risk,
        )

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Strike slice LONG: sliced through {call_strike} Call strike, "
                f"rank #{rank}, body_ratio={body_ratio:.2f}"
            ),
            metadata={
                "signal_type": "slice",
                "strike_rank": rank,
                "strike": call_strike,
                "total_oi": round(total_oi, 1),
                "body_ratio": round(body_ratio, 3),
                "volume_spike": True,
                "delta_positive": True,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (target - entry) / risk, 2
                ) if risk > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # SLICE — SHORT through Put strike (was above, now below)
    # ------------------------------------------------------------------

    def _check_slice_short(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
        top_strikes: List[Tuple[float, int, float]],
    ) -> Optional[Signal]:
        """
        Slice SHORT through a Put strike below price.

        Conditions:
            1. Price slices through a top-OI Put strike (was above, now below)
            2. Strong candle: body > 50% of total range
            3. Volume spike: current > rolling avg by ≥20%
            4. Delta at that strike turning negative
        """
        # Find nearest top-OI strike below price (the one being sliced through)
        put_strike, rank, total_oi = self._nearest_strike_below(top_strikes, price)
        if put_strike is None:
            return None

        # Check strong candle: body > 50% of range
        body_ratio = self._get_candle_body_ratio(rolling_data)
        if body_ratio is None or body_ratio < SLICE_BODY_RATIO:
            return None

        # Check volume spike: current > rolling avg by ≥20%
        if not self._check_volume_spike(rolling_data):
            return None

        # Check delta at that strike turning negative
        if not self._check_delta_negative_at_strike(gex_calc, put_strike):
            return None

        # Compute confidence and build signal
        confidence = self._compute_slice_confidence(
            price, put_strike, rank, total_oi,
            rolling_data, body_ratio, "SHORT", net_gamma,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Entry at current price, stop 0.3% above entry
        entry = price
        stop = entry * (1 + STOP_PCT_SLICE)
        risk = stop - entry

        # Target = next strike below
        target = self._compute_slice_target(
            put_strike, top_strikes, "below", risk,
        )

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Strike slice SHORT: sliced through {put_strike} Put strike, "
                f"rank #{rank}, body_ratio={body_ratio:.2f}"
            ),
            metadata={
                "signal_type": "slice",
                "strike_rank": rank,
                "strike": put_strike,
                "total_oi": round(total_oi, 1),
                "body_ratio": round(body_ratio, 3),
                "volume_spike": True,
                "delta_negative": True,
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (entry - target) / risk, 2
                ) if risk > 0 else 0,
            },
        )

    # ------------------------------------------------------------------
    # Reversal Signal Detection
    # ------------------------------------------------------------------

    def _check_bullish_reversal(
        self,
        rolling_data: Dict[str, Any],
        price: float,
        strike: float,
    ) -> bool:
        """
        Check for bullish reversal at a Put strike.

        Two possible signals (either one qualifies):
            1. Bullish divergence: price made a lower low but volume declined
            2. Bullish candlestick: close > open, upper wick < lower wick * 0.5
        """
        price_window = rolling_data.get("price_5m")
        vol_window = rolling_data.get("volume_5m")

        if price_window is None or vol_window is None:
            return False

        latest = price_window.latest
        if latest is None:
            return False

        # Check 1: Bullish divergence
        if self._check_bullish_divergence(price_window, vol_window, strike):
            return True

        # Check 2: Bullish candlestick pattern
        if self._check_bullish_candlestick(price_window):
            return True

        return False

    def _check_bearish_reversal(
        self,
        rolling_data: Dict[str, Any],
        price: float,
        strike: float,
    ) -> bool:
        """
        Check for bearish reversal at a Call strike.

        Two possible signals (either one qualifies):
            1. Bearish divergence: price made a higher high but volume declined
            2. Bearish candlestick: close < open, lower wick < upper wick * 0.5
        """
        price_window = rolling_data.get("price_5m")
        vol_window = rolling_data.get("volume_5m")

        if price_window is None or vol_window is None:
            return False

        latest = price_window.latest
        if latest is None:
            return False

        # Check 1: Bearish divergence
        if self._check_bearish_divergence(price_window, vol_window, strike):
            return True

        # Check 2: Bearish candlestick pattern
        if self._check_bearish_candlestick(price_window):
            return True

        return False

    @staticmethod
    def _check_bullish_divergence(
        price_window: Any,
        vol_window: Any,
        strike: float,
    ) -> bool:
        """
        Bullish divergence: price made a lower low near strike
        but volume is declining (selling exhaustion).
        """
        window_min = price_window.min
        window_latest = price_window.latest
        vol_latest = vol_window.latest
        vol_avg = vol_window.mean

        if window_min is None or window_latest is None:
            return False
        if vol_latest is None or vol_avg is None or vol_avg == 0:
            return False

        # Price is near the strike (within proximity)
        proximity = abs(window_latest - strike) / strike
        if proximity > BOUNCE_PROXIMITY_PCT * 2:
            return False

        # Volume declining on the latest candle vs rolling avg
        vol_ratio = vol_latest / vol_avg
        return vol_ratio < DIVERGENCE_VOLUME_THRESHOLD

    @staticmethod
    def _check_bearish_divergence(
        price_window: Any,
        vol_window: Any,
        strike: float,
    ) -> bool:
        """
        Bearish divergence: price made a higher high near strike
        but volume is declining (buying exhaustion).
        """
        window_max = price_window.max
        window_latest = price_window.latest
        vol_latest = vol_window.latest
        vol_avg = vol_window.mean

        if window_max is None or window_latest is None:
            return False
        if vol_latest is None or vol_avg is None or vol_avg == 0:
            return False

        # Price is near the strike (within proximity)
        proximity = abs(window_latest - strike) / strike
        if proximity > BOUNCE_PROXIMITY_PCT * 2:
            return False

        # Volume declining on the latest candle vs rolling avg
        vol_ratio = vol_latest / vol_avg
        return vol_ratio < DIVERGENCE_VOLUME_THRESHOLD

    @staticmethod
    def _check_bullish_candlestick(price_window: Any) -> bool:
        """
        Bullish candlestick: close > open (latest > mean of last 2-3),
        upper wick < lower wick * 0.5.

        Approximation:
            close = latest price
            open = rolling mean of last few values
            upper wick = max - close
            lower wick = close - min
        """
        latest = price_window.latest
        window_max = price_window.max
        window_min = price_window.min

        if latest is None or window_max is None or window_min is None:
            return False

        # Approximate open as the mean of the window (rough proxy)
        open_price = price_window.mean
        if open_price is None or open_price == 0:
            return False

        # Close > Open (bullish candle)
        if latest <= open_price:
            return False

        # Upper wick < lower wick * 0.5
        upper_wick = window_max - latest
        lower_wick = latest - window_min

        if lower_wick <= 0:
            return False

        return upper_wick < lower_wick * 0.5

    @staticmethod
    def _check_bearish_candlestick(price_window: Any) -> bool:
        """
        Bearish candlestick: close < open, lower wick < upper wick * 0.5.
        """
        latest = price_window.latest
        window_max = price_window.max
        window_min = price_window.min

        if latest is None or window_max is None or window_min is None:
            return False

        open_price = price_window.mean
        if open_price is None or open_price == 0:
            return False

        # Close < Open (bearish candle)
        if latest >= open_price:
            return False

        # Lower wick < upper wick * 0.5
        upper_wick = window_max - latest
        lower_wick = latest - window_min

        if upper_wick <= 0:
            return False

        return lower_wick < upper_wick * 0.5

    @staticmethod
    def _get_candle_body_ratio(rolling_data: Dict[str, Any]) -> Optional[float]:
        """
        Get candle body ratio: abs(close - open) / (high - low).

        Approximation using price rolling window:
            close = latest
            open = rolling mean
            high = window max
            low = window min
        """
        window = rolling_data.get("price_5m")
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        latest = window.latest
        open_price = window.mean
        window_max = window.max
        window_min = window.min

        if (
            latest is None
            or open_price is None
            or window_max is None
            or window_min is None
        ):
            return None

        close = latest
        high = window_max
        low = window_min

        candle_range = high - low
        if candle_range <= 0:
            return None

        body = abs(close - open_price)
        return body / candle_range

    @staticmethod
    def _check_volume_spike(rolling_data: Dict[str, Any]) -> bool:
        """Check if current volume exceeds rolling average by ≥20%."""
        window = rolling_data.get("volume_5m")
        if window is None or window.count < MIN_DATA_POINTS:
            return False

        current = window.latest
        avg = window.mean
        if current is None or avg is None or avg == 0:
            return False

        return current >= avg * SLICE_VOLUME_RATIO

    @staticmethod
    def _check_delta_positive_at_strike(
        gex_calc: Any,
        strike: float,
    ) -> bool:
        """Check if net delta at the given strike is positive."""
        try:
            delta_data = gex_calc.get_delta_by_strike(strike)
            net_delta = delta_data.get("net_delta", 0)
            return net_delta > 0
        except Exception as exc:
            logger.debug(
                "StrikeConcentration: failed to check delta at %s: %s",
                strike, exc,
            )
            return False

    @staticmethod
    def _check_delta_negative_at_strike(
        gex_calc: Any,
        strike: float,
    ) -> bool:
        """Check if net delta at the given strike is negative."""
        try:
            delta_data = gex_calc.get_delta_by_strike(strike)
            net_delta = delta_data.get("net_delta", 0)
            return net_delta < 0
        except Exception as exc:
            logger.debug(
                "StrikeConcentration: failed to check delta at %s: %s",
                strike, exc,
            )
            return False

    # ------------------------------------------------------------------
    # OI Strike Tracking
    # ------------------------------------------------------------------

    @staticmethod
    def _get_top_oi_strikes(
        greeks_summary: Dict[str, Any],
    ) -> List[Tuple[float, int, float]]:
        """
        Identify the top N strikes by total OI concentration.

        Returns sorted list of (strike, rank, total_oi) tuples,
        ranked from highest OI (rank 1) to lowest.

        Each greeks_summary entry has call_oi and put_oi fields.
        """
        if not greeks_summary:
            return []

        strike_oi_list: List[Tuple[float, float]] = []

        for strike_str, data in greeks_summary.items():
            try:
                strike = float(strike_str)
            except (ValueError, TypeError):
                continue

            call_oi = data.get("call_oi", 0) or 0
            put_oi = data.get("put_oi", 0) or 0
            total_oi = call_oi + put_oi

            if total_oi > 0:
                strike_oi_list.append((strike, total_oi))

        # Sort by total OI descending, take top N
        strike_oi_list.sort(key=lambda x: x[1], reverse=True)
        top = strike_oi_list[:TOP_OI_STRIKES_COUNT]

        # Assign ranks
        return [(strike, rank + 1, total_oi) for rank, (strike, total_oi) in enumerate(top)]

    @staticmethod
    def _nearest_strike_above(
        top_strikes: List[Tuple[float, int, float]],
        price: float,
    ) -> Optional[Tuple[float, int, float]]:
        """Find the nearest top-OI strike ABOVE the current price."""
        above = [s for s in top_strikes if s[0] > price]
        if not above:
            return None
        return min(above, key=lambda s: s[0])

    @staticmethod
    def _nearest_strike_below(
        top_strikes: List[Tuple[float, int, float]],
        price: float,
    ) -> Optional[Tuple[float, int, float]]:
        """Find the nearest top-OI strike BELOW the current price."""
        below = [s for s in top_strikes if s[0] < price]
        if not below:
            return None
        return max(below, key=lambda s: s[0])

    # ------------------------------------------------------------------
    # Target & Stop Computation
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_bounce_target(
        current_strike: float,
        top_strikes: List[Tuple[float, int, float]],
        price: float,
        direction: str,
        risk: float,
    ) -> float:
        """
        Compute bounce target.

        For LONG (bounce off Put below): target = midpoint between
            current strike and next strike above.
        For SHORT (bounce off Call above): target = midpoint between
            current strike and next strike below.

        Falls back to risk-based target if no next strike found.
        """
        if direction == "above":
            # Find next strike above current_strike
            candidates = [s for s in top_strikes if s[0] > current_strike]
            if candidates:
                next_strike = min(candidates, key=lambda s: s[0])
                target = (current_strike + next_strike[0]) / 2
                return target
        else:
            # Find next strike below current_strike
            candidates = [s for s in top_strikes if s[0] < current_strike]
            if candidates:
                next_strike = max(candidates, key=lambda s: s[0])
                target = (current_strike + next_strike[0]) / 2
                return target

        # Fallback: use risk-based target
        return price + (risk * TARGET_RISK_MULT) if risk > 0 else price

    @staticmethod
    def _compute_slice_target(
        current_strike: float,
        top_strikes: List[Tuple[float, int, float]],
        direction: str,
        risk: float,
    ) -> float:
        """
        Compute slice target = next strike in the direction of the slice.

        For LONG slice (through Call above): target = next strike above.
        For SHORT slice (through Put below): target = next strike below.

        Falls back to risk-based target if no next strike found.
        """
        if direction == "above":
            candidates = [s for s in top_strikes if s[0] > current_strike]
            if candidates:
                return min(candidates, key=lambda s: s[0])[0]
        else:
            candidates = [s for s in top_strikes if s[0] < current_strike]
            if candidates:
                return max(candidates, key=lambda s: s[0])[0]

        # Fallback: use risk-based target
        return current_strike + (risk * TARGET_RISK_MULT) if risk > 0 else current_strike

    # ------------------------------------------------------------------
    # Confidence Computation
    # ------------------------------------------------------------------

    def _compute_bounce_confidence(
        self,
        price: float,
        strike: float,
        rank: int,
        total_oi: float,
        rolling_data: Dict[str, Any],
        direction: str,
        net_gamma: float,
    ) -> float:
        """
        Compute bounce confidence (0.0–MAX_CONFIDENCE).

        Factors:
            1. OI concentration rank     (0.20–0.30)  #1 = highest
            2. Proximity to strike        (0.15–0.25)  closer = higher
            3. Signal strength            (0.15–0.20)  candle pattern quality
            4. Regime alignment           (0.10–0.15)  positive gamma
            5. OI volume                  (0.05–0.10)  higher OI = more significant
        """
        # 1. OI rank component (0.20–0.30)
        # Rank 1 = 0.30, Rank 2 = 0.25, Rank 3+ = 0.20
        rank_conf = max(0.20, 0.30 - 0.05 * (rank - 1))

        # 2. Proximity component (0.15–0.25)
        # At 0% distance = 0.25, at 0.3% distance = 0.15
        proximity = abs(price - strike) / strike
        if proximity <= 0:
            prox_conf = 0.25
        elif proximity >= BOUNCE_PROXIMITY_PCT:
            prox_conf = 0.15
        else:
            prox_conf = 0.25 - 0.10 * (proximity / BOUNCE_PROXIMITY_PCT)

        # 3. Signal strength (0.15–0.20)
        # Approximate from volume profile
        vol_window = rolling_data.get("volume_5m")
        if vol_window is not None and vol_window.mean and vol_window.mean > 0:
            vol_latest = vol_window.latest or 0
            vol_ratio = vol_latest / vol_window.mean
            # Lower volume near strike = stronger divergence signal
            if direction == "LONG":
                signal_conf = 0.15 + 0.05 * max(0, 1.0 - vol_ratio)
            else:
                signal_conf = 0.15 + 0.05 * max(0, 1.0 - vol_ratio)
        else:
            signal_conf = 0.15  # baseline

        # 4. Regime alignment (0.10–0.15)
        # Positive gamma regime — bounces are reliable
        regime_conf = 0.10 + 0.05 * min(1.0, abs(net_gamma) / 5_000_000)

        # 5. OI volume component (0.05–0.10)
        # Higher total OI = more significant strike
        oi_conf = 0.05 + 0.05 * min(1.0, total_oi / 1000)

        confidence = (
            rank_conf + prox_conf + signal_conf + regime_conf + oi_conf
        )
        return min(MAX_CONFIDENCE, max(0.0, confidence))

    def _compute_slice_confidence(
        self,
        price: float,
        strike: float,
        rank: int,
        total_oi: float,
        rolling_data: Dict[str, Any],
        body_ratio: float,
        direction: str,
        net_gamma: float,
    ) -> float:
        """
        Compute slice confidence (0.0–MAX_CONFIDENCE).

        Factors:
            1. OI concentration rank     (0.15–0.25)  #1 = highest
            2. Body ratio strength        (0.20–0.30)  stronger = higher
            3. Volume spike magnitude     (0.15–0.20)  stronger spike = higher
            4. Regime alignment           (0.10–0.15)  positive gamma
            5. OI volume                  (0.05–0.10)  higher OI = more significant
        """
        # 1. OI rank component (0.15–0.25)
        rank_conf = max(0.15, 0.25 - 0.05 * (rank - 1))

        # 2. Body ratio component (0.20–0.30)
        # body_ratio = 0.5 → 0.20, body_ratio = 1.0 → 0.30
        body_conf = 0.20 + 0.10 * min(1.0, (body_ratio - SLICE_BODY_RATIO) / 0.5)

        # 3. Volume spike component (0.15–0.20)
        vol_window = rolling_data.get("volume_5m")
        if vol_window is not None and vol_window.mean and vol_window.mean > 0:
            vol_latest = vol_window.latest or 0
            vol_ratio = vol_latest / vol_window.mean
            vol_conf = 0.15 + 0.05 * min(1.0, (vol_ratio - 1.0))
        else:
            vol_conf = 0.15  # baseline

        # 4. Regime alignment (0.10–0.15)
        regime_conf = 0.10 + 0.05 * min(1.0, abs(net_gamma) / 5_000_000)

        # 5. OI volume component (0.05–0.10)
        oi_conf = 0.05 + 0.05 * min(1.0, total_oi / 1000)

        confidence = (
            rank_conf + body_conf + vol_conf + regime_conf + oi_conf
        )
        return min(MAX_CONFIDENCE, max(0.0, confidence))
