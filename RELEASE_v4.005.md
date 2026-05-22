# SYNGEX Release Notes — v4.005

**Date:** 2026-05-22  
**Commit Range:** Latest main branch  
**Build Type:** Strategy hotfix — three dead-to-firing strategies

---

## Summary

Three heatmap strategies were not emitting signals due to gate bottlenecks and data source bugs. All fixed. Plus a centralized participant data fix that ripples across multiple strategies.

---

## Changes

### IV_GEX_DIV (`strategies/layer2/iv_gex_divergence.py`)

| Fix | Severity | Description |
|-----|----------|-------------|
| Skew mismatch | P0 | LONG signals compared call skew against put skew history — always failed. Fixed to always use put skew for both directions. |
| Net gamma scale | P0 | `MIN_POSITIVE_GAMMA = 200000` was meaningless on cumulative gamma. Switched to `get_normalized_net_gamma()` with threshold `5.0`. |
| IV decline ratio | P1 | `0.95 → 0.90` — 5% drop → 10% drop below rolling avg |
| Skew ROC threshold | P1 | `0.15 → 0.08` — 15% → 8% over 5 ticks |
| Gamma density decline | P1 | `0.70 → 0.80` — 30% decline → 20% decline |
| MIN_CONFIDENCE | P2 | `0.0 → 0.20` |
| Docstring | P3 | Updated to document actual 5 components (not 7) |

### TAIL_RISK (`strategies/layer2/delta_iv_divergence.py`)

| Fix | Severity | Description |
|-----|----------|-------------|
| Decoupling abs() | P0 | `current_corr < mean_corr * 0.50` inverted on negative mean_corr. Fixed with `abs()` on both sides. |
| Gamma double-push | P0 | Gate pushed gamma density into shared rolling window during evaluation, double-pushing against main.py's push. Removed the push. |
| Decoupling threshold | P1 | `0.50 → 0.70` — 50% drop → 30% drop from rolling mean |
| Trend z-threshold | P1 | `rolling_window.py`: `_trend_z_threshold` `0.8 → 0.5` |
| Divergence strength | P1 | `0.3 → 0.2` — both z-scores ≥ 0.4 instead of ≥ 0.6 |
| MIN_CONFIDENCE | P2 | `0.0 → 0.20` |
| Confidence c5 | P2 | Now uses `greeks_summary` net gamma when available, range `0→500k` |

### VAMP (`strategies/layer2/vamp_momentum.py`)

| Fix | Severity | Description |
|-----|----------|-------------|
| Gate B multiplier | P1 | `1.2 → 1.05` — depth surge 20% above avg → 5% above avg |
| Gate C removed | P1 | Spread stability gate removed — conceptually misaligned (blocks signals during volatility when they're most useful) |
| MIN_CONFIDENCE | P2 | `0.0 → 0.20` |
| Docstring | P3 | Updated to document 5 components (not 7), 2 gates (not 3) |

### main.py — Participant Data Fix

| Fix | Severity | Description |
|-----|----------|-------------|
| NumParticipants source | P0 | TradeStation returns `NumParticipants` as 0/missing. Replaced per-level reads with `bid_avg_participants` / `ask_avg_participants` from orb_probe.py (already computed correctly). Fixes VAMP Gate A and Whale tracker concentration. |

---

## Impact

- **IV_GEX_DIV:** ~0.01% pass rate → usable signal rate
- **TAIL_RISK:** Multiple simultaneous bottlenecks → removed
- **VAMP:** Gate B blocked 85-95% of ticks, Gate C blocked during volatility → removed/relaxed
- **Participant data:** Fixes ripple to VAMP, Whale tracker, and any future strategies using participant counts

---

## Next Investigation

**PARTICIPANT_CONV** (`participant_diversity_conviction`) — next strategy to investigate for signal emission issues.

---

## Commits

- `4541298` — main.py: NumParticipants → bid/ask avg participants
- `9376e38` — TAIL_RISK: decoupling abs(), gamma double-push, relaxed params
- `132fcbf` — VAMP: Gate B 1.05, Gate C removed, MIN_CONFIDENCE 0.20
