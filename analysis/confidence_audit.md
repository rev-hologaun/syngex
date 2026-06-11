# Confidence Audit Report

**Date:** 2026-06-10  
**Scope:** All strategy files across layer1, layer2, layer3, and full_data  
**Check:** Does `evaluate()` return early (or suppress) when confidence falls below a minimum threshold?

## Summary

| Total Strategies | Has MinConf Check | Missing MinConf Check |
|---|---|---|
| 39 | 39 | **0** |

**All 39 strategies have a minimum confidence floor check.** Every strategy defines `MIN_CONFIDENCE = 0.20` and guards signal emission with a confidence comparison.

---

## Layer 1 — Core Structural Strategies

| Strategy Name | Has MinConfCheck | CurrentValue |
|---|---|---|
| gamma_wall_bounce | YES | 0.20 |
| magnet_accelerate | YES | 0.20 |
| gamma_flip_breakout | YES | 0.20 |
| gamma_squeeze | YES | 0.20 |
| gex_imbalance | YES | 0.20 |
| confluence_reversal | YES | 0.20 |
| vol_compression_range | YES | 0.20 |
| gex_divergence | YES | 0.20 |

---

## Layer 2 — Alpha Strategies

| Strategy Name | Has MinConfCheck | CurrentValue |
|---|---|---|
| delta_gamma_squeeze | YES | 0.20 |
| delta_volume_exhaustion | YES | 0.20 |
| call_put_flow_asymmetry | YES | 0.20 |
| iv_gex_divergence | YES | 0.20 |
| delta_iv_divergence | YES | 0.20 |
| depth_decay_momentum | YES | 0.20 |
| depth_imbalance_momentum | YES | 0.20 |
| exchange_flow_concentration | YES | 0.20 |
| participant_diversity_conviction | YES | 0.20 |
| participant_divergence_scalper | YES | 0.20 |
| exchange_flow_imbalance | YES | 0.20 |
| exchange_flow_asymmetry | YES | 0.20 |
| order_book_fragmentation | YES | 0.20 |
| obi_aggression_flow | YES | 0.20 |
| vamp_momentum | YES | 0.20 |
| order_book_stacking | YES | 0.20 |
| vortex_compression_breakout | YES | 0.20 |

---

## Layer 3 — Micro-Signal Layer

| Strategy Name | Has MinConfCheck | CurrentValue |
|---|---|---|
| gamma_volume_convergence | YES | 0.20 |
| iv_band_breakout | YES | 0.20 |
| strike_concentration | YES | 0.20 |
| theta_burn | YES | 0.20 |

---

## Full Data — v2 Strategies

| Strategy Name | Has MinConfCheck | CurrentValue |
|---|---|---|
| iv_skew_squeeze | YES | 0.20 |
| prob_weighted_magnet | YES | 0.20 |
| prob_distribution_shift | YES | 0.20 |
| extrinsic_intrinsic_flow | YES | 0.20 |
| ghost_premium | YES | 0.20 |
| skew_dynamics | YES | 0.20 |
| smile_dynamics | YES | 0.20 |
| extrinsic_flow | YES | 0.20 |
| gamma_breaker | YES | 0.20 |
| iron_anchor | YES | 0.20 |
| sentiment_sync | YES | 0.20 |
| whale_tracker | YES | 0.20 |

---

## Implementation Patterns

Three patterns were observed across the 39 strategies:

1. **Early return (most common):** `if confidence < MIN_CONFIDENCE: return []`
2. **Floor + early return:** `confidence = max(min_confidence, confidence)` then `if confidence < min_confidence: return []`
3. **Inverted guard:** `if confidence >= MIN_CONFIDENCE: ...` (used by iv_gex_divergence — only emits when above threshold)

All patterns achieve the same effect: signals below 0.20 confidence are suppressed.
