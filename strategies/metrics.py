"""
Simple metrics collector for strategy debugging.
Quick-track implementation - minimal, no persistence.
"""

import time
from typing import Any, Dict, List, Callable

class MetricsCollector:
    """In-memory metrics storage with pub/sub."""
    
    def __init__(self):
        self.latest: Dict[str, Dict[str, Any]] = {}
        self.history: Dict[str, List[Dict]] = {}
        self.subscribers: List[Callable] = []
        self.max_history = 600  # 10 minutes at 60 samples/minute
    
    def publish(self, strategy_id: str, metrics: Dict[str, Any]):
        """Publish metrics from a strategy."""
        point = {
            'timestamp': time.time(),
            'metrics': metrics
        }
        self.latest[strategy_id] = metrics
        
        if strategy_id not in self.history:
            self.history[strategy_id] = []
        
        self.history[strategy_id].append(point)
        
        # Trim history
        if len(self.history[strategy_id]) > self.max_history:
            self.history[strategy_id] = self.history[strategy_id][-self.max_history:]
        
        # Notify subscribers
        for callback in self.subscribers:
            try:
                callback(strategy_id, metrics)
            except Exception:
                pass
    
    def get_latest(self, strategy_id: str) -> Dict[str, Any]:
        """Get latest metrics for a strategy."""
        return self.latest.get(strategy_id, {})
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all latest metrics."""
        return self.latest.copy()
    
    def get_history(self, strategy_id: str, limit: int = 60) -> List[Dict]:
        """Get recent history for a strategy."""
        history = self.history.get(strategy_id, [])
        return history[-limit:]
    
    def subscribe(self, callback: Callable):
        """Register a subscriber callback."""
        self.subscribers.append(callback)

# Singleton instance
collector = MetricsCollector()
