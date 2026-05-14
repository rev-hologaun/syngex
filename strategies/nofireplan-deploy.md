# NoFire Plan — Phase 1 Deployment Sub-Plan

**Parent:** `strategies/nofireplan.md`
**Date:** 2026-05-13
**Status:** Pending approval

---

## Execution Overview

Phase 1 consists of **4 independent batch jobs**. Each job targets a specific config change across a subset of strategies.

**Order matters:** Run 1A → 1B → 1C → 1D (no dependencies, but this order groups similar edits).

**Total files touched:** ~29 (28 strategy files + engine.py + main.py config)
**Total edits:** ~52 individual parameter/config changes
**Estimated time:** 30-45 minutes (4 Forge jobs + verification)
**Revert:** `git revert <commit-hash>`

---

## Batch Job 1: Disable VAMP Validation Gates

**Scope:** 5 strategies — set `use_vamp_validation = False`
**Risk:** Lowest. VAMP validation is a soft gate that often fails silently.
**Files:**
1. `strategies/layer2/depth_imbalance_momentum.py`
2. `strategies/layer2/participant_divergence_scalper.py`
3. `strategies/layer2/participant_diversity_conviction.py`
4. `strategies/layer2/delta_volume_exhaustion.py`
5. `strategies/layer2/exchange_flow_asymmetry.py` (and concentration/imbalance if they have VAMP gates)

**Edit pattern:** Find `use_vamp_validation = params.get("use_vamp_validation", True)` and change default to `False`.
**Also:** Find the `if use_vamp_validation:` block and add `# Phase 1: disabled for data collection` comment, or change to `use_vamp_validation = False` unconditionally.

**Verification:** `grep -r "use_vamp_validation" strategies/layer2/ | grep True` — should return nothing.

---

## Batch Job 2: Halve Data Point Minimums

**Scope:** 8 strategies — halve `min_data_points` / `min_*_data_points` from 10→5 or 5→3
**Risk:** Low. Strategies become active sooner, but logic unchanged.
**Files:**
1. `strategies/layer2/participant_diversity_conviction.py` — `min_data_points: 10 → 5`
2. `strategies/full_data/sentiment_sync.py` — `min_data_points: 10 → 5`
3. `strategies/full_data/iron_anchor.py` — `min_data_points: 10 → 5`
4. `strategies/full_data/whale_tracker.py` — `min_conc_data_points: 10 → 5`
5. `strategies/full_data/skew_dynamics.py` — `min_psi_data_points: 10 → 5`
6. `strategies/full_data/smile_dynamics.py` — `min_omega_data_points: 10 → 5`
7. `strategies/full_data/extrinsic_flow.py` — `min_phi_data_points: 10 → 5`
8. `strategies/layer2/delta_iv_divergence.py` — `min_data_points: 5 → 3`

**Edit pattern:** Find `params.get("min_*_data_points", N)` where N ≥ 5, change N to N//2.
**Also:** Check for `count < min_*_data_points` comparisons to ensure they match.

**Verification:** `grep -r "min_data_points\|min_.*_data_points" strategies/ | grep -E ", [35]\)"` — should show all halved values.

---

## Batch Job 3: Lower Global Confidence Gate to 0.10

**Scope:** Global gate in `engine.py` + `main.py` — `0.15 → 0.10`
**Risk:** Low. The 11 firing strategies won't be affected (their confidence is well above 0.10).
**Files:**
1. `strategies/engine.py` — line 104: `min_confidence: float = 0.15` → `0.10`
2. `main.py` — line 382: `global_config.get("min_confidence", 0.15)` → `0.10`
3. `main.py` — line 569: `global_cfg.get("min_confidence", 0.15)` → `0.10`

**Edit pattern:** Change the default from `0.15` to `0.10` in all 3 locations.

**Verification:** `grep -r "0\.15" strategies/engine.py main.py | grep confidence` — should return zero results.

**Note:** Individual strategy `MIN_CONFIDENCE` constants can stay at 0.15 — they're internal checks. The global gate in engine.py is what actually blocks signals. Lowering the global gate is the single most important change.

---

## Batch Job 4: Add Regime-Soft Mode

**Scope:** 6 strategies — add regime misalignment handling
**Risk:** Moderate. Changes gate B/C behavior. Signals can fire in wrong regime with reduced confidence.
**Files:**
1. `strategies/full_data/extrinsic_flow.py` — Gate B
2. `strategies/full_data/gamma_breaker.py` — Gate B
3. `strategies/full_data/skew_dynamics.py` — Gate B
4. `strategies/full_data/smile_dynamics.py` — Gate B
5. `strategies/full_data/whale_tracker.py` — Gate C
6. `strategies/full_data/iron_anchor.py` — Gate B

**Edit pattern:**
- Add `regime_soft = params.get("regime_soft", True)` at top of evaluate()
- In regime gate methods, replace hard `return False` with confidence reduction:
  ```python
  if regime_soft:
      self._regime_mismatch = True  # flag for confidence reduction
      return True  # allow signal but reduce confidence
  ```
- In `_compute_confidence`, add:
  ```python
  if getattr(self, '_regime_mismatch', False):
      confidence *= 0.7  # 30% penalty for regime misalignment
  ```

**Verification:** Each strategy should have `regime_soft` parameter and the confidence penalty in its compute method.

---

## Post-Deployment Verification

After all 4 batches complete:

1. **Syntax check:** `python3 -c "import strategies.layer2.depth_imbalance_momentum; import strategies.full_data.sentiment_sync; print('OK')"` — import test
2. **Config diff:** `git diff --stat strategies/` — should show ~28 files changed
3. **Signal count baseline:** Let the orchestrator run for 1-2 hours, check if any previously-silent strategies now show signals in the heatmap
4. **Log check:** `grep -c "strategy_id" log/signals_TSLA.jsonl` — compare before/after

---

## Rollback Plan

If anything breaks:
```bash
git revert HEAD~4..HEAD --no-edit  # Revert all 4 batches
```

If only one batch has issues:
```bash
git revert <specific-commit-hash>
```

---

## Approval Required

Show this plan to Hologaun. Once approved, spawn 4 Forge sub-agents sequentially:
1. Forge Batch 1: VAMP validation off
2. Forge Batch 2: Data point minimums halved
3. Forge Batch 3: Confidence floor lowered
4. Forge Batch 4: Regime-soft mode added

Each batch must pass syntax/import verification before proceeding to the next.
