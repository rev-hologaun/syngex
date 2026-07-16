# Order Book Stacking Review — 2026-06-13

## Source: strategies/layer2/order_book_stacking.py (~479 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `normalize(vol_ratio, 0.0, 2.0)` for volume confirmation component (c3). vol_ratio = latest_volume / avg_volume — values of 2.0+ (2× spike) should give full contribution but capping at 2.0 means a 5× volume surge gives same confidence as 2×. Minor loss of differentiation at extreme volume events. | Line ~445 | Acceptable or increase vmax for extreme events |
| info | Strategy uses depth data keys (`KEY_DEPTH_BID_LEVEL_AVG_5M`, `KEY_SIS_BID_5M`, etc.) that must be populated by main.py from L2 market depth streams. If depth stream parsing has issues, rolling windows will be empty and strategy silently returns []. | Evaluate method early returns | Add debug logging for missing depth data |
| info | `_safe_get_walls` calls `gex_calc.get_gamma_walls(threshold=...)` — threshold not explicitly defined in this file, likely defaults to class constant. Verify threshold matches normalized gamma scale. | Wall helper methods | Confirm threshold value |
| info | Four distinct signal types (STACK_BOUNCE_LONG, STACK_BREACH_SHORT, STACK_BOUNCE_SHORT, STACK_BREACH_LONG) all compute SIS independently but could share intermediate computations. Small perf concern with large book scans. | All four _check_* methods | Consider shared computation if performance becomes an issue |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **SIS calculation depends on level-by-level size comparison** — Stack Intensity Score = largest_level_size / average_level_size per side. In deep order books with many narrow levels, average can be dominated by thin levels near the spread while "stacks" are at specific price levels further out. The averaging approach may dilute genuine stack signals when book depth is >10 levels. | SIS formula logic | Consider using median instead of mean for level averaging; median is more robust against thin-tick noise |
| medium | ROC-based direction detection uses SIS_ROC which compares current SIS to past SIS. If initial window fill takes time (need MIN_DATA_POINTS), early signals lack ROC context and default to neutral scoring. This means fresh market opens produce weaker stacking signals until history builds up. | ROC component analysis | Accept as normal warm-up behavior; document expected cold-start delay |
| medium | Volume confirmation uses total volume ratio (latest vs avg). For options markets where volume is event-driven (earnings, economic releases), baseline averages during quiet periods make any trade count as "spike." During active hours, spikes become harder to detect. Adaptive threshold based on session type would help. | Volume confirmation gate | Consider time-of-day aware thresholds |
| medium | Spread tightness score (component weight 0.10) only matters when spread is between 0→0.05%. Tighter spreads get higher scores but beyond that range contribute zero regardless of how wide spread gets. No penalty for widening beyond the normalization ceiling. | Spread component | Consider adding penalty for very wide spreads (>0.1%) |
| low | Participant diversity uses bid_participants / ask_participants ratio deviation from equilibrium (0.5). Equal participants = maximum score. But institutional whale activity often shows ONE dominant participant on one side, which this component penalizes heavily. | Participant diversity component | Consider separate "whale detection" component that actually rewards concentration |
| info | Signal strength formula includes "parts" (participant diversity) and "vol" (volume) components weighted equally — good balanced design. Weighted sum architecture is cleaner than simple averaging. | Signal strength line ~438 | Good pattern |

### Combined Verdict: **REVIEW — Sound concept, possible median-vs-mean improvement**

No critical bugs found. Core logic is well-designed. Primary optimization: consider median-level averaging for SIS instead of mean. No structural changes needed for it to fire.
