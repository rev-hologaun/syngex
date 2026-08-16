"""
strategies/signal_tracker.py — Signal Outcome Tracking

Tracks open signals and resolves them with outcomes for backtesting
and per-strategy statistics.

Resolves signals when:
- Stop loss hit (LOSS)
- Target hit (WIN)
- Time expired (CLOSED)
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SignalOutcome(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    CLOSED = "CLOSED"  # Time expired, neither stop nor target hit


@dataclass
class OpenSignal:
    """An open signal being tracked for outcome."""
    signal_id: str               # Unique ID (timestamp + strategy_id)
    direction: str               # "LONG" or "SHORT"
    strategy_id: str
    entry: float
    stop: float
    target: float
    confidence: float
    timestamp: float
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Per-strategy hold time (0 = use global default)
    max_hold_seconds: int = 0

    # Computed
    risk: float = 0.0
    reward: float = 0.0
    rr_ratio: float = 0.0

    def __post_init__(self) -> None:
        self.risk = abs(self.entry - self.stop)
        self.reward = abs(self.target - self.entry)
        self.rr_ratio = self.reward / self.risk if self.risk > 0 else 0.0


@dataclass
class ResolvedSignal:
    """A resolved signal with outcome."""
    open_signal: OpenSignal
    outcome: SignalOutcome
    exit_price: float
    pnl: float
    pnl_pct: float
    hold_time: float  # seconds
    resolution_time: float


class SignalTracker:
    """
    Tracks open signals and resolves them with outcomes.

    Usage:
        tracker = SignalTracker(max_hold_seconds=900)  # 15 min default
        tracker.track(signal_dict)  # Add a new signal
        tracker.update(underlying_price, timestamp)  # Check for resolutions
        resolved = tracker.get_resolved()  # Get resolved signals
    """

    def __init__(
        self,
        max_hold_seconds: int = 900,
        log_dir: str = "log",
        symbol: str = "UNKNOWN",
        strategy_hold_times: Optional[Dict[str, int]] = None,
        version: str = "",
        max_resolved_in_memory: int = 5000,
    ) -> None:
        """
        Initialize the SignalTracker.

        Args:
            max_hold_seconds: Global default max hold time (seconds) for strategies
                              that don't have a per-strategy override.
            log_dir: Directory for signal outcome logs.
            symbol: Symbol this tracker is monitoring.
            strategy_hold_times: Optional dict mapping strategy_id to max_hold_seconds.
        """
        self.max_hold_seconds = max_hold_seconds
        self._strategy_hold_times = strategy_hold_times or {}
        self._open_signals: Dict[str, OpenSignal] = {}
        self._resolved_signals: List[ResolvedSignal] = []
        # Pilot harness: env SYNGEX_LOG_DIR redirects signal/outcome logs so an
        # A/B pilot run doesn't collide with the live log/ dir. Default "log".
        log_dir = os.environ.get("SYNGEX_LOG_DIR", log_dir)  # noqa: PLW2901
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._symbol = symbol
        self._version = version  # e.g., "" or "_v2"

        # Bound the in-memory resolved-signals list. The durable JSONL log always
        # keeps the full history; RAM only needs the most recent entries for live
        # stats/summary. Without this cap, loading an 8GB outcome log at startup
        # (as Python objects) ate tens of GB and the OOM killer killed the box
        # (fixed 2026-08-13).
        self._max_resolved_in_memory = max(1, max_resolved_in_memory)

        # Per-strategy statistics
        self._strategy_stats: Dict[str, Dict[str, Any]] = {}

        # Track how many resolved signals have been persisted (for incremental saves)
        self._saved_count: int = 0

        # Load resolved signals from disk (survives restarts)
        self._load_resolved()

    def track(self, signal: Dict[str, Any]) -> str:
        """
        Start tracking a new signal.

        Returns the signal_id.
        """
        signal_id = f"{signal['strategy_id']}_{int(signal['timestamp']*1000)}_{uuid.uuid4().hex[:8]}"

        # Look up per-strategy hold time; fall back to global default (0)
        strat_id = signal.get("strategy_id", "")
        hold_seconds = self._strategy_hold_times.get(strat_id, 0)

        open_signal = OpenSignal(
            signal_id=signal_id,
            direction=signal.get("direction", "LONG"),
            strategy_id=strat_id,
            entry=float(signal.get("entry", 0)),
            stop=float(signal.get("stop", 0)),
            target=float(signal.get("target", 0)),
            confidence=float(signal.get("confidence", 0)),
            timestamp=float(signal.get("timestamp", time.time())),
            reason=signal.get("reason", ""),
            metadata=signal.get("metadata", {}),
            max_hold_seconds=hold_seconds,
        )

        self._open_signals[signal_id] = open_signal

        # Initialize strategy stats
        strat = signal.get("strategy_id", "unknown")
        if strat not in self._strategy_stats:
            self._strategy_stats[strat] = {
                "total_signals": 0,
                "wins": 0,
                "losses": 0,
                "closed": 0,
                "resolved_count": 0,
                "hold_time_sum": 0.0,
                "rr_sum": 0.0,
                "pnl_pct_sum": 0.0,
                "total_pnl": 0.0,
                "total_pnl_pct": 0.0,
                "avg_hold_time": 0.0,
                "win_rate": 0.0,
                "avg_rr": 0.0,
                "best_pnl": float("-inf"),
                "worst_pnl": float("inf"),
            }

        self._strategy_stats[strat]["total_signals"] += 1

        # --- Dual-log: append to per-symbol and global signal logs ---
        self._log_signal_to_disk(signal_id, signal)

        return signal_id

    def _log_signal_to_disk(self, signal_id: str, signal: Dict[str, Any]) -> None:
        """Append a new signal to per-symbol and global JSONL logs."""
        log_entry = {
            "signal_id": signal_id,
            "direction": signal.get("direction", "LONG"),
            "confidence": float(signal.get("confidence", 0)),
            "entry": float(signal.get("entry", 0)),
            "stop": float(signal.get("stop", 0)),
            "target": float(signal.get("target", 0)),
            "strategy_id": signal.get("strategy_id", ""),
            "symbol": self._symbol,
            "reason": signal.get("reason", ""),
            "risk_reward_ratio": float(signal.get("risk_reward_ratio", 0)),
            "strength": signal.get("strength", "MODERATE"),
            "timestamp": float(signal.get("timestamp", time.time())),
            "metadata": signal.get("metadata", {}),
        }
        json_line = json.dumps(log_entry) + "\n"

        # Per-symbol log: log/signals_{SYMBOL}.jsonl
        # SignalTracker owns all signal persistence — no global log.
        # StrategyEngine._log_signal() delegates here via track().
        try:
            sym_path = self._log_dir / f"signals_{self._symbol}{self._version}.jsonl"
            with open(sym_path, "a") as f:
                f.write(json_line)
        except OSError:
            pass

    def update(self, underlying_price: float, timestamp: Optional[float] = None) -> List[ResolvedSignal]:
        """
        Check all open signals against the current price.

        Resolves signals that hit stop, target, or expired.

        Returns list of newly resolved signals.
        """
        if timestamp is None:
            timestamp = time.time()

        resolved: List[ResolvedSignal] = []
        to_remove: List[str] = []

        for signal_id, open_sig in self._open_signals.items():
            resolution = self._resolve_signal(open_sig, underlying_price, timestamp)
            if resolution is not None:
                resolved.append(resolution)
                self._append_resolved(resolution)
                to_remove.append(signal_id)
                self._update_strategy_stats(resolution)
                self._recompute_strategy_averages(resolution.open_signal.strategy_id)

        for sig_id in to_remove:
            del self._open_signals[sig_id]

        if resolved:
            self._save_resolved(resolved)

        return resolved

    def _append_resolved(self, resolution: ResolvedSignal) -> None:
        """Append a resolved signal to the in-memory list, keeping it bounded.

        The durable JSONL log always holds the full history, so RAM only keeps
        the most recent ``max_resolved_in_memory`` entries. This bounds memory
        over long sessions (previously the list grew without limit).
        """
        self._resolved_signals.append(resolution)
        overflow = len(self._resolved_signals) - self._max_resolved_in_memory
        if overflow > 0:
            del self._resolved_signals[:overflow]

    def _resolve_signal(
        self,
        open_sig: OpenSignal,
        price: float,
        timestamp: float,
    ) -> Optional[ResolvedSignal]:
        """Resolve a single signal based on price and time."""
        hold_time = timestamp - open_sig.timestamp

        # Check time expiry first (use per-strategy hold time if set, else global default)
        # max_hold == 0 means no time limit (disabled)
        max_hold = open_sig.max_hold_seconds if open_sig.max_hold_seconds > 0 else self.max_hold_seconds
        if max_hold > 0 and hold_time > max_hold:
            exit_price = price
            pnl = self._calc_pnl(open_sig.direction, open_sig.entry, exit_price)
            pnl_pct = (pnl / open_sig.risk * 100) if open_sig.risk > 0 else 0.0
            return ResolvedSignal(
                open_signal=open_sig,
                outcome=SignalOutcome.CLOSED,
                exit_price=exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                hold_time=hold_time,
                resolution_time=timestamp,
            )

        # Check stop loss
        if open_sig.direction == "LONG" and price <= open_sig.stop:
            exit_price = open_sig.stop
            pnl = self._calc_pnl(open_sig.direction, open_sig.entry, exit_price)
            pnl_pct = (pnl / open_sig.risk * 100) if open_sig.risk > 0 else 0.0
            return ResolvedSignal(
                open_signal=open_sig,
                outcome=SignalOutcome.LOSS,
                exit_price=exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                hold_time=hold_time,
                resolution_time=timestamp,
            )

        if open_sig.direction == "SHORT" and price >= open_sig.stop:
            exit_price = open_sig.stop
            pnl = self._calc_pnl(open_sig.direction, open_sig.entry, exit_price)
            pnl_pct = (pnl / open_sig.risk * 100) if open_sig.risk > 0 else 0.0
            return ResolvedSignal(
                open_signal=open_sig,
                outcome=SignalOutcome.LOSS,
                exit_price=exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                hold_time=hold_time,
                resolution_time=timestamp,
            )

        # Check target
        if open_sig.direction == "LONG" and price >= open_sig.target:
            exit_price = open_sig.target
            pnl = self._calc_pnl(open_sig.direction, open_sig.entry, exit_price)
            pnl_pct = (pnl / open_sig.risk * 100) if open_sig.risk > 0 else 0.0
            return ResolvedSignal(
                open_signal=open_sig,
                outcome=SignalOutcome.WIN,
                exit_price=exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                hold_time=hold_time,
                resolution_time=timestamp,
            )

        if open_sig.direction == "SHORT" and price <= open_sig.target:
            exit_price = open_sig.target
            pnl = self._calc_pnl(open_sig.direction, open_sig.entry, exit_price)
            pnl_pct = (pnl / open_sig.risk * 100) if open_sig.risk > 0 else 0.0
            return ResolvedSignal(
                open_signal=open_sig,
                outcome=SignalOutcome.WIN,
                exit_price=exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                hold_time=hold_time,
                resolution_time=timestamp,
            )

        return None

    def _calc_pnl(self, direction: str, entry: float, exit_price: float) -> float:
        """Calculate PnL for a signal."""
        if direction == "LONG":
            return exit_price - entry
        else:
            return entry - exit_price

    def _update_strategy_stats(self, resolution: ResolvedSignal) -> None:
        """Update per-strategy statistics after resolution (O(1))."""
        strat = resolution.open_signal.strategy_id
        stats = self._strategy_stats[strat]

        if resolution.outcome == SignalOutcome.WIN:
            stats["wins"] += 1
        elif resolution.outcome == SignalOutcome.LOSS:
            stats["losses"] += 1
        else:
            stats["closed"] += 1

        stats["total_pnl"] += resolution.pnl
        stats["total_pnl_pct"] += resolution.pnl_pct
        stats["best_pnl"] = max(stats["best_pnl"], resolution.pnl)
        stats["worst_pnl"] = min(stats["worst_pnl"], resolution.pnl)

        # Derive resolved count from outcomes (robust across track/load)
        resolved_count = stats["wins"] + stats["losses"] + stats["closed"]

        # Running sums for averages — avoids rescanning the resolved list per
        # resolution (previous code was O(n) per signal -> O(n^2) overall).
        stats["resolved_count"] = resolved_count
        stats["hold_time_sum"] = stats.get("hold_time_sum", 0.0) + resolution.hold_time
        stats["rr_sum"] = stats.get("rr_sum", 0.0) + resolution.open_signal.rr_ratio
        stats["pnl_pct_sum"] = stats.get("pnl_pct_sum", 0.0) + resolution.pnl_pct
        if resolved_count > 0:
            stats["avg_hold_time"] = stats["hold_time_sum"] / resolved_count
            stats["avg_rr"] = stats["rr_sum"] / resolved_count
            stats["avg_pnl_pct"] = stats["pnl_pct_sum"] / resolved_count
        stats["win_rate"] = stats["wins"] / resolved_count if resolved_count > 0 else 0.0

    def _recompute_strategy_averages(self, strat: str) -> None:
        """Recalculate the per-strategy averages from running sums (O(1))."""
        stats = self._strategy_stats[strat]
        resolved_count = stats.get("resolved_count", 0)
        if resolved_count > 0:
            stats["avg_hold_time"] = stats.get("hold_time_sum", 0.0) / resolved_count
            stats["avg_rr"] = stats.get("rr_sum", 0.0) / resolved_count
            stats["avg_pnl_pct"] = stats.get("pnl_pct_sum", 0.0) / resolved_count

    def get_open_signals(self) -> List[OpenSignal]:
        """Return list of currently open signals."""
        return list(self._open_signals.values())

    def get_resolved(self) -> List[ResolvedSignal]:
        """Return list of resolved signals."""
        return list(self._resolved_signals)

    def get_strategy_stats(self) -> Dict[str, Dict[str, Any]]:
        """Return per-strategy statistics."""
        return dict(self._strategy_stats)

    def get_summary(self) -> Dict[str, Any]:
        """Return overall summary."""
        total = len(self._resolved_signals)
        wins = sum(1 for r in self._resolved_signals if r.outcome == SignalOutcome.WIN)
        losses = sum(1 for r in self._resolved_signals if r.outcome == SignalOutcome.LOSS)
        closed = sum(1 for r in self._resolved_signals if r.outcome == SignalOutcome.CLOSED)
        total_pnl = sum(r.pnl for r in self._resolved_signals)

        return {
            "total_resolved": total,
            "wins": wins,
            "losses": losses,
            "closed": closed,
            "win_rate": wins / total if total > 0 else 0.0,
            "total_pnl": round(total_pnl, 2),
            "avg_hold_time": sum(r.hold_time for r in self._resolved_signals) / total if total > 0 else 0.0,
            "open_signals": len(self._open_signals),
        }

    def _save_resolved(self, resolved_batch: List[ResolvedSignal]) -> None:
        """Append newly resolved signals to disk for persistence.

        Only the batch produced by the current ``update()`` call is written, so
        we don't depend on in-memory list indices (which now get trimmed once
        ``max_resolved_in_memory`` is exceeded). The JSONL log remains the
        durable, complete history.
        """
        if not resolved_batch:
            return
        log_path = self._log_dir / f"signal_outcomes_{self._symbol}{self._version}.jsonl"
        try:
            with open(log_path, "a") as f:
                for r in resolved_batch:
                    data = {
                        "signal_id": r.open_signal.signal_id,
                        "strategy_id": r.open_signal.strategy_id,
                        "direction": r.open_signal.direction,
                        "entry": r.open_signal.entry,
                        "stop": r.open_signal.stop,
                        "target": r.open_signal.target,
                        "outcome": r.outcome.value,
                        "exit_price": r.exit_price,
                        "pnl": round(r.pnl, 2),
                        "pnl_pct": round(r.pnl_pct, 2),
                        "hold_time": round(r.hold_time, 1),
                        "confidence": r.open_signal.confidence,
                        "reason": r.open_signal.reason,
                        "metadata": r.open_signal.metadata,
                        "resolution_time": r.resolution_time,
                    }
                    f.write(json.dumps(data) + "\n")
        except OSError:
            pass
        # Informational: total resolved signals persisted so far (durable source
        # is the JSONL file; this counter is only a coarse progress marker).
        self._saved_count += len(resolved_batch)

    def _load_resolved(self) -> None:
        """Load the most recent resolved signals from disk (bounded tail-load).

        Only the last ``max_resolved_in_memory`` signals are reconstructed in
        memory. The JSONL log remains the complete on-disk history; RAM only
        holds a recent window for live stats/summary. Previously this loaded the
        ENTIRE (multi-GB) log as Python objects, which caused OOM kills.
        """
        log_path = self._log_dir / f"signal_outcomes_{self._symbol}{self._version}.jsonl"
        if not log_path.exists():
            return
        try:
            for line in self._read_tail_lines(log_path, self._max_resolved_in_memory):
                if not line.strip():
                    continue
                data = json.loads(line)
                # Reconstruct OpenSignal
                open_sig = OpenSignal(
                    signal_id=data["signal_id"],
                    direction=data["direction"],
                    strategy_id=data["strategy_id"],
                    entry=float(data["entry"]),
                    stop=float(data["stop"]),
                    target=float(data["target"]),
                    confidence=float(data.get("confidence", 0)),
                    timestamp=float(data.get("timestamp", 0)),
                    reason=data.get("reason", ""),
                    metadata=data.get("metadata", {}),
                )
                resolution = ResolvedSignal(
                    open_signal=open_sig,
                    outcome=SignalOutcome(data["outcome"]),
                    exit_price=float(data["exit_price"]),
                    pnl=float(data["pnl"]),
                    pnl_pct=float(data["pnl_pct"]),
                    hold_time=float(data["hold_time"]),
                    resolution_time=float(data["resolution_time"]),
                )
                self._append_resolved(resolution)
                # Initialize strategy stats entry if needed (for loaded signals)
                strat = resolution.open_signal.strategy_id
                if strat not in self._strategy_stats:
                    self._strategy_stats[strat] = {
                        "total_signals": 0,
                        "wins": 0,
                        "losses": 0,
                        "closed": 0,
                        "resolved_count": 0,
                        "hold_time_sum": 0.0,
                        "rr_sum": 0.0,
                        "pnl_pct_sum": 0.0,
                        "total_pnl": 0.0,
                        "total_pnl_pct": 0.0,
                        "avg_hold_time": 0.0,
                        "win_rate": 0.0,
                        "avg_rr": 0.0,
                        "best_pnl": float("-inf"),
                        "worst_pnl": float("inf"),
                    }
                # Update strategy stats (maintains running-sum averages in O(1))
                self._update_strategy_stats(resolution)
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    @staticmethod
    def _read_tail_lines(path: Path, n: int) -> List[str]:
        """Return the last ``n`` non-empty lines of a file, reading from the end.

        Uses a buffered backwards read so we never load a multi-GB log into
        memory. ``n`` is the max count; fewer lines may be returned if the file
        has fewer.
        """
        lines: List[str] = []
        try:
            with open(path, "r", errors="replace") as fh:
                fh.seek(0, 2)
                size = fh.tell()
                if size == 0:
                    return []
                chunk = 65536
                pos = size
                buffer = ""
                while pos > 0 and len(lines) < n:
                    read_size = min(chunk, pos)
                    pos -= read_size
                    fh.seek(pos)
                    buffer = fh.read(read_size) + buffer
                    if "\n" in buffer:
                        parts = buffer.split("\n")
                        buffer = parts[0]  # may be a partial line at the chunk head
                        for piece in reversed(parts[1:]):
                            if piece.strip():
                                lines.insert(0, piece)
                                if len(lines) >= n:
                                    break
                if buffer.strip() and len(lines) < n:
                    lines.insert(0, buffer)
        except OSError:
            return []
        return lines[-n:] if len(lines) > n else lines
