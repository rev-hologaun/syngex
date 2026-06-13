# extrinsic_intrinsic_flow Code Review

**Date:** 2026-06-13  
**Strategy:** `extrinsic_intrinsic_flow` (full_data layer, v2 Conviction-Master)  
**Run:** June 12 — zero signals despite being enabled

---

## Issues Found

### Critical

**1. gamma_score is clamped to ~0.16 at max, dragging all confidence below MIN_CONFIDENCE**

The `MIN_NET_GAMMA` constant is **5000.0** (line 96), used in the gamma_score formula:
```python
gamma_score = min(1.0, net_gamma / (self._min_net_gamma * 2))  # net_gamma / 10000
```

With `net_gamma_normalized` bounded at ~1608 max, gamma_score caps at **0.161** regardless of how strong the signal is. This is the primary reason confidence never reaches the 0.20 threshold.

The v2 10-component confidence is a simple average of 10 equal-weight components (all 0→1). With gamma_score stuck at 0.16, the maximum achievable confidence (assuming perfect scores on all other 9 components) is:
```
(0.33 + 0.50 + 1.0 + 0.16 + 1.0 + 1.0 + 0.5 + 1.0 + 1.0 + 0.80) / 10 = 0.64
```
But in practice, extrinsic_score (c1) is typically 0.2–0.4 and aggressor_score (c6) is often 0.5–0.7, bringing realistic maximum confidence down to **~0.45–0.55**.

However, the real killer is that **MIN_NET_GAMMA=5000 was calibrated on old cumulative net_gamma in the millions**, not the new normalized per-message-average bounded at ~1608. The divisor should be ~3200 (2× max normalized) not 10000.

**2. MIN_CONFIDENCE docstring/code mismatch**

The docstring (line 15) says "MIN_CONFIDENCE raised from 0.25 → 0.35", but the actual constant is **0.20** (line 87). The code was never updated to match the documentation, suggesting the "v2 Conviction-Master" upgrade was never fully applied. This is misleading for future maintenance.

### High

**3. Legacy confidence methods use MIN_NET_GAMMA=5000 and are dead code**

`_compute_long_confidence`, `_compute_short_confidence`, and `_compute_fade_confidence` all reference `MIN_NET_GAMMA` (line 96) in their gamma component:
```python
gamma_scaled = min(1.0, net_gamma / (MIN_NET_GAMMA * 4))  # net_gamma / 20000
```

These methods are never called — the v2 `_compute_confidence_v2` is used exclusively. But they represent a maintenance liability and confirm the threshold was calibrated on old cumulative values.

**4. Config `min_net_gamma: 5000.0` param is overridden by hardcoded default**

The strategy config specifies `min_net_gamma: 5000.0` (line 297 of strategies.yaml), but `evaluate()` hardcodes the same value as the default:
```python
self._min_net_gamma = self._params.get("min_net_gamma", 5000.0)
```

Even if someone changes the config, the hardcoded module constant `MIN_NET_GAMMA = 5000.0` still appears in the legacy methods and in the c10 confidence component:
```python
c10 = min(1.0, abs(net_gamma) / 2000.0)
```

The c10 divisor of 2000 is also calibrated for old cumulative values (should be ~3200 for normalized).

### Medium

**5. Extrinsic proxy calculation uses cumulative GEX values directly**

`_calculate_extrinsic_proxy` computes `abs(net_delta) * abs(net_gamma_val)` per strike, where `net_gamma_val` is the cumulative gamma (not normalized). This means the extrinsic proxy values grow with message count over time. The rolling window change percentage (`extrinsic_change_pct`) is still valid as a ratio, but the absolute values will drift upward as the session progresses, potentially affecting any future thresholds that reference absolute extrinsic magnitudes.

**6. MIN_DATA_POINTS = 5 conflicts with config min_data_points = 10**

The strategy hardcodes `MIN_DATA_POINTS = 5` (line 82), but the config specifies `min_data_points: 10`. The code uses the hardcoded constant, not the config param. This means the strategy fires with only 5 data points instead of the intended 10, reducing signal reliability.

**7. `_score_delta_skew_coupling` uses wrong signal_type for SHORT**

In `_score_delta_skew_coupling` (line 298), the SHORT case checks `signal_type == "short"` but the callers pass `"expansion"` for both LONG and SHORT (see `_check_long` line 494 and `_check_short` line 649). The skew coupling score will always hit the fallback `return 0.5` for SHORT signals, never computing the actual skew ROC.

### Low

**8. Direction score uses multiplication that zeroes out on any zero component**

```python
direction_score = extrinsic_score * gamma_score * vol_trend_score
```
Since gamma_score maxes at 0.16, direction_score maxes at ~0.05. This value is only written to signal metadata and doesn't gate anything, so it's cosmetic.

**9. FADE signal uses `"expansion"` as signal_type for IV-scaled target**

In `_check_fade`, both the LONG and SHORT fade branches set `fade_signal_type = "expansion"` (lines 823, 829). The IV-scaled target function then uses `base_mult = 1.6` instead of the intended `1.2` for fade signals. The fade target will be 33% wider than intended.

---

## Suggested Fixes

1. **Lower MIN_NET_GAMMA from 5000.0 to ~1600** (or compute it dynamically from observed max normalized gamma). This alone would raise gamma_score from 0.16 to ~0.80 at max, lifting confidence by ~0.064 points.

2. **Fix c10 divisor from 2000.0 to ~3200** (2× max normalized gamma) to match the normalized scale.

3. **Align MIN_CONFIDENCE with documentation** — either set to 0.35 as documented, or update the docstring to reflect the actual 0.20 value.

4. **Use config `min_data_points` instead of hardcoded 5** — change `MIN_DATA_POINTS = 5` to read from `self._params.get("min_data_points", 5)`.

5. **Fix `_score_delta_skew_coupling`** — change the SHORT case check from `"short"` to `"expansion"` to match caller convention, or change callers to pass `"short"`.

6. **Fix FADE signal_type** — use `"fade"` instead of `"expansion"` in `_check_fade` so the IV-scaled target uses `base_mult = 1.2`.

7. **Remove or update legacy confidence methods** — either delete them or update MIN_NET_GAMMA references to match normalized scale.

8. **Consider making MIN_NET_GAMMA a config param** that's actually consumed by all code paths (not just the one that gets overridden).

---

## Root Cause Summary

The strategy **does use `net_gamma_normalized` correctly** (line 150: `data.get("net_gamma_normalized", 0.0)`), so the old API suspicion was partially wrong. The real problem is **threshold calibration**: `MIN_NET_GAMMA = 5000.0` and the c10 divisor of 2000 were set for old cumulative net_gamma values (millions), but the actual data is now bounded at ~1608. This makes gamma_score and c10 structurally weak, pulling the 10-component average confidence below the MIN_CONFIDENCE threshold in nearly all cases.

The extrinsic proxy calculation and rolling window logic are sound — the bottleneck is entirely in the gamma-dependent confidence components.
