"""
tests/unit/test_data/test_token_manager.py

Unit tests for TokenManager.
"""

import pytest
from unittest.mock import MagicMock, patch
from data.token_manager import TokenManager


class TestTokenManager:
    """Tests for TokenManager."""

    def test_create_token_manager(self):
        """Test token manager creation."""
        manager = TokenManager()

        assert manager is not None
        assert manager._token is None
        assert manager._token_expires_at is None

    @pytest.mark.asyncio
    async def test_get_token_loads_from_file(self):
        """Test get_token() loads from file."""
        manager = TokenManager()

        # Mock file exists and has token
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', MagicMock(read=MagicMock(return_value="test_token_123"))):
                token = await manager.get_token()

                assert token == "test_token_123"

    @pytest.mark.asyncio
    async def test_get_token_returns_cached(self):
        """Test get_token() returns cached token."""
        manager = TokenManager()
        manager._token = "cached_token"
        manager._token_expires_at = 9999999999.0  # Far future

        token = await manager.get_token()

        assert token == "cached_token"

    def test_is_token_expired(self):
        """Test _is_token_expired()."""
        manager = TokenManager()
        import time

        # Not expired
        manager._token_expires_at = time.time() + 3600
        assert manager._is_token_expired() is False

        # Expired
        manager._token_expires_at = time.time() - 100
        assert manager._is_token_expired() is True

        # No expiry set
        manager._token_expires_at = None
        assert manager._is_token_expired() is True

    def test_set_token_and_expiry(self):
        """Test setting token and expiry."""
        manager = TokenManager()
        import time

        manager._set_token_and_expiry("new_token", time.time() + 3600)

        assert manager._token == "new_token"
        assert manager._token_expires_at is not None
