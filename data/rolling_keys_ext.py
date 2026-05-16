"""
data/rolling_keys_ext.py — Extended Rolling Window Key Constants

Extended key definitions for metrics computed in the stream processor.
These complement the core keys in strategies/rolling_keys.py.

All metrics here are computed from underlying/option updates and market depth
streams, then pushed into rolling windows for strategy consumption.
"""

from __future__ import annotations

# ── IV Skew Dynamics (SKEW-ALPHA) ──
KEY_SKEW_PSI_5M = "skew_psi_5m"
KEY_SKEW_PSI_ROC_5M = "skew_psi_roc_5m"
KEY_SKEW_PSI_SIGMA_5M = "skew_psi_sigma_5m"

# ── IV Smile Dynamics (CURVE-ALPHA) ──
KEY_CURVE_OMEGA_5M = "curve_omega_5m"
KEY_CURVE_OMEGA_ROC_5M = "curve_omega_roc_5m"
KEY_CURVE_OMEGA_SIGMA_5M = "curve_omega_sigma_5m"
KEY_PUT_SLOPE_5M = "put_slope_5m"
KEY_CALL_SLOPE_5M = "call_slope_5m"

# ── Extrinsic Value Flow (EXTRINSIC-ALPHA) ──
KEY_PHI_CALL_5M = "phi_call_5m"
KEY_PHI_PUT_5M = "phi_put_5m"
KEY_PHI_RATIO_5M = "phi_ratio_5m"
KEY_PHI_TOTAL_5M = "phi_total_5m"
KEY_PHI_TOTAL_SIGMA_5M = "phi_total_sigma_5m"

# ── Delta-IV Divergence v2 (Tail-Risk Divergence) ──
KEY_OTM_DELTA_5M = "otm_delta_5m"
KEY_OTM_IV_5M = "otm_iv_5m"
KEY_DELTA_IV_CORR_5M = "delta_iv_corr_5m"

# ── VAMP Momentum (Volume-Adjusted Mid-Price Momentum) ──
KEY_VAMP_5M = "vamp_5m"
KEY_VAMP_MID_DEV_5M = "vamp_mid_dev_5m"
KEY_VAMP_ROC_5M = "vamp_roc_5m"
KEY_VAMP_PARTICIPANTS_5M = "vamp_participants_5m"
KEY_VAMP_DEPTH_DENSITY_5M = "vamp_depth_density_5m"
KEY_VAMP_LEVELS = "vamp_levels"

# ── Depth Decay Momentum ──
KEY_DEPTH_DECAY_BID_5M = "depth_decay_bid_5m"
KEY_DEPTH_DECAY_ASK_5M = "depth_decay_ask_5m"
KEY_DEPTH_TOP5_BID_5M = "depth_top5_bid_5m"
KEY_DEPTH_TOP5_ASK_5M = "depth_top5_ask_5m"
KEY_DEPTH_VOL_RATIO_5M = "depth_vol_ratio_5m"

# ── Depth Imbalance Momentum ──
KEY_IR_5M = "imbalance_ratio_5m"
KEY_IR_ROC_5M = "imbalance_ratio_roc_5m"
KEY_IR_PARTICIPANTS_5M = "ir_participants_5m"

# ── Gamma Breaker ──
KEY_GAMMA_BREAK_INDEX_5M = "gamma_break_5m"
KEY_PRICE_VELOCITY_5M = "price_velocity_5m"

# ── Prob Weighted Magnet v2 ──
KEY_MAGNET_DELTA_5M = "magnet_delta_5m"

# ── IV Band Breakout v2 ──
KEY_SKEW_WIDTH_5M = "skew_width_5m"

# ── IV-GEX Divergence v2 ──
KEY_IV_SKEW_GRADIENT_5M = "iv_skew_gradient_5m"
KEY_GAMMA_DENSITY_5M = "gamma_density_5m"

# ── Strike Concentration v2 ──
KEY_STRIKE_DELTA_5M = "strike_delta_5m"

# ── ATR Calculation ──
KEY_ATR_5M = "atr_5m"

# ── Prob Distribution Shift v2 ──
KEY_MOMENTUM_ROC_5M = "momentum_roc_5m"

# ── Wall Tracking ──
KEY_WALL_DISTANCE_5M = "wall_distance_5m"
KEY_WALL_GEX_5M = "wall_gex_5m"
KEY_WALL_GEX_SIGMA_5M = "wall_gex_sigma_5m"
KEY_WALL_DELTA_5M = "wall_delta_5m"

# ── Iron Anchor ──
KEY_CONFLUENCE_PROX_5M = "confluence_prox_5m"
KEY_CONFLUENCE_SIGNAL_5M = "confluence_signal_5m"
KEY_LIQUIDITY_WALL_SIZE_5M = "liq_wall_size_5m"
KEY_LIQUIDITY_WALL_SIGMA_5M = "liq_wall_sigma_5m"

# ── Sentiment Sync ──
KEY_SYNC_CORR_5M = "sync_corr_5m"
KEY_SYNC_SIGMA_5M = "sync_sigma_5m"
KEY_SKEW_CHANGE_5M = "skew_change_5m"
KEY_VSI_MAGNITUDE_5M = "vsi_magnitude_5m"

# ── Whale Tracker ──
KEY_BIGGEST_SIZE_5M = "biggest_size_5m"
KEY_SMALLEST_SIZE_5M = "smallest_size_5m"
KEY_CONCENTRATION_RATIO_5M = "conc_ratio_5m"
KEY_CONCENTRATION_SIGMA_5M = "conc_sigma_5m"
KEY_NUM_PARTICIPANTS_5M = "num_participants_5m"

# ── Vortex Compression Breakout ──
KEY_SPREAD_ZSCORE_5M = "spread_zscore_5m"
KEY_LIQUIDITY_DENSITY_5M = "liquidity_density_5m"
KEY_PARTICIPANT_EQUILIBRIUM_5M = "participant_equilibrium_5m"
KEY_VOLUME_SPIKE_5M = "volume_spike_5m"

# ── Market Depth Aggregation ──
KEY_MARKET_DEPTH_AGG = "market_depth_agg"

# ── Ghost Premium (TVD-Alpha) ──
KEY_PDR_5M = "pdr_5m"
KEY_PDR_ROC_5M = "pdr_roc_5m"

# ── Extended Window Sizes ──
# Non-default window sizes for RollingWindow initialization
EXTENDED_ROLLING_WINDOW_SIZES: dict[str, int] = {
    KEY_SKEW_PSI_5M: 900,
    KEY_SKEW_PSI_ROC_5M: 900,
    KEY_SKEW_PSI_SIGMA_5M: 900,
    KEY_CURVE_OMEGA_5M: 900,
    KEY_CURVE_OMEGA_ROC_5M: 900,
    KEY_CURVE_OMEGA_SIGMA_5M: 900,
    KEY_PUT_SLOPE_5M: 900,
    KEY_CALL_SLOPE_5M: 900,
    KEY_SYNC_CORR_5M: 900,
    KEY_SYNC_SIGMA_5M: 900,
    KEY_SKEW_CHANGE_5M: 900,
    KEY_VSI_MAGNITUDE_5M: 900,
    KEY_BIGGEST_SIZE_5M: 900,
    KEY_SMALLEST_SIZE_5M: 900,
    KEY_CONCENTRATION_RATIO_5M: 900,
    KEY_CONCENTRATION_SIGMA_5M: 900,
    KEY_NUM_PARTICIPANTS_5M: 900,
}

# ── Extended Keys Tuple ──
# All extended keys for validation and iteration
EXTENDED_KEYS = (
    KEY_SKEW_PSI_5M, KEY_SKEW_PSI_ROC_5M, KEY_SKEW_PSI_SIGMA_5M,
    KEY_CURVE_OMEGA_5M, KEY_CURVE_OMEGA_ROC_5M, KEY_CURVE_OMEGA_SIGMA_5M,
    KEY_PUT_SLOPE_5M, KEY_CALL_SLOPE_5M,
    KEY_PHI_CALL_5M, KEY_PHI_PUT_5M, KEY_PHI_RATIO_5M,
    KEY_PHI_TOTAL_5M, KEY_PHI_TOTAL_SIGMA_5M,
    KEY_OTM_DELTA_5M, KEY_OTM_IV_5M, KEY_DELTA_IV_CORR_5M,
    KEY_VAMP_5M, KEY_VAMP_MID_DEV_5M, KEY_VAMP_ROC_5M,
    KEY_VAMP_PARTICIPANTS_5M, KEY_VAMP_DEPTH_DENSITY_5M,
    KEY_DEPTH_DECAY_BID_5M, KEY_DEPTH_DECAY_ASK_5M,
    KEY_DEPTH_TOP5_BID_5M, KEY_DEPTH_TOP5_ASK_5M,
    KEY_DEPTH_VOL_RATIO_5M,
    KEY_IR_5M, KEY_IR_ROC_5M, KEY_IR_PARTICIPANTS_5M,
    KEY_GAMMA_BREAK_INDEX_5M, KEY_PRICE_VELOCITY_5M,
    KEY_MAGNET_DELTA_5M,
    KEY_SKEW_WIDTH_5M,
    KEY_IV_SKEW_GRADIENT_5M, KEY_GAMMA_DENSITY_5M,
    KEY_STRIKE_DELTA_5M,
    KEY_ATR_5M,
    KEY_MOMENTUM_ROC_5M,
    KEY_WALL_DISTANCE_5M, KEY_WALL_GEX_5M, KEY_WALL_GEX_SIGMA_5M,
    KEY_WALL_DELTA_5M,
    KEY_CONFLUENCE_PROX_5M, KEY_CONFLUENCE_SIGNAL_5M,
    KEY_LIQUIDITY_WALL_SIZE_5M, KEY_LIQUIDITY_WALL_SIGMA_5M,
    KEY_SYNC_CORR_5M, KEY_SYNC_SIGMA_5M, KEY_SKEW_CHANGE_5M,
    KEY_VSI_MAGNITUDE_5M,
    KEY_BIGGEST_SIZE_5M, KEY_SMALLEST_SIZE_5M,
    KEY_CONCENTRATION_RATIO_5M, KEY_CONCENTRATION_SIGMA_5M,
    KEY_NUM_PARTICIPANTS_5M,
    KEY_SPREAD_ZSCORE_5M, KEY_LIQUIDITY_DENSITY_5M,
    KEY_PARTICIPANT_EQUILIBRIUM_5M, KEY_VOLUME_SPIKE_5M,
    KEY_PDR_5M, KEY_PDR_ROC_5M,
)
