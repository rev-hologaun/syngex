# Configuration Constants Consolidation - Summary

## Issue #7: Consolidate Configuration Constants in Syngex Files

### Overview
This document summarizes the audit and refactoring of hardcoded configuration constants across all Syngex strategy files.

## ✅ Completed Work

### 1. Audit Document Created
- **File:** `/home/hologaun/projects/syngex/HARDCODED_CONSTANTS_AUDIT.md`
- Contains complete inventory of all hardcoded constants by strategy
- Maps each constant to its config key name

### 2. Sample Strategy Refactored: `gamma_wall_bounce.py`
**Changes Made:**
- Replaced class-level constants with `DEFAULT_*` fallback constants
- Added `_apply_params(data)` call at start of `evaluate()`
- Extract params using `self._params.get('key', DEFAULT_VALUE)` pattern
- Updated all internal references to use config-driven values

**Pattern Applied:**
```python
def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
    # Apply config params from data dict
    self._apply_params(data)
    
    # Extract params with fallback defaults
    wall_proximity_pct = self._params.get('wall_proximity_pct', DEFAULT_WALL_PROXIMITY_PCT)
    stop_past_wall_pct = self._params.get('stop_past_wall_pct', DEFAULT_STOP_PAST_WALL_PCT)
    # ... etc
```

## 📋 Strategies Requiring Refactoring

### Layer 1 (7 remaining)
1. ✅ `gamma_wall_bounce.py` - **COMPLETED**
2. ⏳ `confluence_reversal.py` - 6 constants
3. ⏳ `gamma_flip_breakout.py` - 6 constants
4. ⏳ `gamma_squeeze.py` - (check for constants)
5. ⏳ `gex_imbalance.py` - 8 constants
6. ⏳ `magnet_accelerate.py` - 7 constants
7. ⏳ `vol_compression_range.py` - 7 constants
8. ⏳ `gex_divergence.py` - 8 constants

### Layer 2 (5 strategies)
1. ⏳ `call_put_flow_asymmetry.py` - 6 constants (some already in config)
2. ⏳ `delta_iv_divergence.py` - 5 constants
3. ⏳ `delta_volume_exhaustion.py` - 8 constants
4. ⏳ `iv_gex_divergence.py` - 9 constants
5. ⏳ `delta_gamma_squeeze.py` - (check for constants)

### Layer 3 (4 strategies)
1. ⏳ `gamma_volume_convergence.py` - 11 constants
2. ⏳ `iv_band_breakout.py` - 10 constants
3. ⏳ `strike_concentration.py` - 11 constants
4. ⏳ `theta_burn.py` - (check for constants)

### Full Data (4 strategies)
1. ⏳ `extrinsic_intrinsic_flow.py` - 12 constants
2. ⏳ `iv_skew_squeeze.py` - 11 constants
3. ⏳ `prob_distribution_shift.py` - 12 constants
4. ⏳ `prob_weighted_magnet.py` - 10 constants

## 📝 Required Config Updates (strategies.yaml)

### Layer 1 Parameters to Add

#### confluence_reversal
```yaml
confluence_reversal:
  params:
    confluence_distance_pct: 0.003     # Max distance for confluence
    min_structural_signals: 1          # Wall-level confluence alone is valid
    max_confidence_base: 0.6           # Base confidence for score 3
    min_confidence: 0.35               # Minimum confidence to emit signal
    stop_pct: 0.008                    # 0.8% stop
    target_risk_mult: 2.0              # 2× risk for target
```

#### gamma_flip_breakout
```yaml
gamma_flip_breakout:
  params:
    flip_proximity_pct: 0.025          # 2.5% — price must be within this of flip
    stop_other_side_pct: 0.01          # 1% — stop on other side of flip
    atr_mult: 1.5                       # Already in config
    target_rr: 2.5                      # 1:2.5 risk-reward minimum
    min_confidence: 0.35
    min_gamma_strength: 500000         # Minimum |net_gamma| for regime confidence
```

#### gex_imbalance
```yaml
gex_imbalance:
  params:
    put_heavy_threshold: 0.5           # < 0.5 → long bias
    call_heavy_threshold: 0.65         # > 0.65 → short bias
    strong_put_ratio: 0.25             # very strong long signal
    strong_call_ratio: 0.75            # very strong short signal
    min_messages: 20                   # minimum data points for signal quality
    stop_vol_mult: 2.5                 # stop = 2.5x rolling price std dev
    target_risk_mult: 1.5
    min_confidence: 0.35
```

#### magnet_accelerate
```yaml
magnet_accelerate:
  params:
    min_magnet_gex: 500000             # Minimum |normalized GEX| to be a magnet
    magnet_exit_pct: 0.003             # 0.3% — exit within this % of magnet
    breakout_pct: 0.002                # 0.2% — price must be this far past magnet
    max_breakout_pct: 0.02             # 2% — max distance past magnet (no chasing)
    trail_stop_pct: 0.01               # 1% — trailing stop for Phase 2
    target_risk_mult: 1.5
    min_confidence: 0.35
```

#### vol_compression_range
```yaml
vol_compression_range:
  params:
    compression_pct: 0.003             # 0.3% max range for compression
    min_range_bars: 20                 # Minimum data points in rolling window
    wall_edge_proximity: 0.004         # 0.4% from wall for edge trade
    min_confidence: 0.35
    stop_pct: 0.006                    # 0.6% stop (wider for scalping)
    target_risk_mult: 1.5
    std_threshold: 0.002               # Max std of price for compression
```

#### gex_divergence
```yaml
gex_divergence:
  params:
    divergence_min_slope: 0.0005       # Minimum slope magnitude (0.05%)
    divergence_window: 30              # Number of points for slope calculation
    confirmation_candle_pct: 0.002     # 0.2% candle for confirmation
    min_confidence: 0.35
    stop_pct: 0.005                    # 0.5% stop
    target_risk_mult: 1.5
    min_data_points: 15                # Minimum data points for slope calculation
    min_total_gex: 1000000.0           # 1M — minimum GEX wall strength
```

### Layer 2 Parameters to Add

#### call_put_flow_asymmetry
```yaml
call_put_flow_asymmetry:
  params:
    flow_threshold: 1.5                # Already in config
    min_greeks_points: 3               # Minimum greeks data points
    iv_skew_threshold: 0.03            # Already in config
    min_confidence: 0.35
    stop_pct: 0.006                    # Already in config
    target_risk_mult: 2.0              # Already in config
```

#### delta_iv_divergence
```yaml
delta_iv_divergence:
  params:
    min_data_points: 5
    min_diversion_strength: 0.3
    min_confidence: 0.35
    stop_pct: 0.008
    target_risk_mult: 2.0
```

#### delta_volume_exhaustion
```yaml
delta_volume_exhaustion:
  params:
    min_trend_points: 5
    min_greeks_points: 5
    delta_decline_ratio: 0.95          # Delta below 95% of rolling avg
    volume_decline_ratio: 0.90         # Volume below 90% of rolling avg
    min_trend_duration: 2              # At least 2 candles in trend
    stop_pct: 0.008                    # Already in config
    min_confidence: 0.25
    mean_reversion_mult: 1.0           # 1.0× distance — target is the rolling mean
```

#### iv_gex_divergence
```yaml
iv_gex_divergence:
  params:
    price_percentile_threshold: 0.70   # p70 — price in top 30% of range
    min_price_points: 10
    min_iv_points: 5
    min_positive_gamma: 200000         # $200k net gamma
    iv_decline_ratio: 0.95             # IV below 95% of rolling avg
    stop_pct: 0.006                    # Already in config
    target_risk_mult: 1.5              # Already in config
    min_confidence: 0.25
    max_confidence: 0.95
```

### Layer 3 Parameters to Add

#### gamma_volume_convergence
```yaml
gamma_volume_convergence:
  params:
    delta_accel_ratio: 1.10            # Already in config
    delta_accel_min_ratio: 0.30
    gamma_spike_ratio: 1.15            # Already in config
    volume_spike_ratio: 1.15           # Already in config
    stop_pct: 0.005                    # Already in config
    target_pct: 0.010                  # Already in config
    min_confidence: 0.25
    max_confidence: 0.90               # Already in config
    min_data_points: 3                 # Already in config
    price_up_threshold: 0.001          # 0.1% rise over 5m window
    price_down_threshold: -0.001       # 0.1% drop over 5m window
```

#### iv_band_breakout
```yaml
iv_band_breakout:
  params:
    delta_decel_ratio: 0.95            # Delta must be below rolling avg
    price_compression_ratio: 0.40      # Already in config
    breakout_move_pct: 0.0005
    volume_trend_required: true
    stop_pct: 0.005                    # Already in config
    target_pct: 0.010                  # Already in config
    min_confidence: 0.25
    max_confidence: 0.85               # Already in config
    min_data_points: 5                 # Already in config
    min_iv_data_points: 3
```

#### strike_concentration
```yaml
strike_concentration:
  params:
    top_oi_strikes_count: 3            # Already in config
    bounce_proximity_pct: 0.005        # 0.5%
    slice_body_ratio: 0.3              # 30% body
    slice_volume_ratio: 1.20           # 20% above rolling avg
    divergence_volume_threshold: 0.80  # Volume < 80% of avg = declining
    stop_pct_bounce: 0.003             # 0.3% beyond the strike for bounces
    stop_pct_slice: 0.003              # 0.3% against entry for slices
    target_risk_mult: 1.5
    min_confidence: 0.25
    max_confidence: 0.85
    min_data_points: 3                 # Already in config
```

### Full Data Parameters to Add

#### extrinsic_intrinsic_flow
```yaml
extrinsic_intrinsic_flow:
  params:
    extrinsic_expansion_threshold: 0.03    # 3% expansion
    extrinsic_collapse_threshold: 0.10     # 10% collapse
    volume_spike_ratio: 1.30               # 130% of avg (1.3×)
    min_net_gamma: 500000.0
    stop_pct: 0.005                        # Already in config
    target_pct: 0.008                      # Already in config
    min_confidence: 0.25
    max_confidence: 0.80                   # Already in config
    min_data_points: 5                     # Already in config
    valid_volume_trend_long: ["UP"]
    valid_volume_trend_short: ["DOWN"]
    valid_volume_trend_fade: ["DOWN", "FLAT"]
```

#### iv_skew_squeeze
```yaml
iv_skew_squeeze:
  params:
    skew_extreme_positive: 0.20            # Calls 20%+ more expensive (euphoria)
    skew_extreme_negative: -0.07           # Puts 7%+ more expensive (panic)
    price_stable_threshold: 0.005          # Already in config
    min_net_gamma: 500000.0
    stop_pct: 0.005                        # Already in config
    target_pct: 0.008                      # Already in config
    min_confidence: 0.25
    max_confidence: 0.80                   # Already in config
    min_data_points: 5                     # Already in config
    min_skew_data_points: 5
    volume_spike_threshold: 1.5            # Volume > 1.5× avg = spike
```

#### prob_distribution_shift
```yaml
prob_distribution_shift:
  params:
    z_score_threshold: 1.5                 # 1.5 standard deviations
    min_consecutive_signals: 2             # 2 consecutive evaluations
    min_net_gamma: 500000.0
    stop_pct: 0.005                        # Already in config
    target_pct: 0.008                      # Already in config
    min_confidence: 0.25
    max_confidence: 0.80                   # Already in config
    min_strikes_with_data: 5               # Already in config
    min_data_points: 5                     # Already in config
    volume_trend_allowed_long: ["FLAT", "UP"]
    volume_trend_allowed_short: ["FLAT", "DOWN"]
    contribution_threshold: 0.05           # 5% of total momentum
```

#### prob_weighted_magnet
```yaml
prob_weighted_magnet:
  params:
    min_oi_concentration: 2.0              # Minimum total OI at a strike
    consolidation_ratio: 0.50              # 50%
    delta_accel_ratio: 1.05                # 5% change in delta
    min_net_gamma: 500000.0
    stop_pct: 0.005                        # Already in config
    target_risk_mult: 1.5                  # Already in config
    min_confidence: 0.25
    max_confidence: 0.80                   # Already in config
    min_data_points: 3                     # Already in config
    valid_volume_trends: ["FLAT", "DOWN"]
```

## 🔧 Implementation Pattern

All strategies should follow this pattern:

```python
# At top of file - Default fallback constants
DEFAULT_CONSTANT_NAME = value  # Used ONLY if config is missing

class MyStrategy(BaseStrategy):
    strategy_id = "my_strategy"
    layer = "layer1"
    
    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        # 1. Apply config params from data dict
        self._apply_params(data)
        
        # 2. Extract params with fallback defaults
        param1 = self._params.get('param1', DEFAULT_PARAM1)
        param2 = self._params.get('param2', DEFAULT_PARAM2)
        
        # 3. Use param1, param2 throughout the method
        # ...
```

## ✅ Verification Steps

After all refactoring:
1. Run `python3 -m py_compile` on all modified strategy files
2. Verify no hardcoded constant references remain (except DEFAULT_*)
3. Test that strategies load and evaluate without errors
4. Confirm config values override defaults correctly

## Status

- **Audit Complete:** ✅ All hardcoded constants documented
- **Sample Refactoring:** ✅ `gamma_wall_bounce.py` refactored as template
- **Config Updates:** ⏳ Pending - strategies.yaml needs all missing parameters
- **Remaining Strategies:** ⏳ 24 strategies need refactoring

---

*Generated: 2026-05-19*
*Issue: #7 - Consolidate Configuration Constants in Syngex Files*
