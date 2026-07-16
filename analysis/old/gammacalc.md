# Gamma-Related Calculation Sites Analysis — Full Syngex

**Date:** 2026-06-22
**Scope:** Layer 3, Full Data (Layer 4), shared/critical files
**Method:** Systematic grep + deep-read of key files

---

## 1. SOURCE OF TRUTH: GEXCalculator (`engine/gex_calculator.py`)

### 1.1 `_StrikeBucket.net_gamma` (line 74)
- **Type:** Raw cumulative net gamma at a single strike
- **Calculation:** `call_gamma_oi - put_gamma_oi`
- **Normalization:** None — raw OI-weighted gamma
- **Intent:** Per-strike raw gamma exposure

### 1.2 `_StrikeBucket.normalized_gamma()` (line 108)
- **Type:** Per-message-average net gamma
- **Calculation:** `net_gamma / (call_count + put_count)`
- **Normalization:** Divides cumulative gamma by total message count at that strike
- **Intent:** Bounded gamma value that doesn't grow with message count; used for GEX wall detection

### 1.3 `GEXCalculator.get_net_gamma()` (line 223)
- **Type:** Cumulative total net gamma across ALL strikes
- **Calculation:** `sum(b.net_gamma for b in self._ladder.values())`
- **Normalization:** None — cumulative, grows with message count
- **Intent:** Sign detection for regime filtering (POSITIVE vs NEGATIVE)
- **Caching:** Lazy-computed with `_net_gamma_dirty` flag

### 1.4 `GEXCalculator.get_normalized_net_gamma()` (line 235)
- **Type:** Normalized total net gamma (per-message average across all strikes)
- **Calculation:** `sum(bucket.net_gamma / total_count for each bucket)`
- **Normalization:** Per-message average at each strike, summed across all strikes
- **Intent:** Canonical scale for GEX comparisons (walls, magnets, cross-session analysis)

### 1.5 `GEXCalculator.get_strike_net_gamma(strike)` (line 258)
- **Type:** Raw cumulative net gamma at a specific strike
- **Calculation:** `bucket.net_gamma`
- **Normalization:** None

### 1.6 `GEXCalculator.get_normalized_strike_net_gamma(strike)` (line 251)
- **Type:** Normalized net gamma at a specific strike
- **Calculation:** `bucket.normalized_gamma()`
- **Normalization:** Per-message average

### 1.7 `GEXCalculator.get_strike_gex(strike)` (line 266)
- **Type:** Dollar-denominated GEX at a strike
- **Calculation:** `get_strike_net_gamma(strike) * 100 * underlying_price`
- **Normalization:** Uses raw (cumulative) gamma, NOT normalized

### 1.8 `GEXCalculator.get_gamma_walls(threshold=1e6)` (line 294)
- **Type:** List of strikes with massive GEX
- **Calculation:** Iterates all strikes, computes `norm_net_gamma * 100 * price`, filters by `|gex| >= threshold`
- **Normalization:** Uses `bucket.normalized_gamma()` (per-message average)
- **Intent:** Identify gamma walls for strategy signals

### 1.9 `GEXCalculator.get_gamma_flip()` (line 340)
- **Type:** Strike where cumulative normalized gamma turns negative
- **Calculation:** Scans sorted strikes (high→low), accumulates normalized gamma, returns first strike where cumulative < 0
- **Normalization:** Uses normalized gamma
- **Intent:** Gamma flip point for regime filter

### 1.10 `GEXCalculator.get_summary()` (line 277)
- **Returns:** Both `net_gamma` (cumulative) and `net_gamma_normalized` (per-message average)
- **Intent:** Master state dump for orchestrator

### 1.11 `GEXCalculator.get_greeks_summary()` (line 394)
- **Returns:** Per-strike dict with `net_gamma`, `call_gamma`, `put_gamma`, `call_oi`, `put_oi`, `net_delta`, `total_contracts`
- **Normalization:** All gamma values are normalized (per-message average)
- **Intent:** Feed for Layer 2/3 strategies needing per-strike data

---

## 2. DATA PIPELINE: main.py (`main.py`)

### 2.1 Net Gamma Rolling Window Population (line 900-903)
```python
ng = self._calculator.get_net_gamma()
self._rolling_data[KEY_NET_GAMMA_5M].push(ng)
```
- **Value:** Raw cumulative `net_gamma` (from `get_net_gamma()`)
- **Rolling key:** `KEY_NET_GAMMA_5M` = "net_gamma_5m"
- **Intent:** Track net gamma over 5-minute rolling window

### 2.2 Total Gamma Rolling Window (line 992-993)
```python
self._rolling_data[KEY_TOTAL_GAMMA_5M].push(
    self._calculator.get_net_gamma()
)
```
- **Value:** Raw cumulative `net_gamma`
- **Rolling key:** `KEY_TOTAL_GAMMA_5M` = "total_gamma_5m"
- **Intent:** Same metric, different key name (used by gamma_volume_convergence for acceleration)

### 2.3 Gamma Density Rolling Window (line 1678-1692)
```python
gamma_density += abs(call_gamma) + abs(put_gamma)
self._rolling_data[KEY_GAMMA_DENSITY_5M].push(gamma_density)
```
- **Value:** Sum of absolute normalized call_gamma + put_gamma within window_pct of underlying
- **Normalization:** Uses `strike_data.get("call_gamma", 0.0)` from `get_greeks_summary()` → normalized per-message gamma
- **Rolling key:** `KEY_GAMMA_DENSITY_5M` = "gamma_density_5m"
- **Intent:** Concentration of gamma near current price

### 2.4 Gamma Break Index Rolling Window (line 1250-1280)
```python
gamma_concentration = abs(wall_gex) / avg_gex
gamma_break = velocity * gamma_concentration
self._rolling_data[KEY_GAMMA_BREAK_INDEX_5M].push(gamma_break)
```
- **Value:** `velocity * (abs(wall_gex) / avg_gex)` — price velocity × gamma concentration ratio
- **Normalization:** Wall GEX normalized by rolling average GEX
- **Rolling key:** `KEY_GAMMA_BREAK_INDEX_5M` = "gamma_break_5m"
- **Intent:** Combined momentum × gamma signal for GammaBreaker strategy

### 2.5 Wall GEX Rolling Window (line 1266-1267)
```python
self._rolling_data[KEY_WALL_GEX_5M].push(abs(wall_gex))
```
- **Value:** Absolute wall GEX (from `get_gamma_walls()`)
- **Rolling key:** `KEY_WALL_GEX_5M` = "wall_gex_5m"
- **Intent:** Track wall strength over time

### 2.6 Wall GEX Sigma (line 1270-1275)
```python
gex_sig_w.push(math.sqrt(var), ts)
```
- **Value:** Rolling standard deviation of wall GEX
- **Rolling key:** `KEY_WALL_GEX_SIGMA_5M` = "wall_gex_sigma_5m"
- **Intent:** Statistical significance of wall strength

### 2.7 Orchestrator Data Snapshot (line 2506-2528)
```python
summary = self._calculator.get_summary()
net_gamma = summary["net_gamma"]
data = {
    "net_gamma": net_gamma,                    # cumulative
    "net_gamma_normalized": summary["net_gamma_normalized"],  # per-message avg
    "gamma_flip": flip,
    "greeks_summary": self._calculator.get_greeks_summary(),
    "regime": self._gamma_filter.regime,
}
```
- **Key insight:** Both cumulative AND normalized net_gamma are injected into strategy data
- **Regime filter uses:** Cumulative `net_gamma` for sign detection

---

## 3. REGIME FILTER: `strategies/filters/net_gamma_filter.py`

### 3.1 `update_regime()` (line 83-110)
- **Input:** `net_gamma` (cumulative, from GEXCalculator), `flip_strike`, `underlying_price`
- **Regime logic:** `POSITIVE if net_gamma >= 0 else NEGATIVE`
- **Transition detection:** `abs(underlying_price - flip_strike) / underlying_price < flip_buffer / underlying_price`
- **Default regime:** POSITIVE
- **Intent:** Master regime filter that gates ALL strategy signals

### 3.2 `evaluate_signal()` (line 126-148)
- **POSITIVE regime:** Fade extremes — LONG when price < flip, SHORT when price > flip
- **NEGATIVE regime:** Trend-follow — LONG when price > flip, SHORT when price < flip
- **Transitioning:** All signals blocked

---

## 4. STRATEGY ENGINE: `strategies/engine.py`

### 4.1 `process()` (line 182-252)
- **Phase 1:** Evaluate all registered strategies with data dict containing `net_gamma`, `net_gamma_normalized`, `regime`, `gex_calculator`
- **Phase 2:** Apply regime filter callback
- **Phase 2.5:** Inter-strategy conflict detection (LONG vs SHORT within 5s windows)
- **Phase 3:** Cap signals per tick (max_signals_per_tick)
- **Phase 4:** Deliver signals to handlers

### 4.2 Layer Priority (line 300-310)
```python
priority_map = {"layer1": 1, "layer2": 2, "layer3": 3, "full_data": 4}
```
- **full_data strategies have highest priority** in conflict resolution

---

## 5. LAYER 3 STRATEGIES

### 5.1 `gamma_volume_convergence.py`

#### 5.1.1 Input (line 123)
```python
net_gamma = data.get("net_gamma_normalized", 0)
```
- **Uses:** `net_gamma_normalized` (per-message average)
- **Intent:** Signal strength proportional to normalized gamma

#### 5.1.2 MIN_GAMMA_THRESHOLD (line 84)
- **Value:** 500.0 (absolute threshold)
- **Check:** `if abs(net_gamma) < MIN_GAMMA_THRESHOLD: return`
- **Intent:** Minimum dealer positioning to fire signal

#### 5.1.3 Gamma Acceleration (line 537-578)
```python
gamma_accel = (gamma_current - gamma_5_ago) / abs(gamma_5_ago) - (gamma_5_ago - gamma_10_ago) / abs(gamma_10_ago)
```
- **Type:** 2nd derivative of gamma (acceleration of gamma ROC)
- **Source:** `KEY_TOTAL_GAMMA_5M` rolling window
- **Hard gate:** `gamma_accel < 0.10` → reject
- **Score:** `gamma_score = min(1.0, gamma_accel / 0.30)`
- **Intent:** Detect accelerating gamma — ignition signal

#### 5.1.4 Gamma Spike (line 240, 404)
```python
gamma_spike = self._check_gamma_spike(rolling_data)
```
- **Source:** `KEY_TOTAL_GAMMA_5M` rolling window
- **Intent:** Measure gamma spike ratio for confidence scoring

#### 5.1.5 Delta-Gamma Coupling (line 192-196, 356-360)
- **Type:** Hard gate (0.0 or 0.10)
- **Intent:** Ensure delta and gamma move in same direction — filter phantom spikes

#### 5.1.6 Confidence Weighting (line 206)
```python
gamma_score * 0.30  # 30% weight in signal_strength
```

---

### 5.2 `iv_band_breakout.py`

#### 5.2.1 Input (line 117)
```python
net_gamma = data.get("net_gamma_normalized", 0)
```
- **Uses:** `net_gamma_normalized`

#### 5.2.2 Gamma Regime Hard Gate (line 496)
```python
def _check_gamma_regime(regime: str) -> bool:
    return regime in ("POSITIVE", "NEGATIVE")  # NEUTRAL = skip
```
- **Type:** Hard gate
- **Intent:** Only fire in defined gamma regimes

#### 5.2.3 Regime-Dependent Targets (line 577-582)
- **POSITIVE gamma:** Wider targets (`positive_gamma_target_mult`)
- **NEGATIVE gamma:** Tighter targets (`negative_gamma_target_mult`)
- **Intent:** Adjust profit targets based on dealer hedging behavior

#### 5.2.4 Confidence Weighting
- **Gamma regime component:** 0.10 weight (graded)
- **Intent:** Regime alignment contributes to confidence

---

### 5.3 `strike_concentration.py`

#### 5.3.1 Input (line 138)
```python
net_gamma = data.get("net_gamma_normalized", 0)
```
- **Uses:** `net_gamma_normalized`

#### 5.3.2 Regime Check (line 146)
```python
if net_gamma <= 0:  # Only LONG in positive gamma
    return
```
- **Intent:** Only trade bounces in positive gamma regime

#### 5.3.3 Gamma Magnitude at Strike (line 949-964)
```python
gamma_mag = gex_calc.get_strike_net_gamma(strike)  # raw cumulative
return abs(gamma_val)
```
- **Uses:** Raw cumulative gamma at specific strike
- **Intent:** Confidence weighting — stronger gamma wall = higher confidence

#### 5.3.4 Confidence Weighting (line 1192-1195, 1274-1277)
```python
gamma_conf = 0.05 + 0.05 * min(1.0, gamma_mag / GAMMA_MAGNITUDE_THRESHOLD)
```
- **Threshold:** `GAMMA_MAGNITUDE_THRESHOLD` (default 2000)
- **Range:** 0.05 (baseline) to 0.10 (max)
- **Normalization:** Linear scaling capped at threshold

#### 5.3.5 Regime Confidence (line 1208, 1323)
```python
regime_conf = 0.05 + 0.05 * min(1.0, abs(net_gamma) / 2000)
```
- **Normalization:** Linear scaling of |net_gamma|, capped at 2000
- **Range:** 0.05 to 0.10

#### 5.3.6 Final Confidence Formula (line 1237, 1345)
```python
norm_gamma = (gamma_conf - 0.05) / (0.10 - 0.05)
confidence = (norm_rank + norm_prox + norm_gamma + norm_signal + norm_regime + norm_atr) / 6.0
```
- **Normalization:** Linear mapping from [0.05, 0.10] to [0, 1]

---

### 5.4 `theta_burn.py`

#### 5.4.1 Input (line 138)
```python
net_gamma = data.get("net_gamma_normalized", 0)
```
- **Uses:** `net_gamma_normalized`

#### 5.4.2 Regime Mode Selection (line 146-153)
```python
if net_gamma >= 0:
    # POSITIVE gamma → bounce mode (mean reversion at walls)
else:
    # NEGATIVE gamma → slice mode (momentum breakouts)
```
- **Intent:** Different strategy behavior based on gamma sign

#### 5.4.3 GAMMA_STRENGTH_HIGH (line 105)
- **Value:** 2000.0
- **Intent:** Threshold for max gamma strength bonus

#### 5.4.4 Wall Net Gamma (line 249, 377, 551, 668)
```python
wall_net_gamma = nearest_wall.get("net_gamma", 0)
```
- **Source:** `get_gamma_walls()` → normalized gamma per wall
- **Intent:** Wall-specific gamma for confidence scoring

#### 5.4.5 Delta-Gamma Divergence (line 256, 384, 558, 675)
- **Type:** Hard gate (0.20-0.25 range)
- **Intent:** Reject signals when delta and gamma diverge

#### 5.4.6 Confidence Weighting (line 1038-1039, 1075, 1117-1118, 1149)
```python
gamma_strength = abs(wall_net_gamma) if wall_net_gamma != 0 else abs(wall_gex)
gamma_conf = 0.10 + 0.10 * min(1.0, gamma_strength / GAMMA_STRENGTH_HIGH)
norm_gamma = (gamma_conf - 0.10) / (0.20 - 0.10)
```
- **Range:** 0.10 to 0.20
- **Normalization:** Linear mapping to [0, 1]
- **Fallback:** Uses wall_gex if wall_net_gamma is zero

#### 5.4.7 Gamma Walls Access (line 1284-1289)
```python
gex_calc.get_gamma_walls(threshold=MIN_NET_GAMMA)
```
- **Default threshold:** `MIN_NET_GAMMA` (defined in file)

---

## 6. FULL DATA (LAYER 4) STRATEGIES

### 6.1 `iv_skew_squeeze.py`

#### 6.1.1 Constants (line 70-74)
```python
GAMMA_CEILING = 2000.0  # Global ceiling for net_gamma normalization
MIN_GAMMA_CONVICTION = 500.0  # Minimum |net_gamma| for meaningful positioning
```

#### 6.1.2 Input (line 136)
```python
net_gamma = data.get("net_gamma_normalized", 0.0)
```
- **Uses:** `net_gamma_normalized`

#### 6.1.3 Gamma Conviction Check (line 170-174)
```python
_gamma_conviction = min(1.0, max(0.0, net_gamma / GAMMA_CEILING)) if net_gamma > 0 else 0.0
if abs(net_gamma) < MIN_GAMMA_CONVICTION:
    return  # Skip if too weak
```
- **Directional:** Only positive net_gamma contributes to conviction
- **Normalization:** Linear scaling to [0, 1] with ceiling at 2000

#### 6.1.4 Gamma Strength Confidence (line 428-436)
```python
def _gamma_strength_confidence(self, net_gamma: float) -> float:
    if net_gamma < 0:
        return 0.05  # Negative gamma — low confidence
    scale = min(1.0, abs(net_gamma) / (GAMMA_CEILING * 2))
    return 0.05 + 0.05 * scale  # Range: 0.05 to 0.10
```
- **Range:** 0.05 to 0.10
- **Ceiling:** GAMMA_CEILING * 2 = 4000 for full score

#### 6.1.5 Confidence Component (line 470-471)
```python
c5 = min(1.0, net_gamma / 2000.0)  # Directional, no abs
```
- **Intent:** Higher net_gamma = higher confidence for skew squeeze

---

### 6.2 `prob_weighted_magnet.py`

#### 6.2.1 Constants (line 85, 104)
```python
GAMMA_CEILING = 2000.0
GAMMA_SCALE_BASE = 2.0  # gamma value for 2.0× target scaling
```

#### 6.2.2 Input (line 147)
```python
net_gamma = data.get("net_gamma_normalized", 0.0)
```

#### 6.2.3 Gamma Score (line 181-186)
```python
if net_gamma < 0:
    gamma_score = 0.0
else:
    gamma_score = min(1.0, net_gamma / (GAMMA_CEILING * 2))
```
- **Range:** 0 to 1
- **Ceiling:** 4000 for full score
- **Directional:** Negative gamma → 0

#### 6.2.4 Gamma-Weighted Target (line 340-375)
```python
gamma_at_strike = gex_calc.get_strike_net_gamma(magnet_strike)  # raw cumulative
abs_gamma = abs(gamma_at_strike)
gamma_scale = min(2.0, 1.0 + abs_gamma / GAMMA_SCALE_BASE)
target_mult = 1.5 * gamma_scale
```
- **Uses:** Raw cumulative gamma at magnet strike (NOT normalized)
- **Scaling:** Linear, capped at 2.0×
- **Intent:** Higher gamma at magnet = wider target (more dealer hedging pressure)

#### 6.2.5 Confidence (line 433-434)
```python
c4 = gamma_score  # Direct pass-through
```

---

### 6.3 `prob_distribution_shift.py`

#### 6.3.1 Constants (line 83, 86)
```python
MIN_GAMMA_CONVICTION = 500.0
GAMMA_CEILING = 2000.0
```

#### 6.3.2 Input (line 154)
```python
net_gamma = data.get("net_gamma_normalized", 0.0)
```

#### 6.3.3 Regime Check (line 166-167)
```python
regime = data.get("regime", "UNKNOWN")
if regime == "NEUTRAL":
    return  # Skip in neutral regime
```

#### 6.3.4 Gamma Conviction (line 170-173)
```python
# Changed from net_gamma > 0 to abs(net_gamma) so both regimes contribute
_gamma_conviction = min(1.0, max(0.0, abs(net_gamma) / GAMMA_CEILING))
```
- **Key difference:** Uses `abs(net_gamma)` — both POSITIVE and NEGATIVE regimes contribute
- **Intent:** SHORT signals in negative regime are valid (short squeezes)

#### 6.3.5 Confidence Component (line 746-749)
```python
# Changed from net_gamma to abs(net_gamma) so SHORT signals in negative gamma
# regime also score well (short squeezes in negative regime are valid setups)
c7 = min(1.0, abs(net_gamma) / 2000.0)
```
- **Intent:** Bidirectional gamma scoring

---

### 6.4 `extrinsic_intrinsic_flow.py`

#### 6.4.1 Input (line 150)
```python
net_gamma = data.get("net_gamma_normalized", 0.0)
```

#### 6.4.2 Constants (line 151)
```python
self._min_net_gamma = self._params.get("min_net_gamma", 5000.0)
```

#### 6.4.3 Gamma Score (line 158-162)
```python
if net_gamma < 0:
    gamma_score = 0.0
else:
    gamma_score = min(1.0, max(0.0, net_gamma / (self._min_net_gamma * 2)))
```
- **Directional:** Only positive gamma contributes
- **Ceiling:** `min_net_gamma * 2` = 10000 (configurable)

#### 6.4.4 Structural Gamma (line 460)
```python
c10 = min(1.0, abs(net_gamma) / 2000.0)
```
- **Bidirectional:** Uses `abs(net_gamma)`
- **Ceiling:** 2000

#### 6.4.5 Direction Score (line 502, 657, 816)
```python
direction_score = extrinsic_score * gamma_score * vol_trend_score
```
- **Intent:** Gamma acts as multiplier on extrinsic flow signal

---

### 6.5 `extrinsic_flow.py`

#### 6.5.1 Input (line 95)
```python
net_gamma = data.get("net_gamma_normalized", 0.0)
```

#### 6.5.2 Gate B — GEX Regime (line 260-275)
```python
def _gate_b_gex_regime(self, direction: str, regime: str) -> bool:
    if direction == "LONG" and regime == "POSITIVE":
        return True
    if direction == "SHORT" and regime == "NEGATIVE":
        return True
    self._regime_mismatch = True
    return False
```
- **Type:** Hard gate (pass/fail)
- **Intent:** Bullish in positive gamma, bearish in negative gamma

#### 6.5.3 Regime Mismatch Penalty (line 307-309)
```python
if getattr(self, '_regime_mismatch', False):
    confidence *= 0.70  # 30% penalty for mismatch
```
- **Intent:** Soft penalty when regime doesn't align

#### 6.5.4 Confidence Component (line 157)
```python
"regime_score" = gate_b  # 0.0 or 1.0
```
- **Weight:** 0.10 in confidence

---

### 6.6 `skew_dynamics.py`

#### 6.6.1 Input (line 95)
```python
net_gamma = data.get("net_gamma_normalized", 0.0)
```

#### 6.6.2 Constants (line 57)
```python
MIN_GAMMA_CONVICTION = 500.0
```

#### 6.6.3 Gamma Conviction Check (line 96)
```python
if abs(net_gamma) < MIN_GAMMA_CONVICTION:
    return  # Skip if too weak
```
- **Bidirectional:** Uses `abs(net_gamma)`

#### 6.6.4 Regime Score (line 250-266)
```python
def _score_gex_regime(self, direction: str, regime: str) -> float:
    if direction == "LONG" and regime == "POSITIVE": return 1.0
    if direction == "SHORT" and regime == "NEGATIVE": return 1.0
    if direction == "LONG" and regime == "NEGATIVE": return 0.0
    if direction == "SHORT" and regime == "POSITIVE": return 0.0
    return 0.5  # unknown
```
- **Type:** 0.0, 0.5, or 1.0
- **Intent:** Directional alignment with gamma regime

#### 6.6.5 Confidence Component (line 335)
```python
c7 = regime_score
```
- **Weight:** Part of 7-component confidence

---

### 6.7 `smile_dynamics.py`

#### 6.7.1 Input (line 101)
```python
net_gamma = data.get("net_gamma_normalized", 0.0)
```

#### 6.7.2 Constants (line 62)
```python
MIN_GAMMA_CONVICTION = 500.0
```

#### 6.7.3 Gamma Conviction (line 102)
```python
if abs(net_gamma) < MIN_GAMMA_CONVICTION:
    return
```
- **Bidirectional:** Uses `abs(net_gamma)`

#### 6.7.4 Regime Score (line 276-290)
- Same pattern as skew_dynamics: 0.0, 0.5, or 1.0

#### 6.7.5 Regime Factor (line 384-390)
```python
regime_aligned = (direction == "LONG" and regime == "POSITIVE") or (direction == "SHORT" and regime == "NEGATIVE")
regime_factor = 1.0 if regime_aligned else 0.3
return roc_score * regime_factor
```
- **Intent:** 3× penalty for regime misalignment

---

### 6.8 `ghost_premium.py`

#### 6.8.1 Input (line 120)
```python
regime = data.get("regime", "")
```
- Note: Does NOT read `net_gamma_normalized` directly — uses regime string

#### 6.8.2 GEX Regime Alignment (line 361-363)
```python
net_gamma = data.get("net_gamma_normalized", 0.0)
c5 = min(1.0, abs(net_gamma) / 2000.0)
```
- **Bidirectional:** Uses `abs(net_gamma)`
- **Ceiling:** 2000
- **Weight:** 0.10 in confidence

---

### 6.9 `whale_tracker.py`

#### 6.9.1 Input (line 90)
```python
regime = data.get("regime", "")
```

#### 6.9.2 Gate C — GEX Regime (line 319-336)
```python
def _gate_c_gex_regime(self, direction: str, regime: str) -> bool:
    if direction == "LONG" and regime == "POSITIVE": return True
    if direction == "SHORT" and regime == "NEGATIVE": return True
    self._regime_mismatch = True
    return False
```
- Same pattern as extrinsic_flow

#### 6.9.3 Regime Mismatch Penalty (line 371-372)
```python
if getattr(self, '_regime_mismatch', False):
    confidence *= 0.70  # 30% penalty
```

---

### 6.10 `gamma_breaker.py`

#### 6.10.1 Input (line 96-97)
```python
regime = data.get("regime", "")
gex_calc = data.get("gex_calculator")
```
- Note: Does NOT read `net_gamma_normalized` directly — uses regime string

#### 6.10.2 Gamma Break Index (line 109-118)
```python
gamma_break_window = rolling_data.get(KEY_GAMMA_BREAK_INDEX_5M)
current_gamma_break = gamma_break_window.values[-1]
```
- **Source:** Rolling window of `velocity * gamma_concentration`
- **Hard gate:** `current_gamma_break > min_gamma_break` (default 0.005)

#### 6.10.3 Wall GEX (line 120-121)
```python
current_wall_gex = wall_gex_window.values[-1] if wall_gex_window else 0.0
current_wall_gex_sigma = wall_gex_sigma_window.values[-1]
```
- **Source:** Rolling windows populated in main.py

#### 6.10.4 Gate B — GEX Regime (line 285-296)
- Same pattern: LONG needs POSITIVE, SHORT needs NEGATIVE

#### 6.10.5 Confidence Weighting (line 339-350)
```python
c1 = normalize(current_gamma_break, 0.0, 0.01)
c3 = normalize(current_wall_gex_sigma, 0.0, 5.0)
c5 = normalize(current_wall_gex, 0.0, 2000.0)  # Dynamic normalization
```
- **Intent:** Normalized wall GEX for confidence scoring

---

### 6.11 `iron_anchor.py`

#### 6.11.1 Input (line 86-87)
```python
regime = data.get("regime", "")
gex_calc = data.get("gex_calculator")
```

#### 6.11.2 Constants (line 94)
```python
min_gamma_wall_gex = params.get("min_gamma_wall_gex", 2000)
```

#### 6.11.3 Gate B — Gamma Density (line 281-299)
```python
def _gate_b_gamma_density(self, gex_calc, regime, direction, min_gamma_wall_gex):
    if not regime: return False
    # GEX regime alignment
    if gex_calc and hasattr(gex_calc, "get_gamma_walls"):
        walls = gex_calc.get_gamma_walls(threshold=min_gamma_wall_gex)
```
- **Uses:** `get_gamma_walls()` with configurable threshold
- **Intent:** Gamma wall must be significant (not minor outlier)

---

### 6.12 `sentiment_sync.py`

#### 6.12.1 Input (line 95)
```python
regime = data.get("regime", "")
```

#### 6.12.2 GEX Bias (line 359-366)
```python
gex_bias = data.get("gex_bias", 0)
if direction == "LONG":
    c6 = normalize(gex_bias, -1.0, 1.0) * 0.10
else:
    c6 = normalize(-gex_bias, -1.0, 1.0) * 0.10
```
- **Uses:** `gex_bias` (separate from net_gamma)
- **Normalization:** Linear to [-1, 1] range, scaled by 0.10

---

## 7. SHARED/CRITICAL FILES

### 7.1 `strategies/signal.py`
- **Line 15:** `strategy_id="gamma_wall_bounce"` — example signal
- **Line 17:** `metadata={"wall_strike": 196, "gex": 1250000}` — stores GEX in metadata
- **Line 53:** `regime filter before signals reach the dashboard` — comment about regime filtering
- **Line 60:** `strategy_id: str  # e.g. "gamma_wall_bounce"` — documentation

### 7.2 `strategies/metrics/collector.py`
- **No gamma-specific logic** — generic metrics storage
- Stores whatever metrics strategies publish (including net_gamma values)
- Thread-safe, ring buffer (max 1000 entries per strategy)

### 7.3 `orb_probe.py`
- **Line 267:** `gamma = _safe_float(raw.get("Gamma"))` — extracts raw Gamma from option update
- **Line 322:** `"gamma": gamma` — includes in parsed output
- **Intent:** Parse raw Gamma from TradeStation option chain for offline analysis
- **Not connected to GEXCalculator** — standalone probe tool

### 7.4 `data/ingestor.py`
- **Line 13:** `Callback-based message dispatch to the GEXCalculator`
- **No gamma calculation** — purely data ingestion/streaming
- Feeds messages to GEXCalculator via callback

---

## 8. CROSS-CUTTING PATTERNS & ISSUES

### 8.1 Normalization Inconsistency
| File | What it uses | Normalization |
|------|-------------|---------------|
| GEXCalculator.get_net_gamma() | Cumulative | None (grows with msgs) |
| GEXCalculator.get_normalized_net_gamma() | Per-message avg | Divided by msg count |
| Strategies (most) | `net_gamma_normalized` | Per-message avg |
| theta_burn (wall gamma) | `get_strike_net_gamma()` | Raw cumulative |
| prob_weighted_magnet (target) | `get_strike_net_gamma()` | Raw cumulative |
| strike_concentration (gamma_mag) | `get_strike_net_gamma()` | Raw cumulative |

**Issue:** Some strategies use normalized net_gamma for regime checks but raw cumulative gamma for wall-specific calculations. This creates scale inconsistency — cumulative gamma grows with time, so wall gamma magnitudes drift upward even if actual dealer positioning is stable.

### 8.2 Directional vs Bidirectional Gamma
| Pattern | Files |
|---------|-------|
| **Directional** (positive only) | iv_skew_squeeze, prob_weighted_magnet, extrinsic_intrinsic_flow, strike_concentration (LONG only) |
| **Bidirectional** (abs) | prob_distribution_shift, extrinsic_intrinsic_flow (structural c10), ghost_premium, skew_dynamics, smile_dynamics |
| **Regime-gated** (sign-based) | All strategies via regime filter |

### 8.3 Gamma Ceilings/Thresholds
| Constant | Value | Files |
|----------|-------|-------|
| `GAMMA_CEILING` | 2000.0 | iv_skew_squeeze, prob_weighted_magnet, prob_distribution_shift |
| `MIN_GAMMA_CONVICTION` | 500.0 | iv_skew_squeeze, prob_distribution_shift, skew_dynamics, smile_dynamics |
| `MIN_GAMMA_THRESHOLD` | 500.0 | gamma_volume_convergence |
| `GAMMA_MAGNITUDE_THRESHOLD` | 2000.0 | strike_concentration |
| `GAMMA_STRENGTH_HIGH` | 2000.0 | theta_burn |
| `GAMMA_SCALE_BASE` | 2.0 | prob_weighted_magnet |
| `min_net_gamma` (param) | 5000.0 | extrinsic_intrinsic_flow |

**Issue:** 2000.0 is the dominant ceiling but extrinsic_intrinsic_flow uses 5000.0 as its base, creating a 2× inconsistency in what "strong" gamma means across strategies.

### 8.4 Regime Filter vs Strategy-Level Regime Checks
- The **master regime filter** (net_gamma_filter.py) gates ALL signals based on price vs flip point
- **Individual strategies** ALSO check regime alignment (e.g., LONG needs POSITIVE)
- This creates **double-gating** — a signal must pass both the regime filter AND the strategy's internal regime check
- Most strategies use `data.get("regime", "")` which comes from the filter's output

### 8.5 Rolling Window Keys
| Key | Value Source | Used By |
|-----|-------------|---------|
| `net_gamma_5m` | `get_net_gamma()` (cumulative) | gamma_volume_convergence (acceleration) |
| `total_gamma_5m` | `get_net_gamma()` (cumulative) | gamma_volume_convergence (acceleration) |
| `gamma_density_5m` | Sum of abs normalized gamma near price | (internal) |
| `wall_gex_5m` | `abs(wall_gex)` from get_gamma_walls() | gamma_breaker |
| `wall_gex_sigma_5m` | Rolling σ of wall_gex_5m | gamma_breaker |
| `gamma_break_5m` | velocity × gamma_concentration | gamma_breaker |

### 8.6 Missing: sum_pos_gamma / sum_neg_gamma
- **No `sum_pos_gamma` or `sum_neg_gamma` variables found** in any file
- The system uses `net_gamma` (calls - puts) rather than separate long/short gamma sums
- Per-strike buckets track `call_gamma_oi` and `put_gamma_oi` separately, but these are never aggregated into separate sums for strategy use

---

## 9. SUMMARY TABLE

| File | Gamma Source | Normalized? | Directional? | Normalization/Scaling |
|------|-------------|-------------|-------------|----------------------|
| net_gamma_filter.py | `get_net_gamma()` cumulative | No | Sign-based | Binary: ≥0 POSITIVE, <0 NEGATIVE |
| gamma_volume_convergence.py | `net_gamma_normalized` + rolling | Yes | Bidirectional (abs check) | Threshold 500, acceleration 2nd deriv |
| iv_band_breakout.py | `net_gamma_normalized` | Yes | Regime-gated | Hard gate: POSITIVE/NEGATIVE only |
| strike_concentration.py | `net_gamma_normalized` + raw at strike | Mixed | Directional (LONG only) | Linear 0→2000, 6-component confidence |
| theta_burn.py | `net_gamma_normalized` + wall gamma | Mixed | Regime-gated | 0→2000, dual mode (bounce/slice) |
| iv_skew_squeeze.py | `net_gamma_normalized` | Yes | Directional (positive) | Linear 0→2000, conviction gate 500 |
| prob_weighted_magnet.py | `net_gamma_normalized` + raw at strike | Mixed | Directional (positive) | Linear 0→4000, gamma-weighted targets |
| prob_distribution_shift.py | `net_gamma_normalized` | Yes | **Bidirectional (abs)** | Linear 0→2000, both regimes valid |
| extrinsic_intrinsic_flow.py | `net_gamma_normalized` | Yes | Directional (positive) | Linear 0→10000 (configurable), structural abs |
| extrinsic_flow.py | Regime string only | N/A | Regime-gated | Hard gate + 30% mismatch penalty |
| skew_dynamics.py | `net_gamma_normalized` | Yes | Bidirectional (abs) | Conviction gate 500, regime score 0/0.5/1 |
| smile_dynamics.py | `net_gamma_normalized` | Yes | Bidirectional (abs) | Conviction gate 500, regime factor 1.0/0.3 |
| ghost_premium.py | `net_gamma_normalized` | Yes | Bidirectional (abs) | Linear 0→2000 |
| whale_tracker.py | Regime string only | N/A | Regime-gated | Hard gate + 30% mismatch penalty |
| gamma_breaker.py | Rolling gamma_break_index | Pre-computed | Regime-gated | Velocity × concentration ratio |
| iron_anchor.py | `get_gamma_walls()` | Normalized | Regime-gated | Configurable threshold (default 2000) |
| sentiment_sync.py | `gex_bias` (separate) | N/A | Bidirectional | Normalized -1→1 |
| orb_probe.py | Raw `Gamma` field | No | N/A | Direct parse from TradeStation |
| gex_calculator.py | Source of truth | Both modes | Both | Cumulative + per-message-average |

# Gamma Calculation & Usage Sites — `main.py` (3149 lines)

**File:** `/home/hologaun/projects/syngex/main.py`
**Date:** 2026-06-22

---

## 1. Imports & Constants

### 1.1 Imports (lines 77, 90, 93, 106, 116)
| Line | What | Type |
|------|------|------|
| 77 | `from strategies.filters.net_gamma_filter import NetGammaFilter` | Class import |
| 90 | `KEY_NET_GAMMA_5M` | Rolling window key constant |
| 93 | `KEY_TOTAL_GAMMA_5M` | Rolling window key constant |
| 106 | `KEY_GAMMA_DENSITY_5M` | Rolling window key constant |
| 116 | `KEY_GAMMA_BREAK_INDEX_5M` | Rolling window key constant |

### 1.2 Strategy class imports (lines 214–257)
| Line | Class | Gamma relevance |
|------|-------|----------------|
| 214 | `GammaWallBounce` | Wall-based strategy |
| 216 | `GammaFlipBreakout` | Flip-point breakout |
| 217 | `GammaSqueeze` | Squeeze detection |
| 224 | `DeltaGammaSqueeze` | Delta+Gamma combined |
| 243 | `GammaVolumeConvergence` | Volume+gamma convergence |
| 257 | `GammaBreaker` | Gamma breakout index strategy |

---

## 2. Initialization & Configuration

### 2.1 Gamma Filter Setup (lines 308, 438–443)
- **Line 308:** `self._gamma_filter: NetGammaFilter | None = None` — uninitialized state
- **Lines 438–443:** Reads `filter_config.get("net_gamma", {})` → creates `NetGammaFilter(flip_buffer=...)` → registers `self._gamma_filter.evaluate_signal` as a strategy filter
- **Intent:** Regime filter that gates strategy signals based on whether net gamma is positive (fade extremes) or negative (trend-follow)

### 2.2 Gamma Wall Caches (lines 353–355)
```python
self._gamma_walls_100k: Optional[List] = None
self._gamma_walls_500k: Optional[List] = None
self._gamma_walls_5k: Optional[List] = None
```
- Cached gamma wall lists at three thresholds: $100k, $500k, $5k GEX
- Only `_gamma_walls_500k` is persisted across ticks (line 970)

### 2.3 Rolling Window Initialization (lines 448–449)
All rolling windows (including gamma keys) are initialized via:
```python
self._rolling_data: Dict[str, RollingWindow] = {
    key: RollingWindow(window_type="time", window_size=ROLLING_WINDOW_SIZES.get(key, 300))
    for key in ALL_KEYS
}
```
Gamma-related keys in `ALL_KEYS` (from `rolling_keys.py`):
- `KEY_NET_GAMMA_5M` — rolling net gamma
- `KEY_TOTAL_GAMMA_5M` — rolling total gamma
- `KEY_GAMMA_DENSITY_5M` — rolling gamma density
- `KEY_WALL_GEX_5M` — rolling wall GEX
- `KEY_WALL_GEX_SIGMA_5M` — rolling wall GEX std dev
- `KEY_GAMMA_BREAK_INDEX_5M` — rolling gamma break index

---

## 3. Data Processing Loop — Gamma Computations

### 3.1 Rolling Net Gamma (lines 900–903)
```python
if self._calculator._msg_count % 20 == 0:
    ng = self._calculator.get_net_gamma()
    self._rolling_data[KEY_NET_GAMMA_5M].push(ng)
```
- **Type:** `net_gamma` (cumulative, unnormalized)
- **Action:** Calculated via `GEXCalculator.get_net_gamma()` every 20 messages, pushed to rolling window
- **Note:** Rate-limited to avoid per-tick overhead

### 3.2 Total Gamma Rolling (lines 991–994)
```python
self._rolling_data[KEY_TOTAL_GAMMA_5M].push(
    self._calculator.get_net_gamma()
)
```
- **Type:** `net_gamma` (cumulative)
- **Action:** Pushed every tick (not rate-limited) to `KEY_TOTAL_GAMMA_5M`
- **Intent:** "total_gamma_5m — from GEXCalculator net gamma" (comment on line 991)

### 3.3 Gamma Walls (lines 961–971)
```python
# Heavy per-ladder calculations (rate-limited to _is_heavy_tick)
gamma_walls_100k = self._calculator.get_gamma_walls(threshold=100000)
self._gamma_walls_500k = self._calculator.get_gamma_walls(threshold=500000)
gamma_walls_5k = self._calculator.get_gamma_walls(threshold=5000)
```
- **Type:** `gamma_walls` — list of strike dicts with `strike`, `net_gamma` (normalized), `gex`, `side`
- **Action:** Computed via `GEXCalculator.get_gamma_walls()` at three thresholds
- **Normalization:** Uses **normalized** (per-message average) gamma internally
- **GEX formula:** `gex = norm_net_gamma * 100 * price`
- **Intent:** Identify strikes with massive GEX concentration (Gamma Walls)

### 3.4 Gamma Break Index (lines 1230–1281)
```python
# Γ_break = Price_Velocity × Gamma_Concentration_at_Level
walls = gamma_walls_100k
nearest_wall = walls[0]  # Largest GEX wall
wall_gex = nearest_wall["gex"]
wall_dist_pct = abs(wall_strike - price) / price
avg_gex = sum(abs(w["gex"]) for w in walls) / len(walls)
gamma_concentration = abs(wall_gex) / avg_gex
velocity = abs(price_window[-1] - price_window[0]) / abs(price_window[0])
gamma_break = velocity * gamma_concentration
```
- **Type:** `gamma_break` (derived index)
- **Action:** Computed from cached gamma walls + price velocity
- **Formula:** `Γ_break = |Δprice_pct_5m| × (wall_GEX / avg_GEX)`
- **Stored to:** `KEY_WALL_DISTANCE_5M`, `KEY_WALL_GEX_5M`, `KEY_WALL_GEX_SIGMA_5M`, `KEY_PRICE_VELOCITY_5M`, `KEY_GAMMA_BREAK_INDEX_5M`
- **Intent:** Measures how likely price is to break through the nearest gamma wall

### 3.5 Iron Anchor — Gamma/Liquidity Confluence (lines 1286–1339)
```python
# Ω_conf = |Price_GammaWall - Price_LiquidityWall|
gamma_walls = gamma_walls_500k
# Match gamma walls with liquidity walls from depth aggregates
```
- **Type:** `gamma_walls` (500k threshold) + liquidity walls
- **Action:** Cross-references gamma walls against bid/ask liquidity levels
- **Intent:** Detect confluence between gamma walls and liquidity walls (Iron Anchor strategy)
- **Stored to:** `KEY_CONFLUENCE_PROX_5M`, `KEY_CONFLUENCE_SIGNAL_5M`, `KEY_LIQUIDITY_WALL_SIZE_5M`, `KEY_LIQUIDITY_WALL_SIGMA_5M`

### 3.6 Magnet Delta — Near Gamma Walls (lines 1493–1517)
```python
walls = gamma_walls_5k
# Compute average wall delta for nearby walls
avg_wall_delta = sum(w["net_delta"] for w in nearby) / len(nearby)
```
- **Type:** `gamma_walls` (5k threshold) + `net_delta` per wall
- **Action:** Computes average delta of walls within 0.5% of price
- **Intent:** Magnet effect — price attracted to nearby gamma walls

### 3.7 Flow Ratio — Gamma-Weighted OI (lines 1632–1651)
```python
call_score += call_oi * call_gamma * call_delta
put_score += put_oi * put_gamma * put_delta
flow_ratio = call_score / put_score
```
- **Type:** `call_gamma`, `put_gamma` (normalized per-strike)
- **Action:** Computes gamma-weighted OI × delta score per side, then ratio
- **Intent:** Call/put flow asymmetry — directional bias weighted by gamma exposure

### 3.8 Gamma Density (lines 1672–1692)
```python
window_pct = iv_gex_params.get("gamma_density_window_pct", 0.01)
gamma_density = 0.0
for strike in strikes_within_window_pct:
    gamma_density += abs(call_gamma) + abs(put_gamma)
```
- **Type:** `call_gamma`, `put_gamma` (normalized)
- **Action:** Sum of absolute gamma values within `window_pct` (default 1%) of current price
- **Stored to:** `KEY_GAMMA_DENSITY_5M`
- **Intent:** IV-GEX divergence v2 — measures local gamma concentration near ATM

---

## 4. Strategy Evaluation

### 4.1 Regime Filter Update (lines 2503–2527)
```python
summary = self._calculator.get_summary()
net_gamma = summary["net_gamma"]
flip = self._calculator.get_gamma_flip()
self._gamma_filter.update_regime(net_gamma, flip, price)
```
- **Types:** `net_gamma` (cumulative), `gamma_flip` (strike price)
- **Action:** Updates regime filter with current gamma state
- **Regime logic:**
  - POSITIVE net_gamma → fade extremes (buy dips, sell rallies)
  - NEGATIVE net_gamma → trend-follow (buy breakouts, sell breakdowns)
- **Transition zone:** When price is within `flip_buffer` ($0.50 default) of flip strike

### 4.2 Strategy Data Snapshot (lines 2514–2531)
```python
data = {
    "regime": self._gamma_filter.regime,
    "net_gamma": net_gamma,
    "net_gamma_normalized": summary["net_gamma_normalized"],
    "gamma_flip": flip,
    "greeks_summary": self._calculator.get_greeks_summary(),
    "_gamma_sync": _gamma_sync,
    ...
}
```
- **Types passed to strategies:**
  - `net_gamma` — cumulative (for regime)
  - `net_gamma_normalized` — per-message average (for magnitude)
  - `gamma_flip` — flip strike price
  - `greeks_summary` — per-strike dict with `net_gamma`, `call_gamma`, `put_gamma`, `call_oi`, `put_oi`, `net_delta`, `call_delta_sum`, `put_delta_sum` (all normalized for gamma)
  - `_gamma_sync` — correlation from rolling window (Sentiment Sync)

---

## 5. Gamma Profile Reporting

### 5.1 Full Profile Report (lines 2571–2620)
```python
summary = self._calculator.get_summary()
profile = self._calculator.get_gamma_profile()
net = summary["net_gamma"]
flip = self._calculator.get_gamma_flip()
walls = self._gamma_walls_500k
top = sorted(profile["strikes"].items(), key=lambda x: abs(x[1]["net_gamma"]), reverse=True)[:5]
```
- **Types:** `net_gamma` (cumulative), `gamma_flip`, `gamma_walls`, `net_gamma` (normalized, per-strike in profile)
- **Action:** Logs gamma profile at intervals (configurable, line 292)
- **Output:** Net gamma, flip strike, top 3 gamma walls, top 5 strikes by |net_gamma|

---

## 6. GEX State Export

### 6.1 JSON Export for Streamlit (lines 2975–3024)
```python
export = {
    "net_gamma": state["net_gamma"],
    "net_gamma_normalized": state["net_gamma_normalized"],
    "strikes": profile["strikes"],
    ...
}
```
- **Types:** `net_gamma`, `net_gamma_normalized`, `strikes` (per-strike profile)
- **Action:** Writes full GEX state to shared JSON file for dashboard
- **Also exports:** `regime_filter` status from `_gamma_filter.get_status()`

---

## 7. Summary of Gamma Types & Their Normalization

| Gamma Type | Normalized? | Source | Used For |
|-----------|-------------|--------|----------|
| `net_gamma` (cumulative) | No | `GEXCalculator.get_net_gamma()` | Regime detection, sign determination |
| `net_gamma_normalized` | Yes (÷ msg count) | `GEXCalculator.get_normalized_net_gamma()` | GEX magnitude, wall detection, cross-session comparison |
| `call_gamma` / `put_gamma` (per-strike) | Yes (normalized) | `GEXCalculator.get_greeks_summary()` | Strategy greeks_summary, flow ratio, density |
| `gamma_walls` | Yes (normalized → GEX) | `GEXCalculator.get_gamma_walls()` | Wall detection at $100k/$500k/$5k thresholds |
| `gamma_flip` | N/A (strike price) | `GEXCalculator.get_gamma_flip()` | Regime transition boundary |
| `gamma_break` | Derived | Computed in main.py | GammaBreaker strategy input |
| `gamma_density` | Derived | Computed in main.py | IV-GEX divergence v2 |
| `flow_ratio` | Derived | Computed in main.py | Call/put asymmetry |

---

## 8. Key Design Notes

1. **Dual gamma scale:** The codebase maintains BOTH cumulative (`net_gamma`) and normalized (`net_gamma_normalized`) gamma. Cumulative is used for regime/sign detection (the sign doesn't change with message count). Normalized is used for magnitude comparisons (walls, GEX, cross-session).

2. **Rate limiting:** Gamma wall computations and rolling net gamma pushes are rate-limited (`_is_heavy_tick` and `msg_count % 20`) because iterating the full strike ladder is expensive.

3. **Gamma filter regime:** The `NetGammaFilter` gates ALL strategy signals. It checks both the net gamma sign AND whether price is near the flip point (transition zone).

4. **Gamma walls:** Three thresholds exist ($5k, $100k, $500k) for different strategy needs — fine-grained magnet effects vs. major structural walls.

5. **Per-strike gamma in greeks_summary:** All gamma values in `greeks_summary` are normalized (per-message average), while OI values remain cumulative. This is documented in the GEXCalculator docstring.

# Layer 1 Gamma Calculations — Full Audit

**Scope:** All 8 layer-1 strategy files in `/home/hologaun/projects/syngex/strategies/layer1/*.py`
**Date:** 2026-06-22

---

## 1. gamma_wall_bounce.py

### Gamma Types Used
| Gamma Variable | Type | Source |
|---|---|---|
| `wall["gex"]` | Pass-through from `get_gamma_walls()` / `get_wall_classifications()` | `gex_calc` |
| `KEY_TOTAL_GAMMA_5M` | Rolling window (trend detection) | `rolling_data` |
| `net_gamma` | Not directly used — regime derived from wall side (call=positive, put=negative) | — |

### Key Calculations

**Line 46–47 — `MIN_WALL_GEX = 500000`**
- Hard threshold for considering a strike a "wall". This is the **normalized** scale (consistent with `get_gamma_walls()`).
- Wall classification comes from `gex_calc.get_wall_classifications(threshold=MIN_WALL_GEX)` (line 84) or `gex_calc.get_gamma_walls(threshold=500_000)` (line 127).

**Lines 133–135 — `wall_gex = wall["gex"]`**
- Pass-through from gex_calc. The wall dict contains `gex` (the GEX magnitude at that strike).
- Call wall = positive net_gamma → resistance. Put wall = negative net_gamma → support.

**Lines 468–471 — Confidence normalization for wall strength**
```python
norm_strength = (gex_magnitude - MIN_WALL_GEX) / (5_000_000 - MIN_WALL_GEX)
```
- Linear normalization: maps `[MIN_WALL_GEX (500K), 5_000_000]` → `[0, 1]`.
- Ceiling is 5M for wall strength confidence.

**Lines 413–428 — Gamma trend from rolling window**
```python
from strategies.rolling_keys import KEY_PRICE_5M, KEY_TOTAL_GAMMA_5M
gw = rolling_data.get(KEY_TOTAL_GAMMA_5M)
gamma_trend = recent_g[-1] - recent_g[0]
if abs(gamma_trend) > 200000:
    base_score *= 0.7  # penalize if gamma is shifting fast
```
- Uses `KEY_TOTAL_GAMMA_5M` rolling window to detect gamma trend.
- If gamma changes by more than 200K over the window, rejection score is penalized (wall may be evaporating).

### Intent
- Trade mean-reversion bounces off high-GEX gamma walls.
- Positive gamma walls (call walls) = resistance → SHORT bounce.
- Negative gamma walls (put walls) = support → LONG bounce.
- Wall strength (GEX magnitude) is a core confidence component.
- Gamma trend (rolling) used as a quality filter.

---

## 2. magnet_accelerate.py

### Gamma Types Used
| Gamma Variable | Type | Source |
|---|---|---|
| `net_gamma` (from `data["net_gamma_normalized"]`) | Passed-through from upstream | `data.get("net_gamma_normalized", 0)` |
| `magnet_gex` | **Calculated** from `bucket.normalized_gamma()` | Computed |
| `norm_net_gamma` | **Calculated** via `bucket.normalized_gamma()` | `_find_magnet()` |

### Key Calculations

**Line 89 — `net_gamma = data.get("net_gamma_normalized", 0)`**
- Passed through from upstream data dict. Not calculated here.
- Used for regime gating and confidence scoring.

**Lines 107–108 — `magnet_gex` calculation**
```python
magnet_gex = abs(magnet_bucket.normalized_gamma() * 100 * underlying_price)
```
- **Custom calculation:** Takes the bucket's `normalized_gamma()` (per-message average gamma), multiplies by `100 * price` to convert to dollar GEX.
- This is the same formula used in `_find_magnet()` (lines 342–343).
- Scale: normalized gamma × 100 × price → dollar-denominated GEX.

**Lines 326–345 — `_find_magnet()` — Finding highest-GEX strike**
```python
for strike, bucket in ladder.items():
    norm_net_gamma = bucket.normalized_gamma()
    gex = abs(norm_net_gamma * 100 * price)
    if gex > best_gex:
        best_gex = gex
        best_strike = strike
```
- Iterates all strikes in `gex_calc._ladder`.
- Uses `normalized_gamma()` (not raw gamma) for consistent scale.
- Converts to dollar GEX: `abs(norm_net_gamma * 100 * price)`.
- Returns the strike with highest absolute normalized gamma.

**Line 109 — `MIN_MAGNET_GEX = 500000`**
- Minimum |normalized GEX| for a strike to qualify as a magnet.
- Same scale as `MIN_WALL_GEX` in gamma_wall_bounce.

**Lines 393–401 — Phase 1 confidence: gamma strength normalization**
```python
gamma_strength = 0.2 + 0.3 * min(1.0, net_gamma / 2000)
```
- Maps `net_gamma` from `[0, 2000]` → `[0.2, 0.5]` contribution.
- Ceiling: 2000 (normalized scale).

**Lines 426–435 — Phase 2 confidence: gamma magnitude normalization**
```python
gamma_conf = 0.1 + 0.1 * min(1.0, abs(net_gamma) / 2000)
```
- Maps `abs(net_gamma)` from `[0, 2000]` → `[0.1, 0.2]` contribution.
- Same 2000 ceiling for negative gamma regime.

### Intent
- **Phase 1:** In positive gamma regime, price is magnetically pulled toward the highest-GEX strike. Trade LONG below magnet, SHORT above magnet.
- **Phase 2:** When price breaks through magnet AND gamma turns negative, trade the momentum breakout.
- `normalized_gamma()` is the key calculation — converts raw per-message gamma to a per-message average that's consistent across messages.

---

## 3. gamma_flip_breakout.py

### Gamma Types Used
| Gamma Variable | Type | Source |
|---|---|---|
| `net_gamma` (from `data["net_gamma_normalized"]`) | Passed-through | `data.get("net_gamma_normalized", 0)` |
| `flip_mid` | From `get_gamma_flip()` or `get_atm_strike()` | `gex_calc` |
| Wall GEX | Pass-through from `get_gamma_walls()` / `get_wall_classifications()` | `gex_calc` |

### Key Calculations

**Line 86 — `net_gamma = data.get("net_gamma_normalized", 0)`**
- Passed-through from upstream.
- Used for regime strength scoring and confidence.

**Lines 48 — `MIN_GAMMA_STRENGTH = 200`**
- Minimum `|net_gamma_normalized|` for regime confidence.
- Very low threshold — almost any non-trivial gamma qualifies.

**Lines 150–159 — `_get_flip_zone()`**
```python
flip_mid = gex_calc.get_gamma_flip()
if flip_mid is None:
    flip_mid = gex_calc.get_atm_strike(price)
```
- Gets the gamma flip point (where net gamma crosses zero).
- Falls back to ATM strike if no flip point exists.

**Lines 205–206 — Gamma score normalization**
```python
gamma_score = min(1.0, abs(net_gamma) / 2000.0)
```
- Normalizes `|net_gamma|` to `[0, 1]` using 2000 ceiling.
- Used as 0.3 weight in confirmation score.

**Lines 638–639 — Confidence: gamma normalization**
```python
gamma_norm = min(1.0, abs(net_gamma) / 2000.0)
```
- Same normalization, used in confidence calculation.

**Lines 649–650 — Wall proximity normalization**
```python
wall_norm = min(1.0, abs(net_gamma) / 2000.0)
```
- Reuses gamma normalization for wall proximity (same 2000 ceiling).

### Intent
- Trade the regime boundary defined by the gamma flip point.
- Above flip (positive gamma): fade breakouts (mean reversion).
- Below flip (negative gamma): trade breakouts (momentum).
- Gamma strength (`|net_gamma|`) modulates confidence.

---

## 4. gamma_squeeze.py

### Gamma Types Used
| Gamma Variable | Type | Source |
|---|---|---|
| `net_gamma` (from `data["net_gamma_normalized"]`) | Passed-through | `data.get("net_gamma_normalized", 0)` |
| Wall GEX | Pass-through from `get_gamma_walls()` | `gex_calc` |

### Key Calculations

**Line 97 — `net_gamma = data.get("net_gamma_normalized", 0)`**
- Passed-through from upstream.

**Line 54 — `MIN_WALL_GEX = 100`**
- Very low threshold for wall consideration in squeeze context.
- Different from gamma_wall_bounce's 500K — squeeze uses a much lower bar.

**Line 57 — `MIN_MASSIVE_WALL_GEX = 500`**
- Fallback threshold for positive regime filter.
- Used in `_regime_passes()` (line 168).

**Lines 159–165 — Positive regime wall filter (95th percentile)**
```python
walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
gex_values = [abs(w["gex"]) for w in walls]
gex_values.sort()
p95_idx = max(0, int(len(gex_values) * 0.95) - 1)
p95_gex = gex_values[p95_idx]
if abs(wall_gex) >= p95_gex:
    return True
```
- In positive gamma regime, only fires if wall GEX is at 95th percentile of all walls.
- Dynamic threshold based on current wall distribution.

**Lines 201–202 — Pin detection: positive net gamma gate**
```python
if net_gamma <= 0:
    return False
```
- Pin detection requires positive net gamma (dealer support).

**Lines 250–258 — Breakout detection**
```python
walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)
```
- Uses `get_gamma_walls()` to find walls near price for breakout detection.

**Lines 499–509 — Wall strength calculation**
```python
wall_iv = gex_calc.get_iv_by_strike(wall_strike)
atm_iv = gex_calc.get_iv_by_strike(atm_strike)
gex_score = 0.5 + 0.5 * min(1.0, abs(wall.get("gex", 0)) / 2_000)
```
- GEX component: `abs(gex) / 2000` normalized to `[0.5, 1.0]`.
- Ceiling: 2000 (normalized scale).

**Lines 580–583 — Direction alignment check**
```python
if direction == Direction.LONG and net_gamma <= 0:
    return None
if direction == Direction.SHORT and net_gamma >= 0:
    return None
```
- LONG breakout requires positive net gamma.
- SHORT breakout requires negative net gamma.

**Lines 675–679 — Confidence normalization**
```python
norm_wall = min(1.0, abs(wall_gex) / 2_000)
norm_gamma = min(1.0, net_gamma / 2000.0) if net_gamma > 0 else 0.0
```
- Wall GEX: normalized to `[0, 1]` using 2000 ceiling.
- Net gamma: normalized to `[0, 1]` using 2000 ceiling (only positive).

### Intent
- Detect price pinned between gamma walls with positive net gamma, then trade the breakout.
- Positive gamma regime: only fires on massive walls (95th percentile).
- Negative gamma regime: fires freely (squeezes amplify in negative gamma).
- Wall strength = IV premium + GEX magnitude + classification.

---

## 5. gex_imbalance.py

### Gamma Types Used
| Gamma Variable | Type | Source |
|---|---|---|
| `call_gex` | **Calculated** by summing positive gamma per bucket | `_calculate_gex_split()` |
| `put_gex` | **Calculated** by summing absolute negative gamma per bucket | `_calculate_gex_split()` |
| `net_gamma` (from `get_normalized_net_gamma()`) | **Fetched** from gex_calc | `gex_calc.get_normalized_net_gamma()` |
| Ratio = `call_gex / put_gex` | **Calculated** | — |

### Key Calculations

**Lines 108–109 — GEX split calculation**
```python
call_gex, put_gex = self._calculate_gex_split(gex_calc)
```

**Lines 219–242 — `_calculate_gex_split()` — Core gamma calculation**
```python
greeks = gex_calc.get_greeks_summary()
call_gex = 0.0
put_gex = 0.0
for bucket in greeks:
    net_gamma = bucket.get("net_gamma", 0.0)
    if net_gamma > 0:
        call_gex += net_gamma
    else:
        put_gex += abs(net_gamma)
return (call_gex, put_gex)
```
- **This is the primary gamma calculation in the entire layer 1 suite.**
- Iterates all strike buckets from `get_greeks_summary()`.
- Sums positive `net_gamma` → `call_gex` (call-side dealer gamma).
- Sums absolute negative `net_gamma` → `put_gex` (put-side dealer gamma).
- Ratio = `call_gex / put_gex` determines dealer hedging bias.

**Lines 123 — `net_gamma = gex_calc.get_normalized_net_gamma()`**
- Gets the overall normalized net gamma for regime intensity.
- Used for regime alignment bonus.

**Lines 317–329 — Regime intensity**
```python
intensity = min(1.0, abs(net_gamma) / REGIME_GAMMA_THRESHOLD)
```
- `REGIME_GAMMA_THRESHOLD = 2000` (line 62).
- Normalizes `|net_gamma|` to `[0, 1]`.

### Intent
- Trade dealer hedging bias revealed by call/put GEX ratio.
- Call-heavy GEX → dealers short hedge → price pressure DOWN → SHORT.
- Put-heavy GEX → dealers buy hedge → price pressure UP → LONG.
- The `_calculate_gex_split()` method is the only place that explicitly sums positive/negative gamma across all strikes.

---

## 6. confluence_reversal.py

### Gamma Types Used
| Gamma Variable | Type | Source |
|---|---|---|
| Wall GEX | Pass-through from `get_gamma_walls()` | `gex_calc` |
| Flip point | From `get_gamma_flip()` | `gex_calc` |

### Key Calculations

**Lines 127–128 — Gamma structural levels**
```python
walls = gex_calc.get_gamma_walls(threshold=500_000)
flip = gex_calc.get_gamma_flip()
```
- Uses `get_gamma_walls()` for gamma wall detection.
- Uses `get_gamma_flip()` for flip point detection.
- Threshold: 500K (normalized scale).

**Lines 356–358, 461–463 — Stop multiplier based on regime**
```python
NEGATIVE_GAMMA_STOP_MULT = 1.5
POSITIVE_GAMMA_STOP_MULT = 0.75
```
- Wider stops in negative gamma (more noise/volatility).
- Tighter stops in positive gamma (cleaner mean-reversion).

**Lines 615–616 — GEX strength for confidence**
```python
gex_strength = min(1.0, abs(gex) / 10_000_000)
```
- Normalizes wall GEX to `[0, 1]` using 10M ceiling.
- Much higher ceiling than other strategies (10M vs 2K/2000).
- This is the **only** strategy using 10M as a ceiling.

### Intent
- Combine technical S/R with gamma structural levels (walls, flip points).
- Score each level: technical=1, gamma wall=1, flip=1.
- Wall strength (higher |GEX|) provides confidence bonus.
- Stop width adapts to gamma regime (negative=1.5x, positive=0.75x).

---

## 7. vol_compression_range.py

### Gamma Types Used
| Gamma Variable | Type | Source |
|---|---|---|
| `net_gamma` (from `get_normalized_net_gamma()`) | **Fetched** from gex_calc | `gex_calc.get_normalized_net_gamma()` |
| Wall GEX | Pass-through from `get_gamma_walls()` | `gex_calc` |

### Key Calculations

**Lines 237–243 — Regime stop multiplier**
```python
net_gamma = gex_calc.get_normalized_net_gamma()
abs_gamma = abs(net_gamma)
conviction = min(1.0, abs_gamma / GAMMA_CEILING)
```
- `GAMMA_CEILING = 2000.0` (line 65).
- Normalizes `|net_gamma|` to `[0, 1]`.
- Higher conviction → tighter stops (0.7x vs 1.0x).

**Lines 303, 402 — Wall detection**
```python
walls = gex_calc.get_gamma_walls(threshold=500_000)
```
- Uses `get_gamma_walls()` for range edge detection.
- Threshold: 500K (normalized scale).

**Lines 522–523 — Wall strength normalization**
```python
norm_strength = min(1.0, abs(wall_gex) / 5_000_000)
```
- Wall GEX normalized to `[0, 1]` using 5M ceiling.
- Consistent with gamma_wall_bounce's wall strength ceiling.

### Intent
- Range scalping in positive gamma regime.
- Dealer hedging in long gamma dampens volatility → mean-reversion range.
- Gamma conviction (|net_gamma|) determines stop width.
- Gamma walls serve as range edges.

---

## 8. gex_divergence.py

### Gamma Types Used
| Gamma Variable | Type | Source |
|---|---|---|
| `gamma_slope` | **Calculated** from rolling window | `_calculate_slope()` |
| `gamma_accel` | **Calculated** from rolling window | `_calculate_acceleration()` |
| `gamma_window` | Rolling window of net_gamma | `rolling_data.get(KEY_NET_GAMMA_5M)` |
| `net_gamma` (from `get_normalized_net_gamma()`) | **Fetched** from gex_calc | `gex_calc.get_normalized_net_gamma()` |
| `net_gamma_val` (from `get_summary()`) | **Fetched** from gex_calc | `gex_calc.get_summary()` |

### Key Calculations

**Lines 113–127 — Gamma window and slope/acceleration**
```python
gamma_window = self._get_gamma_window(rolling_data)
gamma_slope = self._calculate_slope(gamma_window)
gamma_accel = self._calculate_acceleration(gamma_window, ACCEL_WINDOW_SHORT, ACCEL_WINDOW_LONG)
```
- Gets `KEY_NET_GAMMA_5M` rolling window from `rolling_data`.
- Calculates slope (linear regression) of gamma over the window.
- Calculates acceleration (change in slope between short and long windows).
- `ACCEL_MIN_GAMMA = 0.0003` (line 64) — minimum acceleration threshold.

**Lines 135–136 — Divergence detection**
```python
if (price_slope > 0 and gamma_slope > 0) or \
   (price_slope < 0 and gamma_slope < 0):
    return []  # No divergence — both trending same direction
```
- Divergence = price and gamma trending in **opposite** directions.
- Bearish divergence: price UP + gamma DOWN → SHORT.
- Bullish divergence: price DOWN + gamma UP → LONG.

**Lines 187–189 — Gamma strength from summary**
```python
summary = gex_calc.get_summary()
net_gamma_val = summary.get("net_gamma", 0.0)
gamma_strength_bonus = min(1.0, abs(net_gamma_val) / GAMMA_CEILING)
```
- `GAMMA_CEILING = 2000.0` (line 59).
- Normalizes `|net_gamma|` to `[0, 1]`.

**Lines 351–361 — Regime intensity**
```python
net_gamma = gex_calc.get_normalized_net_gamma()
abs_gamma = abs(net_gamma)
ratio = min(1.0, abs_gamma / (REGIME_INTENSITY_THRESHOLD * 2))
```
- `REGIME_INTENSITY_THRESHOLD = 1000.0` (line 60).
- Normalizes `|net_gamma|` to `[0, 1]` using 2000 (threshold * 2) ceiling.

**Lines 443–444 — Gamma slope normalization**
```python
norm_gamma = min(1.0, abs(gamma_slope) / 0.01)
```
- Gamma slope normalized to `[0, 1]` using 0.01 ceiling.

**Lines 469–470 — Gamma strength normalization**
```python
norm_gamma_strength = min(1.0, gamma_strength_bonus)
```
- Already normalized; just capped at 1.0.

**Lines 494–499 — `_get_gamma_window()`**
```python
for key in (KEY_NET_GAMMA_5M,):
    rw = rolling_data.get(key)
```
- Retrieves the net_gamma rolling window from `rolling_data`.
- This is the only strategy that uses a rolling window for gamma trend analysis.

### Intent
- Fade exhausted trends by detecting price/GEX slope divergence.
- When price trends but gamma walls are evaporating (or strengthening), the trend is losing (or gaining) structural support.
- Gamma slope and acceleration are the primary calculated metrics.
- Rolling window approach is unique to this strategy.

---

## Cross-File Summary: Normalization Ceilings

| Strategy | Gamma Ceiling | Used For |
|---|---|---|
| gamma_wall_bounce | 5,000,000 | Wall strength confidence |
| gamma_wall_bounce | 200,000 | Gamma trend penalty threshold |
| magnet_accelerate | 2,000 | Phase 1 & 2 gamma confidence |
| magnet_accelerate | 500,000 | MIN_MAGNET_GEX |
| gamma_flip_breakout | 2,000 | Gamma score, confidence, wall norm |
| gamma_flip_breakout | 200 | MIN_GAMMA_STRENGTH |
| gamma_squeeze | 2,000 | Wall strength, net gamma confidence |
| gamma_squeeze | 100 | MIN_WALL_GEX |
| gamma_squeeze | 500 | MIN_MASSIVE_WALL_GEX |
| gex_imbalance | 2,000 | REGIME_GAMMA_THRESHOLD |
| confluence_reversal | 10,000,000 | GEX strength confidence |
| vol_compression_range | 2,000 | GAMMA_CEILING |
| vol_compression_range | 5,000,000 | Wall strength confidence |
| gex_divergence | 2,000 | GAMMA_CEILING |
| gex_divergence | 1,000 | REGIME_INTENSITY_THRESHOLD |
| gex_divergence | 0.01 | Gamma slope normalization ceiling |

## Gamma Source Patterns

| Source Pattern | Strategies Using It |
|---|---|
| `data.get("net_gamma_normalized", 0)` | gamma_flip_breakout, gamma_squeeze, magnet_accelerate |
| `gex_calc.get_normalized_net_gamma()` | gex_imbalance, vol_compression_range, gex_divergence |
| `gex_calc.get_summary()["net_gamma"]` | gex_divergence |
| `gex_calc._ladder[].normalized_gamma() * 100 * price` | magnet_accelerate (magnet_gex, _find_magnet) |
| `rolling_data[KEY_TOTAL_GAMMA_5M]` | gamma_wall_bounce (trend) |
| `rolling_data[KEY_NET_GAMMA_5M]` | gex_divergence (slope/acceleration) |
| `bucket.get("net_gamma")` summed by sign | gex_imbalance (_calculate_gex_split) |
| `gex_calc.get_gamma_walls()` | gamma_wall_bounce, gamma_squeeze, gex_divergence, vol_compression_range, confluence_reversal |
| `gex_calc.get_gamma_flip()` | gamma_flip_breakout, confluence_reversal |
| `gex_calc.get_wall_classifications()` | gamma_wall_bounce, gamma_squeeze, magnet_accelerate |

## Key Observations

1. **No file calculates `net_gamma` from raw greeks internally** — all files either receive it pre-calculated (from upstream `data` dict or `gex_calc`), or derive it from `gex_calc` methods. The only exception is `magnet_accelerate.py` which computes `magnet_gex` from `bucket.normalized_gamma()`.

2. **`normalized_gamma()` is the key differentiator** — Used exclusively in `magnet_accelerate.py` to compute per-message-average gamma, then converted to dollar GEX via `* 100 * price`. This ensures consistency across messages with different volumes.

3. **Three distinct normalization ceilings dominate:**
   - **2,000** — Most common. Used for `net_gamma` confidence/scoring across most strategies.
   - **500,000 – 5,000,000** — Used for wall GEX magnitude confidence.
   - **10,000,000** — Only confluence_reversal uses this very high ceiling.

4. **`gex_imbalance.py` is unique** in explicitly summing positive and negative gamma across all strikes to compute `call_gex` and `put_gex`. This is the only file that performs the split calculation.

5. **`gex_divergence.py` is unique** in using rolling windows of gamma to compute slope and acceleration — the only trend-based gamma analysis.

6. **`gamma_wall_bounce.py` is unique** in using `KEY_TOTAL_GAMMA_5M` rolling window for gamma trend detection (penalizing fast-moving walls).

7. **`magnet_accelerate.py` is unique** in directly accessing `gex_calc._ladder` and calling `bucket.normalized_gamma()` to find the highest-GEX strike.

# Gamma-Related Calculations & Usage — Layer 2 Strategies

**Scope:** All 17 files in `/home/hologaun/projects/syngex/strategies/layer2/*.py`
**Date:** 2026-06-22

---

## Summary Table

| # | File | Gamma Types Used | Calculated or Passed-Through? |
|---|------|-----------------|------------------------------|
| 1 | delta_gamma_squeeze.py | net_gamma_normalized, gex_acceleration, wall_gex, KEY_TOTAL_GAMMA_5M | Both: passes net_gamma_normalized, calculates gex_accel from rolling window |
| 2 | call_put_flow_asymmetry.py | net_gamma_normalized, call_gamma, put_gamma, gamma walls | Both: passes net_gamma_normalized, calculates per-strike gamma scores |
| 3 | delta_volume_exhaustion.py | net_gamma_normalized, regime classification via gamma | Passed-through + regime thresholding |
| 4 | delta_iv_divergence.py | net_gamma_normalized, gamma_density, gamma_regime_score, gamma walls | Both: passes net_gamma_normalized, calculates gamma_density from greeks_summary |
| 5 | iv_gex_divergence.py | net_gamma_normalized, gamma_density, gamma_density_decline, gamma walls, gamma_dir_score | Both: passes net_gamma_normalized, calculates gamma_density + decline score |
| 6 | depth_decay_momentum.py | net_gamma (normalized) | Passed-through via gex_calc.get_normalized_net_gamma() |
| 7 | depth_imbalance_momentum.py | (none directly) | Only receives gex_calc object; no gamma calculation |
| 8 | vamp_momentum.py | (none directly) | Only receives gex_calc; wall proximity via generic `get_walls()` |
| 9 | obi_aggression_flow.py | net_gamma_normalized (via gex_calc) | Passed-through: `gex_calc.get_normalized_net_gamma()` |
| 10 | exchange_flow_concentration.py | (none directly) | Only receives gex_calc; no gamma calculation |
| 11 | exchange_flow_imbalance.py | (none directly) | Only receives gex_calc; no gamma calculation |
| 12 | exchange_flow_asymmetry.py | (none directly) | Only receives gex_calc; no gamma calculation |
| 13 | participant_diversity_conviction.py | net_gamma_normalized (via gex_calc) | Passed-through: `gex_calc.get_normalized_net_gamma()` |
| 14 | participant_divergence_scalper.py | net_gamma_normalized (via gex_calc) | Passed-through: `gex_calc.get_normalized_net_gamma()` |
| 15 | order_book_fragmentation.py | (none directly) | No gamma usage at all |
| 16 | order_book_stacking.py | (none directly) | Receives gex_calc but no gamma calculation |
| 17 | vortex_compression_breakout.py | (none directly) | Receives gex_calc but no gamma calculation |

---

## Detailed Findings

### 1. delta_gamma_squeeze.py

**Gamma types:** `net_gamma_normalized`, `gex_acceleration`, `wall_gex`, `KEY_TOTAL_GAMMA_5M`

- **Line 56–57:** `MIN_WALL_GEX = 500000` — minimum wall GEX threshold
- **Line 73:** `GEX_ACCEL_RATIO = 1.10` — delta acceleration ratio (legacy)
- **Line 75:** `GEX_ACCEL_MIN = 1.05` — minimum GEX acceleration ratio
- **Line 113:** `net_gamma = data.get("net_gamma_normalized", 0)` — **passed through** from orchestrator
- **Line 119:** `walls = gex_calc.get_gamma_walls(threshold=MIN_WALL_GEX)` — fetches gamma walls
- **Lines 259–289:** `_check_gex_acceleration()` — **calculates** GEX acceleration ratio
  - Uses `KEY_TOTAL_GAMMA_5M` rolling window
  - Returns `current / rolling_avg` ratio; >1.0 means accelerating
  - Hard gate: must be ≥ `GEX_ACCEL_MIN` (1.05)
- **Lines 543–544:** Confidence component c5: `c5 = min(1.0, abs(net_gamma) / 2000.0)`
  - **Normalization:** abs(net_gamma) scaled 0→2000, clamped to [0,1]
  - **Intent:** Higher absolute gamma = higher squeeze conviction

**Constants:**
- `MIN_WALL_GEX = 500000`
- `GEX_ACCEL_RATIO = 1.10`
- `GEX_ACCEL_MIN = 1.05`

---

### 2. call_put_flow_asymmetry.py

**Gamma types:** `net_gamma_normalized`, `call_gamma`, `put_gamma`, `net_gamma` (per-strike), gamma walls

- **Line 97:** `gex_calc = data.get("gex_calculator")` — fetches GEX calculator
- **Line 101:** `net_gamma = data.get("net_gamma_normalized", 0)` — **passed through**
- **Lines 170–175:** Calls flow score: `call_score += call_oi * call_gamma * call_delta`
  - **Calculated per-strike:** uses `call_gamma` from greeks_summary
  - Filters: `call_oi > 0 AND call_gamma > 0 AND call_delta > 0.01`
- **Lines 181–184:** Puts flow score: `put_score += put_oi * put_gamma * put_delta`
  - **Calculated per-strike:** uses `put_gamma` from greeks_summary
  - Filters: `put_oi > 0 AND put_gamma > 0 AND put_delta > 0.01`
- **Lines 264–279:** `_compute_regime_intensity(net_gamma)` — regime multiplier
  - `abs(net_gamma) < 200000 → 0.8` (low gamma = less conviction)
  - `abs(net_gamma) > 2000 → 1.3` (high gamma = explosive)
  - Otherwise → 1.0 (baseline)
  - **Note:** The `< 200000` check seems like a bug (should likely be `< 2000` given the `> 2000` branch)
- **Lines 281–310:** `_check_wall_proximity()` — proximity to gamma walls
  - Uses `gex_calc.get_gamma_walls(threshold=500_000)`
  - Bonus: +0.0 to +0.10 when within 0.5% of wall
- **Lines 379, 454, 547:** `regime_mult = self._compute_regime_intensity(net_gamma)` — applied to confidence
- **Lines 494, 587:** `gamma_intensity = round(abs(net_gamma) / 2_000, 3)` — metadata field

---

### 3. delta_volume_exhaustion.py

**Gamma types:** `net_gamma_normalized`, regime classification via gamma thresholds

- **Lines 88–91:** Gamma regime target multipliers:
  - `NEGATIVE_GAMMA_TARGET_MULT = 1.5` (NEG regime: let it run)
  - `POSITIVE_GAMMA_TARGET_MULT = 0.8` (POS regime: quick profits)
  - `NEUTRAL_GAMMA_TARGET_MULT = 1.0` (baseline)
  - `GAMMA_INTENSITY_THRESHOLD = 500000` — threshold for regime classification
- **Line 139:** `net_gamma = data.get("net_gamma_normalized", 0)` — **passed through**
- **Lines 497–514:** `_compute_regime_target_mult(net_gamma, regime)` — selects multiplier based on regime string
- **Lines 559–560:** Confidence c5: `c5 = min(1.0, abs(net_gamma) / 2000.0)`
  - **Normalization:** abs(net_gamma) scaled 0→2000, clamped to [0,1]
- **Lines 570–595:** `_regime_alignment()` — checks if gamma regime supports the trend direction

---

### 4. delta_iv_divergence.py

**Gamma types:** `net_gamma_normalized`, `gamma_density`, `gamma_regime_score`, `gamma_density_decline`, gamma walls

- **Line 71:** `GAMMA_DECLINE_THRESHOLD = 0.70` — gamma density decline threshold
- **Line 111:** `net_gamma = data.get("net_gamma_normalized", 0)` — **passed through**
- **Lines 192–193:** `gamma_score = self._gamma_regime_score(gex_calc, rolling_data, price)` — **calculated**
- **Lines 405–436:** `_gamma_regime_score()` — computes gamma regime score 0.0–1.0
  - Computes `gamma_density` via `_compute_gamma_density()`
  - Reads from `KEY_GAMMA_DENSITY_5M` rolling window
  - `ratio = current / mean_density`; `score = min(1.0, ratio)`
  - Higher score = more stable/high gamma (bullish regime)
- **Lines 484–525:** `_check_gamma_regime()` — hard gate: returns True if gamma density declining
  - Uses `GAMMA_DECLINE_THRESHOLD` (0.70)
  - `ratio = current / mean`; returns `ratio < GAMMA_DECLINE_THRESHOLD`
- **Lines 525–544:** `_compute_gamma_density()` — **calculates** gamma density
  - Sum of `abs(call_gamma) + abs(put_gamma)` for strikes within ±1% of price
  - Uses `gex_calc.get_greeks_summary()`
- **Lines 548–567:** `_get_gamma_density_stats()` — returns (current, mean, decline_pct) for metadata
- **Lines 624–670:** `_check_wall_proximity()` — proximity to gamma walls
  - Uses `gex_calc.get_gamma_walls(threshold=500_000)`
  - Bonus: +0.10 when within `WALL_PROX_PCT` (0.01 = 1%)
- **Lines 707–716:** Confidence c5:
  - If greeks_summary available: `c5 = min(1.0, abs(net_gamma_from_summary) / 1600.0)`
  - Else: `c5 = min(1.0, abs(net_gamma) / 1600.0)`
  - **Normalization:** scaled 0→1600 (not 2000 like other strategies)
  - **Intent:** Bounded gamma scale (typical range ~0–1600)
- **Lines 752–765:** `_regime_confidence()` — regime intensity based on gamma magnitude
  - `gamma_abs > 2000 → 0.10`, `> 1000 → 0.08`, else `0.05`

---

### 5. iv_gex_divergence.py

**Gamma types:** `net_gamma_normalized`, `gamma_density`, `gamma_density_decline`, `gamma_dir_score`, gamma walls, `KEY_GAMMA_DENSITY_5M`

- **Lines 80–86:** Gamma thresholds:
  - `MIN_POSITIVE_GAMMA = 200` (deprecated, kept for backward compat)
  - `MIN_POSITIVE_NORMALIZED_GAMMA = 5.0` — normalized gamma threshold for signal trigger
- **Lines 103–104:** `GAMMA_DENSITY_WINDOW_PCT = 0.01` (±1%), `GAMMA_DENSITY_DECLINE_THRESHOLD = 0.85`
- **Line 140:** `net_gamma = data.get("net_gamma_normalized", 0)` — **passed through**
- **Lines 182, 278:** `normalized_gamma = gex_calc.get_normalized_net_gamma()` — **calculated** via gex_calc
- **Lines 186–187:** `gamma_dir_score = max(0.0, min(1.0, normalized_gamma / 10.0))` — positive gamma contributes to confidence
- **Lines 282–283:** `gamma_dir_score = max(0.0, min(1.0, -normalized_gamma / 10.0))` — negative gamma contributes to SHORT
- **Lines 193–194, 289–290:** `density_score = self._score_gamma_density_decline(...)` — **calculated**
- **Lines 550–586:** `_score_gamma_density_decline()` — gamma density decline score 0.0–1.0
  - `decline_pct = 1.0 - (current_density / rolling_mean)`
  - `score = min(1.0, decline_pct / 0.50)` — 50% decline → 1.0
- **Lines 588–607:** `_compute_gamma_density()` — **calculates** gamma density
  - Sum of `abs(call_gamma) + abs(put_gamma)` for strikes within ±1% of price
- **Lines 607–623:** `_get_gamma_density_data()` — returns (current, mean, decline_pct)
- **Lines 750–751:** Confidence c2: `c2 = min(1.0, abs(net_gamma) / 2000.0)` — **normalized**
- **Lines 753–757:** Confidence c3: `c3 = normalize(wall_gex, 0.0, 2000.0)` — wall GEX scaled 0→2000
  - **Note:** Comment says wall GEX from 0→5M, but normalization uses 2000
- **Lines 791–795:** c10 (gamma direction score) — partially redundant with c2, weight halved via reduced denominator (÷9.5 instead of ÷10)
- **Lines 843–847:** `_gamma_magnitude_confidence()` — `min(0.10, 0.10 * min(1.0, abs_gamma / 2000))`
- **Lines 859–868:** `_regime_intensity_confidence()` — `0.05 + 0.10 * min(1.0, abs_gamma / 2000)`

---

### 6. depth_decay_momentum.py

**Gamma types:** `net_gamma` (via `get_normalized_net_gamma()`)

- **Line 76:** `gex_calc = data.get("gex_calculator")` — receives gex_calc
- **Lines 334–338:** GEX regime alignment (c5):
  ```python
  net_gamma = 0
  if gex_calc and regime:
      net_gamma = gex_calc.get_normalized_net_gamma() if hasattr(gex_calc, "get_normalized_net_gamma") else 0
  c5 = min(1.0, abs(net_gamma) / 2000.0)
  ```
  - **Normalization:** abs(net_gamma) scaled 0→2000, clamped to [0,1]
  - **Intent:** Higher absolute gamma = higher conviction (component weight ~0.20 as part of 5-component average)

---

### 7. depth_imbalance_momentum.py

**Gamma types:** None directly

- **Line 77:** `gex_calc = data.get("gex_calculator")` — receives gex_calc object
- **Line 169:** Passes gex_calc to confidence function
- **No gamma calculation or usage** — gex_calc is passed but never used for gamma values in this file

---

### 8. vamp_momentum.py

**Gamma types:** None directly

- **Line 79:** `gex_calc = data.get("gex_calculator")` — receives gex_calc
- **Lines 329–330:** `_wall_proximity_score()` — checks proximity to gamma wall
  - Uses `gex_calc.get_walls()` (generic, not gamma-specific)
  - **Note:** Uses `get_walls()` not `get_gamma_walls()` — may return different data
- **No gamma calculation or normalized gamma usage**

---

### 9. obi_aggression_flow.py

**Gamma types:** `net_gamma_normalized` (via gex_calc)

- **Line 78:** `gex_calc = data.get("gex_calculator")` — receives gex_calc
- **Lines 260–285:** `_gex_regime_alignment()` — determines if GEX regime supports signal direction
  - Uses `gex_calc.get_normalized_net_gamma()` — **passed through**
  - `net_gamma > 0` → positive GEX regime (bullish bias: dealers buy dips)
  - `net_gamma < 0` → negative GEX regime (bearish bias: dealers sell dips)
  - Returns: 1.0 (aligned), 0.5 (neutral), 0.0 (opposed)
- **Lines 343–347:** c7 = `_gex_regime_alignment(regime, gex_calc, direction)` — component weight 0.15 in 7-component weighted average

---

### 10. exchange_flow_concentration.py

**Gamma types:** None directly

- **Line 84:** `gex_calc = data.get("gex_calculator")` — receives gex_calc
- **Line 170:** Passes gex_calc to confidence function
- **No gamma calculation or usage** — gex_calc is passed but never accessed

---

### 11. exchange_flow_imbalance.py

**Gamma types:** None directly

- **Line 92:** `gex_calc = data.get("gex_calculator")` — receives gex_calc
- **Line 206:** Passes gex_calc to confidence function
- **No gamma calculation or usage** — gex_calc is passed but never accessed

---

### 12. exchange_flow_asymmetry.py

**Gamma types:** None

- **No gamma usage at all** — no gex_calc received, no gamma references

---

### 13. participant_diversity_conviction.py

**Gamma types:** `net_gamma_normalized` (via gex_calc)

- **Line 92:** `gex_calc = data.get("gex_calculator")` — receives gex_calc
- **Lines 371–386:** c7 GEX alignment (weight 0.15):
  ```python
  net_gamma = 0.0
  if gex_calc and hasattr(gex_calc, "get_normalized_net_gamma"):
      net_gamma = gex_calc.get_normalized_net_gamma()
  if direction == "LONG":
      if net_gamma > 0.01: c7 = 1.0
      elif net_gamma < -0.01: c7 = 0.2
      else: c7 = 0.5
  else:
      if net_gamma < -0.01: c7 = 1.0
      elif net_gamma > 0.01: c7 = 0.2
      else: c7 = 0.5
  ```
  - **Passed-through:** `gex_calc.get_normalized_net_gamma()`
  - **Threshold:** ±0.01 for binary alignment
  - **Returns:** 1.0 (aligned), 0.5 (neutral), 0.2 (opposed)

---

### 14. participant_divergence_scalper.py

**Gamma types:** `net_gamma_normalized` (via gex_calc)

- **Line 96:** `gex_calc = data.get("gex_calculator")` — receives gex_calc
- **Lines 496–511:** c7 GEX regime alignment (weight 0.15):
  - Identical logic to participant_diversity_conviction.py
  - Uses `gex_calc.get_normalized_net_gamma()`
  - Threshold: ±0.01 for binary alignment
  - Returns: 1.0 (aligned), 0.5 (neutral), 0.2 (opposed)

---

### 15. order_book_fragmentation.py

**Gamma types:** None

- **No gamma usage at all** — no gex_calc received, no gamma references

---

### 16. order_book_stacking.py

**Gamma types:** None directly

- **Line 188:** `gex_calc = data.get("gex_calculator", {})` — receives gex_calc (defaults to empty dict)
- **Line 223:** Passes gex_calc to confidence function
- **No gamma calculation or usage** — gex_calc is passed but never accessed for gamma values

---

### 17. vortex_compression_breakout.py

**Gamma types:** None directly

- **Line 90:** `gex_calc = data.get("gex_calculator")` — receives gex_calc
- **Line 177:** Passes gex_calc to confidence function
- **No gamma calculation or usage** — gex_calc is passed but never accessed

---

## Cross-File Normalization Patterns

### Normalization Ranges for `abs(net_gamma)`:

| Strategy | Normalization Formula | Range |
|----------|----------------------|-------|
| delta_gamma_squeeze | `min(1.0, abs(net_gamma) / 2000.0)` | 0→2000 |
| delta_volume_exhaustion | `min(1.0, abs(net_gamma) / 2000.0)` | 0→2000 |
| delta_iv_divergence | `min(1.0, abs(net_gamma) / 1600.0)` | 0→1600 |
| iv_gex_divergence | `min(1.0, abs(net_gamma) / 2000.0)` | 0→2000 |
| depth_decay_momentum | `min(1.0, abs(net_gamma) / 2000.0)` | 0→2000 |

**Inconsistency:** delta_iv_divergence uses 1600 as the upper bound, while all others use 2000.

### Gamma Wall Threshold:

| Strategy | Threshold |
|----------|-----------|
| delta_gamma_squeeze | 500,000 (MIN_WALL_GEX constant) |
| call_put_flow_asymmetry | 500,000 (hardcoded) |
| delta_iv_divergence | 500,000 (hardcoded) |
| delta_volume_exhaustion | 500,000 (GAMMA_INTENSITY_THRESHOLD constant) |
| iv_gex_divergence | 500,000 (hardcoded) |

All use the same 500K threshold for `get_gamma_walls()`.

### Gamma Density Calculation (shared pattern):

Two strategies independently implement gamma density:
- **delta_iv_divergence:** `_compute_gamma_density()` — sum of `abs(call_gamma) + abs(put_gamma)` within ±1% of price
- **iv_gex_divergence:** `_compute_gamma_density()` — identical logic

Both use `KEY_GAMMA_DENSITY_5M` rolling window for historical comparison.

### Gamma Regime Classification:

| Strategy | Source | Method |
|----------|--------|--------|
| delta_volume_exhaustion | `net_gamma_normalized` | Regime string from orchestrator (NEG/POS/NEUTRAL) |
| call_put_flow_asymmetry | `net_gamma_normalized` | Magnitude-based multiplier (0.8/1.0/1.3) |
| delta_iv_divergence | `gamma_density` rolling | Density decline ratio vs mean |
| iv_gex_divergence | `get_normalized_net_gamma()` | Sign-based direction score |
| obi_aggression_flow | `get_normalized_net_gamma()` | Sign-based alignment (1.0/0.5/0.0) |
| depth_decay_momentum | `get_normalized_net_gamma()` | Magnitude-based (0→2000) |
| participant_* | `get_normalized_net_gamma()` | Sign-based alignment (1.0/0.5/0.2) |

---

## Key Observations

1. **No `sum_pos_gamma` or `sum_neg_gamma`** — these are not calculated anywhere in layer2. Gamma is always used as `net_gamma` (signed) or `net_gamma_normalized`.

2. **Pass-through dominant** — Most strategies receive `net_gamma_normalized` from the orchestrator via `data.get("net_gamma_normalized", 0)`. Only 3 files actually *calculate* gamma values:
   - `delta_gamma_squeeze.py` — GEX acceleration ratio
   - `call_put_flow_asymmetry.py` — per-strike gamma flow scores
   - `delta_iv_divergence.py` — gamma density
   - `iv_gex_divergence.py` — gamma density + decline score

3. **gex_calc usage patterns:**
   - `get_normalized_net_gamma()` — 6 strategies use this
   - `get_gamma_walls(threshold=500_000)` — 5 strategies use this
   - `get_greeks_summary()` — 2 strategies use this for per-strike gamma
   - `get_walls()` — 1 strategy (vamp_momentum) uses this generic variant
   - Many strategies receive `gex_calc` but never use it (depth_imbalance, exchange_flow_concentration, exchange_flow_imbalance, order_book_stacking, vortex_compression)

4. **Consistent confidence component pattern** — gamma magnitude is typically component c5 (or c7 in weighted schemes), normalized to [0,1] with a 2000 upper bound.

5. **Bug candidate:** `call_put_flow_asymmetry.py` line 273 checks `abs(net_gamma) < 200000` before line 275 checks `abs(net_gamma) > 2000`. Since 200000 > 2000, the `> 2000` branch is unreachable when `abs(net_gamma) >= 200000`, and the `< 200000` branch catches everything below 200000. This likely should be `< 2000` instead of `< 200000`.
