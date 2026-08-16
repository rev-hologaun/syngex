# H1 Option-A — Rank Selection Decision Brief

**For:** Hologaun · **From:** Archon · **Date:** 2026-08-16
**Branch:** `feature/h1-optionA-percentile-wall` (commits `e80ba5c`, `095b5aa`, `f0e5fa1`)

---

## What the rank gate does
`rank_keep_frac = X` means *"a wall = a strike whose |gex| is in the top X of its
own symbol's |gex| book"* (computed live per symbol). It replaces the current
absolute dollar-GEX thresholds that are scale/symbol/OI-mode dependent.

The pilot is wired into `gamma_wall_bounce` + `_v2` behind env var
`SYNGEX_WALL_RANK_KEEP_FRAC`. Default (unset) = legacy 500k threshold, byte-identical.

## The core problem the rank fixes
Today's absolute thresholds fire a wildly inconsistent fraction of each symbol's book:

| strategy | threshold | TSLA | SPY | NVDA | INTC |
|---|---|---|---|---|---|
| gamma_squeeze | 100 | 100% | 100% | 100% | 100% |  ← NOISE, every strike is a "wall"
| iron_anchor | 10 | 100% | 100% | 100% | 100% |  ← NOISE
| theta_burn | 5000 | 92% | 100% | 91% | 97% |  ← nearly-useless filter
| gamma_wall_bounce | 500k | 36% | 76% | 33% | 29% |  ← symbol-scattered
| gamma_volume_convergence | 500k | 36% | 76% | 33% | 29% |  ← symbol-scattered

Same threshold, wildly different behavior per symbol → impossible to reason about.

## The rank options (measured, real data)

**Wall-SET size** (how many strikes qualify, of the ~33–39 in each book):

| rank_keep_frac | walls/symbol | gamut across symbols |
|---|---|---|
| 0.25 (top quartile) | ~10 | uniform ✓ |
| 0.10 (top decile) | ~4 | uniform ✓ |
| 0.05 (top 5%) | ~2 | uniform ✓ |

**Signal survival for gamma_wall_bounce** (% of today's 51,797 logged fires kept):

| rank_keep_frac | TSLA | SPY | NVDA | INTC |
|---|---|---|---|---|
| 0.25 | 38% | 76% | 100% | 96% |
| 0.10 | 6% | 29% | 69% | 36% |
| 0.05 | 0% | 0% | 2% | 34% |

---

## Recommendation: **0.25 (top quartile) as the pilot default**

**Why:**
1. It's the least destructive option that still fixes H1. It cuts the noise
   strategies (gamma_squeeze/iron_anchor) from 100%-of-book down to ~10 strikes,
   while keeping the majority (76–100%) of gamma_wall_bounce's genuine fires on
   most symbols.
2. It gives a **uniform, interpretable** wall count (~10) on every symbol — the
   core H1 win — without collapsing the mean-reversion strategy (gamma_wall_bounce
   is a mean-reversion play; it NEEDS enough walls to bounce off).
3. `0.10`/`0.05` are the "if gamma_wall_bounce proves over-firing after the pilot"
   fallback dials. Start at 0.25, tighten only if the live A/B shows it's still
   firing on noise.

**Caveats to note:**
- **TSLA is the outlier**: at 0.25 it keeps only 38% of today's fires (vs 76–100%
  elsewhere). TSLA's book is flatter/more even, so its walls cluster lower. If TSLA
  is your primary symbol, consider 0.25 for non-TSLA and a gentler 0.35–0.40 for
  TSLA — OR accept that TSLA's wall-bounce just gets more selective (which may be
  *correct*, since TSLA wall-bounce may have been over-firing on weak walls).
- **AMD snapshot is stale** (74 msgs) — its numbers are unreliable; exclude from
  the pilot's pass/fail or re-snapshot.
- **Replay limitation:** this is a wall-set + signal-metadata replay off momentary
  snapshots + logged wall_gex; not a full temporal tick replay. The LIVE A/B
  harness (`scripts/pilot_h1_optionA.sh`) is the ground-truth measurement.

## Decision needed from you
1. **Pilot rank:** 0.25 (recommended) or another? TSLA exception or uniform?
2. **Which symbols** to A/B in the first pilot window (suggest: TSLA + SPY, the
   two densest).
3. **Go/no-go:** once feed is up (~1am) run the harness, compare counts vs the
   51,797-signal baseline, then promote to main as v3.225 if clean.