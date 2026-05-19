"""
tests/unit/test_services/test_dashboard_service.py

Unit tests for DashboardService.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from services.dashboard_service import DashboardService


class TestDashboardService:
    """Tests for DashboardService."""

    def test_create_service(self):
        """Test service creation."""
        mock_orch = MagicMock()
        mock_orch._logger = MagicMock()
        mock_orch._correlation_id = "test123"

        service = DashboardService(
            symbol="TSLA",
            port=8501,
            data_dir=Path("/tmp/test"),
            orchestrator_ref=mock_orch,
        )

        assert service.symbol == "TSLA"
        assert service._port == 8501
        assert service._process is None

    def test_start_when_already_running(self):
        """Test start() when already running."""
        mock_orch = MagicMock()
        mock_orch._logger = MagicMock()
        mock_orch._correlation_id = "test123"

        service = DashboardService(
            symbol="TSLA",
            port=8501,
            data_dir=Path("/tmp/test"),
            orchestrator_ref=mock_orch,
        )
        service._process = MagicMock()  # Simulate running

        service.start()  # Should not start again

        assert service._process is not None

    @patch('subprocess.Popen')
    def test_start_spawns_process(self, mock_popen):
        """Test start() spawns subprocess."""
        mock_orch = MagicMock()
        mock_orch._logger = MagicMock()
        mock_orch._correlation_id = "test123"

        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        service = DashboardService(
            symbol="TSLA",
            port=8501,
            data_dir=Path("/tmp/test"),
            orchestrator_ref=mock_orch,
        )

        service.start()

        mock_popen.assert_called_once()
        assert service._process is not None

    @patch('subprocess.Popen')
    def test_start_handles_streamlit_not_found(self, mock_popen):
        """Test start() handles Streamlit not found."""
        mock_orch = MagicMock()
        mock_orch._logger = MagicMock()
        mock_orch._correlation_id = "test123"

        mock_popen.side_effect = FileNotFoundError("streamlit not found")

        service = DashboardService(
            symbol="TSLA",
            port=8501,
            data_dir=Path("/tmp/test"),
            orchestrator_ref=mock_orch,
        )

        # Should not raise
        service.start()

        # Process should still be None
        assert service._process is None

    def test_stop_when_not_running(self):
        """Test stop() when not running."""
        mock_orch = MagicMock()
        mock_orch._logger = MagicMock()
        mock_orch._correlation_id = "test123"

        service = DashboardService(
            symbol="TSLA",
            port=8501,
            data_dir=Path("/tmp/test"),
            orchestrator_ref=mock_orch,
        )
        service._process = None

        service.stop()  # Should not raise

    def test_stop_terminates_process(self):
        """Test stop() terminates process."""
        mock_orch = MagicMock()
        mock_orch._logger = MagicMock()
        mock_orch._correlation_id = "test123"

        mock_process = MagicMock()
        mock_process.pid = 12345

        service = DashboardService(
            symbol="TSLA",
            port=8501,
            data_dir=Path("/tmp/test"),
            orchestrator_ref=mock_orch,
        )
        service._process = mock_process

        service.stop()

        mock_process.terminate.assert_called_once()
        assert service._process is None
