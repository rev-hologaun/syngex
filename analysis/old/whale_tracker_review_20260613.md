# Whale Tracker Review — 2026-06-13

## Source: strategies/full_data/whale_tracker.py (~374 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `normalize(concentration_sigma, 0.0, 5.0)` for concentration magnitude component (c1). Concentration ratio σ values above 5 are possible (hence gate A requiring >5σ), and these would cap at 1.0. This is appropriate since the gate already filters below 5σ, so c1 only differentiates between "just past threshold" and "well past." The scale is reasonable. | Confidence c1 analysis | No action needed — properly calibrated |
| info | Gate C checks if concentration occurs near a gamma wall using gex_calc proximity check. If wall classification thresholds use old-scale values (like other strategies), no walls will be detected and Gate C always fails silently. | Gamma coincidence logic | Verify wall proximity uses normalized gamma scale |
| info | Strategy uses 900s (15min) rolling windows per ROLLING_WINDOW_SIZES mapping for all whale-specific keys. For institutional order tracking where whales may place orders over hours, this window is appropriate. But it also means the strategy can't detect very recent (<15min) whale activity that hasn't accumulated enough history. | Window configuration | Accept as correct for detection methodology |
| info | MIN_CONFIDENCE = 0.20 with 5-component model means each component averages to ~0.20 minimum. With c1 needing 5σ+ data just to enter evaluation, early components start at relatively high values. Good design. | Confidence model | No action needed |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Concentration ratio definition requires scrutiny** — Ω_conc = biggest_size / smallest_size at best price levels. If there's only ONE level on bid side and one on ask side (minimum case), and they're both from same participant, ratio = 1.0. For the ratio to exceed 5σ threshold, you need true outlier sizing. However, in real options markets, most "biggest size" entries are from regular market makers who quote wide sizes naturally. Distinguishing genuine whale accumulation from normal MM quoting behavior requires more than just size ratios. | Core detection logic | Add additional filters: look for persistent concentration across multiple time windows OR new participant appearing → add verification layer |
| medium | num_participants ≤ 2 filter correctly identifies low-participant concentration but creates false positives when legitimate large institutions split orders across exactly 2-3 algo desks. The ≤2 threshold blocks signals from genuinely institutional activity that happens to involve 2-3 execution algorithms. | Participant filter | Consider increasing to ≤3 while adding a confidence penalty for 2 participants vs 1 |
| medium | GEX regime alignment gives binary 1.0/0.0 scoring. LONG signals require POSITIVE gamma regime. But whale accumulation during NEGATIVE gamma could be especially valuable — institutional buying into negative gamma creates strong mean-reversion setups. The regime restriction limits signal opportunities. | Regime gating | Allow signals in any regime with reduced confidence (component 5 instead of separate gate) |
| low | Entry/stop/target uses fixed percentages (0.5% stop, 1.0% target). Whales often move markets more than 0.5%, making stops too tight. During confirmed whale activity, wider targets (1.5-2.0%) with wider stops (1.0%) may capture full intraday impact better. | Stop/target design | Consider dynamic stop based on observed whale order size |
| info | Strategy conceptually elegant: institutional orders leave footprints in size concentration. Low participant count + outsized size = classic whale signature. Clean separation from retail noise filtering. | Overall design | Excellent pattern; consider extending to time-based persistence (order lasting >N minutes) |

### Combined Verdict: **REVIEW — Solid concept, possibly needs broader scope**

No critical bugs found. Potential improvements: relaxed participant threshold (≤3 instead of ≤2), allow any-regime signals with adjusted confidence, wider targets for confirmed whale moves. Strategy should fire when conditions align but range of qualifying scenarios may be narrow.
