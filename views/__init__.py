"""SYNGEX views — modular dashboard view components.

Each view is a self-contained renderer that accepts data and produces
a Rich-compatible Panel. Views are auto-discovered from this package.
"""

from .gamma_magnet import GammaMagnetView, GammaProfileData

__all__ = ["GammaMagnetView", "GammaProfileData"]
