"""
orb_probe.py — Collect all 4 TradeStation streams for 10 minutes simultaneously.

Streams:
    1. Quotes:           GET /v3/marketdata/stream/quotes/{symbol}
    2. Option Chain:     GET /v3/marketdata/stream/options/chains/{symbol}
    3. Depth Quotes:     GET /v3/marketdata/stream/marketdepth/quotes/{symbol}
    4. Depth Aggregates: GET /v3/marketdata/stream/marketdepth/aggregates/{symbol}

All streams run concurrently, each writing to its own JSONL file.
Every line is prefixed with a UTC timestamp for alignment.

Usage:
    python3 orb_probe.py TSLA [duration_seconds]
    python3 orb_probe.py TSLA 600   # 10 minutes (default)

Output files saved to ~/projects/syngex/data/level2/
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import aiohttp

TOKEN_PATH = Path.home() / "projects/tfresh2/token.json"


def load_token(f: Path, data: str) -> str:
    token = json.loads(data)
    access_token = token.get("access_token")
    if not access_token:
        raise ValueError("No access_token in token.json")
    return access_token


def utc_now() -> str:
    """Return current time as UTC ISO string. Always UTC — display layer handles timezone."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def ts_prefix(data: Dict) -> Dict:
    """Add a UTC timestamp to a data dict for alignment."""
    data["_probe_ts"] = utc_now()
    return data


def write_line(path: Path, data: Dict) -> None:
    """Append a JSON line to a file, creating it if needed."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")


def _parse_quote_line(raw: Dict) -> Dict:
    """Transform a raw TradeStation quote into a clean parsed object."""
    parsed = {
        "type": "quote_update",
        "symbol": raw.get("Symbol", ""),
        "last": _safe_float(raw.get("Last")),
        "bid": _safe_float(raw.get("Bid")),
        "ask": _safe_float(raw.get("Ask")),
        "bid_size": raw.get("BidSize", 0),
        "ask_size": raw.get("AskSize", 0),
        "volume": raw.get("Volume", 0),
        "previous_volume": raw.get("PreviousVolume", 0),
        "open": _safe_float(raw.get("Open"), 0.0),
        "high": _safe_float(raw.get("High"), 0.0),
        "low": _safe_float(raw.get("Low"), 0.0),
        "close": _safe_float(raw.get("Close")),
        "previous_close": _safe_float(raw.get("PreviousClose")),
        "net_change": _safe_float(raw.get("NetChange")),
        "net_change_pct": _safe_float(raw.get("NetChangePct")),
        "vwap": _safe_float(raw.get("VWAP"), 0.0),
    }
    last_size = raw.get("LastSize", 0)
    last_venue = raw.get("LastVenue", "")
    five2w_high = _safe_float(raw.get("High52Week"), 0.0)
    five2w_low = _safe_float(raw.get("Low52Week"), 0.0)
    market_flags = raw.get("MarketFlags")
    is_delayed = False
    if isinstance(market_flags, dict):
        is_delayed = market_flags.get("IsDelayed", False)
    is_halted = False
    if isinstance(market_flags, dict):
        is_halted = market_flags.get("IsHalted", False)
    parsed.update({
        "last_size": last_size,
        "last_venue": last_venue,
        "52w_high": five2w_high,
        "52w_low": five2w_low,
        "is_delayed": is_delayed,
        "is_halted": is_halted,
    })
    return parsed


async def collect_quotes(session, symbol, headers, raw_path, parsed_path, duration_seconds):
    """Stream quotes and write to both raw and parsed JSONL files."""
    url = f"https://api.tradestation.com/v3/marketdata/stream/quotes/{symbol}"
    log.info("[%s] Opening quote stream: %s", symbol, url)
    count = 0
    retry_delay = 1

    while duration_seconds > 0:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 401:
                    log.warning("401 on quotes — refreshing token and retrying…")
                    await asyncio.sleep(5)
                    headers["Authorization"] = f"Bearer {load_token(TOKEN_PATH, TOKEN_PATH.read_text())}"
                    continue
                if resp.status == 404:
                    log.error("404 on quotes — endpoint may have changed")
                    await asyncio.sleep(5)
                    continue
                resp.raise_for_status()
                log.info("[%s] Quote stream connected", symbol)
                deadline = time.monotonic() + duration_seconds
                async for line in resp.content:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    try:
                        data = json.loads(line_str)
                    except json.JSONDecodeError:
                        continue
                    raw_data = ts_prefix(dict(data))
                    write_line(raw_path, raw_data)
                    if isinstance(data, dict):
                        parsed = _parse_quote_line(data)
                        parsed["_probe_ts"] = raw_data["_probe_ts"]
                        write_line(parsed_path, parsed)
                    else:
                        write_line(parsed_path, raw_data)
                    count += 1
                    duration_seconds = max(0, duration_seconds - 1)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                backoff = min(retry_delay * 2, 120)
                log.warning("429 on quotes — backing off %.1fs", backoff)
                await asyncio.sleep(backoff)
                retry_delay = min(retry_delay * 2, 120)
            elif e.status == 401:
                await asyncio.sleep(5)
                headers["Authorization"] = f"Bearer {load_token(TOKEN_PATH, TOKEN_PATH.read_text())}"
            else:
                log.error("HTTP error on quotes: %s", e)
                await asyncio.sleep(5)
        except aiohttp.ClientConnectorError as e:
            log.warning("Connection error on quotes: %s. Retrying in %ds…", e, retry_delay)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except asyncio.TimeoutError:
            log.warning("Timeout on quotes. Reconnecting…")
            await asyncio.sleep(2)
        except Exception as e:
            log.error("Unexpected error on quotes: %s", e, exc_info=True)
            await asyncio.sleep(5)

    log.info("[%s] Quote stream done — %d lines", symbol, count)
    return count


def _parse_option_symbol(sym):
    """Parse an option symbol string into (root, side, strike).

    Formats:
        "TSLA 260511C465"  → ("TSLA", "call", 465.0)
        "SPY  260116P0500"  → ("SPY", "put", 500.0)

    The suffix is: YYMMDD + C/P + 4-5 digit strike (decimal implied).
    """
    parts = sym.split()
    if len(parts) < 2:
        return ("unknown", "", 0.0)
    root = parts[0]
    suffix = parts[-1]
    if len(suffix) < 8:
        return (root, "", 0.0)
    side_char = suffix[6]
    side = "call" if side_char.upper() == "C" else "put"
    strike_str = suffix[7:]
    strike = float(strike_str) if strike_str else 0.0
    return (root, side, strike)


def _safe_float(val, default=0.0):
    """Safely convert a value to float, returning default on failure."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _parse_option_chain_line(raw: Dict) -> Dict:
    """Transform a raw TradeStation option-chain message into a clean parsed object.

    Handles both SIM/wrapped format (Legs as list of dicts) and LIVE flat format
    (Legs as list of strings). Extracts greeks, pricing, probabilities.
    """
    legs = raw.get("Legs", [])
    parsed_sym = ""
    strike = 0.0
    side = ""

    if isinstance(legs, list) and legs:
        leg = legs[0]
        if isinstance(leg, dict):
            parsed_sym = leg.get("Symbol", "")
            strike = _safe_float(leg.get("StrikePrice"), 0.0)
            option_type = leg.get("OptionType", "")
            if option_type:
                side = "call" if option_type.upper() in ("CALL", "C") else "put"
        elif isinstance(leg, str):
            parsed_sym, side, strike = _parse_option_symbol(leg.strip())

    if not side:
        raw_side = raw.get("Side", "")
        if raw_side:
            side = "call" if raw_side.upper() in ("CALL", "C") else "put"

    if not strike:
        strikes = raw.get("Strikes", [])
        if isinstance(strikes, list) and strikes:
            strike = _safe_float(strikes[0], 0.0)

    if not strike and parsed_sym:
        _, _, fallback_strike = _parse_option_symbol(parsed_sym)
        strike = fallback_strike

    if not parsed_sym:
        parsed_sym = raw.get("Symbol", "")

    bid = _safe_float(raw.get("Bid"))
    ask = _safe_float(raw.get("Ask"))
    last = _safe_float(raw.get("Last"))
    iv = _safe_float(raw.get("ImpliedVolatility"))
    gamma = _safe_float(raw.get("Gamma"))
    delta = _safe_float(raw.get("Delta"))
    theta = _safe_float(raw.get("Theta"))
    vega = _safe_float(raw.get("Vega"))
    rho = _safe_float(raw.get("Rho"))
    intrinsic = _safe_float(raw.get("IntrinsicValue"))
    extrinsic = _safe_float(raw.get("ExtrinsicValue"))
    theo = _safe_float(raw.get("TheoreticalValue"))
    theo_iv = _safe_float(raw.get("TheoreticalValue_IV"))
    mid = _safe_float(raw.get("Mid"))

    oi = raw.get("DailyOpenInterest")
    if oi is None:
        oi = 0

    volume = raw.get("Volume")
    if volume is None:
        volume = 0

    prob_itm = _safe_float(raw.get("ProbabilityITM"))
    prob_otm = _safe_float(raw.get("ProbabilityOTM"))
    prob_be = _safe_float(raw.get("ProbabilityBE"))
    prob_itm_iv = _safe_float(raw.get("ProbabilityITM_IV"))
    prob_otm_iv = _safe_float(raw.get("ProbabilityOTM_IV"))
    prob_be_iv = _safe_float(raw.get("ProbabilityBE_IV"))

    bid_size = raw.get("BidSize")
    if bid_size is None:
        bid_size = 0

    ask_size = raw.get("AskSize")
    if ask_size is None:
        ask_size = 0

    expiration = ""
    if isinstance(legs, list) and legs:
        leg = legs[0]
        if isinstance(leg, dict):
            expiration = leg.get("Expiration", "")

    parsed = {
        "type": "option_update",
        "symbol": parsed_sym,
        "strike": strike,
        "side": side,
        "bid": bid,
        "ask": ask,
        "last": last,
        "mid": mid,
        "bid_size": bid_size,
        "ask_size": ask_size,
        "volume": volume,
        "open_interest": oi,
        "iv": iv,
        "delta": delta,
        "gamma": gamma,
        "theta": theta,
        "vega": vega,
        "rho": rho,
        "intrinsic_value": intrinsic,
        "extrinsic_value": extrinsic,
        "theoretical_value": theo,
        "theoretical_value_iv": theo_iv,
        "probability_itm": prob_itm,
        "probability_otm": prob_otm,
        "probability_be": prob_be,
        "probability_itm_iv": prob_itm_iv,
        "probability_otm_iv": prob_otm_iv,
        "probability_be_iv": prob_be_iv,
        "close": _safe_float(raw.get("Close")),
        "net_change": _safe_float(raw.get("NetChange")),
        "net_change_pct": _safe_float(raw.get("NetChangePct")),
        "52w_high": _safe_float(raw.get("High52Week"), 0.0),
        "52w_low": _safe_float(raw.get("Low52Week"), 0.0),
        "expiration": expiration,
    }

    return parsed


async def collect_option_chain(session, symbol, headers, raw_path, parsed_path, duration_seconds):
    """Stream option chain and write to both raw and parsed JSONL files.

    Raw: each line + _probe_ts (keep ALL fields, no transformation).
    Parsed: clean option_update objects with normalized fields.
    """
    url = f"https://api.tradestation.com/v3/marketdata/stream/options/chains/{symbol}"
    params = {"strikeProximity": 16}
    log.info("[%s] Opening option-chain stream: %s", symbol, url)
    count = 0
    retry_delay = 1

    while duration_seconds > 0:
        try:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 401:
                    log.error("401 on option-chain — auth failure")
                    await asyncio.sleep(5)
                    continue
                if resp.status == 404:
                    log.error("404 on option-chain — market closed or symbol invalid")
                    await asyncio.sleep(5)
                    continue
                resp.raise_for_status()
                log.info("[%s] Option-chain stream connected", symbol)
                deadline = time.monotonic() + duration_seconds
                async for line in resp.content:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    try:
                        data = json.loads(line_str)
                    except json.JSONDecodeError:
                        continue
                    raw_data = ts_prefix(dict(data))
                    write_line(raw_path, raw_data)
                    if isinstance(data, dict):
                        parsed = _parse_option_chain_line(data)
                        parsed["_probe_ts"] = raw_data["_probe_ts"]
                        write_line(parsed_path, parsed)
                    else:
                        write_line(parsed_path, raw_data)
                    count += 1
                    duration_seconds = max(0, duration_seconds - 1)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                backoff = min(retry_delay * 2, 120)
                log.warning("429 on option-chain — backing off %.1fs", backoff)
                await asyncio.sleep(backoff)
                retry_delay = min(retry_delay * 2, 120)
            elif e.status == 401:
                await asyncio.sleep(5)
            else:
                log.error("HTTP error on option-chain: %s", e)
                await asyncio.sleep(5)
        except aiohttp.ClientConnectorError as e:
            log.warning("Connection error on option-chain: %s. Retrying in %ds…", e, retry_delay)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except asyncio.TimeoutError:
            log.warning("Timeout on option-chain. Reconnecting…")
            await asyncio.sleep(2)
        except Exception as e:
            log.error("Unexpected error on option-chain: %s", e, exc_info=True)
            await asyncio.sleep(5)

    log.info("[%s] Option-chain stream done — %d lines", symbol, count)
    return count


def _parse_depth_entry(entry) -> Dict:
    """Parse a single bid/ask level entry from depth data."""
    size = entry.get("Size", 0)
    if isinstance(size, str):
        try:
            size = int(size)
        except (ValueError, TypeError):
            size = 0
    return {
        "price": _safe_float(entry.get("Price")),
        "size": size,
        "order_count": entry.get("OrderCount", 0),
        "timestamp": entry.get("TimeStamp", ""),
        "exchange": entry.get("Name", ""),
    }


def _parse_depth_line(raw: Dict) -> Dict:
    """Transform raw market depth quotes into a clean parsed object."""
    bids = [_parse_depth_entry(b) for b in raw.get("Bids", [])]
    asks = [_parse_depth_entry(a) for a in raw.get("Asks", [])]

    best_bid = bids[0]["price"] if bids else 0.0
    best_ask = asks[0]["price"] if asks else 0.0

    mid_price = (best_bid + best_ask) / 2 if best_bid > 0 and best_ask > 0 else 0.0
    spread = (best_ask - best_bid) if best_ask > 0 and best_bid > 0 else 0.0

    total_bid_size = sum(b["size"] for b in bids)
    total_ask_size = sum(a["size"] for a in asks)

    bid_exchanges = {}
    for b in bids:
        ex = b["exchange"]
        if ex:
            bid_exchanges[ex] = bid_exchanges.get(ex, 0) + b["size"]

    ask_exchanges = {}
    for a in asks:
        ex = a["exchange"]
        if ex:
            ask_exchanges[ex] = ask_exchanges.get(ex, 0) + a["size"]

    return {
        "type": "market_depth_quotes",
        "symbol": raw.get("symbol", ""),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid_price": mid_price,
        "spread": spread,
        "total_bid_size": total_bid_size,
        "total_ask_size": total_ask_size,
        "bid_levels": len(bids),
        "ask_levels": len(asks),
        "bid_exchanges": bid_exchanges,
        "ask_exchanges": ask_exchanges,
        "bids": bids,
        "asks": asks,
    }


async def collect_market_depth_quotes(session, symbol, headers, raw_path, parsed_path, duration_seconds):
    """Stream market depth quotes (per-participant) and write to both raw and parsed JSONL.

    Raw: each line + _probe_ts (no transformation).
    Parsed: clean market_depth_quotes objects with computed metrics.
    """
    url = f"https://api.tradestation.com/v3/marketdata/stream/marketdepth/quotes/{symbol}"
    params = {"maxlevels": 20}
    log.info("[%s] Opening market depth quotes stream: %s", symbol, url)
    count = 0
    retry_delay = 1

    while duration_seconds > 0:
        try:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 401:
                    log.warning("401 on depth quotes — refreshing token…")
                    await asyncio.sleep(5)
                    continue
                if resp.status == 404:
                    log.error("404 on depth quotes — symbol invalid or market closed")
                    await asyncio.sleep(5)
                    continue
                resp.raise_for_status()
                log.info("[%s] Market depth quotes stream connected", symbol)
                deadline = time.monotonic() + duration_seconds
                async for line in resp.content:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    try:
                        data = json.loads(line_str)
                    except json.JSONDecodeError:
                        continue
                    raw_data = ts_prefix(dict(data))
                    write_line(raw_path, raw_data)
                    if isinstance(data, dict):
                        parsed = _parse_depth_line(data)
                        parsed["_probe_ts"] = raw_data["_probe_ts"]
                        write_line(parsed_path, parsed)
                    else:
                        write_line(parsed_path, raw_data)
                    count += 1
                    duration_seconds = max(0, duration_seconds - 1)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                backoff = min(retry_delay * 2, 120)
                log.warning("429 on depth quotes — backing off %.1fs", backoff)
                await asyncio.sleep(backoff)
                retry_delay = min(retry_delay * 2, 120)
            elif e.status == 401:
                await asyncio.sleep(5)
            else:
                log.error("HTTP error on depth quotes: %s", e)
                await asyncio.sleep(5)
        except aiohttp.ClientConnectorError as e:
            log.warning("Connection error on depth quotes: %s. Retrying in %ds…", e, retry_delay)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except asyncio.TimeoutError:
            log.warning("Timeout on depth quotes. Reconnecting…")
            await asyncio.sleep(2)
        except Exception as e:
            log.error("Unexpected error on depth quotes: %s", e, exc_info=True)
            await asyncio.sleep(5)

    log.info("[%s] Depth quotes stream done — %d lines", symbol, count)
    return count


def _safe_int(val, default=0):
    """Safely convert a value to int, returning default on failure."""
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _parse_agg_entry(entry) -> Dict:
    """Parse a single aggregated bid/ask level."""
    return {
        "price": _safe_float(entry.get("Price")),
        "total_size": _safe_int(entry.get("TotalSize"), 0),
        "biggest_size": _safe_int(entry.get("BiggestSize"), 0),
        "smallest_size": _safe_int(entry.get("SmallestSize"), 0),
        "num_participants": _safe_int(entry.get("NumParticipants"), 0),
        "total_order_count": _safe_int(entry.get("TotalOrderCount"), 0),
        "earliest_time": entry.get("EarliestTime", ""),
        "latest_time": entry.get("LatestTime", ""),
    }


def _parse_depth_agg_line(raw: Dict) -> Dict:
    """Transform raw market depth aggregates into a clean parsed object."""
    bids = [_parse_agg_entry(b) for b in raw.get("Bids", [])]
    asks = [_parse_agg_entry(a) for a in raw.get("Asks", [])]

    best_bid = bids[0]["price"] if bids else 0.0
    best_ask = asks[0]["price"] if asks else 0.0

    mid_price = (best_bid + best_ask) / 2 if best_bid > 0 and best_ask > 0 else 0.0
    spread = (best_ask - best_bid) if best_ask > 0 and best_bid > 0 else 0.0

    total_bid_size = sum(b["total_size"] for b in bids)
    total_ask_size = sum(a["total_size"] for a in asks)

    bid_avg_participants = sum(b["num_participants"] for b in bids) / len(bids) if bids else 0
    ask_avg_participants = sum(a["num_participants"] for a in asks) / len(asks) if asks else 0

    bid_max_participants = max((b["num_participants"] for b in bids), default=0)
    ask_max_participants = max((a["num_participants"] for a in asks), default=0)

    return {
        "type": "market_depth_agg",
        "symbol": raw.get("symbol", ""),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid_price": mid_price,
        "spread": spread,
        "total_bid_size": total_bid_size,
        "total_ask_size": total_ask_size,
        "bid_levels": len(bids),
        "ask_levels": len(asks),
        "bid_avg_participants": bid_avg_participants,
        "ask_avg_participants": ask_avg_participants,
        "bid_max_participants": bid_max_participants,
        "ask_max_participants": ask_max_participants,
        "bids": bids,
        "asks": asks,
    }


async def collect_market_depth_agg(session, symbol, headers, raw_path, parsed_path, duration_seconds):
    """Stream market depth aggregates and write to both raw and parsed JSONL.

    Raw: each line + _probe_ts (no transformation).
    Parsed: clean market_depth_agg objects with computed metrics.
    """
    url = f"https://api.tradestation.com/v3/marketdata/stream/marketdepth/aggregates/{symbol}"
    params = {"maxlevels": 20}
    log.info("[%s] Opening market depth aggregates stream: %s", symbol, url)
    count = 0
    retry_delay = 1

    while duration_seconds > 0:
        try:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 401:
                    log.warning("401 on depth agg — refreshing token…")
                    await asyncio.sleep(5)
                    continue
                if resp.status == 404:
                    log.error("404 on depth agg — symbol invalid or market closed")
                    await asyncio.sleep(5)
                    continue
                resp.raise_for_status()
                log.info("[%s] Market depth aggregates stream connected", symbol)
                deadline = time.monotonic() + duration_seconds
                async for line in resp.content:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    try:
                        data = json.loads(line_str)
                    except json.JSONDecodeError:
                        continue
                    raw_data = ts_prefix(dict(data))
                    write_line(raw_path, raw_data)
                    if isinstance(data, dict):
                        parsed = _parse_depth_agg_line(data)
                        parsed["_probe_ts"] = raw_data["_probe_ts"]
                        write_line(parsed_path, parsed)
                    else:
                        write_line(parsed_path, raw_data)
                    count += 1
                    duration_seconds = max(0, duration_seconds - 1)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                backoff = min(retry_delay * 2, 120)
                log.warning("429 on depth agg — backing off %.1fs", backoff)
                await asyncio.sleep(backoff)
                retry_delay = min(retry_delay * 2, 120)
            elif e.status == 401:
                await asyncio.sleep(5)
            else:
                log.error("HTTP error on depth agg: %s", e)
                await asyncio.sleep(5)
        except aiohttp.ClientConnectorError as e:
            log.warning("Connection error on depth agg: %s. Retrying in %ds…", e, retry_delay)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except asyncio.TimeoutError:
            log.warning("Timeout on depth agg. Reconnecting…")
            await asyncio.sleep(2)
        except Exception as e:
            log.error("Unexpected error on depth agg: %s", e, exc_info=True)
            await asyncio.sleep(5)

    log.info("[%s] Depth agg stream done — %d lines", symbol, count)
    return count


async def main():
    """Orchestrate all 4 streams concurrently."""
    symbol = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 600

    token = load_token(TOKEN_PATH, TOKEN_PATH.read_text())
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    output_dir = Path.home() / "projects/syngex/data/level2"
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    files = {
        "quotes": {
            "raw": output_dir / f"quotes_raw_{symbol}_{ts}.jsonl",
            "parsed": output_dir / f"quotes_parsed_{symbol}_{ts}.jsonl",
        },
        "optionchain": {
            "raw": output_dir / f"optionchain_raw_{symbol}_{ts}.jsonl",
            "parsed": output_dir / f"optionchain_parsed_{symbol}_{ts}.jsonl",
        },
        "depthquotes": {
            "raw": output_dir / f"depthquotes_raw_{symbol}_{ts}.jsonl",
            "parsed": output_dir / f"depthquotes_parsed_{symbol}_{ts}.jsonl",
        },
        "depthagg": {
            "raw": output_dir / f"depthagg_raw_{symbol}_{ts}.jsonl",
            "parsed": output_dir / f"depthagg_parsed_{symbol}_{ts}.jsonl",
        },
    }

    print(f"{'='*60}")
    print(f"ORB Probe starting for {symbol} — {duration} seconds ({duration/60:.1f} min)")
    print(f"{'='*60}")
    print(f"Output files (8 total — raw + parsed per stream):")
    for name, paths in files.items():
        print(f"  {name}:")
        print(f"    raw:        {paths['raw']}")
        print(f"    parsed:     {paths['parsed']}")
    print(f"{'='*60}")
    print(f"All 4 streams will start simultaneously.")
    print()

    start = time.monotonic()

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            collect_quotes(session, symbol, headers, files["quotes"]["raw"], files["quotes"]["parsed"], duration),
            collect_option_chain(session, symbol, headers, files["optionchain"]["raw"], files["optionchain"]["parsed"], duration),
            collect_market_depth_quotes(session, symbol, headers, files["depthquotes"]["raw"], files["depthquotes"]["parsed"], duration),
            collect_market_depth_agg(session, symbol, headers, files["depthagg"]["raw"], files["depthagg"]["parsed"], duration),
            return_exceptions=True,
        )

    elapsed = time.monotonic() - start

    print(f"{'='*60}")
    print(f"ORB PROBE COMPLETE")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"Duration: {duration:.1f}s ({duration/60:.1f} min)")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"Target: {output_dir}")
    print(f"Files: 8 (raw + parsed per stream)")
    print()

    stream_names = ["Quotes", "OptionChain", "DepthQuotes", "DepthAgg"]
    for name, (paths, result) in zip(stream_names, zip(files.values(), results)):
        if isinstance(result, Exception):
            print(f"  [{name}]: ERROR — {result}")
        else:
            raw_path = list(paths.values())[0]
            parsed_path = list(paths.values())[1]
            raw_size = raw_path.stat().st_size if raw_path.exists() else 0
            parsed_size = parsed_path.stat().st_size if parsed_path.exists() else 0
            print(f"  [{name}]: {result} lines")
            print(f"    raw:        {raw_size:>10,} bytes  |  {raw_path.name}")
            print(f"    parsed:     {parsed_size:>10,} bytes  |  {parsed_path.name}")

    print()
    print(f"{'='*60}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    log = logging.getLogger("ORBProbe")
    asyncio.run(main())
