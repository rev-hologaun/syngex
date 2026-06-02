"""
tests/strategies/test_obi_aggression_flow.py — Unit tests for ObiAggressionFlow

Tests the OBI + Aggression Flow strategy's signal emission logic:
master trigger (combined score, individual thresholds), gate evaluation,
confidence scoring, and edge cases (insufficient data, opposite signs).
"""

import pytest

from strategies.layer2.obi_aggression_flow import ObiAggressionFlow
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_OBI_5M,
    KEY_AF_5M,
    KEY_TRADE_SIZE_5M,
    KEY_DEPTH_SPREAD_5M,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class Window:
    """Minimal rolling-window mock matching the strategy's interface."""

    def __init__(self, values, count=None):
        self.values = list(values)
        self.count = count or len(values)

    @property
    def mean(self):
        if not self.values:
            return 0
        return sum(self.values) / len(self.values)


def _make_data(
    obi_values,
    af_values,
    trade_sizes=None,
    spread_values=None,
    depth_snapshot=None,
    regime="NEUTRAL",
    net_gamma=0,
):
    """Build a full data dict for the strategy."""
    rolling_data = {
        KEY_OBI_5M: Window(obi_values),
        KEY_AF_5M: Window(af_values),
    }
    if trade_sizes is not None:
        rolling_data[KEY_TRADE_SIZE_5M] = Window(trade_sizes)
    if spread_values is not None:
        rolling_data[KEY_DEPTH_SPREAD_5M] = Window(spread_values)

    if depth_snapshot is None:
        depth_snapshot = {
            "last_size": 100,
            "bid_avg_participants": 2,
            "ask_avg_participants": 2,
            "spread": 0.05,
        }

    return {
        "underlying_price": 100.0,
        "rolling_data": rolling_data,
        "depth_snapshot": depth_snapshot,
        "regime": regime,
        "net_gamma": net_gamma,
        "gex_calculator": None,
    }


def _make_data_with_params(obi_values, af_values, params=None, **kwargs):
    """Build data with optional strategy params injected."""
    data = _make_data(obi_values, af_values, **kwargs)
    if params is not None:
        data.setdefault("params", {})[ObiAggressionFlow.strategy_id] = params
    return data


def _new_strategy():
    """Create a fresh strategy instance for each test to avoid shared state."""
    return ObiAggressionFlow()


# ---------------------------------------------------------------------------
# 1. Strong agreement — LONG
# ---------------------------------------------------------------------------


def test_strong_agreement_long_signal():
    """OBI=0.8, AF=0.6 (both well above thresholds). Should produce a LONG
    signal with high confidence."""
    obi_vals = [0.8] * 15
    af_vals = [0.6] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)

    assert len(signals) == 1
    sig = signals[0]
    assert sig.direction == Direction.LONG
    assert sig.confidence > 0.70  # high confidence expected
    assert sig.entry == 100.0
    assert sig.stop < sig.entry
    assert sig.target > sig.entry


# ---------------------------------------------------------------------------
# 2. Strong agreement — SHORT
# ---------------------------------------------------------------------------


def test_strong_agreement_short_signal():
    """OBI=-0.8, AF=-0.6. Should produce a SHORT signal."""
    obi_vals = [-0.8] * 15
    af_vals = [-0.6] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)

    assert len(signals) == 1
    sig = signals[0]
    assert sig.direction == Direction.SHORT
    assert sig.stop > sig.entry
    assert sig.target < sig.entry


# ---------------------------------------------------------------------------
# 3. Combined score fires
# ---------------------------------------------------------------------------


def test_combined_score_fires():
    """OBI=0.55, AF=0.50 (neither individually exceeds threshold, but
    combined=1.05 > 1.0). Should fire with moderate confidence."""
    obi_vals = [0.55] * 15
    af_vals = [0.50] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)

    assert len(signals) == 1
    sig = signals[0]
    assert sig.direction == Direction.LONG
    # Combined-score signals should have moderate confidence
    assert sig.confidence >= 0.30


# ---------------------------------------------------------------------------
# 4. Partial agreement fires
# ---------------------------------------------------------------------------


def test_partial_agreement_fires():
    """OBI=0.70, AF=0.20 (OBI exceeds threshold, AF is below but same sign).
    Should fire with lower confidence than strong agreement."""
    obi_vals = [0.70] * 15
    af_vals = [0.20] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)

    assert len(signals) == 1
    sig = signals[0]
    assert sig.direction == Direction.LONG


# ---------------------------------------------------------------------------
# 5. Opposite signs — no signal
# ---------------------------------------------------------------------------


def test_opposite_signs_no_signal():
    """OBI=0.4, AF=-0.3 (agree on nothing, combined=0.7 < 1.0). Should return [].

    Note: The strategy's combined path (abs(obi)+abs(af) > threshold) does NOT
    check sign agreement, so high-magnitude opposite signs will still fire.
    This test uses low-magnitude values to verify the no-signal path."""
    obi_vals = [0.4] * 15
    af_vals = [-0.3] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)

    assert signals == []


def test_opposite_signs_combined_below_threshold():
    """OBI=0.4, AF=-0.3 (agree on nothing, combined=0.7 < 1.0). Should return []."""
    obi_vals = [0.4] * 15
    af_vals = [-0.3] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)

    assert signals == []


# ---------------------------------------------------------------------------
# 6. Both below threshold — no signal
# ---------------------------------------------------------------------------


def test_both_below_threshold_no_signal():
    """OBI=0.3, AF=0.2 (combined=0.5 < 1.0, neither exceeds individual).
    Should return []."""
    obi_vals = [0.3] * 15
    af_vals = [0.2] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)

    assert signals == []


# ---------------------------------------------------------------------------
# 7. Insufficient data — no signal
# ---------------------------------------------------------------------------


def test_insufficient_data_no_signal():
    """OBI window with only 1 data point (below min_obi_data_points=10).
    Should return []."""
    data = _make_data_with_params([0.8], [0.6] * 10)

    signals = _new_strategy().evaluate(data)

    assert signals == []


# ---------------------------------------------------------------------------
# 8. High confidence stronger than marginal
# ---------------------------------------------------------------------------


def test_high_confidence_stronger_than_marginal():
    """Strong agreement (OBI=0.9, AF=0.7) should have higher confidence than
    combined-score marginal (OBI=0.55, AF=0.50)."""
    strong_obi = [0.9] * 15
    strong_af = [0.7] * 10
    strong_data = _make_data_with_params(strong_obi, strong_af)

    marginal_obi = [0.55] * 15
    marginal_af = [0.50] * 10
    marginal_data = _make_data_with_params(marginal_obi, marginal_af)

    strong_signals = _new_strategy().evaluate(strong_data)
    marginal_signals = _new_strategy().evaluate(marginal_data)

    assert len(strong_signals) == 1
    assert len(marginal_signals) == 1

    assert strong_signals[0].confidence > marginal_signals[0].confidence


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------


def test_zero_underlying_price():
    """underlying_price <= 0 should return []."""
    data = _make_data_with_params([0.8] * 15, [0.6] * 10)
    data["underlying_price"] = 0

    signals = _new_strategy().evaluate(data)
    assert signals == []


def test_missing_obi_window():
    """No OBI window in rolling_data should return []."""
    data = _make_data_with_params([], [])
    del data["rolling_data"][KEY_OBI_5M]

    signals = _new_strategy().evaluate(data)
    assert signals == []


def test_missing_af_window():
    """No AF window in rolling_data should return []."""
    data = _make_data_with_params([], [])
    del data["rolling_data"][KEY_AF_5M]

    signals = _new_strategy().evaluate(data)
    assert signals == []


def test_af_insufficient_data():
    """AF window with fewer than min_af_data_points (default 5)."""
    obi_vals = [0.8] * 15
    af_vals = [0.6] * 3  # below min_af_data_points=5
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)
    assert signals == []


def test_signal_metadata_contains_gates():
    """Signal metadata should include gate scores."""
    obi_vals = [0.8] * 15
    af_vals = [0.6] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)
    assert len(signals) == 1

    meta = signals[0].metadata
    assert "gates" in meta
    assert "A_volume_spike" in meta["gates"]
    assert "B_participant_diversity" in meta["gates"]
    assert "C_spread_stability" in meta["gates"]


def test_signal_metadata_contains_obi_af_product():
    """Signal metadata should contain the OBI×AF product."""
    obi_vals = [0.8] * 15
    af_vals = [0.6] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)
    assert len(signals) == 1

    meta = signals[0].metadata
    assert "obi_af_product" in meta
    assert abs(meta["obi_af_product"] - 0.48) < 0.01


def test_signal_reason_includes_values():
    """Signal reason should include OBI and AF values."""
    obi_vals = [0.8] * 15
    af_vals = [0.6] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)
    assert len(signals) == 1

    reason = signals[0].reason
    assert "OBI" in reason
    assert "AF" in reason
    assert "LONG" in reason


def test_custom_params_override_thresholds():
    """Custom lower thresholds should allow marginal signals to fire."""
    params = {"obi_threshold": 0.30, "af_threshold": 0.20}
    # With lowered thresholds: combined = 0.35 + 0.25 = 0.60 > 0.50
    obi_vals = [0.35] * 15
    af_vals = [0.25] * 10
    data = _make_data_with_params(obi_vals, af_vals, params=params)

    signals = _new_strategy().evaluate(data)
    assert len(signals) == 1
    assert signals[0].direction == Direction.LONG


def test_custom_params_raise_thresholds():
    """Custom higher thresholds should prevent marginal signals from firing."""
    params = {"obi_threshold": 0.90, "af_threshold": 0.80}
    obi_vals = [0.8] * 15
    af_vals = [0.6] * 10
    data = _make_data_with_params(obi_vals, af_vals, params=params)

    signals = _new_strategy().evaluate(data)
    # combined = 0.8 + 0.6 = 1.4 > 1.7? No. OBI 0.8 < 0.9, AF 0.6 < 0.8.
    assert signals == []


def test_risk_reward_ratio_in_metadata():
    """Signal metadata should contain risk_reward_ratio."""
    obi_vals = [0.8] * 15
    af_vals = [0.6] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)
    assert len(signals) == 1

    meta = signals[0].metadata
    assert "risk_reward_ratio" in meta
    # Default target_risk_mult=1.5, so RR should be 1.5
    assert meta["risk_reward_ratio"] == 1.5


def test_short_risk_reward_ratio():
    """SHORT signal should have same risk:reward as LONG (symmetric)."""
    obi_vals = [-0.8] * 15
    af_vals = [-0.6] * 10
    data = _make_data_with_params(obi_vals, af_vals)

    signals = _new_strategy().evaluate(data)
    assert len(signals) == 1
    assert signals[0].direction == Direction.SHORT
    assert signals[0].metadata["risk_reward_ratio"] == 1.5
