# Rolling Confidence Calculator — Design Spec

**Date:** 2026-05-28  
**Status:** Final  
**Owner:** Archon → Forge (implementation)
**Scope:** Layer 1 + Layer 2 strategies only (25 total). L3 and full_data excluded from this rollout.

---

## 1. Problem

Strategy confidence scores are computed **once per signal emission** (at entry time). They don't reflect how the signal's conviction evolves as market conditions change. This means:

- We can't see if a signal's confidence is **rising** (thesis strengthening) or **falling** (thesis weakening)
- We can't use confidence as a **live exit trigger** (e.g., exit if drops below 20% after hold time)
- The dashboard shows only the **entry confidence** — no live view of signal strength

## 2. Goal

Compute a **live rolling confidence score** for each strategy, updated every second, displayed on the dashboard heatmap. This is **display-only** — no trading decisions yet.

### Requirements

- [ ] Rolling confidence computed at **1Hz** (every second)
- [ ] **10-second rolling window** with smoothing to prevent whipsaws
- [ ] Displayed on each strategy's heatmap tile, between `last:` and `pnl`
- [ ] **Display only** — no action taken on rolling confidence values
- [ ] Works across all 25 L1+L2 strategies
- [ ] Each strategy gets **1 task** with validation + commit between tasks

## 3. Architecture

```
main.py orchestrator
    │
    ├──► StrategyEngine.process() → signals (existing)
    │
    └──► RollingConfidenceCalculator.compute_all()  [NEW]
              │
              ├──► strategy.evaluate(data)  [reuse same data dict]
              │        │
              │        ▼
              │     Signal(confidence=0.xx, ...)
              │
              ├──► RollingWindow.push(signal.confidence)
              │
              ▼
         smoothed = window.mean
         added to health dict → gex_state_{SYMBOL}.json
              │
              ▼
    app_heatmap.py → SocketIO → heatmap.html
              │
              ▼
    Footer: "Last: 9:30  40%  +$40"
```

### Why call `evaluate()` for confidence?

Each strategy computes confidence differently — `gamma_wall_bounce` uses proximity + GEX strength + rejection score, `confluence_reversal` uses a 4-component formula, `magnet_accelerate` has `_phase1_confidence()` and `_phase2_confidence()`. There is no single confidence formula.

The calculator calls `evaluate()` with the same data dict the main loop already passes. For strategies that produce no signal (confidence below threshold), it returns `None` — which is the "no live confidence" case.

## 4. Component Design

### 4.1 `strategies/rolling_confidence.py` (NEW)

```python
class RollingConfidenceCalculator:
    """
    Computes live rolling confidence for all registered strategies.
    
    For each strategy, at ~1Hz:
    1. Calls strategy.evaluate(data) with current market state
    2. Extracts confidence from returned Signal(s)
    3. Pushes to a 10-second RollingWindow
    4. Returns smoothed confidence % or None
    """
    
    def __init__(self, strategies: List[BaseStrategy]):
        self.strategies = strategies
        self.windows: Dict[str, RollingWindow] = {}
        for s in strategies:
            self.windows[s.strategy_id] = RollingWindow(
                window_type="time", window_size=10
            )
    
    def compute_all(self, data: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """
        Compute rolling confidence for all strategies.
        
        Args:
            data: Same market state dict passed to strategy.evaluate()
            
        Returns:
            Dict[str, Optional[float]] — strategy_id → smoothed confidence % (0-100) or None
        """
        results = {}
        for strategy in self.strategies:
            if not strategy.enabled:
                continue
            
            conf = self._get_confidence(strategy, data)
            
            if conf is None:
                results[strategy.strategy_id] = None
                continue
            
            window = self.windows[strategy.strategy_id]
            window.push(conf, data.get("timestamp", time.time()))
            
            smoothed = window.mean if window.mean is not None else conf
            results[strategy.strategy_id] = round(smoothed * 100, 1)  # percentage
        
        return results
    
    def _get_confidence(self, strategy: BaseStrategy, data: Dict[str, Any]) -> Optional[float]:
        """
        Get confidence from a strategy by calling evaluate() and reading Signal confidence.
        
        For strategies that produce no signal (confidence below threshold),
        returns None — the dashboard will show "—".
        
        For strategies with multiple signals, uses the highest confidence.
        """
        try:
            signals = strategy.evaluate(data)
            if not signals:
                return None
            # Return highest confidence signal
            return max(s.confidence for s in signals)
        except Exception:
            return None
```

### 4.2 Integration with `main.py`

The heatmap data flows through `main.py` → `gex_state_{SYMBOL}.json` → `app_heatmap.py` → `templates/heatmap.html`.

**Changes to `main.py`:**
1. Instantiate `RollingConfidenceCalculator` in `initialize()`
2. Call `compute_all()` in `_evaluate_strategies()` after strategy evaluation
3. Add rolling confidence to `_build_strategy_health()` output

**Changes to `app_heatmap.py`:**
- Pass rolling confidence through the JSON payload (already handled by `_build_strategy_health`)
- No changes needed to the server — it reads from the JSON file

**Changes to `templates/heatmap.html`:**
Update the card footer to include rolling confidence between `Last:` and PnL:

**Current footer:**
```html
<div class="card-footer">
    <span class="card-last" id="last-${s.id}">Last: --:--</span>
    <span class="card-pnl neutral" id="pnl-${s.id}">$0</span>
</div>
```

**New footer:**
```html
<div class="card-footer">
    <span class="card-last" id="last-${s.id}">Last: --:--</span>
    <span class="card-conf" id="conf-${s.id}">—</span>
    <span class="card-pnl neutral" id="pnl-${s.id}">$0</span>
</div>
```

**JavaScript update in `updateDashboard()`:**
```javascript
// Rolling confidence display in footer
const rollingConf = strat.rolling_confidence;
const confEl = document.getElementById(`conf-${id}`);
if (rollingConf !== undefined && rollingConf !== null) {
    const pct = `${Math.round(rollingConf)}%`;
    confEl.textContent = pct;
    if (rollingConf < 20) {
        confEl.className = 'card-conf low';    // red
    } else if (rollingConf >= 20 && rollingConf <= 69) {
        confEl.className = 'card-conf sweet';  // green
    } else {
        confEl.className = 'card-conf high';   // yellow
    }
} else {
    confEl.textContent = '—';
    confEl.className = 'card-conf';
}
```

**CSS additions:**
```css
.card-conf {
    font-size: 1.1rem;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-weight: 700;
    margin: 0 0.3rem;
}
.card-conf.low { color: #ef4444; }     /* < 20% — thesis weakening */
.card-conf.sweet { color: #10b981; }   /* 20-69% — sweet spot */
.card-conf.high { color: #f59e0b; }    /* 70-100% — may be peaking */
```

**Visual result per card footer:**
```
Last: 9:30    40%    +$40
   ────   ─────   ─────
   time   conf    pnl
```

When no rolling confidence is available:
```
Last: 9:30    —      +$40
```

### 4.3 Data Flow

```
main.py orchestrator
    │
    ├──► StrategyEngine.process() → signals (existing)
    │
    └──► RollingConfidenceCalculator.compute_all()  [NEW]
              │
              ├──► strategy.evaluate(data)  [reuse same data dict]
              │        │
              │        ▼
              │     Signal(confidence=0.xx, ...)
              │
              ├──► RollingWindow.push(signal.confidence)
              │
              ▼
         smoothed = window.mean
         added to health dict → gex_state_{SYMBOL}.json
              │
              ▼
    app_heatmap.py reads JSON
              │
              ▼
    SocketIO → templates/heatmap.html
              │
              ▼
    Footer: "Last: 9:30  40%  +$40"
```

## 5. Strategy Audit

### Layer 1 (8 strategies)

| Strategy | Has Confidence? | Notes |
|----------|-----------------|-------|
| gamma_wall_bounce | ✅ `_compute_confidence()` | Works via evaluate() |
| magnet_accelerate | ✅ `_phase1_confidence()` / `_phase2_confidence()` | Works via evaluate() |
| gamma_flip_breakout | ✅ `_compute_confidence()` | Works via evaluate() |
| gamma_squeeze | ✅ `_squeeze_confidence()` | Works via evaluate() |
| gex_imbalance | ✅ `_compute_confidence_v2()` | **Needs v2→v1 rename** |
| gex_divergence | ✅ `_compute_confidence()` | Works via evaluate() |
| confluence_reversal | ✅ Inline in evaluate() | Works via evaluate() |
| vol_compression_range | ✅ `_edge_confidence()` | Works via evaluate() |

**All 8 L1 strategies work via evaluate() call. Only 1 needs v2→v1 rename.**

### Layer 2 (17 strategies)

| Strategy | Has Confidence? | Notes |
|----------|-----------------|-------|
| All others | ✅ `_compute_confidence()` | Works via evaluate() |
| iv_gex_divergence | ✅ `_compute_confidence_v2()` | **Needs v2→v1 rename** |

**All 17 L2 strategies work via evaluate() call. Only 1 needs v2→v1 rename.**

## 6. Implementation Plan

### Task 1: `strategies/rolling_confidence.py` — Core Calculator

**Scope:**
- Create `RollingConfidenceCalculator` class
- Calls `strategy.evaluate(data)` and reads confidence from returned Signal(s)
- Maintains 10-second `RollingWindow` per strategy
- Returns `Dict[str, Optional[float]]` (confidence % or None)

**Inputs available:** Same data dict passed to StrategyEngine.process()
- `gex_calculator` — GEXCalculator instance
- `rolling_data` — Dict[str, RollingWindow]
- `depth_snapshot` — L2 depth data (if available)
- `regime` — "POSITIVE" / "NEGATIVE"
- `underlying_price` — float
- `timestamp` — float

**Validation:**
- Unit test with mock strategy that produces Signal(confidence=0.xx)
- Verify rolling window smooths correctly
- Verify `None` returned when strategy produces no signal
- Commit

### Task 2: `main.py` — Orchestrator Integration

**Scope:**
- Instantiate `RollingConfidenceCalculator` in `initialize()`
- Call `compute_all()` in `_evaluate_strategies()` after strategy evaluation
- Add rolling confidence to `_build_strategy_health()` output
- Ensure data dict passed to calculator has all required inputs

**Validation:**
- Run orchestrator, verify JSON state file includes `rolling_confidence` per strategy
- Check `app_heatmap.py` reads the value correctly
- Commit

### Task 3: `templates/heatmap.html` — Dashboard Display

**Scope:**
- Add `<span class="card-conf">` element to each strategy card footer
- Add CSS for `.card-conf`, `.card-conf.low`, `.card-conf.sweet`, `.card-conf.high`
- Update `updateDashboard()` JS to read `strat.rolling_confidence` and display
- Color coding: <20% red, 20-69% green, 70-100% yellow, None shows "—"

**Validation:**
- Open heatmap in browser, verify confidence displays between Last: and PnL
- Verify color coding works
- Verify "—" shows for strategies without confidence
- Commit

### Task 4: Rename `gex_imbalance._compute_confidence_v2` → `_compute_confidence`

**Scope:**
- Rename method in `strategies/layer1/gex_imbalance.py`
- Update any callers to use new name
- Verify strategy still works

**Validation:**
- Unit test or quick run
- Commit

### Task 5: Rename `iv_gex_divergence._compute_confidence_v2` → `_compute_confidence`

**Scope:**
- Rename method in `strategies/layer2/iv_gex_divergence.py`
- Update any callers to use new name
- Verify strategy still works

**Validation:**
- Unit test or quick run
- Commit

### Execution Order

```
Task 1: rolling_confidence.py (core calculator)
    ↓
Task 2: main.py integration (wire it up)
    ↓
Task 3: heatmap.html display (show it)
    ↓
Task 4: gex_imbalance v2→v1 rename
    ↓
Task 5: iv_gex_divergence v2→v1 rename
```

**Each task is a separate Forge spawn with validation + commit between tasks.**

## 7. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Update frequency | 1Hz | Matches strategy evaluation cadence |
| Scope | L1 + L2 only (25 strategies) | L3 and full_data excluded from this rollout |
| Rolling window | 10 seconds | Balances responsiveness vs. whipsaw prevention |
| Smoothing method | Rolling mean | Simple, effective; can upgrade to EMA later |
| Confidence output | Percentage (0-100) | Matches existing dashboard convention |
| Action on rolling confidence | Display only | Per Hologaun's request — no trading decisions yet |
| Calculator approach | Call `evaluate()`, read Signal.confidence | Reuses existing logic, no new method signatures |
| Strategies without signal | Return None (show "—") | No signal = no confidence, dashboard shows "—" |
| Per-strategy tasks | 1 task per strategy | Allows validation + commit between updates |

## 8. Open Questions

1. **Should we use EMA instead of simple mean for smoothing?** EMA gives more weight to recent values, which is more responsive to changing conditions. But simple mean is simpler and more predictable.

2. **What about strategies that compute confidence differently for LONG vs SHORT?** The confidence computation should be direction-agnostic — it measures signal strength, not direction.

3. **Should we track confidence trend (rising/falling) in addition to the value?** This could be useful for the dashboard (e.g., show an arrow indicating direction). Could add as a follow-up.

## 9. Success Criteria

- [ ] Rolling confidence computed for all 25 L1+L2 strategies at 1Hz
- [ ] 10-second rolling window with smooth output (no jarring jumps)
- [ ] Dashboard displays rolling confidence on each strategy tile
- [ ] Color coding works correctly (red < 20%, green 20-69%, yellow 70-100%)
- [ ] No impact on existing signal generation or trading logic
- [ ] Each strategy update has validation + commit
- [ ] 2 v2→v1 confidence method renames completed
- [ ] Code review passes (clean, no side effects)
