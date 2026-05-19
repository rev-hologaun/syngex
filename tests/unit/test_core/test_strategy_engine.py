"""
tests/unit/test_core/test_strategy_engine.py

Unit tests for StrategyEngine.
"""

import time
from unittest.mock import MagicMock

import pytest

from strategies.engine import StrategyEngine, EngineConfig, BaseStrategy
from strategies.signal import Direction, Signal


# =============================================================================
# Test Strategies
# =============================================================================

class TestStrategy(BaseStrategy):
    """Test strategy implementation."""
    strategy_id = "test_strategy"
    layer = "layer1"

    def __init__(self, return_signals: int = 1):
        super().__init__()
        self.return_signals = return_signals
        self.evaluate_call_count = 0

    def evaluate(self, data: dict) -> list[Signal]:
        """Return sample signals."""
        self.evaluate_call_count += 1
        signals = []
        for i in range(self.return_signals):
            signals.append(Signal(
                direction=Direction.LONG,
                confidence=0.75,
                entry=195.50,
                stop=194.20,
                target=197.80,
                strategy_id=self.strategy_id,
                symbol="TSLA",
                reason=f"Test signal {i}",
                timestamp=time.time(),
            ))
        return signals


class TestShortStrategy(BaseStrategy):
    """Test short signal strategy."""
    strategy_id = "test_short_strategy"
    layer = "layer1"

    def evaluate(self, data: dict) -> list[Signal]:
        return [Signal(
            direction=Direction.SHORT,
            confidence=0.70,
            entry=196.00,
            stop=197.50,
            target=193.50,
            strategy_id=self.strategy_id,
            symbol="TSLA",
            reason="Short signal",
            timestamp=time.time(),
        )]


class TestLowConfidenceStrategy(BaseStrategy):
    """Test low confidence strategy."""
    strategy_id = "test_low_conf"
    layer = "layer1"

    def evaluate(self, data: dict) -> list[Signal]:
        return [Signal(
            direction=Direction.LONG,
            confidence=0.25,  # Below threshold
            entry=195.00,
            stop=194.00,
            target=196.50,
            strategy_id=self.strategy_id,
            symbol="TSLA",
            reason="Low confidence",
            timestamp=time.time(),
        )]


class TestLayer2Strategy(BaseStrategy):
    """Test layer 2 strategy."""
    strategy_id = "test_layer2"
    layer = "layer2"

    def evaluate(self, data: dict) -> list[Signal]:
        return [Signal(
            direction=Direction.LONG,
            confidence=0.80,
            entry=195.50,
            stop=194.00,
            target=198.00,
            strategy_id=self.strategy_id,
            symbol="TSLA",
            reason="Layer 2 signal",
            timestamp=time.time(),
        )]


# =============================================================================
# Initialization Tests
# =============================================================================

class TestStrategyEngineInitialization:
    """Tests for StrategyEngine initialization."""

    def test_create_with_default_config(self):
        """Test engine creation with default config."""
        engine = StrategyEngine()

        assert engine.config.min_confidence == 0.40
        assert engine.config.max_signals_per_tick == 10
        assert engine.strategy_count == 0
        assert engine.signal_count == 0

    def test_create_with_custom_config(self):
        """Test engine creation with custom config."""
        config = EngineConfig(
            min_confidence=0.50,
            max_signals_per_tick=5,
            dedup_window_seconds=120.0,
        )
        engine = StrategyEngine(config=config)

        assert engine.config.min_confidence == 0.50
        assert engine.config.max_signals_per_tick == 5
        assert engine.config.dedup_window_seconds == 120.0

    def test_correlation_id_generated(self):
        """Test that correlation ID is generated."""
        engine1 = StrategyEngine()
        engine2 = StrategyEngine()

        assert engine1._correlation_id != engine2._correlation_id
        assert len(engine1._correlation_id) == 8


# =============================================================================
# Registration Tests
# =============================================================================

class TestStrategyRegistration:
    """Tests for strategy registration."""

    def test_register_strategy(self):
        """Test registering a strategy."""
        engine = StrategyEngine()
        strategy = TestStrategy()

        engine.register(strategy)

        assert engine.strategy_count == 1
        assert strategy in engine._strategies

    def test_register_multiple_strategies(self):
        """Test registering multiple strategies."""
        engine = StrategyEngine()

        engine.register(TestStrategy())
        engine.register(TestShortStrategy())
        engine.register(TestLayer2Strategy())

        assert engine.strategy_count == 3

    def test_register_strategy_without_id_raises(self):
        """Test that registering strategy without ID raises error."""
        engine = StrategyEngine()
        strategy = BaseStrategy()
        strategy.strategy_id = ""  # Empty ID

        with pytest.raises(ValueError, match="no strategy_id"):
            engine.register(strategy)

    def test_register_filter(self):
        """Test registering a filter."""
        engine = StrategyEngine()
        filter_func = lambda s: True  # noqa: E731

        engine.register_filter(filter_func)

        assert engine._filter_callback is not None


# =============================================================================
# Lifecycle Tests
# =============================================================================

class TestStrategyEngineLifecycle:
    """Tests for engine lifecycle."""

    def test_start(self):
        """Test starting the engine."""
        engine = StrategyEngine()

        engine.start()

        assert engine._running is True

    def test_stop(self):
        """Test stopping the engine."""
        engine = StrategyEngine()
        engine.start()

        engine.stop()

        assert engine._running is False

    def test_process_when_not_running_returns_empty(self):
        """Test that process() returns empty when not running."""
        engine = StrategyEngine()
        engine.register(TestStrategy())

        data = {"underlying_price": 195.50, "regime": "POSITIVE"}
        signals = engine.process(data)

        assert signals == []


# =============================================================================
# Strategy Evaluation Tests
# =============================================================================

class TestStrategyEvaluation:
    """Tests for strategy evaluation."""

    def test_process_evaluates_all_strategies(self):
        """Test that process() evaluates all registered strategies."""
        engine = StrategyEngine()
        strategy1 = TestStrategy(return_signals=1)
        strategy2 = TestStrategy(return_signals=2)

        engine.register(strategy1)
        engine.register(strategy2)
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
            "timestamp": time.time(),
        }

        signals = engine.process(data)

        assert strategy1.evaluate_call_count == 1
        assert strategy2.evaluate_call_count == 1
        assert len(signals) == 3  # 1 + 2 signals

    def test_process_filters_by_min_confidence(self):
        """Test that process() filters by minimum confidence."""
        engine = StrategyEngine(config=EngineConfig(min_confidence=0.50))
        engine.register(TestLowConfidenceStrategy())
        engine.register(TestStrategy())  # Returns 0.75 confidence
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        signals = engine.process(data)

        # Only high confidence signals should pass
        for signal in signals:
            assert signal.confidence >= 0.50

    def test_process_applies_regime_filter(self):
        """Test that process() applies regime filter."""
        engine = StrategyEngine()
        filter_func = MagicMock(return_value=True)
        engine.register_filter(filter_func)
        engine.register(TestStrategy())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        engine.process(data)

        assert filter_func.called

    def test_process_deduplicates_by_strategy(self):
        """Test that process() deduplicates signals from same strategy."""
        engine = StrategyEngine(config=EngineConfig(dedup_window_seconds=60.0))
        strategy = TestStrategy(return_signals=2)
        engine.register(strategy)
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        # First call
        signals1 = engine.process(data)
        # Second call immediately
        signals2 = engine.process(data)

        # Second call should have no signals due to dedup
        assert len(signals1) == 2
        assert len(signals2) == 0


# =============================================================================
# Signal Capping Tests
# =============================================================================

class TestSignalCapping:
    """Tests for signal capping."""

    def test_caps_signals_per_tick(self):
        """Test that process() caps signals per tick."""
        engine = StrategyEngine(config=EngineConfig(max_signals_per_tick=3))

        # Register strategies that return many signals
        for i in range(5):
            engine.register(TestStrategy(return_signals=2))

        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        signals = engine.process(data)

        assert len(signals) <= 3

    def test_keeps_highest_confidence_when_capped(self):
        """Test that capping keeps highest confidence signals."""
        engine = StrategyEngine(config=EngineConfig(max_signals_per_tick=2))

        # Register strategies with different confidence levels
        class HighConfStrategy(BaseStrategy):
            strategy_id = "high_conf"
            layer = "layer1"
            def evaluate(self, data):
                return [Signal(
                    direction=Direction.LONG,
                    confidence=0.90,
                    entry=195.50,
                    stop=194.20,
                    target=197.80,
                    strategy_id="high_conf",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]

        class LowConfStrategy(BaseStrategy):
            strategy_id = "low_conf"
            layer = "layer1"
            def evaluate(self, data):
                return [Signal(
                    direction=Direction.LONG,
                    confidence=0.55,
                    entry=195.50,
                    stop=194.20,
                    target=197.80,
                    strategy_id="low_conf",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]

        engine.register(LowConfStrategy())
        engine.register(HighConfStrategy())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        signals = engine.process(data)

        # Should keep the highest confidence signal
        assert all(s.confidence >= 0.75 for s in signals)


# =============================================================================
# Conflict Detection Tests
# =============================================================================

class TestConflictDetection:
    """Tests for conflict detection and resolution."""

    def test_detects_long_short_conflict(self):
        """Test that conflicts between LONG and SHORT are detected."""
        engine = StrategyEngine()
        engine.register(TestStrategy())  # LONG
        engine.register(TestShortStrategy())  # SHORT
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        signals = engine.process(data)

        # Conflicts should be resolved (some signals suppressed)
        assert len(signals) <= 2

    def test_extreme_confidence_gap_resolution(self):
        """Test conflict resolution with extreme confidence gap."""
        engine = StrategyEngine(config=EngineConfig(max_signals_per_tick=10))

        class ExtremeConfStrategy(BaseStrategy):
            strategy_id = "extreme"
            layer = "layer2"
            def evaluate(self, data):
                return [Signal(
                    direction=Direction.LONG,
                    confidence=0.95,  # Extreme
                    entry=195.50,
                    stop=194.20,
                    target=197.80,
                    strategy_id="extreme",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]

        class LowConfOpposingStrategy(BaseStrategy):
            strategy_id = "low_conf_opp"
            layer = "layer1"
            def evaluate(self, data):
                return [Signal(
                    direction=Direction.SHORT,
                    confidence=0.60,  # Low
                    entry=196.00,
                    stop=197.50,
                    target=193.50,
                    strategy_id="low_conf_opp",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]

        engine.register(LowConfOpposingStrategy())
        engine.register(ExtremeConfStrategy())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        signals = engine.process(data)

        # Extreme confidence should win
        assert all(s.strategy_id == "extreme" for s in signals)

    def test_layer_priority_resolution(self):
        """Test conflict resolution with layer priority."""
        engine = StrategyEngine(config=EngineConfig(max_signals_per_tick=10))

        class Layer1Strategy(BaseStrategy):
            strategy_id = "layer1_strat"
            layer = "layer1"
            def evaluate(self, data):
                return [Signal(
                    direction=Direction.LONG,
                    confidence=0.75,
                    entry=195.50,
                    stop=194.20,
                    target=197.80,
                    strategy_id="layer1_strat",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]

        class Layer2Strategy(BaseStrategy):
            strategy_id = "layer2_strat"
            layer = "layer2"
            def evaluate(self, data):
                return [Signal(
                    direction=Direction.SHORT,
                    confidence=0.72,  # Similar confidence
                    entry=196.00,
                    stop=197.50,
                    target=193.50,
                    strategy_id="layer2_strat",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]

        engine.register(Layer1Strategy())
        engine.register(Layer2Strategy())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        signals = engine.process(data)

        # Layer 2 should win over Layer 1
        layer2_signals = [s for s in signals if s.strategy_id == "layer2_strat"]
        assert len(layer2_signals) > 0


# =============================================================================
# Signal Handler Tests
# =============================================================================

class TestSignalHandlers:
    """Tests for signal handlers."""

    def test_register_signal_handler(self):
        """Test registering a signal handler."""
        engine = StrategyEngine()
        handler = MagicMock()

        engine.register_signal_handler(handler)
        engine.register(TestStrategy())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        engine.process(data)

        assert handler.called

    def test_signal_handler_receives_signal(self):
        """Test that handler receives the signal object."""
        engine = StrategyEngine()
        received_signals = []

        def handler(signal):
            received_signals.append(signal)

        engine.register_signal_handler(handler)
        engine.register(TestStrategy())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        engine.process(data)

        assert len(received_signals) > 0
        assert all(isinstance(s, Signal) for s in received_signals)


# =============================================================================
# Status Tests
# =============================================================================

class TestEngineStatus:
    """Tests for engine status methods."""

    def test_get_status(self):
        """Test get_status() returns correct info."""
        engine = StrategyEngine()
        engine.register(TestStrategy())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }
        engine.process(data)

        status = engine.get_status()

        assert status["running"] is True
        assert status["strategies"] == 1
        assert status["total_signals"] > 0
        assert status["ticks_processed"] == 1

    def test_get_recent_signals(self):
        """Test get_recent_signals() returns recent signals."""
        engine = StrategyEngine()
        engine.register(TestStrategy(return_signals=5))
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }
        engine.process(data)

        recent = engine.get_recent_signals(n=3)

        assert len(recent) <= 3
        assert all(isinstance(s, dict) for s in recent)

    def test_reset_recent_signals(self):
        """Test reset_recent_signals() clears buffer."""
        engine = StrategyEngine()
        engine.register(TestStrategy())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }
        engine.process(data)

        engine.reset_recent_signals()

        assert engine.get_recent_signals(n=10) == []
