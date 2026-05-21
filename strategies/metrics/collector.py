"""
MetricsCollector — Thread-safe metrics storage

Provides a centralized, thread-safe store for strategy metrics
that can be exposed via Flask API to the backtest system.
"""

import threading
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional


class MetricsCollector:
    """Thread-safe metrics storage for strategy signals and data."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        # {strategy_id: [(timestamp, metrics_dict), ...]}
        self._metrics: Dict[str, List[tuple]] = defaultdict(list)
        self._max_history: int = 1000  # Keep last 1000 entries per strategy

    def publish(self, strategy_id: str, metrics: Dict[str, Any]) -> None:
        """Store metrics for a strategy.

        Args:
            strategy_id: Unique identifier for the strategy
            metrics: Dict of metric values to store
        """
        with self._lock:
            timestamp = time.time()
            entry = (timestamp, metrics)
            self._metrics[strategy_id].append(entry)

            # Trim old entries
            if len(self._metrics[strategy_id]) > self._max_history:
                self._metrics[strategy_id] = self._metrics[strategy_id][-self._max_history:]

    def get_latest(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent metrics for a strategy.

        Args:
            strategy_id: Unique identifier for the strategy

        Returns:
            Most recent metrics dict, or None if no data exists
        """
        with self._lock:
            if strategy_id not in self._metrics or not self._metrics[strategy_id]:
                return None
            return self._metrics[strategy_id][-1][1]

    def get_history(self, strategy_id: str, limit: int = 60) -> List[Dict[str, Any]]:
        """Get historical metrics for a strategy.

        Args:
            strategy_id: Unique identifier for the strategy
            limit: Maximum number of entries to return (default 60)

        Returns:
            List of {timestamp, metrics} dicts, newest first
        """
        with self._lock:
            if strategy_id not in self._metrics:
                return []

            entries = self._metrics[strategy_id][-limit:]
            return [
                {"timestamp": ts, "metrics": metrics}
                for ts, metrics in reversed(entries)
            ]

    def get_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all metrics for all strategies.

        Returns:
            Dict mapping strategy_id to list of latest metrics
        """
        with self._lock:
            result = {}
            for strategy_id, entries in self._metrics.items():
                if entries:
                    result[strategy_id] = entries[-1][1]
            return result

    def clear(self, strategy_id: Optional[str] = None) -> None:
        """Clear metrics.

        Args:
            strategy_id: If provided, clear only this strategy.
                        If None, clear all strategies.
        """
        with self._lock:
            if strategy_id:
                self._metrics[strategy_id] = []
            else:
                self._metrics.clear()


# Global singleton instance
collector = MetricsCollector()
