# strike_concentration v2 — "Liquidity-Momentum" Upgrade

**Strategy:** `strategies/layer3/strike_concentration.py`
**Config:** `config/strategies.yaml` → `layer3.strike_concentration`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `strike_concentration` is a solid "price-action at OI levels" strategy but has 3 blind spots:
1. **Slice mode is blind to order book** — a volume spike can be a "fake" large limit fill. Need liquidity vacuum confirmation.
2. **Delta sign flip is weak** — delta turning positive/negative is just a direction, not conviction. Need acceleration (ROC).
3. **OI magnitude is secondary** — a bounce off 10K OI is noise; 1M OI is structural. OI should weight confidence more heavily.
4. **Fixed 1.5× risk target** — doesn't adapt to market speed. In fast markets, 1.5× may be too tight; in slow markets, too loose.

Synapse's proposal: upgrade with **Liquidity Vacuum**, **Delta-Surge Validation**, **Gamma-Magnitude Weighting**, and **ATR-Normalized Targets**.

---

## v2 Architecture

### New Confidence Components (8 total for Bounce, 8 for Slice)

| # | Component | Bounce Weight | Slice Weight | Type | Source |
|---|-----------|---------------|--------------|------|--------|
| 1 | Strike OI Rank | 0.10–0.15 | 0.10–0.15 | soft | existing |
| 2 | Proximity | 0.10–0.20 | 0.10–0.20 | soft | existing |
| 3 | Gamma Magnitude | 0.05–0.10 | 0.05–0.10 | soft | **NEW** (gex_calculator) |
| 4 | Signal Strength | 0.10–0.15 | 0.15–0.25 | soft | upgraded |
| 5 | Liquidity Vacuum | — | 0.10–0.15 | **hard gate** | **NEW** (market_depth_agg) |
| 6 | Delta Surge | — | 0.10–0.15 | **hard gate** | **NEW** (d(Delta)/dt) |
| 7 | Regime Alignment | 0.05–0.10 | 0.05–0.10 | soft | existing |
| 8 | ATR Target Quality | 0.05–0.10 | 0.05–0.10 | soft | **NEW** (ATR scaling) |

**New min confidence: 0.35** (up from 0.25 — higher bar for strike interactions)

---

## Phase 1: Liquidity Vacuum for Slice — The Order Book Confirmation

**Goal:** Add `market_depth_agg` bid/ask size ratio check as a **hard gate** for slice signals.

**Logic:**
1. Get `market_depth_agg` from `rolling_data` — contains aggregated bid/ask size by price level
2. For **LONG slice** (price breaking above Call strike): check that **ask side depth** is collapsing (liquidity vacuum above the strike)
3. For **SHORT slice** (price breaking below Put strike): check that **bid side depth** is collapsing (liquidity vacuum below the strike)
4. **Hard gate:** bid/ask ratio must be extreme:
   - LONG slice: `bid_size / ask_size > 3.0` (massive bid wall, tiny ask wall = vacuum above)
   - SHORT slice: `ask_size / bid_size > 3.0` (massive ask wall, tiny bid wall = vacuum below)
5. If depth data unavailable, fall back to volume-only check (backwards compat)

**Why this works:** A real "slice" through a strike requires the opposing liquidity to be thin. If there's a thick wall of orders on the breakout side, price can't slice through — it bounces or stalls. A liquidity vacuum means the path is clear for momentum to carry through.

**Config params to add:**
```yaml
liquidity_vacuum_ratio: 3.0           # bid/ask ratio threshold for vacuum
```

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- `market_depth_agg` stream: `{"bid_levels": [{"price": 418.0, "size": 500}, ...], "ask_levels": [{"price": 420.0, "size": 50}, ...]}`
- If ask size at breakout level is 50 vs bid size 5000 → ratio = 100 → vacuum confirmed
- If ask size at breakout level is 3000 vs bid size 500 → ratio = 0.167 → NO vacuum → reject

---

## Phase 2: Delta-Surge Validation — The Conviction Check

**Goal:** Replace "delta sign flip" with **Delta Acceleration (ROC)** for slice signals.

**Current behavior:** `_check_delta_positive_at_strike()` / `_check_delta_negative_at_strike()` — just checks if net delta > 0 or < 0.

**New behavior:**
1. Get `gex_calculator.get_delta_by_strike(strike)` for current net_delta
2. Get previous net_delta from rolling window (new key `KEY_STRIKE_DELTA_5M`)
3. Compute `delta_accel = current_delta / previous_delta`
4. For **LONG slice:** `delta_accel > 1.15` (delta accelerated ≥15%)
5. For **SHORT slice:** `delta_accel < 0.85` (delta decelerated ≥15%)
6. **Hard gate:** delta_accel must exceed threshold

**Why this works:** Delta sign flip just says "delta is positive/negative" — which could be a slow drift. Delta acceleration says "delta is CHANGING fast" — which is the smoking gun for dealer hedging forcing a move through a strike. This catches the moment dealers are forced to buy/sell aggressively.

**Config params to add:**
```yaml
delta_accel_threshold: 1.15           # delta must accelerate ≥15% at slice
```

**Rolling key to add:** `KEY_STRIKE_DELTA_5M` in `rolling_keys.py`
**main.py change:** Track net delta at top-OI strikes in rolling window

---

## Phase 3: Gamma-Magnitude Weighting — The Structural Weight

**Goal:** Use **Gamma Magnitude** at the strike as a confidence weight, not just OI rank.

**Current behavior:** OI rank (0.20–0.30) and OI volume (0.05–0.10) are the only magnitude signals.

**New behavior:**
1. Get gamma magnitude at the strike: `gex_calculator.get_strike_net_gamma(strike)`
2. Normalize gamma magnitude: `gamma_weight = min(1.0, abs(gamma_at_strike) / gamma_threshold)`
3. Use gamma_weight to scale bounce confidence (0.05–0.10 component)
4. A strike with gamma magnitude > 0.50 gets maximum weight; < 0.10 gets minimum

**Why this works:** OI alone doesn't tell the whole story. A strike with 10K OI but high gamma is a "magnet" — price will be drawn to it. A strike with 10K OI and low gamma is noise. Gamma magnitude captures the dealer hedging pressure at that specific strike, which is what actually causes bounces and slices.

**Config params to add:**
```yaml
gamma_magnitude_threshold: 0.50       # gamma threshold for max weight
```

---

## Phase 4: ATR-Normalized Targets — The Speed-Adaptive Exit

**Goal:** Replace fixed 1.5× risk target with **ATR-normalized targets**.

**Current behavior:** `target = entry + risk * 1.5` — fixed regardless of market speed.

**New behavior:**
1. Compute ATR from price rolling window: `ATR = std_dev of price_5m * sqrt(5)` (approximate ATR)
2. Get rolling mean ATR from `KEY_ATR_5M` rolling window
3. Compute `atr_ratio = current_atr / mean_atr`
4. For **bounce:** `target_mult = 1.5 × atr_ratio`
5. For **slice:** `target_mult = 2.0 × atr_ratio` (slices have more momentum)
6. Cap target_mult at 3.0 (don't overextend)
7. Minimum target: 0.3% from entry (don't scalp for less than 0.3%)

**Why this works:** In fast markets (high ATR), a 1.5× target might be hit in seconds — but 1.5× might also be too small to cover slippage. By scaling with ATR, we adapt to market conditions: wider targets in fast markets, tighter in slow markets.

**Config params to add:**
```yaml
bounce_target_mult: 1.5               # base multiplier for bounces
slice_target_mult: 2.0                # base multiplier for slices
atr_normalization_cap: 3.0            # cap on target multiplier
target_min_pct: 0.003                 # minimum 0.3% target
```

---

## Phase 5: Confidence Recalculation

**New `_compute_bounce_confidence()` structure:**

```python
def _compute_bounce_confidence(self, ...) -> float:
    # 1. OI rank (0.10–0.15)
    rank_conf = max(0.10, 0.15 - 0.025 * (rank - 1))

    # 2. Proximity (0.10–0.20)
    prox_conf = ...  # closer = higher

    # 3. Gamma magnitude (0.05–0.10) — NEW
    gamma_conf = 0.05 + 0.05 * min(1.0, abs(gamma_at_strike) / GAMMA_MAGNITUDE_THRESHOLD)

    # 4. Signal strength (0.10–0.15)
    signal_conf = ...  # candle pattern / divergence quality

    # 5. Regime alignment (0.05–0.10)
    regime_conf = ...

    # 6. ATR target quality (0.05–0.10) — NEW
    atr_conf = ...  # how well the target scales with market speed

    # Normalize and average
    confidence = (norm_rank + norm_prox + norm_gamma + norm_signal + norm_regime + norm_atr) / 6.0
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

**New `_compute_slice_confidence()` structure:**

```python
def _compute_slice_confidence(self, ...) -> float:
    # 1. OI rank (0.10–0.15)
    rank_conf = ...

    # 2. Proximity (0.10–0.20)
    prox_conf = ...

    # 3. Gamma magnitude (0.05–0.10) — NEW
    gamma_conf = ...

    # 4. Signal strength (0.15–0.25) — upgraded: body_ratio + volume
    signal_conf = 0.15 + 0.10 * min(1.0, body_ratio / 0.8)

    # 5. Liquidity vacuum (0.10–0.15) — NEW hard gate
    vacuum_conf = 0.10 + 0.05 * min(1.0, (depth_ratio - LIQUIDITY_VACUUM_RATIO) / 2.0)

    # 6. Delta surge (0.10–0.15) — NEW hard gate
    delta_conf = 0.10 + 0.05 * min(1.0, (delta_accel - 1.0) / 0.5)

    # 7. Regime alignment (0.05–0.10)
    regime_conf = ...

    # 8. ATR target quality (0.05–0.10) — NEW
    atr_conf = ...

    # Normalize and average
    confidence = (sum of 8 norms) / 8.0
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

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
    slice_body_ratio: 0.3
    slice_volume_ratio: 1.20
    divergence_volume_threshold: 0.80
    stop_pct_bounce: 0.003
    stop_pct_slice: 0.003
    target_risk_mult: 1.5
    min_confidence: 0.35          # raised from 0.25
    max_confidence: 0.85

    # === v2 Liquidity-Momentum params ===
    # Liquidity vacuum
    liquidity_vacuum_ratio: 3.0

    # Delta surge
    delta_accel_threshold: 1.15

    # Gamma magnitude
    gamma_magnitude_threshold: 0.50

    # ATR-normalized targets
    bounce_target_mult: 1.5
    slice_target_mult: 2.0
    atr_normalization_cap: 3.0
    target_min_pct: 0.003
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
    "bullish_reversal": ...,
    "bearish_reversal": ...,
    "body_ratio": ...,
    "volume_spike": ...,
    "delta_positive": ...,
    "delta_negative": ...,
    "net_gamma": ...,
    "regime": ...,
    "trend": ...,
    "risk": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "gamma_at_strike": round(gamma_at_strike, 4),
    "liquidity_vacuum_ratio": round(depth_ratio, 2),
    "delta_acceleration": round(delta_accel, 3),
    "atr_current": round(current_atr, 4),
    "atr_mean": round(mean_atr, 4),
    "atr_ratio": round(atr_ratio, 3),
    "target_mult": round(target_mult, 2),
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- Strike Concentration v2 (Liquidity-Momentum) ---
KEY_STRIKE_DELTA_5M = "strike_delta_5m"
KEY_ATR_5M = "atr_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute ATR: `std_dev of price_5m * sqrt(5)` → push to `KEY_ATR_5M`
- Track net delta at top-OI strikes → push to `KEY_STRIKE_DELTA_5M`

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_STRIKE_DELTA_5M`, `KEY_ATR_5M` |
| `main.py` | Add rolling key init + ATR + strike delta computation |
| `strategies/layer3/strike_concentration.py` | Main v2 implementation |
| `config/strategies.yaml` | Add 10 new params under `strike_concentration` |

**No changes needed:** `strategies/layer3/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_liquidity_vacuum()` checks bid/ask depth ratio for slice confirmation
2. ✅ `_check_delta_surge()` computes delta ROC at strike for slice validation
3. ✅ `_get_gamma_magnitude()` retrieves gamma at strike for bounce confidence weighting
4. ✅ `_compute_atr_normalized_target()` scales target with ATR ratio
5. ✅ Hard gates: liquidity vacuum AND delta surge for slice mode
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling keys `KEY_STRIKE_DELTA_5M` and `KEY_ATR_5M` added and populated
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.layer3.strike_concentration import StrikeConcentration; print('OK')"`
11. ✅ Commit message: `feat(strike_conc): v2 Liquidity-Momentum upgrade`

---

## Data Reference (from LEVEL2_DATA_SAMPLES.jsonl)

**Liquidity vacuum patterns (depth_agg_parsed):**
- LONG slice: bid_size=5000, ask_size=50 → ratio=100 → vacuum confirmed
- LONG slice: bid_size=500, ask_size=400 → ratio=1.25 → NO vacuum → reject
- SHORT slice: ask_size=5000, bid_size=50 → ratio=100 → vacuum confirmed

**Delta surge patterns:**
- Slow drift: delta 0.30 → 0.32 → 0.34 → ratio=1.13 → NO surge
- Surge: delta 0.30 → 0.45 → 0.60 → ratio=2.0 → surge confirmed
- For SHORT: delta -0.30 → -0.45 → -0.60 → ratio=2.0 → decel=0.50 → surge confirmed

**Gamma magnitude patterns:**
- Strike 420: gamma=0.80 → weight=max (strong structural wall)
- Strike 425: gamma=0.10 → weight=min (weak noise level)
- Strike 415: gamma=0.40 → weight=moderate (meaningful but not dominant)

**ATR patterns:**
- Fast market: current_atr=2.5, mean_atr=1.0 → atr_ratio=2.5 → target_mult=3.75 → capped at 3.0
- Normal market: current_atr=1.0, mean_atr=1.0 → atr_ratio=1.0 → target_mult=1.5
- Slow market: current_atr=0.5, mean_atr=1.0 → atr_ratio=0.5 → target_mult=0.75
