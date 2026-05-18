# Syngex Strategy Parameter Diff Report
**V1 (Original)** vs **V2.41 (Current)** Parameter Comparison
Generated: /home/hologaun/projects/syngex

## Overview
- **Total Strategies Analyzed:** 48
- **Strategies with Parameter Changes:** 35
- **Total V1 Parameters:** 326
- **Total V2.41 Parameters:** 231
- **Parameters Added:** +231
- **Parameters Removed:** -326
- **Parameters Changed:** 0

---

## Layer 1 (L1) - Foundation Strategies

### confluence_reversal
**Strategy File:** `confluence_reversal.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| CONFLUENCE_DISTANCE_PCT | _new_ | 0.005 | N/A | added |
| DEPTH_SPIKE_THRESHOLD | _new_ | 1.3 | N/A | added |
| IV_WEIGHT_BASE | _new_ | 1.0 | N/A | added |
| IV_WEIGHT_MAX | _new_ | 1.5 | N/A | added |
| IV_WEIGHT_SKEW_THRESHOLD | _new_ | 0.05 | N/A | added |
| MIN_STRUCTURAL_SIGNALS | _new_ | 1 | N/A | added |
| NEGATIVE_GAMMA_STOP_MULT | _new_ | 1.5 | N/A | added |
| POSITIVE_GAMMA_STOP_MULT | _new_ | 0.75 | N/A | added |
| STOP_PCT | _new_ | 0.008 | N/A | added |
| TARGET_RISK_MULT | _new_ | 2.0 | N/A | added |
| VELOCITY_MIN_VOLUME_MULT | _new_ | 1.05 | N/A | added |
| VELOCITY_MIN_ZSCORE | _new_ | 0.5 | N/A | added |

**Summary:** 0 V1 params → 12 V2 params | +12 added | 0 removed | 0 changed

### gamma_flip_breakout
**Strategy File:** `gamma_flip_breakout.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| ATR_MULT | _new_ | 1.5 | N/A | added |
| FLIP_PROXIMITY_PCT | _new_ | 0.025 | N/A | added |
| FLIP_ZONE_PCT | _new_ | 0.015 | N/A | added |
| MIN_GAMMA_STRENGTH | _new_ | 100000 | N/A | added |
| NEGATIVE_GAMMA_STOP_MULT | _new_ | 2.5 | N/A | added |
| POSITIVE_GAMMA_STOP_MULT | _new_ | 0.75 | N/A | added |
| STOP_OTHER_SIDE_PCT | _new_ | 0.01 | N/A | added |
| TARGET_RR | _new_ | 2.5 | N/A | added |

**Summary:** 0 V1 params → 8 V2 params | +8 added | 0 removed | 0 changed

### gamma_squeeze
**Strategy File:** `gamma_squeeze.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| MIN_WALL_GEX | _new_ | 500000 | N/A | added |
| PIN_MAX_RANGE_PCT | _new_ | 0.003 | N/A | added |
| TARGET_RISK_MULT | _new_ | 2.0 | N/A | added |
| VOLUME_SURGE_MULT | _new_ | 1.5 | N/A | added |
| WALL_PROXIMITY_PCT | _new_ | 0.003 | N/A | added |

**Summary:** 0 V1 params → 5 V2 params | +5 added | 0 removed | 0 changed

### gamma_wall_bounce
**Strategy File:** `gamma_wall_bounce.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| MIN_WALL_GEX | _new_ | 500000 | N/A | added |
| STOP_PAST_WALL_PCT | _new_ | 0.004 | N/A | added |
| TARGET_RISK_MULT | _new_ | 1.5 | N/A | added |
| WALL_PROXIMITY_PCT | _new_ | 0.005 | N/A | added |

**Summary:** 0 V1 params → 4 V2 params | +4 added | 0 removed | 0 changed

### gex_divergence
**Strategy File:** `gex_divergence.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| ACCEL_MIN_GAMMA | _new_ | 0.0003 | N/A | added |
| ACCEL_MIN_PRICE | _new_ | 0.0002 | N/A | added |
| ACCEL_WINDOW_LONG | _new_ | 30 | N/A | added |
| ACCEL_WINDOW_SHORT | _new_ | 10 | N/A | added |
| CONFIRMATION_CANDLE_PCT | _new_ | 0.002 | N/A | added |
| DIVERGENCE_MIN_SLOPE | _new_ | 0.0005 | N/A | added |
| DIVERGENCE_WINDOW | _new_ | 30 | N/A | added |
| LIQUIDITY_DECAY_THRESHOLD | _new_ | 0.3 | N/A | added |
| MIN_DATA_POINTS | _new_ | 15 | N/A | added |
| MIN_TOTAL_GEX | _new_ | 1000000.0 | N/A | added |
| REGIME_INTENSITY_THRESHOLD | _new_ | 500000 | N/A | added |
| STOP_PCT | _new_ | 0.005 | N/A | added |
| STRONG_REGIME_CONF_BONUS | _new_ | 0.1 | N/A | added |
| TARGET_RISK_MULT | _new_ | 1.5 | N/A | added |
| WALL_PROXIMITY_BONUS | _new_ | 0.15 | N/A | added |
| WALL_PROXIMITY_PCT | _new_ | 0.005 | N/A | added |

**Summary:** 0 V1 params → 16 V2 params | +16 added | 0 removed | 0 changed

### gex_imbalance
**Strategy File:** `gex_imbalance.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| CALL_HEAVY_RATIO | _new_ | 0.65 | N/A | added |
| MIN_MESSAGES | _new_ | 20 | N/A | added |
| PUT_HEAVY_RATIO | _new_ | 0.5 | N/A | added |
| RATIO_ROC_THRESHOLD | _new_ | 0.1 | N/A | added |
| RATIO_ROC_WINDOW | _new_ | 5 | N/A | added |
| REGIME_GAMMA_THRESHOLD | _new_ | 500000 | N/A | added |
| STOP_VOL_MULT | _new_ | 2.5 | N/A | added |
| STRONG_CALL_RATIO | _new_ | 0.75 | N/A | added |
| STRONG_PUT_RATIO | _new_ | 0.25 | N/A | added |
| TARGET_RISK_MULT | _new_ | 1.5 | N/A | added |
| VWAP_DEVIATION_MIN_STD | _new_ | 1.5 | N/A | added |

**Summary:** 0 V1 params → 11 V2 params | +11 added | 0 removed | 0 changed

### magnet_accelerate
**Strategy File:** `magnet_accelerate.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| BREAKOUT_PCT | _new_ | 0.002 | N/A | added |
| MAGNET_EXIT_PCT | _new_ | 0.003 | N/A | added |
| MAX_BREAKOUT_PCT | _new_ | 0.02 | N/A | added |
| MIN_MAGNET_GEX | _new_ | 500000 | N/A | added |
| TARGET_RISK_MULT | _new_ | 1.5 | N/A | added |
| TRAIL_STOP_PCT | _new_ | 0.01 | N/A | added |

**Summary:** 0 V1 params → 6 V2 params | +6 added | 0 removed | 0 changed

### vol_compression_range
**Strategy File:** `vol_compression_range.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| COMPRESSION_PCT | _new_ | 0.003 | N/A | added |
| DEPTH_SPIKE_THRESHOLD | _new_ | 1.3 | N/A | added |
| IV_COMPRESSION_STD_THRESHOLD | _new_ | 0.03 | N/A | added |
| MIN_RANGE_BARS | _new_ | 20 | N/A | added |
| NEGATIVE_REGIME_STOP_MULT | _new_ | 1.5 | N/A | added |
| POSITIVE_REGIME_TIGHT_STOP_MULT | _new_ | 0.7 | N/A | added |
| REGIME_GAMMA_INTENSITY_THRESHOLD | _new_ | 500000 | N/A | added |
| STD_THRESHOLD | _new_ | 0.002 | N/A | added |
| STOP_PCT | _new_ | 0.006 | N/A | added |
| TARGET_RISK_MULT | _new_ | 1.5 | N/A | added |
| WALL_EDGE_PROXIMITY | _new_ | 0.004 | N/A | added |

**Summary:** 0 V1 params → 11 V2 params | +11 added | 0 removed | 0 changed

## Layer 2 (L2) - Flow & Momentum Strategies

### call_put_flow_asymmetry
**Plan File:** `call_put_flow_asymmetry_v2.md`
**Strategy File:** `call_put_flow_asymmetry.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| flow_breadth_threshold | 0.3 | _removed_ | N/A | removed |
| flow_ratio_roc_threshold | 0.2 | _removed_ | N/A | removed |
| flow_ratio_roc_window | 5 | _removed_ | N/A | removed |
| FLOW_THRESHOLD | **1.5** | **1.2** | -20.0% | less restrictive |
| gamma_intensity_high_mult | 1.3 | _removed_ | N/A | removed |
| gamma_intensity_high_threshold | 500000 | _removed_ | N/A | removed |
| gamma_intensity_low_mult | 0.8 | _removed_ | N/A | removed |
| gamma_intensity_low_threshold | 200000 | _removed_ | N/A | removed |
| IV_SKEW_THRESHOLD | **0.03** | **0.02** | -33.3% | less restrictive |
| max_hold_seconds | 3600 | _removed_ | N/A | removed |
| MIN_GREEKS_POINTS | _new_ | 3 | N/A | added |
| STOP_PCT | **0.006** | **0.006** | +0.0% | similar |
| TARGET_RISK_MULT | **2.0** | **2.0** | +0.0% | similar |
| wall_proximity_bonus | 0.1 | _removed_ | N/A | removed |
| wall_proximity_pct | 0.005 | _removed_ | N/A | removed |

**Summary:** 14 V1 params → 5 V2 params | +1 added | -10 removed | 2 changed

### delta_gamma_squeeze
**Strategy File:** `delta_gamma_squeeze.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| ACCEL_STOP_WIDEN_MULT | _new_ | 1.5 | N/A | added |
| DELTA_ACCEL_MIN | _new_ | 1.05 | N/A | added |
| DELTA_ACCEL_RATIO | _new_ | 1.05 | N/A | added |
| GEX_ACCEL_MIN | _new_ | 1.03 | N/A | added |
| GEX_ACCEL_RATIO | _new_ | 1.1 | N/A | added |
| IV_CONF_BONUS | _new_ | 0.08 | N/A | added |
| IV_ROC_THRESHOLD | _new_ | 0.02 | N/A | added |
| LIQUIDITY_VACUUM_DEPTH_RATIO | _new_ | 0.9 | N/A | added |
| MIN_DATA_POINTS | _new_ | 2 | N/A | added |
| MIN_WALL_GEX | _new_ | 500000 | N/A | added |
| PRICE_ABOVE_MEAN_CONFIDENCE | _new_ | 0.55 | N/A | added |
| STOP_BELOW_WALL_PCT | _new_ | 0.008 | N/A | added |
| TARGET_RISK_MULT | _new_ | 2.0 | N/A | added |
| VOLUME_SPIKE_RATIO | _new_ | 1.1 | N/A | added |
| WALL_PROXIMITY_PCT | _new_ | 0.05 | N/A | added |

**Summary:** 0 V1 params → 15 V2 params | +15 added | 0 removed | 0 changed

### delta_iv_divergence
**Plan File:** `delta_iv_divergence_v2.md`
**Strategy File:** `delta_iv_divergence.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| DECOUPLE_HISTORY_WINDOW | _new_ | 30 | N/A | added |
| DECOUPLE_THRESHOLD | _new_ | 0.8 | N/A | added |
| decoupling_corr_window | 10 | _removed_ | N/A | removed |
| decoupling_history_window | 30 | _removed_ | N/A | removed |
| decoupling_threshold | 0.5 | _removed_ | N/A | removed |
| GAMMA_DECLINE_THRESHOLD | _new_ | 0.85 | N/A | added |
| gamma_density_decline_threshold | 0.7 | _removed_ | N/A | removed |
| gamma_density_window_pct | 0.01 | _removed_ | N/A | removed |
| max_hold_seconds | 2700 | _removed_ | N/A | removed |
| MIN_DATA_POINTS | _new_ | 3 | N/A | added |
| MIN_DIVERSION_STRENGTH | _new_ | 0.2 | N/A | added |
| SK_DIV_THRESHOLD | _new_ | 0.03 | N/A | added |
| skew_divergence_threshold | 0.1 | _removed_ | N/A | removed |
| skew_otm_pct | 0.05 | _removed_ | N/A | removed |
| STOP_PCT | **0.008** | **0.008** | +0.0% | similar |
| TARGET_IV_CAP | _new_ | 4.0 | N/A | added |
| target_iv_expansion_cap | 4.0 | _removed_ | N/A | removed |
| target_iv_expansion_mult | 2.0 | _removed_ | N/A | removed |
| TARGET_IV_MULT | _new_ | 2.0 | N/A | added |
| target_risk_mult | 2.0 | _removed_ | N/A | removed |
| WALL_PROX_BONUS | _new_ | 0.1 | N/A | added |
| WALL_PROX_PCT | _new_ | 0.01 | N/A | added |
| wall_proximity_bonus | 0.1 | _removed_ | N/A | removed |
| wall_proximity_pct | 0.01 | _removed_ | N/A | removed |

**Summary:** 14 V1 params → 11 V2 params | +10 added | -13 removed | 0 changed

### delta_volume_exhaustion
**Plan File:** `delta_volume_exhaustion_v2.md`
**Strategy File:** `delta_volume_exhaustion.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| DELTA_DECLINE_RATIO | **0.9** | **0.95** | +5.6% | more restrictive |
| GAMMA_INTENSITY_THRESHOLD | **500000** | **500000** | +0.0% | similar |
| IV_ACCEL_BONUS | **0.15** | **0.15** | +0.0% | similar |
| iv_accel_penalty | -0.05 | _removed_ | N/A | removed |
| IV_ACCEL_WINDOW | **5** | **5** | +0.0% | similar |
| LIQUIDITY_VACUUM_RATIO_STABILITY | **0.15** | **0.15** | +0.0% | similar |
| LIQUIDITY_VACUUM_SPREAD_WIDEN_MULT | **1.2** | **1.1** | -8.3% | less restrictive |
| max_hold_seconds | 2700 | _removed_ | N/A | removed |
| MEAN_REVERSION_MULT | _new_ | 1.0 | N/A | added |
| MIN_GREEKS_POINTS | _new_ | 5 | N/A | added |
| MIN_TREND_DURATION | _new_ | 2 | N/A | added |
| MIN_TREND_POINTS | _new_ | 5 | N/A | added |
| NEGATIVE_GAMMA_TARGET_MULT | **1.5** | **1.5** | +0.0% | similar |
| NEUTRAL_GAMMA_TARGET_MULT | **1.0** | **1.0** | +0.0% | similar |
| POSITIVE_GAMMA_TARGET_MULT | **0.8** | **0.8** | +0.0% | similar |
| STOP_PCT | _new_ | 0.008 | N/A | added |
| WALL_PROXIMITY_BONUS | **0.1** | **0.1** | +0.0% | similar |
| WALL_PROXIMITY_PCT | **0.003** | **0.003** | +0.0% | similar |

**Summary:** 13 V1 params → 16 V2 params | +5 added | -2 removed | 2 changed

### depth_decay_momentum
**Plan File:** `depth_decay_momentum.md`
**Strategy File:** `depth_decay_momentum.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 6 | _removed_ | N/A | removed |
| depth_decay_lookback | 5 | _removed_ | N/A | removed |
| depth_decay_threshold | 0.15 | _removed_ | N/A | removed |
| max_confidence | 0.9 | _removed_ | N/A | removed |
| max_evap_participants | 2 | _removed_ | N/A | removed |
| max_hold_seconds | 1800 | _removed_ | N/A | removed |
| max_vol_ratio | 0.2 | _removed_ | N/A | removed |
| min_depth_decay_data_points | 10 | _removed_ | N/A | removed |
| min_top5_depth | 100 | _removed_ | N/A | removed |
| row | 3 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| stop_pct | 0.005 | _removed_ | N/A | removed |
| target_risk_mult | 1.5 | _removed_ | N/A | removed |

**Summary:** 14 V1 params → 0 V2 params | +0 added | -14 removed | 0 changed

### depth_imbalance_momentum
**Plan File:** `depth_imbalance_momentum.md`
**Strategy File:** `depth_imbalance_momentum.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 5 | _removed_ | N/A | removed |
| ir_exit_threshold | 1.5 | _removed_ | N/A | removed |
| ir_roc_threshold_long | 0.0 | _removed_ | N/A | removed |
| ir_roc_threshold_short | 0.0 | _removed_ | N/A | removed |
| ir_roc_window | 5 | _removed_ | N/A | removed |
| ir_threshold_long | 3.0 | _removed_ | N/A | removed |
| ir_threshold_short | 0.6 | _removed_ | N/A | removed |
| max_confidence | 0.9 | _removed_ | N/A | removed |
| max_hold_seconds | 1800 | _removed_ | N/A | removed |
| max_total_depth_decay | 0.05 | _removed_ | N/A | removed |
| min_avg_participants | 2.0 | _removed_ | N/A | removed |
| min_ir_data_points | 10 | _removed_ | N/A | removed |
| row | 4 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| stop_pct | 0.008 | _removed_ | N/A | removed |
| target_risk_mult | 2.0 | _removed_ | N/A | removed |
| volume_min_mult | 1.0 | _removed_ | N/A | removed |

**Summary:** 18 V1 params → 0 V2 params | +0 added | -18 removed | 0 changed

### exchange_flow_asymmetry
**Plan File:** `exchange_flow_asymmetry.md`
**Strategy File:** `exchange_flow_asymmetry.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 5 | _removed_ | N/A | removed |
| esi_threshold | 0.8 | _removed_ | N/A | removed |
| max_confidence | 0.95 | _removed_ | N/A | removed |
| max_hold_seconds | 3600 | _removed_ | N/A | removed |
| memx_deviation_threshold | 0.15 | _removed_ | N/A | removed |
| row | 5 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| stop_pct | 0.008 | _removed_ | N/A | removed |
| target_risk_mult | 2.5 | _removed_ | N/A | removed |
| volume_ratio_threshold | 1.5 | _removed_ | N/A | removed |

**Summary:** 11 V1 params → 0 V2 params | +0 added | -11 removed | 0 changed

### exchange_flow_concentration
**Plan File:** `exchange_flow_concentration.md`
**Strategy File:** `exchange_flow_concentration.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 1 | _removed_ | N/A | removed |
| row | 5 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |

**Summary:** 4 V1 params → 0 V2 params | +0 added | -4 removed | 0 changed

### exchange_flow_imbalance
**Plan File:** `exchange_flow_imbalance.md`
**Strategy File:** `exchange_flow_imbalance.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 4 | _removed_ | N/A | removed |
| iex_intent_threshold | 0.15 | _removed_ | N/A | removed |
| max_confidence | 0.95 | _removed_ | N/A | removed |
| max_hold_seconds | 2700 | _removed_ | N/A | removed |
| max_spread_mult | 2.0 | _removed_ | N/A | removed |
| row | 5 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| stop_pct | 0.005 | _removed_ | N/A | removed |
| target_risk_mult | 2.0 | _removed_ | N/A | removed |
| venue_concentration_threshold | 0.3 | _removed_ | N/A | removed |
| vsi_roc_threshold | 0.0 | _removed_ | N/A | removed |
| vsi_threshold | 0.3 | _removed_ | N/A | removed |

**Summary:** 13 V1 params → 0 V2 params | +0 added | -13 removed | 0 changed

### iv_gex_divergence
**Plan File:** `iv_gex_divergence_v2.md`
**Strategy File:** `iv_gex_divergence.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| FALLBACK_STOP_PCT | **0.006** | **0.006** | +0.0% | similar |
| GAMMA_DENSITY_DECLINE_THRESHOLD | **0.7** | **0.8** | +14.3% | more restrictive |
| GAMMA_DENSITY_WINDOW_PCT | **0.01** | **0.01** | +0.0% | similar |
| iv_decline_pct | 0.05 | _removed_ | N/A | removed |
| IV_DECLINE_RATIO | _new_ | 0.95 | N/A | added |
| IV_SKEW_OTM_PCT | **0.05** | **0.05** | +0.0% | similar |
| IV_SKEW_ROC_THRESHOLD | **0.15** | **0.1** | -33.3% | less restrictive |
| IV_SKEW_ROC_WINDOW | **5** | **5** | +0.0% | similar |
| IV_VOLUME_MIN | **100** | **100** | +0.0% | similar |
| iv_volume_weight_log | True | _removed_ | N/A | removed |
| max_hold_seconds | 2700 | _removed_ | N/A | removed |
| MIN_IV_POINTS | _new_ | 5 | N/A | added |
| MIN_POSITIVE_GAMMA | _new_ | 100000 | N/A | added |
| MIN_PRICE_POINTS | _new_ | 10 | N/A | added |
| PRICE_PERCENTILE_THRESHOLD | _new_ | 0.6 | N/A | added |
| STOP_PCT | **0.006** | **0.006** | +0.0% | similar |
| TARGET_RISK_MULT | **1.5** | **1.5** | +0.0% | similar |
| WALL_STOP_BUFFER_PCT | **0.002** | **0.002** | +0.0% | similar |
| WALL_STOP_MAX_DISTANCE_PCT | **0.02** | **0.02** | +0.0% | similar |

**Summary:** 14 V1 params → 16 V2 params | +5 added | -3 removed | 2 changed

### obi_aggression_flow
**Plan File:** `obi_aggression_flow.md`
**Strategy File:** `obi_aggression_flow.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| af_threshold | 0.5 | _removed_ | N/A | removed |
| col | 6 | _removed_ | N/A | removed |
| max_confidence | 0.9 | _removed_ | N/A | removed |
| max_hold_seconds | 900 | _removed_ | N/A | removed |
| max_spread_multiplier | 1.5 | _removed_ | N/A | removed |
| min_af_data_points | 5 | _removed_ | N/A | removed |
| min_avg_participants | 1.0 | _removed_ | N/A | removed |
| min_obi_data_points | 10 | _removed_ | N/A | removed |
| obi_threshold | 0.75 | _removed_ | N/A | removed |
| row | 2 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| stop_pct | 0.005 | _removed_ | N/A | removed |
| target_risk_mult | 1.5 | _removed_ | N/A | removed |
| trade_size_ma_window | 300 | _removed_ | N/A | removed |
| volume_spike_mult | 2.0 | _removed_ | N/A | removed |

**Summary:** 16 V1 params → 0 V2 params | +0 added | -16 removed | 0 changed

### order_book_fragmentation
**Plan File:** `order_book_fragmentation.md`
**Strategy File:** `order_book_fragmentation.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 1 | _removed_ | N/A | removed |
| frag_threshold | 0.5 | _removed_ | N/A | removed |
| max_confidence | 0.9 | _removed_ | N/A | removed |
| max_hold_seconds | 300 | _removed_ | N/A | removed |
| price_proximity_pct | 0.001 | _removed_ | N/A | removed |
| row | 6 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| stop_pct | 0.003 | _removed_ | N/A | removed |
| target_risk_mult | 3.0 | _removed_ | N/A | removed |
| wall_significance_mult | 3.0 | _removed_ | N/A | removed |

**Summary:** 11 V1 params → 0 V2 params | +0 added | -11 removed | 0 changed

### order_book_stacking
**Plan File:** `order_book_stacking.md`
**Strategy File:** `order_book_stacking.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 2 | _removed_ | N/A | removed |
| hold_time | 300 | _removed_ | N/A | removed |
| risk_reward | 3.0 | _removed_ | N/A | removed |
| row | 6 | _removed_ | N/A | removed |
| stop_pct | 0.3 | _removed_ | N/A | removed |

**Summary:** 5 V1 params → 0 V2 params | +0 added | -5 removed | 0 changed

### participant_divergence_scalper
**Plan File:** `participant_divergence_scalper.md`
**Strategy File:** `participant_divergence_scalper.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 3 | _removed_ | N/A | removed |
| decay_velocity_threshold | 0.0 | _removed_ | N/A | removed |
| fragility_threshold | 0.5 | _removed_ | N/A | removed |
| max_confidence | 0.95 | _removed_ | N/A | removed |
| max_hold_seconds | 180 | _removed_ | N/A | removed |
| max_spread_mult | 2.0 | _removed_ | N/A | removed |
| robust_threshold | 0.3 | _removed_ | N/A | removed |
| row | 5 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| stop_pct | 0.003 | _removed_ | N/A | removed |
| target_risk_mult | 1.5 | _removed_ | N/A | removed |
| vol_ratio_robust | 0.5 | _removed_ | N/A | removed |
| vol_ratio_spoof | 0.1 | _removed_ | N/A | removed |
| wall_size_mult | 5.0 | _removed_ | N/A | removed |

**Summary:** 15 V1 params → 0 V2 params | +0 added | -15 removed | 0 changed

### participant_diversity_conviction
**Plan File:** `participant_diversity_conviction.md`
**Strategy File:** `participant_diversity_conviction.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 2 | _removed_ | N/A | removed |
| conviction_exit | 0.4 | _removed_ | N/A | removed |
| conviction_threshold | 0.7 | _removed_ | N/A | removed |
| max_confidence | 0.9 | _removed_ | N/A | removed |
| max_exchanges_norm | 4.0 | _removed_ | N/A | removed |
| max_hold_seconds | 3600 | _removed_ | N/A | removed |
| max_participants_norm | 5.0 | _removed_ | N/A | removed |
| min_exchanges | 2 | _removed_ | N/A | removed |
| min_participants | 3.0 | _removed_ | N/A | removed |
| min_size_ratio | 0.5 | _removed_ | N/A | removed |
| row | 5 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| stop_pct | 0.008 | _removed_ | N/A | removed |
| target_risk_mult | 2.0 | _removed_ | N/A | removed |

**Summary:** 15 V1 params → 0 V2 params | +0 added | -15 removed | 0 changed

### vamp_momentum
**Plan File:** `vamp_momentum.md`
**Strategy File:** `vamp_momentum.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 6 | _removed_ | N/A | removed |
| columns | 6 | _removed_ | N/A | removed |
| depth_ma_window_seconds | 60 | _removed_ | N/A | removed |
| liquidity_density_min_mult | 1.2 | _removed_ | N/A | removed |
| max_confidence | 0.9 | _removed_ | N/A | removed |
| max_hold_seconds | 1800 | _removed_ | N/A | removed |
| min_avg_participants | 1.5 | _removed_ | N/A | removed |
| min_vamp_data_points | 10 | _removed_ | N/A | removed |
| N_TOP_LEVELS | 10 | _removed_ | N/A | removed |
| row | 2 | _removed_ | N/A | removed |
| rows | 8 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |
| spread_stability_ma_seconds | 300 | _removed_ | N/A | removed |
| stop_pct | 0.005 | _removed_ | N/A | removed |
| target_risk_mult | 1.5 | _removed_ | N/A | removed |
| vamp_mid_dev_threshold | 0.0005 | _removed_ | N/A | removed |
| vamp_roc_threshold | 0.0 | _removed_ | N/A | removed |
| vamp_roc_window | 5 | _removed_ | N/A | removed |

**Summary:** 19 V1 params → 0 V2 params | +0 added | -19 removed | 0 changed

### vortex_compression_breakout
**Strategy File:** `vortex_compression_breakout.py`
*No trading parameters found*

## Layer 3 (L3) - Advanced Convergence Strategies

### gamma_volume_convergence
**Plan File:** `gamma_volume_convergence_v2.md`
**Strategy File:** `gamma_volume_convergence.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| aggressor_ratio_threshold_long | 0.6 | _removed_ | N/A | removed |
| aggressor_ratio_threshold_short | 0.4 | _removed_ | N/A | removed |
| atr_max_target_pct | 0.02 | _removed_ | N/A | removed |
| atr_min_target_pct | 0.003 | _removed_ | N/A | removed |
| atr_mult | 1.5 | _removed_ | N/A | removed |
| coupling_min_ratio | 0.5 | _removed_ | N/A | removed |
| DELTA_ACCEL_MIN_RATIO | _new_ | 0.3 | N/A | added |
| DELTA_ACCEL_RATIO | **1.15** | **1.15** | +0.0% | similar |
| gamma_accel_threshold | 0.1 | _removed_ | N/A | removed |
| gamma_accel_window | 5 | _removed_ | N/A | removed |
| GAMMA_SPIKE_RATIO | **1.2** | **1.2** | +0.0% | similar |
| max_confidence | 0.9 | _removed_ | N/A | removed |
| max_hold_seconds | 900 | _removed_ | N/A | removed |
| MIN_DATA_POINTS | **3** | **3** | +0.0% | similar |
| PRICE_UP_THRESHOLD | _new_ | 0.001 | N/A | added |
| STOP_PCT | **0.005** | **0.005** | +0.0% | similar |
| target_pct | 0.01 | _removed_ | N/A | removed |
| VOLUME_SPIKE_RATIO | **1.2** | **1.2** | +0.0% | similar |

**Summary:** 16 V1 params → 7 V2 params | +2 added | -11 removed | 0 changed

### iv_band_breakout
**Plan File:** `iv_band_breakout_v2.md`
**Strategy File:** `iv_band_breakout.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| BREAKOUT_MOVE_PCT | _new_ | 0.0005 | N/A | added |
| DELTA_ACCEL_THRESHOLD | **1.1** | **1.1** | +0.0% | similar |
| DELTA_DECEL_RATIO | **0.95** | **0.95** | +0.0% | similar |
| max_confidence | 0.85 | _removed_ | N/A | removed |
| max_hold_seconds | 900 | _removed_ | N/A | removed |
| MIN_DATA_POINTS | _new_ | 5 | N/A | added |
| MIN_IV_DATA_POINTS | _new_ | 3 | N/A | added |
| NEGATIVE_GAMMA_TARGET_MULT | **1.5** | **1.5** | +0.0% | similar |
| POSITIVE_GAMMA_TARGET_MULT | **2.5** | **2.5** | +0.0% | similar |
| PRICE_COMPRESSION_RATIO | **0.4** | **0.4** | +0.0% | similar |
| SKEW_COMPRESSION_PCT | **0.25** | **0.25** | +0.0% | similar |
| SKEW_OTM_PCT | **0.05** | **0.05** | +0.0% | similar |
| STOP_PCT | **0.005** | **0.005** | +0.0% | similar |
| TARGET_IV_EXPANSION_CAP | **4.0** | **4.0** | +0.0% | similar |
| TARGET_IV_EXPANSION_MULT | **2.5** | **2.5** | +0.0% | similar |
| TARGET_IV_EXPANSION_NEG_MULT | **1.5** | **1.5** | +0.0% | similar |
| TARGET_MIN_PCT | **0.005** | **0.005** | +0.0% | similar |
| TARGET_PCT | **0.01** | **0.01** | +0.0% | similar |

**Summary:** 15 V1 params → 16 V2 params | +3 added | -2 removed | 0 changed

### strike_concentration
**Plan File:** `strike_concentration_v2.md`
**Strategy File:** `strike_concentration.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| atr_high_mult | 2.0 | _removed_ | N/A | removed |
| atr_high_threshold | 0.005 | _removed_ | N/A | removed |
| atr_low_mult | 1.0 | _removed_ | N/A | removed |
| atr_low_threshold | 0.002 | _removed_ | N/A | removed |
| atr_medium_mult | 1.5 | _removed_ | N/A | removed |
| ATR_NORMALIZATION_CAP | _new_ | 3.0 | N/A | added |
| BOUNCE_PROXIMITY_PCT | **0.005** | **0.005** | +0.0% | similar |
| BOUNCE_TARGET_MULT | _new_ | 1.5 | N/A | added |
| DELTA_ACCEL_THRESHOLD_LONG | _new_ | 1.08 | N/A | added |
| DELTA_ACCEL_THRESHOLD_SHORT | _new_ | 0.92 | N/A | added |
| depth_window_pct | 0.002 | _removed_ | N/A | removed |
| DIVERGENCE_VOLUME_THRESHOLD | _new_ | 0.8 | N/A | added |
| GAMMA_MAGNITUDE_THRESHOLD | _new_ | 0.5 | N/A | added |
| LIQUIDITY_VACUUM_RATIO | **0.3** | **3.0** | +900.0% | more restrictive |
| max_confidence | 0.85 | _removed_ | N/A | removed |
| max_hold_seconds | 600 | _removed_ | N/A | removed |
| MIN_DATA_POINTS | _new_ | 3 | N/A | added |
| SLICE_BODY_RATIO | **0.3** | **0.3** | +0.0% | similar |
| SLICE_TARGET_MULT | _new_ | 2.0 | N/A | added |
| SLICE_VOLUME_RATIO | **1.2** | **1.2** | +0.0% | similar |
| STOP_PCT_BOUNCE | **0.003** | **0.003** | +0.0% | similar |
| STOP_PCT_SLICE | **0.003** | **0.003** | +0.0% | similar |
| TARGET_MIN_PCT | **0.002** | **0.003** | +50.0% | more restrictive |
| TARGET_RISK_MULT | **1.5** | **1.5** | +0.0% | similar |
| TOP_OI_STRIKES_COUNT | **3** | **3** | +0.0% | similar |

**Summary:** 17 V1 params → 17 V2 params | +8 added | -8 removed | 2 changed

### theta_burn
**Plan File:** `theta_burn_v2.md`
**Strategy File:** `theta_burn.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| divergence_threshold | 0.15 | _removed_ | N/A | removed |
| iv_target_bounce_max_pct | 0.006 | _removed_ | N/A | removed |
| iv_target_bounce_min_pct | 0.002 | _removed_ | N/A | removed |
| iv_target_slice_max_pct | 0.008 | _removed_ | N/A | removed |
| max_confidence | 0.8 | _removed_ | N/A | removed |
| max_hold_seconds | 480 | _removed_ | N/A | removed |
| MAX_TARGET_PCT | **0.004** | **0.004** | +0.0% | similar |
| MIDNIGHT_UTC_END | _new_ | 19.5 | N/A | added |
| MIDNIGHT_UTC_START | _new_ | 16.5 | N/A | added |
| MIN_DATA_POINTS | _new_ | 3 | N/A | added |
| MIN_NET_GAMMA | **5000.0** | **5000.0** | +0.0% | similar |
| MIN_TARGET_PCT | **0.002** | **0.002** | +0.0% | similar |
| RANGE_NARROWNESS_RATIO | **0.4** | **0.4** | +0.0% | similar |
| STOP_PAST_WALL_PCT | **0.003** | **0.003** | +0.0% | similar |
| wall_min_ask_depth | 100 | _removed_ | N/A | removed |
| wall_min_bid_depth | 100 | _removed_ | N/A | removed |
| WALL_PROXIMITY_PCT | **0.005** | **0.005** | +0.0% | similar |
| wall_vacuum_depth | 50 | _removed_ | N/A | removed |

**Summary:** 15 V1 params → 9 V2 params | +3 added | -9 removed | 0 changed

## Full Data - Composite Strategies

### extrinsic_flow
**Strategy File:** `extrinsic_flow.py`
*No trading parameters found*

### extrinsic_intrinsic_flow
**Plan File:** `extrinsic_intrinsic_flow_v2.md`
**Strategy File:** `extrinsic_intrinsic_flow.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| aggressor_threshold | 0.55 | _removed_ | N/A | removed |
| extrinsic_accel_threshold | 0.1 | _removed_ | N/A | removed |
| EXTRINSIC_COLLAPSE_THRESHOLD | **0.1** | **0.1** | +0.0% | similar |
| EXTRINSIC_EXPANSION_THRESHOLD | **0.03** | **0.03** | +0.0% | similar |
| max_confidence | 0.8 | _removed_ | N/A | removed |
| max_hold_seconds | 10800 | _removed_ | N/A | removed |
| MIN_DATA_POINTS | **5** | **5** | +0.0% | similar |
| min_net_gamma | 500000.0 | _removed_ | N/A | removed |
| STOP_PCT | **0.005** | **0.005** | +0.0% | similar |
| target_iv_expansion_cap | 2.5 | _removed_ | N/A | removed |
| target_iv_expansion_fade_mult | 1.2 | _removed_ | N/A | removed |
| target_iv_expansion_mult | 1.6 | _removed_ | N/A | removed |
| target_min_pct | 0.005 | _removed_ | N/A | removed |
| target_pct | 0.008 | _removed_ | N/A | removed |
| VOLUME_SPIKE_RATIO | **1.3** | **1.3** | +0.0% | similar |

**Summary:** 15 V1 params → 5 V2 params | +0 added | -10 removed | 0 changed

### gamma_breaker
**Strategy File:** `gamma_breaker.py`
*No trading parameters found*

### ghost_premium
**Strategy File:** `ghost_premium.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| ASK_SIZE_SIGMA_MULT | _new_ | 2.0 | N/A | added |
| MAX_NET_CHANGE_PCT | _new_ | 0.02 | N/A | added |
| MIN_ASK_SIZE_SIGMA | _new_ | 1.0 | N/A | added |
| MIN_PDR_DATA_POINTS | _new_ | 10 | N/A | added |
| PDR_TRIGGER | _new_ | 0.6 | N/A | added |
| STOP_PCT | _new_ | 0.005 | N/A | added |
| TARGET_RISK_MULT | _new_ | 2.0 | N/A | added |

**Summary:** 0 V1 params → 7 V2 params | +7 added | 0 removed | 0 changed

### iron_anchor
**Strategy File:** `iron_anchor.py`
*No trading parameters found*

### iv_skew_squeeze
**Plan File:** `iv_skew_squeeze_v2.md`
**Strategy File:** `iv_skew_squeeze.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| DELTA_ROC_THRESHOLD | **0.05** | **0.05** | +0.0% | similar |
| max_confidence | 0.8 | _removed_ | N/A | removed |
| max_hold_seconds | 600 | _removed_ | N/A | removed |
| MIN_DATA_POINTS | _new_ | 5 | N/A | added |
| MIN_NET_GAMMA | **500000.0** | **500000.0** | +0.0% | similar |
| MIN_SKEW_DATA_POINTS | _new_ | 5 | N/A | added |
| PRICE_STABLE_THRESHOLD | **0.005** | **0.005** | +0.0% | similar |
| SKEW_EXTREME_POSITIVE | **0.2** | **0.2** | +0.0% | similar |
| SKEW_ROC_THRESHOLD | **0.05** | **0.05** | +0.0% | similar |
| STOP_PCT | **0.005** | **0.005** | +0.0% | similar |
| TARGET_IV_EXPANSION_CAP | **2.0** | **2.0** | +0.0% | similar |
| TARGET_IV_EXPANSION_MULT | **1.6** | **1.6** | +0.0% | similar |
| TARGET_MIN_PCT | **0.005** | **0.005** | +0.0% | similar |
| TARGET_PCT | **0.008** | **0.008** | +0.0% | similar |
| VOL_FRAGILE_THRESHOLD | **0.3** | **0.3** | +0.0% | similar |
| VOL_WEIGHTED_STABILITY_MIN | **0.5** | **0.5** | +0.0% | similar |
| VOLUME_SPIKE_THRESHOLD | **1.5** | **1.5** | +0.0% | similar |

**Summary:** 15 V1 params → 15 V2 params | +2 added | -2 removed | 0 changed

### prob_distribution_shift
**Plan File:** `prob_distribution_shift_v2.md`
**Strategy File:** `prob_distribution_shift.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| capital_breadth_threshold | 0.1 | _removed_ | N/A | removed |
| CONTRIBUTION_THRESHOLD | **0.05** | **0.05** | +0.0% | similar |
| max_confidence | 0.8 | _removed_ | N/A | removed |
| max_hold_seconds | 7200 | _removed_ | N/A | removed |
| MIN_CONSECUTIVE_SIGNALS | **2** | **2** | +0.0% | similar |
| MIN_DATA_POINTS | _new_ | 5 | N/A | added |
| MIN_NET_GAMMA | **500000.0** | **500000.0** | +0.0% | similar |
| MIN_STRIKES_WITH_DATA | **5** | **5** | +0.0% | similar |
| momentum_accel_threshold | 0.1 | _removed_ | N/A | removed |
| STOP_PCT | **0.005** | **0.005** | +0.0% | similar |
| target_iv_expansion_cap | 2.5 | _removed_ | N/A | removed |
| target_iv_expansion_mult | 1.6 | _removed_ | N/A | removed |
| target_min_pct | 0.005 | _removed_ | N/A | removed |
| target_pct | 0.008 | _removed_ | N/A | removed |
| Z_SCORE_THRESHOLD | **1.5** | **1.5** | +0.0% | similar |

**Summary:** 14 V1 params → 7 V2 params | +1 added | -8 removed | 0 changed

### prob_weighted_magnet
**Plan File:** `prob_weighted_magnet_v2.md`
**Strategy File:** `prob_weighted_magnet.py`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| CONSOLIDATION_RATIO | **0.5** | **0.5** | +0.0% | similar |
| DELTA_ACCEL_RATIO | **1.05** | **1.05** | +0.0% | similar |
| DELTA_ROC_THRESHOLD | **0.05** | **0.05** | +0.0% | similar |
| GAMMA_SCALE_BASE | **2.0** | **2.0** | +0.0% | similar |
| LIQUIDITY_VACUUM_RATIO | **0.3** | **0.3** | +0.0% | similar |
| max_confidence | 0.8 | _removed_ | N/A | removed |
| max_hold_seconds | 2700 | _removed_ | N/A | removed |
| MIN_DATA_POINTS | _new_ | 3 | N/A | added |
| MIN_NET_GAMMA | **500000.0** | **500000.0** | +0.0% | similar |
| MIN_OI_CONCENTRATION | **2.0** | **2.0** | +0.0% | similar |
| STOP_PCT | **0.005** | **0.005** | +0.0% | similar |
| TARGET_MIN_PCT | **0.005** | **0.005** | +0.0% | similar |
| TARGET_MULT_CAP | **3.0** | **3.0** | +0.0% | similar |
| TARGET_RISK_MULT | **1.5** | **1.5** | +0.0% | similar |

**Summary:** 13 V1 params → 12 V2 params | +1 added | -2 removed | 0 changed

### sentiment_sync
**Strategy File:** `sentiment_sync.py`
*No trading parameters found*

### skew_dynamics
**Strategy File:** `skew_dynamics.py`
*No trading parameters found*

### smile_dynamics
**Strategy File:** `smile_dynamics.py`
*No trading parameters found*

### whale_tracker
**Strategy File:** `whale_tracker.py`
*No trading parameters found*

## Unknown Layer

### archon_cdepth
**Plan File:** `archon_cdepth.md`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| normal | 0.35 | _removed_ | N/A | removed |
| spoofed | 0.5 | _removed_ | N/A | removed |
| stressed | 0.45 | _removed_ | N/A | removed |
| trending | 0.3 | _removed_ | N/A | removed |

**Summary:** 4 V1 params → 0 V2 params | +0 added | -4 removed | 0 changed

### depth_stream_design
**Plan File:** `depth_stream_design.md`
*No trading parameters found*

### forge_cdepth
**Plan File:** `forge_cdepth.md`
*No trading parameters found*

### heatmap_expansion
**Plan File:** `heatmap_expansion.md`

| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |
|-----------|---------------|-----------------|--------|-----------|
| col | 1 | _removed_ | N/A | removed |
| columns | 6 | _removed_ | N/A | removed |
| row | 5 | _removed_ | N/A | removed |
| rows | 8 | _removed_ | N/A | removed |
| span_cols | 1 | _removed_ | N/A | removed |
| span_rows | 1 | _removed_ | N/A | removed |

**Summary:** 6 V1 params → 0 V2 params | +0 added | -6 removed | 0 changed

### rune_cdepth
**Plan File:** `rune_cdepth.md`
*No trading parameters found*

### strategy-audit-plan-v2.21
**Plan File:** `strategy-audit-plan-v2.21.md`
*No trading parameters found*

### synapse_cdepth
**Plan File:** `synapse_cdepth.md`
*No trading parameters found*

---

## Quick Reference: Strategies with Parameter Changes

| Strategy | Layer | V1 → V2 | Added | Removed | Changed |
|----------|-------|---------|-------|---------|---------|
| archon_cdepth | unknown | 4 → _0_ | +0 | -4 | 0 |
| call_put_flow_asymmetry | layer2 | 14 → 5 | +5 | -14 | 0 |
| confluence_reversal | layer1 | _0_ → 12 | +12 | 0 | 0 |
| delta_gamma_squeeze | layer2 | _0_ → 15 | +15 | 0 | 0 |
| delta_iv_divergence | layer2 | 14 → 11 | +11 | -14 | 0 |
| delta_volume_exhaustion | layer2 | 13 → 16 | +16 | -13 | 0 |
| depth_decay_momentum | layer2 | 14 → _0_ | +0 | -14 | 0 |
| depth_imbalance_momentum | layer2 | 18 → _0_ | +0 | -18 | 0 |
| exchange_flow_asymmetry | layer2 | 11 → _0_ | +0 | -11 | 0 |
| exchange_flow_concentration | layer2 | 4 → _0_ | +0 | -4 | 0 |
| exchange_flow_imbalance | layer2 | 13 → _0_ | +0 | -13 | 0 |
| extrinsic_intrinsic_flow | full_data | 15 → 5 | +5 | -15 | 0 |
| gamma_flip_breakout | layer1 | _0_ → 8 | +8 | 0 | 0 |
| gamma_squeeze | layer1 | _0_ → 5 | +5 | 0 | 0 |
| gamma_volume_convergence | layer3 | 16 → 7 | +7 | -16 | 0 |
| gamma_wall_bounce | layer1 | _0_ → 4 | +4 | 0 | 0 |
| gex_divergence | layer1 | _0_ → 16 | +16 | 0 | 0 |
| gex_imbalance | layer1 | _0_ → 11 | +11 | 0 | 0 |
| ghost_premium | full_data | _0_ → 7 | +7 | 0 | 0 |
| heatmap_expansion | unknown | 6 → _0_ | +0 | -6 | 0 |
| iv_band_breakout | layer3 | 15 → 16 | +16 | -15 | 0 |
| iv_gex_divergence | layer2 | 14 → 16 | +16 | -14 | 0 |
| iv_skew_squeeze | full_data | 15 → 15 | +15 | -15 | 0 |
| magnet_accelerate | layer1 | _0_ → 6 | +6 | 0 | 0 |
| obi_aggression_flow | layer2 | 16 → _0_ | +0 | -16 | 0 |
| order_book_fragmentation | layer2 | 11 → _0_ | +0 | -11 | 0 |
| order_book_stacking | layer2 | 5 → _0_ | +0 | -5 | 0 |
| participant_divergence_scalper | layer2 | 15 → _0_ | +0 | -15 | 0 |
| participant_diversity_conviction | layer2 | 15 → _0_ | +0 | -15 | 0 |
| prob_distribution_shift | full_data | 14 → 7 | +7 | -14 | 0 |
| prob_weighted_magnet | full_data | 13 → 12 | +12 | -13 | 0 |
| strike_concentration | layer3 | 17 → 17 | +17 | -17 | 0 |
| theta_burn | layer3 | 15 → 9 | +9 | -15 | 0 |
| vamp_momentum | layer2 | 19 → _0_ | +0 | -19 | 0 |
| vol_compression_range | layer1 | _0_ → 11 | +11 | 0 | 0 |
