# Gamma Normalization Refactor Plan

## Overview
Replace all hardcoded global net_gamma thresholds (1M–10M range) with a **global 2,000 ceiling**, converting them from **hard gates** to **confidence-loading components**. The signal density stays; conviction reflects actual gamma strength.

## Change Pattern (uniform across all strategies)

### Before (pattern A): Confidence normalization with large ceiling
```python
c5 = normalize(abs(net_gamma), 0.0, 5_000_000.0)
# or
gamma_norm = min(1.0, abs(net_gamma) / 1_000_000)
# or
gamma_strength = 0.2 + 0.3 * min(1.0, net_gamma / 1_000_000)
```

### After (pattern B): Global 2,000 ceiling, confidence-only
```python
GAMMA_CEILING = 2_000  # Global max meaningful |net_gamma|

c5 = min(1.0, abs(net_gamma) / GAMMA_CEILING)
# or
gamma_norm = min(1.0, abs(net_gamma) / GAMMA_CEILING)
# or
gamma_strength = 0.2 + 0.3 * min(1.0, net_gamma / GAMMA_CEILING)
```

**Key differences from old normalize():**
- Replace `normalize(x, 0, N)` with `min(1.0, x / N)` wherever N was a threshold constant
- Keep the formula identical except the ceiling value changes
- If the original used `abs()`, keep `abs()`
- If the original did NOT use `abs()` (directional, like magnet_accelerate keeping sign), keep directionality

### Before (pattern C): Hard gate on net_gamma
```python
if abs(net_gamma_val) < MIN_TOTAL_GEX:  # e.g. 1_000_000 or 100_000
    return None / skip_signal
```

### After (pattern D): Soft confidence bonus (remove gate, add as conf component)
```python
# Remove the hard gate entirely
# Use abs(net_gamma) / 2_000 as a confidence multiplier elsewhere in scoring
```

### Before (pattern E): Wall-based thresholds (gex_calc walls)
```python
walls = gex_calc.get_gamma_walls(threshold=500_000)  # or 5_000_000, 100_000
# or
gex_score = 0.5 + 0.5 * min(1.0, abs(wall_gex) / 5_000_000)
```

### KEEP AS-IS (not changed):
- **Wall GEX thresholds** (`get_gamma_walls(threshold=...)`) — these measure individual strike wall magnitudes, which operate on a different scale. Per-snapshot data shows some walls still hit 5M+.
- **`get_normalized_net_gamma()`** reads — these already return per-message-average values on a reasonable scale
- **Small-scale thresholds** in iv_gex_divergence.py (uses normalized gamma on 0→10 scale, already appropriate)

---

## Batch Execution Plan

Each batch spawns one Forge task. Read the relevant file first to understand context, make surgical edits, verify syntax.

### Batch 1: 5M Ceiling → 2K (most impactful)
Files: All using `normalize(..., ..., 5_000_000.0)` or `/ 5_000_000` on net_gamma

1. `full_data/extrinsic_intrinsic_flow.py` — line ~460, c10
2. `full_data/ghost_premium.py` — line ~353, c5
3. `full_data/iv_skew_squeeze.py` — line ~465, c5
4. `layer2/delta_gamma_squeeze.py` — line ~544, c5
5. `layer2/delta_volume_exhaustion.py` — line ~560, c5
6. `layer2/depth_decay_momentum.py` — line ~338, c5
7. `layer2/iv_gex_divergence.py` — multiple lines (~749, ~755, ~841, ~857, ~862), c2/c3/additional
8. `layer3/strike_concentration.py` — lines ~1208, ~1323, regime_conf

### Batch 2: 1M Ceiling → 2K
Files: Using `normalize(..., ..., 1_000_000.0)` or `/ 1_000_000` on net_gamma

9. `full_data/prob_distribution_shift.py` — lines ~731 (also 10M → check pattern)
10. `layer1/gamma_flip_breakout.py` — lines ~206, ~639 (also gate MIN_GAMMA_STRENGTH=100000 → remove gate)
11. `layer1/magnet_accelerate.py` — line ~394
12. `layer2/delta_iv_divergence.py` — lines ~738, ~740 (500K → 2K)
13. `layer3/theta_burn.py` — line 105 GAMMA_STRENGTH_HIGH=1_000_000 → 2000, lines ~1039, ~1118

### Batch 3: Gates removed / minor files
Files: Hard gates that become soft confidence bonuses, plus remaining files

14. `layer1/gex_divergence.py` — MIN_TOTAL_GEX=1_000_000 gate → remove, replace with confidence score
15. `layer2/iv_gex_divergence.py` — MIN_POSITIVE_NORMALIZED_GAMMA=5.0 stays (it's on normalized scale, already correct)
16. `layer2/call_put_flow_asymmetry.py` — lines ~494, ~587, metadata "gamma_intensity" division 1M → 2K
17. `layer1/gamma_squeeze.py` — MIN_MASSIVE_WALL_GEX=5_000_000 if it's on net_gamma (check); wall GEX stays

### Cross-cutting notes for all batches:
- Update docstrings/comments that reference old thresholds (e.g., "10. Net gamma: net_gamma / 5_000_000" → "2_000")
- If a file defines a constant like `MIN_GAMMA_STRENGTH = 100_000`, replace or remove it based on whether it's a gate or a normalization ceiling
- Do NOT modify any `get_gamma_walls(threshold=N)` calls — those are wall-level GEX, not net_gamma
- Verify all edit targets exist in the file before editing (grep confirms line positions may shift slightly)
- Syntax check after every edit (python3 -m py_compile on the file)
