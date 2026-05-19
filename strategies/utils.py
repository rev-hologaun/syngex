"""
strategies/utils.py — Shared utility functions for all strategies

Common utilities used across strategy implementations:
    - Confidence normalization
    - Common calculations
    - Helper functions
"""

from __future__ import annotations


def normalize_confidence(value: float, min_val: float, max_val: float, default: float = 0.5) -> float:
    """
    Normalize a confidence value to 0.0-1.0 range.

    This is the standard normalization function used across all strategies
    to ensure consistent confidence calculation behavior.

    Args:
        value: The raw confidence value to normalize
        min_val: The minimum expected value (maps to 0.0)
        max_val: The maximum expected value (maps to 1.0)
        default: Value to return if range is invalid (default: 0.5)

    Returns:
        Normalized value clamped to [0.0, 1.0]

    Example:
        >>> normalize_confidence(0.20, 0.15, 0.25)
        0.5
        >>> normalize_confidence(0.25, 0.15, 0.25)
        1.0
        >>> normalize_confidence(0.15, 0.15, 0.25)
        0.0
    """
    range_val = max_val - min_val
    if range_val <= 0:
        return default
    return max(0.0, min(1.0, (value - min_val) / range_val))
