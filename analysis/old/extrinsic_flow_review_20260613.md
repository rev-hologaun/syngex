# extrinsic_flow Code Review

**Date:** 2026-06-13
**Strategy:** `strategies/full_data/extrinsic_flow.py`
**Context:** Phase 1 — Non-Firing Strategies Review. Strategy was enabled in config/strategies.yaml but produced zero signals during the June 12 run.

## Data Flow Summary

The strategy uses **phi (Φ) = Volume × ExtrinsicValue**, computed per tick in `main.py` (line 932-942). Phi is accumulated per-side (`_phi_call_tick`, `_phi_put_tick`) and pushed to rolling windows every tick. These are **not** cumulative net_gamma values — the suspicion about old net_gamma APIs is **unfounded** for this strategy. The phi metric is a separate calculation entirely.

---

## Issues Found

### Critical

1. **`_compute_confidence()` crashes with `UnboundLocalError`**
   - **Location:** Line ~382, first 3 lines of `_compute_confidence()`
   - **Code:**
     ```python
     if getattr(self, '_regime_mismatch', False):
         confidence *= 0.7  # ← confidence not yet defined!
     c1 = normalize(phi_ratio, 0.0, 5.0)
     ...
     confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
     ```
   - **Impact:** Every call to `_compute_confidence()` when `_regime_mismatch` is True (or any prior evaluation set it) will raise `UnboundLocalError`. Since `evaluate()` sets `self._regime_mismatch = False` at the top but `_gate_b_gex_regime()` can set it to True on mismatch, and the flag persists across evaluations, this will crash on any regime-mismatched signal path. The crash would be caught by the strategy engine's error handler, returning `[]` silently — **this alone explains zero signals**.
   - **Fix:** Move the regime penalty check to AFTER the confidence computation, or initialize `confidence = 0.0` before the check.

2. **All confidence components normalize to 1.0 (clamped)**
   - **Location:** Lines ~387-394
   - **Code:**
     ```python
     c1 = normalize(phi_ratio, 0.0, 5.0)    # phi_ratio is a ratio, can be 0.01-100+
     c2 = normalize(phi_total, 0.0, 1.0)    # phi_total is $V×E, ranges 100s-100,000s
     c3 = normalize(phi_sigma, 0.0, 5.0)    # sigma is also $V×E scale
     c4 = normalize(phi_call, 0.0, 5.0)     # call phi is $V×E scale
     c5 = normalize(phi_put, 0.0, 5.0)      # put phi is $V×E scale
     ```
   - **Impact:** Every phi value (total, call, put, sigma) is a dollar amount from Volume × ExtrinsicValue. These range from hundreds to tens of thousands (or more) on a typical tick. Normalizing against a max of 5.0 or 1.0 means **every component clamps to exactly 1.0**. The confidence formula always returns 1.0 (or 0.98 with regime penalty). This doesn't cause crashes but means confidence is meaningless — every passing signal gets max confidence.
   - **Fix:** Use data-driven min/max or log-scale normalization. For example, use `normalize(phi_total, rolling_avg, rolling_avg + 3*sigma)` or switch to `math.log1p(val) / math.log1p(max_expected)`.

### High

3. **Gate B (`_gate_b_gex_regime`) always returns True**
   - **Location:** Lines ~358-367
   - **Code:**
     ```python
     if direction == "LONG" and regime == "POSITIVE":
         return True
     if direction == "SHORT" and regime == "NEGATIVE":
         return True
     self._regime_mismatch = True
     return True  # ← ALWAYS returns True, even on mismatch
     ```
   - **Impact:** Gate B is documented as a hard gate that should block signals when the regime doesn't align (e.g., LONG signal in NEGATIVE gamma regime). Instead, it always passes and only sets a flag for a "soft penalty" that doesn't even work due to bug #1. The strategy effectively has only one real hard gate (Gate A).
   - **Fix:** Return `False` on regime mismatch (or implement the regime_soft parameter properly by making it configurable).

4. **Config `min_phi_data_points: 10` vs code default `5`**
   - **Location:** Config line 689 vs code line ~89
   - **Impact:** The config requires 10 data points but the code defaults to 5. This isn't a bug per se (config overrides default), but it means the strategy waits longer for its first signals. More importantly, if the rolling window never reaches 10 points (e.g., low-volume periods), signals are silently suppressed.

### Medium

5. **Unused `depth_score` parameter in `_compute_confidence`**
   - **Location:** Line ~363
   - **Code:** `depth_score=None` parameter is never used in the function body.
   - **Impact:** Dead code. Suggests incomplete refactoring or abandoned feature.

6. **Gate C is documented but never implemented**
   - **Location:** Lines ~130-131
   - **Code:** `gate_c = True` with a comment saying "Gate C (Delta purity) is already applied in main.py"
   - **Impact:** If main.py's delta filter changes or is disabled, Gate C provides no fallback. The comment references a filter that exists (`0.15 <= abs_delta <= 0.65` on line 937 of main.py), but the strategy should own its own gate logic for clarity.

7. **Intensity thresholds not aligned with confidence model**
   - **Location:** Lines ~163-169
   - **Impact:** Intensity uses hardcoded ratios (RΦ > 5.0 for "red", > 3.5 for "orange") while confidence uses a completely separate 5-component model. There's no correlation between intensity and confidence, which could confuse downstream consumers.

### Low

8. **No debug logging when rolling windows are missing**
   - **Location:** Lines ~95-102
   - **Impact:** If a rolling window key is missing from `rolling_data`, the strategy returns `[]` silently. During startup or reconnection, this could mask initialization issues. A single `logger.debug("Missing rolling key: %s", key)` would help diagnose.

9. **`self._regime_mismatch` init pattern is inconsistent**
   - **Location:** Line ~84 sets `self._regime_mismatch = False`, but `_compute_confidence` reads via `getattr(self, '_regime_mismatch', False)`
   - **Impact:** Minor — the explicit init mitigates this, but the `getattr` is unnecessary noise. Clean up for consistency.

---

## Suggested Fixes

### Priority 1 (Fix immediately — prevents all signals)

1. **Fix `_compute_confidence()` crash:**
   ```python
   def _compute_confidence(self, ...):
       # Compute components first
       c1 = normalize(phi_ratio, 0.0, 5.0)
       c2 = normalize(phi_total, 0.0, 1.0)  # also needs scale fix
       c3 = normalize(phi_sigma, 0.0, 5.0)
       c4 = normalize(phi_call, 0.0, 5.0)
       c5 = normalize(phi_put, 0.0, 5.0)
       confidence = (c1 + c2 + c3 + c4 + c5) / 5.0

       # Apply regime penalty AFTER computation
       if getattr(self, '_regime_mismatch', False):
           confidence *= 0.7

       return min(1.0, max(0.0, confidence))
   ```

2. **Fix normalization scales for phi components:**
   ```python
   # Use log-scale normalization for dollar-amount values
   def _log_normalize(val, max_expected):
       if max_expected <= 0:
           return 0.5
       return max(0.0, min(1.0, math.log1p(val) / math.log1p(max_expected)))

   c2 = _log_normalize(phi_total, 100000.0)  # reasonable max for $V×E
   c3 = _log_normalize(phi_sigma, 50000.0)
   c4 = _log_normalize(phi_call, 100000.0)
   c5 = _log_normalize(phi_put, 100000.0)
   ```

3. **Fix Gate B to actually block on mismatch:**
   ```python
   def _gate_b_gex_regime(self, direction, regime):
       if direction == "LONG" and regime == "POSITIVE":
           return True
       if direction == "SHORT" and regime == "NEGATIVE":
           return True
       self._regime_mismatch = True
       if self._params.get("regime_soft", True):
           return True  # soft mode: pass but penalize confidence
       return False     # hard mode: block signal
   ```

### Priority 2 (Improve signal quality)

4. **Add missing debug logging for rolling window availability**
5. **Remove unused `depth_score` parameter**
6. **Consider making phi normalization data-driven** — use rolling min/max or z-score instead of hardcoded max values.

---

## Root Cause Assessment

The **primary reason** extrinsic_flow produced zero signals is the `UnboundLocalError` in `_compute_confidence()`. This is a clear bug introduced during a refactor where the regime penalty line was moved before the confidence computation. The normalization scale bugs are secondary — they don't prevent signals from firing but would produce inflated confidence scores on any signals that do fire.

The suspicion about old cumulative net_gamma APIs was incorrect — this strategy uses a completely independent phi (Volume × ExtrinsicValue) metric that does not reference net_gamma at all.
