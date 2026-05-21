# Plan: Exchange Flow Asymmetry

## Synapse's Design Summary

**Core Insight:** Different exchanges have distinct "personality signatures." MEMX is the home of institutional accumulation (heavy bid-side liquidity). BATS is the epicenter of momentum sweeps (high-velocity aggressive orders). By tracking **signature deviation** — when a venue's behavior diverges from its own historical baseline — we detect genuine flow shifts, not just noise.

**Key Metrics:**
- **Venue-Specific Imbalance (ESI):** `(venue_bid - venue_ask) / (venue_bid + venue_ask)` — normalized -1.0 to +1.0
- **Baseline Deviation:** `current_ESI - EMA(ESI, 1h)` — detects signature breakouts from the venue's normal behavior
- **Venue Volume ROC:** `ROC(venue_volume, 10s)` — confirms real movement, not stale quotes
- **Venue Divergence Index:** `|baseline_deviation| / std(ESI, 1h)` — z-score style signal strength

**Signal Types:**
- **MEMX Accumulation (LONG):** ESI_MEMX > 0.8 + ROC(ESI_MEMX) > 0 + Gates A/B/C pass
- **BATS Sweep (SHORT):** ESI_BATS < -0.8 + ROC(ESI_BATS) < 0 + Gates A/B/C pass

**Target Hold Time:** 15–60 minutes (mid-term venue-driven trends)

**Heatmap Visual:** "Venue Signature" cell — Bright Gold (MEMX accumulation), Electric Blue (BATS momentum). Displays "Venue Divergence Index".

---

## Implementation Plan

### Step 1: Add Rolling Keys (`strategies/rolling_keys.py`)

Add 8 new key constants:

```python
# --- Exchange Flow Asymmetry ---
KEY_ESI_MEMX_5M = "esi_memx_5m"
KEY_ESI_MEMX_ROC_5M = "esi_memx_roc_5m"
KEY_ESI_BATS_5M = "esi_bats_5m"
KEY_ESI_BATS_ROC_5M = "esi_bats_roc_5m"
KEY_MEMX_VOL_RATIO_5M = "memx_vol_ratio_5m"
KEY_BATS_VOL_RATIO_5M = "bats_vol_ratio_5m"
KEY_ESI_BASELINE_MEMX_1H = "esi_baseline_memx_1h"
KEY_ESI_BASELINE_BATS_1H = "esi_baseline_bats_1h"
```

Add to `ALL_KEYS` tuple and `__all__` list.

### Step 2: Enrich Data Extraction in `main.py`

**Location:** Inside the `if msg_type == "market_depth_quotes":` block. Exchange data is already parsed for ExchangeFlowConcentration and ExchangeFlowImbalance. Extend the existing block.

**Compute ESI for MEMX and BATS:**
```python
# ── Exchange Flow Asymmetry: Venue Signature Tracking ──

# MEMX ESI
memx_total_size = memx_bid + memx_ask
esi_memx = (memx_bid - memx_ask) / memx_total_size if memx_total_size > 0 else 0.0

# BATS ESI
bats_total_size = bats_bid + bats_ask
esi_bats = (bats_bid - bats_ask) / bats_total_size if bats_total_size > 0 else 0.0

# Venue volume (total size across both sides)
memx_vol = memx_total_size
bats_vol = bats_total_size

# Venue volume ratio (current vs 5m average)
memx_vol_ratio = 0.0
memx_vol_rw = rolling_data.get(KEY_MEMX_VOL_RATIO_5M)
if memx_vol_rw and memx_vol_rw.count >= 10:
    avg_vol = sum(memx_vol_rw.values) / len(memx_vol_rw.values) if memx_vol_rw.values else 1.0
    memx_vol_ratio = memx_vol / avg_vol if avg_vol > 0 else 1.0

bats_vol_ratio = 0.0
bats_vol_rw = rolling_data.get(KEY_BATS_VOL_RATIO_5M)
if bats_vol_rw and bats_vol_rw.count >= 10:
    avg_vol = sum(bats_vol_rw.values) / len(bats_vol_rw.values) if bats_vol_rw.values else 1.0
    bats_vol_ratio = bats_vol / avg_vol if avg_vol > 0 else 1.0

# ESI ROC (rate of change over lookback)
esi_memx_roc = 0.0
esi_memx_rw = rolling_data.get(KEY_ESI_MEMX_5M)
if esi_memx_rw and esi_memx_rw.count >= 10:
    past_esi = esi_memx_rw.values[-10] if esi_memx_rw.values[-10] != 0 else 0.001
    esi_memx_roc = (esi_memx - past_esi) / abs(past_esi)

esi_bats_roc = 0.0
esi_bats_rw = rolling_data.get(KEY_ESI_BATS_5M)
if esi_bats_rw and esi_bats_rw.count >= 10:
    past_esi = esi_bats_rw.values[-10] if esi_bats_rw.values[-10] != 0 else -0.001
    esi_bats_roc = (esi_bats - past_esi) / abs(past_esi)

# Baseline deviation (ESI vs 1h rolling mean)
esi_baseline_memx = 0.0
esi_baseline_bats = 0.0
baseline_rw_memx = rolling_data.get(KEY_ESI_BASELINE_MEMX_1H)
baseline_rw_bats = rolling_data.get(KEY_ESI_BASELINE_BATS_1H)
if baseline_rw_memx and baseline_rw_memx.count >= 60:
    esi_baseline_memx = sum(baseline_rw_memx.values[-60:]) / min(60, baseline_rw_memx.count)
if baseline_rw_bats and baseline_rw_bats.count >= 60:
    esi_baseline_bats = sum(baseline_rw_bats.values[-60:]) / min(60, baseline_rw_bats.count)

memx_deviation = esi_memx - esi_baseline_memx
bats_deviation = esi_bats - esi_baseline_bats
```

**Push to rolling windows:**
```python
if KEY_ESI_MEMX_5M in rolling_data:
    rolling_data[KEY_ESI_MEMX_5M].push(esi_memx, ts)
if KEY_ESI_MEMX_ROC_5M in rolling_data:
    rolling_data[KEY_ESI_MEMX_ROC_5M].push(esi_memx_roc, ts)
if KEY_ESI_BATS_5M in rolling_data:
    rolling_data[KEY_ESI_BATS_5M].push(esi_bats, ts)
if KEY_ESI_BATS_ROC_5M in rolling_data:
    rolling_data[KEY_ESI_BATS_ROC_5M].push(esi_bats_roc, ts)
if KEY_MEMX_VOL_RATIO_5M in rolling_data:
    rolling_data[KEY_MEMX_VOL_RATIO_5M].push(memx_vol_ratio, ts)
if KEY_BATS_VOL_RATIO_5M in rolling_data:
    rolling_data[KEY_BATS_VOL_RATIO_5M].push(bats_vol_ratio, ts)
if KEY_ESI_BASELINE_MEMX_1H in rolling_data:
    rolling_data[KEY_ESI_BASELINE_MEMX_1H].push(esi_baseline_memx, ts)
if KEY_ESI_BASELINE_BATS_1H in rolling_data:
    rolling_data[KEY_ESI_BASELINE_BATS_1H].push(esi_baseline_bats, ts)
```

**Enrich `depth_snapshot`** in `_build_depth_snapshot()` with the new keys.

### Step 3: Create Strategy File

**Path:** `strategies/layer2/exchange_flow_asymmetry.py`

**Class:** `ExchangeFlowAsymmetry(BaseStrategy)`
- `strategy_id = "exchange_flow_asymmetry"`
- `layer = "layer2"`

**Signal Logic:**

```
MEMX ACCUMULATION (LONG):
    esi_memx > esi_threshold (0.8)
    AND esi_memx_roc > 0 (imbalance accelerating)
    AND memx_vol_ratio > volume_threshold (1.5× — volume spike)
    AND memx_deviation > deviation_threshold (significant baseline break)
    AND Gate A: cross-venue confluence (other exchanges show some movement)
    AND Gate B: total book alignment (OBI moves same direction as esi_memx)
    AND spread < 2× avg spread

BATS SWEEP (SHORT):
    esi_bats < -esi_threshold (-0.8)
    AND esi_bats_roc < 0 (imbalance accelerating down)
    AND bats_vol_ratio > volume_threshold (1.5× — volume spike)
    AND bats_deviation < -deviation_threshold (significant baseline break)
    AND Gate A: cross-venue confluence
    AND Gate B: total book alignment (OBI moves same direction as esi_bats)
    AND spread < 2× avg spread
```

**Hard Gates (all must pass):**
- Gate A: **Cross-Venue Confluence** — at least one other exchange (EDGX, ARCA) shows non-trivial movement. Prevents trading isolated "ghost" orders.
- Gate B: **Total Book Alignment** — `OBI` (overall bid/ask imbalance) moves in the same direction as the venue ESI. Ensures venue move isn't fighting the macro trend.
- Gate C: **Volume Threshold** — venue volume > 1.5× its 5-minute moving average. Confirms real liquidity movement.

**Confidence Model (5 components, sum to 1.0):**
1. ESI magnitude (0.0–0.30) — how extreme the venue imbalance is (0.8–1.0 maps to 0.0–0.30)
2. Baseline deviation (0.0–0.25) — z-score of deviation from 1h baseline
3. Volume confirmation (0.0–0.20) — volume ratio above 1.5×
4. Book alignment (0.0–0.15) — OBI direction matches venue ESI direction
5. Cross-venue confluence (0.0–0.10) — other exchanges also participating

**Parameters (from YAML config):**
```yaml
exchange_flow_asymmetry:
  enabled: true
  tracker:
    max_hold_seconds: 3600  # 60 min max for venue-driven trends
  params:
    esi_threshold: 0.8
    memx_deviation_threshold: 0.15
    bats_deviation_threshold: -0.15
    volume_ratio_threshold: 1.5
    min_confidence: 0.50
    max_confidence: 0.95
    stop_pct: 0.008  # 0.8% stop for trend trades
    target_risk_mult: 2.5
```

### Step 4: Register Strategy in `main.py`

**Import:** Add to layer2 imports
```python
from strategies.layer2.exchange_flow_asymmetry import ExchangeFlowAsymmetry
```

**Register:** Add to `_create_strategy_engine()` dict
```python
"exchange_flow_asymmetry": ExchangeFlowAsymmetry,
```

### Step 5: Add to Heatmap Config

**`config/heatmap.yaml`:** Add to Row 5, Col 5 (free slot):
```yaml
exchange_flow_asymmetry:
  row: 5
  col: 5
  span_cols: 1
  span_rows: 1
```

**`templates/heatmap.html`:** Add to `STRATEGIES` array (after `exchange_flow_imbalance`):
```javascript
{ id: "exchange_flow_asymmetry", name: "Flow Asymmetry", layer: "L2", group: "Venue Signature" },
```

### Step 6: Add to `config/strategies.yaml`

Add the strategy config block under `layer2:` section with the parameters from Step 3.

---

## File Change Summary

| File | Change |
|------|--------|
| `strategies/rolling_keys.py` | Add 8 new key constants, update ALL_KEYS |
| `main.py` | Enrich exchange data parsing with ESI + baseline + volume ratio, enrich depth_snapshot |
| `strategies/layer2/exchange_flow_asymmetry.py` | **NEW** — strategy class (~300 lines) |
| `strategies/layer2/__init__.py` | Add import for new strategy |
| `config/strategies.yaml` | Add strategy config block |
| `config/heatmap.yaml` | Add Row 5, Col 5 placement |
| `templates/heatmap.html` | Add to STRATEGIES array |

## Total: 7 files changed, ~430 lines added

## Key Design Decisions

1. **ESI threshold of ±0.8 is aggressive:** This is by design — Synapse wants only extreme venue imbalances. Most of the time, the signal won't fire, but when it does, it's a high-conviction move.

2. **Baseline deviation is the key differentiator:** Unlike ExchangeFlowImbalance which looks at absolute VSI levels, this strategy looks at **deviation from the venue's own history**. A MEMX ESI of 0.6 might be normal for MEMX, but if the 1h baseline is 0.1, that's a 0.5 deviation = significant signal.

3. **Cross-venue confluence gate:** Prevents trading isolated "ghost" orders on a single venue. If MEMX is extreme but EDGX/ARCA are flat, it might be a spoof or stale quote.

4. **Total book alignment gate:** Ensures the venue-level signal isn't fighting the overall market. If MEMX is bid-heavy but the total book is ask-heavy, the venue move might be a localized anomaly.

5. **Volume ratio as primary confirmation:** A venue imbalance backed by a 1.5× volume spike is real flow, not just quote padding.

6. **Longer hold time (60 min):** Venue-driven trends can persist for extended periods. This is a trend-following play, not a scalp.

7. **Uses existing exchange data pipeline:** The MEMX/BATS bid/ask sizes are already parsed in `main.py`. We extend that block rather than duplicating.
