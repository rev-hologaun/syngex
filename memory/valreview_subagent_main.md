# Validation Review — main.py (Syngex Orchestrator)

- **Baseline:** v3.221 `717e531`
- **Scope:** `main.py` (~3551 LOC) only + how it consumes `SignalTracker` / `StrategyEngine` / `GEXCalculator.get_greeks_summary()`
- **Human concerns:** calculation/type errors (str+int, None operands, timestamp math), silent logic bugs, V1/V2 shared-callback cross-contamination.
- **Verdict:** Found **1 confirmed HIGH (silent, total signal-chain failure)**, several MEDIUM correctness/robustness issues, and a handful of LOW/OBS. No CRITICAL crash-level arithmetic bug found; the worst is a silent dead metric, not a wrong executed value. All finding locations verified against source.

---

### [SEVERITY: HIGH] prob_momentum reads nonexistent greeks keys → metric is always `None`; entire Prob-Momentum signal chain is dead
- File / Lines: `main.py:1057-1109` (`_calculate_prob_momentum`), consumed at `main.py:1646-1666`
- Issue: `get_greeks_summary()` (engine/gex_calculator.py:394) returns per-strike keys `net_delta, call_delta_sum, put_delta_sum` — it has **NO** `call_delta` or `put_delta` keys. But `_calculate_prob_momentum` reads `strike_data.get("call_delta", 0.0)` and `strike_data.get("put_delta", 0.0)`.
- Evidence:
  ```python
  # main.py:1091-1103
  call_delta = strike_data.get("call_delta", 0.0)
  put_delta  = strike_data.get("put_delta", 0.0)
  net_delta  = call_delta - put_delta
  if call_delta == 0 and put_delta == 0:
      continue
  ...
  return total_momentum if contributing >= 5 else None
  ```
  Both keys are always absent → both defaults `0.0` → every strike `continue`s → `contributing == 0` → `_calculate_prob_momentum` **always returns `None`**. Then at `main.py:1646`:
  ```python
  if prob_mom is not None:
      self._rolling_data[KEY_PROB_MOMENTUM_5M].push(prob_mom)
  ```
  never fires, so `KEY_PROB_MOMENTUM_5M` is never populated, and the `prob_distribution_shift` / `prob_weighted_magnet` ROC/accel chain (`main.py:1651+`) is always empty. Verified by simulation. The sibling method `_calculate_extrinsic_proxy` (main.py:1050) correctly uses `call_delta_sum`/`put_delta_sum`, confirming the key name is simply wrong here.
- Suggested fix: use `strike_data.get("call_delta_sum", 0.0)` and `strike_data.get("put_delta_sum", 0.0)` (matching the actual summary keys, and matcher to extrinsic proxy).

---

### [SEVERITY: MEDIUM] Unguarded `int(size_str)` on exchange sizes — a single malformed value aborts the WHOLE message handler (both orchestrators)
- File / Lines: `main.py:1994-1997` (inside `_on_message`)
- Issue: Per-exchange sizes are cast with `int(size_str)` with no try/except (`ValueError` on an empty/non-numeric string), while everywhere else in `_on_message` the code defensively guards string conversions (e.g. the `last_size` `isinstance(str)` guard at ~line 2430). The entire `_on_message` body is wrapped in one `try/except Exception` that **logs and returns**, so a bad depth exchange value silently drops **all** rolling-window updates for that tick — for both V1 and V2 (dispatched via `_on_shared_message`).
- Evidence:
  ```python
  # main.py:1994-1997
  for venue, size_str in b.get("bid_exchanges", {}).items():
      exchange_bid_sizes[venue] = exchange_bid_sizes.get(venue, 0) + int(size_str)
  for venue, size_str in a.get("ask_exchanges", {}).items():
      exchange_ask_sizes[venue] = exchange_ask_sizes.get(venue, 0) + int(size_str)
  ```
- Suggested fix: wrap in try/except and skip malformed venue, or pre-coerce with `isinstance(size_str, str)` guards like the `last_size` path. At minimum, narrow the `_on_message` try/except so one bad depth field doesn't discard the whole message.

---

### [SEVERITY: MEDIUM] Fixed `0.001` epsilon divider when `past_vsi == 0` → huge VSI-ROC outliers (±1000×)
- File / Lines: `main.py:2070-2080`
- Issue: When the aggressor VSI window has 10 entries but prior `past_vsi == 0`, the code divides by a hardcoded `0.001` to avoid div-by-zero. `aggressor_vsi` lives in roughly [-1, +1], so the ROC becomes `vsi / 0.001` → up to ±1000. This can blow up downstream gates/confidence that consume `KEY_AGGRESSOR_VSI_ROC_5M`.
- Evidence:
  ```python
  if past_vsi != 0:
      vsi_roc = (aggressor_vsi - past_vsi) / abs(past_vsi)
  else:
      vsi_roc = (aggressor_vsi - past_vsi) / 0.001   # --- arbitrary epsilon → ±1000
  ```
- Suggested fix: return `0.0` (or guard on the earlier `if past_vsi != 0` and clamp/NaN) rather than dividing by a magic tiny constant; the result is not a meaningful ROC when prior value is 0.

---

### [SEVERITY: MEDIUM] ROC/accel offsets read *positional* slots of *time-based* windows and treat them as fixed time deltas
- File / Lines: multiple — `main.py:1228` (`extrinsic_roc` `vals[-6]` "~5 min"), `1660` (`momentum_roc` `vals[-6]`), `1395/2040` (`vsi_roc` `values[-10]`), `2368` (`bid_decay` `values[-5]`), `2794` etc.
- Issue: `RollingWindow` here is time-based (`ROLLING_WINDOW_SIZES` = 300 s) and evicts by age, so the number of points held varies with message rate. Indexing `[-5]`/`[-6]`/`[-10]`/`[-11]` is "N ticks ago", not "N seconds/minutes ago". The comments claim "change over last 5 data points (~5 min)" — that assumption only holds if exactly one push per unit time. Under high/low throughput, the effective ROC lookback is time-varying → misleading rates-of-change feeding strategy gates. Silent logic, not a crash.
- Suggested fix: for ROC/accel, either use `count`-based windows, or compute the delta from a stored timestamp (e.g. find index whose timestamp is ~300s old) rather than positional slicing.

---

### [SEVERITY: MEDIUM] Heavy synchronous `_on_message` work blocks the asyncio run loop; shared class-level dispatch couples V1 and V2 timing
- File / Lines: `main.py:392-402` (`_on_shared_message`), `1112+` (`_on_message`), `580+` (`run` loop)
- Issue: The TradeStation client invokes `_on_message_callback(data)` synchronously from the stream path (`ingestor/tradestation_client.py:247`). `_on_message` runs extremely heavy work inline — full-ladder `get_iv_skew`, `get_gamma_walls`, `_calculate_extrinsic_proxy`, per-strike `get_delta_by_strike`/`get_iv_by_strike` (O(strikes) each, effectively O(strikes²) per message on the non-heavy path). Because it shares the event loop with the `run()` loop, this stalls the loop's cadence: `_signal_tracker.update()` (signal resolution), `_evaluate_strategies()`, and `_export_gex_state()` all get delayed behind data processing. `_on_shared_message` then dispatches to **both** orchestrators sequentially, so V1 and V2 resolution/export cadence degrade together. The per-message `/ 0.001`, `int()` and price-type exceptions (findings above) only worsen stall risk.
- Suggested fix: offload `_on_message`'s rolling-window/computation work onto an executor or a bounded queue consumed at a fixed rate; keep only cheap bookkeeping on the data path. At minimum, decouple the two orchestrators' dispatch so one heavy branch can't starve the other.

---

### [SEVERITY: MEDIUM] `_build_last_trigger` can mask a currently-open signal with a stale resolved one; displayed `timestamp` is the close time
- File / Lines: `main.py:2886-2953`
- Issue: The open/resolved merge compares `open_sig["timestamp"]` (the **open** price time) against `resolved_sig["timestamp"]` (the **resolution/close** time). Because a resolution time is always > the open time of an older open, any resolved signal newer than an open signal's open-time wins the merge — even while the strategy still has an open position. The execution card (`last_trigger`) can therefore show the closed trade's `entry/stop/target/direction/side` (and a `timestamp` that is the *close* time) instead of the live open trigger.
- Evidence:
  ```python
  resolved_by_strat[sid] = {..., "timestamp": r.resolution_time, ...}   # close time
  ...
  if open_sig["timestamp"] >= resolved_sig["timestamp"]:
      last = open_sig
  else:
      last = resolved_sig   # close time outweighs a still-open entry
  ```
- Suggested fix: prefer the open signal whenever one exists for the strategy (fall back to resolved only when no open), and expose an explicit open/closed flag + the signal's true open timestamp rather than resolution_time.

---

### [SEVERITY: LOW → MEDIUM] `_build_strategy_health` refetches open signals per strategy + unused `signal_count`
- File / Lines: `main.py:3002-3037`
- Issue: `tracker.get_open_signals()` is called inside the per-strategy loop (O(strategies × open) and allocates a list each iteration). Also `signal_count` is computed and never used (dead code) — total_signals comes from stats. Not a correctness bug, but a hot, wasteful read in an Every-second export.
- Evidence: `for strat in self._strategy_engine._strategies: ... open_signals = tracker.get_open_signals()`
- Suggested fix: fetch `open_signals = tracker.get_open_signals()` once before the loop; remove the unused `signal_count` accumulator.

---

### [SEVERITY: LOW] Underlying-price arithmetic assumes numeric; a string `price` raises TypeError that aborts the whole message
- File / Lines: `main.py:1141-1143`
- Issue: `price = data.get("price"); if price and price > 0:` performs `price > 0` directly. If the stream ever delivers `price` as a string (the human's "str+int=invalid" fear; `last_size`/exchange sizes are strings elsewhere in this codebase), `price > 0` raises `TypeError`, which is swallowed by the outer `_on_message` except → all updates for that message are dropped. Same pattern at `main.py:1457` (`if price > 0`).
- Suggested fix: coerce with `float(price)` in a guard (like the `last_size` defensive path) before comparing, or check `isinstance(price, (int, float))`.

---

### [SEVERITY: LOW] Gamma walls computed only on heavy ticks → GammaBreaker / Iron Anchor / theta_burn silently skip 4/5 ticks
- File / Lines: `main.py:1216-1224, 1457, 1580, 1693` (local `gamma_walls_100k/500k/5k`)
- Issue: `gamma_walls_100k/500k/5k` are **local** variables assigned `None` on every `_on_message` and only assigned on heavy ticks (`_tick_modulus` = 5). Every consumer block that uses them (`walls = gamma_walls_100k` for Gamma Breakout, `gamma_walls_500k` for Iron Anchor, `gamma_walls_5k` for theta_burn) is silently skipped on 4 of every 5 messages. Only `self._gamma_walls_500k` (instance attr) persists for `_report_profile`. Inconsistent effective update rates across gamma-wall consumers; silent staleness.
- Suggested fix: gate these consumers on a shared per-orchestrator "last computed walls" snapshot (like `self._gamma_walls_500k`) so all emit from the same cached ladder each tick, or document that they intentionally run at 1/5 rate.

---

### [SEVERITY: OBS] `_active_instances` never removes instances; `_on_shared_message` swallows per-instance errors silently
- File / Lines: `main.py:376, 392-402`
- Issue: The class registry `_active_instances.append(self)` in `__init__` never removes on shutdown. The dispatch loop catches each `inst._on_message(data)` exception with bare `pass`. Combined with `_on_message`'s own `except Exception` (which does log), most errors are logged once, but any exception raised outside `_on_message` (e.g. in dispatch) is invisible. Not a correctness bug in a single symbolic single-run process, but fragile for restart/reconnect scenarios.
- Suggested fix: add a `shutdown()` removal (`self._active_instances.remove(self)`), and log (not pass) dispatch failures.

---

### [SEVERITY: OBS] V1/V2 routing is config-dependent — currently safe, but fragile to config drift
- File / Lines: `main.py:275-286, 767-770, 875-1009`, `_build_strategy_health` Bug-2 guard at 2976.
- Issue: Verified the current configs are safe: `config/strategies.yaml` has **0** `_v2` keys (V1 engine registers only non-v2), and `config/strategies_v2.yaml` is fully `_v2`-suffixed — so `_register_strategies_from_config` (main.py:767) correctly skips them for the V2 orchestrator and `_register_v2_strategies` owns the V2 set. No live V1/V2 cross-contamination at present. However: (a) the primary (V1) engine **would** register any `_v2`-named strategy present in its own config (the skip guard only applies when `not self._own_pipeline`), and (b) if a future V2 config drops the `_v2` suffix on a key, that base strategy silently registers into the V2 engine and routes into `self._signal_tracker` (the V2 orchestrator's V1 tracker, not the V2 tracker). Fragility to config drift, not a current bug.
- Suggested fix: make the skip/suffix rule symmetric (skip `_v2` in primary and require `_v2` in V2), or enforce a config schema validation that rejects non-`_v2` keys in the V2 config.

---

## Summary

- **1 HIGH:** `_calculate_prob_momentum` wrong key names → always `None` → Prob-Momentum / `prob_distribution_shift` / `prob_weighted_magnet` chain dead (silent, no error). **Most impactful finding — this is the kind of silent logic bug the operator worried about.**
- **4 MEDIUM:** unguarded `int(size_str)` message-kill; `/0.001` epsilon ROC outlier; positional-slice-vs-time-window ROC/accel timing mismatch; blocking/heavy `_on_message` + shared dispatch coupling V1/V2 cadence.
- **1 MEDIUM:** `_build_last_trigger` can show a stale resolved trigger's close-time over a live open.
- **LOW/OBS:** price-type guard, per-strategy open-signal refetch, gamma-wall staleness (heavy-tick only), `_active_instances` leak, config-dependent V1/V2 routing.
- **No CRITICAL crash:** verified there is no confirmed str+int or div-by-zero that misfires on normal numeric data at execution time; the one `int(value)` cast and the epsilon divide are the only real crash/outlier risks, and both are guarded paths that abort/outlier rather than corrupt the executed trade.
- **V1/V2 shared callback is structurally sound** with current configs; the "Bug 1" shared-dispatach and "Bug 2" tracker routing fixes are correctly implemented. Residual risk is config-drift-dependent, not a live bug today.

Deliverable written to `~/projects/syngex/memory/valreview_subagent_main.md`.