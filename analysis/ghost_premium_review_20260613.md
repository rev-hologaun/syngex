# Ghost Premium Review — 2026-06-13

## Source: strategies/full_data/ghost_premium.py (~380 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `_gate_a_ask_size()` uses `pdr_window.std` as proxy for ask_size volatility, but pdr values are ratios (0→3+), not ask_size counts. The std of PDR is a measure of PDR variance, not ask_size variance. Gate A may pass when it shouldn't because the metric doesn't match the gate description. | Lines ~215-239 | Either compute actual ask_size sigma from option update data OR rename gate to reflect what's actually being checked |
| warning | `c3 = normalize(ask_size_sigma, 0.0, 5.0)` in confidence — if ask_size_sigma is derived from PDR.std (which ranges maybe 0-0.5), this will always return very low confidence contribution. The normalization scale mismatch reduces component impact to near-zero. | Line ~362 | Adjust vmax to realistic range or use different metric |
| info | Gate B stability check defaults to True when IV window isn't available. While conservative ("don't block on uncertain data"), this effectively makes Gate B always-pass when iv_window isn't provided. | Lines ~242-258 | Add explicit logging when gate B passes by default |
| info | Strategy ONLY evaluates call options (PDR > 0). Put-side ghost premium scenarios are ignored entirely. This limits strategy applicability by half. | Evaluate method | Consider adding symmetric put evaluation path |
| info | _classify_intensity thresholds (0.60/1.00/1.50) are hardcoded. These should be configurable params that match the PDR_TRIGGER threshold. | Lines ~379-388 | Tie intensity thresholds to min_pdr param |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Gate A misnamed/misimplemented** — The docstring says "ask_size > 2σ above rolling avg ask_size" but implementation checks `latest_PDR > mean_PDR + 2σ_PDR`. It's checking PDR divergence from its own mean, not ask_size at all. This means Gate A fires whenever PDR has recently spiked relative to its history, NOT when liquidity is elevated. | Lines ~215-239 | Decide: either fix Gate A to check actual ask_size data, or rename gate and document what it really does |
| medium | PDR trigger at 0.60 (60% overpriced) is aggressive but reasonable for detecting speculative extremes. However, during earnings/IV-expansion events, ALL options can be 60%+ overpriced simultaneously, reducing signal specificity. | Logic ~112 | Consider adding regime filter (block during earnings windows) |
| medium | Confidence components c3 (ask_size_sigma) and c5 (net_gamma) both contribute near-zero because of scale mismatches. Effective confidence comes from only c1 (PDR magnitude), c2 (velocity), and c4 (IV ratio). Three components carry 90%+ weight despite 5-component design. | Component analysis | Re-normalize or remove underperforming components |
| medium | Strategy produces LONG-only signals. For overpriced puts (negative PDR / mid < theoretical), there's no SHORT signal. Missing half the market opportunity. | Single-direction design | Add put-side evaluation for completeness |
| low | `abs(current_pdr_roc) < 0.2` normalization range assumes PDR ROC stays below 20%. During fast moves, PDR can change faster. Clamp handles overflow but loses differentiation at extremes. | Line ~357 | Consider log-scale normalization for velocity |
| info | Gate B allows through even when underlying is moving > 2%, as long as IV alignment check passes. In practice, IV_roc comparisons with PDR are comparing apples-to-oranges (one is %/minute, other is ratio). | Lines ~242-258 | Document assumptions or reconsider alignment logic |

### Combined Verdict: **FIX — Gate A implements wrong check + single-direction limitation**

Fix Gate A to either check real ask_size or rename and re-specify. Consider adding put-side SHORT evaluation. Confidence scoring needs component scale fixes. Moderate complexity fix.
