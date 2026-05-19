"""
tests/conftest.py — Pytest fixtures for Syngex test suite

Provides shared fixtures for all test modules including:
- Mock components (GEXCalculator, StrategyEngine, etc.)
- Sample data fixtures
- Mock TradeStation client
- Configuration fixtures
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Generator, Optional
from unittest.mock import MagicMock, Mock

import pytest

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Logging Setup for Tests
# =============================================================================

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    # Reduce noise from third-party libraries
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV data for testing."""
    from tests.fixtures.sample_gex_data import SAMPLE_OHLCV_DATA
    return SAMPLE_OHLCV_DATA


@pytest.fixture
def sample_option_chain():
    """Sample option chain data for testing."""
    from tests.fixtures.sample_gex_data import SAMPLE_OPTION_CHAIN
    return SAMPLE_OPTION_CHAIN


@pytest.fixture
def sample_gex_snapshot_positive():
    """Sample GEX snapshot in positive regime."""
    from tests.fixtures.sample_gex_data import SAMPLE_GEX_SNAPSHOT_POSITIVE_REGIME
    return SAMPLE_GEX_SNAPSHOT_POSITIVE_REGIME


@pytest.fixture
def sample_gex_snapshot_negative():
    """Sample GEX snapshot in negative regime."""
    from tests.fixtures.sample_gex_data import SAMPLE_GEX_SNAPSHOT_NEGATIVE_REGIME
    return SAMPLE_GEX_SNAPSHOT_NEGATIVE_REGIME


@pytest.fixture
def sample_gamma_walls():
    """Sample gamma walls data."""
    from tests.fixtures.sample_gex_data import SAMPLE_GAMMA_WALLS
    return SAMPLE_GAMMA_WALLS


# =============================================================================
# Signal Fixtures
# =============================================================================

@pytest.fixture
def sample_signal():
    """Create a sample Signal for testing."""
    from strategies.signal import Direction, Signal
    import time

    return Signal(
        direction=Direction.LONG,
        confidence=0.75,
        entry=195.50,
        stop=194.20,
        target=197.80,
        strategy_id="test_strategy",
        symbol="TSLA",
        reason="Test signal for unit tests",
        timestamp=time.time(),
        expiry="2024-05-19",
        metadata={"test_key": "test_value"},
    )


@pytest.fixture
def sample_signals_list():
    """List of sample signals for testing."""
    from tests.fixtures.sample_signals import SAMPLE_SIGNAL_LIST
    return SAMPLE_SIGNAL_LIST


@pytest.fixture
def sample_open_signal():
    """Sample OpenSignal object."""
    from tests.fixtures.sample_signals import SAMPLE_OPEN_SIGNAL
    return SAMPLE_OPEN_SIGNAL


@pytest.fixture
def sample_resolved_signal():
    """Sample ResolvedSignal object."""
    from tests.fixtures.sample_signals import SAMPLE_RESOLVED_SIGNAL_TP
    return SAMPLE_RESOLVED_SIGNAL_TP


# =============================================================================
# Component Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_gex_calculator() -> MagicMock:
    """Mock GEXCalculator with test data."""
    from engine.gex_calculator import GEXCalculator

    mock = MagicMock(spec=GEXCalculator)
    mock.symbol = "TSLA"
    mock.underlying_price = 195.50
    mock._msg_count = 100
    mock._option_count = 50

    # Mock methods
    mock.get_net_gamma.return_value = 1250.5
    mock.get_gamma_flip.return_value = 194.0
    mock.get_gamma_walls.return_value = [
        {"strike": 200.0, "net_gamma": 2500.0, "gex": 487500.0, "side": "call"},
        {"strike": 195.0, "net_gamma": -1800.0, "gex": -351000.0, "side": "put"},
    ]
    mock.get_greeks_summary.return_value = {
        "net_delta": 1250.5,
        "net_gamma": 1250.5,
        "total_volume": 15000,
        "underlying_price": 195.50,
    }
    mock.get_iv_by_strike_avg.return_value = {
        190.0: 0.52,
        195.0: 0.48,
        200.0: 0.45,
    }
    mock.get_iv_skew.return_value = 0.03
    mock.get_delta_by_strike.return_value = {"net_delta": 125.5}
    mock.get_atm_strike.return_value = 195.0
    mock.get_gamma_profile.return_value = {
        "underlying_price": 195.50,
        "net_gamma": 1250.5,
        "strikes": {
            190.0: {"net_gamma": 50.0},
            195.0: {"net_gamma": 16.2},
            200.0: {"net_gamma": 18.0},
        },
    }

    return mock


@pytest.fixture
def sample_gex_calculator():
    """Create a real GEXCalculator instance for integration tests."""
    from engine.gex_calculator import GEXCalculator

    calc = GEXCalculator(symbol="TSLA")
    calc.set_underlying_price(195.50)
    return calc


@pytest.fixture
def mock_strategy_engine() -> MagicMock:
    """Mock StrategyEngine for testing."""
    from strategies.engine import StrategyEngine, EngineConfig

    mock = MagicMock(spec=StrategyEngine)
    mock.config = EngineConfig(min_confidence=0.40, max_signals_per_tick=10)
    mock._strategies = []
    mock._running = False
    mock._signal_count = 0
    mock._tick_count = 0

    # Mock methods
    mock.register = MagicMock()
    mock.register_filter = MagicMock()
    mock.start = MagicMock()
    mock.stop = MagicMock()
    mock.process = MagicMock(return_value=[])
    mock.get_status.return_value = {
        "running": False,
        "strategies": 0,
        "total_signals": 0,
        "ticks_processed": 0,
    }
    mock.get_recent_signals.return_value = []
    mock.strategy_count = 0
    mock.signal_count = 0

    return mock


@pytest.fixture
def sample_strategy_engine():
    """Create a real StrategyEngine instance."""
    from strategies.engine import StrategyEngine, EngineConfig

    config = EngineConfig(min_confidence=0.40, max_signals_per_tick=10)
    return StrategyEngine(config=config)


@pytest.fixture
def mock_signal_tracker() -> MagicMock:
    """Mock SignalTracker for testing."""
    from strategies.signal_tracker import SignalTracker

    mock = MagicMock(spec=SignalTracker)
    mock._max_hold_seconds = 900
    mock._strategy_hold_times = {}
    mock._open_signals = {}
    mock._resolved_signals = []

    # Mock methods
    mock.track_signal = MagicMock(return_value=None)
    mock.update = MagicMock(return_value=[])
    mock.get_open_signals = MagicMock(return_value=[])
    mock.get_resolved_signals = MagicMock(return_value=[])
    mock.get_stats = MagicMock(return_value={
        "total_signals": 0,
        "resolved_signals": 0,
        "take_profits": 0,
        "stop_losses": 0,
        "expired": 0,
        "win_rate": 0.0,
    })

    return mock


@pytest.fixture
def sample_signal_tracker():
    """Create a real SignalTracker instance."""
    from strategies.signal_tracker import SignalTracker
    from pathlib import Path

    log_dir = Path(__file__).parent.parent / "log"
    log_dir.mkdir(exist_ok=True)

    return SignalTracker(
        max_hold_seconds=900,
        strategy_hold_times={},
        log_dir=str(log_dir),
        symbol="TSLA",
        signal_log_path=str(log_dir / "signals.jsonl"),
    )


@pytest.fixture
def mock_orchestrator() -> MagicMock:
    """Mock SyngexOrchestrator for testing."""
    from core.orchestrator import SyngexOrchestrator

    mock = MagicMock(spec=SyngexOrchestrator)
    mock.symbol = "TSLA"
    mock.mode = "stream"
    mock._running = False
    mock._correlation_id = "test123"

    # Mock lifecycle methods
    mock.initialize = MagicMock()
    mock.connect = MagicMock()
    mock.run = MagicMock()
    mock.shutdown = MagicMock()

    # Mock components
    mock._client = None
    mock._calculator = None
    mock._strategy_engine = None
    mock._signal_tracker = None
    mock._gamma_filter = None
    mock._gamma_profile = None

    return mock


@pytest.fixture
def sample_orchestrator():
    """Create a real SyngexOrchestrator instance (minimal setup)."""
    from core.orchestrator import SyngexOrchestrator

    orchestrator = SyngexOrchestrator(symbol="TSLA", mode="stream")
    return orchestrator


@pytest.fixture
def mock_health_service() -> MagicMock:
    """Mock HealthCheckService for testing."""
    from services.health_service import HealthCheckService

    mock = MagicMock(spec=HealthCheckService)
    mock.is_healthy = MagicMock(return_value=True)
    mock.get_status = MagicMock(return_value={
        "status": "healthy",
        "uptime": 3600,
        "components": {
            "gex_calculator": "healthy",
            "strategy_engine": "healthy",
            "signal_tracker": "healthy",
        },
    })

    return mock


@pytest.fixture
def mock_dashboard_service() -> MagicMock:
    """Mock DashboardService for testing."""
    from services.dashboard_service import DashboardService

    mock = MagicMock(spec=DashboardService)
    mock.start = MagicMock()
    mock.stop = MagicMock()
    mock.is_running = MagicMock(return_value=False)
    mock._process = None

    return mock


@pytest.fixture
def mock_heatmap_service() -> MagicMock:
    """Mock HeatmapService for testing."""
    from services.heatmap_service import HeatmapService

    mock = MagicMock(spec=HeatmapService)
    mock.start = MagicMock()
    mock.stop = MagicMock()
    mock.is_running = MagicMock(return_value=False)
    mock._process = None

    return mock


@pytest.fixture
def mock_state_exporter() -> MagicMock:
    """Mock StateExporter for testing."""
    from services.state_exporter import StateExporter

    mock = MagicMock(spec=StateExporter)
    mock.export = MagicMock()
    mock._data_dir = Path("/tmp/test_data")
    mock._calculator_ref = None
    mock._strategy_engine_ref = None

    return mock


# =============================================================================
# TradeStation Client Mock
# =============================================================================

@pytest.fixture
def mock_trade_station() -> MagicMock:
    """Mock TradeStation client for testing."""
    from data.ingestor import TradeStationClient

    mock = MagicMock(spec=TradeStationClient)
    mock.base_url = "https://api.tradestation.com/v3"
    mock._is_running = False
    mock._option_chain_failed = False
    mock._quote_symbols = []
    mock._option_chain_symbols = []
    mock._on_message_callback = None

    # Mock methods
    mock.connect = MagicMock()
    mock.stop = MagicMock()
    mock.subscribe_to_quotes = MagicMock()
    mock.subscribe_to_option_chain = MagicMock()
    mock.set_on_message_callback = MagicMock()

    return mock


@pytest.fixture
def mock_trade_station_client() -> MagicMock:
    """Alternative mock TradeStation client."""
    return mock_trade_station()


# =============================================================================
# Configuration Fixtures
# =============================================================================

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock configuration dictionary."""
    return {
        "global": {
            "min_confidence": 0.35,
            "max_signals_per_tick": 10,
            "signal_log_path": "log/signals.jsonl",
            "dedup_window_seconds": 60.0,
        },
        "filter": {
            "net_gamma": {
                "enabled": True,
                "params": {
                    "flip_buffer": 0.50,
                },
            },
        },
        "layer1": {
            "gamma_wall_bounce": {
                "enabled": True,
                "params": {
                    "min_wall_gex": 100000,
                },
            },
        },
        "layer2": {},
        "layer3": {},
        "full_data": {},
    }


@pytest.fixture
def sample_config_path(tmp_path: Path) -> Path:
    """Create a temporary config file for testing."""
    import yaml

    config = {
        "global": {
            "min_confidence": 0.35,
            "max_signals_per_tick": 10,
        },
        "layer1": {
            "gamma_wall_bounce": {
                "enabled": True,
                "params": {"min_wall_gex": 100000},
            },
        },
    }

    config_file = tmp_path / "strategies.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)

    return config_file


# =============================================================================
# Rolling Window Fixtures
# =============================================================================

@pytest.fixture
def rolling_window_count():
    """Create a count-based RollingWindow."""
    from strategies.rolling_window import RollingWindow

    return RollingWindow(window_type="count", window_size=10)


@pytest.fixture
def rolling_window_time():
    """Create a time-based RollingWindow (30 seconds)."""
    from strategies.rolling_window import RollingWindow

    return RollingWindow(window_type="time", window_size=30)


# =============================================================================
# Message Fixtures
# =============================================================================

@pytest.fixture
def sample_option_message():
    """Sample option_update message for GEXCalculator testing."""
    return {
        "type": "option_update",
        "strike": 195.0,
        "gamma": 0.025,
        "open_interest": 1000.0,
        "side": "call",
        "delta": 0.55,
        "iv": 0.45,
    }


@pytest.fixture
def sample_put_message():
    """Sample put option message."""
    return {
        "type": "option_update",
        "strike": 195.0,
        "gamma": 0.020,
        "open_interest": 800.0,
        "side": "put",
        "delta": -0.45,
        "iv": 0.48,
    }


@pytest.fixture
def sample_underlying_message():
    """Sample underlying_update message."""
    return {
        "type": "underlying_update",
        "symbol": "TSLA",
        "price": 195.50,
        "timestamp": 1716072000.0,
    }


# =============================================================================
# Async Test Helpers
# =============================================================================

@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_test_client():
    """Async test client fixture."""
    client = MagicMock()
    client.connect = AsyncMock()
    client.stop = AsyncMock()
    yield client


class AsyncMock(Mock):
    """Async mock for asyncio tests."""
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


# =============================================================================
# Temporary Directories
# =============================================================================

@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    """Create a temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def test_log_dir(tmp_path: Path) -> Path:
    """Create a temporary log directory for tests."""
    log_dir = tmp_path / "log"
    log_dir.mkdir()
    return log_dir


# =============================================================================
# Parametrized Fixtures
# =============================================================================

@pytest.fixture(params=["count", "time"])
def rolling_window_type(request):
    """Parametrized rolling window type fixture."""
    return request.param


@pytest.fixture(params=["TSLA", "AAPL", "SPY"])
def symbol_fixture(request):
    """Parametrized symbol fixture."""
    return request.param


@pytest.fixture(params=[0.30, 0.50, 0.70, 0.90])
def confidence_fixture(request):
    """Parametrized confidence fixture."""
    return request.param
