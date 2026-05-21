"""
Telemetry emitter for strategy metrics.

Usage:
    from telemetry import TelemetryEmitter, TelemetryLine

    calculations = [
        TelemetryLine(name="rsi", value=65.4, confidence=0.95),
        TelemetryLine(name="macd_signal", value=1.23, confidence=0.88),
    ]
    await TelemetryEmitter.emit("my_strategy", calculations)
"""

from dataclasses import dataclass
from typing import List, Any
import time
import httpx


@dataclass
class TelemetryLine:
    """A single telemetry data point with confidence scoring."""
    name: str
    value: Any
    confidence: float  # 0.0 to 1.0


class TelemetryEmitter:
    """Async telemetry emitter for strategy calculations."""
    
    DASHBOARD_URL = "http://localhost:8000/metrics"
    
    @classmethod
    async def emit(cls, strategy_name: str, calculations: List[TelemetryLine]) -> None:
        """
        Emit telemetry data to the dashboard.
        
        Args:
            strategy_name: Name of the trading strategy
            calculations: List of TelemetryLine objects to emit
            
        Note:
            Fails silently on errors to avoid slowing down strategy execution.
        """
        payload = {
            "strategy": strategy_name,
            "timestamp": time.time(),
            "lines": [
                {
                    "name": line.name,
                    "value": str(line.value),
                    "confidence": line.confidence
                }
                for line in calculations
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                await client.post(cls.DASHBOARD_URL, json=payload)
        except Exception:
            # Silent fail - don't let telemetry issues slow down the strategy
            pass
