# PNL V2 Plan — Syngex v2 Dashboard

**Created:** 2026-07-31  
**Status:** Planning  
**Goal:** Single syngex instance running against one symbol hosts both dashboards and all 82 strategies (41 original + 41 `_v2`). No stream count conflict, no second process.

---

## ⚡ Quick-Start Context (for any agent waking up later)

### What to do first
Read `pnlv2plan.md` fully. Then spawn **Forge** for Phase 1 (scaffold). The entire plan has everything Forge needs.

### Key technical facts

**Strategy registration pattern:** In `main.py`, line ~709, there's a `_get_strategy_class(self, layer, name)` method with a hardcoded `strategy_map` dict mapping `(layer, name)` → class objects. Each strategy module defines:
```python
class GammaWallBounce(BaseStrategy):
    strategy_id = "gamma_wall_bounce"
    layer = "layer1"
```
Classes are imported at the top of `main.py` via statements like:
```python
from strategies.layer1.gamma_wall_bounce import GammaWallBounce
```

**_v2 copy convention:** Duplicate each strategy file as `foo_v2.py`. Inside, change:
- Class name: `GammaWallBounce` → `GammaWallBounceV2`
- `strategy_id`: `"gamma_wall_bounce"` → `"gamma_wall_bounce_v2"`
- Any other identifiers should end in `v2` or `V2`

**Config-driven loading:** Strategies load from `config/strategies.yaml` via `_register_strategies_from_config()` (line ~659). It calls `_get_strategy_class(layer, strat_name)` and instantiates if enabled.

**Phase 1 implementation for Forge:**
1. **Copy strategies:** Shell command to duplicate all 41 `.py` files in `strategies/layer1/`, `strategies/layer2/`, `strategies/layer3/`, `strategies/full_data/` appending `_v2` to filenames. Use `sed` or Python script to also rename class names and `strategy_id` values inside each file.
2. **Modify main.py imports:** Add dynamic imports for `_v2` modules alongside existing ones (or use `importlib.import_module`).
3. **Modify main.py `_get_strategy_class`:** Extend `strategy_map` to include `_v2` entries. For example: `"gamma_wall_bounce_v2": GammaWallBounceV2`. This requires importing the _v2 classes and adding entries for all 41 strategies.
4. **Add CLI arg:** After `parser.add_argument("symbol", ...)` (~line 3093), add: `parser.add_argument("--v2-config", default=None, help="Path to strategies_v2.yaml")` then after instantiation (`SyngexApp(...)`), conditionally call `_register_v2_strategies(config_path=args.v2_config)` if provided.
5. **Create `config/strategies_v2.yaml`:** Mirror of `config/strategies.yaml` but with all keys suffixed `_v2` and `enabled: true`.
6. **Create `app_dashboard_v2.py`:** Copy of `app_dashboard.py`. Modify the dashboard to only show strategies whose `strategy_id` contains `_v2`. Filter in the signal display sections by matching strategy_id suffix.
7. **Test:** Run `python3 main.py TSLA --v2-config config/strategies_v2.yaml dashboard_v2` and verify both dashboards work simultaneously on separate ports.

**Shared components NO ONE touches during scaffold:**
- `engine/` — GEXCalculator, NetGammaFilter
- `ingestor/*` — TradeStation client  
- `core/*` — rolling window, key management
- `strategies/engine.py` — StrategyEngine core loop
- `strategies/signal.py` — Signal class
- `strategies/signal_tracker.py` — Resolution/PnL logic
- `strategies/analyzer.py` — metrics analysis

### File layout reference

```
~/projects/syngex/
├── main.py                              # Orchestrator (modify: CLI arg + v2 imports)
├── app_dashboard.py                     # Original dashboard (copy to _v2)
├── app_dashboard_v2.py                  # NEW: v2 dashboard
├── config/
│   ├── strategies.yaml                  # Original configs (untouched)
│   └── strategies_v2.yaml               # NEW: v2 configs
├── strategies/
│   ├── __init__.py
│   ├── engine.py                        # Shared (don't touch)
│   ├── signal.py                        # Shared (don't touch)
│   ├── signal_tracker.py                # Shared (don't touch)
│   ├── layer1/
│   │   ├── gamma_wall_bounce.py         # Original
│   │   ├── gamma_wall_bounce_v2.py      # Copied + renamed
│   │   ├── __init__.py                  # Don't modify
│   │   └── ...
│   ├── layer2/
│   │   ├── delta_volume_exhaustion.py   # Original
│   │   ├── delta_volume_exhaustion_v2.py # Copied + renamed
│   │   └── ...
│   ├── layer3/
│   │   └── ...
│   └── full_data/
│       └── ...
└── analysis/
    ├── pnlv2plan.md                     # THIS FILE
    ├── analyzed_strategies_v4.md        # Latest performance data
    └── runepnl_batch*.md               # Rune recommendations
```

### Files Forge needs to read before starting
- `/home/hologaun/projects/syngex/main.py` — lines 3090-3120 (CLI args), 659-708 (_register_strategies_from_config), 709-810 (_get_strategy_class + strategy_map)
- `/home/hologaun/projects/syngex/strategies/layer1/gamma_wall_bounce.py` — template for strategy structure (class name, strategy_id, layer attrs)
- `/home/hologaun/projects/syngex/app_dashboard.py` — full copy source for dashboard
- `/home/hologaun/projects/syngex/config/strategies.yaml` — source for mirror yaml

---

## Overview

A single syngex process on one symbol runs **both** the existing dashboard and the v2 dashboard simultaneously. The v2 dashboard shows metrics from `_v2` strategy variants only; the existing dashboard shows original strategies only. All strategies share the same data streams, GEX calculator, rolling windows, and signal tracker.

_Why this works:_ Strategies are already config-driven via `config/strategies.yaml`. There's one TradeStation subscription set per symbol (~4 subscriptions = ~$80/min). Adding more strategies inside the same StrategyEngine loop costs only CPU/memory — nothing on the stream budget.

When a v2 strategy change proves valuable, we promote it back into the original strategy file in `strategies/`.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│          Single Syngex Process                       │
│          One Symbol (5-symbol limit shared)          │
│                                                      │
│  TradeStation Streams (4 x 1 symbol)                 │
│    - Quotes                                          │
│    - Option Chain                                    │
│    - Market Depth Quotes                             │
│    - Market Depth Aggregates                         │
│                                                      │
│  Data Flow:                                          │
│    GEX Calc -> RollingWindows                        │
│      -> StrategyEngine (82 strategies total)         │
│          41 Original Strategies                      │
│          41 _v2 Strategies                           │
│                                                      │
│  SignalTracker -> signals.jsonl + signal_outcomes_*  │
│                                                      │
│  Shared JSON State:                                  │
│    gex_state_{SYMBOL}.json                           │
│                                                      │
│  Two Dashboards (separate Streamlit processes):      │
│    app_dashboard.py   -> reads state -> ORIGINAL     │
│         Port 8501                                     │
│    app_dashboard_v2.py -> reads state -> V2 VIEW     │
│         Port TBD                                      │
│                                                      │
│  Config:                                             │
│    config/strategies.yaml  -> v3.100 strategies       │
│    config/strategies_v2.yaml -> _v2 strategies        │
└──────────────────────────────────────────────────────┘
```

**What stays shared (no duplication):**
- `engine/` — GEXCalculator, NetGammaFilter
- `ingestor/` — TradeStation client
- `core/` — rolling window, rolling keys
- `services/` — shared services
- `strategies/signal.py` — Signal class, Direction enum
- `strategies/signal_tracker.py` — OpenSignal resolution logic
- `strategies/engine.py` — StrategyEngine core loop
- `strategies/analyzer.py`, `metrics/`, `rolling_keys.py`, etc.

**What gets duplicated (_v2 copies):**
- All 41 strategy modules (`layer1/*.py`, `layer2/*.py`, `layer3/*.py`, `full_data/*.py`) — each gets a `_v2` sibling with potential logic/code changes
- Standalone files that import from shared modules; no cross-file dependencies between strategies

**What's new (top-level additions):**
- `app_dashboard_v2.py` — copy of dashboard reading same JSON but filtering to `_v2` strategies
- `config/strategies_v2.yaml` — enables/disables `_v2` strategies independently
- Main.py modification: optional `--v2-config` arg to load and register `_v2` strategies

---

## Strategy Inventory (41 total across all layers)

### Layer 1 (8 strategies)
| # | Original (strategies/) | _v2 Status |
|---|------------------------|------------|
| 1 | confluence_reversal.py | Pending |
| 2 | gamma_flip_breakout.py | Pending |
| 3 | gamma_squeeze.py | Pending |
| 4 | gamma_wall_bounce.py | Pending |
| 5 | gex_divergence.py | Pending |
| 6 | gex_imbalance.py | Pending |
| 7 | magnet_accelerate.py | Pending |
| 8 | vol_compression_range.py | Pending |

### Layer 2 (14 strategies)
| # | Original (strategies/) | _v2 Status |
|---|------------------------|------------|
| 9 | call_put_flow_asymmetry.py | Pending |
| 10 | delta_gamma_squeeze.py | Pending |
| 11 | delta_iv_divergence.py | Pending |
| 12 | delta_volume_exhaustion.py | Pending |
| 13 | depth_decay_momentum.py | Pending |
| 14 | depth_imbalance_momentum.py | Pending |
| 15 | exchange_flow_asymmetry.py | Pending |
| 16 | exchange_flow_concentration.py | Pending |
| 17 | exchange_flow_imbalance.py | Pending |
| 18 | iv_gex_divergence.py | Pending |
| 19 | obi_aggression_flow.py | Pending |
| 20 | order_book_fragmentation.py | Pending |
| 21 | order_book_stacking.py | Pending |
| 22 | participant_diversity_conviction.py | Pending |
| 23 | participant_divergence_scalper.py | Pending |
| 24 | vamp_momentum.py | Pending |
| 25 | vortex_compression_breakout.py | Pending |

### Layer 3 (4 strategies)
| # | Original (strategies/) | _v2 Status |
|---|------------------------|------------|
| 26 | gamma_volume_convergence.py | Pending |
| 27 | iv_band_breakout.py | Pending |
| 28 | strike_concentration.py | Pending |
| 29 | theta_burn.py | Pending |

### Full Data (11 strategies)
| # | Original (strategies/) | _v2 Status |
|---|------------------------|------------|
| 30 | extrinsic_flow.py | Pending |
| 31 | extrinsic_intrinsic_flow.py | Pending |
| 32 | gamma_breaker.py | Pending |
| 33 | ghost_premium.py | Pending |
| 34 | iron_anchor.py | Pending |
| 35 | iv_skew_squeeze.py | Pending |
| 36 | prob_distribution_shift.py | Pending |
| 37 | prob_weighted_magnet.py | Pending |
| 38 | sentiment_sync.py | Pending |
| 39 | skew_dynamics.py | Pending |
| 40 | smile_dynamics.py | Pending |
| 41 | whale_tracker.py | Pending |

---

## Workflow

### Phase 1: Scaffold v2 (one-shot)

Forge to execute:

1. Modify `main.py`: add `--v2-config <path>` CLI arg. When present, load strategy classes from `strategies/` that end in `_v2.py`, instantiate them, and register alongside originals.
2. Create `config/strategies_v2.yaml` — duplicate of `strategies.yaml` controlling enable/disable/params for `_v2` variants.
3. Create `app_dashboard_v2.py` — copy of `app_dashboard.py`; filters strategy display by name suffix `_v2`.
4. Copy all 41 strategy `.py` files appending `_v2` to module level (strategy_id, class names).
5. Test: single process runs both dashboards on separate ports, no conflicts.

### Phase 2: Per-Strategy Review & Implement (iterative, one at a time)

For **each strategy**, in priority order:

1. **Review** — Archon presents current performance (from analyzed_strategies_v4.md) plus rune's recommendations (from runepnl_batch*.md)
2. **Discuss** — Hologaun and Archon discuss trade-offs live
3. **Decide** — Agreed-upon changes recorded in this document under that strategy section
4. **Implement** — Forge spawns to apply specific changes to the `_v2` copy only
5. **Verify** — Smoke test: confirm signals flow correctly from the _v2 variant
6. **Log** — Record final decision and reasoning in plan for audit trail

**Change types allowed in `_v2`:**
- Logic/code fixes (gate thresholds, confidence calculations, stop/target logic, RR multipliers, etc.)
- New parameters or constants
- Additional filters or conditions
- Removed/reduced conditions

**What NOT to do in `_v2`:**
- Modify shared components (signal.py, signal_tracker.py, engine.py, analyzer.py, metrics/) — separate review needed
- Delete strategies without explicit approval
- Change signal output format

### Phase 3: Dashboard & Comparison

- Original dashboard shows original strategies' metrics
- v2 dashboard shows `_v2` strategies' metrics
- Both read from same JSON state file (written once by orchestrator)
- Each dashboard independently controls which strategies are visible
- Key metric views: WR by session/confidence, avg P&L, signal volume, direction split
- Ability to toggle individual strategies on/off per-dashboard for quick A/B testing

### Phase 4: Promotion

Once a `_v2` strategy iteration demonstrates measurable improvement:
1. Document exact diff between original and _v2
2. Promote changes back into original strategy file in `strategies/`
3. Re-run analysis to confirm improvement persists
4. Remove _v2 version (or keep as backup comment)

---

## Per-Strategy Change Tracking

### Strategy 1: delta_volume_exhaustion

**Current (v3.100):** WR 46.5% (post-change bear market), SHORT WR 56.0%, avg P&L +$0.83 (short side)
**Previous baseline (pre-bear, analyzed_20260717):** WR 68.8%, SHORT WR 69.7%, avg P&L +$0.17
**Key insight from archon analysis:** Performance regression likely due to bear market conditions, not code change itself. Low-confidence flood (MIN_CONFIDENCE=0.05) was generating massive noise that performed worse in bearish regimes.

**Rune's batch 1 recommendations:**
1. Raise MIN_CONFIDENCE from 0.05 → 0.25-0.35 (documented value was 0.35)
2. Fix BASE_TARGET_FRACS asymmetry: POSITIVE 0.6→0.75, NEGATIVE 1.0→1.25, NEUTRAL 0.75→0.90
3. Add actual R:R gate (currently checks stop distance only, not target R:R)
4. Add slippage modeling
5. Widen STOP_PCT from 0.012→0.015
6. Investigate LONG vs SHORT asymmetry

**Agreed v2 changes:** *Pending discussion*

---

### Strategy 2: gamma_wall_bounce

**Current (v3.100):** Overall WR 46.9%, avg P&L +$1.01. SHORT side dominates: WR 61.7%, avg P&L +$2.81. LONG side is bleeding: WR 24.3%, avg P&L -$1.74.
**Peak cell:** Afternoon 90-99% conf = 88.3% WR, +$5.52

**Rune's batch 2 recommendations (batch1_part2):**
1. Increase LONG target multiplier from 1.5→2.0 (LONG needs higher RR to be profitable at 29% WR)
2. Add per-direction RR analysis

**Agreed v2 changes:** *Pending discussion*

---

### Strategy 3: gamma_flip_breakout

**Current (v3.100):** Overall WR 53.8%, avg P&L +$0.24. LONG WR 58.8%, avg P&L +$0.21. SHORT WR 51.3%, avg P&L +$0.25.
**Both directions profitable — strongest balanced performer.**

**Rune's recommendations:** To be discussed

**Agreed v2 changes:** *Pending discussion*

---

### Strategy 4: gamma_squeeze

**Current (v3.100):** Overall WR 30.9%, avg P&L -$0.28. LONG WR 33.9% (-$0.07). SHORT WR 25.3% (-$0.66).

**Rune's batch 4 recommendations:**
1. Convert net_gamma hard gate → soft confidence penalty
2. Lower POSITIVE regime threshold from 95th→80th percentile
3. Consider directional bias when net_gamma near zero

**Agreed v2 changes:** *Pending discussion*

---

### Strategy 5: gex_divergence

**Current (v3.100):** Overall WR 39.3%, avg P&L -$0.07. LONG WR 40.4% (+$0.03). SHORT WR 37.4% (-$0.26).
**Goldmine cell:** Morning 90-99% conf = 74.0% WR, +$1.74. ORB 50-59% conf = 63.7% WR, +$1.77.

**Rune's batch 5 recommendations:**
1. Tighten confirmation candle from 3x→2x CONFIRMATION_CANDLE_PCT
2. Add slope smoothness metric
3. Add session-specific afternoon boost
4. Consider regime-weighted targets

**Agreed v2 changes:** *Pending discussion*

---

### Strategy 6: gex_imbalance

**Current (v3.100):** Overall WR 36.5%, avg P&L -$0.29. MASSIVE skew: LONG 218 signals / 30.3% WR / -$0.02. SHORT 27,172 signals / 36.5% WR / -$0.30.

**Rune's batch 5 recommendations:**
1. Add minimum GEX magnitude filter for LONG signals
2. Consider dynamic threshold (rolling percentiles vs fixed)
3. Investigate tiny LONG sample (125 signals in previous analysis)

**Agreed v2 changes:** *Pending discussion*

---

### Strategy 7: magnet_accelerate

**Current (v3.100):** Overall WR 23.8%, avg P&L -$0.04. LONG WR 20.0% (-$0.29). SHORT WR 29.6% (+$0.36).
**Standout cell:** ORB 50-59% conf = 73.1% WR, +$1.13. ORB 40-49% conf = 52.1% WR, +$0.36.

**Rune's batch 3 recommendations:**
1. Dynamic magnet target update (fix stale target issue)
2. Separate Phase 1 and Phase 2 WR reporting
3. Increase Phase 1 stop for LONG from 1%→1.5%
4. ORB-specific confidence boost

**Agreed v2 changes:** *Pending discussion*

---

### Strategy 8: vol_compression_range

**Current (v3.100):** Overall WR 40.4%, avg P&L -$0.12. LONG WR 22.7% (-$2.06). SHORT WR 64.7%, avg P&L +$2.56.
**Strong SHORT performer but small N (3,139 signals).**

**Rune's recommendations:** To be discussed

**Agreed v2 changes:** *Pending discussion*

---

### Remaining Strategies (9-41)

Per-strategy review pending. Rune hasn't analyzed these individually yet. Priority order depends on which ones show most promise during v2 data collection.

Strategies marked as "clear losers" (may skip v2 entirely unless requested):
- **call_put_flow_asymmetry** — Entirely unprofitable, worst strategy
- **order_book_fragmentation** — Near-zero return after 35K signals
- **exchange_flow_asymmetry** — Deeply negative on LONG side
- **delta_gamma_squeeze** — Only 112 signals, broken
- **prob_weighted_magnet** — 20% WR, -$0.31 avg

---

## Infrastructure Changes Required

### Files modified

| File | Purpose | Change Type |
|------|---------|------------|
| `main.py` | Orchestrator entry point | Add `--v2-config` CLI arg; dynamic loading of `_v2` strategy classes after original registration |
| `config/strategies_v2.yaml` (NEW) | Enable/disable _v2 strategies | New file, mirror of strategies.yaml |
| `app_dashboard_v2.py` (NEW) | v2 dashboard UI | New file, copy of app_dashboard.py with _v2 strategy filter |

### What stays UNCHANGED (shared, no changes needed)
- `strategies/engine.py` — StrategyEngine registers additional strategies fine, no routing changes
- `strategies/signal.py` — Signal class unchanged
- `strategies/signal_tracker.py` — Resolution/PnL unchanged
- `engine/gex_calculator.py` — GEX computation correct
- `ingestor/*` — Data feeds work identically
- `core/*` — Rolling windows, key management
- `config/trade_guard.py` — READ_ONLY enforcement
- `app_dashboard.py` — Original dashboard untouched
---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Same-process resource contention | Profiling during scaffold phase; 82 strategies in one process vs two instances with fewer strategies |
| `_v2` drift from originals over time | Track all changes in this plan; use git diffs |
| Overfitting to 1 week of data | Keep the 4-week primary data collection cycle running on v3.100 (same process, same streams) |

---

## Next Steps

1. **Immediate:** Plan reviewed and approved
2. **Phase 1 execution:** Archon spawns Forge to scaffold v2 (copy strategies, add CLI arg, create supporting files)
3. **Phase 2 kickoff:** Begin with delta_volume_exhaustion (highest impact, best documented by rune)
4. **Ongoing:** Each strategy reviewed one-at-a-time in Discord before implementation
