# Gamma Flip Breakout — Strategy Review
**Date:** 2026-06-13  
**File:** `strategies/layer1/gamma_flip_breakout.py`  
**Status:** Did NOT produce signals during June 12 Syngex run (enabled in config)

---

## Executive Summary

The strategy **does use the correct normalized gamma field** (`net_gamma_normalized`) from the data dict, but suffers from **two threshold calibration bugs** that are almost certainly the root cause of zero signals. The `MIN_GAMMA_STRENGTH` constant is stale (leftover from old cumulative-gamma code) and creates a third, subtler issue in wall classification.

---

## Findings

### 🔴 CRITICAL — `evaluate()` early-exit threshold is calibrated on old cumulative gamma

**Location:** Line 90

```python
if abs(net_gamma) < 200000:
    return []
```

**Problem:** This gate checks `net_gamma_normalized` against `200000`. Based on actual gex_state data:

| Symbol | `net_gamma_normalized` | Passes? |
|--------|----------------------|---------|
| AAPL   | 39.2                 | ❌      |
| AMD    | 611.4                | ❌      |
| TSLA   | 216.9                | ❌      |
| INTC   | 2447.1               | ✅      |
| NVDA   | 3189.0               | ✅      |

Only **INTC and NVDA** pass this gate. AAPL, AMD, and TSLA are silently dropped before any signal logic runs. The value `200000` is clearly calibrated for **cumulative** `net_gamma` (which runs in the millions), not normalized gamma (which runs 0–3200).

**Suggested Fix:** Replace `200000` with a value appropriate for the normalized scale. Based on the data, `2000` (matching the `REGIME_GAMMA_THRESHOLD = 2000` used in `gex_imbalance.py`) would be a reasonable starting point. This allows ~75% of symbols to pass the gate.

---

### 🔴 CRITICAL — `get_wall_classifications()` threshold mismatch

**Location:** Line 224

```python
walls = gex_calc.get_wall_classifications(threshold=MIN_GAMMA_STRENGTH)
```

**Problem:** `MIN_GAMMA_STRENGTH = 100000` is passed as the `threshold` parameter to `get_wall_classifications()`. That method computes:

```python
gex = norm_net_gamma * 100 * price
if abs(gex) >= threshold:
```

So `threshold=100000` means `|norm_net_gamma * 100 * price| >= 100000`, i.e. `|norm_net_gamma| >= 100000 / price`.

- For a $150 stock: requires `|norm_net_gamma| >= 667` — only AMD (611) and above pass
- For a $25 stock: requires `|norm_net_gamma| >= 4000` — nothing passes (max is ~3189)
- For a $900 stock: requires `|norm_net_gamma| >= 111` — most pass

The constant `100000` is a **stale cumulative-gamma threshold** that has no semantic meaning on the normalized GEX scale. It should match the `threshold=1e6` default used by `get_wall_classifications()` in `gex_calculator.py`, or be removed entirely.

**Suggested Fix:** Either:
1. Remove `MIN_GAMMA_STRENGTH` and use the default `threshold=1e6` from `get_wall_classifications()`, or
2. Set `MIN_GAMMA_STRENGTH = 1e6` to match the canonical wall threshold used elsewhere.

---

### 🟡 HIGH — Confidence scoring uses wrong normalization ceiling

**Location:** Lines 206, 639, 650

```python
# _check_regime_confirmation():
gamma_score = min(1.0, abs(net_gamma) / 2000.0)

# _compute_confidence():
gamma_norm = min(1.0, abs(net_gamma) / 2000.0)
wall_norm = min(1.0, abs(net_gamma) / 2000.0)
```

**Problem:** The ceiling of `2000.0` is shared with `gex_imbalance.py`'s `REGIME_GAMMA_THRESHOLD = 2000`, which is reasonable for the normalized scale. However:

- **AAPL** (normalized γ = 39.2): gamma_norm = 0.02 → contributes almost nothing to confidence
- **AMD** (normalized γ = 611.4): gamma_norm = 0.31 → weak contribution
- **TSLA** (normalized γ = 216.9): gamma_norm = 0.11 → very weak
- **INTC** (normalized γ = 2447.1): gamma_norm = 1.0 → max
- **NVDA** (normalized γ = 3189.0): gamma_norm = 1.0 → max

For AAPL, TSLA, and AMD, gamma contributes almost nothing to confidence. This is **not necessarily wrong** (weak gamma = low confidence), but the `MIN_GAMMA_STRENGTH` wall filter (Finding #2) compounds the problem by potentially filtering out valid walls for these symbols.

**Suggested Fix:** Consider whether the 2000 ceiling is appropriate, or add a per-symbol calibration. Alternatively, the `MIN_GAMMA_STRENGTH` fix (Finding #2) would help by allowing more walls to be found for weaker-gamma symbols.

---

### 🟡 HIGH — Dead code path: unused `stop_mult` variables

**Location:** Lines 300, 308, 440, 515

```python
# _short_fade / _long_fade:
stop_mult = POSITIVE_GAMMA_STOP_MULT  # 0.75

# _long_breakout / _short_breakout:
stop_mult = NEGATIVE_GAMMA_STOP_MULT  # 2.5
```

**Problem:** `stop_mult` is assigned but **never used** in the stop calculation. The actual stop formulas use `STOP_OTHER_SIDE_PCT` and `ATR_MULT` directly:

```python
# _short_fade (line 302):
stop = max(price * (1 + stop_mult * STOP_OTHER_SIDE_PCT), ...)  # stop_mult IS used here
```

Wait — looking more carefully, `stop_mult` **is** used in `_short_fade` and `_long_fade` (lines 302, 310) but **NOT** in `_long_breakout` and `_short_breakout`:

```python
# _long_breakout (line 442):
stop = max(flip_mid * (1 - STOP_OTHER_SIDE_PCT), price * (1 - ATR_MULT * atr / price))
# stop_mult = NEGATIVE_GAMMA_STOP_MULT is assigned but never used!

# _short_breakout (line 517):
stop = min(flip_mid * (1 + STOP_OTHER_SIDE_PCT), price * (1 + ATR_MULT * atr / price))
# stop_mult = NEGATIVE_GAMMA_STOP_MULT is assigned but never used!
```

The `NEGATIVE_GAMMA_STOP_MULT = 2.5` is assigned in both breakout methods but never applied. The stop calculation uses `ATR_MULT * atr / price` instead, which is a different formula. The wider stops intended for negative gamma are not being applied.

**Suggested Fix:** Apply `stop_mult` consistently in breakout methods, e.g.:
```python
stop = max(flip_mid * (1 - STOP_OTHER_SIDE_PCT), price * (1 - stop_mult * ATR_MULT * atr / price))
```

---

### 🟢 MEDIUM — `MIN_GAMMA_STRENGTH` constant is stale dead code

**Location:** Line 48

```python
MIN_GAMMA_STRENGTH = 100000  # Minimum |net_gamma| for regime confidence
```

**Problem:** The comment says "Minimum |net_gamma|" but the constant is actually used as a threshold for `get_wall_classifications()`, not for regime confidence. The value `100000` has no semantic meaning on the normalized gamma scale. This is a leftover from when the strategy used cumulative `net_gamma`.

**Suggested Fix:** Either update the value to `1e6` (matching `gex_calculator.py` defaults) or remove the constant and use the default directly.

---

### 🟢 MEDIUM — No SYNGEX-specific data available

**Problem:** The gex_state data files are for AAPL, AMD, INTC, NVDA, TSLA — no SYNGEX symbol. If the June 12 run was for a different symbol, the thresholds may need symbol-specific calibration.

**Suggested Fix:** Verify which symbol(s) were active during the June 12 run and check if the thresholds apply.

---

### 🔵 LOW — Minor: `depth_score` parameter is dead code

**Location:** Line 587

```python
depth_score: Optional[float] = None,
```

The `depth_score` parameter is documented as a "Future (Phase 5)" addition but is never passed or used. Harmless dead code.

---

## Summary Table

| # | Severity | Issue | Impact |
|---|----------|-------|--------|
| 1 | 🔴 CRITICAL | `evaluate()` gate: `abs(net_gamma) < 200000` on normalized gamma | Blocks ~75% of symbols from any signal evaluation |
| 2 | 🔴 CRITICAL | `MIN_GAMMA_STRENGTH = 100000` stale threshold for wall classification | May filter out valid gamma walls, especially on low-price stocks |
| 3 | 🟡 HIGH | Confidence ceiling at 2000 under-weights weaker-gamma symbols | Low confidence for AAPL/TSLA/AMD even when they pass the gate |
| 4 | 🟡 HIGH | `NEGATIVE_GAMMA_STOP_MULT` assigned but never used in breakout methods | Stop calculations don't reflect intended wider stops for negative gamma |
| 5 | 🟢 MEDIUM | `MIN_GAMMA_STRENGTH` constant is stale/dead code | Code clarity issue, compounded by Finding #2 |
| 6 | 🟢 MEDIUM | No SYNGEX-specific data for threshold validation | Cannot confirm thresholds are appropriate for the target symbol |
| 7 | 🔵 LOW | `depth_score` parameter is dead code | Harmless, cosmetic |

---

## Suggested Fixes (Priority Order)

### Fix 1 — Replace `200000` gate threshold (CRITICAL)
```python
# Line 90: Change from
if abs(net_gamma) < 200000:
# To
if abs(net_gamma) < 2000:  # Match REGIME_GAMMA_THRESHOLD in gex_imbalance.py
```

### Fix 2 — Fix wall classification threshold (CRITICAL)
```python
# Line 48: Update constant
MIN_GAMMA_STRENGTH = 1e6  # Match gex_calculator.py default

# Or remove and use default:
# walls = gex_calc.get_wall_classifications()  # uses threshold=1e6
```

### Fix 3 — Apply `stop_mult` in breakout methods (HIGH)
```python
# _long_breakout / _short_breakout: use stop_mult in ATR calculation
stop = max(flip_mid * (1 - STOP_OTHER_SIDE_PCT), 
           price * (1 - stop_mult * ATR_MULT * atr / price))
```

### Fix 4 — Verify with actual June 12 run data
Check which symbol(s) were active and validate that the above fixes produce signals.

---

## Root Cause Conclusion

The strategy **did not fire because the `evaluate()` early-exit gate** (`abs(net_gamma) < 200000`) filters out nearly all symbols when `net_gamma` is the **normalized** value (0–3200 range). The value `200000` was calibrated for cumulative gamma (millions). This is a **copy-paste bug** from the old cumulative-gamma API era. The strategy correctly reads `net_gamma_normalized` from the data dict, but the threshold was never updated to match the new scale.

The wall classification threshold (`MIN_GAMMA_STRENGTH = 100000`) is a secondary issue that would cause problems even if Fix 1 is applied.
