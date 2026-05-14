# Implementation Plan: Syngex Confluence & Alpha Discovery Engine
**Target Developer:** @Forge
**Author:** @Synapse
**Objective:** Transform the static performance analysis script into a proactive discovery engine that identifies temporal, structural, and statistical confluences.

---

## Phase 1: Statistical Edge Discovery (The "Anomaly Hunter")
**Goal:** Automatically identify "Alpha Anomalies"—strategies that outperform the global win-rate average within specific confidence buckets.

### Technical Requirements:
1.  **Global Baseline Calculation:** 
    *   At the start of the report generation, calculate the `Global_WinRate` for every confidence bucket (e.g., `Global_WR_30_39%`) across *all* strategies combined.
2.  **Anomaly Detection Logic:**
    *   For each strategy, compare its bucket-specific win rate against the global baseline.
    *   **Threshold:** Flag any strategy where `Strategy_Bucket_WR > (Global_Bucket_WR * 1.5)` or where the deviation exceeds `2.0σ` (if standard deviation is tracked).
3.  **Reporting UI:**
    *   Add a new section: `## 🚀 Statistical Edge Anomalies`.
    *   Use a fixed-width ASCII table to list:
        `| Strategy | Bucket | Strategy WR | Global WR | Lift |`
    *   Highlight these rows with `[ALPHA]` tags.

### Value Prop:
This directly addresses the "30-39% cluster" mystery. It will tell us if that high win rate is a fluke of one strategy or a systemic property of the market being captured by multiple strategies.

---

## Phase 2: Temporal Confluence Engine (The "Super-Signal" Detector)
**Goal:** Detect high-frequency "bursts" where multiple strategies fire simultaneously, indicating a massive, multi-factor market event.

### Technical Requirements:
1.  **Signal Coincidence Mapping:**
    *   Implement a "sliding window" scan (e.g., 10-second windows) across the entire `all_signals` dataset.
    *   Group signals that occur within the same window.
2.  **Coincidence Scoring:**
    *   A "Coincidence Score" is calculated based on the number of *unique* `strategy_id`s firing in that window.
    *   Example: 3 different strategies firing in 5 seconds = `Coincidence Score: 3`.
3.  **Reporting UI:**
    *   Add a new section: `## ⚡ Temporal Burst Events`.
    *   Display:
        `| Timestamp | Count | Strategies | Primary Reason |`
    *   This allows us to see if "Super-Signals" are occurring during high-volatility regime shifts.

### Value Prop:
This identifies "Super-Signals." If three different logic engines (Flow, GEX, and Depth) all agree on a direction at the same second, the probability of that signal being "noise" drops exponentially.

---

## Phase 3: Microstructure Fingerprinting (The "Event-Type" Classifier)
**Goal:** Move beyond strategy names to "Event Types" by analyzing metadata similarities.

### Technical Requirements:
1.  **Metadata Feature Extraction:**
    *   Identify common keys in `metadata` across all signals (e.g., `venue_concentration`, `call_wall_strike`, `esi_memx`, `vamp_bias`).
2.  **Similarity Clustering:**
    *   When signals from different strategies share significant metadata values (e.g., they both trigger on the same `call_wall_strike` or `venue_concentration` spike), group them as an `Event_Cluster`.
3.  **Reporting UI:**
    *   Add a new section: `## 🧬 Microstructure Event Clusters`.
    *   Display:
        `| Event Type | Detected Signals | Common Metadata Trigger | Win Rate |`
    *   Example: `[Exchange Sweep] | 14 signals | venue_concentration > 2.5 | 42%`

### Value Prop:
This allows us to build "Meta-Strategies." Instead of coding for `strategy_id`, we can code for `Event_Type`. It transitions the project from "Strategy Trading" to "Market Regime/Event Trading."

---

## Summary of Implementation Phases

| Phase | Name | Primary Metric | Complexity |
| :--- | :--- | :--- | :--- |
| **1** | **Edge Discovery** | Win Rate Deviation | Low |
| **2** | **Temporal Engine** | Coincidence Count | Medium |
| **3** | **Fingerprinting** | Metadata Similarity | High |
