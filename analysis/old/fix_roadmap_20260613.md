# Syngex Zero-Fire Fix Roadmap — 2026-06-13

**Generated:** After reviewing all 20 strategy files + 20 review outputs
**Status:** Ready for batch execution

---

## Issue Summary (by severity)

| Tier | Count | Strategies Affected | Description |
|------|-------|---------------------|-------------|
| **Critical** | 5 | gamma_flip_breakout, extrinsic_flow | Hard old-scale thresholds + crash bugs that completely block signals |
| **High** | 11 | delta_iv_divergence, extrinsic_intrinsic_flow, gamma_breaker, ghost_premium, iron_anchor, iv_band_breakout, iv_gex_divergence, iv_skew_squeeze, obi_aggression_flow, prob_distribution_shift, sentiment_sync, skew_dynamics, smile_dynamics | Logic bugs, scale mismatches, wrong parameters that prevent firing under real conditions |
| **Medium** | 14 | All 20 strategies | Calibration issues, overly strict gates, missing edge-case handling |
| **Low** | 8 | delta_iv_divergence, extrinsic_intrinsic_flow, gamma_breaker, gamma_volume_convergence, gamma_flip_breakout, order_book_stacking, vamp_momentum | Dead code, cosmetic inconsistencies, comment typos |

**Total unique fixes needed: ~38 across 20 strategies**

---

## Batch Grouping

### Batch 1: Scale Fixes (Old-Scale Thresholds → Normalized)
**Strategies:** gamma_flip_breakout, gamma_breaker, iron_anchor, iv_gex_divergence

**Theme:** Hard-coded millions-scale constants blocking normalized data

| Strategy | Fix | Location | Severity |
|----------|-----|----------|----------|
| gamma_flip_breakout | `abs(net_gamma) < 200000` → `< 2000` | Line ~95 | critical |
| gamma_flip_breakout | `MIN_GAMMA_STRENGTH = 100000` → `2000` | Line ~48 | critical |
| gamma_breaker | Wall classification threshold 500k→2k (if used in _safe_get_walls) | Method-level | warning |
| gamma_breaker | c5 normalize wall_gex against 1M→dynamic/vol-based | Line ~347 | warning |
| iron_anchor | Dollar proximity $1.00 → percentage (e.g., 0.2%) | Line ~116 | high |
| iron_anchor | Gamma density gate threshold 500000→proportional | _gate_b_gamma_density | warning |
| iv_gex_divergence | Verify MIN_POSITIVE_GAMMA = 200000 usage; remove or adjust | Line ~17 | warning |

**Est effort:** 1h  
**Priority:** HIGH — these are the most common failure pattern across entire codebase

---

### Batch 2: Crash & Logic Bugs
**Strategies:** extrinsic_flow, extrinsic_intrinsic_flow

**Theme:** Code errors causing crashes or wrong signal direction

| Strategy | Fix | Location | Severity |
|----------|-----|----------|----------|
| extrinsic_flow | Fix `_compute_confidence()` regime penalty referencing undefined `confidence` variable | Line ~382 | critical |
| extrinsic_flow | Fix c2 normalize(phi_total, 0.0, 1.0) → actual phi range (~500000) | Line ~388 | warning |
| extrinsic_flow | Fix c4/c5 normalize phi_call/put against 5.0 → actual scale | Lines ~392-394 | warning |
| extrinsic_flow | Implement Gate C or document it's removed (currently always passes) | Gate section | warning |
| extrinsic_intrinsic_flow | Fix `_check_short()` calls `_compute_confidence_v2(signal_type="expansion")` → `"short"` | Line ~653 | high |
| extrinsic_intrinsic_flow | Remove dead legacy confidence methods (lines ~828-913) | Legacy section | low |
| extrinsic_intrinsic_flow | Verify MIN_CONFIDENCE = 0.20 vs doc claim of 0.35 | Line ~78 | info |

**Est effort:** 45min  
**Priority:** HIGH — crash bug blocks ALL extrinsic_flow signals

---

### Batch 3: Confidence Normalization Fixes
**Strategies:** iv_skew_squeeze, skew_dynamics, smile_dynamics, vamp_momentum, gamma_breaker

**Theme:** normalize() vmax parameters far exceed actual data ranges, making components contribute zero

| Strategy | Fix | Component | Current vmax → Fixed | Severity |
|----------|-----|-----------|---------------------|----------|
| iv_skew_squeeze | Skew extremity (c4) | current_skew | 10.0 → 1.0 | high |
| skew_dynamics | Ψ magnitude (c1) | abs(skew_psi) | 5.0 → 1.0 | high |
| smile_dynamics | Ω magnitude (c1) | abs(omega) | 5.0 → 3.0 | high |
| smile_dynamics | Add min slope floor before computing Ω ratio | put_slope/call_slope | n/a | medium |
| vamp_momentum | Participant count (c3) | avg_participants | 5.0 → 15-20 | high |
| ghost_premium | Ask size sigma (c3) | ask_size_sigma from PDR std | 5.0 → dynamic | warning |
| gamma_breaker | Velocity normalization (c4) | current_velocity | 0.02 → verify against data | warning |

**Est effort:** 45min  
**Priority:** HIGH — this is the #1 systematic issue affecting confidence scoring across 7+ strategies

---

### Batch 4: Gate/Threshold Tightening
**Strategies:** gamma_flip_breakout, gamma_breaker, ob i_aggression_flow, sentiment_sync, prob_distribution_shift, iv_band_breakout

**Theme:** Overly restrictive hard gates preventing legitimate signals

| Strategy | Fix | Description | Severity |
|----------|-----|-------------|----------|
| gamma_flip_breakout | `abs(net_gamma) < 200000` check already covered in Batch 1 | — | done |
| gamma_breaker | Increase min_gamma_break default from 0.0005 to 0.005 | Breakout too sensitive | high |
| gamma_breaker | Add price-wall proximity directionality for LONG/SHORT | Direction currently purely regime-based | high |
| gamma_breaker | Remove dead `_regime_mismatch` flag (always returns True) | Dead code | medium |
| obi_aggression_flow | Lower OBI threshold from 0.75 to 0.65, AF from 0.5 to 0.40 | Simultaneous extremes too rare | high |
| sentiment_sync | Change dual-2σ requirement → one at 2σ + one at 1.5σ OR OR logic | Dual-extreme too restrictive | high |
| sentiment_sync | Volume gate relative to session baseline | Midday lull blocks signals | medium |
| prob_distribution_shift | Allow SHORT with negative net_gamma | Both directions require positive gamma | high |
| prob_distribution_shift | Soften triple-gate filter (z-score + breadth + ROC acceleration) | Too many simultaneous requirements | medium |
| iv_band_breakout | Verify delta acceleration direction-awareness for SHORT | May allow weak declines as strong breakouts | medium |

**Est effort:** 1.5h  
**Priority:** MEDIUM-HIGH — core logic fixes that enable firing under more realistic conditions

---

### Batch 5: Edge Cases, Dead Code & Polish
**Strategies:** All remaining strategies

**Theme:** Small fixes, cleanup, robustness improvements

| Strategy | Fix | Category | Severity |
|----------|-----|----------|----------|
| delta_iv_divergence | Fix `_gamma_regime_score` direction (inverted meaning) | Logic | medium |
| delta_iv_divergence | Remove dead `_check_decoupling()` method | Dead code | info |
| delta_iv_divergence | Clarify MIN_DIVERSION_STRENGTH rationale / consider lowering | Documentation | low |
| gamma_volume_convergence | Fix volume spike cross-contamination (use per-direction mean) | Bug | high |
| gamma_volume_convergence | Remove/comment dead GAMMA_SPIKE_RATIO constant | Dead code | low |
| gamma_volume_convergence | Add division-by-zero protection for rolling_avg ≈ 0 | Edge case | medium |
| ghost_premium | Fix Gate A to check actual ask_size OR rename/document what it checks | Specification | high |
| ghost_premium | Consider adding put-side evaluation (LONG-only limitation) | Enhancement | low |
| order_book_stacking | Consider median instead of mean for level averaging in SIS | Robustness | high |
| iv_gex_divergence | Audit ALL normalize() vmax values across file | Systematic | warning |
| iv_gex_divergence | De-duplicate gamma components in 10-component confidence | Redundancy | medium |
| vampire_momentum | Add minimum level count check for VAMP stability | Edge case | medium |
| vortex_compression_breakout | Verify Gate D exists and matches documentation | Completeness | info |
| whale_tracker | Increase participant filter ≤2 → ≤3 with confidence penalty | Scope | medium |
| extrinsic_flow | Initialize `self._regime_mismatch = False` in evaluate() | State safety | warning |

**Est effort:** 1h  
**Priority:** LOW-MEDIUM — polish after core fixes applied

---

## Execution Order

```
Batch 1 (Scale)     → Batch 2 (Crash/Logic) → Batch 3 (Normalization) 
         ↓                     ↓                      ↓
Batch 4 (Gates)              → Batch 5 (Polish)  → Rune QA
```

**Estimated total time:** 4.5 hours active work + verification

---

## Verification Plan Per Batch

After each batch:
1. `python3 -m py_compile <strategy_file>` for syntax check
2. Import test: `cd /home/hologaun/projects/syngex && python3 -c "from strategies.layer2 import delta_iv_divergence"` (adjust path per layer)
3. Diff output saved to `analysis/diff_batch_N.log`
4. Run existing tests if any: `pytest tests/test_strategies/ -v --tb=short`

---

## Success Criteria

- [ ] All critical bugs fixed (strategies crash/block immediately)
- [ ] All high-priority scale/calibration issues resolved
- [ ] No strategies produce confidence scores >1.0 or <0.0
- [ ] All strategies import cleanly without errors
- [ ] Rune QA passes with go/no-go per strategy
- [ ] Fixed strategies re-enabled in config/strategies.yaml if they were disabled
- [ ] Fix log documents every change with before/after context
