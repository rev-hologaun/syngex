# Structured JSON Logging for Production Monitoring

## Overview

This logging system provides structured JSON output for production monitoring with correlation IDs for tracing signal lifecycles.

## Configuration

### Enable JSON Logging

**Option 1: Command Line Flag**
```bash
python3 main.py TSLA --json-log
```

**Option 2: Environment Variable**
```bash
export SYNGEX_JSON_LOG=true
python3 main.py TSLA
```

**Option 3: Programmatically**
```python
from config.logging_config import setup_logging

# Production mode (JSON)
logger = setup_logging(log_level="INFO", json_format=True)

# Development mode (text)
logger = setup_logging(log_level="DEBUG", json_format=False)
```

## Log Levels

The system uses standard Python log levels:

- **CRITICAL**: Pipeline failures, unrecoverable errors
- **ERROR**: Error conditions (option chain failures, config errors)
- **WARNING**: Non-critical issues (missing config files, startup warnings)
- **INFO**: Normal operation (signals, lifecycle events, config reloads)
- **DEBUG**: Detailed debugging (strike inference, OI updates)

**Important**: Errors are now logged at ERROR level, not DEBUG, making them visible in production without verbose logging.

## Log Format

### Production (JSON)

```json
{
  "timestamp": "2026-05-19T07:43:00.123456Z",
  "level": "INFO",
  "logger": "Syngex.StrategyEngine",
  "message": "Signal created",
  "module": "engine",
  "function": "process",
  "line": 123,
  "correlation_id": "abc12345",
  "signal_id": "sig-456",
  "strategy_id": "gamma_wall_bounce",
  "direction": "LONG",
  "confidence": 0.75
}
```

### Development (Text)

```
07:43:00 [INFO] Syngex.StrategyEngine: Signal created
```

## Correlation IDs

Each component (orchestrator, strategy engine, GEX calculator) generates a unique correlation ID on startup. This ID is included in all logs from that component, enabling:

- **Signal Lifecycle Tracing**: Follow a signal from creation through resolution
- **Component Correlation**: Link related events across different modules
- **Debugging**: Trace issues across the entire pipeline

Example correlation flow:
1. Orchestrator creates signal with `correlation_id="abc12345"`
2. StrategyEngine logs processing with same `correlation_id`
3. SignalTracker logs resolution with same `correlation_id`

Query all logs for a correlation ID:
```bash
grep "abc12345" logs/*.log
```

## Key Features

### 1. Structured Output

JSON format enables:
- Easy parsing by log aggregators (ELK, Datadog, Splunk)
- Field-based filtering and querying
- Automatic metric extraction

### 2. Error Level Correction

Previously, many errors were logged at DEBUG level ("zero-noise design"). Now:
- Actual errors → ERROR level
- Warnings → WARNING level
- Normal operation → INFO level
- Debug details → DEBUG level

### 3. Context-Rich Logs

Each log entry includes:
- Timestamp (UTC ISO format)
- Log level
- Logger name
- Module, function, line number
- Correlation ID (if applicable)
- Custom fields (signal_id, strategy_id, symbol, etc.)

## Usage Examples

### Logging a Signal

```python
from config.logging_config import log_with_correlation
import logging

log_with_correlation(
    logger, logging.INFO,
    "Signal created",
    correlation_id=signal_id,
    strategy_id="gamma_wall_bounce",
    direction="LONG",
    confidence=0.75,
    entry=250.50,
    target=260.00
)
```

### Logging with Extra Context

```python
log_with_correlation(
    logger, logging.WARNING,
    "Config file not found, using defaults",
    correlation_id=self._correlation_id,
    config_path="/path/to/config.yaml"
)
```

### Error Logging

```python
try:
    # Some operation
    pass
except Exception as exc:
    log_with_correlation(
        logger, logging.ERROR,
        "Operation failed",
        correlation_id=self._correlation_id,
        error=str(exc)
    )
```

## Components Updated

1. **config/logging_config.py** - Core logging configuration
2. **main.py** - Orchestrator with correlation IDs
3. **strategies/engine.py** - Strategy engine with structured logging
4. **engine/gex_calculator.py** - GEX calculator with error logging

## Testing

### Development Mode
```bash
python3 main.py TSLA
# Output: Human-readable text format
```

### Production Mode
```bash
python3 main.py TSLA --json-log
# Output: Structured JSON format
```

### Verify JSON Output
```bash
python3 main.py TSLA --json-log 2>&1 | head -5 | jq .
```

## Migration Notes

- **Backward Compatible**: Text format still available for development
- **No Breaking Changes**: All existing log messages preserved
- **Enhanced Visibility**: Errors now visible at ERROR level instead of DEBUG

## Future Enhancements

- [ ] Log rotation configuration
- [ ] File output option
- [ ] Log sampling for high-volume events
- [ ] Distributed tracing integration
