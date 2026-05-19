# Layer 1 Strategy Constants Refactoring Summary

## Issue #7a: Audit and Fix Layer 1 Strategy Constants

### Overview
Refactored hardcoded configuration constants in Layer 1 strategy files to use the `self._params.get()` pattern with documented DEFAULT_* fallback values. This allows configuration via `config/strategies.yaml` while maintaining safe defaults.

### Files Modified

#### 1. **magnet_accelerate.py** ✅
**Constants Refactored:**
- `MIN_MAGNET_GEX` → `DEFAULT_MIN_MAGNET_GEX` (500000)
- `MAGNET_EXIT_PCT` → `DEFAULT_MAGNET_EXIT_PCT` (0.003)
- `BREAKOUT_PCT` → `DEFAULT_BREAKOUT_PCT` (0.002)
- `MAX_BREAKOUT_PCT` → `DEFAULT_MAX_BREAKOUT_PCT` (0.02)
- `TRAIL_STOP_PCT` → `DEFAULT_TRAIL_STOP_PCT` (0.01)
- `TARGET_RISK_MULT` → `DEFAULT_TARGET_RISK_MULT` (1.5)
- `MIN_CONFIDENCE` → `DEFAULT_MIN_CONFIDENCE` (0.65)

**Changes:**
- Added `self._apply_params(data)` call in `evaluate()`
- Extract params with fallback defaults at the start of `evaluate()`
- Updated `_phase1_pull()` and `_phase2_accelerate()` to accept param values as arguments

---

#### 2. **gamma_flip_breakout.py** ✅
**Constants Refactored:**
- `FLIP_PROXIMITY_PCT` → `DEFAULT_FLIP_PROXIMITY_PCT` (0.025)
- `STOP_OTHER_SIDE_PCT` → `DEFAULT_STOP_OTHER_SIDE_PCT` (0.01)
- `ATR_MULT` → `DEFAULT_ATR_MULT` (1.5)
- `TARGET_RR` → `DEFAULT_TARGET_RR` (2.5)
- `MIN_CONFIDENCE` → `DEFAULT_MIN_CONFIDENCE` (0.65)
- `MIN_GAMMA_STRENGTH` → `DEFAULT_MIN_GAMMA_STRENGTH` (500000)

**Changes:**
- Added `self._apply_params(data)` call in `evaluate()`
- Extract all params with fallback defaults
- Updated `_fade_above_flip()`, `_short_fade()`, `_long_fade()`, `_breakout_below_flip()`, `_long_breakout()`, and `_short_breakout()` to accept param values

---

#### 3. **gex_imbalance.py** ✅
**Constants Refactored:**
- `PUT_HEAVY_RATIO` → `DEFAULT_PUT_HEAVY_RATIO` (0.5)
- `CALL_HEAVY_RATIO` → `DEFAULT_CALL_HEAVY_RATIO` (0.65)
- `STRONG_PUT_RATIO` → `DEFAULT_STRONG_PUT_RATIO` (0.25)
- `STRONG_CALL_RATIO` → `DEFAULT_STRONG_CALL_RATIO` (0.75)
- `MIN_MESSAGES` → `DEFAULT_MIN_MESSAGES` (20)
- `STOP_VOL_MULT` → `DEFAULT_STOP_VOL_MULT` (2.5)
- `TARGET_RISK_MULT` → `DEFAULT_TARGET_RISK_MULT` (1.5)
- `MIN_CONFIDENCE` → `DEFAULT_MIN_CONFIDENCE` (0.55)

**Changes:**
- Added `self._apply_params(data)` call in `evaluate()`
- Extract all params with fallback defaults
- Updated `_classify_bias()` to accept ratio thresholds as arguments
- Updated `_compute_confidence()` to accept ratio thresholds as arguments

---

#### 4. **confluence_reversal.py** ✅
**Constants Refactored:**
- `CONFLUENCE_DISTANCE_PCT` → `DEFAULT_CONFLUENCE_DISTANCE_PCT` (0.003)
- `MIN_STRUCTURAL_SIGNALS` → `DEFAULT_MIN_STRUCTURAL_SIGNALS` (1)
- `MAX_CONFIDENCE_BASE` → `DEFAULT_MAX_CONFIDENCE_BASE` (0.6)
- `MIN_CONFIDENCE` → `DEFAULT_MIN_CONFIDENCE` (0.65)
- `STOP_PCT` → `DEFAULT_STOP_PCT` (0.008)
- `TARGET_RISK_MULT` → `DEFAULT_TARGET_RISK_MULT` (2.0)

**Changes:**
- Added `self._apply_params(data)` call in `evaluate()`
- Extract all params with fallback defaults
- Updated `_find_confluence_levels()` to accept `confluence_distance_pct` and `min_structural_signals`
- Updated `_build_short_signal()` and `_build_long_signal()` to accept `stop_pct`, `target_risk_mult`, and `min_confidence`

---

#### 5. **vol_compression_range.py** ✅
**Constants Refactored:**
- `COMPRESSION_PCT` → `DEFAULT_COMPRESSION_PCT` (0.003)
- `MIN_RANGE_BARS` → `DEFAULT_MIN_RANGE_BARS` (20)
- `WALL_EDGE_PROXIMITY` → `DEFAULT_WALL_EDGE_PROXIMITY` (0.004)
- `MIN_CONFIDENCE` → `DEFAULT_MIN_CONFIDENCE` (0.45)
- `STOP_PCT` → `DEFAULT_STOP_PCT` (0.006)
- `TARGET_RISK_MULT` → `DEFAULT_TARGET_RISK_MULT` (1.5)
- `STD_THRESHOLD` → `DEFAULT_STD_THRESHOLD` (0.002)

**Changes:**
- Added `self._apply_params(data)` call in `evaluate()`
- Extract all params with fallback defaults
- Updated `_check_compression()` to accept `compression_pct` and `std_threshold`
- Updated `_check_upper_edge()` and `_check_lower_edge()` to accept all relevant params

---

#### 6. **gex_divergence.py** ✅
**Constants Refactored:**
- `DIVERGENCE_MIN_SLOPE` → `DEFAULT_DIVERGENCE_MIN_SLOPE` (0.0005)
- `DIVERGENCE_WINDOW` → `DEFAULT_DIVERGENCE_WINDOW` (30)
- `CONFIRMATION_CANDLE_PCT` → `DEFAULT_CONFIRMATION_CANDLE_PCT` (0.002)
- `MIN_CONFIDENCE` → `DEFAULT_MIN_CONFIDENCE` (0.25)
- `STOP_PCT` → `DEFAULT_STOP_PCT` (0.005)
- `TARGET_RISK_MULT` → `DEFAULT_TARGET_RISK_MULT` (1.5)
- `MIN_DATA_POINTS` → `DEFAULT_MIN_DATA_POINTS` (15)
- `MIN_TOTAL_GEX` → `DEFAULT_MIN_TOTAL_GEX` (1000000.0)

**Changes:**
- Added `self._apply_params(data)` call in `evaluate()`
- Extract all params with fallback defaults
- Updated `_check_confirmation()` to accept `confirmation_candle_pct`
- Updated `_get_gamma_window()` to use `min_data_points` parameter

---

### Files Already Compliant (No Changes Needed)

#### **gamma_wall_bounce.py** ✅
Already uses the correct pattern with `DEFAULT_*` constants and `self._params.get()` calls.

#### **gamma_squeeze.py** ✅
Already imports all constants from `config.parameters` module.

---

### Pattern Applied

**Before:**
```python
class MyStrategy(BaseStrategy):
    MIN_CONFIDENCE = 0.55
    TARGET_RISK_MULT = 1.5
    
    def evaluate(self, data):
        if confidence < self.MIN_CONFIDENCE:
            return None
```

**After:**
```python
# Default Fallback Constants
DEFAULT_MIN_CONFIDENCE = 0.55
DEFAULT_TARGET_RISK_MULT = 1.5

class MyStrategy(BaseStrategy):
    def evaluate(self, data):
        # Apply config params from data dict
        self._apply_params(data)
        
        # Extract params with fallback defaults
        min_confidence = self._params.get('min_confidence', DEFAULT_MIN_CONFIDENCE)
        target_risk_mult = self._params.get('target_risk_mult', DEFAULT_TARGET_RISK_MULT)
        
        if confidence < min_confidence:
            return None
```

---

### Configuration Example (strategies.yaml)

```yaml
layer1:
  magnet_accelerate:
    params:
      min_magnet_gex: 500000
      magnet_exit_pct: 0.003
      breakout_pct: 0.002
      max_breakout_pct: 0.02
      trail_stop_pct: 0.01
      target_risk_mult: 1.5
      min_confidence: 0.65
  
  gamma_flip_breakout:
    params:
      flip_proximity_pct: 0.025
      stop_other_side_pct: 0.01
      atr_mult: 1.5
      target_rr: 2.5
      min_confidence: 0.65
      min_gamma_strength: 500000
  
  gex_imbalance:
    params:
      put_heavy_ratio: 0.5
      call_heavy_ratio: 0.65
      strong_put_ratio: 0.25
      strong_call_ratio: 0.75
      min_messages: 20
      stop_vol_mult: 2.5
      target_risk_mult: 1.5
      min_confidence: 0.55
  
  confluence_reversal:
    params:
      confluence_distance_pct: 0.003
      min_structural_signals: 1
      max_confidence_base: 0.6
      min_confidence: 0.65
      stop_pct: 0.008
      target_risk_mult: 2.0
  
  vol_compression_range:
    params:
      compression_pct: 0.003
      min_range_bars: 20
      wall_edge_proximity: 0.004
      min_confidence: 0.45
      stop_pct: 0.006
      target_risk_mult: 1.5
      std_threshold: 0.002
  
  gex_divergence:
    params:
      divergence_min_slope: 0.0005
      divergence_window: 30
      confirmation_candle_pct: 0.002
      min_confidence: 0.25
      stop_pct: 0.005
      target_risk_mult: 1.5
      min_data_points: 15
      min_total_gex: 1000000.0
```

---

### Verification

All modified files passed syntax validation:
```bash
python3 -m py_compile strategies/layer1/magnet_accelerate.py
python3 -m py_compile strategies/layer1/gamma_flip_breakout.py
python3 -m py_compile strategies/layer1/gex_imbalance.py
python3 -m py_compile strategies/layer1/confluence_reversal.py
python3 -m py_compile strategies/layer1/vol_compression_range.py
python3 -m py_compile strategies/layer1/gex_divergence.py
```

**Result:** ✅ All files compiled successfully

---

### Next Steps

1. Update `config/strategies.yaml` with the parameter structure shown above
2. Test each strategy to ensure config overrides work correctly
3. Document any strategy-specific parameter requirements
4. Consider adding parameter validation in the base strategy class
