"""strategies/si_monitor.py — Structural Integrity sidecar monitor.

Computes SI scores from a snapshot of market data. Pure data collection,
no signal emission, no strategy integration. Designed to be called once
per tick per symbol from the orchestrator.
"""

from __future__ import annotations

import time
from typing import Any, Dict

from strategies.si_component import StructuralIntegrity, MomentumValidator, LiquidityAnchor, RegimeCoherence


class SIMonitor:
    """One-shot SI computation for monitoring/analysis."""

    def __init__(self, net_gamma: float, regime: str, delta_density: float,
                 volume_zscore: float, distance_to_wall_pct: float,
                 wall_depth: float, book_depth: float, signal_direction: str = "long"):
        self.net_gamma = net_gamma
        self.regime = regime
        self.signal_direction = signal_direction
        self._mv = MomentumValidator(volume_zscore, delta_density, 0.0, net_gamma)
        self._la = LiquidityAnchor(distance_to_wall_pct, wall_depth, book_depth, 0.0)
        self._rc = RegimeCoherence(signal_direction, regime, net_gamma)
        self._si = StructuralIntegrity(self._mv, self._la, self._rc)

    def compute(self) -> Dict[str, Any]:
        """Return SI snapshot as a dict."""
        return {
            "timestamp": time.time(),
            "net_gamma": round(self.net_gamma, 2),
            "regime": self.regime,
            "signal_direction": self.signal_direction,
            "si_score": round(self._si.compute(), 4),
            "momentum": round(self._si.get_scores()["momentum"], 4),
            "liquidity": round(self._si.get_scores()["liquidity"], 4),
            "regime_coherence": round(self._si.get_scores()["regime"], 4),
        }
