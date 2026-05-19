"""
tests/unit/test_data/test_stream_processor.py

Unit tests for StreamProcessor.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from data.stream_processor import StreamProcessor


class TestStreamProcessor:
    """Tests for StreamProcessor."""

    def test_create_processor(self):
        """Test processor creation."""
        processor = StreamProcessor()

        assert processor is not None
        assert processor._callbacks == []

    def test_register_callback(self):
        """Test registering a callback."""
        processor = StreamProcessor()

        def callback(data):
            pass

        processor.register_callback(callback)

        assert len(processor._callbacks) == 1

    def test_register_multiple_callbacks(self):
        """Test registering multiple callbacks."""
        processor = StreamProcessor()

        processor.register_callback(lambda x: x)
        processor.register_callback(lambda x: x)
        processor.register_callback(lambda x: x)

        assert len(processor._callbacks) == 3

    def test_process_message_calls_callbacks(self):
        """Test process_message() calls all callbacks."""
        processor = StreamProcessor()

        calls = []
        def make_callback(name):
            def callback(data):
                calls.append(name)
            return callback

        processor.register_callback(make_callback("cb1"))
        processor.register_callback(make_callback("cb2"))

        data = {"type": "test", "value": 123}
        processor.process_message(data)

        assert "cb1" in calls
        assert "cb2" in calls

    def test_process_message_with_no_callbacks(self):
        """Test process_message() with no callbacks."""
        processor = StreamProcessor()

        # Should not raise
        processor.process_message({"type": "test"})

    def test_clear_callbacks(self):
        """Test clearing callbacks."""
        processor = StreamProcessor()

        processor.register_callback(lambda x: x)
        processor.register_callback(lambda x: x)
        processor.clear_callbacks()

        assert len(processor._callbacks) == 0
