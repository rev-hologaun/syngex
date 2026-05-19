# Syngex Modularization Plan

## 🎯 Objective
Transform monolithic `main.py` (500+ lines) and tightly-coupled components into a clean, modular architecture that follows separation of concerns and enables independent testing, scaling, and maintenance.

---

## 📊 Current State (v3.01)

### Problems
1. **Monolithic Orchestrator:** `main.py` has 1400+ lines mixing:
   - Lifecycle management (init, connect, run, shutdown)
   - Signal processing
   - Strategy evaluation
   - Dashboard/heatmap subprocess spawning
   - Config hot-reload
   - GEX state export

2. **Tight Coupling:**
   - `SyngexOrchestrator` directly instantiates all components
   - Circular dependency: `Dashboard(orchestrator=self)`
   - Global state accessed across modules

3. **Testing Difficulties:**
   - No dependency injection
   - Cannot test components in isolation
   - Integration tests required for everything

4. **Scalability Issues:**
   - Adding new features requires touching core orchestrator
   - Cannot scale components independently (e.g., separate GEX service)

---

## 🏗️ Target Architecture

```
syngex/
├── core/
│   ├── __init__.py
│   ├── orchestrator.py          # Lifecycle management only
│   ├── config_loader.py         # Config parsing & hot-reload
│   └── event_bus.py             # Pub/sub for component communication
│
├── data/
│   ├── __init__.py
│   ├── ingestor.py              # TradeStation client (quotes/options)
│   ├── token_manager.py         # Token refresh (moved from ingestor/)
│   └── stream_processor.py      # SSE stream handling
│
├── engine/
│   ├── __init__.py
│   ├── gex_calculator.py        # GEX aggregation & gamma ladder
│   ├── rolling_window.py        # Time/count-based windows (unchanged)
│   └── gamma_profile.py         # Flip detection, wall calculation
│
├── strategies/
│   ├── __init__.py
│   ├── engine.py                # Strategy evaluation & conflict resolution
│   ├── signal.py                # Signal data model (unchanged)
│   ├── signal_tracker.py        # Open/resolved signal tracking (unchanged)
│   ├── filters/
│   │   ├── __init__.py
│   │   └── net_gamma_filter.py  # Regime filtering
│   └── layer[1-4]/              # Strategy implementations (unchanged)
│
├── services/
│   ├── __init__.py
│   ├── dashboard_service.py     # Dashboard subprocess management
│   ├── heatmap_service.py       # Heatmap Flask app management
│   └── state_exporter.py        # GEX state JSON export
│
├── config/
│   ├── __init__.py
│   ├── parameters.py            # Constants (unchanged)
│   ├── strategies.yaml          # Strategy configuration (unchanged)
│   ├── heatmap.yaml             # Heatmap configuration (unchanged)
│   └── logging_config.py        # Logging setup (unchanged)
│
├── api/
│   ├── __init__.py
│   └── health_endpoint.py       # /health endpoint (moved from app_heatmap.py)
│
├── tests/                       # Unit tests for each module
├── integration_tests/           # Integration tests
└── main.py                      # Entry point (~100 lines, minimal)
```

---

## 📋 Implementation Phases

### Phase 1: Extract Lifecycle Management
**Goal:** Isolate orchestrator lifecycle from business logic

**Tasks:**
1. Create `core/orchestrator.py` with:
   - `SyngexOrchestrator` class (lifecycle methods only)
   - `initialize()`, `connect()`, `run()`, `shutdown()`
   - Component registration interface

2. Move subprocess management to `services/dashboard_service.py` and `services/heatmap_service.py`

3. Simplify `main.py` to:
   ```python
   def main():
       args = parse_args()
       orchestrator = SyngexOrchestrator(args.symbol)
       asyncio.run(orchestrator.run())
   ```

**Deliverables:**
- `core/orchestrator.py` (300 lines)
- `services/dashboard_service.py`
- `services/heatmap_service.py`
- `main.py` reduced to <150 lines

---

### Phase 2: Extract Config & Event Bus
**Goal:** Decouple configuration and inter-component communication

**Tasks:**
1. Create `core/config_loader.py`:
   - Load YAML configs
   - Hot-reload watching
   - Config change events

2. Create `core/event_bus.py`:
   - Pub/sub pattern for component communication
   - Events: `DATA_UPDATE`, `SIGNAL_CREATED`, `STRATEGY_EVALUATED`, etc.

3. Update components to use event bus instead of direct calls

**Deliverables:**
- `core/config_loader.py`
- `core/event_bus.py`
- Updated `main.py` and `orchestrator.py` to use event bus

---

### Phase 3: Service Layer
**Goal:** Move dashboard, heatmap, and state export to independent services

**Tasks:**
1. `services/dashboard_service.py`:
   - Manage Streamlit subprocess
   - Health monitoring
   - Graceful shutdown

2. `services/heatmap_service.py`:
   - Manage Flask subprocess
   - Port management
   - Health endpoint

3. `services/state_exporter.py`:
   - Periodic GEX state export
   - JSON file writing
   - Error handling

**Deliverables:**
- All three service modules
- Updated orchestrator to use services

---

### Phase 4: Data Layer Cleanup
**Goal:** Separate data ingestion from business logic

**Tasks:**
1. Move `token_manager.py` from `ingestor/` to `data/`
2. Create `data/ingestor.py` to wrap TradeStation client
3. Create `data/stream_processor.py` for SSE handling
4. Remove `ingestor/` directory (replaced by `data/`)

**Deliverables:**
- `data/ingestor.py`
- `data/stream_processor.py`
- `data/token_manager.py`
- Cleanup old `ingestor/` directory

---

### Phase 5: Engine Layer
**Goal:** Ensure GEX calculation is pure and testable

**Tasks:**
1. Verify `engine/gex_calculator.py` has no side effects
2. Extract gamma flip/wall logic to `engine/gamma_profile.py`
3. Add dependency injection for calculator

**Deliverables:**
- `engine/gamma_profile.py`
- Updated `engine/gex_calculator.py`
- Dependency injection in orchestrator

---

### Phase 6: API Layer
**Goal:** Separate health endpoint from heatmap app

**Tasks:**
1. Create `api/health_endpoint.py`:
   - Standalone health check service
   - Can run independently of heatmap

2. Update `app_heatmap.py` to use `api/health_endpoint.py`

**Deliverables:**
- `api/health_endpoint.py`
- Updated `app_heatmap.py`

---

### Phase 7: Testing Infrastructure
**Goal:** Enable independent component testing

**Tasks:**
1. Add `tests/core/` for orchestrator, config, event bus
2. Add `tests/data/` for ingestor, stream processor
3. Add `tests/engine/` for GEX calculator, rolling window
4. Add `tests/services/` for dashboard, heatmap, state exporter
5. Create test fixtures and mocks

**Deliverables:**
- Complete test suite
- CI/CD integration ready

---

## ⏱️ Timeline (Estimated)

| Phase | Duration | Dependency |
|-------|----------|------------|
| Phase 1 | 2-3 hours | None |
| Phase 2 | 2-3 hours | Phase 1 |
| Phase 3 | 2 hours | Phase 1 |
| Phase 4 | 1-2 hours | None |
| Phase 5 | 1 hour | Phase 2, 4 |
| Phase 6 | 30 min | Phase 3 |
| Phase 7 | 3-4 hours | Phase 1-6 |
| **Total** | **~15 hours** | |

---

## ✅ Success Criteria

1. **`main.py` < 150 lines** - Entry point only
2. **No circular dependencies** - Can import modules independently
3. **Component tests possible** - Each module can be tested in isolation
4. **Event-driven architecture** - Components communicate via event bus
5. **Service independence** - Dashboard/heatmap can run independently
6. **All tests pass** - 149 existing tests + new modularization tests

---

## 🚀 Rollback Plan

If issues arise during migration:
1. Keep original `main.py` as `main_legacy.py`
2. Gradually switch components one at a time
3. Maintain v3.01 tag as restore point
4. Can revert by checking out v3.01 tag

---

## 📝 Notes

- **Preserve all functionality:** No behavior changes during refactoring
- **Incremental rollout:** Each phase should pass tests before next phase
- **Backwards compatible:** API contracts remain the same
- **Documentation:** Update README with new structure

---

**Ready for Forge to begin Phase 1 implementation.**
