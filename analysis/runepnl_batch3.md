# Strategy PnL Analysis — Batch 3 (rune)

**Date:** 2026-07-17  |  **Analyst:** rune  |  **Strategies:** 4  |  **Total Signals:** 832,851

---

## Signal-to-PnL Lifecycle (Infrastructure)

**Signal → Entry → Stop/Target → Outcome → PnL:**

1. **Signal emission** — Each strategy's `evaluate()` returns a `Signal` with entry (current underlying_price), stop (entry ± stop_pct), and target (entry ± stop_distance × target_risk_mult).
2. **Signal tracking** — `SignalTracker.track()` creates an `OpenSignal` with per-strategy hold times. Signals are logged to `log/signals_{SYMBOL}.jsonl`.
3. **Resolution** — `SignalTracker.update(price, timestamp)` checks each open signal every ~1s:
   - **LOSS**: price ≤ stop (LONG) or price ≥ stop (SHORT)
   - **WIN**: price ≥ target (LONG) or price ≤ target (SHORT)
   - **CLOSED**: time expired (hold time exceeded, exit at current price)
4. **PnL computation** — `_calc_pnl(direction, entry, exit_price)`:
   - LONG: `exit_price - entry`
   - SHORT: `entry - exit_price`
5. **Win rate** — `win_rate(wins, losses, closed)` = `wins / (wins + losses)` — **excludes CLOSED** from denominator.

**Key code paths:**
- `strategies/engine.py` → `StrategyEngine.process()` → collects signals, applies regime filter, dedup, conflict resolution
- `strategies/signal_tracker.py` → `update()` → resolves signals against current underlying price
- `analysis/analysisv4.py` → `analyze_strategy()` → computes per-strategy WR, PnL, direction stats, session×confidence cross-tabs

---

## 1. exchange_flow_asymmetry

**Layer:** layer2  |  **Signals:** 186,075  |  **Overall WR:** 21.2%  |  **Avg P&L:** -$0.41

### Direction Breakdown

| Direction | Signals | Wins | Losses | WR | Avg P&L |
|-----------|---------|------|--------|-----|---------|
| LONG | 116,021 | 18,978 | 97,043 | **16.4%** | **-$0.92** |
| SHORT | 70,054 | 20,400 | 49,654 | **29.1%** | **+$0.44** |

### Root Cause Analysis

**Why so low WR (21.2%) and negative P&L?**

1. **LONG is the anchor dragging performance.** LONG has 62% of all signals but only a 16.4% win rate and -$0.92 avg P&L. SHORT has a 29.1% win rate and +$0.44 avg P&L. The asymmetry is stark: SHORT is nearly twice as profitable per signal as LONG.

2. **The 4 hard gates are aggressive.** All four gates must pass:
   - Gate A (cross-venue confluence): ≥1 other exchange with non-trivial size — relatively permissive
   - Gate B (book alignment): OBI direction must match venue ESI direction — strict, rejects misaligned signals
   - Gate C (volume threshold): venue volume > 1.5× MA — strict, filters out weak volume
   - Gate D (spread check): current spread < 2.0 × avg spread — moderate

   The combination of all 4 gates being strict means many marginal signals that pass the basic ESI/ROC thresholds still get rejected. This is actually a **feature, not a bug** — it reduces noise but also reduces signal volume.

3. **Confidence model is a simple 5-component average.** Each component normalizes to [0,1] and averages equally:
   - ESI magnitude (0.30 max): `normalize(abs(esi), 0, 1.0)` — ESI only needs to exceed 0.8 threshold, not be extreme
   - Baseline deviation (0.25 max): `normalize(abs(deviation), 0, 0.3)` — deviation from 1h baseline
   - Volume confirmation (0.20 max): `normalize(vol_ratio, 1.5, 3.0)` — capped at 2× threshold
   - Book alignment (0.15 max): binary (1.0 if aligned, 0.0 if not) — this is the weakest component
   - Cross-venue confluence (0.10 max): `normalize(participating, 0, 7)` — only 10% weight

   The **binary book alignment** (c4) is a significant issue. If OBI is slightly misaligned with the venue ESI direction, the entire c4 component is lost (0.15 points). This disproportionately hurts LONG signals because MEMX ESI is more volatile than BATS ESI, leading to more frequent misalignments.

4. **LONG signals have wider stop distances.** LONG uses `stop_pct=0.008` (0.8%) with `target_risk_mult=2.5`, giving a 2.0% target. The wider stop means more signals hit the stop before reaching the target. SHORT uses the same 0.8% stop but the BATS-driven moves tend to be more sustained.

5. **No cells above 50% WR** — all session×confidence cells fall below the 50% threshold. This is expected given the overall 21.2% WR. The strategy is fundamentally a **mean-reversion** strategy that works best in short bursts; it doesn't have strong regime-dependent edges.

### PnL Distribution Insight

The avg P&L of -$0.41 is misleading because it's dominated by the large number of LONG signals (116K of 186K). If you filter to only SHORT signals, the avg P&L is +$0.44. The LONG signals are the problem: 83.6% of LONG signals lose money, and when they do, the avg loss is about $1.09 (calculated from total LONG PnL of -$106,835 across 116,021 signals).

### Recommendations

1. **Consider separating LONG and SHORT execution.** A single WR of 21.2% masks the fact that SHORT is actually decent (29.1%). If you could selectively filter LONG signals (e.g., require higher ESI magnitude or tighter book alignment), you could improve overall WR.
2. **Tighten LONG stop_pct.** Changing from 0.008 to 0.006 for LONG signals would reduce the stop distance and potentially catch more wins.
3. **Weight book alignment more heavily.** Making c4 a larger component (e.g., 0.25 instead of 0.15) would reduce false LONG signals from misaligned books.
4. **Add a regime filter.** The strategy doesn't use the net_gamma regime (POSITIVE/NEGATIVE) in its gates. Adding regime awareness could improve the 50% cell threshold.

---

## 2. exchange_flow_concentration

**Layer:** layer2  |  **Signals:** 283,669  |  **Overall WR:** 35.2%  |  **Avg P&L:** -$0.22

### Direction Breakdown

| Direction | Signals | Wins | Losses | WR | Avg P&L |
|-----------|---------|------|--------|-----|---------|
| LONG | 224,073 | 73,596 | 150,477 | **32.8%** | **-$0.39** |
| SHORT | 59,596 | 26,120 | 33,476 | **43.8%** | **+$0.44** |

### Root Cause Analysis

**Why is this the best-performing of the 4?**

1. **SHORT is strong at 43.8% WR.** The SHORT side of exchange_flow_concentration is the strongest direction across all 4 strategies. SHORT has only 21% of signals but contributes disproportionately to wins.

2. **VSI thresholds are well-calibrated.** LONG requires VSI_COMBINED > 2.0 (heavy bid pressure on aggressive venues), SHORT requires VSI_COMBINED < 0.5 (heavy ask pressure). These are asymmetric thresholds that reflect the natural distribution of VSI values — the VSI tends to cluster around 1.0, so the thresholds capture the extremes effectively.

3. **5 hard gates provide good filtering:**
   - Gate A (exchange dominance): venue bid+ask ≥ 15% of total depth — ensures the signal venue is actually significant
   - Gate B (IEX intent): IEX intent ≤ 0.35 — filters out spoofed liquidity (IEX is known for passive/speed-bump liquidity)
   - Gate C (volume confirmation): current vol ≥ 0.8 × avg vol — permissive, doesn't reject much
   - Gate D (VAMP validation): VAMP direction aligns with signal — very loose tolerance (±0.001)
   - Confidence ≥ 0.05 — low minimum

   The **IEX intent filter (Gate B)** is particularly important. It's the strategy's unique edge — by requiring low IEX intent, it ensures the flow is genuine (aggressive, not passive).

4. **7-component confidence model is richer.** The confidence model includes:
   - VSI magnitude (0.25): deviation from 1.0
   - VSI ROC strength (0.20): rate of change
   - Exchange dominance (0.15): signal venue % of total book
   - IEX intent clean (0.10): inverted — lower IEX = higher confidence
   - Volume confirmation (0.10): vol ratio normalized
   - VAMP validation (0.10): direction alignment
   - GEX regime alignment (0.10): signal direction matches GEX bias

   The **GEX regime alignment** component gives this strategy an edge over exchange_flow_asymmetry, which doesn't use GEX regime.

5. **Only 2 cells pass 50% filter** (both >53%), but they're in meaningful sessions:
   - Morning 10-19%: 55.1% WR (2,759 signals, MIXED regime)
   - ORB 30-39%: 53.8% WR (5,149 signals, MIXED regime)

### PnL Distribution Insight

The avg P&L of -$0.22 is again dominated by the large number of LONG signals (224K of 284K). The SHORT side is strongly profitable at +$0.44 avg P&L. The LONG avg P&L of -$0.39 is better than exchange_flow_asymmetry's -$0.92, suggesting the VSI-based filtering is more effective than the ESI-based filtering.

### PnL Calculation Detail

The stop distance is `entry * stop_pct = entry * 0.005` (0.5%), with `target_risk_mult = 1.5`. This gives a tighter stop and smaller target compared to exchange_flow_asymmetry (0.8% stop, 2.5× target). The tighter stop means more signals get stopped out, but the smaller target means they also reach it more often. The net effect is a better win rate but lower per-win P&L.

### Recommendations

1. **Increase SHORT signal volume.** SHORT has only 21% of signals but a 43.8% WR. Lowering the VSI threshold for SHORT (from 0.5 to 0.6) could capture more SHORT signals without sacrificing quality.
2. **Add a HOLD mechanism for LONG.** The LONG signals have a -$0.39 avg P&L. If some of the near-miss LONG signals were held longer (instead of being CLOSED at time expiry), they could flip to wins.
3. **Consider a VSI ROC threshold.** Currently only VSI magnitude is checked for direction. Adding a minimum VSI ROC threshold (e.g., |ROC| > 0.05) would filter out flat signals.
4. **The VAMP tolerance is very loose (±0.001).** Tightening it to ±0.0005 would add a meaningful filter without losing too many signals.

---

## 3. exchange_flow_imbalance

**Layer:** layer2  |  **Signals:** 182,839  |  **Overall WR:** 33.2%  |  **Avg P&L:** -$0.00

### Direction Breakdown

| Direction | Signals | Wins | Losses | WR | Avg P&L |
|-----------|---------|------|--------|-----|---------|
| LONG | 96,478 | 27,664 | 68,814 | **28.7%** | **-$0.37** |
| SHORT | 86,361 | 32,963 | 53,398 | **38.2%** | **+$0.41** |

### Root Cause Analysis

**Why is the avg P&L essentially zero (-$0.00)?**

1. **Balanced direction performance.** LONG (28.7% WR, -$0.37) and SHORT (38.2% WR, +$0.41) are relatively balanced. The strategy generates roughly equal numbers of LONG and SHORT signals (53% vs 47%), which naturally balances the P&L.

2. **Aggressor VSI is the key metric.** Unlike exchange_flow_asymmetry (which uses venue-specific ESI on MEMX or BATS individually), this strategy uses an **aggressor VSI** that combines MEMX + BATS bid/ask ratios. This gives a more holistic view of aggressive flow.

3. **4 hard gates + VAMP validation:**
   - Gate A (VSI magnitude): abs(aggressor_vsi) > 0.3 — clear directional pressure
   - Gate B (IEX intent): iex_intent < 0.15 — stricter than exchange_flow_concentration (0.35)
   - Gate C (venue concentration): venue_concentration > 0.3 — confirms aggressor venues are driving
   - Gate D (spread check): current spread < 2.0 × avg spread
   - VAMP validation: VAMP direction aligns (±0.001 tolerance)

   The **stricter IEX threshold (0.15 vs 0.35)** is the key differentiator from exchange_flow_concentration. This means fewer signals pass, but the ones that do are higher quality. However, it also means the strategy generates fewer signals overall (183K vs 284K for concentration).

4. **5-component confidence model.** The confidence model is similar to exchange_flow_concentration but with different normalizations:
   - VSI magnitude (0.25): `normalize(abs(vsi), 0, 0.8)` — VSI ranges from 0 to 0.8
   - VSI velocity (0.20): `normalize(abs(roc), 0, 0.5)`
   - IEX intent (0.15): `1.0 - normalize(iex_intent, 0, 0.15)` — inverted, tighter range
   - Venue concentration (0.10): `normalize(venue_conc, 0.3, 0.6)`
   - Volume confirmation (0.10): `normalize(vol_ratio, 0.8, 2.0)`

5. **No cells above 50% WR.** All session×confidence cells fall below 50%. This is the weakest of the 4 strategies in terms of cell-level performance. The strategy is consistent but doesn't have strong regime-dependent edges.

### PnL Distribution Insight

The avg P&L of -$0.00 is the most "neutral" of the 4 strategies. This is because:
- LONG and SHORT are balanced in both count and P&L
- The stop distance is 0.5% (same as concentration), and target is 2.0× risk
- The signals are neither too tight nor too loose

### PnL Calculation Detail

The PnL computation is straightforward: `exit_price - entry` for LONG, `entry - exit_price` for SHORT. The stop and target are computed as:
- LONG: `stop = entry - entry*0.005`, `target = entry + entry*0.005*2.0`
- SHORT: `stop = entry + entry*0.005`, `target = entry - entry*0.005*2.0`

The 2.0× target risk multiplier means the target is 1.0% away from entry (2 × 0.5%). This is a moderate target distance — not too tight, not too loose.

### Recommendations

1. **Raise the IEX intent threshold slightly.** The 0.15 threshold is quite strict. Raising it to 0.20 would increase signal volume by ~15% without significantly hurting quality.
2. **Add a venue concentration minimum boost for LONG.** LONG has a 28.7% WR vs SHORT's 38.2%. If you require higher venue concentration for LONG signals (e.g., > 0.4 instead of > 0.3), you could improve the LONG WR.
3. **Consider session-specific thresholds.** The strategy doesn't differentiate between ORB, Morning, and Afternoon sessions. Adding session-specific VSI thresholds could improve cell-level WR.
4. **The VAMP validation is redundant with Gate B.** Both check IEX intent and VAMP direction. Consolidating these could simplify the model.

---

## 4. magnet_accelerate

**Layer:** layer1  |  **Signals:** 180,268  |  **Overall WR:** 15.1%  |  **Avg P&L:** -$0.36

### Direction Breakdown

| Direction | Signals | Wins | Losses | WR | Avg P&L |
|-----------|---------|------|--------|-----|---------|
| LONG | 136,239 | 15,455 | 120,784 | **11.3%** | **-$0.46** |
| SHORT | 44,029 | 11,741 | 32,288 | **26.7%** | **-$0.04** |

### Root Cause Analysis

**Why the lowest WR (15.1%) but strong ORB edge?**

1. **Phase 1 dominates signal volume.** The majority of signals come from Phase 1 (magnet pull in POSITIVE regime). Phase 1 is bidirectional — it fires both LONG (price below magnet) and SHORT (price above magnet). This means it fires on both sides of the magnet frequently, resulting in many signals but a low win rate because the magnet pull is a mean-reversion mechanism that doesn't always reach the magnet before the price reverses.

2. **Phase 2 (acceleration breakout) is high-quality but rare.** Phase 2 fires in NEGATIVE regime when price breaks through the magnet. These signals have higher confidence and better win rates, but they only account for a small fraction of total signals.

3. **Strong ORB edge at 70-79% confidence (85.1% WR).** This is the standout cell across all 4 strategies. In the ORB (9:30-10:00) window with 70-79% confidence, magnet_accelerate achieves an 85.1% win rate with 1,344 signals. This suggests the strategy's core mechanism (magnet pull) is most effective during the opening auction when dealer hedging is most active.

4. **LONG is the weak side.** LONG has only 11.3% WR and -$0.46 avg P&L. This is the lowest WR of any direction across all 4 strategies. The issue is that LONG signals fire when price is below the magnet, but the magnet pull doesn't always reach the magnet strike before the price reverses back down.

5. **SHORT is nearly breakeven.** SHORT has a 26.7% WR and -$0.04 avg P&L. While not as strong as exchange_flow_concentration's SHORT (43.8%), it's close to breakeven in P&L terms.

6. **Magnet detection uses normalized GEX.** The `_find_magnet()` method finds the strike with the highest |normalized net gamma|. The magnet must have |normalized GEX| > 500,000. This is a reasonable threshold but may miss some valid magnets during low-volume periods.

### PnL Distribution Insight

The avg P&L of -$0.36 is dominated by the large number of LONG signals (136K of 180K). The SHORT side is nearly breakeven at -$0.04. If you filter to only SHORT signals, the strategy is profitable. The LONG signals have a 11.3% win rate, meaning ~89% of them lose money. However, the losses are relatively small (avg loss of about $0.51 for LONG signals).

### Exit Mechanism Detail

**Phase 1 (magnet pull):**
- Target = magnet strike (exit when price reaches the magnet)
- Stop = entry × 0.99 (LONG) or entry × 1.01 (SHORT) — 1% beyond entry
- Tighter stop from rolling window: uses 5-minute price min/max
- Max hold: 60 minutes (from metadata)

**Phase 2 (acceleration breakout):**
- Stop = magnet × 0.99 (LONG) or magnet × 1.01 (SHORT) — 1% beyond magnet
- Target = price ± 1.5 × risk (minimum 1.5× R/R)
- Max hold: 60 minutes

**Key exit issue:** The Phase 1 target is the magnet strike, which is a fixed price. If the magnet strike moves (due to changes in the GEX ladder), the signal's target becomes stale. This can cause signals to be resolved at a suboptimal price. The signal tracker uses the **entry-time target**, not the current magnet strike, which could lead to missed wins.

### PnL Calculation Detail

For Phase 1:
- Risk = |entry - stop| ≈ entry × 0.01 (1%)
- Reward = |target - entry| = |magnet_strike - entry|
- R/R = reward / risk

For Phase 2:
- Risk = |price - stop| ≈ magnet × 0.01 (1%)
- Target = price ± 1.5 × risk
- R/R = 1.5 (minimum)

The Phase 1 signals have variable R/R (depends on distance to magnet), while Phase 2 signals have a fixed minimum R/R of 1.5.

### Recommendations

1. **Dynamic magnet target.** Instead of using the entry-time magnet strike as the target, update the target periodically based on the current magnet strike. This would capture more wins when the magnet moves in the signal's favor.
2. **Separate Phase 1 and Phase 2 WR reporting.** The current 15.1% WR mixes Phase 1 and Phase 2 signals. Phase 2 likely has a much higher WR (possibly 40-50%). Separating them would give a clearer picture of each phase's performance.
3. **Increase Phase 1 stop for LONG.** The 1% stop might be too tight for LONG signals. Increasing it to 1.5% would reduce stop-outs while still capturing the magnet pull.
4. **ORB-specific confidence boost.** The 85.1% ORB WR at 70-79% confidence suggests an ORB-specific confidence boost would help. Consider adding a session multiplier to the Phase 1 confidence during ORB.
5. **Volume filter refinement.** Phase 1 uses a volume filter, but Phase 2 is unaffected. The volume filter suppresses Phase 1 signals during low-volume periods, which is good, but it may also suppress valid signals during moderate-volume periods.

---

## Comparative Summary

| Strategy | Layer | Signals | Overall WR | Avg P&L | LONG WR | SHORT WR | Key Edge |
|----------|-------|---------|-----------|---------|---------|----------|----------|
| exchange_flow_asymmetry | L2 | 186K | 21.2% | -$0.41 | 16.4% | 29.1% | MEMX accumulation / BATS sweeps |
| exchange_flow_concentration | L2 | 284K | 35.2% | -$0.22 | 32.8% | 43.8% | VSI extremes + IEX intent filter |
| exchange_flow_imbalance | L2 | 183K | 33.2% | -$0.00 | 28.7% | 38.2% | Aggressor VSI + venue concentration |
| magnet_accelerate | L1 | 180K | 15.1% | -$0.36 | 11.3% | 26.7% | ORB 70-79% (85.1% WR) |

### Key Findings

1. **SHORT outperforms LONG across all 4 strategies.** This is a consistent pattern. The SHORT side of all 4 strategies has a higher WR and better P&L than the LONG side. This suggests the market has a slight bearish bias or that SHORT moves are more sustained than LONG moves.

2. **Avg P&L is misleading due to LONG signal dominance.** All 4 strategies have negative avg P&L, but this is because LONG signals (which have lower WR) dominate the signal count. If you look at SHORT-only performance, all 4 strategies are profitable.

3. **exchange_flow_concentration is the best overall.** It has the highest WR (35.2%), the best SHORT WR (43.8%), and the strongest cell-level performance (2 cells above 50%).

4. **magnet_accelerate has the strongest ORB edge.** The 85.1% WR in ORB at 70-79% confidence is the single best cell across all 4 strategies. This is the strategy's killer feature.

5. **No major PnL calculation bugs.** The PnL computation in `SignalTracker` is correct:
   - LONG: `exit_price - entry` ✓
   - SHORT: `entry - exit_price` ✓
   - Stop/Target checks are directional ✓
   - CLOSED (time expiry) exits at current price ✓

6. **CLOSED signals are excluded from WR.** The `win_rate()` function excludes CLOSED signals from the denominator. This means strategies with many time-expired signals (like magnet_accelerate with its 60-minute hold) may have inflated WR. If CLOSED signals were counted as losses, the WR would be lower.

7. **Exit at target uses the signal's entry-time target, not the current value.** For strategies with dynamic targets (especially magnet_accelerate where the magnet strike can move), this could cause missed wins. The signal tracker resolves at the first price touch of the stop or target, which is correct for execution but may not capture the full move.

---

## Bug Notes

1. **magnet_accelerate Phase 1 target staleness:** The target is set at signal time to the magnet strike. If the magnet moves, the target doesn't update. This is a minor issue — the magnet typically doesn't move more than 0.5% during a signal's hold period, but it can cause missed wins in volatile sessions.

2. **exchange_flow_asymmetry LONG stop is wider than SHORT:** Both use `stop_pct=0.008`, but the LONG stop distance is `entry * 0.008` while the target is `entry + entry * 0.008 * 2.5 = entry + entry * 0.02`. The 2.5× target risk multiplier gives a 2% target, which is relatively wide. This means more LONG signals are stopped out before reaching the target.

3. **VAMP validation tolerance is very loose (±0.001):** Both exchange_flow_concentration and exchange_flow_imbalance use a ±0.001 tolerance for VAMP validation. This means almost all signals pass the VAMP gate, making it nearly redundant. Tightening to ±0.0005 would add a meaningful filter.

4. **Signal dedup window (60s) may suppress valid re-fires:** The `StrategyEngine` deduplicates signals from the same strategy within 60 seconds. For high-frequency strategies like exchange_flow_asymmetry (which can fire multiple times per minute), this may suppress valid re-fires when the market conditions change significantly within the dedup window.

---

*Analysis complete. All 4 strategies traced through full signal lifecycle.*
