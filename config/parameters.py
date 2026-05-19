"""
config/parameters.py — Centralized Strategy Parameters

This file contains all magic numbers extracted from strategy files.
Each parameter is documented with its purpose and which strategies use it.

Edit here to tune all strategies consistently.
"""

# ============================================================================
# GLOBAL CONFIDENCE PARAMETERS
# ============================================================================

# Confidence normalization range (used by normalize_confidence helper)
CONFIDENCE_MIN = 0.25
CONFIDENCE_MAX = 0.75

# Default minimum confidence for signals (can be overridden per strategy)
DEFAULT_MIN_CONFIDENCE = 0.35

# Max signals per tick to prevent flooding
MAX_SIGNALS_PER_TICK = 10

# Deduplication window in seconds
DEDUP_WINDOW_SECONDS = 60

# ============================================================================
# LAYER 1: STRUCTURAL (GEX + OHLC) PARAMETERS
# ============================================================================

# --- Gamma Wall Bounce ---
GAMMA_WALL_BOUNCE_PROXIMITY_PCT = 0.005       # 0.5% — how close price must be to wall
GAMMA_WALL_BOUNCE_STOP_PAST_WALL_PCT = 0.004  # 0.4% — stop beyond the wall
GAMMA_WALL_BOUNCE_MIN_CONFIDENCE = 0.25
GAMMA_WALL_BOUNCE_MAX_CONFIDENCE = 0.85

# --- Gamma Squeeze ---
GAMMA_SQUEEZE_PIN_ATR_PCT = 0.003             # 0.3% — max range for pin detection
GAMMA_SQUEEZE_WALL_PROXIMITY_PCT = 0.003      # 0.3% — price must be near wall for breakout
GAMMA_SQUEEZE_VOLUME_SURGE_MULT = 1.5         # 1.5× average volume = confirmation
GAMMA_SQUEEZE_MIN_WALL_GEX = 500000           # Minimum |GEX| for wall consideration
GAMMA_SQUEEZE_MIN_CONFIDENCE = 0.50           # Higher than default due to breakout nature
GAMMA_SQUEEZE_TARGET_RISK_MULT = 2.0          # 2× risk for squeeze targets
GAMMA_SQUEEZE_MIN_MASSIVE_WALL_GEX = 5000000  # Fallback threshold for POSITIVE regime filter

# --- Gamma Flip Breakout ---
GAMMA_FLIP_BREAKOUT_PROXIMITY_PCT = 0.025     # 2.5% — price must be within this of flip
GAMMA_FLIP_BREAKOUT_STOP_OTHER_SIDE_PCT = 0.01  # 1% — stop on other side of flip
GAMMA_FLIP_BREAKOUT_MIN_CONFIDENCE = 0.65

# --- Magnet Accelerate ---
MAGNET_PROXIMITY_PCT = 0.01                   # 1% — proximity to magnet
MAGNET_EXIT_PCT = 0.003                       # 0.3% — exit within this % of magnet
MAGNET_BREAKOUT_PCT = 0.002                   # 0.2% — price must be this far past magnet
MAGNET_EMA_FAST = 9
MAGNET_EMA_SLOW = 21

# --- GEX Imbalance ---
GEX_IMBALANCE_CALL_HEAVY_RATIO = 0.65         # > 0.65 → short bias
GEX_IMBALANCE_STRONG_PUT_RATIO = 0.25         # very strong long signal
GEX_IMBALANCE_STRONG_CALL_RATIO = 0.75        # very strong short signal
GEX_IMBALANCE_MIN_CONFIDENCE = 0.55

# --- Confluence Reversal ---
CONFLUENCE_DISTANCE_PCT = 0.003               # 0.3% — max distance for confluence
CONFLUENCE_MIN_CONFLUENCE_SCORE = 2
CONFLUENCE_MIN_CONFIDENCE = 0.65
CONFLUENCE_STOP_PCT = 0.008                   # 0.8% stop

# --- GEX Divergence ---
GEX_DIVERGENCE_MIN_SLOPE = 0.0005             # Minimum slope magnitude (0.05%)
GEX_DIVERGENCE_CONFIRMATION_CANDLE_PCT = 0.002  # 0.2% candle for confirmation
GEX_DIVERGENCE_MIN_CONFIDENCE = 0.25
GEX_DIVERGENCE_STOP_PCT = 0.005               # 0.5% stop

# --- Vol Compression Range ---
VOL_COMPRESSION_THRESHOLD_PCT = 0.5           # 0.5% compression threshold
VOL_COMPRESSION_WALL_PROXIMITY_PCT = 0.005    # 0.5% wall proximity

# ============================================================================
# LAYER 2: ALPHA GREEKS PARAMETERS
# ============================================================================

# --- Delta-Gamma Squeeze ---
DELTA_GAMMA_SQUEEZE_WALL_PROXIMITY_PCT = 0.03  # 3% — wider wall proximity
DELTA_GAMMA_SQUEEZE_DELTA_ACCEL_RATIO = 1.10   # 10% above rolling avg
DELTA_GAMMA_SQUEEZE_VOLUME_SPIKE_RATIO = 1.20  # 20% above rolling avg
DELTA_GAMMA_SQUEEZE_MIN_WALL_GEX = 500000
DELTA_GAMMA_SQUEEZE_PRICE_ABOVE_MEAN_CONFIDENCE = 0.55
DELTA_GAMMA_SQUEEZE_MIN_DATA_POINTS = 3
DELTA_GAMMA_SQUEEZE_MIN_CONFIDENCE = 0.25
DELTA_GAMMA_SQUEEZE_STOP_BELOW_WALL_PCT = 0.008  # 0.8% below/above entry
DELTA_GAMMA_SQUEEZE_TARGET_RISK_MULT = 2.0

# --- Delta Volume Exhaustion ---
DELTA_VOLUME_DELTA_DECLINE_RATIO = 0.90        # Delta declining to 90% of previous
DELTA_VOLUME_VOLUME_DECLINE_RATIO = 0.85       # Volume declining to 85% of previous
DELTA_VOLUME_TREND_DURATION = 3
DELTA_VOLUME_MIN_CONFIDENCE = 0.25

# --- Call Put Flow Asymmetry ---
CALL_PUT_FLOW_THRESHOLD = 1.5                  # Flow ratio threshold
CALL_PUT_FLOW_IV_SKEW_THRESHOLD = 0.03         # 3% IV skew
CALL_PUT_FLOW_STOP_PCT = 0.006                 # 0.6% stop
CALL_PUT_FLOW_TARGET_RISK_MULT = 2.0
CALL_PUT_FLOW_MIN_CONFIDENCE = 0.25

# --- IV-GEX Divergence ---
IV_GEX_IV_DECLINE_PCT = 0.05                   # 5% IV decline
IV_GEX_MIN_CONFIDENCE = 0.25

# ============================================================================
# LAYER 3: MICRO-SIGNAL (1HZ) PARAMETERS
# ============================================================================

# --- Theta Burn ---
THETA_BURN_MIN_NET_GAMMA = 500000.0            # Must be strongly positive
THETA_BURN_WALL_PROXIMITY_PCT = 0.005          # 0.5% wall proximity
THETA_BURN_STOP_PAST_WALL_PCT = 0.003          # 0.3% beyond the wall
THETA_BURN_MIN_TARGET_PCT = 0.002              # 0.2% min target
THETA_BURN_MAX_TARGET_PCT = 0.004              # 0.4% max target
THETA_BURN_RANGE_NARROWNESS_RATIO = 0.40       # 5m range < 40% of 30m range
THETA_BURN_DIVERGENCE_VOLUME_THRESHOLD = 0.80  # Volume < 80% of avg = declining
THETA_BURN_MIN_CONFIDENCE = 0.25
THETA_BURN_MAX_CONFIDENCE = 0.80               # Micro-signal cap
THETA_BURN_MIN_DATA_POINTS = 3
THETA_BURN_GAMMA_STRENGTH_HIGH = 500000.0      # Above this = max gamma bonus

# Midday lull window in UTC (11:30-14:30 ET = 16:30-19:30 UTC)
THETA_BURN_MIDDAY_UTC_START = 16.5             # 16:30 UTC (4:30 PM PT)
THETA_BURN_MIDDAY_UTC_END = 19.5               # 19:30 UTC (7:30 PM PT)

# --- Gamma Volume Convergence ---
GAMMA_VOL_DELTA_ACCEL_RATIO = 1.15
GAMMA_VOL_GAMMA_SPIKE_RATIO = 1.20
GAMMA_VOL_VOLUME_SPIKE_RATIO = 1.20
GAMMA_VOL_STOP_PCT = 0.005                     # 0.5% stop
GAMMA_VOL_TARGET_PCT = 0.010                   # 1.0% target
GAMMA_VOL_MIN_DATA_POINTS = 3
GAMMA_VOL_MIN_CONFIDENCE = 0.35
GAMMA_VOL_MAX_CONFIDENCE = 0.90

# --- IV Band Breakout ---
IV_BAND_PRICE_COMPRESSION_RATIO = 0.30         # 30% compression
IV_BAND_VOLUME_SPIKE_RATIO = 1.20
IV_BAND_STOP_PCT = 0.005                       # 0.5% stop
IV_BAND_TARGET_PCT = 0.010                     # 1.0% target
IV_BAND_MIN_DATA_POINTS = 3
IV_BAND_MIN_CONFIDENCE = 0.35
IV_BAND_MAX_CONFIDENCE = 0.85

# --- Strike Concentration ---
STRIKE_CONCENTRATION_TOP_OI_STRIKES_COUNT = 3
STRIKE_CONCENTRATION_BOUNCE_PROXIMITY_PCT = 0.003  # 0.3%
STRIKE_CONCENTRATION_SLICE_BODY_RATIO = 0.5
STRIKE_CONCENTRATION_SLICE_VOLUME_RATIO = 1.20
STRIKE_CONCENTRATION_STOP_PCT = 0.003          # 0.3% stop
STRIKE_CONCENTRATION_MIN_DATA_POINTS = 3
STRIKE_CONCENTRATION_MIN_CONFIDENCE = 0.35
STRIKE_CONCENTRATION_MAX_CONFIDENCE = 0.85

# ============================================================================
# LAYER 4: FULL-DATA (V2) PARAMETERS
# ============================================================================

# --- IV Skew Squeeze ---
IV_SKEW_SKEW_EXTREME_POSITIVE = 0.30           # 30% positive skew
IV_SKEW_SKEW_EXTREME_NEGATIVE = -0.10          # -10% negative skew
IV_SKEW_PRICE_STABLE_THRESHOLD = 0.005         # 0.5% price stability
IV_SKEW_MIN_NET_GAMMA = 5000.0
IV_SKEW_STOP_PCT = 0.005                       # 0.5% stop
IV_SKEW_TARGET_PCT = 0.008                     # 0.8% target
IV_SKEW_MIN_DATA_POINTS = 5
IV_SKEW_MIN_SKEW_DATA_POINTS = 10
IV_SKEW_MIN_CONFIDENCE = 0.35
IV_SKEW_MAX_CONFIDENCE = 0.80

# --- Prob Weighted Magnet ---
PROB_MAGNET_MIN_OI_CONCENTRATION = 5.0         # 5% OI concentration
PROB_MAGNET_CONSOLIDATION_RATIO = 0.40         # 40% consolidation
PROB_MAGNET_DELTA_ACCEL_RATIO = 1.10           # 10% delta acceleration
PROB_MAGNET_MIN_NET_GAMMA = 5000.0
PROB_MAGNET_STOP_PCT = 0.005                   # 0.5% stop
PROB_MAGNET_TARGET_RISK_MULT = 1.5
PROB_MAGNET_MIN_DATA_POINTS = 3
PROB_MAGNET_MIN_CONFIDENCE = 0.35
PROB_MAGNET_MAX_CONFIDENCE = 0.80

# --- Prob Distribution Shift ---
PROB_DIST_Z_SCORE_THRESHOLD = 2.0              # 2 standard deviations
PROB_DIST_MIN_CONSECUTIVE_SIGNALS = 3
PROB_DIST_MIN_NET_GAMMA = 5000.0
PROB_DIST_STOP_PCT = 0.005                     # 0.5% stop
PROB_DIST_TARGET_PCT = 0.008                   # 0.8% target
PROB_DIST_MIN_STRIKES_WITH_DATA = 5
PROB_DIST_MIN_DATA_POINTS = 10
PROB_DIST_MIN_CONFIDENCE = 0.35
PROB_DIST_MAX_CONFIDENCE = 0.80

# --- Extrinsic Intrinsic Flow ---
FLOW_EXTRINSIC_EXPANSION_THRESHOLD = 0.05      # 5% expansion
FLOW_EXTRINSIC_COLLAPSE_THRESHOLD = 0.10       # 10% collapse
FLOW_VOLUME_SPIKE_RATIO = 1.50                 # 1.5× volume
FLOW_MIN_NET_GAMMA = 5000.0
FLOW_STOP_PCT = 0.005                          # 0.5% stop
FLOW_TARGET_PCT = 0.008                        # 0.8% target
FLOW_MIN_DATA_POINTS = 10
FLOW_MIN_CONFIDENCE = 0.35
FLOW_MAX_CONFIDENCE = 0.80

# ============================================================================
# LAYER 0: MASTER FILTER PARAMETERS
# ============================================================================

# Net Gamma Filter
FILTER_NET_GAMMA_FLIP_BUFFER = 0.5             # 50% buffer for flip detection

# ============================================================================
# TRACKER PARAMETERS (Max Hold Times in Seconds)
# ============================================================================

TRACKER_LAYER1_DEFAULT = 1800                  # 30 minutes
TRACKER_LAYER2_DEFAULT = 1800                  # 30 minutes
TRACKER_LAYER3_DEFAULT = 900                   # 15 minutes
TRACKER_LAYER4_DEFAULT = 7200                  # 2 hours

# Strategy-specific overrides
TRACKER_GAMMA_WALL_BOUNCE = 1800
TRACKER_MAGNET_ACCELERATE = 3600
TRACKER_GAMMA_FLIP_BREAKOUT = 3600
TRACKER_GAMMA_SQUEEZE = 1800
TRACKER_GEX_IMBALANCE = 2700
TRACKER_CONFLUENCE_REVERSAL = 3600
TRACKER_VOL_COMPRESSION = 7200
TRACKER_GEX_DIVERGENCE = 3600
TRACKER_DELTA_GAMMA_SQUEEZE = 1800
TRACKER_DELTA_VOLUME_EXHAUSTION = 2700
TRACKER_CALL_PUT_FLOW = 3600
TRACKER_IV_GEX_DIVERGENCE = 2700
TRACKER_DELTA_IV_DIVERGENCE = 2700
TRACKER_GAMMA_VOL_CONVERGENCE = 900
TRACKER_IV_BAND_BREAKOUT = 2700
TRACKER_STRIKE_CONCENTRATION = 900
TRACKER_THETA_BURN = 480                       # 8 minutes (quick scalps)
TRACKER_IV_SKEW_SQUEEZE = 14400                # 4 hours
TRACKER_PROB_MAGNET = 2700
TRACKER_PROB_DIST = 7200
TRACKER_FLOW = 10800                           # 3 hours

# ============================================================================
# UTILITY / HELPER PARAMETERS
# ============================================================================

# ATR Periods (for various calculations)
ATR_PERIOD_SHORT = 14
ATR_PERIOD_MEDIUM = 21
ATR_PERIOD_LONG = 50

# Lookback Windows (in bars/ticks)
LOOKBACK_SHORT = 5
LOOKBACK_MEDIUM = 20
LOOKBACK_LONG = 60

# Percentile thresholds for statistical calculations
PERCENTILE_25 = 0.25
PERCENTILE_50 = 0.50
PERCENTILE_75 = 0.75
PERCENTILE_95 = 0.95

# Risk multipliers
RISK_MULT_CONSERVATIVE = 1.0
RISK_MULT_MODERATE = 1.5
RISK_MULT_AGGRESSIVE = 2.0

# ============================================================================
# REGIME THRESHOLDS
# ============================================================================

# Net gamma thresholds for regime classification
REGIME_POSITIVE_THRESHOLD = 0
REGIME_NEGATIVE_THRESHOLD = 0

# ============================================================================
# VOLUME FILTER PARAMETERS
# ============================================================================

VOLUME_FILTER_MIN_CONFIDENCE = 0.35
VOLUME_SPIKE_RATIO_HIGH = 1.5
VOLUME_SPIKE_RATIO_MODERATE = 1.2
VOLUME_DECLINE_RATIO_LOW = 0.8
VOLUME_DECLINE_RATIO_MODERATE = 0.85
