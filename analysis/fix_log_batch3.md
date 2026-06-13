# Batch 3 — Confidence Normalization Fixes

**Date:** 2026-06-13
**Purpose:** Fix `normalize(x, vmin, vmax)` calls where `vmax` far exceeds actual data ranges, causing confidence components to contribute ~0 instead of meaningful differentiation.

---

## Fix 1: iv_skew_squeeze.py — Skew extremity c4 component

**File:** `strategies/full_data/iv_skew_squeeze.py`
**Component:** c4 — Skew extremity in `_compute_confidence_v2()`

**Problem:** `normalize(current_skew, 0.0, 10.0)` — actual skew values range [-0.07, +0.20]. A value of 0.20 normalized against a 10.0 ceiling yields 0.02, making this component effectively dead weight.

**Before:**
```python
# 4. Skew extremity: current_skew 0→10, higher = more extreme = higher
c4 = normalize(current_skew, 0.0, 10.0)
```

**After:**
```python
# 4. Skew extremity: current_skew 0→1, higher = more extreme = higher
c4 = normalize(current_skew, 0.0, 1.0)
```

**Impact:** Skew values of 0.20 now normalize to 0.20 (was 0.02), giving the extremity component meaningful differentiation across the actual data range.

---

## Fix 2: skew_dynamics.py — Ψ magnitude c1 component

**File:** `strategies/full_data/skew_dynamics.py`
**Component:** c1 — Ψ magnitude in `_compute_confidence()`

**Problem:** `normalize(current_psi, 0.0, 5.0)` — actual Ψ values are much smaller than 5.0, so normalization yields near-zero values for all entries.

**Before:**
```python
# 1. Ψ magnitude: current_psi from 0→5, higher = higher
c1 = normalize(current_psi, 0.0, 5.0)
```

**After:**
```python
# 1. Ψ magnitude: current_psi from 0→1, higher = higher
c1 = normalize(current_psi, 0.0, 1.0)
```

**Impact:** Ψ values now properly scale to [0,1] within their actual range, giving this component meaningful weight in the 10-component average.

---

## Fix 3: smile_dynamics.py — Ω magnitude c1 component

**File:** `strategies/full_data/smile_dynamics.py`
**Component:** c1 — Ω magnitude in `_compute_confidence()`

**Problem:** `normalize(current_omega, 0.0, 5.0)` — Ω values don't reach 5.0, causing near-zero normalization.

**Before:**
```python
# 1. Ω magnitude: higher = more curvature asymmetry
c1 = normalize(current_omega, 0.0, 5.0)
```

**After:**
```python
# 1. Ω magnitude: higher = more curvature asymmetry
c1 = normalize(current_omega, 0.0, 3.0)
```

**Impact:** Using 3.0 as ceiling provides better differentiation for the actual Ω range while still allowing headroom for extreme values.

---

## Fix 4: vamp_momentum.py — Participant count c3 component

**File:** `strategies/layer2/vamp_momentum.py`
**Component:** c3 — Participant conviction in `_compute_confidence()`

**Problem:** `normalize(avg_participants, 1.0, 5.0)` — actual participant counts range 15-20+, so all values saturate at 1.0 immediately, making this component a constant rather than a differentiator.

**Before:**
```python
# 3. Participant conviction: avg_participants from 1.0→3.0, higher = higher
# (relaxed from min_participants→2×min_participants to 1.0→3.0 for softer scale)
c3 = normalize(avg_participants, 1.0, 5.0)
```

**After:**
```python
# 3. Participant conviction: avg_participants from 1.0→20.0, higher = higher
c3 = normalize(avg_participants, 1.0, 20.0)
```

**Impact:** Participant counts of 5-20+ now properly differentiate across the range instead of all capping at 1.0.

---

## Verification

All four files pass `python3 -m py_compile`:
- ✅ `iv_skew_squeeze.py` — syntax OK
- ✅ `skew_dynamics.py` — syntax OK
- ✅ `smile_dynamics.py` — syntax OK
- ✅ `vamp_momentum.py` — syntax OK
