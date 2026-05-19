"""
strategies/layer1/magnet_accelerate.py — Magnet & Accelerate

Two-phase strategy centered on the highest-GEX strike (the "magnet").

Phase 1 — Magnet Pull (bidirectional in POSITIVE regime):
    When net gamma is positive, dealer hedging pulls price toward the magnet:
    - Price below magnet → LONG toward magnet (dealer hedging pulls price up)
    - Price above magnet → SHORT toward magnet (dealer hedging pulls price down)

Phase 2 — Acceleration (NEGATIVE regime, bidirectional):
    When price breaks through the magnet and cumulative gamma
    turns negative, enter in the breakout direction.
    Dealer hedging accelerates the move.

Entry:
    - Phase 1: LONG when price < magnet (positive gamma), SHORT when price > magnet (positive gamma)
    - Phase 2: LONG or SHORT on magnet breakout + negative gamma regime

Exit:
    - Phase 1: Exit within 0.3% of magnet or when GEX weakens
    - Phase 2: Trail aggressively (stop = 1% beyond magnet)

Confidence factors:
    - Distance to magnet (closer = higher confidence for Phase 1)
    - Net gamma magnitude (stronger = higher confidence)
    - Gamma acceleration (for Phase 2)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import KEY_PRICE_5M
from strategies.volume_filter import VolumeFilter
from strategies.utils import normalize_confidence

logger = logging.getLogger("Syngex.Strategies.MagnetAccelerate")

# ---------------------------------------------------------------------------
# Default Fallback Constants
# These are used ONLY if config/strategies.yaml is missing values.
# The actual values should be configured in strategies.yaml under
# layer1.magnet_accelerate.params
# ---------------------------------------------------------------------------

DEFAULT_MIN_MAGNET_GEX = 500000       # Minimum |normalized GEX| to be a magnet
DEFAULT_MAGNET_EXIT_PCT = 0.003       # 0.3% — exit within this % of magnet
DEFAULT_BREAKOUT_PCT = 0.002          # 0.2% — price must be this far past magnet to breakout
DEFAULT_MAX_BREAKOUT_PCT = 0.02       # 2% — max distance past magnet (no chasing)
DEFAULT_TRAIL_STOP_PCT = 0.01         # 1% — trailing stop for Phase 2
DEFAULT_TARGET_RISK_MULT = 1.5        # Minimum 1.5× risk for target distance
DEFAULT_MIN_CONFIDENCE = 0.65         # Minimum confidence to emit signal


class MagnetAccelerate(BaseStrategy):
    """
    Two-phase strategy: magnet pull + gamma-accelerated breakout.

    The magnet is the strike with the highest |net_gamma|.
    Positive gamma regime = magnet pulls price toward it.
    Negative gamma regime after breakout = acceleration phase.
    """

    strategy_id = "magnet_accelerate"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state and return magnet/acceleration signals.

        No cooldown — every tick is evaluated independently.
        Signals include a max_hold_minutes metadata field (60 min) for
        the engine to enforce hold-time limits.

        Returns empty list when magnet is not identifiable or conditions
        are not met.
        """
        # Apply config params from data dict
        self._apply_params(data)

        # Extract params with fallback defaults
        min_magnet_gex = self._params.get('min_magnet_gex', DEFAULT_MIN_MAGNET_GEX)
        magnet_exit_pct = self._params.get('magnet_exit_pct', DEFAULT_MAGNET_EXIT_PCT)
        breakout_pct = self._params.get('breakout_pct', DEFAULT_BREAKOUT_PCT)
        max_breakout_pct = self._params.get('max_breakout_pct', DEFAULT_MAX_BREAKOUT_PCT)
        trail_stop_pct = self._params.get('trail_stop_pct', DEFAULT_TRAIL_STOP_PCT)
        target_risk_mult = self._params.get('target_risk_mult', DEFAULT_TARGET_RISK_MULT)
        min_confidence = self._params.get('min_confidence', DEFAULT_MIN_CONFIDENCE)

        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        regime = data.get("regime", "")
        net_gamma = data.get("net_gamma", 0)

        # Global volume filter — Phase 1 only (Phase 2 breakout is unaffected)
        vol_check = VolumeFilter.evaluate(rolling_data, min_confidence)
        if not vol_check["recommended"]:
            # Volume too low — suppress Phase 1 signals only
            # Phase 2 (breakout) signals still fire below
            pass  # We'll gate Phase 1 explicitly below

        # Find the magnet strike (highest |net_gamma|)
        magnet_strike = self._find_magnet(gex_calc)
        if magnet_strike is None:
            return []

        magnet_bucket = gex_calc._ladder.get(magnet_strike)
        if magnet_bucket is None:
            return []

        # Use normalized GEX for consistent scale with get_gamma_walls()
        magnet_gex = abs(magnet_bucket.normalized_gamma() * 100 * underlying_price)
        if magnet_gex < min_magnet_gex:
            return []

        signals: List[Signal] = []

        # Phase 1: Magnet pull (bidirectional in POSITIVE regime)
        # Gate with volume filter — low volume = no mean-reversion signals
        if regime == "POSITIVE" and net_gamma > 0 and vol_check["recommended"]:
            # LONG: price below magnet → LONG toward magnet
            if underlying_price < magnet_strike:
                sig = self._phase1_pull(
                    magnet_strike, magnet_gex, underlying_price, net_gamma, rolling_data, Direction.LONG,
                    min_confidence
                )
                if sig:
                    signals.append(sig)
            # SHORT: price above magnet → SHORT toward magnet
            elif underlying_price > magnet_strike:
                sig = self._phase1_pull(
                    magnet_strike, magnet_gex, underlying_price, net_gamma, rolling_data, Direction.SHORT,
                    min_confidence
                )
                if sig:
                    signals.append(sig)

        # Phase 2: Acceleration breakout (NEGATIVE regime only)
        # Phase 2 is unaffected by volume filter — breakout signals are high-conviction
        if regime == "NEGATIVE":
            sig = self._phase2_accelerate(
                magnet_strike, underlying_price, net_gamma, regime, rolling_data,
                breakout_pct, max_breakout_pct, trail_stop_pct, target_risk_mult, min_confidence
            )
            if sig:
                signals.append(sig)

        return signals

    # ------------------------------------------------------------------
    # Phase 1: Magnet Pull
    # ------------------------------------------------------------------

    def _phase1_pull(
        self,
        magnet_strike: float,
        magnet_gex: float,
        price: float,
        net_gamma: float,
        rolling_data: Dict[str, Any],
        direction: Direction,
        min_confidence: float,
    ) -> Optional[Signal]:
        """
        Phase 1: Bidirectional magnet pull in positive gamma regime.

        Direction.LONG:  price below magnet → LONG toward magnet
                        (dealer hedging pulls price up)
        Direction.SHORT: price above magnet → SHORT toward magnet
                        (dealer hedging pulls price down)
        """
        if direction == Direction.LONG:
            if price >= magnet_strike:
                return None
            distance_pct = (magnet_strike - price) / price
        else:
            # Direction.SHORT
            if price <= magnet_strike:
                return None
            distance_pct = (price - magnet_strike) / price

        if distance_pct < 0.003:
            return None  # Already at magnet — not a pull
        if distance_pct > 0.02:
            # More than 2% away — not in magnet range
            return None

        price_window = rolling_data.get(KEY_PRICE_5M)
        momentum = self._price_momentum(rolling_data)

        # Confidence: closer to magnet + stronger gamma + good momentum
        confidence = self._phase1_confidence(distance_pct, magnet_gex, net_gamma, momentum)
        if confidence < min_confidence:
            return None

        # Target: magnet strike (exit within magnet_exit_pct of it)
        target = magnet_strike
        # Stop: 1% beyond entry (opposite direction)
        stop = price * (1 + 0.01) if direction == Direction.SHORT else price * (1 - 0.01)

        risk = abs(price - stop)
        if risk <= 0:
            return None

        return Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Magnet pull {'SHORT' if direction == Direction.SHORT else 'LONG'}: "
                   f"price {price:.2f} {'above' if direction == Direction.SHORT else 'below'} "
                   f"magnet {magnet_strike:.2f}, positive gamma regime, GEX={magnet_gex:.0f}",
            metadata={
                "phase": 1,
                "direction": direction.name,
                "magnet_strike": magnet_strike,
                "magnet_gex": magnet_gex,
                "distance_to_magnet_pct": round(distance_pct, 4),
                "net_gamma": round(net_gamma, 2),
                "momentum": momentum,
                "regime": "POSITIVE",
                "trend": price_window.trend if price_window else "UNKNOWN",
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
                "max_hold_minutes": 60,
            },
        )

    # ------------------------------------------------------------------
    # Phase 2: Acceleration Breakout
    # ------------------------------------------------------------------

    def _phase2_accelerate(
        self,
        magnet_strike: float,
        price: float,
        net_gamma: float,
        regime: str,
        rolling_data: Dict[str, Any],
        breakout_pct: float,
        max_breakout_pct: float,
        trail_stop_pct: float,
        target_risk_mult: float,
        min_confidence: float,
    ) -> Optional[Signal]:
        """
        Phase 2: Price breaks magnet + gamma turns negative → breakout.

        When price crosses the magnet and gamma flips negative,
        dealer hedging accelerates in the breakout direction.
        """
        distance_from_magnet = (price - magnet_strike) / magnet_strike

        price_window = rolling_data.get(KEY_PRICE_5M)

        # Need price to be past the magnet by at least breakout_pct
        if abs(distance_from_magnet) < breakout_pct:
            return None

        # Reject if price is too far past the magnet — don't chase established moves
        if abs(distance_from_magnet) > max_breakout_pct:
            return None

        # Direction in NEGATIVE regime: opposite of Phase 1
        # Price below magnet → oversold bounce (LONG)
        # Price above magnet → overextended pullback (SHORT)
        if distance_from_magnet < 0:
            # Price below magnet in NEGATIVE regime → LONG (oversold bounce)
            direction = Direction.LONG
            stop = magnet_strike * (1 - trail_stop_pct)
        else:
            # Price above magnet in NEGATIVE regime → SHORT (overextended)
            direction = Direction.SHORT
            stop = magnet_strike * (1 + trail_stop_pct)

        # Confidence: further from magnet + stronger negative gamma
        confidence = self._phase2_confidence(
            abs(distance_from_magnet), net_gamma, regime
        )
        if confidence < min_confidence:
            return None

        risk = abs(price - stop)
        if risk <= 0:
            return None

        # Calculate target proportional to risk (minimum target_risk_mult× R/R)
        if direction == Direction.LONG:
            target = price + risk * target_risk_mult
        else:
            target = price - risk * target_risk_mult

        # Verify computed R/R meets minimum threshold
        computed_rr = abs(target - price) / risk
        if computed_rr < target_risk_mult:
            return None

        return Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Magnet breakout: price {price:.2f} past magnet {magnet_strike:.2f}, "
                f"net_gamma={net_gamma:.2f}, regime={regime}"
            ),
            metadata={
                "phase": 2,
                "direction": direction.name,
                "magnet_strike": magnet_strike,
                "distance_from_magnet_pct": round(distance_from_magnet, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "trend": price_window.trend if price_window else "UNKNOWN",
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
                "max_hold_minutes": 60,
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_magnet(self, gex_calc: Any) -> Optional[float]:
        """Find the strike with the highest |normalized net gamma|.

        Uses normalized (per-message average) gamma for consistent scale
        with get_gamma_walls() and other GEX comparisons.
        """
        ladder = gex_calc._ladder
        if not ladder:
            return None

        best_strike = None
        best_gex = 0.0
        price = gex_calc.underlying_price

        for strike, bucket in ladder.items():
            # Use normalized gamma for consistent scale
            norm_net_gamma = bucket.normalized_gamma()
            gex = abs(norm_net_gamma * 100 * price)
            if gex > best_gex:
                best_gex = gex
                best_strike = strike

        return best_strike

    def _price_momentum(self, rolling_data: Dict[str, Any]) -> float:
        """
        Estimate price momentum from rolling window.

        Returns 0.0–1.0. Positive = upward momentum.
        """
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window is None:
            return 0.5  # Neutral if no data

        if price_window.count < 3:
            return 0.5

        # Use z_score of latest value — positive = above mean = bullish
        zs = price_window.z_score
        if zs is None:
            return 0.5

        # Normalize z_score to 0–1 range (z=0 → 0.5, z=2 → ~1.0)
        return min(1.0, max(0.0, 0.5 + zs * 0.15))

    def _phase1_confidence(
        self,
        distance_pct: float,
        magnet_gex: float,
        net_gamma: float,
        momentum: float,
    ) -> float:
        """Phase 1 confidence: proximity + strength + momentum."""
        # Proximity: closer to magnet = higher confidence (0.2–0.4)
        proximity = 0.2 + 0.2 * (1 - distance_pct / 0.02)

        # Gamma strength: higher net_gamma = higher confidence (0.2–0.3)
        gamma_strength = 0.2 + 0.3 * min(1.0, net_gamma / 1000000)

        # Momentum: 0.1–0.2
        momentum_conf = 0.1 + 0.1 * momentum

        # Normalize each component to [0,1] and average
        norm_prox = normalize_confidence(proximity, 0.2, 0.4)
        norm_gamma = normalize_confidence(gamma_strength, 0.2, 0.5)
        norm_mom = normalize_confidence(momentum_conf, 0.1, 0.2)
        return min(1.0, max(0.0, (norm_prox + norm_gamma + norm_mom) / 3.0))

    def _phase2_confidence(
        self,
        distance_pct: float,
        net_gamma: float,
        regime: str,
    ) -> float:
        """Phase 2 confidence: breakout distance + gamma regime."""
        # Distance from magnet: further = more confirmed (0.2–0.3)
        dist_conf = 0.2 + 0.1 * min(1.0, distance_pct / 0.01)

        # Regime alignment: negative regime + negative gamma = higher confidence (0.3–0.4)
        regime_conf = 0.3 if (regime == "NEGATIVE" and net_gamma < 0) else 0.15

        # Gamma magnitude: stronger negative gamma = higher confidence (0.1–0.2)
        gamma_conf = 0.1 + 0.1 * min(1.0, abs(net_gamma) / 500000)

        # Normalize each component to [0,1] and average
        norm_dist = normalize_confidence(dist_conf, 0.2, 0.3)
        norm_regime = normalize_confidence(regime_conf, 0.15, 0.3)
        norm_gamma = normalize_confidence(gamma_conf, 0.1, 0.2)
        return min(1.0, max(0.0, (norm_dist + norm_regime + norm_gamma) / 3.0))
