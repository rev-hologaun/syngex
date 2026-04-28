#!/usr/bin/env python3
"""
SYNGEX - TradeStation Option Chain Streamer
────────────────────────────────────────────
Main application that subscribes ONLY to the option chain stream endpoint.

NO REST quote lookups. NO backup polling. Just the SSE stream.

Usage:
    python3 main.py [SYMBOL]
"""

import asyncio
import json
import os
import sys
import time

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
    """Loads tokens from tfresh2's token.json and provides a valid access token."""

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
            print(f"[TokenManager] Loaded token from {self.token_path}")
            print(f"[TokenManager] Expires at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(self._expires_at))}")
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
# TradeStationClient — minimal, stream-only
# ---------------------------------------------------------------------------

import httpx

BASE_URL = "https://sim-api.tradestation.com"


class TradeStationClient:
    """HTTP client for TradeStation API with streaming support.

    NOTE: This client does NOT perform REST quote lookups.
    It only supports streaming via SSE.
    """

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
    ) -> list[dict]:
        """Stream real-time option chain updates for a symbol.

        Connects to /v3/marketdata/stream/options/chains/{symbol} and
        reads SSE events until duration expires or max_items reached.
        """
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
                            print(f"[CHAIN] {json.dumps(obj, default=str)[:400]}")
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
# Main — subscribe to option chain stream ONLY
# ---------------------------------------------------------------------------

async def main(symbol: str):
    print("=" * 60)
    print("  --- SYNGEX OPTION CHAIN STREAMER ---")
    print(f"  Symbol: {symbol}")
    print("=" * 60)
    print()

    # 1. Initialize token manager
    tm = TokenManager()
    if not tm.is_valid():
        print("\n⚠ WARNING: Token may be expired. Streaming may fail.")
    print()

    # 2. Initialize client
    client = TradeStationClient(tm)

    # 3. Subscribe to option chain stream ONLY
    #    NO REST quote lookups. NO backup polling.
    print("-" * 60)
    print("SUBSCRIBING TO OPTION CHAIN STREAM")
    print("-" * 60)
    print(f"  Endpoint: /v3/marketdata/stream/options/chains/{symbol}")
    print(f"  Duration: 30 seconds")
    print(f"  Max items: 100")
    print()

    try:
        results = await client.stream_option_chain(
            symbol=symbol,
            duration_seconds=30,
            max_items=100,
        )
        print()
        print(f"  Total option chain updates received: {len(results)}")
        if results:
            print(f"  Last update: {json.dumps(results[-1], default=str)[:400]}")
        else:
            print("  No option chain updates received in 30 seconds.")
    except Exception as e:
        print(f"  ✗ Exception during stream: {e}")

    print()
    print("=" * 60)
    print("  STREAM COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [SYMBOL]")
        print(f"Example: {sys.argv[0]} SYNX")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    asyncio.run(main(symbol))
