#!/usr/bin/env python3
"""
main.py — Syngex Orchestrator Entry Point

Clean, robust entry point for Project Syngex.
Delegates all orchestration to the orchestrator.lifecycle module.

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

import asyncio
import logging
import signal
import sys
from pathlib import Path

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
# Safety — READ-ONLY enforcement (blocks all order placement)
# ---------------------------------------------------------------------------
from config.trade_guard import READ_ONLY
if READ_ONLY:
    logger.info("🔒 SAFETY: READ-ONLY mode active — all order placement blocked")

# ---------------------------------------------------------------------------
# Import orchestrator
# ---------------------------------------------------------------------------
from orchestrator.lifecycle import SyngexOrchestrator


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main() -> None:
    """Main entry point — delegates to SyngexOrchestrator."""
    import argparse

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
    _shutdown_called = False

    def _signal_handler() -> None:
        nonlocal _shutdown_called
        if _shutdown_called:
            return
        _shutdown_called = True
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
        if not _shutdown_called:
            await orchestrator.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
