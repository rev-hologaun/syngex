"""
strategies/engine.py — The StrategyEngine

Central rule-evaluation loop.

Responsibilities:
    1. Accept incoming data snapshots from the orchestrator
    2. Pass data to all registered strategies
    3. Collect signals, apply the Net Gamma regime filter
    4. Route filtered signals to the Command Center / signal log

Architecture:
    Data → [Net Gamma Filter] → [Strategy 1, Strategy 2, ...] → Signal Collector → Route

    The Net Gamma filter runs first. It sets a regime context
    (POSITIVE / NEGATIVE) that all strategies check before producing signals.

    Only signals that pass the filter reach the output.
"""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

from .signal import Direction, Signal, SignalStrength
from .rolling_window import RollingWindow

logger = logging.getLogger("Syngex.StrategyEngine")


# ---------------------------------------------------------------------------
# Strategy protocol
# ---------------------------------------------------------------------------

class BaseStrategy:
    """
    Base class for all strategies.

    Subclasses implement:
        - evaluate(data) -> List[Signal]

    The engine calls evaluate() with each data snapshot.
    Strategies should be stateless or manage their own state.
    """

    strategy_id: str = ""
    layer: str = ""          # "layer1", "layer2", "layer3", "full_data"
    enabled: bool = True     # Toggle via config

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Allow subclasses to accept any init args (calculator, config, etc)."""
        self._params: Dict[str, Any] = {}

    def set_params(self, params: Dict[str, Any]) -> None:
        """Apply config params to this strategy."""
        self._params = params

    def _apply_params(self, data: Dict[str, Any]) -> None:
        """
        Apply config params from data dict to this strategy.

        This is called at the start of evaluate() to override
        class-level constants with config values.

        Usage in subclasses (override in each strategy):
            self._apply_params(data)
            # Now use self.params for config-driven values
        """
        params = data.get("params", {}).get(self.strategy_id, {})
        if params:
            self.set_params(params)

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate incoming data and return signals.

        Args:
            data: Dict containing current market state:
                - underlying_price: float
                - gex_calculator: GEXCalculator instance
                - rolling_data: Dict[str, RollingWindow]
                - timestamp: float
                - regime: str ("POSITIVE" or "NEGATIVE")

        Returns:
            List of Signal objects (may be empty).
        """
        raise NotImplementedError


# ---------------------------------------------------------------------------
# StrategyEngine
# ---------------------------------------------------------------------------

@dataclass
class EngineConfig:
    """Configuration for the StrategyEngine."""
    min_confidence: float = 0.40       # Minimum confidence to pass the filter
    max_signals_per_tick: int = 10     # Prevent signal spam
    dedup_window_seconds: float = 60.0  # Don't repeat same strategy signal within this window


class StrategyEngine:
    """
    Central strategy evaluation engine.

    Lifecycle:
        1. Create engine
        2. Register strategies: engine.register(MyStrategy())
        3. Start: engine.start()
        4. Feed data: engine.process(data) -> List[Signal]
        5. Stop: engine.stop()
    """

    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        signal_tracker: Any = None,
    ) -> None:
        self.config = config or EngineConfig()
        self._strategies: List[BaseStrategy] = []
        self._filter_callback: Optional[Callable[[Signal], bool]] = None
        self._signal_handlers: List[Callable[[Signal], None]] = []
        self._running = False
        self._last_signals: Dict[str, float] = {}  # strategy_id -> last signal time
        self._signal_count: int = 0
        self._tick_count: int = 0

        # In-memory ring buffer for recent signals (used by Command Center)
        self._recent_signals: List[Dict[str, Any]] = []  # last N signal dicts
        self._recent_buffer_size: int = 200  # keep up to 200 recent signals in memory

        # Signal tracker for per-symbol logging (delegates all signal writes)
        self._signal_tracker = signal_tracker

        logger.info("StrategyEngine initialized (min_confidence=%.2f, max_per_tick=%d)",
                     self.config.min_confidence, self.config.max_signals_per_tick)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, strategy: BaseStrategy) -> None:
        """Register a strategy for evaluation."""
        if not strategy.strategy_id:
            raise ValueError(f"Strategy {type(strategy).__name__} has no strategy_id")
        self._strategies.append(strategy)
        logger.info("Registered strategy: %s (layer=%s)", strategy.strategy_id, strategy.layer)

    def register_filter(self, callback: Callable[[Signal], bool]) -> None:
        """
        Register the Net Gamma regime filter.

        The filter receives a Signal and returns True if the signal
        should pass, False if it should be blocked.
        """
        self._filter_callback = callback
        logger.info("Regime filter registered")

    def register_signal_handler(self, callback: Callable[[Signal], None]) -> None:
        """Register a handler for output signals (e.g., Command Center push)."""
        self._signal_handlers.append(callback)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the engine."""
        self._running = True
        logger.info("StrategyEngine started (%d strategies registered)", len(self._strategies))

    def stop(self) -> None:
        """Stop the engine."""
        self._running = False
        logger.info("StrategyEngine stopped. Total signals: %d", self._signal_count)

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def process(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Process a single data snapshot through all registered strategies.

        This is the main entry point called from the orchestrator loop.

        Args:
            data: Current market state dict. Must contain:
                - underlying_price (float)
                - gex_calculator (GEXCalculator)
                - rolling_data (Dict[str, RollingWindow])
                - timestamp (float)
                - regime (str) — from Net Gamma filter

        Returns:
            List of signals that passed all filters.
        """
        if not self._running:
            return []

        self._tick_count += 1
        all_signals: List[Signal] = []
        now = time.time()

        # Extract symbol from data for propagation to signals
        signal_symbol = data.get("symbol", "")

        # Phase 1: Evaluate all strategies
        for strategy in self._strategies:
            if not strategy.enabled:
                continue
            try:
                # Inject params into data before evaluation
                params = data.get("params", {})
                strat_params = params.get(strategy.strategy_id, {})
                strategy.set_params(strat_params)

                signals = strategy.evaluate(data)
                for signal in signals:
                    # Attach symbol to signal if not already set
                    if signal_symbol and not signal.symbol:
                        # Can't mutate frozen dataclass — rebuild with symbol
                        signal = Signal(
                            direction=signal.direction,
                            confidence=signal.confidence,
                            entry=signal.entry,
                            stop=signal.stop,
                            target=signal.target,
                            strategy_id=signal.strategy_id,
                            _layer=strategy.layer,
                            symbol=signal_symbol,
                            timestamp=signal.timestamp,
                            reason=signal.reason,
                            expiry=signal.expiry,
                            metadata=signal.metadata,
                        )
                    # Dedup: skip if same strategy fired recently
                    last_time = self._last_signals.get(signal.strategy_id, 0)
                    if now - last_time < self.config.dedup_window_seconds:
                        continue
                    all_signals.append(signal)
            except Exception as exc:
                logger.error("Strategy %s error: %s", strategy.strategy_id, exc, exc_info=True)

        # Phase 2: Apply regime filter
        if self._filter_callback:
            filtered = [s for s in all_signals if self._filter_callback(s)]
            blocked = len(all_signals) - len(filtered)
            if blocked > 0:
                logger.debug("Regime filter blocked %d signals", blocked)
            all_signals = filtered

        # Phase 2.5: Inter-strategy conflict detection & resolution
        conflicts = self._detect_conflicts(all_signals)
        if conflicts:
            logger.info(
                "Conflict detection: found %d conflict group(s) among %d signals",
                len(conflicts),
                len(all_signals),
            )
            all_signals = self._filter_signals(all_signals, conflicts)

        # Phase 3: Cap signals per tick
        if len(all_signals) > self.config.max_signals_per_tick:
            # Keep highest confidence signals
            all_signals.sort(key=lambda s: s.confidence, reverse=True)
            all_signals = all_signals[:self.config.max_signals_per_tick]

        # Phase 4: Deliver signals
        for signal in all_signals:
            self._last_signals[signal.strategy_id] = now
            self._signal_count += 1
            # Log to file
            self._log_signal(signal)
            # Store in memory buffer for Command Center queries
            sig_dict = signal.to_dict()
            self._recent_signals.append(sig_dict)
            if len(self._recent_signals) > self._recent_buffer_size:
                self._recent_signals = self._recent_signals[-self._recent_buffer_size:]
            # Push to handlers
            for handler in self._signal_handlers:
                try:
                    handler(signal)
                except Exception as exc:
                    logger.error("Signal handler error: %s", exc)

        if all_signals:
            logger.info(
                "Tick %d: %d signals produced (confidence: %s)",
                self._tick_count,
                len(all_signals),
                ", ".join(f"{s.strategy_id}={s.confidence:.2f}" for s in all_signals[:5]),
            )

        return all_signals

    # ------------------------------------------------------------------
    # Inter-strategy conflict detection & resolution
    # ------------------------------------------------------------------

    def _detect_conflicts(
        self, signals: List[Signal]
    ) -> List[Tuple[List[Signal], List[Signal]]]:
        """
        Detect contradictory signals within 5-second windows.

        Groups signals by symbol and 5-second time window. Identifies groups
        where both LONG and SHORT signals exist — these are contradictions.

        Returns:
            List of (conflict_group, suppressed) tuples:
            - conflict_group: the signals involved in the conflict
            - suppressed: signals marked for suppression
        """
        if len(signals) < 2:
            return []

        # Group by (symbol, 5-second window)
        windows: Dict[Tuple[str, int], List[Signal]] = defaultdict(list)
        for sig in signals:
            window_key = int(sig.timestamp / 5.0)
            symbol = sig.symbol or "__global__"
            windows[(symbol, window_key)].append(sig)

        conflicts: List[Tuple[List[Signal], List[Signal]]] = []

        for key, group in windows.items():
            symbol, _ = key
            # Quick check: does this group have both directions?
            directions = {s.direction for s in group}
            if Direction.LONG not in directions or Direction.SHORT not in directions:
                continue

            # Separate by direction
            longs = [s for s in group if s.direction == Direction.LONG]
            shorts = [s for s in group if s.direction == Direction.SHORT]

            # Resolve and record
            suppressed = self._resolve_conflicts(longs, shorts, symbol)
            if suppressed:
                conflict_group = longs + shorts
                conflicts.append((conflict_group, suppressed))

        return conflicts

    def _resolve_conflicts(
        self,
        longs: List[Signal],
        shorts: List[Signal],
        symbol: str,
    ) -> List[Signal]:
        """
        Resolve a LONG vs SHORT conflict for the same symbol/window.

        Resolution rules (applied in order):
        1. **Extreme confidence gap** — if one signal has confidence >= 0.9
           and the other < 0.7, suppress the lower-confidence one.
        2. **Layer priority** — if confidence is similar, Layer 2 signals
           take priority over Layer 1 (alpha > structural).
        3. **Same layer, keep all** — if both are same layer and similar
           confidence, keep both (they may represent different aspects).

        Returns:
            List of signals to suppress.
        """
        suppressed: List[Signal] = []

        # --- Rule 1: Extreme confidence gap ---
        # Check if any signal has >= 0.9 confidence vs any < 0.7
        high_conf = [s for s in longs + shorts if s.confidence >= 0.9]
        low_conf = [s for s in longs + shorts if s.confidence < 0.7]

        if high_conf and low_conf:
            # Find which direction the high-confidence signal is on
            high_directions = {s.direction for s in high_conf}
            for lc in low_conf:
                if lc.direction not in high_directions:
                    suppressed.append(lc)
                    logger.warning(
                        "CONFLICT [%s]: suppressed %s (conf=%.2f, str=%s) "
                        "vs %s (conf=%.2f, str=%s) — extreme confidence gap",
                        symbol,
                        lc.direction.value,
                        lc.confidence,
                        lc.strategy_id,
                        "HIGH" if high_conf else "?",
                        max(s.confidence for s in high_conf),
                        ",".join(s.strategy_id for s in high_conf),
                    )
            return suppressed

        # --- Rule 2: Layer priority (similar confidence) ---
        # Group signals by layer (across both directions)
        all_by_layer: Dict[str, List[Signal]] = defaultdict(list)
        for s in longs + shorts:
            layer = s._layer or self._get_strategy_layer(s.strategy_id)
            all_by_layer[layer].append(s)

        all_layers = set(all_by_layer.keys())

        # Check if there are signals on different layers
        if len(all_layers) > 1:
            # Find the highest-priority layer present
            max_priority = max(self._layer_priority(l) for l in all_layers)
            max_priority_layers = {l for l in all_layers if self._layer_priority(l) == max_priority}

            # Find the lowest-priority layer present
            min_priority = min(self._layer_priority(l) for l in all_layers)
            min_priority_layers = {l for l in all_layers if self._layer_priority(l) == min_priority}

            # If there's a clear layer gap (e.g., layer2 vs layer1), suppress lower-priority
            if max_priority > min_priority:
                for layer in min_priority_layers:
                    for s in all_by_layer[layer]:
                        if s not in suppressed:
                            suppressed.append(s)
                            logger.info(
                                "CONFLICT [%s]: suppressed %s (conf=%.2f, str=%s, layer=%s) "
                                "in favor of higher-layer signal",
                                symbol,
                                s.direction.value,
                                s.confidence,
                                s.strategy_id,
                                layer,
                            )
        else:
            # Same layer for all signals — check confidence spread
            layer = list(all_layers)[0]
            long_max = max(s.confidence for s in longs) if longs else 0.0
            short_max = max(s.confidence for s in shorts) if shorts else 0.0
            confidence_spread = abs(long_max - short_max)

            # If confidence spread is small (<=0.15), they're "similar"
            # Same layer + similar confidence = keep both (Rule 3)
            # No suppression needed here

        # --- Rule 3: Same layer, similar confidence — keep all ---
        # No suppression needed; different strategies may capture different aspects

        return suppressed

    def _get_strategy_layer(self, strategy_id: str) -> str:
        """Look up the layer for a strategy by scanning registered strategies."""
        for strat in self._strategies:
            if strat.strategy_id == strategy_id:
                return strat.layer
        return "layer1"  # default fallback

    @staticmethod
    def _layer_priority(layer: str) -> int:
        """
        Return numeric priority for a layer string.
        Higher = more important.

        Layer hierarchy:
            layer1 (structural)  -> 1
            layer2 (alpha)       -> 2
            layer3 (Micro-Signal) -> 3
            full_data (IV/Prob/Skew) -> 4
        """
        priority_map = {
            "layer1": 1,
            "layer2": 2,
            "layer3": 3,
            "full_data": 4,
        }
        return priority_map.get(layer, 1)

    def _filter_signals(
        self, signals: List[Signal], conflicts: List[Tuple[List[Signal], List[Signal]]]
    ) -> List[Signal]:
        """
        Remove suppressed signals from the signal list.

        Args:
            signals: All signals after regime filtering.
            conflicts: Output from _detect_conflicts().

        Returns:
            Filtered signal list with suppressed signals removed.
        """
        suppressed_ids: Set[int] = set()
        for _, suppressed in conflicts:
            for s in suppressed:
                suppressed_ids.add(id(s))

        filtered = [s for s in signals if id(s) not in suppressed_ids]
        total_suppressed = len(signals) - len(filtered)
        if total_suppressed > 0:
            logger.info(
                "Conflict resolution: suppressed %d of %d signals",
                total_suppressed,
                len(signals),
            )
        return filtered

    # ------------------------------------------------------------------
    # Signal logging
    # ------------------------------------------------------------------

    def _log_signal(self, signal: Signal) -> None:
        """Delegate signal logging to the SignalTracker (per-symbol log).

        The SignalTracker owns all signal persistence — it writes to
        log/signals_{SYMBOL}.jsonl with full fields (signal_id, symbol,
        strategy_id, etc.). No global log is maintained.
        """
        if self._signal_tracker is not None:
            try:
                self._signal_tracker.track(signal.to_dict())
            except Exception as exc:
                logger.warning("Failed to log signal via tracker: %s", exc)
        else:
            logger.warning("SignalTracker not configured — signal not logged: %s", signal.strategy_id)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_recent_signals(self, n: int = 20) -> List[Dict[str, Any]]:
        """Return the last N signals as dicts (for Command Center micro-signal overlay)."""
        return list(self._recent_signals[-n:])

    @property
    def strategy_count(self) -> int:
        return len(self._strategies)

    @property
    def signal_count(self) -> int:
        return self._signal_count

    def get_status(self) -> Dict[str, Any]:
        """Engine status for Command Center."""
        return {
            "running": self._running,
            "strategies": len(self._strategies),
            "enabled_strategies": sum(1 for s in self._strategies if s.enabled),
            "total_signals": self._signal_count,
            "ticks_processed": self._tick_count,
        }

    def reset_recent_signals(self) -> None:
        """Clear the in-memory signal buffer (e.g. on restart)."""
        self._recent_signals.clear()
