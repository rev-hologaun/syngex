"""
tests/unit/test_core/test_gex_engine.py

Unit tests for GEXCalculator.
"""

import pytest
from engine.gex_calculator import GEXCalculator, _StrikeBucket


class TestStrikeBucket:
    """Tests for _StrikeBucket dataclass."""

    def test_net_gamma_calculation(self):
        """Test net_gamma property."""
        bucket = _StrikeBucket(strike=195.0)
        bucket.call_gamma_oi = 80.0
        bucket.put_gamma_oi = 63.8

        assert bucket.net_gamma == 16.2

    def test_net_oi_calculation(self):
        """Test net_oi property."""
        bucket = _StrikeBucket(strike=195.0)
        bucket.call_oi = 3200.0
        bucket.put_oi = 2900.0

        assert bucket.net_oi == 300.0

    def test_net_delta_calculation(self):
        """Test net_delta property."""
        bucket = _StrikeBucket(strike=195.0)
        bucket.call_delta = 0.55
        bucket.put_delta = -0.45

        assert bucket.net_delta == 1.0

    def test_normalized_gamma(self):
        """Test normalized (per-message average) net gamma."""
        bucket = _StrikeBucket(strike=195.0)
        bucket.call_gamma_oi = 80.0
        bucket.put_gamma_oi = 63.8
        bucket.call_count = 2
        bucket.put_count = 2

        # (80 - 63.8) / (2 + 2) = 16.2 / 4 = 4.05
        assert bucket.normalized_gamma() == 4.05

    def test_normalized_gamma_zero_count(self):
        """Test normalized gamma with zero count."""
        bucket = _StrikeBucket(strike=195.0)
        assert bucket.normalized_gamma() == 0.0


class TestGEXCalculator:
    """Tests for GEXCalculator."""

    def test_create_calculator(self):
        """Test calculator creation."""
        calc = GEXCalculator(symbol="TSLA")

        assert calc.symbol == "TSLA"
        assert calc.underlying_price == 0.0
        assert calc._msg_count == 0

    def test_set_underlying_price(self):
        """Test setting underlying price."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        assert calc.underlying_price == 195.50

    def test_process_option_message(self):
        """Test processing option update message."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        message = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "delta": 0.55,
        }

        calc.process_message(message)

        assert calc._msg_count == 1
        assert calc._option_count == 1
        assert 195.0 in calc._ladder

    def test_process_underlying_message(self):
        """Test processing underlying update message."""
        calc = GEXCalculator(symbol="TSLA")

        message = {
            "type": "underlying_update",
            "price": 195.50,
        }

        calc.process_message(message)

        assert calc.underlying_price == 195.50

    def test_get_net_gamma(self):
        """Test get_net_gamma()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        # Add some option data
        calc.process_message({
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
        })

        net_gamma = calc.get_net_gamma()
        assert net_gamma is not None
        assert net_gamma >= 0

    def test_get_atm_strike(self):
        """Test get_atm_strike()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        # Add strikes around ATM
        for strike in [190.0, 195.0, 200.0]:
            calc.process_message({
                "type": "option_update",
                "strike": strike,
                "gamma": 0.02,
                "open_interest": 1000.0,
                "side": "call",
            })

        atm = calc.get_atm_strike(195.50)
        assert atm == 195.0

    def test_get_greeks_summary(self):
        """Test get_greeks_summary()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        # Add option data
        calc.process_message({
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "delta": 0.55,
            "volume": 100,
        })

        summary = calc.get_greeks_summary()

        assert summary is not None
        assert "net_delta" in summary
        assert "underlying_price" in summary
        assert summary["underlying_price"] == 195.50

    def test_get_gamma_flip(self):
        """Test get_gamma_flip()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        # Add data that creates a flip
        calc.process_message({
            "type": "option_update",
            "strike": 190.0,
            "gamma": 0.015,
            "open_interest": 2500.0,
            "side": "call",
        })
        calc.process_message({
            "type": "option_update",
            "strike": 200.0,
            "gamma": 0.018,
            "open_interest": 4100.0,
            "side": "put",
        })

        flip = calc.get_gamma_flip()
        # Should return a flip strike or None
        assert flip is None or isinstance(flip, float)

    def test_get_gamma_walls(self):
        """Test get_gamma_walls()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        # Add data for walls
        for strike in [190.0, 195.0, 200.0]:
            calc.process_message({
                "type": "option_update",
                "strike": strike,
                "gamma": 0.02,
                "open_interest": 5000.0,
                "side": "call",
            })

        walls = calc.get_gamma_walls(threshold=50000)
        assert isinstance(walls, list)

    def test_get_iv_by_strike_avg(self):
        """Test get_iv_by_strike_avg()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        calc.process_message({
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "iv": 0.48,
        })

        iv_by_strike = calc.get_iv_by_strike_avg()
        assert 195.0 in iv_by_strike

    def test_get_iv_skew(self):
        """Test get_iv_skew()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        # Add call and put at same strike
        calc.process_message({
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "iv": 0.48,
        })
        calc.process_message({
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.022,
            "open_interest": 900.0,
            "side": "put",
            "iv": 0.50,
        })

        skew = calc.get_iv_skew()
        # Skew should be call_iv - put_iv (negative if puts higher)
        assert skew is not None

    def test_get_gamma_profile(self):
        """Test get_gamma_profile()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        # Add some strikes
        for strike in [190.0, 195.0, 200.0]:
            calc.process_message({
                "type": "option_update",
                "strike": strike,
                "gamma": 0.02,
                "open_interest": 1000.0,
                "side": "call",
            })

        profile = calc.get_gamma_profile()

        assert "underlying_price" in profile
        assert "net_gamma" in profile
        assert "strikes" in profile

    def test_get_summary(self):
        """Test get_summary()."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.50)

        summary = calc.get_summary()

        assert "underlying_price" in summary
        assert summary["underlying_price"] == 195.50
