"""
data/stream_processor_stubs.py — Stub functions for backward compatibility

These stub functions provide backward compatibility for code that expects
standalone process_* functions. In the refactored architecture, these
functions are methods of the StreamProcessor class.
"""

from typing import Any, Dict, Tuple


def process_underlying_update(
    data: Dict[str, Any],
    rolling_data: Dict[str, Any],
    calculator: Any,
    call_update_count: int,
    put_update_count: int,
    ts: float
) -> Tuple[int, int]:
    """Stub for process_underlying_update.
    
    Returns the input counts unchanged. Actual processing should be done
    via StreamProcessor._process_underlying_update method.
    """
    return call_update_count, put_update_count


def process_option_update(
    data: Dict[str, Any],
    rolling_data: Dict[str, Any],
    calculator: Any,
    gex_summary: Dict[str, Any],
    phi_call_tick: int,
    phi_put_tick: int,
    ts: float
) -> Tuple[int, int]:
    """Stub for process_option_update.
    
    Returns the input ticks unchanged. Actual processing should be done
    via StreamProcessor._process_option_update method.
    """
    return phi_call_tick, phi_put_tick


def process_market_depth(
    data: Dict[str, Any],
    rolling_data: Dict[str, Any],
    exchange_bid_sizes: Dict[str, int],
    exchange_ask_sizes: Dict[str, int],
    ts: float
) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Stub for process_market_depth.
    
    Returns the input sizes unchanged. Actual processing should be done
    via StreamProcessor._process_market_depth method.
    """
    return exchange_bid_sizes, exchange_ask_sizes
