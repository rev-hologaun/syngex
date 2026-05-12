"""
strategies/volume_filter.py — Global Volume Confirmation Filter

Evaluates whether current rolling volume supports trading activity.
Low volume = weak conviction = higher fakeout rate across all strategies.
"""

from __future__ import annotations
from typing import Any, Dict

from strategies.rolling_keys import KEY_VOLUME_5M


class VolumeFilter:
    """
    Global volume confirmation filter.

    Returns a dict with:
      - status: "HIGH" | "NORMAL" | "LOW" | "CRITICAL"
      - ratio: current_volume / 20-period_avg_volume
      - recommended: bool — should the current strategy fire?
      - reason: str — explanation
    """

    # Thresholds are inlined in evaluate() — this dict was dead config
    # (ratio < 0.01 → CRITICAL via the else branch)
    THRESHOLD_HIGH = 1.3
    THRESHOLD_NORMAL = 1.0
    THRESHOLD_LOW = 0.01

    @staticmethod
    def evaluate(rolling_data: Dict[str, Any], min_confidence: float = 0.0) -> Dict:
        """
        Check volume state and determine if signals should fire.

        Args:
            rolling_data: Dict containing rolling volume data
            min_confidence: Minimum confidence required for signals to fire.
                           0.0 = no filter (all signals OK).
                           >0.0 = only fire if confidence >= this threshold.
        """
        vol_window = rolling_data.get(KEY_VOLUME_5M)

        if vol_window is None or vol_window.mean is None or vol_window.mean == 0:
            return {
                "status": "UNKNOWN",
                "ratio": 0.0,
                "recommended": True,
                "reason": "No volume data"
            }

        current_vol = vol_window.latest
        avg_vol = vol_window.mean
        ratio = current_vol / avg_vol if avg_vol > 0 else 0.0

        if ratio >= 1.3:
            status = "HIGH"
            reason = "Volume above average"
        elif ratio >= 1.0:
            status = "NORMAL"
            reason = "Volume at average"
        elif ratio >= 0.01:
            status = "LOW"
            reason = f"Volume at {ratio:.0%} of average"
        else:
            status = "CRITICAL"
            reason = f"Volume at {ratio:.0%} of average"

        if status in ("HIGH", "NORMAL"):
            recommended = True
        elif status == "LOW":
            recommended = min_confidence >= 0.70
        else:
            recommended = False

        return {
            "status": status,
            "ratio": round(ratio, 3),
            "recommended": recommended,
            "reason": reason
        }
