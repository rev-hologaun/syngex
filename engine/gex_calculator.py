"""
engine/gex_calculator.py — The Brain

Real-time Gamma Exposure (GEX) calculation engine.

Maintains an in-memory "Gamma Ladder" mapping strikes to their aggregate
Net Gamma. As JSON packets arrive from the stream, the engine instantly
updates the specific strike in the ladder.

Formula:
    Net Gamma at Strike K = Σ (Gamma_i × OpenInterest_i × Side_i)

Where Side_i is +1 for calls and -1 for puts.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Syngex.Engine.GEXCalculator")


@dataclass
class _StrikeBucket:
    """Aggregate state for a single strike price."""

    strike: float
    call_gamma_oi: float = 0.0        # Σ(gamma × OI) for calls
    put_gamma_oi: float = 0.0          # Σ(gamma × OI) for puts
    call_count: int = 0
    put_count: int = 0
    last_update: float = field(default_factory=time.perf_counter)

    @property
    def net_gamma(self) -> float:
        """Net Gamma at this strike: calls positive, puts negative."""
        return self.call_gamma_oi - self.put_gamma_oi

    @property
    def total_gamma_oi(self) -> float:
        return self.call_gamma_oi + self.put_gamma_oi


class GEXCalculator:
    """
    High-performance GEX calculation engine.

    State Management:
        - Maintains an in-memory Gamma Ladder: Dict[float, _StrikeBucket]
        - Each bucket aggregates all contracts at that strike
        - Updates are O(1) per incoming message

    The Math:
        Net Gamma at Strike K = Σ (Gamma_i × OpenInterest_i × Side_i)
        where Side_i = +1 for calls, -1 for puts
    """

    def __init__(self, symbol: str) -> None:
        self.symbol: str = symbol.upper()
        self.underlying_price: float = 0.0
        self._ladder: Dict[float, _StrikeBucket] = {}
        self._msg_count: int = 0
        self._option_count: int = 0
        self._quote_count: int = 0
        self._net_gamma: float = 0.0
        self._net_gamma_dirty: bool = True

        logger.info("GEXCalculator initialized for %s", self.symbol)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_message(self, message: Dict[str, Any]) -> None:
        """
        Process an incoming JSON message from the TradeStation stream.

        Handles:
            - option_update  → updates a specific strike in the ladder
            - underlying_update  → updates the underlying price
            - raw TradeStation quotes  → extracts underlying price
            - raw TradeStation option-chain  → extracts contracts
        """
        self._msg_count += 1

        try:
            msg_type = message.get("type")

            if msg_type == "underlying_update" and "price" in message:
                self._quote_count += 1
                self._update_underlying_price(message["price"])
                return

            if msg_type == "option_update":
                self._option_count += 1
                self._update_strike(message)
                return

            # Raw TradeStation quote objects (no "type" field)
            if "Last" in message and "Symbol" in message:
                self._quote_count += 1
                if message["Symbol"] == self.symbol:
                    self._update_underlying_price(float(message["Last"]))
                return

            # Raw TradeStation option-chain individual contract
            # Structure: {"Gamma": "0.02", "DailyOpenInterest": 500,
            #             "Side": "Call", "Strikes": ["400"],
            #             "Legs": [{"StrikePrice": "400", "OptionType": "Call"}]}
            if self._is_option_contract(message):
                self._option_count += 1
                self._update_strike_from_contract(message)
                return

            # Raw TradeStation option-chain response (fallback)
            # Structure: {"optionChain": {"underlying": {...}, "calls": [...], "puts": [...]}}
            chain = message.get("optionChain") or message.get("option_chain")
            if chain and isinstance(chain, dict):
                self._process_raw_option_chain(chain)
                return

        except Exception as exc:
            logger.error("Error processing message: %s", exc, exc_info=True)

    def update_underlying_price(self, price: float) -> None:
        """Direct setter for underlying price (used for initial setup)."""
        self._update_underlying_price(price)

    def get_net_gamma(self) -> float:
        """Return the total Net Gamma across all strikes."""
        if self._net_gamma_dirty:
            self._net_gamma = sum(b.net_gamma for b in self._ladder.values())
            self._net_gamma_dirty = False
        return self._net_gamma

    def get_strike_net_gamma(self, strike: float) -> float:
        """Return the Net Gamma for a specific strike."""
        bucket = self._ladder.get(strike)
        return bucket.net_gamma if bucket else 0.0

    def get_strike_gex(self, strike: float) -> float:
        """
        Return GEX for a specific strike.

        GEX = Net Gamma × 100 × Underlying Price
        """
        if self.underlying_price <= 0:
            return 0.0
        return self.get_strike_net_gamma(strike) * 100 * self.underlying_price

    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of the current state."""
        return {
            "symbol": self.symbol,
            "underlying_price": self.underlying_price,
            "net_gamma": self.get_net_gamma(),
            "active_strikes": len(self._ladder),
            "total_messages": self._msg_count,
            "option_updates": self._option_count,
            "quote_updates": self._quote_count,
        }

    def get_gamma_walls(self, threshold: float = 1e6) -> List[Dict[str, Any]]:
        """
        Identify Gamma Walls — strikes with massive GEX.

        A Gamma Wall is a strike where the Net GEX (in dollar terms)
        exceeds the given threshold.

        Returns sorted list of wall dicts sorted by absolute GEX.
        """
        walls: List[Dict[str, Any]] = []
        price = self.underlying_price
        if price <= 0:
            return walls

        for strike, bucket in self._ladder.items():
            gex = bucket.net_gamma * 100 * price
            if abs(gex) >= threshold:
                walls.append({
                    "strike": strike,
                    "net_gamma": bucket.net_gamma,
                    "gex": gex,
                    "side": "call" if bucket.net_gamma > 0 else "put",
                    "total_contracts": bucket.call_count + bucket.put_count,
                })

        walls.sort(key=lambda w: abs(w["gex"]), reverse=True)
        return walls

    def get_gamma_flip(self) -> Optional[float]:
        """
        Identify the Gamma Flip point.

        The Gamma Flip is the strike where net gamma shifts from
        positive (above) to negative (below) — i.e. the highest
        strike where cumulative net gamma goes negative when
        scanning from high to low.

        Returns the flip strike price, or None if no flip detected.
        """
        if not self._ladder:
            return None

        sorted_strikes = sorted(self._ladder.keys(), reverse=True)
        cumulative = 0.0

        for strike in sorted_strikes:
            cumulative += self._ladder[strike].net_gamma
            if cumulative < 0:
                return strike

        return None

    def get_gamma_profile(self) -> Dict[str, Any]:
        """
        Return the full Gamma Ladder profile — the evolving state.

        Used by the orchestrator for logging/reports.
        """
        profile: Dict[str, Any] = {
            "symbol": self.symbol,
            "underlying_price": self.underlying_price,
            "net_gamma": self.get_net_gamma(),
            "strikes": {},
        }

        for strike, bucket in sorted(self._ladder.items()):
            profile["strikes"][strike] = {
                "call_gamma_oi": bucket.call_gamma_oi,
                "put_gamma_oi": bucket.put_gamma_oi,
                "net_gamma": bucket.net_gamma,
                "total_contracts": bucket.call_count + bucket.put_count,
            }

        return profile

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _update_underlying_price(self, price: float) -> None:
        if price <= 0:
            return
        if price != self.underlying_price:
            self.underlying_price = price
            self._net_gamma_dirty = True
            logger.debug("Underlying price updated: %.2f", price)

    def _is_option_contract(self, msg: Dict[str, Any]) -> bool:
        """Check if this message is a raw TradeStation option contract."""
        return "Gamma" in msg and "DailyOpenInterest" in msg

    def _update_strike_from_contract(self, msg: Dict[str, Any]) -> None:
        """Extract strike, gamma, OI, and side from a raw option contract message."""
        # Gamma can be string or float
        gamma_raw = msg.get("Gamma", 0)
        gamma = float(gamma_raw) if gamma_raw else 0.0

        # DailyOpenInterest
        oi_raw = msg.get("DailyOpenInterest", 0)
        oi = float(oi_raw) if oi_raw else 0.0

        # Side: "Call" or "Put"
        side_raw = msg.get("Side", "")
        side = "call" if side_raw.lower() == "call" else "put"

        # Strike: try Strikes[] first, then Legs[].StrikePrice
        strike = 0.0
        strikes_arr = msg.get("Strikes", [])
        if isinstance(strikes_arr, list) and strikes_arr:
            try:
                strike = float(strikes_arr[0])
            except (ValueError, TypeError):
                pass
        if strike == 0:
            legs = msg.get("Legs", [])
            if isinstance(legs, list) and legs:
                leg = legs[0]
                if isinstance(leg, dict):
                    try:
                        strike = float(leg.get("StrikePrice", 0))
                    except (ValueError, TypeError):
                        pass

        if strike <= 0:
            return

        self._update_strike({
            "strike": strike,
            "gamma": gamma,
            "open_interest": oi,
            "side": side,
        })

    def _process_raw_option_chain(self, chain: Dict[str, Any]) -> None:
        """
        Process a raw TradeStation option-chain response.

        Extracts underlying price and all call/put contracts.
        Dispatches each contract as an option_update internally.
        """
        # Extract underlying price
        underlying = chain.get("underlying", {})
        price = underlying.get("lastPrice") or underlying.get("last") or 0.0
        if price and price > 0:
            self._update_underlying_price(price)

        for side_key in ("calls", "puts"):
            leg_list = chain.get(side_key, [])
            if not isinstance(leg_list, list):
                continue
            side_label = "call" if side_key == "calls" else "put"
            for leg in leg_list:
                if not isinstance(leg, dict):
                    continue
                strike = leg.get("strike", 0)
                gamma = leg.get("gamma", 0)
                oi = leg.get("openInterest", leg.get("open_interest", 0))
                symbol = leg.get("symbol", "")
                if not symbol:
                    continue
                self._option_count += 1
                self._update_strike({
                    "strike": strike,
                    "gamma": gamma,
                    "open_interest": oi,
                    "side": side_label,
                })

    def _update_strike(self, data: Dict[str, Any]) -> None:
        strike = data["strike"]
        gamma = data["gamma"]
        oi = data["open_interest"]
        side = data.get("side", "")

        # Determine sign: call = +1, put = -1
        is_call = side == "call"
        contribution = gamma * oi

        # Get or create the strike bucket
        if strike not in self._ladder:
            self._ladder[strike] = _StrikeBucket(strike=strike)

        bucket = self._ladder[strike]

        if is_call:
            bucket.call_gamma_oi += contribution
            bucket.call_count += 1
        else:
            bucket.put_gamma_oi += contribution
            bucket.put_count += 1

        bucket.last_update = time.perf_counter()
        self._net_gamma_dirty = True
