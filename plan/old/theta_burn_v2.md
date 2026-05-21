# theta_burn v2 — "Pinning-Master" Upgrade

**Strategy:** `strategies/layer3/theta_burn.py`
**Config:** `config/strategies.yaml` → `layer3.theta_burn`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `theta_burn` is a solid "pinning effect" strategy but has 4 critical blind spots:
1. **Wall breaker vulnerability** — assumes walls hold; gets steamrolled when a wall breaks.
2. **Volume/candle rejection is weak** — doesn't capture the "hard rejection" signature (delta spike + price stationary).
3. **Fixed 0.2-0.4% targets** — doesn't scale with IV expansion (volatility squeeze = bigger breakout).
4. **Positive-gamma-only** — misses momentum opportunities in negative gamma where pins can break violently.

Synapse's proposal: upgrade to **Wall Liquidity Exhaustion Detection**, **Delta-Gamma Divergence Rejection**, **IV-Expansion Scaled Targets**, and **Regime-Specific Logic** (bounce vs slice).

---

## v2 Architecture

### New Confidence Components

| Mode | Component | Weight | Type | Source |
|------|-----------|--------|------|--------|
| **Bounce** | Gamma Strength | 0.10–0.20 | soft | gex_calc walls (existing) |
| **Bounce** | Wall Proximity | 0.15–0.25 | soft | price vs wall (existing) |
| **Bounce** | Range Narrowness | 0.10–0.15 | soft | 5m/30m range ratio (existing) |
| **Bounce** | **Delta-Gamma Divergence** | 0.20–0.25 | **hard gate** | gex_calc per-strike delta/gamma |
| **Bounce** | **Wall Liquidity** | 0.10–0.15 | **hard gate** | market_depth_agg wall depth |
| **Bounce** | IV Expansion | 0.05–0.10 | soft | KEY_ATM_IV_5M |
| **Slice** | Gamma Strength | 0.10–0.20 | soft | gex_calc walls (existing) |
| **Slice** | **Delta-Gamma Divergence** | 0.20–0.25 | **hard gate** | gex_calc per-strike delta/gamma |
| **Slice** | **Wall Liquidity Exhaustion** | 0.15–0.20 | **hard gate** | market_depth_agg collapsing |
| **Slice** | Range Narrowness | 0.10–0.15 | soft | 5m/30m range ratio (existing) |
| **Slice** | Volume Confirmation | 0.10–0.15 | soft | KEY_VOLUME_5M |
| **Slice** | IV Expansion | 0.05–0.10 | soft | KEY_ATM_IV_5M |

**New min confidence: 0.35** (up from 0.25 — higher bar for pin trades)

---

## Phase 1: Wall Liquidity Exhaustion — The Wall Breaker Check

**Goal:** Detect when the wall being hit is collapsing (liquidity exhaustion), invalidating the pin.

**Logic:**
1. Read `market_depth_agg` from `data` dict
2. For **LONG bounce** (Put wall below): check that bid depth at the wall is holding (not collapsing)
3. For **SHORT bounce** (Call wall above): check that ask depth at the wall is holding
4. For **Slice mode** (NEGATIVE gamma): check that wall depth is **collapsing** (liquidity vacuum = breakout confirmed)
5. **Hard gate:** wall depth must be above minimum threshold (for bounce) OR below minimum threshold (for slice)

**Implementation details:**
```python
def _check_wall_liquidity(self, data, wall_strike, direction, mode):
    depth = data.get("market_depth_agg", {})
    if not depth:
        return True  # No depth data = pass (backwards compat)
    
    bids = depth.get("bids", [])
    asks = depth.get("asks", [])
    
    # Find depth at/near the wall strike
    bid_at_wall = sum(b["size"] for b in bids if abs(b["price"] - wall_strike) / wall_strike < 0.001)
    ask_at_wall = sum(a["size"] for a in asks if abs(a["price"] - wall_strike) / wall_strike < 0.001)
    
    if mode == "bounce":
        # Wall must have depth to hold
        if direction == "LONG":  # Put wall = bid side
            return bid_at_wall > WALL_MIN_BID_DEPTH
        else:  # Call wall = ask side
            return ask_at_wall > WALL_MIN_ASK_DEPTH
    else:  # slice mode — wall must be collapsing
        if direction == "LONG":  # Breaking through Call wall above
            return ask_at_wall < WALL_MIN_ASK_DEPTH  # Thin asks = vacuum
        else:  # Breaking through Put wall below
            return bid_at_wall < WALL_MIN_BID_DEPTH  # Thin bids = vacuum
```

**Config params:**
```yaml
wall_min_bid_depth: 100        # minimum bid size for bounce validation
wall_min_ask_depth: 100        # minimum ask size for bounce validation
wall_vacuum_depth: 50          # max depth for slice vacuum detection
```

---

## Phase 2: Delta-Gamma Divergence Rejection — The Hard Rejection Check

**Goal:** Replace volume/candle rejection with **Delta-Gamma Divergence** — the signature of a hard wall rejection.

**Current behavior:** `_check_rejection()` uses volume divergence, price position, candle pattern. Weak signals.

**New behavior:**
1. Get per-strike delta and gamma from `gex_calc.get_delta_by_strike(wall_strike)` and `gex_calc.get_strike_net_gamma(wall_strike)`
2. Compute delta-gamma divergence score:
   - `delta_spike = abs(current_delta - delta_mean_5m) / delta_mean_5m`
   - `price_stillness = 1.0 - (price_range_5m / price_30m_range)`
   - `divergence_score = delta_spike * price_stillness`
3. A "hard rejection" = delta spike + price stationary = high divergence score
4. **Hard gate:** divergence_score > 0.15 (must have meaningful delta movement + price stationary)

**Implementation details:**
```python
def _check_delta_gamma_divergence(self, data, wall_strike, direction):
    gex_calc = data.get("gex_calculator")
    rolling_data = data.get("rolling_data", {})
    
    if gex_calc is None:
        return False
    
    # Get current delta at wall strike
    try:
        delta_data = gex_calc.get_delta_by_strike(wall_strike)
        current_delta = delta_data.get("net_delta", 0)
    except Exception:
        return False
    
    # Get delta rolling window
    delta_window = rolling_data.get(KEY_WALL_DELTA_5M)
    if delta_window is None or delta_window.count < 3:
        return False
    
    delta_mean = delta_window.mean
    if delta_mean is None or delta_mean == 0:
        return False
    
    # Delta spike: how much has delta moved from mean?
    delta_spike = abs(current_delta - delta_mean) / abs(delta_mean)
    
    # Price stillness: how stationary is price?
    price_5m = rolling_data.get(KEY_PRICE_5M)
    price_30m = rolling_data.get(KEY_PRICE_30M)
    if price_5m is None or price_30m is None:
        return False
    
    range_5m = price_5m.range or 0
    range_30m = price_30m.range or 1
    price_stillness = 1.0 - (range_5m / range_30m)
    
    # Divergence score: delta spike × price stillness
    divergence_score = delta_spike * price_stillness
    
    # Hard gate: must have meaningful divergence
    if divergence_score < 0.15:
        return False
    
    # Direction check: for LONG (Put wall), delta should be negative (selling pressure rejected)
    # For SHORT (Call wall), delta should be positive (buying pressure rejected)
    if direction == "LONG":
        return current_delta < delta_mean  # Delta dropping = rejection
    else:
        return current_delta > delta_mean  # Delta rising = rejection
```

**Rolling key to add:** `KEY_WALL_DELTA_5M` in `rolling_keys.py`
**main.py change:** Track net_delta at wall strikes in rolling window

---

## Phase 3: IV-Expansion Scaled Targets — The Volatility Escape

**Goal:** Replace fixed 0.2-0.4% targets with **IV-expansion scaled targets**.

**Current behavior:** Fixed 0.2-0.4% target based on wall midpoints.

**New behavior:**
1. Get ATM IV from `KEY_ATM_IV_5M` rolling window
2. Compute IV expansion: `iv_factor = current_iv / mean_iv`
3. For **bounce mode** (POSITIVE gamma):
   - Base target: midpoint between walls (existing logic)
   - If IV expanding (factor > 1.0): extend target toward next wall, up to 0.6%
   - If IV contracting (factor < 1.0): tighten target to 0.2%
4. For **slice mode** (NEGATIVE gamma):
   - Base target: 0.3% × iv_factor (explosive breakout)
   - Cap at 0.8% (don't overextend on violent breakouts)

**Implementation details:**
```python
def _compute_iv_scaled_target(self, wall_strike, walls, price, direction, rolling_data, mode):
    iv_window = rolling_data.get(KEY_ATM_IV_5M)
    if iv_window is None or iv_window.mean is None:
        # Fallback to existing midpoint logic
        return self._compute_bounce_target(wall_strike, walls, price, direction, None)
    
    current_iv = iv_window.latest
    mean_iv = iv_window.mean
    iv_factor = current_iv / mean_iv if mean_iv > 0 else 1.0
    
    if mode == "bounce":
        # Start with midpoint target (existing logic)
        base_target = self._compute_bounce_target(wall_strike, walls, price, direction, None)
        
        # Scale: IV expansion = wider target, IV contraction = tighter
        if iv_factor > 1.0:
            # IV expanding — extend target toward 0.6%
            scale = min(0.6, (base_target - price) / (price * 0.003)) * iv_factor
            target = price + (price * 0.003 * scale) if direction == "above" else price - (price * 0.003 * scale)
        else:
            # IV contracting — tighten to 0.2%
            target = price + (price * 0.002) if direction == "above" else price - (price * 0.002)
        
        return target
    else:  # slice mode
        # Base 0.3% × IV factor, capped at 0.8%
        base_pct = 0.003 * iv_factor
        base_pct = min(0.008, base_pct)
        target = price + (price * base_pct) if direction == "above" else price - (price * base_pct)
        return target
```

**Config params:**
```yaml
iv_target_bounce_max_pct: 0.006    # max bounce target with IV expansion
iv_target_slice_max_pct: 0.008     # max slice target with IV expansion
iv_target_bounce_min_pct: 0.002    # min bounce target (IV contracting)
```

---

## Phase 4: Gamma-Regime Hard Gate — Regime-Specific Logic

**Goal:** Replace "POSITIVE only" with **regime-specific logic**.

**Current behavior:** Only trades in POSITIVE gamma regime (bounce mode).

**New behavior:**
1. **POSITIVE gamma regime:** Trade **Bounce** mode (mean reversion at walls)
   - Pinning effect is reliable — dealers hedge counter-cyclically
   - Use bounce confidence scoring + wall liquidity check
   - Use IV-scaled bounce targets (0.2-0.6%)

2. **NEGATIVE gamma regime:** Trade **Slice** mode (momentum breakouts through walls)
   - Pins are dangerous — walls break violently
   - Only trade breakouts, not bounces
   - Use slice confidence scoring + wall liquidity vacuum check
   - Use IV-scaled slice targets (0.3-0.8%)

3. **NEUTRAL regime:** Skip signals (no clear regime bias)

4. **Hard gate:** Regime must be POSITIVE or NEGATIVE (not NEUTRAL)

**Implementation details:**
```python
def evaluate(self, data):
    # ...existing setup...
    
    regime = data.get("regime", "")
    
    # Hard gate: must be POSITIVE or NEGATIVE
    if regime not in ("POSITIVE", "NEGATIVE"):
        return []
    
    if regime == "POSITIVE":
        # Bounce mode: trade wall bounces
        return self._check_bounce_mode(data, gex_calc, rolling_data, net_gamma, walls, timestamp)
    else:  # NEGATIVE
        # Slice mode: trade wall breakouts
        return self._check_slice_mode(data, gex_calc, rolling_data, net_gamma, walls, timestamp)
```

---

## Phase 5: Confidence Recalculation

**New `_compute_bounce_confidence_v2()` structure (6 components):**

| # | Component | Weight | Type |
|---|-----------|--------|------|
| 1 | Gamma Strength | 0.10–0.20 | soft |
| 2 | Wall Proximity | 0.15–0.25 | soft |
| 3 | Range Narrowness | 0.10–0.15 | soft |
| 4 | **Delta-Gamma Divergence** | 0.20–0.25 | **hard gate** |
| 5 | **Wall Liquidity** | 0.10–0.15 | **hard gate** |
| 6 | IV Expansion | 0.05–0.10 | soft |

**New `_compute_slice_confidence_v2()` structure (7 components):**

| # | Component | Weight | Type |
|---|-----------|--------|------|
| 1 | Gamma Strength | 0.10–0.20 | soft |
| 2 | **Delta-Gamma Divergence** | 0.20–0.25 | **hard gate** |
| 3 | **Wall Liquidity Vacuum** | 0.15–0.20 | **hard gate** |
| 4 | Range Narrowness | 0.10–0.15 | soft |
| 5 | Volume Confirmation | 0.10–0.15 | soft |
| 6 | IV Expansion | 0.05–0.10 | soft |
| 7 | Time of Day | 0.05–0.10 | soft |

**Hard gates for both modes:**
- Delta-gamma divergence (must show hard rejection)
- Wall liquidity (must hold for bounce, must collapse for slice)

**Min confidence: 0.35** (up from 0.25)

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `layer3.theta_burn`:**

```yaml
theta_burn:
  enabled: true
  tracker:
    max_hold_seconds: 480
  params:
    # === v1 params (kept for backwards compat) ===
    min_net_gamma: 5000.0
    wall_proximity_pct: 0.005
    stop_past_wall_pct: 0.003
    min_target_pct: 0.002
    max_target_pct: 0.004
    range_narrowness_ratio: 0.40
    min_confidence: 0.35          # raised from 0.25
    max_confidence: 0.80

    # === v2 Pinning-Master params ===
    # Wall liquidity
    wall_min_bid_depth: 100
    wall_min_ask_depth: 100
    wall_vacuum_depth: 50

    # Delta-gamma divergence
    divergence_threshold: 0.15    # min divergence score for hard rejection

    # IV-scaled targets
    iv_target_bounce_max_pct: 0.006
    iv_target_slice_max_pct: 0.008
    iv_target_bounce_min_pct: 0.002
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "wall_type": ...,
    "wall_strike": ...,
    "wall_gex": ...,
    "wall_net_gamma": ...,
    "distance_to_wall_pct": ...,
    "range_ratio": ...,
    "net_gamma": ...,
    "risk": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "divergence_score": round(divergence_score, 3),
    "delta_at_wall": round(current_delta, 4),
    "wall_bid_depth": round(bid_depth, 1),
    "wall_ask_depth": round(ask_depth, 1),
    "wall_liquidity_status": "holding" / "collapsing" / "unknown",
    "iv_factor": round(iv_factor, 3),
    "target_pct": round(target_pct, 4),
    "mode": "bounce" / "slice",
    "regime": regime,
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- Theta Burn v2 (Pinning-Master) ---
KEY_WALL_DELTA_5M = "wall_delta_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Track net_delta at major wall strikes in rolling window KEY_WALL_DELTA_5M
- Get wall strikes from gex_calc.get_gamma_walls(), compute net_delta at each wall

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_WALL_DELTA_5M` |
| `main.py` | Add rolling key init + wall delta tracking |
| `strategies/layer3/theta_burn.py` | Full v2 rewrite — wall liquidity, delta-gamma divergence, IV targets, regime logic |
| `config/strategies.yaml` | Add 9 new params under `theta_burn` |

**No changes needed:** `strategies/layer3/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_wall_liquidity()` validates wall depth for bounces / detects vacuum for slices
2. ✅ `_check_delta_gamma_divergence()` detects hard rejection (delta spike + price stationary)
3. ✅ `_compute_iv_scaled_target()` scales target with IV expansion factor
4. ✅ Regime-specific logic: POSITIVE = bounce, NEGATIVE = slice
5. ✅ Hard gates: delta-gamma divergence AND wall liquidity (for both modes)
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling key `KEY_WALL_DELTA_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.layer3.theta_burn import ThetaBurn; print('OK')"`
11. ✅ Commit message: `feat(theta): v2 Pinning-Master upgrade`

---

## Data Reference

**Wall liquidity patterns (market_depth_agg):**
- Strong wall: bid_at_wall=5000 (Put) → holds → bounce valid
- Collapsing wall: bid_at_wall=50 (Put) → breaking → signal invalid
- Slice vacuum: ask_at_wall=30 (Call) → thin asks = breakout confirmed

**Delta-gamma divergence patterns:**
- Normal approach: delta 0.30 → 0.32 → 0.31, price 420.5 → 420.8 → 420.6 → divergence ≈ 0.02 (weak)
- Hard rejection at Put wall: delta 0.30 → 0.50 → 0.65, price 420.0 → 420.01 → 419.99 → divergence ≈ 0.45 (strong)
- Hard rejection at Call wall: delta -0.30 → -0.50 → -0.65, price 425.0 → 425.01 → 425.00 → divergence ≈ 0.45 (strong)

**IV expansion patterns:**
- IV contracting: 0.40 → 0.35 → factor=0.875 → target = 0.2% (tight)
- IV stable: 0.50 → 0.51 → factor=1.02 → target = midpoint (baseline)
- IV expanding: 0.40 → 0.70 → factor=1.75 → target = 0.5% (wider, capture breakout)
- IV exploding: 0.30 → 0.90 → factor=3.0 → target = 0.6% (capped)

**Regime patterns:**
- POSITIVE gamma: dealer hedging amplifies bounces → mean reversion reliable
- NEGATIVE gamma: dealer hedging fights moves → pins break violently → trade breakouts
- NEUTRAL gamma: no clear regime → skip signals
