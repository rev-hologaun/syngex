#!/usr/bin/env python3
"""
SYNGEX RAW STREAM DEBUGGER
───────────────────────────
Diagnostic script to verify TradeStation API data flow for a given symbol.

Uses the existing TokenManager (reading from ~/projects/tfresh2/token.json)
and TradeStationClient (from tradestation_mcp) to test:
  1. REST: Option Chain GET /v3/marketdata/optionchain/{symbol}
  2. Stream: Real-time option chain updates via /v3/marketdata/stream/options/chains/{symbol}

Usage:
    python3 debug_stream.py [SYMBOL]
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
# Minimal TokenManager that reads from ~/projects/tfresh2/token.json
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
            print(f"[TokenManager] Scope: {self._scope}")
            print(f"[TokenManager] Expires at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(self._expires_at))}")
            print(f"[TokenManager] Has refresh_token: {bool(self._refresh_token)}")
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
# Minimal TradeStationClient (adapted from tradestation_mcp.client)
# ---------------------------------------------------------------------------

import httpx

BASE_URL = "https://sim-api.tradestation.com"

ERROR_DESCRIPTIONS = {
    400: "Bad Request — The request was malformed or contained invalid parameters.",
    401: "Unauthorized — Access token is missing, invalid, or expired.",
    403: "Forbidden — You do not have permission to access this resource.",
    404: "Not Found — The requested resource does not exist.",
    429: "Rate Limited — Too many requests. Please slow down.",
    503: "Service Unavailable — TradeStation API is temporarily unavailable.",
    504: "Gateway Timeout — The request timed out upstream.",
}


class TradeStationClient:
    """HTTP client for TradeStation API with streaming support."""

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

    async def get(self, path: str, params: dict | None = None) -> httpx.Response:
        """Return raw httpx.Response for debugging (not parsed)."""
        client = await self._ensure_client()
        resp = await client.get(path, headers=self._get_headers(), params=params)
        return resp

    async def stream_get(
        self,
        path: str,
        params: dict | None = None,
        duration_seconds: int = 10,
        max_items: int = 100,
    ) -> list[dict]:
        """Stream data from a TradeStation streaming endpoint."""
        results: list[dict] = []
        client = await self._ensure_client()
        headers = self._get_headers()

        try:
            async with client.stream(
                "GET", path, headers=headers, params=params,
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
                            print(f"[QUOTE STREAM] {json.dumps(obj, default=str)[:300]}")
                        except json.JSONDecodeError:
                            pass

                        if len(results) >= max_items:
                            return results

                    if asyncio.get_event_loop().time() >= deadline:
                        break

        except httpx.ReadTimeout:
            pass
        except httpx.HTTPError as e:
            print(f"[QUOTE STREAM] Error: {e}")

        return results


# ---------------------------------------------------------------------------
# Main diagnostic flow
# ---------------------------------------------------------------------------

async def main(symbol: str):
    print("=" * 60)
    print("  --- SYNGEX RAW STREAM DEBUGGER ---")
    print(f"  Target symbol: {symbol}")
    print("=" * 60)
    print()

    # 1. Initialize token manager
    tm = TokenManager()
    if not tm.is_valid():
        print("\n⚠ WARNING: Token is expired or invalid. Continuing anyway to see API response...")
    print()

    # 2. Initialize client
    client = TradeStationClient(tm)

    # ── Test 1: REST — Quote Lookup ─────────────────────────────
    # Uses the working REST /quotes endpoint to verify the symbol
    # is recognized by the API. If the symbol returns 404, skip
    # straight to the stream test (option chains may still work).
    print("-" * 60)
    print("TEST 1: REST — Quote Lookup")
    print("-" * 60)
    print(f"  Endpoint: GET /v3/marketdata/quotes/{symbol}")
    print(f"  Purpose:  Verify symbol is recognized by the API")
    print(f"  Type:     Standard REST request (one-shot)")
    print()

    try:
        resp = await client.get(f"/v3/marketdata/quotes/{symbol}")
        print(f"  Status: {resp.status_code}")
        raw_body = resp.text
        print(f"  Response body length: {len(raw_body)} bytes")
        print()

        if resp.status_code == 200:
            print("  ✓ SUCCESS — Quote returned data")
            print()
            try:
                data = resp.json()
                lines = json.dumps(data, indent=2, default=str).split("\n")[:5]
                print("  First 5 lines of parsed JSON:")
                for line in lines:
                    print(f"    {line}")
            except json.JSONDecodeError:
                print(f"  Raw response (first 500 chars):")
                print(f"    {raw_body[:500]}")
        elif resp.status_code == 404:
            print("  ⚠ 404 Not Found: Symbol not found via REST quotes — skipping to stream test.")
        else:
            print(f"  ⚠ Unexpected status {resp.status_code} — proceeding to stream test.")
            print(f"  Response: {raw_body[:500]}")
    except Exception as e:
        print(f"  ⚠ Exception during REST request: {e} — proceeding to stream test.")

    print()

    # ── Test 2: Stream — Real-time Option Chain ──────────────────
    # This opens a persistent SSE connection to receive live option chain
    # updates for the symbol. Different from the REST call in Test 1.
    print("-" * 60)
    print("TEST 2: Stream — Real-time Option Chain")
    print("-" * 60)
    print(f"  Endpoint: GET /v3/marketdata/stream/options/chains/{symbol}")
    print(f"  Purpose:  Listen for live option chain updates via SSE")
    print(f"  Type:     Persistent streaming connection")
    print(f"  Duration: 10 seconds")
    print()

    try:
        results = await client.stream_get(
            f"/v3/marketdata/stream/options/chains/{symbol}",
            duration_seconds=10,
            max_items=50,
        )
        print()
        print(f"  Total option chain updates received: {len(results)}")
        if results:
            print(f"  Last update: {json.dumps(results[-1], default=str)[:300]}")
        else:
            print("  No option chain updates received in 10 seconds.")
    except Exception as e:
        print(f"  ✗ Exception during Stream Option Chain: {e}")

    print()
    print("=" * 60)
    print("  DEBUG COMPLETE")
    print("=" * 60)
    print()
    print("  Summary:")
    print("    Test 1 (REST)  → Is the option chain available for this symbol?")
    print("    Test 2 (Stream) → Can we receive live option chain updates?")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [SYMBOL]")
        print(f"Example: {sys.argv[0]} SYNX")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    asyncio.run(main(symbol))
