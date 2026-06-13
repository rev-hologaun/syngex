# VAMP Momentum Review — 2026-06-13

## Source: strategies/layer2/vamp_momentum.py (~384 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `normalize(avg_participants, 1.0, 5.0)` for participant conviction component (c3). If average participants typically range from 2-20 in options markets, then vmax=5 caps at 1.0 for any book with >5 participants, which is most of the time. This makes participant conviction always-max regardless of actual participant diversity. | Line ~299 | Adjust vmax to realistic max participant count or use log scale |
| info | Deviation threshold (`dev_threshold`) used in confidence c1 normalization. If computed from rolling data and the current deviation equals dev_threshold exactly, normalize returns 0.5 (midpoint). This means signals right at threshold boundary get moderate confidence rather than being filtered. | Confidence line ~287 | Document behavior; consider using strict > comparison |
| info | Spread stability uses `spread_ratio = current_spread / mean_spread` normalized against 0→2.0. Spreads that widen to 3× normal (ratio=3.0) normalize to exactly 1.0 contribution, same as a tight spread. No differentiation beyond 2×. | Spread scoring | Consider asymmetric penalty for widening vs compression |
| info | GEX regime confidence uses min(1.0, abs(net_gamma) / 2000.0). Correct normalized scale. Consistent with other strategies. Good practice. | Regime confidence | No action needed — properly calibrated |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Participant count normalization ceiling too low** — avg_participants > 5 normalizes to full score regardless of whether book has 5 or 50 participants. In real options markets, top 10 bid/ask levels can have 10-30 distinct participants. The 5-participant cap means participant conviction doesn't differentiate between "few participants" (concentration signal) and "many participants" (broad participation = more reliable). | Component 3 analysis | Increase vmax to match observed participant range (15-20) or reverse logic (more participants = lower conviction for concentration trades) |
| medium | VAMP deviation depends on price × size weighting across top 10 levels. At market open when liquidity is sparse, top 10 may not fill evenly (some levels wide gap), making VAMP calculation unstable. Mid-price computation assumes continuous depth within top 10 levels. | VAMP formula | Add minimum level count check (need ≥ 7 filled levels out of 10) before computing VAMP |
| medium | Volume depth density checks `Σ size(top 10) > MA(total depth, 60s)`. Using 60-second MA for total depth is very short window — during rapid order flow changes, this adapts quickly but also creates noise. A 60s window might miss slower structural shifts in market depth. | Gate B logic | Evaluate 120s or 180s MA for smoother baseline |
| low | Entry price = underlying mid-price with fixed 0.5% stop. Unlike gamma-based strategies that use wall proximity for dynamic stops, VAMP uses mechanical stop placement. Acceptable for microstructure strategy where holds are short (1-5 min). | Stop/target design | Consider ATR-normalized stops for adaptability |
| info | Strategy concept is clean: volume-weighted center-of-gravity deviation from mid reveals book bias before L1 price reacts. Sound microstructure theory applied well. | Overall design | Excellent pattern worth documenting as reusable concept |

### Combined Verdict: **REVIEW — Minor participant scale calibration**

No critical bugs. Primary fix: adjust participant count normalization ceiling to match observed ranges. Secondary: add minimum depth level check for market-open robustness. Strategy architecture is sound.
