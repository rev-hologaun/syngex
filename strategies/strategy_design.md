# Syngex Strategy Design Document

**Date:** 2026-04-29  
**Author:** Archon (The Celestial Loom)  
**Data Sources:** OHLC bars + Options Chain (real-time) + GEX/Gamma calculations

---

## What Syngex Gives Us

Our GEX calculator maintains a real-time **Gamma Ladder** — a mapping of every strike to its aggregate Net Gamma = Σ(Gamma × OpenInterest × Side), where calls are +1 and puts are -1. From this we derive:

- **Net Gamma** — total across all strikes (positive = dealer buying dips/selling rallies = dampened volatility; negative = dealer selling dips/buying rallies = amplified volatility)
- **Gamma Walls** — strikes with massive GEX concentration (≥$500K threshold). Call walls = resistance magnets. Put walls = support barriers.
- **Gamma Flip** — the highest strike where cumulative net gamma turns negative. Below flip = stabilizing regime. Above flip = accelerating regime.
- **Strike-by-strike Net Gamma** — granular view of dealer positioning at every level

Combined with **OHLC streaming** (price action, volume, momentum), we can build strategies that use options flow as a structural map and price action as the execution trigger.

---

## Strategy 1: Gamma Wall Bounce

**Type:** Mean Reversion / Range Trade  
**Best For:** Positive gamma regimes, liquid names (TSLA, SPY, IWM, QQQ, MSFT)  
**Timeframe:** 5-min bars

### Logic

In a **positive gamma** environment, market makers are net long gamma and must hedge counter-cyclically — buying dips and selling rallies. This creates natural support/resistance at Gamma Walls.

**Entry (Long):**
1. Net Gamma > 0 (positive gamma regime)
2. Price approaches a **Put Wall** (large negative gamma strike below price) within 0.5%
3. OHLC confirmation: bullish candlestick pattern (hammer, engulfing, doji reversal) at or near the wall
4. Volume spike on the reversal candle

**Entry (Short):**
1. Net Gamma > 0
2. Price approaches a **Call Wall** (large positive gamma strike above price) within 0.5%
3. OHLC confirmation: bearish candlestick pattern (shooting star, bearish engulfing) at or near the wall

**Exit:**
- Target: Midpoint between current wall and next wall (or center of gamma range)
- Stop: 0.3% beyond the wall (walls can break)
- Time exit: Flat before close if target not hit

### Why It Works

Market makers hedging large gamma positions at these walls create mechanical buy/sell pressure that pushes price back toward the center. This is the most well-established GEX-based edge.

### Risk

- Walls can break during high-impact news or earnings
- Low liquidity names may not have meaningful walls
- In negative gamma regimes, walls become acceleration zones (see Strategy 2)

---

## Strategy 2: Gamma Flip Breakout

**Type:** Momentum / Breakout  
**Best For:** Transitioning regimes, high-volatility names (TSLA, NVDA, AMD)  
**Timeframe:** 5-min bars

### Logic

The **Gamma Flip** is a regime boundary. When price crosses it, the market transitions from stabilizing to accelerating (or vice versa). This is where gamma-driven dealer hedging creates momentum explosions.

**Entry (Long Breakout):**
1. Price is **above** the Gamma Flip strike (positive cumulative gamma → accelerating regime)
2. Price breaks above a **Call Wall** with volume ≥ 1.5× 20-bar average
3. OHLC: strong bullish candle closing near its high, volume surge
4. Net Gamma is positive and rising

**Entry (Short Breakdown):**
1. Price is **below** the Gamma Flip strike (negative cumulative gamma → stabilizing/deaccelerating regime)
2. Price breaks below a **Put Wall** with volume ≥ 1.5× 20-bar average
3. OHLC: strong bearish candle closing near its low, volume surge
4. Net Gamma is negative and falling

**Exit:**
- Trail stop using 5-min ATR × 1.5
- Or exit when price crosses back through the Gamma Flip
- Minimum hold: 15 minutes (avoid noise entries)

### Why It Works

When price crosses the gamma flip, dealer hedging flips from counter-cyclical to pro-cyclical. Market makers who were buying dips now sell into weakness, creating a feedback loop. This is where the biggest intraday moves happen.

### Risk

- False breakouts are common — volume confirmation is critical
- In choppy markets, price may whipsaw around the flip level
- Requires fast execution (this is a momentum strategy)

---

## Strategy 3: Magnet Zone Scalp

**Type:** Intraday Scalping / Mean Reversion  
**Best For:** All liquid names, especially during mid-day lull (11:30 AM – 2:30 PM ET)  
**Timeframe:** 2-min bars

### Logic

When **Net Gamma is positive** and price is **between two major gamma walls**, the price is "magnetized" — it tends to oscillate between the walls as dealers continuously hedge. This creates a range-bound scalping opportunity.

**Setup:**
1. Net Gamma > 0
2. Identify the two closest gamma walls surrounding current price (one above = call wall, one below = put wall)
3. Calculate the "magnet zone" = the range between these two walls
4. Price must be ≥ 2% away from both walls (not at an edge)

**Entry (Long):**
1. Price is in the lower third of the magnet zone
2. RSI(7) < 35 on 2-min bars (oversold within the range)
3. Bullish divergence on volume (price makes lower low but volume declining)

**Entry (Short):**
1. Price is in the upper third of the magnet zone
2. RSI(7) > 65 on 2-min bars (overbought within the range)
3. Bearish divergence on volume

**Exit:**
- Target: Center of the magnet zone (midpoint between walls)
- Stop: 0.2% beyond the nearest wall
- Quick exits: 3-8 minute holds, 0.3-0.6% targets

### Why It Works

In positive gamma regimes, dealer hedging creates a "rubber band" effect. Price stretches toward walls but snaps back as dealers rebalance. The magnet zone is essentially the "fair value" range for the day.

### Risk

- If gamma regime flips during the trade, the magnet becomes a spring (acceleration)
- Low-volume periods (lunch hour) can produce fake signals
- Earnings or news events destroy the range

---

## Strategy 4: Gamma-Support/Resistance Divergence

**Type:** Confluence / Reversal  
**Best For:** Names with strong technical + options confluence (SPY, QQQ, TSLA, AMZN)  
**Timeframe:** 15-min bars

### Logic

When **traditional technical analysis** (horizontal support/resistance, trendlines, moving averages) **aligns with gamma levels** (walls, flip, high OI strikes), the confluence creates a high-probability reversal zone.

**Setup:**
1. Identify a technical level:
   - Previous day high/low
   - VWAP reversion level
   - 20/50 EMA on 15-min chart
   - Horizontal S/R from daily chart
2. Check if a **Gamma Wall** or **high OI strike** is within 0.3% of that level
3. Calculate a "confluence score":
   - Technical level + Gamma Wall = score 2
   - Technical level + Gamma Flip = score 2
   - Technical level + Gamma Wall + Gamma Flip nearby = score 3 (strongest)

**Entry (Long at Support Confluence):**
1. Confluence score ≥ 2
2. Price touches the confluence zone
3. Reversal candlestick pattern on 15-min bar
4. RSI(14) < 40 (oversold)

**Entry (Short at Resistance Confluence):**
1. Confluence score ≥ 2
2. Price touches the confluence zone
3. Reversal candlestick pattern
4. RSI(14) > 60 (overbought)

**Exit:**
- Target: Next confluence level or 1.5× ATR(14)
- Stop: 0.5% beyond the confluence zone
- Let winners run if momentum continues

### Why It Works

When technical traders and options dealers are both positioned at the same level, you get a double-stacked support/resistance. Technical traders place stops just beyond the level, and dealers hedge aggressively at the gamma wall. This creates a "cliff edge" effect — price bounces hard off the confluence.

### Risk

- Requires manual identification of technical levels (can be automated)
- Weak confluence (score 1) should be avoided
- In strong trending markets, confluence levels get blown through

---

## Strategy 5: Call/Put GEX Imbalance Play

**Type:** Sentiment / Positioning  
**Best For:** Earnings weeks, high-IV environments, directional names  
**Timeframe:** 5-min bars

### Logic

The **ratio of Call GEX to Put GEX** reveals dealer positioning bias. When one side dominates significantly, it creates a directional bias for the underlying. This is essentially reading the "smart money" positioning through the options market.

**Setup:**
1. Calculate total Call GEX and Put GEX across the chain
2. Compute the imbalance ratio: `CallGEX / (CallGEX + PutGEX)`
3. Identify the regime:
   - **Call-heavy** (ratio > 0.6): Dealers are net short calls → they're selling calls aggressively → bearish for underlying (dealers hedge by shorting)
   - **Put-heavy** (ratio < 0.4): Dealers are net short puts → they're selling puts aggressively → bullish for underlying (dealers hedge by buying)
   - **Balanced** (0.4-0.6): No directional bias, use Strategies 1-3

**Entry (Long on Put-heavy):**
1. Call/Put GEX ratio < 0.4 (put-heavy dealer positioning)
2. Net Gamma is positive (stable environment)
3. Price is above VWAP on 5-min chart
4. OHLC: higher low pattern forming, volume expanding on up bars

**Entry (Short on Call-heavy):**
1. Call/Put GEX ratio > 0.6 (call-heavy dealer positioning)
2. Net Gamma is positive
3. Price is below VWAP on 5-min chart
4. OHLC: lower high pattern forming, volume expanding on down bars

**Exit:**
- Target: 0.5-1.0% move (directional but not breakout)
- Stop: 0.3% against position
- Exit if imbalance ratio normalizes back toward 0.5

### Why It Works

Market makers selling large amounts of puts (put-heavy) must buy the underlying to hedge their short delta. This creates a natural bid under the stock. Conversely, selling calls creates a natural ceiling. The imbalance ratio captures this structural pressure.

### Risk

- GEX measures dealer positioning, not directional conviction — dealers can be wrong
- In negative gamma regimes, the imbalance amplifies moves in the wrong direction
- Must combine with net gamma regime filter (Strategy 5 only works in positive gamma)

---

## Strategy Comparison Matrix

| Strategy | Type | Win Rate Est. | Risk/Reward | Complexity | Best Market |
|----------|------|---------------|-------------|------------|-------------|
| Gamma Wall Bounce | Mean Reversion | 60-65% | 1:1.5 | Low | Positive gamma, range-bound |
| Gamma Flip Breakout | Momentum | 45-50% | 1:2.5 | Medium | Negative gamma, trending |
| Magnet Zone Scalp | Scalping | 55-60% | 1:1.2 | Medium | Positive gamma, mid-day |
| Confluence Reversal | Reversal | 55-65% | 1:2.0 | High | All regimes |
| GEX Imbalance | Positioning | 50-55% | 1:1.5 | Low | Positive gamma, directional |

---

## Implementation Notes

### Data Requirements Per Strategy

| Strategy | OHLC Needed | GEX Needed | Options Chain Needed |
|----------|-------------|------------|---------------------|
| Wall Bounce | 5-min bars, volume | Walls, Net Gamma | Open Interest |
| Flip Breakout | 5-min bars, volume | Flip, Walls, Net Gamma | Gamma values |
| Magnet Scalp | 2-min bars, RSI | Walls, Net Gamma | Strike-level gamma |
| Confluence | 15-min bars, VWAP | Walls, Flip, OI | Strike-level data |
| GEX Imbalance | 5-min bars, VWAP | Call/Put GEX by side | Full chain breakdown |

### Prerequisites Before Running Any Strategy

1. **Regime Filter:** Check Net Gamma sign first
   - Positive → Strategies 1, 3, 5 (mean reversion / range)
   - Negative → Strategy 2 (momentum / breakout)
   - Near zero → Strategy 4 (confluence) or sit out

2. **Liquidity Filter:** Only trade symbols with:
   - ≥ 30 active strikes with data
   - Total GEX > $10M
   - Average 5-min bar volume > 50K shares

3. **Time Filter:** Avoid first 15 minutes and last 30 minutes of the session

---

## Next Steps

1. **Backtest each strategy** against historical OHLC + option chain data
2. **Paper trade** for 2-4 weeks before live capital
3. **Parameter tuning** per symbol (wall thresholds, RSI periods, volume multipliers)
4. **Build a unified dashboard** showing all 5 strategy signals simultaneously
5. **Add risk management layer** — position sizing, max daily loss, correlation checks
