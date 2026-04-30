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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

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
    signal_log_path: str = "log/signals.jsonl"
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

    def __init__(self, config: Optional[EngineConfig] = None) -> None:
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

        # Ensure log directory exists
        log_path = Path(self.config.signal_log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

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
                    # Apply minimum confidence threshold
                    if signal.confidence < self.config.min_confidence:
                        continue
                    # Dedup: skip if same strategy fired recently
                    last_time = self._last_signals.get(signal.strategy_id, 0)
                    if now - last_time < self.config.dedup_window_seconds:
                        continue
                    all_signals.append(signal)
                    self._last_signals[signal.strategy_id] = now
            except Exception as exc:
                logger.error("Strategy %s error: %s", strategy.strategy_id, exc, exc_info=True)

        # Phase 2: Apply regime filter
        if self._filter_callback:
            filtered = [s for s in all_signals if self._filter_callback(s)]
            blocked = len(all_signals) - len(filtered)
            if blocked > 0:
                logger.debug("Regime filter blocked %d signals", blocked)
            all_signals = filtered

        # Phase 3: Cap signals per tick
        if len(all_signals) > self.config.max_signals_per_tick:
            # Keep highest confidence signals
            all_signals.sort(key=lambda s: s.confidence, reverse=True)
            all_signals = all_signals[:self.config.max_signals_per_tick]

        # Phase 4: Deliver signals
        for signal in all_signals:
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
    # Signal logging
    # ------------------------------------------------------------------

    def _log_signal(self, signal: Signal) -> None:
        """Append signal to JSONL log file for backtesting."""
        try:
            log_path = Path(self.config.signal_log_path)
            with open(log_path, "a") as f:
                f.write(json.dumps(signal.to_dict()) + "\n")
        except Exception as exc:
            logger.warning("Failed to log signal: %s", exc)

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
