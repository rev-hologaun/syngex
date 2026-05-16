"""
WebSocket Server for real-time Syngex data streaming.

Provides:
- Real-time signals, metrics, GEX ladder, positions broadcasts
- Client subscription management
- Graceful shutdown with connection draining
"""

import asyncio
import logging
from typing import Set, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

logger = logging.getLogger("SyngexWebSocket")


class SyngexWebSocketServer:
    """WebSocket server for real-time dashboard communication."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8202, timeout: int = 5000):
        self.host = host
        self.port = port
        self.timeout_ms = timeout
        self.app = FastAPI(title="Syngex WebSocket Server")
        self.active_connections: Set[WebSocket] = set()
        self._server = None
        self._background_tasks: Set[asyncio.Task] = set()

        # Register routes
        self.app.websocket("/ws")(self.websocket_endpoint)
        self.app.get("/health")(self.health_check)

    async def start(self):
        """Start WebSocket server as background task."""
        import uvicorn

        class LogFilter(logging.Filter):
            def filter(self, record):
                return "Uvicorn running" not in record.getMessage()

        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.addFilter(LogFilter())

        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(config)

        task = asyncio.create_task(self._server.serve())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

        await asyncio.sleep(0.5)  # Give server time to start
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")

    async def stop(self):
        """Stop WebSocket server with graceful connection draining."""
        logger.info("Shutting down WebSocket server...")

        # Close all active connections
        disconnect_tasks = []
        for connection in list(self.active_connections):
            disconnect_tasks.append(asyncio.create_task(connection.close()))

        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)

        self.active_connections.clear()

        # Stop server
        if self._server:
            self._server.should_exit = True
            await asyncio.wait_for(self._server.shutdown(), timeout=self.timeout_ms / 1000)

        logger.info("WebSocket server stopped")

    async def websocket_endpoint(self, websocket: WebSocket):
        """Handle WebSocket connections."""
        await websocket.accept()
        self.active_connections.add(websocket)

        try:
            # Send initial connection confirmation
            await websocket.send_json(
                {"type": "connected", "timestamp": asyncio.get_event_loop().time() * 1000}
            )

            # Keep connection alive
            while True:
                # Receive (client may send subscription requests)
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                    # Handle subscription requests if needed
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await websocket.send_json({"type": "ping"})
        except WebSocketDisconnect:
            pass
        finally:
            self.active_connections.discard(websocket)
            logger.debug(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def health_check(self):
        """Health check endpoint."""
        return {
            "status": "healthy",
            "active_connections": len(self.active_connections),
            "port": self.port,
        }

    # Broadcast methods (sync wrappers for orchestrator compatibility)
    def broadcast_signals(self, signals: list):
        """Broadcast new signals to all clients (sync wrapper)."""
        asyncio.create_task(self._broadcast("signals_update", signals))

    def broadcast_metrics(self, metrics: dict):
        """Broadcast metrics to all clients (sync wrapper)."""
        asyncio.create_task(self._broadcast("metrics_update", metrics))

    def broadcast_gex(self, gex_ladder: dict):
        """Broadcast GEX ladder to all clients (sync wrapper)."""
        asyncio.create_task(self._broadcast("gex_update", gex_ladder))

    def broadcast_positions(self, positions: list):
        """Broadcast positions to all clients (sync wrapper)."""
        asyncio.create_task(self._broadcast("positions_update", positions))

    async def _broadcast(self, msg_type: str, data: Any):
        """Internal broadcast to all connected clients."""
        message = {
            "type": msg_type,
            "timestamp": asyncio.get_event_loop().time() * 1000,
            "data": data,
        }

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)
