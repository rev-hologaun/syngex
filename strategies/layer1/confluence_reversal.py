"""
strategies/layer1/confluence_reversal.py — Confluence Reversal

When technical support/resistance aligns with a Gamma Wall or Flip point
within a tight distance (0.3%), that's a double-stacked level with high
reversal probability.

Concept:
    Gamma walls act as structural barriers. Technical S/R levels reflect
    market psychology. When they coincide, the combined level has
    significantly higher probability of causing a reversal.

Scoring:
    - Technical level (swing high/low, VWAP) near price: +1
    - Gamma wall within 0.3% of price: +1
    - Gamma flip within 0.3% of price: +1

    Score 3 = max conviction (technical + wall + flip)
    Score 2 = moderate conviction (any two)
    Score < 2 = no trade

Entry:
    - Score 3 at resistance (call wall + flip + swing high) → SHORT
    - Score 3 at support (put wall + flip + swing low) → LONG
    - Score 2: still trade with lower confidence

Exit:
    - Stop: 0.4% past the confluence level
    - Target: 2× risk (1:2 RR)

Confidence factors:
    - Base confidence from score (score 3 → 0.7, score 2 → 0.45)
    - Wall strength bonus (higher |GEX| = more confidence)
    - Regime alignment bonus
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.ConfluenceReversal")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFLUENCE_DISTANCE_PCT = 0.003  # 0.3% — max distance for confluence
MIN_SCORE = 2                     # Minimum confluence score to trade
MAX_CONFIDENCE_BASE = 0.7         # Base confidence for score 3
MIN_CONFIDENCE = 0.40             # Minimum confidence to emit signal
STOP_PCT = 0.004                  # 0.4% stop
TARGET_RISK_MULT = 2.0            # 2× risk for target


class ConfluenceReversal(BaseStrategy):
    """
    Confluence Reversal strategy: trade reversals at double-stacked levels.

    Combines technical S/R with gamma structural levels for high-probability
    reversal trades. Score each level: technical=1, gamma wall=1, flip=1.
    Trade only levels with score >= 2.
    """

    strategy_id = "confluence_reversal"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate confluence levels and return reversal signals.

        Returns empty list when no confluence level meets the threshold.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        regime = data.get("regime", "")

        # Gather structural levels
        walls = gex_calc.get_gamma_walls(threshold=500_000)
        flip = gex_calc.get_gamma_flip()

        # Find confluence levels
        resistance_levels = self._find_confluence_levels(
            underlying_price, walls, flip, rolling_data, "resistance"
        )
        support_levels = self._find_confluence_levels(
            underlying_price, walls, flip, rolling_data, "support"
        )

        signals: List[Signal] = []

        # Best resistance level → SHORT signal
        if resistance_levels:
            best_resist = max(resistance_levels, key=lambda x: x["score"])
            if best_resist["score"] >= MIN_SCORE:
                sig = self._build_short_signal(
                    best_resist, underlying_price, regime
                )
                if sig:
                    signals.append(sig)

        # Best support level → LONG signal
        if support_levels:
            best_support = max(support_levels, key=lambda x: x["score"])
            if best_support["score"] >= MIN_SCORE:
                sig = self._build_long_signal(
                    best_support, underlying_price, regime
                )
                if sig:
                    signals.append(sig)

        return signals

    # ------------------------------------------------------------------
    # Confluence level detection
    # ------------------------------------------------------------------

    def _find_confluence_levels(
        self,
        price: float,
        walls: List[Dict[str, Any]],
        flip: Optional[Dict[str, Any]],
        rolling_data: Dict[str, Any],
        side: str,
    ) -> List[Dict[str, Any]]:
        """
        Find confluence levels on a given side (resistance or support).

        For resistance: look at walls ABOVE price and rolling max.
        For support: look at walls BELOW price and rolling min.

        Returns list of level dicts with score and details.
        """
        levels: List[Dict[str, Any]] = []

        # Check gamma walls on the relevant side
        if side == "resistance":
            candidate_walls = [w for w in walls if w["strike"] > price]
        else:
            candidate_walls = [w for w in walls if w["strike"] < price]

        for wall in candidate_walls:
            distance_pct = abs(wall["strike"] - price) / price
            if distance_pct > CONFLUENCE_DISTANCE_PCT:
                continue  # Too far from price

            score = 1  # Wall proximity
            level_info = {
                "type": "wall",
                "strike": wall["strike"],
                "score": score,
                "gex": wall["gex"],
                "side": wall["side"],
                "distance_pct": distance_pct,
            }

            # Check if flip is also near this wall
            if flip is not None:
                flip_strike = flip.get("flip_strike")
                if flip_strike is not None:
                    flip_distance = abs(flip_strike - price) / price
                    if flip_distance <= CONFLUENCE_DISTANCE_PCT:
                        score += 1
                        level_info["has_flip"] = True
                        level_info["flip_strike"] = flip_strike
                    elif abs(flip_strike - wall["strike"]) <= CONFLUENCE_DISTANCE_PCT:
                        # Flip is near the wall itself
                        score += 1
                        level_info["has_flip"] = True
                        level_info["flip_strike"] = flip_strike

            # Check if price is near rolling max/min
            rw = self._get_price_window(rolling_data)
            if rw is not None and rw.count >= 3:
                if side == "resistance" and rw.max is not None:
                    max_distance = abs(rw.max - price) / price
                    if max_distance <= CONFLUENCE_DISTANCE_PCT * 2:
                        score += 1
                        level_info["has_technical"] = True
                        level_info["technical_type"] = "rolling_max"
                elif side == "support" and rw.min is not None:
                    min_distance = abs(rw.min - price) / price
                    if min_distance <= CONFLUENCE_DISTANCE_PCT * 2:
                        score += 1
                        level_info["has_technical"] = True
                        level_info["technical_type"] = "rolling_min"

            if score >= MIN_SCORE:
                level_info["score"] = score
                levels.append(level_info)

        # Also check VWAP (rolling mean) as a standalone confluence
        vw = self._get_price_window(rolling_data)
        if vw is not None and vw.count >= 10:
            mean = vw.mean
            if mean is not None and mean > 0:
                vw_distance = abs(mean - price) / price
                if vw_distance <= CONFLUENCE_DISTANCE_PCT:
                    # VWAP is a confluence level
                    wall_near_vwap = None
                    for wall in candidate_walls:
                        if abs(wall["strike"] - mean) / mean <= CONFLUENCE_DISTANCE_PCT:
                            wall_near_vwap = wall
                            break

                    score = 1  # VWAP
                    if wall_near_vwap:
                        score += 1  # Wall at VWAP
                    if flip is not None:
                        flip_strike = flip.get("flip_strike")
                        if flip_strike is not None:
                            flip_distance = abs(flip_strike - mean) / mean
                            if flip_distance <= CONFLUENCE_DISTANCE_PCT:
                                score += 1  # Flip at VWAP

                    if score >= MIN_SCORE:
                        levels.append({
                            "type": "vwap",
                            "strike": mean,
                            "score": score,
                            "gex": wall_near_vwap["gex"] if wall_near_vwap else 0,
                            "side": wall_near_vwap["side"] if wall_near_vwap else "unknown",
                            "distance_pct": vw_distance,
                            "has_flip": flip is not None,
                            "technical_type": "vwap",
                        })

        return levels

    # ------------------------------------------------------------------
    # Signal building
    # ------------------------------------------------------------------

    def _build_short_signal(
        self,
        level: Dict[str, Any],
        price: float,
        regime: str,
    ) -> Optional[Signal]:
        """Build a SHORT signal from a resistance confluence level."""
        strike = level["strike"]
        score = level["score"]
        gex = level.get("gex", 0)

        # Base confidence from score
        if score >= 3:
            confidence = MAX_CONFIDENCE_BASE
        else:
            confidence = MAX_CONFIDENCE_BASE - 0.25

        # Wall strength bonus
        gex_bonus = min(0.15, abs(gex) / 10_000_000)
        confidence += gex_bonus

        # Regime alignment bonus
        if regime == "NEGATIVE":
            confidence += 0.05  # Negative regime favors shorts

        confidence = min(1.0, max(0.0, confidence))
        if confidence < MIN_CONFIDENCE:
            return None

        # Stop past the confluence level
        stop = strike * (1 + STOP_PCT)
        target = price - (price - stop) * TARGET_RISK_MULT
        risk = stop - price
        if risk <= 0:
            return None

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=price,
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=f"Confluence SHORT at {strike:.0f}: "
                   f"score={score}, type={level.get('type', 'unknown')}, "
                   f"has_flip={level.get('has_flip', False)}, "
                   f"regime={regime}",
            metadata={
                "score": score,
                "level_type": level.get("type", "unknown"),
                "confluence_strike": strike,
                "wall_gex": gex,
                "has_flip": level.get("has_flip", False),
                "technical_type": level.get("technical_type"),
                "distance_pct": round(level["distance_pct"], 4),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    def _build_long_signal(
        self,
        level: Dict[str, Any],
        price: float,
        regime: str,
    ) -> Optional[Signal]:
        """Build a LONG signal from a support confluence level."""
        strike = level["strike"]
        score = level["score"]
        gex = level.get("gex", 0)

        # Base confidence from score
        if score >= 3:
            confidence = MAX_CONFIDENCE_BASE
        else:
            confidence = MAX_CONFIDENCE_BASE - 0.25

        # Wall strength bonus
        gex_bonus = min(0.15, abs(gex) / 10_000_000)
        confidence += gex_bonus

        # Regime alignment bonus
        if regime == "POSITIVE":
            confidence += 0.05  # Positive regime favors longs

        confidence = min(1.0, max(0.0, confidence))
        if confidence < MIN_CONFIDENCE:
            return None

        # Stop past the confluence level
        stop = strike * (1 - STOP_PCT)
        target = price + (stop - price) * (-TARGET_RISK_MULT)
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
            reason=f"Confluence LONG at {strike:.0f}: "
                   f"score={score}, type={level.get('type', 'unknown')}, "
                   f"has_flip={level.get('has_flip', False)}, "
                   f"regime={regime}",
            metadata={
                "score": score,
                "level_type": level.get("type", "unknown"),
                "confluence_strike": strike,
                "wall_gex": gex,
                "has_flip": level.get("has_flip", False),
                "technical_type": level.get("technical_type"),
                "distance_pct": round(level["distance_pct"], 4),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_price_window(
        self, rolling_data: Dict[str, Any]
    ) -> Optional[Any]:
        """Get the best available price rolling window."""
        for key in ("price", "price_5m", "price_30m"):
            rw = rolling_data.get(key)
            if rw is not None:
                return rw
        return None
