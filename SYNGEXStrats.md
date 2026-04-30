# Syngex Strategy Blueprint: The Evolutionary Hierarchy

This document organizes our trading intelligence into three distinct layers of complexity, moving from structural market mechanics to high-frequency micro-signals.

---

## 🏗️ Layer 1: The Structural Foundation (GEX + OHLC)
*Focus: Trading the "Gravity" of the market. These strategies use the physical structure of the Gamma Ladder to identify support, resistance, and regime shifts.*

### 🧱 Gamma Wall Bounce (Mean Reversion)
* **Concept:** Price gravitates toward massive GEX strikes (Call/Put Walls). Dealers sell rallies at Call Walls and buy dips at Put Walls.
* **Logic:** Identify high-GEX walls. When price approaches within 0.5% and shows an OHLC rejection (e.g., shooting star, hammer) with volume confirmation, trade the bounce.
* **Stop:** 0.3-0.5% past the wall. **Target:** Midpoint between walls or opposite wall.
* **Best For:** GLD, MSFT (Stable walls). 60-65% win rate, 1:1.5 RR.

### 🧲 Magnet & Accelerate (Two-Phase)
* **Concept:** The highest GEX strike is the gravitational center. Phase 1: trade toward it. Phase 2: if it breaks, ride the acceleration.
* **Logic:**
  * **Phase 1 — Magnet Pull:** Price below magnet + net gamma positive → go long, targeting magnet. Use 5-min EMA(9)/EMA(21) crossover for entry. Exit within 0.3% of magnet or when GEX weakens.
  * **Phase 2 — Acceleration:** Price breaks magnet + volume > 2× average + cumulative gamma turns negative → enter breakout direction with RSI confirmation. Trail aggressively (1× ATR).
* **Best For:** TSLA, NVDA (strong magnet behavior).

### 🔄 Gamma Flip Breakout (Regime Trend)
* **Concept:** The Gamma Flip is the boundary between a stabilizing regime (Positive Gamma) and an accelerating regime (Negative Gamma).
* **Logic:**
  * **Above Flip:** Fade breakouts; look for pullbacks to EMA/VWAP.
  * **Below Flip:** Trade breakouts; price acceleration is fueled by dealer hedging.
* **Stop:** Other side of flip or 1.5× ATR. **Target:** Next gamma wall (1:2.5 RR).
* **Best For:** TSLA, NVDA (High volatility, frequent flip crossings). 45-50% win rate but 1:2.5 RR makes it profitable.

### 🐍 Gamma Squeeze / Wall-Breaker (Momentum)
* **Concept:** When price is trapped between walls (Pinning) and then breaks through a massive Call Wall, the "trap door" opens.
* **Logic:** Pin detection (ATR < 0.3%, net gamma positive, between walls) + breakout candle close beyond wall + volume spike + negative gamma confirmed → enter squeeze. Net gamma flip at breakout = dealer hedging accelerates the move.
* **Best For:** TSLA, NVDA (High-velocity momentum).

### 📊 GEX Imbalance Play (Positioning Bias)
* **Concept:** Call/Put GEX ratio reveals dealer bias independent of price action.
* **Logic:**
  * Put-heavy ratio (<0.4) → dealers must buy to hedge → long bias
  * Call-heavy ratio (>0.6) → dealers must short → short bias
  * Trade with VWAP trend confirmation
* **Best For:** All liquid equities. 50-55% win rate.

### 🎯 Confluence Reversal (Double-Stacked)
* **Concept:** When technical S/R (VWAP, EMA, daily highs/lows) aligns with a Gamma Wall or Flip within 0.3%, that's a double-stacked level.
* **Logic:** Score confluence levels 1-3 (technical level = 1, gamma wall = 1, flip = 1). Only trade levels with score ≥ 2. Price bounces hard off confluence zones.
* **Best For:** All three — filters entries across every other strategy. 55-65% win rate, 1:2.0 RR.

### 🌊 Net Gamma Regime Filter (Master Filter)
* **Concept:** Net gamma sign is your master filter. Don't fight the regime.
* **Logic:**
  * **Positive (>0):** Dealers buy dips, sell rallies → fade extremes, range-bound strategies only
  * **Negative (<0):** Dealers sell dips, buy rallies → trend-follow, breakout-biased strategies only
  * **Filter rule:** Only take longs in positive gamma when price > flip. Only take shorts in negative gamma when price < flip.
* **Best For:** All three — TSLA (switches regimes intraday), GLD (stays positive most days), MSFT (stable positive gamma).

### 📉 Volatility Compression Range Trade (Vol Selling)
* **Concept:** In a "Long Gamma" regime (Price > Flip), market makers' hedging dampens volatility. Sell it.
* **Logic:** Confirm positive gamma regime + Bollinger Band squeeze or RSI extremes. Sell vol (Iron Condors or Credit Spreads) or scalp range edges — the structural Long Gamma environment fights large breakouts.
* **Best For:** GLD, MSFT (Lower vol, steady institutional flows).

---

## 📈 Layer 2: The Alpha Layer (Greeks + Order Flow)
*Focus: Trading the "Conviction" of the market. These strategies detect when the price action contradicts the underlying options positioning.*

### ⚖️ GEX Divergence (The Fade)
* **Concept:** Finding exhaustion by comparing price trend vs. GEX trend.
* **Logic:** If Price ↑ but Total GEX ↓ (walls evaporating), the trend is losing structural support. Enter fade on OHLC confirmation.
* **Best For:** High-beta equities during news/earnings.

### 📊 Delta-Gamma Squeeze (Extreme Momentum)
* **Concept:** The "engine room" of a squeeze — a violent feedback loop between rapid Delta hedging and high Gamma.
* **Logic:** Price approaches Call Wall + Delta of contracts at that strike accelerates non-linearly + VolumeUp spike on breakout above wall → enter long. Exit when Delta plateaus or IV spikes (overextended squeeze).
* **Best For:** TSLA, NVDA (violent squeeze plays).

### 🔀 Delta-Volume Exhaustion (Trend Reversal)
* **Concept:** Identify when a trend is "running out of gas" via Delta + Volume divergence.
* **Logic:** Strong trending move (3-4 consecutive candles) + Delta of trend-following contracts declining + VolumeUp declining → fade the move (reverse). Exit at next gamma wall or fixed R:R.
* **Best For:** Any trending stock showing weakening conviction.

### 🔀 Call/Put Flow Asymmetry (Positioning Bias)
* **Concept:** Real-time ratio of Call vs. Put volume/gamma/delta to detect dealer bias.
* **Logic:** Calculate Flow Score every 10s: `Call Score = (Call Vol × Call Gamma × Call Delta) / (Put Vol × Put Gamma × Put Delta)`. Long when Call Score > 1.5× Put Score + VolumeUp dominant + call IV < put IV. Short when inverse. Track bid/ask size ratio for conviction confirmation.
* **Best For:** TSLA (Huge flow swings).

### 🎯 Delta-IV Divergence (Sentiment Shift)
* **Concept:** Detecting shifts in market "fear" vs. "intent."
* **Logic:** If Delta is increasing on a strike but IV is dropping, it indicates high-conviction directional accumulation (smart money buying before the crowd).
* **Best For:** Rapidly moving momentum stocks.

### 🌊 IV-GEX Divergence (Volatility Mean Reversion)
* **Concept:** Price makes new high but IV for nearest OTM strikes is crashing — the market is pricing in calm continuation or reversal.
* **Logic:** Price at High + IV crashing + Net Gamma strongly positive → short the underlying (or buy puts). Exit at major Gamma Wall or RSI overbought divergence.
* **Best For:** High-beta stocks during "melt-up" or "melt-down" exhaustion.

### 🔀 IV Skew Squeeze (Sentiment Reversal) — *v2 Full-Data*
* **Concept:** IV Skew = IV of OTM puts minus IV of OTM calls. When skew is extreme, the market is pricing a disaster that hasn't happened yet.
* **Logic:**
  * Skew > 0.30 (puts 30% more expensive) + price not breaking down → long (panic overblown, skew normalizes)
  * Skew < -0.10 (calls more expensive) + price not breaking out → short (euphoria overblown)
  * Entry: Skew crosses back toward zero + candle close confirms
* **Best For:** Earnings week, news events. 1-4hr hold.

---

## ⚡ Layer 3: The Micro-Signal Layer (1Hz High-Frequency)
*Focus: Trading the "Reaction." These strategies exploit the sub-second bursts of data provided by the 1Hz stream to catch the exact moment of dealer re-hedging.*

### 📊 Gamma-Volume Convergence (GVC)
* **Concept:** Detecting the exact second a gamma spike meets a volume surge.
* **Logic:** Monitor 1Hz stream for sudden spikes in Δ or Γ at specific strikes coinciding with `VolumeUp`. This is the "ignition" signal for a squeeze.
* **Best For:** Scalping high-velocity breakouts.

### 🌊 IV Band Breakout (Compression Expansion)
* **Concept:** Exploiting the transition from IV compression to expansion.
* **Logic:** IV in bottom 25% of 30m range + Price Compression (high-low < 30% of 20-period ATR) + Theta more negative than 30m avg → breakout: Price breaks OHLC high + VolumeUp + Delta turning positive → Long. Break low + VolumeDown + Delta negative → Short.
* **Best For:** TSLA, GLD (Predictable compression/expansion cycles).

### 📊 Strike Concentration Scalp (Micro-Reaction)
* **Concept:** Trading the immediate reaction to the most active strikes.
* **Logic:** Pre-market: identify top 3 strikes by total contracts. Intraday: bounces off strike (wick/reversal candle) → trade bounce opposite. Slices through (strong candle, high volume) → ride momentum. Larger size on #1 strike. Best in first 2 hours and last hour.
* **Best For:** MSFT, GLD (Highly liquid, clean strike reactions).

### 🔥 Theta-Burn Scalp (The Pinning Effect)
* **Concept:** In a high-GEX, low-volatility environment, time becomes the friend of the range-trader.
* **Logic:** Strongly positive gamma regime + High aggregate Theta + Price oscillating in narrow range → sell rips (short moves to Call Walls) and buy dips (long moves to Put Walls). Very quick targets (0.2-0.4%) or when IV expands.
* **Best For:** GLD, MSFT during midday lull. 3-8 min holds.

### 🎯 Probability-Weighted Magnet (Smart Money Flow) — *v2 Full-Data*
* **Concept:** Use ProbabilityITM + Open Interest to find where "smart money" is positioning, not just where GEX is highest.
* **Logic:** Scan for strikes where ProbabilityITM rises rapidly but Price hasn't moved yet + High OI at those strikes + Price consolidating (low volume/narrow range) → anticipatory entry. Exit when price slices through the strike.
* **Best For:** All three. Detects stealth accumulation before price reacts.

### 📊 Probability Distribution Shift (Full Distribution) — *v2 Full-Data*
* **Concept:** Probability ITM across all strikes shifts asymmetrically before price moves.
* **Logic:** Calculate "Probability Momentum" = Σ(ΔProbITM × ΔStrike) across all strikes. Positive momentum = mass shifting right (bullish). Negative = shifting left (bearish). Enter when >2σ for 3+ consecutive seconds + volume confirms.
* **Best For:** All three. Leading indicator — market's view changes before price does.

### 💰 Extrinsic/Intrinsic Flow (New Money Tracking) — *v2 Full-Data*
* **Concept:** Extrinsic value expansion = new money entering with conviction. Collapse = money leaving.
* **Logic:**
  * **Expansion:** Extrinsic value +5% in 5min + volume >150% avg + VolumeUp/Down directional confirmation → enter in volume direction
  * **Collapse:** Extrinsic dropping + volume declining → exit or fade remaining momentum
  * **Theoretical vs Market:** Theoretical < Market bid on calls → calls cheap → bullish. Theoretical > Market ask on puts → puts expensive → bearish.
* **Best For:** All three. Tracks conviction, not just direction.

---

## 🏷️ Gamma Magnet Zone (Sub-Strategies)
*These are specialized variations that slot into Layer 1 strategies.*

### Magnet Zone Scalp
* In positive gamma, price oscillates between two surrounding walls like a rubber band. Trade the range: buy lower third, sell upper third using RSI(7) on 2-min bars. 3-8 min holds, 0.3-0.6% targets. Best during 11:30-2:30 ET lull.

---

## 🛠️ Implementation Roadmap

1. **Data Aggregator:** Extend `GEXCalculator` to support rolling windows of Delta, IV, Theta, ProbabilityITM, ExtrinsicValue.
2. **Strategy Engine:** Create a `StrategyEngine` to evaluate all rules against the incoming 1Hz stream.
3. **Signal Overlay:** Update `GammaMagnetView` to display "Strategy Confidence" (e.g., 🟢 *Squeeze Prob: 85%*) directly on the heatmap.
4. **Filter Pipeline:** Net Gamma Regime Filter runs first — routes signals to appropriate strategy pool (fade vs. trend).

---

## 📋 Master Strategy Index

| # | Strategy | Layer | Key Data | Signal Type | Hold Time |
|---|----------|-------|----------|-------------|-----------|
| 1 | Gamma Wall Bounce | 1 | GEX + OHLC | Mean Reversion | 15-30 min |
| 2 | Magnet & Accelerate | 1 | GEX + EMA + Volume | Two-Phase | 5-60 min |
| 3 | Gamma Flip Breakout | 1 | Flip + GEX + OHLC | Regime Trend | 15-60 min |
| 4 | Gamma Squeeze / Wall-Breaker | 1 | GEX + OHLC + Volume | Momentum | 5-30 min |
| 5 | GEX Imbalance | 1 | Call/Put GEX Ratio | Positioning Bias | 15-45 min |
| 6 | Confluence Reversal | 1 | Technical S/R + Gamma | Double-Stacked | 15-60 min |
| 7 | Net Gamma Regime Filter | 1 | Net Gamma Sign | Master Filter | N/A (filter) |
| 8 | Vol Compression Range | 1 | Positive Gamma + BB | Vol Selling | 30-120 min |
| 9 | GEX Divergence | 2 | Price vs GEX | Fade | 15-60 min |
| 10 | Delta-Gamma Squeeze | 2 | Δ + Γ + VolumeUp | Extreme Momentum | 5-30 min |
| 11 | Delta-Volume Exhaustion | 2 | Δ + Volume + OHLC | Reversal | 15-45 min |
| 12 | Call/Put Flow Asymmetry | 2 | Call/Put Vol/Gamma/Delta | Directional | 5-60 min |
| 13 | Delta-IV Divergence | 2 | Delta + IV | Sentiment Shift | 15-60 min |
| 14 | IV-GEX Divergence | 2 | Price + IV + GEX | Vol Mean Reversion | 15-45 min |
| 15 | IV Skew Squeeze | 2 | IV Skew + Volume | Sentiment Reversal | 1-4 hr |
| 16 | Gamma-Volume Convergence | 3 | Δ/Γ spike + VolumeUp | Ignition | 5-15 min |
| 17 | IV Band Breakout | 3 | IV + OHLC range + Theta | Breakout | 10-45 min |
| 18 | Strike Concentration Scalp | 3 | Top OI strikes + OHLC | Micro-Reaction | 3-15 min |
| 19 | Theta-Burn Scalp | 3 | Theta + GEX + OHLC | Pin Trading | 3-8 min |
| 20 | Prob-Weighted Magnet | 3 | ProbITM + OI + OHLC | Stealth Accumulation | 15-45 min |
| 21 | Prob Distribution Shift | 3 | Full ProbITM distribution | Leading Indicator | 30min-2hr |
| 22 | Extrinsic/Intrinsic Flow | 3 | Extrinsic + Intrinsic + Vol | Conviction Tracking | 15min-3hr |

---

**Total: 22 distinct strategies across 3 layers + 1 sub-strategy.**

All can run on top of the existing Syngex architecture. The 1Hz options data gives us the ability to detect micro-signals — gamma spikes lasting 2-3 seconds, IV changes between candles, and call/put flow imbalances resolving within minutes.
