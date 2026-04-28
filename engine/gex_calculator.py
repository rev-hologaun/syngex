"""
GEX (Gamma Exposure) Calculator
─────────────────────────────────
Calculates gamma exposure from TradeStation option chain data.

GEX = Σ (Gamma × Open Interest × 100) per strike
    = Σ Gamma × Open Interest × 100 for calls − Σ Gamma × Open Interest × 100 for puts

Positive GEX → market makers buy dips / sell rips (stabilizing)
Negative GEX → market makers sell dips / buy rips (destabilizing)
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class OptionExposure:
    """Gamma exposure for a single option."""
    symbol: str
    strike: float
    option_type: str  # "Call" or "Put"
    expiration: str
    gamma: float
    open_interest: int
    gex: float  # Gamma × OI × 100
    ask_size: int = 0
    bid_size: int = 0


@dataclass
class GEXResult:
    """Aggregated GEX analysis."""
    symbol: str
    total_gex: float
    call_gex: float
    put_gex: float
    net_gex: float  # call_gex + put_gex (put_gex is negative)
    options: list[OptionExposure] = field(default_factory=list)
    by_strike: dict[float, float] = field(default_factory=lambda: defaultdict(float))
    by_expiration: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    top_strikes: list[tuple[float, float]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CONTRACT_MULTIPLIER = 100


def _parse_strike_from_symbol(symbol: str) -> float | None:
    """Extract strike price from TradeStation option symbol.

    Formats:
        TSLA 260501C00360000  → 360.000
        TSLA  260501C00360000 → 360.000
        TSLA260501C00360000   → 360.000
    """
    # Strip the underlying ticker, then look for 7-digit strike at end
    # Pattern: 6-digit date + C/P + 7-digit strike
    m = re.search(r'[CP](\d{7})$', symbol)
    if m:
        return float(m.group(1)) / 1000.0
    return None


def _parse_type_from_symbol(symbol: str) -> str | None:
    """Extract option type from TradeStation option symbol."""
    if 'C' in symbol[-8:] and 'C' == symbol[-8]:
        return "Call"
    if 'P' in symbol[-8:] and 'P' == symbol[-8]:
        return "Put"
    # Fallback: check last char
    last = symbol[-1]
    if last == 'C':
        return "Call"
    if last == 'P':
        return "Put"
    return None


# ---------------------------------------------------------------------------
# Core calculations
# ---------------------------------------------------------------------------

def calculate_option_gex(gamma: float, open_interest: int) -> float:
    """Calculate gamma exposure for a single option."""
    return gamma * open_interest * CONTRACT_MULTIPLIER


def calculate_gex(options: list[dict[str, Any]]) -> GEXResult:
    """Calculate GEX from a list of option chain events.

    Each event is a dict with fields like:
        Symbol, StrikePrice, OptionType, ExpirationDate,
        Gamma, DailyOpenInterest, AskSize, BidSize

    Returns a GEXResult with aggregated data.
    """
    exposures: list[OptionExposure] = []
    by_strike: dict[float, float] = defaultdict(float)
    by_expiration: dict[str, float] = defaultdict(float)

    for event in options:
        # Get fields — prefer explicit fields, fall back to symbol parsing
        strike = event.get("StrikePrice")
        option_type = event.get("OptionType")
        expiration = event.get("ExpirationDate", "")
        gamma = float(event.get("Gamma", 0))
        open_interest = int(event.get("DailyOpenInterest", 0))
        ask_size = int(event.get("AskSize", 0))
        bid_size = int(event.get("BidSize", 0))
        symbol = event.get("Symbol", "")

        # Fallback: parse from symbol if explicit fields missing
        if strike is None:
            strike = _parse_strike_from_symbol(symbol)
        if option_type is None:
            option_type = _parse_type_from_symbol(symbol)

        if strike is None or option_type is None:
            continue

        # Skip zero-gamma options (no meaningful GEX)
        if gamma == 0:
            continue

        gex = calculate_option_gex(gamma, open_interest)

        # Puts contribute negative GEX (market makers short puts = buy rips)
        if option_type == "Put":
            gex = -abs(gex)

        exposure = OptionExposure(
            symbol=symbol,
            strike=strike,
            option_type=option_type,
            expiration=expiration,
            gamma=gamma,
            open_interest=open_interest,
            gex=gex,
            ask_size=ask_size,
            bid_size=bid_size,
        )
        exposures.append(exposure)
        by_strike[strike] += gex
        if expiration:
            by_expiration[expiration] += gex

    # Sort strikes by absolute GEX (top movers first)
    sorted_strikes = sorted(by_strike.items(), key=lambda x: abs(x[1]), reverse=True)

    total_gex = sum(e.gex for e in exposures)
    call_gex = sum(e.gex for e in exposures if e.option_type == "Call")
    put_gex = sum(e.gex for e in exposures if e.option_type == "Put")

    return GEXResult(
        symbol="",  # Set by caller
        total_gex=total_gex,
        call_gex=call_gex,
        put_gex=put_gex,
        net_gex=total_gex,
        options=exposures,
        by_strike=by_strike,
        by_expiration=by_expiration,
        top_strikes=sorted_strikes,
    )


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def analyze_gex(result: GEXResult) -> dict[str, Any]:
    """Produce a human-readable analysis of the GEX result."""
    total = result.total_gex
    call = result.call_gex
    put = result.put_gex

    if total > 1e6:
        regime = "POSITIVE GAMMA"
        behavior = "Market makers buy dips, sell rips → stabilizing (range-bound)"
    elif total < -1e6:
        regime = "NEGATIVE GAMMA"
        behavior = "Market makers sell dips, buy rips → destabilizing (trending/volatile)"
    else:
        regime = "NEUTRAL GAMMA"
        behavior = "Balanced market maker positioning"

    top_n = 5
    top_strikes = result.top_strikes[:top_n]

    return {
        "regime": regime,
        "behavior": behavior,
        "total_gex": total,
        "call_gex": call,
        "put_gex": put,
        "top_strikes": top_strikes,
        "num_options": len(result.options),
        "num_strikes": len(result.by_strike),
        "num_expirations": len(result.by_expiration),
    }
