"""
Sample GEX data fixtures for testing.

Provides realistic OHLCV data, option chain data, and GEX snapshots
for unit and integration tests.
"""

from typing import Any, Dict, List


# =============================================================================
# Sample OHLCV Data
# =============================================================================

SAMPLE_OHLCV_DATA: List[Dict[str, Any]] = [
    {
        "timestamp": 1716072000.0,  # 2024-05-19 09:30:00 PST
        "open": 194.50,
        "high": 195.20,
        "low": 194.30,
        "close": 195.00,
        "volume": 125000,
    },
    {
        "timestamp": 1716072060.0,  # 09:31:00
        "open": 195.00,
        "high": 195.80,
        "low": 194.90,
        "close": 195.50,
        "volume": 98000,
    },
    {
        "timestamp": 1716072120.0,  # 09:32:00
        "open": 195.50,
        "high": 196.00,
        "low": 195.30,
        "close": 195.75,
        "volume": 110000,
    },
    {
        "timestamp": 1716072180.0,  # 09:33:00
        "open": 195.75,
        "high": 196.20,
        "low": 195.60,
        "close": 196.00,
        "volume": 135000,
    },
    {
        "timestamp": 1716072240.0,  # 09:34:00
        "open": 196.00,
        "high": 196.50,
        "low": 195.80,
        "close": 196.25,
        "volume": 142000,
    },
]


# =============================================================================
# Sample Option Chain Data
# =============================================================================

SAMPLE_OPTION_CHAIN: List[Dict[str, Any]] = [
    # Call options
    {
        "type": "option_update",
        "symbol": "TSLA240519C00190000",
        "strike": 190.0,
        "side": "call",
        "gamma": 0.015,
        "delta": 0.75,
        "open_interest": 2500.0,
        "iv": 0.52,
        "volume": 150,
    },
    {
        "type": "option_update",
        "symbol": "TSLA240519C00195000",
        "strike": 195.0,
        "side": "call",
        "gamma": 0.025,
        "delta": 0.55,
        "open_interest": 3200.0,
        "iv": 0.48,
        "volume": 280,
    },
    {
        "type": "option_update",
        "symbol": "TSLA240519C00200000",
        "strike": 200.0,
        "side": "call",
        "gamma": 0.018,
        "delta": 0.35,
        "open_interest": 4100.0,
        "iv": 0.45,
        "volume": 320,
    },
    {
        "type": "option_update",
        "symbol": "TSLA240519C00205000",
        "strike": 205.0,
        "side": "call",
        "gamma": 0.012,
        "delta": 0.20,
        "open_interest": 1800.0,
        "iv": 0.43,
        "volume": 95,
    },
    # Put options
    {
        "type": "option_update",
        "symbol": "TSLA240519P00190000",
        "strike": 190.0,
        "side": "put",
        "gamma": 0.014,
        "delta": -0.25,
        "open_interest": 1800.0,
        "iv": 0.54,
        "volume": 120,
    },
    {
        "type": "option_update",
        "symbol": "TSLA240519P00195000",
        "strike": 195.0,
        "side": "put",
        "gamma": 0.022,
        "delta": -0.45,
        "open_interest": 2900.0,
        "iv": 0.50,
        "volume": 210,
    },
    {
        "type": "option_update",
        "symbol": "TSLA240519P00200000",
        "strike": 200.0,
        "side": "put",
        "gamma": 0.016,
        "delta": -0.65,
        "open_interest": 3500.0,
        "iv": 0.47,
        "volume": 275,
    },
    {
        "type": "option_update",
        "symbol": "TSLA240519P00205000",
        "strike": 205.0,
        "side": "put",
        "gamma": 0.010,
        "delta": -0.80,
        "open_interest": 1200.0,
        "iv": 0.45,
        "volume": 85,
    },
]


# =============================================================================
# Sample Underlying Price Updates
# =============================================================================

SAMPLE_UNDERLYING_UPDATES: List[Dict[str, Any]] = [
    {
        "type": "underlying_update",
        "symbol": "TSLA",
        "price": 195.00,
        "timestamp": 1716072000.0,
    },
    {
        "type": "underlying_update",
        "symbol": "TSLA",
        "price": 195.50,
        "timestamp": 1716072060.0,
    },
    {
        "type": "underlying_update",
        "symbol": "TSLA",
        "price": 196.00,
        "timestamp": 1716072120.0,
    },
]


# =============================================================================
# Sample GEX Snapshots
# =============================================================================

SAMPLE_GEX_SNAPSHOT_POSITIVE_REGIME: Dict[str, Any] = {
    "symbol": "TSLA",
    "underlying_price": 195.50,
    "net_gamma": 1250.5,  # Positive regime
    "total_call_gamma": 2800.0,
    "total_put_gamma": 1549.5,
    "gamma_flip_strike": 194.0,
    "strikes": {
        190.0: {
            "call_gamma": 0.015 * 2500,
            "put_gamma": 0.014 * 1800,
            "net_gamma": (0.015 * 2500) - (0.014 * 1800),
        },
        195.0: {
            "call_gamma": 0.025 * 3200,
            "put_gamma": 0.022 * 2900,
            "net_gamma": (0.025 * 3200) - (0.022 * 2900),
        },
        200.0: {
            "call_gamma": 0.018 * 4100,
            "put_gamma": 0.016 * 3500,
            "net_gamma": (0.018 * 4100) - (0.016 * 3500),
        },
    },
}


SAMPLE_GEX_SNAPSHOT_NEGATIVE_REGIME: Dict[str, Any] = {
    "symbol": "TSLA",
    "underlying_price": 193.50,
    "net_gamma": -850.2,  # Negative regime
    "total_call_gamma": 1200.0,
    "total_put_gamma": 2050.2,
    "gamma_flip_strike": 195.0,
    "strikes": {
        190.0: {
            "call_gamma": 0.010 * 1500,
            "put_gamma": 0.020 * 2200,
            "net_gamma": (0.010 * 1500) - (0.020 * 2200),
        },
        195.0: {
            "call_gamma": 0.018 * 2000,
            "put_gamma": 0.028 * 3500,
            "net_gamma": (0.018 * 2000) - (0.028 * 3500),
        },
        200.0: {
            "call_gamma": 0.012 * 2800,
            "put_gamma": 0.018 * 3000,
            "net_gamma": (0.012 * 2800) - (0.018 * 3000),
        },
    },
}


# =============================================================================
# Sample Gamma Walls
# =============================================================================

SAMPLE_GAMMA_WALLS: List[Dict[str, Any]] = [
    {
        "strike": 200.0,
        "net_gamma": 2500.0,
        "gex": 487500.0,  # net_gamma * underlying_price
        "side": "call",
        "total_contracts": 7500,
    },
    {
        "strike": 195.0,
        "net_gamma": -1800.0,
        "gex": -351000.0,
        "side": "put",
        "total_contracts": 6100,
    },
    {
        "strike": 190.0,
        "net_gamma": 1200.0,
        "gex": 234000.0,
        "side": "call",
        "total_contracts": 4300,
    },
]


# =============================================================================
# Helper Functions
# =============================================================================

def get_sample_greeks_summary() -> Dict[str, Any]:
    """Get a sample greeks summary dict."""
    return {
        "net_delta": 1250.5,
        "net_gamma": 1250.5,
        "total_volume": 15000,
        "call_volume": 8500,
        "put_volume": 6500,
        "underlying_price": 195.50,
    }


def get_sample_strike_bucket_data() -> Dict[str, Any]:
    """Get sample data for a single strike bucket."""
    return {
        "strike": 195.0,
        "call_gamma_oi": 80.0,  # 0.025 * 3200
        "put_gamma_oi": 63.8,   # 0.022 * 2900
        "call_gamma": 0.025,
        "put_gamma": 0.022,
        "call_oi": 3200.0,
        "put_oi": 2900.0,
        "call_delta": 0.55,
        "put_delta": -0.45,
        "call_iv_sum": 0.48,
        "put_iv_sum": 0.50,
        "call_count": 1,
        "put_count": 1,
    }
