# prob_weighted_magnet v2 — "Velocity-Magnet" Upgrade

**Strategy:** `strategies/full_data/prob_weighted_magnet.py`
**Config:** `config/strategies.yaml` → `full_data.prob_weighted_magnet`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `prob_weighted_magnet` is a solid "stealth accumulation" strategy but has 3 critical blind spots:
1. **Delta level is static** — absolute delta doesn't tell us if accumulation is accelerating. We need **Delta ROC (Rate of Change)**.
2. **Consolidation via price std is fragile** — low-volatility drifting looks like consolidation but can break in a tick. Need **liquidity vacuum confirmation**.
3. **No volatility surface context** — ignores IV skew which should tilt toward the magnet direction before price moves.
4. **Fixed target at strike level** — doesn't scale with gamma magnitude. A strike with 1M gamma is a stronger magnet than one with 10K.

Synapse's proposal: upgrade to **Delta-Acceleration (ROC)**, **Liquidity Vacuum Consolidation**, **Skew-Convergence Confirmation**, and **Gamma-Weighted Targets**.

---

## v2 Architecture

### New Confidence Components (7 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | OI Concentration | 0.10–0.15 | soft | greeks_summary (unchanged) |
| 2 | **Delta Acceleration (ROC)** | 0.20–0.30 | **hard gate** | gex_calc per-strike delta |
| 3 | **Liquidity Vacuum** | 0.15–0.20 | **hard gate** | market_depth_agg |
| 4 | **Skew Convergence** | 0.15–0.20 | **hard gate** | KEY_IV_SKEW_5M |
| 5 | Consolidation Tightness | 0.10–0.15 | soft | price_5m/30m range (unchanged) |
| 6 | Volume Profile | 0.05–0.10 | soft | volume trend (unchanged) |
| 7 | Distance to Target | 0.05–0.10 | soft | price to strike (unchanged) |

**New min confidence: 0.35** (up from 0.25 — higher bar for magnet signals)

---

## Phase 1: Delta-Acceleration (The Lead Indicator)

**Goal:** Replace absolute delta check with **Delta ROC** — signal only valid if delta is accelerating at the magnet strike.

**Current behavior:** Uses `abs(call_delta - put_delta)` as a static threshold (`> 0`). No acceleration check.

**New behavior:**
1. Get per-strike delta from `gex_calc.get_delta_by_strike(magnet_strike)`
2. Get delta from rolling window `KEY_MAGNET_DELTA_5M` (delta 5 ticks ago)
3. Compute delta ROC: `delta_roc = (current_delta - delta_5_ago) / abs(delta_5_ago)`
4. For **LONG** (bullish accumulation): delta_roc > 0.05 (delta accelerating up ≥5%)
5. For **SHORT** (bearish distribution): delta_roc < -0.05 (delta accelerating down ≥5%)
6. **Hard gate:** |delta_roc| > DELTA_ROC_THRESHOLD (0.05)

**Why this works:** A high delta can persist for hours. The moment delta ROC spikes is the exact moment "smart money" begins pushing. This transforms the strategy from "level watcher" to "momentum anticipator."

**Rolling key to add:** `KEY_MAGNET_DELTA_5M` in `rolling_keys.py`
**main.py change:** Compute per-strike delta ROC at magnet strikes, push to rolling window

---

## Phase 2: Liquidity Vacuum Consolidation — The Real Coiling Check

**Goal:** Replace price-range-only consolidation with **order book liquidity vacuum** confirmation.

**Current behavior:** `consolidation_ratio = range_5m / range_30m < 0.50` — price range must be tight.

**New behavior:**
1. Read `market_depth_agg` from `data` dict
2. For **LONG magnet** (price consolidating below magnet strike): check that **ask side depth is thin** (liquidity vacuum above = price can easily break up)
3. For **SHORT magnet** (price consolidating above magnet strike): check that **bid side depth is thin** (liquidity vacuum below = price can easily break down)
4. **Hard gate:** bid/ask ratio < 0.30 on the consolidation side

**Why this works:** A price that's flat with thin order book on the breakout side = coiled spring ready to explode. A price that's flat with thick order book = genuine resistance/support. Liquidity vacuum confirms the "stealth" state.

**Implementation details:**
```python
def _check_liquidity_vacuum(self, data, price, direction):
    depth = data.get("market_depth_agg", {})
    if not depth:
        return True  # No depth data = pass (backwards compat)
    
    bids = depth.get("bids", [])
    asks = depth.get("asks", [])
    
    # Sum depth within ±0.2% of price
    bid_total = sum(b["size"] for b in bids if abs(b["price"] - price) / price < 0.002)
    ask_total = sum(a["size"] for a in asks if abs(a["price"] - price) / price < 0.002)
    
    if direction == "LONG":
        # For bullish magnet: ask side should be thin (easy to break up)
        if ask_total == 0:
            return True
        ratio = ask_total / bid_total if bid_total > 0 else 0
        return ratio < 0.30
    else:
        # For bearish magnet: bid side should be thin (easy to break down)
        if bid_total == 0:
            return True
        ratio = bid_total / ask_total if ask_total > 0 else 0
        return ratio < 0.30
```

---

## Phase 3: Skew-Convergence Confirmation — The Volatility Surface Signal

**Goal:** Cross-reference magnet formation with **IV Skew** tilting toward the target direction.

**Current behavior:** No skew check at all.

**New behavior:**
1. Get `KEY_IV_SKEW_5M` rolling window
2. Compute skew ROC: `skew_roc = (current_skew - skew_5_ago) / abs(skew_5_ago)`
3. For **LONG magnet** (bullish accumulation): skew should be normalizing from negative toward zero (skew_roc > 0)
4. For **SHORT magnet** (bearish distribution): skew should be normalizing from positive toward zero (skew_roc < 0)
5. **Hard gate:** skew must be moving in the magnet direction

**Why this works:** If a bullish magnet is forming (smart money buying calls below price), we should see the IV skew start to normalize from negative (fear) toward neutral. This is a leading signal — skew tilts before price moves.

**Implementation details:**
```python
def _check_skew_convergence(self, rolling_data, direction):
    skew_window = rolling_data.get(KEY_IV_SKEW_5M)
    if skew_window is None or skew_window.count < 5:
        return True  # No skew data = pass (backwards compat)
    
    current_skew = skew_window.latest
    avg_skew = skew_window.mean
    if current_skew is None or avg_skew is None or avg_skew == 0:
        return True
    
    skew_roc = (current_skew - avg_skew) / abs(avg_skew)
    
    if direction == "LONG":
        # Bullish magnet: skew should normalize from negative toward zero
        # current_skew should be > avg_skew (less negative)
        return current_skew > avg_skew
    else:
        # Bearish magnet: skew should normalize from positive toward zero
        # current_skew should be < avg_skew (less positive)
        return current_skew < avg_skew
```

---

## Phase 4: Gamma-Weighted Targets — The Magnet Strength Scaling

**Goal:** Replace fixed 1.5× risk target with **gamma-weighted targets**.

**Current behavior:** `target = entry ± risk × 1.5` (fixed 1.5×)

**New behavior:**
1. Get gamma magnitude at the magnet strike from `gex_calc.get_strike_net_gamma(magnet_strike)`
2. Compute gamma scaling: `gamma_scale = min(2.0, abs(gamma_at_strike) / GAMMA_SCALE_BASE)`
3. For **LONG magnet:** `target_mult = 1.5 × gamma_scale` (higher gamma = wider target)
4. For **SHORT magnet:** `target_mult = 1.5 × gamma_scale` (higher gamma = wider target)
5. Cap target_mult at 3.0 (don't overextend)
6. Minimum target: 0.5% from entry

**Why this works:** A strike with 1M gamma is a much stronger magnet than one with 10K gamma. Higher gamma = more dealer hedging pressure = price more likely to overshoot the strike. Scale targets accordingly.

**Implementation details:**
```python
def _compute_gamma_weighted_target(self, entry, risk, magnet_strike, gex_calc, direction):
    try:
        gamma_at_strike = gex_calc.get_strike_net_gamma(magnet_strike)
    except Exception:
        gamma_at_strike = 0.0
    
    # Gamma scale: abs(0.5) → 1.0×, abs(2.0+) → 2.0×
    abs_gamma = abs(gamma_at_strike)
    gamma_scale = min(2.0, 1.0 + abs_gamma / 2.0)
    
    target_mult = 1.5 * gamma_scale
    target_mult = min(3.0, target_mult)  # Cap at 3.0×
    
    if direction == "LONG":
        target = entry + (risk * target_mult)
    else:
        target = entry - (risk * target_mult)
    
    # Minimum 0.5% target
    min_target = entry * 0.005
    if direction == "LONG":
        target = max(target, entry + min_target)
    else:
        target = min(target, entry - min_target)
    
    return target, target_mult, gamma_scale
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence_v2()` structure (7 components, unified for LONG and SHORT):**

```python
def _compute_confidence_v2(
    self, oi_concentration, delta_roc, liquidity_vacuum,
    skew_converging, consolidation_ratio, vol_trend,
    distance_pct, net_gamma, direction, gex_calc, magnet_strike,
) -> float:
    # 1. OI concentration (soft — 0.10–0.15)
    oi_conf = self._oi_concentration_confidence(oi_concentration)
    
    # 2. Delta acceleration (hard gate — 0.0 or 0.20–0.30)
    delta_conf = self._delta_acceleration_confidence(delta_roc, direction)
    
    # 3. Liquidity vacuum (hard gate — 0.0 or 0.15–0.20)
    vacuum_conf = self._liquidity_vacuum_confidence(liquidity_vacuum)
    
    # 4. Skew convergence (hard gate — 0.0 or 0.15–0.20)
    skew_conf = self._skew_convergence_confidence(skew_converging)
    
    # 5. Consolidation tightness (soft — 0.10–0.15)
    cons_conf = self._consolidation_confidence(consolidation_ratio)
    
    # 6. Volume profile (soft — 0.05–0.10)
    vol_conf = self._volume_confidence(vol_trend)
    
    # 7. Distance to target (soft — 0.05–0.10)
    dist_conf = self._distance_confidence(distance_pct)
    
    confidence = oi_conf + delta_conf + vacuum_conf + skew_conf + cons_conf + vol_conf + dist_conf
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

**Hard gates (all must pass for signal):**
- Delta acceleration (ROC > 5% at magnet strike)
- Liquidity vacuum (thin order book on breakout side)
- Skew convergence (skew tilting toward magnet direction)

**Soft factors (boost confidence):**
- OI concentration (how much OI at the strike)
- Consolidation tightness (how coiled is the price)
- Volume profile (declining = accumulation)
- Distance to target (closer = higher probability)

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `full_data.prob_weighted_magnet`:**

```yaml
prob_weighted_magnet:
  enabled: true
  tracker:
    max_hold_seconds: 2700        # 45 min (slower strategy)
  params:
    # === v1 params (kept for backwards compat) ===
    min_oi_concentration: 2.0
    consolidation_ratio: 0.50
    delta_accel_ratio: 1.05
    min_net_gamma: 500000.0
    stop_pct: 0.005
    target_risk_mult: 1.5
    min_confidence: 0.35          # raised from 0.25
    max_confidence: 0.80
    valid_volume_trends: ["FLAT", "DOWN"]

    # === v2 Velocity-Magnet params ===
    delta_roc_threshold: 0.05       # 5% ROC for delta acceleration
    liquidity_vacuum_ratio: 0.30    # bid/ask ratio for vacuum
    gamma_scale_base: 2.0           # gamma value for 2.0× target scaling
    target_mult_cap: 3.0            # max target multiplier
    target_min_pct: 0.005           # minimum 0.5% target
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "magnet_strike": ...,
    "oi_concentration": ...,
    "call_oi": ...,
    "put_oi": ...,
    "call_delta": ...,
    "put_delta": ...,
    "net_delta": ...,
    "distance_to_magnet_pct": ...,
    "consolidation_ratio": ...,
    "volume_trend": ...,
    "net_gamma": ...,
    "qualifying_strikes": ...,
    "stop_pct": ...,
    "target_risk_mult": ...,
    "risk": ...,
    "risk_reward_ratio": ...,
    "trend": ...,

    # === v2 new fields ===
    "delta_roc": round(delta_roc, 4),
    "liquidity_vacuum_ratio": round(vacuum_ratio, 3),
    "skew_roc": round(skew_roc, 4),
    "gamma_at_magnet": round(gamma_at_strike, 4),
    "gamma_scale": round(gamma_scale, 2),
    "target_mult": round(target_mult, 2),
    "skew_converging": True/False,
    "liquidity_vacuum": True/False,
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- Prob Weighted Magnet v2 (Velocity-Magnet) ---
KEY_MAGNET_DELTA_5M = "magnet_delta_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Get magnet strikes from greeks_summary (highest OI strikes below/above price)
- Compute per-strike delta from gex_calc.get_delta_by_strike(magnet_strike)
- Compute delta ROC: `(current_delta - delta_5_ago) / abs(delta_5_ago)`
- Push to rolling window KEY_MAGNET_DELTA_5M

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_MAGNET_DELTA_5M` |
| `main.py` | Add rolling key init + magnet delta ROC computation |
| `strategies/full_data/prob_weighted_magnet.py` | Full v2 rewrite — delta acceleration, liquidity vacuum, skew convergence, gamma targets |
| `config/strategies.yaml` | Add 7 new params under `prob_weighted_magnet` |

**No changes needed:** `strategies/full_data/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_delta_acceleration()` detects delta ROC > 5% at magnet strike
2. ✅ `_check_liquidity_vacuum()` validates thin order book on breakout side
3. ✅ `_check_skew_convergence()` validates skew tilting toward magnet direction
4. ✅ `_compute_gamma_weighted_target()` scales target with gamma magnitude
5. ✅ Hard gates: delta acceleration AND liquidity vacuum AND skew convergence
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling key `KEY_MAGNET_DELTA_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.full_data.prob_weighted_magnet import ProbWeightedMagnet; print('OK')"`
11. ✅ Commit message: `feat(magnet): v2 Velocity-Magnet upgrade`

---

## Data Reference

**Delta acceleration patterns (at magnet strike):**
- Stale: delta 0.30 → 0.31 → 0.30 → roc ≈ 0 (no acceleration, stale OI)
- Bullish accumulation: delta 0.30 → 0.40 → 0.50 → roc = (0.50-0.30)/0.30 = 0.67 (strong)
- Bearish distribution: delta -0.30 → -0.40 → -0.50 → roc = (-0.50-(-0.30))/0.30 = -0.67 (strong)
- Threshold: |roc| > 0.05 = acceleration confirmed

**Liquidity vacuum patterns (market_depth_agg):**
- Normal: bid_total=5000, ask_total=5000 → ratio=1.0 (balanced)
- LONG vacuum: bid_total=5000, ask_total=50 → ratio=0.01 (thin asks = easy to break up)
- SHORT vacuum: bid_total=50, ask_total=5000 → ratio=0.01 (thin bids = easy to break down)
- Threshold: ratio < 0.30 = vacuum confirmed

**Skew convergence patterns:**
- LONG magnet: skew -0.20 → -0.15 → -0.08 → current > avg (normalizing from fear) → converging ✅
- LONG magnet: skew -0.20 → -0.25 → -0.30 → current < avg (getting more fearful) → NOT converging ❌
- SHORT magnet: skew 0.30 → 0.25 → 0.12 → current < avg (normalizing from euphoria) → converging ✅
- SHORT magnet: skew 0.30 → 0.35 → 0.40 → current > avg (getting more euphoric) → NOT converging ❌

**Gamma-weighted targets:**
- Low gamma magnet: gamma=0.1 → scale=1.05 → target=1.57× risk (tight)
- Medium gamma magnet: gamma=1.0 → scale=1.5 → target=2.25× risk (baseline)
- High gamma magnet: gamma=3.0 → scale=2.0 → target=3.0× risk (capped)
- Cap: gamma_scale capped at 2.0 → target_mult capped at 3.0×
