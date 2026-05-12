# gamma_volume_convergence v2 — "Ignition-Master" Upgrade

**Strategy:** `strategies/layer3/gamma_volume_convergence.py`
**Config:** `config/strategies.yaml` → `layer3.gamma_volume_convergence`
**Data Source:** `data/level2/LEVEL2_DATA_SAMPLES.jsonl`

---

## Problem Statement

Current `gamma_volume_convergence` is a solid micro-signal strategy but has 3 blind spots:
1. **Volume is unweighted** — a volume spike of passive limit orders is treated the same as aggressive market orders. We need **aggressor-weighted volume** to distinguish real ignition from passive rotation.
2. **Gamma spike is 1st derivative** — we check if gamma is above average, but not if the *rate of gamma growth* is accelerating. A sudden change in gamma growth rate ("jerk") is more predictive.
3. **No Delta-Gamma coupling check** — if gamma spikes but delta doesn't move proportionally, it's likely a phantom spike (single large contract update). We need a **Delta-Gamma correlation gate**.
4. **Fixed target** — 1.0% target regardless of volatility regime. In high-vol environments this is too tight; in low-vol it's too loose.

Synapse's proposal: add **Aggressor-Weighted Volume**, **Gamma Acceleration (2nd derivative)**, **Delta-Gamma Coupling Gate**, and **ATR-Normalized Targets**.

---

## v2 Architecture

### New Confidence Components (6 total)

| # | Component | Weight | Type | Source |
|---|-----------|--------|------|--------|
| 1 | Delta Acceleration | 0.15 | soft | current total_delta / rolling avg (unchanged) |
| 2 | **Gamma Acceleration** | 0.20 | **hard gate** | 2nd derivative of gamma (was 1st derivative) |
| 3 | **Aggressor-Weighted Volume** | 0.15 | **hard gate** | VolumeUp/Down ratio × market order aggressor (was simple volume spike) |
| 4 | **Delta-Gamma Coupling** | 0.10 | **hard gate** | Delta and gamma must move in lockstep (NEW) |
| 5 | ATR-Normalized Target | 0.10 | soft | target scales with ATR (was fixed 1.0%) |
| 6 | Wall Proximity | 0.05 | soft | proximity to gamma wall (unchanged) |

**New min confidence: 0.35** (up from 0.25 — higher bar for micro-signals)

---

## Phase 1: Aggressor-Weighted Volume — The Conviction Filter

**Goal:** Replace simple volume spike check with **aggressor-weighted volume** that distinguishes market orders (aggressive) from limit orders (passive).

**Logic:**
1. Use `KEY_VOLUME_UP_5M` and `KEY_VOLUME_DOWN_5M` rolling windows (already available)
2. Compute **aggressor ratio** = VolumeUp / (VolumeUp + VolumeDown) — this measures what fraction of total volume is aggressive buying vs selling
3. For **LONG ignition:** aggressor_ratio should be > 0.60 (majority of volume is aggressive buying)
4. For **SHORT ignition:** aggressor_ratio should be < 0.40 (majority of volume is aggressive selling)
5. **Hard gate:** aggressor_ratio must exceed the threshold (60% for LONG, 40% for SHORT)
6. **Volume spike check:** VolumeUp (for LONG) or VolumeDown (for SHORT) must be > 1.20× rolling average (slightly raised from 1.15)

**Why this works:** A volume spike of passive limit orders being filled is just rotation — the market is absorbing orders, not aggressively pushing price. A volume spike where 80%+ is market orders (aggressive) means real conviction — traders are hitting the bid/ask, not resting. This distinguishes "real" ignition from "passive" rotation.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- `quotes_parsed`: VolumeUp/VolumeDown tracking available via rolling windows
- `depthquotes_parsed`: Individual market maker quotes with order counts — can infer aggressor direction from timestamp patterns
- `depthagg_parsed`: Total bid/ask sizes — if bid sizes are collapsing while ask sizes are growing, that's aggressive selling

**Config params to add:**
```yaml
aggressor_ratio_threshold_long: 0.60    # VolumeUp must be >60% of total for LONG
aggressor_ratio_threshold_short: 0.40   # VolumeUp must be <40% of total for SHORT
volume_spike_ratio: 1.20                # Volume must be >120% of rolling avg
```

---

## Phase 2: Gamma Acceleration (2nd Derivative) — The "Jerk" Signal

**Goal:** Replace simple gamma spike ratio with **gamma acceleration** — the rate of change of the gamma growth rate.

**Current behavior:** `_check_gamma_spike()` returns `current_gamma / rolling_avg_gamma` — a 1st derivative.

**New behavior:**
1. Maintain a rolling window of gamma values (use `KEY_TOTAL_GAMMA_5M`)
2. Compute 1st derivative: `gamma_roc = (current_gamma - gamma_5_ago) / gamma_5_ago`
3. Compute 2nd derivative (acceleration): `gamma_accel = gamma_roc_current - gamma_roc_5_ago`
4. **Hard gate:** `gamma_accel > 0.10` (gamma growth rate is increasing by ≥10%)
5. For **SHORT:** same gamma acceleration gate (gamma spikes in both squeeze and fade scenarios)

**Why this works:** A gamma spike where gamma is growing at a constant rate is expected — dealers are hedging normally. A gamma spike where the *rate of growth* is accelerating means dealers are entering a self-reinforcing hedging loop — that's the ignition point. The 2nd derivative catches this inflection.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- `optionchain_parsed`: ATM Call (420C) gamma=0.0627, ATM Put (420P) gamma=0.0627 → high gamma zone
- `optionchain_parsed`: OTM Call (425C) gamma=0.043 → moderate gamma
- `optionchain_parsed`: OTM Put (395P) gamma=0.0025 → low gamma
- If gamma goes from 0.043 → 0.0627 → 0.080 → acceleration is increasing → ignition

**Config params to add:**
```yaml
gamma_accel_window: 5                 # window for gamma ROC calculation
gamma_accel_threshold: 0.10           # gamma acceleration must exceed this
```

**Rolling key to add:** `KEY_GAMMA_ACCEL_5M` in `rolling_keys.py`

---

## Phase 3: Delta-Gamma Coupling Check — The Phantom Spike Filter

**Goal:** Ensure delta and gamma move in lockstep. If gamma spikes but delta doesn't, it's a phantom spike.

**Logic:**
1. Get delta acceleration ratio: `delta_accel = current_delta / rolling_avg_delta`
2. Get gamma acceleration: `gamma_accel` (from Phase 2)
3. Compute coupling: `coupling = abs(delta_accel - 1.0) / gamma_accel`
   - For LONG: delta should be rising (delta_accel > 1.0) AND gamma should be spiking
   - For SHORT: delta should be declining (delta_accel < 1.0) AND gamma should be spiking
4. **Hard gate:** `abs(delta_accel - 1.0) >= gamma_accel * 0.5`
   - Delta movement must be at least 50% of gamma movement
   - If delta barely moves while gamma spikes → phantom spike → skip
5. If coupling passes → confidence += 0.10 (strong coupling = high conviction)

**Why this works:** A single large contract update can cause a gamma spike without real market movement. If delta (the directional pressure) isn't moving proportionally to gamma, the signal is likely noise. True ignition requires BOTH delta and gamma to move together.

**Config params to add:**
```yaml
coupling_min_ratio: 0.5               # delta movement must be ≥50% of gamma movement
```

---

## Phase 4: ATR-Normalized Targets — The Dynamic Exit

**Goal:** Replace fixed 1.0% target with **ATR-normalized target** that scales with current volatility.

**Current behavior:** `target = entry * (1 ± 0.010)` — fixed 1.0% regardless of volatility.

**New behavior:**
1. Compute ATR from price rolling window: `ATR = price_window.std × sqrt(252)` (annualized) or use rolling window standard deviation directly
2. For micro-scalping, use 5-minute ATR: `atr_5m = price_window.std`
3. **LONG target:** `target = entry + atr_5m * ATR_MULT`
4. **SHORT target:** `target = entry - atr_5m * ATR_MULT`
5. ATR_MULT = 1.5 (target is 1.5× the 5-minute volatility)
6. Minimum target: 0.3% (don't scalp for less than 0.3%)
7. Maximum target: 2.0% (don't scalp for more than 2.0%)

**Why this works:** In high-volatility environments (large ATR), a 1.0% target is too tight — the price swings too much. A wider target (e.g., 1.5× ATR) gives the scalp room to breathe. In low-volatility environments (small ATR), a 1.0% target might be 5× the normal range — too loose, risk of giving back profits. ATR-normalized targets adapt to the current market regime.

**Data reference (from LEVEL2_DATA_SAMPLES.jsonl):**
- `quotes_parsed`: TSLA high=425.70, low=418.65 → intraday range ~7 points → high vol
- `quotes_parsed`: TSLA spread ~0.07 → tight spread → low vol
- Wider range = higher ATR = wider target
- Tighter range = lower ATR = tighter target

**Config params to add:**
```yaml
atr_mult: 1.5                         # target = ATR × 1.5
atr_min_target_pct: 0.003             # minimum 0.3% target
atr_max_target_pct: 0.020             # maximum 2.0% target
```

---

## Phase 5: Confidence Recalculation

**New `_compute_confidence()` structure:**

```python
def _compute_confidence(
    self, price, delta_accel, gamma_accel,
    aggressor_ratio, atr_mult, direction,
    net_gamma, gex_calc,
) -> float:
    # 1. Delta acceleration (0.0–0.15)
    delta_conf = self._delta_accel_confidence(delta_accel)

    # 2. Gamma acceleration (hard gate — 0.0 or 0.20)
    gamma_conf = 0.20 if gamma_accel else 0.0

    # 3. Aggressor-weighted volume (hard gate — 0.0 or 0.15)
    vol_conf = 0.15 if aggressor_ratio else 0.0

    # 4. Delta-gamma coupling (hard gate — 0.0 or 0.10)
    coupling_conf = 0.10 if coupling_passes else 0.0

    # 5. ATR-normalized target quality (soft — 0.0–0.10)
    target_conf = self._atr_target_confidence(atr_mult)

    # 6. Wall proximity (soft — 0.05–0.10)
    wall_conf = self._wall_proximity_confidence(price, direction, gex_calc)

    confidence = delta_conf + gamma_conf + vol_conf + coupling_conf + target_conf + wall_conf
    return min(MAX_CONFIDENCE, max(0.0, confidence))
```

**Hard gates (all must pass for signal):**
- Gamma acceleration > 0.10 (2nd derivative confirms ignition)
- Aggressor ratio > 60% (LONG) or < 40% (SHORT) (real conviction)
- Delta-gamma coupling ≥ 0.5 (not a phantom spike)

**Soft factors (boost confidence but don't block):**
- Delta acceleration magnitude
- ATR-normalized target quality
- Wall proximity

---

## Phase 6: Config Updates

**Add to `config/strategies.yaml` under `layer3.gamma_volume_convergence`:**

```yaml
gamma_volume_convergence:
  enabled: true
  tracker:
    max_hold_seconds: 900
  params:
    # === v1 params (kept for backwards compat) ===
    delta_accel_ratio: 1.15
    gamma_spike_ratio: 1.20
    volume_spike_ratio: 1.20
    stop_pct: 0.005
    target_pct: 0.010
    min_confidence: 0.35          # raised from 0.25
    max_confidence: 0.90
    min_data_points: 3

    # === v2 Ignition-Master params ===
    # Aggressor-weighted volume
    aggressor_ratio_threshold_long: 0.60
    aggressor_ratio_threshold_short: 0.40
    volume_spike_ratio: 1.20

    # Gamma acceleration
    gamma_accel_window: 5
    gamma_accel_threshold: 0.10

    # Delta-gamma coupling
    coupling_min_ratio: 0.5

    # ATR-normalized targets
    atr_mult: 1.5
    atr_min_target_pct: 0.003
    atr_max_target_pct: 0.020
```

---

## Phase 7: Signal Metadata Updates

**Expand Signal metadata dict to include new v2 fields:**

```python
metadata = {
    # === v1 fields (kept) ===
    "atm_strike": ...,
    "delta_acceleration_ratio": ...,
    "gamma_spike_ratio": ...,
    "volume_up/down_spike": ...,
    "price_trend": ...,
    "rolling_trend": ...,
    "net_gamma": ...,
    "regime": ...,
    "wall_above/below": ...,
    "distance_to_wall_pct": ...,
    "risk": ...,
    "risk_reward_ratio": ...,

    # === v2 new fields ===
    "gamma_acceleration": round(gamma_accel, 4),       # 2nd derivative
    "gamma_accel_window": gamma_accel_window_count,     # data points used
    "aggressor_ratio": round(aggressor_ratio, 3),       # VolumeUp / total
    "coupling_ratio": round(coupling, 4),               # delta-gamma coupling
    "atr_value": round(atr_5m, 4),                      # 5-min ATR
    "target_mult": round(target_mult, 2),               # ATR multiplier used
    "target_pct_actual": round(actual_target_pct, 4),   # actual target % from entry
}
```

---

## Phase 8: Rolling Window Key Addition

**Add to `strategies/rolling_keys.py`:**

```python
# --- Gamma acceleration tracking (gamma_volume_convergence v2) ---
KEY_GAMMA_ACCEL_5M = "gamma_accel_5m"
```

Include in `ALL_KEYS` tuple.

**Add to `main.py`** in `_update_rolling_data()`:
- Compute gamma acceleration: get gamma ROC over last 5 points, compute 2nd derivative, push to rolling key

---

## Files to Modify

| File | Changes |
|------|---------|
| `strategies/rolling_keys.py` | Add `KEY_GAMMA_ACCEL_5M` |
| `main.py` | Add rolling key init + push gamma acceleration |
| `strategies/layer3/gamma_volume_convergence.py` | Full v2 rewrite — aggressor volume, gamma accel, coupling gate, ATR targets |
| `config/strategies.yaml` | Add 12 new params under `gamma_volume_convergence` |

**No changes needed:** `strategies/layer3/__init__.py` — no registration changes.

---

## Acceptance Criteria

1. ✅ `_check_aggressor_volume()` computes aggressor ratio from VolumeUp/VolumeDown
2. ✅ `_check_gamma_acceleration()` computes 2nd derivative of gamma
3. ✅ `_check_delta_gamma_coupling()` verifies delta and gamma move in lockstep
4. ✅ `_compute_atr_target()` scales target with 5-minute ATR
5. ✅ Hard gates: gamma acceleration AND aggressor ratio AND delta-gamma coupling
6. ✅ Min confidence raised from 0.25 → 0.35
7. ✅ Rolling key `KEY_GAMMA_ACCEL_5M` added and populated in main.py
8. ✅ New metadata fields in signal output
9. ✅ Config params added to strategies.yaml
10. ✅ Import passes: `python3 -c "from strategies.layer3.gamma_volume_convergence import GammaVolumeConvergence; print('OK')"`
11. ✅ Commit message: `feat(gvc): v2 Ignition-Master upgrade`

---

## Data Reference (from LEVEL2_DATA_SAMPLES.jsonl)

**Aggressor volume patterns:**
- `quotes_parsed`: VolumeUp/VolumeDown tracking available
- If VolumeUp = 8000, VolumeDown = 2000 → aggressor_ratio = 0.80 (strong bullish conviction)
- If VolumeUp = 2000, VolumeDown = 8000 → aggressor_ratio = 0.20 (strong bearish conviction)
- If VolumeUp = 5000, VolumeDown = 5000 → aggressor_ratio = 0.50 (balanced, no conviction)

**Gamma acceleration patterns:**
- `optionchain_parsed`: ATM gamma=0.0627 → baseline
- `optionchain_parsed`: If gamma goes 0.043 → 0.0627 → 0.080 → ROC1=0.45, ROC2=0.29 → acceleration positive → ignition
- `optionchain_parsed`: If gamma goes 0.0627 → 0.0627 → 0.0627 → ROC1=0, ROC2=0 → no acceleration → no ignition

**Delta-gamma coupling patterns:**
- True ignition: delta_accel = 1.30, gamma_accel = 0.20 → coupling = 0.30/0.20 = 1.5 ≥ 0.5 → PASS
- Phantom spike: delta_accel = 1.02, gamma_accel = 0.20 → coupling = 0.02/0.20 = 0.1 < 0.5 → FAIL

**ATR patterns:**
- `quotes_parsed`: TSLA high=425.70, low=418.65 → range ~7.05 → high vol → wide ATR → wider target
- `quotes_parsed`: TSLA spread ~0.07 → tight spread → low vol → narrow ATR → tighter target
