# Sentiment Sync Review — 2026-06-13

## Source: strategies/full_data/sentiment_sync.py (~335 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `_compute_confidence()` component c1 normalizes `abs(skew_sigma)` against vmax=5.0. If skew_sigma is in standard deviation units (which could be >5 during stress), values clamp at 1.0 always. The ceiling may be appropriate for normal conditions but caps out during high-sigma events when differentiation matters most. | Confidence component c1 | Acceptable or make adaptive based on realized sigma regime |
| info | Gate A magnitude check requires `abs_skew_change > abs_skew_sigma * MAGNITUDE_SIGMA_MULT` AND `abs_vsi > abs_vsi_sigma * MAGNITUDE_SIGMA_MULT`. Both must exceed 2σ simultaneously — rare event. This is by design for "lockstep" detection but inherently low-frequency. | Gate A logic | Verify MAGNITUDE_SIGMA_MULT value matches documented 2σ requirement |
| info | VSI data comes from venue-specific bid/ask imbalance on MEMX+BATS (as per docstring). If venue data stream isn't properly feeding into KEY_VSI_MAGNITUDE_5M window, strategy silently returns []. Cross-check that main.py populates VSI keys. | Rolling window deps | Ensure VSI data pipeline is active |
| info | SYNC_CORR_5M and SYNC_SIGMA_5M use 900s window size per ROLLING_WINDOW_SIZES mapping. Longer windows mean slower response to regime changes vs other 300s-key strategies. | Window configuration | Document rationale for 15min sync window |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Requires BOTH ΔSkew AND VSI to exceed 2σ** — Gate A demands both components show extreme statistical significance simultaneously. In reality, options sentiment and equity flow operate on different time scales: IV skew can change intraday while VSI aggregates over trade ticks. Their σ thresholds are computed independently with different sampling rates. Requiring simultaneous extreme signals means sync events are exceedingly rare. | Gate A (both >2σ) | Consider AND → OR logic OR lower one threshold to 1.5σ while keeping the other at 2σ |
| medium | Γ_sync = Sign(ΔSkew) × Sign(Aggressor_VSI): LONG when both negative (complacency + buying) and SHORT when both positive (fear + selling). This is correct mathematically BUT the interpretation of what "sync" means is subtle. A falling ΔSkew = COMPLACENCY isn't necessarily bullish by itself — it could mean the market is ignoring risk warnings. The confluence assumption needs empirical validation. | Sync sign logic | Validate with backtest; consider adding volatility regime filter |
| medium | Volume anchor gate (Gate B) checks total_volume > rolling average. During market opening/closing, volume naturally exceeds averages, causing Gate B to pass trivially. During midday lull, Gate B blocks all signals even if sync conditions are perfect. | Gate B | Make volume gate relative to session-typical baseline rather than simple average |
| low | GEX regime alignment only gives three discrete states (1.0/0.5/0.0). No gradient between aligned/mismatched. A slightly-misaligned signal gets same 0.5 score as completely inverted regime. | Regime score | Add continuous regime strength metric instead of binary alignment |
| info | Strategy conceptually elegant: detecting when two independent markets (options pricing and equity trades) agree. When they do, conviction should be higher than either signal alone. | Overall design | Excellent multi-market confirmation pattern |

### Combined Verdict: **FIX — Dual-2σ requirement too restrictive**

Primary fix: reduce dual-σ requirement to allow ONE component at 2σ and other at 1.5σ (or OR logic). Secondary: verify VSI data pipeline feeds correctly. Strategy has strong conceptual foundation but current gates are too tight.
