# Heatmap Startup Procedure

Quick reference for starting the Syngex Heatmap system.

## Quick Start

### Option 1: Use Startup Script (Recommended)

```bash
cd /home/hologaun/.openclaw/workspace/forge
./scripts/start-heatmap.sh
```

### Option 2: Manual Start

Open three terminal windows:

**Terminal 1 - WebSocket Server:**
```bash
cd /home/hologaun/.openclaw/workspace/forge/syngex
python3 -c "
from websocket_server import create_server
import asyncio
server = create_server(port=8202)
asyncio.run(server.start())
"
```

**Terminal 2 - HTTP Frontend:**
```bash
cd /home/hologaun/.openclaw/workspace/forge/dashboard/mockup
python3 -m http.server 8201 --bind 0.0.0.0
```

**Terminal 3 - Test/Monitor:**
```bash
# Check WebSocket health
curl http://localhost:8202/health

# Open browser
open http://localhost:8201  # macOS
xdg-open http://localhost:8201  # Linux
```

## Access

| Service | URL | Port |
|---------|-----|------|
| Frontend Dashboard | http://localhost:8201 | 8201 |
| WebSocket Server | ws://localhost:8202/ws | 8202 |
| Health Check | http://localhost:8202/health | 8202 |

## Stop

### Using Script

Press `Ctrl+C` in the terminal running the script.

### Manual Stop

```bash
# Kill by port
pkill -f "http.server 8201"
pkill -f "websocket_server"

# Or by PID (if you recorded them)
kill <WS_PID> <HTTP_PID>
```

## Verify Running

```bash
# Check ports
lsof -i :8201
lsof -i :8202

# Check health
curl http://localhost:8202/health

# Check frontend
curl http://localhost:8201/index.html | head -5
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8201
lsof -i :8202

# Kill process
kill -9 <PID>
```

### WebSocket Not Connecting

1. Verify server is running: `curl http://localhost:8202/health`
2. Check browser console for errors
3. Verify WebSocket URL is `ws://localhost:8202/ws`

### Frontend Not Loading

1. Verify HTTP server is running: `curl http://localhost:8201`
2. Check that mockup files exist: `ls dashboard/mockup/`
3. Verify you're in the correct directory

### No Data Displaying

1. Check WebSocket connection in browser DevTools (Network tab → WS)
2. Verify orchestrator is sending data
3. Check browser console for JavaScript errors

## Auto-Start (Production)

### systemd Service

```bash
# Enable service
sudo systemctl enable syngex-heatmap
sudo systemctl start syngex-heatmap

# Check status
sudo systemctl status syngex-heatmap

# View logs
sudo journalctl -u syngex-heatmap -f
```

### Startup Script (.bashrc)

Add to `~/.bashrc`:
```bash
alias start-heatmap='cd /home/hologaun/.openclaw/workspace/forge && ./scripts/start-heatmap.sh'
alias stop-heatmap='pkill -f "http.server 8201" && pkill -f "websocket_server"'
```

## Logs

### WebSocket Server
- Console output (stdout)
- Configure logging level in `websocket_server.py`

### HTTP Server
- Console output (stdout)
- Python's built-in HTTP server logging

### Browser Console
- Open DevTools (F12)
- Check Console tab for errors
- Check Network tab → WS for WebSocket status

## Next Steps

See `HEATMAP_IMPLEMENTATION_PLAN.md` for full implementation details.
