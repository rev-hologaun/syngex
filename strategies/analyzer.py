"""
strategies/analyzer.py — Signal Review & Backtesting CLI

Usage:
    python3 -m strategies.analyzer summary      # Overall signal summary
    python3 -m strategies.analyzer stats        # Per-strategy statistics
    python3 -m strategies.analyzer open         # Currently open signals
    python3 -m strategies.analyzer recent -n 20 # Last N resolved signals
    python3 -m strategies.analyzer report       # Full report with tables
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .signal_tracker import SignalTracker, SignalOutcome


def cmd_summary(tracker: SignalTracker) -> None:
    """Print overall signal summary."""
    summary = tracker.get_summary()
    print(f"{'='*60}")
    print(f"  SIGNAL SUMMARY")
    print(f"{'='*60}")
    print(f"  Total resolved: {summary['total_resolved']}")
    print(f"  Wins: {summary['wins']}  |  Losses: {summary['losses']}  |  Closed: {summary['closed']}")
    print(f"  Win rate: {summary['win_rate']:.1%}")
    print(f"  Total PnL: ${summary['total_pnl']:,.2f}")
    print(f"  Avg hold time: {summary['avg_hold_time']:.0f}s ({summary['avg_hold_time']/60:.1f}m)")
    print(f"  Open signals: {summary['open_signals']}")
    print(f"{'='*60}")


def cmd_stats(tracker: SignalTracker) -> None:
    """Print per-strategy statistics."""
    stats = tracker.get_strategy_stats()
    if not stats:
        print("No strategy data available.")
        return

    print(f"{'='*80}")
    print(f"  PER-STRATEGY STATISTICS")
    print(f"{'='*80}")
    print(f"  {'Strategy':<35} {'Signals':>8} {'WR':>6} {'PnL':>10} {'Avg RR':>8}")
    print(f"  {'-'*35} {'-'*8} {'-'*6} {'-'*10} {'-'*8}")

    for strat, s in sorted(stats.items(), key=lambda x: x[1]["total_signals"], reverse=True):
        wr = s["win_rate"]
        pnl = s["total_pnl"]
        rr = s["avg_rr"]
        print(f"  {strat:<35} {s['total_signals']:>8} {wr:>6.1%} ${pnl:>9,.2f} {rr:>8.2f}")

    print(f"{'='*80}")


def cmd_open(tracker: SignalTracker) -> None:
    """Print currently open signals."""
    open_signals = tracker.get_open_signals()
    if not open_signals:
        print("No open signals.")
        return

    print(f"{'='*80}")
    print(f"  OPEN SIGNALS ({len(open_signals)})")
    print(f"{'='*80}")
    print(f"  {'Strategy':<30} {'Dir':>4} {'Entry':>10} {'Stop':>10} {'Target':>10} {'Age':>8}")
    print(f"  {'-'*30} {'-'*4} {'-'*10} {'-'*10} {'-'*10} {'-'*8}")

    now = time.time()
    for sig in open_signals:
        age = now - sig.timestamp
        age_str = f"{age/60:.1f}m" if age < 3600 else f"{age/3600:.1f}h"
        print(f"  {sig.strategy_id:<30} {sig.direction:>4} ${sig.entry:>9,.2f} ${sig.stop:>9,.2f} ${sig.target:>9,.2f} {age_str:>8}")

    print(f"{'='*80}")


def cmd_recent(tracker: SignalTracker, n: int = 20) -> None:
    """Print last N resolved signals."""
    resolved = tracker.get_resolved()
    recent = resolved[-n:] if len(resolved) > n else resolved

    if not recent:
        print("No resolved signals.")
        return

    print(f"{'='*100}")
    print(f"  RECENT RESOLVED SIGNALS (last {len(recent)})")
    print(f"{'='*100}")
    print(f"  {'Strategy':<25} {'Dir':>4} {'Entry':>10} {'Exit':>10} {'Outcome':>8} {'PnL':>10} {'Hold':>8}")
    print(f"  {'-'*25} {'-'*4} {'-'*10} {'-'*10} {'-'*8} {'-'*10} {'-'*8}")

    for r in recent:
        pnl_str = f"${r.pnl:>+9,.2f}"
        hold_str = f"{r.hold_time/60:.1f}m" if r.hold_time < 3600 else f"{r.hold_time/3600:.1f}h"
        print(f"  {r.open_signal.strategy_id:<25} {r.open_signal.direction:>4} ${r.open_signal.entry:>9,.2f} ${r.exit_price:>9,.2f} {r.outcome.value:>8} {pnl_str:>10} {hold_str:>8}")

    print(f"{'='*100}")


def cmd_report(tracker: SignalTracker) -> None:
    """Print full report."""
    cmd_summary(tracker)
    print()
    cmd_stats(tracker)
    print()
    cmd_open(tracker)
    print()
    cmd_recent(tracker, n=10)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Syngex Signal Analyzer")
    parser.add_argument(
        "command",
        choices=["summary", "stats", "open", "recent", "report"],
        help="Command to run",
    )
    parser.add_argument("-n", type=int, default=20, help="Number of recent signals (for 'recent' command)")

    args = parser.parse_args()

    # Find signal tracker
    log_dir = Path(__file__).parent.parent / "log"
    tracker = SignalTracker(log_dir=str(log_dir))

    # Run command
    commands = {
        "summary": lambda: cmd_summary(tracker),
        "stats": lambda: cmd_stats(tracker),
        "open": lambda: cmd_open(tracker),
        "recent": lambda: cmd_recent(tracker, args.n),
        "report": lambda: cmd_report(tracker),
    }

    commands[args.command]()


if __name__ == "__main__":
    main()
