"""
strategies/layer2/vortex_compression_breakout.py — Vortex Compression Breakout

"Coiled spring" micro-structure strategy. When bid-ask spread compresses to
extreme lows while liquidity density remains high, it signals a dense
battleground — not a hollow spread. Entry on spread widening + volume surge.

LONG: Spread z-score < -2.0 (compression)
      AND liquidity density > threshold (dense, not hollow)
      AND volume spike > 1.5× (surge on the snap)
      AND spread widening > 2σ (spring uncoiled)

SHORT: Same conditions but spread widening in opposite direction

Hard gates (all must pass):
    Gate A: spread_z_score < -2.0 — compression in bottom ~2.5% of 30m
    Gate B: liquidity_density > threshold — dense compression (not hollow)
    Gate C: volume_spike > 1.5× — volume surge confirming the snap
    Gate D: spread widening velocity > threshold — spring actually uncoiled

Confidence model (7 components, sum to 1.0):
    1. Spread compression depth  (0.0–0.25) — how extreme the compression is
    2. Liquidity density         (0.0–0.20) — how dense the compression is
    3. Participant equilibrium   (0.0–0.10) — balanced participants on both sides
    4. Volume spike magnitude    (0.0–0.15) — how strong the volume surge is
    5. Spread widening velocity  (0.0–0.10) — how fast the spread is expanding
    6. VAMP validation           (0.0–0.10) — VAMP direction aligns with signal
    7. GEX regime alignment      (0.0–0.10) — signal direction matches GEX bias
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_SPREAD_ZSCORE_5M,
    KEY_LIQUIDITY_DENSITY_5M,
    KEY_PARTICIPANT_EQUILIBRIUM_5M,
    KEY_VOLUME_SPIKE_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_VOLUME_5M,
)

logger = logging.getLogger("Syngex.Strategies.VortexCompressionBreakout")

MIN_CONFIDENCE = 0.30


class VortexCompressionBreakout(BaseStrategy):
    """
    Vortex Compression Breakout strategy — "coiled spring" micro-structure detection.

    Detects when bid-ask spread compresses to extreme lows while liquidity density
    remains high, signaling a dense battleground. Entry occurs on spread widening
    combined with a volume surge.

    LONG: Spread z-score < -2.0 AND liquidity density > threshold
          AND volume spike > 1.5× AND spread widening confirmed
    SHORT: Same conditions but spread widening in opposite direction
    """

    strategy_id = "vortex_compression_breakout"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for vortex compression breakout signal.

        Returns a single LONG or SHORT signal when conditions are met,
        or empty list when gates fail or no clear signal.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        self._apply_params(data)
        rolling_data = data.get("rolling_data", {})
        params = self._params
        gex_calc = data.get("gex_calculator")
        regime = data.get("regime", "")

        # 1. Read rolling windows
        min_data_points = params.get("min_data_points", 10)
        spread_z_window = rolling_data.get(KEY_SPREAD_ZSCORE_5M)
        liq_density_window = rolling_data.get(KEY_LIQUIDITY_DENSITY_5M)
        part_eq_window = rolling_data.get(KEY_PARTICIPANT_EQUILIBRIUM_5M)
        vol_spike_window = rolling_data.get(KEY_VOLUME_SPIKE_5M)

        if not spread_z_window or spread_z_window.count < min_data_points:
            return []
        if not liq_density_window or liq_density_window.count < min_data_points:
            return []
        if not part_eq_window or part_eq_window.count < min_data_points:
            return []
        if not vol_spike_window or vol_spike_window.count < 5:
            return []

        current_spread_z = spread_z_window.values[-1]
        current_liq_density = liq_density_window.values[-1]
        current_part_eq = part_eq_window.values[-1]
        current_vol_spike = vol_spike_window.values[-1]

        # 2. Get spread data for widening velocity
        spread_window = rolling_data.get(KEY_DEPTH_SPREAD_5M)
        current_spread = spread_window.latest if spread_window else 0.0
        prev_spread = spread_window.values[-2] if spread_window and spread_window.count >= 2 else current_spread

        # 3. Read thresholds
        spread_z_threshold = params.get("spread_z_threshold", -2.0)
        liq_density_threshold = params.get("liq_density_threshold", 5000.0)
        vol_spike_threshold = params.get("vol_spike_threshold", 1.5)
        spread_widening_threshold = params.get("spread_widening_threshold", 0.0)

        # 4. Evaluate hard gates
        direction = None
        gate_a = False
        gate_b = False
        gate_c = False
        gate_d = False

        # Gate A: spread compression
        gate_a = current_spread_z < spread_z_threshold

        # Gate B: liquidity density above threshold
        gate_b = current_liq_density > liq_density_threshold

        # Gate C: volume spike
        gate_c = current_vol_spike > vol_spike_threshold

        # Gate D: spread widening (current > prev means spread expanded = spring uncoiled)
        if prev_spread > 0:
            spread_widening = (current_spread - prev_spread) / prev_spread
        else:
            spread_widening = 0.0
        gate_d = spread_widening > spread_widening_threshold

        # All 4 gates must pass
        if not (gate_a and gate_b and gate_c and gate_d):
            return []

        # Determine direction from participant equilibrium
        part_eq_threshold = params.get("participant_equilibrium_threshold", 1.0)
        if current_part_eq > part_eq_threshold:
            direction = "LONG"
        else:
            direction = "SHORT"

        # 5. VAMP validation
        use_vamp_validation = params.get("use_vamp_validation", True)
        vamp_validated = True
        if use_vamp_validation:
            vamp_validated = self._vamp_validation(rolling_data, direction)

        if not vamp_validated:
            return []

        # 6. Compute confidence (7-component model)
        confidence = self._compute_confidence(
            current_spread_z, current_liq_density, current_part_eq,
            current_vol_spike, spread_widening, direction,
            rolling_data, data, params, regime, gex_calc,
        )

        min_confidence = MIN_CONFIDENCE
        max_confidence = 1.0
        confidence = max(min_confidence, confidence)

        if confidence < min_confidence:
            return []

        # 7. Build signal
        stop_pct = params.get("stop_pct", 0.005)
        target_risk_mult = params.get("target_risk_mult", 2.0)
        entry = underlying_price
        stop_distance = entry * stop_pct

        if direction == "LONG":
            stop = entry - stop_distance
            target = entry + (stop_distance * target_risk_mult)
        else:
            stop = entry + stop_distance
            target = entry - (stop_distance * target_risk_mult)

        direction_enum = Direction.LONG if direction == "LONG" else Direction.SHORT

        return [Signal(
            direction=direction_enum,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Vortex {direction}: SpreadZ={current_spread_z:.3f}, "
                f"LiqDens={current_liq_density:.0f}, VolSpike={current_vol_spike:.2f}×"
            ),
            metadata={
                "direction": direction,
                "spread_z_score": round(current_spread_z, 4),
                "liquidity_density": round(current_liq_density, 2),
                "participant_equilibrium": round(current_part_eq, 4),
                "volume_spike": round(current_vol_spike, 4),
                "spread_widening": round(spread_widening, 6),
                "gates": {
                    "A_spread_compression": gate_a,
                    "B_liquidity_density": gate_b,
                    "C_volume_spike": gate_c,
                    "D_spread_widening": gate_d,
                    "D_vamp": vamp_validated,
                },
                "regime": regime,
            },
        )]

    def _vamp_validation(self, rolling_data: Dict[str, Any], direction: str) -> bool:
        """
        VAMP validation: VAMP direction should align with signal direction.
        """
        vamp_levels = rolling_data.get("vamp_levels")
        if not vamp_levels:
            return True
        vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)
        if direction == "LONG":
            return vamp_mid_dev >= -0.001
        else:
            return vamp_mid_dev <= 0.001

    def _compute_confidence(
        self,
        spread_z: float,
        liq_density: float,
        part_eq: float,
        vol_spike: float,
        spread_widening: float,
        direction: str,
        rolling_data: Dict[str, Any],
        data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str,
        gex_calc: Any,
    ) -> float:
        """
        Compute 7-component confidence score (sum to 1.0).

        Returns 0.0–1.0.
        """
        liq_density_threshold = params.get("liq_density_threshold", 5000.0)
        vol_spike_threshold = params.get("vol_spike_threshold", 1.5)
        spread_z_threshold = params.get("spread_z_threshold", -2.0)

        # 1. Spread compression depth (0.0–0.25)
        # More negative = deeper compression = higher confidence
        # -2.0 = baseline, -4.0 = max
        conf_spread = 0.0
        if spread_z < spread_z_threshold:
            conf_spread = min(0.25, 0.25 * min(1.0, abs(spread_z) / 4.0))

        # 2. Liquidity density (0.0–0.20)
        conf_liq = 0.0
        if liq_density > liq_density_threshold:
            conf_liq = min(0.20, 0.20 * min(1.0, liq_density / (liq_density_threshold * 2)))

        # 3. Participant equilibrium (0.0–0.10)
        conf_part = 0.05  # baseline
        if direction == "LONG" and part_eq > 1.0:
            conf_part = min(0.10, 0.05 + 0.05 * min(1.0, (part_eq - 1.0) * 2))
        elif direction == "SHORT" and part_eq < 1.0:
            conf_part = min(0.10, 0.05 + 0.05 * min(1.0, (1.0 - part_eq) * 2))

        # 4. Volume spike magnitude (0.0–0.15)
        conf_vol = 0.05  # baseline (gate C passed)
        if vol_spike > vol_spike_threshold:
            conf_vol = min(0.15, 0.05 + 0.10 * min(1.0, (vol_spike - vol_spike_threshold) / vol_spike_threshold))

        # 5. Spread widening velocity (0.0–0.10)
        conf_widen = 0.0
        if spread_widening > 0:
            conf_widen = min(0.10, 0.10 * min(1.0, spread_widening / 0.05))

        # 6. VAMP validation (0.0–0.10)
        conf_vamp = 0.05
        vamp_levels = rolling_data.get("vamp_levels")
        if vamp_levels:
            vamp_mid_dev = vamp_levels.get("vamp_mid_dev", 0)
            if direction == "LONG" and vamp_mid_dev >= 0:
                conf_vamp = 0.10
            elif direction == "SHORT" and vamp_mid_dev <= 0:
                conf_vamp = 0.10

        # 7. GEX regime alignment (0.0–0.10)
        conf_gex = 0.05
        if gex_calc and regime:
            net_gamma = gex_calc.get_net_gamma() if hasattr(gex_calc, "get_net_gamma") else 0
            if direction == "LONG" and net_gamma > 0:
                conf_gex = 0.10
            elif direction == "SHORT" and net_gamma < 0:
                conf_gex = 0.10

        return min(1.0, max(0.0, conf_spread + conf_liq + conf_part + conf_vol + conf_widen + conf_vamp + conf_gex))
