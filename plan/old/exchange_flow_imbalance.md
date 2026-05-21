# Plan: Exchange Flow Imbalance

## Synapse's Design Summary

**Core Insight:** Not all liquidity is equal — different exchanges serve different market roles:
- **MEMX/BATS:** "Aggressor venues" — HFTs sweep here for aggressive directional flow
- **IEX:** "Passive venue" — speed bump, used for intent-driven/mean-reversion liquidity

**Key Metrics:**
- **Venue-Specific Imbalance (VSI):** `(exchange_bid - exchange_ask) / (exchange_bid + exchange_ask)` — normalized -1.0 to +1.0
- **Aggression Velocity:** `ROC(VSI, 10s)` — confirms imbalance is accelerating
- **IEX Intent Score:** `IEX_total_size / total_depth` — measures passive venue dominance
- **Venue Concentration:** What fraction of total book imbalance comes from aggressor venues

**Signal Types:**
- **Aggressive Buy Sweep (LONG):** VSI_MEMX/BATS > threshold + ROC > 0 + IEX intent low
- **Aggressive Sell Sweep (SHORT):** VSI_MEMX/BATS < threshold + ROC < 0 + IEX intent low

**Target Hold Time:** 10–45 minutes (venue-driven momentum)

**Heatmap Visual:** "Venue Pulse" cell — Electric Cyan for buy aggression, Deep Magenta for sell aggression. Displays "Venue Concentration Index".

---

## Implementation Plan

### Step 1: Add Rolling Keys (`strategies/rolling_keys.py`)

Add 6 new key constants:

```python
# --- Exchange Flow Imbalance ---
KEY_AGGRESSOR_VSI_5M = "aggressor_vsi_5m"
KEY_AGGRESSOR_VSI_ROC_5M = "aggressor_vsi_roc_5m"
KEY_IEX_INTENT_SCORE_5M = "iex_intent_score_5m"
KEY_MEMX_VSI_5M = "memx_vsi_5m"
KEY_BATS_VSI_5M = "bats_vsi_5m"
KEY_VENUE_CONCENTRATION_5M = "venue_concentration_5m"
```

Add to `ALL_KEYS` tuple and `__all__` list.

### Step 2: Enrich Data Extraction in `main.py`

**Location:** Inside the `if msg_type == "market_depth_quotes":` block. Exchange data is already being parsed for ExchangeFlowConcentration (~line 1247). We extend it with VSI calculations.

**Compute VSI for aggressor venues and IEX intent:**
```python
# ── Exchange Flow Imbalance: Venue-Specific Imbalance ──

# Aggressor venues combined (MEMX + BATS)
aggressor_bid = memx_bid + bats_bid
aggressor_ask = memx_ask + bats_ask
aggressor_total = aggressor_bid + aggressor_ask
aggressor_vsi = (aggressor_bid - aggressor_ask) / aggressor_total if aggressor_total > 0 else 0.0

# Individual venue VSI
memx_total = memx_bid + memx_ask
memx_vsi = (memx_bid - memx_ask) / memx_total if memx_total > 0 else 0.0

bats_total = bats_bid + bats_ask
bats_vsi = (bats_bid - bats_ask) / bats_total if bats_total > 0 else 0.0

# IEX intent score: fraction of total depth on IEX
iex_total = iex_bid + iex_ask
iex_intent_score = iex_total / total_depth if total_depth > 0 else 0.0

# Venue concentration: what fraction of total book imbalance comes from aggressor venues
total_imbalance = total_bid_size - total_ask_size
aggressor_imbalance = aggressor_bid - aggressor_ask
venue_concentration = abs(aggressor_imbalance) / abs(total_imbalance) if total_imbalance != 0 else 0.0

# VSI ROC (aggression velocity): rate of change over lookback
vsi_roc = 0.0
aggressor_rw = rolling_data.get(KEY_AGGRESSOR_VSI_5M)
if aggressor_rw and aggressor_rw.count >= 10:
    past_vsi = aggressor_rw.values[-10] if aggressor_rw.values[-10] != 0 else 0.001
    vsi_roc = (aggressor_vsi - past_vsi) / abs(past_vsi)
```

**Push to rolling windows:**
```python
if KEY_AGGRESSOR_VSI_5M in rolling_data:
    rolling_data[KEY_AGGRESSOR_VSI_5M].push(aggressor_vsi, ts)
if KEY_AGGRESSOR_VSI_ROC_5M in rolling_data:
    rolling_data[KEY_AGGRESSOR_VSI_ROC_5M].push(vsi_roc, ts)
if KEY_IEX_INTENT_SCORE_5M in rolling_data:
    rolling_data[KEY_IEX_INTENT_SCORE_5M].push(iex_intent_score, ts)
if KEY_MEMX_VSI_5M in rolling_data:
    rolling_data[KEY_MEMX_VSI_5M].push(memx_vsi, ts)
if KEY_BATS_VSI_5M in rolling_data:
    rolling_data[KEY_BATS_VSI_5M].push(bats_vsi, ts)
if KEY_VENUE_CONCENTRATION_5M in rolling_data:
    rolling_data[KEY_VENUE_CONCENTRATION_5M].push(venue_concentration, ts)
```

**Enrich `depth_snapshot`** in `_build_depth_snapshot()` with the new keys.

### Step 3: Create Strategy File

**Path:** `strategies/layer2/exchange_flow_imbalance.py`

**Class:** `ExchangeFlowImbalance(BaseStrategy)`
- `strategy_id = "exchange_flow_imbalance"`
- `layer = "layer2"`

**Signal Logic:**

```
AGGRESSIVE BUY SWEEP (LONG):
    aggressor_vsi > vsi_threshold (0.3)
    AND vsi_roc > 0 (imbalance accelerating)
    AND iex_intent_score < iex_threshold (0.15 — IEX not dominating)
    AND venue_concentration > concentration_threshold (0.3 — aggressor venues driving the move)
    AND spread < 2× avg spread

AGGRESSIVE SELL SWEEP (SHORT):
    aggressor_vsi < -vsi_threshold (-0.3)
    AND vsi_roc < 0 (imbalance accelerating down)
    AND iex_intent_score < iex_threshold (0.15)
    AND venue_concentration > concentration_threshold (0.3)
    AND spread < 2× avg spread
```

**Hard Gates (all must pass):**
- Gate A: `abs(aggressor_vsi) > vsi_threshold` — clear directional pressure on aggressor venues
- Gate B: `iex_intent_score < iex_threshold` — not a passive venue game
- Gate C: `venue_concentration > concentration_threshold` — aggressor venues are primary drivers
- Gate D: `spread < max_spread_mult × avg_spread` — scalp must be profitable

**Confidence Model (7 components, sum to 1.0):**
1. VSI magnitude (0.0–0.25) — how extreme the venue imbalance is
2. VSI velocity (0.0–0.20) — accelerating or decelerating
3. IEX intent suppression (0.0–0.15) — low IEX = higher conviction
4. Venue concentration (0.0–0.10) — aggressor venues driving the move
5. Volume confirmation (0.0–0.10) — volume supports the direction
6. VAMP validation (0.0–0.10) — VAMP direction aligns
7. GEX regime alignment (0.0–0.10) — matches GEX bias

**Parameters (from YAML config):**
```yaml
exchange_flow_imbalance:
  enabled: true
  tracker:
    max_hold_seconds: 2700  # 45 min max for venue momentum
  params:
    vsi_threshold: 0.3
    vsi_roc_threshold: 0.0
    iex_intent_threshold: 0.15
    venue_concentration_threshold: 0.3
    max_spread_mult: 2.0
    stop_pct: 0.005  # 0.5% stop for venue momentum
    target_risk_mult: 2.0
    min_confidence: 0.40
    max_confidence: 0.95
```

### Step 4: Register Strategy in `main.py`

**Import:** Add to layer2 imports (~line 157)
```python
from strategies.layer2.exchange_flow_imbalance import ExchangeFlowImbalance
```

**Register:** Add to `_create_strategy_engine()` dict (~line 649)
```python
"exchange_flow_imbalance": ExchangeFlowImbalance,
```

### Step 5: Add to Heatmap Config

**`config/heatmap.yaml`:** Add to Row 5, Col 4 (free slot):
```yaml
exchange_flow_imbalance:
  row: 5
  col: 4
  span_cols: 1
  span_rows: 1
```

**`templates/heatmap.html`:** Add to `STRATEGIES` array (after `participant_divergence_scalper`):
```javascript
{ id: "exchange_flow_imbalance", name: "Flow Imbalance", layer: "L2", group: "Venue Flow" },
```

### Step 6: Add to `config/strategies.yaml`

Add the strategy config block under `layer2:` section with the parameters from Step 3.

---

## File Change Summary

| File | Change |
|------|--------|
| `strategies/rolling_keys.py` | Add 6 new key constants, update ALL_KEYS |
| `main.py` | Enrich exchange data parsing with VSI + IEX intent + venue concentration, enrich depth_snapshot |
| `strategies/layer2/exchange_flow_imbalance.py` | **NEW** — strategy class (~300 lines) |
| `strategies/layer2/__init__.py` | Add import for new strategy |
| `config/strategies.yaml` | Add strategy config block |
| `config/heatmap.yaml` | Add Row 5, Col 4 placement |
| `templates/heatmap.html` | Add to STRATEGIES array |

## Total: 7 files changed, ~450 lines added

## Key Design Decisions

1. **VSI normalized to -1.0 to +1.0:** Unlike raw ratios, VSI is a clean normalized metric. +1.0 = all bids on venue, -1.0 = all asks, 0.0 = balanced.

2. **IEX intent as a filter, not a signal:** High IEX presence suppresses signals rather than triggering them. IEX dominance = passive market = no directional edge.

3. **Venue concentration gate:** Ensures aggressor venues (MEMX/BATS) are actually driving the move, not just participating. If total imbalance is driven by ARCA/EDGX but aggressor venues are flat, it's not a venue-driven signal.

4. **Symmetric thresholds for LONG/SHORT:** VSI > 0.3 triggers LONG, VSI < -0.3 triggers SHORT. Same thresholds, opposite directions.

5. **Longer hold time (45 min) than other L2 strategies:** Venue-driven momentum tends to persist longer than microstructure noise. This is a momentum play, not a scalp.

6. **Leverages existing exchange data pipeline:** Exchange bid/ask sizes are already parsed in `main.py` for ExchangeFlowConcentration. We extend that block rather than duplicating.
