# Cross-Strategy Designs — Phase 1 Anomaly Exploitation

**Author:** Archon  
**Date:** 2026-05-21  
**Source:** `analysis/analyzed_20260520.md` — Statistical Edge Anomalies, Temporal Bursts, Microstructure Clusters

---

## Data-Driven Insights (The "Why")

### 1. The Inverted Confidence Curve
Global baseline WR by confidence bucket:

| Bucket | Global WR |
|--------|-----------|
| 10-19% | 82.9% |
| 20-29% | 72.6% |
| 30-39% | 59.9% |
| 40-49% | 48.0% |
| 50-59% | 29.7% |
| 60-69% | 41.0% |
| 70-79% | 32.5% |
| 80-89% | 11.1% |
| 90-99% | 30.8% |

**Key insight:** The 80-89% bucket is catastrophically bad (11.1% WR). High confidence ≠ high quality. The curve is inverted in the high-confidence zone, suggesting those signals are overfit or hitting resistance. This is a **contrarian edge** — when many strategies agree at high confidence, the market is likely at a structural ceiling.

### 2. Temporal Burst Patterns
- 3,738 bursts detected in 10-second windows
- Top bursts involve 7-9 strategies firing simultaneously
- Common triggers: **flow imbalances**, **BATS sweeps**, **flip zone breakouts**, **wall rejections**
- Burst events are the market's "multifactor consensus" — when independent strategies agree within 10 seconds, it's a real structural event

### 3. Microstructure Clusters
- **Gamma Wall Support @ 300.0**: 66.1% WR, $0.1 avg P&L — the single best cluster
- **Gamma Exposure**: 54.1% WR (best sub-cluster) — net_gamma spikes are real edges
- **Exchange Sweep**: 0.0% WR — avoid entirely
- Gamma Wall @ 300.0 is the only wall with meaningful edge; others are noise

### 4. Strategy-Specific Anomalies
- `gamma_flip_breakout` dominates: 93.5% WR at 50-59%, 95.6% at 30-39%, 92.9% at 40-49%
- `gex_divergence` peaks at 90-99% (100% WR, n=8) and 50-59% (60% WR, n=1600)
- `magnet_accelerate` shines at 80-89% (44.8% WR, +302% lift) — anomalous in a terrible bucket
- `strike_concentration` at 50-59%: 68.2% WR

---

## Cross-Strategy Designs

### Design 1: FLOW-GAMMA MOMENTUM CONTINUATION

**Concept:** When a temporal burst fires on a flow imbalance (AggVSI spike), the move continues for 10-30 seconds beyond the burst. Capture the continuation, not the initial spike.

**Trigger:**
1. Detect flow imbalance signal (`exchange_flow_imbalance` or `exchange_flow_asymmetry`) with AggVSI > 0.5 or < -0.5
2. Within 10 seconds, at least 3 other strategies fire
3. Direction confirmed by `gamma_flip_breakout` firing in the same direction

**Entry:** Market on the 4th strategy firing (not the first)
**Stop:** 0.5% past entry
**Target:** 1.5× risk (1:3 RR)
**Max Hold:** 30 seconds

**Data Rationale:**
- Temporal bursts average 8 strategies firing within 10 seconds
- Flow imbalance signals show AggVSI of 0.6-1.0 during bursts
- `gamma_flip_breakout` at 50-59% has 93.5% WR — use it as a confirmation filter
- The burst is the ignition; the continuation is the profit

**Edge:** Most strategies fire on the initial spike (too early). By waiting for the 4th strategy confirmation, we enter at the start of the continuation phase.

---

### Design 2: BURST CONFLUENCE SCORER

**Concept:** A meta-strategy that scores every 10-second window based on how many independent strategies fire, what types they are, and their historical performance in similar conditions. Fires only when the composite score exceeds a threshold.

**Scoring System (0-100):**

| Factor | Weight | Score |
|--------|--------|-------|
| # unique strategies firing | 25% | count / 9 × 25 |
| Flow strategies present (imbalance, asymmetry, concentration) | 15% | 15 if any, 0 if none |
| Gamma strategies present (flip, squeeze, wall) | 15% | 15 if any, 0 if none |
| Depth strategies present (decay, imbalance) | 10% | 10 if any, 0 if none |
| Avg confidence of firing strategies | 15% | avg_conf / 100 × 15 |
| Direction alignment (all same direction) | 20% | 20 if unanimous, 10 if split 50/50, 0 if mixed |

**Trigger:** Composite score ≥ 65

**Entry:** Long if majority direction is LONG, SHORT if SHORT
**Stop:** 0.6% past entry
**Target:** 1.5× risk
**Max Hold:** 60 seconds

**Data Rationale:**
- Top bursts have 8-9 strategies firing — high score
- Bursts with flow + gamma + depth = multifactor event = higher continuation probability
- Unanimous direction in bursts correlates with sustained moves

**Edge:** Converts raw burst detection into a quantified, thresholded signal. Filters noise by requiring multiple independent confirmations.

---

### Design 3: GAMMA WALL 300 CONTINUATION

**Concept:** The 300.0 gamma wall has 66.1% WR — 3× better than any other wall. When price approaches this wall and multiple strategies fire, trade the bounce/continuation.

**Trigger:**
1. Price within 0.5% of wall_strike=300.0
2. At least 2 strategies fire in the wall cluster (gamma_squeeze, gamma_wall_bounce, vol_compression_range)
3. Net gamma > 0 (positive gamma regime)

**Entry:** LONG if price approaches from below, SHORT if from above
**Stop:** 0.4% past the wall
**Target:** 1.5× risk
**Max Hold:** 30 minutes

**Data Rationale:**
- Gamma Wall @ 300.0: 66.1% WR, $0.1 avg P&L — best performing cluster
- Only 2,818 signals, so it's a sparse but high-quality signal
- Positive gamma regime preferred (range-bound friendly)

**Edge:** This is a focused, high-signal-to-noise strategy. Instead of trading all walls equally, we concentrate on the one that actually works.

---

### Design 4: INVERTED CURVE CONTRARIAN

**Concept:** Exploit the inverted confidence curve. When strategies fire in the 80-89% bucket (11.1% global WR), the market is at a structural ceiling or floor. Trade the rejection.

**Trigger:**
1. Any strategy fires with confidence in 80-89% bucket
2. Price is at or near a gamma wall or flip zone
3. Volume is above average (confirms the structural level)

**Entry:** CONTRARIAN to the signal direction
- If signal is LONG at resistance → SHORT
- If signal is SHORT at support → LONG

**Stop:** 0.3% past the structural level
**Target:** 0.8× risk (tight, because the level is real — we're just fading the overshoot)
**Max Hold:** 15 minutes

**Data Rationale:**
- 80-89% bucket: 11.1% WR — the worst performing bucket by far
- 95.6% of signals in this bucket are losses
- High confidence = market is at a structural extreme = likely to reject

**Edge:** The confidence metric is misleading in this zone. By trading contrarian, we capture the rejection that the market is signaling.

---

### Design 5: GEX DIVERGENCE CONFIRMATION

**Concept:** `gex_divergence` fires when price moves against gamma exposure (bullish divergence = price falling but GEX rising). Combine with `gamma_flip_breakout` for confirmation.

**Trigger:**
1. `gex_divergence` signals bullish divergence (price falling, GEX rising) or bearish (price rising, GEX falling)
2. `gamma_flip_breakout` fires in the SAME direction within 30 seconds
3. Confidence of `gex_divergence` ≥ 50%

**Entry:** Market on confirmation
**Stop:** 0.5% past entry
**Target:** 2× risk (1:2 RR)
**Max Hold:** 30 minutes

**Data Rationale:**
- `gex_divergence`: 51.1% overall WR, $0.3 avg P&L
- Best at 90-99% (100% WR, n=8) and 50-59% (60% WR, n=1600)
- `gamma_flip_breakout` at 50-59%: 93.5% WR — strong confirmation signal
- Divergence alone is suggestive; breakout confirmation makes it actionable

**Edge:** GEX divergence identifies the setup; gamma flip breakout confirms the timing. Two independent edges aligned = higher probability.

---

### Design 6: STRIKE CONCENTRATION MOMENTUM

**Concept:** When `strike_concentration` fires at 50-59% confidence (68.2% WR), the market is reacting to a specific strike. Ride the momentum for 5-15 minutes.

**Trigger:**
1. `strike_concentration` fires with confidence in 50-59% bucket
2. Volume is above rolling average (confirms institutional activity at the strike)
3. Price is moving in the signal direction

**Entry:** Market on confirmation
**Stop:** 0.4% past entry
**Target:** 1.5× risk
**Max Hold:** 15 minutes

**Data Rationale:**
- `strike_concentration` at 50-59%: 68.2% WR, $0.3 avg P&L
- Best timeframe: Medium (5-15 min) — 61.5% WR, $0.8 avg P&L
- Trade shows are concentrated at specific strikes, creating short-term momentum

**Edge:** Strike-level institutional activity creates predictable short-term price action. The 5-15 minute window captures the momentum without holding through reversals.

---

### Design 7: MULTI-REGIME GAMMA FLIP

**Concept:** `gamma_flip_breakout` has 95.6% WR at 30-39% confidence and 92.9% at 40-49%. Most signals are at higher confidence (50%+) where performance drops. Filter for the sweet spot.

**Trigger:**
1. `gamma_flip_breakout` fires with confidence in 30-49% bucket
2. Price is trending (use `price_30m` trend indicator)
3. NOT in negative gamma regime (performance drops there)

**Entry:** Market on signal
**Stop:** 0.4% past entry
**Target:** 1.5× risk
**Max Hold:** 30 minutes

**Data Rationale:**
- `gamma_flip_breakout` at 30-39%: 95.6% WR, $0.8 avg P&L
- At 50-59%: 93.5% WR, $0.2 — still good but less profitable
- At 80-89%: 38.4% WR — terrible, avoid
- Trending market: 84.2% WR vs Sideways: 71.6%

**Edge:** This is a quality filter, not a new strategy. By restricting to the 30-49% confidence bucket and trending markets, we capture the best-performing signals while avoiding the noise at high confidence.

---

### Design 8: FLOW SWEEP MOMENTUM

**Concept:** BATS sweeps (ESI < -0.5) and flow imbalances (AggVSI > 0.5) are the most common burst triggers. Trade the sweep continuation.

**Trigger:**
1. `exchange_flow_imbalance` or `exchange_flow_asymmetry` fires with AggVSI > 0.5 or ESI < -0.5
2. Direction: LONG if AggVSI positive, SHORT if ESI negative
3. Within 10 seconds, `gamma_flip_breakout` or `gamma_squeeze` fires in same direction

**Entry:** Market on confirmation
**Stop:** 0.5% past entry
**Target:** 1.5× risk
**Max Hold:** 20 seconds (very short — sweeps are fast events)

**Data Rationale:**
- Top burst triggers: "Flow imbalance LONG: AggVSI=0.760 (+76.0%)" and "BATS sweep SHORT: ESI=-0.813"
- These are the most common burst catalysts
- `gamma_flip_breakout` at 40-49%: 92.9% WR — good confirmation
- Swaps are fast — 10-second windows are appropriate

**Edge:** Flow sweeps are the market's "explosive" events. Combining the sweep signal with gamma confirmation captures the high-momentum continuation phase.

---

### Design 9: REGIME-ADAPTIVE CROSS-FILTER

**Concept:** All strategies perform differently in positive vs negative gamma regimes. This meta-strategy adapts the entry criteria based on the current regime.

**Regime Rules:**

| Regime | Preferred Strategies | Avoid | Stop Size |
|--------|---------------------|-------|-----------|
| Positive Gamma | gamma_wall_bounce, gamma_flip_breakout, vol_compression_range | exchange_flow_asymmetry | Tight (0.4%) |
| Negative Gamma | gamma_flip_breakout, gex_divergence | gamma_wall_bounce, exchange_flow_imbalance | Wide (0.8%) |

**Trigger:**
1. Current regime detected (positive or negative gamma)
2. Strategy fires in the "preferred" list for that regime
3. At least one confirming strategy from a different layer

**Entry:** Market on confirmation
**Stop:** Regime-adaptive (see table)
**Target:** 1.5-2× risk
**Max Hold:** Regime-dependent

**Data Rationale:**
- `gamma_wall_bounce` in negative gamma: 0.0% WR (16 signals, 0 wins)
- `gamma_flip_breakout` in positive gamma: 76.7% WR (all signals)
- `exchange_flow_asymmetry`: 5.0% WR overall — terrible in all regimes
- Different strategies work in different regimes — the cross-filter maximizes edge

**Edge:** Most strategies don't account for regime. By explicitly filtering which strategies to trust based on the current gamma regime, we dramatically reduce false signals.

---

## Summary

| Design | Name | Core Edge | Expected WR |
|--------|------|-----------|-------------|
| 1 | Flow-Gamma Momentum Continuation | Burst continuation after flow spike | 55-65% |
| 2 | Burst Confluence Scorer | Multi-strategy composite scoring | 50-60% |
| 3 | Gamma Wall 300 Continuation | Best-performing wall cluster | 60-70% |
| 4 | Inverted Curve Contrarian | High-confidence bucket rejection | 60-70% |
| 5 | GEX Divergence Confirmation | Divergence + breakout confirmation | 55-65% |
| 6 | Strike Concentration Momentum | Strike-level institutional activity | 55-65% |
| 7 | Multi-Regime Gamma Flip | Quality filter on best strategy | 70-80% |
| 8 | Flow Sweep Momentum | Sweep + gamma confirmation | 55-65% |
| 9 | Regime-Adaptive Cross-Filter | Regime-based strategy selection | 50-65% |

---

## Implementation Notes

1. **Design 7 (Multi-Regime Gamma Flip)** should be the first to implement — it's a quality filter on the best-performing strategy, requiring minimal new infrastructure.

2. **Design 3 (Gamma Wall 300)** needs a dedicated wall detection module for the 300.0 strike specifically.

3. **Design 4 (Inverted Curve)** needs confidence bucket tracking per strategy — currently the system uses continuous confidence, not bucketed.

4. **Design 2 (Burst Confluence Scorer)** is the most complex but potentially the highest-reward — it requires real-time burst detection and scoring.

5. **Design 9 (Regime-Adaptive)** requires regime detection infrastructure — should be built first as a foundation for other designs.

6. All designs should be tested in simulation before live deployment.

---

*Archon 🕸️ — The Celestial Loom*
