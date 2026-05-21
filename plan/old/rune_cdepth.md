# Rune's Depth-Enhanced Confidence Framework

> Generated 2026-05-13 by Rune 🐉
> Context: Syngex v2.09, 41 strategies, 0 runtime data, market opens in ~6.5h
> Goal: Integrate Level 2 / TotalView / BATS depth data into confidence formulae

---

## The Problem

We have 41 strategies flying blind on untested code. The confidence formulae are set, the bugs are fixed, but we're calculating confidence on a fraction of the available data. Depth data from Level 2 / TotalView / BATS streams sits in the rolling windows but isn't fully leveraged in the confidence calculation.

## What We Already Have

Four active data streams feeding rolling windows:

| Stream | What It Gives | Current Depth Keys |
|--------|--------------|-------------------|
| **Quotes (L1)** | Price, bid, ask, size, volume, VWAP, venue | `volume_5m`, `flow_ratio_5m` |
| **Depth Aggregates (L2)** | Top 20 levels, total size, participants, order counts | `depth_bid_size_5m`, `depth_ask_size_5m`, `depth_spread_5m`, `depth_bid_levels_5m`, `depth_ask_levels_5m` |
| **Depth Quotes / TotalView** | Per-exchange breakdown (NSDQ, MEMX, BATS, EDGX, ARCX, IEX, etc.) | Exchange-specific sizes in rolling windows |
| **Option Chain** | Greeks, IV, probabilities, OI, volume | `net_gamma_5m`, `iv_skew_5m`, `total_delta_5m`, `wall_delta_5m` |

Plus VAMP, depth decay, depth imbalance, and exchange flow metrics already computed.

---

## Five Depth Integration Approaches

### Approach 1: Universal Depth Modifier (UDM)

**Concept:** Add a single depth quality score that every strategy can optionally consume. It's a normalized 0–1 score computed from 4 depth dimensions:

```
depth_quality = 0.30 × depth_imbalance + 0.25 × participant_diversity
              + 0.25 × liquidity_density + 0.20 × spread_quality
```

Each component normalizes to [0, 1]:

| Component | Formula | Normalization |
|-----------|---------|--------------|
| **Depth Imbalance** | `(bid_size - ask_size) / (bid_size + ask_size)` | abs from 0→1 |
| **Participant Diversity** | `avg(bid_participants + ask_participants) / 2` | 0.5→5.0 → [0,1] |
| **Liquidity Density** | `total_depth / rolling_mean_depth` | 0.2→3.0 → [0,1] |
| **Spread Quality** | `1 - (current_spread / rolling_max_spread)` | 0→1 |

**How it modifies confidence:**
- Each strategy adds `depth_quality × depth_weight` to its existing confidence
- `depth_weight` is configurable per strategy (0.0 = ignore depth, 1.0 = depth fully counts)
- Default `depth_weight = 0.20` — depth contributes up to 20% of total confidence

**Pros:**
- Minimal code change — one new rolling key, one new parameter per strategy
- Works with ALL 41 strategies, even ones that don't directly use depth
- Easy to tune — adjust `depth_weight` per strategy without changing signal logic

**Cons:**
- Generic — doesn't capture depth-specific nuances per strategy
- The 4-component formula is a "one size fits most" approach

**Best for:** Strategies where depth is a *confirmation* signal rather than the *driver* (e.g., gamma_wall_bounce, confluence_reversal, gex_divergence)

---

### Approach 2: Depth-Specific Confidence Components (DSCC)

**Concept:** Instead of a universal modifier, add 2-3 depth-specific components to each strategy's existing confidence formula. Each component is a normalized [0, 1] factor that the strategy's `_compute_confidence()` method already knows how to handle.

**Depth components to add:**

| Component | What It Measures | Depth Source | Normalization Range |
|-----------|-----------------|--------------|-------------------|
| **Book Depth Strength** | Total bid+ask size vs. historical | Depth Aggregates | 1000 → 20000 shares |
| **Depth Imbalance Direction** | Does depth agree with signal direction? | Depth Aggregates | -1 → +1 (imbalance ratio) |
| **Exchange Concentration** | Are aggressive flows on one exchange or spread out? | Depth Quotes (TotalView) | 1 → 10 exchanges |
| **Top-Level Quality** | Are the top 3 levels thick or thin? | Depth Aggregates | 50 → 5000 shares per level |
| **Depth Decay Rate** | Is liquidity stable or evaporating? | Depth Aggregates | -0.3 → +0.3 ROC |

**How it works:**
- Each strategy adds 2-3 of these components to its `_compute_confidence()` method
- Components are normalized using the `normalize(val, vmin, vmax)` helper already used
- The confidence formula shifts from "average of 5" to "average of 7" (or 5→8, etc.)

**Example — gamma_wall_bounce with DSCC:**

Current confidence (5 components): wall proximity, wall strength, price position, volume, regime.
With DSCC (7 components): + book depth strength, + depth imbalance direction, + exchange concentration.

```python
# In gamma_wall_bounce._compute_confidence():
# Existing:
c1 = normalize(wall_proximity, 0.0, 2.0)    # wall proximity
c2 = normalize(wall_strength, 0, 5000000)    # wall strength
c3 = normalize(price_position, 0.0, 1.0)    # price position
c4 = normalize(volume_ratio, 0.5, 2.0)      # volume
c5 = regime_bonus                           # regime

# New depth components:
c6 = normalize(book_depth, 1000, 20000)     # ← NEW: total depth
c7 = normalize(exchange_count, 1, 10)       # ← NEW: exchange diversity

confidence = (c1 + c2 + c3 + c4 + c5 + c6 + c7) / 7.0
```

**Pros:**
- Each strategy gets depth-specific confidence that makes sense for its logic
- No new architecture — just extends existing `_compute_confidence()` methods
- Easy to debug — each component is visible in the signal metadata

**Cons:**
- More code changes — 41 strategies × 2-3 components each
- Need to determine the right normalization ranges (can use historical percentiles)

**Best for:** Strategies where depth is a *core driver* of the signal (e.g., depth_imbalance_momentum, depth_decay_momentum, vamp_momentum, exchange_flow_asymmetry)

---

### Approach 3: Dynamic Depth-Adjusted Thresholds (DDAT)

**Concept:** Instead of modifying confidence scores, use depth data to *dynamically adjust the signal thresholds* that trigger a signal in the first place. When depth is strong, lower the confidence threshold; when depth is weak, raise it.

**How it works:**

```python
# Instead of:
if confidence < MIN_CONFIDENCE:
    return []

# Use:
adjusted_threshold = MIN_CONFIDENCE * depth_adjustment_factor
if confidence < adjusted_threshold:
    return []

# Where:
depth_adjustment_factor = 1.0 - (depth_quality - 0.5) * 0.4
# depth_quality = 1.0 → factor = 0.6 (threshold lowered by 40%)
# depth_quality = 0.5 → factor = 1.0 (no change)
# depth_quality = 0.0 → factor = 1.4 (threshold raised by 40%)
```

**Depth-adjusted signal gates:**

| Depth Condition | Effect | Example |
|----------------|--------|---------|
| Strong bid depth + strong participants | Lower confidence threshold, fire more signals | MIN_CONFIDENCE 0.15 → 0.12 |
| Weak depth (thin book) | Raise confidence threshold, fire fewer signals | MIN_CONFIDENCE 0.15 → 0.20 |
| Extreme imbalance (ratio > 8 or < 0.2) | Override threshold entirely — fire regardless | MIN_CONFIDENCE → 0.0 |
| Spread widening + weak depth | Double-gate — require both confidence AND depth | confidence > 0.20 AND depth_quality > 0.5 |

**Pros:**
- Changes signal *behavior* not just scoring — more signals in good conditions, fewer in bad
- No changes to `_compute_confidence()` — only the threshold comparison
- Intuitive: "strong depth = more signals" is easy to explain

**Cons:**
- Less granular than component-based approaches
- Harder to see *which* depth factor caused the adjustment
- Need to calibrate the adjustment ranges carefully

**Best for:** Quick wins before market open — can be implemented with minimal code changes

---

### Approach 4: Depth Confluence Scoring (DCS)

**Concept:** When multiple depth signals agree on direction, boost confidence multiplicatively (not additively). This captures the "conviction multiplier" effect — one depth signal is good, three agreeing depth signals are great.

**Depth signal types that can confluence:**

| Signal Type | Source | Direction |
|------------|--------|-----------|
| **Depth Imbalance** | bid/ask ratio > 1 or < 1 | bid-heavy → LONG, ask-heavy → SHORT |
| **VAMP Bias** | VAMP > mid → LONG, VAMP < mid → SHORT | Volume-adjusted mid-price |
| **Exchange Flow** | MEMX/BATS bid aggression → LONG | Venue-specific flow |
| **Depth Decay** | Ask evaporation → LONG, bid evaporation → SHORT | Liquidity dynamics |
| **Participant Quality** | High participants → conviction | Multi-exchange agreement |

**Confluence scoring:**

```python
# Count how many depth signals agree with the strategy's direction
agreeing_depth_signals = sum(
    1 for depth_signal in [depth_imbalance, vamp_bias, exchange_flow, depth_decay, participant_quality]
    if depth_signal.direction == strategy_direction
)

# Confluence multiplier: 1.0 + 0.08 × agreeing_signals
# 0 agreeing = ×1.0 (no boost)
# 1 agreeing = ×1.08
# 2 agreeing = ×1.16
# 3 agreeing = ×1.24
# 4 agreeing = ×1.32
# 5 agreeing = ×1.40 (maximum boost)

confluence_multiplier = 1.0 + 0.08 * agreeing_depth_signals
adjusted_confidence = min(1.0, confidence * confluence_multiplier)
```

**Confluence tiers:**

| Tier | Agreeing Signals | Multiplier | Effect |
|------|-----------------|-----------|--------|
| **Solo** | 0 | ×1.00 | No depth boost |
| **Supported** | 1 | ×1.08 | Slight boost |
| **Confirmed** | 2 | ×1.16 | Noticeable boost |
| **Confluent** | 3 | ×1.24 | Strong boost |
| **Aligned** | 4 | ×1.32 | Very strong |
| **Harmonic** | 5 | ×1.40 | Maximum depth conviction |

**Pros:**
- Captures the "wisdom of crowds" effect — multiple independent depth signals agreeing
- Multiplicative boost is more impactful than additive at high confluence levels
- Easy to visualize on the heatmap — "Harmonic" signals get a special badge

**Cons:**
- Requires computing all 5 depth signals for every tick (slight performance cost)
- The 0.08 per-signal multiplier is heuristic — needs backtesting to optimize
- Depth signals must be *independent* — if two depth signals are correlated, they over-count

**Best for:** High-conviction filtering — when all depth signals point the same way, we should be very confident

---

### Approach 5: Depth-Weighted Rolling Windows (DWRW)

**Concept:** The rolling windows that feed strategy confidence are currently simple time-weighted averages. Modify them to be *depth-weighted* — periods with stronger depth get higher weight in the rolling calculation.

**How it works:**

```python
# Current: simple rolling average
# rolling_mean = sum(values) / count

# Depth-weighted:
# rolling_mean = sum(values × depth_weight) / sum(depth_weight)

# Where depth_weight for each tick = 1.0 + depth_quality(tick) × weight_multiplier
# weight_multiplier = 0.5 (default) — so depth_quality=1.0 → weight=1.5
#                    depth_quality=0.0 → weight=1.0 (no boost)

# Effect:
# - Strong depth periods contribute more to the rolling average
# - Weak depth periods contribute less
# - The rolling average becomes more responsive to current conditions
```

**Impact on confidence:**

| Scenario | Without DWRW | With DWRW |
|----------|-------------|-----------|
| Strong depth + rising price | Rolling avg lags (old weak data weighs equally) | Rolling avg rises faster (strong data weighs more) |
| Weak depth + falling price | Rolling avg stays flat (old strong data drags it up) | Rolling avg falls faster (weak data weighs less) |
| Depth regime change | Slow to reflect (50/50 old/new) | Fast to reflect (new regime gets proper weight) |

**Implementation:**

```python
# In rolling_window.py, add depth_weighted option:
class RollingWindow:
    def __init__(self, maxlen, depth_weighted=False, depth_key="depth_quality"):
        self.depth_weighted = depth_weighted
        self.depth_key = depth_key

    def add(self, value, depth_quality=1.0):
        if self.depth_weighted:
            weight = 1.0 + depth_quality * 0.5
            self._weighted_sum += value * weight
            self._weight_total += weight
        else:
            self._sum += value
            self._count += 1

    @property
    def mean(self):
        if self.depth_weighted:
            return self._weighted_sum / self._weight_total if self._weight_total > 0 else 0
        return self._sum / self._count if self._count > 0 else 0
```

**Pros:**
- Improves ALL strategies that use rolling windows (most of them)
- No changes to individual strategy confidence formulas
- More responsive to current market conditions
- Captures the idea that "strong depth data is more informative"

**Cons:**
- More subtle effect — harder to see the impact directly
- Requires modifying the RollingWindow class and all strategy references
- The depth_weighted flag needs to be set per-strategy (not all strategies benefit equally)

**Best for:** Strategies that rely heavily on rolling window statistics (gamma_wall_bounce, vol_compression_range, gex_divergence)

---

## Recommended Implementation Plan

### Phase 0: Pre-Market (Next 6.5 hours) — Quick Wins

**Implement Approach 3 (DDAT) + Approach 1 (UDM):**
- Add the universal depth quality score to `main.py` (one function, one rolling key)
- Add depth-adjusted thresholds to the top 10 strategies by signal volume
- These require minimal code changes and give immediate benefit

**Priority strategies for Phase 0:**
1. `gamma_wall_bounce` — highest signal volume, depth confirmation matters
2. `depth_imbalance_momentum` — already uses depth, confidence can be boosted
3. `gex_divergence` — depth adds direction confirmation
4. `confluence_reversal` — depth walls = stronger confluence
5. `vol_compression_range` — depth density = better compression detection

### Phase 1: Post-Market Day 1 — Full Integration

**Implement Approach 2 (DSCC) for all 41 strategies:**
- Add 2-3 depth components to each strategy's `_compute_confidence()`
- Use historical percentiles for normalization ranges (first day of runtime data)
- Log depth component values in signal metadata for post-market analysis

### Phase 2: Week 1 — Optimization

**Implement Approach 4 (DCS) and Approach 5 (DWRW):**
- Add confluence scoring for high-conviction filtering
- Switch rolling windows to depth-weighted mode
- Backtest all depth parameters against Day 1 data
- Tune the 0.08 confluence multiplier and 0.5 depth weight multiplier

---

## Depth Data Sources Summary

| Source | Fields Used | Strategies That Benefit |
|--------|------------|----------------------|
| **Depth Aggregates** | total_bid_size, total_ask_size, bid_levels[], ask_levels[], num_participants, total_order_count | All 41 (via UDM), 14+ L2 (via DSCC) |
| **Depth Quotes / TotalView** | Per-exchange sizes (NSDQ, MEMX, BATS, EDGX, ARCX, IEX), order_count, timestamp | Exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance |
| **VAMP** | mid_price, vamp_mid_dev, bid_levels[], ask_levels[] | vamp_momentum, depth_imbalance_momentum, depth_decay_momentum |
| **Depth Decay** | bid_decay_roc, ask_decay_roc, depth_vol_ratio | depth_decay_momentum, depth_imbalance_momentum |
| **Exchange Flow** | memx_bias, bats_bias, iex_intent, cross_exchange_agreement | exchange_flow_asymmetry, participant_diversity_conviction |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Depth data is stale or noisy on first day | Medium | Use soft gates (depth boosts confidence but doesn't block signals) |
| Over-counting correlated depth signals | Low | Approach 4's confluence uses independent signal types |
| Performance impact of extra depth calculations | Low | Depth computations are simple arithmetic on already-loaded data |
| Confidence scores shift too much with depth | Medium | Start with conservative depth_weight (0.15-0.20), tune after Day 1 |
| Normalization ranges wrong for first day | Low | Use wide normalization ranges on Day 1, narrow after data accumulates |

---

## Rune's Recommendation

**Start with Approach 1 (UDM) + Approach 3 (DDAT) before market open.**

The universal depth modifier gives every strategy a depth boost with one new rolling key, and the dynamic thresholds ensure we fire more signals when depth is strong and fewer when it's weak. This is the highest-leverage, lowest-risk approach for our current situation.

**Then layer in Approach 2 (DSCC) for the 14+ L2 strategies that already have depth data in their rolling windows.** These strategies can get the most out of depth-specific components because they already compute the underlying metrics.

**Approach 4 (DCS) is the "nice to have"** — it's elegant and will produce some beautiful high-conviction signals, but it requires computing 5 depth signals per tick, which is more work. Save it for Week 1 optimization.

**Approach 5 (DWRW) is the "set and forget"** — once implemented, it improves all rolling-window-based strategies automatically. Good investment for the long term.

---

*Rune 🐉 — 2026-05-13*
