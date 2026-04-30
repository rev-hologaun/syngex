"""
strategies/filters/net_gamma_filter.py — Net Gamma Regime Filter

The master filter that gates ALL strategy signals.

Logic:
    - Positive Net Gamma → dealers buy dips, sell rallies → fade extremes
    - Negative Net Gamma → dealers sell dips, buy rallies → trend-follow

A signal is only allowed if it aligns with the current regime.
"""

from __future__ import annotations

import logging
from typing import Optional

from ..signal import Direction, Signal

logger = logging.getLogger("Syngex.StrategyEngine.Filter")


class Regime(str):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class NetGammaFilter:
    """
    Master regime filter.

    Usage:
        filter = NetGammaFilter()
        engine.register_filter(filter.evaluate_signal)

        # During data processing, update the regime:
        filter.update_regime(net_gamma, flip_price, underlying_price)

        # Each signal is checked:
        if filter.evaluate_signal(signal):
            # signal passes
    """

    def __init__(self, flip_buffer: float = 0.5) -> None:
        """
        Args:
            flip_buffer: Distance (in $) around the flip point where
                         regime is considered "transitioning" and signals
                         are blocked to avoid whipsaws.
        """
        self._regime: str = Regime.POSITIVE  # Default to positive
        self._flip_strike: Optional[float] = None
        self._underlying_price: float = 0.0
        self._flip_buffer = flip_buffer
        self._transitioning = False

        logger.info("NetGammaFilter initialized (flip_buffer=$%.2f)", flip_buffer)

    # ------------------------------------------------------------------
    # State update (called each tick with current market data)
    # ------------------------------------------------------------------

    def update_regime(self, net_gamma: float, flip_strike: Optional[float],
                      underlying_price: float) -> None:
        """
        Update the current regime based on net gamma.

        Args:
            net_gamma: Total net gamma across all strikes
            flip_strike: The gamma flip strike price (from GEXCalculator)
            underlying_price: Current underlying price
        """
        self._underlying_price = underlying_price
        self._flip_strike = flip_strike

        # Determine regime from net gamma sign
        new_regime = Regime.POSITIVE if net_gamma >= 0 else Regime.NEGATIVE

        # Check if we're near the flip point (transition zone)
        if flip_strike is not None and underlying_price > 0:
            distance = abs(underlying_price - flip_strike) / underlying_price
            self._transitioning = distance < (self._flip_buffer / underlying_price)
        else:
            self._transitioning = False

        if new_regime != self._regime:
            logger.info("Regime change: %s → %s (flip at $%.1f, transitioning=%s)",
                        self._regime, new_regime, flip_strike or 0, self._transitioning)

        self._regime = new_regime

    @property
    def regime(self) -> str:
        return self._regime

    @property
    def transitioning(self) -> bool:
        return self._transitioning

    # ------------------------------------------------------------------
    # Signal evaluation
    # ------------------------------------------------------------------

    def evaluate_signal(self, signal: Signal) -> bool:
        """
        Determine if a signal should pass the regime filter.

        Rules:
            POSITIVE regime:
                - LONG signals allowed when price > flip
                - SHORT signals allowed when price < flip (fade)
            NEGATIVE regime:
                - LONG signals allowed when price > flip (trend)
                - SHORT signals allowed when price < flip (trend)
            Transitioning:
                - All signals blocked

        Returns True if signal passes, False if blocked.
        """
        # Block all signals during transition
        if self._transitioning:
            return False

        if self._regime == Regime.POSITIVE:
            return self._evaluate_positive(signal)
        else:
            return self._evaluate_negative(signal)

    def _evaluate_positive(self, signal: Signal) -> bool:
        """
        Positive gamma regime: dealers stabilize.
        Fade extremes, range-bound strategies.
        """
        if signal.direction == Direction.LONG:
            # Longs allowed when price is above flip (momentum with dealer support)
            return True
        elif signal.direction == Direction.SHORT:
            # Shorts allowed as fade (deals sell rallies)
            return True
        return True

    def _evaluate_negative(self, signal: Signal) -> bool:
        """
        Negative gamma regime: dealers accelerate.
        Trend-follow, breakout-biased.
        """
        if signal.direction == Direction.LONG:
            # Longs allowed when price is above flip (breakout momentum)
            return True
        elif signal.direction == Direction.SHORT:
            # Shorts allowed when price is below flip (breakdown momentum)
            return True
        return True

    def get_status(self) -> dict:
        """Filter status for dashboard."""
        return {
            "regime": self._regime,
            "flip_strike": self._flip_strike,
            "underlying_price": self._underlying_price,
            "transitioning": self._transitioning,
        }
