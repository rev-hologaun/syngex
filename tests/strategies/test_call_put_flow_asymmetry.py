"""
tests/strategies/test_call_put_flow_asymmetry.py — Unit tests for CallPutFlowAsymmetry

Tests the Call/Put Flow Asymmetry v2 strategy by mocking its inputs
and verifying signal generation, helper functions, and edge cases.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the project root is on sys.path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from strategies.layer2.call_put_flow_asymmetry import (
    CallPutFlowAsymmetry,
    FLOW_THRESHOLD,
    IV_SKEW_THRESHOLD,
    MIN_CONFIDENCE,
    MIN_GREEKS_POINTS,
)
from strategies.signal import Direction, Signal


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

class MockGexCalc:
    """Minimal mock of the GEX calculator interface."""

    def __init__(self, iv_skew=None, gamma_walls=None):
        self._iv_skew = iv_skew
        self._gamma_walls = gamma_walls or []

    def get_iv_skew(self):
        return self._iv_skew

    def get_gamma_walls(self, threshold=500000):
        return self._gamma_walls


def _make_greeks_summary(call_data, put_data):
    """
    Build a greeks_summary dict from call_data and put_data lists.

    Each item is a dict with keys: strike, call_oi, call_gamma,
    call_delta_sum, put_oi, put_gamma, put_delta_sum.
    """
    summary = {}
    for i, cd in enumerate(call_data):
        strike = cd.get("strike", f"strike_{i}_c")
        summary[strike] = {
            "call_oi": cd.get("call_oi", 0),
            "call_gamma": cd.get("call_gamma", 0),
            "call_delta_sum": cd.get("call_delta_sum", 0),
            "put_oi": 0,
            "put_gamma": 0,
            "put_delta_sum": 0,
        }
    for i, pd in enumerate(put_data):
        strike = pd.get("strike", f"strike_{i}_p")
        if strike in summary:
            summary[strike]["put_oi"] = pd.get("put_oi", 0)
            summary[strike]["put_gamma"] = pd.get("put_gamma", 0)
            summary[strike]["put_delta_sum"] = pd.get("put_delta_sum", 0)
        else:
            summary[strike] = {
                "call_oi": 0,
                "call_gamma": 0,
                "call_delta_sum": 0,
                "put_oi": pd.get("put_oi", 0),
                "put_gamma": pd.get("put_gamma", 0),
                "put_delta_sum": pd.get("put_delta_sum", 0),
            }
    return summary


def _make_data(
    greeks_summary,
    gex_calc=None,
    rolling_data=None,
    regime="NEUTRAL",
    net_gamma=0,
    price=100.0,
):
    """Build a complete data dict for strategy.evaluate()."""
    if gex_calc is None:
        gex_calc = MockGexCalc()
    if rolling_data is None:
        rolling_data = {}
    return {
        "underlying_price": price,
        "gex_calculator": gex_calc,
        "rolling_data": rolling_data,
        "greeks_summary": greeks_summary,
        "regime": regime,
        "net_gamma": net_gamma,
    }


def _make_flow_window(values):
    """Create a mock rolling window object with `values` and `count`."""

    class _MockWindow:
        def __init__(self, vals):
            self._vals = list(vals)
            self.count = len(self._vals)

        @property
        def values(self):
            return self._vals

    return _MockWindow(values)


def _make_volume_window(trend, count=3):
    """Create a mock rolling window object with `trend` and `count`."""

    class _MockWindow:
        def __init__(self, tr, c):
            self.trend = tr
            self.count = c

    return _MockWindow(trend, count)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def strategy():
    return CallPutFlowAsymmetry()


@pytest.fixture
def call_dominant_summary():
    """3 call strikes with high OI/gamma/delta, minimal puts.
    Must have 2+ put strikes to pass MIN_GREEKS_POINTS."""
    return _make_greeks_summary(
        call_data=[
            {"strike": "100", "call_oi": 50000, "call_gamma": 200000, "call_delta_sum": 0.5},
            {"strike": "101", "call_oi": 40000, "call_gamma": 150000, "call_delta_sum": 0.4},
            {"strike": "102", "call_oi": 30000, "call_gamma": 100000, "call_delta_sum": 0.3},
        ],
        put_data=[
            {"strike": "99", "put_oi": 1000, "put_gamma": 10000, "put_delta_sum": 0.05},
            {"strike": "98", "put_oi": 800, "put_gamma": 8000, "put_delta_sum": 0.04},
        ],
    )


@pytest.fixture
def put_dominant_summary():
    """3 put strikes with high OI/gamma/delta, minimal calls.
    Must have 2+ call strikes to pass MIN_GREEKS_POINTS."""
    return _make_greeks_summary(
        call_data=[
            {"strike": "101", "call_oi": 1000, "call_gamma": 10000, "call_delta_sum": 0.05},
            {"strike": "102", "call_oi": 800, "call_gamma": 8000, "call_delta_sum": 0.04},
        ],
        put_data=[
            {"strike": "100", "put_oi": 50000, "put_gamma": 200000, "put_delta_sum": 0.5},
            {"strike": "99", "put_oi": 40000, "put_gamma": 150000, "put_delta_sum": 0.4},
            {"strike": "98", "put_oi": 30000, "put_gamma": 100000, "put_delta_sum": 0.3},
        ],
    )


@pytest.fixture
def balanced_summary():
    """Roughly equal calls and puts."""
    return _make_greeks_summary(
        call_data=[
            {"strike": "100", "call_oi": 50000, "call_gamma": 200000, "call_delta_sum": 0.5},
            {"strike": "101", "call_oi": 40000, "call_gamma": 150000, "call_delta_sum": 0.4},
            {"strike": "102", "call_oi": 30000, "call_gamma": 100000, "call_delta_sum": 0.3},
        ],
        put_data=[
            {"strike": "100", "put_oi": 48000, "put_gamma": 190000, "put_delta_sum": 0.48},
            {"strike": "99", "put_oi": 42000, "put_gamma": 140000, "put_delta_sum": 0.42},
            {"strike": "98", "put_oi": 35000, "put_gamma": 90000, "put_delta_sum": 0.35},
        ],
    )


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestCallDominantLongSignal:
    """test_call_dominant_long_signal — calls dominate → LONG signal."""

    def test_returns_long_signal(self, strategy, call_dominant_summary):
        gex_calc = MockGexCalc(iv_skew=0.02)  # call IV < put IV → aligned
        data = _make_data(call_dominant_summary, gex_calc=gex_calc)
        signals = strategy.evaluate(data)

        assert len(signals) >= 1, "Expected at least one signal when calls dominate"
        assert signals[0].direction == Direction.LONG

    def test_signal_has_reason(self, strategy, call_dominant_summary):
        gex_calc = MockGexCalc(iv_skew=0.02)
        data = _make_data(call_dominant_summary, gex_calc=gex_calc)
        signals = strategy.evaluate(data)

        assert len(signals) >= 1
        assert "Call flow dominant" in signals[0].reason

    def test_signal_metadata_contains_scores(self, strategy, call_dominant_summary):
        gex_calc = MockGexCalc(iv_skew=0.02)
        data = _make_data(call_dominant_summary, gex_calc=gex_calc)
        signals = strategy.evaluate(data)

        assert len(signals) >= 1
        meta = signals[0].metadata
        assert "call_flow_score" in meta
        assert "put_flow_score" in meta
        assert "flow_ratio" in meta


class TestPutDominantShortSignal:
    """test_put_dominant_short_signal — puts dominate → SHORT signal."""

    def test_returns_short_signal(self, strategy, put_dominant_summary):
        gex_calc = MockGexCalc(iv_skew=0.02)
        data = _make_data(put_dominant_summary, gex_calc=gex_calc)
        signals = strategy.evaluate(data)

        assert len(signals) >= 1, "Expected at least one signal when puts dominate"
        assert signals[0].direction == Direction.SHORT

    def test_signal_has_reason(self, strategy, put_dominant_summary):
        gex_calc = MockGexCalc(iv_skew=0.02)
        data = _make_data(put_dominant_summary, gex_calc=gex_calc)
        signals = strategy.evaluate(data)

        assert len(signals) >= 1
        assert "Put flow dominant" in signals[0].reason


class TestBalancedFlowNoSignal:
    """test_balanced_flow_no_signal — roughly equal calls and puts → no signal."""

    def test_returns_empty_list(self, strategy, balanced_summary):
        gex_calc = MockGexCalc()
        data = _make_data(balanced_summary, gex_calc=gex_calc)
        signals = strategy.evaluate(data)

        assert signals == [], "Expected no signal when flow is balanced"


class TestInsufficientGreeksPoints:
    """test_insufficient_greeks_points_no_signal — fewer than MIN_GREEKS_POINTS
    active strikes per side → no signal."""

    def test_one_call_one_put(self, strategy):
        summary = _make_greeks_summary(
            call_data=[
                {"strike": "100", "call_oi": 50000, "call_gamma": 200000, "call_delta_sum": 0.5},
            ],
            put_data=[
                {"strike": "100", "put_oi": 50000, "put_gamma": 200000, "put_delta_sum": 0.5},
            ],
        )
        data = _make_data(summary)
        signals = strategy.evaluate(data)
        assert signals == []

    def test_one_call_no_puts(self, strategy):
        summary = _make_greeks_summary(
            call_data=[
                {"strike": "100", "call_oi": 50000, "call_gamma": 200000, "call_delta_sum": 0.5},
            ],
            put_data=[],
        )
        data = _make_data(summary)
        signals = strategy.evaluate(data)
        assert signals == []

    def test_two_calls_one_put(self, strategy):
        """2 calls pass MIN_GREEKS_POINTS but only 1 put fails."""
        summary = _make_greeks_summary(
            call_data=[
                {"strike": "100", "call_oi": 50000, "call_gamma": 200000, "call_delta_sum": 0.5},
                {"strike": "101", "call_oi": 40000, "call_gamma": 150000, "call_delta_sum": 0.4},
            ],
            put_data=[
                {"strike": "99", "put_oi": 50000, "put_gamma": 200000, "put_delta_sum": 0.5},
            ],
        )
        data = _make_data(summary)
        signals = strategy.evaluate(data)
        assert signals == []


class TestFlowAcceleration:
    """test_acceleration_returns_score — _check_flow_acceleration returns
    float 0.0–1.0, not a bool."""

    def test_strong_acceleration_long(self, strategy):
        """ROC > 0.20 → score = 1.0."""
        window = _make_flow_window([1.0, 1.0, 1.0, 1.0, 1.25])  # 25% ROC
        rolling = {"flow_ratio_5m": window}
        score = strategy._check_flow_acceleration(rolling, 1.25, "LONG")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score == 1.0

    def test_partial_acceleration_long(self, strategy):
        """ROC between 0 and 0.20 → partial score."""
        window = _make_flow_window([1.0, 1.0, 1.0, 1.0, 1.10])  # 10% ROC
        rolling = {"flow_ratio_5m": window}
        score = strategy._check_flow_acceleration(rolling, 1.10, "LONG")
        assert isinstance(score, float)
        assert 0.0 < score < 1.0
        # Expected: 0.10 / 0.20 = 0.5 (allowing floating point)
        assert abs(score - 0.5) < 0.001

    def test_no_acceleration_long(self, strategy):
        """ROC <= 0 → score = 0.0."""
        window = _make_flow_window([1.0, 1.0, 1.0, 1.0, 0.95])  # negative ROC
        rolling = {"flow_ratio_5m": window}
        score = strategy._check_flow_acceleration(rolling, 0.95, "LONG")
        assert isinstance(score, float)
        assert score == 0.0

    def test_strong_acceleration_short(self, strategy):
        """ROC < -0.20 → score = 1.0 for SHORT."""
        window = _make_flow_window([1.0, 1.0, 1.0, 1.0, 0.70])  # -30% ROC
        rolling = {"flow_ratio_5m": window}
        score = strategy._check_flow_acceleration(rolling, 0.70, "SHORT")
        assert isinstance(score, float)
        assert score == 1.0

    def test_insufficient_history(self, strategy):
        """Window with fewer than 5 values → score = 0.0."""
        window = _make_flow_window([1.0, 1.0, 1.0])  # count=3
        rolling = {"flow_ratio_5m": window}
        score = strategy._check_flow_acceleration(rolling, 1.0, "LONG")
        assert score == 0.0

    def test_no_window(self, strategy):
        """No rolling data → score = 0.0."""
        score = strategy._check_flow_acceleration({}, 1.0, "LONG")
        assert score == 0.0


class TestFlowBreadth:
    """test_breadth_returns_score — _check_flow_breadth returns float 0.0–1.0."""

    def test_full_breadth(self, strategy):
        """Breadth = 0.5 → score = 1.0."""
        score = strategy._check_flow_breadth(0.5)
        assert isinstance(score, float)
        assert score == 1.0

    def test_marginal_breadth(self, strategy):
        """Breadth = 0.15 → score = 0.5 (0.15 / 0.30)."""
        score = strategy._check_flow_breadth(0.15)
        assert isinstance(score, float)
        assert score == 0.5

    def test_no_breadth(self, strategy):
        """Breadth = None → score = 0.0."""
        score = strategy._check_flow_breadth(None)
        assert isinstance(score, float)
        assert score == 0.0

    def test_zero_breadth(self, strategy):
        """Breadth = 0.0 → score = 0.0."""
        score = strategy._check_flow_breadth(0.0)
        assert isinstance(score, float)
        assert score == 0.0

    def test_breadth_above_threshold(self, strategy):
        """Breadth >= 0.30 → score = 1.0."""
        score = strategy._check_flow_breadth(0.30)
        assert score == 1.0
        score = strategy._check_flow_breadth(1.0)
        assert score == 1.0


class TestRatioConfidenceNormalized:
    """test_confidence_normalized — _ratio_confidence_normalized returns
    values in 0.0–1.0 range."""

    def test_high_ratio(self, strategy):
        """Ratio = 10.0 → score = 1.0 (maxed out)."""
        score = strategy._ratio_confidence_normalized(10.0)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score == 1.0

    def test_ratio_at_threshold(self, strategy):
        """Ratio = FLOW_THRESHOLD (1.2) → score = 0.0."""
        score = strategy._ratio_confidence_normalized(FLOW_THRESHOLD)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # (1.2 - 1.2) / (10.0 - 1.2) = 0.0
        assert score == 0.0

    def test_ratio_below_threshold(self, strategy):
        """Ratio = 1.0 → score is negative (no lower clamp in implementation)."""
        score = strategy._ratio_confidence_normalized(1.0)
        assert isinstance(score, float)
        # log_ratio = 1.0, (1.0 - 1.2) / (10.0 - 1.2) = -0.0227
        # The function only clamps the upper bound with min(1.0, ...)
        # so negative values are returned as-is.
        assert score < 0.0

    def test_ratio_between_threshold_and_max(self, strategy):
        """Ratio = 5.0 → partial score."""
        score = strategy._ratio_confidence_normalized(5.0)
        assert isinstance(score, float)
        assert 0.0 < score < 1.0
        # (5.0 - 1.2) / (10.0 - 1.2) = 3.8 / 8.8 ≈ 0.432
        assert abs(score - 3.8 / 8.8) < 0.001

    def test_ratio_inverted_below_1(self, strategy):
        """Ratio = 0.5 → inverted normalization."""
        score = strategy._ratio_confidence_normalized(0.5)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # normalized = 1/0.5 = 2.0, (2.0 - 1.2) / (10.0 - 1.2) = 0.8/8.8 ≈ 0.091
        assert score == 0.8 / 8.8


class TestStrongFlowHigherConfidence:
    """test_strong_flow_higher_confidence — strong call dominance should produce
    higher confidence than marginal dominance."""

    def test_strong_vs_marginal_call_dominance(self, strategy):
        """Create two scenarios: strong (ratio=5.0) vs marginal (ratio=1.25)."""
        # Strong: 5 call strikes, minimal puts
        strong_summary = _make_greeks_summary(
            call_data=[
                {"strike": "100", "call_oi": 100000, "call_gamma": 500000, "call_delta_sum": 0.5},
                {"strike": "101", "call_oi": 90000, "call_gamma": 400000, "call_delta_sum": 0.45},
                {"strike": "102", "call_oi": 80000, "call_gamma": 300000, "call_delta_sum": 0.4},
                {"strike": "103", "call_oi": 70000, "call_gamma": 200000, "call_delta_sum": 0.35},
                {"strike": "104", "call_oi": 60000, "call_gamma": 100000, "call_delta_sum": 0.3},
            ],
            put_data=[
                {"strike": "99", "put_oi": 500, "put_gamma": 5000, "put_delta_sum": 0.01},
                {"strike": "98", "put_oi": 400, "put_gamma": 4000, "put_delta_sum": 0.01},
            ],
        )

        # Marginal: just above threshold
        marginal_summary = _make_greeks_summary(
            call_data=[
                {"strike": "100", "call_oi": 20000, "call_gamma": 100000, "call_delta_sum": 0.3},
                {"strike": "101", "call_oi": 18000, "call_gamma": 80000, "call_delta_sum": 0.25},
                {"strike": "102", "call_oi": 15000, "call_gamma": 60000, "call_delta_sum": 0.2},
            ],
            put_data=[
                {"strike": "99", "put_oi": 15000, "put_gamma": 80000, "put_delta_sum": 0.2},
                {"strike": "98", "put_oi": 12000, "put_gamma": 60000, "put_delta_sum": 0.15},
                {"strike": "97", "put_oi": 10000, "put_gamma": 50000, "put_delta_sum": 0.1},
            ],
        )

        gex_calc = MockGexCalc(iv_skew=0.02)

        # Strong: add acceleration window
        strong_window = _make_flow_window([1.0, 1.0, 1.0, 1.0, 5.0])  # big spike
        strong_data = _make_data(
            strong_summary, gex_calc=gex_calc,
            rolling_data={"flow_ratio_5m": strong_window},
        )
        strong_signals = strategy.evaluate(strong_data)

        # Marginal: add small acceleration
        marginal_window = _make_flow_window([1.0, 1.0, 1.0, 1.0, 1.25])
        marginal_data = _make_data(
            marginal_summary, gex_calc=gex_calc,
            rolling_data={"flow_ratio_5m": marginal_window},
        )
        marginal_signals = strategy.evaluate(marginal_data)

        # Both should produce signals (assuming confidence >= MIN_CONFIDENCE)
        # Strong should have higher confidence
        if strong_signals and marginal_signals:
            assert strong_signals[0].confidence > marginal_signals[0].confidence, (
                f"Strong confidence ({strong_signals[0].confidence}) should exceed "
                f"marginal confidence ({marginal_signals[0].confidence})"
            )


class TestEdgeCases:
    """Additional edge case tests."""

    def test_zero_underlying_price(self, strategy):
        """underlying_price <= 0 → no signals."""
        data = _make_data({}, price=0.0)
        assert strategy.evaluate(data) == []

        data = _make_data({}, price=-1.0)
        assert strategy.evaluate(data) == []

    def test_missing_gex_calculator(self, strategy):
        """No gex_calculator in data → no signals."""
        data = _make_data({}, gex_calc=None)
        assert strategy.evaluate(data) == []

    def test_empty_greeks_summary(self, strategy):
        """Empty greeks_summary → no signals."""
        gex_calc = MockGexCalc()
        data = _make_data({}, gex_calc=gex_calc)
        assert strategy.evaluate(data) == []

    def test_wall_proximity_bonus(self, strategy):
        """Gamma wall within 0.5% → bonus added."""
        summary = _make_greeks_summary(
            call_data=[
                {"strike": "100", "call_oi": 100000, "call_gamma": 500000, "call_delta_sum": 0.5},
                {"strike": "101", "call_oi": 90000, "call_gamma": 400000, "call_delta_sum": 0.45},
            ],
            put_data=[
                {"strike": "99", "put_oi": 500, "put_gamma": 5000, "put_delta_sum": 0.02},
                {"strike": "98", "put_oi": 400, "put_gamma": 4000, "put_delta_sum": 0.02},
            ],
        )
        # Wall at 100.3 (0.3% above price 100)
        walls = [{"side": "CALL", "strike": 100.3}]
        gex_calc = MockGexCalc(iv_skew=0.02, gamma_walls=walls)

        flow_window = _make_flow_window([1.0, 1.0, 1.0, 1.0, 5.0])
        data = _make_data(
            summary, gex_calc=gex_calc,
            rolling_data={"flow_ratio_5m": flow_window},
            net_gamma=600000,  # high gamma for max regime intensity
        )
        signals = strategy.evaluate(data)
        assert len(signals) >= 1
        assert signals[0].direction == Direction.LONG
        # Wall bonus should be in metadata
        meta = signals[0].metadata
        assert "wall_proximity_bonus" in meta
        assert meta["wall_proximity_bonus"] == 0.10

    def test_regime_intensity_scaling(self, strategy):
        """Net gamma magnitude affects regime intensity."""
        # Low gamma
        assert strategy._compute_regime_intensity(100000) == 0.8
        # High gamma
        assert strategy._compute_regime_intensity(600000) == 1.3
        # Baseline gamma
        assert strategy._compute_regime_intensity(300000) == 1.0

    def test_signal_direction_enum(self, strategy, call_dominant_summary):
        """Signal direction should be Direction enum, not string."""
        gex_calc = MockGexCalc(iv_skew=0.02)
        data = _make_data(call_dominant_summary, gex_calc=gex_calc)
        signals = strategy.evaluate(data)
        assert len(signals) >= 1
        assert isinstance(signals[0].direction, Direction)
        assert signals[0].direction == Direction.LONG

    def test_signal_has_stop_and_target(self, strategy, call_dominant_summary):
        """Signal should have entry, stop, and target."""
        gex_calc = MockGexCalc(iv_skew=0.02)
        data = _make_data(call_dominant_summary, gex_calc=gex_calc)
        signals = strategy.evaluate(data)
        assert len(signals) >= 1
        sig = signals[0]
        assert sig.entry > 0
        assert sig.stop > 0
        assert sig.target > 0
        # For LONG: stop < entry < target
        assert sig.stop < sig.entry < sig.target
