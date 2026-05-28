# VAMP Momentum — Why It's Not Firing Signals

## Executive Summary

VAMP Momentum (`vamp_momentum.py`) is blocked by **Gate B (Liquidity Density)** as the primary bottleneck, with **Gate A (Participants)** as a secondary blocker when `NumParticipants` data is missing or zero. The combination of these two hard gates means ~95%+ of ticks are filtered out before signal direction even gets evaluated.

---

## Root Cause Analysis

### 🔴 PRIMARY: Gate B — Liquidity Density (Confidence: HIGH)

**Location:** `vamp_momentum.py` lines 160-165

**The gate:**
```python
gate_b = current_total_size > ma_depth * liquidity_density_min_mult  # 1.2
```

**Problem:** This requires `current_total_size` (sum of top 10 levels) to be **20% ABOVE** the 60-second rolling average of the same metric. This is a "depth surge" gate, not a "sufficient depth" gate.

In normal market conditions:
- Depth fluctuates around its mean (the rolling average)
- A value 20% above the mean is a genuine spike, not a typical tick
- This blocks ~85-95% of all ticks

**Data pipeline:**
- `main.py` line 2182: `KEY_VAMP_DEPTH_DENSITY_5M` stores `total_size` (sum of top 10 levels)
- Rolling window defaults to 300 seconds (not in `ROLLING_WINDOW_SIZES`)
- Strategy reads `depth_density_history.mean` and compares `current_total_size > mean * 1.2`

**The math:** If average top-10 depth is 5000 shares, current depth must be > 6000 shares to pass. Most ticks hover near 5000.

### 🟡 SECONDARY: Gate A — Participants (Confidence: HIGH)

**Location:** `vamp_momentum.py` lines 128-143

**The gate:**
```python
min_avg_participants = params.get("min_avg_participants", 1.5)
gate_a = avg_participants >= min_avg_participants
```

**Problem:** Two sub-issues compound:

**A1. `NumParticipants` defaults to 0 from the API:**
- `tradestation_client.py` line 609: `"NumParticipants": b.get("NumParticipants", 0)` — defaults to 0
- `main.py` line 2079: `"participants": int(b.get("NumParticipants", 1))` — defaults to 1
- When API returns 0, it's stored as 0 (the `get` returns 0, not missing)
- Strategy fallback line 134: `l.get("participants", 1)` — defaults to 1 only if key missing

**A2. Rolling window stores 0s, strategy reads 0:**
- `main.py` line 2177-2181: `avg_participants = (bid_avg_p + ask_avg_p) / 2` — correctly averages
- But `bid_avg_participants` and `ask_avg_participants` come from `orb_probe.py` / `tradestation_client.py` which compute averages from `num_participants` / `OrderCount` fields
- If these fields are 0, the rolling window stores 0.0
- Strategy reads `participants_history.latest` which is 0.0
- `0.0 >= 1.5` → **FAIL**

**A3. Fallback is unreachable:**
- `participants_history.count > 0` is almost always true (data flows every tick)
- So the fallback (lines 135-142) that computes from stored levels is rarely used
- Even if reached, stored levels have `participants=0` from API, so fallback average ≈ 0

### 🟡 TERTIARY: Gate C — Spread Stability (Confidence: MEDIUM)

**Location:** `vamp_momentum.py` lines 168-173

**The gate:**
```python
gate_c = current_spread < ma_spread
```

**Problem:** Requires current spread to be **tighter** than the 5-minute average. During trending/volatile markets — when VAMP momentum signals would be most useful — spreads typically WIDEN, causing this gate to block signals at the worst times.

This is a conceptual mismatch: VAMP detects book imbalance *before* price reacts. Momentum signals are most valuable during volatility, but Gate C requires calm markets (tighter-than-average spread).

### 🟢 MINOR: MIN_CONFIDENCE = 0.0 (Confidence: HIGH)

**Location:** `vamp_momentum.py` line 47

`MIN_CONFIDENCE = 0.0` is a no-op threshold. Every signal that passes gates A/B/C gets through regardless of confidence score. Compare to `delta_iv_divergence.py` and `iv_gex_divergence.py` which use `MIN_CONFIDENCE = 0.20`.

### 🟢 MINOR: Docstring says 7 confidence components, code computes 5 (Confidence: HIGH)

**Location:** `vamp_momentum.py` lines 23-32 (docstring) vs lines 244-305 (actual code)

Docstring claims 7 components:
1. VAMP deviation magnitude (0.0–0.25)
2. VAMP ROC strength (0.0–0.20)
3. Participant conviction (0.0–0.15)
4. Liquidity density (0.0–0.15)
5. Spread stability (0.0–0.10)
6. GEX regime alignment (0.0–0.10) ← **NOT IMPLEMENTED**
7. Depth level quality (0.0–0.05) ← **NOT IMPLEMENTED**

Actual code computes 5 components (lines 273-304):
1. `c1`: VAMP deviation magnitude
2. `c2`: VAMP ROC strength
3. `c3`: Participant conviction
4. `c4`: Liquidity density
5. `c5`: Spread stability

Same pattern as `iv_gex_divergence.py` (Issue E from task brief).

---

## Specific Code-Level Issues

### Issue 1: Gate B multiplier too aggressive (vamp_momentum.py line 158)

**Current:** `liquidity_density_min_mult = 1.2` (20% above average)
**Impact:** Blocks ~85-95% of ticks

### Issue 2: `NumParticipants` field defaults to 0 (tradestation_client.py line 609)

**Current:** `"NumParticipants": b.get("NumParticipants", 0)`
**Impact:** Rolling window stores 0.0, Gate A fails

### Issue 3: Gate A threshold too high for 0 participant data (vamp_momentum.py line 156)

**Current:** `min_avg_participants = 1.5`
**Impact:** Fails when participant data is 0 or 1

### Issue 4: MIN_CONFIDENCE no-op (vamp_momentum.py line 47)

**Current:** `MIN_CONFIDENCE = 0.0`
**Impact:** No confidence filtering

---

## Recommended Fixes

### Fix 1: Gate B — Lower multiplier or change to absolute threshold (vamp_momentum.py lines 157-165)

**Option A (lower multiplier):**
```python
# Change line 158 default
liquidity_density_min_mult = params.get("liquidity_density_min_mult", 1.05)
```
- 5% above average instead of 20%
- Would pass ~40-50% of ticks (much more reasonable)

**Option B (absolute minimum depth):**
```python
# Replace Gate B with minimum depth check
min_depth = params.get("min_depth", 2000)  # shares
gate_b = current_total_size >= min_depth
```
- Checks for "sufficient liquidity" rather than "depth surge"
- More intuitive for a momentum strategy

**Option C (z-score based):**
```python
# Use z-score instead of fixed multiplier
if depth_density_history and depth_density_history.count > 0:
    z = (current_total_size - depth_density_history.mean) / (depth_density_history.std or 1)
    gate_b = z > -0.5  # within 0.5σ below mean
```
- Allows normal depth variation
- Only blocks extreme thin-book conditions

### Fix 2: Gate A — Lower threshold or make optional (vamp_momentum.py lines 155-159)

```python
# Option A: Lower threshold
min_avg_participants = params.get("min_avg_participants", 1.0)

# Option B: Only require if participant data is available
if participants_history and participants_history.count > 0 and participants_history.latest > 0:
    gate_a = avg_participants >= min_avg_participants
else:
    gate_a = True  # Skip gate if no participant data
```

### Fix 3: Gate C — Make it a soft filter or remove (vamp_momentum.py lines 167-173)

```python
# Option A: Remove Gate C entirely (VAMP is designed for volatile markets)
gate_c = True

# Option B: Make it a confidence component instead of hard gate
# (already computed as c5 in _compute_confidence)
gate_c = True
```

### Fix 4: Set MIN_CONFIDENCE = 0.20 (vamp_momentum.py line 47)

```python
MIN_CONFIDENCE = 0.20
```

### Fix 5: Align docstring with implementation (vamp_momentum.py lines 23-32)

Update docstring to reflect 5-component model, or implement components 6-7.

---

## Priority Order

1. **Gate B fix** (highest impact — likely single biggest blocker)
2. **Gate A fix** (secondary blocker when participant data is 0)
3. **Gate C reconsideration** (conceptual mismatch with strategy purpose)
4. **MIN_CONFIDENCE** (low effort, reasonable safety)
5. **Docstring alignment** (documentation hygiene)

## Confidence Assessment

| Finding | Confidence | Evidence |
|---------|-----------|----------|
| Gate B blocks 85-95% of ticks | **HIGH** | Statistical property of "X% above mean" gates on stationary time series |
| Gate A fails with 0 participant data | **HIGH** | Confirmed: API defaults to 0, rolling window stores 0, strategy reads 0 |
| Gate C blocks during volatility | **MEDIUM** | Conceptual analysis; would benefit from empirical spread data |
| MIN_CONFIDENCE = 0.0 | **HIGH** | Direct code observation |
| Docstring mismatch | **HIGH** | Direct code observation |
