# iv_skew_squeeze v2 — "Skew-Velocity" Upgrade

**Strategy:** `strategies/full_data/iv_skew_squeeze.py`
**Config:** `config/strategies.yaml` → `full_data.iv_skew_squeeze`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `iv_skew_squeeze` is a solid "state-based" skew mean-reversion strategy but has 3 critical blind spots:
1. **Skew can persist at extremes** — absolute skew value alone can stay extreme for hours. The most profitable trades happen when skew **snaps** back toward zero rapidly.
2. **Price stability on low volume is fragile** — a flat price with tiny volume can break in a tick. Stability on high volume = true conviction.
3. **Skew normalization without delta confirmation is weak** — skew easing alone doesn't confirm the move. Need delta flow to align.

Synapse's proposal: upgrade to **Skew Acceleration (ROC)**, **Volume-Weighted Stability**, **Delta-Skew Convergence**, and **IV-Expansion Scaled Targets**.

---

## v2 Architecture

### New Confidence Components (6 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | Skew Acceleration (ROC) | 0.20–0.30 | **hard gate** | Skew ROC (was absolute value) |
| 2 | Volume-Weighted Stability | 0.15–0.25 | **hard gate** | Price stability / volume intensity |
| 3 | Delta-Skew Convergence | 0.15–0.20 | **hard gate** | Delta flow aligning with skew normalization |
| 4 | Skew Extremity | 0.10–0.15 | soft | How far from zero (unchanged) |
| 5 | Volume Alignment | 0.05–0.10 | soft | No opposite volume spike (unchanged) |
| 6 | Net Gamma Strength | 0.05–0.10 | soft | Stable environment (unchanged) |

**New min confidence: 0.35** (up from 0.25 — higher bar for mean-reversion signals)

---

## Phase 1: Skew-Velocity (Skew ROC) — The Leading Indicator

**Goal:** Replace absolute skew threshold with **Skew Rate of Change (ROC)**. Signal only valid when skew is rapidly collapsing toward zero.

**Current behavior:** Skew must be beyond absolute threshold (-0.07 or +0.20) AND current skew must be moving toward zero (current > avg for negative, current < avg for positive).

**New behavior:**
1. Compute skew ROC: `skew_roc = (current_skew - skew_5_ticks_ago) / abs(skew_5_ticks_ago)`
2. For **LONG** (negative skew): skew_roc > 0 (skew becoming less negative = normalizing)
3. For **SHORT** (positive skew): skew_roc < 0 (skew becoming less positive = normalizing)
4. **Hard gate:** |skew_roc| > SKEW_ROC_THRESHOLD (0.05 = 5% ROC)

**Why this works:** A high skew can persist for hours. The moment the skew ROC spikes toward zero is the exact moment the "squeeze" releases. This is a leading indicator — it catches the snap before the price moves.

**Rolling key to add:** `KEY_SKEW_ROC_5M` in `rolling_keys.py`
**main.py change:** Compute skew ROC = (current_skew - skew_5_ago) / abs(skew_5_ago), push to rolling window

---

## Phase 2: Volume-Weighted Stability — The Conviction Filter

**Goal:** Replace simple price stability check with **Volume-Weighted Stability**.

**Current behavior:** `price_change_pct < 0.005` (5m price change < 0.5%). No volume consideration.

**New behavior:**
1. Compute `price_stability = 1.0 - (abs(price_change_pct) / PRICE_STABLE_THRESHOLD)`
2. Compute `volume_intensity = current_volume / rolling_avg_volume`
3. Compute `conviction_stability = price_stability / volume_intensity`
4. **Hard gate:** conviction_stability > 0.50 (price stable on meaningful volume)
5. If volume is extremely low (< 0.3× avg), stability is fragile → signal invalid

**Why this works:** A price that's flat on huge volume means big players are absorbing all the flow — that's a "coiled spring" signal. A price that's flat on tiny volume means there's no one trading — easily broken. Volume-weighted stability distinguishes real conviction from fragile equilibrium.

**Implementation details:**
```python
def _check_volume_weighted_stability(self, price_window, volume_window, direction):
    price_change = abs(price_window.change_pct or 0)
    price_stability = 1.0 - min(1.0, price_change / PRICE_STABLE_THRESHOLD)
    
    vol_ratio = volume_window.latest / volume_window.mean if volume_window.mean > 0 else 1.0
    
    # Extremely low volume = fragile stability
    if vol_ratio < 0.30:
        return False, 0.0
    
    conviction_stability = price_stability / vol_ratio
    
    # Hard gate: conviction_stability > 0.50
    if conviction_stability < 0.50:
        return False, 0.0
    
    return True, conviction_stability
```

---

## Phase 3: Delta-Skew Convergence — The Conviction Filter

**Goal:** Cross-reference skew normalization with **delta flow normalization**.

**Current behavior:** Skew normalization alone (skew moving toward zero). No delta check.

**New behavior:**
1. Get delta from `gex_calc.get_delta_by_strike()` or from rolling data
2. Compute delta ROC: `delta_roc = (current_delta - delta_5_ticks_ago) / abs(delta_5_ticks_ago)`
3. For **LONG** (negative skew normalizing): delta should be turning positive (delta_roc > 0)
4. For **SHORT** (positive skew normalizing): delta should be turning negative (delta_roc < 0)
5. **Hard gate:** delta must move in the same direction as skew normalization

**Why this works:** Skew tells us about fear/euphoria in pricing. Delta tells us about actual flow direction. When skew normalizes AND delta confirms (panic fading = delta turning positive), the signal has much higher conviction.

**Rolling key to add:** `KEY_DELTA_ROC_5M` in `rolling_keys.py` (if not already added)
**main.py change:** Compute delta ROC and push to rolling window

---

## Phase 4: IV-Expansion Scaled Targets — The Dynamic Exit

**Goal:** Replace fixed 1.6× risk target with **IV-expansion scaled targets**.

**Current behavior:** `target = entry ± TARGET_PCT` (fixed 0.8%)

**New behavior:**
1. Get ATM IV from `KEY_ATM_IV_5M` rolling window
2. Compute `iv_factor = current_iv / mean_iv`
3. For **LONG:** `target = entry + risk * 1.6 * iv_factor`
4. For **SHORT:** `target = entry - risk * 1.6 * iv_factor`
5. Cap target at 2.0× risk (don't overextend)
6. Minimum target: 0.5% (don't scalp for less than 0.5%)

**Why this works:** Skew normalization accompanied by IV expansion (volatility crush) means the market is releasing pent-up energy — the move will be bigger. Scale targets accordingly.

**Config params:**
```yaml
target_iv_expansion_mult: 1.6
target_iv_expansion_cap: 2.0
target_min_pct: 0.005
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence_v2()` structure (6 components, unified for LONG and SHORT):**

```python
def _compute_confidence_v2(
    self, current_skew, skew_roc, conviction_stability,
    delta_roc, skew_extremity, volume_ratio, net_gamma, direction,
) -> float:
    # 1. Skew acceleration (hard gate — 0.0 or 0.20–0.30)
    skew_accel = self._skew_accel_confidence(skew_roc, direction)
    
    # 2. Volume-weighted stability (hard gate — 0.0 or 0.15–0.25)
    vol_stability = self._vol_weighted_stability_confidence(conviction_stability)
    
    # 3. Delta-skew convergence (hard gate — 0.0 or 0.15–0.20)
    delta_conv = self._delta_skew_convergence_confidence(delta_roc, direction)
    
    # 4. Skew extremity (soft — 0.10–0.15)
    skew_ext = self._skew_extremity_confidence(skew_extremity, direction)
    
    # 5. Volume alignment (soft — 0.05–0.10)
    vol_align = self._volume_alignment_confidence(volume_ratio)
    
    # 6. Net gamma strength (soft — 0.05–0.10)
    gamma_str = self._gamma_strength_confidence(net_gamma)
    
    confidence = skew_accel + vol_stability + delta_conv + skew_ext + vol_align + gamma_str
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

**Hard gates (all must pass for signal):**
- Skew acceleration (ROC > 5% toward zero)
- Volume-weighted stability (conviction > 0.50)
- Delta-skew convergence (delta moves with skew)

**Soft factors (boost confidence):**
- Skew extremity (how extreme was the original skew)
- Volume alignment (no opposite volume spike)
- Net gamma strength (stable environment)

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `full_data.iv_skew_squeeze`:**

```yaml
iv_skew_squeeze:
  enabled: true
  tracker:
    max_hold_seconds: 600
  params:
    # === v1 params (kept for backwards compat) ===
    skew_extreme_positive: 0.20
    skew_extreme_negative: -0.07
    price_stable_threshold: 0.005
    min_net_gamma: 500000.0
    stop_pct: 0.005
    target_pct: 0.008
    min_confidence: 0.35          # raised from 0.25
    max_confidence: 0.80
    volume_spike_threshold: 1.5

    # === v2 Skew-Velocity params ===
    skew_roc_threshold: 0.05        # 5% ROC for skew acceleration
    vol_weighted_stability_min: 0.50 # min conviction stability
    vol_fragile_threshold: 0.30     # volume < 30% avg = fragile
    delta_roc_threshold: 0.05       # 5% ROC for delta confirmation
    target_iv_expansion_mult: 1.6
    target_iv_expansion_cap: 2.0
    target_min_pct: 0.005
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "skew_value": ...,
    "skew_rolling_avg": ...,
    "skew_direction": ...,
    "price_change_pct": ...,
    "net_gamma": ...,
    "volume_ratio": ...,
    "skew_normalizing": ...,
    "stop_pct": ...,
    "target_pct": ...,
    "risk_reward_ratio": ...,
    "trend": ...,

    # === v2 new fields ===
    "skew_roc": round(skew_roc, 4),
    "conviction_stability": round(conviction_stability, 3),
    "delta_roc": round(delta_roc, 4),
    "delta_skew_converging": True/False,
    "iv_factor": round(iv_factor, 3),
    "target_mult": round(target_mult, 2),
    "vol_intensity": round(vol_ratio, 2),
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- IV Skew Squeeze v2 (Skew-Velocity) ---
KEY_SKEW_ROC_5M = "skew_roc_5m"
KEY_DELTA_ROC_5M = "delta_roc_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute skew ROC: `(current_skew - skew_5_ago) / abs(skew_5_ago)`, push to KEY_SKEW_ROC_5M
- Compute delta ROC: `(current_delta - delta_5_ago) / abs(delta_5_ago)`, push to KEY_DELTA_ROC_5M

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_SKEW_ROC_5M` and `KEY_DELTA_ROC_5M` |
| `main.py` | Add rolling key init + skew ROC + delta ROC computation |
| `strategies/full_data/iv_skew_squeeze.py` | Full v2 rewrite — skew ROC, vol-weighted stability, delta-skew convergence, IV targets |
| `config/strategies.yaml` | Add 10 new params under `iv_skew_squeeze` |

**No changes needed:** `strategies/full_data/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_skew_acceleration()` detects skew ROC > 5% toward zero
2. ✅ `_check_volume_weighted_stability()` validates conviction stability > 0.50
3. ✅ `_check_delta_skew_convergence()` validates delta moves with skew normalization
4. ✅ `_compute_iv_scaled_target()` scales target with IV expansion factor
5. ✅ Hard gates: skew acceleration AND vol-weighted stability AND delta-skew convergence
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling keys `KEY_SKEW_ROC_5M` and `KEY_DELTA_ROC_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.full_data.iv_skew_squeeze import IVSkewSqueeze; print('OK')"`
11. ✅ Commit message: `feat(skew): v2 Skew-Velocity upgrade`

---

## Data Reference

**Skew ROC patterns:**
- Normal: skew goes -0.10 → -0.11 → -0.105 → roc ≈ 0 (stable, no acceleration)
- LONG squeeze: skew goes -0.20 → -0.15 → -0.08 → roc = (−0.08 − −0.15) / 0.15 = 0.47 (massive acceleration toward zero)
- SHORT squeeze: skew goes 0.30 → 0.25 → 0.12 → roc = (0.12 − 0.25) / 0.25 = −0.52 (massive deceleration toward zero)
- Threshold: |roc| > 0.05 = acceleration confirmed

**Volume-weighted stability patterns:**
- Stable on high volume: price_change=0.2%, vol_ratio=1.5 → stability=0.6, conviction=0.6/1.5=0.40 (borderline)
- Stable on extreme volume: price_change=0.1%, vol_ratio=2.0 → stability=0.8, conviction=0.8/2.0=0.40 (still borderline)
- Stable on normal volume: price_change=0.1%, vol_ratio=1.0 → stability=0.8, conviction=0.8/1.0=0.80 (strong)
- Stable on low volume: price_change=0.1%, vol_ratio=0.2 → fragile (below 0.30 threshold)
- Threshold: conviction > 0.50 = stable on meaningful volume

**Delta-skew convergence patterns:**
- LONG squeeze: skew -0.20 → -0.08 (normalizing), delta -0.50 → -0.20 → +0.10 (turning positive) → converging ✅
- LONG squeeze: skew -0.20 → -0.08 (normalizing), delta -0.50 → -0.60 → -0.70 (turning more negative) → NOT converging ❌
- SHORT squeeze: skew 0.30 → 0.12 (normalizing), delta +0.50 → +0.20 → -0.10 (turning negative) → converging ✅
- SHORT squeeze: skew 0.30 → 0.12 (normalizing), delta +0.50 → +0.60 → +0.70 (turning more positive) → NOT converging ❌

**IV expansion patterns:**
- IV contracting: 0.50 → 0.40 → factor=0.80 → target = 1.6 × 0.80 = 1.28× risk (tight)
- IV stable: 0.50 → 0.51 → factor=1.02 → target = 1.6 × 1.02 = 1.63× risk (baseline)
- IV expanding: 0.40 → 0.70 → factor=1.75 → target = 1.6 × 1.75 = 2.8× → capped at 2.0× risk
