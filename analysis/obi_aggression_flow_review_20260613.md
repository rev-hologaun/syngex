# OBI + Aggression Flow Review — 2026-06-13

## Source: strategies/layer2/obi_aggression_flow.py (~360 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `net_gamma = gex_calc.get_normalized_net_gamma()` for regime direction determination (line ~276). If get_normalized_net_gamma() returns values near zero during flat markets, the GEX bias score always defaults to 0.5 (neutral) instead of 0.0 or 1.0. | Lines ~273-280 | Add minimum threshold for meaningful bias detection |
| info | `_eval_counter` module-level variable used for throttling INFO logs. Thread-safe in single-threaded context but not safe if multiple instances run concurrently. | Module level ~24 | Consider class-level counter or remove throttle entirely (logging is cheap) |
| info | Gate A checks volume spike > 1.5× rolling avg using KEY_VOLUME_5M window. If total volume window isn't populated correctly by main.py, Gate A passes by default ("no data → pass gate"). | _gate_a_volume method | Make missing data = fail instead of pass-by-default |
| info | GEX regime alignment scoring uses min(1.0, abs(net_gamma) / 2000.0). Correct scale. However, it applies the same scaling regardless of strategy-specific gamma relevance. | Confidence c7 | Consider strategy-specific gamma importance weighting |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **OBI and AF magnitude thresholds may be too tight** — OBI > 0.75 requires 75% bid-heavy book (for LONG). OBI formula = (bid_size - ask_size) / total_depth means 0.75 requires bid/ask ratio of 7:1. In liquid options markets, this extreme imbalance happens only during stress events. Similarly AF > 0.5 requires 75% buy aggression. Both extremes simultaneously are very rare. | Master trigger lines ~100-105 | Consider relaxing thresholds to 0.65/0.40 or document as intentional "only ultra-high conviction" filter |
| medium | Confluence factor `abs(OBI × AF)` gives highest weight when BOTH are strongly aligned (e.g., OBI=0.9, AF=0.8 → product=0.72). But a weak OBI (0.2) with strong AF (0.9) produces only 0.18, potentially below confidence floor. The multiplication penalizes partial agreement disproportionately. | Line ~331-332 | Consider using min() or geometric mean instead of raw product |
| medium | 7-component confidence includes participant diversity (Gate B), which checks that trades come from ≥2 exchanges. This is correct microstructure hygiene but may block signals during venue-specific events where one exchange dominates flow temporarily. | Gate B logic | Accept as feature; note that venue concentration signals will be filtered out |
| low | Entry price = underlying_price with fixed stop at STOP_PCT (0.5%). No wall-based stops like other layer2 strategies. Simple but less adaptive to current market structure. | Signal construction | Consider incorporating nearest gamma wall for stop placement |
| info | Strategy design is elegant: passive book skew + active trade execution confirmation = high precision, lower frequency. The dual-confirmation approach filters noise well. | Overall design | Good pattern worth replicating in other strategies |

### Combined Verdict: **REVIEW — Thresholds likely just too strict for normal market**

No code bugs found. OBI > 0.75 AND AF > 0.5 simultaneously is extremely restrictive. Consider lowering to 0.65/0.40 range. Strategy architecture is sound.
