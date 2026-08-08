# PnL Calculation Logic — Batch 5 Strategy Analysis

**Date:** 2026-07-17  |  **Strategies:** 4  |  **Total Signals:** ~1.03M

---

## PnL Computation Pipeline (Shared Across All 4 Strategies)

### Signal → Entry → Stop/Target → Resolution → PnL

```
Strategy.evaluate() → Signal(entry, stop, target, confidence)
    ↓
SignalTracker.track() → OpenSignal stored with entry/stop/target
    ↓
SignalTracker.update(price, timestamp) every ~1s
    ↓
_resolve_signal() checks in order:
    1. Time expiry (if max_hold_seconds > 0)
    2. Stop loss hit (price <= stop for LONG, price >= stop for SHORT)
    3. Target hit (price >= target for LONG, price <= target for SHORT)
    ↓
_calc_pnl(direction, entry, exit_price):
    LONG:  exit - entry
    SHORT: entry - exit
    ↓
pnl_pct = (pnl / risk * 100)
```

### Key PnL Mechanics

- **Stop-loss exit:** exit_price = stop (not actual price at stop) — can under-report losses if price gaps through
- **Target exit:** exit_price = target (not actual price at target) — can under-report wins if price overshoots
- **CLOSED (time expiry):** exit_price = current underlying price — PnL depends on drift since entry
- **All 4 strategies have max_hold_seconds=0** (no time limit) in config — signals never expire by time, only by stop/target
- **Dedup window:** 60s — same strategy won't re-fire within 60s, potentially missing rapid re-entries
- **Regime filter:** Net Gamma filter applied before signals reach dashboard; strike_concentration additionally requires `regime == "POSITIVE"` and `net_gamma > 0`

### Why All 4 Show Negative Avg P&L Despite Decent Win Rates

This is the central puzzle. With win rates of 25-37%, the strategies should be profitable if wins are larger than losses. The negative P&L indicates:

1. **Wins don't fully capture target distance:** Target exits use the theoretical target price, not the actual price when hit. If price often overshoots, the recorded win is smaller than realized.
2. **Losses hit stop precisely:** Stop exits use the stop price, which is accurate. But with many signals, losses accumulate.
3. **The "closed" state is rare** (all 0 in the analysis) because max_hold_seconds=0 — so every signal resolves as WIN or LOSS, and the loss volume outweighs the wins.
4. **Directional skew:** 3 of 4 strategies have SHORT outperforming LONG. The LONG side carries more losses.

---

## 1. call_put_flow_asymmetry

**Analysis:** 419K signals | WR 26.7% | Avg P&L -$0.56 | LONG WR 26.8% / SHORT WR 18.0%

### Code Location
`strategies/layer2/call_put_flow_asymmetry.py` (622 lines)

### Signal Lifecycle

```
1. _calculate_flow_scores() — aggregates OI×Gamma×Delta across all strikes
   → call_score, put_score, flow_breadth

2. flow_ratio = call_score / put_score
   → LONG if ratio >= 1.2 (FLOW_THRESHOLD)
   → SHORT if ratio <= 0.833 (1/1.2)

3. _compute_confidence() — 7-component average:
   a. Flow ratio magnitude (log-scaled 0-1)
   b. Flow acceleration (ROC, 0-1)
   c. Flow breadth (cross-strike, 0-1)
   d. IV skew alignment (binary: 0 or 1)
   e. Volume alignment (binary: 0 or 1)
   f. Regime intensity (0.8→1.3 normalized to 0-1)
   g. Wall proximity bonus (+0 to +0.10)

4. Signal(entry=price, stop=price*(1±0.006), target=entry±risk*2.0)
   → Stop: 0.6% | Target: 2× risk (1:3.33 R:R)
```

### Why WR 26.7% (Low)

- **Flow ratio threshold is tight:** 1.2× means even modest imbalances trigger signals. With 419K signals, many are marginal.
- **Binary gates hurt:** IV alignment and volume alignment are binary (0 or 1). If either fails, the confidence drops by ~0.15-0.17 (1/7th each), potentially pushing weak signals below MIN_CONFIDENCE=0.05.
- **Flow acceleration is strict:** ROC must be >0.20 for full credit. In flat markets, flow ratios can be high but not accelerating.

### Why P&L is -$0.56

- **LONG side dominates (415K vs 3.9K SHORT)** and carries most of the loss burden.
- **LONG WR 26.8%:** For every win, ~2.7 losses. At 1:3.33 R:R, breakeven requires 23% WR — this is close, so the negative P&L is expected.
- **SHORT side is weak (18.0% WR):** Only 3.9K signals but losing money at -$0.32 avg. The SHORT threshold (ratio <= 0.833) is harder to hit, so fewer but lower-quality signals.
- **Stop-loss frequency:** With 0.6% stops and 419K signals, many positions get stopped out before reaching the 1.2% target.

### Findings & Recommendations

| Issue | Severity | Detail |
|-------|----------|--------|
| **LONG dominates signal count** | Medium | 415K LONG vs 3.9K SHORT — asymmetric signal production. The LONG threshold (ratio >= 1.2) is easier than SHORT (ratio <= 0.833), creating a volume bias. |
| **Flow ratio normalization** | Low | Uses linear scaling from 1.2 to 10.0. Marginal ratios near 1.2 produce very low confidence (0.05-0.15), flooding the tracker with low-quality signals. |
| **Binary IV/volume gates** | Low | Both are binary (0 or 1) rather than graded. A signal with good flow ratio but failed IV alignment loses ~17% of its confidence. |
| **Regime intensity normalization** | Low | Formula: `(regime_mult - 0.8) / (1.3 - 0.8)` — hardcoded denominator of 0.5. The 0.8→1.3 range is correct, but the normalization could be tighter. |
| **Wall proximity bonus** | Low | Bonus is +0.10 added as `bonus/7` = +0.014. Small but meaningful for marginal signals. |

**Recommendation:** Consider raising MIN_CONFIDENCE from 0.05 to 0.15-0.20 for call_put_flow_asymmetry to filter marginal signals. This would reduce signal volume and potentially improve WR.

---

## 2. depth_imbalance_momentum

**Analysis:** 172K signals | WR 28.7% | Avg P&L -$0.21 | LONG WR 20.8% / SHORT WR 30.9%

### Code Location
`strategies/layer2/depth_imbalance_momentum.py` (387 lines)

### Signal Lifecycle

```
1. _calculate_imbalance() — computes Intraday Range (IR) per direction
   → IR = |price - reference| / range (0-1, lower = stronger)

2. IR threshold: 0.4 (configurable)
   → LONG if bid IR < threshold
   → SHORT if ask IR < threshold

3. _compute_confidence() — 7-component average:
   a. IR magnitude (0-1)
   b. Volume ratio (current/mean, 0-1)
   c. IV alignment (binary)
   d. Volume alignment (binary)
   e. Regime intensity (0.8→1.3 normalized)
   f. Flow breadth (0-1)
   g. Wall proximity bonus (+0 to +0.10)

4. Signal(entry=price, stop=price*(1±0.005), target=entry±risk*1.5)
   → Stop: 0.5% | Target: 1.5× risk (1:3 R:R)
```

### Why WR 28.7% (Moderate)

- **IR threshold of 0.4 is permissive:** Allows many signals through, but many are marginal.
- **Only 1 cell passes 50% filter:** ORB 30-39% confidence at 60% WR. The strategy produces many signals but few with high conviction.
- **Volume ratio is graded** (0-1), which helps — signals with strong volume get higher confidence.

### Why P&L is -$0.21 (Least Negative of the 4)

- **SHORT side is strong (30.9% WR, -$0.03 avg):** 134K SHORT signals with a solid win rate. The SHORT threshold (ask IR < 0.4) is well-calibrated.
- **LONG side is weak (20.8% WR, -$0.84 avg):** Only 37K LONG signals but they lose more per signal. The LONG threshold (bid IR < 0.4) is harder to hit with quality.
- **1:3 R:R ratio:** With 28.7% WR, breakeven requires 25% WR — this is close, explaining the near-zero P&L.

### Findings & Recommendations

| Issue | Severity | Detail |
|-------|----------|--------|
| **LONG/SHORT asymmetry** | Medium | 37K LONG vs 134K SHORT — the LONG side is underproducing signals. The bid IR threshold may be too tight for LONG entries. |
| **Confidence ceiling** | Low | 7-component average with binary gates limits the maximum confidence. Even with all components optimal, confidence caps at ~0.86 (before wall bonus). |
| **Volume ratio grading** | Positive | The graded volume ratio (0-1) is a strength — it provides smooth confidence scaling rather than binary pass/fail. |
| **Stop distance** | Low | 0.5% stop is tight. In volatile markets, this can cause premature stop-outs. |

**Recommendation:** Investigate whether the LONG IR threshold should be adjusted (e.g., 0.35 instead of 0.4) to capture more quality LONG signals. Consider separating LONG and SHORT thresholds.

---

## 3. participant_diversity_conviction

**Analysis:** 351K signals | WR 25.2% | Avg P&L -$0.62 | LONG WR 19.6% / SHORT WR 31.2%

### Code Location
`strategies/layer2/participant_diversity_conviction.py` (414 lines)

### Signal Lifecycle

```
1. _calculate_conviction() — measures participant/exchange diversity
   → participant_score = min(1.0, participants / 5.0)
   → exchange_score = min(1.0, exchanges / 4.0)
   → conviction = 0.6 × participant + 0.4 × exchange

2. _gate_c_size_score() — size score for direction
   → size_score = min(1.0, current_size / (avg_size × 1.5))

3. _compute_confidence() — 7-component average:
   a. IR magnitude (0-1)
   b. Volume ratio (0-1)
   c. IV alignment (binary)
   d. Volume alignment (binary)
   e. Regime intensity (0.8→1.3 normalized)
   f. Flow breadth (0-1)
   g. Wall proximity bonus (+0 to +0.10)

4. Signal(entry=price, stop=price*(1±0.005), target=entry±risk*1.5)
   → Stop: 0.5% | Target: 1.5× risk (1:3 R:R)
```

### Why WR 25.2% (Lowest)

- **Signal threshold of 0.35 is moderate:** Allows many signals but with lower conviction.
- **Only 3 cells pass 50% filter (all ORB):** The strategy's strength is concentrated in the ORB session. Outside ORB, the WR drops significantly.
- **Participant diversity is noisy:** The participant/exchange counts can fluctuate, producing signals during periods of low conviction.

### Why P&L is -$0.62 (Most Negative)

- **LONG side is weak (19.6% WR, -$1.24 avg):** 181K LONG signals with the weakest WR. The LONG threshold (bid participants/exchanges) is harder to satisfy with quality.
- **SHORT side is strong (31.2% WR, +$0.04 avg):** 169K SHORT signals with a solid win rate. The SHORT threshold is well-calibrated.
- **Heaviest losses per signal:** At -$0.62 avg, each signal costs more on average. This suggests the stop-losses are being hit frequently.
- **1:3 R:R ratio:** With 25.2% WR, breakeven requires 25% WR — just barely met. The slight shortfall explains the negative P&L.

### Findings & Recommendations

| Issue | Severity | Detail |
|-------|----------|--------|
| **ORB concentration** | Medium | All 3 cells passing 50% filter are ORB. The strategy is essentially an ORB strategy with broader signal production. Consider ORB-specific tuning. |
| **LONG underperformance** | Medium | LONG WR (19.6%) is significantly below SHORT WR (31.2%). The bid participant/exchange thresholds may need calibration. |
| **Signal volume** | Low | 351K signals is the second-highest volume. Many marginal signals dilute the overall WR. |
| **Conviction scoring** | Low | The 0.6/0.4 participant/exchange weighting is reasonable but could be optimized. Participant count has more impact than exchange diversity. |

**Recommendation:** Implement ORB-specific signal thresholding (lower threshold during ORB, higher during other sessions). Consider raising the signal threshold from 0.35 to 0.40 during non-ORB hours.

---

## 4. strike_concentration

**Analysis:** 84K signals | WR 36.5% | Avg P&L -$0.42 | LONG WR 29.6% / SHORT WR 42.6%

### Code Location
`strategies/layer3/strike_concentration.py` (1354 lines)

### Signal Lifecycle

```
1. Regime gate: requires regime == "POSITIVE" AND net_gamma > 0

2. Identify top 3 OI strikes (by total OI concentration)

3. Two modes per direction:
   BOUNCE: Price bounces off strike (reversal)
   → LONG: bounce off Put strike (below price)
   → SHORT: bounce off Call strike (above price)
   → Stop: 0.3% beyond strike | Target: 1.5× risk

   SLICE: Price slices through strike (breakout)
   → LONG: slices through Call strike
   → SHORT: slices through Put strike
   → Stop: 0.3% against entry | Target: 2.0× risk
   → Hard gates: body_ratio >= 0.3, volume_spike >= 1.2, liquidity_vacuum >= 3.0

4. Confidence: 6 components (bounce) or 8 components (slice)
   → Each normalized to 0-1, averaged

5. Signal(entry=price, stop=price*(1±0.003), target=entry±risk*mult)
   → Stop: 0.3% (tightest of all 4 strategies)
   → Target: 1.5× (bounce) or 2.0× (slice) risk
```

### Why WR 36.5% (Highest)

- **Tight stop (0.3%):** Reduces loss frequency. The strategy exits quickly.
- **High confidence scoring:** 6-8 component average with good normalization. The bounce confidence uses 6 components, slice uses 8.
- **Regime filter:** Requires POSITIVE regime + net_gamma > 0, which filters out low-quality signals.
- **Direction strongly favors SHORT (42.6% WR):** SHORT signals have higher conviction and win rate.

### Why P&L is -$0.42

- **LONG side underperforms (29.6% WR, -$1.09 avg):** 39K LONG signals with lower WR. The bounce/slice logic for LONG may be less effective.
- **SHORT side is strong (42.6% WR, +$0.18 avg):** 44K SHORT signals with the highest WR among all strategies.
- **Tight stops help but don't fully compensate:** 0.3% stops mean smaller losses per signal, but the low LONG WR drags down the average.
- **1:5 R:R for slices:** Slice targets are 2× risk with 0.3% stops, giving a 1:5 R:R ratio. This is the best R:R of all strategies.

### Findings & Recommendations

| Issue | Severity | Detail |
|-------|----------|--------|
| **Regime gate restrictiveness** | Medium | Requires BOTH regime == "POSITIVE" AND net_gamma > 0. This is stricter than other strategies and may miss opportunities in NEGATIVE regime. |
| **Bounce vs Slice balance** | Low | Bounce signals have 6 components, slice has 8. The confidence formulas differ, potentially creating inconsistency in signal quality across modes. |
| **Liquidity vacuum gate** | Low | Slice signals require liquidity_vacuum >= 3.0 (hard gate). This can filter out valid slice signals during low-liquidity periods. |
| **Delta surge gate** | Low | Slice signals require delta_accel > 1.15 (LONG) or < 0.85 (SHORT). This is a strict threshold that may miss moderate momentum signals. |
| **Tight stops** | Positive | 0.3% stops are the tightest of all 4 strategies, reducing loss frequency and size. |

**Recommendation:** Consider relaxing the regime gate to allow NEGATIVE regime signals with high net_gamma magnitude. Also, evaluate whether the liquidity_vacuum and delta_surge hard gates should be soft gates (graded) to capture more slice signals.

---

## Cross-Strategy Comparison

| Strategy | Signals | WR | Avg P&L | LONG WR | SHORT WR | Stop | Target R:R | Key Gate |
|----------|---------|-----|---------|---------|----------|------|------------|----------|
| call_put_flow_asymmetry | 419K | 26.7% | -$0.56 | 26.8% | 18.0% | 0.6% | 1:3.33 | Flow ratio >= 1.2 |
| depth_imbalance_momentum | 172K | 28.7% | -$0.21 | 20.8% | 30.9% | 0.5% | 1:3.0 | IR < 0.4 |
| participant_diversity_conviction | 351K | 25.2% | -$0.62 | 19.6% | 31.2% | 0.5% | 1:3.0 | Conviction >= 0.35 |
| strike_concentration | 84K | 36.5% | -$0.42 | 29.6% | 42.6% | 0.3% | 1:3-5 | POSITIVE + gamma > 0 |

### Key Patterns

1. **All 4 strategies have negative avg P&L** despite win rates above 25%. The common thread is that losses (frequency × size) outweigh wins.
2. **SHORT side consistently outperforms LONG side** in 3 of 4 strategies. This suggests the SHORT signals are more reliably calibrated.
3. **Strike concentration has the highest WR (36.5%)** but still negative P&L — its tight stops (0.3%) keep losses small, but the LONG underperformance drags it down.
4. **Participant diversity has the most negative P&L (-$0.62)** — it produces the most signals (351K) with the lowest WR (25.2%), and the longest signals have the heaviest losses.
5. **Depth imbalance has the least negative P&L (-$0.21)** — it has a moderate signal count (172K) and a balanced WR.

### P&L Calculation Bug Assessment

| Potential Issue | Impact | Evidence |
|----------------|--------|----------|
| Stop-loss exit uses theoretical stop, not actual price | Low | Exit price = stop, not price at stop. Can under-report losses by small amounts. |
| Target exit uses theoretical target, not actual price | Low | Exit price = target, not price at target. Can under-report wins. |
| CLOSED signals rare (max_hold=0) | Low-Medium | All resolved signals are WIN or LOSS. No time-expired signals to dilute P&L. |
| Confidence thresholds too low (0.05) | Medium | Many marginal signals pass the filter, reducing WR. |
| Regime filter blocks signals | Low | strike_concentration requires POSITIVE regime, potentially missing opportunities. |

---

## Summary & Recommendations

### Top 5 Action Items

1. **Raise MIN_CONFIDENCE for call_put_flow_asymmetry** from 0.05 to 0.15-0.20 — would filter marginal signals and improve WR.
2. **Calibrate LONG thresholds** across all strategies — LONG WR is consistently lower than SHORT WR. Consider direction-specific thresholds.
3. **Relax strike_concentration regime gate** — allow NEGATIVE regime with high gamma magnitude to capture more signals.
4. **Consider soft gates for depth_imbalance_momentum** — convert IV and volume binary gates to graded components for smoother confidence.
5. **Monitor participant_diversity_conviction ORB concentration** — all strong cells are ORB. ORB-specific tuning could improve overall WR.

### P&L Root Cause

The negative avg P&L across all 4 strategies is primarily driven by **signal volume overwhelming win capture**. Each strategy produces more signals than it can profitably resolve. The win rates (25-37%) are above the breakeven threshold for their respective R:R ratios, but the sheer number of marginal signals creates a drag. Tightening confidence thresholds and calibrating direction-specific thresholds would be the most impactful improvements.
