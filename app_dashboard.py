"""
app_dashboard.py — Syngex Real-Time Gamma Exposure Dashboard

Standalone Streamlit app that reads GEX data from a shared JSON file
written by the Syngex orchestrator (`main.py`).

Data file : data/gex_state.json  (written by orchestrator every ~1s)
Refresh   : every 2s via Streamlit rerun
Bind      : 0.0.0.0:8501

Layout
------
    Header → Metric cards → 3-col grid (Profile / Flip / Walls) →
    Top Strikes table → Signals log → Footer
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
SIGNALS_FILE = Path(__file__).parent / "log" / "signals.jsonl"
POLL_INTERVAL = 2  # seconds between polls

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Syngex GEX Dashboard",
    page_icon="🕸️",
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


@st.cache_data(ttl=2)
def load_signals(n: int = 20) -> list[dict]:
    """Load the N most recent signals from the signals log."""
    if not SIGNALS_FILE.exists():
        return []
    try:
        lines = SIGNALS_FILE.read_text().strip().splitlines()
        # Read last N lines
        recent = [json.loads(line) for line in lines[-n:] if line.strip()]
        return list(reversed(recent))  # Oldest first
    except (json.JSONDecodeError, OSError):
        return []


def is_data_stale(state: dict, max_age_seconds: int = 30) -> bool:
    """Return True if the last_updated timestamp is older than *max_age_seconds*."""
    try:
        ts = time.strptime(state.get("last_updated", ""), "%Y-%m-%d %H:%M:%S %Z")
        file_age = time.time() - time.mktime(ts)
        return file_age > max_age_seconds
    except (ValueError, TypeError, OSError):
        return False


# ---------------------------------------------------------------------------
# Render functions
# ---------------------------------------------------------------------------


def render_header(state: dict) -> None:
    """Header row: symbol + underlying price."""
    symbol = state.get("symbol", "???")
    price = state.get("underlying_price", 0.0)
    st.markdown(
        f"### 🕸️ **Syngex Gamma Dashboard** — **{symbol}**  |  Price: ${price:,.2f}"
    )


def render_metrics(state: dict) -> None:
    """Metric cards — Net Gamma is color-coded green / red."""
    net_gamma = state.get("net_gamma", 0.0)
    active_strikes = state.get("active_strikes", 0)
    total_messages = state.get("total_messages", 0)
    underlying_price = state.get("underlying_price", 0.0)

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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📈 Underlying Price",
            value=f"${underlying_price:,.2f}",
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
    """Column 1 — Gamma Profile: line chart of Strike vs. Net Gamma."""
    strikes = state.get("strikes", {})
    st.subheader("📊 Gamma Profile")

    if not strikes:
        st.warning("No gamma data available yet.")
        return

    # Build DataFrame: strike (float), net_gamma
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


def render_gamma_flip(state: dict) -> None:
    """Column 2 — Gamma Flip: flip strike metric + compact cumulative scan."""
    strikes = state.get("strikes", {})
    current_price = state.get("underlying_price", 0.0)

    if not strikes:
        st.warning("No gamma data available yet.")
        return

    # Calculate cumulative gamma from high → low strikes
    sorted_strikes = sorted(strikes.keys(), key=lambda x: float(x), reverse=True)
    cumulative = 0.0
    flip_strike = None
    cumulative_rows = []

    for strike in sorted_strikes:
        bucket = strikes[strike]
        net_gamma = bucket.get("net_gamma", 0.0)
        cumulative += net_gamma
        cumulative_rows.append({
            "Strike": float(strike),
            "Net Gamma": net_gamma,
            "Cumulative": cumulative,
        })
        if flip_strike is None and cumulative < 0:
            flip_strike = float(strike)

    # Main flip metric
    if flip_strike is not None:
        st.metric(
            label="🔄 Gamma Flip Strike",
            value=f"${flip_strike:.1f}",
        )
        if current_price > 0:
            dist = flip_strike - current_price
            pct = (dist / current_price * 100)
            st.caption(f"Distance from ${current_price:.2f}: {dist:+.2f} ({pct:+.1f}%)")
    else:
        st.info("No gamma flip detected — cumulative gamma stays positive at all strikes.")

    st.caption(
        "The Gamma Flip is the highest strike where cumulative net gamma turns negative. "
        "Below this level, the market tends to self-stabilize (negative gamma). "
        "Above it, the market tends to accelerate (positive gamma)."
    )

    # Compact cumulative gamma scan table (~8 rows max)
    st.subheader("Cumulative Gamma Scan")
    cum_df = pd.DataFrame(cumulative_rows)
    cum_df["Strike"] = cum_df["Strike"].apply(lambda x: f"${x:.1f}")
    cum_df["Net Gamma"] = cum_df["Net Gamma"].apply(lambda x: f"{x:,.2f}")
    cum_df["Cumulative"] = cum_df["Cumulative"].apply(lambda x: f"{x:,.2f}")

    # Show up to 8 rows
    display_df = cum_df.head(8)
    st.dataframe(display_df, width="stretch", height=200)


def render_gamma_walls(state: dict) -> None:
    """Column 3 — Gamma Walls: dominant wall metric + compact walls table."""
    strikes = state.get("strikes", {})
    current_price = state.get("underlying_price", 0.0)

    if not strikes:
        st.warning("No gamma data available yet.")
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
            "Strike": float(strike),
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

    # Main metric — dominant wall
    if significant_walls:
        top_wall = significant_walls[0]
        st.metric(
            label="🧱 Dominant Gamma Wall",
            value=f"{top_wall['Color']} Strike ${top_wall['Strike']:.1f} ({top_wall['Side']})",
            delta=f"GEX: ${top_wall['GEX']:,.0f}",
            delta_color="green" if top_wall["GEX"] > 0 else "red",
        )
        if current_price > 0:
            dist = top_wall["Strike"] - current_price
            pct = (dist / current_price * 100)
            st.caption(f"Distance from ${current_price:.2f}: {dist:+.2f} ({pct:+.1f}%)")
    else:
        st.info("No significant gamma walls detected above $500K threshold.")

    st.caption(
        "Gamma Walls are strikes with massive GEX concentration. "
        "Call walls (green) act as magnetic attractors. "
        "Put walls (red) act as support/resistance barriers. "
        "Threshold: $500K GEX."
    )

    # Compact walls table (~8 rows max)
    st.subheader("Gamma Walls")
    wall_df = pd.DataFrame(walls)
    wall_df["Strike"] = wall_df["Strike"].apply(lambda x: f"${x:.1f}")
    wall_df["Net Gamma"] = wall_df["Net Gamma"].apply(lambda x: f"{x:,.2f}")
    wall_df["GEX"] = wall_df["GEX"].apply(lambda x: f"${x:,.0f}")
    wall_df = wall_df[["Color", "Strike", "Side", "Net Gamma", "GEX", "Contracts"]]

    # Show up to 8 rows
    display_df = wall_df.head(8)
    st.dataframe(display_df, width="stretch", height=200)


def render_top_strikes(state: dict) -> None:
    """Bottom full-width table — Top Strikes by |Net Gamma|."""
    strikes = state.get("strikes", {})
    st.subheader("⚡ Top Strikes")

    if not strikes:
        st.warning("No strike data available yet.")
        return

    # Sort by absolute net gamma descending
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

    st.dataframe(top_df, width="stretch", height=600)


def render_signals(signals: list[dict]) -> None:
    """Display recent strategy signals."""
    st.subheader("📡 Recent Signals")

    if not signals:
        st.info("No signals generated yet. Start the orchestrator to generate signals.")
        return

    # Build display table
    sig_df = pd.DataFrame(
        [
            {
                "Time": s.get("timestamp", ""),
                "Strategy": s.get("strategy_id", ""),
                "Direction": s.get("direction", ""),
                "Confidence": f"{s.get('confidence', 0):.2f}",
                "Entry": f"${s.get('entry', 0):,.2f}",
                "Stop": f"${s.get('stop', 0):,.2f}",
                "Target": f"${s.get('target', 0):,.2f}",
                "Reason": s.get("reason", ""),
            }
            for s in signals
        ]
    )

    st.dataframe(sig_df, width="stretch", height=min(400, len(signals) * 35))


def render_status(state: dict | None, signals: list[dict]) -> None:
    """Footer / status message."""
    if state is None:
        st.info(
            "⏳ **Waiting for data…**  "
            "Start the Syngex orchestrator (`python3 main.py TSLA dashboard`) and the "
            "dashboard will update automatically."
        )
    else:
        last_updated = state.get("last_updated", "unknown")
        symbol = state.get("symbol", "???")
        stale = is_data_stale(state)
        if stale:
            st.warning(
                f"⚠️ Data may be stale (last update: {last_updated}). "
                f"Check that the orchestrator is running for **{symbol}**."
            )
        else:
            st.caption(f"Last updated: {last_updated}  |  Symbol: {symbol}")

        # Show strategy engine status
        engine_status = state.get("strategy_engine", {})
        if engine_status:
            signal_count = engine_status.get("signal_count", 0)
            registered = engine_status.get("registered_strategies", 0)
            st.caption(f"Strategy engine: {registered} strategies registered, {signal_count} signals produced")


# ---------------------------------------------------------------------------
# Main loop — auto-refresh
# ---------------------------------------------------------------------------

state = load_gex_state()
signals = load_signals(20)

if state is None:
    st.info(
        "⏳ **Waiting for data…**  "
        "Start the Syngex orchestrator (`python3 main.py TSLA dashboard`) and the "
        "dashboard will update automatically."
    )
    # Poll until data arrives
    while state is None:
        time.sleep(1)
        state = load_gex_state()
        signals = load_signals(20)

# All data loaded — render single-page Command Center layout
render_header(state)
render_metrics(state)

# 3-column grid
col1, col2, col3 = st.columns(3)

with col1:
    render_gamma_profile(state)

with col2:
    render_gamma_flip(state)

with col3:
    render_gamma_walls(state)

# Bottom full-width table
render_top_strikes(state)

# Recent signals
render_signals(signals)

# Status footer
render_status(state, signals)

# Auto-refresh loop
while True:
    time.sleep(POLL_INTERVAL)
    st.rerun()
