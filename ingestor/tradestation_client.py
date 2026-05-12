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
        self._quote_session: aiohttp.ClientSession | None = None
        self._option_chain_session: aiohttp.ClientSession | None = None
        self._depth_quote_session: aiohttp.ClientSession | None = None
        self._depth_agg_session: aiohttp.ClientSession | None = None
        self._on_message_callback: Optional[Callable[[dict], Any]] = None
        self._is_running = False
        self._headers: Dict[str, str] = {}
        self._quote_symbols: List[str] = []
        self._option_chain_symbols: List[str] = []
        self._depth_quote_symbols: List[str] = []
        self._depth_agg_symbols: List[str] = []
        self._option_chain_failed = False
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

        TradeStation endpoint: /v3/marketdata/stream/marketdepth/quotes/{symbol}
        Returns per-exchange order book (Level 2 / TotalView).
        """
        if symbol not in self._depth_quote_symbols:
            self._depth_quote_symbols.append(symbol)
            logger.info("Queued market-depth-quotes subscription for %s", symbol)

    def subscribe_to_market_depth_aggregates(self, symbol: str) -> None:
        """Register a symbol for aggregated market-depth streaming.

        TradeStation endpoint: /v3/marketdata/stream/marketdepth/aggregates/{symbol}
        Returns aggregated depth per price level.
        """
        if symbol not in self._depth_agg_symbols:
            self._depth_agg_symbols.append(symbol)
            logger.info("Queued market-depth-aggregates subscription for %s", symbol)

    async def stop(self) -> None:
        """Gracefully stop the client, cancel stream tasks, and close the session."""
        self._is_running = False
        # Cancel background stream tasks
        for task in self._stream_tasks:
            if not task.done():
                task.cancel()
        if self._stream_tasks:
            await asyncio.gather(*self._stream_tasks, return_exceptions=True)
        for attr in ("_quote_session", "_option_chain_session", "_depth_quote_session", "_depth_agg_session"):
            session = getattr(self, attr)
            if session and not session.closed:
                await session.close()
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

        if self._depth_quote_symbols:
            for sym in self._depth_quote_symbols:
                self._stream_tasks.append(
                    asyncio.create_task(
                        self._stream_depth_quotes_loop(sym),
                        name=f"DepthQuoteStream-{sym}",
                    )
                )

        if self._depth_agg_symbols:
            for sym in self._depth_agg_symbols:
                self._stream_tasks.append(
                    asyncio.create_task(
                        self._stream_depth_agg_loop(sym),
                        name=f"DepthAggStream-{sym}",
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

    async def _ensure_quote_session(self) -> aiohttp.ClientSession:
        if self._quote_session is None or self._quote_session.closed:
            timeout = aiohttp.ClientTimeout(sock_read=60)
            self._quote_session = aiohttp.ClientSession(timeout=timeout)
        return self._quote_session

    async def _ensure_option_chain_session(self) -> aiohttp.ClientSession:
        if self._option_chain_session is None or self._option_chain_session.closed:
            timeout = aiohttp.ClientTimeout(sock_read=60)
            self._option_chain_session = aiohttp.ClientSession(timeout=timeout)
        return self._option_chain_session

    async def _ensure_depth_quote_session(self) -> aiohttp.ClientSession:
        if self._depth_quote_session is None or self._depth_quote_session.closed:
            timeout = aiohttp.ClientTimeout(sock_read=60)
            self._depth_quote_session = aiohttp.ClientSession(timeout=timeout)
        return self._depth_quote_session

    async def _ensure_depth_agg_session(self) -> aiohttp.ClientSession:
        if self._depth_agg_session is None or self._depth_agg_session.closed:
            timeout = aiohttp.ClientTimeout(sock_read=60)
            self._depth_agg_session = aiohttp.ClientSession(timeout=timeout)
        return self._depth_agg_session

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
                await self._refresh_token_if_needed()

                session = await self._ensure_quote_session()
                async with session.get(url, headers=self._headers) as resp:
                    if resp.status == 401:
                        logger.error("401 Unauthorized — token expired.")
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
                await self._refresh_token_if_needed()

                session = await self._ensure_option_chain_session()
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

    # ------------------------------------------------------------------
    # Market Depth Quotes Stream
    # ------------------------------------------------------------------

    async def _stream_depth_quotes_loop(self, symbol: str) -> None:
        """Stream market depth quotes (per-exchange TotalView data).

        Endpoint: /v3/marketdata/stream/marketdepth/quotes/{symbol}
        Returns per-exchange order book with Price, Size, OrderCount, Name.
        """
        url = f"{self.base_url}/marketdata/stream/marketdepth/quotes/{symbol}"
        params = {"maxlevels": 20}
        logger.info("[%s] Opening depth-quotes stream: %s", symbol, url)

        retry_delay = 1
        while self._is_running:
            try:
                await self._refresh_token_if_needed()

                session = await self._ensure_depth_quote_session()
                async with session.get(url, headers=self._headers, params=params) as resp:
                    if resp.status == 401:
                        logger.error("401 Unauthorized on depth-quotes for %s. Refreshing token.", symbol)
                        await self._refresh_token_if_needed()
                        await asyncio.sleep(5)
                        continue
                    if resp.status == 404:
                        logger.error(
                            "404 on depth-quotes for %s — symbol invalid or market closed.",
                            symbol,
                        )
                        break
                    resp.raise_for_status()

                    logger.info("[%s] Depth-quotes stream connected", symbol)
                    retry_delay = 1

                    async for line in resp.content:
                        if not self._is_running:
                            break
                        line_str = line.decode("utf-8", errors="replace").strip()
                        if not line_str:
                            continue
                        try:
                            data = json.loads(line_str)
                            msg = self._normalize_depth_quotes(data)
                            self._dispatch(msg)
                        except json.JSONDecodeError:
                            pass

            except aiohttp.ClientResponseError as exc:
                if exc.status == 429:
                    backoff = min(retry_delay * 2, 120)
                    logger.warning("[%s] 429 on depth-quotes — backing off %.1fs", symbol, backoff)
                    await asyncio.sleep(backoff)
                    retry_delay = min(retry_delay * 2, 120)
                elif exc.status == 401:
                    logger.warning("[%s] 401 on depth-quotes — refreshing token", symbol)
                    await asyncio.sleep(5)
                else:
                    logger.warning("[%s] HTTP error on depth-quotes: %s", symbol, exc)
                    await asyncio.sleep(5)

            except aiohttp.ClientConnectorError as exc:
                logger.warning("[%s] Connection error on depth-quotes: %s. Retrying in %ds…", symbol, exc, retry_delay)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)

            except asyncio.TimeoutError:
                logger.warning("[%s] Depth-quotes timeout. Reconnecting…", symbol)
                await asyncio.sleep(2)

            except Exception as exc:
                logger.error("[%s] Unexpected error on depth-quotes: %s", symbol, exc, exc_info=True)
                await asyncio.sleep(5)

    @staticmethod
    def _normalize_depth_quotes(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw depth-quotes data to match main.py expectations.

        Raw API fields: Price, Size, OrderCount, Name (exchange), TimeStamp
        Main.py expects: Price, Size, OrderCount, TimeStamp, exchange, bid_exchanges, ask_exchanges

        The TradeStation depth-quotes API returns one entry per exchange per price level.
        main.py's _on_message expects each entry to have:
          - exchange: the exchange name (string)
          - bid_exchanges: dict of venue→size for this bid entry (for VSI/ESI computation)
          - ask_exchanges: dict of venue→size for this ask entry

        We map Name→exchange and build bid_exchanges/ask_exchanges from the full
        Bids/Asks arrays so main.py's exchange flow logic works correctly.
        """
        # Build exchange→size maps from the full bid/ask arrays
        # (each entry is one exchange, so we aggregate by exchange name)
        bid_exchange_map: Dict[str, int] = {}
        for b in data.get("Bids", []):
            venue = b.get("Name", "")
            size = int(b.get("Size", 0))
            if venue:
                bid_exchange_map[venue] = bid_exchange_map.get(venue, 0) + size

        ask_exchange_map: Dict[str, int] = {}
        for a in data.get("Asks", []):
            venue = a.get("Name", "")
            size = int(a.get("Size", 0))
            if venue:
                ask_exchange_map[venue] = ask_exchange_map.get(venue, 0) + size

        bids = []
        for b in data.get("Bids", []):
            bids.append({
                "Price": b.get("Price", 0),
                "Size": b.get("Size", 0),
                "OrderCount": b.get("OrderCount", 0),
                "TimeStamp": b.get("TimeStamp", ""),
                "exchange": b.get("Name", ""),
                "num_participants": b.get("OrderCount", 0),
                "bid_exchanges": bid_exchange_map,
                "ask_exchanges": ask_exchange_map,
            })
        asks = []
        for a in data.get("Asks", []):
            asks.append({
                "Price": a.get("Price", 0),
                "Size": a.get("Size", 0),
                "OrderCount": a.get("OrderCount", 0),
                "TimeStamp": a.get("TimeStamp", ""),
                "exchange": a.get("Name", ""),
                "num_participants": a.get("OrderCount", 0),
                "bid_exchanges": bid_exchange_map,
                "ask_exchanges": ask_exchange_map,
            })
        return {
            "type": "market_depth_quotes",
            "symbol": data.get("symbol", ""),
            "Bids": bids,
            "Asks": asks,
        }

    # ------------------------------------------------------------------
    # Market Depth Aggregates Stream
    # ------------------------------------------------------------------

    async def _stream_depth_agg_loop(self, symbol: str) -> None:
        """Stream market depth aggregates (total size per level).

        Endpoint: /v3/marketdata/stream/marketdepth/aggregates/{symbol}
        Returns aggregated depth with TotalSize, NumParticipants, etc.
        """
        url = f"{self.base_url}/marketdata/stream/marketdepth/aggregates/{symbol}"
        params = {"maxlevels": 20}
        logger.info("[%s] Opening depth-aggregates stream: %s", symbol, url)

        retry_delay = 1
        while self._is_running:
            try:
                await self._refresh_token_if_needed()

                session = await self._ensure_depth_agg_session()
                async with session.get(url, headers=self._headers, params=params) as resp:
                    if resp.status == 401:
                        logger.error("401 Unauthorized on depth-aggregates for %s. Refreshing token.", symbol)
                        await self._refresh_token_if_needed()
                        await asyncio.sleep(5)
                        continue
                    if resp.status == 404:
                        logger.error(
                            "404 on depth-aggregates for %s — symbol invalid or market closed.",
                            symbol,
                        )
                        break
                    resp.raise_for_status()

                    logger.info("[%s] Depth-aggregates stream connected", symbol)
                    retry_delay = 1

                    async for line in resp.content:
                        if not self._is_running:
                            break
                        line_str = line.decode("utf-8", errors="replace").strip()
                        if not line_str:
                            continue
                        try:
                            data = json.loads(line_str)
                            msg = self._normalize_depth_agg(data)
                            self._dispatch(msg)
                        except json.JSONDecodeError:
                            pass

            except aiohttp.ClientResponseError as exc:
                if exc.status == 429:
                    backoff = min(retry_delay * 2, 120)
                    logger.warning("[%s] 429 on depth-aggregates — backing off %.1fs", symbol, backoff)
                    await asyncio.sleep(backoff)
                    retry_delay = min(retry_delay * 2, 120)
                elif exc.status == 401:
                    logger.warning("[%s] 401 on depth-aggregates — refreshing token", symbol)
                    await asyncio.sleep(5)
                else:
                    logger.warning("[%s] HTTP error on depth-aggregates: %s", symbol, exc)
                    await asyncio.sleep(5)

            except aiohttp.ClientConnectorError as exc:
                logger.warning("[%s] Connection error on depth-aggregates: %s. Retrying in %ds…", symbol, exc, retry_delay)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)

            except asyncio.TimeoutError:
                logger.warning("[%s] Depth-aggregates timeout. Reconnecting…", symbol)
                await asyncio.sleep(2)

            except Exception as exc:
                logger.error("[%s] Unexpected error on depth-aggregates: %s", symbol, exc, exc_info=True)
                await asyncio.sleep(5)

    @staticmethod
    def _normalize_depth_agg(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw depth-aggregate data to match main.py expectations.

        Raw API fields: Price, TotalSize, BiggestSize, SmallestSize,
                        NumParticipants, TotalOrderCount, EarliestTime, LatestTime
        Main.py expects: TotalSize, NumParticipants, Price (PascalCase keys).
        We normalize to lowercase 'price' for main.py's float() calls but keep
        PascalCase for the fields main.py reads directly.
        """
        bids = []
        for b in data.get("Bids", []):
            bids.append({
                "Price": b.get("Price", 0),
                "TotalSize": b.get("TotalSize", 0),
                "BiggestSize": b.get("BiggestSize", 0),
                "SmallestSize": b.get("SmallestSize", 0),
                "NumParticipants": b.get("NumParticipants", 0),
                "TotalOrderCount": b.get("TotalOrderCount", 0),
                "EarliestTime": b.get("EarliestTime", ""),
                "LatestTime": b.get("LatestTime", ""),
            })
        asks = []
        for a in data.get("Asks", []):
            asks.append({
                "Price": a.get("Price", 0),
                "TotalSize": a.get("TotalSize", 0),
                "BiggestSize": a.get("BiggestSize", 0),
                "SmallestSize": a.get("SmallestSize", 0),
                "NumParticipants": a.get("NumParticipants", 0),
                "TotalOrderCount": a.get("TotalOrderCount", 0),
                "EarliestTime": a.get("EarliestTime", ""),
                "LatestTime": a.get("LatestTime", ""),
            })
        return {
            "type": "market_depth_agg",
            "symbol": data.get("symbol", ""),
            "Bids": bids,
            "Asks": asks,
        }

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
