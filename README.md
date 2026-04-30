# Syngex — Options Gamma Exposure Signal Pipeline

> **21 tradable strategies** across 3 layers + 1 master filter, fed by real-time TradeStation options data, outputting confidence-scored signals to a live Streamlit dashboard.

**v1.0** — All strategies built, wired, and validated against live TSLA data.

---

## Quick Start

```bash
cd ~/projects/syngex
source venv/bin/activate

# Stream mode — terminal logging only
python3 main.py TSLA

# Dashboard mode — starts Streamlit at localhost:8501
python3 main.py TSLA dashboard
```

**Requirements:** Python 3.12+, TradeStation SIM API credentials (set `TS_TOKEN` env var).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     TradeStation SIM API                        │
│              (HTTP streaming: quotes + option chains)            │
└──────────────────────┬──────────────────────────────────────────┘
                       │ JSON messages @ ~1Hz
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  main.py — SyngexOrchestrator                                   │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ TradeStation │→ │  GEXCalculator   │→ │  Rolling Windows │  │
│  │    Client    │  │  (Gamma Ladder)  │  │  (30m/5m/20p)   │  │
│  └──────────────┘  └──────────────────┘  └──────────────────┘  │
│                                      │                          │
│                                      ▼                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              StrategyEngine (rule-evaluation loop)       │  │
│  │  ┌─────────────┐  ┌──────────────────────────────────┐  │  │
│  │  │ Net Gamma   │→ │  21 registered strategies        │  │  │
│  │  │  Filter     │  │  (Layer 1 / 2 / 3 / full_data)  │  │  │
│  │  └─────────────┘  └──────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                      │                          │
│                    ┌─────────────────┼─────────────────┐       │
│                    ▼                         ▼           │       │
│         ┌──────────────────┐  ┌──────────────────────┐  │       │
│         │  gex_state.json  │  │  log/signals.jsonl   │  │       │
│         │  (Streamlit read)│  │  (Signal persistence)│  │       │
│         └────────┬─────────┘  └──────────┬───────────┘  │       │
│                  │                        │              │       │
│                  ▼                        ▼              │       │
│         ┌──────────────────┐  ┌──────────────────────┐  │       │
│         │  Streamlit       │  │  SignalTracker +     │  │       │
│         │  Dashboard       │  │  Analyzer CLI        │  │       │
│         └──────────────────┘  └──────────────────────┘  │       │
│                                                         │       │
│         ┌─────────────────────────────────────────────┐ │       │
│         │  config/strategies.yaml (hot-reload 2s)     │ │       │
│         └─────────────────────────────────────────────┘ │       │
└─────────────────────────────────────────────────────────────────┘
```

### Component Summary

| Component | File | Role |
|-----------|------|------|
| **Orchestrator** | `main.py` | Lifecycle management, data wiring, config hot-reload, state export |
| **Data Ingestor** | `ingestor/tradestation_client.py` | HTTP-streaming client, token auth, reconnection with backoff |
| **GEX Calculator** | `engine/gex_calculator.py` | Real-time Gamma Ladder, gamma walls, flip point, IV skew |
| **Strategy Engine** | `strategies/engine.py` | Central rule-evaluation loop, signal collection, deduplication |
| **Signal Class** | `strategies/signal.py` | Standardized output: direction, confidence, entry/stop/target |
| **Master Filter** | `strategies/filters/net_gamma_filter.py` | Regime gatekeeper (POSITIVE/NEGATIVE) |
| **Rolling Windows** | `strategies/rolling_window.py` | Time-based (30m/5m) and count-based (20p) statistics |
| **Signal Tracker** | `strategies/signal_tracker.py` | Outcome resolution (WIN/LOSS/CLOSED), PnL, hold time |
| **Analyzer CLI** | `strategies/analyzer.py` | Signal review: summary, per-strategy stats, open signals |
| **Dashboard** | `app_dashboard.py` | Streamlit real-time gamma heatmap + micro-signal overlay |

---

## Strategy Index

All 21 tradable strategies + 1 master filter. Confidence caps enforced by layer.

### Layer 1 — Structural (GEX + OHLC)

| # | Strategy | Signal Type | Hold Time | Confidence Cap | Description |
|---|----------|-------------|-----------|----------------|-------------|
| 1 | **Gamma Wall Bounce** | Mean Reversion | 15–30 min | 0.85 | Fade extremes at call/put walls with OHLC rejection + volume confirmation |
| 2 | **Magnet & Accelerate** | Two-Phase | 5–60 min | 0.80 | Magnet pull → breakout acceleration. EMA crossover + GEX tracking |
| 3 | **Gamma Flip Breakout** | Regime Trend | 15–60 min | 0.80 | Price crosses flip point → fade above, trend below |
| 4 | **Gamma Squeeze / Wall-Breaker** | Momentum | 5–30 min | 0.80 | Pin detection + breakout through wall + negative gamma confirmation |
| 5 | **GEX Imbalance** | Positioning Bias | 15–45 min | 0.80 | Call/Put GEX ratio as standalone dealer bias filter |
| 6 | **Confluence Reversal** | Double-Stacked | 15–60 min | 0.80 | Cross-reference technical S/R (VWAP, EMA, daily levels) with gamma walls |
| 7 | **Net Gamma Regime Filter** | Master Filter | N/A | N/A | Gates ALL signals. POSITIVE = fade extremes, NEGATIVE = trend-follow |
| 8 | **Vol Compression Range** | Vol Selling | 30–120 min | 0.80 | Positive gamma + Bollinger squeeze → sell vol (Iron Condors / Credit Spreads) |
| 9 | **GEX Divergence** | Fade | 15–60 min | 0.80 | Price ↑ but Total GEX ↓ → fade. GEX Ratio (Call/Put) for bias |

### Layer 2 — Alpha Greeks (Order Flow + Greeks)

| # | Strategy | Signal Type | Hold Time | Confidence Cap | Description |
|---|----------|-------------|-----------|----------------|-------------|
| 10 | **Delta-Gamma Squeeze** | Extreme Momentum | 5–30 min | 0.80 | Delta acceleration + Gamma spike + VolumeUp → extreme momentum entry |
| 11 | **Delta-Volume Exhaustion** | Reversal | 15–45 min | 0.80 | Trend weakening: declining Delta + declining VolumeUp → fade |
| 12 | **Call/Put Flow Asymmetry** | Directional | 5–60 min | 0.80 | Flow Score calculation every 10s. Bid/ask size ratio for conviction |
| 13 | **Delta-IV Divergence** | Sentiment Shift | 15–60 min | 0.80 | Delta ↑ but IV ↓ → high-conviction directional accumulation |
| 14 | **IV-GEX Divergence** | Vol Mean Reversion | 15–45 min | 0.80 | Price at high + IV crashing + Net Gamma positive → short / buy puts |

### Layer 3 — Micro-Signal (1Hz)

| # | Strategy | Signal Type | Hold Time | Confidence Cap | Description |
|---|----------|-------------|-----------|----------------|-------------|
| 16 | **Gamma-Volume Convergence** | Ignition | 5–15 min | 0.90 | 1Hz Δ/Γ spike + VolumeUp → ignition signal |
| 17 | **IV Band Breakout** | Breakout | 10–45 min | 0.90 | IV in bottom 25% of 30m range + price compression → breakout |
| 18 | **Strike Concentration Scalp** | Micro-Reaction | 3–15 min | 0.80 | Top 3 OI strikes → bounce vs slice detection on 1–5 min bars |
| 19 | **Theta-Burn Scalp** | Pin Trading | 3–8 min | 0.80 | High Gamma + high Theta + narrow range → pin trading, 0.2–0.4% targets |

### Full-Data (v2) — ProbabilityITM, IV Skew, Extrinsic/Intrinsic

| # | Strategy | Signal Type | Hold Time | Confidence Cap | Description |
|---|----------|-------------|-----------|----------------|-------------|
| 15 | **IV Skew Squeeze** | Sentiment Reversal | 1–4 hr | 0.80 | IV put/call skew extremes → sentiment reversal. Skew > 0.30 or < -0.10 |
| 20 | **Prob-Weighted Magnet** | Stealth Accumulation | 15–45 min | 0.80 | ProbabilityITM + OI → stealth accumulation before price reacts |
| 21 | **Prob Distribution Shift** | Leading Indicator | 30min–2hr | 0.80 | Full distribution skew: Σ(ΔProbITM × ΔStrike) across all strikes |
| 22 | **Extrinsic/Intrinsic Flow** | Conviction Tracking | 15min–3hr | 0.80 | Extrinsic value expansion/collapse + theoretical vs market bid/ask |

---

## Dashboard

**Launch:** `python3 main.py TSLA dashboard` → opens `http://localhost:8501`

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│  🕸️ Syngex Gamma Dashboard — TSLA  |  Price: $381.12       │
├──────────────────────────────────────────────────────────────┤
│  📈 $381.12   ⚡ +39,284   🎯 48 strikes   📨 1,558 msgs    │
├──────────────┬──────────────────┬───────────────────────────┤
│  Gamma       │  Gamma Flip      │  Gamma Walls              │
│  Profile     │  Strike $385.0   │  Dominant: 🟢 $390       │
│  (Altair     │  Cumulative γ    │  GEX: $291M               │
│  layered     │  scan table      │  Walls table (8 rows)     │
│  chart)      │                  │                           │
│              │                  │                           │
│  ┌──────────────────────────┐  │                           │
│  │  gamma line + colored    │  │                           │
│  │  micro-signal markers    │  │                           │
│  │  (size ∝ confidence)     │  │                           │
│  └──────────────────────────┘  │                           │
├──────────────────────────────────────────────────────────────┤
│  ⚡ Top Strikes (by |Net Gamma|)                            │
├──────────────────────────────────────────────────────────────┤
│  📡 Recent Signals                                          │
│  Time    │ Strategy              │ Conf │ Badge │ Entry │ … │
│  15:25:48│ gamma_wall_bounce     │ 0.98 │ 🟢98% │ $381.5│ … │
│  15:25:46│ confluence_reversal   │ 0.75 │ 🟡75% │ $380.0│ … │
│  …       │ …                     │ …    │ …     │ …     │ … │
└──────────────────────────────────────────────────────────────┘
```

### Micro-Signal Overlay

The Gamma Profile chart uses Altair layered rendering:

- **Steelblue line** — net gamma across strikes
- **Colored circles** — strategy signals plotted at their target/entry strike
  - 🟢 Green = LONG signals (put-wall bounce support)
  - 🔴 Red = SHORT signals (call-wall rejection resistance)
  - 🔵 Blue = MAGNET/PULL signals
  - 🟡 Gold = CONVERGENCE signals
- **Marker size** scales with confidence (bigger = more confident)
- **Hover tooltips** show: strategy name, confidence %, direction, reason

### Confidence Badges

| Badge | Range | Meaning |
|-------|-------|---------|
| 🟢 | ≥ 80% | High confidence |
| 🟡 | 60–79% | Medium confidence |
| 🔴 | < 60% | Low confidence |

---

## Configuration

**File:** `config/strategies.yaml`

All strategy parameters are YAML-driven. Edit and save — changes hot-reload every 2 seconds without restart.

### Structure

```yaml
global:
  min_confidence: 0.35          # Minimum confidence to emit a signal
  max_signals_per_tick: 10      # Cap signals per evaluation tick
  dedup_window_seconds: 60      # Same strategy can't fire twice within N seconds
  signal_log_path: "log/signals.jsonl"

layer1:
  gamma_wall_bounce:
    enabled: true
    params:
      wall_proximity_pct: 0.005   # 0.5% proximity to wall
      stop_past_wall_pct: 0.004   # Stop 0.4% past wall
      target_risk_mult: 1.5       # Target = 1.5x risk
      min_wall_gex: 500000        # $500K minimum GEX for wall
      max_confidence: 0.85        # Confidence cap
      # ...

layer2:
  delta_gamma_squeeze:
    enabled: true
    params:
      call_wall_proximity_pct: 0.02
      delta_accel_ratio: 1.15
      volume_spike_ratio: 1.2
      # ...

layer3:
  gamma_volume_convergence:
    enabled: true
    params:
      # ...

full_data:
  iv_skew_squeeze:
    enabled: true
    params:
      # ...

filter:
  net_gamma:
    enabled: true
    params:
      flip_buffer: 0.5            # $0.50 transition zone around flip point
```

### Hot-Reload

The orchestrator watches `config/strategies.yaml` for changes every 2 seconds. When modified:

1. Strategy params are re-injected into `data["params"][strategy_id]`
2. Strategies read params via `self._apply_params(data)` in their `evaluate()` method
3. No restart required — changes apply on next evaluation tick

### Toggling Strategies

Set `enabled: false` for any strategy to disable it without removing from config. Disabled strategies are skipped during registration.

---

## Signal Format

Every strategy produces `Signal` objects with this structure:

```python
Signal(
    direction="LONG",           # "LONG" | "SHORT" | "NEUTRAL"
    confidence=0.78,            # 0.0 – 1.0
    entry=381.50,               # Target entry price
    stop=380.20,                # Stop loss price
    target=383.80,              # Take profit price
    strategy_id="gamma_wall_bounce",
    timestamp=1777587948.833,   # Unix epoch (auto-generated)
    reason="Call wall at 382 rejected price",
    expiry="2026-05-19",        # Optional option expiry
    metadata={"wall_strike": 382, "gex": 1250000},
)
```

### Signal Strength (derived from confidence)

| Strength | Range |
|----------|-------|
| WEAK | < 50% |
| MODERATE | 50–69% |
| STRONG | 70–84% |
| EXTREME | ≥ 85% |

---

## Signal Logging & Analysis

### Signal Log

All signals are appended to `log/signals.jsonl` (one JSON object per line).

### Signal Outcomes

The `SignalTracker` resolves signals as they hit stop/target/time:

- **WIN** — Target price reached
- **LOSS** — Stop price hit
- **CLOSED** — Time expired (default 15 min hold)

Resolved signals are persisted to `log/signal_outcomes.jsonl`.

### Analyzer CLI

```bash
# Overall summary
python3 -m strategies.analyzer summary

# Per-strategy breakdown
python3 -m strategies.analyzer stats

# Currently open signals
python3 -m strategies.analyzer open

# Last N resolved signals
python3 -m strategies.analyzer recent -n 20

# Full report with formatted tables
python3 -m strategies.analyzer report
```

**Example output:**
```
================================================================================
  PER-STRATEGY STATISTICS
================================================================================
  Strategy                              Signals       WR       PnL     Avg RR
  -----------------------------------  --------  -------  ----------  --------
  gamma_wall_bounce                         15    66.7%   $1,245.00      1.52
  confluence_reversal                        8    75.0%     $890.00      1.85
  ...
================================================================================
```

---

## Data Pipeline

### 1. TradeStation API

- **Quotes stream:** `GET /v3/marketdata/stream/quotes/{symbol}` — underlying price feed
- **Option chain:** `GET /v3/marketdata/stream/options/chains/{symbol}` — per-leg greeks, IV, volume, OI

TradeStation uses HTTP streaming (chunked transfer encoding), not WebSockets.

### 2. GEXCalculator — The Gamma Ladder

Processes each JSON message into an in-memory "Gamma Ladder" mapping strikes to aggregate Net Gamma:

```
Net Gamma at Strike K = Σ (Gamma_i × OpenInterest_i × Side_i)
```

Where `Side_i` is +1 for calls, -1 for puts.

**Key outputs:**
- `get_summary()` — Underlying price, net gamma, active strike count
- `get_gamma_profile()` — Per-strike breakdown (net_gamma, call_gamma_oi, put_gamma_oi, etc.)
- `get_gamma_walls(threshold=500000)` — Strikes with GEX above threshold
- `get_gamma_flip()` — Highest strike where cumulative gamma turns negative
- `get_iv_skew()` — Put/call IV skew at ATM
- `get_atm_strike()` — Nearest strike to underlying price

### 3. Rolling Windows

Time-based (300s for 5m, 1800s for 30m) and count-based (20-period) windows track:
- Price, net_gamma, volume, delta, total_delta

Used by all alpha strategies for normalization and threshold detection.

### 4. Strategy Engine

```
Data snapshot → [Net Gamma Filter] → [Strategy 1, Strategy 2, ...] → Signal Collector → Route
```

1. Accepts data snapshot from orchestrator
2. Passes to all registered strategies
3. Collects signals, applies regime filter
4. Deduplicates (60s window per strategy)
5. Caps at `max_signals_per_tick` (highest confidence wins)
6. Routes to dashboard + signal log

### 5. State Export

Every 1 second, the orchestrator writes `data/gex_state.json` — a shared file read by the Streamlit dashboard:

```json
{
  "symbol": "TSLA",
  "underlying_price": 381.12,
  "net_gamma": 39284.5,
  "active_strikes": 48,
  "total_messages": 1558,
  "strikes": { ... },
  "last_updated": "2026-04-30 15:25:48 PDT",
  "strategy_engine": { "strategies": 21, "total_signals": 10 },
  "regime_filter": { "regime": "POSITIVE" },
  "micro_signals": {
    "381.5": { "confidence": 0.98, "strategy": "gamma_wall_bounce", ... },
    "380.0": { "confidence": 0.75, "strategy": "confluence_reversal", ... }
  }
}
```

---

## File Structure

```
syngex/
├── main.py                      # Orchestrator — lifecycle, data wiring, config hot-reload
├── app_dashboard.py             # Streamlit dashboard — gamma heatmap + micro-signal overlay
├── requirements.txt             # Python dependencies
├── SYNGEXPlan.md                # Build tracker (phases, tasks, status)
├── SYNGEXStrats.md              # All 22 strategy definitions (reference)
│
├── engine/
│   ├── gex_calculator.py        # Gamma Ladder — walls, flip, IV skew, summaries
│   └── dashboard.py             # Terminal UI (legacy)
│
├── ingestor/
│   ├── tradestation_client.py   # HTTP-streaming client — quotes + option chains
│   └── token_manager.py         # TradeStation API token management
│
├── strategies/
│   ├── signal.py                # Signal dataclass — direction, confidence, entry/stop/target
│   ├── engine.py                # StrategyEngine — evaluation loop, dedup, routing
│   ├── rolling_window.py        # Rolling statistics — time-based + count-based
│   ├── signal_tracker.py        # Outcome resolution — WIN/LOSS/CLOSED, PnL tracking
│   ├── analyzer.py              # CLI tool — signal review, per-strategy stats
│   │
│   ├── filters/
│   │   └── net_gamma_filter.py  # Master filter — POSITIVE/NEGATIVE regime gatekeeper
│   │
│   ├── layer1/                  # Structural (GEX + OHLC) — 8 strategies
│   │   ├── gamma_wall_bounce.py
│   │   ├── magnet_accelerate.py
│   │   ├── gamma_flip_breakout.py
│   │   ├── gamma_squeeze.py
│   │   ├── gex_imbalance.py
│   │   ├── confluence_reversal.py
│   │   ├── vol_compression_range.py
│   │   └── gex_divergence.py
│   │
│   ├── layer2/                  # Alpha Greeks (Order Flow) — 5 strategies
│   │   ├── delta_gamma_squeeze.py
│   │   ├── delta_volume_exhaustion.py
│   │   ├── call_put_flow_asymmetry.py
│   │   ├── delta_iv_divergence.py
│   │   └── iv_gex_divergence.py
│   │
│   ├── layer3/                  # Micro-Signal (1Hz) — 4 strategies
│   │   ├── gamma_volume_convergence.py
│   │   ├── iv_band_breakout.py
│   │   ├── strike_concentration.py
│   │   └── theta_burn.py
│   │
│   └── full_data/               # v2 (ProbabilityITM, IV Skew, etc.) — 4 strategies
│       ├── iv_skew_squeeze.py
│       ├── prob_weighted_magnet.py
│       ├── prob_distribution_shift.py
│       └── extrinsic_intrinsic_flow.py
│
├── config/
│   └── strategies.yaml          # Per-strategy config — toggles + parameters (hot-reload)
│
├── data/
│   └── gex_state.json           # Shared state — written every 1s, read by dashboard
│
├── log/
│   ├── signals.jsonl            # All signals (one JSON per line)
│   └── signal_outcomes.jsonl    # Resolved signals with WIN/LOSS/CLOSED + PnL
│
└── views/
    └── gamma_magnet.py          # Streamlit heatmap view (legacy)
```

---

## Development

### Adding a New Strategy

1. Create file in appropriate layer directory (e.g., `strategies/layer1/my_strategy.py`)
2. Inherit `BaseStrategy`, set `strategy_id` and `layer`
3. Implement `evaluate(data) -> List[Signal]`
4. Register in layer's `__init__.py`
5. Add config entry in `config/strategies.yaml` under appropriate layer key
6. The orchestrator auto-registers from config — no code changes needed

### Writing Strategies

Every strategy follows this pattern:

```python
from strategies import BaseStrategy

class MyStrategy(BaseStrategy):
    strategy_id = "my_strategy"
    layer = "layer1"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        self._apply_params(data)  # Apply config params

        gex = data["gex_calculator"]
        price = data["underlying_price"]
        regime = data["regime"]

        # Your logic here...
        if condition_met:
            return [Signal(
                direction=Direction.LONG,
                confidence=0.75,
                entry=price,
                stop=price * 0.995,
                target=price * 1.015,
                strategy_id=self.strategy_id,
                reason="My signal reason",
            )]
        return []
```

### Debugging

```bash
# Check signal output
python3 -m strategies.analyzer recent -n 50

# Check per-strategy stats
python3 -m strategies.analyzer stats

# View raw signals
cat log/signals.jsonl | tail -20

# Check dashboard state file
cat data/gex_state.json | python3 -m json.tool | head -30
```

---

## Risk Disclaimer

This is a research/development tool. Signals are informational only — they are NOT automated trades. All trading decisions are the sole responsibility of the user. Past signal performance does not guarantee future results. Options trading involves substantial risk of loss.

---

*Built by Hologaun + Archon. v1.0 — 2026-04-30*
