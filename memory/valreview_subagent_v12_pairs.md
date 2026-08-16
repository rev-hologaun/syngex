# ValReview Subagent — v1/v2 Mirrored Strategy Pair Divergence Audit

Baseline: v3.221 (717e531). Read-only review of mirrored base `_v2` strategy pairs.
Focus: duplicate-logic divergence (a bugfix in one variant but not the other), calculation/type
bugs (mixed units/scale), and cut-paste errors in duplicated normalize()/confidence blocks.

## Verdict up front
Most pairs are BIT-IDENTICAL except for intentional identity renames
(logger name / class suffix / `strategy_id` -> `..._v2`) and deliberate parameter tuning
(e.g. `POSITIVE_GAMMA_STOP_MULT` 0.75->0.50, `stop_pct`/`target_risk_mult` loosening).
Three pairs carry REAL logic divergence. The single most dangerous is strike_concentration_v2.
Findings below are ranked.

---

### [SEVERITY: CRITICAL] strike_concentration_v2 "relaxed regime gate" compares net_gamma against a PRICE percentile — dead code + 1000x unit mismatch
- Files: `strategies/layer3/strike_concentration_v2.py` vs `strategies/layer3/strike_concentration.py`
- Line(s): ~150-160 (v2 only)
- Issue: v2 relaxes the "bounce requires POSITIVE gamma" gate to also allow NEGATIVE-regime
  extremes via "if |net_gamma| is in top 95th percentile of recent values". But it reads the
  **price** rolling window (`KEY_PRICE_5M`) and compares it to `abs(net_gamma)` where `net_gamma`
  is `data["net_gamma_normalized"]` (a bounded per-message gamma, magnitude ~0.x). Price p95 for
  e.g. SPX ~5100 vs |net_gamma| ~0.35 => condition is essentially *never* true. The relaxation
  can NEVER fire, so v2's advertised feature is silently dead AND the corrected key
  `KEY_NET_GAMMA_5M` (exists in rolling_keys.py) was not used. Cut-paste of the nearby
  `price_window = rolling_data.get(KEY_PRICE_5M)` line.
- Evidence:
  ```python
  ng_window = rolling_data_ng.get(KEY_PRICE_5M)          # PRICE, not net_gamma!
  sorted_vals = sorted(abs(v) for v in ng_window.values if v is not None)
  p95_threshold = sorted_vals[p95_idx]
  if abs(net_gamma) >= p95_threshold:                     # 0.35 >= ~5081 -> False
      _regime_ok = True
  ```
- Suggested fix: use `rolling_data.get(KEY_NET_GAMMA_5M)` (and gate on `len(values)>10`), or
  replace the whole percentile scheme with a fixed |net_gamma| threshold consistent with the
  normalized-gamma scale used elsewhere (cf. regime_conf `/2000` bug below).

---

### [SEVERITY: HIGH] delta_volume_exhaustion: real R:R gate fixed in _v2 only — v1's "1:1 RR" gate is ineffective (mixed-units comparison)
- Files: `strategies/layer2/delta_volume_exhaustion.py` vs `..._v2.py`
- Line(s): v1 ~242-248; v2 ~257-264
- Issue: DUPLICATE-LOGIC DIVERGENCE — a genuine bugfix applied to _v2 only. Both comment-tag the
  gate as "require at least 1:1 RR", but:
  - v1: `if risk > 0 and risk * target_min_risk_mult > min_stop_distance` compares **dollar risk
    to dollar min_stop_distance**. Since `risk == stop_distance == max(base_stop_dist,
    min_stop_distance)`, `risk > min_stop_distance` is true whenever `base_stop_dist >
    min_stop_distance`. It NEVER compares against the target, so it does not enforce any R:R.
  - v2: `if risk > 0 and target_dist >= risk * target_min_risk_mult` correctly checks the *target*
    vs *risk*. This rejects a large class of signals v1 emits (e.g. target ~0.3% entry vs stop
    ~0.6% => v1 fires, v2 rejects).
  - Net divergence: v1 and v2 fire materially different signal sets with different R:R profiles.
- Evidence:
  ```python
  # v1 (broken)
  if risk > 0 and risk * target_min_risk_mult > min_stop_distance:
      pass
  else:
      return None
  # v2 (fixed)
  min_stop_distance = entry * max(STOP_PCT, 0.006)
  if risk > 0 and target_dist >= risk * target_min_risk_mult:
      pass
  else:
      return None
  ```
- Suggested fix: port the v2 gate into v1 (or derisk by flagging that v1 currently ignores
  target R:R entirely).

---

### [SEVERITY: MEDIUM] regime_conf `/2000` — normalized net_gamma divided by a huge constant pins component at its floor (shared bug, both variants)
- Files: `strategies/layer3/strike_concentration.py` (line 1208, 1323) AND `..._v2.py` (1281, 1398)
- Line(s): `regime_conf = 0.05 + 0.05 * min(1.0, abs(net_gamma) / 2000)`
- Issue: `net_gamma = data["net_gamma_normalized"]` is a bounded per-message average gamma
  (engine/gex_calculator.get_normalized_net_gamma). Magnitude is sub-1 / low tens. Dividing by
  2000 => `abs(net_gamma)/2000` ~ 0 => `regime_conf` is effectively ALWAYS 0.05. The regime
  alignment confidence component (advertised 0.05-0.10) never rises, making the strategy less
  selective than designed. The `2000` looks tuned for the cumulative `net_gamma` scale (which does
  grow with message count), i.e. stale-units from an earlier refactor. NOT a divergence (identical
  in v1 & v2) but a real calc bug worth fixing in both.
- Suggested fix: re-scale divisor to the normalized scale (e.g. `/ 1.0` or a defined cap), or
  normalize `net_gamma_normalized` before this term.

---

### [SEVERITY: MEDIUM] strike_concentration_v2 soft-penalty delta blocks use inconsistent normalization (hardcoded magic vs named constants); LONG floor more lenient than SHORT
- Files: `strategies/layer3/strike_concentration_v2.py` (LONG ~466-468, SHORT ~590-592)
- Line(s): LONG `max(0, (delta_accel - 0.5)/(DELTA_ACCEL_THRESHOLD_LONG - 0.5))`;
       SHORT `max(0, (1.15 - delta_accel)/0.3)`
- Issue: v2 converted the delta-accel hard gates into soft penalties. LONG uses named
  constants but hardcodes the lower clamp `0.5`; SHORT hardcodes BOTH `1.15` and `0.3` instead of
  using `DELTA_ACCEL_THRESHOLD_LONG`/`_SHORT`. Today it is coincidentally symmetric
  (0.3 = 1.15-0.85), but the SHORT penalty is not anchored to the constants: if anyone tunes
  `DELTA_ACCEL_THRESHOLD_*`, SHORT silently stops matching LONG and the penalty range mis-scales
  (e.g. fall to 1.05 would leave SHORT penalty denominator wrong). This is the exact cut-paste
  divergence class that silently decays over edits.
- Evidence:
  ```python
  # SHORT (hardcoded, not constant-derived)
  slice_conf_multiplier *= max(0, (1.15 - delta_accel) / 0.3)
  # LONG (mixed: constant-derived upper, hardcoded lower)
  slice_conf_multiplier *= max(0, (delta_accel - 0.5) / (DELTA_ACCEL_THRESHOLD_LONG - 0.5))
  ```
- Suggested fix: derive both from constants, e.g.
  `(DELTA_ACCEL_THRESHOLD_LONG - delta_accel)/(DELTA_ACCEL_THRESHOLD_LONG - DELTA_ACCEL_THRESHOLD_SHORT)`.

---

### [SEVERITY: MEDIUM] gamma_squeeze: v1 hard-gates on net-gamma opposition, v2 soft-penalizes — same "strategy" now diverges in signal gating/risk
- Files: `strategies/layer1/gamma_squeeze.py` vs `..._v2.py`
- Line(s): v1 580-584 (`return None`); v2 580-587 + 612-613 (`confidence *= 0.5`)
- Issue: In the breakout path, v1 returns `None` (no signal) whenever net_gamma opposes the
  breakout direction. v2 instead discounts confidence by 0.5× per opposing sign and lets the signal
  through if still above MIN_CONFIDENCE. This is an intentional v2 softening BUT it means the two
  "mirror" files are no longer equivalent — they will fire different signal sets with different
  win/risk profiles, and downstream `analysis_all.py` that treats *.py and *_v2.py as strategies in
  the same family may double-count divergent behavior. v2 applies the penalty BEFORE the
  MIN_CONFIDENCE check (correct), so no re-check bug — flagging as an OBS/HIGH-of-divergence rather
  than a code defect.
- Evidence: see diff lines 580-587 / 612-613.
- Suggested fix: document the divergence explicitly (it's currently silent), or decide whether the
  hard gate (v1) or soft penalty (v2) is canonical and mirror it in both.

---

### [SEVERITY: LOW] strike_concentration_v2 stale comment: "MIN_CONFIDENCE raised from 0.25 to 0.35" contradicts actual constants
- Files: `strategies/layer3/strike_concentration_v2.py` (~line 79-82)
- Line(s): `MIN_CONFIDENCE = 0.05` ; `LONG_MIN_CONFIDENCE = 0.15`
- Issue: constant comment reads "v2: raised from 0.25 to 0.35" but the file defines
  `MIN_CONFIDENCE = 0.05` (SHORT/slice default) and `LONG_MIN_CONFIDENCE = 0.15`. The comment was
  copied from an intermediate tuning pass and is inconsistent with the code — a maintainer could
  trust the >0.25 threshold and be surprised by 0.05 signals.
- Suggested fix: correct the comment to match the actual constants (0.05 / 0.15).

---

## Clean pairs (no divergence beyond identity renames / intentional tuning)
- layer1: confluence_reversal, gamma_flip_breakout (tonly POSITIVE_GAMMA_STOP_MULT 0.75->0.50 tuning)
- layer2: iv_gex_divergence, delta_gamma_squeeze, depth_imbalance_momentum, delta_iv_divergence (bit-identical besides id).
  depth_decay_momentum (only stop_pct 0.005->0.007, target_risk_mult 1.5->2.0 tuning).
- layer3: theta_burn, gamma_volume_convergence, iv_band_breakout (identity + debug-string renames only).
- full_data: prob_weighted_magnet, prob_distribution_shift, extrinsic_intrinsic_flow, iv_skew_squeeze,
  gamma_breaker, iron_anchor, sentiment_sync, ghost_premium, smile_dynamics, skew_dynamics, extrinsic_flow
  — ALL bit-identical after id rename (verified several by reading diffs). recommend fixing the 
  strike_concentration_v2 regime gate and the delta_volume_exhaustion v1 R:R gate first.

## Confirmed clean (no cut-paste error found) in duplicated normalize/avg blocks
- `layer3/strike_concentration(_v2)` `_compute_slice_confidence` 8-component normalization +
  `/8.0` average is byte-identical between v1 and v2 (checked both tails).