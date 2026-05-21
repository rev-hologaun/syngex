import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, send_from_directory
import time
from strategies.metrics import collector

app = Flask(__name__)

@app.route('/api/metrics/health')
def health():
    return {"status": "ok", "timestamp": time.time()}

@app.route('/api/metrics/all')
def get_all():
    return jsonify(collector.get_all())

@app.route('/api/metrics/<strategy_id>/latest')
def get_latest(strategy_id):
    return jsonify(collector.get_latest(strategy_id))

@app.route('/api/metrics/<strategy_id>/history')
def get_history(strategy_id):
    limit = int(request.args.get('limit', 60))
    return jsonify(collector.get_history(strategy_id, limit))

# Serve dashboard files
DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dashboard')

@app.route('/dashboard/')
def dashboard_index():
    return send_from_directory(DASHBOARD_DIR, 'index.html')

@app.route('/dashboard/<path:filename>')
def serve_dashboard(filename):
    return send_from_directory(DASHBOARD_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
