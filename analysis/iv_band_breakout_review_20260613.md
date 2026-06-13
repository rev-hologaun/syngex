# IV Band Breakout Review — 2026-06-13

## Source: strategies/layer3/iv_band_breakout.py (~862 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `normalize(current_wall_gex, 0.0, 1_000_000)` doesn't exist in this file but similar patterns appear: c5 normalizes wall GEX data that may use old cumulative scales. Check for any normalize() calls with large v_max values that don't match normalized input. | Review confidence components | Audit all normalize() vmax parameters against actual data ranges |
| info | `SKEW_COMPRESSION_PCT = 0.25` requires skew to be in bottom 25% of rolling range. This is strict but appropriate for compression detection. However, if the rolling window doesn't cover a full compression cycle, the threshold adapts incorrectly. | Line ~90 | Document assumption about window covering full market cycle |
| info | `_compute_atm_strike()` tries `gex_calc.get_atm_strike(price)` first, falls back to nearest strike. The fallback logic uses `min(walls, key=abs_diff)` which assumes walls have "strike" field. If greeks_summary provides strikes instead, both paths should work consistently. | _check_long/_check_short methods | Ensure consistent strike resolution across all code paths |
| info | Gate D checks delta acceleration ≥10% (`DELTA_ACCEL_THRESHOLD = 1.10`). For SHORT, it's ≤-10%. Both require magnitude ≥0.10 deviation from baseline. Hard-coded thresholds in constants; consider making configurable. | Constants ~84-96 | Add to params dict for hot-reload capability |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Delta acceleration check for SHORT compares absolute value** — `abs(delta_accel - 1.0) >= 0.10` works for LONG (delta_accel > 1.10) but for SHORT where delta_accel < 0.90, same formula gives `(0.90-1.0)=−0.10 abs=0.10 → passes`. This means weak decline (-10%) passes as easily as strong breakouts (>+10%). For SHORT signals, you want DECLINING delta, not just deviation. | Delta acceleration gate | Verify direction-awareness: SHORT needs delta moving DOWN, not any deviation |
| medium | Skew width computation uses OTM ±5% strikes. With normalized IV values (0-1 range), the absolute difference between OTM put IV and OTM call IV will be small numbers. The compression ratio calculation must account for this — verify math holds at scale. | Skew compression logic | Test with known compressed/expanding regimes |
| medium | Price compression check: range < 30% (or 40%) of rolling mean range. At very low volatility (range ≈ 0), division or comparison becomes unstable. Add minimum range floor before computing ratios. | Price compression gate | Add floor: if rolling_mean_range < 0.01, skip compression check |
| medium | Strategy requires regime NOT NEUTRAL. In transition periods near gamma flip, strategy is blind. This is correct behavior but means entire sessions could produce zero signals during regime transitions. | Regime check | Accept as correct by design; document expected coverage gaps |
| low | Target scaling uses `TARGET_IV_EXPANSION_MULT * (current_iv / mean_iv)` capped at 4.0×. If current_iv equals mean_iv (no expansion), target multiplier stays at base (2.5 positive / 1.5 negative). This might give asymmetric targets even for symmetric setups. | Target computation | Consider symmetrizing base multipliers or adding IV-change dependency |
| info | 6-component confidence model with weighted components (not equal) — weights sum to 1.0 explicitly. Well-designed compared to other strategies using naive averages. | Confidence method | Good pattern; apply to other strategies |

### Combined Verdict: **REVIEW — Solid design, minor calibration needed**

No critical bugs found. Direction-awareness of delta acceleration needs verification. Compression floors need edge-case handling. Generally well-built strategy that likely needs parameter tuning rather than structural fixes.
