# SYNGEX Release Notes — v4.006

**Date:** 2026-05-31  
**Build Type:** Bugfix + performance + architecture cleanup

## Summary

This release seals the "Hidden Logic Leak" — a systemic bug where raw market data strings were treated as numeric values without consistent casting, causing silent calculation corruption across 40+ strategies. It also includes performance improvements to the rolling window engine and several code quality cleanups.

## Changes Since v4.005

### 🐛 Bugfixes

- **Hidden Logic Leak (CRITICAL)** — Centralized numeric type casting at the ingestor layer. The TradeStation API returns numeric fields as strings (e.g., `"Size": "150"`, `"Gamma": "0.02"`). Previously, these strings flowed through multiple layers without casting, causing silent corruption in strategy calculations. Fixed by:
  - Adding `_safe_int()` / `_safe_float()` helpers with try/except to all three ingestor normalizers
  - Adding type guards in `GEXCalculator._update_strike` that log and cast any string-encoded fields
  - Ensuring `get_greeks_summary()` always returns floats
  - Adding explicit `float()` casts in `_build_depth_snapshot()`
  - Adding casts to `_process_raw_option_chain()` fallback path

- **gamma_walls_500k NameError** — Fixed undefined variable in `_report_profile()` by storing on `self`

### ⚡ Performance

- **RollingWindow lazy-eval caches** — Added caching for mean, median, std, min, max, percentiles, and trend. Values are only computed when first accessed and invalidated on push. Reduces redundant computation during high-frequency strategy evaluation.
- **RollingWindow hard cap** — Added `_hard_cap` (2000 entries) for time-based windows to prevent unbounded memory growth.

### 🧹 Code Quality

- Downgraded type guard log level from `error` to `debug` (prevents log flooding at market open)
- Moved `_safe_int()` / `_safe_float()` from local function definitions to module level
- Removed redundant `int()` casts on already-cast fields
- Removed duplicate `_strike_delta_cache` / `_strike_iv_cache` declarations
- Added casts to `_process_raw_option_chain()` for consistency with `_extract_contracts`

### 📊 Strategy Config

- Disabled global max hold times (set to 0)
- Disabled all per-strategy max hold times (set to 0)
- Updated strategy analysis report with rolling confidence specification

### 📄 Documentation

- Added `hidden_logic_leak.md` — full analysis of the bug, affected strategies, and fix
- Added `normalizer_plan.md` — implementation plan and execution tracking

## Impact

The Hidden Logic Leak fix is the highest-impact change. Strategies that were silently producing corrupted signals (or failing to fire entirely) due to string-numeric confusion should now operate correctly with real market data.
