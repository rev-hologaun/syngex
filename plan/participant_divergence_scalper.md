# Plan: Participant Divergence Scalper

## Synapse's Design Summary

**Core Insight:** Spoof walls have massive size but few participants (often 1 player). Robust walls have massive size AND many participants across multiple exchanges. We trade both: the collapse of fake walls and the bounce off real ones.

**Two Wall Types:**
- **Fragile Wall (Spoof):** Large size, low `num_participants` (1), single exchange → will collapse
- **Robust Wall (Anchor):** Large size, high `num_participants`, multi-exchange → will hold

**Key Metrics:**
- **Fragility Index:** `1 / (num_participants × exchange_count)` → 1.0 = max fragile, ~0.0 = max robust
- **Decay Velocity:** `ROC(level_size, 1s)` → detects when a spoof is being pulled in real-time

**Signal Types:**
- **Spoof Breach (SHORT):** Fragile Ask Wall evaporates → scalp the vacuum through to next bid wall
- **Spoof Breach (LONG):** Fragile Bid Wall evaporates → scalp the vacuum through to next ask wall
- **Robust Bounce (LONG):** Robust Bid Wall holds → scalp the bounce back up
- **Robust Bounce (SHORT):** Robust Ask Wall holds → scalp the bounce back down

**Target Hold Time:** 10 seconds – 3 minutes (pure microstructure scalping)

**Heatmap Visual:** "Divergence Pulse" cell — Electric Yellow for fragile walls (spoof warning), Bright White for robust walls (high conviction anchor). Displays Fragility Score (0.0–1.0).

---

## Implementation Plan

### Step 1: Add Rolling Keys (`strategies/rolling_keys.py`)

Add 6 new key constants:

```python
# --- Participant Divergence Scalper ---
KEY_FRAGILITY_BID_5M = "fragility_bid_5m"
KEY_FRAGILITY_ASK_5M = "fragility_ask_5m"
KEY_DECAY_VELOCITY_BID_5M = "decay_velocity_bid_5m"
KEY_DECAY_VELOCITY_ASK_5M = "decay_velocity_ask_5m"
KEY_TOP_WALL_BID_SIZE_5M = "top_wall_bid_size_5m"
KEY_TOP_WALL_ASK_SIZE_5M = "top_wall_ask_size_5m"
```

Add to `ALL_KEYS` tuple and `__all__` list.

### Step 2: Enrich Data Extraction in `main.py`

**Location:** Inside the `if msg_type == "market_depth_quotes":` block, after the existing Participant Diversity Conviction parsing (~line 1290), before the spread calculation.

**Compute per-level fragility for top 5 levels on each side:**
```python
def _compute_fragility(levels, side_key):
    """Fragility = 1 / (num_participants × exchange_count), averaged over top N."""
    if not levels:
        return 0.0
    fragilities = []
    for lvl in levels[:5]:
        n_part = max(1, int(lvl.get("num_participants", 0)))
        exchanges = lvl.get(side_key, {})
        n_exch = max(1, len(exchanges)) if exchanges else 1
        fragilities.append(1.0 / (n_part * n_exch))
    return sum(fragilities) / len(fragilities)

frag_bid = _compute_fragility(bids, "bid_exchanges")
frag_ask = _compute_fragility(asks, "ask_exchanges")
```

**Track strongest wall per side (level with max size):**
```python
# Strongest wall = level with max size on each side
top_bid_level = max(bids, key=lambda b: int(b.get("Size", 0)), default=None)
top_ask_level = max(asks, key=lambda a: int(a.get("Size", 0)), default=None)
top_bid_wall_size = int(top_bid_level.get("Size", 0)) if top_bid_level else 0
top_ask_wall_size = int(top_ask_level.get("Size", 0)) if top_ask_level else 0

# Decay velocity = rate of change of strongest wall size over lookback
bid_decay = 0.0
ask_decay = 0.0
bid_wall_rw = rolling_data.get(KEY_TOP_WALL_BID_SIZE_5M)
ask_wall_rw = rolling_data.get(KEY_TOP_WALL_ASK_SIZE_5M)

if bid_wall_rw and bid_wall_rw.count >= 5 and top_bid_wall_size > 0:
    past = bid_wall_rw.values[-5] if bid_wall_rw.values[-5] > 0 else 1
    bid_decay = (top_bid_wall_size - past) / past

if ask_wall_rw and ask_wall_rw.count >= 5 and top_ask_wall_size > 0:
    past = ask_wall_rw.values[-5] if ask_wall_rw.values[-5] > 0 else 1
    ask_decay = (top_ask_wall_size - past) / past
```

**Push to rolling windows:**
```python
if KEY_FRAGILITY_BID_5M in rolling_data:
    rolling_data[KEY_FRAGILITY_BID_5M].push(frag_bid, ts)
if KEY_FRAGILITY_ASK_5M in rolling_data:
    rolling_data[KEY_FRAGILITY_ASK_5M].push(frag_ask, ts)
if KEY_DECAY_VELOCITY_BID_5M in rolling_data:
    rolling_data[KEY_DECAY_VELOCITY_BID_5M].push(bid_decay, ts)
if KEY_DECAY_VELOCITY_ASK_5M in rolling_data:
    rolling_data[KEY_DECAY_VELOCITY_ASK_5M].push(ask_decay, ts)
if KEY_TOP_WALL_BID_SIZE_5M in rolling_data:
    rolling_data[KEY_TOP_WALL_BID_SIZE_5M].push(top_bid_wall_size, ts)
if KEY_TOP_WALL_ASK_SIZE_5M in rolling_data:
    rolling_data[KEY_TOP_WALL_ASK_SIZE_5M].push(top_ask_wall_size, ts)
```

**Enrich `depth_snapshot`** in `_build_depth_snapshot()` with fragility and decay keys.

### Step 3: Create Strategy File

**Path:** `strategies/layer2/participant_divergence_scalper.py`

**Class:** `ParticipantDivergenceScalper(BaseStrategy)`
- `strategy_id = "participant_divergence_scalper"`
- `layer = "layer2"`

**Signal Logic:**

```
SPOOF BREACH (SHORT): frag_ask > fragility_threshold (0.5)
                      AND decay_velocity_ask > decay_threshold (0.0)
                      AND vol_ratio < 0.1 (no real trades eating the wall)
                      AND spread < 2× avg spread (tight enough for scalp)

SPOOF BREACH (LONG):  frag_bid > fragility_threshold
                      AND decay_velocity_bid > decay_threshold
                      AND vol_ratio < 0.1
                      AND spread < 2× avg spread

ROBUST BOUNCE (LONG): frag_bid < robust_threshold (0.3)
                      AND decay_velocity_bid <= 0 (wall not evaporating)
                      AND vol_ratio > 0.5 (some activity, wall absorbing)
                      AND spread < 2× avg spread

ROBUST BOUNCE (SHORT): frag_ask < robust_threshold (0.3)
                       AND decay_velocity_ask <= 0
                       AND vol_ratio > 0.5
                       AND spread < 2× avg spread
```

**Hard Gates (all must pass):**
- Gate A: Wall size >= 5× average level size (significant wall, not noise)
- Gate B: `vol_ratio` matches signal type (< 0.1 for spoof, > 0.5 for robust)
- Gate C: Spread < 2× average spread (scalp must be profitable)

**Confidence Model (7 components, sum to 1.0):**
1. Fragility strength (0.0–0.30) — how extreme the fragility is
2. Decay velocity (0.0–0.20) — how fast wall is evaporating/holding
3. Wall size significance (0.0–0.15) — wall vs average ratio
4. Volume confirmation (0.0–0.10) — vol ratio confirms signal type
5. Spread tightness (0.0–0.10) — tight spread = profitable scalp
6. VAMP validation (0.0–0.10) — VAMP direction aligns
7. GEX regime alignment (0.0–0.10) — matches GEX bias

**Parameters (from YAML config):**
```yaml
participant_divergence_scalper:
  enabled: true
  tracker:
    max_hold_seconds: 180  # 3 min max for scalping
  params:
    fragility_threshold: 0.5
    robust_threshold: 0.3
    decay_velocity_threshold: 0.0
    wall_size_mult: 5.0
    vol_ratio_spoof: 0.1
    vol_ratio_robust: 0.5
    max_spread_mult: 2.0
    stop_pct: 0.003  # Tighter stop for scalping (0.3%)
    target_risk_mult: 1.5
    min_confidence: 0.45
    max_confidence: 0.95
```

### Step 4: Register Strategy in `main.py`

**Import:** Add to layer2 imports (~line 157)
```python
from strategies.layer2.participant_divergence_scalper import ParticipantDivergenceScalper
```

**Register:** Add to `_create_strategy_engine()` dict (~line 636)
```python
"participant_divergence_scalper": ParticipantDivergenceScalper,
```

### Step 5: Add to Heatmap Config

**`config/heatmap.yaml`:** Add to Row 5, Col 3 (free slot):
```yaml
participant_divergence_scalper:
  row: 5
  col: 3
  span_cols: 1
  span_rows: 1
```

**`templates/heatmap.html`:** Add to `STRATEGIES` array (after `participant_diversity_conviction`):
```javascript
{ id: "participant_divergence_scalper", name: "Divergence Scalper", layer: "L2", group: "Micro-Scalp" },
```

### Step 6: Add to `config/strategies.yaml`

Add the strategy config block under `layer2:` section with the parameters from Step 3.

---

## File Change Summary

| File | Change |
|------|--------|
| `strategies/rolling_keys.py` | Add 6 new key constants, update ALL_KEYS |
| `main.py` | Enrich depth_quotes parsing with fragility + decay velocity, enrich depth_snapshot |
| `strategies/layer2/participant_divergence_scalper.py` | **NEW** — strategy class (~350 lines) |
| `strategies/layer2/__init__.py` | Add import for new strategy |
| `config/strategies.yaml` | Add strategy config block |
| `config/heatmap.yaml` | Add Row 5, Col 3 placement |
| `templates/heatmap.html` | Add to STRATEGIES array |

## Total: 7 files changed, ~550 lines added

## Key Design Decisions

1. **Fragility is per-level, averaged over top 5:** Smooths noise while preserving signal. A single spoofed level won't spike the metric.

2. **Decay velocity tracks strongest wall:** The most important wall is the one with max size. Its rate of change gives the clearest signal of wall evaporation or holding.

3. **Hysteresis band (0.3–0.5):** Separate thresholds for spoof (fragile > 0.5) vs robust (fragile < 0.3). In between, neither signal fires — prevents whipsaw.

4. **Tighter stops for scalping:** 0.3% stop loss (vs 0.5–0.8% for other strategies) because target hold times are seconds to minutes, not hours.

5. **Shares data with Participant Diversity Conviction:** Both strategies use `num_participants` and `bid_exchanges`/`ask_exchanges`. The divergence scalper adds fragility and decay velocity on top of the same data pipeline.
