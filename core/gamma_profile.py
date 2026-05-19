"""
core/gamma_profile.py — Gamma Profile Engine

Separates gamma profile calculations from GEXCalculator.
Provides pure, testable functions for gamma flip, walls, and profile formatting.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from engine.gex_calculator import GEXCalculator


logger = logging.getLogger("Syngex.Core.GammaProfile")


class GammaProfileEngine:
    """Engine for gamma profile analysis and formatting.

    This class separates gamma profile calculations from GEXCalculator,
    which should remain a pure data aggregation engine.

    Responsibilities:
        - Gamma flip detection
        - Gamma wall identification
        - Top strikes ranking
        - Profile line formatting
    """

    def __init__(self, logger: Optional[Any] = None) -> None:
        """Initialize the gamma profile engine.

        Args:
            logger: Optional logger instance for diagnostics.
        """
        self._logger = logger or logger

    def get_gamma_flip(self, gex_calculator: GEXCalculator) -> Optional[float]:
        """Get the gamma flip strike.

        The Gamma Flip is the strike where net gamma shifts from
        positive (above) to negative (below) — i.e., the highest
        strike where cumulative net gamma goes negative when
        scanning from high to low.

        Args:
            gex_calculator: The GEXCalculator instance.

        Returns:
            The flip strike price, or None if no flip detected.
        """
        return gex_calculator.get_gamma_flip()

    def get_gamma_walls(self, gex_calculator: GEXCalculator, threshold: float = 500000) -> List[Dict[str, Any]]:
        """Get gamma walls above the threshold.

        A Gamma Wall is a strike where the normalized Net GEX (in dollar terms)
        exceeds the given threshold. Uses normalized (per-message average) gamma
        values so GEX stays bounded regardless of message count.

        Args:
            gex_calculator: The GEXCalculator instance.
            threshold: Minimum absolute GEX to qualify as a wall.

        Returns:
            List of wall dicts sorted by absolute GEX.
            Each dict contains: strike, net_gamma, gex, side, total_contracts
        """
        return gex_calculator.get_gamma_walls(threshold=threshold)

    def get_top_strikes(self, gex_calculator: GEXCalculator, profile: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
        """Get top N strikes by absolute Net Gamma.

        Args:
            gex_calculator: The GEXCalculator instance (unused, kept for API consistency).
            profile: The gamma profile from gex_calculator.get_gamma_profile().
            count: Number of top strikes to return.

        Returns:
            List of top strike dicts with strike, net_gamma, sign, and abs_gamma.
        """
        top = sorted(
            profile["strikes"].items(),
            key=lambda x: abs(x[1]["net_gamma"]),
            reverse=True,
        )[:count]

        result = []
        for strike, bucket in top:
            ng = bucket["net_gamma"]
            result.append({
                "strike": strike,
                "net_gamma": ng,
                "sign": "+" if ng >= 0 else "-",
                "abs_gamma": abs(ng),
            })
        return result

    def format_profile_line(self, symbol: str, price: float, net_gamma: float, strikes: int, messages: int) -> str:
        """Format the GAMMA_PROFILE log line.

        Args:
            symbol: The ticker symbol.
            price: Current underlying price.
            net_gamma: Current net gamma value.
            strikes: Number of active strikes.
            messages: Total message count.

        Returns:
            Formatted log line string.
        """
        return (
            f"GAMMA_PROFILE  |  {symbol}  |  Underlying: ${price:.2f}  |  "
            f"Net Gamma: {net_gamma:+.2f}  |  Strikes: {strikes}  |  Msgs: {messages}"
        )

    def format_gamma_walls(self, walls: List[Dict[str, Any]], max_walls: int = 3) -> str:
        """Format the GAMMA_WALLS log line.

        Args:
            walls: List of wall dicts from get_gamma_walls().
            max_walls: Maximum number of walls to display.

        Returns:
            Formatted log line string, or empty string if no walls.
        """
        if not walls:
            return ""

        wall_parts = []
        for w in walls[:max_walls]:
            sign = "+" if w["gex"] > 0 else "-"
            wall_parts.append(f"${w['strike']:.0f} ({w['side']}) {sign}${abs(w['gex']):,.0f}")
        return "  |  ".join(wall_parts)

    def format_top_strikes(self, top: List[Dict[str, Any]]) -> str:
        """Format the TOP_STRIKES log line.

        Args:
            top: List of top strike dicts from get_top_strikes().

        Returns:
            Formatted log line string, or empty string if no strikes.
        """
        if not top:
            return ""

        parts = []
        for strike_data in top:
            parts.append(f"  K{strike_data['strike']:.1f}: {strike_data['sign']}{abs(strike_data['abs_gamma']):,.2f}")
        return "  |  ".join(parts)

    def format_gamma_flip(self, flip: float) -> str:
        """Format the GAMMA_FLIP log line.

        Args:
            flip: The gamma flip strike price.

        Returns:
            Formatted log line string.
        """
        return f"  GAMMA_FLIP:  Strike ${flip:.1f} (cumulative gamma turns negative below this)"
