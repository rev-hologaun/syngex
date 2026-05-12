# Whale Tracker (CONCENTRATION-ALPHA) — Implementation Plan

## Strategy Overview
**Name:** whale_tracker  
**Layer:** full_data  
**Type:** Concentration Spike  
**Direction:** Bidirectional (bid concentration = LONG, ask concentration = SHORT)  
**Synapse ID:** "The Whale Tracker"  

## Core Concept
Detect institutional "whale" orders in the order book by analyzing the size concentration ratio at individual price levels. Retail orders are granular (many small orders); institutional orders are lumpy (few massive orders with low participant count). We're looking for `biggest_size / smallest_size` spikes where `num_participants` is very low (1-2).

## Mathematical Definition
```
Ω_conc = biggest_size / smallest_size at a given price level

Trigger:
- Bullish: Ω_conc > 5σ above rolling avg AND num_participants ≤ 2 AND price near support
- Bearish: Ω_conc > 5σ above rolling avg AND num_participants ≤ 2 AND price near resistance
```

## Files to Create/Modify

### 1. `strategies/rolling_keys.py` — Add rolling keys
```python
KEY_BIGGEST_SIZE_5M = "biggest_size_5m"          # Max order size at best levels
KEY_SMALLEST_SIZE_5M = "smallest_size_5m"        # Min order size at best levels
KEY_CONCENTRATION_RATIO_5M = "conc_ratio_5m"     # Ω_conc = biggest/smallest
KEY_CONCENTRATION_SIGMA_5M = "conc_sigma_5m"     # Ω_conc rolling σ
KEY_NUM_PARTICIPANTS_5M = "num_participants_5m"  # Participant count at best levels
```
Add to `ALL_KEYS` tuple and `__all__` list.

### 2. `main.py` — Add rolling windows + concentration engine

**a) Rolling window initialization** (near line 420, after sentiment_sync windows):
```python
KEY_BIGGEST_SIZE_5M: RollingWindow(window_type="time", window_size=900),
KEY_SMALLEST_SIZE_5M: RollingWindow(window_type="time", window_size=900),
KEY_CONCENTRATION_RATIO_5M: RollingWindow(window_type="time", window_size=900),
KEY_CONCENTRATION_SIGMA_5M: RollingWindow(window_type="time", window_size=900),
KEY_NUM_PARTICIPANTS_5M: RollingWindow(window_type="time", window_size=900),
```

**b) In the `_process_data` method** — add concentration engine.
This goes in the `market_depth_agg` processing block (after the VAMP computation, around line 2180+):

```python
# Whale Tracker — Concentration Ratio Engine
# Ω_conc = biggest_size / smallest_size at best levels
try:
    if msg_type == "market_depth_agg" and bids and asks:
        # Extract per-level stats from depth aggregates
        # bids/asks contain dicts with Price, TotalSize, NumParticipants
        
        # Get best 5 bid levels and best 5 ask levels
        top_bids = bids[:5] if len(bids) >= 5 else bids
        top_asks = asks[:5] if len(asks) >= 5 else asks
        
        if top_bids and top_asks:
            # Bid side: find biggest and smallest sizes
            bid_sizes = [int(b.get("TotalSize", 0)) for b in top_bids if int(b.get("TotalSize", 0)) > 0]
            bid_participants = [int(b.get("NumParticipants", 0)) for b in top_bids]
            
            ask_sizes = [int(a.get("TotalSize", 0)) for a in top_asks if int(a.get("TotalSize", 0)) > 0]
            ask_participants = [int(a.get("NumParticipants", 0)) for a in top_asks]
            
            if bid_sizes and ask_sizes:
                # Compute concentration ratios
                bid_biggest = max(bid_sizes)
                bid_smallest = min(bid_sizes)
                bid_conc_ratio = bid_biggest / bid_smallest if bid_smallest > 0 else 0.0
                
                ask_biggest = max(ask_sizes)
                ask_smallest = min(ask_sizes)
                ask_conc_ratio = ask_biggest / ask_smallest if ask_smallest > 0 else 0.0
                
                # Use the side with higher concentration
                best_conc_ratio = max(bid_conc_ratio, ask_conc_ratio)
                best_side = "bid" if bid_conc_ratio > ask_conc_ratio else "ask"
                best_participants = (
                    min(bid_participants) if best_side == "bid" else min(ask_participants)
                )
                
                # Push to rolling windows
                big_w = self._rolling_data.get(KEY_BIGGEST_SIZE_5M)
                if big_w: big_w.push(max(bid_biggest, ask_biggest), ts)
                
                small_w = self._rolling_data.get(KEY_SMALLEST_SIZE_5M)
                if small_w: small_w.push(min(bid_smallest, ask_smallest), ts)
                
                conc_w = self._rolling_data.get(KEY_CONCENTRATION_RATIO_5M)
                if conc_w: conc_w.push(best_conc_ratio, ts)
                
                # Concentration σ
                conc_sig_w = self._rolling_data.get(KEY_CONCENTRATION_SIGMA_5M)
                if conc_w and conc_sig_w and conc_w.count >= 5:
                    vals = list(conc_w.values)
                    mean_c = sum(vals) / len(vals)
                    var = sum((x - mean_c)**2 for x in vals) / len(vals)
                    conc_sig_w.push(math.sqrt(var), ts)
                
                parts_w = self._rolling_data.get(KEY_NUM_PARTICIPANTS_5M)
                if parts_w: parts_w.push(best_participants, ts)
except Exception:
    pass
```

### 3. `strategies/full_data/whale_tracker.py` — New strategy file

```python
"""
strategies/full_data/whale_tracker.py — Whale Tracker (CONCENTRATION-ALPHA)

Detects institutional "whale" orders by analyzing size concentration ratio.
Ω_conc = biggest_size / smallest_size at best price levels.

Bullish: Ω_conc > 5σ AND num_participants ≤ 2 AND bid-side concentration → LONG
Bearish: Ω_conc > 5σ AND num_participants ≤ 2 AND ask-side concentration → SHORT
Filters out retail "noise" by requiring low participant count at large orders.

Trigger: Concentration ratio > 5σ above rolling avg AND num_participants ≤ 2

Hard gates (ALL must pass):
    Gate A: Whale threshold — biggest_size > 5σ above rolling avg
    Gate B: Single-entity filter — num_participants ≤ 2 at concentrated level
    Gate C: Gamma coincidence — concentration near gamma wall (optional, highest conviction)

Confidence model (5 components):
    1. Concentration magnitude (0.0–0.30) — Ω_conc in σ units
    2. Participant conviction (0.0–0.20) — low participant count = high conviction
    3. Size anomaly (0.0–0.15) — biggest_size > 3σ above avg
    4. Gamma coincidence (0.0–0.10) — concentration near gamma wall
    5. GEX regime alignment (0.0–0.10) — signal direction matches GEX bias
"""
```

Key implementation details:
- `strategy_id = "whale_tracker"`, `layer = "full_data"`
- Default params:
  - `min_conc_sigma = 5.0` — Gate A: concentration > 5σ above avg
  - `max_participants = 2` — Gate B: num_participants ≤ 2
  - `min_biggest_size_sigma = 3.0` — Gate C: biggest_size > 3σ above avg
  - `min_confidence = 0.35`
  - `max_confidence = 0.85`
  - `stop_pct = 0.005`
  - `target_risk_mult = 2.0`

- **Direction logic:**
  - LONG when bid-side concentration > 5σ AND num_participants ≤ 2 AND regime == "POSITIVE"
  - SHORT when ask-side concentration > 5σ AND num_participants ≤ 2 AND regime == "NEGATIVE"

- **Gate B (GEX Alignment):** Same pattern as other full_data strategies
  - LONG only valid when `regime == "POSITIVE"`
  - SHORT only valid when `regime == "NEGATIVE"`

- **Intensity metadata:**
  - Yellow: High concentration (3-5σ)
  - Orange: Whale concentration (5-10σ)
  - Red: Extreme concentration (>10σ) + near gamma wall

### 4. `strategies/full_data/__init__.py` — Add export
```python
from .whale_tracker import WhaleTracker
```
Add `WhaleTracker` to `__all__`.

### 5. `config/strategies.yaml` — Add config
Under `full_data:` section:
```yaml
whale_tracker:
  enabled: true
  params:
    min_conc_sigma: 5.0
    max_participants: 2
    min_biggest_size_sigma: 3.0
    min_confidence: 0.35
    max_confidence: 0.85
    stop_pct: 0.005
    target_risk_mult: 2.0
```

## Data Flow
1. `orb_probe.py` → `depthagg_parsed` → TradeStationClient → depth aggregate messages
2. `_process_data()` extracts `biggest_size`, `smallest_size`, `num_participants` from depth levels
3. Computes concentration ratio Ω_conc and pushes to rolling windows
4. `StrategyEngine.process()` passes `data` (including `regime`) to `whale_tracker.evaluate()`
5. Strategy evaluates concentration thresholds + participant count + GEX regime → produces Signal

## Heatmap Integration
- Appears in full_data layer
- Bidirectional: LONG (bid concentration) or SHORT (ask concentration)
- Intensity: Yellow/Orange/Red by concentration magnitude and proximity to gamma wall
- GEX regime alignment shown in signal metadata

## Gate A — Whale Threshold Detail
- Check `concentration_ratio > rolling_avg + min_conc_sigma × rolling_std`
- Ensures we only react to statistically anomalous concentration, not normal book noise

## Gate B — Single-Entity Filter Detail
- Check `num_participants ≤ max_participants` (default 2)
- Ensures large orders are from single entities (institutions), not clusters of retail orders

## Gate C — Gamma Coincidence Detail (Optional)
- Check if concentrated price level is within $1.00 of a gamma wall
- If yes, boosts confidence (the "Iron Anchor" effect)
- Uses `self._calculator.get_gamma_walls()` to find nearby walls

## Validation Checklist (for Synapse)
- [ ] Ω_conc formula: `biggest_size / smallest_size` ✓
- [ ] Concentration detection from depth aggregate levels ✓
- [ ] Trigger: Ω_conc > 5σ AND num_participants ≤ 2 ✓
- [ ] Gate A: Whale threshold (concentration > 5σ) ✓
- [ ] Gate B: Single-entity filter (participants ≤ 2) ✓
- [ ] Gate C: Gamma coincidence (near gamma wall) ✓
- [ ] Direction: Bidirectional (bid-concentration=LONG, ask-concentration=SHORT) ✓
- [ ] Intensity: Yellow/Orange/Red by concentration magnitude ✓
