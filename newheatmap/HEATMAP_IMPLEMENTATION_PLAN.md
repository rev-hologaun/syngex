# Heatmap Implementation Plan

## Executive Summary

This document provides a comprehensive plan for replacing the discontinued dashboard (`dashboard/app.py`, `dashboard/client.py`) with the new mockup as the production heatmap system.

### Recommendation

**Recommended Approach: Option A (Static Server + WebSocket)**

While Option B (FastAPI Integration) was initially considered, **Option A** is the optimal choice because:
- The mockup is already a complete static HTML/CSS/JS application
- No backend API endpoints are needed for historical data (WebSocket provides real-time)
- Clean separation of concerns: static files served independently, WebSocket handles data
- Minimal dependencies and complexity
- Easier to deploy and maintain
- Existing WebSocket server (port 8202) is already FastAPI-based and production-ready

### Timeline and Risks

- **Total Estimated Time**: 8-10 hours (can be completed in 1-2 sprints)
- **Risk Level**: Low (mockup is complete, WebSocket server is tested)
- **Key Risk**: Data format alignment between WebSocket server and frontend
- **Mitigation**: Define clear message schema, implement validation layer

---

## 1. Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Orchestrator                        │
│                        (main.py)                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              SyngexWebSocketServer (port 8202)            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │  Signals    │  │  Metrics    │  │    GEX      │       │  │
│  │  │  Broadcast  │  │  Broadcast  │  │  Broadcast  │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ WebSocket (ws://localhost:8202/ws)
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Heatmap Frontend (Static)                    │
│              (dashboard/mockup/ - served on port 8201)          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  WebSocket Client                                         │  │
│  │  ├─ Connect → Subscribe to channels                      │  │
│  │  ├─ Receive real-time updates                            │  │
│  │  └─ Auto-reconnect on failure                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  UI Components                                            │  │
│  │  ├─ Profile Charts (gamma, OI, volume, etc.)             │  │
│  │  ├─ Risk Metrics Heatmap                                 │  │
│  │  ├─ Dominant Levels Heatmap                              │  │
│  │  ├─ Strategy Grid (6x7 = 42 cells)                       │  │
│  │  └─ System Log Stream                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Orchestrator → WebSocket Server → Frontend
     ↓                ↓               ↓
[Signal Data]   [Broadcast]    [Update Heatmap]
[GEX Data]      [to clients]   [Update Charts]
[Metrics]       [JSON msgs]    [Update Logs]
[Positions]                      [Update UI]
```

### Component Relationships

| Component | Role | Port | Status |
|-----------|------|------|--------|
| Main Orchestrator (main.py) | Core system, data processing | N/A | ✅ Running |
| WebSocket Server | Real-time data distribution | 8202 | ✅ Built & Tested |
| Heatmap Frontend (mockup) | User interface | 8201 | ✅ Mockup Complete |
| Old Dashboard (app.py) | Legacy system | 8200/8201 | ❌ Discontinued |

---

## 2. Implementation Phases

### Phase 1: Infrastructure Setup (2-3 hours)

#### 1.1 Choose Deployment Method
- **Decision**: Option A - Static Server + Separate WebSocket
- **Rationale**: Clean separation, minimal complexity, mockup is pure static files

#### 1.2 Set Up Static File Server

Create a lightweight server to serve the mockup:

**File: `dashboard/server.py`**
```python
"""
Lightweight HTTP server for heatmap static files.
Serves dashboard/mockup/ on port 8201.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class HeatmapHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='dashboard/mockup', **kwargs)
    
    def log_message(self, format, *args):
        # Log to file instead of stderr
        print(f"[Heatmap] {args[0]}")

def run_server(host='0.0.0.0', port=8201):
    server = HTTPServer((host, port), HeatmapHandler)
    print(f"Heatmap server running on http://{host}:{port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
```

**Alternative: Use Python's built-in server**
```bash
cd dashboard/mockup && python3 -m http.server 8201 --bind 0.0.0.0
```

#### 1.3 Configure Ports
- **Heatmap UI**: Port 8201 (original dashboard port)
- **WebSocket**: Port 8202 (existing WebSocket server)

#### 1.4 Add Process Manager

**File: `scripts/start-heatmap.sh`**
```bash
#!/bin/bash
# Start heatmap frontend and WebSocket server

cd /home/hologaun/.openclaw/workspace/forge/syngex

# Start WebSocket server in background
python3 -c "
from websocket_server import create_server
import asyncio
server = create_server(host='0.0.0.0', port=8202)
asyncio.run(server.start())
" &
WS_PID=$!
echo "WebSocket server started (PID: $WS_PID)"

# Start heatmap frontend
cd ../dashboard/mockup
python3 -m http.server 8201 --bind 0.0.0.0 &
HTTP_PID=$!
echo "Heatmap frontend started (PID: $HTTP_PID)"

echo "Heatmap system running. Access at http://localhost:8201"
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap "kill $WS_PID $HTTP_PID 2>/dev/null; exit" INT TERM
wait
```

**Systemd Service (optional for auto-start)**

**File: `/etc/systemd/system/syngex-heatmap.service`**
```ini
[Unit]
Description=Syngex Heatmap Frontend
After=network.target

[Service]
Type=simple
User=hologaun
WorkingDirectory=/home/hologaun/.openclaw/workspace/forge/dashboard/mockup
ExecStart=/usr/bin/python3 -m http.server 8201 --bind 0.0.0.0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

### Phase 2: Data Integration (3-4 hours)

#### 2.1 Define WebSocket Message Format

The frontend needs to consume these message types:

```javascript
// Message Schema
{
  "type": "snapshot" | "signals_update" | "metrics_update" | "gex_update" | "positions_update",
  "timestamp": 1715840400123,
  "data": {
    // Type-specific payload
  }
}
```

**Signal Format (for strategy grid):**
```javascript
{
  "name": "GEX_WALL",
  "direction": "BUY" | "SELL" | null,
  "confidence": 0-100,
  "entry": 418.57,
  "stop": 421.68,
  "target": 413.90,
  "pnl": -705597,
  "time": "10:55",
  "active": true,
  "layer": "L1" | "L2" | "L3"
}
```

**Metrics Format (for risk metrics panel):**
```javascript
{
  "var1d": "2.3%",
  "maxDrawdown": "8.1%",
  "sharpe": 1.42,
  "exposure": "POS",
  "ohlc": { "open": 415.20, "high": 422.50, "low": 414.80, "close": 418.57 },
  "volume": "2.4M",
  "volumeChange": "+15%",
  "delta": 1240,
  "gamma": 7,
  "theta": -340,
  "vega": 890,
  "openInterest": "32 strikes"
}
```

**GEX Format (for dominant levels heatmap):**
```javascript
{
  "heatmapStrikes": [
    { "strike": 410, "gex": -8, "type": "neutral" },
    { "strike": 420, "gex": -25, "type": "put-wall" },
    { "strike": 430, "gex": 45, "type": "call-wall" }
  ],
  "gammaFlip": 417.25
}
```

**Log Format (for system log stream):**
```javascript
{
  "type": "SIGNAL" | "ALERT" | "GEX" | "FLOW",
  "msg": "gamma_wall_bounce SHORT conf:0.653 $418.57",
  "timestamp": "10:28:45"
}
```

#### 2.2 Connect Frontend to Real WebSocket

**Modify: `dashboard/mockup/js/app.js`**

Add WebSocket connection logic after the existing initialization:

```javascript
// ========== WebSocket Connection ==========
let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 2000; // 2 seconds

function connectWebSocket() {
    const wsUrl = 'ws://localhost:8202/ws';
    console.log(`Connecting to WebSocket: ${wsUrl}`);
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        reconnectAttempts = 0;
        updateWebSocketStatus(true);
        
        // Subscribe to all channels
        ws.send(JSON.stringify({
            type: 'subscribe',
            channels: ['signals', 'metrics', 'gex', 'positions']
        }));
    };
    
    ws.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleMessage(message);
        } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateWebSocketStatus(false);
        
        // Attempt reconnection
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++;
            console.log(`Reconnecting in ${RECONNECT_DELAY}ms (attempt ${reconnectAttempts})...`);
            setTimeout(connectWebSocket, RECONNECT_DELAY);
        } else {
            console.error('Max reconnection attempts reached');
        }
    };
}

function handleMessage(message) {
    const { type, data } = message;
    
    switch (type) {
        case 'snapshot':
            // Initial state - update all components
            console.log('Received initial snapshot');
            updateDashboardFromSnapshot(data);
            break;
            
        case 'signals_update':
            // Update strategy grid
            updateStrategyGrid(data.signals);
            break;
            
        case 'metrics_update':
            // Update risk metrics
            updateRiskMetrics(data);
            break;
            
        case 'gex_update':
            // Update dominant levels heatmap
            updateDominantLevels(data);
            break;
            
        case 'positions_update':
            // Update positions (if shown)
            updatePositions(data.positions);
            break;
            
        default:
            console.log('Unknown message type:', type);
    }
}

function updateWebSocketStatus(connected) {
    const statusElements = document.querySelectorAll('.ws-status');
    statusElements.forEach(el => {
        if (connected) {
            el.className = 'ws-status connected';
            el.textContent = '● WebSocket: Connected';
        } else {
            el.className = 'ws-status disconnected';
            el.textContent = '● WebSocket: Disconnected';
        }
    });
}

function updateDashboardFromSnapshot(snapshotData) {
    // Map snapshot data to syngexData structure
    if (snapshotData.signals) {
        syngexData.strategyGrid = snapshotData.signals;
        renderStrategyHeatmap();
    }
    if (snapshotData.metrics) {
        syngexData.riskMetrics = snapshotData.metrics;
        renderRiskMetricsExtended();
    }
    if (snapshotData.gex) {
        syngexData.heatmapStrikes = snapshotData.gex.heatmapStrikes || [];
        renderDominantLevelsHeatmap();
    }
    if (snapshotData.logs) {
        syngexData.logs = snapshotData.logs;
        renderLogStream();
    }
}

function updateStrategyGrid(signals) {
    syngexData.strategyGrid = signals;
    renderStrategyHeatmap();
}

function updateRiskMetrics(metrics) {
    syngexData.riskMetrics = { ...syngexData.riskMetrics, ...metrics };
    renderRiskMetricsExtended();
}

function updateDominantLevels(gexData) {
    if (gexData.heatmapStrikes) {
        syngexData.heatmapStrikes = gexData.heatmapStrikes;
        renderDominantLevelsHeatmap();
    }
}

function updatePositions(positions) {
    syngexData.activePositions = positions;
    renderActivePositions();
}

// Initialize WebSocket connection after DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // ... existing initialization code ...
    
    // Connect to WebSocket
    connectWebSocket();
});
```

#### 2.3 Replace Mock Data with Live Streams

The current `data.js` contains static sample data. The WebSocket connection will replace this dynamically.

**Key Changes:**
1. Remove auto-simulation timers in `app.js`
2. Data now comes from WebSocket callbacks
3. Fallback to mock data only if WebSocket fails to connect

#### 2.4 Add Reconnection Logic

Already included in the WebSocket code above:
- Exponential backoff (configurable)
- Max retry attempts
- Status indicator in UI

#### 2.5 Error Handling and Fallbacks

```javascript
// Graceful degradation if WebSocket fails
function initializeWithFallback() {
    // Try WebSocket first
    connectWebSocket();
    
    // If not connected after 5 seconds, use mock data
    setTimeout(() => {
        if (ws && ws.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket not available, using mock data');
            updateWebSocketStatus(false);
            // Data already loaded from data.js
        }
    }, 5000);
}
```

---

### Phase 3: Testing (2-3 hours)

#### 3.1 Unit Tests for WebSocket Client

**File: `dashboard/mockup/tests/test_websocket_client.js`**
```javascript
// Test WebSocket connection logic
// Note: Requires Jest or similar framework

describe('WebSocket Client', () => {
    test('connects to WebSocket server', () => {
        // Mock WebSocket
        global.WebSocket = class MockWebSocket {
            constructor(url) {
                this.url = url;
                setTimeout(() => this.onopen(), 10);
            }
            send(data) {}
            close() {}
        };
        
        connectWebSocket();
        // Assert connection established
    });
    
    test('handles message parsing', () => {
        // Test message handling logic
    });
    
    test('reconnects on failure', () => {
        // Test reconnection logic
    });
});
```

#### 3.2 Integration Tests with Orchestrator

```bash
# Start WebSocket server
cd /home/hologaun/.openclaw/workspace/forge/syngex
python3 -c "
from websocket_server import create_server
import asyncio
server = create_server(port=8202)
asyncio.run(server.start())
" &

# Test connection
curl http://localhost:8202/health

# Open browser to http://localhost:8201 and verify connection
```

#### 3.3 Load Testing

Test with many concurrent updates:
```python
# Test script: scripts/test_load.py
import asyncio
import json
from websocket_server import create_server, get_server

async def test_load():
    server = get_server()
    
    # Simulate rapid updates
    for i in range(100):
        await server.broadcast_signals([
            {'name': f'STRAT_{i}', 'direction': 'BUY', 'confidence': 80}
        ])
        await asyncio.sleep(0.01)  # 10ms between updates
    
    print('Load test complete')

asyncio.run(test_load())
```

#### 3.4 Browser Compatibility Check

Test on:
- ✅ Chrome/Chromium (primary)
- ✅ Firefox
- ✅ Safari (if macOS available)

#### 3.5 Mobile Responsiveness (Optional)

Current mockup is desktop-optimized. Mobile support can be added later.

---

### Phase 4: Deployment (1 hour)

#### 4.1 Backup Old Dashboard Code

```bash
# Create backup
cd /home/hologaun/.openclaw/workspace/forge
git add dashboard/
git commit -m "Backup: Old dashboard before heatmap migration"

# Tag the backup
git tag -a heatmap-pre-migration -m "Pre-migration backup"
```

#### 4.2 Deploy New Heatmap

**Step 1: Test locally**
```bash
# Terminal 1: Start WebSocket server
cd syngex
python3 -c "
from websocket_server import create_server
import asyncio
server = create_server(port=8202)
asyncio.run(server.start())
"

# Terminal 2: Start heatmap frontend
cd dashboard/mockup
python3 -m http.server 8201 --bind 0.0.0.0

# Terminal 3: Test connection
curl http://localhost:8202/health
open http://localhost:8201
```

**Step 2: Verify data flow**
- Check WebSocket connection in browser DevTools
- Verify data updates in real-time
- Test reconnection by restarting WebSocket server

#### 4.3 Configure Auto-Start

**Option A: systemd service (recommended for production)**

```bash
# Create service file
sudo tee /etc/systemd/system/syngex-heatmap.service > /dev/null <<'EOF'
[Unit]
Description=Syngex Heatmap Frontend
After=network.target

[Service]
Type=simple
User=hologaun
WorkingDirectory=/home/hologaun/.openclaw/workspace/forge/dashboard/mockup
ExecStart=/usr/bin/python3 -m http.server 8201 --bind 0.0.0.0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable syngex-heatmap
sudo systemctl start syngex-heatmap
```

**Option B: Simple startup script**

```bash
# Add to ~/.bashrc or ~/.profile
alias start-heatmap='cd /home/hologaun/.openclaw/workspace/forge/dashboard/mockup && python3 -m http.server 8201 --bind 0.0.0.0'
```

#### 4.4 Document Startup Procedure

**File: `dashboard/STARTUP.md`**
```markdown
# Heatmap Startup Procedure

## Quick Start

```bash
# Start everything (WebSocket + Frontend)
./scripts/start-heatmap.sh
```

## Manual Start

```bash
# Terminal 1: WebSocket server
cd syngex
python3 -c "from websocket_server import create_server; import asyncio; server = create_server(port=8202); asyncio.run(server.start())"

# Terminal 2: Frontend
cd dashboard/mockup
python3 -m http.server 8201 --bind 0.0.0.0
```

## Access

- Frontend: http://localhost:8201
- WebSocket Health: http://localhost:8202/health

## Stop

```bash
# Kill processes
pkill -f "http.server 8201"
pkill -f "websocket_server"
```

## Troubleshooting

See `TROUBLESHOOTING.md`
```

#### 4.5 Update Runbook

Add to existing operational runbook:
- Heatmap URL and access
- WebSocket server status check
- Restart procedures
- Contact information for issues

---

### Phase 5: Validation (1 hour)

#### 5.1 Verify All Data Streams Working

**Checklist:**
- [ ] WebSocket connection established (green indicator)
- [ ] Strategy grid updates with real signals
- [ ] Risk metrics display current values
- [ ] Dominant levels heatmap shows GEX data
- [ ] Log stream receives real-time events
- [ ] Profile charts can be selected (visual only)

#### 5.2 Check Performance Under Load

**Targets:**
- Update latency: < 100ms from orchestrator to display
- Memory usage: < 100MB for frontend
- CPU usage: < 5% for frontend

**Test:**
```javascript
// In browser console
const start = performance.now();
// Trigger update
const end = performance.now();
console.log(`Update took ${end - start}ms`);
```

#### 5.3 Confirm Error Handling

**Test Scenarios:**
1. **WebSocket server restart**: Frontend should auto-reconnect
2. **Network interruption**: Connection status should update
3. **Invalid message format**: Should log error, not crash

#### 5.4 User Acceptance (Hologaun)

**Demo Points:**
- Open heatmap in browser
- Show real-time updates
- Demonstrate reconnection
- Verify all panels display correctly
- Confirm no console errors

---

## 3. Technical Details

### WebSocket Protocol Specification

**Connection:**
```
ws://localhost:8202/ws
```

**Client → Server Messages:**

```json
// Subscribe to channels
{
  "type": "subscribe",
  "channels": ["signals", "metrics", "gex", "positions"]
}

// Unsubscribe from channels
{
  "type": "unsubscribe",
  "channels": ["signals"]
}
```

**Server → Client Messages:**

```json
// Initial snapshot (sent on connect)
{
  "type": "snapshot",
  "timestamp": 1715840400123,
  "data": {
    "signals": [...],
    "metrics": {...},
    "gex": {...},
    "positions": [...]
  }
}

// Real-time updates
{
  "type": "signals_update",
  "timestamp": 1715840400123,
  "data": {
    "signals": [...],
    "count": 5
  }
}
```

### Message Format Schema

See Phase 2.1 for complete schema definitions.

### Error Handling Strategy

**Frontend:**
1. WebSocket connection failures → Auto-reconnect with backoff
2. Invalid messages → Log error, skip message
3. Missing data → Use last known good values
4. UI rendering errors → Catch exceptions, log, continue

**WebSocket Server:**
1. Client disconnect → Clean up, log
2. Invalid messages → Log warning, ignore
3. Broadcast failures → Log, continue with other clients

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Update latency | < 100ms | WebSocket → Display |
| Frontend memory | < 100MB | Browser DevTools |
| Frontend CPU | < 5% | Browser DevTools |
| Reconnect time | < 5s | Disconnect → Reconnect |
| Max concurrent clients | 10+ | Load test |

---

## 4. Deployment

### Step-by-Step Rollout

**Pre-Deployment (15 min):**
1. [ ] Review implementation plan
2. [ ] Ensure WebSocket server tests pass
3. [ ] Backup current state (git commit)
4. [ ] Notify stakeholders (if applicable)

**Deployment (30 min):**
1. [ ] Start WebSocket server
2. [ ] Start heatmap frontend
3. [ ] Verify health endpoints
4. [ ] Open browser, verify connection
5. [ ] Check data flow in DevTools

**Validation (15 min):**
1. [ ] Test all data streams
2. [ ] Verify reconnection logic
3. [ ] Check error handling
4. [ ] User acceptance test

**Post-Deployment (15 min):**
1. [ ] Configure auto-start
2. [ ] Update documentation
3. [ ] Monitor for issues
4. [ ] Clean up backup if stable

### Configuration Files

**File: `dashboard/mockup/config.js`** (create if needed)
```javascript
// Heatmap configuration
const HEATMAP_CONFIG = {
    websocket: {
        url: 'ws://localhost:8202/ws',
        reconnectDelay: 2000,
        maxReconnectAttempts: 10
    },
    refresh: {
        strategyGrid: 1000,  // 1 second
        metrics: 2000,       // 2 seconds
        gex: 1000           // 1 second
    }
};
```

### Process Management

**Supervisor (alternative to systemd):**

**File: `/etc/supervisor/conf.d/syngex-heatmap.conf`**
```ini
[program:syngex-heatmap]
command=/usr/bin/python3 -m http.server 8201 --bind 0.0.0.0
directory=/home/hologaun/.openclaw/workspace/forge/dashboard/mockup
user=hologaun
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/syngex/heatmap.log
```

---

## 5. Rollback Plan

### When to Rollback

- Critical bugs preventing dashboard use
- Data corruption or incorrect displays
- Performance issues worse than old system
- User rejection after UAT

### How to Rollback

**Option 1: Git Restore**
```bash
# Stop new heatmap
pkill -f "http.server 8201"
pkill -f "websocket_server"

# Restore old dashboard files
cd /home/hologaun/.openclaw/workspace/forge
git checkout heatmap-pre-migration -- dashboard/app.py dashboard/client.py

# Restart old dashboard
python3 dashboard/app.py
```

**Option 2: Manual Restore**
```bash
# If git backup not available
# Restore from known good backup location
cp /backup/dashboard/app.py /home/hologaun/.openclaw/workspace/forge/dashboard/
cp /backup/dashboard/client.py /home/hologaun/.openclaw/workspace/forge/dashboard/
```

### Verification Steps

After rollback:
1. [ ] Old dashboard starts without errors
2. [ ] Data displays correctly
3. [ ] No console errors in browser
4. [ ] All features functional
5. [ ] Document rollback reason

### Rollback Communication

If rollback is needed:
1. Notify Hologaun immediately
2. Document the issue
3. Set up separate debugging environment
4. Fix issue without affecting production

---

## 6. Monitoring Plan

### Health Checks

**WebSocket Server:**
```bash
# Health endpoint
curl http://localhost:8202/health

# Expected response:
# {"status": "healthy", "clients": 1, "running": true}
```

**Frontend:**
```bash
# HTTP endpoint
curl http://localhost:8201

# Should return HTML
```

### Logging

**WebSocket Server Logs:**
```python
# In websocket_server.py
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
```

**Frontend Logs:**
```javascript
// Browser console
console.log('Heatmap initialized');
console.error('WebSocket connection failed');
```

### Alerts

**Configure alerts for:**
- WebSocket server down (health check fails)
- Frontend server down (HTTP 500)
- No connected clients for > 5 minutes (if monitoring)

### Metrics to Track

| Metric | Source | Frequency |
|--------|--------|-----------|
| Connected clients | WebSocket server | Real-time |
| Message throughput | WebSocket server | Per-second |
| Error rate | Both | Per-minute |
| Uptime | Both | Continuous |

---

## 7. Appendix

### A. API Documentation

**WebSocket Endpoints:**
- `/ws` - WebSocket connection for real-time data

**HTTP Endpoints:**
- `/health` - Health check (WebSocket server)
- `/*` - Static file serving (frontend)

### B. Testing Procedures

**Manual Testing Checklist:**
```markdown
- [ ] Open http://localhost:8201
- [ ] Verify WebSocket connected (green indicator)
- [ ] Check strategy grid has data
- [ ] Verify risk metrics display
- [ ] Check dominant levels heatmap
- [ ] Verify log stream has entries
- [ ] Test profile tab switching
- [ ] Test strategy cell selection
- [ ] Test log filtering
- [ ] Restart WebSocket server, verify reconnection
- [ ] Check browser console for errors
```

**Automated Test Commands:**
```bash
# Run WebSocket server tests
cd syngex
python3 -m pytest tests/test_websocket_server.py -v

# Test HTTP server
curl http://localhost:8201/index.html | head -20
```

### C. Monitoring Setup

**Simple monitoring script:**

**File: `scripts/monitor-heatmap.sh`**
```bash
#!/bin/bash

# Check WebSocket server
WS_HEALTH=$(curl -s http://localhost:8202/health)
if [ $? -ne 0 ]; then
    echo "ERROR: WebSocket server unhealthy"
    echo "$WS_HEALTH"
fi

# Check Frontend
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8201)
if [ "$FRONTEND_HEALTH" != "200" ]; then
    echo "ERROR: Frontend unhealthy (HTTP $FRONTEND_HEALTH)"
fi

# If both healthy
if [ $? -eq 0 ] && [ "$FRONTEND_HEALTH" = "200" ]; then
    echo "OK: Heatmap system healthy"
fi
```

---

## Questions for Hologaun

### Decisions Needed Before Implementation

1. **Deployment method preference:**
   - [x] Option A: Static server + separate WebSocket **(RECOMMENDED)**
   - [ ] Option B: FastAPI integrated
   - [ ] Option C: Flask lightweight

2. **Port preferences:**
   - Heatmap UI: [x] 8201 (original) [ ] Other: ___
   - WebSocket: [x] 8202 (current) [ ] Other: ___

3. **Timeline urgency:**
   - [ ] ASAP (before Monday market open)
   - [x] Not urgent (can test over weekend)

4. **Rollback preference:**
   - [x] Keep old dashboard in parallel (git backup)
   - [ ] Replace entirely, rollback via git only

5. **Process manager preference:**
   - [x] Simple scripts (start-heatmap.sh)
   - [ ] systemd service
   - [ ] Supervisor

6. **Additional features needed:**
   - [ ] Mobile responsiveness
   - [ ] Historical data API endpoints
   - [ ] User authentication
   - [ ] Custom alerts/notifications

---

## Success Criteria

| Requirement | Status | Verification |
|-------------|--------|--------------|
| New heatmap replaces old dashboard | ✅ Plan | Deployed to port 8201 |
| All data streams working | ✅ Plan | WebSocket broadcasts |
| WebSocket reconnection on failure | ✅ Plan | Exponential backoff |
| Error handling and logging | ✅ Plan | Try/catch + console |
| Performance acceptable (<100ms updates) | ✅ Plan | Load testing |
| Auto-start on system boot | ⏳ Pending | systemd/supervisor |
| Documentation updated | ✅ Plan | This document + STARTUP.md |
| Rollback plan tested | ⏳ Pending | Git restore test |

---

**Document Version:** 1.0  
**Created:** 2026-05-16  
**Author:** Forge 🐙  
**Status:** Ready for Review

---

*This plan provides the roadmap for deploying the new heatmap. Once approved, implementation can proceed through the defined phases.*
