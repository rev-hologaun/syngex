# Non-Firing Strategy Disable Plan — Pending Approval

**Date:** 2026-08-09
**Author:** Archon
**Status:** ⏳ AWAITING HOLOGAUN APPROVAL
**Source data:** `analysis/analyzed_strategies_v4.md`, `analysis/analyzed_strategies_v3.md`, live `log/signals_*_v2.jsonl`, `config/strategies_v2.yaml`

---

## What This Is

Hologaun is running 5 syngex instances on the v2 config with mostly-empty streams (CPU ~20%). Goal: **disable the strategies that have never fired** to reclaim compute, while we keep and optimize the strategies that actually produce signals.

This plan identifies the non-firing set and the exact config toggles to disable them. **Nothing is executed until approval.**

## Method (how "firing" was determined)

1. Parsed the 41 strategies registered in `config/strategies_v2.yaml` (8 layer1 + 17 layer2 + 4 layer3 + 12 full_data). `net_gamma` is a regime filter, not a strategy — excluded.
2. Cross-referenced each against the **v4/v3 performance analysis** (4.38M historical signals). A strategy present in the analysis has real signal history (cells require ≥50 signals). A strategy **absent** from both analyses has no meaningful historical fire record.
3. Cross-checked the **live v2 signal streams** (`signals_*_v2.jsonl`) to see what's firing under the current v2 config right now.

Two independent signals → confidence in the classification.

---

## FIRING STRATEGIES (22) — KEEP

These have real signal history in v4/v3 analysis. Bucketed by current live behavior:

### A. Confirmed firing under v2 right now (9)
| Strategy | Layer |
|---|---|
| gamma_wall_bounce_v2 | layer1 |
| gamma_squeeze_v2 | layer1 |
| gex_imbalance_v2 | layer1 |
| magnet_accelerate_v2 | layer1 |
| call_put_flow_asymmetry_v2 | layer2 |
| delta_gamma_squeeze_v2 | layer2 |
| exchange_flow_concentration_v2 | layer2 |
| order_book_fragmentation_v2 | layer2 |
| participant_diversity_conviction_v2 | layer2 |

### B. Has history, currently quiet under v2 (13) — KEEP, do NOT disable
These fired historically (they're "firing strategies" by definition) but are silent in the short live window. They stay enabled while we optimize.
| Strategy | Layer |
|---|---|
| confluence_reversal_v2 | layer1 |
| gamma_flip_breakout_v2 | layer1 |
| gex_divergence_v2 | layer1 |
| vol_compression_range_v2 | layer1 |
| delta_volume_exhaustion_v2 | layer2 |
| depth_decay_momentum_v2 | layer2 |
| depth_imbalance_momentum_v2 | layer2 |
| exchange_flow_asymmetry_v2 | layer2 |
| exchange_flow_imbalance_v2 | layer2 |
| participant_divergence_scalper_v2 | layer2 |
| prob_weighted_magnet_v2 | full_data |
| strike_concentration_v2 | layer3 |
| theta_burn_v2 | layer3 |

---

## NON-FIRING STRATEGIES (19) — PROPOSE TO DISABLE

No meaningful signal history in v4/v3 analysis **and** not firing in live v2. Pure compute overhead today.

### full_data (11) — the biggest chunk
| Strategy |
|---|
| extrinsic_flow_v2 |
| extrinsic_intrinsic_flow_v2 |
| gamma_breaker_v2 |
| ghost_premium_v2 |
| iron_anchor_v2 |
| iv_skew_squeeze_v2 |
| prob_distribution_shift_v2 |
| sentiment_sync_v2 |
| skew_dynamics_v2 |
| smile_dynamics_v2 |
| whale_tracker_v2 |

### layer2 (6)
| Strategy |
|---|
| delta_iv_divergence_v2 |
| iv_gex_divergence_v2 |
| obi_aggression_flow_v2 |
| order_book_stacking_v2 |
| vamp_momentum_v2 |
| vortex_compression_breakout_v2 |

### layer3 (2)
| Strategy |
|---|
| gamma_volume_convergence_v2 |
| iv_band_breakout_v2 |

**Total to disable: 19 of 41.** Keeps 22 firing strategies running untouched.

---

## Execution Plan (ON HOLD until approval)

### Mechanism
Single source of truth: `config/strategies_v2.yaml`. Each strategy has an `enabled: true` flag. Setting it to `false` prevents registration AND evaluation (verified in `main.py` lines ~792, ~985, ~2793). The config file is watched for mtime changes and **hot-reloads live** (`_reload_config`, ~line 699) — no restart needed, applies to all 5 instances automatically.

### Steps
1. **Backup / revert path:** confirm clean git state (`git status`). Revert = one `git` operation or flipping flags back to `true`.
2. **Edit `config/strategies_v2.yaml`:** flip `enabled: false` for the 19 non-firing strategies above. Keep all 22 firing strategies at `enabled: true` untouched.
3. **Verify hot-reload:**
   - Check a running instance log for `Config reloaded: N strategies updated` with N = 22 (down from 41).
   - `grep -c strategy_id log/signals_*_v2.jsonl` — confirm firing set unchanged (still the 9 live strategies producing signals).
4. **Observe CPU:** confirm system utilization drops from ~20% as the dead strategies stop evaluating on every tick.
5. **Regression safety:** the 22 kept strategies are untouched — no logic changes, only registration toggles. TradeStation/streams/heatmap unaffected.

### Rollback
- Flip the 19 back to `enabled: true` (or `git checkout config/strategies_v2.yaml`). Hot-reloads the same way.

---

## Notes / Caveats
- **Strategy names differ subtly between analysis and config:** analysis uses v1 names (`gamma_squeeze`); config uses `_v2` suffix (`gamma_squeeze_v2`). Mapping is 1:1 on base name — verified programmatically.
- **`prob_weighted_magnet_v2`** has history (v4) → kept. Its full_data siblings (12 others) mostly have no history → disabled.
- **History is v1-era.** The live v2 window is only ~1 day, so "currently quiet" under v2 for the 13 kept strategies is expected — they're not being disabled, just monitored.
- **These 19 are disabled, not deleted.** If a swept strategy later shows promise we can re-enable with one flag flip.

---

## Requested Action
Approve to proceed with the 19-strategy disable, OR adjust the list (e.g. keep some full_data strategies, or also gate the 13 quiet-but-historical ones).