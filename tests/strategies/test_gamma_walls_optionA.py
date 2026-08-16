"""Tests for H1 Option-A rank-based gamma wall gate (scale/symbol-invariant)."""
import pytest

from engine.gex_calculator import GEXCalculator


def _feed(gc: GEXCalculator, strike: float, gamma: float, side: str = "Call"):
    """Feed one option contract update for a strike (accumulates gamma)."""
    gc.process_message({
        "Gamma": str(gamma),
        "DailyOpenInterest": 1000,
        "Side": side,
        "Strikes": [str(strike)],
        "Legs": [{"StrikePrice": str(strike), "OptionType": side}],
    })


def _build(strike_gammas, price=100.0):
    """Build a calculator with a fixed ladder and underlying price.

    strike_gammas: {strike: gamma} (call gamma positively).
    """
    gc = GEXCalculator("TEST")
    gc.update_underlying_price(price)
    for st, g in strike_gammas.items():
        _feed(gc, st, g)
    return gc


def test_rank_gate_keeps_top_quartile():
    """rank_keep_frac=0.25 keeps roughly the top quartile of strikes."""
    # 8 strikes of varying gamma -> top 2 should pass a top-25% gate
    gammas = {100 + 5 * i: float(v) for i, v in enumerate([1, 2, 3, 4, 5, 6, 7, 8])}
    gc = _build(gammas, price=100.0)
    walls = gc.get_gamma_walls(threshold=1e6, rank_keep_frac=0.25)
    # top 2 by |gex| = the two highest-gamma strikes
    top2 = {st for st in sorted(gammas, key=lambda s: -abs(gammas[s]))[:2]}
    assert {w["strike"] for w in walls} == top2


def test_rank_gate_is_scale_invariant():
    """Multiplying all gamma by 10x must NOT change which strikes pass a rank gate
    (the core H1 fix: same meaning regardless of OI mode / price / symbol)."""
    gammas = {100 + 5 * i: float(v) for i, v in enumerate([1, 2, 3, 4, 5, 6, 7, 8])}
    base = _build(gammas, price=100.0)
    scaled = _build({s: g * 10 for s, g in gammas.items()}, price=100.0)

    for keep in (0.25, 0.5, 1.0):
        b = {w["strike"] for w in base.get_gamma_walls(rank_keep_frac=keep)}
        s = {w["strike"] for w in scaled.get_gamma_walls(rank_keep_frac=keep)}
        assert b == s, f"rank={keep}: base={b} scaled={s} must match (scale-invariant)"


def test_rank_gate_symbol_agnostic():
    """Two symbols with different absolute GEX scales but same relative shape must
    select the same fraction + same relative rank set."""
    shape = {100: 1.0, 105: 3.0, 110: 6.0, 115: 9.0}
    low = _build(shape, price=50.0)      # small dollar GEX
    high = _build({s: g for s, g in shape.items()}, price=5000.0)  # huge dollar GEX
    top_half_key = lambda w: w["strike"]
    lw = sorted(gc["strike"] for gc in low.get_gamma_walls(rank_keep_frac=0.5))
    hw = sorted(gc["strike"] for gc in high.get_gamma_walls(rank_keep_frac=0.5))
    assert lw == hw, f"symbol-invariance broken: {lw} vs {hw}"


def test_backward_compat_absolute_threshold():
    """rank_keep_frac=None must behave EXACTLY like the old absolute threshold."""
    gammas = {100: 1.0, 105: 3.0, 110: 6.0, 115: 9.0}
    gc = _build(gammas, price=100.0)
    # each strike's gex = (gamma * OI(=1000)) * 100 * price =>
    # [10M, 30M, 60M, 90M] for gamma [1,3,6,9]. threshold 50M keeps 60M+90M.
    thr = 5e7
    a = {w["strike"] for w in gc.get_gamma_walls(threshold=thr)}
    b = {w["strike"] for w in gc.get_gamma_walls(threshold=thr, rank_keep_frac=None)}
    assert a == b == {110.0, 115.0}, f"backward-compat broken: {a} vs {b}"


def test_empty_ladder_returns_empty():
    gc = GEXCalculator("TEST")
    gc.update_underlying_price(100.0)
    assert gc.get_gamma_walls(rank_keep_frac=0.25) == []


def test_keep_all_rank_1_0_returns_all_strikes():
    gammas = {100: 1.0, 105: 3.0}
    gc = _build(gammas, price=100.0)
    walls = gc.get_gamma_walls(rank_keep_frac=1.0)
    assert {w["strike"] for w in walls} == {100.0, 105.0}