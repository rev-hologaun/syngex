#!/bin/bash
# Start heatmap system (WebSocket server + Frontend)

set -e
cd /home/hologaun/projects/syngex

echo "=== Syngex Heatmap Startup ==="

# Kill any existing processes
pkill -f "python3 -m http.server 8201" 2>/dev/null || true
pkill -f "websocket_server" 2>/dev/null || true
sleep 1

# Start WebSocket server in background
echo "Starting WebSocket server on port 8202..."
python3 scripts/start-ws-server.py &
WS_PID=$!
echo "✓ WebSocket server started (PID: $WS_PID)"

# Start frontend
echo "Starting heatmap frontend on port 8201..."
cd dashboard
python3 -m http.server 8201 --bind 0.0.0.0 &
HTTP_PID=$!
echo "✓ Frontend started (PID: $HTTP_PID)"

echo ""
echo "=== Heatmap System Running ==="
echo "Frontend: http://localhost:8201"
echo "WebSocket: ws://localhost:8202/ws"
echo ""
echo "Press Ctrl+C to stop"

# Cleanup on exit
trap "kill $WS_PID $HTTP_PID 2>/dev/null; echo 'Shutdown complete'; exit" INT TERM

# Wait for interrupt
wait
