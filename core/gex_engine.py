"""GEX Profile Engine - formatting and gamma profile analysis."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from engine.gex_calculator import GEXCalculator


class GEXProfileEngine:
    """Engine for GEX profile formatting and gamma analysis.

    Extracts gamma flip, walls, top strikes, and profile formatting logic
    from the orchestrator into a dedicated, testable module.
    """

    def __init__(self, logger: Optional[Any] = None, correlation_id: Optional[str] = None) -> None:
        self._logger = logger
        self._correlation_id = correlation_id

    def get_gamma_flip(self, gex_calculator: GEXCalculator) -> Optional[float]:
        """Get the gamma flip strike.

        The Gamma Flip is the strike where net gamma shifts from
        positive (above) to negative (below).

        Args:
            gex_calculator: The GEXCalculator instance.

        Returns:
            The flip strike price, or None if no flip detected.
        """
        return gex_calculator.get_gamma_flip()

    def get_gamma_walls(self, gex_calculator: GEXCalculator, threshold: float = 500000) -> List[Dict[str, Any]]:
        """Get gamma walls above the threshold.

        A Gamma Wall is a strike where the normalized Net GEX exceeds
        the given threshold.

        Args:
            gex_calculator: The GEXCalculator instance.
            threshold: Minimum absolute GEX to qualify as a wall.

        Returns:
            List of wall dicts sorted by absolute GEX.
        """
        return gex_calculator.get_gamma_walls(threshold=threshold)

    def get_top_strikes(self, gex_calculator: GEXCalculator, profile: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
        """Get top N strikes by absolute Net Gamma.

        Args:
            gex_calculator: The GEXCalculator instance.
            profile: The gamma profile from gex_calculator.get_gamma_profile().
            count: Number of top strikes to return.

        Returns:
            List of top strike dicts with strike, net_gamma, and sign.
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

    def format_profile_line(self, symbol: str, price: float, net_gamma: float, strikes: int, total_messages: int) -> str:
        """Format the main GAMMA_PROFILE log line.

        Args:
            symbol: The ticker symbol.
            price: Current underlying price.
            net_gamma: Current net gamma value.
            strikes: Number of active strikes.
            total_messages: Total message count.

        Returns:
            Formatted log line string.
        """
        return (
            f"GAMMA_PROFILE  |  {symbol}  |  Underlying: ${price:.2f}  |  "
            f"Net Gamma: {net_gamma:+.2f}  |  Strikes: {strikes}  |  Msgs: {total_messages}"
        )

    def format_gamma_flip(self, flip: float) -> str:
        """Format the GAMMA_FLIP log line.

        Args:
            flip: The gamma flip strike price.

        Returns:
            Formatted log line string.
        """
        return f"  GAMMA_FLIP:  Strike ${flip:.1f} (cumulative gamma turns negative below this)"

    def format_gamma_walls(self, walls: List[Dict[str, Any]], max_walls: int = 3) -> str:
        """Format the GAMMA_WALLS log line.

        Args:
            walls: List of wall dicts from get_gamma_walls().
            max_walls: Maximum number of walls to display.

        Returns:
            Formatted log line string.
        """
        if not walls:
            return ""

        wall_parts = []
        for w in walls[:max_walls]:
            sign = "+" if w["gex"] > 0 else "-"
            wall_parts.append(f"${w['strike']:.0f} ({w['side']}) {sign}${abs(w['gex']):,.0f}")
        return "  |  ".join(wall_parts)

    def format_top_strikes(self, top_strikes: List[Dict[str, Any]]) -> str:
        """Format the TOP_STRIKES log line.

        Args:
            top_strikes: List of top strike dicts from get_top_strikes().

        Returns:
            Formatted log line string.
        """
        if not top_strikes:
            return ""

        parts = []
        for strike_data in top_strikes:
            parts.append(f"  K{strike_data['strike']:.1f}: {strike_data['sign']}{abs(strike_data['abs_gamma']):,.2f}")
        return "  |  ".join(parts)

    def log_profile(self, symbol: str, price: float, net_gamma: float, strikes: int, total_messages: int,
                    flip: Optional[float], walls: List[Dict[str, Any]], top_strikes: List[Dict[str, Any]]) -> None:
        """Log the complete gamma profile.

        Args:
            symbol: The ticker symbol.
            price: Current underlying price.
            net_gamma: Current net gamma value.
            strikes: Number of active strikes.
            total_messages: Total message count.
            flip: Gamma flip strike (or None).
            walls: Gamma walls list.
            top_strikes: Top strikes list.
        """
        # Main profile line
        profile_line = self.format_profile_line(symbol, price, net_gamma, strikes, total_messages)
        if self._logger:
            self._logger.info(profile_line)

        # Gamma flip
        if flip is not None:
            flip_line = self.format_gamma_flip(flip)
            if self._logger:
                self._logger.info(flip_line)

        # Gamma walls
        if walls:
            walls_line = self.format_gamma_walls(walls)
            if walls_line and self._logger:
                self._logger.info(f"  GAMMA_WALLS:  {walls_line}")

        # Top strikes
        if top_strikes:
            top_line = self.format_top_strikes(top_strikes)
            if top_line and self._logger:
                self._logger.info(f"  TOP_STRIKES:  {top_line}")
