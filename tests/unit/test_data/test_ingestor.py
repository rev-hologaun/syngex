"""
tests/unit/test_data/test_ingestor.py

Unit tests for TradeStationClient (data ingestor).
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from data.ingestor import TradeStationClient


class TestTradeStationClient:
    """Tests for TradeStationClient."""

    def test_create_client(self):
        """Test client creation."""
        client = TradeStationClient()

        assert client.base_url == "https://api.tradestation.com/v3"
        assert client._is_running is False
        assert client._quote_symbols == []
        assert client._option_chain_symbols == []

    def test_create_client_with_custom_url(self):
        """Test client creation with custom URL."""
        client = TradeStationClient(base_url="https://custom.api.com/v3")

        assert client.base_url == "https://custom.api.com/v3"

    def test_subscribe_to_quotes(self):
        """Test quote subscription."""
        client = TradeStationClient()

        client.subscribe_to_quotes("TSLA")
        client.subscribe_to_quotes("AAPL")
        client.subscribe_to_quotes("TSLA")  # Duplicate

        assert "TSLA" in client._quote_symbols
        assert "AAPL" in client._quote_symbols
        assert len(client._quote_symbols) == 2  # No duplicates

    def test_subscribe_to_option_chain(self):
        """Test option chain subscription."""
        client = TradeStationClient()

        client.subscribe_to_option_chain("TSLA")
        client.subscribe_to_option_chain("TSLA")  # Duplicate

        assert "TSLA" in client._option_chain_symbols
        assert len(client._option_chain_symbols) == 1

    def test_set_on_message_callback(self):
        """Test setting message callback."""
        client = TradeStationClient()

        def callback(msg):
            pass

        client.set_on_message_callback(callback)

        assert client._on_message_callback is not None

    @pytest.mark.asyncio
    async def test_stop_cleans_up(self):
        """Test stop() cleans up resources."""
        client = TradeStationClient()
        client._is_running = True
        client._stream_tasks = []

        # Mock session
        mock_session = AsyncMock()
        mock_session.closed = False
        client._session = mock_session

        await client.stop()

        assert client._is_running is False
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_when_already_stopped(self):
        """Test stop() when already stopped."""
        client = TradeStationClient()
        client._is_running = False
        client._session = None

        await client.stop()  # Should not raise

        assert client._is_running is False

    def test_option_chain_failed_flag(self):
        """Test option chain failed flag."""
        client = TradeStationClient()

        assert client._option_chain_failed is False

        # Simulate failure
        client._option_chain_failed = True

        assert client._option_chain_failed is True
