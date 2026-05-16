"""tests/test_signal_persistence — Comprehensive tests for SignalPersistence class."""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from data.signal_persistence import SignalPersistence
from strategies.signal_tracker import OpenSignal, ResolvedSignal, SignalOutcome


# ========== Test Fixtures ==========

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def persistence(temp_dir):
    """Create a SignalPersistence instance with temp files."""
    open_path = temp_dir / "open_signals.jsonl"
    resolved_path = temp_dir / "resolved_signals.jsonl"
    
    return SignalPersistence(
        open_signals_path=open_path,
        resolved_signals_path=resolved_path,
        flush_interval_seconds=60.0,
        max_buffer_size=1000,
    )


@pytest.fixture
def sample_open_signal():
    """Create a sample OpenSignal for testing."""
    return OpenSignal(
        signal_id="test-signal-001",
        direction="LONG",
        strategy_id="gamma_wall_bounce",
        entry=245.50,
        stop=243.00,
        target=250.00,
        confidence=0.75,
        timestamp=1715822400000,
        reason="Wall bounce detected",
        metadata={"test_key": "test_value"},
        max_hold_seconds=900,
        risk=2.50,
        reward=4.50,
        rr_ratio=1.8,
    )


@pytest.fixture
def sample_resolved_signal(sample_open_signal):
    """Create a sample ResolvedSignal for testing."""
    return ResolvedSignal(
        open_signal=sample_open_signal,
        outcome=SignalOutcome.WIN,
        exit_price=250.00,
        pnl=4.50,
        pnl_pct=1.83,
        hold_time=600.0,
        resolution_time=1715823000000,
    )


# ========== Test: Serialization/Deserialization ==========

class TestSerialization:
    """Test signal serialization and deserialization."""
    
    def test_serialize_open_signal(self, persistence, sample_open_signal):
        """Test OpenSignal serialization to JSON line."""
        json_line = persistence._serialize_open_signal(sample_open_signal)
        
        # Verify it's valid JSON
        data = json.loads(json_line)
        
        # Verify key fields
        assert data["signal_id"] == "test-signal-001"
        assert data["strategy_id"] == "gamma_wall_bounce"
        assert data["direction"] == "LONG"
        assert data["entry"] == 245.50
        assert data["metadata"]["test_key"] == "test_value"
    
    def test_serialize_resolved_signal(self, persistence, sample_resolved_signal):
        """Test ResolvedSignal serialization to JSON line."""
        json_line = persistence._serialize_resolved_signal(sample_resolved_signal)
        
        # Verify it's valid JSON
        data = json.loads(json_line)
        
        # Verify key fields
        assert data["outcome"] == "WIN"
        assert data["exit_price"] == 250.00
        assert data["pnl"] == 4.50
        assert data["pnl_pct"] == 1.83
        assert data["open_signal"]["signal_id"] == "test-signal-001"
    
    def test_deserialize_open_signal(self, persistence, sample_open_signal):
        """Test deserializing JSON line to OpenSignal."""
        json_line = persistence._serialize_open_signal(sample_open_signal)
        deserialized = persistence._deserialize_open_signal(json_line)
        
        # Verify all fields match
        assert deserialized.signal_id == sample_open_signal.signal_id
        assert deserialized.strategy_id == sample_open_signal.strategy_id
        assert deserialized.direction == sample_open_signal.direction
        assert deserialized.entry == sample_open_signal.entry
        assert deserialized.metadata == sample_open_signal.metadata
    
    def test_deserialize_resolved_signal(self, persistence, sample_resolved_signal):
        """Test deserializing JSON line to ResolvedSignal."""
        json_line = persistence._serialize_resolved_signal(sample_resolved_signal)
        deserialized = persistence._deserialize_resolved_signal(json_line)
        
        # Verify all fields match
        assert deserialized.open_signal.signal_id == sample_resolved_signal.open_signal.signal_id
        assert deserialized.outcome == sample_resolved_signal.outcome
        assert deserialized.exit_price == sample_resolved_signal.exit_price
        assert deserialized.pnl == sample_resolved_signal.pnl
    
    def test_round_trip_open_signal(self, persistence, sample_open_signal):
        """Test that serialize -> deserialize produces identical signal."""
        # Serialize and deserialize
        json_line = persistence._serialize_open_signal(sample_open_signal)
        deserialized = persistence._deserialize_open_signal(json_line)
        
        # Verify all fields match
        assert deserialized.signal_id == sample_open_signal.signal_id
        assert deserialized.direction == sample_open_signal.direction
        assert deserialized.strategy_id == sample_open_signal.strategy_id
        assert deserialized.entry == sample_open_signal.entry
        assert deserialized.stop == sample_open_signal.stop
        assert deserialized.target == sample_open_signal.target
        assert deserialized.confidence == sample_open_signal.confidence
        assert deserialized.timestamp == sample_open_signal.timestamp
        assert deserialized.reason == sample_open_signal.reason
        assert deserialized.metadata == sample_open_signal.metadata
        assert deserialized.max_hold_seconds == sample_open_signal.max_hold_seconds
        assert deserialized.risk == sample_open_signal.risk
        assert deserialized.reward == sample_open_signal.reward
        assert deserialized.rr_ratio == sample_open_signal.rr_ratio
    
    def test_round_trip_resolved_signal(self, persistence, sample_resolved_signal):
        """Test that serialize -> deserialize produces identical signal."""
        # Serialize and deserialize
        json_line = persistence._serialize_resolved_signal(sample_resolved_signal)
        deserialized = persistence._deserialize_resolved_signal(json_line)
        
        # Verify all fields match
        assert deserialized.open_signal.signal_id == sample_resolved_signal.open_signal.signal_id
        assert deserialized.outcome == sample_resolved_signal.outcome
        assert deserialized.exit_price == sample_resolved_signal.exit_price
        assert deserialized.pnl == sample_resolved_signal.pnl
        assert deserialized.pnl_pct == sample_resolved_signal.pnl_pct
        assert deserialized.hold_time == sample_resolved_signal.hold_time
        assert deserialized.resolution_time == sample_resolved_signal.resolution_time


# ========== Test: File I/O ==========

class TestFileIO:
    """Test file read/write operations."""
    
    def test_save_open_signal_to_file(self, persistence, sample_open_signal):
        """Test saving open signal writes to file."""
        # Save signal
        persistence.save_open_signal(sample_open_signal)
        persistence.flush()
        
        # Verify file exists and contains the signal
        assert persistence.open_signals_path.exists()
        
        with open(persistence.open_signals_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["signal_id"] == sample_open_signal.signal_id
    
    def test_save_resolved_signal_to_file(self, persistence, sample_resolved_signal):
        """Test saving resolved signal writes to file."""
        # Save signal
        persistence.save_resolved_signal(sample_resolved_signal)
        persistence.flush()
        
        # Verify file exists and contains the signal
        assert persistence.resolved_signals_path.exists()
        
        with open(persistence.resolved_signals_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["open_signal"]["signal_id"] == sample_resolved_signal.open_signal.signal_id
    
    def test_load_open_signals_from_file(self, persistence, sample_open_signal):
        """Test loading open signals from file."""
        # Write signal to file manually
        persistence.open_signals_path.parent.mkdir(parents=True, exist_ok=True)
        with open(persistence.open_signals_path, 'w') as f:
            f.write(persistence._serialize_open_signal(sample_open_signal) + '\n')
        
        # Load signals
        signals = persistence.load_open_signals()
        
        assert len(signals) == 1
        assert signals[0].signal_id == sample_open_signal.signal_id
        assert signals[0].entry == sample_open_signal.entry
    
    def test_load_resolved_signals_from_file(self, persistence, sample_resolved_signal):
        """Test loading resolved signals from file."""
        # Write signal to file manually
        persistence.resolved_signals_path.parent.mkdir(parents=True, exist_ok=True)
        with open(persistence.resolved_signals_path, 'w') as f:
            f.write(persistence._serialize_resolved_signal(sample_resolved_signal) + '\n')
        
        # Load signals
        signals = persistence.load_resolved_signals()
        
        assert len(signals) == 1
        assert signals[0].open_signal.signal_id == sample_resolved_signal.open_signal.signal_id
        assert signals[0].pnl == sample_resolved_signal.pnl
    
    def test_load_nonexistent_file_returns_empty_list(self, persistence):
        """Test that loading from non-existent file returns empty list."""
        open_signals = persistence.load_open_signals()
        resolved_signals = persistence.load_resolved_signals()
        
        assert open_signals == []
        assert resolved_signals == []
    
    def test_load_empty_file_returns_empty_list(self, persistence):
        """Test that loading from empty file returns empty list."""
        # Create empty files
        persistence.open_signals_path.parent.mkdir(parents=True, exist_ok=True)
        persistence.open_signals_path.touch()
        persistence.resolved_signals_path.touch()
        
        open_signals = persistence.load_open_signals()
        resolved_signals = persistence.load_resolved_signals()
        
        assert open_signals == []
        assert resolved_signals == []
    
    def test_save_multiple_signals(self, persistence):
        """Test saving multiple signals appends to file."""
        # Create and save multiple signals
        for i in range(5):
            signal = OpenSignal(
                signal_id=f"signal-{i}",
                direction="LONG",
                strategy_id="test",
                entry=100.0 + i,
                stop=95.0,
                target=110.0,
                confidence=0.8,
                timestamp=1715822400000 + i * 1000,
                reason="Test",
            )
            persistence.save_open_signal(signal)
        
        persistence.flush()
        
        # Verify all signals are in file
        signals = persistence.load_open_signals()
        assert len(signals) == 5
        
        # Verify signal IDs
        signal_ids = [s.signal_id for s in signals]
        for i in range(5):
            assert f"signal-{i}" in signal_ids
    
    def test_ensure_paths_exist_creates_directories(self, temp_dir):
        """Test that _ensure_paths_exist creates parent directories."""
        deep_path = temp_dir / "deep" / "nested" / "path" / "signals.jsonl"
        
        persistence = SignalPersistence(
            open_signals_path=deep_path,
            resolved_signals_path=temp_dir / "resolved.jsonl",
        )
        
        # This should not raise an error
        persistence._ensure_paths_exist()
        
        # Verify directory was created
        assert (temp_dir / "deep" / "nested" / "path").exists()


# ========== Test: Buffer Flush ==========

class TestBufferFlush:
    """Test buffer flush logic."""
    
    def test_flush_writes_buffered_signals(self, persistence, sample_open_signal):
        """Test that flush writes all buffered signals to disk."""
        # Add signals to buffer (don't trigger auto-flush)
        persistence.max_buffer_size = 1000
        persistence.flush_interval_seconds = 3600  # 1 hour
        
        persistence.save_open_signal(sample_open_signal)
        
        # Buffer should have the signal but file should be empty
        assert len(persistence._open_buffer) == 1
        assert not persistence.open_signals_path.exists()
        
        # Flush
        persistence.flush()
        
        # Buffer should be empty, file should have signal
        assert len(persistence._open_buffer) == 0
        assert persistence.open_signals_path.exists()
        
        signals = persistence.load_open_signals()
        assert len(signals) == 1
    
    def test_flush_clears_both_buffers(self, persistence, sample_open_signal, sample_resolved_signal):
        """Test that flush clears both open and resolved buffers."""
        persistence.max_buffer_size = 1000
        persistence.flush_interval_seconds = 3600
        
        persistence.save_open_signal(sample_open_signal)
        persistence.save_resolved_signal(sample_resolved_signal)
        
        assert len(persistence._open_buffer) == 1
        assert len(persistence._resolved_buffer) == 1
        
        persistence.flush()
        
        assert len(persistence._open_buffer) == 0
        assert len(persistence._resolved_buffer) == 0
    
    def test_flush_if_needed_by_buffer_size(self, persistence):
        """Test that flush_if_needed triggers when buffer is full."""
        # Set small buffer size
        persistence.max_buffer_size = 3
        
        # Add signals up to limit
        for i in range(3):
            signal = OpenSignal(
                signal_id=f"signal-{i}",
                direction="LONG",
                strategy_id="test",
                entry=100.0,
                stop=95.0,
                target=110.0,
                confidence=0.8,
                timestamp=1715822400000,
                reason="Test",
            )
            persistence.save_open_signal(signal)
        
        # Should have flushed automatically
        assert len(persistence._open_buffer) == 0
        assert persistence.open_signals_path.exists()
    
    def test_flush_if_needed_by_time_elapsed(self, persistence, sample_open_signal, monkeypatch):
        """Test that flush_if_needed triggers when time elapsed."""
        # Set short flush interval
        persistence.flush_interval_seconds = 0.1  # 100ms
        
        # Mock time to simulate elapsed time
        import time
        original_time = time.time
        time_counter = [time.time()]
        
        def mock_time():
            time_counter[0] += 0.2  # Advance by 200ms
            return time_counter[0]
        
        monkeypatch.setattr(time, 'time', mock_time)
        
        # Add signal
        persistence.save_open_signal(sample_open_signal)
        
        # Should have flushed due to time elapsed
        assert len(persistence._open_buffer) == 0


# ========== Test: Cleanup ==========

class TestCleanup:
    """Test resolved signal cleanup."""
    
    def test_cleanup_removes_old_signals(self, persistence):
        """Test that cleanup removes signals older than threshold."""
        import time
        current_time = time.time()
        
        # Create signals with different ages
        recent_signal = OpenSignal(
            signal_id="recent-1",
            direction="LONG",
            strategy_id="test",
            entry=100.0,
            stop=95.0,
            target=110.0,
            confidence=0.8,
            timestamp=current_time * 1000 - (10 * 24 * 60 * 60 * 1000),
            reason="Recent",
        )
        
        recent_resolved = ResolvedSignal(
            open_signal=recent_signal,
            outcome=SignalOutcome.WIN,
            exit_price=105.0,
            pnl=5.0,
            pnl_pct=5.0,
            hold_time=60.0,
            resolution_time=current_time - (10 * 24 * 60 * 60),  # 10 days ago
        )
        
        old_signal = OpenSignal(
            signal_id="old-1",
            direction="LONG",
            strategy_id="test",
            entry=100.0,
            stop=95.0,
            target=110.0,
            confidence=0.8,
            timestamp=current_time * 1000 - (45 * 24 * 60 * 60 * 1000),
            reason="Old",
        )
        
        old_resolved = ResolvedSignal(
            open_signal=old_signal,
            outcome=SignalOutcome.LOSS,
            exit_price=95.0,
            pnl=-5.0,
            pnl_pct=-5.0,
            hold_time=60.0,
            resolution_time=current_time - (45 * 24 * 60 * 60),  # 45 days ago
        )
        
        # Write signals to file
        persistence.resolved_signals_path.parent.mkdir(parents=True, exist_ok=True)
        with open(persistence.resolved_signals_path, 'w') as f:
            f.write(persistence._serialize_resolved_signal(recent_resolved) + '\n')
            f.write(persistence._serialize_resolved_signal(old_resolved) + '\n')
        
        # Run cleanup with 30-day threshold
        deleted_count = persistence.cleanup_resolved_signals(older_than_days=30)
        
        # Verify
        assert deleted_count == 1
        
        remaining = persistence.load_resolved_signals()
        assert len(remaining) == 1
        assert remaining[0].open_signal.signal_id == "recent-1"
    
    def test_cleanup_returns_zero_when_no_signals(self, persistence):
        """Test that cleanup returns 0 when no signals exist."""
        deleted_count = persistence.cleanup_resolved_signals()
        assert deleted_count == 0
    
    def test_cleanup_deletes_all_if_all_old(self, persistence):
        """Test cleanup when all signals are old."""
        import time
        current_time = time.time()
        
        # Create old signal
        old_signal = OpenSignal(
            signal_id="very-old",
            direction="LONG",
            strategy_id="test",
            entry=100.0,
            stop=95.0,
            target=110.0,
            confidence=0.8,
            timestamp=current_time * 1000 - (100 * 24 * 60 * 60 * 1000),
            reason="Very old",
        )
        
        old_resolved = ResolvedSignal(
            open_signal=old_signal,
            outcome=SignalOutcome.LOSS,
            exit_price=95.0,
            pnl=-5.0,
            pnl_pct=-5.0,
            hold_time=60.0,
            resolution_time=current_time - (100 * 24 * 60 * 60),  # 100 days ago
        )
        
        persistence.resolved_signals_path.parent.mkdir(parents=True, exist_ok=True)
        with open(persistence.resolved_signals_path, 'w') as f:
            f.write(persistence._serialize_resolved_signal(old_resolved) + '\n')
        
        deleted_count = persistence.cleanup_resolved_signals(older_than_days=30)
        assert deleted_count == 1
        
        remaining = persistence.load_resolved_signals()
        assert len(remaining) == 0


# ========== Test: Error Handling ==========

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_corrupt_json_line_skipped(self, persistence):
        """Test that corrupt JSON lines are skipped with warning."""
        persistence.open_signals_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(persistence.open_signals_path, 'w') as f:
            # Write a valid signal first
            signal = OpenSignal(
                signal_id="valid-1",
                direction="LONG",
                strategy_id="test",
                entry=100.0,
                stop=95.0,
                target=110.0,
                confidence=0.8,
                timestamp=1715822400000,
                reason="Valid",
            )
            f.write(persistence._serialize_open_signal(signal) + '\n')
            f.write('not valid json\n')
            f.write('{"also_invalid": true}\n')  # Missing required fields
        
        # Should not raise, just skip corrupt lines
        signals = persistence.load_open_signals()
        
        # Should have loaded the valid line
        assert len(signals) == 1
        assert signals[0].signal_id == "valid-1"
    
    def test_missing_required_field_raises_keyerror(self, persistence):
        """Test that missing required fields raise KeyError."""
        json_line = '{"signal_id": "test"}'  # Missing many required fields
        
        with pytest.raises(KeyError):
            persistence._deserialize_open_signal(json_line)
    
    def test_invalid_enum_value_raises_valueerror(self, persistence):
        """Test that invalid enum values raise ValueError."""
        # Create a valid signal first, then modify outcome
        signal = OpenSignal(
            signal_id="test-001",
            direction="LONG",
            strategy_id="test",
            entry=100.0,
            stop=95.0,
            target=110.0,
            confidence=0.8,
            timestamp=1715822400000,
            reason="Test",
        )
        
        resolved = ResolvedSignal(
            open_signal=signal,
            outcome=SignalOutcome.WIN,
            exit_price=105.0,
            pnl=5.0,
            pnl_pct=5.0,
            hold_time=60.0,
            resolution_time=1715823000000,
        )
        
        # Serialize and corrupt the outcome
        json_line = persistence._serialize_resolved_signal(resolved)
        data = json.loads(json_line)
        data["outcome"] = "INVALID_OUTCOME"
        corrupted_line = json.dumps(data)
        
        with pytest.raises(ValueError):
            persistence._deserialize_resolved_signal(corrupted_line)
    
    def test_io_error_on_unreadable_file(self, temp_dir):
        """Test handling of file I/O errors."""
        open_path = temp_dir / "open.jsonl"
        resolved_path = temp_dir / "resolved.jsonl"
        
        persistence = SignalPersistence(
            open_signals_path=open_path,
            resolved_signals_path=resolved_path,
        )
        
        # Should return empty list for non-existent file
        signals = persistence.load_open_signals()
        assert signals == []


# ========== Test: Integration ==========

class TestIntegration:
    """Integration tests for full workflow."""
    
    def test_full_open_signal_lifecycle(self, persistence):
        """Test complete open signal lifecycle: save, flush, load."""
        # Create and save signal
        signal = OpenSignal(
            signal_id="lifecycle-test-001",
            direction="LONG",
            strategy_id="gamma_wall_bounce",
            entry=245.50,
            stop=243.00,
            target=250.00,
            confidence=0.75,
            timestamp=1715822400000,
            reason="Wall bounce detected",
        )
        
        persistence.save_open_signal(signal)
        persistence.flush()
        
        # Load and verify
        loaded_signals = persistence.load_open_signals()
        assert len(loaded_signals) == 1
        
        loaded = loaded_signals[0]
        assert loaded.signal_id == signal.signal_id
        assert loaded.strategy_id == signal.strategy_id
        assert loaded.direction == signal.direction
        assert loaded.entry == signal.entry
    
    def test_full_resolved_signal_lifecycle(self, persistence):
        """Test complete resolved signal lifecycle: save, flush, load."""
        # Create open signal first
        open_signal = OpenSignal(
            signal_id="resolved-lifecycle-001",
            direction="LONG",
            strategy_id="gamma_wall_bounce",
            entry=245.50,
            stop=243.00,
            target=250.00,
            confidence=0.75,
            timestamp=1715822400000,
            reason="Wall bounce detected",
        )
        
        # Create resolved signal
        resolved_signal = ResolvedSignal(
            open_signal=open_signal,
            outcome=SignalOutcome.WIN,
            exit_price=250.00,
            pnl=4.50,
            pnl_pct=1.83,
            hold_time=600.0,
            resolution_time=1715823000000,
        )
        
        persistence.save_resolved_signal(resolved_signal)
        persistence.flush()
        
        # Load and verify
        loaded_signals = persistence.load_resolved_signals()
        assert len(loaded_signals) == 1
        
        loaded = loaded_signals[0]
        assert loaded.open_signal.signal_id == resolved_signal.open_signal.signal_id
        assert loaded.exit_price == resolved_signal.exit_price
        assert loaded.pnl == resolved_signal.pnl
        assert loaded.outcome == resolved_signal.outcome
    
    def test_mixed_open_and_resolved_signals(self, persistence):
        """Test handling both open and resolved signals together."""
        open_signal = OpenSignal(
            signal_id="open-001",
            direction="LONG",
            strategy_id="test",
            entry=100.0,
            stop=95.0,
            target=110.0,
            confidence=0.8,
            timestamp=1715822400000,
            reason="Test",
        )
        
        resolved_signal = ResolvedSignal(
            open_signal=OpenSignal(
                signal_id="resolved-001",
                direction="SHORT",
                strategy_id="test",
                entry=110.0,
                stop=115.0,
                target=100.0,
                confidence=0.8,
                timestamp=1715822400000,
                reason="Test",
            ),
            outcome=SignalOutcome.WIN,
            exit_price=100.0,
            pnl=10.0,
            pnl_pct=9.09,
            hold_time=600.0,
            resolution_time=1715823000000,
        )
        
        # Save both
        persistence.save_open_signal(open_signal)
        persistence.save_resolved_signal(resolved_signal)
        persistence.flush()
        
        # Load both
        open_signals = persistence.load_open_signals()
        resolved_signals = persistence.load_resolved_signals()
        
        assert len(open_signals) == 1
        assert len(resolved_signals) == 1
        assert open_signals[0].signal_id == "open-001"
        assert resolved_signals[0].open_signal.signal_id == "resolved-001"
        assert open_signals[0].direction == "LONG"
        assert resolved_signals[0].open_signal.direction == "SHORT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
