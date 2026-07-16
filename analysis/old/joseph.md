11 Strategies Gate Analysis,

---

 Weak — Almost No Gamma Filtering (may fire blind),

sentiment_sync,
Zero gamma connection. Combines skew + VSI but has no gamma regime awareness.,
Gates are pure magnitude/volume/price confirmation: |skew_change|/σ ≥ 2.0, vol ≥ avg × 1.0×, vsi_mag ≥ 0.1%.,
Skew + volume surge together would fire regardless of whether you're fading a breakout in negative gamma or getting run over by one.,

---

 Moderate — Some Filtering But Gaps,

whale_tracker,
Bug: Gate C always returns True. The regime gate logic has return True as the default path — it flags _regime_mismatch but never blocks. Dead code.,
Otherwise has decent sigma-based flow detection and volume normalization.,

extrinsic_flow,
Binary regime gate (LONG↔POSITIVE, SHORT↔NEGative) but only checks the label, not magnitude. Tiny net_gamma = 1.0 → "POSITIVE" → passes.,
phi_call_threshold: 3.0, phi_put_threshold: 0.3, phi_sigma_mult: 2.0 — solid phi-filtering otherwise.,

gamma_breaker,
Wall must be 2σ+ (min_wall_gex_sigma: 2.0), gamma break index > 0.05%, volume spike ≥1.5×. Solid design.,
Missing absolute net_gamma floor, but regime gate + wall proximity provides adequate filtering for a strategy focused on wall-break events.,

---

 Reasonable,

ghost_premium,
PDR > mean + 2σ, stability gate (|net_change| < 2%), volume > 0. Well-structured.,
net_gamma boosts confidence via normalization ceiling of 2000, doesn't gate. Fine for what it does (detects phantom/ghost options positioning).,

iv_band_breakout,
 (sub-agent labeled this #10 in their numbering)
Best-gated of all three. Explicit NEUTRAL block, graded POS(1.0)/NEG(0.8), delta snap ±10%, skew compression in bottom quartile, composite strength ≥0.30. Smart asymmetric targets by regime.,

---
Summary Classification

| Risk                              | Strategies                                                             | Issue                                      |
| --------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------ |
| 🔴 Won't fire (dead gate)         | iron_anchor ✅ fixed, gamma_volume_convergence, prob_distribution_shift | Threshold too high or parameter never read |
| 🔴 Blind firing (no gamma filter) | sentiment_sync, skew_dynamics, smile_dynamics, gex_divergence*         | Designed without gamma context             |
| 🟡 Weak/regime-only               | extrinsic_flow, ghost_premium, whale_tracker(bug)                      | Regime label checked but not magnitude     |
| ✅ OK                              | gamma_breaker, iv_band_breakout                                        | Adequate multi-gate structure              |

_*gexdivergence was in the original non-firing list but wasn't part of these 11 — already analyzed earlier.

The pattern is clear: half these strategies were built with options microstructure logic but no gamma regime awareness. That's not necessarily wrong if they're designed to work across all regimes, but combined with the broken thresholds, they'd generate noise that gets filtered later by the global engine — or worse, produce signals that lose money before anyone notices.
Your previous report was truncated after strategy #8 (whale_tracker). Please provide the complete analysis for only these three remaining strategies:

gamma_volume_convergence,
iv_band_breakout,
prob_distribution_shift,

Same format as before:
Gamma/GEX gates and numeric thresholds,
GEX/Wall proximity checks,
Flip zone / flip buffer,
Regime filters that block signals,
Config values,
Assessment of whether the gating is reasonable,

Search the same files you already read — just give me #9-11.
