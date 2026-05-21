# Forge: Market Depth Integration for Confidence Calculations

**Date:** 2026-05-13
**Author:** Forge
**Context:** Syngex v2.09, 41 strategies, 0 runtime data. Market opens in ~6.5h.
**Goal:** Integrate Level 2 / TotalView / BATS depth data from TradeStation into confidence formulae.

---

## Current State Assessment

### What We Already Have

We're not starting from zero. The depth pipeline is fully wired:

1. **Two depth streams** subscribed in `main.py`:
   - `marketdepth/quotes/{symbol}` — per-exchange TotalView (BATS, MEMX, IEX, EDGX, etc.)
   - `marketdepth/aggregates/{symbol}` — aggregated depth per price level with `TotalSize`, `NumParticipants`, `BiggestSize`, `SmallestSize`

2. **Depth rolling windows** already populated in `_on_message`:
   - `KEY_DEPTH_BID_SIZE_5M`, `KEY_DEPTH_ASK_SIZE_5M` — total bid/ask depth
   - `KEY_DEPTH_SPREAD_5M` — current bid-ask spread
   - `KEY_DEPTH_BID_LEVELS_5M`, `KEY_DEPTH_ASK_LEVELS_5M` — number of levels
   - `KEY_MARKET_DEPTH_AGG` — full depth agg snapshot (per-level data)
   - `KEY_VAMP_LEVELS` — volume-weighted mid-price levels

3. **Derived depth metrics** computed in `_on_message`:
   - VSI (Venue Specific Imbalance) for MEMX, BATS, combined
   - IEX intent score (passive venue depth / total depth)
   - Exchange flow asymmetry (ESI) for MEMX and BATS
   - Aggressor VSI (aggressor-side VSI)

4. **Strategies already using depth** (12+):
   - `depth_imbalance_momentum` — IR + ROC + participants + VAMP
   - `depth_decay_momentum` — bid/ask ROC + vol/depth ratio
   - `vamp_momentum` — VAMP deviation + spread + participants
   - `order_book_stacking` — SIS (Stack Intensity Score)
   - `exchange_flow_imbalance` — MEMX/BATS VSI + IEX intent
   - `exchange_flow_asymmetry` — ESI for MEMX/BATS
   - `exchange_flow_concentration` — venue concentration
   - `participant_diversity_conviction` — participant spread across exchanges
   - `participant_divergence_scalper` — fragility + decay velocity
   - `order_book_fragmentation` — order book fragmentation analysis

### The Gap

The existing strategies use depth data for **signal generation** (do we emit a signal?), but the **confidence scores** within those strategies are narrowly scoped — they mostly use 1-3 depth-derived metrics per strategy. We have rich depth data flowing through the pipeline that's underutilized for confidence calibration.

---

## Proposed Depth Confidence Signals

### Signal 1: Depth-to-Trade Volume Ratio (Liquidity Confirmation)

**Concept:** A signal is only as good as the liquidity behind it. If a strategy fires on a depth imbalance but trade volume is thin, the book could be spoofed or easily consumed.

**Computation:**
```
depth_to_volume_ratio = (total_bid_depth + total_ask_depth) / (trade_volume_5m + epsilon)
```

**Interpretation:**
- **High ratio (>50):** Deep book, thin trades → book may be spoofed or passive. Lower confidence.
- **Medium ratio (10-50):** Healthy liquidity relative to activity. Full confidence.
- **Low ratio (<10):** Heavy trading, shallow book → momentum is real but fragile. Moderate confidence.

**Implementation:**
- Add `KEY_DEPTH_TO_VOL_RATIO_5M` rolling window in main.py
- Normalize to 0-1: peak at ~20 (optimal), taper on both sides
- Apply as a **multiplier** (0.7-1.0) to existing confidence, not a component

**Best for:** All strategies, but especially L1 strategies that don't currently use depth (gamma_wall_bounce, gamma_flip_breakout, magnet_accelerate, vol_compression_range).

---

### Signal 2: Spread Compression/Expansion (Volatility Context)

**Concept:** The bid-ask spread is the market's instantaneous volatility indicator. A tightening spread before a signal = dealer positioning for calm (good for range strategies). A widening spread = dealer uncertainty (good for breakout strategies, bad for mean-reversion).

**Computation:**
```
spread_zscore = (current_spread - mean_spread_5m) / std_spread_5m
```

**Interpretation:**
- **Negative z-score (tightening):** Dealers absorbing risk → supports mean-reversion signals (confluence_reversal, vol_compression_range)
- **Near zero (normal):** No additional signal
- **Positive z-score (widening):** Dealers stepping back → supports breakout signals (gamma_flip_breakout, gamma_squeeze)

**Implementation:**
- Add `KEY_SPREAD_ZSCORE_5M` rolling window (already partially computed in vortex_compression_breakout)
- Directional confidence boost: +0.05-0.10 for spread-aligned signals
- Directional confidence penalty: -0.10 for spread-misaligned signals

**Best for:** L1 mean-reversion strategies and breakout strategies.

---

### Signal 3: Participant Concentration / Spoofing Detection

**Concept:** If 80%+ of bid depth comes from a single exchange or participant, the depth wall is likely a spoof (single entity, easily pulled). Genuine structural support has broad participation.

**Computation:**
```
bid_concentration = max(exchange_bid_sizes.values()) / total_bid_depth
ask_concentration = max(exchange_ask_sizes.values()) / total_ask_depth
spoof_risk = max(bid_concentration, ask_concentration)
```

**Interpretation:**
- **Low concentration (<30%):** Broad participation → high confidence
- **Medium concentration (30-60%):** Some concentration → normal confidence
- **High concentration (>60%):** Single-player wall → reduce confidence by 0.15-0.25

**Implementation:**
- Already have `self._exchange_bid_sizes` and `self._exchange_ask_sizes` populated in `_on_message`
- Add `KEY_PARTICIPANT_CONCENTRATION_5M` rolling window
- Apply as a **penalty** to confidence when concentration is high

**Best for:** All strategies, especially order_book_stacking (already does this partially) and depth_imbalance_momentum.

---

### Signal 4: Depth Slope / Wall Gradient

**Concept:** The shape of the depth curve reveals conviction. A steep gradient (small orders near mid, large orders far away) = weak support. A flat gradient (large orders consistently across levels) = strong conviction.

**Computation:**
```
# From KEY_MARKET_DEPTH_AGG snapshot
bid_gradient = slope(linear_regression(depth_values, price_distances_from_mid))
# Positive gradient = depth increases as you move away from mid (weak)
# Negative gradient = depth increases as you approach mid (strong support)
```

**Interpretation:**
- **Negative gradient:** Depth concentrated near mid → strong support/resistance
- **Near zero:** Uniform depth → neutral
- **Positive gradient:** Depth concentrated far from mid → weak support

**Implementation:**
- Compute in `_on_message` from `KEY_MARKET_DEPTH_AGG` snapshot
- Add `KEY_DEPTH_GRADIENT_BID_5M` and `KEY_DEPTH_GRADIENT_ASK_5M`
- Apply as a confidence component (0.0-0.10) for strategies that use depth

**Best for:** depth_decay_momentum, order_book_stacking, and any strategy that references wall proximity.

---

### Signal 5: Exchange-Specific Depth Imbalance (Venue Signature)

**Concept:** Different exchanges have different behaviors. MEMX and BATS are aggressive execution venues (HFTs sweep here). IEX has a speed bump (passive, intent-driven). EDGX is a mix. The **direction** of imbalance on each venue tells a different story:
- **BATS/MEMX bid-heavy:** Aggressive buyers stepping up → real momentum
- **IEX bid-heavy:** Passive accumulation → slower, more sustainable
- **Cross-venue alignment (all venues bid-heavy):** Strong conviction
- **Cross-venue divergence (BATS bid-heavy, IEX ask-heavy):** Conflict → lower confidence

**Computation:**
```
# Already partially computed as VSI per venue
bats_vsi = bats_bid / bats_ask
iex_vsi = iex_bid / iex_ask
memx_vsi = memx_bid / memx_ask

# Cross-venue alignment score
alignment = 1.0 - std([bats_vsi, memx_vsi, iex_vsi]) / mean([bats_vsi, memx_vsi, iex_vsi])
```

**Interpretation:**
- **High alignment (>0.8):** All venues agree → boost confidence +0.10
- **Medium alignment (0.5-0.8):** Partial agreement → neutral
- **Low alignment (<0.5):** Venues disagree → reduce confidence -0.10

**Implementation:**
- Already have per-venue VSI computed in `_on_message`
- Add `KEY_VENUE_ALIGNMENT_5M` rolling window
- Apply as confidence modifier

**Best for:** exchange_flow_imbalance, exchange_flow_asymmetry, exchange_flow_concentration, and any L2 strategy.

---

### Signal 6: Depth Imbalance ROC Acceleration

**Concept:** The rate of change of the rate of change. If depth imbalance is not just increasing but *accelerating*, the conviction is higher than a linear increase.

**Computation:**
```
imbalance = bid_depth / ask_depth  # or ask/bid for SHORT
imbalance_roc = (imbalance_t - imbalance_t-n) / imbalance_t-n
imb_accel = (imbalance_roc_t - imbalance_roc_t-n) / imbalance_roc_t-n
```

**Interpretation:**
- **Positive acceleration:** Momentum building → boost confidence
- **Negative acceleration:** Momentum fading → reduce confidence
- **Near zero:** Steady state → neutral

**Implementation:**
- `KEY_IR_ROC_5M` already exists in depth_imbalance_momentum
- Compute acceleration in `_on_message` or in-strategy
- Add `KEY_IR_ROC_ROC_5M` rolling window
- Apply as confidence component (0.0-0.10)

**Best for:** depth_imbalance_momentum, depth_decay_momentum, vamp_momentum.

---

## Implementation Strategy

### Phase 1: Rolling Window Additions (main.py)

Add these new rolling windows in `_on_message` (depth data section):

```python
# New rolling windows to add:
KEY_DEPTH_TO_VOL_RATIO_5M        # total_depth / trade_volume
KEY_SPREAD_ZSCORE_5M             # (spread - mean) / std
KEY_PARTICIPANT_CONCENTRATION_5M # max_exchange / total
KEY_DEPTH_GRADIENT_BID_5M        # slope of bid depth curve
KEY_DEPTH_GRADIENT_ASK_5M        # slope of ask depth curve
KEY_VENUE_ALIGNMENT_5M           # cross-venue VSI agreement
KEY_IR_ACCEL_5M                  # ROC of imbalance ratio ROC
```

### Phase 2: Confidence Modifier Layer

Rather than rewriting every strategy's `_compute_confidence`, add a **post-computation depth confidence modifier** in the StrategyEngine or as a mixin. This keeps changes minimal:

```python
def apply_depth_modifier(signal: Signal, depth_data: Dict) -> Signal:
    """Apply depth-derived confidence modifiers post-computation."""
    modifier = 0.0

    # Liquidity confirmation
    dv_ratio = depth_data.get("depth_to_vol_ratio", 20.0)
    modifier += _depth_to_vol_confidence(dv_ratio)

    # Spread context
    spread_z = depth_data.get("spread_zscore", 0.0)
    modifier += _spread_context_confidence(signal, spread_z)

    # Spoofing detection
    conc = depth_data.get("participant_concentration", 0.5)
    modifier -= _spoofing_penalty(conc)

    # Venue alignment
    alignment = depth_data.get("venue_alignment", 0.5)
    modifier += _venue_alignment_bonus(alignment)

    signal.confidence = max(0.0, min(1.0, signal.confidence + modifier))
    signal.metadata["depth_modifier"] = round(modifier, 3)
    return signal
```

### Phase 3: Per-Strategy Tuning

After Phase 1-2 are deployed, each strategy's confidence formula gets a depth-derived component. The key insight: **not all strategies benefit equally from depth data.**

| Strategy | Depth Value | Recommended Depth Component |
|---|---|---|
| gamma_wall_bounce (L1) | High (no depth currently) | Depth-to-Volume + Spread Z-Score |
| gamma_flip_breakout (L1) | High (no depth currently) | Depth-to-Volume + Venue Alignment |
| magnet_accelerate (L1) | Medium | Spread Z-Score + Participant Conc. |
| vol_compression_range (L1) | High (no depth currently) | Spread Z-Score + Depth Gradient |
| depth_imbalance_momentum (L2) | Medium (already uses depth) | IR Acceleration + Spoofing |
| depth_decay_momentum (L2) | Medium (already uses depth) | Depth Gradient + Venue Alignment |
| vamp_momentum (L2) | Medium (already uses VAMP) | Depth-to-Volume + IR Acceleration |
| order_book_stacking (L2) | Medium (already uses SIS) | Spoofing + Venue Alignment |
| exchange_flow_imbalance (L2) | Low (already venue-specific) | Venue Alignment only |
| exchange_flow_asymmetry (L2) | Low (already venue-specific) | Venue Alignment only |
| L3 strategies | Variable | Depth-to-Volume as universal modifier |
| full_data strategies | Variable | Depth-to-Volume as universal modifier |

### Phase 4: Validation

Since we have 0 runtime data and market opens in ~6.5h:

1. **Pre-market:** Run the new depth modifiers with `min_confidence` set high (0.50+) to only see extreme signals
2. **Open (9:30-10:30 PT):** Watch for signals that would have been filtered out by depth. Log them.
3. **Mid-day (12:00-14:30 PT):** Verify depth data prevents false signals during the lull (we already know this is a problem zone)
4. **Post-market:** Compare signal confidence distributions with and without depth modifiers

---

## Risk Assessment

### Low Risk
- **Phase 1 (rolling windows):** Purely additive. If computation fails, the new windows just stay empty. No existing strategy behavior changes.
- **Phase 2 (modifier layer):** Applied post-computation. Can be toggled on/off via config. Default to +0.0 modifier (no change) during initial deployment.

### Medium Risk
- **Phase 3 (per-strategy tuning):** Requires parameter adjustments. If depth signals are noisy, they could degrade confidence accuracy. Mitigation: start with conservative modifiers (±0.05) and scale up based on validation.

### High Risk
- **Depth stream instability:** If TotalView/Level 2 streams drop or have latency spikes, depth-derived metrics could be stale. Mitigation: always check `depth_snapshot` timestamp before using depth data; fall back to no-modifier confidence if data is >5s old.

---

## Quick Win: The Universal Depth Modifier

The highest-impact, lowest-effort change is **Signal 1 (Depth-to-Volume Ratio)** as a universal post-computation modifier. It requires:

1. One new rolling window in main.py (~5 lines)
2. One confidence modifier function (~15 lines)
3. One call in the strategy engine post-processing (~3 lines)

This gives all 41 strategies an immediate depth-awareness boost without touching any individual strategy file. The modifier is:

```python
def depth_to_vol_modifier(dv_ratio: float) -> float:
    """Returns confidence modifier: +0.10 at optimal (20), -0.15 at extremes."""
    if dv_ratio < 3.0:
        return -0.15  # Very thin book — likely spoof or illiquid
    elif dv_ratio < 10.0:
        return -0.05  # Shallow — reduce confidence slightly
    elif dv_ratio <= 30.0:
        return +0.10  # Optimal range — boost confidence
    elif dv_ratio <= 60.0:
        return +0.05  # Deep but thin trades — slight boost
    else:
        return -0.05  # Very deep, very thin — likely spoof
```

This single change would affect all 41 strategies and requires zero per-strategy modifications.

---

## Summary

| Signal | Effort | Impact | Risk | Best For |
|---|---|---|---|---|
| Depth-to-Volume Ratio | Low | High | Low | Universal modifier |
| Spread Z-Score | Low | Medium | Low | L1 mean-reversion & breakout |
| Participant Concentration | Low | Medium | Low | Spoofing detection |
| Depth Gradient | Medium | Medium | Low | Wall-proximity strategies |
| Venue Alignment | Low | Medium | Low | L2 venue-specific strategies |
| IR Acceleration | Low | Low-Medium | Low | Momentum strategies |

**Recommendation:** Deploy the Universal Depth Modifier (Signal 1) first as a safety net for all 41 strategies, then iterate on per-strategy depth components based on validation results.
