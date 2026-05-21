# Strategy Live Metrics Dashboard - Design Plan

**Author:** Forge 🐙
**Date:** 2026-05-20
**Target:** `~/projects/syngex/`

---

## 🎯 Objective

Build a real-time tile-based dashboard that provides second-by-second visibility into strategy calculations, including confidence scores, for debug and monitoring purposes.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGY ENGINE                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Strategy │  │ Strategy │  │ Strategy │  │ Strategy │        │
│  │    A     │  │    B     │  │    C     │  │    D     │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │                │
│       └─────────────┴─────────────┴─────────────┘                │
│                           │                                       │
│                    Metrics Emitter                                │
└───────────────────────────┼───────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  WebSocket     │
                    │  Server (Node) │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │   Dashboard    │
                    │   (React/Vue)  │
                    └────────────────┘
```

---

## 📊 Dashboard Layout

### Tile-Based Grid System

```
┌──────────────────────────────────────────────────────────────────┐
│  SYNGEX LIVE METRICS DASHBOARD                    [Auto-Refresh: ON] │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │  STRATEGY: GAMMA-SCAN │  │  STRATEGY: DELTA-HEDGE│            │
│  │  ─────────────────── │  │  ─────────────────── │            │
│  │  ✓ Price: $152.34    │  │  ✓ Price: $152.34    │            │
│  │  ✓ OI Change: +234   │  │  ✓ Delta: 0.67       │            │
│  │  ✓ Gamma: 0.023      │  │  ✓ Gamma: 0.023      │            │
│  │  ✓ IV Percentile: 78 │  │  ✓ Theta: -12.4      │            │
│  │  ✓ Confidence: 87%   │  │  ✓ Confidence: 72%   │            │
│  │                       │  │                       │            │
│  │  [Last update: 07:59:58]│  │  [Last update: 07:59:59]│        │
│  └──────────────────────┘  └──────────────────────┘             │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │  STRATEGY: VEGA-PLAY │  │  STRATEGY: VOL-ARBITR│            │
│  │  ─────────────────── │  │  ─────────────────── │            │
│  │  ✓ Vega: 45.2        │  │  ✓ Bid-Ask Spread: 0.12│           │
│  │  ✓ IV Skew: +3.4%    │  │  ✓ Implied Vol: 28%  │            │
│  │  ✓ Confidence: 91%   │  │  ✓ Historical Vol: 24%│            │
│  │  ✓ Signal Strength:  │  │  ✓ Confidence: 65%   │            │
│  │    ████████░░ 82%    │  │                       │            │
│  │  [Last update: 07:59:57]│  │  [Last update: 07:59:59]│        │
│  └──────────────────────┘  └──────────────────────┘             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### 1. Strategy Metrics Emitter (Python)

Each strategy must expose a metrics hook:

```python
# syngex/strategies/base_strategy.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any
import time

@dataclass
class MetricLine:
    name: str
    value: Any
    confidence: float  # 0.0 to 1.0
    timestamp: float

class StrategyMetricsEmitter:
    """Singleton for broadcasting strategy metrics to dashboard."""
    
    _instance = None
    _subscribers = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metrics_buffer = {}
        return cls._instance
    
    def subscribe(self, callback):
        self._subscribers.append(callback)
    
    def emit(self, strategy_name: str, metrics: list[MetricLine]):
        """Broadcast metrics to all connected dashboard clients."""
        payload = {
            "strategy": strategy_name,
            "metrics": [
                {"name": m.name, "value": m.value, "confidence": m.confidence}
                for m in metrics
            ],
            "timestamp": time.time()
        }
        for callback in self._subscribers:
            callback(payload)

class BaseStrategy(ABC):
    """Base class all strategies inherit from."""
    
    def __init__(self, name: str):
        self.name = name
        self.emitter = StrategyMetricsEmitter()
    
    @abstractmethod
    def calculate(self, market_data: Dict) -> Dict:
        """Return dict with 'metrics' key containing list of MetricLine objects."""
        pass
    
    def run(self, market_data: Dict):
        """Execute strategy and emit metrics."""
        result = self.calculate(market_data)
        
        # Emit metrics for dashboard
        metric_lines = [
            MetricLine(
                name=k,
                value=v.get('value'),
                confidence=v.get('confidence', 1.0),
                timestamp=time.time()
            )
            for k, v in result.get('metrics', {}).items()
        ]
        
        self.emitter.emit(self.name, metric_lines)
        return result
```

### 2. WebSocket Server (Node.js)

```javascript
// syngex/dashboard/server.js
const WebSocket = require('ws');
const http = require('http');

const server = http.createServer();
const wss = new WebSocket.Server({ server });

// Store connected clients
const clients = new Set();

// Strategy metrics cache (last known state)
const strategyMetrics = new Map();

wss.on('connection', (ws) => {
    clients.add(ws);
    console.log('Dashboard client connected');
    
    // Send current state immediately
    ws.send(JSON.stringify({
        type: 'initial_state',
        data: Object.fromEntries(strategyMetrics)
    }));
    
    ws.on('close', () => {
        clients.delete(ws);
    });
});

// Python -> Node bridge via HTTP POST (or use redis/pubsub)
const express = require('express');
const app = express();
app.use(express.json());

app.post('/metrics', (req, res) => {
    const { strategy, metrics, timestamp } = req.body;
    
    // Cache latest state
    strategyMetrics.set(strategy, { metrics, timestamp });
    
    // Broadcast to all dashboard clients
    const payload = JSON.stringify({
        type: 'update',
        data: { strategy, metrics, timestamp }
    });
    
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(payload);
        }
    });
    
    res.sendStatus(200);
});

server.listen(3001, () => {
    console.log('Metrics WebSocket server running on port 3001');
});
```

### 3. React Dashboard Component

```jsx
// syngex/dashboard/src/components/StrategyTile.jsx
import { useEffect, useState } from 'react';

export function StrategyTile({ strategyName, metrics, lastUpdate }) {
    const maxConfidence = Math.max(...metrics.map(m => m.confidence));
    
    return (
        <div className="strategy-tile">
            <div className="tile-header">
                <h3>STRATEGY: {strategyName.toUpperCase()}</h3>
                <span className={`confidence-badge confidence-${Math.round(maxConfidence * 100)}`}>
                    Max Confidence: {Math.round(maxConfidence * 100)}%
                </span>
            </div>
            
            <div className="metrics-list">
                {metrics.map((metric, idx) => (
                    <div key={idx} className="metric-row">
                        <span className="metric-name">✓ {metric.name}:</span>
                        <span className="metric-value">{formatValue(metric.value)}</span>
                        <span 
                            className="confidence-bar"
                            style={{ width: `${metric.confidence * 100}%` }}
                        />
                        <span className="confidence-text">
                            {Math.round(metric.confidence * 100)}%
                        </span>
                    </div>
                ))}
            </div>
            
            <div className="tile-footer">
                <small>[Last update: {formatTime(lastUpdate)}]</small>
            </div>
        </div>
    );
}

// syngex/dashboard/src/App.jsx
import { useEffect, useState } from 'react';
import { StrategyTile } from './components/StrategyTile';

function App() {
    const [strategies, setStrategies] = useState({});
    
    useEffect(() => {
        const ws = new WebSocket('ws://localhost:3001');
        
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            
            if (msg.type === 'initial_state') {
                setStrategies(msg.data);
            } else if (msg.type === 'update') {
                setStrategies(prev => ({
                    ...prev,
                    [msg.data.strategy]: {
                        metrics: msg.data.metrics,
                        lastUpdate: msg.data.timestamp
                    }
                }));
            }
        };
        
        return () => ws.close();
    }, []);
    
    return (
        <div className="dashboard">
            <h1>SYNGEX LIVE METRICS DASHBOARD</h1>
            <div className="tile-grid">
                {Object.entries(strategies).map(([name, data]) => (
                    <StrategyTile
                        key={name}
                        strategyName={name}
                        metrics={data.metrics}
                        lastUpdate={data.lastUpdate}
                    />
                ))}
            </div>
        </div>
    );
}
```

---

## 📁 File Structure

```
~/projects/syngex/
├── plan/
│   └── forge-dashboard-design.md          # This file
├── src/
│   ├── strategies/
│   │   ├── base_strategy.py              # Base class with metrics emitter
│   │   ├── gamma_scan.py                 # Example strategy implementation
│   │   └── ...
│   └── metrics/
│       └── emitter.py                     # Standalone metrics emitter module
├── dashboard/
│   ├── server.js                          # WebSocket server
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       └── components/
│           └── StrategyTile.jsx
└── README.md
```

---

## 🔄 Data Flow

1. **Strategy Execution** (Python, every ~100-500ms)
   - Strategy calculates metrics
   - Emits via `StrategyMetricsEmitter.emit()`

2. **Metrics Bridge** (Python → Node)
   - Option A: HTTP POST to `/metrics` endpoint
   - Option B: Redis pub/sub for scalability
   - Option C: Direct WebSocket from Python (simpler for MVP)

3. **Dashboard Broadcast** (Node WebSocket)
   - Receives metrics update
   - Broadcasts to all connected clients
   - Clients update UI instantly

4. **UI Refresh** (React)
   - Tile updates with new metrics
   - Confidence bars animate
   - Timestamp refreshes

---

## 🎨 Visual Design Notes

### Color Coding by Confidence
- **90-100%**: Green (`#22c55e`)
- **70-89%**: Yellow/Orange (`#f59e0b`)
- **50-69%**: Amber (`#fb923c`)
- **<50%**: Red (`#ef4444`)

### Tile States
- **Active**: Bright border, pulsing update indicator
- **Stale** (>5s no update): Dimmed, gray border
- **Error**: Red border, error message displayed

### Layout Options
- **Grid**: Auto-fit columns based on screen width
- **List**: Vertical stack for mobile
- **Focus Mode**: Expand single tile to full screen

---

## ⚡ Performance Considerations

1. **Update Rate**: 1 second max (throttle if strategies push faster)
2. **Metric Limit**: Cap at 50 metrics per strategy to prevent UI lag
3. **Connection Pool**: Single WebSocket per dashboard instance
4. **Memory**: Prune old metric history after N updates (configurable)

---

## 🧪 Debug Features

- **Pause/Resume**: Toggle auto-refresh
- **Export**: Download current metrics snapshot (JSON/CSV)
- **Filter**: Show/hide strategies by confidence threshold
- **Timeline**: Historical view (last N minutes)

---

## 📋 Implementation Phases

### Phase 1: MVP (1-2 days)
- [ ] Base strategy metrics emitter in Python
- [ ] Simple HTTP endpoint for metrics ingestion
- [ ] Basic React dashboard with static tiles
- [ ] WebSocket connection for live updates

### Phase 2: Polish (1 day)
- [ ] Confidence-based color coding
- [ ] Auto-layout grid system
- [ ] Stale tile detection
- [ ] Last update timestamps

### Phase 3: Advanced (2-3 days)
- [ ] Historical timeline view
- [ ] Export functionality
- [ ] Strategy filtering/search
- [ ] Focus mode for single strategy
- [ ] Alert thresholds (confidence drops, etc.)

---

## 🚀 Next Steps

1. Confirm this design matches your vision
2. I'll start with Phase 1 implementation
3. We iterate based on what you see in the dashboard

Ready to build this when you give the green light. 🐙
