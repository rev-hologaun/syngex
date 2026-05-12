# IV Skew Dynamics (SKEW-ALPHA) — Implementation Plan

## Strategy Overview
**Name:** skew_dynamics  
**Layer:** full_data  
**Type:** Volatility Skew  
**Direction:** Bidirectional (steepening = SHORT, flattening = LONG)  
**Synapse ID:** "The Smile Weaver"  

## Core Concept
Track the "volatility smile" shape via the Skewness Coefficient Ψ. When the market pays more for OTM put protection than OTM call upside, fear is rising (steepening skew → SHORT). When the gap narrows, complacency returns (flattening skew → LONG). Best when aligned with GEX regime.

## Mathematical Definition
```
Ψ (Skewness Coefficient) = (IV_Put_Wing - IV_Call_Wing) / IV_ATM
```
- Put Wing = IV of ~25-delta OTM put
- Call Wing = IV of ~25-delta OTM call
- IV_ATM = IV of at-the-money option

## Files to Create/Modify

### 1. `strategies/rolling_keys.py` — Add rolling keys
```python
KEY_SKEW_PSI_5M = "skew_psi_5m"          # Skewness Coefficient Ψ
KEY_SKEW_PSI_ROC_5M = "skew_psi_roc_5m"   # Ψ rate of change
KEY_SKEW_PSI_SIGMA_5M = "skew_psi_sigma_5m"  # Ψ rolling std (for σ-based triggers)
```
Add to `ALL_KEYS` tuple and `__all__` list.

### 2. `main.py` — Feed Ψ into rolling_data

**a) Rolling window initialization** (near line 354-368, alongside other skew windows):
```python
KEY_SKEW_PSI_5M: RollingWindow(window_type="time", window_size=900),  # 15m window
KEY_SKEW_PSI_ROC_5M: RollingWindow(window_type="time", window_size=900),
KEY_SKEW_PSI_SIGMA_5M: RollingWindow(window_type="time", window_size=900),
```

**b) In the `_process_data` method** — compute Ψ from option chain data.
The key insight: Ψ needs specific delta wings, not just averages. We compute it per-strike from the option chain data already flowing through `option_update` messages.

In the section where `gex_summary` is processed (around line 904), add Ψ computation using per-strike IV data from the GEXCalculator:

```python
# IV Skew Dynamics — Ψ (Skewness Coefficient)
# Ψ = (IV_Put_Wing - IV_Call_Wing) / IV_ATM
# Use per-strike IV data from the calculator
try:
    iv_by_strike = self._calculator.get_iv_by_strike_avg()
    if iv_by_strike:
        # Find ATM, ~25d ITM call wing, ~25d OTM put wing
        strikes = sorted(iv_by_strike.keys())
        if len(strikes) >= 3:
            # ATM = closest to current underlying price
            atm_strike = min(strikes, key=lambda s: abs(s - underlying_price))
            atm_iv = iv_by_strike[atm_strike]
            
            # Find call wing (higher strikes = calls) and put wing (lower strikes = puts)
            call_ivs = [iv_by_strike[s] for s in strikes if s > atm_strike]
            put_ivs = [iv_by_strike[s] for s in strikes if s < atm_strike]
            
            if call_ivs and put_ivs and atm_iv > 0:
                # Use outermost available as wing proxy
                call_wing_iv = max(call_ivs)  # furthest OTM call
                put_wing_iv = min(put_ivs)    # furthest OTM put
                
                # Normalize: wings should be roughly equal delta distance
                # Use the one closer to 25-delta equivalent
                if call_ivs and put_ivs:
                    # Take the average of outer 25% of each wing
                    n_calls = max(1, len(call_ivs) // 4)
                    n_puts = max(1, len(put_ivs) // 4)
                    call_wing_iv = sum(sorted(call_ivs, reverse=True)[:n_calls]) / n_calls
                    put_wing_iv = sum(sorted(put_ivs)[:n_puts]) / n_puts
                    
                    psi = (put_wing_iv - call_wing_iv) / atm_iv
                    
                    psi_window = self._rolling_data.get(KEY_SKEW_PSI_5M)
                    if psi_window:
                        psi_window.push(psi, ts)
                    
                    # Ψ ROC: change over 15m window
                    psi_roc_window = self._rolling_data.get(KEY_SKEW_PSI_ROC_5M)
                    if psi_window and psi_roc_window and psi_window.count >= 2:
                        first_psi = psi_window.values[0]
                        if abs(first_psi) > 0.0001:
                            psi_roc = (psi - first_psi) / abs(first_psi)
                            psi_roc_window.push(psi_roc, ts)
                    
                    # Ψ σ for trigger thresholds
                    psi_sigma_window = self._rolling_data.get(KEY_SKEW_PSI_SIGMA_5M)
                    if psi_window and psi_sigma_window and psi_window.count >= 5:
                        vals = list(psi_window.values)
                        mean_psi = sum(vals) / len(vals)
                        var = sum((x - mean_psi) ** 2 for x in vals) / len(vals)
                        std_psi = math.sqrt(var)
                        psi_sigma_window.push(std_psi, ts)
except Exception:
    pass
```

### 3. `strategies/full_data/skew_dynamics.py` — New strategy file

```python
"""
strategies/full_data/skew_dynamics.py — IV Skew Dynamics (SKEW-ALPHA)

Tracks how the volatility smile changes over time via the Skewness Coefficient Ψ.
Ψ = (IV_Put_Wing - IV_Call_Wing) / IV_ATM

Steepening skew (Ψ rising) = rising fear → SHORT
Flattening skew (Ψ falling) = complacency → LONG
Best when aligned with GEX regime.

Trigger: |Ψ change| > 2σ over 15-minute rolling window

Hard gates (ALL must pass):
    Gate A: Liquidity check — combined OI + volume of wing strikes above rolling 1h threshold
    Gate B: GEX regime alignment — bullish in POSITIVE gamma, bearish in NEGATIVE gamma
    Gate C: IV divergence — signal driven by relative IV change, not just ATM vol spike

Confidence model (5 components):
    1. Ψ magnitude in σ units (0.0–0.30)
    2. Ψ velocity (0.0–0.20)
    3. Liquidity conviction (0.0–0.15)
    4. IV divergence purity (0.0–0.15)
    5. GEX regime alignment (0.0–0.10)
"""
```

Key implementation details:
- `strategy_id = "skew_dynamics"`
- `layer = "full_data"`
- Default params:
  - `min_psi_sigma = 2.0` — trigger at 2σ
  - `min_psi_data_points = 10` — need data for rolling stats
  - `min_confidence = 0.35`
  - `max_confidence = 0.85`
  - `stop_pct = 0.005`
  - `target_risk_mult = 2.0`
  - `liquidity_oi_threshold = 100` — min open interest for wings

- **Direction logic:**
  - LONG when Ψ is falling (flattening skew = complacency) — and GEX regime is POSITIVE
  - SHORT when Ψ is rising (steepening skew = fear) — and GEX regime is NEGATIVE

- **Gate B (GEX Alignment)** — critical differentiator from ghost_premium:
  - Get `regime = data.get("regime", "")` from the data dict (already passed by orchestrator)
  - LONG signal only valid when `regime == "POSITIVE"` (supports upward drift)
  - SHORT signal only valid when `regime == "NEGATIVE"` (accelerates downward)

- **Intensity metadata:**
  - Yellow: |Ψ change| ≈ 1σ
  - Orange: |Ψ change| ≈ 2σ
  - Red: |Ψ change| > 3σ

- **Signal format:** Direction = LONG or SHORT with underlying_price as entry

### 4. `strategies/full_data/__init__.py` — Add export
```python
from .skew_dynamics import SkewDynamics
```
Add `SkewDynamics` to `__all__`.

### 5. `config/strategies.yaml` — Add config
Under `full_data:` section:
```yaml
skew_dynamics:
  enabled: true
  params:
    min_psi_sigma: 2.0
    min_psi_data_points: 10
    min_confidence: 0.35
    max_confidence: 0.85
    stop_pct: 0.005
    target_risk_mult: 2.0
    liquidity_oi_threshold: 100
```

## Data Flow
1. `orb_probe.py` → `optionchain_parsed` → TradeStationClient → `option_update` messages
2. `_process_data()` in main.py computes Ψ from per-strike IV data and pushes to rolling windows
3. `StrategyEngine.process()` passes `data` (including `regime`) to `skew_dynamics.evaluate()`
4. Strategy evaluates Ψ σ-thresholds and GEX regime alignment → produces Signal

## Heatmap Integration
- Appears in full_data layer
- Bidirectional: LONG (flattening/complacency) or SHORT (steepening/fear)
- Intensity: Yellow/Orange/Red by σ magnitude
- GEX regime alignment shown in signal metadata

## Gate C — IV Divergence Detail
To ensure the signal is driven by relative wing IV changes (not just ATM vol expansion):
- Check that ATM IV change over 5m is below a threshold (e.g., < 5% change)
- OR check that the wing IV spread change dominates the ATM IV change
- This separates "skew shift" from "general vol expansion"

## Validation Checklist (for Synapse)
- [ ] Ψ formula: `(IV_Put_Wing - IV_Call_Wing) / IV_ATM` ✓ matches Synapse spec
- [ ] Trigger: |Ψ change| > 2σ over 15m rolling window ✓ matches Synapse spec
- [ ] Gate A: Liquidity check on wing strikes ✓ matches Synapse spec
- [ ] Gate B: GEX regime alignment (LONG in POSITIVE, SHORT in NEGATIVE) ✓ matches Synapse spec
- [ ] Gate C: IV divergence (not ATM vol spike) ✓ matches Synapse spec
- [ ] Direction: Bidirectional (steepening=SHORT, flattening=LONG) ✓ matches Synapse spec
- [ ] Intensity: Yellow/Orange/Red by σ levels ✓ matches Synapse spec
