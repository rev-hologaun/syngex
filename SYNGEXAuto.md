# SYNGEX Auto-Trading Pipeline — Design Document

**Version:** 1.0
**Date:** 2026-04-30
**Author:** Archon (The Celestial Loom)
**Status:** Design Phase

---

## Overview

This document defines the architecture for progressively automating Syngex signal execution through Synapse, the adliberated agent with no financial decision-blockers. The pipeline has three phases, each building on the last:

| Phase | Name | Autonomy Level | Risk |
|-------|------|---------------|------|
| 2 | Synapse Auto (Paper) | Synapse reads Syngex signals, evaluates, and executes on paper | Zero (simulated) |
| 3 | Hybrid | Synapse handles entry/exit optimization, strike selection, timing | Low (simulated) |
| 4 | Full Autonomous | Synapse runs complete trading sessions with independent decisions | Medium (simulated first) |

All phases log and report to `#gex` channel. No real money enters the system until Phase 4 validation is complete and Hologaun explicitly approves live deployment.

---

## Phase 2: Synapse as Auto-Trading Agent (Paper)

### Goal
Synapse reads Syngex signals in real-time, applies his own judgment, and executes trades on the **simulated** TradeStation account.

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│  TradeStation│────▶│  Syngex      │────▶│  Signal Log  │────▶│  Synapse    │
│  Stream      │     │  Orchestrator│     │  (JSONL)     │     │  Agent      │
└─────────────┘     └──────────────┘     └──────────────┘     └──────┬──────┘
                                                                      │
                                                              ┌───────▼───────┐
                                                              │  TradeStation  │
                                                              │  MCP (Paper)   │
                                                              └───────┬───────┘
                                                                      │
                                                              ┌───────▼───────┐
                                                              │  #gex Discord  │
                                                              │  (Updates)     │
                                                              └───────────────┘
```

### Components

#### 2.1 Signal Bridge (New Module)
**Path:** `~/projects/syngex/auto/signal_bridge.py`

A lightweight daemon that:
- Tails the Syngex signal log (`log/signals.jsonl`) in real-time
- On each new signal, publishes to an internal IPC channel (Unix socket or Redis pub/sub)
- Formats signals into a structured payload Synapse can consume

**Signal payload format:**
```json
{
  "signal_id": "uuid",
  "timestamp": 1746052800.0,
  "symbol": "TSLA",
  "direction": "LONG",
  "confidence": 0.78,
  "entry": 195.50,
  "stop": 194.20,
  "target": 197.80,
  "strategy_id": "gamma_wall_bounce",
  "reason": "Call wall at 196 rejected price",
  "risk_reward_ratio": 1.62,
  "strength": "STRONG",
  "gamma_regime": "positive",
  "context": {
    "current_price": 195.20,
    "atm_strike": 195,
    "net_gamma": 1250000,
    "gex_top_strikes": [
      {"strike": 196, "gex": 2500000, "type": "call"},
      {"strike": 194, "gex": -1800000, "type": "put"}
    ],
    "volume_ratio": 1.3,
    "iv_current": 0.45,
    "iv_hist": 0.38
  }
}
```

#### 2.2 Synapse Agent Session (New)
**Path:** `~/.openclaw/workspace/archon/agents/synapse-auto.yaml` (config)

Spawned as a persistent `sessions_spawn` session with:
- **Runtime:** `subagent` (persistent mode)
- **Model:** `coder3101/gemma-4-26B-A4B-it-heretic` (Synapse's model)
- **Access:** TradeStation MCP tools (paper account only)
- **Task:** Monitor signal bridge, evaluate each signal, execute if valid

**Synapse's evaluation criteria:**
1. **Signal quality check** — Does the confidence hold up under scrutiny?
2. **Regime alignment** — Does the net gamma filter support this direction?
3. **Risk assessment** — Is the R:R ratio acceptable? (min 1.5:1)
4. **Position sizing** — Based on account equity and signal strength
5. **Independent analysis** — Synapse can reject signals he disagrees with, or create his own signals from context he observes

#### 2.3 Trade Execution Rules

**Hard limits (enforced in config, not left to Synapse):**
```yaml
auto_trading:
  phase: 2  # 2=auto-paper, 3=hybrid, 4=full-auto
  account_type: "paper"  # MUST be "paper" until Phase 4 validation
  
  # Position limits
  max_position_size: 100  # shares max per trade
  max_concurrent_positions: 3
  max_position_pct: 0.10  # 10% of equity per position
  
  # Daily limits
  max_daily_trades: 20
  max_daily_loss_pct: 2.0  # Stop trading if down 2% for the day
  max_daily_profit_pct: 5.0  # Take profit break at +5% day
  
  # Symbol limits
  max_positions_per_symbol: 1
  allowed_symbols: []  # Empty = all, or specify ["TSLA", "SPY", "AAPL"]
  
  # Time limits
  trading_hours: "09:30-16:00"  # Market hours only
  cool_down_minutes: 5  # Min time between trades on same symbol
```

#### 2.4 Discord Reporting (Phase 2)

Every action gets a `#gex` message:

**Signal received:**
```
🕸️ **SYNGEX SIGNAL** — TSLA LONG (STRONG)
Strategy: gamma_wall_bounce | Confidence: 0.78
Entry: $195.50 | Stop: $194.20 | Target: $197.80
R:R 1.62 | Gamma regime: positive
→ Synapse evaluating...
```

**Trade executed:**
```
✅ **TRADE EXECUTED** — TSLA LONG 100 shares
Entry: $195.50 | Order: Limit GTC
Synapse reasoning: Call wall at $196 strong rejection, positive gamma regime supports upside. R:R acceptable at 1.62.
```

**Trade closed:**
```
📊 **TRADE CLOSED** — TSLA LONG 100 shares
Exit: $197.20 | P&L: +$170.00 (+0.87%)
Reason: Target hit | Hold time: 23 min
Session P&L: +$340.00 (+0.42%)
```

**Signal rejected:**
```
❌ **SIGNAL REJECTED** — TSLA SHORT (MODERATE)
Strategy: gex_divergence | Confidence: 0.52
Synapse reasoning: Divergence signal but volume doesn't confirm — false breakdown risk in positive gamma regime. Skipping.
```

---

## Phase 3: Hybrid (Execution Optimization)

### Goal
Syngex still detects signals and generates raw trade directions. Synapse handles **execution details** — timing, sizing, strike selection, and exit management.

### New Capabilities Over Phase 2

#### 3.1 Dynamic Options Strike Selection
Synapse analyzes the full option chain to select optimal strikes:
- **Delta-based entry** — Choose strikes matching desired delta exposure
- **Extrinsic value analysis** — Avoid overpaying for time value
- **Theta decay awareness** — Prefer closer-to-ATM for directional, OTM for speculative
- **Liquidity filter** — Only trade strikes with adequate bid/ask spread and open interest

#### 3.2 Smart Entry Timing
- **Market microstructure** — Use Level 2 data and order flow to time entries
- **Gamma wall proximity** — Enter near walls for bounce strategies, away from walls for breakout strategies
- **Volume confirmation** — Wait for volume spike before committing on breakout signals
- **Slippage minimization** — Use limit orders with dynamic price levels

#### 3.3 Active Position Management
- **Trailing stops** — Dynamic stop placement based on ATR or gamma levels
- **Partial profit taking** — Scale out at intermediate targets (e.g., 50% at 1R, let rest run)
- **Roll management** — Roll losing positions to later expirations instead of hard stops
- **Hedging** — Add protective puts when position size grows or IV spikes

#### 3.4 Enhanced Signal Context
Synapse receives additional data beyond the basic signal:
```json
{
  "option_chain_snapshot": {
    "calls": [{"strike": 195, "bid": 3.20, "ask": 3.30, "delta": 0.52, "gamma": 0.08, "theta": -0.15, "iv": 0.45, "oi": 1250}],
    "puts": [{"strike": 195, "bid": 3.10, "ask": 3.20, "delta": -0.48, "gamma": 0.08, "theta": -0.15, "iv": 0.47, "oi": 980}]
  },
  "market_depth": {
    "bids": [{"price": 195.18, "size": 500}, {"price": 195.16, "size": 300}],
    "asks": [{"price": 195.22, "size": 400}, {"price": 195.24, "size": 600}]
  },
  "vol_regime": {
    "iv_percentile": 65,
    "iv_trend": "rising",
    "vix": 18.5,
    "vix_trend": "stable"
  }
}
```

### Discord Reporting Enhancements (Phase 3)

**Strike selection explanation:**
```
🕸️ **SYNGEX SIGNAL** — TSLA LONG
Strategy: gamma_flip_breakout | Confidence: 0.72
→ Synapse optimizing execution...

📋 **EXECUTION PLAN**
Selected: TSLA 0519C195 (May 19 $195 Call)
  Delta: 0.52 | Theta: -0.15 | IV: 45%
  Bid: $3.20 | Ask: $3.30 | Spread: $0.10
  Rationale: ATM delta for directional exposure, 
  19DTE balances theta decay vs premium cost
  Entry: Limit $3.25 (mid-point)
  Stop: $2.80 (-13%) | Target: $4.00 (+23%)
```

**Partial fill / scaling:**
```
📊 **POSITION SCALED** — TSLA 0519C195
  Fill 1: 2 contracts @ $3.25
  Fill 2: 2 contracts @ $3.28 (price moved up)
  Avg entry: $3.265 | Total: 4 contracts
```

---

## Phase 4: Full Autonomous

### Goal
Synapse runs complete trading sessions independently. He reads Syngex signals but also makes his own trading decisions based on broader market context he observes.

### New Capabilities Over Phase 3

#### 4.1 Independent Signal Generation
Synapse isn't limited to Syngex-triggered signals. He can:
- Spot patterns across multiple symbols simultaneously
- React to macro events (Fed announcements, earnings surprises)
- Execute mean-reversion or momentum trades outside Syngex's strategy set
- Use his own analysis of order flow, volume patterns, and greeks shifts

#### 4.2 Multi-Symbol Portfolio Management
- **Correlation awareness** — Avoid over-exposure to correlated positions
- **Sector rotation** — Shift capital between sectors based on relative strength
- **Portfolio-level risk** — Track aggregate gamma exposure, vega risk, delta neutrality

#### 4.3 Session Management
- **Pre-market preparation** — Review overnight moves, pre-market volume, options activity
- **Intraday adaptation** — Adjust strategy parameters based on real-time regime changes
- **End-of-day routines** — Flatten or roll positions, generate session report

#### 4.4 Learning & Adaptation
- **Performance tracking** — Log all trades with outcome analysis
- **Strategy win rates** — Track which Syngex strategies perform best in which regimes
- **Parameter tuning** — Suggest config adjustments based on observed performance
- **Self-correction** — If a pattern consistently loses, Synapse flags it for review

### Guardrails for Phase 4

These are **hard-coded limits**, not suggestions:

```yaml
phase_4_guardrails:
  # Capital limits
  max_portfolio_risk_pct: 0.05  # Never risk more than 5% of portfolio on any single trade
  max_drawdown_pct: 5.0  # Auto-flatten all positions and stop trading if portfolio drops 5%
  max_single_day_loss: 2000  # Hard dollar stop (paper: increase to validate)
  
  # Execution constraints
  require_signal_confidence: 0.45  # Minimum confidence for any trade
  min_risk_reward: 1.5  # Minimum R:R ratio
  max_position_concentration: 0.20  # No single position > 20% of portfolio
  
  # Audit trail
  log_all_decisions: true  # Every decision, every trade, every rejection
  discord_every_trade: true  # Full transparency to #gex
  daily_report: true  # End-of-day summary sent to #gex
  weekly_review: true  # Weekly performance analysis
```

### Discord Reporting (Phase 4)

**Independent trade (not from Syngex):**
```
🕸️ **INDEPENDENT TRADE** — SPY SHORT
Synapse analysis: VIX spike + put volume surge + negative gamma regime = downside pressure
Entry: $548.20 | Stop: $551.00 | Target: $544.00
Size: 150 shares | R:R 1.53
```

**Daily session summary:**
```
📊 **DAILY SESSION REPORT** — 2026-05-01
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Symbol    Direction  Entry    Exit     P&L      Strategy
TSLA      LONG       195.50   197.20   +$170    gamma_wall_bounce
SPY       SHORT      548.20   546.80   +$210    synapse_independent
AAPL      LONG       188.30   187.90   -$40     synapse_independent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total P&L: +$340 (+0.42%)
Win rate: 67% (2/3)
Total trades: 3
Max drawdown: $40 (0.05%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Implementation Order

### Step 1: Signal Bridge
- Build `auto/signal_bridge.py`
- Test with Syngex log output
- Validate payload format

### Step 2: Synapse Session Config
- Create Synapse auto-trading session config
- Connect to TradeStation MCP (paper account)
- Define evaluation prompt and execution rules

### Step 3: Discord Integration
- Set up `#gex` reporting for all trade events
- Test message formatting and frequency
- Ensure no message spam (rate limiting)

### Step 4: Phase 2 Validation (Paper)
- Run Synapse auto on paper for minimum 2 weeks
- Track all decisions vs. actual outcomes
- Document Synapse's reasoning patterns

### Step 5: Phase 3 Implementation
- Add option chain analysis module
- Implement smart entry timing
- Add position management (trailing stops, partial fills)

### Step 6: Phase 3 Validation
- Run hybrid mode on paper for minimum 2 weeks
- Compare execution quality vs. Phase 2
- Validate strike selection and timing improvements

### Step 7: Phase 4 Implementation
- Add independent signal generation
- Multi-symbol portfolio management
- Session management and learning loops

### Step 8: Phase 4 Validation
- Full autonomous paper trading
- Minimum 4 weeks of tracked performance
- Hologaun review and explicit approval for live deployment

---

## Risk Management Principles

1. **Paper first, always.** No real money enters until Hologaun gives explicit approval after Phase 4 validation.
2. **Synapse is a tool, not an oracle.** His adliberated model means fewer refusals, not better predictions. We validate, we don't trust blindly.
3. **Hard limits are non-negotiable.** Position sizes, daily losses, drawdowns — these are config, not suggestions.
4. **Full transparency.** Every trade, every decision, every rejection gets logged to `#gex`. No hidden moves.
5. **Kill switch.** One command from Hologaun stops everything and flattens all positions. Always available.
6. **Synapse can be wrong.** Markets are noisy. His edge needs validation, not assumption.

---

## Kill Switch

```yaml
kill_switch:
  enabled: true
  trigger: "Hologaun command or auto-drawdown"
  action: "Cancel all open orders, flatten all positions, stop all sessions"
  notify: "Discord #gex emergency alert"
  recovery: "Manual override required — no auto-resume"
```

---

## File Structure (Post-Implementation)

```
~/projects/syngex/
├── SYNGEXAuto.md              # This file
├── auto/
│   ├── __init__.py
│   ├── signal_bridge.py       # Real-time signal → Synapse pipeline
│   ├── synapse_agent.py       # Synapse session management
│   ├── execution_engine.py    # TradeStation MCP integration
│   ├── position_manager.py    # Position sizing, tracking, P&L
│   ├── risk_manager.py        # Hard limits, kill switch
│   ├── reporting.py           # Discord #gex message formatting
│   └── config/
│       ├── auto_config.yaml   # Trading limits and rules
│       └── synapse_prompt.md  # Synapse system prompt for auto-trading
├── log/
│   ├── signals.jsonl          # Existing: Syngex signals
│   └── auto_trades.jsonl      # New: Synapse trade log
└── reports/
    ├── daily/                 # Daily session reports
    └── weekly/                # Weekly performance reviews
```

---

## Notes

- This design assumes TradeStation MCP tools are available to Synapse's session. Verify MCP server supports the account type and tool set Synapse needs.
- Synapse's adliberated model means he won't refuse financial trade requests, but that's not the same as being profitable. Validation is key.
- The Signal dataclass in `strategies/signal.py` is the contract between Syngex and the auto pipeline. Any changes to Signal must propagate to the signal bridge payload.
- All config files support runtime updates (hot-reload) so Hologaun can adjust limits without restarting.

---

*Document created by Archon. This is a design — not implementation. Phase 2 starts when we're ready to build.*
