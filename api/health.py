"""
Health Check Service

Standalone health check service for Syngex components.
Provides comprehensive health status for all system components.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class HealthCheckService:
    """
    Health check service for Syngex components.
    
    Provides health status checks for:
    - GEX Calculator
    - Strategy Engine
    - Signal Tracker
    - TradeStation Connection
    
    Can be used independently by any service that needs health monitoring.
    """
    
    def __init__(self, base_path: Path | None = None, symbol: str | None = None):
        """
        Initialize the health check service.
        
        Args:
            base_path: Base path to the Syngex project directory.
                      Defaults to parent of this module's location.
            symbol: Trading symbol (e.g., "SPY", "TSLA").
                   Defaults to SYNGEX_SYMBOL env var or "UNKNOWN".
        """
        import os
        
        self._base_path = base_path or Path(__file__).parent.parent
        self._symbol = symbol or os.environ.get("SYNGEX_SYMBOL", "UNKNOWN").upper()
        
        # Paths to data files
        self._data_dir = self._base_path / "data"
        self._log_dir = self._base_path / "log"
        self._gex_state_file = self._data_dir / f"gex_state_{self._symbol}.json"
        self._signals_log_file = self._log_dir / f"signals_{self._symbol}.jsonl"
        
        # Track service start time for uptime calculation
        self._start_time = time.time()
    
    def check_gex_calculator(self) -> str:
        """
        Verify GEX calculator is responsive.
        
        Checks if the GEX state file exists and is readable.
        
        Returns:
            "healthy" if GEX calculator is working, "unhealthy" otherwise.
        """
        try:
            if not self._gex_state_file.exists():
                return "unhealthy"
            
            # Try to read and parse the file
            with open(self._gex_state_file, "r") as f:
                data = json.load(f)
            
            # Verify essential fields exist
            if "underlying_price" not in data:
                return "unhealthy"
            if "strikes" not in data:
                return "unhealthy"
            
            return "healthy"
        except (json.JSONDecodeError, OSError, UnicodeDecodeError, KeyError):
            return "unhealthy"
    
    def check_strategy_engine(self) -> str:
        """
        Verify strategy engine is running.
        
        Checks if strategy health data is present in the GEX state file.
        
        Returns:
            "healthy" if strategy engine is running, "unhealthy" otherwise.
        """
        try:
            if not self._gex_state_file.exists():
                return "unhealthy"
            
            with open(self._gex_state_file, "r") as f:
                data = json.load(f)
            
            # Check if strategy_health section exists and has data
            strategy_health = data.get("strategy_health", {})
            if not strategy_health:
                return "unhealthy"
            
            # Verify at least one strategy is active
            for strat_name, health in strategy_health.items():
                if health.get("status") != "error":
                    return "healthy"
            
            return "unhealthy"
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            return "unhealthy"
    
    def check_signal_tracker(self) -> str:
        """
        Verify signal tracker has data.
        
        Checks if signals are being logged.
        
        Returns:
            "healthy" if signal tracker has recent data, "unhealthy" otherwise.
        """
        try:
            if not self._signals_log_file.exists():
                # Alternative: check if GEX state has micro_signals
                if not self._gex_state_file.exists():
                    return "unhealthy"
                
                with open(self._gex_state_file, "r") as f:
                    data = json.load(f)
                
                micro_signals = data.get("micro_signals", {})
                if micro_signals:
                    return "healthy"
                
                return "unhealthy"
            
            # Check if signals file has content
            file_size = self._signals_log_file.stat().st_size
            if file_size == 0:
                return "unhealthy"
            
            # Verify it contains valid JSONL
            with open(self._signals_log_file, "r") as f:
                first_line = f.readline()
                if not first_line.strip():
                    return "unhealthy"
                
                try:
                    json.loads(first_line)
                    return "healthy"
                except json.JSONDecodeError:
                    return "unhealthy"
                    
        except OSError:
            return "unhealthy"
    
    def check_trade_station_connection(self) -> str:
        """
        Verify data feed is connected.
        
        Checks if the TradeStation data feed is providing updates.
        
        Returns:
            "connected" if data feed is active, "disconnected" otherwise.
        """
        try:
            if not self._gex_state_file.exists():
                return "disconnected"
            
            with open(self._gex_state_file, "r") as f:
                data = json.load(f)
            
            # Check if underlying_price is being updated (not zero or None)
            underlying_price = data.get("underlying_price")
            if underlying_price is None or underlying_price == 0:
                return "disconnected"
            
            # Check if last_updated timestamp is recent (within last 5 minutes)
            last_updated = data.get("last_updated", "")
            if last_updated:
                try:
                    # Parse ISO format timestamp
                    last_update_time = datetime.fromisoformat(
                        last_updated.replace("Z", "+00:00")
                    )
                    now = datetime.now(timezone.utc)
                    time_diff = (now - last_update_time).total_seconds()
                    
                    # If update is older than 5 minutes, consider disconnected
                    if time_diff > 300:
                        return "disconnected"
                except (ValueError, TypeError):
                    # Can't parse timestamp, but data exists
                    pass
            
            return "connected"
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            return "disconnected"
    
    def _get_signals_last_minute(self) -> int:
        """
        Count signals generated in the last minute.
        
        Returns:
            Number of signals in the last 60 seconds.
        """
        try:
            if not self._signals_log_file.exists():
                return 0
            
            now = time.time()
            count = 0
            
            # Read last few lines (most recent signals)
            with open(self._signals_log_file, "r") as f:
                # Read from end - get last 100 lines
                lines = f.readlines()[-100:]
                
                for line in reversed(lines):
                    if not line.strip():
                        continue
                    
                    try:
                        entry = json.loads(line)
                        timestamp = entry.get("timestamp", 0)
                        
                        if now - timestamp <= 60:
                            count += 1
                        elif now - timestamp > 60:
                            # Old enough to stop counting
                            break
                    except json.JSONDecodeError:
                        continue
            
            return count
        except OSError:
            return 0
    
    def _get_active_strategies(self) -> int:
        """
        Count active strategies (those with signals in last 15 minutes).
        
        Returns:
            Number of active strategies.
        """
        try:
            if not self._gex_state_file.exists():
                return 0
            
            with open(self._gex_state_file, "r") as f:
                data = json.load(f)
            
            strategy_health = data.get("strategy_health", {})
            now = time.time()
            active_count = 0
            
            for strat_name, health in strategy_health.items():
                last_ts = health.get("last_signal_ts", 0)
                if last_ts > 0 and now - last_ts <= 900:  # 15 minutes
                    active_count += 1
            
            return active_count
        except (json.JSONDecodeError, OSError):
            return 0
    
    def _get_last_signal_timestamp(self) -> float | None:
        """
        Get the timestamp of the most recent signal.
        
        Returns:
            Unix timestamp of last signal, or None if no signals.
        """
        try:
            if not self._signals_log_file.exists():
                return None
            
            with open(self._signals_log_file, "r") as f:
                lines = f.readlines()
                if not lines:
                    return None
                
                # Get last non-empty line
                for line in reversed(lines):
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            return entry.get("timestamp")
                        except json.JSONDecodeError:
                            continue
            
            return None
        except OSError:
            return None
    
    def get_full_status(self) -> Dict[str, Any]:
        """
        Return complete health status JSON.
        
        Checks all components and returns comprehensive status.
        
        Returns:
            Dictionary with status, timestamp, components, and metrics.
        """
        # Check all components
        gex_status = self.check_gex_calculator()
        strategy_status = self.check_strategy_engine()
        signal_status = self.check_signal_tracker()
        ts_status = self.check_trade_station_connection()
        
        # Build components dict
        components = {
            "gex_calculator": gex_status,
            "strategy_engine": strategy_status,
            "signal_tracker": signal_status,
            "trade_station": ts_status
        }
        
        # Calculate metrics
        uptime_seconds = int(time.time() - self._start_time)
        signals_last_minute = self._get_signals_last_minute()
        active_strategies = self._get_active_strategies()
        last_signal_ts = self._get_last_signal_timestamp()
        
        metrics = {
            "uptime_seconds": uptime_seconds,
            "signals_last_minute": signals_last_minute,
            "active_strategies": active_strategies,
            "last_signal_timestamp": last_signal_ts
        }
        
        # Determine overall status
        # healthy: all components OK
        # degraded: some non-critical issues
        # unhealthy: critical component failed
        
        critical_failures = (
            gex_status == "unhealthy" or
            ts_status == "disconnected"
        )
        
        non_critical_failures = (
            strategy_status == "unhealthy" or
            signal_status == "unhealthy"
        )
        
        if critical_failures:
            overall_status = "unhealthy"
        elif non_critical_failures:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "components": components,
            "metrics": metrics
        }
    
    def get_short_status(self) -> Dict[str, str]:
        """
        Return a brief status summary.
        
        Returns:
            Simple dictionary with overall status and component states.
        """
        full_status = self.get_full_status()
        
        return {
            "status": full_status["status"],
            "gex_calculator": full_status["components"]["gex_calculator"],
            "strategy_engine": full_status["components"]["strategy_engine"],
            "signal_tracker": full_status["components"]["signal_tracker"],
            "trade_station": full_status["components"]["trade_station"]
        }
