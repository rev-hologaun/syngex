"""
Heatmap server - serves the new mockup as static files.
Integrated into main.py orchestrator lifecycle.
"""

import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import logging

logger = logging.getLogger('SyngexHeatmap')

class HeatmapHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from mockup directory
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), 'mockup'), **kwargs)
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")
    
    def end_headers(self):
        # Disable caching
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def run_heatmap(host='0.0.0.0', port=8001):
    """
    Start HTTP server serving the mockup heatmap.
    Called from main.py orchestrator.
    
    Returns:
        tuple: (server, thread) for later shutdown
    """
    server = HTTPServer((host, port), HeatmapHandler)
    logger.info(f"Heatmap running on http://{host}:{port}")
    logger.info(f"Serving from: {os.path.abspath(os.path.join(os.path.dirname(__file__), 'mockup'))}")
    
    # Run in background thread
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    return server, thread

def stop_heatmap(server):
    """Stop the heatmap server."""
    logger.info("Stopping heatmap server...")
    server.shutdown()
