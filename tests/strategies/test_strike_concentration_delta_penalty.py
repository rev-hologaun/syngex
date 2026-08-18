"""Regression tests for M9: strike_concentration_v2 delta soft-penalty magic numbers.

Bug (M9): the slice SHORT delta soft-penalty hardcoded magic 1.15/0.3 instead of
deriving from the DELTA_ACCEL thresholds. The LONG sibling hardcoded a 0.5 floor
(in both numerator and denominator). If the thresholds were tuned, these magic
values would silently diverge from the constants. Fix introduces:
  - DELTA_ACCEL_RAMP_SPAN  = LONG - SHORT (was magic 0.3)
  - DELTA_ACCEL_FLOOR      = 0.5 (named LONG penalty floor)
These tests fail on the pre-fix hardcoded-magic code if the constants drift out of
sync with the formulas.
"""
import pytest

from strategies.layer3 import strike_concentration_v2 as scv2


def test_ramp_span_constant_derived_from_thresholds():
    """RAMP_SPAN must equal LONG-SHORT (the old magic 0.3 was 1.15-0.85)."""
    assert scv2.DELTA_ACCEL_RAMP_SPAN == pytest.approx(
        scv2.DELTA_ACCEL_THRESHOLD_LONG - scv2.DELTA_ACCEL_THRESHOLD_SHORT
    )


def test_floor_constant_present():
    """LONG penalty floor is a named constant (was magic 0.5)."""
    assert scv2.DELTA_ACCEL_FLOOR == pytest.approx(0.5)


def test_short_penalty_matches_original_ramp():
    """Result of the SHORT soft-penalty equals the original 1.15/0.3 ramp at the
    threshold boundaries (and is well-formed across the ramp)."""
    LONG = scv2.DELTA_ACCEL_THRESHOLD_LONG
    SHORT = scv2.DELTA_ACCEL_THRESHOLD_SHORT
    span = scv2.DELTA_ACCEL_RAMP_SPAN

    def short_pen(da):
        return max(0.0, (LONG - da) / span)

    # at the SHORT threshold -> full credit (1.0)
    assert short_pen(SHORT) == pytest.approx(1.0)
    # at the LONG threshold -> zero credit (0.0)
    assert short_pen(LONG) == pytest.approx(0.0)
    # mid-ramp monotone decreasing
    assert short_pen(0.9) > short_pen(1.0) > short_pen(1.1)
    # clamps to 0 above LONG (no negative multiplier / no unbounded growth below 0)
    assert short_pen(1.5) == 0.0


def test_long_penalty_matches_original_ramp():
    """Result of the LONG soft-penalty equals the original 0.5-floor ramp."""
    LONG = scv2.DELTA_ACCEL_THRESHOLD_LONG
    floor = scv2.DELTA_ACCEL_FLOOR

    def long_pen(da):
        return max(0.0, (da - floor) / (LONG - floor))

    # at the LONG threshold -> full credit (1.0)
    assert long_pen(LONG) == pytest.approx(1.0)
    # at the floor -> zero credit
    assert long_pen(floor) == pytest.approx(0.0)
    # below floor clamps to 0
    assert long_pen(0.1) == 0.0
    # mid-ramp monotone increasing
    assert long_pen(0.7) < long_pen(0.9) < long_pen(1.0)