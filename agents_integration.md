# Agents → Syngex Integration Plan

**Created:** 2026-06-23
**Status:** Planning
**Purpose:** Design doc for converting ~120 years of cumulative EA development (`~/projects/agents/`) into syngex-native Python strategies — without modifying trading logic, just porting it.

---

## Background

`~/projects/agents/` contains three fully-designed, fully-tested technical analysis strategies originally built for TradeStation EasyLanguage (.el files) and a GUI scanner frontend. They represent 3+ years of iterative refinement across momentum reversal, trend breakout, and volatility squeeze paradigms.

Syngex runs ~30+ options-flow strategies (GEX, IV, depth-book, gamma walls). It already streams underlier price updates via the TS client but doesn't compute equity TA indicators. This plan bridges the gap by adding a shared indicator layer that both legacy strategy conversions and future new strategies can draw from.

**Goal:** Port the three agents strategies into syngex without rewriting their trading logic — only translating .el → Python + plugging into the existing signal pipeline.

---

## Current State Comparison

| Dimension | ~/projects/agents/ | ~/projects/syngex/ |
|---|---|---|
| Language | EasyLanguage (.el) | Python |
| Data source | TradeStation API + CSV indicators | TradeStation option chain + level2 + underlying price |
| Strategy model | Monolithic `.el` file (entry/exit SL/TP all inline) | Pluggable `BaseStrategy.evaluate(data)` → `Signal()` |
| Config | Hardcoded inputs in `.el` | YAML (`config/strategies.yaml`) + per-strategy params |
| Indicators | 5-8 per strategy, defined inline | None — GEX/IV focused only |
| Execution | Direct market orders | Signal → filter → Command Center |
| Output | Trade log CSV | JSONL signals + dashboard |

The core insight: **syngex already has the price data**. The TS client dispatches `underlying_update` events with bid/last price per-ticker. We just need an indicator calculator on top of that stream.

---

## Architecture Overview

```
TS Client ──price──> Engine ──OHLCV rollup──> IndicatorManager
                                                    │
                                ┌───────────────────┼───────────────────┐
                                │                   │                   │
                         strat1_eval()      strat2_eval()       strat3_eval()
                           │     │              │     │             │     │
                     rsi(14),bb(20)    stoch(14)   adx(14)  supertrend(7) donchian(20) keltner(20,1.5)
                                │                   │                   │
                                ▼                   ▼                   ▼
                          Signal(conference...)  Signal(...)        Signal(...)
                                │                   │                   │
                                └───────────────────┼───────────────────┘
                                                    ▼
                                         Net Gamma Filter (optional)
                                                    ▼
                                             Signal output (JSONL)
```

### Key Design Decision: Shared IndicatorManager

All indicators live in a single `IndicatorManager` class. Strategies don't create their own indicator instances — they query the shared manager. This means:

- One rolling window per indicator per ticker
- Indicator computation happens exactly once per tick
- Parameters are unified from YAML config, not scattered across strategy files

---

## Component Breakdown

### 1. Indicator Manager (`strategies/utils/indicators.py`)

A centralized calculator maintaining per-symbol, per-indicator state.

```python
class IndicatorManager:
    """
    Computes and caches TA indicators for a set of tickers.
    Consumes OHLCV updates and exposes computed values on demand.
    """

    def __init__(self, config: Dict[str, Any]):
        # Parse global config for indicator defaults
        self._global_params = config.get("indicators", {})
        self._ticker_indicators: Dict[str, TickerIndicators] = {}

    def update(self, symbol: str, timestamp: float, open_: float, high: float, low: float, close: float, volume: int):
        """Called by engine for every OHLCV event. Updates all indicators for the symbol."""
        if symbol not in self._ticker_indicators:
            self._ticker_indicators[symbol] = TickerIndicators(self._global_params)
        self._ticker_indicators[symbol].update(open_, high, low, close, volume, timestamp)

    def get_values(self, symbol: str) -> Dict[str, Any]:
        """Return computed indicator values for a ticker. Called by strategy.evaluate()."""
        ...

    def _make_indicator_key(self, name: str, config_override: Optional[Dict] = None) -> str:
        """Generate unique key considering parameter hash (see section 2)."""
        ...
```

### 2. Parameter Resolution Strategy

This is the critical design choice: **how do we handle different strategies wanting different parameters for the same indicator?**

**Option A: Single global instance per indicator name** ⭐ RECOMMENDED
- One `rsi_14`, one `stoch_14_3_3`, etc.
- Strategies declare which "version" they need by referencing its configured parameters
- If two strategies want different RSI lengths, they're treated as separate named instances

```yaml
indicators:
  rsi:
    defaults: { length: 14 }
    instances:
      standard: { length: 14 }
      fast: { length: 9 }
      slow: { length: 21 }
  bb:
    defaults: { length: 20, std_dev: 2.0 }
    instances:
      standard: { length: 20, std_dev: 2.0 }
      tight: { length: 20, std_dev: 1.5 }
  stoch:
    defaults: { k_length: 14, d_period: 3, slowing: 3 }
    instances:
      standard: { k_length: 14, d_period: 3, slowing: 3 }
  adx:
    defaults: { length: 14 }
    instances:
      standard: { length: 14 }
  atr:
    defaults: { length: 14 }
    instances:
      standard: { length: 14 }
      fast: { length: 7 }
  macd:
    defaults: { fast: 12, slow: 26, signal: 9 }
    instances:
      standard: { fast: 12, slow: 26, signal: 9 }
  super_trend:
    defaults: { length: 7, multiplier: 2.5 }
    instances:
      standard: { length: 7, multiplier: 2.5 }
      aggressive: { length: 5, multiplier: 2.0 }
  donchian:
    defaults: { length: 20 }
    instances:
      standard: { length: 20 }
      short: { length: 10 }
  keltner:
    defaults: { ema_length: 20, atr_mult: 1.5, atr_length: 14 }
    instances:
      standard: { ema_length: 20, atr_mult: 1.5, atr_length: 14 }
```

Each strategy then references its needed instances:

```yaml
strategies:
  momentum_reversal:
    enabled: true
    indicators_used:
      - name: rsi
        instance: standard
      - name: stoch
        instance: standard
      - name: bb
        instance: standard
      - name: adx
        instance: standard
      - name: atr
        instance: standard
      - name: macd
        instance: standard
    signal_params:
      rsi_oversold: 28
      rsi_overbought: 72
      adx_ranging_max: 20
      bb_entry_lower: true
      exit_on_regime_change: true
      stop_multiplier: 2.0
      tp1_band: middle
      tp2_band: opposite
  trend_breakout:
    enabled: false
    indicators_used:
      - name: adx
        instance: standard
      - name: super_trend
        instance: standard
      - name: donchian
        instance: standard
      - name: macd
        instance: standard
      - name: atr
        instance: standard
    signal_params:
      adx_trending_min: 23
      di_gap_threshold: 3
      volume_conviction: 1.75
      stop_multiplier: 2.0
      target_multiplier: 1.5
      trailing_enable: true
  vol_squeeze:
    enabled: false
    indicators_used:
      - name: bb
        instance: standard
      - name: keltner
        instance: standard
      - name: atr
        instance: standard
    signal_params:
      squeeze_confirmed_when_bb_inside_kc: true
      breakout_requires_volume_confirmation: true
      min_squeeze_duration_bars: 10
      stop_multiplier: 2.0
      tp_target_mult: 2.0
```

**Why Option A over Option B:** Simpler implementation, less memory, shared state means fewer calculations. The tradeoff is slight YAML verbosity — but each named instance is human-readable and reusable across strategies.

### 3. Underlying Indicator Calculator

Internal helper that maintains per-indicator rolling windows:

```python
class IndicatorCalculator:
    """
    Thread-safe rolling-window calculator for individual TA indicators.

    All methods return partial results gracefully — missing values are
    None, not exceptions. Strategies check for None before acting.
    """

    # Required data points before first valid output
    WARMUP_BARS = {"rsi": 14, "stoch": 14, "bb": 20, "adx": 14, "atr": 14,
                   "macd": 26, "super_trend": 7, "donchian": 20, "keltner": 20}

    def __init__(self, name: str, params: Dict[str, float], ohlcv_window: RollingWindow):
        self.name = name
        self.params = params
        self._window = ohlcv_window  # Shared OHLCV rolling buffer

    def evaluate(self) -> Dict[str, Optional[float]]:
        """Compute all outputs for this indicator given current window state."""
        ...

    # Per-indicator implementations:
    def _calc_rsi(self) -> Optional[float]: ...
    def _calc_stochastic(self) -> Tuple[Optional[float], Optional[float]]: ...  # K, D
    def _calc_bollinger(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]: ...  # upper, mid, lower, %B
    def _calc_adx(self) -> Tuple[Optional[float], Optional[float], Optional[float]]: ...  # DI+, DI-, ADX
    def _calc_atr(self) -> Optional[float]: ...
    def _calc_macd(self) -> Tuple[Optional[float], Optional[float], Optional[float]]: ...  # line, signal, histogram
    def _calc_super_trend(self) -> Tuple[Optional[float], Optional[int]]: ...  # value, direction (+1/-1)
    def _calc_donchian(self) -> Tuple[Optional[float], Optional[float]]: ...  # upper, lower
    def _calc_keltner(self) -> Tuple[Optional[float], Optional[float]]: ...  # upper, lower
```

### 4. Strategy Conversions

Each agent strategy becomes a syngex strategy file. No trading logic changes — only structural translation from .el to Python.

#### `strategies/full_data/momentum_reversal.py`

Corresponds to `Strategy1_MomentumReversal.el`.

**Conversion mapping:**
| .el Logic | Python Equivalent |
|---|---|
| `BuySignal = RSI_Green AND StoX_Green AND BB_Green AND ADX_Green` | Evaluate all 5 conditions → signal if all TRUE |
| `SellSignal = RSI_Red AND StoX_Red AND BB_Red AND ADX_Green` | Same for shorts |
| `if BuySignal then Buy(...)` next bar at Market | Set entry price on signal, execute via syngex execution handler |
| Exit: `MarketPosition=1 and (not RSI_Green or not BB_Green or not ADX_Green)` | On hold, check exit conditions each tick |
| `Stop Loss: Entry - 2×ATR` | Calculated in signal construction |
| `Target 1: Middle BB, Target 2: Upper BB` | Two-tier TP or trail to second target |

**Entry conditions (all must be TRUE simultaneously):**
- RSI ≤ 28 (long) / ≥ 72 (short)
- Stochastic %K crosses above %D (long) / crosses below %D (short)
- Price at/below lower BB (long) / at/above upper BB (short)
- MACD histogram negative & rising (long) / positive & falling (short)
- ADX ≤ 20 (ranging market confirmed)

**Exit conditions:**
- Early exit when any entry condition turns FALSE (mean reversion failed)
- Take profit at middle BB (TP1) and upper/lower BB (TP2)
- Time stop: 3 bars if no profit

**Risk management:**
- Stop: ±2×ATR from entry
- Position size: max 1% account risk per trade
- Max 3 concurrent positions

#### `strategies/full_data/trend_breakout.py`

Corresponds to `Strategy2_TrendBreakout.el`.

**Conversion mapping:**
| .el Logic | Python Equivalent |
|---|---|
| Full confluence entry (6 conditions) | All must be TRUE |
| Stop-loss + take-profit + trail | Three-part exit logic |
| SuperTrend trail exit | Monitor ST direction flip |

**Entry conditions (all must be TRUE simultaneously):**
- ADX ≥ 23 (strong trend)
- +DI − −DI ≥ 3 (directional bias)
- SuperTrend below price (uptrend) / above price (downtrend)
- Price breaks Donchian upper (breakout) / lower (breakdown)
- MACD histogram positive & rising / negative & falling
- Volume ≥ 1.75× 20-period average

**Exit conditions:**
- Stop loss: max(SuperTrendValue, entry ± 2×ATR) — uses SuperTrend floor/ceiling
- Take profit: entry ± 1.5×ATR (limit order)
- Trail: SuperTrend direction flip triggers market exit

**Note:** This is the most sophisticated exit logic of the three — triple exit (stop/TP/trail). In syngex this maps cleanly to Signal properties plus a post-signal monitoring hook in the tracker.

#### `strategies/full_data/volatility_squeeze.py`

Corresponds to `ScanStrat3_VolatilitySqueeze.md` (design-only, no .el file yet).

**Entry conditions:**
- Bollinger Bands inside Keltner Channels (squeeze confirmed)
- BB bandwidth at or near 20-period minimum
- ATR below 20-period average (compression)
- Price breaks out of BB band with volume confirmation

**Exit conditions:**
- Standard SL (e.g., 2×ATR)
- TP based on projected move magnitude
- Monitor for volatility expansion unwinding

**Key adaptation challenge:** Squeeze detection requires comparing BB width to KC width. Both calculators are in `indicators.py`, so the comparison happens purely in strategy logic — no external dependency.

### 5. Signal Generation Pattern

Each converted strategy follows the exact same structure:

```python
class MomentumReversal(BaseStrategy):
    strategy_id = "momentum_reversal"
    layer = "full_data"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        symbols = data["symbols"]
        signals = []

        for sym in symbols:
            indicators = data["indicators"].get_values(sym)

            # Skip warmup
            if indicators["rsi"] is None or indicators["atr"] is None:
                continue

            params = self._params  # loaded from YAML

            # --- Long entries ---
            buy_signal = self._check_buy(indicators, params)
            if buy_signal:
                sl = indicators["close"] - params["stop_multiplier"] * indicators["atr"]
                tp1 = indicators["bb_middle"]  # middle BB band
                tp2 = indicators["bb_upper"]   # upper BB band
                confidence = self._compute_confidence(indicators, params)
                signals.append(Signal(
                    direction=Direction.LONG,
                    confidence=confidence,
                    entry=indicators["close"],
                    stop=sl,
                    target=tp2,  # ultimate target; TP1 handled by partial exit logic
                    symbol=sym,
                    strategy_id=self.strategy_id,
                    reason="Mean reversal: RSI oversold + Stoch cross + BB lower + MACD shift + ranging market",
                    metadata={"rsi": indicators["rsi"], "stoch_k": indicators["stoch_k"],
                              "stoch_d": indicators["stoch_d"], "adx": indicators["adx"],
                              "atr": indicators["atr"], "bb_pctb": indicators["bb_pctb"]},
                ))

            # --- Short entries ---
            sell_signal = self._check_sell(indicators, params)
            if sell_signal:
                sl = indicators["close"] + params["stop_multiplier"] * indicators["atr"]
                tp1 = indicators["bb_middle"]
                tp2 = indicators["bb_lower"]
                confidence = self._compute_confidence(indicators, params)
                signals.append(Signal(
                    direction=Direction.SHORT,
                    confidence=confidence,
                    entry=indicators["close"],
                    stop=sl,
                    target=tp2,
                    symbol=sym,
                    strategy_id=self.strategy_id,
                    reason="Mean reversal: RSI overbought + Stoch cross + BB upper + MACD shift + ranging market",
                    metadata={"rsi": indicators["rsi"], "stoch_k": indicators["stoch_k"],
                              "stoch_d": indicators["stoch_d"], "adx": indicators["adx"],
                              "atr": indicators["atr"], "bb_pctb": indicators["bb_pctb"]},
                ))

        return signals

    def _check_buy(self, indicators, params):
        rsi = indicators["rsi"]
        stoch_k, stoch_d = indicators["stoch_k"], indicators["stoch_d"]
        bb_pctb = indicators["bb_pctb"]
        adx = indicators["adx"]
        mac_hist_rising = indicators["macd_histogram"] > indicators["macd_histogram_prev"]

        return (rsi <= params["rsi_oversold"] and
                stoch_k <= 20 and stoch_k_crossed_above(stoch_d) and
                bb_pctb <= 0.0 and
                adx <= params["adx_ranging_max"] and
                mac_hist_rising)
```

The same pattern repeats for all three strategies, varying only the indicator combinations and threshold logic.

### 6. Data Flow in the Engine

Minimal engine changes to support indicator computation:

```
current flow:
  TS Client ──price_event──> Engine.process_tick(symbol, bid, last, ...)
                                        │
                                        └──> all strategies.evaluate(tick_data)

new flow:
  TS Client ──price_event──> Engine.process_tick(symbol, bid, last, ...)
                                        │
                                        ├──> IndicatorManager.update(symbol, O, H, L, C, V)
                                        │
                                        └──> all strategies.evaluate(tick_data_with_indicators)
                                                │
                                                └──> data["indicators"] = IndicatorManager.get_values(symbol)
```

Engine-level responsibilities:
1. Maintain per-symbol OHLCV aggregation window (bar construction — 1M, 5M configurable)
2. Call `IndicatorManager.update()` before calling strategy evaluate
3. Pass merged `data` dict to strategies

No changes to existing layer 1/2/3 strategies — they'll simply see extra keys in `data` that they ignore.

---

## Configuration Structure (Full)

```yaml
# Top-level additions to config/strategies.yaml

indicators:
  # Global defaults applied when no explicit instance is specified
  rsi:
    defaults: { length: 14 }
    instances:
      standard: { length: 14 }
      fast: { length: 9 }
      slow: { length: 21 }
  stoch:
    defaults: { k_length: 14, d_period: 3, slowing: 3 }
    instances:
      standard: { k_length: 14, d_period: 3, slowing: 3 }
  bb:
    defaults: { length: 20, std_dev: 2.0 }
    instances:
      standard: { length: 20, std_dev: 2.0 }
      tight: { length: 20, std_dev: 1.5 }
  adx:
    defaults: { length: 14 }
    instances:
      standard: { length: 14 }
  atr:
    defaults: { length: 14 }
    instances:
      standard: { length: 14 }
      fast: { length: 7 }
  macd:
    defaults: { fast: 12, slow: 26, signal: 9 }
    instances:
      standard: { fast: 12, slow: 26, signal: 9 }
  super_trend:
    defaults: { length: 7, multiplier: 2.5 }
    instances:
      standard: { length: 7, multiplier: 2.5 }
      aggressive: { length: 5, multiplier: 2.0 }
  donchian:
    defaults: { length: 20 }
    instances:
      standard: { length: 20 }
  keltner:
    defaults: { ema_length: 20, atr_mult: 1.5, atr_length: 14 }
    instances:
      standard: { ema_length: 20, atr_mult: 1.5, atr_length: 14 }

# Existing full_data strategies...

full_data:
  # NEW — converted from agents Strategy1
  momentum_reversal:
    enabled: false
    indicators_used:
      - name: rsi
        instance: standard
      - name: stoch
        instance: standard
      - name: bb
        instance: standard
      - name: adx
        instance: standard
      - name: atr
        instance: standard
      - name: macd
        instance: standard
    signal_params:
      rsi_oversold: 28
      rsi_overbought: 72
      adx_ranging_max: 20
      stop_multiplier: 2.0
      time_stop_bars: 3
      max_positions: 3
      tp1: middle_bb
      tp2: outer_bb
      exit_on_condition_failure: true

  # NEW — converted from agents Strategy2
  trend_breakout:
    enabled: false
    indicators_used:
      - name: adx
        instance: standard
      - name: super_trend
        instance: standard
      - name: donchian
        instance: standard
      - name: macd
        instance: standard
      - name: atr
        instance: standard
    signal_params:
      adx_trending_min: 23
      di_gap_threshold: 3
      volume_conviction: 1.75
      stop_multiplier: 2.0
      target_multiplier: 1.5
      trailing_enable: true
      trail_trigger: super_trend_flip

  # NEW — converted from ScanStrat3
  vol_squeeze:
    enabled: false
    indicators_used:
      - name: bb
        instance: standard
      - name: keltner
        instance: standard
      - name: atr
        instance: standard
    signal_params:
      squeeze_confirm_bb_inside_kc: true
      volume_confirmation_required: true
      min_squeeze_bars: 10
      stop_multiplier: 2.0
      tp_target_mult: 2.0
```

---

## Implementation Phases

### Phase 1: Indicator Framework (Foundation)
**Scope:** `indicators.py` only — no new strategies yet.

Tasks:
1. Create `strategies/utils/indicators.py` with `IndicatorManager` + `IndicatorCalculator`
2. Implement all 9 indicator calculators (RSI, Stoch, BB, ADX, ATR, MACD, SuperTrend, Donchian, Keltner)
3. Handle warmup periods gracefully (return None until enough bars accumulated)
4. Add YAML parsing in engine bootstrap for `indicators.*` config sections
5. Write unit tests for each indicator against known reference values
6. Integrate `IndicatorManager.update()` into engine's tick processing loop

**Deliverable:** Working indicator calculator that can process a year of minute bars and produce correct values for all 9 indicators. Verified against TradingView/Pine Script output.

### Phase 2: Strategy 1 — Momentum Reversal Conversion
**Scope:** Port `.el` → Python, plug into existing engine.

Tasks:
1. Create `strategies/full_data/momentum_reversal.py` with `MomentumReversal(BaseStrategy)` class
2. Map all .el conditions to Python boolean evaluations
3. Add strategy config entry in `strategies.yaml`
4. Write pytest tests simulating historical price scenarios
5. Enable (`enabled: true`) in a non-trading config profile and verify signal generation matches .el backtest expectations
6. Compare trade outcomes vs the original .el backtest logs (the existing TradeLog.csv files serve as ground truth)

**Deliverable:** Fully functional momentum reversal strategy producing Signals identical to the .el file's behavior.

### Phase 3: Strategy 2 — Trend Breakout Conversion
**Scope:** Same as Phase 2 but for the more complex SL/TP/trail exit logic.

Tasks:
1. Create `strategies/full_data/trend_breakout.py`
2. Implement three-part exit: hard stop, limit TP, SuperTrend trail
3. The trail exit is the trickiest — may need a post-signal monitor or tracker component similar to what existing layer1 strategies use
4. Tests + verification against `.el` backtest logs

**Deliverable:** Trend breakout strategy with matching SL/TP/trail behavior.

### Phase 4: Strategy 3 — Volatility Squeeze Conversion
**Scope:** Same as previous phases but starting from design doc only (no .el).

Tasks:
1. Create `strategies/full_data/volatility_squeeze.py`
2. Translate ScanStrat3.md specs directly (no .el to match against — ground truth is the spec itself)
3. BB/KC squeeze detection: compare BB width to KC width each tick
4. Volume confirmation on breakout
5. Tests + paper trading verification

**Deliverable:** Volatility squeeze strategy functioning per spec.

### Phase 5: Cross-Strategy Analysis & Tuning
**Scope:** Observational — not code, but analysis work.

Tasks:
1. Run all three concurrently (with small position sizes) alongside existing syngex strategies
2. Analyze overlap/conflict: do these TA strategies fire when options-flow strategies already signal? Or complementary?
3. Potential enhancement: use TA indicators as **filters on top of existing strategies**. E.g., "only show gamma_wall_bounce signals when RSI confirms mean-reversal zone." This would combine the strengths of both systems rather than running them side-by-side.
4. Document findings in `analysis/` folder

---

## Mapping Guide: Indicator Names

For easy reference between .el syntax and Python/indicator calculator:

| .el Name | Python Key | Description |
|---|---|---|
| `RSI(RSILength)` | `rsi` | Relative Strength Index |
| `SlowK(StoXLength)` | `stoch_k` | Stochastic %K |
| `Average(StoXK, StoXSMA)` | `stoch_d` | Stochastic %D (smoothed K) |
| `BBMID` / `BBUpper` / `BBLower` | `bb_mid`, `bb_upper`, `bb_lower` | Bollinger Band levels |
| `BBPercentB` | `bb_pctb` | Bollinger %B (0=lower, 1=upper) |
| `MACD(MACDFast, MACDSlow, MACDSignal)` | `macd_line`, `macd_signal`, `macd_histogram` | MACD values |
| `ADX(ADXLength)` | `adx` | Average Directional Index |
| `DMI(1)[1]` / `[2]` | `di_plus`, `di_minus` | Directional Indicators |
| `AverageTrueRange(ATRLength)` | `atr` | Average True Range |
| Custom `SuperTrend` | `super_trend_value`, `super_trend_dir` | SuperTrend level and direction |
| Custom `Donchian(Highest/Lowest)` | `donchian_upper`, `donchian_lower` | Donchian Channel |
| Custom `Keltner` | `keltner_upper`, `keltner_lower` | Keltner Channel |

---

## Risks & Open Questions

1. **Bar construction timing**: Should indicators calculate on every tick (intra-bar) or only on bar close? The .el files run on bar close. For real-time signal generation, intra-bar makes sense but changes signal timing. Recommend: flag each signal with `realized: bool` and prefer realized signals for execution.

2. **TradeStation .el exit logic nuance**: The .el exit conditions check `(not RSI_Green or not BB_Green or not ADX_Green)` — meaning any single condition failure exits the position. Translating this to continuous evaluation requires careful handling to avoid premature exits during minor indicator flicker. Suggestion: add a "condition stable for N ticks" gate before triggering exit.

3. **Position sizing**: Syngex's current system handles option contracts. These strategies trade equities directly. Need to reconcile execution paths — likely a separate trade queue or broker routing, unless the intent is purely signal/alert generation without execution.

4. **Net Gamma filter relevance**: The existing engine runs a net gamma regime filter that sets POSITIVE/NEGATIVE context. Should the three agents strategies also respect this? Options: make it mandatory (both signals must align), optional (configurable), or independent (these strategies know nothing about gamma). Recommendation: configurable, default to independent since TA strategies operate on different logic domains.

5. **Indicator data freshness**: Option chain strategies may have different data pipelines than the price stream feeding the indicator calculator. Need to confirm the TS client's price updates arrive at sufficient frequency and reliability for sub-minute indicator computation.

6. **Backtest parity**: How do we verify the Python implementation produces the same signals as the .el files? The .el files were tested against TradeStation's internal bar data. Without replaying the exact same historical bars, we won't get perfect parity. Recommendation: accept approximate parity and focus on directional correctness rather than exact signal-for-signal match.

---

## Why This Is Worth Doing

- **Three proven strategies** backed by 3+ years of backtesting vs zero-equity-TA coverage in syngex today
- **Shared infrastructure gain**: The indicator framework benefits not just these three strategies but any future TA-based strategy the team builds
- **Complementary edge**: Options-flow (syngex) and price action (agents) measure completely different aspects of the market. Combined, they could filter false signals from either system alone
- **Config-driven tuning**: Once the framework exists, flipping between strategies is just a YAML edit and restart
