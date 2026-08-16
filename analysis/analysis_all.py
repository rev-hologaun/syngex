#!/usr/bin/env python3
"""
Unified per-strategy signal analysis — all strategy versions, session-sliced.

Reads EVERY signal_outcomes_*.jsonl stream (raw, _v2, and any future _v3/_v4...)
via a streaming generator, so memory stays flat even on multi-GB outcome files.
The strategy version is derived from the strategy_id suffix (_v2, _v3, ...), so
new strategy versions show up automatically.

Report structure:
  * 7 sessions: ORB (9:30-10:00) + six 1-hour buckets (10-16 ET).
  * Per-strategy tables bucketed by (session, confidence), filtered to cells
    above a win-rate floor (default 50%) with a minimum sample per cell.
  * A per-base-strategy V1-vs-V2 (vs V3...) rollup: side-by-side WR / N /
    expectancy / avg P&L, so "did the newer version actually improve it?"
    is answered at a glance.
  * Global version footer: aggregate WR / expectancy per strategy version.

Strategies are kept in alphabetical order within each version section so the
original + V2 + any future V* are directly comparable.

Modes:
  * default: one detail section filtered to the WR floor (default 50%).
  * --both: emits the detail twice — strict WR>=floor ("tradeable") and a
    "exploration" view with no WR cut — so you can compare in one file.
"""

import argparse
import glob
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("/home/hologaun/projects/syngex/log")
OUTPUT_FILE = Path("/home/hologaun/projects/syngex/analysis/analyzed_all.md")

# Match every outcome stream, including _v2/_v3/etc filename variants.
OUTCOME_GLOB = "signal_outcomes_*.jsonl"

CONFIDENCE_BUCKETS = [
    ("1-9%",    0.01, 0.10),
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

# 7 sessions: ORB + six hourly buckets ending at the 16:00 close.
VALID_SESSIONS = {
    "ORB (9:30-10:00)",
    "Hour 1 (10-11)",
    "Hour 2 (11-12)",
    "Hour 3 (12-13)",
    "Hour 4 (13-14)",
    "Hour 5 (14-15)",
    "Hour 6 (15-16)",
}
SESSION_ORDER = [
    "ORB (9:30-10:00)",
    "Hour 1 (10-11)",
    "Hour 2 (11-12)",
    "Hour 3 (12-13)",
    "Hour 4 (13-14)",
    "Hour 5 (14-15)",
    "Hour 6 (15-16)",
]
CONF_ORDER = [label for label, _, _ in CONFIDENCE_BUCKETS]

# strategy_id suffix patterns: 'magnet_accelerate' -> (base, version=1),
# '	magnet_accelerate_v2' -> (base, version=2), '..._v10' -> version 10.
_VERSION_RE = re.compile(r"^(?P<base>.+?)_v(?P<ver>\d+)$")

DEFAULT_MIN_N_STRATEGY = 50   # strategy-level sample floor (report inclusion)
DEFAULT_MIN_N_CELL = 10       # per-cell granularity floor (still shows in table)
DEFAULT_WR_MIN = 0.50         # win-rate floor per cell

# ── Helpers ──────────────────────────────────────────────────────────

def split_strategy_id(sid):
    """Return (base_name, version). Version 1 if no _v{n} suffix."""
    m = _VERSION_RE.match(sid)
    if m:
        return m.group("base"), int(m.group("ver"))
    return sid, 1


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
    """Map an ET hour float to one of the 7 session labels (or out-of-session)."""
    if signal_epoch <= 0:
        return "Overnight"
    et_hour = signal_et_hour(signal_epoch)
    if et_hour < 9.5:
        return "Pre-market"
    elif et_hour < 10.0:
        return "ORB (9:30-10:00)"
    elif et_hour < 11.0:
        return "Hour 1 (10-11)"
    elif et_hour < 12.0:
        return "Hour 2 (11-12)"
    elif et_hour < 13.0:
        return "Hour 3 (12-13)"
    elif et_hour < 14.0:
        return "Hour 4 (13-14)"
    elif et_hour < 15.0:
        return "Hour 5 (14-15)"
    elif et_hour < 16.0:
        return "Hour 6 (15-16)"
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


def expectancy(total, wins, losses, closed, pnl):
    """Net $ per resolved signal (excludes CLOSED / time-expired)."""
    resolved = wins + losses
    if resolved == 0:
        return 0.0
    return pnl / resolved


# ── Data Loading ─────────────────────────────────────────────────────

def load_all_outcomes(confidence_min=0.01, symbols=None):
    """Yield ALL signal outcomes (raw + _v2 + future V*) as a stream (generator).

    Streaming keeps memory flat instead of loading GBs of signals into a list.
    The version is derived from strategy_id, so every stream is kept.
    """
    files = sorted(glob.glob(str(LOG_DIR / OUTCOME_GLOB)))
    sym_set = set(symbols.split(",")) if symbols else None
    for f in files:
        # Filename is signal_outcomes_{SYMBOL}.jsonl or ..._{SYMBOL}_v2.jsonl.
        symbol = Path(f).stem.replace("signal_outcomes_", "")
        if "_v" in symbol:
            # strip trailing _v2/_v3 filename suffix to recover symbol
            symbol = _VERSION_RE.sub(lambda m: m.group("base"), symbol)
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
                    rec["_version"] = split_strategy_id(rec.get("strategy_id", ""))[1]
                    if rec.get("confidence", 0.0) < confidence_min:
                        continue
                    yield rec
                except json.JSONDecodeError:
                    continue


# ── Analysis ─────────────────────────────────────────────────────────

def analyze_strategy(signals):
    """Analyze every strategy (across all versions). Returns per-strategy accumulators."""
    results = {}

    for sig in signals:
        sig_ts = extract_signal_timestamp(sig)
        sw_label = signal_time_window_label(sig_ts)
        if sw_label not in VALID_SESSIONS:
            continue

        sid = sig["strategy_id"]
        base, version = split_strategy_id(sid)
        if sid not in results:
            results[sid] = {
                "base": base, "version": version,
                "total": 0, "wins": 0, "losses": 0, "closed": 0,
                "pnl": 0.0, "pnl_list": [], "symbols": set(),
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
        r["pnl"] += pnl
        r["pnl_list"].append(pnl)

        conf = sig.get("confidence", 0.5)
        cb = bucket_confidence(conf)
        direction = sig.get("direction", "UNKNOWN")
        meta = sig.get("metadata", {})
        regime = meta.get("regime", "UNKNOWN")
        regime_key = "POSITIVE" if regime == "POSITIVE" else ("NEGATIVE" if regime == "NEGATIVE" else "MIXED")

        # Direction accumulators
        if direction in r["direction"]:
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
    """Compute global baseline tables keyed by (session, version).

    Version is included so the ORB-heavy V2 stream doesn't skew the baseline a
    V1 strategy is compared against (and vice versa).
    """
    # globalConf[version][bucket]; globalSession[version][session];
    # globalSessionConf[version][(session, bucket)]; globalVersion[version]
    versions = sorted({r["version"] for r in strategy_results.values()})

    global_conf = {v: {l: {"total": 0, "wins": 0, "losses": 0, "closed": 0}
                       for l, _, _ in CONFIDENCE_BUCKETS} for v in versions}
    global_session = {v: {s: {"total": 0, "wins": 0, "losses": 0, "closed": 0}
                          for s in SESSION_ORDER} for v in versions}
    global_session_conf = {v: defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0})
                           for v in versions}
    global_version = {v: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0} for v in versions}

    for sid, r in strategy_results.items():
        ver = r["version"]
        # roll into version totals
        gv = global_version[ver]
        gv["total"] += r["total"]
        gv["wins"] += r["wins"]
        gv["losses"] += r["losses"]
        gv["closed"] += r["closed"]
        gv["pnl"] += r["pnl"]

        for session, buckets in r.get("session_conf_regime", {}).items():
            if session not in SESSION_ORDER:
                continue
            for conf_label, regimes in buckets.items():
                total = sum(rd["total"] for rd in regimes.values())
                wins = sum(rd["wins"] for rd in regimes.values())
                losses = sum(rd["losses"] for rd in regimes.values())
                closed = sum(rd["closed"] for rd in regimes.values())
                if total == 0:
                    continue
                gc = global_conf[ver].get(conf_label)
                if gc:
                    gc["total"] += total; gc["wins"] += wins
                    gc["losses"] += losses; gc["closed"] += closed
                gs = global_session[ver][session]
                gs["total"] += total; gs["wins"] += wins
                gs["losses"] += losses; gs["closed"] += closed
                gsc = global_session_conf[ver][(session, conf_label)]
                gsc["total"] += total; gsc["wins"] += wins
                gsc["losses"] += losses; gsc["closed"] += closed

    for v in versions:
        for d in global_conf[v].values():
            d["wr"] = win_rate(d["wins"], d["losses"], d["closed"])
        for s in global_session[v].values():
            s["wr"] = win_rate(s["wins"], s["losses"], s["closed"])
        for d in global_session_conf[v].values():
            d["wr"] = win_rate(d["wins"], d["losses"], d["closed"])
        gv = global_version[v]
        gv["wr"] = win_rate(gv["wins"], gv["losses"], gv["closed"])

    return versions, global_conf, global_session, global_session_conf, global_version


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


def generate_report(strategy_results, versions, global_conf, global_session,
                    global_session_conf, global_version, min_n_strategy=50,
                    min_n_cell=10, wr_min=0.50, include_sessions=True,
                    both_mode=False):
    """Generate the markdown report.

    If both_mode is True, emits the detail section twice: once at the strict
    (wr_min) floor and once at a loose floor (0.0 = no WR cut), so you can
    compare 'tradeable only' vs 'everything with decent sample' in one file.
    """
    lines = []
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    all_signals = sum(r["total"] for r in strategy_results.values())
    total_wins = sum(r["wins"] for r in strategy_results.values())
    total_losses = sum(r["losses"] for r in strategy_results.values())
    total_closed = sum(r["closed"] for r in strategy_results.values())
    total_pnl = sum(r["pnl"] for r in strategy_results.values())

    lines.append("# Unified Strategy Performance Analysis — All Versions")
    lines.append("")
    lines.append(
        f"**Date:** {report_date}  |  **Generated:** {report_time}  |  "
        f"**Total Signals:** {all_signals:,}  |  **Strategies:** {len(strategy_results)}  |  "
        f"**Min Strategy N:** {min_n_strategy}  |  **Min Cell N:** {min_n_cell}  |  "
        f"**Min Cell WR:** {wr_min:.0%}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Global Version Footer (top summary) ────────────────────────
    lines.append("## Summary Across Versions")
    lines.append("")
    widths = [10, 10, 7, 7, 7, 9, 12, 12]
    h = table_header(["Version", "Strategies", "Total", "Wins", "Losses", "Win Rate", "Net P&L", "Expectancy"], widths)
    lines.append(h)
    for v in versions:
        n_strat = sum(1 for r in strategy_results.values() if r["version"] == v)
        gv = global_version[v]
        exp = expectancy(gv["total"], gv["wins"], gv["losses"], gv["closed"], gv["pnl"])
        lines.append(table_row([
            f"V{v}", n_strat, gv["total"], gv["wins"], gv["losses"],
            f"{gv['wr']:.1f}%", fmt_pnl(gv["pnl"]), fmt_pnl(exp),
        ], widths))
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── V1-vs-V2 (and beyond) rollup per base strategy ─────────────
    lines.append("## Rollup: Base Strategy × Version")
    lines.append("")
    lines.append("≤50% WR cells are shown here regardless of the WR floor (this is the comparison view).")
    lines.append("")

    # group by base
    bases = defaultdict(list)
    for sid, r in strategy_results.items():
        bases[r["base"]].append(r)

    widths = [26, 8, 7, 6, 6, 9, 12, 12, 10]
    h = table_header(["Base Strategy", "Ver", "Total", "Wins", "Losses", "Win Rate", "Net P&L", "Expectancy", "LONG/SHORT"], widths)
    lines.append(h)
    for base in sorted(bases.keys()):
        for r in sorted(bases[base], key=lambda x: x["version"]):
            exp = expectancy(r["total"], r["wins"], r["losses"], r["closed"], r["pnl"])
            long_wr = win_rate(r["direction"]["LONG"]["wins"], r["direction"]["LONG"]["losses"], r["direction"]["LONG"]["closed"])
            short_wr = win_rate(r["direction"]["SHORT"]["wins"], r["direction"]["SHORT"]["losses"], r["direction"]["SHORT"]["closed"])
            ls = f"{long_wr:.0f}%L/{short_wr:.0f}%S"
            lines.append(table_row([
                base, f"V{r['version']}", r["total"], r["wins"], r["losses"],
                f"{win_rate(r['wins'], r['losses'], r['closed']):.1f}%",
                fmt_pnl(r["pnl"]), fmt_pnl(exp), ls,
            ], widths))
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Session Summary per version ────────────────────────────────
    if include_sessions:
        lines.append("## Session Win Rate by Version")
        lines.append("")
        for v in versions:
            lines.append(f"### Session WR — V{v}")
            lines.append("")
            widths = [22, 8, 6, 6, 6, 9]
            h = table_header(["Session", "Total", "Wins", "Losses", "Closed", "Win Rate"], widths)
            lines.append(h)
            for s in SESSION_ORDER:
                gs = global_session[v][s]
                if gs["total"] >= min_n_cell:
                    lines.append(table_row([s, gs["total"], gs["wins"], gs["losses"], gs["closed"],
                                           f"{gs['wr']:.1f}%"], widths))
            lines.append("")

    lines.append("---")
    lines.append("")

    # ── Per-Strategy Detail (alphabetical by base, then by version) ─
    if both_mode:
        # Strict (tradeable) then loose (exploration) detail in one file.
        lines.extend(_render_detail(
            strategy_results, global_session_conf, min_n_strategy, min_n_cell,
            wr_min, "## Per-Strategy Detail — Tradeable (WR ≥ {:.0%})".format(wr_min)))
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.extend(_render_detail(
            strategy_results, global_session_conf, min_n_strategy, min_n_cell,
            0.0, "## Per-Strategy Detail — Exploration (no WR cut)"))
    else:
        lines.extend(_render_detail(
            strategy_results, global_session_conf, min_n_strategy, min_n_cell,
            wr_min, "## Per-Strategy Detail"))

    return "\n".join(lines)


def _render_detail(strategy_results, global_session_conf, min_n_strategy,
                   min_n_cell, wr_min, heading):
    """Render the per-strategy detail section at a given WR floor.

    Returns a list of lines. Strategies are sorted alphabetically by base name,
    then by version. The strategy-level WR floor controls which strategies are
    included; the cell-level floor controls which confidence cells are shown.
    """
    lines = []
    lines.append(heading)
    lines.append("")

    def strategy_included(r, wr_min_cell, min_n_s):
        """Include a strategy if its overall WR >= floor and total >= min."""
        if r["total"] < min_n_s:
            return False
        return win_rate(r["wins"], r["losses"], r["closed"]) >= wr_min_cell * 100

    # sort strategies: alphabetically by base, then version asc
    ordered = sorted(strategy_results.values(), key=lambda r: (r["base"], r["version"]))

    printed_any = False
    for r in ordered:
        if not strategy_included(r, wr_min, min_n_strategy):
            continue
        printed_any = True
        total = r["total"]
        wr = win_rate(r["wins"], r["losses"], r["closed"])
        net_pnl = r["pnl"]
        exp = expectancy(total, r["wins"], r["losses"], r["closed"], net_pnl)
        avg_p = avg_pnl(r["pnl_list"])
        symbols_str = ", ".join(sorted(r["symbols"]))
        ver = r["version"]

        long_data = r["direction"]["LONG"]
        short_data = r["direction"]["SHORT"]
        long_wr = win_rate(long_data["wins"], long_data["losses"], long_data["closed"])
        short_wr = win_rate(short_data["wins"], short_data["losses"], short_data["closed"])
        long_exp = expectancy(long_data["total"], long_data["wins"], long_data["losses"], long_data["closed"], long_data["pnl"])
        short_exp = expectancy(short_data["total"], short_data["wins"], short_data["losses"], short_data["closed"], short_data["pnl"])

        lines.append(f"### {r['base']} (V{ver})")
        lines.append("")
        lines.append(
            f"**Symbols:** {symbols_str}  |  "
            f"**Total:** {total:,}  |  "
            f"**WR:** {wr:.1f}%  |  "
            f"**Net P&L:** {fmt_pnl(net_pnl)}  |  "
            f"**Expectancy:** {fmt_pnl(exp)}/signal  |  "
            f"**Avg P&L:** {fmt_pnl(avg_p)}"
        )
        lines.append("")
        lines.append(f"**Direction — LONG:** WR {long_wr:.1f}% ({long_data['wins']}W/{long_data['losses']}L), Exp {fmt_pnl(long_exp)}  |  "
                     f"**SHORT:** WR {short_wr:.1f}% ({short_data['wins']}W/{short_data['losses']}L), Exp {fmt_pnl(short_exp)}")
        lines.append("")

        # Optionally a per-session mini-view
        session_totals = {}
        for session in SESSION_ORDER:
            st = 0; sw = 0; sl = 0; sc = 0; sp = 0.0
            for cb_label in CONF_ORDER:
                regimes = r["session_conf_regime"][session].get(cb_label, {})
                for rd in regimes.values():
                    st += rd["total"]; sw += rd["wins"]; sl += rd["losses"]
                    sc += rd["closed"]; sp += rd["pnl"]
            if st > 0:
                session_totals[session] = (st, sw, sl, sc, win_rate(sw, sl, sc), expectancy(st, sw, sl, sc, sp))

        if session_totals:
            widths = [22, 6, 6, 6, 9, 12]
            h = table_header(["Session", "Total", "Wins", "Losses", "Win Rate", "Expectancy"], widths)
            lines.append(h)
            for s in SESSION_ORDER:
                if s in session_totals:
                    st, sw, sl, sc, swr, sexp = session_totals[s]
                    if swr >= wr_min * 100 or st >= min_n_cell:
                        lines.append(table_row([s, st, sw, sl, f"{swr:.1f}%", fmt_pnl(sexp)], widths))
            lines.append("")

        # Build confidence cross-tab rows (session × confidence)
        rows = []
        for session in SESSION_ORDER:
            buckets = r["session_conf_regime"].get(session, {})
            for conf_label in CONF_ORDER:
                regimes = buckets.get(conf_label, {})
                cell_total = sum(rd["total"] for rd in regimes.values())
                cell_wins = sum(rd["wins"] for rd in regimes.values())
                cell_losses = sum(rd["losses"] for rd in regimes.values())
                cell_closed = sum(rd["closed"] for rd in regimes.values())
                cell_pnl = sum(rd["pnl"] for rd in regimes.values())
                cell_symbols = set()
                for rd in regimes.values():
                    cell_symbols |= rd["symbols"]
                cell_regimes = {k for rd in regimes.values() for k in rd.keys()}

                if cell_total < min_n_cell:
                    continue
                cell_wr = win_rate(cell_wins, cell_losses, cell_closed)
                if cell_wr < wr_min * 100:
                    continue
                cell_exp = expectancy(cell_total, cell_wins, cell_losses, cell_closed, cell_pnl)

                # Δ vs global baseline for this version × session × confidence
                gsc = global_session_conf[ver].get((session, conf_label))
                if gsc and gsc["total"] >= min_n_cell:
                    delta = cell_wr - gsc["wr"]
                    z_score, is_sig = binomial_z_score(cell_wr, cell_total, gsc["wr"])
                    sig_flag = "🟢" if (is_sig and z_score > 0) else "🔴"
                else:
                    delta = 0.0
                    z_score = 0.0
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
                    "exp": cell_exp,
                    "delta": delta,
                    "sig_flag": sig_flag,
                    "z_score": z_score,
                })

        # Sort: 🟢 first, then expectancy desc (primary filter is real dollars),
        # then WR desc as a tiebreaker.
        rows.sort(key=lambda x: (0 if x["sig_flag"] == "🟢" else 1, -x["exp"], -x["wr"]))

        if rows:
            widths = [22, 12, 10, 8, 6, 6, 6, 9, 12, 8, 6]
            h = table_header(["Session", "Confidence", "Symbols", "Regime", "N", "Wins", "Losses", "Win Rate", "Expectancy", "Δ vs Global", "Sig"], widths)
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
                    f"{row['wr']:.1f}%",
                    fmt_pnl(row["exp"]),
                    f"{row['delta']:+.1f}pp",
                    row["sig_flag"],
                ], widths))
            lines.append("")
        else:
            lines.append("_No cells meet the win-rate + sample threshold._")
            lines.append("")

        lines.append("---")
        lines.append("")

    if not printed_any:
        lines.append("_No strategies met the WR floor and minimum-sample thresholds._")
        lines.append("")

    return lines


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Unified per-strategy analysis (all versions, 7 sessions)")
    parser.add_argument("--min-n-strategy", type=int, default=DEFAULT_MIN_N_STRATEGY,
                        help="Min signals per strategy to include (default %(default)s)")
    parser.add_argument("--min-n-cell", type=int, default=DEFAULT_MIN_N_CELL,
                        help="Min signals per session×confidence cell (default %(default)s)")
    parser.add_argument("--wr-min", type=float, default=DEFAULT_WR_MIN,
                        help="Min cell win-rate floor as decimal (default %(default)s). Use 0.0 to disable.")
    parser.add_argument("--confidence-min", type=float, default=0.01,
                        help="Overall confidence floor (default %(default)s)")
    parser.add_argument("--symbols", type=str, default=None,
                        help="Comma-separated symbol filter (e.g. 'SPY,NVDA,TSLA')")
    parser.add_argument("--output", type=str, default=None, help="Override output path")
    parser.add_argument("--no-sessions", action="store_true",
                        help="Skip the per-version session summary section")
    parser.add_argument("--both", action="store_true",
                        help="Emit detail twice: strict (WR>=wr-min) + loose (no WR cut)")
    args = parser.parse_args()

    output_path = Path(args.output) if args.output else OUTPUT_FILE

    print(f"Loading ALL signals (confidence ≥ {args.confidence_min})...", file=sys.stderr)
    signal_stream = load_all_outcomes(confidence_min=args.confidence_min, symbols=args.symbols)

    print("Analyzing strategies (streaming)...", file=sys.stderr)
    strategy_results = analyze_strategy(signal_stream)
    print(f"Found {len(strategy_results)} strategy ids", file=sys.stderr)

    print("Computing global baselines...", file=sys.stderr)
    versions, global_conf, global_session, global_session_conf, global_version = \
        compute_global_baselines(strategy_results)

    print("Generating report...", file=sys.stderr)
    report = generate_report(
        strategy_results, versions, global_conf, global_session,
        global_session_conf, global_version,
        min_n_strategy=args.min_n_strategy, min_n_cell=args.min_n_cell,
        wr_min=args.wr_min, include_sessions=not args.no_sessions,
        both_mode=args.both,
    )

    output_path.write_text(report)
    print(f"\n✅ Report written to {output_path}", file=sys.stderr)

    # Summary to stderr
    tw = sum(r["wins"] for r in strategy_results.values())
    tl = sum(r["losses"] for r in strategy_results.values())
    tp = sum(r["pnl"] for r in strategy_results.values())
    print(f"Total resolved: {tw + tl:,} | WR: {win_rate(tw, tl):.1f}% | Net P&L: {fmt_pnl(tp)}", file=sys.stderr)


if __name__ == "__main__":
    main()