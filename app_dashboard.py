"""
app_dashboard.py — Syngex Real-Time Gamma Exposure Dashboard

Standalone Streamlit app that reads GEX data from a shared JSON file
written by the Syngex orchestrator (`main.py`).

Data file : data/gex_state.json  (written by orchestrator every ~1 s)
Refresh   : every 2 s via Streamlit rerun

Widgets
-------
    st.empty() containers for smooth, flicker-free updates
    st.metric   — Symbol price & Net Gamma (color-coded)
    st.line_chart — Gamma Profile (Strike → Net Gamma)
    st.dataframe — Top Strikes ranked by absolute Net Gamma
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "gex_state.json"
POLL_INTERVAL = 2  # seconds between polls

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Syngex GEX Dashboard",
    page_icon="🐙",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


@st.cache_data(ttl=2)
def load_gex_state() -> dict | None:
    """Load the latest GEX state from the shared JSON file.

    Cached with a 2-second TTL so the dashboard auto-refreshes
    without requiring a manual page reload.

    Returns None when the file is missing, empty, or corrupt.
    """
    if not DATA_FILE.exists():
        return None
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return None
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return None


def is_data_stale(state: dict, max_age_seconds: int = 30) -> bool:
    """Return True if the last_updated timestamp is older than *max_age_seconds*."""
    try:
        ts = time.strptime(state.get("last_updated", ""), "%Y-%m-%d %H:%M:%S %Z")
        file_age = time.time() - time.mktime(ts)
        return file_age > max_age_seconds
    except (ValueError, TypeError, OSError):
        return False


# ---------------------------------------------------------------------------
# UI — all mutable sections live inside st.empty() containers
# ---------------------------------------------------------------------------

# Placeholder containers (created once, replaced on every rerun)
header_container = st.empty()
metric_container = st.empty()
chart_container = st.empty()
table_container = st.empty()
status_container = st.empty()


# ---------------------------------------------------------------------------
# Render functions
# ---------------------------------------------------------------------------

def render_header(state: dict) -> None:
    """Header row: symbol + underlying price."""
    symbol = state.get("symbol", "???")
    price = state.get("underlying_price", 0.0)
    header_container.markdown(
        f"### 🐙 **Syngex Gamma Dashboard**  —  **{symbol}**  "
        f"  |  Price: ${price:,.2f}"
    )


def render_metrics(state: dict) -> None:
    """Metric cards — Net Gamma is color-coded green / red."""
    net_gamma = state.get("net_gamma", 0.0)
    active_strikes = state.get("active_strikes", 0)
    total_messages = state.get("total_messages", 0)

    # Color decision for the Net Gamma delta
    if net_gamma > 0:
        delta_color = "green"
        delta_prefix = "+"
    elif net_gamma < 0:
        delta_color = "red"
        delta_prefix = ""
    else:
        delta_color = None
        delta_prefix = ""

    col1, col2, col3, col4 = metric_container.columns(4)

    with col1:
        st.metric(
            label="📈 Underlying Price",
            value=f"${state.get('underlying_price', 0.0):,.2f}",
        )

    with col2:
        st.metric(
            label="⚡ Net Gamma",
            value=f"{net_gamma:,.2f}",
            delta=f"{delta_prefix}{net_gamma:+,.2f}",
            delta_color=delta_color,
        )

    with col3:
        st.metric(label="🎯 Active Strikes", value=f"{active_strikes:,}")

    with col4:
        st.metric(label="📨 Messages", value=f"{total_messages:,}")


def render_gamma_profile(state: dict) -> None:
    """Line chart of the Gamma Profile (Strike vs. Net Gamma)."""
    strikes = state.get("strikes", {})
    chart_container.subheader("Gamma Profile")

    if not strikes:
        chart_container.warning("No gamma data available yet.")
        return

    # Build DataFrame: index = strike (float), column = net_gamma
    profile_df = pd.DataFrame(
        [
            {"strike": float(s), "net_gamma": b.get("net_gamma", 0.0)}
            for s, b in strikes.items()
        ]
    ).sort_values("strike")

    chart_container.line_chart(
        profile_df.set_index("strike"),
        y="net_gamma",
        width="stretch",
    )


def render_top_strikes(state: dict) -> None:
    """Table of the top strikes ranked by absolute Net Gamma."""
    strikes = state.get("strikes", {})
    table_container.subheader("Top Strikes by Absolute Net Gamma")

    if not strikes:
        table_container.warning("No strike data available yet.")
        return

    sorted_strikes = sorted(
        strikes.items(),
        key=lambda x: abs(x[1].get("net_gamma", 0.0)),
        reverse=True,
    )

    top_df = pd.DataFrame(
        [
            {
                "Strike": f"${float(s):.1f}",
                "Net Gamma": f"{b.get('net_gamma', 0.0):,.2f}",
                "Call GEX": f"{b.get('call_gamma_oi', 0.0):,.2f}",
                "Put GEX": f"{b.get('put_gamma_oi', 0.0):,.2f}",
                "Contracts": b.get("total_contracts", 0),
            }
            for s, b in sorted_strikes
        ]
    )

    table_container.dataframe(top_df, width="stretch")


def render_status(state: dict | None) -> None:
    """Footer / status message."""
    if state is None:
        status_container.info(
            "⏳ **Waiting for data…**  "
            "Start the Syngex orchestrator (`python3 main.py TSLA`) and the "
            "dashboard will update automatically."
        )
    else:
        last_updated = state.get("last_updated", "unknown")
        symbol = state.get("symbol", "???")
        stale = is_data_stale(state)
        if stale:
            status_container.warning(
                f"⚠️ Data may be stale (last update: {last_updated}). "
                f"Check that the orchestrator is running for **{symbol}**."
            )
        else:
            status_container.caption(
                f"Last updated: {last_updated}  |  Symbol: {symbol}"
            )


# ---------------------------------------------------------------------------
# Main loop — auto-refresh
# ---------------------------------------------------------------------------

spinner = st.empty()
state = load_gex_state()

if state is None:
    spinner.info(
        "⏳ **Waiting for data…**  "
        "Start the Syngex orchestrator (`python3 main.py TSLA`) and the "
        "dashboard will update automatically."
    )
    # Poll until data arrives
    while state is None:
        time.sleep(1)
        state = load_gex_state()
    spinner.empty()  # Remove spinner once data arrives

# All data loaded — render into containers
render_header(state)
render_metrics(state)
render_gamma_profile(state)
render_top_strikes(state)
render_status(state)

# Auto-refresh loop
while True:
    time.sleep(POLL_INTERVAL)
    st.rerun()
