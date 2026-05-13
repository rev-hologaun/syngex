#!/usr/bin/env python3
"""
main.py — Syngex Orchestrator

Clean, robust entry point for Project Syngex.

Structured lifecycle:
    1. Initialize  → create components
    2. Connect     → establish data streams
    3. Run Loop    → process data, report Gamma Profile
    4. Cleanup     → graceful shutdown

Zero-noise logging: only high-level status and evolving Gamma Profile.

Usage:
    python3 main.py TSLA              # stream mode (terminal logging)
    python3 main.py TSLA dashboard    # dashboard mode (starts Streamlit)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import math
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

# Suppress all noisy loggers; only our orchestrator speaks
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
# Safety — READ-ONLY enforcement (blocks all order placement)
# ---------------------------------------------------------------------------
from config.trade_guard import READ_ONLY
if READ_ONLY:
    logger.info("🔒 SAFETY: READ-ONLY mode active — all order placement blocked")

# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

from ingestor.tradestation_client import TradeStationClient
from engine.gex_calculator import GEXCalculator
from strategies.engine import StrategyEngine, EngineConfig
from strategies.filters.net_gamma_filter import NetGammaFilter
from strategies.rolling_window import RollingWindow
from strategies.rolling_keys import (
    KEY_OBI_5M,
    KEY_AGGRESSIVE_BUY_VOL_5M,
    KEY_AGGRESSIVE_SELL_VOL_5M,
    KEY_AF_5M,
    KEY_TRADE_SIZE_5M,
    KEY_ATM_DELTA_5M,
    KEY_ATM_IV_5M,
    KEY_VOLUME_5M,
    KEY_VOLUME_DOWN_5M,
    KEY_VOLUME_UP_5M,
    KEY_NET_GAMMA_5M,
    KEY_TOTAL_DELTA_5M,
    KEY_WALL_DELTA_5M,
    KEY_TOTAL_GAMMA_5M,
    KEY_IV_SKEW_5M,
    KEY_SKEW_WIDTH_5M,
    KEY_FLOW_RATIO_5M,
    KEY_EXTRINSIC_PROXY_5M,
    KEY_EXTRINSIC_ROC_5M,
    KEY_PROB_MOMENTUM_5M,
    KEY_PHI_CALL_5M,
    KEY_PHI_PUT_5M,
    KEY_PHI_RATIO_5M,
    KEY_PHI_TOTAL_5M,
    KEY_PHI_TOTAL_SIGMA_5M,
    KEY_IV_SKEW_GRADIENT_5M,
    KEY_GAMMA_DENSITY_5M,
    KEY_OTM_DELTA_5M,
    KEY_OTM_IV_5M,
    KEY_DELTA_IV_CORR_5M,
    KEY_CONSEC_LONG,
    KEY_CONSEC_SHORT,
    KEY_WALL_DISTANCE_5M,
    KEY_WALL_GEX_5M,
    KEY_WALL_GEX_SIGMA_5M,
    KEY_PRICE_VELOCITY_5M,
    KEY_GAMMA_BREAK_INDEX_5M,
    KEY_CONFLUENCE_PROX_5M,
    KEY_CONFLUENCE_SIGNAL_5M,
    KEY_LIQUIDITY_WALL_SIZE_5M,
    KEY_LIQUIDITY_WALL_SIGMA_5M,
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_ASK_SIZE_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_DEPTH_BID_LEVELS_5M,
    KEY_DEPTH_ASK_LEVELS_5M,
    KEY_DEPTH_BID_SIZE_ROLLING,
    KEY_DEPTH_ASK_SIZE_ROLLING,
    KEY_SKEW_ROC_5M,
    KEY_DELTA_ROC_5M,
    KEY_STRIKE_DELTA_5M,
    KEY_ATR_5M,
    KEY_MAGNET_DELTA_5M,
    KEY_MOMENTUM_ROC_5M,
    KEY_VAMP_5M,
    KEY_VAMP_MID_DEV_5M,
    KEY_VAMP_ROC_5M,
    KEY_VAMP_PARTICIPANTS_5M,
    KEY_VAMP_DEPTH_DENSITY_5M,
    KEY_PRICE_5M,
    KEY_PRICE_30M,
    KEY_DEPTH_DECAY_BID_5M,
    KEY_DEPTH_DECAY_ASK_5M,
    KEY_DEPTH_TOP5_BID_5M,
    KEY_DEPTH_TOP5_ASK_5M,
    KEY_DEPTH_VOL_RATIO_5M,
    KEY_IR_5M,
    KEY_IR_ROC_5M,
    KEY_IR_PARTICIPANTS_5M,
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
    KEY_ESI_BASELINE_MEMX_1H,
    KEY_ESI_BASELINE_BATS_1H,
    KEY_MEMX_VOL_RATIO_5M,
    KEY_BATS_VOL_RATIO_5M,
    KEY_DEPTH_BID_LEVEL_AVG_5M,
    KEY_DEPTH_ASK_LEVEL_AVG_5M,
    KEY_SIS_BID_5M,
    KEY_SIS_ASK_5M,
    KEY_SIS_BID_ROC_5M,
    KEY_SIS_ASK_ROC_5M,
    KEY_PDR_5M,
    KEY_PDR_ROC_5M,
    KEY_SKEW_PSI_5M,
    KEY_SKEW_PSI_ROC_5M,
    KEY_SKEW_PSI_SIGMA_5M,
    KEY_PUT_SLOPE_5M,
    KEY_CALL_SLOPE_5M,
    KEY_CURVE_OMEGA_5M,
    KEY_CURVE_OMEGA_ROC_5M,
    KEY_CURVE_OMEGA_SIGMA_5M,
    KEY_SYNC_CORR_5M,
    KEY_SYNC_SIGMA_5M,
    KEY_SKEW_CHANGE_5M,
    KEY_VSI_MAGNITUDE_5M,
    KEY_BIGGEST_SIZE_5M,
    KEY_SMALLEST_SIZE_5M,
    KEY_CONCENTRATION_RATIO_5M,
    KEY_CONCENTRATION_SIGMA_5M,
    KEY_NUM_PARTICIPANTS_5M,
    KEY_IEX_INTENT_5M,
    KEY_VSI_COMBINED_5M,
    KEY_VSI_ROC_5M,
    KEY_SPREAD_ZSCORE_5M,
    KEY_LIQUIDITY_DENSITY_5M,
    KEY_PARTICIPANT_EQUILIBRIUM_5M,
    KEY_VOLUME_SPIKE_5M,
    KEY_MARKET_DEPTH_AGG,
    KEY_VAMP_LEVELS,
)
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
from strategies.signal_tracker import SignalTracker


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def _compute_linear_slope(x_vals, y_vals):
    """Compute slope using least-squares linear regression."""
    n = len(x_vals)
    if n < 2:
        return 0.0
    x_mean = sum(x_vals) / n
    y_mean = sum(y_vals) / n
    numerator = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
    denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
    if denominator == 0:
        return 0.0
    return numerator / denominator


class SyngexOrchestrator:
    """
    Manages the full lifecycle of the Syngex pipeline.

    Lifecycle:
        initialize() → connect() → run() → shutdown()
    """

    # How often (seconds) to log the Gamma Profile
    PROFILE_INTERVAL: float = 5.0

    # How often (seconds) to persist phi accumulators to disk
    PHI_WRITE_INTERVAL: float = 5.0

    def __init__(
        self, symbol: str, mode: str = "stream", port: int = 8501
    ) -> None:
        self.symbol = symbol.upper()
        self.mode = mode.lower()
        self._port = port
        self._client: TradeStationClient | None = None
        self._calculator: GEXCalculator | None = None
        self._dashboard: SyngexDashboard | None = None
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
        self._heatmap_stderr: Any = None  # file handle for heatmap stderr
        self._state_export_timer: float = 0.0

        # Shared data file for Streamlit dashboard (symbol-specific)
        self._data_dir = Path(__file__).parent / "data"
        self._data_file = self._data_dir / f"gex_state_{self.symbol}.json"

        # Strategy configuration (loaded from YAML in initialize())
        self._strategy_config: Dict[str, Any] = {}
        self._config_path = Path(__file__).parent / "config" / "strategies.yaml"
        self._config_mtime: float = 0.0  # Last known modification time
        self._config_lock = asyncio.Lock()  # Thread-safe config reload

        # Signal outcome tracker
        self._signal_tracker: SignalTracker | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Create and wire all components."""
        logger.info("Initializing components…")

        self._calculator = GEXCalculator(symbol=self.symbol)
        self._client = TradeStationClient()

        # Phase 0: Strategy Engine + Filter

        # Load strategy configuration from YAML
        config_path = Path(__file__).parent / "config" / "strategies.yaml"
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
        self._signal_tracker = SignalTracker(
            max_hold_seconds=900,  # global default
            strategy_hold_times=strategy_hold_times,
            log_dir=str(log_dir),
            symbol=self.symbol,
        )

        # Apply global config to EngineConfig
        global_config = self._strategy_config.get("global", {})
        self._strategy_engine = StrategyEngine(
            config=EngineConfig(
                min_confidence=global_config.get("min_confidence", 0.15),
                max_signals_per_tick=global_config.get("max_signals_per_tick", 10),
                dedup_window_seconds=global_config.get("dedup_window_seconds", 60.0),
            ),
            signal_tracker=self._signal_tracker,
        )
        # Register strategies from config (config-driven, not hardcoded)
        self._register_strategies_from_config()

        # Register Layer 0 (master filter) — controlled by config
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

        # Call/put update counters for volume_up/volume_down tracking
        self._call_update_count: int = 0
        self._put_update_count: int = 0

        # Extrinsic Value Flow — Φ (Premium Conviction) per-tick accumulators
        self._phi_call_tick: float = 0.0
        self._phi_put_tick: float = 0.0

        # Crash-recovery state file for phi accumulators (symbol-specific)
        self._phi_state_file = self._data_dir / f"phi_state_{self.symbol}.json"

        # Phi write throttle — rate-limit disk writes to avoid excessive I/O
        self._phi_last_write: float = 0.0  # time.time() of last successful write

        # Load persisted phi accumulators (crash recovery)
        self._load_phi_accumulators()

        # Per-strike IV windows (populated lazily)
        self._iv_windows: Dict[str, RollingWindow] = {}

        # Wire callback: ingestor → calculator + engine
        self._client.set_on_message_callback(self._on_message)

        # Register subscriptions — quotes feed underlying price, option chain feeds contracts
        self._client.subscribe_to_quotes(self.symbol)
        self._client.subscribe_to_option_chain(self.symbol)
        # L2 market depth streams
        self._client.subscribe_to_market_depth_quotes(self.symbol)
        self._client.subscribe_to_market_depth_aggregates(self.symbol)

        logger.info("Components initialized. Symbol: %s", self.symbol)

    async def connect(self) -> None:
        """Establish streaming connections."""
        assert self._client is not None
        logger.info("Connecting to TradeStation streams…")
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
        self._strategy_eval_timer = time.monotonic()
        self._state_export_timer = time.monotonic()

        # Start strategy engine
        self._strategy_engine.start()

        logger.info("Pipeline running. Ctrl+C to stop.  Mode: %s", self.mode)
        logger.info("Strategy engine: %d strategies registered, filter active", len(self._strategy_engine._strategies))

        # Start the Streamlit dashboard and heatmap as background subprocesses (dashboard mode only)
        if self.mode == "dashboard":
            self._start_dashboard()
            self._start_heatmap()

        try:
            # Start config watcher task
            config_task = asyncio.create_task(self._watch_config())

            while self._running:
                now = time.monotonic()

                # Report Gamma Profile at intervals
                if now - self._profile_timer >= self.PROFILE_INTERVAL:
                    self._report_profile()
                    self._profile_timer = now

                # Export GEX state to shared file for Streamlit dashboard
                if now - self._state_export_timer >= 1.0:
                    self._export_gex_state()
                    self._state_export_timer = now

                # Signal resolution (every ~1s)
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

                # Strategy evaluation (every ~1s)
                if now - self._strategy_eval_timer >= 1.0:
                    self._evaluate_strategies()
                    self._strategy_eval_timer = now

                # Fail-fast: option chain critical error
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
        logger.info("Shutting down…")
        self._running = False

        # Stop strategy engine
        if self._strategy_engine:
            self._strategy_engine.stop()
            logger.info("Strategy engine: %d signals produced", self._strategy_engine.signal_count)

        # Stop dashboard subprocess
        self._stop_dashboard()
        # Stop heatmap subprocess
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
                    return  # No change

                with open(self._config_path, "r") as f:
                    strategy_config = yaml.safe_load(f)

                self._config_mtime = mtime
                self._strategy_config = strategy_config

                # Apply global config
                global_cfg = strategy_config.get("global", {})
                if global_cfg and self._strategy_engine:
                    self._strategy_engine.config.min_confidence = global_cfg.get("min_confidence", 0.15)
                    self._strategy_engine.config.max_signals_per_tick = global_cfg.get("max_signals_per_tick", 10)
                    self._strategy_engine.config.dedup_window_seconds = global_cfg.get("dedup_window_seconds", 60.0)

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
            ts = time.time()

            # Update rolling windows with underlying price
            if data.get("type") == "underlying_update":
                price = data.get("price")
                if price and price > 0:
                    self._rolling_data[KEY_PRICE_5M].push(price, ts)
                    self._rolling_data[KEY_PRICE_30M].push(price, ts)

                    # ATR: std_dev of price_5m * sqrt(5) (Strike Conc v2)
                    if KEY_ATR_5M in self._rolling_data:
                        price_vals = self._rolling_data[KEY_PRICE_5M].values
                        if len(price_vals) >= 5:
                            mean_p = sum(price_vals) / len(price_vals)
                            var = sum((x - mean_p) ** 2 for x in price_vals) / len(price_vals)
                            atr = math.sqrt(var) * math.sqrt(5)
                            self._rolling_data[KEY_ATR_5M].push(atr, ts)

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

                # Premium Divergence Ratio (Ghost Premium / TVD-Alpha)
                theoretical_value = data.get("theoretical_value", 0.0)
                mid = data.get("mid", 0.0)
                if theoretical_value and theoretical_value > 0.01:
                    pdr = (mid - theoretical_value) / theoretical_value
                    pdr_window = self._rolling_data.get(KEY_PDR_5M)
                    if pdr_window:
                        pdr_window.push(pdr, ts)
                    # PDR ROC: rate of change over 5m window
                    pdr_roc_window = self._rolling_data.get(KEY_PDR_ROC_5M)
                    if pdr_window and pdr_roc_window and pdr_window.count >= 2:
                        first_pdr = pdr_window.values[0]
                        if abs(first_pdr) > 0.001:
                            pdr_roc = (pdr - first_pdr) / abs(first_pdr)
                            pdr_roc_window.push(pdr_roc, ts)

                # Extrinsic Value Flow — Φ (Premium Conviction)
                # Φ = Volume × ExtrinsicValue, tracked per side
                # Delta purity filter: only 15-65 delta contracts
                try:
                    extrinsic = data.get("extrinsic_value", 0.0)
                    volume = data.get("volume", 0)
                    delta = data.get("delta", 0.0)
                    if extrinsic and extrinsic > 0 and volume and volume > 0:
                        abs_delta = abs(delta) if delta else 0.0
                        if 0.15 <= abs_delta <= 0.65:
                            phi = volume * extrinsic
                            if side == "call":
                                self._phi_call_tick += phi
                            elif side == "put":
                                self._phi_put_tick += phi
                except Exception:
                    pass

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

                # gamma_accel_5m — 2nd derivative of gamma (v2 Ignition-Master)
                # iv_skew_5m — avg call IV minus avg put IV
                try:
                    iv_skew = self._calculator.get_iv_skew()
                    if iv_skew is not None:
                        self._rolling_data[KEY_IV_SKEW_5M].push(iv_skew)
                except Exception:
                    pass

                # iv_skew_squeeze v2 — Skew ROC (rate of change over 5m window)
                try:
                    skew_window = self._rolling_data.get(KEY_IV_SKEW_5M)
                    if (skew_window is not None and skew_window.count >= 2
                            and KEY_SKEW_ROC_5M in self._rolling_data):
                        first_val = skew_window.values[0]
                        if abs(first_val) > 0:
                            skew_roc = (iv_skew - first_val) / abs(first_val)
                            self._rolling_data[KEY_SKEW_ROC_5M].push(skew_roc)
                except Exception:
                    pass

                # IV Skew Dynamics — Ψ (Skewness Coefficient)
                # Ψ = (IV_Put_Wing - IV_Call_Wing) / IV_ATM
                try:
                    underlying_price = self._calculator.underlying_price
                    iv_by_strike = self._calculator.get_iv_by_strike_avg()
                    if iv_by_strike:
                        strikes = sorted(iv_by_strike.keys())
                        if len(strikes) >= 3:
                            atm_strike = min(
                                strikes, key=lambda s: abs(s - underlying_price)
                            )
                            atm_iv = iv_by_strike[atm_strike]

                            call_ivs = [
                                iv_by_strike[s] for s in strikes if s > atm_strike
                            ]
                            put_ivs = [
                                iv_by_strike[s] for s in strikes if s < atm_strike
                            ]

                            if call_ivs and put_ivs and atm_iv > 0:
                                # Use outermost available as wing proxy
                                n_calls = max(1, len(call_ivs) // 4)
                                n_puts = max(1, len(put_ivs) // 4)
                                call_wing_iv = (
                                    sum(sorted(call_ivs, reverse=True)[:n_calls])
                                    / n_calls
                                )
                                put_wing_iv = (
                                    sum(sorted(put_ivs)[:n_puts]) / n_puts
                                )

                                psi = (put_wing_iv - call_wing_iv) / atm_iv

                                psi_window = self._rolling_data.get(
                                    KEY_SKEW_PSI_5M
                                )
                                if psi_window:
                                    psi_window.push(psi, ts)

                                # Ψ ROC
                                psi_roc_window = self._rolling_data.get(
                                    KEY_SKEW_PSI_ROC_5M
                                )
                                if (
                                    psi_window
                                    and psi_roc_window
                                    and psi_window.count >= 2
                                ):
                                    first_psi = psi_window.values[0]
                                    if abs(first_psi) > 0.0001:
                                        psi_roc = (
                                            (psi - first_psi) / abs(first_psi)
                                        )
                                        psi_roc_window.push(psi_roc, ts)

                                # Ψ σ
                                psi_sigma_window = self._rolling_data.get(
                                    KEY_SKEW_PSI_SIGMA_5M
                                )
                                if (
                                    psi_window
                                    and psi_sigma_window
                                    and psi_window.count >= 5
                                ):
                                    vals = list(psi_window.values)
                                    mean_psi = sum(vals) / len(vals)
                                    var = sum(
                                        (x - mean_psi) ** 2 for x in vals
                                    ) / len(vals)
                                    std_psi = math.sqrt(var)
                                    psi_sigma_window.push(std_psi, ts)
                except Exception:
                    pass

                # IV Smile Dynamics — Ω (Curvature Asymmetry Index)
                # Ω = |Slope_Put_Wing| / |Slope_Call_Wing|
                # Slope = dIV/dK (derivative of IV vs moneyness via least-squares)
                try:
                    underlying_price = self._calculator.underlying_price
                    iv_by_strike = self._calculator.get_iv_by_strike_avg()
                    if iv_by_strike:
                        strikes = sorted(iv_by_strike.keys())
                        if len(strikes) >= 6:
                            atm_strike = min(
                                strikes, key=lambda s: abs(s - underlying_price)
                            )
                            put_strikes = [
                                (s, iv_by_strike[s])
                                for s in strikes
                                if s < atm_strike and iv_by_strike[s] > 0.01
                            ]
                            call_strikes = [
                                (s, iv_by_strike[s])
                                for s in strikes
                                if s > atm_strike and iv_by_strike[s] > 0.01
                            ]
                            if len(put_strikes) >= 2 and len(call_strikes) >= 2:
                                put_x = [s / atm_strike for s, iv in put_strikes]
                                put_y = [iv for s, iv in put_strikes]
                                put_slope = _compute_linear_slope(put_x, put_y)

                                call_x = [s / atm_strike for s, iv in call_strikes]
                                call_y = [iv for s, iv in call_strikes]
                                call_slope = _compute_linear_slope(call_x, call_y)

                                if abs(call_slope) > 0.0001:
                                    omega = abs(put_slope) / abs(call_slope)

                                    omega_window = self._rolling_data.get(
                                        KEY_CURVE_OMEGA_5M
                                    )
                                    if omega_window:
                                        omega_window.push(omega, ts)

                                    ps_window = self._rolling_data.get(
                                        KEY_PUT_SLOPE_5M
                                    )
                                    if ps_window:
                                        ps_window.push(put_slope, ts)

                                    cs_window = self._rolling_data.get(
                                        KEY_CALL_SLOPE_5M
                                    )
                                    if cs_window:
                                        cs_window.push(call_slope, ts)

                                    # Ω ROC
                                    omega_roc_window = self._rolling_data.get(
                                        "curve_omega_roc_5m"
                                    )
                                    if (omega_window and omega_roc_window
                                            and omega_window.count >= 2):
                                        first_omega = omega_window.values[0]
                                        if abs(first_omega) > 0.0001:
                                            omega_roc = (
                                                (omega - first_omega) / abs(first_omega)
                                            )
                                            omega_roc_window.push(omega_roc, ts)

                                    # Ω σ
                                    omega_sigma_window = self._rolling_data.get(
                                        "curve_omega_sigma_5m"
                                    )
                                    if (omega_window and omega_sigma_window
                                            and omega_window.count >= 5):
                                        vals = list(omega_window.values)
                                        mean_omega = sum(vals) / len(vals)
                                        var = sum(
                                            (x - mean_omega) ** 2 for x in vals
                                        ) / len(vals)
                                        std_omega = math.sqrt(var)
                                        omega_sigma_window.push(std_omega, ts)
                except Exception:
                    pass

                # volume_up_5m / volume_down_5m — call/put update counts as proxy
                self._rolling_data[KEY_VOLUME_UP_5M].push(self._call_update_count)
                self._rolling_data[KEY_VOLUME_DOWN_5M].push(self._put_update_count)

                # extrinsic_proxy_5m — aggregate extrinsic value proxy
                extrinsic_proxy = self._calculate_extrinsic_proxy(gex_summary)
                if extrinsic_proxy is not None:
                    self._rolling_data[KEY_EXTRINSIC_PROXY_5M].push(extrinsic_proxy)

                # extrinsic_roc_5m — v2 Conviction-Master: ROC + acceleration of extrinsic
                try:
                    ext_window = self._rolling_data.get(KEY_EXTRINSIC_PROXY_5M)
                    if (ext_window is not None and ext_window.count >= 6
                            and KEY_EXTRINSIC_ROC_5M in self._rolling_data):
                        vals = list(ext_window.values)
                        current_ext = vals[-1]
                        # Extrinsic ROC: change over last 5 data points (~5 min)
                        if len(vals) >= 6 and abs(vals[-6]) > 0:
                            ext_roc = (current_ext - vals[-6]) / abs(vals[-6])
                        else:
                            ext_roc = 0.0
                        # Extrinsic acceleration: ROC change over last 5 points
                        if len(vals) >= 11 and abs(vals[-11]) > 0:
                            prev_roc = (vals[-6] - vals[-11]) / abs(vals[-11])
                            ext_accel = (ext_roc - prev_roc) / abs(prev_roc) if abs(prev_roc) > 0 else 0.0
                        else:
                            ext_accel = 0.0
                        self._rolling_data[KEY_EXTRINSIC_ROC_5M].push(ext_accel, time.time())
                except Exception:
                    pass

                # Commit per-tick Φ accumulators to rolling windows
                if self._phi_call_tick > 0 or self._phi_put_tick > 0:
                    phi_call_w = self._rolling_data.get(KEY_PHI_CALL_5M)
                    if phi_call_w:
                        phi_call_w.push(self._phi_call_tick, ts)
                    phi_put_w = self._rolling_data.get(KEY_PHI_PUT_5M)
                    if phi_put_w:
                        phi_put_w.push(self._phi_put_tick, ts)
                    total = self._phi_call_tick + self._phi_put_tick
                    if total > 0:
                        phi_total_w = self._rolling_data.get(KEY_PHI_TOTAL_5M)
                        if phi_total_w:
                            phi_total_w.push(total, ts)
                        phi_ratio_w = self._rolling_data.get(KEY_PHI_RATIO_5M)
                        if phi_put_w and self._phi_put_tick > 0:
                            ratio = self._phi_call_tick / self._phi_put_tick
                            phi_ratio_w.push(ratio, ts)
                        # Φ total σ
                        phi_sig_w = self._rolling_data.get(KEY_PHI_TOTAL_SIGMA_5M)
                        if phi_total_w and phi_sig_w and phi_total_w.count >= 5:
                            vals = list(phi_total_w.values)
                            mean_t = sum(vals) / len(vals)
                            var = sum((x - mean_t) ** 2 for x in vals) / len(vals)
                            phi_sig_w.push(math.sqrt(var), ts)
                    # Reset per-tick accumulators
                    self._phi_call_tick = 0.0
                    self._phi_put_tick = 0.0
                    # Persist state (crash recovery)
                    self._persist_phi_accumulators()

                # Gamma Breaker — Γ_break (Gamma Breakout Index)
                # Γ_break = Price_Velocity × Gamma_Concentration_at_Level
                try:
                    price = self._calculator.underlying_price
                    if price > 0:
                        # Get nearest gamma walls
                        walls = self._calculator.get_gamma_walls(threshold=100000)

                        if walls:
                            nearest_wall = walls[0]  # Largest GEX wall
                            wall_strike = nearest_wall["strike"]
                            wall_gex = nearest_wall["gex"]
                            wall_side = nearest_wall["side"]

                            # Distance to wall as % of price
                            wall_dist_pct = abs(wall_strike - price) / price

                            # Gamma concentration: wall GEX / average GEX across all walls
                            all_gex = [abs(w["gex"]) for w in walls]
                            avg_gex = sum(all_gex) / len(all_gex) if all_gex else 1.0
                            gamma_concentration = abs(wall_gex) / avg_gex if avg_gex > 0 else 1.0

                            # Price velocity: |net_change_pct| over 5m
                            price_window = self._rolling_data.get(KEY_PRICE_5M)
                            if price_window and price_window.count >= 2:
                                velocity = abs(price_window.values[-1] - price_window.values[0]) / abs(price_window.values[0]) if price_window.values[0] != 0 else 0.0
                            else:
                                velocity = 0.0

                            # Γ_break = velocity × gamma_concentration
                            gamma_break = velocity * gamma_concentration

                            # Push to rolling windows
                            dist_w = self._rolling_data.get(KEY_WALL_DISTANCE_5M)
                            if dist_w: dist_w.push(wall_dist_pct, ts)

                            gex_w = self._rolling_data.get(KEY_WALL_GEX_5M)
                            if gex_w: gex_w.push(abs(wall_gex), ts)

                            # Wall GEX σ
                            gex_sig_w = self._rolling_data.get(KEY_WALL_GEX_SIGMA_5M)
                            if gex_w and gex_sig_w and gex_w.count >= 5:
                                vals = list(gex_w.values)
                                mean_g = sum(vals) / len(vals)
                                var = sum((x - mean_g)**2 for x in vals) / len(vals)
                                gex_sig_w.push(math.sqrt(var), ts)

                            vel_w = self._rolling_data.get(KEY_PRICE_VELOCITY_5M)
                            if vel_w: vel_w.push(velocity, ts)

                            gb_w = self._rolling_data.get(KEY_GAMMA_BREAK_INDEX_5M)
                            if gb_w: gb_w.push(gamma_break, ts)
                except Exception:
                    pass

                # Iron Anchor — Confluence Detection
                # Ω_conf = |Price_GammaWall - Price_LiquidityWall|
                # Match gamma walls with liquidity walls from depth aggregates
                try:
                    price = self._calculator.underlying_price
                    if price > 0:
                        # Get gamma walls (major walls only)
                        gamma_walls = self._calculator.get_gamma_walls(threshold=500000)

                        if gamma_walls:
                            # Get liquidity levels from depth aggregates
                            depth_agg = self._rolling_data.get(KEY_MARKET_DEPTH_AGG, {})
                            bid_levels = depth_agg.get("bid_levels", [])
                            ask_levels = depth_agg.get("ask_levels", [])

                            if bid_levels or ask_levels:
                                best_prox = float('inf')
                                best_signal = 0  # +1 bullish, -1 bearish
                                best_liq_size = 0

                                for wall in gamma_walls:
                                    wall_strike = wall["strike"]
                                    wall_side = wall["side"]  # "call" or "put"

                                    # Bid liquidity near put walls (bullish), ask near call walls (bearish)
                                    target_levels = bid_levels if wall_side == "put" else ask_levels

                                    if not target_levels:
                                        continue

                                    for level in target_levels:
                                        liq_price = level["price"]
                                        liq_size = level["size"]
                                        if liq_price <= 0:
                                            continue

                                        prox = abs(wall_strike - liq_price)
                                        if prox < best_prox:
                                            best_prox = prox
                                            best_signal = +1 if wall_side == "put" else -1
                                            best_liq_size = liq_size

                                # Push confluence metrics to rolling windows
                                prox_w = self._rolling_data.get(KEY_CONFLUENCE_PROX_5M)
                                if prox_w: prox_w.push(best_prox, ts)

                                sig_w = self._rolling_data.get(KEY_CONFLUENCE_SIGNAL_5M)
                                if sig_w: sig_w.push(best_signal, ts)

                                liq_w = self._rolling_data.get(KEY_LIQUIDITY_WALL_SIZE_5M)
                                if liq_w: liq_w.push(best_liq_size, ts)

                                # Liquidity wall σ
                                liq_sig_w = self._rolling_data.get(KEY_LIQUIDITY_WALL_SIGMA_5M)
                                if liq_w and liq_sig_w and liq_w.count >= 5:
                                    vals = list(liq_w.values)
                                    mean_l = sum(vals) / len(vals)
                                    var = sum((x - mean_l) ** 2 for x in vals) / len(vals)
                                    liq_sig_w.push(math.sqrt(var), ts)
                except Exception:
                    pass

                # Sentiment Sync — Γ_sync (Synchronization Engine)
                # Γ_sync = Sign(ΔSkew) × Sign(Aggressor_VSI)
                try:
                    # 1. Get skew change over rolling window
                    skew_window = self._rolling_data.get(KEY_IV_SKEW_5M)
                    if skew_window and skew_window.count >= 10:
                        first_skew = skew_window.values[0]
                        current_skew = skew_window.values[-1]
                        if abs(first_skew) > 0.001:
                            skew_change = (current_skew - first_skew) / abs(first_skew)
                        else:
                            skew_change = current_skew

                        # 2. Get aggressor VSI from rolling window
                        vsi_window = self._rolling_data.get(KEY_AGGRESSOR_VSI_5M)
                        if vsi_window and vsi_window.count >= 10:
                            current_vsi = vsi_window.values[-1]
                        else:
                            current_vsi = 0.0

                        # 3. Compute synchronization: sign agreement
                        skew_sign = 1.0 if skew_change > 0 else (-1.0 if skew_change < 0 else 0.0)
                        vsi_sign = 1.0 if current_vsi > 0 else (-1.0 if current_vsi < 0 else 0.0)

                        # Γ_sync: +1 = both positive (fear+selling), -1 = both negative (complacency+buying)
                        gamma_sync = skew_sign * vsi_sign

                        # 4. Compute σ for significance threshold
                        skew_vals = list(skew_window.values)
                        mean_skew = sum(skew_vals) / len(skew_vals)
                        skew_var = sum((x - mean_skew)**2 for x in skew_vals) / len(skew_vals)
                        skew_sigma = math.sqrt(skew_var) if skew_var > 0 else 0.001

                        vsi_vals = list(vsi_window.values)
                        mean_vsi = sum(vsi_vals) / len(vsi_vals)
                        vsi_var = sum((x - mean_vsi)**2 for x in vsi_vals) / len(vsi_vals)
                        vsi_sigma = math.sqrt(vsi_var) if vsi_var > 0 else 0.001

                        # Push to rolling windows
                        corr_w = self._rolling_data.get(KEY_SYNC_CORR_5M)
                        if corr_w: corr_w.push(gamma_sync, ts)

                        sig_w = self._rolling_data.get(KEY_SYNC_SIGMA_5M)
                        if sig_w: sig_w.push(max(skew_sigma, vsi_sigma), ts)

                        skew_chg_w = self._rolling_data.get(KEY_SKEW_CHANGE_5M)
                        if skew_chg_w: skew_chg_w.push(skew_change, ts)

                        vsi_mag_w = self._rolling_data.get(KEY_VSI_MAGNITUDE_5M)
                        if vsi_mag_w: vsi_mag_w.push(abs(current_vsi), ts)
                except Exception:
                    pass

                # prob_momentum_5m — probability distribution momentum
                prob_mom = self._calculate_prob_momentum(gex_summary)
                if prob_mom is not None:
                    self._rolling_data[KEY_PROB_MOMENTUM_5M].push(prob_mom)

                # ── prob_distribution_shift v2: Momentum ROC & acceleration ──
                try:
                    mom_window = self._rolling_data.get(KEY_PROB_MOMENTUM_5M)
                    if (mom_window is not None and mom_window.count >= 6
                            and KEY_MOMENTUM_ROC_5M in self._rolling_data):
                        vals = list(mom_window.values)
                        current_momentum = vals[-1]
                        # Momentum ROC: change over last 5 data points (~5 min)
                        if len(vals) >= 6 and abs(vals[-6]) > 0:
                            momentum_roc = (current_momentum - vals[-6]) / abs(vals[-6])
                        else:
                            momentum_roc = 0.0
                        # Momentum acceleration: ROC change over last 5 points
                        if len(vals) >= 11 and abs(vals[-11]) > 0:
                            prev_roc = (vals[-6] - vals[-11]) / abs(vals[-11])
                            momentum_accel = (momentum_roc - prev_roc) / abs(prev_roc) if abs(prev_roc) > 0 else 0.0
                        else:
                            momentum_accel = 0.0
                        self._rolling_data[KEY_MOMENTUM_ROC_5M].push(momentum_accel, time.time())
                except Exception:
                    pass

                # Push per-strike ATM delta and IV for delta_iv_divergence
                atm_price = self._calculator.underlying_price
                atm_strike = self._calculator.get_atm_strike(atm_price)
                if atm_strike is not None:
                    delta_data = self._calculator.get_delta_by_strike(atm_strike)
                    atm_delta = delta_data.get("net_delta", 0.0)
                    if KEY_ATM_DELTA_5M in self._rolling_data:
                        self._rolling_data[KEY_ATM_DELTA_5M].push(atm_delta)

                    # iv_skew_squeeze v2 — Delta ROC (rate of change over 5m window)
                    try:
                        delta_window = self._rolling_data.get(KEY_ATM_DELTA_5M)
                        if (delta_window is not None and delta_window.count >= 2
                                and KEY_DELTA_ROC_5M in self._rolling_data):
                            first_delta = delta_window.values[0]
                            if abs(first_delta) > 0:
                                delta_roc = (atm_delta - first_delta) / abs(first_delta)
                                self._rolling_data[KEY_DELTA_ROC_5M].push(delta_roc)
                    except Exception:
                        pass

                    atm_iv = self._calculator.get_iv_by_strike(atm_strike)
                    if atm_iv is not None and KEY_ATM_IV_5M in self._rolling_data:
                        self._rolling_data[KEY_ATM_IV_5M].push(atm_iv)

                # ── prob_weighted_magnet v2: Magnet delta ROC tracking ──
                try:
                    if KEY_MAGNET_DELTA_5M in self._rolling_data and gex_summary:
                        price = self._calculator.underlying_price
                        if price and price > 0:
                            # Identify magnet strikes: highest OI strikes below/above price
                            magnet_strikes: List[float] = []
                            for strike_str, strike_data in gex_summary.items():
                                try:
                                    s = float(strike_str)
                                except (ValueError, TypeError):
                                    continue
                                call_oi = strike_data.get("call_oi", 0)
                                put_oi = strike_data.get("put_oi", 0)
                                total_oi = call_oi + put_oi
                                if total_oi < 1.0:
                                    continue
                                if s < price:
                                    magnet_strikes.append(s)
                                elif s > price:
                                    magnet_strikes.append(s)

                            if magnet_strikes:
                                # Pick the strike with highest OI as the magnet
                                best_strike = None
                                best_oi = 0.0
                                for ms in magnet_strikes:
                                    sd = gex_summary.get(str(ms), {})
                                    oi = sd.get("call_oi", 0) + sd.get("put_oi", 0)
                                    if oi > best_oi:
                                        best_oi = oi
                                        best_strike = ms

                                if best_strike is not None:
                                    delta_data = self._calculator.get_delta_by_strike(best_strike)
                                    current_delta = delta_data.get("net_delta", 0.0)
                                    # Compute ROC against 5 ticks ago
                                    mag_window = self._rolling_data[KEY_MAGNET_DELTA_5M]
                                    if mag_window.count >= 5:
                                        delta_5_ago = mag_window.values[-5]
                                        if abs(delta_5_ago) > 0:
                                            delta_roc = (current_delta - delta_5_ago) / abs(delta_5_ago)
                                            self._rolling_data[KEY_MAGNET_DELTA_5M].push(delta_roc, time.time())
                                    else:
                                        self._rolling_data[KEY_MAGNET_DELTA_5M].push(current_delta, time.time())
                except Exception:
                    pass

                # ── theta_burn v2: Wall delta tracking ──
                try:
                    if KEY_WALL_DELTA_5M in self._rolling_data:
                        walls = self._calculator.get_gamma_walls(threshold=5000)
                        if walls:
                            wall_deltas = []
                            for wall in walls:
                                try:
                                    ws = wall.get("strike", 0)
                                    if ws and ws > 0:
                                        dd = self._calculator.get_delta_by_strike(ws)
                                        nd = dd.get("net_delta", 0.0)
                                        wall_deltas.append(nd)
                                except Exception:
                                    pass
                            if wall_deltas:
                                avg_wall_delta = sum(wall_deltas) / len(wall_deltas)
                                self._rolling_data[KEY_WALL_DELTA_5M].push(avg_wall_delta)
                except Exception:
                    pass

                # ── iv_band_breakout v2: Skew width (|OTM Put IV - OTM Call IV|) ──
                try:
                    if atm_strike is not None and KEY_SKEW_WIDTH_5M in self._rolling_data:
                        # OTM Put strike: ATM - 5%
                        otm_put_strike = atm_strike * 0.95
                        # OTM Call strike: ATM + 5%
                        otm_call_strike = atm_strike * 1.05

                        otm_put_iv = self._calculator.get_iv_by_strike(otm_put_strike)
                        otm_call_iv = self._calculator.get_iv_by_strike(otm_call_strike)

                        if otm_put_iv is not None and otm_put_iv > 0 and otm_call_iv is not None and otm_call_iv > 0:
                            skew_width = abs(otm_put_iv - otm_call_iv)
                            self._rolling_data[KEY_SKEW_WIDTH_5M].push(skew_width)
                except Exception:
                    pass

                # ── delta_iv_divergence v2: OTM Delta/IV and Delta-IV correlation ──
                try:
                    price = self._calculator.underlying_price
                    if price and price > 0 and gex_summary:
                        # OTM Put strike: ATM - 5%
                        otm_put_strike = atm_strike * 0.95 if atm_strike else None
                        # OTM Call strike: ATM + 5%
                        otm_call_strike = atm_strike * 1.05 if atm_strike else None

                        # OTM Delta: use the closer of OTM put/call
                        otm_delta = 0.0
                        if otm_put_strike and otm_call_strike:
                            put_data = self._calculator.get_delta_by_strike(otm_put_strike)
                            call_data = self._calculator.get_delta_by_strike(otm_call_strike)
                            put_delta = put_data.get("net_delta", 0.0)
                            call_delta = call_data.get("net_delta", 0.0)
                            # Use the one with larger absolute delta
                            if abs(put_delta) >= abs(call_delta):
                                otm_delta = put_delta
                            else:
                                otm_delta = call_delta
                        elif otm_put_strike:
                            put_data = self._calculator.get_delta_by_strike(otm_put_strike)
                            otm_delta = put_data.get("net_delta", 0.0)
                        elif otm_call_strike:
                            call_data = self._calculator.get_delta_by_strike(otm_call_strike)
                            otm_delta = call_data.get("net_delta", 0.0)

                        if KEY_OTM_DELTA_5M in self._rolling_data:
                            self._rolling_data[KEY_OTM_DELTA_5M].push(otm_delta)

                        # OTM IV: use the closer of OTM put/call IV
                        otm_iv = 0.0
                        if otm_put_strike and otm_call_strike:
                            put_iv = self._calculator.get_iv_by_strike(otm_put_strike)
                            call_iv = self._calculator.get_iv_by_strike(otm_call_strike)
                            if put_iv is not None and call_iv is not None:
                                otm_iv = max(put_iv, call_iv) if put_iv > 0 and call_iv > 0 else (put_iv or call_iv or 0.0)
                            elif put_iv is not None:
                                otm_iv = put_iv
                            elif call_iv is not None:
                                otm_iv = call_iv
                        elif otm_put_strike:
                            otm_iv = self._calculator.get_iv_by_strike(otm_put_strike) or 0.0
                        elif otm_call_strike:
                            otm_iv = self._calculator.get_iv_by_strike(otm_call_strike) or 0.0

                        if otm_iv > 0 and KEY_OTM_IV_5M in self._rolling_data:
                            self._rolling_data[KEY_OTM_IV_5M].push(otm_iv)

                        # Delta-IV correlation: rolling correlation between
                        # KEY_ATM_DELTA_5M and KEY_ATM_IV_5M over last 10 points
                        if (KEY_ATM_DELTA_5M in self._rolling_data
                                and KEY_ATM_IV_5M in self._rolling_data):
                            delta_vals = self._rolling_data[KEY_ATM_DELTA_5M].values
                            iv_vals = self._rolling_data[KEY_ATM_IV_5M].values
                            n = min(len(delta_vals), len(iv_vals))
                            if n >= 10:
                                # Use last 10 points
                                d = delta_vals[-10:]
                                v = iv_vals[-10:]
                                # Pearson correlation
                                mean_d = sum(d) / 10.0
                                mean_v = sum(v) / 10.0
                                num = sum((di - mean_d) * (vi - mean_v) for di, vi in zip(d, v))
                                den_d = (sum((di - mean_d) ** 2 for di in d)) ** 0.5
                                den_v = (sum((vi - mean_v) ** 2 for vi in v)) ** 0.5
                                if den_d > 0 and den_v > 0:
                                    corr = num / (den_d * den_v)
                                else:
                                    corr = 0.0
                                if KEY_DELTA_IV_CORR_5M in self._rolling_data:
                                    self._rolling_data[KEY_DELTA_IV_CORR_5M].push(corr)
                except Exception:
                    pass

                # Push flow_ratio to rolling window for call_put_flow_asymmetry v2
                try:
                    call_score = 0.0
                    put_score = 0.0
                    for strike_str, strike_data in gex_summary.items():
                        call_oi = strike_data.get("call_oi", 0)
                        call_gamma = strike_data.get("call_gamma", 0)
                        call_delta = abs(strike_data.get("call_delta_sum", 0))
                        if call_oi > 0 and call_gamma > 0 and call_delta > 0.01:
                            call_score += call_oi * call_gamma * call_delta

                        put_oi = strike_data.get("put_oi", 0)
                        put_gamma = strike_data.get("put_gamma", 0)
                        put_delta = abs(strike_data.get("put_delta_sum", 0))
                        if put_oi > 0 and put_gamma > 0 and put_delta > 0.01:
                            put_score += put_oi * put_gamma * put_delta

                    if put_score > 0:
                        flow_ratio = call_score / put_score
                    elif call_score > 0:
                        flow_ratio = float("inf")
                    else:
                        flow_ratio = 0.0

                    if KEY_FLOW_RATIO_5M in self._rolling_data:
                        self._rolling_data[KEY_FLOW_RATIO_5M].push(flow_ratio)
                except Exception:
                    pass

                # ── iv_gex_divergence v2: IV skew gradient ──
                try:
                    atm_strike = self._calculator.get_atm_strike(
                        self._calculator.underlying_price,
                    )
                    if atm_strike is not None:
                        atm_iv = self._calculator.get_iv_by_strike(atm_strike)
                        if atm_iv is not None and atm_iv > 0:
                            # Compute IV skew: OTM Put IV - ATM IV
                            otm_put_strike = atm_strike * 0.95  # 5% OTM
                            otm_put_iv = self._calculator.get_iv_by_strike(otm_put_strike)
                            if otm_put_iv is not None and otm_put_iv > 0:
                                iv_skew = otm_put_iv - atm_iv
                                if KEY_IV_SKEW_GRADIENT_5M in self._rolling_data:
                                    self._rolling_data[KEY_IV_SKEW_GRADIENT_5M].push(
                                        iv_skew,
                                    )
                except Exception:
                    pass

                # ── iv_gex_divergence v2: Gamma density ──
                try:
                    price = self._calculator.underlying_price
                    if price and price > 0 and gex_summary:
                        params = data.get("params", {})
                        iv_gex_params = params.get("iv_gex_divergence", {})
                        window_pct = iv_gex_params.get("gamma_density_window_pct", 0.01)
                        gamma_density = 0.0
                        for strike_str, strike_data in gex_summary.items():
                            try:
                                strike = float(strike_str)
                            except (ValueError, TypeError):
                                continue
                            distance = abs(strike - price) / price
                            if distance <= window_pct:
                                call_gamma = strike_data.get("call_gamma", 0.0)
                                put_gamma = strike_data.get("put_gamma", 0.0)
                                gamma_density += abs(call_gamma) + abs(put_gamma)
                        if KEY_GAMMA_DENSITY_5M in self._rolling_data:
                            self._rolling_data[KEY_GAMMA_DENSITY_5M].push(
                                gamma_density,
                            )
                except Exception:
                    pass

                # ── Strike Concentration v2: net delta at top-OI strikes ──
                try:
                    if KEY_STRIKE_DELTA_5M in self._rolling_data and gex_summary:
                        # Identify top-OI strikes (same logic as StrikeConcentration)
                        strike_oi_list = []
                        for strike_str, strike_data in gex_summary.items():
                            try:
                                strike = float(strike_str)
                            except (ValueError, TypeError):
                                continue
                            call_oi = strike_data.get("call_oi", 0) or 0
                            put_oi = strike_data.get("put_oi", 0) or 0
                            total_oi = call_oi + put_oi
                            if total_oi > 0:
                                strike_oi_list.append((strike, total_oi))
                        strike_oi_list.sort(key=lambda x: x[1], reverse=True)
                        top_strikes = strike_oi_list[:3]

                        # Compute net delta at top-OI strikes
                        total_net_delta = 0.0
                        for strike, _ in top_strikes:
                            delta_data = self._calculator.get_delta_by_strike(strike)
                            total_net_delta += delta_data.get("net_delta", 0.0)
                        self._rolling_data[KEY_STRIKE_DELTA_5M].push(total_net_delta)
                except Exception:
                    pass

            # ── Depth data capture (L2/TotalView) ──
            msg_type = data.get("type", "")
            if msg_type in ("market_depth_quotes", KEY_MARKET_DEPTH_AGG):
                bids = data.get("Bids", [])
                asks = data.get("Asks", [])

                old_bid = 0.0
                old_ask = 0.0

                # Aggregate size from all bid/ask levels
                if msg_type == "market_depth_quotes":
                    # Per-exchange: Size field is string → int
                    total_bid_size = sum(int(b.get("Size", 0)) for b in bids)
                    total_ask_size = sum(int(a.get("Size", 0)) for a in asks)
                else:
                    # Aggregated: TotalSize field
                    total_bid_size = sum(int(b.get("TotalSize", 0)) for b in bids)
                    total_ask_size = sum(int(a.get("TotalSize", 0)) for a in asks)

                # ── Exchange Flow Concentration: parse per-exchange sizes (quotes only) ──
                if msg_type == "market_depth_quotes":
                    exchange_bid_sizes: Dict[str, int] = {}
                    exchange_ask_sizes: Dict[str, int] = {}
                    for b in bids:
                        for venue, size_str in b.get("bid_exchanges", {}).items():
                            exchange_bid_sizes[venue] = exchange_bid_sizes.get(venue, 0) + int(size_str)
                    for a in asks:
                        for venue, size_str in a.get("ask_exchanges", {}).items():
                            exchange_ask_sizes[venue] = exchange_ask_sizes.get(venue, 0) + int(size_str)
                    # Store for strategy access (Gate A: cross-venue confluence)
                    self._exchange_bid_sizes = exchange_bid_sizes
                    self._exchange_ask_sizes = exchange_ask_sizes

                    memx_bid = exchange_bid_sizes.get("MEMX", 0)
                    memx_ask = exchange_ask_sizes.get("MEMX", 0)
                    bats_bid = exchange_bid_sizes.get("BATS", 0)
                    bats_ask = exchange_ask_sizes.get("BATS", 0)
                    iex_bid = exchange_bid_sizes.get("IEX", 0)
                    iex_ask = exchange_ask_sizes.get("IEX", 0)

                    memx_vsi = memx_bid / memx_ask if memx_ask > 0 else 999.0
                    bats_vsi = bats_bid / bats_ask if bats_ask > 0 else 999.0
                    vsi_combined = max(memx_vsi, bats_vsi)

                    total_depth = total_bid_size + total_ask_size
                    iex_total = iex_bid + iex_ask
                    iex_intent = iex_total / total_depth if total_depth > 0 else 0.0

                    # VSI ROC over 5-tick lookback
                    vsi_window = self._rolling_data.get(KEY_VSI_COMBINED_5M)
                    vsi_roc = 0.0
                    if vsi_window and vsi_window.count >= 5:
                        past_vsi = vsi_window.values[-5]
                        if past_vsi > 0:
                            vsi_roc = (vsi_combined - past_vsi) / past_vsi

                    if KEY_VSI_COMBINED_5M in self._rolling_data:
                        self._rolling_data[KEY_VSI_COMBINED_5M].push(vsi_combined, ts)
                    if KEY_VSI_ROC_5M in self._rolling_data:
                        self._rolling_data[KEY_VSI_ROC_5M].push(vsi_roc, ts)
                    if KEY_IEX_INTENT_5M in self._rolling_data:
                        self._rolling_data[KEY_IEX_INTENT_5M].push(iex_intent, ts)

                    # ── Exchange Flow Imbalance: Venue-Specific Imbalance ──
                    # Aggressor venues combined (MEMX + BATS)
                    aggressor_bid = memx_bid + bats_bid
                    aggressor_ask = memx_ask + bats_ask
                    aggressor_total = aggressor_bid + aggressor_ask
                    aggressor_vsi = (
                        (aggressor_bid - aggressor_ask) / aggressor_total
                        if aggressor_total > 0
                        else 0.0
                    )

                    # Individual venue VSI
                    memx_total = memx_bid + memx_ask
                    memx_vsi_val = (
                        (memx_bid - memx_ask) / memx_total if memx_total > 0 else 0.0
                    )
                    bats_total = bats_bid + bats_ask
                    bats_vsi_val = (
                        (bats_bid - bats_ask) / bats_total if bats_total > 0 else 0.0
                    )

                    # IEX intent score: fraction of total depth on IEX
                    iex_intent_score = (
                        iex_total / total_depth if total_depth > 0 else 0.0
                    )

                    # Venue concentration: what fraction of total book imbalance
                    # comes from aggressor venues
                    total_imbalance = total_bid_size - total_ask_size
                    aggressor_imbalance = aggressor_bid - aggressor_ask
                    venue_concentration = (
                        abs(aggressor_imbalance) / abs(total_imbalance)
                        if total_imbalance != 0
                        else 0.0
                    )

                    # VSI ROC (aggression velocity): rate of change over lookback
                    vsi_roc = 0.0
                    aggressor_rw = self._rolling_data.get(KEY_AGGRESSOR_VSI_5M)
                    if aggressor_rw and aggressor_rw.count >= 10:
                        past_vsi = aggressor_rw.values[-10]
                        if past_vsi != 0:
                            vsi_roc = (
                                (aggressor_vsi - past_vsi) / abs(past_vsi)
                            )
                        else:
                            vsi_roc = (
                                (aggressor_vsi - past_vsi) / 0.001
                            )

                    # Push to rolling windows
                    if KEY_AGGRESSOR_VSI_5M in self._rolling_data:
                        self._rolling_data[KEY_AGGRESSOR_VSI_5M].push(aggressor_vsi, ts)
                    if KEY_AGGRESSOR_VSI_ROC_5M in self._rolling_data:
                        self._rolling_data[KEY_AGGRESSOR_VSI_ROC_5M].push(vsi_roc, ts)
                    if KEY_IEX_INTENT_SCORE_5M in self._rolling_data:
                        self._rolling_data[KEY_IEX_INTENT_SCORE_5M].push(iex_intent_score, ts)
                    if KEY_MEMX_VSI_5M in self._rolling_data:
                        self._rolling_data[KEY_MEMX_VSI_5M].push(memx_vsi_val, ts)
                    if KEY_BATS_VSI_5M in self._rolling_data:
                        self._rolling_data[KEY_BATS_VSI_5M].push(bats_vsi_val, ts)
                    if KEY_VENUE_CONCENTRATION_5M in self._rolling_data:
                        self._rolling_data[KEY_VENUE_CONCENTRATION_5M].push(venue_concentration, ts)

                    # ── Exchange Flow Asymmetry: Venue Signature Tracking ──
                    # MEMX ESI
                    memx_total_size = memx_bid + memx_ask
                    esi_memx = (
                        (memx_bid - memx_ask) / memx_total_size
                        if memx_total_size > 0
                        else 0.0
                    )
                    # BATS ESI
                    bats_total_size = bats_bid + bats_ask
                    esi_bats = (
                        (bats_bid - bats_ask) / bats_total_size
                        if bats_total_size > 0
                        else 0.0
                    )
                    # Venue volume (total size across both sides)
                    memx_vol = memx_total_size
                    bats_vol = bats_total_size
                    # Venue volume ratio (current vs 5m average)
                    memx_vol_ratio = 0.0
                    memx_vol_rw = self._rolling_data.get(KEY_MEMX_VOL_RATIO_5M)
                    if memx_vol_rw and memx_vol_rw.count >= 10:
                        avg_vol = (
                            sum(memx_vol_rw.values) / len(memx_vol_rw.values)
                            if memx_vol_rw.values
                            else 1.0
                        )
                        memx_vol_ratio = memx_vol / avg_vol if avg_vol > 0 else 1.0
                    bats_vol_ratio = 0.0
                    bats_vol_rw = self._rolling_data.get(KEY_BATS_VOL_RATIO_5M)
                    if bats_vol_rw and bats_vol_rw.count >= 10:
                        avg_vol = (
                            sum(bats_vol_rw.values) / len(bats_vol_rw.values)
                            if bats_vol_rw.values
                            else 1.0
                        )
                        bats_vol_ratio = bats_vol / avg_vol if avg_vol > 0 else 1.0
                    # ESI ROC (rate of change over lookback)
                    esi_memx_roc = 0.0
                    esi_memx_rw = self._rolling_data.get(KEY_ESI_MEMX_5M)
                    if esi_memx_rw and esi_memx_rw.count >= 10:
                        past_esi = (
                            esi_memx_rw.values[-10]
                            if esi_memx_rw.values[-10] != 0
                            else 0.001
                        )
                        esi_memx_roc = (esi_memx - past_esi) / abs(past_esi)
                    esi_bats_roc = 0.0
                    esi_bats_rw = self._rolling_data.get(KEY_ESI_BATS_5M)
                    if esi_bats_rw and esi_bats_rw.count >= 10:
                        past_esi = (
                            esi_bats_rw.values[-10]
                            if esi_bats_rw.values[-10] != 0
                            else -0.001
                        )
                        esi_bats_roc = (esi_bats - past_esi) / abs(past_esi)
                    # Baseline deviation (ESI vs 1h rolling mean)
                    esi_baseline_memx = 0.0
                    esi_baseline_bats = 0.0
                    baseline_rw_memx = self._rolling_data.get(
                        KEY_ESI_BASELINE_MEMX_1H
                    )
                    baseline_rw_bats = self._rolling_data.get(
                        KEY_ESI_BASELINE_BATS_1H
                    )
                    if baseline_rw_memx and baseline_rw_memx.count >= 60:
                        esi_baseline_memx = (
                            sum(baseline_rw_memx.values[-60:])
                            / min(60, baseline_rw_memx.count)
                        )
                    if baseline_rw_bats and baseline_rw_bats.count >= 60:
                        esi_baseline_bats = (
                            sum(baseline_rw_bats.values[-60:])
                            / min(60, baseline_rw_bats.count)
                        )
                    memx_deviation = esi_memx - esi_baseline_memx
                    bats_deviation = esi_bats - esi_baseline_bats
                    # OBI for Gate B (book alignment)
                    total_depth = total_bid_size + total_ask_size
                    obi = (
                        (total_bid_size - total_ask_size) / total_depth
                        if total_depth > 0
                        else 0.0
                    )
                    # Push to rolling windows
                    if KEY_ESI_MEMX_5M in self._rolling_data:
                        self._rolling_data[KEY_ESI_MEMX_5M].push(esi_memx, ts)
                    if KEY_ESI_MEMX_ROC_5M in self._rolling_data:
                        self._rolling_data[KEY_ESI_MEMX_ROC_5M].push(esi_memx_roc, ts)
                    if KEY_ESI_BATS_5M in self._rolling_data:
                        self._rolling_data[KEY_ESI_BATS_5M].push(esi_bats, ts)
                    if KEY_ESI_BATS_ROC_5M in self._rolling_data:
                        self._rolling_data[KEY_ESI_BATS_ROC_5M].push(esi_bats_roc, ts)
                    if KEY_MEMX_VOL_RATIO_5M in self._rolling_data:
                        self._rolling_data[KEY_MEMX_VOL_RATIO_5M].push(
                            memx_vol_ratio, ts
                        )
                    if KEY_BATS_VOL_RATIO_5M in self._rolling_data:
                        self._rolling_data[KEY_BATS_VOL_RATIO_5M].push(
                            bats_vol_ratio, ts
                        )
                    if KEY_ESI_BASELINE_MEMX_1H in self._rolling_data:
                        self._rolling_data[KEY_ESI_BASELINE_MEMX_1H].push(
                            esi_baseline_memx, ts
                        )
                    if KEY_ESI_BASELINE_BATS_1H in self._rolling_data:
                        self._rolling_data[KEY_ESI_BASELINE_BATS_1H].push(
                            esi_baseline_bats, ts
                        )

                    # ── Participant Diversity Conviction: parse participants + exchanges ──
                    top_bid_participants = (
                        max(int(b.get("num_participants", 0)) for b in bids) if bids else 0
                    )
                    top_ask_participants = (
                        max(int(a.get("num_participants", 0)) for a in asks) if asks else 0
                    )

                    # Unique exchanges across all levels
                    top_bid_exchanges = len({k for b in bids if b.get("bid_exchanges") for k in b["bid_exchanges"].keys()}) if bids else 0
                    top_ask_exchanges = len({k for a in asks if a.get("ask_exchanges") for k in a["ask_exchanges"].keys()}) if asks else 0

                    # Avg participants across top N levels
                    top_n = min(5, len(bids)) if bids else 0
                    avg_bid_participants = (
                        sum(int(b.get("num_participants", 0)) for b in bids[:top_n]) / top_n
                        if top_n > 0 else 0
                    )
                    top_n_ask = min(5, len(asks)) if asks else 0
                    avg_ask_participants = (
                        sum(int(a.get("num_participants", 0)) for a in asks[:top_n_ask]) / top_n_ask
                        if top_n_ask > 0 else 0
                    )

                    # Push to rolling windows
                    if KEY_BID_PARTICIPANTS_5M in self._rolling_data:
                        self._rolling_data[KEY_BID_PARTICIPANTS_5M].push(avg_bid_participants, ts)
                    if KEY_ASK_PARTICIPANTS_5M in self._rolling_data:
                        self._rolling_data[KEY_ASK_PARTICIPANTS_5M].push(avg_ask_participants, ts)
                    if KEY_BID_EXCHANGES_5M in self._rolling_data:
                        self._rolling_data[KEY_BID_EXCHANGES_5M].push(top_bid_exchanges, ts)
                    if KEY_ASK_EXCHANGES_5M in self._rolling_data:
                        self._rolling_data[KEY_ASK_EXCHANGES_5M].push(top_ask_exchanges, ts)

                    # Compute conviction score (participant_score × exchange_score)
                    max_participants_norm = 5.0
                    max_exchanges_norm = 4.0
                    bid_participant_score = min(1.0, avg_bid_participants / max_participants_norm)
                    bid_exchange_score = min(1.0, top_bid_exchanges / max_exchanges_norm)
                    bid_conviction_score = bid_participant_score * bid_exchange_score
                    ask_participant_score = min(1.0, avg_ask_participants / max_participants_norm)
                    ask_exchange_score = min(1.0, top_ask_exchanges / max_exchanges_norm)
                    ask_conviction_score = ask_participant_score * ask_exchange_score
                    avg_conviction_score = (bid_conviction_score + ask_conviction_score) / 2.0

                    if KEY_CONVICT_SCORE_5M in self._rolling_data:
                        self._rolling_data[KEY_CONVICT_SCORE_5M].push(avg_conviction_score, ts)

                    # ── Participant Divergence Scalper: fragility + decay velocity ──
                    def _compute_fragility(levels, side_key):
                        """Fragility = 1 / (num_participants × exchange_count), averaged over top N."""
                        if not levels:
                            return 0.0
                        fragilities = []
                        for lvl in levels[:5]:
                            n_part = max(1, int(lvl.get("num_participants", 0)))
                            exchanges = lvl.get(side_key, {})
                            n_exch = max(1, len(exchanges)) if exchanges else 1
                            fragilities.append(1.0 / (n_part * n_exch))
                        return sum(fragilities) / len(fragilities)

                    frag_bid = _compute_fragility(bids, "bid_exchanges")
                    frag_ask = _compute_fragility(asks, "ask_exchanges")

                    # Track strongest wall per side (level with max size)
                    top_bid_level = max(bids, key=lambda b: int(b.get("Size", 0)), default=None)
                    top_ask_level = max(asks, key=lambda a: int(a.get("Size", 0)), default=None)
                    top_bid_wall_size = int(top_bid_level.get("Size", 0)) if top_bid_level else 0
                    top_ask_wall_size = int(top_ask_level.get("Size", 0)) if top_ask_level else 0

                    bid_decay = 0.0
                    ask_decay = 0.0
                    bid_wall_rw = self._rolling_data.get(KEY_TOP_WALL_BID_SIZE_5M)
                    ask_wall_rw = self._rolling_data.get(KEY_TOP_WALL_ASK_SIZE_5M)
                    if bid_wall_rw and bid_wall_rw.count >= 5 and top_bid_wall_size > 0:
                        past = bid_wall_rw.values[-5] if bid_wall_rw.values[-5] > 0 else 1
                        bid_decay = (top_bid_wall_size - past) / past
                    if ask_wall_rw and ask_wall_rw.count >= 5 and top_ask_wall_size > 0:
                        past = ask_wall_rw.values[-5] if ask_wall_rw.values[-5] > 0 else 1
                        ask_decay = (top_ask_wall_size - past) / past

                    # Push to rolling windows
                    if KEY_FRAGILITY_BID_5M in self._rolling_data:
                        self._rolling_data[KEY_FRAGILITY_BID_5M].push(frag_bid, ts)
                    if KEY_FRAGILITY_ASK_5M in self._rolling_data:
                        self._rolling_data[KEY_FRAGILITY_ASK_5M].push(frag_ask, ts)
                    if KEY_DECAY_VELOCITY_BID_5M in self._rolling_data:
                        self._rolling_data[KEY_DECAY_VELOCITY_BID_5M].push(bid_decay, ts)
                    if KEY_DECAY_VELOCITY_ASK_5M in self._rolling_data:
                        self._rolling_data[KEY_DECAY_VELOCITY_ASK_5M].push(ask_decay, ts)
                    if KEY_TOP_WALL_BID_SIZE_5M in self._rolling_data:
                        self._rolling_data[KEY_TOP_WALL_BID_SIZE_5M].push(top_bid_wall_size, ts)
                    if KEY_TOP_WALL_ASK_SIZE_5M in self._rolling_data:
                        self._rolling_data[KEY_TOP_WALL_ASK_SIZE_5M].push(top_ask_wall_size, ts)

                    # Best bid/ask for spread
                best_bid = float(bids[0].get("Price", 0)) if bids else 0.0
                best_ask = float(asks[0].get("Price", 0)) if asks else 0.0
                spread = best_ask - best_bid if best_bid > 0 and best_ask > 0 else 0.0

                if KEY_DEPTH_BID_SIZE_5M in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_BID_SIZE_5M].push(total_bid_size, ts)
                if KEY_DEPTH_ASK_SIZE_5M in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_ASK_SIZE_5M].push(total_ask_size, ts)
                if KEY_DEPTH_SPREAD_5M in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_SPREAD_5M].push(spread, ts)
                if KEY_DEPTH_BID_LEVELS_5M in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_BID_LEVELS_5M].push(len(bids), ts)
                if KEY_DEPTH_ASK_LEVELS_5M in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_ASK_LEVELS_5M].push(len(asks), ts)

                # ── Vortex Compression: spread z-score, liquidity density, participant equilibrium, volume spike ──
                if KEY_SPREAD_ZSCORE_5M in self._rolling_data:
                    spread_window = self._rolling_data[KEY_DEPTH_SPREAD_5M]
                    if spread_window.count >= 10:
                        mean_spread = spread_window.mean
                        std_spread = spread_window.std
                        current_spread = spread_window.latest
                        if std_spread is not None and std_spread > 0 and mean_spread is not None and current_spread is not None:
                            spread_z = (current_spread - mean_spread) / std_spread
                        else:
                            spread_z = 0.0
                        self._rolling_data[KEY_SPREAD_ZSCORE_5M].push(spread_z, ts)

                # liquidity_density = (total_bid_size + total_ask_size) / spread
                if spread > 0:
                    liquidity_density = (total_bid_size + total_ask_size) / spread
                    if KEY_LIQUIDITY_DENSITY_5M in self._rolling_data:
                        self._rolling_data[KEY_LIQUIDITY_DENSITY_5M].push(liquidity_density, ts)

                # participant_equilibrium = bid_avg_participants / ask_avg_participants
                bid_avg_p = data.get("bid_avg_participants", 0)
                ask_avg_p = data.get("ask_avg_participants", 0)
                if ask_avg_p > 0:
                    participant_equil = bid_avg_p / ask_avg_p
                else:
                    participant_equil = 1.0
                if KEY_PARTICIPANT_EQUILIBRIUM_5M in self._rolling_data:
                    self._rolling_data[KEY_PARTICIPANT_EQUILIBRIUM_5M].push(participant_equil, ts)

                # volume_spike = current_volume / 5m_avg_volume
                volume_window = self._rolling_data.get(KEY_VOLUME_5M)
                if volume_window and volume_window.count > 0 and volume_window.mean and volume_window.mean > 0:
                    current_vol = volume_window.latest if volume_window.latest else 0
                    volume_spike = current_vol / volume_window.mean if current_vol > 0 else 0.0
                else:
                    volume_spike = 1.0
                if KEY_VOLUME_SPIKE_5M in self._rolling_data:
                    self._rolling_data[KEY_VOLUME_SPIKE_5M].push(volume_spike, ts)

                # Squeeze-specific: track depth on the breakout side for liquidity vacuum detection
                if KEY_DEPTH_BID_SIZE_ROLLING in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_BID_SIZE_ROLLING].push(total_bid_size, ts)
                if KEY_DEPTH_ASK_SIZE_ROLLING in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_ASK_SIZE_ROLLING].push(total_ask_size, ts)

                # Store raw depth levels for StrikeConcentration v2 liquidity vacuum
                if msg_type == KEY_MARKET_DEPTH_AGG:
                    bid_levels = [{"price": float(b.get("Price", 0)), "size": int(b.get("TotalSize", 0))} for b in bids]
                    ask_levels = [{"price": float(a.get("Price", 0)), "size": int(a.get("TotalSize", 0))} for a in asks]
                    self._rolling_data[KEY_MARKET_DEPTH_AGG] = {
                        "bid_levels": bid_levels,
                        "ask_levels": ask_levels,
                    }

                    # ── VAMP Momentum: store top N levels + compute VAMP ──
                    N_TOP_LEVELS = 10
                    bid_levels_full = [
                        {"price": float(b.get("Price", 0)), "size": int(b.get("TotalSize", 0)),
                         "participants": int(b.get("NumParticipants", 1))}
                        for b in bids[:N_TOP_LEVELS]
                    ]
                    ask_levels_full = [
                        {"price": float(a.get("Price", 0)), "size": int(a.get("TotalSize", 0)),
                         "participants": int(a.get("NumParticipants", 1))}
                        for a in asks[:N_TOP_LEVELS]
                    ]
                    self._rolling_data[KEY_VAMP_LEVELS] = {
                        "bid_levels": bid_levels_full,
                        "ask_levels": ask_levels_full,
                        "mid_price": data.get("mid_price", 0),
                        "spread": spread,
                        "bid_avg_participants": data.get("bid_avg_participants", 0),
                        "ask_avg_participants": data.get("ask_avg_participants", 0),
                    }

                    # VAMP computation: volume-weighted center of gravity
                    bid_weighted = sum(l["price"] * l["size"] for l in bid_levels_full)
                    bid_total = sum(l["size"] for l in bid_levels_full)
                    ask_weighted = sum(l["price"] * l["size"] for l in ask_levels_full)
                    ask_total = sum(l["size"] for l in ask_levels_full)
                    total_weighted = bid_weighted + ask_weighted
                    total_size = bid_total + ask_total
                    mid_price = data.get("mid_price", 0)

                    if total_size > 0 and mid_price > 0:
                        vamp = total_weighted / total_size
                        vamp_mid_dev = (vamp - mid_price) / mid_price
                    else:
                        vamp = mid_price
                        vamp_mid_dev = 0

                    # Push to rolling windows
                    vamp_roc = 0
                    if KEY_VAMP_5M in self._rolling_data:
                        self._rolling_data[KEY_VAMP_5M].push(vamp, ts)
                        vamp_history = self._rolling_data[KEY_VAMP_5M]
                        if vamp_history.count >= 5:
                            past_vamp = vamp_history.values[-5]
                            vamp_roc = (vamp - past_vamp) / past_vamp if past_vamp != 0 else 0
                        else:
                            vamp_roc = 0
                    if KEY_VAMP_MID_DEV_5M in self._rolling_data:
                        self._rolling_data[KEY_VAMP_MID_DEV_5M].push(vamp_mid_dev, ts)
                    if KEY_VAMP_ROC_5M in self._rolling_data:
                        self._rolling_data[KEY_VAMP_ROC_5M].push(vamp_roc, ts)

                    # ── Depth Decay Momentum: compute depth ROC and top-level decay ──
                    # Overall depth ROC (30s lookback using 5-tick window)
                    bid_size_window = self._rolling_data.get(KEY_DEPTH_BID_SIZE_5M)
                    ask_size_window = self._rolling_data.get(KEY_DEPTH_ASK_SIZE_5M)

                    bid_depth_roc = 0.0
                    ask_depth_roc = 0.0

                    if bid_size_window and bid_size_window.count >= 5:
                        old_bid = bid_size_window.values[-5]
                        current_bid = bid_size_window.values[-1]
                        if old_bid > 0:
                            bid_depth_roc = (current_bid - old_bid) / old_bid

                    if ask_size_window and ask_size_window.count >= 5:
                        old_ask = ask_size_window.values[-5]
                        current_ask = ask_size_window.values[-1]
                        if old_ask > 0:
                            ask_depth_roc = (current_ask - old_ask) / old_ask

                    if KEY_DEPTH_DECAY_BID_5M in self._rolling_data:
                        self._rolling_data[KEY_DEPTH_DECAY_BID_5M].push(bid_depth_roc, ts)
                    if KEY_DEPTH_DECAY_ASK_5M in self._rolling_data:
                        self._rolling_data[KEY_DEPTH_DECAY_ASK_5M].push(ask_depth_roc, ts)

                    # Top-5 level depth (for magnitude gate)
                    bid_levels = self._rolling_data.get(KEY_MARKET_DEPTH_AGG, {}).get("bid_levels", [])
                    ask_levels = self._rolling_data.get(KEY_MARKET_DEPTH_AGG, {}).get("ask_levels", [])

                    top5_bid_depth = sum(l["size"] for l in bid_levels[:5])
                    top5_ask_depth = sum(l["size"] for l in ask_levels[:5])

                    if KEY_DEPTH_TOP5_BID_5M in self._rolling_data:
                        self._rolling_data[KEY_DEPTH_TOP5_BID_5M].push(top5_bid_depth, ts)
                    if KEY_DEPTH_TOP5_ASK_5M in self._rolling_data:
                        self._rolling_data[KEY_DEPTH_TOP5_ASK_5M].push(top5_ask_depth, ts)

                    # Volume/depth ratio: track volume changes alongside depth changes
                    volume_window = self._rolling_data.get(KEY_VOLUME_5M)
                    if volume_window and volume_window.count >= 5:
                        old_vol = volume_window.values[-5]
                        current_vol = volume_window.values[-1]
                        vol_change = abs(current_vol - old_vol)
                        depth_change = abs((current_bid + current_ask) - (old_bid + old_ask)) if (old_bid and old_ask) else 0
                        if depth_change > 0:
                            vol_ratio = vol_change / depth_change
                        else:
                            vol_ratio = 0.0
                        if KEY_DEPTH_VOL_RATIO_5M in self._rolling_data:
                            self._rolling_data[KEY_DEPTH_VOL_RATIO_5M].push(vol_ratio, ts)
                    if KEY_VAMP_PARTICIPANTS_5M in self._rolling_data:
                        avg_participants = (
                            data.get("bid_avg_participants", 0) + data.get("ask_avg_participants", 0)
                        ) / 2
                        self._rolling_data[KEY_VAMP_PARTICIPANTS_5M].push(avg_participants, ts)
                    if KEY_VAMP_DEPTH_DENSITY_5M in self._rolling_data:
                        self._rolling_data[KEY_VAMP_DEPTH_DENSITY_5M].push(total_size, ts)

                    # ── Depth Imbalance Momentum: compute IR and ROC ──
                    bid_size_window = self._rolling_data.get(KEY_DEPTH_BID_SIZE_5M)
                    ask_size_window = self._rolling_data.get(KEY_DEPTH_ASK_SIZE_5M)

                    ir = 0.0
                    ir_roc = 0.0

                    if bid_size_window and ask_size_window and bid_size_window.count > 0 and ask_size_window.count > 0:
                        current_bid = bid_size_window.values[-1]
                        current_ask = ask_size_window.values[-1]
                        if current_ask > 0:
                            ir = current_bid / current_ask
                        else:
                            ir = 999.0

                        if bid_size_window.count >= 5 and ask_size_window.count >= 5:
                            old_bid = bid_size_window.values[-5]
                            old_ask = ask_size_window.values[-5]
                            if old_ask > 0:
                                old_ir = old_bid / old_ask
                                if old_ir > 0:
                                    ir_roc = (ir - old_ir) / old_ir

                    if KEY_IR_5M in self._rolling_data:
                        self._rolling_data[KEY_IR_5M].push(ir, ts)
                    if KEY_IR_ROC_5M in self._rolling_data:
                        self._rolling_data[KEY_IR_ROC_5M].push(ir_roc, ts)

                    # OBI computation from depth agg
                    total_depth = total_bid_size + total_ask_size
                    if total_depth > 0:
                        obi = (total_bid_size - total_ask_size) / total_depth
                    else:
                        obi = 0.0
                    if KEY_OBI_5M in self._rolling_data:
                        self._rolling_data[KEY_OBI_5M].push(obi, ts)

                    # ── Order Book Stacking: SIS computation ──
                    N_TOP_LEVELS = 10
                    top_n = min(N_TOP_LEVELS, len(bids)) if bids else 0
                    top_n_ask = min(N_TOP_LEVELS, len(asks)) if asks else 0

                    # Compute rolling avg of top N level sizes
                    bid_sizes = [int(b.get("Size", 0)) for b in bids[:top_n]] if bids else []
                    ask_sizes = [int(a.get("Size", 0)) for a in asks[:top_n_ask]] if asks else []

                    bid_avg = sum(bid_sizes) / len(bid_sizes) if bid_sizes else 0
                    ask_avg = sum(ask_sizes) / len(ask_sizes) if ask_sizes else 0

                    # Push level averages to rolling windows
                    if KEY_DEPTH_BID_LEVEL_AVG_5M in self._rolling_data:
                        self._rolling_data[KEY_DEPTH_BID_LEVEL_AVG_5M].push(bid_avg, ts)
                    if KEY_DEPTH_ASK_LEVEL_AVG_5M in self._rolling_data:
                        self._rolling_data[KEY_DEPTH_ASK_LEVEL_AVG_5M].push(ask_avg, ts)

                    # Compute SIS = max(level_size) / rolling_avg(level_size)
                    if bid_avg > 0 and bid_sizes:
                        max_bid_size = max(bid_sizes)
                        sis_bid = max_bid_size / bid_avg
                    else:
                        sis_bid = 0.0

                    if ask_avg > 0 and ask_sizes:
                        max_ask_size = max(ask_sizes)
                        sis_ask = max_ask_size / ask_avg
                    else:
                        sis_ask = 0.0

                    # Push SIS to rolling windows
                    if KEY_SIS_BID_5M in self._rolling_data:
                        self._rolling_data[KEY_SIS_BID_5M].push(sis_bid, ts)
                    if KEY_SIS_ASK_5M in self._rolling_data:
                        self._rolling_data[KEY_SIS_ASK_5M].push(sis_ask, ts)

                    # Compute ROC of max sizes for decay detection
                    # Track max bid/ask sizes separately for ROC
                    bid_max_rw = self._rolling_data.get(KEY_TOP_WALL_BID_SIZE_5M)
                    ask_max_rw = self._rolling_data.get(KEY_TOP_WALL_ASK_SIZE_5M)

                    bid_max_roc = 0.0
                    ask_max_roc = 0.0
                    if bid_max_rw and bid_max_rw.count >= 5 and bid_sizes:
                        current_max_bid = max(bid_sizes)
                        past_max = bid_max_rw.values[-5]
                        if past_max > 0:
                            bid_max_roc = (current_max_bid - past_max) / past_max
                    if ask_max_rw and ask_max_rw.count >= 5 and ask_sizes:
                        current_max_ask = max(ask_sizes)
                        past_max = ask_max_rw.values[-5]
                        if past_max > 0:
                            ask_max_roc = (current_max_ask - past_max) / past_max

                    # Push ROC of max sizes to rolling windows
                    if KEY_SIS_BID_ROC_5M in self._rolling_data:
                        self._rolling_data[KEY_SIS_BID_ROC_5M].push(bid_max_roc, ts)
                    if KEY_SIS_ASK_ROC_5M in self._rolling_data:
                        self._rolling_data[KEY_SIS_ASK_ROC_5M].push(ask_max_roc, ts)

                    # ── Whale Tracker — Concentration Ratio Engine ──
                    # Ω_conc = biggest_size / smallest_size at best levels
                    try:
                        if msg_type == KEY_MARKET_DEPTH_AGG and bids and asks:
                            top_bids = bids[:5] if len(bids) >= 5 else bids
                            top_asks = asks[:5] if len(asks) >= 5 else asks

                            if top_bids and top_asks:
                                bid_sizes = [
                                    int(b.get("TotalSize", 0))
                                    for b in top_bids
                                    if int(b.get("TotalSize", 0)) > 0
                                ]
                                bid_participants = [
                                    int(b.get("NumParticipants", 0))
                                    for b in top_bids
                                ]

                                ask_sizes = [
                                    int(a.get("TotalSize", 0))
                                    for a in top_asks
                                    if int(a.get("TotalSize", 0)) > 0
                                ]
                                ask_participants = [
                                    int(a.get("NumParticipants", 0))
                                    for a in top_asks
                                ]

                                if bid_sizes and ask_sizes:
                                    bid_biggest = max(bid_sizes)
                                    bid_smallest = min(bid_sizes)
                                    bid_conc_ratio = (
                                        bid_biggest / bid_smallest
                                        if bid_smallest > 0
                                        else 0.0
                                    )

                                    ask_biggest = max(ask_sizes)
                                    ask_smallest = min(ask_sizes)
                                    ask_conc_ratio = (
                                        ask_biggest / ask_smallest
                                        if ask_smallest > 0
                                        else 0.0
                                    )

                                    best_conc_ratio = max(
                                        bid_conc_ratio, ask_conc_ratio
                                    )
                                    best_side = (
                                        "bid"
                                        if bid_conc_ratio > ask_conc_ratio
                                        else "ask"
                                    )
                                    best_participants = (
                                        min(bid_participants)
                                        if best_side == "bid"
                                        else min(ask_participants)
                                    )

                                    big_w = self._rolling_data.get(
                                        KEY_BIGGEST_SIZE_5M
                                    )
                                    if big_w:
                                        big_w.push(
                                            max(bid_biggest, ask_biggest), ts
                                        )

                                    small_w = self._rolling_data.get(
                                        KEY_SMALLEST_SIZE_5M
                                    )
                                    if small_w:
                                        small_w.push(
                                            min(bid_smallest, ask_smallest), ts
                                        )

                                    conc_w = self._rolling_data.get(
                                        KEY_CONCENTRATION_RATIO_5M
                                    )
                                    if conc_w:
                                        conc_w.push(best_conc_ratio, ts)

                                    conc_sig_w = self._rolling_data.get(
                                        KEY_CONCENTRATION_SIGMA_5M
                                    )
                                    if (
                                        conc_w
                                        and conc_sig_w
                                        and conc_w.count >= 5
                                    ):
                                        vals = list(conc_w.values)
                                        mean_c = sum(vals) / len(vals)
                                        var = sum(
                                            (x - mean_c) ** 2
                                            for x in vals
                                        ) / len(vals)
                                        conc_sig_w.push(
                                            math.sqrt(var), ts
                                        )

                                    parts_w = self._rolling_data.get(
                                        KEY_NUM_PARTICIPANTS_5M
                                    )
                                    if parts_w:
                                        parts_w.push(best_participants, ts)
                    except Exception:
                        pass

            # Aggression Flow from quotes stream — detect aggressive trades
            if data.get("type") == "quote_update":
                last = data.get("last", 0)
                bid = data.get("bid", 0)
                ask = data.get("ask", 0)
                last_size = data.get("last_size", 0)
                if isinstance(last_size, str):
                    try:
                        last_size = int(last_size)
                    except (ValueError, TypeError):
                        last_size = 0

                if last_size > 0:
                    if last >= ask and ask > 0:
                        # Aggressive buy — hit the ask
                        if KEY_AGGRESSIVE_BUY_VOL_5M in self._rolling_data:
                            self._rolling_data[KEY_AGGRESSIVE_BUY_VOL_5M].push(last_size, ts)
                    elif last <= bid and bid > 0:
                        # Aggressive sell — hit the bid
                        if KEY_AGGRESSIVE_SELL_VOL_5M in self._rolling_data:
                            self._rolling_data[KEY_AGGRESSIVE_SELL_VOL_5M].push(last_size, ts)

                    # Track individual trade size for volume gate
                    if KEY_TRADE_SIZE_5M in self._rolling_data:
                        self._rolling_data[KEY_TRADE_SIZE_5M].push(last_size, ts)

                # Compute AF from rolling aggressive volumes
                buy_vol_window = self._rolling_data.get(KEY_AGGRESSIVE_BUY_VOL_5M)
                sell_vol_window = self._rolling_data.get(KEY_AGGRESSIVE_SELL_VOL_5M)
                if buy_vol_window and sell_vol_window and buy_vol_window.count > 0 and sell_vol_window.count > 0:
                    total_buy = sum(buy_vol_window.values)
                    total_sell = sum(sell_vol_window.values)
                    total_aggressive = total_buy + total_sell
                    if total_aggressive > 0:
                        af = (total_buy - total_sell) / total_aggressive
                    else:
                        af = 0.0
                else:
                    af = 0.0

                if KEY_AF_5M in self._rolling_data:
                    self._rolling_data[KEY_AF_5M].push(af, ts)


        except Exception as exc:
            logger.error("Error processing message: %s", exc, exc_info=True)

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

        # Build data snapshot for strategies
        # Inject _gamma_sync from rolling window (Sentiment Sync)
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

        # Build depth snapshot for strategies
        depth_snapshot = self._build_depth_snapshot()
        data["depth_snapshot"] = depth_snapshot

        # Inject per-strategy config params into data dict
        # Strategies can read params from data["params"][strategy_id] in evaluate()
        strategy_params: Dict[str, Dict[str, Any]] = {}
        for layer in ["layer1", "layer2", "layer3", "full_data"]:
            layer_config = self._strategy_config.get(layer, {})
            for strat_name, strat_cfg in layer_config.items():
                if strat_cfg.get("enabled", True):
                    params = strat_cfg.get("params", {})
                    strategy_params[strat_name] = params
        data["params"] = strategy_params

        # Run evaluation
        signals = self._strategy_engine.process(data)

        if signals:
            # Track new signals for outcome resolution
            if self._signal_tracker:
                for s in signals:
                    self._signal_tracker.track(s.to_dict())

            for s in signals:
                logger.info("SIGNAL  |  %s  |  %s  |  conf=%.2f  |  %s",
                           s.strategy_id, s.direction.value, s.confidence, s.reason)

    def _report_profile(self) -> None:
        """Log the current Gamma Profile — the evolving state."""
        assert self._calculator is not None

        summary = self._calculator.get_summary()
        profile = self._calculator.get_gamma_profile()

        net = summary["net_gamma"]
        price = summary["underlying_price"]
        strikes = summary["active_strikes"]

        # Format: one line per top-level metric
        logger.info(
            "GAMMA_PROFILE  |  %s  |  Underlying: $%.2f  |  "
            "Net Gamma: %+.2f  |  Strikes: %d  |  Msgs: %d",
            self.symbol,
            price,
            net,
            strikes,
            summary["total_messages"],
        )

        # Gamma Flip point
        flip = self._calculator.get_gamma_flip()
        if flip is not None:
            logger.info("  GAMMA_FLIP:  Strike $%.1f (cumulative gamma turns negative below this)", flip)

        # Gamma Walls
        walls = self._calculator.get_gamma_walls(threshold=500000)
        if walls:
            wall_parts = []
            for w in walls[:3]:
                sign = "+" if w["gex"] > 0 else "-"
                wall_parts.append(f"${w['strike']:.0f} ({w['side']}) {sign}${abs(w['gex']):,.0f}")
            logger.info("  GAMMA_WALLS:  %s", "  |  ".join(wall_parts))

        # Top 5 strikes by absolute Net Gamma
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
    # Per-strategy last trigger
    # ------------------------------------------------------------------

    def _build_last_trigger(self) -> Dict[str, Dict[str, Any]]:
        """Build last_trigger data for each strategy from open + resolved signals."""
        if not self._signal_tracker:
            return {}

        triggers: Dict[str, Dict[str, Any]] = {}
        now = time.time()

        # Build timestamp -> signal map for open signals
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

        # Build timestamp -> signal map for resolved signals
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

        # Merge: prefer open signal (most recent), fall back to resolved
        all_strats = set(open_by_strat.keys()) | set(resolved_by_strat.keys())
        for sid in all_strats:
            open_sig = open_by_strat.get(sid)
            resolved_sig = resolved_by_strat.get(sid)

            if open_sig and resolved_sig:
                # Pick whichever is more recent
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

    # ------------------------------------------------------------------
    # Per-strategy health data
    # ------------------------------------------------------------------

    def _build_strategy_health(self) -> Dict[str, Dict[str, Any]]:
        """Build per-strategy health data for the heatmap JSON export."""
        if not self._strategy_engine or not self._signal_tracker:
            return {}

        health: Dict[str, Dict[str, Any]] = {}
        now = time.time()

        # Get strategy stats from signal tracker
        strat_stats = self._signal_tracker.get_strategy_stats()

        for strat in self._strategy_engine._strategies:
            sid = strat.strategy_id
            stats = strat_stats.get(sid, {})

            # Count signals from recent signals buffer
            signal_count = 0
            last_signal_ts = 0.0
            sparkline_values: list = []

            # Get resolved signals for this strategy
            resolved = self._signal_tracker.get_resolved()
            strategy_resolved = [r for r in resolved if r.open_signal.strategy_id == sid]

            # Build sparkline from cumulative PnL over resolved signals
            cumulative = 0.0
            for r in strategy_resolved[-8:]:
                cumulative += r.pnl
                sparkline_values.append(round(cumulative, 2))

            # If not enough resolved signals, pad with zeros
            while len(sparkline_values) < 8:
                sparkline_values.insert(0, 0.0)

            # Count total signals for this strategy
            total_signals = stats.get("total_signals", 0)
            wins = stats.get("wins", 0)
            losses = stats.get("losses", 0)
            closed = stats.get("closed", 0)
            resolved_count = wins + losses + closed

            # Win rate from resolved signals
            win_rate = wins / resolved_count if resolved_count > 0 else 0.0

            # PnL
            pnl = stats.get("total_pnl", 0.0)

            # Status: active if has resolved signals, idle otherwise
            if total_signals > 0:
                status = "active"
            else:
                status = "idle"

            # Check if any open signals exist for this strategy
            open_signals = self._signal_tracker.get_open_signals()
            has_open = any(s.strategy_id == sid for s in open_signals)
            if has_open and status == "idle":
                status = "active"

            # Track the most recent signal timestamp (open or resolved)
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

    # ------------------------------------------------------------------
    # Dashboard (Streamlit)
    # ------------------------------------------------------------------

    def _start_dashboard(self) -> None:
        """Spawn the Streamlit Command Center as a background subprocess."""
        if self._dashboard_process is not None:
            return  # already running

        # Pass symbol via environment variable so multi-instance works
        env = os.environ.copy()
        env["SYNGEX_SYMBOL"] = self.symbol

        script_path = Path(__file__).parent / "app_dashboard.py"
        venv_streamlit = Path(__file__).parent / "venv" / "bin" / "streamlit"

        logger.info("Starting Command Center…")

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
                cwd=str(Path(__file__).parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
            logger.info(
                "Command Center started (PID %d, port %d).  "
                "Open http://localhost:%d in a browser.",
                self._dashboard_process.pid,
                self._port,
                self._port,
            )
        except FileNotFoundError:
            logger.warning(
                "Streamlit not found at %s — Command Center will not start.  "
                "Install with: pip install streamlit",
                venv_streamlit,
            )
        except Exception as exc:
            logger.warning("Failed to start Command Center: %s", exc)

    def _stop_dashboard(self) -> None:
        """Terminate the Streamlit Command Center subprocess."""
        if self._dashboard_process is None:
            return

        logger.info("Stopping Command Center (PID %d)…", self._dashboard_process.pid)
        try:
            self._dashboard_process.terminate()
            self._dashboard_process.wait(timeout=5)
        except Exception:
            try:
                self._dashboard_process.kill()
            except Exception:
                pass
        finally:
            self._dashboard_process = None

    # ------------------------------------------------------------------
    # Heatmap (Flask + SocketIO)
    # ------------------------------------------------------------------

    def _start_heatmap(self) -> None:
        """Spawn the Heatmap Dashboard as a background subprocess on port self._port + 1."""
        if self._heatmap_process is not None:
            return  # already running

        heatmap_port = self._port + 1

        env = os.environ.copy()
        env["SYNGEX_SYMBOL"] = self.symbol
        env["HEATMAP_PORT"] = str(heatmap_port)

        script_path = Path(__file__).parent / "app_heatmap.py"
        venv_python = Path(__file__).parent / "venv" / "bin" / "python"
        log_path = self._data_dir.parent / "log" / "heatmap.log"

        logger.info("Starting Heatmap Dashboard…")

        try:
            self._heatmap_stderr = open(log_path, "a")  # append mode — avoids PIPE buffer deadlock
            self._heatmap_process = subprocess.Popen(
                [
                    str(venv_python),
                    str(script_path),
                ],
                cwd=str(Path(__file__).parent),
                stdout=subprocess.DEVNULL,
                stderr=self._heatmap_stderr,
                env=env,
            )
            # Check for immediate startup failures
            ret = self._heatmap_process.poll()
            if ret is not None:
                self._heatmap_process.wait()
                try:
                    with open(log_path, "r") as f:
                        err_msg = f.read().strip()
                except OSError:
                    err_msg = "unknown"
                logger.warning(
                    "Heatmap Dashboard failed to start (exit %d): %s",
                    ret, err_msg[:500],
                )
                self._heatmap_process = None
                return
            logger.info(
                "Heatmap Dashboard started (PID %d, port %d).  "
                "Open http://localhost:%d in a browser.",
                self._heatmap_process.pid,
                heatmap_port,
                heatmap_port,
            )
        except FileNotFoundError:
            logger.warning(
                "app_heatmap.py not found — Heatmap Dashboard will not start.  "
                "Ensure flask and flask-socketio are installed.",
            )
        except Exception as exc:
            logger.warning("Failed to start Heatmap Dashboard: %s", exc)

    def _stop_heatmap(self) -> None:
        """Terminate the Heatmap Dashboard subprocess."""
        if self._heatmap_process is None:
            return

        logger.info("Stopping Heatmap Dashboard (PID %d)…", self._heatmap_process.pid)
        try:
            self._heatmap_process.terminate()
            self._heatmap_process.wait(timeout=5)
        except Exception:
            try:
                self._heatmap_process.kill()
            except Exception:
                pass
        finally:
            if self._heatmap_stderr is not None:
                try:
                    self._heatmap_stderr.close()
                except Exception:
                    pass
                self._heatmap_stderr = None
            self._heatmap_process = None

    # ------------------------------------------------------------------
    # Phi Accumulator Crash Recovery
    # ------------------------------------------------------------------

    def _persist_phi_accumulators(self) -> None:
        """Write current phi tick accumulators to a JSON file for crash recovery.

        Rate-limited: only writes if PHI_WRITE_INTERVAL seconds have elapsed
        since the last write. This avoids excessive disk I/O during high-
        frequency streaming while still preserving accumulators on crash.
        """
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
            logger.debug("Failed to persist phi accumulators: %s", exc)

    def _load_phi_accumulators(self) -> None:
        """Load persisted phi tick accumulators from disk on startup.

        Restores in-progress accumulators so a crash doesn't lose
        partial tick data.
        """
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
            logger.debug("Failed to load phi accumulators: %s", exc)

    # ------------------------------------------------------------------
    # GEX State Export (shared file for Streamlit)
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

        # Add strategy engine status
        if self._strategy_engine:
            export["strategy_engine"] = self._strategy_engine.get_status()
            # Per-strategy health data for heatmap
            export["strategy_health"] = self._build_strategy_health()
            # Per-strategy last trigger for execution card
            export["last_trigger"] = self._build_last_trigger()
            # Micro-signal confidence overlay for dashboard
            recent = self._strategy_engine.get_recent_signals(20)
            micro_signals: Dict[str, Dict[str, Any]] = {}
            for sig in recent:
                strike = sig.get("target", sig.get("entry", 0))
                if strike:
                    key = f"{strike:.1f}"
                    # Keep highest confidence per strike
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

    # ------------------------------------------------------------------
    # Depth snapshot builder
    # ------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Syngex Pipeline Orchestrator"
    )
    parser.add_argument("symbol", help="The ticker symbol to trade (e.g., TSLA)")
    parser.add_argument(
        "mode",
        nargs="?",
        default="stream",
        choices=["stream", "dashboard"],
        help="Run mode: 'stream' (terminal logging, default) or 'dashboard' (starts Streamlit)",
    )
    # --quotes kept as no-op for backwards compatibility
    parser.add_argument(
        "--quotes",
        action="store_true",
        help="(deprecated — quotes are always subscribed)",
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

    # Graceful shutdown on signals
    loop = asyncio.get_running_loop()

    def _signal_handler() -> None:
        logger.info("Shutdown signal received.")
        asyncio.ensure_future(orchestrator.shutdown())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)

    try:
        # 1. Initialize
        await orchestrator.initialize()

        # 2. Connect
        await orchestrator.connect()

        # 3. Run
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
