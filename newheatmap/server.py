"""
dashboard/server.py — Lightweight HTTP server for heatmap static files.

Serves dashboard/mockup/ on port 8201.
This is Option A from the implementation plan: Static Server + Separate WebSocket.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Heatmap] %(message)s",
)
logger = logging.getLogger(__name__)


class HeatmapHandler(SimpleHTTPRequestHandler):
    """Custom handler for heatmap static files."""
    
    def __init__(self, *args, **kwargs):
        # Serve from dashboard/mockup directory
        super().__init__(*args, directory='dashboard/mockup', **kwargs)
    
    def log_message(self, format, *args):
        """Log to logger instead of stderr."""
        logger.info("%s - %s", self.address_string(), format % args)
    
    def do_GET(self):
        """Handle GET requests."""
        # Redirect root to index.html
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()


def run_server(host='0.0.0.0', port=8201):
    """Start the heatmap HTTP server.
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to listen on (default: 8201)
    """
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    logger.info("Working directory: %s", os.getcwd())
    
    server = HTTPServer((host, port), HeatmapHandler)
    logger.info("Heatmap server running on http://%s:%d", host, port)
    logger.info("Access the dashboard at http://localhost:%d", port)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.shutdown()


if __name__ == '__main__':
    run_server()
