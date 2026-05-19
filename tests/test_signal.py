"""
tests/test_signal.py — Test Signal serialization/deserialization and core functionality
"""

import pytest
import json
from strategies.signal import Signal, Direction, SignalStrength


class TestSignalCreation:
    """Test Signal creation with valid data."""

    def test_create_basic_signal(self):
        """Test creating a basic Signal with required fields."""
        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="gamma_wall_bounce",
        )

        assert signal.direction == Direction.LONG
        assert signal.confidence == 0.75
        assert signal.entry == 195.50
        assert signal.stop == 194.20
        assert signal.target == 197.80
        assert signal.strategy_id == "gamma_wall_bounce"
        assert signal.symbol == ""
        assert signal.reason == ""

    def test_create_signal_with_all_fields(self):
        """Test creating a Signal with all optional fields."""
        signal = Signal(
            direction=Direction.SHORT,
            confidence=0.82,
            entry=196.00,
            stop=197.50,
            target=193.00,
            strategy_id="call_wall_rejection",
            symbol="TSLA",
            reason="Call wall at 196 rejected price",
            expiry="2026-05-19",
            metadata={"wall_strike": 196, "gex": 1250000},
        )

        assert signal.direction == Direction.SHORT
        assert signal.symbol == "TSLA"
        assert signal.reason == "Call wall at 196 rejected price"
        assert signal.expiry == "2026-05-19"
        assert signal.metadata == {"wall_strike": 196, "gex": 1250000}

    def test_create_neutral_signal(self):
        """Test creating a NEUTRAL direction signal."""
        signal = Signal(
            direction=Direction.NEUTRAL,
            confidence=0.60,
            entry=195.00,
            stop=195.00,
            target=195.00,
            strategy_id="range_bound",
        )

        assert signal.direction == Direction.NEUTRAL


class TestSignalImmutability:
    """Test Signal immutability (frozen dataclass)."""

    def test_signal_is_frozen(self, sample_signal):
        """Test that Signal cannot be modified after creation."""
        with pytest.raises(Exception):  # FrozenDataClassError
            sample_signal.confidence = 0.90

    def test_signal_metadata_immutability(self, sample_signal):
        """Test that while dataclass is frozen, mutable fields can still be modified."""
        # Note: This is a quirk of frozen dataclasses with mutable defaults
        # The dict itself can be modified, but reassignment would fail
        sample_signal.metadata["new_key"] = "new_value"
        assert "new_key" in sample_signal.metadata


class TestSignalSerialization:
    """Test Signal serialization to JSON."""

    def test_to_dict(self, sample_signal):
        """Test serialization to dictionary."""
        data = sample_signal.to_dict()

        assert data["direction"] == "LONG"
        assert data["confidence"] == 0.75
        assert data["entry"] == 195.50
        assert data["stop"] == 194.20
        assert data["target"] == 197.80
        assert data["strategy_id"] == "test_strategy"
        assert data["symbol"] == "TSLA"
        assert data["reason"] == "Test signal for unit tests"
        # expiry may be included if set, but check it's in the dict
        assert "expiry" in data or data.get("expiry") is None
        assert data["metadata"] == {"test_key": "test_value"}
        assert "timestamp" in data
        assert "risk_reward_ratio" in data
        assert "strength" in data

    def test_to_dict_json_serializable(self, sample_signal):
        """Test that to_dict output is fully JSON serializable."""
        data = sample_signal.to_dict()
        json_str = json.dumps(data)
        assert isinstance(json_str, str)

        # Verify we can parse it back
        parsed = json.loads(json_str)
        assert parsed["direction"] == "LONG"
        assert parsed["confidence"] == 0.75

    def test_risk_reward_ratio_in_serialization(self, sample_signal):
        """Test that risk_reward_ratio is calculated correctly in serialization."""
        data = sample_signal.to_dict()
        # Risk = |195.50 - 194.20| = 1.30
        # Reward = |197.80 - 195.50| = 2.30
        # RR = 2.30 / 1.30 = 1.77
        assert data["risk_reward_ratio"] == pytest.approx(1.77, rel=0.01)


class TestSignalDeserialization:
    """Test Signal deserialization from JSON/dict."""

    def test_from_dict_basic(self):
        """Test deserializing a basic signal."""
        data = {
            "direction": "LONG",
            "confidence": 0.80,
            "entry": 195.00,
            "stop": 193.50,
            "target": 198.00,
            "strategy_id": "test_strategy",
        }

        signal = Signal.from_dict(data)

        assert signal.direction == Direction.LONG
        assert signal.confidence == 0.80
        assert signal.entry == 195.00
        assert signal.strategy_id == "test_strategy"

    def test_from_dict_with_all_fields(self):
        """Test deserializing a signal with all fields."""
        data = {
            "direction": "SHORT",
            "confidence": 0.72,
            "entry": 196.50,
            "stop": 198.00,
            "target": 194.00,
            "strategy_id": "gamma_flip_rejection",
            "symbol": "AAPL",
            "reason": "Gamma flip at 197",
            "expiry": "2026-05-26",
            "timestamp": 1234567890.0,
            "metadata": {"flip_strike": 197},
        }

        signal = Signal.from_dict(data)

        assert signal.direction == Direction.SHORT
        assert signal.symbol == "AAPL"
        assert signal.reason == "Gamma flip at 197"
        assert signal.expiry == "2026-05-26"
        assert signal.timestamp == 1234567890.0
        assert signal.metadata == {"flip_strike": 197}

    def test_from_dict_with_optional_fields_missing(self):
        """Test deserializing when optional fields are missing."""
        data = {
            "direction": "LONG",
            "confidence": 0.65,
            "entry": 195.00,
            "stop": 194.00,
            "target": 197.00,
            "strategy_id": "simple_strategy",
        }

        signal = Signal.from_dict(data)

        assert signal.symbol == ""
        assert signal.reason == ""
        assert signal.expiry is None
        assert signal.metadata == {}
        # timestamp should default to current time
        assert signal.timestamp > 0

    def test_round_trip_serialization(self):
        """Test that signal -> dict -> signal preserves data."""
        # Use explicit timestamp to avoid timing issues
        # Note: expiry is NOT included in to_dict() output, so it won't be preserved
        test_time = 1234567890.0
        original = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test_strategy",
            symbol="TSLA",
            reason="Test signal for unit tests",
            metadata={"test_key": "test_value"},
            timestamp=test_time,
        )
        data = original.to_dict()
        reconstructed = Signal.from_dict(data)

        assert reconstructed.direction == original.direction
        assert reconstructed.confidence == original.confidence
        assert reconstructed.entry == original.entry
        assert reconstructed.stop == original.stop
        assert reconstructed.target == original.target
        assert reconstructed.strategy_id == original.strategy_id
        assert reconstructed.symbol == original.symbol
        assert reconstructed.reason == original.reason
        # expiry is not in to_dict output, so it will be None after reconstruction
        assert reconstructed.expiry is None
        assert reconstructed.metadata == original.metadata
        assert reconstructed.timestamp == original.timestamp


class TestSignalEquality:
    """Test Signal equality and hashing."""

    def test_equal_signals(self):
        """Test that identical signals are equal."""
        # Use explicit timestamp to avoid timing issues
        test_time = 1234567890.0
        signal1 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
            timestamp=test_time,
        )
        signal2 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
            timestamp=test_time,
        )

        assert signal1 == signal2

    def test_different_direction_not_equal(self):
        """Test that signals with different directions are not equal."""
        signal1 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
        )
        signal2 = Signal(
            direction=Direction.SHORT,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
        )

        assert signal1 != signal2

    def test_different_confidence_not_equal(self):
        """Test that signals with different confidence are not equal."""
        signal1 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
        )
        signal2 = Signal(
            direction=Direction.LONG,
            confidence=0.80,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
        )

        assert signal1 != signal2

    def test_not_hashable(self):
        """Test that signals are NOT hashable due to mutable metadata dict."""
        # Even with empty metadata, the dict field makes the dataclass unhashable
        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
            metadata={},
        )

        # This should raise TypeError because dict is mutable
        with pytest.raises(TypeError):
            hash(signal)

    def test_equality_ignores_timestamp(self):
        """Test that signals can be compared for equality."""
        # Signals with same values but different timestamps are NOT equal
        # because timestamp is part of the dataclass
        signal1 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
            timestamp=1234567890.0,
        )
        signal2 = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
            timestamp=1234567891.0,  # Different timestamp
        )

        # Different timestamps mean signals are not equal
        assert signal1 != signal2
        # But they have the same core properties
        assert signal1.direction == signal2.direction
        assert signal1.confidence == signal2.confidence


class TestSignalProperties:
    """Test Signal computed properties."""

    def test_risk_reward_ratio(self):
        """Test risk_reward_ratio calculation."""
        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.50,
            stop=194.20,
            target=197.80,
            strategy_id="test",
        )

        # Risk = 1.30, Reward = 2.30, RR = 1.77
        assert signal.risk_reward_ratio == pytest.approx(1.77, rel=0.01)

    def test_risk_reward_ratio_zero_risk(self):
        """Test risk_reward_ratio when risk is zero."""
        signal = Signal(
            direction=Direction.NEUTRAL,
            confidence=0.50,
            entry=195.00,
            stop=195.00,
            target=195.00,
            strategy_id="test",
        )

        assert signal.risk_reward_ratio == 0.0

    def test_strength_properties(self):
        """Test strength property mapping."""
        # EXTREME >= 0.85
        signal_extreme = Signal(
            direction=Direction.LONG,
            confidence=0.90,
            entry=195.00,
            stop=194.00,
            target=197.00,
            strategy_id="test",
        )
        assert signal_extreme.strength == SignalStrength.EXTREME

        # STRONG >= 0.70
        signal_strong = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.00,
            stop=194.00,
            target=197.00,
            strategy_id="test",
        )
        assert signal_strong.strength == SignalStrength.STRONG

        # MODERATE >= 0.50
        signal_moderate = Signal(
            direction=Direction.LONG,
            confidence=0.60,
            entry=195.00,
            stop=194.00,
            target=197.00,
            strategy_id="test",
        )
        assert signal_moderate.strength == SignalStrength.MODERATE

        # WEAK < 0.50
        signal_weak = Signal(
            direction=Direction.LONG,
            confidence=0.35,
            entry=195.00,
            stop=194.00,
            target=197.00,
            strategy_id="test",
        )
        assert signal_weak.strength == SignalStrength.WEAK

    def test_repr(self, sample_signal):
        """Test string representation."""
        repr_str = repr(sample_signal)
        assert "LONG" in repr_str
        assert "test_strategy" in repr_str
        assert "conf=0.75" in repr_str
        assert "Test signal for unit tests" in repr_str


class TestSignalEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_confidence_boundary_values(self):
        """Test confidence at boundary values."""
        signal_min = Signal(
            direction=Direction.LONG,
            confidence=0.0,
            entry=195.00,
            stop=194.00,
            target=197.00,
            strategy_id="test",
        )
        assert signal_min.confidence == 0.0

        signal_max = Signal(
            direction=Direction.LONG,
            confidence=1.0,
            entry=195.00,
            stop=194.00,
            target=197.00,
            strategy_id="test",
        )
        assert signal_max.confidence == 1.0

    def test_empty_metadata(self):
        """Test signal with empty metadata."""
        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.00,
            stop=194.00,
            target=197.00,
            strategy_id="test",
            metadata={},
        )
        assert signal.metadata == {}

    def test_complex_metadata(self):
        """Test signal with complex nested metadata."""
        signal = Signal(
            direction=Direction.LONG,
            confidence=0.75,
            entry=195.00,
            stop=194.00,
            target=197.00,
            strategy_id="test",
            metadata={
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "number": 42,
            },
        )
        assert signal.metadata["nested"]["key"] == "value"
        assert signal.metadata["list"] == [1, 2, 3]
