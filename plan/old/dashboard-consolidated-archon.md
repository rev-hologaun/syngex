# Syngex Live Metrics Dashboard - Consolidated Plan

**Author:** Archon 🕸️ (synthesizing all four plans)  
**Date:** 2026-05-20  
**Goal:** Second-by-second debug visibility with simplest implementation

---

## Executive Summary

A tile-based real-time dashboard showing live strategy calculations with confidence scores. Each strategy = one tile, line-by-line calculation stream, updates at 1Hz.

**Simplicity principle:** FastAPI backend (HTTP + WebSocket in one), vanilla JS frontend (no build step), in-memory cache (no Redis for MVP).

---

## Architecture (Simplified)

```
┌─────────────────────────────────────────────────────────┐
│                 Strategy Engine                          │
│  [gamma_scan.py]  [delta_hedge.py]  [vega_play.py]      │
│         │                  │                  │          │
│         └──────────────────┼──────────────────┘          │
│                            │                             │
│                    emit_telemetry()                       │
│                            │                             │
└────────────────────────────┼─────────────────────────────┘
                             │ HTTP POST /metrics
                    ┌────────▼────────┐
                    │   FastAPI       │
                    │   (one app)     │
                    │  - HTTP ingest  │
                    │  - WebSocket    │
                    │  - in-memory    │
                    └────────┬────────┘
                             │ WebSocket push
                    ┌────────▼────────┐
                    │  Dashboard UI   │
                    │  (vanilla JS)   │
                    │  - tile grid    │
                    │  - 1Hz refresh  │
                    └─────────────────┘
```

---

## Tile Design (Final)

```
┌─────────────────────────────────────────────────┐
│ GAMMA-SCAN              [🟢 LIVE] [conf: 87%]   │
├─────────────────────────────────────────────────┤
│ [08:05:01.123] price: 152.34      | conf: 0.92  │
│ [08:05:01.123] sma_20: 151.89     | conf: 0.88  │
│ [08:05:01.123] deviation: 0.00296 | conf: 0.87  │
│ [08:05:01.123] signal: BUY        | conf: 0.85  │
│ [08:05:01.123] vol_check: OK      | conf: 0.91  │
├─────────────────────────────────────────────────┤
│ Last update: 08:05:01.456                       │
└─────────────────────────────────────────────────┘
```

### Tile States
- **🟢 LIVE** - Active streaming, green border glow
- **🟡 PAUSED** - User paused, yellow border
- **🔴 STALE** - No update >5s, red border, pulsing
- **⚫ OFFLINE** - Strategy not running, gray border

### Confidence Color Coding
- **90-100%**: Green (`#22c55e`)
- **70-89%**: Yellow (`#f59e0b`)
- **50-69%**: Amber (`#fb923c`)
- **<50%**: Red (`#ef4444`)

---

## Implementation (Simplest Path)

### 1. Telemetry Emitter (Python)

```python
# ~/projects/syngex/dashboard/telemetry.py
import time
from dataclasses import dataclass
from typing import Dict, List, Any
import httpx  # async HTTP client

@dataclass
class TelemetryLine:
    name: str
    value: Any
    confidence: float  # 0.0-1.0

class TelemetryEmitter:
    """Strategies call this to emit metrics to dashboard."""
    
    DASHBOARD_URL = "http://localhost:8000/metrics"
    
    @classmethod
    async def emit(cls, strategy_name: str, calculations: List[TelemetryLine]):
        """Send metrics to dashboard server."""
        payload = {
            "strategy": strategy_name,
            "timestamp": time.time(),
            "lines": [
                {"name": l.name, "value": str(l.value), "confidence": l.confidence}
                for l in calculations
            ]
        }
        async with httpx.AsyncClient() as client:
            try:
                await client.post(cls.DASHBOARD_URL, json=payload, timeout=1.0)
            except Exception as e:
                # Silent fail - don't slow down strategy
                pass
```

### 2. FastAPI Backend (HTTP + WebSocket)

```python
# ~/projects/syngex/dashboard/server.py
from fastapi import FastAPI, WebSocket
from typing import Dict, List
import time

app = FastAPI()

# In-memory storage
strategy_data: Dict[str, dict] = {}
websockets: List[WebSocket] = []

@app.post("/metrics")
async def receive_metrics(data: dict):
    """Strategy calls this to send metrics."""
    strategy = data["strategy"]
    strategy_data[strategy] = {
        "lines": data["lines"],
        "timestamp": data["timestamp"],
        "status": "LIVE"
    }
    # Broadcast to all connected dashboards
    await broadcast(data)
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Dashboard connects here for live updates."""
    await websocket.accept()
    websockets.append(websocket)
    
    # Send initial state
    await websocket.send_json({"type": "init", "data": strategy_data})
    
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        websockets.remove(websocket)

async def broadcast(payload: dict):
    """Send update to all connected dashboards."""
    message = {"type": "update", "data": payload}
    for ws in websockets:
        try:
            await ws.send_json(message)
        except:
            pass  # Dead connection

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3. Frontend (Vanilla HTML/CSS/JS)

```html
<!-- ~/projects/syngex/dashboard/index.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Syngex Live Metrics</title>
    <style>
        body { background: #111; color: #eee; font-family: 'JetBrains Mono', monospace; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 16px; padding: 20px; }
        .tile { border: 2px solid #444; border-radius: 8px; padding: 12px; }
        .tile.live { border-color: #22c55e; box-shadow: 0 0 8px rgba(34, 197, 94, 0.3); }
        .tile.stale { border-color: #ef4444; animation: pulse 2s infinite; }
        .header { display: flex; justify-content: space-between; margin-bottom: 12px; }
        .line { padding: 4px 0; border-bottom: 1px solid #222; }
        .line .conf { float: right; }
        .conf-90 { color: #22c55e; }
        .conf-70 { color: #f59e0b; }
        .conf-50 { color: #fb923c; }
        .conf-0 { color: #ef4444; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
    </style>
</head>
<body>
    <h1>Syngex Live Metrics Dashboard</h1>
    <div id="grid" class="grid"></div>
    <script>
        const ws = new WebSocket('ws://localhost:8000/ws');
        const grid = document.getElementById('grid');
        
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if (msg.type === 'init') renderAll(msg.data);
            else if (msg.type === 'update') renderTile(msg.data);
        };
        
        function renderAll(data) {
            grid.innerHTML = '';
            Object.entries(data).forEach(([name, d]) => renderTile({strategy: name, ...d}));
        }
        
        function renderTile({strategy, lines, timestamp, status = 'LIVE'}) {
            const tile = document.createElement('div');
            tile.className = `tile ${status.toLowerCase()}`;
            
            const maxConf = Math.max(...lines.map(l => l.confidence));
            tile.innerHTML = `
                <div class="header">
                    <strong>${strategy.toUpperCase()}</strong>
                    <span>[${status}] [conf: ${Math.round(maxConf * 100)}%]</span>
                </div>
                <div class="lines">
                    ${lines.map(l => `
                        <div class="line">
                            <span>[${new Date(timestamp * 1000).toISOString().split('T')[1].slice(0,12)}] ${l.name}: ${l.value}</span>
                            <span class="conf conf-${Math.floor(l.confidence / 0.1) * 10 - 10}">${Math.round(l.confidence * 100)}%</span>
                        </div>
                    `).join('')}
                </div>
                <small>Last: ${new Date(timestamp * 1000).toLocaleTimeString()}</small>
            `;
            
            // Replace existing tile or append
            const existing = grid.querySelector(`[data-strategy="${strategy}"]`);
            if (existing) existing.replaceWith(tile);
            else tile.dataset.strategy = strategy;
        }
    </script>
</body>
</html>
```

---

## File Structure

```
~/projects/syngex/
├── dashboard/
│   ├── telemetry.py           # Emitter class (import in strategies)
│   ├── server.py              # FastAPI backend
│   ├── index.html             # Frontend (open in browser)
│   └── requirements.txt       # fastapi, uvicorn, httpx
├── src/
│   └── strategies/
│       └── gamma_scan.py      # Add: from telemetry import TelemetryEmitter
└── plan/
    └── dashboard-consolidated-archon.md
```

---

## Integration Example (Strategy)

```python
# ~/projects/syngex/src/strategies/gamma_scan.py
from telemetry import TelemetryEmitter, TelemetryLine

class GammaScan:
    async def calculate(self, market_data):
        lines = [
            TelemetryLine("price", market_data["price"], 0.92),
            TelemetryLine("sma_20", self.sma_20, 0.88),
            TelemetryLine("deviation", self.deviation, 0.87),
            TelemetryLine("signal", "BUY", 0.85),
        ]
        await TelemetryEmitter.emit("gamma_scan", lines)
        return {"signal": "BUY"}
```

---

## Implementation Phases

### Phase 1: Core Backend (Forge)
- [ ] Create `dashboard/` directory
- [ ] Write `telemetry.py` emitter class
- [ ] Write `server.py` FastAPI app
- [ ] Test with `python server.py` and manual HTTP POST

### Phase 2: Frontend (Forge)
- [ ] Write `index.html` with vanilla JS
- [ ] Test WebSocket connection
- [ ] Verify tile rendering and confidence colors

### Phase 3: Integration (Archon + Forge)
- [ ] Add telemetry hooks to existing strategies
- [ ] Test end-to-end (strategy → server → dashboard)
- [ ] Tune update rate (1Hz target)
- [ ] Add stale detection (>5s timeout)

---

## Questions for Hologaun

1. **FastAPI OK?** We skip Node entirely for simplicity.
2. **Vanilla JS OK?** No React/Vue build step needed.
3. **Existing strategies:** Should I delegate the telemetry hook integration to Forge after Phase 1 is done?
4. **Deployment:** Run server as background process? systemd service?

---

Ready to start Phase 1. This is the simplest path to working dashboard in ~1 day. 🕸️
