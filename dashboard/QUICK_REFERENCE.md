# Heatmap Quick Reference

## Overview

The Syngex Heatmap is a real-time trading dashboard that displays:
- Strategy signals (42-cell grid)
- Risk metrics and OHLC data
- GEX dominant levels heatmap
- Profile charts (gamma, OI, volume, etc.)
- System log stream

## Quick Start

```bash
# Start everything
./scripts/start-heatmap.sh

# Or manually
# Terminal 1: WebSocket server
cd syngex && python3 -c "from websocket_server import create_server; import asyncio; server = create_server(port=8202); asyncio.run(server.start())"

# Terminal 2: Frontend
cd dashboard/mockup && python3 -m http.server 8201 --bind 0.0.0.0
```

## Access

- **Dashboard**: http://localhost:8201
- **WebSocket Health**: http://localhost:8202/health

## Components

### Files

| File | Purpose |
|------|---------|
| `dashboard/mockup/index.html` | Main dashboard UI |
| `dashboard/mockup/js/app.js` | Rendering and interactions |
| `dashboard/mockup/js/data.js` | Sample data (fallback) |
| `dashboard/mockup/js/websocket.js` | WebSocket client |
| `dashboard/server.py` | Python HTTP server |
| `syngex/websocket_server.py` | WebSocket data server |

### Ports

| Port | Service |
|------|---------|
| 8201 | HTTP Frontend |
| 8202 | WebSocket Server |

## Data Flow

```
Orchestrator → WebSocket Server (8202) → Frontend (8201)
     ↓                ↓                      ↓
[Signals]    [Broadcast]          [Update Strategy Grid]
[GEX]        [to clients]         [Update Heatmap]
[Metrics]    [JSON messages]      [Update Metrics]
```

## WebSocket Messages

### Subscribe
```json
{ "type": "subscribe", "channels": ["signals", "metrics", "gex"] }
```

### Snapshot (on connect)
```json
{
  "type": "snapshot",
  "timestamp": 1715840400123,
  "data": {
    "signals": [...],
    "metrics": {...},
    "gex": {...}
  }
}
```

### Updates
```json
{
  "type": "signals_update",
  "timestamp": 1715840400123,
  "data": { "signals": [...], "count": 5 }
}
```

## Status Indicators

- **Green dot** (●): WebSocket connected
- **Red dot** (●): WebSocket disconnected
- **Strategy cells**: Green (BUY), Red (SELL), Gray (inactive)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | `lsof -i :8201` then `kill -9 <PID>` |
| No data | Check WebSocket connection in DevTools |
| Blank page | Check browser console for errors |
| Won't reconnect | Check WebSocket server is running |

## Stop

```bash
pkill -f "http.server 8201"
pkill -f "websocket_server"
```

## Documentation

- **Full Plan**: `HEATMAP_IMPLEMENTATION_PLAN.md`
- **Startup Guide**: `STARTUP.md`
- **WebSocket Docs**: `syngex/WEBSOCKET_README.md`
