"""
tests/strategies/test_gex_imbalance.py — Unit tests for GEX Imbalance strategy.

Tests cover:
  - Put-heavy → LONG signal
  - Call-heavy → SHORT signal
  - Neutral zone → no signal
  - Insufficient data → no signal
  - Low confidence → no signal
  - VWAP directional check (wrong side → no signal)
  - Strong bias → higher confidence than marginal
"""

import time
from unittest.mock import MagicMock

import pytest

from strategies.layer1.gex_imbalance import GEXImbalance
from strategies.signal import Direction
from strategies.rolling_keys import KEY_PRICE_5M


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_gex_summary(call_gex: float, put_gex: float) -> dict:
    """Build a greeks_summary dict that sums to the given call/put GEX."""
    if call_gex > 0 and put_gex > 0:
        return {
            "100": {"net_gamma": call_gex},
            "101": {"net_gamma": -put_gex},
        }
    if call_gex > 0:
        return {"100": {"net_gamma": call_gex}}
    if put_gex > 0:
        return {"100": {"net_gamma": -put_gex}}
    return {}


def _make_price_window(
    count: int = 100,
    mean: float = 100.0,
    std: float = 0.5,
    trend: str = "UP",
) -> MagicMock:
    """Return a mock RollingWindow with the given attributes."""
    w = MagicMock()
    w.count = count
    w.mean = mean
    w.std = std
    w.trend = trend
    return w


def _make_data(
    call_gex: float = 1000.0,
    put_gex: float = 5000.0,
    underlying_price: float = 100.0,
    total_messages: int = 100,
    regime: str = "POSITIVE",
    price_window: MagicMock | None = None,
    depth_snapshot: dict | None = None,
    timestamp: float | None = None,
    symbol: str = "SPY",
) -> dict:
    """Build a complete data dict for GEXImbalance.evaluate()."""
    gex_calc = MagicMock()
    gex_calc.get_summary.return_value = {"total_messages": total_messages}
    gex_calc.get_greeks_summary.return_value = _make_gex_summary(call_gex, put_gex)
    gex_calc.get_net_gamma.return_value = call_gex - put_gex

    if price_window is None:
        price_window = _make_price_window()

    rolling_data = {KEY_PRICE_5M: price_window}

    if depth_snapshot is None:
        depth_snapshot = {"total_bid_size": 500, "total_ask_size": 500}

    return {
        "underlying_price": underlying_price,
        "gex_calculator": gex_calc,
        "rolling_data": rolling_data,
        "regime": regime,
        "depth_snapshot": depth_snapshot,
        "timestamp": timestamp or time.time(),
        "symbol": symbol,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGEXImbalance:
    """Tests for GEXImbalance.evaluate()."""

    # ------------------------------------------------------------------
    # 1. Put-heavy → LONG signal
    # ------------------------------------------------------------------

    def test_put_heavy_long_signal(self):
        """call_gex=1000, put_gex=5000 → ratio=0.2, well below PUT_HEAVY_RATIO=0.45.
        Should produce a LONG signal with decent confidence."""
        strat = GEXImbalance()
        data = _make_data(call_gex=1000, put_gex=5000, underlying_price=100.0)
        signals = strat.evaluate(data)

        assert len(signals) == 1
        sig = signals[0]
        assert sig.direction == Direction.LONG
        assert sig.confidence > 0.3  # decent confidence
        assert sig.entry == 100.0
        assert sig.stop < sig.entry
        assert sig.target > sig.entry
        assert sig.strategy_id == "gex_imbalance"
        assert "put-heavy" in sig.reason

    # ------------------------------------------------------------------
    # 2. Call-heavy → SHORT signal
    # ------------------------------------------------------------------

    def test_call_heavy_short_signal(self):
        """call_gex=5000, put_gex=1000 → ratio=5.0, well above CALL_HEAVY_RATIO=0.60.
        Should produce a SHORT signal."""
        strat = GEXImbalance()
        data = _make_data(call_gex=5000, put_gex=1000, underlying_price=100.0)
        signals = strat.evaluate(data)

        assert len(signals) == 1
        sig = signals[0]
        assert sig.direction == Direction.SHORT
        assert sig.entry == 100.0
        assert sig.stop > sig.entry
        assert sig.target < sig.entry
        assert "call-heavy" in sig.reason

    # ------------------------------------------------------------------
    # 3. Neutral zone → no signal
    # ------------------------------------------------------------------

    def test_neutral_zone_no_signal(self):
        """call_gex=500, put_gex=900 → ratio≈0.556, in neutral zone [0.45, 0.60].
        Should return []."""
        strat = GEXImbalance()
        data = _make_data(call_gex=500, put_gex=900, underlying_price=100.0)
        signals = strat.evaluate(data)

        assert signals == []

    # ------------------------------------------------------------------
    # 4. Insufficient data → no signal
    # ------------------------------------------------------------------

    def test_insufficient_data_no_signal(self):
        """total_messages=5 < MIN_MESSAGES=10. Should return []."""
        strat = GEXImbalance()
        data = _make_data(total_messages=5, underlying_price=100.0)
        signals = strat.evaluate(data)

        assert signals == []

    # ------------------------------------------------------------------
    # 5. Low confidence → no signal
    # ------------------------------------------------------------------

    def test_low_confidence_no_signal(self):
        """Ratio just barely above CALL_HEAVY_RATIO (0.6) with opposing ROC
        and low depth alignment → confidence < MIN_CONFIDENCE (0.10).
        Should return [].
        """
        strat = GEXImbalance()
        # ratio = 0.6 → bias_strength = 0.0, norm_ratio = 0.0
        # depth with opposing bias (bid-heavy for SHORT) → norm_depth ≈ 0.1
        # no VWAP data → norm_vwap = 0.0
        # no history → roc_modifier = 0.0
        # confidence = (0.0 + 0.0 + 0.1 + 0.0 + 0.0) / 5.0 = 0.02 < 0.10
        data = _make_data(
            call_gex=600,
            put_gex=1000,
            underlying_price=100.0,
            depth_snapshot={"total_bid_size": 900, "total_ask_size": 100},
        )
        signals = strat.evaluate(data)

        assert signals == []

    # ------------------------------------------------------------------
    # 6. VWAP directional check
    # ------------------------------------------------------------------

    def test_vwap_directional_check_long_wrong_side(self):
        """LONG bias but price ABOVE mean → _check_vwap_deviation returns None.
        With boundary ratio (call_gex=449, put_gex=1000 → ratio=0.449) the
        bias_strength is ~0, norm_vwap is 0, and depth is against bias →
        confidence < MIN_CONFIDENCE → no signal."""
        strat = GEXImbalance()
        # ratio=0.449 < 0.45 → LONG bias
        # bias_strength = (0.45 - 0.449) / 0.45 = 0.002
        # norm_ratio = 1.0 - (0.449 / 0.45) = 0.002
        # price=102 > mean=100 → deviation > 0 → LONG gets None from _check_vwap_deviation
        # depth bid-heavy=50/1000 → against LONG → norm_depth = 0.05
        # confidence = (0.002 + 0.002 + 0.05 + 0.0 + 0.0) / 5.0 = 0.011 < 0.10
        data = _make_data(
            call_gex=449,
            put_gex=1000,
            underlying_price=102.0,  # above mean of 100 → wrong side for LONG
            depth_snapshot={"total_bid_size": 50, "total_ask_size": 950},
        )
        signals = strat.evaluate(data)

        assert signals == []

    def test_vwap_directional_check_short_wrong_side(self):
        """SHORT bias but price BELOW mean → _check_vwap_deviation returns None.
        With boundary ratio (call_gex=601, put_gex=1000 → ratio=0.601) the
        bias_strength is ~0, norm_vwap is 0, and depth is against bias →
        confidence < MIN_CONFIDENCE → no signal."""
        strat = GEXImbalance()
        # ratio=0.601 > 0.60 → SHORT bias
        # bias_strength = (0.601 - 0.60) / (3.0 - 0.60) = 0.004
        # norm_ratio = min(1.0, (0.601 - 0.60) / (3.0 - 0.60)) = 0.004
        # price=98 < mean=100 → deviation < 0 → SHORT gets None from _check_vwap_deviation
        # depth ask-heavy=50/1000 → against SHORT → norm_depth = 0.05
        # confidence = (0.004 + 0.004 + 0.05 + 0.0 + 0.0) / 5.0 = 0.012 < 0.10
        data = _make_data(
            call_gex=601,
            put_gex=1000,
            underlying_price=98.0,  # below mean of 100 → wrong side for SHORT
            depth_snapshot={"total_bid_size": 950, "total_ask_size": 50},
        )
        signals = strat.evaluate(data)

        assert signals == []

    # ------------------------------------------------------------------
    # 7. Strong bias → higher confidence than marginal
    # ------------------------------------------------------------------

    def test_strong_bias_higher_confidence(self):
        """Extreme ratio (call_gex=100, put_gex=9000 → ratio≈0.011) should produce
        higher confidence than marginal ratio (call_gex=400, put_gex=600 → ratio≈0.667).
        """
        # Strong bias: extreme put-heavy
        strong = GEXImbalance()
        strong_data = _make_data(
            call_gex=100,
            put_gex=9000,
            underlying_price=100.0,
        )
        strong_signals = strong.evaluate(strong_data)
        assert len(strong_signals) == 1
        strong_conf = strong_signals[0].confidence

        # Marginal bias: barely call-heavy
        marginal = GEXImbalance()
        marginal_data = _make_data(
            call_gex=400,
            put_gex=600,
            underlying_price=100.0,
        )
        marginal_signals = marginal.evaluate(marginal_data)
        assert len(marginal_signals) == 1
        marginal_conf = marginal_signals[0].confidence

        assert strong_conf > marginal_conf
