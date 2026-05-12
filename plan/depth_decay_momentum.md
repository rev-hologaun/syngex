# Depth Decay Momentum — Implementation Plan

**Strategy:** Depth Decay Momentum (Liquidity Evaporation Detection)
**Author:** Synapse (design) → Archon (plan)
**Layer:** Layer 2 — Liquidity Dynamics
**Data Sources:** `depthagg_parsed` (depth size tracking, top levels)
**Date:** 2026-05-12

---

## 1. Overview

Detects when liquidity is *pulled* (not consumed by trades) from one side of the book. When ask-side depth drops 15%+ in 30s without corresponding trade volume, sellers are exiting → bullish. When bid-side depth drops similarly → bearish.

**Core formulas:**
```
Depth_ROC = (Current_Depth - Depth_Lookback) / Depth_Lookback
  Where lookback = 30 seconds

Volume_Ratio = Volume_30s / |Depth_Change_30s|
  Low ratio (< 0.2) = liquidity evaporated (not consumed)
  High ratio = liquidity was consumed by trades (normal)

Signal = Depth_ROC side + Volume_Ratio filter + VAMP directional bias
```

---

## 2. Files to Create/Modify

### 2.1 New file: `strategies/layer2/depth_decay_momentum.py`

Full strategy implementation following the Layer 2 pattern.

### 2.2 Modify: `strategies/rolling_keys.py`

Add these new rolling window keys:

```python
# Depth Decay Momentum
KEY_DEPTH_DECAY_BID_5M = "depth_decay_bid_5m"      # ROC of bid depth
KEY_DEPTH_DECAY_ASK_5M = "depth_decay_ask_5m"       # ROC of ask depth
KEY_DEPTH_TOP5_BID_5M = "depth_top5_bid_5m"         # Top 5 bid level depth
KEY_DEPTH_TOP5_ASK_5M = "depth_top5_ask_5m"         # Top 5 ask level depth
KEY_DEPTH_VOL_RATIO_5M = "depth_vol_ratio_5m"       # Volume / Depth change ratio
```

Add to `ALL_KEYS` tuple and `__all__` list. Add a new `DEPTH_DECAY_KEYS` tuple.

### 2.3 Modify: `main.py`

**A. Rolling window initializations** (in `__init__`, alongside other RollingWindow defs):

```python
KEY_DEPTH_DECAY_BID_5M: RollingWindow(window_type="time", window_size=300),
KEY_DEPTH_DECAY_ASK_5M: RollingWindow(window_type="time", window_size=300),
KEY_DEPTH_TOP5_BID_5M: RollingWindow(window_type="time", window_size=300),
KEY_DEPTH_TOP5_ASK_5M: RollingWindow(window_type="time", window_size=300),
KEY_DEPTH_VOL_RATIO_5M: RollingWindow(window_type="time", window_size=300),
```

**B. Depth decay computation** (in `_on_message`, inside the `market_depth_agg` block, after the VAMP block):

The depth agg data already provides `total_bid_size`, `total_ask_size`, `bid_levels`, `ask_levels`. We compute:
- Overall depth ROC (30s lookback) using existing `KEY_DEPTH_BID_SIZE_5M`/`KEY_DEPTH_ASK_SIZE_5M`
- Top-5 level depth for the magnitude gate
- Volume/depth ratio for the volume filter

```python
# ── Depth Decay Momentum: compute depth ROC and top-level decay ──
# Use existing rolling windows for overall depth ROC
ts = time.time()

# Overall depth ROC (30s lookback)
bid_size_window = self._rolling_data.get(KEY_DEPTH_BID_SIZE_5M)
ask_size_window = self._rolling_data.get(KEY_DEPTH_ASK_SIZE_5M)

bid_depth_roc = 0.0
ask_depth_roc = 0.0

if bid_size_window and bid_size_window.count >= 5:
    old_bid = bid_size_window.values[-5] if bid_size_window.count >= 5 else 0
    current_bid = bid_size_window.values[-1]
    if old_bid > 0:
        bid_depth_roc = (current_bid - old_bid) / old_bid

if ask_size_window and ask_size_window.count >= 5:
    old_ask = ask_size_window.values[-5] if ask_size_window.count >= 5 else 0
    current_ask = ask_size_window.values[-1]
    if old_ask > 0:
        ask_depth_roc = (current_ask - old_ask) / old_ask

if KEY_DEPTH_DECAY_BID_5M in self._rolling_data:
    self._rolling_data[KEY_DEPTH_DECAY_BID_5M].push(bid_depth_roc, ts)
if KEY_DEPTH_DECAY_ASK_5M in self._rolling_data:
    self._rolling_data[KEY_DEPTH_DECAY_ASK_5M].push(ask_depth_roc, ts)

# Top-5 level depth (for magnitude gate)
market_depth = self._rolling_data.get("market_depth_agg", {})
bid_levels = market_depth.get("bid_levels", [])
ask_levels = market_depth.get("ask_levels", [])

top5_bid_depth = sum(l["size"] for l in bid_levels[:5])
top5_ask_depth = sum(l["size"] for l in ask_levels[:5])

if KEY_DEPTH_TOP5_BID_5M in self._rolling_data:
    self._rolling_data[KEY_DEPTH_TOP5_BID_5M].push(top5_bid_depth, ts)
if KEY_DEPTH_TOP5_ASK_5M in self._rolling_data:
    self._rolling_data[KEY_DEPTH_TOP5_ASK_5M].push(top5_ask_depth, ts)

# Volume/depth ratio: track volume changes alongside depth changes
volume_window = self._rolling_data.get(KEY_VOLUME_5M)
if volume_window and volume_window.count >= 5:
    old_vol = volume_window.values[-5]
    current_vol = volume_window.values[-1]
    vol_change = abs(current_vol - old_vol)
    depth_change = abs(current_bid + current_ask - old_bid - old_ask) if (old_bid and old_ask) else 0
    if depth_change > 0:
        vol_ratio = vol_change / depth_change
    else:
        vol_ratio = 0.0
    if KEY_DEPTH_VOL_RATIO_5M in self._rolling_data:
        self._rolling_data[KEY_DEPTH_VOL_RATIO_5M].push(vol_ratio, ts)
```

**C. Import the new keys** at top of main.py.

### 2.4 Modify: `strategies/layer2/__init__.py`

Add `DepthDecayMomentum` to imports and `__all__`.

### 2.5 Modify: `config/heatmap.yaml`

Grid is already 8×6. Place Depth Decay at row 3, col 5 (push VAMP to col 6):

```yaml
  depth_decay_momentum:
    row: 3
    col: 5
    span_cols: 1
    span_rows: 1
```

Move VAMP to col 6:
```yaml
  vamp_momentum:
    row: 3
    col: 6
    span_cols: 1
    span_rows: 1
```

### 2.6 Modify: `config/strategies.yaml`

Add under `layer2:` section:

```yaml
  depth_decay_momentum:
    enabled: true
    tracker:
      max_hold_seconds: 1800
    params:
      # === Core Depth Decay params ===
      depth_decay_threshold: 0.15           # |ROC| must exceed 15%
      depth_decay_lookback: 5               # 5 ticks ≈ 30s lookback
      min_depth_decay_data_points: 10       # Min data points for ROC stability
      max_vol_ratio: 0.2                    # Volume/Depth ratio threshold

      # === Gate A: Magnitude Gate ===
      min_top5_depth: 100                   # Top 5 levels must have meaningful depth

      # === Gate B: Participant Consistency ===
      max_evap_participants: 2              # Evaporating levels should have few participants

      # === Gate C: Volume/Depth Ratio ===
      # (already covered by max_vol_ratio)

      # === VAMP Directional Bias ===
      use_vamp_bias: true                   # Require VAMP to align with decay direction

      # === Execution ===
      stop_pct: 0.005                       # 0.5% stop loss
      target_risk_mult: 1.5                 # 1.5× risk for target
      min_confidence: 0.40
      max_confidence: 0.90

      # === Confidence factors ===
      # 1. Depth decay magnitude            (0.0–0.25) — soft
      # 2. Volume/depth ratio strength       (0.0–0.20) — soft
      # 3. Top-level concentration           (0.0–0.15) — soft
      # 4. Participant consistency           (0.0–0.10) — soft
      # 5. VAMP directional alignment        (0.0–0.10) — soft
      # 6. Overall depth magnitude           (0.0–0.10) — soft
      # 7. GEX regime alignment              (0.0–0.10) — soft
```

---

## 3. Depth Decay Momentum Strategy Implementation Details

### 3.1 Class structure

```python
class DepthDecayMomentum(BaseStrategy):
    strategy_id = "depth_decay_momentum"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        # 1. Get depth ROC from rolling_data
        # 2. Get volume/depth ratio from rolling_data
        # 3. Get top-5 depth from rolling_data
        # 4. Apply 3 hard gates
        # 5. Check VAMP directional bias (if enabled)
        # 6. If all pass → compute confidence and emit signal
```

### 3.2 Depth ROC computation

Already computed in main.py and stored in `rolling_data[KEY_DEPTH_DECAY_BID_5M]` and `rolling_data[KEY_DEPTH_DECAY_ASK_5M]`.

```python
bid_decay = rolling_data.get(KEY_DEPTH_DECAY_BID_5M)
ask_decay = rolling_data.get(KEY_DEPTH_DECAY_ASK_5M)

if bid_decay and bid_decay.count >= min_data_points:
    current_bid_roc = bid_decay.values[-1]
else:
    return []

if ask_decay and ask_decay.count >= min_data_points:
    current_ask_roc = ask_decay.values[-1]
else:
    return []
```

### 3.3 Signal logic

```python
# Ask-side evaporation → bullish (sellers pulling → price can rise)
# Bid-side evaporation → bearish (buyers pulling → price can fall)

ask_evaporating = current_ask_roc < -depth_decay_threshold   # Ask depth dropping
bid_evaporating = current_bid_roc < -depth_decay_threshold   # Bid depth dropping
```

### 3.4 Hard gates

```python
# Gate A: Magnitude — top 5 levels must have meaningful depth
top5_ask = rolling_data.get(KEY_DEPTH_TOP5_ASK_5M)
top5_bid = rolling_data.get(KEY_DEPTH_TOP5_BID_5M)
if top5_ask and top5_ask.count > 0:
    gate_a_ask = top5_ask.values[-1] >= min_top5_depth
if top5_bid and top5_bid.count > 0:
    gate_a_bid = top5_bid.values[-1] >= min_top5_depth

# Gate B: Participant consistency — evaporating levels should have few participants
# Use the depth_snapshot participant data
gate_b = True  # Check depth_snapshot for participant counts at evaporating levels

# Gate C: Volume/depth ratio
vol_ratio_window = rolling_data.get(KEY_DEPTH_VOL_RATIO_5M)
if vol_ratio_window and vol_ratio_window.count > 0:
    current_vol_ratio = vol_ratio_window.values[-1]
    gate_c = current_vol_ratio < max_vol_ratio
else:
    gate_c = True  # No history yet
```

### 3.5 VAMP directional bias

```python
# If VAMP is available, require alignment with decay direction
vamp_bias_aligned = True
if use_vamp_bias:
    vamp_levels = rolling_data.get("vamp_levels", {})
    vamp_mid_dev = vamp_levels.get("mid_price", 0)
    # VAMP > mid → book is bid-weighted → supports ask-side evaporation (bullish)
    # VAMP < mid → book is ask-weighted → supports bid-side evaporation (bearish)
    # (Detailed bias check in implementation)
```

### 3.6 Confidence model (7 components)

| # | Factor | Range | Type | Description |
|---|--------|-------|------|-------------|
| 1 | Depth decay magnitude | 0.0–0.25 | Soft | |ROC| scaled |
| 2 | Volume/depth ratio strength | 0.0–0.20 | Soft | Lower ratio = higher confidence |
| 3 | Top-level concentration | 0.0–0.15 | Soft | How much decay is in top 5 vs total |
| 4 | Participant consistency | 0.0–0.10 | Soft | Few participants = single-player pull = higher confidence |
| 5 | VAMP directional alignment | 0.0–0.10 | Soft | VAMP bias matches decay direction |
| 6 | Overall depth magnitude | 0.0–0.10 | Soft | Deeper book = more meaningful signal |
| 7 | GEX regime alignment | 0.0–0.10 | Soft | Decay direction matches GEX bias |

### 3.7 Entry/Stop/Target

```python
entry = underlying_price
stop_distance = entry * stop_pct  # 0.5%

if direction == "LONG":  # Ask-side evaporation → bullish
    stop = entry - stop_distance
    target = entry + (stop_distance * target_risk_mult)
else:  # Bid-side evaporation → bearish
    stop = entry + stop_distance
    target = entry - (stop_distance * target_risk_mult)
```

---

## 4. Dashboard Integration

### 4.1 Heatmap card

Placed at row 3, col 5. VAMP moves to row 3, col 6.

### 4.2 Card content

Depth Decay card displays:
- **Ask Decay ROC:** formatted as percentage (e.g., "-18%")
- **Bid Decay ROC:** formatted as percentage (e.g., "-5%")
- **Signal:** LONG/SHORT/NEUTRAL with color coding
  - Cyan: Ask-side evaporation (bullish)
  - Purple: Bid-side evaporation (bearish)
- **Evaporation Velocity:** % depth lost per second

---

## 5. Testing Checklist

- [ ] Depth ROC correctly computes (negative = depth dropping)
- [ ] Ask ROC < -0.15 triggers LONG candidate
- [ ] Bid ROC < -0.15 triggers SHORT candidate
- [ ] Gate A rejects when top 5 depth is too thin
- [ ] Gate C rejects when volume/depth ratio is high (liquidity consumed, not evaporated)
- [ ] VAMP bias filter works when enabled
- [ ] No signals when both sides decay equally
- [ ] Confidence scores correlate with decay magnitude
- [ ] Strategy appears in heatmap at row 3, col 5
- [ ] No regressions in existing 22 strategies

---

## 6. Edge Cases

1. **Zero depth:** ROC = 0, no signal (handled)
2. **Both sides decaying equally:** No directional signal (handled)
3. **Depth dropping due to trades (not pull):** Volume/depth ratio is high → Gate C rejects
4. **Very thin book:** Gate A rejects (min_top5_depth)
5. **Rapid oscillation:** Use min_data_points to require sustained decay
6. **Market close/illiquid:** Low volume → volume/depth ratio may be unreliable
7. **Large single-level withdrawal:** Participant gate helps distinguish single-player pull vs broad exit

---

## 7. Dependencies & Impact

- **main.py:** Adds 5 new rolling window initializations, computes depth ROC and top-5 depth from existing depth data
- **rolling_keys.py:** Adds 5 new key constants
- **No changes to GEXCalculator:** Uses raw depth data
- **No changes to signal.py:** Uses existing Signal class
- **No changes to engine.py:** Uses existing BaseStrategy pattern
- **Grid:** Already 8×6. Just repositions row 3 col 5-6.

---

## 8. Implementation Order

1. **rolling_keys.py** — Add new depth decay keys (prerequisite)
2. **main.py** — Data ingestion (depth ROC, top-5 depth, volume/depth ratio)
3. **depth_decay_momentum.py** — Strategy implementation
4. **layer2/__init__.py** — Register DepthDecayMomentum
5. **heatmap.yaml** — Place at row 3 col 5, move VAMP to col 6
6. **strategies.yaml** — Depth decay config
7. **Test & validate**

---

*Plan by Archon. Ready for Forge to implement.* 🕸️
