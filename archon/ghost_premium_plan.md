# Ghost Premium (TVD-Alpha) — Implementation Plan

## Strategy Overview
**Name:** ghost_premium  
**Layer:** full_data  
**Type:** Volatility Divergence  
**Direction:** Bullish (calls overpriced → mean reversion / gamma squeeze)  
**Synapse ID:** "The Ghost Premium"  

## Core Concept
Detect when `MarketMid > TheoreticalValue` by 60%+ on call options. This "Ghost Premium" signals dealer hedging pressure or speculative mania — price will either mean-revert or trigger a gamma squeeze.

## Files to Create/Modify

### 1. `strategies/rolling_keys.py` — Add rolling key
```python
KEY_PDR_5M = "pdr_5m"              # Premium Divergence Ratio
KEY_PDR_ROC_5M = "pdr_roc_5m"       # PDR rate of change
```
Add to `ALL_KEYS` tuple and `__all__` list.

### 2. `main.py` — Feed PDR into rolling_data
In the `_process_data` loop (where `data.get("type") == "option_update"`), calculate PDR for each option update:
```python
# When processing option_update data:
theoretical_value = data.get("theoretical_value", 0.0)
mid = data.get("mid", 0.0)
if theoretical_value > 0.01:  # avoid divide-by-zero / near-zero
    pdr = (mid - theoretical_value) / theoretical_value
    if "pdr_5m" in self._rolling_data:
        self._rolling_data["pdr_5m"].push(pdr, ts)
```
Also compute PDR ROC (rate of change over 5m window).

### 3. `strategies/full_data/ghost_premium.py` — New strategy file
**Trigger Conditions:**
- `PDR > 0.60` on call options (calls 60%+ overpriced vs theoretical)
- Only evaluates call options (`side == "call"`)

**Hard Gates (ALL must pass):**
- **Gate A:** `ask_size > 2σ` above 5-min rolling avg ask_size — real tradeable event, not stale quote
- **Gate B:** Underlying `net_change_pct` stable OR `iv` rising slower than `mid` — separates IV expansion from price dislocation
- **Gate C:** `volume > 0` — contract is actively trading

**Intensity Classification (for heatmap metadata):**
- Yellow (caution): PDR ≈ 0.60–1.00
- Orange (warning): PDR ≈ 1.00–1.50
- Red (extreme): PDR > 1.50

**Confidence Model (5 components):**
1. PDR magnitude (0.0–0.30) — how extreme the premium is
2. PDR velocity (0.0–0.20) — is the premium growing or shrinking?
3. Ask size conviction (0.0–0.15) — liquidity behind the premium
4. IV alignment (0.0–0.15) — IV not already capturing this move
5. GEX regime alignment (0.0–0.10) — signal direction matches GEX bias

**Output:** Signal with direction=LONG (mean reversion play on overpriced calls)

### 4. `main.py` — Register in config
Add to `config/strategy_config.yaml` under `full_data`:
```yaml
ghost_premium:
  enabled: true
  params:
    min_pdr: 0.60
    min_pdr_data_points: 10
    ask_size_sigma_mult: 2.0
    min_ask_size_sigma: 1.0
    max_net_change_pct: 0.02
    min_confidence: 0.35
    max_confidence: 0.85
    stop_pct: 0.005
    target_risk_mult: 2.0
```

## Data Flow
1. `orb_probe.py` → `optionchain_parsed_*.jsonl` → TradeStationClient
2. Client emits `{"type": "option_update", "mid": ..., "theoretical_value": ..., ...}`
3. `_process_data()` in main.py computes PDR and pushes to `rolling_data["pdr_5m"]`
4. `StrategyEngine.process()` passes rolling_data to `ghost_premium.evaluate()`
5. Strategy evaluates PDR thresholds and produces Signal

## Heatmap Integration
- The heatmap reads strategy signals from `rolling_data` and signal history
- `ghost_premium` will appear in the full_data layer
- Intensity color: Yellow/Orange/Red based on PDR magnitude
- Row/Col: Assigned by heatmap positioning logic (next available full_data slot)

## Validation Checklist (for Synapse)
- [ ] PDR formula: `(mid - theoretical_value) / theoretical_value` ✓ matches Synapse spec
- [ ] Trigger: PDR > 0.60 on calls ✓ matches Synapse spec
- [ ] Gate A: ask_size > 2σ above rolling avg ✓ matches Synapse spec
- [ ] Gate B: underlying net_change_pct stable OR iv rising slower than mid ✓ matches Synapse spec
- [ ] Classification: Yellow/Orange/Red by PDR ranges ✓ matches Synapse spec
- [ ] Direction: Always LONG (bullish — overpriced calls = speculative demand) ✓ matches Synapse spec
