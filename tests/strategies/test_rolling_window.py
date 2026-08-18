"""Tests for RollingWindow percentile math (H4 fix).

The p25/p75 quartiles must match the canonical linear-interpolation method
(numpy 'linear', i.e. method 7). The old implementation returned wrong
quartiles for most window sizes (n=3,4,6,7,8,12...), silently shifting the
bottom/top-quartile gates used by live strategies (e.g. iv_band_breakout).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from strategies.rolling_window import RollingWindow

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

# Reference values computed with numpy.percentile(vals, [25, 75]) (linear/method-7).
# [p25, p75] for window of consecutive values 1..n. Note: quartiles require >=2
# values (single-value windows return None per _refresh design).
REFERENCE = {
    2: (1.25, 1.75),
    3: (1.5, 2.5),
    4: (1.75, 3.25),
    5: (2.0, 4.0),
    6: (2.25, 4.75),
    7: (2.5, 5.5),
    8: (2.75, 6.25),
    9: (3.0, 7.0),
    10: (3.25, 7.75),
    11: (3.5, 8.5),
    12: (3.75, 9.25),
}


def _window_of(vals):
    """Return a RollingWindow seeded with vals (count-based, big window)."""
    w = RollingWindow(window_type="count", window_size=len(vals) + 20)
    for v in vals:
        w.push(v)
    return w


def test_quartiles_match_reference_across_window_sizes():
    for n, (exp_p25, exp_p75) in REFERENCE.items():
        vals = list(range(1, n + 1))
        w = _window_of(vals)
        assert w.p25 == exp_p25, f"n={n}: p25={w.p25} != {exp_p25}"
        assert w.p75 == exp_p75, f"n={n}: p75={w.p75} != {exp_p75}"


def test_quartiles_match_numpy():
    if not _HAS_NUMPY:
        return  # skip silently if numpy absent
    for n in range(2, 25):
        vals = list(range(1, n + 1))
        w = _window_of(vals)
        exp_p25 = float(np.percentile(vals, 25))
        exp_p75 = float(np.percentile(vals, 75))
        assert abs(w.p25 - exp_p25) < 1e-9, f"n={n} p25"
        assert abs(w.p75 - exp_p75) < 1e-9, f"n={n} p75"


def test_single_value_window():
    # Quartiles are undefined for a single value -> None (per _refresh design)
    w = _window_of([7.0])
    assert w.p25 is None
    assert w.p75 is None


def test_empty_window_returns_none():
    w = RollingWindow(window_type="count", window_size=10)
    assert w.p25 is None
    assert w.p75 is None


def test_bottom_quartile_gate_boundary():
    """iv_band_breakout uses `current_skew <= p25` => 'compressed'.

    The latest value (max) must NOT be flagged as bottom-quartile, and the
    p25 boundary must sit strictly between the window min and the next value.
    """
    vals = list(range(1, 9))  # p25 = 2.75
    w = _window_of(vals)
    assert w.latest == 8
    assert not (w.latest <= w.p25)  # max is not in the bottom quartile
    assert 2 < w.p25 < 3


def test_top_quartile_gate_boundary():
    vals = list(range(1, 9))  # p75 = 6.25
    w = _window_of(vals)
    assert w.latest == 8
    assert w.latest >= w.p75  # max is in top quartile

# ---------------------------------------------------------------------------
# M4: time-anchored lookback (sample_before_now)
# ---------------------------------------------------------------------------

BASE = 1_700_000_000.0  # fixed reference "now" epoch for determinism


def _time_window(pairs):
    """Time-based window seeded with [(ts, value), ...] in ascending ts."""
    w = RollingWindow(window_type="time", window_size=300)
    for ts, v in pairs:
        w.push(v, timestamp=ts)
    return w


def test_sample_before_now_returns_value_at_age():
    # samples every second for 10s; anchor 4s ago from now=base+9.5
    w = _time_window([(BASE + i, float(i)) for i in range(10)])
    # cutoff = (base+9.5) - 4 = base+5.5 -> newest ts<=5.5 is ts=5 -> value 5.0
    assert w.sample_before_now(4, now=BASE + 9.5) == 5.0


def test_sample_before_now_returns_latest_for_tiny_age():
    w = _time_window([(BASE + i, float(i)) for i in range(10)])
    # cutoff = base+9.0 -> newest ts<=9.0 is ts=9 -> value 9.0
    assert w.sample_before_now(0.5, now=BASE + 9.5) == 9.0


def test_sample_before_now_none_when_window_younger_than_age():
    w = _time_window([(BASE + i, float(i)) for i in range(5)])  # only 0..4
    # age 100s from now -> cutoff way before oldest sample -> None
    assert w.sample_before_now(100, now=BASE + 9.5) is None


def test_sample_before_now_nonpositive_age_returns_latest():
    w = _time_window([(BASE + i, float(i)) for i in range(5)])
    assert w.sample_before_now(0, now=BASE + 9.5) == 4.0
    assert w.sample_before_now(-3, now=BASE + 9.5) == 4.0


def test_sample_before_now_empty_returns_none():
    assert RollingWindow(window_type="time", window_size=300).sample_before_now(300) is None


def test_sample_before_now_warm_window_returns_rightmost_old_enough():
    # all samples 500s old -> every one satisfies a 300s lookback; returns newest
    w = _time_window([(BASE - 500 + i, float(100 + i)) for i in range(20)])
    assert w.sample_before_now(300, now=BASE + 9.5) == 119.0


def test_sample_before_now_bisect_mid_window():
    # irregular gaps: ensure it returns value at the boundary, not a slot
    w = _time_window([(BASE + t, float(v)) for t, v in
                      [(0, 1.0), (1, 2.0), (5, 3.0), (9, 4.0), (20, 5.0)]])
    # now=base+20, age=10 -> cutoff=base+10 -> newest ts<=10 is ts=9 -> value 4.0
    assert w.sample_before_now(10, now=BASE + 20) == 4.0
