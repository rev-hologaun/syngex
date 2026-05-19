# Hardcoded Constants Audit - Issue #7

## Summary
This document catalogs all hardcoded configuration constants found in strategy files that should be config-driven via `strategies.yaml`.

## Findings by Layer

### Layer 1 Strategies

#### confluence_reversal.py
- `CONFLUENCE_DISTANCE_PCT = 0.003` → `confluence_distance_pct`
- `MIN_STRUCTURAL_SIGNALS = 1` → `min_structural_signals`
- `MAX_CONFIDENCE_BASE = 0.6` → `max_confidence_base`
- `MIN_CONFIDENCE = 0.65` → `min_confidence`
- `STOP_PCT = 0.008` → `stop_pct`
- `TARGET_RISK_MULT = 2.0` → `target_risk_mult`

#### gamma_flip_breakout.py
- `FLIP_PROXIMITY_PCT = 0.025` → `flip_proximity_pct`
- `STOP_OTHER_SIDE_PCT = 0.01` → `stop_other_side_pct`
- `ATR_MULT = 1.5` → `atr_mult` (already in config)
- `TARGET_RR = 2.5` → `target_rr`
- `MIN_CONFIDENCE = 0.65` → `min_confidence`
- `MIN_GAMMA_STRENGTH = 500000` → `min_gamma_strength`

#### gamma_wall_bounce.py
- `WALL_PROXIMITY_PCT = 0.005` → `wall_proximity_pct` (already in config)
- `STOP_PAST_WALL_PCT = 0.004` → `stop_past_wall_pct` (already in config)
- `TARGET_RISK_MULT = 1.5` → `target_risk_mult` (already in config)
- `MIN_WALL_GEX = 500000` → `min_wall_gex` (already in config)
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.85` → `max_confidence` (already in config)

#### gex_divergence.py
- `DIVERGENCE_MIN_SLOPE = 0.0005` → `divergence_min_slope`
- `DIVERGENCE_WINDOW = 30` → `divergence_window`
- `CONFIRMATION_CANDLE_PCT = 0.002` → `confirmation_candle_pct`
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `STOP_PCT = 0.005` → `stop_pct`
- `TARGET_RISK_MULT = 1.5` → `target_risk_mult`
- `MIN_DATA_POINTS = 15` → `min_data_points`
- `MIN_TOTAL_GEX = 1000000.0` → `min_total_gex`

#### gex_imbalance.py
- `PUT_HEAVY_RATIO = 0.5` → `put_heavy_threshold`
- `CALL_HEAVY_RATIO = 0.65` → `call_heavy_threshold`
- `STRONG_PUT_RATIO = 0.25` → `strong_put_ratio`
- `STRONG_CALL_RATIO = 0.75` → `strong_call_ratio`
- `MIN_MESSAGES = 20` → `min_messages`
- `STOP_VOL_MULT = 2.5` → `stop_vol_mult`
- `TARGET_RISK_MULT = 1.5` → `target_risk_mult`
- `MIN_CONFIDENCE = 0.55` → `min_confidence`

#### magnet_accelerate.py
- `MIN_MAGNET_GEX = 500000` → `min_magnet_gex`
- `MAGNET_EXIT_PCT = 0.003` → `magnet_exit_pct`
- `BREAKOUT_PCT = 0.002` → `breakout_pct`
- `MAX_BREAKOUT_PCT = 0.02` → `max_breakout_pct`
- `TRAIL_STOP_PCT = 0.01` → `trail_stop_pct`
- `TARGET_RISK_MULT = 1.5` → `target_risk_mult`
- `MIN_CONFIDENCE = 0.65` → `min_confidence`

#### vol_compression_range.py
- `COMPRESSION_PCT = 0.003` → `compression_pct`
- `MIN_RANGE_BARS = 20` → `min_range_bars`
- `WALL_EDGE_PROXIMITY = 0.004` → `wall_edge_proximity`
- `MIN_CONFIDENCE = 0.45` → `min_confidence`
- `STOP_PCT = 0.006` → `stop_pct`
- `TARGET_RISK_MULT = 1.5` → `target_risk_mult`
- `STD_THRESHOLD = 0.002` → `std_threshold`

### Layer 2 Strategies

#### call_put_flow_asymmetry.py
- `FLOW_THRESHOLD = 1.5` → `flow_threshold` (already in config)
- `MIN_GREEKS_POINTS = 3` → `min_greeks_points`
- `IV_SKEW_THRESHOLD = 0.03` → `iv_skew_threshold` (already in config)
- `MIN_CONFIDENCE = 0.35` → `min_confidence`
- `STOP_PCT = 0.006` → `stop_pct` (already in config)
- `TARGET_RISK_MULT = 2.0` → `target_risk_mult` (already in config)

#### delta_iv_divergence.py
- `MIN_DATA_POINTS = 5` → `min_data_points`
- `MIN_DIVERSION_STRENGTH = 0.3` → `min_diversion_strength`
- `MIN_CONFIDENCE = 0.35` → `min_confidence`
- `STOP_PCT = 0.008` → `stop_pct`
- `TARGET_RISK_MULT = 2.0` → `target_risk_mult`

#### delta_volume_exhaustion.py
- `MIN_TREND_POINTS = 5` → `min_trend_points`
- `MIN_GREEKS_POINTS = 5` → `min_greeks_points`
- `DELTA_DECLINE_RATIO = 0.95` → `delta_decline_ratio`
- `VOLUME_DECLINE_RATIO = 0.90` → `volume_decline_ratio`
- `MIN_TREND_DURATION = 2` → `min_trend_duration`
- `STOP_PCT = 0.008` → `stop_pct`
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MEAN_REVERSION_MULT = 1.0` → `mean_reversion_mult`

#### iv_gex_divergence.py
- `PRICE_PERCENTILE_THRESHOLD = 0.70` → `price_percentile_threshold`
- `MIN_PRICE_POINTS = 10` → `min_price_points`
- `MIN_IV_POINTS = 5` → `min_iv_points`
- `MIN_POSITIVE_GAMMA = 200000` → `min_positive_gamma`
- `IV_DECLINE_RATIO = 0.95` → `iv_decline_ratio`
- `STOP_PCT = 0.006` → `stop_pct`
- `TARGET_RISK_MULT = 1.5` → `target_risk_mult`
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.95` → `max_confidence`

### Layer 3 Strategies

#### gamma_volume_convergence.py
- `DELTA_ACCEL_RATIO = 1.10` → `delta_accel_ratio`
- `DELTA_ACCEL_MIN_RATIO = 0.30` → `delta_accel_min_ratio`
- `GAMMA_SPIKE_RATIO = 1.15` → `gamma_spike_ratio`
- `VOLUME_SPIKE_RATIO = 1.15` → `volume_spike_ratio`
- `STOP_PCT = 0.005` → `stop_pct`
- `TARGET_PCT = 0.010` → `target_pct`
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.90` → `max_confidence`
- `MIN_DATA_POINTS = 3` → `min_data_points`
- `PRICE_UP_THRESHOLD = 0.001` → `price_up_threshold`
- `PRICE_DOWN_THRESHOLD = -0.001` → `price_down_threshold`

#### iv_band_breakout.py
- `DELTA_DECEL_RATIO = 0.95` → `delta_decel_ratio`
- `PRICE_COMPRESSION_RATIO = 0.40` → `price_compression_ratio`
- `BREAKOUT_MOVE_PCT = 0.0005` → `breakout_move_pct`
- `VOLUME_TREND_REQUIRED = True` → `volume_trend_required`
- `STOP_PCT = 0.005` → `stop_pct` (already in config)
- `TARGET_PCT = 0.010` → `target_pct` (already in config)
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.85` → `max_confidence` (already in config)
- `MIN_DATA_POINTS = 5` → `min_data_points`
- `MIN_IV_DATA_POINTS = 3` → `min_iv_data_points`

#### strike_concentration.py
- `TOP_OI_STRIKES_COUNT = 3` → `top_oi_strikes_count` (already in config)
- `BOUNCE_PROXIMITY_PCT = 0.005` → `bounce_proximity_pct`
- `SLICE_BODY_RATIO = 0.3` → `slice_body_ratio`
- `SLICE_VOLUME_RATIO = 1.20` → `slice_volume_ratio`
- `DIVERGENCE_VOLUME_THRESHOLD = 0.80` → `divergence_volume_threshold`
- `STOP_PCT_BOUNCE = 0.003` → `stop_pct_bounce`
- `STOP_PCT_SLICE = 0.003` → `stop_pct_slice`
- `TARGET_RISK_MULT = 1.5` → `target_risk_mult`
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.85` → `max_confidence`
- `MIN_DATA_POINTS = 3` → `min_data_points`

### Full Data Strategies

#### extrinsic_intrinsic_flow.py
- `EXTRINSIC_EXPANSION_THRESHOLD = 0.03` → `extrinsic_expansion_threshold`
- `EXTRINSIC_COLLAPSE_THRESHOLD = 0.10` → `extrinsic_collapse_threshold`
- `VOLUME_SPIKE_RATIO = 1.30` → `volume_spike_ratio`
- `MIN_NET_GAMMA = 500000.0` → `min_net_gamma`
- `STOP_PCT = 0.005` → `stop_pct` (already in config)
- `TARGET_PCT = 0.008` → `target_pct` (already in config)
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.80` → `max_confidence` (already in config)
- `MIN_DATA_POINTS = 5` → `min_data_points`
- `VALID_VOLUME_TREND_LONG = ["UP"]` → `valid_volume_trend_long`
- `VALID_VOLUME_TREND_SHORT = ["DOWN"]` → `valid_volume_trend_short`
- `VALID_VOLUME_TREND_FADE = ["DOWN", "FLAT"]` → `valid_volume_trend.fade`

#### iv_skew_squeeze.py
- `SKEW_EXTREME_POSITIVE = 0.20` → `skew_extreme_positive`
- `SKEW_EXTREME_NEGATIVE = -0.07` → `skew_extreme_negative`
- `PRICE_STABLE_THRESHOLD = 0.005` → `price_stable_threshold` (already in config)
- `MIN_NET_GAMMA = 500000.0` → `min_net_gamma`
- `STOP_PCT = 0.005` → `stop_pct` (already in config)
- `TARGET_PCT = 0.008` → `target_pct` (already in config)
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.80` → `max_confidence` (already in config)
- `MIN_DATA_POINTS = 5` → `min_data_points`
- `MIN_SKEW_DATA_POINTS = 5` → `min_skew_data_points`
- `VOLUME_SPIKE_THRESHOLD = 1.5` → `volume_spike_threshold`

#### prob_distribution_shift.py
- `Z_SCORE_THRESHOLD = 1.5` → `z_score_threshold`
- `MIN_CONSECUTIVE_SIGNALS = 2` → `min_consecutive_signals`
- `MIN_NET_GAMMA = 500000.0` → `min_net_gamma`
- `STOP_PCT = 0.005` → `stop_pct` (already in config)
- `TARGET_PCT = 0.008` → `target_pct` (already in config)
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.80` → `max_confidence` (already in config)
- `MIN_STRIKES_WITH_DATA = 5` → `min_strikes_with_data`
- `MIN_DATA_POINTS = 5` → `min_data_points`
- `VOLUME_TREND_ALLOWED_LONG = ["FLAT", "UP"]` → `volume_trend_allowed_long`
- `VOLUME_TREND_ALLOWED_SHORT = ["FLAT", "DOWN"]` → `volume_trend_allowed_short`
- `CONTRIBUTION_THRESHOLD = 0.05` → `contribution_threshold`

#### prob_weighted_magnet.py
- `MIN_OI_CONCENTRATION = 2.0` → `min_oi_concentration`
- `CONSOLIDATION_RATIO = 0.50` → `consolidation_ratio`
- `DELTA_ACCEL_RATIO = 1.05` → `delta_accel_ratio`
- `MIN_NET_GAMMA = 500000.0` → `min_net_gamma`
- `STOP_PCT = 0.005` → `stop_pct` (already in config)
- `TARGET_RISK_MULT = 1.5` → `target_risk_mult` (already in config)
- `MIN_CONFIDENCE = 0.25` → `min_confidence`
- `MAX_CONFIDENCE = 0.80` → `max_confidence` (already in config)
- `MIN_DATA_POINTS = 3` → `min_data_points`
- `VALID_VOLUME_TRENDS = ("FLAT", "DOWN")` → `valid_volume_trends`

## Implementation Plan

1. Update each strategy file to:
   - Remove class-level constants
   - Use `self._params.get('key', DEFAULT_VALUE)` pattern
   - Call `_apply_params(data)` at start of `evaluate()`

2. Update `config/strategies.yaml` to add missing parameters with comments

3. Verify `strategies/engine.py` properly passes config (already done - it does)

4. Run `python3 -m py_compile` on all modified files
