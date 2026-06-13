# IV-GEX Divergence Review — 2026-06-13

## Source: strategies/layer2/iv_gex_divergence.py (~980 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `MIN_POSITIVE_GAMMA = 200000` is a hard-coded old-scale threshold (comment says "$200k net gamma cumulative"). With normalized max ~1600, this check would block all signals if used. Check if this constant is actually applied anywhere or just documented. | Line ~17 | Search usages; remove or adjust to 2000 |
| info | `normalize(net_gamma, 0.0, 2000.0)` — correct scale for normalized gamma. Good. But c5 in some confidence methods uses abs(normalized) which can distort directional sensitivity. | Various `_compute_confidence` methods | Verify directional vs magnitude scoring consistency |
| info | Wall stop calculation (`WALL_STOP_BUFFER_PCT = 0.002`) computes wall distance and places stops beyond nearest wall. If get_wall_classifications() returns walls using old-scale thresholds, no walls will be found and fallback stop (FALLBACK_STOP_PCT = 0.006) always applies. | Wall stop logic | Verify wall classification thresholds match normalized data |
| info | Multiple normalize() calls with different v_max values across LONG and SHORT confidence computations: some use 2000, some use 5_000_000. Need consistent audit of ALL normalization ceilings. | Throughout file | Create centralized normalizer or audit function |
| info | `_score_iv_skew_acceleration` divides by `abs(mean_skew_roc) + 0.01`. The small epsilon prevents div-by-zero but makes near-zero ROC give inflated scores. | Skew acceleration scoring | Document epsilon rationale; consider larger epsilon like 0.05 |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Confidence uses 10 components but c5-c10 are weighted differently than c1-c4** — Component weighting isn't uniform despite "simple average" documentation. c1-c4 are normalized [0-1], but c5-gamma-direction uses abs(γ)/2000 while c10 also references same ratio. There's potential double-counting of gamma magnitude across multiple components. | Component analysis | De-duplicate gamma references; ensure each component captures unique information |
| medium | IV expanding/crashing gates use rolling average thresholds that depend on window being properly populated from main.py. If iv_skew_gradient or iv_skew_roc windows aren't initialized, these gates return early without signal. Cross-check with rolling_keys.py to verify KEY_IV_SKEW_GRADIENT_5M is registered. | _check_iv_expanding/_check_iv_crashing | Verify window initialization in main.py |
| medium | Price percentile gate: LONG requires price ≤ p40, SHORT requires price ≥ p60. These use the same rolling window (KEY_PRICE_30M). For mean-reversion strategy, this correctly targets extremes. However, at low volatility, the 30m range shrinks making it harder to reach percentile extremes. | Price percentile logic | Consider adaptive percentile threshold based on realized vol regime |
| medium | Gamma density gradient check requires declining gamma within ±1% of price. This is tight spatial tolerance AND requires declining trend. Dual constraints may rarely fire simultaneously during actual trading sessions. | Gamma density score | Evaluate firing rate; may need wider window or relaxed decline requirement |
| low | Volume conviction weight (component 4) uses log(volume) as mentioned in docstring but code shows `min(1.0, total_volume / 100_000.0)` — linear not log-scale. Docstring mismatch. | Component 4 analysis | Align code with doc: either add log transformation or update comment |
| info | Bidirectional design evaluates SHORT and LONG independently and can emit both simultaneously. Unlike most other strategies (single signal), this supports dual signals. Useful for extreme regime transitions. | evaluate() method | Good design pattern; document when dual signals expected |

### Combined Verdict: **REVIEW — Well-designed but needs scale audit**

No critical blockers identified. Primary concerns: verify MIN_POSITIVE_GAMMA threshold usage, audit ALL normalize vmax parameters, check wall classification compatibility with normalized data. Strategy architecture is sound and likely fires under appropriate extreme conditions.
