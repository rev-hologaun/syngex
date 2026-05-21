# VAMP Momentum — Implementation Plan

**Strategy:** VAMP Momentum (Volume-Adjusted Mid-Price Momentum)
**Author:** Synapse (design) → Archon (plan)
**Layer:** Layer 2 — Microstructure Momentum
**Data Source:** `depthagg_parsed` (top 10 levels from market depth aggregates)
**Date:** 2026-05-12

---

## 1. Overview

VAMP computes a volume-weighted center of gravity from the top 10 bid/ask levels. When VAMP deviates from the simple mid-price, it reveals when the book is bid-weighted or ask-weighted — often before L1 price reacts.

**Core formula:**
```
VAMP = Σ(price_i × size_i) / Σ(size_i)   for all i in top 10 levels
Δ_VAMP = (VAMP - Mid) / Mid
```

**Signal:**
- LONG: Δ_VAMP > +0.0005 AND ROC(VAMP, 5) > 0
- SHORT: Δ_VAMP < -0.0005 AND ROC(VAMP, 5) < 0

**Hard gates (all must pass):**
- Gate A: Avg participants over top 10 > 1.5
- Gate B: Σ size(top 10) > MA(total depth, 60s) × 1.2
- Gate C: Spread < MA(spread, 5m)

---

## 2. Files to Create/Modify

### 2.1 New file: `strategies/layer2/vamp_momentum.py`

Full strategy implementation. Must follow the existing Layer 2 strategy pattern:
- `strategy_id = "vamp_momentum"`
- `layer = "layer2"`
- `evaluate(data) -> List[Signal]`
- 7-component confidence model
- Bidirectional (LONG and SHORT signals)

### 2.2 Modify: `strategies/rolling_keys.py`

Add these new rolling window keys:

```python
# VAMP Momentum
KEY_VAMP_5M = "vamp_5m"
KEY_VAMP_MID_DEV_5M = "vamp_mid_dev_5m"
KEY_VAMP_ROC_5M = "vamp_roc_5m"
KEY_VAMP_PARTICIPANTS_5M = "vamp_participants_5m"
KEY_VAMP_DEPTH_DENSITY_5M = "vamp_depth_density_5m"
```

Add to `ALL_KEYS` tuple and `__all__` list.

### 2.3 Modify: `main.py`

**A. Data ingestion (in `_on_message`):**

When processing `market_depth_agg` messages, parse top 10 levels from the depth agg data and compute VAMP. The depth agg data arrives as:

```python
data = {
    "type": "market_depth_agg",
    "best_bid": float,
    "best_ask": float,
    "mid_price": float,
    "spread": float,
    "total_bid_size": int,
    "total_ask_size": int,
    "bid_levels": int,
    "ask_levels": int,
    "bid_avg_participants": float,
    "ask_avg_participants": float,
    "bid_max_participants": int,
    "ask_max_participants": int,
    "top_3_bids": [...],  # list of {price, total_size, biggest_size, smallest_size, num_participants, ...}
    "top_3_asks": [...],
}
```

Since only top 3 levels are stored in rolling_data, we need to store the full top 10 (or more) levels for VAMP computation. Add to the depth agg processing block:

```python
# Store top N levels (for VAMP Momentum)
N_TOP_LEVELS = 10
bid_levels_full = [{"price": float(b.get("Price", 0)), "size": int(b.get("TotalSize", 0)), 
                    "participants": int(b.get("NumParticipants", 1))} for b in bids[:N_TOP_LEVELS]]
ask_levels_full = [{"price": float(a.get("Price", 0)), "size": int(a.get("TotalSize", 0)),
                    "participants": int(a.get("NumParticipants", 1))} for a in asks[:N_TOP_LEVELS]]
self._rolling_data["vamp_levels"] = {
    "bid_levels": bid_levels_full,
    "ask_levels": ask_levels_full,
    "mid_price": data.get("mid_price", 0),
    "spread": spread,
    "bid_avg_participants": data.get("bid_avg_participants", 0),
    "ask_avg_participants": data.get("ask_avg_participants", 0),
}
```

**B. Rolling window updates (in `_on_message`):**

After computing VAMP, push to rolling windows:

```python
ts = time.time()
if KEY_VAMP_5M in self._rolling_data:
    self._rolling_data[KEY_VAMP_5M].push(vamp, ts)
if KEY_VAMP_MID_DEV_5M in self._rolling_data:
    self._rolling_data[KEY_VAMP_MID_DEV_5M].push(vamp_mid_dev, ts)
if KEY_VAMP_ROC_5M in self._rolling_data:
    self._rolling_data[KEY_VAMP_ROC_5M].push(vamp_roc, ts)
if KEY_VAMP_PARTICIPANTS_5M in self._rolling_data:
    avg_participants = (data.get("bid_avg_participants", 0) + data.get("ask_avg_participants", 0)) / 2
    self._rolling_data[KEY_VAMP_PARTICIPANTS_5M].push(avg_participants, ts)
if KEY_VAMP_DEPTH_DENSITY_5M in self._rolling_data:
    self._rolling_data[KEY_VAMP_DEPTH_DENSITY_5M].push(total_bid_size + total_ask_size, ts)
```

**C. Pass data to strategies:**

In `_evaluate_strategies`, the `data` dict already contains `rolling_data` and `depth_snapshot`. The VAMP levels will be accessible via `data["rolling_data"]["vamp_levels"]`.

### 2.4 Modify: `strategies/layer2/__init__.py`

Add VampMomentum to imports and `__all__`:

```python
from .vamp_momentum import VampMomentum

__all__ = [
    "DeltaGammaSqueeze",
    "DeltaVolumeExhaustion",
    "CallPutFlowAsymmetry",
    "IVGEXDivergence",
    "DeltaIVDivergence",
    "VampMomentum",
]
```

### 2.5 Modify: `config/heatmap.yaml`

**A. Expand grid to 8 rows × 6 columns:**

```yaml
grid:
  columns: 6
  rows: 8
```

**B. Add VAMP Momentum to grid** — place at row 2, col 6 (first row, last column is full):

```yaml
  vamp_momentum:
    row: 2
    col: 6
    span_cols: 1
    span_rows: 1
```

Full grid placement:
```
Row 1: gamma_wall_bounce | magnet_accelerate | gamma_flip_breakout | gamma_squeeze | gex_imbalance | confluence_reversal
Row 2: vol_compression_range | gex_divergence | delta_gamma_squeeze | delta_volume_exhaustion | call_put_flow_asymmetry | vamp_momentum (NEW)
Row 3: iv_gex_divergence | iv_skew_squeeze | gamma_volume_convergence | iv_band_breakout | strike_concentration | theta_burn
Row 4: prob_weighted_magnet | prob_distribution_shift | extrinsic_intrinsic_flow | (empty) | (empty) | (empty)
Row 5-8: (reserved for future strategies)
```

### 2.6 Modify: `config/strategies.yaml`

Add to `layer2` section:

```yaml
  vamp_momentum:
    enabled: true
    tracker:
      max_hold_seconds: 1800
    params:
      # === Core VAMP params ===
      vamp_mid_dev_threshold: 0.0005       # Δ_VAMP threshold for signal
      vamp_roc_window: 5                    # Ticks for ROC calculation
      vamp_roc_threshold: 0.0               # ROC must be > 0 for LONG, < 0 for SHORT
      min_vamp_data_points: 10              # Min data points for VAMP stability

      # === Gate A: Participant Conviction ===
      min_avg_participants: 1.5             # Avg participants over top 10

      # === Gate B: Liquidity Density ===
      liquidity_density_min_mult: 1.2       # Σ size(top 10) > MA(total_depth, 60s) × 1.2
      depth_ma_window_seconds: 60           # Rolling window for depth MA

      # === Gate C: Spread Stability ===
      spread_stability_ma_seconds: 300      # 5m MA for spread comparison

      # === Execution ===
      stop_pct: 0.005                       # 0.5% stop loss
      target_risk_mult: 1.5                 # 1.5× risk for target
      min_confidence: 0.40                  # Raised for microstructure strategy
      max_confidence: 0.90

      # === Confidence factors ===
      # 1. VAMP deviation magnitude     (0.0–0.25) — soft
      # 2. VAMP ROC strength            (0.0–0.20) — soft
      # 3. Participant conviction       (0.0–0.15) — soft
      # 4. Liquidity density            (0.0–0.15) — soft
      # 5. Spread stability             (0.0–0.10) — soft
      # 6. GEX regime alignment         (0.0–0.10) — soft
      # 7. Depth level quality           (0.0–0.05) — soft
```

---

## 3. VAMP Momentum Strategy Implementation Details

### 3.1 Class structure

```python
class VampMomentum(BaseStrategy):
    strategy_id = "vamp_momentum"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        # 1. Get VAMP levels from rolling_data
        # 2. Compute VAMP, mid, Δ_VAMP
        # 3. Compute ROC of VAMP
        # 4. Apply 3 hard gates (participant, density, spread)
        # 5. If gates pass and signal direction clear → compute confidence
        # 6. Build and return Signal(s)
```

### 3.2 VAMP computation

From `data["rolling_data"]["vamp_levels"]`:

```python
vamp_levels = rolling_data.get("vamp_levels", {})
bid_levels = vamp_levels.get("bid_levels", [])
ask_levels = vamp_levels.get("ask_levels", [])
mid_price = vamp_levels.get("mid_price", 0)

# VAMP = Σ(price × size) / Σ(size) for all top levels
# For bids: price is the bid price, for asks: price is the ask price
# VAMP is the weighted center of the entire book

bid_weighted = sum(l["price"] * l["size"] for l in bid_levels)
bid_total = sum(l["size"] for l in bid_levels)
ask_weighted = sum(l["price"] * l["size"] for l in ask_levels)
ask_total = sum(l["size"] for l in ask_levels)

total_weighted = bid_weighted + ask_weighted
total_size = bid_total + ask_total

if total_size > 0:
    vamp = total_weighted / total_size
else:
    vamp = mid_price

vamp_mid_dev = (vamp - mid_price) / mid_price if mid_price > 0 else 0
```

### 3.3 ROC computation

```python
vamp_roc_window = self._params.get("vamp_roc_window", 5)
vamp_history = rolling_data.get(KEY_VAMP_5M)
if vamp_history and vamp_history.count >= vamp_roc_window:
    current_vamp = vamp_history.values[-1]
    past_vamp = vamp_history.values[-vamp_roc_window]
    vamp_roc = (current_vamp - past_vamp) / past_vamp if past_vamp != 0 else 0
```

### 3.4 Hard gates

```python
# Gate A: Participant conviction
avg_participants = (vamp_levels.get("bid_avg_participants", 0) + 
                    vamp_levels.get("ask_avg_participants", 0)) / 2
gate_a = avg_participants >= min_avg_participants

# Gate B: Liquidity density
depth_density = rolling_data.get(KEY_VAMP_DEPTH_DENSITY_5M)
if depth_density and depth_density.count > 0:
    ma_depth = sum(depth_density.values) / len(depth_density.values)
    current_depth = total_size
    gate_b = current_depth > ma_depth * liquidity_density_min_mult
else:
    gate_b = True  # No history yet

# Gate C: Spread stability
spread = vamp_levels.get("spread", 0)
spread_ma_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
if spread_ma_window and spread_ma_window.count > 0:
    ma_spread = sum(spread_ma_window.values) / len(spread_ma_window.values)
    gate_c = spread < ma_spread
else:
    gate_c = True  # No history yet

all_gates_pass = gate_a and gate_b and gate_c
```

### 3.5 Signal generation

```python
signals = []

if all_gates_pass:
    # LONG signal
    if vamp_mid_dev > threshold and vamp_roc > 0:
        signal = self._build_signal(data, "LONG", vamp, mid_price, vamp_mid_dev, vamp_roc)
        signals.append(signal)
    
    # SHORT signal
    elif vamp_mid_dev < -threshold and vamp_roc < 0:
        signal = self._build_signal(data, "SHORT", vamp, mid_price, vamp_mid_dev, vamp_roc)
        signals.append(signal)
```

### 3.6 Confidence model (7 components)

| # | Factor | Range | Type | Description |
|---|--------|-------|------|-------------|
| 1 | VAMP deviation magnitude | 0.0–0.25 | Soft | |Δ_VAMP| scaled linearly |
| 2 | VAMP ROC strength | 0.0–0.20 | Soft | |ROC| scaled, direction-aligned |
| 3 | Participant conviction | 0.0–0.15 | Soft | avg_participants above threshold |
| 4 | Liquidity density | 0.0–0.15 | Soft | current depth vs MA depth ratio |
| 5 | Spread stability | 0.0–0.10 | Soft | spread below MA spread |
| 6 | GEX regime alignment | 0.0–0.10 | Soft | VAMP direction matches GEX bias |
| 7 | Depth level quality | 0.0–0.05 | Soft | number of levels with participants > 1 |

### 3.7 Entry/Stop/Target

```python
entry = underlying_price
stop_distance = entry * stop_pct  # e.g., 0.5%

if direction == "LONG":
    stop = entry - stop_distance
    target = entry + (stop_distance * target_risk_mult)
else:
    stop = entry + stop_distance
    target = entry - (stop_distance * target_risk_mult)
```

---

## 4. Dashboard Integration

### 4.1 Heatmap card

The heatmap dashboard reads `config/heatmap.yaml` for strategy placement. VAMP will appear as a standard strategy card at row 2, col 6.

### 4.2 Card content

VAMP card should display:
- **Strategy name:** "VAMP Momentum"
- **Current Δ_VAMP:** formatted as percentage (e.g., "+0.08%" or "-0.12%")
- **Signal:** LONG/SHORT/NEUTRAL with color coding
  - Green: LONG signal active
  - Red: SHORT signal active
  - Grey: No signal
- **Gate status:** Small indicators for A/B/C gates
- **Heat intensity:** Based on |Δ_VAMP| magnitude

### 4.3 Implementation note

The heatmap dashboard (`app.py` or `dashboard.py`) reads strategy health data from the orchestrator. The VAMP strategy will report its Δ_VAMP value and gate status through the standard signal metadata mechanism. No separate dashboard code changes needed beyond the heatmap.yaml grid placement — the existing dashboard rendering loop will pick up the new strategy card.

---

## 5. Testing Checklist

- [ ] VAMP computation produces reasonable values (close to mid-price)
- [ ] Δ_VAMP sign correctly indicates bid vs ask weight
- [ ] ROC computation works with rolling window
- [ ] Gate A rejects single-participant walls
- [ ] Gate B rejects thin books
- [ ] Gate C rejects during spread expansion
- [ ] LONG signal fires when book is bid-weighted + rising
- [ ] SHORT signal fires when book is ask-weighted + falling
- [ ] No signals fire when gates fail
- [ ] Confidence scores correlate with signal strength
- [ ] Strategy appears in heatmap at correct position
- [ ] No regressions in existing 20 strategies

---

## 6. Edge Cases

1. **Empty bid/ask levels:** VAMP = mid_price, Δ_VAMP = 0 → no signal
2. **Single level:** VAMP = that level's price, but Gate A likely fails (participants = 1)
3. **Zero size at a level:** Skip in weighted sum (handled by `size > 0` check)
4. **Very small mid_price:** Guard against division by zero in Δ_VAMP
5. **First few ticks:** Rolling windows may not have enough data → use `min_vamp_data_points`
6. **Discontinuous price jumps:** VAMP may lag → ROC helps confirm direction
7. **Spoofed walls:** Gate A (participant conviction) is the primary anti-spoof filter

---

## 7. Dependencies & Impact

- **main.py:** Adds `vamp_levels` dict and 5 new rolling window pushes per depth_agg message
- **rolling_keys.py:** Adds 5 new key constants
- **No changes to GEXCalculator:** VAMP uses raw depth data, not option-derived metrics
- **No changes to signal.py:** Uses existing Signal class
- **No changes to engine.py:** Uses existing BaseStrategy pattern
- **No changes to GEXCalculator:** VAMP uses raw depth data, not option-derived metrics

---

## 8. Implementation Order

1. **rolling_keys.py** — Add new keys (prerequisite for everything else)
2. **main.py** — Data ingestion (VAMP computation + rolling window pushes)
3. **vamp_momentum.py** — Strategy implementation
4. **layer2/__init__.py** — Register VampMomentum
5. **heatmap.yaml** — Grid expansion + VAMP placement
6. **strategies.yaml** — VAMP config
7. **Test & validate**

---

*Plan by Archon. Ready for Forge to implement.* 🕸️
