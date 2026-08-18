"""
strategies/rolling_window.py — Rolling statistics class

Supports multiple window types used by ALL strategies:
- Time-based windows (30m, 5min)
- Count-based windows (20-period, custom)
- Tracks: mean, std, min, max, percentiles, trend direction

Used by every alpha strategy for normalization and threshold detection.
"""

from __future__ import annotations

import bisect
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
    _trend: str = "FLAT"
    _trend_z_threshold: float = 0.5       # z-score needed to ENTER a trend
    _trend_exit_threshold: float = 0.3    # z-score below which we EXIT
    _hard_cap: int = 2000                  # max entries for time-based windows

    # --- lazy-evaluation caches ---
    _dirty: bool = True
    _mean_cache: Optional[float] = None
    _median_cache: Optional[float] = None
    _std_cache: Optional[float] = None
    _min_cache: Optional[float] = None
    _max_cache: Optional[float] = None
    _p25_cache: Optional[float] = None
    _p75_cache: Optional[float] = None
    _trend_cache: Optional[str] = "FLAT"

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
        self._dirty = True

        # Hard cap: prevent unbounded growth in time-based windows
        if self.window_type == "time" and len(self._values) > self._hard_cap:
            while len(self._values) > self._hard_cap:
                self._values.popleft()
                self._timestamps.popleft()

    def trim(self) -> None:
        """Force-trim oldest entries to stay within _hard_cap."""
        if len(self._values) > self._hard_cap:
            while len(self._values) > self._hard_cap:
                self._values.popleft()
                self._timestamps.popleft()
            self._dirty = True

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
        if self._dirty:
            self._refresh()
        return self._mean_cache

    @property
    def median(self) -> Optional[float]:
        """Rolling median."""
        if self._dirty:
            self._refresh()
        return self._median_cache

    @property
    def std(self) -> Optional[float]:
        """Rolling standard deviation (sample). Returns None if < 2 values."""
        if self._dirty:
            self._refresh()
        return self._std_cache

    @property
    def min(self) -> Optional[float]:
        if self._dirty:
            self._refresh()
        return self._min_cache

    @property
    def max(self) -> Optional[float]:
        if self._dirty:
            self._refresh()
        return self._max_cache

    @property
    def range(self) -> Optional[float]:
        """Current range (max - min)."""
        if self._dirty:
            self._refresh()
        if self._min_cache is None or self._max_cache is None:
            return None
        return self._max_cache - self._min_cache

    @property
    def p25(self) -> Optional[float]:
        if self._dirty:
            self._refresh()
        return self._p25_cache

    @property
    def p75(self) -> Optional[float]:
        if self._dirty:
            self._refresh()
        return self._p75_cache

    @property
    def trend(self) -> str:
        """
        Trend direction with hysteresis to prevent flip-flopping.

        Returns: "UP", "DOWN", or "FLAT"
        """
        if self._dirty:
            self._refresh()
        # Always compute trend — it's idempotent and needs to run even
        # when _dirty is False (e.g. after mean/std were accessed first).
        self._compute_trend()
        return self._trend_cache

    def _compute_trend(self) -> None:
        """Compute trend direction with hysteresis.

        Idempotent — safe to call repeatedly with the same data.
        """
        if len(self._values) < 4:
            self._trend_cache = "FLAT"
            return

        vals = list(self._values)
        half = len(vals) // 2
        first_half = statistics.mean(vals[:half])
        second_half = statistics.mean(vals[half:])

        diff = second_half - first_half
        std = self._std_cache
        if std is None or std == 0:
            self._trend_cache = "FLAT"
            return

        z = diff / std

        # Hysteresis: different thresholds for entering vs exiting trends
        if self._trend_cache in ("UP", "FLAT"):
            if z > self._trend_z_threshold:
                self._trend_cache = "UP"
            elif self._trend_cache == "UP" and z < self._trend_exit_threshold:
                self._trend_cache = "FLAT"
        elif self._trend_cache == "DOWN":
            if z < -self._trend_z_threshold:
                self._trend_cache = "DOWN"
            elif z > -self._trend_exit_threshold:
                self._trend_cache = "FLAT"

    @property
    def latest(self) -> Optional[float]:
        """Most recent value."""
        return self._values[-1] if self._values else None

    def sample_before_now(self, age_seconds: float, now: Optional[float] = None) -> Optional[float]:
        """
        Return the value recorded closest to (and at-or-before) ``now - age_seconds``.

        Time-anchored read required by M4: instead of assuming a positional slot
        (``[-5]``) has stable meaning on a *time-based* window (where ticks per
        wall-clock span vary with feed rate), it resolves the actual sample at a
        fixed lookback age. Timestamps are pushed in monotonic order, so a bisect
        over ``_timestamps`` locates the boundary in O(log n).

        Args:
            age_seconds: how far back in wall-clock time to sample (300 for 5m).
            now: reference "now"; defaults to real time. Pass a fixed value in
                tests for determinism.

        Returns:
            Value whose timestamp is the newest <= ``now - age_seconds``, or None
            if no sample that old exists (window younger than lookback, or empty).
        """
        if not self._values or not self._timestamps:
            return None
        if age_seconds <= 0:
            return self._values[-1]
        now = now if now is not None else _now()
        i = bisect.bisect_right(self._timestamps, now - age_seconds) - 1
        if i < 0:
            return None
        return self._values[i]

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
        if self._dirty:
            self._refresh()
        if self._mean_cache is None or self._std_cache is None or self._std_cache == 0:
            return None
        if self.latest is None:
            return None
        return (self.latest - self._mean_cache) / self._std_cache

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Reset the window."""
        self._values.clear()
        self._timestamps.clear()
        self._dirty = True
        self._mean_cache = None
        self._median_cache = None
        self._std_cache = None
        self._min_cache = None
        self._max_cache = None
        self._p25_cache = None
        self._p75_cache = None
        self._trend_cache = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _percentile(sorted_vals: List[float], q: float) -> float:
        """Canonical linear-interpolation percentile (the numpy-linear method, n = method 7).

        ``q`` is in [0, 100]. Deterministic and matches the definition every
        standard stats library uses. Replaces the old nearest/midpoint-only
        calculation, which returned wrong quartiles for most window sizes
        (e.g. n=3,4,6,7,8,12...), silently shifting bottom/top-quartile gates.
        """
        n = len(sorted_vals)
        if n == 1:
            return sorted_vals[0]
        pos = (n - 1) * (q / 100.0)
        lower = int(pos)
        upper = min(lower + 1, n - 1)
        frac = pos - lower
        return sorted_vals[lower] + frac * (sorted_vals[upper] - sorted_vals[lower])

    def _refresh(self) -> None:
        """Compute all cached values in one pass.  Called when _dirty is True."""
        # Initialize trend_cache so _compute_trend's hysteresis logic has a baseline
        if self._trend_cache not in ("UP", "DOWN"):
            self._trend_cache = "FLAT"

        if not self._values:
            self._mean_cache = None
            self._median_cache = None
            self._std_cache = None
            self._min_cache = None
            self._max_cache = None
            self._p25_cache = None
            self._p75_cache = None
            self._dirty = False
            return

        self._mean_cache = statistics.mean(self._values)
        self._median_cache = statistics.median(self._values)
        self._min_cache = min(self._values)
        self._max_cache = max(self._values)

        if len(self._values) >= 2:
            self._std_cache = statistics.stdev(self._values)
            sorted_vals = sorted(self._values)
            self._p25_cache = self._percentile(sorted_vals, 25.0)
            self._p75_cache = self._percentile(sorted_vals, 75.0)
        else:
            self._std_cache = None
            self._p25_cache = None
            self._p75_cache = None

        self._dirty = False

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
