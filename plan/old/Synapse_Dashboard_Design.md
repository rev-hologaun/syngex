# Synapse Strategy Live-Metric Dashboard Design

## Vision
To provide real-time, second-by-second visibility into the "internal monologue" of our trading strategies. This dashboard acts as a live debugger, transforming opaque algorithmic decisions into a readable, high-density stream of telemetry.

## Architecture: The "Strategy Pulse" Dashboard

### 1. UI/UX: The Tile Grid
- **Layout**: A responsive CSS Grid of "Strategy Tiles."
- **Tile Identity**: Each tile is headed by the Strategy Name (e.g., `Alpha-Trend-v2`) and its current status (Active, Paused, Error).
- **The Stream**: The body of each tile is a terminal-style scrolling text area. It mimics a live log but is specifically formatted for metric readability.
- **Visual Cues**: Tile borders glow based on activity levels or confidence thresholds (e.g., Green for high confidence, Red for low/divergent, Pulsing Blue for active calculation).

### 2. Data Flow: The Telemetry Pipeline
To avoid performance bottlenecks, we must not poll files. Instead, we use a **Pub/Sub** or **WebSocket** model.

- **Strategy Side (Producer)**:
  - Strategies in `~/projects/syngex/` will include a lightweight `TelemetryEmitter` module.
  - Every calculation step (e.g., `RSI: 65.2`, `MACD: Cross-Down`, `Volatility: 0.12`) is emitted as a structured JSON packet via a local UDP socket or a lightweight Redis stream.
  - **Packet Structure**:
    ```json
    {
      "ts": "2026-05-20T08:05:01.123Z",
      "strat": "Alpha-Trend-v2",
      "calc": "RSI_Value",
      "val": "65.2",
      "conf": 0.88,
      "level": "INFO"
    }
    ```

- **Dashboard Backend (Aggregator)**:
  - A small Python/FastAPI service that listens to the telemetry stream.
  - It maintains the "last 60 seconds" of data in memory for each strategy to allow for rapid UI updates.
  - It serves this data via WebSockets to the frontend.

- **Frontend (Consumer)**:
  - A React/Vite application using `Tailwind CSS` for the tile layout and `Xterm.js` (or a lightweight custom component) for the high-speed text streaming within tiles.
  - **Update Frequency**: The UI refreshes the text stream at 1Hz (once per second) to match the user's requirement, ensuring it's readable but highly responsive.

### 3. Key Features
- **Line-by-Line Trace**: Each tile shows the exact sequence of calculations. 
  - *Example Trace*:
    - `[08:05:01] MACD: 0.02 (Conf: 0.92)`
    - `[08:05:01] VOL: 1.2 (Conf: 0.45)`
    - `[08:05:01] SIGNAL: HOLD (Conf: 0.77)`
- **Confidence Heatmap**: The "Confidence Score" within the line is color-coded. A low confidence score (e.g., < 0.5) causes the line to appear in dim gray, while high confidence (e.g., > 0.9) appears in bright white or green.
- **Debug Mode Toggle**: A global switch to increase/decrease the granularity of the telemetry (e.g., "Verbose" vs. "Summary").

## Implementation Roadmap

1.  **Phase 1: Telemetry Module**: Develop the `TelemetryEmitter` class and integrate it into the base Strategy class in `~/projects/syngex/`.
2.  **Phase 2: The Aggregator**: Build the FastAPI service to capture and broadcast the stream.
3.  **Phase 3: The Frontend**: Build the React-based dashboard with the tile-grid and streaming text components.
4.  **Phase 4: Integration**: Deploy the dashboard locally and verify the second-by-second latency.

---
*Designed by Synapse* 👁️‍🗨️