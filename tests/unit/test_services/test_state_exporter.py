"""
tests/unit/test_services/test_state_exporter.py

Unit tests for StateExporter.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from services.state_exporter import StateExporter


class TestStateExporter:
    """Tests for StateExporter."""

    def test_create_exporter(self):
        """Test exporter creation."""
        mock_calc = MagicMock()
        mock_engine = MagicMock()
        mock_tracker = MagicMock()
        mock_filter = MagicMock()
        mock_logger = MagicMock()

        exporter = StateExporter(
            data_dir=Path("/tmp/test"),
            calculator_ref=mock_calc,
            strategy_engine_ref=mock_engine,
            signal_tracker_ref=mock_tracker,
            gamma_filter_ref=mock_filter,
            symbol="TSLA",
            logger=mock_logger,
            correlation_id="test123",
        )

        assert exporter._data_dir == Path("/tmp/test")
        assert exporter._symbol == "TSLA"

    @patch('pathlib.Path.write_text')
    def test_export_writes_file(self, mock_write):
        """Test export() writes JSON file."""
        mock_calc = MagicMock()
        mock_calc.get_summary.return_value = {"underlying_price": 195.50}

        mock_engine = MagicMock()
        mock_tracker = MagicMock()
        mock_filter = MagicMock()
        mock_logger = MagicMock()

        exporter = StateExporter(
            data_dir=Path("/tmp/test"),
            calculator_ref=mock_calc,
            strategy_engine_ref=mock_engine,
            signal_tracker_ref=mock_tracker,
            gamma_filter_ref=mock_filter,
            symbol="TSLA",
            logger=mock_logger,
            correlation_id="test123",
        )

        exporter.export()

        mock_write.assert_called_once()

    @patch('pathlib.Path.write_text')
    def test_export_creates_directory(self, mock_write):
        """Test export() creates data directory if needed."""
        mock_calc = MagicMock()
        mock_engine = MagicMock()
        mock_tracker = MagicMock()
        mock_filter = MagicMock()
        mock_logger = MagicMock()

        # Non-existent directory
        exporter = StateExporter(
            data_dir=Path("/tmp/test_nonexistent/subdir"),
            calculator_ref=mock_calc,
            strategy_engine_ref=mock_engine,
            signal_tracker_ref=mock_tracker,
            gamma_filter_ref=mock_filter,
            symbol="TSLA",
            logger=mock_logger,
            correlation_id="test123",
        )

        # Should create directory and not raise
        exporter.export()

    def test_export_with_none_calculator(self):
        """Test export() when calculator is None."""
        mock_engine = MagicMock()
        mock_tracker = MagicMock()
        mock_filter = MagicMock()
        mock_logger = MagicMock()

        exporter = StateExporter(
            data_dir=Path("/tmp/test"),
            calculator_ref=None,
            strategy_engine_ref=mock_engine,
            signal_tracker_ref=mock_tracker,
            gamma_filter_ref=mock_filter,
            symbol="TSLA",
            logger=mock_logger,
            correlation_id="test123",
        )

        # Should handle gracefully
        exporter.export()
