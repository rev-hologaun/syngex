# Syngex Strategy Build Plan

> **Reference:** All 22 strategies are defined in [SYNGEXStrats.md](SYNGEXStrats.md).
> This document is the build tracker — phases, tasks, status, and dependencies.

---

## Current State Assessment

| Component | Status | Notes |
|-----------|--------|-------|
| `tradestation_client.py` | ✅ Done | HTTP-streaming client, quotes + options chain |
| `gex_calculator.py` | ✅ Done | Processes option messages into Gamma Ladder, walls, flip |
| `main.py` orchestrator | ✅ Done | Lifecycle management, data export to `gex_state.json` |
| `gamma_magnet.py` view | ✅ Done | Streamlit heatmap |
| `dashboard.py` | ✅ Done | Rich terminal UI |
| **StrategyEngine** | ✅ Done | Central rule-evaluation loop |
| **Signal class** | ✅ Done | Standardized output format |
| **Rolling windows** | ✅ Done | 30m, 5min, 20-period averages for strategies |
| **IV Skew calculator** | ✅ Done | Added to GEXCalculator (`get_iv_skew()`, `get_iv_by_strike()`) |
| **ProbabilityITM distribution** | ✅ Done | Aggregated across all strikes |
| **Extrinsic/Intrinsic tracking** | ✅ Done | Rolling baselines available via stream greeks |

---

## Build Phases

### Phase 0: Foundation (Estimated: 2–3 days)

*Nothing else works without this. Every strategy depends on it.*

| # | Task | Description | Depends On |
|---|------|-------------|------------|
| 0.1 | **Signal class** | `Signal(direction, confidence, entry, stop, target, expiry, strategy_id)` — the standard output format all strategies produce | — |
| 0.2 | **StrategyEngine** | Central evaluation loop. Reads incoming stream data, passes it to registered strategies, collects signals, routes through Net Gamma filter | 0.1 |
| 0.3 | **RollingWindow** | Rolling statistics class: supports 30m, 5min, 20-period, custom windows. Tracks mean, std, min, max, percentiles. Used by ALL alpha and micro strategies | 0.2 |
| 0.4 | **Extend GEXCalculator** | Add methods: `get_oi_by_strike()`, `get_delta_by_strike()`, `get_theta_by_strike()`, `get_iv_by_strike()`, `get_extrinsic_by_strike()`, `get_probability_itm_by_strike()`. These fields arrive in the 1Hz stream but aren't currently aggregated | 0.2 |
| 0.5 | **Integration test** | Wire StrategyEngine into main.py orchestrator. Run with TSLA, verify signals flow end-to-end (even if empty). Dashboard shows "Strategy Confidence" overlay | 0.1–0.4 |

**Deliverable:** A working strategy pipeline that can accept data, evaluate rules, and output signals.

---

### Phase 1: Master Filter (Estimated: 0.5 days)

*The Net Gamma Regime Filter is the gatekeeper. Every strategy runs through it.*

| # | Task | Description | Depends On |
|---|------|-------------|------------|
| 1.1 | **Net Gamma Regime Filter** | Implements strategy #7 from SYNGEXStrats.md. Returns regime state: `POSITIVE` (fade extremes), `NEGATIVE` (trend-follow). Routes strategy evaluations accordingly | 0.5 |
| 1.2 | **Filter integration** | Register as first-pass evaluator in StrategyEngine. All other strategies check `filter.regime` before producing signals | 1.1 |

**Deliverable:** The pipeline knows which regime we're in and filters signals accordingly.

---

### Phase 2: Core Structural Strategies (Estimated: 2–3 days)

*The "bread and butter" — validates the full pipeline with real, actionable signals.*

| # | Task | Strategy | Key Dependencies |
|---|------|----------|-----------------|
| 2.1 | **Gamma Wall Bounce** (#1) | Mean reversion at Call/Put Walls. OHLC rejection + volume confirmation. 60–65% win rate | 0.5, 1.2 |
| 2.2 | **Magnet & Accelerate** (#2) | Two-phase: magnet pull → breakout acceleration. EMA crossover + GEX tracking | 0.5, 1.2 |
| 2.3 | **Gamma Flip Breakout** (#3) | Regime trend. Price crosses flip → fade above, trend below | 1.2 |
| 2.4 | **Gamma Squeeze / Wall-Breaker** (#4) | Pin detection + breakout through wall + negative gamma confirmation | 0.5, 1.2 |

**Deliverable:** 4 live strategies producing signals on the dashboard. The "core experience" — real gamma-driven trading logic.

---

### Phase 3: Alpha Strategies — Divergence & Positioning (Estimated: 2–3 days) ✅ DONE

*Detecting when price action contradicts options structure.*

| # | Task | Strategy | Key Dependencies | Status |
|---|------|----------|-----------------|--------|
| 3.1 | **GEX Divergence** (#9) | Price ↑ but Total GEX ↓ → fade. GEX Ratio (Call/Put) for bias | 0.5, 1.2 | ✅ |
| 3.2 | **GEX Imbalance** (#5) | Call/Put GEX ratio as standalone dealer bias filter | 0.5, 1.2 | ✅ |
| 3.3 | **Confluence Reversal** (#6) | Cross-reference technical S/R (VWAP, EMA, daily levels) with gamma walls. Score 1–3 | 0.5, 1.2 | ✅ |
| 3.4 | **Volatility Compression Range** (#8) | Positive gamma regime + Bollinger squeeze → sell vol (Iron Condors / Credit Spreads) | 1.2 | ✅ |

**Deliverable:** 4 alpha strategies that detect structural divergence. Dashboard shows "confidence scores" for confluence levels. — **Completed 2026-04-30**

---

### Phase 4: Alpha Strategies — Greeks + Order Flow (Estimated: 2–3 days) ✅ DONE

*Higher-frequency signals using Delta, IV, and flow data.*

| # | Task | Strategy | Key Dependencies | Status |
|---|------|----------|-----------------|--------|
| 4.1 | **Delta-Gamma Squeeze** (#10) | Delta acceleration + Gamma spike + VolumeUp → extreme momentum entry | 0.5, 1.2, 0.4 | ✅ |
| 4.2 | **Delta-Volume Exhaustion** (#11) | Trend weakening: declining Delta + declining VolumeUp → fade | 0.5, 1.2, 0.4 | ✅ |
| 4.3 | **Call/Put Flow Asymmetry** (#12) | Flow Score calculation every 10s. Bid/ask size ratio for conviction | 0.5, 1.2, 0.4 | ✅ |
| 4.4 | **Delta-IV Divergence** (#13) | Delta ↑ but IV ↓ → high-conviction directional accumulation | 0.5, 1.2, 0.4 | ✅ |
| 4.5 | **IV-GEX Divergence** (#14) | Price at high + IV crashing + Net Gamma positive → short / buy puts | 0.5, 1.2, 0.4 | ✅ |

**Deliverable:** 5 greeks-driven strategies. Dashboard shows IV and Delta trend indicators. — **Completed 2026-04-30**

---

### Phase 5: Micro-Signal Layer (1Hz) (Estimated: 2–3 days) ✅ DONE

*Sub-second bursts. The real advantage of 1Hz options data.*

| # | Task | Strategy | Key Dependencies | Status |
|---|------|----------|-----------------|--------|
| 5.1 | **Gamma-Volume Convergence** (#16) | 1Hz Δ/Γ spike + VolumeUp → ignition signal | 0.5, 1.2, 0.4 | ✅ |
| 5.2 | **IV Band Breakout** (#17) | IV in bottom 25% of 30m range + price compression → breakout | 0.3, 0.5, 1.2 | ✅ |
| 5.3 | **Strike Concentration Scalp** (#18) | Top 3 OI strikes → bounce vs slice detection on 1–5 min bars | 0.5, 1.2 | ✅ |
| 5.4 | **Theta-Burn Scalp** (#19) | High Gamma + high Theta + narrow range → pin trading, 0.2–0.4% targets | 0.5, 1.2, 0.4 | ✅ |

**Deliverable:** 4 micro-strategies. Dashboard shows micro-signal indicators with real-time confidence.

---

### Phase 6: Full-Data Strategies (v2) (Estimated: 2–3 days) ✅ DONE

*Requires the extended GEXCalculator (Phase 0.4) — ProbabilityITM, Extrinsic, IV Skew.*

| # | Task | Strategy | Key Dependencies | Status |
|---|------|----------|-----------------|--------|
| 6.1 | **IV Skew Squeeze** (#15) | IV put/call skew extremes → sentiment reversal. Skew > 0.30 or < -0.10 | 0.4, 0.5, 1.2 | ✅ |
| 6.2 | **Probability-Weighted Magnet** (#20) | ProbabilityITM + OI → stealth accumulation before price reacts | 0.4, 0.5, 1.2 | ✅ |
| 6.3 | **Probability Distribution Shift** (#21) | Full distribution skew: Σ(ΔProbITM × ΔStrike) across all strikes | 0.4, 0.5, 1.2 | ✅ |
| 6.4 | **Extrinsic/Intrinsic Flow** (#22) | Extrinsic value expansion/collapse + theoretical vs market bid/ask | 0.4, 0.5, 1.2 | ✅ |

**Deliverable:** 4 advanced strategies using the full data set. The "full Syngex experience."

---

### Phase 7: Polish & Integration (Estimated: 1–2 days) ✅ COMPLETE

| # | Task | Description | Status |
|---|------|-------------|--------|
| 7.1 | **Dashboard micro-signal overlay** | Altair layered chart — gamma profile with confidence markers at signal strikes, hover tooltips, color-coded by strategy type | ✅ |
| 7.2 | **Signal outcome tracking** | SignalTracker resolves signals as WIN/LOSS/CLOSED, computes PnL, win rate, avg hold time, avg RR per strategy. CLI analyzer tool | ✅ |
| 7.3 | **Per-strategy toggles** | Enable/disable individual strategies via YAML config with graceful fallback defaults | ✅ |
| 7.4 | **Parameter tuning** | All strategy params injected from YAML, hot-reload every 2s without restart | ✅ |
| 7.5 | **Documentation** | Comprehensive README — architecture, strategy index, config, dashboard, CLI, signal format, analyzer | ✅ |
| 7.6 | **SignalTracker hold times** | Per-strategy `max_hold_seconds` from YAML config — Theta-Burn gets 8min, IV Skew gets 4hr | ✅ |

---

## Strategy Index (from SYNGEXStrats.md)

| # | Strategy | Layer | Signal Type | Hold Time | Phase |
|---|----------|-------|-------------|-----------|-------|
| 1 | Gamma Wall Bounce | 1 | Mean Reversion | 15–30 min | 2 |
| 2 | Magnet & Accelerate | 1 | Two-Phase | 5–60 min | 2 |
| 3 | Gamma Flip Breakout | 1 | Regime Trend | 15–60 min | 2 |
| 4 | Gamma Squeeze / Wall-Breaker | 1 | Momentum | 5–30 min | 2 |
| 5 | GEX Imbalance | 1 | Positioning Bias | 15–45 min | 3 |
| 6 | Confluence Reversal | 1 | Double-Stacked | 15–60 min | 3 |
| 7 | Net Gamma Regime Filter | 1 | Master Filter | N/A | 1 |
| 8 | Vol Compression Range | 1 | Vol Selling | 30–120 min | 3 |
| 9 | GEX Divergence | 2 | Fade | 15–60 min | 3 |
| 10 | Delta-Gamma Squeeze | 2 | Extreme Momentum | 5–30 min | 4 |
| 11 | Delta-Volume Exhaustion | 2 | Reversal | 15–45 min | 4 |
| 12 | Call/Put Flow Asymmetry | 2 | Directional | 5–60 min | 4 |
| 13 | Delta-IV Divergence | 2 | Sentiment Shift | 15–60 min | 4 |
| 14 | IV-GEX Divergence | 2 | Vol Mean Reversion | 15–45 min | 4 |
| 15 | IV Skew Squeeze | 2 | Sentiment Reversal | 1–4 hr | 6 |
| 16 | Gamma-Volume Convergence | 3 | Ignition | 5–15 min | 5 |
| 17 | IV Band Breakout | 3 | Breakout | 10–45 min | 5 |
| 18 | Strike Concentration Scalp | 3 | Micro-Reaction | 3–15 min | 5 |
| 19 | Theta-Burn Scalp | 3 | Pin Trading | 3–8 min | 5 |
| 20 | Prob-Weighted Magnet | 3 | Stealth Accumulation | 15–45 min | 6 |
| 21 | Prob Distribution Shift | 3 | Leading Indicator | 30min–2hr | 6 |
| 22 | Extrinsic/Intrinsic Flow | 3 | Conviction Tracking | 15min–3hr | 6 |

**Total: 22 strategies + 1 sub-strategy (Magnet Zone Scalp)**

---

## File Structure (Target)

```
syngex/
├── main.py                      # Orchestrator (existing)
├── app_dashboard.py             # Streamlit dashboard (existing)
├── strategies/
│   ├── __init__.py              # Strategy registry
│   ├── signal.py                # 0.1 — Signal class
│   ├── engine.py                # 0.2 — StrategyEngine
│   ├── rolling_window.py        # 0.3 — RollingWindow
│   ├── rolling_keys.py          # Rolling window key constants (prevents silent typos)
│   ├── filters/
│   │   ├── __init__.py
│   │   └── net_gamma_filter.py  # 1.1 — Phase 1 (now with actual directional filtering)
│   ├── layer1/                  # Structural (GEX + OHLC)
│   │   ├── gamma_wall_bounce.py       # 2.1
│   │   ├── magnet_accelerate.py       # 2.2
│   │   ├── gamma_flip_breakout.py     # 2.3
│   │   ├── gamma_squeeze.py           # 2.4
│   │   ├── gex_imbalance.py           # 3.1
│   │   ├── confluence_reversal.py     # 3.2
│   │   └── vol_compression_range.py   # 3.3
│   ├── layer2/                  # Alpha (Greeks + Order Flow)
│   │   ├── gex_divergence.py          # 3.4
│   │   ├── delta_gamma_squeeze.py     # 4.1
│   │   ├── delta_volume_exhaustion.py # 4.2
│   │   ├── call_put_flow_asymmetry.py # 4.3
│   │   ├── delta_iv_divergence.py     # 4.4
│   │   └── iv_gex_divergence.py       # 4.5
│   ├── layer3/                  # Micro-Signal (1Hz)
│   │   ├── gamma_volume_convergence.py # 5.1
│   │   ├── iv_band_breakout.py         # 5.2
│   │   ├── strike_concentration.py     # 5.3
│   │   └── theta_burn.py               # 5.4
│   └── full_data/             # v2 strategies (ProbabilityITM, IV Skew, etc.)
│       ├── iv_skew_squeeze.py
│       ├── prob_weighted_magnet.py
│       ├── prob_distribution_shift.py
│       └── extrinsic_intrinsic_flow.py
├── engine/
│   ├── gex_calculator.py      # Extended with greeks aggregation (0.4)
│   └── dashboard.py           # Terminal UI (existing)
├── views/
│   └── gamma_magnet.py        # Streamlit heatmap (updated in Phase 7)
├── data/
│   └── gex_state.json         # Shared state (existing)
├── log/
│   └── signals.jsonl          # 7.2 — Signal persistence
├── config/
│   └── strategies.yaml        # 7.4 — Per-strategy parameters
├── SYNGEXStrats.md            # Strategy definitions (reference)
├── plan.md                    # This file
└── requirements.txt
```

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| GEXCalculator can't handle all greeks fields | Phase 0 blocked | Check TradeStation API docs for all available fields; may need to extend `_update_strike` to capture Delta, Theta, Vega, IV, ProbITM, Extrinsic |
| 1Hz stream has latency | Micro-strategies unreliable | Start with 5s–30s aggregation windows; optimize latency later |
| Signal noise in live market | False signals overwhelm dashboard | Phase 7 parameter tuning UI is critical; start with conservative thresholds |
| Strategy overlap (multiple strategies firing same signal) | Conflicting signals | Net Gamma filter + signal deduplication in StrategyEngine |

---

## Progress Tracker

| Phase | Status | Started | Completed | Notes |
|-------|--------|---------|-----------|-------|
| 0 | ✅ | 2026-04-30 | 2026-04-30 | Foundation — Signal, RollingWindow, StrategyEngine, GEXCalculator greeks, NetGammaFilter |
| 1 | ✅ | 2026-04-30 | 2026-04-30 | Master filter — NetGammaFilter integrated into engine pipeline |
| 2 | ✅ | 2026-04-30 | 2026-04-30 | Core structural — Gamma Wall Bounce, Magnet & Accelerate, Gamma Flip Breakout, Gamma Squeeze (all Layer 1) |
| 3 | ✅ | 2026-04-30 | 2026-04-30 | Alpha — divergence — GEX Imbalance, Confluence Reversal, Vol Compression Range, GEX Divergence (all Layer 1) |
| 4 | ✅ | 2026-04-30 | 2026-04-30 | Alpha — greeks — DeltaGammaSqueeze, DeltaVolumeExhaustion, CallPutFlowAsymmetry, IVGEXDivergence (all Layer 2) |
| 5 | ✅ | 2026-04-30 | 2026-04-30 | Micro-signal (1Hz) — Gamma-Volume Convergence, IV Band Breakout, Strike Concentration Scalp, Theta-Burn Scalp (all Layer 3) |
| 6 | ✅ | 2026-04-30 | 2026-04-30 | Full-data (v2) — IV Skew Squeeze, Prob-Weighted Magnet, Prob Distribution Shift, Extrinsic/Intrinsic Flow (all full_data) |
| 7 | ✅ | 2026-04-30 | 2026-05-01 | 7.1–7.6 complete (overlay, outcome tracking, toggles, hot-reload, docs, per-strategy hold times) |
| **Phase A** | ✅ | 2026-05-03 | 2026-05-03 | **Heatmap Dashboard** — `app_heatmap.py` (Flask+SocketIO), `heatmap.html` (6-col grid, status LEDs, sparklines), file-based decoupling, SignalTracker stats, health classification, connection status. v1.5. |
| **Val2** | ✅ | 2026-05-05 | 2026-05-05 | **Val2 Optimization** — All 22 strategies: cooldowns removed, MIN_CONFIDENCE 0.35→0.25, trend/regime metadata added, bidirectional expansion, regime/trend filters. 19 fixes + 1 bug fix. v1.72. |

**Total: 22/22 strategies complete (100%) | v1.72 with Val2 optimizations**

---

### Phase A: Heatmap Dashboard (v1.5) (Estimated: 0.5 days) ✅ DONE

*Real-time WebSocket-powered strategy health grid — a compact, glanceable alternative to the Streamlit dashboard.*

| # | Task | Description | Depends On |
|---|------|-------------|------------|
| A.1 | **`app_heatmap.py`** | Standalone Flask + Flask-SocketIO server on configurable port (default 8502). Reads `data/gex_state_{SYMBOL}.json` every 1s, transforms data, emits via WebSocket `strategy_update` event. Background thread handles JSON polling; no blocking the server. | — |
| A.2 | **`templates/heatmap.html`** | Dark-themed 6-column strategy grid. Each card shows: strategy name, status LED (green=pulse active, gray=idle, red=pulse bleeding, off=void), sparkline chart, last signal time, PnL, confidence bar. Layer 2 overview card aggregates signals/confidence/active count. System log stream at bottom. | A.1 |
| A.3 | **Data pipeline integration** | `main.py` orchestrator exports `strategy_health` dict per tick into `gex_state_{SYMBOL}.json`. Each strategy health entry: `status`, `signal_count`, `last_signal_ts`, `confidence`, `win_rate`, `pnl`, `sparkline`. Heatmap reads this file independently — zero coupling to the orchestrator. | main.py |
| A.4 | **Signal outcome stats** | `app_heatmap.py` parses `log/signal_outcomes_{SYMBOL}.jsonl` to compute per-strategy `win_rate` and `pnl`. Merges into strategy health payload for accurate card classification. | signal_tracker |
| A.5 | **Health classification** | Cards classified as: `profitable` (win_rate ≥ 60% + positive PnL), `amber` (active but mixed), `bleeding` (error or win_rate < 35% / PnL < -$100), `idle` (>5 min since last signal), `void` (no data). Color-coded overlays per state. | A.2 |
| A.6 | **Connection status** | Socket.IO 4.7.4 client with WebSocket + polling transport fallback. Connection indicator in header (green dot + "connected" / red dot + "disconnected"). | A.2 |

**Deliverable:** A standalone heatmap dashboard that runs independently of the Streamlit dashboard, showing real-time strategy health in a compact grid format. Accessible at `http://{host}:{PORT}/`.

**Usage:**
```
SYNGEX_SYMBOL=TSLA python3 app_heatmap.py    # runs on port 8502
SYNGEX_SYMBOL=TSLA HEATMAP_PORT=8201 python3 app_heatmap.py  # custom port
```

**Architecture:**
```
main.py (orchestrator) → gex_state_{SYMBOL}.json (shared file)
                                        ↓
                          app_heatmap.py (Flask + SocketIO)
                                        ↓
                          heatmap.html (WebSocket client)
```

**Key design decisions:**
- **File-based decoupling:** Heatmap reads JSON file, no direct import of orchestrator modules. Each runs independently.
- **Background polling:** JSON file read happens in a background thread, 1s interval. Socket.IO emits to all connected clients.
- **Config-driven port:** `HEATMAP_PORT` env var (default 8502), `SYNGEX_SYMBOL` env var (default "UNKNOWN").
- **Socket.IO v4.7.4:** Downgraded from v5.1.0 for flask-socketio compatibility. CDN via jsdelivr (reliable) instead of cdn.socket.io (flaky).

---

## v1.6 Fixes (2026-05-04)

| Fix | File | Impact |
|-----|------|--------|
| **GEX scale unification** | `engine/gex_calculator.py`, `layer1/magnet_accelerate.py` | `get_normalized_net_gamma()` added as canonical scale for magnitude comparisons. `MagnetAccelerate._find_magnet()` now uses normalized gamma. `MIN_MAGNET_GEX` dropped from 500,000 → 1,000. Walls and magnets now on the same scale. |
| **NetGammaFilter directional split** | `filters/net_gamma_filter.py` | Positive regime: LONG when price < flip (buy dip), SHORT when price > flip (sell rally) — fade extremes. Negative regime: LONG when price > flip (breakout), SHORT when price < flip (breakdown) — trend-follow. Previously both regimes used identical logic (inverted for positive). |

### Revert: NetGammaFilter Directional Split

If the inverted positive-regime filtering causes issues during live validation:

1. **Quick revert** — replace the two methods in `filters/net_gamma_filter.py` with identical logic (restore original behavior):
   ```python
   def _evaluate_positive(self, signal: Signal) -> bool:
       if self._flip_strike is None: return True
       if signal.direction == Direction.LONG:
           return self._underlying_price > self._flip_strike
       elif signal.direction == Direction.SHORT:
           return self._underlying_price < self._flip_strike
       return True

   def _evaluate_negative(self, signal: Signal) -> bool:
       # Identical to _evaluate_positive (restore original)
       return self._evaluate_positive(signal)
   ```
2. **Or git revert** — `git checkout HEAD -- strategies/filters/net_gamma_filter.py`

The GEX scale fix (`get_normalized_net_gamma()`) is a safe additive change — the new methods don't break anything and can be left in place regardless of the filter decision.

---

## v1.72 — Val2 Optimization/Fixes Complete (2026-05-05)

**Goal:** Fix broken strategies, remove development-time filters, add regime/trend awareness, expand bidirectional trading, and lower confidence thresholds for maximum signal volume during development. Full reference: `val2plan.md` + `val2fix_raw.md`.

**Scope:** All 22 strategies. 19 targeted fixes + 1 bug fix. Sequential execution (one Forge task at a time), all committed and pushed.

### Universal Changes (All 22 Strategies)

| Change | Impact |
|--------|--------|
| Remove all 5-minute cooldowns | Signals fire on every qualifying tick |
| Lower MIN_CONFIDENCE from 0.35 → 0.25 | Development sees all signals; production stays at 70%+ |
| Add `trend` field to all Signal metadata | Enables post-hoc correlation by price trend |
| Add `regime` field to all Signal metadata | Enables post-hoc correlation by gamma regime |

### P0 Critical Fixes (2 strategies)

| # | Strategy | Key Changes |
|---|----------|-------------|
| P0-1 | **Gamma Squeeze** | Added SHORT leg for short squeezes; hard regime filter (prefer NEGATIVE gamma); sustain filter (price must stay beyond wall 2+ ticks); cooldown removed |
| P0-2 | **Confluence Reversal** | Added SHORT direction; hard regime filter (prefer NEGATIVE gamma); trend filter (prefer range-bound); structural threshold relaxed; cooldown removed |

### P1 Important Fixes (2 strategies)

| # | Strategy | Key Changes |
|---|----------|-------------|
| P1-3 | **Magnet Accelerate** | Added SHORT magnet direction; regime-aware (SHORT in POSITIVE, LONG in NEGATIVE); 60-min hold limit; cooldown removed |
| P1-4 | **Gamma Wall Bounce** | Added velocity filter (0.5% tick threshold — treats fast walls as permeable); rejection_score > 0.6 minimum; regime bonus +0.15; cooldown removed |

### P2 Polish Fixes (2 strategies)

| # | Strategy | Key Changes |
|---|----------|-------------|
| P2-5 | **Vol Compression Range** | Expanded LONG side (any wall below, not just call walls); cooldown removed |
| P2-6 | **GEX Imbalance** | Lowered thresholds (PUT 0.5, CALL 0.65); soft regime filter; cooldown removed |

### P3 Layer 2/3 Fixes (14 strategies)

| # | Strategy | Key Threshold Changes |
|---|----------|----------------------|
| P3-7 | **Gamma Flip Breakout** | MIN_CONFIDENCE 0.35→0.25; cooldown removed |
| P3-8 | **GEX Divergence** | DIVERGENCE_MIN_SLOPE 0.001→0.0005; MIN_CONFIDENCE 0.45→0.25; cooldown removed |
| P3-9 | **Delta Gamma Squeeze** | CALL_WALL_PROXIMITY 0.02→0.03; DELTA_ACCEL 1.15→1.10; MIN_CONFIDENCE 0.35→0.25 |
| P3-10 | **Delta Volume Exhaustion** | DELTA_DECLINE 0.90→0.95; VOL_DECLINE 0.85→0.90; MIN_CONSEC 4→2; MIN_CONFIDENCE 0.35→0.25 |
| P3-11 | **IV-GEX Divergence** | PRICE_PERCENTILE 0.75→0.70; MIN_POSITIVE_GAMMA 500k→200k; MIN_CONFIDENCE 0.35→0.25 |
| P3-12 | **IV Band Breakout** | PRICE_COMPRESSION 0.30→0.40; DELTA_DECEL 0.98→0.95; MIN_CONFIDENCE 0.35→0.25 |
| P3-13 | **Strike Concentration** | BOUNCE_PROXIMITY 0.003→0.005; SLICE_BODY_RATIO 0.5→0.3; MIN_CONFIDENCE 0.35→0.25 |
| P3-14 | **Theta Burn** | RANGE_NARROWNESS 0.30→0.40; MIN_NET_GAMMA 10k→5k; REJECTION_SCORE 0.4→0.3; MIN_CONFIDENCE 0.35→0.25 |
| P3-15 | **Extrinsic/Intrinsic Flow** | EXTRINSIC_EXPANSION 0.05→0.03; VOL_SPIKE 1.50→1.30; MIN_DATA 10→5; MIN_NET_GAMMA 5k→2k; MIN_CONFIDENCE 0.35→0.25 |
| P3-16 | **IV Skew Squeeze** | SKEW_POS 0.30→0.20; SKEW_NEG -0.10→-0.07; MIN_DATA 10→5; MIN_CONFIDENCE 0.35→0.25 |
| P3-17 | **Prob Distribution Shift** | Z_SCORE 2.0→1.5; MIN_CONSEC 3→2; MIN_DATA 10→5; MIN_NET_GAMMA 5k→2k; MIN_CONFIDENCE 0.35→0.25 |
| P3-18 | **Prob Weighted Magnet** | CONSOLIDATION 0.40→0.50; OI 5.0→2.0; DELTA_ACCEL 1.10→1.05; MIN_NET_GAMMA 5k→2k; MIN_CONFIDENCE 0.35→0.25 |
| P3-19 | **Gamma Volume Convergence** | DELTA_ACCEL 1.15→1.10; GAMMA_SPIKE 1.20→1.15; VOL_SPIKE 1.20→1.15; MIN_CONFIDENCE 0.35→0.25 |
| P3-20 | **Call/Put Flow Asymmetry** | MIN_CONFIDENCE 0.35→0.25; cooldown removed |

### Bug Fix

| # | Fix | Impact |
|---|-----|--------|
| BF-1 | **GEX Imbalance NameError** | `_compute_confidence()` referenced `bias` parameter but `evaluate()` never passed it. Added `bias` to function signature and call site. |

### Implementation Details

- **Execution:** Sequential — one Forge subagent task at a time, no parallel spawns
- **Commit granularity:** Every fix committed individually for clean history
- **Total commits:** 19 (strategy fixes) + 1 (bug fix) = 20 commits
- **Commit range:** `29c459d` → `82a6341`
- **All pushed to:** `origin/main`

### Design Principles (Per Hologaun)

1. Remove all 5-minute/time filters — get ALL signals during development
2. Production trading stays at 70%+ confidence — development sees everything at 25%
3. Regime-aware filtering — some strategies work in Positive gamma, others in Negative
4. Trend-aware filtering — some strategies work in trending markets, others in range-bound
5. Strategy development focus — maximize signal volume, improve signal quality

### References

- **Full strategy-by-strategy analysis:** `val2plan.md` (solution design with regime/trend matrices)
- **Raw signal data & agent analysis:** `val2fix_raw.md` (Synapse, Forge, Rune analysis of May 5 signals)

---

## v1.3–v1.4 Fixes (2026-05-01)

| Fix | File | Impact |
|-----|------|--------|
| **NetGammaFilter directional logic** | `filters/net_gamma_filter.py` | Master filter now actually filters — LONG only when price > flip, SHORT only when price < flip in both regimes. Was a NO-OP (always returned True). |
| **Rolling window key constants** | `strategies/rolling_keys.py` (new) | All 18 rolling window keys centralized as constants. 20 strategy files updated. Prevents silent typos from creating phantom windows. |
| **Dead views cleanup** | Removed `views/` directory | Broken import stub for deleted `gamma_magnet.py`. Zero references anywhere in codebase. |
| **SignalTracker per-strategy hold times** | `signal_tracker.py`, `main.py`, `strategies.yaml` | Each strategy gets its own `max_hold_seconds` from YAML config. Theta-Burn: 8min, IV Skew Squeeze: 4hr. Global default 15min for missing configs. |
| **Confluence + Vol Compression target inversion** | `layer1/confluence_reversal.py`, `layer1/vol_compression_range.py` | SHORT targets were placed above entry, LONG below. Standardized to `price +/- risk * TARGET_RISK_MULT`. |
| **Dashboard gamma line thinning** | `app_dashboard.py` (Forge) | Reduced gamma line `strokeWidth` from 2 to 1. |
| **Dashboard micro-signal markers** | `app_dashboard.py` (Forge) | Added `net_gamma` Y-position lookup so dots are visible against gamma profile line. |
| **GEX Imbalance dynamic stops** | `layer1/gex_imbalance.py` | Replaced fixed 1%/1.5% with volatility-based (price_5m rolling std × 2.5, 0.5% fallback). Fixed unreachable thresholds for low-vol symbols. |
| **Delta-IV Divergence removal** | `layer2/` (removed) | 0% win rate across all 10 symbols, 3,611 signals, all losses at 0-1s holds. Per-strike delta rolling windows never populated correctly. |
| **Gamma Flip Breakout thresholds** | `layer1/gamma_flip_breakout.py` | FLIP_PROXIMITY_PCT 2.5%→5%, z-score ±0.5→±0.3. |

---

## v0.4 Fixes (2026-04-30)

| Fix | File | Impact |
|-----|------|--------|
| Gamma wall bounce confidence cap at 0.85 | `layer1/gamma_wall_bounce.py` | No more confidence=1.00 spam on every tick near a wall |
| Dedup window 30s → 60s | `engine.py` | Same strategy can't fire twice within a minute |
| Confluence requires 2+ independent structural signals | `layer1/confluence_reversal.py` | Wall+rolling_max no longer counts as confluence; needs wall+flip, wall+VWAP, or all three |
| Call/Put Flow Asymmetry field name bug | `layer2/call_put_flow_asymmetry.py` | `call_delta_sum`→`call_delta`, `put_delta_sum`→`put_delta` — was returning 0 for every strike |
| Delta-Gamma Squeeze thresholds relaxed | `layer2/delta_gamma_squeeze.py` | Wall proximity 1.5%→2%, delta accel 1.25→1.15x, volume spike 1.4→1.2x, min points 5→3 |
| Delta-Volume Exhaustion thresholds relaxed | `layer2/delta_volume_exhaustion.py` | Delta decline 0.85→0.90x, volume decline 0.80→0.85x, trend duration 4→3 candles |

---

## 📊 First Validation Run Results (2026-05-04, 02:00–13:25 PDT)

**8 symbols monitored, 12,018 signals generated, 19,424 outcomes recorded**
**Overall resolved win rate: 33.7% | Total P&L: -$3,568.45 | 4,389 unresolved (22.6%)**

### Per-Symbol Performance

| Symbol | Signals | Outcomes | WR | P&L | Assessment |
|--------|---------|----------|-----|-----|------------|
| **NVDA** | 1,131 | 2,240 | 37.7% | **+$43.89** ✅ | Only profitable symbol |
| AMZN | 2,375 | 3,700 | 38.9% | -$10.42 | Near breakeven |
| SOFI | 1,790 | 2,701 | 39.3% | -$23.10 | Near breakeven |
| INTC | 1,795 | 3,491 | 33.5% | -$181.13 | Moderate loss |
| AMD | 1,095 | 1,853 | 35.2% | -$267.18 | Moderate loss |
| TSLL | 387 | 656 | 30.7% | -$9.27 | Small sample |
| META | 1,148 | 1,520 | 14.9% | **-$1,280.61** 🔴 | Black hole |
| **TSLA** | 2,297 | 3,263 | 26.3% | **-$1,840.63** 🔴 | Biggest drain (87% of losses with META) |

**TSLA + META = 87% of total losses.** These two symbols need symbol-specific tuning or exclusion.

### Strategy Performance (All Symbols Aggregated)

| Strategy | Total Signals | Resolved WR | P&L | Assessment |
|----------|--------------|-------------|-----|------------|
| **gamma_wall_bounce** | 3,037 | 39.8% | **+$188** | **Only profitable strategy** — NVDA 65.6%, AMZN 60.1%, INTC 50.2% |
| vol_compression_range | 817 | 47.5% | -$110 | High WR but low signal count, TSLA 8.5% bleed |
| gamma_flip_breakout | 109 | 44.4% | -$86 | Only META+NVDA fired (6/8 symbols zero signals) |
| magnet_accelerate | 2,799 | 36.0% | -$800 | 100% LONG, Phase 2 never fired, META 0% WR |
| gex_imbalance | 5,257 | 36.3% | -$546 | 100% SHORT on 7/8 symbols, VWAP logic inverted |
| confluence_reversal | 1,744 | 31.6% | -$67 | TSLA hemorrhaging (-$450), regime filter weak |
| gex_divergence | 4,231 | 26.9% | -$961 | Over-trading, noise generator, 9,687 signals |
| gamma_squeeze | 1,430 | 15.4% | -$533 | Worst WR, fragile signals, 0% on AMD/NVDA/META |

### Critical Findings

1. **12 strategies NEVER FIRED** — layer2, layer3, full_data had no rolling window data feeds (volume_up/down, total_gamma, iv_skew, extrinsic, prob_momentum). Fixed by wiring 7 new keys in main.py.
2. **gamma_wall_bounce is the only profitable strategy** — its mean-reversion logic at gamma walls works when walls are strong (NVDA $200 call wall, AMZN $270). Fails on TSLA/META where walls are absorbed.
3. **TSLA is a structural problem** — not just one strategy, but ALL strategies bleed on TSLA. The options structure behaves differently from other names.
4. **META is a structural problem too** — 14.9% WR overall, 0% on 5 of 8 strategies.
5. **Signal volume is excessive** — 5,257 gex_imbalance signals, 4,231 gex_divergence signals. Most are marginal/false signals.
6. **All 8 L1 strategies fired** — no dormant L1 strategies. The issue was layer2/3/full_data data feeds.

### Optimizations Applied (2026-05-04 Afternoon Session)

All 8 L1 strategies optimized. Sequential task ordering (MOE routing best practice) used for reliability:

| Strategy | Fixes Applied | Key Change |
|----------|--------------|------------|
| gex_divergence | Slope threshold ↑, GEX wall gate, regime alignment, 5min cooldown | Cuts noise signals, requires strong GEX |
| gamma_squeeze | Volume confirmation, net gamma alignment, wider stop | Stops fighting dealer positioning |
| confluence_reversal | 10min cooldown, hard regime filter, wider stop | Stops TSLA spam, cross-regime filtering |
| gex_imbalance | VWAP LONG logic fix, regime filter, 5min cooldown, ratio threshold ↑ | Unlocks dead LONG side |
| magnet_accelerate | Phase 2 bidirectional, min distance filter, 5min cooldown, magnet GEX ↑ | Lights up SHORT side |
| gamma_wall_bounce | 5min cooldown, momentum rejection, regime bonus, wall strength check | Best performer gets quality filter |
| gamma_flip_breakout | 10min cooldown, min gamma strength, tighter proximity | Filters weak regimes |
| vol_compression_range | 10min cooldown, tighter compression, wider stop | Only genuine ranges trade |

### Rolling Window Data Pipeline Fix (v1.66)

7 new rolling window keys wired up in `main.py`:
- `volume_up_5m` / `volume_down_5m` — call/put update counts
- `total_gamma_5m` — from GEXCalculator net_gamma
- `iv_skew_5m` — from GEXCalculator get_iv_skew
- `extrinsic_proxy_5m` — ∑\|net_delta\|×\|net_gamma\|
- `prob_momentum_5m` — Σ(net_delta×|strike-ATM|)

All 12 dormant layer2/3/full_data strategies should now fire on next run.

### MOE Multitasking Lesson

- Both Archon and Forge run Qwen3.6 MOE mode
- True multitasking (parallel file edits) causes routing noise and stalled tasks
- **Sequential task ordering** (one file, one logical sequence) gives highest coding win rate
- When Forge stalls on multi-edit tasks, re-spawn with step-by-step approach works

---

## Next Steps

| Priority | Task | Notes |
|----------|------|-------|
| 🔴 High | **Val2 live validation (May 6)** | Run all 22 strategies with relaxed thresholds. Expect 3-5x signal volume vs May 5. Compare win rates. |
| 🔴 High | **Signal volume analysis** | Track which strategies actually fire with new thresholds. Identify noise vs genuine signals. |
| 🟡 Medium | **Production deployment** | Apply 70%+ confidence filter, re-enable cooldowns, apply regime/trend gates per `val2plan.md` |
| 🟡 Medium | **TSLA/META symbol-specific tuning** | Either exclude or create symbol-specific parameter sets |
| 🟢 Low | **Future — Backtesting framework** | Use signal_outcomes.jsonl for historical strategy performance analysis |
| 🟢 Low | **Future — Real execution pipeline** | TradeStation API integration for automated order placement |
| 🟢 Low | Future — Backtesting framework | Use signal_outcomes.jsonl for historical strategy performance analysis |
| 🟢 Low | Future — Real execution pipeline | TradeStation API integration for automated order placement |
| 🟢 Low | Future — Price-band signal dedup | See Future Enhancements below |

---

## Future Enhancements

### Adopt n8n for Workflow Orchestration

**Source:** https://github.com/n8n-io/n8n

**What it is:** Fair-code workflow automation platform — visual node-based pipeline builder with 400+ integrations, native AI/LangChain support, self-hostable (runs on gojira).

**Why SYNGEX needs it:** Right now our orchestration is fragmented — Python orchestrator (`main.py`), cron jobs, manual monitoring, separate alert systems. n8n could unify the pipeline plumbing into a single visual workflow with built-in error handling, retries, and webhook notifications.

**Use cases:**
- TradeStation data → analysis → alert → execution as a monitored pipeline
- News/sentiment feeds (RSS, API connectors) → LLM summarization → signal injection
- Discord/Telegram webhook alerts when high-confidence signals fire
- Scheduled heatmap runs, validation runs, reporting
- 400+ integrations mean we get connectors for free (news APIs, data services, monitoring tools)

**What it replaces:** Ad-hoc cron jobs, manual monitoring, custom alert scripts, fragmented orchestration.

**What it doesn't replace:** SYNGEX's Python analysis engine. n8n is the glue, not the brain.

**Status:** Research phase. Self-hostable, runs on gojira, no vendor lock-in.

### ProspectAI — Critic Pattern for Adversarial Review

**Source:** https://github.com/moisesprat/ProspectAI

**Idea:** ProspectAI's standout feature is its **Critic** stage — an adversarial review agent that checks 12 failure modes (schema validity, allocation math, entry zone logic, R/R ratios, regime consistency) and emits structured correction directives before the final output is produced.

**Plan:** When we adopt n8n for orchestration, build the Critic pattern into the pipeline as an n8n workflow node. After the strategy engine produces draft signals/recommendations, the Critic reviews them against failure-mode checks and returns structured corrections. A final pass incorporates those corrections.

**Why:** TradingAgents was a learning exercise — great ideas, but yfinance-level data. The Critic pattern is worth stealing: it catches garbage before it becomes the final output, adds an adversarial quality gate, and forces the pipeline to self-correct.

**Status:** Idea captured. Implement as part of n8n orchestration upgrade.

### trading_skills — MCP Integration Layer

**Source:** https://github.com/staskh/trading_skills

**What it is:** Claude-powered advisor system for options traders. MCP server + Claude Code skills that expose 23 trading analysis tools (market data, technicals, options greeks, spread analysis, scanners, IBKR portfolio management) as a conversational front end. Data from Yahoo Finance, whale detection via Massive API.

**Integration idea:** Wrap SYNGEX's strategy engine behind an MCP endpoint. Claude could query SYNGEX for signals on any ticker the same way it queries technical indicators or fundamentals. The unified query flow: fundamentals → technicals → correlation check → SYNGEX gamma signals → IBKR portfolio impact → unified recommendation.

**Why this works:** trading_skills is an orchestration + presentation layer, not a strategy engine. SYNGEX is the gamma/structural strategy module. They're complementary — trading_skills brings PMCC scoring, IBKR portfolio mgmt, correlation matrices; SYNGEX brings 22 gamma-driven options strategies. Different data layers (Yahoo Finance batch vs TradeStation streaming) but both useful.

**Architecture vision:**
- n8n → pipeline orchestration, alerts, data flows
- trading_skills → conversational front end, multi-data fusion via Claude
- SYNGEX → gamma/structural strategy engine (MCP tool)
- TradeStation → execution

**Status:** Conceptual. Requires wrapping SYNGEX as an MCP tool and integrating with trading_skills' MCP server.

### Price-Band Signal Deduplication

**Problem:** `dedup_window_seconds: 60` only deduplicates by `strategy_id`. Multiple strategies can independently fire signals for the same direction at nearly identical prices (e.g., 3 LONG signals within 2% of each other from different strategies). This creates noise on the dashboard.

**Proposed solution:**
- Add `dedup_price_band_pct` to config (default TBD — 0.5% is a starting guess)
- After existing `strategy_id` dedup, run a second pass: group signals by `(direction, symbol)` within the time window, keep only the highest-confidence signal per price band
- Log suppressed signals as "confluence confirmed" — multiple strategies agreeing = higher signal strength
- This turns noise reduction into a signal-strength indicator for the heatmap

**Parameters to tune post-validation:**
- `dedup_price_band_pct` — depends on symbol price level (±0.1% for TSLA at $400 = $0.40; ±0.1% for $50 stock = $0.05 — may need adaptive banding)
- `dedup_keep_best` — keep highest confidence, or average confidence across agreeing strategies
- Suppression logging — how to display confluence signals on the heatmap

**Status:** Deferred until after dual-validation data collection. Need to observe signal patterns in live data before choosing the right band percentage.

### Other Future Enhancements

- **iv_skew_squeeze inline window:** Creates `RollingWindow` on first call. Safe but could create two windows if called in parallel. Consider moving to `__init__`.
- **VWAP confirmation buffer:** `gex_imbalance` uses binary `price > mean` pass/fail. A small buffer zone (e.g., X% above VWAP) could reduce whipsaw in choppy markets.

### Config Hot-Reload (Live Parameter Tuning)

**Current state:** `main.py` has a `_watch_config()` async task that polls `strategies.yaml` every 2 seconds for file modification changes. When a change is detected, it re-reads the YAML and updates `self._strategy_config`. **But this is cosmetic only** — the already-initialized strategy instances hold their original parameters from startup. They never receive the new values.

**What's needed to make it real:**
1. **Strategy parameter accessor:** Each strategy needs a `set_params(dict)` method that accepts a config dict and updates its internal thresholds/weights at runtime
2. **Engine-level reload hook:** When `_watch_config` detects a change, it iterates over `self._strategy_engine._strategies` and calls `set_params()` on each with the matching config entry
3. **Signal safety:** Hot-reloaded params should only apply to *new* signals, not affect signals already in-flight. The `SignalTracker` already handles this via `max_hold_seconds` — a strategy with updated hold times just won't close old signals early.
4. **Validation warning:** Log the param change to the log stream so the operator sees what changed and when. Optionally emit a Socket.IO event to the heatmap for a "config updated" notification.

**Use cases:**
- During live validation: tune thresholds (confidence caps, proximity ranges, delta acceleration ratios) without killing the pipeline
- Quick response to changing market conditions: a strategy that's too aggressive in high-vol regimes can be dialed back mid-session
- A/B testing: run two different parameter sets side-by-side by temporarily editing the YAML

**Status:** Deferred. The infrastructure (file watcher, YAML reload) exists. Just needs the strategy-level `set_params()` contract and the engine's reload hook. Low priority — useful for tuning, not critical for correctness.

### temple-stuart-accounting — Steal Ideas From

**Source:** https://github.com/Temple-Stuart/temple-stuart-accounting

Built by a daily options trader. Full financial OS, but the Trading Analytics module has several concepts worth stealing for SYNGEX when we have the PostgreSQL OHLC data layer (1m, back to 2015):

**Convergence Pipeline Architecture** — Scores universe across 4 categories, requires 3/4 above threshold to qualify for trade generation. Same pattern: institutional pre-filter → multi-category scoring → trade card generation. Could map to our gamma-driven strategies (Gamma Regime + GEX Structure + Volume Confirmation + Signal Confluence).

**Three-Outcome EV Model** — Win/loss/breakeven expected value with honest "Est. PoP" labels. Uses N(d2) Black-Scholes probability at actual breakeven prices. Not a guess — mathematical. Worth implementing in our signal output format.

**3-Tier Filter Panel** — 15 configurable parameters across liquidity gates, risk profile, edge metrics. Institutional-grade pre-filtering before running strategies.

**Trade Card Persistence** — Save, link, and grade trades with an A/B/C/D/F system. Cleaner than our current WIN/LOSS/CLOSED tracking.

**Lot-Based Cost Basis** — FIFO, LIFO, HIFO, Specific ID. Real accounting, not just trade tracking. Useful when we have the full OHLC history for backtesting.

**Wash Sale Tracking** — IRS Pub 550 compliant, 30-day window. Good to have in the system even if not immediately actionable.

**Risk Flags** — Insider selling, earnings proximity, low liquidity warnings. Pre-trade risk checklist.

**Status:** Steal ideas from, not code. TypeScript/Next.js/PostgreSQL — we'd re-implement concepts in Python. Depends on PostgreSQL OHLC data layer being ready.

### Database — SYNGEX Data Pipeline

**Concept:** Populate PostgreSQL with OHLC + options data from every SYNGEX run. Store OHLC at 1m, GEX ladder snapshots at 1m (not raw chains at 1Hz — too heavy), key metrics (net gamma, IV skew, flip state) at 1m, and signal events at event time. This enables backtesting against real options structure, replaying past trades (e.g., TSLL), and building the Temple Stuart convergence pipeline on actual data. Raw chains at 30s granularity for reconstruction when needed.

**Status:** Deep future. Requires PostgreSQL infrastructure, storage planning, and orchestrator integration.

### DeerFlow — 18-Middleware Chain for Lead Agent Orchestration

**Source:** https://github.com/bytedance/deer-flow

ByteDance's super agent harness uses an 18-middleware chain on its lead agent. Each middleware runs in strict append order, intercepting or augmenting the agent's behavior at specific points. This could become our lead agent / orchestrator layer — especially if wired into n8n as the "brain" routing between SYNGEX strategies.

**The middleware chain:**

1. **ThreadDataMiddleware** — Creates per-thread isolation scope, resolves user identity
2. **UploadsMiddleware** — Tracks and injects uploaded files into conversation
3. **SandboxMiddleware** — Acquires sandbox, stores sandbox_id in state
4. **DanglingToolCallMiddleware** — Injects placeholder results for interrupted tool calls (prevents malformed history errors)
5. **LLMErrorHandlingMiddleware** — Normalizes provider/model failures into recoverable errors
6. **GuardrailMiddleware** — Pre-tool-call authorization via pluggable providers (allowlist, OAP policies, custom)
7. **SandboxAuditMiddleware** — Audits sandboxed shell/file operations for security logging
8. **ToolErrorHandlingMiddleware** — Converts tool exceptions into recoverable errors instead of aborting
9. **SummarizationMiddleware** — Context reduction when approaching token limits (optional)
10. **TodoListMiddleware** — Task tracking with write_todos (optional, plan mode)
11. **TokenUsageMiddleware** — Records token usage metrics (optional)
12. **TitleMiddleware** — Auto-generates thread title after first complete exchange
13. **MemoryMiddleware** — Queues conversations for async memory update (filters to user + final AI responses)
14. **ViewImageMiddleware** — Injects base64 image data before LLM call (conditional on vision support)
15. **DeferredToolFilterMiddleware** — Hides deferred tool schemas until tool search is enabled (optional)
16. **SubagentLimitMiddleware** — Truncates excess subagent task calls to enforce concurrency limit
17. **LoopDetectionMiddleware** — Detects repeated tool-call loops; hard-stops with forced text answer
18. **ClarificationMiddleware** — Intercepts clarification requests, interrupts via Command(goto=END) (must be last)

**SYNGEX relevance:** The ones worth stealing for our orchestrator:
- **#4 DanglingToolCall** — when a strategy call times out, inject a fallback result instead of crashing the pipeline
- **#5 LLMErrorHandling** — normalize model failures into recoverable states (critical for vLLM + local models)
- **#6 Guardrails** — pre-execution authorization: only allow trades above certain confidence thresholds, block risky signals
- **#8 ToolErrorHandling** — strategy failures don't kill the pipeline; they become recoverable errors
- **#9 Summarization** — context reduction for long sessions (keep the most relevant signals, compress older ones)
- **#13 Memory** — async memory updates, fact deduplication at apply time
- **#16 SubagentLimit** — cap concurrent strategy evaluations to prevent resource exhaustion
- **#17 LoopDetection** — detect when a strategy is stuck in a repetitive pattern and force a reset

**Status:** Conceptual. The middleware pattern is the key idea — a chain of interceptors that handle errors, guardrails, context management, and loop detection before/after strategy execution. Could be implemented as a Python middleware chain in the StrategyEngine or as n8n workflow nodes.

---

*Last updated: 2026-05-03 — v1.5 — Heatmap dashboard (Phase A) complete. 22/22 strategies live. Dual-validation required: both Streamlit dashboard AND Heatmap must be validated during full-market runs. Next: Full-market validation Monday 6:30 AM PT.*
