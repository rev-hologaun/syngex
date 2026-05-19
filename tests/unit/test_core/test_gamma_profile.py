"""
tests/unit/test_core/test_gamma_profile.py

Unit tests for GammaProfileEngine.
"""

import pytest
from unittest.mock import MagicMock

from core.gamma_profile import GammaProfileEngine


class TestGammaProfileEngine:
    """Tests for GammaProfileEngine."""

    def test_create_engine(self):
        """Test engine creation."""
        engine = GammaProfileEngine()
        assert engine is not None

    def test_get_gamma_flip(self):
        """Test get_gamma_flip delegates to calculator."""
        engine = GammaProfileEngine()
        mock_calc = MagicMock()
        mock_calc.get_gamma_flip.return_value = 194.0

        flip = engine.get_gamma_flip(mock_calc)

        assert flip == 194.0
        mock_calc.get_gamma_flip.assert_called_once()

    def test_get_gamma_walls(self):
        """Test get_gamma_walls delegates to calculator."""
        engine = GammaProfileEngine()
        mock_calc = MagicMock()
        mock_calc.get_gamma_walls.return_value = [
            {"strike": 200.0, "net_gamma": 2500.0, "gex": 487500.0, "side": "call"},
        ]

        walls = engine.get_gamma_walls(mock_calc, threshold=50000)

        assert len(walls) == 1
        assert walls[0]["strike"] == 200.0

    def test_get_top_strikes(self):
        """Test get_top_strikes()."""
        engine = GammaProfileEngine()
        profile = {
            "strikes": {
                190.0: {"net_gamma": 50.0},
                195.0: {"net_gamma": 16.2},
                200.0: {"net_gamma": 18.0},
            }
        }

        top = engine.get_top_strikes(None, profile, count=2)

        assert len(top) == 2
        # Should be sorted by absolute net_gamma
        assert top[0]["strike"] == 190.0
        assert top[0]["abs_gamma"] == 50.0

    def test_format_profile_line(self):
        """Test format_profile_line()."""
        engine = GammaProfileEngine()

        line = engine.format_profile_line(
            symbol="TSLA",
            price=195.50,
            net_gamma=1250.5,
            strikes=10,
            messages=100,
        )

        assert "TSLA" in line
        assert "195.50" in line
        assert "+1250.50" in line

    def test_format_gamma_walls(self):
        """Test format_gamma_walls()."""
        engine = GammaProfileEngine()

        walls = [
            {"strike": 200.0, "net_gamma": 2500.0, "gex": 487500.0, "side": "call"},
            {"strike": 195.0, "net_gamma": -1800.0, "gex": -351000.0, "side": "put"},
        ]

        line = engine.format_gamma_walls(walls)

        assert "$200" in line
        assert "$195" in line

    def test_format_gamma_walls_empty(self):
        """Test format_gamma_walls with empty list."""
        engine = GammaProfileEngine()

        line = engine.format_gamma_walls([])

        assert line == ""

    def test_format_top_strikes(self):
        """Test format_top_strikes()."""
        engine = GammaProfileEngine()

        top = [
            {"strike": 190.0, "net_gamma": 50.0, "sign": "+", "abs_gamma": 50.0},
            {"strike": 200.0, "net_gamma": 18.0, "sign": "+", "abs_gamma": 18.0},
        ]

        line = engine.format_top_strikes(top)

        assert "K190.0" in line
        assert "K200.0" in line

    def test_format_gamma_flip(self):
        """Test format_gamma_flip()."""
        engine = GammaProfileEngine()

        line = engine.format_gamma_flip(194.0)

        assert "194.0" in line
        assert "GAMMA_FLIP" in line
