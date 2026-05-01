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
# Components
# ---------------------------------------------------------------------------

from ingestor.tradestation_client import TradeStationClient
from engine.gex_calculator import GEXCalculator
from engine.dashboard import SyngexDashboard
from strategies.engine import StrategyEngine, EngineConfig
from strategies.filters.net_gamma_filter import NetGammaFilter
from strategies.rolling_window import RollingWindow
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

        # Signal tracker for outcome resolution (symbol-specific log)
        log_dir = self._data_dir.parent / "log"
        self._signal_tracker = SignalTracker(
            max_hold_seconds=900,
            log_dir=str(log_dir),
            symbol=self.symbol,
        )

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
            "price": RollingWindow(window_type="time", window_size=300),
            "price_5m": RollingWindow(window_type="time", window_size=300),
            "price_30m": RollingWindow(window_type="time", window_size=1800),
            "net_gamma": RollingWindow(window_type="time", window_size=300),
            "net_gamma_5m": RollingWindow(window_type="time", window_size=300),
            "volume_5m": RollingWindow(window_type="time", window_size=300),
            # Layer 2 rolling windows
            "total_delta_5m": RollingWindow(window_type="time", window_size=300),
            "delta": RollingWindow(window_type="time", window_size=300),
            "volume": RollingWindow(window_type="time", window_size=300),
        }

        # Per-strike IV windows (populated lazily)
        self._iv_windows: Dict[str, RollingWindow] = {}

        # Wire callback: ingestor → calculator + engine
        self._client.set_on_message_callback(self._on_message)

        # Register subscriptions — quotes feed underlying price, option chain feeds contracts
        self._client.subscribe_to_quotes(self.symbol)
        self._client.subscribe_to_option_chain(self.symbol)

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

        # Start the Streamlit dashboard as a background subprocess (dashboard mode only)
        if self.mode == "dashboard":
            self._start_dashboard()

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
                    self._rolling_data["price"].push(price, ts)
                    self._rolling_data["price_5m"].push(price, ts)
                    self._rolling_data["price_30m"].push(price, ts)

            # Periodically update net_gamma rolling window
            if self._calculator._msg_count % 20 == 0:
                ng = self._calculator.get_net_gamma()
                self._rolling_data["net_gamma"].push(ng)
                self._rolling_data["net_gamma_5m"].push(ng)

            # Update Layer 2 rolling windows
            gex_summary = self._calculator.get_greeks_summary()
            if gex_summary:
                net_delta = gex_summary.get("net_delta", 0.0)
                if "delta" in self._rolling_data:
                    self._rolling_data["delta"].push(net_delta)
                if "volume" in self._rolling_data:
                    total_vol = gex_summary.get("total_volume", 0)
                    self._rolling_data["volume"].push(total_vol)
                # Track total_delta_5m for delta_volume_exhaustion
                if "total_delta_5m" in self._rolling_data:
                    self._rolling_data["total_delta_5m"].push(net_delta)

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
