"""
tests/test_rolling_window.py — Test RollingWindow statistics
"""

import pytest
import time
from strategies.rolling_window import RollingWindow


class TestRollingWindowCreation:
    """Test RollingWindow initialization."""

    def test_create_count_based_window(self):
        """Test creating a count-based window."""
        window = RollingWindow(window_type="count", window_size=10)

        assert window.window_type == "count"
        assert window.window_size == 10
        assert len(window) == 0

    def test_create_time_based_window(self):
        """Test creating a time-based window."""
        window = RollingWindow(window_type="time", window_size=60)

        assert window.window_type == "time"
        assert window.window_size == 60
        assert len(window) == 0

    def test_default_window(self):
        """Test default window parameters."""
        window = RollingWindow()

        assert window.window_type == "count"
        assert window.window_size == 20


class TestWindowPopulation:
    """Test window population with sample data."""

    def test_push_single_value(self, rolling_window_count):
        """Test pushing a single value."""
        rolling_window_count.push(195.5)

        assert len(rolling_window_count) == 1
        assert rolling_window_count.latest == 195.5
        assert rolling_window_count.count == 1

    def test_push_multiple_values(self, rolling_window_count):
        """Test pushing multiple values."""
        values = [195.0, 195.5, 196.0, 196.5, 197.0]
        for v in values:
            rolling_window_count.push(v)

        assert len(rolling_window_count) == 5
        assert rolling_window_count.values == values
        assert rolling_window_count.latest == 197.0

    def test_push_with_timestamp(self, rolling_window_time):
        """Test pushing values with explicit timestamps."""
        base_time = 1000.0
        rolling_window_time.push_pair(195.0, base_time)
        rolling_window_time.push_pair(196.0, base_time + 10)
        rolling_window_time.push_pair(197.0, base_time + 20)

        assert len(rolling_window_time) == 3
        assert rolling_window_time.latest == 197.0

    def test_push_pair_explicit(self, rolling_window_count):
        """Test push_pair method."""
        rolling_window_count.push_pair(195.0, 1000.0)
        rolling_window_count.push_pair(196.0, 1001.0)

        assert len(rolling_window_count) == 2
        assert rolling_window_count.values == [195.0, 196.0]


class TestStatisticsCalculations:
    """Test statistics calculations (mean, std, max, min)."""

    def test_mean_basic(self, rolling_window_count):
        """Test mean calculation."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0]
        for v in values:
            rolling_window_count.push(v)

        assert rolling_window_count.mean == pytest.approx(197.0)

    def test_mean_empty_window(self, rolling_window_count):
        """Test mean on empty window."""
        assert rolling_window_count.mean is None

    def test_median_basic(self, rolling_window_count):
        """Test median calculation."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0]
        for v in values:
            rolling_window_count.push(v)

        assert rolling_window_count.median == pytest.approx(197.0)

    def test_std_basic(self, rolling_window_count):
        """Test standard deviation calculation."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0]
        for v in values:
            rolling_window_count.push(v)

        # Sample std of [195, 196, 197, 198, 199]
        assert rolling_window_count.std is not None
        assert rolling_window_count.std > 0

    def test_std_single_value(self, rolling_window_count):
        """Test std with single value (should be None)."""
        rolling_window_count.push(195.0)
        assert rolling_window_count.std is None

    def test_std_empty_window(self, rolling_window_count):
        """Test std on empty window."""
        assert rolling_window_count.std is None

    def test_min_max_basic(self, rolling_window_count):
        """Test min and max calculations."""
        values = [195.0, 197.0, 194.0, 198.0, 196.0]
        for v in values:
            rolling_window_count.push(v)

        assert rolling_window_count.min == pytest.approx(194.0)
        assert rolling_window_count.max == pytest.approx(198.0)

    def test_min_max_empty(self, rolling_window_count):
        """Test min and max on empty window."""
        assert rolling_window_count.min is None
        assert rolling_window_count.max is None

    def test_range_basic(self, rolling_window_count):
        """Test range calculation."""
        values = [195.0, 197.0, 194.0, 198.0, 196.0]
        for v in values:
            rolling_window_count.push(v)

        assert rolling_window_count.range == pytest.approx(4.0)

    def test_range_empty(self, rolling_window_count):
        """Test range on empty window."""
        assert rolling_window_count.range is None

    def test_percentiles_basic(self, rolling_window_count):
        """Test percentile calculations."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0, 200.0, 201.0, 202.0]
        for v in values:
            rolling_window_count.push(v)

        assert rolling_window_count.p25 is not None
        assert rolling_window_count.p75 is not None
        assert rolling_window_count.p25 < rolling_window_count.p75

    def test_percentiles_insufficient_data(self, rolling_window_count):
        """Test percentiles with insufficient data."""
        rolling_window_count.push(195.0)
        assert rolling_window_count.p25 is None
        assert rolling_window_count.p75 is None


class TestWindowExpiration:
    """Test window expiration (old data drops off)."""

    def test_count_based_eviction(self, rolling_window_count):
        """Test that count-based window evicts old values."""
        # Window size is 10
        for i in range(15):
            rolling_window_count.push(195.0 + i)

        # Should only have last 10 values
        assert len(rolling_window_count) == 10
        assert rolling_window_count.values == [195.0 + i for i in range(5, 15)]

    def test_time_based_eviction(self, rolling_window_time):
        """Test that time-based window evicts old values."""
        base_time = 1000.0

        # Push values at t=0, t=10, t=20
        rolling_window_time.push_pair(195.0, base_time)
        rolling_window_time.push_pair(196.0, base_time + 10)
        rolling_window_time.push_pair(197.0, base_time + 20)

        assert len(rolling_window_time) == 3

        # Push new value at t=45 (window is 30 seconds, cutoff = 15)
        # Values at t=0 and t=10 should expire (both < 15)
        rolling_window_time.push_pair(198.0, base_time + 45)

        # Only values from t=20 and t=45 should remain
        assert len(rolling_window_time) == 2
        assert 197.0 in rolling_window_time.values
        assert 198.0 in rolling_window_time.values
        assert 195.0 not in rolling_window_time.values
        assert 196.0 not in rolling_window_time.values

    def test_time_based_exact_cutoff(self, rolling_window_time):
        """Test time-based eviction at exact cutoff boundary."""
        base_time = 1000.0

        # Push value at t=0
        rolling_window_time.push_pair(195.0, base_time)

        # Push value at t=31 (just past window boundary of 30)
        # Cutoff = 1031, so t=0 value (1000 < 1031) should be evicted
        rolling_window_time.push_pair(196.0, base_time + 31)

        # Value at t=0 should be evicted
        assert len(rolling_window_time) == 1
        assert rolling_window_time.latest == 196.0


class TestEdgeCases:
    """Test edge cases (empty window, single value)."""

    def test_empty_window_statistics(self, rolling_window_count):
        """Test all statistics return None on empty window."""
        assert rolling_window_count.mean is None
        assert rolling_window_count.median is None
        assert rolling_window_count.std is None
        assert rolling_window_count.min is None
        assert rolling_window_count.max is None
        assert rolling_window_count.range is None
        assert rolling_window_count.p25 is None
        assert rolling_window_count.p75 is None
        assert rolling_window_count.latest is None
        assert rolling_window_count.change is None
        assert rolling_window_count.change_pct is None
        assert rolling_window_count.z_score is None

    def test_single_value_statistics(self, rolling_window_count):
        """Test statistics with single value."""
        rolling_window_count.push(195.0)

        assert rolling_window_count.mean == pytest.approx(195.0)
        assert rolling_window_count.median == pytest.approx(195.0)
        assert rolling_window_count.std is None  # Sample std needs >= 2 values
        assert rolling_window_count.min == pytest.approx(195.0)
        assert rolling_window_count.max == pytest.approx(195.0)
        assert rolling_window_count.range == pytest.approx(0.0)
        assert rolling_window_count.latest == pytest.approx(195.0)
        assert rolling_window_count.change is None
        assert rolling_window_count.change_pct is None
        assert rolling_window_count.z_score is None

    def test_two_values_statistics(self, rolling_window_count):
        """Test statistics with two values."""
        rolling_window_count.push(195.0)
        rolling_window_count.push(197.0)

        assert rolling_window_count.mean == pytest.approx(196.0)
        assert rolling_window_count.median == pytest.approx(196.0)
        assert rolling_window_count.std is not None  # Can compute sample std
        assert rolling_window_count.min == pytest.approx(195.0)
        assert rolling_window_count.max == pytest.approx(197.0)
        assert rolling_window_count.range == pytest.approx(2.0)
        assert rolling_window_count.change == pytest.approx(2.0)
        assert rolling_window_count.change_pct == pytest.approx(2.0 / 195.0)


class TestTrendDetection:
    """Test trend direction detection."""

    def test_trend_up(self, rolling_window_count):
        """Test upward trend detection."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0, 200.0]
        for v in values:
            rolling_window_count.push(v)

        assert rolling_window_count.trend == "UP"

    def test_trend_down(self, rolling_window_count):
        """Test downward trend detection."""
        values = [200.0, 199.0, 198.0, 197.0, 196.0, 195.0]
        for v in values:
            rolling_window_count.push(v)

        assert rolling_window_count.trend == "DOWN"

    def test_trend_flat(self, rolling_window_count):
        """Test flat trend detection."""
        values = [197.0, 197.0, 197.0, 197.0, 197.0, 197.0]
        for v in values:
            rolling_window_count.push(v)

        assert rolling_window_count.trend == "FLAT"

    def test_trend_insufficient_data(self, rolling_window_count):
        """Test trend with insufficient data."""
        rolling_window_count.push(195.0)
        rolling_window_count.push(196.0)
        rolling_window_count.push(197.0)

        # Need at least 4 values
        assert rolling_window_count.trend == "FLAT"


class TestZScore:
    """Test z-score calculations."""

    def test_z_score_positive(self, rolling_window_count):
        """Test positive z-score."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0]
        for v in values:
            rolling_window_count.push(v)

        # Latest is 199, mean is 197, std > 0
        # z = (199 - 197) / std
        z = rolling_window_count.z_score
        assert z is not None
        assert z > 0

    def test_z_score_negative(self, rolling_window_count):
        """Test negative z-score."""
        values = [199.0, 198.0, 197.0, 196.0, 195.0]
        for v in values:
            rolling_window_count.push(v)

        z = rolling_window_count.z_score
        assert z is not None
        assert z < 0

    def test_z_score_zero(self, rolling_window_count):
        """Test z-score near zero."""
        values = [197.0, 197.0, 197.0, 197.0, 197.0]
        for v in values:
            rolling_window_count.push(v)

        # All values same, std = 0, z_score should be None
        assert rolling_window_count.z_score is None


class TestPercentileRank:
    """Test percentile rank calculations."""

    def test_percentile_rank_basic(self, rolling_window_count):
        """Test percentile rank."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0]
        for v in values:
            rolling_window_count.push(v)

        # Value 195 should be at 0% (lowest)
        assert rolling_window_count.percentile_rank(195.0) == pytest.approx(0.0)

        # Value 199 should be at 80% (4 out of 5 below)
        assert rolling_window_count.percentile_rank(199.0) == pytest.approx(0.8)

    def test_percentile_rank_empty(self, rolling_window_count):
        """Test percentile rank on empty window."""
        assert rolling_window_count.percentile_rank(195.0) is None


class TestQuartileChecks:
    """Test quartile membership checks."""

    def test_is_in_bottom_quartile(self, rolling_window_count):
        """Test bottom quartile detection."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0, 200.0, 201.0, 202.0]
        for v in values:
            rolling_window_count.push(v)

        # Latest is 202, which is in top quartile
        assert not rolling_window_count.is_in_bottom_quartile()

    def test_is_in_top_quartile(self, rolling_window_count):
        """Test top quartile detection."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0, 200.0, 201.0, 202.0]
        for v in values:
            rolling_window_count.push(v)

        # Latest is 202, which is in top quartile
        assert rolling_window_count.is_in_top_quartile()


class TestChangeCalculations:
    """Test change and percent change calculations."""

    def test_change_basic(self, rolling_window_count):
        """Test change calculation."""
        rolling_window_count.push(195.0)
        rolling_window_count.push(197.0)

        assert rolling_window_count.change == pytest.approx(2.0)

    def test_change_negative(self, rolling_window_count):
        """Test negative change."""
        rolling_window_count.push(197.0)
        rolling_window_count.push(195.0)

        assert rolling_window_count.change == pytest.approx(-2.0)

    def test_change_pct_basic(self, rolling_window_count):
        """Test percent change calculation."""
        rolling_window_count.push(195.0)
        rolling_window_count.push(197.0)

        assert rolling_window_count.change_pct == pytest.approx(2.0 / 195.0)

    def test_change_pct_zero_base(self, rolling_window_count):
        """Test percent change with zero base."""
        rolling_window_count.push(0.0)
        rolling_window_count.push(195.0)

        assert rolling_window_count.change_pct is None


class TestClearAndReset:
    """Test window clearing."""

    def test_clear_window(self, rolling_window_count):
        """Test clearing the window."""
        values = [195.0, 196.0, 197.0]
        for v in values:
            rolling_window_count.push(v)

        assert len(rolling_window_count) == 3

        rolling_window_count.clear()

        assert len(rolling_window_count) == 0
        assert rolling_window_count.mean is None

    def test_clear_time_based_window(self, rolling_window_time):
        """Test clearing a time-based window."""
        rolling_window_time.push_pair(195.0, 1000.0)
        rolling_window_time.push_pair(196.0, 1001.0)

        rolling_window_time.clear()

        assert len(rolling_window_time) == 0


class TestSnapshot:
    """Test window snapshot export."""

    def test_snapshot_contains_all_stats(self, rolling_window_count):
        """Test that snapshot contains all statistics."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0]
        for v in values:
            rolling_window_count.push(v)

        snapshot = rolling_window_count.snapshot()

        assert "count" in snapshot
        assert "mean" in snapshot
        assert "median" in snapshot
        assert "std" in snapshot
        assert "min" in snapshot
        assert "max" in snapshot
        assert "range" in snapshot
        assert "p25" in snapshot
        assert "p75" in snapshot
        assert "trend" in snapshot
        assert "latest" in snapshot
        assert "change" in snapshot
        assert "change_pct" in snapshot
        assert "z_score" in snapshot

    def test_snapshot_values(self, rolling_window_count):
        """Test snapshot values match direct properties."""
        values = [195.0, 196.0, 197.0, 198.0, 199.0]
        for v in values:
            rolling_window_count.push(v)

        snapshot = rolling_window_count.snapshot()

        assert snapshot["count"] == 5
        assert snapshot["mean"] == pytest.approx(197.0)
        assert snapshot["latest"] == pytest.approx(199.0)
        assert snapshot["trend"] == "UP"


class TestBoolAndLen:
    """Test boolean and length operators."""

    def test_bool_empty(self, rolling_window_count):
        """Test boolean value of empty window."""
        assert not rolling_window_count

    def test_bool_non_empty(self, rolling_window_count):
        """Test boolean value of non-empty window."""
        rolling_window_count.push(195.0)
        assert rolling_window_count

    def test_len(self, rolling_window_count):
        """Test length operator."""
        assert len(rolling_window_count) == 0

        rolling_window_count.push(195.0)
        assert len(rolling_window_count) == 1

        rolling_window_count.push(196.0)
        assert len(rolling_window_count) == 2
