# gamma_breaker Code Review

**Date:** 2026-06-13  
**Strategy:** `strategies/full_data/gamma_breaker.py`  
**Status:** Zero signals in June 12 run despite being enabled in config

---

## Issues Found

### Critical

1. **Rolling data keys never populated (strategy starved)**
   - The 5 rolling keys used by this strategy (`wall_distance_5m`, `wall_gex_5m`, `wall_gex_sigma_5m`, `price_velocity_5m`, `gamma_break_5m`) are only pushed in `main.py` lines 1262–1280, inside the `gamma_walls_100k` block.
   - That block runs on a 5-second timer. If no gamma walls ≥$100K GEX are found in a cycle, **none of these windows receive any data**.
   - The strategy checks `gamma_break_window.count < 2` and returns `[]` immediately — the most common early exit path. This is the primary reason zero signals fired.

2. **`NameError` in confidence formula (line 337)**
   ```python
   if getattr(self, '_regime_mismatch', False):
       confidence *= 0.7  # NameError: 'confidence' not defined yet
   ```
   - `confidence` is assigned on line 349 (`confidence = (c1 + c2 + c3 + c4 + c5) / 5.0`), but line 337 references it before assignment. This will raise `UnboundLocalError` whenever `_regime_mismatch` is True, crashing the confidence computation.

### High

3. **Wall GEX normalization ceiling is wrong**
   - Line 347: `c5 = normalize(current_wall_gex, 0.0, 1000000.0)`
   - `current_wall_gex` comes from `get_gamma_walls(threshold=100000)` which uses **normalized** (per-message-average) GEX: `gex = norm_net_gamma * 100 * price`.
   - With max observed `net_gamma_normalized ≈ 1608` and SYNGEX price ~$100, individual wall GEX values are in the range of ~100K–16M. A 1M ceiling means most walls normalize to 1.0 (capped) or 0.0 (below threshold), destroying discrimination.
   - Should use the actual max observed wall GEX or a dynamic percentile-based ceiling.

4. **Volume confirmation gate too strict (Gate C)**
   - Line 307: `return current_vol >= avg_vol * volume_spike_mult` where `volume_spike_mult` defaults to 1.5.
   - Requires volume to be ≥150% of 5-minute average. In normal trading conditions this rarely fires, causing consistent Gate C failures even when other conditions are met.

5. **Gamma break index uses cumulative (not normalized) net gamma**
   - `main.py` line 1249: `gamma_concentration = abs(wall_gex) / avg_gex`
   - Both `wall_gex` and `avg_gex` come from `get_gamma_walls()` which already uses normalized GEX, so this particular computation is actually correct. However, the comment in the strategy docstring says "Gamma_Concentration_at_Level" implying a ratio of cumulative values, which is misleading.

### Medium

6. **Gate B (regime alignment) is a no-op**
   - Lines 287–293: Returns `True` in both branches, including the `self._regime_mismatch = True; return True` fallback.
   - The docstring says LONG requires POSITIVE regime and SHORT requires NEGATIVE regime, but the code always passes. The `_regime_mismatch` flag is set but only used in the broken confidence formula (issue #2).

7. **Long/short signal logic is identical**
   - Lines 125–136: `long_signal` and `short_signal` use the exact same condition: `current_gamma_break > min_gamma_break and velocity_accelerating`.
   - Direction is determined solely by regime (line 142), not by which wall (call vs put) is being broken. The strategy's own docstring says "LONG when price above nearest call wall" but the code doesn't check wall side at all.

8. **Wall GEX sigma computation uses population std on raw GEX**
   - `main.py` lines 1270–1274: computes std of `abs(wall_gex)` values. Since `wall_gex` values can range from 100K to 16M+, the sigma will be dominated by the largest wall and may not meaningfully distinguish "major" from "minor" walls.

### Low

9. **`min_gamma_break` threshold too low**
   - Default 0.0005. Gamma break = velocity × gamma_concentration. Even modest velocity with concentration ≥1 easily exceeds this. The threshold provides almost no filtering.

10. **Gamma break direction not used**
    - The strategy computes `current_gamma_break` as a positive value (velocity is `abs(...)`, concentration is `abs(...)`) but the docstring implies positive/negative direction should matter. The strategy never uses the sign of the break or the wall side (call vs put).

11. **`_regime_mismatch` flag inconsistency**
    - `_regime_mismatch` is set in `_gate_b_gex_regime` but the gate always returns True, so the flag is set whenever regime doesn't match direction, yet the gate doesn't actually block. This creates a phantom "regime mismatch" state that feeds into the broken confidence formula.

## Suggested Fixes

1. **Fix rolling data population:** Ensure the 5 rolling keys are populated every cycle, not just when gamma walls are found. Either:
   - Push zero/NaN values for the keys when no walls exist, or
   - Move the rolling data push outside the `if walls:` block so it always fires.

2. **Fix confidence NameError:** Move the regime-mismatch penalty to after `confidence` is computed:
   ```python
   confidence = (c1 + c2 + c3 + c4 + c5) / 5.0
   if getattr(self, '_regime_mismatch', False):
       confidence *= 0.7
   ```

3. **Recalibrate wall GEX normalization:** Replace the hardcoded 1M ceiling with either:
   - A dynamic value from `rolling_data.get(KEY_WALL_GEX_5M)` max, or
   - A reasonable ceiling based on observed max wall GEX (e.g., 20M for SYNGEX at $100).

4. **Relax volume confirmation:** Reduce `volume_spike_mult` default from 1.5 to 1.1 or make it configurable per-strategy with a lower default.

5. **Fix Gate B:** Make it actually enforce regime alignment (return False on mismatch) or remove the regime-soft flag entirely.

6. **Differentiate long/short signals:** Use wall side (`nearest_wall["side"]`) to determine direction instead of relying solely on regime. Add a check that LONG signals correspond to call walls and SHORT to put walls.

7. **Increase `min_gamma_break` default** to something more discriminating (e.g., 0.01 or 0.05) or compute it dynamically from rolling statistics.
