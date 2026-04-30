"""
strategies/signal.py — The Signal class

Standardized output format for ALL strategies. Every strategy produces
Signal objects. The StrategyEngine collects, filters, and routes them.

Usage:
    signal = Signal(
        direction="LONG",
        confidence=0.78,
        entry=195.50,
        stop=194.20,
        target=197.80,
        expiry="2026-05-19",
        strategy_id="gamma_wall_bounce",
        reason="Call wall at 196 rejected price",
        metadata={"wall_strike": 196, "gex": 1250000},
    )
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


class SignalStrength(str, Enum):
    """Categorical strength for quick dashboard filtering."""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    EXTREME = "EXTREME"


@dataclass(frozen=True)
class Signal:
    """
    Immutable signal produced by a strategy.

    All fields are required except metadata and reason — strategies
    should always provide a human-readable reason for the signal.

    Confidence is 0.0–1.0. The StrategyEngine applies the Net Gamma
    regime filter before signals reach the dashboard.
    """
    direction: Direction
    confidence: float          # 0.0 – 1.0
    entry: float               # Target entry price
    stop: float                # Stop loss price
    target: float              # Take profit price
    strategy_id: str           # e.g. "gamma_wall_bounce"
    timestamp: float = field(default_factory=time.time)

    # Optional
    reason: str = ""
    expiry: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def risk_reward_ratio(self) -> float:
        """Risk:Reward ratio based on entry, stop, target."""
        risk = abs(self.entry - self.stop)
        reward = abs(self.target - self.entry)
        if risk == 0:
            return 0.0
        return reward / risk

    @property
    def strength(self) -> SignalStrength:
        """Map confidence to categorical strength."""
        if self.confidence >= 0.85:
            return SignalStrength.EXTREME
        elif self.confidence >= 0.70:
            return SignalStrength.STRONG
        elif self.confidence >= 0.50:
            return SignalStrength.MODERATE
        else:
            return SignalStrength.WEAK

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/dashboard."""
        return {
            "direction": self.direction.value,
            "confidence": self.confidence,
            "entry": self.entry,
            "stop": self.stop,
            "target": self.target,
            "strategy_id": self.strategy_id,
            "reason": self.reason,
            "risk_reward_ratio": round(self.risk_reward_ratio, 2),
            "strength": self.strength.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Signal:
        """Reconstruct from serialized dict."""
        return cls(
            direction=Direction(data["direction"]),
            confidence=data["confidence"],
            entry=data["entry"],
            stop=data["stop"],
            target=data["target"],
            strategy_id=data["strategy_id"],
            timestamp=data.get("timestamp", time.time()),
            reason=data.get("reason", ""),
            expiry=data.get("expiry"),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return (
            f"Signal({self.direction.value} | {self.strategy_id} | "
            f"conf={self.confidence:.2f} | strength={self.strength.value} | "
            f"RR={self.risk_reward_ratio:.2f} | {self.reason})"
        )
