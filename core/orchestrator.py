"""Syngex Orchestrator - lifecycle management wrapper."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Type

import yaml

from services.dashboard_service import DashboardService
from services.heatmap_service import HeatmapService
from services.state_exporter import StateExporter


# Import all components
from data.ingestor import TradeStationClient
from engine.gex_calculator import GEXCalculator
from engine.dashboard import SyngexDashboard
from strategies.engine import StrategyEngine, EngineConfig
from strategies.filters.net_gamma_filter import NetGammaFilter as LegacyNetGammaFilter
from strategies.rolling_window import RollingWindow
from strategies.rolling_keys import *
from strategies.layer1 import (
    GammaWallBounce,
    MagnetAccelerate,
    GammaFlipBreakout,
    GammaSqueeze,
    GEXImbalance,
    ConfluenceReversal,
    VolCompressionRange,
    GEXDivergence,
)
from strategies.layer2 import (
    DeltaGammaSqueeze,
    DeltaVolumeExhaustion,
    CallPutFlowAsymmetry,
    IVGEXDivergence,
)
from strategies.layer2.delta_iv_divergence import DeltaIVDivergence
from strategies.layer3 import (
    GammaVolumeConvergence,
    IVBandBreakout,
    StrikeConcentration,
    ThetaBurn,
)
from strategies.full_data import (
    IVSkewSqueeze,
    ProbWeightedMagnet,
    ProbDistributionShift,
    ExtrinsicIntrinsicFlow,
)
from strategies.signal_tracker import SignalTracker

# Import new engines (Phase 2)
from core.strategy_engine import StrategyEvaluationEngine

# Import Phase 4 engines
from core.gamma_profile import GammaProfileEngine
from core.filters import NetGammaFilter

from config.logging_config import setup_logging, log_with_correlation


class SyngexOrchestrator:
    """
    Manages the full lifecycle of the Syngex pipeline.

    Lifecycle:
        initialize() → connect() → run() → shutdown()

    Uses service layer for dashboard, heatmap, and state export.
    """

    # How often (seconds) to log the Gamma Profile
    PROFILE_INTERVAL: float = 5.0

    def __init__(
        self, symbol: str, mode: str = "stream", port: int = 8501,
        json_log: bool = False
    ) -> None:
        self.symbol = symbol.upper()
        self.mode = mode.lower()
        self._port = port
        self._json_log = json_log
        self._client: TradeStationClient | None = None
        self._calculator: GEXCalculator | None = None
        self._dashboard: SyngexDashboard | None = None
        self._strategy_engine: StrategyEngine | None = None
        self._gamma_filter: NetGammaFilter | None = None  # From core.filters
        self._gamma_profile: GammaProfileEngine | None = None
        self._rolling_data: Dict[str, RollingWindow] = {}
        self._running = False
        self._profile_timer: float = 0.0
        self._signal_timer: float = 0.0
        self._state_export_timer: float = 0.0

        # Shared data file for Streamlit dashboard (symbol-specific)
        self._data_dir = Path(__file__).parent.parent / "data"

        # Strategy configuration (loaded from YAML in initialize())
        self._strategy_config: Dict[str, Any] = {}
        self._config_path = Path(__file__).parent.parent / "config" / "strategies.yaml"
        self._config_mtime: float = 0.0  # Last known modification time
        self._config_lock = asyncio.Lock()  # Thread-safe config reload

        # Signal outcome tracker
        self._signal_tracker: SignalTracker | None = None

        # Correlation ID for this orchestrator instance (traces signal lifecycle)
        self._correlation_id = str(uuid.uuid4())[:8]

        # Logging
        self._logger = setup_logging(log_level="DEBUG", json_format=json_log)

        # Services (created in initialize())
        self._dashboard_service: DashboardService | None = None
        self._heatmap_service: HeatmapService | None = None
        self._state_exporter: StateExporter | None = None

        # Phase 2 Engines
        self._strategy_engine_eval: StrategyEvaluationEngine | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Create and wire all components."""
        log_with_correlation(
            self._logger, logging.INFO,
            "Initializing components",
            correlation_id=self._correlation_id,
            symbol=self.symbol
        )

        self._calculator = GEXCalculator(symbol=self.symbol)
        self._dashboard = SyngexDashboard(orchestrator=self)
        self._client = TradeStationClient()

        # Phase 4: Create Gamma Profile Engine and NetGammaFilter
        self._gamma_profile = GammaProfileEngine()
        self._gamma_filter = NetGammaFilter(flip_buffer=0.50)

        # Load strategy configuration from YAML
        config_path = Path(__file__).parent.parent / "config" / "strategies.yaml"
        self._strategy_config: Dict[str, Any] = {}
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    self._strategy_config = yaml.safe_load(f) or {}
                log_with_correlation(
                    self._logger, logging.INFO,
                    "Loaded strategy config",
                    correlation_id=self._correlation_id,
                    config_path=str(config_path)
                )
            except Exception as exc:
                log_with_correlation(
                    self._logger, logging.WARNING,
                    "Failed to load strategy config, using defaults",
                    correlation_id=self._correlation_id,
                    error=str(exc)
                )
                self._strategy_config = {}
        else:
            log_with_correlation(
                self._logger, logging.WARNING,
                "Strategy config not found, using defaults",
                correlation_id=self._correlation_id,
                config_path=str(config_path)
            )

        # Build per-strategy hold times from YAML config
        strategy_hold_times: Dict[str, int] = {}
        for layer_key in ["layer1", "layer2", "layer3", "full_data"]:
            layer_config = self._strategy_config.get(layer_key, {})
            for strat_name, strat_cfg in layer_config.items():
                hold = strat_cfg.get("tracker", {}).get("max_hold_seconds")
                if hold is not None:
                    strategy_hold_times[strat_name] = hold

        # Signal tracker for outcome resolution (symbol-specific log)
        log_dir = self._data_dir.parent / "log"
        signal_log_path = str(log_dir / "signals.jsonl")  # global master ledger
        self._signal_tracker = SignalTracker(
            max_hold_seconds=900,  # global default
            strategy_hold_times=strategy_hold_times,
            log_dir=str(log_dir),
            symbol=self.symbol,
            signal_log_path=signal_log_path,
        )

        # Apply global config to EngineConfig
        global_config = self._strategy_config.get("global", {})
        self._strategy_engine = StrategyEngine(
            config=EngineConfig(
                min_confidence=global_config.get("min_confidence", 0.35),
                max_signals_per_tick=global_config.get("max_signals_per_tick", 10),
                signal_log_path=global_config.get(
                    "signal_log_path", str(self._data_dir.parent / "log" / "signals.jsonl")
                ),
                dedup_window_seconds=global_config.get("dedup_window_seconds", 60.0),
            )
        )
        self._strategy_engine.register_filter(self._gamma_filter.evaluate_signal)

        # Register strategies from config (config-driven, not hardcoded)
        self._register_strategies_from_config()

        # Register Layer 0 (master filter) — controlled by config
        filter_config = self._strategy_config.get("filter", {})
        net_gamma_cfg = filter_config.get("net_gamma", {})
        if net_gamma_cfg.get("enabled", True):
            flip_buffer = net_gamma_cfg.get("params", {}).get("flip_buffer", 0.5)
            self._gamma_filter = NetGammaFilter(flip_buffer=flip_buffer)
            log_with_correlation(
                self._logger, logging.INFO,
                "Registered net_gamma filter",
                correlation_id=self._correlation_id,
                flip_buffer=flip_buffer
            )

        # Rolling windows for key metrics
        self._rolling_data = {
            KEY_PRICE_5M: RollingWindow(window_type="time", window_size=300),
            KEY_PRICE_30M: RollingWindow(window_type="time", window_size=1800),
            KEY_NET_GAMMA_5M: RollingWindow(window_type="time", window_size=300),
            KEY_VOLUME_5M: RollingWindow(window_type="time", window_size=300),
            # Layer 2 rolling windows
            KEY_TOTAL_DELTA_5M: RollingWindow(window_type="time", window_size=300),
            KEY_WALL_DELTA_5M: RollingWindow(window_type="time", window_size=300),
            KEY_ATM_DELTA_5M: RollingWindow(window_type="time", window_size=300),
            KEY_ATM_IV_5M: RollingWindow(window_type="time", window_size=300),
            # Layer 3 / full_data rolling windows (now populated via _on_message)
            KEY_VOLUME_UP_5M: RollingWindow(window_type="time", window_size=300),
            KEY_VOLUME_DOWN_5M: RollingWindow(window_type="time", window_size=300),
            KEY_TOTAL_GAMMA_5M: RollingWindow(window_type="time", window_size=300),
            KEY_IV_SKEW_5M: RollingWindow(window_type="time", window_size=300),
            KEY_EXTRINSIC_PROXY_5M: RollingWindow(window_type="time", window_size=300),
            KEY_PROB_MOMENTUM_5M: RollingWindow(window_type="time", window_size=300),
        }

        # Call/put update counters for volume_up/volume_down tracking
        self._call_update_count: int = 0
        self._put_update_count: int = 0

        # Per-strike IV windows (populated lazily)
        self._iv_windows: Dict[str, RollingWindow] = {}

        # Wire callback: ingestor → calculator + engine
        self._client.set_on_message_callback(self._on_message)

        # Register subscriptions — quotes feed underlying price, option chain feeds contracts
        self._client.subscribe_to_quotes(self.symbol)
        self._client.subscribe_to_option_chain(self.symbol)

        # Create services
        self._dashboard_service = DashboardService(
            symbol=self.symbol,
            port=self._port,
            data_dir=self._data_dir,
            orchestrator_ref=self,
        )
        self._heatmap_service = HeatmapService(
            symbol=self.symbol,
            port=self._port,
            data_dir=self._data_dir,
            orchestrator_ref=self,
        )
        self._state_exporter = StateExporter(
            data_dir=self._data_dir,
            calculator_ref=self._calculator,
            strategy_engine_ref=self._strategy_engine,
            signal_tracker_ref=self._signal_tracker,
            gamma_filter_ref=self._gamma_filter,
            symbol=self.symbol,
            logger=self._logger,
            correlation_id=self._correlation_id,
            strategy_engine_eval=self._strategy_engine_eval,
        )

        # Phase 2: Create Strategy Evaluation Engine
        self._strategy_engine_eval = StrategyEvaluationEngine(
            gex_calculator=self._calculator,
            strategy_engine=self._strategy_engine,
            signal_tracker=self._signal_tracker,
            gamma_filter=self._gamma_filter,
            logger=self._logger,
            correlation_id=self._correlation_id,
        )

        log_with_correlation(
            self._logger, logging.INFO,
            "Components initialized",
            correlation_id=self._correlation_id,
            symbol=self.symbol
        )

    async def connect(self) -> None:
        """Establish streaming connections."""
        assert self._client is not None
        log_with_correlation(
            self._logger, logging.INFO,
            "Connecting to TradeStation streams",
            correlation_id=self._correlation_id
        )
        await self._client.connect()

    async def run(self) -> None:
        """
        Main run loop.

        Monitors the Gamma Profile and reports at regular intervals.
        Also watches for fail-fast conditions.
        Spawns the Streamlit dashboard as a background subprocess (dashboard mode only).
        """
        assert self._client is not None
        assert self._calculator is not None

        self._running = True
        self._profile_timer = time.monotonic()
        self._state_export_timer = time.monotonic()

        # Start strategy engine
        self._strategy_engine.start()

        log_with_correlation(
            self._logger, logging.INFO,
            "Pipeline running",
            correlation_id=self._correlation_id,
            mode=self.mode,
            strategy_count=len(self._strategy_engine._strategies)
        )

        # Start the Streamlit dashboard and heatmap as background subprocesses (dashboard mode only)
        if self.mode == "dashboard":
            self._dashboard_service.start()
            self._heatmap_service.start()

        try:
            # Start config watcher task
            config_task = asyncio.create_task(self._watch_config())

            while self._running:
                now = time.monotonic()

                # Report Gamma Profile at intervals (using new engine)
                if now - self._profile_timer >= self.PROFILE_INTERVAL:
                    if self._strategy_engine_eval:
                        self._strategy_engine_eval.report_profile(self._calculator, self.symbol)
                    self._profile_timer = now

                # Export GEX state to shared file for Streamlit dashboard
                if now - self._state_export_timer >= 1.0:
                    self._state_exporter.export()
                    self._state_export_timer = now

                # Signal resolution (every ~1s)
                if now - self._signal_timer >= 1.0:
                    if self._signal_tracker and self._calculator:
                        price = self._calculator.get_summary()["underlying_price"]
                        resolved = self._signal_tracker.update(price, time.time())
                        if resolved:
                            for r in resolved:
                                log_with_correlation(
                                    self._logger, logging.INFO,
                                    "SIGNAL_RESOLVED",
                                    correlation_id=self._correlation_id,
                                    strategy_id=r.open_signal.strategy_id,
                                    direction=r.open_signal.direction.value,
                                    outcome=r.outcome.value,
                                    pnl=r.pnl,
                                    hold_seconds=r.hold_time
                                )
                    self._signal_timer = now

                # Strategy evaluation (every ~1s) - using new engine
                if now - self._profile_timer >= 1.0:
                    if self._strategy_engine_eval:
                        self._strategy_engine_eval.evaluate_strategies(self)
                    self._profile_timer = now

                # Fail-fast: option chain critical error
                if self._client._option_chain_failed:
                    log_with_correlation(
                        self._logger, logging.ERROR,
                        "Option chain stream failed (critical error), shutting down",
                        correlation_id=self._correlation_id
                    )
                    break

                await asyncio.sleep(0.25)
        finally:
            config_task.cancel()
            self._dashboard_service.stop()
            self._heatmap_service.stop()

    async def shutdown(self) -> None:
        """Graceful shutdown."""
        log_with_correlation(
            self._logger, logging.INFO,
            "Shutting down",
            correlation_id=self._correlation_id
        )
        self._running = False

        # Stop strategy engine
        if self._strategy_engine:
            self._strategy_engine.stop()
            log_with_correlation(
                self._logger, logging.INFO,
                "Strategy engine stopped",
                correlation_id=self._correlation_id,
                signal_count=self._strategy_engine.signal_count
            )

        # Stop dashboard and heatmap services
        if self._dashboard_service:
            self._dashboard_service.stop()
        if self._heatmap_service:
            self._heatmap_service.stop()

        if self._client:
            await self._client.stop()

        log_with_correlation(
            self._logger, logging.INFO,
            "System shutdown complete",
            correlation_id=self._correlation_id
        )

    # ------------------------------------------------------------------
    # Config hot-reload
    # ------------------------------------------------------------------

    async def _reload_config(self) -> None:
        """Re-read config and apply new params to all strategies."""
        async with self._config_lock:
            try:
                if not self._config_path.exists():
                    return

                mtime = self._config_path.stat().st_mtime
                if mtime == self._config_mtime:
                    return  # No change

                with open(self._config_path, "r") as f:
                    strategy_config = yaml.safe_load(f)

                self._config_mtime = mtime
                self._strategy_config = strategy_config

                # Apply global config
                global_cfg = strategy_config.get("global", {})
                if global_cfg and self._strategy_engine:
                    self._strategy_engine.config.min_confidence = global_cfg.get("min_confidence", 0.35)
                    self._strategy_engine.config.max_signals_per_tick = global_cfg.get("max_signals_per_tick", 10)
                    self._strategy_engine.config.dedup_window_seconds = global_cfg.get("dedup_window_seconds", 60.0)
                    log_path = global_cfg.get("signal_log_path", "log/signals.jsonl")
                    self._strategy_engine.config.signal_log_path = str(self._data_dir.parent / log_path)

                # Apply per-strategy params
                for layer in ["layer1", "layer2", "layer3", "full_data"]:
                    layer_config = strategy_config.get(layer, {})
                    for strat_name, strat_cfg in layer_config.items():
                        params = strat_cfg.get("params", {})
                        # Find the registered strategy by name
                        if self._strategy_engine:
                            for strat in self._strategy_engine._strategies:
                                if strat.strategy_id == strat_name:
                                    strat.set_params(params)
                                    break

                # Apply filter config
                filter_cfg = strategy_config.get("filter", {}).get("net_gamma", {})
                if filter_cfg and self._gamma_filter:
                    params = filter_cfg.get("params", {})
                    if "flip_buffer" in params:
                        self._gamma_filter.flip_buffer = params["flip_buffer"]

                log_with_correlation(
                    self._logger, logging.INFO,
                    "Config reloaded",
                    correlation_id=self._correlation_id,
                    strategy_count=len(self._strategy_engine._strategies) if self._strategy_engine else 0
                )

            except Exception as exc:
                log_with_correlation(
                    self._logger, logging.ERROR,
                    "Config reload error",
                    correlation_id=self._correlation_id,
                    error=str(exc)
                )

    async def _watch_config(self) -> None:
        """Watch config file for changes and reload when detected."""
        while self._running:
            try:
                if self._config_path.exists():
                    mtime = self._config_path.stat().st_mtime
                    if mtime != self._config_mtime:
                        await self._reload_config()
            except Exception:
                log_with_correlation(
                    self._logger, logging.DEBUG,
                    "Config watch error",
                    correlation_id=self._correlation_id
                )

            await asyncio.sleep(2)  # Check every 2 seconds

    # ------------------------------------------------------------------
    # Config-driven strategy registration
    # ------------------------------------------------------------------

    def _register_strategies_from_config(self) -> None:
        """Register strategies from config file instead of hardcoded lists."""
        layers = ["layer1", "layer2", "layer3", "full_data"]
        total_registered = 0
        total_enabled = 0
        total_disabled = 0

        for layer in layers:
            layer_config = self._strategy_config.get(layer, {})
            if not layer_config:
                log_with_correlation(
                    self._logger, logging.INFO,
                    "No config for layer, skipping",
                    correlation_id=self._correlation_id,
                    layer=layer
                )
                continue

            layer_enabled = 0
            layer_disabled = 0

            for strat_name, strat_cfg in layer_config.items():
                strat_cls = self._get_strategy_class(layer, strat_name)
                if strat_cls is None:
                    log_with_correlation(
                        self._logger, logging.WARNING,
                        "Unknown strategy in layer, skipping",
                        correlation_id=self._correlation_id,
                        strategy_name=strat_name,
                        layer=layer
                    )
                    continue

                enabled = strat_cfg.get("enabled", True)
                if enabled:
                    strat = strat_cls(self._calculator)
                    self._strategy_engine.register(strat)
                    layer_enabled += 1
                    total_enabled += 1
                else:
                    layer_disabled += 1
                    total_disabled += 1
                    log_with_correlation(
                        self._logger, logging.INFO,
                        "Strategy disabled via config",
                        correlation_id=self._correlation_id,
                        strategy_name=strat_name,
                        layer=layer
                    )

            total_registered += layer_enabled
            log_with_correlation(
                self._logger, logging.INFO,
                "Layer registration summary",
                correlation_id=self._correlation_id,
                layer=layer,
                enabled=layer_enabled,
                disabled=layer_disabled
            )

        log_with_correlation(
            self._logger, logging.INFO,
            "Strategy registration complete",
            correlation_id=self._correlation_id,
            registered=total_enabled,
            disabled=total_disabled,
            total=total_enabled + total_disabled
        )

    def _get_strategy_class(
        self, layer: str, name: str
    ) -> Optional[Type]:
        """Map a strategy name string (from YAML) to its class."""
        strategy_map = {
            "layer1": {
                "gamma_wall_bounce": GammaWallBounce,
                "magnet_accelerate": MagnetAccelerate,
                "gamma_flip_breakout": GammaFlipBreakout,
                "gamma_squeeze": GammaSqueeze,
                "gex_imbalance": GEXImbalance,
                "confluence_reversal": ConfluenceReversal,
                "vol_compression_range": VolCompressionRange,
                "gex_divergence": GEXDivergence,
            },
            "layer2": {
                "delta_gamma_squeeze": DeltaGammaSqueeze,
                "delta_volume_exhaustion": DeltaVolumeExhaustion,
                "call_put_flow_asymmetry": CallPutFlowAsymmetry,
                "iv_gex_divergence": IVGEXDivergence,
                "delta_iv_divergence": DeltaIVDivergence,
            },
            "layer3": {
                "gamma_volume_convergence": GammaVolumeConvergence,
                "iv_band_breakout": IVBandBreakout,
                "strike_concentration": StrikeConcentration,
                "theta_burn": ThetaBurn,
            },
            "full_data": {
                "iv_skew_squeeze": IVSkewSqueeze,
                "prob_weighted_magnet": ProbWeightedMagnet,
                "prob_distribution_shift": ProbDistributionShift,
                "extrinsic_intrinsic_flow": ExtrinsicIntrinsicFlow,
            },
        }
        layer_map = strategy_map.get(layer, {})
        return layer_map.get(name)

    # ------------------------------------------------------------------
    # Helper calculations for rolling window feeds
    # ------------------------------------------------------------------

    def _calculate_extrinsic_proxy(
        self, greeks_summary: Dict[str, Any],
    ) -> Optional[float]:
        """Calculate aggregate extrinsic value proxy across all strikes.

        Uses abs(net_delta) * abs(net_gamma) as a proxy for extrinsic value.
        Returns total extrinsic proxy or None if insufficient data.
        """
        try:
            total_proxy = 0.0
            strike_count = 0

            for strike_str, strike_data in greeks_summary.items():
                try:
                    float(strike_str)
                except (ValueError, TypeError):
                    continue

                call_delta = strike_data.get("call_delta_sum", 0.0)
                put_delta = strike_data.get("put_delta_sum", 0.0)
                call_gamma = strike_data.get("call_gamma", 0.0)
                put_gamma = strike_data.get("put_gamma", 0.0)

                if call_delta == 0 and put_delta == 0:
                    continue

                net_delta = call_delta - put_delta
                net_gamma_val = call_gamma + put_gamma
                proxy = abs(net_delta) * abs(net_gamma_val)

                if proxy <= 0:
                    continue

                total_proxy += proxy
                strike_count += 1

            return total_proxy if strike_count >= 3 else None

        except Exception:
            return None

    def _calculate_prob_momentum(
        self, greeks_summary: Dict[str, Any],
    ) -> Optional[float]:
        """Calculate probability momentum across all strikes.

        ProbMomentum = Σ(net_delta_i * |strike_i - ATM_strike|)
        Positive = mass shifting right (bullish).
        Negative = mass shifting left (bearish).
        """
        try:
            atm_strike = None
            min_distance = float("inf")

            for strike_str in greeks_summary:
                try:
                    s = float(strike_str)
                except (ValueError, TypeError):
                    continue
                dist = abs(s - self._calculator.underlying_price)
                if dist < min_distance:
                    min_distance = dist
                    atm_strike = s

            if atm_strike is None:
                return None

            total_momentum = 0.0
            contributing = 0

            for strike_str, strike_data in greeks_summary.items():
                try:
                    strike = float(strike_str)
                except (ValueError, TypeError):
                    continue

                call_delta = strike_data.get("call_delta", 0.0)
                put_delta = strike_data.get("put_delta", 0.0)
                net_delta = call_delta - put_delta

                if call_delta == 0 and put_delta == 0:
                    continue

                distance = strike - atm_strike
                total_momentum += net_delta * distance
                contributing += 1

            return total_momentum if contributing >= 5 else None

        except Exception:
            return None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_message(self, data: Dict[str, Any]) -> None:
        """Callback from TradeStationClient — feed to GEXCalculator + update rolling windows."""
        assert self._calculator is not None
        try:
            self._calculator.process_message(data)

            # Update rolling windows with underlying price
            if data.get("type") == "underlying_update":
                price = data.get("price")
                if price and price > 0:
                    ts = time.time()
                    self._rolling_data[KEY_PRICE_5M].push(price, ts)
                    self._rolling_data[KEY_PRICE_30M].push(price, ts)

            # Periodically update net_gamma rolling window
            if self._calculator._msg_count % 20 == 0:
                ng = self._calculator.get_net_gamma()
                self._rolling_data[KEY_NET_GAMMA_5M].push(ng)

            # Track call/put option update counts for volume_up/volume_down proxy
            if data.get("type") == "option_update":
                side = data.get("side", "")
                if side == "call":
                    self._call_update_count += 1
                elif side == "put":
                    self._put_update_count += 1

            # Update Layer 2 rolling windows
            gex_summary = self._calculator.get_greeks_summary()
            if gex_summary:
                net_delta = gex_summary.get("net_delta", 0.0)
                total_vol = gex_summary.get("total_volume", 0)
                # Push total volume for volume confirmation filter
                if KEY_VOLUME_5M in self._rolling_data:
                    self._rolling_data[KEY_VOLUME_5M].push(total_vol)
                # Track total_delta_5m for delta_volume_exhaustion
                if KEY_TOTAL_DELTA_5M in self._rolling_data:
                    self._rolling_data[KEY_TOTAL_DELTA_5M].push(net_delta)

                # Per-strike IV windows for iv_gex_divergence
                iv_by_strike = self._calculator.get_iv_by_strike_avg()
                for strike, avg_iv in iv_by_strike.items():
                    key = f"iv_{strike}_5m"
                    if key not in self._rolling_data:
                        self._rolling_data[key] = RollingWindow(
                            window_type="time", window_size=300
                        )
                    if avg_iv > 0:
                        self._rolling_data[key].push(avg_iv)

                # Push missing rolling window feeds for layer2/3/full_data strategies
                # total_gamma_5m — from GEXCalculator net gamma
                self._rolling_data[KEY_TOTAL_GAMMA_5M].push(
                    self._calculator.get_net_gamma()
                )

                # iv_skew_5m — avg call IV minus avg put IV
                try:
                    iv_skew = self._calculator.get_iv_skew()
                    if iv_skew is not None:
                        self._rolling_data[KEY_IV_SKEW_5M].push(iv_skew)
                except Exception:
                    pass

                # volume_up_5m / volume_down_5m — call/put update counts as proxy
                self._rolling_data[KEY_VOLUME_UP_5M].push(self._call_update_count)
                self._rolling_data[KEY_VOLUME_DOWN_5M].push(self._put_update_count)

                # extrinsic_proxy_5m — aggregate extrinsic value proxy
                extrinsic_proxy = self._calculate_extrinsic_proxy(gex_summary)
                if extrinsic_proxy is not None:
                    self._rolling_data[KEY_EXTRINSIC_PROXY_5M].push(extrinsic_proxy)

                # prob_momentum_5m — probability distribution momentum
                prob_mom = self._calculate_prob_momentum(gex_summary)
                if prob_mom is not None:
                    self._rolling_data[KEY_PROB_MOMENTUM_5M].push(prob_mom)

                # Push per-strike ATM delta and IV for delta_iv_divergence
                atm_price = self._calculator.underlying_price
                atm_strike = self._calculator.get_atm_strike(atm_price)
                if atm_strike is not None:
                    delta_data = self._calculator.get_delta_by_strike(atm_strike)
                    atm_delta = delta_data.get("net_delta", 0.0)
                    if KEY_ATM_DELTA_5M in self._rolling_data:
                        self._rolling_data[KEY_ATM_DELTA_5M].push(atm_delta)

                    atm_iv = self._calculator.get_iv_by_strike(atm_strike)
                    if atm_iv is not None and KEY_ATM_IV_5M in self._rolling_data:
                        self._rolling_data[KEY_ATM_IV_5M].push(atm_iv)


        except Exception as exc:
            log_with_correlation(
                self._logger, logging.ERROR,
                "Error processing message",
                correlation_id=self._correlation_id,
                error=str(exc)
            )
