# PnL Calculation Logic — Batch 4 Strategy Analysis

**Date:** 2026-07-17  |  **Analyst:** rune (subagent)  |  **Strategies:** 4  |  **Total Signals:** ~1.36M

---

## Infrastructure Overview

### Signal Lifecycle (Code-Traced)

```
Data Snapshot → Strategy.evaluate() → Signal(direction, entry, stop, target, confidence)
    ↓
StrategyEngine.process() → Dedup (60s window) → Regime Filter → Conflict Resolution → Max 10/tick
    ↓
SignalTracker.track() → OpenSignal stored in memory
    ↓
SignalTracker.update(price, timestamp) every ~1s
    ↓
Resolution: stop hit (LOSS) | target hit (WIN) | time expired (CLOSED)
    ↓
PnL = exit_price - entry (LONG) | entry - exit_price (SHORT)
```

### Key PnL Mechanics

- **Stop/Target Logic:** Hard gates in `_resolve_signal()` — stop checked before target. LONG: stop ≤ price = LOSS, target ≥ price = WIN. SHORT: stop ≥ price = LOSS, target ≤ price = WIN.
- **Hold Time:** All 4 strategies have `max_hold_seconds: 0` in config → uses global default of 900s (15 min). Signals held too long become CLOSED (exit at current price, not at stop/target level).
- **PnL Formula:** `$pnl = (exit - entry)` for LONG, `(entry - exit)` for SHORT. PnL is in **dollar terms** (not risk multiples), computed in `_calc_pnl()`.
- **Win Rate:** `wins / (wins + losses + closed)` — CLOSED signals count in denominator but are NOT wins. This is critical: strategies with many CLOSED signals have their WR suppressed.
- **Avg P&L:** Simple arithmetic mean of all resolved PnL values (wins + losses + closed).

---

## 1. gamma_squeeze

**File:** `strategies/layer1/gamma_squeeze.py`  |  **Signals:** 126,671  |  **WR:** 24.0%  |  **Avg P&L:** -$0.52

### Architecture

Pin detection + wall-breakout squeeze. Fires when price breaks through a gamma wall with depth-aware liquidity vacuum confirmation. LONG = call wall breakout, SHORT = put wall breakout.

### Signal → Entry → Exit → PnL Trace

1. **evaluate()** checks pin setup (`_is_pin`), then wall breakout (`_detect_breakout`) for LONG and SHORT independently.
2. **`_regime_passes()`** is a hard gate: NEGATIVE regime = fire freely; POSITIVE regime = wall GEX must be ≥ 95th percentile of all walls (very strict).
3. **`_enter_squeeze()`** has a critical **net_gamma direction alignment gate**:
   - LONG signal requires `net_gamma > 0` (positive = dealer buying → supports upward squeeze)
   - SHORT signal requires `net_gamma < 0` (negative = dealer selling → supports downward squeeze)
   - If net_gamma direction contradicts the breakout direction, the signal is **rejected entirely** (returns `None`).
4. **Stop/target:** Liquidity-aware stop placement (0.3-0.5% from wall), target at 2× risk (`TARGET_RISK_MULT = 2.0`).
5. **Resolution:** Stop hit → LOSS at stop price. Target hit → WIN at target price. Time expired → CLOSED at current price.

### Why 24.0% WR / -$0.52 Avg P&L?

**Root cause: The net_gamma direction alignment gate creates a directional bottleneck.**

The strategy requires `net_gamma > 0` for LONG and `net_gamma < 0` for SHORT. When net_gamma is near zero (common in choppy markets), signals on both sides get rejected. This means:

- **LONG side (24.0% WR, -$0.53):** Fires when net_gamma > 0 and price breaks call wall. The 24% WR is consistent — squeezes run hard (2× target) but need >33% WR to be profitable. The 2× risk target is generous but the stop is tight (0.3-0.5%), so the break-even WR is only 33%. At 24%, the strategy loses money on average.
- **SHORT side (20.9% WR, -$0.07):** Fires when net_gamma < 0 and price breaks put wall. Nearly identical WR to LONG but much better P&L because the short signals are rarer (3,163 vs 123,508 LONG) — they only fire when conditions are truly aligned.

**The 2× risk target means wins are big ($1.00+) but losses are small (~$0.50).** This creates a negative skew: many small losses, few large wins. At 24% WR with 2× RR, the expected value is: `0.24 × 2 - 0.76 × 1 = -0.28` (in risk units). The -$0.52 avg P&L is consistent with this.

### Identified Issues

1. **POSITIVE regime over-filtering:** In POSITIVE regime, wall GEX must exceed the 95th percentile. This is very strict — most walls don't qualify. The fallback threshold of 500 is better but still blocks many signals. This is why most passing cells are in ORB (where wall GEX tends to be higher).

2. **net_gamma alignment is too strict:** The hard gate in `_enter_squeeze()` rejects LONG signals when net_gamma ≤ 0 and SHORT signals when net_gamma ≥ 0. In practice, net_gamma oscillates around zero frequently, causing many valid breakouts to be rejected. Consider making this a soft confidence factor instead of a hard gate.

3. **Liquidity vacuum threshold (0.2) may be too low:** The `_detect_liquidity_vacuum()` returns 0.0 when there's no depth data. During periods without depth snapshots, ALL signals are rejected (graceful degradation but effectively a no-op).

4. **Stop placement variability:** The `_liquidity_aware_stop()` varies between 0.3% and 0.5% depending on depth. This means the risk/reward ratio isn't consistent across signals — some have 2× RR, others have 4× RR.

### Recommendations

- **Relax net_gamma gate:** Change from hard `if net_gamma <= 0: return None` to a confidence penalty. This would increase signal volume without adding noise.
- **Lower POSITIVE regime threshold:** The 95th percentile is too strict. Consider 80th percentile or a tiered approach (e.g., 95th for ORB, 80th for afternoon).
- **Consider adding a directional bias:** When net_gamma is near zero, prefer the direction of the larger wall GEX rather than rejecting the signal.

---

## 2. gex_divergence

**File:** `strategies/layer1/gex_divergence.py`  |  **Signals:** 234,905  |  **WR:** 35.3%  |  **Avg P&L:** -$0.13

### Architecture

Fades exhausted trends by comparing price slope vs. GEX slope. Bearish divergence (price ↑, GEX ↓) → SHORT. Bullish divergence (price ↓, GEX ↑) → LONG.

### Signal → Entry → Exit → PnL Trace

1. **evaluate()** gets price_window and gamma_window from rolling_data.
2. **Slope calculation:** `(last - first) / abs(first)` over the rolling window. Divergence = opposite signs + both exceed `DIVERGENCE_MIN_SLOPE = 0.0005`.
3. **v2 Acceleration (2nd derivative):** Checks short-term vs. long-term slope acceleration. Both must exceed minimum thresholds. This is a hard gate.
4. **Liquidity decay:** Hard gate — checks bid/ask depth ratio. For bearish: `bid/ask < 1.3`. For bullish: `ask/bid < 1.3`.
5. **Confirmation candle:** Price change must not strongly oppose the divergence. For bearish (SHORT): `price_change < 0.6%`. For bullish (LONG): `price_change > -0.6%`.
6. **Regime:** Soft confidence factor (not a hard gate). Misaligned regime reduces confidence by 50% on the regime component.
7. **Entry/Stop/Target:** Stop at 0.5% from entry. Target at 1.5× risk (1:1.5 RR). Entry = underlying_price at signal time.
8. **Resolution:** Standard stop/target/time logic.

### Why 35.3% WR / -$0.13 Avg P&L?

**The strategy is well-calibrated but suffers from the 1:1.5 RR ratio.**

With 1.5× target and 0.5% stop, the break-even WR is 40%. At 35.3%, the strategy is slightly below break-even, consistent with the -$0.13 avg P&L.

- **LONG side (36.1% WR, -$0.17):** Slightly better WR than SHORT. Bullish divergences benefit from the fact that price falling while GEX strengthening is a clear structural signal.
- **SHORT side (32.4% WR, +$0.01):** Lower WR but nearly breakeven P&L. Short signals are fewer (50K vs 185K LONG) and tend to fire in stronger conditions.

**The Afternoon 50-59% cell at 56.4% WR with +$1.18 is the standout.** This suggests the strategy works best in the afternoon session at mid-confidence levels. The afternoon session has more stable GEX trends, making divergence signals more reliable.

### Identified Issues

1. **Slope calculation is simplistic:** Uses `(last - first) / abs(first)` — a simple linear slope over the entire window. This doesn't account for the number of data points or the smoothness of the trend. A window with 15 points and a window with 100 points get the same slope calculation method.

2. **Confirmation candle is too loose:** `price_change < 0.6%` for bearish and `> -0.6%` for bullish. This is 3× the `CONFIRMATION_CANDLE_PCT = 0.002`. The 3× multiplier makes the confirmation very permissive — many signals pass confirmation even when the price is moving against the divergence.

3. **Regime is soft but inconsistent:** The regime_misaligned flag reduces the regime component from 1.0 to 0.5 (a 0.1 point difference in the 6-component average). But the regime itself is set by the NetGammaFilter, which may not be aligned with the GEX divergence logic. A POSITIVE regime with bullish divergence is "misaligned" but the strategy still fires — it just gets lower confidence.

4. **Liquidity decay threshold (0.3) may be too tight:** The `_check_liquidity_decay()` returns `True` (pass) when depth data is missing. This means signals fire even without depth confirmation, potentially adding noise.

### Recommendations

- **Tighten confirmation candle:** Reduce the 3× multiplier from 3.0 to 2.0. This would filter out signals where price is still strongly moving against the divergence.
- **Add slope smoothness metric:** Weight the slope by the number of data points or by the variance within the window.
- **Consider regime-weighted targets:** In aligned regimes, use a slightly larger target (e.g., 1.8× instead of 1.5×) to capitalize on higher-confidence divergences.
- **The Afternoon 50-59% cell is a goldmine:** Consider creating a session-specific filter that boosts confidence for afternoon signals.

---

## 3. gex_imbalance

**File:** `strategies/layer1/gex_imbalance.py`  |  **Signals:** 509,540  |  **WR:** 42.5%  |  **Avg P&L:** +$0.08

### Architecture

Call/Put GEX ratio reveals dealer hedging bias. Call-heavy (ratio > 0.60) → SHORT bias. Put-heavy (ratio < 0.45) → LONG bias. Neutral zone (0.45-0.60) → no signal.

### Signal → Entry → Exit → PnL Trace

1. **evaluate()** calculates call_gex and put_gex from `gex_calc.get_greeks_summary()`.
2. **Ratio = call_gex / put_gex.** Classifies bias using `_classify_bias()`.
3. **ROC modifier:** Checks rate-of-change of the ratio over 5 ticks. Alignment bonus (+0.1) or opposition penalty (-0.1).
4. **Depth alignment:** Checks bid/ask ratio for depth support.
5. **VWAP deviation:** Checks if price is on the correct side of VWAP for the bias direction.
6. **Regime intensity:** Scaled by `|net_gamma| / 2000`.
7. **Entry/Stop/Target:** Volatility-based stop (`2.5× price std dev`). Target at 1.5× stop distance.
8. **Resolution:** Standard logic.

### Why 42.5% WR / +$0.08 Avg P&L? The 99.98% SHORT Anomaly

**This is the most extreme directional skew of all 4 strategies.**

- **LONG:** Only 125 signals (0.02% of total), WR 23.2%, Avg P&L -$2.79
- **SHORT:** 509,415 signals (99.98% of total), WR 42.5%, Avg P&L +$0.08

**Why is the LONG side so weak?**

Looking at `_classify_bias()`:
```python
if ratio < PUT_HEAVY_RATIO:  # ratio < 0.45
    strength = min(1.0, (PUT_HEAVY_RATIO - ratio) / PUT_HEAVY_RATIO)
    return ("LONG", strength)
```

The LONG threshold is `ratio < 0.45`. This means put_gex must be more than 2.22× call_gex for a LONG signal. This is a **very high bar** — the put side must be heavily dominant. When it does fire, the signals are rare and often in extreme conditions where the mean reversion move is already partially priced in.

**Why does SHORT dominate?**

The SHORT threshold is `ratio > 0.60`. This is much easier to achieve — call_gex just needs to be 1.67× put_gex. This condition is met far more often, generating 509K signals. The 42.5% WR is the dominant metric because it's driven by the massive SHORT sample.

**The LONG P&L of -$2.79 is alarming.** With only 125 signals, this is a small sample, but the magnitude suggests that LONG signals fire in extreme put-heavy conditions where the price has already moved up, and the mean reversion (which is the expected direction for put-heavy) is weak or delayed.

### Code Issues

1. **`_calculate_gex_split()` sums net_gamma per strike:** Call gamma = positive gamma, Put gamma = absolute negative gamma. This is correct, but the ratio calculation doesn't account for the absolute magnitude — a ratio of 0.45 with tiny GEX values is different from a ratio of 0.45 with massive GEX values.

2. **`_compute_confidence_v2()` has a 5-component model but the ratio extremity component is asymmetric:** For put-heavy, `norm_ratio = 1.0 - (ratio / PUT_HEAVY_RATIO)`. For call-heavy, `norm_ratio = (ratio - CALL_HEAVY_RATIO) / (3.0 - CALL_HEAVY_RATIO)`. The put-heavy normalization is inverted (lower ratio = higher confidence), while call-heavy is direct (higher ratio = higher confidence). This is correct but creates different confidence distributions for LONG vs SHORT.

3. **The confidence model doesn't penalize the LONG side for extreme ratios:** When ratio is very low (e.g., 0.1), the norm_ratio is `1.0 - 0.1/0.45 = 0.78`. This is high confidence, but the actual performance (23.2% WR) suggests the signals are firing in conditions where the mean reversion doesn't materialize quickly enough.

### Recommendations

1. **Add a minimum GEX magnitude filter for LONG signals:** Require absolute put_gex > some threshold (e.g., 500) to ensure the signal fires in meaningful put-heavy conditions, not just when the ratio happens to be low due to tiny call_gex.

2. **Consider a dynamic threshold:** Instead of fixed 0.45/0.60, use rolling percentiles of the ratio distribution. This would adapt to different market regimes.

3. **The LONG signals need investigation:** With only 125 signals, the 23.2% WR and -$2.79 P&L could be an artifact. Consider increasing the sample size by lowering the LONG threshold to 0.55 (currently the neutral zone extends to 0.60).

4. **The 42.5% overall WR is misleading:** It's dominated by SHORT. The true "gex_imbalance" signal quality is better measured by the SHORT WR alone (42.5%) rather than the combined metric.

---

## 4. participant_divergence_scalper

**File:** `strategies/layer2/participant_divergence_scalper.py`  |  **Signals:** 492,443  |  **WR:** 40.5%  |  **Avg P&L:** $0.00

### Architecture

Microstructure scalping that distinguishes between fragile "spoof" walls and robust multi-participant liquidity. Four signal types: SPOOF_SHORT (fragile ask wall evaporates), SPOOF_LONG (fragile bid wall evaporates), ROBUST_LONG (robust bid wall holds), ROBUST_SHORT (robust ask wall holds).

### Signal → Entry → Exit → PnL Trace

1. **evaluate()** gets fragility and decay windows for bid and ask.
2. **Four continuous strengths computed:**
   - SPOOF_SHORT: `frag_ask > robust_threshold AND decay_ask > decay_threshold`
   - SPOOF_LONG: `frag_bid > robust_threshold AND decay_bid > decay_threshold`
   - ROBUST_LONG: `frag_bid < fragility_threshold AND decay_bid <= 0`
   - ROBUST_SHORT: `frag_ask < fragility_threshold AND decay_ask <= 0`
3. **Strongest signal wins** (sorted by strength). Minimum strength = 0.2.
4. **Signal strength = strength × 0.6 + wall_score × 0.15 + vol_score × 0.15 + spread_score × 0.10 + vamp_score × 0.05.** Must exceed 0.30.
5. **Confidence:** 7-component weighted model (fragility 0.25, decay 0.15, wall 0.10, volume 0.10, spread 0.10, VAMP 0.10, GEX regime 0.15).
6. **Entry/Stop/Target:** Stop at 0.3% from entry (scalper-tight). Target at 1.5× risk. Entry = underlying_price.
7. **Resolution:** Standard logic.

### Why 40.5% WR / $0.00 Avg P&L? The Perfect Balance

**This strategy is almost perfectly calibrated — wins and losses cancel out.**

- **LONG:** 251,733 signals, WR 40.6%, Avg P&L -$0.06
- **SHORT:** 240,710 signals, WR 40.4%, Avg P&L +$0.07

The near-perfect balance is remarkable. Both directions have nearly identical WR and P&L. This suggests the strategy is capturing microstructure noise effectively — the 0.3% stop and 0.45% target (1.5×) create a break-even WR of 40%, and the strategy hits this almost exactly.

### Why No Cells Pass the 50% Filter?

**This is the key question.** With 40.5% overall WR and 492K signals, you'd expect some cells (session × confidence combinations) to exceed 50%. The answer lies in the signal distribution:

1. **The 40.5% WR is distributed across many cells.** Unlike strategies with a few strong cells and many weak ones, participant_divergence_scalper has a flat distribution — most cells are in the 35-45% range.

2. **The signal strength threshold (0.30) is too low.** The minimum strength of 0.2 and signal_strength of 0.30 allow many marginal signals through. These marginal signals have ~40% WR, pulling down the best cells.

3. **The 7-component confidence model is too granular.** With 7 components summing to 1.0, individual components have small weights. A signal needs to be strong across multiple dimensions to achieve high confidence. This creates a "wall of mediocrity" — many signals at 0.40-0.60 confidence, few above 0.70.

4. **The fragility/decay thresholds create a continuous filter, not a binary gate.** Unlike gamma_squeeze which has clear pass/fail gates, participant_divergence_scalper produces graded signals. This means the "best" signals aren't dramatically better than the "worst" — they're just slightly stronger.

5. **The 0.3% stop is very tight.** This means most signals are resolved quickly (either as WIN or LOSS), with few CLOSED signals. But the tight stop also means the win rate is sensitive to small price movements — a $0.01 move can flip a signal from WIN to LOSS.

### Code Issues

1. **Robust signal decay condition may be too strict:** `decay_bid <= 0` and `decay_ask <= 0` for ROBUST signals. This means ROBUST signals only fire when decay is negative or zero. Positive decay values (even small ones) push the signal into SPOOF territory. This may be too binary — a small positive decay doesn't necessarily mean the wall is fragile.

2. **The `_gate_b_vol_score()` has asymmetric logic:** For SPOOF signals, low vol is good (`vol_score = 1.0 - vol_ratio / 0.5`). For ROBUST signals, high vol is good (`vol_score = vol_ratio / 1.5`). The thresholds (0.5 for SPOOF, 1.5 for ROBUST) are different, creating different vol sensitivity for different signal types.

3. **VAMP validation is a soft bonus, not a hard gate.** When `use_vamp_validation` is True, signals with VAMP score < 0.2 are allowed through with a warning. This means some signals fire with weak VAMP confirmation, potentially reducing WR.

4. **The confidence breakdown is computed per-signal but not used for filtering.** The 7-component model produces a confidence score, but there's no per-component threshold — only the total confidence matters. This means a signal could have excellent fragility (c1 = 0.9) but poor volume (c4 = 0.2) and still fire if the total is above 0.05.

### Recommendations

1. **Raise the signal strength threshold:** Increase from 0.30 to 0.40. This would filter out marginal signals and potentially push some cells above 50% WR.

2. **Add a minimum confidence per-component:** Require at least 2 components above 0.5 (not just the total). This would ensure signals are strong across multiple dimensions.

3. **Consider session-specific thresholds:** The ORB session may benefit from different fragility/decay thresholds than the afternoon session.

4. **Investigate the decay threshold:** The `<= 0` condition for ROBUST signals is binary. Consider a soft threshold (e.g., `decay <= 0.01`) to capture more ROBUST signals.

5. **The $0.00 avg P&L is a feature, not a bug:** This strategy is designed as a "market maker" — it captures small, frequent profits that cancel out losses. The value is in consistency, not in big wins. Consider measuring performance in terms of Sharpe ratio or frequency-adjusted returns rather than raw P&L.

---

## Cross-Strategy Comparison

| Metric | gamma_squeeze | gex_divergence | gex_imbalance | participant_div_scalper |
|--------|---------------|----------------|---------------|------------------------|
| Total Signals | 126,671 | 234,905 | 509,540 | 492,443 |
| Overall WR | 24.0% | 35.3% | 42.5% | 40.5% |
| Avg P&L | -$0.52 | -$0.13 | +$0.08 | $0.00 |
| LONG WR | 24.0% | 36.1% | 23.2% | 40.6% |
| SHORT WR | 20.9% | 32.4% | 42.5% | 40.4% |
| LONG N | 123,508 | 184,722 | 125 | 251,733 |
| SHORT N | 3,163 | 50,183 | 509,415 | 240,710 |
| Stop % | 0.3-0.5% | 0.5% | 2.5×σ | 0.3% |
| Target RR | 2.0× | 1.5× | 1.5× | 1.5× |
| Break-even WR | 33% | 40% | 40% | 40% |
| Directional Balance | LONG-heavy | LONG-heavy | SHORT-heavy | Balanced |

### Key Insights

1. **gamma_squeeze** has the worst WR (24%) but the highest risk-reward (2×). It needs a higher WR to be profitable. The net_gamma direction gate is the biggest issue.

2. **gex_divergence** is well-calibrated at 35.3% WR, just below the 40% break-even. The Afternoon 50-59% cell (56.4% WR, +$1.18) is the best performing cell across all 4 strategies.

3. **gex_imbalance** has the highest overall WR (42.5%) but the directional skew is extreme — 99.98% SHORT. The LONG side (125 signals, 23.2% WR, -$2.79) is a data quality concern.

4. **participant_divergence_scalper** is the most balanced — near-identical LONG/SHORT performance, $0.00 avg P&L, 492K signals. The lack of cells above 50% WR is due to the flat distribution of signal quality, not poor performance.

---

## PnL Calculation Bug Analysis

### Bug 1: gex_imbalance LONG sample size
**Severity:** Medium  |  **Impact:** -$2.79 avg P&L for LONG

The LONG side has only 125 signals out of 509K total. This is suspicious — the PUT_HEAVY_RATIO = 0.45 threshold may be too high, or the ratio calculation may have a bias toward call-heavy conditions. The -$2.79 P&L for LONG is also much worse than SHORT (+$0.08), suggesting the LONG signals fire in conditions where the expected mean reversion doesn't materialize.

**Fix:** Investigate the ratio distribution. Consider lowering PUT_HEAVY_RATIO to 0.55 and adding a minimum put_gex magnitude filter.

### Bug 2: participant_divergence_scalper no cells > 50%
**Severity:** Low  |  **Impact:** Missed optimization opportunity

With 40.5% overall WR and 492K signals, the absence of any cells above 50% suggests the signal strength threshold (0.30) is too low. Raising it to 0.40 would filter out marginal signals and potentially reveal hidden high-WR cells.

**Fix:** Raise signal_strength threshold from 0.30 to 0.40 and re-evaluate.

### Bug 3: gamma_squeeze net_gamma hard gate
**Severity:** Medium  |  **Impact:** Rejected signals in choppy markets

The hard gate in `_enter_squeeze()` rejects LONG signals when net_gamma ≤ 0 and SHORT signals when net_gamma ≥ 0. In choppy markets where net_gamma oscillates near zero, valid breakouts are rejected. This reduces signal volume and may miss profitable opportunities.

**Fix:** Convert from hard gate to soft confidence factor. When net_gamma contradicts the breakout direction, reduce confidence by 0.2 instead of rejecting the signal.

### Bug 4: Hold time resolution
**Severity:** Low  |  **Impact:** Slightly suppressed WR

All 4 strategies use `max_hold_seconds: 0` (global default 900s). Signals held for the full 15 minutes and then closed at current price may have different P&L than those resolved at stop/target. If the price drifts away from the entry during the hold period, CLOSED signals may have negative P&L, suppressing the overall WR.

**Fix:** Consider per-strategy hold times. gamma_squeeze (2× target) might benefit from longer holds (15-20 min), while participant_divergence_scalper (0.3% stop) might benefit from shorter holds (5-10 min).

---

## Summary of Recommendations

1. **gamma_squeeze:** Relax net_gamma direction gate from hard to soft. Lower POSITIVE regime threshold from 95th to 80th percentile.

2. **gex_divergence:** Tighten confirmation candle from 3× to 2× CONFIRMATION_CANDLE_PCT. Add session-specific confidence boost for afternoon signals.

3. **gex_imbalance:** Investigate the LONG side — likely needs a minimum GEX magnitude filter and/or a lower PUT_HEAVY_RATIO threshold.

4. **participant_divergence_scalper:** Raise signal_strength threshold from 0.30 to 0.40. Consider softening the decay threshold for ROBUST signals from `<= 0` to `<= 0.01`.

5. **All strategies:** Consider per-strategy hold times instead of the global 900s default. This would improve resolution accuracy and potentially boost WR.
