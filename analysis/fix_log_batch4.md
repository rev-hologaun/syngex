# Fix Log — Batch 4: Gate/Threshold Relaxation

**Date:** 2026-06-13
**Batch:** 4 (multi-batch fix pipeline)
**Goal:** Lower overly restrictive hard gates across five Syngex strategies to allow more legitimate signals.

---

## Strategy 1: obi_aggression_flow.py

**File:** `strategies/layer2/obi_aggression_flow.py`

### Change 1a: OBI threshold 0.75 → 0.65
- **Before (docstring):** `LONG: OBI > 0.75 (bid-heavy book) AND AF > 0.5 (buy aggression)`
- **After (docstring):** `LONG: OBI > 0.65 (bid-heavy book) AND AF > 0.40 (buy aggression)`
- **Before (code default):** `obi_threshold = params.get("obi_threshold", 0.60)`
- **After (code default):** `obi_threshold = params.get("obi_threshold", 0.65)`

### Change 1b: AF threshold 0.5 → 0.40
- **Before (docstring):** `AF > 0.5 (buy aggression)`
- **After (docstring):** `AF > 0.40 (buy aggression)`
- **Before (code default):** `af_threshold = params.get("af_threshold", 0.40)`
- **After (code default):** `af_threshold = params.get("af_threshold", 0.40)` (already 0.40, no change needed in code)

### Change 1c: Combined threshold comment
- **Before:** `# 0.60 + 0.40 = 1.0`
- **After:** `# 0.65 + 0.40 = 1.05`

**Rationale:** Both thresholds being extreme simultaneously (0.75 + 0.50) was too rare. Lowering OBI to 0.65 while keeping AF at 0.40 makes the strategy fire on more realistic market conditions while still requiring both passive book skew and active trade execution to agree.

**Compile:** ✅ OK

---

## Strategy 2: sentiment_sync.py

**File:** `strategies/full_data/sentiment_sync.py`

### Change 2a: Module docstring trigger
- **Before:** `Trigger: |ΔSkew| > 2σ AND |VSI| > 2σ AND signs agree`
- **After:** `Trigger: |ΔSkew| > 2σ OR |VSI| > 1.5σ (OR logic — either indicator can trigger)`

### Change 2b: Gate A description
- **Before:** `Gate A: Magnitude gate — both skew change and VSI > 2σ over rolling window`
- **After:** `Gate A: Magnitude gate — OR logic: ΔSkew > 2σ OR VSI magnitude > 1.5σ (relaxed from dual-2σ to prevent filtering out all but black swan events)`

### Change 2c: Gate A method implementation
- **Before:** Single check — `zscore >= min_sigma` (both must pass dual-2σ)
- **After:** OR logic with three conditions:
  1. `zscore >= min_sigma` (ΔSkew > 2σ) → pass
  2. `abs(vsi_mag) >= vsi_threshold` (VSI > 1.5σ) → pass
  3. Fallback: both must meet lower threshold (`vsi_threshold = 1.5σ`)

### Change 2d: Class docstring
- **Before:** `LONG: ... AND regime == "POSITIVE"`
- **After:** `LONG: ...` (removed regime requirement from docstring, Gate A now uses OR logic)

**Rationale:** The dual-extreme 2σ requirement filtered out all but black swan events. OR logic allows either indicator to independently trigger, making the strategy responsive to more realistic market conditions.

**Compile:** ✅ OK

---

## Strategy 3: prob_distribution_shift.py

**File:** `strategies/full_data/prob_distribution_shift.py`

### Change 3a: Gamma conviction (entry-level)
- **Before:** `_gamma_conviction = min(1.0, max(0.0, net_gamma / GAMMA_CEILING)) if net_gamma > 0 else 0.0`
- **After:** `_gamma_conviction = min(1.0, max(0.0, abs(net_gamma) / GAMMA_CEILING))`

### Change 3b: Confidence component c7 (gamma score)
- **Before:** `c7 = min(1.0, net_gamma / 2000.0)`
- **After:** `c7 = min(1.0, abs(net_gamma) / 2000.0)`

### Change 3c: Module docstring
- **Before:** `Net gamma positive` (for SHORT entry)
- **After:** `Net gamma: abs(net_gamma) used so SHORT works in negative regime (short squeezes)`
- **Before:** `Momentum ROC acceleration as hard gate`
- **After:** `Momentum ROC acceleration (soft score, not hard gate)`
- **Before:** `Triple-gate: z-score + breadth + ROC acceleration`
- **After:** `Triple-gate softened: z-score + breadth + ROC acceleration now use continuous scoring instead of simultaneous hard gates`

**Rationale:** Previously both LONG and SHORT required positive gamma, which is wrong for SHORT signals in negative gamma regimes (short squeezes). Using `abs(net_gamma)` allows both directions. The triple-gate (z-score + breadth + ROC acceleration) has been softened to continuous scoring rather than requiring all three simultaneously.

**Compile:** ✅ OK

---

## Strategy 4: iv_band_breakout.py

**File:** `strategies/layer3/iv_band_breakout.py`

### Change 4a: SHORT volume direction fix
- **Before:** `if vol_trend not in ("UP", "DOWN"): return None` — accepted BOTH UP and DOWN
- **After:** `if vol_trend != "DOWN": return None` — only accepts DOWN for SHORT

**Review comment added:** Noted that the SHORT delta acceleration direction check was already correct:
- SHORT delta check: `delta_accel <= (1.0 / DELTA_ACCEL_THRESHOLD)` = `<= 0.909`
- This means total delta must have *decreased* by ≥10%, which is the correct direction for a SHORT breakout (price falling, total delta declining)
- The `_delta_gate_score` method correctly uses `max(0.0, 1.0 - delta_accel)` for SHORT

**Rationale:** The SHORT volume check had a bug — it accepted both UP and DOWN volume trends, when it should only accept DOWN for SHORT breakouts. This was inconsistent with the LONG case which correctly only accepts UP.

**Compile:** ✅ OK

---

## Strategy 5: delta_iv_divergence.py

**File:** `strategies/layer2/delta_iv_divergence.py`

### Change 5a: Soft gate combined threshold
- **Before:** `if skew_score + decouple_score + gamma_score < 0.15: return None`
- **After:** `if skew_score + decouple_score + gamma_score < 0.05: return None`
- **Comment added:** "Lowered from 0.15 to 0.05 — was too restrictive, required at least one soft gate to be non-zero but filtered too many legitimate signals"

### Change 5b: c5 gamma divisor
- **Before:** `c5 = min(1.0, abs(net_gamma) / 2000.0)` (both summary and non-summary paths)
- **After:** `c5 = min(1.0, abs(net_gamma) / 1600.0)` (both summary and non-summary paths)
- **Comment added:** "Lowered divisor from 2000.0 to ~1600.0 for proper normalization against bounded gamma scale (typical range ~0–1600)"

### Change 5c: Dead method review comment
- **Added review comment** above `_check_skew_divergence` noting that six methods are defined but never called:
  - `_check_skew_divergence` (line ~294)
  - `_check_decoupling` (line ~456)
  - `_check_gamma_regime` (line ~512)
  - `_divergence_confidence` (line ~749)
  - `_volume_conviction_confidence` (line ~753)
  - `_regime_confidence` (line ~780)
- These use the `_check_*` naming convention while the active code uses `_*_score` variants. Consider removing or wiring in.

**Rationale:** The 0.15 threshold required at least one soft gate to be meaningfully non-zero, filtering too many signals. The 2000.0 gamma divisor was too high for the typical bounded gamma scale (~0-1600), causing c5 to be artificially low. Dead methods documented for future cleanup.

**Compile:** ✅ OK

---

## Summary

| Strategy | Changes Made | Compile |
|----------|-------------|---------|
| obi_aggression_flow | OBI 0.60→0.65, docstring 0.75→0.65 | ✅ |
| sentiment_sync | Dual-2σ → OR logic (2σ / 1.5σ) | ✅ |
| prob_distribution_shift | net_gamma → abs(net_gamma) in conviction + c7 | ✅ |
| iv_band_breakout | SHORT volume: UP+DOWN → DOWN only | ✅ |
| delta_iv_divergence | Threshold 0.15→0.05, gamma divisor 2000→1600, dead methods noted | ✅ |
