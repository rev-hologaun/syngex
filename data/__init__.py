"""
data package — Data stream processing and rolling keys.

Modules:
    rolling_keys_ext: Extended rolling window key constants
    stream_processor: Data stream processing functions
"""

from .rolling_keys_ext import (
    EXTENDED_KEYS,
    EXTENDED_ROLLING_WINDOW_SIZES,
    # Skew PSI
    KEY_SKEW_PSI_5M,
    KEY_SKEW_PSI_ROC_5M,
    KEY_SKEW_PSI_SIGMA_5M,
    # Smile Omega
    KEY_CURVE_OMEGA_5M,
    KEY_CURVE_OMEGA_ROC_5M,
    KEY_CURVE_OMEGA_SIGMA_5M,
    KEY_PUT_SLOPE_5M,
    KEY_CALL_SLOPE_5M,
    # Phi accumulators
    KEY_PHI_CALL_5M,
    KEY_PHI_PUT_5M,
    KEY_PHI_RATIO_5M,
    KEY_PHI_TOTAL_5M,
    KEY_PHI_TOTAL_SIGMA_5M,
    # Delta-IV divergence
    KEY_OTM_DELTA_5M,
    KEY_OTM_IV_5M,
    KEY_DELTA_IV_CORR_5M,
    # VAMP
    KEY_VAMP_5M,
    KEY_VAMP_MID_DEV_5M,
    KEY_VAMP_ROC_5M,
    KEY_VAMP_PARTICIPANTS_5M,
    KEY_VAMP_DEPTH_DENSITY_5M,
    KEY_VAMP_LEVELS,
    # Depth decay
    KEY_DEPTH_DECAY_BID_5M,
    KEY_DEPTH_DECAY_ASK_5M,
    KEY_DEPTH_TOP5_BID_5M,
    KEY_DEPTH_TOP5_ASK_5M,
    KEY_DEPTH_VOL_RATIO_5M,
    # IR
    KEY_IR_5M,
    KEY_IR_ROC_5M,
    KEY_IR_PARTICIPANTS_5M,
    # Gamma breaker
    KEY_GAMMA_BREAK_INDEX_5M,
    KEY_PRICE_VELOCITY_5M,
    # Magnet delta
    KEY_MAGNET_DELTA_5M,
    # Skew width
    KEY_SKEW_WIDTH_5M,
    # IV-GEX divergence
    KEY_IV_SKEW_GRADIENT_5M,
    KEY_GAMMA_DENSITY_5M,
    # Strike delta
    KEY_STRIKE_DELTA_5M,
    # ATR
    KEY_ATR_5M,
    # Momentum ROC
    KEY_MOMENTUM_ROC_5M,
    # Wall tracking
    KEY_WALL_DISTANCE_5M,
    KEY_WALL_GEX_5M,
    KEY_WALL_GEX_SIGMA_5M,
    KEY_WALL_DELTA_5M,
    # Confluence
    KEY_CONFLUENCE_PROX_5M,
    KEY_CONFLUENCE_SIGNAL_5M,
    KEY_LIQUIDITY_WALL_SIZE_5M,
    KEY_LIQUIDITY_WALL_SIGMA_5M,
    # Sync
    KEY_SYNC_CORR_5M,
    KEY_SYNC_SIGMA_5M,
    KEY_SKEW_CHANGE_5M,
    KEY_VSI_MAGNITUDE_5M,
    # Whale tracker
    KEY_BIGGEST_SIZE_5M,
    KEY_SMALLEST_SIZE_5M,
    KEY_CONCENTRATION_RATIO_5M,
    KEY_CONCENTRATION_SIGMA_5M,
    KEY_NUM_PARTICIPANTS_5M,
    # Vortex compression
    KEY_SPREAD_ZSCORE_5M,
    KEY_LIQUIDITY_DENSITY_5M,
    KEY_PARTICIPANT_EQUILIBRIUM_5M,
    KEY_VOLUME_SPIKE_5M,
    # Market depth
    KEY_MARKET_DEPTH_AGG,
    # PDR
    KEY_PDR_5M,
    KEY_PDR_ROC_5M,
)

from .stream_processor import (
    process_underlying_update,
    process_option_update,
    process_market_depth,
    _compute_linear_slope,
)

__all__ = [
    # Rolling keys exports
    "EXTENDED_KEYS",
    "EXTENDED_ROLLING_WINDOW_SIZES",
    "KEY_SKEW_PSI_5M",
    "KEY_SKEW_PSI_ROC_5M",
    "KEY_SKEW_PSI_SIGMA_5M",
    "KEY_CURVE_OMEGA_5M",
    "KEY_CURVE_OMEGA_ROC_5M",
    "KEY_CURVE_OMEGA_SIGMA_5M",
    "KEY_PUT_SLOPE_5M",
    "KEY_CALL_SLOPE_5M",
    "KEY_PHI_CALL_5M",
    "KEY_PHI_PUT_5M",
    "KEY_PHI_RATIO_5M",
    "KEY_PHI_TOTAL_5M",
    "KEY_PHI_TOTAL_SIGMA_5M",
    "KEY_OTM_DELTA_5M",
    "KEY_OTM_IV_5M",
    "KEY_DELTA_IV_CORR_5M",
    "KEY_VAMP_5M",
    "KEY_VAMP_MID_DEV_5M",
    "KEY_VAMP_ROC_5M",
    "KEY_VAMP_PARTICIPANTS_5M",
    "KEY_VAMP_DEPTH_DENSITY_5M",
    "KEY_VAMP_LEVELS",
    "KEY_DEPTH_DECAY_BID_5M",
    "KEY_DEPTH_DECAY_ASK_5M",
    "KEY_DEPTH_TOP5_BID_5M",
    "KEY_DEPTH_TOP5_ASK_5M",
    "KEY_DEPTH_VOL_RATIO_5M",
    "KEY_IR_5M",
    "KEY_IR_ROC_5M",
    "KEY_IR_PARTICIPANTS_5M",
    "KEY_GAMMA_BREAK_INDEX_5M",
    "KEY_PRICE_VELOCITY_5M",
    "KEY_MAGNET_DELTA_5M",
    "KEY_SKEW_WIDTH_5M",
    "KEY_IV_SKEW_GRADIENT_5M",
    "KEY_GAMMA_DENSITY_5M",
    "KEY_STRIKE_DELTA_5M",
    "KEY_ATR_5M",
    "KEY_MOMENTUM_ROC_5M",
    "KEY_WALL_DISTANCE_5M",
    "KEY_WALL_GEX_5M",
    "KEY_WALL_GEX_SIGMA_5M",
    "KEY_WALL_DELTA_5M",
    "KEY_CONFLUENCE_PROX_5M",
    "KEY_CONFLUENCE_SIGNAL_5M",
    "KEY_LIQUIDITY_WALL_SIZE_5M",
    "KEY_LIQUIDITY_WALL_SIGMA_5M",
    "KEY_SYNC_CORR_5M",
    "KEY_SYNC_SIGMA_5M",
    "KEY_SKEW_CHANGE_5M",
    "KEY_VSI_MAGNITUDE_5M",
    "KEY_BIGGEST_SIZE_5M",
    "KEY_SMALLEST_SIZE_5M",
    "KEY_CONCENTRATION_RATIO_5M",
    "KEY_CONCENTRATION_SIGMA_5M",
    "KEY_NUM_PARTICIPANTS_5M",
    "KEY_SPREAD_ZSCORE_5M",
    "KEY_LIQUIDITY_DENSITY_5M",
    "KEY_PARTICIPANT_EQUILIBRIUM_5M",
    "KEY_VOLUME_SPIKE_5M",
    "KEY_MARKET_DEPTH_AGG",
    "KEY_PDR_5M",
    "KEY_PDR_ROC_5M",
    # Stream processor exports
    "process_underlying_update",
    "process_option_update",
    "process_market_depth",
    "_compute_linear_slope",
]
