"""
orchestrator/lifecycle.py — Syngex Orchestrator Lifecycle

Manages the full lifecycle of the Syngex pipeline:
    initialize() → connect() → run() → shutdown()

This module contains the SyngexOrchestrator class which coordinates:
- TradeStationClient for data streaming
- GEXCalculator for gamma exposure calculations
- StrategyEngine for strategy evaluation
- NetGammaFilter for regime filtering
- SignalTracker for signal outcome resolution

Data processing logic is delegated to data/stream_processor.py.

Usage:
    orchestrator = SyngexOrchestrator(symbol="TSLA", mode="stream")
    await orchestrator.initialize()
    await orchestrator.connect()
    await orchestrator.run()
    await orchestrator.shutdown()
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml

# ---------------------------------------------------------------------------
# Logging — strict, zero-noise
# ---------------------------------------------------------------------------
_noisy_loggers = {
    "ingestor.tradestation_client": logging.WARNING,
    "GEXCalculator": logging.WARNING,
    "aiohttp": logging.WARNING,
    "httpx": logging.WARNING,
    "asyncio": logging.WARNING,
}
for _name, _level in _noisy_loggers.items():
    logging.getLogger(_name).setLevel(_level)
    logging.getLogger(_name).handlers.clear()

logger = logging.getLogger("Syngex")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
)
logger.addHandler(_handler)

# ---------------------------------------------------------------------------
# Safety — READ-ONLY enforcement
# ---------------------------------------------------------------------------
from config.trade_guard import READ_ONLY
if READ_ONLY:
    logger.info("🔒 SAFETY: READ-ONLY mode active — all order placement blocked")

# ---------------------------------------------------------------------------
# Component imports
# ---------------------------------------------------------------------------
from ingestor.tradestation_client import TradeStationClient
from engine.gex_calculator import GEXCalculator
from strategies.engine import StrategyEngine, EngineConfig
from strategies.filters.net_gamma_filter import NetGammaFilter
from strategies.rolling_window import RollingWindow
from strategies.signal_tracker import SignalTracker
from strategies.si_monitor import SIMonitor

# Rolling keys imports
from strategies.rolling_keys import (
    KEY_NET_GAMMA_5M,
    KEY_PRICE_5M,
    KEY_PRICE_30M,
    KEY_ATR_5M,
    KEY_DELTA_DENSITY_5M,
    KEY_VOLUME_5M,
    KEY_TOTAL_DELTA_5M,
    KEY_TOTAL_GAMMA_5M,
    KEY_IV_SKEW_5M,
    KEY_ATM_DELTA_5M,
    KEY_ATM_IV_5M,
    KEY_SYNC_CORR_5M,
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_ASK_SIZE_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_DEPTH_BID_LEVELS_5M,
    KEY_DEPTH_ASK_LEVELS_5M,
    KEY_BID_PARTICIPANTS_5M,
    KEY_ASK_PARTICIPANTS_5M,
    KEY_BID_EXCHANGES_5M,
    KEY_ASK_EXCHANGES_5M,
    KEY_CONVICT_SCORE_5M,
    KEY_FRAGILITY_BID_5M,
    KEY_FRAGILITY_ASK_5M,
    KEY_DECAY_VELOCITY_BID_5M,
    KEY_DECAY_VELOCITY_ASK_5M,
    KEY_TOP_WALL_BID_SIZE_5M,
    KEY_TOP_WALL_ASK_SIZE_5M,
    KEY_AGGRESSOR_VSI_5M,
    KEY_AGGRESSOR_VSI_ROC_5M,
    KEY_IEX_INTENT_SCORE_5M,
    KEY_MEMX_VSI_5M,
    KEY_BATS_VSI_5M,
    KEY_VENUE_CONCENTRATION_5M,
    KEY_ESI_MEMX_5M,
    KEY_ESI_MEMX_ROC_5M,
    KEY_ESI_BATS_5M,
    KEY_ESI_BATS_ROC_5M,
    KEY_MEMX_VOL_RATIO_5M,
    KEY_BATS_VOL_RATIO_5M,
    KEY_ESI_BASELINE_MEMX_1H,
    KEY_ESI_BASELINE_BATS_1H,
    KEY_SIS_BID_5M,
    KEY_SIS_ASK_5M,
    KEY_SIS_BID_ROC_5M,
    KEY_SIS_ASK_ROC_5M,
    KEY_ORDER_BOOK_DEPTH_5M,
    KEY_VOLUME_ZSCORE_5M,
    MSG_TYPE_UNDERLYING_UPDATE,
    MSG_TYPE_OPTION_UPDATE,
    MSG_TYPE_MARKET_DEPTH_QUOTES,
    MSG_TYPE_QUOTE_UPDATE,
    KEY_MARKET_DEPTH_AGG,
    KEY_OBI_5M,
    KEY_VAMP_LEVELS,
    KEY_FLOW_RATIO_5M,
    KEY_EXTRINSIC_PROXY_5M,
    KEY_EXTRINSIC_ROC_5M,
    KEY_SKEW_PSI_5M,
    KEY_SKEW_PSI_ROC_5M,
    KEY_SKEW_PSI_SIGMA_5M,
    KEY_CURVE_OMEGA_5M,
    KEY_CURVE_OMEGA_ROC_5M,
    KEY_CURVE_OMEGA_SIGMA_5M,
    KEY_PUT_SLOPE_5M,
    KEY_CALL_SLOPE_5M,
    KEY_PHI_CALL_5M,
    KEY_PHI_PUT_5M,
    KEY_PHI_RATIO_5M,
    KEY_PHI_TOTAL_5M,
    KEY_PHI_TOTAL_SIGMA_5M,
    KEY_GAMMA_BREAK_INDEX_5M,
    KEY_MAGNET_DELTA_5M,
    KEY_WALL_DELTA_5M,
    KEY_SKEW_WIDTH_5M,
    KEY_OTM_DELTA_5M,
    KEY_OTM_IV_5M,
    KEY_DELTA_IV_CORR_5M,
    KEY_IV_SKEW_GRADIENT_5M,
    KEY_GAMMA_DENSITY_5M,
    KEY_STRIKE_DELTA_5M,
    KEY_VAMP_5M,
    KEY_VAMP_MID_DEV_5M,
    KEY_VAMP_ROC_5M,
    KEY_VAMP_PARTICIPANTS_5M,
    KEY_VAMP_DEPTH_DENSITY_5M,
    KEY_DEPTH_DECAY_BID_5M,
    KEY_DEPTH_DECAY_ASK_5M,
    KEY_DEPTH_TOP5_BID_5M,
    KEY_DEPTH_TOP5_ASK_5M,
    KEY_DEPTH_VOL_RATIO_5M,
    KEY_IR_5M,
    KEY_IR_ROC_5M,
    KEY_IR_PARTICIPANTS_5M,
    KEY_SPREAD_ZSCORE_5M,
    KEY_LIQUIDITY_DENSITY_5M,
    KEY_PARTICIPANT_EQUILIBRIUM_5M,
    KEY_VOLUME_SPIKE_5M,
    KEY_BIGGEST_SIZE_5M,
    KEY_SMALLEST_SIZE_5M,
    KEY_CONCENTRATION_RATIO_5M,
    KEY_CONCENTRATION_SIGMA_5M,
    KEY_NUM_PARTICIPANTS_5M,
    KEY_DEPTH_BID_SIZE_ROLLING,
    KEY_DEPTH_ASK_SIZE_ROLLING,
    KEY_DEPTH_BID_LEVEL_AVG_5M,
    KEY_DEPTH_ASK_LEVEL_AVG_5M,
    KEY_VSI_COMBINED_5M,
    KEY_VSI_ROC_5M,
    KEY_IEX_INTENT_5M,
    KEY_PDR_5M,
    KEY_PDR_ROC_5M,
    KEY_SKEW_ROC_5M,
    KEY_DELTA_ROC_5M,
    KEY_MOMENTUM_ROC_5M,
    KEY_SKEW_CHANGE_5M,
    KEY_VSI_MAGNITUDE_5M,
    KEY_CONFLUENCE_PROX_5M,
    KEY_CONFLUENCE_SIGNAL_5M,
    KEY_LIQUIDITY_WALL_SIZE_5M,
    KEY_LIQUIDITY_WALL_SIGMA_5M,
    KEY_SYNC_SIGMA_5M,
    KEY_PRICE_VELOCITY_5M,
    KEY_GAMMA_DENSITY_5M,
    KEY_WALL_DISTANCE_5M,
    KEY_WALL_GEX_5M,
    KEY_WALL_GEX_SIGMA_5M,
)
# Extended keys module not yet created - placeholder for future expansion
EXTENDED_KEYS = []
EXTENDED_ROLLING_WINDOW_SIZES = {}

# Strategy imports
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
    VampMomentum,
    ObiAggressionFlow,
    DepthDecayMomentum,
    DepthImbalanceMomentum,
)
from strategies.layer2.exchange_flow_concentration import ExchangeFlowConcentration
from strategies.layer2.participant_diversity_conviction import ParticipantDiversityConviction
from strategies.layer2.participant_divergence_scalper import ParticipantDivergenceScalper
from strategies.layer2.delta_iv_divergence import DeltaIVDivergence
from strategies.layer2.exchange_flow_imbalance import ExchangeFlowImbalance
from strategies.layer2.exchange_flow_asymmetry import ExchangeFlowAsymmetry
from strategies.layer2.order_book_fragmentation import OrderBookFragmentation
from strategies.layer2.order_book_stacking import OrderBookStacking
from strategies.layer2.vortex_compression_breakout import VortexCompressionBreakout
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
    GhostPremium,
    SkewDynamics,
    SmileDynamics,
    ExtrinsicFlow,
    GammaBreaker,
    IronAnchor,
    SentimentSync,
    WhaleTracker,
)

# Stream processor for message handling
from data.stream_processor import (
    process_underlying_update,
    process_option_update,
    process_market_depth,
)


class SyngexOrchestrator:
    """
    Manages the full lifecycle of the Syngex pipeline.

    Lifecycle:
        initialize() → connect() → run() → shutdown()

    This orchestrator coordinates:
    - Data streaming via TradeStationClient
    - Gamma exposure calculations via GEXCalculator
    - Strategy evaluation via StrategyEngine
    - Signal tracking and resolution via SignalTracker

    Data processing (metrics computation, rolling window updates) is
    delegated to the stream_processor module.

    Attributes:
        symbol: The ticker symbol being tracked
        mode: Run mode ("stream" or "dashboard")
    """

    # How often (seconds) to log the Gamma Profile
    PROFILE_INTERVAL: float = 5.0

    # How often (seconds) to persist phi accumulators to disk
    PHI_WRITE_INTERVAL: float = 5.0

    def __init__(
        self, symbol: str, mode: str = "stream", port: int = 8501
    ) -> None:
        """Initialize the orchestrator.

        Args:
            symbol: Ticker symbol to track (e.g., "TSLA")
            mode: Run mode - "stream" for terminal logging, "dashboard" for Streamlit
            port: Port for the Streamlit dashboard (default: 8501)
        """
        self.symbol = symbol.upper()
        self.mode = mode.lower()
        self._port = port
        self._client: TradeStationClient | None = None
        self._calculator: GEXCalculator | None = None
        self._dashboard: Any | None = None
        self._strategy_engine: StrategyEngine | None = None
        self._gamma_filter: NetGammaFilter | None = None
        self._rolling_data: Dict[str, RollingWindow] = {}
        self._running = False
        self._exchange_bid_sizes: Dict[str, int] = {}
        self._exchange_ask_sizes: Dict[str, int] = {}
        self._profile_timer: float = 0.0
        self._strategy_eval_timer: float = 0.0
        self._signal_timer: float = 0.0
        self._dashboard_process: subprocess.Popen | None = None
        self._heatmap_process: subprocess.Popen | None = None
        self._heatmap_stderr: Any = None
        self._state_export_timer: float = 0.0

        # Data directories and files
        self._data_dir = Path(__file__).parent.parent / "data"
        self._data_file = self._data_dir / f"gex_state_{self.symbol}.json"

        # Strategy configuration
        self._strategy_config: Dict[str, Any] = {}
        self._config_path = Path(__file__).parent.parent / "config" / "strategies.yaml"
        self._config_mtime: float = 0.0
        self._config_lock = asyncio.Lock()

        # Signal tracking
        self._signal_tracker: SignalTracker | None = None

        # Message counters
        self._call_update_count: int = 0
        self._put_update_count: int = 0

        # Phi accumulators for extrinsic value flow
        self._phi_call_tick: float = 0.0
        self._phi_put_tick: float = 0.0
        self._phi_state_file = self._data_dir / f"phi_state_{self.symbol}.json"
        self._phi_last_write: float = 0.0

        # Per-strike IV windows
        self._iv_windows: Dict[str, RollingWindow] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Create and wire all components."""
        logger.info("Initializing components...")

        self._calculator = GEXCalculator(symbol=self.symbol)
        self._client = TradeStationClient()

        # Load strategy configuration
        config_path = Path(__file__).parent.parent / "config" / "strategies.yaml"
        self._strategy_config: Dict[str, Any] = {}
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    self._strategy_config = yaml.safe_load(f) or {}
                logger.info("Loaded strategy config from %s", config_path)
            except Exception as exc:
                logger.warning("Failed to load strategy config (%s), using defaults", exc)
                self._strategy_config = {}
        else:
            logger.warning("Strategy config not found at %s, using defaults", config_path)

        # Build per-strategy hold times
        strategy_hold_times: Dict[str, int] = {}
        for layer_key in ["layer1", "layer2", "layer3", "full_data"]:
            layer_config = self._strategy_config.get(layer_key, {})
            for strat_name, strat_cfg in layer_config.items():
                hold = strat_cfg.get("tracker", {}).get("max_hold_seconds")
                if hold is not None:
                    strategy_hold_times[strat_name] = hold

        # Signal tracker
        log_dir = self._data_dir.parent / "log"
        self._signal_tracker = SignalTracker(
            max_hold_seconds=900,
            strategy_hold_times=strategy_hold_times,
            log_dir=str(log_dir),
            symbol=self.symbol,
        )

        # Strategy engine
        global_config = self._strategy_config.get("global", {})
        self._strategy_engine = StrategyEngine(
            config=EngineConfig(
                min_confidence=global_config.get("min_confidence", 0.10),
                max_signals_per_tick=global_config.get("max_signals_per_tick", 10),
                dedup_window_seconds=global_config.get("dedup_window_seconds", 60.0),
            ),
            signal_tracker=self._signal_tracker,
        )
        self._register_strategies_from_config()

        # Net gamma filter
        filter_config = self._strategy_config.get("filter", {})
        net_gamma_cfg = filter_config.get("net_gamma", {})
        if net_gamma_cfg.get("enabled", True):
            flip_buffer = net_gamma_cfg.get("params", {}).get("flip_buffer", 0.5)
            self._gamma_filter = NetGammaFilter(flip_buffer=flip_buffer)
            self._strategy_engine.register_filter(self._gamma_filter.evaluate_signal)
            logger.info("Registered net_gamma filter (flip_buffer=%.2f)", flip_buffer)

        # Rolling windows for key metrics
        from strategies.rolling_keys import ALL_KEYS, ROLLING_WINDOW_SIZES

        self._rolling_data: Dict[str, RollingWindow] = {
            key: RollingWindow(window_type="time", window_size=ROLLING_WINDOW_SIZES.get(key, 300))
            for key in ALL_KEYS
        }

        # Extended rolling windows
        for key, window_size in EXTENDED_ROLLING_WINDOW_SIZES.items():
            if key not in self._rolling_data:
                self._rolling_data[key] = RollingWindow(window_type="time", window_size=window_size)

        # SI Component windows
        if KEY_DELTA_DENSITY_5M not in self._rolling_data:
            self._rolling_data[KEY_DELTA_DENSITY_5M] = RollingWindow(window_type="time", window_size=300)
        if KEY_VOLUME_ZSCORE_5M not in self._rolling_data:
            self._rolling_data[KEY_VOLUME_ZSCORE_5M] = RollingWindow(window_type="time", window_size=300)

        # Load phi accumulators for crash recovery
        self._load_phi_accumulators()

        # Wire callback
        self._client.set_on_message_callback(self._on_message)

        # Subscribe to streams
        self._client.subscribe_to_quotes(self.symbol)
        self._client.subscribe_to_option_chain(self.symbol)
        self._client.subscribe_to_market_depth_quotes(self.symbol)
        self._client.subscribe_to_market_depth_aggregates(self.symbol)

        logger.info("Components initialized. Symbol: %s", self.symbol)

    async def connect(self) -> None:
        """Establish streaming connections."""
        assert self._client is not None
        logger.info("Connecting to TradeStation streams...")
        await self._client.connect()

    async def run(self) -> None:
        """
        Main run loop.

        Monitors the Gamma Profile and reports at regular intervals.
        Spawns the Streamlit dashboard as a background subprocess (dashboard mode only).
        """
        assert self._client is not None
        assert self._calculator is not None

        self._running = True
        self._profile_timer = time.monotonic()
        self._strategy_eval_timer = time.monotonic()
        self._state_export_timer = time.monotonic()

        # Start strategy engine
        self._strategy_engine.start()

        logger.info("Pipeline running. Ctrl+C to stop.  Mode: %s", self.mode)
        logger.info("Strategy engine: %d strategies registered, filter active", len(self._strategy_engine._strategies))

        # Start dashboard and heatmap in dashboard mode
        if self.mode == "dashboard":
            self._start_dashboard()
            self._start_heatmap()

        try:
            config_task = asyncio.create_task(self._watch_config())

            while self._running:
                now = time.monotonic()

                # Report Gamma Profile
                if now - self._profile_timer >= self.PROFILE_INTERVAL:
                    self._report_profile()
                    self._profile_timer = now

                # Export GEX state
                if now - self._state_export_timer >= 1.0:
                    self._export_gex_state()
                    self._state_export_timer = now

                # Signal resolution
                if now - self._signal_timer >= 1.0:
                    if self._signal_tracker and self._calculator:
                        price = self._calculator.get_summary()["underlying_price"]
                        resolved = self._signal_tracker.update(price, time.time())
                        if resolved:
                            for r in resolved:
                                logger.info(
                                    "SIGNAL_RESOLVED  |  %s  |  %s  |  %s  |  PnL: $%.2f  |  Hold: %.0fs",
                                    r.open_signal.strategy_id,
                                    r.open_signal.direction,
                                    r.outcome.value,
                                    r.pnl,
                                    r.hold_time,
                                )
                    self._signal_timer = now

                # Strategy evaluation
                if now - self._strategy_eval_timer >= 1.0:
                    self._evaluate_strategies()
                    self._strategy_eval_timer = now

                # Fail-fast check
                if self._client._option_chain_failed:
                    logger.error("Option chain stream failed (critical error). Shutting down.")
                    break

                await asyncio.sleep(0.25)
        finally:
            config_task.cancel()
            self._stop_dashboard()
            self._stop_heatmap()

    async def shutdown(self) -> None:
        """Graceful shutdown."""
        logger.info("Shutting down...")
        self._running = False

        if self._strategy_engine:
            self._strategy_engine.stop()
            logger.info("Strategy engine: %d signals produced", self._strategy_engine.signal_count)

        self._stop_dashboard()
        self._stop_heatmap()

        if self._client:
            await self._client.stop()

        summary = self._calculator.get_summary() if self._calculator else {}
        logger.info("Final state: %s", summary)
        logger.info("System shutdown complete.")

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
                    return

                with open(self._config_path, "r") as f:
                    strategy_config = yaml.safe_load(f)

                self._config_mtime = mtime
                self._strategy_config = strategy_config

                # Apply global config
                global_cfg = strategy_config.get("global", {})
                if global_cfg and self._strategy_engine:
                    self._strategy_engine.config.min_confidence = global_cfg.get("min_confidence", 0.10)
                    self._strategy_engine.config.max_signals_per_tick = global_cfg.get("max_signals_per_tick", 10)
                    self._strategy_engine.config.dedup_window_seconds = global_cfg.get("dedup_window_seconds", 60.0)

                # Apply per-strategy params
                for layer in ["layer1", "layer2", "layer3", "full_data"]:
                    layer_config = strategy_config.get(layer, {})
                    for strat_name, strat_cfg in layer_config.items():
                        params = strat_cfg.get("params", {})
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

                logger.info("Config reloaded: %d strategies updated", len(self._strategy_engine._strategies) if self._strategy_engine else 0)

            except Exception as exc:
                logger.error("Config reload error: %s", exc, exc_info=True)

    async def _watch_config(self) -> None:
        """Watch config file for changes and reload when detected."""
        while self._running:
            try:
                if self._config_path.exists():
                    mtime = self._config_path.stat().st_mtime
                    if mtime != self._config_mtime:
                        await self._reload_config()
            except Exception as exc:
                logger.debug("Config watch error: %s", exc)

            await asyncio.sleep(2)

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
                logger.info("No config for layer %s, skipping", layer)
                continue

            layer_enabled = 0
            layer_disabled = 0

            for strat_name, strat_cfg in layer_config.items():
                strat_cls = self._get_strategy_class(layer, strat_name)
                if strat_cls is None:
                    logger.warning(
                        "Unknown strategy '%s' in layer '%s' — skipping",
                        strat_name, layer,
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
                    logger.info(
                        "Strategy '%s' (%s) disabled via config",
                        strat_name, layer,
                    )

            total_registered += layer_enabled
            logger.info(
                "Layer %s: %d enabled, %d disabled",
                layer, layer_enabled, layer_disabled,
            )

        logger.info(
            "Strategy registration complete: %d registered, %d disabled out of %d configured",
            total_enabled, total_disabled, total_enabled + total_disabled,
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
                "vamp_momentum": VampMomentum,
                "obi_aggression_flow": ObiAggressionFlow,
                "depth_decay_momentum": DepthDecayMomentum,
                "depth_imbalance_momentum": DepthImbalanceMomentum,
                "exchange_flow_concentration": ExchangeFlowConcentration,
                "participant_diversity_conviction": ParticipantDiversityConviction,
                "participant_divergence_scalper": ParticipantDivergenceScalper,
                "exchange_flow_imbalance": ExchangeFlowImbalance,
                "exchange_flow_asymmetry": ExchangeFlowAsymmetry,
                "order_book_fragmentation": OrderBookFragmentation,
                "order_book_stacking": OrderBookStacking,
                "vortex_compression_breakout": VortexCompressionBreakout,
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
                "ghost_premium": GhostPremium,
                "skew_dynamics": SkewDynamics,
                "smile_dynamics": SmileDynamics,
                "extrinsic_flow": ExtrinsicFlow,
                "gamma_breaker": GammaBreaker,
                "iron_anchor": IronAnchor,
                "sentiment_sync": SentimentSync,
                "whale_tracker": WhaleTracker,
            },
        }
        layer_map = strategy_map.get(layer, {})
        return layer_map.get(name)

    # ------------------------------------------------------------------
    # Message processing (delegated to stream_processor)
    # ------------------------------------------------------------------

    def _on_message(self, data: Dict[str, Any]) -> None:
        """Callback from TradeStationClient — delegate to stream processor.

        Args:
            data: Message data from the stream
        """
        assert self._calculator is not None
        try:
            self._calculator.process_message(data)
            ts = time.time()
            gex_summary = self._calculator.get_greeks_summary()

            msg_type = data.get("type", "")

            # Delegate to stream processor based on message type
            if msg_type == MSG_TYPE_UNDERLYING_UPDATE:
                self._call_update_count, self._put_update_count = process_underlying_update(
                    data, self._rolling_data, self._calculator,
                    self._call_update_count, self._put_update_count, ts
                )

            elif msg_type == MSG_TYPE_OPTION_UPDATE:
                self._phi_call_tick, self._phi_put_tick = process_option_update(
                    data, self._rolling_data, self._calculator,
                    gex_summary, self._phi_call_tick, self._phi_put_tick, ts
                )

            elif msg_type in (MSG_TYPE_MARKET_DEPTH_QUOTES, KEY_MARKET_DEPTH_AGG):
                self._exchange_bid_sizes, self._exchange_ask_sizes = process_market_depth(
                    data, self._rolling_data,
                    self._exchange_bid_sizes, self._exchange_ask_sizes, ts
                )

            # Periodic updates
            if self._calculator._msg_count % 20 == 0:
                ng = self._calculator.get_net_gamma()
                if KEY_NET_GAMMA_5M in self._rolling_data:
                    self._rolling_data[KEY_NET_GAMMA_5M].push(ng)

        except Exception as exc:
            logger.error("Message processing failed (critical): %s", exc, exc_info=True)

    # ------------------------------------------------------------------
    # Strategy evaluation
    # ------------------------------------------------------------------

    def _evaluate_strategies(self) -> None:
        """Run strategy evaluation with current market state."""
        assert self._calculator is not None
        assert self._strategy_engine is not None
        assert self._gamma_filter is not None

        summary = self._calculator.get_summary()
        net_gamma = summary["net_gamma"]
        flip = self._calculator.get_gamma_flip()
        price = summary["underlying_price"]

        # Update regime filter
        self._gamma_filter.update_regime(net_gamma, flip, price)

        # Build data snapshot
        _gamma_sync = 0.0
        sync_corr = self._rolling_data.get(KEY_SYNC_CORR_5M)
        if sync_corr and sync_corr.count > 0:
            _gamma_sync = sync_corr.values[-1]

        data = {
            "underlying_price": price,
            "symbol": self.symbol,
            "gex_calculator": self._calculator,
            "rolling_data": self._rolling_data,
            "timestamp": time.time(),
            "regime": self._gamma_filter.regime,
            "net_gamma": net_gamma,
            "gamma_flip": flip,
            "greeks_summary": self._calculator.get_greeks_summary(),
            "_gamma_sync": _gamma_sync,
            "exchange_data": {
                "bid_sizes": self._exchange_bid_sizes,
                "ask_sizes": self._exchange_ask_sizes,
            },
        }

        depth_snapshot = self._build_depth_snapshot()
        data["depth_snapshot"] = depth_snapshot

        # Strategy params
        strategy_params: Dict[str, Dict[str, Any]] = {}
        for layer in ["layer1", "layer2", "layer3", "full_data"]:
            layer_config = self._strategy_config.get(layer, {})
            for strat_name, strat_cfg in layer_config.items():
                if strat_cfg.get("enabled", True):
                    params = strat_cfg.get("params", {})
                    strategy_params[strat_name] = params
        data["params"] = strategy_params

        # SI Monitor (opt-in)
        _si_enabled = Path(__file__).parent.parent / "logs" / "si_monitor_enabled"
        if _si_enabled.exists():
            try:
                walls = self._calculator.get_gamma_walls(threshold=1e6)
                nearest_wall = None
                nearest_dist = float('inf')
                for w in walls:
                    dist = abs(w['strike'] - price) / price if price > 0 else float('inf')
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_wall = w

                if nearest_wall:
                    wall_gex_out = abs(nearest_wall.get('gex', 0.0))
                    wall_strength = wall_gex_out / (price * 100 * price) if price and price > 0 else 0.0
                    distance_to_wall_pct = nearest_dist
                    wall_depth = wall_gex_out
                else:
                    distance_to_wall_pct = 0.0
                    wall_depth = 0.0
                    wall_gex_out = 0.0
                    wall_strength = 0.0

                delta_density = self._calculator.get_total_delta_activity()

                vol_window = self._rolling_data.get(KEY_VOLUME_5M, None)
                if vol_window and vol_window.count >= 5:
                    vals = list(vol_window.values)
                    mean_v = sum(vals) / len(vals)
                    var_v = sum((x - mean_v) ** 2 for x in vals) / len(vals)
                    std_v = math.sqrt(var_v) if var_v > 0 else 1.0
                    volume_zscore = (vol_window.latest - mean_v) / std_v if vol_window.latest is not None else 0.0
                else:
                    volume_zscore = 0.0

                bd = self._rolling_data.get(KEY_ORDER_BOOK_DEPTH_5M, None)
                book_depth = bd.latest if bd is not None and bd.latest is not None else 0.0

                signal_dir = "long" if self._gamma_filter.regime == "POSITIVE" else "short"
                monitor = SIMonitor(
                    net_gamma=net_gamma,
                    regime=self._gamma_filter.regime,
                    delta_density=delta_density,
                    volume_zscore=volume_zscore,
                    distance_to_wall_pct=distance_to_wall_pct,
                    wall_depth=wall_depth,
                    book_depth=book_depth,
                    signal_direction=signal_dir,
                )
                si_record = monitor.compute()
                si_record["symbol"] = self.symbol
                si_record["volume_zscore"] = round(volume_zscore, 4)
                si_record["delta_density"] = round(delta_density, 4)
                si_record["distance_to_wall_pct"] = round(distance_to_wall_pct, 4)
                si_record["wall_depth"] = round(wall_depth, 4)
                si_record["wall_gex"] = round(wall_gex_out, 4)
                si_record["book_depth"] = round(book_depth, 4)
                si_record["net_gamma_raw"] = round(net_gamma, 2)

                _logs_dir = Path(__file__).parent.parent / "logs"
                _logs_dir.mkdir(parents=True, exist_ok=True)
                log_path = _logs_dir / "si_monitor.jsonl"
                with open(log_path, "a") as f:
                    f.write(json.dumps(si_record) + "\n")
            except Exception as exc:
                logger.warning("SI monitor error: %s", exc)

        # Run evaluation
        signals = self._strategy_engine.process(data)

        if signals:
            if self._signal_tracker:
                for s in signals:
                    self._signal_tracker.track(s.to_dict())

            for s in signals:
                logger.info("SIGNAL  |  %s  |  %s  |  conf=%.2f  |  %s",
                           s.strategy_id, s.direction.value, s.confidence, s.reason)

    # ------------------------------------------------------------------
    # Gamma Profile reporting
    # ------------------------------------------------------------------

    def _report_profile(self) -> None:
        """Log the current Gamma Profile — the evolving state."""
        assert self._calculator is not None

        summary = self._calculator.get_summary()
        profile = self._calculator.get_gamma_profile()

        net = summary["net_gamma"]
        price = summary["underlying_price"]
        strikes = summary["active_strikes"]

        logger.info(
            "GAMMA_PROFILE  |  %s  |  Underlying: $%.2f  |  "
            "Net Gamma: %+.2f  |  Strikes: %d  |  Msgs: %d",
            self.symbol, price, net, strikes, summary["total_messages"],
        )

        flip = self._calculator.get_gamma_flip()
        if flip is not None:
            logger.info("  GAMMA_FLIP:  Strike $%.1f (cumulative gamma turns negative below this)", flip)

        walls = self._calculator.get_gamma_walls(threshold=500000)
        if walls:
            wall_parts = []
            for w in walls[:3]:
                sign = "+" if w["gex"] > 0 else "-"
                wall_parts.append(f"${w['strike']:.0f} ({w['side']}) {sign}${abs(w['gex']):,.0f}")
            logger.info("  GAMMA_WALLS:  %s", "  |  ".join(wall_parts))

        top = sorted(
            profile["strikes"].items(),
            key=lambda x: abs(x[1]["net_gamma"]),
            reverse=True,
        )[:5]

        if top:
            parts = []
            for strike, bucket in top:
                ng = bucket["net_gamma"]
                sign = "+" if ng >= 0 else "-"
                parts.append(f"  K{strike:.1f}: {sign}{abs(ng):,.2f}")
            logger.info("  TOP_STRIKES:  %s", "  |  ".join(parts))

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _build_last_trigger(self) -> Dict[str, Dict[str, Any]]:
        """Build last_trigger data for each strategy from open + resolved signals."""
        if not self._signal_tracker:
            return {}

        triggers: Dict[str, Dict[str, Any]] = {}
        now = time.time()

        open_by_strat: Dict[str, Dict[str, Any]] = {}
        for sig in self._signal_tracker.get_open_signals():
            sid = sig.strategy_id
            if sid not in open_by_strat or sig.timestamp > open_by_strat[sid].get("timestamp", 0):
                open_by_strat[sid] = {
                    "direction": sig.direction,
                    "confidence": sig.confidence,
                    "entry": sig.entry,
                    "stop": sig.stop,
                    "target": sig.target,
                    "timestamp": sig.timestamp,
                }

        resolved_by_strat: Dict[str, Dict[str, Any]] = {}
        for r in self._signal_tracker.get_resolved():
            sid = r.open_signal.strategy_id
            if sid not in resolved_by_strat or r.resolution_time > resolved_by_strat[sid].get("timestamp", 0):
                resolved_by_strat[sid] = {
                    "direction": r.open_signal.direction,
                    "confidence": r.open_signal.confidence,
                    "entry": r.open_signal.entry,
                    "stop": r.open_signal.stop,
                    "target": r.open_signal.target,
                    "timestamp": r.resolution_time,
                }

        all_strats = set(open_by_strat.keys()) | set(resolved_by_strat.keys())
        for sid in all_strats:
            open_sig = open_by_strat.get(sid)
            resolved_sig = resolved_by_strat.get(sid)

            if open_sig and resolved_sig:
                last = open_sig if open_sig["timestamp"] >= resolved_sig["timestamp"] else resolved_sig
            elif open_sig:
                last = open_sig
            else:
                last = resolved_sig

            if last:
                triggers[sid] = {
                    "side": "BUY" if last["direction"] == "LONG" else "SELL",
                    "confidence": round(last["confidence"], 3),
                    "entry": round(last["entry"], 2),
                    "stop": round(last["stop"], 2),
                    "target": round(last["target"], 2),
                    "timestamp": last["timestamp"],
                }

        return triggers

    def _build_strategy_health(self) -> Dict[str, Dict[str, Any]]:
        """Build per-strategy health data for the heatmap JSON export."""
        if not self._strategy_engine or not self._signal_tracker:
            return {}

        health: Dict[str, Dict[str, Any]] = {}
        now = time.time()
        strat_stats = self._signal_tracker.get_strategy_stats()

        for strat in self._strategy_engine._strategies:
            sid = strat.strategy_id
            stats = strat_stats.get(sid, {})

            signal_count = 0
            last_signal_ts = 0.0
            sparkline_values: list = []

            resolved = self._signal_tracker.get_resolved()
            strategy_resolved = [r for r in resolved if r.open_signal.strategy_id == sid]

            cumulative = 0.0
            for r in strategy_resolved[-8:]:
                cumulative += r.pnl
                sparkline_values.append(round(cumulative, 2))

            while len(sparkline_values) < 8:
                sparkline_values.insert(0, 0.0)

            total_signals = stats.get("total_signals", 0)
            wins = stats.get("wins", 0)
            losses = stats.get("losses", 0)
            closed = stats.get("closed", 0)
            resolved_count = wins + losses + closed

            win_rate = wins / resolved_count if resolved_count > 0 else 0.0
            pnl = stats.get("total_pnl", 0.0)

            status = "active" if total_signals > 0 else "idle"

            open_signals = self._signal_tracker.get_open_signals()
            has_open = any(s.strategy_id == sid for s in open_signals)
            if has_open and status == "idle":
                status = "active"

            for s in open_signals:
                if s.strategy_id == sid and s.timestamp > last_signal_ts:
                    last_signal_ts = s.timestamp
            for r in strategy_resolved:
                if r.resolution_time > last_signal_ts:
                    last_signal_ts = r.resolution_time

            health[sid] = {
                "status": status,
                "signal_count": total_signals,
                "last_signal_ts": last_signal_ts,
                "win_rate": round(win_rate, 4),
                "pnl": round(pnl, 2),
                "sparkline": sparkline_values[-8:],
            }

        return health

    def _build_depth_snapshot(self) -> Dict[str, Any]:
        """Build current depth snapshot from rolling windows."""
        snap: Dict[str, Any] = {}
        for rw_key, short_key in [
            (KEY_DEPTH_BID_SIZE_5M, "bid_size"),
            (KEY_DEPTH_ASK_SIZE_5M, "ask_size"),
            (KEY_DEPTH_SPREAD_5M, "spread"),
            (KEY_DEPTH_BID_LEVELS_5M, "bid_levels"),
            (KEY_DEPTH_ASK_LEVELS_5M, "ask_levels"),
            (KEY_BID_PARTICIPANTS_5M, "bid_participants"),
            (KEY_ASK_PARTICIPANTS_5M, "ask_participants"),
            (KEY_BID_EXCHANGES_5M, "bid_exchanges"),
            (KEY_ASK_EXCHANGES_5M, "ask_exchanges"),
            (KEY_CONVICT_SCORE_5M, "conviction_score"),
            (KEY_FRAGILITY_BID_5M, "fragility_bid"),
            (KEY_FRAGILITY_ASK_5M, "fragility_ask"),
            (KEY_DECAY_VELOCITY_BID_5M, "decay_velocity_bid"),
            (KEY_DECAY_VELOCITY_ASK_5M, "decay_velocity_ask"),
            (KEY_TOP_WALL_BID_SIZE_5M, "top_wall_bid_size"),
            (KEY_TOP_WALL_ASK_SIZE_5M, "top_wall_ask_size"),
            (KEY_AGGRESSOR_VSI_5M, "aggressor_vsi"),
            (KEY_AGGRESSOR_VSI_ROC_5M, "aggressor_vsi_roc"),
            (KEY_IEX_INTENT_SCORE_5M, "iex_intent_score"),
            (KEY_MEMX_VSI_5M, "memx_vsi"),
            (KEY_BATS_VSI_5M, "bats_vsi"),
            (KEY_VENUE_CONCENTRATION_5M, "venue_concentration"),
            (KEY_ESI_MEMX_5M, "esi_memx"),
            (KEY_ESI_MEMX_ROC_5M, "esi_memx_roc"),
            (KEY_ESI_BATS_5M, "esi_bats"),
            (KEY_ESI_BATS_ROC_5M, "esi_bats_roc"),
            (KEY_MEMX_VOL_RATIO_5M, "memx_vol_ratio"),
            (KEY_BATS_VOL_RATIO_5M, "bats_vol_ratio"),
            (KEY_ESI_BASELINE_MEMX_1H, "esi_baseline_memx"),
            (KEY_ESI_BASELINE_BATS_1H, "esi_baseline_bats"),
        ]:
            rw = self._rolling_data.get(rw_key)
            if rw and rw.count > 0:
                snap[short_key] = {
                    "current": rw.values[-1] if rw.values else 0,
                    "mean": sum(rw.values) / len(rw.values) if rw.values else 0,
                    "count": rw.count,
                }
        return snap

    # ------------------------------------------------------------------
    # Dashboard and Heatmap management
    # ------------------------------------------------------------------

    def _start_dashboard(self) -> None:
        """Spawn the Streamlit Command Center as a background subprocess."""
        if self._dashboard_process is not None:
            return

        env = os.environ.copy()
        env["SYNGEX_SYMBOL"] = self.symbol

        script_path = Path(__file__).parent.parent / "app_dashboard.py"
        venv_streamlit = Path(__file__).parent.parent / "venv" / "bin" / "streamlit"

        logger.info("Starting Command Center...")

        try:
            self._dashboard_process = subprocess.Popen(
                [
                    str(venv_streamlit),
                    "run",
                    str(script_path),
                    "--server.headless",
                    "true",
                    "--browser.gatherUsageStats",
                    "false",
                    "--server.port",
                    str(self._port),
                ],
                cwd=str(Path(__file__).parent.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
            logger.info(
                "Command Center started (PID %d, port %d).  "
                "Open http://localhost:%d in a browser.",
                self._dashboard_process.pid, self._port, self._port,
            )
        except FileNotFoundError:
            logger.warning("Streamlit not found — Command Center will not start.")
        except Exception as exc:
            logger.warning("Command Center (Streamlit) startup failed: %s", exc)

    def _stop_dashboard(self) -> None:
        """Terminate the Streamlit Command Center subprocess."""
        if self._dashboard_process is None:
            return

        logger.info("Stopping Command Center (PID %d)...", self._dashboard_process.pid)
        try:
            self._dashboard_process.terminate()
            self._dashboard_process.wait(timeout=5)
        except Exception as e:
            logger.debug("Dashboard termination failed, attempting kill: %s", e)
            try:
                self._dashboard_process.kill()
            except Exception as kill_exc:
                logger.debug("Dashboard kill also failed: %s", kill_exc)
        finally:
            self._dashboard_process = None

    def _start_heatmap(self) -> None:
        """Spawn the Heatmap Dashboard as a background subprocess."""
        if self._heatmap_process is not None:
            return

        heatmap_port = self._port + 1
        env = os.environ.copy()
        env["SYNGEX_SYMBOL"] = self.symbol
        env["HEATMAP_PORT"] = str(heatmap_port)

        script_path = Path(__file__).parent.parent / "app_heatmap.py"
        venv_python = Path(__file__).parent.parent / "venv" / "bin" / "python"
        log_path = self._data_dir.parent / "log" / "heatmap.log"

        logger.info("Starting Heatmap Dashboard...")

        try:
            self._heatmap_stderr = open(log_path, "a")
            self._heatmap_process = subprocess.Popen(
                [str(venv_python), str(script_path)],
                cwd=str(Path(__file__).parent.parent),
                stdout=subprocess.DEVNULL,
                stderr=self._heatmap_stderr,
                env=env,
            )
            ret = self._heatmap_process.poll()
            if ret is not None:
                self._heatmap_process.wait()
                try:
                    with open(log_path, "r") as f:
                        err_msg = f.read().strip()
                except OSError:
                    err_msg = "unknown"
                logger.warning("Heatmap Dashboard failed to start (exit %d): %s", ret, err_msg[:500])
                self._heatmap_process = None
                return
            logger.info(
                "Heatmap Dashboard started (PID %d, port %d).  "
                "Open http://localhost:%d in a browser.",
                self._heatmap_process.pid, heatmap_port, heatmap_port,
            )
        except FileNotFoundError:
            logger.warning("app_heatmap.py not found — Heatmap Dashboard will not start.")
        except Exception as exc:
            logger.warning("Heatmap Dashboard startup failed: %s", exc)

    def _stop_heatmap(self) -> None:
        """Terminate the Heatmap Dashboard subprocess."""
        if self._heatmap_process is None:
            return

        logger.info("Stopping Heatmap Dashboard (PID %d)...", self._heatmap_process.pid)
        try:
            self._heatmap_process.terminate()
            self._heatmap_process.wait(timeout=5)
        except Exception as e:
            logger.debug("Heatmap termination failed, attempting kill: %s", e)
            try:
                self._heatmap_process.kill()
            except Exception as kill_exc:
                logger.debug("Heatmap kill also failed: %s", kill_exc)
        finally:
            if self._heatmap_stderr is not None:
                try:
                    self._heatmap_stderr.close()
                except Exception as close_exc:
                    logger.debug("Heatmap stderr close failed: %s", close_exc)
                self._heatmap_stderr = None
            self._heatmap_process = None

    # ------------------------------------------------------------------
    # Phi accumulator persistence
    # ------------------------------------------------------------------

    def _persist_phi_accumulators(self) -> None:
        """Write current phi tick accumulators to disk for crash recovery."""
        now = time.time()
        if now - self._phi_last_write < self.PHI_WRITE_INTERVAL:
            return

        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            state = {
                "_phi_call_tick": self._phi_call_tick,
                "_phi_put_tick": self._phi_put_tick,
            }
            with open(self._phi_state_file, "w") as f:
                json.dump(state, f)
            self._phi_last_write = now
        except Exception as exc:
            logger.debug("Phi accumulator persistence failed: %s", exc)

    def _load_phi_accumulators(self) -> None:
        """Load persisted phi tick accumulators from disk on startup."""
        try:
            if not self._phi_state_file.exists():
                return
            with open(self._phi_state_file, "r") as f:
                state = json.load(f)
            self._phi_call_tick = float(state.get("_phi_call_tick", 0.0))
            self._phi_put_tick = float(state.get("_phi_put_tick", 0.0))
            if self._phi_call_tick > 0 or self._phi_put_tick > 0:
                logger.info(
                    "Restored phi accumulators: call=%.4f put=%.4f",
                    self._phi_call_tick, self._phi_put_tick,
                )
        except Exception as exc:
            logger.debug("Phi accumulator load failed: %s", exc)

    # ------------------------------------------------------------------
    # GEX state export
    # ------------------------------------------------------------------

    def _export_gex_state(self) -> None:
        """Write the current GEX state to a shared JSON file."""
        assert self._calculator is not None

        state = self._calculator.get_summary()
        profile = self._calculator.get_gamma_profile()

        export = {
            "symbol": state["symbol"],
            "underlying_price": state["underlying_price"],
            "net_gamma": state["net_gamma"],
            "active_strikes": state["active_strikes"],
            "total_messages": state["total_messages"],
            "strikes": profile["strikes"],
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        }

        if self._strategy_engine:
            export["strategy_engine"] = self._strategy_engine.get_status()
            export["strategy_health"] = self._build_strategy_health()
            export["last_trigger"] = self._build_last_trigger()
            recent = self._strategy_engine.get_recent_signals(20)
            micro_signals: Dict[str, Dict[str, Any]] = {}
            for sig in recent:
                strike = sig.get("target", sig.get("entry", 0))
                if strike:
                    key = f"{strike:.1f}"
                    if key not in micro_signals or sig.get("confidence", 0) > micro_signals[key]["confidence"]:
                        micro_signals[key] = {
                            "confidence": sig.get("confidence", 0),
                            "strategy": sig.get("strategy_id", ""),
                            "direction": sig.get("direction", ""),
                            "reason": sig.get("reason", ""),
                            "timestamp": sig.get("timestamp", ""),
                        }
            if micro_signals:
                export["micro_signals"] = micro_signals
        if self._gamma_filter:
            export["regime_filter"] = self._gamma_filter.get_status()

        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            with open(self._data_file, "w") as f:
                json.dump(export, f, indent=2)
        except Exception as exc:
            logger.warning("Failed to export GEX state: %s", exc)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    """Main entry point for the Syngex orchestrator."""
    parser = argparse.ArgumentParser(description="Syngex Pipeline Orchestrator")
    parser.add_argument("symbol", help="The ticker symbol to trade (e.g., TSLA)")
    parser.add_argument(
        "mode",
        nargs="?",
        default="stream",
        choices=["stream", "dashboard"],
        help="Run mode: 'stream' (terminal logging, default) or 'dashboard' (starts Streamlit)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port for the Streamlit Command Center (default: 8501)",
    )
    args = parser.parse_args()

    orchestrator = SyngexOrchestrator(
        symbol=args.symbol, mode=args.mode, port=args.port
    )

    loop = asyncio.get_running_loop()

    def _signal_handler() -> None:
        logger.info("Shutdown signal received.")
        asyncio.ensure_future(orchestrator.shutdown())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)

    try:
        await orchestrator.initialize()
        await orchestrator.connect()
        await orchestrator.run()
    except Exception as exc:
        logger.critical("Pipeline failure: %s", exc, exc_info=True)
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
