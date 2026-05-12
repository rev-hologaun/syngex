# iv_band_breakout v2 — "Breakout-Master" Upgrade

**Strategy:** `strategies/layer3/iv_band_breakout.py`
**Config:** `config/strategies.yaml` → `layer3.iv_band_breakout`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `iv_band_breakout` is a solid "coiled spring" strategy but has 3 blind spots:
1. **ATM-only IV check** — true coiling shows up in the entire volatility surface (OTM skew tightens), not just ATM IV. A breakout often begins when the skew itself compresses.
2. **Regime as confidence booster only** — breakouts in POSITIVE gamma are controlled trends; in NEGATIVE gamma they're explosive mean-reversion moves. The regime should be a **hard gate** with different behavior per regime.
3. **Delta deceleration is the setup, not the trigger** — we detect coiling but don't catch the "snap" moment. Need **Delta Acceleration** at the breakout to confirm the explosion.
4. **Fixed 1.0% target** — doesn't scale with the actual volatility expansion that accompanies a breakout.

Synapse's proposal: upgrade to **Skew Width Compression**, **Gamma-Regime Hard Gate**, **Delta-Acceleration Snap Detection**, and **IV-Expansion Scaled Targets**.

---

## v2 Architecture

### New Confidence Components (6 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | Skew Compression | 0.20 | **hard gate** | Skew width tightening (was ATM IV only) |
| 2 | Gamma-Regime Gate | 0.15 | **hard gate** | Regime-specific breakout behavior (was confidence booster) |
| 3 | Delta Acceleration | 0.15 | **hard gate** | Snap detection at breakout (was deceleration only) |
| 4 | Price Compression | 0.10 | soft | Tight range = more coiled (unchanged) |
| 5 | IV-Expansion Target | 0.10 | soft | Target scales with IV expansion (was fixed 1.0%) |
| 6 | Volume Confirmation | 0.05–0.10 | soft | Volume trend alignment (unchanged) |

**New min confidence: 0.35** (up from 0.25 — higher bar for breakout signals)

---

## Phase 1: Skew Width Compression — The Full-Surface Check

**Goal:** Replace ATM IV-only compression check with **skew width** monitoring — the gap between OTM Put IV and OTM Call IV.

**Logic:**
1. Get OTM Put IV at ATM - 5% strike and OTM Call IV at ATM + 5% strike
2. Compute `skew_width = abs(OTM_Put_IV - OTM_Call_IV)`
3. Maintain a rolling window of skew_width values using new key `KEY_SKEW_WIDTH_5M`
4. **Hard gate:** current skew_width is in bottom 25% of its rolling range (compression)
5. **Compression depth:** how far below p25 is the current skew_width — deeper = higher confidence

**Why this works:** A true "coiled spring" compresses the entire volatility surface, not just ATM. When the skew width tightens, it means the market has reached a consensus on volatility — the "quiet before the storm." This is a more robust signal than ATM-only IV because it accounts for the full surface.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- ATM Put (420P): IV=0.60
- OTM Put (395P): IV=1.05 → wide skew (0.45 gap)
- ATM Call (420C): IV=0.60
- OTM Call (425C): IV=0.65 → narrow call skew (0.05 gap)
- If skew goes from 0.45 → 0.15 → compression = coiled spring

**Config params to add:**
```yaml
skew_otm_pct: 0.05                    # OTM strike distance (5% OTM)
skew_compression_pct: 0.25            # skew must be in bottom 25% of range
```

**Rolling key to add:** `KEY_SKEW_WIDTH_5M` in `rolling_keys.py`
**main.py change:** Compute skew width (|OTM_Put_IV - OTM_Call_IV|) and push to rolling window

---

## Phase 2: Gamma-Regime Hard Gate — The Regime Filter

**Goal:** Use regime as a **hard gate** with different breakout behavior per regime.

**Current behavior:** Regime is a confidence booster (0.10 in POSITIVE, 0.05 otherwise). Strategy only works in POSITIVE gamma.

**New behavior:**
1. **POSITIVE gamma regime:** Breakouts are "controlled" — trend-following. Wider targets allowed (2.5× risk).
2. **NEGATIVE gamma regime:** Breakouts are "explosive" — mean-reversion. Tighter targets (1.5× risk).
3. **NEUTRAL regime:** Skip signals (no clear regime bias).
4. **Hard gate:** Regime must be POSITIVE or NEGATIVE (not NEUTRAL).

**Why this works:** Breakouts in POSITIVE gamma are driven by dealer hedging that amplifies the move (gamma feedback loop). Breakouts in NEGATIVE gamma are driven by panic — violent but short-lived. The strategy behavior should differ based on which type of breakout we're catching.

**Config params to add:**
```yaml
positive_gamma_target_mult: 2.5       # POS regime: wider target (trend)
negative_gamma_target_mult: 1.5       # NEG regime: tighter target (scalp)
```

---

## Phase 3: Delta-Acceleration Snap Detection — The Trigger

**Goal:** Add **Delta Acceleration** check at the breakout moment to confirm the "snap" from coiling to explosion.

**Current behavior:** Delta deceleration (coiling) is the setup, but there's no check for the actual breakout snap.

**New behavior:**
1. Compute delta acceleration at breakout: `delta_accel = current_delta / delta_5_ticks_ago`
2. For **LONG breakout:** delta_accel > 1.10 (delta accelerated ≥10% at breakout)
3. For **SHORT breakout:** delta_accel < 0.90 (delta decelerated ≥10% at breakout)
4. **Hard gate:** delta_accel must exceed threshold (confirms the snap)

**Why this works:** Delta deceleration = coiling (spring tightening). Delta acceleration = snap (spring releasing). We need BOTH: the coiling sets up the signal, the acceleration confirms the breakout is real and not a false move. This catches the exact moment of the "explosion."

**Config params to add:**
```yaml
delta_accel_threshold: 1.10           # delta must accelerate ≥10% at breakout
```

---

## Phase 4: IV-Expansion Scaled Targets — The Dynamic Exit

**Goal:** Replace fixed 1.0% target with **IV-expansion scaled targets**.

**Current behavior:** `target = entry * (1 ± 0.010)` — fixed regardless of volatility expansion.

**New behavior:**
1. Get ATM IV from current greeks_summary
2. Get rolling mean ATM IV from `KEY_ATM_IV_5M`
3. Compute `iv_expansion_factor = current_iv / mean_iv`
4. For **POSITIVE gamma:** `target_mult = 2.5 × iv_expansion_factor`
5. For **NEGATIVE gamma:** `target_mult = 1.5 × iv_expansion_factor`
6. Cap target_mult at 4.0 (don't overextend)
7. Minimum target: 0.5% (don't scalp for less than 0.5%)

**Why this works:** A breakout accompanied by massive IV expansion (e.g., IV goes from 0.40 → 0.80, factor=2.0) should have a much wider target to capture the full volatility move. A breakout with minimal IV expansion should take profits quickly.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- ATM Put (420P): IV=0.60 → baseline
- ATM Call (420C): IV=0.60 → baseline
- If IV goes from 0.40 → 0.80 → factor=2.0 → target = 2.5 × 2.0 = 5.0× risk (capped at 4.0)
- If IV goes from 0.60 → 0.65 → factor=1.08 → target = 2.5 × 1.08 = 2.7× risk

**Config params to add:**
```yaml
target_iv_expansion_mult: 2.5         # base multiplier for POS regime
target_iv_expansion_neg_mult: 1.5     # base multiplier for NEG regime
target_iv_expansion_cap: 4.0          # cap on multiplier
target_min_pct: 0.005                 # minimum 0.5% target
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence()` structure (unified for LONG and SHORT):**

```python
def _compute_confidence(
    self, skew_depth, delta_accel, iv_expansion,
    price_compression, net_gamma, regime, direction,
) -> float:
    # 1. Skew compression (hard gate — 0.0 or 0.20)
    skew_conf = 0.20 if skew_compressed else 0.0

    # 2. Gamma regime gate (hard gate — 0.0 or 0.15)
    regime_conf = 0.15 if regime_gate_passes else 0.0

    # 3. Delta acceleration (hard gate — 0.0 or 0.15)
    delta_conf = 0.15 if delta_accel_passes else 0.0

    # 4. Price compression (soft — 0.0–0.10)
    price_conf = self._price_compression_confidence(price_compression)

    # 5. IV expansion target quality (soft — 0.0–0.10)
    iv_conf = self._iv_expansion_confidence(iv_expansion)

    # 6. Volume confirmation (soft — 0.05–0.10)
    vol_conf = self._volume_confidence(vol_trend)

    confidence = skew_conf + regime_conf + delta_conf + price_conf + iv_conf + vol_conf
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

**Hard gates (all must pass for signal):**
- Skew compression (bottom 25% of rolling range)
- Gamma regime gate (POSITIVE or NEGATIVE, not NEUTRAL)
- Delta acceleration at breakout (snap confirmed)

**Soft factors (boost confidence but don't block):**
- Price compression tightness
- IV expansion factor
- Volume confirmation

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `layer3.iv_band_breakout`:**

```yaml
iv_band_breakout:
  enabled: true
  tracker:
    max_hold_seconds: 900
  params:
    # === v1 params (kept for backwards compat) ===
    delta_decel_ratio: 0.95
    price_compression_ratio: 0.40
    stop_pct: 0.005
    target_pct: 0.010
    min_confidence: 0.35          # raised from 0.25
    max_confidence: 0.85

    # === v2 Breakout-Master params ===
    # Skew compression
    skew_otm_pct: 0.05
    skew_compression_pct: 0.25

    # Gamma regime
    positive_gamma_target_mult: 2.5
    negative_gamma_target_mult: 1.5

    # Delta acceleration
    delta_accel_threshold: 1.10

    # IV-expansion targets
    target_iv_expansion_mult: 2.5
    target_iv_expansion_neg_mult: 1.5
    target_iv_expansion_cap: 4.0
    target_min_pct: 0.005
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "atm_strike": ...,
    "iv_compression_depth": ...,
    "price_compression_ratio": ...,
    "delta_deceleration_ratio": ...,
    "volume_trend": ...,
    "price_trend": ...,
    "net_gamma": ...,
    "regime": ...,
    "risk": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "skew_width_current": round(current_skew, 4),
    "skew_width_mean": round(mean_skew, 4),
    "skew_compression_depth": round(skew_depth, 4),
    "delta_acceleration": round(delta_accel, 4),
    "iv_expansion_factor": round(iv_expansion, 3),
    "target_mult": round(target_mult, 2),
    "regime_type": regime,              # "POSITIVE" or "NEGATIVE"
    "target_type": "scaled" or "fixed", # how target was determined
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- IV Band Breakout v2 (Breakout-Master) ---
KEY_SKEW_WIDTH_5M = "skew_width_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute skew width: |OTM_Put_IV - OTM_Call_IV| at ±5% from ATM
- Push to rolling window KEY_SKEW_WIDTH_5M

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_SKEW_WIDTH_5M` |
| `main.py` | Add rolling key init + push skew width |
| `strategies/layer3/iv_band_breakout.py` | Full v2 rewrite — skew compression, regime gate, delta accel, IV-scaled targets |
| `config/strategies.yaml` | Add 11 new params under `iv_band_breakout` |

**No changes needed:** `strategies/layer3/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_skew_compression()` computes OTM Put vs OTM Call IV skew width
2. ✅ `_check_gamma_regime()` enforces regime as hard gate (POSITIVE or NEGATIVE)
3. ✅ `_check_delta_acceleration()` detects snap at breakout moment
4. ✅ `_compute_iv_scaled_target()` scales target with IV expansion factor
5. ✅ Hard gates: skew compression AND gamma regime AND delta acceleration
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling key `KEY_SKEW_WIDTH_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.layer3.iv_band_breakout import IVBandBreakout; print('OK')"`
11. ✅ Commit message: `feat(iv_band): v2 Breakout-Master upgrade`

---

## Data Reference (from LEVEL2_DATA_SAMPLES.jsonl)

**Skew compression patterns (optionchain_parsed):**
- ATM Put (420P): IV=0.60, ATM Call (420C): IV=0.60 → skew=0.00 (compressed)
- OTM Put (395P): IV=1.05, OTM Call (425C): IV=0.65 → skew=0.40 (wide)
- If skew goes 0.40 → 0.20 → 0.05 → compression = coiled spring

**Gamma regime patterns:**
- POSITIVE gamma: dealer hedging amplifies moves → controlled trend → wider targets
- NEGATIVE gamma: dealer hedging fights moves → violent mean-reversion → tighter targets
- NEUTRAL gamma: no clear regime → skip signals

**Delta acceleration patterns:**
- Coiling: delta goes 0.80 → 0.60 → 0.40 (decelerating)
- Snap: delta goes 0.40 → 0.50 → 0.65 (accelerating) → breakout confirmed
- If delta keeps decelerating after breakout → false move → no signal

**IV expansion patterns:**
- ATM IV goes 0.40 → 0.80 → factor=2.0 → wide target (capture full expansion)
- ATM IV goes 0.60 → 0.65 → factor=1.08 → moderate target
- ATM IV goes 0.60 → 0.55 → factor=0.92 → tight target (no expansion)
