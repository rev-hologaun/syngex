"""
tests/unit/test_core/test_orchestrator.py

Unit tests for SyngexOrchestrator lifecycle management.
"""

import asyncio
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

from core.orchestrator import SyngexOrchestrator


logger = logging.getLogger(__name__)


# =============================================================================
# Initialization Tests
# =============================================================================

class TestOrchestratorInitialization:
    """Tests for orchestrator initialization."""

    def test_orchestrator_create(self):
        """Test basic orchestrator creation."""
        orchestrator = SyngexOrchestrator(symbol="TSLA", mode="stream")

        assert orchestrator.symbol == "TSLA"
        assert orchestrator.mode == "stream"
        assert orchestrator._running is False
        assert orchestrator._client is None
        assert orchestrator._calculator is None

    def test_orchestrator_with_dashboard_mode(self):
        """Test orchestrator in dashboard mode."""
        orchestrator = SyngexOrchestrator(symbol="AAPL", mode="dashboard", port=8502)

        assert orchestrator.symbol == "AAPL"
        assert orchestrator.mode == "dashboard"
        assert orchestrator._port == 8502

    def test_orchestrator_correlation_id(self):
        """Test that orchestrator generates unique correlation ID."""
        orch1 = SyngexOrchestrator(symbol="TSLA")
        orch2 = SyngexOrchestrator(symbol="AAPL")

        assert orch1._correlation_id != orch2._correlation_id
        assert len(orch1._correlation_id) == 8


# =============================================================================
# Lifecycle Method Tests
# =============================================================================

class TestOrchestratorLifecycle:
    """Tests for orchestrator lifecycle methods."""

    @pytest.mark.asyncio
    async def test_initialize_creates_components(self):
        """Test that initialize() creates all required components."""
        orchestrator = SyngexOrchestrator(symbol="TSLA")

        with patch.object(orchestrator, '_register_strategies_from_config'):
            await orchestrator.initialize()

        assert orchestrator._calculator is not None
        assert orchestrator._dashboard is not None
        assert orchestrator._client is not None
        assert orchestrator._gamma_profile is not None
        assert orchestrator._gamma_filter is not None
        assert orchestrator._signal_tracker is not None
        assert orchestrator._strategy_engine is not None

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connect() method."""
        orchestrator = SyngexOrchestrator(symbol="TSLA")

        # Mock client
        mock_client = MagicMock()
        async def mock_connect():
            pass
        mock_client.connect = mock_connect
        orchestrator._client = mock_client

        await orchestrator.connect()

        mock_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown(self):
        """Test shutdown() method."""
        orchestrator = SyngexOrchestrator(symbol="TSLA")

        # Mock components
        orchestrator._strategy_engine = MagicMock()
        orchestrator._strategy_engine.stop = MagicMock()
        orchestrator._dashboard_service = MagicMock()
        orchestrator._dashboard_service.stop = MagicMock()
        orchestrator._heatmap_service = MagicMock()
        orchestrator._heatmap_service.stop = MagicMock()
        orchestrator._client = MagicMock()
        async def mock_stop():
            pass
        orchestrator._client.stop = mock_stop
        orchestrator._running = True

        await orchestrator.shutdown()

        assert orchestrator._running is False
        orchestrator._strategy_engine.stop.assert_called_once()
        orchestrator._dashboard_service.stop.assert_called_once()
        orchestrator._heatmap_service.stop.assert_called_once()


# =============================================================================
# Strategy Registration Tests
# =============================================================================

class TestOrchestratorStrategyRegistration:
    """Tests for strategy registration."""

    @pytest.mark.asyncio
    async def test_register_strategies_from_config(self):
        """Test strategy registration from config."""
        orchestrator = SyngexOrchestrator(symbol="TSLA")

        # Mock strategy engine
        mock_engine = MagicMock()
        orchestrator._strategy_engine = mock_engine

        # Mock config
        orchestrator._strategy_config = {
            "layer1": {
                "gamma_wall_bounce": {"enabled": True},
            },
            "layer2": {},
            "layer3": {},
            "full_data": {},
        }

        orchestrator._register_strategies_from_config()

        # Should register enabled strategies
        assert mock_engine.register.called
