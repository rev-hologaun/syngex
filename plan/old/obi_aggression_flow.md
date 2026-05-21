# OBI + Aggression Flow — Implementation Plan

**Strategy:** OBI + Aggression Flow (Order Book Imbalance + Aggressive Trade Flow)
**Author:** Synapse (design) → Archon (plan)
**Layer:** Layer 2 — Microstructure Execution
**Data Sources:** `depthagg_parsed` (OBI), quotes stream (Aggression Flow)
**Date:** 2026-05-12

---

## 1. Overview

OBI detects passive order book skew; Aggression Flow validates with actual trade execution. Only enter when BOTH the passive book AND active trades agree on direction — filters out spoofing and passive walls that never get tested.

**Core formulas:**
```
OBI = (Total_Bid_Size - Total_Ask_Size) / (Total_Bid_Size + Total_Ask_Size)
  Range: -1.0 (pure ask) to +1.0 (pure bid)

AF = (Aggressive_Buy_Volume - Aggressive_Sell_Volume) / Total_Trade_Volume
  Range: -1.0 (pure sell aggression) to +1.0 (pure buy aggression)

Master Trigger: OBI × AF > 0 (same direction) AND |OBI| > 0.75 AND |AF| > 0.5
```

---

## 2. Files to Create/Modify

### 2.1 New file: `strategies/layer2/obi_aggression_flow.py`

Full strategy implementation. Must follow the existing Layer 2 strategy pattern.

### 2.2 Modify: `strategies/rolling_keys.py`

Add these new rolling window keys:

```python
# OBI + Aggression Flow
KEY_OBI_5M = "obi_5m"
KEY_AGGRESSIVE_BUY_VOL_5M = "aggressive_buy_vol_5m"
KEY_AGGRESSIVE_SELL_VOL_5M = "aggressive_sell_vol_5m"
KEY_AF_5M = "aggression_flow_5m"
KEY_TRADE_SIZE_5M = "trade_size_5m"
```

Add to `ALL_KEYS` tuple and `__all__` list. Add a new `OBI_KEYS` tuple.

### 2.3 Modify: `main.py`

**A. Rolling window initializations** (in `__init__`, alongside other RollingWindow defs):

```python
KEY_OBI_5M: RollingWindow(window_type="time", window_size=300),
KEY_AGGRESSIVE_BUY_VOL_5M: RollingWindow(window_type="time", window_size=300),
KEY_AGGRESSIVE_SELL_VOL_5M: RollingWindow(window_type="time", window_size=300),
KEY_AF_5M: RollingWindow(window_type="time", window_size=300),
KEY_TRADE_SIZE_5M: RollingWindow(window_type="time", window_size=300),
```

**B. OBI computation** (in `_on_message`, inside the existing `market_depth_agg` block — total_bid_size and total_ask_size are already computed there):

```python
# OBI computation from depth agg
total_depth = total_bid_size + total_ask_size
if total_depth > 0:
    obi = (total_bid_size - total_ask_size) / total_depth
else:
    obi = 0.0

ts = time.time()
if KEY_OBI_5M in self._rolling_data:
    self._rolling_data[KEY_OBI_5M].push(obi, ts)
```

**C. Aggression Flow from quotes** (NEW — add a handler block in `_on_message`, right AFTER the `market_depth_agg` block and BEFORE the `option_update` block):

IMPORTANT: The quotes stream from tradestation_client.py dispatches raw TradeStation data with fields `Bid`, `Ask`, `Last`, `BidSize`, `AskSize`, `Volume`, `LastSize`, `LastVenue` (capitalized). There is NO `type` field on quote data. Detect quotes by checking for `"Bid"` and `"Ask"` keys.

```python
# Aggression Flow from quotes stream — detect aggressive trades
# Quote data has "Bid" and "Ask" fields (capitalized, from raw TS API)
if "Bid" in data and "Ask" in data:
    last = float(data.get("Last", 0) or 0)
    bid = float(data.get("Bid", 0) or 0)
    ask = float(data.get("Ask", 0) or 0)
    last_size = data.get("LastSize", 0)
    if isinstance(last_size, str):
        try:
            last_size = int(last_size)
        except (ValueError, TypeError):
            last_size = 0
    
    if last_size > 0:
        if last >= ask and ask > 0:
            # Aggressive buy — hit the ask
            if KEY_AGGRESSIVE_BUY_VOL_5M in self._rolling_data:
                self._rolling_data[KEY_AGGRESSIVE_BUY_VOL_5M].push(last_size, ts)
        elif last <= bid and bid > 0:
            # Aggressive sell — hit the bid
            if KEY_AGGRESSIVE_SELL_VOL_5M in self._rolling_data:
                self._rolling_data[KEY_AGGRESSIVE_SELL_VOL_5M].push(last_size, ts)
        
        # Track individual trade size for volume gate
        if KEY_TRADE_SIZE_5M in self._rolling_data:
            self._rolling_data[KEY_TRADE_SIZE_5M].push(last_size, ts)
    
    # Compute AF from rolling aggressive volumes
    buy_vol_window = self._rolling_data.get(KEY_AGGRESSIVE_BUY_VOL_5M)
    sell_vol_window = self._rolling_data.get(KEY_AGGRESSIVE_SELL_VOL_5M)
    if buy_vol_window and sell_vol_window and buy_vol_window.count > 0 and sell_vol_window.count > 0:
        total_buy = sum(buy_vol_window.values)
        total_sell = sum(sell_vol_window.values)
        total_aggressive = total_buy + total_sell
        if total_aggressive > 0:
            af = (total_buy - total_sell) / total_aggressive
        else:
            af = 0.0
    else:
        af = 0.0
    
    if KEY_AF_5M in self._rolling_data:
        self._rolling_data[KEY_AF_5M].push(af, ts)
```

**D. Import the new keys** at top of main.py:

```python
from strategies.rolling_keys import (
    # ... existing imports ...
    KEY_OBI_5M,
    KEY_AGGRESSIVE_BUY_VOL_5M,
    KEY_AGGRESSIVE_SELL_VOL_5M,
    KEY_AF_5M,
    KEY_TRADE_SIZE_5M,
)
```

### 2.4 Modify: `strategies/layer2/__init__.py`

Add `ObiAggressionFlow` to imports and `__all__`.

### 2.5 Modify: `config/heatmap.yaml`

**A. Grid already expanded to 8×6 from VAMP.** No change needed.

**B. Add OBI + Aggression Flow** — place at row 2, col 5 (push call_put_flow_asymmetry to col 6):

```yaml
  obi_aggression_flow:
    row: 2
    col: 5
    span_cols: 1
    span_rows: 1
```

**Update call_put_flow_asymmetry** to col 6:
```yaml
  call_put_flow_asymmetry:
    row: 2
    col: 6
    span_cols: 1
    span_rows: 1
```

### 2.6 Modify: `config/strategies.yaml`

Add under `layer2:` section:

```yaml
  obi_aggression_flow:
    enabled: true
    tracker:
      max_hold_seconds: 900
    params:
      # === Core OBI/AF params ===
      obi_threshold: 0.75               # |OBI| must exceed this
      af_threshold: 0.5                 # |AF| must exceed this
      min_obi_data_points: 10           # Min data points for OBI stability
      min_af_data_points: 5             # Min data points for AF stability

      # === Gate A: Volume Threshold ===
      volume_spike_mult: 2.0            # Trade size > 2× avg trade size
      trade_size_ma_window: 300         # 5m MA for trade size

      # === Gate B: Participant Diversity ===
      min_avg_participants: 1.0         # (from depth_agg, already available)

      # === Gate C: Spread Stability ===
      max_spread_multiplier: 1.5        # Spread < 1.5× MA spread

      # === Execution ===
      stop_pct: 0.005                   # 0.5% stop loss
      target_risk_mult: 1.5             # 1.5× risk for target
      min_confidence: 0.45              # Higher bar for execution strategy
      max_confidence: 0.90

      # === Confidence factors ===
      # 1. OBI magnitude                (0.0–0.25) — soft
      # 2. AF magnitude                 (0.0–0.25) — soft
      # 3. OBI × AF confluence          (0.0–0.15) — soft
      # 4. Volume spike strength        (0.0–0.10) — soft
      # 5. Participant diversity        (0.0–0.10) — soft
      # 6. Spread stability             (0.0–0.05) — soft
      # 7. GEX regime alignment         (0.0–0.10) — soft
```

---

## 3. OBI + Aggression Flow Strategy Implementation Details

### 3.1 Class structure

```python
class ObiAggressionFlow(BaseStrategy):
    strategy_id = "obi_aggression_flow"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        # 1. Get OBI from rolling_data
        # 2. Get AF from rolling_data
        # 3. Compute master trigger: OBI × AF
        # 4. Apply 3 hard gates (volume, participants, spread)
        # 5. If gates pass and master trigger clear → compute confidence
        # 6. Build and return Signal(s)
```

### 3.2 OBI computation

Already computed in main.py and stored in `rolling_data[KEY_OBI_5M]`.

```python
obi_window = rolling_data.get(KEY_OBI_5M)
if obi_window and obi_window.count >= min_obi_data_points:
    current_obi = obi_window.values[-1]
else:
    return []  # Not enough data
```

### 3.3 AF computation

Already computed in main.py and stored in `rolling_data[KEY_AF_5M]`.

```python
af_window = rolling_data.get(KEY_AF_5M)
if af_window and af_window.count >= min_af_data_points:
    current_af = af_window.values[-1]
else:
    return []  # Not enough data
```

### 3.4 Master trigger

```python
# LONG: OBI > 0.75 (bid heavy) AND AF > 0.5 (buy aggression)
# SHORT: OBI < -0.75 (ask heavy) AND AF < -0.5 (sell aggression)

long_signal = current_obi > obi_threshold and current_af > af_threshold
short_signal = current_obi < -obi_threshold and current_af < -af_threshold
```

### 3.5 Hard gates

```python
# Gate A: Volume threshold — triggering trade size > 2× average
trade_size_window = rolling_data.get(KEY_TRADE_SIZE_5M)
gate_a = True
if trade_size_window and trade_size_window.count > 0:
    avg_trade_size = sum(trade_size_window.values) / len(trade_size_window.values)
    # Use latest trade size from depth_agg snapshot
    latest_trade_size = data.get("depth_snapshot", {}).get("last_size", 0)
    if avg_trade_size > 0:
        gate_a = latest_trade_size > avg_trade_size * volume_spike_mult

# Gate B: Participant diversity — from depth_agg
gate_b = True  # Validated by data quality

# Gate C: Spread stability
spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
gate_c = True
if spread_window and spread_window.count > 0:
    ma_spread = sum(spread_window.values) / len(spread_window.values)
    current_spread = data.get("depth_snapshot", {}).get("spread", 0)
    if ma_spread > 0:
        gate_c = current_spread < ma_spread * max_spread_multiplier

all_gates_pass = gate_a and gate_b and gate_c
```

### 3.6 Confidence model (7 components)

| # | Factor | Range | Type | Description |
|---|--------|-------|------|-------------|
| 1 | OBI magnitude | 0.0–0.25 | Soft | `|OBI|` scaled to [0, 0.25] |
| 2 | AF magnitude | 0.0–0.25 | Soft | `|AF|` scaled to [0, 0.25] |
| 3 | OBI × AF confluence | 0.0–0.15 | Soft | Product magnitude, direction-aligned |
| 4 | Volume spike strength | 0.0–0.10 | Soft | Trade size vs MA ratio |
| 5 | Participant diversity | 0.0–0.10 | Soft | Avg participants above threshold |
| 6 | Spread stability | 0.0–0.05 | Soft | Spread below MA threshold |
| 7 | GEX regime alignment | 0.0–0.10 | Soft | OBI direction matches GEX bias |

### 3.7 Entry/Stop/Target

```python
entry = underlying_price
stop_distance = entry * stop_pct  # 0.5%

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

VAMP already expanded grid to 8×6. OBI placed at row 2, col 5. call_put_flow_asymmetry moves to col 6.

### 4.2 Card content

OBI card displays:
- **Current OBI:** formatted as fraction (e.g., "+0.82" or "-0.65")
- **Current AF:** formatted as fraction (e.g., "+0.73" or "-0.58")
- **Signal:** LONG/SHORT/NEUTRAL with color coding
- **Heat intensity:** Based on |OBI × AF| product

---

## 5. Testing Checklist

- [ ] OBI correctly ranges from -1.0 to +1.0
- [ ] OBI > 0 when bids dominate, < 0 when asks dominate
- [ ] AF correctly tracks aggressive buy vs sell volume
- [ ] AF > 0 when buy aggression dominates, < 0 when sell dominates
- [ ] LONG signal fires when OBI > 0.75 AND AF > 0.5
- [ ] SHORT signal fires when OBI < -0.75 AND AF < -0.5
- [ ] Gate A rejects trades below volume spike threshold
- [ ] Gate C rejects during spread expansion
- [ ] No signals when OBI and AF disagree (spoofing scenario)
- [ ] Confidence scores correlate with signal strength
- [ ] Strategy appears in heatmap at row 2, col 5
- [ ] No regressions in existing 21 strategies

---

## 6. Edge Cases

1. **Zero depth:** OBI = 0, no signal (handled)
2. **No trades yet:** AF = 0, no signal (handled by min_af_data_points)
3. **OBI extreme but no AF:** Spoofing detected → no signal (master trigger fails)
4. **AF extreme but OBI neutral:** No book pressure → no signal (master trigger fails)
5. **Rapid OBI oscillation:** Use min_data_points to require sustained imbalance
6. **Very small trade sizes:** Gate A filters out retail noise
7. **Spread widening during signal:** Gate C prevents entry during slippage-heavy conditions

---

## 7. Dependencies & Impact

- **main.py:** Adds 5 new rolling window initializations, handles raw quotes data for aggression detection, computes OBI from existing depth_agg data
- **rolling_keys.py:** Adds 5 new key constants
- **No changes to GEXCalculator:** OBI uses raw depth data, AF uses raw quotes data
- **No changes to signal.py:** Uses existing Signal class
- **No changes to engine.py:** Uses existing BaseStrategy pattern
- **Grid:** Already 8×6 from VAMP. Just repositions row 2 col 5-6.

---

## 8. Implementation Order

1. **rolling_keys.py** — Add new OBI/AF keys (prerequisite)
2. **main.py** — Data ingestion (OBI from depth_agg + AF from quotes)
3. **obi_aggression_flow.py** — Strategy implementation
4. **layer2/__init__.py** — Register ObiAggressionFlow
5. **heatmap.yaml** — Place OBI at row 2 col 5, move call_put_flow to col 6
6. **strategies.yaml** — OBI config
7. **Test & validate**

---

*Plan by Archon. Ready for Forge to implement.* 🕸️
