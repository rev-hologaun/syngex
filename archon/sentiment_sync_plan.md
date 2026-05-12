# Sentiment Sync (SYNCHRONY-ALPHA) — Implementation Plan

## Strategy Overview
**Name:** sentiment_sync  
**Layer:** full_data  
**Type:** Sentiment Synchronization  
**Direction:** Bidirectional (complacency+buying = LONG, fear+selling = SHORT)  
**Synapse ID:** "The Sentiment Sync"  

## Core Concept
Most strategies fail because they treat options sentiment and equity flow as separate entities. This strategy identifies **synchronized momentum** — when the volatility surface sentiment and the order book aggressive flow move in lockstep. If options are screaming "fear" (steepening skew) AND the equity book shows aggressive selling, that's a high-conviction signal. If they disagree, it's a divergence trap.

## Mathematical Definition
```
Γ_sync = Sign(ΔSkew) × Sign(Aggressor_VSI)

ΔSkew = change in IV skew (rolling window, e.g., 15m)
Aggressor_VSI = (aggressor_bid - aggressor_ask) / (aggressor_bid + aggressor_ask)

Bullish Sync: ΔSkew falling (complacency) AND Aggressor_VSI positive (buying)
Bearish Sync: ΔSkew rising (fear) AND Aggressor_VSI negative (selling)
```

## Files to Create/Modify

### 1. `strategies/rolling_keys.py` — Add rolling keys
```python
KEY_SYNC_CORR_5M = "sync_corr_5m"             # Γ_sync: skew-VSI correlation
KEY_SYNC_SIGMA_5M = "sync_sigma_5m"           # σ for significance threshold
KEY_SKEW_CHANGE_5M = "skew_change_5m"         # ΔSkew: skew rolling change
KEY_VSI_MAGNITUDE_5M = "vsi_magnitude_5m"     # |Aggressor_VSI| magnitude
```
Add to `ALL_KEYS` tuple and `__all__` list.

### 2. `main.py` — Add rolling windows + synchronization engine

**a) Rolling window initialization** (near line 405, after iron_anchor windows):
```python
KEY_SYNC_CORR_5M: RollingWindow(window_type="time", window_size=900),
KEY_SYNC_SIGMA_5M: RollingWindow(window_type="time", window_size=900),
KEY_SKEW_CHANGE_5M: RollingWindow(window_type="time", window_size=900),
KEY_VSI_MAGNITUDE_5M: RollingWindow(window_type="time", window_size=900),
```

**b) In the `_process_data` method** — add synchronization engine.
This goes in the gex_summary processing block (after the iron_anchor block, around line 1300+):

```python
# Sentiment Sync — Γ_sync (Synchronization Engine)
# Γ_sync = Sign(ΔSkew) × Sign(Aggressor_VSI)
# Both must be statistically significant and agree in direction
try:
    # 1. Get skew change over rolling window
    skew_window = self._rolling_data.get(KEY_IV_SKEW_5M)
    if skew_window and skew_window.count >= 10:
        first_skew = skew_window.values[0]
        current_skew = skew_window.values[-1]
        if abs(first_skew) > 0.001:
            skew_change = (current_skew - first_skew) / abs(first_skew)
        else:
            skew_change = current_skew
        
        # 2. Get aggressor VSI from rolling window
        vsi_window = self._rolling_data.get(KEY_AGGRESSOR_VSI_5M)
        if vsi_window and vsi_window.count >= 10:
            current_vsi = vsi_window.values[-1]
        else:
            current_vsi = 0.0
        
        # 3. Compute synchronization: sign agreement
        skew_sign = 1.0 if skew_change > 0 else (-1.0 if skew_change < 0 else 0.0)
        vsi_sign = 1.0 if current_vsi > 0 else (-1.0 if current_vsi < 0 else 0.0)
        
        # Γ_sync: +1 = both positive (fear+selling), -1 = both negative (complacency+buying)
        gamma_sync = skew_sign * vsi_sign
        
        # 4. Compute σ for significance threshold
        skew_vals = list(skew_window.values)
        mean_skew = sum(skew_vals) / len(skew_vals)
        skew_var = sum((x - mean_skew)**2 for x in skew_vals) / len(skew_vals)
        skew_sigma = math.sqrt(skew_var) if skew_var > 0 else 0.001
        
        vsi_vals = list(vsi_window.values)
        mean_vsi = sum(vsi_vals) / len(vsi_vals)
        vsi_var = sum((x - mean_vsi)**2 for x in vsi_vals) / len(vsi_vals)
        vsi_sigma = math.sqrt(vsi_var) if vsi_var > 0 else 0.001
        
        # Push to rolling windows
        corr_w = self._rolling_data.get(KEY_SYNC_CORR_5M)
        if corr_w: corr_w.push(gamma_sync, ts)
        
        sig_w = self._rolling_data.get(KEY_SYNC_SIGMA_5M)
        if sig_w: sig_w.push(max(skew_sigma, vsi_sigma), ts)
        
        skew_chg_w = self._rolling_data.get(KEY_SKEW_CHANGE_5M)
        if skew_chg_w: skew_chg_w.push(skew_change, ts)
        
        vsi_mag_w = self._rolling_data.get(KEY_VSI_MAGNITUDE_5M)
        if vsi_mag_w: vsi_mag_w.push(abs(current_vsi), ts)
except Exception:
    pass
```

### 3. `strategies/full_data/sentiment_sync.py` — New strategy file

```python
"""
strategies/full_data/sentiment_sync.py — Sentiment Sync (SYNCHRONY-ALPHA)

Detects when options sentiment (IV skew) and equity flow (Aggressor VSI)
move in lockstep. Γ_sync = Sign(ΔSkew) × Sign(Aggressor_VSI)

Bullish Sync: ΔSkew falling (complacency) AND VSI positive (buying) → LONG
Bearish Sync: ΔSkew rising (fear) AND VSI negative (selling) → SHORT
Filters out false signals where options positioning doesn't translate to stock flow.

Trigger: |ΔSkew| > 2σ AND |VSI| > 2σ AND signs agree

Hard gates (ALL must pass):
    Gate A: Magnitude gate — both skew change and VSI > 2σ over rolling window
    Gate B: Volume anchor — total volume above rolling average
    Gate C: Price confirmation — price moving in direction of sync

Confidence model (5 components):
    1. Skew significance (0.0–0.25) — ΔSkew in σ units
    2. VSI significance (0.0–0.25) — Aggressor VSI in σ units
    3. Sign agreement (0.0–0.15) — how cleanly both signals agree
    4. Volume confirmation (0.0–0.10) — volume above average
    5. Price confirmation (0.0–0.10) — price moving in sync direction
    6. GEX regime alignment (0.0–0.10) — signal direction matches GEX bias
"""
```

Key implementation details:
- `strategy_id = "sentiment_sync"`, `layer = "full_data"`
- Default params:
  - `min_sig_sigma = 2.0` — Gate A: both skew and VSI > 2σ
  - `min_data_points = 10` — need data for rolling stats
  - `volume_min_mult = 1.0` — Gate B: volume ≥ avg
  - `price_confirm_pct = 0.001` — Gate C: price moved ≥ 0.1% in sync direction
  - `min_confidence = 0.35`
  - `max_confidence = 0.85`
  - `stop_pct = 0.005`
  - `target_risk_mult = 2.0`

- **Direction logic:**
  - LONG when ΔSkew < 0 (falling/complacency) AND VSI > 0 (buying) AND regime == "POSITIVE"
  - SHORT when ΔSkew > 0 (rising/fear) AND VSI < 0 (selling) AND regime == "NEGATIVE"

- **Gate B (GEX Alignment):** Same pattern as other full_data strategies
  - LONG only valid when `regime == "POSITIVE"`
  - SHORT only valid when `regime == "NEGATIVE"`

- **Intensity metadata:**
  - Yellow: Both signals trending same direction (1σ)
  - Orange: Both signals significant (2σ)
  - Red: Both signals extreme (3σ+)

### 4. `strategies/full_data/__init__.py` — Add export
```python
from .sentiment_sync import SentimentSync
```
Add `SentimentSync` to `__all__`.

### 5. `config/strategies.yaml` — Add config
Under `full_data:` section:
```yaml
sentiment_sync:
  enabled: true
  params:
    min_sig_sigma: 2.0
    min_data_points: 10
    volume_min_mult: 1.0
    price_confirm_pct: 0.001
    min_confidence: 0.35
    max_confidence: 0.85
    stop_pct: 0.005
    target_risk_mult: 2.0
```

## Data Flow
1. `orb_probe.py` → `quotes_parsed` + `optionchain_parsed` → TradeStationClient
2. IV skew already computed in `_process_data` → `KEY_IV_SKEW_5M`
3. Aggressor VSI already computed in `_process_data` → `KEY_AGGRESSOR_VSI_5M`
4. Sync engine computes Γ_sync from these two rolling windows
5. `StrategyEngine.process()` passes `data` (including `regime`) to `sentiment_sync.evaluate()`
6. Strategy evaluates significance thresholds + price confirmation → produces Signal

## Heatmap Integration
- Appears in full_data layer
- Bidirectional: LONG (complacency+buying) or SHORT (fear+selling)
- Intensity: Yellow/Orange/Red by σ significance level
- GEX regime alignment shown in signal metadata

## Gate A — Magnitude Gate Detail
- Check `abs(skew_change) > min_sig_sigma × skew_sigma` AND `abs(current_vsi) > min_sig_sigma × vsi_sigma`
- Both must be statistically significant — no "soft" sentiment

## Gate B — Volume Anchor Detail
- Check `volume_5m.latest >= volume_5m.mean × volume_min_mult`
- Ensures the flow is backed by meaningful volume

## Gate C — Price Confirmation Detail
- Check `price has moved ≥ price_confirm_pct in sync direction`
- If Γ_sync is bullish but price is dropping → divergence trap, stay out
- Uses `KEY_PRICE_5M` rolling window to compute recent price movement

## Validation Checklist (for Synapse)
- [ ] Γ_sync formula: `Sign(ΔSkew) × Sign(Aggressor_VSI)` ✓
- [ ] Both skew and VSI already tracked in rolling windows ✓
- [ ] Trigger: |ΔSkew| > 2σ AND |VSI| > 2σ AND signs agree ✓
- [ ] Gate A: Magnitude gate (both > 2σ) ✓
- [ ] Gate B: Volume anchor (volume ≥ avg) ✓
- [ ] Gate C: Price confirmation (price moving in sync direction) ✓
- [ ] Direction: Bidirectional (complacency+buying=LONG, fear+selling=SHORT) ✓
- [ ] Intensity: Yellow/Orange/Red by σ significance ✓
