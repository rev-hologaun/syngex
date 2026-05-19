"""Strategy Engine - strategy evaluation, triggers, and health tracking."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from engine.gex_calculator import GEXCalculator
from strategies.engine import StrategyEngine
from strategies.signal_tracker import SignalTracker
from core.filters import NetGammaFilter


class StrategyEvaluationEngine:
    """Engine for strategy evaluation and signal processing.

    Extracts strategy evaluation, trigger building, health tracking,
    and gamma profile reporting from the orchestrator into a dedicated module.
    """

    def __init__(
        self,
        gex_calculator: GEXCalculator,
        strategy_engine: StrategyEngine,
        signal_tracker: SignalTracker,
        gamma_filter: NetGammaFilter,
        logger: Optional[Any] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        self._gex_calculator = gex_calculator
        self._strategy_engine = strategy_engine
        self._signal_tracker = signal_tracker
        self._gamma_filter = gamma_filter
        self._logger = logger
        self._correlation_id = correlation_id

    def evaluate_strategies(self, orchestrator_ref: Any) -> None:
        """Run the full strategy evaluation loop.

        Args:
            orchestrator_ref: Reference to the orchestrator for accessing
                             rolling data, config, and symbol.
        """
        if not self._gex_calculator or not self._strategy_engine or not self._gamma_filter:
            return

        summary = self._gex_calculator.get_summary()
        net_gamma = summary["net_gamma"]
        flip = self._gex_calculator.get_gamma_flip()
        price = summary["underlying_price"]

        # Update regime filter
        # Check regime filter
        if not self._gamma_filter.check_regime(net_gamma, flip, price):
            return  # Blocked - transitioning regime

        # Build data snapshot for strategies
        data = {
            "underlying_price": price,
            "symbol": orchestrator_ref.symbol,
            "gex_calculator": self._gex_calculator,
            "rolling_data": orchestrator_ref._rolling_data,
            "timestamp": time.time(),
            "regime": self._gamma_filter._regime.value,
            "net_gamma": net_gamma,
            "gamma_flip": flip,
            "greeks_summary": self._gex_calculator.get_greeks_summary(),
        }

        # Inject per-strategy config params into data dict
        strategy_params: Dict[str, Dict[str, Any]] = {}
        for layer in ["layer1", "layer2", "layer3", "full_data"]:
            layer_config = orchestrator_ref._strategy_config.get(layer, {})
            for strat_name, strat_cfg in layer_config.items():
                if strat_cfg.get("enabled", True):
                    params = strat_cfg.get("params", {})
                    strategy_params[strat_name] = params
        data["params"] = strategy_params

        # Run evaluation
        signals = self._strategy_engine.process(data)

        if signals:
            # Track new signals for outcome resolution
            if self._signal_tracker:
                for s in signals:
                    self._signal_tracker.track(s.to_dict())

            for s in signals:
                if self._logger:
                    from config.logging_config import log_with_correlation
                    log_with_correlation(
                        self._logger, logging.INFO,
                        "SIGNAL",
                        correlation_id=self._correlation_id,
                        strategy_id=s.strategy_id,
                        direction=s.direction.value,
                        confidence=s.confidence,
                        reason=s.reason
                    )

    def build_last_trigger(self, signal_tracker: SignalTracker) -> Dict[str, Dict[str, Any]]:
        """Build last_trigger data for each strategy from open + resolved signals.

        Args:
            signal_tracker: The SignalTracker instance.

        Returns:
            Dict mapping strategy_id to last trigger data.
        """
        from strategies.signal import Direction
        from strategies.signal_tracker import SignalOutcome

        if not signal_tracker:
            return {}

        triggers: Dict[str, Dict[str, Any]] = {}

        # Build timestamp -> signal map for open signals
        open_by_strat: Dict[str, Dict[str, Any]] = {}
        for sig in signal_tracker.get_open_signals():
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
        resolved_by_strat: Dict[str, Dict[str, Any]] = {}
        for r in signal_tracker.get_resolved():
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
                    "side": "BUY" if last["direction"] == Direction.LONG else "SELL",
                    "confidence": round(last["confidence"], 3),
                    "entry": round(last["entry"], 2),
                    "stop": round(last["stop"], 2),
                    "target": round(last["target"], 2),
                    "timestamp": last["timestamp"],
                }

        return triggers

    def build_strategy_health(self, orchestrator_ref: Any) -> Dict[str, Dict[str, Any]]:
        """Build per-strategy health data for the heatmap JSON export.

        Args:
            orchestrator_ref: Reference to the orchestrator for accessing
                             strategy engine and signal tracker.

        Returns:
            Dict mapping strategy_id to health data.
        """
        if not self._strategy_engine or not self._signal_tracker:
            return {}

        health: Dict[str, Dict[str, Any]] = {}

        # Get strategy stats from signal tracker
        strat_stats = self._signal_tracker.get_strategy_stats()

        for strat in self._strategy_engine._strategies:
            sid = strat.strategy_id
            stats = strat_stats.get(sid, {})

            # Count signals from recent signals buffer
            last_signal_ts = 0.0
            sparkline_values: List = []

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

    def report_profile(self, gex_calculator: GEXCalculator, symbol: str) -> None:
        """Log the current Gamma Profile.

        Args:
            gex_calculator: The GEXCalculator instance.
            symbol: The ticker symbol.
        """
        if not self._logger:
            return

        summary = gex_calculator.get_summary()
        profile = gex_calculator.get_gamma_profile()

        net = summary["net_gamma"]
        price = summary["underlying_price"]
        strikes = summary["active_strikes"]

        # Format: one line per top-level metric
        self._logger.info(
            "GAMMA_PROFILE  |  %s  |  Underlying: $%.2f  |  "
            "Net Gamma: %+.2f  |  Strikes: %d  |  Msgs: %d",
            symbol,
            price,
            net,
            strikes,
            summary["total_messages"],
        )

        # Gamma Flip point
        flip = gex_calculator.get_gamma_flip()
        if flip is not None:
            self._logger.info("  GAMMA_FLIP:  Strike $%.1f (cumulative gamma turns negative below this)", flip)

        # Gamma Walls
        walls = gex_calculator.get_gamma_walls(threshold=500000)
        if walls:
            wall_parts = []
            for w in walls[:3]:
                sign = "+" if w["gex"] > 0 else "-"
                wall_parts.append(f"${w['strike']:.0f} ({w['side']}) {sign}${abs(w['gex']):,.0f}")
            self._logger.info("  GAMMA_WALLS:  %s", "  |  ".join(wall_parts))

        # Top 5 strikes by absolute Net Gamma
        top = sorted(
            profile["strikes"].items(),
            key=lambda x: abs(x[1]["net_gamma"]),
            reverse=True,
        )[:5]

        if top:
            parts = []
            for strike, bucket in top:
                ng = bucket["net_gamma"]
                sign = "+" if ng >= 0 else "-"
                parts.append(f"  K{strike:.1f}: {sign}{abs(ng):,.2f}")
            self._logger.info("  TOP_STRIKES:  %s", "  |  ".join(parts))
