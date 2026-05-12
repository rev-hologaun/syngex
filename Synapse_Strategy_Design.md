# 👁️‍🗨️ Synapse Strategy Design: High-Fidelity Stream Integration

**Date:** 2026-05-11
**Author:** Synapse
**Context:** Post-v1.90 Upgrade (Level 2 / TotalView / BATS Integration)

---

## 🧠 Intelligence Synthesis

The integration of the four TradeStation streams (Quotes, Option Chain, Depth Quotes, and Depth Aggregates) provides a multi-dimensional view of market microstructure that was previously unavailable. We are no longer just observing price; we are observing the **intent** (Depth Quotes), the **liquidity density** (Depth Aggregates), and the **hedging pressure** (Option Chain) in real-time.

### Data Capabilities Matrix
| Stream | Primary Signal | Microstructure Insight |
| :--- | :--- | :--- |
| **Quotes (L1)** | Price/Volume | Venue-specific execution (IEX vs BATS), VWAP deviation. |
| **Depth Quotes (L2)** | Order Book Imbalance | Individual participant walls (e.g., MEMX ask walls), liquidity voids. |
| **Depth Aggregates** | Liquidity Density | Participant concentration, rapid shifts in aggregate bid/ask pressure. |
| **Option Chain** | Gamma/Delta Skew | Dealer hedging zones, IV-driven tail risk, speculative flow. |

---

## 🚀 New Strategy Proposals

### 1. The "Liquidity Vacuum" Hunter (L2 + Aggregates)
**Concept:** Detect sudden "thinning" of the order book combined with aggressive price movement.
- **Signal:** A rapid decrease in `total_bid_size` or `total_ask_size` in the `depthagg` stream, occurring simultaneously with a large `last_size` print on a specific venue (e.g., BATS) in the `quotes` stream.
- **Logic:** When a large order clears a price level and the `num_participants` at that level drops to zero, it creates a "vacuum." Price often teleports through these voids.
- **Execution:** Scalp the gap between the previous mid-price and the new, lower-liquidity mid-price.

### 2. Gamma-Weighted Momentum (Options + L2)
**Concept:** Use Option Gamma to identify "sticky" price zones and trade breakouts from them.
- **Signal:** High `gamma` and `open_interest` at a specific strike (e.g., TSLA 420C) acting as a "Gamma Wall." 
- **Logic:** Dealers must hedge aggressively as price approaches these strikes. If price breaks the wall with high `total_ask_size` (from `depthagg`) and high `volume` (from `optionchain`), the dealer hedging becomes a self-fulfilling momentum driver.
- **Execution:** Trend-following entry upon a "Gamma Wall Breakout," confirmed by L2 liquidity exhaustion on the opposing side.

### 3. The "Participant Divergence" Scalper (L2 + Aggregates)
**Concept:** Identify "Fake Walls" vs. "Real Walls."
- **Signal:** A large `total_size` at a price level in `depthagg` where `num_participants` is very low (e.g., 1 participant holding 90% of the size).
- **Logic:** A single-participant wall is fragile and easily "spoofed" or pulled. A multi-participant wall (high `num_participants`) is much more robust.
- **Execution:** 
    - **Fade the Spoof:** If price approaches a low-participant wall, expect a rapid breach.
    - **Ride the Wall:** If price approaches a high-participant wall, treat it as hard support/resistance.

### 4. IV Skew / Tail-Risk Reversal (Options + L1)
**Concept:** Trade the "Fear Gradient."
- **Signal:** Rapid expansion in `iv` and `probability_otm_iv` for OTM Puts relative to OTM Calls, combined with increasing `net_change_pct` in the `quotes` stream.
- **Logic:** When IV skew steepens sharply, it indicates institutional hedging (tail-risk protection). This often precedes a volatility expansion event.
- **Execution:** Long volatility (straddles/strangles) or shorting the underlying when the skew reaches extreme historical percentiles.

---

## 🛠️ Implementation Roadmap

1.  **Phase 1 (Validation):** Backtest the "Liquidity Vacuum" logic using the `orb_probe.py` historical logs.
2.  **Phase 2 (Integration):** Add `gamma_density` and `participant_concentration` metrics to the existing Syngex heatmap.
3.  **Phase 3 (Live Alpha):** Deploy the "Gamma-Weighted Momentum" as a high-conviction sub-strategy within the `Ignition-Master` v2 framework.

---
*End of Design Document*
