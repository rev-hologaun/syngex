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
| **StrategyEngine** | ❌ Missing | Central rule-evaluation loop |
| **Signal class** | ❌ Missing | Standardized output format |
| **Rolling windows** | ❌ Missing | 30m, 5min, 20-period averages for strategies |
| **IV Skew calculator** | ❌ Missing | Not in GEX calculator |
| **ProbabilityITM distribution** | ❌ Missing | Aggregated across all strikes |
| **Extrinsic/Intrinsic tracking** | ❌ Missing | Rolling baselines needed |

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

### Phase 3: Alpha Strategies — Divergence & Positioning (Estimated: 2–3 days)

*Detecting when price action contradicts options structure.*

| # | Task | Strategy | Key Dependencies |
|---|------|----------|-----------------|
| 3.1 | **GEX Divergence** (#9) | Price ↑ but Total GEX ↓ → fade. GEX Ratio (Call/Put) for bias | 0.5, 1.2 |
| 3.2 | **GEX Imbalance** (#5) | Call/Put GEX ratio as standalone dealer bias filter | 0.5, 1.2 |
| 3.3 | **Confluence Reversal** (#6) | Cross-reference technical S/R (VWAP, EMA, daily levels) with gamma walls. Score 1–3 | 0.5, 1.2 |
| 3.4 | **Volatility Compression Range** (#8) | Positive gamma regime + Bollinger squeeze → sell vol (Iron Condors / Credit Spreads) | 1.2 |

**Deliverable:** 4 alpha strategies that detect structural divergence. Dashboard shows "confidence scores" for confluence levels.

---

### Phase 4: Alpha Strategies — Greeks + Order Flow (Estimated: 2–3 days)

*Higher-frequency signals using Delta, IV, and flow data.*

| # | Task | Strategy | Key Dependencies |
|---|------|----------|-----------------|
| 4.1 | **Delta-Gamma Squeeze** (#10) | Delta acceleration + Gamma spike + VolumeUp → extreme momentum entry | 0.5, 1.2, 0.4 |
| 4.2 | **Delta-Volume Exhaustion** (#11) | Trend weakening: declining Delta + declining VolumeUp → fade | 0.5, 1.2, 0.4 |
| 4.3 | **Call/Put Flow Asymmetry** (#12) | Flow Score calculation every 10s. Bid/ask size ratio for conviction | 0.5, 1.2, 0.4 |
| 4.4 | **Delta-IV Divergence** (#13) | Delta ↑ but IV ↓ → high-conviction directional accumulation | 0.5, 1.2, 0.4 |
| 4.5 | **IV-GEX Divergence** (#14) | Price at high + IV crashing + Net Gamma positive → short / buy puts | 0.5, 1.2, 0.4 |

**Deliverable:** 5 greeks-driven strategies. Dashboard shows IV and Delta trend indicators.

---

### Phase 5: Micro-Signal Layer (1Hz) (Estimated: 2–3 days)

*Sub-second bursts. The real advantage of 1Hz options data.*

| # | Task | Strategy | Key Dependencies |
|---|------|----------|-----------------|
| 5.1 | **Gamma-Volume Convergence** (#16) | 1Hz Δ/Γ spike + VolumeUp → ignition signal | 0.5, 1.2, 0.4 |
| 5.2 | **IV Band Breakout** (#17) | IV in bottom 25% of 30m range + price compression → breakout | 0.3, 0.5, 1.2 |
| 5.3 | **Strike Concentration Scalp** (#5) | Top 3 OI strikes → bounce vs slice detection on 1–5 min bars | 0.5, 1.2 |
| 5.4 | **Theta-Burn Scalp** (#19) | High Gamma + high Theta + narrow range → pin trading, 0.2–0.4% targets | 0.5, 1.2, 0.4 |

**Deliverable:** 4 micro-strategies. Dashboard shows micro-signal indicators with real-time confidence.

---

### Phase 6: Full-Data Strategies (v2) (Estimated: 2–3 days)

*Requires the extended GEXCalculator (Phase 0.4) — ProbabilityITM, Extrinsic, IV Skew.*

| # | Task | Strategy | Key Dependencies |
|---|------|----------|-----------------|
| 6.1 | **IV Skew Squeeze** (#15) | IV put/call skew extremes → sentiment reversal. Skew > 0.30 or < -0.10 | 0.4, 0.5, 1.2 |
| 6.2 | **Probability-Weighted Magnet** (#20) | ProbabilityITM + OI → stealth accumulation before price reacts | 0.4, 0.5, 1.2 |
| 6.3 | **Probability Distribution Shift** (#21) | Full distribution skew: Σ(ΔProbITM × ΔStrike) across all strikes | 0.4, 0.5, 1.2 |
| 6.4 | **Extrinsic/Intrinsic Flow** (#22) | Extrinsic value expansion/collapse + theoretical vs market bid/ask | 0.4, 0.5, 1.2 |

**Deliverable:** 4 advanced strategies using the full data set. The "full Syngex experience."

---

### Phase 7: Polish & Integration (Estimated: 1–2 days)

| # | Task | Description |
|---|------|-------------|
| 7.1 | **Dashboard signal overlay** | Update `GammaMagnetView` to show strategy confidence scores directly on heatmap |
| 7.2 | **Signal logging** | Persist all signals to JSON/SQLite for backtesting and review |
| 7.3 | **Per-strategy toggles** | Enable/disable individual strategies from config |
| 7.4 | **Parameter tuning UI** | Allow threshold adjustments (GEX wall threshold, RSI periods, ATR multipliers) without code changes |
| 7.5 | **Documentation** | Update README with strategy index, setup guide, and API reference |

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
│   ├── filters/
│   │   ├── __init__.py
│   │   └── net_gamma_filter.py  # 1.1 — Phase 1
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
| 3 | ⏸️ | — | — | Alpha — divergence |
| 4 | ⏸️ | — | — | Alpha — greeks |
| 5 | ⏸️ | — | — | Micro-signal (1Hz) |
| 6 | ⏸️ | — | — | Full-data (v2) |
| 7 | ⏸️ | — | — | Polish & integration |

---

*Last updated: 2026-04-30*
