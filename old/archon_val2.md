# Syngex Codebase Validation Report — Archon Val2

**Date:** 2026-05-12  
**Auditor:** Archon (Sr SDE Hat)  
**Scope:** Full codebase validation — strategies, data streams, Tradestation integration, logic correctness  
**Path:** `/home/hologaun/projects/syngex/`

---

## Executive Summary

| Metric | Count |
|--------|-------|
| **Total Python files** | ~40 |
| **Total strategies** | 41 (8 Layer1 + 17 Layer2 + 4 Layer3 + 12 FullData) |
| **Critical Issues** | 3 |
| **High Issues** | 7 |
| **Medium Issues** | 9 |
| **Low Issues** | 12 |
| **Dead Code** | 5 |
| **Missing Integrations** | 4 |

---

## 1. CRITICAL ISSUES (Must Fix Before Production)

### C1. Market Depth Streams Are No-Op Stubs — Strategies Starved of L2 Data

**Severity:** CRITICAL  
**Files:** `ingestor/tradestation_client.py` (lines ~75-86)

```python
def subscribe_to_market_depth_quotes(self, symbol: str) -> None:
    """...depth data is derived from the regular quote stream..."""
    logger.debug("Market-depth-quotes subscription for %s (no-op stub)", symbol)

def subscribe_to_market_depth_aggregates(self, symbol: str) -> None:
    """...depth data is derived from the regular quote stream..."""
    logger.debug("Market-depth-aggregates subscription for %s (no-op stub)", symbol)
```

**Impact:** 14+ Layer2 strategies depend on `market_depth_agg` and `market_depth_quotes` data that is NEVER populated:

- `ObiAggressionFlow` — uses `aggressive_buy_vol`, `aggressive_sell_vol`
- `VampMomentum` — uses `vamp_depth_density`, participant counts
- `DepthDecayMomentum` — uses `depth_decay_bid/ask`, `depth_top5_bid/ask`
- `DepthImbalanceMomentum` — uses `imbalance_ratio`, participant counts
- `ExchangeFlowConcentration` — uses `vsi_combined`, `iex_intent`
- `ExchangeFlowImbalance` — uses `aggressor_vsi`, `memx_vsi`, `bats_vsi`
- `ExchangeFlowAsymmetry` — uses `esi_memx`, `esi_bats`, venue baselines
- `OrderBookFragmentation` — uses `fragility_bid/ask`, `decay_velocity`
- `OrderBookStacking` — uses `sis_bid/ask`
- `ParticipantDiversityConviction` — uses `bid_participants`, `bid_exchanges`
- `ParticipantDivergenceScalper` — uses `fragility_bid/ask`, `top_wall_bid/ask`
- `VortexCompressionBreakout` — uses `spread_zscore`, `liquidity_density`
- `GhostPremium` — uses `pdr` (PDR requires depth data)
- `IronAnchor` — uses `liq_wall_size`, `liq_wall_sigma`

**Root Cause:** The TradeStation HTTP streaming API does not have dedicated market-depth endpoints. The `subscribe_to_market_depth_*` methods are documented as no-op stubs. However, the orchestrator never populates `market_depth_agg` or `market_depth_quotes` in the data dict passed to strategies. The strategies check `data.get("market_depth_agg", {})` and get empty dicts, causing these strategies to silently return `[]` (no signals).

**Fix Required:** Either:
1. Implement actual market-depth parsing from the quotes stream (Bid/Ask sizes, participant counts per level) and populate `market_depth_agg`/`market_depth_quotes` in the data dict
2. Or disable/unregister the L2 strategies until real depth data is available

---

### C2. Double NetGammaFilter Registration — Signal Blocked Twice

**Severity:** CRITICAL  
**File:** `main.py` (lines ~330-350)

```python
# First registration (Phase 0)
self._gamma_filter = NetGammaFilter(flip_buffer=0.5)
self._strategy_engine.register_filter(self._gamma_filter.evaluate_signal)

# ... later ...

# Second registration — creates NEW filter, registers AGAIN
filter_config = self._strategy_config.get("filter", {})
net_gamma_cfg = filter_config.get("net_gamma", {})
if net_gamma_cfg.get("enabled", True):
    flip_buffer = net_gamma_cfg.get("params", {}).get("flip_buffer", 0.5)
    self._gamma_filter = NetGammaFilter(flip_buffer=flip_buffer)  # NEW instance
    self._strategy_engine.register_filter(self._gamma_filter.evaluate_signal)  # REGISTERED AGAIN
```

**Impact:** The strategy engine has TWO identical filter callbacks registered. Every signal is evaluated twice by the same logic. This is wasteful and the second registration overwrites the first instance's state (flip_buffer from config is applied to the new instance, but the old instance is never used).

**Fix Required:** Remove the first registration. Only create and register the filter once, using config values from the start.

---

### C3. Dead Strategy Imports — Never Registered with Engine

**Severity:** CRITICAL  
**Files:** `main.py` imports, `strategies/layer2/__init__.py`

The following strategies are imported in `main.py` but NEVER registered with the strategy engine:

| Strategy | File |
|----------|------|
| `ExtrinsicFlow` | `strategies/full_data/extrinsic_flow.py` |
| `GhostPremium` | `strategies/full_data/ghost_premium.py` |
| `SkewDynamics` | `strategies/full_data/skew_dynamics.py` |
| `SmileDynamics` | `strategies/full_data/smile_dynamics.py` |
| `GammaBreaker` | `strategies/full_data/gamma_breaker.py` |
| `IronAnchor` | `strategies/full_data/iron_anchor.py` |
| `SentimentSync` | `strategies/full_data/sentiment_sync.py` |
| `WhaleTracker` | `strategies/full_data/whale_tracker.py` |
| `VortexCompressionBreakout` | `strategies/layer2/vortex_compression_breakout.py` |

**Impact:** 9 fully-implemented strategies exist in the codebase but produce ZERO signals because they are never registered. The `_register_strategies_from_config()` method only registers strategies from the `layer1`, `layer2`, `layer3`, and `full_data` keys in the YAML config. The `layer2` YAML key only lists 16 strategies (not 17), and `full_data` only lists 4 strategies (not 12).

**Fix Required:** Either:
1. Add missing strategy entries to `config/strategies.yaml` under their respective layers
2. Or remove dead strategy files

---

## 2. HIGH ISSUES (Should Fix Before Production)

### H1. Confidence Filter Applied Twice — Premature Signal Loss

**Severity:** HIGH  
**File:** `strategies/engine.py` — `process()` method

```python
# Phase 1: Confidence check in engine loop
if signal.confidence < self.config.min_confidence:
    continue  # Signal dropped here

# Phase 2: Regime filter
if self._filter_callback:
    filtered = [s for s in all_signals if self._filter_callback(s)]
```

**Impact:** Signals that pass the strategy's own `min_confidence` check but fall below the engine's global `min_confidence` (0.35 from YAML) are silently dropped BEFORE the regime filter runs. This means:
- A signal with confidence 0.33 passes the strategy's check but is dropped by the engine
- The regime filter never sees it — we can't tell if it would have been regime-correct
- Signal loss is invisible in logs

**Fix Required:** Apply regime filter FIRST, then apply engine-level confidence threshold. This preserves the signal flow: `Strategy → Regime Filter → Confidence → Dedup`.

---

### H2. Strategy Evaluation Timing Bug

**Severity:** HIGH  
**File:** `main.py` — `run()` method

```python
# Strategy evaluation (every ~1s)
if now - self._profile_timer >= 1.0:
    self._evaluate_strategies()
```

**Impact:** `self._profile_timer` is reset every 5 seconds in the profile reporting block. The strategy evaluation condition `now - self._profile_timer >= 1.0` will only be true once per 5-second cycle (right after the profile timer resets), not every 1 second. Strategies effectively evaluate every 5 seconds, not every 1 second.

**Fix Required:** Use a separate timer variable for strategy evaluation:
```python
self._eval_timer: float = 0.0
# ...
if now - self._eval_timer >= 1.0:
    self._evaluate_strategies()
    self._eval_timer = now
```

---

### H3. ExtrinsicIntrinsicFlow Hardcoded MIN_NET_GAMMA Overrides YAML

**Severity:** HIGH  
**File:** `strategies/full_data/extrinsic_intrinsic_flow.py`

```python
# Module-level constant — NOT configurable
MIN_NET_GAMMA = 500000.0
```

**Impact:** The strategy checks `if net_gamma < MIN_NET_GAMMA: return []` but `MIN_NET_GAMMA` is a hardcoded module constant. The YAML config has no `min_net_gamma` parameter for this strategy. Changing the threshold requires code modification, not config edit.

**Fix Required:** Read from YAML params: `min_net_gamma = params.get("min_net_gamma", 500000.0)`

---

### H4. Config Hot-Reload Can't Modify Private Attributes

**Severity:** HIGH  
**File:** `main.py` — `_reload_config()` method

```python
# This silently fails — flip_buffer is a private attribute
self._gamma_filter.flip_buffer = params["flip_buffer"]
```

**Impact:** The `NetGammaFilter` class stores `flip_buffer` as a private attribute (`self._flip_buffer`). The hot-reload code tries to set `self._gamma_filter.flip_buffer` which creates a new public attribute but doesn't update the private one used by the filter logic. Config changes to `flip_buffer` are silently ignored.

**Fix Required:** Add a public setter method `set_flip_buffer()` to `NetGammaFilter`, or make `flip_buffer` a public attribute.

---

### H5. ExtrinsicIntrinsicFlow Short Target Uses Wrong Signal Type

**Severity:** HIGH  
**File:** `strategies/full_data/extrinsic_intrinsic_flow.py` — `_check_short()`

```python
# BUG: Passes "expansion" for SHORT signal type
target = self._compute_iv_scaled_target(price, risk, rolling_data, "expansion")
```

**Impact:** The SHORT signal should use `"short"` or `"fade"` as the signal type for IV-scaled target computation. Using `"expansion"` means SHORT signals get the same (LONG) target multiplier, which may be too aggressive for short positions.

**Fix Required:** Pass `"short"` as the signal type to `_compute_iv_scaled_target()`.

---

### H6. Heatmap YAML References Unregistered Strategies

**Severity:** HIGH  
**File:** `config/heatmap.yaml`

The heatmap grid references strategies not in the YAML config's `layer2` section:
- `exchange_flow_asymmetry` — listed in heatmap but NOT in `layer2` YAML config
- `order_book_fragmentation` — listed in heatmap but NOT in `layer2` YAML config  
- `order_book_stacking` — listed in heatmap but NOT in `layer2` YAML config
- `vortex_compression_breakout` — listed in heatmap but NOT in `layer2` YAML config

**Impact:** These strategies will show in the heatmap but never produce signals. The heatmap will show them as permanently "idle" with 0 signals.

**Fix Required:** Add these strategies to `config/strategies.yaml` under `layer2`, or remove from heatmap.

---

### H7. Rolling Window Trend Detection Too Sensitive

**Severity:** HIGH  
**File:** `strategies/rolling_window.py` — `trend` property

```python
if diff / std > 0.5:
    return "UP"
elif diff / std < -0.5:
    return "DOWN"
```

**Impact:** A 0.5σ difference between first-half and second-half means is extremely sensitive. For a 300-second window with normal market noise, the trend will flip-flop constantly. Strategies relying on `trend` for signal gating (e.g., `ExtrinsicIntrinsicFlow` checking `vol_trend == "UP"`) will see inconsistent results.

**Fix Required:** Increase threshold to 1.0σ or 1.5σ, or use a more robust trend detection method.

---

## 3. MEDIUM ISSUES (Should Fix)

### M1. NetGammaFilter.update_regime Accesses Private Attribute

**Severity:** MEDIUM  
**File:** `main.py` — `_evaluate_strategies()`

```python
self._gamma_filter.flip_buffer = params["flip_buffer"]
```

The hot-reload tries to set `flip_buffer` but the class stores it as `_flip_buffer`. No setter exists.

---

### M2. Signal ID Collision Risk

**Severity:** MEDIUM  
**File:** `strategies/signal_tracker.py`

```python
signal_id = f"{signal['strategy_id']}_{int(signal['timestamp']*1000)}_{uuid.uuid4().hex[:8]}"
```

Uses millisecond-precision timestamp + UUID. Collision is extremely unlikely but not impossible. For a high-frequency system, consider using a monotonically increasing counter instead.

---

### M3. Heatmap Dashboard Lacks Strategy Health Details

**Severity:** MEDIUM  
**File:** `app_heatmap.py`

The heatmap only tracks `win_rate` and `pnl` from disk. It does NOT track:
- Signal count accuracy (relies on JSONL file reads which can be slow)
- Strategy-specific error rates
- Time-to-resolution distribution
- Per-strategy confidence distribution

---

### M4. Data Race on Shared JSON File

**Severity:** MEDIUM  
**Files:** `main.py` (writes), `app_dashboard.py` / `app_heatmap.py` (reads)

```python
# Orchestrator writes
with open(self._data_file, "w") as f:
    json.dump(state, f)

# Dashboard reads
with open(DATA_FILE, "r") as f:
    content = f.read().strip()
```

If the dashboard reads while the orchestrator is writing, it may get a partial/corrupt JSON. No file locking is used.

**Fix Required:** Write to a temp file, then atomically rename. Or use file locking.

---

### M5. VolumeFilter Not Used by StrategyEngine

**Severity:** MEDIUM  
**File:** `strategies/volume_filter.py`

The `VolumeFilter` class exists and is well-implemented, but it is:
1. Never imported in `main.py`
2. Never registered as a filter in the StrategyEngine
3. Never called anywhere in the codebase

**Impact:** Dead code. The volume confirmation filter is implemented but never active.

---

### M6. GEXCalculator OI Values Are Relative, Not Absolute

**Severity:** MEDIUM  
**File:** `engine/gex_calculator.py` — `_StrikeBucket` docstring

```
Note: OI values from stream greeks are **relative** (not absolute
contract counts). The stream does not include real open interest —
OI defaults to 1.0 per message.
```

**Impact:** Strategies that use OI-dependent logic (e.g., `CallPutFlowAsymmetry` flow ratios, `ProbWeightedMagnet` OI concentration) are working with relative ratios, not real contract counts. This is acknowledged but could produce misleading signals if the relative values don't correlate well with real OI.

**Fix Required:** Add periodic OI fetching from the REST API to calibrate relative values.

---

### M7. ExtrinsicFlow Confidence Volume Component Log Scale

**Severity:** MEDIUM  
**File:** `strategies/full_data/extrinsic_flow.py` — `_compute_confidence()`

```python
conf_volume = min(0.15, 0.15 * min(1.0, math.log1p(phi_total) / 10.0))
```

The log scale compresses high volume values. A phi_total of 1,000,000 and 10,000,000 both map to nearly the same confidence component (~0.15). This reduces discriminative power for extreme volume events.

---

### M8. Conflict Detection Uses 5-Second Windows — Too Coarse for L3

**Severity:** MEDIUM  
**File:** `strategies/engine.py` — `_detect_conflicts()`

```python
window_key = int(sig.timestamp / 5.0)
```

Layer 3 strategies (1Hz micro-signals) operate at sub-second granularity. A 5-second conflict window groups 5 signals together, potentially suppressing legitimate rapid-fire signals from different strategies.

---

### M9. Missing Error Handling in _process_raw_option_chain

**Severity:** MEDIUM  
**File:** `engine/gex_calculator.py`

The `_process_raw_option_chain` method is called as a fallback but is not shown in the read output. If it has insufficient error handling, a malformed option chain response could crash the message processing loop.

---

## 4. LOW ISSUES (Nice to Fix)

### L1. Hardcoded Constants in Strategy Files

Multiple strategy files have hardcoded constants at module level that should be in YAML:
- `extrinsic_intrinsic_flow.py`: `MIN_NET_GAMMA = 500000.0`
- `extrinsic_intrinsic_flow.py`: `STOP_PCT = 0.005`
- `gamma_wall_bounce.py`: Various hardcoded thresholds

### L2. Logging Verbosity

The orchestrator suppresses noisy loggers but the strategy evaluation logs can be very verbose during high-activity periods. Consider adaptive logging levels.

### L3. No Integration Tests

The codebase has no test files. All strategy logic, data flow, and filtering should have unit tests.

### L4. No Schema Validation for TradeStation Responses

The `TradeStationClient` parses raw JSON without schema validation. A change in the TradeStation API response format could silently break parsing.

### L5. Heatmap Template File Not Shown

`app_heatmap.py` references `render_template("heatmap.html")` but the HTML template file was not in the audit scope. Verify it exists and is correct.

### L6. No Rate Limiting on Signal Output

The engine has `max_signals_per_tick` but no rate limiting across ticks. A strategy could fire every tick for 60 seconds (dedup window), producing up to 60 signals.

### L7. Phi Accumulator Crash Recovery

The `_load_phi_accumulators()` / `_save_phi_accumulators()` methods provide crash recovery for extrinsic flow tracking, but the file I/O is not atomic. A crash during save could corrupt the state file.

### L8. No Health Check Endpoint

The heatmap Flask app has no `/health` endpoint for monitoring systems to verify the dashboard is running.

### L9. Streamlit Spinner Blocks Main Thread

In `app_dashboard.py`, the spinner while loop (`while state is None: time.sleep(1)`) blocks the Streamlit main thread. This is a known Streamlit anti-pattern.

### L10. No Graceful Degradation for Missing Strategy Config

If a strategy is in the heatmap YAML but not in the strategies YAML, the heatmap will show it as idle with no indication why.

### L11. `_compute_linear_slope` Is Unused

The `_compute_linear_slope()` function in `main.py` is defined but never called. Dead code.

### L12. Module-Level Imports in Strategy Files

Several strategy files use `from strategies.engine import BaseStrategy` with relative-style paths. These work but could be cleaner with relative imports.

---

## 5. TRADESTATION INTEGRATION VALIDATION

### 5.1 Data Stream Coverage

| Stream | Status | Notes |
|--------|--------|-------|
| Quotes (underlying price) | ✅ Active | `subscribe_to_quotes()` — feeds `underlying_update` |
| Option Chain | ✅ Active | `subscribe_to_option_chain()` — feeds `option_update` |
| Market Depth Quotes (L2) | ❌ Stub | No-op, no data populated |
| Market Depth Aggregates | ❌ Stub | No-op, no data populated |
| TotalView (order flow) | ❌ Not Implemented | No TotalView endpoint or parsing |
| BATS venue data | ❌ Not Implemented | No venue-level data in streams |

### 5.2 Data Normalization

The `TradeStationClient._extract_contracts()` method normalizes raw option chain JSON into `option_update` messages. Key fields extracted:
- `symbol`, `strike`, `gamma`, `open_interest`, `side`, `underlying_price`

**Gap:** The normalization does NOT extract:
- `delta`, `theta`, `vega`, `iv` (implied volatility) — these are in the stream but not extracted
- `volume` per contract
- `bid`/`ask` prices per option
- Venue/exchange information (BATS, MEMX, IEX)

### 5.3 GEXCalculator Processing

The `GEXCalculator.process_message()` method handles:
1. `underlying_update` messages → updates `self.underlying_price`
2. `option_update` messages → updates `_StrikeBucket` for the strike
3. Raw TradeStation quotes → extracts underlying price
4. Raw option-chain contracts → infers strike/side
5. Stream greeks objects → infers strike/side from greeks

**Issue:** The GEXCalculator accumulates gamma × OI products per message. Since OI defaults to 1.0 per message (relative), the cumulative gamma values grow linearly with message count. The calculator provides both `get_net_gamma()` (cumulative) and `get_normalized_net_gamma()` (per-message average). Strategies should use the normalized version.

---

## 6. STRATEGY REGISTRATION AUDIT

### 6.1 YAML Config vs Engine Registration

| Layer | YAML Config | Registered | Missing |
|-------|-------------|------------|---------|
| Layer 1 | 8 | 8 | None |
| Layer 2 | 16 | 16 | None (but 4 more exist as files) |
| Layer 3 | 4 | 4 | None |
| Full Data | 4 | 4 | 8 (GhostPremium, SkewDynamics, SmileDynamics, ExtrinsicFlow, GammaBreaker, IronAnchor, SentimentSync, WhaleTracker) |

### 6.2 Heatmap vs YAML Config

The heatmap YAML references strategies not in the strategies YAML:
- `exchange_flow_asymmetry` — in heatmap, NOT in strategies YAML
- `order_book_fragmentation` — in heatmap, NOT in strategies YAML
- `order_book_stacking` — in heatmap, NOT in strategies YAML
- `vortex_compression_breakout` — in heatmap, NOT in strategies YAML

---

## 7. RECOMMENDATIONS

### Priority 1 (Before Any Live Trading)
1. **Fix C1:** Implement real market depth data population or disable L2 strategies
2. **Fix C2:** Remove duplicate NetGammaFilter registration
3. **Fix C3:** Register all 9 missing strategies or remove dead files
4. **Fix H2:** Fix strategy evaluation timing

### Priority 2 (Before Backtesting)
5. **Fix H1:** Reorder filter chain (regime → confidence → dedup)
6. **Fix H3:** Make MIN_NET_GAMMA configurable
7. **Fix H4:** Add flip_buffer setter to NetGammaFilter
8. **Fix H5:** Correct SHORT signal target computation

### Priority 3 (Before Scaling)
9. **Fix H7:** Increase rolling window trend threshold
10. **Fix M4:** Add file locking for shared JSON state
11. **Fix M5:** Either use VolumeFilter or remove it
12. **Add tests:** Unit tests for strategy evaluation, GEX calculation, filter logic

---

## 8. ARCHITECTURAL NOTES

### Strengths
- Clean separation of concerns: ingestor → calculator → engine → strategies → dashboard
- Config-driven strategy registration allows hot-reload of parameters
- Signal outcome tracking with persistence (JSONL) supports backtesting
- Multi-layer strategy architecture (structural → alpha → micro → full-data)
- Conflict detection and resolution between contradictory signals
- NetGamma regime filter provides market-context awareness

### Areas for Improvement
- No data validation layer between ingestor and calculator
- No circuit breaker for cascading strategy failures
- No performance monitoring (signal rate, processing latency)
- Dashboard processes (Streamlit, Flask) have no health checks
- No A/B testing framework for strategy comparison

---

*Report generated by Archon — 2026-05-12 04:00 PDT*
