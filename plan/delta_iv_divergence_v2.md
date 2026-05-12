# delta_iv_divergence v2 — "Tail-Risk Divergence" Upgrade

**Strategy:** `strategies/layer2/delta_iv_divergence.py`
**Config:** `config/strategies.yaml` → `layer2.delta_iv_divergence`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `delta_iv_divergence` only monitors **ATM strikes**. True sentiment shifts often show up in **OTM strikes first** — smart money positions at the edges before the center reacts. The strategy also treats Delta and IV as independent variables, missing the **coupling relationship** between them. And it uses a fixed 2× risk target regardless of the volatility regime.

Synapse's proposal: upgrade to **Delta-IV Skew Gradient**, **Decoupling Coefficient**, **Gamma-Regime Filtering**, and **Volatility-Scaled Targets**.

---

## v2 Architecture

### New Confidence Components (7 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | **Skew Gradient** | 0.20 | **hard gate** | OTM vs ATM Delta-IV divergence (was ATM-only) |
| 2 | **Decoupling Coefficient** | 0.15 | **hard gate** | Delta-IV correlation collapse |
| 3 | Gamma Regime Filter | 0.15 | hard gate | Gamma density declining (was just magnitude bonus) |
| 4 | Divergence Strength | 0.10 | soft | Z-score divergence (unchanged, enhanced) |
| 5 | Volume-Weighted Conviction | 0.10 | soft | Option volume weighting (NEW) |
| 6 | Wall Proximity | 0.10 | soft | Proximity to gamma wall (NEW) |
| 7 | Regime Intensity | 0.05–0.10 | soft | Gamma magnitude scaling |

**New min confidence: 0.40** (up from 0.35 — higher bar for edge signals)

---

## Phase 1: Delta-IV Skew Gradient — The Edge Detection

**Goal:** Replace ATM-only monitoring with **OTM vs ATM skew comparison**. OTM moves lead ATM moves.

**Logic:**
1. For **LONG** (bullish accumulation): Compare OTM Put Delta/IV vs ATM Put Delta/IV
   - If OTM Put Delta is rising faster than ATM Put Delta → bullish accumulation in the wings
   - If OTM Put IV is rising faster than ATM Put IV → tail risk pricing in before center
2. For **SHORT** (bearish positioning): Compare OTM Call Delta/IV vs ATM Call Delta/IV
   - If OTM Call Delta is falling faster than ATM Call Delta → bearish accumulation in the wings
   - If OTM Call IV is rising faster than ATM Call IV → tail risk pricing in before center
3. **Hard gate:** `skew_divergence > 0.10` (OTM divergence is stronger than ATM divergence)
4. Compute skew divergence as: `|d(OTM_Delta)/dt - d(ATM_Delta)/dt| / max(|d(ATM_Delta)/dt|, 0.001)`

**Why this works:** Smart money positions at the edges first. OTM puts getting expensive while ATM is calm = institutional hedging. OTM calls getting expensive while ATM is calm = institutional shorting. The skew gradient catches this before the ATM data reflects the shift.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- ATM Put (420P): delta=-0.52, IV=0.60 → baseline
- OTM Put (395P): delta=-0.01, IV=1.05 → **elevated tail risk**
- ATM Call (420C): delta=0.48, IV=0.60 → baseline
- OTM Call (425C): delta=0.22, IV=0.65 → moderate call skew

If OTM Put IV goes from 0.80 → 1.05 while ATM stays at 0.60, that's a 75% skew increase → strong fear signal.

**Config params to add:**
```yaml
skew_otm_pct: 0.05                    # OTM strike distance (5% OTM)
skew_divergence_threshold: 0.10        # skew divergence must exceed this
```

**Rolling keys to add:** `KEY_OTM_DELTA_5M`, `KEY_OTM_IV_5M` in `rolling_keys.py`
**main.py change:** Compute OTM Delta/IV and push to rolling windows

---

## Phase 2: Delta-IV Decoupling Coefficient — The Conviction Filter

**Goal:** Detect when the correlation between Delta and IV **collapses** — this is the "decoupling event" that signals a true sentiment shift.

**Logic:**
1. Maintain rolling windows of both Delta and IV with timestamps
2. Compute rolling correlation over last 10 data points
3. Track correlation history (e.g., over last 30 points)
4. **Hard gate:** current correlation < rolling mean correlation × 0.5 (correlation has collapsed by ≥50%)
5. For **LONG:** Delta and IV should be **negatively correlated** (delta up, IV down = accumulation)
6. For **SHORT:** Delta and IV should be **negatively correlated** (delta down, IV up = distribution)
7. A sudden **break** in this negative correlation = the decoupling event = signal

**Why this works:** In a healthy market, Delta and IV are negatively correlated during accumulation/distribution phases. When this relationship **breaks**, it means the market structure is shifting — the "sentiment" has changed faster than the "fear" can adjust. This is the exact moment to enter.

**Config params to add:**
```yaml
decoupling_corr_window: 10             # window for correlation calculation
decoupling_history_window: 30          # window for correlation history
decoupling_threshold: 0.50             # correlation must collapse ≥50%
```

**Rolling key to add:** `KEY_DELTA_IV_CORR_5M` in `rolling_keys.py`

---

## Phase 3: Gamma-Regime Filtering — The Stability Check

**Goal:** Use gamma density gradient as a **regime filter** instead of just a confidence booster.

**Current behavior:** Net gamma magnitude adds 0.10–0.15 to confidence.

**New behavior:**
1. Compute gamma density around current price (same as iv_gex_divergence v2)
2. **Hard gate:** gamma density must be **declining** (moving into unstable zone)
   - current_density < rolling_mean_density × 0.70
3. If gamma density is **rising** or **stable** → the signal is a "fake-out" in a stable regime → skip
4. If gamma density is **declining** → we're moving into an unstable zone → signal is valid

**Why this works:** Divergences in high-gamma environments (stable) are often "fake-outs" — price grinds but doesn't snap. Divergences in low-gamma environments (unstable) are "breakouts" — price moves fast. Only trade divergences when the structural cushion is evaporating.

**Config params to add:**
```yaml
gamma_density_window_pct: 0.01         # ±1% window for gamma density
gamma_density_decline_threshold: 0.70  # density must decline ≥30%
```

---

## Phase 4: Volatility-Scaled Targets — The Dynamic Exit

**Goal:** Scale target distance based on IV expansion factor instead of fixed 2× risk.

**Current behavior:** `target = entry + risk × 2.0` — fixed regardless of volatility regime.

**New behavior:**
1. Compute `iv_expansion_factor = current_iv / rolling_mean_iv`
2. For **LONG:** `target_mult = 2.0 × iv_expansion_factor`
   - If IV is expanding (factor > 1.0) → wider target (capture volatility expansion)
   - If IV is contracting (factor < 1.0) → tighter target (quick profit)
3. For **SHORT:** `target_mult = 2.0 × iv_expansion_factor`
4. Cap target_mult at 4.0 (don't overextend)

**Why this works:** A divergence during massive IV expansion (e.g., panic buying puts) should have a wider target to capture the full volatility move. A divergence during calm IV should take profits quickly.

**Config params to add:**
```yaml
target_iv_expansion_mult: 2.0          # base multiplier
target_iv_expansion_cap: 4.0           # cap on multiplier
```

---

## Phase 5: Wall Proximity Bonus

**Goal:** Add confidence bonus when divergence occurs near a gamma wall.

**Logic:**
1. Get gamma walls via `gex_calc.get_gamma_walls(threshold=500_000)`
2. For **LONG:** bonus if nearest **put wall** is within 1% below price (support that will hold)
3. For **SHORT:** bonus if nearest **call wall** is within 1% above price (resistance that will hold)
4. Bonus: +0.10 confidence
5. If walls are far away → no bonus

**Config params to add:**
```yaml
wall_proximity_pct: 0.01               # within 1% of wall
wall_proximity_bonus: 0.10             # confidence bonus
```

---

## Phase 6: Confidence Recalculation

**New `_compute_confidence()` structure:**

```python
def _compute_confidence(
    self, skew_divergence, decoupling, gamma_decline,
    divergence_strength, iv_expansion, net_gamma, regime,
    wall_bonus, direction,
) -> float:
    # 1. Skew gradient (hard gate — 0.0 or 0.20)
    skew_conf = 0.20 if skew_divergence else 0.0

    # 2. Decoupling coefficient (hard gate — 0.0 or 0.15)
    decouple_conf = 0.15 if decoupling else 0.0

    # 3. Gamma regime filter (hard gate — 0.0 or 0.15)
    gamma_conf = 0.15 if gamma_decline else 0.0

    # 4. Divergence strength (soft — 0.0–0.10)
    div_conf = self._divergence_confidence(divergence_strength)

    # 5. Volume-weighted conviction (soft — 0.0–0.10)
    vol_conf = self._volume_conviction_confidence(iv_expansion)

    # 6. Wall proximity (soft — 0.0–0.10)
    wall_conf = wall_bonus

    # 7. Regime intensity (soft — 0.05–0.10)
    regime_conf = self._regime_confidence(net_gamma, direction)

    confidence = skew_conf + decouple_conf + gamma_conf + div_conf + vol_conf + wall_conf + regime_conf
    return min(1.0, max(0.0, confidence))
```

**Hard gates (all must pass for signal):**
- Skew divergence > 0.10 (edge signal confirmed)
- Decoupling coefficient < 0.5× (correlation collapsed)
- Gamma density declining (moving to unstable zone)

**Soft factors (boost confidence but don't block):**
- Divergence strength
- Volume-weighted conviction
- Wall proximity
- Regime intensity

---

## Phase 7: Config Updates

**Add to `config/strategies.yaml` under `layer2.delta_iv_divergence`:**

```yaml
delta_iv_divergence:
  enabled: true
  tracker:
    max_hold_seconds: 2700
  params:
    # === v1 params (kept for backwards compat) ===
    min_confidence: 0.40          # raised from 0.35
    stop_pct: 0.008
    target_risk_mult: 2.0

    # === v2 Tail-Risk Divergence params ===
    # Skew gradient
    skew_otm_pct: 0.05
    skew_divergence_threshold: 0.10

    # Decoupling coefficient
    decoupling_corr_window: 10
    decoupling_history_window: 30
    decoupling_threshold: 0.50

    # Gamma regime
    gamma_density_window_pct: 0.01
    gamma_density_decline_threshold: 0.70

    # Volatility-scaled targets
    target_iv_expansion_mult: 2.0
    target_iv_expansion_cap: 4.0

    # Wall proximity
    wall_proximity_pct: 0.01
    wall_proximity_bonus: 0.10
```

---

## Phase 8: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "direction": ...,
    "delta_trend": ...,
    "iv_trend": ...,
    "divergence_strength": ...,
    "delta_z": ...,
    "iv_z": ...,
    "net_gamma": ...,
    "regime": ...,
    "risk": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "skew_divergence": round(skew_div, 4),       # OTM vs ATM divergence
    "decoupling_coefficient": round(decouple, 4), # correlation collapse
    "gamma_density_current": current_density,
    "gamma_density_mean": mean_density,
    "gamma_density_decline_pct": decline_pct,
    "iv_expansion_factor": round(iv_expansion, 3),
    "target_mult": round(target_mult, 2),
    "wall_proximity_pct": wall_dist_pct,
    "nearest_wall_type": wall_type,
    "wall_proximity_bonus": wall_bonus,
}
```

---

## Phase 9: Rolling Window Key Additions

**Add to `strategies/rolling_keys.py`:**

```python
# --- Delta-IV Divergence v2 keys ---
KEY_OTM_DELTA_5M = "otm_delta_5m"
KEY_OTM_IV_5M = "otm_iv_5m"
KEY_DELTA_IV_CORR_5M = "delta_iv_corr_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute OTM Delta/IV (5% OTM from ATM) and push to rolling windows
- Compute Delta-IV correlation and push to rolling window

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add 3 new keys: `KEY_OTM_DELTA_5M`, `KEY_OTM_IV_5M`, `KEY_DELTA_IV_CORR_5M` |
| `main.py` | Add rolling key init + push OTM Delta/IV + Delta-IV correlation |
| `strategies/layer2/delta_iv_divergence.py` | Full v2 rewrite — skew gradient, decoupling, gamma filter, vol-scaled targets |
| `config/strategies.yaml` | Add 14 new params under `delta_iv_divergence` |

**No changes needed:** `strategies/layer2/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_skew_divergence()` computes OTM-vs-ATM Delta-IV skew divergence
2. ✅ `_check_decoupling()` computes Delta-IV correlation collapse
3. ✅ `_check_gamma_regime()` verifies declining gamma density
4. ✅ `_compute_vol_scaled_target()` scales target by IV expansion factor
5. ✅ `_check_wall_proximity()` adds +0.10 bonus near gamma walls
6. ✅ Hard gates: skew divergence AND decoupling AND gamma decline
7. ✅ Min confidence raised from 0.35 → 0.40
8. ✅ Rolling keys added and populated in main.py
9. ✅ New metadata fields in signal output
10. ✅ Config params added to strategies.yaml
11. ✅ Import passes: `python3 -c "from strategies.layer2.delta_iv_divergence import DeltaIVDivergence; print('OK')"`
12. ✅ Commit message: `feat(delta_iv): v2 Tail-Risk Divergence upgrade`

---

## Data Reference (from LEVEL2_DATA_SAMPLES.jsonl)

**Skew patterns (optionchain_parsed):**
- ATM Put (420P): delta=-0.52, IV=0.60 → baseline
- OTM Put (395P): delta=-0.01, IV=1.05 → **elevated tail risk** (skew = 0.45)
- ATM Call (420C): delta=0.48, IV=0.60 → baseline
- OTM Call (425C): delta=0.22, IV=0.65 → moderate call skew (skew = 0.05)

**Decoupling patterns:**
- Healthy accumulation: delta rising, IV falling → negative correlation
- Decoupling event: delta still rising but IV starts rising → correlation collapses
- This is the "smart money enters before fear" moment

**Gamma density patterns:**
- ATM strikes (420C, 420P): gamma=0.0627 → high density zone (stable)
- OTM strikes (425C): gamma=0.043 → medium density
- Deep OTM strikes (395P): gamma=0.0025 → low density zone (unstable)
- If price moves from 420 (gamma peak) to 435 (no gamma peak) → density drops → breakout likely

**Volume patterns:**
- OTM Call (425C): vol=56k → high conviction
- ATM Call (420C): vol=26k → moderate conviction
- Deep ITM Call (382.5C): vol=9 → low conviction (despite IV=1.98)

**Wall patterns:**
- Call wall at 420 (gamma=0.0627) → major resistance
- Put wall at 420 (gamma=0.0627) → major support
- Call wall at 425 (gamma=0.043) → secondary resistance
- Put wall at 395 (gamma=0.0025) → weak support
