"""Event System for Syngex.

Provides a pub/sub event bus for loose coupling between components.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class EventType(str, Enum):
    """Standard event types for Syngex."""

    # Data events
    DATA_UPDATED = "DATA_UPDATED"
    UNDERLYING_UPDATE = "UNDERLYING_UPDATE"
    OPTION_CHAIN_UPDATE = "OPTION_CHAIN_UPDATE"
    GEX_CALCULATED = "GEX_CALCULATED"

    # Signal events
    SIGNAL_CREATED = "SIGNAL_CREATED"
    SIGNAL_UPDATED = "SIGNAL_UPDATED"
    SIGNAL_RESOLVED = "SIGNAL_RESOLVED"

    # Strategy events
    STRATEGY_EVALUATED = "STRATEGY_EVALUATED"
    STRATEGY_ENABLED = "STRATEGY_ENABLED"
    STRATEGY_DISABLED = "STRATEGY_DISABLED"

    # System events
    COMPONENT_STARTED = "COMPONENT_STARTED"
    COMPONENT_STOPPED = "COMPONENT_STOPPED"
    CONFIG_RELOADED = "CONFIG_RELOADED"
    ERROR_OCCURRED = "ERROR_OCCURRED"


@dataclass
class Event:
    """Base event class."""

    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    source: Optional[str] = None
    correlation_id: Optional[str] = None


@dataclass
class DataUpdatedEvent(Event):
    """Event emitted when data is updated."""

    def __post_init__(self):
        self.event_type = EventType.DATA_UPDATED


@dataclass
class SignalCreatedEvent(Event):
    """Event emitted when a new signal is created."""

    def __post_init__(self):
        self.event_type = EventType.SIGNAL_CREATED


@dataclass
class SignalResolvedEvent(Event):
    """Event emitted when a signal is resolved."""

    def __post_init__(self):
        self.event_type = EventType.SIGNAL_RESOLVED


@dataclass
class StrategyEvaluatedEvent(Event):
    """Event emitted when a strategy is evaluated."""

    def __post_init__(self):
        self.event_type = EventType.STRATEGY_EVALUATED


class EventBus:
    """
    Pub/Sub event bus for component communication.

    Enables loose coupling between components by allowing them to
    publish and subscribe to events without direct dependencies.

    Example:
        ```python
        event_bus = EventBus()

        def handle_signal(event: Event):
            print(f"New signal: {event.data}")

        event_bus.subscribe('SIGNAL_CREATED', handle_signal)
        event_bus.publish('SIGNAL_CREATED', {'strategy': 'gamma_squeeze', 'direction': 'LONG'})
        ```
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the event bus.

        Args:
            logger: Optional logger for event bus events
        """
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._async_subscribers: Dict[EventType, List[Callable[[Event], Any]]] = {}
        self._logger = logger or logging.getLogger(__name__)
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._running = False

    def subscribe(
        self,
        event_type: str | EventType,
        callback: Callable[[Event], None],
    ) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        if isinstance(event_type, str):
            event_type = EventType(event_type)

        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(callback)
        self._logger.debug(f"Subscribed to {event_type.value}")

    def subscribe_async(
        self,
        event_type: str | EventType,
        callback: Callable[[Event], Any],
    ) -> None:
        """Subscribe to an event type with an async callback.

        Args:
            event_type: Type of event to subscribe to
            callback: Async function to call when event is published
        """
        if isinstance(event_type, str):
            event_type = EventType(event_type)

        if event_type not in self._async_subscribers:
            self._async_subscribers[event_type] = []

        self._async_subscribers[event_type].append(callback)
        self._logger.debug(f"Subscribed (async) to {event_type.value}")

    def unsubscribe(
        self,
        event_type: str | EventType,
        callback: Callable[[Event], None],
    ) -> bool:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove

        Returns:
            True if callback was found and removed
        """
        if isinstance(event_type, str):
            event_type = EventType(event_type)

        if event_type not in self._subscribers:
            return False

        try:
            self._subscribers[event_type].remove(callback)
            return True
        except ValueError:
            return False

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers.

        Args:
            event: Event to publish
        """
        # Call sync subscribers
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self._logger.error(f"Event handler error: {e}")

        # Queue async subscribers for later processing
        if event.event_type in self._async_subscribers:
            asyncio.create_task(self._process_async_subscribers(event))

    async def publish_async(self, event: Event) -> None:
        """Publish an event and wait for async subscribers.

        Args:
            event: Event to publish
        """
        # Call sync subscribers
        self.publish(event)

        # Wait for async subscribers
        if event.event_type in self._async_subscribers:
            await asyncio.gather(
                *[callback(event) for callback in self._async_subscribers[event.event_type]],
                return_exceptions=True,
            )

    async def _process_async_subscribers(self, event: Event) -> None:
        """Process async subscribers for an event."""
        if event.event_type not in self._async_subscribers:
            return

        for callback in self._async_subscribers[event.event_type]:
            try:
                await callback(event)
            except Exception as e:
                self._logger.error(f"Async event handler error: {e}")

    def start(self) -> None:
        """Start the event bus processing loop."""
        if self._running:
            return

        self._running = True

        async def _process_loop():
            while self._running:
                try:
                    event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                    await self.publish_async(event)
                    self._event_queue.task_done()
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._logger.error(f"Event processing error: {e}")

        self._processing_task = asyncio.create_task(_process_loop())
        self._logger.info("Event bus started")

    def stop(self) -> None:
        """Stop the event bus processing loop."""
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                asyncio.get_event_loop().run_until_complete(self._processing_task)
            except (asyncio.CancelledError, RuntimeError):
                pass
            self._processing_task = None
        self._logger.info("Event bus stopped")

    def clear(self) -> None:
        """Clear all subscribers."""
        self._subscribers.clear()
        self._async_subscribers.clear()
        self._logger.debug("Cleared all subscribers")

    @property
    def subscriber_count(self) -> Dict[str, int]:
        """Get count of subscribers per event type.

        Returns:
            Dict mapping event type to subscriber count
        """
        return {
            et.value: len(self._subscribers.get(et, [])) + len(self._async_subscribers.get(et, []))
            for et in EventType
        }


# Global event bus instance (optional, for simple use cases)
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.

    Returns:
        Global EventBus instance
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def init_event_bus(logger: Optional[logging.Logger] = None) -> EventBus:
    """Initialize the global event bus.

    Args:
        logger: Optional logger instance

    Returns:
        Initialized EventBus instance
    """
    global _global_event_bus
    _global_event_bus = EventBus(logger=logger)
    return _global_event_bus
