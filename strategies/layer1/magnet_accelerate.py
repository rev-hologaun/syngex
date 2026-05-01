"""
strategies/layer1/magnet_accelerate.py — Magnet & Accelerate

Two-phase strategy centered on the highest-GEX strike (the "magnet").

Phase 1 — Magnet Pull:
    When net gamma is positive and price is below the magnet,
    go LONG targeting the magnet. Dealer hedging pulls price up.

Phase 2 — Acceleration:
    When price breaks through the magnet and cumulative gamma
    turns negative, enter in the breakout direction.
    Dealer hedging accelerates the move.

Entry:
    - Phase 1: LONG when price < magnet and net_gamma > 0
    - Phase 2: LONG or SHORT on magnet breakout + gamma regime flip

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

logger = logging.getLogger("Syngex.Strategies.MagnetAccelerate")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_MAGNET_GEX = 500000       # Minimum |net_gamma| to be a magnet
MAGNET_EXIT_PCT = 0.003       # 0.3% — exit within this % of magnet
BREAKOUT_PCT = 0.002          # 0.2% — price must be this far past magnet to breakout
MAX_BREAKOUT_PCT = 0.02       # 2% — max distance past magnet (no chasing)
TRAIL_STOP_PCT = 0.01         # 1% — trailing stop for Phase 2
TARGET_RISK_MULT = 1.5        # Minimum 1.5× risk for target distance
MIN_CONFIDENCE = 0.35         # Minimum confidence to emit signal


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

        Returns empty list when magnet is not identifiable or conditions
        are not met.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        regime = data.get("regime", "")
        net_gamma = data.get("net_gamma", 0)

        # Find the magnet strike (highest |net_gamma|)
        magnet_strike = self._find_magnet(gex_calc)
        if magnet_strike is None:
            return []

        magnet_bucket = gex_calc._ladder.get(magnet_strike)
        if magnet_bucket is None:
            return []

        magnet_gex = abs(magnet_bucket.net_gamma * 100 * underlying_price)
        if magnet_gex < MIN_MAGNET_GEX:
            return []

        signals: List[Signal] = []

        # Phase 1: Magnet pull
        if regime == "POSITIVE" and net_gamma > 0:
            sig = self._phase1_pull(
                magnet_strike, magnet_gex, underlying_price, net_gamma, rolling_data
            )
            if sig:
                signals.append(sig)

        # Phase 2: Acceleration breakout
        if regime == "NEGATIVE" or net_gamma < 0:
            sig = self._phase2_accelerate(
                magnet_strike, underlying_price, net_gamma, regime, rolling_data
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
    ) -> Optional[Signal]:
        """
        Phase 1: Price below magnet + positive gamma → LONG toward magnet.

        Dealer hedging (long gamma) means they buy dips and sell rallies,
        which naturally pulls price toward the magnet strike.
        """
        if price >= magnet_strike:
            return None

        distance_pct = (magnet_strike - price) / price
        if distance_pct > 0.02:
            # More than 2% away — not in magnet range
            return None

        # Check for upward momentum in recent price action
        momentum = self._price_momentum(rolling_data)

        # Confidence: closer to magnet + stronger gamma + good momentum
        confidence = self._phase1_confidence(distance_pct, magnet_gex, net_gamma, momentum)
        if confidence < MIN_CONFIDENCE:
            return None

        # Target: magnet strike (exit within 0.3% of it)
        target = magnet_strike
        # Stop: below recent low or 1% below entry
        stop = price * (1 - 0.01)

        # Check rolling window low for tighter stop
        price_window = rolling_data.get("price_5m")
        if price_window and price_window.min is not None:
            stop = max(stop, price_window.min * 0.998)

        risk = price - stop
        if risk <= 0:
            return None

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Magnet pull: price {price:.2f} → magnet {magnet_strike:.2f}, "
                   f"positive gamma regime, GEX={magnet_gex:.0f}",
            metadata={
                "phase": 1,
                "magnet_strike": magnet_strike,
                "magnet_gex": magnet_gex,
                "distance_to_magnet_pct": round(distance_pct, 4),
                "net_gamma": round(net_gamma, 2),
                "momentum": momentum,
                "risk": round(risk, 2),
                "risk_reward_ratio": round((target - price) / risk, 2),
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
    ) -> Optional[Signal]:
        """
        Phase 2: Price breaks magnet + gamma turns negative → breakout.

        When price crosses the magnet and gamma flips negative,
        dealer hedging accelerates in the breakout direction.
        """
        distance_from_magnet = (price - magnet_strike) / magnet_strike

        # Need price to be past the magnet by at least BREAKOUT_PCT
        if abs(distance_from_magnet) < BREAKOUT_PCT:
            return None

        # Reject if price is too far past the magnet — don't chase established moves
        if abs(distance_from_magnet) > MAX_BREAKOUT_PCT:
            return None

        # Direction depends on which side of magnet we are
        if distance_from_magnet > 0:
            # Price above magnet → potential LONG breakout
            direction = Direction.LONG
            stop = magnet_strike * (1 - TRAIL_STOP_PCT)
        else:
            # Price below magnet → potential SHORT breakout
            direction = Direction.SHORT
            stop = magnet_strike * (1 + TRAIL_STOP_PCT)

        # Confidence: further from magnet + stronger negative gamma
        confidence = self._phase2_confidence(
            abs(distance_from_magnet), net_gamma, regime
        )
        if confidence < MIN_CONFIDENCE:
            return None

        risk = abs(price - stop)
        if risk <= 0:
            return None

        # Calculate target proportional to risk (minimum 1.5× R/R)
        if direction == Direction.LONG:
            target = price + risk * TARGET_RISK_MULT
        else:
            target = price - risk * TARGET_RISK_MULT

        # Verify computed R/R meets minimum threshold
        computed_rr = abs(target - price) / risk
        if computed_rr < TARGET_RISK_MULT:
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
                "magnet_strike": magnet_strike,
                "distance_from_magnet_pct": round(distance_from_magnet, 4),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_magnet(self, gex_calc: Any) -> Optional[float]:
        """Find the strike with the highest |net_gamma|."""
        ladder = gex_calc._ladder
        if not ladder:
            return None

        best_strike = None
        best_gex = 0.0

        for strike, bucket in ladder.items():
            gex = abs(bucket.net_gamma * 100 * gex_calc.underlying_price)
            if gex > best_gex:
                best_gex = gex
                best_strike = strike

        return best_strike

    def _price_momentum(self, rolling_data: Dict[str, Any]) -> float:
        """
        Estimate price momentum from rolling window.

        Returns 0.0–1.0. Positive = upward momentum.
        """
        price_window = rolling_data.get("price_5m")
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
        norm_prox = (proximity - 0.2) / (0.4 - 0.2) if 0.4 != 0.2 else 1.0
        norm_gamma = (gamma_strength - 0.2) / (0.5 - 0.2) if 0.5 != 0.2 else 1.0
        norm_mom = (momentum_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
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
        norm_dist = (dist_conf - 0.2) / (0.3 - 0.2) if 0.3 != 0.2 else 1.0
        norm_regime = (regime_conf - 0.15) / (0.3 - 0.15) if 0.3 != 0.15 else 1.0
        norm_gamma = (gamma_conf - 0.1) / (0.2 - 0.1) if 0.2 != 0.1 else 1.0
        return min(1.0, max(0.0, (norm_dist + norm_regime + norm_gamma) / 3.0))
