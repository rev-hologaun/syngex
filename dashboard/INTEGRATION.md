# Heatmap Dashboard Integration

## Overview
The new mockup heatmap has been integrated into the main.py orchestrator. Running:

```bash
python3 main.py --port 8200 tsla dashboard
```

Now launches the new mockup heatmap on port 8201 (port + 1) instead of the old Streamlit dashboard.

## Architecture

### Components

| Component | Port | Status | Description |
|-----------|------|--------|-------------|
| **Command Center** | 8200 (configurable) | ✅ Main orchestrator | Streamlit dashboard from `app_dashboard.py` |
| **Heatmap** | 8201 (port + 1) | ✅ Integrated | Static file server from `dashboard/server.py` |
| **WebSocket** | 8202 (port + 2) | ✅ Integrated | Real-time data from `websocket_server.py` |

### File Structure

```
dashboard/
├── server.py          # NEW: Integrated HTTP server
├── mockup/
│   ├── index.html     # Main HTML (inline CSS)
│   └── js/
│       ├── app.js     # Application logic
│       └── websocket.js  # WebSocket client (connects to ws://localhost:8202/ws)
```

## Changes Made

### 1. Created `dashboard/server.py`
- Serves the mockup as static files
- Runs as a background thread (not a subprocess)
- Integrated into orchestrator lifecycle
- Features:
  - No caching (development-friendly)
  - Proper logging via Syngex logger
  - Clean shutdown support

### 2. Modified `orchestrator/lifecycle.py`
- Updated `_start_heatmap()`: Now imports and runs `dashboard.server.run_heatmap()` as a thread
- Updated `_stop_heatmap()`: Now calls `dashboard.server.stop_heatmap()` for clean shutdown
- Added instance variables: `_heatmap_server` and `_heatmap_thread`

### 3. WebSocket Integration
- Mockup's `websocket.js` already connects to `ws://localhost:8202/ws`
- WebSocket server runs on port 8202 (main port + 2)
- No changes needed - already compatible

## Usage

### Start with Dashboard
```bash
cd ~/projects/syngex
python3 main.py --port 8200 tsla dashboard
```

This will:
1. Start Command Center on http://localhost:8200
2. Start Heatmap on http://localhost:8201
3. Start WebSocket on ws://localhost:8202/ws

### Access Points
- **Command Center**: http://localhost:8200
- **Heatmap**: http://localhost:8201
- **WebSocket**: ws://localhost:8202/ws

## Old Dashboard Status
The old dashboard files (`app.py`, `client.py`) have been replaced. The new mockup is fully self-contained in the `mockup/` directory.

## Technical Details

### Server Implementation
```python
# dashboard/server.py
def run_heatmap(host='0.0.0.0', port=8001):
    """Start HTTP server serving the mockup heatmap."""
    server = HTTPServer((host, port), HeatmapHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread

def stop_heatmap(server):
    """Stop the heatmap server."""
    server.shutdown()
```

### Integration in Orchestrator
```python
# orchestrator/lifecycle.py
def _start_heatmap(self):
    from dashboard.server import run_heatmap
    self._heatmap_server, self._heatmap_thread = run_heatmap(port=heatmap_port)

def _stop_heatmap(self):
    from dashboard.server import stop_heatmap
    stop_heatmap(self._heatmap_server)
```

## Benefits

1. **Single Command**: Everything starts with one `python3 main.py` command
2. **No Separate Processes**: Heatmap runs as a thread, not a subprocess
3. **Clean Shutdown**: Proper lifecycle management
4. **No Caching**: Development-friendly with no-cache headers
5. **WebSocket Ready**: Already configured for real-time updates

## Testing

To test the integration:
```bash
# Start the orchestrator
python3 main.py --port 8200 tsla dashboard

# Verify services are running
curl http://localhost:8200  # Command Center
curl http://localhost:8201  # Heatmap
curl http://localhost:8202/health  # WebSocket health check

# Stop with Ctrl+C
```

## Future Enhancements

- Add more mockup features as needed
- Enhance WebSocket message formats
- Add production caching options
- Add HTTPS support if needed

---

**Integration Date**: May 16, 2026  
**Status**: ✅ Complete and tested
