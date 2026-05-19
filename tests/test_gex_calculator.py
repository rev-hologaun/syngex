"""
tests/test_gex_calculator.py — Test GEX calculations
"""

import pytest
from engine.gex_calculator import GEXCalculator, _StrikeBucket


class TestStrikeBucket:
    """Test _StrikeBucket internal class."""

    def test_bucket_creation(self):
        """Test creating a strike bucket."""
        bucket = _StrikeBucket(strike=195.0)

        assert bucket.strike == 195.0
        assert bucket.call_gamma_oi == 0.0
        assert bucket.put_gamma_oi == 0.0
        assert bucket.net_gamma == 0.0

    def test_net_gamma_call(self):
        """Test net_gamma with call gamma."""
        bucket = _StrikeBucket(strike=195.0)
        bucket.call_gamma_oi = 25.0
        bucket.put_gamma_oi = 0.0

        assert bucket.net_gamma == 25.0

    def test_net_gamma_put(self):
        """Test net_gamma with put gamma."""
        bucket = _StrikeBucket(strike=195.0)
        bucket.call_gamma_oi = 0.0
        bucket.put_gamma_oi = 20.0

        assert bucket.net_gamma == -20.0

    def test_net_gamma_mixed(self):
        """Test net_gamma with both call and put gamma."""
        bucket = _StrikeBucket(strike=195.0)
        bucket.call_gamma_oi = 25.0
        bucket.put_gamma_oi = 20.0

        assert bucket.net_gamma == 5.0

    def test_normalized_gamma(self):
        """Test normalized gamma calculation."""
        bucket = _StrikeBucket(strike=195.0)
        bucket.call_gamma_oi = 25.0
        bucket.call_count = 5
        bucket.put_gamma_oi = 0.0
        bucket.put_count = 0

        # Normalized = 25.0 / 5 = 5.0
        assert bucket.normalized_gamma() == pytest.approx(5.0)

    def test_normalized_gamma_no_messages(self):
        """Test normalized gamma with no messages."""
        bucket = _StrikeBucket(strike=195.0)
        assert bucket.normalized_gamma() == 0.0


class TestGEXCalculatorInitialization:
    """Test GEXCalculator initialization."""

    def test_create_calculator(self):
        """Test creating a GEXCalculator."""
        calc = GEXCalculator(symbol="TSLA")

        assert calc.symbol == "TSLA"
        assert calc.underlying_price == 0.0
        assert calc._msg_count == 0

    def test_set_underlying_price(self):
        """Test setting underlying price."""
        calc = GEXCalculator(symbol="TSLA")
        calc.set_underlying_price(195.00)

        assert calc.underlying_price == 195.00


class TestGEXAggregation:
    """Test GEX aggregation from stream data."""

    def test_process_option_update_call(self, gex_calculator, sample_option_message):
        """Test processing a call option update."""
        gex_calculator.process_message(sample_option_message)

        # Strike 195.0 should have call gamma
        assert 195.0 in gex_calculator._ladder
        bucket = gex_calculator._ladder[195.0]
        assert bucket.call_gamma_oi == pytest.approx(25.0)  # 0.025 * 1000
        assert bucket.put_gamma_oi == 0.0

    def test_process_option_update_put(self, gex_calculator, sample_put_message):
        """Test processing a put option update."""
        gex_calculator.process_message(sample_put_message)

        # Strike 195.0 should have put gamma
        assert 195.0 in gex_calculator._ladder
        bucket = gex_calculator._ladder[195.0]
        assert bucket.put_gamma_oi == pytest.approx(16.0)  # 0.020 * 800
        assert bucket.call_gamma_oi == 0.0

    def test_aggregate_calls_and_puts(self, gex_calculator, sample_option_message, sample_put_message):
        """Test aggregating calls and puts at same strike."""
        gex_calculator.process_message(sample_option_message)
        gex_calculator.process_message(sample_put_message)

        bucket = gex_calculator._ladder[195.0]
        assert bucket.call_gamma_oi == pytest.approx(25.0)
        assert bucket.put_gamma_oi == pytest.approx(16.0)
        assert bucket.net_gamma == pytest.approx(9.0)

    def test_multiple_messages_same_strike(self, gex_calculator):
        """Test multiple messages to same strike accumulate."""
        msg1 = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.01,
            "open_interest": 500.0,
            "side": "call",
        }
        msg2 = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.015,
            "open_interest": 600.0,
            "side": "call",
        }

        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)

        bucket = gex_calculator._ladder[195.0]
        # First: 0.01 * 500 = 5.0
        # Second: 0.015 * 600 = 9.0
        # Total: 14.0
        assert bucket.call_gamma_oi == pytest.approx(14.0)

    def test_underlying_price_update(self, gex_calculator):
        """Test underlying price update via message."""
        msg = {"type": "underlying_update", "price": 196.50}
        gex_calculator.process_message(msg)

        assert gex_calculator.underlying_price == 196.50


class TestGammaLadderBucketing:
    """Test gamma ladder bucketing by strike."""

    def test_multiple_strikes(self, gex_calculator):
        """Test bucketing across multiple strikes."""
        messages = [
            {"type": "option_update", "strike": 190.0, "gamma": 0.02, "open_interest": 1000.0, "side": "call"},
            {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"},
            {"type": "option_update", "strike": 200.0, "gamma": 0.03, "open_interest": 1000.0, "side": "call"},
        ]

        for msg in messages:
            gex_calculator.process_message(msg)

        assert 190.0 in gex_calculator._ladder
        assert 195.0 in gex_calculator._ladder
        assert 200.0 in gex_calculator._ladder

        assert gex_calculator._ladder[190.0].call_gamma_oi == pytest.approx(20.0)
        assert gex_calculator._ladder[195.0].call_gamma_oi == pytest.approx(25.0)
        assert gex_calculator._ladder[200.0].call_gamma_oi == pytest.approx(30.0)

    def test_strike_bucket_separation(self, gex_calculator):
        """Test that different strikes have separate buckets."""
        msg1 = {"type": "option_update", "strike": 195.0, "gamma": 0.02, "open_interest": 1000.0, "side": "call"}
        msg2 = {"type": "option_update", "strike": 196.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}

        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)

        assert gex_calculator._ladder[195.0].call_gamma_oi == pytest.approx(20.0)
        assert gex_calculator._ladder[196.0].call_gamma_oi == pytest.approx(25.0)
        # Each bucket should only have its own gamma
        assert gex_calculator._ladder[195.0].call_gamma_oi != gex_calculator._ladder[196.0].call_gamma_oi


class TestIVCalculation:
    """Test IV calculation by strike."""

    def test_iv_by_strike(self, gex_calculator):
        """Test IV calculation at a strike."""
        msg = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "iv": 0.45,
        }
        gex_calculator.process_message(msg)

        iv = gex_calculator.get_iv_by_strike(195.0)
        assert iv == pytest.approx(0.45)

    def test_iv_by_strike_multiple_messages(self, gex_calculator):
        """Test IV averaging across multiple messages."""
        msg1 = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "iv": 0.40,
        }
        msg2 = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "iv": 0.50,
        }
        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)

        # Average IV should be (0.40 + 0.50) / 2 = 0.45
        iv = gex_calculator.get_iv_by_strike(195.0)
        assert iv == pytest.approx(0.45)

    def test_iv_by_strike_no_data(self, gex_calculator):
        """Test IV when no data exists."""
        iv = gex_calculator.get_iv_by_strike(200.0)
        assert iv is None

    def test_iv_skew(self, gex_calculator):
        """Test IV skew calculation (call IV - put IV)."""
        call_msg = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "iv": 0.45,
        }
        put_msg = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.020,
            "open_interest": 800.0,
            "side": "put",
            "iv": 0.50,
        }
        gex_calculator.process_message(call_msg)
        gex_calculator.process_message(put_msg)

        # Skew = avg_call_iv - avg_put_iv = 0.45 - 0.50 = -0.05
        skew = gex_calculator.get_iv_skew()
        assert skew == pytest.approx(-0.05)

    def test_iv_skew_insufficient_data(self, gex_calculator):
        """Test IV skew with insufficient data."""
        # Only calls, no puts
        call_msg = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "iv": 0.45,
        }
        gex_calculator.process_message(call_msg)

        skew = gex_calculator.get_iv_skew()
        assert skew is None


class TestGammaWallDetection:
    """Test gamma wall detection."""

    def test_gamma_wall_detection(self, gex_calculator):
        """Test detecting gamma walls."""
        # Set underlying price
        gex_calculator.set_underlying_price(195.00)

        # Create a large gamma position at strike 195
        msg = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.50,  # Large gamma
            "open_interest": 10000.0,  # Large OI
            "side": "call",
        }
        gex_calculator.process_message(msg)

        # GEX = normalized_gamma * 100 * underlying_price
        # normalized_gamma = 5000 / 1 = 5000
        # GEX = 5000 * 100 * 195 = 97,500,000
        walls = gex_calculator.get_gamma_walls(threshold=1_000_000)

        assert len(walls) > 0
        assert walls[0]["strike"] == 195.0
        assert walls[0]["side"] == "call"

    def test_gamma_wall_no_walls(self, gex_calculator):
        """Test when no walls exist."""
        gex_calculator.set_underlying_price(195.00)

        # Small gamma position
        msg = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.01,
            "open_interest": 100.0,
            "side": "call",
        }
        gex_calculator.process_message(msg)

        # With high threshold, no walls should be detected
        walls = gex_calculator.get_gamma_walls(threshold=1_000_000_000)
        assert len(walls) == 0

    def test_gamma_wall_put(self, gex_calculator):
        """Test detecting put gamma wall."""
        gex_calculator.set_underlying_price(195.00)

        msg = {
            "type": "option_update",
            "strike": 190.0,
            "gamma": 0.50,
            "open_interest": 10000.0,
            "side": "put",
        }
        gex_calculator.process_message(msg)

        walls = gex_calculator.get_gamma_walls(threshold=1_000_000)

        assert len(walls) > 0
        assert walls[0]["strike"] == 190.0
        assert walls[0]["side"] == "put"

    def test_gamma_walls_sorted_by_gex(self, gex_calculator):
        """Test that walls are sorted by absolute GEX."""
        gex_calculator.set_underlying_price(195.00)

        # Create walls at different strikes with different sizes
        msg1 = {"type": "option_update", "strike": 190.0, "gamma": 0.10, "open_interest": 1000.0, "side": "put"}
        msg2 = {"type": "option_update", "strike": 195.0, "gamma": 0.50, "open_interest": 10000.0, "side": "call"}
        msg3 = {"type": "option_update", "strike": 200.0, "gamma": 0.30, "open_interest": 5000.0, "side": "call"}

        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)
        gex_calculator.process_message(msg3)

        walls = gex_calculator.get_gamma_walls(threshold=100_000)

        # Should be sorted by absolute GEX (largest first)
        assert len(walls) >= 2
        assert abs(walls[0]["gex"]) >= abs(walls[1]["gex"])


class TestNetGammaCalculations:
    """Test net gamma calculations."""

    def test_get_net_gamma(self, gex_calculator):
        """Test total net gamma calculation."""
        msg1 = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        msg2 = {"type": "option_update", "strike": 195.0, "gamma": 0.020, "open_interest": 800.0, "side": "put"}

        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)

        # Net gamma = 25.0 - 16.0 = 9.0
        net_gamma = gex_calculator.get_net_gamma()
        assert net_gamma == pytest.approx(9.0)

    def test_get_normalized_net_gamma(self, gex_calculator):
        """Test normalized net gamma calculation."""
        msg1 = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        msg2 = {"type": "option_update", "strike": 195.0, "gamma": 0.020, "open_interest": 800.0, "side": "put"}

        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)

        # Normalized net gamma = (25.0/1) - (16.0/1) = 9.0
        # But note: the bucket has 2 messages total (1 call + 1 put)
        # So normalized = net_gamma / total_count = 9.0 / 2 = 4.5
        # Actually, looking at the code, it sums normalized per strike
        # bucket.normalized_gamma() = net_gamma / (call_count + put_count) = 9.0 / 2 = 4.5
        norm_net_gamma = gex_calculator.get_normalized_net_gamma()
        assert norm_net_gamma == pytest.approx(4.5)

    def test_get_strike_net_gamma(self, gex_calculator):
        """Test net gamma for specific strike."""
        msg = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        gex_calculator.process_message(msg)

        strike_gamma = gex_calculator.get_strike_net_gamma(195.0)
        assert strike_gamma == pytest.approx(25.0)

    def test_get_strike_net_gamma_no_data(self, gex_calculator):
        """Test net gamma for strike with no data."""
        strike_gamma = gex_calculator.get_strike_net_gamma(200.0)
        assert strike_gamma == 0.0


class TestGEXCalculations:
    """Test GEX (dollar gamma) calculations."""

    def test_get_strike_gex(self, gex_calculator):
        """Test GEX for specific strike."""
        gex_calculator.set_underlying_price(195.00)
        msg = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        gex_calculator.process_message(msg)

        # GEX = normalized_net_gamma * 100 * underlying_price
        # normalized_net_gamma = 25.0 / 1 = 25.0
        # GEX = 25.0 * 100 * 195 = 487,500
        gex = gex_calculator.get_strike_gex(195.0)
        assert gex == pytest.approx(487500.0)

    def test_get_strike_gex_no_underlying_price(self, gex_calculator):
        """Test GEX when underlying price is not set."""
        # Note: gex_calculator fixture sets underlying price to 195.00
        # So we need to test with a fresh calculator
        calc = GEXCalculator(symbol="TSLA")
        # Don't set underlying price - leave it at 0
        msg = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        calc.process_message(msg)

        # Underlying price is 0, so GEX should be 0
        gex = calc.get_strike_gex(195.0)
        assert gex == pytest.approx(0.0)


class TestGammaFlip:
    """Test gamma flip point detection."""

    def test_gamma_flip_detection(self, gex_calculator):
        """Test detecting gamma flip point."""
        gex_calculator.set_underlying_price(195.00)

        # Create positive gamma above, negative below
        msg1 = {"type": "option_update", "strike": 200.0, "gamma": 0.50, "open_interest": 1000.0, "side": "call"}
        msg2 = {"type": "option_update", "strike": 195.0, "gamma": 0.30, "open_interest": 2000.0, "side": "put"}

        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)

        # Flip should be at or near 195.0
        flip = gex_calculator.get_gamma_flip()
        assert flip is not None
        assert flip <= 200.0

    def test_gamma_flip_no_flip(self, gex_calculator):
        """Test when no gamma flip exists."""
        gex_calculator.set_underlying_price(195.00)

        # All positive gamma
        msg = {"type": "option_update", "strike": 195.0, "gamma": 0.50, "open_interest": 1000.0, "side": "call"}
        gex_calculator.process_message(msg)

        flip = gex_calculator.get_gamma_flip()
        # No flip if all gamma is positive
        assert flip is None


class TestGammaProfile:
    """Test gamma profile output."""

    def test_get_gamma_profile(self, gex_calculator):
        """Test getting full gamma profile."""
        gex_calculator.set_underlying_price(195.00)

        msg = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        gex_calculator.process_message(msg)

        profile = gex_calculator.get_gamma_profile()

        assert profile["symbol"] == "TSLA"
        assert profile["underlying_price"] == 195.00
        assert "strikes" in profile
        assert 195.0 in profile["strikes"]

    def test_get_summary(self, gex_calculator):
        """Test getting calculator summary."""
        msg = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        gex_calculator.process_message(msg)

        summary = gex_calculator.get_summary()

        assert summary["symbol"] == "TSLA"
        assert summary["active_strikes"] == 1
        assert summary["total_messages"] == 1
        assert summary["option_updates"] == 1


class TestGreeksSummary:
    """Test greeks summary output."""

    def test_get_greeks_summary(self, gex_calculator):
        """Test getting greeks summary."""
        msg = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "delta": 0.55,
            "iv": 0.45,
        }
        gex_calculator.process_message(msg)

        summary = gex_calculator.get_greeks_summary()

        assert 195.0 in summary
        assert summary[195.0]["net_gamma"] == pytest.approx(25.0)
        assert summary[195.0]["call_gamma"] == pytest.approx(25.0)
        assert summary[195.0]["net_oi"] == pytest.approx(1000.0)

    def test_get_delta_by_strike(self, gex_calculator):
        """Test getting delta by strike."""
        msg = {
            "type": "option_update",
            "strike": 195.0,
            "gamma": 0.025,
            "open_interest": 1000.0,
            "side": "call",
            "delta": 0.55,
        }
        gex_calculator.process_message(msg)

        delta_data = gex_calculator.get_delta_by_strike(195.0)

        assert delta_data["call_delta"] == pytest.approx(0.55)
        assert delta_data["net_delta"] == pytest.approx(0.55)


class TestATMStrike:
    """Test ATM strike detection."""

    def test_get_atm_strike(self, gex_calculator):
        """Test finding ATM strike."""
        gex_calculator.set_underlying_price(195.75)

        # Add strikes at 195.0 and 197.5
        msg1 = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        msg2 = {"type": "option_update", "strike": 197.5, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}

        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)

        atm = gex_calculator.get_atm_strike(195.75)

        # 195.75 is 0.75 from 195.0 and 1.75 from 197.5
        # So 195.0 should be closer
        assert atm == 195.0

    def test_get_atm_strike_empty_ladder(self, gex_calculator):
        """Test ATM strike with empty ladder."""
        atm = gex_calculator.get_atm_strike(195.00)
        assert atm is None


class TestStreamGreeksProcessing:
    """Test processing stream greeks objects."""

    def test_process_stream_greeks_itm_call(self, gex_calculator):
        """Test processing stream greeks for ITM call."""
        gex_calculator.set_underlying_price(195.00)

        # ITM call: delta > 0, intrinsic > 0
        msg = {
            "Delta": 0.70,
            "Gamma": 0.025,
            "IntrinsicValue": 5.0,  # Strike = 195 - 5 = 190
            "ImpliedVolatility": 0.45,
            "ProbabilityITM": 0.70,
        }

        gex_calculator.process_message(msg)

        # Should infer strike at 190.0
        assert 190.0 in gex_calculator._ladder

    def test_process_stream_greeks_otm_put(self, gex_calculator):
        """Test processing stream greeks for OTM put."""
        gex_calculator.set_underlying_price(195.00)

        # OTM put: delta < 0, intrinsic = 0, low ProbITM
        msg = {
            "Delta": -0.20,
            "Gamma": 0.015,
            "IntrinsicValue": 0.0,
            "ImpliedVolatility": 0.50,
            "ProbabilityITM": 0.10,  # Far OTM
        }

        gex_calculator.process_message(msg)

        # Should infer strike based on probability
        # ProbITM = 0.10 means ~4 strikes OTM (0.40 away from 0.50)
        # Strike = 195 - 4 * 2.5 = 185.0
        assert len(gex_calculator._ladder) > 0

    def test_process_stream_greeks_invalid_gamma(self, gex_calculator):
        """Test that invalid gamma is skipped."""
        msg = {
            "Delta": 0.50,
            "Gamma": 0.0,  # Invalid
            "IntrinsicValue": 0.0,
        }

        gex_calculator.process_message(msg)

        # No strikes should be added
        assert len(gex_calculator._ladder) == 0


class TestRawContractProcessing:
    """Test processing raw TradeStation contract messages."""

    def test_process_raw_contract_call(self, gex_calculator):
        """Test processing raw contract message."""
        msg = {
            "Gamma": "0.025",
            "DailyOpenInterest": 1000,
            "Side": "Call",
            "Strikes": ["195.0"],
        }

        gex_calculator.process_message(msg)

        assert 195.0 in gex_calculator._ladder
        assert gex_calculator._ladder[195.0].call_gamma_oi == pytest.approx(25.0)

    def test_process_raw_contract_put(self, gex_calculator):
        """Test processing raw put contract message."""
        msg = {
            "Gamma": 0.020,
            "DailyOpenInterest": 800,
            "Side": "Put",
            "Strikes": [195.0],
        }

        gex_calculator.process_message(msg)

        assert 195.0 in gex_calculator._ladder
        assert gex_calculator._ladder[195.0].put_gamma_oi == pytest.approx(16.0)


class TestOptionChainProcessing:
    """Test processing raw option chain responses."""

    def test_process_option_chain(self, gex_calculator):
        """Test processing option chain response."""
        # The code expects 'optionChain' or 'option_chain' wrapper
        chain = {
            "optionChain": {
                "underlying": {"lastPrice": 195.50},
                "calls": [
                    {"strike": 195.0, "gamma": 0.025, "openInterest": 1000, "symbol": "TSLA230616C00195000"},
                    {"strike": 200.0, "gamma": 0.020, "openInterest": 800, "symbol": "TSLA230616C00200000"},
                ],
                "puts": [
                    {"strike": 190.0, "gamma": 0.015, "openInterest": 600, "symbol": "TSLA230616P00190000"},
                ],
            }
        }

        gex_calculator.process_message(chain)

        # Verify underlying price was updated
        assert gex_calculator.underlying_price == pytest.approx(195.50)
        # Verify strikes were added
        assert 195.0 in gex_calculator._ladder
        assert 200.0 in gex_calculator._ladder
        assert 190.0 in gex_calculator._ladder


class TestOpenInterestUpdate:
    """Test open interest updates."""

    def test_set_open_interest(self, gex_calculator):
        """Test updating open interest."""
        msg = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        gex_calculator.process_message(msg)

        # Update with real OI
        gex_calculator.set_open_interest(strike=195.0, call_oi=5000.0, put_oi=0.0)

        bucket = gex_calculator._ladder[195.0]
        # gamma_oi should be recalculated: avg_gamma * new_oi
        # avg_gamma = call_gamma / call_count = 25.0 / 1 = 25.0
        # new gamma_oi = 25.0 * 5000 = 125000
        # But the code does: avg_call_gamma = bucket.call_gamma / bucket.call_count
        # bucket.call_gamma = 0.025 (the raw gamma, not gamma_oi)
        # So avg_call_gamma = 0.025 / 1 = 0.025
        # new gamma_oi = 0.025 * 5000 = 125.0
        assert bucket.call_gamma_oi == pytest.approx(125.0)
        assert bucket.call_oi == pytest.approx(5000.0)

    def test_set_open_interest_no_bucket(self, gex_calculator, caplog):
        """Test updating OI for non-existent strike."""
        gex_calculator.set_open_interest(strike=200.0, call_oi=1000.0, put_oi=0.0)

        # Should log warning and not create bucket
        assert 200.0 not in gex_calculator._ladder


class TestMessageCounting:
    """Test message and option counting."""

    def test_message_count(self, gex_calculator):
        """Test message counting."""
        msg1 = {"type": "option_update", "strike": 195.0, "gamma": 0.025, "open_interest": 1000.0, "side": "call"}
        msg2 = {"type": "underlying_update", "price": 195.50}

        gex_calculator.process_message(msg1)
        gex_calculator.process_message(msg2)

        assert gex_calculator._msg_count == 2
        assert gex_calculator._option_count == 1
        assert gex_calculator._quote_count == 1
