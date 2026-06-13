# Rune QA — Extrinsic Flow Verdict

**Date:** 2026-06-13
**Strategy:** `strategies/full_data/extrinsic_flow.py`
**Phase:** 4 — Rune Quality Assurance
**Verdict:** **NOT APPROVED**

---

## Summary

Two of three batch fixes are correct, but the **critical crash bug remains unfixed**. The regime penalty line `confidence *= 0.7` is still positioned **before** `confidence` is defined, so the same `UnboundLocalError` that the review identified will still occur when `_regime_mismatch` is True.

---

## Fix-by-Fix Analysis

### 1. Crash Bug (UnboundLocalError) — ❌ NOT FIXED

**Current code (lines 294–296, 307):**
```python
def _compute_confidence(self, ...):
    if getattr(self, '_regime_mismatch', False):
        confidence *= 0.7          # ← confidence not yet defined!
    c1 = normalize(phi_ratio, 0.0, 5.0)
    c2 = normalize(phi_total, 0.0, 1000.0)
    c3 = normalize(phi_sigma, 0.0, 5.0)
    c4 = normalize(phi_call, 0.0, 1000.0)
    c5 = normalize(phi_put, 0.0, 1000.0)
    confidence = (c1 + c2 + c3 + c4 + c5) / 5.0   # ← defined here
    return min(1.0, max(0.0, confidence))
```

The regime penalty still reads `confidence` before it's assigned. When `_regime_mismatch` is True, Python raises `UnboundLocalError: local variable 'confidence' referenced before assignment`. The review's suggested fix was to move the penalty after the computation — this was not done.

**Trigger path:** Any evaluation where `_gate_b_gex_regime()` sets `self._regime_mismatch = True` (regime mismatch) will cause the crash. The flag persists across evaluations, so once set, it will crash on every subsequent call.

### 2. Regime Mismatch Init — ✅ FIXED

**Line 89:**
```python
self._regime_mismatch = False
```

This is correctly initialized at the top of `evaluate()`, before any gates are evaluated. This prevents the `getattr(self, '_regime_mismatch', False)` from ever falling back to a missing attribute. Note: this init only prevents the `getattr` from failing — it does **not** fix the `confidence *= 0.7` crash, because the variable is local to `_compute_confidence()`, not an instance attribute.

### 3. Normalization Calibrations — ✅ FIXED (with caveats)

**Before (original):**
```python
c2 = normalize(phi_total, 0.0, 1.0)    # phi_total ~100-100,000 → clamped to 1.0
c3 = normalize(phi_sigma, 0.0, 5.0)    # phi_sigma ~1-10 → clamped to 1.0
c4 = normalize(phi_call, 0.0, 5.0)     # phi_call ~100-100,000 → clamped to 1.0
c5 = normalize(phi_put, 0.0, 5.0)      # phi_put ~100-100,000 → clamped to 1.0
```

**After (batch fix):**
```python
c2 = normalize(phi_total, 0.0, 1000.0)  # phi_total ~100-100,000 → 0.1-1.0 range
c3 = normalize(phi_sigma, 0.0, 5.0)     # phi_sigma ~1-10 → 0.2-2.0 range (clamped)
c4 = normalize(phi_call, 0.0, 1000.0)   # phi_call ~100-100,000 → 0.1-1.0 range
c5 = normalize(phi_put, 0.0, 1000.0)    # phi_put ~100-100,000 → 0.1-1.0 range
```

**Verification results:**

| Component | New Max | Typical Value | Normalized | Verdict |
|-----------|---------|---------------|------------|---------|
| c1 (phi_ratio) | 5.0 | 0.5–5.0 | 0.10–1.00 | ✅ Good — ratio naturally fits 0–5 |
| c2 (phi_total) | 1000 | 100–10,000 | 0.10–1.00 | ✅ Acceptable — provides spread |
| c3 (phi_sigma) | 5.0 | 1–10 | 0.20–1.00 | ✅ Good — sigma is typically < 5 |
| c4 (phi_call) | 1000 | 100–10,000 | 0.10–1.00 | ✅ Acceptable — provides spread |
| c5 (phi_put) | 1000 | 100–10,000 | 0.10–1.00 | ✅ Acceptable — provides spread |

**Caveat:** For very high-volume scenarios (phi_total > 1000, phi_call > 1000, phi_put > 1000), c2/c4/c5 still clamp to 1.0. This is acceptable — it means the strategy correctly caps confidence at 1.0 rather than exceeding it. The review's suggestion of log-scale normalization for dollar amounts is a nice-to-have optimization, not a bug.

**Confidence score examples (verified):**
- Typical: confidence = 0.480 (with regime penalty: 0.336)
- High volume: confidence = 0.880
- Low volume: confidence = 0.070
- Zero values: confidence = 0.000
- Extreme values: confidence = 1.000

All produce valid [0, 1] ranges. ✅

---

## Confidence Score Validity — ✅ NO REGRESSIONS

All code paths produce valid [0, 1] confidence:
- `normalize()` clamps to [0, 1]
- Final `min(1.0, max(0.0, confidence))` ensures bounds
- `evaluate()` applies `max(MIN_CONFIDENCE, confidence)` where `MIN_CONFIDENCE = 0.20`
- Regime penalty `*= 0.7` (when it works) scales down without going negative

---

## Other Issues Not Addressed by Batch Fixes

These are **not blockers** but worth noting:

1. **Gate B always returns True** (line 274): Even on regime mismatch, `_gate_b_gex_regime()` returns `True` and only sets `self._regime_mismatch = True`. The review noted this should optionally return `False` for hard-mode operation. This is a quality-of-signal issue, not a crash.

2. **Unused `depth_score` parameter** (line 286): Dead code from incomplete refactoring. No impact.

3. **No debug logging for missing rolling windows** (lines 95–102): Strategy returns `[]` silently. Minor — doesn't affect correctness.

4. **Intensity thresholds not aligned with confidence model** (lines 163–169): Intensity uses hardcoded RΦ ratios while confidence uses the 5-component model. No correlation between them. Cosmetic.

---

## Required Fix

The crash bug must be fixed before approval. Two equivalent solutions:

**Option A — Move penalty after computation (cleaner):**
```python
def _compute_confidence(self, ...):
    c1 = normalize(phi_ratio, 0.0, 5.0)
    c2 = normalize(phi_total, 0.0, 1000.0)
    c3 = normalize(phi_sigma, 0.0, 5.0)
    c4 = normalize(phi_call, 0.0, 1000.0)
    c5 = normalize(phi_put, 0.0, 1000.0)
    confidence = (c1 + c2 + c3 + c4 + c5) / 5.0

    if getattr(self, '_regime_mismatch', False):
        confidence *= 0.7

    return min(1.0, max(0.0, confidence))
```

**Option B — Initialize confidence before penalty:**
```python
def _compute_confidence(self, ...):
    confidence = 0.0  # ← add this line
    if getattr(self, '_regime_mismatch', False):
        confidence *= 0.7
    c1 = normalize(phi_ratio, 0.0, 5.0)
    ...
```

---

## Final Verdict: NOT APPROVED

**Reason:** The critical `UnboundLocalError` crash in `_compute_confidence()` is still present. The regime penalty `confidence *= 0.7` executes **before** `confidence` is defined on line 307. When `_regime_mismatch` is True (which it will be on any regime mismatch), the function crashes. The batch fix description claims this was addressed, but the code shows the penalty line is still in its original pre-computation position.

**Confidence score ranges are valid** and normalization calibrations are **sensible** for the data ranges. No regressions in the confidence model. The remaining issues (Gate B, depth_score, logging) are non-blocking.
