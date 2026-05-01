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
from strategies.rolling_keys import KEY_PRICE, KEY_PRICE_5M, KEY_PRICE_30M

logger = logging.getLogger("Syngex.Strategies.ConfluenceReversal")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFLUENCE_DISTANCE_PCT = 0.003  # 0.3% — max distance for confluence
MIN_STRUCTURAL_SIGNALS = 2        # Must have 2+ independent structural signals
MAX_CONFIDENCE_BASE = 0.7         # Base confidence for score 3
MIN_CONFIDENCE = 0.40             # Minimum confidence to emit signal
STOP_PCT = 0.004                  # 0.4% stop
TARGET_RISK_MULT = 2.0            # 2× risk for target

# Structural signals (independent sources of truth)
# Only wall, flip, and VWAP count as structural — rolling extremes are technical, not structural


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
            best_resist = max(resistance_levels, key=lambda x: x.get("structural_count", x.get("score", 0)))
            if best_resist.get("structural_count", best_resist.get("score", 0)) >= MIN_STRUCTURAL_SIGNALS:
                sig = self._build_short_signal(
                    best_resist, underlying_price, regime
                )
                if sig:
                    signals.append(sig)

        # Best support level → LONG signal
        if support_levels:
            best_support = max(support_levels, key=lambda x: x.get("structural_count", x.get("score", 0)))
            if best_support.get("structural_count", best_support.get("score", 0)) >= MIN_STRUCTURAL_SIGNALS:
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
        flip: Optional[float],
        rolling_data: Dict[str, Any],
        side: str,
    ) -> List[Dict[str, Any]]:
        """
        Find confluence levels on a given side (resistance or support).

        Confluence requires at least MIN_STRUCTURAL_SIGNALS independent
        structural signals: gamma wall, gamma flip, and/or VWAP.
        Rolling extremes (max/min) are technical — they can boost
        confidence but don't count as structural signals.

        Returns list of level dicts with score and details.
        """
        levels: List[Dict[str, Any]] = []

        # Check gamma walls on the relevant side
        if side == "resistance":
            candidate_walls = [w for w in walls if w["strike"] > price]
        else:
            candidate_walls = [w for w in walls if w["strike"] < price]

        # Get rolling window for technical signal check
        rw = self._get_price_window(rolling_data)
        has_technical = False
        technical_type = None
        if rw is not None and rw.count >= 3:
            if side == "resistance" and rw.max is not None:
                if abs(rw.max - price) / price <= CONFLUENCE_DISTANCE_PCT * 2:
                    has_technical = True
                    technical_type = "rolling_max"
            elif side == "support" and rw.min is not None:
                if abs(rw.min - price) / price <= CONFLUENCE_DISTANCE_PCT * 2:
                    has_technical = True
                    technical_type = "rolling_min"

        # Check each wall for confluence with independent structural signals
        for wall in candidate_walls:
            distance_pct = abs(wall["strike"] - price) / price
            if distance_pct > CONFLUENCE_DISTANCE_PCT:
                continue  # Too far from price

            # Count independent structural signals
            structural_count = 1  # Wall itself
            level_info = {
                "type": "wall",
                "strike": wall["strike"],
                "structural_count": structural_count,
                "gex": wall["gex"],
                "side": wall["side"],
                "distance_pct": distance_pct,
                "has_flip": False,
                "has_vwap": False,
                "has_technical": has_technical,
                "technical_type": technical_type,
            }

            # Check if flip is also near (independent structural signal)
            if flip is not None:
                flip_distance = abs(flip - price) / price
                if flip_distance <= CONFLUENCE_DISTANCE_PCT:
                    structural_count += 1
                    level_info["has_flip"] = True
                    level_info["flip_strike"] = flip
                elif abs(flip - wall["strike"]) <= CONFLUENCE_DISTANCE_PCT:
                    # Flip is near the wall itself — still independent
                    structural_count += 1
                    level_info["has_flip"] = True
                    level_info["flip_strike"] = flip

            # Check if VWAP is near (independent structural signal)
            vw = self._get_price_window(rolling_data)
            if vw is not None and vw.count >= 10 and vw.mean is not None:
                vw_distance = abs(vw.mean - wall["strike"]) / vw.mean
                if vw_distance <= CONFLUENCE_DISTANCE_PCT:
                    structural_count += 1
                    level_info["has_vwap"] = True

            # Only emit if we have enough independent structural signals
            if structural_count >= MIN_STRUCTURAL_SIGNALS:
                level_info["structural_count"] = structural_count
                level_info["score"] = structural_count
                levels.append(level_info)

        # Also check VWAP as standalone confluence level
        vw = self._get_price_window(rolling_data)
        if vw is not None and vw.count >= 10:
            mean = vw.mean
            if mean is not None and mean > 0:
                vw_distance = abs(mean - price) / price
                if vw_distance <= CONFLUENCE_DISTANCE_PCT:
                    structural_count = 1  # VWAP itself

                    # Check for wall at VWAP
                    wall_near_vwap = None
                    for wall in candidate_walls:
                        if abs(wall["strike"] - mean) / mean <= CONFLUENCE_DISTANCE_PCT:
                            wall_near_vwap = wall
                            break

                    if wall_near_vwap:
                        structural_count += 1  # Wall at VWAP

                    # Check for flip at VWAP
                    if flip is not None:
                        flip_distance = abs(flip - mean) / mean
                        if flip_distance <= CONFLUENCE_DISTANCE_PCT:
                            structural_count += 1  # Flip at VWAP

                    if structural_count >= MIN_STRUCTURAL_SIGNALS:
                        levels.append({
                            "type": "vwap",
                            "strike": mean,
                            "score": structural_count,
                            "structural_count": structural_count,
                            "gex": wall_near_vwap["gex"] if wall_near_vwap else 0,
                            "side": wall_near_vwap["side"] if wall_near_vwap else "unknown",
                            "distance_pct": vw_distance,
                            "has_flip": flip is not None,
                            "has_vwap": True,
                            "has_technical": has_technical,
                            "technical_type": technical_type,
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
        structural_count = level.get("structural_count", level.get("score", 0))
        gex = level.get("gex", 0)

        # Base confidence from structural signal count
        if structural_count >= 3:
            confidence = MAX_CONFIDENCE_BASE
        else:
            confidence = MAX_CONFIDENCE_BASE - 0.25

        # Wall strength bonus (normalize to [0,1])
        gex_bonus = min(0.15, abs(gex) / 10_000_000)
        # Technical signal bonus (normalize to [0,1])
        tech_bonus = 0.05 if level.get("has_technical") else 0.0
        # Regime alignment bonus (normalize to [0,1])
        regime_bonus = 0.05 if regime == "NEGATIVE" else 0.0
        # Normalize and average with base
        norm_base = (confidence - 0.45) / (0.7 - 0.45) if 0.7 != 0.45 else 1.0
        norm_gex = gex_bonus / 0.15 if 0.15 != 0 else 0.0
        norm_tech = tech_bonus / 0.05 if 0.05 != 0 else 0.0
        norm_regime = regime_bonus / 0.05 if 0.05 != 0 else 0.0
        confidence = (norm_base + norm_gex + norm_tech + norm_regime) / 4.0
        if confidence < MIN_CONFIDENCE:
            return None

        # Stop past the confluence level
        stop = strike * (1 + STOP_PCT)
        risk = stop - price
        target = price - risk * TARGET_RISK_MULT
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
                   f"{structural_count} structural signals, type={level.get('type', 'unknown')}, "
                   f"has_flip={level.get('has_flip', False)}, "
                   f"regime={regime}",
            metadata={
                "structural_count": structural_count,
                "level_type": level.get("type", "unknown"),
                "confluence_strike": strike,
                "wall_gex": gex,
                "has_flip": level.get("has_flip", False),
                "has_vwap": level.get("has_vwap", False),
                "has_technical": level.get("has_technical", False),
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
        structural_count = level.get("structural_count", level.get("score", 0))
        gex = level.get("gex", 0)

        # Base confidence from structural signal count
        if structural_count >= 3:
            confidence = MAX_CONFIDENCE_BASE
        else:
            confidence = MAX_CONFIDENCE_BASE - 0.25

        # Wall strength bonus (normalize to [0,1])
        gex_bonus = min(0.15, abs(gex) / 10_000_000)
        # Technical signal bonus (normalize to [0,1])
        tech_bonus = 0.05 if level.get("has_technical") else 0.0
        # Regime alignment bonus (normalize to [0,1])
        regime_bonus = 0.05 if regime == "POSITIVE" else 0.0
        # Normalize and average with base
        norm_base = (confidence - 0.45) / (0.7 - 0.45) if 0.7 != 0.45 else 1.0
        norm_gex = gex_bonus / 0.15 if 0.15 != 0 else 0.0
        norm_tech = tech_bonus / 0.05 if 0.05 != 0 else 0.0
        norm_regime = regime_bonus / 0.05 if 0.05 != 0 else 0.0
        confidence = (norm_base + norm_gex + norm_tech + norm_regime) / 4.0
        if confidence < MIN_CONFIDENCE:
            return None

        # Stop past the confluence level
        stop = strike * (1 - STOP_PCT)
        risk = price - stop
        target = price + risk * TARGET_RISK_MULT
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
                   f"{structural_count} structural signals, type={level.get('type', 'unknown')}, "
                   f"has_flip={level.get('has_flip', False)}, "
                   f"regime={regime}",
            metadata={
                "structural_count": structural_count,
                "level_type": level.get("type", "unknown"),
                "confluence_strike": strike,
                "wall_gex": gex,
                "has_flip": level.get("has_flip", False),
                "has_vwap": level.get("has_vwap", False),
                "has_technical": level.get("has_technical", False),
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
        for key in (KEY_PRICE, KEY_PRICE_5M, KEY_PRICE_30M):
            rw = rolling_data.get(key)
            if rw is not None:
                return rw
        return None
