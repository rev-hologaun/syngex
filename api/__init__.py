"""
Syngex API Layer

Provides health checks and component status interfaces.
"""

from .health import HealthCheckService

__all__ = ["HealthCheckService"]
__version__ = "1.0.0"
