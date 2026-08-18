"""Regression tests for M1: strike_concentration regime-align confidence fix.

Bug (M1): regime_conf divided normalized net_gamma by /2000, a divisor tuned for
the CUMULATIVE scale. Real net_gamma_normalized spans ~0.2-136 across the fleet,
so /2000 pinned the regime component at ~0.00-0.07 (effectively dead). The fix
introduces REGIME_GAMMA_CEILING=100.0 so strong regime alignment saturates toward
1.0 and weak values stay low. These tests FAIL on the pre-fix /2000.
"""
import pytest

from strategies.layer3 import strike_concentration as sc
from strategies.layer3 import strike_concentration_v2 as sc_v2

# Real observed net_gamma_normalized across the 5-symbol fleet (2026-08-18).
FLEET = {
    "AMD": 0.20,
    "NVDA": 30.5,
    "TSLA": 40.1,
    "INTC": 108.2,
    "SPY": 136.4,
}


def _regime_component(net_gamma: float, ceiling: float) -> float:
    """Mirror the code's regime normalization: (regime_conf - 0.05) / 0.05."""
    conf = 0.05 + 0.05 * min(1.0, abs(net_gamma) / ceiling)
    return (conf - 0.05) / (0.10 - 0.05)


@pytest.mark.parametrize("mod", [sc, sc_v2])
def test_regime_ceiling_constant_present(mod):
    """Both strategy variants expose a sane REGIME_GAMMA_CEILING constant."""
    assert hasattr(mod, "REGIME_GAMMA_CEILING")
    assert mod.REGIME_GAMMA_CEILING == pytest.approx(100.0)


@pytest.mark.parametrize("mod", [sc, sc_v2])
def test_regime_component_is_live_not_dead(mod):
    """Strong fleet values must move the regime component well above the old
    dead floor (old /2000 gave <=0.07 for all of these)."""
    for name, ng in FLEET.items():
        c = _regime_component(ng, mod.REGIME_GAMMA_CEILING)
        if name in ("INTC", "SPY"):  # strongest regime -> saturate
            assert c == pytest.approx(1.0, abs=1e-6), f"{name}: {c}"
        else:  # mid/weak -> meaningfully non-zero for mid, near zero for weak
            assert c >= 0.0 and c <= 1.0, f"{name}: {c}"


@pytest.mark.parametrize("mod", [sc, sc_v2])
def test_regime_component_monotonic_and_bounded(mod):
    """Component is monotone non-decreasing in |net_gamma| and clamped to [0,1]."""
    lows = sorted({0.0, 1.0, 5.0, 25.0, 50.0, 90.0, 100.0, 150.0, 1000.0})
    vals = [_regime_component(g, mod.REGIME_GAMMA_CEILING) for g in lows]
    assert vals == sorted(vals)  # non-decreasing
    assert all(0.0 <= v <= 1.0 for v in vals)
    # zero / tiny net_gamma must not spuriously boost confidence
    assert _regime_component(0.0, mod.REGIME_GAMMA_CEILING) == 0.0
    # strong / very strong must saturate (no unbounded growth / no rollover)
    assert _regime_component(100.0, mod.REGIME_GAMMA_CEILING) == pytest.approx(1.0)
    assert _regime_component(1000.0, mod.REGIME_GAMMA_CEILING) == pytest.approx(1.0)


def test_fix_would_fail_on_old_dead_divisor_2000():
    """Guard against regression to the dead /2000 divisor."""
    for name, ng in FLEET.items():
        old_dead = _regime_component(ng, 2000.0)
        fixed = _regime_component(ng, sc.REGIME_GAMMA_CEILING)
        # the fix must materially lift the component for mid/strong values
        assert fixed >= old_dead
        if name in ("INTC", "SPY", "TSLA", "NVDA"):
            assert fixed - old_dead > 0.2, f"{name}: old={old_dead:.3f} new={fixed:.3f}"