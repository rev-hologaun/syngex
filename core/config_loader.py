"""Configuration loader with hot-reload support."""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import yaml


@dataclass
class GlobalConfig:
    """Global configuration settings."""
    symbol: str = "TSLA"
    port: int = 8200
    log_level: str = "INFO"
    min_confidence: float = 0.35
    max_signals_per_tick: int = 10
    dedup_window_seconds: float = 60.0
    signal_log_path: str = "log/signals.jsonl"


@dataclass
class StrategyParams:
    """Strategy-specific parameters."""
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)
    tracker: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LayerConfig:
    """Configuration for a strategy layer."""
    strategies: Dict[str, StrategyParams] = field(default_factory=dict)


@dataclass
class FilterConfig:
    """Configuration for filters."""
    net_gamma: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategiesConfig:
    """Full strategies configuration."""
    global_config: GlobalConfig = field(default_factory=GlobalConfig)
    layer1: LayerConfig = field(default_factory=LayerConfig)
    layer2: LayerConfig = field(default_factory=LayerConfig)
    layer3: LayerConfig = field(default_factory=LayerConfig)
    full_data: LayerConfig = field(default_factory=LayerConfig)
    filter_config: FilterConfig = field(default_factory=FilterConfig)


class ConfigLoader:
    """
    YAML configuration loader with hot-reload support.

    Features:
        - Load YAML configuration files
        - Validate configuration structure
        - Hot-reload support with file watching
        - Type-safe configuration objects
    """

    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the config loader.

        Args:
            config_path: Path to the YAML configuration file
            logger: Logger instance for debug output
        """
        self._config_path = Path(config_path) if config_path else None
        self._logger = logger or logging.getLogger(__name__)
        self._config = StrategiesConfig()
        self._raw_config: Dict[str, Any] = {}
        self._config_mtime: float = 0.0
        self._watch_task: Optional[asyncio.Task] = None
        self._reload_callbacks: list[Callable[[StrategiesConfig], None]] = []
        self._lock = asyncio.Lock()

    @property
    def config(self) -> StrategiesConfig:
        """Get the current configuration."""
        return self._config

    @property
    def config_path(self) -> Optional[Path]:
        """Get the configuration file path."""
        return self._config_path

    def load(self, config_path: Optional[str | Path] = None) -> StrategiesConfig:
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file (overrides constructor path)

        Returns:
            Parsed StrategiesConfig object
        """
        if config_path:
            self._config_path = Path(config_path)

        if not self._config_path or not self._config_path.exists():
            self._logger.warning(f"Config file not found: {self._config_path}")
            return self._config

        try:
            with open(self._config_path, "r") as f:
                self._raw_config = yaml.safe_load(f) or {}

            self._parse_config()
            self._config_mtime = self._config_path.stat().st_mtime
            self._logger.info(f"Loaded config from {self._config_path}")

            return self._config

        except Exception as e:
            self._logger.error(f"Failed to load config: {e}")
            return self._config

    def _parse_config(self) -> None:
        """Parse raw YAML config into typed configuration objects."""
        # Parse global config
        global_cfg = self._raw_config.get("global", {})
        self._config.global_config = GlobalConfig(
            symbol=global_cfg.get("symbol", "TSLA"),
            port=global_cfg.get("port", 8200),
            log_level=global_cfg.get("log_level", "INFO"),
            min_confidence=global_cfg.get("min_confidence", 0.35),
            max_signals_per_tick=global_cfg.get("max_signals_per_tick", 10),
            dedup_window_seconds=global_cfg.get("dedup_window_seconds", 60.0),
            signal_log_path=global_cfg.get("signal_log_path", "log/signals.jsonl"),
        )

        # Parse strategy layers
        for layer_name in ["layer1", "layer2", "layer3", "full_data"]:
            layer_data = self._raw_config.get("strategies", {}).get(layer_name, {})
            layer_config = LayerConfig(strategies={})

            for strat_name, strat_data in layer_data.items():
                if strat_data is None:
                    strat_data = {}

                strategy_params = StrategyParams(
                    enabled=strat_data.get("enabled", True),
                    params=strat_data.get("params", {}),
                    tracker=strat_data.get("tracker", {}),
                )
                layer_config.strategies[strat_name] = strategy_params

            setattr(self._config, layer_name, layer_config)

        # Parse filter config
        filter_data = self._raw_config.get("filter", {})
        self._config.filter_config = FilterConfig(
            net_gamma=filter_data.get("net_gamma", {})
        )

    def reload(self) -> bool:
        """Reload configuration if file has changed.

        Returns:
            True if config was reloaded, False otherwise
        """
        if not self._config_path or not self._config_path.exists():
            return False

        try:
            current_mtime = self._config_path.stat().st_mtime
            if current_mtime == self._config_mtime:
                return False  # No change

            with self._lock:
                old_config = self._config
                self.load()

                # Notify callbacks
                for callback in self._reload_callbacks:
                    try:
                        callback(self._config)
                    except Exception as e:
                        self._logger.error(f"Config reload callback error: {e}")

                self._logger.info("Config reloaded successfully")
                return True

        except Exception as e:
            self._logger.error(f"Config reload error: {e}")
            return False

    async def reload_async(self) -> bool:
        """Async version of reload."""
        return await asyncio.to_thread(self.reload)

    def start_watching(self, interval: float = 2.0) -> None:
        """Start watching config file for changes.

        Args:
            interval: Check interval in seconds
        """
        if self._watch_task:
            return

        async def _watch_loop():
            while True:
                try:
                    await asyncio.sleep(interval)
                    await self.reload_async()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._logger.error(f"Config watch error: {e}")

        self._watch_task = asyncio.create_task(_watch_loop())
        self._logger.info(f"Started config watching (interval={interval}s)")

    def stop_watching(self) -> None:
        """Stop watching config file for changes."""
        if self._watch_task:
            self._watch_task.cancel()
            self._watch_task = None
            self._logger.info("Stopped config watching")

    def on_reload(self, callback: Callable[[StrategiesConfig], None]) -> None:
        """Register a callback to be called on config reload.

        Args:
            callback: Function to call with new config
        """
        self._reload_callbacks.append(callback)

    def get_strategy_params(self, layer: str, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get parameters for a specific strategy.

        Args:
            layer: Layer name (layer1, layer2, layer3, full_data)
            strategy_name: Strategy name

        Returns:
            Strategy parameters or None if not found
        """
        layer_config = getattr(self._config, layer, None)
        if not layer_config:
            return None

        strategy = layer_config.strategies.get(strategy_name)
        return strategy.params if strategy else None

    def is_strategy_enabled(self, layer: str, strategy_name: str) -> bool:
        """Check if a strategy is enabled.

        Args:
            layer: Layer name
            strategy_name: Strategy name

        Returns:
            True if enabled
        """
        layer_config = getattr(self._config, layer, None)
        if not layer_config:
            return False

        strategy = layer_config.strategies.get(strategy_name)
        return strategy.enabled if strategy else False

    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration structure.

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Validate global config
        if not self._config.global_config.symbol:
            errors.append("Global config: symbol is required")

        if self._config.global_config.port < 1 or self._config.global_config.port > 65535:
            errors.append(f"Global config: port must be between 1 and 65535 (got {self._config.global_config.port})")

        if self._config.global_config.min_confidence < 0 or self._config.global_config.min_confidence > 1:
            errors.append(f"Global config: min_confidence must be between 0 and 1 (got {self._config.global_config.min_confidence})")

        # Validate strategy layers
        for layer_name in ["layer1", "layer2", "layer3", "full_data"]:
            layer_config = getattr(self._config, layer_name)
            for strat_name, strategy in layer_config.strategies.items():
                if not isinstance(strategy.enabled, bool):
                    errors.append(f"{layer_name}.{strat_name}: enabled must be boolean")

        return len(errors) == 0, errors


def load_config(
    config_path: str | Path,
    logger: Optional[logging.Logger] = None,
) -> StrategiesConfig:
    """Convenience function to load configuration.

    Args:
        config_path: Path to YAML configuration file
        logger: Optional logger instance

    Returns:
        Parsed StrategiesConfig object
    """
    loader = ConfigLoader(config_path=config_path, logger=logger)
    return loader.load()
