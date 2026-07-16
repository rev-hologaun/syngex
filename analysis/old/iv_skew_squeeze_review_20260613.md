# IV Skew Squeeze Review — 2026-06-13

## Source: strategies/full_data/iv_skew_squeeze.py (~738 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `normalize(current_skew, 0.0, 10.0)` for skew extremity component (c4). Actual IV skew ranges from roughly -0.5 to +0.5 in normalized terms, so vmax of 10.0 means all values normalize to near-zero contribution. This effectively makes skew extremity a non-factor in confidence scoring. | Line ~462 (`c4 = normalize(current_skew, 0.0, 10.0)`) | Reduce vmax to match actual skew range (~1.0 or less) |
| warning | GAMMA_CEILING = 2000.0 is defined but only used as comment reference. The actual net_gamma normalization uses `/2000.0` inline throughout confidence calculations. Both agree at 2000, which matches current scale. Good — no old-scale bug here. | N/A | Verify consistency across all references |
| info | MIN_CONFIDENCE = 0.20 despite docstring saying "raised from 0.25 to 0.35 for v2". Comment discrepancy. Either INTENT was 0.35 and value is wrong, or doc is stale and 0.20 is correct. | Line ~60 | Verify intended value against design spec |
| info | Volume fragility threshold `VOL_FRAGILE_THRESHOLD = 0.30` means volume below 30% of average triggers fragile flag. This is aggressive — normal market activity can dip below 30% during low-volume periods (midday lull), potentially blocking signals unnecessarily. | Constants section | Consider adaptive fragility based on time-of-day or rolling baseline |
| info | Target computation doesn't have explicit floor/ceiling unlike other strategies. If vol_ratio approaches zero, target calculation could produce degenerate targets. | Target computation methods | Add min/max target guards |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Skew extremity normalization scale mismatch** — c4 uses normalize(current_skew, 0.0, 10.0) where actual skew is [-0.07, +0.20] range. Normalized contribution will be ~0.01-0.02 instead of meaningful differentiation. One-fifth of confidence components essentially do nothing. | Line ~462 | Change vmax to 1.0 or dynamic scale |
| medium | Skew extreme thresholds (SKEW_EXTREME_POSITIVE = 0.20, SKEW_EXTREME_NEGATIVE = -0.07) are asymmetric — positive skew must be 3× more extreme than negative to trigger. This intentional asymmetry may reflect historical skew behavior, but verify it wasn't copied from old unnormalized data. | Lines ~49-50 | Validate thresholds against current normalized skew distribution |
| medium | Delta-skew convergence gate checks delta_roc alignment with skew ROC direction. But KEY_DELTA_ROC_5M window depends on total_delta rolling changes. With normalized gamma/delta values, absolute ROC magnitudes differ significantly from pre-normalization values. Gate thresholds may need recalibration. | Delta-skew convergence logic | Re-test gate threshold against current data distributions |
| medium | Volume-weighted stability requires volume > mean_vol * 1.5 (VOLUME_SPIKE_THRESHOLD). Combined with price stability (<0.5% change), both conditions must hold simultaneously. These are orthogonal requirements that rarely coexist: stable prices typically have lower volume. | Stability check logic | Consider AND → OR logic OR reduce strictness |
| low | Net gamma strength component in confidence always uses abs(net_gamma)/2000 regardless of signal direction. For LONG signals during negative gamma regime, this gives full credit when actually conflicting with regime. Direction-aware gamma scoring would be better. | Net gamma component | Make gamma score directional |
| info | Strategy correctly handles BOTH skew directions (+ve → SHORT, -ve → LONG) with symmetric evaluation paths. Good bidirectional pattern. | evaluate() method | Apply this symmetry pattern to other unidirectional strategies |

### Combined Verdict: **FIX — Scale mismatch blocks key confidence component**

Fix skew extremity normalization (vmax too high by factor of 50+). Then re-evaluate whether MIN_CONFIDENCE should be 0.20 or 0.35 per docs. Core strategy concept is solid.
