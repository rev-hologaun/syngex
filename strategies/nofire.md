# Strategies That Did Not Fire — TSLA Full Day (2026-05-13)

**Analysis date:** 2026-05-13  
**Symbol:** TSLA  
**Data period:** Full trading day  
**Total strategies defined:** 40 (39 strategies + 1 regime filter)  
**Strategies that fired:** 11  
**Strategies that did NOT fire:** 29

---

## Fired Strategies (for reference)

| # | Strategy | Layer |
|---|----------|-------|
| 1 | `gamma_wall_bounce` | layer1 |
| 2 | `magnet_accelerate` | layer1 |
| 3 | `gamma_flip_breakout` | layer1 |
| 4 | `gamma_squeeze` | layer1 |
| 5 | `gex_divergence` | layer1 |
| 6 | `vol_compression_range` | layer1 |
| 7 | `depth_decay_momentum` | layer2 |
| 8 | `exchange_flow_asymmetry` | layer2 |
| 9 | `exchange_flow_concentration` | layer2 |
| 10 | `exchange_flow_imbalance` | layer2 |
| 11 | `strike_concentration` | layer3 |

---

## Non-Firing Strategies (by Layer)

### Layer 1 — GEX / Wall / Structure (3 strategies)

#### 1. `confluence_reversal`
- **File:** `strategies/layer1/confluence_reversal.py`
- **Concept:** Reversal when price hits a GEX wall AND a technical level (rolling max/min) AND/OR VWAP simultaneously.
- **Why it might not fire:** Requires structural + technical confluence. TSLA may not have had price action aligning both wall proximity AND a technical level within 0.3%.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `CONFLUENCE_DISTANCE_PCT` | `0.003` | Max distance for confluence (0.3%) |
  | `MIN_STRUCTURAL_SIGNALS` | `1` | Min structural signals needed |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `STOP_PCT` | `0.008` | Stop distance (0.8%) |
  | `TARGET_RISK_MULT` | `2.0` | Target = risk × 2 |
  | `VELOCITY_MIN_ZSCORE` | `1.0` | Min |z-score| for approach velocity |
  | `VELOCITY_MIN_VOLUME_MULT` | `1.2` | Volume must be ≥ 1.2× rolling avg |
  | `IV_WEIGHT_BASE` | `1.0` | Base IV weight |
  | `IV_WEIGHT_MAX` | `1.5` | Max IV weight |
  | `IV_WEIGHT_SKEW_THRESHOLD` | `0.05` | IV skew threshold for weight |
  | `DEPTH_SPIKE_THRESHOLD` | `1.5` | Current depth ≥ 1.5× rolling avg |
  | `NEGATIVE_GAMMA_STOP_MULT` | `1.5` | Wider stops in NEG gamma |
  | `POSITIVE_GAMMA_STOP_MULT` | `0.75` | Tighter stops in POS gamma |

#### 2. `gex_imbalance`
- **File:** `strategies/layer1/gex_imbalance.py`
- **Concept:** Trade based on call/put GEX ratio extremes. Long when put-heavy, short when call-heavy.
- **Why it might not fire:** Requires extreme GEX ratio (call/put < 0.5 for long, > 0.65 for short) AND sufficient message count (20+) AND ratio ROC (10% change). TSLA may have had balanced GEX.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `PUT_HEAVY_RATIO` | `0.5` | < 0.5 → long bias |
  | `CALL_HEAVY_RATIO` | `0.65` | > 0.65 → short bias |
  | `STRONG_PUT_RATIO` | `0.25` | Very strong long signal |
  | `STRONG_CALL_RATIO` | `0.75` | Very strong short signal |
  | `MIN_MESSAGES` | `20` | Min data points for signal quality |
  | `STOP_VOL_MULT` | `2.5` | Stop = 2.5× rolling price std |
  | `TARGET_RISK_MULT` | `1.5` | Target = 1.5× stop distance |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `RATIO_ROC_WINDOW` | `5` | Ticks back for ROC |
  | `RATIO_ROC_THRESHOLD` | `0.10` | Min ROC to trigger (10%) |
  | `REGIME_GAMMA_THRESHOLD` | `500000` | Gamma threshold for regime |
  | `VWAP_DEVIATION_MIN_STD` | `1.5` | Min VWAP deviation in std |

#### 3. `vol_compression_range`
- **File:** `strategies/layer1/vol_compression_range.py`
- **Concept:** Range-bound trading when volatility compresses — price oscillates in a tight range before breakout.
- **Why it might not fire:** TSLA may not have exhibited sufficient volatility compression. Requires specific range contraction patterns.
- **Adjustable parameters:** *(check source for exact values)*

---

### Layer 2 — Flow / Depth / Participant (12 strategies)

#### 4. `call_put_flow_asymmetry`
- **File:** `strategies/layer2/call_put_flow_asymmetry.py`
- **Concept:** Tracks call vs put option flow scoring. When call flow significantly exceeds put flow (or vice versa), signals directional bias.
- **Why it might not fire:** Requires flow ratio > 1.5× AND minimum 3 Greeks points. TSLA options flow may have been balanced.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `FLOW_THRESHOLD` | `1.5` | Call score must exceed put score by 1.5× |
  | `MIN_GREEKS_POINTS` | `3` | Min Greeks points for signal |
  | `IV_SKEW_THRESHOLD` | `0.03` | 3% IV difference for alignment |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `STOP_PCT` | `0.006` | 0.6% stop |
  | `TARGET_RISK_MULT` | `2.0` | Target = risk × 2 |

#### 5. `delta_gamma_squeeze`
- **File:** `strategies/layer2/delta_gamma_squeeze.py`
- **Concept:** Detects gamma squeeze conditions where delta acceleration + gamma concentration + volume spike align.
- **Why it might not fire:** Requires delta acceleration ratio ≥ 1.10, volume spike ≥ 1.2×, and wall GEX ≥ 500k simultaneously. Tight multi-condition gate.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `WALL_PROXIMITY_PCT` | `0.03` | Must be within 3% of wall |
  | `DELTA_ACCEL_RATIO` | `1.10` | Delta must accelerate ≥ 10% |
  | `VOLUME_SPIKE_RATIO` | `1.20` | Volume ≥ 1.2× rolling avg |
  | `MIN_WALL_GEX` | `500000` | Min wall GEX |
  | `PRICE_ABOVE_MEAN_CONFIDENCE` | `0.55` | Price in upper half of 5m window |
  | `MIN_DATA_POINTS` | `3` | Min data points |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `STOP_BELOW_WALL_PCT` | `0.008` | 0.8% below entry |
  | `TARGET_RISK_MULT` | `2.0` | Target = risk × 2 |
  | `GEX_ACCEL_RATIO` | `1.10` | GEX acceleration threshold |
  | `DELTA_ACCEL_MIN` | `1.05` | Min delta acceleration |
  | `GEX_ACCEL_MIN` | `1.05` | Min GEX acceleration |
  | `LIQUIDITY_VACUUM_DEPTH_RATIO` | `0.8` | Depth ratio for vacuum |
  | `IV_ROC_THRESHOLD` | `0.02` | IV ROC threshold |
  | `ACCEL_STOP_WIDEN_MULT` | `1.5` | Widen stop for acceleration |

#### 6. `delta_iv_divergence`
- **File:** `strategies/layer2/delta_iv_divergence.py`
- **Concept:** Detects divergence between delta trend and IV trend. When delta and IV move in opposite directions, signals mean reversion.
- **Why it might not fire:** Requires skew divergence + decoupling + gamma decline all passing simultaneously. Very strict multi-gate.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_DATA_POINTS` | `5` | Min data points |
  | `MIN_DIVERSION_STRENGTH` | `0.3` | Min divergence strength |
  | `STOP_PCT` | `0.008` | 0.8% stop |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `SK_DIV_THRESHOLD` | `0.10` | Skew divergence threshold |
  | `DECOUPLE_HISTORY_WINDOW` | `30` | History window for decoupling |
  | `DECOUPLE_THRESHOLD` | `0.50` | Decoupling threshold |
  | `GAMMA_DECLINE_THRESHOLD` | `0.70` | Gamma must decline ≥ 30% |
  | `TARGET_IV_MULT` | `2.0` | Base IV target multiplier |
  | `TARGET_IV_CAP` | `4.0` | Cap on IV target |
  | `WALL_PROX_PCT` | `0.01` | Wall proximity threshold |
  | `WALL_PROX_BONUS` | `0.10` | Confidence bonus for wall proximity |

#### 7. `delta_volume_exhaustion`
- **File:** `strategies/layer2/delta_volume_exhaustion.py`
- **Concept:** Detects volume exhaustion in trending moves — delta declining while volume confirms, signaling trend reversal.
- **Why it might not fire:** Requires delta decline + liquidity vacuum + IV acceleration alignment. Multiple hard gates.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_TREND_POINTS` | `5` | Min trend data points |
  | `MIN_GREEKS_POINTS` | `5` | Min Greeks points |
  | `DELTA_DECLINE_RATIO` | `0.95` | Delta below 95% of rolling avg |
  | `MIN_TREND_DURATION` | `2` | Min candles in trend |
  | `STOP_PCT` | `0.008` | 0.8% beyond swing |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MEAN_REVERSION_MULT` | `1.0` | Target = 1.0× distance to mean |
  | `LIQUIDITY_VACUUM_RATIO_STABILITY` | `0.15` | Ratio must be within 15% of rolling mean |
  | `LIQUIDITY_VACUUM_SPREAD_WIDEN_MULT` | `1.2` | Spread must be > 1.2× rolling mean |
  | `IV_ACCEL_WINDOW` | `5` | Window for IV ROC |
  | `IV_ACCEL_BONUS` | `0.15` | Confidence bonus when IV aligns |
  | `WALL_PROXIMITY_PCT` | `0.003` | Within 0.3% of wall |
  | `WALL_PROXIMITY_BONUS` | `0.10` | Confidence bonus |
  | `NEGATIVE_GAMMA_TARGET_MULT` | `1.5` | NEG regime: let it run |
  | `POSITIVE_GAMMA_TARGET_MULT` | `0.8` | POS regime: quick profits |
  | `NEUTRAL_GAMMA_TARGET_MULT` | `1.0` | Baseline |
  | `GAMMA_INTENSITY_THRESHOLD` | `500000` | Threshold for regime classification |

#### 8. `depth_imbalance_momentum`
- **File:** `strategies/layer2/depth_imbalance_momentum.py`
- **Concept:** Pressure-tracking engine monitoring bid/ask depth structural weight. When bid side becomes massively larger than ask (or vice versa), creates gravitational pressure. Combined with ROC, detects accelerating pressure.
- **Signal types:** LONG: IR > 3.0 (heavy bid) AND ROC > 0. SHORT: IR < 0.6 (heavy ask) AND ROC < 0.
- **Hard gates (all must pass):** Gate A: avg participants ≥ 2.0, Gate B: total depth not evaporating (max decay 5%), Gate C: volume ≥ MA(volume).
- **Why it might not fire:** Requires IR > 3.0 or < 0.6 (very extreme imbalance) AND ROC alignment AND participant conviction AND depth stability AND volume confirmation. IR threshold of 3.0 is extremely high — most normal order books won't reach it.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_ir_data_points` | `10` | Min IR data points for signal |
  | `ir_threshold_long` | `3.0` | IR must exceed 3.0 for LONG signal (very extreme) |
  | `ir_threshold_short` | `0.6` | IR must drop below 0.6 for SHORT signal |
  | `ir_roc_threshold_long` | `0.0` | Min IR ROC for LONG |
  | `ir_roc_threshold_short` | `0.0` | Min IR ROC for SHORT |
  | `min_avg_participants` | `2.0` | Min avg participants per level (Gate A) |
  | `max_total_depth_decay` | `0.05` | Max depth decay rate 5% (Gate B) |
  | `volume_min_mult` | `1.0` | Volume must be ≥ 1.0× MA (Gate C) |
  | `use_vamp_validation` | `True` | Enable VAMP validation gate |
  | `stop_pct` | `0.008` | 0.8% stop distance |
  | `target_risk_mult` | `2.0` | Target = risk × 2 |

#### 9. `obi_aggression_flow`
- **File:** `strategies/layer2/obi_aggression_flow.py`
- **Concept:** Combines Order Book Imbalance (passive book skew) with Aggression Flow (active trade execution). Only enters when BOTH passive book AND active trades agree on direction — filters out spoofing and passive walls that never get tested.
- **Signal types:** LONG: OBI > 0.75 (bid-heavy book) AND AF > 0.5 (buy aggression). SHORT: OBI < -0.75 (ask-heavy book) AND AF < -0.5 (sell aggression).
- **Hard gates (all must pass):** Gate A: latest trade size > 2.0× MA(trade_size), Gate B: avg participants ≥ 1.0, Gate C: current spread < 1.5× MA(spread).
- **Why it might not fire:** Requires BOTH OBI > 0.75 AND AF > 0.5 simultaneously (or both negative for SHORT). These are independent metrics that rarely agree. Gate A requires a trade size spike — if no aggressive trades occurred, this fails.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `obi_threshold` | `0.75` | OBI must exceed 0.75 for LONG (or < -0.75 for SHORT) |
  | `af_threshold` | `0.5` | AF must exceed 0.5 for LONG (or < -0.5 for SHORT) |
  | `min_obi_data_points` | `10` | Min OBI data points |
  | `min_af_data_points` | `5` | Min AF data points |
  | `volume_spike_mult` | `2.0` | Latest trade must be > 2.0× MA (Gate A) |
  | `min_avg_participants` | `1.0` | Min avg participants (Gate B) |
  | `max_spread_multiplier` | `1.5` | Spread < 1.5× MA (Gate C) |
  | `stop_pct` | `0.005` | 0.5% stop distance |
  | `target_risk_mult` | `1.5` | Target = risk × 1.5 |

#### 10. `order_book_fragmentation`
- **File:** `strategies/layer2/order_book_fragmentation.py`
- **Concept:** Structural integrity strategy distinguishing fragile "spoof" walls (massive size, few participants) from robust "anchor" walls (massive size, many participants across exchanges). Trades both spoof breaches (fake walls evaporating) and robust bounces (real walls holding).
- **Signal types:** SPOOF BREACH LONG: fragile ask wall evaporates → breakout. SPOOF BREACH SHORT: fragile bid wall evaporates → breakdown. ROBUST BOUNCE LONG: robust bid wall holds → bounce. ROBUST BOUNCE SHORT: robust ask wall holds → rejection.
- **Hard gates (all must pass):** Gate A: wall size ≥ 3× average level size, Gate B: VAMP deviation confirms price movement ("Void" check), Gate C: vol/depth ratio matches signal type (< 0.1 for spoof, > 0.5 for robust), Gate D: spread < 2.0× average spread.
- **Why it might not fire:** Requires fragility AND decay threshold to align (4 signal conditions), plus 4 hard gates. The fragility/decay thresholds (frag > 0.5 AND decay < -0.1 for spoof) are strict. Also requires 5+ data points in ALL 4 rolling windows (fragility bid/ask, decay bid/ask).
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `frag_threshold` | `0.5` | Fragility threshold (spoof if > 0.5, robust if < 0.5) |
  | `decay_threshold` | `-0.1` | Decay velocity threshold (negative = evaporating) |
  | `wall_significance_mult` | `3.0` | Wall must be ≥ 3× avg level size (Gate A) |
  | `price_proximity_pct` | `0.001` | Price proximity threshold (0.1%) |
  | `vol_ratio_spoof` | `0.1` | Vol/depth ratio < 0.1 for spoof breach (Gate C) |
  | `vol_ratio_robust` | `0.5` | Vol/depth ratio > 0.5 for robust bounce (Gate C) |
  | `max_spread_mult` | `2.0` | Spread < 2.0× avg spread (Gate D) |
  | `stop_pct` | `0.003` | 0.3% stop distance |
  | `target_risk_mult` | `3.0` | Target = risk × 3 |

#### 11. `order_book_stacking`
- **File:** `strategies/layer2/order_book_stacking.py`
- **Concept:** Structural concentration strategy detecting anomalous order book walls using Stack Intensity Score (SIS). A "stack" is a level whose size significantly exceeds the recent average level size. Trades bounces off real stacks and breakouts when they collapse.
- **Signal types:** STACK_BOUNCE LONG: massive bid stack holds → scalp bounce. STACK_BREACH SHORT: massive ask stack eaten → scalp breakout. STACK_BOUNCE SHORT: massive ask stack holds → scalp rejection. STACK_BREACH LONG: massive bid stack evaporates → scalp breakdown.
- **Hard gates (all must pass):** Gate A: stack size ≥ 3× average level size, Gate B: ≥ 2 unique participants (anti-spoof), Gate C: vol/depth ratio confirms real consumption for breach signals, Gate D: spread < 2.0× average spread.
- **Why it might not fire:** Requires SIS > 4.0 (very high intensity) AND ROC < -0.5 for breach signals. Gate B needs ≥ 2 unique participants (anti-spoof). Also requires 10+ data points for SIS windows. The combination of high SIS + decay + participants + spread gates is very restrictive.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_data_points` | `10` | Min data points for SIS windows |
  | `sis_threshold` | `4.0` | SIS must exceed 4.0 for stack detection |
  | `magnitude_factor` | `3.0` | Stack must be ≥ 3× avg level size (Gate A) |
  | `min_participants` | `2` | Min unique participants (Gate B) |
  | `price_tolerance` | `0.001` | Price proximity tolerance (0.1%) |
  | `roc_threshold` | `-0.5` | ROC must be < -0.5 for breach signals |
  | `vol_ratio_breach` | `0.15` | Vol/depth ≥ 0.15 for breach signals (Gate C) |
  | `max_spread_mult` | `2.0` | Spread < 2.0× avg spread (Gate D) |
  | `stop_pct` | `0.003` | 0.3% stop distance |
  | `target_risk_mult` | `3.0` | Target = risk × 3 |

#### 12. `participant_divergence_scalper`
- **File:** `strategies/layer2/participant_divergence_scalper.py`
- **Concept:** Microstructure scalping strategy distinguishing fragile "spoof" walls (massive size, few participants) from robust multi-participant liquidity. Trades both spoof breaches (fake walls collapsing) and robust bounces (real walls holding).
- **Signal types:** SPOOF BREACH SHORT: fragile ask wall evaporates → scalp vacuum. SPOOF BREACH LONG: fragile bid wall evaporates → scalp vacuum. ROBUST BOUNCE LONG: robust bid wall holds → scalp bounce. ROBUST BOUNCE SHORT: robust ask wall holds → scalp bounce.
- **Hard gates (all must pass):** Gate A: wall size ≥ 5× average level size, Gate B: vol_ratio matches signal type (< 0.1 for spoof, > 0.5 for robust), Gate C: spread < 2.0× average spread, Gate D: VAMP validation (direction alignment).
- **Why it might not fire:** Requires fragility AND decay to align simultaneously (4 signal conditions), plus 4 hard gates. Gate A uses 5× multiplier (stricter than order_book_fragmentation's 3×). Also requires 10+ data points in fragility windows AND 5+ in decay windows. The VAMP validation gate adds another filter.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `fragility_window` | `5` | Rolling window size for fragility |
  | `min_frag_data_points` | `10` | Min data points for fragility windows |
  | `fragility_threshold` | `0.5` | Fragility threshold (spoof if > 0.5) |
  | `robust_threshold` | `0.3` | Robustness threshold (robust if < 0.3) |
  | `decay_velocity_threshold` | `0.0` | Decay velocity threshold |
  | `vol_ratio_spoof` | `0.1` | Vol/depth < 0.1 for spoof (Gate B) |
  | `vol_ratio_robust` | `0.5` | Vol/depth > 0.5 for robust (Gate B) |
  | `max_spread_mult` | `2.0` | Spread < 2.0× avg spread (Gate C) |
  | `wall_size_mult` | `5.0` | Wall ≥ 5× avg level size (Gate A, stricter than obs) |
  | `use_vamp_validation` | `True` | Enable VAMP direction validation (Gate D) |
  | `stop_pct` | `0.003` | 0.3% stop distance |
  | `target_risk_mult` | `1.5` | Target = risk × 1.5 |

#### 13. `participant_diversity_conviction`
- **File:** `strategies/layer2/participant_diversity_conviction.py`
- **Concept:** Measures institutional conviction by analyzing intra-level diversity (participants per price level) and inter-exchange diversity (unique exchanges per level). A wall with 4 participants across 3 exchanges = high conviction (institutional). A wall with 1 participant = likely spoofed.
- **Signal types:** LONG: bid_participants ≥ 3 AND bid_exchanges ≥ 2 AND conviction_score > 0.7 AND price breaks recent high. SHORT: ask_participants ≥ 3 AND ask_exchanges ≥ 2 AND conviction_score > 0.7 AND price breaks recent low.
- **Hard gates (all must pass):** Gate A: avg_participants ≥ min_participants (already checked in signal detection), Gate B: num_exchanges ≥ min_exchanges (already checked), Gate C: current_depth_size ≥ min_size_ratio × MA(size), Gate D: VAMP validation (direction alignment).
- **Why it might not fire:** Requires 4 separate rolling windows (bid_participants, ask_participants, bid_exchanges, ask_exchanges) all with ≥ 10 data points. Also requires conviction_score > 0.7 (product of participant_score × exchange_score). Then adds price breakout/breakdown confirmation AND size ratio gate AND VAMP validation. The conviction_threshold of 0.7 is high — both participant and exchange scores must be strong simultaneously.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_data_points` | `10` | Min data points for all 4 rolling windows |
  | `min_participants` | `3.0` | Min avg participants per side (LONG: bid, SHORT: ask) |
  | `min_exchanges` | `2` | Min unique exchanges per side |
  | `conviction_threshold` | `0.7` | Conviction score must exceed (participant_score × exchange_score) |
  | `max_participants_norm` | `5.0` | Max participants for confidence normalization |
  | `max_exchanges_norm` | `4.0` | Max exchanges for confidence normalization |
  | `min_size_ratio` | `0.5` | Current depth must be ≥ 0.5× MA(size) (Gate C) |
  | `use_vamp_validation` | `True` | Enable VAMP direction validation (Gate D) |
  | `stop_pct` | `0.008` | 0.8% stop distance |
  | `target_risk_mult` | `2.0` | Target = risk × 2 |

#### 14. `vamp_momentum`
- **File:** `strategies/layer2/vamp_momentum.py`
- **Concept:** Volume-Adjusted Mid-Price Momentum. Computes VAMP = Σ(price × size) / Σ(size) over top 10 bid/ask levels. When VAMP deviates from mid-price, reveals bid/ask weight bias — often before L1 price reacts. LONG: Δ_VAMP > threshold AND ROC > 0. SHORT: Δ_VAMP < -threshold AND ROC < 0.
- **Hard gates (all must pass):** Gate A: avg participants over top 10 ≥ min_avg_participants, Gate B: Σ size(top 10) > MA(total depth, 60s) × liquidity_density_min_mult, Gate C: current spread < MA(spread, 5m).
- **Why it might not fire:** Requires VAMP deviation > 0.05% AND ROC > 0 (for LONG) or VAMP deviation < -0.05% AND ROC < 0 (for SHORT). Gate C requires current spread < MA(spread) — if spread is wider than average, this fails immediately. Also requires participant conviction (≥ 1.5) AND liquidity density (top 10 size > 1.2× MA). All 3 gates must pass.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `vamp_roc_window` | `5` | Rolling window for VAMP ROC calculation |
  | `min_avg_participants` | `1.5` | Min avg participants (Gate A) |
  | `liquidity_density_min_mult` | `1.2` | Top 10 size > 1.2× MA depth (Gate B) |
  | `depth_ma_window_seconds` | `60` | MA window for depth (Gate B) |
  | `spread_stability_ma_seconds` | `300` | MA window for spread (Gate C) |
  | `vamp_mid_dev_threshold` | `0.0005` | VAMP deviation threshold (0.05%) |
  | `vamp_roc_threshold` | `0.0` | ROC threshold (must be > 0 for LONG, < 0 for SHORT) |
  | `stop_pct` | `0.005` | 0.5% stop distance |
  | `target_risk_mult` | `1.5` | Target = risk × 1.5 |

#### 15. `vortex_compression_breakout`
- **File:** `strategies/layer2/vortex_compression_breakout.py`
- **Concept:** Detects compression in the vortex indicator (spread + liquidity + volume) followed by breakout.
- **Why it might not fire:** Requires spread compression + liquidity density + volume spike + spread widening — four sequential gates that must all fire in order.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `spread_z_threshold` | *(check source)* | Spread z-score threshold |
  | `liq_density_threshold` | *(check source)* | Liquidity density threshold |
  | `vol_spike_threshold` | *(check source)* | Volume spike threshold |
  | `spread_widening_threshold` | *(check source)* | Spread widening threshold |

#### 16. `iv_gex_divergence`
- **File:** `strategies/layer2/iv_gex_divergence.py`
- **Concept:** Detects divergence between IV movement and GEX regime — when IV declines/expands while gamma regime suggests opposite.
- **Why it might not fire:** Requires price percentile + IV decline + gamma density decline + skew ROC all passing. Very strict.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `PRICE_PERCENTILE_THRESHOLD` | `0.70` | Price in top 30% of range |
  | `MIN_PRICE_POINTS` | `10` | Min price data points |
  | `MIN_IV_POINTS` | `5` | Min IV data points |
  | `MIN_POSITIVE_GAMMA` | `200000` | Min net gamma |
  | `IV_DECLINE_RATIO` | `0.95` | IV below 95% of rolling avg |
  | `STOP_PCT` | `0.006` | 0.6% fallback stop |
  | `TARGET_RISK_MULT` | `1.5` | Target = risk × 1.5 |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `IV_SKEW_OTM_PCT` | `0.05` | 5% OTM for skew |
  | `IV_SKEW_ROC_WINDOW` | `5` | Ticks for skew ROC |
  | `IV_SKEW_ROC_THRESHOLD` | `0.15` | Skew must rise ≥ 15% |
  | `GAMMA_DENSITY_WINDOW_PCT` | `0.01` | ±1% window for density |
  | `GAMMA_DENSITY_DECLINE_THRESHOLD` | `0.70` | Density must decline ≥ 30% |
  | `IV_VOLUME_MIN` | `100` | Min volume for IV |
  | `WALL_STOP_BUFFER_PCT` | `0.002` | 0.2% buffer beyond wall |
  | `WALL_STOP_MAX_DISTANCE_PCT` | `0.02` | Max distance to wall (2%) |

---

### Layer 3 — Advanced / Confluence (3 strategies)

#### 17. `gamma_volume_convergence`
- **File:** `strategies/layer3/gamma_volume_convergence.py`
- **Concept:** Detects convergence between gamma spikes and volume spikes — high-confidence reversal signal.
- **Why it might not fire:** Requires delta acceleration + gamma spike + volume spike + coupling all aligning. Layer 3 = higher bar.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `DELTA_ACCEL_RATIO` | `1.15` | Delta must accelerate ≥ 15% |
  | `DELTA_ACCEL_MIN_RATIO` | `0.30` | Min delta acceleration ratio |
  | `GAMMA_SPIKE_RATIO` | `1.20` | Gamma spike ≥ 1.2× |
  | `VOLUME_SPIKE_RATIO` | `1.20` | Volume spike ≥ 1.2× |
  | `STOP_PCT` | `0.005` | 0.5% stop |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MIN_DATA_POINTS` | `3` | Min data points |
  | `PRICE_UP_THRESHOLD` | `0.001` | 0.1% rise over 5m window |

#### 18. `iv_band_breakout`
- **File:** `strategies/layer3/iv_band_breakout.py`
- **Concept:** Detects IV band compression followed by breakout — when skew width compresses to bottom quartile and then expands.
- **Why it might not fire:** Requires skew compression (bottom 25%) + delta acceleration + IV expansion + volume confirmation. Very multi-gated.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `DELTA_DECEL_RATIO` | `0.95` | Delta deceleration threshold |
  | `PRICE_COMPRESSION_RATIO` | `0.40` | Price compression ratio |
  | `BREAKOUT_MOVE_PCT` | `0.0005` | Min breakout move (0.05%) |
  | `STOP_PCT` | `0.005` | 0.5% stop |
  | `TARGET_PCT` | `0.010` | 1.0% target |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MIN_DATA_POINTS` | `5` | Min data points |
  | `MIN_IV_DATA_POINTS` | `3` | Min IV data points |
  | `SKEW_OTM_PCT` | `0.05` | 5% OTM for skew |
  | `SKEW_COMPRESSION_PCT` | `0.25` | Skew in bottom 25% |
  | `POSITIVE_GAMMA_TARGET_MULT` | `2.5` | POS regime target mult |
  | `NEGATIVE_GAMMA_TARGET_MULT` | `1.5` | NEG regime target mult |
  | `DELTA_ACCEL_THRESHOLD` | `1.10` | Delta ≥ 10% at breakout |
  | `TARGET_IV_EXPANSION_MULT` | `2.5` | Base IV expansion mult |
  | `TARGET_IV_EXPANSION_NEG_MULT` | `1.5` | NEG IV expansion mult |
  | `TARGET_IV_EXPANSION_CAP` | `4.0` | Cap on IV expansion |
  | `TARGET_MIN_PCT` | `0.005` | Min 0.5% target |

#### 19. `theta_burn`
- **File:** `strategies/layer3/theta_burn.py`
- **Concept:** Theta decay play — trades the time decay of options near GEX walls. Bounce or slice depending on gamma regime.
- **Why it might not fire:** Requires wall proximity (0.5%) + range narrowing + gamma strength + liquidity checks. Also has a time-of-day window (16:30-19:30 UTC).
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_NET_GAMMA` | `5000.0` | Min net gamma |
  | `WALL_PROXIMITY_PCT` | `0.005` | 0.5% to wall |
  | `STOP_PAST_WALL_PCT` | `0.003` | 0.3% beyond wall |
  | `MIN_TARGET_PCT` | `0.002` | 0.2% min target |
  | `MAX_TARGET_PCT` | `0.004` | 0.4% max target |
  | `RANGE_NARROWNESS_RATIO` | `0.40` | 5m range / 30m range ≤ 40% |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MIN_DATA_POINTS` | `3` | Min data points |
  | `MIDNIGHT_UTC_START` | `16.5` | 16:30 UTC start window |
  | `MIDNIGHT_UTC_END` | `19.5` | 19:30 UTC end window |
  | `GAMMA_STRENGTH_HIGH` | `1_000_000` | Above = max gamma bonus |

---

### Full Data — Complex Multi-Source (11 strategies)

#### 20. `extrinsic_flow`
- **File:** `strategies/full_data/extrinsic_flow.py`
- **Concept:** Tracks Volume × Extrinsic Value (Premium Conviction) separately for calls and puts. Φ_Call = Σ(Volume × ExtrinsicValue) for calls, Φ_Put = Σ(Volume × ExtrinsicValue) for puts. RΦ = Φ_Call / Φ_Put (Relative Conviction Ratio). Call-heavy (RΦ > 3.0) = speculative bullish → LONG. Put-heavy (RΦ < 0.3) = defensive hedging → SHORT.
- **Signal types:** LONG: RΦ > 3.0 (call-side speculative) AND GEX regime is POSITIVE. SHORT: RΦ < 0.3 (put-side defensive) AND GEX regime is NEGATIVE.
- **Hard gates (all must pass):** Gate A: total Φ > phi_sigma_mult × σ (volume anchor — statistically significant volume), Gate B: bullish in POSITIVE gamma, bearish in NEGATIVE gamma (gamma guardrail), Gate C: delta purity (already filtered in main.py — only 15-65 delta contracts counted).
- **Why it might not fire:** Requires RΦ > 3.0 or < 0.3 (very extreme ratio) AND Gate A requires total Φ > 2.0 × σ (must be 2σ above baseline — very strict for low-volume periods). Gate B requires regime alignment: LONG needs POSITIVE gamma, SHORT needs NEGATIVE gamma. If the market was in the wrong regime for the signal direction, it gets blocked.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_phi_data_points` | `10` | Min data points for all Φ rolling windows |
  | `phi_sigma_mult` | `2.0` | Total Φ must exceed 2.0 × σ (Gate A) |
  | `phi_call_threshold` | `3.0` | RΦ > 3.0 for LONG signal |
  | `phi_put_threshold` | `0.3` | RΦ < 0.3 for SHORT signal |
  | `stop_pct` | `0.005` | 0.5% stop distance |
  | `target_risk_mult` | `2.0` | Target = risk × 2 |

#### 21. `extrinsic_intrinsic_flow`
- **File:** `strategies/full_data/extrinsic_intrinsic_flow.py`
- **Concept:** Tracks extrinsic vs intrinsic value shifts in options — expansion/collapse patterns.
- **Why it might not fire:** Requires extrinsic expansion (3%) or collapse (10%) + volume spike (1.3×) + delta acceleration + skew coupling.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `EXTRINSIC_EXPANSION_THRESHOLD` | `0.03` | 3% extrinsic expansion |
  | `EXTRINSIC_COLLAPSE_THRESHOLD` | `0.10` | 10% extrinsic collapse |
  | `VOLUME_SPIKE_RATIO` | `1.30` | 1.3× avg volume |
  | `STOP_PCT` | `0.005` | 0.5% stop |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MIN_DATA_POINTS` | `5` | Min data points |

#### 22. `gamma_breaker`
- **File:** `strategies/full_data/gamma_breaker.py`
- **Concept:** Detects when price breaks through a major Gamma Wall with dealer hedging acceleration. Γ_break = Price_Velocity × Gamma_Concentration_at_Level. When price approaches a large gamma wall, dealers must hedge in the direction of the move, accelerating price toward and through the wall (self-reinforcing feedback loop).
- **Signal types:** Bullish Breakout: price > nearest call wall + velocity accelerating → LONG. Bearish Breakout: price < nearest put wall + velocity accelerating → SHORT.
- **Hard gates (all must pass):** Gate A: wall GEX > min_wall_gex_sigma × σ above rolling avg (major wall), Gate B: bullish in POSITIVE gamma, bearish in NEGATIVE gamma (regime alignment), Gate C: volume > volume_spike_mult × MA(volume) (breakout confirmation).
- **Why it might not fire:** Requires Γ_break > 0.05% AND velocity accelerating (current > previous) simultaneously. Gate A requires wall_gex_sigma ≥ 2.0 (wall must be 2σ above average — major wall). Gate B requires regime alignment. Gate C requires volume > 1.5× MA. All 3 gates plus the gamma break + velocity conditions must align.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_gamma_break` | `0.0005` | Min Γ_break index (0.05%) |
  | `min_wall_gex_sigma` | `2.0` | Wall GEX must be ≥ 2.0σ above avg (Gate A) |
  | `min_wall_distance_pct` | `0.005` | Min wall distance (0.5%) |
  | `volume_spike_mult` | `1.5` | Volume > 1.5× MA (Gate C) |
  | `stop_pct` | `0.005` | 0.5% stop distance |
  | `target_risk_mult` | `2.0` | Target = risk × 2 |

#### 23. `ghost_premium`
- **File:** `strategies/full_data/ghost_premium.py`
- **Concept:** Detects when call options are overpriced relative to theoretical value (PDR = Premium-to-Draw ratio).
- **Why it might not fire:** Requires PDR > 0.60 AND ask size > 2σ AND volume confirmation. Very specific conditions.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `PDR_TRIGGER` | `0.60` | Calls 60%+ overpriced |
  | `MIN_PDR_DATA_POINTS` | `10` | Min PDR data points |
  | `ASK_SIZE_SIGMA_MULT` | `2.0` | Ask size > 2σ |
  | `STOP_PCT` | `0.005` | 0.5% stop |
  | `TARGET_RISK_MULT` | `2.0` | Target = risk × 2 |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MIN_ASK_SIZE_SIGMA` | `1.0` | Min ask size σ |
  | `MAX_NET_CHANGE_PCT` | `0.02` | Max net change 2% |

#### 24. `iron_anchor`
- **File:** `strategies/full_data/iron_anchor.py`
- **Concept:** Detects when a Gamma Wall aligns with a Liquidity Wall within $1.00. Ω_conf = |Price_GammaWall - Price_LiquidityWall|. Bullish Reversal: Bid Liquidity Wall near Put Wall → LONG (mean reversion). Bearish Reversal: Ask Liquidity Wall near Call Wall → SHORT (mean reversion). Highest conviction mean reversion signal — dual confirmation.
- **Signal types:** LONG: Bid Liquidity Wall near Put Wall (bullish reversal) AND velocity decreasing AND GEX regime POSITIVE. SHORT: Ask Liquidity Wall near Call Wall (bearish reversal) AND velocity decreasing AND GEX regime NEGATIVE.
- **Hard gates (all must pass):** Gate A: liquidity wall size > min_liq_wall_sigma × σ above rolling avg (weight check), Gate B: gamma wall significant (not minor outlier) AND regime alignment, Gate C: price velocity decreasing (exhaustion — current < avg × velocity_mult).
- **Why it might not fire:** Requires confluence proximity < $1.00 (Ω_conf) AND confluence signal direction (> 0 for LONG, < 0 for SHORT). Gate A requires liq_sigma > 0 AND liq_size > mean + 3.0 × σ (very strict — wall must be 3σ above average). Gate B requires regime alignment. Gate C requires velocity decreasing (current < avg × 0.8). Also needs ≥ 10 data points in ALL 4 rolling windows (proximity, signal, liq_size, liq_sigma). The combination of proximity threshold + 3σ wall + exhaustion + regime is extremely restrictive.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_data_points` | `10` | Min data points for all 4 rolling windows |
  | `max_confluence_distance` | `1.0` | Max $ distance between gamma + liquidity walls |
  | `min_liq_wall_sigma` | `3.0` | Wall must be ≥ 3.0σ above avg (Gate A) |
  | `min_gamma_wall_gex` | `500000` | Min gamma wall GEX (Gate B) |
  | `exhaustion_velocity_mult` | `0.8` | Velocity must be < 0.8× avg (Gate C) |
  | `stop_pct` | `0.008` | 0.8% stop distance |
  | `target_risk_mult` | `1.5` | Target = risk × 1.5 |

#### 25. `iv_skew_squeeze`
- **File:** `strategies/full_data/iv_skew_squeeze.py`
- **Concept:** Detects IV skew extremes (calls 20%+ more expensive) combined with price stability — squeeze before expansion.
- **Why it might not fire:** Requires skew positivity + volume spike (1.5×) + skew ROC (5%) + delta ROC (5%) + conviction stability. Five gates.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `SKEW_EXTREME_POSITIVE` | `0.20` | Calls 20%+ more expensive |
  | `PRICE_STABLE_THRESHOLD` | `0.005` | 0.5% max price change |
  | `MIN_NET_GAMMA` | `500000.0` | 500k min net gamma |
  | `STOP_PCT` | `0.005` | 0.5% stop |
  | `TARGET_PCT` | `0.008` | 0.8% target |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MIN_DATA_POINTS` | `5` | Min data points |
  | `MIN_SKEW_DATA_POINTS` | `5` | Min skew data points |
  | `VOLUME_SPIKE_THRESHOLD` | `1.5` | Volume > 1.5× avg |
  | `SKEW_ROC_THRESHOLD` | `0.05` | 5% skew ROC |
  | `VOL_WEIGHTED_STABILITY_MIN` | `0.50` | Min conviction stability |
  | `VOL_FRAGILE_THRESHOLD` | `0.30` | Volume < 30% avg = fragile |
  | `DELTA_ROC_THRESHOLD` | `0.05` | 5% delta ROC |
  | `TARGET_IV_EXPANSION_MULT` | `1.6` | Base IV expansion mult |
  | `TARGET_IV_EXPANSION_CAP` | `2.0` | Cap on IV expansion |
  | `TARGET_MIN_PCT` | `0.005` | Min 0.5% target |

#### 26. `prob_distribution_shift`
- **File:** `strategies/full_data/prob_distribution_shift.py`
- **Concept:** Detects probability distribution shifts in options — when capital flows to specific strikes indicating directional bias.
- **Why it might not fire:** Requires z-score ≥ 1.5 + consecutive signals + min net gamma (500k) + OI concentration. Multi-gated.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `Z_SCORE_THRESHOLD` | `1.5` | 1.5σ from mean |
  | `MIN_CONSECUTIVE_SIGNALS` | `2` | 2 consecutive evaluations |
  | `MIN_NET_GAMMA` | `500000.0` | 500k min net gamma |
  | `STOP_PCT` | `0.005` | 0.5% stop |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MIN_STRIKES_WITH_DATA` | `5` | Min strikes with data |
  | `MIN_DATA_POINTS` | `5` | Min data points |
  | `CONTRIBUTION_THRESHOLD` | `0.05` | 5% of total momentum |

#### 27. `prob_weighted_magnet`
- **File:** `strategies/full_data/prob_weighted_magnet.py`
- **Concept:** Probabilistic magnet — identifies strikes with high OI concentration and trades the magnetic pull toward them.
- **Why it might not fire:** Requires OI concentration ≥ 2.0 + consolidation ratio ≤ 50% + delta acceleration + net gamma ≥ 500k.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_OI_CONCENTRATION` | `2.0` | Min total OI at strike |
  | `CONSOLIDATION_RATIO` | `0.50` | 5m range / 30m range ≤ 50% |
  | `DELTA_ACCEL_RATIO` | `1.05` | 5% delta change |
  | `MIN_NET_GAMMA` | `500000.0` | 500k min net gamma |
  | `STOP_PCT` | `0.005` | 0.5% stop |
  | `TARGET_RISK_MULT` | `1.5` | Target = risk × 1.5 |
  | `MIN_CONFIDENCE` | `0.15` | Min confidence |
  | `MIN_DATA_POINTS` | `3` | Min data points |
  | `DELTA_ROC_THRESHOLD` | `0.05` | 5% delta ROC |
  | `LIQUIDITY_VACUUM_RATIO` | `0.30` | Bid/ask ratio for vacuum |
  | `GAMMA_SCALE_BASE` | `2.0` | Gamma value for scaling |
  | `TARGET_MULT_CAP` | `3.0` | Max target multiplier |
  | `TARGET_MIN_PCT` | `0.005` | Min 0.5% target |

#### 28. `sentiment_sync`
- **File:** `strategies/full_data/sentiment_sync.py`
- **Concept:** Detects when options sentiment (IV skew) and equity flow (Aggressor VSI) move in lockstep. Γ_sync = Sign(ΔSkew) × Sign(Aggressor_VSI). ΔSkew = rolling % change in IV skew over 5m. VSI = venue-specific bid/ask imbalance on MEMX+BATS. Bullish Sync: ΔSkew falling (complacency) AND VSI positive (buying) → LONG. Bearish Sync: ΔSkew rising (fear) AND VSI negative (selling) → SHORT.
- **Signal types:** LONG: ΔSkew < 0 (falling/complacency) AND VSI > 0 (buying) AND regime == POSITIVE. SHORT: ΔSkew > 0 (rising/fear) AND VSI < 0 (selling) AND regime == NEGATIVE.
- **Hard gates (all must pass):** Gate A: |ΔSkew| > min_sig_sigma × σ (both skew change and VSI must be significant), Gate B: total volume ≥ rolling average (volume anchor), Gate C: VSI magnitude > price_confirm_pct (price confirmation proxy).
- **Why it might not fire:** Requires 4 rolling windows (correlation, sigma, skew_change, vsi_magnitude) all with ≥ 10 data points AND correlation sign to match direction AND Gate A requires z-score ≥ 2.0 (both dimensions must exceed 2σ simultaneously). Gate C uses VSI magnitude as price proxy — if VSI magnitude < 0.001, this fails. All three data sources (skew, VSI, volume) must align.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_data_points` | `10` | Min data points for all 4 rolling windows |
  | `min_sig_sigma` | `2.0` | Both ΔSkew and VSI must exceed 2.0σ (Gate A) |
  | `volume_min_mult` | `1.0` | Volume ≥ 1.0× MA (Gate B) |
  | `price_confirm_pct` | `0.001` | Min VSI magnitude for price confirmation (Gate C) |
  | `stop_pct` | `0.005` | 0.5% stop distance |
  | `target_risk_mult` | `2.0` | Target = risk × 2 |

#### 29. `skew_dynamics`
- **File:** `strategies/full_data/skew_dynamics.py`
- **Concept:** Tracks how the volatility smile changes over time via the Skewness Coefficient Ψ. Ψ = (IV_Put_Wing - IV_Call_Wing) / IV_ATM. Steepening skew (Ψ rising) = rising fear → SHORT. Flattening skew (Ψ falling) = complacency → LONG. Best when aligned with GEX regime.
- **Signal types:** LONG: Ψ falling (flattening skew) AND GEX regime is POSITIVE. SHORT: Ψ rising (steepening skew) AND GEX regime is NEGATIVE.
- **Hard gates (all must pass):** Gate A: combined OI + volume of wing strikes above rolling 1h threshold (liquidity check), Gate B: bullish in POSITIVE gamma, bearish in NEGATIVE gamma (GEX regime alignment), Gate C: |Ψ| > 0.001 (IV divergence purity — skew-driven, not ATM vol spike).
- **Why it might not fire:** Requires Ψ ROC z-score ≥ 2.0 (|Ψ_ROC| / Ψ_sigma ≥ 2.0) AND regime alignment AND |Ψ| > 0.001. Gate C is a soft gate (always passes if volume data exists). Gate B requires regime alignment. The 2.0σ z-score threshold on Ψ ROC is the main blocker — skew changes must be statistically significant.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_psi_data_points` | `10` | Min data points for Ψ rolling windows |
  | `min_psi_sigma` | `2.0` | Ψ ROC z-score must exceed 2.0σ |
  | `liquidity_oi_threshold` | `100` | Min OI threshold for liquidity gate (fallback) |
  | `stop_pct` | `0.005` | 0.5% stop distance |
  | `target_risk_mult` | `2.0` | Target = risk × 2 |

#### 30. `smile_dynamics`
- **File:** `strategies/full_data/smile_dynamics.py`
- **Concept:** Measures the Curvature Asymmetry Index Ω across multiple strikes. Ω = |Slope_Put_Wing| / |Slope_Call_Wing|. Put-side curvature dominant (Ω rising) = fear jaw opening → SHORT. Call-side curvature dominant (Ω falling) = euphoria jaw closing → LONG. Leading indicator: curvature shifts often precede price moves.
- **Signal types:** LONG: Ω falling (flattening smile) AND GEX regime is POSITIVE. SHORT: Ω rising (opening smile) AND GEX regime is NEGATIVE.
- **Hard gates (all must pass):** Gate A: total OI of wing strikes above minimum threshold (liquidity anchor), Gate B: bullish in POSITIVE gamma, bearish in NEGATIVE gamma (gamma guardrail), Gate C: |put_slope| > 0.001 OR |call_slope| > 0.001 (vol divergence purity — real curvature, not ATM vol expansion).
- **Why it might not fire:** Requires Ω ROC z-score ≥ 2.0 (|Ω_ROC| / Ω_sigma ≥ 2.0) AND regime alignment AND meaningful slope divergence. Gate A always passes if volume data exists. Gate C requires at least one slope to be > 0.001. The 2.0σ z-score threshold on Ω ROC is the main blocker — curvature changes must be statistically significant.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_omega_data_points` | `10` | Min data points for Ω rolling windows |
  | `min_omega_sigma` | `2.0` | Ω ROC z-score must exceed 2.0σ |
  | `liquidity_oi_threshold` | `100` | Min OI threshold for liquidity gate (fallback) |
  | `stop_pct` | `0.005` | 0.5% stop distance |
  | `target_risk_mult` | `2.0` | Target = risk × 2 |

#### 31. `whale_tracker`
- **File:** `strategies/full_data/whale_tracker.py`
- **Concept:** Detects institutional "whale" orders by analyzing size concentration ratio. Ω_conc = biggest_size / smallest_size at best price levels. A high ratio means one participant is placing a very large order while others are small — classic whale signature. Filters out retail "noise" by requiring low participant count at large orders.
- **Signal types:** LONG: bid-side concentration > 5σ AND num_participants ≤ 2 AND GEX regime is POSITIVE. SHORT: ask-side concentration > 5σ AND num_participants ≤ 2 AND GEX regime is NEGATIVE.
- **Hard gates (all must pass):** Gate A: biggest_size z-score ≥ min_biggest_size_sigma (whale threshold — must be significantly above rolling avg), Gate B: num_participants ≤ max_participants (single-entity filter — low count = institutional), Gate C: bullish in POSITIVE gamma, bearish in NEGATIVE gamma (GEX regime alignment).
- **Why it might not fire:** Requires concentration z-score ≥ 5.0 (Ω_conc / Ω_sigma ≥ 5.0 — extremely high bar) AND Gate A requires biggest_size z-score ≥ 3.0 AND Gate B requires ≤ 2 participants AND Gate C requires regime alignment. The 5.0σ concentration threshold is the primary blocker — whale concentration must be extreme. Also requires ≥ 10 data points in conc_ratio and biggest windows, and ≥ 5 in sigma window.
- **Adjustable parameters:**
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `MIN_CONFIDENCE` | `0.15` | Min confidence to emit signal |
  | `min_conc_sigma` | `5.0` | Concentration z-score must exceed 5.0σ (primary threshold) |
  | `max_participants` | `2` | Max participants for single-entity filter (Gate B) |
  | `min_biggest_size_sigma` | `3.0` | Biggest size z-score must exceed 3.0σ (Gate A) |
  | `stop_pct` | `0.005` | 0.5% stop distance |
  | `target_risk_mult` | `2.0` | Target = risk × 2 |

---

## Summary & Recommendations

### Key Observations

1. **Heavy gate dependency:** Most non-firing strategies have 3-5 hard gates that must ALL pass. The 11 firing strategies likely have fewer/harder-to-block gates.

2. **Layer bias:** All 11 firing strategies are from Layer 1 (GEX/walls) and Layer 2 (flow/depth). No Layer 3 or Full Data strategies fired — these have higher bars by design.

3. **Common pattern:** Non-firing strategies often require:
   - Specific volume spikes (1.2×-1.5× rolling avg)
   - IV/derivative conditions (skew, PDR, extrinsic)
   - Participant/order book conditions (fragmentation, stacking, diversity)
   - Multi-source correlation (gamma + skew + VSI, etc.)

4. **TSLA-specific:** TSLA had 12,630 signals but only from 11 strategies. The market conditions that day favored simple GEX/wall-based strategies over complex multi-factor ones.

### Suggested Next Steps

1. **Lower gate thresholds** on the most promising non-firing strategies (especially Layer 3 and full_data)
2. **Check per-strategy signal counts** across all 5 symbols to see if any fired on other symbols
3. **Review gate pass rates** — identify which specific gate blocks each strategy most often
4. **Consider adaptive thresholds** — some strategies may need dynamic thresholds based on market regime
5. **Add logging** to track gate pass/fail rates for each strategy per tick
