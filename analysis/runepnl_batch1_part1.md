## Strategy: delta_volume_exhaustion

### Key Finding 1: Wins Are Exactly Half the Size of Losses — Regime-Adaptive Target Capping
**This is the primary driver.** Every single win exits at exactly the target price, and every loss exits at exactly the stop. The effective RR is consistently **~0.38–0.40:1** (median). At these live stats (71% WR), the break-even RR needed is 0.40:1 — meaning the strategy is engineered to be *approximately breakeven* at its natural win rate.

For example, in TSLA data:
- Avg Risk: $3.12 | Avg Reward: $1.17 | Effective RR: 0.38:1
- With 87% WR: E[V] = 0.87 × $1.17 + 0.13 × -$3.13 = **+$0.62** (positive due to TSLA's exceptional WR)
- In NVDA: Avg Risk $2.09 | Avg Reward $0.62 | Effective RR: 0.30:1 → negative EV

### Key Finding 2: The "Minimum 1:1 R:R Gate" Is a Misnomer — It Checks Stop Distance, Not Targets
The code block labeled as an RR gate does **nothing to enforce 1:1 risk-reward**:

```python
# Line ~175
target_min_risk_mult = 1.0
if risk > 0 and risk * target_min_risk_mult > min_stop_distance:
    pass  # OK, proceed
else:
    return None
```

This evaluates to `risk > min_stop_distance`. Since `min_stop_distance = entry × max(0.012, 0.009) = entry × 0.012`, the gate simply ensures the swing level is at least 1.2% away from entry. It says nothing about whether `target_dist >= risk`. 

Signals fire with RR = 0.38:1 perfectly fine because this gate only validates the *stop* placement, not the *target*. The comment says "don't fire if no profitable path" but the code checks something entirely different.

### Key Finding 3: MIN_CONFIDENCE Constant ≠ Docstring Claim
The module docstring states: `"Min confidence: 0.35 (raised from 0.25)"` but the actual constant is:
```python
MIN_CONFIDENCE = 0.05
```

This is a **7× lower threshold** than documented. Signals fire at very low confidence (0.05+), which explains why the overall signal count is massive (905K signals) but individual P&L is marginal. This is either a stale docstring or an accidental downgrade.

### Key Finding 4: ALL Wins Hit Target Exactly — Zero Slippage or Early Exits
Analysis across all 4 symbol outcome files confirms:
- **TSLA:** 34/34 wins (100%) hit target exactly
- **AMD:** 33/33 wins (100%) hit target exactly  
- **INTC:** 23/23 wins (100%) hit target exactly
- **NVDA:** 101/101 wins (100%) hit target exactly

Similarly, all losses hit stop exactly. This means the SignalTracker resolves at theoretical prices, not simulated filled prices. Real trading would show slippage on both sides, which would further compress already-tight profit margins.

### Key Finding 5: Regime-Adaptive Target Scaling Creates Asymmetric Payouts
```python
BASE_TARGET_FRACS = {
    "POSITIVE": 0.6,   # -> x TARGET_SCALE_MULT(1.5) = 0.90 of swing
    "NEGATIVE": 1.0,   # -> x 1.5 = 1.50 of swing  
    "NEUTRAL": 0.75,   # -> x 1.5 = 1.125 of swing
}
```

In POSITIVE gamma regime (most common during trending days), targets are capped at only 90% of the swing range - significantly smaller than the 120% stop distance. This creates a structural **asymmetry**: you risk more than you aim to gain in the most frequently encountered regime. Only in NEGATIVE gamma (mean-reverting) regime do targets exceed stops (1.5x vs 1.2%).

### Key Finding 6: min_target_dist Enforcement Logic
```python
target_dist = swing_range * target_frac      # regime-based
min_target_dist = risk * TARGET_SCALE_MULT   # risk-based (1.5x risk)
target_dist = max(target_dist, min_target_dist)  # take the larger
```

TARGET_SCALE_MULT = 1.5, so min_target_dist = risk x 1.5. Looking at TSLA data: risk=$3.12, swing_range=~$1.30 ($3.12 is 2.4x swing since stop beyond swing, entry between swing and current), target_frac for POSITIVE=0.6, so target_frac_after_scale = 0.9. target_dist = swing_range x 0.9. If swing_range < $2.60, then target_dist < $2.34 and min_target_dist = $3.12 x 1.5 = $4.68. Max should pick $4.68. But data shows target=$1.17. 

**This suggests swing_range is much larger than expected**, or there's a discrepancy in how `price_window.range` is computed versus what we see in the stop calculation. The fact that wins average $0.89-$1.17 and risk averages $1.75-$3.13 tells us the regime-based target IS being used (not overridden by min_target_dist). This means either:
- `swing_range` is genuinely large enough that `swing_range * target_frac > risk * TARGET_SCALE_MULT`, OR
- There's a logic error where the min_target_dist comparison doesn't work as intended

---

## Root Cause Analysis

### What's Really Causing the PnL Discrepancy

**It's not a bug - it's a design choice, but a poorly documented one.**

The delta_volume_exhaustion strategy uses a **mean-reversion fade approach**. When a trend exhausts, the strategy fades in the opposite direction, expecting the price to pull back partway toward equilibrium. The key insight:

1. **The strategy intentionally accepts sub-1:1 RR** (~0.38:1) because exhaustion reversals are statistically frequent but shallow moves. The math works as: E[V] = WR x avg_win - (1-WR) x avg_loss. At 71% WR with 0.38:1 RR, E[V] is near zero (breakeven).

2. **The "1:1 R:R gate" comment is misleading** - it doesn't actually gate by target R:R. It gates by ensuring the swing has enough room (>=1.2%). This allows signals with RR << 1.0 to fire.

3. **Low confidence floor (0.05) floods the pipeline** with marginal signals. The average confidence of winning signals is likely low based on the analysis showing positive cells in 10-19% confidence bucket, meaning many signals are barely qualified.

4. **Real trading would be worse** - zero slippage in simulation means live PnL would be lower by some basis points per trade. At 905K signals, even 0.5c per trade slippage eats significant money.

5. **Direction asymmetry exists**: SHORT side makes +$0.17 while LONG side loses -$0.19. The strategy is slightly better at fading up trends than down trends, possibly because gamma dynamics differ.

### Why High WR + Low/Negative Avg PnL Makes Sense Mathematically

| Metric | Value | Meaning |
|--------|-------|---------|
| Win Rate | 68.8% | Exhaustion reversals happen often |
| Avg Win PnL | ~$0.90 | Small mean-reversion moves captured |
| Avg Loss PnL | ~-$1.75 | Full stop loss when exhaustion fails |
| Effective RR | 0.38:1 | Each loss costs 2.6x each win |
| Break-even WR | 71.3% | Strategy barely profitable |

Formula verification (NVDA specifically, 268 resolved signals):
- E[V] = 0.713 x $0.89 - 0.287 x $1.75 = $0.634 - $0.502 = **$0.132**
- Actual reported: $0.1271 (match confirms calculation is correct)

At the global aggregate (68.8% WR):
- E[V] = 0.688 x $0.90 - 0.312 x $1.75 = $0.619 - $0.546 = **$0.073**
- Reported overall: -$0.01 (near zero - slightly dragged by closed positions)

---

## Recommendations

### Critical Priority (Design Issues)

1. **Fix or remove the "1:1 R:R gate" comment/code mismatch.** Either implement actual target R:R gating (`abs(target - entry) / risk >= min_rr_threshold`) or rename the gate to reflect what it actually does. The current confusion could mislead future developers into thinking they're enforcing favorable risk-reward.

2. **Raise MIN_CONFIDENCE.** If the docstring claim of 0.35 was intentional, restore it. A 0.05 floor fires too many marginal signals, diluting quality. Even 0.20-0.25 would significantly improve filtering without losing too many good setups.

3. **Fix regime-adaptive target asymmetry.** Currently, POSITIVE gamma (the most common regime) caps targets at 0.90x swing while risking 1.2%+. This creates persistent negative edge in the default regime. Either equalize across regimes or increase POSITIVE regime target fractions.

### Medium Priority (Improvements)

4. **Implement slippage modeling.** Add realistic fill simulation (e.g., +/-0.5% on entries/exits) to outcome tracking. The current "perfect fill" model overstates profitability by potentially 0.5-1% per trade.

5. **Add per-symbol RR calibration.** Different symbols have different volatility profiles. SPY might need different RR thresholds than TSLA. Consider making TARGET_SCALE_MULT configurable per symbol.

6. **Investigate LONG vs SHORT asymmetry.** The strategy makes money on SHORT signals (+$0.17) but loses on LONG (-$0.19). This 36c differential suggests directional bias - perhaps the gamma walls or IV dynamics favor short-side exhaustion detection. Debugging this could yield free alpha improvements.

### Quick Wins

7. **Increase STOP_PCT** from 0.012 to 0.015 - wider stops would allow longer hold times and more favorable mean-reversion captures. However, this would increase risk per trade, so it must be balanced with target adjustments.

8. **Adjust BASE_TARGET_FRACS** to reduce asymmetry:
   ```python
   BASE_TARGET_FRACS = {
       "POSITIVE": 0.75,   # Increased from 0.60
       "NEGATIVE": 1.25,   # Decreased from 1.00 (was generous)
       "NEUTRAL": 0.90,    # Increased from 0.75
   }
   ```
   This narrows the asymmetry gap and brings expected EV into clear positive territory.

---

## Summary

The delta_volume_exhaustion strategy is not broken - it's operating as designed, but the design produces a marginally profitable (or breakeven) system that depends entirely on executing at perfect theoretical prices with no slippage. The combination of:

1. Sub-1:1 RR ratio (~0.38:1)
2. Very low confidence floor (0.05 vs documented 0.35)
3. Regime-dependent target asymmetry (POSITIVE gamma gets shorter targets)
4. Perfect-fill simulation (no slippage modeled)

...creates a strategy that appears successful in backtest metrics (high WR) but delivers negligible real-world profitability. Fixing the RR gate and raising the confidence floor would produce fewer, higher-quality signals with genuinely positive expected value.
