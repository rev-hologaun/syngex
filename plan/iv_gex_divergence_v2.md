# iv_gex_divergence v2 — "Volatility-Snap" Upgrade

**Strategy:** `strategies/layer2/iv_gex_divergence.py`
**Config:** `config/strategies.yaml` → `layer2.iv_gex_divergence`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `iv_gex_divergence` checks **ATM IV** only. A true "panic bottom" is often preceded by a massive spike in **OTM Put IV** (the tail) rather than just ATM IV. The strategy also uses a **fixed percentage stop** instead of gamma-wall-aware stops, and doesn't account for option volume when measuring IV changes (IV can spike on low volume = noise).

Synapse's proposal: upgrade to **IV Skew Gradient** (tail risk), **Gamma Density Gradient** (structural snap), **Volume-Weighted IV** (conviction filter), and **Wall-Based Stops** (dynamic risk).

---

## v2 Architecture

### New Confidence Components (6 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | Price Extremeness | 0.15 | soft | price percentile in 30m window (unchanged) |
| 2 | **IV Skew Acceleration** | 0.20 | **hard gate** | OTM Put IV vs ATM IV gap widening (was ATM IV only) |
| 3 | **Gamma Density Gradient** | 0.15 | **hard gate** | declining gamma density as price moves to extreme |
| 4 | **Volume-Weighted IV** | 0.10 | soft | IV change × log(volume) (was raw IV change) |
| 5 | Net Gamma Magnitude | 0.10 | soft | abs(net_gamma) (unchanged) |
| 6 | Wall Proximity | 0.10 | soft | proximity to gamma wall (unchanged) |
| 7 | **Regime Intensity** | 0.05–0.15 | soft | gamma magnitude scaling (enhanced) |

**New min confidence: 0.35** (up from 0.25 — higher bar for structural snap signals)

---

## Phase 1: IV Skew Acceleration — The Tail Risk Detector

**Goal:** Replace ATM IV-only check with **IV Skew Gradient** — monitor the gap between OTM Put IV and ATM IV (for SHORT signals) or OTM Call IV and ATM IV (for LONG signals).

**Logic:**
1. For **SHORT** (blow-off top): Get IV at OTM Put strikes (e.g., strike - 2% and - 4% from ATM) and ATM strike. Compute `skew = OTM_Put_IV - ATM_IV`.
2. For **LONG** (panic bottom): Get IV at OTM Call strikes (e.g., strike + 2% and + 4% from ATM) and ATM strike. Compute `skew = OTM_Call_IV - ATM_IV`.
3. Maintain a rolling window of skew values using new key `KEY_IV_SKEW_GRADIENT_5M`.
4. **Hard gate:** `skew_roc > 0.15` (skew has increased ≥15% in last 5 ticks)
5. For SHORT: skew should be **increasing** (OTM puts getting expensive = fear building)
6. For LONG: skew should be **increasing** (OTM calls getting expensive = euphoria building)

**Why this works:** A true panic bottom isn't just ATM IV rising — it's the **tail** (OTM puts) getting expensive first. Smart money buys OTM protection before the broader market reacts. The skew gradient catches this early.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- ATM Put (420P): IV=0.60, delta=-0.52 → baseline
- OTM Put (395P): IV=1.05, delta=-0.01, prob_ITM=0% → **elevated tail risk**
- ATM Call (420C): IV=0.60 → baseline
- OTM Call (425C): IV=0.65 → moderate call skew

If OTM Put IV goes from 0.80 → 1.05 while ATM stays at 0.60, that's a 75% skew increase → strong fear signal.

**Config params to add:**
```yaml
iv_skew_otm_pct: 0.05              # OTM strike distance (5% OTM)
iv_skew_roc_window: 5              # window for skew ROC
iv_skew_roc_threshold: 0.15        # skew must have risen ≥15%
```

**Rolling key to add:** `KEY_IV_SKEW_GRADIENT_5M` in `rolling_keys.py`
**main.py change:** Compute skew gradient and push to rolling window

---

## Phase 2: Gamma Density Gradient — The Structural Snap

**Goal:** Detect when price is moving from a high-gamma zone (stable) into a low-gamma zone (unstable). A "snap" occurs when the structural support evaporates.

**Logic:**
1. Get gamma ladder from `gex_calc.get_greeks_summary()`
2. Compute `gamma_density` around current price: sum of |gamma| for strikes within ±1% of price
3. Compute `gamma_density` from 5 ticks ago (from rolling window)
4. **Hard gate:** current gamma_density < rolling mean gamma_density × 0.7 (gamma density has declined ≥30%)
5. This confirms the price is moving into an "unstable" zone where dealer hedging provides less support

**Why this works:** High gamma zones act as "magnets" — price moves slowly, dealers hedge gently. Low gamma zones are "vacuum" — price moves fast, dealers hedge aggressively. A price extreme in a low-gamma zone is much more likely to snap back because there's no structural support holding it there.

**Data reference:**
- ATM options have highest gamma (0.0627) → high gamma density zone
- OTM options have low gamma (0.0025 for 395P) → low gamma density zone
- If price is at 425 (near 420C gamma peak of 0.0627) → high gamma, stable
- If price moves to 435 (far from any gamma peak) → low gamma, unstable → snap likely

**Config params to add:**
```yaml
gamma_density_window_pct: 0.01     # ±1% window for gamma density
gamma_density_decline_threshold: 0.70  # density must decline ≥30%
```

---

## Phase 3: Volume-Weighted IV — The Conviction Filter

**Goal:** Weight IV changes by option volume to distinguish real conviction from liquidity-gap noise.

**Logic:**
1. For the ATM strike being checked, get current option volume from `greeks_summary`
2. Compute `conviction_iv = iv_change × log(volume + 1)`
3. Normalize: if volume is very high (e.g., 56k on 425C), conviction is amplified
4. If volume is very low (e.g., 9 on 382.5C), conviction is dampened
5. **Soft factor:** conviction_iv replaces raw iv_change in confidence calculation

**Why this works:** IV can spike on very low volume (a single quote change = noise). An IV expansion accompanied by massive option volume (e.g., 56k contracts on 425C) is real conviction. Volume-weighting prevents false signals from illiquid strikes.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- OTM Call (425C): vol=56k, IV=0.65 → high volume, high conviction
- ATM Call (420C): vol=26k, IV=0.60 → moderate volume, moderate conviction
- ATM Put (420P): vol=39k, IV=0.60 → moderate volume
- Deep ITM Call (382.5C): vol=9, IV=1.98 → low volume, low conviction (despite high IV)

**Config params to add:**
```yaml
iv_volume_min: 100                 # min volume to consider IV meaningful
iv_volume_weight_log: true         # use log(volume) weighting
```

---

## Phase 4: Dynamic Wall-Based Stops

**Goal:** Replace fixed percentage stop with gamma-wall-aware dynamic stops.

**Current behavior:** `stop = entry * (1 ± STOP_PCT)` — fixed 0.6% stop.

**New behavior:**
1. Get gamma walls via `gex_calc.get_gamma_walls(threshold=500_000)`
2. For **SHORT** signal: place stop just beyond the nearest **call wall** above price
   - `stop = wall_strike + (wall_strike × 0.002)` (2% buffer beyond wall)
   - If no wall within 2% → fall back to `entry * (1 + STOP_PCT)`
3. For **LONG** signal: place stop just beyond the nearest **put wall** below price
   - `stop = wall_strike - (wall_strike × 0.002)` (2% buffer beyond wall)
   - If no wall within 2% → fall back to `entry * (1 - STOP_PCT)`

**Why this works:** Gamma walls are dealer hedging zones. A SHORT signal near a call wall means the wall is resistance — if price breaks through the wall, the SHORT thesis is wrong. Placing the stop just beyond the wall gives the trade room to breathe but cuts losses if the wall breaks.

**Data reference:**
- ATM Call (420C): gamma=0.0627 → major call wall at 420
- ATM Put (420P): gamma=0.0627 → major put wall at 420
- OTM Call (425C): gamma=0.043 → secondary call wall at 425
- OTM Put (395P): gamma=0.0025 → weak put wall at 395

**Config params to add:**
```yaml
wall_stop_buffer_pct: 0.002        # 0.2% buffer beyond wall
wall_stop_max_distance_pct: 0.02   # max distance to nearest wall (2%)
fallback_stop_pct: 0.006           # fallback if no wall nearby
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence()` structure:**

```python
def _compute_confidence(
    self, price_percentile, iv_skew_roc, gamma_density_decline,
    conviction_iv, net_gamma, wall, regime, signal_type,
) -> float:
    # 1. Price extremeness (0.0–0.15)
    pct_conf = self._price_extremeness_confidence(price_percentile, signal_type)

    # 2. IV skew acceleration (hard gate — 0.0 or 0.20)
    skew_conf = 0.20 if iv_skew_roc else 0.0

    # 3. Gamma density gradient (hard gate — 0.0 or 0.15)
    density_conf = 0.15 if gamma_density_decline else 0.0

    # 4. Volume-weighted IV (soft — 0.0–0.10)
    vol_iv_conf = self._conviction_iv_confidence(conviction_iv)

    # 5. Net gamma magnitude (0.0–0.10)
    gamma_conf = self._gamma_magnitude_confidence(net_gamma)

    # 6. Wall proximity (0.0–0.10)
    wall_conf = self._wall_proximity_confidence(wall)

    # 7. Regime intensity (0.05–0.15)
    regime_conf = self._regime_intensity_confidence(net_gamma, signal_type)

    confidence = pct_conf + skew_conf + density_conf + vol_iv_conf + gamma_conf + wall_conf + regime_conf
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

**Hard gates (all must pass for signal):**
- Price extremeness (unchanged: p70 high or p30 low)
- IV skew acceleration > 15% (NEW)
- Gamma density decline > 30% (NEW)

**Soft factors (boost confidence but don't block):**
- Volume-weighted IV conviction
- Net gamma magnitude
- Wall proximity
- Regime intensity

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `layer2.iv_gex_divergence`:**

```yaml
iv_gex_divergence:
  enabled: true
  tracker:
    max_hold_seconds: 2700
  params:
    # === v1 params (kept for backwards compat) ===
    iv_decline_pct: 0.05
    min_confidence: 0.35          # raised from 0.25
    stop_pct: 0.006
    target_risk_mult: 1.5

    # === v2 Volatility-Snap params ===
    # IV skew gradient
    iv_skew_otm_pct: 0.05
    iv_skew_roc_window: 5
    iv_skew_roc_threshold: 0.15

    # Gamma density
    gamma_density_window_pct: 0.01
    gamma_density_decline_threshold: 0.70

    # Volume-weighted IV
    iv_volume_min: 100

    # Wall-based stops
    wall_stop_buffer_pct: 0.002
    wall_stop_max_distance_pct: 0.02
    fallback_stop_pct: 0.006
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "price_percentile": ...,
    "iv_atm": ...,
    "iv_decline_pct": ...,
    "net_gamma": ...,
    "wall_above/below_strike": ...,
    "wall_above/below_gex": ...,
    "regime": ...,
    "trend": ...,
    "risk": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "iv_skew": round(current_skew, 4),         # OTM IV - ATM IV
    "iv_skew_roc": round(skew_roc, 4),         # skew rate of change
    "gamma_density_current": round(current_density, 2),
    "gamma_density_mean": round(mean_density, 2),
    "gamma_density_decline_pct": round(density_decline, 4),
    "conviction_iv": round(conviction_iv, 4),
    "option_volume": option_volume,
    "stop_type": "wall" or "fixed",             # how stop was determined
    "stop_wall_strike": wall_strike,            # wall used for stop
    "regime_intensity": round(gamma_intensity, 3),
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- IV skew gradient (iv_gex_divergence v2) ---
KEY_IV_SKEW_GRADIENT_5M = "iv_skew_gradient_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute IV skew gradient (OTM IV - ATM IV) for both puts and calls
- Push to rolling window

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_IV_SKEW_GRADIENT_5M`, add to `ALL_KEYS` |
| `main.py` | Add rolling key init, compute and push IV skew gradient |
| `strategies/layer2/iv_gex_divergence.py` | Full v2 rewrite — skew gradient, gamma density, volume-weighted IV, wall-based stops |
| `config/strategies.yaml` | Add 12 new params under `iv_gex_divergence` |

**No changes needed:** `strategies/layer2/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_iv_skew_acceleration()` computes OTM-vs-ATM IV skew ROC
2. ✅ `_check_gamma_density_gradient()` detects declining gamma density
3. ✅ `_compute_conviction_iv()` weights IV change by log(volume)
4. ✅ Wall-based stops: dynamic stop beyond nearest gamma wall
5. ✅ Hard gates: price extremeness AND IV skew ROC AND gamma density decline
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling key `KEY_IV_SKEW_GRADIENT_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.layer2.iv_gex_divergence import IVGEXDivergence; print('OK')"`
11. ✅ Commit message: `feat(iv_gex): v2 Volatility-Snap upgrade`

---

## Data Reference (from LEVEL2_DATA_SAMPLES.jsonl)

**IV Skew patterns (optionchain_parsed):**
- ATM Put (420P): IV=0.60 → baseline
- OTM Put (395P): IV=1.05 → **skew = 0.45** (high tail risk)
- ATM Call (420C): IV=0.60 → baseline
- OTM Call (425C): IV=0.65 → **skew = 0.05** (moderate call skew)
- If skew goes from 0.20 → 0.45 → ROC = 125% → explosive fear signal

**Gamma density patterns:**
- ATM strikes (420C, 420P): gamma=0.0627 → high density zone
- OTM strikes (425C): gamma=0.043 → medium density
- Deep OTM strikes (395P): gamma=0.0025 → low density zone
- If price moves from 420 (gamma peak) to 435 (no gamma peak) → density drops → snap likely

**Volume patterns:**
- OTM Call (425C): vol=56k → high conviction
- ATM Call (420C): vol=26k → moderate conviction
- ATM Put (420P): vol=39k → moderate conviction
- Deep ITM Call (382.5C): vol=9 → low conviction (despite IV=1.98)

**Wall patterns:**
- Call wall at 420 (gamma=0.0627) → major resistance
- Put wall at 420 (gamma=0.0627) → major support
- Call wall at 425 (gamma=0.043) → secondary resistance
- Put wall at 395 (gamma=0.0025) → weak support
