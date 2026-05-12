# extrinsic_intrinsic_flow v2 — "Conviction-Master" Upgrade

**Strategy:** `strategies/full_data/extrinsic_intrinsic_flow.py`
**Config:** `config/strategies.yaml` → `full_data.extrinsic_intrinsic_flow`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `extrinsic_intrinsic_flow` is a solid "conviction tracker" but has 3 critical blind spots:
1. **Extrinsic change is static** — absolute % change from rolling avg tells us conviction _is_ high, but not how fast it's _arriving_. The most explosive moves happen when extrinsic ROC spikes.
2. **Volume is unweighted** — raw volume spike doesn't distinguish "passive" limit order rotation from "aggressive" market orders. A true conviction move is driven by market orders.
3. **No volatility surface confirmation** — a true conviction shift should see skew moving with delta. Without this, isolated extrinsic expansion can be noise.

Synapse's proposal: upgrade to **Extrinsic Acceleration (ROC of ROC)**, **Aggressor-Weighted Volume**, **Delta-Skew Coupling**, and **IV-Expansion Scaled Targets**.

---

## v2 Architecture

### New Confidence Components (7 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | Extrinsic Magnitude | 0.05–0.10 | soft | extrinsic change % (unchanged) |
| 2 | **Extrinsic Acceleration (ROC)** | 0.20–0.30 | **hard gate** | Extrinsic ROC of rolling window |
| 3 | **Aggressor-Weighted Volume** | 0.15–0.20 | **hard gate** | market_depth_agg aggressor ratio |
| 4 | **Delta-Skew Coupling** | 0.15–0.20 | **hard gate** | Skew moving with extrinsic change |
| 5 | Volume Spike | 0.05–0.10 | soft | volume ratio (unchanged) |
| 6 | Volume Direction | 0.05–0.10 | soft | volume trend (unchanged) |
| 7 | Net Gamma | 0.05–0.10 | soft | regime quality (unchanged) |

**New min confidence: 0.35** (up from 0.25 — higher bar for conviction signals)

---

## Phase 1: Extrinsic Acceleration (ROC of ROC) — The Leading Indicator

**Goal:** Replace absolute extrinsic change % with **Extrinsic Acceleration** — signal only valid if extrinsic change is accelerating.

**Current behavior:** `extrinsic_change_pct = (current - mean) / mean`. Threshold: >3% for expansion, <-10% for collapse. Static.

**New behavior:**
1. Compute extrinsic ROC: `extrinsic_roc = (current_extrinsic - extrinsic_5_ticks_ago) / abs(extrinsic_5_ticks_ago)`
2. Compute extrinsic acceleration: `extrinsic_accel = (extrinsic_roc - extrinsic_roc_5_ago) / abs(extrinsic_roc_5_ago)`
3. For **expansion** signals: extrinsic_accel > 0.10 (accelerating upward ≥10%)
4. For **collapse/fade** signals: extrinsic_accel < -0.10 (accelerating downward ≥10%)
5. **Hard gate:** |extrinsic_accel| > EXTRINSIC_ACCEL_THRESHOLD (0.10)

**Why this works:** A slow extrinsic drift can persist for hours without a price move. The moment extrinsic ROC spikes is the exact moment "new money" floods the market. This transforms the strategy from "conviction tracker" to "conviction hunter."

**Rolling key to add:** `KEY_EXTRINSIC_ROC_5M` in `rolling_keys.py`
**main.py change:** Compute extrinsic ROC and acceleration, push to rolling window

---

## Phase 2: Aggressor-Weighted Volume — The Real Volume Check

**Goal:** Replace raw volume spike with **aggressor-weighted volume** (market order ratio).

**Current behavior:** Checks volume ratio (latest / mean) > 1.30. Doesn't distinguish passive limit orders from aggressive market orders.

**New behavior:**
1. Read `data.get("market_depth_agg", {})` — contains "bids" and "asks" with participant info
2. Compute aggressor ratio: `aggressor_ratio = market_order_volume / total_volume`
3. For **LONG** (bullish): ask-side aggressor ratio > 0.60 (aggressive buyers)
4. For **SHORT** (bearish): bid-side aggressor ratio > 0.60 (aggressive sellers)
5. For **FADE** (collapse): any aggressor ratio is acceptable (money leaving)
6. **Hard gate:** aggressor_ratio > AGGRESSOR_THRESHOLD (0.55) for expansion signals

**Why this works:** A volume spike driven by limit orders (passive) is just market rotation. A volume spike driven by market orders (aggressive) is real conviction. This distinguishes "noise" from "signal."

**Implementation details:**
```python
def _check_aggressor_volume(self, data, direction):
    """Check if volume is driven by aggressive market orders."""
    depth = data.get("market_depth_agg", {})
    if not depth:
        return True  # No depth data = pass (backwards compat)
    
    bids = depth.get("bids", [])
    asks = depth.get("asks", [])
    
    # Sum bid/ask sizes to estimate aggressor flow
    bid_total = sum(b.get("size", 0) for b in bids)
    ask_total = sum(a.get("size", 0) for a in asks)
    total = bid_total + ask_total
    
    if total == 0:
        return True
    
    if direction == "LONG":
        # Bullish: aggressive buying = ask-side dominates
        aggressor_ratio = ask_total / total
    elif direction == "SHORT":
        # Bearish: aggressive selling = bid-side dominates
        aggressor_ratio = bid_total / total
    else:
        # FADE: any direction, just need volume
        aggressor_ratio = max(bid_total, ask_total) / total
    
    return aggressor_ratio > 0.55
```

---

## Phase 3: Delta-Skew Coupling — The Regime Confirmation

**Goal:** Cross-reference extrinsic change with **IV Skew movement**.

**Current behavior:** No skew check. Extrinsic and skew treated as separate entities.

**New behavior:**
1. Get `KEY_IV_SKEW_5M` rolling window
2. Compute skew ROC: `skew_roc = (current_skew - skew_5_ago) / abs(skew_5_ago)`
3. For **LONG** (bullish expansion): skew should be normalizing from negative toward zero (skew_roc > 0)
4. For **SHORT** (bearish expansion): skew should be normalizing from positive toward zero (skew_roc < 0)
5. For **FADE** (collapse): skew direction doesn't matter (money leaving)
6. **Hard gate:** skew must move in same direction as extrinsic expansion

**Why this works:** In a true conviction shift, extrinsic expansion and IV skew move in lockstep. If extrinsic is expanding but skew is flat, it's likely a "fake" move driven by a single strike or passive rotation. Skew coupling confirms the entire volatility surface is agreeing.

**Implementation details:**
```python
def _check_delta_skew_coupling(self, rolling_data, direction):
    skew_window = rolling_data.get(KEY_IV_SKEW_5M)
    if skew_window is None or skew_window.count < 5:
        return True  # No skew data = pass (backwards compat)
    
    current_skew = skew_window.latest
    avg_skew = skew_window.mean
    if current_skew is None or avg_skew is None or avg_skew == 0:
        return True
    
    skew_roc = (current_skew - avg_skew) / abs(avg_skew)
    
    if direction == "LONG":
        # Bullish expansion: skew normalizing from negative toward zero
        return skew_roc > 0
    elif direction == "SHORT":
        # Bearish expansion: skew normalizing from positive toward zero
        return skew_roc < 0
    else:
        # FADE: skew direction doesn't matter
        return True
```

---

## Phase 4: IV-Expansion Scaled Targets — The Dynamic Exit

**Goal:** Replace fixed 1.6× risk target with **IV-expansion scaled targets**.

**Current behavior:** `target = entry ± TARGET_PCT` (fixed 0.8%)

**New behavior:**
1. Get `KEY_ATM_IV_5M` rolling window
2. Compute `iv_factor = current_iv / mean_iv`
3. For **expansion** signals: `target = entry ± risk * 1.6 * iv_factor`
4. For **fade** signals: `target = entry ± risk * 1.2 * iv_factor` (fades are shorter trades)
5. Cap target at 2.5× risk (don't overextend)
6. Minimum target: 0.5% from entry

**Why this works:** Conviction shifts are often accompanied by IV expansion (volatility crush or explosion). Scale targets to capture the full move. Fade signals should be shorter (1.2× base) since they're mean-reversion plays.

**Config params:**
```yaml
target_iv_expansion_mult: 1.6
target_iv_expansion_fade_mult: 1.2
target_iv_expansion_cap: 2.5
target_min_pct: 0.005
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence_v2()` structure (7 components, unified for all signal types):**

```python
def _compute_confidence_v2(
    self, extrinsic_change_pct, extrinsic_accel,
    aggressor_ratio, skew_coupling,
    vol_ratio, vol_trend, net_gamma, signal_type,
) -> float:
    # 1. Extrinsic magnitude (soft — 0.05–0.10)
    ext_conf = self._extrinsic_confidence(extrinsic_change_pct, signal_type)
    
    # 2. Extrinsic acceleration (hard gate — 0.0 or 0.20–0.30)
    accel_conf = self._extrinsic_acceleration_confidence(extrinsic_accel, signal_type)
    
    # 3. Aggressor volume (hard gate — 0.0 or 0.15–0.20)
    agg_conf = self._aggressor_confidence(aggressor_ratio)
    
    # 4. Delta-skew coupling (hard gate — 0.0 or 0.15–0.20)
    skew_conf = self._skew_coupling_confidence(skew_coupling, signal_type)
    
    # 5. Volume spike (soft — 0.05–0.10)
    vol_conf = self._volume_spike_confidence(vol_ratio)
    
    # 6. Volume direction (soft — 0.05–0.10)
    vol_dir_conf = self._volume_direction_confidence(vol_trend, signal_type)
    
    # 7. Net gamma (soft — 0.05–0.10)
    gamma_conf = self._gamma_confidence(net_gamma)
    
    confidence = ext_conf + accel_conf + agg_conf + skew_conf + vol_conf + vol_dir_conf + gamma_conf
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

**Hard gates (all must pass for expansion signals):**
- Extrinsic acceleration (ROC of ROC > 10%)
- Aggressor volume (aggressor_ratio > 0.55)
- Delta-skew coupling (skew moves with extrinsic change)

**Hard gates (for fade signals):**
- Extrinsic acceleration (ROC of ROC < -10%)
- Delta-skew coupling (skew direction doesn't matter for fade)

**Soft factors (boost confidence):**
- Extrinsic magnitude (how extreme is the change)
- Volume spike (how much above average)
- Volume direction (aligned with signal)
- Net gamma strength

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `full_data.extrinsic_intrinsic_flow`:**

```yaml
extrinsic_intrinsic_flow:
  enabled: true
  tracker:
    max_hold_seconds: 10800        # 3hr (conviction signal)
  params:
    # === v1 params (kept for backwards compat) ===
    extrinsic_expansion_threshold: 0.03
    extrinsic_collapse_threshold: 0.10
    volume_spike_ratio: 1.30
    min_net_gamma: 500000.0
    stop_pct: 0.005
    target_pct: 0.008
    min_confidence: 0.35           # raised from 0.25
    max_confidence: 0.80
    min_data_points: 5

    # === v2 Conviction-Master params ===
    extrinsic_accel_threshold: 0.10       # 10% ROC of ROC for acceleration
    aggressor_threshold: 0.55             # 55% market order ratio
    target_iv_expansion_mult: 1.6
    target_iv_expansion_fade_mult: 1.2
    target_iv_expansion_cap: 2.5
    target_min_pct: 0.005
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "signal_type": ...,
    "extrinsic_change_pct": ...,
    "volume_ratio": ...,
    "volume_trend": ...,
    "net_gamma": ...,
    "stop_pct": ...,
    "target_pct": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "extrinsic_roc": round(extrinsic_roc, 4),
    "extrinsic_accel": round(extrinsic_accel, 4),
    "aggressor_ratio": round(aggressor_ratio, 3),
    "skew_roc": round(skew_roc, 4),
    "delta_skew_coupled": True/False,
    "iv_factor": round(iv_factor, 3),
    "target_mult": round(target_mult, 2),
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- Extrinsic/Intrinsic Flow v2 (Conviction-Master) ---
KEY_EXTRINSIC_ROC_5M = "extrinsic_roc_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute extrinsic ROC: `(current_extrinsic - extrinsic_5_ago) / abs(extrinsic_5_ago)`
- Compute extrinsic acceleration: `(extrinsic_roc - extrinsic_roc_5_ago) / abs(extrinsic_roc_5_ago)`
- Push to rolling window KEY_EXTRINSIC_ROC_5M

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_EXTRINSIC_ROC_5M` |
| `main.py` | Add rolling key init + extrinsic ROC + acceleration computation |
| `strategies/full_data/extrinsic_intrinsic_flow.py` | Full v2 rewrite — extrinsic acceleration, aggressor volume, skew coupling, IV targets |
| `config/strategies.yaml` | Add 6 new params under `extrinsic_intrinsic_flow` |

**No changes needed:** `strategies/full_data/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_extrinsic_acceleration()` detects extrinsic ROC of ROC > 10%
2. ✅ `_check_aggressor_volume()` validates aggressor_ratio > 0.55
3. ✅ `_check_delta_skew_coupling()` validates skew moves with extrinsic change
4. ✅ `_compute_iv_scaled_target()` scales target with IV expansion factor
5. ✅ Hard gates: extrinsic acceleration AND aggressor volume AND delta-skew coupling (for expansion)
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling key `KEY_EXTRINSIC_ROC_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.full_data.extrinsic_intrinsic_flow import ExtrinsicIntrinsicFlow; print('OK')"`
11. ✅ Commit message: `feat(extrinsic_flow): v2 Conviction-Master upgrade`

---

## Data Reference

**Extrinsic acceleration patterns:**
- Stale: extrinsic 1.00 → 1.01 → 1.00 → roc ≈ 0, accel ≈ 0 (no acceleration)
- Bullish burst: extrinsic 1.00 → 1.10 → 1.25 → roc = (1.10-1.00)/1.00 = 0.10, next roc = (1.25-1.10)/1.10 = 0.136, accel = (0.136-0.10)/0.10 = 0.36 (accelerating)
- Bearish burst: extrinsic 1.00 → 0.90 → 0.78 → similar acceleration downward
- Threshold: |accel| > 0.10 = acceleration confirmed

**Aggressor volume patterns:**
- Passive rotation: bid_total = 500, ask_total = 500 → ratio = 0.50 (no conviction)
- Bullish conviction: bid_total = 200, ask_total = 800 → ratio = 0.80 (aggressive buying)
- Bearish conviction: bid_total = 800, ask_total = 200 → ratio = 0.80 (aggressive selling)
- Threshold: ratio > 0.55 = real conviction

**Delta-skew coupling patterns:**
- Bullish expansion + skew normalizing: extrinsic expanding, skew -0.20 → -0.10 → converging ✅
- Bullish expansion + skew diverging: extrinsic expanding, skew -0.20 → -0.30 → NOT converging ❌
- Bearish expansion + skew normalizing: extrinsic expanding, skew 0.30 → 0.15 → converging ✅
- Bearish expansion + skew diverging: extrinsic expanding, skew 0.30 → 0.45 → NOT converging ❌
- Fade: skew direction doesn't matter (money leaving, not entering)

**IV expansion patterns:**
- IV contracting: 0.50 → 0.40 → factor=0.80 → target = 1.6 × 0.80 = 1.28× risk (tight)
- IV stable: 0.50 → 0.51 → factor=1.02 → target = 1.6 × 1.02 = 1.63× risk (baseline)
- IV expanding: 0.40 → 0.70 → factor=1.75 → target = 1.6 × 1.75 = 2.8× → capped at 2.5× risk
