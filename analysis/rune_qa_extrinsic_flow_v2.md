# Rune QA — Extrinsic Flow Verdict (v2)

**Date:** 2026-06-13
**Strategy:** `strategies/full_data/extrinsic_flow.py`
**Phase:** 4 — Rune Quality Assurance
**Version:** v2 (second attempt, post-crash-bug-fix)
**Verdict:** **APPROVED**

---

## Summary

The critical `UnboundLocalError` crash in `_compute_confidence()` is **fixed**. The regime penalty `confidence *= 0.7` has been moved to **after** the confidence computation, resolving the issue identified in the v1 review. All other components — normalization calibrations, gate logic, confidence floor — remain sound with no regressions.

---

## Crash Bug Fix — ✅ FIXED

**What was broken (v1):**
```python
def _compute_confidence(self, ...):
    if getattr(self, '_regime_mismatch', False):
        confidence *= 0.7          # ← UnboundLocalError! confidence not yet defined
    c1 = normalize(phi_ratio, 0.0, 5.0)
    c2 = normalize(phi_total, 0.0, 1000.0)
    c3 = normalize(phi_sigma, 0.0, 5.0)
    c4 = normalize(phi_call, 0.0, 1000.0)
    c5 = normalize(phi_put, 0.0, 1000.0)
    confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
    return min(1.0, max(0.0, confidence))
```

**What is fixed (v2):**
```python
def _compute_confidence(self, ...):
    c1 = normalize(phi_ratio, 0.0, 5.0)
    c2 = normalize(phi_total, 0.0, 1000.0)
    c3 = normalize(phi_sigma, 0.0, 5.0)
    c4 = normalize(phi_call, 0.0, 1000.0)
    c5 = normalize(phi_put, 0.0, 1000.0)
    confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
    # Apply regime penalty AFTER confidence is computed
    if getattr(self, '_regime_mismatch', False):
        confidence *= 0.7
    return min(1.0, max(0.0, confidence))
```

**Why this works:** Python determines at compile time that `confidence` is a local variable (because it's assigned later in the function). When the `if` block tries to read `confidence` before the assignment, it raises `UnboundLocalError`. Moving the penalty after `confidence = ...` ensures the variable exists when the `*=` operator reads it.

**Trigger path verified:**
1. `evaluate()` calls `_gate_b_gex_regime()` → sets `self._regime_mismatch = True` on mismatch
2. `evaluate()` calls `_compute_confidence()` → penalty correctly applies `confidence *= 0.7`
3. No crash. ✅

---

## Supporting Fix: `_regime_mismatch` Initialization — ✅

**Line ~89 in `evaluate()`:**
```python
self._regime_mismatch = False
```

This is initialized at the top of `evaluate()`, before any gates are evaluated. This ensures:
- The `getattr(self, '_regime_mismatch', False)` in `_compute_confidence()` always has a value to read
- Each call to `evaluate()` starts fresh (no stale mismatch from prior calls)
- The flag persists across gate evaluation within the same call

---

## Other Components — No Regressions

### Normalization Calibrations — ✅
Same as v1 review: c2/c4/c5 max values raised from 5.0 to 1000.0, providing proper spread for typical data ranges. No regression.

### Confidence Floor — ✅
- Module-level `MIN_CONFIDENCE = 0.20`
- `evaluate()` applies `confidence = max(min_confidence, confidence)` then `if confidence < min_confidence: return []`
- Pattern: "Floor + early return" (Pattern #2 from confidence audit)

### Gate B — ✅
Returns `True` in all cases, sets `_regime_mismatch = True` on mismatch. This is the intended behavior for regime-soft mode. No change needed.

### Confidence Bounds — ✅
- Each `normalize()` call returns [0.0, 1.0]
- Average of 5 components → [0.0, 1.0]
- Regime penalty `*= 0.7` → [0.0, 0.7] when active
- Final `min(1.0, max(0.0, confidence))` → [0.0, 1.0]
- `evaluate()` floor `max(MIN_CONFIDENCE, ...)` → [0.20, 1.0]

### Early Return Guards — ✅
All 5 rolling window checks (phi_call, phi_put, phi_ratio, phi_total, phi_sigma) guard against missing/insufficient data with early `return []`. No risk of downstream crashes.

---

## Minor Notes (Non-Blocking)

1. **Gate B always returns True** — On regime mismatch, Gate B still passes and the penalty is applied in confidence instead. This is intentional for regime-soft mode. If hard-mode is desired later, Gate B could return `False` on mismatch.

2. **Unused `depth_score` parameter** — Dead code from incomplete refactoring in `_compute_confidence()`. No impact.

3. **No debug logging for missing rolling windows** — Strategy returns `[]` silently. Minor — doesn't affect correctness.

4. **Intensity thresholds** — Use hardcoded RΦ ratios independent of the 5-component confidence model. Cosmetic, no correlation issue.

---

## Comparison: v1 vs v2

| Component | v1 Verdict | v2 Verdict |
|-----------|-----------|-----------|
| Crash bug (UnboundLocalError) | ❌ NOT FIXED | ✅ FIXED |
| `_regime_mismatch` init | ✅ FIXED | ✅ FIXED |
| Normalization calibrations | ✅ FIXED | ✅ FIXED |
| Confidence floor | ✅ | ✅ |
| Gate B logic | ✅ | ✅ |
| Confidence bounds | ✅ | ✅ |

---

## Final Verdict: **APPROVED**

**Reason:** The critical `UnboundLocalError` crash is resolved. The regime penalty `confidence *= 0.7` now executes after `confidence` is defined, and all supporting components remain intact with no regressions. The strategy is ready for production.

**Confidence in verdict:** High. The fix is a single-line relocation that directly addresses the root cause identified in v1. All code paths have been verified.
