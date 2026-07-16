# Iron Anchor Review — 2026-06-13

## Source: strategies/full_data/iron_anchor.py (~363 lines)

---

## Forge Code Review

| Severity | Issue | Location | Suggested Fix |
|----------|-------|----------|---------------|
| warning | `normalize(current_liq_size, 0.0, 1000000.0)` — liquidity wall sizes are raw contract counts or dollar values that can easily exceed 1M on high-volume days. Normalizing against 1M ceiling means large walls (1M+) always cap at confidence contribution 1.0, losing differentiation between massive and extreme walls. | Line ~355 | Increase vmax or use log-scale normalization |
| info | Gate B `_gate_b_gamma_density` uses `min_gamma_wall_gex = params.get(..., 500000)` default. If greeks_summary doesn't populate per-strike gamma values meeting this threshold, gate B fails silently. The threshold matches old cumulative scales. | Lines ~164-170 | Reduce to 5000 or verify normalized gamma wall scale |
| info | Both current_velocity and avg_velocity from PRICE_VELOCITY_5M window use same data source. Since velocity is typically small (% change), averaging vs latest may not differentiate well. | Lines ~118-120 | Consider using rolling median instead of mean for robustness |
| info | Confluence proximity check `if current_prox > max_confluence_distance` defaults to $1.00. At $500+ stock price, this is <0.2% — extremely tight. Most gamma/liquidity walls won't align within $1 unless both are coincidentally near the same strike. | Line ~116 | Consider scaling proximity to price percentage instead of absolute dollar amount |

## Synapse Analytical Review

| Severity | Finding | Detail | Recommendation |
|----------|---------|--------|----------------|
| high | **Proximity threshold is absolute $, not %** — `max_confluence_distance = 1.0` means gamma wall must be within $1.0 of liquidity wall. For a $500 stock, this is 0.2%; for $50, it's 2%. High-priced stocks will almost never fire this strategy. Switch to percentage-based proximity. | Logic ~116 | Change to percentage: e.g., `prox_pct > max_prox_pct` where prox_pct = distance / price |
| medium | Gamma density gate checks per-strike gamma (from greeks_summary), but if net_gamma has been normalized from millions to ~1600, individual strike gammas will also be scaled down. A 500000 threshold would need to be proportionally reduced. | _gate_b_gamma_density method | Scale gamma wall thresholds proportionally |
| medium | The "exhaustion" concept (velocity decreasing as approaching confluence) is good in theory but uses raw velocity comparison against itself (current vs average). Without normalization by recent volatility, "decreasing" is relative to whatever the baseline was, not relative to current market conditions. | Lines ~118-120, ~177-182 | Normalize velocity decrease by recent volatility std |
| medium | Only fires when BOTH gamma wall AND liquidity wall exist within $1.0. Dual-wall confluence events are genuinely rare. Strategy design is correct but inherently low-frequency. May be OK if signals are high-quality. | Overall logic | Accept low frequency as feature; focus on signal quality rather than firing rate |
| low | Intensity classification only has basic logic based on proximity — no multi-level intensity like other strategies (yellow/orange/red). Simpler than peers. | Confidence output | Add intensity levels for consistency |
| info | Strategy requires `greeks_summary` dict populated by main.py. Missing or empty summary → early return. Ensure this field is consistently provided. | evaluate() method | Verify main.py populates greeks_summary before strategy evaluation |

### Combined Verdict: **FIX — Dollar-based proximity blocks high-priced stocks**

Primary fix: convert $1.00 proximity to % proximity (e.g., 0.2%). Secondary: verify gamma wall thresholds match normalized scale. This is a fundamentally sound strategy that just needs parameter calibration.
