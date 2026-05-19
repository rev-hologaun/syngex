"""
tests/test_utils.py — Tests for strategies/utils.py

Tests for the normalize_confidence utility function.
"""

import pytest
from strategies.utils import normalize_confidence


class TestNormalizeConfidence:
    """Tests for the normalize_confidence function."""

    def test_basic_normalization(self):
        """Test basic normalization within range."""
        # Midpoint should give 0.5
        assert normalize_confidence(0.20, 0.15, 0.25) == pytest.approx(0.5)
        
        # Lower bound should give 0.0
        assert normalize_confidence(0.15, 0.15, 0.25) == pytest.approx(0.0)
        
        # Upper bound should give 1.0
        assert normalize_confidence(0.25, 0.15, 0.25) == pytest.approx(1.0)

    def test_clamping(self):
        """Test that values outside range are clamped."""
        # Below minimum should clamp to 0.0
        assert normalize_confidence(0.10, 0.15, 0.25) == pytest.approx(0.0)
        
        # Above maximum should clamp to 1.0
        assert normalize_confidence(0.30, 0.15, 0.25) == pytest.approx(1.0)

    def test_invalid_range(self):
        """Test behavior when range is invalid (max <= min)."""
        # max == min should return default
        assert normalize_confidence(0.20, 0.25, 0.25) == pytest.approx(0.5)
        
        # max < min should return default
        assert normalize_confidence(0.20, 0.30, 0.25) == pytest.approx(0.5)

    def test_custom_default(self):
        """Test custom default value for invalid range."""
        assert normalize_confidence(0.20, 0.25, 0.25, default=0.0) == pytest.approx(0.0)
        assert normalize_confidence(0.20, 0.25, 0.25, default=1.0) == pytest.approx(1.0)

    def test_different_ranges(self):
        """Test normalization with different min/max ranges."""
        # Range 0.2 to 0.4
        assert normalize_confidence(0.30, 0.20, 0.40) == pytest.approx(0.5)
        assert normalize_confidence(0.20, 0.20, 0.40) == pytest.approx(0.0)
        assert normalize_confidence(0.40, 0.20, 0.40) == pytest.approx(1.0)
        
        # Range 0.0 to 0.15
        assert normalize_confidence(0.075, 0.0, 0.15) == pytest.approx(0.5)
        assert normalize_confidence(0.0, 0.0, 0.15) == pytest.approx(0.0)
        assert normalize_confidence(0.15, 0.0, 0.15) == pytest.approx(1.0)
        
        # Range 0.1 to 0.2
        assert normalize_confidence(0.15, 0.10, 0.20) == pytest.approx(0.5)
        assert normalize_confidence(0.10, 0.10, 0.20) == pytest.approx(0.0)
        assert normalize_confidence(0.20, 0.10, 0.20) == pytest.approx(1.0)

    def test_edge_cases(self):
        """Test edge cases with zero and negative values."""
        # Zero range
        assert normalize_confidence(0.0, 0.0, 0.0) == pytest.approx(0.5)
        
        # Negative values
        assert normalize_confidence(-0.5, -1.0, 0.0) == pytest.approx(0.5)
        assert normalize_confidence(-1.0, -1.0, 0.0) == pytest.approx(0.0)
        assert normalize_confidence(0.0, -1.0, 0.0) == pytest.approx(1.0)

    def test_precision(self):
        """Test that the function maintains reasonable precision."""
        # Should handle small differences
        result = normalize_confidence(0.151, 0.15, 0.25)
        assert result > 0.0
        assert result < 1.0
        
        # Should handle large differences
        result = normalize_confidence(100.0, 0.0, 1000.0)
        assert result == pytest.approx(0.1)
