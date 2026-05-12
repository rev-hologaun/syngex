"""
config/trade_guard.py — Safety guard for live environments

READ_ONLY = True  → blocks all order placement (live env safety)
READ_ONLY = False → allows live order placement (dev/test only)
"""

import functools
import logging

logger = logging.getLogger(__name__)

READ_ONLY = True  # KEEP TRUE IN LIVE ENVIRONMENTS


class ReadOnlyError(RuntimeError):
    """Raised when order placement is attempted in READ_ONLY mode."""


def enforce_read_only(fn=None, *, raise_error=True):
    """Decorator to enforce READ_ONLY mode on order placement functions.

    Usage:
        @enforce_read_only
        def place_order(...):
            ...

        # Or with custom error message:
        @enforce_read_only(raise_error=False)
        def place_order(...):
            ...  # Returns None instead of raising
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if READ_ONLY:
                msg = f"Order placement blocked: {func.__name__}() in READ_ONLY mode"
                logger.warning(msg)
                if raise_error:
                    raise ReadOnlyError(msg)
                return None
            return func(*args, **kwargs)
        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator
