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


# --------------------------------------------------------------------------
# 4. Exponential BACKOFF variant: a stuck wall must not re-fire at the base
#    window forever; its cooldown must grow. Default is off (multiplier=1.0).
# --------------------------------------------------------------------------


def _run_stuck_wall(engine, base_ts, step=60.5, n=12):
    """Feed the same wall every `step` seconds `n` times; return delivered counts."""
    delivered = []
    t = base_ts
    for i in range(n):
        out = process_at(engine, t)
        delivered.append(len(out))
        t += step
    return delivered


def test_backoff_default_off_matches_legacy_anchor_behavior():
    # multiplier=1.0 (default) -> fixed 60s window -> a stuck wall re-fires
    # every cycle (legacy anchor behavior preserved).
    eng = make_engine(dedup=60.0)  # mult defaults to 1.0
    eng.register(FakeWallStrategy([(225.0, "put")]))
    eng.start()
    delivered = _run_stuck_wall(eng, 1000.0)
    # Every 60.5s step is past the 60s window -> all fire.
    assert delivered == [1] * 12
    eng.stop()


def test_backoff_enabled_grows_window_and_suppresses_stuck_wall():
    # multiplier=2.0 -> window grows 60,120,240,... so a stuck wall firing every
    # ~60s gets suppressed on re-fires, and the GAPS between actual fires grow
    # monotonically (exponential backoff in action).
    eng = StrategyEngine(config=EngineConfig(dedup_window_seconds=60.0,
                                             dedup_backoff_multiplier=2.0))
    eng.register(FakeWallStrategy([(225.0, "put")]))
    eng.start()

    t = 1000.0
    fire_times = []
    for _ in range(14):
        out = process_at(eng, t)
        if len(out) == 1:
            fire_times.append(t)
        t += 60.5

    # Every re-fire must come LATER than the previous (gaps strictly grow), and
    # after the first fire the wall must NOT fire every 60s (backoff suppresses
    # the immediate re-fire).
    gaps = [round(fire_times[i + 1] - fire_times[i]) for i in range(len(fire_times) - 1)]
    assert 2 <= len(fire_times) <= 6, f"expected backoff to thin fires, got {fire_times}"
    assert gaps == sorted(gaps), f"fire gaps should grow monotonically: {gaps}"
    assert gaps[0] > 60, f"first re-fire must be delayed past the base window: {gaps}"
    eng.stop()


def test_backoff_max_strikes_caps_window():
    # max_strikes caps the accumulated strike count, bounding the effective
    # window at base * mult^max so a setup is never suppressed forever. The
    # stored count must never exceed max, and the computed window must equal
    # the capped value (not keep growing past it). Decay disabled so the test
    # only exercises the cap itself.
    max_strikes = 3
    eng = StrategyEngine(config=EngineConfig(dedup_window_seconds=60.0,
                                             dedup_backoff_multiplier=2.0,
                                             dedup_backoff_max_strikes=max_strikes,
                                             dedup_backoff_decay_seconds=0.0))
    eng.register(FakeWallStrategy([(225.0, "put")]))
    eng.start()
    key = ("fake_wall", "level:225.0")

    # Drive well past the cap: each fire uses a huge gap that clears any
    # window, and decay is off, so strikes accumulate and then clamp at max.
    t = 1000.0
    for _ in range(6):
        out = process_at(eng, t)
        assert len(out) == 1
        t += 2000.0

    # Count must be capped at max_strikes, window at base*mult^max, not higher.
    assert eng._backoff_counts[key] == max_strikes
    assert eng._cooldown_window(key, t) == 60.0 * (2.0 ** max_strikes)
    eng.stop()


def test_backoff_decay_resets_strikes_after_quiet_period():
    # A setup that goes quiet past dedup_backoff_decay_seconds resets its
    # strikes to 0, so a genuinely re-established wall fires at the base window.
    eng = StrategyEngine(config=EngineConfig(dedup_window_seconds=60.0,
                                             dedup_backoff_multiplier=2.0,
                                             dedup_backoff_decay_seconds=300.0))
    eng.register(FakeWallStrategy([(225.0, "put")]))
    eng.start()
    key = ("fake_wall", "level:225.0")

    # Fire a few times with gaps under decay to build up strikes.
    t = 1000.0
    for _ in range(3):
        process_at(eng, t); t += 250.0
    assert eng._backoff_counts[key] >= 1

    # Go quiet past decay (300s), then fire again -> 1 new signal, strikes reset.
    out = process_at(eng, t + 400.0)
    assert len(out) == 1
    assert eng._backoff_counts[key] == 0
    eng.stop()