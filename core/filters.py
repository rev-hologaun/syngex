"""Core filters for Syngex - regime filtering and signal validation."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional


class Regime(str, Enum):
    """Gamma regime states."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class NetGammaFilter:
    """Net Gamma Regime Filter.

    Master filter that gates ALL strategy signals based on the current
    gamma regime.

    Logic:
        - Positive Net Gamma → dealers buy dips, sell rallies → fade extremes
        - Negative Net Gamma → dealers sell dips, buy rallies → trend-follow

    A signal is only allowed if it aligns with the current regime.

    Usage:
        filter = NetGammaFilter(flip_buffer=0.50)
        ...
        filter.check_regime(net_gamma, flip_strike, underlying_price)
        if filter.check_signal(signal):
            # signal passes
    """

    def __init__(self, flip_buffer: float = 0.50) -> None:
        """Initialize the filter.

        Args:
            flip_buffer: Distance (in $) around the flip point where
                        regime is considered "transitioning" and signals
                        are blocked to avoid whipsaws.
        """
        self._flip_buffer = flip_buffer
        self._regime: Regime = Regime.POSITIVE  # Default to positive
        self._flip_strike: Optional[float] = None
        self._underlying_price: float = 0.0
        self._transitioning: bool = False

        logger = logging.getLogger("Syngex.Core.NetGammaFilter")
        logger.info("NetGammaFilter initialized (flip_buffer=$%.2f)", flip_buffer)

    def check_regime(self, net_gamma: float, flip_strike: Optional[float],
                     underlying_price: float) -> bool:
        """Check if the current signal passes the regime filter.

        Updates the internal regime state based on current market data,
        then determines if a signal would be allowed.

        Args:
            net_gamma: Total net gamma across all strikes.
            flip_strike: The gamma flip strike price (from GEXCalculator).
            underlying_price: Current underlying price.

        Returns:
            True if signals are allowed (not transitioning), False if blocked.
        """
        # Update internal state
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

        # Log regime changes
        if new_regime != self._regime:
            self.notify_regime_change(self._regime, new_regime)

        self._regime = new_regime

        # Block all signals during transition
        return not self._transitioning

    def get_status(self) -> dict:
        """Get the current filter status.

        Returns:
            Dict with regime, flip_strike, underlying_price, and transitioning.
        """
        return {
            "regime": self._regime.value,
            "flip_strike": self._flip_strike,
            "underlying_price": self._underlying_price,
            "transitioning": self._transitioning,
        }

    def notify_regime_change(self, old_regime: Regime, new_regime: Regime) -> None:
        """Log a regime change event.

        Args:
            old_regime: The previous regime state.
            new_regime: The new regime state.
        """
        logger = logging.getLogger("Syngex.Core.NetGammaFilter")
        logger.info(
            "Regime change: %s → %s (flip at $%.1f, transitioning=%s)",
            old_regime.value,
            new_regime.value,
            self._flip_strike or 0,
            self._transitioning
        )

    @property
    def regime(self) -> Regime:
        """Get the current regime state."""
        return self._regime

    @property
    def transitioning(self) -> bool:
        """Get the transitioning state."""
        return self._transitioning

    @property
    def flip_buffer(self) -> float:
        """Get the flip buffer value."""
        return self._flip_buffer

    @flip_buffer.setter
    def flip_buffer(self, value: float) -> None:
        """Set the flip buffer value."""
        self._flip_buffer = value
        logger = logging.getLogger("Syngex.Core.NetGammaFilter")
        logger.info("Flip buffer updated to $%.2f", value)
