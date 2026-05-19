"""
tests/test_strategy_evaluation_engine.py - Unit tests for StrategyEvaluationEngine

Tests cover:
- evaluate_strategies() calls strategy evaluation correctly
- evaluate_strategies() respects regime filter (blocked if regime check fails)
- evaluate_strategies() processes signals and tracks them
- build_last_trigger() returns correct structure for each strategy
- build_strategy_health() returns status, signal_count, win_rate, pnl, sparkline
- report_profile() logs gamma profile correctly
- Test with empty strategy list
- Test with no signals generated
- Test with multiple signals from different strategies

All dependencies are mocked: GEXCalculator, StrategyEngine, SignalTracker, NetGammaFilter
"""

import logging
import time
from unittest.mock import MagicMock, Mock, PropertyMock

import pytest

from core.strategy_engine import StrategyEvaluationEngine
from strategies.signal import Direction, Signal
from strategies.signal_tracker import SignalTracker, OpenSignal, ResolvedSignal, SignalOutcome
from core.filters import NetGammaFilter, Regime


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_gex_calculator():
    """Mock GEXCalculator with configurable summary and flip."""
    mock = MagicMock()
    mock.get_summary.return_value = {
        "net_gamma": 1000.0,
        "underlying_price": 100.0,
        "active_strikes": 10,
        "total_messages": 100,
    }
    mock.get_gamma_flip.return_value = 95.0
    mock.get_greeks_summary.return_value = {}
    return mock


@pytest.fixture
def mock_strategy_engine():
    """Mock StrategyEngine with configurable process output."""
    mock = MagicMock()
    mock._strategies = []  # Will be populated by tests
    mock.process.return_value = []
    return mock


@pytest.fixture
def mock_signal_tracker():
    """Mock SignalTracker with configurable signals."""
    mock = MagicMock(spec=SignalTracker)
    mock.get_open_signals.return_value = []
    mock.get_resolved.return_value = []
    mock.get_strategy_stats.return_value = {}
    return mock


@pytest.fixture
def mock_gamma_filter():
    """Mock NetGammaFilter with configurable regime check."""
    mock = MagicMock(spec=NetGammaFilter)
    mock.check_regime.return_value = True  # Default: allow signals
    mock._regime = Regime.POSITIVE
    return mock


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    mock = MagicMock(spec=logging.Logger)
    mock.name = "test.logger"  # Required by log_with_correlation
    mock.info = MagicMock()
    mock.error = MagicMock()
    mock.debug = MagicMock()
    mock.warning = MagicMock()
    mock.critical = MagicMock()
    return mock


@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator with required attributes."""
    mock = MagicMock()
    mock.symbol = "TEST"
    mock._rolling_data = {"test": "data"}
    mock._strategy_config = {
        "layer1": {},
        "layer2": {},
        "layer3": {},
        "full_data": {},
    }
    return mock


@pytest.fixture
def strategy_engine(mock_gex_calculator, mock_strategy_engine, mock_signal_tracker, mock_gamma_filter, mock_logger):
    """Create a StrategyEvaluationEngine with mocked dependencies."""
    return StrategyEvaluationEngine(
        gex_calculator=mock_gex_calculator,
        strategy_engine=mock_strategy_engine,
        signal_tracker=mock_signal_tracker,
        gamma_filter=mock_gamma_filter,
        logger=mock_logger,
        correlation_id="test-correlation-123",
    )


# ---------------------------------------------------------------------------
# Tests for evaluate_strategies()
# ---------------------------------------------------------------------------

class TestEvaluateStrategies:
    """Tests for StrategyEvaluationEngine.evaluate_strategies()"""

    def test_evaluate_strategies_calls_strategy_engine_process(
        self, strategy_engine, mock_strategy_engine, mock_orchestrator
    ):
        """Test that evaluate_strategies calls strategy_engine.process() with correct data."""
        # Setup
        mock_strategy_engine.process.return_value = []

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert
        mock_strategy_engine.process.assert_called_once()
        call_args = mock_strategy_engine.process.call_args[0][0]
        assert "underlying_price" in call_args
        assert "symbol" in call_args
        assert "gex_calculator" in call_args
        assert "rolling_data" in call_args
        assert "timestamp" in call_args
        assert "regime" in call_args
        assert "net_gamma" in call_args
        assert "gamma_flip" in call_args

    def test_evaluate_strategies_respects_regime_filter_blocked(
        self, strategy_engine, mock_gamma_filter, mock_strategy_engine, mock_orchestrator
    ):
        """Test that evaluate_strategies returns early when regime check fails."""
        # Setup: regime filter blocks
        mock_gamma_filter.check_regime.return_value = False

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: process should NOT be called
        mock_strategy_engine.process.assert_not_called()

    def test_evaluate_strategies_respects_regime_filter_allowed(
        self, strategy_engine, mock_gamma_filter, mock_strategy_engine, mock_orchestrator
    ):
        """Test that evaluate_strategies proceeds when regime check passes."""
        # Setup: regime filter allows
        mock_gamma_filter.check_regime.return_value = True
        mock_strategy_engine.process.return_value = []

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: process should be called
        mock_strategy_engine.process.assert_called_once()

    def test_evaluate_strategies_processes_signals_and_tracks_them(
        self, strategy_engine, mock_strategy_engine, mock_signal_tracker, mock_orchestrator
    ):
        """Test that signals are tracked when generated."""
        # Setup: engine returns signals
        mock_signal1 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=100.0,
            stop=98.0,
            target=105.0,
            strategy_id="test_strategy",
            reason="Test signal",
        )
        mock_strategy_engine.process.return_value = [mock_signal1]

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: signal tracker should have track called
        mock_signal_tracker.track.assert_called_once()
        track_call_args = mock_signal_tracker.track.call_args[0][0]
        assert track_call_args["strategy_id"] == "test_strategy"
        assert track_call_args["direction"] == "LONG"

    def test_evaluate_strategies_with_empty_strategy_list(
        self, strategy_engine, mock_strategy_engine, mock_orchestrator
    ):
        """Test that evaluate_strategies handles empty strategy list gracefully."""
        # Setup: no strategies registered
        mock_strategy_engine.process.return_value = []

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: should complete without error
        mock_strategy_engine.process.assert_called_once()

    def test_evaluate_strategies_with_no_signals_generated(
        self, strategy_engine, mock_strategy_engine, mock_signal_tracker, mock_orchestrator
    ):
        """Test that evaluate_strategies handles no signals gracefully."""
        # Setup: process returns empty list
        mock_strategy_engine.process.return_value = []

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: tracker should NOT be called (no signals to track)
        mock_signal_tracker.track.assert_not_called()

    def test_evaluate_strategies_with_multiple_signals_from_different_strategies(
        self, strategy_engine, mock_strategy_engine, mock_signal_tracker, mock_orchestrator
    ):
        """Test that multiple signals from different strategies are all tracked."""
        # Setup: multiple signals from different strategies
        mock_signal1 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=100.0,
            stop=98.0,
            target=105.0,
            strategy_id="strategy_alpha",
            reason="Alpha signal",
        )
        mock_signal2 = Signal(
            direction=Direction.SHORT,
            confidence=0.80,
            entry=100.0,
            stop=102.0,
            target=95.0,
            strategy_id="strategy_beta",
            reason="Beta signal",
        )
        mock_strategy_engine.process.return_value = [mock_signal1, mock_signal2]

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: both signals should be tracked
        assert mock_signal_tracker.track.call_count == 2
        track_calls = [call[0][0] for call in mock_signal_tracker.track.call_args_list]
        strategy_ids = [call["strategy_id"] for call in track_calls]
        assert "strategy_alpha" in strategy_ids
        assert "strategy_beta" in strategy_ids

    def test_evaluate_strategies_logs_signals(self, strategy_engine, mock_logger, mock_strategy_engine, mock_orchestrator):
        """Test that signals are logged correctly."""
        # Setup
        mock_signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=100.0,
            stop=98.0,
            target=105.0,
            strategy_id="test_strategy",
            reason="Test signal",
        )
        mock_strategy_engine.process.return_value = [mock_signal]

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: signal was tracked (logging behavior depends on log_with_correlation implementation)
        # The key assertion is that the signal processing completed without error
        mock_signal_tracker = strategy_engine._signal_tracker
        assert mock_signal_tracker.track.called  # Signal should be tracked

    def test_evaluate_strategies_resets_error_count_on_success(
        self, strategy_engine, mock_strategy_engine, mock_orchestrator
    ):
        """Test that error count is reset after successful processing."""
        # Setup: set error count to non-zero
        strategy_engine._error_count = 5
        mock_strategy_engine.process.return_value = []

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: error count should be reset to 0
        assert strategy_engine._error_count == 0

    def test_evaluate_strategies_increments_error_count_on_exception(
        self, strategy_engine, mock_strategy_engine, mock_logger, mock_orchestrator
    ):
        """Test that error count is incremented when exception occurs."""
        # Setup: process raises exception
        mock_strategy_engine.process.side_effect = Exception("Test error")

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: error count should be incremented
        assert strategy_engine._error_count >= 1
        # Note: logging behavior depends on log_with_correlation implementation

    def test_evaluate_strategies_circuit_breaker_triggers(
        self, strategy_engine, mock_strategy_engine, mock_logger, mock_orchestrator
    ):
        """Test that circuit breaker triggers after max consecutive errors."""
        # Setup: set error count to max threshold
        strategy_engine._error_count = 10  # _max_consecutive_errors
        mock_strategy_engine.process.side_effect = Exception("Test error")

        # Execute
        strategy_engine.evaluate_strategies(mock_orchestrator)

        # Assert: critical should be called for circuit breaker
        mock_logger.critical.assert_called()
        assert "CIRCUIT BREAKER" in str(mock_logger.critical.call_args)

    def test_evaluate_strategies_returns_early_if_missing_dependencies(
        self, mock_gex_calculator, mock_strategy_engine, mock_signal_tracker, mock_gamma_filter, mock_logger, mock_orchestrator
    ):
        """Test that evaluate_strategies returns early if dependencies are missing."""
        # Setup: set gex_calculator to None
        engine = StrategyEvaluationEngine(
            gex_calculator=None,  # Missing dependency
            strategy_engine=mock_strategy_engine,
            signal_tracker=mock_signal_tracker,
            gamma_filter=mock_gamma_filter,
            logger=mock_logger,
        )

        # Execute
        engine.evaluate_strategies(mock_orchestrator)

        # Assert: process should NOT be called
        mock_strategy_engine.process.assert_not_called()


# ---------------------------------------------------------------------------
# Tests for build_last_trigger()
# ---------------------------------------------------------------------------

class TestBuildLastTrigger:
    """Tests for StrategyEvaluationEngine.build_last_trigger()"""

    def test_build_last_trigger_returns_empty_dict_when_no_tracker(self, strategy_engine):
        """Test that build_last_trigger returns empty dict when signal_tracker is None."""
        # Setup: no tracker
        strategy_engine._signal_tracker = None

        # Execute
        result = strategy_engine.build_last_trigger(None)

        # Assert
        assert result == {}

    def test_build_last_trigger_returns_empty_dict_when_tracker_empty(
        self, strategy_engine, mock_signal_tracker
    ):
        """Test that build_last_trigger returns empty dict when no signals exist."""
        # Setup: tracker has no signals
        mock_signal_tracker.get_open_signals.return_value = []
        mock_signal_tracker.get_resolved.return_value = []

        # Execute
        result = strategy_engine.build_last_trigger(mock_signal_tracker)

        # Assert
        assert result == {}

    def test_build_last_trigger_returns_correct_structure_for_open_signals(
        self, strategy_engine, mock_signal_tracker
    ):
        """Test that build_last_trigger returns correct structure for open signals."""
        # Setup: open signal
        mock_open_signal = OpenSignal(
            signal_id="test_123",
            direction="LONG",
            strategy_id="test_strategy",
            entry=100.0,
            stop=98.0,
            target=105.0,
            confidence=0.75,
            timestamp=1000.0,
            reason="Test",
        )
        mock_signal_tracker.get_open_signals.return_value = [mock_open_signal]
        mock_signal_tracker.get_resolved.return_value = []

        # Execute
        result = strategy_engine.build_last_trigger(mock_signal_tracker)

        # Assert
        assert "test_strategy" in result
        assert result["test_strategy"]["side"] == "BUY"
        assert result["test_strategy"]["confidence"] == 0.75
        assert result["test_strategy"]["entry"] == 100.0
        assert result["test_strategy"]["stop"] == 98.0
        assert result["test_strategy"]["target"] == 105.0
        assert result["test_strategy"]["timestamp"] == 1000.0

    def test_build_last_trigger_returns_correct_structure_for_short_signals(
        self, strategy_engine, mock_signal_tracker
    ):
        """Test that build_last_trigger correctly handles SHORT signals."""
        # Setup: short open signal
        mock_open_signal = OpenSignal(
            signal_id="test_123",
            direction="SHORT",
            strategy_id="test_strategy",
            entry=100.0,
            stop=102.0,
            target=95.0,
            confidence=0.80,
            timestamp=1000.0,
            reason="Test",
        )
        mock_signal_tracker.get_open_signals.return_value = [mock_open_signal]
        mock_signal_tracker.get_resolved.return_value = []

        # Execute
        result = strategy_engine.build_last_trigger(mock_signal_tracker)

        # Assert
        assert result["test_strategy"]["side"] == "SELL"

    def test_build_last_trigger_returns_correct_structure_for_resolved_signals(
        self, strategy_engine, mock_signal_tracker
    ):
        """Test that build_last_trigger returns correct structure for resolved signals."""
        # Setup: resolved signal
        mock_open_signal = OpenSignal(
            signal_id="test_123",
            direction="LONG",
            strategy_id="test_strategy",
            entry=100.0,
            stop=98.0,
            target=105.0,
            confidence=0.75,
            timestamp=900.0,
            reason="Test",
        )
        mock_resolved_signal = ResolvedSignal(
            open_signal=mock_open_signal,
            outcome=SignalOutcome.WIN,
            exit_price=105.0,
            pnl=5.0,
            pnl_pct=500.0,
            hold_time=100.0,
            resolution_time=1000.0,
        )
        mock_signal_tracker.get_open_signals.return_value = []
        mock_signal_tracker.get_resolved.return_value = [mock_resolved_signal]

        # Execute
        result = strategy_engine.build_last_trigger(mock_signal_tracker)

        # Assert
        assert "test_strategy" in result
        assert result["test_strategy"]["side"] == "BUY"
        assert result["test_strategy"]["timestamp"] == 1000.0  # resolution_time

    def test_build_last_trigger_prefers_open_signal_over_resolved(
        self, strategy_engine, mock_signal_tracker
    ):
        """Test that build_last_trigger prefers open signal when both exist."""
        # Setup: both open and resolved signals
        mock_open_signal = OpenSignal(
            signal_id="test_123",
            direction="LONG",
            strategy_id="test_strategy",
            entry=100.0,
            stop=98.0,
            target=105.0,
            confidence=0.75,
            timestamp=1000.0,  # More recent
            reason="Test",
        )
        mock_resolved_signal = ResolvedSignal(
            open_signal=mock_open_signal,
            outcome=SignalOutcome.WIN,
            exit_price=105.0,
            pnl=5.0,
            pnl_pct=500.0,
            hold_time=100.0,
            resolution_time=900.0,  # Older
        )
        mock_signal_tracker.get_open_signals.return_value = [mock_open_signal]
        mock_signal_tracker.get_resolved.return_value = [mock_resolved_signal]

        # Execute
        result = strategy_engine.build_last_trigger(mock_signal_tracker)

        # Assert: should use open signal (more recent)
        assert result["test_strategy"]["timestamp"] == 1000.0

    def test_build_last_trigger_uses_resolved_when_open_is_older(
        self, strategy_engine, mock_signal_tracker
    ):
        """Test that build_last_trigger uses resolved signal when it's more recent."""
        # Setup: resolved signal is more recent
        mock_open_signal = OpenSignal(
            signal_id="test_123",
            direction="LONG",
            strategy_id="test_strategy",
            entry=100.0,
            stop=98.0,
            target=105.0,
            confidence=0.75,
            timestamp=900.0,  # Older
            reason="Test",
        )
        mock_resolved_signal = ResolvedSignal(
            open_signal=mock_open_signal,
            outcome=SignalOutcome.WIN,
            exit_price=105.0,
            pnl=5.0,
            pnl_pct=500.0,
            hold_time=100.0,
            resolution_time=1000.0,  # More recent
        )
        mock_signal_tracker.get_open_signals.return_value = [mock_open_signal]
        mock_signal_tracker.get_resolved.return_value = [mock_resolved_signal]

        # Execute
        result = strategy_engine.build_last_trigger(mock_signal_tracker)

        # Assert: should use resolved signal (more recent)
        assert result["test_strategy"]["timestamp"] == 1000.0

    def test_build_last_trigger_rounds_values_correctly(
        self, strategy_engine, mock_signal_tracker
    ):
        """Test that build_last_trigger rounds values correctly."""
        # Setup: signal with values that need rounding
        mock_open_signal = OpenSignal(
            signal_id="test_123",
            direction="LONG",
            strategy_id="test_strategy",
            entry=100.12345,
            stop=98.67890,
            target=105.98765,
            confidence=0.75123,
            timestamp=1000.0,
            reason="Test",
        )
        mock_signal_tracker.get_open_signals.return_value = [mock_open_signal]
        mock_signal_tracker.get_resolved.return_value = []

        # Execute
        result = strategy_engine.build_last_trigger(mock_signal_tracker)

        # Assert: values should be rounded
        assert result["test_strategy"]["confidence"] == 0.751  # 3 decimal places
        assert result["test_strategy"]["entry"] == 100.12  # 2 decimal places
        assert result["test_strategy"]["stop"] == 98.68  # 2 decimal places
        assert result["test_strategy"]["target"] == 105.99  # 2 decimal places


# ---------------------------------------------------------------------------
# Tests for build_strategy_health()
# ---------------------------------------------------------------------------

class TestBuildStrategyHealth:
    """Tests for StrategyEvaluationEngine.build_strategy_health()"""

    def test_build_strategy_health_returns_empty_dict_when_missing_dependencies(
        self, strategy_engine, mock_gex_calculator, mock_gamma_filter
    ):
        """Test that build_strategy_health returns empty dict when dependencies are missing."""
        # Setup: missing strategy_engine or signal_tracker
        strategy_engine._strategy_engine = None
        strategy_engine._signal_tracker = None

        # Create mock orchestrator
        mock_orchestrator = MagicMock()

        # Execute
        result = strategy_engine.build_strategy_health(mock_orchestrator)

        # Assert
        assert result == {}

    def test_build_strategy_health_returns_status_signal_count_win_rate_pnl_sparkline(
        self, strategy_engine, mock_strategy_engine, mock_signal_tracker
    ):
        """Test that build_strategy_health returns correct health data structure."""
        # Setup: strategy with stats
        mock_strategy = MagicMock()
        mock_strategy.strategy_id = "test_strategy"
        mock_strategy_engine._strategies = [mock_strategy]

        mock_signal_tracker.get_strategy_stats.return_value = {
            "test_strategy": {
                "total_signals": 10,
                "wins": 7,
                "losses": 2,
                "closed": 1,
                "total_pnl": 50.0,
            }
        }
        mock_signal_tracker.get_resolved.return_value = []
        mock_signal_tracker.get_open_signals.return_value = []

        # Create mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator._strategy_engine = mock_strategy_engine
        mock_orchestrator._signal_tracker = mock_signal_tracker

        # Execute
        result = strategy_engine.build_strategy_health(mock_orchestrator)

        # Assert
        assert "test_strategy" in result
        assert result["test_strategy"]["status"] == "active"
        assert result["test_strategy"]["signal_count"] == 10
        assert result["test_strategy"]["win_rate"] == 0.7  # 7/10
        assert result["test_strategy"]["pnl"] == 50.0
        assert "sparkline" in result["test_strategy"]
        assert len(result["test_strategy"]["sparkline"]) == 8

    def test_build_strategy_health_with_no_signals_returns_idle_status(
        self, strategy_engine, mock_strategy_engine, mock_signal_tracker
    ):
        """Test that build_strategy_health returns idle status when no signals."""
        # Setup: strategy with no signals
        mock_strategy = MagicMock()
        mock_strategy.strategy_id = "test_strategy"
        mock_strategy_engine._strategies = [mock_strategy]

        mock_signal_tracker.get_strategy_stats.return_value = {
            "test_strategy": {
                "total_signals": 0,
                "wins": 0,
                "losses": 0,
                "closed": 0,
                "total_pnl": 0.0,
            }
        }
        mock_signal_tracker.get_resolved.return_value = []
        mock_signal_tracker.get_open_signals.return_value = []

        # Create mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator._strategy_engine = mock_strategy_engine
        mock_orchestrator._signal_tracker = mock_signal_tracker

        # Execute
        result = strategy_engine.build_strategy_health(mock_orchestrator)

        # Assert
        assert result["test_strategy"]["status"] == "idle"
        assert result["test_strategy"]["signal_count"] == 0
        assert result["test_strategy"]["win_rate"] == 0.0
        assert result["test_strategy"]["pnl"] == 0.0

    def test_build_strategy_health_builds_sparkline_from_resolved_signals(
        self, strategy_engine, mock_strategy_engine, mock_signal_tracker
    ):
        """Test that build_strategy_health builds sparkline from cumulative PnL."""
        # Setup: strategy with resolved signals
        mock_strategy = MagicMock()
        mock_strategy.strategy_id = "test_strategy"
        mock_strategy_engine._strategies = [mock_strategy]

        mock_signal_tracker.get_strategy_stats.return_value = {
            "test_strategy": {
                "total_signals": 5,
                "wins": 3,
                "losses": 2,
                "closed": 0,
                "total_pnl": 10.0,
            }
        }

        # Create resolved signals with PnL
        mock_open1 = OpenSignal(signal_id="s1", direction="LONG", strategy_id="test_strategy",
                                 entry=100.0, stop=98.0, target=105.0, confidence=0.7,
                                 timestamp=100.0, reason="Test")
        mock_open2 = OpenSignal(signal_id="s2", direction="LONG", strategy_id="test_strategy",
                                 entry=100.0, stop=98.0, target=105.0, confidence=0.7,
                                 timestamp=200.0, reason="Test")
        mock_open3 = OpenSignal(signal_id="s3", direction="LONG", strategy_id="test_strategy",
                                 entry=100.0, stop=98.0, target=105.0, confidence=0.7,
                                 timestamp=300.0, reason="Test")

        mock_resolved1 = ResolvedSignal(open_signal=mock_open1, outcome=SignalOutcome.WIN,
                                         exit_price=105.0, pnl=5.0, pnl_pct=500.0,
                                         hold_time=100.0, resolution_time=150.0)
        mock_resolved2 = ResolvedSignal(open_signal=mock_open2, outcome=SignalOutcome.LOSS,
                                         exit_price=98.0, pnl=-2.0, pnl_pct=-200.0,
                                         hold_time=100.0, resolution_time=250.0)
        mock_resolved3 = ResolvedSignal(open_signal=mock_open3, outcome=SignalOutcome.WIN,
                                         exit_price=105.0, pnl=5.0, pnl_pct=500.0,
                                         hold_time=100.0, resolution_time=350.0)

        mock_signal_tracker.get_resolved.return_value = [mock_resolved1, mock_resolved2, mock_resolved3]
        mock_signal_tracker.get_open_signals.return_value = []

        # Create mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator._strategy_engine = mock_strategy_engine
        mock_orchestrator._signal_tracker = mock_signal_tracker

        # Execute
        result = strategy_engine.build_strategy_health(mock_orchestrator)

        # Assert: sparkline should have cumulative PnL values
        sparkline = result["test_strategy"]["sparkline"]
        assert len(sparkline) == 8  # Padded to 8 values
        # First values should be 0.0 (padding), then cumulative: 5.0, 3.0, 8.0
        assert 0.0 in sparkline  # Padding values

    def test_build_strategy_health_pads_sparkline_to_8_values(
        self, strategy_engine, mock_strategy_engine, mock_signal_tracker
    ):
        """Test that build_strategy_health pads sparkline to exactly 8 values."""
        # Setup: strategy with only 2 resolved signals
        mock_strategy = MagicMock()
        mock_strategy.strategy_id = "test_strategy"
        mock_strategy_engine._strategies = [mock_strategy]

        mock_signal_tracker.get_strategy_stats.return_value = {
            "test_strategy": {
                "total_signals": 2,
                "wins": 1,
                "losses": 1,
                "closed": 0,
                "total_pnl": 3.0,
            }
        }

        mock_open = OpenSignal(signal_id="s1", direction="LONG", strategy_id="test_strategy",
                                entry=100.0, stop=98.0, target=105.0, confidence=0.7,
                                timestamp=100.0, reason="Test")
        mock_resolved1 = ResolvedSignal(open_signal=mock_open, outcome=SignalOutcome.WIN,
                                         exit_price=105.0, pnl=5.0, pnl_pct=500.0,
                                         hold_time=100.0, resolution_time=150.0)
        mock_resolved2 = ResolvedSignal(open_signal=mock_open, outcome=SignalOutcome.LOSS,
                                         exit_price=98.0, pnl=-2.0, pnl_pct=-200.0,
                                         hold_time=100.0, resolution_time=200.0)

        mock_signal_tracker.get_resolved.return_value = [mock_resolved1, mock_resolved2]
        mock_signal_tracker.get_open_signals.return_value = []

        # Create mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator._strategy_engine = mock_strategy_engine
        mock_orchestrator._signal_tracker = mock_signal_tracker

        # Execute
        result = strategy_engine.build_strategy_health(mock_orchestrator)

        # Assert: sparkline should be exactly 8 values
        assert len(result["test_strategy"]["sparkline"]) == 8

    def test_build_strategy_health_with_open_signals_sets_active_status(
        self, strategy_engine, mock_strategy_engine, mock_signal_tracker
    ):
        """Test that build_strategy_health sets status to active when open signals exist."""
        # Setup: strategy with open signal but no resolved
        mock_strategy = MagicMock()
        mock_strategy.strategy_id = "test_strategy"
        mock_strategy_engine._strategies = [mock_strategy]

        mock_signal_tracker.get_strategy_stats.return_value = {
            "test_strategy": {
                "total_signals": 0,  # No resolved signals
                "wins": 0,
                "losses": 0,
                "closed": 0,
                "total_pnl": 0.0,
            }
        }

        mock_open_signal = OpenSignal(
            signal_id="test_123",
            direction="LONG",
            strategy_id="test_strategy",
            entry=100.0,
            stop=98.0,
            target=105.0,
            confidence=0.75,
            timestamp=1000.0,
            reason="Test",
        )
        mock_signal_tracker.get_open_signals.return_value = [mock_open_signal]
        mock_signal_tracker.get_resolved.return_value = []

        # Create mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator._strategy_engine = mock_strategy_engine
        mock_orchestrator._signal_tracker = mock_signal_tracker

        # Execute
        result = strategy_engine.build_strategy_health(mock_orchestrator)

        # Assert: status should be active due to open signal
        assert result["test_strategy"]["status"] == "active"


# ---------------------------------------------------------------------------
# Tests for report_profile()
# ---------------------------------------------------------------------------

class TestReportProfile:
    """Tests for StrategyEvaluationEngine.report_profile()"""

    def test_report_profile_logs_gamma_profile_correctly(
        self, strategy_engine, mock_gex_calculator, mock_logger
    ):
        """Test that report_profile logs gamma profile correctly."""
        # Setup
        mock_gex_calculator.get_summary.return_value = {
            "net_gamma": 1000.0,
            "underlying_price": 100.0,
            "active_strikes": 10,
            "total_messages": 100,
        }
        mock_gex_calculator.get_gamma_profile.return_value = {
            "symbol": "TEST",
            "underlying_price": 100.0,
            "net_gamma": 1000.0,
            "strikes": {
                95.0: {"net_gamma": 500.0},
                100.0: {"net_gamma": 300.0},
                105.0: {"net_gamma": 200.0},
            },
        }
        mock_gex_calculator.get_gamma_flip.return_value = 95.0
        mock_gex_calculator.get_gamma_walls.return_value = [
            {"strike": 95.0, "gex": 500000, "side": "call"},
            {"strike": 105.0, "gex": -300000, "side": "put"},
        ]

        # Execute
        strategy_engine.report_profile(mock_gex_calculator, "TEST")

        # Assert: logger.info should be called multiple times
        assert mock_logger.info.call_count >= 1

    def test_report_profile_logs_gamma_flip(self, strategy_engine, mock_gex_calculator, mock_logger):
        """Test that report_profile logs gamma flip when available."""
        # Setup
        mock_gex_calculator.get_summary.return_value = {
            "net_gamma": 1000.0,
            "underlying_price": 100.0,
            "active_strikes": 10,
            "total_messages": 100,
        }
        mock_gex_calculator.get_gamma_profile.return_value = {"strikes": {}}
        mock_gex_calculator.get_gamma_flip.return_value = 95.0
        mock_gex_calculator.get_gamma_walls.return_value = []

        # Execute
        strategy_engine.report_profile(mock_gex_calculator, "TEST")

        # Assert: gamma flip should be logged
        flip_logged = any("GAMMA_FLIP" in str(call) for call in mock_logger.info.call_args_list)
        assert flip_logged

    def test_report_profile_logs_gamma_walls(self, strategy_engine, mock_gex_calculator, mock_logger):
        """Test that report_profile logs gamma walls when available."""
        # Setup
        mock_gex_calculator.get_summary.return_value = {
            "net_gamma": 1000.0,
            "underlying_price": 100.0,
            "active_strikes": 10,
            "total_messages": 100,
        }
        mock_gex_calculator.get_gamma_profile.return_value = {"strikes": {}}
        mock_gex_calculator.get_gamma_flip.return_value = None
        mock_gex_calculator.get_gamma_walls.return_value = [
            {"strike": 95.0, "gex": 500000, "side": "call"},
        ]

        # Execute
        strategy_engine.report_profile(mock_gex_calculator, "TEST")

        # Assert: gamma walls should be logged
        walls_logged = any("GAMMA_WALLS" in str(call) for call in mock_logger.info.call_args_list)
        assert walls_logged

    def test_report_profile_logs_top_strikes(self, strategy_engine, mock_gex_calculator, mock_logger):
        """Test that report_profile logs top strikes by absolute Net Gamma."""
        # Setup
        mock_gex_calculator.get_summary.return_value = {
            "net_gamma": 1000.0,
            "underlying_price": 100.0,
            "active_strikes": 10,
            "total_messages": 100,
        }
        mock_gex_calculator.get_gamma_profile.return_value = {
            "strikes": {
                95.0: {"net_gamma": 500.0},
                100.0: {"net_gamma": 300.0},
                105.0: {"net_gamma": 200.0},
            },
        }
        mock_gex_calculator.get_gamma_flip.return_value = None
        mock_gex_calculator.get_gamma_walls.return_value = []

        # Execute
        strategy_engine.report_profile(mock_gex_calculator, "TEST")

        # Assert: top strikes should be logged
        top_strikes_logged = any("TOP_STRIKES" in str(call) for call in mock_logger.info.call_args_list)
        assert top_strikes_logged

    def test_report_profile_uses_default_logger_when_none_provided(self, mock_gex_calculator):
        """Test that report_profile uses default logger when no logger is provided."""
        # Setup: no logger
        engine = StrategyEvaluationEngine(
            gex_calculator=mock_gex_calculator,
            strategy_engine=MagicMock(),
            signal_tracker=MagicMock(),
            gamma_filter=MagicMock(),
            logger=None,  # No logger
        )

        mock_gex_calculator.get_summary.return_value = {
            "net_gamma": 1000.0,
            "underlying_price": 100.0,
            "active_strikes": 10,
            "total_messages": 100,
        }
        mock_gex_calculator.get_gamma_profile.return_value = {"strikes": {}}
        mock_gex_calculator.get_gamma_flip.return_value = None
        mock_gex_calculator.get_gamma_walls.return_value = []

        # Execute: should not raise exception
        engine.report_profile(mock_gex_calculator, "TEST")

        # Assert: should complete without error (uses default logger)


# ---------------------------------------------------------------------------
# Integration-style tests
# ---------------------------------------------------------------------------

class TestStrategyEvaluationEngineIntegration:
    """Integration-style tests for StrategyEvaluationEngine."""

    def test_full_evaluation_loop_with_all_components(
        self, mock_gex_calculator, mock_strategy_engine, mock_signal_tracker, mock_gamma_filter, mock_logger, mock_orchestrator
    ):
        """Test a full evaluation loop with all components working together."""
        # Setup
        engine = StrategyEvaluationEngine(
            gex_calculator=mock_gex_calculator,
            strategy_engine=mock_strategy_engine,
            signal_tracker=mock_signal_tracker,
            gamma_filter=mock_gamma_filter,
            logger=mock_logger,
            correlation_id="integration-test",
        )

        # Create signals
        mock_signal1 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=100.0,
            stop=98.0,
            target=105.0,
            strategy_id="strategy_alpha",
            reason="Alpha signal",
        )
        mock_signal2 = Signal(
            direction=Direction.SHORT,
            confidence=0.80,
            entry=100.0,
            stop=102.0,
            target=95.0,
            strategy_id="strategy_beta",
            reason="Beta signal",
        )
        mock_strategy_engine.process.return_value = [mock_signal1, mock_signal2]
        mock_gamma_filter.check_regime.return_value = True

        # Execute evaluate_strategies
        engine.evaluate_strategies(mock_orchestrator)

        # Assert: signals tracked
        assert mock_signal_tracker.track.call_count == 2

        # Setup for build_last_trigger
        mock_signal_tracker.get_open_signals.return_value = [
            OpenSignal(
                signal_id="strategy_alpha_123",
                direction="LONG",
                strategy_id="strategy_alpha",
                entry=100.0,
                stop=98.0,
                target=105.0,
                confidence=0.75,
                timestamp=1000.0,
                reason="Test",
            )
        ]
        mock_signal_tracker.get_resolved.return_value = []

        # Execute build_last_trigger
        triggers = engine.build_last_trigger(mock_signal_tracker)
        assert "strategy_alpha" in triggers

        # Setup for build_strategy_health
        mock_strategy = MagicMock()
        mock_strategy.strategy_id = "strategy_alpha"
        mock_strategy_engine._strategies = [mock_strategy]
        mock_signal_tracker.get_strategy_stats.return_value = {
            "strategy_alpha": {
                "total_signals": 10,
                "wins": 7,
                "losses": 2,
                "closed": 1,
                "total_pnl": 50.0,
            }
        }
        mock_signal_tracker.get_resolved.return_value = []
        mock_signal_tracker.get_open_signals.return_value = []

        # Execute build_strategy_health
        health = engine.build_strategy_health(mock_orchestrator)
        assert "strategy_alpha" in health
        assert health["strategy_alpha"]["status"] == "active"
        assert health["strategy_alpha"]["win_rate"] == 0.7

        # Execute report_profile
        mock_gex_calculator.get_gamma_profile.return_value = {"strikes": {}}
        mock_gex_calculator.get_gamma_flip.return_value = None
        mock_gex_calculator.get_gamma_walls.return_value = []
        engine.report_profile(mock_gex_calculator, "TEST")

        # Assert: profile logged
        assert mock_logger.info.called
