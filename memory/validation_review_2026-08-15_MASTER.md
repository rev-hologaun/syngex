# Syngex Validation Code Review — Master Report

**Date:** 2026-08-15 (Sat, evening session)
**Baseline:** v3.221 (`717e531`) — git tree clean at review start
**Method:** 4 parallel reviewers (Archon core + 3 sub-agents) covering: rolling-window/signal-tracker core, engine+ingestor, main.py orchestrator, and all 27 v1/v2 mirrored strategy pairs. Findings verified against real logged TSLA/SPY option data and/or empirical Python tests where possible.
**Scope:** hidden/silent bugs, logic bugs, calculation correctness ("str+int=invalid"), rolling-confidence window correctness, duplicate code, v1/v2 divergence.
**Result:** 35 unique findings (after dedup) — **2 CRITICAL, 4 HIGH, 9 MEDIUM, 12 LOW, 8 OBS/pattern-risk.**

Raw per-review logs (with full evidence + line numbers):
- `memory/validation_review_2026-08-15.md` (core)
- `memory/valreview_subagent_engine_core.md`
- `memory/valreview_subagent_main.md`
- `memory/valreview_subagent_v12_pairs.md`

---

## CRITICAL (fix immediately — silent, whole-signal/whole-strategy failure)

### C1. Prob-Momentum chain is completely dead — main.py reads nonexistent greeks keys
- **File/Lines:** `main.py:1091-1103` (`_calculate_prob_momentum`); consumed `main.py:1646-1666`
- **Issue:** reads `strike_data.get("call_delta")` / `.get("put_delta")`, but `get_greeks_summary()` (engine/gex_calculator.py:426-428) only returns `net_delta`/`call_delta_sum`/`put_delta_sum`. Both keys always default `0.0` → every strike `continue`s → `contributing==0` → **always returns `None`** → `KEY_PROB_MOMENTUM_5M` never pushed → **`prob_distribution_shift` (v1 AND v2) can never fire.** Sibling `_calculate_extrinsic_proxy` (main.py:1034) uses the correct keys, confirming the cut-paste typo.
- **Empirically verified.** Suggests why prob-family strategies are barely represented in analysis.
- **Fix:** use `call_delta_sum` / `put_delta_sum`.

### C2. strike_concentration_v2 "relaxed regime gate" compares net_gamma vs a PRICE percentile — dead feature, 1000× unit mismatch
- **File/Lines:** `strategies/layer3/strike_concentration_v2.py:150-160` (v2 only; base has no such block)
- **Issue:** reads `ng_window = rolling_data.get(KEY_PRICE_5M)` (PRICES), computes 95th percentile of absolute **prices**, then `if abs(net_gamma) >= p95_threshold` where `net_gamma = data["net_gamma_normalized"]` (~0.x). SPX price p95 ~5100 vs gamma ~0.35 → condition never true → the NEGATIVE-regime relaxation **can never fire** (silently dead). `KEY_NET_GAMMA_5M` exists and was almost certainly intended. Cut-paste of the nearby `KEY_PRICE_5M` line. Independently found by 2 reviewers.
- **Fix:** use `KEY_NET_GAMMA_5M`, or replace with a fixed |net_gamma| threshold on the normalized scale.

---

## HIGH

### H1. Gamma wall/flip thresholds are scale-inconsistent across OI feed modes — walls silently never fire (or fire on noise)
- **File:** `engine/gex_calculator.py` `get_gamma_walls`/`get_wall_classifications`/`get_gamma_flip` (~420-610)
- **Issue:** gex = norm_net_gamma×100×price; norm_net_gamma magnitude depends on OI-feed mode. OI=1 (stream) → per-strike |gex| median≈81; real OI → up to 3.6M. Yet strategy thresholds span 10 → 500,000 on the SAME value. `threshold=500_000` fires 0/32 strikes in OI=1 mode (dead gate); `MIN_WALL_GEX=100` fires 32/32 in real-OI (noise); `threshold=10` fires everything. Verified against real parsed TSLA data.
- **Fix:** one canonical GEX unit; make thresholds mode-independent; add a scale-invariance unit test.

### H2. `_normalize_depth_quotes` grabs FULL book-wide exchange map onto EVERY bid/ask entry → per-level summation over-counts by ~levels
- **File:** `ingestor/tradestation_client.py` `_normalize_depth_quotes` (~600-670)
- **Issue:** bid/ask exchange maps computed once over ALL levels, then same dict assigned to every entry; main.py:1993-1996 sums `int(size_str)` per level → ~20× over-count. Feeds conviction score + fragility (main.py:2244-2268) → silent score inflation.
- **Fix:** give each entry ONLY its own venue sizes, or emit at message level.

### H3. delta_volume_exhaustion real R:R gate fixed in _v2 only — v1's "1:1 RR" gate is ineffective (mixed-units)
- **Files:** `strategies/layer2/delta_volume_exhaustion.py:242-248` vs `_v2.py:257-264`
- **Issue:** v1 compares dollar `risk` to dollar `min_stop_distance` (never the target) → enforces nothing; v2 correctly checks `target_dist >= risk * mult`. v1 and v2 fire materially different signal sets (different R:R).
- **Fix:** port the v2 gate into v1 (or flag v1 as ignoring target R:R).

### H4. RollingWindow.p25/p75 quartiles are wrong for most window sizes (calc correctness, gates live signals)
- **File:** `strategies/rolling_window.py:_refresh()`
- **Issue:** custom percentiles use `q1_idx=n/4` + single-index; only matches canonical (numpy-linear) quartiles at n=5,9. Errors of ±0.25 (and varying) for n=3,4,6,7,8,12... Empirically verified:
  - n=4 [1,2,3,4]: reports p25=1.5 (correct 1.75); n=8: 2.5 (correct 2.75); n=6: 2.0 (correct 2.25).
- **Consumers (live gates):** `iv_band_breakout(.py+_v2):478` uses `current_skew <= p25` → "skew compressed" boundary shifts → changes which signals fire. Window is time-based (5m) so `n` varies live → continuously mis-gated.
- **Fix:** implement canonical linear-interpolation quartiles (or nearest-rank consistently), with a unit test vs reference.

---

## MEDIUM

- **M1. regime_conf `/2000`** (shared, both variants) — `strike_concentration(.py/1208,1323 & _v2.py/1281,1398)`: `min(1.0, abs(net_gamma_normalized)/2000)` pins the regime-alignment confidence at its 0.05 floor (normalized gamma ~0.x). Stale cumulative-scale units. Fix: rescale divisor.
- **M2. `int(size_str)` unguarded on depth exchange sizes** (main.py:1994-1997) — one malformed value aborts whole `_on_message`, dropping all metric updates for that tick (both orchestrators, via shared dispatch).
- **M3. `/0.001` epsilon divider when `past_vsi==0`** (main.py:2070-2080) → ±1000 VSI-ROC outliers. Fix: return 0.0 or guard.
- **M4. ROC/accel use positional slots (`[-5]/[-6]/[-10]`) of time-based windows** (main.py:1228,1395,1660,2040,2368...) → time-varying lookback, misleading rates-of-change. Fix: count-based windows or timestamp lookup.
- **M5. Heavy synchronous `_on_message` blocks asyncio loop; shared dispatch couples V1/V2 cadence** (main.py:392,1112) — O(strikes²)/msg stalls resolution + strategy eval + export for both pipelines.
- **M6. `_build_last_trigger` compares open-entry time vs resolved-close time; stale resolved can mask live open** (main.py:2886-2953). Displayed timestamp = close time.
- **M7. `_extract_contracts` compares possibly-string `lastPrice` to int (`price>0`)** → TypeError drops whole option-chain batch (`ingestor/tradestation_client.py` ~700). Fix: `_safe_float` before guard.
- **M8. `get_gamma_flip` sums per-message-normalized gamma** (engine/gex_calculator.py ~460) — high-volume strikes underweighted; flip strike is message-count-sensitive (gamma_flip_breakout/confluence_reversal gates).
- **M9. strike_concentration_v2 SHORT delta soft-penalty hardcodes magic `1.15`/`0.3` instead of constants** (v2.py:590-592) — asymmetric tuning hazard, silently diverges on future edits.

---

## LOW

- **L1.** st like `_update_strike_from_stream` delta==0 → `_infer_side` always "put" (call/put bias); OTM all fall to coarse prob-strike inference (`engine/gex_calculator.py` ~480-560).
- **L2.** `_stream_quotes_loop` only feeds underlying if option-chain sub exists (`_watched_symbol` unset for quotes-only) → dollar GEX silently 0 (`ingestor/tradestation_client.py:203,250`).
- **L3.** `_build_last_trigger` open-signal refetch per-strategy + dead `signal_count` (main.py:3002-3037) — hot wasteful read.
- **L4.** Underlying-price arithmetic `if price > 0` assumes numeric (main.py:1141-1143,1457) — string price → TypeError → whole message dropped.
- **L5.** Gamma walls computed only on heavy ticks (local `gamma_walls_*` resets each msg) → GammaBreaker/IronAnchor/theta_burn silently skip 4/5 ticks (main.py:1216-1224,1457,1580,1693). Staleness.
- **L6.** orb_probe `_parse_option_symbol` doesn't apply decimal-implied strike scaling (orb_probe.py ~210) — fractional strikes parse 10× wrong (probe only).
- **L7.** orb_probe `_parse_depth_line` assumes bids[0]/asks[0] is best level, no sort (orb_probe.py).
- **L8.** RollingWindow.trend never returns "SPIKE" but prob_distribution_shift_v2 `vol_trend_scores` has `"SPIKE":0.2` → dead confidence branch.
- **L9.** strike_concentration_v2 stale comment ("raised 0.25→0.35" vs actual 0.05/0.15).
- **L10.** gamma_squeeze v1 hard-gates net-gamma opposition (`return None`), v2 soft-penalizes (×0.5) — intentional but silent behavioral divergence between "mirror" files.
- **L11.** SignalTracker.pnl_pct is %-of-risk (R×100), not %-of-entry — units doc, could mislead.
- **L12.** gex_imbalance_v2 `_rolling_percentile_threshold` self-includes current value into history when window not full → cold-start bias, warm-start doesn't → inconsistent cold/warm behavior (~line 295).

---

## OBS / pattern-risk

- **O1.** SignalTracker bounded-window (5000) semantic drift — post-restart `get_strategy_stats()`/`get_summary()` reflect last-5000, not lifetime JSONL; heatmap win_rate (main.py:3008) diverges from analysis reports. By-design OOM tradeoff, but silent.
- **O2.** `normalize(v, threshold, threshold*2)` / `normalize(v, threshold, 1.0)` — if threshold>1.0, vmin>vmax → inverted nonsense. Latent across many layer2 strategies; needs constant audit.
- **O3.** Depth-normalized messages carry `symbol:""` (raw feed has no top-level symbol) (`ingestor/tradestation_client.py`).
- **O4.** `services/metrics_api.py` `int(request.args['limit'])` → 500 on non-numeric.
- **O5.** `_active_instances` registry never removes on shutdown; dispatch swallows per-instance errors with bare `pass` (main.py:376,392).
- **O6.** V1/V2 routing currently safe (configs verified: strategies.yaml has 0 `_v2`, strategies_v2.yaml fully `_v2`) but fragile to config drift — primary engine would register stray `_v2` keys; V2 engine would register non-`_v2` keys if suffix dropped.
- **O7.** Duplicate `normalize()` defined identically in 10+ strategy files (duplicate code) — consolidate to one shared helper to prevent drift.
- **O8.** `_score_momentum_acceleration`/`vol_trend_scores` — SPIKE dead-weight coupling (see L8).

---

## CLEARED (verified NOT bugs — important negative evidence)
- **No mixed-type arithmetic in GEXCalculator / greeks path** — type-guards + `_safe_float` cast all string numerics before math.
- **Division-by-zero** all guarded (`count==0`, `price<=0`, denominator checks) across engine/ingestor.
- **Timestamp math** consistent (perf_counter/monotonic/ISO-UTC); no epoch ms-vs-s mismatch found.
- **`_read_tail_lines`** (OOM-fix tail load) correct across single- and multi-chunk boundaries (empirically tested).
- **RollingWindow basic trend/mean/std/zscore** correct for normal cases (empirical tests).
- **RollingWindow.trend hysteresis** retains state correctly across pushes (empirical test 5b).
- **v1/v2 duplicate confidence/avg blocks** (e.g. strike_concentration `_compute_slice_confidence`) byte-identical — no cut-paste error in the 8-component average.
- **`prob_distribution_shift_v2._calculate_momentum`** itself is correct (the dead chain is purely main.py's missing push, C1).

---

## Recommended action order
1. **C1** (prob_momentum keys) — one-line fix, un-deads a whole strategy family.
2. **C2** (strike_concentration_v2 gate) — use KEY_NET_GAMMA_5M.
3. **H3** (delta_volume_exhaustion v1 R:R gate) — port v2 fix to v1.
4. **H4** (rolling_window percentiles) — correct quartile math + unit test (affects iv_band_breakout gates live).
5. **H1/H2** (engine/ingestor scale + double-count) — canonical GEX unit; per-entry exchange sizes.
6. **M3/M2/L4** (epsilon divide, int cast, price-type) — cheap robustness fixes on `_on_message` hot path.
7. **M1/M9** (regime_conf /2000, SHORT delta constants) — strike_concentration tuning bugs.
8. Remaining MED/LOW as triage resources allow.

**No source was modified during this review.** Baseline v3.221 clean. Recommend committing the 4 raw log files + this master report so findings are versioned, then tackling C1-C2 in a follow-up session.
---
## FIX STATUS — C1 + C2 (applied 2026-08-15 22:00 PDT, NOT yet committed)

FIXED:
- C1: main.py `_calculate_prob_momentum` keys -> call_delta_sum/put_delta_sum. Compiles; un-deads prob_momentum + prob_distribution_shift chain.
- C2 (partial): strike_concentration_v2 gate reads KEY_NET_GAMMA_5M (was KEY_PRICE_5M) + import added. Fixes the price-vs-gamma category error.

C2 RESIDUAL (flagged, NOT fixed — needs owner decision): KEY_NET_GAMMA_5M is populated from get_net_gamma() (CUMULATIVE, main.py:1148), but the strategy's net_gamma is net_gamma_normalized (bounded ~0.x). So the gate may STILL under-fire (compares bounded normalized gamma vs percentile of cumulative gamma history). Fixing fully requires either (a) pushing get_normalized_net_gamma() into a dedicated window (NOTE: changing main.py:1148 would silently alter gex_divergence's _window_smoothness behavior — needs separate review), or (b) replacing the percentile with a fixed |net_gamma_normalized| threshold. Safety: this gate only RELAXES NEGATIVE-regime firing; if it stays dead, the strategy is merely MORE conservative in NEGATIVE regime (never reckless). So low-urgency, but the feature remains effectively off until decided.

TESTS: my changes caused ZERO new failures. Full suite = 17 failed / 83 passed on BOTH the clean v3.221 baseline AND with my edits (verified via git stash). The 17 failures are PRE-EXISTING at v3.221, all in untouched files (delta_iv_divergence, delta_volume_exhaustion, gex_imbalance, obi_aggression_flow) — likely stale tests vs v3.220/v3.221 tuning changes. SEE ALSO the "stale tests" note in next-review list.

NOT COMMITTED: changes are in working tree only (main.py + strike_concentration_v2.py). v3.221 baseline intact. Recommend committing as v3.222 after Hologaun reviews the C2 residual decision.

## FIX STATUS — BATCH 2 (H3, M2, M3, L4) — applied 2026-08-16 00:30 PDT, NOT yet committed
- H3: delta_volume_exhaustion.py — moved swing_range/target_frac/target_dist ABOVE the R:R gate;
      gate now `target_dist >= risk` (was broken `risk > min_stop_distance`). Matches v2. Compiles.
      BEHAVIOR NOTE: v1 will now REJECT signals with target < 1x risk → fires few, higher-quality
      signals; v1/v2 now gate consistently. This is a behavioral change, not purely a bug fix.
- M2: main.py _on_message depth exchange `int(size_str)` wrapped in try/except(ValueError,TypeError)
      → skip malformed venue instead of aborting the whole message.
- M3: main.py VSI-ROC past_vsi==0 branch → emit 0.0 (was /0.001 → ±1000 outliers).
- L4: main.py underlying feed price guard — isinstance(str) → float cast before `price > 0`
      (extended line 1132 only; 1479/1535/1698/1798/1920 use calculator.underlying_price which is
      already numeric — confirmed NOT at risk).
Tests: suite = 17 failed / 83 passed — IDENTICAL to baseline (verified). Zero new regressions.
All 6 fixes (C1,C2 + H3,M2,M3,L4) in working tree, uncommitted. Recommend commit as v3.222.

## FIX STATUS — H4 (rolling-window quartiles) — implemented + VERIFIED, not yet committed
- strategies/rolling_window.py: added `_percentile()` canonical linear-interpolation (numpy method-7);
      `_refresh` uses it for p25/p75. Confirmed matches numpy across n=2..24 (0 failures).
      Also fixed a stray `\/` docstring escape (SyntaxWarning).
- tests/strategies/test_rolling_window.py (NEW, 6 tests): reference quartiles n=2..12, numpy cross-check,
      single-value -> None, empty -> None, bottom/top-quartile gate boundaries. ALL PASS.
- iv_band_breakout threshold VERIFICATION (v1 + _v2 both read shared RollingWindow.p25 — no per-file change needed):
  * Hard gate `current_skew <= p25`: MEASURED 0.00% disagreement old-vs-new across n=5..20, 5000 trials each.
    The gate fires at an IDENTICAL rate (old 24-40% == new 24-40%). Boundary VALUE changed but pass/fail
    decisions are unchanged in practice. => NOT looser/tighter at the gate level.
  * Confidence `skew_score = min(1.0, skew_depth/0.05)`: skew_depth increased ~15-20% (e.g. n=8 +0.0109->+0.0131),
    a SMALL continuous bump that may nudge a few borderline signals over MIN_CONFIDENCE. Intended consequence.
  * `/0.05` is an absolute IV-unit scale constant (independent of percentile method) => does NOT need retuning.
  CONCLUSION: H4 fix is SAFE. No threshold compensation required. Confidence effect is small and intended.
- Full suite: 89 passed / 17 failed (was 83/17 baseline) => +6 new tests, ZERO new regressions. Same 17 pre-existing
  failures in untouched files.
- NOTE: analysis/analyzed_all.md was regenerated by an external/scheduled process at 02:48 with --wr-min 0.45
  (unrelated to H4). Reverted it from the working tree so H4 commit stays clean. Not in OpenClaw cron; likely a
  host-level script — flag for Hologaun.
COMMITTED as v3.223 (2026-08-16 04:00 PDT).

## FIX STATUS — H2 (depth-quotes double-count) — implemented + VERIFIED, committed as v3.224
- ingestor/tradestation_client.py `_normalize_depth_quotes`: each bid/ask entry now carries ONLY its
      own venue's exchange size ({venue: size}), not the full-book aggregate map. Aggregates computed
      once over the whole Bids/Asks array and attached to every entry over-counted sizes ~N-levels-fold
      in exchange-flow concentration (main.py 1993-2011) and inflated per-level venue count used by
      fragility (main.py 2273-2274).
- Consumer verification:
  * Exchange Flow Concentration sums (1993-2011): per-entry venue sizes now sum to the correct book-wide
    total per venue (was N-fold inflation).
  * Conviction unique-venue set (2226-2227): unchanged — set-union already deduped, so never inflated.
  * Fragility n_exch (2273-2274): now reflects each level's real venue count (was ~always-max).
    A real correctness fix; makes fragility stricter/less artificially-liquid.
- Tests: 17 failed / 89 passed, IDENTICAL to baseline (89/17). Zero new regressions. ZERO new failures.
- Working tree clean afterwards. All 10 review fixes now committed: C1,C2 (v3.222), H3,M2,M3,L4 (v3.222),
  H4 (v3.223), H2 (v3.224).

## REMAINING RECOMMENDED WORK (from action order)
- H1: engine/gex_calculator.py gamma wall/flip thresholds scale-inconsistent across OI feed modes
      (OI=1 stream vs real DailyOpenInterest span |gex| ~10x-3.6M; thresholds 10->500k fire 0/32 or
      32/32 on the same value). Dead gate on ~15 strategies in stream mode + noise in real-OI mode.
      NOT started — needs owner decision on canonical GEX unit (largest architectural fix).
- Remaining MED/LOW: M1 (regime_conf /2000), M4 (ROC positional slots), M5/M6 (async + last_trigger),
      M7 (string lastPrice guard), M8 (gamma_flip message-count), M9 (SHORT delta constants); L-series.
