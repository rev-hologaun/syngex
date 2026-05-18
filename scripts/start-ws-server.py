#!/usr/bin/env python3
"""
Wrapper to start Syngex WebSocket server.
"""

import sys
import asyncio
import logging

# Add parent directory to path
sys.path.insert(0, '/home/hologaun/projects/syngex')

from websocket_server import SyngexWebSocketServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WebSocketWrapper')

async def main():
    server = SyngexWebSocketServer(host='0.0.0.0', port=8202)
    await server.start()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await server.stop()

if __name__ == '__main__':
    logger.info("Starting Syngex WebSocket Server on port 8202...")
    asyncio.run(main())
