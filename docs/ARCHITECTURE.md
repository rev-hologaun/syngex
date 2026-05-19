# Syngex Architecture

## Overview

Syngex is a modular, event-driven trading pipeline that analyzes options market data to identify gamma-based trading signals. The architecture follows separation of concerns principles with clear component boundaries and dependency injection support.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Syngex Pipeline                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │   main.py    │───▶│  Container   │───▶│  Orchestrator        │  │
│  │  (Entry)     │    │  (DI)        │    │  (Lifecycle)         │  │
│  └──────────────┘    └──────────────┘    └──────────┬───────────┘  │
│                                                     │              │
│                          ┌──────────────────────────┼──────────┐   │
│                          │                          │          │   │
│          ┌───────────────▼────────┐  ┌─────────────▼──────┐   │   │
│          │   Config Loader        │  │   Event Bus        │   │   │
│          │   (YAML + Hot-reload)  │  │   (Pub/Sub)        │   │   │
│          └────────────────────────┘  └────────────────────┘   │   │
│                          │                          │          │   │
│          ┌───────────────┴────────┐  ┌─────────────┴──────┐   │   │
│          ▼                       ▼  ▼                    ▼   │   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Data Layer    │    │   Engine Layer  │    │ Service Layer│ │
│  │                 │    │                 │    │              │ │
│  │ - Ingestor      │    │ - GEX Calculator│    │ - Dashboard  │ │
│  │ - Stream Proc.  │    │ - Gamma Profile │    │ - Heatmap    │ │
│  │ - Token Manager │    │ - Strategy Eng. │    │ - State Exp. │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Core Layer

#### `core/orchestrator.py` - SyngexOrchestrator
**Purpose:** Lifecycle management and component coordination

**Responsibilities:**
- Initialize, connect, run, and shutdown lifecycle
- Component wiring and dependency resolution
- Config hot-reload coordination
- Error handling and graceful shutdown

**Not Responsible For:**
- Business logic (delegates to engines)
- Data processing (delegates to data layer)
- UI/Subprocess management (delegates to services)

#### `core/container.py` - SyngexContainer
**Purpose:** Dependency Injection Container

**Features:**
- Component registration and resolution
- Singleton and scoped lifetimes
- Automatic dependency injection
- Mock component support for testing

**Usage:**
```python
container = SyngexContainer()
container.register(GEXCalculator, singleton=True)
container.register(StrategyEngine, dependencies=['GEXCalculator'])
orchestrator = container.resolve(SyngexOrchestrator)
```

#### `core/config_loader.py` - ConfigLoader
**Purpose:** Configuration management with hot-reload

**Features:**
- YAML configuration parsing
- Type-safe configuration objects
- File watching for hot-reload
- Validation and error handling

**Configuration Structure:**
```yaml
global:
  symbol: "TSLA"
  port: 8200
  log_level: "INFO"
  min_confidence: 0.35

strategies:
  layer1:
    gamma_squeeze:
      enabled: true
      params:
        pin_atr_pct: 0.003
  layer2:
    delta_gamma_squeeze:
      enabled: true
      params:
        min_wall_gex: 500000

filter:
  net_gamma:
    enabled: true
    params:
      flip_buffer: 0.5
```

#### `core/events.py` - EventBus
**Purpose:** Pub/Sub event system for loose coupling

**Event Types:**
- `DATA_UPDATED` - Market data changes
- `SIGNAL_CREATED` - New trading signal
- `SIGNAL_RESOLVED` - Signal outcome determined
- `STRATEGY_EVALUATED` - Strategy evaluation complete
- `CONFIG_RELOADED` - Configuration changed

**Usage:**
```python
event_bus = EventBus()
event_bus.subscribe('SIGNAL_CREATED', handle_new_signal)
event_bus.publish('SIGNAL_CREATED', signal_data)
```

### Data Layer

#### `data/ingestor.py` - TradeStationClient
**Purpose:** TradeStation API client for market data

**Responsibilities:**
- WebSocket connection management
- Quote and option chain subscription
- Message parsing and validation
- Token refresh handling

#### `data/stream_processor.py` - StreamProcessor
**Purpose:** SSE stream processing and routing

**Responsibilities:**
- Stream connection management
- Message routing to callbacks
- Error handling and reconnection

#### `data/token_manager.py` - TokenManager
**Purpose:** TradeStation token lifecycle management

**Responsibilities:**
- Token acquisition and refresh
- Token caching
- Expiration monitoring

### Engine Layer

#### `engine/gex_calculator.py` - GEXCalculator
**Purpose:** Gamma exposure calculations

**Responsibilities:**
- Option chain aggregation
- GEX by strike calculation
- Net gamma and delta computation
- Gamma ladder generation

**Pure Functions:** No side effects, fully testable

#### `engine/gamma_profile.py` - GammaProfileEngine
**Purpose:** Gamma flip and wall detection

**Responsibilities:**
- Flip point identification
- Wall calculation
- Profile visualization data

#### `engine/strategy_engine.py` - StrategyEngine
**Purpose:** Strategy registration and evaluation

**Responsibilities:**
- Strategy lifecycle management
- Signal generation
- Conflict resolution
- Signal tracking

### Service Layer

#### `services/dashboard_service.py` - DashboardService
**Purpose:** Streamlit dashboard subprocess management

**Responsibilities:**
- Subprocess spawning and monitoring
- Health checking
- Graceful shutdown
- Port management

#### `services/heatmap_service.py` - HeatmapService
**Purpose:** Flask heatmap application management

**Responsibilities:**
- Flask app subprocess management
- API endpoint exposure
- Health monitoring

#### `services/state_exporter.py` - StateExporter
**Purpose:** GEX state export for external consumption

**Responsibilities:**
- Periodic state serialization
- JSON file writing
- Shared data file management

### Strategy Layer

#### Layer 1: Foundation Strategies
- `gamma_squeeze` - Gamma squeeze detection
- `gamma_wall_bounce` - Wall bounce patterns
- `magnet_accelerate` - Magnet effect acceleration
- `gamma_flip_breakout` - Flip point breakouts
- `gex_imbalance` - GEX divergence patterns
- `confluence_reversal` - Multi-factor reversals
- `vol_compression_range` - Volatility compression
- `gex_divergence` - GEX divergence signals

#### Layer 2: Advanced Strategies
- `delta_gamma_squeeze` - Delta-gamma combination
- `delta_volume_exhaustion` - Volume-based exhaustion
- `call_put_flow_asymmetry` - Flow imbalance
- `iv_gex_divergence` - IV vs GEX divergence
- `delta_iv_divergence` - Delta-IV divergence

#### Layer 3: Complex Patterns
- `gamma_volume_convergence` - Gamma-volume alignment
- `iv_band_breakout` - IV band breaks
- `strike_concentration` - Strike concentration analysis
- `theta_burn` - Time decay patterns

#### Full Data: Advanced Analytics
- `iv_skew_squeeze` - IV skew analysis
- `prob_weighted_magnet` - Probability-weighted magnets
- `prob_distribution_shift` - Distribution shifts
- `extrinsic_intrinsic_flow` - Extrinsic/intrinsic flow

## Data Flow

```
1. Market Data Ingestion
   ┌──────────────┐
   │ TradeStation │
   └──────┬───────┘
          │ WebSocket
          ▼
   ┌──────────────┐
   │  Ingestor    │
   └──────┬───────┘
          │ Parsed Messages
          ▼
   ┌──────────────┐
   │ Stream Proc. │
   └──────┬───────┘
          │ Route to callbacks
          ▼
   ┌──────────────┐
   │ Orchestrator │ (on_message callback)
   └──────┬───────┘
          │
          ├──────────────┬──────────────┐
          ▼              ▼              ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │   GEX        │ │ Rolling      │ │ Strategy     │
   │   Calculator │ │ Windows      │ │ Engine       │
   └──────┬───────┘ └──────────────┘ └──────┬───────┘
          │                                  │
          ▼                                  ▼
   ┌──────────────┐                  ┌──────────────┐
   │ Gamma        │                  │ Signal       │
   │ Profile      │                  │ Tracker      │
   └──────────────┘                  └──────┬───────┘
                                            │
                                            ▼
                                   ┌──────────────┐
                                   │   Event      │
                                   │   Bus        │
                                   └──────┬───────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │   Dashboard  │
                                   │   / Heatmap  │
                                   └──────────────┘
```

## Extension Points

### Adding New Strategies

1. Create strategy class in `strategies/layerX/`
2. Implement `evaluate()` method
3. Register in `strategies/engine.py` strategy map
4. Add configuration in `config/strategies.yaml`

```python
class MyNewStrategy(BaseStrategy):
    def evaluate(self, data: Dict[str, Any]) -> Optional[Signal]:
        # Your logic here
        if condition:
            return Signal(
                strategy_id="my_new_strategy",
                direction=Direction.LONG,
                confidence=0.75,
                metadata={"reason": "example"}
            )
```

### Adding New Event Types

1. Add to `EventType` enum in `core/events.py`
2. Create event class if needed
3. Publish from component
4. Subscribe in interested components

### Adding New Services

1. Create service class in `services/`
2. Implement lifecycle methods (start, stop, health)
3. Register in orchestrator
4. Add configuration if needed

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Use dependency injection for mocks
- Focus on business logic

### Integration Tests
- Test component interactions
- Use test containers for external services
- Verify end-to-end flows

### Performance Tests
- Benchmark GEX calculations
- Measure event processing throughput
- Identify bottlenecks

See `docs/TESTING.md` for detailed testing guide.

## Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Production                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐    ┌──────────────┐              │
│  │  Syngex      │    │  Dashboard   │              │
│  │  Pipeline    │───▶│  (Streamlit) │              │
│  │  (Main)      │    │  :8501       │              │
│  └──────┬───────┘    └──────────────┘              │
│         │                                           │
│         ▼                                           │
│  ┌──────────────┐    ┌──────────────┐              │
│  │  Heatmap     │    │  Log Files   │              │
│  │  (Flask)     │    │  /log/       │
│  │  :8200       │    │              │              │
│  └──────────────┘    └──────────────┘              │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Configuration Management

### Environment Variables
- `SYNGEX_SYMBOL` - Default ticker symbol
- `SYNGEX_PORT` - Default dashboard port
- `SYNGEX_LOG_LEVEL` - Logging level

### Config Files
- `config/strategies.yaml` - Strategy configuration
- `config/heatmap.yaml` - Heatmap settings
- `config/logging_config.py` - Logging setup

### Hot-Reload
- Config files watched for changes
- Automatic reload on modification
- No restart required for parameter changes

## Performance Considerations

### Optimization Strategies
1. **GEX Calculations:** Cached where possible
2. **Event Processing:** Async processing queue
3. **Data Structures:** Optimized for frequent updates
4. **I/O Operations:** Batched writes

### Monitoring
- Correlation IDs for tracing
- Structured JSON logging
- Performance metrics exported

## Security Considerations

- API tokens stored securely
- No sensitive data in logs
- Port binding to localhost only
- Input validation on all inputs
