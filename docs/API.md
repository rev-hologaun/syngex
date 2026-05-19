# Syngex API Documentation

## Overview

The Syngex API layer provides health checks and component status interfaces for monitoring the trading system. The API is designed to be lightweight, reliable, and usable by both internal components and external monitoring systems.

## Directory Structure

```
api/
├── __init__.py          # Module exports
├── health.py            # HealthCheckService class
└── responses.py         # API response formatting utilities
```

## Health Check Service

### Class: `HealthCheckService`

The `HealthCheckService` provides comprehensive health monitoring for all Syngex components.

#### Initialization

```python
from api.health import HealthCheckService
from pathlib import Path

# Default initialization (uses SYNGEX_SYMBOL env var)
health = HealthCheckService()

# Custom symbol and base path
health = HealthCheckService(
    base_path=Path("/path/to/syngex"),
    symbol="SPY"
)
```

#### Methods

##### `check_gex_calculator() -> str`

Verifies the GEX calculator is responsive.

**Returns:** `"healthy"` or `"unhealthy"`

**Checks:**
- GEX state file exists and is readable
- Contains required fields (`underlying_price`, `strikes`)

##### `check_strategy_engine() -> str`

Verifies the strategy engine is running.

**Returns:** `"healthy"` or `"unhealthy"`

**Checks:**
- Strategy health data is present
- At least one strategy is active (not in error state)

##### `check_signal_tracker() -> str`

Verifies the signal tracker has data.

**Returns:** `"healthy"` or `"unhealthy"`

**Checks:**
- Signals log file exists and contains valid JSONL
- Or GEX state contains micro_signals data

##### `check_trade_station_connection() -> str`

Verifies the TradeStation data feed is connected.

**Returns:** `"connected"` or `"disconnected"`

**Checks:**
- Underlying price is non-zero
- Last update timestamp is recent (within 5 minutes)

##### `get_full_status() -> dict`

Returns comprehensive health status for all components.

**Returns:** Dictionary with the following structure:

```json
{
  "status": "healthy|unhealthy|degraded",
  "timestamp": "2026-05-19T12:00:00Z",
  "components": {
    "gex_calculator": "healthy|unhealthy",
    "strategy_engine": "healthy|unhealthy",
    "signal_tracker": "healthy|unhealthy",
    "trade_station": "connected|disconnected"
  },
  "metrics": {
    "uptime_seconds": 12345,
    "signals_last_minute": 12,
    "active_strategies": 5,
    "last_signal_timestamp": 1715011200.0
  }
}
```

**Status Values:**
- `healthy`: All components operational
- `degraded`: Non-critical components have issues
- `unhealthy`: Critical component failed (GEX calculator or data feed)

##### `get_short_status() -> dict`

Returns a brief status summary.

**Returns:**

```json
{
  "status": "healthy",
  "gex_calculator": "healthy",
  "strategy_engine": "healthy",
  "signal_tracker": "healthy",
  "trade_station": "connected"
}
```

## API Endpoints

### `/health` - Health Check Endpoint

**Method:** `GET`

**Description:** Returns the current health status of all Syngex components.

**Response Codes:**
- `200 OK`: System is healthy or degraded (operational)
- `503 Service Unavailable`: Critical component failure

**Response Body:**

```json
{
  "status": "healthy",
  "timestamp": "2026-05-19T12:00:00Z",
  "components": {
    "gex_calculator": "healthy",
    "strategy_engine": "healthy",
    "signal_tracker": "healthy",
    "trade_station": "connected"
  },
  "metrics": {
    "uptime_seconds": 12345,
    "signals_last_minute": 12,
    "active_strategies": 5,
    "last_signal_timestamp": 1715011200.0
  }
}
```

**Example Usage:**

```bash
# Using curl
curl http://localhost:8502/health

# Pretty print
curl -s http://localhost:8502/health | jq .
```

## Response Formatting

### Class: `APIResponse`

Utility class for formatting consistent API responses.

#### Methods

##### `success(data, message=None, status_code=200)`

Creates a successful API response.

```python
from api.responses import APIResponse

return APIResponse.success(
    data={"key": "value"},
    message="Operation completed successfully",
    status_code=201
)
```

**Response Format:**

```json
{
  "success": true,
  "data": {"key": "value"},
  "message": "Operation completed successfully",
  "timestamp": "2026-05-19T12:00:00Z"
}
```

##### `error(message, status_code=400, details=None)`

Creates an error response.

```python
return APIResponse.error(
    message="Invalid request parameters",
    status_code=400,
    details={"field": "Expected integer, got string"}
)
```

**Response Format:**

```json
{
  "success": false,
  "error": {
    "message": "Invalid request parameters",
    "timestamp": "2026-05-19T12:00:00Z",
    "details": {
      "field": "Expected integer, got string"
    }
  }
}
```

##### `health_response(status, components, metrics)`

Creates a standardized health check response.

```python
return APIResponse.health_response(
    status="healthy",
    components={"gex_calculator": "healthy"},
    metrics={"uptime_seconds": 12345}
)
```

## Health Check Semantics

### Component Status Definitions

| Component | Healthy | Unhealthy/Disconnected |
|-----------|---------|----------------------|
| GEX Calculator | State file readable with valid data | File missing, corrupted, or invalid |
| Strategy Engine | Active strategies present | No strategies or all in error state |
| Signal Tracker | Valid signal log or micro_signals | No signals or invalid format |
| TradeStation | Price updates within 5 minutes | No price or stale data |

### Overall Status Logic

```
if (gex_calculator == unhealthy OR trade_station == disconnected):
    status = "unhealthy"
elif (strategy_engine == unhealthy OR signal_tracker == unhealthy):
    status = "degraded"
else:
    status = "healthy"
```

### Metrics Definitions

| Metric | Description |
|--------|-------------|
| `uptime_seconds` | Time since health service started |
| `signals_last_minute` | Count of signals in last 60 seconds |
| `active_strategies` | Strategies with signals in last 15 minutes |
| `last_signal_timestamp` | Unix timestamp of most recent signal |

## Integration Examples

### Using in Custom Monitoring

```python
from api.health import HealthCheckService
from pathlib import Path

# Initialize
health = HealthCheckService(
    base_path=Path("/home/user/syngex"),
    symbol="SPY"
)

# Check individual components
if health.check_gex_calculator() == "healthy":
    print("GEX calculator is running")

# Get full status
status = health.get_full_status()
print(f"Overall status: {status['status']}")
print(f"Signals last minute: {status['metrics']['signals_last_minute']}")

# Check for critical failures
if status['status'] == 'unhealthy':
    # Alert or take corrective action
    send_alert("Syngex system unhealthy!")
```

### Flask Integration

```python
from flask import Flask
from api.health import HealthCheckService
from pathlib import Path

app = Flask(__name__)
health_service = HealthCheckService(base_path=Path(__file__).parent)

@app.route("/health")
def health():
    status = health_service.get_full_status()
    
    if status['status'] == 'healthy':
        return jsonify(status), 200
    elif status['status'] == 'degraded':
        return jsonify(status), 200
    else:
        return jsonify(status), 503
```

## Testing

### Unit Tests

```python
import pytest
from api.health import HealthCheckService
from pathlib import Path

def test_health_service_initialization():
    health = HealthCheckService()
    assert health is not None

def test_check_gex_calculator():
    health = HealthCheckService()
    status = health.check_gex_calculator()
    assert status in ["healthy", "unhealthy"]

def test_get_full_status():
    health = HealthCheckService()
    status = health.get_full_status()
    
    assert "status" in status
    assert "timestamp" in status
    assert "components" in status
    assert "metrics" in status
    assert status["status"] in ["healthy", "unhealthy", "degraded"]
```

### Manual Testing

```bash
# Start the heatmap server
cd ~/projects/syngex
python3 app_heatmap.py

# Test health endpoint in another terminal
curl http://localhost:8502/health | jq .

# Expected output:
{
  "status": "healthy",
  "timestamp": "2026-05-19T12:00:00Z",
  "components": {
    "gex_calculator": "healthy",
    "strategy_engine": "healthy",
    "signal_tracker": "healthy",
    "trade_station": "connected"
  },
  "metrics": {
    "uptime_seconds": 12345,
    "signals_last_minute": 12,
    "active_strategies": 5,
    "last_signal_timestamp": 1715011200.0
  }
}
```

## Backward Compatibility

The new API layer maintains backward compatibility with the previous health check implementation:

- The `/health` endpoint returns the same HTTP status codes (200/503)
- Response structure is similar but more standardized
- Component names have been updated for clarity (see migration guide below)

### Component Name Migration

| Old Name | New Name |
|----------|----------|
| `orchestrator` | (removed - inferred from gex_calculator) |
| `signal_engine` | `strategy_engine` |
| `gex_calculator` | `gex_calculator` (unchanged) |
| `heatmap_server` | (removed - endpoint itself proves availability) |
| `data_feed` | `trade_station` |

## Troubleshooting

### Common Issues

**Issue:** Health check returns "unhealthy"

**Possible Causes:**
1. GEX state file not being written by orchestrator
2. Data feed disconnected from TradeStation
3. Symbol mismatch between health service and data files

**Resolution:**
```bash
# Check if data file exists
ls -la ~/projects/syngex/data/gex_state_SPY.json

# Check if orchestrator is running
ps aux | grep main.py

# Check logs
tail -f ~/projects/syngex/log/main.log
```

**Issue:** Component status is "degraded"

**Possible Causes:**
1. Strategy engine not producing signals
2. Signal tracker log is empty or corrupted

**Resolution:**
```bash
# Check strategy engine logs
tail -f ~/projects/syngex/log/strategies.log

# Check signal log
tail -20 ~/projects/syngex/log/signals_SPY.jsonl
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-19 | Initial API layer (Phase 5) |

## Future Enhancements

Planned improvements for future phases:

1. **Metrics Endpoint:** Add `/metrics` for Prometheus-style metrics
2. **Configuration Endpoint:** Add `/config` for runtime configuration
3. **Webhook Support:** Notify external systems on status changes
4. **Historical Health Data:** Track health over time
5. **Component Dependency Graph:** Show component relationships
