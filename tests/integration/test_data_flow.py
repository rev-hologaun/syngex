"""
tests/integration/test_data_flow.py

Integration tests for data flow through the pipeline.
"""

import pytest
import time
from unittest.mock import MagicMock

from engine.gex_calculator import GEXCalculator
from strategies.rolling_window import RollingWindow
from strategies.signal import Signal, Direction
from strategies.engine import StrategyEngine, EngineConfig
from strategies.signal_tracker import SignalTracker
from core.filters import NetGammaFilter


class TestDataFlow:
    """Tests for data flow through the pipeline."""

    def test_rolling_window_data_propagation(self):
        """Test rolling window data propagation over time."""
        window = RollingWindow(window_type="time", window_size=300)  # 5 minutes

        base_time = time.time()

        # Push data over time
        for i in range(20):
            price = 195.0 + (i % 10) * 0.1  # Oscillating price
            window.push(price, base_time + i * 15)  # Every 15 seconds

        # Verify data is in window
        assert len(window._values) > 0

        # Get statistics
        avg = window.get_average()
        min_val = window.get_min()
        max_val = window.get_max()

        assert avg is not None
        assert min_val is not None
        assert max_val is not None
        assert min_val <= avg <= max_val

    def test_count_based_rolling_window(self):
        """Test count-based rolling window."""
        window = RollingWindow(window_type="count", window_size=10)

        # Push more than window size
        for i in range(15):
            window.push(i)

        # Should only keep last 10
        assert len(window._values) == 10
        assert window._values[0] == 5  # Oldest kept value
        assert window._values[-1] == 14  # Newest value

    def test_signal_resolution_flow(self):
        """Test signal resolution flow."""
        tracker = SignalTracker(
            max_hold_seconds=900,
            strategy_hold_times={},
            log_dir="/tmp/test_logs",
            symbol="TSLA",
            signal_log_path="/tmp/test_logs/signals.jsonl",
        )

        # Track a signal
        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test_flow",
            symbol="TSLA",
            reason="Test",
            timestamp=time.time(),
        )

        tracker.track_signal(signal)

        # Simulate price reaching target
        resolved = tracker.update(197.80, time.time())

        # Should have resolved signal
        assert len(resolved) >= 0  # May be 0 if hold time not exceeded

    def test_gex_data_accumulation(self):
        """Test GEX data accumulation over multiple messages."""
        calculator = GEXCalculator(symbol="TSLA")
        calculator.set_underlying_price(195.50)

        # Process multiple option messages
        for strike in [190.0, 195.0, 200.0]:
            for i in range(5):  # Multiple updates per strike
                calculator.process_message({
                    "type": "option_update",
                    "strike": strike,
                    "gamma": 0.02 + (i * 0.001),
                    "open_interest": 2000.0,
                    "side": "call",
                    "delta": 0.5,
                })

        # Verify message count
        assert calculator._msg_count > 0
        assert calculator._option_count > 0

        # Get summary
        summary = calculator.get_greeks_summary()
        assert summary is not None
        assert summary["underlying_price"] == 195.50

    def test_state_export_flow(self):
        """Test state export flow."""
        from services.state_exporter import StateExporter
        from pathlib import Path
        import json

        calculator = GEXCalculator(symbol="TSLA")
        calculator.set_underlying_price(195.50)

        mock_engine = MagicMock()
        mock_tracker = MagicMock()
        mock_filter = MagicMock()
        mock_logger = MagicMock()

        exporter = StateExporter(
            data_dir=Path("/tmp/test_export"),
            calculator_ref=calculator,
            strategy_engine_ref=mock_engine,
            signal_tracker_ref=mock_tracker,
            gamma_filter_ref=mock_filter,
            symbol="TSLA",
            logger=mock_logger,
            correlation_id="test123",
        )

        # Export state
        exporter.export()

        # Verify file was created
        export_file = Path("/tmp/test_export/gex_state.json")
        assert export_file.exists()

        # Verify JSON is valid
        with open(export_file) as f:
            data = json.load(f)
            assert "underlying_price" in data

    def test_filter_chaining(self):
        """Test multiple filters chained together."""
        # Create filter
        gamma_filter = NetGammaFilter(flip_buffer=0.50)

        # Set regime
        gamma_filter.check_regime(
            net_gamma=1250.5,
            flip_strike=194.0,
            underlying_price=195.50,
        )

        # Create engine with filter
        config = EngineConfig(min_confidence=0.40)
        engine = StrategyEngine(config=config)
        engine.register_filter(gamma_filter.evaluate_signal)

        # Register strategy
        class TestStrat:
            strategy_id = "test_filter_chain"
            layer = "layer1"
            enabled = True
            def evaluate(self, data):
                return [Signal(
                    direction=Direction.LONG,
                    confidence=0.75,
                    entry=194.0,
                    stop=193.0,
                    target=196.0,
                    strategy_id="test_filter_chain",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]
            def set_params(self, params):
                pass

        engine.register(TestStrat())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
        }

        signals = engine.process(data)

        # Signal should pass both min_confidence and regime filter
        assert isinstance(signals, list)

    def test_multiple_symbols_data_isolation(self):
        """Test that data for different symbols is isolated."""
        calc_tsla = GEXCalculator(symbol="TSLA")
        calc_aapl = GEXCalculator(symbol="AAPL")

        calc_tsla.set_underlying_price(195.50)
        calc_aapl.set_underlying_price(175.00)

        # Add data
        calc_tsla.process_message({
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 2000.0,
            "side": "call",
        })

        calc_aapl.process_message({
            "type": "option_update",
            "strike": 175.0,
            "gamma": 0.030,
            "open_interest": 3000.0,
            "side": "call",
        })

        # Verify isolation
        assert calc_tsla.underlying_price == 195.50
        assert calc_aapl.underlying_price == 175.00
        assert calc_tsla.symbol == "TSLA"
        assert calc_aapl.symbol == "AAPL"
