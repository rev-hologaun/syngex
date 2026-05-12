# Gamma-Weighted Momentum (GAMMA-ALPHA) — Implementation Plan

## Strategy Overview
**Name:** gamma_breaker  
**Layer:** full_data  
**Type:** Gamma Breakout  
**Direction:** Bidirectional (break above wall = LONG, break below wall = SHORT)  
**Synapse ID:** "The Gamma Breaker"  

## Core Concept
Detect when price breaks through a major Gamma Wall with dealer hedging acceleration. A Gamma Wall breakout creates a self-reinforcing feedback loop — dealers must buy/sell to stay delta-neutral, fueling the move. We're not just watching price break a level; we're watching price break a level while dealer hedging accelerates.

## Mathematical Definition
```
Gamma Breakout Index (Γ_break) = Price_Velocity × Gamma_Concentration_at_Level

Price_Velocity = |net_change_pct| over 5m window
Gamma_Concentration_at_Level = |GEX| at the nearest wall / avg GEX across all walls

Trigger:
- Bullish: Price > nearest call wall (above) AND Price_Velocity accelerating AND Γ_break > threshold
- Bearish: Price < nearest put wall (below) AND Price_Velocity accelerating AND Γ_break > threshold
```

## Files to Create/Modify

### 1. `strategies/rolling_keys.py` — Add rolling keys
```python
KEY_WALL_DISTANCE_5M = "wall_distance_5m"       # Distance to nearest wall (pct)
KEY_WALL_GEX_5M = "wall_gex_5m"                 # GEX at nearest wall
KEY_WALL_GEX_SIGMA_5M = "wall_gex_sigma_5m"     # Wall GEX rolling std
KEY_PRICE_VELOCITY_5M = "price_velocity_5m"     # |net_change_pct| over 5m
KEY_GAMMA_BREAK_INDEX_5M = "gamma_break_5m"     # Γ_break = velocity × concentration
```
Add to `ALL_KEYS` tuple and `__all__` list.

### 2. `main.py` — Add rolling windows + Γ injection

**a) Rolling window initialization** (near line 390, after phi windows):
```python
KEY_WALL_DISTANCE_5M: RollingWindow(window_type="time", window_size=300),
KEY_WALL_GEX_5M: RollingWindow(window_type="time", window_size=300),
KEY_WALL_GEX_SIGMA_5M: RollingWindow(window_type="time", window_size=300),
KEY_PRICE_VELOCITY_5M: RollingWindow(window_type="time", window_size=300),
KEY_GAMMA_BREAK_INDEX_5M: RollingWindow(window_type="time", window_size=300),
```

**b) In the `_process_data` method** — add Γ_break calculation.
This goes in the gex_summary processing block (after the phi commit block, around line 1160+):

```python
# Gamma Breaker — Γ_break (Gamma Breakout Index)
# Γ_break = Price_Velocity × Gamma_Concentration_at_Level
try:
    price = self._calculator.underlying_price
    if price > 0:
        # 1. Get nearest gamma walls
        walls = self._calculator.get_gamma_walls(threshold=100000)
        
        if walls:
            nearest_wall = walls[0]  # Largest GEX wall
            wall_strike = nearest_wall["strike"]
            wall_gex = nearest_wall["gex"]
            wall_side = nearest_wall["side"]
            
            # Distance to wall as % of price
            wall_dist_pct = abs(wall_strike - price) / price
            
            # Gamma concentration: wall GEX / average GEX across all walls
            all_gex = [abs(w["gex"]) for w in walls]
            avg_gex = sum(all_gex) / len(all_gex) if all_gex else 1.0
            gamma_concentration = abs(wall_gex) / avg_gex if avg_gex > 0 else 1.0
            
            # Price velocity: |net_change_pct| over 5m
            price_window = self._rolling_data.get(KEY_PRICE_5M)
            if price_window and price_window.count >= 2:
                velocity = abs(price_window.values[-1] - price_window.values[0]) / abs(price_window.values[0]) if price_window.values[0] != 0 else 0.0
            else:
                velocity = 0.0
            
            # Γ_break = velocity × gamma_concentration
            gamma_break = velocity * gamma_concentration
            
            # Push to rolling windows
            dist_w = self._rolling_data.get(KEY_WALL_DISTANCE_5M)
            if dist_w: dist_w.push(wall_dist_pct, ts)
            
            gex_w = self._rolling_data.get(KEY_WALL_GEX_5M)
            if gex_w: gex_w.push(abs(wall_gex), ts)
            
            # Wall GEX σ
            gex_sig_w = self._rolling_data.get(KEY_WALL_GEX_SIGMA_5M)
            if gex_w and gex_sig_w and gex_w.count >= 5:
                vals = list(gex_w.values)
                mean_g = sum(vals) / len(vals)
                var = sum((x - mean_g)**2 for x in vals) / len(vals)
                gex_sig_w.push(math.sqrt(var), ts)
            
            vel_w = self._rolling_data.get(KEY_PRICE_VELOCITY_5M)
            if vel_w: vel_w.push(velocity, ts)
            
            gb_w = self._rolling_data.get(KEY_GAMMA_BREAK_INDEX_5M)
            if gb_w: gb_w.push(gamma_break, ts)
except Exception:
    pass
```

### 3. `strategies/full_data/gamma_breaker.py` — New strategy file

```python
"""
strategies/full_data/gamma_breaker.py — Gamma-Weighted Momentum (GAMMA-ALPHA)

Detects when price breaks through a major Gamma Wall with dealer hedging acceleration.
Γ_break = Price_Velocity × Gamma_Concentration_at_Level

Bullish Breakout: Price > nearest call wall + velocity accelerating → LONG
Bearish Breakout: Price < nearest put wall + velocity accelerating → SHORT
Leading indicator: dealer hedging creates self-reinforcing feedback loop.

Trigger: Γ_break > threshold AND price has crossed wall

Hard gates (ALL must pass):
    Gate A: Wall strength — wall GEX > 2σ above rolling avg (major wall)
    Gate B: Regime alignment — bullish in POSITIVE gamma, bearish in NEGATIVE gamma
    Gate C: Volume confirmation — breakout accompanied by volume spike

Confidence model (5 components):
    1. Γ_break magnitude (0.0–0.30)
    2. Wall proximity (0.0–0.20)
    3. Wall strength (0.0–0.15)
    4. Volume confirmation (0.0–0.15)
    5. GEX regime alignment (0.0–0.10)
"""
```

Key implementation details:
- `strategy_id = "gamma_breaker"`, `layer = "full_data"`
- Default params:
  - `min_gamma_break = 0.0005` — Γ_break threshold (adjust based on data)
  - `min_wall_gex_sigma = 2.0` — Gate A: wall GEX > 2σ above avg
  - `min_wall_distance_pct = 0.005` — Price must be within 0.5% of wall to be "at" the wall
  - `volume_spike_mult = 1.5` — Gate C: volume > 1.5× avg
  - `min_confidence = 0.35`
  - `max_confidence = 0.85`
  - `stop_pct = 0.005`
  - `target_risk_mult = 2.0`

- **Direction logic:**
  - LONG when price > nearest wall strike (above) AND velocity accelerating AND regime == "POSITIVE"
  - SHORT when price < nearest wall strike (below) AND velocity accelerating AND regime == "NEGATIVE"
  - The wall direction is determined by `wall_side` (call wall = bullish breakout, put wall = bearish breakout)

- **Gate B (GEX Alignment):** Same pattern as other full_data strategies
  - LONG only valid when `regime == "POSITIVE"`
  - SHORT only valid when `regime == "NEGATIVE"`

- **Intensity metadata:**
  - Yellow: Price approaching wall (within 0.1%)
  - Orange: Price has crossed wall, Γ_break detected
  - Red: Price rapidly moving away, dealer hedging in "panic mode"

### 4. `strategies/full_data/__init__.py` — Add export
```python
from .gamma_breaker import GammaBreaker
```
Add `GammaBreaker` to `__all__`.

### 5. `config/strategies.yaml` — Add config
Under `full_data:` section:
```yaml
gamma_breaker:
  enabled: true
  params:
    min_gamma_break: 0.0005
    min_wall_gex_sigma: 2.0
    min_wall_distance_pct: 0.005
    volume_spike_mult: 1.5
    min_confidence: 0.35
    max_confidence: 0.85
    stop_pct: 0.005
    target_risk_mult: 2.0
```

## Data Flow
1. `orb_probe.py` → `quotes_parsed` → TradeStationClient → `quote_update` messages
2. `_process_data()` computes Γ_break from `get_gamma_walls()` + price velocity and pushes to rolling windows
3. `StrategyEngine.process()` passes `data` (including `regime`) to `gamma_breaker.evaluate()`
4. Strategy evaluates Γ_break thresholds + GEX regime alignment → produces Signal

## Heatmap Integration
- Appears in full_data layer
- Bidirectional: LONG (bullish breakout above wall) or SHORT (bearish breakout below wall)
- Intensity: Yellow/Orange/Red by proximity and Γ_break magnitude
- GEX regime alignment shown in signal metadata

## Gate A — Wall Strength Detail
- Check `wall_gex > rolling_avg + min_wall_gex_sigma × rolling_std`
- Ensures we only trade "major" walls, not minor liquidity pockets

## Gate C — Volume Confirmation Detail
- Check `volume_5m.latest > volume_5m.mean × volume_spike_mult`
- Ensures breakout is supported by actual order flow, not a vacuum

## Validation Checklist (for Synapse)
- [ ] Γ_break formula: `Price_Velocity × Gamma_Concentration_at_Level` ✓
- [ ] Wall detection via `get_gamma_walls()` ✓
- [ ] Trigger: Γ_break > threshold + price crossed wall ✓
- [ ] Gate A: Wall strength (GEX > 2σ above avg) ✓
- [ ] Gate B: GEX regime alignment (LONG→POSITIVE, SHORT→NEGATIVE) ✓
- [ ] Gate C: Volume confirmation (spike > 1.5× avg) ✓
- [ ] Direction: Bidirectional (above wall=LONG, below wall=SHORT) ✓
- [ ] Intensity: Yellow/Orange/Red by proximity and Γ_break ✓
