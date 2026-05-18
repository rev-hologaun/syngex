# Syngex Strategy Parameters - v2.41
**Generated:** /home/hologaun/projects/syngex
---

## LAYER1

### `strategies/layer1/confluence_reversal.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `CONFLUENCE_DISTANCE_PCT` | 0.005 | 0.5% — max distance for confluence |
| `MIN_STRUCTURAL_SIGNALS` | 1 | Wall-level confluence alone is valid |
| `MIN_CONFIDENCE` | 0.10 | Minimum confidence to emit signal |
| `STOP_PCT` | 0.008 | 0.8% stop |
| `TARGET_RISK_MULT` | 2.0 | 2× risk for target |
| `VELOCITY_MIN_ZSCORE` | 0.5 | Minimum \|z-score\| for approach velocity |
| `VELOCITY_MIN_VOLUME_MULT` | 1.05 | Volume must be >= 1.05x rolling average |
| `IV_WEIGHT_BASE` | 1.0 |  |
| `IV_WEIGHT_MAX` | 1.5 |  |
| `IV_WEIGHT_SKEW_THRESHOLD` | 0.05 |  |
| `DEPTH_SPIKE_THRESHOLD` | 1.3 | Current depth >= 1.3x rolling average |
| `NEGATIVE_GAMMA_STOP_MULT` | 1.5 | Wider stops in negative gamma (more noise) |
| `POSITIVE_GAMMA_STOP_MULT` | 0.75 | Tighter stops in positive gamma (cleaner) |

### `strategies/layer1/gamma_flip_breakout.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `FLIP_PROXIMITY_PCT` | 0.025 | 2.5% — price must be within this of flip |
| `FLIP_ZONE_PCT` | 0.015 | 1.5% — the transition zone around flip |
| `STOP_OTHER_SIDE_PCT` | 0.01 | 1% — stop on other side of flip |
| `ATR_MULT` | 1.5 | 1.5× rolling range as ATR proxy |
| `TARGET_RR` | 2.5 | 1:2.5 risk-reward minimum |
| `MIN_CONFIDENCE` | 0.10 | Minimum confidence to emit signal |
| `MIN_GAMMA_STRENGTH` | 100000 | Minimum \|net_gamma\| for regime confidence |
| `NEGATIVE_GAMMA_STOP_MULT` | 2.5 | Wider stops in negative gamma (more noise) |
| `POSITIVE_GAMMA_STOP_MULT` | 0.75 | Tighter stops in positive gamma (less noise) |

### `strategies/layer1/gamma_squeeze.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `PIN_MAX_RANGE_PCT` | 0.003 | 0.3% — max rolling range for pin detection |
| `WALL_PROXIMITY_PCT` | 0.003 | 0.3% — price must be near wall for breakout |
| `VOLUME_SURGE_MULT` | 1.5 | 1.5× average volume = confirmation |
| `MIN_WALL_GEX` | 500000 | Minimum \|GEX\| for wall consideration |
| `MIN_CONFIDENCE` | 0.10 | relaxed from 0.15 |
| `TARGET_RISK_MULT` | 2.0 | 2× risk for squeeze targets |
| `MIN_MASSIVE_WALL_GEX` | 5_000_000 | Fallback threshold for POSITIVE regime filter |

### `strategies/layer1/gamma_wall_bounce.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `WALL_PROXIMITY_PCT` | 0.005 | 0.5% — how close price must be to wall |
| `STOP_PAST_WALL_PCT` | 0.004 | 0.4% — stop beyond the wall |
| `TARGET_RISK_MULT` | 1.5 | 1.5× risk for target |
| `MIN_WALL_GEX` | 500000 | Minimum \|GEX\| to consider a wall |
| `MIN_CONFIDENCE` | 0.10 | Minimum confidence to emit signal |
| `VELOCITY_THRESHOLD` | 0.005 |  |

### `strategies/layer1/gex_divergence.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `DIVERGENCE_MIN_SLOPE` | 0.0005 | Minimum slope magnitude (0.05% — catches subtler divergences) |
| `DIVERGENCE_WINDOW` | 30 | Number of points for slope calculation |
| `CONFIRMATION_CANDLE_PCT` | 0.002 | 0.2% candle for confirmation |
| `MIN_CONFIDENCE` | 0.10 | Minimum confidence to emit signal (relaxed for v2 Structural-Decay) |
| `STOP_PCT` | 0.005 | 0.5% stop |
| `TARGET_RISK_MULT` | 1.5 | 1.5× risk for target |
| `MIN_DATA_POINTS` | 15 | Minimum data points for slope calculation |
| `MIN_TOTAL_GEX` | 1000000.0 | 1M — minimum GEX wall strength |
| `ACCEL_WINDOW_SHORT` | 10 |  |
| `ACCEL_WINDOW_LONG` | 30 |  |
| `ACCEL_MIN_GAMMA` | 0.0003 |  |
| `ACCEL_MIN_PRICE` | 0.0002 |  |
| `WALL_PROXIMITY_PCT` | 0.005 |  |
| `WALL_PROXIMITY_BONUS` | 0.15 |  |
| `LIQUIDITY_DECAY_THRESHOLD` | 0.3 |  |
| `REGIME_INTENSITY_THRESHOLD` | 500000 |  |
| `STRONG_REGIME_CONF_BONUS` | 0.1 |  |

### `strategies/layer1/gex_imbalance.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `PUT_HEAVY_RATIO` | 0.5 | < 0.5 → long bias |
| `CALL_HEAVY_RATIO` | 0.65 | > 0.65 → short bias |
| `STRONG_PUT_RATIO` | 0.25 | very strong long signal |
| `STRONG_CALL_RATIO` | 0.75 | very strong short signal |
| `MIN_MESSAGES` | 20 | minimum data points for signal quality |
| `STOP_VOL_MULT` | 2.5 | stop = 2.5x rolling price std dev |
| `TARGET_RISK_MULT` | 1.5 | target = 1.5x stop distance |
| `MIN_CONFIDENCE` | 0.10 | Minimum confidence to emit signal |
| `RATIO_ROC_WINDOW` | 5 | Number of ticks back for ROC |
| `RATIO_ROC_THRESHOLD` | 0.10 | Minimum ROC to trigger (10% change) |
| `REGIME_GAMMA_THRESHOLD` | 500000 |  |
| `VWAP_DEVIATION_MIN_STD` | 1.5 |  |

### `strategies/layer1/magnet_accelerate.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_MAGNET_GEX` | 500000 | Minimum \|normalized GEX\| to be a magnet (on same scale as wall threshold) |
| `MAGNET_EXIT_PCT` | 0.003 | 0.3% — exit within this % of magnet |
| `BREAKOUT_PCT` | 0.002 | 0.2% — price must be this far past magnet to breakout |
| `MAX_BREAKOUT_PCT` | 0.02 | 2% — max distance past magnet (no chasing) |
| `TRAIL_STOP_PCT` | 0.01 | 1% — trailing stop for Phase 2 |
| `TARGET_RISK_MULT` | 1.5 | Minimum 1.5× risk for target distance |
| `MIN_CONFIDENCE` | 0.10 | Minimum confidence to emit signal |

### `strategies/layer1/vol_compression_range.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `COMPRESSION_PCT` | 0.003 | 0.3% max range for compression |
| `MIN_RANGE_BARS` | 20 | Minimum data points in rolling window |
| `WALL_EDGE_PROXIMITY` | 0.004 | 0.4% from wall for edge trade |
| `MIN_CONFIDENCE` | 0.10 | Minimum confidence to emit signal (relaxed) |
| `STOP_PCT` | 0.006 | 0.6% stop (wider for scalping) |
| `TARGET_RISK_MULT` | 1.5 | 1.5× risk for target |
| `STD_THRESHOLD` | 0.002 | Max std of price for compression |
| `IV_COMPRESSION_STD_THRESHOLD` | 0.03 | Max rolling std of IV skew for compression |
| `DEPTH_SPIKE_THRESHOLD` | 1.3 | Current depth >= 1.3x rolling avg for edge validation |
| `REGIME_GAMMA_INTENSITY_THRESHOLD` | 500000 | \|net_gamma\| for strong regime |
| `NEGATIVE_REGIME_STOP_MULT` | 1.5 | Wider stops (fallback, strategy requires POSITIVE) |
| `POSITIVE_REGIME_TIGHT_STOP_MULT` | 0.7 | Tighter stops in strong positive gamma |


## LAYER2

### `strategies/layer2/call_put_flow_asymmetry.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `FLOW_THRESHOLD` | 1.2 | Call Score > 1.2× Put Score |
| `MIN_GREEKS_POINTS` | 3 |  |
| `IV_SKEW_THRESHOLD` | 0.02 | 2% IV difference |
| `MIN_CONFIDENCE` | 0.10 |  |
| `STOP_PCT` | 0.006 | 0.6% stop |
| `TARGET_RISK_MULT` | 2.0 | 2× risk target |

### `strategies/layer2/delta_gamma_squeeze.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `WALL_PROXIMITY_PCT` | 0.05 | 5% (was 3%) — wider wall proximity |
| `DELTA_ACCEL_RATIO` | 1.05 | 5% above rolling avg (was 10%) |
| `VOLUME_SPIKE_RATIO` | 1.10 | 10% above rolling avg |
| `MIN_WALL_GEX` | 500000 |  |
| `PRICE_ABOVE_MEAN_CONFIDENCE` | 0.55 | Price in upper half of 5m window |
| `MIN_DATA_POINTS` | 2 | Fewer points needed (was 3) |
| `MIN_CONFIDENCE` | 0.10 |  |
| `STOP_BELOW_WALL_PCT` | 0.008 | 0.8% below entry |
| `TARGET_RISK_MULT` | 2.0 | 2× risk for target |
| `GEX_ACCEL_RATIO` | 1.10 |  |
| `DELTA_ACCEL_MIN` | 1.05 |  |
| `GEX_ACCEL_MIN` | 1.03 |  |
| `LIQUIDITY_VACUUM_DEPTH_RATIO` | 0.9 |  |
| `IV_ROC_THRESHOLD` | 0.02 |  |
| `IV_CONF_BONUS` | 0.08 |  |
| `ACCEL_STOP_WIDEN_MULT` | 1.5 |  |

### `strategies/layer2/delta_iv_divergence.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_DATA_POINTS` | 3 |  |
| `MIN_DIVERSION_STRENGTH` | 0.2 |  |
| `STOP_PCT` | 0.008 | 0.8% |
| `MIN_CONFIDENCE` | 0.10 |  |
| `SK_DIV_THRESHOLD` | 0.03 |  |
| `DECOUPLE_HISTORY_WINDOW` | 30 |  |
| `DECOUPLE_THRESHOLD` | 0.80 |  |
| `GAMMA_DECLINE_THRESHOLD` | 0.85 |  |
| `TARGET_IV_MULT` | 2.0 |  |
| `TARGET_IV_CAP` | 4.0 |  |
| `WALL_PROX_PCT` | 0.01 |  |
| `WALL_PROX_BONUS` | 0.10 |  |

### `strategies/layer2/delta_volume_exhaustion.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_TREND_POINTS` | 5 |  |
| `MIN_GREEKS_POINTS` | 5 |  |
| `DELTA_DECLINE_RATIO` | 0.95 | Delta below 95% of rolling avg (was 90%) |
| `MIN_TREND_DURATION` | 2 | At least 2 candles in trend (was 3) |
| `STOP_PCT` | 0.008 | 0.8% beyond swing |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MEAN_REVERSION_MULT` | 1.0 | 1.0× distance — target is the rolling mean |
| `LIQUIDITY_VACUUM_RATIO_STABILITY` | 0.15 | ratio must be within 15% of rolling mean |
| `LIQUIDITY_VACUUM_SPREAD_WIDEN_MULT` | 1.10 | spread must be > 1.10× rolling mean |
| `IV_ACCEL_WINDOW` | 5 | window for IV ROC calculation |
| `IV_ACCEL_BONUS` | 0.15 | confidence bonus when IV aligns |
| `IV_ACCEL_PENALTY` | -0.05 | confidence penalty when IV opposes |
| `WALL_PROXIMITY_PCT` | 0.003 | within 0.3% of wall |
| `WALL_PROXIMITY_BONUS` | 0.10 | confidence bonus |
| `NEGATIVE_GAMMA_TARGET_MULT` | 1.5 | NEG regime: let it run |
| `POSITIVE_GAMMA_TARGET_MULT` | 0.8 | POS regime: quick profits |
| `NEUTRAL_GAMMA_TARGET_MULT` | 1.0 | baseline |
| `GAMMA_INTENSITY_THRESHOLD` | 500000 | threshold for regime classification |

### `strategies/layer2/depth_decay_momentum.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/depth_imbalance_momentum.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/exchange_flow_asymmetry.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/exchange_flow_concentration.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/exchange_flow_imbalance.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/iv_gex_divergence.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `PRICE_PERCENTILE_THRESHOLD` | 0.60 | p60 — price in top 40% of range |
| `MIN_PRICE_POINTS` | 10 |  |
| `MIN_IV_POINTS` | 5 |  |
| `MIN_POSITIVE_GAMMA` | 100000 | $100k net gamma |
| `IV_DECLINE_RATIO` | 0.95 | IV below 95% of rolling avg |
| `STOP_PCT` | 0.006 | 0.6% fallback stop |
| `TARGET_RISK_MULT` | 1.5 | 1.5× risk toward mean |
| `MIN_CONFIDENCE` | 0.10 |  |
| `IV_SKEW_OTM_PCT` | 0.05 | 5% OTM for skew calculation |
| `IV_SKEW_ROC_WINDOW` | 5 | ticks for skew ROC |
| `IV_SKEW_ROC_THRESHOLD` | 0.10 | skew must have risen ≥10% |
| `GAMMA_DENSITY_WINDOW_PCT` | 0.01 | ±1% window for gamma density |
| `GAMMA_DENSITY_DECLINE_THRESHOLD` | 0.80 | density must decline ≥20% |
| `IV_VOLUME_MIN` | 100 | min volume to consider IV meaningful |
| `WALL_STOP_BUFFER_PCT` | 0.002 | 0.2% buffer beyond wall |
| `WALL_STOP_MAX_DISTANCE_PCT` | 0.02 | max distance to nearest wall (2%) |
| `FALLBACK_STOP_PCT` | 0.006 | fallback if no wall nearby |

### `strategies/layer2/obi_aggression_flow.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/order_book_fragmentation.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/order_book_stacking.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/participant_divergence_scalper.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/participant_diversity_conviction.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/vamp_momentum.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/layer2/vortex_compression_breakout.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |


## LAYER3

### `strategies/layer3/gamma_volume_convergence.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `DELTA_ACCEL_RATIO` | 1.15 |  |
| `DELTA_ACCEL_MIN_RATIO` | 0.30 |  |
| `GAMMA_SPIKE_RATIO` | 1.20 |  |
| `VOLUME_SPIKE_RATIO` | 1.20 |  |
| `STOP_PCT` | 0.005 |  |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MIN_DATA_POINTS` | 3 |  |
| `PRICE_UP_THRESHOLD` | 0.001 | 0.1% rise over 5m window |
| `PRICE_DOWN_THRESHOLD` | -0.001 | 0.1% drop over 5m window |

### `strategies/layer3/iv_band_breakout.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `DELTA_DECEL_RATIO` | 0.95 |  |
| `PRICE_COMPRESSION_RATIO` | 0.40 |  |
| `BREAKOUT_MOVE_PCT` | 0.0005 |  |
| `STOP_PCT` | 0.005 | 0.5% stop |
| `TARGET_PCT` | 0.010 | 1.0% target |
| `MIN_CONFIDENCE` | 0.10 | Raised from 0.25, lowered to 0.10 for global confluence hunting |
| `MIN_DATA_POINTS` | 5 |  |
| `MIN_IV_DATA_POINTS` | 3 |  |
| `SKEW_OTM_PCT` | 0.05 | OTM strike distance (5%) |
| `SKEW_COMPRESSION_PCT` | 0.25 | skew must be in bottom 25% of range |
| `POSITIVE_GAMMA_TARGET_MULT` | 2.5 |  |
| `NEGATIVE_GAMMA_TARGET_MULT` | 1.5 |  |
| `DELTA_ACCEL_THRESHOLD` | 1.10 | delta must accelerate ≥10% at breakout |
| `TARGET_IV_EXPANSION_MULT` | 2.5 | base multiplier for POS regime |
| `TARGET_IV_EXPANSION_NEG_MULT` | 1.5 | base multiplier for NEG regime |
| `TARGET_IV_EXPANSION_CAP` | 4.0 | cap on multiplier |
| `TARGET_MIN_PCT` | 0.005 | minimum 0.5% target |

### `strategies/layer3/strike_concentration.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `TOP_OI_STRIKES_COUNT` | 3 |  |
| `BOUNCE_PROXIMITY_PCT` | 0.005 | 0.5% |
| `SLICE_BODY_RATIO` | 0.3 | 30% body |
| `SLICE_VOLUME_RATIO` | 1.20 | 20% above rolling avg |
| `DIVERGENCE_VOLUME_THRESHOLD` | 0.80 | Volume < 80% of avg = declining |
| `STOP_PCT_BOUNCE` | 0.003 | 0.3% beyond the strike for bounces |
| `STOP_PCT_SLICE` | 0.003 | 0.3% against entry for slices |
| `TARGET_RISK_MULT` | 1.5 | 1.5× risk for bounce targets |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MIN_DATA_POINTS` | 3 |  |
| `LIQUIDITY_VACUUM_RATIO` | 3.0 |  |
| `DELTA_ACCEL_THRESHOLD_LONG` | 1.08 | delta accelerated ≥8% |
| `DELTA_ACCEL_THRESHOLD_SHORT` | 0.92 | delta decelerated ≥8% |
| `GAMMA_MAGNITUDE_THRESHOLD` | 0.50 |  |
| `BOUNCE_TARGET_MULT` | 1.5 |  |
| `SLICE_TARGET_MULT` | 2.0 |  |
| `ATR_NORMALIZATION_CAP` | 3.0 |  |
| `TARGET_MIN_PCT` | 0.003 |  |

### `strategies/layer3/theta_burn.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_NET_GAMMA` | 5000.0 |  |
| `WALL_PROXIMITY_PCT` | 0.005 | 0.5% |
| `STOP_PAST_WALL_PCT` | 0.003 | 0.3% beyond the wall |
| `MIN_TARGET_PCT` | 0.002 | 0.2% min target |
| `MAX_TARGET_PCT` | 0.004 | 0.4% max target |
| `RANGE_NARROWNESS_RATIO` | 0.40 | 40% |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MIN_DATA_POINTS` | 3 |  |
| `MIDNIGHT_UTC_START` | 16.5 | 16:30 UTC |
| `MIDNIGHT_UTC_END` | 19.5 | 19:30 UTC |
| `GAMMA_STRENGTH_HIGH` | 1_000_000.0 | Above this = max gamma strength bonus |


## FULL_DATA

### `strategies/full_data/extrinsic_flow.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/full_data/extrinsic_intrinsic_flow.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `EXTRINSIC_EXPANSION_THRESHOLD` | 0.03 | 3% expansion |
| `EXTRINSIC_COLLAPSE_THRESHOLD` | 0.10 | 10% collapse |
| `VOLUME_SPIKE_RATIO` | 1.30 | 130% of avg (1.3×) |
| `STOP_PCT` | 0.005 | 0.5% stop |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MIN_DATA_POINTS` | 5 |  |
| `VALID_VOLUME_TREND_LONG` | ["UP"] |  |
| `VALID_VOLUME_TREND_SHORT` | ["DOWN"] |  |
| `VALID_VOLUME_TREND_FADE` | ["DOWN", "FLAT"] |  |

### `strategies/full_data/gamma_breaker.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/full_data/ghost_premium.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `PDR_TRIGGER` | 0.60 | Calls 60%+ overpriced vs theoretical |
| `MIN_PDR_DATA_POINTS` | 10 |  |
| `ASK_SIZE_SIGMA_MULT` | 2.0 |  |
| `STOP_PCT` | 0.005 | 0.5% stop |
| `TARGET_RISK_MULT` | 2.0 | 2.0× risk for target |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MIN_ASK_SIZE_SIGMA` | 1.0 |  |
| `MAX_NET_CHANGE_PCT` | 0.02 |  |

### `strategies/full_data/iron_anchor.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/full_data/iv_skew_squeeze.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `SKEW_EXTREME_POSITIVE` | 0.20 | Calls 20%+ more expensive (euphoria) |
| `SKEW_EXTREME_NEGATIVE` | -0.07 | Puts 7%+ more expensive (panic) |
| `PRICE_STABLE_THRESHOLD` | 0.005 | 0.5% change max |
| `MIN_NET_GAMMA` | 500000.0 | 500k — matches other strategies' thresholds |
| `STOP_PCT` | 0.005 | 0.5% stop |
| `TARGET_PCT` | 0.008 | 0.8% target (1.6:1 R:R) |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MIN_DATA_POINTS` | 5 | Need data for basic checks |
| `MIN_SKEW_DATA_POINTS` | 5 | Minimum for skew rolling window |
| `VOLUME_SPIKE_THRESHOLD` | 1.5 | Volume > 1.5× avg = spike |
| `SKEW_ROC_THRESHOLD` | 0.05 | 5% ROC for skew acceleration |
| `VOL_WEIGHTED_STABILITY_MIN` | 0.50 | min conviction stability |
| `VOL_FRAGILE_THRESHOLD` | 0.30 | volume < 30% avg = fragile |
| `DELTA_ROC_THRESHOLD` | 0.05 | 5% ROC for delta confirmation |
| `TARGET_IV_EXPANSION_MULT` | 1.6 | base multiplier for IV-scaled target |
| `TARGET_IV_EXPANSION_CAP` | 2.0 | cap on target multiplier |
| `TARGET_MIN_PCT` | 0.005 | minimum target 0.5% |

### `strategies/full_data/prob_distribution_shift.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `Z_SCORE_THRESHOLD` | 1.5 | 1.5 standard deviations |
| `MIN_CONSECUTIVE_SIGNALS` | 2 | 2 consecutive evaluations |
| `MIN_NET_GAMMA` | 500000.0 |  |
| `STOP_PCT` | 0.005 | 0.5% stop |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MIN_STRIKES_WITH_DATA` | 5 | Need at least 5 strikes for distribution |
| `MIN_DATA_POINTS` | 5 | Need enough data for z-score calculation |
| `VOLUME_TREND_ALLOWED_LONG` | ["FLAT", "UP"] |  |
| `VOLUME_TREND_ALLOWED_SHORT` | ["FLAT", "DOWN"] |  |
| `CONTRIBUTION_THRESHOLD` | 0.05 | 5% of total momentum |

### `strategies/full_data/prob_weighted_magnet.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_OI_CONCENTRATION` | 2.0 | Minimum total OI at a strike |
| `CONSOLIDATION_RATIO` | 0.50 | 50% |
| `DELTA_ACCEL_RATIO` | 1.05 | 5% change in delta |
| `MIN_NET_GAMMA` | 500000.0 |  |
| `STOP_PCT` | 0.005 | 0.5% stop |
| `TARGET_RISK_MULT` | 1.5 | 1.5× risk for target (v1 fallback) |
| `MIN_CONFIDENCE` | 0.10 |  |
| `MIN_DATA_POINTS` | 3 |  |
| `VALID_VOLUME_TRENDS` | ("FLAT", "DOWN") |  |
| `DELTA_ROC_THRESHOLD` | 0.05 | 5% ROC for delta acceleration |
| `LIQUIDITY_VACUUM_RATIO` | 0.30 | bid/ask ratio for vacuum check |
| `GAMMA_SCALE_BASE` | 2.0 | gamma value for 2.0× target scaling |
| `TARGET_MULT_CAP` | 3.0 | max target multiplier |
| `TARGET_MIN_PCT` | 0.005 | minimum 0.5% target |

### `strategies/full_data/sentiment_sync.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/full_data/skew_dynamics.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/full_data/smile_dynamics.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

### `strategies/full_data/whale_tracker.py`

| Parameter | Value | Comment |
|-----------|-------|---------|
| `MIN_CONFIDENCE` | 0.10 |  |

