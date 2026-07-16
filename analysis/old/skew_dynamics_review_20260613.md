# Skew Dynamics Review — 2026-06-13

## Source: strategies/full_data/skew_dynamics.py (~328 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `_compute_confidence()` uses `normalize(put_slope, 0.0, 0.5)` and `normalize(call_slope, 0.0, 0.5)`. Put/call slopes are IV gradient measurements that can exceed ±0.5 during extreme skew events. Both components will cap at 1.0 regardless of how extreme the actual slope is beyond 0.5. This means the strategy can't distinguish between "steep" and "extremely steep" skew. | Slope normalization ~235-240 | Consider log-scale or adaptive vmax based on realized volatility regime |
| info | Strategy doesn't call get_normalized_net_gamma() explicitly but may receive net_gamma through greeks_summary dict. Verify that gamma-based confidence components (c7, c10) work with available data sources. | Confidence component analysis | Ensure gamma data is populated before evaluation |
| info | Ψ computation formula `(IV_Put_Wing - IV_Call_Wing) / IV_ATM` requires all three IV values to be populated. If wing strikes aren't tracked properly in main.py's rolling window population, Ψ will be None and strategy returns []. | Core formula dependency | Verify KEY_SKEW_PSI_5M is populated by main.py |
| info | Soft scores (A-D) have no hard gates except directional selection. This means even weak Ψ movements produce signals if they clear MIN_CONFIDENCE. The direction-specific scoring ensures only the stronger signal fires, which is efficient filtering. | Soft gate design | Good design pattern |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Ψ magnitude normalization range is [0.0, 5.0]** — c1 normalizes abs(Ψ) against vmax=5.0. Typical Ψ values range from -0.5 to +0.5 for most options chains. At this scale, even extreme Ψ=±0.5 gives score of 0.1. Most market conditions give <0.05. This effectively makes the primary magnitude component non-contributory, pushing total confidence below MIN_CONFIDENCE. | Line ~230 (`normalize(abs_skew_psi, 0.0, 5.0)`) | Reduce vmax to 1.0 to match actual Ψ range |
| medium | GEX regime alignment gives binary 1.0/0.0 (POSITIVE→LONG only, NEGATIVE→SHORT only). No gradient for strength-of-regime. A barely-positive-gamma regime gives same 1.0 as strongly-positive. This could allow signals in marginal regimes where mean-reversion thesis is weakest. | Regime scoring | Add continuous regime strength factor |
| medium | Liquidity score combines OI × volume of wing strikes above rolling 1h threshold. This is conceptually sound but the 1h window (ROLLING_WINDOW_SIZES maps these keys to 900s) may not capture intraday liquidity shifts well enough. During rapid IV changes, a 15-min window might be more responsive than 1h. | Liquidity gate | Evaluate window size vs responsiveness tradeoff |
| medium | Direction selection picks highest score (long_dir_score >= short_dir_score → LONG, else SHORT) WITHOUT requiring a minimum absolute score. A very weak LONG score of 0.18 vs SHORT of 0.17 produces a marginally-confident LONG signal. The comparison mechanism works even when both signals are essentially noise. | Direction selection | Add absolute minimum threshold per direction before comparing |
| low | Z-score significance component uses Ψ_sigma from rolling window. During trending markets where skew continuously moves in one direction, Ψ_sigma increases (larger standard deviation), making current moves appear less significant. Counter-intuitive: trending markets suppress signals precisely when skew dynamics should be most active. | Z-score component | Consider using rolling median absolute deviation instead of std for robustness |
| info | Clean architecture: computes Ψ once, derives ROC and sigma automatically, applies soft scoring uniformly. No duplicated logic between LONG and SHORT paths. | Code quality | Model to follow for other strategies |

### Combined Verdict: **FIX — Ψ normalization ceiling too high**

Primary fix: reduce Ψ magnitude normalization vmax from 5.0 to 1.0 (or dynamically based on observed range). Secondary: add absolute score floor before direction comparison. Strategy concept is elegant; just needs calibration.
