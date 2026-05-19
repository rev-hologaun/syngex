"""
config/logging_config.py — Structured JSON Logging Configuration

Provides production-ready structured logging with:
- JSON format for production monitoring
- Text format for development
- Correlation IDs for tracing signal lifecycles
- Proper log levels (ERROR for actual errors, not DEBUG)

Usage:
    # In main.py or other entry points:
    from config.logging_config import setup_logging, log_with_correlation
    
    # Setup at startup
    logger = setup_logging(log_level="INFO", json_format=False)  # dev mode
    
    # Log with correlation ID
    log_with_correlation(logger, logging.INFO, "Signal created", 
                        correlation_id=signal_id, signal_type="LONG")
"""

from __future__ import annotations

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Structured JSON formatter for production logging.
    
    Output format:
    {
        "timestamp": "2026-05-19T07:43:00.123456Z",
        "level": "INFO",
        "logger": "Syngex.StrategyEngine",
        "message": "Signal created",
        "module": "engine",
        "function": "process",
        "line": 123,
        "correlation_id": "abc-123",  # optional
        "signal_id": "signal-456",     # optional
        "extra_field": "value",        # any extra fields
        "exception": "..."             # if exception occurred
    }
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation ID if present
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        
        # Add signal ID if present
        if hasattr(record, "signal_id"):
            log_entry["signal_id"] = record.signal_id
        
        # Add any extra fields that were set on the record
        extra_fields = ["correlation_id", "signal_id", "strategy_id", "strike", 
                       "symbol", "direction", "confidence", "signal_type"]
        for field in extra_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO", json_format: bool = False) -> logging.Logger:
    """Configure the root logger with structured logging.
    
    Args:
        log_level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        json_format: If True, use JSON format (production). If False, use text format (development).
    
    Returns:
        Configured root logger
    
    Example:
        # Development mode (human-readable)
        logger = setup_logging(log_level="DEBUG", json_format=False)
        
        # Production mode (structured JSON)
        logger = setup_logging(log_level="INFO", json_format=True)
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))
    
    # Set formatter based on mode
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%H:%M:%S"
            )
        )
    
    root_logger.addHandler(handler)
    
    # Suppress noisy loggers
    noisy_loggers = {
        "aiohttp": logging.WARNING,
        "httpx": logging.WARNING,
        "asyncio": logging.WARNING,
        "websockets": logging.WARNING,
    }
    for name, level in noisy_loggers.items():
        logging.getLogger(name).setLevel(level)
    
    return root_logger


def log_with_correlation(
    logger: logging.Logger,
    level: int,
    message: str,
    *args: Any,
    correlation_id: Optional[str] = None,
    signal_id: Optional[str] = None,
    exc_info: Optional[bool] = False,
    **extra: Any
) -> None:
    """Log a message with optional correlation ID and extra fields.
    
    This is a helper function for structured logging with context.
    
    Args:
        logger: The logger to use
        level: Log level (logging.INFO, logging.ERROR, etc.)
        message: The log message (can use % formatting)
        *args: Arguments for message formatting (e.g., "Error: %s" % arg)
        correlation_id: Optional correlation ID for tracing (e.g., signal lifecycle)
        signal_id: Optional signal ID for signal-specific tracking
        exc_info: If True, include exception information (traceback) in the log
        **extra: Additional fields to include in the log entry
    
    Example:
        log_with_correlation(
            logger,
            logging.INFO,
            "Signal created",
            correlation_id="abc-123",
            signal_id="sig-456",
            strategy_id="gamma_wall_bounce",
            direction="LONG",
            confidence=0.75
        )
        
        # With message formatting:
        log_with_correlation(
            logger,
            logging.ERROR,
            "Strategy %s error: %s",
            strategy_id,
            str(exc),
            correlation_id="abc-123",
            exc_info=True
        )
    """
    # Get exception info if requested
    exc_info_tuple = None
    if exc_info:
        import sys
        exc_info_tuple = sys.exc_info()
    
    # Build the log record with extra attributes
    # Pass args for message formatting, exc_info_tuple for exception info
    log_record = logger.makeRecord(
        logger.name,
        level,
        "",
        0,
        message,
        args if args else (),
        exc_info_tuple
    )
    
    # Add correlation ID if present
    if correlation_id:
        log_record.correlation_id = correlation_id
    
    # Add signal ID if present
    if signal_id:
        log_record.signal_id = signal_id
    
    # Add any extra fields
    for key, value in extra.items():
        setattr(log_record, key, value)
    
    # Handle the record (this triggers formatting and output)
    logger.handle(log_record)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger (convenience wrapper).
    
    Args:
        name: Logger name (e.g., "Syngex.StrategyEngine")
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
