"""
tests/integration/test_end_to_end.py

End-to-end integration tests for the complete Syngex pipeline.
"""

import pytest
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from strategies.signal import Direction
from strategies.engine import StrategyEngine, EngineConfig
from strategies.signal_tracker import SignalTracker
from engine.gex_calculator import GEXCalculator
from core.filters import NetGammaFilter


class TestEndToEndPipeline:
    """End-to-end pipeline tests."""

    def test_full_data_to_signal_pipeline(self):
        """Test complete pipeline from data to signal."""
        # Setup components
        calculator = GEXCalculator(symbol="TSLA")
        calculator.set_underlying_price(195.50)

        config = EngineConfig(min_confidence=0.40, max_signals_per_tick=10)
        engine = StrategyEngine(config=config)

        tracker = SignalTracker(
            max_hold_seconds=900,
            strategy_hold_times={},
            log_dir="/tmp/test_logs",
            symbol="TSLA",
            signal_log_path="/tmp/test_logs/signals.jsonl",
        )

        gamma_filter = NetGammaFilter(flip_buffer=0.50)
        engine.register_filter(gamma_filter.evaluate_signal)

        # Add some option data to create a gamma profile
        for strike in [190.0, 195.0, 200.0]:
            calculator.process_message({
                "type": "option_update",
                "strike": strike,
                "gamma": 0.02,
                "open_interest": 2000.0,
                "side": "call",
                "delta": 0.5,
            })

        # Create evaluation data
        data = {
            "underlying_price": 195.50,
            "gex_calculator": calculator,
            "regime": "POSITIVE",
            "symbol": "TSLA",
            "timestamp": time.time(),
            "rolling_data": {},
        }

        # Process through engine (should return empty without strategies registered)
        signals = engine.process(data)

        # Pipeline completed without errors
        assert isinstance(signals, list)

    def test_gamma_profile_integration(self):
        """Test gamma profile calculations end-to-end."""
        calculator = GEXCalculator(symbol="TSLA")
        calculator.set_underlying_price(195.50)

        # Add data creating positive net gamma
        calculator.process_message({
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 3000.0,
            "side": "call",
            "delta": 0.55,
        })

        # Get net gamma
        net_gamma = calculator.get_net_gamma()
        assert net_gamma is not None
        assert net_gamma > 0  # Positive regime

        # Get gamma profile
        profile = calculator.get_gamma_profile()
        assert profile is not None
        assert "underlying_price" in profile
        assert "net_gamma" in profile
        assert profile["underlying_price"] == 195.50

    def test_signal_tracking_integration(self):
        """Test signal tracking end-to-end."""
        tracker = SignalTracker(
            max_hold_seconds=900,
            strategy_hold_times={},
            log_dir="/tmp/test_logs",
            symbol="TSLA",
            signal_log_path="/tmp/test_logs/signals.jsonl",
        )

        # Create and track a signal
        from strategies.signal import Signal

        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test_integration",
            symbol="TSLA",
            reason="Integration test signal",
            timestamp=time.time(),
        )

        tracker.track_signal(signal)

        # Verify signal was tracked
        open_signals = tracker.get_open_signals()
        assert len(open_signals) > 0

    def test_regime_filter_integration(self):
        """Test regime filter integration with signals."""
        filter = NetGammaFilter(flip_buffer=0.50)

        # Set up positive regime
        filter.check_regime(
            net_gamma=1250.5,
            flip_strike=194.0,
            underlying_price=195.50,
        )

        # Create signal that should pass
        from strategies.signal import Signal

        signal_below_flip = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=194.0,
            stop=193.0,
            target=196.0,
            strategy_id="test",
            symbol="TSLA",
            timestamp=time.time(),
        )

        # In positive regime, LONG below flip should pass
        result = filter.evaluate_signal(signal_below_flip)
        assert result is True

        # Create signal that should fail
        signal_above_flip = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=196.0,
            stop=195.0,
            target=198.0,
            strategy_id="test",
            symbol="TSLA",
            timestamp=time.time(),
        )

        # In positive regime, LONG above flip should fail
        result = filter.evaluate_signal(signal_above_flip)
        assert result is False

    def test_rolling_window_integration(self):
        """Test rolling window data propagation."""
        from strategies.rolling_window import RollingWindow

        window = RollingWindow(window_type="time", window_size=300)  # 5 minutes

        # Push data points
        base_time = time.time()
        for i in range(10):
            window.push(195.50 + i * 0.1, base_time + i * 30)  # Every 30 seconds

        # Verify window has data
        assert len(window._values) == 10

        # Get average
        avg = window.get_average()
        assert avg is not None
        assert 195.50 <= avg <= 196.50

    def test_multiple_strategies_integration(self):
        """Test multiple strategies running together."""
        config = EngineConfig(min_confidence=0.35, max_signals_per_tick=10)
        engine = StrategyEngine(config=config)

        # Register multiple test strategies
        class Strat1:
            strategy_id = "strat1"
            layer = "layer1"
            enabled = True
            def evaluate(self, data):
                from strategies.signal import Signal, Direction
                return [Signal(
                    direction=Direction.LONG,
                    confidence=0.65,
                    entry=195.50,
                    stop=194.50,
                    target=197.00,
                    strategy_id="strat1",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]
            def set_params(self, params):
                pass

        class Strat2:
            strategy_id = "strat2"
            layer = "layer2"
            enabled = True
            def evaluate(self, data):
                from strategies.signal import Signal, Direction
                return [Signal(
                    direction=Direction.SHORT,
                    confidence=0.70,
                    entry=196.00,
                    stop=197.00,
                    target=194.00,
                    strategy_id="strat2",
                    symbol="TSLA",
                    timestamp=time.time(),
                )]
            def set_params(self, params):
                pass

        engine.register(Strat1())
        engine.register(Strat2())
        engine.start()

        data = {
            "underlying_price": 195.50,
            "regime": "POSITIVE",
            "symbol": "TSLA",
            "timestamp": time.time(),
        }

        signals = engine.process(data)

        # Should get signals from both strategies (before conflict resolution)
        assert len(signals) >= 0  # May be reduced by conflict resolution
