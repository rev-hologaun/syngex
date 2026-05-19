# Config Directory

This directory contains configuration files for Project Syngex.

## Files

### `logging_config.py`
Structured JSON logging configuration for production monitoring.

**Features:**
- JSON format for production (machine-readable logs)
- Text format for development (human-readable)
- Correlation IDs for tracing signal lifecycles
- Proper log levels (ERROR for actual errors, not DEBUG)

**Usage:**
```python
from config.logging_config import setup_logging, log_with_correlation
import logging

# Setup at startup
logger = setup_logging(log_level="INFO", json_format=False)  # dev mode
# or
logger = setup_logging(log_level="INFO", json_format=True)   # production

# Log with correlation ID
log_with_correlation(
    logger, logging.INFO,
    "Signal created",
    correlation_id="abc-123",
    strategy_id="gamma_wall_bounce",
    direction="LONG",
    confidence=0.75
)
```

**Configuration:**
- CLI flag: `--json-log` enables JSON format
- Environment variable: `SYNGEX_JSON_LOG=1` enables JSON format

See `LOGGING.md` for detailed documentation.

### `strategies.yaml`
Strategy configuration file (see strategies documentation).

### `parameters.py`
Global parameters and constants.
