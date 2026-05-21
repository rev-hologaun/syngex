# Depth Imbalance Momentum — Implementation Plan

**Strategy:** Depth Imbalance Momentum (Pressure-Tracking Engine)
**Author:** Synapse (design) → Archon (plan)
**Layer:** Layer 2 — Microstructure Pressure
**Data Sources:** `depthagg_parsed` (bid/ask size aggregates)
**Date:** 2026-05-12

---

## 1. Overview

Tracks the **structural weight** of the order book. When the bid side becomes massively larger than the ask side (or vice versa), it creates gravitational pressure. Combined with ROC, we detect when this pressure is *accelerating*, not just static.

**Core formulas:**
```
IR = Total_Bid_Size / Total_Ask_Size
  IR > 3.0 = heavy bid pressure (bullish)
  IR < 0.6 = heavy ask pressure (bearish)

ROC(IR) = (IR_current - IR_lookback) / IR_lookback
  ROC > 0 = imbalance increasing
  ROC < 0 = imbalance decreasing
```

**Key distinction from Depth Decay:**
- Depth Decay = liquidity *evaporating* (orders pulled without being hit)
- Depth Imbalance = liquidity *shifting* (weight moving to one side)
- They are complementary: Imbalance shows intent, Decay shows lack of resistance

---

## 2. Files to Create/Modify

### 2.1 New file: `strategies/layer2/depth_imbalance_momentum.py`

Full strategy implementation following the Layer 2 pattern.

### 2.2 Modify: `strategies/rolling_keys.py`

Add these new rolling window keys:

```python
# Depth Imbalance Momentum
KEY_IR_5M = "imbalance_ratio_5m"           # IR = bid_size / ask_size
KEY_IR_ROC_5M = "imbalance_ratio_roc_5m"   # ROC of IR
KEY_IR_PARTICIPANTS_5M = "ir_participants_5m"  # avg participants on imbalance side
```

Add to `ALL_KEYS` tuple and `__all__` list.

### 2.3 Modify: `main.py`

**A. Rolling window initializations** (in `__init__`, alongside other RollingWindow defs around line 325):

```python
KEY_IR_5M: RollingWindow(window_type="time", window_size=300),
KEY_IR_ROC_5M: RollingWindow(window_type="time", window_size=300),
KEY_IR_PARTICIPANTS_5M: RollingWindow(window_type="time", window_size=300),
```

**B. IR computation** (in `_on_message`, inside the `market_depth_agg` block, after existing depth pushes around line 1225):

The `KEY_DEPTH_BID_SIZE_5M` and `KEY_DEPTH_ASK_SIZE_5M` windows are already being pushed. We compute IR from these:

```python
# ── Depth Imbalance Momentum: compute IR and ROC ──
bid_size_window = self._rolling_data.get(KEY_DEPTH_BID_SIZE_5M)
ask_size_window = self._rolling_data.get(KEY_DEPTH_ASK_SIZE_5M)

ir = 0.0
ir_roc = 0.0

if bid_size_window and ask_size_window and bid_size_window.count > 0 and ask_size_window.count > 0:
    current_bid = bid_size_window.values[-1]
    current_ask = ask_size_window.values[-1]
    if current_ask > 0:
        ir = current_bid / current_ask
    else:
        ir = 999.0  # Extreme imbalance when ask is near zero
    
    # ROC of IR
    if bid_size_window.count >= 5 and ask_size_window.count >= 5:
        old_bid = bid_size_window.values[-5]
        old_ask = ask_size_window.values[-5]
        if old_ask > 0:
            old_ir = old_bid / old_ask
            if old_ir > 0:
                ir_roc = (ir - old_ir) / old_ir
            else:
                ir_roc = 0.0

if KEY_IR_5M in self._rolling_data:
    self._rolling_data[KEY_IR_5M].push(ir, ts)
if KEY_IR_ROC_5M in self._rolling_data:
    self._rolling_data[KEY_IR_ROC_5M].push(ir_roc, ts)
```

**C. Import the new keys** at top of main.py.

### 2.4 Modify: `strategies/layer2/__init__.py`

Add `DepthImbalanceMomentum` to imports and `__all__`.

### 2.5 Modify: `config/heatmap.yaml`

**A. Fix heatmap conflict:** `theta_burn` and `strike_concentration` are both at row 3, col 4. Fix:

```yaml
  strike_concentration:
    row: 3
    col: 4
    span_cols: 1
    span_rows: 1
  # theta_burn should be at col 5, but depth_decay_momentum is there
  # Move theta_burn to row 4 col 5
  theta_burn:
    row: 4
    col: 5
    span_cols: 1
    span_rows: 1
```

**B. Add Depth Imbalance Momentum** at row 4, col 6 (last free slot in row 4):

```yaml
  depth_imbalance_momentum:
    row: 4
    col: 6
    span_cols: 1
    span_rows: 1
```

**C. Move theta_burn** to row 4, col 5 (currently conflicts with strike_concentration at row 3 col 4):

```yaml
  theta_burn:
    row: 4
    col: 5
    span_cols: 1
    span_rows: 1
```

### 2.6 Modify: `config/strategies.yaml`

Add under `layer2:` section:

```yaml
  depth_imbalance_momentum:
    enabled: true
    tracker:
      max_hold_seconds: 1800
    params:
      # === Core IR params ===
      ir_threshold_long: 3.0              # IR > 3.0 for LONG
      ir_threshold_short: 0.6             # IR < 0.6 for SHORT
      ir_exit_threshold: 1.5              # Exit when IR drops below this
      min_ir_data_points: 10              # Min data points for IR stability

      # === Momentum (ROC) ===
      ir_roc_window: 5                    # 5-tick lookback for ROC
      ir_roc_threshold_long: 0.0          # ROC > 0 for LONG (rising imbalance)
      ir_roc_threshold_short: 0.0         # ROC < 0 for SHORT (falling imbalance)

      # === Gate A: Participant Conviction ===
      min_avg_participants: 2.0           # Avg participants on imbalance side > 2

      # === Gate B: Depth Decay Check ===
      max_total_depth_decay: 0.05         # Total depth shouldn't be evaporating

      # === Gate C: Volume Confirmation ===
      volume_min_mult: 1.0                # Volume >= MA(volume)

      # === VAMP Validation ===
      use_vamp_validation: true           # Require VAMP near mid

      # === Execution ===
      stop_pct: 0.008                     # 0.8% stop loss (wider for momentum)
      target_risk_mult: 2.0               # 2× risk for momentum target
      min_confidence: 0.40
      max_confidence: 0.90

      # === Confidence factors ===
      # 1. IR magnitude                   (0.0–0.25) — soft
      # 2. IR ROC strength                (0.0–0.20) — soft
      # 3. Participant conviction         (0.0–0.15) — soft
      # 4. Depth decay check              (0.0–0.10) — soft
      # 5. Volume confirmation            (0.0–0.10) — soft
      # 6. VAMP validation                (0.0–0.10) — soft
      # 7. GEX regime alignment           (0.0–0.10) — soft
```

---

## 3. Depth Imbalance Momentum Strategy Implementation Details

### 3.1 Class structure

```python
class DepthImbalanceMomentum(BaseStrategy):
    strategy_id = "depth_imbalance_momentum"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        # 1. Get IR and ROC from rolling_data
        # 2. Apply 3 hard gates
        # 3. Check VAMP validation
        # 4. If gates pass and IR threshold clear → compute confidence
        # 5. Build and return Signal(s)
```

### 3.2 IR computation

Already computed in main.py and stored in `rolling_data[KEY_IR_5M]`.

```python
ir_window = rolling_data.get(KEY_IR_5M)
if ir_window and ir_window.count >= min_ir_data_points:
    current_ir = ir_window.values[-1]
else:
    return []  # Not enough data
```

### 3.3 ROC computation

Already computed in main.py and stored in `rolling_data[KEY_IR_ROC_5M]`.

```python
ir_roc_window = rolling_data.get(KEY_IR_ROC_5M)
if ir_roc_window and ir_roc_window.count >= 5:
    current_ir_roc = ir_roc_window.values[-1]
else:
    return []  # Not enough data for ROC
```

### 3.4 Signal logic

```python
# LONG: IR > 3.0 (heavy bid pressure) AND ROC > 0 (imbalance rising)
# SHORT: IR < 0.6 (heavy ask pressure) AND ROC < 0 (imbalance falling)

long_signal = current_ir > ir_threshold_long and current_ir_roc > ir_roc_threshold_long
short_signal = current_ir < ir_threshold_short and current_ir_roc < ir_roc_threshold_short
```

### 3.5 Hard gates

```python
# Gate A: Participant conviction — imbalance side must have > 2 participants
# Use bid_avg_participants and ask_avg_participants from depth_agg
depth_data = data.get("depth_snapshot", {})
avg_participants = (data.get("bid_avg_participants", 0) + data.get("ask_avg_participants", 0)) / 2
gate_a = avg_participants >= min_avg_participants

# Gate B: Depth decay check — total depth shouldn't be evaporating
depth_decay_window = rolling_data.get(KEY_DEPTH_DECAY_BID_5M)
# Use the depth decay windows already computed in main.py
gate_b = True  # Check that total depth isn't rapidly evaporating

# Gate C: Volume confirmation — volume should be at least average
volume_window = rolling_data.get(KEY_VOLUME_5M)
gate_c = True  # Check current volume >= MA(volume)
```

### 3.6 VAMP validation

```python
# VAMP should be near mid-price (not far away from the weight)
# If VAMP is far from mid, the book weight doesn't reflect actual price
vamp_levels = rolling_data.get("vamp_levels", {})
mid_price = vamp_levels.get("mid_price", 0)
if use_vamp_validation and mid_price > 0:
    vamp_deviation = abs(vamp - mid_price) / mid_price
    # If deviation is too large, skip (price already moved)
```

### 3.7 Confidence model (7 components)

| # | Factor | Range | Type | Description |
|---|--------|-------|------|-------------|
| 1 | IR magnitude | 0.0–0.25 | Soft | How extreme the IR is (3.0+ = strong) |
| 2 | IR ROC strength | 0.0–0.20 | Soft | How fast the imbalance is changing |
| 3 | Participant conviction | 0.0–0.15 | Soft | Avg participants above threshold |
| 4 | Depth decay check | 0.0–0.10 | Soft | Total depth stable (not evaporating) |
| 5 | Volume confirmation | 0.0–0.10 | Soft | Volume above average |
| 6 | VAMP validation | 0.0–0.10 | Soft | VAMP near mid (not divergent) |
| 7 | GEX regime alignment | 0.0–0.10 | Soft | IR direction matches GEX bias |

### 3.8 Entry/Stop/Target

```python
entry = underlying_price
stop_distance = entry * stop_pct  # 0.8%

if direction == "LONG":
    stop = entry - stop_distance
    target = entry + (stop_distance * target_risk_mult)  # 1.6% target
else:
    stop = entry + stop_distance
    target = entry - (stop_distance * target_risk_mult)
```

---

## 4. Dashboard Integration

### 4.1 Heatmap card

Placed at row 4, col 6. Also fixes the `theta_burn` / `strike_concentration` conflict at row 3 col 4.

### 4.2 Card content

Depth Imbalance card displays:
- **Current IR:** formatted as ratio (e.g., "3.42" or "0.55")
- **IR ROC:** formatted as percentage (e.g., "+12%" or "-8%")
- **Signal:** LONG/SHORT/NEUTRAL with color coding
  - Electric Green: High bid pressure (IR rising)
  - Deep Crimson: High ask pressure (IR falling)
- **Metric:** Current Imbalance Ratio value

---

## 5. Testing Checklist

- [ ] IR correctly computes (bid_size / ask_size)
- [ ] IR > 3.0 triggers LONG candidate
- [ ] IR < 0.6 triggers SHORT candidate
- [ ] ROC correctly measures IR rate of change
- [ ] Gate A rejects when participants < 2
- [ ] Gate B rejects when total depth is evaporating
- [ ] Gate C rejects when volume is below average
- [ ] VAMP validation works when enabled
- [ ] No signals when IR is between 0.6 and 3.0
- [ ] Confidence scores correlate with IR magnitude
- [ ] Strategy appears in heatmap at row 4, col 6
- [ ] No regressions in existing 23 strategies
- [ ] Heatmap conflict (theta_burn / strike_concentration) resolved

---

## 6. Edge Cases

1. **Zero ask size:** IR → infinity, handled by checking ask > 0
2. **Both sizes near zero:** IR meaningless, gate B (depth decay) catches this
3. **IR extreme but ROC flat:** Static imbalance (possibly spoofed) → gate A (participants) catches
4. **IR extreme but total depth evaporating:** Fake imbalance caused by ask disappearing → gate B catches
5. **Very thin book:** Gate B rejects (depth too thin)
6. **Rapid IR oscillation:** Use min_data_points to require sustained imbalance
7. **Market open/close:** Volume may be unreliable → gate C handles

---

## 7. Dependencies & Impact

- **main.py:** Adds 3 new rolling window initializations, computes IR and ROC from existing bid/ask size windows
- **rolling_keys.py:** Adds 3 new key constants
- **No changes to GEXCalculator:** IR uses raw depth data
- **No changes to signal.py:** Uses existing Signal class
- **No changes to engine.py:** Uses existing BaseStrategy pattern
- **Grid:** Row 4 col 6 is free. Also fixes theta_burn / strike_concentration conflict.

---

## 8. Implementation Order

1. **rolling_keys.py** — Add new IR keys (prerequisite)
2. **main.py** — Data ingestion (IR and ROC from existing bid/ask size windows)
3. **depth_imbalance_momentum.py** — Strategy implementation
4. **layer2/__init__.py** — Register DepthImbalanceMomentum
5. **heatmap.yaml** — Fix theta_burn conflict, place at row 4 col 6
6. **strategies.yaml** — Depth imbalance config
7. **Test & validate**

---

*Plan by Archon. Ready for Forge to implement.* 🕸️
