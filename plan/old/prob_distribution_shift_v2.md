# prob_distribution_shift v2 — "Momentum-Master" Upgrade

**Strategy:** `strategies/full_data/prob_distribution_shift.py`
**Config:** `config/strategies.yaml` → `full_data.prob_distribution_shift`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `prob_distribution_shift` is a solid "macro" leading indicator but has 3 critical blind spots:
1. **Momentum is static** — absolute Z-score tells us the distribution _has_ shifted, but not how fast. The most explosive moves happen when momentum ROC spikes.
2. **Breadth is naive** — counting strikes doesn't distinguish 10 strikes with 100 OI from 10 strikes with 100K OI. Need **capital-weighted breadth**.
3. **No volatility surface confirmation** — a true regime shift should see skew moving with delta. Without this, isolated delta shifts can be false signals.

Synapse's proposal: upgrade to **Momentum Acceleration (ROC of ROC)**, **Capital-Weighted Breadth**, **Delta-Skew Coupling**, and **IV-Expansion Scaled Targets**.

---

## v2 Architecture

### New Confidence Components (7 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | Z-Score Magnitude | 0.10–0.15 | soft | rolling momentum (unchanged) |
| 2 | **Momentum Acceleration (ROC)** | 0.20–0.30 | **hard gate** | Momentum ROC of rolling window |
| 3 | **Capital-Weighted Breadth** | 0.15–0.20 | **hard gate** | Total OI of contributing strikes |
| 4 | **Delta-Skew Coupling** | 0.15–0.20 | **hard gate** | Skew moving with delta shift |
| 5 | Duration | 0.05–0.10 | soft | consecutive signals (unchanged) |
| 6 | Volume Confirmation | 0.05–0.10 | soft | volume trend (unchanged) |
| 7 | Net Gamma | 0.05–0.10 | soft | regime quality (unchanged) |

**New min confidence: 0.35** (up from 0.25 — higher bar for macro signals)

---

## Phase 1: Momentum Acceleration (ROC of ROC) — The Leading Indicator

**Goal:** Replace absolute Z-score threshold with **Momentum Acceleration** — signal only valid if momentum is accelerating.

**Current behavior:** Z-score > 1.5σ for 2+ consecutive evaluations. Static threshold.

**New behavior:**
1. Compute momentum ROC: `momentum_roc = (current_momentum - momentum_5_ticks_ago) / abs(momentum_5_ticks_ago)`
2. Compute momentum acceleration: `momentum_accel = (momentum_roc - momentum_roc_5_ago) / abs(momentum_roc_5_ago)`
3. For **LONG** (bullish shift): momentum_accel > 0.10 (accelerating upward ≥10%)
4. For **SHORT** (bearish shift): momentum_accel < -0.10 (accelerating downward ≥10%)
5. **Hard gate:** |momentum_accel| > MOMENTUM_ACCEL_THRESHOLD (0.10)

**Why this works:** A slow momentum shift can persist for hours. The moment momentum ROC spikes is the exact moment "smart money" floods the market. This transforms the strategy from "regime monitor" to "momentum hunter."

**Rolling key to add:** `KEY_MOMENTUM_ROC_5M` in `rolling_keys.py`
**main.py change:** Compute momentum ROC and acceleration, push to rolling window

---

## Phase 2: Capital-Weighted Breadth — The Real Breadth Check

**Goal:** Replace naive strike count with **capital-weighted breadth** (OI-weighted).

**Current behavior:** Counts strikes contributing > 5% of total momentum. Doesn't distinguish 10 strikes with 100 OI from 10 strikes with 100K OI.

**New behavior:**
1. Sum total OI of contributing strikes: `capital_breadth = Σ(OI_at_contributing_strikes)`
2. Compute capital weight: `capital_weight = capital_breadth / TOTAL_CHAIN_OI`
3. **Hard gate:** capital_weight > CAPITAL_BREADTH_THRESHOLD (0.10 = 10% of chain OI)

**Why this works:** A shift involving 10 strikes with 100K OI each (1M total) is a massive institutional move. A shift involving 10 strikes with 100 OI each (1K total) is retail noise. Capital-weighted breadth distinguishes real institutional flow from noise.

**Implementation details:**
```python
def _compute_capital_weighted_breadth(self, greeks_summary, momentum, price):
    """Compute capital-weighted breadth of the momentum shift."""
    atm_strike = self._find_atm_strike(greeks_summary, price)
    if atm_strike is None:
        return 0.0, 0.0
    
    total_chain_oi = 0
    contributing_oi = 0
    total_abs_momentum = abs(momentum) if momentum != 0 else 1.0
    
    for strike_str, strike_data in greeks_summary.items():
        try:
            strike = float(strike_str)
        except (ValueError, TypeError):
            continue
        
        call_oi = strike_data.get("call_oi", 0) or 0
        put_oi = strike_data.get("put_oi", 0) or 0
        total_chain_oi += call_oi + put_oi
        
        call_delta = strike_data.get("call_delta_sum", 0.0)
        put_delta = strike_data.get("put_delta_sum", 0.0)
        net_delta = call_delta - put_delta
        if call_delta == 0 and put_delta == 0:
            continue
        
        distance = strike - atm_strike
        contribution = abs(net_delta * distance)
        
        if contribution > CONTRIBUTION_THRESHOLD * total_abs_momentum:
            contributing_oi += call_oi + put_oi
    
    capital_weight = contributing_oi / total_chain_oi if total_chain_oi > 0 else 0
    return capital_weight, contributing_oi
```

---

## Phase 3: Delta-Skew Coupling — The Regime Confirmation

**Goal:** Cross-reference delta momentum shift with **IV Skew movement**.

**Current behavior:** No skew check. Delta and skew treated as separate entities.

**New behavior:**
1. Get `KEY_IV_SKEW_5M` rolling window
2. Compute skew ROC: `skew_roc = (current_skew - skew_5_ago) / abs(skew_5_ago)`
3. For **LONG** (bullish shift): skew should be normalizing from negative toward zero (skew_roc > 0)
4. For **SHORT** (bearish shift): skew should be normalizing from positive toward zero (skew_roc < 0)
5. **Hard gate:** skew must move in same direction as delta shift

**Why this works:** In a true regime shift, delta flow and IV skew move in lockstep. If delta is shifting right but skew is flat, it's likely a "fake" move driven by a single strike. Skew coupling confirms the entire volatility surface is agreeing.

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
        # Bullish shift: skew should normalize from negative toward zero
        return skew_roc > 0
    else:
        # Bearish shift: skew should normalize from positive toward zero
        return skew_roc < 0
```

---

## Phase 4: IV-Expansion Scaled Targets — The Dynamic Exit

**Goal:** Replace fixed 1.6× risk target with **IV-expansion scaled targets**.

**Current behavior:** `target = entry ± TARGET_PCT` (fixed 0.8%)

**New behavior:**
1. Get ATM IV from `KEY_ATM_IV_5M` rolling window
2. Compute `iv_factor = current_iv / mean_iv`
3. For **LONG:** `target = entry + risk * 1.6 * iv_factor`
4. For **SHORT:** `target = entry - risk * 1.6 * iv_factor`
5. Cap target at 2.5× risk (don't overextend)
6. Minimum target: 0.5% from entry

**Why this works:** Distribution shifts are often accompanied by IV expansion (volatility crush or explosion). Scale targets to capture the full move.

**Config params:**
```yaml
target_iv_expansion_mult: 1.6
target_iv_expansion_cap: 2.5
target_min_pct: 0.005
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence_v2()` structure (7 components, unified for LONG and SHORT):**

```python
def _compute_confidence_v2(
    self, z_score, momentum_accel, capital_weight,
    skew_coupling, consecutive_count, vol_trend,
    net_gamma, direction,
) -> float:
    # 1. Z-score magnitude (soft — 0.10–0.15)
    z_conf = self._z_score_confidence(z_score)
    
    # 2. Momentum acceleration (hard gate — 0.0 or 0.20–0.30)
    accel_conf = self._momentum_acceleration_confidence(momentum_accel, direction)
    
    # 3. Capital-weighted breadth (hard gate — 0.0 or 0.15–0.20)
    breadth_conf = self._capital_breadth_confidence(capital_weight)
    
    # 4. Delta-skew coupling (hard gate — 0.0 or 0.15–0.20)
    coupling_conf = self._delta_skew_coupling_confidence(skew_coupling)
    
    # 5. Duration (soft — 0.05–0.10)
    dur_conf = self._duration_confidence(consecutive_count)
    
    # 6. Volume confirmation (soft — 0.05–0.10)
    vol_conf = self._volume_confidence(vol_trend)
    
    # 7. Net gamma (soft — 0.05–0.10)
    gamma_conf = self._gamma_confidence(net_gamma)
    
    confidence = z_conf + accel_conf + breadth_conf + coupling_conf + dur_conf + vol_conf + gamma_conf
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

**Hard gates (all must pass for signal):**
- Momentum acceleration (ROC of ROC > 10%)
- Capital-weighted breadth (capital_weight > 10%)
- Delta-skew coupling (skew moves with delta)

**Soft factors (boost confidence):**
- Z-score magnitude (how many σ from mean)
- Duration (consecutive signals)
- Volume confirmation
- Net gamma strength

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `full_data.prob_distribution_shift`:**

```yaml
prob_distribution_shift:
  enabled: true
  tracker:
    max_hold_seconds: 7200        # 2hr (macro signal)
  params:
    # === v1 params (kept for backwards compat) ===
    z_score_threshold: 1.5
    min_consecutive_signals: 2
    min_net_gamma: 500000.0
    stop_pct: 0.005
    target_pct: 0.008
    min_confidence: 0.35          # raised from 0.25
    max_confidence: 0.80
    min_strikes_with_data: 5
    contribution_threshold: 0.05

    # === v2 Momentum-Master params ===
    momentum_accel_threshold: 0.10    # 10% ROC of ROC for acceleration
    capital_breadth_threshold: 0.10   # 10% of chain OI
    target_iv_expansion_mult: 1.6
    target_iv_expansion_cap: 2.5
    target_min_pct: 0.005
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "momentum": ...,
    "z_score": ...,
    "consecutive_count": ...,
    "volume_trend": ...,
    "price_trend": ...,
    "net_gamma": ...,
    "regime": ...,
    "momentum_window_count": ...,
    "momentum_window_mean": ...,
    "momentum_window_std": ...,
    "stop_pct": ...,
    "target_pct": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "momentum_roc": round(momentum_roc, 4),
    "momentum_accel": round(momentum_accel, 4),
    "capital_breadth": round(capital_weight, 4),
    "contributing_oi": round(contributing_oi, 1),
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
# --- Prob Distribution Shift v2 (Momentum-Master) ---
KEY_MOMENTUM_ROC_5M = "momentum_roc_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute momentum ROC: `(current_momentum - momentum_5_ago) / abs(momentum_5_ago)`
- Compute momentum acceleration: `(momentum_roc - momentum_roc_5_ago) / abs(momentum_roc_5_ago)`
- Push both to rolling window KEY_MOMENTUM_ROC_5M

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_MOMENTUM_ROC_5M` |
| `main.py` | Add rolling key init + momentum ROC + acceleration computation |
| `strategies/full_data/prob_distribution_shift.py` | Full v2 rewrite — momentum acceleration, capital breadth, skew coupling, IV targets |
| `config/strategies.yaml` | Add 6 new params under `prob_distribution_shift` |

**No changes needed:** `strategies/full_data/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_momentum_acceleration()` detects momentum ROC of ROC > 10%
2. ✅ `_compute_capital_weighted_breadth()` validates capital_weight > 10%
3. ✅ `_check_delta_skew_coupling()` validates skew moves with delta shift
4. ✅ `_compute_iv_scaled_target()` scales target with IV expansion factor
5. ✅ Hard gates: momentum acceleration AND capital-weighted breadth AND delta-skew coupling
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling key `KEY_MOMENTUM_ROC_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.full_data.prob_distribution_shift import ProbDistributionShift; print('OK')"`
11. ✅ Commit message: `feat(dist_shift): v2 Momentum-Master upgrade`

---

## Data Reference

**Momentum acceleration patterns:**
- Stale: momentum 0.50 → 0.51 → 0.50 → roc ≈ 0, accel ≈ 0 (no acceleration)
- Bullish burst: momentum 0.50 → 0.70 → 1.00 → roc = (0.70-0.50)/0.50 = 0.40, next roc = (1.00-0.70)/0.70 = 0.43, accel = (0.43-0.40)/0.40 = 0.075 (accelerating)
- Bearish burst: momentum -0.50 → -0.70 → -1.00 → similar acceleration downward
- Threshold: |accel| > 0.10 = acceleration confirmed

**Capital-weighted breadth patterns:**
- 10 strikes × 100 OI = 1K total, chain total = 1M → weight = 0.001 (noise)
- 10 strikes × 10K OI = 100K total, chain total = 1M → weight = 0.10 (borderline)
- 10 strikes × 100K OI = 1M total, chain total = 1M → weight = 1.00 (massive institutional)
- Threshold: weight > 0.10 = meaningful capital flow

**Delta-skew coupling patterns:**
- Bullish shift + skew normalizing: delta shifting right, skew -0.20 → -0.10 → converging ✅
- Bullish shift + skew diverging: delta shifting right, skew -0.20 → -0.30 → NOT converging ❌
- Bearish shift + skew normalizing: delta shifting left, skew 0.30 → 0.15 → converging ✅
- Bearish shift + skew diverging: delta shifting left, skew 0.30 → 0.45 → NOT converging ❌

**IV expansion patterns:**
- IV contracting: 0.50 → 0.40 → factor=0.80 → target = 1.6 × 0.80 = 1.28× risk (tight)
- IV stable: 0.50 → 0.51 → factor=1.02 → target = 1.6 × 1.02 = 1.63× risk (baseline)
- IV expanding: 0.40 → 0.70 → factor=1.75 → target = 1.6 × 1.75 = 2.8× → capped at 2.5× risk
