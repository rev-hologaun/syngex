# STRATEGY_DESIGN_LEVEL2 — New Strategies for Level 2 / TotalView / BATS Data

> **Author:** Forge 🐙
> **Date:** 2026-05-11
> **Purpose:** Design new strategies that leverage the full depth of Level 2 (aggregated), TotalView (per-exchange quotes), and BATS venue data — beyond what the existing 22 strategies use.
> **Status:** Design phase. Ready for Archon to implement.

---

## Data Inventory — What We Have That Existing Strategies Don't Fully Use

### 1. Depth Aggregated (`market_depth_agg`)
- **Top 20 bid/ask levels** with total size per level
- **Participant counts** per level (how many different traders/exchanges are at each price)
- **Order counts** per level (how many individual orders)
- **Biggest/Smallest size** per level (distribution of order sizes)
- **Time stamps** (earliest/latest order at each level)

**What existing strategies use:** Best bid/ask, total bid/ask size, spread.
**What they DON'T use:** Participant diversity, order count intensity, size distribution, time decay of liquidity.

### 2. Depth Quotes / TotalView (`market_depth_quotes`)
- **Per-exchange breakdown:** NSDQ, MEMX, ARCX, EDGA, EDGX, BATS, CHXE, BATY, IEX, MPRL
- **Individual level entries** with exchange, size, order count, timestamp
- **Exchange-specific liquidity concentration**

**What existing strategies use:** Nothing directly.
**What they DON'T use:** Exchange-specific flow, venue concentration, inter-exchange dynamics.

### 3. Quotes (Level 1)
- **Venue of last trade:** IEX, BATS, EDGX, etc.
- **VWAP tracking**
- **Bid/ask size at best level only**

**What existing strategies use:** Price, VWAP, bid/ask size, volume.
**What they DON'T use:** Venue-specific aggression patterns, last-trade venue concentration.

### 4. Option Chain
- **Per-strike Greeks, IV, probabilities, OI, volume**

**What existing strategies use:** Gamma walls, IV skew, delta, probability ITM, extrinsic/intrinsic.
**What they DON'T use:** Cross-validation with order book depth, IV-scaled depth analysis.

---

## New Strategy Designs

### Strategy L2-01: VAMP Momentum (Volume-Adjusted Mid-Price)

**Layer:** Layer 2 (Alpha — Order Book Microstructure)
**Data Sources:** Depth Aggregated + Quotes
**Hold Time:** 5–30 min
**Direction:** Bidirectional (LONG/SHORT)

#### Concept
The simple mid-price `(best_bid + best_ask) / 2` is a poor estimate of fair value when the book is imbalanced. The **Volume-Adjusted Mid-Price (VAMP)** weights each side by the depth at each level:

```
VAMP_N = (Σ(P_bid^i × Q_ask^i) + Σ(P_ask^i × Q_bid^i)) / (ΣQ_bid^i + ΣQ_ask^i)
```

Where N = number of price levels (use top 5, 10, or 20).

When VAMP > mid-price, the book is weighted toward the bid side → bullish microstructure.
When VAMP < mid-price, the book is weighted toward the ask side → bearish microstructure.

#### Signal Logic
1. Compute VAMP using top N levels (configurable: 5, 10, 20)
2. Compute `vamp_deviation = (VAMP - mid_price) / mid_price`
3. LONG signal when: `vamp_deviation > threshold` AND price is NOT already at 30m high
4. SHORT signal when: `vamp_devidence < -threshold` AND price is NOT already at 30m low
5. Use Net Gamma filter for regime confirmation

#### Confidence Components
- `vamp_deviation_magnitude` — primary signal strength
- `depth_ratio` — total bid/ask depth (confirms genuine imbalance, not just one level)
- `volume_confirmation` — recent volume spike supports the move
- `regime_bonus` — +0.15 if Net Gamma regime aligns

#### Why It Works
VAMP is a well-established microstructure metric used by market makers and HFT firms. It captures the "true" mid-price when the book is skewed. When VAMP deviates significantly from the simple mid, it means one side of the book is absorbing more liquidity — a leading indicator of price movement.

#### Parameters (YAML)
```yaml
vamp_momentum:
  min_confidence: 0.35
  vamp_levels: 10          # Number of levels for VAMP calculation
  long_threshold: 0.0003   # 3 bps deviation
  short_threshold: -0.0003
  depth_ratio_min: 0.5     # Min bid/ask ratio (avoid extreme thinness)
  hold_seconds: 900
  cooldown_seconds: 30
```

---

### Strategy L2-02: Participant Diversity Conviction

**Layer:** Layer 2 (Alpha — Order Book Microstructure)
**Data Sources:** Depth Aggregated
**Hold Time:** 15–45 min
**Direction:** Bidirectional

#### Concept
A liquidity wall supported by **many participants** is structurally stronger than one supported by a single participant. Participant count is a proxy for institutional conviction:
- **1 participant** = likely a single large order (fragile, can be pulled)
- **3+ participants** = multiple traders agree on this level (strong, sticky)

This strategy identifies price levels where the participant count diverges significantly between bid and ask sides.

#### Signal Logic
1. Compute `bid_diversity = avg(bid_levels.num_participants)` for top 5 levels
2. Compute `ask_diversity = avg(ask_levels.num_participants)` for top 5 levels
3. Compute `diversity_ratio = bid_diversity / ask_diversity`
4. LONG signal when: `diversity_ratio > 2.0` (many buyers, few sellers at key levels)
5. SHORT signal when: `diversity_ratio < 0.5` (many sellers, few buyers at key levels)
6. Additional filter: at least one bid/ask level must have 3+ participants

#### Confidence Components
- `diversity_ratio` — primary signal strength
- `max_bid_participants` — peak conviction on bid side
- `max_ask_participants` — peak conviction on ask side
- `depth_weighted_diversity` — weight diversity by size at each level
- `regime_bonus` — +0.15 if Net Gamma regime aligns

#### Why It Works
Single-participant walls are often spoofing or thin liquidity. Multi-participant walls represent genuine market agreement on value. This is the "smart money" signal hidden in the order book metadata.

#### Parameters (YAML)
```yaml
participant_diversity:
  min_confidence: 0.35
  diversity_window: 5      # Top N levels to analyze
  long_threshold: 2.0      # Bid diversity 2x ask diversity
  short_threshold: 0.5     # Ask diversity 2x bid diversity
  min_participants: 3      # At least N participants at one level
  hold_seconds: 1200
  cooldown_seconds: 60
```

---

### Strategy L2-03: Exchange Flow Concentration

**Layer:** Layer 2 (Alpha — Venue Flow)
**Data Sources:** Depth Quotes (TotalView)
**Hold Time:** 5–20 min
**Direction:** Bidirectional

#### Concept
Different exchanges attract different types of flow:
- **NSDQ (NASDAQ):** Institutional, large orders, slower flow
- **MEMX:** Newer exchange, aggressive flow, often leads price discovery
- **BATS:** High-frequency, aggressive, often first to move
- **EDGX/EDGA:** CBOE venues, mix of institutional and flow
- **IEX:** "Speed bump" exchange, often shows genuine intent (not spoofing)
- **ARCX (NYSE):** Traditional, institutional

When aggressive flow concentrates on one exchange, it often precedes price movement. MEMX and BATS are particularly good leading indicators because they attract flow-hungry algorithms.

#### Signal Logic
1. Track exchange-specific bid/ask sizes over a rolling 2-minute window
2. Compute `memx_bias = memx_bid_size / memx_ask_size`
3. Compute `bats_bias = bats_bid_size / bats_ask_size`
4. Compute `iex_intent_score = iex_bid_size / (iex_bid_size + iex_ask_size)` — IEX is less prone to spoofing
5. LONG signal when: `memx_bias > 2.0` OR `bats_bias > 2.0` OR `iex_intent_score > 0.7`
6. SHORT signal when: `memx_bias < 0.5` OR `bats_bias < 0.5` OR `iex_intent_score < 0.3`
7. Require at least 2 of 3 signals to confirm (reduces false signals)

#### Confidence Components
- `memx_concentration` — MEMX bid/ask ratio
- `bats_concentration` — BATS bid/ask ratio
- `iex_intent` — IEX intent score (weighted higher due to lower spoof risk)
- `cross_exchange_agreement` — how many exchanges agree on direction
- `regime_bonus` — +0.15 if Net Gamma regime aligns

#### Why It Works
MEMX and BATS are known to attract aggressive, flow-driven algorithms. When these venues show concentrated buying or selling, it's often a leading signal. IEX's "speed bump" design filters out latency arbitrage, making its flow more indicative of genuine intent.

#### Parameters (YAML)
```yaml
exchange_flow:
  min_confidence: 0.35
  memx_threshold: 2.0      # MEMX bid/ask ratio
  bats_threshold: 2.0      # BATS bid/ask ratio
  iex_intent_threshold: 0.7 # IEX intent score
  confirm_count: 2         # Require N of 3 exchanges to agree
  hold_seconds: 600
  cooldown_seconds: 30
```

---

### Strategy L2-04: Depth Decay Momentum

**Layer:** Layer 2 (Alpha — Liquidity Dynamics)
**Data Sources:** Depth Aggregated
**Hold Time:** 3–15 min
**Direction:** Bidirectional

#### Concept
Liquidity doesn't just sit there — it appears and disappears. The **rate of decay** of liquidity on one side of the book is a powerful short-term signal:
- **Bid liquidity disappearing** = buyers are pulling orders → bearish
- **Ask liquidity disappearing** = sellers are pulling orders → bullish
- **New liquidity appearing on the opposite side** = aggressive positioning

This strategy tracks the rate of change of total bid/ask size and detects when one side is "evaporating."

#### Signal Logic
1. Track `total_bid_size` and `total_ask_size` over a 30-second rolling window
2. Compute `bid_decay_rate = (current_bid - avg_bid_30s) / avg_bid_30s`
3. Compute `ask_decay_rate = (current_ask - avg_ask_30s) / avg_ask_30s`
4. LONG signal when: `ask_decay_rate < -0.15` (ask liquidity evaporating ≥15%)
5. SHORT signal when: `bid_decay_rate < -0.15` (bid liquidity evaporating ≥15%)
6. Additional filter: new liquidity must be appearing on the opposite side (confirming aggression)
7. Exclude if spread is widening (could be market stress, not directional signal)

#### Confidence Components
- `ask_decay_rate` / `bid_decay_rate` — primary signal strength
- `opposite_side_growth` — new liquidity on opposite side (confirms aggression)
- `spread_stability` — narrow/stable spread (excludes stress events)
- `depth_ratio_change` — how the overall bid/ask ratio is shifting
- `regime_bonus` — +0.15 if Net Gamma regime aligns

#### Why It Works
When liquidity evaporates on one side, it means participants are pulling orders — often because they anticipate price moving in that direction. This is a leading indicator of short-term price movement. The "evaporation" signal is particularly strong when accompanied by new liquidity appearing on the opposite side (aggressive positioning).

#### Parameters (YAML)
```yaml
depth_decay:
  min_confidence: 0.35
  decay_window_seconds: 30  # Rolling window for decay calculation
  decay_threshold: 0.15     # 15% decay to trigger signal
  opposite_growth_min: 0.05 # Min growth on opposite side to confirm
  max_spread_bps: 15        # Exclude if spread > 15 bps
  hold_seconds: 480
  cooldown_seconds: 15
```

---

### Strategy L2-05: Gamma Wall + Liquidity Wall Confluence

**Layer:** Layer 3 (Micro-Signal — Cross-Asset)
**Data Sources:** Depth Aggregated + Option Chain (Gamma)
**Hold Time:** 10–30 min
**Direction:** Mean Reversion at confluence levels

#### Concept
Gamma walls (from options) and liquidity walls (from order book) at the same price level create **doubly strong** support/resistance. When both converge, the price reaction is amplified:
- **Gamma call wall + bid liquidity wall** = extremely strong support → LONG bounce
- **Gamma put wall + ask liquidity wall** = extremely strong resistance → SHORT bounce
- **Gamma wall WITHOUT liquidity wall** = weaker signal (options-only walls can be gamed)

This is the "confluence on steroids" — combining two independent data sources that both predict the same price reaction.

#### Signal Logic
1. Identify top 3 gamma call walls (highest positive gamma) and put walls (highest negative gamma)
2. For each gamma wall, check if there's significant liquidity within ±$1.00:
   - `liquidity_present = total_size_at_wall_level > 500`
   - `liquidity_strong = total_size_at_wall_level > 2000`
3. Compute `confluence_score`:
   - Gamma wall + liquidity within $1.00 = +0.3
   - Gamma wall + liquidity within $0.50 = +0.2 bonus
   - Liquidity strength > 2000 = +0.1 bonus
   - Participant diversity > 2 at wall level = +0.1 bonus
4. LONG signal when: confluence_score > 0.6 at a gamma call wall + bid liquidity
5. SHORT signal when: confluence_score > 0.6 at a gamma put wall + ask liquidity

#### Confidence Components
- `gamma_strength` — gamma magnitude at the wall
- `liquidity_strength` — total size at the wall
- `price_proximity` — how close price is to the wall
- `participant_diversity` — multi-participant confirmation
- `regime_bonus` — +0.15 if regime supports mean reversion (positive gamma)

#### Why It Works
Gamma walls force dealer hedging (buy dips, sell rips in positive gamma). Liquidity walls represent actual order flow. When both align, you have structural + flow confirmation — the highest conviction signal available in the data.

#### Parameters (YAML)
```yaml
gamma_liquidity_confluence:
  min_confidence: 0.40
  gamma_wall_threshold: 50000   # Min gamma magnitude
  liquidity_threshold: 500       # Min size for "present"
  liquidity_strong: 2000         # Min size for "strong"
  proximity_dollar: 1.0          # Max distance for confluence
  proximity_bonus_dollar: 0.5    # Bonus for tighter proximity
  hold_seconds: 1200
  cooldown_seconds: 120
```

---

### Strategy L2-06: Order Count Intensity (Retail vs Institutional)

**Layer:** Layer 2 (Alpha — Order Book Microstructure)
**Data Sources:** Depth Aggregated
**Hold Time:** 5–20 min
**Direction:** Bidirectional

#### Concept
The relationship between **order count** and **total size** at a price level reveals the type of participant:
- **High size / low order count** = few large orders = institutional
- **Low size / high order count** = many small orders = retail
- **High size / high order count** = mixed = strong conviction

This strategy uses the `biggest_size / smallest_size` ratio and `total_order_count` to detect institutional accumulation/distribution.

#### Signal Logic
1. For top 5 bid levels: compute `institutional_ratio = sum(biggest_size) / sum(smallest_size)`
2. For top 5 ask levels: compute `institutional_ratio = sum(biggest_size) / sum(smallest_size)`
3. Compute `order_intensity = total_order_count / total_size` (orders per share)
4. LONG signal when:
   - Bid institutional_ratio > 5.0 (large bid orders, few small ones)
   - Bid order_intensity < 0.01 (few orders, large size)
   - Ask institutional_ratio < 2.0 (sellers are retail/fragmented)
5. SHORT signal when:
   - Ask institutional_ratio > 5.0 (large ask orders)
   - Ask order_intensity < 0.01
   - Bid institutional_ratio < 2.0 (buyers are retail/fragmented)

#### Confidence Components
- `bid_institutional_ratio` — institutional conviction on bid side
- `ask_institutional_ratio` — institutional conviction on ask side
- `bid_order_intensity` — retail vs institutional mix on bids
- `ask_order_intensity` — retail vs institutional mix on asks
- `size_concentration` — how concentrated the largest orders are
- `regime_bonus` — +0.15 if Net Gamma regime aligns

#### Why It Works
Institutional orders are harder to pull than retail orders. When you see large, concentrated orders on one side and fragmented orders on the other, it signals that "smart money" is positioned directionally. The biggest_size/smallest_size ratio is a direct proxy for this.

#### Parameters (YAML)
```yaml
order_intensity:
  min_confidence: 0.35
  institutional_threshold: 5.0   # Biggest/Smallest ratio
  retail_threshold: 2.0          # Max ratio for "retail" side
  order_intensity_threshold: 0.01 # Orders per share
  hold_seconds: 900
  cooldown_seconds: 30
```

---

### Strategy L2-07: IV-Skew Depth Confirmation

**Layer:** Layer 3 (Micro-Signal — Cross-Asset)
**Data Sources:** Depth Aggregated + Option Chain (IV Skew)
**Hold Time:** 15–60 min
**Direction:** Bidirectional

#### Concept
IV skew tells you the market's sentiment (fear vs greed). Depth imbalance tells you the actual order flow. When **both agree**, you have high-conviction signals:
- **High put skew (fear) + bid depth dominance** = genuine institutional put buying → SHORT (fear is being hedged, not directional)
- **High call skew (greed) + ask depth dominance** = genuine institutional call buying → LONG
- **High put skew + ask depth dominance** = fear but sellers are aggressive → STRONG SHORT
- **High call skew + bid depth dominance** = greed but buyers are aggressive → STRONG LONG

The key insight: IV skew alone can be misleading (options traders hedge differently than stock traders). Depth confirmation validates whether the options sentiment is translating to actual stock flow.

#### Signal Logic
1. Compute `iv_skew = IV_put_ATM - IV_call_ATM` (from option chain)
2. Compute `depth_imbalance = (total_bid_size - total_ask_size) / (total_bid_size + total_ask_size)`
3. Compute `confirmation_score`:
   - Skew > 0 (fear) + depth_imbalance > 0.2 (bid heavy) = +0.2 (hedging, not directional)
   - Skew > 0 (fear) + depth_imbalance < -0.2 (ask heavy) = +0.4 (STRONG SHORT)
   - Skew < 0 (greed) + depth_imbalance < -0.2 (ask heavy) = +0.2 (hedging)
   - Skew < 0 (greed) + depth_imbalance > 0.2 (bid heavy) = +0.4 (STRONG LONG)
   - Skew near 0 + any depth imbalance = +0.15 (neutral regime, pure depth signal)
4. LONG signal when: `confirmation_score > 0.35`
5. SHORT signal when: `confirmation_score > 0.35` (inverse direction)

#### Confidence Components
- `iv_skew_magnitude` — options sentiment strength
- `depth_imbalance` — order flow direction
- `skew_depth_agreement` — do they point the same way?
- `volume_confirmation` — recent volume supports the move
- `regime_bonus` — +0.15 if Net Gamma regime aligns

#### Why It Works
IV skew captures options market sentiment, which often leads stock price. But options traders hedge differently than stock traders. By cross-validating with actual stock depth, you filter out false signals where options positioning doesn't translate to stock flow.

#### Parameters (YAML)
```yaml
iv_skew_depth:
  min_confidence: 0.35
  skew_threshold: 0.05       # Min IV skew to consider
  depth_imbalance_threshold: 0.2  # Min depth imbalance
  strong_agreement_score: 0.4
  weak_agreement_score: 0.2
  neutral_depth_score: 0.15
  hold_seconds: 1800
  cooldown_seconds: 120
```

---

### Strategy L2-08: Order Book Imbalance (OBI) with Order Flow

**Layer:** Layer 2 (Alpha — Order Book Microstructure)
**Data Sources:** Depth Aggregated + Quotes
**Hold Time:** 3–15 min
**Direction:** Bidirectional

#### Concept
**Order Book Imbalance (OBI)** is the most studied microstructure signal in academic literature. It measures the relative size of bid vs ask depth:

```
OBI = (ΣQ_bid^N - ΣQ_ask^N) / (ΣQ_bid^N + ΣQ_ask^N)
```

Where N = number of price levels. OBI ranges from -1 (all ask) to +1 (all bid).

The key innovation: combine OBI with **order flow** (volume-weighted bid/ask trades from quotes) to distinguish between passive positioning and active aggression.

#### Signal Logic
1. Compute `obi_5 = (ΣQ_bid_top5 - ΣQ_ask_top5) / (ΣQ_bid_top5 + ΣQ_ask_top5)`
2. Compute `obi_10 = (ΣQ_bid_top10 - ΣQ_ask_top10) / (ΣQ_bid_top10 + ΣQ_ask_top10)`
3. Compute `order_flow = (volume_on_up_ticks - volume_on_down_ticks) / total_volume`
4. LONG signal when:
   - `obi_10 > 0.3` (significant bid depth advantage)
   - `order_flow > 0.1` (aggressive buying)
   - Price NOT at 30m high (room to run)
5. SHORT signal when:
   - `obi_10 < -0.3` (significant ask depth advantage)
   - `order_flow < -0.1` (aggressive selling)
   - Price NOT at 30m low (room to fall)
6. Use `obi_5 / obi_10` ratio to detect if imbalance is concentrated at best level (fragile) or deeper (stronger)

#### Confidence Components
- `obi_10` — primary imbalance signal
- `order_flow` — confirms active aggression vs passive positioning
- `obi_concentration` — ratio of 5-level to 10-level OBI (concentrated = fragile)
- `volume_spike` — volume confirms the move
- `regime_bonus` — +0.15 if Net Gamma regime aligns

#### Why It Works
OBI is a proven academic signal. The addition of order flow distinguishes between passive liquidity provision and active aggression. When both OBI and order flow agree, the signal is much stronger than either alone.

#### Parameters (YAML)
```yaml
obi_orderflow:
  min_confidence: 0.35
  obi_threshold: 0.3         # Min OBI magnitude
  order_flow_threshold: 0.1  # Min order flow
  max_obi_concentration: 0.7 # Max ratio of 5-level to 10-level OBI
  hold_seconds: 480
  cooldown_seconds: 15
```

---

## Strategy Summary Table

| # | Strategy | Layer | Data Sources | Hold Time | Signal Type | Key Innovation |
|---|----------|-------|-------------|-----------|-------------|----------------|
| L2-01 | VAMP Momentum | 2 | Depth Agg + Quotes | 5–30m | Momentum | Volume-adjusted mid-price |
| L2-02 | Participant Diversity | 2 | Depth Agg | 15–45m | Conviction | Multi-participant walls = institutional |
| L2-03 | Exchange Flow Concentration | 2 | Depth Quotes | 5–20m | Flow | MEMX/BATS leading indicator |
| L2-04 | Depth Decay Momentum | 2 | Depth Agg | 3–15m | Momentum | Liquidity evaporation = leading signal |
| L2-05 | Gamma+Liquidity Confluence | 3 | Depth Agg + Options | 10–30m | Mean Reversion | Dual-wall confirmation |
| L2-06 | Order Count Intensity | 2 | Depth Agg | 5–20m | Institutional Flow | Size/count ratio = retail vs institutional |
| L2-07 | IV-Skew Depth Confirmation | 3 | Depth Agg + Options | 15–60m | Cross-Asset | Options sentiment + stock flow validation |
| L2-08 | OBI + Order Flow | 2 | Depth Agg + Quotes | 3–15m | Momentum | Academic OBI + active aggression |

---

## Implementation Priority

### Tier 1 (Quick Wins — Pure Depth Agg data, easy to implement)
1. **L2-08 OBI + Order Flow** — Most academically proven, uses existing depth agg data
2. **L2-01 VAMP Momentum** — Novel for Syngex, uses existing depth agg data
3. **L2-04 Depth Decay** — Dynamic, captures liquidity changes

### Tier 2 (Requires Depth Quotes / TotalView)
4. **L2-03 Exchange Flow** — Requires per-exchange data, high signal quality
5. **L2-02 Participant Diversity** — Requires participant counts, good signal

### Tier 3 (Cross-Asset — Need to wire in options data)
6. **L2-05 Gamma+Liquidity Confluence** — Combines two data sources, high conviction
7. **L2-07 IV-Skew Depth** — Cross-asset validation, longer hold time

---

## Notes on Data Availability

From the LEVEL2_DATA_SAMPLES.jsonl, the following fields are confirmed available:
- ✅ `total_bid_size`, `total_ask_size` (depth agg)
- ✅ `bid_levels`, `ask_levels` (depth agg)
- ✅ `num_participants` per level (depth agg)
- ✅ `total_order_count` per level (depth agg)
- ✅ `biggest_size`, `smallest_size` per level (depth agg)
- ✅ `earliest_time`, `latest_time` per level (depth agg)
- ✅ `bid_exchanges`, `ask_exchanges` dicts (depth quotes)
- ✅ Exchange-specific sizes: NSDQ, MEMX, ARCX, EDGA, EDGX, BATS, CHXE, BATY, IEX, MPRL
- ✅ Per-level exchange entries with size, order_count, timestamp, exchange name
- ✅ Option chain: IV, delta, gamma, theta, vega, probability_ITM, extrinsic, intrinsic

All 8 strategies are feasible with the current data pipeline.

---

## Future Enhancements (Not in Scope)

1. **Order Book Reconstruction** — Reconstruct the full LOB from depth quotes for more granular analysis
2. **Spoofing Detection** — Detect and filter out spoofed liquidity (rapid appearance/disappearance)
3. **Cross-Symbol Depth** — If we add SPY/QQQ depth, we can detect index-driven moves
4. **ML Classification** — Train a classifier on historical depth patterns to predict short-term direction
5. **Real-Time Heatmap** — Add depth-based indicators to the heatmap dashboard
