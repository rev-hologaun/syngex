#!/usr/bin/env python3
"""
app_heatmap.py — Syngex Heatmap Dashboard (Flask + SocketIO)

Standalone heatmap server on port 8502.
Reads data/gex_state_{SYMBOL}.json every 1s and pushes updates via WebSocket.

Usage:
    python3 app_heatmap.py              # uses SYNGEX_SYMBOL env var (default: UNKNOWN)
    SYNGEX_SYMBOL=TSLA python3 app_heatmap.py

Data source: shared JSON file written by main.py orchestrator.
No direct coupling — reads the file independently.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict

from flask import Flask, render_template

# ---------------------------------------------------------------------------
# Running stats for O(1) strategy P&L and win-rate lookups
# ---------------------------------------------------------------------------


class RunningStats:
    """Per-strategy running stats for P&L and win rate."""

    def __init__(self) -> None:
        self.total: float = 0.0  # cumulative P&L
        self.wins: int = 0  # count of WIN outcomes
        self.count: int = 0  # total signals resolved

    def update(self, pnl: float, outcome: str) -> None:
        self.total += pnl
        self.count += 1
        if outcome == "WIN":
            self.wins += 1

    @property
    def win_rate(self) -> float:
        return self.wins / self.count if self.count > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {"win_rate": round(self.win_rate, 4), "pnl": round(self.total, 2)}


def _load_stats_from_disk(symbol: str) -> Dict[str, RunningStats]:
    log_path = LOG_DIR / f"signal_outcomes_{symbol}.jsonl"
    stats: Dict[str, RunningStats] = {}
    if not log_path.exists():
        return stats
    for line in log_path.read_text().strip().splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            sid = entry.get("strategy_id", "")
            if not sid:
                continue
            if sid not in stats:
                stats[sid] = RunningStats()
            stats[sid].update(entry.get("pnl", 0.0), entry.get("outcome", ""))
        except json.JSONDecodeError:
            pass
    return stats
from flask_socketio import SocketIO, emit, join_room

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
LOG_DIR = Path(__file__).parent / "log"
SYMBOL = os.environ.get("SYNGEX_SYMBOL", "UNKNOWN").upper()
DATA_FILE = DATA_DIR / f"gex_state_{SYMBOL}.json"
PORT = int(os.environ.get("HEATMAP_PORT", 8502))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

# Avoid logging.basicConfig() — it conflicts with Werkzeug's dev server
# which also calls basicConfig, causing the server to crash silently.
# Use manual handler setup instead.
logger = logging.getLogger("SyngexHeatmap")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
)
logger.addHandler(_handler)

# ---------------------------------------------------------------------------
# Flask + SocketIO
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = "syngex-heatmap-secret-key"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Pre-load strategy stats from disk (avoids O(n) JSONL parse every 1s)
_strategy_stats: Dict[str, RunningStats] = _load_stats_from_disk(SYMBOL)

# In-memory cache of latest data
_latest_data: dict = {}
_latest_ts: float = 0.0
_latest_data_lock = threading.Lock()


# ---------------------------------------------------------------------------
# JSON reader (background)
# ---------------------------------------------------------------------------

def _read_json_file() -> dict | None:
    """Read and parse the shared JSON file. Returns None on failure."""
    if not DATA_FILE.exists():
        return None
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None


def _transform_for_socket(data: dict) -> dict:
    """Transform raw GEX state into a clean SocketIO payload."""
    global _latest_ts
    _latest_ts = time.time()

    strategies = {}
    strategy_health = data.get("strategy_health", {})
    strategy_stats = {}

    # Use pre-loaded running stats (O(1) per strategy)
    for sid, rs in _strategy_stats.items():
        strategy_stats[sid] = rs.to_dict()

    # Load signal counts from per-symbol signal log (authoritative, survives restarts)
    try:
        sig_log_path = LOG_DIR / f"signals_{SYMBOL}.jsonl"
        if sig_log_path.exists():
            strat_signal_counts: Dict[str, int] = {}
            for line in sig_log_path.read_text().strip().splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    sid = entry.get("strategy_id", "")
                    if sid:
                        strat_signal_counts[sid] = strat_signal_counts.get(sid, 0) + 1
                except json.JSONDecodeError:
                    pass
            # Merge signal counts into strategy_stats
            for sid, count in strat_signal_counts.items():
                if sid not in strategy_stats:
                    strategy_stats[sid] = {}
                strategy_stats[sid]["signal_count"] = count
    except Exception:
        pass

    now = time.time()

    for strat_name, health in strategy_health.items():
        stats = strategy_stats.get(strat_name, {})
        last_signal_ts = health.get("last_signal_ts", 0)
        time_since = now - last_signal_ts if last_signal_ts > 0 else 9999

        # Determine status
        if health.get("status") == "error":
            status = "error"
        elif time_since > 300:  # 5 min idle threshold
            status = "idle"
        else:
            status = "active"

        # Build sparkline from recent signals if available
        sparkline = health.get("sparkline", [])
        if not sparkline:
            # Fallback: generate from stats
            sparkline = [0.0] * 8

        strategies[strat_name] = {
            "status": status,
            "signal_count": health.get("signal_count", 0),
            "last_signal_ts": last_signal_ts,
            "win_rate": stats.get("win_rate", health.get("win_rate", 0.0)),
            "pnl": stats.get("pnl", health.get("pnl", 0.0)),
            "sparkline": sparkline[-8:],  # last 8 values
            "confidence": health.get("confidence", 0.0),
        }

    # Transform per-strike gamma data for the chart and wall panel
    gamma_data = []
    strikes_raw = data.get("strikes", {})
    for strike_str, bucket in strikes_raw.items():
        try:
            strike = float(strike_str)
        except (ValueError, TypeError):
            continue
        gamma_data.append({
            "strike": strike,
            "net_gamma": bucket.get("net_gamma", 0.0),
            "call_gamma_oi": bucket.get("call_gamma_oi", 0.0),
            "put_gamma_oi": bucket.get("put_gamma_oi", 0.0),
            "total_contracts": bucket.get("total_contracts", 0),
        })
    gamma_data.sort(key=lambda x: x["strike"])

    return {
        "symbol": data.get("symbol", SYMBOL),
        "underlying_price": data.get("underlying_price", 0.0),
        "net_gamma": data.get("net_gamma", 0.0),
        "regime": data.get("regime_filter", {}).get("regime", "UNKNOWN"),
        "timestamp": _latest_ts,
        "strategies": strategies,
        "last_updated": data.get("last_updated", ""),
        "micro_signals": data.get("micro_signals", {}),
        "gamma_data": gamma_data,
        "last_trigger": data.get("last_trigger", {}),
        "data_valid": True,
    }


def _push_latest() -> None:
    """Read JSON, transform, emit to all connected clients."""
    global _latest_data
    data = _read_json_file()
    if data is None:
        # Emit a minimal payload with data_valid=False so the frontend
        # can show a "void" state instead of blank/neutral cards.
        payload = {
            "symbol": SYMBOL,
            "underlying_price": 0.0,
            "net_gamma": 0.0,
            "regime": "UNKNOWN",
            "timestamp": _latest_ts,
            "strategies": {},
            "last_updated": "",
            "micro_signals": {},
            "data_valid": False,
        }
        with _latest_data_lock:
            _latest_data = payload
        socketio.emit("strategy_update", _latest_data, room=SYMBOL)
        return
    _latest_data = _transform_for_socket(data)
    socketio.emit("strategy_update", _latest_data, room=SYMBOL)


# ---------------------------------------------------------------------------
# Background updater
# ---------------------------------------------------------------------------

def _background_updater():
    """Background thread: read JSON and emit updates every 1 second."""
    logger.info("Background updater started (reading %s)", DATA_FILE)
    while True:
        try:
            socketio.sleep(1.0)
            _push_latest()
        except Exception as exc:
            logger.warning("Background updater error: %s", exc)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@socketio.on("connect")
def handle_connect():
    """Push latest data immediately on connect."""
    logger.info("Client connected")
    join_room(SYMBOL)
    with _latest_data_lock:
        snapshot = dict(_latest_data)
    if snapshot:
        emit("strategy_update", snapshot, room=SYMBOL)


@socketio.on("disconnect")
def handle_disconnect():
    logger.info("Client disconnected")


@app.route("/")
def index():
    """Serve the heatmap HTML page."""
    return render_template("heatmap.html", symbol=SYMBOL, port=PORT)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Syngex Heatmap Dashboard starting on port %d", PORT)
    logger.info("Data file: %s", DATA_FILE)
    logger.info("Symbol: %s", SYMBOL)

    # Start background updater thread
    import threading
    bg_thread = threading.Thread(target=_background_updater, daemon=True)
    bg_thread.start()

    socketio.run(app, host="0.0.0.0", port=PORT, debug=False, allow_unsafe_werkzeug=True)
