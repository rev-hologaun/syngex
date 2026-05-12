"""
strategies/layer2/delta_iv_divergence.py — Delta-IV Divergence v2
"Tail-Risk Divergence" Upgrade

Detects sentiment shifts where delta and IV diverge, enhanced with:
- OTM-vs-ATM skew gradient (edge detection)
- Delta-IV decoupling coefficient (conviction filter)
- Gamma-regime filtering (stability check)
- Volatility-scaled targets (dynamic exit)
- Wall proximity bonus (confidence boost)

LONG: delta rising + IV falling → bullish accumulation
SHORT: delta falling + IV rising → bearish positioning

The divergence between conviction (delta) and fear (IV) signals
smart money positioning before the crowd catches on.

v2 adds:
- Skew gradient: OTM vs ATM Delta-IV divergence (hard gate)
- Decoupling coefficient: Delta-IV correlation collapse (hard gate)
- Gamma regime filter: declining gamma density = unstable zone (hard gate)
- Vol-scaled targets: target distance scales with IV expansion
- Wall proximity: +0.10 bonus near gamma walls
"""

from __future__ import annotations

import logging
import statistics
from typing import Any, Dict, List, Optional

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal
from strategies.rolling_keys import (
    KEY_ATM_DELTA_5M,
    KEY_ATM_IV_5M,
    KEY_DELTA_IV_CORR_5M,
    KEY_OTM_DELTA_5M,
    KEY_OTM_IV_5M,
)

logger = logging.getLogger("Syngex.Strategies.DeltaIVDivergence")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Min data points for both delta and IV windows
MIN_DATA_POINTS = 5

# Minimum divergence strength (combined z-score magnitude)
MIN_DIVERSION_STRENGTH = 0.3

# Stop distance
STOP_PCT = 0.008  # 0.8%

# Confidence threshold
MIN_CONFIDENCE = 0.40

# Skew divergence threshold
SK_DIV_THRESHOLD = 0.10

# Decoupling history window (data points)
DECOUPLE_HISTORY_WINDOW = 30

# Decoupling correlation threshold
DECOUPLE_THRESHOLD = 0.50

# Gamma density decline threshold
GAMMA_DECLINE_THRESHOLD = 0.70

# IV expansion multiplier
TARGET_IV_MULT = 2.0

# IV expansion cap
TARGET_IV_CAP = 4.0

# Wall proximity percentage
WALL_PROX_PCT = 0.01

# Wall proximity confidence bonus
WALL_PROX_BONUS = 0.10

# ---------------------------------------------------------------------------
# Strategy class
# ---------------------------------------------------------------------------


class DeltaIVDivergence(BaseStrategy):
    """
    Detects delta-IV divergence for sentiment shift signals.

    LONG: delta rising + IV falling → bullish accumulation
    SHORT: delta falling + IV rising → bearish positioning

    v2: Tail-Risk Divergence with skew gradient, decoupling, gamma filter,
        vol-scaled targets, and wall proximity bonus.
    """

    strategy_id = "delta_iv_divergence"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """Evaluate current state for delta-IV divergence."""
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")
        greeks_summary = data.get("greeks_summary", {})
        gex_calc = data.get("gex_calculator")

        signals: List[Signal] = []

        # Check LONG setup: delta UP + IV DOWN
        long_sig = self._check_divergence(
            rolling_data, underlying_price, net_gamma, regime, "LONG",
            greeks_summary=greeks_summary, gex_calc=gex_calc,
        )
        if long_sig:
            signals.append(long_sig)

        # Check SHORT setup: delta DOWN + IV UP
        short_sig = self._check_divergence(
            rolling_data, underlying_price, net_gamma, regime, "SHORT",
            greeks_summary=greeks_summary, gex_calc=gex_calc,
        )
        if short_sig:
            signals.append(short_sig)

        return signals

    def _check_divergence(
        self,
        rolling_data: Dict[str, Any],
        price: float,
        net_gamma: float,
        regime: str,
        direction: str,  # "LONG" or "SHORT"
        greeks_summary: Dict,
        gex_calc: Any,
    ) -> Optional[Signal]:
        """Check for delta-IV divergence and return signal or None."""
        delta_window = rolling_data.get(KEY_ATM_DELTA_5M)
        iv_window = rolling_data.get(KEY_ATM_IV_5M)

        # Both windows need sufficient data
        if delta_window is None or iv_window is None:
            return None
        if delta_window.count < MIN_DATA_POINTS or iv_window.count < MIN_DATA_POINTS:
            return None

        # Check trend alignment
        delta_trend = delta_window.trend  # "UP", "DOWN", or "FLAT"
        iv_trend = iv_window.trend

        if direction == "LONG":
            # LONG: delta UP + IV DOWN
            if delta_trend != "UP" or iv_trend != "DOWN":
                return None
        else:
            # SHORT: delta DOWN + IV UP
            if delta_trend != "DOWN" or iv_trend != "UP":
                return None

        # Compute divergence strength from z-scores
        delta_z = delta_window.z_score or 0.0
        iv_z = iv_window.z_score or 0.0

        if direction == "LONG":
            # LONG: delta z should be positive, iv z should be negative
            divergence_strength = min(delta_z, abs(iv_z)) / 2.0
        else:
            # SHORT: delta z should be negative, iv z should be positive
            divergence_strength = min(abs(delta_z), iv_z) / 2.0

        divergence_strength = max(0.0, divergence_strength)
        if divergence_strength < MIN_DIVERSION_STRENGTH:
            return None

        # ── v2 hard gates ──

        # 1. Skew divergence (edge signal confirmed)
        skew_divergence = self._check_skew_divergence(
            rolling_data, direction,
        )
        if not skew_divergence:
            return None

        # 2. Decoupling coefficient (correlation collapsed)
        decoupling = self._check_decoupling(
            rolling_data, DECOUPLE_HISTORY_WINDOW, DECOUPLE_THRESHOLD,
        )
        if not decoupling:
            return None

        # 3. Gamma regime filter (moving into unstable zone)
        gamma_decline = self._check_gamma_regime(
            gex_calc, rolling_data, price,
        )
        if not gamma_decline:
            return None

        # ── v2 soft factors ──

        # Wall proximity bonus
        wall_bonus, wall_dist_pct, wall_type = self._check_wall_proximity(
            gex_calc, price, direction, WALL_PROX_PCT,
        )

        # IV expansion factor (for vol-scaled targets)
        iv_window_for_target = rolling_data.get(KEY_ATM_IV_5M)
        iv_expansion = self._compute_iv_expansion(iv_window_for_target)

        # Compute confidence
        confidence = self._compute_confidence(
            skew_divergence=True,  # already passed hard gate
            decoupling=True,       # already passed hard gate
            gamma_decline=True,    # already passed hard gate
            divergence_strength=divergence_strength,
            iv_expansion=iv_expansion,
            net_gamma=net_gamma,
            regime=regime,
            wall_bonus=wall_bonus,
            direction=direction,
            greeks_summary=greeks_summary,
        )
        if confidence < MIN_CONFIDENCE:
            return None

        # Compute vol-scaled target
        entry = price
        reverse = 1 if direction == "LONG" else -1
        stop = entry * (1 - STOP_PCT * reverse)
        risk = abs(entry - stop)

        target_price, target_mult, iv_expansion_factor = self._compute_vol_scaled_target(
            entry, risk, iv_window_for_target, direction,
            iv_expansion, TARGET_IV_MULT, TARGET_IV_CAP,
        )

        # Gamma density stats for metadata
        gamma_density_current, gamma_density_mean, gamma_density_decline_pct = (
            self._get_gamma_density_stats(gex_calc, rolling_data, price)
        )

        # Decoupling coefficient value
        decouple_coeff = self._get_decoupling_coefficient(rolling_data)

        # Skew divergence value
        skew_div_val = self._get_skew_divergence_value(rolling_data, direction)

        return Signal(
            direction=Direction.LONG if direction == "LONG" else Direction.SHORT,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target_price, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Delta-IV divergence: delta {delta_trend} + IV {iv_trend} "
                f"({divergence_strength:.2f} strength) — {direction} signal "
                f"(skew={skew_div_val:.3f}, decouple={decouple_coeff:.3f}, "
                f"gamma_decline={gamma_density_decline_pct:.0f}%)"
            ),
            metadata={
                # === v1 fields (kept) ===
                "direction": direction,
                "delta_trend": delta_trend,
                "iv_trend": iv_trend,
                "divergence_strength": round(divergence_strength, 3),
                "delta_z": round(delta_z, 3),
                "iv_z": round(iv_z, 3),
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target_price - entry) / risk, 2) if risk > 0 else 0,

                # === v2 new fields ===
                "skew_divergence": round(skew_div_val, 4),
                "decoupling_coefficient": round(decouple_coeff, 4),
                "gamma_density_current": round(gamma_density_current, 6),
                "gamma_density_mean": round(gamma_density_mean, 6),
                "gamma_density_decline_pct": round(gamma_density_decline_pct, 1),
                "iv_expansion_factor": round(iv_expansion_factor, 3),
                "target_mult": round(target_mult, 2),
                "wall_proximity_pct": round(wall_dist_pct, 4),
                "nearest_wall_type": wall_type,
                "wall_proximity_bonus": wall_bonus,
            },
        )

    # ------------------------------------------------------------------
    # v2 Hard Gate: Skew Divergence
    # ------------------------------------------------------------------

    def _check_skew_divergence(
        self, rolling_data: Dict[str, Any], direction: str,
    ) -> bool:
        """
        Check if OTM Delta diverges from ATM Delta.

        Logic:
        - Compute Delta ROC for both OTM and ATM over last 5 data points
        - skew_divergence = |d(OTM_Delta)/dt - d(ATM_Delta)/dt| / max(|d(ATM_Delta)/dt|, 0.001)
        - Hard gate: skew_divergence > 0.10

        Returns True if skew divergence passes the threshold.
        """
        otm_delta_window = rolling_data.get(KEY_OTM_DELTA_5M)
        atm_delta_window = rolling_data.get(KEY_ATM_DELTA_5M)

        if otm_delta_window is None or atm_delta_window is None:
            return False
        if otm_delta_window.count < 6 or atm_delta_window.count < 6:
            return False

        otm_vals = otm_delta_window.values
        atm_vals = atm_delta_window.values

        # Get values 5 points ago
        otm_current = otm_vals[-1]
        otm_5_ago = otm_vals[-6] if len(otm_vals) >= 6 else otm_vals[0]
        atm_current = atm_vals[-1]
        atm_5_ago = atm_vals[-6] if len(atm_vals) >= 6 else atm_vals[0]

        # Compute Delta ROC (rate of change)
        otm_roc = (otm_current - otm_5_ago) / max(abs(otm_5_ago), 0.001)
        atm_roc = (atm_current - atm_5_ago) / max(abs(atm_5_ago), 0.001)

        # Skew divergence: absolute difference in ROCs
        skew_div = abs(otm_roc - atm_roc) / max(abs(atm_roc), 0.001)

        # Hard gate
        return skew_div > 0.10

    def _get_skew_divergence_value(
        self, rolling_data: Dict[str, Any], direction: str,
    ) -> float:
        """Get the raw skew divergence value for metadata."""
        otm_delta_window = rolling_data.get(KEY_OTM_DELTA_5M)
        atm_delta_window = rolling_data.get(KEY_ATM_DELTA_5M)

        if otm_delta_window is None or atm_delta_window is None:
            return 0.0
        if otm_delta_window.count < 6 or atm_delta_window.count < 6:
            return 0.0

        otm_vals = otm_delta_window.values
        atm_vals = atm_delta_window.values

        otm_current = otm_vals[-1]
        otm_5_ago = otm_vals[-6] if len(otm_vals) >= 6 else otm_vals[0]
        atm_current = atm_vals[-1]
        atm_5_ago = atm_vals[-6] if len(atm_vals) >= 6 else atm_vals[0]

        otm_roc = (otm_current - otm_5_ago) / max(abs(otm_5_ago), 0.001)
        atm_roc = (atm_current - atm_5_ago) / max(abs(atm_5_ago), 0.001)

        return abs(otm_roc - atm_roc) / max(abs(atm_roc), 0.001)

    # ------------------------------------------------------------------
    # v2 Hard Gate: Decoupling Coefficient
    # ------------------------------------------------------------------

    def _check_decoupling(
        self, rolling_data: Dict[str, Any],
        history_window: int, threshold: float,
    ) -> bool:
        """
        Check if Delta-IV correlation has collapsed.

        Logic:
        - Read KEY_DELTA_IV_CORR_5M rolling window
        - Compute rolling mean correlation over last `history_window` points
        - Hard gate: current correlation < rolling mean × threshold
          (correlation collapsed by ≥50% when threshold=0.50)

        Returns True if decoupling passes the threshold.
        """
        corr_window = rolling_data.get(KEY_DELTA_IV_CORR_5M)
        if corr_window is None or corr_window.count < 2:
            return False

        corr_vals = corr_window.values
        current_corr = corr_vals[-1]

        if corr_window.count < 2:
            return False

        # Rolling mean over last min(history_window, count) points
        history = min(history_window, len(corr_vals) - 1)
        if history < 1:
            return False
        mean_corr = statistics.mean(corr_vals[-(history + 1):-1]) if history > 0 else current_corr

        # Hard gate: current correlation < rolling mean × threshold
        return current_corr < mean_corr * threshold

    def _get_decoupling_coefficient(self, rolling_data: Dict[str, Any]) -> float:
        """Get the raw decoupling coefficient for metadata."""
        corr_window = rolling_data.get(KEY_DELTA_IV_CORR_5M)
        if corr_window is None or corr_window.count < 2:
            return 0.0

        corr_vals = corr_window.values
        current_corr = corr_vals[-1]
        history = min(30, len(corr_vals) - 1)
        if history < 1:
            return 0.0
        mean_corr = statistics.mean(corr_vals[-(history + 1):-1]) if history > 0 else current_corr

        if mean_corr == 0:
            return 0.0
        return current_corr / mean_corr

    # ------------------------------------------------------------------
    # v2 Hard Gate: Gamma Regime Filter
    # ------------------------------------------------------------------

    def _check_gamma_regime(
        self, gex_calc: Any, rolling_data: Dict[str, Any], price: float,
    ) -> bool:
        """
        Check if gamma density is declining (moving into unstable zone).

        Logic:
        - Compute gamma density: sum of (call_gamma + put_gamma) for strikes
          within ±1% of price
        - Store in rolling window (KEY_GAMMA_DENSITY_5M)
        - Hard gate: current density < rolling mean × 0.70
          (density declined by ≥30%)

        Returns True if gamma density is declining.
        """
        if gex_calc is None:
            return False

        gamma_density = self._compute_gamma_density(gex_calc, price)
        if gamma_density is None:
            return False

        gamma_window = rolling_data.get(KEY_GAMMA_DENSITY_5M)
        if gamma_window is None:
            return False

        gamma_window.push(gamma_density)

        if gamma_window.count < 3:
            return False

        # Current density vs rolling mean
        current = gamma_density
        mean_density = gamma_window.mean or 0.0

        if mean_density <= 0:
            return False

        # Hard gate: current < mean × 0.70
        return current < mean_density * 0.70

    def _compute_gamma_density(self, gex_calc: Any, price: float) -> Optional[float]:
        """Compute gamma density: sum of gamma for strikes within ±1% of price."""
        try:
            greeks_summary = gex_calc.get_greeks_summary()
            if not greeks_summary:
                return None

            gamma_density = 0.0
            for strike_str, strike_data in greeks_summary.items():
                try:
                    strike = float(strike_str)
                except (ValueError, TypeError):
                    continue
                distance = abs(strike - price) / price
                if distance <= 0.01:  # ±1% window
                    call_gamma = strike_data.get("call_gamma", 0.0)
                    put_gamma = strike_data.get("put_gamma", 0.0)
                    gamma_density += abs(call_gamma) + abs(put_gamma)

            return gamma_density
        except Exception:
            return None

    def _get_gamma_density_stats(
        self, gex_calc: Any, rolling_data: Dict[str, Any], price: float,
    ) -> tuple:
        """Get gamma density current, mean, and decline percentage for metadata."""
        if gex_calc is None:
            return (0.0, 0.0, 0.0)

        gamma_density = self._compute_gamma_density(gex_calc, price)
        if gamma_density is None:
            return (0.0, 0.0, 0.0)

        gamma_window = rolling_data.get(KEY_GAMMA_DENSITY_5M)
        if gamma_window is None:
            return (gamma_density, 0.0, 0.0)

        current = gamma_density
        mean_density = gamma_window.mean or 0.0

        decline_pct = 0.0
        if mean_density > 0:
            decline_pct = (1.0 - current / mean_density) * 100.0

        return (current, mean_density, decline_pct)

    # ------------------------------------------------------------------
    # v2 Soft: Volatility-Scaled Target
    # ------------------------------------------------------------------

    def _compute_vol_scaled_target(
        self, entry: float, risk: float, iv_window: Any,
        direction: str, iv_expansion: float,
        target_iv_mult: float, target_iv_cap: float,
    ) -> tuple:
        """
        Compute volatility-scaled target price.

        iv_expansion_factor = current_iv / mean_iv
        target_mult = target_iv_mult × iv_expansion_factor, capped at target_iv_cap
        For LONG: target = entry + risk × target_mult
        For SHORT: target = entry - risk × target_mult

        Returns (target_price, target_mult, iv_expansion_factor).
        """
        if iv_window is None or iv_window.count < 2:
            return (entry + risk * target_iv_mult, target_iv_mult, 1.0)

        current_iv = iv_window.latest or 0.0
        mean_iv = iv_window.mean or 0.0

        if mean_iv <= 0:
            return (entry + risk * target_iv_mult, target_iv_mult, 1.0)

        iv_expansion_factor = current_iv / mean_iv
        target_mult = target_iv_mult * iv_expansion_factor
        target_mult = min(target_mult, target_iv_cap)

        reverse = 1 if direction == "LONG" else -1
        target_price = entry + (risk * target_mult * reverse)

        return (target_price, target_mult, iv_expansion_factor)

    def _compute_iv_expansion(self, iv_window: Any) -> float:
        """Compute IV expansion factor from rolling window."""
        if iv_window is None or iv_window.count < 2:
            return 1.0
        current_iv = iv_window.latest or 0.0
        mean_iv = iv_window.mean or 0.0
        if mean_iv <= 0:
            return 1.0
        return current_iv / mean_iv

    # ------------------------------------------------------------------
    # v2 Soft: Wall Proximity Bonus
    # ------------------------------------------------------------------

    def _check_wall_proximity(
        self, gex_calc: Any, price: float, direction: str,
        wall_prox_pct: float,
    ) -> tuple:
        """
        Check proximity to gamma wall for confidence bonus.

        For LONG: bonus if nearest put wall is within wall_prox_pct below price
        For SHORT: bonus if nearest call wall is within wall_prox_pct above price

        Returns (bonus, wall_dist_pct, wall_type).
        """
        if gex_calc is None:
            return (0.0, 0.0, None)

        try:
            walls = gex_calc.get_gamma_walls(threshold=500_000)
        except Exception:
            return (0.0, 0.0, None)

        if not walls:
            return (0.0, 0.0, None)

        if direction == "LONG":
            # Check nearest put wall below price
            best_wall = None
            best_dist = float("inf")
            for wall in walls:
                if wall.get("side") == "put" and wall["strike"] < price:
                    dist = (price - wall["strike"]) / price
                    if dist < best_dist:
                        best_dist = dist
                        best_wall = wall
            if best_wall and best_dist <= wall_prox_pct:
                return (0.10, best_dist * 100, "put")
        else:
            # SHORT: check nearest call wall above price
            best_wall = None
            best_dist = float("inf")
            for wall in walls:
                if wall.get("side") == "call" and wall["strike"] > price:
                    dist = (wall["strike"] - price) / price
                    if dist < best_dist:
                        best_dist = dist
                        best_wall = wall
            if best_wall and best_dist <= wall_prox_pct:
                return (0.10, best_dist * 100, "call")

        return (0.0, 0.0, None)

    # ------------------------------------------------------------------
    # v2 Confidence Computation
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        skew_divergence: bool,
        decoupling: bool,
        gamma_decline: bool,
        divergence_strength: float,
        iv_expansion: float,
        net_gamma: float,
        regime: str,
        wall_bonus: float,
        direction: str,
        greeks_summary: Dict,
    ) -> float:
        """
        Combine v2 confidence factors into a score 0.0–1.0.

        Hard gates (all must pass for signal):
        1. Skew divergence: 0.0 or 0.20
        2. Decoupling: 0.0 or 0.15
        3. Gamma regime: 0.0 or 0.15

        Soft factors (boost confidence):
        4. Divergence strength: 0.0–0.10
        5. Volume conviction: 0.0–0.10
        6. Wall proximity: +0.0 to +0.10
        7. Regime intensity: 0.05–0.10
        """
        # 1. Skew gradient (hard gate — 0.0 or 0.20)
        skew_conf = 0.20 if skew_divergence else 0.0

        # 2. Decoupling coefficient (hard gate — 0.0 or 0.15)
        decouple_conf = 0.15 if decoupling else 0.0

        # 3. Gamma regime filter (hard gate — 0.0 or 0.15)
        gamma_conf = 0.15 if gamma_decline else 0.0

        # 4. Divergence strength (soft — 0.0–0.10)
        div_conf = self._divergence_confidence(divergence_strength)

        # 5. Volume-weighted conviction (soft — 0.0–0.10)
        vol_conf = self._volume_conviction_confidence(iv_expansion, greeks_summary)

        # 6. Wall proximity (soft — 0.0–0.10)
        wall_conf = wall_bonus

        # 7. Regime intensity (soft — 0.05–0.10)
        regime_conf = self._regime_confidence(net_gamma, direction)

        confidence = skew_conf + decouple_conf + gamma_conf + div_conf + vol_conf + wall_conf + regime_conf
        return min(1.0, max(0.0, confidence))

    def _divergence_confidence(self, divergence_strength: float) -> float:
        """Convert divergence strength to confidence contribution (0.0–0.10)."""
        return min(0.10, 0.10 * min(1.0, divergence_strength / 2.0))

    def _volume_conviction_confidence(
        self, iv_expansion: float, greeks_summary: Dict,
    ) -> float:
        """
        Volume-weighted conviction (0.0–0.10).

        Uses option volume from greeks_summary to weight conviction.
        Higher IV expansion + higher volume = stronger conviction.
        """
        if not greeks_summary:
            return 0.0

        # Sum total volume across all strikes
        total_volume = 0.0
        for strike_data in greeks_summary.values():
            call_vol = strike_data.get("call_volume", 0)
            put_vol = strike_data.get("put_volume", 0)
            total_volume += call_vol + put_vol

        # Normalize: 100k+ volume = full conviction
        vol_factor = min(1.0, total_volume / 100_000.0)

        # IV expansion boosts conviction (more volume in expanding IV = real move)
        iv_factor = min(1.0, iv_expansion) if iv_expansion > 0 else 0.5

        return min(0.10, 0.10 * vol_factor * iv_factor)

    def _regime_confidence(self, net_gamma: float, direction: str) -> float:
        """
        Regime intensity (0.05–0.10).

        Gamma magnitude scaling: stronger gamma = more conviction.
        """
        gamma_abs = abs(net_gamma)
        if gamma_abs > 500_000:
            return 0.10
        elif gamma_abs > 100_000:
            return 0.08
        else:
            return 0.05
