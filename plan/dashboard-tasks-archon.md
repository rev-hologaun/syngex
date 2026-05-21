# Dashboard Implementation Task Tracker

**Author:** Archon 🕸️  
**Date:** 2026-05-20  
**Status:** Phase 1 in progress

---

## Phase 1: Backend Core (FastAPI + Telemetry)

### Task 1.1: Create dashboard directory structure
- [x] Create `~/projects/syngex/dashboard/` directory
- [ ] Create `requirements.txt` with dependencies

**Status:** Ready to start

### Task 1.2: Write telemetry.py emitter class
- [ ] Create `TelemetryLine` dataclass
- [ ] Create `TelemetryEmitter` async class
- [ ] Implement `emit()` method with HTTP POST to dashboard
- [ ] Add silent fail (don't slow down strategy)

**Status:** Pending (waiting for 1.1)

### Task 1.3: Write server.py FastAPI backend
- [ ] Create FastAPI app
- [ ] Add `/metrics` HTTP POST endpoint
- [ ] Add `/ws` WebSocket endpoint
- [ ] Implement in-memory strategy_data storage
- [ ] Implement broadcast() to all connected clients
- [ ] Test with manual HTTP POST

**Status:** Pending (waiting for 1.2)

### Task 1.4: Test backend end-to-end
- [ ] Run `python server.py`
- [ ] Send test POST to `/metrics`
- [ ] Verify data stored in memory
- [ ] Check logs for errors

**Status:** Pending (waiting for 1.3)

---

## Phase 2: Frontend (Vanilla JS Dashboard)

### Task 2.1: Write index.html skeleton
- [ ] Create HTML structure with grid layout
- [ ] Add dark theme CSS
- [ ] Add tile state styles (live/stale/offline)
- [ ] Add confidence color classes

**Status:** Pending

### Task 2.2: Add WebSocket connection
- [ ] Connect to `ws://localhost:8000/ws`
- [ ] Handle `init` message (full state)
- [ ] Handle `update` message (single strategy)
- [ ] Render tiles dynamically

**Status:** Pending (waiting for 2.1)

### Task 2.3: Add tile rendering logic
- [ ] Create `renderTile()` function
- [ ] Implement confidence color coding
- [ ] Add timestamp display
- [ ] Replace existing tiles on update

**Status:** Pending (waiting for 2.2)

### Task 2.4: Test frontend
- [ ] Open `index.html` in browser
- [ ] Verify WebSocket connects
- [ ] Send test metrics from backend
- [ ] Check tile updates in real-time

**Status:** Pending (waiting for 2.3)

---

## Phase 3: Integration (Hook into Existing Strategies)

### Task 3.1: Add telemetry import to base strategy
- [ ] Import `TelemetryEmitter` in strategy base class
- [ ] Add `emit_telemetry()` helper method
- [ ] Document usage for other strategies

**Status:** Pending

### Task 3.2: Instrument first strategy (gamma_scan)
- [ ] Add telemetry hooks to calculation steps
- [ ] Create `TelemetryLine` objects for each calc
- [ ] Call `emit()` after calculations
- [ ] Test end-to-end flow

**Status:** Pending (waiting for 3.1)

### Task 3.3: Test with live strategy data
- [ ] Run strategy with dashboard open
- [ ] Verify tiles update at ~1Hz
- [ ] Check confidence colors render correctly
- [ ] Confirm no performance impact on strategy

**Status:** Pending (waiting for 3.2)

### Task 3.4: Add stale detection
- [ ] Track last update timestamp per strategy
- [ ] Mark tile as STALE if >5s no update
- [ ] Add visual indicator (red border, pulse)

**Status:** Pending (waiting for 3.3)

---

## Phase 4: Polish & Features

### Task 4.1: Add pause/resume toggle
- [ ] Add global pause button
- [ ] Store pause state in localStorage
- [ ] Prevent UI updates when paused

**Status:** Pending

### Task 4.2: Add export functionality
- [ ] Add "Export Snapshot" button
- [ ] Download current state as JSON/CSV
- [ ] Include timestamp in filename

**Status:** Pending (waiting for 4.1)

### Task 4.3: Add strategy filtering
- [ ] Add search/filter input
- [ ] Hide strategies below confidence threshold
- [ ] Toggle strategy visibility

**Status:** Pending (waiting for 4.2)

### Task 4.4: Performance tuning
- [ ] Profile update rate with 10+ strategies
- [ ] Optimize DOM updates if needed
- [ ] Add metric limit per tile (cap at 50)

**Status:** Pending (waiting for 4.3)

---

## Notes

- **Work in small batches:** Each task should be <50 lines of code
- **Test after each task:** Don't batch multiple tasks together
- **cwd:** Always use `cwd: "~/projects/syngex/"` when spawning Forge
- **Review:** I'll review each task before moving to the next

---

## Progress Log

| Date | Task | Status | Notes |
|------|------|--------|-------|
| 2026-05-20 | 1.1 | IN PROGRESS | Starting now |
