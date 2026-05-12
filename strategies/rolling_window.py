"""
strategies/rolling_window.py — Rolling statistics class

Supports multiple window types used by ALL strategies:
- Time-based windows (30m, 5min)
- Count-based windows (20-period, custom)
- Tracks: mean, std, min, max, percentiles, trend direction

Used by every alpha strategy for normalization and threshold detection.
"""

from __future__ import annotations

import statistics
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RollingWindow:
    """
    Rolling statistics window supporting time-based and count-based windows.

    Usage:
        # Time-based: 30-minute window
        window = RollingWindow(window_type="time", window_size=1800)

        # Count-based: 20-period window
        window = RollingWindow(window_type="count", window_size=20)

        # Push values
        window.push(195.5)
        window.push(196.2)

        # Query
        window.mean      # 195.85
        window.std       # 0.495
        window.p25       # 25th percentile
        window.trend     # "UP" / "DOWN" / "FLAT"
    """

    window_type: str = "count"       # "time" or "count"
    window_size: int = 20            # seconds for time, periods for count
    _values: deque = field(default_factory=deque)
    _timestamps: deque = field(default_factory=deque)

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def push(self, value: float, timestamp: Optional[float] = None) -> None:
        """Add a new value, evicting expired entries."""
        now = timestamp or _now()

        if self.window_type == "time":
            # Evict entries older than window_size seconds
            cutoff = now - self.window_size
            while self._timestamps and self._timestamps[0] < cutoff:
                self._values.popleft()
                self._timestamps.popleft()
        else:
            # Count-based: enforce max size
            if len(self._values) >= self.window_size:
                self._values.popleft()
                self._timestamps.popleft()

        self._values.append(value)
        self._timestamps.append(now)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def values(self) -> List[float]:
        """Current window values as a list."""
        return list(self._values)

    @property
    def count(self) -> int:
        """Number of values in the window."""
        return len(self._values)

    @property
    def mean(self) -> Optional[float]:
        """Rolling mean."""
        if not self._values:
            return None
        return statistics.mean(self._values)

    @property
    def median(self) -> Optional[float]:
        """Rolling median."""
        if not self._values:
            return None
        return statistics.median(self._values)

    @property
    def std(self) -> Optional[float]:
        """Rolling standard deviation (sample). Returns None if < 2 values."""
        if len(self._values) < 2:
            return None
        return statistics.stdev(self._values)

    @property
    def min(self) -> Optional[float]:
        if not self._values:
            return None
        return min(self._values)

    @property
    def max(self) -> Optional[float]:
        if not self._values:
            return None
        return max(self._values)

    @property
    def range(self) -> Optional[float]:
        """Current range (max - min)."""
        if not self._values:
            return None
        return self.max - self.min

    @property
    def p25(self) -> Optional[float]:
        if len(self._values) < 2:
            return None
        sorted_vals = sorted(self._values)
        n = len(sorted_vals)
        q1_idx = n / 4
        if q1_idx == int(q1_idx):
            return (sorted_vals[int(q1_idx) - 1] + sorted_vals[int(q1_idx)]) / 2
        return sorted_vals[int(q1_idx)]

    @property
    def p75(self) -> Optional[float]:
        if len(self._values) < 2:
            return None
        sorted_vals = sorted(self._values)
        n = len(sorted_vals)
        q3_idx = 3 * n / 4
        if q3_idx == int(q3_idx):
            return (sorted_vals[int(q3_idx) - 1] + sorted_vals[int(q3_idx)]) / 2
        return sorted_vals[int(q3_idx)]

    @property
    def trend(self) -> str:
        """
        Trend direction based on recent vs older half of window.

        Returns: "UP", "DOWN", or "FLAT"
        """
        if len(self._values) < 4:
            return "FLAT"

        vals = list(self._values)
        half = len(vals) // 2
        first_half = statistics.mean(vals[:half])
        second_half = statistics.mean(vals[half:])

        diff = second_half - first_half
        std = self.std
        if std is None or std == 0:
            return "FLAT"

        # Normalize by std to avoid noise
        if diff / std > 0.5:
            return "UP"
        elif diff / std < -0.5:
            return "DOWN"
        else:
            return "FLAT"

    @property
    def latest(self) -> Optional[float]:
        """Most recent value."""
        return self._values[-1] if self._values else None

    @property
    def change(self) -> Optional[float]:
        """Change from first to latest value in window."""
        if len(self._values) < 2:
            return None
        return self._values[-1] - self._values[0]

    @property
    def change_pct(self) -> Optional[float]:
        """Percent change from first to latest value."""
        if len(self._values) < 2 or self._values[0] == 0:
            return None
        return (self._values[-1] - self._values[0]) / abs(self._values[0])

    # ------------------------------------------------------------------
    # Percentile rank of a value within the window
    # ------------------------------------------------------------------

    def percentile_rank(self, value: float) -> Optional[float]:
        """
        Where does `value` sit within the current window?
        Returns 0.0 (lowest) to 1.0 (highest).
        """
        if not self._values:
            return None
        count_below = sum(1 for v in self._values if v < value)
        return count_below / len(self._values)

    def is_in_bottom_quartile(self) -> bool:
        """Is the latest value in the bottom 25% of the window?"""
        if self.p25 is None or self.latest is None:
            return False
        return self.latest <= self.p25

    def is_in_top_quartile(self) -> bool:
        """Is the latest value in the top 25% of the window?"""
        if self.p75 is None or self.latest is None:
            return False
        return self.latest >= self.p75

    # ------------------------------------------------------------------
    # Z-score of latest value
    # ------------------------------------------------------------------

    @property
    def z_score(self) -> Optional[float]:
        """Z-score of the latest value relative to window mean/std."""
        if self.mean is None or self.std is None or self.std == 0:
            return None
        if self.latest is None:
            return None
        return (self.latest - self.mean) / self.std

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Reset the window."""
        self._values.clear()
        self._timestamps.clear()

    def snapshot(self) -> Dict[str, Any]:
        """Export current state for logging/dashboard."""
        return {
            "count": self.count,
            "mean": self.mean,
            "median": self.median,
            "std": self.std,
            "min": self.min,
            "max": self.max,
            "range": self.range,
            "p25": self.p25,
            "p75": self.p75,
            "trend": self.trend,
            "latest": self.latest,
            "change": self.change,
            "change_pct": self.change_pct,
            "z_score": self.z_score,
        }

    def __len__(self) -> int:
        return len(self._values)

    def __bool__(self) -> bool:
        return bool(self._values)


def _now() -> float:
    import time
    return time.time()
