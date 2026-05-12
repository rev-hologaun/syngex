"""
strategies/rolling_keys.py — Rolling window key constants

All rolling window keys are defined here to prevent typos from silently
creating new windows. Every strategy should import from this module.
"""

from __future__ import annotations

# --- Core price/indicator keys (defined in main.py _rolling_data) ---
KEY_PRICE_5M = "price_5m"
KEY_PRICE_30M = "price_30m"
KEY_NET_GAMMA_5M = "net_gamma_5m"
KEY_VOLUME_5M = "volume_5m"
KEY_VOLUME_DOWN_5M = "volume_down_5m"
KEY_VOLUME_UP_5M = "volume_up_5m"
KEY_TOTAL_DELTA_5M = "total_delta_5m"
KEY_WALL_DELTA_5M = "wall_delta_5m"
KEY_TOTAL_GAMMA_5M = "total_gamma_5m"
KEY_IV_SKEW_5M = "iv_skew_5m"
KEY_ATM_DELTA_5M = "atm_delta_5m"
KEY_ATM_IV_5M = "atm_iv_5m"

# --- Depth / L2 keys (market depth streams) ---
KEY_DEPTH_BID_SIZE_5M = "depth_bid_size_5m"
KEY_DEPTH_ASK_SIZE_5M = "depth_ask_size_5m"
KEY_DEPTH_SPREAD_5M = "depth_spread_5m"
KEY_DEPTH_BID_LEVELS_5M = "depth_bid_levels_5m"
KEY_DEPTH_ASK_LEVELS_5M = "depth_ask_levels_5m"

# --- Squeeze depth rolling keys (liquidity vacuum detection) ---
KEY_DEPTH_BID_SIZE_ROLLING = "depth_bid_size_rolling"
KEY_DEPTH_ASK_SIZE_ROLLING = "depth_ask_size_rolling"

# --- Flow ratio tracking (call_put_flow_asymmetry v2) ---
KEY_FLOW_RATIO_5M = "flow_ratio_5m"

# --- Strategy-specific keys (created by individual strategies) ---
KEY_EXTRINSIC_PROXY_5M = "extrinsic_proxy_5m"
KEY_PROB_MOMENTUM_5M = "prob_momentum_5m"

# --- IV Band Breakout v2 (Breakout-Master) ---
KEY_SKEW_WIDTH_5M = "skew_width_5m"

# --- IV skew gradient (iv_gex_divergence v2) ---
KEY_IV_SKEW_GRADIENT_5M = "iv_skew_gradient_5m"
KEY_GAMMA_DENSITY_5M = "gamma_density_5m"

# --- IV Skew Squeeze v2 (Skew-Velocity) ---
KEY_SKEW_ROC_5M = "skew_roc_5m"
KEY_DELTA_ROC_5M = "delta_roc_5m"

# --- Delta-IV Divergence v2 (Tail-Risk Divergence) ---
KEY_OTM_DELTA_5M = "otm_delta_5m"
KEY_OTM_IV_5M = "otm_iv_5m"
KEY_DELTA_IV_CORR_5M = "delta_iv_corr_5m"

# --- Gamma acceleration tracking (gamma_volume_convergence v2) ---
KEY_GAMMA_ACCEL_5M = "gamma_accel_5m"

# --- Signal tracking keys (used in rolling_data for signal state) ---
KEY_CONSEC_LONG = "consec_long"
KEY_CONSEC_SHORT = "consec_short"

# --- Strike Concentration v2 (Liquidity-Momentum) ---
KEY_STRIKE_DELTA_5M = "strike_delta_5m"
KEY_ATR_5M = "atr_5m"

# --- Prob Weighted Magnet v2 (Velocity-Magnet) ---
KEY_MAGNET_DELTA_5M = "magnet_delta_5m"

# --- Convenience: all core keys in one tuple ---
CORE_KEYS = (
    KEY_PRICE_5M,
    KEY_PRICE_30M,
    KEY_NET_GAMMA_5M,
    KEY_VOLUME_5M,
    KEY_VOLUME_DOWN_5M,
    KEY_VOLUME_UP_5M,
    KEY_TOTAL_DELTA_5M,
    KEY_WALL_DELTA_5M,
    KEY_TOTAL_GAMMA_5M,
    KEY_IV_SKEW_5M,
    KEY_ATM_DELTA_5M,
    KEY_ATM_IV_5M,
    KEY_OTM_DELTA_5M,
    KEY_OTM_IV_5M,
    KEY_DELTA_IV_CORR_5M,
    KEY_SKEW_ROC_5M,
    KEY_DELTA_ROC_5M,
)

# Depth keys tuple
DEPTH_KEYS = (
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_ASK_SIZE_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_DEPTH_BID_LEVELS_5M,
    KEY_DEPTH_ASK_LEVELS_5M,
    KEY_DEPTH_BID_SIZE_ROLLING,
    KEY_DEPTH_ASK_SIZE_ROLLING,
)

# All keys in one tuple for validation
ALL_KEYS = (*CORE_KEYS, *DEPTH_KEYS, KEY_FLOW_RATIO_5M,
            KEY_EXTRINSIC_PROXY_5M, KEY_PROB_MOMENTUM_5M,
            KEY_IV_SKEW_GRADIENT_5M, KEY_GAMMA_DENSITY_5M,
            KEY_OTM_DELTA_5M, KEY_OTM_IV_5M, KEY_DELTA_IV_CORR_5M,
            KEY_GAMMA_ACCEL_5M,
            KEY_CONSEC_LONG, KEY_CONSEC_SHORT,
            KEY_DEPTH_BID_SIZE_ROLLING, KEY_DEPTH_ASK_SIZE_ROLLING,
            KEY_SKEW_WIDTH_5M,
            KEY_STRIKE_DELTA_5M, KEY_ATR_5M,
            KEY_SKEW_ROC_5M, KEY_DELTA_ROC_5M,
            KEY_MAGNET_DELTA_5M)

__all__ = [
    "KEY_PRICE_5M", "KEY_PRICE_30M",
    "KEY_NET_GAMMA_5M",
    "KEY_VOLUME_5M", "KEY_VOLUME_DOWN_5M", "KEY_VOLUME_UP_5M",
    "KEY_TOTAL_DELTA_5M", "KEY_WALL_DELTA_5M", "KEY_TOTAL_GAMMA_5M", "KEY_IV_SKEW_5M",
    "KEY_ATM_DELTA_5M", "KEY_ATM_IV_5M",
    "KEY_OTM_DELTA_5M", "KEY_OTM_IV_5M", "KEY_DELTA_IV_CORR_5M",
    "KEY_FLOW_RATIO_5M",
    "KEY_IV_SKEW_GRADIENT_5M", "KEY_GAMMA_DENSITY_5M",
    "KEY_DEPTH_BID_SIZE_5M", "KEY_DEPTH_ASK_SIZE_5M", "KEY_DEPTH_SPREAD_5M",
    "KEY_DEPTH_BID_LEVELS_5M", "KEY_DEPTH_ASK_LEVELS_5M",
    "KEY_DEPTH_BID_SIZE_ROLLING", "KEY_DEPTH_ASK_SIZE_ROLLING",
    "KEY_EXTRINSIC_PROXY_5M", "KEY_PROB_MOMENTUM_5M",
    "KEY_GAMMA_ACCEL_5M",
    "KEY_CONSEC_LONG", "KEY_CONSEC_SHORT",
    "KEY_SKEW_WIDTH_5M",
    "KEY_STRIKE_DELTA_5M", "KEY_ATR_5M",
    "KEY_SKEW_ROC_5M", "KEY_DELTA_ROC_5M",
    "KEY_MAGNET_DELTA_5M",
    "CORE_KEYS", "DEPTH_KEYS", "ALL_KEYS",
]
