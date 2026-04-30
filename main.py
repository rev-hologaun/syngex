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
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

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
    DeltaIVDivergence,
    IVGEXDivergence,
)


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
        self, symbol: str, mode: str = "stream"
    ) -> None:
        self.symbol = symbol.upper()
        self.mode = mode.lower()
        self._client: TradeStationClient | None = None
        self._calculator: GEXCalculator | None = None
        self._dashboard: SyngexDashboard | None = None
        self._strategy_engine: StrategyEngine | None = None
        self._gamma_filter: NetGammaFilter | None = None
        self._rolling_data: Dict[str, RollingWindow] = {}
        self._running = False
        self._profile_timer: float = 0.0
        self._dashboard_process: subprocess.Popen | None = None
        self._state_export_timer: float = 0.0

        # Shared data file for Streamlit dashboard
        self._data_dir = Path(__file__).parent / "data"
        self._data_file = self._data_dir / "gex_state.json"

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
        self._strategy_engine = StrategyEngine(
            config=EngineConfig(
                min_confidence=0.35,
                max_signals_per_tick=10,
                signal_log_path=str(self._data_dir.parent / "log" / "signals.jsonl"),
                dedup_window_seconds=30.0,
            )
        )
        self._strategy_engine.register_filter(self._gamma_filter.evaluate_signal)

        # Register all layer1 strategies
        for strat_cls in (
            GammaWallBounce,
            MagnetAccelerate,
            GammaFlipBreakout,
            GammaSqueeze,
            GEXImbalance,
            ConfluenceReversal,
            VolCompressionRange,
            GEXDivergence,
        ):
            self._strategy_engine.register(strat_cls(self._calculator))
        logger.info("Registered %d layer1 strategies", self._strategy_engine.strategy_count)

        # Register Layer 2 strategies (Alpha Greeks)
        ENABLE_LAYER2 = True
        if ENABLE_LAYER2:
            layer2_strategies = (
                DeltaGammaSqueeze,
                DeltaVolumeExhaustion,
                CallPutFlowAsymmetry,
                DeltaIVDivergence,
                IVGEXDivergence,
            )
            for strat_cls in layer2_strategies:
                self._strategy_engine.register(strat_cls(self._calculator))
            logger.info("Registered %d layer2 strategies", len(layer2_strategies))

        # Rolling windows for key metrics
        self._rolling_data = {
            "price": RollingWindow(window_type="time", window_size=300),
            "price_5m": RollingWindow(window_type="time", window_size=300),
            "price_30m": RollingWindow(window_type="time", window_size=1800),
            "net_gamma": RollingWindow(window_type="time", window_size=300),
            "net_gamma_5m": RollingWindow(window_type="time", window_size=300),
            "volume_5m": RollingWindow(window_type="time", window_size=300),
        }

        # Layer 2 rolling windows
        if "delta" not in self._rolling_data:
            self._rolling_data["delta"] = RollingWindow(window_type="time", window_size=300)
        if "volume" not in self._rolling_data:
            self._rolling_data["volume"] = RollingWindow(window_type="time", window_size=300)

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

                # Strategy evaluation (every ~1s)
                if now - self._profile_timer >= 1.0:
                    self._evaluate_strategies()

                # Fail-fast: option chain critical error
                if self._client._option_chain_failed:
                    logger.error("Option chain stream failed (critical error). Shutting down.")
                    break

                await asyncio.sleep(0.25)
        finally:
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
            "gex_calculator": self._calculator,
            "rolling_data": self._rolling_data,
            "timestamp": time.time(),
            "regime": self._gamma_filter.regime,
            "net_gamma": net_gamma,
            "gamma_flip": flip,
            "greeks_summary": self._calculator.get_greeks_summary(),
        }

        # Run evaluation
        signals = self._strategy_engine.process(data)

        if signals:
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
        """Spawn the Streamlit dashboard as a background subprocess."""
        if self._dashboard_process is not None:
            return  # already running

        # Ensure data directory exists
        self._data_dir.mkdir(parents=True, exist_ok=True)

        script_path = Path(__file__).parent / "app_dashboard.py"
        venv_streamlit = Path(__file__).parent / "venv" / "bin" / "streamlit"

        logger.info("Starting Streamlit dashboard…")

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
                ],
                cwd=str(Path(__file__).parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(
                "Dashboard started (PID %d).  "
                "Open http://localhost:8501 in a browser.",
                self._dashboard_process.pid,
            )
        except FileNotFoundError:
            logger.warning(
                "Streamlit not found at %s — dashboard will not start.  "
                "Install with: pip install streamlit",
                venv_streamlit,
            )
        except Exception as exc:
            logger.warning("Failed to start dashboard: %s", exc)

    def _stop_dashboard(self) -> None:
        """Terminate the Streamlit dashboard subprocess."""
        if self._dashboard_process is None:
            return

        logger.info("Stopping dashboard (PID %d)…", self._dashboard_process.pid)
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
    args = parser.parse_args()

    orchestrator = SyngexOrchestrator(
        symbol=args.symbol, mode=args.mode
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
