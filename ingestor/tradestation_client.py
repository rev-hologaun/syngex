"""
ingestor/tradestation_client.py — The Data Ingestor

HTTP-streaming client for the TradeStation SIM API.

Endpoints:
    Quotes stream:  GET /v3/marketdata/stream/quotes/{symbol}
    Option chain:   GET /v3/marketdata/stream/options/chains/{symbol}

Handles:
    - Token loading from TokenManager
    - Automatic reconnection with exponential backoff
    - Callback-based message dispatch to the GEXCalculator
    - Graceful option-chain fallback
    - Fail-fast on critical errors (401, 404)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional

import aiohttp

from .token_manager import TokenManager

logger = logging.getLogger("Syngex.Ingestor.TradeStationClient")


class TradeStationClient:
    """
    HTTP-streaming client for TradeStation SIM API.

    TradeStation does NOT use WebSockets — it uses HTTP Streaming
    (chunked transfer encoding / Server-Sent Events).

    Lifecycle:
        1. __init__ → create client
        2. subscribe_* → register symbols
        3. connect() → run the streaming loop
        4. stop() → graceful shutdown
    """

    BASE_URL = "https://sim-api.tradestation.com/v3"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or self.BASE_URL
        self.token_manager = TokenManager()
        self._session: aiohttp.ClientSession | None = None
        self._on_message_callback: Optional[Callable[[dict], Any]] = None
        self._is_running = False
        self._headers: Dict[str, str] = {}
        self._quote_symbols: List[str] = []
        self._option_chain_symbols: List[str] = []
        self._option_chain_failed = False
        self._session_lock = asyncio.Lock()
        self._watched_symbol: str = ""  # Symbol whose quotes feed the underlying price
        self._stream_tasks: list[asyncio.Task] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_on_message_callback(self, callback: Callable[[dict], Any]) -> None:
        """Set the callback for incoming messages."""
        self._on_message_callback = callback

    def subscribe_to_quotes(self, symbol: str) -> None:
        """Register a symbol for real-time quote streaming."""
        if symbol not in self._quote_symbols:
            self._quote_symbols.append(symbol)
            logger.info("Queued quote subscription for %s", symbol)

    def subscribe_to_option_chain(self, symbol: str, strike_proximity: int = 16) -> None:
        """Register a symbol for option-chain data."""
        if symbol not in self._option_chain_symbols:
            self._option_chain_symbols.append(symbol)
            logger.info(
                "Queued option-chain subscription for %s (proximity=%d)",
                symbol, strike_proximity,
            )

    def subscribe_to_market_depth_quotes(self, symbol: str) -> None:
        """Register a symbol for market-depth-quotes streaming.

        TradeStation HTTP streaming does not have a dedicated market-depth
        endpoint.  This method is a no-op stub — depth data is derived from
        the regular quote stream (Bid/Ask fields) and dispatched by
        ``_on_message`` with type="market_depth_quotes".
        """
        logger.debug("Market-depth-quotes subscription for %s (no-op stub)", symbol)

    def subscribe_to_market_depth_aggregates(self, symbol: str) -> None:
        """Register a symbol for aggregated market-depth streaming.

        TradeStation HTTP streaming does not have a dedicated market-depth
        endpoint.  This method is a no-op stub — depth data is derived from
        the regular quote stream and dispatched by ``_on_message`` with
        type="market_depth_agg".
        """
        logger.debug("Market-depth-aggregates subscription for %s (no-op stub)", symbol)

    async def stop(self) -> None:
        """Gracefully stop the client, cancel stream tasks, and close the session."""
        self._is_running = False
        # Cancel background stream tasks
        for task in self._stream_tasks:
            if not task.done():
                task.cancel()
        if self._stream_tasks:
            await asyncio.gather(*self._stream_tasks, return_exceptions=True)
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("TradeStationClient stopped.")

    # ------------------------------------------------------------------
    # Connection loop
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """
        Establish streaming connections.

        Spawns quote and option-chain streams as background tasks
        that run until stop() is called. Returns immediately.
        """
        self._is_running = True
        await self._refresh_token_if_needed()
        logger.info("Starting TradeStation HTTP-streaming connections…")

        self._stream_tasks: List[asyncio.Task] = []

        if self._quote_symbols:
            for sym in self._quote_symbols:
                self._stream_tasks.append(
                    asyncio.create_task(
                        self._stream_quotes_loop(sym),
                        name=f"QuoteStream-{sym}",
                    )
                )

        if self._option_chain_symbols:
            for sym in self._option_chain_symbols:
                self._stream_tasks.append(
                    asyncio.create_task(
                        self._fetch_option_chain_loop(sym),
                        name=f"OptionChain-{sym}",
                    )
                )

        # Track which symbol feeds the underlying price
        if self._option_chain_symbols:
            self._watched_symbol = self._option_chain_symbols[0]

        if not self._stream_tasks:
            logger.warning("No subscriptions registered.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def _refresh_token_if_needed(self) -> None:
        token = self.token_manager.get_access_token()
        if not token:
            raise ConnectionError("Could not retrieve access token from TokenManager.")
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def _dispatch(self, data: dict) -> None:
        """Dispatch message to callback."""
        if self._on_message_callback:
            try:
                self._on_message_callback(data)
            except Exception as exc:
                logger.error("Callback error: %s", exc)

    # ------------------------------------------------------------------
    # Quote Stream
    # ------------------------------------------------------------------

    async def _stream_quotes_loop(self, symbol: str) -> None:
        url = f"{self.base_url}/marketdata/stream/quotes/{symbol}"
        logger.info("[%s] Opening quote stream: %s", symbol, url)

        retry_delay = 1
        while self._is_running:
            try:
                async with self._session_lock:
                    await self._refresh_token_if_needed()

                session = await self._ensure_session()
                async with session.get(url, headers=self._headers) as resp:
                    if resp.status == 401:
                        logger.error("401 Unauthorized — token expired.")
                        async with self._session_lock:
                            await self._refresh_token_if_needed()
                        await asyncio.sleep(5)
                        continue
                    if resp.status == 404:
                        logger.error("404 Not Found — endpoint may have changed: %s", url)
                        break
                    resp.raise_for_status()

                    logger.info("[%s] Quote stream connected", symbol)
                    retry_delay = 1

                    async for line in resp.content:
                        if not self._is_running:
                            break
                        line_str = line.decode("utf-8", errors="replace").strip()
                        if not line_str:
                            continue
                        try:
                            data = json.loads(line_str)
                            # Feed underlying price from quotes stream
                            if self._watched_symbol and "Symbol" in data and data["Symbol"] == self._watched_symbol:
                                bid = data.get("Bid", 0)
                                if bid and float(bid) > 0:
                                    self._dispatch({"type": "underlying_update", "price": float(bid)})
                                else:
                                    last = data.get("Last", 0)
                                    if last and float(last) > 0:
                                        self._dispatch({"type": "underlying_update", "price": float(last)})
                            self._dispatch(data)
                        except json.JSONDecodeError:
                            logger.debug(f"NON-JSON LINE: {line_str}")
                            pass

            except aiohttp.ClientConnectorError as exc:
                logger.warning("[%s] Connection error: %s. Retrying in %ds…", symbol, exc, retry_delay)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)

            except aiohttp.ClientPayloadError as exc:
                logger.warning("[%s] Payload error: %s. Reconnecting…", symbol, exc)
                await asyncio.sleep(2)

            except asyncio.TimeoutError:
                logger.warning("[%s] Stream timeout. Reconnecting…", symbol)
                await asyncio.sleep(2)

            except Exception as exc:
                logger.error("[%s] Unexpected error: %s", symbol, exc)
                await asyncio.sleep(5)

    # ------------------------------------------------------------------
    # Option Chain
    # ------------------------------------------------------------------

    async def _fetch_option_chain_loop(self, symbol: str) -> None:
        url = f"{self.base_url}/marketdata/stream/options/chains/{symbol}"
        logger.info("[%s] Opening option-chain stream: %s", symbol, url)
        retry_delay = 1

        while self._is_running:
            try:
                async with self._session_lock:
                    await self._refresh_token_if_needed()

                session = await self._ensure_session()
                params = {"strikeProximity": 16}

                async with session.get(url, headers=self._headers, params=params) as resp:
                    if resp.status == 401:
                        logger.error("401 Unauthorized on option-chain for %s. Auth failure.", symbol)
                        self._option_chain_failed = True
                        break

                    if resp.status == 404:
                        logger.error(
                            "404 on option-chain for %s — market may be closed or symbol invalid. Failing fast.",
                            symbol,
                        )
                        self._option_chain_failed = True
                        break

                    resp.raise_for_status()
                    logger.info("[%s] Option-chain stream connected", symbol)
                    retry_delay = 1

                    msg_count = 0
                    async for line in resp.content:
                        if not self._is_running:
                            break
                        line_str = line.decode("utf-8", errors="replace").strip()
                        if not line_str:
                            continue
                        msg_count += 1
                        try:
                            raw = json.loads(line_str)
                            # Transform raw TradeStation option-chain JSON
                            # into per-contract option_update messages
                            contracts = self._extract_contracts(raw)
                            if contracts:
                                for contract in contracts:
                                    self._dispatch(contract)
                            else:
                                # Raw individual contract format — dispatch directly
                                self._dispatch(raw)
                        except json.JSONDecodeError:
                            pass

            except aiohttp.ClientConnectorError as exc:
                logger.warning("[%s] Option-chain connection error: %s. Retrying in %ds…", symbol, exc, retry_delay)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)

            except asyncio.TimeoutError:
                logger.warning("[%s] Option-chain timeout. Reconnecting…", symbol)
                await asyncio.sleep(2)

            except Exception as exc:
                logger.error("[%s] Option-chain error: %s", symbol, exc, exc_info=True)
                if "JSON" in type(exc).__name__ or "decode" in str(exc).lower():
                    logger.error("[%s] Unrecoverable option-chain error — failing fast.", symbol)
                    self._option_chain_failed = True
                    break
                await asyncio.sleep(5)

    @staticmethod
    def _extract_contracts(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse a TradeStation option-chain response into option_update messages.

        Expected structure:
        {
          "optionChain": {
            "underlying": { "lastPrice": 195.5 },
            "calls": [ { "symbol": "...", "strike": 190, "gamma": 0.02,
                         "openInterest": 500, ... }, ... ],
            "puts":  [ { ... }, ... ]
          }
        }
        """
        contracts: List[Dict[str, Any]] = []

        chain = data.get("optionChain") or data.get("option_chain") or data
        if not isinstance(chain, dict):
            logger.warning("Option chain response is not a dict — skipping")
            return contracts

        # Extract underlying price and emit as a separate message
        underlying = chain.get("underlying", {})
        price = underlying.get("lastPrice") or underlying.get("last") or 0.0
        if price and price > 0:
            contracts.append({
                "type": "underlying_update",
                "price": price,
            })

        for side_key in ("calls", "puts"):
            leg_list = chain.get(side_key, [])
            if not isinstance(leg_list, list):
                continue
            for leg in leg_list:
                if not isinstance(leg, dict):
                    continue
                strike = leg.get("strike", 0)
                gamma = leg.get("gamma", 0)
                oi = leg.get("openInterest", leg.get("open_interest", 0))
                symbol = leg.get("symbol", "")

                if not symbol:
                    continue

                side_label = "call" if side_key == "calls" else "put"

                contracts.append({
                    "type": "option_update",
                    "symbol": symbol,
                    "strike": strike,
                    "gamma": gamma,
                    "open_interest": oi,
                    "underlying_price": price,
                    "side": side_label,
                })

        return contracts
