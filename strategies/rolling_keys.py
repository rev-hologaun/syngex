"""
strategies/rolling_keys.py — Rolling window key constants

All rolling window keys are defined here to prevent typos from silently
creating new windows. Every strategy should import from this module.
"""

from __future__ import annotations

# --- Core price/indicator keys (defined in main.py _rolling_data) ---
KEY_PRICE = "price"
KEY_PRICE_5M = "price_5m"
KEY_PRICE_30M = "price_30m"
KEY_NET_GAMMA = "net_gamma"
KEY_NET_GAMMA_5M = "net_gamma_5m"
KEY_VOLUME = "volume"
KEY_VOLUME_5M = "volume_5m"
KEY_VOLUME_DOWN_5M = "volume_down_5m"
KEY_VOLUME_UP_5M = "volume_up_5m"
KEY_TOTAL_DELTA_5M = "total_delta_5m"
KEY_DELTA = "delta"
KEY_TOTAL_GAMMA_5M = "total_gamma_5m"
KEY_IV_SKEW_5M = "iv_skew_5m"

# --- Strategy-specific keys (created by individual strategies) ---
KEY_EXTRINSIC_PROXY_5M = "extrinsic_proxy_5m"
KEY_PROB_MOMENTUM_5M = "prob_momentum_5m"

# --- Signal tracking keys (used in rolling_data for signal state) ---
KEY_CONSEC_LONG = "consec_long"
KEY_CONSEC_SHORT = "consec_short"

# --- Convenience: all core keys in one tuple ---
CORE_KEYS = (
    KEY_PRICE,
    KEY_PRICE_5M,
    KEY_PRICE_30M,
    KEY_NET_GAMMA,
    KEY_NET_GAMMA_5M,
    KEY_VOLUME,
    KEY_VOLUME_5M,
    KEY_VOLUME_DOWN_5M,
    KEY_VOLUME_UP_5M,
    KEY_TOTAL_DELTA_5M,
    KEY_DELTA,
    KEY_TOTAL_GAMMA_5M,
    KEY_IV_SKEW_5M,
)

# All keys in one tuple for validation
ALL_KEYS = (*CORE_KEYS, KEY_EXTRINSIC_PROXY_5M, KEY_PROB_MOMENTUM_5M,
            KEY_CONSEC_LONG, KEY_CONSEC_SHORT)

__all__ = [
    "KEY_PRICE", "KEY_PRICE_5M", "KEY_PRICE_30M",
    "KEY_NET_GAMMA", "KEY_NET_GAMMA_5M",
    "KEY_VOLUME", "KEY_VOLUME_5M", "KEY_VOLUME_DOWN_5M", "KEY_VOLUME_UP_5M",
    "KEY_TOTAL_DELTA_5M", "KEY_DELTA", "KEY_TOTAL_GAMMA_5M", "KEY_IV_SKEW_5M",
    "KEY_EXTRINSIC_PROXY_5M", "KEY_PROB_MOMENTUM_5M",
    "KEY_CONSEC_LONG", "KEY_CONSEC_SHORT",
    "CORE_KEYS", "ALL_KEYS",
]
