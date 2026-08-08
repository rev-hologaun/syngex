from __future__ import annotations
from pathlib import Path
from typing import Any, Optional
import threading


class SharedPipeline:
    """Shared data pipeline used by multiple orchestrator instances."""

    def __init__(self, symbol: str, alternate_data_file: Optional[Path] = None):
        self.symbol = symbol
        self.alternate_data_file = alternate_data_file

        # TradeStation connections (stream mode)
        self.ts_client: Any = None
        self.stocks_subscriptions: list[dict] = []
        self.options_subscriptions: list[dict] = []
        self.streams_active: bool = False

        # WebSocket GEX feed
        self.ws_gex_enabled: bool = False
        self.ws_gex_url: str = ""

        # Data cache
        self.gex_data_cache: dict[str, Any] = {}

        # Lock for thread-safe updates
        self._lock = threading.Lock()

        # Run loop state
        self.running: bool = False

    @property
    def log_dir(self) -> Path:
        return Path(__file__).parent / "log"
