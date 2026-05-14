#!/usr/bin/env python3
"""
Validation Round 3 — Per-Strategy Deep Analysis
================================================
Analyzes each strategy on its own across 5 dimensions:
1) Performance at each confidence level
2) Market type fit (Trending / Sideways / Volatile-Breakout)
3) Timeframe performance (ORB / Early / Mid / Late)
4) Additional insights
5) Recommended enhancements
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ── Paths ──────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "log")
OUT_FILE = os.path.join(os.path.dirname(__file__), "..", "analysis_round3.md")

# ── Timezone ───────────────────────────────────────────────────────────
# All timestamps are Unix epoch. Market hours PT: 9:30-16:00 PT
# ORB:  9:30-10:00  (first 30 min)
# Early: 10:00-12:00
# Mid:  12:00-14:30
# Late: 14:30-16:00

def ts_to_hour(ts):
    """Convert Unix timestamp to hour of trading day (PT)."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    # Convert UTC to PT (UTC-7 in May)
    pt_hour = dt.hour - 7
    if pt_hour < 0:
        pt_hour += 24
    return pt_hour + dt.minute / 60.0

def classify_timeframe(ts, resolution_time=None):
    """Classify a timestamp into Pre, ORB, Early, Mid, or Late."""
    # Prefer resolution_time if ts is 0 (common in signal_outcomes)
    if ts == 0 and resolution_time:
        ts = resolution_time
    h = ts_to_hour(ts)
    if h < 9.5:
        return "Pre-Market (<9:30 PT)"
    elif h < 10.0:
        return "ORB (9:30-10:00 PT)"
    elif h < 12.0:
        return "Early (10:00-12:00 PT)"
    elif h < 14.5:
        return "Mid (12:00-14:30 PT)"
    elif h < 16.0:
        return "Late (14:30-16:00 PT)"
    else:
        return f"After-Hours ({h:.1f} PT)"

def confidence_bucket(conf):
    """Map confidence 0-1 to bucket string."""
    b = int(conf * 100) // 10
    lo = b * 10
    return f"{lo}-{lo+9}%"

def load_all_outcomes():
    """Load all signal_outcomes_*.jsonl files."""
    outcomes = []
    for fname in sorted(os.listdir(LOG_DIR)):
        if fname.startswith("signal_outcomes_") and fname.endswith(".jsonl"):
            symbol = fname.replace("signal_outcomes_", "").replace(".jsonl", "")
            path = os.path.join(LOG_DIR, fname)
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        rec = json.loads(line)
                        rec["_symbol"] = symbol
                        outcomes.append(rec)
    return outcomes

def load_signals():
    """Load main signals.jsonl (no symbol prefix — these are symbol-agnostic or all symbols)."""
    signals = []
    path = os.path.join(LOG_DIR, "signals.jsonl")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    signals.append(rec)
    return signals

# ── Analysis Functions ────────────────────────────────────────────────

def analyze_confidence(outcomes):
    """Q1: Performance at each confidence level."""
    buckets = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "total_pnl": 0.0})
    for r in outcomes:
        b = confidence_bucket(r.get("confidence", 0.5))
        buckets[b]["total"] += 1
        if r.get("outcome") == "WIN":
            buckets[b]["wins"] += 1
            buckets[b]["total_pnl"] += r.get("pnl", 0)
        elif r.get("outcome") == "LOSS":
            buckets[b]["losses"] += 1
            buckets[b]["total_pnl"] += r.get("pnl", 0)
        else:
            buckets[b]["total_pnl"] += r.get("pnl", 0)
    return buckets

def analyze_market_type(outcomes):
    """Q2: Market type performance.
    Infer from metadata: regime (POSITIVE/NEGATIVE), trend (UP/DOWN/FLAT).
    POSITIVE + FLAT → Sideways (range-bound)
    POSITIVE + UP/DOWN → Trending
    NEGATIVE → Volatile/Breakout
    """
    types = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "total_pnl": 0.0})
    for r in outcomes:
        meta = r.get("metadata", {})
        regime = meta.get("regime", "POSITIVE")
        trend = meta.get("trend", "FLAT")
        if regime == "NEGATIVE":
            mtype = "Volatile/Breakout"
        elif trend in ("UP", "DOWN"):
            mtype = "Trending"
        else:
            mtype = "Sideways"
        types[mtype]["total"] += 1
        if r.get("outcome") == "WIN":
            types[mtype]["wins"] += 1
            types[mtype]["total_pnl"] += r.get("pnl", 0)
        elif r.get("outcome") == "LOSS":
            types[mtype]["losses"] += 1
            types[mtype]["total_pnl"] += r.get("pnl", 0)
        else:
            types[mtype]["total_pnl"] += r.get("pnl", 0)
    return types

def analyze_timeframe(outcomes):
    """Q3: Timeframe performance."""
    tf = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "total_pnl": 0.0})
    for r in outcomes:
        # Use resolution_time as primary for signal_outcomes (timestamp is often 0)
        ts = r.get("resolution_time", r.get("timestamp", 0))
        t = classify_timeframe(r.get("timestamp", 0), resolution_time=ts)
        tf[t]["total"] += 1
        if r.get("outcome") == "WIN":
            tf[t]["wins"] += 1
            tf[t]["total_pnl"] += r.get("pnl", 0)
        elif r.get("outcome") == "LOSS":
            tf[t]["losses"] += 1
            tf[t]["total_pnl"] += r.get("pnl", 0)
        else:
            tf[t]["total_pnl"] += r.get("pnl", 0)
    return tf

def analyze_hold_time(outcomes):
    """Hold time analysis."""
    buckets = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
    for r in outcomes:
        ht = r.get("hold_time", 0)
        if ht < 60:
            b = "Fast (<1 min)"
        elif ht < 300:
            b = "Short (1-5 min)"
        elif ht < 900:
            b = "Medium (5-15 min)"
        else:
            b = "Long (>15 min)"
        buckets[b]["total"] += 1
        if r.get("outcome") == "WIN":
            buckets[b]["wins"] += 1
        elif r.get("outcome") == "LOSS":
            buckets[b]["losses"] += 1
    return buckets

def compute_strat_metrics(outcomes):
    """Compute overall metrics for a strategy."""
    total = len(outcomes)
    wins = sum(1 for r in outcomes if r.get("outcome") == "WIN")
    losses = sum(1 for r in outcomes if r.get("outcome") == "LOSS")
    total_pnl = sum(r.get("pnl", 0) for r in outcomes)
    win_pnl = sum(r.get("pnl", 0) for r in outcomes if r.get("outcome") == "WIN")
    loss_pnl = sum(r.get("pnl", 0) for r in outcomes if r.get("outcome") == "LOSS")
    avg_win = win_pnl / wins if wins else 0
    avg_loss = loss_pnl / losses if losses else 0
    avg_hold = sum(r.get("hold_time", 0) for r in outcomes) / total if total else 0
    avg_conf = sum(r.get("confidence", 0.5) for r in outcomes) / total if total else 0
    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "win_rate": wins / total if total else 0,
        "total_pnl": total_pnl,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "avg_hold": avg_hold,
        "avg_confidence": avg_conf,
    }

# ── Per-Strategy Analysis ────────────────────────────────────────────

def get_strategies(outcomes):
    """Group outcomes by strategy_id."""
    by_strat = defaultdict(list)
    for r in outcomes:
        sid = r.get("strategy_id", "unknown")
        by_strat[sid].append(r)
    return by_strat

def generate_analysis():
    """Main analysis pipeline."""
    outcomes = load_all_outcomes()
    by_strat = get_strategies(outcomes)
    
    lines = []
    lines.append("# Validation Round 3 — Per-Strategy Deep Analysis\n")
    lines.append(f"**Date:** 2026-05-06 | **Total Signals Analyzed:** {len(outcomes):,}\n")
    lines.append("---\n")
    
    # Overall summary
    all_metrics = compute_strat_metrics(outcomes)
    lines.append("## 📊 Overall Summary\n")
    lines.append(f"- **Total Signals:** {all_metrics['total']:,}")
    lines.append(f"- **Win Rate:** {all_metrics['win_rate']*100:.1f}%")
    lines.append(f"- **Total P&L:** ${all_metrics['total_pnl']:,.2f}")
    lines.append(f"- **Avg Win:** ${all_metrics['avg_win']:.2f} | **Avg Loss:** ${all_metrics['avg_loss']:.2f}")
    lines.append(f"- **Avg Hold Time:** {all_metrics['avg_hold']:.0f}s ({all_metrics['avg_hold']/60:.1f} min)")
    lines.append(f"- **Avg Confidence:** {all_metrics['avg_confidence']*100:.0f}%\n")
    
    # Per-strategy deep dives
    for strat_id, strat_outcomes in sorted(by_strat.items(), key=lambda x: -len(x[1])):
        m = compute_strat_metrics(strat_outcomes)
        lines.append(f"\n## 🐉 Strategy: {strat_id.replace('_', ' ').title()}\n")
        
        # Overview
        lines.append("### Overview")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Total Signals | {m['total']:,} |")
        lines.append(f"| Win Rate | {m['win_rate']*100:.1f}% |")
        lines.append(f"| Total P&L | ${m['total_pnl']:,.2f} |")
        lines.append(f"| Avg Win | ${m['avg_win']:.2f} |")
        lines.append(f"| Avg Loss | ${m['avg_loss']:.2f} |")
        lines.append(f"| Avg Hold Time | {m['avg_hold']:.0f}s ({m['avg_hold']/60:.1f} min) |")
        lines.append(f"| Avg Confidence | {m['avg_confidence']*100:.0f}% |\n")
        
        # Q1: Confidence Levels
        lines.append("### Q1: Performance by Confidence Level\n")
        conf_buckets = analyze_confidence(strat_outcomes)
        lines.append("| Confidence | Total | Wins | Losses | Win Rate | Avg P&L |")
        lines.append("|------------|-------|------|--------|----------|---------|")
        for b in sorted(conf_buckets.keys()):
            d = conf_buckets[b]
            wr = d["wins"] / d["total"] * 100 if d["total"] else 0
            avg_pnl = d["total_pnl"] / d["total"] if d["total"] else 0
            lines.append(f"| {b} | {d['total']} | {d['wins']} | {d['losses']} | {wr:.0f}% | ${avg_pnl:.2f} |")
        lines.append("")
        
        # Q2: Market Type
        lines.append("### Q2: Market Type Performance\n")
        market = analyze_market_type(strat_outcomes)
        lines.append("| Market Type | Total | Wins | Losses | Win Rate | Avg P&L |")
        lines.append("|-------------|-------|------|--------|----------|---------|")
        for mt in sorted(market.keys()):
            d = market[mt]
            wr = d["wins"] / d["total"] * 100 if d["total"] else 0
            avg_pnl = d["total_pnl"] / d["total"] if d["total"] else 0
            lines.append(f"| {mt} | {d['total']} | {d['wins']} | {d['losses']} | {wr:.0f}% | ${avg_pnl:.2f} |")
        lines.append("")
        
        # Q3: Timeframe
        lines.append("### Q3: Timeframe Performance\n")
        tf = analyze_timeframe(strat_outcomes)
        lines.append("| Timeframe | Total | Wins | Losses | Win Rate | Avg P&L |")
        lines.append("|-----------|-------|------|--------|----------|---------|")
        for t in sorted(tf.keys()):
            d = tf[t]
            wr = d["wins"] / d["total"] * 100 if d["total"] else 0
            avg_pnl = d["total_pnl"] / d["total"] if d["total"] else 0
            lines.append(f"| {t} | {d['total']} | {d['wins']} | {d['losses']} | {wr:.0f}% | ${avg_pnl:.2f} |")
        lines.append("")
        
        # Q4: Additional Insights
        lines.append("### Q4: Additional Insights\n")
        
        # Direction analysis
        dir_stats = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        for r in strat_outcomes:
            d = r.get("direction", "NEUTRAL")
            dir_stats[d]["total"] += 1
            if r.get("outcome") == "WIN":
                dir_stats[d]["wins"] += 1
            elif r.get("outcome") == "LOSS":
                dir_stats[d]["losses"] += 1
        
        lines.append("**Direction Breakdown:**")
        for d in sorted(dir_stats.keys()):
            ds = dir_stats[d]
            wr = ds["wins"] / ds["total"] * 100 if ds["total"] else 0
            lines.append(f"- {d}: {ds['wins']}/{ds['total']} ({wr:.0f}% win rate)")
        lines.append("")
        
        # Strength analysis
        strength_stats = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})
        for r in strat_outcomes:
            s = r.get("strength", "UNKNOWN")
            strength_stats[s]["total"] += 1
            if r.get("outcome") == "WIN":
                strength_stats[s]["wins"] += 1
            elif r.get("outcome") == "LOSS":
                strength_stats[s]["losses"] += 1
        
        lines.append("**Signal Strength:**")
        for s in sorted(strength_stats.keys()):
            ss = strength_stats[s]
            wr = ss["wins"] / ss["total"] * 100 if ss["total"] else 0
            lines.append(f"- {s}: {ss['wins']}/{ss['total']} ({wr:.0f}% win rate)")
        lines.append("")
        
        # Hold time distribution
        ht = analyze_hold_time(strat_outcomes)
        lines.append("**Hold Time Distribution:**")
        for h in sorted(ht.keys()):
            hd = ht[h]
            wr = hd["wins"] / hd["total"] * 100 if hd["total"] else 0
            lines.append(f"- {h}: {hd['wins']}/{hd['total']} ({wr:.0f}% win rate)")
        lines.append("")
        
        # Symbol distribution
        sym_stats = defaultdict(lambda: {"total": 0, "wins": 0})
        for r in strat_outcomes:
            sym = r.get("_symbol", "ALL")
            sym_stats[sym]["total"] += 1
            if r.get("outcome") == "WIN":
                sym_stats[sym]["wins"] += 1
        
        lines.append("**Symbol Distribution:**")
        for sym in sorted(sym_stats.keys()):
            ss = sym_stats[sym]
            wr = ss["wins"] / ss["total"] * 100 if ss["total"] else 0
            lines.append(f"- {sym}: {ss['wins']}/{ss['total']} ({wr:.0f}% win rate)")
        lines.append("")
        
        # Q5: Recommendations
        lines.append("### Q5: Recommended Enhancements\n")
        
        # Generate recommendations based on data patterns
        recommendations = []
        
        # Confidence threshold analysis
        if conf_buckets:
            best_conf = max(conf_buckets.items(), key=lambda x: x[1]["wins"]/x[1]["total"] if x[1]["total"] else 0)
            worst_conf = min(conf_buckets.items(), key=lambda x: x[1]["wins"]/x[1]["total"] if x[1]["total"] else 0)
            if best_conf[1]["total"] >= 5 and worst_conf[1]["total"] >= 5:
                recommendations.append(
                    f"**Confidence Threshold:** Signals in {best_conf[0]} bucket perform best "
                    f"({best_conf[1]['wins']}/{best_conf[1]['total']} = {best_conf[1]['wins']/best_conf[1]['total']*100:.0f}% WR). "
                    f"Consider raising minimum confidence from 0.30 to {best_conf[0].split('-')[0]}/100."
                )
        
        # Market type
        if market:
            best_mt = max(market.items(), key=lambda x: x[1]["wins"]/x[1]["total"] if x[1]["total"] else 0)
            recommendations.append(
                f"**Market Type Fit:** Best in {best_mt[0]} (WR: {best_mt[1]['wins']/best_mt[1]['total']*100:.0f}%). "
                f"Consider adding a regime filter to avoid trading in non-optimal regimes."
            )
        
        # Timeframe
        if tf:
            best_tf = max(tf.items(), key=lambda x: x[1]["wins"]/x[1]["total"] if x[1]["total"] else 0)
            recommendations.append(
                f"**Timeframe Optimization:** {best_tf[0]} shows strongest results "
                f"({best_tf[1]['wins']}/{best_tf[1]['total']} = {best_tf[1]['wins']/best_tf[1]['total']*100:.0f}% WR). "
                f"Consider weighting signals from this period higher."
            )
        
        # Hold time
        if ht:
            best_ht = max(ht.items(), key=lambda x: x[1]["wins"]/x[1]["total"] if x[1]["total"] else 0)
            recommendations.append(
                f"**Hold Time:** Optimal hold range is {best_ht[0]} "
                f"({best_ht[1]['wins']}/{best_ht[1]['total']} = {best_ht[1]['wins']/best_ht[1]['total']*100:.0f}% WR). "
                f"Consider implementing dynamic exit based on hold time."
            )
        
        # General
        if m["win_rate"] < 0.50:
            recommendations.append(
                f"**Win Rate:** At {m['win_rate']*100:.0f}%, consider adding a secondary confirmation filter "
                f"(e.g., volume spike, RSI confirmation) to improve signal quality."
            )
        elif m["win_rate"] > 0.60:
            recommendations.append(
                f"**Strong Win Rate:** At {m['win_rate']*100:.0f}%, this strategy is performing well. "
                f"Consider increasing position size or reducing stop distance to improve R:R."
            )
        
        if m["total_pnl"] < 0:
            recommendations.append(
                f"**P&L Negative:** Total P&L is ${m['total_pnl']:,.2f}. Review if large losses are "
                f"outliers or systemic. Consider tighter stops or adding a max-loss-per-day rule."
            )
        
        for rec in recommendations:
            lines.append(f"- {rec}")
        lines.append("")
    
    # ── Cross-Strategy Comparison ─────────────────────────────────────
    lines.append("\n---\n\n## 📋 Cross-Strategy Comparison\n\n")
    lines.append("| Strategy | Signals | Win Rate | Total P&L | Avg Hold | Best Timeframe | Best Market |")
    lines.append("|----------|---------|----------|-----------|----------|----------------|-------------|")
    
    strat_summary = []
    for strat_id, strat_outcomes in sorted(by_strat.items(), key=lambda x: -len(x[1])):
        m = compute_strat_metrics(strat_outcomes)
        market = analyze_market_type(strat_outcomes)
        tf = analyze_timeframe(strat_outcomes)
        best_mt = max(market.items(), key=lambda x: x[1]["wins"]/x[1]["total"] if x[1]["total"] else 0)
        best_tf = max(tf.items(), key=lambda x: x[1]["wins"]/x[1]["total"] if x[1]["total"] else 0)
        strat_summary.append({
            "name": strat_id.replace("_", " ").title(),
            "signals": m["total"],
            "wr": f"{m['win_rate']*100:.0f}%",
            "pnl": f"${m['total_pnl']:,.0f}",
            "hold": f"{m['avg_hold']/60:.1f}m",
            "best_tf": best_tf[0].split("(")[0].strip(),
            "best_mt": best_mt[0],
        })
    
    for s in strat_summary:
        lines.append(f"| {s['name']} | {s['signals']} | {s['wr']} | {s['pnl']} | {s['hold']} | {s['best_tf']} | {s['best_mt']} |")
    
    lines.append("\n---\n\n*Analysis generated by Archon for Validation Round 3.*")
    
    # Write output
    with open(OUT_FILE, "w") as f:
        f.write("\n".join(lines))
    
    # Also print summary to stdout
    print(f"\n{'='*70}")
    print(f"  VALIDATION ROUND 3 — ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"  Total signals analyzed: {len(outcomes):,}")
    print(f"  Strategies found: {len(by_strat)}")
    print(f"  Output: {OUT_FILE}")
    print(f"{'='*70}\n")
    
    # Print per-strategy quick summary
    for s in strat_summary:
        print(f"  {s['name']:30s} | {s['signals']:>5} sigs | {s['wr']:>5s} WR | {s['pnl']:>10s} | {s['hold']:>5s} | Best: {s['best_tf']} / {s['best_mt']}")
    
    return by_strat

if __name__ == "__main__":
    generate_analysis()
