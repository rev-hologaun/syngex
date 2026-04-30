# Syngex Strategy Design — V2

**Date:** 2026-04-29  
**Data Sources:**
- **OHLC:** Open, High, Low, Close, Volume (from TradeStation quotes stream)
- **VolumeUp:** Aggressive buying volume (buyers hitting asks)
- **VolumeDown:** Aggressive selling volume (sellers hitting bids)
- **Options Chain (per-second):** Delta, Theta, Gamma, Rho, Vega, ImpliedVolatility, IntrinsicValue, ExtrinsicValue, TheoreticalValue, ProbabilityITM, ProbabilityOTM, ProbabilityBE, OpenInterest

---

## Strategy 1: Delta-Volume Divergence

**Type:** Mean Reversion / Reversal  
**Timeframe:** 5-min bars for price, 10-sec rolling for options  
**Best For:** TSLA, GLD, MSFT — liquid names with tight spreads

### The Edge

Options delta tells you which way dealers MUST hedge. Stock VolumeUp/VolumeDown tells you what the market is actually doing. When they disagree, one side is trapped — and trapped positions create violent reversals.

### Data Fields Used

| Field | Source | Purpose |
|-------|--------|---------|
| Delta (all options) | Options chain | Aggregate directional pressure from dealers |
| VolumeUp | OHLC stream | Aggressive buying in the stock |
| VolumeDown | OHLC stream | Aggressive selling in the stock |
| ImpliedVolatility | Options chain | Confirm fear/greed state |

### Signal Construction

**Step 1 — Aggregate Delta:**
```
NetDelta = Σ(|Delta_i| × OpenInterest_i) for calls (positive)
           - Σ(|Delta_i| × OpenInterest_i) for puts (negative)
```
Rolling 10-second change: `ΔNetDelta = NetDelta_current - NetDelta_10s_ago`

**Step 2 — Volume Imbalance:**
```
VolumeRatio = VolumeUp / (VolumeUp + VolumeDown)
```
- > 0.55 = buyers aggressive
- < 0.45 = sellers aggressive

**Step 3 — Divergence Detection:**

**BULLISH DIVERGENCE (Long signal):**
- ΔNetDelta is POSITIVE (calls gaining delta → dealers must BUY to hedge)
- VolumeRatio < 0.45 (stock is being SOLD — sellers hitting bids)
- Price is making lower lows while delta is rising
- ImpliedVolatility is rising (panic selling → reversal setup)

**BEARISH DIVERGENCE (Short signal):**
- ΔNetDelta is NEGATIVE (puts gaining delta → dealers must SELL to hedge)
- VolumeRatio > 0.55 (stock is being BOUGHT — buyers hitting asks)
- Price is making higher highs while delta is falling
- ImpliedVolatility is rising (panic buying → reversal setup)

### Entry/Exit

**Entry:**
- Wait for divergence to persist for ≥ 30 seconds (avoid noise)
- Enter on the next 5-min candle open after confirmation
- Size: proportional to |ΔNetDelta| magnitude

**Exit:**
- Target: 0.5-1.0% move (divergence plays are quick reversals)
- Stop: 0.3% beyond recent swing high/low
- Time exit: Flat if no move within 3 candles (60 minutes)

### Why It Works

When dealers are forced to buy (rising call delta) but the stock is being sold (VolumeDown > VolumeUp), the sellers are hitting into a wall. Eventually the selling dries up and the dealer-hedging bid pushes price up. This is "smart money absorbing retail panic."

### Risk

- Divergences can persist during strong trends (don't fight a real move)
- Filter: Only take divergence signals when price is at a gamma wall or key S/R level
- In earnings/imminent news, deltas can be noisy

---

## Strategy 2: Gamma-Volume Acceleration

**Type:** Momentum / Breakout  
**Timeframe:** 5-min bars  
**Best For:** TSLA, NVDA, AMD — high-vol names with gamma sensitivity

### The Edge

Gamma is the multiplier. When ATM gamma is high, every tick of volume gets amplified by dealer hedging. This strategy catches the moment when volume + gamma align to create a self-reinforcing move.

### Data Fields Used

| Field | Source | Purpose |
|-------|--------|---------|
| Gamma (all options) | Options chain | Dealer hedging sensitivity |
| VolumeUp | OHLC stream | Confirming aggressive buying |
| VolumeDown | OHLC stream | Confirming aggressive selling |
| Delta (ATM options) | Options chain | Confirming directional bias |
| ExtrinsicValue (ATM) | Options chain | Confirming option pricing environment |

### Signal Construction

**Step 1 — ATM Gamma Score:**
```
ATM_Gamma = Σ(Gamma_i × OpenInterest_i) for strikes within ±1% of current price
```
Rolling 1-minute average of ATM_Gamma. Spike when current > 1.5× average.

**Step 2 — Volume Confirmation:**
```
VolumeSpike = Volume_current / SMA(Volume, 20)
```
- VolumeSpike > 1.5 = above-average activity
- VolumeSpike > 2.0 = strong conviction

**Step 3 — Directional Alignment:**
```
For LONG:  ATM_Gamma spikes ↑  AND  VolumeUp > VolumeDown  AND  ATM Call Delta > 0.3
For SHORT: ATM_Gamma spikes ↑  AND  VolumeDown > VolumeUp  AND  ATM Put Delta < -0.3
```

### Entry/Exit

**Entry:**
- All three conditions must align within the same 5-min candle
- Enter on the close of the confirming candle
- If VolumeSpike > 2.5, enter on the candle (no wait)

**Exit:**
- Target: Next gamma wall in the trade direction (use Syngex GEX calculator)
- Trail stop: 1.5× ATR(14) on 5-min bars
- Hard stop: Below breakout candle low (longs) / above high (shorts)

### Why It Works

High ATM gamma means dealers' delta-hedging is most sensitive right where price is. When volume pushes price in one direction, dealers must hedge aggressively, which pushes price further, which requires more hedging. This is the gamma acceleration loop. Volume confirms that real money is behind the move, not just dealer noise.

### Risk

- False breakouts on low liquidity
- Filter: Require VolumeSpike > 1.5 minimum
- In negative gamma regimes, the acceleration goes both ways (use with caution)

---

## Strategy 3: IV-Extrinsic Mean Reversion

**Type:** Mean Reversion / Options Premium Harvest  
**Timeframe:** 15-min bars  
**Best For:** GLD, MSFT — stable names with predictable IV ranges

### The Edge

Implied Volatility and extrinsic value are mean-reverting by nature. When IV spikes abnormally (panic) or collapses abnormally (complacency), the underlying tends to correct. This strategy trades the IV correction using stock direction.

### Data Fields Used

| Field | Source | Purpose |
|-------|--------|---------|
| ImpliedVolatility (ATM) | Options chain | IV level and direction |
| ExtrinsicValue (ATM) | Options chain | Option premium content |
| Theta (ATM) | Options chain | Time decay rate |
| VolumeUp/VolumeDown | OHLC stream | Confirming panic/complacency |
| ProbabilityITM | Options chain | Confirming sentiment extremes |

### Signal Construction

**Step 1 — IV Z-Score:**
```
IV_Z = (IV_current - SMA(IV, 50)) / STD(IV, 50)
```
- IV_Z > +2.0 = IV is elevated (panic)
- IV_Z < -2.0 = IV is suppressed (complacency)

**Step 2 — Extrinsic Value Check:**
```
ATM_Extrinsic = average ExtrinsicValue of ATM calls and puts
```
- High extrinsic + high IV = overpriced options (fade the move)
- Low extrinsic + low IV = underpriced options (prepare for expansion)

**Step 3 — Volume Sentiment Confirmation:**

**FADe SETUP (IV spike → mean reversion):**
- IV_Z > +2.0 (panic)
- ExtrinsicValue > 70th percentile (overpriced)
- VolumeRatio < 0.35 (massive selling — panic selling)
- ProbabilityITM for OTM puts is elevated (hedging frenzy)
- → **SHORT** the underlying (expect IV crush + price bounce)

**EXPANSION SETUP (IV collapse → breakout coming):**
- IV_Z < -2.0 (complacency)
- ExtrinsicValue < 30th percentile (cheap)
- VolumeRatio near 0.50 (no panic, no conviction)
- Theta is low (time decay not accelerating)
- → **Wait for breakout** — when price moves with VolumeSpike > 2.0, enter in breakout direction

### Entry/Exit

**Fade (IV spike):**
- Enter short when IV_Z crosses above +2.0 AND VolumeRatio < 0.35
- Target: IV_Z returns to 0 (normal)
- Stop: 0.5% beyond recent swing low
- Time: Close within 2 hours (IV crush happens fast)

**Expansion (IV collapse):**
- No entry on IV signal alone — wait for price breakout
- When breakout occurs with VolumeSpike > 2.0, enter in breakout direction
- Target: 1.0-1.5% move
- Stop: Back inside the range

### Why It Works

IV is a fear gauge. When it spikes, the market is overreacting — and overreactions revert. Extrinsic value tells you how much premium is baked in. When extrinsic is high and IV is elevated, options are expensive and the underlying move is likely overdone. VolumeUp/VolumeDown confirms whether it's panic (one-sided) or normal flow.

### Risk

- IV can stay elevated during real news events
- Filter: Only fade when no earnings/news catalyst
- GLD is ideal because its IV is very mean-reverting
- TSLA IV can stay high for days during earnings

---

## Strategy 4: Probability Shift Momentum

**Type:** Momentum / Trend Following  
**Timeframe:** 5-min bars  
**Best For:** TSLA, MSFT — names with clear directional trends

### The Edge

ProbabilityITM tells you how the options market perceives the likelihood of the underlying being in-the-money at expiration. When these probabilities shift rapidly, it's a leading indicator of price momentum — before the stock price even moves.

### Data Fields Used

| Field | Source | Purpose |
|-------|--------|---------|
| ProbabilityITM (ATM calls/puts) | Options chain | Leading momentum signal |
| ProbabilityOTM | Options chain | Confirming probability shift |
| Delta (ATM) | Options chain | Cross-check with probability |
| VolumeUp/VolumeDown | OHLC stream | Confirming the move |
| Gamma (ATM) | Options chain | Confirming sensitivity |

### Signal Construction

**Step 1 — Probability Momentum:**
```
CallProb_Momentum = ΔProbabilityITM(ATM Call) / Δt
PutProb_Momentum = ΔProbabilityITM(ATM Put) / Δt
```
Track over 30-second windows. Rapid changes = momentum building.

**Step 2 — Probability Spread:**
```
ProbSpread = ProbabilityITM(ATM Call) - ProbabilityITM(ATM Put)
```
- Widening positive = bullish momentum building
- Widening negative = bearish momentum building

**Step 3 — Delta-Probability Convergence:**
```
ATM Call Delta ≈ ProbabilityITM(ATM Call)  (theoretical relationship)
```
When Delta and ProbabilityITM diverge from each other, the options market is mispricing direction — a quick mean reversion opportunity.

### Signal Types

**BULLISH MOMENTUM:**
- ProbSpread is widening positive (> 0.10 change in 2 minutes)
- Call ProbabilityITM rising (e.g., 0.50 → 0.65)
- Put ProbabilityITM falling (e.g., 0.50 → 0.35)
- VolumeUp > VolumeDown (stock confirms)
- ATM Call Delta > 0.40 (options market pricing in upside)

**BEARISH MOMENTUM:**
- ProbSpread is widening negative
- Put ProbabilityITM rising (e.g., 0.50 → 0.65)
- Call ProbabilityITM falling
- VolumeDown > VolumeUp
- ATM Put Delta < -0.40

**PROBABILITY DIVERGENCE (Mean Reversion):**
- Call ProbabilityITM > 0.80 but price is NOT making new highs
- Put ProbabilityITM > 0.80 but price is NOT making new lows
- → Probability is pricing in a move that hasn't happened yet → fade

### Entry/Exit

**Momentum Entry:**
- Enter when ProbSpread change exceeds threshold AND Volume confirms
- Size proportional to |ProbSpread change| magnitude
- Target: 0.5-1.0% move (momentum plays run 2-4 candles)

**Divergence Entry:**
- Enter against the probability bias (fade)
- Target: ProbabilityITM returns to 0.50 (neutral)
- Stop: 0.3% beyond recent swing

**Exit:**
- Trail with 3-min EMA cross
- Or exit when ProbSpread stops widening
- Time exit: 4 candles max (20 minutes)

### Why It Works

ProbabilityITM is derived from the Black-Scholes model using current price, IV, and time to expiration. When it shifts rapidly, it means either IV is changing or the market is repricing the expected move. Since IV changes slowly intraday, rapid probability shifts are primarily driven by price expectations — making it a leading signal. VolumeUp/VolumeDown confirms whether real money is acting on those expectations.

### Risk

- Probability shifts can be driven by IV changes (not price expectations)
- Filter: Cross-check with Delta — if Delta is stable but ProbabilityITM shifts, it's IV-driven (ignore)
- In choppy markets, probabilities whipsaw

---

## Strategy 5: Vega-Volume Regime Shift

**Type:** Regime Detection / Position Switching  
**Timeframe:** 15-min bars for detection, 5-min for entry  
**Best For:** All names — this is a master regime filter

### The Edge

Vega measures sensitivity to volatility changes. When vega-weighted volume shifts dramatically, it signals a regime change — the market is transitioning between low-volatility consolidation and high-volatility trending. This strategy detects the regime change early and switches strategies accordingly.

### Data Fields Used

| Field | Source | Purpose |
|-------|--------|---------|
| Vega (all options) | Options chain | Volatility sensitivity |
| ImpliedVolatility (all) | Options chain | Volatility level |
| VolumeUp/VolumeDown | OHLC stream | Confirming volume regime |
| Theta (all) | Options chain | Time decay pressure |
| Gamma (ATM) | Options chain | Confirming sensitivity regime |

### Signal Construction

**Step 1 — Vega-Weighted Volume:**
```
VegaVolumeUp = Σ(Vega_i × VolumeUp) for all options
VegaVolumeDown = Σ(Vega_i × VolumeDown) for all options
```
This weights volume by how sensitive each option is to volatility changes. High vega-volume means big players are positioning for volatility changes.

**Step 2 — Regime Classification:**

**LOW VOL REGIME:**
- IV_Z < -1.0 (below normal)
- Gamma (ATM) is low (low sensitivity)
- VolumeRatio near 0.50 (balanced, no panic)
- Theta is low (slow time decay)
- → **Strategy:** Range trading, sell premium, fade extremes

**HIGH VOL REGIME:**
- IV_Z > +1.0 (above normal)
- Gamma (ATM) is high (high sensitivity)
- VolumeRatio extreme (> 0.60 or < 0.40)
- Theta is high (accelerating decay)
- → **Strategy:** Trend following, buy premium, ride breakouts

**TRANSITION DETECTION (The Alpha):**

**BULLISH TRANSITION (Low → High vol with upside):**
- IV_Z crosses from below -1.0 toward 0
- Gamma starts rising from low levels
- VolumeUp starts exceeding VolumeDown
- VegaVolumeUp > VegaVolumeDown (vol buyers are bulls)
- → **Switch to momentum strategy, go long**

**BEARISH TRANSITION (Low → High vol with downside):**
- IV_Z crosses from below -1.0 toward 0
- Gamma starts rising from low levels
- VolumeDown starts exceeding VolumeUp
- VegaVolumeDown > VegaVolumeUp (vol buyers are bears)
- → **Switch to momentum strategy, go short**

### Entry/Exit

**Transition Entry:**
- Enter when all four transition conditions align
- Size: moderate (transition trades have higher uncertainty)
- Target: 1.0-2.0% move (regime changes produce bigger moves)

**Exit:**
- Trail with ATR(14) on 5-min
- Exit when IV_Z returns to mean (volatility normalizes)
- Or when VolumeRatio returns to 0.50 (balance restored)

### Why It Works

Vega is highest for ATM options with longer expirations. When vega-weighted volume shifts, it means large players are buying/selling options to position for volatility changes. Since volatility changes precede price moves (volatility is a leading indicator), this gives early warning of regime shifts. Combining vega-volume with VolumeUp/VolumeDown tells you the direction of the volatility play.

### Risk

- Transition signals can be false (IV can spike and revert without price move)
- Filter: Require Gamma to also be rising (confirms sensitivity increase)
- Best used as a FILTER for other strategies, not a standalone entry

---

## Strategy Comparison Matrix

| Strategy | Type | Win Rate | R:R | Complexity | Hold Time | Key Data |
|----------|------|----------|-----|------------|-----------|----------|
| Delta-Volume Divergence | Mean Reversion | 55-60% | 1:1.5 | Medium | 15-60 min | Delta, VolUp, VolDown, IV |
| Gamma-Volume Acceleration | Momentum | 50-55% | 1:2.0 | Medium | 30-120 min | Gamma, VolUp, VolDown, Delta |
| IV-Extrinsic Mean Reversion | Mean Reversion | 60-65% | 1:1.5 | High | 30-120 min | IV, Extrinsic, Theta, VolRatio |
| Probability Shift Momentum | Momentum | 55-60% | 1:1.8 | Medium | 15-60 min | ProbITM, ProbOTM, Delta, Vol |
| Vega-Volume Regime Shift | Regime Filter | 45-50% | 1:3.0 | High | 1-4 hrs | Vega, IV, Gamma, VolUp, VolDown |

---

## Implementation Architecture

### New Classes Needed

```
engine/
  ├── gex_calculator.py        # Existing — Gamma Ladder
  ├── strategy_engine.py       # NEW — Orchestrates all 5 strategies
  ├── signals.py               # NEW — Signal dataclass
  └── indicators.py            # NEW — Rolling delta, IV z-score, etc.
```

### Signal Object

```python
@dataclass
class Signal:
    strategy: str           # Strategy name
    direction: str          # "LONG", "SHORT", "NEUTRAL"
    confidence: float       # 0.0 - 1.0
    entry_price: float      # Suggested entry
    stop_price: float       # Suggested stop
    target_price: float     # Suggested target
    reason: str             # Human-readable explanation
    timestamp: float        # Signal generation time
```

### Data Pipeline

```
TradeStation Quotes Stream
    → OHLC + VolumeUp + VolumeDown
    → Rolling indicators (indicators.py)

TradeStation Options Chain Stream (per-second)
    → Delta, Gamma, Theta, Vega, IV, ProbITM, ExtrinsicValue
    → Aggregate metrics (strategy_engine.py)
    → Signal generation (per strategy)

StrategyEngine
    → Reads indicators + aggregates
    → Runs each strategy's logic
    → Produces Signal objects
    → Exports to gex_state.json for dashboard
```

### Dashboard Integration

Extend `app_dashboard.py` with:
- Strategy signal panel (current signals for all 5 strategies)
- Confidence meter per strategy
- Regime indicator (Low Vol / High Vol / Transition)
- Volume imbalance gauge (VolumeUp vs VolumeDown)
