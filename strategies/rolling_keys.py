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

# --- SI Component keys (Structural Integrity) ---
KEY_DELTA_DENSITY_5M = "delta_density_5m"
KEY_VOLUME_ZSCORE_5M = "volume_zscore_5m"
KEY_ORDER_BOOK_DEPTH_5M = "order_book_depth_5m"

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
KEY_EXTRINSIC_ROC_5M = "extrinsic_roc_5m"
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

# --- Signal tracking keys (used in rolling_data for signal state) ---
KEY_CONSEC_LONG = "consec_long"
KEY_CONSEC_SHORT = "consec_short"

# --- Strike Concentration v2 (Liquidity-Momentum) ---
KEY_STRIKE_DELTA_5M = "strike_delta_5m"
KEY_ATR_5M = "atr_5m"

# --- Prob Weighted Magnet v2 (Velocity-Magnet) ---
KEY_MAGNET_DELTA_5M = "magnet_delta_5m"

# --- Prob Distribution Shift v2 (Momentum-Master) ---
KEY_MOMENTUM_ROC_5M = "momentum_roc_5m"

# --- VAMP Momentum (Volume-Adjusted Mid-Price Momentum) ---
KEY_VAMP_5M = "vamp_5m"
KEY_VAMP_MID_DEV_5M = "vamp_mid_dev_5m"
KEY_VAMP_ROC_5M = "vamp_roc_5m"
KEY_VAMP_PARTICIPANTS_5M = "vamp_participants_5m"
KEY_VAMP_DEPTH_DENSITY_5M = "vamp_depth_density_5m"

# --- OBI + Aggression Flow ---
KEY_OBI_5M = "obi_5m"
KEY_AGGRESSIVE_BUY_VOL_5M = "aggressive_buy_vol_5m"
KEY_AGGRESSIVE_SELL_VOL_5M = "aggressive_sell_vol_5m"
KEY_AF_5M = "aggression_flow_5m"
KEY_TRADE_SIZE_5M = "trade_size_5m"

# --- Ghost Premium (TVD-Alpha) ---
KEY_PDR_5M = "pdr_5m"
KEY_PDR_ROC_5M = "pdr_roc_5m"

# --- Depth Decay Momentum ---
KEY_DEPTH_DECAY_BID_5M = "depth_decay_bid_5m"
KEY_DEPTH_DECAY_ASK_5M = "depth_decay_ask_5m"
KEY_DEPTH_TOP5_BID_5M = "depth_top5_bid_5m"
KEY_DEPTH_TOP5_ASK_5M = "depth_top5_ask_5m"
KEY_DEPTH_VOL_RATIO_5M = "depth_vol_ratio_5m"

# --- Depth Imbalance Momentum ---
KEY_IR_5M = "imbalance_ratio_5m"
KEY_IR_ROC_5M = "imbalance_ratio_roc_5m"
KEY_IR_PARTICIPANTS_5M = "ir_participants_5m"

# --- Exchange Flow Concentration ---
KEY_VSI_COMBINED_5M = "vsi_combined_5m"
KEY_VSI_ROC_5M = "vsi_roc_5m"
KEY_IEX_INTENT_5M = "iex_intent_5m"

# --- Participant Diversity Conviction ---
KEY_BID_PARTICIPANTS_5M = "bid_participants_5m"
KEY_ASK_PARTICIPANTS_5M = "ask_participants_5m"
KEY_BID_EXCHANGES_5M = "bid_exchanges_5m"
KEY_ASK_EXCHANGES_5M = "ask_exchanges_5m"
KEY_CONVICT_SCORE_5M = "conviction_score_5m"

# --- Participant Divergence Scalper ---
KEY_FRAGILITY_BID_5M = "fragility_bid_5m"
KEY_FRAGILITY_ASK_5M = "fragility_ask_5m"
KEY_DECAY_VELOCITY_BID_5M = "decay_velocity_bid_5m"
KEY_DECAY_VELOCITY_ASK_5M = "decay_velocity_ask_5m"
KEY_TOP_WALL_BID_SIZE_5M = "top_wall_bid_size_5m"
KEY_TOP_WALL_ASK_SIZE_5M = "top_wall_ask_size_5m"

# --- Exchange Flow Imbalance ---
KEY_AGGRESSOR_VSI_5M = "aggressor_vsi_5m"
KEY_AGGRESSOR_VSI_ROC_5M = "aggressor_vsi_roc_5m"
KEY_IEX_INTENT_SCORE_5M = "iex_intent_score_5m"
KEY_MEMX_VSI_5M = "memx_vsi_5m"
KEY_BATS_VSI_5M = "bats_vsi_5m"
KEY_VENUE_CONCENTRATION_5M = "venue_concentration_5m"

# --- Exchange Flow Asymmetry: Venue Signature Tracking ---
KEY_ESI_MEMX_5M = "esi_memx_5m"
KEY_ESI_MEMX_ROC_5M = "esi_memx_roc_5m"
KEY_ESI_BATS_5M = "esi_bats_5m"
KEY_ESI_BATS_ROC_5M = "esi_bats_roc_5m"
KEY_MEMX_VOL_RATIO_5M = "memx_vol_ratio_5m"
KEY_BATS_VOL_RATIO_5M = "bats_vol_ratio_5m"
KEY_ESI_BASELINE_MEMX_1H = "esi_baseline_memx_1h"
KEY_ESI_BASELINE_BATS_1H = "esi_baseline_bats_1h"

# --- Order Book Stacking (Structural Concentration) ---
KEY_DEPTH_BID_LEVEL_AVG_5M = "depth_bid_level_avg_5m"
KEY_DEPTH_ASK_LEVEL_AVG_5M = "depth_ask_level_avg_5m"
KEY_SIS_BID_5M = "sis_bid_5m"
KEY_SIS_ASK_5M = "sis_ask_5m"
KEY_SIS_BID_ROC_5M = "sis_bid_roc_5m"
KEY_SIS_ASK_ROC_5M = "sis_ask_roc_5m"

# --- Gamma-Weighted Momentum (GAMMA-ALPHA) ---
KEY_WALL_DISTANCE_5M = "wall_distance_5m"
KEY_WALL_GEX_5M = "wall_gex_5m"
KEY_WALL_GEX_SIGMA_5M = "wall_gex_sigma_5m"
KEY_PRICE_VELOCITY_5M = "price_velocity_5m"
KEY_GAMMA_BREAK_INDEX_5M = "gamma_break_5m"

# --- Iron Anchor (CONFLUENCE-ALPHA) ---
KEY_CONFLUENCE_PROX_5M = "confluence_prox_5m"
KEY_CONFLUENCE_SIGNAL_5M = "confluence_signal_5m"
KEY_LIQUIDITY_WALL_SIZE_5M = "liq_wall_size_5m"
KEY_LIQUIDITY_WALL_SIGMA_5M = "liq_wall_sigma_5m"

# --- Sentiment Sync (SYNCHRONY-ALPHA) ---
KEY_SYNC_CORR_5M = "sync_corr_5m"
KEY_SYNC_SIGMA_5M = "sync_sigma_5m"
KEY_SKEW_CHANGE_5M = "skew_change_5m"
KEY_VSI_MAGNITUDE_5M = "vsi_magnitude_5m"

# --- Whale Tracker (CONCENTRATION-ALPHA) ---
KEY_BIGGEST_SIZE_5M = "biggest_size_5m"
KEY_SMALLEST_SIZE_5M = "smallest_size_5m"
KEY_CONCENTRATION_RATIO_5M = "conc_ratio_5m"
KEY_CONCENTRATION_SIGMA_5M = "conc_sigma_5m"
KEY_NUM_PARTICIPANTS_5M = "num_participants_5m"

# --- Vortex Compression Breakout ---
KEY_SPREAD_ZSCORE_5M = "spread_zscore_5m"
KEY_LIQUIDITY_DENSITY_5M = "liquidity_density_5m"
KEY_PARTICIPANT_EQUILIBRIUM_5M = "participant_equilibrium_5m"
KEY_VOLUME_SPIKE_5M = "volume_spike_5m"

# --- Market Depth Aggregation ---
KEY_MARKET_DEPTH_AGG = "market_depth_agg"

# --- VAMP Levels ---
KEY_VAMP_LEVELS = "vamp_levels"

# --- Message Type Identifiers (JSON stream protocol) ---
MSG_TYPE_QUOTE_UPDATE = "quote_update"
MSG_TYPE_OPTION_UPDATE = "option_update"
MSG_TYPE_UNDERLYING_UPDATE = "underlying_update"
MSG_TYPE_MARKET_DEPTH_QUOTES = "market_depth_quotes"

# --- IV Skew Dynamics (SKEW-ALPHA) ---
KEY_SKEW_PSI_5M = "skew_psi_5m"
KEY_SKEW_PSI_ROC_5M = "skew_psi_roc_5m"
KEY_SKEW_PSI_SIGMA_5M = "skew_psi_sigma_5m"

# --- IV Smile Dynamics (CURVE-ALPHA) ---
KEY_CURVE_OMEGA_5M = "curve_omega_5m"
KEY_CURVE_OMEGA_ROC_5M = "curve_omega_roc_5m"
KEY_CURVE_OMEGA_SIGMA_5M = "curve_omega_sigma_5m"
KEY_PUT_SLOPE_5M = "put_slope_5m"
KEY_CALL_SLOPE_5M = "call_slope_5m"

# --- Extrinsic Value Flow (EXTRINSIC-ALPHA) ---
KEY_PHI_CALL_5M = "phi_call_5m"
KEY_PHI_PUT_5M = "phi_put_5m"
KEY_PHI_RATIO_5M = "phi_ratio_5m"
KEY_PHI_TOTAL_5M = "phi_total_5m"
KEY_PHI_TOTAL_SIGMA_5M = "phi_total_sigma_5m"

# --- Non-default window sizes for RollingWindow initialization ---
# Keys not listed here default to 300 seconds.
ROLLING_WINDOW_SIZES: dict[str, int] = {
    KEY_PRICE_30M: 1800,
    KEY_SYNC_CORR_5M: 900,
    KEY_SYNC_SIGMA_5M: 900,
    KEY_SKEW_CHANGE_5M: 900,
    KEY_VSI_MAGNITUDE_5M: 900,
    KEY_BIGGEST_SIZE_5M: 900,
    KEY_SMALLEST_SIZE_5M: 900,
    KEY_CONCENTRATION_RATIO_5M: 900,
    KEY_CONCENTRATION_SIGMA_5M: 900,
    KEY_NUM_PARTICIPANTS_5M: 900,
    KEY_SKEW_PSI_5M: 900,
    KEY_SKEW_PSI_ROC_5M: 900,
    KEY_SKEW_PSI_SIGMA_5M: 900,
    KEY_CURVE_OMEGA_5M: 900,
    KEY_CURVE_OMEGA_ROC_5M: 900,
    KEY_CURVE_OMEGA_SIGMA_5M: 900,
    KEY_PUT_SLOPE_5M: 900,
    KEY_CALL_SLOPE_5M: 900,
    KEY_DEPTH_BID_SIZE_ROLLING: 60,
    KEY_DEPTH_ASK_SIZE_ROLLING: 60,
}

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
    KEY_EXTRINSIC_ROC_5M,
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

# Depth Decay Momentum keys tuple
DEPTH_DECAY_KEYS = (
    KEY_DEPTH_DECAY_BID_5M,
    KEY_DEPTH_DECAY_ASK_5M,
    KEY_DEPTH_TOP5_BID_5M,
    KEY_DEPTH_TOP5_ASK_5M,
    KEY_DEPTH_VOL_RATIO_5M,
)

# VAMP Momentum keys tuple
VAMP_KEYS = (
    KEY_VAMP_5M,
    KEY_VAMP_MID_DEV_5M,
    KEY_VAMP_ROC_5M,
    KEY_VAMP_PARTICIPANTS_5M,
    KEY_VAMP_DEPTH_DENSITY_5M,
)

# OBI + Aggression Flow keys tuple
OBI_KEYS = (
    KEY_OBI_5M,
    KEY_AGGRESSIVE_BUY_VOL_5M,
    KEY_AGGRESSIVE_SELL_VOL_5M,
    KEY_AF_5M,
    KEY_TRADE_SIZE_5M,
)

# All keys in one tuple for validation
ALL_KEYS = (*CORE_KEYS, *DEPTH_KEYS, KEY_FLOW_RATIO_5M,
            KEY_EXTRINSIC_PROXY_5M, KEY_PROB_MOMENTUM_5M,
            KEY_IV_SKEW_GRADIENT_5M, KEY_GAMMA_DENSITY_5M,
            KEY_CONSEC_LONG, KEY_CONSEC_SHORT,
            KEY_SKEW_WIDTH_5M,
            KEY_STRIKE_DELTA_5M, KEY_ATR_5M,
            KEY_MAGNET_DELTA_5M,
            KEY_MOMENTUM_ROC_5M,
            KEY_VAMP_5M, KEY_VAMP_MID_DEV_5M, KEY_VAMP_ROC_5M,
            KEY_VAMP_PARTICIPANTS_5M, KEY_VAMP_DEPTH_DENSITY_5M,
            KEY_OBI_5M, KEY_AGGRESSIVE_BUY_VOL_5M, KEY_AGGRESSIVE_SELL_VOL_5M,
            KEY_AF_5M, KEY_TRADE_SIZE_5M,
            *DEPTH_DECAY_KEYS,
            KEY_IR_5M, KEY_IR_ROC_5M, KEY_IR_PARTICIPANTS_5M,
            KEY_VSI_COMBINED_5M, KEY_VSI_ROC_5M, KEY_IEX_INTENT_5M,
            KEY_BID_PARTICIPANTS_5M, KEY_ASK_PARTICIPANTS_5M,
            KEY_BID_EXCHANGES_5M, KEY_ASK_EXCHANGES_5M,
            KEY_CONVICT_SCORE_5M,
            KEY_FRAGILITY_BID_5M, KEY_FRAGILITY_ASK_5M,
            KEY_DECAY_VELOCITY_BID_5M, KEY_DECAY_VELOCITY_ASK_5M,
            KEY_TOP_WALL_BID_SIZE_5M, KEY_TOP_WALL_ASK_SIZE_5M,
            KEY_AGGRESSOR_VSI_5M, KEY_AGGRESSOR_VSI_ROC_5M,
            KEY_IEX_INTENT_SCORE_5M, KEY_MEMX_VSI_5M,
            KEY_BATS_VSI_5M, KEY_VENUE_CONCENTRATION_5M,
            KEY_ESI_MEMX_5M, KEY_ESI_MEMX_ROC_5M,
            KEY_ESI_BATS_5M, KEY_ESI_BATS_ROC_5M,
            KEY_MEMX_VOL_RATIO_5M, KEY_BATS_VOL_RATIO_5M,
            KEY_ESI_BASELINE_MEMX_1H, KEY_ESI_BASELINE_BATS_1H,
            KEY_DEPTH_BID_LEVEL_AVG_5M, KEY_DEPTH_ASK_LEVEL_AVG_5M,
            KEY_SIS_BID_5M, KEY_SIS_ASK_5M,
            KEY_SIS_BID_ROC_5M, KEY_SIS_ASK_ROC_5M,
            KEY_PDR_5M, KEY_PDR_ROC_5M,
            KEY_SKEW_PSI_5M, KEY_SKEW_PSI_ROC_5M, KEY_SKEW_PSI_SIGMA_5M,
            KEY_CURVE_OMEGA_5M, KEY_CURVE_OMEGA_ROC_5M, KEY_CURVE_OMEGA_SIGMA_5M,
            KEY_PUT_SLOPE_5M, KEY_CALL_SLOPE_5M,
            KEY_PHI_CALL_5M, KEY_PHI_PUT_5M, KEY_PHI_RATIO_5M,
            KEY_PHI_TOTAL_5M, KEY_PHI_TOTAL_SIGMA_5M,
            KEY_WALL_DISTANCE_5M, KEY_WALL_GEX_5M, KEY_WALL_GEX_SIGMA_5M,
            KEY_PRICE_VELOCITY_5M, KEY_GAMMA_BREAK_INDEX_5M,
            KEY_CONFLUENCE_PROX_5M, KEY_CONFLUENCE_SIGNAL_5M,
            KEY_LIQUIDITY_WALL_SIZE_5M, KEY_LIQUIDITY_WALL_SIGMA_5M,
            KEY_SYNC_CORR_5M, KEY_SYNC_SIGMA_5M, KEY_SKEW_CHANGE_5M,
            KEY_VSI_MAGNITUDE_5M,
            KEY_BIGGEST_SIZE_5M, KEY_SMALLEST_SIZE_5M,
            KEY_CONCENTRATION_RATIO_5M, KEY_CONCENTRATION_SIGMA_5M,
            KEY_NUM_PARTICIPANTS_5M,
            KEY_SPREAD_ZSCORE_5M, KEY_LIQUIDITY_DENSITY_5M,
            KEY_PARTICIPANT_EQUILIBRIUM_5M, KEY_VOLUME_SPIKE_5M,
            KEY_DELTA_DENSITY_5M, KEY_VOLUME_ZSCORE_5M, KEY_ORDER_BOOK_DEPTH_5M,)

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
    "KEY_EXTRINSIC_PROXY_5M", "KEY_EXTRINSIC_ROC_5M", "KEY_PROB_MOMENTUM_5M",
    "KEY_CONSEC_LONG", "KEY_CONSEC_SHORT",
    "KEY_SKEW_WIDTH_5M",
    "KEY_STRIKE_DELTA_5M", "KEY_ATR_5M",
    "KEY_SKEW_ROC_5M", "KEY_DELTA_ROC_5M",
    "KEY_MAGNET_DELTA_5M",
    "KEY_MOMENTUM_ROC_5M",
    "KEY_VAMP_5M", "KEY_VAMP_MID_DEV_5M", "KEY_VAMP_ROC_5M",
    "KEY_VAMP_PARTICIPANTS_5M", "KEY_VAMP_DEPTH_DENSITY_5M",
    "KEY_OBI_5M", "KEY_AGGRESSIVE_BUY_VOL_5M", "KEY_AGGRESSIVE_SELL_VOL_5M",
    "KEY_AF_5M", "KEY_TRADE_SIZE_5M",
    "KEY_DEPTH_DECAY_BID_5M", "KEY_DEPTH_DECAY_ASK_5M",
    "KEY_DEPTH_TOP5_BID_5M", "KEY_DEPTH_TOP5_ASK_5M",
    "KEY_DEPTH_VOL_RATIO_5M",
    "KEY_IR_5M", "KEY_IR_ROC_5M", "KEY_IR_PARTICIPANTS_5M",
    "KEY_VSI_COMBINED_5M", "KEY_VSI_ROC_5M", "KEY_IEX_INTENT_5M",
    "KEY_BID_PARTICIPANTS_5M", "KEY_ASK_PARTICIPANTS_5M",
    "KEY_BID_EXCHANGES_5M", "KEY_ASK_EXCHANGES_5M",
    "KEY_CONVICT_SCORE_5M",
    "KEY_FRAGILITY_BID_5M", "KEY_FRAGILITY_ASK_5M",
    "KEY_DECAY_VELOCITY_BID_5M", "KEY_DECAY_VELOCITY_ASK_5M",
    "KEY_TOP_WALL_BID_SIZE_5M", "KEY_TOP_WALL_ASK_SIZE_5M",
    "KEY_AGGRESSOR_VSI_5M", "KEY_AGGRESSOR_VSI_ROC_5M",
    "KEY_IEX_INTENT_SCORE_5M", "KEY_MEMX_VSI_5M",
    "KEY_BATS_VSI_5M", "KEY_VENUE_CONCENTRATION_5M",
    "KEY_ESI_MEMX_5M", "KEY_ESI_MEMX_ROC_5M",
    "KEY_ESI_BATS_5M", "KEY_ESI_BATS_ROC_5M",
    "KEY_MEMX_VOL_RATIO_5M", "KEY_BATS_VOL_RATIO_5M",
    "KEY_ESI_BASELINE_MEMX_1H", "KEY_ESI_BASELINE_BATS_1H",
    "KEY_DEPTH_BID_LEVEL_AVG_5M", "KEY_DEPTH_ASK_LEVEL_AVG_5M",
    "KEY_SIS_BID_5M", "KEY_SIS_ASK_5M",
    "KEY_SIS_BID_ROC_5M", "KEY_SIS_ASK_ROC_5M",
    "KEY_PDR_5M", "KEY_PDR_ROC_5M",
    "KEY_SKEW_PSI_5M", "KEY_SKEW_PSI_ROC_5M", "KEY_SKEW_PSI_SIGMA_5M",
    "KEY_CURVE_OMEGA_5M", "KEY_CURVE_OMEGA_ROC_5M", "KEY_CURVE_OMEGA_SIGMA_5M",
    "KEY_PUT_SLOPE_5M", "KEY_CALL_SLOPE_5M",
    "KEY_PHI_CALL_5M", "KEY_PHI_PUT_5M", "KEY_PHI_RATIO_5M",
    "KEY_PHI_TOTAL_5M", "KEY_PHI_TOTAL_SIGMA_5M",
    "KEY_WALL_DISTANCE_5M", "KEY_WALL_GEX_5M", "KEY_WALL_GEX_SIGMA_5M",
    "KEY_PRICE_VELOCITY_5M", "KEY_GAMMA_BREAK_INDEX_5M",
    "KEY_CONFLUENCE_PROX_5M", "KEY_CONFLUENCE_SIGNAL_5M",
    "KEY_LIQUIDITY_WALL_SIZE_5M", "KEY_LIQUIDITY_WALL_SIGMA_5M",
    "KEY_SYNC_CORR_5M", "KEY_SYNC_SIGMA_5M", "KEY_SKEW_CHANGE_5M",
    "KEY_VSI_MAGNITUDE_5M",
    "KEY_BIGGEST_SIZE_5M", "KEY_SMALLEST_SIZE_5M",
    "KEY_CONCENTRATION_RATIO_5M", "KEY_CONCENTRATION_SIGMA_5M",
    "KEY_NUM_PARTICIPANTS_5M",
    "KEY_SPREAD_ZSCORE_5M", "KEY_LIQUIDITY_DENSITY_5M",
    "KEY_PARTICIPANT_EQUILIBRIUM_5M", "KEY_VOLUME_SPIKE_5M",
    "KEY_DELTA_DENSITY_5M", "KEY_VOLUME_ZSCORE_5M", "KEY_ORDER_BOOK_DEPTH_5M",
    "KEY_MARKET_DEPTH_AGG", "KEY_VAMP_LEVELS",
    "MSG_TYPE_QUOTE_UPDATE",
    "MSG_TYPE_OPTION_UPDATE",
    "MSG_TYPE_UNDERLYING_UPDATE",
    "MSG_TYPE_MARKET_DEPTH_QUOTES",
    "CORE_KEYS", "DEPTH_KEYS", "DEPTH_DECAY_KEYS", "ALL_KEYS", "OBI_KEYS",
]
