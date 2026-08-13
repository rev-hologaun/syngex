#!/usr/bin/env python3
"""
Per-strategy signal analysis v2 — focused on session × confidence cross-tabs.

Reads the _v2 signal OUTCOME files (signal_outcomes_*_v2.jsonl) written by the
v2 orchestrator. Outputs one table per strategy showing win rate, avg P&L, and
significance for each (session, confidence) cell, with symbol and regime
breakdowns.

Same analysis engine as analysis_v1.py, but ingests the _v2 outcome streams.
"""

import argparse
import glob
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("/home/hologaun/projects/syngex/log")
OUTPUT_FILE = Path("/home/hologaun/projects/syngex/analysis/analyzed_strategies_v2.md")

# Signal outcome files to ingest. v1 uses signal_outcomes_*.jsonl; v2 uses the
# _v2 variants so v1 and v2 streams are analyzed independently.
OUTCOME_GLOB = "signal_outcomes_*_v2.jsonl"

CONFIDENCE_BUCKETS = [
    ("1-4%",    0.01, 0.05),
    ("5-9%",    0.05, 0.10),
    ("10-19%",  0.10, 0.20),
    ("20-29%",  0.20, 0.30),
    ("30-39%",  0.30, 0.40),
    ("40-49%",  0.40, 0.50),
    ("50-59%",  0.50, 0.60),
    ("60-69%",  0.60, 0.70),
    ("70-79%",  0.70, 0.80),
    ("80-89%",  0.80, 0.90),
    ("90-99%",  0.90, 1.00),
    ("100%",    1.00, 1.10),
]

VALID_SESSIONS = {"ORB (9:30-10:00)", "Morning (10:00-12:00)", "Afternoon (12:00-16:00)"}
SESSION_ORDER = ["ORB (9:30-10:00)", "Morning (10:00-12:00)", "Afternoon (12:00-16:00)"]
CONF_ORDER = [label for label, _, _ in CONFIDENCE_BUCKETS]


# ── Helpers ──────────────────────────────────────────────────────────

def win_rate(w, l, c=0):
    """Win rate excluding CLOSED (time expired)."""
    resolved = w + l
    if resolved == 0:
        return 0.0
    return (w / resolved) * 100


def avg_pnl(pnl_list):
    if not pnl_list:
        return 0.0
    return sum(pnl_list) / len(pnl_list)


def binomial_z_score(win_rate_val, total, overall_wr):
    """Z-score of a win rate vs a baseline win rate.

    Returns (z_score, is_significant).
    """
    if total < 5:
        return 0.0, False
    se = math.sqrt(overall_wr * (1 - overall_wr) / total) if 0 < overall_wr < 1 else 0.01
    if se == 0:
        se = 0.01
    z = (win_rate_val - overall_wr) / se
    return round(z, 2), abs(z) > 1.645


def bucket_confidence(conf):
    for label, lo, hi in CONFIDENCE_BUCKETS:
        if lo <= conf < hi:
            return label
    return "Other"


def extract_signal_timestamp(sig):
    """Extract epoch-second timestamp from signal_id (second-to-last underscore part)."""
    sid = sig.get("signal_id", "")
    parts = sid.split("_")
    if len(parts) < 2:
        return 0.0
    ts_part = parts[-2]
    if ts_part.isdigit() and len(ts_part) >= 10:
        ts_ms = int(ts_part)
        return ts_ms / 1000.0 if ts_ms > 1e12 else float(ts_ms)
    return 0.0


def signal_et_hour(signal_epoch):
    if signal_epoch <= 0:
        return 0.0
    et_epoch = signal_epoch - 4 * 3600
    return (et_epoch % 86400) / 3600.0


def signal_time_window_label(signal_epoch):
    if signal_epoch <= 0:
        return "Overnight"
    et_hour = signal_et_hour(signal_epoch)
    if et_hour < 9.5:
        return "Pre-market"
    elif et_hour < 10.0:
        return "ORB (9:30-10:00)"
    elif et_hour < 12.0:
        return "Morning (10:00-12:00)"
    elif et_hour < 16.0:
        return "Afternoon (12:00-16:00)"
    elif et_hour < 20.0:
        return "After-hours (16:00-20:00)"
    return "Overnight"


def fmt_num(v, decimals=3):
    return f"{v:,.{decimals}f}"


def fmt_pct(v):
    return f"{v:.1f}%"


def fmt_pnl(v):
    if v >= 0:
        return f"+${v:,.2f}"
    return f"-${abs(v):,.2f}"


# ── Data Loading ─────────────────────────────────────────────────────

def load_all_outcomes(confidence_min=0.05, symbols=None):
    """Load all signal outcome files, applying filters."""
    all_signals = []
    files = sorted(glob.glob(str(LOG_DIR / OUTCOME_GLOB)))
    sym_set = set(symbols.split(",")) if symbols else None
    for f in files:
        # Filenames are signal_outcomes_{SYMBOL}_v2.jsonl -> strip prefix and
        # trailing _v2 to recover the symbol (e.g. TSLA_v2 -> TSLA).
        symbol = Path(f).stem.replace("signal_outcomes_", "")
        if symbol.endswith("_v2"):
            symbol = symbol[:-3]
        if sym_set and symbol not in sym_set:
            continue
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    rec["_symbol"] = symbol
                    if rec.get("confidence", 0.0) < confidence_min:
                        continue
                    all_signals.append(rec)
                except json.JSONDecodeError:
                    continue
    return all_signals


# ── Analysis ─────────────────────────────────────────────────────────

def analyze_strategy(signals):
    """Analyze a single strategy. Returns per-strategy accumulators."""
    results = {}

    for sig in signals:
        sig_ts = extract_signal_timestamp(sig)
        sw_label = signal_time_window_label(sig_ts)
        if sw_label not in VALID_SESSIONS:
            continue

        sid = sig["strategy_id"]
        if sid not in results:
            results[sid] = {
                "total": 0, "wins": 0, "losses": 0, "closed": 0,
                "pnl_list": [], "symbols": set(),
                "direction": {"LONG": {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0},
                              "SHORT": {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}},
                # session × confidence × regime
                "session_conf_regime": defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
                    "total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0, "symbols": set()
                }))),
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
        r["pnl_list"].append(pnl)

        conf = sig.get("confidence", 0.5)
        cb = bucket_confidence(conf)
        direction = sig.get("direction", "UNKNOWN")
        meta = sig.get("metadata", {})
        regime = meta.get("regime", "UNKNOWN")
        regime_key = "POSITIVE" if regime == "POSITIVE" else ("NEGATIVE" if regime == "NEGATIVE" else "MIXED")

        # Direction accumulators
        dp = r["direction"][direction]
        dp["total"] += 1
        if outcome == "WIN": dp["wins"] += 1
        elif outcome == "LOSS": dp["losses"] += 1
        elif outcome == "CLOSED": dp["closed"] += 1
        dp["pnl"] += pnl

        # Session × Confidence × Regime cell
        cell = r["session_conf_regime"][sw_label][cb][regime_key]
        cell["total"] += 1
        if outcome == "WIN": cell["wins"] += 1
        elif outcome == "LOSS": cell["losses"] += 1
        elif outcome == "CLOSED": cell["closed"] += 1
        cell["pnl"] += pnl
        cell["symbols"].add(sig["_symbol"])

    return results


def compute_global_baselines(strategy_results):
    """Compute 3 global baseline tables needed for Δ calculation.

    Returns:
      global_conf: {bucket: {total, wins, losses, closed, wr}}
      global_session: {session: {total, wins, losses, closed, wr}}
      global_session_conf: {(session, bucket): {total, wins, losses, closed, wr}}
    """
    global_conf = {}
    for label, lo, hi in CONFIDENCE_BUCKETS:
        global_conf[label] = {"total": 0, "wins": 0, "losses": 0, "closed": 0}

    global_session = {s: {"total": 0, "wins": 0, "losses": 0, "closed": 0} for s in SESSION_ORDER}
    global_session_conf = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0})

    for sid, r in strategy_results.items():
        for session, buckets in r.get("session_conf_regime", {}).items():
            if session not in global_session:
                continue
            for conf_label, regimes in buckets.items():
                # Aggregate across regimes
                total = 0
                wins = 0
                losses = 0
                closed = 0
                for reg_data in regimes.values():
                    total += reg_data["total"]
                    wins += reg_data["wins"]
                    losses += reg_data["losses"]
                    closed += reg_data["closed"]
                if total == 0:
                    continue

                # Global confidence
                gc = global_conf.get(conf_label)
                if gc:
                    gc["total"] += total
                    gc["wins"] += wins
                    gc["losses"] += losses
                    gc["closed"] += closed

                # Global session
                gs = global_session[session]
                gs["total"] += total
                gs["wins"] += wins
                gs["losses"] += losses
                gs["closed"] += closed

                # Global session × confidence
                gsc = global_session_conf[(session, conf_label)]
                gsc["total"] += total
                gsc["wins"] += wins
                gsc["losses"] += losses
                gsc["closed"] += closed

    # Compute WRs
    for label, data in global_conf.items():
        data["wr"] = win_rate(data["wins"], data["losses"], data["closed"])

    for session, data in global_session.items():
        data["wr"] = win_rate(data["wins"], data["losses"], data["closed"])

    for key, data in global_session_conf.items():
        data["wr"] = win_rate(data["wins"], data["losses"], data["closed"])

    return global_conf, global_session, global_session_conf


# ── Report Generation ────────────────────────────────────────────────

def table_header(cols, widths=None):
    if widths is None:
        widths = [len(c) for c in cols]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header = "|" + "|".join(f" {c:<{w}} " for c, w in zip(cols, widths)) + "|"
    return header + "\n" + sep


def table_row(values, widths):
    cells = [f" {str(v):<{w}} " for v, w in zip(values, widths)]
    return "|" + "|".join(cells) + "|"


def regime_label(regimes_present):
    """Return regime display: POSITIVE, NEGATIVE, or MIXED."""
    if len(regimes_present) == 1:
        return next(iter(regimes_present))
    return "MIXED"


def generate_report(all_signals, strategy_results, global_conf, global_session, global_session_conf, min_n=50, wr_min=0.0):
    """Generate the markdown report."""
    lines = []
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    total_wins = sum(r["wins"] for r in strategy_results.values())
    total_losses = sum(r["losses"] for r in strategy_results.values())
    total_closed = sum(r["closed"] for r in strategy_results.values())
    all_pnl = [s.get("pnl", 0) for s in all_signals]

    lines.append("# Strategy Performance Analysis — Session × Confidence (v2)")
    lines.append("")
    lines.append(f"**Date:** {report_date}  |  **Generated:** {report_time}  |  **Total Signals:** {len(all_signals):,}  |  **Strategies:** {len(strategy_results)}  |  **Min Cell N:** {min_n}  |  **Min Win Rate:** {wr_min:.0%}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Global Baselines ───────────────────────────────────────────
    lines.append("## Global Baselines")
    lines.append("")

    # Table 1: Overall WR by confidence bucket
    lines.append("### Overall Win Rate by Confidence Bucket")
    lines.append("")
    widths = [12, 8, 6, 6, 6, 9]
    h = table_header(["Bucket", "Total", "Wins", "Losses", "Closed", "Win Rate"], widths)
    lines.append(h)
    for label, lo, hi in CONFIDENCE_BUCKETS:
        gc = global_conf[label]
        if gc["total"] >= min_n:
            lines.append(table_row([label, gc["total"], gc["wins"], gc["losses"], gc["closed"],
                                   f"{gc['wr']:.1f}%"], widths))
    lines.append("")

    # Table 2: WR by session
    lines.append("### Win Rate by Session")
    lines.append("")
    widths = [22, 8, 6, 6, 6, 9]
    h = table_header(["Session", "Total", "Wins", "Losses", "Closed", "Win Rate"], widths)
    lines.append(h)
    for s in SESSION_ORDER:
        gs = global_session[s]
        if gs["total"] >= min_n:
            lines.append(table_row([s, gs["total"], gs["wins"], gs["losses"], gs["closed"],
                                   f"{gs['wr']:.1f}%"], widths))
    lines.append("")

    # Table 3: WR by session × confidence
    lines.append("### Win Rate by Session × Confidence")
    lines.append("")
    widths = [22, 12, 8, 6, 6, 6, 9]
    h = table_header(["Session", "Confidence", "Total", "Wins", "Losses", "Closed", "Win Rate"], widths)
    lines.append(h)
    for sk in SESSION_ORDER:
        for cb_label in CONF_ORDER:
            gsc = global_session_conf.get((sk, cb_label))
            if gsc and gsc["total"] >= min_n:
                lines.append(table_row([sk, cb_label, gsc["total"], gsc["wins"], gsc["losses"], gsc["closed"],
                                       f"{gsc['wr']:.1f}%"], widths))
    lines.append("")

    lines.append("---")
    lines.append("")

    # ── Per-Strategy Tables ────────────────────────────────────────
    lines.append("## Per-Strategy Analysis")
    lines.append("")

    for sid in sorted(strategy_results.keys()):
        r = strategy_results[sid]
        total = r["total"]
        wr = win_rate(r["wins"], r["losses"], r["closed"])
        avg_p = avg_pnl(r["pnl_list"])
        symbols_str = ", ".join(sorted(r["symbols"]))

        # Direction stats
        long_data = r["direction"].get("LONG", {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0})
        short_data = r["direction"].get("SHORT", {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0})
        long_wr = win_rate(long_data["wins"], long_data["losses"], long_data["closed"])
        short_wr = win_rate(short_data["wins"], short_data["losses"], short_data["closed"])

        # Summary line
        lines.append(f"### {sid}")
        lines.append("")
        lines.append(
            f"**Symbols:** {symbols_str}  |  "
            f"**Total Signals:** {total:,}  |  "
            f"**Overall WR:** {wr:.1f}%  |  "
            f"**Overall Avg P&L:** {fmt_pnl(avg_p)}  |  "
            f"**Direction:** LONG WR {long_wr:.1f}% ({long_data['wins']}W/{long_data['losses']}L)  |  "
            f"SHORT WR {short_wr:.1f}% ({short_data['wins']}W/{short_data['losses']}L)"
        )
        lines.append("")

        # Build cross-tab rows
        rows = []
        for session in SESSION_ORDER:
            buckets = r["session_conf_regime"].get(session, {})
            for conf_label in CONF_ORDER:
                regimes = buckets.get(conf_label, {})
                # Merge across regimes
                cell_total = 0
                cell_wins = 0
                cell_losses = 0
                cell_closed = 0
                cell_pnl = 0.0
                cell_symbols = set()
                cell_regimes = set()
                for reg_key, reg_data in regimes.items():
                    cell_total += reg_data["total"]
                    cell_wins += reg_data["wins"]
                    cell_losses += reg_data["losses"]
                    cell_closed += reg_data["closed"]
                    cell_pnl += reg_data["pnl"]
                    cell_symbols |= reg_data["symbols"]
                    cell_regimes.add(reg_key)

                if cell_total < min_n:
                    continue

                cell_wr = win_rate(cell_wins, cell_losses, cell_closed)
                if cell_wr < wr_min * 100:
                    continue
                cell_avg_pnl = cell_pnl / (cell_wins + cell_losses) if (cell_wins + cell_losses) > 0 else 0.0

                # Δ vs global baseline for this session × confidence
                gsc = global_session_conf.get((session, conf_label))
                if gsc and gsc["total"] >= min_n:
                    delta = cell_wr - gsc["wr"]
                    z_score, is_sig = binomial_z_score(cell_wr, cell_total, gsc["wr"])
                    sig_flag = "🟢" if is_sig and z_score > 0 else "🔴"
                else:
                    delta = 0.0
                    sig_flag = "—"

                rows.append({
                    "session": session,
                    "confidence": conf_label,
                    "symbols": ", ".join(sorted(cell_symbols)),
                    "regime": regime_label(cell_regimes),
                    "total": cell_total,
                    "wins": cell_wins,
                    "losses": cell_losses,
                    "closed": cell_closed,
                    "wr": cell_wr,
                    "avg_pnl": cell_avg_pnl,
                    "delta": delta,
                    "sig_flag": sig_flag,
                    "z_score": z_score,
                })

        # Sort: 🟢 first, then by WR descending
        rows.sort(key=lambda x: (0 if x["sig_flag"] == "🟢" else 1, -x["wr"]))

        if rows:
            # Print table
            widths = [22, 12, 14, 10, 5, 5, 6, 6, 8, 10, 8, 10]
            h = table_header(["Session", "Confidence", "Symbols", "Regime", "N", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L", "Δ vs Global", "Significance"], widths)
            lines.append(h)
            for row in rows:
                lines.append(table_row([
                    row["session"],
                    row["confidence"],
                    row["symbols"],
                    row["regime"],
                    row["total"],
                    row["wins"],
                    row["losses"],
                    row["closed"],
                    f"{row['wr']:.1f}%",
                    fmt_pnl(row["avg_pnl"]),
                    f"{row['delta']:+.1f}pp",
                    row["sig_flag"],
                ], widths))
            lines.append("")
        else:
            if wr_min > 0:
                lines.append("_No cells meet the win rate threshold._")
            else:
                lines.append("_No cells meet the minimum sample threshold._")
            lines.append("")

        # Direction summary (always printed)
        lines.append("**Direction Summary:**")
        lines.append("")
        for dname, ddata in [("LONG", long_data), ("SHORT", short_data)]:
            dwr = win_rate(ddata["wins"], ddata["losses"], ddata["closed"])
            dap = ddata["pnl"] / (ddata["wins"] + ddata["losses"]) if (ddata["wins"] + ddata["losses"]) > 0 else 0.0
            lines.append(f"- **{dname}:** {ddata['total']} signals, WR {dwr:.1f}%, Avg P&L {fmt_pnl(dap)}")
        lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Per-strategy signal analysis v2 (reads signal_outcomes_*_v2.jsonl)")
    parser.add_argument("--min-n", type=int, default=50, help="Minimum signals per cell (default: 50)")
    parser.add_argument("--wr-min", type=float, default=0.0, help="Min WR threshold as decimal (e.g. 0.50). Default 0.0 = no filter.")
    parser.add_argument("--confidence-min", type=float, default=0.01, help="Overall confidence floor (default: 0.01)")
    parser.add_argument("--symbols", type=str, default=None, help="Comma-separated symbol filter (e.g. 'SPY,NVDA,TSLA')")
    parser.add_argument("--output", type=str, default=None, help="Override output path")
    args = parser.parse_args()

    output_path = Path(args.output) if args.output else OUTPUT_FILE

    print(f"Loading signals (confidence ≥ {args.confidence_min})...", file=sys.stderr)
    all_signals = load_all_outcomes(confidence_min=args.confidence_min, symbols=args.symbols)
    print(f"Loaded {len(all_signals):,} signals", file=sys.stderr)

    print("Analyzing strategies...", file=sys.stderr)
    strategy_results = analyze_strategy(all_signals)
    print(f"Found {len(strategy_results)} strategies", file=sys.stderr)

    print("Computing global baselines...", file=sys.stderr)
    global_conf, global_session, global_session_conf = compute_global_baselines(strategy_results)

    print(f"Generating report (min-n={args.min_n})...", file=sys.stderr)
    report = generate_report(all_signals, strategy_results, global_conf, global_session, global_session_conf, min_n=args.min_n, wr_min=args.wr_min)

    output_path.write_text(report)
    print(f"\n✅ Report written to {output_path}", file=sys.stderr)

    # Print summary stats to stderr
    total_wins = sum(r["wins"] for r in strategy_results.values())
    total_losses = sum(r["losses"] for r in strategy_results.values())
    print(f"Total resolved: {total_wins + total_losses:,} | WR: {win_rate(total_wins, total_losses):.1f}%", file=sys.stderr)


if __name__ == "__main__":
    main()
