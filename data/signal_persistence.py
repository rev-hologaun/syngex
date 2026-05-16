"""data/signal_persistence — JSONL persistence layer for signal recovery across restarts."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from strategies.signal_tracker import OpenSignal, ResolvedSignal, SignalOutcome


@dataclass
class SignalPersistence:
    """Persist signals to JSONL files for recovery across restarts.
    
    This class provides a persistent storage mechanism for open and resolved signals,
    allowing the system to recover signal state across restarts. Signals are stored
    in JSONL format (one JSON object per line) for efficient append-only writes and
    easy parsing.
    
    Attributes:
        open_signals_path: Path to the open signals JSONL file
        resolved_signals_path: Path to the resolved signals JSONL file
        flush_interval_seconds: How often to automatically flush to disk (default: 60s)
        max_buffer_size: Max signals in buffer before forced flush (default: 1000)
    
    Example:
        >>> persistence = SignalPersistence(
        ...     open_signals_path=Path("~/data/signals/open_signals.jsonl"),
        ...     resolved_signals_path=Path("~/data/signals/resolved_signals.jsonl")
        ... )
        >>> persistence.save_open_signal(my_signal)
        >>> persistence.flush_if_needed()
        >>> open_signals = persistence.load_open_signals()
    """
    
    # File paths
    open_signals_path: Path
    resolved_signals_path: Path
    
    # Configuration
    flush_interval_seconds: float = 60.0  # How often to flush to disk
    max_buffer_size: int = 1000  # Max signals before forced flush
    
    # Runtime state
    _open_buffer: List[OpenSignal] = field(default_factory=list)
    _resolved_buffer: List[ResolvedSignal] = field(default_factory=list)
    _last_flush_ts: float = field(default_factory=lambda: time.time())
    
    def __post_init__(self):
        """Ensure parent directories exist on initialization."""
        self._ensure_paths_exist()
    
    # ========== Core Operations ==========
    
    def save_open_signal(self, signal: OpenSignal) -> None:
        """Add open signal to buffer.
        
        Adds the signal to the in-memory buffer and triggers an automatic flush
        if the buffer exceeds max_buffer_size.
        
        Args:
            signal: OpenSignal to persist
            
        Example:
            >>> persistence.save_open_signal(signal)
        """
        self._open_buffer.append(signal)
        self.flush_if_needed()
    
    def save_resolved_signal(self, signal: ResolvedSignal) -> None:
        """Add resolved signal to buffer.
        
        Adds the signal to the in-memory buffer and triggers an automatic flush
        if the buffer exceeds max_buffer_size.
        
        Args:
            signal: ResolvedSignal to persist
            
        Example:
            >>> persistence.save_resolved_signal(resolved_signal)
        """
        self._resolved_buffer.append(signal)
        self.flush_if_needed()
    
    def load_open_signals(self) -> List[OpenSignal]:
        """Load all open signals from file.
        
        Reads the open signals JSONL file and deserializes all signals.
        Returns an empty list if the file doesn't exist or is empty.
        
        Returns:
            List of OpenSignal objects from the file
            
        Example:
            >>> open_signals = persistence.load_open_signals()
            >>> for signal in open_signals:
            ...     print(f"Signal {signal.signal_id} is being tracked")
        """
        return self._load_signals_from_file(self.open_signals_path, self._deserialize_open_signal)
    
    def load_resolved_signals(self) -> List[ResolvedSignal]:
        """Load all resolved signals from file.
        
        Reads the resolved signals JSONL file and deserializes all signals.
        Returns an empty list if the file doesn't exist or is empty.
        
        Returns:
            List of ResolvedSignal objects from the file
            
        Example:
            >>> resolved_signals = persistence.load_resolved_signals()
            >>> wins = [s for s in resolved_signals if s.outcome == SignalOutcome.WIN]
        """
        return self._load_signals_from_file(self.resolved_signals_path, self._deserialize_resolved_signal)
    
    def flush(self) -> None:
        """Write all buffered signals to disk.
        
        Serializes all signals in both buffers and appends them to their
        respective JSONL files. Updates the last flush timestamp.
        
        This is an append-only operation - existing signals in the file are not
        overwritten.
        
        Example:
            >>> persistence.save_open_signal(signal1)
            >>> persistence.save_open_signal(signal2)
            >>> persistence.flush()  # Write both to disk
        """
        self._ensure_paths_exist()
        
        # Flush open signals
        if self._open_buffer:
            with open(self.open_signals_path, 'a') as f:
                for signal in self._open_buffer:
                    line = self._serialize_open_signal(signal)
                    f.write(line + '\n')
            self._open_buffer.clear()
        
        # Flush resolved signals
        if self._resolved_buffer:
            with open(self.resolved_signals_path, 'a') as f:
                for signal in self._resolved_buffer:
                    line = self._serialize_resolved_signal(signal)
                    f.write(line + '\n')
            self._resolved_buffer.clear()
        
        # Update last flush timestamp
        self._last_flush_ts = time.time()
    
    def flush_if_needed(self) -> None:
        """Flush if buffer full or time elapsed.
        
        Automatically flushes to disk if either:
        - Total buffered signals (open + resolved) exceeds max_buffer_size
        - More than flush_interval_seconds have passed since last flush
        
        Example:
            >>> persistence.save_open_signal(signal)
            >>> persistence.flush_if_needed()  # Auto-flush if thresholds met
        """
        total_buffered = len(self._open_buffer) + len(self._resolved_buffer)
        time_elapsed = time.time() - self._last_flush_ts
        
        if total_buffered >= self.max_buffer_size or time_elapsed >= self.flush_interval_seconds:
            self.flush()
    
    # ========== File Operations ==========
    
    def _serialize_open_signal(self, signal: OpenSignal) -> str:
        """Convert OpenSignal to JSON line.
        
        Serializes an OpenSignal to a single JSON line for JSONL storage.
        
        Args:
            signal: OpenSignal to serialize
            
        Returns:
            JSON string representation of the signal
            
        Example:
            >>> signal = OpenSignal(...)
            >>> json_line = persistence._serialize_open_signal(signal)
        """
        data = {
            "signal_id": signal.signal_id,
            "direction": signal.direction,
            "strategy_id": signal.strategy_id,
            "entry": signal.entry,
            "stop": signal.stop,
            "target": signal.target,
            "confidence": signal.confidence,
            "timestamp": signal.timestamp,
            "reason": signal.reason,
            "metadata": signal.metadata,
            "max_hold_seconds": signal.max_hold_seconds,
            "risk": signal.risk,
            "reward": signal.reward,
            "rr_ratio": signal.rr_ratio,
        }
        return json.dumps(data)
    
    def _serialize_resolved_signal(self, signal: ResolvedSignal) -> str:
        """Convert ResolvedSignal to JSON line.
        
        Serializes a ResolvedSignal to a single JSON line for JSONL storage.
        Includes the full open_signal data nested within.
        
        Args:
            signal: ResolvedSignal to serialize
            
        Returns:
            JSON string representation of the signal
            
        Example:
            >>> signal = ResolvedSignal(...)
            >>> json_line = persistence._serialize_resolved_signal(signal)
        """
        data = {
            "open_signal": {
                "signal_id": signal.open_signal.signal_id,
                "direction": signal.open_signal.direction,
                "strategy_id": signal.open_signal.strategy_id,
                "entry": signal.open_signal.entry,
                "stop": signal.open_signal.stop,
                "target": signal.open_signal.target,
                "confidence": signal.open_signal.confidence,
                "timestamp": signal.open_signal.timestamp,
                "reason": signal.open_signal.reason,
                "metadata": signal.open_signal.metadata,
                "max_hold_seconds": signal.open_signal.max_hold_seconds,
                "risk": signal.open_signal.risk,
                "reward": signal.open_signal.reward,
                "rr_ratio": signal.open_signal.rr_ratio,
            },
            "outcome": signal.outcome.value if hasattr(signal.outcome, 'value') else str(signal.outcome),
            "exit_price": signal.exit_price,
            "pnl": signal.pnl,
            "pnl_pct": signal.pnl_pct,
            "hold_time": signal.hold_time,
            "resolution_time": signal.resolution_time,
        }
        return json.dumps(data)
    
    def _deserialize_open_signal(self, line: str) -> OpenSignal:
        """Parse JSON line to OpenSignal.
        
        Deserializes a JSON line from the open signals file back to an OpenSignal.
        
        Args:
            line: JSON string line from the file
            
        Returns:
            OpenSignal instance
            
        Raises:
            json.JSONDecodeError: If line is not valid JSON
            KeyError: If required fields are missing
        """
        data = json.loads(line.strip())
        return OpenSignal(
            signal_id=data["signal_id"],
            direction=data["direction"],
            strategy_id=data["strategy_id"],
            entry=data["entry"],
            stop=data["stop"],
            target=data["target"],
            confidence=data["confidence"],
            timestamp=data["timestamp"],
            reason=data.get("reason", ""),
            metadata=data.get("metadata", {}),
            max_hold_seconds=data.get("max_hold_seconds", 0),
            risk=data.get("risk", 0.0),
            reward=data.get("reward", 0.0),
            rr_ratio=data.get("rr_ratio", 0.0),
        )
    
    def _deserialize_resolved_signal(self, line: str) -> ResolvedSignal:
        """Parse JSON line to ResolvedSignal.
        
        Deserializes a JSON line from the resolved signals file back to a ResolvedSignal.
        
        Args:
            line: JSON string line from the file
            
        Returns:
            ResolvedSignal instance
            
        Raises:
            json.JSONDecodeError: If line is not valid JSON
            KeyError: If required fields are missing
        """
        data = json.loads(line.strip())
        
        # Deserialize nested open_signal
        open_data = data["open_signal"]
        open_signal = OpenSignal(
            signal_id=open_data["signal_id"],
            direction=open_data["direction"],
            strategy_id=open_data["strategy_id"],
            entry=open_data["entry"],
            stop=open_data["stop"],
            target=open_data["target"],
            confidence=open_data["confidence"],
            timestamp=open_data["timestamp"],
            reason=open_data.get("reason", ""),
            metadata=open_data.get("metadata", {}),
            max_hold_seconds=open_data.get("max_hold_seconds", 0),
            risk=open_data.get("risk", 0.0),
            reward=open_data.get("reward", 0.0),
            rr_ratio=open_data.get("rr_ratio", 0.0),
        )
        
        # Deserialize outcome
        outcome_value = data["outcome"]
        if isinstance(outcome_value, str):
            outcome = SignalOutcome(outcome_value)
        else:
            outcome = outcome_value
        
        return ResolvedSignal(
            open_signal=open_signal,
            outcome=outcome,
            exit_price=data["exit_price"],
            pnl=data["pnl"],
            pnl_pct=data["pnl_pct"],
            hold_time=data["hold_time"],
            resolution_time=data["resolution_time"],
        )
    
    def _ensure_paths_exist(self) -> None:
        """Create parent directories if needed.
        
        Ensures that the parent directories for both signal files exist,
        creating them if necessary. Does not create the files themselves.
        
        Example:
            >>> persistence._ensure_paths_exist()
        """
        self.open_signals_path.parent.mkdir(parents=True, exist_ok=True)
        self.resolved_signals_path.parent.mkdir(parents=True, exist_ok=True)
    
    # ========== Cleanup ==========
    
    def cleanup_resolved_signals(self, older_than_days: int = 30) -> int:
        """Delete old resolved signals, return count deleted.
        
        Reads all resolved signals from file, removes those older than the
        specified threshold, and writes the remaining signals back.
        
        Args:
            older_than_days: Signals older than this many days will be deleted (default: 30)
            
        Returns:
            Number of signals deleted
            
        Example:
            >>> deleted = persistence.cleanup_resolved_signals(older_than_days=30)
            >>> print(f"Deleted {deleted} old signals")
        """
        # Load all resolved signals
        signals = self.load_resolved_signals()
        
        if not signals:
            return 0
        
        # Calculate cutoff timestamp (milliseconds)
        cutoff_ts = time.time() - (older_than_days * 24 * 60 * 60)
        
        # Filter out old signals
        kept_signals = [s for s in signals if s.resolution_time > cutoff_ts]
        deleted_count = len(signals) - len(kept_signals)
        
        # Rewrite the file with kept signals
        if kept_signals:
            with open(self.resolved_signals_path, 'w') as f:
                for signal in kept_signals:
                    line = self._serialize_resolved_signal(signal)
                    f.write(line + '\n')
        else:
            # No signals kept, truncate the file
            with open(self.resolved_signals_path, 'w') as f:
                pass  # Empty file
        
        return deleted_count
    
    # ========== Internal Helpers ==========
    
    def _load_signals_from_file(self, file_path: Path, deserializer) -> List:
        """Load signals from a JSONL file using the provided deserializer.
        
        Internal helper that handles file I/O and error handling for loading signals.
        
        Args:
            file_path: Path to the JSONL file
            deserializer: Function to convert JSON line to signal object
            
        Returns:
            List of deserialized signals (empty list if file doesn't exist or is empty)
        """
        signals = []
        
        if not file_path.exists():
            return signals
        
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        signal = deserializer(line)
                        signals.append(signal)
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        # Log but don't fail on corrupt lines
                        print(f"Warning: Skipping corrupt line {line_num} in {file_path}: {e}")
                        continue
        except IOError as e:
            print(f"Warning: Could not read {file_path}: {e}")
        
        return signals
