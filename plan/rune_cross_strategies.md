# Cross-Strategy Designs — Rune 🐉

**Date:** 2026-05-21  
**Based on:** `analyzed_20260520.md` — Round 3 Validation (392,508 signals, 12 strategies)  
**Focus:** Statistical Edge Anomalies, Temporal Burst Events, Microstructure Event Clusters

---

## TL;DR — The Core Insight

The data reveals **three distinct market regimes** that the current single-strategy approach treats independently:

1. **Gamma Wall Regime** — price reacts to structural walls (300.0, 114.0, 425.0) with 50-66% win rates
2. **Burst Regime** — 7-9 strategies fire within 10s windows, indicating multi-factor events (3,738 total bursts)
3. **Anomaly Regime** — specific confidence buckets where strategies dramatically outperform (18 alpha anomalies detected)

The problem: **CONFLUENCE and other strategies operate in isolation**, missing the cross-signal opportunities that arise when these regimes overlap.

---

## Cross-Strategy Design 1: Wall-Burst Confluence (WBC)

### Concept
When a gamma wall support level (from Phase 3 clusters) coincides with a temporal burst event (Phase 2), the probability of a sustained move increases significantly.

### Data Basis
- **Gamma Wall Support (300.0):** 66.1% WR, $0.1 avg P&L, 2,818 signals, 3 strategies
- **Gamma Wall Support (114.0):** 51.4% WR, $0.2 avg P&L, 760 signals
- **Temporal Bursts:** 3,738 total, top bursts show 7-9 strategies firing within 10s
- **Burst triggers often reference walls:** "Call wall at 225.0 rejected", "Put wall at 412.5 supported"

### Design
```
Signal = gamma_wall_support AND temporal_burst AND velocity_confirmed

Conditions:
  1. Price within 1.5% of a known gamma wall (300.0, 114.0, 225.0, 412.5, 415.0)
  2. ≥4 strategies fire within 10s window (temporal burst detection)
  3. Volume multiplier ≥ 1.05 (velocity gate)
  4. Wall GEX ≥ 500,000 (structural integrity)

Direction:
  - Wall REJECTED (price breaks through) → direction of breakout
  - Wall SUPPORTED (price bounces) → opposite direction
  - Use the burst reason field to determine direction
```

### Expected Edge
- Wall alone: ~50-66% WR
- Wall + burst: estimated 65-78% WR (burst confirms multi-strategy agreement)
- Targets: 1:2 risk/reward, stop past wall

---

## Cross-Strategy Design 2: Anomaly-Stacked Entry (ASE)

### Concept
Exploit the 18 detected statistical anomalies by creating a composite signal that requires multiple anomaly conditions to align simultaneously.

### Data Basis
Key anomalies with highest lift:
| Strategy | Bucket | Strat WR | Global WR | Lift | Sigma |
|----------|--------|----------|-----------|------|-------|
| gamma_flip_breakout | 50-59% | 93.5% | 29.7% | 215% | 2.26σ |
| gex_divergence | 90-99% | 100% | 30.8% | 224% | 2.06σ |
| magnet_accelerate | 80-89% | 44.8% | 11.1% | 302% | 1.86σ |
| gex_divergence | 80-89% | 43.6% | 11.1% | 291% | 1.80σ |

### Design
```
Signal = anomaly_stack_score ≥ threshold

Anomaly Stack Components (each contributes 0-1):
  1. gamma_flip_breakout in 50-59% bucket (high weight: 2.26σ)
  2. gex_divergence in 80-89% bucket (1.80σ)
  3. magnet_accelerate in 80-89% bucket (1.86σ)
  4. gamma_flip_breakout in 40-49% bucket (1.20σ, 92.9% WR)
  5. gamma_squeeze in 40-49% bucket (1.39σ, 100% WR)

Stack Score = weighted_sum(anomaly_signals) / sum(weights)

Entry when:
  - Stack Score ≥ 0.6 (at least 2 strong anomalies aligned)
  - Price in positive gamma regime (range-bound friendly)
  - Volume supports (vol_mult ≥ 1.05)

Direction:
  - gamma_flip_breakout signals → follow breakout direction
  - gex_divergence signals → divergence direction (bullish when price falls but GEX rises)
  - magnet_accelerate signals → magnet pull direction
```

### Expected Edge
- Single anomaly: 30-45% WR (vs 11-30% global)
- Stacked (≥2 anomalies): estimated 55-70% WR
- Best in positive gamma regime (where most anomalies are detected)

---

## Cross-Strategy Design 3: Multi-Wall Hierarchy (MWH)

### Concept
Instead of treating all gamma walls equally, create a hierarchy based on wall GEX, distance from price, and historical win rate. Trade the "strongest wall" on each side.

### Data Basis
- 9 event clusters, 7 are Gamma Wall Support variants
- Wall strikes: 300.0 (66.1% WR), 114.0 (51.4%), 425.0 (30.9%), 225.0 (27.1%)
- Wall GEX ranges from 22 to 18,518,620
- Stronger walls (higher GEX) correlate with higher win rates

### Design
```
Wall Hierarchy Score:
  wall_score = log(GEX) * wall_type_weight * proximity_factor

Wall Types:
  - Call Wall (resistance): weight = 1.0
  - Put Wall (support): weight = 1.1 (puts tend to be stickier)
  - Flip Zone: weight = 0.9

Proximity Factor:
  - Within 0.5%: 1.5
  - Within 1.0%: 1.2
  - Within 1.5%: 1.0
  - Within 2.0%: 0.8

Entry:
  - Find strongest wall on each side (resistance/support)
  - If wall_score > threshold AND velocity confirmed → trade
  - Strongest wall gets priority (score 3 confluence)
  - Second strongest acts as secondary target

Exit:
  - Target = next wall in hierarchy (not fixed 2× risk)
  - Stop = past the traded wall (regime-adaptive)
```

### Expected Edge
- Captures the full wall spectrum, not just the nearest
- Higher GEX walls have proven higher win rates
- Dynamic targets based on wall hierarchy

---

## Cross-Strategy Design 4: Regime-Switching Ensemble (RSE)

### Concept
Create a meta-strategy that selects the best individual strategy based on the current market regime, rather than running all strategies in parallel.

### Data Basis
- **Positive Gamma (Range-Bound):** 68,996 signals, strategies perform best here
  - gamma_wall_bounce: 33.0% WR (sideways), 25.1% (trending)
  - gamma_flip_breakout: 76.7% WR (positive gamma)
  - vol_compression_range: 42.2% WR (positive gamma)
  
- **Negative Gamma (Volatile/Breakout):** 16 signals (small sample but important)
  - depth_decay_momentum: 0% WR (small sample)
  - gamma_flip_breakout: still profitable

- **Key regime-dependent anomalies:**
  - magnet_accelerate anomaly (80-89%) is strongest in positive gamma
  - gamma_flip_breakout 50-59% bucket (93.5% WR) is in positive gamma

### Design
```
Regime Detection:
  - Positive Gamma: net_gamma > 0, price range-bound (low ATR)
  - Negative Gamma: net_gamma < 0, price volatile (high ATR)
  - Transition: net_gamma near zero, increasing volatility

Strategy Selection Matrix:

  Positive Gamma (Range-Bound):
    Primary: gamma_flip_breakout (76.7% WR, $0.4 P&L)
    Secondary: gamma_wall_bounce (33.0% WR in sideways)
    Tertiary: vol_compression_range (42.2% WR)

  Negative Gamma (Volatile):
    Primary: gamma_flip_breakout (still strong)
    Secondary: depth_decay_momentum (needs tuning)
    Tertiary: gex_divergence (51.1% WR, works in both)

  Transition (Gamma Flip):
    Primary: gex_divergence (51.1% WR, designed for this)
    Secondary: gamma_flip_breakout (by definition)

Confidence Boost:
  - When ensemble agrees (≥2 strategies signal same direction): +0.15 confidence
  - When regime matches strategy's optimal regime: +0.10 confidence
```

### Expected Edge
- Avoids wasting signals in wrong regime
- Ensemble agreement acts as a quality filter
- Captures the gamma flip transition events (high-value, low-frequency)

---

## Cross-Strategy Design 5: Velocity-Depth Cascade (VDC)

### Concept
A two-stage filter that first checks for velocity (price momentum toward a level), then confirms with depth absorption (order book support). This is essentially a refined CONFLUENCE but with cascading (not AND) gates.

### Data Basis
- CONFLUENCE has TWO hard gates (velocity AND absorption), both can reject independently
- Current params: velocity z-score ≥ 1.0, volume mult ≥ 1.05, depth spike ≥ 1.2
- The v4.001 loosening: velocity_min_volume_mult 1.2→1.05, depth_spike 1.5→1.2

### Design
```
Stage 1 — Velocity Gate (soft):
  - Calculate z-score of price vs rolling mean
  - If |z-score| ≥ 0.5: velocity_score = |z-score| / 3.0 (0.17-1.0)
  - If |z-score| < 0.5: velocity_score = 0.17 (minimum, not rejected)
  - Volume multiplier: if ≥ 1.05 → pass, else velocity_score *= 0.5

Stage 2 — Depth Gate (soft):
  - Calculate spike ratio (current depth / rolling avg depth)
  - If spike ≥ 1.2: absorption_score = min(1.0, spike / 3.0)
  - If 0.8 ≤ spike < 1.2: absorption_score = spike / 1.2 * 0.5
  - If spike < 0.8: absorption_score = 0.15 (minimum, not rejected)

Final Confidence:
  - confidence = (base_score + wall_integrity + velocity_score + absorption_score) / 4
  - If velocity_score < 0.17 AND absorption_score < 0.15: reject (both failed)
  - If only one failed: reduce confidence by 0.15 (not full rejection)

Key Difference from Current CONFLUENCE:
  - Current: BOTH gates must pass (hard AND) → many signals rejected
  - VDC: Gates are soft cascading → partial credit for partial signals
```

### Expected Edge
- More signals pass through (reduced false negatives)
- Signals with partial velocity/depth still get appropriate confidence
- Estimated 20-30% more signals with similar or better win rates

---

## Cross-Strategy Design 6: Burst-Cluster Fusion (BCF)

### Concept
Merge temporal burst detection (Phase 2) with microstructure event clustering (Phase 3). When a burst event occurs AND the participating strategies share a common microstructure fingerprint, the signal quality is significantly enhanced.

### Data Basis
- 3,738 temporal bursts detected (10s window)
- 9 event clusters with shared metadata fingerprints
- Top clusters have coincidence scores of 3-4 (3-4 strategies on same microstructure)
- Burst reasons reference specific events: "Call wall at 225.0 rejected", "Flow imbalance LONG"

### Design
```
Burst Detection:
  - Track strategy signals in 10s rolling windows
  - A "burst" = ≥3 strategies firing in the same window

Cluster Confirmation:
  - For each burst, check if participating strategies share a common:
    a) wall_strike (gamma wall support cluster)
    b) net_gamma level (gamma exposure cluster)
    c) iex_intent value (exchange sweep cluster)
  - If shared fingerprint found → cluster confirmation

Signal Strength:
  - Burst only: base confidence
  - Burst + cluster: +0.20 confidence
  - Burst + cluster + velocity: +0.30 confidence
  - Burst + cluster + velocity + regime match: +0.40 confidence

Direction Determination:
  - From burst reason field (e.g., "Breakout LONG below flip zone")
  - From cluster type (wall support = bounce, wall rejection = break)
  - From individual strategy directions (majority vote)
```

### Expected Edge
- Filters out coincidental bursts (strategies firing randomly)
- Cluster confirmation adds structural evidence
- Estimated 60-75% WR for burst+cluster signals (vs ~33% overall)

---

## Priority Ranking

| Rank | Design | Complexity | Expected Edge | Data Support | Implementation Effort |
|------|--------|-----------|---------------|-------------|---------------------|
| 1 | Velocity-Depth Cascade (VDC) | Low | +20% more signals | Direct CONFLUENCE fix | 1-2 days |
| 2 | Wall-Burst Confluence (WBC) | Medium | 65-78% WR | Strong (3,738 bursts, 7 wall clusters) | 2-3 days |
| 3 | Anomaly-Stacked Entry (ASE) | Medium | 55-70% WR | 18 alpha anomalies mapped | 2-3 days |
| 4 | Burst-Cluster Fusion (BCF) | Medium | 60-75% WR | Bursts + clusters already computed | 2-3 days |
| 5 | Multi-Wall Hierarchy (MWH) | Low | Better targets | Wall GEX data available | 1-2 days |
| 6 | Regime-Switching Ensemble (RSE) | High | Regime-optimized | Regime labels in data | 3-5 days |

---

## Recommended Implementation Order

1. **VDC** — Quick win, fixes the most obvious CONFLUENCE bottleneck (hard AND gates)
2. **WBC** — Leverages the rich burst and cluster data already computed
3. **ASE** — Builds on anomaly detection for high-confidence signals
4. **BCF** — Combines bursts and clusters for the strongest signals
5. **MWH** — Refines wall trading with hierarchy
6. **RSE** — Full ensemble with regime switching (most complex, highest potential)

---

## Notes on Current CONFLUENCE

The v4.001 loosening (0.003→0.015, 1.2→1.05, 1.5→1.2) helps but doesn't fully address the root causes:

1. **Hard AND gates** — velocity AND absorption both must pass. Making them soft (VDC) would let partial signals through with reduced confidence.
2. **Structural signal counting** — only wall, flip, VWAP count as structural. Rolling extremes (max/min) are technical only. Consider giving rolling extremes partial credit.
3. **Confidence averaging** — the 4-component average means one weak component drags down the whole signal. Weighted average (giving more weight to wall integrity and velocity) would help.
4. **Wall proximity** — 1.5% is reasonable but the data shows walls at 225.0, 300.0, 412.5, 415.0, 425.0, 114.0, 120.0 have different characteristics. A distance-weighted approach would be better.
