# Order Book Stacking — Implementation Plan

**Strategy:** Order Book Stacking (v1.0)  
**Author:** Synapse (design) → Archon (plan) → Forge (implementation)  
**Layer:** Layer 2 (Structural Concentration)  
**Target Hold Time:** 1–10 minutes

---

## Core Concept

Detects large order concentrations ("stacks") at specific price levels that act as hidden support/resistance. A stack is anomalous when its size significantly exceeds the recent average level size.

## Mathematical Engine

**Stack Intensity Score (SIS):**
```
SIS_bid = max(bid_level_size / rolling_avg(bid_level_size, 60s)) over top N levels
SIS_ask = max(ask_level_size / rolling_avg(ask_level_size, 60s)) over top N levels
```

A level with SIS > 4.0 is a massive outlier compared to the recent "normal" book depth.

## Signal Types

1. **STACK_BOUNCE_LONG** — Mean Reversion / Bounce
   - Setup: SIS_bid > 4.0 (massive bid stack)
   - Trigger: Price approaches within 0.1% of stack AND VAMP not accelerating through
   - Action: Scalp the bounce off the wall

2. **STACK_BREACH_SHORT** — Momentum / Breakout
   - Setup: SIS_ask > 4.0 (massive ask stack)
   - Trigger: ROC(ask_size, 5 ticks) < -0.5 (stack being eaten rapidly)
   - Action: Scalp the breakout as wall collapses

3. **STACK_BOUNCE_SHORT** — Mean Reversion / Rejection
   - Setup: SIS_ask > 4.0 (massive ask stack)
   - Trigger: Price approaches within 0.1% AND not breaking through
   - Action: Scalp the rejection

4. **STACK_BREACH_LONG** — Momentum / Breakout
   - Setup: SIS_bid > 4.0 (massive bid stack)
   - Trigger: ROC(bid_size, 5 ticks) < -0.5 (bid stack evaporating)
   - Action: Scalp the breakdown

## Hard Gates

- **Gate A (Magnitude):** Stack must be ≥ 3× average level size
- **Gate B (Participant):** ≥ 2 unique participants (avoid single-player spoofing)
- **Gate C (Volume/Depth):** For breach signals, confirm volume/depth ratio indicates real consumption, not just evaporation

## Rolling Keys (add to `strategies/rolling_keys.py`)

```python
KEY_DEPTH_BID_LEVEL_AVG_5M = "depth_bid_level_avg_5m"
KEY_DEPTH_ASK_LEVEL_AVG_5M = "depth_ask_level_avg_5m"
KEY_SIS_BID_5M = "sis_bid_5m"
KEY_SIS_ASK_5M = "sis_ask_5m"
KEY_SIS_BID_ROC_5M = "sis_bid_roc_5m"
KEY_SIS_ASK_ROC_5M = "sis_ask_roc_5m"
```

## Implementation Files

### 1. `strategies/rolling_keys.py` — Add new keys
Add the 6 new rolling keys above to the file.

### 2. `strategies/layer2/order_book_stacking.py` — New strategy (~280 lines)
Following the established pattern from `order_book_fragmentation.py`:

```python
class OrderBookStacking(BaseStrategy):
    NAME = "order_book_stacking"
    LAYER = "L2"
    HOLD_TIME = 300  # 5 minutes
    STOP_PCT = "0.3"
    RISK_REWARD = 3.0
    
    SIGNAL_TYPES = {
        "STACK_BOUNCE_LONG": "Mean reversion bounce off bid stack",
        "STACK_BREACH_SHORT": "Momentum breakout as ask stack eaten",
        "STACK_BOUNCE_SHORT": "Mean reversion rejection off ask stack",
        "STACK_BREACH_LONG": "Momentum breakdown as bid stack evaporates",
    }
    
    # Required rolling keys
    ROLLING_KEYS = [
        KEY_DEPTH_BID_LEVEL_AVG_5M,
        KEY_DEPTH_ASK_LEVEL_AVG_5M,
        KEY_SIS_BID_5M,
        KEY_SIS_ASK_5M,
        KEY_SIS_BID_ROC_5M,
        KEY_SIS_ASK_ROC_5M,
    ]
    
    # Signal thresholds
    SIS_THRESHOLD = 4.0        # Stack intensity threshold
    MAGNITUDE_FACTOR = 3.0     # Must be 3x average
    MIN_PARTICIPANTS = 2       # Anti-spoof gate
    PRICE_TOLERANCE = 0.001    # 0.1% for bounce triggers
    ROC_THRESHOLD = -0.5       # Stack decay threshold
```

Key methods:
- `compute_sis(bid_levels, ask_levels)` — Calculate SIS for both sides
- `compute_stack_decay(levels)` — ROC of top level size over 5 ticks
- `check_participant_gate(levels)` — Count unique participants
- `generate_signal(bid_data, ask_data, price_data)` — Main signal logic

### 3. `main.py` — Register strategy
- Import: `from strategies.layer2.order_book_stacking import OrderBookStacking`
- Register in `_get_strategy_class` map: `"order_book_stacking": OrderBookStacking`
- Compute rolling keys in telemetry handler (compute bid/ask level averages and SIS)

### 4. `strategies/layer2/__init__.py` — Import + export
```python
from .order_book_stacking import OrderBookStacking
__all__ = [..., "OrderBookStacking"]
```

### 5. `config/strategies.yaml` — Strategy config
```yaml
order_book_stacking:
  enabled: true
  layer: L2
  hold_time: 300
  stop_pct: 0.3
  risk_reward: 3.0
  min_confidence: 0.55
```

### 6. `config/heatmap.yaml` — Heatmap config
```yaml
order_book_stacking:
  label: STACKING
  layer: L2
  row: 6
  col: 2
  color_bid: "#f97316"    # Bright Orange (bid stack = support)
  color_ask: "#a855f7"    # Electric Purple (ask stack = resistance)
```

### 7. `templates/heatmap.html` — Add to STRATEGIES array
Add after `order_book_fragmentation`:
```javascript
{ id: 'order_book_stacking', label: 'STACKING',    layer: 'L2', row: 6, col: 2 },
```

## Data Source

- `depth_quotes_parsed` telemetry with per-level `bid_exchanges`/`ask_exchanges` dicts
- Per-level size data to compute level-by-level averages
- Participant counts from `num_participants` field

## Telemetry Computation (in main.py)

In the depth_quotes_parsed handler, after computing level data:

```python
# Compute rolling avg of top N bid/ask level sizes
bid_sizes = [int(b.get("size", 0)) for b in bids[:top_n]]
ask_sizes = [int(a.get("size", 0)) for a in asks[:top_n]]

bid_avg = sum(bid_sizes) / len(bid_sizes) if bid_sizes else 0
ask_avg = sum(ask_sizes) / len(ask_sizes) if ask_sizes else 0

# Push to rolling windows
self._rolling_data[KEY_DEPTH_BID_LEVEL_AVG_5M].push(bid_avg, ts)
self._rolling_data[KEY_DEPTH_ASK_LEVEL_AVG_5M].push(ask_avg, ts)

# Compute SIS
if bid_avg > 0:
    max_bid_size = max(bid_sizes) if bid_sizes else 0
    sis_bid = max_bid_size / bid_avg
else:
    sis_bid = 0.0

if ask_avg > 0:
    max_ask_size = max(ask_sizes) if ask_sizes else 0
    sis_ask = max_ask_size / ask_avg
else:
    sis_ask = 0.0

self._rolling_data[KEY_SIS_BID_5M].push(sis_bid, ts)
self._rolling_data[KEY_SIS_ASK_5M].push(sis_ask, ts)

# Compute ROC of max sizes for decay detection
# Need to track max sizes separately for ROC
```

## Heatmap Visual

- **Bid Stack:** Bright Orange (#f97316) — "Structural Support Spike"
- **Ask Stack:** Electric Purple (#a855f7) — "Structural Resistance Spike"
- **Display:** Shows the SIS value (e.g., "SIS: 5.2")

## Rollout Order

1. Add rolling keys to `rolling_keys.py`
2. Create `order_book_stacking.py`
3. Register in `__init__.py`
4. Import + register in `main.py` + add telemetry computation
5. Update `config/strategies.yaml`
6. Update `config/heatmap.yaml`
7. Update `templates/heatmap.html`
8. Tag `v1.98` and push
