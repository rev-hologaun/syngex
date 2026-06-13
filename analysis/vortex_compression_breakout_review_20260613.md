# Vortex Compression Breakout Review — 2026-06-13

## Source: strategies/layer2/vortex_compression_breakout.py (~247 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | Gate A check `spread_z_score < -2.0` requires spread in bottom ~2.5% of distribution. For normal spread distributions, this is genuinely extreme compression. However, with normalized data, z-scores should already be properly standardized by RollingWindow.std(). If main.py computes raw spread z-scores differently (e.g., against wrong baseline), the -2.0 threshold may be misaligned. | Gate A logic | Verify z-score computation matches RollingWindow implementation |
| info | `normalize(abs(spread_z), 0.0, 4.0)` for compression depth component (c1). At z=-3 (compression deeper than required), contribution = min(1.0, 3/4) = 0.75. Good differentiation. This normalization scale looks correct. | Confidence c1 | No action needed |
| info | Volume spike threshold uses KEY_VOLUME_SPIKE_5M which maps to 900s window per ROLLING_WINDOW_SIZES. 15-minute volume history for a strategy designed for microstructure entries (seconds-to-minutes hold) may introduce lag. | Window config | Consider shorter window (300s) for faster adaptation |
| info | Spread widening velocity gate (Gate D) checks `current_spread > prev_spread * 1.5` (spreading ≥50%). Hard-coded in constants but not checked in current code body at visible offset — verify _gate_d method exists and applies correctly. | Gate D | Confirm gate implementation exists |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **"Spread widening velocity" concept needs clarification** — The "spring uncoiling" requires spread to expand AND volume surge simultaneously. But during genuine breakouts, spreads often WIDEN due to dealer hedging demand while volume comes from the trade flow itself. These are correlated but not identical phenomena. If spread widening and volume surge don't co-exist within the same time bucket, signal misses. | Spring uncoil logic | Consider sequential trigger: compression first (signal preparation), then EITHER widening OR volume surge (signal confirmation), rather than requiring both simultaneously |
| medium | Liquidity density threshold must confirm compression is "dense battleground" not "thin market." But how does the strategy measure liquidity density? If using total_depth × some factor, thin options markets may never achieve "high density" regardless of compression quality. | Density measurement | Verify density metric matches actual market depth scales; add fallback density estimation from order book level sizes |
| medium | VAMP validation component (component 6) checks that VAMP direction aligns with signal. This adds cross-strategy confirmation but also creates dependency: if VAMP doesn't populate its rolling windows correctly (e.g., missing vamm_levels data), VAMP score defaults to 0.0 or neutral, penalizing otherwise valid signals. | Cross-strategy dependency | Make VAMP validation soft-fallback (neutral score) rather than blocking when VAMP data unavailable |
| low | All four hard gates must pass + confidence floor ≥ MIN_CONFIDENCE. Combined filter stack makes this very selective strategy. With spread z < -2.0 AND density > threshold AND volume > 1.5× AND widening confirmed, firing rate will be extremely low. | Filter stacking | Accept as intentional high-precision design; document expected firing frequency |
| info | Clean, focused strategy with well-documented concept ("coiled spring"). Single responsibility — detect compression→breakout pattern. Much simpler architecture than layer2 peers like iv_gex_divergence. | Design simplicity | Good example of focused strategy design |

### Combined Verdict: **REVIEW — Sound concept, possibly over-filtered**

No critical bugs identified. Primary concern: simultaneous spread widening + volume surge requirement may be too tight. Secondary: verify all hard-gate implementations exist and match documented behavior. Strategy is clean and focused.
