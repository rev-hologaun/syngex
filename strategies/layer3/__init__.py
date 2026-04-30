"""
strategies/layer3/ — Micro-Signal Layer

Layer 3: Sub-second burst detection strategies. These operate at 1Hz
and detect the exact moment gamma/delta spikes coincide with volume
surges — the ignition signals for gamma squeezes.

Strategies:
    - GammaVolumeConvergence : Simultaneous delta + gamma + volume spike at ATM strike
    - IVBandBreakout        : IV compression-to-expansion breakout detection
    - StrikeConcentration   : Bounce/slice trades off top-OI strikes
    - ThetaBurn             : Pinning effect — range-bound bounces at gamma walls
"""

from .gamma_volume_convergence import GammaVolumeConvergence
from .iv_band_breakout import IVBandBreakout
from .strike_concentration import StrikeConcentration
from .theta_burn import ThetaBurn

__all__ = [
    "GammaVolumeConvergence",
    "IVBandBreakout",
    "StrikeConcentration",
    "ThetaBurn",
]
