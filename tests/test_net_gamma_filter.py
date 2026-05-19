"""
tests/test_net_gamma_filter.py — Unit tests for NetGammaFilter

Tests for the Net Gamma Regime Filter (Phase 4 component).
"""

import pytest
from core.filters import NetGammaFilter, Regime


class TestNetGammaFilterInit:
    """Test NetGammaFilter initialization."""

    def test_default_flip_buffer(self):
        """Test default flip_buffer is 0.50."""
        filter = NetGammaFilter()
        assert filter.flip_buffer == 0.50

    def test_custom_flip_buffer(self):
        """Test custom flip_buffer value."""
        filter = NetGammaFilter(flip_buffer=1.00)
        assert filter.flip_buffer == 1.00

    def test_default_regime_is_positive(self):
        """Test default regime is POSITIVE."""
        filter = NetGammaFilter()
        assert filter.regime == Regime.POSITIVE

    def test_flip_buffer_property_setter(self):
        """Test flip_buffer property setter."""
        filter = NetGammaFilter()
        filter.flip_buffer = 2.00
        assert filter.flip_buffer == 2.00


class TestCheckRegimePositive:
    """Test check_regime() with positive net_gamma."""

    def test_positive_net_gamma_returns_positive_regime(self):
        """Test positive net_gamma results in POSITIVE regime."""
        filter = NetGammaFilter()
        # When price is far from flip_strike, not transitioning
        result = filter.check_regime(
            net_gamma=100.0,
            flip_strike=195.0,
            underlying_price=200.0  # 5 away from flip, outside default 0.50 buffer
        )
        assert filter.regime == Regime.POSITIVE
        assert result is True  # Not transitioning

    def test_positive_net_gamma_large_value(self):
        """Test large positive net_gamma."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=10000.0,
            flip_strike=195.0,
            underlying_price=210.0  # Far from flip
        )
        assert filter.regime == Regime.POSITIVE
        assert result is True

    def test_positive_net_gamma_small_value(self):
        """Test small positive net_gamma."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=0.01,
            flip_strike=195.0,
            underlying_price=205.0  # Far from flip
        )
        assert filter.regime == Regime.POSITIVE
        assert result is True

    def test_zero_net_gamma(self):
        """Test net_gamma = 0 defaults to POSITIVE regime."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=0.0,
            flip_strike=195.0,
            underlying_price=200.0  # Far from flip
        )
        assert filter.regime == Regime.POSITIVE
        assert result is True


class TestCheckRegimeNegative:
    """Test check_regime() with negative net_gamma."""

    def test_negative_net_gamma_returns_negative_regime(self):
        """Test negative net_gamma results in NEGATIVE regime."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=-100.0,
            flip_strike=195.0,
            underlying_price=200.0  # Far from flip
        )
        assert filter.regime == Regime.NEGATIVE
        assert result is True  # Not transitioning

    def test_negative_net_gamma_large_value(self):
        """Test large negative net_gamma."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=-10000.0,
            flip_strike=195.0,
            underlying_price=210.0  # Far from flip
        )
        assert filter.regime == Regime.NEGATIVE
        assert result is True

    def test_negative_net_gamma_small_value(self):
        """Test small negative net_gamma."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=-0.01,
            flip_strike=195.0,
            underlying_price=205.0  # Far from flip
        )
        assert filter.regime == Regime.NEGATIVE
        assert result is True


class TestRegimeTransitions:
    """Test regime transitions when crossing flip threshold."""

    def test_transition_from_positive_to_negative(self):
        """Test transition from POSITIVE to NEGATIVE regime."""
        filter = NetGammaFilter()

        # Start in positive regime
        filter.check_regime(100.0, 195.0, 195.0)
        assert filter.regime == Regime.POSITIVE

        # Cross to negative regime
        filter.check_regime(-100.0, 195.0, 195.0)
        assert filter.regime == Regime.NEGATIVE

    def test_transition_from_negative_to_positive(self):
        """Test transition from NEGATIVE to POSITIVE regime."""
        filter = NetGammaFilter()

        # Start in negative regime
        filter.check_regime(-100.0, 195.0, 195.0)
        assert filter.regime == Regime.NEGATIVE

        # Cross to positive regime
        filter.check_regime(100.0, 195.0, 195.0)
        assert filter.regime == Regime.POSITIVE

    def test_multiple_transitions(self):
        """Test multiple regime transitions."""
        filter = NetGammaFilter()

        # Positive → Negative → Positive → Negative
        filter.check_regime(100.0, 195.0, 195.0)
        assert filter.regime == Regime.POSITIVE

        filter.check_regime(-100.0, 195.0, 195.0)
        assert filter.regime == Regime.NEGATIVE

        filter.check_regime(100.0, 195.0, 195.0)
        assert filter.regime == Regime.POSITIVE

        filter.check_regime(-100.0, 195.0, 195.0)
        assert filter.regime == Regime.NEGATIVE


class TestFlipBufferBehavior:
    """Test flip_buffer_pct behavior (prevents rapid flipping)."""

    def test_transitioning_when_within_buffer(self):
        """Test that transitioning is True when price is within buffer zone."""
        filter = NetGammaFilter(flip_buffer=1.00)

        # flip_strike = 195.0, flip_buffer = 1.00
        # Buffer zone: 194.0 to 196.0 (distance < 1.00 from flip_strike)
        # Using relative distance: distance = |price - flip| / price
        # transitioning = distance < (flip_buffer / underlying_price)
        # For price=195.0, flip=195.0: distance=0, threshold=1/195=0.0051
        # 0 < 0.0051 → transitioning=True

        result = filter.check_regime(
            net_gamma=100.0,
            flip_strike=195.0,
            underlying_price=195.0  # Exactly at flip strike
        )
        assert filter.transitioning is True
        assert result is False  # Signals blocked during transition

    def test_not_transitioning_when_outside_buffer(self):
        """Test that transitioning is False when price is outside buffer zone."""
        filter = NetGammaFilter(flip_buffer=1.00)

        # flip_strike = 195.0, flip_buffer = 1.00
        # Price at 200.0: distance = |200-195|/200 = 0.025
        # threshold = 1.00/200 = 0.005
        # 0.025 > 0.005 → transitioning=False

        result = filter.check_regime(
            net_gamma=100.0,
            flip_strike=195.0,
            underlying_price=200.0  # Well above flip strike
        )
        assert filter.transitioning is False
        assert result is True  # Signals allowed

    def test_buffer_zone_prevents_whipsaw(self):
        """Test that buffer zone prevents rapid regime flipping."""
        filter = NetGammaFilter(flip_buffer=2.00)

        # At flip strike, should be transitioning
        filter.check_regime(100.0, 195.0, 195.0)
        assert filter.transitioning is True

        # Small price movement, still in buffer
        filter.check_regime(100.0, 195.0, 195.50)
        # distance = 0.50/195.50 = 0.00256
        # threshold = 2.00/195.50 = 0.0102
        # 0.00256 < 0.0102 → transitioning=True
        assert filter.transitioning is True

    def test_larger_buffer_wider_transition_zone(self):
        """Test that larger flip_buffer creates wider transition zone."""
        filter_small = NetGammaFilter(flip_buffer=0.50)
        filter_large = NetGammaFilter(flip_buffer=2.00)

        # Price slightly away from flip
        price = 196.0
        flip = 195.0

        # Small buffer: distance = 1/196 = 0.0051, threshold = 0.5/196 = 0.0026
        # 0.0051 > 0.0026 → not transitioning
        filter_small.check_regime(100.0, flip, price)
        assert filter_small.transitioning is False

        # Large buffer: distance = 1/196 = 0.0051, threshold = 2/196 = 0.0102
        # 0.0051 < 0.0102 → transitioning
        filter_large.check_regime(100.0, flip, price)
        assert filter_large.transitioning is True


class TestEdgeCases:
    """Test edge cases: net_gamma = 0, flip = None."""

    def test_flip_strike_none(self):
        """Test behavior when flip_strike is None."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=100.0,
            flip_strike=None,
            underlying_price=195.0
        )
        assert filter.regime == Regime.POSITIVE
        assert filter.transitioning is False
        assert result is True

    def test_underlying_price_zero(self):
        """Test behavior when underlying_price is 0."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=100.0,
            flip_strike=195.0,
            underlying_price=0.0
        )
        assert filter.regime == Regime.POSITIVE
        assert filter.transitioning is False
        assert result is True

    def test_both_flip_and_price_none_zero(self):
        """Test when both flip_strike and underlying_price are None/0."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=100.0,
            flip_strike=None,
            underlying_price=0.0
        )
        assert filter.regime == Regime.POSITIVE
        assert filter.transitioning is False
        assert result is True

    def test_very_small_underlying_price(self):
        """Test with very small underlying price."""
        filter = NetGammaFilter()
        result = filter.check_regime(
            net_gamma=100.0,
            flip_strike=0.01,
            underlying_price=0.02  # 0.01 away, outside 0.50 buffer (but relative)
        )
        # Should not crash, regime determined by net_gamma
        assert filter.regime == Regime.POSITIVE
        # distance = 0.01/0.02 = 0.5, threshold = 0.50/0.02 = 25, so transitioning=True
        # Actually at 0.02 with flip=0.01: distance = 0.01/0.02 = 0.5, threshold = 0.50/0.02 = 25
        # 0.5 < 25, so transitioning is True, result is False
        assert result is False  # In transition zone due to relative calculation


class TestRegimeStability:
    """Test regime stays stable when within buffer zone."""

    def test_regime_stable_within_buffer(self):
        """Test regime doesn't flip when price moves within buffer."""
        filter = NetGammaFilter(flip_buffer=5.00)

        # Start at flip strike
        filter.check_regime(100.0, 195.0, 195.0)
        initial_regime = filter.regime

        # Move price within buffer (but not crossing net_gamma sign)
        filter.check_regime(100.0, 195.0, 197.0)
        assert filter.regime == initial_regime

        filter.check_regime(100.0, 195.0, 193.0)
        assert filter.regime == initial_regime

    def test_regime_only_changes_on_net_gamma_sign_change(self):
        """Test regime only changes when net_gamma sign changes."""
        filter = NetGammaFilter()

        # Price moves significantly but net_gamma stays positive
        filter.check_regime(100.0, 195.0, 190.0)
        assert filter.regime == Regime.POSITIVE

        filter.check_regime(50.0, 195.0, 200.0)
        assert filter.regime == Regime.POSITIVE

        filter.check_regime(0.01, 195.0, 185.0)
        assert filter.regime == Regime.POSITIVE

    def test_transitioning_state_persists_within_buffer(self):
        """Test transitioning state remains True while price in buffer."""
        filter = NetGammaFilter(flip_buffer=3.00)

        # At flip strike
        filter.check_regime(100.0, 195.0, 195.0)
        assert filter.transitioning is True

        # Small movement within buffer
        filter.check_regime(100.0, 195.0, 196.0)
        # distance = 1/196 = 0.0051, threshold = 3/196 = 0.0153
        assert filter.transitioning is True

        # Another small movement
        filter.check_regime(100.0, 195.0, 194.0)
        # distance = 1/194 = 0.0052, threshold = 3/194 = 0.0155
        assert filter.transitioning is True


class TestGetStatus:
    """Test get_status() method."""

    def test_get_status_returns_correct_dict(self):
        """Test get_status returns expected structure."""
        filter = NetGammaFilter(flip_buffer=1.00)
        filter.check_regime(100.0, 195.0, 195.0)

        status = filter.get_status()

        assert "regime" in status
        assert "flip_strike" in status
        assert "underlying_price" in status
        assert "transitioning" in status

    def test_get_status_values(self):
        """Test get_status returns correct values."""
        filter = NetGammaFilter(flip_buffer=1.00)
        filter.check_regime(100.0, 195.0, 195.0)

        status = filter.get_status()

        assert status["regime"] == "POSITIVE"
        assert status["flip_strike"] == 195.0
        assert status["underlying_price"] == 195.0
        assert status["transitioning"] is True

    def test_get_status_after_regime_change(self):
        """Test get_status after regime change."""
        filter = NetGammaFilter()
        filter.check_regime(-100.0, 200.0, 200.0)

        status = filter.get_status()

        assert status["regime"] == "NEGATIVE"
        assert status["flip_strike"] == 200.0
        assert status["underlying_price"] == 200.0
