# Plan: Heatmap Strategy Reordering (Layer-Grouped, 6 Columns)

## 1. Current State Analysis

**What we found:**

- `app_heatmap.py`: `_transform_for_socket()` line ~83 iterates `strategy_health.items()` — Python dicts preserve insertion order (3.7+). No sorting/grouping happens here. Strategies flow in whatever order main.py produces.
- `templates/heatmap.html`: Lines ~506–529 render `Object.values(s)` in `style="grid-template-columns: repeat(6, 1fr)"`. The frontend ALREADY has group-header detection logic (`getLayer()`, `getLayerLabel()`), but two problems:
  - **Bug**: `currentLayer` variable is assigned once at line ~516 but NEVER updated inside the forEach loop — only the first group gets styled.
  - No actual re-sorting by layer occurs before rendering.
- `main.py` (line ~2692): `_build_strategies_for_heatmap()` iterates `for layer_key in ["layer1", "layer2", "full_data", "layer3"]`. Within each layer, strategies come out in **YAML dict key order**. Since Python 3.7+, dicts preserve insertion order. So the ordering IS controlled by `config/strategies.yaml`.

**Conclusion:** Minimal changes required — reorder keys in the YAML, fix one frontend bug. No backend server changes needed.

### Files that need modification

| File | Change type | Description |
|------|-------------|-------------|
| `config/strategies.yaml` | Reorder keys | Reorder TOP-LEVEL KEYS under `layer1:`, `layer2:`, and `full_data:` sections to match target ordering |
| `templates/heatmap.html` | Bug fix + enhancement | Fix `currentLayer` never-updating bug; add explicit client-side SORT priority map as belt-and-suspenders |
| `app_heatmap.py` | None | Already works correctly — preserves key order through the pipeline |

---

## 2. Target Strategy Ordering

| Layer | Position | Strategy | Rationale |
|-------|----------|----------|-----------|
| **Layer 1** | 1 | price_velocity | Pure price change rate — simplest, most direct signal |
| | 2 | volume_spike | Binary event trigger — still simple, just needs anomaly detection |
| | 3 | flow_delta | Bid/ask delta comparison — one ratio check |
| | 4 | volume_imbalance | Two-volume comparison + sigma threshold — slightly more complex |
| | 5 | order_flow_imbalance | Volume-adjusted flow direction with multiple thresholds |
| | 6 | tick_momentum | Tick-direction persistence tracking — multi-step stateful |
| **Layer 2** | 1 | extrinsic_proximity | Distance-to-resistance proximity check — simple threshold |
| | 2 | gamma_flip_zone | Gamma flip detection — single state flag |
| | 3 | gamma_breaker | Gamma wall break detection — directional breach analysis |
| | 4 | iv_skew_squeeze | IV skew extreme detection — volatility surface math |
| | 5 | volatility_term_structure | Term structure curve analysis — multi-strike computation |
| | 6 | skew_dynamics | IV skew slope tracking — rolling window derivative |
| | 7 | smile_dynamics | Skew surface dynamics — shape/concavity analysis (most complex L2) |
| **Full Data** | 1 | prob_weighted_magnet | OI-weighted probability check — clear formula |
| | 2 | ghost_premium | PDR detection — single metric with gates |
| | 3 | prob_distribution_shift | Distribution shift analysis — heavy statistical computation |
| | 4 | extrinsic_intrinsic_flow | Extrinsic/intrinsic value flow — dual-window comparison |
| | 5 | extrinsic_flow | Extrinsic value flow tracking — single-window multi-gate |
| | 6 | sentiment_sync | Cross-market options+equity correlation — sync detection |
| | 7 | iron_anchor | Wall convergence analysis — complex spatial math |
| | 8 | whale_tracker | Market depth concentration — lowest-level microstructure |
| **Layer 3** | 1 | gamma_volume_convergence | Only one, stays put |

**Design principle:** Within each layer, place the simplest/directest signals first and the most computationally-heavy/composite signals last. This creates a natural reading flow: scan the left side for quick signals, look right for confirmation.

---

## 3. Implementation Steps

### Step 1: Reorder YAML keys in `config/strategies.yaml`

Reorder the top-level keys under each layer section (only these three layers have multiple strategies):

**`layer1:`** (6 strategies) → Order: price_velocity, volume_spike, flow_delta, volume_imbalance, order_flow_imbalance, tick_momentum

**`layer2:`** (7 strategies) → Order: extrinsic_proximity, gamma_flip_zone, gamma_breaker, iv_skew_squeeze, volatility_term_structure, skew_dynamics, smile_dynamics

**`full_data:`** (8 strategies) → Order: prob_weighted_magnet, ghost_premium, prob_distribution_shift, extrinsic_intrinsic_flow, extrinsic_flow, sentiment_sync, iron_anchor, whale_tracker

(`layer3:` has only one strategy — no change needed.)

**Important:** Preserve all existing content (params, tracker settings, comments) — only move the YAMl keys to new positions.

### Step 2: Fix heatmap template bug

In `templates/heatmap.html`, find the JavaScript that processes strategy entries (~lines 516–530):

**Bug fix:** Add `currentLayer = layerName;` after the group-separator block to ensure subsequent groups are properly detected.

```javascript
// After detecting layer boundary and creating group separator div, add:
currentLayer = layerName;  // <-- THIS LINE WAS MISSING
```

**Enhancement:** Add an explicit client-side STRATEGY_PRIORITY sort map AFTER the group-header detection logic, as belt-and-suspenders against any server-side key-order issues:

```javascript
// Priority map: [layer_priority, display_order_within_layer]
const STRATEGY_PRIORITY = {
    // Layer 1 (priority 1)
    'price_velocity': [1, 1],
    'volume_spike': [1, 2],
    'flow_delta': [1, 3],
    'volume_imbalance': [1, 4],
    'order_flow_imbalance': [1, 5],
    'tick_momentum': [1, 6],
    // Layer 2 (priority 2)
    'extrinsic_proximity': [2, 1],
    'gamma_flip_zone': [2, 2],
    'gamma_breaker': [2, 3],
    'iv_skew_squeeze': [2, 4],
    'volatility_term_structure': [2, 5],
    'skew_dynamics': [2, 6],
    'smile_dynamics': [2, 7],
    // Full Data (priority 3)
    'prob_weighted_magnet': [3, 1],
    'ghost_premium': [3, 2],
    'prob_distribution_shift': [3, 3],
    'extrinsic_intrinsic_flow': [3, 4],
    'extrinsic_flow': [3, 5],
    'sentiment_sync': [3, 6],
    'iron_anchor': [3, 7],
    'whale_tracker': [3, 8],
    // Layer 3 (priority 4)
    'gamma_volume_convergence': [4, 1],
};

// Apply sort using priority map (belt-and-suspenders)
const sortedEntries = Object.entries(s).sort((a, b) => {
    const priA = STRATEGY_PRIORITY[a[0]?.toLowerCase()] || [99, 99];
    const priB = STRATEGY_PRIORITY[b[0]?.toLowerCase()] || [99, 99];
    return priA[0] !== priB[0] ? priA[0] - priB[0] : priA[1] - priB[1];
});

// Then iterate sortedEntries instead of Object.entries(s)
sortedEntries.forEach(([key, val]) => { ... });
```

### Step 3: Validation

1. Restart the heatmap service: `python3 app_heatmap.py`
2. Open in browser (port 8502 or HEATMAP_PORT env var)
3. Verify:
   - Exactly 6 columns visible
   - Group headers appear between layers
   - No strategy appears twice or missing
   - Total cards = enabled strategy count from config
4. Check the `currentLayer` fix: scrolling should show proper gap styling between all group boundaries

---

## 4. Risk Assessment

- **Low risk.** YAML reordering is purely cosmetic — the engine doesn't care about key order. It only reads by strategy name.
- **Frontend sort map** is defensive — if YAML ever gets corrupted, the JS sort still works.
- **Zero functional impact** — no trading logic, no data processing, no behavioral changes.
- Must restart heatmap process (not main.py) to see changes since it's a standalone Flask subprocess.
