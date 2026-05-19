"""
Sample signal fixtures for testing.

Provides sample Signal, OpenSignal, and ResolvedSignal objects
for unit and integration tests.
"""

import time
from typing import Any, Dict

from strategies.signal import Direction, Signal
from strategies.signal_tracker import OpenSignal, ResolvedSignal, SignalOutcome


# =============================================================================
# Sample Signal Objects
# =============================================================================

def create_sample_signal(
    direction: Direction = Direction.LONG,
    confidence: float = 0.75,
    entry: float = 195.50,
    stop: float = 194.20,
    target: float = 197.80,
    strategy_id: str = "test_strategy",
    symbol: str = "TSLA",
    reason: str = "Test signal",
    timestamp: float | None = None,
) -> Signal:
    """Create a sample Signal object with defaults."""
    return Signal(
        direction=direction,
        confidence=confidence,
        entry=entry,
        stop=stop,
        target=target,
        strategy_id=strategy_id,
        symbol=symbol,
        reason=reason,
        timestamp=timestamp or time.time(),
        expiry="2024-05-19",
        metadata={"test": True},
    )


SAMPLE_SIGNAL_LONG: Signal = create_sample_signal(
    direction=Direction.LONG,
    confidence=0.75,
    strategy_id="gamma_wall_bounce",
    reason="Call wall at 196 rejected price",
)

SAMPLE_SIGNAL_SHORT: Signal = create_sample_signal(
    direction=Direction.SHORT,
    confidence=0.68,
    strategy_id="gamma_flip_breakout",
    reason="Break below gamma flip",
)

SAMPLE_SIGNAL_LOW_CONFIDENCE: Signal = create_sample_signal(
    confidence=0.35,  # Below default threshold
    strategy_id="weak_strategy",
    reason="Low confidence signal",
)

SAMPLE_SIGNAL_HIGH_CONFIDENCE: Signal = create_sample_signal(
    confidence=0.92,  # Extreme confidence
    strategy_id="strong_strategy",
    reason="Very strong setup",
)

SAMPLE_SIGNAL_LAYER1: Signal = create_sample_signal(
    strategy_id="gamma_squeeze",
    layer="layer1",
    confidence=0.65,
)

SAMPLE_SIGNAL_LAYER2: Signal = create_sample_signal(
    strategy_id="delta_gamma_squeeze",
    layer="layer2",
    confidence=0.78,
)

SAMPLE_SIGNAL_LAYER3: Signal = create_sample_signal(
    strategy_id="theta_burn",
    layer="layer3",
    confidence=0.70,
)

SAMPLE_SIGNAL_FULL_DATA: Signal = create_sample_signal(
    strategy_id="prob_weighted_magnet",
    layer="full_data",
    confidence=0.82,
)


# =============================================================================
# Sample OpenSignal Objects
# =============================================================================

def create_sample_open_signal(
    signal: Signal | None = None,
    entry_price: float = 195.50,
    timestamp: float | None = None,
) -> OpenSignal:
    """Create a sample OpenSignal object."""
    if signal is None:
        signal = SAMPLE_SIGNAL_LONG

    return OpenSignal(
        signal=signal,
        entry_price=entry_price,
        open_timestamp=timestamp or time.time(),
    )


SAMPLE_OPEN_SIGNAL: OpenSignal = create_sample_open_signal(
    signal=SAMPLE_SIGNAL_LONG,
    entry_price=195.50,
)


# =============================================================================
# Sample ResolvedSignal Objects
# =============================================================================

def create_sample_resolved_signal(
    open_signal: OpenSignal | None = None,
    outcome: SignalOutcome = SignalOutcome.TAKE_PROFIT,
    exit_price: float = 197.80,
    exit_timestamp: float | None = None,
    pnl: float = 230.0,
    hold_time: float = 60.0,
) -> ResolvedSignal:
    """Create a sample ResolvedSignal object."""
    if open_signal is None:
        open_signal = SAMPLE_OPEN_SIGNAL

    return ResolvedSignal(
        open_signal=open_signal,
        outcome=outcome,
        exit_price=exit_price,
        exit_timestamp=exit_timestamp or time.time(),
        pnl=pnl,
        hold_time=hold_time,
    )


SAMPLE_RESOLVED_SIGNAL_TP: ResolvedSignal = create_sample_resolved_signal(
    outcome=SignalOutcome.TAKE_PROFIT,
    exit_price=197.80,
    pnl=230.0,
)

SAMPLE_RESOLVED_SIGNAL_SL: ResolvedSignal = create_sample_resolved_signal(
    outcome=SignalOutcome.STOP_LOSS,
    exit_price=194.20,
    pnl=-130.0,
)

SAMPLE_RESOLVED_SIGNAL_EXPIRED: ResolvedSignal = create_sample_resolved_signal(
    outcome=SignalOutcome.EXPIRED,
    exit_price=195.50,
    pnl=0.0,
)


# =============================================================================
# Sample Outcome Data
# =============================================================================

SAMPLE_OUTCOME_STATS: Dict[str, Any] = {
    "total_signals": 100,
    "resolved_signals": 85,
    "take_profits": 45,
    "stop_losses": 30,
    "expired": 10,
    "win_rate": 0.529,  # 45 / 85
    "total_pnl": 4500.0,
    "avg_pnl": 52.94,
    "avg_hold_time": 120.5,  # seconds
}

SAMPLE_STRATEGY_OUTCOMES: Dict[str, Any] = {
    "gamma_wall_bounce": {
        "total": 25,
        "wins": 15,
        "losses": 8,
        "expired": 2,
        "win_rate": 0.652,
        "total_pnl": 1850.0,
    },
    "gamma_flip_breakout": {
        "total": 20,
        "wins": 10,
        "losses": 9,
        "expired": 1,
        "win_rate": 0.526,
        "total_pnl": 650.0,
    },
    "gamma_squeeze": {
        "total": 15,
        "wins": 8,
        "losses": 6,
        "expired": 1,
        "win_rate": 0.571,
        "total_pnl": 420.0,
    },
}


# =============================================================================
# Signal Lists for Testing
# =============================================================================

SAMPLE_SIGNAL_LIST: list[Signal] = [
    SAMPLE_SIGNAL_LONG,
    SAMPLE_SIGNAL_SHORT,
    SAMPLE_SIGNAL_LOW_CONFIDENCE,
    SAMPLE_SIGNAL_HIGH_CONFIDENCE,
]

SAMPLE_LAYER1_SIGNALS: list[Signal] = [
    create_sample_signal(
        direction=Direction.LONG,
        confidence=0.68,
        strategy_id="gamma_wall_bounce",
        reason="Wall bounce",
    ),
    create_sample_signal(
        direction=Direction.SHORT,
        confidence=0.72,
        strategy_id="gamma_flip_breakout",
        reason="Flip breakout",
    ),
]

SAMPLE_LAYER2_SIGNALS: list[Signal] = [
    create_sample_signal(
        direction=Direction.LONG,
        confidence=0.75,
        strategy_id="delta_gamma_squeeze",
        reason="Delta gamma squeeze",
    ),
    create_sample_signal(
        direction=Direction.SHORT,
        confidence=0.78,
        strategy_id="iv_gex_divergence",
        reason="IV/GEX divergence",
    ),
]
