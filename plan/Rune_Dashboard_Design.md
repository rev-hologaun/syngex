# Rune's Dashboard Design: The Fractal Observer 🐉

## Vision
To provide a high-fidelity, second-by-second window into the "mind" of our trading strategies. Instead of looking at aggregated results, we are looking at the raw, flowing thought processes of the agents in real-time. This is not just a monitor; it is a debug-grade telemetry stream.

## Architecture: The "Tile-Stream" Model

### 1. The Dashboard Interface (Frontend)
- **Layout**: A responsive, dark-themed grid (CSS Grid/Flexbox) of "Strategy Tiles."
- **Tile Component**:
    - **Header**: Strategy Name (e.g., `GEX-Alpha-01`), Status (Running/Paused), and a "Heartbeat" indicator (flashing green when data is flowing).
    - **Body**: A high-speed, scrolling text stream. Each line represents a single calculation step.
    - **Footer**: A prominent, color-coded **Confidence Score** (e.g., 0.85 $\rightarrow$ bright emerald; 0.30 $\rightarrow$ warning amber; 0.05 $\rightarrow$ critical red).
- **Visual Style**: Monospaced fonts (JetBrains Mono or Fira Code) to ensure alignment. The "heatmap" vibe is maintained through color-coded text rather than just blocks.

### 2. The Telemetry Engine (Backend/Data Flow)
- **The "Thought Log" Protocol**: Each strategy in `~/projects/syngex/` must implement a standardized `emit_telemetry()` method.
- **Payload Structure**:
  ```json
  {
    "timestamp": "2026-05-20T08:05:01.123Z",
    "strategy_id": "syngex-gex-01",
    "step": "RSI_Cross_Check",
    "calc_value": "0.65",
    "confidence": 0.88,
    "raw_data_ref": "vol_spike_detected"
  }
  ```
- **Transport**: A lightweight WebSocket server (FastAPI/Uvicorn) that broadcasts these telemetry packets to the dashboard frontend. This ensures sub-second latency.

### 3. The Debug Stream (The "Line-by-Line" View)
- Each line in the tile is a discrete event.
- **Example Stream in Tile**:
  ```text
  [08:05:01] STEP: Volatility_Check | VAL: 0.12 | CONF: 0.92 | OK
  [08:05:02] STEP: Momentum_Delta | VAL: -0.04 | CONF: 0.45 | WARN
  [08:05:03] STEP: RSI_Threshold | VAL: 68.2 | CONF: 0.81 | OK
  ```
- This allows us to see exactly *where* a confidence score drops or where a calculation deviates from expected behavior.

## Implementation Roadmap

### Phase 1: The Telemetry Interface (The "Hook")
- Define the `SyngexTelemetry` base class.
- Integrate the `emit_telemetry` hook into existing strategy loops in `~/projects/syngex/`.

### Phase 2: The Streamer (The "Pipe")
- Build a standalone service `syngex-telemetry-server`.
- This service acts as the central hub, receiving data from all running processes and pushing it to the WebSocket.

### Phase 3: The Observer (The "Lens")
- Develop the React/Vue-based dashboard.
- Implement the "Tile" component with high-performance rendering (using `requestAnimationFrame` to prevent UI lag during high-frequency updates).

## Summary of Benefits
- **Instant Debugging**: No more digging through massive log files. If a strategy fails, you see the exact calculation step that preceded the failure.
- **Live Confidence Monitoring**: Watch the "conviction" of our models in real-time.
- **Zero Friction**: The dashboard is a passive observer; it doesn't interfere with the execution speed of the strategies.

---
*Drafted by Rune* 🐉
*Location: ~/projects/syngex/plan/Rune_Dashboard_Design.md*