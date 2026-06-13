# delta_iv_divergence Code Review

**Date:** 2026-06-13
**Strategy:** `strategies/layer2/delta_iv_divergence.py` (Delta-IV Divergence v2 — Tail-Risk Divergence)
**Status:** No signals produced during June 12 run despite being enabled in config.

---

## Issues Found

### Critical

1. **`_regime_confidence()` uses old-scale thresholds (2000, 1000) — dead but misleading**
   - The method hardcodes thresholds of 2000 and 1000 for `abs(net_gamma)`:
     ```python
     if gamma_abs > 2_000: return 0.10
     elif gamma_abs > 1_000: return 0.08
     else: return 0.05
     ```
   - With normalized gamma maxing at ~1608, this method would **always return 0.05** even if called.
   - The thresholds match the old cumulative net_gamma scale (millions), not the normalized scale (~1608 max).
   - **Impact:** If wired in, this would contribute a flat 0.05 to confidence regardless of actual gamma regime.

### High

2. **Dead code: `_regime_confidence()`, `_volume_conviction_confidence()`, `_divergence_confidence()` are never called**
   - All three methods exist in the class but are not referenced in `_compute_confidence()`.
   - `_compute_confidence()` averages exactly 5 components: `c1=c2=c3=c4=c5`.
   - The docstring claims "Family A simple average" but the method names and return ranges suggest they were intended as additional confidence contributors that were dropped during a refactor.
   - **Impact:** Confidence scores are lower than designed, making it harder to reach the `MIN_CONFIDENCE=0.20` threshold.

3. **Hard gate methods are defined but never wired in**
   - `_check_skew_divergence()` — implements hard gate (`skew_div > 0.10`), never called
   - `_check_decoupling()` — implements hard gate (`abs(current_corr) < abs(mean_corr) * threshold`), never called
   - `_check_gamma_regime()` — implements hard gate (`current < mean * 0.70`), never called
   - Only the soft score variants (`_skew_divergence_score`, `_decoupling_score`, `_gamma_regime_score`) are used.
   - **Impact:** If these hard gates were intended as additional filters, the strategy has no such gates and may produce false signals in edge cases. If they were meant to be removed, they're dead code clutter.

### Medium

4. **`_compute_confidence()` c5 double-sources net_gamma with a redundant fallback path**
   - The method receives `net_gamma` (normalized, already bounded ~1608) as a parameter.
   - It also re-computes `net_gamma_from_summary` by summing `net_gamma` across all strikes in `greeks_summary`, then divides by 2000.0.
   - The 2000.0 divisor is calibrated for the old cumulative scale. With normalized values (~1608 max), `c5 = min(1.0, 1608/2000) = 0.804` — not broken, but the divisor should be ~1600 to cap at 1.0.
   - The fallback path (`else: c5 = min(1.0, abs(net_gamma) / 2000.0)`) is correct in using the parameter directly.
   - **Fix:** Either remove the greeks_summary summation (it's redundant) or update the divisor to ~1600.

5. **Soft gate combined threshold (0.15) is likely too restrictive**
   - The condition `skew_score + decouple_score + gamma_score < 0.15` requires at least one soft gate to be non-zero.
   - If skew divergence is below 0.10 (common), decoupling ratio is near 1.0 (common in stable markets), and gamma density isn't declining (common), all three scores are 0.0 and the strategy returns early.
   - **Impact:** This creates a narrow funnel that can block all signals during normal market conditions.

### Low

6. **Strategy keys are correctly defined and populated**
   - The strategy requires: `KEY_OTM_DELTA_5M`, `KEY_OTM_IV_5M`, `KEY_DELTA_IV_CORR_5M`, `KEY_GAMMA_DENSITY_5M`.
   - All four are defined in `rolling_keys.py`, populated in `main.py`, and included in `ALL_KEYS`.
   - **Verdict:** No issue — data pipeline is correct.

7. **Wall proximity threshold (500,000) is consistent with other strategies**
   - With normalized GEX bounded at ~1608 per strike, a wall needs: `1608 * 100 * price >= 500,000` → `price >= 3.10`. For TSLA at ~$400, this means `norm_gamma >= 12.5` — easily achievable.
   - **Verdict:** Threshold is fine for normalized GEX.

---

## Root Cause Analysis

The strategy's core logic (delta-IV trend alignment, z-score divergence) is sound and uses the correct `net_gamma_normalized` key. The **most likely reasons for zero signals** are:

1. **Soft gate combined threshold too high:** The condition `skew_score + decouple_score + gamma_score < 0.15` requires at least one soft gate to be non-zero. During normal market conditions, all three scores can be 0.0, causing the strategy to return early.

2. **Divergence strength threshold:** `MIN_DIVERSION_STRENGTH = 0.2` requires `min(delta_z, abs(iv_z)) / 2.0 >= 0.2` → both z-scores must be ≥ 0.4. Combined with the soft gate requirement, this creates a narrow funnel.

3. **Confidence formula missing contributors:** The dead `_regime_confidence()` and `_volume_conviction_confidence()` methods suggest the original design had 7 components. With only 5, the average confidence is lower, making it harder to clear `MIN_CONFIDENCE = 0.20`.

---

## Suggested Fixes

| Priority | Action |
|----------|--------|
| **P0** | **Wire in or remove dead methods.** Either call `_regime_confidence()` and `_volume_conviction_confidence()` in `_compute_confidence()`, or delete them. If keeping, update regime thresholds to ~1600 max for normalized gamma. |
| **P1** | **Lower the soft gate combined threshold** from 0.15 to 0.05, or make it per-gate (e.g., at least 1 of 3 must be > 0.05). The current 0.15 combined threshold is likely too restrictive. |
| **P1** | **Fix c5 divisor** from 2000.0 to ~1600.0 to properly normalize against the bounded gamma scale. |
| **P2** | **Wire in the hard gate methods** (`_check_skew_divergence`, `_check_decoupling`, `_check_gamma_regime`) as additional filters if they were intended to exist, or remove them if they're obsolete. |
| **P2** | **Remove `_divergence_confidence()`** dead code — it's never called and duplicates the divergence_strength → confidence logic already in the main formula. |
| **P3** | **Add logging** at key decision points (soft gate scores, divergence_strength, confidence) to diagnose signal suppression during runs. |
