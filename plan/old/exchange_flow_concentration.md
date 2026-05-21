# Plan: Exchange Flow Concentration

**Author:** Archon (adapted from Synapse design v1.0)  
**Target Layer:** Layer 2 (Venue-Specific Flow)  
**Heatmap Placement:** Row 5, Col 1 (currently empty)  
**Data Source:** `market_depth_quotes` → `bid_exchanges` / `ask_exchanges` per level

---

## 1. Concept

Not all liquidity is created equal. MEMX and BATS are **aggressive execution venues** — HFTs and institutional algos sweep there. IEX has a **speed bump** and is known for passive, intent-driven liquidity (and spoofing).

**Core insight:** A surge in bid/ask ratio specifically on MEMX or BATS signals aggressive directional flow. An IEX intent score filters out spoofed walls.

---

## 2. Data Source Analysis

### Current Gap
`main.py` currently only aggregates `total_bid_size` and `total_ask_size` from the depth_quotes stream. The per-exchange dictionaries (`bid_exchanges`, `ask_exchanges`) on each bid/ask level are **not parsed**.

### What main.py must add (inside `msg_type == "market_depth_quotes"` block, ~line 1219)

For each bid level:
```python
for b in bids:
    exchanges = b.get("bid_exchanges", {})  # {"MEMX": "500", "BATS": "300", ...}
    for venue, size_str in exchanges.items():
        size = int(size_str)
        exchange_bid_sizes[venue] += size
```

For each ask level:
```python
for a in asks:
    exchanges = a.get("ask_exchanges", {})
    for venue, size_str in exchanges.items():
        size = int(size_str)
        exchange_ask_sizes[venue] += size
```

Then compute per-venue totals:
- `memx_bid_size = exchange_bid_sizes.get("MEMX", 0)`
- `memx_ask_size = exchange_ask_sizes.get("MEMX", 0)`
- `bats_bid_size = exchange_bid_sizes.get("BATS", 0)`
- `bats_ask_size = exchange_ask_sizes.get("BATS", 0)`
- `iex_bid_size = exchange_bid_sizes.get("IEX", 0)`
- `iex_ask_size = exchange_ask_sizes.get("IEX", 0)`

---

## 3. Signal Computation

### 3.1 Venue-Specific Imbalance (VSI)

```
VSI_MEMX  = memx_bid_size / memx_ask_size    (999 if ask=0)
VSI_BATS  = bats_bid_size / bats_ask_size    (999 if ask=0)
VSI_COMBINED = max(VSI_MEMX, VSI_BATS)       # Use the more extreme venue
```

### 3.2 VSI ROC (Aggression Velocity)

Rolling ROC over 5-tick (~30s) lookback:
```
vsi_roc = (current_vsi - past_vsi) / past_vsi   # past = values[-5]
```

### 3.3 IEX Intent Score

```
iex_total_size = iex_bid_size + iex_ask_size
total_book_size = total_bid_size + total_ask_size
iex_intent = iex_total_size / total_book_size    # Fraction of book on IEX
```

**Interpretation:** High IEX intent (>0.30) = passive/spoofed liquidity. Low IEX intent (<0.20) = genuine aggressive flow on other venues.

### 3.4 Signal Triggers

| Direction | VSI_COMBINED | VSI_ROC |
|-----------|-------------|---------|
| LONG      | > 2.0       | > 0     |
| SHORT     | < 0.5       | < 0     |

> **Archon note:** Synapse proposed 2.5/0.4. Lowering to 2.0/0.5 for better signal frequency while keeping gates strict.

---

## 4. Hard Gates (All Must Pass)

### Gate A: Exchange Dominance
The venue-specific bid+ask (MEMX or BATS) must account for ≥ 15% of total book depth on the signal side.

```
signal_venue_size = memx_bid_size if LONG else memx_ask_size
total_depth = total_bid_size + total_ask_size
exchange_dominance = signal_venue_size / total_depth
gate_a = exchange_dominance >= 0.15
```

### Gate B: IEX Intent Filter
IEX intent score must be below threshold (not a spoofed book).

```
gate_b = iex_intent <= 0.35
```

### Gate C: Cross-Venue Validation
Total volume must be above average (confirms exchange imbalance results in actual trades).

```
current_vol = rolling_data[KEY_VOLUME_5M].latest
avg_vol = rolling_data[KEY_VOLUME_5M].mean
gate_c = current_vol >= avg_vol * 0.8   # Slightly relaxed for microstructure
```

---

## 5. Confidence Model (7 Components)

| # | Component | Range | Logic |
|---|-----------|-------|-------|
| 1 | VSI Magnitude | 0.0–0.25 | How extreme VSI is (at 2.0 = baseline, at 4.0+ = max) |
| 2 | VSI ROC Strength | 0.0–0.20 | How fast VSI is changing |
| 3 | Exchange Dominance | 0.0–0.15 | What % of total book is on the signal venue |
| 4 | IEX Intent Clean | 0.0–0.10 | Low IEX = high conviction |
| 5 | Volume Confirmation | 0.0–0.10 | Volume above average |
| 6 | VAMP Validation | 0.0–0.10 | VAMP direction aligns with signal |
| 7 | GEX Regime Alignment | 0.0–0.10 | Signal direction matches GEX bias |

---

## 6. Execution Parameters

| Parameter | Value |
|-----------|-------|
| Stop loss | 0.5% |
| Target risk mult | 1.5× |
| Min confidence | 0.40 |
| Max confidence | 0.90 |
| Max hold | 1800s (30 min) |

---

## 7. Implementation Steps

### Step 1: `strategies/rolling_keys.py`
Add 3 new keys:
```python
KEY_VSI_COMBINED_5M = "vsi_combined_5m"
KEY_VSI_ROC_5M = "vsi_roc_5m"
KEY_IEX_INTENT_5M = "iex_intent_5m"
```

Add to `ALL_KEYS` tuple and `__all__` list.

### Step 2: `main.py` (~line 1219, inside `market_depth_quotes` block)
After computing `total_bid_size`/`total_ask_size`, add:

1. Parse per-exchange sizes from `bid_exchanges`/`ask_exchanges` dicts on each level
2. Sum by venue: `MEMX`, `BATS`, `IEX` for both bid and ask
3. Compute `VSI_COMBINED = max(memx_vsi, bats_vsi)`
4. Compute `VSI_ROC` over 5-tick lookback
5. Compute `IEX_INTENT = (iex_bid + iex_ask) / total_depth`
6. Push all 3 to rolling windows

### Step 3: `strategies/layer2/exchange_flow_concentration.py`
New strategy class:
- `strategy_id = "exchange_flow_concentration"`
- `layer = "layer2"`
- `evaluate(data) -> List[Signal]`
- Implements signal triggers, 3 hard gates, 7-component confidence
- Follows exact same structure as `depth_imbalance_momentum.py`

### Step 4: `strategies/layer2/__init__.py`
Add import and `__all__` entry for `ExchangeFlowConcentration`.

### Step 5: `main.py` strategy_map
Add entry in `_STRATEGY_MAP` under `layer2`:
```python
"exchange_flow_concentration": ExchangeFlowConcentration,
```

### Step 6: `config/heatmap.yaml`
Add placement:
```yaml
exchange_flow_concentration:
  row: 5
  col: 1
  span_cols: 1
  span_rows: 1
```

### Step 7: `config/strategies.yaml`
Add under `layer2:` section with all 15 params from Section 6.

---

## 8. Grid Layout After Placement

```
Row 1: gamma_wall | magnet | gamma_flip | gamma_squeeze | gex_imbalance | confluence
Row 2: vol_comp | gex_divergence | delta_gamma_sq | delta_vol_exh | obi_af | call_put_flow
Row 3: iv_gex_div | gamma_vol_conv | iv_band | strike_conc | depth_decay | vamp
Row 4: iv_skew | prob_magnet | prob_dist_shift | extrinsic_flow | theta_burn | depth_imbalance
Row 5: exchange_flow ✨ | [free] | [free] | [free] | [free] | [free]
Row 6-8: [all free — reserved for future strategies]
```

**Total strategies: 25**

---

## 9. Risk Notes & Archon Adaptations

1. **VSI threshold lowered:** Synapse proposed 2.5/0.4 → Archon adjusts to 2.0/0.5 for better signal frequency. Gates compensate.

2. **Exchange dominance threshold:** Synapse proposed 40% → Archon adjusts to 15%. 40% is too strict for venues that may only represent 10-20% of total book even when driving flow. The signal is about *venue-specific concentration*, not total book majority.

3. **IEX intent interpretation:** Synapse's Gate B says "IEX intent below threshold = good." Refined: high IEX intent (>0.35) means the book is dominated by passive/IEX liquidity, which is a spoofing risk. Low IEX intent means flow is on aggressive venues = genuine signal.

4. **Cross-venue validation:** Synapse mentions "spike in total_volume on quotes stream." Since we don't have a dedicated volume rolling window per venue, Gate C uses the existing `KEY_VOLUME_5M` as a proxy. This is acceptable — volume confirmation is a general market activity check, not venue-specific.

5. **Data availability risk:** If TradeStation's depth_quotes stream doesn't include `bid_exchanges`/`ask_exchanges` dicts, the strategy will gracefully return no signals (missing data → early return). This is safe.

---

## 10. Validation Plan

After implementation:
1. Check that `vsi_combined_5m`, `vsi_roc_5m`, `iex_intent_5m` appear in rolling_data
2. Verify heatmap cell appears at R5C1
3. Backtest against `LEVEL2_DATA_SAMPLES.jsonl` if exchange data is present
4. Monitor signal frequency — should be rare (1-5 per hour) given strict gates
