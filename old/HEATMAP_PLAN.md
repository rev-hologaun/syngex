# Syngex Heatmap Dashboard — Design Plan

## Goal

Launch a **second web process** alongside the existing Streamlit Command Center that serves a real-time "Syngex Command Grid" heatmap — a CSS Grid layout showing all 22 strategies as live status cards.

## Current Architecture

```
TradeStation API
    ↓
TradeStationClient (main.py async loop)
    ↓
GEXCalculator (processes messages, builds gamma ladder)
    ↓
StrategyEngine (evaluates 22 strategies, emits signals)
    ↓
JSON file: data/gex_state_{SYMBOL}.json  (updated every 1s)
    ↓
Streamlit app (app_dashboard.py) ← port 8501 ← polls JSON every 2s
```

The Streamlit dashboard is a **single-page** GEX-focused view. The heatmap is a **strategy-centric** view — different lens, different data emphasis.

## Design: Dual-Process Web Layer

### Overview

```
main.py (orchestrator)
    ├── Streamlit subprocess  →  :8501  (Command Center — GEX focused)
    └── Flask subprocess      →  :8502  (Heatmap — strategy grid focused)
            ↕ WebSocket (Flask-SocketIO)
            ↕ JSON file read (data/gex_state_{SYMBOL}.json)
            ↓
        Browser → heatmap.html (CSS Grid layout, Synapse's prototype adapted)
```

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | **Flask + Flask-SocketIO** | Lightweight, already fits the project. No need to add Node.js. |
| Port | **8502** | Separate from Streamlit's 8501. No port conflicts. |
| Data transport | **WebSocket push** (not polling) | Real-time updates, lower latency, cleaner architecture. |
| Heatmap data source | **Shared JSON file** (read-only) | Decouples heatmap from orchestrator. Orchestrator writes, heatmap reads. |
| HTML template | **Adapted Synapse prototype** | Reuse the CSS Grid pattern, populate with strategy cards. |

### File Changes

#### New files:
1. **`app_heatmap.py`** — Flask app + SocketIO server
   - Serves `heatmap.html` at `/`
   - Connects via SocketIO at `/socket.io`
   - Reads `data/gex_state_{SYMBOL}.json` every 1s
   - Pushes updates via SocketIO events

2. **`heatmap.html`** — The heatmap page (adapted from Synapse's prototype)
   - CSS Grid: 6 columns × 4 rows = 24 cells (22 strategies + 2 system widgets)
   - Each strategy card: status LED, name, sparkline, PnL, last signal time
   - Background pulse color: green (profitable), amber (edge), grey (idle), red (bleeding)
   - JavaScript: SocketIO client, renders cards, updates sparklines

3. **`config/heatmap.yaml`** — Heatmap layout config
   - Which strategies go in which cells
   - Card sizing (span-1, span-2-cols, span-2-rows)
   - Color thresholds

#### Modified files:
4. **`main.py`** — Orchestrator
   - Add `_start_heatmap()` and `_stop_heatmap()` (parallel to Streamlit logic)
   - Export enhanced state: add strategy-level data to JSON (per-strategy PnL, signal count, status)
   - New CLI flag: `--heatmap` (starts heatmap on port 8502)
   - Or auto-start when `--port` is specified

5. **`requirements.txt`** — Add `flask`, `flask-socketio`, `python-socketio[asyncio]`

### Data Flow (Heatmap)

```
main.py orchestrator
    │
    ├── writes to: data/gex_state_{SYMBOL}.json (every 1s)
    │       {
    │         "symbol": "TSLA",
    │         "underlying_price": 285.42,
    │         "net_gamma": 1234567.89,
    │         "strikes": { ... },
    │         "strategy_engine": {
    │           "strategies": 22,
    │           "total_signals": 147,
    │           "per_strategy": {          ← NEW
    │             "gamma_wall_bounce": {
    │               "status": "active",     ← active | idle | error
    │               "signal_count": 23,
    │               "last_signal": 1714723200,
    │               "win_rate": 0.65,
    │               "pnl": 420.00,
    │               "sparkline": [10, 12, 11, 14, 13, 15, 14, 16]  ← last 8
    │             },
    │             ...
    │           }
    │         },
    │         "regime_filter": { ... },
    │         "last_updated": "2026-05-03 10:30:00 PDT"
    │       }
    │
    ▼
app_heatmap.py (Flask + SocketIO)
    │
    ├── reads JSON file (every 1s)
    ├── transforms → SocketIO event payload
    └── emits: socket.emit('strategy_update', payload)
    │
    ▼
Browser (heatmap.html)
    │
    ├── connects: io('http://localhost:8502')
    ├── listens: socket.on('strategy_update', render)
    └── renders: CSS Grid with strategy cards
```

### Heatmap Layout (6×4 Tactical Matrix)

```
┌─────────────────────────────────────────────────────────────┐
│  🕸️ SYNGEX COMMAND GRID — TSLA              [Regime: POS_GAMMA]  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │
│  │L1-01 │ │L1-02 │ │L1-03 │ │L1-04 │ │L1-05 │ │L1-06 │     │
│  │WALL  │ │MAGNET│ │FLIP  │ │SQUEEZE│ │IMBAL │ │CONFL │     │
│  │BOUNCE│ │ACCEL │ │BREAK │ │       │ │ANCE │ │ENCE │     │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘     │
│  ┌──────┐ ┌──────┐ ┌──────────────┐ ┌──────┐ ┌──────┐     │
│  │L1-07 │ │L1-08 │ │  L2 OVERVIEW  │ │L2-01 │ │L2-02 │     │
│  │VOL_  │ │GEX_  │ │  (span 2 cols)│ │DELTA │ │DELTA │     │
│  │COMP  │ │DIV   │ │               │ │GAMMA │ │VOL_ │     │
│  └──────┘ └──────┘ └──────────────┘ └──────┘ └──────┘     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │
│  │L2-03 │ │L2-04 │ │L3-01 │ │L3-02 │ │L3-03 │ │L3-04 │     │
│  │CALL  │ │IV_  │ │GAMMA │ │IV_  │ │STRIKE│ │THETA │     │
│  │PUT_  │ │GEX_  │ │VOL_  │ │BAND  │ │CONC │ │BURN │     │
│  │FLOW  │ │DIV   │ │CONV  │ │BREAK │ │TRAT │ │     │     │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────┐ ┌──────┐     │
│  │FULL-01       │ │FULL-02       │ │FULL-03│ │FULL-04│     │
│  │IV SKEW       │ │PROB WEIGHTED │ │PROB  │ │EXTRIN│     │
│  │SQUEEZE       │ │MAGNET        │ │DIST  │ │SIC   │     │
│  └──────────────┘ └──────────────┘ └──────┘ └──────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐│
│  │  SYSTEM LOG STREAM (span full width)                    ││
│  │  [10:30:01] SIGNAL: gamma_wall_bounce LONG conf=0.82   ││
│  │  [10:30:02] RESOLVED: vol_compression_range WIN +$125  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Strategy Card Anatomy

Each card in the grid shows:

1. **Background pulse** — color reflects strategy health:
   - `#065f46` (deep green) — win_rate ≥ 0.60 AND pnl > 0
   - `#92400e` (amber) — win_rate 0.35–0.60 OR pnl near 0
   - `#1f2937` (dark grey) — idle (no signals in last 5 min)
   - `#7f1d1d` (crimson) — win_rate < 0.35 OR pnl < -$100

2. **Header row:**
   - Left: Strategy short name (e.g., `GEX_WALL_BOUNCE`)
   - Right: Status LED — 🟢 active / ⚪ idle / 🔴 error

3. **Center:**
   - Mini sparkline (canvas-drawn line, 40×20px)
   - Shows last 8 data points of cumulative PnL or signal count

4. **Footer row:**
   - Left: `Last: 14:22` (HH:MM of last signal)
   - Right: `PnL: +$420` (color-coded)
   - Bottom edge: thin confidence bar (0–100%)

### WebSocket Events

```python
# Server → Client
socket.emit('strategy_update', {
    'symbol': 'TSLA',
    'underlying_price': 285.42,
    'regime': 'POS_GAMMA',
    'timestamp': 1714723200,
    'strategies': {
        'gamma_wall_bounce': {
            'status': 'active',
            'signal_count': 23,
            'last_signal_ts': 1714723200,
            'win_rate': 0.65,
            'pnl': 420.00,
            'sparkline': [10, 12, 11, 14, 13, 15, 14, 16]
        },
        ...
    }
})

# Client → Server (optional, for future interactivity)
socket.emit('card_click', {'strategy_id': 'gamma_wall_bounce'})
```

### Flask App Structure (`app_heatmap.py`)

```python
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import time
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'syngex-heatmap-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = Path(__file__).parent / "data" / f"gex_state_{os.environ.get('SYNGEX_SYMBOL', 'UNKNOWN')}.json"

@app.route('/')
def index():
    return render_template('heatmap.html')  # or serve static HTML directly

@socketio.on('connect')
def handle_connect():
    # Push latest data immediately on connect
    push_latest()

def push_latest():
    """Read JSON, transform, emit to all connected clients."""
    if not DATA_FILE.exists():
        return
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
        socketio.emit('strategy_update', data)
    except Exception:
        pass

# Background task: push every 1 second
def _background_updater():
    while True:
        socketio.sleep(1)
        push_latest()
```

### Integration with `main.py`

Add to `SyngexOrchestrator`:

```python
# New fields
self._heatmap_process: subprocess.Popen | None = None

# New methods (mirror _start_dashboard / _stop_dashboard)
def _start_heatmap(self) -> None:
    # Spawn Flask subprocess on port 8502
    ...

def _stop_heatmap(self) -> None:
    # Terminate Flask subprocess
    ...

# In run():
if self.mode == "dashboard":
    self._start_dashboard()
    self._start_heatmap()  # NEW: start heatmap alongside
```

### Dependencies

Add to `requirements.txt`:
```
flask
flask-socketio
python-socketio[asyncio]
```

### Implementation Order

1. **Phase 1 — Skeleton** (Forge)
   - Add Flask + SocketIO to requirements
   - Create `app_heatmap.py` with basic Flask/SocketIO server
   - Create `heatmap.html` adapted from Synapse's prototype
   - Wire into `main.py` (`_start_heatmap`, `--port` flag)
   - Test: static page loads, no data yet

2. **Phase 2 — Data Pipeline** (Forge)
   - Enhance JSON export in `main.py` with per-strategy data
   - Flask reads JSON, emits via SocketIO
   - Browser connects, renders cards with data

3. **Phase 3 — Polish** (Forge)
   - Sparkline rendering (canvas/SVG)
   - Status LED animations (CSS pulse)
   - Background pulse colors based on health
   - Config-driven layout (`config/heatmap.yaml`)
   - Responsive breakpoints

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| JSON file race condition | Flask reads with try/except; skips if corrupt |
| Flask blocks main thread | Runs as subprocess (like Streamlit), no blocking |
| WebSocket disconnects | SocketIO auto-reconnects; push_latest() on reconnect |
| Too many JSON writes | Orchestrator writes once/sec; Flask reads same file |
| Port conflict | Hardcoded 8502, separate from 8501 |
