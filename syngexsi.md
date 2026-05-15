# Design Document: Structural Integrity (SI) Component
**Project:** Syngex Intelligence Evolution
**Target Implementation:** @Forge
**Architectural Oversight:** @Archon
**Conceptual Designer:** @Synapse

---

## 🎯 Objective
To transition the Syngex signal engine from **Reactive Ratio-Based Confidence** (which is prone to "stop-out noise") to **Predictive Structural Confidence**. 

The goal is to ensure that high-confidence signals are backed by verifiable market forces, rather than just mathematically tight stop-losses.

---

## 🏗️ The SI Framework: Three Pillars of Validation

The **Structural Integrity (SI) Score** will be a composite metric (0.0 to 1.0) derived from three independent validation modules.

### 1. The Momentum Validator (MV) — "The Force"
*   **Purpose:** Distinguest between "price drift" and "aggressive intent."
*   **Core Metric:** $\text{Force Index} = \frac{\Delta \text{Delta Density}}{\Delta \text{Volume}}$
*   **Logic:** Measures the efficiency of price movement. High volume with low delta density is "churn." High volume with massive delta density is "structural force."
*   **High Integrity Trigger:** A sudden, non-linear spike in delta-to-volume ratio.

### 2. The Liquidity Anchor (LA) — "The Gravity"
*   **Purpose:** Determines if the signal is fighting the market's structural "walls" or riding them.
*   **Core Metric:** $\text{Wall-Interaction Score} = \frac{\text{Proximity to Wall}}{\text{Order Book Depth at Wall}}$
*   **Logic:** A signal approaching a massive Gamma Wall with high depth is "dangerous." A signal breaking through a wall with high depth is "structural."
*   **High Integrity Trigger:** A breakout event where the `wall_gex` is high, but the `order_book_depth` is being rapidly consumed (the "breakout" signature).

### 3. The Regime Coherence (RC) — "The Context"
*   **Purpose:** Ensures the signal direction aligns with the prevailing market regime.
*   **Core Metric:** $\text{Regime Alignment} = \text{Direction} \cdot \text{Regime Sign}$
*   **Logic:** A LONG signal in a Negative Gamma (Volatile) regime has lower structural integrity than a LONG signal in a Positive Gamma (Mean-Reverting) regime.
*   **High Integrity Trigger:** Perfect alignment between signal direction and the `net_gamma` regime state.

---

## 🧪 Mathematical Synthesis (The SI Score)

The final score is a weighted harmonic mean (to ensure that a zero in any single pillar heavily penalizes the total score):

$$SI = \left( \frac{w_1}{MV} + \frac{w_2}{LA} + \frac{w_3}{RC} \right)^{-1}$$

*(Weights $w$ to be tuned during Phase 1 testing)*

---

## 🚀 Integration Plan: `gamma_flip_breakout` (Phase 1 Target)

The first practical application will be to replace the "dangerous" `risk_norm` in the `gamma_flip_breakout.py` strategy.

### **Current (Flawed) Logic:**
$$\text{Confidence} \propto \text{Tightness of Stop (Risk)}$$
*Problem: Small stops in high volatility lead to high confidence but low win rates.*

### **Proposed (Robust) Logic:**
$$\text{Confidence} = \text{Base\_Confidence}(\text{Gamma/Wall/Regime}) \times \text{Structural Integrity (SI)}$$

**How it will work in the code:**
1.  **Remove:** `risk_norm` from the `_compute_confidence` function.
2.  **Add:** An `_evaluate_structural_integrity` call within the `evaluate` loop.
3.  **Result:**
    *   **The "Noise" Signal:** Price hits a wall, stop is tiny $\rightarrow$ $SI$ is low (no volume/delta) $\rightarrow$ **Confidence stays low.**
    *   **The "Real" Breakout:** Price breaks a wall, volume spikes, delta density explodes $\rightarrow$ $SI$ is high $\rightarrow$ **Confidence skyrockents.**

---

## 📅 Implementation Roadmap for @Archon

1.  **Phase 1 (Data Prep):** Update `rolling_data` to include `delta_density` and `volume_zscore` to support the MV module.
2.  **Phase 2 (Module Dev):** Implement the three SI sub-modules as standalone Python classes.
3.  **Phase 3 (Integration):** Refactor `gamma_flip_breakout.py` to utilize the SI score.
4.  **Phase 4 (Validation):** Run the `analyze_strategies_forge.py` to verify the Win% vs. Confidence correlation.
