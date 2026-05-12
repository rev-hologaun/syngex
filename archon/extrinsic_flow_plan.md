# Extrinsic Value Flow (EXTRINSIC-ALPHA) — Implementation Plan

## Strategy Overview
**Name:** extrinsic_flow  
**Layer:** full_data  
**Type:** Extrinsic Flow  
**Direction:** Bidirectional (call-heavy = LONG bullish, put-heavy = SHORT bearish)  
**Synapse ID:** "The Premium Pulse"  

## Core Concept
Track `Volume × Extrinsic Value` (the "Premium Conviction") separately for calls and puts. When call-side conviction dominates (RΦ > 3.0), it signals speculative bullish positioning. When put-side dominates (RΦ < 0.3), it signals defensive hedging. Leading indicator of positioning shifts.

## Mathematical Definition
```
Φ_Call = Σ(Volume_i × ExtrinsicValue_i) for all call contracts
Φ_Put  = Σ(Volume_i × ExtrinsicValue_i) for all put contracts
RΦ = Φ_Call / Φ_Put   (Relative Conviction Ratio)
```

**Trigger:**
- LONG (Bullish): RΦ > 3.0 (call-side speculative mania)
- SHORT (Bearish): RΦ < 0.3 (put-side defensive hedging)

## Files to Create/Modify

### 1. `strategies/rolling_keys.py` — Add rolling keys
```python
KEY_PHI_CALL_5M = "phi_call_5m"           # Call-side extrinsic conviction flow
KEY_PHI_PUT_5M = "phi_put_5m"             # Put-side extrinsic conviction flow
KEY_PHI_RATIO_5M = "phi_ratio_5m"         # RΦ = Φ_Call / Φ_Put
KEY_PHI_TOTAL_5M = "phi_total_5m"         # Φ_Call + Φ_Put (total flow)
KEY_PHI_TOTAL_SIGMA_5M = "phi_total_sigma_5m"  # Φ total rolling std
```
Add to `ALL_KEYS` tuple and `__all__` list.

### 2. `main.py` — Add rolling windows + Φ injection

**a) Rolling window initialization** (near line 380, after extrinsic_proxy windows):
```python
KEY_PHI_CALL_5M: RollingWindow(window_type="time", window_size=300),
KEY_PHI_PUT_5M: RollingWindow(window_type="time", window_size=300),
KEY_PHI_RATIO_5M: RollingWindow(window_type="time", window_size=300),
KEY_PHI_TOTAL_5M: RollingWindow(window_type="time", window_size=300),
KEY_PHI_TOTAL_SIGMA_5M: RollingWindow(window_type="time", window_size=300),
```

**b) In the `_process_data` method** — add Φ calculation in the `option_update` block.
This goes where `data.get("type") == "option_update"` is handled (around line 835+). We accumulate Φ per tick since multiple option_update messages arrive per cycle:

```python
# Extrinsic Value Flow — Φ (Premium Conviction)
# Φ = Volume × ExtrinsicValue, tracked per side
# RΦ = Φ_Call / Φ_Put
try:
    if data.get("type") == "option_update":
        side = data.get("side", "")
        extrinsic = data.get("extrinsic_value", 0.0)
        volume = data.get("volume", 0)
        delta = data.get("delta", 0.0)
        
        if extrinsic and extrinsic > 0 and volume and volume > 0:
            # Gate C: Delta purity — only count 25-delta to 45-delta contracts
            abs_delta = abs(delta) if delta else 0.0
            if 0.15 <= abs_delta <= 0.65:  # ~15-65 delta range (broad enough for various strikes)
                phi = volume * extrinsic
                
                if side == "call":
                    self._phi_call_tick += phi
                elif side == "put":
                    self._phi_put_tick += phi
except Exception:
    pass
```

Then in the gex_summary processing block (where rolling windows are pushed), add the tick-to-window commit:
```python
# Commit per-tick Φ accumulators to rolling windows
if self._phi_call_tick > 0 or self._phi_put_tick > 0:
    phi_call_w = self._rolling_data.get(KEY_PHI_CALL_5M)
    if phi_call_w: phi_call_w.push(self._phi_call_tick, ts)
    
    phi_put_w = self._rolling_data.get(KEY_PHI_PUT_5M)
    if phi_put_w: phi_put_w.push(self._phi_put_tick, ts)
    
    total = self._phi_call_tick + self._phi_put_tick
    if total > 0:
        phi_total_w = self._rolling_data.get(KEY_PHI_TOTAL_5M)
        if phi_total_w: phi_total_w.push(total, ts)
        
        phi_ratio_w = self._rolling_data.get(KEY_PHI_RATIO_5M)
        if phi_put_w and self._phi_put_tick > 0:
            ratio = self._phi_call_tick / self._phi_put_tick
            phi_ratio_w.push(ratio, ts)
        
        # Φ total σ
        phi_sig_w = self._rolling_data.get(KEY_PHI_TOTAL_SIGMA_5M)
        if phi_total_w and phi_sig_w and phi_total_w.count >= 5:
            vals = list(phi_total_w.values)
            mean_t = sum(vals) / len(vals)
            var = sum((x - mean_t)**2 for x in vals) / len(vals)
            phi_sig_w.push(math.sqrt(var), ts)
    
    # Reset per-tick accumulators
    self._phi_call_tick = 0.0
    self._phi_put_tick = 0.0
```

**c) Initialize accumulators** in `__init__` or `initialize()`:
```python
self._phi_call_tick = 0.0
self._phi_put_tick = 0.0
```

### 3. `strategies/full_data/extrinsic_flow.py` — New strategy file

```python
"""
strategies/full_data/extrinsic_flow.py — Extrinsic Value Flow (EXTRINSIC-ALPHA)

Tracks Volume × Extrinsic Value (Premium Conviction) separately for calls and puts.
Φ_Call = Σ(Volume × ExtrinsicValue) for calls
Φ_Put  = Σ(Volume × ExtrinsicValue) for puts
RΦ = Φ_Call / Φ_Put (Relative Conviction Ratio)

Call-heavy (RΦ > 3.0) = speculative bullish → LONG
Put-heavy (RΦ < 0.3) = defensive hedging → SHORT
Leading indicator of positioning shifts.

Trigger: RΦ > 3.0 (bullish) or RΦ < 0.3 (bearish)

Hard gates (ALL must pass):
    Gate A: Volume anchor — total Φ > 2σ above 1h rolling avg
    Gate B: Gamma guardrail — bullish in POSITIVE gamma, bearish in NEGATIVE gamma
    Gate C: Delta purity — only count 15-65 delta contracts (already filtered in main.py)

Confidence model (5 components):
    1. RΦ magnitude (0.0–0.30)
    2. Φ total momentum (0.0–0.20)
    3. Volume conviction (0.0–0.15)
    4. Ratio purity (0.0–0.15)
    5. GEX regime alignment (0.0–0.10)
"""
```

Key implementation details:
- `strategy_id = "extrinsic_flow"`
- `layer = "full_data"`
- Default params:
  - `phi_call_threshold = 3.0` — RΦ trigger for bullish
  - `phi_put_threshold = 0.3` — RΦ trigger for bearish
  - `min_phi_data_points = 10`
  - `phi_sigma_mult = 2.0` — Gate A: total Φ > 2σ above avg
  - `min_confidence = 0.35`
  - `max_confidence = 0.85`
  - `stop_pct = 0.005`
  - `target_risk_mult = 2.0`

- **Direction logic:**
  - LONG when RΦ > 3.0 (call-side speculative mania) AND regime == "POSITIVE"
  - SHORT when RΦ < 0.3 (put-side defensive hedging) AND regime == "NEGATIVE"

- **Gate B (GEX Alignment):** Same pattern as skew_dynamics/smile_dynamics
  - LONG only valid when `regime == "POSITIVE"`
  - SHORT only valid when `regime == "NEGATIVE"`

- **Intensity metadata:**
  - Yellow: RΦ trending (moderate deviation from 1.0)
  - Orange: RΦ spiking (approaching 3.0 or 0.3)
  - Red: RΦ at extreme levels (well beyond 3.0 or below 0.3)

### 4. `strategies/full_data/__init__.py` — Add export
```python
from .extrinsic_flow import ExtrinsicFlow
```
Add `ExtrinsicFlow` to `__all__`.

### 5. `config/strategies.yaml` — Add config
Under `full_data:` section:
```yaml
extrinsic_flow:
  enabled: true
  params:
    phi_call_threshold: 3.0
    phi_put_threshold: 0.3
    min_phi_data_points: 10
    phi_sigma_mult: 2.0
    min_confidence: 0.35
    max_confidence: 0.85
    stop_pct: 0.005
    target_risk_mult: 2.0
```

## Data Flow
1. `orb_probe.py` → `optionchain_parsed` → TradeStationClient → `option_update` messages
2. `_process_data()` accumulates `volume × extrinsic_value` per side (filtered by delta 15-65)
3. Per-tick accumulators committed to rolling windows on gex_summary tick
4. `StrategyEngine.process()` passes `data` (including `regime`) to `extrinsic_flow.evaluate()`
5. Strategy evaluates RΦ thresholds + GEX regime alignment → produces Signal

## Heatmap Integration
- Appears in full_data layer
- Bidirectional: LONG (call-heavy) or SHORT (put-heavy)
- Intensity: Yellow/Orange/Red by RΦ extremity
- GEX regime alignment shown in signal metadata

## Gate A — Volume Anchor Detail
- Check `total_Φ > rolling_avg + phi_sigma_mult × rolling_std`
- Ensures we only react to "whale" flow, not small-fry noise

## Gate C — Delta Purity Detail
- Already filtered in main.py (15-65 delta range)
- This prevents deep ITM "substitute" contracts from skewing the signal
- The filter is applied at data ingestion, so the strategy sees clean data

## Validation Checklist (for Synapse)
- [ ] Φ formula: `Volume × ExtrinsicValue` per side ✓
- [ ] RΦ formula: `Φ_Call / Φ_Put` ✓
- [ ] Trigger: RΦ > 3.0 (bullish) or RΦ < 0.3 (bearish) ✓
- [ ] Gate A: Volume anchor (total Φ > 2σ above avg) ✓
- [ ] Gate B: GEX regime alignment (LONG→POSITIVE, SHORT→NEGATIVE) ✓
- [ ] Gate C: Delta purity (15-65 delta range, filtered in main.py) ✓
- [ ] Direction: Bidirectional (call-heavy=LONG, put-heavy=SHORT) ✓
- [ ] Intensity: Yellow/Orange/Red by RΦ extremity ✓
