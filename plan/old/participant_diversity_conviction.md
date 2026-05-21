# Plan: Participant Diversity Conviction Strategy

## Synapse's Design Summary

**Core Insight:** A wall with 4 participants is structurally stronger than one with 1. Multi-participant + multi-exchange walls = institutional conviction. Single-player walls = likely spoofed.

**Two Dimensions:**
1. **Intra-Level Diversity** — `num_participants` per price level (from depth_quotes)
2. **Inter-Exchange Diversity** — unique exchanges contributing to a price level

**Conviction Score:** `Participant_Score × Exchange_Score` → normalized 0.0–1.0

**Hard Gates:**
- Gate A: ≥3 unique participants at the wall
- Gate B: ≥2 exchanges represented
- Gate C: Size consistent with recent history (not flash walls)

**Signal Logic:**
- CONVICTION BUY: Score > 0.8 AND price breakout
- CONVICTION SELL: Score > 0.8 AND price breakdown
- Exit: Score drops < 0.4 OR stop-loss hit

---

## Implementation Plan

### Step 1: Add Rolling Keys (`strategies/rolling_keys.py`)

Add 5 new key constants:

```python
# --- Participant Diversity Conviction ---
KEY_BID_PARTICIPANTS_5M = "bid_participants_5m"
KEY_ASK_PARTICIPANTS_5M = "ask_participants_5m"
KEY_BID_EXCHANGES_5M = "bid_exchanges_5m"
KEY_ASK_EXCHANGES_5M = "ask_exchanges_5m"
KEY_CONVICT_SCORE_5M = "conviction_score_5m"
```

Add to `ALL_KEYS` tuple and `__all__` list.

### Step 2: Extract Participant/Exchange Data in `main.py`

**Location:** Inside the `if msg_type == "market_depth_quotes":` block (~line 1230), after the existing Exchange Flow Concentration parsing.

**Extract per-level data from each bid/ask level:**
- `num_participants` field → count of participants at that level
- `bid_exchanges`/`ask_exchanges` → dict of venue→size, extract unique venue count

**Aggregate into rolling windows:**
```python
# Per-level: max participants and max exchanges at any single level
top_bid_participants = max(int(b.get("num_participants", 0)) for b in bids) if bids else 0
top_ask_participants = max(int(a.get("num_participants", 0)) for a in asks) if asks else 0

# Unique exchanges across all levels
top_bid_exchanges = len(set(b.get("bid_exchanges", {}).keys()) for b in bids if b.get("bid_exchanges")) if bids else 0
top_ask_exchanges = len(set(a.get("ask_exchanges", {}).keys()) for a in asks if a.get("ask_exchanges")) if asks else 0

# Also compute: avg participants per level (across top N levels)
top_n = min(5, len(bids)) if bids else 0
avg_bid_participants = sum(int(b.get("num_participants", 0)) for b in bids[:top_n]) / top_n if top_n > 0 else 0
avg_ask_participants = sum(int(a.get("num_participants", 0)) for a in asks[:top_n]) / top_n if top_n > 0 else 0

# Push to rolling windows
self._rolling_data[KEY_BID_PARTICIPANTS_5M].push(avg_bid_participants, ts)
self._rolling_data[KEY_ASK_PARTICIPANTS_5M].push(avg_ask_participants, ts)
self._rolling_data[KEY_BID_EXCHANGES_5M].push(top_bid_exchanges, ts)
self._rolling_data[KEY_ASK_EXCHANGES_5M].push(top_ask_exchanges, ts)
```

**Also enrich `depth_snapshot` with participant/exchange data:**
```python
# In _build_depth_snapshot(), add:
for rw_key, short_key in [
    (KEY_BID_PARTICIPANTS_5M, "bid_participants"),
    (KEY_ASK_PARTICIPANTS_5M, "ask_participants"),
    (KEY_BID_EXCHANGES_5M, "bid_exchanges"),
    (KEY_ASK_EXCHANGES_5M, "ask_exchanges"),
]:
    ...
```

### Step 3: Create Strategy File

**Path:** `strategies/layer2/participant_diversity_conviction.py`

**Class:** `ParticipantDiversityConviction(BaseStrategy)`
- `strategy_id = "participant_diversity_conviction"`
- `layer = "layer2"`

**Signal Logic:**
```
LONG:  avg_bid_participants >= 3.0 AND bid_exchanges >= 2 AND conviction_score > 0.7
      AND price action = breakout above recent high

SHORT: avg_ask_participants >= 3.0 AND ask_exchanges >= 2 AND conviction_score > 0.7
       AND price action = breakdown below recent low

Exit: conviction_score drops < 0.4 OR stop-loss hit
```

**Conviction Score Calculation:**
```
participant_score = min(1.0, avg_participants / max_participants)  # max_participants configurable, default 5
exchange_score = min(1.0, num_exchanges / max_exchanges)          # max_exchanges configurable, default 4
conviction_score = participant_score * exchange_score
```

**Hard Gates (all must pass):**
- Gate A: `avg_participants >= 3.0` (minimum participant threshold)
- Gate B: `num_exchanges >= 2` (multi-exchange requirement)
- Gate C: `current_size >= 0.5 × MA(size)` (not a flash wall)

**Confidence Model (7 components):**
1. Participant score (0.0–0.25) — how diverse the participants are
2. Exchange score (0.0–0.20) — how many exchanges contribute
3. Score magnitude (0.0–0.15) — conviction_score vs threshold
4. Score ROC (0.0–0.10) — conviction rising or falling
5. Size correlation (0.0–0.10) — size consistent with history
6. VAMP validation (0.0–0.10) — VAMP direction aligns
7. GEX regime alignment (0.0–0.10) — matches GEX bias

**Parameters (from YAML config):**
```yaml
participant_diversity_conviction:
  enabled: true
  tracker:
    max_hold_seconds: 3600  # 15-60 min → use 1h default
  params:
    min_participants: 3.0
    min_exchanges: 2
    conviction_threshold: 0.7
    conviction_exit: 0.4
    max_participants_norm: 5.0
    max_exchanges_norm: 4.0
    min_size_ratio: 0.5
    stop_pct: 0.008
    target_risk_mult: 2.0
    min_confidence: 0.40
    max_confidence: 0.90
```

### Step 4: Register Strategy in `main.py`

**Import:** Add to layer2 imports (~line 157)
```python
from strategies.layer2.participant_diversity_conviction import ParticipantDiversityConviction
```

**Register:** Add to `_create_strategy_engine()` dict (~line 636)
```python
"participant_diversity_conviction": ParticipantDiversityConviction,
```

### Step 5: Add to Heatmap Config

**`config/heatmap.yaml`:** Add to Row 5 (free slot):
```yaml
participant_diversity_conviction:
  row: 5
  col: 2
  span_cols: 1
  span_rows: 1
```

**`templates/heatmap.html`:** Add to `STRATEGIES` array (after `theta_burn`):
```javascript
{ id: "participant_diversity_conviction", name: "Participant Conviction", layer: "L2", group: "Meta-Filter" },
```

### Step 6: Add to `config/strategies.yaml`

Add the strategy config block under `layer2:` section with the parameters from Step 3.

---

## File Change Summary

| File | Change |
|------|--------|
| `strategies/rolling_keys.py` | Add 5 new key constants, update ALL_KEYS |
| `main.py` | Extract participant/exchange data from depth quotes, enrich depth_snapshot |
| `strategies/layer2/participant_diversity_conviction.py` | **NEW** — strategy class (~350 lines) |
| `strategies/layer2/__init__.py` | Add import for new strategy |
| `config/strategies.yaml` | Add strategy config block |
| `config/heatmap.yaml` | Add Row 5, Col 2 placement |
| `templates/heatmap.html` | Add to STRATEGIES array |

## Total: 7 files changed, ~500 lines added
