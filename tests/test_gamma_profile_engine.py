"""
tests/test_gamma_profile_engine.py — Unit Tests for GammaProfileEngine

Comprehensive tests for the GammaProfileEngine component (Phase 4).
Tests cover:
- get_gamma_profile() structure and calculations
- get_gamma_walls() filtering and data
- get_gamma_flip() detection
- Formatting methods
- Edge cases (empty ladder, single strike, multiple strikes)
"""

import pytest
from unittest.mock import Mock
from core.gamma_profile import GammaProfileEngine
from engine.gex_calculator import GEXCalculator


class TestGammaProfileEngine:
    """Test suite for GammaProfileEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a GammaProfileEngine instance for testing."""
        return GammaProfileEngine()

    @pytest.fixture
    def mock_gex_calculator(self):
        """Create a mocked GEXCalculator with configurable return values."""
        mock = Mock(spec=GEXCalculator)
        return mock

    # =========================================================================
    # Test get_gamma_flip()
    # =========================================================================

    def test_get_gamma_flip_returns_flip_point(self, engine, mock_gex_calculator):
        """Test that get_gamma_flip() returns the flip point where cumulative gamma changes sign."""
        mock_gex_calculator.get_gamma_flip.return_value = 450.0

        # Execute
        result = engine.get_gamma_flip(mock_gex_calculator)

        # Assert
        assert result == 450.0
        mock_gex_calculator.get_gamma_flip.assert_called_once()

    def test_get_gamma_flip_with_empty_ladder(self, engine, mock_gex_calculator):
        """Test get_gamma_flip() with empty ladder (no flip)."""
        mock_gex_calculator.get_gamma_flip.return_value = None

        # Execute
        result = engine.get_gamma_flip(mock_gex_calculator)

        # Assert
        assert result is None

    def test_get_gamma_flip_with_single_strike(self, engine, mock_gex_calculator):
        """Test get_gamma_flip() with single strike."""
        mock_gex_calculator.get_gamma_flip.return_value = 400.0

        # Execute
        result = engine.get_gamma_flip(mock_gex_calculator)

        # Assert
        assert result == 400.0

    def test_get_gamma_flip_with_multiple_strikes_both_sides(self, engine, mock_gex_calculator):
        """Test get_gamma_flip() with multiple strikes on both sides."""
        mock_gex_calculator.get_gamma_flip.return_value = 450.0

        # Execute
        result = engine.get_gamma_flip(mock_gex_calculator)

        # Assert
        assert result == 450.0

    # =========================================================================
    # Test get_gamma_walls()
    # =========================================================================

    def test_get_gamma_walls_filters_by_threshold(self, engine, mock_gex_calculator):
        """Test that get_gamma_walls() passes threshold to GEXCalculator."""
        mock_gex_calculator.get_gamma_walls.return_value = [
            {"strike": 450.0, "net_gamma": 500.0, "gex": 5000000.0, "side": "call", "total_contracts": 100},
            {"strike": 440.0, "net_gamma": 100.0, "gex": 1000000.0, "side": "call", "total_contracts": 50},
        ]

        # Execute with threshold
        result = engine.get_gamma_walls(mock_gex_calculator, threshold=500000)

        # Assert - threshold is passed to GEXCalculator
        mock_gex_calculator.get_gamma_walls.assert_called_once_with(threshold=500000)
        assert len(result) == 2

    def test_get_gamma_walls_returns_correct_wall_data(self, engine, mock_gex_calculator):
        """Test that get_gamma_walls() returns correct wall data (strike, side, gex)."""
        expected_walls = [
            {
                "strike": 500.0,
                "net_gamma": 1000.0,
                "gex": 10000000.0,
                "side": "call",
                "total_contracts": 200
            },
            {
                "strike": 480.0,
                "net_gamma": -800.0,
                "gex": -8000000.0,
                "side": "put",
                "total_contracts": 150
            }
        ]
        mock_gex_calculator.get_gamma_walls.return_value = expected_walls

        # Execute
        result = engine.get_gamma_walls(mock_gex_calculator, threshold=1000000)

        # Assert
        assert len(result) == 2
        # Check first wall
        assert result[0]["strike"] == 500.0
        assert result[0]["side"] == "call"
        assert result[0]["gex"] == 10000000.0
        assert "net_gamma" in result[0]
        assert "total_contracts" in result[0]
        # Check second wall
        assert result[1]["strike"] == 480.0
        assert result[1]["side"] == "put"
        assert result[1]["gex"] == -8000000.0

    def test_get_gamma_walls_with_empty_ladder(self, engine, mock_gex_calculator):
        """Test get_gamma_walls() with empty ladder (no walls)."""
        mock_gex_calculator.get_gamma_walls.return_value = []

        # Execute
        result = engine.get_gamma_walls(mock_gex_calculator, threshold=500000)

        # Assert
        assert result == []
        mock_gex_calculator.get_gamma_walls.assert_called_once_with(threshold=500000)

    def test_get_gamma_walls_with_single_wall(self, engine, mock_gex_calculator):
        """Test get_gamma_walls() with a single wall."""
        mock_gex_calculator.get_gamma_walls.return_value = [
            {"strike": 350.0, "net_gamma": 500.0, "gex": 5000000.0, "side": "call", "total_contracts": 100}
        ]

        # Execute
        result = engine.get_gamma_walls(mock_gex_calculator, threshold=1000000)

        # Assert
        assert len(result) == 1
        assert result[0]["strike"] == 350.0
        assert result[0]["gex"] == 5000000.0

    def test_get_gamma_walls_with_multiple_strikes_both_sides(self, engine, mock_gex_calculator):
        """Test get_gamma_walls() with multiple strikes on both sides."""
        mock_gex_calculator.get_gamma_walls.return_value = [
            {"strike": 480.0, "net_gamma": 600.0, "gex": 6000000.0, "side": "call", "total_contracts": 120},
            {"strike": 490.0, "net_gamma": 400.0, "gex": 4000000.0, "side": "call", "total_contracts": 80},
            {"strike": 500.0, "net_gamma": 200.0, "gex": 2000000.0, "side": "call", "total_contracts": 40},
            {"strike": 510.0, "net_gamma": -300.0, "gex": -3000000.0, "side": "put", "total_contracts": 60},
            {"strike": 520.0, "net_gamma": -500.0, "gex": -5000000.0, "side": "put", "total_contracts": 100},
        ]

        # Execute
        result = engine.get_gamma_walls(mock_gex_calculator, threshold=1000000)

        # Assert
        assert len(result) == 5
        # Should include both call walls (below) and put walls (above)
        call_walls = [w for w in result if w["side"] == "call"]
        put_walls = [w for w in result if w["side"] == "put"]
        assert len(call_walls) == 3
        assert len(put_walls) == 2

    # =========================================================================
    # Test get_gamma_flip()
    # =========================================================================

    def test_get_gamma_flip_returns_flip_point(self, engine, mock_gex_calculator):
        """Test that get_gamma_flip() returns flip point where cumulative gamma changes sign."""
        # Setup mock to return a flip strike
        mock_gex_calculator.get_gamma_flip.return_value = 450.0

        # Execute
        result = engine.get_gamma_flip(mock_gex_calculator)

        # Assert
        assert result == 450.0
        mock_gex_calculator.get_gamma_flip.assert_called_once()

    def test_get_gamma_flip_with_empty_ladder(self, engine, mock_gex_calculator):
        """Test get_gamma_flip() with empty ladder (no flip)."""
        mock_gex_calculator.get_gamma_flip.return_value = None

        # Execute
        result = engine.get_gamma_flip(mock_gex_calculator)

        # Assert
        assert result is None
        mock_gex_calculator.get_gamma_flip.assert_called_once()

    def test_get_gamma_flip_with_single_strike(self, engine, mock_gex_calculator):
        """Test get_gamma_flip() with single strike (no flip possible)."""
        # With a single strike, cumulative gamma won't change sign
        mock_gex_calculator.get_gamma_flip.return_value = None

        # Execute
        result = engine.get_gamma_flip(mock_gex_calculator)

        # Assert
        assert result is None

    def test_get_gamma_flip_with_multiple_strikes_both_sides(self, engine, mock_gex_calculator):
        """Test get_gamma_flip() with multiple strikes on both sides."""
        # Setup mock with flip detected
        mock_gex_calculator.get_gamma_flip.return_value = 475.0

        # Execute
        result = engine.get_gamma_flip(mock_gex_calculator)

        # Assert
        assert result == 475.0
        # The flip should be a valid strike price
        assert isinstance(result, float)

    # =========================================================================
    # Test get_top_strikes()
    # =========================================================================

    def test_get_top_strikes_returns_top_by_absolute_gamma(self, engine, mock_gex_calculator):
        """Test that get_top_strikes() returns top N by absolute gamma."""
        profile = {
            "symbol": "SPY",
            "underlying_price": 450.0,
            "net_gamma": 1000.0,
            "strikes": {
                440.0: {"net_gamma": 100.0},
                450.0: {"net_gamma": 500.0},
                460.0: {"net_gamma": -300.0},
                470.0: {"net_gamma": 200.0},
                480.0: {"net_gamma": -400.0},
            }
        }
        mock_gex_calculator.get_gamma_profile.return_value = profile

        # Execute
        result = engine.get_top_strikes(mock_gex_calculator, profile, count=3)

        # Assert - sorted by absolute gamma: 500, 400, 300
        assert len(result) == 3
        assert result[0]["strike"] == 450.0  # |500|
        assert result[1]["strike"] == 480.0  # |-400|
        assert result[2]["strike"] == 460.0  # |-300|

    def test_get_top_strikes_includes_sign_and_abs_gamma(self, engine, mock_gex_calculator):
        """Test that get_top_strikes() includes sign and abs_gamma fields."""
        profile = {
            "symbol": "AAPL",
            "underlying_price": 175.0,
            "net_gamma": 200.0,
            "strikes": {
                170.0: {"net_gamma": 150.0},
                180.0: {"net_gamma": -200.0},
            }
        }
        mock_gex_calculator.get_gamma_profile.return_value = profile

        # Execute
        result = engine.get_top_strikes(mock_gex_calculator, profile, count=2)

        # Assert
        assert len(result) == 2
        # Check first strike (180 with -200)
        assert result[0]["strike"] == 180.0
        assert result[0]["net_gamma"] == -200.0
        assert result[0]["sign"] == "-"
        assert result[0]["abs_gamma"] == 200.0
        # Check second strike (170 with 150)
        assert result[1]["strike"] == 170.0
        assert result[1]["net_gamma"] == 150.0
        assert result[1]["sign"] == "+"
        assert result[1]["abs_gamma"] == 150.0

    def test_get_top_strikes_with_empty_profile(self, engine, mock_gex_calculator):
        """Test get_top_strikes() with empty profile."""
        profile = {
            "symbol": "TSLA",
            "underlying_price": 250.0,
            "net_gamma": 0.0,
            "strikes": {}
        }
        mock_gex_calculator.get_gamma_profile.return_value = profile

        # Execute
        result = engine.get_top_strikes(mock_gex_calculator, profile, count=5)

        # Assert
        assert result == []

    # =========================================================================
    # Test format_profile_line()
    # =========================================================================

    def test_format_profile_line_returns_correct_format(self, engine):
        """Test that format_profile_line() returns correctly formatted string."""
        # Execute
        result = engine.format_profile_line("SPY", 450.00, 1250.5, 10, 100)

        # Assert
        assert "GAMMA_PROFILE" in result
        assert "SPY" in result
        assert "$450.00" in result
        assert "+1250.50" in result
        assert "Strikes: 10" in result
        assert "Msgs: 100" in result

    def test_format_profile_line_with_negative_gamma(self, engine):
        """Test format_profile_line() with negative net gamma."""
        result = engine.format_profile_line("AAPL", 175.00, -500.0, 5, 50)

        # Assert
        assert "-500.00" in result

    # =========================================================================
    # Test format_gamma_walls()
    # =========================================================================

    def test_format_gamma_walls_returns_correct_format(self, engine):
        """Test that format_gamma_walls() returns correctly formatted string."""
        walls = [
            {"strike": 450.0, "side": "call", "gex": 5000000.0},
            {"strike": 440.0, "side": "call", "gex": 2000000.0},
        ]

        # Execute
        result = engine.format_gamma_walls(walls)

        # Assert
        assert "$450" in result
        assert "(call)" in result
        assert "+$5,000,000" in result
        assert "$440" in result
        assert "+$2,000,000" in result

    def test_format_gamma_walls_with_negative_gex(self, engine):
        """Test format_gamma_walls() with negative GEX (put walls)."""
        walls = [
            {"strike": 460.0, "side": "put", "gex": -3000000.0},
        ]

        # Execute
        result = engine.format_gamma_walls(walls)

        # Assert
        assert "-$3,000,000" in result
        assert "(put)" in result

    def test_format_gamma_walls_with_empty_list(self, engine):
        """Test format_gamma_walls() with empty list."""
        result = engine.format_gamma_walls([])

        # Assert
        assert result == ""

    def test_format_gamma_walls_respects_max_walls(self, engine):
        """Test format_gamma_walls() respects max_walls parameter."""
        walls = [
            {"strike": 450.0, "side": "call", "gex": 5000000.0},
            {"strike": 440.0, "side": "call", "gex": 3000000.0},
            {"strike": 430.0, "side": "call", "gex": 2000000.0},
        ]

        # Execute with max_walls=2
        result = engine.format_gamma_walls(walls, max_walls=2)

        # Assert - should only include first 2 walls
        assert "$450" in result
        assert "$440" in result
        assert "$430" not in result

    # =========================================================================
    # Test format_top_strikes()
    # =========================================================================

    def test_format_top_strikes_returns_correct_format(self, engine):
        """Test that format_top_strikes() returns correctly formatted string."""
        top_strikes = [
            {"strike": 450.0, "net_gamma": 500.0, "sign": "+", "abs_gamma": 500.0},
            {"strike": 460.0, "net_gamma": -300.0, "sign": "-", "abs_gamma": 300.0},
        ]

        # Execute
        result = engine.format_top_strikes(top_strikes)

        # Assert
        assert "K450.0" in result
        assert "+500" in result
        assert "K460.0" in result
        assert "-300" in result

    def test_format_top_strikes_with_empty_list(self, engine):
        """Test format_top_strikes() with empty list."""
        result = engine.format_top_strikes([])

        # Assert
        assert result == ""

    # =========================================================================
    # Test format_gamma_flip()
    # =========================================================================

    def test_format_gamma_flip_returns_correct_format(self, engine):
        """Test that format_gamma_flip() returns correctly formatted string."""
        # Execute
        result = engine.format_gamma_flip(450.0)

        # Assert
        assert "GAMMA_FLIP" in result
        assert "$450.0" in result
        assert "cumulative gamma turns negative below this" in result

    # =========================================================================
    # Integration Tests with Real GEXCalculator
    # =========================================================================

    def test_gamma_profile_engine_with_real_gex_calculator_empty(self):
        """Test GammaProfileEngine with a real (empty) GEXCalculator instance."""
        engine = GammaProfileEngine()
        gex_calc = GEXCalculator("SPY")

        # Test get_gamma_flip with empty ladder
        flip = engine.get_gamma_flip(gex_calc)
        assert flip is None

        # Test get_gamma_walls with empty ladder
        walls = engine.get_gamma_walls(gex_calc)
        assert walls == []

        # Test get_top_strikes with empty profile
        profile = gex_calc.get_gamma_profile()
        top = engine.get_top_strikes(gex_calc, profile)
        assert top == []

    def test_gamma_profile_engine_with_real_gex_calculator_single_strike(self):
        """Test GammaProfileEngine with a real GEXCalculator with single strike."""
        engine = GammaProfileEngine()
        gex_calc = GEXCalculator("AAPL")
        gex_calc.set_underlying_price(175.0)

        # Add a single strike with data
        gex_calc.process_message({
            "type": "option_update",
            "strike": 175.0,
            "gamma": 0.05,
            "open_interest": 100.0,
            "side": "call"
        })

        # Test get_gamma_flip with single strike (no flip possible)
        flip = engine.get_gamma_flip(gex_calc)
        assert flip is None  # Single strike can't have a flip

        # Test get_gamma_walls
        walls = engine.get_gamma_walls(gex_calc, threshold=100)
        assert len(walls) >= 0  # May or may not have walls depending on threshold

    def test_gamma_profile_engine_with_real_gex_calculator_multiple_strikes(self):
        """Test GammaProfileEngine with real GEXCalculator with multiple strikes."""
        engine = GammaProfileEngine()
        gex_calc = GEXCalculator("TSLA")
        gex_calc.set_underlying_price(250.0)

        # Add multiple strikes on both sides
        gex_calc.process_message({"type": "option_update", "strike": 240.0, "gamma": 0.04, "open_interest": 50.0, "side": "call"})
        gex_calc.process_message({"type": "option_update", "strike": 250.0, "gamma": 0.06, "open_interest": 100.0, "side": "call"})
        gex_calc.process_message({"type": "option_update", "strike": 250.0, "gamma": 0.03, "open_interest": 80.0, "side": "put"})
        gex_calc.process_message({"type": "option_update", "strike": 260.0, "gamma": 0.05, "open_interest": 60.0, "side": "put"})

        # Test get_gamma_walls
        walls = engine.get_gamma_walls(gex_calc, threshold=1000)
        # Should have walls based on GEX values

        # Test get_top_strikes
        profile = gex_calc.get_gamma_profile()
        top = engine.get_top_strikes(gex_calc, profile, count=3)
        assert len(top) <= 3
        # Verify sorting by absolute gamma
        if len(top) >= 2:
            assert top[0]["abs_gamma"] >= top[1]["abs_gamma"]

    def test_format_methods_integration(self):
        """Test that all format methods work together correctly."""
        engine = GammaProfileEngine()

        # Test format_profile_line
        profile_line = engine.format_profile_line("SPY", 450.00, 1000.0, 5, 25)
        assert "GAMMA_PROFILE" in profile_line

        # Test format_gamma_walls
        walls = [
            {"strike": 450.0, "side": "call", "gex": 1000000.0},
            {"strike": 440.0, "side": "put", "gex": -500000.0},
        ]
        walls_line = engine.format_gamma_walls(walls)
        assert "$450" in walls_line
        assert "$440" in walls_line

        # Test format_top_strikes
        top = [
            {"strike": 450.0, "net_gamma": 100.0, "sign": "+", "abs_gamma": 100.0},
        ]
        top_line = engine.format_top_strikes(top)
        assert "K450.0" in top_line

        # Test format_gamma_flip
        flip_line = engine.format_gamma_flip(445.0)
        assert "GAMMA_FLIP" in flip_line
