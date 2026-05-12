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
    """Aggregate state for a single strike price.

    Note: OI values from stream greeks are **relative** (not absolute
    contract counts). The stream does not include real open interest —
    OI defaults to 1.0 per message. Use `set_open_interest()` to update
    with real OI from REST API if/when we add periodic OI fetching.

    OI-dependent strategies (e.g. Call/Put Flow Asymmetry) use relative
    ratios which still work for detecting asymmetry direction and magnitude.
    """

    strike: float
    # Accumulated gamma × OI products (used for GEX calculation)
    call_gamma_oi: float = 0.0
    put_gamma_oi: float = 0.0
    # Individual gamma sums (for per-strike analysis)
    call_gamma: float = 0.0
    put_gamma: float = 0.0
    # Open interest (relative from stream; update via set_open_interest)
    call_oi: float = 0.0
    put_oi: float = 0.0
    # Delta sums (for per-strike delta analysis)
    call_delta: float = 0.0
    put_delta: float = 0.0
    # IV sums (for per-strike IV averaging)
    call_iv_sum: float = 0.0
    put_iv_sum: float = 0.0
    # Message counts
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

    @property
    def net_oi(self) -> float:
        """Net open interest: calls minus puts."""
        return self.call_oi - self.put_oi

    @property
    def net_delta(self) -> float:
        """Net delta: call_delta_sum minus put_delta_sum."""
        return self.call_delta - self.put_delta

    @property
    def net_delta_density(self) -> float:
        """Delta density: abs(net_delta) / total message count.

        Measures how concentrated the delta is per message at this strike.
        High density = aggressive positioning (magnet). Low density = passive
        hedging (wall).
        """
        total_count = self.call_count + self.put_count
        if total_count == 0:
            return 0.0
        return abs(self.net_delta) / total_count

    def normalized_gamma(self) -> float:
        """Return normalized (per-message average) net gamma.

        The cumulative gamma_oi values grow linearly with message count,
        so we divide by total messages for that strike to get a bounded
        per-message average. This is the value used for GEX calculations.
        """
        total_count = self.call_count + self.put_count
        if total_count == 0:
            return 0.0
        return self.net_gamma / total_count

    def normalized_call_gamma(self) -> float:
        """Return normalized (per-message average) call gamma."""
        if self.call_count == 0:
            return 0.0
        return self.call_gamma_oi / self.call_count

    def normalized_put_gamma(self) -> float:
        """Return normalized (per-message average) put gamma."""
        if self.put_count == 0:
            return 0.0
        return self.put_gamma_oi / self.put_count


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
            - stream greeks objects  → infers strike/side from greeks
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

            # Stream greeks objects — flat JSON with Delta, Gamma, IntrinsicValue, etc.
            # No contract identifier, strike, or side. Must infer everything.
            if self._is_stream_greeks(message):
                self._option_count += 1
                self._update_strike_from_stream(message)
                return

        except Exception as exc:
            logger.error("Error processing message: %s", exc, exc_info=True)

    def update_underlying_price(self, price: float) -> None:
        """Direct setter for underlying price (used for initial setup)."""
        self._update_underlying_price(price)

    def get_net_gamma(self) -> float:
        """Return the total Net Gamma across all strikes (cumulative).

        This returns cumulative values that grow with message count.
        Use for sign detection (regime filtering). For magnitude
        comparisons, use get_normalized_net_gamma() instead.
        """
        if self._net_gamma_dirty:
            self._net_gamma = sum(b.net_gamma for b in self._ladder.values())
            self._net_gamma_dirty = False
        return self._net_gamma

    def get_normalized_net_gamma(self) -> float:
        """Return the total normalized (per-message average) net gamma across all strikes.

        Unlike get_net_gamma() which returns cumulative values that grow with
        message count, this returns bounded per-message averages — the canonical
        scale for GEX comparisons (walls, magnets, etc.).

        Computed as: sum over all strikes of (net_gamma / total_messages_at_strike)
        """
        total = 0.0
        for bucket in self._ladder.values():
            total_count = bucket.call_count + bucket.put_count
            if total_count > 0:
                total += bucket.net_gamma / total_count
        return total

    def get_normalized_strike_net_gamma(self, strike: float) -> float:
        """Return normalized (per-message average) net gamma for a specific strike."""
        bucket = self._ladder.get(strike)
        if bucket is None:
            return 0.0
        return bucket.normalized_gamma()

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
        """Return a summary of the current state.

        Contains both cumulative and normalized net gamma:
            - net_gamma: cumulative gamma that grows with message count.
              Useful for sign detection (regime filtering).
            - net_gamma_normalized: per-message average gamma, bounded
              regardless of message count. The canonical scale for GEX
              comparisons (walls, magnets, cross-session analysis).
        """
        return {
            "symbol": self.symbol,
            "underlying_price": self.underlying_price,
            "net_gamma": self.get_net_gamma(),
            "net_gamma_normalized": self.get_normalized_net_gamma(),
            "active_strikes": len(self._ladder),
            "total_messages": self._msg_count,
            "option_updates": self._option_count,
            "quote_updates": self._quote_count,
        }

    def get_gamma_walls(
        self, threshold: float = 1e6, include_ghosts: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Identify Gamma Walls — strikes with massive GEX.

        A Gamma Wall is a strike where the normalized Net GEX (in dollar terms)
        exceeds the given threshold. Uses normalized (per-message average) gamma
        values so GEX stays bounded regardless of message count.

        The threshold is on the normalized GEX scale (e.g. 1e6).
        For total GEX magnitude across all strikes, use get_normalized_net_gamma().

        Args:
            threshold: Minimum |GEX| to consider a wall.
            include_ghosts: If False, exclude walls with no recent updates
                (older than 60 seconds). Default True for backward compatibility.

        Returns sorted list of wall dicts sorted by absolute GEX.
        """
        walls: List[Dict[str, Any]] = []
        price = self.underlying_price
        if price <= 0:
            return walls

        for strike, bucket in self._ladder.items():
            # Normalize cumulative gamma by message count for bounded GEX
            norm_net_gamma = bucket.normalized_gamma()
            gex = norm_net_gamma * 100 * price
            if abs(gex) >= threshold:
                # Skip ghost walls unless explicitly requested
                if not include_ghosts:
                    age = time.perf_counter() - bucket.last_update
                    if age > 60.0:
                        continue
                walls.append({
                    "strike": strike,
                    "net_gamma": norm_net_gamma,
                    "gex": gex,
                    "side": "call" if norm_net_gamma > 0 else "put",
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
        Gamma values are normalized (per-message average) for realistic display.
        """
        profile: Dict[str, Any] = {
            "symbol": self.symbol,
            "underlying_price": self.underlying_price,
            "net_gamma": self.get_net_gamma(),
            "strikes": {},
        }

        for strike, bucket in sorted(self._ladder.items()):
            profile["strikes"][strike] = {
                "call_gamma_oi": bucket.normalized_call_gamma(),
                "put_gamma_oi": bucket.normalized_put_gamma(),
                "net_gamma": bucket.normalized_gamma(),
                "total_contracts": bucket.call_count + bucket.put_count,
            }

        return profile

    # ------------------------------------------------------------------
    # Greeks Summary (for Layer 2 strategies)
    # ------------------------------------------------------------------

    def get_greeks_summary(self) -> Dict[float, Dict[str, float]]:
        """Return per-strike greeks summary for strategy use.

        Returns dict mapping strike -> {
            'net_gamma': float,  # normalized (per-message average)
            'call_gamma': float,  # normalized (per-message average)
            'put_gamma': float,   # normalized (per-message average)
            'call_oi': float,
            'put_oi': float,
            'net_oi': float,
            'net_delta': float,
            'call_delta_sum': float,
            'put_delta_sum': float,
        }

        Gamma values are normalized (divided by message count) to produce
        bounded, per-message averages. OI values remain cumulative as they
        represent relative OI from the stream.

        Note: OI values are **relative** (not absolute contract counts).
        OI-dependent strategies use relative ratios which still work for
        detecting asymmetry direction and magnitude.
        """
        summary: Dict[float, Dict[str, float]] = {}
        for strike, bucket in self._ladder.items():
            summary[strike] = {
                "net_gamma": bucket.normalized_gamma(),
                "call_gamma": bucket.normalized_call_gamma(),
                "put_gamma": bucket.normalized_put_gamma(),
                "call_oi": bucket.call_oi,
                "put_oi": bucket.put_oi,
                "net_oi": bucket.net_oi,
                "net_delta": bucket.net_delta,
                "call_delta_sum": bucket.call_delta,
                "put_delta_sum": bucket.put_delta,
            }
        return summary

    # ------------------------------------------------------------------
    # Layer 2 helper methods (for strategy use)
    # ------------------------------------------------------------------

    def get_delta_by_strike(self, strike: float) -> Dict[str, float]:
        """Return delta data for a specific strike.

        Returns dict with:
            call_delta: sum of call deltas at this strike
            put_delta: sum of put deltas at this strike
            net_delta: call_delta - put_delta
            call_count, put_count: number of messages
        """
        bucket = self._ladder.get(strike)
        if bucket is None:
            return {
                "call_delta": 0.0,
                "put_delta": 0.0,
                "net_delta": 0.0,
                "call_count": 0,
                "put_count": 0,
            }
        return {
            "call_delta": bucket.call_delta,
            "put_delta": bucket.put_delta,
            "net_delta": bucket.net_delta,
            "call_count": bucket.call_count,
            "put_count": bucket.put_count,
        }

    def get_iv_by_strike(self, strike: float) -> Optional[float]:
        """Return average IV at a specific strike.

        IV is tracked per-message and averaged across all messages
        for that strike/side.
        """
        bucket = self._ladder.get(strike)
        if bucket is None:
            return None

        total_iv = bucket.call_iv_sum + bucket.put_iv_sum
        total_count = bucket.call_count + bucket.put_count
        if total_count == 0:
            return None
        return total_iv / total_count

    def get_iv_skew(self) -> Optional[float]:
        """Return IV skew: average call IV minus average put IV.

        Positive skew = calls more expensive (bullish fear).
        Negative skew = puts more expensive (bearish fear).

        Returns None if insufficient data.
        """
        total_call_iv = 0.0
        total_put_iv = 0.0
        call_count = 0
        put_count = 0

        for bucket in self._ladder.values():
            total_call_iv += bucket.call_iv_sum
            call_count += bucket.call_count
            total_put_iv += bucket.put_iv_sum
            put_count += bucket.put_count

        if call_count == 0 or put_count == 0:
            return None

        avg_call_iv = total_call_iv / call_count
        avg_put_iv = total_put_iv / put_count
        return avg_call_iv - avg_put_iv

    def get_greeks_cache(self) -> Dict[str, Any]:
        """Return a read-only view of per-strike greeks data for Layer 2 strategies.

        Returns dict mapping strike -> {"calls": [...], "puts": [...]}
        where each entry contains delta, gamma, iv, oi from stream messages.

        Note: This is a snapshot of current state. For read-only access,
        consumers should not modify the returned data.
        """
        cache: Dict[str, Any] = {}
        for strike, bucket in self._ladder.items():
            cache[strike] = {
                "call_delta": bucket.call_delta,
                "put_delta": bucket.put_delta,
                "call_gamma": bucket.call_gamma,
                "put_gamma": bucket.put_gamma,
                "call_oi": bucket.call_oi,
                "put_oi": bucket.put_oi,
                "call_count": bucket.call_count,
                "put_count": bucket.put_count,
                "call_iv_sum": bucket.call_iv_sum,
                "put_iv_sum": bucket.put_iv_sum,
                "net_gamma": bucket.net_gamma,
                "net_oi": bucket.net_oi,
            }
        return cache

    def set_open_interest(self, strike: float, call_oi: float, put_oi: float) -> None:
        """Update open interest for a specific strike.

        Called from REST API data when we add periodic OI fetching.
        Replaces the relative OI (default 1.0) with real contract counts.

        Args:
            strike: The strike price to update.
            call_oi: Real call open interest (contract count).
            put_oi: Real put open interest (contract count).
        """
        bucket = self._ladder.get(strike)
        if bucket is None:
            logger.warning("No bucket for strike %.1f — OI update ignored", strike)
            return

        # Recalculate gamma_oi products with real OI
        # gamma_oi = gamma × oi for each side
        # We preserve the per-gamma values and recompute products
        if bucket.call_count > 0:
            avg_call_gamma = bucket.call_gamma / bucket.call_count
            bucket.call_gamma_oi = avg_call_gamma * call_oi
            bucket.call_oi = call_oi
        if bucket.put_count > 0:
            avg_put_gamma = bucket.put_gamma / bucket.put_count
            bucket.put_gamma_oi = avg_put_gamma * put_oi
            bucket.put_oi = put_oi

        self._net_gamma_dirty = True
        logger.debug("Updated OI for strike %.1f: call=%.0f put=%.0f", strike, call_oi, put_oi)

    def get_iv_by_strike_avg(self) -> Dict[float, float]:
        """Return average IV per strike for all strikes with data.

        Returns dict mapping strike -> average IV value.
        Used by iv_gex_divergence for rolling IV window tracking.
        """
        result: Dict[float, float] = {}
        for strike, bucket in self._ladder.items():
            total_count = bucket.call_count + bucket.put_count
            if total_count > 0:
                total_iv = bucket.call_iv_sum + bucket.put_iv_sum
                result[strike] = total_iv / total_count
        return result

    # ------------------------------------------------------------------
    # Delta Density & Wall Classification
    # ------------------------------------------------------------------

    def get_delta_density(self, strike: float) -> float:
        """Return delta density for a specific strike.

        Delta density = abs(net_delta) / (call_count + put_count).
        Measures how concentrated the delta is per message at this strike.

        Args:
            strike: The strike price to look up.

        Returns:
            Delta density value (float). Returns 0.0 if no bucket exists.
        """
        bucket = self._ladder.get(strike)
        if bucket is None:
            return 0.0
        return bucket.net_delta_density

    def classify_wall(
        self, bucket: _StrikeBucket, gex: float, price: float,
        density_threshold: float = 0.5, magnet_threshold: float = 2.0,
    ) -> str:
        """Classify a strike bucket as a wall, magnet, or weak.

        Classification logic:
            - "wall"   — high GEX, low delta density → dealers are hedging passively,
                         price repels (good for gamma_wall_bounce)
            - "magnet" — high GEX, high delta density → dealers are heavily positioned,
                         price attracts (NOT for gamma_wall_bounce)
            - "weak"   — low GEX, high delta density → noise, not a real structure

        Args:
            bucket: The _StrikeBucket to classify.
            gex: The GEX value at this strike.
            price: Current underlying price (unused but kept for future extensibility).
            density_threshold: Delta density below which we consider it "low".
            magnet_threshold: Delta density above which we consider it "high".

        Returns:
            One of "wall", "magnet", or "weak".
        """
        density = bucket.net_delta_density
        if density < density_threshold and abs(gex) > 0:
            return "wall"
        elif density > magnet_threshold and abs(gex) > 0:
            return "magnet"
        else:
            return "weak"

    def get_wall_classifications(
        self, threshold: float = 1e6,
        density_threshold: float = 0.5, magnet_threshold: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """Return all gamma walls with classification added.

        Reuses get_gamma_walls() logic and adds a "classification" key
        to each wall dict: "wall", "magnet", or "weak".

        Args:
            threshold: Minimum |GEX| to consider a wall.
            density_threshold: Delta density below which = "wall".
            magnet_threshold: Delta density above which = "magnet".

        Returns:
            List of wall dicts with added "classification" key.
        """
        walls: List[Dict[str, Any]] = []
        price = self.underlying_price
        if price <= 0:
            return walls

        for strike, bucket in self._ladder.items():
            norm_net_gamma = bucket.normalized_gamma()
            gex = norm_net_gamma * 100 * price
            if abs(gex) >= threshold:
                classification = self.classify_wall(
                    bucket, gex, price,
                    density_threshold=density_threshold,
                    magnet_threshold=magnet_threshold,
                )
                walls.append({
                    "strike": strike,
                    "net_gamma": norm_net_gamma,
                    "gex": gex,
                    "side": "call" if norm_net_gamma > 0 else "put",
                    "total_contracts": bucket.call_count + bucket.put_count,
                    "classification": classification,
                })

        walls.sort(key=lambda w: abs(w["gex"]), reverse=True)
        return walls

    def get_wall_with_freshness(
        self, threshold: float = 1e6, max_age_seconds: float = 60.0,
    ) -> List[Dict[str, Any]]:
        """Return walls filtered by freshness.

        Uses bucket.last_update (perf_counter timestamp) to check if a wall
        is stale. Adds "is_ghost" and "last_update_age" to each wall dict.

        Args:
            threshold: Minimum |GEX| to consider a wall.
            max_age_seconds: Maximum age in seconds before a wall is considered
                a ghost.

        Returns:
            List of wall dicts with added "is_ghost" and "last_update_age" keys.
        """
        walls: List[Dict[str, Any]] = []
        price = self.underlying_price
        if price <= 0:
            return walls

        now = time.perf_counter()
        for strike, bucket in self._ladder.items():
            norm_net_gamma = bucket.normalized_gamma()
            gex = norm_net_gamma * 100 * price
            if abs(gex) >= threshold:
                age = now - bucket.last_update
                is_ghost = age > max_age_seconds
                walls.append({
                    "strike": strike,
                    "net_gamma": norm_net_gamma,
                    "gex": gex,
                    "side": "call" if norm_net_gamma > 0 else "put",
                    "total_contracts": bucket.call_count + bucket.put_count,
                    "is_ghost": is_ghost,
                    "last_update_age": age,
                })

        walls.sort(key=lambda w: abs(w["gex"]), reverse=True)
        return walls

    def get_atm_strike(self, price: float) -> Optional[float]:
        """Find the nearest strike in the gamma ladder to the current price.

        Public API — replaces direct access to _ladder.
        """
        if not self._ladder:
            return None

        nearest = None
        min_dist = float("inf")

        for strike in self._ladder:
            dist = abs(strike - price)
            if dist < min_dist:
                min_dist = dist
                nearest = strike

        return nearest

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

    def _is_stream_greeks(self, msg: Dict[str, Any]) -> bool:
        """
        Detect a stream greeks object from the TradeStation option-chain SSE.

        These are flat JSON objects with Delta, Gamma, IntrinsicValue, etc.
        but NO contract identifier, strike, or side field.

        Heuristic: has Delta AND Gamma AND IntrinsicValue, but NO
        DailyOpenInterest (which distinguishes from the old contract format).
        """
        has_greeks = "Delta" in msg and "Gamma" in msg
        has_intrinsic = "IntrinsicValue" in msg
        no_oi = "DailyOpenInterest" not in msg
        return has_greeks and has_intrinsic and no_oi

    def _infer_side(self, delta: float) -> str:
        """Infer call/put from Delta sign. Delta > 0 → call, Delta < 0 → put."""
        return "call" if delta > 0 else "put"

    def _infer_strike_from_intrinsic(self, intrinsic_value: float, delta: float) -> Optional[float]:
        """
        Infer strike price from IntrinsicValue and underlying price.

        For ITM options (intrinsic > 0):
            Put:  strike = underlying + intrinsic
            Call: strike = underlying - intrinsic

        For OTM options (intrinsic == 0), return None — strike must be
        approximated from delta/probability instead.

        Returns the strike rounded to the nearest $2.50 interval (standard
        for equity options), or None if strike cannot be determined.
        """
        if self.underlying_price <= 0:
            return None

        if intrinsic_value > 0:
            # ITM: exact strike from intrinsic value
            if delta > 0:
                # Call: intrinsic = underlying - strike
                strike = self.underlying_price - intrinsic_value
            else:
                # Put: intrinsic = strike - underlying
                strike = self.underlying_price + intrinsic_value
            return self._round_strike(strike)

        return None  # OTM — need delta-based approximation

    def _infer_strike_from_probability(self, prob_itm: float, delta: float) -> Optional[float]:
        """
        Approximate strike for OTM options using ProbabilityITM.

        Calibrated mapping: each ~10% drop in ProbITM ≈ 1 strike interval ($2.50)
        from ATM. This is more reliable than delta for strike inference.

        For calls: ProbITM directly gives the probability.
        For puts: ProbITM = 1 - ProbOTM (but stream gives both).

        Calibration (TSLA observed):
            ProbITM ~0.41 → 1 strike OTM
            ProbITM ~0.30 → 2 strikes OTM
            ProbITM ~0.20 → 3 strikes OTM
            ProbITM ~0.13 → 4 strikes OTM
            ProbITM ~0.08 → 5 strikes OTM
        """
        if self.underlying_price <= 0:
            return None

        # Use ProbabilityITM for calls, (1 - ProbITM) for puts
        if delta > 0:
            # Call: ProbITM is directly available
            prob = prob_itm
        else:
            # Put: use 1 - ProbITM (since ProbITM for puts is low when OTM)
            # Actually, for puts ProbITM IS the probability the put is ITM
            # An OTM put has LOW ProbITM (e.g., 0.08 for 5 strikes OTM)
            # So we need 1 - ProbITM to get the "distance" metric
            prob = 1.0 - prob_itm

        # If prob is very close to 0.5, this is ATM — can't distinguish
        if abs(prob - 0.5) < 0.05:
            return None

        # Distance from ATM in probability units
        prob_distance = abs(prob - 0.5)

        # Each $2.50 strike ≈ 0.10 probability change near ATM
        prob_per_strike = 0.10
        strikes_away = prob_distance / prob_per_strike

        strikes_away_rounded = round(strikes_away)

        if strikes_away_rounded < 1:
            return None

        # Direction: OTM call → strike > underlying, OTM put → strike < underlying
        if delta > 0:
            strike = self.underlying_price + strikes_away_rounded * 2.5
        else:
            strike = self.underlying_price - strikes_away_rounded * 2.5

        return self._round_strike(strike)

    @staticmethod
    def _round_strike(strike: float) -> float:
        """Round to nearest $2.50 interval (standard equity option strike)."""
        return round(strike / 2.5) * 2.5

    def _update_strike_from_stream(self, msg: Dict[str, Any]) -> None:
        """
        Process a stream greeks object — infer strike, side, and update ladder.

        Stream greeks objects have:
            Delta, Theta, Gamma, Rho, Vega, ImpliedVolatility,
            IntrinsicValue, ExtrinsicValue, TheoreticalValue,
            ProbabilityITM, ProbabilityOTM, ProbabilityBE

        Missing fields (inferred):
            side    → from Delta sign
            strike  → from IntrinsicValue + underlying_price (ITM)
                      or from delta approximation (OTM)
            open_interest → defaults to 1.0 (not in stream)

        Note: OI values are **relative** (not absolute contract counts).
        The stream does not include real open interest. Use
        `set_open_interest()` to update with real OI from REST API
        when we add periodic OI fetching.
        """
        # Extract greeks
        try:
            delta = float(msg.get("Delta", 0))
            gamma = float(msg.get("Gamma", 0))
            intrinsic = float(msg.get("IntrinsicValue", 0))
        except (ValueError, TypeError):
            return

        if gamma <= 0:
            return  # Skip invalid gamma

        # Infer side from delta sign
        side = self._infer_side(delta)

        # Try to infer strike from intrinsic value (works for ITM)
        strike = self._infer_strike_from_intrinsic(intrinsic, delta)

        # If intrinsic is 0 (OTM), approximate from ProbabilityITM
        if strike is None:
            prob_itm = float(msg.get("ProbabilityITM", 0.5))
            strike = self._infer_strike_from_probability(prob_itm, delta)

        if strike is None or strike <= 0:
            logger.debug(
                "Cannot infer strike for delta=%.4f intrinsic=%.2f, skipping",
                delta, intrinsic,
            )
            return

        # Open interest not in stream — default to 1.0
        # This means GEX values are relative, not absolute
        oi = 1.0

        # Extract IV from stream greeks
        iv = float(msg.get("ImpliedVolatility", 0))

        self._update_strike({
            "strike": strike,
            "gamma": gamma,
            "open_interest": oi,
            "side": side,
            "delta": delta,
            "iv": iv,
        })

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
        delta = data.get("delta", 0.0)  # Optional from stream greeks
        iv = data.get("iv", 0.0)  # Optional IV from stream greeks

        # Determine sign: call = +1, put = -1
        is_call = side == "call"
        contribution = gamma * oi

        # Get or create the strike bucket
        if strike not in self._ladder:
            self._ladder[strike] = _StrikeBucket(strike=strike)

        bucket = self._ladder[strike]

        if is_call:
            bucket.call_gamma_oi += contribution
            bucket.call_gamma += gamma
            bucket.call_oi += oi
            bucket.call_delta += delta
            bucket.call_iv_sum += iv
            bucket.call_count += 1
        else:
            bucket.put_gamma_oi += contribution
            bucket.put_gamma += gamma
            bucket.put_oi += oi
            bucket.put_delta += delta
            bucket.put_iv_sum += iv
            bucket.put_count += 1

        bucket.last_update = time.perf_counter()
        self._net_gamma_dirty = True

    def set_underlying_price(self, price: float) -> None:
        """
        Set the underlying price directly.

        Required for strike inference from stream greeks objects,
        since the SSE stream does not include the underlying price.
        """
        self._update_underlying_price(price)
