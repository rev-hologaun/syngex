# call_put_flow_asymmetry v2 — "Flow-Velocity" Upgrade

**Strategy:** `strategies/layer2/call_put_flow_asymmetry.py`
**Config:** `config/strategies.yaml` → `layer2.call_put_flow_asymmetry`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `call_put_flow_asymmetry` is a **state-based** indicator. It detects that an imbalance exists, but not how fast it's forming. A high ratio that's been stable for 30 minutes is less actionable than one that just spiked from 1.2× to 2.5× in the last tick. The strategy also can't distinguish between broad-based flow across the chain vs. concentrated flow on a single strike (which could be a single large player = noise).

Synapse's proposal: add **Flow ROC** (acceleration), **Flow Breadth** (strike distribution), and **Regime-Adaptive Scaling** (gamma magnitude multiplier).

---

## v2 Architecture

### New Confidence Components (7 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | Flow Ratio Magnitude | 0.15 | soft | call_score / put_score (unchanged, enhanced with ROC) |
| 2 | **Flow Acceleration** | 0.20 | **hard gate** | flow_ratio ROC (was flat, now rising) |
| 3 | **Flow Breadth** | 0.15 | **hard gate** | active_strike_count / total_active_strikes |
| 4 | IV Skew Alignment | 0.15 | soft | call IV vs put IV (unchanged) |
| 5 | Volume Alignment | 0.10 | soft | volume_up / volume_down (unchanged) |
| 6 | **Regime Intensity** | 0.10 | soft | abs(net_gamma) magnitude (was binary bonus) |
| 7 | **Wall Proximity Bonus** | +0.10 | **bonus** | gamma walls proximity |

**New min confidence: 0.40** (up from 0.35 — catches only the most explosive flow shifts)

---

## Phase 1: Flow Acceleration (ROC) — The Leading Indicator

**Goal:** Replace static flow ratio check with rate-of-change detection. Catch the exact moment the imbalance SPIKES.

**Logic:**
1. Maintain a rolling window of `flow_ratio` values in `rolling_data` using new key `KEY_FLOW_RATIO_5M`
2. Compute ROC over last 5 data points: `flow_roc = (current_ratio - ratio_5_ago) / ratio_5_ago`
3. **Hard gate:** `flow_roc > 0.20` (ratio has increased ≥20% in last 5 ticks)
4. For **call-dominant:** ratio should be rising (accelerating bullish flow)
5. For **put-dominant:** ratio should be falling (accelerating bearish flow) → check `1/ratio` ROC

**Why this works:** A flow imbalance that's been building slowly is the market digesting info. A sudden spike is the market **reacting** — that's when the explosive move happens. The ROC catches the inflection point.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- OTM Call (425C): vol=56k, OI=4k → high volume, speculative bullish flow
- ATM Call (420C): vol=26k, OI=4.6k → moderate flow
- OTM Put (395P): vol=344, OI=1.8k, IV=1.05 → low volume, high IV (hedging)

If call scores go from 500 → 800 in 5 ticks, that's a 60% ROC — explosive signal.
If call scores go from 500 → 550 in 5 ticks, that's 10% ROC — noise.

**Config params to add:**
```yaml
flow_ratio_roc_window: 5                # window for ROC calculation
flow_ratio_roc_threshold: 0.20           # ratio must have risen ≥20%
```

**Rolling key to add:** `KEY_FLOW_RATIO_5M` in `rolling_keys.py`
**main.py change:** Push `flow_ratio` to this key in `_update_rolling_data()`

---

## Phase 2: Flow Breadth (Strike Distribution) — The Conviction Filter

**Goal:** Ensure the flow imbalance is broad-based across the chain, not concentrated on one or two strikes.

**Logic:**
1. In `_calculate_flow_scores()`, track which strikes contribute to the flow
2. Count `active_strikes` (strikes with OI > 0 AND gamma > 0)
3. Count `total_strikes` (strikes with any OI > 0)
4. `flow_breadth = active_strikes / total_strikes`
5. **Hard gate:** `flow_breadth > 0.30` (at least 30% of strikes participating)
6. If breadth < 0.30 → flow concentrated on few strikes → likely single-player noise → skip

**Why this works:** A true "smart money" flow shift involves many strikes across the chain. A single large block on one strike (e.g., whale buying 10k contracts of a single OTM call) creates a skewed score but isn't market-wide conviction. Breadth filters out the noise.

**Data reference:**
- If flow comes from 420C, 422.5C, 425C, 427.5C, 430C → breadth ~0.5 (strong signal)
- If flow comes from 425C only → breadth ~0.1 (weak signal, single-strike whale)
- Deep ITM Call (382.5C): delta=0.97, IV=1.98, vol=9 → share substitute, low breadth contributor
- ATM options: gamma peak ~0.0627 → highest gamma contribution per contract

**Config params to add:**
```yaml
flow_breadth_threshold: 0.30             # min fraction of strikes participating
```

---

## Phase 3: Regime-Adaptive Scaling

**Goal:** Scale confidence by regime intensity (net gamma magnitude) instead of a binary directional bonus.

**Current behavior:** Binary regime alignment — LONG gets 0.10 in POSITIVE, 0.05 otherwise.

**New behavior:**
1. Compute `gamma_intensity = abs(net_gamma) / 1_000_000` (capped at 1.0)
2. **High gamma regime** (gamma_intensity > 0.5): confidence × 1.3 (flow in strong gamma = explosive)
3. **Medium gamma** (0.2–0.5): confidence × 1.0 (baseline)
4. **Low gamma** (gamma_intensity < 0.2): confidence × 0.8 (flow in flat market = less conviction)

**Why this works:** In a high-gamma regime, dealers are heavily hedging. Any flow imbalance gets amplified by dealer positioning. In a low-gamma regime, the same flow imbalance may not move the needle.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- `depthagg`: extreme bid pressure (8061/639 = ratio 12.62) → positive gamma regime → flow amplified
- `depthagg`: balanced depth (2019/2270) → neutral gamma → baseline flow
- `depthagg`: ask pressure (1940/2217 = ratio 0.88) → negative gamma regime → flow amplified

**Config params to add:**
```yaml
gamma_intensity_high_threshold: 500000   # above = high gamma regime
gamma_intensity_low_threshold: 200000    # below = low gamma regime
gamma_intensity_high_mult: 1.3           # high gamma multiplier
gamma_intensity_low_mult: 0.8            # low gamma multiplier
```

---

## Phase 4: Wall Proximity Bonus

**Goal:** Add a confidence bonus when flow asymmetry occurs near a major gamma wall.

**Logic:**
1. Get gamma walls via `gex_calc.get_gamma_walls(threshold=500_000)`
2. Compute distance from current price to nearest wall (call or put)
3. If distance < 0.5% of price → `confidence += 0.10`
4. Bonus is direction-aware:
   - Call-dominant + nearby **call wall** above price → bonus (calls pushing toward resistance)
   - Put-dominant + nearby **put wall** below price → bonus (puts pushing toward support)
   - Wrong side → no bonus

**Why this works:** A flow imbalance near a gamma wall is a structural clash — smart money flow pushing against dealer hedging. If the flow wins, the wall breaks = explosive move.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- ATM Call (420C): gamma=0.0627 → major gamma wall at 420
- ATM Put (420P): gamma=0.0627 → major gamma wall at 420
- OTM Call (425C): gamma=0.043 → secondary wall at 425
- OTM Put (395P): gamma=0.0025 → weak wall at 395

**Config params to add:**
```yaml
wall_proximity_pct: 0.005              # within 0.5% of wall
wall_proximity_bonus: 0.10             # confidence bonus
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence()` structure:**

```python
def _compute_confidence(
    self, flow_ratio, flow_roc, flow_breadth,
    iv_aligned, vol_aligned, net_gamma, regime,
    direction, gex_calc, price,
) -> float:
    # 1. Flow ratio magnitude (0.0–0.15)
    ratio_conf = self._ratio_confidence(flow_ratio)

    # 2. Flow acceleration (hard gate — 0.0 or 0.20)
    accel_conf = 0.20 if flow_roc else 0.0

    # 3. Flow breadth (hard gate — 0.0 or 0.15)
    breadth_conf = 0.15 if flow_breadth else 0.0

    # 4. IV skew alignment (soft — 0.0–0.15)
    iv_conf = 0.15 if iv_aligned else 0.0

    # 5. Volume alignment (soft — 0.0–0.10)
    vol_conf = 0.10 if vol_aligned else 0.0

    # 6. Regime intensity (soft — 0.0–0.10)
    regime_conf = self._regime_intensity_confidence(net_gamma)

    confidence = ratio_conf + accel_conf + breadth_conf + iv_conf + vol_conf + regime_conf

    # 7. Wall proximity bonus (+0.0 to +0.10)
    wall_bonus = self._wall_proximity_bonus(gex_calc, price, direction)
    confidence += wall_bonus

    return min(1.0, max(0.0, confidence))
```

**Hard gates (all must pass for signal):**
- Flow ratio threshold (unchanged: >1.5× or <0.66×)
- Flow ROC > 0.20 (acceleration)
- Flow breadth > 0.30 (broad-based)

**Soft factors (boost confidence but don't block):**
- IV skew alignment
- Volume alignment
- Regime intensity
- Wall proximity bonus

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `layer2.call_put_flow_asymmetry`:**

```yaml
call_put_flow_asymmetry:
  enabled: true
  tracker:
    max_hold_seconds: 3600
  params:
    # === v1 params (kept for backwards compat) ===
    flow_threshold: 1.5
    iv_skew_threshold: 0.03
    stop_pct: 0.006
    target_risk_mult: 2.0
    min_confidence: 0.40          # raised from 0.35

    # === v2 Flow-Velocity params ===
    # Flow acceleration
    flow_ratio_roc_window: 5
    flow_ratio_roc_threshold: 0.20

    # Flow breadth
    flow_breadth_threshold: 0.30

    # Regime intensity
    gamma_intensity_high_threshold: 500000
    gamma_intensity_low_threshold: 200000
    gamma_intensity_high_mult: 1.3
    gamma_intensity_low_mult: 0.8

    # Wall proximity
    wall_proximity_pct: 0.005
    wall_proximity_bonus: 0.10
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "call_flow_score": ...,
    "put_flow_score": ...,
    "flow_ratio": ...,
    "iv_skew": ...,
    "iv_aligned": ...,
    "volume_up/down": ...,
    "net_gamma": ...,
    "regime": ...,
    "risk": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "flow_roc": round(flow_roc, 4),            # rate of change
    "flow_roc_window": flow_roc_window_count,   # data points used
    "flow_breadth": round(flow_breadth, 3),     # 0.0–1.0
    "active_call_strikes": active_call_count,
    "active_put_strikes": active_put_count,
    "total_active_strikes": total_strike_count,
    "gamma_intensity": round(gamma_intensity, 3),
    "regime_mult": round(regime_mult, 2),
    "wall_proximity_pct": round(wall_dist_pct, 4),
    "nearest_wall_type": nearest_wall_type,     # "call", "put", or None
    "wall_proximity_bonus": wall_bonus,
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- Flow ratio tracking (call_put_flow_asymmetry v2) ---
KEY_FLOW_RATIO_5M = "flow_ratio_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
```python
# Push flow ratio to rolling window (for v2 flow acceleration)
if KEY_FLOW_RATIO_5M in self._rolling_data:
    # flow_ratio is available via gex_calc.get_iv_skew() or computed from scores
    # We need to pass it through from the strategy evaluation
    # Best approach: compute in main.py from greeks_summary
    ...
```

**Note:** Since flow_ratio is computed inside the strategy's `_calculate_flow_scores()`, we have two options:
- **Option A:** Compute flow_ratio in main.py and push to rolling key (cleaner, strategy-independent)
- **Option B:** Strategy computes flow_ratio and we add a callback to push it

**Recommendation Option A:** Add flow ratio computation in main.py near where greeks_summary is processed. This keeps the rolling window population centralized.

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_FLOW_RATIO_5M`, add to `ALL_KEYS` |
| `main.py` | Add rolling key initialization, add flow_ratio push in `_update_rolling_data()` |
| `strategies/layer2/call_put_flow_asymmetry.py` | Add flow ROC, flow breadth, regime scaling, wall proximity; update confidence; update metadata |
| `config/strategies.yaml` | Add 11 new params under `call_put_flow_asymmetry` |

---

## Acceptance Criteria

1. ✅ `_check_flow_acceleration()` computes flow_ratio ROC over rolling window
2. ✅ `_check_flow_breadth()` counts active strikes / total strikes
3. ✅ `_compute_regime_intensity()` scales confidence by gamma magnitude
4. ✅ `_check_wall_proximity()` adds +0.10 bonus near gamma walls
5. ✅ Hard gates: flow ratio threshold AND flow ROC AND flow breadth
6. ✅ Min confidence raised from 0.35 → 0.40
7. ✅ Rolling key `KEY_FLOW_RATIO_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.layer2.call_put_flow_asymmetry import CallPutFlowAsymmetry; print('OK')"`
11. ✅ Commit message: `feat(flow): v2 Flow-Velocity upgrade`

---

## Data Reference (from LEVEL2_DATA_SAMPLES.jsonl)

**Flow patterns (optionchain_parsed):**
- ATM Call (420C): vol=26k, OI=4.6k, delta=0.48, gamma=0.0627, IV=0.60 → strong flow, high gamma contribution
- OTM Call (425C): vol=56k, OI=4k, delta=0.22, gamma=0.043, IV=0.65 → HIGH volume, speculative bullish flow
- Deep ITM Call (382.5C): vol=9, OI=283, delta=0.97, gamma=0.003, IV=1.98 → low volume, share substitute, high IV
- ATM Put (420P): vol=39k, OI=3k, delta=-0.52, gamma=0.0627, IV=0.60 → symmetric flow
- OTM Put (395P): vol=344, OI=1.8k, delta=-0.01, gamma=0.0025, IV=1.05 → low volume, high IV (hedging)

**Breadth indicators:**
- If flow is concentrated on 425C only → breadth low (single-strike whale)
- If flow spreads across 420C, 422.5C, 425C, 427.5C → breadth high (market-wide bullish)
- If put flow spreads across 420P, 417.5P, 415P, 412.5P → breadth high (market-wide bearish)

**Regime context (depthagg_parsed):**
- `depthagg`: extreme bid pressure (8061/639 = ratio 12.62) → positive gamma regime → flow amplified
- `depthagg`: balanced depth (2019/2270) → neutral gamma → baseline flow
- `depthagg`: ask pressure (1940/2217 = ratio 0.88) → negative gamma regime → flow amplified (opposite direction)

**Exchange-level context (depthquotes_parsed):**
- MEMX wall 2040 shares on asks → structural resistance, may cap call flow
- BATS 80 shares on bids → demand signal, supports put flow
- 8-exchange ask diversity → deep liquidity, flow needs more pressure to break through
