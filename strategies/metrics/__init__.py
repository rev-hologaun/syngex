"""
strategies/metrics — Metrics Collector

Thread-safe metrics storage for Flask API exposure.
"""

from .collector import collector

__all__ = ["collector"]
