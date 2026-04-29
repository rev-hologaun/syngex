#!/usr/bin/env python3
"""
SYNGEX — Terminal GEX Calculator (Smoke Test)
──────────────────────────────────────────────
Lightweight, single-file script to validate the TradeStation option chain
data stream and GEX calculation logic.

Prints ONE high-visibility line per processed message:
    [TIMESTAMP] | [MSG_TYPE] | [STRIKE] | [NET_GAMMA_DELTA]

No Rich, no TUI framework — plain fast stdout.

Usage:
    python3 tui_test_gex.py [SYMBOL]
"""

import asyncio
import json
import os
import sys
import time

# Unbuffered stdout for real-time output
sys.stdout.reconfigure(line_buffering=True)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TFRESH_DIR = os.path.expanduser("~/projects/tfresh2")
TOKEN_PATH = os.path.join(TFRESH_DIR, "token.json")

# ---------------------------------------------------------------------------
# TokenManager — reads from tfresh2's token.json
# ---------------------------------------------------------------------------

class TokenManager:
    def __init__(self, token_path: str = TOKEN_PATH):
        self.token_path = token_path
        self._access_token: str | None = None
        self._load()

    def _load(self):
        if not os.path.exists(self.token_path):
            print(f"ERROR: Token file not found: {self.token_path}")
            return
        try:
            with open(self.token_path, "r") as f:
                data = json.load(f)
            self._access_token = data.get("access_token")
            self._scope = data.get("scope", "")
            self._expires_at = data.get("expires_at", 0)
            self._refresh_token = data.get("refresh_token")
        except Exception as e:
            print(f"ERROR: Failed to load token: {e}")

    def is_valid(self) -> bool:
        if not self._access_token:
            return False
        return time.time() < (self._expires_at - 120)

    def get_access_token(self) -> str:
        if not self.is_valid():
            print("WARNING: Access token may be expired or invalid.")
        if not self._access_token:
            raise RuntimeError("No access token available.")
        return self._access_token


# ---------------------------------------------------------------------------
# TradeStationClient — stream-only (minimal copy from main.py)
# ---------------------------------------------------------------------------

import httpx

BASE_URL = "https://sim-api.tradestation.com"


class TradeStationClient:
    def __init__(self, token_manager: TokenManager):
        self._token_manager = token_manager
        self._http: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                base_url=BASE_URL,
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._http

    def _get_headers(self) -> dict:
        token = self._token_manager.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    async def stream_option_chain(
        self,
        symbol: str,
        duration_seconds: int = 30,
        max_items: int = 100,
        on_message=None,
    ):
        """Stream option chain updates. Calls on_message(obj) for each parsed SSE event."""
        results: list[dict] = []
        client = await self._ensure_client()
        headers = self._get_headers()
        path = f"/v3/marketdata/stream/options/chains/{symbol}"

        try:
            async with client.stream(
                "GET", path, headers=headers,
                timeout=httpx.Timeout(duration_seconds + 10, connect=10.0),
            ) as resp:
                if resp.status_code != 200:
                    body = b""
                    async for chunk in resp.aiter_bytes():
                        body += chunk
                        if len(body) > 4096:
                            break
                    print(f"\n[STREAM] Non-200 status: {resp.status_code}")
                    print(f"[STREAM] Body: {body.decode(errors='replace')[:500]}")
                    return results

                deadline = asyncio.get_event_loop().time() + duration_seconds
                buffer = ""

                async for chunk in resp.aiter_text():
                    buffer += chunk
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            results.append(obj)
                            if on_message:
                                on_message(obj)
                        except json.JSONDecodeError:
                            pass

                        if len(results) >= max_items:
                            return results

                    if asyncio.get_event_loop().time() >= deadline:
                        break

        except httpx.ReadTimeout:
            pass
        except httpx.HTTPError as e:
            print(f"[STREAM] Error: {e}")

        return results


# ---------------------------------------------------------------------------
# GEXCalculator — inline (from engine/gex_calculator.py)
# ---------------------------------------------------------------------------

from collections import defaultdict

CONTRACT_MULTIPLIER = 100


def _parse_strike_from_symbol(symbol: str):
    import re
    m = re.search(r'[CP](\d{7})$', symbol)
    if m:
        return float(m.group(1)) / 1000.0
    return None


def _parse_type_from_symbol(symbol: str):
    if len(symbol) >= 8 and symbol[-8] == 'C':
        return "Call"
    if len(symbol) >= 8 and symbol[-8] == 'P':
        return "Put"
    last = symbol[-1]
    if last == 'C':
        return "Call"
    if last == 'P':
        return "Put"
    return None


def _extract_strike(event: dict) -> float | None:
    """Extract strike from a stream event."""
    # Try Legs[0].StrikePrice first
    legs = event.get("Legs", [])
    if legs and isinstance(legs, list) and len(legs) > 0:
        lp = legs[0].get("StrikePrice")
        if lp is not None:
            try:
                return float(lp)
            except (ValueError, TypeError):
                pass
    # Try Strikes[] array
    strikes = event.get("Strikes", [])
    if strikes and isinstance(strikes, list) and len(strikes) > 0:
        try:
            return float(strikes[0])
        except (ValueError, TypeError):
            pass
    return None


def _extract_type(event: dict) -> str | None:
    """Extract option type from a stream event."""
    # Try Legs[0].OptionType first
    legs = event.get("Legs", [])
    if legs and isinstance(legs, list) and len(legs) > 0:
        ot = legs[0].get("OptionType")
        if ot:
            return ot
    # Fallback to Side
    side = event.get("Side")
    if side:
        return side
    return None


def _extract_expiration(event: dict) -> str:
    """Extract expiration from a stream event."""
    legs = event.get("Legs", [])
    if legs and isinstance(legs, list) and len(legs) > 0:
        return legs[0].get("Expiration", "")
    return ""


def _extract_symbol(event: dict) -> str:
    """Extract symbol from a stream event."""
    legs = event.get("Legs", [])
    if legs and isinstance(legs, list) and len(legs) > 0:
        return legs[0].get("Symbol", "")
    return event.get("Symbol", "")


def calculate_gex(options: list[dict]):
    """Calculate GEX from a list of option chain events (stream format)."""
    by_strike: dict[float, float] = defaultdict(float)
    num_options = 0

    for event in options:
        strike = _extract_strike(event)
        option_type = _extract_type(event)
        gamma = float(event.get("Gamma", 0))
        open_interest = int(event.get("DailyOpenInterest", 0))

        if strike is None or option_type is None:
            continue
        if gamma == 0:
            continue

        gex = gamma * open_interest * CONTRACT_MULTIPLIER
        if option_type == "Put":
            gex = -abs(gex)

        by_strike[strike] += gex
        num_options += 1

    total_gex = sum(by_strike.values())
    call_gex = sum(v for k, v in by_strike.items() if True)
    put_gex = 0.0

    return {
        "total_gex": total_gex,
        "call_gex": call_gex,
        "put_gex": put_gex,
        "by_strike": by_strike,
        "num_options": num_options,
    }


# ---------------------------------------------------------------------------
# Stream handler — batches events and prints GEX summary periodically
# ---------------------------------------------------------------------------

class GEXHandler:
    """Accumulates SSE events, flushes GEX summary every flush_interval seconds."""

    def __init__(self, symbol: str, flush_interval: float = 1.0):
        self.symbol = symbol
        self.flush_interval = flush_interval  # seconds between summaries
        self.buffer: list[dict] = []
        self.last_flush: float = time.time()
        self.total_received = 0

    def on_message(self, obj: dict):
        """Called for each SSE event. Batches and periodically flushes."""
        self.buffer.append(obj)
        self.total_received += 1
        now = time.time()
        if now - self.last_flush >= self.flush_interval:
            self._flush(now)

    def _flush(self, now: float):
        """Calculate GEX from the batch and print summary."""
        ts = time.strftime("%H:%M:%S")
        count = len(self.buffer)

        if not self.buffer:
            return

        gex_result = calculate_gex(self.buffer)
        total_gex = gex_result["total_gex"]
        by_strike = gex_result["by_strike"]

        # Find top strike by absolute GEX
        if by_strike:
            top_strike = max(by_strike, key=lambda k: abs(by_strike[k]))
            top_gex = by_strike[top_strike]
            strike_str = f"{top_strike:>10.2f}"
            gex_str = f"{top_gex:>14,.0f}"
        else:
            strike_str = "       N/A"
            gex_str = "           0"

        print(f"[{ts}] | CHAIN_UPDATE | {strike_str} | {gex_str}")

        # Reset
        self.buffer = []
        self.last_flush = now

    def final_flush(self):
        """Flush remaining buffer (called at end of stream)."""
        if self.buffer:
            self._flush(time.time())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main(symbol: str):
    print("=" * 70)
    print(f"  SYNGEX GEX CALCULATOR — SMOKE TEST")
    print(f"  Symbol: {symbol}")
    print(f"  Format: [TIMESTAMP] | [MSG_TYPE] | [STRIKE] | [NET_GAMMA_DELTA]")
    print("=" * 70)
    print()

    # Token
    tm = TokenManager()
    if not tm.is_valid():
        print("⚠ Token may be expired — streaming may fail.\n")
    else:
        print(f"✓ Token valid (expires {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(tm._expires_at))})\n")

    # Client
    client = TradeStationClient(tm)

    # Header for summary lines
    print(f"{'TIMESTAMP':<10} | {'MSG_TYPE':<14} | {'STRIKE':>10} | {'NET_GAMMA_DELTA':>14}")
    print("-" * 70)

    # Stream with callback
    handler = GEXHandler(symbol, flush_interval=1.0)
    try:
        results = await client.stream_option_chain(
            symbol=symbol,
            duration_seconds=10,
            max_items=500,
            on_message=handler.on_message,
        )
    except Exception as e:
        print(f"\n✗ Stream error: {e}")
        results = []

    # Flush any remaining events
    handler.final_flush()
    print(f"\n  Total events received: {handler.total_received}")

    print()
    print("=" * 70)
    print(f"  STREAM COMPLETE — {len(results)} messages received")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [SYMBOL]")
        print(f"Example: {sys.argv[0]} SYNX")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    asyncio.run(main(symbol))
