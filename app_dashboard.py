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


def render_tab_gamma_profile(state: dict) -> None:
    """Tab for Gamma Profile — line chart of Strike vs. Net Gamma."""
    strikes = state.get("strikes", {})
    st.subheader("Gamma Profile")

    if not strikes:
        st.warning("No gamma data available yet.")
        return

    # Build DataFrame: index = strike (float), column = net_gamma
    profile_df = pd.DataFrame(
        [
            {"strike": float(s), "net_gamma": b.get("net_gamma", 0.0)}
            for s, b in strikes.items()
        ]
    ).sort_values("strike")

    st.line_chart(
        profile_df.set_index("strike"),
        y="net_gamma",
        width="stretch",
    )


def render_tab_top_strikes(state: dict) -> None:
    """Table of the top strikes ranked by absolute Net Gamma."""
    strikes = state.get("strikes", {})
    st.subheader("Top Strikes by Absolute Net Gamma")

    if not strikes:
        st.warning("No strike data available yet.")
        return

    sorted_strikes = sorted(
        strikes.items(),
        key=lambda x: float(x[0]),  # sort by strike price
        reverse=True,                # descending (highest first)
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

    row_height = 36
    height = min(len(top_df) * row_height, 1200)  # cap at 1200px
    st.dataframe(top_df, width="stretch", height=height)


def render_tab_gamma_flip(state: dict) -> None:
    """Tab for Gamma Flip analysis."""
    strikes = state.get("strikes", {})
    symbol = state.get("symbol", "???")
    current_price = state.get("underlying_price", 0.0)

    if not strikes:
        st.warning("No strike data available yet.")
        return

    # Calculate cumulative gamma from high to low strikes
    sorted_strikes = sorted(strikes.keys(), reverse=True)
    cumulative = 0.0
    flip_strike = None
    cumulative_rows = []

    for strike in sorted_strikes:
        bucket = strikes[strike]
        net_gamma = bucket.get("net_gamma", 0.0)
        cumulative += net_gamma
        cumulative_rows.append({
            "Strike": strike,
            "Net Gamma": net_gamma,
            "Cumulative": cumulative,
            "Flip": False,
        })
        if flip_strike is None and cumulative < 0:
            flip_strike = strike
            cumulative_rows[-1]["Flip"] = True

    # Main flip metric
    flip_col1, flip_col2, flip_col3 = st.columns([1, 2, 1])
    with flip_col2:
        if flip_strike is not None:
            st.metric(
                label="🔄 Gamma Flip Strike",
                value=f"${float(flip_strike):.1f}",
            )
            # Show distance from current price
            if current_price > 0:
                dist = float(flip_strike) - current_price
                pct = (dist / current_price * 100)
                st.caption(f"Distance from ${current_price:.2f}: {dist:+.2f} ({pct:+.1f}%)")
        else:
            st.info("No gamma flip detected — cumulative gamma stays positive at all strikes.")

    # Explanation
    st.caption(
        "The Gamma Flip is the highest strike where cumulative net gamma turns negative. "
        "Below this level, the market tends to self-stabilize (negative gamma). "
        "Above it, the market tends to accelerate (positive gamma)."
    )

    # Cumulative gamma table
    st.subheader("Cumulative Gamma Scan (High → Low Strikes)")
    cum_df = pd.DataFrame(cumulative_rows)
    cum_df["Strike"] = cum_df["Strike"].astype(float).apply(lambda x: f"${x:.1f}")
    cum_df["Net Gamma"] = cum_df["Net Gamma"].astype(float).apply(lambda x: f"{x:,.2f}")
    cum_df["Cumulative"] = cum_df["Cumulative"].astype(float).apply(lambda x: f"{x:,.2f}")

    # Highlight the flip row
    styled = cum_df.style.highlight_max(
        subset=["Cumulative"], color="lightgreen"
    ).highlight_min(
        subset=["Cumulative"], color="lightcoral"
    )
    st.dataframe(styled, width="stretch", use_container_width=True)


def render_tab_gamma_walls(state: dict) -> None:
    """Tab for Gamma Walls analysis."""
    strikes = state.get("strikes", {})
    current_price = state.get("underlying_price", 0.0)

    if not strikes:
        st.warning("No strike data available yet.")
        return

    # Calculate GEX per strike
    GEX_MULTIPLIER = 100
    THRESHOLD = 500_000  # $500K in GEX terms
    walls = []

    for strike, bucket in strikes.items():
        net_gamma = bucket.get("net_gamma", 0.0)
        gex = net_gamma * GEX_MULTIPLIER * current_price if current_price > 0 else 0
        total_contracts = bucket.get("total_contracts", 0)
        side = "Call Wall" if net_gamma > 0 else "Put Wall"
        color = "🟢" if net_gamma > 0 else "🔴"

        walls.append({
            "Strike": strike,
            "Side": side,
            "Color": color,
            "Net Gamma": net_gamma,
            "GEX": gex,
            "Contracts": total_contracts,
        })

    # Sort by absolute GEX
    walls.sort(key=lambda x: abs(x["GEX"]), reverse=True)

    # Filter to significant walls
    significant_walls = [w for w in walls if abs(w["GEX"]) >= THRESHOLD]

    # Main metric
    if significant_walls:
        top_wall = significant_walls[0]
        wall_col1, wall_col2, wall_col3 = st.columns([1, 2, 1])
        with wall_col2:
            st.metric(
                label="🧱 Dominant Gamma Wall",
                value=f"{top_wall['Color']} Strike ${float(top_wall['Strike']):.1f} ({top_wall['Side']})",
                delta=f"GEX: ${top_wall['GEX']:,.0f}",
                delta_color="green" if top_wall["GEX"] > 0 else "red",
            )
            if current_price > 0:
                dist = float(top_wall["Strike"]) - current_price
                pct = (dist / current_price * 100)
                st.caption(f"Distance from ${current_price:.2f}: {dist:+.2f} ({pct:+.1f}%)")
    else:
        st.info("No significant gamma walls detected above $500K threshold.")

    # Explanation
    st.caption(
        "Gamma Walls are strikes with massive GEX concentration. "
        "Call walls (green) act as magnetic attractors. "
        "Put walls (red) act as support/resistance barriers. "
        "Threshold: $500K GEX."
    )

    # Show ALL walls table (not just significant)
    st.subheader("All Gamma Walls (Sorted by GEX Magnitude)")
    wall_df = pd.DataFrame(walls)
    wall_df["Strike"] = wall_df["Strike"].astype(float).apply(lambda x: f"${x:.1f}")
    wall_df["Net Gamma"] = wall_df["Net Gamma"].astype(float).apply(lambda x: f"{x:,.2f}")
    wall_df["GEX"] = wall_df["GEX"].astype(float).apply(lambda x: f"${x:,.0f}")
    wall_df = wall_df[["Color", "Strike", "Side", "Net Gamma", "GEX", "Contracts"]]

    styled = wall_df.style.highlight_max(
        subset=["GEX"], color="lightgreen"
    ).highlight_min(
        subset=["GEX"], color="lightcoral"
    )
    st.dataframe(styled, width="stretch", use_container_width=True)


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

# All data loaded — render into tabs
render_header(state)
render_metrics(state)

tab1, tab2, tab3 = st.tabs(["📊 Gamma Profile", "🔄 Gamma Flip", "🧱 Gamma Walls"])

with tab1:
    render_tab_gamma_profile(state)
    render_tab_top_strikes(state)

with tab2:
    render_tab_gamma_flip(state)

with tab3:
    render_tab_gamma_walls(state)

render_status(state)

# Auto-refresh loop
while True:
    time.sleep(POLL_INTERVAL)
    st.rerun()
