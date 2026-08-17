"""
Engine dedup anchor tests (re-fire / cooldown fix).

Verifies that the StrategyEngine's cooldown is keyed on (strategy_id, anchor)
— where the anchor identifies the specific setup (e.g. wall_strike) — rather
than strategy_id alone. Regression guard for:

  1. RE-FIRE SPAM: a single stuck wall was re-firing every dedup_window
     (observed: SPY gamma_wall_bounce 40x/hour on one strike, 35/40 gaps
     at exactly ~60.7s).
  2. MISSED TRADES: the coarse strategy_id bucket was also blocking a
     DIFFERENT valid wall of the same strategy during the window.
"""
import time

import pytest

from strategies.engine import EngineConfig, StrategyEngine
from strategies.signal import Direction, Signal


class FakeWallStrategy:
    """Minimal strategy that emits a signal per 'walls' config each tick."""
    strategy_id = "fake_wall"
    layer = "layer1"
    enabled = True

    def __init__(self, walls):
        # walls: list of (strike, side) emitted every call
        self._walls = walls

    def set_params(self, params):
        pass

    def evaluate(self, data):
        out = []
        ts = data.get("timestamp", time.time())
        for strike, side in self._walls:
            out.append(Signal(
                direction=Direction.LONG if side == "call" else Direction.SHORT,
                confidence=0.7,
                entry=float(strike),
                stop=float(strike - 1.0),
                target=float(strike + 1.0),
                strategy_id=self.strategy_id,
                _layer=self.layer,
                timestamp=ts,
                symbol="SPY",
                reason=f"wall {strike}",
                metadata={"wall_strike": strike, "wall_side": side},
            ))
        return out


def make_engine(dedup=60.0):
    return StrategyEngine(config=EngineConfig(dedup_window_seconds=dedup))


def process_at(engine, fake_now, **data):
    """Process one tick with a monkeypatched wall clock."""
    with _clock(fake_now):
        return engine.process({"timestamp": fake_now, "symbol": "SPY", **data})


class _clock:
    def __init__(self, t):
        self._t = t
        self._orig = None

    def __enter__(self):
        self._orig = time.time
        time.time = lambda: self._t

    def __exit__(self, *a):
        time.time = self._orig


# --------------------------------------------------------------------------
# 1. Same wall must NOT re-fire within the window (no spam)
# --------------------------------------------------------------------------

def test_same_wall_suppressed_within_window():
    eng = make_engine(dedup=60.0)
    eng.register(FakeWallStrategy([(778.0, "call")]))
    eng.start()

    out1 = process_at(eng, 1000.0)
    assert len(out1) == 1, "first fire on the wall should pass"

    # Same wall, 30s later (within 60s window)
    out2 = process_at(eng, 1030.0)
    assert out2 == [], "same wall must not re-fire within the dedup window"

    eng.stop()


def test_same_wall_refires_after_window():
    eng = make_engine(dedup=60.0)
    eng.register(FakeWallStrategy([(778.0, "call")]))
    eng.start()

    process_at(eng, 1000.0)
    process_at(eng, 1030.0)  # suppressed
    out = process_at(eng, 1065.0)  # 65s after first fire -> past window
    assert len(out) == 1, "same wall re-fires once the window elapses"

    eng.stop()


# --------------------------------------------------------------------------
# 2. Different walls of the same strategy cool down independently
#    (no missed trades)
# --------------------------------------------------------------------------

def test_different_walls_fire_independently_within_window():
    eng = make_engine(dedup=60.0)
    # Two distinct walls emitted together each tick.
    eng.register(FakeWallStrategy([(778.0, "call"), (777.0, "call")]))
    eng.start()

    out1 = process_at(eng, 1000.0)
    strikes = {s.metadata["wall_strike"] for s in out1}
    assert strikes == {778.0, 777.0}, "both walls fire on first tick (independent setups)"

    # 30s later both walls still in band — both are within their own windows,
    # so BOTH should be suppressed (neither re-fires).
    out2 = process_at(eng, 1030.0)
    assert out2 == [], "both walls suppressed within their own windows"

    eng.stop()


def test_different_wall_fires_while_first_still_cooldown_regardless_of_order():
    eng = make_engine(dedup=60.0)
    # Wall 777 emits only on the 2nd call to prove it is NOT blocked by 778's
    # cooldown.
    calls = {"n": 0}
    class CfgStrategy(FakeWallStrategy):
        def evaluate(self, data):
            calls["n"] += 1
            if calls["n"] == 1:
                return FakeWallStrategy.evaluate(self, {**data, "timestamp": time.time()})
            return FakeWallStrategy([(777.0, "call")]).evaluate(
                {**data, "timestamp": time.time()}
            )

    eng.register(CfgStrategy([(778.0, "call")]))
    eng.start()

    out1 = process_at(eng, 1000.0)
    assert {s.metadata["wall_strike"] for s in out1} == {778.0}

    # 30s later, only 777 emits (778 is in cool down). A strategy_id-only key
    # would wrongly suppress it; the anchor key must let it through.
    out2 = process_at(eng, 1030.0)
    assert {s.metadata["wall_strike"] for s in out2} == {777.0}, (
        "different wall must fire even while another wall of the same "
        "strategy is cooling down"
    )

    eng.stop()


# --------------------------------------------------------------------------
# 3. Legacy fallback: strategy WITHOUT a level anchor still cooldowns.
#    (No metadata -> anchor = symbol+direction; opposite direction is a
#    different setup.)
# --------------------------------------------------------------------------

class FakeDirStrategy:
    strategy_id = "fake_dir"
    layer = "layer1"
    enabled = True

    def __init__(self, direction: Direction):
        self._direction = direction

    def set_params(self, params):
        pass

    def evaluate(self, data):
        return [Signal(
            direction=self._direction,
            confidence=0.7,
            entry=10.0,
            stop=9.0,
            target=11.0,
            strategy_id=self.strategy_id,
            _layer=self.layer,
            timestamp=data.get("timestamp", time.time()),
            symbol="SPY",
            reason="no-level",
            metadata={},  # deliberately empty -> dir fallback anchor
        )]


def test_no_anchor_same_direction_suppressed():
    eng = make_engine(dedup=60.0)
    eng.register(FakeDirStrategy(Direction.LONG))
    eng.start()

    out1 = process_at(eng, 1000.0)
    assert len(out1) == 1
    out2 = process_at(eng, 1030.0)
    assert out2 == [], "same strategy+direction with no level anchor suppressed"
    eng.stop()


def test_opposite_direction_fires_within_window():
    eng = make_engine(dedup=60.0)

    class Both(FakeDirStrategy):
        def evaluate(self, data):
            return (
                FakeDirStrategy(Direction.LONG).evaluate(data)
                + FakeDirStrategy(Direction.SHORT).evaluate(data)
            )

    eng.register(Both(Direction.LONG))
    eng.start()

    out1 = process_at(eng, 1000.0)
    dirs1 = {s.direction for s in out1}
    assert dirs1 == {Direction.LONG, Direction.SHORT}

    # 30s later both within their own windows -> suppressed.
    out2 = process_at(eng, 1030.0)
    assert out2 == []
    eng.stop()


def test_backward_compat_default_window():
    # Default EngineConfig keeps dedup_window_seconds=60.0.
    assert EngineConfig().dedup_window_seconds == 60.0