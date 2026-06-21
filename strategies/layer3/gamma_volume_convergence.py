"""
strategies/layer3/gamma_volume_convergence.py — Gamma-Volume Convergence (GVC) v2

"Ignition-Master" upgrade:
    - Aggressor-weighted volume (VolumeUp/Down ratio) instead of simple volume spike
    - Gamma acceleration (2nd derivative) instead of 1st derivative spike
    - Delta-gamma coupling gate to filter phantom spikes
    - ATR-normalized targets that scale with current volatility

Logic:
    - Monitor ATM strike for simultaneous delta + gamma acceleration
    - Aggressor-weighted volume confirmation (VolumeUp/Down ratio)
    - Gamma acceleration confirms ignition (2nd derivative)
    - Delta-gamma coupling ensures real signal, not phantom spike
    - ATR-normalized targets for dynamic exits

Entry:
    - LONG:  delta ↑ + gamma acceleration ↑ + aggressive VolumeUp + price rising
    - SHORT: delta ↓ + gamma acceleration ↑ + aggressive VolumeDown + price falling

Confidence factors (6 components):
    1. Delta acceleration magnitude  (0.0–0.15, soft)
    2. Gamma acceleration (hard gate — 0.0 or 0.20)
    3. Aggressor-weighted volume (hard gate — 0.0 or 0.15)
    4. Delta-gamma coupling (hard gate — 0.0 or 0.10)
    5. ATR-normalized target quality (0.0–0.10, soft)
    6. Wall proximity (0.05–0.10, soft)

This is a **filter-style convergence engine** — it produces graded signal strength
based on gamma/delta acceleration, not binary pass/fail.

Signal strength per direction:
    strength = gamma*0.30 + vol*0.25 + coupling*0.20 + price*0.15 + delta*0.10
    Emit when signal_strength >= 0.25 and gamma >= 0.05
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_PRICE_5M, KEY_VOLUME_5M, KEY_VOLUME_UP_5M, KEY_VOLUME_DOWN_5M,
    KEY_TOTAL_DELTA_5M, KEY_TOTAL_GAMMA_5M,
)

logger = logging.getLogger("Syngex.Strategies.GammaVolumeConvergence")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Delta acceleration threshold: current total_delta must exceed rolling avg
# by this ratio (15% above rolling average)
DELTA_ACCEL_RATIO = 1.15

# Delta acceleration lower bound for SHORT: current total_delta must be
# above this ratio of rolling avg (ensures delta is declining, not negative).
DELTA_ACCEL_MIN_RATIO = 0.30

# Gamma spike threshold (deprecated — not used in logic, removed)
# GAMMA_SPIKE_RATIO = 1.20  # REMOVED: dead constant, never referenced in logic

# Volume spike threshold (kept for metadata)
VOLUME_SPIKE_RATIO = 1.20

# Stop loss: 0.5% against entry
STOP_PCT = 0.005

# Minimum confidence to emit a signal (raised from 0.25)
MIN_CONFIDENCE = 0.20

# Maximum confidence — micro-signals shouldn't carry max conviction

# Minimum data points in rolling windows before trusting signals
MIN_DATA_POINTS = 3

# Price trend confirmation thresholds (over 5m window)
PRICE_UP_THRESHOLD = 0.001       # 0.1% rise over 5m window
PRICE_DOWN_THRESHOLD = -0.001    # 0.1% drop over 5m window

# Minimum absolute net_gamma for a signal to fire (dealer positioning threshold)
MIN_GAMMA_THRESHOLD = 200


class GammaVolumeConvergence(BaseStrategy):
    """
    Detects gamma/volume ignition signals (v2 Ignition-Master).

    When delta and gamma acceleration spike simultaneously at the ATM strike AND
    aggressor-weighted volume confirms (VolumeUp/Down ratio), that's the exact
    moment dealers are aggressively re-hedging — the ignition point for a
    gamma squeeze.

    Hard gates (all must pass):
        - Gamma acceleration > 0.10 (2nd derivative confirms ignition)
        - Aggressor ratio > 60% (LONG) or < 40% (SHORT) (real conviction)
        - Delta-gamma coupling >= 0.5 (not a phantom spike)

    Exits are quick: ATR-normalized target, 0.5% stop, 5–15 min hold window.
    """

    strategy_id = "gamma_volume_convergence"
    layer = "layer3"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for gamma-volume convergence signals.

        Returns empty list when no ignition signal is detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma_normalized", 0)
        regime = data.get("regime", "neutral")

        signals: List[Signal] = []

        # Check LONG ignition
        long_sig = self._check_long(
            underlying_price, gex_calc, rolling_data, net_gamma,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT ignition
        short_sig = self._check_short(
            underlying_price, gex_calc, rolling_data, net_gamma,
        )
        if short_sig:
            signals.append(short_sig)

        return signals

    # ------------------------------------------------------------------
    # LONG entry: delta ↑ + gamma acceleration ↑ + aggressive VolumeUp
    # ------------------------------------------------------------------

    def _check_long(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
    ) -> Optional[Signal]:
        """
        Evaluate LONG ignition signal.

        Conditions:
            1. Net Gamma > 0
            2. ATM delta accelerating (≥15% above rolling avg)
            3. Gamma acceleration > 0.10 (2nd derivative confirms ignition)
            4. Aggressor ratio > 0.60 (VolumeUp > 60% of total)
            5. Delta-gamma coupling >= 0.5 (not a phantom spike)
            6. Price trending UP over 5m window
        """
        # Get ATM strike
        atm_strike = self._get_atm_strike(gex_calc, price)
        if atm_strike is None:
            return None

        # Gamma magnitude gate — need meaningful dealer positioning
        if abs(net_gamma) < MIN_GAMMA_THRESHOLD:
            return None

        # Check delta acceleration
        delta_accel = self._check_delta_acceleration(rolling_data)
        if delta_accel is None or delta_accel < DELTA_ACCEL_RATIO:
            return None

        # Check gamma acceleration (2nd derivative, graded score)
        gamma_accel = self._check_gamma_acceleration(rolling_data)
        if gamma_accel is None or gamma_accel < 0.05:
            return None
        gamma_score = min(1.0, gamma_accel / 0.30)

        # Check aggressor volume (graded score)
        aggressor_ratio = self._check_aggressor_volume(rolling_data, "LONG")
        if aggressor_ratio is None or aggressor_ratio < 0.55:
            return None
        vol_score = max(0.0, min(1.0, (aggressor_ratio - 0.55) / 0.45))

        # Check delta-gamma coupling (hard gate — direction-aware threshold)
        coupling_passes = self._check_delta_gamma_coupling(delta_accel, gamma_accel, "LONG")
        if not coupling_passes:
            return None
        coupling_score = self._coupling_score(delta_accel, gamma_accel, "LONG")

        # Check price trend (graded score)
        price_score = self._price_trend_score(rolling_data, "LONG")
        if price_score < 0.1:
            return None

        # Compute signal_strength from graded components
        delta_conf = self._delta_accel_confidence(delta_accel, "LONG")
        signal_strength = (
            gamma_score * 0.30
            + vol_score * 0.25
            + coupling_score * 0.20
            + price_score * 0.15
            + delta_conf * 0.10
        )
        if signal_strength < 0.25:
            return None

        # All conditions met — compute confidence and build signal
        confidence = self._compute_confidence(
            price, delta_accel, gamma_accel,
            aggressor_ratio, rolling_data, "LONG", net_gamma, gex_calc,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal with ATR-normalized target
        entry = price
        stop = entry * (1 - STOP_PCT)
        target, atr_5m, target_mult = self._compute_atr_target(entry, rolling_data, "LONG")

        # Get wall proximity for metadata
        walls = self._safe_get_walls(gex_calc)
        call_wall_above = self._nearest_wall_above(walls, price)

        # Rolling window trend
        price_window = rolling_data.get(KEY_PRICE_5M)
        rolling_trend = price_window.trend if price_window else "UNKNOWN"

        # Actual target percentage from entry
        target_pct_actual = (target - entry) / entry if entry > 0 else 0.0

        # Gamma spike ratio (for metadata, v1 compat)
        gamma_spike = self._check_gamma_spike(rolling_data)
        if gamma_spike is None:
            gamma_spike = 0.0

        # Gamma acceleration window count
        gamma_accel_window = 0
        gamma_window = rolling_data.get(KEY_TOTAL_GAMMA_5M)
        if gamma_window is not None:
            gamma_accel_window = min(gamma_window.count, 10)

        # Coupling ratio
        coupling_ratio = (
            abs(delta_accel - 1.0) / gamma_accel if gamma_accel > 0 else 0.0
        )

        return Signal(
            direction=Direction.LONG,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"GVC ignition: ATM {atm_strike} delta x{delta_accel:.1f}, "
                f"gamma accel {gamma_accel:.3f}, aggressor {aggressor_ratio:.2f}, price UP"
            ),
            metadata={
                # === v1 fields (kept) ===
                "atm_strike": atm_strike,
                "delta_acceleration_ratio": round(delta_accel, 3),
                "gamma_spike_ratio": round(gamma_spike, 3),
                "volume_up_spike": True,
                "price_trend": "UP",
                "rolling_trend": rolling_trend,
                "net_gamma": round(net_gamma, 2),
                "gamma_regime_aligned": True,
                "call_wall_above": call_wall_above["strike"] if call_wall_above else None,
                "distance_to_call_wall_pct": (
                    round((call_wall_above["strike"] - price) / price, 4)
                    if call_wall_above else None
                ),
                "risk": round(entry - stop, 2),
                "risk_reward_ratio": round(
                    (target - entry) / (entry - stop), 2
                ) if (entry - stop) > 0 else 0,

                # === v2 new fields ===
                "gamma_acceleration": round(gamma_accel, 4),
                "gamma_accel_window": gamma_accel_window,
                "aggressor_ratio": round(aggressor_ratio, 3),
                "coupling_ratio": round(coupling_ratio, 4),
                "atr_value": round(atr_5m, 4),
                "target_mult": round(target_mult, 2),
                "target_pct_actual": round(target_pct_actual, 4),

                # === graded score components ===
                "gamma_score": round(gamma_score, 3),
                "vol_score": round(vol_score, 3),
                "coupling_score": round(coupling_score, 3),
                "price_score": round(price_score, 3),
                "signal_strength": round(signal_strength, 3),
            },
        )

    # ------------------------------------------------------------------
    # SHORT entry: delta ↓ + gamma acceleration ↑ + aggressive VolumeDown
    # ------------------------------------------------------------------

    def _check_short(
        self,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
    ) -> Optional[Signal]:
        """
        Evaluate SHORT ignition signal.

        Conditions:
            1. Net Gamma > 0
            2. ATM delta declining (DELTA_ACCEL_MIN_RATIO <= ratio < 0.85)
            3. Gamma acceleration > 0.10 (2nd derivative confirms ignition)
            4. Aggressor ratio < 0.40 (VolumeUp < 40% of total = aggressive selling)
            5. Delta-gamma coupling >= 0.5 (not a phantom spike)
            6. Price trending DOWN over 5m window
        """
        # Get ATM strike
        atm_strike = self._get_atm_strike(gex_calc, price)
        if atm_strike is None:
            return None

        # Gamma magnitude gate — need meaningful dealer positioning
        if abs(net_gamma) < MIN_GAMMA_THRESHOLD:
            return None

        # Check delta acceleration (looking for downward acceleration)
        delta_accel = self._check_delta_acceleration(rolling_data)
        if delta_accel is None:
            return None
        # For SHORT, we want delta declining but still positive:
        # DELTA_ACCEL_MIN_RATIO <= ratio < 0.85
        if delta_accel >= 0.85 or delta_accel < DELTA_ACCEL_MIN_RATIO:
            return None

        # Check gamma acceleration (2nd derivative, graded score)
        gamma_accel = self._check_gamma_acceleration(rolling_data)
        if gamma_accel is None or gamma_accel < 0.05:
            return None
        gamma_score = min(1.0, gamma_accel / 0.30)

        # Check aggressor volume (graded score)
        aggressor_ratio = self._check_aggressor_volume(rolling_data, "SHORT")
        if aggressor_ratio is None or aggressor_ratio > 0.45:
            return None
        vol_score = max(0.0, min(1.0, (0.45 - aggressor_ratio) / 0.45))

        # Check delta-gamma coupling (hard gate — direction-aware threshold)
        coupling_passes = self._check_delta_gamma_coupling(delta_accel, gamma_accel, "SHORT")
        if not coupling_passes:
            return None
        coupling_score = self._coupling_score(delta_accel, gamma_accel, "SHORT")

        # Check price trend (graded score)
        price_score = self._price_trend_score(rolling_data, "SHORT")
        if price_score < 0.1:
            return None

        # Compute signal_strength from graded components
        delta_conf = self._delta_accel_confidence(delta_accel, "SHORT")
        signal_strength = (
            gamma_score * 0.30
            + vol_score * 0.25
            + coupling_score * 0.20
            + price_score * 0.15
            + delta_conf * 0.10
        )
        if signal_strength < 0.25:
            return None

        # All conditions met — compute confidence and build signal
        confidence = self._compute_confidence(
            price, delta_accel, gamma_accel,
            aggressor_ratio, rolling_data, "SHORT", net_gamma, gex_calc,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Build signal with ATR-normalized target
        entry = price
        stop = entry * (1 + STOP_PCT)
        target, atr_5m, target_mult = self._compute_atr_target(entry, rolling_data, "SHORT")

        # Get wall proximity for metadata
        walls = self._safe_get_walls(gex_calc)
        put_wall_below = self._nearest_wall_below(walls, price)

        # Rolling window trend
        price_window = rolling_data.get(KEY_PRICE_5M)
        rolling_trend = price_window.trend if price_window else "UNKNOWN"

        # Actual target percentage from entry
        target_pct_actual = (entry - target) / entry if entry > 0 else 0.0

        # Gamma spike ratio (for metadata, v1 compat)
        gamma_spike = self._check_gamma_spike(rolling_data)
        if gamma_spike is None:
            gamma_spike = 0.0

        # Gamma acceleration window count
        gamma_accel_window = 0
        gamma_window = rolling_data.get(KEY_TOTAL_GAMMA_5M)
        if gamma_window is not None:
            gamma_accel_window = min(gamma_window.count, 10)

        # Coupling ratio
        coupling_ratio = (
            abs(delta_accel - 1.0) / gamma_accel if gamma_accel > 0 else 0.0
        )

        return Signal(
            direction=Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"GVC ignition fade: ATM {atm_strike} delta ↓, "
                f"gamma accel {gamma_accel:.3f}, aggressor {aggressor_ratio:.2f}, price DOWN"
            ),
            metadata={
                # === v1 fields (kept) ===
                "atm_strike": atm_strike,
                "delta_acceleration_ratio": round(delta_accel, 3),
                "gamma_spike_ratio": round(gamma_spike, 3),
                "volume_down_spike": True,
                "price_trend": "DOWN",
                "rolling_trend": rolling_trend,
                "net_gamma": round(net_gamma, 2),
                "gamma_regime_aligned": True,
                "put_wall_below": put_wall_below["strike"] if put_wall_below else None,
                "distance_to_put_wall_pct": (
                    round((price - put_wall_below["strike"]) / price, 4)
                    if put_wall_below else None
                ),
                "risk": round(stop - entry, 2),
                "risk_reward_ratio": round(
                    (entry - target) / (stop - entry), 2
                ) if (stop - entry) > 0 else 0,

                # === v2 new fields ===
                "gamma_acceleration": round(gamma_accel, 4),
                "gamma_accel_window": gamma_accel_window,
                "aggressor_ratio": round(aggressor_ratio, 3),
                "coupling_ratio": round(coupling_ratio, 4),
                "atr_value": round(atr_5m, 4),
                "target_mult": round(target_mult, 2),
                "target_pct_actual": round(target_pct_actual, 4),

                # === graded score components ===
                "gamma_score": round(gamma_score, 3),
                "vol_score": round(vol_score, 3),
                "coupling_score": round(coupling_score, 3),
                "price_score": round(price_score, 3),
                "signal_strength": round(signal_strength, 3),
            },
        )

    # ------------------------------------------------------------------
    # v2 Checks
    # ------------------------------------------------------------------

    @staticmethod
    def _check_aggressor_volume(
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> Optional[float]:
        """
        Check aggressor-weighted volume.

        Computes aggressor_ratio = VolumeUp / (VolumeUp + VolumeDown).
        For LONG: aggressor_ratio > 0.60 (majority aggressive buying).
        For SHORT: aggressor_ratio < 0.40 (majority aggressive selling).

        Also checks that VolumeUp (LONG) or VolumeDown (SHORT) exceeds
        1.20× its rolling average.

        Returns:
            aggressor_ratio float if gate passes, None otherwise.
        """
        vol_up = rolling_data.get(KEY_VOLUME_UP_5M)
        vol_down = rolling_data.get(KEY_VOLUME_DOWN_5M)

        if vol_up is None or vol_down is None:
            return None

        current_up = vol_up.latest
        current_down = vol_down.latest

        if current_up is None or current_down is None:
            return None

        total = current_up + current_down
        if total == 0:
            return None

        aggressor_ratio = current_up / total

        # Hard gate: LONG needs > 0.60, SHORT needs < 0.40
        if direction == "LONG" and aggressor_ratio <= 0.60:
            return None
        if direction == "SHORT" and aggressor_ratio >= 0.40:
            return None

        # Volume spike check: VolumeUp (LONG) or VolumeDown (SHORT) > 1.20× rolling avg
        if direction == "LONG":
            spike_window = vol_up
            spike_threshold = 1.20
        else:
            spike_window = vol_down
            spike_threshold = 1.20

        # Volume spike check: use per-direction rolling mean to avoid cross-contamination.
        # LONG: VolumeUp must exceed its own rolling mean * threshold.
        # SHORT: VolumeDown must exceed its own rolling mean * threshold.
        if direction == "LONG":
            if vol_up.mean is not None and vol_up.mean > 0:
                if current_up < vol_up.mean * spike_threshold:
                    return None
        else:
            if vol_down.mean is not None and vol_down.mean > 0:
                if current_down < vol_down.mean * spike_threshold:
                    return None

        return aggressor_ratio

    @staticmethod
    def _check_gamma_acceleration(
        rolling_data: Dict[str, Any],
    ) -> Optional[float]:
        """
        Check gamma acceleration (2nd derivative).

        Computes:
            1st derivative (ROC): (gamma_current - gamma_5_ago) / gamma_5_ago
            2nd derivative (acceleration): ROC_current - ROC_prev

        Hard gate: acceleration > 0.10

        Returns:
            gamma_acceleration float if gate passes, None otherwise.
        """
        window = rolling_data.get(KEY_TOTAL_GAMMA_5M)
        if window is None or window.count < 10:
            return None

        vals = list(window.values)
        if len(vals) < 10:
            return None

        # 1st derivative: ROC over last 5 points
        gamma_current = vals[-1]
        gamma_5_ago = vals[-5]
        gamma_10_ago = vals[-10]

        # Division-by-zero protection: guard against near-zero gamma values
        if abs(gamma_5_ago) < 1e-12 or abs(gamma_10_ago) < 1e-12:
            return None
        roc_current = (gamma_current - gamma_5_ago) / abs(gamma_5_ago)
        roc_prev = (gamma_5_ago - gamma_10_ago) / abs(gamma_10_ago)

        # 2nd derivative (acceleration)
        gamma_accel = roc_current - roc_prev

        # Hard gate: acceleration > 0.10
        if gamma_accel < 0.10:
            return None

        return gamma_accel

    @staticmethod
    def _check_delta_gamma_coupling(
        delta_accel: float,
        gamma_accel: float,
        direction: str = "LONG",
    ) -> bool:
        """
        Check delta-gamma coupling to filter phantom spikes.

        coupling = abs(delta_accel - 1.0) / gamma_accel

        Hard gate: direction-aware threshold
            - LONG: coupling >= 0.5 (strong delta movement relative to gamma)
            - SHORT: coupling >= 0.3 (lower threshold — delta movement is smaller)
            - If delta barely moves while gamma spikes → phantom spike

        Returns:
            True if coupling passes, False otherwise.
        """
        if gamma_accel <= 0:
            return False

        coupling = abs(delta_accel - 1.0) / gamma_accel

        if direction == "SHORT":
            return coupling >= 0.3
        return coupling >= 0.5

    @staticmethod
    def _compute_atr_target(
        entry: float,
        rolling_data: Dict[str, Any],
        direction: str,
    ) -> tuple:
        """
        Compute ATR-normalized target.

        atr_5m = standard deviation of price window (5-minute volatility)
        target = entry ± atr_5m * ATR_MULT
        Clamped to [0.3%, 2.0%] of entry.

        Returns:
            (target_price, atr_5m, target_mult)
        """
        price_window = rolling_data.get(KEY_PRICE_5M)
        if price_window is None:
            # Fallback: fixed 1.0% target
            if direction == "LONG":
                target = entry * 1.010
            else:
                target = entry * 0.990
            return (target, 0.0, 1.0)

        # Use std of price window as ATR proxy
        atr_5m = price_window.std or 0.0

        if atr_5m <= 0:
            # Fallback: fixed 1.0% target
            if direction == "LONG":
                target = entry * 1.010
            else:
                target = entry * 0.990
            return (target, 0.0, 1.0)

        target_mult = 1.5
        if direction == "LONG":
            target = entry + atr_5m * target_mult
        else:
            target = entry - atr_5m * target_mult

        # Clamp target percentage to [0.3%, 2.0%]
        target_pct = abs(target - entry) / entry if entry > 0 else 0.0
        if target_pct < 0.003:
            # Too tight — widen to minimum 0.3%
            if direction == "LONG":
                target = entry * 1.003
            else:
                target = entry * 0.997
            target_mult = 0.003 * entry / atr_5m if atr_5m > 0 else 1.5
        elif target_pct > 0.020:
            # Too loose — cap at 2.0%
            if direction == "LONG":
                target = entry * 1.020
            else:
                target = entry * 0.980
            target_mult = 0.020 * entry / atr_5m if atr_5m > 0 else 1.5

        return (target, atr_5m, target_mult)

    # ------------------------------------------------------------------
    # v1 Helpers (kept for metadata and backward compat)
    # ------------------------------------------------------------------

    @staticmethod
    def _check_delta_acceleration(
        rolling_data: Dict[str, Any],
    ) -> Optional[float]:
        """
        Check delta acceleration by comparing current total_delta
        to its rolling average.

        Returns ratio of current to rolling avg.
            > 1.0 = accelerating upward
            < 1.0 = accelerating downward
            None  = insufficient data
        """
        window = rolling_data.get(KEY_TOTAL_DELTA_5M)
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        rolling_avg = window.mean
        if rolling_avg is None or abs(rolling_avg) < 1e-12:
            return None

        current = window.latest
        if current is None:
            return None

        return current / rolling_avg

    @staticmethod
    def _check_gamma_spike(rolling_data: Dict[str, Any]) -> Optional[float]:
        """
        Check gamma spike (1st derivative, for metadata).

        Returns ratio of current to rolling avg.
        """
        window = rolling_data.get(KEY_TOTAL_GAMMA_5M)
        if window is None or window.count < MIN_DATA_POINTS:
            return None

        rolling_avg = window.mean
        if rolling_avg is None or abs(rolling_avg) < 1e-12:
            return None

        current = window.latest
        if current is None:
            return None

        return current / rolling_avg

    @staticmethod
    def _check_price_trend(rolling_data: Dict[str, Any]) -> str:
        """
        Check price trend from the rolling window.

        Returns "UP", "DOWN", or "FLAT".
        """
        window = rolling_data.get(KEY_PRICE_5M)
        if window is None:
            return "FLAT"

        # Use the trend property from RollingWindow
        trend = window.trend
        if trend != "FLAT":
            return trend

        # Fallback: check change_pct directly
        if window.change_pct is not None:
            if window.change_pct > PRICE_UP_THRESHOLD:
                return "UP"
            elif window.change_pct < PRICE_DOWN_THRESHOLD:
                return "DOWN"

        return "FLAT"

    # ------------------------------------------------------------------
    # Confidence (v2 — 6 components)
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        price: float,
        delta_accel: float,
        gamma_accel: float,
        aggressor_ratio: float,
        rolling_data: Dict[str, Any],
        direction: str,
        net_gamma: float,
        gex_calc: Any,
    ) -> float:
        """
        Combine all factors into a single confidence score (v2).

        Components (all continuous, graded):
            1. Delta acceleration: 0.0–0.20 (soft, direction-aware)
            2. Gamma acceleration: 0.0–0.25 (continuous, graded)
            3. Aggressor volume: 0.0–0.20 (continuous, direction-aware)
            4. Delta-gamma coupling: 0.0–0.15 (continuous, graded)
            5. ATR target quality: 0.0–0.10 (soft)
            6. Wall proximity: 0.05–0.10 (soft)

        Returns 0.0–1.0.
        """
        # 1. Delta acceleration (0.0–0.20, soft) — direction-aware
        delta_conf = self._delta_accel_confidence(delta_accel, direction)

        # 2. Gamma acceleration (0.0–0.25, continuous)
        # gamma_accel 0→0.30 maps to 0→1.0
        gamma_conf = 0.25 * min(1.0, gamma_accel / 0.30)

        # 3. Aggressor ratio (0.0–0.20, continuous, direction-aware)
        # LONG: aggressor_ratio 0.60→1.0 maps to 0→1.0
        # SHORT: aggressor_ratio 0.0→0.40 maps to 1.0→0
        if direction == "LONG":
            vol_score = max(0.0, min(1.0, (aggressor_ratio - 0.60) / 0.40))
        else:
            vol_score = max(0.0, min(1.0, (0.40 - aggressor_ratio) / 0.40))
        vol_conf = 0.20 * vol_score

        # 4. Delta-gamma coupling (0.0–0.15, continuous)
        coupling_score = self._coupling_score(delta_accel, gamma_accel, direction)
        coupling_conf = 0.15 * coupling_score

        # 5. ATR target quality (0.0–0.10, soft)
        _, atr_5m, target_mult = self._compute_atr_target(price, rolling_data, direction)
        target_conf = self._atr_target_confidence(target_mult)

        # 6. Wall proximity (0.05–0.10, soft)
        wall_conf = self._wall_proximity_confidence(price, direction, gex_calc)

        confidence = delta_conf + gamma_conf + vol_conf + coupling_conf + target_conf + wall_conf
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def _delta_accel_confidence(delta_accel: float, direction: str) -> float:
        """
        Compute confidence from delta acceleration.

        LONG: deviation from 1.0, scaled 0→0.20 as delta_accel grows from 1.0→2.5
        SHORT: deviation from 1.0 (delta is declining), scaled 0→0.20 as
               delta_accel drops from 0.85→0.30
        """
        if direction == "LONG":
            deviation = abs(delta_accel - 1.0)
            # delta_accel=1.0 → 0.0, delta_accel=2.5 → 0.20
            return min(0.20, 0.20 * deviation / 1.5)
        else:  # SHORT
            # delta_accel=0.85 → low conf, delta_accel=0.30 → high conf
            # Map 0.30→0.85 to 1.0→0.0
            deviation = abs(delta_accel - 1.0)
            # delta_accel=0.30 → deviation=0.70 → conf=0.20
            # delta_accel=0.85 → deviation=0.15 → conf=0.04
            return min(0.20, 0.20 * deviation / 0.70)

    @staticmethod
    def _coupling_score(delta_accel: float, gamma_accel: float, direction: str) -> float:
        """
        Compute continuous coupling score (0.0–1.0).

        coupling = abs(delta_accel - 1.0) / gamma_accel

        For LONG (delta_accel > 1.0): coupling measures how much delta moved
            relative to gamma spike
        For SHORT (delta_accel < 1.0): coupling measures how much delta declined
            relative to gamma spike

        The key fix: for SHORT, delta_accel is 0.30-0.85, so coupling = 0.15-0.70 /
            gamma_accel. If gamma_accel = 0.10 (barely passing), coupling = 1.5-7.0
            (always passes easily). We normalize: score = min(1.0, coupling / 3.0)
            so it's graded.

        Returns:
            Continuous coupling score 0.0–1.0.
        """
        if gamma_accel <= 0:
            return 0.0

        coupling = abs(delta_accel - 1.0) / gamma_accel

        # Normalize: coupling 0→3.0 maps to 0→1.0
        # coupling >= 3.0 = very strong coupling (delta moved a lot relative to gamma)
        return min(1.0, coupling / 3.0)

    @staticmethod
    def _atr_target_confidence(atr_mult: float) -> float:
        """
        Compute confidence from ATR target quality.

        Ideal multiplier is 1.5. Closer to 1.5 = higher confidence.
        Scale: 0.0 (mult=0 or mult>3) to 0.10 (mult=1.5).
        """
        if atr_mult <= 0 or atr_mult > 3.0:
            return 0.0
        # Ideal is 1.5, scale down as we move away
        deviation = abs(atr_mult - 1.5)
        conf = max(0.0, 0.10 * (1.0 - deviation / 1.5))
        return conf

    def _wall_proximity_confidence(
        self,
        price: float,
        direction: str,
        gex_calc: Any,
    ) -> float:
        """
        Compute confidence bonus from proximity to relevant gamma wall.

        For LONG:  closer to call wall above = higher confidence.
        For SHORT: closer to put wall below = higher confidence.
        """
        walls = self._safe_get_walls(gex_calc)
        if not walls:
            return 0.05  # baseline when no walls

        if direction == "LONG":
            wall = self._nearest_wall_above(walls, price)
        else:
            wall = self._nearest_wall_below(walls, price)

        if wall is None:
            return 0.05  # baseline when no relevant wall

        wall_strike = wall["strike"]
        distance_pct = abs(wall_strike - price) / price

        # Closer = higher confidence (0.05–0.10)
        # At 0% distance = 0.10, at 2% distance = 0.05
        if distance_pct <= 0:
            return 0.10
        elif distance_pct >= 0.02:
            return 0.05
        else:
            return 0.10 - 0.05 * (distance_pct / 0.02)

    # ------------------------------------------------------------------
    # Price trend scoring
    # ------------------------------------------------------------------

    @staticmethod
    def _price_trend_score(rolling_data, direction):
        """
        Price trend score: 0.0–1.0 based on how strongly price is trending
        in the signal direction.
        """
        price_window = rolling_data.get(KEY_PRICE_5M)
        if not price_window or price_window.count < 5:
            return 0.5  # neutral

        trend = price_window.trend if hasattr(price_window, 'trend') else "UNKNOWN"

        if direction == "LONG":
            if trend == "UP":
                return 1.0
            elif trend == "FLAT":
                return 0.3
            else:  # DOWN
                return 0.0
        else:  # SHORT
            if trend == "DOWN":
                return 1.0
            elif trend == "FLAT":
                return 0.3
            else:  # UP
                return 0.0

    # ------------------------------------------------------------------
    # Wall helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_atm_strike(gex_calc: Any, price: float) -> Optional[float]:
        """Get the nearest ATM strike from the GEX calculator."""
        try:
            return gex_calc.get_atm_strike(price)
        except Exception as exc:
            logger.debug("GVC: failed to get ATM strike: %s", exc)
            return None

    @staticmethod
    def _safe_get_walls(gex_calc: Any) -> List[Dict[str, Any]]:
        """Safely retrieve gamma walls, returning empty list on error."""
        try:
            return gex_calc.get_gamma_walls(threshold=500_000)
        except Exception as exc:
            logger.debug("GVC: failed to get gamma walls: %s", exc)
            return []

    @staticmethod
    def _nearest_wall_above(
        walls: List[Dict[str, Any]], price: float,
    ) -> Optional[Dict[str, Any]]:
        """Find the nearest gamma wall above the current price."""
        above = [w for w in walls if w["strike"] > price]
        if not above:
            return None
        return min(above, key=lambda w: w["strike"])

    @staticmethod
    def _nearest_wall_below(
        walls: List[Dict[str, Any]], price: float,
    ) -> Optional[Dict[str, Any]]:
        """Find the nearest gamma wall below the current price."""
        below = [w for w in walls if w["strike"] < price]
        if not below:
            return None
        return max(below, key=lambda w: w["strike"])
