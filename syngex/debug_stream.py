#!/usr/bin/env python3
"""
syngex/debug_stream.py — Live-stream TradeStation marketdata SSE endpoints to a terminal.

Usage:
    python -m syngex debug_stream quotes SPY
    python -m syngex debug_stream options SPY
    python -m syngex debug_stream depth-quotes SPY
    python -m syngex debug_stream depth-agg SPY
    python -m syngex debug_stream all SPY

Options:
    --lines       Print raw JSON lines instead of pretty-printed
    --help        Show this help message
"""

from __future__ import annotations

import argparse
import asyncio
import json
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import aiohttp

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so relative imports work
# ---------------------------------------------------------------------------
_project_root = __import__("pathlib").Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ingestor.token_manager import TokenManager  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://api.tradestation.com/v3"

RETRY_START = 1       # initial reconnect delay (seconds)
RETRY_MAX = 30        # maximum reconnect delay cap (seconds)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts() -> str:
    """Return a [HH:MM:SS.mmm] timestamp for stderr output."""
    now = datetime.now().astimezone(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    return f"[{now}]"


def _log(msg: str) -> None:
    """Print a timestamped message to stderr."""
    print(f"{_ts()} {msg}", file=sys.stderr, flush=True)


def _build_endpoint(subcmd: str, symbol: str) -> tuple[str, Dict[str, Any]]:
    """Return (url, params) for the given subcommand and symbol."""
    if subcmd == "quotes":
        return f"{BASE_URL}/marketdata/stream/quotes/{symbol}", {}
    if subcmd == "options":
        return f"{BASE_URL}/marketdata/stream/options/chains/{symbol}", {"strikeProximity": 16}
    if subcmd == "depth-quotes":
        return f"{BASE_URL}/marketdata/stream/marketdepth/quotes/{symbol}", {"maxlevels": 20}
    if subcmd == "depth-agg":
        return f"{BASE_URL}/marketdata/stream/marketdepth/aggregates/{symbol}", {"maxlevels": 20}
    raise ValueError(f"Unknown subcommand: {subcmd}")


# ---------------------------------------------------------------------------
# Stream runner
# ---------------------------------------------------------------------------

async def _stream_loop(
    subcmd: str,
    symbol: str,
    pretty: bool,
) -> None:
    """Open an SSE connection and drain messages to stdout."""
    url, params = _build_endpoint(subcmd, symbol)
    token_mgr = TokenManager()
    token = token_mgr.get_access_token()

    if not token:
        _log("❌ No access token found. Ensure ~/projects/tfresh2/token.json exists.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    timeout = aiohttp.ClientTimeout(sock_read=60)

    retry_delay = RETRY_START
    session: Optional[aiohttp.ClientSession] = None
    session_start = time.monotonic()
    msg_count = 0

    try:
        while True:
            try:
                if session is None or session.closed:
                    session = aiohttp.ClientSession(timeout=timeout)

                await asyncio.sleep(0)  # yield before connect

                _log(f"🔗 Connecting to {url}")
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 401:
                        _log("❌ 401 Unauthorized — token may be expired.")
                        await asyncio.sleep(5)
                        continue
                    if resp.status == 404:
                        _log(f"❌ 404 Not Found — endpoint may have changed: {url}")
                        return
                    resp.raise_for_status()

                    # Connected
                    session_start = time.monotonic()
                    msg_count = 0
                    retry_delay = RETRY_START
                    _log(f"✅ Connected — {url}  (session msgs: 0)")

                    async for line in resp.content:
                        line_str = line.decode("utf-8", errors="replace").strip()
                        if not line_str:
                            continue

                        msg_count += 1
                        try:
                            data = json.loads(line_str)
                        except json.JSONDecodeError:
                            _log(f"⚠️  Non-JSON line (#{msg_count}): {line_str[:120]}")
                            continue

                        if pretty:
                            print(json.dumps(data, indent=2, default=str))
                        else:
                            print(line_str)

                        # Flush stdout after each message so it appears live
                        sys.stdout.flush()

            except aiohttp.ClientConnectorError as exc:
                _log(f"❌ Connection error: {exc}. Reconnecting in {retry_delay}s…")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, RETRY_MAX)

            except aiohttp.ClientPayloadError as exc:
                _log(f"❌ Payload error: {exc}. Reconnecting in 2s…")
                await asyncio.sleep(2)

            except asyncio.TimeoutError:
                _log("⚠️  Stream timeout. Reconnecting in 2s…")
                await asyncio.sleep(2)

            except aiohttp.ClientResponseError as exc:
                if exc.status == 429:
                    _log(f"⚠️  429 Too Many Requests — backing off {retry_delay}s…")
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, RETRY_MAX)
                elif exc.status == 401:
                    _log("⚠️  401 Unauthorized — refreshing token and retrying…")
                    token = token_mgr.get_access_token()
                    if token:
                        headers["Authorization"] = f"Bearer {token}"
                    await asyncio.sleep(5)
                else:
                    _log(f"⚠️  HTTP {exc.status}: {exc}. Reconnecting in 5s…")
                    await asyncio.sleep(5)

            except Exception as exc:
                _log(f"❌ Unexpected error: {type(exc).__name__}: {exc}")
                await asyncio.sleep(5)

    finally:
        if session and not session.closed:
            await session.close()
        elapsed = time.monotonic() - session_start
        _log(f"📊 Session stats — {msg_count} messages over {elapsed:.1f}s")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

SUBCOMMANDS = ["quotes", "options", "depth-quotes", "depth-agg", "all"]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Live-stream TradeStation marketdata SSE endpoints to a terminal.",
    )
    parser.add_argument(
        "subcommand",
        choices=SUBCOMMANDS,
        help="Which endpoint to stream (quotes, options, depth-quotes, depth-agg, all)",
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="Symbol(s) to stream (e.g. SPY or SPY AAPL)",
    )
    parser.add_argument(
        "--lines",
        action="store_true",
        help="Print raw JSON lines instead of pretty-printed",
    )
    return parser.parse_args(argv)


async def _run_all(symbols: list[str], pretty: bool) -> None:
    """Run all subcommands concurrently for the given symbols."""
    tasks = []
    for subcmd in ["quotes", "options", "depth-quotes", "depth-agg"]:
        for sym in symbols:
            tasks.append(asyncio.create_task(_stream_loop(subcmd, sym, pretty)))
    await asyncio.gather(*tasks)


async def _main_async() -> None:
    args = _parse_args()
    pretty = not args.lines

    # Handle SIGINT / Ctrl+C cleanly
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        _log("🛑 Interrupted — shutting down…")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    if args.subcommand == "all":
        await _run_all(args.symbols, pretty)
    else:
        for sym in args.symbols:
            await _stream_loop(args.subcommand, sym, pretty)


def main() -> None:
    try:
        asyncio.run(_main_async())
    except KeyboardInterrupt:
        _log("🛑 Interrupted — exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
