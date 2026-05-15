# SyngexSI — Task Plan for Forge
**Author:** @Archon
**Source Design:** `~/projects/syngex/syngexsi.md`
**Target:** `~/projects/syngex/strategies/layer1/gamma_flip_breakout.py`
**Analysis Script:** `~/projects/syngex/analysis/analyze_strategies_forge.py`

---

## Overview

Replace the "dangerous" `risk_norm` in `gamma_flip_breakout._compute_confidence()` with a **Structural Integrity (SI)** score. The SI is a composite of three independent validators:

1. **Momentum Validator (MV)** — delta density / volume efficiency
2. **Liquidity Anchor (LA)** — proximity to walls × order book depth
3. **Regime Coherence (RC)** — signal direction × regime alignment

The SI uses a **harmonic mean** so that a zero in any pillar heavily penalizes the total score.

---

## Data Flow Context

Before coding, understand the data pipeline:

- `rolling_data` dict is passed into each strategy's `evaluate()` call
- `rolling_data` contains `KEY_PRICE_5M` (price window) and `KEY_IV_SKEW_5M` (IV skew window)
- These come from `rolling_keys.py` which reads from the rolling window manager
- The orchestrator (`main.py`) populates `rolling_data` from the `GEXCalculator` and rolling window data
- `gex_calculator` provides `get_delta_density()`, `get_gamma_flip()`, `get_wall_classifications()`

---

## Task List

### Task 1: Add rolling data keys for SI
**File:** `~/projects/syngex/strategies/rolling_keys.py`
**Complexity:** Low
**Description:** Add new key constants for the SI data inputs:
- `KEY_DELTA_DENSITY_5M` — delta density rolling window
- `KEY_VOLUME_ZSCORE_5M` — volume z-score rolling window
- `KEY_ORDER_BOOK_DEPTH_5M` — order book depth rolling window
- `KEY_NET_GAMMA_5M` — net gamma rolling window (for regime coherence)

Add these constants alongside existing keys (`KEY_PRICE_5M`, `KEY_IV_SKEW_5M`, etc.).

---

### Task 2: Wire SI data into the orchestrator
**File:** `~/projects/syngex/main.py` (or the orchestrator file that populates `rolling_data`)
**Complexity:** Low
**Description:** In the data preparation loop, compute and add the new rolling data to `rolling_data`:
- `delta_density` — pull from `gex_calculator.get_delta_density()` at the current flip strike
- `volume_zscore` — compute rolling z-score of volume (5-min window)
- `order_book_depth` — pull from the market depth feed or GEX calculator
- `net_gamma_5m` — rolling mean of net_gamma over 5-min window

Add these to the `rolling_data` dict that gets passed to each strategy.

---

### Task 3: Implement the SI module (standalone)
**File:** `~/projects/syngex/strategies/si_component.py` (new file)
**Complexity:** Medium
**Description:** Create a standalone Python module with three classes:

#### 3a. `MomentumValidator`
- `__init__(self, volume_zscore: float, delta_density: float, price: float)`
- `compute(self) -> float` — returns 0.0–1.0
- Logic: `force_index = delta_density / max(volume_zscore, 1.0)`
- Score: if force_index > threshold → high momentum (1.0), else scales down
- Thresholds tunable via class constants

#### 3b. `LiquidityAnchor`
- `__init__(self, distance_to_wall_pct: float, wall_depth: float, book_depth: float, price: float)`
- `compute(self) -> float` — returns 0.0–1.0
- Logic: `wall_interaction = distance_to_wall_pct / max(wall_depth, 1.0)`
- Score: breakout through wall with depth = high integrity (1.0)
- Distance to wall should be small (near the wall) for fade setups

#### 3c. `RegimeCoherence`
- `__init__(self, signal_direction: str, regime: str, net_gamma: float)`
- `compute(self) -> float` — returns 0.0–1.0
- Logic: signal direction × regime sign alignment
- POSITIVE regime + SHORT signal = coherent (fade) → 1.0
- NEGATIVE regime + LONG signal = coherent (breakout) → 1.0
- Mismatched = 0.3 (low coherence)

#### 3d. `StructuralIntegrity` (orchestrator class)
- `__init__(self, mv: MomentumValidator, la: LiquidityAnchor, rc: RegimeCoherence)`
- `compute(self) -> float` — returns harmonic mean of the three scores
- `harmonic_mean = 3 / (1/mv + 1/la + 1/rc)` — handles zero gracefully (min 0.01)
- Weighted variant: `harmonic_mean = sum(w) / sum(w/score)` for tunable weights

---

### Task 4: Refactor gamma_flip_breakout — remove risk_norm, add SI
**File:** `~/projects/syngex/strategies/layer1/gamma_flip_breakout.py`
**Complexity:** Medium
**Description:** Two changes:

#### 4a. Update `_compute_confidence()` signature and logic
- Remove `risk` and `price` parameters (no longer needed for risk_norm)
- Add `si_score: float` parameter
- Remove the `risk_norm` calculation entirely
- Replace the 4-component average with a 3-component average:
  - `(gamma_norm + regime_norm + wall_norm) / 3.0` (no risk_norm)
- Multiply the result by `si_score` to modulate confidence based on structural integrity
- New formula: `confidence = ((gamma_norm + regime_norm + wall_norm) / 3.0) * si_score`
- Keep all other logic (gamma_norm, regime_norm, wall_norm) unchanged

#### 4b. Update all callers of `_compute_confidence()`
- There are 4 callers: `_short_fade`, `_long_fade`, `_long_breakout`, `_short_breakout`
- Each currently calls: `self._compute_confidence(risk, price, net_gamma, regime, side, flip_mid, confirmation_score)`
- Change to: `self._compute_confidence(net_gamma, regime, side, flip_mid, confirmation_score, si_score)`
- Pass `si_score` computed from the SI component

---

### Task 5: Wire SI computation into gamma_flip_breakout evaluate()
**File:** `~/projects/syngex/strategies/layer1/gamma_flip_breakout.py`
**Complexity:** Medium
**Description:** In each of the four signal methods (`_short_fade`, `_long_fade`, `_long_breakout`, `_short_breakout`), compute the SI score before calling `_compute_confidence()`:

For each method:
1. Extract SI data from `rolling_data`:
   ```python
   delta_density = rolling_data.get(KEY_DELTA_DENSITY_5M)
   volume_zscore = rolling_data.get(KEY_VOLUME_ZSCORE_5M)
   ```
2. Get distance to wall from existing `_find_target_wall()` call
3. Get order book depth (may need to pull from `gex_calculator` or rolling data)
4. Create the three SI sub-components and compute SI score
5. Pass `si_score` to `_compute_confidence()`

The SI score should be computed inside each method, using the same data that's already available in `rolling_data` and `gex_calc`.

---

### Task 6: Add SI score to signal metadata
**File:** `~/projects/syngex/strategies/layer1/gamma_flip_breakout.py`
**Complexity:** Low
**Description:** Add SI-related fields to the `metadata` dict in each Signal:
```python
"si_score": round(si_score, 3),
"si_momentum": round(mv_score, 3),
"si_liquidity": round(la_score, 3),
"si_regime": round(rc_score, 3),
```

This lets the analysis script track SI performance over time.

---

### Task 7: Validate with analysis script
**File:** `~/projects/syngex/analysis/analyze_strategies_forge.py`
**Complexity:** Low
**Description:** After running the updated system for a trading day, re-run the analysis to verify:
1. The Win% vs Confidence correlation has improved (higher confidence → higher win rate)
2. The "100% confidence with low win rate" anomaly is resolved
3. The `gamma_flip_breakout` performance metrics look reasonable
4. Check if the SI scores in metadata are being captured and analyzed

---

## Execution Order

Tasks must be done in this order (dependencies):

```
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7
```

Each task should be committed and tested before moving to the next.

---

## Task Batching Strategy

Send Forge tasks in batches of 2-3 to maximize throughput. Each task should be a separate `sessions_spawn` call with clear, focused instructions.

### Batch 1: Data Foundation (Tasks 1 + 2)
- Task 1: Add rolling data keys
- Task 2: Wire SI data into orchestrator

### Batch 2: SI Module (Task 3)
- Task 3: Implement standalone SI module (this is the biggest task, keep it alone)

### Batch 3: Integration (Tasks 4 + 5)
- Task 4: Refactor `_compute_confidence()`
- Task 5: Wire SI computation into evaluate()

### Batch 4: Polish & Validate (Tasks 6 + 7)
- Task 6: Add SI to metadata
- Task 7: Validation with analysis script

---

## Notes for Forge

- **Keep it small:** Each task should modify minimal files. Don't refactor unrelated code.
- **Don't break existing behavior:** The strategy must still emit signals with the same entry/exit logic. Only the confidence scoring changes.
- **Harmonic mean edge case:** If any component score is 0, the harmonic mean would be 0. Use a floor of 0.01 to prevent division by zero.
- **Weights:** Start with equal weights (1/3 each) for the harmonic mean. Hologaun can tune them later.
- **Imports:** Add new SI module imports to `gamma_flip_breakout.py` at the top of the file.
- **Tests:** If there's an existing test file for `gamma_flip_breakout`, update it. Otherwise, skip tests for now.
