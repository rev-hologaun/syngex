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
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Type

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
from engine.dashboard import SyngexDashboard
from strategies.engine import StrategyEngine, EngineConfig
from strategies.filters.net_gamma_filter import NetGammaFilter
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


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class SyngexOrchestrator:
    """
    Manages the full lifecycle of the Syngex pipeline.

    Lifecycle:
        initialize() → connect() → run() → shutdown()
    """

    # How often (seconds) to log the Gamma Profile
    PROFILE_INTERVAL: float = 5.0

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
        self._profile_timer: float = 0.0
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
        self._dashboard = SyngexDashboard(orchestrator=self)
        self._client = TradeStationClient()

        # Phase 0: Strategy Engine + Filter
        self._gamma_filter = NetGammaFilter(flip_buffer=0.5)

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
            self._strategy_engine.register_filter(self._gamma_filter.evaluate_signal)
            logger.info("Registered net_gamma filter (flip_buffer=%.2f)", flip_buffer)

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
            # Layer 3 / full_data rolling windows (missing feeds)
            KEY_VOLUME_UP_5M: RollingWindow(window_type="time", window_size=300),
            KEY_VOLUME_DOWN_5M: RollingWindow(window_type="time", window_size=300),
            KEY_TOTAL_GAMMA_5M: RollingWindow(window_type="time", window_size=300),
            KEY_IV_SKEW_5M: RollingWindow(window_type="time", window_size=300),
            KEY_FLOW_RATIO_5M: RollingWindow(window_type="time", window_size=300),
            KEY_EXTRINSIC_PROXY_5M: RollingWindow(window_type="time", window_size=300),
            KEY_PROB_MOMENTUM_5M: RollingWindow(window_type="time", window_size=300),
            # iv_gex_divergence v2 — Volatility-Snap rolling windows
            KEY_IV_SKEW_GRADIENT_5M: RollingWindow(window_type="time", window_size=300),
            KEY_GAMMA_DENSITY_5M: RollingWindow(window_type="time", window_size=300),
            # delta_iv_divergence v2 — Tail-Risk Divergence rolling windows
            KEY_OTM_DELTA_5M: RollingWindow(window_type="time", window_size=300),
            KEY_OTM_IV_5M: RollingWindow(window_type="time", window_size=300),
            KEY_DELTA_IV_CORR_5M: RollingWindow(window_type="time", window_size=300),
            # Depth / L2 rolling windows
            KEY_DEPTH_BID_SIZE_5M: RollingWindow(window_type="time", window_size=300),
            KEY_DEPTH_ASK_SIZE_5M: RollingWindow(window_type="time", window_size=300),
            KEY_DEPTH_SPREAD_5M: RollingWindow(window_type="time", window_size=300),
            KEY_DEPTH_BID_LEVELS_5M: RollingWindow(window_type="time", window_size=300),
            KEY_DEPTH_ASK_LEVELS_5M: RollingWindow(window_type="time", window_size=300),
            # Squeeze depth rolling windows (liquidity vacuum detection)
            KEY_DEPTH_BID_SIZE_ROLLING: RollingWindow(window_type="time", window_size=60),
            KEY_DEPTH_ASK_SIZE_ROLLING: RollingWindow(window_type="time", window_size=60),
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
                if now - self._profile_timer >= 1.0:
                    self._evaluate_strategies()

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

                # Push probability momentum for prob_distribution_shift
                try:
                    atm_strike = self._calculator.get_atm_strike(self._calculator.underlying_price)
                    if atm_strike is not None and KEY_PROB_MOMENTUM_5M in self._rolling_data:
                        momentum = 0.0
                        for strike_str, strike_data in gex_summary.items():
                            try:
                                strike = float(strike_str)
                            except (ValueError, TypeError):
                                continue
                            call_delta = strike_data.get("call_delta_sum", 0.0)
                            put_delta = strike_data.get("put_delta_sum", 0.0)
                            if call_delta == 0 and put_delta == 0:
                                continue
                            distance = strike - atm_strike
                            momentum += (call_delta - put_delta) * distance
                        self._rolling_data[KEY_PROB_MOMENTUM_5M].push(momentum, time.time())
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

                    atm_iv = self._calculator.get_iv_by_strike(atm_strike)
                    if atm_iv is not None and KEY_ATM_IV_5M in self._rolling_data:
                        self._rolling_data[KEY_ATM_IV_5M].push(atm_iv)

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

            # ── Depth data capture (L2/TotalView) ──
            msg_type = data.get("type", "")
            if msg_type in ("market_depth_quotes", "market_depth_agg"):
                bids = data.get("Bids", [])
                asks = data.get("Asks", [])

                # Aggregate size from all bid/ask levels
                if msg_type == "market_depth_quotes":
                    # Per-exchange: Size field is string → int
                    total_bid_size = sum(int(b.get("Size", 0)) for b in bids)
                    total_ask_size = sum(int(a.get("Size", 0)) for a in asks)
                else:
                    # Aggregated: TotalSize field
                    total_bid_size = sum(int(b.get("TotalSize", 0)) for b in bids)
                    total_ask_size = sum(int(a.get("TotalSize", 0)) for a in asks)

                # Best bid/ask for spread
                best_bid = float(bids[0].get("Price", 0)) if bids else 0.0
                best_ask = float(asks[0].get("Price", 0)) if asks else 0.0
                spread = best_ask - best_bid if best_bid > 0 and best_ask > 0 else 0.0

                ts = time.time()
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

                # Squeeze-specific: track depth on the breakout side for liquidity vacuum detection
                if KEY_DEPTH_BID_SIZE_ROLLING in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_BID_SIZE_ROLLING].push(total_bid_size, ts)
                if KEY_DEPTH_ASK_SIZE_ROLLING in self._rolling_data:
                    self._rolling_data[KEY_DEPTH_ASK_SIZE_ROLLING].push(total_ask_size, ts)


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
