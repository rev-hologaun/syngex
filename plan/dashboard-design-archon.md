# Syngex Live Metrics Dashboard - Design Plan

**Author:** Archon 🕸️  
**Date:** 2026-05-20  
**Goal:** Second-by-second debug visibility into strategy calculations

---

## Overview

A tile-based real-time dashboard that displays live strategy metrics with calculation-by-calculation transparency. Each strategy gets its own tile, showing every intermediate calculation and confidence score, updating at 1Hz.

---

## Architecture

### Data Flow

```
Strategy Engine → Metrics Collector → WebSocket Stream → Dashboard Frontend
                        ↓
                 Redis/PubSub (optional cache layer)
```

### Components

1. **Metrics Collector (Backend)**
   - Hooks into existing strategy calculation pipeline
   - Serializes each calculation step with timestamp
   - Emits via WebSocket to connected dashboard clients
   - Optional: Redis cache for last-N seconds of history

2. **WebSocket Server**
   - Push-based updates at 1Hz (configurable)
   - Topic-based subscriptions (per-strategy or all)
   - Handles multiple concurrent dashboard clients

3. **Dashboard Frontend**
   - Tile-based grid layout (responsive)
   - Real-time DOM updates (no page refresh)
   - Collapse/expand tiles
   - Color-coded confidence indicators
   - Pause/resume streaming
   - Export snapshot functionality

---

## Tile Design

### Visual Layout (per tile)

```
┌─────────────────────────────────────────┐
│ STRATEGY_NAME              [🟢 LIVE]    │
├─────────────────────────────────────────┤
│ calc_id: 12345                          │
│   input: price=152.34, volume=45000     │
│   op: moving_average(20)                │
│   result: 151.89                        │
│   confidence: 0.87 ████████░░           │
├─────────────────────────────────────────┤
│ calc_id: 12346                          │
│   input: rsi=67.2, macd=0.34            │
│   op: momentum_signal()                 │
│   result: BUY                           │
│   confidence: 0.92 ██████████           │
├─────────────────────────────────────────┤
│ [Last update: 08:01:23.456]             │
└─────────────────────────────────────────┘
```

### Tile States

- **🟢 LIVE** - Actively streaming
- **🟡 PAUSED** - Streaming paused by user
- **🔴 STALE** - No updates >5 seconds
- **⚫ OFFLINE** - Strategy not running

---

## Technical Specifications

### Backend (Python)

```python
# Metrics collector interface
class StrategyMetricsCollector:
    def emit_calculation(self, strategy_id: str, calc_data: dict):
        """
        calc_data = {
            "calc_id": "unique_id",
            "timestamp": "ISO8601",
            "input": {...},
            "operation": "function_name",
            "result": value,
            "confidence": 0.0-1.0,
            "metadata": {...}
        }
        """
        pass

# WebSocket handler
class MetricsWebSocketHandler:
    async def broadcast(self, strategy_id: str, payload: dict):
        # Push to all subscribed dashboard clients
        pass
```

### Frontend (TypeScript/React or vanilla JS)

- **Framework:** React (for component reusability) or vanilla JS (lighter)
- **State Management:** Minimal - just latest calc per strategy
- **Rendering:** RequestAnimationFrame for smooth updates
- **Styling:** CSS Grid for tile layout, flexbox inside tiles

### Data Schema

```json
{
  "strategy_id": "mean_reversion_v2",
  "calculations": [
    {
      "calc_id": "calc_1779288883_001",
      "timestamp": "2026-05-20T15:01:23.456Z",
      "input": {
        "price": 152.34,
        "volume": 45000,
        "sma_20": 151.89
      },
      "operation": "price_deviation",
      "result": 0.00296,
      "confidence": 0.87,
      "confidence_label": "HIGH"
    }
  ],
  "status": "LIVE",
  "last_update": "2026-05-20T15:01:23.456Z"
}
```

---

## Implementation Phases

### Phase 1: Backend Metrics Pipeline (Forge)
- [ ] Define metrics collector interface
- [ ] Hook into existing strategy calculation flow
- [ ] Implement WebSocket server
- [ ] Add Redis cache layer (optional, for history)

### Phase 2: Frontend Dashboard (Forge)
- [ ] Create tile component
- [ ] Implement WebSocket client
- [ ] Build responsive grid layout
- [ ] Add confidence visualization (progress bars)
- [ ] Implement pause/resume controls

### Phase 3: Integration & Polish (Archon + Forge)
- [ ] Connect to existing strategies
- [ ] Performance testing (1Hz updates with multiple strategies)
- [ ] Add export/snapshot feature
- [ ] Color scheme refinement
- [ ] Mobile responsiveness check

---

## Key Design Decisions

1. **Push vs Pull:** WebSocket push (server → client) for real-time updates
2. **Update Frequency:** 1Hz default (configurable per strategy)
3. **History:** Last 60 seconds in memory, optional Redis for longer
4. **Performance:** Virtual DOM updates only for changed tiles
5. **Fallback:** If WebSocket fails, auto-reconnect with exponential backoff

---

## Questions for Hologaun

1. **Existing Heatmap:** Should this integrate with or replace the current heatmap?
2. **Strategy List:** How do we dynamically discover active strategies?
3. **Data Retention:** How long should we keep calculation history?
4. **Access Control:** Any authentication needed for the dashboard?
5. **Deployment:** Local-only or accessible from other machines?

---

## File Structure Proposal

```
~/projects/syngex/
├── dashboard/
│   ├── backend/
│   │   ├── metrics_collector.py
│   │   ├── websocket_server.py
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── index.html
│   │   ├── styles.css
│   │   ├── dashboard.js
│   │   └── components/
│   │       ├── Tile.js
│   │       ├── ConfidenceBar.js
│   │       └── Grid.js
│   └── README.md
└── plan/
    └── dashboard-design-archon.md (this file)
```

---

Ready to start implementation when you give the green light. I'll delegate the coding to Forge in small batches as per our workflow. 🕸️
