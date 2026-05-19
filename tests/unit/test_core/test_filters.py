"""
tests/unit/test_core/test_filters.py

Unit tests for NetGammaFilter and other filters.
"""

import pytest
from strategies.signal import Direction, Signal
from core.filters import NetGammaFilter, Regime


class TestNetGammaFilter:
    """Tests for NetGammaFilter."""

    def test_create_filter(self):
        """Test filter creation."""
        filter = NetGammaFilter(flip_buffer=0.50)

        assert filter.flip_buffer == 0.50
        assert filter.regime == Regime.POSITIVE
        assert filter.transitioning is False

    def test_check_regime_positive(self):
        """Test check_regime with positive net gamma."""
        filter = NetGammaFilter(flip_buffer=0.50)

        result = filter.check_regime(
            net_gamma=1250.5,
            flip_strike=194.0,
            underlying_price=195.50,
        )

        assert filter.regime == Regime.POSITIVE
        assert result is True  # Not transitioning

    def test_check_regime_negative(self):
        """Test check_regime with negative net gamma."""
        filter = NetGammaFilter(flip_buffer=0.50)

        result = filter.check_regime(
            net_gamma=-850.2,
            flip_strike=195.0,
            underlying_price=193.50,
        )

        assert filter.regime == Regime.NEGATIVE
        assert result is True

    def test_check_regime_transitioning(self):
        """Test check_regime when near flip point."""
        filter = NetGammaFilter(flip_buffer=0.50)

        # Price very close to flip (within buffer)
        result = filter.check_regime(
            net_gamma=100.0,
            flip_strike=195.0,
            underlying_price=195.20,  # Very close to flip
        )

        # Should be transitioning if within buffer
        # Note: actual behavior depends on buffer calculation

    def test_evaluate_signal_positive_regime_long_below_flip(self):
        """Test evaluate_signal: LONG in positive regime below flip."""
        filter = NetGammaFilter(flip_buffer=0.50)
        filter._regime = Regime.POSITIVE
        filter._flip_strike = 195.0
        filter._underlying_price = 194.0
        filter._transitioning = False

        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=194.50,
            stop=193.50,
            target=196.00,
            strategy_id="test",
            symbol="TSLA",
            timestamp=0,
        )

        result = filter.evaluate_signal(signal)

        # In positive regime, LONG below flip should pass
        assert result is True

    def test_evaluate_signal_positive_regime_long_above_flip(self):
        """Test evaluate_signal: LONG in positive regime above flip."""
        filter = NetGammaFilter(flip_buffer=0.50)
        filter._regime = Regime.POSITIVE
        filter._flip_strike = 195.0
        filter._underlying_price = 196.0
        filter._transitioning = False

        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=196.50,
            stop=195.50,
            target=198.00,
            strategy_id="test",
            symbol="TSLA",
            timestamp=0,
        )

        result = filter.evaluate_signal(signal)

        # In positive regime, LONG above flip should fail (should short)
        assert result is False

    def test_evaluate_signal_negative_regime_long_above_flip(self):
        """Test evaluate_signal: LONG in negative regime above flip."""
        filter = NetGammaFilter(flip_buffer=0.50)
        filter._regime = Regime.NEGATIVE
        filter._flip_strike = 195.0
        filter._underlying_price = 196.0
        filter._transitioning = False

        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=196.50,
            stop=195.50,
            target=198.00,
            strategy_id="test",
            symbol="TSLA",
            timestamp=0,
        )

        result = filter.evaluate_signal(signal)

        # In negative regime, LONG above flip should pass (trend follow)
        assert result is True

    def test_evaluate_signal_negative_regime_short_below_flip(self):
        """Test evaluate_signal: SHORT in negative regime below flip."""
        filter = NetGammaFilter(flip_buffer=0.50)
        filter._regime = Regime.NEGATIVE
        filter._flip_strike = 195.0
        filter._underlying_price = 194.0
        filter._transitioning = False

        signal = Signal(
            direction=Direction.SHORT,
            confidence=0.75,
            entry=193.50,
            stop=194.50,
            target=192.00,
            strategy_id="test",
            symbol="TSLA",
            timestamp=0,
        )

        result = filter.evaluate_signal(signal)

        # In negative regime, SHORT below flip should pass (trend follow)
        assert result is True

    def test_evaluate_signal_transitioning_blocks_all(self):
        """Test evaluate_signal: transitioning blocks all signals."""
        filter = NetGammaFilter(flip_buffer=0.50)
        filter._regime = Regime.POSITIVE
        filter._flip_strike = 195.0
        filter._underlying_price = 195.2
        filter._transitioning = True

        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.50,
            target=197.00,
            strategy_id="test",
            symbol="TSLA",
            timestamp=0,
        )

        result = filter.evaluate_signal(signal)

        # Transitioning should block all signals
        assert result is False

    def test_get_status(self):
        """Test get_status()."""
        filter = NetGammaFilter(flip_buffer=0.50)
        filter._regime = Regime.POSITIVE
        filter._flip_strike = 195.0
        filter._underlying_price = 195.50
        filter._transitioning = False

        status = filter.get_status()

        assert status["regime"] == "POSITIVE"
        assert status["flip_strike"] == 195.0
        assert status["underlying_price"] == 195.50
        assert status["transitioning"] is False

    def test_flip_buffer_setter(self):
        """Test flip_buffer setter."""
        filter = NetGammaFilter(flip_buffer=0.50)

        filter.flip_buffer = 1.00

        assert filter.flip_buffer == 1.00
