# Plan: Order Book Fragmentation

## Synapse's Design Summary

**Core Insight:** A large order book wall can be deceptive. We must distinguish between:
- **Fragile Walls (Spoof):** Massive size held by 1–2 participants. Easily pulled/flickered to manipulate price.
- **Robust Walls (Anchor):** Massive size distributed across many participants. Genuine institutional commitment, hard to move.

By measuring the **Fragmentation Ratio** — total size divided by number of unique participants at a level — we predict which walls will hold and which will crumble.

**Key Metrics:**
- **Fragility Index:** `1 / (num_participants × exchange_count)` averaged over top N levels — quantifies how "fake" a wall looks
- **Decay Velocity:** `ROC(level_size, 10 ticks)` — detects the instant a spoof is pulled
- **Concentration Check:** `max_participant_size / total_level_size` — identifies if one player dominates the level
- **Wall Significance:** Wall size vs average level size — ensures we're looking at a real wall, not noise

**Signal Types:**
- **Spoof Breach — LONG:** Fragile Ask Wall rapidly evaporates → price breaks through the fake resistance
- **Spoof Breach — SHORT:** Fragile Bid Wall rapidly evaporates → price breaks through the fake support
- **Robust Bounce — LONG:** Robust Bid Wall holds → price bounces off real support
- **Robust Bounce — SHORT:** Robust Ask Wall holds → price rejects off real resistance

**Target Hold Time:** 30 seconds – 5 minutes (high-frequency microstructure scalping)

**Heatmap Visual:** "Fragmentation Pulse" — Electric Yellow (fragile wall warning), Bright White (robust anchor). Displays "Fragility Score" (0.0–1.0).

---

## Implementation Plan

### Step 1: Add Rolling Keys (`strategies/rolling_keys.py`)

Add 6 new key constants:

```python
# --- Order Book Fragmentation ---
KEY_FRAGILITY_BID_5M = "fragility_bid_5m"
KEY_FRAGILITY_ASK_5M = "fragility_ask_5m"
KEY_DECAY_VELOCITY_BID_5M = "decay_velocity_bid_5m"
KEY_DECAY_VELOCITY_ASK_5M = "decay_velocity_ask_5m"
KEY_TOP_WALL_BID_SIZE_5M = "top_wall_bid_size_5m"
KEY_TOP_WALL_ASK_SIZE_5M = "top_wall_ask_size_5m"
```

Add to `ALL_KEYS` tuple and `__all__` list.

### Step 2: Enrich Data Extraction in `main.py`

**Location:** Inside the `if msg_type == "market_depth_quotes":` block.

**Data already available:**
- `num_participants` per level — already parsed in `depth_quotes_parsed`
- `bid_exchanges` / `ask_exchanges` per level — already available
- `bid_avg_participants` / `ask_avg_participants` — already computed in Participant Diversity Conviction section
- `bid_avg_exchanges` / `ask_avg_exchanges` — already computed
- `total_bid_size` / `total_ask_size` — already computed
- `depth_bid_levels` / `depth_ask_levels` — already computed

**Extend the existing exchange parsing block** (after Participant Divergence Scalper section, before the VAMP computation section) with:

```python
# ── Order Book Fragmentation: Structural Integrity Analysis ──

# Compute fragility for top N bid/ask levels
# Fragility = 1 / (num_participants × exchange_count), averaged over top N
def _compute_fragility(levels, top_n=5):
    if not levels or top_n == 0:
        return 0.0
    fragilities = []
    for lvl in levels[:top_n]:
        n_part = max(1, int(lvl.get("num_participants", 1)))
        n_exch = max(1, len(lvl.get("bid_exchanges", lvl.get("ask_exchanges", {}))))
        fragilities.append(1.0 / (n_part * n_exch))
    return sum(fragilities) / len(fragilities)

frag_bid = _compute_fragility(bids, top_n=5)
frag_ask = _compute_fragility(asks, top_n=5)

# Identify strongest wall per side (level with max size)
top_bid_level = max(bids, key=lambda b: int(b.get("Size", 0)), default=None)
top_ask_level = max(asks, key=lambda a: int(a.get("Size", 0)), default=None)

top_bid_wall_size = int(top_bid_level.get("Size", 0)) if top_bid_level else 0
top_ask_wall_size = int(top_ask_level.get("Size", 0)) if top_ask_level else 0

# Decay velocity: compare current wall size to size N ticks ago
decay_bid = 0.0
decay_ask = 0.0
if top_bid_wall_size > 0 and KEY_TOP_WALL_BID_SIZE_5M in rolling_data:
    rw = rolling_data[KEY_TOP_WALL_BID_SIZE_5M]
    if rw.count >= 5 and len(rw.values) >= 5:
        past_size = rw.values[-5] if rw.values[-5] > 0 else 1.0
        decay_bid = (top_bid_wall_size - past_size) / past_size
if top_ask_wall_size > 0 and KEY_TOP_WALL_ASK_SIZE_5M in rolling_data:
    rw = rolling_data[KEY_TOP_WALL_ASK_SIZE_5M]
    if rw.count >= 5 and len(rw.values) >= 5:
        past_size = rw.values[-5] if rw.values[-5] > 0 else 1.0
        decay_ask = (top_ask_wall_size - past_size) / past_size

# Push to rolling windows
if KEY_FRAGILITY_BID_5M in rolling_data:
    rolling_data[KEY_FRAGILITY_BID_5M].push(frag_bid, ts)
if KEY_FRAGILITY_ASK_5M in rolling_data:
    rolling_data[KEY_FRAGILITY_ASK_5M].push(frag_ask, ts)
if KEY_DECAY_VELOCITY_BID_5M in rolling_data:
    rolling_data[KEY_DECAY_VELOCITY_BID_5M].push(decay_bid, ts)
if KEY_DECAY_VELOCITY_ASK_5M in rolling_data:
    rolling_data[KEY_DECAY_VELOCITY_ASK_5M].push(decay_ask, ts)
if KEY_TOP_WALL_BID_SIZE_5M in rolling_data:
    rolling_data[KEY_TOP_WALL_BID_SIZE_5M].push(top_bid_wall_size, ts)
if KEY_TOP_WALL_ASK_SIZE_5M in rolling_data:
    rolling_data[KEY_TOP_WALL_ASK_SIZE_5M].push(top_ask_wall_size, ts)
```

**Enrich `depth_snapshot`** in `_build_depth_snapshot()` with the new keys.

### Step 3: Create Strategy File

**Path:** `strategies/layer2/order_book_fragmentation.py`

**Class:** `OrderBookFragmentation(BaseStrategy)`
- `strategy_id = "order_book_fragmentation"`
- `layer = "layer2"`

**Signal Logic:**

```
SPOOF BREACH — LONG (Fragile Ask Wall evaporates):
    frag_ask > frag_threshold (e.g., 0.5 — very fragile ask wall)
    AND decay_ask < -decay_threshold (ask wall rapidly shrinking)
    AND top_ask_wall_size > avg_wall_size × 3 (wall is significant)
    AND Gate A: wall significance
    AND Gate B: VAMP deviation spike (price moving into the vacuum)
    AND Gate C: volume/depth ratio low (liquidity evaporated, not consumed)

SPOOF BREACH — SHORT (Fragile Bid Wall evaporates):
    frag_bid > frag_threshold (very fragile bid wall)
    AND decay_bid < -decay_threshold (bid wall rapidly shrinking)
    AND top_bid_wall_size > avg_wall_size × 3 (wall is significant)
    AND Gate A: wall significance
    AND Gate B: VAMP deviation spike
    AND Gate C: volume/depth ratio low

ROBUST BOUNCE — LONG (Robust Bid Wall holds):
    frag_bid < frag_threshold (robust bid wall, many participants)
    AND decay_bid > -decay_threshold (wall holding, not shrinking)
    AND top_bid_wall_size > avg_wall_size × 3
    AND price near bid wall (within 0.1% of top bid)
    AND Gate A: wall significance
    AND Gate B: VAMP deviation spike (price approaching wall)
    AND Gate C: volume/depth ratio high (wall being consumed but holding)

ROBUST BOUNCE — SHORT (Robust Ask Wall holds):
    frag_ask < frag_threshold (robust ask wall)
    AND decay_ask > -decay_threshold (wall holding)
    AND top_ask_wall_size > avg_wall_size × 3
    AND price near ask wall (within 0.1% of top ask)
    AND Gate A: wall significance
    AND Gate B: VAMP deviation spike
    AND Gate C: volume/depth ratio high
```

**Hard Gates (all must pass):**
- Gate A: **Significance Gate** — wall size >= 3× average level size. Ensures we're looking at a real wall.
- Gate B: **The "Void" Check** — VAMP deviation spike confirms price is moving into the vacuum (for spoof breach) or approaching the wall (for robust bounce).
- Gate C: **Volume/Depth Ratio** — low ratio (< 0.1) for spoof breach (liquidity evaporated), high ratio (> 0.5) for robust bounce (wall being consumed but holding).

**Confidence Model (6 components, sum to 1.0):**
1. Fragility magnitude (0.0–0.30) — how extreme the fragility is
2. Decay velocity (0.0–0.25) — how fast the wall is disappearing/holding
3. Wall significance (0.0–0.15) — wall size vs average
4. VAMP validation (0.0–0.15) — VAMP direction confirms signal
5. Volume confirmation (0.0–0.10) — volume/depth ratio matches signal type
6. Spread tightness (0.0–0.05) — spread < 2× average (scalp profitable)

**Parameters (from YAML config):**
```yaml
order_book_fragmentation:
  enabled: true
  tracker:
    max_hold_seconds: 300  # 5 min max for microstructure scalping
  params:
    frag_threshold: 0.5
    decay_threshold: -0.1
    wall_significance_mult: 3.0
    price_proximity_pct: 0.001  # 0.1% for robust bounce
    min_confidence: 0.45
    max_confidence: 0.90
    stop_pct: 0.003  # 0.3% tight stop for scalp trades
    target_risk_mult: 3.0
```

### Step 4: Register Strategy in `main.py`

**Import:** Add to layer2 imports
```python
from strategies.layer2.order_book_fragmentation import OrderBookFragmentation
```

**Register:** Add to `_create_strategy_engine()` dict
```python
"order_book_fragmentation": OrderBookFragmentation,
```

### Step 5: Add to Heatmap Config

**`config/heatmap.yaml`:** Add to Row 6, Col 1 (new row):
```yaml
order_book_fragmentation:
  row: 6
  col: 1
  span_cols: 1
  span_rows: 1
```

**`templates/heatmap.html`:** Add to STRATEGIES array (after `exchange_flow_asymmetry`):
```javascript
{ id: "order_book_fragmentation", name: "OB Fragmentation", layer: "L2", group: "Structural Integrity" },
```

### Step 6: Add to `config/strategies.yaml`

Add under `layer2:` section with the parameters from Step 3.

---

## File Change Summary

| File | Change |
|------|--------|
| `strategies/rolling_keys.py` | Add 6 new key constants, update ALL_KEYS |
| `main.py` | Enrich data extraction with fragility + decay + wall size, enrich depth_snapshot |
| `strategies/layer2/order_book_fragmentation.py` | **NEW** — strategy class (~300 lines) |
| `strategies/layer2/__init__.py` | Add import for new strategy |
| `config/strategies.yaml` | Add strategy config block |
| `config/heatmap.yaml` | Add Row 6, Col 1 placement |
| `templates/heatmap.html` | Add to STRATEGIES array |

## Total: 7 files changed, ~400 lines added

## Key Design Decisions

1. **Fragility vs Robustness are two sides of the same coin:** A fragile ask wall evaporating = bullish (fake resistance gone). A robust bid wall holding = bullish (real support holding). Both can produce LONG signals but through different mechanisms.

2. **Decay velocity is the trigger:** A fragile wall sitting there doing nothing is not a signal. The signal fires when the fragile wall *evaporates* — that's the spoof breach. Conversely, a robust wall *holding* during price pressure is the robust bounce.

3. **Wall significance gate prevents noise:** We only care about walls that are 3× larger than the average level. A small wall that evaporates is just normal market noise.

4. **Volume/depth ratio distinguishes evaporated vs consumed:** If a wall disappears with little volume, it evaporated (spoof). If volume is high but the wall still holds, it was consumed (real demand/supply).

5. **Tight stop (0.3%) for scalp trades:** This is a high-frequency strategy. We enter quickly and exit quickly. 0.3% stop, 3.0× risk:reward target.

6. **5-minute max hold:** Unlike venue-driven strategies (15–60 min), this is microstructure — the signal decays fast.

7. **Data already available:** `num_participants` and `bid_exchanges`/`ask_exchanges` per level are already parsed in `depth_quotes_parsed`. We extend existing computations rather than duplicating.
