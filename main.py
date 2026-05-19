#!/usr/bin/env python3
"""Syngex Pipeline - Entry Point"""

import argparse
import asyncio
import signal
import sys

from core.orchestrator import SyngexOrchestrator


async def main() -> None:
    parser = argparse.ArgumentParser(description="Syngex Pipeline")
    parser.add_argument("symbol", help="Ticker symbol")
    parser.add_argument(
        "mode",
        nargs="?",
        default="stream",
        choices=["stream", "dashboard"],
        help="Run mode: 'stream' (terminal logging) or 'dashboard' (starts Streamlit)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port for the Streamlit Command Center (default: 8501)",
    )
    parser.add_argument(
        "--json-log",
        action="store_true",
        help="Enable structured JSON logging for production",
    )
    args = parser.parse_args()

    orchestrator = SyngexOrchestrator(
        symbol=args.symbol,
        mode=args.mode,
        port=args.port,
        json_log=args.json_log,
    )

    # Graceful shutdown on signals
    loop = asyncio.get_running_loop()

    def _signal_handler() -> None:
        asyncio.ensure_future(orchestrator.shutdown())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)

    try:
        await orchestrator.initialize()
        await orchestrator.connect()
        await orchestrator.run()
    except Exception as exc:
        print(f"Pipeline failure: {exc}")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
