"""State exporter service - exports GEX state to JSON."""

import json
import logging
import time
from pathlib import Path
from typing import Any


class StateExporter:
    """Exports GEX state to JSON file for dashboard consumption."""

    def __init__(
        self,
        data_dir: Path,
        calculator_ref: Any,
        strategy_engine_ref: Any,
        signal_tracker_ref: Any,
        gamma_filter_ref: Any,
        symbol: str,
        logger: Any,
        correlation_id: str,
    ) -> None:
        self._data_dir = data_dir
        self._calculator = calculator_ref
        self._strategy_engine = strategy_engine_ref
        self._signal_tracker = signal_tracker_ref
        self._gamma_filter = gamma_filter_ref
        self.symbol = symbol
        self._logger = logger
        self._correlation_id = correlation_id
        self._data_file = data_dir / f"gex_state_{self.symbol}.json"

    def export(self) -> None:
        """Write the current GEX state to a shared JSON file."""
        if self._calculator is None:
            return

        state = self._calculator.get_summary()
        profile = self._calculator.get_gamma_profile()

        export = {
            "symbol": state["symbol"],
            "underlying_price": state["underlying_price"],
            "net_gamma": state["net_gamma"],
            "active_strikes": state["active_strikes"],
            "total_messages": state["total_messages"],
            "strikes": profile["strikes"],
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        }

        # Add strategy engine status
        if self._strategy_engine:
            export["strategy_engine"] = self._strategy_engine.get_status()
            # Per-strategy health data for heatmap
            export["strategy_health"] = self._build_strategy_health()
            # Per-strategy last trigger for execution card
            export["last_trigger"] = self._build_last_trigger()
            # Micro-signal confidence overlay for dashboard
            recent = self._strategy_engine.get_recent_signals(20)
            micro_signals: dict[str, dict[str, Any]] = {}
            for sig in recent:
                strike = sig.get("target", sig.get("entry", 0))
                if strike:
                    key = f"{strike:.1f}"
                    # Keep highest confidence per strike
                    if key not in micro_signals or sig.get("confidence", 0) > micro_signals[key]["confidence"]:
                        micro_signals[key] = {
                            "confidence": sig.get("confidence", 0),
                            "strategy": sig.get("strategy_id", ""),
                            "direction": sig.get("direction", ""),
                            "reason": sig.get("reason", ""),
                            "timestamp": sig.get("timestamp", ""),
                        }
            if micro_signals:
                export["micro_signals"] = micro_signals

        if self._gamma_filter:
            export["regime_filter"] = self._gamma_filter.get_status()

        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            with open(self._data_file, "w") as f:
                json.dump(export, f, indent=2)
        except Exception as exc:
            from config.logging_config import log_with_correlation
            log_with_correlation(
                self._logger, logging.WARNING,
                "Failed to export GEX state",
                correlation_id=self._correlation_id,
                error=str(exc)
            )

    def _build_last_trigger(self) -> dict[str, dict[str, Any]]:
        """Build last_trigger data for each strategy from open + resolved signals."""
        if not self._signal_tracker:
            return {}

        from strategies.signal_tracker import SignalDirection, SignalOutcome, SignalResolution
        triggers: dict[str, dict[str, Any]] = {}

        # Build timestamp -> signal map for open signals
        open_by_strat: dict[str, dict[str, Any]] = {}
        for sig in self._signal_tracker.get_open_signals():
            sid = sig.strategy_id
            if sid not in open_by_strat or sig.timestamp > open_by_strat[sid].get("timestamp", 0):
                open_by_strat[sid] = {
                    "direction": sig.direction,
                    "confidence": sig.confidence,
                    "entry": sig.entry,
                    "stop": sig.stop,
                    "target": sig.target,
                    "timestamp": sig.timestamp,
                }

        # Build timestamp -> signal map for resolved signals
        resolved_by_strat: dict[str, dict[str, Any]] = {}
        for r in self._signal_tracker.get_resolved():
            sid = r.open_signal.strategy_id
            if sid not in resolved_by_strat or r.resolution_time > resolved_by_strat[sid].get("timestamp", 0):
                resolved_by_strat[sid] = {
                    "direction": r.open_signal.direction,
                    "confidence": r.open_signal.confidence,
                    "entry": r.open_signal.entry,
                    "stop": r.open_signal.stop,
                    "target": r.open_signal.target,
                    "timestamp": r.resolution_time,
                }

        # Merge: prefer open signal (most recent), fall back to resolved
        all_strats = set(open_by_strat.keys()) | set(resolved_by_strat.keys())
        for sid in all_strats:
            open_sig = open_by_strat.get(sid)
            resolved_sig = resolved_by_strat.get(sid)

            if open_sig and resolved_sig:
                # Pick whichever is more recent
                last = open_sig if open_sig["timestamp"] >= resolved_sig["timestamp"] else resolved_sig
            elif open_sig:
                last = open_sig
            else:
                last = resolved_sig

            if last:
                triggers[sid] = {
                    "side": "BUY" if last["direction"] == SignalDirection.LONG else "SELL",
                    "confidence": round(last["confidence"], 3),
                    "entry": round(last["entry"], 2),
                    "stop": round(last["stop"], 2),
                    "target": round(last["target"], 2),
                    "timestamp": last["timestamp"],
                }

        return triggers

    def _build_strategy_health(self) -> dict[str, dict[str, Any]]:
        """Build per-strategy health data for the heatmap JSON export."""
        if not self._strategy_engine or not self._signal_tracker:
            return {}

        health: dict[str, dict[str, Any]] = {}

        # Get strategy stats from signal tracker
        strat_stats = self._signal_tracker.get_strategy_stats()

        for strat in self._strategy_engine._strategies:
            sid = strat.strategy_id
            stats = strat_stats.get(sid, {})

            # Count signals from recent signals buffer
            last_signal_ts = 0.0
            sparkline_values: list = []

            # Get resolved signals for this strategy
            resolved = self._signal_tracker.get_resolved()
            strategy_resolved = [r for r in resolved if r.open_signal.strategy_id == sid]

            # Build sparkline from cumulative PnL over resolved signals
            cumulative = 0.0
            for r in strategy_resolved[-8:]:
                cumulative += r.pnl
                sparkline_values.append(round(cumulative, 2))

            # If not enough resolved signals, pad with zeros
            while len(sparkline_values) < 8:
                sparkline_values.insert(0, 0.0)

            # Count total signals for this strategy
            total_signals = stats.get("total_signals", 0)
            wins = stats.get("wins", 0)
            losses = stats.get("losses", 0)
            closed = stats.get("closed", 0)
            resolved_count = wins + losses + closed

            # Win rate from resolved signals
            win_rate = wins / resolved_count if resolved_count > 0 else 0.0

            # PnL
            pnl = stats.get("total_pnl", 0.0)

            # Status: active if has resolved signals, idle otherwise
            if total_signals > 0:
                status = "active"
            else:
                status = "idle"

            # Check if any open signals exist for this strategy
            open_signals = self._signal_tracker.get_open_signals()
            has_open = any(s.strategy_id == sid for s in open_signals)
            if has_open and status == "idle":
                status = "active"

            # Track the most recent signal timestamp (open or resolved)
            for s in open_signals:
                if s.strategy_id == sid and s.timestamp > last_signal_ts:
                    last_signal_ts = s.timestamp
            for r in strategy_resolved:
                if r.resolution_time > last_signal_ts:
                    last_signal_ts = r.resolution_time

            health[sid] = {
                "status": status,
                "signal_count": total_signals,
                "last_signal_ts": last_signal_ts,
                "win_rate": round(win_rate, 4),
                "pnl": round(pnl, 2),
                "sparkline": sparkline_values[-8:],
            }

        return health
