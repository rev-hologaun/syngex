"""
tests/conftest.py — Pytest fixtures for Syngex test suite
"""

import pytest
import time


@pytest.fixture
def sample_signal():
    """Create a sample Signal for testing."""
    from strategies.signal import Signal, Direction

    return Signal(
        direction=Direction.LONG,
        confidence=0.75,
        entry=195.50,
        stop=194.20,
        target=197.80,
        strategy_id="test_strategy",
        symbol="TSLA",
        reason="Test signal for unit tests",
        expiry="2026-05-19",
        metadata={"test_key": "test_value"},
    )


@pytest.fixture
def rolling_window_count():
    """Create a count-based RollingWindow."""
    from strategies.rolling_window import RollingWindow

    return RollingWindow(window_type="count", window_size=10)


@pytest.fixture
def rolling_window_time():
    """Create a time-based RollingWindow (30 seconds)."""
    from strategies.rolling_window import RollingWindow

    return RollingWindow(window_type="time", window_size=30)


@pytest.fixture
def gex_calculator():
    """Create a GEXCalculator instance."""
    from engine.gex_calculator import GEXCalculator

    calc = GEXCalculator(symbol="TSLA")
    calc.set_underlying_price(195.00)
    return calc


@pytest.fixture
def strategy_engine():
    """Create a StrategyEngine instance."""
    from strategies.engine import StrategyEngine, EngineConfig

    config = EngineConfig(min_confidence=0.40, max_signals_per_tick=10)
    return StrategyEngine(config=config)


@pytest.fixture
def sample_option_message():
    """Sample option_update message for GEXCalculator testing."""
    return {
        "type": "option_update",
        "strike": 195.0,
        "gamma": 0.025,
        "open_interest": 1000.0,
        "side": "call",
        "delta": 0.55,
        "iv": 0.45,
    }


@pytest.fixture
def sample_put_message():
    """Sample put option message."""
    return {
        "type": "option_update",
        "strike": 195.0,
        "gamma": 0.020,
        "open_interest": 800.0,
        "side": "put",
        "delta": -0.45,
        "iv": 0.48,
    }
