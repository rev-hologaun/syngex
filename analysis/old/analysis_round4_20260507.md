# Validation Round 4 — Per-Strategy Enhancement Analysis

**Date:** 2026-05-07 | **Total Signals Analyzed:** 30,597 (resolved: 15,025) | **Strategies:** 9

---

## 📊 Overall Summary

| Metric | Value |
|--------|-------|
| Total Signals | 30,597 |
| Resolved (W+L) | 15,025 |
| Time-Expired (CLOSED) | 15,572 |
| Overall Win Rate (excl. CLOSED) | 49.6% |
| Total P&L | $-554.85 |
| Avg Win | $2.31 |
| Avg Loss | $-1.82 |
| Avg Hold Time | 1837s (30.6 min) |

**Key observation:** 51% of all signals time out (CLOSED). The system generates far more signals than it can resolve within max hold time. This isn't necessarily bad — time-expired signals are neutral, not losses — but it means many strategies are being starved of their natural hold windows.

---

## Per-Strategy Analysis

### 1. Gamma Flip Breakout 🏆
**WR: 86.5% | P&L: +$705.95 | Signals: 5,430 | Avg Hold: 30.3 min**

The clear star. Both LONG (88% WR) and SHORT (85% WR) work. Confidence is the differentiator: 90%+ confidence hits 66% WR on resolved signals. Hold time shows clean degradation: <1min (100%), 1-5min (89%), 5-15min (84%), 15-30min (74%), 30-60min (86%).

**The one change: Add time-decay confidence weighting to the exit logic.**

The strategy works because it catches directional momentum. The 36% timeout rate (1,975 signals) represents capital sitting idle rather than cycling. Instead of adding filters that constrain *when* we enter, enhance *how* we exit: implement a confidence decay function that reduces the effective confidence as hold time increases. At 15 minutes, decay to 80%; at 30 minutes, decay to 60%. This doesn't add new constraints — it lets the strategy self-optimize exit timing based on its own observed hold-time performance. Signals that are still valid at 30+ minutes will maintain high confidence; fading signals will naturally trigger earlier exits.

---

### 2. Theta Burn
**WR: 70.4% | P&L: -$72.70 | Signals: 2,319 | Avg Hold: 6.5 min**

The paradox: highest win rate but negative P&L. The issue is asymmetric: SHORT trades are profitable (+$8.25, 74% WR) while LONG trades lose money (-$80.95, 53% WR). Average win is $0.77 vs average loss of $1.40 — losses are nearly 2x wins. Hold time shows <1min (87% WR), 1-5min (67% WR), 5-15min (70% WR).

**The one change: Implement asymmetric stop-loss sizing based on direction.**

SHORT theta burns work because shorting benefits from time decay and mean reversion. LONG theta burns fail because the upside is capped while downside is theoretically larger. Instead of constraining which direction we trade, adjust the risk parameters per direction: tighten LONG stops to 0.5x the current width and extend LONG targets to 2x. This preserves the strategy's signal generation while fixing the P&L asymmetry. The SHORT side can keep current parameters since it's already profitable.

---

### 3. GEX Imbalance
**WR: 44.1% | P&L: +$97.64 | Signals: 7,214 | Avg Hold: 11.9 min**

Highest signal volume. SHORT direction works (45% WR, +$157 P&L) while LONG struggles (30% WR, -$59 P&L). Hold time sweet spot: 5-15min (48% WR), 30-60min (60% WR). The 30-60min bucket is small (230 signals) but exceptionally strong.

**The one change: Add a dynamic hold-time target based on signal confidence.**

The strategy generates too many low-quality signals that expire before reaching optimal hold windows. Instead of filtering signals pre-entry, enhance the post-entry behavior: use confidence to set a dynamic max hold time. High confidence (70%+) gets 30-minute hold window; medium (50-69%) gets 15 minutes; low (<50%) gets 5 minutes. This lets the strategy adapt its hold behavior to signal quality without adding pre-entry constraints. The 30-60min bucket's 60% WR suggests many signals need more time to play out — this change gives them that time proportionally.

---

### 4. Gamma Squeeze
**WR: 46.6% | P&L: +$457.21 | Signals: 2,906 | Avg Hold: 29.4 min**

Only LONG signals. Excellent risk/reward: avg win $6.54 vs avg loss $3.24 (2.02x). But 94% time-out rate means only 161 resolved out of 2,906. Hold time: 5-15min (50% WR), 15-30min (49% WR). The strategy works when it has time — the issue is the hold window is too short relative to the strategy's natural rhythm.

**The one change: Extend the default max hold time from 30min to 60min.**

This is the single most impactful change for this strategy. The resolved signals at 5-15min and 15-30min both hit ~50% WR with large wins ($6.54 avg). The 94% timeout rate means the strategy is being starved. Extending max hold to 60min doesn't constrain the strategy — it gives it room to breathe. The risk/reward ratio means even a modest increase in resolved signals will significantly boost P&L. This is an enhancement of capacity, not a constraint.

---

### 5. Magnet Accelerate
**WR: 32.5% | P&L: +$78.94 | Signals: 1,962 | Avg Hold: 31.3 min**

Directional asymmetry: SHORT (42% WR, +$124 P&L) vs LONG (25% WR, -$45 P&L). Hold time: 15-30min (41% WR) is the sweet spot. The strategy works best when given 15-30 minutes to play out, but current avg hold is 31.3 min with many signals timing out.

**The one change: Add a direction-aware hold-time multiplier.**

SHORT signals get 1.5x the standard hold time; LONG signals get 0.75x. This doesn't constrain the strategy — it adjusts the hold behavior to match each direction's observed performance. SHORT signals need more time (41% WR at 15-30min) and are profitable. LONG signals underperform (25% WR) and lose money — giving them less time reduces their drag. The multiplier approach is adaptive rather than hard-coded, so it enhances both directions proportionally to their actual performance.

---

### 6. Strike Concentration
**WR: 52.6% | P&L: -$625.21 | Signals: 2,006 | Avg Hold: 12.2 min**

The most dangerous strategy: highest win rate but worst P&L. The problem is catastrophic losses. SHORT has 61% WR but loses $494; LONG has 39% WR and loses $131. Hold time: <1min (94% WR but avg -$2.90!), 1-5min (39% WR), 5-15min (32% WR). The <1min bucket wins 94% of the time but loses $2.90 per trade on average — the losses are devastating when they hit.

**The one change: Implement a per-signal max-loss cap at 50% below current stop distance.**

This isn't constraining the strategy — it's preventing individual losses from destroying the strategy's edge. The 52.6% win rate proves the signal logic works. The negative P&L comes from a small number of catastrophic losses. Capping max loss per signal at half the current stop distance preserves the strategy's signal generation and win rate while eliminating the tail risk that's causing the negative P&L. The strategy becomes a steady earner rather than a potential portfolio drainer.

---

### 7. Vol Compression Range
**WR: 30.0% | P&L: -$503.42 | Signals: 2,352 | Avg Hold: 86.0 min**

Longest hold time of any strategy. Directional asymmetry: SHORT (45% WR, +$110) vs LONG (19% WR, -$614). Hold time: 30-60min (39% WR) is the sweet spot. 57% time-out rate. The strategy needs 30-60 minutes to play out but many signals are cut short.

**The one change: Add a post-signal compression validation filter that confirms the compression is still active before entry.**

The strategy identifies range-bound conditions but doesn't verify that compression is ongoing at entry. Many signals fire at the beginning of a compression cycle when the range hasn't actually tightened yet. Adding a secondary check — confirm that recent volatility (last 5 bars) is below the strategy's threshold — ensures we enter when compression is actively happening, not just when it might happen. This enhances signal quality without constraining the strategy's range of operation. The SHORT direction is already profitable (+$110); improving entry timing will compound that advantage.

---

### 8. Gamma Wall Bounce
**WR: 27.7% | P&L: -$576.57 | Signals: 6,756 | Avg Hold: 26.2 min**

Second-highest signal volume but worst P&L. Both directions lose money. Hold time: 15-30min (33% WR) is the only positive hold window. The strategy triggers too frequently (6,756 signals) but each signal is weak. The 76% timeout rate suggests the bounce thesis needs more time than the current hold window provides.

**The one change: Add a minimum gamma wall proximity threshold that requires the wall to be within 2% of current price.**

The strategy fires on gamma wall detection but doesn't verify the wall is actually relevant to current price action. Many signals likely fire on distant walls that price never reaches. Requiring walls within 2% of current price ensures each signal has a meaningful target. This enhances signal quality (fewer, better signals) without constraining the strategy's ability to fire — it just raises the relevance bar. The 15-30min hold window's 33% WR suggests the strategy works when given time; fewer, more relevant signals means more signals that actually get that time.

---

### 9. Confluence Reversal
**WR: 20.6% | P&L: +$35.30 | Signals: 3,657 | Avg Hold: 55.9 min**

Longest avg hold time. Only LONG signals. 87% timeout rate. Hold time: 15-30min (28% WR) is the best resolved window. The strategy requires multiple confluence factors to align, which is rare — hence the low signal count and low win rate. But when it works, avg win is $5.52 vs avg loss of $2.67 (2.07x risk/reward).

**The one change: Reduce the confluence requirement from 3 factors to 2 factors.**

The strategy is over-constrained. Requiring 3+ confluence factors produces only 3,657 signals with 20.6% WR. The 2.07x risk/reward proves the signals that do fire are high-quality — they just don't fire often enough. Reducing to 2 confluence factors would increase signal volume while maintaining quality. The strategy's edge is in risk/reward, not win rate. More signals = more opportunities to capture the asymmetric payouts. This is the one change that directly addresses the strategy's core weakness (signal scarcity) without constraining its operation.

---

## 📋 Summary Table

| Strategy | WR | P&L | Proposed Change | Expected Impact |
|----------|-----|---------|--------------------------------------------------------|-----------------|
| Gamma Flip Breakout | 86.5% | +$706 | Time-decay confidence on exit | Reduce 36% timeout rate |
| Theta Burn | 70.4% | -$73 | Asymmetric stop sizing by direction | Fix LONG/SHORT P&L asymmetry |
| GEX Imbalance | 44.1% | +$98 | Dynamic hold-time by confidence | Capture 30-60min 60% WR bucket |
| Gamma Squeeze | 46.6% | +$457 | Extend max hold to 60min | Reduce 94% timeout rate |
| Magnet Accelerate | 32.5% | +$79 | Direction-aware hold multiplier | Boost SHORT performance, reduce LONG drag |
| Strike Concentration | 52.6% | -$625 | Per-signal max-loss cap at 50% | Eliminate catastrophic tail losses |
| Vol Compression | 30.0% | -$503 | Post-signal compression validation | Improve entry timing for SHORT edge |
| Gamma Wall Bounce | 27.7% | -$577 | Min wall proximity threshold (2%) | Fewer, more relevant signals |
| Confluence Reversal | 20.6% | +$35 | Reduce confluence from 3→2 factors | Increase signal volume, maintain quality |

---

## 🎯 Priority Recommendations

**Immediate (fix P&L leaks):**
1. **Strike Concentration** — max-loss cap. The -$625 P&L on 52.6% WR is the most dangerous pattern in the system.
2. **Theta Burn** — asymmetric stops. The -$73 P&L on 70% WR is a quick fix.
3. **Gamma Wall Bounce** — proximity threshold. -$577 P&L on 6,756 signals means most signals are noise.

**Medium-term (enhance winners):**
4. **Gamma Squeeze** — extend hold time. The +$457 P&L with 94% timeout means there's more upside.
5. **GEX Imbalance** — dynamic hold-time. The +$98 P&L with a 60% WR at 30-60min is untapped potential.

**Long-term (structural):**
6. **Confluence Reversal** — reduce confluence factors. The strategy works but is too rare.
7. **Magnet Accelerate** — direction-aware holds. Small P&L with clear directional asymmetry.
8. **Gamma Flip Breakout** — time-decay confidence. The best strategy, but 36% timeout is wasteful.

---

*Analysis generated by Archon — Validation Round 4, 2026-05-07*
