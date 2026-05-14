# NoFire Strategy Threshold Lowering Plan

**Date:** 2026-05-13
**Status:** Phase 1 pending approval
**Scope:** 30 non-firing strategies across Layer 2, Layer 3, and Full Data

---

## Background

SYNGEX V2.09 ran its first full day across 5 symbols (TSLA, AAPL, MSFT, NVDA, SPY). Only 11 strategies fired — all Layer 1 (GEX/walls) and a few Layer 2 (flow/depth). All 30 other strategies remained silent across all 5 symbols.

This is not a bug — it's a data collection problem. The 30 silent strategies are designed to catch rare, high-conviction signals. They won't fire every day. But if they *never* fire, we can't validate whether their logic is sound or whether the thresholds are simply too strict.

**Goal:** Lower thresholds enough to get initial signals for data collection. Not to change the strategy's core behavior — just to prove they can fire and collect outcome data.

---

## Analysis: Why They're Not Firing

Three categories of blockers, in order of impact:

### 1. σ-Thresholds Are Extreme (Primary Blocker)

The most common pattern: a rolling z-score must exceed 2.0-5.0σ. This is statistically rigorous but means the signal only fires during extreme events — which may not happen every day.

| Strategy | Current Threshold | Type |
|----------|------------------|------|
| `whale_tracker` | Concentration z-score ≥ 5.0σ | Gate |
| `sentiment_sync` | ΔSkew/VSI z-score ≥ 2.0σ | Gate |
| `skew_dynamics` | Ψ ROC z-score ≥ 2.0σ | Gate |
| `smile_dynamics` | Ω ROC z-score ≥ 2.0σ | Gate |
| `gamma_breaker` | Wall GEX ≥ 2.0σ | Gate |
| `iron_anchor` | Liq wall ≥ 3.0σ | Gate |

### 2. Raw Value Thresholds Are Extreme (Secondary Blocker)

Many strategies require extreme raw metric values before they even reach gate evaluation:

| Strategy | Current Threshold | Type |
|----------|------------------|------|
| `depth_imbalance_momentum` | IR > 3.0 or < 0.6 | Signal detection |
| `obi_aggression_flow` | OBI > 0.75 AND AF > 0.5 | Signal detection |
| `extrinsic_flow` | RΦ > 3.0 or < 0.3 | Signal detection |

### 3. Multi-Condition AND Requirements (Tertiary Blocker)

Some strategies require two or more independent metrics to agree simultaneously:

| Strategy | Conditions | Type |
|----------|-----------|------|
| `obi_aggression_flow` | OBI > 0.75 AND AF > 0.5 | Signal detection (AND) |
| `sentiment_sync` | ΔSkew > 2σ AND VSI > 2σ | Gate A (AND) |
| `iron_anchor` | Proximity < $1.00 AND 3σ wall AND velocity decreasing | Multiple gates |

---

## Phase 1: Soft Gate Relaxation (Safe, Reversible)

**Risk:** Low. No logic changes. Config-only.
**Timeline:** 1-2 hours (4 batch jobs)
**Revert:** Commit hash, one line revert.

### 1A. Disable VAMP Validation Gates

VAMP validation checks that VAMP direction aligns with signal direction. It's already optional (`use_vamp_validation = True`). Flip to `False`.

**Strategies affected (5):**
- `depth_imbalance_momentum` — Gate D
- `participant_divergence_scalper` — Gate D
- `participant_diversity_conviction` — Gate D
- `delta_volume_exhaustion` — Gate D (if present)
- `exchange_flow_*` — Gate D (if present)

**Impact:** Removes one gate that often fails silently. These strategies will fire whenever the other gates pass.

### 1B. Halve Data Point Minimums

Many strategies require 10+ data points before evaluating. This means they're blind for the first ~10 ticks of each window, and may never accumulate enough data during slow periods.

**Strategies affected (8):**
- `participant_diversity_conviction` — min_data_points: 10 → 5
- `sentiment_sync` — min_data_points: 10 → 5
- `iron_anchor` — min_data_points: 10 → 5
- `whale_tracker` — min_conc_data_points: 10 → 5
- `skew_dynamics` — min_psi_data_points: 10 → 5
- `smile_dynamics` — min_omega_data_points: 10 → 5
- `extrinsic_flow` — min_phi_data_points: 10 → 5
- `delta_iv_divergence` — min_data_points: 5 → 3

**Impact:** Strategies become active sooner. More signal opportunities.

### 1C. Lower Confidence Floor to 0.10

Many strategies pass all gates but then get blocked by `confidence < MIN_CONFIDENCE (0.15)`. The confidence models are complex 5-7 component calculations. If gates pass but confidence is 0.12, the signal dies.

**Strategies affected (all 30):**
- `MIN_CONFIDENCE` = 0.15 → 0.10

**Impact:** Weak signals pass through for data collection. No change to gate logic or signal detection.

### 1D. Add Regime-Soft Mode

Gate B (GEX regime alignment) blocks signals when direction doesn't match regime:
- `extrinsic_flow`: LONG requires POSITIVE gamma
- `gamma_breaker`: LONG requires POSITIVE gamma
- `skew_dynamics`: LONG requires POSITIVE gamma
- `smile_dynamics`: LONG requires POSITIVE gamma
- `whale_tracker`: LONG requires POSITIVE gamma
- `iron_anchor`: LONG requires POSITIVE gamma

**Approach:** Add a `regime_soft` parameter. When True, regime misalignment reduces confidence by 0.10 instead of blocking entirely.

**Strategies affected (6):**
- `extrinsic_flow` — Gate B
- `gamma_breaker` — Gate B
- `skew_dynamics` — Gate B
- `smile_dynamics` — Gate B
- `whale_tracker` — Gate C
- `iron_anchor` — Gate B

**Impact:** Signals can fire in "wrong" regime but with reduced confidence. Collects data on whether regime-mismatched signals have lower win rates.

---

## Phase 2: σ-Threshold Reduction (Moderate Risk)

**Risk:** Moderate. Logic changes. May increase signal frequency significantly.
**Timeline:** 1-2 hours (4 batch jobs)
**Revert:** Commit hash, one line revert.

### 2A. Reduce σ Thresholds

| Strategy | Current | New | Rationale |
|----------|---------|-----|-----------|
| `whale_tracker` | ≥ 5.0σ | ≥ 3.0σ | Still significant, catches more whales |
| `sentiment_sync` | ≥ 2.0σ | ≥ 1.5σ | 1.5σ = 93% confidence, still meaningful |
| `skew_dynamics` | ≥ 2.0σ | ≥ 1.5σ | Same rationale |
| `smile_dynamics` | ≥ 2.0σ | ≥ 1.5σ | Same rationale |
| `gamma_breaker` | ≥ 2.0σ | ≥ 1.5σ | Major walls at 1.5σ are still meaningful |
| `iron_anchor` | ≥ 3.0σ | ≥ 2.0σ | 2σ = 95% confidence, still strong |

### 2B. Reduce Raw Value Thresholds

| Strategy | Current | New | Rationale |
|----------|---------|-----|-----------|
| `depth_imbalance_momentum` | IR > 3.0 | IR > 2.0 | 2.0 is still extreme bid/ask imbalance |
| `obi_aggression_flow` | OBI > 0.75, AF > 0.5 | OBI > 0.5, AF > 0.3 | Moderate skew/aggression still valid |
| `extrinsic_flow` | RΦ > 3.0 or < 0.3 | RΦ > 2.0 or < 0.5 | 2.0x conviction is still strong |

---

## Phase 3: Multi-Condition AND → OR (Higher Risk)

**Risk:** High. Changes core strategy logic. May flood with signals.
**Timeline:** TBD
**Revert:** Commit hash, one line revert.

### 3A. Partial-Agreement Modes

For strategies requiring two independent metrics to agree:

| Strategy | Current | New Mode |
|----------|---------|----------|
| `obi_aggression_flow` | OBI > 0.75 AND AF > 0.5 | OBI > 0.5 OR AF > 0.3 (reduced conf) |
| `sentiment_sync` | ΔSkew > 2σ AND VSI > 2σ | ΔSkew > 2σ OR VSI > 2σ (reduced conf) |

Reduced confidence when only one condition met: confidence *= 0.7

---

## Evaluation Criteria

After Phase 1, assess:
1. **Signal frequency:** How many signals per day per strategy?
2. **Signal distribution:** Are signals clustered in time or spread throughout the day?
3. **Early signals:** Are strategies firing in the first 30 minutes (data point test)?
4. **Regime mismatches:** Are regime-soft signals actually firing?

After Phase 2, assess:
1. **Win rate comparison:** Do lower-threshold signals have lower WR than the 11 baseline strategies?
2. **Signal quality:** Are the signals actually meaningful or just noise?
3. **P&L impact:** If traded, would they be profitable?

**Kill criteria:** If after Phase 2 a strategy still has zero signals, it's dead. Archive it.
**Promotion criteria:** If after Phase 2 a strategy fires 5+ signals with WR > 35%, it's a candidate for production.

---

## Risk Management

- All changes are **per-strategy**, not global. One bad strategy doesn't affect others.
- All changes are **config-only** (Phase 1) or **parameter-only** (Phase 2). No logic refactoring.
- All changes are **tracked in git** with commit messages referencing this plan.
- **Data collection continues regardless** — every signal (fired or not) is logged.
- **No trading decisions** based on Phase 1-2 data. This is purely validation.

---

## Deployment Plan

See `nofireplan-deploy.md` for the batch job execution plan.
