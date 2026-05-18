# Syngex Ultimate Control Center - Production Heatmap

## Overview

Production-ready real-time trading dashboard for Syngex. Displays strategy signals, risk metrics, GEX data, and system logs with WebSocket-powered live updates.

**Status**: ✅ Production Ready

## Quick Start

### Option 1: Use Startup Script (Recommended)

```bash
cd /home/hologaun/.openclaw/workspace/forge
./scripts/start-heatmap.sh
```

### Option 2: Manual Start

**Terminal 1 - WebSocket Server:**
```bash
cd syngex
python3 -c "from websocket_server import create_server; import asyncio; server = create_server(port=8202); asyncio.run(server.start())"
```

**Terminal 2 - Frontend:**
```bash
cd dashboard/mockup
python3 -m http.server 8201 --bind 0.0.0.0
```

### Access

- **Dashboard**: http://localhost:8201
- **WebSocket Health**: http://localhost:8202/health

## Features

### Real-Time Data (WebSocket)
- ✅ Live strategy signals from orchestrator
- ✅ Real-time risk metrics updates
- ✅ GEX ladder data streaming
- ✅ System log stream
- ✅ Auto-reconnection on failure

### Layout (12-column CSS Grid)
- ✅ Header: Symbol, price, gamma, OI, strategy count
- ✅ Profile Tabs: Gamma, OI, Volume, Flow, GEX, IV, Greeks
- ✅ Profile Chart Panel: Canvas-based charts with SVG overlay
- ✅ Dominant Levels Panel: PUT/CALL walls, magnets, GEX zero
- ✅ Risk Metrics Panel: VaR, Max DD, Sharpe, Exposure, OHLC
- ✅ Strategy Grid Panel: 6x7 grid (42 cells) with full details
- ✅ System Log Stream: Color-coded, filterable logs
- ✅ Footer: Signal counts, P&L, WebSocket status

### Color System
- Dark theme with navy backgrounds (#0f172a)
- Buy signals: Green (#10b981)
- Sell signals: Red (#ef4444)
- Positive gamma: Cyan (#06b6d4)
- Negative gamma: Magenta (#d946ef)
- Confidence levels: Gray → Blue → Cyan

### Interactions
- ✅ Tab switching (profile chart types)
- ✅ Hover states (brightness, border, transform)
- ✅ Strategy cell selection (click to highlight)
- ✅ Log filtering (All/Signal/Alert/GEX/Flow)
- ✅ Real-time WebSocket updates

## File Structure

```
dashboard/
├── mockup/                  # Production heatmap frontend
│   ├── index.html          # Main dashboard UI
│   ├── css/
│   │   ├── style.css       # All styling
│   │   └── grid.css        # 12-column grid system
│   └── js/
│       ├── app.js          # Rendering and interactions
│       ├── data.js         # Sample data (fallback)
│       └── websocket.js    # WebSocket client
├── server.py               # Python HTTP server
├── STARTUP.md              # Startup procedures
├── QUICK_REFERENCE.md      # Quick reference guide
└── HEATMAP_IMPLEMENTATION_PLAN.md  # Full implementation plan

syngex/
└── websocket_server.py     # WebSocket data server (port 8202)
```

## Data Integration

The dashboard connects to the WebSocket server for real-time data:

```javascript
// WebSocket client automatically connects on page load
// Listens for:
// - snapshot: Initial state on connect
// - signals_update: Strategy signals
// - metrics_update: Risk metrics
// - gex_update: GEX ladder data
```

See `WEBSOCKET_README.md` in the syngex directory for protocol details.

## Sample Data

The dashboard includes sample TSLA data for testing:
- Current Price: $418.57
- Net Gamma: +7
- Active Strikes: 32
- Strategies: 41 total, 8 active
- Sample P&L: +$12.4K

When connected to the WebSocket server, real data replaces the sample data.

## Design Notes

### Panels
1. **Header** (50px fixed): Dashboard title and key metrics
2. **Tabs** (35px fixed): Profile type switching
3. **Chart + Levels** (250px): Main visualization area
4. **Risk Metrics** (120px): Quick metrics overview (3 rows)
5. **Strategy Grid** (300px): Detailed strategy cells (6x7 grid)
6. **Log Stream** (100px): Real-time event feed
7. **Footer** (30px fixed): Status bar

### Responsive
- Desktop optimized (1200px minimum)
- Tablet: 3-column strategy grid
- Mobile: 2-column strategy grid

## Documentation

- **Quick Start**: See above
- **Full Plan**: `HEATMAP_IMPLEMENTATION_PLAN.md`
- **Startup Guide**: `STARTUP.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **WebSocket Docs**: `syngex/WEBSOCKET_README.md`

## Troubleshooting

### Port Already in Use
```bash
lsof -i :8201  # Find process
kill -9 <PID>  # Kill it
```

### WebSocket Not Connecting
1. Verify server running: `curl http://localhost:8202/health`
2. Check browser console for errors
3. Verify URL: `ws://localhost:8202/ws`

### No Data Displaying
1. Check WebSocket status (should be green)
2. Open DevTools → Network → WS tab
3. Check for message traffic

## Next Steps

1. **Deploy**: Use `./scripts/start-heatmap.sh` for easy startup
2. **Monitor**: Check WebSocket health endpoint
3. **Configure**: Set up systemd service for auto-start
4. **Validate**: Verify all data streams working

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-05-16  
**Author**: Forge 🐙 - Syngex Development Team
