# SYNGEX Val2Plan — Strategy Solution Design Guide

**Version:** 1.0  
**Date:** 2026-05-05  
**Goal:** Fix broken strategies, remove development-time filters, add regime/trend awareness, keep production safety net at 70%+ confidence.

---

## 🎯 Design Principles (Per Hologaun)

1. **Remove all 5-minute/time filters** — we want ALL signals they detect during development
2. **Production trading** stays at 70%+ confidence — but development sees everything
3. **Regime-aware filtering** — some strategies work in Positive gamma, others in Negative
4. **Trend-aware filtering** — some strategies work in trending markets, others in range-bound
5. **Strategy development focus** — don't limit signal volume, improve signal quality

---

## 📊 Market Regime Context (May 5 Baseline)

| Regime | Description | Profitable Strategies | Failing Strategies |
|--------|-------------|----------------------|-------------------|
| **Positive Gamma** | Dealers long gamma → buy dips, sell rips → dampens volatility | Vol Compression Range, Gamma Wall Bounce (marginal) | Gamma Squeeze, Confluence Reversal, Magnet Accelerate |
| **Negative Gamma** | Dealers short gamma → sell dips, buy rips → amplifies volatility | Gamma Squeeze, Confluence Reversal, Magnet Accelerate | Vol Compression Range |
| **Trending** | Price breaks through walls, momentum carries | Gamma Squeeze (if timed right) | Wall Bounce, Vol Compression, Confluence Reversal |
| **Range-Bound** | Price oscillates within boundaries | Vol Compression Range, Wall Bounce | Gamma Squeeze, Magnet Accelerate |

**Key insight:** No single strategy works across all regimes. Each strategy needs a regime/trend filter that determines WHEN it should fire, not a confidence threshold that determines WHETHER to trade.

---

## 🔧 Strategy-by-Strategy Fixes

### 1. 🥇 Vol Compression Range — ✅ ALREADY WORKING
- **May 5 Performance:** +$16.25 | 55% WR | 26 signals
- **Current Filters:** Tight compression threshold (0.3%), wider stop (0.6%)
- **Verdict:** This is the benchmark strategy. Works because it's regime-agnostic — it fires when price compresses, regardless of gamma regime.

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 1.1 | Remove 5-min cooldown | Filter removal | Get all compression signals |
| 1.2 | Add LONG side (currently 91% SHORT) | Strategy expansion | Compressions work both directions |
| 1.3 | Add regime filter: prefer POSITIVE gamma | Regime awareness | May 5 was positive gamma, strategy worked |
| 1.4 | Add trend filter: prefer NON-trending | Trend awareness | Strategy needs range-bound conditions |
| 1.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals, production filters at 70% |

**Regime/Trend Matrix:**
| Regime | Trend | Action |
|--------|-------|--------|
| Positive | Range-bound | ✅ PRIMARY — fire freely |
| Positive | Trending | ⚠️ Caution — range may be breaking |
| Negative | Range-bound | ✅ Fire — compression works in both regimes |
| Negative | Trending | ❌ Suppress — trend will break compression |

---

### 2. 🥈 Gamma Wall Bounce — ⚠️ NEAR BREAKEVEN, NEEDS TWEAKS
- **May 5 Performance:** -$2.39 | 46% WR | 236 signals
- **Problem:** Correctly identifies walls but can't distinguish rejection from piercing
- **Synapse's diagnosis:** Needs a "velocity filter" — if delta-gamma acceleration is too high, treat wall as permeable

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 2.1 | Remove 5-min cooldown | Filter removal | Get all wall bounce signals |
| 2.2 | Add velocity filter | Strategy enhancement | If price crosses wall at high velocity, skip — wall is permeable |
| 2.3 | Add regime filter: prefer POSITIVE gamma | Regime awareness | Walls reflect better in positive gamma (dealers hedge counter-cyclically) |
| 2.4 | Add rejection_score threshold: > 0.6 minimum | Confidence threshold | Cuts out weak wall interactions |
| 2.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

**Velocity Filter Logic:**
```
velocity = abs(current_price - previous_price) / previous_price
if velocity > VELOCITY_THRESHOLD (0.5% per tick):
    return []  # Wall is being pierced, not bouncing
```

**Regime/Trend Matrix:**
| Regime | Trend | Action |
|--------|-------|--------|
| Positive | Range-bound | ✅ PRIMARY — walls reflect, bounces work |
| Positive | Trending | ⚠️ With velocity filter — pierce-throughs filtered |
| Negative | Range-bound | ⚠️ Caution — walls may be tested more |
| Negative | Trending | ❌ Suppress — negative gamma amplifies breakouts |

---

### 3. 🥉 Gamma Squeeze — 🔴 NEEDS REGIME FILTER + BIDIRECTIONAL
- **May 5 Performance:** -$162.39 | 39% WR | 473 signals (53% of ALL signals)
- **Problem:** 100% LONG bias, fires in positive gamma where squeezes are suppressed
- **Rune's diagnosis:** Needs SHORT leg for short squeezes; 495 signals at low confidence

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 3.1 | Remove 5-min cooldown | Filter removal | Get all squeeze signals |
| 3.2 | Add SHORT leg detection | Strategy expansion | Detect when price breaks below put wall with accelerating delta |
| 3.3 | Add regime filter: prefer NEGATIVE gamma | Regime awareness | SQUEEZES WORK IN NEGATIVE GAMMA — dealers short gamma amplify moves |
| 3.4 | Add sustain filter: price must stay beyond wall for 2+ ticks | Strategy enhancement | Prevents false breakouts (May 5 had many wall pierce-then-reject) |
| 3.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

**Critical Regime Filter:**
```python
if regime == "NEGATIVE":
    # Squeeze amplifies — fire both directions
    pass
elif regime == "POSITIVE":
    # Squeeze suppressed — only fire if wall is MASSIVE (top 5% of GEX)
    if wall_gex < MIN_MASSIVE_WALL_GEX:
        return []
```

**Regime/Trend Matrix:**
| Regime | Trend | Action |
|--------|-------|--------|
| Positive | Range-bound | ❌ Suppress — squeezes dampened |
| Positive | Trending | ⚠️ Only if wall is MASSIVE |
| Negative | Range-bound | ⚠️ Caution — squeezes possible but limited |
| Negative | Trending | ✅ PRIMARY — squeezes amplify in negative gamma + trend |

---

### 4. Magnet Accelerate — 🔴 NEEDS REGIME AWARENESS
- **May 5 Performance:** -$18.84 | 41% WR | 115 signals
- **Problem:** 100% LONG bias, fights positive gamma regime
- **Forge's diagnosis:** In positive gamma, dealers dampen acceleration — magnet was repelling, not pulling

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 4.1 | Remove 5-min cooldown | Filter removal | Get all magnet signals |
| 4.2 | Add SHORT magnet direction | Strategy expansion | In positive gamma, magnet pulls DOWN (not up) |
| 4.3 | Add regime filter: LONG in NEGATIVE, SHORT in POSITIVE | Regime awareness | Magnet direction depends on gamma regime |
| 4.4 | Add hold-time limit: max 60 min | Risk management | Prevents long-drawdown losses |
| 4.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

**Regime-Aware Direction Logic:**
```python
if regime == "POSITIVE":
    # Dealers buy dips, sell rips → magnet pulls toward center (DOWN from above, UP from below)
    direction = Direction.SHORT  # Bet against magnet pull
elif regime == "NEGATIVE":
    # Dealers sell dips, buy rips → magnet amplifies → LONG
    direction = Direction.LONG
```

**Regime/Trend Matrix:**
| Regime | Trend | Action |
|--------|-------|--------|
| Positive | Range-bound | ⚠️ SHORT magnet — bet against pull |
| Positive | Trending | ❌ Suppress — trend overwhelms magnet |
| Negative | Range-bound | ✅ LONG magnet — pull is real |
| Negative | Trending | ⚠️ Caution — trend may overpower magnet |

---

### 5. Confluence Reversal — 🔴 NEEDS REGIME + DIRECTION FIX
- **May 5 Performance:** -$35.46 | 30% WR | 37 signals
- **Problem:** 100% LONG, 100% has_flip=False, worst win/loss ratio (0.44:1)
- **Forge's diagnosis:** Trading reversals in a trending market; high confidence but wrong direction

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 5.1 | Remove 5-min cooldown | Filter removal | Get all confluence signals |
| 5.2 | Add SHORT direction | Strategy expansion | Reversals go both ways |
| 5.3 | Add regime filter: prefer NEGATIVE gamma | Regime awareness | Reversals work better in negative gamma (amplified moves reverse harder) |
| 5.4 | Add trend filter: prefer NON-trending | Trend awareness | Reversals fail in trending markets |
| 5.5 | Fix has_flip logic | Bug fix | 100% False suggests flip detection is broken |
| 5.6 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

**Critical Bug — has_flip=False on 100% of signals:**
The strategy requires a gamma flip (call/put regime change) as primary confirmation. But every signal had `has_flip=False`. Either:
- The flip detection code is broken (returns False always), or
- The strategy generates phantom signals without its primary confirmation

**Fix:** Audit the flip detection logic. If flip detection is working, the strategy should only fire when `has_flip=True`. If flip detection is broken, fix it.

**Regime/Trend Matrix:**
| Regime | Trend | Action |
|--------|-------|--------|
| Positive | Range-bound | ⚠️ Caution — reversals possible but weak |
| Positive | Trending | ❌ Suppress — trend punches through confluences |
| Negative | Range-bound | ✅ Fire — reversals off confluences work |
| Negative | Trending | ⚠️ With flip confirmation — amplified reversals |

---

### 6. GEX Imbalance — ⚠️ PROMISING, NEEDS BROADER COVERAGE
- **May 5 Performance:** -$7.94 | 29% WR | 25 signals (only 5 symbols tracked)
- **Problem:** Only fired on SOFI, needs broader symbol coverage
- **Rune's note:** 41 signals in full dataset, all in META

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 6.1 | Remove 5-min cooldown | Filter removal | Get all imbalance signals |
| 6.2 | Lower ratio thresholds: PUT_HEAVY from 0.4 → 0.5 | Threshold adjustment | More symbols will qualify |
| 6.3 | Lower CALL_HEAVY from 0.75 → 0.65 | Threshold adjustment | More symbols will qualify |
| 6.4 | Add regime filter: LONG in POSITIVE, SHORT in NEGATIVE | Regime awareness | Dealer hedging bias depends on regime |
| 6.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 7. Gamma Flip Breakout — ✅ NEEDS ATM FALLBACK (ALREADY FIXED)
- **May 5 Performance:** 0 signals (no flip points existed)
- **Fix already deployed:** ATM fallback added in v1.71

**Additional Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 7.1 | Remove 5-min cooldown | Filter removal | Get all flip breakout signals |
| 7.2 | Add regime filter: fade in POSITIVE, breakout in NEGATIVE | Regime awareness | Strategy's core logic |
| 7.3 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 8. GEX Divergence — ✅ NEEDS REGIME SOFTENING (ALREADY FIXED)
- **May 5 Performance:** 0 signals (regime filter blocked all)
- **Fix already deployed:** Hard regime gate → soft confidence penalty in v1.71

**Additional Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 8.1 | Remove 5-min cooldown | Filter removal | Get all divergence signals |
| 8.2 | Lower DIVERGENCE_MIN_SLOPE from 0.001 → 0.0005 | Threshold adjustment | More divergences will be detected |
| 8.3 | Lower MIN_CONFIDENCE from 0.45 → 0.25 | Confidence threshold | Development: see all signals |

---

### 9. Delta Gamma Squeeze — ✅ DEAD CODE REMOVED (ALREADY FIXED)
- **May 5 Performance:** 0 signals (no wall proximity or delta acceleration)
- **Fix already deployed:** Removed dead `delta_{side}_5m` key path in v1.71

**Additional Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 9.1 | Remove 5-min cooldown | Filter removal | Get all delta-gamma squeeze signals |
| 9.2 | Lower CALL_WALL_PROXIMITY_PCT from 0.02 → 0.03 | Threshold adjustment | More walls will be in range |
| 9.3 | Lower DELTA_ACCEL_RATIO from 1.15 → 1.10 | Threshold adjustment | More delta acceleration detected |
| 9.4 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 10. Delta Volume Exhaustion — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs strong trend + declining delta + declining volume simultaneously

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 10.1 | Remove 5-min cooldown | Filter removal | Get all exhaustion signals |
| 10.2 | Lower DELTA_DECLINE_RATIO from 0.90 → 0.95 | Threshold adjustment | More delta declines detected |
| 10.3 | Lower VOLUME_DECLINE_RATIO from 0.85 → 0.90 | Threshold adjustment | More volume declines detected |
| 10.4 | Add regime filter: prefer POSITIVE gamma | Regime awareness | Exhaustion + mean reversion works in positive gamma |
| 10.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 11. Vol Compression Range — ✅ ALREADY OPTIMIZED
No additional changes needed. Already the best performer.

---

### 12. IV-GEX Divergence — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs price at extreme + IV changing + net gamma strongly directional

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 12.1 | Remove 5-min cooldown | Filter removal | Get all IV-GEX divergence signals |
| 12.2 | Lower PRICE_PERCENTILE_THRESHOLD from 0.75 → 0.70 | Threshold adjustment | More price extremes detected |
| 12.3 | Lower MIN_POSITIVE_GAMMA from 500000 → 200000 | Threshold adjustment | More gamma conditions met |
| 12.4 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 13. IV Band Breakout — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs IV at bottom 25% + price compression + delta deceleration + breakout

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 13.1 | Remove 5-min cooldown | Filter removal | Get all IV band breakout signals |
| 13.2 | Lower PRICE_COMPRESSION_RATIO from 0.30 → 0.40 | Threshold adjustment | More compression detected |
| 13.3 | Lower DELTA_DECEL_RATIO from 0.98 → 0.95 | Threshold adjustment | More delta deceleration detected |
| 13.4 | Add regime filter: prefer POSITIVE gamma | Regime awareness | IV compression + breakout works better in positive gamma |
| 13.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 14. Strike Concentration — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs price within 0.3% of top OI strike + strong candle + volume spike

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 14.1 | Remove 5-min cooldown | Filter removal | Get all strike concentration signals |
| 14.2 | Increase BOUNCE_PROXIMITY_PCT from 0.003 → 0.005 | Threshold adjustment | More proximity matches |
| 14.3 | Lower SLICE_BODY_RATIO from 0.5 → 0.3 | Threshold adjustment | More slice candles detected |
| 14.4 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 15. Theta Burn — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs extreme range compression (5m < 30% of 30m)

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 15.1 | Remove 5-min cooldown | Filter removal | Get all theta burn signals |
| 15.2 | Increase RANGE_NARROWNESS_RATIO from 0.30 → 0.40 | Threshold adjustment | More pinning conditions detected |
| 15.3 | Lower REJECTION_SCORE_THRESHOLD from 0.4 → 0.3 | Threshold adjustment | More rejection signals detected |
| 15.4 | Lower MIN_NET_GAMMA from 10000 → 5000 | Threshold adjustment | More gamma conditions met |
| 15.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 16. Extrinsic/Intrinsic Flow — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs extrinsic proxy +5% + volume >150% simultaneously

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 16.1 | Remove 5-min cooldown | Filter removal | Get all extrinsic flow signals |
| 16.2 | Lower EXTRINSIC_EXPANSION_THRESHOLD from 0.05 → 0.03 | Threshold adjustment | More extrinsic expansion detected |
| 16.3 | Lower VOLUME_SPIKE_RATIO from 1.50 → 1.30 | Threshold adjustment | More volume spikes detected |
| 16.4 | Lower MIN_DATA_POINTS from 10 → 5 | Threshold adjustment | More extrinsic data available |
| 16.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 17. IV Skew Squeeze — ✅ SKEW-EASING LOGIC FIXED (ALREADY DEPLOYED)
- **May 5 Performance:** 0 signals (skew didn't reach extreme levels)
- **Fix already deployed:** Reversed skew-easing logic in `_check_long` in v1.71

**Additional Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 17.1 | Remove 5-min cooldown | Filter removal | Get all skew squeeze signals |
| 17.2 | Lower SKEW_EXTREME_POSITIVE from 0.30 → 0.20 | Threshold adjustment | More euphoria conditions detected |
| 17.3 | Lower SKEW_EXTREME_NEGATIVE from -0.10 → -0.07 | Threshold adjustment | More panic conditions detected |
| 17.4 | Lower MIN_SKEW_DATA_POINTS from 10 → 5 | Threshold adjustment | More skew data available |
| 17.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 18. Prob Distribution Shift — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs z-score > 2σ for 3 consecutive evaluations

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 18.1 | Remove 5-min cooldown | Filter removal | Get all prob shift signals |
| 18.2 | Lower Z_SCORE_THRESHOLD from 2.0 → 1.5 | Threshold adjustment | More shifts detected |
| 18.3 | Lower MIN_CONSECUTIVE_SIGNALS from 3 → 2 | Threshold adjustment | Fewer consecutive needed |
| 18.4 | Lower MIN_DATA_POINTS from 10 → 5 | Threshold adjustment | More momentum data available |
| 18.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 19. Prob Weighted Magnet — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs consolidation + flat/declining volume + high OI concentration

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 19.1 | Remove 5-min cooldown | Filter removal | Get all prob magnet signals |
| 19.2 | Increase CONSOLIDATION_RATIO from 0.40 → 0.50 | Threshold adjustment | More consolidation detected |
| 19.3 | Lower MIN_OI_CONCENTRATION from 5.0 → 2.0 | Threshold adjustment | More strikes qualify |
| 19.4 | Lower DELTA_ACCEL_RATIO from 1.10 → 1.05 | Threshold adjustment | More delta acceleration detected |
| 19.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

### 20. Gamma Volume Convergence — ⏸️ NO SIGNALS
- **May 5 Performance:** 0 signals
- **Problem:** Needs delta accel + gamma spike + volume spike + price trend ALL simultaneously

**Fixes:**
| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 20.1 | Remove 5-min cooldown | Filter removal | Get all GVC signals |
| 20.2 | Lower DELTA_ACCEL_RATIO from 1.15 → 1.10 | Threshold adjustment | More delta acceleration detected |
| 20.3 | Lower GAMMA_SPIKE_RATIO from 1.20 → 1.15 | Threshold adjustment | More gamma spikes detected |
| 20.4 | Lower VOLUME_SPIKE_RATIO from 1.20 → 1.15 | Threshold adjustment | More volume spikes detected |
| 20.5 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Confidence threshold | Development: see all signals |

---

## 📋 Universal Changes (All Strategies)

| # | Change | Impact |
|---|--------|--------|
| U.1 | Remove all 5-minute cooldowns | +200-500% more signals across all strategies |
| U.2 | Lower MIN_CONFIDENCE from 0.35 → 0.25 | Signals fire at lower confidence during development |
| U.3 | Add regime field to all Signal metadata | Enables post-hoc analysis by regime |
| U.4 | Add trend field to all Signal metadata | Enables post-hoc analysis by trend |
| U.5 | Log regime+trend at signal creation time | Enables correlation analysis |

---

## 📈 Production Deployment Plan

When ready to go to production:

1. **Apply 70%+ confidence filter** across all strategies
2. **Re-enable 5-minute cooldowns** to prevent signal flooding
3. **Apply regime/trend filters** per strategy's matrix above
4. **Monitor signal volume** — expect ~30-50% reduction from development mode
5. **Track win rate by regime** — validate regime filters are correct

---

## 📊 Expected Signal Volume After Changes

| Category | Current Signals | After Development Changes |
|----------|----------------|--------------------------|
| Core Structural (1-5) | ~887 | ~2,000-3,000 |
| Alpha Layer (6-11) | ~41 | ~100-200 |
| Layer 2 (12-15) | ~0 | ~50-150 |
| Layer 3 (16-20) | ~0 | ~30-100 |
| **Total** | **~928** | **~2,180-3,450** |

**Note:** Volume increase is expected. The 70%+ confidence filter in production will reduce this back down while keeping the development data rich for analysis.

---

## 🎯 Priority Order for Implementation

| Priority | Strategy | Why |
|----------|----------|-----|
| **P0** | Gamma Squeeze | Biggest P&L drain, needs regime filter ASAP |
| **P0** | Confluence Reversal | Worst WR, has_flip bug needs fixing |
| **P1** | Magnet Accelerate | Fighting positive gamma, needs direction fix |
| **P1** | Gamma Wall Bounce | Near breakeven, velocity filter will help |
| **P2** | Vol Compression Range | Already working, just needs LONG side |
| **P2** | GEX Imbalance | Promising, needs broader coverage |
| **P3** | All Layer 2/3 strategies | Currently 0 signals, relax thresholds |

---

## 🔍 Regime Detection Reference

**How to determine gamma regime:**
```python
regime = "POSITIVE" if net_gamma > 0 else "NEGATIVE"
flip_strike = gex_calc.get_gamma_flip()  # Boundary between regimes
```

**How to determine trend:**
```python
trend = "UP" if price_window.trend == "UP" else "DOWN" if price_window.trend == "DOWN" else "RANGE"
```

**How to determine volatility state:**
```python
vol_state = "HIGH" if rolling_range > rolling_mean_range * 1.5 else "LOW" if rolling_range < rolling_mean_range * 0.5 else "NORMAL"
```

These fields should be added to every Signal's metadata for post-hoc correlation analysis.
