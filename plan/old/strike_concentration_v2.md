# strike_concentration v2 — "Liquidity-Momentum" Upgrade

**Strategy:** `strategies/layer3/strike_concentration.py`
**Config:** `config/strategies.yaml` → `layer3.strike_concentration`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `strike_concentration` is a solid OI-strike strategy but has 4 blind spots:
1. **Slice "fake-out" vulnerability** — Volume spike alone can't distinguish a real liquidity vacuum breakout from a large limit order fill.
2. **Delta sign flip is too weak** — Delta turning positive/negative is just a direction check, not a conviction check. We need **Delta Acceleration (ROC)**.
3. **Bounce confidence blind to gamma magnitude** — A bounce off a strike with 10K OI is noise; a bounce off a strike with 1M OI is structural. Current code only uses OI rank, not absolute gamma magnitude.
4. **Fixed 1.5× risk target** — Doesn't scale with market speed. High-vol environments need wider targets; low-vol needs tighter.

Synapse's proposal: upgrade to **Liquidity Vacuum Slice Confirmation**, **Delta-Surge Validation**, **Gamma-Magnitude Bounce Weighting**, and **ATR-Normalized Micro-Scalp Targets**.

---

## v2 Architecture

### New Confidence Components

| Mode | Component | Weight | Type | Source |
|------|-----------|--------|------|--------|
| **Bounce** | OI Rank | 0.15–0.25 | soft | greeks_summary (existing) |
| **Bounce** | Proximity | 0.15–0.25 | soft | price vs strike (existing) |
| **Bounce** | Signal Strength | 0.15–0.20 | soft | candle/divergence (existing) |
| **Bounce** | **Gamma Magnitude** | 0.10–0.20 | **soft** | greeks_summary net_gamma at strike |
| **Bounce** | Regime Alignment | 0.10–0.15 | soft | regime (existing) |
| **Slice** | OI Rank | 0.15–0.25 | soft | greeks_summary (existing) |
| **Slice** | **Liquidity Vacuum** | 0.20–0.30 | **hard gate** | market_depth_agg |
| **Slice** | **Delta Acceleration** | 0.15–0.20 | **hard gate** | KEY_DELTA_ROC_5M (new key) |
| **Slice** | Body Ratio | 0.20–0.30 | soft | candle (existing) |
| **Slice** | Volume Spike | 0.10–0.15 | soft | volume (existing) |

**New min confidence: 0.35** (up from 0.25 — higher bar for strike signals)

---

## Phase 1: Liquidity Vacuum Slice Confirmation — The Hard Gate

**Goal:** Replace volume-only slice confirmation with **market depth liquidity vacuum detection**.

**Logic:**
1. Read `market_depth_agg` from `data` dict (contains aggregated bid/ask size data)
2. For **LONG slice** (through Call above): check that **ask side depth has collapsed** (liquidity vacuum above)
3. For **SHORT slice** (through Put below): check that **bid side depth has collapsed** (liquidity vacuum below)
4. **Hard gate:** bid/ask depth ratio must be extreme on the breakout side

**Implementation details:**
```python
def _check_liquidity_vacuum(self, data, direction):
    depth = data.get("market_depth_agg", {})
    if not depth:
        return False
    
    bid_levels = depth.get("bids", [])  # list of {price, size}
    ask_levels = depth.get("asks", [])  # list of {price, size}
    
    if direction == "LONG":
        # Check ask side (above price) — should be thin
        near_ask = [a for a in ask_levels if a["price"] <= price * 1.002]
        near_bid = [b for b in bid_levels if b["price"] >= price * 0.998]
        ask_total = sum(a["size"] for a in near_ask)
        bid_total = sum(b["size"] for b in near_bid)
        if bid_total == 0:
            return True  # No bids = free run up
        ratio = ask_total / bid_total
        return ratio < 0.30  # Ask side < 30% of bid side = vacuum
    else:
        # Check bid side (below price) — should be thin
        near_bid = [b for b in bid_levels if b["price"] <= price * 1.002]
        near_ask = [a for a in ask_levels if a["price"] >= price * 0.998]
        bid_total = sum(b["size"] for b in near_bid)
        ask_total = sum(a["size"] for a in near_ask)
        if ask_total == 0:
            return True  # No asks = free run down
        ratio = bid_total / ask_total
        return ratio < 0.30  # Bid side < 30% of ask side = vacuum
```

**Config params:**
```yaml
liquidity_vacuum_ratio: 0.30        # bid/ask ratio threshold for vacuum
depth_window_pct: 0.002             # ±0.2% price window for depth check
```

---

## Phase 2: Delta-Surge Validation — The Snap Detection

**Goal:** Replace delta sign flip with **Delta Acceleration (Rate of Change)**.

**Current behavior:** `_check_delta_positive_at_strike()` / `_check_delta_negative_at_strike()` — just checks if net_delta > 0 or < 0.

**New behavior:**
1. Compute delta ROC: `delta_accel = (current_delta - delta_5_ticks_ago) / abs(delta_5_ticks_ago)`
2. For **LONG slice:** delta_accel > 0.10 (delta accelerated ≥10%)
3. For **SHORT slice:** delta_accel < -0.10 (delta decelerated ≥10%)
4. **Hard gate:** delta_accel must exceed threshold (confirms the snap)

**Implementation details:**
```python
def _check_delta_surge(self, rolling_data, direction):
    window = rolling_data.get(KEY_DELTA_ROC_5M)
    if window is None or window.count < MIN_DATA_POINTS:
        return False
    
    roc = window.latest
    if roc is None:
        return False
    
    if direction == "LONG":
        return roc > 0.10  # Delta accelerating up
    else:
        return roc < -0.10  # Delta accelerating down
```

**Rolling key to add:** `KEY_DELTA_ROC_5M` in `rolling_keys.py`
**main.py change:** Compute delta ROC = (current_net_delta - delta_5_ago) / abs(delta_5_ago), push to rolling window

---

## Phase 3: Gamma-Magnitude Bounce Weighting — The Structural Signal

**Goal:** Replace OI-only bounce confidence with **gamma magnitude at the strike**.

**Current behavior:** `_compute_bounce_confidence()` uses OI rank (0.20–0.30) and OI volume (0.05–0.10). No gamma magnitude.

**New behavior:**
1. Get net_gamma at the bounce strike from `greeks_summary[strike]["net_gamma"]`
2. Compute gamma confidence: `gamma_conf = min(0.20, abs(net_gamma) * gamma_scale)`
3. Scale gamma_scale so that gamma of 1.0 → 0.20 confidence (high conviction)
4. Replace the OI volume component (0.05–0.10) with gamma magnitude (0.10–0.20)

**Implementation details:**
```python
def _gamma_bounce_confidence(self, strike, greeks_summary):
    """Get gamma magnitude confidence for a bounce at a specific strike."""
    strike_data = greeks_summary.get(strike, {})
    net_gamma = strike_data.get("net_gamma", 0)
    if net_gamma is None:
        net_gamma = 0
    
    # Gamma magnitude → confidence: abs(0.5) → 0.10, abs(2.0+) → 0.20
    abs_gamma = abs(net_gamma)
    if abs_gamma < 0.5:
        return 0.05
    elif abs_gamma >= 2.0:
        return 0.20
    else:
        # Linear interpolation between 0.5 and 2.0
        return 0.05 + 0.15 * ((abs_gamma - 0.5) / 1.5)
```

---

## Phase 4: ATR-Normalized Micro-Scalp Targets — The Dynamic Exit

**Goal:** Replace fixed 1.5× risk target with **ATR-normalized targets**.

**Current behavior:** `target = entry + risk * TARGET_RISK_MULT` (fixed 1.5×)

**New behavior:**
1. Compute ATR from `KEY_PRICE_5M` rolling window: `atr = price_window.std * sqrt(5)` (5-min ATR proxy)
2. Normalize ATR to percentage: `atr_pct = atr / price`
3. Determine ATR multiplier based on volatility regime:
   - High vol (ATR > 0.5%): target_mult = 2.0 × risk (wider scalp)
   - Medium vol (ATR 0.2–0.5%): target_mult = 1.5 × risk (baseline)
   - Low vol (ATR < 0.2%): target_mult = 1.0 × risk (tight scalp)
4. Cap minimum target: 0.2% from entry (don't scalp for pennies)

**Implementation details:**
```python
def _compute_atr_target(self, entry, risk, rolling_data, direction):
    window = rolling_data.get(KEY_PRICE_5M)
    if window is None or window.std is None:
        return entry + (risk * TARGET_RISK_MULT)  # fallback
    
    price = abs(entry)
    atr = window.std * math.sqrt(5)  # 5-min ATR proxy
    atr_pct = atr / price if price > 0 else 0
    
    if atr_pct > 0.005:
        mult = 2.0   # High vol
    elif atr_pct > 0.002:
        mult = 1.5   # Medium vol
    else:
        mult = 1.0   # Low vol
    
    target = entry + (risk * mult) if direction == "LONG" else entry - (risk * mult)
    
    # Minimum 0.2% target
    min_target = entry * 0.002 if direction == "LONG" else entry * -0.002
    if direction == "LONG":
        target = max(target, entry + min_target)
    else:
        target = min(target, entry - min_target)
    
    return target
```

**Config params:**
```yaml
atr_high_mult: 2.0
atr_medium_mult: 1.5
atr_low_mult: 1.0
atr_high_threshold: 0.005
atr_low_threshold: 0.002
target_min_pct: 0.002
```

---

## Phase 5: Confidence Recalculation

**New `_compute_bounce_confidence_v2()` structure (5 components):**

| Component | Weight | Type |
|-----------|--------|------|
| OI Rank | 0.15–0.25 | soft |
| Proximity | 0.15–0.25 | soft |
| Signal Strength (candle/divergence) | 0.15–0.20 | soft |
| **Gamma Magnitude** | 0.10–0.20 | **soft** |
| Regime Alignment | 0.10–0.15 | soft |

**New `_compute_slice_confidence_v2()` structure (6 components):**

| Component | Weight | Type |
|-----------|--------|------|
| **Liquidity Vacuum** | 0.20–0.30 | **hard gate** |
| **Delta Acceleration** | 0.15–0.20 | **hard gate** |
| OI Rank | 0.15–0.25 | soft |
| Body Ratio | 0.20–0.30 | soft |
| Volume Spike | 0.10–0.15 | soft |
| Regime Alignment | 0.10–0.15 | soft |

**Hard gates for slice:**
- Liquidity vacuum (bid/ask ratio < 0.30)
- Delta acceleration (ROC > 0.10 or < -0.10)

**Min confidence: 0.35** (up from 0.25)

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `layer3.strike_concentration`:**

```yaml
strike_concentration:
  enabled: true
  tracker:
    max_hold_seconds: 600
  params:
    # === v1 params (kept for backwards compat) ===
    top_oi_strikes_count: 3
    bounce_proximity_pct: 0.005
    slice_body_ratio: 0.30
    slice_volume_ratio: 1.20
    stop_pct_bounce: 0.003
    stop_pct_slice: 0.003
    target_risk_mult: 1.5
    min_confidence: 0.35          # raised from 0.25
    max_confidence: 0.85

    # === v2 Liquidity-Momentum params ===
    # Liquidity vacuum
    liquidity_vacuum_ratio: 0.30
    depth_window_pct: 0.002

    # ATR targets
    atr_high_mult: 2.0
    atr_medium_mult: 1.5
    atr_low_mult: 1.0
    atr_high_threshold: 0.005
    atr_low_threshold: 0.002
    target_min_pct: 0.002
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "signal_type": ...,
    "strike_rank": ...,
    "strike": ...,
    "total_oi": ...,
    "proximity_pct": ...,
    "net_gamma": ...,
    "regime": ...,
    "risk": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    # Bounce
    "gamma_magnitude": round(abs(strike_gamma), 4),
    "gamma_confidence": round(gamma_conf, 3),

    # Slice
    "liquidity_vacuum_ratio": round(vacuum_ratio, 3),
    "delta_acceleration": round(delta_roc, 4),
    "atr_pct": round(atr_pct, 5),
    "target_mult": round(target_mult, 2),
    "vol_regime": "high" / "medium" / "low",
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- Strike Concentration v2 (Liquidity-Momentum) ---
KEY_DELTA_ROC_5M = "delta_roc_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute delta ROC: get current net_delta from greeks_summary, get delta 5 ticks ago, compute `roc = (current - delta_5_ago) / abs(delta_5_ago)`
- Push to rolling window KEY_DELTA_ROC_5M

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_DELTA_ROC_5M` |
| `main.py` | Add rolling key init + delta ROC computation |
| `strategies/layer3/strike_concentration.py` | v2 rewrite — liquidity vacuum, delta surge, gamma magnitude, ATR targets |
| `config/strategies.yaml` | Add 9 new params under `strike_concentration` |

**No changes needed:** `strategies/layer3/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_liquidity_vacuum()` detects bid/ask depth collapse on breakout side
2. ✅ `_check_delta_surge()` detects delta ROC ≥10% at breakout
3. ✅ `_gamma_bounce_confidence()` scales confidence by gamma magnitude at strike
4. ✅ `_compute_atr_target()` scales target by ATR volatility regime
5. ✅ Hard gates: liquidity vacuum AND delta surge (for slice mode)
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling key `KEY_DELTA_ROC_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.layer3.strike_concentration import StrikeConcentration; print('OK')"`
11. ✅ Commit message: `feat(strike): v2 Liquidity-Momentum upgrade`

---

## Data Reference

**Liquidity vacuum patterns (market_depth_agg):**
- Normal: bid_total=500, ask_total=500 → ratio=1.0 (balanced)
- LONG vacuum: bid_total=500, ask_total=50 → ratio=0.10 (thin asks = free run up)
- SHORT vacuum: bid_total=50, ask_total=500 → ratio=0.10 (thin bids = free run down)
- Threshold: ratio < 0.30 = vacuum confirmed

**Delta acceleration patterns:**
- Normal: delta goes 0.30 → 0.32 → 0.31 → roc ≈ 0 (no acceleration)
- LONG surge: delta goes 0.30 → 0.45 → 0.60 → roc = (0.60-0.30)/0.30 = 1.00 (massive acceleration)
- SHORT surge: delta goes -0.30 → -0.45 → -0.60 → roc = (-0.60-(-0.30))/0.30 = -1.00 (massive deceleration)
- Threshold: |roc| > 0.10 = surge confirmed

**Gamma magnitude patterns (from greeks_summary):**
- Strike with 10K OI: net_gamma ≈ 0.2 → gamma_conf ≈ 0.06 (noise)
- Strike with 100K OI: net_gamma ≈ 1.0 → gamma_conf ≈ 0.13 (moderate)
- Strike with 1M OI: net_gamma ≈ 3.0 → gamma_conf = 0.20 (structural)

**ATR patterns:**
- High vol: price_std=2.0 → atr=4.5 → atr_pct=0.8% → mult=2.0 (wide scalp)
- Medium vol: price_std=1.0 → atr=2.2 → atr_pct=0.4% → mult=1.5 (baseline)
- Low vol: price_std=0.3 → atr=0.7 → atr_pct=0.1% → mult=1.0 (tight scalp)
