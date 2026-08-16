# Engine/Core/Ingestor Validation Review — 2026-08-15
Reviewer: Archon subagent (engine/core/ingestor path)
Baseline: v3.221 (717e531). READ-ONLY review. Findings verified against real logged TSLA/SPY option data in data/level2/ and spy-options.log where noted.

Scope covered: engine/gex_calculator.py, ingestor/tradestation_client.py, services/metrics_api.py, data_pipeline.py, orb_probe.py (core/ and api/ are empty). Timestamp math (epoch ms vs s) checked across scope files: all consistent (perf_counter/monotonic/ISO-UTC); no ms-s mismatch found in scope.

---

### [SEVERITY: HIGH] Gamma wall/flip thresholds are scale-inconsistent across OI feed modes — same engine yields gex ~100s vs ~100k–3.6M; many wall-gating strategies silently never fire (or fire on noise)
- File: engine/gex_calculator.py — `get_gamma_walls`, `get_wall_classifications`, `get_gamma_flip`, `get_wall_with_freshness` (lines ~420-610)
- Issue: `gex = norm_net_gamma * 100 * price` where `norm_net_gamma` is the **per-message average** net gamma. Its magnitude depends entirely on the Open-Interest mode feeding the ladder:
  - `_update_strike_from_stream()` → hardcodes `oi = 1.0` (relative).
  - `_update_strike_from_contract()` / `set_open_interest()` → real OI (`DailyOpenInterest`, e.g. 1756).
  Both paths accumulate into the SAME ladder buckets, so the same engine can flip between scales at runtime. Verified on real parsed TSLA data (data/level2/optionchain_parsed_*):
    - OI=1 (stream): per-strike |gex| min≈3, median≈81, max≈138.
    - OI=real: |gex| min≈242, median≈228,721, max≈3,643,108.
  Meanwhile strategy thresholds passed to `get_gamma_walls`/`get_wall_classifications` span **10 → 500,000**:
    - `threshold=500_000`: gamma_wall_bounce(_v2), delta_gamma_squeeze(_v2), delta_volume_exhaustion(_v2), iv_gex_divergence(_v2), vol_compression_range(_v2), confluence_reversal(_v2), call_put_flow_asymmetry(_v2), gamma_volume_convergence(_v2), main.py:1214-1216. In OI=1 mode this fires **0/32** strikes — the "wall" gate silently never activates.
    - `MIN_WALL_GEX=100` (gamma_squeeze(_v2)) fires on **all 32/32** strikes in real-OI mode — every strike is "a wall" (noise).
    - `threshold=10.0` (delta_iv_divergence(_v2), iron_anchor(_v2) default min 10.0) fires on 29/32 in OI=1 mode and **everything** in real-OI mode — pure noise.
- Evidence: real gamma magnitudes 0.0007–0.064; `gex = norm_net_gamma*100*price`; thresholds 10 vs 500_000 both applied to this value (vs gex_calculator.py docstring "threshold is on the normalized GEX scale (e.g. 1e6)", which itself is irreconcilable with gamma_squeeze's 100).
- Suggested fix: define ONE canonical GEX unit and make thresholds mode-independent. Either (a) always use real OI (drop the oi=1.0 default and the `_update_strike_from_stream` relative path), or (b) always use OI=1 relative and re-calibrate every threshold constant (they currently differ by 5×10^4). Add a unit test asserting the gex scale is invariant to feed mode. This is the highest-value finding: it gates live wall/magnet/flip signals silently.

### [SEVERITY: HIGH] `_normalize_depth_quotes` attaches the FULL book-wide exchange-size map to every bid/ask entry → downstream per-level summation over-counts sizes by ~number-of-levels
- File: ingestor/tradestation_client.py — `_normalize_depth_quotes` (lines ~600-670)
- Issue: `bid_exchange_map`/`ask_exchange_map` are computed once over ALL levels (aggregated), then the SAME dict object is assigned to `"bid_exchanges"`/`"ask_exchanges"` on EVERY entry. main.py:1993-1996 then does `for venue, size_str in b.get("bid_exchanges", {}).items(): exchange_bid_sizes[venue] += int(size_str)` **for every bid**. With N bid levels each carrying the full aggregate, `exchange_bid_sizes[venue]` ≈ true size × N. Buffer over-count by ~20× (maxlevels). Feeds `_exchange_bid_sizes` → `KEY_CONVICT_SCORE_5M` and `_compute_fragility` (main.py:2244-2268) — silent score inflation.
- Evidence: real raw depth shows each entry is a single exchange with `Size`, and the aggregate map per entry is the whole book's total (code builds it via `for b in data.get("Bids")` then reuses for all bids).
- Suggested fix: give each entry only ITS OWN venue's sizes (`{b["Name"]: b["Size"]}`), or emit the exchange map at message level (not per-entry). Drop the shared-map reference.

### [SEVERITY: MEDIUM] `_extract_contracts` compares possibly-string `lastPrice` to an int (`price > 0`) → TypeError aborts the WHOLE option-chain batch, silently dropping all contracts for that message
- File: ingestor/tradestation_client.py — `_extract_contracts` (price guard around line ~700)
- Issue: `price = underlying.get("lastPrice") or underlying.get("last") or 0.0` then `if price and price > 0:`. If TS sends `lastPrice` as string (real feed sends many numerics as strings, e.g. `"Gamma":"0.0047"`, `"Price":"419.65"`), `"123.45" > 0` raises `TypeError`. The exception is caught by the generic handler in `_fetch_option_chain_loop`, but it aborts `_extract_contracts` BEFORE the call/put contracts are appended/dispatched → the entire option-chain update for that line is lost (and an error is logged with exc_info each time).
- Evidence: raw feed confirms string-typed numerics; the same function already uses `_safe_float(price)` when appending the underlying message, showing the string hazard is known but the guard runs the raw value.
- Suggested fix: `price = _safe_float(underlying.get("lastPrice") or underlying.get("last") or 0.0); if price > 0:`. Move the float cast before the guard.

### [SEVERITY: MEDIUM] `get_gamma_flip` sums per-message-normalized gamma across strikes — scale-inconsistent, high-volume strikes underweighted; flip strike is message-count sensitive
- File: engine/gex_calculator.py — `get_gamma_flip` (line ~460)
- Issue: `cumulative += self._ladder[strike].normalized_gamma()` where `normalized_gamma()` divides by THAT strike's message count. Summing per-message averages across strikes is not additive in gamma/GEX terms: a strike with 1 message and gamma 0.05 contributes 0.05, while a strike with 100 messages and total gamma 0.05 also contributes ~0.0005 — i.e. the flip location is dominated by whichever strikes happen to have few messages, not by economic gamma concentration. Consumers gamma_flip_breakout(_v2), confluence_reversal(_v2), main.py:2752/2854 use it for regime gating.
- Suggested fix: accumulate absolute gamma (or gamma×OI) sums per strike, then scan cumulative abs values; or weight by strike message count. At minimum document that it's a per-message heuristic, not dollar gamma.

### [SEVERITY: MEDIUM] `_update_strike_from_stream`: delta == 0 (missing/bad field) → `_infer_side` assigns "put" for every degenerate delta; OTM strikes land on coarse probability heuristic
- File: engine/gex_calculator.py — `_infer_side`, `_infer_strike_from_intrinsic`, `_infer_strike_from_probability` (~lines 480-560)
- Issue: `_infer_side` = `"call" if delta > 0 else "put"`. When Delta is absent/0 the message is always treated as a put (call/put asymmetry bias). Separately, because `_infer_strike_from_intrinsic` returns None whenever `intrinsic <= 0`, ALL OTM options fall through to `_infer_strike_from_probability`, whose `prob_per_strike = 0.10` mapping and `round()` can place a contract on a wrong strike — and that wrong-strike value permanently seeds the ladder bucket. Real log shows many `IntrinsicValue:"0"` messages, so this path is heavily exercised.
- Suggested fix: reject delta==0 explicitly (skip rather than assume put); validate prob-derived strike stays within a few strikes of ATM and log when inference is uncertain.

### [SEVERITY: MEDIUM] `_stream_quotes_loop` never feeds the underlying price unless an option-chain subscription exists (`_watched_symbol` only set from option-chain list)
- File: ingestor/tradestation_client.py — `connect()` line 203 + `_stream_quotes_loop` (lines ~250-270)
- Issue: `self._watched_symbol = self._option_chain_symbols[0]` — only set when `_option_chain_symbols` is non-empty. If a deployment subscribes to quotes-only (no option chain), the guard `if self._watched_symbol and ...` means the quote stream's bid/last is NEVER dispatched as `MSG_TYPE_UNDERLYING_UPDATE`, so `GEXCalculator.underlying_price` stays 0 and all dollar-term GEX/wall calcs return 0 silently.
- Suggested fix: set `_watched_symbol` from `_quote_symbols` when option-chain list is empty; or derive watched symbol from the first configured primary symbol.

### [SEVERITY: LOW] orb_probe `_parse_option_symbol` does not apply the documented "decimal implied" scaling for sub-dollar strikes
- File: orb_probe.py — `_parse_option_symbol` (~line 210)
- Issue: docstring says "4-5 digit strike (decimal implied)" but the code does `strike = float(strike_str)` with no decimal-place scaling. Whole-dollar examples work by accident (`float("0500")=500.0`), but a fractional strike encoded as e.g. `C4650` (meaning 465.0) or sub-dollar strikes would parse at 10× error. Diagnostic/probe tool (not live signal), so LOW.
- Suggested fix: scale by implied decimals (`strike = float(strike_str) / 10**k` based on expected strike precision), or parse from the option's `StrikePrice` field when available.

### [SEVERITY: LOW] orb_probe `_parse_depth_line`/`_parse_depth_agg_line` assume `bids[0]`/`asks[0]` is the best level (no sort)
- File: orb_probe.py — `_parse_depth_line`, `_parse_depth_agg_line`
- Issue: `best_bid = bids[0]["price"]`, `best_ask = asks[0]["price"]`. If the feed returns levels unsorted (or a per-exchange feed like the raw sample which intermixes exchanges), best bid/ask, mid, and spread are wrong. Probe/diagnostics only. LOW.
- Suggested fix: take max bid price and min ask price; guard empty.

### [SEVERITY: OBS] Depth-normalized messages carry `symbol: ""` — raw depth feed has no top-level `symbol` key
- File: ingestor/tradestation_client.py — `_normalize_depth_quotes`/`_normalize_depth_agg` return `"symbol": data.get("symbol", "")`
- Issue: raw depth-quotes messages in real data contain `Bids`/`Asks` with per-entry `Side`/`Name`, and no top-level lowercase `"symbol"` (raw uses PascalCase). So the normalized `symbol` is invariably `""`. If any depth consumer keys on `symbol`, it silently breaks. Confirmed empty in real data. OBS.
- Suggested fix: derive `symbol` from the subscription symbol or from entry `Symbol` field when present.

### [SEVERITY: OBS] `services/metrics_api.py` — `int(request.args.get('limit', 60))` raises on non-numeric query → 500
- File: services/metrics_api.py — `/api/metrics/<strategy_id>/history`
- Issue: non-numeric `?limit=` → `ValueError` → HTTP 500. Cosmetic (metrics API), not trade-gating. OBS.
- Suggested fix: wrap in try/except or use a safe-int helper (a `_safe_int` already exists in the ingestor — reuse the pattern).

---

## Investigated and CLEARED (no bug found)
- **Mixed-type arithmetic in the calculator:** `_update_strike` runs a TYPE GUARD + `_safe_float` on all numeric fields before any math; string-encoded numerics (`"0.02"`) are cast safely. No `int+str` in scope files' numeric paths.
- **Division-by-zero:** all `count`-denominator divisions (`normalized_gamma*`, `net_delta_density`, `get_iv_by_strike`, `get_iv_skew`, `get_iv_by_strike_avg`) check `== 0` first.
- **Division-by-zero:** gex `*100*price` guarded by `price <= 0` returns `[]`/`0.0`.
- **Timestamp math:** all age/deadline math uses `time.perf_counter()`/`time.monotonic()` consistently; `utc_now` is ISO-UTC; no epoch ms-vs-s mismatch in scope.
- **Cumulative vs normalized:** `get_net_gamma` (cumulative, sign only) is correctly documented vs `get_normalized_net_gamma` (per-message) and used appropriately in most consumers; the mismatch risk is the per-strike threshold issue covered in the HIGH finding above.