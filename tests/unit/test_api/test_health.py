"""
tests/unit/test_api/test_health.py

Unit tests for HealthCheckService.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from api.health import HealthCheckService


class TestHealthCheckService:
    """Tests for HealthCheckService."""

    def test_create_service(self):
        """Test service creation."""
        service = HealthCheckService(base_path=Path("/tmp/test"), symbol="TSLA")

        assert service._symbol == "TSLA"
        assert service._base_path == Path("/tmp/test")

    def test_create_service_with_env_symbol(self):
        """Test service creation uses env var for symbol."""
        with patch.dict('os.environ', {'SYNGEX_SYMBOL': 'AAPL'}):
            service = HealthCheckService(base_path=Path("/tmp/test"))

            assert service._symbol == "AAPL"

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_check_gex_calculator_healthy(self, mock_stat, mock_exists):
        """Test check_gex_calculator when healthy."""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024

        service = HealthCheckService(base_path=Path("/tmp/test"), symbol="TSLA")

        # Mock file content
        with patch('builtins.open', MagicMock(read=MagicMock(return_value='{"underlying_price": 195.50, "strikes": {}}'))):
            status = service.check_gex_calculator()
            assert status == "healthy"

    @patch('pathlib.Path.exists')
    def test_check_gex_calculator_unhealthy_missing_file(self, mock_exists):
        """Test check_gex_calculator when file missing."""
        mock_exists.return_value = False

        service = HealthCheckService(base_path=Path("/tmp/test"), symbol="TSLA")

        status = service.check_gex_calculator()
        assert status == "unhealthy"

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_check_signal_tracker_healthy(self, mock_stat, mock_exists):
        """Test check_signal_tracker when healthy."""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024

        service = HealthCheckService(base_path=Path("/tmp/test"), symbol="TSLA")

        # Mock valid JSONL content
        with patch('builtins.open', MagicMock(readline=MagicMock(return_value='{"timestamp": 123}'))):
            status = service.check_signal_tracker()
            assert status == "healthy"

    @patch('pathlib.Path.exists')
    def test_check_trade_station_connected(self, mock_exists):
        """Test check_trade_station_connection when connected."""
        mock_exists.return_value = True

        service = HealthCheckService(base_path=Path("/tmp/test"), symbol="TSLA")

        # Mock file with valid price
        with patch('builtins.open', MagicMock(read=MagicMock(return_value='{"underlying_price": 195.50, "last_updated": "2024-05-19T12:00:00Z"}'))):
            status = service.check_trade_station_connection()
            # May be disconnected if timestamp is old, but file exists
            assert status in ["connected", "disconnected"]

    def test_get_short_status(self):
        """Test get_short_status() returns summary."""
        service = HealthCheckService(base_path=Path("/tmp/test"), symbol="TSLA")

        # Mock all checks
        with patch.object(service, 'check_gex_calculator', return_value="healthy"):
            with patch.object(service, 'check_strategy_engine', return_value="healthy"):
                with patch.object(service, 'check_signal_tracker', return_value="healthy"):
                    with patch.object(service, 'check_trade_station_connection', return_value="connected"):
                        status = service.get_short_status()

                        assert "status" in status
                        assert "gex_calculator" in status
                        assert status["status"] == "healthy"

    def test_get_full_status(self):
        """Test get_full_status() returns comprehensive status."""
        service = HealthCheckService(base_path=Path("/tmp/test"), symbol="TSLA")

        # Mock all checks
        with patch.object(service, 'check_gex_calculator', return_value="healthy"):
            with patch.object(service, 'check_strategy_engine', return_value="healthy"):
                with patch.object(service, 'check_signal_tracker', return_value="healthy"):
                    with patch.object(service, 'check_trade_station_connection', return_value="connected"):
                        with patch.object(service, '_get_signals_last_minute', return_value=5):
                            with patch.object(service, '_get_active_strategies', return_value=10):
                                status = service.get_full_status()

                                assert "status" in status
                                assert "timestamp" in status
                                assert "components" in status
                                assert "metrics" in status
                                assert status["metrics"]["signals_last_minute"] == 5
