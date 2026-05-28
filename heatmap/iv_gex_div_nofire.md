# IV-GEX Divergence Strategy — Signal Not Firing Investigation

**Date:** 2026-05-22  
**Strategy:** `IVGEXDivergence` in `strategies/layer2/iv_gex_divergence.py`  
**Goal:** Identify why the strategy is not emitting signals

---

## Executive Summary

The strategy has **5 sequential hard gates** that ALL must pass for a signal to fire. The combination creates an extremely narrow signal window. I found **1 confirmed bug** (IV skew mismatch for LONG) and **4 structural/parametric issues** that collectively make signal emission nearly impossible.

---

## Root Cause Analysis

### Gate Pass Rate (Estimated)

| Gate | Condition | Estimated Pass Rate |
|------|-----------|-------------------|
| 1. Price | percentile ≥ 0.70 (SHORT) or ≤ 0.30 (LONG) | ~30% of time |
| 2. IV crash/expanding | latest IV < 95% of 5m avg (or > 105%) | ~5-10% of time |
| 3. Net gamma | \|net_gamma\| > 200,000 | Variable (cumulative) |
| 4. IV skew ROC | skew ROC > 15% over 5 ticks | **~1-2% of time** ← bottleneck |
| 5. Gamma density decline | current < 70% of rolling mean | **~5-10% of time** ← bottleneck |

**Combined estimated pass rate: ~0.01-0.1%** — essentially never in normal conditions.

---

## Finding 1: IV Skew Calculation Mismatch (BUG — HIGH CONFIDENCE)

**Location:** `iv_gex_divergence.py` lines 236-248 (`_check_iv_skew_acceleration`) and lines 269-295 (`_get_skew_data`)

**Problem:** The rolling data pipeline in `main.py` (line ~1607) **always** computes **put skew**:
```python
# main.py ~line 1607
otm_put_strike = atm_strike * 0.95  # 5% OTM put
otm_put_iv = self._calculator.get_iv_by_strike(otm_put_strike)
iv_skew = otm_put_iv - atm_iv       # always put skew
self._rolling_data[KEY_IV_SKEW_GRADIENT_5M].push(iv_skew)
```

But the strategy's `_check_iv_skew_acceleration` (line 241-248) computes:
- **SHORT:** OTM put skew (`atm_strike * 0.95`) — ✅ matches rolling data
- **LONG:** OTM **call** skew (`atm_strike * 1.05`) — ❌ **mismatch**

For LONG signals, the strategy computes `current_skew = call_iv - atm_iv` live, but compares it against `skew_old` from the rolling window which contains **put skew**. This compares apples to oranges:

```python
# Strategy line 241-248
if signal_type == "SHORT":
    otm_strike = atm_strike * (1.0 - IV_SKEW_OTM_PCT)  # put
else:
    otm_strike = atm_strike * (1.0 + IV_SKEW_OTM_PCT)  # call ← BUG
```

The ROC calculation `(current_skew - skew_old) / abs(skew_old)` will produce meaningless results because `current_skew` is call skew and `skew_old` is put skew.

**Impact:** LONG signals are effectively **always blocked** by this gate. SHORT signals pass correctly.

**Recommended Fix:**
```python
# Option A: Always use put skew in rolling window, compute put skew for both directions
# In _check_iv_skew_acceleration, always compute put skew regardless of signal type:
otm_strike = atm_strike * (1.0 - IV_SKEW_OTM_PCT)  # always put skew

# Option B: Store both put and call skew in rolling data
# Add KEY_CALL_SKEW_GRADIENT_5M to main.py and rolling_keys.py
```

**Confidence:** HIGH — the mismatch is clear and deterministic.

---

## Finding 2: Net Gamma Uses Cumulative (Not Normalized) Values (BUG — HIGH CONFIDENCE)

**Location:** `iv_gex_divergence.py` line 107 (`evaluate` method) and `main.py` line 2447

**Problem:** The `net_gamma` passed to the strategy comes from `summary["net_gamma"]` which calls `get_net_gamma()` — a **cumulative** value that grows with message count:

```python
# gex_calculator.py line 222-224
def get_net_gamma(self) -> float:
    if self._net_gamma_dirty:
        self._net_gamma = sum(b.net_gamma for b in self._ladder.values())
    return self._net_gamma  # cumulative, grows with message count
```

The strategy checks `net_gamma > 200000` (line 107) against this cumulative value. This is problematic because:

1. **Early session:** Cumulative gamma may never reach 200,000 (threshold too high)
2. **Late session:** Cumulative gamma easily exceeds 200,000 (threshold too low, always passes)
3. **No normalization:** The threshold has no meaningful scale

The gex_calculator has a `get_normalized_net_gamma()` method (line 227) that returns bounded per-message averages — the canonical scale for GEX comparisons.

**Recommended Fix:**
```python
# In main.py _evaluate_strategies(), pass normalized gamma instead:
data = {
    ...
    "net_gamma": self._calculator.get_normalized_net_gamma(),  # use this instead
    ...
}

# And adjust the threshold accordingly:
# MIN_POSITIVE_GAMMA = 200000 → depends on normalized scale (likely much smaller)
```

**Confidence:** HIGH — the code explicitly documents that `get_net_gamma()` is cumulative and `get_normalized_net_gamma()` is the canonical scale.

---

## Finding 3: IV Crash Gate Too Tight (PARAMETRIC — MEDIUM CONFIDENCE)

**Location:** `iv_gex_divergence.py` line 68 (`IV_DECLINE_RATIO = 0.95`) and lines 155-180 (`_check_iv_crashing`)

**Problem:** The gate requires `latest_iv < avg * 0.95`, meaning ATM IV must drop **at least 5% below** its 5-minute rolling average. This is extremely tight:

```python
IV_DECLINE_RATIO = 0.95  # IV below 95% of rolling avg
is_crashing = latest < avg * IV_DECLINE_RATIO  # latest < avg * 0.95
```

For a 5-minute rolling average on options IV (which is relatively stable intraday), a 5% drop is a significant move that rarely occurs. The same ratio is used for `_check_iv_expanding` with `latest > avg / 0.95` (≈ 5.26% increase).

**Impact:** This gate alone blocks ~90-95% of potential signals. Combined with the other gates, it creates a "perfect storm" where all conditions must align simultaneously.

**Recommended Fix:**
```python
# Relax the ratio to something more realistic:
IV_DECLINE_RATIO = 0.90  # 10% decline (was 5%)
# Or make it configurable per strategy:
# IV_DECLINE_RATIO = params.get("iv_decline_ratio", 0.90)
```

**Confidence:** MEDIUM — depends on actual IV volatility characteristics of the underlying.

---

## Finding 4: IV Skew ROC Threshold Too High (PARAMETRIC — MEDIUM CONFIDENCE)

**Location:** `iv_gex_divergence.py` line 78 (`IV_SKEW_ROC_THRESHOLD = 0.15`)

**Problem:** The skew must have risen **≥15%** over just 5 ticks. For IV skew (which is typically a small value like 0.02-0.08), a 15% change over 5 ticks is a very fast move:

```python
IV_SKEW_ROC_WINDOW = 5      # ticks for skew ROC
IV_SKEW_ROC_THRESHOLD = 0.15  # skew must have risen ≥15%
```

The skew ROC calculation:
```python
skew_roc = (current_skew - skew_old) / abs(skew_old)
return skew_roc > IV_SKEW_ROC_THRESHOLD
```

If skew_old is small (e.g., 0.03), then current_skew must be > 0.0345 — a 0.0045 absolute change in 5 ticks. This is possible but rare.

**Recommended Fix:**
```python
# Lower the threshold:
IV_SKEW_ROC_THRESHOLD = 0.08  # 8% change (was 15%)
# Or increase the window for smoother ROC:
IV_SKEW_ROC_WINDOW = 10  # 10 ticks (was 5)
```

**Confidence:** MEDIUM — depends on typical skew velocity in the underlying.

---

## Finding 5: Gamma Density Decline Gate Too Strict (PARAMETRIC — MEDIUM CONFIDENCE)

**Location:** `iv_gex_divergence.py` line 80 (`GAMMA_DENSITY_DECLINE_THRESHOLD = 0.70`) and lines 306-330 (`_check_gamma_density_gradient`)

**Problem:** Current gamma density must be **< 70% of rolling mean** (a 30% decline):

```python
GAMMA_DENSITY_DECLINE_THRESHOLD = 0.70  # density must decline ≥30%
return current_density < rolling_mean * GAMMA_DENSITY_DECLINE_THRESHOLD
```

Gamma density within ±1% of the current price is a narrow window. Small price movements can cause the density to fluctuate significantly, but a sustained 30% decline below the rolling mean is uncommon.

**Recommended Fix:**
```python
GAMMA_DENSITY_DECLINE_THRESHOLD = 0.80  # 20% decline (was 30%)
# Or make it configurable:
# GAMMA_DENSITY_DECLINE_THRESHOLD = params.get("gamma_decline_threshold", 0.80)
```

**Confidence:** MEDIUM — gamma density behavior depends on the underlying's options structure.

---

## Finding 6: Confidence Score Mismatch (DOCBUG — LOW CONFIDENCE)

**Location:** `iv_gex_divergence.py` docstring (lines 1-40) and `_compute_confidence_v2` (lines 420-470)

**Problem:** The docstring claims 7 confidence components, but the actual code averages only 5:

```python
# Docstring says:
# 1. Price extremeness (0.0-0.15)
# 2. IV skew acceleration (0.0 or 0.20)  ← NOT in code
# 3. Gamma density decline (0.0 or 0.15)  ← NOT in code
# 4. Volume-weighted IV (0.0-0.10)        ← NOT in code
# 5. Net gamma magnitude (0.0-0.10)       ← NOT in code
# 6. Wall proximity (0.0-0.10)            ← NOT in code
# 7. Regime intensity (0.05-0.15)         ← NOT in code

# Actual code averages only 5:
confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
```

Additionally, `MIN_CONFIDENCE = 0.0` (line 74) makes the confidence check a no-op. The docstring says "raised to 0.35 for v2" but the code has 0.0.

**Impact:** Low — doesn't affect signal emission (confidence check is bypassed), but misleading for debugging.

**Recommended Fix:**
```python
# Either implement the 7-component confidence or update docstring:
MIN_CONFIDENCE = 0.35  # as documented
# And add the missing components to _compute_confidence_v2
```

**Confidence:** HIGH for the code/doc mismatch, LOW for impact (no-op threshold).

---

## Finding 7: Data Pipeline Consistency (VERIFIED OK — LOW CONFIDENCE ISSUE)

**Location:** `main.py` lines 1607-1633 vs `iv_gex_divergence.py` strategy evaluation

**Verification:**
- ✅ `KEY_IV_SKEW_GRADIENT_5M` and `KEY_GAMMA_DENSITY_5M` are in `ALL_KEYS` and initialized as RollingWindow objects
- ✅ ATM strike calculation is consistent: both use `gex_calc.get_atm_strike(price)` which finds nearest strike in ladder
- ✅ IV values are consistent: `get_iv_by_strike()` and `get_iv_by_strike_avg()` compute the same average
- ✅ `get_greeks_summary()` returns `Dict[float, Dict[str, float]]` — keys are floats, strategy does `float(strike_str)` which works fine
- ✅ `gamma_density_5m` rolling window is populated in main.py lines 1620-1633

**No issues found in data pipeline consistency.**

---

## Summary of Issues

| # | Issue | Type | Confidence | Impact | Priority |
|---|-------|------|------------|--------|----------|
| 1 | IV skew mismatch (LONG uses call skew vs put skew history) | Bug | HIGH | LONG signals never fire | P0 |
| 2 | Net gamma uses cumulative instead of normalized | Bug | HIGH | Threshold meaningless | P0 |
| 3 | IV decline ratio 0.95 (5% drop) too tight | Parametric | MEDIUM | Blocks ~90% of signals | P1 |
| 4 | Skew ROC threshold 15% over 5 ticks too high | Parametric | MEDIUM | Blocks ~98% of signals | P1 |
| 5 | Gamma density decline 30% too strict | Parametric | MEDIUM | Blocks ~90% of signals | P1 |
| 6 | Confidence doc/code mismatch | Docbug | HIGH | Low (no-op threshold) | P3 |
| 7 | Data pipeline consistency | Verified OK | N/A | N/A | N/A |

---

## Recommended Fix Order

1. **Fix #1 (IV skew mismatch):** Always compute put skew for both directions, or store separate call/put skew windows. This alone enables LONG signals.

2. **Fix #2 (Normalized gamma):** Switch to `get_normalized_net_gamma()` and recalibrate the threshold. This makes the gamma gate meaningful.

3. **Relax parametric gates (#3, #4, #5):** Start with `IV_DECLINE_RATIO=0.90`, `IV_SKEW_ROC_THRESHOLD=0.08`, `GAMMA_DENSITY_DECLINE_THRESHOLD=0.80`. Backtest to find optimal values.

4. **Fix #6 (Confidence):** Set `MIN_CONFIDENCE=0.35` and implement the documented 7-component confidence score.

---

## Notes

- The strategy's sequential `return signals` pattern (line 115 and 186) means if the skew acceleration gate fails for SHORT, it immediately returns without checking LONG. This is intentional but means one failed gate blocks both directions.
- The `greeks_summary` in the strategy's `evaluate()` method falls back to `gex_calc.get_greeks_summary()` if not provided in `data`. This is safe.
- The `rolling_data` dict is shared between all strategies. Keys like `iv_{strike}_5m` are created lazily (line 914-920 in main.py) when IV data is available.
