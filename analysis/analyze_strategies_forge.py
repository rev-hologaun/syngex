#!/usr/bin/env python3
"""
Comprehensive per-strategy performance analysis for Round 3 validation.
Analyzes all signal_outcomes_*.jsonl files across all symbols.
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

LOG_DIR = Path("/home/hologaun/projects/syngex/log")
OUTPUT_FILE = Path("/home/hologaun/projects/syngex/analysis/analyzed_strategies_forge.md")

# ── Time window definitions ──────────────────────────────────────────
# Market opens at 9:30 AM PT. Timestamps are epoch seconds.
# We detect the first signal timestamp as "market open" for each symbol.
TIME_WINDOWS = {
    "ORB (9:30-10:00)":  (0,   30*60),    # 0-30 min
    "Early (10:00-11:30)": (30*60, 90*60),  # 30-90 min
    "Mid-day (11:30-14:00)": (90*60, 240*60), # 90-240 min
    "Late (14:00-16:00)": (240*60, 480*60),  # 240-480 min
}

CONFIDENCE_BUCKETS = [
    ("10-19%",  0.10, 0.20),
    ("20-29%",  0.20, 0.30),
    ("30-39%",  0.30, 0.40),
    ("40-49%",  0.40, 0.50),
    ("50-59%",  0.50, 0.60),
    ("60-69%",  0.60, 0.70),
    ("70-79%",  0.70, 0.80),
    ("80-89%",  0.80, 0.90),
    ("90-99%",  0.90, 1.00),
    ("100%",    1.00, 1.01),
]

TREND_MAP = {
    "UP": "Trending (Up)",
    "DOWN": "Trending (Down)",
    "FLAT": "Sideways",
}

REGIME_MAP = {
    "POSITIVE": "Positive Gamma (Range-Bound friendly)",
    "NEGATIVE": "Negative Gamma (Volatile/Breakout friendly)",
}


def load_all_outcomes():
    """Load all signal outcome files."""
    all_signals = []
    import glob
    files = sorted(glob.glob(str(LOG_DIR / "signal_outcomes_*.jsonl")))
    for f in files:
        symbol = Path(f).stem.replace("signal_outcomes_", "")
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    rec["_symbol"] = symbol
                    all_signals.append(rec)
                except json.JSONDecodeError:
                    continue
    return all_signals


def bucket_confidence(conf):
    """Return confidence bucket label."""
    for label, lo, hi in CONFIDENCE_BUCKETS:
        if lo <= conf < hi:
            return label
    return "Other"


def time_window_label(hold_time_sec, resolution_time_sec, first_ts):
    """Determine which time window a signal falls into based on resolution time."""
    elapsed = resolution_time_sec - first_ts
    for label, (lo, hi) in TIME_WINDOWS.items():
        if lo <= elapsed < hi:
            return label
    return "Post-close / Unknown"


def analyze_strategy(signals):
    """Analyze a single strategy across all symbols."""
    results = {}
    
    for sig in signals:
        sid = sig["strategy_id"]
        if sid not in results:
            results[sid] = {
                "total": 0,
                "wins": 0,
                "losses": 0,
                "closed": 0,
                "total_pnl": 0.0,
                "total_pnl_pct": 0.0,
                "avg_hold_time": 0.0,
                "confidence_buckets": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0, "pnl_pct": 0.0}),
                "trend_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "regime_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "time_window_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "direction_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "hold_time_buckets": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "symbols": set(),
                "pnl_list": [],
                "hold_times": [],
            }
        
        r = results[sid]
        r["total"] += 1
        r["symbols"].add(sig["_symbol"])
        
        outcome = sig.get("outcome", "UNKNOWN")
        if outcome == "WIN":
            r["wins"] += 1
        elif outcome == "LOSS":
            r["losses"] += 1
        elif outcome == "CLOSED":
            r["closed"] += 1
        
        pnl = sig.get("pnl", 0.0)
        pnl_pct = sig.get("pnl_pct", 0.0)
        r["total_pnl"] += pnl
        r["total_pnl_pct"] += pnl_pct
        r["pnl_list"].append(pnl)
        
        hold = sig.get("hold_time", 0.0)
        r["hold_times"].append(hold)
        
        # Confidence bucket
        conf = sig.get("confidence", 0.5)
        cb = bucket_confidence(conf)
        cb_data = r["confidence_buckets"][cb]
        cb_data["total"] += 1
        if outcome == "WIN": cb_data["wins"] += 1
        elif outcome == "LOSS": cb_data["losses"] += 1
        elif outcome == "CLOSED": cb_data["closed"] += 1
        cb_data["pnl"] += pnl
        cb_data["pnl_pct"] += pnl_pct
        
        # Trend
        meta = sig.get("metadata", {})
        trend = meta.get("trend", "UNKNOWN")
        trend_key = TREND_MAP.get(trend, trend)
        tp = r["trend_perf"][trend_key]
        tp["total"] += 1
        if outcome == "WIN": tp["wins"] += 1
        elif outcome == "LOSS": tp["losses"] += 1
        elif outcome == "CLOSED": tp["closed"] += 1
        tp["pnl"] += pnl
        
        # Regime
        regime = meta.get("regime", "UNKNOWN")
        regime_key = REGIME_MAP.get(regime, regime)
        rp = r["regime_perf"][regime_key]
        rp["total"] += 1
        if outcome == "WIN": rp["wins"] += 1
        elif outcome == "LOSS": rp["losses"] += 1
        elif outcome == "CLOSED": rp["closed"] += 1
        rp["pnl"] += pnl
        
        # Time window (use resolution_time - first_ts approximation)
        # We'll use hold_time as proxy for time-of-day grouping
        tw = "Unknown"
        if hold < 30*60:
            tw = "ORB / Early (0-30 min)"
        elif hold < 90*60:
            tw = "Early (30-90 min)"
        elif hold < 240*60:
            tw = "Mid-day (90-240 min)"
        elif hold < 480*60:
            tw = "Late (240-480 min)"
        else:
            tw = "Extended (>8h)"
        twp = r["time_window_perf"][tw]
        twp["total"] += 1
        if outcome == "WIN": twp["wins"] += 1
        elif outcome == "LOSS": twp["losses"] += 1
        elif outcome == "CLOSED": twp["closed"] += 1
        twp["pnl"] += pnl
        
        # Direction
        direction = sig.get("direction", "UNKNOWN")
        dp = r["direction_perf"][direction]
        dp["total"] += 1
        if outcome == "WIN": dp["wins"] += 1
        elif outcome == "LOSS": dp["losses"] += 1
        elif outcome == "CLOSED": dp["closed"] += 1
        dp["pnl"] += pnl
        
        # Hold time buckets
        if hold < 60:
            ht_key = "Very Fast (<1 min)"
        elif hold < 300:
            ht_key = "Fast (1-5 min)"
        elif hold < 900:
            ht_key = "Medium (5-15 min)"
        elif hold < 1800:
            ht_key = "Slow (15-30 min)"
        elif hold < 3600:
            ht_key = "Long (30-60 min)"
        else:
            ht_key = "Very Long (>1h)"
        htb = r["hold_time_buckets"][ht_key]
        htb["total"] += 1
        if outcome == "WIN": htb["wins"] += 1
        elif outcome == "LOSS": htb["losses"] += 1
        elif outcome == "CLOSED": htb["closed"] += 1
        htb["pnl"] += pnl
    
    return results


def win_rate(w, l, c):
    """Win rate excluding CLOSED (time expired)."""
    resolved = w + l
    if resolved == 0:
        return 0.0
    return (w / resolved) * 100


def avg_pnl(pnl_list):
    if not pnl_list:
        return 0.0
    return sum(pnl_list) / len(pnl_list)


def avg_hold(hold_times):
    if not hold_times:
        return 0.0
    return sum(hold_times) / len(hold_times)


def median_hold(hold_times):
    if not hold_times:
        return 0.0
    s = sorted(hold_times)
    n = len(s)
    if n % 2 == 0:
        return (s[n//2 - 1] + s[n//2]) / 2
    return s[n//2]


def fmt_pct(v):
    return f"{v:.1f}%"


def fmt_num(v, decimals=1):
    return f"{v:,.{decimals}f}"


def fmt_num_no_comma(v, decimals=2):
    return f"{v:.{decimals}f}"


def fmt_pnl(v):
    """Format P&L value for fixed-width display."""
    if v >= 0:
        return f" +${v:,.2f}"
    else:
        return f"-${abs(v):,.2f}"


def fmt_pct_cell(v):
    """Format percentage for fixed-width cell."""
    return f"{v:6.1f}%"


def fmt_count(v):
    """Format count for fixed-width cell."""
    return f"{v:>5}"


def fmt_pct_pct(v):
    """Format P&L% for fixed-width cell."""
    return f"{v:7.1f}%"


def table_header(cols, widths=None):
    """Build a fixed-width table header.
    cols: list of column name strings.
    widths: optional list of column widths (defaults to len of each col name).
    """
    if widths is None:
        widths = [len(c) for c in cols]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header = "|" + "|".join(f" {c:<{w}} " for c, w in zip(cols, widths)) + "|"
    return header + "\n" + sep  # no trailing newline — data rows follow immediately


def table_row(values, widths):
    """Build a fixed-width table row."""
    cells = []
    for v, w in zip(values, widths):
        cells.append(f" {str(v):<{w}} ")
    return "|" + "|".join(cells) + "|"


def generate_report(all_signals, strategy_results):
    """Generate the markdown report with fixed-width tables."""
    lines = []
    lines.append("# Strategy Performance Analysis — Round 3 Validation")
    lines.append("")
    lines.append(f"**Date:** 2026-05-06  |  **Total Resolved Signals:** {len(all_signals):,}  |  **Strategies Analyzed:** {len(strategy_results)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Overall Summary ──────────────────────────────────────────
    total_wins = sum(r["wins"] for r in strategy_results.values())
    total_losses = sum(r["losses"] for r in strategy_results.values())
    total_closed = sum(r["closed"] for r in strategy_results.values())
    total_pnl = sum(r["total_pnl"] for r in strategy_results.values())
    all_pnl = [s.get("pnl", 0) for s in all_signals]

    lines.append("## Overall Summary")
    lines.append("")
    lines.append(table_header(["Metric", "Value"], [20, 60]))
    lines.append(table_row(["Total Resolved Signals", f"{len(all_signals):,}"], [20, 60]))
    lines.append(table_row(["Total Wins", f"{total_wins:,}"], [20, 60]))
    lines.append(table_row(["Total Losses", f"{total_losses:,}"], [20, 60]))
    lines.append(table_row(["Time-Expired (CLOSED)", f"{total_closed:,}"], [20, 60]))
    lines.append(table_row(["Overall Win Rate", f"{win_rate(total_wins, total_losses, total_closed):.1f}%"], [20, 60]))
    lines.append(table_row(["Total P&L", f"${fmt_num_no_comma(total_pnl, 2)}"], [20, 60]))
    lines.append(table_row(["Avg P&L per Signal", f"${fmt_num_no_comma(avg_pnl(all_pnl))}"], [20, 60]))
    lines.append(table_row(["Symbols Traded", ", ".join(sorted(set(s["_symbol"] for s in all_signals)))], [20, 60]))
    lines.append("")

    # ── Per-Strategy Deep Dive ───────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Per-Strategy Deep Dive")
    lines.append("")

    for sid in sorted(strategy_results.keys()):
        r = strategy_results[sid]
        total = r["total"]
        wr = win_rate(r["wins"], r["losses"], r["closed"])
        avg_p = avg_pnl(r["pnl_list"])
        avg_h = avg_hold(r["hold_times"])
        med_h = median_hold(r["hold_times"])

        lines.append(f"### {sid}")
        lines.append("")
        lines.append(
            f"**Symbols:** {', '.join(sorted(r['symbols']))}  |  "
            f"**Total Signals:** {total:,}  |  "
            f"**Win Rate:** {wr:.1f}%  |  "
            f"**Avg P&L:** ${fmt_num(avg_p)}  |  "
            f"**Avg Hold:** {avg_h:.0f}s ({avg_h/60:.1f}m)  |  "
            f"**Median Hold:** {med_h:.0f}s"
        )
        lines.append("")

        # ── 1. Confidence Level Performance ──────────────────────
        lines.append("#### 1) Performance by Confidence Level")
        lines.append("")
        widths = [14, 5, 5, 6, 6, 9, 8, 8]
        h = table_header(["Confidence", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L", "Avg P&L%"], widths)
        lines.append(h)

        for label, lo, hi in CONFIDENCE_BUCKETS:
            cb = r["confidence_buckets"].get(label)
            if cb and cb["total"] > 0:
                cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                cap = cb["pnl"] / cb["total"] if cb["total"] > 0 else 0
                cpp = cb["pnl_pct"] / cb["total"] if cb["total"] > 0 else 0
                lines.append(table_row([label, cb["total"], cb["wins"], cb["losses"], cb["closed"],
                                       f"{cwr:.1f}%", f"${fmt_num(cap)}", f"{cpp:.1f}%"], widths))

        # Any "Other" bucket
        for label, cb in r["confidence_buckets"].items():
            if label not in [l for l, _, _ in CONFIDENCE_BUCKETS] and cb["total"] > 0:
                cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                cap = cb["pnl"] / cb["total"] if cb["total"] > 0 else 0
                cpp = cb["pnl_pct"] / cb["total"] if cb["total"] > 0 else 0
                lines.append(table_row([label, cb["total"], cb["wins"], cb["losses"], cb["closed"],
                                       f"{cwr:.1f}%", f"${fmt_num(cap)}", f"{cpp:.1f}%"], widths))

        lines.append("")

        # ── 2. Market Type Performance ───────────────────────────
        lines.append("#### 2) Performance by Market Type")
        lines.append("")
        widths = [20, 5, 5, 6, 6, 9, 8]
        h = table_header(["Market Type", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for mk in sorted(r["trend_perf"].keys()):
            tp = r["trend_perf"][mk]
            if tp["total"] > 0:
                twr = win_rate(tp["wins"], tp["losses"], tp["closed"])
                tap = tp["pnl"] / tp["total"]
                lines.append(table_row([mk, tp["total"], tp["wins"], tp["losses"], tp["closed"],
                                       f"{twr:.1f}%", f"${fmt_num(tap)}"], widths))

        lines.append("")
        lines.append("**Regime Performance:**")
        lines.append("")
        widths = [20, 5, 5, 6, 6, 9, 8]
        h = table_header(["Regime", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for rk in sorted(r["regime_perf"].keys()):
            rp = r["regime_perf"][rk]
            if rp["total"] > 0:
                rwr = win_rate(rp["wins"], rp["losses"], rp["closed"])
                rap = rp["pnl"] / rp["total"]
                lines.append(table_row([rk, rp["total"], rp["wins"], rp["losses"], rp["closed"],
                                       f"{rwr:.1f}%", f"${fmt_num(rap)}"], widths))

        lines.append("")

        # ── 3. Timeframe Performance ─────────────────────────────
        lines.append("#### 3) Performance by Timeframe (Hold Duration)")
        lines.append("")
        widths = [22, 5, 5, 6, 6, 9, 8]
        h = table_header(["Timeframe", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for tk in sorted(r["time_window_perf"].keys()):
            twp = r["time_window_perf"][tk]
            if twp["total"] > 0:
                twr = win_rate(twp["wins"], twp["losses"], twp["closed"])
                tap = twp["pnl"] / twp["total"]
                lines.append(table_row([tk, twp["total"], twp["wins"], twp["losses"], twp["closed"],
                                       f"{twr:.1f}%", f"${fmt_num(tap)}"], widths))

        lines.append("")

        # ── 4. Direction Performance ─────────────────────────────
        lines.append("#### 4) Performance by Direction")
        lines.append("")
        widths = [12, 5, 5, 6, 6, 9, 8]
        h = table_header(["Direction", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for dk in sorted(r["direction_perf"].keys()):
            dp = r["direction_perf"][dk]
            if dp["total"] > 0:
                dwr = win_rate(dp["wins"], dp["losses"], dp["closed"])
                dap = dp["pnl"] / dp["total"]
                lines.append(table_row([dk, dp["total"], dp["wins"], dp["losses"], dp["closed"],
                                       f"{dwr:.1f}%", f"${fmt_num(dap)}"], widths))

        lines.append("")

        # ── 5. Hold Time Distribution ────────────────────────────
        lines.append("#### 5) Hold Time Distribution")
        lines.append("")
        widths = [22, 5, 5, 6, 6, 9, 8]
        h = table_header(["Hold Time", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for hk in sorted(r["hold_time_buckets"].keys()):
            htb = r["hold_time_buckets"][hk]
            if htb["total"] > 0:
                hwr = win_rate(htb["wins"], htb["losses"], htb["closed"])
                hap = htb["pnl"] / htb["total"]
                lines.append(table_row([hk, htb["total"], htb["wins"], htb["losses"], htb["closed"],
                                       f"{hwr:.1f}%", f"${fmt_num(hap)}"], widths))

        lines.append("")

        # ── 6. Insights & Recommendations ────────────────────────
        lines.append("#### 6) Insights & Recommendations")
        lines.append("")

        insights = generate_insights(sid, r)
        for insight in insights:
            lines.append(f"- {insight}")
        lines.append("")

        lines.append("---")
        lines.append("")

    # ── Cross-Strategy Rankings ──────────────────────────────────
    lines.append("## Cross-Strategy Rankings")
    lines.append("")
    widths = [5, 24, 7, 8, 8, 16, 14, 14]
    lines.append(
        table_header(["Rank", "Strategy", "Signals", "Win Rate", "Avg P&L",
                      "Best Confidence", "Best Market", "Best Timeframe"], widths)
    )

    ranked = []
    for sid, r in strategy_results.items():
        wr = win_rate(r["wins"], r["losses"], r["closed"])
        avg_p = avg_pnl(r["pnl_list"])

        best_cb = None
        best_cb_wr = -1
        for label, cb in r["confidence_buckets"].items():
            if cb["total"] >= 5:
                cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                if cwr > best_cb_wr:
                    best_cb_wr = cwr
                    best_cb = label

        best_mt = None
        best_mt_wr = -1
        for mk, tp in r["trend_perf"].items():
            if tp["total"] >= 5:
                twr = win_rate(tp["wins"], tp["losses"], tp["closed"])
                if twr > best_mt_wr:
                    best_mt_wr = twr
                    best_mt = mk

        best_tf = None
        best_tf_wr = -1
        for tk, twp in r["time_window_perf"].items():
            if twp["total"] >= 5:
                twr = win_rate(twp["wins"], twp["losses"], twp["closed"])
                if twr > best_tf_wr:
                    best_tf_wr = twr
                    best_tf = tk

        ranked.append((sid, r["total"], wr, avg_p, best_cb, best_mt, best_tf))

    ranked.sort(key=lambda x: x[3], reverse=True)

    for i, (sid, total, wr, avg_p, best_cb, best_mt, best_tf) in enumerate(ranked, 1):
        lines.append(table_row([
            str(i), sid, f"{total:,}", f"{wr:.1f}%", f"${fmt_num(avg_p)}",
            best_cb or "N/A", best_mt or "N/A", best_tf or "N/A"
        ], widths))

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by Forge 🐙 — Round 3 Validation Analysis*")

    return "\n".join(lines)


def generate_insights(sid, r):
    """Generate qualitative insights for a strategy."""
    insights = []
    total = r["total"]
    wr = win_rate(r["wins"], r["losses"], r["closed"])
    avg_p = avg_pnl(r["pnl_list"])
    avg_h = avg_hold(r["hold_times"])
    
    # Win rate assessment
    if wr >= 65:
        insights.append(f"✅ Strong win rate of {wr:.1f}% — this strategy consistently picks directional moves.")
    elif wr >= 50:
        insights.append(f"⚖️ Moderate win rate of {wr:.1f}% — strategy works but needs tighter entry/exit or higher confidence thresholds.")
    else:
        insights.append(f"⚠️ Low win rate of {wr:.1f}% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.")
    
    # P&L assessment
    if avg_p > 0:
        insights.append(f"💰 Positive avg P&L of ${avg_p:.2f} per signal — profitable even with {wr:.1f}% win rate (good risk/reward).")
    else:
        insights.append(f"📉 Negative avg P&L of ${avg_p:.2f} per signal — losses outweigh wins. Review stop-loss placement and entry timing.")
    
    # Confidence analysis
    best_cb = None
    best_cb_wr = -1
    for label, cb in r["confidence_buckets"].items():
        if cb["total"] >= 5:
            cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
            if cwr > best_cb_wr:
                best_cb_wr = cwr
                best_cb = label
    if best_cb:
        insights.append(f"🎯 Best performance at {best_cb} confidence ({best_cb_wr:.1f}% win rate) — consider raising minimum confidence threshold.")
    
    # Worst confidence
    worst_cb = None
    worst_cb_wr = 101
    for label, cb in r["confidence_buckets"].items():
        if cb["total"] >= 5:
            cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
            if cwr < worst_cb_wr:
                worst_cb_wr = cwr
                worst_cb = label
    if worst_cb:
        insights.append(f"🚫 Worst at {worst_cb} ({worst_cb_wr:.1f}% win rate) — signals in this range may be noise. Consider filtering them out.")
    
    # Market type
    best_mt = None
    best_mt_pnl = -999999
    for mk, tp in r["trend_perf"].items():
        if tp["total"] >= 5:
            tap = tp["pnl"] / tp["total"]
            if tap > best_mt_pnl:
                best_mt_pnl = tap
                best_mt = mk
    if best_mt:
        insights.append(f"📈 Best market type: {best_mt} (avg P&L ${best_mt_pnl:.2f}) — this strategy thrives in {best_mt.lower()} conditions.")
    
    # Timeframe
    best_tf = None
    best_tf_pnl = -999999
    for tk, twp in r["time_window_perf"].items():
        if twp["total"] >= 5:
            tap = twp["pnl"] / twp["total"]
            if tap > best_tf_pnl:
                best_tf_pnl = tap
                best_tf = tk
    if best_tf:
        insights.append(f"⏰ Best timeframe: {best_tf} (avg P&L ${best_tf_pnl:.2f}) — optimal hold duration is {best_tf}.")
    
    # Hold time
    if avg_h > 600:
        insights.append(f"⏱️ Long avg hold time ({avg_h:.0f}s / {avg_h/60:.1f}m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.")
    elif avg_h < 60:
        insights.append(f"⚡ Very fast avg hold time ({avg_h:.0f}s) — strategy captures quick moves. Ensure slippage/commissions don't eat into thin margins.")
    
    # CLOSED signals
    closed_pct = (r["closed"] / total * 100) if total > 0 else 0
    if closed_pct > 30:
        insights.append(f"⏳ {closed_pct:.0f}% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.")
    
    return insights


def main():
    print("Loading all signal outcomes...")
    all_signals = load_all_outcomes()
    print(f"Loaded {len(all_signals):,} resolved signals")
    
    print("Analyzing strategies...")
    strategy_results = analyze_strategy(all_signals)
    print(f"Found {len(strategy_results)} unique strategies")
    
    print("Generating report...")
    report = generate_report(all_signals, strategy_results)
    
    # Write to file
    OUTPUT_FILE.write_text(report)
    print(f"\n✅ Report written to {OUTPUT_FILE}")
    
    # Also print to stdout
    print("\n" + "=" * 80)
    print(report)


if __name__ == "__main__":
    main()
