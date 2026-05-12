# IV Smile Dynamics (CURVE-ALPHA) — Implementation Plan

## Strategy Overview
**Name:** smile_dynamics  
**Layer:** full_data  
**Type:** Volatility Curvature  
**Direction:** Bidirectional (put-side curvature dominant = SHORT, call-side dominant = LONG)  
**Synapse ID:** "The Jaw Breaker"  

## Core Concept
Measure the **Curvature Asymmetry Index Ω** across multiple strikes on both wings of the volatility smile. When the put-side IV slope steepens relative to the call-side, the market is pricing in non-linear tail risk (jaw opening → SHORT). When the smile symmetrically flattens, fear is evaporating (jaw closing → LONG). Leading indicator — curvature shifts often precede price moves.

## Mathematical Definition
```
Slope_Put_Wing = dIV/dK for put-side strikes (moneyness < 1)
Slope_Call_Wing = dIV/dK for call-side strikes (moneyness > 1)
Ω = |Slope_Put_Wing| / |Slope_Call_Wing|
```
- Slope computed via linear regression (least-squares) of IV vs moneyness across 5-7 strikes per wing
- Ω > 1: put-side steeper (fear jaw opening)
- Ω < 1: call-side steeper (euphoria jaw closing)
- Ω ≈ 1: symmetric smile (neutral)

## Files to Create/Modify

### 1. `strategies/rolling_keys.py` — Add rolling keys
```python
KEY_CURVE_OMEGA_5M = "curve_omega_5m"
KEY_CURVE_OMEGA_ROC_5M = "curve_omega_roc_5m"
KEY_CURVE_OMEGA_SIGMA_5M = "curve_omega_sigma_5m"
KEY_PUT_SLOPE_5M = "put_slope_5m"
KEY_CALL_SLOPE_5M = "call_slope_5m"
```
Add to `ALL_KEYS` tuple and `__all__` list.

### 2. `main.py` — Add rolling windows + Ω injection

**a) Rolling window initialization** (after the Ψ windows around line 365):
```python
KEY_CURVE_OMEGA_5M: RollingWindow(window_type="time", window_size=900),
KEY_CURVE_OMEGA_ROC_5M: RollingWindow(window_type="time", window_size=900),
KEY_CURVE_OMEGA_SIGMA_5M: RollingWindow(window_type="time", window_size=900),
KEY_PUT_SLOPE_5M: RollingWindow(window_type="time", window_size=900),
KEY_CALL_SLOPE_5M: RollingWindow(window_type="time", window_size=900),
```

**b) Ω calculation in `_process_data`** — right after the Ψ block (around line 984+):
```python
# IV Smile Dynamics — Ω (Curvature Asymmetry Index)
# Ω = |Slope_Put_Wing| / |Slope_Call_Wing|
# Slope = dIV/dK via least-squares linear regression of IV vs moneyness
try:
    iv_by_strike = self._calculator.get_iv_by_strike_avg()
    if iv_by_strike:
        strikes = sorted(iv_by_strike.keys())
        if len(strikes) >= 6:  # Need enough strikes for slope calc
            atm_strike = min(strikes, key=lambda s: abs(s - underlying_price))
            
            # Split into put/call wings, filter to valid IV data
            put_wing = [(s, iv_by_strike[s]) for s in strikes 
                        if s < atm_strike and iv_by_strike[s] > 0.01]
            call_wing = [(s, iv_by_strike[s]) for s in strikes 
                         if s > atm_strike and iv_by_strike[s] > 0.01]
            
            if len(put_wing) >= 2 and len(call_wing) >= 2:
                # Compute slope via least-squares regression: IV vs moneyness
                put_x = [s / atm_strike for s, iv in put_wing]  # moneyness
                put_y = [iv for s, iv in put_wing]
                put_slope = _compute_linear_slope(put_x, put_y)
                
                call_x = [s / atm_strike for s, iv in call_wing]
                call_y = [iv for s, iv in call_wing]
                call_slope = _compute_linear_slope(call_x, call_y)
                
                if abs(call_slope) > 0.0001:
                    omega = abs(put_slope) / abs(call_slope)
                    
                    # Push to rolling windows
                    omega_w = self._rolling_data.get(KEY_CURVE_OMEGA_5M)
                    if omega_w: omega_w.push(omega, ts)
                    
                    ps_w = self._rolling_data.get(KEY_PUT_SLOPE_5M)
                    if ps_w: ps_w.push(put_slope, ts)
                    
                    cs_w = self._rolling_data.get(KEY_CALL_SLOPE_5M)
                    if cs_w: cs_w.push(call_slope, ts)
                    
                    # Ω ROC
                    omega_roc_w = self._rolling_data.get(KEY_CURVE_OMEGA_ROC_5M)
                    if omega_w and omega_roc_w and omega_w.count >= 2:
                        first_omega = omega_w.values[0]
                        if abs(first_omega) > 0.0001:
                            omega_roc = (omega - first_omega) / abs(first_omega)
                            omega_roc_w.push(omega_roc, ts)
                    
                    # Ω σ
                    omega_sig_w = self._rolling_data.get(KEY_CURVE_OMEGA_SIGMA_5M)
                    if omega_w and omega_sig_w and omega_w.count >= 5:
                        vals = list(omega_w.values)
                        mean_o = sum(vals) / len(vals)
                        var = sum((x - mean_o)**2 for x in vals) / len(vals)
                        omega_sig_w.push(math.sqrt(var), ts)
except Exception:
    pass
```

**c) Helper function** — add as a module-level function before the Orchestrator class or at top of `_process_data`:
```python
def _compute_linear_slope(x_vals, y_vals):
    """Compute slope via least-squares linear regression."""
    n = len(x_vals)
    if n < 2:
        return 0.0
    x_mean = sum(x_vals) / n
    y_mean = sum(y_vals) / n
    num = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
    den = sum((x_vals[i] - x_mean)**2 for i in range(n))
    if den == 0:
        return 0.0
    return num / den
```

### 3. `strategies/full_data/smile_dynamics.py` — New strategy

```python
"""
strategies/full_data/smile_dynamics.py — IV Smile Dynamics (CURVE-ALPHA)

Measures Curvature Asymmetry Index Ω across multiple strikes.
Ω = |Slope_Put_Wing| / |Slope_Call_Wing|
Slope = dIV/dK via least-squares linear regression of IV vs moneyness

Put-side curvature dominant (Ω rising) = fear jaw opening → SHORT
Call-side curvature dominant (Ω falling) = euphoria jaw closing → LONG
Leading indicator: curvature shifts often precede price moves.

Trigger: |Ω change| > 2σ over 15-minute rolling window

Hard gates (ALL must pass):
    Gate A: Liquidity anchor — total OI of wing strikes > 3σ above 1h rolling avg
    Gate B: Gamma guardrail — bullish in POSITIVE gamma, bearish in NEGATIVE gamma
    Gate C: Volatility divergence — shift driven by relative slope, not ATM vol expansion

Confidence model (5 components):
    1. Ω magnitude in σ units (0.0–0.30)
    2. Ω velocity (0.0–0.20)
    3. Liquidity conviction (0.0–0.15)
    4. Slope divergence purity (0.0–0.15)
    5. GEX regime alignment (0.0–0.10)
"""
```

Key details:
- `strategy_id = "smile_dynamics"`, `layer = "full_data"`
- Default params: `min_omega_sigma=2.0`, `min_omega_data_points=10`, `liquidity_oi_threshold=100`, `min_confidence=0.35`, `max_confidence=0.85`, `stop_pct=0.005`, `target_risk_mult=2.0`
- **Direction logic:**
  - LONG when Ω ROC < 0 (call-side dominant / smile flattening) AND regime == "POSITIVE"
  - SHORT when Ω ROC > 0 (put-side dominant / jaw opening) AND regime == "NEGATIVE"
- **Gate B (GEX Alignment):** Same pattern as skew_dynamics — LONG only in POSITIVE, SHORT only in NEGATIVE
- **Intensity metadata:** yellow (≈1σ), orange (≈2σ), red (>3σ)

### 4. `strategies/full_data/__init__.py` — Add export
```python
from .smile_dynamics import SmileDynamics
```
Add `SmileDynamics` to `__all__`.

### 5. `config/strategies.yaml` — Add config
Under `full_data:` section:
```yaml
smile_dynamics:
  enabled: true
  params:
    min_omega_sigma: 2.0
    min_omega_data_points: 10
    min_confidence: 0.35
    max_confidence: 0.85
    stop_pct: 0.005
    target_risk_mult: 2.0
    liquidity_oi_threshold: 100
```

## Data Flow
1. `orb_probe.py` → `optionchain_parsed` → TradeStationClient → `option_update`
2. `_process_data()` computes Ω from per-strike IV data via `get_iv_by_strike_avg()` and pushes to rolling windows
3. `StrategyEngine.process()` passes `data` (including `regime`) to `smile_dynamics.evaluate()`
4. Strategy evaluates Ω σ-thresholds + GEX regime alignment → produces Signal

## Heatmap Integration
- Full_data layer
- Bidirectional: LONG (call-side dominant) or SHORT (put-side dominant)
- Intensity: Yellow/Orange/Red by σ magnitude
- GEX regime alignment in signal metadata

## Validation Checklist (for Synapse)
- [ ] Ω formula: `|Slope_Put_Wing| / |Slope_Call_Wing|` ✓
- [ ] Slope = least-squares regression of IV vs moneyness (dIV/dK) ✓
- [ ] Multi-strike sampling across available strikes ✓
- [ ] Trigger: |Ω change| > 2σ over 15m rolling window ✓
- [ ] Gate A: Liquidity anchor on wing strikes ✓
- [ ] Gate B: GEX regime alignment (LONG→POSITIVE, SHORT→NEGATIVE) ✓
- [ ] Gate C: Volatility divergence (not ATM vol expansion) ✓
- [ ] Direction: Bidirectional (put-dominant=SHORT, call-dominant=LONG) ✓
- [ ] Intensity: Yellow/Orange/Red by σ levels ✓
