# Plan: Heatmap Expansion — 6×8 Grid, All 25 Strategies

**Author:** Archon  
**Issue:** Frontend `heatmap.html` has a hardcoded `STRATEGIES` array with only 20 entries. 5 strategies are missing from the render (delta_volume_exhaustion, iv_gex_divergence, vamp_momentum, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration).

---

## 1. Problem

The `heatmap.yaml` config has 25 strategy placements, but the frontend `templates/heatmap.html` has a hardcoded JS `STRATEGIES` array with only 20 entries. The YAML is never read by the frontend.

Additionally, the current layout has some suboptimal groupings (e.g., Layer 2 and Layer 3 mixed on same row).

---

## 2. Proposed Layout (6×8 grid)

We have 25 strategies. 6×8 = 48 cells. Plenty of room for future growth.

### Logical grouping by layer:

| Row | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|-----|-------|-------|-------|-------|-------|-------|
| 1 | gamma_wall_bounce | magnet_accelerate | gamma_flip_breakout | gamma_squeeze | gex_imbalance | confluence_reversal |
| 2 | vol_compression_range | gex_divergence | delta_gamma_squeeze | delta_volume_exhaustion | obi_aggression_flow | call_put_flow_asymmetry |
| 3 | iv_gex_divergence | gamma_volume_convergence | iv_band_breakout | strike_concentration | depth_decay_momentum | vamp_momentum |
| 4 | depth_imbalance_momentum | exchange_flow_concentration | iv_skew_squeeze | prob_weighted_magnet | prob_distribution_shift | extrinsic_intrinsic_flow |
| 5 | theta_burn | [free] | [free] | [free] | [free] | [free] |
| 6 | [free] | [free] | [free] | [free] | [free] | [free] |
| 7 | [free] | [free] | [free] | [free] | [free] | [free] |
| 8 | [free] | [free] | [free] | [free] | [free] | [free] |

**Grouping logic:**
- **Row 1:** Layer 1 — Structural GEX strategies (8 total, 6 on row 1, 2 spill to row 2)
- **Row 2:** Layer 1 remainder + Layer 2 alpha (vol compression, gex divergence from L1; delta gamma squeeze, delta volume exhaustion, OBI, call/put flow from L2)
- **Row 3:** Layer 2 + Layer 3 mix (iv gex div, gamma vol conv, iv band break, strike conc, depth decay, vamp)
- **Row 4:** Layer 2 momentum + Layer 3 + Full Data (depth imbalance, exchange flow, iv skew, prob magnet, prob dist, extrinsic)
- **Row 5:** theta_burn (L3) + 5 free cells for future strategies
- **Rows 6-8:** All free

### Why this grouping?

1. **Row 1-2 = pure Layer 1/alpha.** These are the core GEX + order flow strategies. Most active, most signals.
2. **Row 3 = microstructure layer.** VAMP, depth decay, depth imbalance — these use L2 order book data. Grouped together because they share data dependencies.
3. **Row 4 = advanced venues + full data.** Exchange flow (venue-specific), iv_skew, prob strategies — these need more data/context. Lower signal frequency.
4. **theta_burn** on row 5 as a standalone — it's a full_data strategy with unique behavior (pinning detection).

---

## 3. Implementation

### File: `templates/heatmap.html`

Update the `STRATEGIES` array (around line ~370) from 20 to 25 entries:

```javascript
const STRATEGIES = [
    // Row 1: Layer 1 — Core GEX
    { id: 'gamma_wall_bounce',     label: 'GEX_WALL',        layer: 'L1', row: 1, col: 1 },
    { id: 'magnet_accelerate',     label: 'MAGNET',          layer: 'L1', row: 1, col: 2 },
    { id: 'gamma_flip_breakout',   label: 'FLIP_BREAKOUT',   layer: 'L1', row: 1, col: 3 },
    { id: 'gamma_squeeze',         label: 'GAMMA_SQ',        layer: 'L1', row: 1, col: 4 },
    { id: 'gex_imbalance',         label: 'GEX_IMBAL',       layer: 'L1', row: 1, col: 5 },
    { id: 'confluence_reversal',   label: 'CONFLUENCE',      layer: 'L1', row: 1, col: 6 },
    // Row 2: Layer 1/2 Alpha
    { id: 'vol_compression_range', label: 'VOL_COMP',        layer: 'L1', row: 2, col: 1 },
    { id: 'gex_divergence',        label: 'GEX_DIV',         layer: 'L1', row: 2, col: 2 },
    { id: 'delta_gamma_squeeze',   label: 'DELTA_GAMMA',     layer: 'L2', row: 2, col: 3 },
    { id: 'delta_volume_exhaustion', label: 'DELTA_VOL',      layer: 'L2', row: 2, col: 4 },
    { id: 'obi_aggression_flow',   label: 'OBI_AF',          layer: 'L2', row: 2, col: 5 },
    { id: 'call_put_flow_asymmetry', label: 'CALL_PUT_FLOW',  layer: 'L2', row: 2, col: 6 },
    // Row 3: Layer 2/3 Microstructure
    { id: 'iv_gex_divergence',     label: 'IV_GEX_DIV',      layer: 'L2', row: 3, col: 1 },
    { id: 'gamma_volume_convergence', label: 'GAMMA_VOL',    layer: 'L3', row: 3, col: 2 },
    { id: 'iv_band_breakout',      label: 'IV_BAND',         layer: 'L3', row: 3, col: 3 },
    { id: 'strike_concentration',  label: 'STRIKE_CONC',     layer: 'L3', row: 3, col: 4 },
    { id: 'depth_decay_momentum',  label: 'DEPTH_DECAY',     layer: 'L2', row: 3, col: 5 },
    { id: 'vamp_momentum',         label: 'VAMP',            layer: 'L2', row: 3, col: 6 },
    // Row 4: Layer 2 Advanced + Full Data
    { id: 'depth_imbalance_momentum', label: 'DEPTH_IMBAL',  layer: 'L2', row: 4, col: 1 },
    { id: 'exchange_flow_concentration', label: 'EXCHANGE',   layer: 'L2', row: 4, col: 2 },
    { id: 'iv_skew_squeeze',       label: 'IV_SKEW',         layer: 'FULL', row: 4, col: 3 },
    { id: 'prob_weighted_magnet',  label: 'PROB_MAGNET',     layer: 'FULL', row: 4, col: 4 },
    { id: 'prob_distribution_shift', label: 'PROB_DIST',     layer: 'FULL', row: 4, col: 5 },
    { id: 'extrinsic_intrinsic_flow', label: 'EXTRINSIC',    layer: 'FULL', row: 4, col: 6 },
    // Row 5: Full Data remainder
    { id: 'theta_burn',            label: 'THETA_BURN',      layer: 'FULL', row: 5, col: 1 },
];
```

### File: `config/heatmap.yaml`

Update to match the new layout (fix existing conflicts, add all 25):

```yaml
grid:
  columns: 6
  rows: 8

strategies:
  # Row 1: Layer 1 — Core GEX
  gamma_wall_bounce:
    row: 1
    col: 1
    span_cols: 1
    span_rows: 1
  magnet_accelerate:
    row: 1
    col: 2
    span_cols: 1
    span_rows: 1
  gamma_flip_breakout:
    row: 1
    col: 3
    span_cols: 1
    span_rows: 1
  gamma_squeeze:
    row: 1
    col: 4
    span_cols: 1
    span_rows: 1
  gex_imbalance:
    row: 1
    col: 5
    span_cols: 1
    span_rows: 1
  confluence_reversal:
    row: 1
    col: 6
    span_cols: 1
    span_rows: 1
  # Row 2: Layer 1/2 Alpha
  vol_compression_range:
    row: 2
    col: 1
    span_cols: 1
    span_rows: 1
  gex_divergence:
    row: 2
    col: 2
    span_cols: 1
    span_rows: 1
  delta_gamma_squeeze:
    row: 2
    col: 3
    span_cols: 1
    span_rows: 1
  delta_volume_exhaustion:
    row: 2
    col: 4
    span_cols: 1
    span_rows: 1
  obi_aggression_flow:
    row: 2
    col: 5
    span_cols: 1
    span_rows: 1
  call_put_flow_asymmetry:
    row: 2
    col: 6
    span_cols: 1
    span_rows: 1
  # Row 3: Layer 2/3 Microstructure
  iv_gex_divergence:
    row: 3
    col: 1
    span_cols: 1
    span_rows: 1
  gamma_volume_convergence:
    row: 3
    col: 2
    span_cols: 1
    span_rows: 1
  iv_band_breakout:
    row: 3
    col: 3
    span_cols: 1
    span_rows: 1
  strike_concentration:
    row: 3
    col: 4
    span_cols: 1
    span_rows: 1
  depth_decay_momentum:
    row: 3
    col: 5
    span_cols: 1
    span_rows: 1
  vamp_momentum:
    row: 3
    col: 6
    span_cols: 1
    span_rows: 1
  # Row 4: Layer 2 Advanced + Full Data
  depth_imbalance_momentum:
    row: 4
    col: 1
    span_cols: 1
    span_rows: 1
  exchange_flow_concentration:
    row: 4
    col: 2
    span_cols: 1
    span_rows: 1
  iv_skew_squeeze:
    row: 4
    col: 3
    span_cols: 1
    span_rows: 1
  prob_weighted_magnet:
    row: 4
    col: 4
    span_cols: 1
    span_rows: 1
  prob_distribution_shift:
    row: 4
    col: 5
    span_cols: 1
    span_rows: 1
  extrinsic_intrinsic_flow:
    row: 4
    col: 6
    span_cols: 1
    span_rows: 1
  # Row 5: Full Data remainder
  theta_burn:
    row: 5
    col: 1
    span_cols: 1
    span_rows: 1
```

---

## 4. Files to Change

| File | Changes |
|------|---------|
| `templates/heatmap.html` | Update `STRATEGIES` array from 20 → 25 entries, new layout |
| `config/heatmap.yaml` | Rewrite to match new layout, remove conflicts |

---

## 5. After Changes

```
Row 1: gamma_wall | magnet | gamma_flip | gamma_squeeze | gex_imbalance | confluence
Row 2: vol_comp | gex_divergence | delta_gamma_sq | delta_vol_exh | obi_af | call_put_flow
Row 3: iv_gex_div | gamma_vol_conv | iv_band | strike_conc | depth_decay | vamp
Row 4: depth_imbal | exchange | iv_skew | prob_magnet | prob_dist | extrinsic
Row 5: theta_burn | [free] | [free] | [free] | [free] | [free]
Row 6-8: [all free — reserved for future strategies]
```

**25 strategies rendered. 23 free cells for future growth.**

---

## 6. Implementation Steps for Forge

1. Edit `templates/heatmap.html` — replace the `STRATEGIES` array (lines ~370-410) with the new 25-entry array above
2. Rewrite `config/heatmap.yaml` with the new layout
3. Commit and push
