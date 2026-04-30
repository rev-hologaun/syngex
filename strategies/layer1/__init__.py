"""
strategies/layer1/ — Core Structural Strategies

Layer 1: Pure GEX-driven structural trades. No indicators, no volume,
no order-flow — just gamma walls, flip points, and magnet strikes.

Strategies:
    - Gamma Wall Bounce    : Mean reversion at call/put walls
    - Magnet & Accelerate  : Two-phase magnet pull + breakout
    - Gamma Flip Breakout  : Regime boundary trades
    - Gamma Squeeze        : Pin detection + wall-break breakout
    - GEX Imbalance        : Call/put GEX ratio dealer bias
    - Confluence Reversal  : Technical S/R + gamma wall double-stacked levels
    - Vol Compression Range: Range scalping in positive gamma regime
    - GEX Divergence       : Fade exhausted trends via price/GEX slope divergence
"""

from .gamma_wall_bounce import GammaWallBounce
from .magnet_accelerate import MagnetAccelerate
from .gamma_flip_breakout import GammaFlipBreakout
from .gamma_squeeze import GammaSqueeze
from .gex_imbalance import GEXImbalance
from .confluence_reversal import ConfluenceReversal
from .vol_compression_range import VolCompressionRange
from .gex_divergence import GEXDivergence

__all__ = [
    "GammaWallBounce",
    "MagnetAccelerate",
    "GammaFlipBreakout",
    "GammaSqueeze",
    "GEXImbalance",
    "ConfluenceReversal",
    "VolCompressionRange",
    "GEXDivergence",
]
