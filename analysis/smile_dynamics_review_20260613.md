# IV Smile Dynamics Review — 2026-06-13

## Source: strategies/full_data/smile_dynamics.py (~378 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `normalize(put_slope, 0.0, 0.5)` and `normalize(call_slope, 0.0, 0.5)` — same ceiling issue as skew_dynamics (its sibling strategy). Put/call slopes that exceed ±0.5 during extreme events always normalize to exactly 1.0, losing differentiation between moderately steep and extremely steep smiles. | Slope normalizations ~228-232 | Consider log-scale normalization or adaptive v_max |
| info | `_safe_get_walls()` calls gex_calc methods that may not exist. Wrapped in try/except returning empty list on failure. Silent swallow means no diagnostic logging when wall lookups fail. | Wall helper method | Add debug logging for missing gex_calc methods |
| info | Strategy depends on KEY_CURVE_OMEGA_5M (Ω), KEY_PUT_SLOPE_5M, KEY_CALL_SLOPE_5M being populated by main.py. These are custom keys that must be explicitly registered. If main.py doesn't compute the Curvature Asymmetry Index, all rolling windows will be empty. | Rolling window deps | Verify key registration in ROLLING_WINDOW_SIZES (mapped to 900s) |
| info | Direction selection uses long_dir_score >= short_dir_score comparison. No absolute floor — the higher of two weak scores fires even if both are essentially noise. Compare with skew_dynamics which has same pattern. | Direction scoring | Consider adding minimum absolute score per direction |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Same Ψ-scale problem as sibling strategy skew_dynamics** — Ω magnitude normalized against vmax=5.0 (`normalize(abs_omega, 0.0, 5.0)`). Typical Ω values (ratio of put slope to call slope magnitudes) range from near-zero to maybe 2-3 for extreme smiles. A value of 2.0 only scores 0.4 confidence contribution. Primary component contributes very little. | Omega magnitude line ~225 | Reduce vmax to 3.0 or dynamically based on observed Ω range |
| medium | Curvature asymmetry ratio Ω = |Slope_Put_Wing| / |Slope_Call_Wing|. When call wing is flat (slope ≈ 0), division produces extremely large Ω values (>10) that dominate scoring and create instability. The normalization handles overflow but creates "all-or-nothing" scoring where any tiny call slope change swings Ω from 0.1 to 100+. | Division-by-flat-slope edge case | Add minimum slope floor before computing ratio (e.g., slope > 0.01 required) |
| medium | GEX regime alignment gives binary 1.0/0.0 scoring similar to skew_dynamics. POSITIVE→LONG, NEGATIVE→SHORT. But the smile dynamics thesis (curvature shifts leading price moves) should work across regimes — curvature changes indicate market sentiment regardless of gamma sign. | Regime gating | Consider making regime a soft score rather than binary gate |
| low | Volume liquidity score uses recent 5m volume normalized to 10k ceiling. For options contracts with much higher trading volumes (millions of contracts daily), this caps out at 1.0 constantly, making volume a non-differentiating factor. | Volume scoring | Use session-relative volume instead of absolute threshold |
| info | Strategy conceptually pairs perfectly with skew_dynamics: Ψ measures vertical skew shift, Ω measures smile curvature asymmetry. Together they form a complete volatility surface analysis. Running both could provide complementary signals. | Cross-strategy synergy | Consider cross-strategy confidence boost when both fire |
| info | Clean architecture mirrors skew_dynamics design. Both use the same soft-gate pattern (A-D scores) mapped to different metrics (Ψ vs Ω). Good modular design. | Design quality | Maintain consistent API between sibling strategies |

### Combined Verdict: **FIX — Scale mismatch + flat-slope edge case**

Primary fix: reduce Ω normalization vmax from 5.0 to 3.0 (or dynamic). Secondary: add minimum slope floor before computing ratio to prevent numerical instability. Strategy is sibling to skew_dynamics; fix both together.
