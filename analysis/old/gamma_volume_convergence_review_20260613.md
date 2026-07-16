# Gamma-Volume Convergence Review — 2026-06-13

## Source: strategies/layer3/gamma_volume_convergence.py (~878 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `_check_aggressor_volume()` Gate requires VolumeUp or VolumeDown > 1.20× rolling avg, but the spike check uses BOTH volume_up AND volume_down comparison against vol_up.mean as baseline. For SHORT signals, volume_down should be compared against its own mean, not volume_up's mean. | Lines ~496-505 (spike threshold section) | Compare each direction against its own rolling average |
| info | `gex_calc.get_gamma_walls(threshold=500_000)` uses old-scale gamma wall threshold. With normalized max ~1600, this will never find walls. Both `_safe_get_walls` and confidence wall proximity return default values. | Line ~710 | Reduce threshold to 2000 or match normalized scale |
| info | `_coupling_score` for SHORT direction normalizes by dividing coupling by 3.0 — if gamma_accel = 0.10 (barely passing), delta_accel between 0.30-0.85 gives coupling of 1.5-7.0, always normalizing to 1.0. This means SHORT coupling is effectively a pass-through, never differentiating weak from strong signals. | Lines ~646-660 | Add direction-aware normalization ceiling |
| info | Wall proximity confidence in `_wall_proximity_confidence` uses absolute distance percentage capped at 2%. At typical intraday price movements, walls within 2% are common, giving mostly baseline 0.05-0.10 bonuses regardless of actual proximity. | Lines ~688-708 | Document expected wall frequency; consider dynamic threshold |
| info | ATR target clamping to [0.3%, 2.0%] of entry may override meaningful volatility signals during extreme moves. The clamp could produce targets that don't reflect actual market conditions. | Lines ~552-565 | Consider allowing wider targets when realized vol spikes |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Spike volume check cross-contaminates LONG/SHORT** — When checking SHORT, it compares current_volume_down against volume_up.mean (not volume_down.mean). If volume_up.mean ≠ volume_down.mean (common in trending markets), the spike gate fails unfairly for SHORT signals. | Lines ~496-505 | Fix to compare each direction against its OWN historical mean |
| medium | Signal_strength formula (`gamma*0.30 + vol*0.25 + coupling*0.20 + price*0.15 + delta*0.10`) has minimum 0.25 but individual hard gates already filter most scenarios. Combined effect: very few signals fire even when conditions are partially met. | Lines ~155-161 | Verify with backtest data; may need lower signal_strength threshold |
| medium | Delta acceleration ratio uses total_delta (sum across strikes) vs rolling average. With normalized gamma, total_delta might be small enough that the ratio becomes unstable (division near zero when rolling_avg → 0). Check for division-by-zero protection. | Lines ~622-636 | Ensure division-by-zero handling exists |
| medium | GAMMA_SPIKE_RATIO = 1.20 is defined but the code checks `gamma_accel < 0.05` directly instead of using the ratio. The named constant is dead code. | Line ~41 | Use GAMMA_SPIKE_RATIO or remove the constant |
| low | Price trend score only considers UP/DOWN/FLAT strings, not z-scores or change_pct magnitudes. A barely-UP signal scores same as strongly-UP. | Lines ~768-784 | Incorporate magnitude into trend scoring |
| info | Strategy expects greeks_summary but doesn't use it in evaluation (unlike other strategies). Only uses rolling_data windows and gex_calc methods. | evaluate() method | Either add greeks_summary usage or document why it's passed but unused |

### Combined Verdict: **FIX — Spike volume bug + dead constants**

Primary fix: correct volume spike comparison (use per-direction rolling mean). Secondary: remove/fix dead constants. The core logic is sound but these bugs prevent signals from firing under edge-case conditions.
