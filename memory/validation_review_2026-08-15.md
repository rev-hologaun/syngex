findings log started 2026-08-16T03:51:18Z

# Validation Code Review — 2026-08-15 (Saturday evening session)
Focus (per Hologaun): hidden/silent bugs, logic bugs, calc correctness ("string+int=invalid"),
rolling confidence window correctness, duplicate code. Baseline: v3.221 (717e531).

## CONFIRMED FINDINGS (sex, so far)
### [BUG] RollingWindow.p25/p75 — wrong quartiles for most window sizes (calc correctness, signal-affecting)
- File: strategies/rolling_window.py:_refresh()
- Math uses q1_idx=n/4, reads sorted_vals[int(q1_idx)] and single/index nearest-rank-ish
- Verified vs numpy linear-interp: only n=5 and n=9 match; n=3,4,6,7,8 diverge
  - n=3 [1,2,3]: reports p25=1,p75=3; correct 1.5,2.5
  - n=4 [1,2,3,4]: reports 1.5,3.5; correct 1.75,3.25
  - n=8 [1..8]: 2.5,6.5; correct 2.75,6.25
- CONSUMERS (live signal gates): iv_band_breakout(.py +_v2) line ~478 uses `current_skew <= p25`
  to decide "skew compressed" -> bottom-quartile boundary shifts -> changes which signals fire
- Severity: HIGH (directly gates signals; silent)

### [BUG] gex_imbalance_v2._rolling_percentile_threshold — self-inclusion look-ahead bias (cold vs warm start inconsistency)
- File: strategies/layer1/gex_imbalance_v2.py (~line 295)
- When len(vals)<PERCENTILE_WINDOW: injects current_value into its own history before
  computing threshold AND rank -> self-inclusion biasis rank/threshold upward
- Warm start (full 200 window) does NOT self-include -> silent behavior change across cold/warm
- Severity: MEDIUM (small ~0.5%/point bias; but inconsistent cold/warm)

### [INFO] RollingWindow.trend never returns "SPIKE"
- prob_distribution_shift_v2.py vol_trend_scores has "SPIKE":0.2 but RollingWindow.trend
  only yields UP/DOWN/FLAT -> dead branch / dead confidence weighting
- Severity: LOW (dead code; possibility trend detector was meant to detect spikes)

### [OBS] RollingWindow.trend hysteresis state — verify no reset-between-pushes
- trend getter calls _refresh() then _compute_trend(). _refresh() resets _trend_cache to FLAT
  only if not already UP/DOWN. Empirically strong-up then mild dip stayed UP (test 5b OK).
- No bug found; note for completeness.

### [OBS] SignalTracker bounded-window semantic drift (post-restart stats != lifetime stats)
- File: strategies/signal_tracker.py
- _load_resolved tail-loads only last max_resolved_in_memory (5000) -> _update_strategy_stats
  running sums/wins/losses/win_rate reflect last 5000, not full JSONL history
- get_strategy_stats()/get_summary() after restart = window-relative; during live session =
  full accumulation -> same strategy's stats differ across restart. Heatmap (main.py
  _build_strategy_health) reads window-relative win_rate.
- By-design OOM tradeoff, but silent drift; downstream heatmap numbers diverge from analysis
  reports (which read full JSONL). Severity: MEDIUM-OBS (display, not trade gating).

### [OBS] pnl_pct is %-of-risk (R-multiple*100), not %-of-entry
- File: strategies/signal_tracker.py:_resolve_signal  pnl_pct=(pnl/risk*100)
- Internally consistent across WIN/LOSS/CLOSED; naming could mislead (not true return %)
- Severity: LOW (units doc)

### [BUG] strike_concentration_v2 — NEGATIVE-regime relaxation gate compares gamma vs PRICE percentile (unit/scale mismatch, dead gate)
- File: strategies/layer3/strike_concentration_v2.py (~line 155-162)
- Uses ng_window = rolling_data.get(KEY_PRICE_5M)  (PRICES)
  sorted_vals = sorted(abs prices); p95_idx=int(n*0.95)-1; threshold=price_p95
  then `if abs(net_gamma) >= p95_threshold: _regime_ok=True`
- net_gamma_normalized = per-message avg net gamma (gamma units, e.g. ~hundreds/thousands),
  price ~ hundreds. Compare gamma vs price percentile -> unit/scale mismatch, effectively
  dead relax gate (or spurious).
- KEY_NET_GAMMA_5M exists (rolling_keys.py:13) -> almost certainly meant to be used here.
- Base (v1) strike_concentration.py does NOT have this relaxation block -> v1/v2 divergence.
- Severity: HIGH (silent logic bug, dead gate)

### [OBS] main.py _build_last_trigger — compares open-signal entry timestamp vs resolved resolution timestamp (inconsistent timebase)
- File: main.py ~line 2912-2940 (_build_last_trigger)
- open_by_strat keyed on sig.timestamp (entry); resolved_by_strat keyed on resolution_time
- Merge: last = open_sig if open_sig["ts"] >= resolved_sig["ts"] else resolved_sig
  -> compares signal-ENTRY time against signal-RESOLUTION time (different clocks/base).
  A resolved signal from minutes ago (resolution_time large) beats a NEWER open signal (entry ts).
  Displays/uses the resolved one instead of the still-open newer one.
- Severity: LOW-MED (display "last trigger"); could matter if used to dedupe refires.

### [PATTERN-RISK] normalize(v, threshold, threshold*2) and normalize(v, threshold, 1.0)
- If threshold constant > 1.0 or threshold > 1.0, vmin>vmax causes inverted/nonsense normalization.
- Many layer2 strategies use this pattern. Needs constant-value audit (sub-agent checking pairs).
- Severity: CHECK (latent)
