# Iron Anchor (CONFLUENCE-ALPHA) — Implementation Plan

## Strategy Overview
**Name:** iron_anchor  
**Layer:** full_data  
**Type:** Confluence Reversal  
**Direction:** Bidirectional (mean reversion — LONG at bid+gamma confluence, SHORT at ask+gamma confluence)  
**Synapse ID:** "The Iron Anchor"  

## Core Concept
When a Gamma Wall (dealer hedge structural level) aligns within $1.00 of a Liquidity Wall (massive limit orders in the book), you get dual-confirmation support/resistance. This is the "Immovable Object" — highest conviction mean reversion signal.

**Bullish Reversal:** Bid Liquidity Wall within ±$1.00 of Gamma Support Wall (put wall, negative GEX)  
**Bearish Reversal:** Ask Liquidity Wall within ±$1.00 of Gamma Resistance Wall (call wall, positive GEX)

## Mathematical Definition
```
Ω_conf = |Price_GammaWall - Price_LiquidityWall|  (confluence proximity)

Trigger:
- LONG: Ω_conf < $1.00 AND price approaching AND velocity decreasing (exhaustion)
- SHORT: Ω_conf < $1.00 AND price approaching AND velocity decreasing (exhaustion)
```

## Files to Create/Modify

### 1. `strategies/rolling_keys.py` — Add rolling keys
```python
KEY_CONFLUENCE_PROX_5M = "confluence_prox_5m"     # Ω_conf: distance between gamma wall and liquidity wall
KEY_CONFLUENCE_SIGNAL_5M = "confluence_signal_5m"  # +1 for bullish, -1 for bearish
KEY_LIQUIDITY_WALL_SIZE_5M = "liq_wall_size_5m"   # Size of nearest liquidity wall
KEY_LIQUIDITY_WALL_SIGMA_5M = "liq_wall_sigma_5m"  # Liquidity wall size rolling std
```
Add to `ALL_KEYS` tuple and `__all__` list.

### 2. `main.py` — Add rolling windows + confluence detection

**a) Rolling window initialization** (near line 400, after gamma_breaker windows):
```python
KEY_CONFLUENCE_PROX_5M: RollingWindow(window_type="time", window_size=300),
KEY_CONFLUENCE_SIGNAL_5M: RollingWindow(window_type="time", window_size=300),
KEY_LIQUIDITY_WALL_SIZE_5M: RollingWindow(window_type="time", window_size=300),
KEY_LIQUIDITY_WALL_SIGMA_5M: RollingWindow(window_type="time", window_size=300),
```

**b) In the `_process_data` method** — add confluence detection.
This goes in the gex_summary processing block (after the gamma_breaker block, around line 1230+):

```python
# Iron Anchor — Confluence Detection
# Ω_conf = |Price_GammaWall - Price_LiquidityWall|
# Match gamma walls with liquidity walls from depth aggregates
try:
    price = self._calculator.underlying_price
    if price > 0:
        # Get gamma walls (major walls only, higher threshold)
        gamma_walls = self._calculator.get_gamma_walls(threshold=500000)
        
        if gamma_walls:
            # Get liquidity levels from depth aggregates
            depth_agg = self._rolling_data.get("market_depth_agg", {})
            bid_levels = depth_agg.get("bid_levels", [])
            ask_levels = depth_agg.get("ask_levels", [])
            
            if bid_levels or ask_levels:
                best_prox = float('inf')
                best_signal = 0  # +1 bullish, -1 bearish
                best_liq_size = 0
                
                for wall in gamma_walls:
                    wall_strike = wall["strike"]
                    wall_gex = wall["gex"]
                    wall_side = wall["side"]  # "call" or "put"
                    
                    # For bullish reversal: look for bid liquidity near put walls (negative GEX)
                    # For bearish reversal: look for ask liquidity near call walls (positive GEX)
                    target_levels = bid_levels if wall_side == "put" else ask_levels
                    
                    if not target_levels:
                        continue
                    
                    # Find nearest liquidity level to this gamma wall
                    for level in target_levels:
                        liq_price = level["price"]
                        liq_size = level["size"]
                        if liq_price <= 0:
                            continue
                        
                        prox = abs(wall_strike - liq_price)
                        if prox < best_prox:
                            best_prox = prox
                            best_signal = +1 if wall_side == "put" else -1
                            best_liq_size = liq_size
                
                # Push confluence metrics to rolling windows
                prox_w = self._rolling_data.get(KEY_CONFLUENCE_PROX_5M)
                if prox_w: prox_w.push(best_prox, ts)
                
                sig_w = self._rolling_data.get(KEY_CONFLUENCE_SIGNAL_5M)
                if sig_w: sig_w.push(best_signal, ts)
                
                liq_w = self._rolling_data.get(KEY_LIQUIDITY_WALL_SIZE_5M)
                if liq_w: liq_w.push(best_liq_size, ts)
                
                # Liquidity wall σ
                liq_sig_w = self._rolling_data.get(KEY_LIQUIDITY_WALL_SIGMA_5M)
                if liq_w and liq_sig_w and liq_w.count >= 5:
                    vals = list(liq_w.values)
                    mean_l = sum(vals) / len(vals)
                    var = sum((x - mean_l)**2 for x in vals) / len(vals)
                    liq_sig_w.push(math.sqrt(var), ts)
except Exception:
    pass
```

### 3. `strategies/full_data/iron_anchor.py` — New strategy file

```python
"""
strategies/full_data/iron_anchor.py — Iron Anchor (CONFLUENCE-ALPHA)

Detects when a Gamma Wall aligns with a Liquidity Wall within $1.00.
Ω_conf = |Price_GammaWall - Price_LiquidityWall|

Bullish Reversal: Bid Liquidity Wall near Put Wall → LONG (mean reversion)
Bearish Reversal: Ask Liquidity Wall near Call Wall → SHORT (mean reversion)
Highest conviction mean reversion signal — dual confirmation.

Trigger: Ω_conf < $1.00 AND price approaching AND velocity decreasing

Hard gates (ALL must pass):
    Gate A: Weight check — liquidity wall size > 3σ above rolling avg
    Gate B: Gamma density — gamma wall must be significant (not minor outlier)
    Gate C: Exhaustion — price velocity decreasing as approaching confluence

Confidence model (5 components):
    1. Confluence proximity (0.0–0.30) — tighter Ω_conf = higher confidence
    2. Liquidity weight (0.0–0.20) — heavier wall = more conviction
    3. Gamma density (0.0–0.15) — thicker wall = more structural support
    4. Exhaustion signal (0.0–0.15) — velocity dying = better entry
    5. GEX regime alignment (0.0–0.10) — signal direction matches GEX bias
"""
```

Key implementation details:
- `strategy_id = "iron_anchor"`, `layer = "full_data"`
- Default params:
  - `max_confluence_distance = 1.0` — Ω_conf must be < $1.00
  - `min_liq_wall_sigma = 3.0` — Gate A: liquidity wall > 3σ above avg
  - `min_gamma_wall_gex = 500000` — Gate B: minimum GEX for gamma wall
  - `exhaustion_velocity_mult = 0.8` — velocity must be < 80% of rolling avg
  - `min_confidence = 0.35`
  - `max_confidence = 0.85`
  - `stop_pct = 0.008` — slightly wider for reversal strategies
  - `target_risk_mult = 1.5` — mean reversion has tighter targets

- **Direction logic:**
  - LONG when confluence signal is bullish (bid wall near put wall) AND velocity decreasing AND regime == "POSITIVE"
  - SHORT when confluence signal is bearish (ask wall near call wall) AND velocity decreasing AND regime == "NEGATIVE"
  - Note: For mean reversion, the GEX regime should support the reversal direction

- **Gate B (GEX Alignment):** For mean reversion, the regime should support the reversal
  - LONG mean reversion (bounce off support) works best in POSITIVE gamma (stabilizing)
  - SHORT mean reversion (reject off resistance) works best in NEGATIVE gamma (destabilizing)

- **Intensity metadata:**
  - Yellow: Price within $1.00 of confluence (proximity detected)
  - Orange: Price touching wall; both liquidity and gamma high
  - Red: Price hits wall; velocity dies; Ω_conf near zero

### 4. `strategies/full_data/__init__.py` — Add export
```python
from .iron_anchor import IronAnchor
```
Add `IronAnchor` to `__all__`.

### 5. `config/strategies.yaml` — Add config
Under `full_data:` section:
```yaml
iron_anchor:
  enabled: true
  params:
    max_confluence_distance: 1.0
    min_liq_wall_sigma: 3.0
    min_gamma_wall_gex: 500000
    exhaustion_velocity_mult: 0.8
    min_confidence: 0.35
    max_confidence: 0.85
    stop_pct: 0.008
    target_risk_mult: 1.5
```

## Data Flow
1. `orb_probe.py` → `depthagg_parsed` → TradeStationClient → depth aggregate messages
2. `_process_data()` stores depth levels in `rolling_data["market_depth_agg"]` with `bid_levels`/`ask_levels`
3. gex_summary processing block runs confluence detection: matches gamma walls to liquidity levels
4. `StrategyEngine.process()` passes `data` (including `regime`) to `iron_anchor.evaluate()`
5. Strategy evaluates Ω_conf thresholds + exhaustion + GEX regime → produces Signal

## Heatmap Integration
- Appears in full_data layer
- Bidirectional: LONG (bid+gamma confluence = bounce) or SHORT (ask+gamma confluence = reject)
- Intensity: Yellow/Orange/Red by proximity and engagement level
- GEX regime alignment shown in signal metadata

## Gate A — Weight Check Detail
- Check `liq_wall_size > rolling_avg + min_liq_wall_sigma × rolling_std`
- Ensures we only trade "heavy" liquidity walls, not ghost orders

## Gate B — Gamma Density Detail
- Check `wall_gex > min_gamma_wall_gex` from config
- Ensures the gamma wall is structurally significant

## Gate C — Exhaustion Detail
- Check `price_velocity < rolling_avg_velocity × exhaustion_velocity_mult`
- Ensures price is slowing as it approaches the confluence (not crashing through)

## Validation Checklist (for Synapse)
- [ ] Ω_conf formula: `|Price_GammaWall - Price_LiquidityWall|` ✓
- [ ] Confluence detection: spatial join between gamma walls and depth levels ✓
- [ ] Trigger: Ω_conf < $1.00 + velocity decreasing ✓
- [ ] Gate A: Weight check (liq wall > 3σ above avg) ✓
- [ ] Gate B: Gamma density (wall GEX significant) ✓
- [ ] Gate C: Exhaustion (velocity decreasing) ✓
- [ ] Direction: Bidirectional (bid+gamma=LONG, ask+gamma=SHORT) ✓
- [ ] Intensity: Yellow/Orange/Red by proximity and engagement ✓
