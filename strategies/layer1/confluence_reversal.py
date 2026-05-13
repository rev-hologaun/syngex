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
    Score 1 = wall-level confluence alone is valid
    Score 0 = no trade

Entry:
    - Score 3 at resistance (call wall + flip + swing high) → SHORT
    - Score 3 at support (put wall + flip + swing low) → LONG
    - Score 2: still trade with lower confidence

Exit:
    - Stop: 0.4% past the confluence level
    - Target: 2× risk (1:2 RR)

Confidence factors:
    - Base confidence from score (score 3 → 0.6, score 2 → 0.35)
    - Wall strength bonus (higher |GEX| = more confidence)
    - Regime alignment bonus
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_PRICE_5M,
    KEY_PRICE_30M,
    KEY_IV_SKEW_5M,
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_ASK_SIZE_5M,
)
from strategies.volume_filter import VolumeFilter

logger = logging.getLogger("Syngex.Strategies.ConfluenceReversal")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFLUENCE_DISTANCE_PCT = 0.003  # 0.3% — max distance for confluence
MIN_STRUCTURAL_SIGNALS = 1        # Wall-level confluence alone is valid
MIN_CONFIDENCE = 0.15             # Minimum confidence to emit signal
STOP_PCT = 0.008                  # 0.8% stop
TARGET_RISK_MULT = 2.0            # 2× risk for target

# Confluence Velocity (Phase 1)
VELOCITY_MIN_ZSCORE = 1.0         # Minimum |z-score| for approach velocity
VELOCITY_MIN_VOLUME_MULT = 1.2    # Volume must be >= 1.2x rolling average

# IV-Skew Wall Quality (Phase 2)
IV_WEIGHT_BASE = 1.0
IV_WEIGHT_MAX = 1.5
IV_WEIGHT_SKEW_THRESHOLD = 0.05

# Liquidity Absorption (Phase 3)
DEPTH_SPIKE_THRESHOLD = 1.5       # Current depth >= 1.5x rolling average

# Regime-Adaptive Stops (Phase 4)
NEGATIVE_GAMMA_STOP_MULT = 1.5    # Wider stops in negative gamma (more noise)
POSITIVE_GAMMA_STOP_MULT = 0.75   # Tighter stops in positive gamma (cleaner)

# Structural signals (independent sources of truth)
# Only wall, flip, and VWAP count as structural — rolling extremes are technical, not structural


class ConfluenceReversal(BaseStrategy):
    """
    Confluence Reversal strategy: trade reversals at double-stacked levels.

    Combines technical S/R with gamma structural levels for high-probability
    reversal trades. Score each level: technical=1, gamma wall=1, flip=1.
    Trade levels with score >= 1 (wall-level confluence alone is valid).
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

        # Global volume filter — skip if volume doesn't support the signal
        vol_check = VolumeFilter.evaluate(rolling_data, MIN_CONFIDENCE)
        if not vol_check["recommended"]:
            return []

        regime = data.get("regime", "")
        depth_snapshot = data.get("depth_snapshot")

        # Gather structural levels
        walls = gex_calc.get_gamma_walls(threshold=500_000)
        flip = gex_calc.get_gamma_flip()

        # Price window for trend info (used by signal builders)
        price_window = self._get_price_window(rolling_data)

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
            best_resist = max(resistance_levels, key=lambda x: x.get("structural_count", 0))
            if best_resist.get("structural_count", 0) >= MIN_STRUCTURAL_SIGNALS:
                sig = self._build_short_signal(
                    best_resist, underlying_price, regime, price_window,
                    depth_snapshot, rolling_data,
                )
                if sig:
                    signals.append(sig)

        # Best support level → LONG signal
        if support_levels:
            best_support = max(support_levels, key=lambda x: x.get("structural_count", 0))
            if best_support.get("structural_count", 0) >= MIN_STRUCTURAL_SIGNALS:
                sig = self._build_long_signal(
                    best_support, underlying_price, regime, price_window,
                    depth_snapshot, rolling_data,
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
        Wall-level confluence alone (score 1) is valid.
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
        price_window = self._get_price_window(rolling_data)
        rw = price_window
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
        price_window: Optional[Any],
        depth_snapshot: Optional[Dict[str, Any]],
        rolling_data: Dict[str, Any],
    ) -> Optional[Signal]:
        """Build a SHORT signal from a resistance confluence level."""
        strike = level["strike"]
        structural_count = level.get("structural_count", 0)
        gex = level.get("gex", 0)
        wall_side = level.get("side", "call")

        # === Velocity check (hard gate) ===
        velocity_score = self._check_confluence_velocity(price, rolling_data)
        if velocity_score is None:
            return None

        # === Liquidity absorption check (hard gate) ===
        absorption_score = self._check_liquidity_absorption(
            wall_side, depth_snapshot, rolling_data
        )
        if absorption_score is None:
            return None

        # === Regime-adaptive stop ===
        regime_mult = (
            NEGATIVE_GAMMA_STOP_MULT
            if regime == "NEGATIVE"
            else POSITIVE_GAMMA_STOP_MULT
        )
        stop = strike * (1 + STOP_PCT * regime_mult)
        risk = stop - price
        target = price - risk * TARGET_RISK_MULT
        if risk <= 0:
            return None

        # === 4-component confidence (Family A) ===
        # 1. Base from structural count: normalized to [0, 1]
        #    score 3 → 1.0, score 2 → 0.5, score 1 → 0.25
        norm_base = min(1.0, structural_count / 3.0)

        # 2. Wall integrity: already [0, 1] from _compute_wall_integrity
        wall_integrity = self._compute_wall_integrity(
            abs(gex), wall_side, rolling_data
        )
        norm_integrity = wall_integrity

        # 3. Velocity: already [0, 1]
        norm_velocity = velocity_score

        # 4. Absorption: already [0, 1]
        norm_absorption = absorption_score

        confidence = (norm_base + norm_integrity + norm_velocity + norm_absorption) / 4.0
        confidence = min(1.0, max(0.0, confidence))

        if confidence < MIN_CONFIDENCE:
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
                   f"velocity={velocity_score:.3f}, absorption={absorption_score:.3f}, "
                   f"regime={regime}, trend={trend}",
            metadata={
                "structural_count": structural_count,
                "level_type": level.get("type", "unknown"),
                "confluence_strike": strike,
                "wall_gex": gex,
                "wall_integrity": round(wall_integrity, 3),
                "has_flip": level.get("has_flip", False),
                "has_vwap": level.get("has_vwap", False),
                "has_technical": level.get("has_technical", False),
                "technical_type": level.get("technical_type"),
                "distance_pct": round(level["distance_pct"], 4),
                "regime": regime,
                "trend": trend,
                "velocity_score": velocity_score,
                "absorption_score": absorption_score,
                "regime_stop_mult": regime_mult,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    def _build_long_signal(
        self,
        level: Dict[str, Any],
        price: float,
        regime: str,
        price_window: Optional[Any],
        depth_snapshot: Optional[Dict[str, Any]],
        rolling_data: Dict[str, Any],
    ) -> Optional[Signal]:
        """Build a LONG signal from a support confluence level."""
        strike = level["strike"]
        structural_count = level.get("structural_count", 0)
        gex = level.get("gex", 0)
        wall_side = level.get("side", "put")

        # === Velocity check (hard gate) ===
        velocity_score = self._check_confluence_velocity(price, rolling_data)
        if velocity_score is None:
            return None

        # === Liquidity absorption check (hard gate) ===
        absorption_score = self._check_liquidity_absorption(
            wall_side, depth_snapshot, rolling_data
        )
        if absorption_score is None:
            return None

        # === Regime-adaptive stop ===
        regime_mult = (
            NEGATIVE_GAMMA_STOP_MULT
            if regime == "NEGATIVE"
            else POSITIVE_GAMMA_STOP_MULT
        )
        stop = strike * (1 - STOP_PCT * regime_mult)
        risk = price - stop
        target = price + risk * TARGET_RISK_MULT
        if risk <= 0:
            return None

        # === 4-component confidence (Family A) ===
        # 1. Base from structural count: normalized to [0, 1]
        #    score 3 → 1.0, score 2 → 0.5, score 1 → 0.25
        norm_base = min(1.0, structural_count / 3.0)

        # 2. Wall integrity: already [0, 1] from _compute_wall_integrity
        wall_integrity = self._compute_wall_integrity(
            abs(gex), wall_side, rolling_data
        )
        norm_integrity = wall_integrity

        # 3. Velocity: already [0, 1]
        norm_velocity = velocity_score

        # 4. Absorption: already [0, 1]
        norm_absorption = absorption_score

        confidence = (norm_base + norm_integrity + norm_velocity + norm_absorption) / 4.0
        confidence = min(1.0, max(0.0, confidence))

        if confidence < MIN_CONFIDENCE:
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
                   f"velocity={velocity_score:.3f}, absorption={absorption_score:.3f}, "
                   f"regime={regime}, trend={trend}",
            metadata={
                "structural_count": structural_count,
                "level_type": level.get("type", "unknown"),
                "confluence_strike": strike,
                "wall_gex": gex,
                "wall_integrity": round(wall_integrity, 3),
                "has_flip": level.get("has_flip", False),
                "has_vwap": level.get("has_vwap", False),
                "has_technical": level.get("has_technical", False),
                "technical_type": level.get("technical_type"),
                "distance_pct": round(level["distance_pct"], 4),
                "regime": regime,
                "trend": trend,
                "velocity_score": velocity_score,
                "absorption_score": absorption_score,
                "regime_stop_mult": regime_mult,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - price) / risk, 2),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Confluence Velocity
    # ------------------------------------------------------------------

    def _check_confluence_velocity(
        self, price: float, rolling_data: Dict[str, Any]
    ) -> Optional[float]:
        """Check if price is approaching with sufficient velocity.

        Returns velocity score 0.0-1.0, or None if insufficient data.
        Hard gate: None means skip signal.
        """
        price_window = self._get_price_window(rolling_data)
        if price_window is None or price_window.count < 5:
            return None
        if price_window.std is None or price_window.std <= 0:
            return None
        if price_window.mean is None:
            return None

        z_score = (price - price_window.mean) / price_window.std

        vol_filter = VolumeFilter.evaluate(rolling_data, 0.0)
        vol_mult = vol_filter.get("volume_multiplier", 1.0)

        if vol_mult < VELOCITY_MIN_VOLUME_MULT:
            return None

        velocity_score = min(1.0, abs(z_score) / 3.0)
        return round(velocity_score, 3)

    # ------------------------------------------------------------------
    # IV-Skew Wall Quality
    # ------------------------------------------------------------------

    def _compute_wall_integrity(
        self,
        gex: float,
        wall_side: str,
        rolling_data: Dict[str, Any],
    ) -> float:
        """Compute IV-weighted structural integrity of a wall.

        Returns integrity score 0.0-1.0.
        High IV skew = wall is more "sticky" = higher structural integrity.
        """
        iv_skew_rw = rolling_data.get(KEY_IV_SKEW_5M)
        iv_skew = (
            iv_skew_rw.mean
            if iv_skew_rw and iv_skew_rw.mean is not None
            else 0.0
        )

        # For resistance walls (call): positive skew = calls expensive = sticky
        # For support walls (put): negative skew = puts expensive = sticky
        if wall_side == "call":
            iv_weight = IV_WEIGHT_BASE + min(
                IV_WEIGHT_MAX - IV_WEIGHT_BASE,
                max(0.0, iv_skew) / IV_WEIGHT_SKEW_THRESHOLD,
            )
        else:
            iv_weight = IV_WEIGHT_BASE + min(
                IV_WEIGHT_MAX - IV_WEIGHT_BASE,
                max(0.0, -iv_skew) / IV_WEIGHT_SKEW_THRESHOLD,
            )

        iv_weight = min(IV_WEIGHT_MAX, iv_weight)
        gex_strength = min(1.0, abs(gex) / 10_000_000)
        return gex_strength * iv_weight

    # ------------------------------------------------------------------
    # Liquidity Absorption
    # ------------------------------------------------------------------

    def _check_liquidity_absorption(
        self,
        level_side: str,
        depth_snapshot: Optional[Dict[str, Any]],
        rolling_data: Dict[str, Any],
    ) -> Optional[float]:
        """Check if order book depth shows absorption at the level.

        Returns absorption score 0.0-1.0, or None if insufficient depth data.
        Hard gate: None means skip signal.
        """
        if not depth_snapshot:
            return None

        if level_side == "call":
            current_depth = depth_snapshot.get("total_ask_size", 0)
            key = KEY_DEPTH_ASK_SIZE_5M
        else:
            current_depth = depth_snapshot.get("total_bid_size", 0)
            key = KEY_DEPTH_BID_SIZE_5M

        depth_rw = rolling_data.get(key)
        if depth_rw is None or depth_rw.count < 10 or depth_rw.mean is None:
            return None

        avg_depth = depth_rw.mean
        if avg_depth <= 0:
            return None

        spike_ratio = current_depth / avg_depth

        if spike_ratio >= DEPTH_SPIKE_THRESHOLD:
            return min(1.0, spike_ratio / 3.0)
        elif spike_ratio >= 1.0:
            return spike_ratio / DEPTH_SPIKE_THRESHOLD * 0.5
        else:
            return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_price_window(
        self, rolling_data: Dict[str, Any]
    ) -> Optional[Any]:
        """Get the best available price rolling window."""
        for key in (KEY_PRICE_5M, KEY_PRICE_30M):
            rw = rolling_data.get(key)
            if rw is not None:
                return rw
        return None
