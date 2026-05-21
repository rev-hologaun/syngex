"""
Syngex Dashboard Backend - FastAPI server for real-time strategy metrics.

Provides WebSocket connectivity for live dashboard updates and REST API
for receiving metrics from trading strategies.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Dict
import time
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Syngex.Dashboard.Server")

app = FastAPI(title="Syngex Dashboard Server")

# Global storage
strategy_data: Dict[str, dict] = {}  # stores latest metrics per strategy
websockets: List[WebSocket] = []  # connected dashboard clients


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the dashboard HTML file."""
    return FileResponse("index.html")


async def broadcast(message: dict) -> None:
    """
    Broadcast a message to all connected WebSocket clients.
    
    Args:
        message: Dictionary to serialize and send to clients
        
    Removes disconnected clients from the websocket list gracefully.
    """
    logger.info(f"📡 Broadcasting to {len(websockets)} connected client(s)")
    disconnected = []
    for websocket in websockets:
        try:
            await websocket.send_json(message)
            logger.info(f"✅ Sent to client")
        except Exception as e:
            # Client disconnected, mark for removal
            logger.warning(f"⚠️ Client disconnected: {e}")
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for websocket in disconnected:
        websockets.remove(websocket)


@app.post("/metrics")
async def receive_metrics(payload: dict):
    """
    Receive strategy metrics and broadcast to dashboard clients.
    
    Expected payload:
        {
            "strategy": str,      # Strategy identifier
            "timestamp": float,   # Unix timestamp
            "lines": list         # Metric lines/data
        }
    
    Returns:
        {"status": "ok"} on success
    """
    strategy = payload.get("strategy")
    timestamp = payload.get("timestamp")
    lines = payload.get("lines")
    
    if not all([strategy, timestamp is not None, lines is not None]):
        logger.error(f"❌ Missing required fields: strategy, timestamp, lines")
        return {"status": "error", "message": "Missing required fields: strategy, timestamp, lines"}
    
    logger.info(f"📥 Received metrics from strategy: {strategy} ({len(lines)} data points)")
    
    # Store the latest metrics for this strategy
    strategy_data[strategy] = {
        "lines": lines,
        "timestamp": timestamp,
        "status": "LIVE"
    }
    
    # Broadcast update to all connected clients
    await broadcast({
        "type": "update",
        "strategy": strategy,
        "data": strategy_data[strategy]
    })
    
    logger.info(f"✅ Broadcast update for strategy: {strategy}")
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard connectivity.
    
    Clients connect here to receive live strategy metric updates.
    Initial connection sends full state, subsequent messages are
    incremental updates.
    """
    await websocket.accept()
    websockets.append(websocket)
    
    # Send initial state
    await websocket.send_json({
        "type": "init",
        "data": strategy_data
    })
    
    try:
        # Keep connection alive - listen for any client messages
        while True:
            # Small timeout to allow periodic checks
            data = await websocket.receive_text()
            # Could handle incoming messages here if needed
    except WebSocketDisconnect:
        pass
    finally:
        # Remove from list on disconnect
        if websocket in websockets:
            websockets.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
