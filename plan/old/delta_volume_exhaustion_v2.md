# delta_volume_exhaustion v2 — "Exhaustion-Master" Upgrade

**Strategy:** `strategies/layer2/delta_volume_exhaustion.py`
**Config:** `config/strategies.yaml` → `layer2.delta_volume_exhaustion`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `delta_volume_exhaustion` detects trend exhaustion via **delta decay + volume decay**. Volume is a **lagging** indicator — by the time volume dries up, the reversal may already be underway. The strategy is also blind to structural context: it doesn't know if the exhaustion happened because the trend hit a gamma wall, or because liquidity evaporated.

Synapse's proposal: replace volume decay with **liquidity vacuum detection** (depth-based), add **gamma wall proximity** bonus, add **IV acceleration** for blow-off-top detection, and implement **regime-adaptive targets**.

---

## v2 Architecture

### New Confidence Components (5 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | Trend Strength | 0.20 | soft | price_window (unchanged) |
| 2 | Delta Decline | 0.20 | hard gate | total_delta vs rolling avg (unchanged) |
| 3 | **Liquidity Vacuum** | 0.25 | **hard gate** | depth_snapshot bid/ask ratio + spread |
| 4 | **IV Acceleration** | 0.15 | soft | IV skew rolling window |
| 5 | **Regime Alignment** | 0.10 | soft | regime + net_gamma (unchanged, enhanced) |
| 6 | **Wall Proximity Bonus** | +0.10 | **bonus** | gamma walls proximity |

**New min confidence: 0.35** (up from 0.25 — higher bar, higher quality signals)

---

## Phase 1: Hard Gate — Liquidity Vacuum Detection

**Goal:** Replace `_check_volume_decline()` with `_check_liquidity_vacuum()` that uses `depth_snapshot` to detect pre-reversal order book thinning.

**Logic:**
1. Extract `total_bid_size` and `total_ask_size` from `depth_snapshot`
2. Compute `bid_ask_ratio = total_bid_size / total_ask_size`
3. Compare current ratio to rolling mean of bid/ask ratio (from `KEY_DEPTH_BID_SIZE_5M` / `KEY_DEPTH_ASK_SIZE_5M`)
4. Check spread widening: current spread > rolling mean spread × threshold
5. **Hard gate:** Both conditions must be met:
   - `bid_ask_ratio` is within 15% of its rolling mean (ratio has "stabilized" — no more aggressive one-sided buying/selling)
   - `spread` has widened > 1.2× its rolling mean (liquidity is thinning)

**Why this works:** Before a trend exhausts, the aggressive one-sided order flow that drove the trend stops. The bid/ask ratio flattens toward 1.0, and the spread widens as market makers pull quotes. This happens **before** volume shows a decline.

**Sample data reference:**
- Bullish depth: `total_bid_size=8061, total_ask_size=639, ratio=12.62, spread=0.05` — extreme imbalance, NOT exhaustion
- Bearish depth: `total_bid_size=1940, total_ask_size=2217, ratio=0.88, spread=0.04` — balanced/thin, possible exhaustion
- Balanced depth: `total_bid_size=2019, total_ask_size=2270, ratio=0.89, spread=0.09` — balanced, wider spread

**Config params to add:**
```yaml
liquidity_vacuum_ratio_stability: 0.15    # ratio must be within 15% of rolling mean
liquidity_vacuum_spread_widen_mult: 1.2   # spread must be > 1.2× rolling mean
```

---

## Phase 2: Soft Factor — IV Acceleration

**Goal:** Add IV acceleration check to detect "blow-off top" / "capitulation bottom" patterns.

**Logic:**
1. Access `KEY_IV_SKEW_5M` rolling window from `rolling_data`
2. Compute IV rate of change (ROC) over last 5 data points
3. **For exhausted UP trends:** IV should be accelerating upward (fear is building, smart money buying puts)
4. **For exhausted DOWN trends:** IV should be decelerating or still elevated (panic hasn't fully subsided)
5. If IV acceleration aligns with expected direction → confidence += 0.15
6. If IV moves contrary → confidence -= 0.05 (signal weakened)

**Why this works:** In a true exhaustion, the move that drove the trend is being counter-traded by options buyers. This shows up as rising IV on the side opposite the exhausted trend. A blow-off top = price stalls but put IV spikes. A capitulation bottom = price stalls but call IV spikes.

**Config params to add:**
```yaml
iv_accel_window: 5                          # window for IV ROC calculation
iv_accel_bonus: 0.15                        # confidence bonus when IV aligns
iv_accel_penalty: -0.05                     # confidence penalty when IV opposes
```

---

## Phase 3: Bonus — Gamma Wall Proximity

**Goal:** Add a confidence bonus when exhaustion occurs near a major gamma wall.

**Logic:**
1. Get gamma walls via `gex_calc.get_gamma_walls(threshold=500_000)`
2. Compute distance from current price to nearest wall (call or put)
3. If distance < 0.3% of price → `confidence += 0.10`
4. Bonus is direction-aware:
   - Exhausted UP trend + nearby **call wall** above price → bonus (wall is resistance that stopped the uptrend)
   - Exhausted DOWN trend + nearby **put wall** below price → bonus (wall is support that stopped the downtrend)
   - Wrong side → no bonus (wall isn't the cause of exhaustion)

**Why this works:** Gamma walls are dealer hedging zones that create structural resistance/support. A trend exhausting near a wall is far more likely to reverse than one exhausting in open space.

**Config params to add:**
```yaml
wall_proximity_pct: 0.003                 # within 0.3% of wall
wall_proximity_bonus: 0.10                # confidence bonus
```

---

## Phase 4: Regime-Adaptive Targets

**Goal:** Scale target distance based on regime intensity instead of fixed mean reversion.

**Current behavior:** `target = entry + (rolling_mean - entry) * 1.0` — fixed 1× distance to rolling mean.

**New behavior:**
1. Compute `regime_intensity = abs(net_gamma) / 1_000_000` (capped at 1.0)
2. **NEGATIVE gamma regime** (high vol, fast moves): `target_mult = 1.5` — let the reversal run further
3. **POSITIVE gamma regime** (low vol, slow moves): `target_mult = 0.8` — take profits quicker
4. **NEUTRAL regime:** `target_mult = 1.0` — baseline

**Config params to add:**
```yaml
negative_gamma_target_mult: 1.5           # NEG regime: let it run
positive_gamma_target_mult: 0.8           # POS regime: quick profits
neutral_gamma_target_mult: 1.0            # baseline
gamma_intensity_threshold: 500000         # threshold for regime classification
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence()` structure:**

```python
def _compute_confidence(
    self, trend_strength, delta_decline, liquidity_vacuum,
    iv_accel_score, regime, net_gamma, trend_direction,
    wall_proximity_bonus,
) -> float:
    # 1. Trend strength (0.0–0.20)
    trend_conf = 0.10 + 0.10 * trend_strength

    # 2. Delta decline (hard gate — 0.0 or 0.20)
    delta_conf = 0.20 if delta_decline else 0.0

    # 3. Liquidity vacuum (hard gate — 0.0 or 0.25)
    liq_conf = 0.25 if liquidity_vacuum else 0.0

    # 4. IV acceleration (soft — -0.05 to +0.15)
    iv_conf = iv_accel_score  # already computed as -0.05 or +0.15

    # 5. Regime alignment (soft — 0.0 to 0.10)
    regime_conf = self._regime_alignment(regime, net_gamma, trend_direction)

    # 6. Wall proximity bonus (+0.0 to +0.10)
    wall_conf = wall_proximity_bonus

    confidence = trend_conf + delta_conf + liq_conf + iv_conf + regime_conf + wall_conf
    return min(1.0, max(0.0, confidence))
```

**Hard gates (both must pass for signal):**
- Delta decline: current delta < avg × DELTA_DECLINE_RATIO
- Liquidity vacuum: ratio stabilized AND spread widened

**Soft factors (boost confidence but don't block):**
- Trend strength
- IV acceleration
- Regime alignment
- Wall proximity bonus

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `layer2.delta_volume_exhaustion`:**

```yaml
delta_volume_exhaustion:
  enabled: true
  tracker:
    max_hold_seconds: 2700
  params:
    # === v1 params (kept for backwards compat) ===
    delta_decline_ratio: 0.90
    min_confidence: 0.35          # raised from 0.25

    # === v2 Exhaustion-Master params ===
    # Liquidity vacuum
    liquidity_vacuum_ratio_stability: 0.15
    liquidity_vacuum_spread_widen_mult: 1.2

    # IV acceleration
    iv_accel_window: 5
    iv_accel_bonus: 0.15
    iv_accel_penalty: -0.05

    # Wall proximity
    wall_proximity_pct: 0.003
    wall_proximity_bonus: 0.10

    # Regime-adaptive targets
    negative_gamma_target_mult: 1.5
    positive_gamma_target_mult: 0.8
    neutral_gamma_target_mult: 1.0
    gamma_intensity_threshold: 500000
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "exhausted_trend": trend_direction,
    "trend_strength": trend_strength,
    "total_delta": total_delta,
    "delta_decline": delta_decline,

    # === v2 new fields ===
    "liquidity_vacuum": liq_vacuum,
    "depth_bid_ask_ratio": round(bid_ask_ratio, 3),
    "depth_spread_current": round(current_spread, 4),
    "depth_spread_mean": round(mean_spread, 4),
    "spread_widening_mult": round(current_spread / mean_spread, 2) if mean_spread else 0,
    "iv_acceleration": round(iv_accel, 4),
    "iv_accel_aligned": iv_accel_aligned,
    "wall_proximity_pct": round(wall_dist_pct, 4),
    "nearest_wall_type": nearest_wall_type,  # "call" or "put" or None
    "wall_proximity_bonus": wall_proximity_bonus,
    "regime": regime,
    "regime_target_mult": regime_target_mult,
    "net_gamma": round(net_gamma, 2),
    "risk": round(risk, 2),
    "risk_reward_ratio": rr_ratio,
}
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/layer2/delta_volume_exhaustion.py` | Replace `_check_volume_decline` → `_check_liquidity_vacuum`, add `_check_iv_acceleration`, `_check_wall_proximity`, `_compute_regime_target_mult`, update `_compute_confidence`, update `evaluate` to accept `gex_calculator`, update metadata |
| `config/strategies.yaml` | Add 10 new params under `delta_volume_exhaustion` |

**No changes needed:** `main.py`, `strategies/layer2/__init__.py`, `strategies/rolling_keys.py` — all required keys and data sources already available.

---

## Acceptance Criteria

1. ✅ `_check_liquidity_vacuum()` uses `depth_snapshot` bid/ask ratio + spread widening
2. ✅ `_check_iv_acceleration()` uses `KEY_IV_SKEW_5M` rolling window
3. ✅ `_check_wall_proximity()` uses `gex_calc.get_gamma_walls()` with 0.3% threshold
4. ✅ Regime-adaptive targets scale by NEG/POS/NEUTRAL gamma
5. ✅ Hard gates: delta decline AND liquidity vacuum must both pass
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ New metadata fields in signal output
8. ✅ Config params added to strategies.yaml
9. ✅ All existing tests pass (no regression)
10. ✅ Commit message follows v2 naming convention: `feat(exhaustion): v2 Exhaustion-Master upgrade`

---

## Data Reference (from LEVEL2_DATA_SAMPLES.jsonl)

**Liquidity vacuum patterns:**
- `depthagg`: balanced depth (2019/2270, spread=0.09) → exhaustion candidate
- `depthagg`: thin bids (1940/2217, spread=0.04) → early exhaustion
- `depthagg`: extreme imbalance (8061/639, spread=0.05) → NOT exhaustion, trend continuation

**IV acceleration patterns:**
- `optionchain`: ATM put IV=0.60, call IV=0.60 → neutral
- `optionchain`: OTM put IV=1.05 → elevated fear (blow-off top signal)
- `optionchain`: OTM call IV spikes → capitulation bottom signal

**Wall proximity patterns:**
- `optionchain`: ATM gamma peak (0.0627) at 420 → major gamma wall
- `optionchain`: Deep ITM call delta=0.97 → dealer hedging zone
- `optionchain`: High volume call (56k vol) at 425 → speculative flow, potential wall

**Exchange-level patterns:**
- `depthquotes`: MEMX wall 2040 shares on asks → structural resistance
- `depthquotes`: BATS 80 shares on bids → demand signal
- `depthquotes`: 8-exchange ask diversity → deep liquidity, NOT exhaustion
