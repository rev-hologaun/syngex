# Prob Distribution Shift Review — 2026-06-13

## Source: strategies/full_data/prob_distribution_shift.py (~760 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `normalize(net_gamma, 0.0, 2_000)` for gamma score component (c7). While 2000 matches current normalized scale ceiling, using abs() implicitly since net_gamma could be negative for SHORT signals. Component always scores high regardless of gamma direction, losing directional conviction signal. | Gamma score computation | Use directional gamma or add sign-aware scoring |
| info | Momentum ROC window (`KEY_MOMENTUM_ROC_5M`) needs to be populated by main.py from probability momentum calculations. If this rolling key isn't registered in ROLLING_WINDOW_SIZES, it defaults to 300s which may not align with strategy expectations. | Rolling window dependencies | Verify KEY_MOMENTUM_ROC_5M is in ROLLING_WINDOW_SIZES or default config |
| info | Z-score consecutive tracking (KEY_CONSEC_LONG/KEY_CONSEC_SHORT) requires state persistence between evaluations. If gex_calc doesn't properly maintain these counters across ticks, consecutive count resets and gates requiring "2+ consecutive" never fire. | Consecutive gate logic | Verify zscore counter state management |
| info | Capital-weighted breadth check uses per-strike delta × distance-from-ATM contribution. With normalized deltas (much smaller than raw), weighted sums will be proportionally smaller. Thresholds derived from pre-normalization data may need proportional reduction. | Breadth calculation | Verify capital_weight thresholds match normalized scale |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Requires BOTH net_gamma positive AND breaching z-score threshold** — For both LONG and SHORT entries, net_gamma must be positive (line ~156 area). But SHORT signals should logically occur during NEGATIVE gamma regime too. A SHORT position during positive gamma means mean-reverting fade, which contradicts the "probability shift leading indicator" thesis where direction should follow distribution momentum, not gamma regime. | Entry conditions (both LONG and SHORT require positive gamma) | Allow SHORT signals when net_gamma is negative OR remove gamma constraint entirely |
| medium | Probability momentum = Σ(ΔProbITM_i × ΔStrike_i) uses delta as proxy for ProbITM. Delta ≈ ProbITM is a standard approximation but breaks down deeply OTM/ITM where delta diverges from true tail probabilities. During gamma squeeze events, this approximation underestimates real probability shifts. | Core formula concept | Consider using actual IV-based ProbITM instead of delta proxy for accuracy |
| medium | Momentum ROC acceleration ≥10% threshold combined with z-score > 1.5 AND capital breadth threshold creates triple-gate filter. All three must pass simultaneously. This is likely too restrictive — probability distributions shift gradually, and by the time all three filters trigger, the move may already be partially priced in. | Triple-gate filter design | Consider soft gates with graded scoring instead of hard thresholds |
| low | Volume non-declining requirement (FLAT or UP trend) is reasonable but eliminates signals during natural consolidation after big moves. Volume often spikes on the initial shift then declines as market digests. | Volume gate | Consider volume spike + decline combination (initial spike followed by stabilization) |
| info | 10 equal-weight components provide granular confidence scoring. Well-designed architecture that captures multiple dimensions of the probability shift hypothesis. | Confidence design | Apply this multi-component pattern to other strategies |

### Combined Verdict: **FIX — Dual-direction gamma constraint blocks SHORT signals**

Primary fix: allow SHORT signals with negative net_gamma (current requirement forces all signals to be gamma-positive regardless of direction). Secondary: consider softening the triple-gate filter. Strategy logic is sophisticated but over-constrained.
