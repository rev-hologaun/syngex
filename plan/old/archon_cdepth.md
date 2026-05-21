# Market Depth → Confidence Integration — Archon's Ideas

**Author:** Archon 🕸️
**Date:** 2026-05-13
**Context:** v2.09, 41 strategies, 0 runtime data. Market opens in ~6.5h. Need depth-driven confidence upgrades.

---

## Guiding Principle

Depth data should not just create *new* strategies — it should make *all* strategies smarter. The highest-leverage approach is a **modular depth-confidence layer** that any strategy can tap into, plus a few depth-native strategies for pure microstructure signals.

---

## Idea 1: Depth Quality Score (DQS) — Universal Confidence Multiplier

**Concept:** A single scalar (0.0–1.0) that measures "how reliable is the current order book for making a directional bet." Every strategy reads this score and uses it to scale its confidence.

**Why:** A signal generated when the book is thin, one-sided, and single-participant is inherently less trustworthy than one generated when the book is deep, diverse, and balanced. DQS captures this.

### Components (5 sub-scores, each 0–1, averaged):

| Sub-Score | Formula | What It Captures |
|-----------|---------|-----------------|
| **Liquidity Depth** | `min(top5_bid_size, top5_ask_size) / baseline` | Is there enough book to trust? Thin books = fake signals. |
| **Book Balance** | `1 - |bid_size - ask_size| / (bid_size + ask_size)` | Extreme imbalance can be genuine conviction OR spoofing. Moderate balance = higher DQS (we trust balanced books more). |
| **Participant Diversity** | `avg(num_participants, top_10_levels)` | Multi-participant walls = institutional. Single participant = likely spoof. |
| **Exchange Spread** | `1 - spread_bps / max_spread_bps` | Wide spreads = stress or illiquidity. Narrow spreads = healthy market. |
| **Depth Stability** | `1 - |depth_ROC_30s|` | Rapidly changing depth = unstable. Stable depth = reliable. |

### Integration Pattern

```python
# In any strategy's confidence computation:
dqs = data.get("dqs", 0.5)  # Default 0.5 when no depth data

# Scale the strategy's computed confidence by DQS
raw_confidence = self._compute_raw_confidence(...)
depth_adjusted = raw_confidence * (0.5 + 0.5 * dqs)  # Maps: DQS=0→0.5×, DQS=1→1.0×
```

**Impact:** When depth is poor, confidence gets halved. When depth is excellent, confidence is untouched. This automatically suppresses false signals during illiquid/stressed conditions without changing any strategy logic.

### Baseline Calibration

`baseline` for liquidity depth should be computed from the first 30 minutes of depth data (market open) — a rolling 30m average of `top5_bid_size + top5_ask_size`.

---

## Idea 2: Depth-Confirmed Confluence — For Gamma/Options Strategies

**Concept:** Strategies that already use options data (strike_concentration, theta_burn, gamma_volume_convergence, iv_band_breakout, etc.) get a **depth confirmation bonus** when order book data aligns with their options-based signal.

**Why:** A gamma wall at $480 is one data point. A gamma wall at $480 *with* a bid liquidity wall at $479.50 and multi-participant depth at that level = much stronger signal.

### Confluence Matrix

| Options Signal | Depth Confirmation | Confidence Bonus |
|----------------|-------------------|-----------------|
| Gamma call wall (support) | Bid wall within $0.50 | +0.08 |
| Gamma call wall (support) | Bid wall within $0.20 + 3+ participants | +0.12 |
| Gamma put wall (resistance) | Ask wall within $0.50 | +0.08 |
| Gamma put wall (resistance) | Ask wall within $0.20 + 3+ participants | +0.12 |
| IV skew (fear) + bid depth dominance | Depth imbalance > 0.3 | +0.06 |
| IV skew (greed) + ask depth dominance | Depth imbalance < -0.3 | +0.06 |
| No confluence | — | +0.00 (baseline) |

### Implementation

Each options-based strategy gets a new confidence component:

```python
def _depth_confluence_bonus(self, signal_direction, rolling_data, depth_snapshot):
    """Additional confidence when depth confirms options-based signal."""
    gamma_walls = rolling_data.get("gamma_walls", {})
    depth_agg = depth_snapshot or {}
    
    # Find nearest depth wall to gamma wall
    nearest_depth = self._find_nearest_depth_wall(gamma_walls, depth_agg)
    
    if nearest_depth and nearest_depth.proximity < 0.50:
        if nearest_depth.participants >= 3:
            return 0.12
        return 0.08
    return 0.0
```

**Impact:** Strategies like `strike_concentration` and `theta_bounce` (which already compute gamma-based confidence) get a meaningful confidence bump when depth confirms. This is the highest-ROI integration because it leverages existing strategy logic with a single new component.

---

## Idea 3: Depth Regime Classification — Context-Aware Confidence

**Concept:** Classify the current market microstructure into one of 4 depth regimes, then adjust confidence thresholds per regime. Different regimes require different confidence levels for the same signal.

### Regimes

| Regime | Characteristics | Confidence Adjustment |
|--------|----------------|----------------------|
| **Normal** | Balanced book, moderate depth, narrow spread | Baseline — no change |
| **Trending** | Depth evaporating in one direction, deep on the other | +0.05 bonus (trend is confirmed by depth) |
| **Stressed** | Wide spread, thin book, high depth volatility | -0.10 penalty (higher bar for signals) |
| **Spoofed** | Extreme imbalance, single-participant walls, rapid depth changes | -0.15 penalty (likely fake signal) |

### Detection Logic

```python
def classify_depth_regime(depth_data):
    spread_bps = depth_data["spread_bps"]
    depth_volatility = depth_data["depth_roc_std"]
    imbalance = depth_data["imbalance_ratio"]
    participant_ratio = depth_data["single_participant_levels"] / total_levels
    
    if spread_bps > 15 or depth_volatility > 0.3:
        return "stressed"
    elif participant_ratio > 0.6 and abs(imbalance) > 0.7:
        return "spoofed"
    elif abs(imbalance) > 0.4 and depth_data["evap_direction"]:
        return "trending"
    else:
        return "normal"
```

### Per-Strategy Threshold Adjustment

```yaml
# In strategies.yaml, each strategy gets regime-aware thresholds:
strike_concentration:
  min_confidence:
    normal: 0.35
    trending: 0.30    # Lower threshold in trending (depth confirms)
    stressed: 0.45    # Higher threshold in stressed (suppress noise)
    spoofed: 0.50     # Highest threshold in spoofed (avoid traps)
```

**Impact:** This is subtle but powerful. The same raw signal strength gets different confidence scores depending on the market context. A signal during a trending regime is more trustworthy than the same signal during a spoofed regime.

---

## Idea 4: Depth-Flow Divergence — The "Fake-Out Detector"

**Concept:** Compare the direction implied by depth (order book) against the direction implied by flow (trades/volume). When they diverge, it's a powerful signal — but the confidence depends on *which* side is diverging.

### Logic

| Depth Signal | Flow Signal | Interpretation | Confidence |
|-------------|-------------|----------------|------------|
| Bid-heavy | Selling pressure | Buyers absorbing sells → **LONG** | +0.10 (strong) |
| Ask-heavy | Buying pressure | Sellers absorbing buys → **SHORT** | +0.10 (strong) |
| Bid-heavy | Buying pressure | Both agree → **LONG** | +0.05 (moderate, already known) |
| Ask-heavy | Selling pressure | Both agree → **SHORT** | +0.05 (moderate, already known) |

### Why Divergence > Agreement

When depth and flow agree, the signal is already priced in. When depth says "buyers are here" but flow says "people are selling," it means passive buyers are absorbing aggressive sellers — a classic accumulation pattern. This is where the alpha lives.

### Implementation

```python
def compute_divergence_signal(depth_data, flow_data):
    depth_bias = depth_data["imbalance_ratio"]  # +1 = bid heavy, -1 = ask heavy
    flow_bias = flow_data["aggressive_buy_ratio"]  # +1 = buying, -1 = selling
    
    # Divergence = opposite signs
    divergence = -depth_bias * flow_bias  # Positive = divergence
    
    if divergence > 0.3:
        if depth_bias > 0:  # Bid-heavy, selling flow → absorption → LONG
            return "LONG", 0.10
        else:  # Ask-heavy, buying flow → absorption → SHORT
            return "SHORT", 0.10
    return None, 0.0
```

**Impact:** This is the most "alpha-generating" depth integration. It's not just confirming existing signals — it's generating *new* signal types that don't exist without depth data.

---

## Idea 5: Per-Strategy Depth Key Mapping

**Concept:** Not all strategies need all depth metrics. Map each strategy to the specific depth keys it should read, avoiding over-engineering.

### Mapping

| Strategy Group | Depth Keys to Read | Rationale |
|---------------|-------------------|-----------|
| **Gamma/Mean Reversion** (strike_concentration, theta_burn, gamma_volume_convergence) | Depth walls, participant counts, confluence proximity | Need to confirm gamma walls with liquidity walls |
| **Momentum** (iv_band_breakout, extrinsic_intrinsic_flow) | Depth decay, imbalance ROC, VAMP deviation | Need to confirm momentum with depth evaporation |
| **Volume/Flow** (prob_distribution_shift, prob_weighted_magnet) | Divergence signals, flow bias, volume/depth ratio | Need to cross-validate volume with order book |
| **IV-Based** (delta_iv_divergence, iv_gex_divergence, iv_skew_squeeze) | Depth imbalance, IV-depth confluence | Options sentiment confirmed by stock flow |
| **Pure Depth** (depth_imbalance, depth_decay, order_book_stacking, vamp_momentum) | All available depth keys | These *are* depth strategies |

### Implementation

Each strategy's `evaluate()` method reads only the keys it needs from `data["rolling_data"]`:

```python
# In strike_concentration.evaluate():
depth_walls = rolling_data.get(KEY_DEPTH_WALLS)  # Only reads what it needs
dqs = rolling_data.get("dqs", 0.5)  # Universal quality score

# In vamp_momentum.evaluate():
# Reads: all depth agg keys, VAMP-specific calculations
# This strategy is the "pure depth" implementation
```

**Impact:** Keeps the system modular. New depth strategies only need to declare which keys they consume. No global refactoring required.

---

## Recommended Rollout Order

Given the 6.5-hour deadline and 0 runtime data:

### Phase 1: Universal Layer (Deploy First)
1. **DQS (Idea 1)** — Single scalar, affects all strategies, minimal code change
2. **Depth Regime (Idea 3)** — Regime classification + threshold adjustment
3. **Depth Flow Divergence (Idea 4)** — New signal types, high alpha potential

These three require minimal new infrastructure. DQS and regime classification can be computed once in `main.py` and read by all strategies.

### Phase 2: Options-Depth Confluence (Deploy Second)
4. **Confluence Bonus (Idea 2)** — Add to existing options strategies, leverages gamma infrastructure already in place

### Phase 3: Pure Depth Strategies (Deploy Last / Next Cycle)
5. **Existing depth strategies** (depth_imbalance, depth_decay, order_book_stacking, vamp_momentum) — These are already designed, just need the depth streaming stubs fixed

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Depth streams are no-op stubs | Fix `tradestation_client.py` depth subscriptions first (designed, ~200 lines) |
| DQS baseline calibration needs warm-up | Default DQS=0.5 for first 30m, then switch to calibrated values |
| Too many depth components → overfitting | Start with DQS (5 sub-scores) only; add confluence and divergence after validation |
| Regime classification wrong in edge cases | Conservative defaults; regime penalties are symmetric (both up and down) |
| Divergence signal noisy in first sessions | Start with high threshold (0.3), lower after seeing data |

---

## Files to Modify (Consolidated)

| File | Changes |
|------|---------|
| `ingestor/tradestation_client.py` | Fix depth streaming stubs (design exists in `depth_stream_design.md`) |
| `main.py` | Compute DQS, regime classification, divergence signals; push to rolling_data |
| `strategies/rolling_keys.py` | Add `dqs`, `depth_regime`, `divergence_signal` keys |
| `strategies/layer3/*.py` (options strategies) | Add `_depth_confluence_bonus()` method |
| `config/strategies.yaml` | Add regime-aware `min_confidence` thresholds |
| `config/heatmap.yaml` | Add DQS and regime indicators to dashboard |

---

## Summary

| Idea | Leverage | Complexity | Alpha Potential |
|------|----------|-----------|-----------------|
| **DQS** | All 41 strategies | Low (compute once, read everywhere) | Medium (suppresses bad signals) |
| **Confluence** | ~10 options strategies | Low-Medium (add 1 component) | High (dual-confirmation) |
| **Regime** | All 41 strategies | Medium (classification logic) | Medium (context-aware thresholds) |
| **Divergence** | All strategies | Medium (flow+depth cross-compare) | **Very High** (new signal types) |
| **Per-strategy mapping** | Architecture enabler | Low (documentation + key declarations) | N/A (enables the rest) |

**My recommendation:** Start with DQS + Confluence. These are the highest-ROI, lowest-risk integrations. Divergence and Regime are powerful but need validation data before fine-tuning thresholds.

🕸️
