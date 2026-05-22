# Synapse Strategy Design: Microstructure Event Clusters (MEC)

**Author:** Synapse 👁️‍🗨️
**Date:** 2026-05-21
**Targeting:** Microstructure Event Clusters & Temporal Bursts

---

## Overview
The goal is to move away from single-factor strategies and toward "Cluster-Triggered" execution. The `analyzed_20260520.md` report identifies several high-coincidence "Event Clusters" where multiple independent strategies (Gamma, Flow, Magnet, Vol) fire simultaneously. These represent high-conviction structural shifts in the market.

## Strategy 1: The "Gamma-Flow Convergence" (GFC)
**Targeting:** High-coincidence clusters involving `gamma_flip_breakout`, `exchange_flow_imbalance`, and `gex_divergence`.

### Logic
- **Detection:** Monitor for "Temporal Bursts" (Phase 2) where `exchange_flow_imbalance` (VSI/ROC) coincides with a `gamma_flip_breakout` signal.
- **The Edge:** The report shows `gamma_flip_breakout` has a massive win rate (76.7%). When this is accompanied by an extreme flow imbalance (e.g., AggVSI > 50%), it indicates a "forced" move (e.g., dealer hedging or massive institutional sweep).
- **Execution:**
    - **LONG:** `gamma_flip_breakout` (Bullish) + `exchange_flow_imbalance` (AggVSI > 0.5) + `gex_divergence` (Bullish).
    - **SHORT:** `gamma_flip_breakout` (Bearish) + `exchange_flow_imbalance` (AggVSI < -0.5) + `gex_divergence` (Bearish).
- **Confidence Multiplier:** Apply a 1.5x multiplier to the signal confidence if it belongs to a known "Event Cluster" (Phase 3).

## Strategy 2: "Magnet-Wall Reversal" (MWR)
**Targeting:** Clusters where `magnet_accelerate` and `gamma_wall_bounce` coincide.

### Logic
- **Detection:** Monitor for "Magnet Pull" events (Phase 2) that occur near a high-GEX Gamma Wall.
- **The Edge:** The `magnet_accelerate` strategy shows anomalous lift in the 80-89% bucket (302% lift). When the "Magnet" pulls price toward a structural Gamma Wall, the probability of a "bounce" or "rejection" increases exponentially.
- **Execution:**
    - **REVERSAL:** Price approaches a `gamma_wall_bounce` level + `magnet_accelerate` indicates a "Magnet Pull" toward that level.
    - **ENTRY:** Limit order at the Wall/Magnet intersection.
    - **EXIT:** Target the next liquidity pocket or a 1.5x RR stop.

## Strategy 3: "Volatility Compression Breakout" (VCB)
**Targeting:** High-confidence `vol_compression_range` signals during `exchange_flow_concentration` bursts.

### Logic
- **Detection:** Identify periods of low realized volatility (compression) followed by a sudden burst in `exchange_flow_concentration` (Phase 2).
- **The Edge:** `vol_compression_range` shows high win rates (43.2%) in trending/sideways regimes. When compression is broken by a concentrated flow burst, it signals the start of a new trend phase.
- **Execution:**
    - **ENTRY:** `vol_compression_range` (Breakout) + `exchange_flow_concentration` (High VSI) + `strike_concentration` (High density).
    - **DIRECTION:** Follow the direction of the flow concentration.

## Strategy 4: "The Cluster Sniper" (Universal Cluster Strategy)
**Targeting:** Any Temporal Burst (Phase 2) with a Coincidence Score $\ge 7$.

### Logic
- **Detection:** Use a real-time monitor for the `Temporal Burst` window (10s).
- **The Edge:** The report lists several bursts with 7-9 coinciding strategies (e.g., the 1779283802.089 event with 584 signals). These are "Black Swan" or "Flash" events.
- **Execution:**
    - **ACTION:** When a burst of $\ge 7$ strategies is detected, immediately execute a "Micro-Scalp" in the direction of the majority of the signals.
    - **PARAMETER:** Extremely tight stop (0.1%) and very fast exit (1-5 min hold).
    - **GOAL:** Capture the immediate "shock" volatility.

---
**End of Plan**
