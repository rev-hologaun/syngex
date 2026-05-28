# TAIL_RISK (Delta-IV Divergence) — Why It's Not Firing

**Date:** 2026-05-22  
**Strategy:** `strategies/layer2/delta_iv_divergence.py` (DeltaIVDivergence)  
**Status:** No signals fired — multiple gates are bottlenecks

---

## Root Cause Summary

The strategy has **6 sequential hard gates** plus a no-op confidence floor. The bottleneck is primarily the **decoupling gate** (gate 5), which has a **logic bug with negative mean correlation** and is **extremely strict with positive correlations**. Combined with the **strict trend detection** (z > 0.8) and **joint z-score requirement** (both delta and IV must be simultaneously extreme), the strategy is nearly impossible to trigger in normal market conditions.

---

## Gate-by-Gate Analysis

### Gate 1: Data Availability — ✅ PASSING
- **Line 146-150** in `delta_iv_divergence.py`
- Requires `KEY_ATM_DELTA_5M` and `KEY_ATM_IV_5M` windows with ≥ 3 points each.
- **Data pipeline verified**: Both keys are pushed every tick in `main.py` (lines 1370, 1386).
- **Data pipeline verified**: `KEY_OTM_DELTA_5M` (line 1518), `KEY_DELTA_IV_CORR_5M` (line 1561), and `KEY_GAMMA_DENSITY_5M` (line 1633) are all properly pushed.
- **Conclusion:** Not a bottleneck. Data flows correctly.

### Gate 2: Trend Alignment — ⚠️ BOTTLENECK (Medium-High Confidence)
- **Line 154-162** in `delta_iv_divergence.py`
- Requires `delta_window.trend == "UP"` AND `iv_window.trend == "DOWN"` (for LONG), or reversed for SHORT.
- **Trend detection** in `rolling_window.py` (lines 171-196) uses a **z-score threshold of 0.8** to enter a trend:
  ```python
  _trend_z_threshold: float = 0.8       # line 47
  ```
- **Problem:** z > 0.8 is very strict for noisy delta/IV data. Delta values (typically -0.5 to +0.5) and IV values (typically 10-50) are noisy tick-to-tick. The half-window comparison (`first_half` vs `second_half`) with z > 0.8 means the second half must be 0.8 standard deviations above the first half.
- **Hysteresis adds lag:** Once in a trend, it takes z < 0.3 to exit, but entering requires z > 0.8. This creates a wide "dead zone" where the trend stays FLAT.
- **Impact:** Most ticks will have `trend == "FLAT"` for both delta and IV, causing early return at line 160/162.
- **Confidence: HIGH** — The z > 0.8 threshold is objectively strict for noisy financial data.

### Gate 3: Divergence Strength — ⚠️ BOTTLENECK (Medium Confidence)
- **Line 165-173** in `delta_iv_divergence.py`
- Formula: `min(delta_z, abs(iv_z)) / 2.0 >= 0.3`
- **Problem:** This requires **both** delta_z >= 0.6 **and** abs(iv_z) >= 0.6 simultaneously. This is a joint extreme event requirement.
  - delta_z = 0.7, iv_z = 0.3 → fails (iv too weak)
  - delta_z = 0.4, iv_z = 0.9 → fails (delta too weak)
- Combined with Gate 2 (trend already requires z > 0.8), this is a **double-threshold** problem. By the time trends are detected (z > 0.8), the z-scores are likely already > 0.6, but the trend detection itself is the harder filter.
- **Confidence: MEDIUM** — The formula is mathematically valid but compounds the trend detection problem.

### Gate 4: Skew Divergence — ⚠️ BOTTLENECK (Medium Confidence)
- **Line 304-335** in `delta_iv_divergence.py`
- Requires `skew_div > 0.10` with ≥ 6 data points in both OTM and ATM delta windows.
- **Problem 1:** Needs ≥ 6 data points (≈ 30 seconds of data). Combined with the warm-up for other gates, this adds latency.
- **Problem 2:** When ATM delta is very small (near 0), the ROC calculation becomes unstable:
  ```python
  atm_roc = (atm_current - atm_5_ago) / max(abs(atm_5_ago), 0.001)
  ```
  The floor of 0.001 can produce artificially large ROC values when ATM delta is genuinely small, making the skew_div unpredictable.
- **Problem 3:** The gate checks for *any* divergence between OTM and ATM delta ROC, but doesn't validate that the divergence direction aligns with the trade direction. This is a design gap, not a bug.
- **Confidence: MEDIUM** — The gate works in principle but adds another filter on already-strained data.

### Gate 5: Decoupling Coefficient — 🔴 CRITICAL BOTTLENECK (High Confidence)
- **Line 368-398** in `delta_iv_divergence.py`
- **BUG 1: Negative mean_corr inverts the gate logic.**
  ```python
  # Line 396:
  return current_corr < mean_corr * threshold  # threshold = 0.50
  ```
  When `mean_corr` is negative (correlations range from -1 to 1), this gate **inverts**:
  - Example: `mean_corr = -0.5`, `threshold = 0.5` → gate passes when `current_corr < -0.25`
  - This means `current_corr = 0.9` (strong positive correlation) **PASSES** the decoupling gate, which is the opposite of what decoupling should detect.
  - The gate should use **absolute values**: `abs(current_corr) < abs(mean_corr) * threshold`
  
- **BUG 2: Extremely strict with positive correlations.**
  - If `mean_corr = 0.7`, current must be `< 0.35` (50% drop). This is a rare event.
  - Delta-IV correlation is typically stable (0.3-0.8 range). A 50% drop from the rolling mean is an extreme event that may never occur in normal trading.
  
- **BUG 3: Rolling mean window includes the current value's predecessor but not the current value itself.**
  - Line 393: `mean_corr = statistics.mean(corr_vals[-(history + 1):-1])`
  - This excludes the current value from the mean, which is correct, but the window calculation `-(history + 1):-1` is off-by-one for the last element. When `corr_vals` has 31 elements and `history = 30`, this reads `corr_vals[-31:-1]` = indices 0-29 (30 values), excluding index 30 (current). This is correct but fragile.

- **Confidence: HIGH** — The negative mean_corr bug is a clear logic error. The strictness with positive correlations is a design issue that effectively blocks signals.

### Gate 6: Gamma Regime Filter — ⚠️ BOTTLENECK (Medium Confidence)
- **Line 420-452** in `delta_iv_divergence.py`
- Requires `current < mean_density * 0.70` (30% decline from rolling mean).
- **Problem 1:** The gate **pushes to the rolling window inside the check** (line 448):
  ```python
  gamma_window.push(gamma_density)
  ```
  This mutates state during evaluation. The mean is then computed **after** the push, so the current value is included in the mean. This biases the comparison — the mean is pulled toward the current value, making it harder to detect a decline.
  - Fix: Compute mean from historical data **before** pushing, or push to a separate tracking window.
  
- **Problem 2:** 30% decline threshold is strict for gamma density, which can be volatile. When gamma density is already low (near zero), even small fluctuations trigger the gate.

- **Problem 3:** `KEY_GAMMA_DENSITY_5M` is pushed in `main.py` (line 1633) AND in `_check_gamma_regime` (line 448). This means gamma density is pushed **twice per tick** — once in main, once in the strategy check. The second push adds a duplicate value to the rolling window, potentially skewing the mean.

- **Confidence: MEDIUM** — The double-push is a clear issue. The 30% threshold is strict but not broken.

### Gate 7: Confidence (MIN_CONFIDENCE = 0.0) — ⚠️ NO-OP (Medium Confidence)
- **Line 52** in `delta_iv_divergence.py`
- `MIN_CONFIDENCE = 0.0` means **every signal that passes the hard gates automatically passes this check**.
- This is inconsistent with other strategies (e.g., IV_GEX_DIV likely uses a non-zero threshold).
- **Confidence: MEDIUM** — Not a bug per se, but a design oversight. Should be ≥ 0.20 for consistency.

---

## Additional Issues

### Issue D: Confidence c5 Uses Cumulative net_gamma (Medium Confidence)
- **Line 573** in `delta_iv_divergence.py`:
  ```python
  c5 = normalize(abs(net_gamma), 0.0, 5000000.0)
  ```
- `net_gamma` is cumulative across the session, so c5 is always near 0.0 early in session and near 1.0 late in session. This makes c5 a **session duration proxy**, not a meaningful conviction signal.
- **Impact:** c5 contributes ~0.5 to the average confidence on average, inflating signals that should be lower-confidence.

### Issue E: Data Pipeline — ✅ VERIFIED OK
- All 5 required keys (`KEY_ATM_DELTA_5M`, `KEY_OTM_DELTA_5M`, `KEY_ATM_IV_5M`, `KEY_DELTA_IV_CORR_5M`, `KEY_GAMMA_DENSITY_5M`) are properly initialized in `ALL_KEYS` (rolling_keys.py) and pushed in `main.py`.
- Rolling windows are created with `window_type="time"` and default 300s window (line 411).
- **Conclusion:** Data pipeline is not a bottleneck.

---

## Recommended Fixes (Priority Order)

### Fix 1: Decoupling Gate — Negative Mean Bug (HIGH PRIORITY)
**File:** `delta_iv_divergence.py`, line 396

```python
# BEFORE:
return current_corr < mean_corr * threshold

# AFTER:
return abs(current_corr) < abs(mean_corr) * threshold
```

**Confidence: HIGH** — This is a clear logic bug. Negative correlations are valid (delta and IV can be negatively correlated), and the gate should detect correlation collapse regardless of sign.

### Fix 2: Decoupling Gate — Relax Threshold (HIGH PRIORITY)
**File:** `delta_iv_divergence.py`, line 66

```python
# BEFORE:
DECOUPLE_THRESHOLD = 0.50

# AFTER:
DECOUPLE_THRESHOLD = 0.70  # Allow 30% drop instead of 50%
```

**Confidence: MEDIUM** — A 30% drop from rolling mean is more achievable while still filtering noise. Should be tuned empirically.

### Fix 3: Gamma Regime — Fix Double-Push (MEDIUM PRIORITY)
**File:** `delta_iv_divergence.py`, lines 445-450

```python
# BEFORE:
gamma_window = rolling_data.get(KEY_GAMMA_DENSITY_5M)
if gamma_window is None:
    return False

gamma_window.push(gamma_density)  # ← pushes to shared window (already pushed in main.py)

if gamma_window.count < 3:
    return False

current = gamma_density
mean_density = gamma_window.mean or 0.0
```

```python
# AFTER: Use a local window for the check, or compute mean before push
gamma_window = rolling_data.get(KEY_GAMMA_DENSITY_5M)
if gamma_window is None:
    return False

if gamma_window.count < 3:
    return False

# Compute mean from existing data (before current push)
mean_density = gamma_window.mean or 0.0

# Only push if we're going to use this for other purposes
# gamma_window.push(gamma_density)  ← Remove or move to a separate tracking window

current = gamma_density
```

**Confidence: HIGH** — Double-push is a clear bug. The shared window is already being updated in main.py (line 1633).

### Fix 4: Trend Detection — Lower Z-Threshold (MEDIUM PRIORITY)
**File:** `rolling_window.py`, line 47

```python
# BEFORE:
_trend_z_threshold: float = 0.8

# AFTER:
_trend_z_threshold: float = 0.5
```

**Confidence: MEDIUM** — 0.5 is more appropriate for noisy financial data. The hysteresis (exit at 0.3) still prevents flip-flopping.

### Fix 5: Divergence Strength — Reduce Threshold (LOW PRIORITY)
**File:** `delta_iv_divergence.py`, line 50

```python
# BEFORE:
MIN_DIVERSION_STRENGTH = 0.3

# AFTER:
MIN_DIVERSION_STRENGTH = 0.2
```

**Confidence: LOW** — This is a design choice. Lowering to 0.2 requires both z-scores >= 0.4, which is more achievable.

### Fix 6: Confidence Floor — Set Non-Zero Threshold (LOW PRIORITY)
**File:** `delta_iv_divergence.py`, line 52

```python
# BEFORE:
MIN_CONFIDENCE = 0.0

# AFTER:
MIN_CONFIDENCE = 0.20
```

**Confidence: MEDIUM** — Consistent with other strategies. Prevents very low-confidence signals from passing.

---

## Summary of Bottlenecks

| Gate | Bottleneck? | Confidence | Severity |
|------|-------------|------------|----------|
| 1. Data Availability | No | — | N/A |
| 2. Trend Alignment | Yes | HIGH | High |
| 3. Divergence Strength | Yes | MEDIUM | Medium |
| 4. Skew Divergence | Yes | MEDIUM | Medium |
| 5. Decoupling | **CRITICAL** | HIGH | Critical |
| 6. Gamma Regime | Yes | MEDIUM | Medium |
| 7. Confidence | No-op | MEDIUM | Low |

**The single biggest fix is Gate 5 (decoupling)** — the negative mean_corr bug means the gate is fundamentally broken. Fixing this alone may not be enough, but it's the most impactful change.

**Recommended fix sequence:**
1. Fix Gate 5 negative mean bug (1-line change)
2. Fix Gate 6 double-push (1-line change)
3. Relax Gate 5 threshold (constant change)
4. Relax Gate 2 z-threshold (constant change)
5. Relax Gate 3 threshold (constant change)
6. Set non-zero MIN_CONFIDENCE (constant change)

After these fixes, run backtests to validate signal frequency and quality.
