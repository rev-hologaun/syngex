# Rune's Level 2 New Strategy Designs
> Generated 2026-05-11 by Rune 🐉
> Context: Syngex v1.90, 22 existing strategies, 4 live streams (Quotes, Option Chain, Depth Quotes, Depth Aggregates)

---

## Data Context Summary

### What orb_probe.py Gives Us (4 Streams)

| Stream | Key Fields | Frequency | Current Use |
|--------|-----------|-----------|-------------|
| **Quotes** (L1) | last, bid, ask, bid_size, ask_size, volume, VWAP, venue (IEX, BATS, etc.) | ~1Hz | Price action, VWAP deviation, venue analysis |
| **Depth Aggregates** (L2) | total_bid_size, total_ask_size, bid/ask ratio, participant counts, top 3 levels | ~1Hz | Liquidity imbalance, bid/ask pressure |
| **Depth Quotes** (TotalView) | Per-exchange order book (NSDQ, MEMX, BATS, EDGX, ARCX, etc.), individual quotes with exchange attribution | ~1Hz | Exchange-specific flow, venue concentration |
| **Option Chain** | Greeks (delta, gamma, theta, vega, rho), IV, ProbITM, intrinsic/extrinsic, theoretical value | ~1Hz | Gamma walls, IV skew, delta density |

### Key Observations from LEVEL2_DATA_SAMPLES.jsonl

- **Bid/Ask ratios swing wildly**: 12.62 (extreme bullish) to 0.88 (bearish) — currently unused as a standalone signal
- **Exchange diversity**: 8 exchanges visible (NSDQ, MEMX, BATS, BATY, EDGX, EDGA, ARCX, CHXE) — each with different behavior profiles
- **MEMX walls**: Large single-exchange orders (2040 shares on MEMX asks) act as resistance/support
- **BATS activity**: BATS shows up as both buyer (bids) and seller (asks) — aggressive flow
- **Participant concentration**: Best bid can have 1-4 participants — concentration vs. broad participation matters
- **Spread compression**: Spreads as tight as 0.04, as wide as 0.09 — correlates with volatility regimes
- **Top 3 levels**: Rich data on the 3 best bid/ask levels — size distribution, order count, timestamps

---

## New Strategy Designs

### 1. Exchange Flow Asymmetry (EFA)
**Layer:** Layer 2 (Order Flow)  
**Signal Type:** Directional — exchange-specific flow imbalance  
**Hold Time:** 10–45 min  
**Confidence Components:** Exchange volume ratio, venue concentration, flow direction, regime filter

**Concept:**  
Different exchanges have different participant profiles. MEMX is often institutional/aggressive, BATS is algorithmic, NSDQ is mixed, IEX has the "speed bump" (retail-friendly). When one exchange's flow diverges significantly from the cross-exchange average, it signals informed positioning.

**Triggers:**
- Any single exchange contributes >35% of total bid OR ask volume (vs. historical baseline of ~15-20%)
- Directional: if MEMX dominates bids → LONG; if MEMX dominates asks → SHORT
- BATS aggressive flow (high order_count relative to size) → momentum confirmation
- IEX concentration on one side → retail-driven, fade if extreme

**Data Sources:**
- `depthquotes_parsed` — exchange breakdown of bid/ask sizes
- `quotes_parsed` — last_venue for trade-side confirmation
- Rolling 30m baseline per exchange

**Example from samples:**
```
MEMX asks = 2040 shares (49% of total ask size of 4083)
→ Strong resistance signal, expect price to bounce off or break through with volume
```

**Hard Gates:**
- Net Gamma Regime filter (like all Syngex strategies)
- Minimum total depth (500 shares combined bid+ask)
- Exchange concentration must exceed 2σ from 30m rolling mean

**Synergy with existing:**
- Complements `Call/Put Flow Asymmetry` (options → equities)
- Works with `Gamma Wall Bounce` — exchange flow at wall = higher conviction
- Adds venue dimension to `GEX Divergence`

---

### 2. Depth Imbalance Momentum (DIM)
**Layer:** Layer 2 (Order Book Dynamics)  
**Signal Type:** Directional — bid/ask pressure asymmetry  
**Hold Time:** 5–30 min  
**Confidence Components:** Bid/ask ratio, ratio rate of change, depth slope, participant spread

**Concept:**  
The total bid/ask size ratio from depth aggregates is a powerful but underutilized signal. A ratio of 12.62 means bid pressure is 12× ask — price wants to go up. But the *rate of change* of this ratio matters more than the absolute value. Rapidly widening ratio = accelerating momentum. Shrinking ratio = exhaustion.

**Triggers:**
- **LONG:** bid/ask ratio > 3.0 AND rising (rate of change > 0.1 per 10s)
- **SHORT:** bid/ask ratio < 0.6 AND falling
- **MOMENTUM BOOST:** ratio > 5.0 OR < 0.4 → extreme, expect continuation
- **EXHAUSTION:** ratio > 8.0 → overextended, potential mean reversion

**Data Sources:**
- `depthagg_parsed` — total_bid_size, total_ask_size, spread
- Rolling 5min and 30m ratio windows

**Rate of Change Calculation:**
```
roc = (current_ratio - ratio_10s_ago) / ratio_10s_ago
roc > 0.1  → accelerating
roc < -0.1 → decelerating
```

**Example from samples:**
```
Sample 1: bid=8061, ask=639, ratio=12.62, spread=0.05
→ Extreme bid pressure, tight spread = bullish breakout imminent

Sample 2: bid=1940, ask=2217, ratio=0.88, spread=0.04
→ Slight ask dominance, thin bids = bearish pressure building
```

**Hard Gates:**
- Net Gamma Regime filter
- Minimum depth (total > 1500 shares)
- Spread must be < $0.15 (avoid illiquid conditions)

**Synergy with existing:**
- Direct complement to `Gamma Wall Bounce` — depth imbalance at wall = strong bounce
- Adds order book dimension to `Magnet & Accelerate`
- Can replace or enhance `GEX Imbalance` (which uses options GEX, this uses equity depth)

---

### 3. Liquidity Vacuum Breakout (LVB)
**Layer:** Layer 3 (Micro-Signal)  
**Signal Type:** Breakout — thin book acceleration  
**Hold Time:** 3–15 min  
**Confidence Components:** Liquidity gap depth, price proximity, volume confirmation, gamma alignment

**Concept:**  
When the order book has thin liquidity at consecutive price levels (a "vacuum"), price can accelerate through them rapidly. This is the micro-structure equivalent of a short squeeze but at the order book level. We detect these by finding gaps in the depth where total_size drops below a threshold for 2+ consecutive levels.

**Triggers:**
- **UP vacuum:** 2+ consecutive ask levels with total_size < 50 shares each, price within 0.15 of first thin level
- **DOWN vacuum:** 2+ consecutive bid levels with total_size < 50 shares each, price within 0.15 of first thin level
- **VACUUM DEPTH:** Count total shares to cross (sum of thin levels) — deeper vacuum = stronger signal
- **VOLUME CONFIRMATION:** Volume spike (> 1.5× rolling mean) as price enters vacuum

**Data Sources:**
- `depthagg_parsed` — top 20 bid/ask levels with total_size
- `quotes_parsed` — volume, last price, VWAP

**Liquidity Gap Detection:**
```
For each level i:
  if total_size[i] < THRESHOLD (default 50):
    mark as thin
  else:
    break consecutive run

Consecutive thin levels >= 2 → vacuum detected
```

**Example pattern:**
```
Asks: 419.57 (8), 419.58 (128), 419.59 (8), 419.60 (5), 419.61 (3)
                    ↑ thin   ↑ thin   ↑ thin
Vacuum from 419.57-419.61 (3 thin levels, only 139 shares total)
Price at 419.56 → UP vacuum breakout signal
```

**Hard Gates:**
- Volume must be > 50% of 5min rolling mean
- Price must be within 1× spread of vacuum entry
- Net Gamma Regime: prefer LONG in negative gamma, SHORT in positive gamma (for breakouts)

**Synergy with existing:**
- Micro version of `Gamma Squeeze / Wall-Breaker` — but at order book level, not gamma wall level
- Complements `Strike Concentration Scalp` — LVB finds gaps between concentration points
- Fast hold time fits Layer 3 micro-signal profile

---

### 4. IV Smile Dynamics (ISD)
**Layer:** Full Data (Advanced)  
**Signal Type:** Sentiment reversal — IV skew curvature  
**Hold Time:** 30 min – 2 hr  
**Confidence Components:** Smile curvature, skew slope, moneyness distribution, volume confirmation

**Concept:**  
The IV "smile" or "skew" across strikes reveals market sentiment. A normal smile has higher IV at OTM calls and OTM puts. When the smile becomes asymmetric (e.g., OTM puts much higher IV than OTM calls), it signals fear on the downside. The *change* in smile curvature is a leading indicator of price direction.

**Triggers:**
- **BULLISH:** OTM call IV < OTM put IV by > 0.10 AND call IV is falling
- **BEARISH:** OTM put IV < OTM call IV by > 0.10 AND put IV is falling
- **SMILE WIDENING:** (OTM_call_IV + OTM_put_IV) / ATM_IV > 1.15 → volatility expansion expected
- **SMILE FLATTENING:** ratio < 0.95 → volatility compression, range-bound expected

**Data Sources:**
- `optionchain_parsed` — IV, delta, volume per strike
- `gex_calculator` — IV skew, gamma ladder

**IV Smile Calculation:**
```
call_smile = avg(IV for OTM calls 1-3 strikes above ATM)
put_smile  = avg(IV for OTM puts  1-3 strikes below ATM)
atm_iv     = IV at ATM strike

skew       = call_smile - put_smile    (+ = call premium, - = put premium)
smile_width = (call_smile + put_smile) / atm_iv
```

**Example from samples:**
```
ATM Call (420C): IV=0.6008, delta=0.48
ATM Put  (420P): IV=0.6001, delta=-0.52
OTM Call (425C): IV=0.6486, delta=0.22
OTM Put  (395P): IV=1.0465, delta=-0.01

put_smile = 1.0465 (deep OTM put has HIGH IV = fear)
call_smile = 0.6486 (moderate)
skew = -0.398 (put premium dominant)
→ Bearish sentiment, but deep OTM put IV could mean oversold fear
```

**Hard Gates:**
- Minimum 5 strikes on each side (calls and puts)
- Volume filter: OTM options must have volume > 0
- Rolling 30m IV baseline for change detection

**Synergy with existing:**
- Enhances `IV Skew Squeeze` (#15) with curvature analysis
- Complements `Delta-IV Divergence` (#13) — this looks at cross-strike, that looks at ATM
- Works with `Extrinsic/Intrinsic Flow` (#22) — extrinsic value relates to IV

---

### 5. Order Book Stacking (OBS)
**Layer:** Layer 2 (Order Book Dynamics)  
**Signal Type:** Support/Resistance — hidden S/R from depth  
**Hold Time:** 15–60 min  
**Confidence Components:** Stack size, stack depth, price proximity, exchange quality

**Concept:**  
Large concentrations of orders at specific price levels (stacks) act as hidden support or resistance. Unlike gamma walls (which are options-derived), these are equity-level S/R from the actual order book. A "stack" is defined as a price level where total_size exceeds 3× the average level size. When price approaches a stack, it either bounces (if the stack holds) or breaks through with force (if the stack is consumed).

**Triggers:**
- **STACK DETECTION:** Any price level with total_size > 3× average level size
- **BOUNCE:** Price approaches stack from away, shows rejection (last price moves back)
- **BREAK:** Price approaches stack, volume surges, levels get consumed
- **STACK QUALITY:** Multi-exchange stacks (3+ exchanges) are stronger than single-exchange

**Data Sources:**
- `depthagg_parsed` — all 20 bid/ask levels with total_size, num_participants
- `depthquotes_parsed` — exchange attribution for stack quality
- `quotes_parsed` — last price for proximity

**Stack Detection:**
```
avg_level_size = sum(all_level_sizes) / num_levels
stack_threshold = 3.0 × avg_level_size

For each level:
  if total_size > stack_threshold:
    mark as stack
    stack_strength = total_size / stack_threshold
```

**Example from samples:**
```
Depth Aggregates Sample 1:
  419.50: total_size=4681, 4 participants ← MASSIVE bid stack
  Average level size ≈ 400
  Stack strength = 4681 / (3 × 400) = 3.9 → Very strong

  Price at 419.54, stack at 419.50 (0.04 below)
  → Strong support, expect bounce if price tests it
```

**Hard Gates:**
- Stack must be within 0.50 of current price
- Minimum 2 participants for "quality stack"
- Volume confirmation: volume > 80% of 5min mean

**Synergy with existing:**
- Equity-level complement to `Gamma Wall Bounce` — options walls vs. equity stacks
- Works with `Confluence Reversal` — stack + gamma wall = double S/R
- Adds depth dimension to `Magnet & Accelerate`

---

### 6. Spread Compression Breakout (SCB)
**Layer:** Layer 3 (Micro-Signal)  
**Signal Type:** Breakout — spread squeeze → expansion  
**Hold Time:** 3–20 min  
**Confidence Components:** Spread percentile, compression rate, volume, gamma alignment

**Concept:**  
When the bid-ask spread compresses to unusually tight levels, it signals energy buildup — like a coiled spring. The subsequent expansion (widening) often coincides with a directional move. This is the order book equivalent of Bollinger Band squeeze but at the micro-spread level.

**Triggers:**
- **COMPRESSION:** Spread in bottom 25% of 30m rolling range
- **BREAKOUT SIGNAL:** Spread starts widening (ROC > 0) AND price moves in direction of volume
- **LONG:** spread widens + price > VWAP + volume on bids
- **SHORT:** spread widens + price < VWAP + volume on asks

**Data Sources:**
- `depthagg_parsed` — spread (best_ask - best_bid)
- `quotes_parsed` — VWAP, volume, bid/ask sizes
- Rolling 30m spread window

**Spread Compression Detection:**
```
spread = best_ask - best_bid
spread_percentile = rank(spread, last_30m_spreads) / 30m_count

if spread_percentile < 0.25:
    compression = True
if spread_percentile > 0.25 and previous_percentile < 0.25:
    breakout = True  ← compression releasing
```

**Example from samples:**
```
Sample 1: spread = 0.05 (tight)
Sample 2: spread = 0.04 (very tight)
Sample 3: spread = 0.09 (normal/wide)

If 0.04 → 0.09 transition happens with volume → breakout signal
```

**Hard Gates:**
- Compression must last at least 3 consecutive ticks
- Volume must be > 60% of 5min mean
- Price must move at least 0.05 in breakout direction

**Synergy with existing:**
- Micro version of `Vol Compression Range` (#8) — spread vs. Bollinger
- Complements `IV Band Breakout` (#17) — equity spread vs. IV band
- Fast hold time fits Layer 3

---

### 7. Participant Diversity Signal (PDS)
**Layer:** Layer 2 (Order Book Dynamics)  
**Signal Type:** Conviction — breadth of participation  
**Hold Time:** 5–30 min  
**Confidence Components:** Participant count, exchange diversity, order concentration, trend alignment

**Concept:**  
When more participants (exchanges/venues) are actively quoting at the top levels, it signals broader market conviction. A single-exchange wall can be fake (spoofing); a multi-exchange concentration is real. Participant diversity is a quality filter for all other depth-based signals.

**Triggers:**
- **HIGH DIVERSITY:** bid_max_participants ≥ 3 AND ask_max_participants ≥ 2 → strong conviction
- **LOW DIVERSITY:** bid_max_participants ≤ 1 AND ask_max_participants ≤ 1 → weak, possibly spoofed
- **DIVERSITY SHIFT:** Rapid increase in participant count → new money entering
- **DIRECTIONAL:** High diversity on bid side + price rising = bullish conviction

**Data Sources:**
- `depthagg_parsed` — bid_avg_participants, ask_avg_participants, bid_max_participants, ask_max_participants
- `depthquotes_parsed` — exchange-level participant data

**Participant Quality Score:**
```
bid_quality = bid_max_participants / bid_avg_participants
ask_quality = ask_max_participants / ask_avg_participants

quality_score = (bid_quality + ask_quality) / 2

if quality_score > 2.0: strong conviction
if quality_score < 1.2: weak, possibly spoofed
```

**Example from samples:**
```
Sample 1: bid_avg=1.35, bid_max=4 → bid_quality=2.96
          ask_avg=1.20, ask_max=3 → ask_quality=2.50
          quality_score = 2.73 → Strong conviction

Sample 2: bid_avg=1.25, bid_max=3 → bid_quality=2.40
          ask_avg=1.20, ask_max=3 → ask_quality=2.50
          quality_score = 2.45 → Strong conviction
```

**Hard Gates:**
- Minimum 15 levels on each side (bid_levels ≥ 15, ask_levels ≥ 15)
- Participant diversity must be above baseline (rolling 30m)

**Synergy with existing:**
- Quality filter for all depth-based strategies (DIM, OBS, LVB)
- Complements `Call/Put Flow Asymmetry` — options flow quality
- Can enhance `Confluence Reversal` confidence score

---

### 8. Dealer Hedging Feedback Loop (DHFL)
**Layer:** Full Data (Advanced)  
**Signal Type:** Momentum — dealer-driven price acceleration  
**Hold Time:** 15–60 min  
**Confidence Components:** Gamma-driven delta, hedging flow, volume confirmation, regime alignment

**Concept:**  
When dealers are net short gamma, they must buy as price rises and sell as price falls (amplifying moves). When net long gamma, they fade moves (dampening). The feedback loop between price movement and dealer hedging creates self-reinforcing momentum. We detect this by tracking the relationship between price delta, gamma exposure, and volume.

**Triggers:**
- **POSITIVE FEEDBACK (momentum):** Price ↑ + Net Gamma negative + Volume ↑ → dealer buying accelerates rally
- **NEGATIVE FEEDBACK (mean reversion):** Price ↑ + Net Gamma positive + Volume ↓ → dealer selling dampens rally
- **FEEDBACK REVERSAL:** Price at extreme + Gamma flips sign → dealer hedging direction changes

**Data Sources:**
- `optionchain_parsed` — gamma, delta, volume per strike
- `gex_calculator` — Net Gamma, Gamma Ladder
- `quotes_parsed` — price, volume, net_change

**Feedback Loop Detection:**
```
gamma_regime = "negative" if net_gamma < 0 else "positive"

if gamma_regime == "negative" and price_delta > 0 and volume_spike:
    signal = "LONG"  # dealer hedging amplifies upward move
elif gamma_regime == "negative" and price_delta < 0 and volume_spike:
    signal = "SHORT" # dealer hedging amplifies downward move
elif gamma_regime == "positive" and price_delta > 0 and volume_decline:
    signal = "SHORT" # dealer hedging fades upward move
elif gamma_regime == "positive" and price_delta < 0 and volume_decline:
    signal = "LONG"  # dealer hedging fades downward move
```

**Hard Gates:**
- Net Gamma must be above/below threshold (±50k)
- Volume spike = > 1.3× rolling mean
- Gamma regime must persist for at least 5 minutes

**Synergy with existing:**
- Enhances `Gamma Flip Breakout` (#3) with dealer hedging context
- Complements `Delta-Gamma Squeeze` (#10) — this looks at the feedback loop, that looks at the squeeze
- Works with `Net Gamma Regime Filter` — provides the regime context for all strategies

---

## Strategy Summary Table

| # | Strategy | Layer | Signal | Hold | Data | Complexity |
|---|----------|-------|--------|------|------|------------|
| 23 | Exchange Flow Asymmetry | L2 | Directional | 10-45m | Depth Quotes | Medium |
| 24 | Depth Imbalance Momentum | L2 | Directional | 5-30m | Depth Agg | Low |
| 25 | Liquidity Vacuum Breakout | L3 | Breakout | 3-15m | Depth Agg | Low |
| 26 | IV Smile Dynamics | Full | Reversal | 30m-2h | Option Chain | Medium |
| 27 | Order Book Stacking | L2 | S/R | 15-60m | Depth Agg+Quotes | Medium |
| 28 | Spread Compression Breakout | L3 | Breakout | 3-20m | Depth Agg+Quotes | Low |
| 29 | Participant Diversity | L2 | Conviction | 5-30m | Depth Agg+Quotes | Low |
| 30 | Dealer Hedging Feedback | Full | Momentum | 15-60m | Option+GEX | High |

**Total after new strategies: 30 strategies (22 existing + 8 new)**

---

## Implementation Plan

### Phase 1: Quick Wins (Low complexity, high data leverage)
1. **Depth Imbalance Momentum** — uses existing depthagg data, simple ratio calculation
2. **Liquidity Vacuum Breakout** — uses existing depthagg levels, gap detection
3. **Spread Compression Breakout** — uses existing spread data, percentile-based
4. **Participant Diversity** — uses existing participant counts, quality scoring

### Phase 2: Medium Complexity
5. **Exchange Flow Asymmetry** — needs exchange baseline tracking
6. **Order Book Stacking** — needs stack detection algorithm
7. **IV Smile Dynamics** — needs cross-strike IV analysis

### Phase 3: Advanced
8. **Dealer Hedging Feedback Loop** — needs gamma-delta-volume integration

### Code Organization
- New strategies go in existing directories:
  - Layer 2: `strategies/layer2/`
  - Layer 3: `strategies/layer3/`
  - Full Data: `strategies/full_data/`
- Extend `GEXCalculator` with:
  - `get_exchange_flow()` — exchange volume breakdown
  - `get_depth_imbalance()` — bid/ask ratio + ROC
  - `detect_liquidity_vacuum()` — gap detection in depth
  - `get_iv_smile()` — cross-strike IV curvature
  - `detect_stacks()` — level size concentration
  - `get_spread_percentile()` — spread rolling percentile
  - `get_participant_quality()` — diversity scoring
  - `get_hedging_feedback()` — gamma-delta-volume loop

---

## Design Philosophy

These 8 strategies were designed with three principles:

1. **Data Leverage:** Each strategy uses Level 2 data that orb_probe.py already collects. No new data sources needed.
2. **Non-Overlap:** Each strategy captures a distinct market phenomenon — exchange flow, depth pressure, liquidity gaps, IV curvature, order book stacks, spread dynamics, participant quality, and dealer hedging.
3. **Progressive Complexity:** From simple ratio-based signals (DIM, SCB) to multi-factor strategies (DHFL), allowing incremental implementation and validation.

The goal is to give Syngex a comprehensive view of the market: from the micro (spread, liquidity gaps) to the macro (IV smile, dealer hedging), from the equity level (depth, exchange flow) to the options level (gamma feedback), all powered by the 4 streams orb_probe.py delivers.

---

*Rune's analysis — 2026-05-11 🐉*
