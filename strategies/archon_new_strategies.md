# Archon's New Strategy Designs for Syngex v2.0

**Author:** Archon (The Celestial Loom)
**Date:** 2026-05-12
**Purpose:** New strategy concepts leveraging Level 2 / TotalView / BATS venue data streams
**Target Layer:** Primarily Layer 2 (order flow + depth), some Layer 3 (micro-signals)

---

## Data Streams Ingested

From `orb_probe.py` and `LEVEL2_DATA_SAMPLES.jsonl`:

### Stream 1: Quotes (Level 1)
- **Fields:** last, bid, ask, bid_size, ask_size, volume, VWAP, last_size, last_venue
- **Venues:** IEX, BATS, EDGX, MEMX, BATY, NSDQ, ARCX, CHXE, EDGA, MPRL
- **Extras:** 52w high/low, is_delayed, is_halted, previous_volume, net_change_pct

### Stream 2: Depth Aggregates (Level 2)
- **Fields:** best_bid, best_ask, spread, total_bid_size, total_ask_size, bid_levels, ask_levels
- **Participant metrics:** bid_avg_participants, bid_max_participants, ask_avg_participants, ask_max_participants
- **Top 3 levels:** price, total_size, biggest_size, smallest_size, num_participants, total_order_count, earliest_time, latest_time

### Stream 3: Depth Quotes (Level 2 / TotalView)
- **Fields:** best_bid, best_ask, spread, total_bid_size, total_ask_size, bid_levels, ask_levels
- **Exchange-specific:** bid_exchanges dict, ask_exchanges dict (per-exchange sizes)
- **Per-level detail:** size, order_count, timestamp, exchange per bid/ask level

### Stream 4: Option Chain
- **Fields:** bid, ask, last, mid, bid_size, ask_size, volume, open_interest
- **Greeks:** delta, gamma, theta, vega, rho
- **Volatility:** iv, theoretical_value_iv
- **Probabilities:** probability_itm, probability_otm, probability_be (and IV-based variants)
- **Value:** intrinsic_value, extrinsic_value, theoretical_value
- **Metadata:** expiration, net_change, net_change_pct, 52w high/low

---

## Strategy Design Philosophy

The existing 20 strategies cover:
- **Layer 1:** Pure GEX structural plays (walls, magnets, flips, squeezes, imbalances, confluence, compression, divergence)
- **Layer 2:** Greeks + flow asymmetry (delta-gamma squeeze, delta-volume exhaustion, call/put flow, IV-GEX divergence, delta-IV divergence)
- **Layer 3:** Micro-signals (gamma-volume convergence, IV band breakout, strike concentration, theta burn)

**What's missing:** Strategies that specifically use the **exchange-level granularity**, **participant counts**, **order book depth structure**, and **venue-specific flow patterns** that our new Level 2/TotalView streams provide. These are the strategies below.

---

## New Strategy 1: Exchange Flow Imbalance (EFI)

**Layer:** Layer 2
**Data Sources:** Depth Quotes (exchange sizes), Quotes (venue)

### Concept
Different exchanges have different participant profiles:
- **MEMX / BATS / EDGX:** Often attract aggressive market orders (hitting the ask/bid)
- **IEX:** Known for the "speed bump" — attracts more passive, resting orders
- **NSDQ (NASDAQ):** Largest liquidity pool, institutional flow
- **ARCX (NYSE Arca):** Mix of institutional and retail
- **CHXE / MPRL / EDGA:** Smaller exchanges, often thin liquidity

When one exchange's size dominates the order book, it signals that a particular type of participant is accumulating aggressively. This creates directional pressure.

### Signal Logic

```
EFI Score = Σ(exchange_weight × exchange_size_ratio)

Where:
  exchange_weight = {
    MEMX: +0.3 (aggressive buyer proxy),
    BATS: +0.2 (aggressive buyer proxy),
    EDGX: +0.15 (aggressive buyer proxy),
    IEX: -0.2 (passive/mean-reversion proxy),
    NSDQ: +0.1 (institutional flow),
    ARCX: +0.05 (neutral institutional)
  }
  exchange_size_ratio = exchange_bid_size / total_bid_size
                       (or ask side for SHORT signals)

LONG signal: EFI > +0.35 (aggressive exchange dominance on bids)
SHORT signal: EFI < -0.30 (passive/defensive exchange dominance on asks)
```

### Entry/Exit
- **Entry:** EFI crosses threshold + price trending in signal direction
- **Stop:** 1% from entry
- **Target:** 1.5% from entry
- **Confidence boost:** When EFI aligns with GEX imbalance direction

### Why It's Unique
No existing Syngex strategy uses exchange-level granularity. This is pure Level 2 TotalView data — the ability to see that MEMX has 2040 shares on asks while NSDQ has 4582 on bids tells a story that total size alone cannot.

### Complexity: Low
Requires only exchange size aggregation and weighted scoring.

---

## New Strategy 2: Liquidity Vacuum Detection (LVD)

**Layer:** Layer 3 (micro-signal)
**Data Sources:** Depth Aggregates (top 3 levels), Depth Quotes

### Concept
A "liquidity vacuum" occurs when there's a gap in order book depth — a price zone with little to no resting orders between large walls. When price enters a vacuum, it accelerates through with minimal resistance, often overshooting.

From our data:
```
Level 1: 419.52 → 3 shares (thin)
Level 2: 419.50 → 4681 shares (wall)
Level 3: 419.49 → 1 share (vacuum!)
Level 4: 419.38 → 140 shares (wall)
```

The 419.50 → 419.49 gap is a vacuum. If price breaks 419.50, it'll likely accelerate toward 419.38.

### Signal Logic

```
For each price level i:
  depth_gap_i = |size_level_i - size_level_{i+1}|
  vacuum_score_i = depth_gap_i / avg_depth_nearby

Vacuum Zone = contiguous price levels where size < 0.2 × median_depth

LVD LONG: Price breaks above a vacuum zone → momentum upward
LVD SHORT: Price breaks below a vacuum zone → momentum downward

Entry: Price crosses vacuum boundary + volume spike
Stop: Other side of vacuum zone
Target: Next liquidity wall (largest adjacent depth level)
```

### Confidence Factors
1. **Vacuum width** (0.0–0.20): Wider vacuum = stronger signal
2. **Wall strength on exit side** (0.0–0.20): Stronger wall = bigger target
3. **Volume confirmation** (0.0–0.15): Volume > 2× average = validation
4. **Speed of approach** (0.0–0.10): Faster approach = higher momentum

### Complexity: Low-Medium
Requires scanning top 3-5 levels and computing depth gaps.

---

## New Strategy 3: Order Book Fragmentation (OBF)

**Layer:** Layer 2
**Data Sources:** Depth Aggregates (participant counts)

### Concept
When liquidity is concentrated among few participants at a price level, that wall is fragile — one participant pulling it causes a cascade. When liquidity is fragmented across many participants, the wall is robust and likely to hold.

From our data:
```
Fragile wall: price 419.50, size 4681, 4 participants → each has ~1170 shares
Robust wall:  price 419.39, size 140, 3 participants → distributed intent

Fragility ratio = max_order_size / total_size_at_level
  0.8+ = fragile (one participant dominates)
  0.3- = robust (distributed across many)
```

A fragile wall on the bid side that's about to be tested = high probability of sudden downside acceleration. A fragile wall on the ask side = upside breakout risk.

### Signal Logic

```
For each of top 3 bid/ask levels:
  fragility = biggest_size / total_size

LONG signal: Fragile ask wall + price approaching from below
  (ask wall about to break → acceleration upward)
SHORT signal: Fragile bid wall + price approaching from above
  (bid wall about to break → acceleration downward)

Entry: Price within 0.1% of fragile wall
Stop: Beyond the wall
Target: Next robust liquidity zone
```

### Confidence Factors
1. **Fragility ratio** (0.0–0.25): Higher = more fragile = stronger signal
2. **Distance to wall** (0.0–0.15): Closer = higher probability of test
3. **Wall size** (0.0–0.10): Larger fragile wall = bigger move when it breaks
4. **Participant count trend** (0.0–0.10): Decreasing participants = wall dissolving

### Complexity: Low
Requires biggest_size / total_size ratio computation per level.

---

## New Strategy 4: Theoretical Value Deviation (TVD)

**Layer:** Layer 2
**Data Sources:** Option Chain (theoretical_value, bid, ask, iv, delta)

### Concept
Options have a theoretical value derived from the Black-Scholes (or similar) model using the stream's own greeks and IV. When market bid/ask prices deviate significantly from theoretical value, it signals either:
1. **Mispricing** → potential arbitrage/profit opportunity
2. **Dealer hedging pressure** → dealers adjusting quotes due to gamma exposure

From our data samples:
```
TSLA 420C: bid=2.35, ask=2.37, theoretical=1.45
  Deviation = (2.36 - 1.45) / 1.45 = 62% overpriced
  → Dealer hedging pressure or elevated uncertainty

TSLA 395P: bid=0.03, ask=0.04, theoretical=0.00
  Deviation = extreme but tiny absolute value
  → Tail risk pricing (insurance premium)
```

### Signal Logic

```
For each option contract:
  deviation = (mid_price - theoretical_value) / theoretical_value

Aggregated across strikes:
  call_deviation = mean(|deviation|) for calls
  put_deviation = mean(|deviation|) for puts

LONG signal: call_deviation > put_deviation by threshold
  → Calls are relatively more expensive → dealer short gamma → price pressure up
  → OR: Call market is "hot" → speculative demand

SHORT signal: put_deviation > call_deviation by threshold
  → Puts are relatively more expensive → fear/hedging demand
  → OR: Put market is "hot" → defensive positioning

Entry: Deviation ratio crosses threshold
Stop: Deviation ratio reverses
Target: Mean reversion to normal deviation
```

### Confidence Factors
1. **Deviation magnitude** (0.0–0.25): Larger deviation = stronger signal
2. **IV level** (0.0–0.10): High IV = wider theoretical bands = be cautious
3. **Time to expiry** (0.0–0.10): Near expiry = gamma risk = higher deviation expected
4. **Volume alignment** (0.0–0.15): High volume on expensive side confirms flow

### Complexity: Low
Requires theoretical value comparison — already computed in the stream.

---

## New Strategy 5: IV Skew Dynamics (IVSD)

**Layer:** Layer 2
**Data Sources:** Option Chain (iv, strike, delta, side)

### Concept
The IV skew (volatility smile) tells us about market sentiment. Traditionally, puts have higher IV than calls (the "skew"). But the **dynamics** of the skew — how it changes over time — are more informative than the static level.

From our data, we have IV at every strike. We can compute:
- **Skew slope:** IV of OTM puts vs IV of OTM calls
- **Skew curvature:** Is the smile getting steeper or flatter?
- **Skew velocity:** Rate of change of skew over time

From samples:
```
TSLA 420C (ATM): IV = 0.6008
TSLA 425C (OTM call): IV = 0.6486
TSLA 420P (ATM): IV = 0.6001
TSLA 395P (OTM put): IV = 1.0465

Skew = IV(395P) - IV(425C) = 1.0465 - 0.6486 = 0.3979
  → Steep skew = fear regime
  → Flattening skew = complacency → potential calm
```

### Signal Logic

```
Skew = mean(IV of OTM puts) - mean(IV of OTM calls)
Skew_velocity = d(Skew)/dt over rolling window

LONG signal: Skew velocity < -threshold (skew flattening)
  → Fear decreasing → potential rally
  → Best when combined with positive GEX regime

SHORT signal: Skew velocity > +threshold (skew steepening)
  → Fear increasing → potential decline
  → Best when combined with negative GEX regime

Entry: Skew velocity crosses threshold
Stop: Skew velocity reverses
Target: Mean reversion to historical skew
```

### Confidence Factors
1. **Skew velocity magnitude** (0.0–0.25): Faster change = stronger signal
2. **Absolute skew level** (0.0–0.10): Extreme skew = mean reversion more likely
3. **GEX regime alignment** (0.0–0.15): Skew + GEX in same direction = high confidence
4. **Volume on OTM options** (0.0–0.10): High OTM volume confirms positioning

### Complexity: Low-Medium
Requires tracking IV across strikes over time and computing derivatives.

---

## New Strategy 6: Spread Compression Breakout (SCB)

**Layer:** Layer 3 (micro-signal)
**Data Sources:** Quotes (bid/ask), Depth Aggregates (spread)

### Concept
The bid-ask spread is a direct measure of liquidity conditions and market maker uncertainty. When spreads compress to extreme lows, it often precedes a volatility expansion and significant price move. This is analogous to Bollinger Band squeezes but at the microstructure level.

From our data:
```
Tight spread: 0.04 (419.38 → 419.42 on 419.40 mid) = 0.01% of price
Wide spread: 0.09 (419.39 → 419.48 on 419.435 mid) = 0.02% of price

Spread % = (ask - bid) / mid_price × 100
```

### Signal Logic

```
Rolling spread % over window W (e.g., 50 ticks)
spread_compression = current_spread_pct / rolling_avg_spread_pct

LONG signal: Spread compression + volume surge + price above VWAP
  → Liquidity tightening before upward breakout
  → Entry: Price breaks above recent high + spread re-expands

SHORT signal: Spread compression + volume surge + price below VWAP
  → Liquidity tightening before downward breakout
  → Entry: Price breaks below recent low + spread re-expands

Stop: Opposite side of compression range
Target: 1.5× the compression range height
```

### Confidence Factors
1. **Compression ratio** (0.0–0.25): More compressed = stronger signal
2. **Volume surge** (0.0–0.20): Volume > 2× average during compression
3. **VWAP alignment** (0.0–0.10): Price direction aligned with VWAP
4. **Depth confirmation** (0.0–0.15): Total depth declining during compression

### Complexity: Low
Requires rolling spread percentage and volume comparison.

---

## New Strategy 7: Extrinsic Value Flow (EVF)

**Layer:** Layer 2
**Data Sources:** Option Chain (extrinsic_value, volume, open_interest, delta)

### Concept
Extrinsic value (time value) is the portion of option premium that reflects speculative positioning and time decay. By tracking extrinsic value flow (volume × extrinsic value), we can detect when traders are paying for speculation vs. when they're buying/selling insurance.

From our data:
```
TSLA 420C: extrinsic = 2.37, volume = 26670
  Extrinsic flow = 26670 × 2.37 = 63,208

TSLA 395P: extrinsic = 0.04, volume = 344
  Extrinsic flow = 344 × 0.04 = 13.8

Call extrinsic flow vs Put extrinsic flow tells us:
  Call-heavy = speculative bullish positioning
  Put-heavy = defensive/hedging positioning
```

### Signal Logic

```
call_extrinsic_flow = Σ(volume × extrinsic_value) for all calls
put_extrinsic_flow = Σ(volume × extrinsic_value) for all puts

EVF ratio = call_extrinsic_flow / put_extrinsic_flow

LONG signal: EVF ratio > threshold + call extrinsic concentrated in OTM
  → Speculative call buying → bullish momentum expected

SHORT signal: EVF ratio < threshold + put extrinsic concentrated in OTM
  → Speculative put buying → bearish momentum expected

Entry: EVF ratio crosses threshold
Stop: EVF ratio reverses
Target: Momentum continuation until ratio normalizes
```

### Confidence Factors
1. **EVF ratio magnitude** (0.0–0.25): More extreme = stronger signal
2. **OI change alignment** (0.0–0.15): Rising OI on the flow side confirms new positions
3. **Delta profile** (0.0–0.10): OTM flow = speculative (stronger signal) vs ITM flow = directional
4. **Theta environment** (0.0–0.10): High theta = extrinsic decaying faster = urgency

### Complexity: Low-Medium
Requires aggregating extrinsic flow across all options and tracking over time.

---

## Implementation Priority Matrix

| Strategy | Layer | Complexity | Data Dependency | Edge Potential | Implementation Priority |
|----------|-------|-----------|-----------------|----------------|----------------------|
| Exchange Flow Imbalance | L2 | Low | Depth Quotes | ★★★★☆ | **1st** |
| Liquidity Vacuum Detection | L3 | Low-Med | Depth Agg/Quotes | ★★★★☆ | **2nd** |
| Order Book Fragmentation | L2 | Low | Depth Agg | ★★★☆☆ | **3rd** |
| Theoretical Value Deviation | L2 | Low | Option Chain | ★★★☆☆ | **4th** |
| IV Skew Dynamics | L2 | Low-Med | Option Chain | ★★★★☆ | **5th** |
| Spread Compression Breakout | L3 | Low | Quotes/Depth | ★★★☆☆ | **6th** |
| Extrinsic Value Flow | L2 | Low-Med | Option Chain | ★★★★☆ | **7th** |

---

## Grid Placement Recommendations

Current heatmap is 6×4 with 20 strategy cells. New strategies can be added by:
1. **Replacing underperformers:** Identify strategies with persistent bleeding P&L and swap
2. **Expanding grid:** Move to 6×5 (30 cells) for room to grow
3. **Layer reorganization:** Consider a Layer 2.5 for order book-specific strategies

**Recommended initial placements:**

| New Strategy | Current Slot To Replace | Reason |
|-------------|------------------------|--------|
| Exchange Flow Imbalance | Replace lowest-WR strategy | High edge, complementary to existing |
| IV Skew Dynamics | Replace lowest-WR strategy | Complements IV band breakout |
| Liquidity Vacuum Detection | Replace lowest-WR strategy | Micro-signal, complements gamma squeezes |

---

## Key Insights from Data Analysis

### What the Streams Reveal That Previous Data Didn't

1. **Venue granularity:** We can now see WHICH exchange is providing liquidity, not just how much. MEMX walls vs NSDQ walls tell different stories.

2. **Participant behavior:** The `num_participants` and `biggest_size` fields let us distinguish between a single large player and distributed consensus. This is critical for wall reliability.

3. **Order book structure:** `total_size` vs `biggest_size` vs `smallest_size` per level gives us the full distribution of order sizes at each price — not just the aggregate.

4. **Theoretical values:** The option chain stream provides model-derived theoretical values, enabling real-time mispricing detection without computing our own Black-Scholes.

5. **Probabilities:** ITM/OTM/Break-even probabilities give us direct market-implied probability distributions, not just delta-based approximations.

### Data Quality Notes

- **venue field:** In Depth Quotes, exchange names vary (NSDQ vs NASDAQ, BATY vs BATS). Need normalization.
- **size types:** Depth Aggregates uses `total_size`, Depth Quotes uses `size`. Quotes uses string sizes. Need consistent parsing.
- **probe timestamps:** All streams include `_probe_ts` for alignment. Use this to synchronize multi-stream signals.
- **empty symbol:** Depth streams have `symbol: ""` — need to infer from context/orchestrator.

---

## Next Steps

1. **Validate:** Run backtests on existing LEVEL2_DATA_SAMPLES.jsonl for each new strategy
2. **Implement:** Delegate to Forge with clear specs from this document
3. **Register:** Add to layer2/__init__.py or layer3/__init__.py
4. **Configure:** Add to config/heatmap.yaml grid placement
5. **Monitor:** Track P&L and win rates alongside existing 20 strategies

---

*Archon out. The loom weaves new threads.* 🕸️
