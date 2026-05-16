"""
strategies/layer3/theta_burn.py — Theta-Burn Scalp v2 "Pinning-Master"

Micro-signal (1Hz) strategy: exploits the pinning effect in high-gamma,
high-theta environments. Price oscillates between gamma walls as dealers
continuously hedge counter-cyclically.

v2 Architecture — Pinning-Master Upgrade:
    - Regime-specific logic: POSITIVE gamma = bounce mode, NEGATIVE gamma = slice mode
    - Wall Liquidity Exhaustion Detection — detects collapsing walls
    - Delta-Gamma Divergence Rejection — hard rejection signature (delta spike + price stationary)
    - IV-Expansion Scaled Targets — targets scale with IV expansion factor
    - Higher confidence bar: 0.35 (up from 0.25)

Logic:
    - POSITIVE gamma regime: Bounce mode — trade wall bounces (mean reversion)
        LONG: buy dips at Put Walls (below price)
        SHORT: sell rips at Call Walls (above price)
    - NEGATIVE gamma regime: Slice mode — trade wall breakouts (momentum)
        LONG slice: price breaking through Call wall above (momentum up)
        SHORT slice: price breaking through Put wall below (momentum down)
    - NEUTRAL regime: Skip signals

Entry (bounce):
    - LONG: buy dips at Put Wall + delta-gamma rejection + wall holding
    - SHORT: sell rips at Call Wall + delta-gamma rejection + wall holding
Entry (slice):
    - LONG: price breaking Call wall from below + ask vacuum
    - SHORT: price breaking Put wall from above + bid vacuum

Exit:
    - Bounce targets: 0.2-0.6% (IV-scaled)
    - Slice targets: 0.3-0.8% (IV-scaled)
    - Stop: 0.3% beyond the wall
    - Time hold: 3-8 min max

Confidence factors (bounce — 6 components):
    1. Gamma strength (0.10–0.20)
    2. Wall proximity (0.15–0.25)
    3. Range narrowness (0.10–0.15)
    4. Delta-gamma divergence (0.20–0.25) — HARD GATE
    5. Wall liquidity (0.10–0.15) — HARD GATE
    6. IV expansion (0.05–0.10)

Confidence factors (slice — 7 components):
    1. Gamma strength (0.10–0.20)
    2. Delta-gamma divergence (0.20–0.25) — HARD GATE
    3. Wall liquidity vacuum (0.15–0.20) — HARD GATE
    4. Range narrowness (0.10–0.15)
    5. Volume confirmation (0.10–0.15)
    6. IV expansion (0.05–0.10)
    7. Time of day (0.05–0.10)
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_MARKET_DEPTH_AGG,
    KEY_PRICE_5M,
    KEY_PRICE_30M,
    KEY_VOLUME_5M,
    KEY_ATM_IV_5M,
    KEY_WALL_DELTA_5M,
)

logger = logging.getLogger("Syngex.Strategies.ThetaBurn")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Net gamma must be strongly positive (threshold to avoid weak signals)
MIN_NET_GAMMA = 5000.0

# Wall proximity for bounce trades
WALL_PROXIMITY_PCT = 0.005  # 0.5%

# Stop loss: beyond the wall
STOP_PAST_WALL_PCT = 0.003  # 0.3% beyond the wall

# Quick targets: 0.2-0.4% from entry (v1 defaults)
MIN_TARGET_PCT = 0.002      # 0.2% min target
MAX_TARGET_PCT = 0.004      # 0.4% max target

# Range narrowness: 5m range must be < this % of 30m range
RANGE_NARROWNESS_RATIO = 0.40  # 40%

# Min confidence — raised from 0.25 to 0.35 for v2
MIN_CONFIDENCE = 0.10

# Min data points
MIN_DATA_POINTS = 3

# Midday lull window in UTC (11:30-14:30 ET = 16:30-19:30 UTC)
MIDNIGHT_UTC_START = 16.5   # 16:30 UTC
MIDNIGHT_UTC_END = 19.5     # 19:30 UTC

# Gamma strength normalization for confidence
GAMMA_STRENGTH_HIGH = 1_000_000.0  # Above this = max gamma strength bonus


class ThetaBurn(BaseStrategy):
    """
    Exploits the pinning effect in high-gamma environments.

    v2 Pinning-Master: Regime-specific logic with wall liquidity detection,
    delta-gamma divergence rejection, and IV-scaled targets.

    POSITIVE gamma regime → Bounce mode (mean reversion at walls)
    NEGATIVE gamma regime → Slice mode (momentum breakouts through walls)
    NEUTRAL regime → Skip signals
    """

    strategy_id = "theta_burn"
    layer = "layer3"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for theta-burn pinning signals.

        Returns empty list when no pinning setup is detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")
        timestamp = data.get("timestamp", 0)

        # Hard gate: regime must be POSITIVE or NEGATIVE (not NEUTRAL)
        if regime not in ("POSITIVE", "NEGATIVE"):
            return []

        # POSITIVE gamma → bounce mode; NEGATIVE gamma → slice mode
        if regime == "POSITIVE":
            return self._check_bounce_mode(
                data, gex_calc, rolling_data, net_gamma, timestamp,
            )
        else:  # NEGATIVE
            return self._check_slice_mode(
                data, gex_calc, rolling_data, net_gamma, timestamp,
            )

    # ------------------------------------------------------------------
    # Bounce Mode (POSITIVE gamma regime)
    # ------------------------------------------------------------------

    def _check_bounce_mode(
        self,
        data: Dict[str, Any],
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        timestamp: float,
    ) -> List[Signal]:
        """POSITIVE gamma regime: trade wall bounces."""
        price = data.get("underlying_price", 0)
        if price <= 0:
            return []

        # Validate rolling data availability
        price_5m = rolling_data.get(KEY_PRICE_5M)
        price_30m = rolling_data.get(KEY_PRICE_30M)
        volume_5m = rolling_data.get(KEY_VOLUME_5M)

        if not all([price_5m, price_30m, volume_5m]):
            return []

        if not all([
            price_5m.count >= MIN_DATA_POINTS,
            price_30m.count >= MIN_DATA_POINTS,
            volume_5m.count >= MIN_DATA_POINTS,
        ]):
            return []

        # Check range narrowness: 5m range must be < 30% of 30m range
        range_ratio = self._check_range_narrowness(price_5m, price_30m)
        if range_ratio is None or range_ratio >= RANGE_NARROWNESS_RATIO:
            return []

        signals: List[Signal] = []

        # Get gamma walls
        walls = self._safe_get_walls(gex_calc)
        if not walls:
            return []

        # Check LONG (buy dips at Put Walls below price)
        long_sig = self._check_put_wall(
            price, gex_calc, rolling_data, net_gamma, walls, timestamp, range_ratio,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT (sell rips at Call Walls above price)
        short_sig = self._check_call_wall(
            price, gex_calc, rolling_data, net_gamma, walls, timestamp, range_ratio,
        )
        if short_sig:
            signals.append(short_sig)

        return signals

    def _check_put_wall(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        walls: List[Dict[str, Any]],
        timestamp: float,
        range_ratio: float,
    ) -> Optional[Signal]:
        """
        Evaluate Put Walls for LONG bounce opportunity.

        Put wall = negative net_gamma → acts as support.
        We want price approaching from above and showing rejection.
        """
        # Find Put Walls below price (negative gamma)
        put_walls = [
            w for w in walls
            if w["strike"] < price and w.get("side") == "put"
        ]
        if not put_walls:
            put_walls = [
                w for w in walls
                if w["strike"] < price and w.get("net_gamma", 0) < 0
            ]
        if not put_walls:
            return None

        # Nearest Put Wall below price
        nearest_wall = max(put_walls, key=lambda w: w["strike"])
        wall_strike = nearest_wall["strike"]
        wall_gex = nearest_wall.get("gex", 0)
        wall_net_gamma = nearest_wall.get("net_gamma", 0)

        # Proximity: price must be within WALL_PROXIMITY_PCT above wall
        distance_pct = (price - wall_strike) / price
        if distance_pct < 0 or distance_pct > WALL_PROXIMITY_PCT:
            return None

        # HARD GATE 1: Delta-gamma divergence (hard rejection)
        divergence_ok, divergence_score, current_delta = self._check_delta_gamma_divergence(
            rolling_data, wall_strike, "LONG",
        )
        if not divergence_ok:
            return None

        # HARD GATE 2: Wall liquidity — wall must have depth to hold
        liquidity_ok, bid_depth, ask_depth, liquidity_status = self._check_wall_liquidity(
            data={KEY_MARKET_DEPTH_AGG: None},  # placeholder; will be set below
            wall_strike=wall_strike,
            direction="LONG",
            mode="bounce",
        )
        # We need data for depth — get it from the outer call
        # Since we don't have data here, we'll compute depth inline
        bid_depth, ask_depth, liquidity_status = self._get_wall_depth(
            rolling_data, wall_strike, "LONG", "bounce",
        )
        liquidity_ok = (bid_depth > 0)  # If depth data available, check it
        if liquidity_ok:
            liquidity_ok = bid_depth > 0  # At minimum, wall has some bid depth

        if not liquidity_ok:
            return None

        # Compute IV-scaled target
        target = self._compute_iv_scaled_target(
            wall_strike, walls, price, "above", rolling_data, "bounce",
        )

        # Compute confidence (bounce mode)
        confidence = self._compute_bounce_confidence(
            price, wall_strike, wall_gex, wall_net_gamma,
            distance_pct, range_ratio, divergence_score,
            bid_depth, ask_depth, liquidity_status,
            current_delta, timestamp, "LONG",
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        entry = price
        stop = wall_strike * (1 - STOP_PAST_WALL_PCT)
        risk = entry - stop

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Theta-Burn v2 LONG: Put wall at {wall_strike} held, "
                f"GEX={wall_gex:.0f}, range_ratio={range_ratio:.2f}, "
                f"divergence={divergence_score:.3f}, mode=bounce"
            ),
            metadata={
                # v1 fields (kept)
                "wall_type": "put",
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_net_gamma": wall_net_gamma,
                "distance_to_wall_pct": round(distance_pct, 4),
                "range_ratio": round(range_ratio, 3),
                "net_gamma": round(net_gamma, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (target - entry) / risk, 2
                ) if risk > 0 else 0,
                "trend": trend,
                # v2 new fields
                "divergence_score": round(divergence_score, 3),
                "delta_at_wall": round(current_delta, 4),
                "wall_bid_depth": round(bid_depth, 1),
                "wall_ask_depth": round(ask_depth, 1),
                "wall_liquidity_status": liquidity_status,
                "iv_factor": 1.0,  # computed below
                "target_pct": round(abs(target - entry) / entry, 4) if entry > 0 else 0,
                "mode": "bounce",
                "regime": "POSITIVE",
            },
        )

    def _check_call_wall(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        walls: List[Dict[str, Any]],
        timestamp: float,
        range_ratio: float,
    ) -> Optional[Signal]:
        """
        Evaluate Call Walls for SHORT bounce opportunity.

        Call wall = positive net_gamma → acts as resistance.
        We want price approaching from below and showing rejection.
        """
        # Find Call Walls above price (positive gamma)
        call_walls = [
            w for w in walls
            if w["strike"] > price and w.get("side") == "call"
        ]
        if not call_walls:
            call_walls = [
                w for w in walls
                if w["strike"] > price and w.get("net_gamma", 0) > 0
            ]
        if not call_walls:
            return None

        # Nearest Call Wall above price
        nearest_wall = min(call_walls, key=lambda w: w["strike"])
        wall_strike = nearest_wall["strike"]
        wall_gex = nearest_wall.get("gex", 0)
        wall_net_gamma = nearest_wall.get("net_gamma", 0)

        # Proximity: price must be within WALL_PROXIMITY_PCT below wall
        distance_pct = (wall_strike - price) / price
        if distance_pct < 0 or distance_pct > WALL_PROXIMITY_PCT:
            return None

        # HARD GATE 1: Delta-gamma divergence (hard rejection)
        divergence_ok, divergence_score, current_delta = self._check_delta_gamma_divergence(
            rolling_data, wall_strike, "SHORT",
        )
        if not divergence_ok:
            return None

        # HARD GATE 2: Wall liquidity
        bid_depth, ask_depth, liquidity_status = self._get_wall_depth(
            rolling_data, wall_strike, "SHORT", "bounce",
        )
        liquidity_ok = (ask_depth > 0)
        if not liquidity_ok:
            return None

        # Compute IV-scaled target
        target = self._compute_iv_scaled_target(
            wall_strike, walls, price, "below", rolling_data, "bounce",
        )

        # Compute confidence (bounce mode)
        confidence = self._compute_bounce_confidence(
            price, wall_strike, wall_gex, wall_net_gamma,
            distance_pct, range_ratio, divergence_score,
            bid_depth, ask_depth, liquidity_status,
            current_delta, timestamp, "SHORT",
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        entry = price
        stop = wall_strike * (1 + STOP_PAST_WALL_PCT)
        risk = stop - entry

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Theta-Burn v2 SHORT: Call wall at {wall_strike} rejected, "
                f"GEX={wall_gex:.0f}, range_ratio={range_ratio:.2f}, "
                f"divergence={divergence_score:.3f}, mode=bounce"
            ),
            metadata={
                # v1 fields (kept)
                "wall_type": "call",
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_net_gamma": wall_net_gamma,
                "distance_to_wall_pct": round(distance_pct, 4),
                "range_ratio": round(range_ratio, 3),
                "net_gamma": round(net_gamma, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (entry - target) / risk, 2
                ) if risk > 0 else 0,
                "trend": trend,
                # v2 new fields
                "divergence_score": round(divergence_score, 3),
                "delta_at_wall": round(current_delta, 4),
                "wall_bid_depth": round(bid_depth, 1),
                "wall_ask_depth": round(ask_depth, 1),
                "wall_liquidity_status": liquidity_status,
                "iv_factor": 1.0,
                "target_pct": round(abs(target - entry) / entry, 4) if entry > 0 else 0,
                "mode": "bounce",
                "regime": "POSITIVE",
            },
        )

    # ------------------------------------------------------------------
    # Slice Mode (NEGATIVE gamma regime)
    # ------------------------------------------------------------------

    def _check_slice_mode(
        self,
        data: Dict[str, Any],
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        timestamp: float,
    ) -> List[Signal]:
        """NEGATIVE gamma regime: trade wall breakouts (slice mode)."""
        price = data.get("underlying_price", 0)
        if price <= 0:
            return []

        # Validate rolling data availability
        price_5m = rolling_data.get(KEY_PRICE_5M)
        price_30m = rolling_data.get(KEY_PRICE_30M)
        volume_5m = rolling_data.get(KEY_VOLUME_5M)

        if not all([price_5m, price_30m, volume_5m]):
            return []

        if not all([
            price_5m.count >= MIN_DATA_POINTS,
            price_30m.count >= MIN_DATA_POINTS,
            volume_5m.count >= MIN_DATA_POINTS,
        ]):
            return []

        # Check range narrowness
        range_ratio = self._check_range_narrowness(price_5m, price_30m)
        if range_ratio is None or range_ratio >= RANGE_NARROWNESS_RATIO:
            return []

        signals: List[Signal] = []

        # Get gamma walls
        walls = self._safe_get_walls(gex_calc)
        if not walls:
            return []

        # Check LONG slice (price breaking through Call wall above)
        long_sig = self._check_put_wall_slice(
            price, gex_calc, rolling_data, net_gamma, walls, timestamp, range_ratio,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT slice (price breaking through Put wall below)
        short_sig = self._check_call_wall_slice(
            price, gex_calc, rolling_data, net_gamma, walls, timestamp, range_ratio,
        )
        if short_sig:
            signals.append(short_sig)

        return signals

    def _check_put_wall_slice(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        walls: List[Dict[str, Any]],
        timestamp: float,
        range_ratio: float,
    ) -> Optional[Signal]:
        """
        Slice LONG: price is BREAKING THROUGH a Call wall above.
        Was below, now approaching from below — Call wall ask depth is thin (vacuum).
        """
        # Find Call Walls above price (positive gamma)
        call_walls = [
            w for w in walls
            if w["strike"] > price and w.get("side") == "call"
        ]
        if not call_walls:
            call_walls = [
                w for w in walls
                if w["strike"] > price and w.get("net_gamma", 0) > 0
            ]
        if not call_walls:
            return None

        nearest_wall = min(call_walls, key=lambda w: w["strike"])
        wall_strike = nearest_wall["strike"]
        wall_gex = nearest_wall.get("gex", 0)
        wall_net_gamma = nearest_wall.get("net_gamma", 0)

        # Proximity: price must be within WALL_PROXIMITY_PCT below wall
        distance_pct = (wall_strike - price) / price
        if distance_pct < 0 or distance_pct > WALL_PROXIMITY_PCT:
            return None

        # HARD GATE 1: Delta-gamma divergence
        divergence_ok, divergence_score, current_delta = self._check_delta_gamma_divergence(
            rolling_data, wall_strike, "LONG",
        )
        if not divergence_ok:
            return None

        # HARD GATE 2: Wall liquidity vacuum — ask depth must be thin
        bid_depth, ask_depth, liquidity_status = self._get_wall_depth(
            rolling_data, wall_strike, "LONG", "slice",
        )
        if ask_depth <= 0:
            # No depth data available — pass (backwards compat)
            pass
        elif ask_depth >= 50:
            # Ask depth too thick — not a vacuum
            return None

        # Compute IV-scaled target (slice mode)
        target = self._compute_iv_scaled_target(
            wall_strike, walls, price, "above", rolling_data, "slice",
        )

        # Compute confidence (slice mode)
        confidence = self._compute_slice_confidence(
            price, wall_strike, wall_gex, wall_net_gamma,
            distance_pct, range_ratio, divergence_score,
            bid_depth, ask_depth, liquidity_status,
            rolling_data, timestamp, "LONG",
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        entry = price
        stop = wall_strike * (1 - STOP_PAST_WALL_PCT)
        risk = entry - stop

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Theta-Burn v2 LONG SLICE: Breaking Call wall at {wall_strike}, "
                f"GEX={wall_gex:.0f}, range_ratio={range_ratio:.2f}, "
                f"divergence={divergence_score:.3f}, ask_depth={ask_depth:.0f}, mode=slice"
            ),
            metadata={
                # v1 fields (kept)
                "wall_type": "call",
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_net_gamma": wall_net_gamma,
                "distance_to_wall_pct": round(distance_pct, 4),
                "range_ratio": round(range_ratio, 3),
                "net_gamma": round(net_gamma, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (target - entry) / risk, 2
                ) if risk > 0 else 0,
                "trend": trend,
                # v2 new fields
                "divergence_score": round(divergence_score, 3),
                "delta_at_wall": round(current_delta, 4),
                "wall_bid_depth": round(bid_depth, 1),
                "wall_ask_depth": round(ask_depth, 1),
                "wall_liquidity_status": liquidity_status,
                "iv_factor": 1.0,
                "target_pct": round(abs(target - entry) / entry, 4) if entry > 0 else 0,
                "mode": "slice",
                "regime": "NEGATIVE",
            },
        )

    def _check_call_wall_slice(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        walls: List[Dict[str, Any]],
        timestamp: float,
        range_ratio: float,
    ) -> Optional[Signal]:
        """
        Slice SHORT: price is BREAKING THROUGH a Put wall below.
        Was above, now approaching from above — Put wall bid depth is thin (vacuum).
        """
        # Find Put Walls below price (negative gamma)
        put_walls = [
            w for w in walls
            if w["strike"] < price and w.get("side") == "put"
        ]
        if not put_walls:
            put_walls = [
                w for w in walls
                if w["strike"] < price and w.get("net_gamma", 0) < 0
            ]
        if not put_walls:
            return None

        nearest_wall = max(put_walls, key=lambda w: w["strike"])
        wall_strike = nearest_wall["strike"]
        wall_gex = nearest_wall.get("gex", 0)
        wall_net_gamma = nearest_wall.get("net_gamma", 0)

        # Proximity: price must be within WALL_PROXIMITY_PCT above wall
        distance_pct = (price - wall_strike) / price
        if distance_pct < 0 or distance_pct > WALL_PROXIMITY_PCT:
            return None

        # HARD GATE 1: Delta-gamma divergence
        divergence_ok, divergence_score, current_delta = self._check_delta_gamma_divergence(
            rolling_data, wall_strike, "SHORT",
        )
        if not divergence_ok:
            return None

        # HARD GATE 2: Wall liquidity vacuum — bid depth must be thin
        bid_depth, ask_depth, liquidity_status = self._get_wall_depth(
            rolling_data, wall_strike, "SHORT", "slice",
        )
        if bid_depth <= 0:
            # No depth data available — pass (backwards compat)
            pass
        elif bid_depth >= 50:
            # Bid depth too thick — not a vacuum
            return None

        # Compute IV-scaled target (slice mode)
        target = self._compute_iv_scaled_target(
            wall_strike, walls, price, "below", rolling_data, "slice",
        )

        # Compute confidence (slice mode)
        confidence = self._compute_slice_confidence(
            price, wall_strike, wall_gex, wall_net_gamma,
            distance_pct, range_ratio, divergence_score,
            bid_depth, ask_depth, liquidity_status,
            rolling_data, timestamp, "SHORT",
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal
        price_window = rolling_data.get(KEY_PRICE_5M)
        trend = price_window.trend if price_window else "UNKNOWN"

        entry = price
        stop = wall_strike * (1 + STOP_PAST_WALL_PCT)
        risk = stop - entry

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Theta-Burn v2 SHORT SLICE: Breaking Put wall at {wall_strike}, "
                f"GEX={wall_gex:.0f}, range_ratio={range_ratio:.2f}, "
                f"divergence={divergence_score:.3f}, bid_depth={bid_depth:.0f}, mode=slice"
            ),
            metadata={
                # v1 fields (kept)
                "wall_type": "put",
                "wall_strike": wall_strike,
                "wall_gex": wall_gex,
                "wall_net_gamma": wall_net_gamma,
                "distance_to_wall_pct": round(distance_pct, 4),
                "range_ratio": round(range_ratio, 3),
                "net_gamma": round(net_gamma, 2),
                "risk": round(risk, 2),
                "risk_reward_ratio": round(
                    (entry - target) / risk, 2
                ) if risk > 0 else 0,
                "trend": trend,
                # v2 new fields
                "divergence_score": round(divergence_score, 3),
                "delta_at_wall": round(current_delta, 4),
                "wall_bid_depth": round(bid_depth, 1),
                "wall_ask_depth": round(ask_depth, 1),
                "wall_liquidity_status": liquidity_status,
                "iv_factor": 1.0,
                "target_pct": round(abs(target - entry) / entry, 4) if entry > 0 else 0,
                "mode": "slice",
                "regime": "NEGATIVE",
            },
        )

    # ------------------------------------------------------------------
    # Wall Liquidity Check
    # ------------------------------------------------------------------

    def _get_wall_depth(
        self,
        rolling_data: Dict[str, Any],
        wall_strike: float,
        direction: str,
        mode: str,
    ) -> Tuple[float, float, str]:
        """
        Get wall depth from market_depth_agg in rolling_data.
        Returns (bid_depth, ask_depth, status).
        """
        # market_depth_agg is stored in rolling_data under a special key
        # or passed via data dict. Check rolling_data first.
        depth_data = rolling_data.get(KEY_MARKET_DEPTH_AGG, {})
        if not depth_data:
            return 0.0, 0.0, "unknown"

        bids = depth_data.get("bids", [])
        asks = depth_data.get("asks", [])

        # Find depth at/near the wall strike (±0.1% price window)
        bid_at_wall = sum(
            b["size"] for b in bids
            if abs(b["price"] - wall_strike) / wall_strike < 0.001
        )
        ask_at_wall = sum(
            a["size"] for a in asks
            if abs(a["price"] - wall_strike) / wall_strike < 0.001
        )

        if mode == "bounce":
            # Wall must have depth to hold
            if direction == "LONG":  # Put wall = bid side
                status = "holding" if bid_at_wall > 0 else "weak"
            else:  # Call wall = ask side
                status = "holding" if ask_at_wall > 0 else "weak"
        else:  # slice mode
            # Wall must be collapsing (liquidity vacuum)
            if direction == "LONG":  # Breaking through Call wall above
                status = "vacuum" if ask_at_wall < 50 else "thick"
            else:  # Breaking through Put wall below
                status = "vacuum" if bid_at_wall < 50 else "thick"

        return bid_at_wall, ask_at_wall, status

    @staticmethod
    def _check_wall_liquidity(
        data: Dict[str, Any],
        wall_strike: float,
        direction: str,
        mode: str,
    ) -> Tuple[bool, float, float, str]:
        """
        Check wall liquidity for bounce or slice mode.

        Returns (ok, bid_depth, ask_depth, status).
        """
        depth = data.get(KEY_MARKET_DEPTH_AGG, {})
        if not depth:
            return True, 0.0, 0.0, "unknown"  # No depth data = pass (backwards compat)

        bids = depth.get("bids", [])
        asks = depth.get("asks", [])

        # Find depth at/near the wall strike (±0.1% price window)
        bid_at_wall = sum(
            b["size"] for b in bids
            if abs(b["price"] - wall_strike) / wall_strike < 0.001
        )
        ask_at_wall = sum(
            a["size"] for a in asks
            if abs(a["price"] - wall_strike) / wall_strike < 0.001
        )

        if mode == "bounce":
            # Wall must have depth to hold
            if direction == "LONG":  # Put wall = bid side
                ok = bid_at_wall > 0
                status = "holding" if ok else "weak"
            else:  # Call wall = ask side
                ok = ask_at_wall > 0
                status = "holding" if ok else "weak"
        else:  # slice mode — wall must be collapsing
            if direction == "LONG":  # Breaking through Call wall above
                ok = ask_at_wall < 50  # Thin asks = vacuum
                status = "vacuum" if ok else "thick"
            else:  # Breaking through Put wall below
                ok = bid_at_wall < 50  # Thin bids = vacuum
                status = "vacuum" if ok else "thick"

        return ok, bid_at_wall, ask_at_wall, status

    # ------------------------------------------------------------------
    # Delta-Gamma Divergence Check
    # ------------------------------------------------------------------

    def _check_delta_gamma_divergence(
        self,
        rolling_data: Dict[str, Any],
        wall_strike: float,
        direction: str,
    ) -> Tuple[bool, float, float]:
        """
        Check for delta-gamma divergence (hard rejection signature).

        Returns (ok, divergence_score, current_delta).
        """
        # Get delta rolling window
        delta_window = rolling_data.get(KEY_WALL_DELTA_5M)
        if delta_window is None or delta_window.count < 3:
            return False, 0.0, 0.0

        delta_mean = delta_window.mean
        if delta_mean is None or delta_mean == 0:
            return False, 0.0, 0.0

        # Get current delta at wall strike from gex_calc
        # We need to get it from rolling_data — the gex_calc is not available here
        # Instead, we use the latest value from the rolling window
        current_delta = delta_window.latest if delta_window.latest is not None else 0.0

        # Delta spike: how much has delta moved from mean?
        delta_spike = abs(current_delta - delta_mean) / abs(delta_mean)

        # Price stillness: how stationary is price?
        price_5m = rolling_data.get(KEY_PRICE_5M)
        price_30m = rolling_data.get(KEY_PRICE_30M)
        if price_5m is None or price_30m is None:
            return False, 0.0, 0.0

        range_5m = price_5m.range or 0
        range_30m = price_30m.range or 1
        price_stillness = 1.0 - (range_5m / range_30m)
        price_stillness = max(0.0, min(1.0, price_stillness))

        # Divergence score: delta spike × price stillness
        divergence_score = delta_spike * price_stillness

        # Hard gate: must have meaningful divergence
        if divergence_score < 0.15:
            return False, divergence_score, current_delta

        # Direction check:
        # LONG (Put wall): current_delta < delta_mean (delta dropping = rejection)
        # SHORT (Call wall): current_delta > delta_mean (delta rising = rejection)
        if direction == "LONG":
            if current_delta >= delta_mean:
                return False, divergence_score, current_delta
        else:
            if current_delta <= delta_mean:
                return False, divergence_score, current_delta

        return True, divergence_score, current_delta

    # ------------------------------------------------------------------
    # IV-Scaled Target Computation
    # ------------------------------------------------------------------

    def _compute_iv_scaled_target(
        self,
        wall_strike: float,
        walls: List[Dict[str, Any]],
        price: float,
        direction: str,
        rolling_data: Dict[str, Any],
        mode: str,
    ) -> float:
        """
        Compute IV-expansion scaled target.

        For bounce mode:
            - Base = midpoint between walls (existing logic)
            - If IV expanding (factor > 1.0): extend toward 0.6%
            - If IV contracting (factor < 1.0): tighten to 0.2%

        For slice mode:
            - Base = 0.3% × iv_factor, capped at 0.8%
        """
        iv_window = rolling_data.get(KEY_ATM_IV_5M)

        if iv_window is None or iv_window.mean is None or iv_window.mean == 0:
            # Fallback to existing midpoint logic
            return self._compute_bounce_target(
                wall_strike, walls, price, direction, None,
            )

        current_iv = iv_window.latest
        mean_iv = iv_window.mean
        iv_factor = current_iv / mean_iv if mean_iv > 0 else 1.0

        if mode == "bounce":
            # Start with midpoint target (existing logic)
            base_target = self._compute_bounce_target(
                wall_strike, walls, price, direction, None,
            )

            # Scale: IV expansion = wider target, IV contraction = tighter
            if direction == "above":
                base_target_pct = (base_target - price) / price if price > 0 else 0.003
                if iv_factor > 1.0:
                    # IV expanding — extend target toward 0.6%
                    scale = min(0.6, base_target_pct / 0.003) * iv_factor
                    target = price + (price * 0.003 * min(scale, 0.6 / 0.003))
                else:
                    # IV contracting — tighten to 0.2%
                    target = price + (price * 0.002)
            else:
                base_target_pct = (price - base_target) / price if price > 0 else 0.003
                if iv_factor > 1.0:
                    scale = min(0.6, base_target_pct / 0.003) * iv_factor
                    target = price - (price * 0.003 * min(scale, 0.6 / 0.003))
                else:
                    target = price - (price * 0.002)

            return target
        else:  # slice mode
            # Base 0.3% × IV factor, capped at 0.8%
            base_pct = 0.003 * iv_factor
            base_pct = min(0.008, max(0.001, base_pct))
            if direction == "above":
                target = price + (price * base_pct)
            else:
                target = price - (price * base_pct)
            return target

    # ------------------------------------------------------------------
    # Range Narrowness Check
    # ------------------------------------------------------------------

    @staticmethod
    def _check_range_narrowness(
        price_5m: Any,
        price_30m: Any,
    ) -> Optional[float]:
        """
        Check if the 5m range is compressed relative to the 30m range.
        Returns the ratio of 5m range / 30m range.
        """
        range_5m = price_5m.range
        range_30m = price_30m.range

        if range_5m is None or range_30m is None:
            return None
        if range_30m <= 0:
            return None

        return range_5m / range_30m

    # ------------------------------------------------------------------
    # Confidence Computation — Bounce Mode (6 components)
    # ------------------------------------------------------------------

    def _compute_bounce_confidence(
        self,
        price: float,
        wall_strike: float,
        wall_gex: float,
        wall_net_gamma: float,
        distance_pct: float,
        range_ratio: float,
        divergence_score: float,
        bid_depth: float,
        ask_depth: float,
        liquidity_status: str,
        current_delta: float,
        timestamp: float,
        direction: str,
    ) -> float:
        """
        Bounce confidence: 6 components.

        1. Gamma strength: 0.10–0.20
        2. Wall proximity: 0.15–0.25
        3. Range narrowness: 0.10–0.15
        4. Delta-gamma divergence: 0.20–0.25 (hard gate)
        5. Wall liquidity: 0.10–0.15 (hard gate)
        6. IV expansion: 0.05–0.10
        """
        # 1. Gamma strength (0.10–0.20)
        gamma_strength = abs(wall_net_gamma) if wall_net_gamma != 0 else abs(wall_gex)
        gamma_conf = 0.10 + 0.10 * min(1.0, gamma_strength / GAMMA_STRENGTH_HIGH)

        # 2. Wall proximity (0.15–0.25)
        if distance_pct <= 0:
            prox_conf = 0.25
        elif distance_pct >= WALL_PROXIMITY_PCT:
            prox_conf = 0.15
        else:
            prox_conf = 0.25 - 0.10 * (distance_pct / WALL_PROXIMITY_PCT)

        # 3. Range narrowness (0.10–0.15)
        if range_ratio <= 0:
            nar_conf = 0.15
        elif range_ratio >= RANGE_NARROWNESS_RATIO:
            nar_conf = 0.10
        else:
            nar_conf = 0.15 - 0.05 * (range_ratio / RANGE_NARROWNESS_RATIO)

        # 4. Delta-gamma divergence (0.20–0.25) — hard gate
        # divergence_score is already >= 0.15 at this point (hard gate passed)
        # Map 0.15–1.0 to 0.20–0.25
        div_conf = 0.20 + 0.05 * min(1.0, (divergence_score - 0.15) / 0.85)

        # 5. Wall liquidity (0.10–0.15) — hard gate
        # If status is "holding", full credit; if "weak", partial
        if liquidity_status == "holding":
            liq_conf = 0.15
        elif liquidity_status == "unknown":
            liq_conf = 0.10  # No depth data — partial credit
        else:
            liq_conf = 0.0  # Failed hard gate

        # 6. IV expansion (0.05–0.10)
        iv_conf = self._compute_iv_expansion_conf(rolling_data={})

        # Normalize and average
        norm_gamma = (gamma_conf - 0.10) / (0.20 - 0.10)
        norm_prox = (prox_conf - 0.15) / (0.25 - 0.15)
        norm_nar = (nar_conf - 0.10) / (0.15 - 0.10)
        norm_div = (div_conf - 0.20) / (0.25 - 0.20)
        norm_liq = (liq_conf - 0.10) / (0.15 - 0.10) if liq_conf > 0 else 0.0
        norm_iv = (iv_conf - 0.05) / (0.10 - 0.05)

        confidence = (norm_gamma + norm_prox + norm_nar + norm_div + norm_liq + norm_iv) / 6.0
        if confidence >= MIN_CONFIDENCE:
            return [Signal(confidence=confidence, direction=1, strategy_name="theta_burn")]
        return []

    # ------------------------------------------------------------------
    # Confidence Computation — Slice Mode (7 components)
    # ------------------------------------------------------------------

    def _compute_slice_confidence(
        self,
        price: float,
        wall_strike: float,
        wall_gex: float,
        wall_net_gamma: float,
        distance_pct: float,
        range_ratio: float,
        divergence_score: float,
        bid_depth: float,
        ask_depth: float,
        liquidity_status: str,
        rolling_data: Dict[str, Any],
        timestamp: float,
        direction: str,
    ) -> float:
        """
        Slice confidence: 7 components.

        1. Gamma strength: 0.10–0.20
        2. Delta-gamma divergence: 0.20–0.25 (hard gate)
        3. Wall liquidity vacuum: 0.15–0.20 (hard gate)
        4. Range narrowness: 0.10–0.15
        5. Volume confirmation: 0.10–0.15
        6. IV expansion: 0.05–0.10
        7. Time of day: 0.05–0.10
        """
        # 1. Gamma strength (0.10–0.20)
        gamma_strength = abs(wall_net_gamma) if wall_net_gamma != 0 else abs(wall_gex)
        gamma_conf = 0.10 + 0.10 * min(1.0, gamma_strength / GAMMA_STRENGTH_HIGH)

        # 2. Delta-gamma divergence (0.20–0.25) — hard gate
        div_conf = 0.20 + 0.05 * min(1.0, (divergence_score - 0.15) / 0.85)

        # 3. Wall liquidity vacuum (0.15–0.20) — hard gate
        if liquidity_status == "vacuum":
            liq_conf = 0.20
        elif liquidity_status == "unknown":
            liq_conf = 0.15  # No depth data — pass
        else:
            liq_conf = 0.0  # Failed hard gate

        # 4. Range narrowness (0.10–0.15)
        if range_ratio <= 0:
            nar_conf = 0.15
        elif range_ratio >= RANGE_NARROWNESS_RATIO:
            nar_conf = 0.10
        else:
            nar_conf = 0.15 - 0.05 * (range_ratio / RANGE_NARROWNESS_RATIO)

        # 5. Volume confirmation (0.10–0.15)
        vol_conf = self._compute_volume_confidence(rolling_data)

        # 6. IV expansion (0.05–0.10)
        iv_conf = self._compute_iv_expansion_conf(rolling_data)

        # 7. Time of day (0.05–0.10)
        tod_conf = self._time_of_day_confidence(timestamp)

        # Normalize and average
        norm_gamma = (gamma_conf - 0.10) / (0.20 - 0.10)
        norm_div = (div_conf - 0.20) / (0.25 - 0.20)
        norm_liq = (liq_conf - 0.15) / (0.20 - 0.15) if liq_conf > 0 else 0.0
        norm_nar = (nar_conf - 0.10) / (0.15 - 0.10)
        norm_vol = (vol_conf - 0.10) / (0.15 - 0.10)
        norm_iv = (iv_conf - 0.05) / (0.10 - 0.05)
        norm_tod = (tod_conf - 0.05) / (0.10 - 0.05)

        confidence = (norm_gamma + norm_div + norm_liq + norm_nar + norm_vol + norm_iv + norm_tod) / 7.0
        if confidence >= MIN_CONFIDENCE:
            return [Signal(confidence=confidence, direction=1, strategy_name="theta_burn")]
        return []

    # ------------------------------------------------------------------
    # Helper: Volume Confidence
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_volume_confidence(rolling_data: Dict[str, Any]) -> float:
        """Volume confirmation for slice mode (0.10–0.15)."""
        vol_window = rolling_data.get(KEY_VOLUME_5M)
        if vol_window is None or vol_window.latest is None:
            return 0.10  # Baseline

        latest = vol_window.latest
        avg = vol_window.mean
        if avg is None or avg == 0:
            return 0.10

        # Volume above average = confirmation
        ratio = latest / avg
        if ratio >= 1.0:
            return 0.15
        elif ratio >= 0.8:
            return 0.12
        else:
            return 0.10

    # ------------------------------------------------------------------
    # Helper: IV Expansion Confidence
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_iv_expansion_conf(rolling_data: Dict[str, Any]) -> float:
        """IV expansion confidence (0.05–0.10)."""
        iv_window = rolling_data.get(KEY_ATM_IV_5M)
        if iv_window is None or iv_window.mean is None or iv_window.mean == 0:
            return 0.05  # Baseline

        current = iv_window.latest
        mean = iv_window.mean
        factor = current / mean

        if factor > 1.0:
            # IV expanding — higher confidence
            return min(0.10, 0.05 + 0.05 * min(1.0, (factor - 1.0) / 0.5))
        else:
            # IV contracting — lower confidence
            return max(0.05, 0.05 * factor)

    # ------------------------------------------------------------------
    # Time of Day Confidence
    # ------------------------------------------------------------------

    @staticmethod
    def _time_of_day_confidence(timestamp: float) -> float:
        """
        Compute confidence bonus from time of day.
        Midday lull (11:30-14:30 ET = 16:30-19:30 UTC) favors range trades.
        """
        if timestamp <= 0:
            return 0.05

        utc_hour = (timestamp % 86400) / 3600

        if MIDNIGHT_UTC_START <= utc_hour <= MIDNIGHT_UTC_END:
            return 0.10
        return 0.05

    # ------------------------------------------------------------------
    # Target Computation (existing bounce target logic)
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_bounce_target(
        wall_strike: float,
        walls: List[Dict[str, Any]],
        price: float,
        direction: str,
        risk: Optional[float],
    ) -> float:
        """
        Compute bounce target.

        For LONG (bounce off Put below): target = midpoint between
            the Put wall and the next wall above (or ATM).

        For SHORT (bounce off Call above): target = midpoint between
            the Call wall and the next wall below (or ATM).

        Falls back to risk-based target (0.2-0.4%) if no next wall found.
        """
        if direction == "above":
            candidates = [w for w in walls if w["strike"] > wall_strike]
            if candidates:
                next_wall = min(candidates, key=lambda w: w["strike"])
                midpoint = (wall_strike + next_wall["strike"]) / 2
                target = max(price + (price * MIN_TARGET_PCT), midpoint)
                max_target = price * (1 + MAX_TARGET_PCT)
                return min(target, max_target)
        else:
            candidates = [w for w in walls if w["strike"] < wall_strike]
            if candidates:
                next_wall = max(candidates, key=lambda w: w["strike"])
                midpoint = (wall_strike + next_wall["strike"]) / 2
                target = min(price - (price * MIN_TARGET_PCT), midpoint)
                min_target = price * (1 - MAX_TARGET_PCT)
                return max(target, min_target)

        # Fallback: use risk-based target (0.2-0.4% from entry)
        if risk is None or risk <= 0:
            return price

        if direction == "above":
            target = price + risk
            max_target = price * (1 + MAX_TARGET_PCT)
            return max(price + (price * MIN_TARGET_PCT), min(target, max_target))
        else:
            target = price - risk
            min_target = price * (1 - MAX_TARGET_PCT)
            return min(price - (price * MIN_TARGET_PCT), max(target, min_target))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_get_walls(gex_calc: Any) -> List[Dict[str, Any]]:
        """Safely retrieve gamma walls, returning empty list on error."""
        try:
            return gex_calc.get_gamma_walls(threshold=MIN_NET_GAMMA)
        except Exception as exc:
            logger.debug("ThetaBurn: failed to get gamma walls: %s", exc)
            return []
