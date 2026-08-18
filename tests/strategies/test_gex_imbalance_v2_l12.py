"""L12: gex_imbalance_v2 _rolling_percentile_threshold cold-start self-inclusion fix.

The old code prepended the current value into the history when the rolling
history was shorter than PERCENTILE_WINDOW, comparing a value against itself and
guaranteeing a pass at cold start with inconsistent cold-vs-warm behavior. After
the fix, the current value is compared against REAL history only; cold start
(< 20 samples) still falls back to (True, 0.5).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from strategies.layer1.gex_imbalance_v2 import GEXImbalanceV2


def _sut(history):
    s = GEXImbalanceV2()
    s._ratio_history_pct = list(history)
    return s


def test_cold_start_returns_true_passthrough():
    # < 20 real history samples -> cold-start fallback (True, 0.5); signal fires.
    s = _sut([0.5] * 15)
    assert s._rolling_percentile_threshold(1.0, "_ratio_history_pct") == (True, 0.5)


def test_low_value_against_full_history_does_not_pass():
    # 20+ real history; current value is LOW => must NOT pass. The old self-include
    # bug would make a low value appear to rank higher because it entered its own
    # percentile window. After the fix it compares against history only.
    s = _sut([0.5] * 19 + [1.0])
    passed, rank = s._rolling_percentile_threshold(0.1, "_ratio_history_pct")
    assert passed is False
    assert rank is not None


def test_high_value_against_full_history_passes():
    # Genuinely high current value exceeds the 85th percentile of real history.
    s = _sut([0.5] * 19 + [1.0])
    passed, rank = s._rolling_percentile_threshold(1.1, "_ratio_history_pct")
    assert passed is True


def test_self_inclusion_removed_not_guaranteed_pass():
    # Regression guard: a value near the median must NOT pass just because it
    # would have been added to (and ranked within) its own cold window.
    history = list(range(1, 41))  # 1..40, 40 samples
    s = _sut(history)
    # current = 1 (below 85th pct ~ 34) => must not pass
    passed, _ = s._rolling_percentile_threshold(1.0, "_ratio_history_pct")
    assert passed is False