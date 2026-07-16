# Syngex Strategy PNL Calculator Analysis
**Date:** 2026-06-30
**Total Strategies Analyzed:** 43

## Summary by Layer
| Layer | Count | Avg Stop% | Avg Target RR | Dynamic Stops |
|-------|-------|-----------|---------------|---------------|
| Layer 1 | 8 | ~0.5% | 1.75 | 8 |
| Layer 2 | 17 | ~0.5% | 1.75 | 6 |
| Layer 3 | 4 | ~0.5% | 2.00 | 2 |
| Full Data | 12 | ~0.5% | 1.70 | 0 |

## Layer 1 Strategies

### gex_imbalance (`gex_imbalance.py`)
> Append (ts, ratio) to history, capped at 20 entries.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - `TARGET_RISK_MULT` = 1.5
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - Rolling mean-based stop

### gamma_wall_bounce (`gamma_wall_bounce.py`)
> strategies/layer1/gamma_wall_bounce.py — Gamma Wall Bounce  Mean-reversion strategy: trade the rejection at high-GEX ...

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 1.5
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - Wall-based: `stop = wall_strike * (1 - STOP_PAST_WALL_PCT)`
- Wall-based: `stop = wall_strike * (1 + STOP_PAST_WALL_PCT)`

### gamma_flip_breakout (`gamma_flip_breakout.py`)
> SHORT fade: price rallied toward flip, expect rejection.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - ATR-normalized stop distance

### confluence_reversal (`confluence_reversal.py`)
> Build a SHORT signal from a resistance confluence level.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 2.0
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.008

### gex_divergence (`gex_divergence.py`)
> Calculate acceleration (2nd derivative) for a rolling window.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - `TARGET_RISK_MULT` = 1.5
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.005

### magnet_accelerate (`magnet_accelerate.py`)
> strategies/layer1/magnet_accelerate.py — Magnet & Accelerate  Two-phase strategy centered on the highest-GEX strike (...

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 1.5
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `TRAIL_STOP_PCT` = 0.01
- Trailing stop: `TRAIL_STOP_PCT`
- Rolling mean-based stop

### vol_compression_range (`vol_compression_range.py`)
> Get the best available price rolling window.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 1.5
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.006

### gamma_squeeze (`gamma_squeeze.py`)
> strategies/layer1/gamma_squeeze.py — Gamma Squeeze / Wall-Breaker v2 (Squeeze-Force)  Pin detection + breakout throug...

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 2.0
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - Liquidity-aware: `self._liquidity_aware_stop()`

## Layer 2 Strategies

### exchange_flow_imbalance (`exchange_flow_imbalance.py`)
> strategies/layer2/exchange_flow_imbalance.py — Exchange Flow Imbalance  Venue-specific order book imbalance strategy....

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### depth_imbalance_momentum (`depth_imbalance_momentum.py`)
> strategies/layer2/depth_imbalance_momentum.py — Depth Imbalance Momentum  Pressure-tracking engine that monitors stru...

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### depth_decay_momentum (`depth_decay_momentum.py`)
> strategies/layer2/depth_decay_momentum.py — Depth Decay Momentum  Liquidity evaporation detection strategy (bidirecti...

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### participant_divergence_scalper (`participant_divergence_scalper.py`)
> Get current spread from rolling data.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### exchange_flow_concentration (`exchange_flow_concentration.py`)
> strategies/layer2/exchange_flow_concentration.py — Exchange Flow Concentration  Venue-specific flow concentration str...

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### participant_diversity_conviction (`participant_diversity_conviction.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### delta_gamma_squeeze (`delta_gamma_squeeze.py`)
> Evaluate a specific wall for squeeze setup.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 2.0
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - Dynamic: uses `effective_stop_pct` (IV-adjusted)

### delta_iv_divergence (`delta_iv_divergence.py`)
> Evaluate current state for delta-IV divergence.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_IV_MULT` = 2.0
- Rolling mean-based target
- IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.008
- Percentage: `stop = entry * (1 - STOP_PCT)` for LONG

### call_put_flow_asymmetry (`call_put_flow_asymmetry.py`)
> Evaluate call-dominant flow for LONG signal.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 2.0
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.006
- Percentage: `stop = entry * (1 - STOP_PCT)` for LONG
- Percentage: `stop = entry * (1 + STOP_PCT)` for SHORT

### delta_volume_exhaustion (`delta_volume_exhaustion.py`)
> Return a 0.0-1.0 score for delta decline strength.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `NEGATIVE_GAMMA_TARGET_MULT` = 1.5
- `POSITIVE_GAMMA_TARGET_MULT` = 0.8
- `NEUTRAL_GAMMA_TARGET_MULT` = 1.0
- Rolling mean-based target
- IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.008

### exchange_flow_asymmetry (`exchange_flow_asymmetry.py`)
> strategies/layer2/exchange_flow_asymmetry.py — Exchange Flow Asymmetry  Venue-signature tracking strategy. MEMX is th...

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### obi_aggression_flow (`obi_aggression_flow.py`)
> strategies/layer2/obi_aggression_flow.py — OBI + Aggression Flow  Order Book Imbalance + Aggressive Trade Flow strate...

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### order_book_stacking (`order_book_stacking.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### vortex_compression_breakout (`vortex_compression_breakout.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### iv_gex_divergence (`iv_gex_divergence.py`)
> Check if price is at a high in the 30m rolling window.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 1.5
- Rolling mean-based target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.006
- `FALLBACK_STOP_PCT` = 0.006

### order_book_fragmentation (`order_book_fragmentation.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### vamp_momentum (`vamp_momentum.py`)
> strategies/layer2/vamp_momentum.py — VAMP Momentum  Volume-Adjusted Mid-Price Momentum strategy (bidirectional). Dete...

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

## Layer 3 Strategies

### strike_concentration (`strike_concentration.py`)
> Check if current volume exceeds rolling average by ≥20%.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 1.5
- ATR-normalized: scaled by current ATR / mean ATR ratio
- Risk-multiplication: `target = entry + risk * MULT` (LONG)
- Risk-multiplication: `target = entry - risk * MULT` (SHORT)
- Rolling mean-based target
- IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT_BOUNCE` = 0.003
- `STOP_PCT_SLICE` = 0.003
- Percentage: `stop = entry * (1 - STOP_PCT)` for LONG
- Percentage: `stop = entry * (1 + STOP_PCT)` for SHORT

### theta_burn (`theta_burn.py`)
> POSITIVE gamma regime: trade wall bounces.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - Wall-based: `stop = wall_strike * (1 - STOP_PAST_WALL_PCT)`
- Wall-based: `stop = wall_strike * (1 + STOP_PAST_WALL_PCT)`

### gamma_volume_convergence (`gamma_volume_convergence.py`)
> Get the nearest ATM strike from the GEX calculator.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - ATR-normalized: scaled by current ATR / mean ATR ratio
- Rolling mean-based target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.005
- Percentage: `stop = entry * (1 - STOP_PCT)` for LONG
- Percentage: `stop = entry * (1 + STOP_PCT)` for SHORT
- ATR-normalized stop distance

### iv_band_breakout (`iv_band_breakout.py`)
> Price compression confidence: 0.0–0.10. Tighter = higher. Data-not-available = neutral.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `POSITIVE_GAMMA_TARGET_MULT` = 2.5
- `NEGATIVE_GAMMA_TARGET_MULT` = 1.5
- `TARGET_IV_EXPANSION_MULT` = 2.5
- `TARGET_IV_EXPANSION_NEG_MULT` = 1.5
- `TARGET_IV_EXPANSION_CAP` = 4.0
- Risk-multiplication: `target = entry + risk * MULT` (LONG)
- Risk-multiplication: `target = entry - risk * MULT` (SHORT)
- Percentage: `target = entry * (1 + PCT)`
- IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.005
- Percentage: `stop = entry * (1 - STOP_PCT)` for LONG
- Percentage: `stop = entry * (1 + STOP_PCT)` for SHORT

## Full Data Strategies

### skew_dynamics (`skew_dynamics.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### extrinsic_flow (`extrinsic_flow.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### iv_skew_squeeze (`iv_skew_squeeze.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_IV_EXPANSION_MULT` = 1.6
- `TARGET_IV_EXPANSION_CAP` = 2.0
- Risk-multiplication: `target = entry + risk * MULT` (LONG)
- Risk-multiplication: `target = entry - risk * MULT` (SHORT)
- Rolling mean-based target
- IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.005

### sentiment_sync (`sentiment_sync.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### prob_weighted_magnet (`prob_weighted_magnet.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - `TARGET_RISK_MULT` = 1.5
- `TARGET_MULT_CAP` = 3.0
- Rolling mean-based target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.005

### extrinsic_intrinsic_flow (`extrinsic_intrinsic_flow.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current price (`entry = price`)
- **Target Price:** - Risk-multiplication: `target = entry + risk * MULT` (LONG)
- Risk-multiplication: `target = entry - risk * MULT` (SHORT)
- Percentage: `target = entry * (1 + PCT)`
- Rolling mean-based target
- IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.005

### prob_distribution_shift (`prob_distribution_shift.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Risk-multiplication: `target = entry + risk * MULT` (LONG)
- Risk-multiplication: `target = entry - risk * MULT` (SHORT)
- Percentage: `target = entry * (1 + PCT)`
- Rolling mean-based target
- IV-scaled target
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.005

### smile_dynamics (`smile_dynamics.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### iron_anchor (`iron_anchor.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### whale_tracker (`whale_tracker.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### ghost_premium (`ghost_premium.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - `TARGET_RISK_MULT` = 2.0
- Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- Risk-reward ratio tracked in signal metadata
- **Stop Loss:** - `STOP_PCT` = 0.005
- Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

### gamma_breaker (`gamma_breaker.py`)
> Normalize a value to [0, 1] given a min/max range.

- **Entry Price:** Set to current underlying price (`entry = underlying_price`)
- **Target Price:** - Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)
- Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)
- **Stop Loss:** - Distance-based: `stop = entry - stop_distance` (LONG)
- Distance-based: `stop = entry + stop_distance` (SHORT)

## Infrastructure / Utility Modules

These modules do not calculate prices directly:

- **analyzer.py**: Analysis utilities — helper functions for data analysis and metric computation
- **engine.py**: Strategy orchestrator — manages strategy lifecycle, delegates to strategy subclasses
- **metrics.py**: Metrics collection — aggregates and reports performance metrics
- **rolling_keys.py**: Rolling window key constants — standardized keys for price, volume, ATR, etc.
- **rolling_window.py**: RollingWindow data structure — maintains sliding windows of numeric data with stats
- **signal.py**: Signal dataclass definition — Direction enum and Signal dataclass for strategy outputs
- **signal_tracker.py**: Signal tracking — manages signal history and state across evaluation cycles
- **volume_filter.py**: Volume filtering — filters signals based on volume thresholds and patterns
