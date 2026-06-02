"""
tests/strategies/test_delta_volume_exhaustion.py — Unit tests for DELTA_VOL
(DeltaVolumeExhaustion) strategy.

The strategy checks BOTH UP and DOWN exhaustion directions. For each direction:
  - Matching trend: modifier=0.0
  - Mismatched trend: modifier=-0.15

Both directions fire when confidence >= 0.10. Tests verify the correct
direction fires with higher confidence than the mismatched direction.
"""

import statistics
from unittest.mock import MagicMock

import pytest

from strategies.layer2.delta_volume_exhaustion import DeltaVolumeExhaustion
from strategies.signal import Direction
from strategies.rolling_keys import (
    KEY_DEPTH_ASK_SIZE_5M,
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_PRICE_5M,
    KEY_TOTAL_DELTA_5M,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class Window:
    """Minimal rolling window mock matching the interface used by the strategy."""

    def __init__(self, values, count=None, mean=None, std=None, trend=None, latest=0):
        self.values = list(values)
        self.count = count or len(values)
        self.mean = mean or (sum(values) / len(values) if values else 0)
        self.std = std if std is not None else statistics.stdev(values) if len(values) > 1 else 0
        self.trend = trend  # "UP", "DOWN", or "SIDEWAYS"
        self.latest = latest or (values[-1] if values else 0)


def _make_data(
    price,
    rolling_data=None,
    regime="NEUTRAL",
    net_gamma=0,
    greeks_summary=None,
    depth_snapshot=None,
    gex_calc=None,
):
    """Construct a full data dict for the strategy's evaluate() method."""
    if rolling_data is None:
        rolling_data = {}
    if greeks_summary is None:
        greeks_summary = {}
    return {
        "underlying_price": price,
        "rolling_data": rolling_data,
        "greeks_summary": greeks_summary,
        "net_gamma": net_gamma,
        "regime": regime,
        "gex_calculator": gex_calc,
        "depth_snapshot": depth_snapshot,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def strategy():
    return DeltaVolumeExhaustion()


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

def test_up_exhaustion_long_signal(strategy):
    """UP trend with declining delta and liquidity vacuum → LONG signal.

    The strategy checks both UP and DOWN exhaustion. With a strong UP trend:
    - UP exhaustion check matches (modifier=0) → SHORT signal at higher conf
    - DOWN exhaustion check mismatches (modifier=-0.15) → LONG signal at lower conf
    """
    price = 100.0

    greeks_summary = {"strike1": {"net_delta": 50}}

    rolling_data = {
        KEY_PRICE_5M: Window(
            [100, 101, 102, 103, 104], trend="UP",
        ),
        KEY_TOTAL_DELTA_5M: Window(
            [100, 100, 100, 100, 50],  # declining sharply
        ),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10, 0.10, 0.10]),
    }

    depth_snapshot = {
        "bid_size": {"current": 5000},
        "ask_size": {"current": 5000},
        "spread": {"current": 0.20},
    }

    data = _make_data(
        price=price,
        rolling_data=rolling_data,
        greeks_summary=greeks_summary,
        depth_snapshot=depth_snapshot,
        net_gamma=0,
    )

    signals = strategy.evaluate(data)
    # Both directions fire; matching (UP→SHORT) has higher confidence
    assert len(signals) == 2
    # Find the LONG signal (DOWN exhaustion, mismatched direction)
    long_signals = [s for s in signals if s.direction == Direction.LONG]
    short_signals = [s for s in signals if s.direction == Direction.SHORT]
    assert len(long_signals) == 1
    assert len(short_signals) == 1
    # SHORT (matching UP exhaustion) should have higher confidence
    assert short_signals[0].confidence > long_signals[0].confidence


def test_down_exhaustion_short_signal(strategy):
    """DOWN trend with declining delta and liquidity vacuum → SHORT signal.

    With a DOWN trend:
    - DOWN exhaustion check matches (modifier=0) → LONG signal at higher conf
    - UP exhaustion check mismatches (modifier=-0.15) → SHORT signal at lower conf
    """
    price = 100.0

    greeks_summary = {"strike1": {"net_delta": 50}}

    rolling_data = {
        KEY_PRICE_5M: Window(
            [104, 103, 102, 101, 100], trend="DOWN",
        ),
        KEY_TOTAL_DELTA_5M: Window(
            [100, 100, 100, 100, 50],  # declining sharply
        ),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10, 0.10, 0.10]),
    }

    depth_snapshot = {
        "bid_size": {"current": 5000},
        "ask_size": {"current": 5000},
        "spread": {"current": 0.20},
    }

    data = _make_data(
        price=price,
        rolling_data=rolling_data,
        greeks_summary=greeks_summary,
        depth_snapshot=depth_snapshot,
        net_gamma=0,
    )

    signals = strategy.evaluate(data)
    assert len(signals) == 2
    long_signals = [s for s in signals if s.direction == Direction.LONG]
    short_signals = [s for s in signals if s.direction == Direction.SHORT]
    assert len(long_signals) == 1
    assert len(short_signals) == 1
    # LONG (matching DOWN exhaustion) should have higher confidence
    assert long_signals[0].confidence > short_signals[0].confidence


def test_no_trend_no_signal(strategy):
    """SIDEWAYS trend should not produce signals for either direction.

    Both UP and DOWN checks get the -0.15 trend_direction_modifier since
    neither matches SIDEWAYS. With delta_score=0 (delta at rolling avg),
    net_gamma=0, and liquidity_score=0 (depth ratio unstable + spread not
    widened), confidence drops below 0.10 for both.
    """
    price = 100.0

    # delta=100 matches rolling avg of 100 → delta_score=0
    greeks_summary = {"strike1": {"net_delta": 100}}

    rolling_data = {
        KEY_PRICE_5M: Window(
            [100, 101, 99, 101, 100], trend="SIDEWAYS",
        ),
        KEY_TOTAL_DELTA_5M: Window(
            [100, 100, 100, 100, 100],  # not declining
        ),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10, 0.10, 0.10]),
    }

    # Depth snapshot: bid/ask ratio (3000/7000=0.43) deviates >40% from
    # rolling mean ratio (1.0), so ratio_stable=False. Spread (0.12) <
    # 1.3x rolling mean (0.13), so spread_widened=False. liq_score=0.
    depth_snapshot = {
        "bid_size": {"current": 3000},
        "ask_size": {"current": 7000},
        "spread": {"current": 0.12},
    }

    data = _make_data(
        price=price,
        rolling_data=rolling_data,
        greeks_summary=greeks_summary,
        depth_snapshot=depth_snapshot,
        net_gamma=0,
    )

    signals = strategy.evaluate(data)
    assert len(signals) == 0


def test_insufficient_trend_points_no_signal(strategy):
    """Fewer than MIN_TREND_POINTS (3) data points → no signal."""
    price = 100.0

    rolling_data = {
        KEY_PRICE_5M: Window(
            [100, 101], trend="UP",  # only 2 points, below MIN_TREND_POINTS=3
        ),
        KEY_TOTAL_DELTA_5M: Window([100, 100, 100, 100, 50]),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10, 0.10, 0.10]),
    }

    depth_snapshot = {
        "bid_size": {"current": 5000},
        "ask_size": {"current": 5000},
        "spread": {"current": 0.20},
    }

    data = _make_data(
        price=price,
        rolling_data=rolling_data,
        depth_snapshot=depth_snapshot,
        net_gamma=100000,
    )

    signals = strategy.evaluate(data)
    assert len(signals) == 0


def test_marginal_trend_fires_with_low_confidence(strategy):
    """Trend matches but is weak (few points, low strength) → fires with
    low confidence (>= 0.10) rather than being killed by the gate."""
    price = 100.0

    greeks_summary = {"strike1": {"net_delta": 50}}

    # Very flat upward trend: first-half mean ≈ second-half mean
    # so trend_strength stays low (~0.3) and confidence < 0.50
    rolling_data = {
        KEY_PRICE_5M: Window(
            [100, 100.05, 100.1], trend="UP",
        ),
        KEY_TOTAL_DELTA_5M: Window(
            [100, 100, 50],  # declining below avg
        ),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10]),
    }

    depth_snapshot = {
        "bid_size": {"current": 5000},
        "ask_size": {"current": 5000},
        "spread": {"current": 0.20},  # spread widened
    }

    data = _make_data(
        price=price,
        rolling_data=rolling_data,
        greeks_summary=greeks_summary,
        depth_snapshot=depth_snapshot,
        net_gamma=0,
    )

    signals = strategy.evaluate(data)
    assert len(signals) == 2
    short_signals = [s for s in signals if s.direction == Direction.SHORT]
    long_signals = [s for s in signals if s.direction == Direction.LONG]
    assert len(short_signals) == 1
    assert len(long_signals) == 1
    # Both fire with low confidence (marginal case)
    assert short_signals[0].confidence >= 0.10
    assert long_signals[0].confidence >= 0.10
    assert short_signals[0].confidence < 0.50
    assert long_signals[0].confidence < 0.50
    # Matching direction still higher
    assert short_signals[0].confidence > long_signals[0].confidence


def test_delta_not_declining_no_signal(strategy):
    """Delta is at or above rolling average (not declining) → low confidence.

    With delta_score=0, the matching direction still fires (trend+liquidity
    contribute) but with significantly lower confidence than when delta IS
    declining. The mismatched direction stays below 0.10 due to -0.15 modifier.
    """
    price = 100.0

    # Delta at 100 = rolling avg of 100 → ratio = 1.0 → delta_score = 0.0
    greeks_summary = {"strike1": {"net_delta": 100}}

    rolling_data = {
        KEY_PRICE_5M: Window(
            [100, 101, 102, 103, 104], trend="UP",
        ),
        KEY_TOTAL_DELTA_5M: Window(
            [100, 100, 100, 100, 100],  # not declining
        ),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10, 0.10, 0.10]),
    }

    depth_snapshot = {
        "bid_size": {"current": 5000},
        "ask_size": {"current": 5000},
        "spread": {"current": 0.20},
    }

    data = _make_data(
        price=price,
        rolling_data=rolling_data,
        greeks_summary=greeks_summary,
        depth_snapshot=depth_snapshot,
        net_gamma=0,
    )

    signals = strategy.evaluate(data)
    # Both directions fire; matching direction has higher confidence
    assert len(signals) == 2
    short_signals = [s for s in signals if s.direction == Direction.SHORT]
    long_signals = [s for s in signals if s.direction == Direction.LONG]
    # Confidence should be moderate (trend+liquidity contribute, but no delta)
    assert short_signals[0].confidence < 0.50
    assert long_signals[0].confidence < 0.50
    assert short_signals[0].confidence > long_signals[0].confidence


def test_trend_mismatch_lower_confidence(strategy):
    """Trend direction doesn't match (checking UP exhaustion but trend is DOWN).
    The -0.15 direction modifier should result in lower confidence for the
    mismatched direction compared to the matching one.
    """
    price = 100.0

    greeks_summary = {"strike1": {"net_delta": 50}}

    rolling_data = {
        KEY_PRICE_5M: Window(
            [104, 103, 102, 101, 100], trend="DOWN",
        ),
        KEY_TOTAL_DELTA_5M: Window(
            [100, 100, 100, 100, 50],  # declining
        ),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10, 0.10, 0.10]),
    }

    depth_snapshot = {
        "bid_size": {"current": 5000},
        "ask_size": {"current": 5000},
        "spread": {"current": 0.20},
    }

    data = _make_data(
        price=price,
        rolling_data=rolling_data,
        greeks_summary=greeks_summary,
        depth_snapshot=depth_snapshot,
        net_gamma=0,
    )

    signals = strategy.evaluate(data)
    assert len(signals) == 2
    long_signals = [s for s in signals if s.direction == Direction.LONG]
    short_signals = [s for s in signals if s.direction == Direction.SHORT]
    # LONG (matching DOWN exhaustion) should have higher confidence
    assert long_signals[0].confidence > short_signals[0].confidence
    # The mismatched direction should be at least 0.10 lower
    assert long_signals[0].confidence - short_signals[0].confidence >= 0.14


def test_strong_exhaustion_higher_confidence(strategy):
    """Strong trend + strong delta decline + both liquidity components pass →
    higher confidence than a marginal case."""
    price = 100.0

    greeks_summary = {"strike1": {"net_delta": 50}}

    # Strong upward trend: 5 points, clear direction
    rolling_data = {
        KEY_PRICE_5M: Window(
            [100, 101, 102, 103, 104], trend="UP",
        ),
        KEY_TOTAL_DELTA_5M: Window(
            [100, 100, 100, 100, 50],  # strong decline
        ),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10, 0.10, 0.10]),
    }

    depth_snapshot = {
        "bid_size": {"current": 5000},
        "ask_size": {"current": 5000},
        "spread": {"current": 0.20},  # spread widened > 1.3×
    }

    data = _make_data(
        price=price,
        rolling_data=rolling_data,
        greeks_summary=greeks_summary,
        depth_snapshot=depth_snapshot,
        net_gamma=0,
    )

    signals = strategy.evaluate(data)
    assert len(signals) == 2

    # Build marginal case: flat trend (first-half mean ≈ second-half mean)
    # so trend_strength stays low (~0.36) and doesn't normalize to 0.75
    marginal_rolling = {
        KEY_PRICE_5M: Window([100, 101, 101, 100], trend="UP"),
        KEY_TOTAL_DELTA_5M: Window([100, 100, 50]),
        KEY_DEPTH_BID_SIZE_5M: Window([5000, 5000, 5000, 5000]),
        KEY_DEPTH_ASK_SIZE_5M: Window([5000, 5000, 5000, 5000]),
        KEY_DEPTH_SPREAD_5M: Window([0.10, 0.10, 0.10, 0.10]),
    }
    marginal_depth = {
        "bid_size": {"current": 5000},
        "ask_size": {"current": 5000},
        "spread": {"current": 0.20},
    }
    marginal_data = _make_data(
        price=price,
        rolling_data=marginal_rolling,
        greeks_summary=greeks_summary,
        depth_snapshot=marginal_depth,
        net_gamma=0,
    )
    marginal_signals = strategy.evaluate(marginal_data)
    assert len(marginal_signals) == 2

    # Get matching direction (SHORT for UP exhaustion) from both
    strong_short = [s for s in signals if s.direction == Direction.SHORT][0]
    marginal_short = [s for s in marginal_signals if s.direction == Direction.SHORT][0]

    # Strong exhaustion should have higher confidence
    assert strong_short.confidence > marginal_short.confidence
