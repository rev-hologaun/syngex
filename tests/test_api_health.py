"""
Tests for the API layer health check service.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.health import HealthCheckService


class TestHealthCheckService:
    """Test suite for HealthCheckService."""
    
    @pytest.fixture
    def temp_syngex_dir(self, tmp_path):
        """Create a temporary Syngex directory structure."""
        # Create data and log directories
        data_dir = tmp_path / "data"
        log_dir = tmp_path / "log"
        data_dir.mkdir()
        log_dir.mkdir()
        
        return tmp_path
    
    @pytest.fixture
    def health_service(self, temp_syngex_dir):
        """Create a HealthCheckService instance with temp directory."""
        return HealthCheckService(base_path=temp_syngex_dir, symbol="SPY")
    
    def test_initialization(self, temp_syngex_dir):
        """Test service initialization."""
        service = HealthCheckService(base_path=temp_syngex_dir, symbol="SPY")
        
        assert service._symbol == "SPY"
        assert service._base_path == temp_syngex_dir
        assert service._gex_state_file == temp_syngex_dir / "data" / "gex_state_SPY.json"
        assert service._signals_log_file == temp_syngex_dir / "log" / "signals_SPY.jsonl"
    
    def test_check_gex_calculator_unhealthy_no_file(self, health_service):
        """Test GEX calculator check when file doesn't exist."""
        status = health_service.check_gex_calculator()
        assert status == "unhealthy"
    
    def test_check_gex_calculator_healthy(self, health_service, temp_syngex_dir):
        """Test GEX calculator check with valid data file."""
        # Create valid GEX state file
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {
                "440": {"net_gamma": 1000, "call_gamma_oi": 500, "put_gamma_oi": 500},
                "450": {"net_gamma": 2000, "call_gamma_oi": 1000, "put_gamma_oi": 1000}
            }
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.check_gex_calculator()
        assert status == "healthy"
    
    def test_check_gex_calculator_unhealthy_missing_fields(self, health_service, temp_syngex_dir):
        """Test GEX calculator check with missing required fields."""
        # Create invalid GEX state file
        gex_data = {
            "symbol": "SPY"
            # Missing underlying_price and strikes
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.check_gex_calculator()
        assert status == "unhealthy"
    
    def test_check_strategy_engine_unhealthy_no_file(self, health_service):
        """Test strategy engine check when file doesn't exist."""
        status = health_service.check_strategy_engine()
        assert status == "unhealthy"
    
    def test_check_strategy_engine_healthy(self, health_service, temp_syngex_dir):
        """Test strategy engine check with active strategies."""
        # Create GEX state with strategy health
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {"440": {"net_gamma": 1000}},
            "strategy_health": {
                "gamma_flip": {
                    "status": "active",
                    "last_signal_ts": time.time(),
                    "signal_count": 10
                }
            }
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.check_strategy_engine()
        assert status == "healthy"
    
    def test_check_strategy_engine_unhealthy_error_state(self, health_service, temp_syngex_dir):
        """Test strategy engine check with all strategies in error."""
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {"440": {"net_gamma": 1000}},
            "strategy_health": {
                "gamma_flip": {"status": "error"}
            }
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.check_strategy_engine()
        assert status == "unhealthy"
    
    def test_check_signal_tracker_unhealthy_no_file(self, health_service):
        """Test signal tracker check when no files exist."""
        status = health_service.check_signal_tracker()
        assert status == "unhealthy"
    
    def test_check_signal_tracker_healthy_from_log(self, health_service, temp_syngex_dir):
        """Test signal tracker check with valid signal log."""
        # Create signal log
        log_file = temp_syngex_dir / "log" / "signals_SPY.jsonl"
        with open(log_file, "w") as f:
            f.write(json.dumps({"timestamp": time.time(), "strategy_id": "test"}) + "\n")
        
        status = health_service.check_signal_tracker()
        assert status == "healthy"
    
    def test_check_signal_tracker_healthy_from_micro_signals(self, health_service, temp_syngex_dir):
        """Test signal tracker check with micro_signals in GEX state."""
        # Create GEX state with micro_signals
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {"440": {"net_gamma": 1000}},
            "micro_signals": {"test_signal": {"timestamp": time.time()}}
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.check_signal_tracker()
        assert status == "healthy"
    
    def test_check_trade_station_connection_disconnected_no_file(self, health_service):
        """Test TradeStation connection check when file doesn't exist."""
        status = health_service.check_trade_station_connection()
        assert status == "disconnected"
    
    def test_check_trade_station_connection_disconnected_zero_price(self, health_service, temp_syngex_dir):
        """Test TradeStation connection check with zero price."""
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 0,
            "strikes": {"440": {"net_gamma": 1000}}
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.check_trade_station_connection()
        assert status == "disconnected"
    
    def test_check_trade_station_connection_connected(self, health_service, temp_syngex_dir):
        """Test TradeStation connection check with valid data."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {"440": {"net_gamma": 1000}},
            "last_updated": now
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.check_trade_station_connection()
        assert status == "connected"
    
    def test_get_full_status_structure(self, health_service, temp_syngex_dir):
        """Test full status returns correct structure."""
        # Create minimal valid data
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {"440": {"net_gamma": 1000}},
            "strategy_health": {
                "gamma_flip": {"status": "active", "last_signal_ts": time.time()}
            },
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.get_full_status()
        
        # Verify structure
        assert "status" in status
        assert "timestamp" in status
        assert "components" in status
        assert "metrics" in status
        
        # Verify status value
        assert status["status"] in ["healthy", "unhealthy", "degraded"]
        
        # Verify timestamp format (ISO 8601)
        assert "T" in status["timestamp"]
        assert status["timestamp"].endswith("Z")
        
        # Verify components
        assert "gex_calculator" in status["components"]
        assert "strategy_engine" in status["components"]
        assert "signal_tracker" in status["components"]
        assert "trade_station" in status["components"]
        
        # Verify metrics
        assert "uptime_seconds" in status["metrics"]
        assert "signals_last_minute" in status["metrics"]
        assert "active_strategies" in status["metrics"]
    
    def test_get_full_status_healthy_all_components(self, health_service, temp_syngex_dir):
        """Test full status returns healthy when all components are OK."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {"440": {"net_gamma": 1000}},
            "strategy_health": {
                "gamma_flip": {"status": "active", "last_signal_ts": time.time()}
            },
            "micro_signals": {"test": {"timestamp": time.time()}},
            "last_updated": now
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        # Create signal log
        log_file = temp_syngex_dir / "log" / "signals_SPY.jsonl"
        with open(log_file, "w") as f:
            f.write(json.dumps({"timestamp": time.time()}) + "\n")
        
        status = health_service.get_full_status()
        
        assert status["status"] == "healthy"
        assert status["components"]["gex_calculator"] == "healthy"
        assert status["components"]["strategy_engine"] == "healthy"
        assert status["components"]["signal_tracker"] == "healthy"
        assert status["components"]["trade_station"] == "connected"
    
    def test_get_full_status_unhealthy_critical_failure(self, health_service, temp_syngex_dir):
        """Test full status returns unhealthy when critical component fails."""
        # Create GEX state with zero price (critical failure)
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 0,  # Critical: no price data
            "strikes": {}
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.get_full_status()
        
        assert status["status"] == "unhealthy"
        assert status["components"]["trade_station"] == "disconnected"
    
    def test_get_full_status_degraded_non_critical_failure(self, health_service, temp_syngex_dir):
        """Test full status returns degraded when non-critical component fails."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {"440": {"net_gamma": 1000}},
            "strategy_health": {
                "gamma_flip": {"status": "error"}  # Non-critical: strategy error
            },
            "last_updated": now
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        status = health_service.get_full_status()
        
        assert status["status"] == "degraded"
        assert status["components"]["strategy_engine"] == "unhealthy"
        assert status["components"]["trade_station"] == "connected"
    
    def test_get_short_status(self, health_service, temp_syngex_dir):
        """Test short status returns simplified view."""
        # Create minimal valid data
        gex_data = {
            "symbol": "SPY",
            "underlying_price": 450.25,
            "strikes": {"440": {"net_gamma": 1000}},
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        gex_file = temp_syngex_dir / "data" / "gex_state_SPY.json"
        with open(gex_file, "w") as f:
            json.dump(gex_data, f)
        
        short_status = health_service.get_short_status()
        
        assert "status" in short_status
        assert "gex_calculator" in short_status
        assert "strategy_engine" in short_status
        assert "signal_tracker" in short_status
        assert "trade_station" in short_status
        assert "metrics" not in short_status  # Short status excludes metrics


class TestHealthResponseFormatter:
    """Test suite for HealthResponseFormatter."""
    
    def test_format_health_response(self):
        """Test formatting a health response."""
        from api.responses import HealthResponseFormatter
        
        components = {
            "gex_calculator": "healthy",
            "strategy_engine": "healthy",
            "signal_tracker": "healthy",
            "trade_station": "connected"
        }
        
        metrics = {
            "uptime_seconds": 12345,
            "signals_last_minute": 10,
            "active_strategies": 5
        }
        
        response = HealthResponseFormatter.format(
            status="healthy",
            components=components,
            metrics=metrics,
            version="1.0.0"
        )
        
        assert response["status"] == "healthy"
        assert response["components"] == components
        assert response["metrics"] == metrics
        assert response["version"] == "1.0.0"
        assert "timestamp" in response
    
    def test_to_json(self):
        """Test converting health response to JSON string."""
        from api.responses import HealthResponseFormatter
        
        components = {"gex_calculator": "healthy"}
        metrics = {"uptime_seconds": 100}
        
        json_str = HealthResponseFormatter.to_json(
            status="healthy",
            components=components,
            metrics=metrics,
            indent=2
        )
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["status"] == "healthy"
        assert "2" in json_str  # Indentation present


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
