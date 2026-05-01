"""
strategies/layer2/delta_iv_divergence.py — Delta-IV Divergence

Detects shifts in market "fear" vs "intent" by scanning all strikes
for the pattern: delta increasing while IV is dropping.

This is a classic smart money signal: when options are being accumulated
(delta rises) but implied volatility is falling, it means informed
participants are buying before the crowd catches on. The crowd hasn't
driven IV up yet, but delta is already moving.

Logic:
    - Scan all strikes for Δ(delta) > 0 AND Δ(IV) < 0
    - Multiple strikes showing this = strong conviction
    - Call-side divergence → LONG
    - Put-side divergence → SHORT

Exit: When IV catches up to delta (divergence closes)

Confidence factors:
    - Number of strikes showing divergence
    - Magnitude of delta increase
    - Magnitude of IV decrease
    - Regime alignment
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from strategies.engine import BaseStrategy
from strategies.signal import Direction, Signal

logger = logging.getLogger("Syngex.Strategies.DeltaIVDivergence")


# Internal state keys used to store previous averages between calls
_PREV_AVG_DELTA = "_prev_avg_delta"
_PREV_AVG_IV = "_prev_avg_iv"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Min strikes showing divergence for signal
MIN_DIVERGENT_STRIKES = 2

# Min delta increase threshold (as fraction of current delta)
MIN_DELTA_INCREASE = 0.05           # 5% delta increase

# Min IV decrease threshold (as fraction of current IV)
MIN_IV_DECREASE = 0.03              # 3% IV decrease

# Min greeks data points per strike
MIN_STRIKE_POINTS = 3

# Stop and target
STOP_PCT = 0.006                    # 0.6% stop
TARGET_RISK_MULT = 2.0              # 2× risk target


class DeltaIVDivergence(BaseStrategy):
    """
    Detects smart money accumulation via delta-IV divergence.

    When delta rises on a strike but IV drops, it signals that
    informed participants are accumulating positions before the
    broader market adjusts. Multiple strikes showing this pattern
    confirms the signal.
    """

    strategy_id = "delta_iv_divergence"
    layer = "layer2"

    def evaluate(self, data: Dict[str, Any]) -> List[Signal]:
        """
        Evaluate current state for delta-IV divergence.

        Returns empty list when no divergence detected.
        """
        underlying_price = data.get("underlying_price", 0)
        if underlying_price <= 0:
            return []

        gex_calc = data.get("gex_calculator")
        if gex_calc is None:
            return []

        rolling_data = data.get("rolling_data", {})
        net_gamma = data.get("net_gamma", 0)
        regime = data.get("regime", "")

        # Scan all strikes for divergence
        call_divergences, put_divergences = self._scan_divergence(gex_calc, rolling_data)

        if not call_divergences and not put_divergences:
            return []

        signals: List[Signal] = []

        # Evaluate call-side divergence → LONG
        if len(call_divergences) >= MIN_DIVERGENT_STRIKES:
            sig = self._evaluate_divergence(
                call_divergences, "call", underlying_price,
                gex_calc, rolling_data, net_gamma, regime,
            )
            if sig:
                signals.append(sig)

        # Evaluate put-side divergence → SHORT
        if len(put_divergences) >= MIN_DIVERGENT_STRIKES:
            sig = self._evaluate_divergence(
                put_divergences, "put", underlying_price,
                gex_calc, rolling_data, net_gamma, regime,
            )
            if sig:
                signals.append(sig)

        return signals

    def _scan_divergence(
        self,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Scan all strikes for delta-IV divergence pattern.

        Computes actual delta changes by comparing the current average delta
        per message (call_delta / call_count) against the rolling window mean.
        Compares current IV against rolling average IV to detect IV drops.

        A divergence requires:
          - Delta change >= MIN_DELTA_INCREASE (delta increasing)
          - IV change <= -MIN_IV_DECREASE (IV decreasing)

        Returns (call_divergences, put_divergences) — lists of strike
        dicts with delta_change, iv_change, and current values.
        """
        greeks_cache = gex_calc.get_greeks_cache()
        if not greeks_cache:
            return [], []

        iv_by_strike = gex_calc.get_iv_by_strike_avg()

        call_divergences: List[Dict[str, Any]] = []
        put_divergences: List[Dict[str, Any]] = []

        for strike, bucket in greeks_cache.items():
            call_delta = bucket.get("call_delta", 0.0)
            call_oi = bucket.get("call_oi", 0.0)
            call_count = bucket.get("call_count", 0)
            put_delta = bucket.get("put_delta", 0.0)
            put_oi = bucket.get("put_oi", 0.0)
            put_count = bucket.get("put_count", 0)

            # Get current IV for this strike
            current_iv = iv_by_strike.get(strike, 0.0) or 0.0
            iv_window = rolling_data.get(f"iv_{strike}_5m")
            rolling_avg_iv = iv_window.mean if iv_window is not None and iv_window.mean is not None else 0.0

            # ------------------------------------------------------------------
            # Call side: compute actual delta change
            # ------------------------------------------------------------------
            if call_count >= MIN_STRIKE_POINTS and call_oi > 0:
                # Average delta per message (normalizes the cumulative sum)
                avg_call_delta = call_delta / call_count if call_count != 0 else 0.0

                # Delta change: compare current avg delta per message against
                # the rolling window mean of those averages
                delta_window = rolling_data.get(f"delta_call_{strike}_5m")
                rolling_avg_delta = 0.0
                if delta_window is not None and delta_window.count >= MIN_STRIKE_POINTS:
                    rolling_avg_delta = delta_window.mean or 0.0
                    if rolling_avg_delta != 0:
                        delta_change_pct = (avg_call_delta - rolling_avg_delta) / abs(rolling_avg_delta)
                    else:
                        delta_change_pct = 0.0
                else:
                    delta_change_pct = 0.0

                # IV change: current vs rolling avg
                if rolling_avg_iv > 0 and current_iv > 0:
                    iv_change_pct = (current_iv - rolling_avg_iv) / rolling_avg_iv
                else:
                    iv_change_pct = 0.0

                call_div = {
                    "strike": strike,
                    "side": "call",
                    "delta_change": round(avg_call_delta, 6),
                    "delta_change_pct": round(delta_change_pct, 4),
                    "recent_delta": round(avg_call_delta, 6),
                    "recent_iv": round(current_iv, 4),
                    "rolling_avg_iv": round(rolling_avg_iv, 4),
                    "rolling_avg_delta": round(rolling_avg_delta, 6) if delta_window is not None else 0.0,
                    "iv_change_pct": round(iv_change_pct, 4),
                }
                call_divergences.append(call_div)

            # ------------------------------------------------------------------
            # Put side: compute actual delta change
            # ------------------------------------------------------------------
            if put_count >= MIN_STRIKE_POINTS and put_oi > 0:
                avg_put_delta = put_delta / put_count if put_count != 0 else 0.0

                put_delta_window = rolling_data.get(f"delta_put_{strike}_5m")
                put_rolling_avg_delta = 0.0
                if put_delta_window is not None and put_delta_window.count >= MIN_STRIKE_POINTS:
                    put_rolling_avg_delta = put_delta_window.mean or 0.0
                    if put_rolling_avg_delta != 0:
                        delta_change_pct = (avg_put_delta - put_rolling_avg_delta) / abs(put_rolling_avg_delta)
                    else:
                        delta_change_pct = 0.0
                else:
                    delta_change_pct = 0.0

                if rolling_avg_iv > 0 and current_iv > 0:
                    iv_change_pct = (current_iv - rolling_avg_iv) / rolling_avg_iv
                else:
                    iv_change_pct = 0.0

                put_div = {
                    "strike": strike,
                    "side": "put",
                    "delta_change": round(avg_put_delta, 6),
                    "delta_change_pct": round(delta_change_pct, 4),
                    "recent_delta": round(avg_put_delta, 6),
                    "recent_iv": round(current_iv, 4),
                    "rolling_avg_iv": round(rolling_avg_iv, 4),
                    "rolling_avg_delta": round(put_rolling_avg_delta, 6) if put_delta_window is not None else 0.0,
                    "iv_change_pct": round(iv_change_pct, 4),
                }
                put_divergences.append(put_div)

        # Sort by magnitude of divergence
        call_divergences.sort(
            key=lambda d: abs(d.get("delta_change_pct", 0)), reverse=True
        )
        put_divergences.sort(
            key=lambda d: abs(d.get("delta_change_pct", 0)), reverse=True
        )

        return call_divergences, put_divergences

    def _check_strike_divergence(
        self,
        strike: float,
        messages: List[Dict[str, Any]],
        side: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Check a single strike for delta-IV divergence.

        Returns dict with divergence details if pattern detected, else None.
        """
        if len(messages) < MIN_STRIKE_POINTS:
            return None

        # Need at least a few messages to compare
        n = len(messages)
        if n < 4:
            return None

        # Use recent half vs older half for comparison
        recent = messages[n // 2:]
        older = messages[:n // 2]

        # Calculate average delta and IV for each period
        recent_delta = sum(float(m.get("delta", 0)) for m in recent) / len(recent)
        older_delta = sum(float(m.get("delta", 0)) for m in older) / len(older)

        recent_iv = sum(float(m.get("implied_volatility", 0)) for m in recent) / len(recent)
        older_iv = sum(float(m.get("implied_volatility", 0)) for m in older) / len(older)

        # Delta should be increasing: recent > older
        # For calls: delta is positive and should increase
        # For puts: delta is negative and should become less negative (increase)
        delta_change = recent_delta - older_delta

        # IV should be decreasing: recent < older
        iv_change = recent_iv - older_iv

        # Check thresholds
        if older_delta == 0 or older_iv == 0:
            return None

        delta_change_pct = delta_change / abs(older_delta)
        iv_change_pct = iv_change / abs(older_iv)

        # Divergence: delta up AND iv down
        if delta_change_pct >= MIN_DELTA_INCREASE and iv_change_pct <= -MIN_IV_DECREASE:
            return {
                "strike": strike,
                "side": side,
                "delta_change": round(delta_change, 4),
                "delta_change_pct": round(delta_change_pct, 4),
                "iv_change": round(iv_change, 4),
                "iv_change_pct": round(iv_change_pct, 4),
                "recent_delta": round(recent_delta, 4),
                "recent_iv": round(recent_iv, 4),
            }

        return None

    def _evaluate_divergence(
        self,
        divergences: List[Dict[str, Any]],
        side: str,
        price: float,
        gex_calc: Any,
        rolling_data: Dict[str, Any],
        net_gamma: float,
        regime: str,
    ) -> Optional[Signal]:
        """Evaluate a set of divergent strikes for a signal."""
        if not divergences:
            return None

        num_strikes = len(divergences)
        avg_delta_change = sum(d["delta_change_pct"] for d in divergences) / num_strikes
        avg_iv_change = sum(d["iv_change_pct"] for d in divergences) / num_strikes

        # Find nearest strike for entry reference
        nearest_strike = divergences[0]["strike"]

        # Determine direction
        if side == "call":
            direction = Direction.LONG
        else:
            direction = Direction.SHORT

        confidence = self._compute_confidence(
            num_strikes, avg_delta_change, avg_iv_change,
            net_gamma, regime,
        )
        if confidence < 0.35:
            return None

        # Build signal
        entry = price
        reverse = 1 if side == "call" else -1
        stop = entry * (1 + STOP_PCT * reverse)
        risk = abs(entry - stop)
        target = entry + (risk * TARGET_RISK_MULT * reverse)

        side_label = "calls" if side == "call" else "puts"
        action = "accumulation" if side == "call" else "distribution"

        return Signal(
            direction=direction,
            confidence=round(confidence, 3),
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy_id=self.strategy_id,
            reason=(
                f"Delta-IV divergence: {num_strikes} {side_label} showing "
                f"delta up (Δ{avg_delta_change:.1%}) + IV down (Δ{avg_iv_change:.1%}) "
                f"— smart money {action}"
            ),
            metadata={
                "divergence_side": side,
                "num_strikes": num_strikes,
                "avg_delta_change_pct": round(avg_delta_change, 4),
                "avg_iv_change_pct": round(avg_iv_change, 4),
                "divergent_strikes": [d["strike"] for d in divergences[:5]],
                "net_gamma": round(net_gamma, 2),
                "regime": regime,
                "risk": round(risk, 2),
                "risk_reward_ratio": round(abs(target - entry) / risk, 2) if risk > 0 else 0,
            },
        )

    def _compute_confidence(
        self,
        num_strikes: int,
        avg_delta_change: float,
        avg_iv_change: float,
        net_gamma: float,
        regime: str,
    ) -> float:
        """
        Combine divergence factors into confidence.

        Returns 0.0–1.0.
        """
        # 1. Number of divergent strikes (0.20–0.30)
        strike_conf = 0.20 + 0.10 * min(1.0, (num_strikes - MIN_DIVERGENT_STRIKES) / 5.0)

        # 2. Delta change magnitude (0.20–0.25)
        delta_conf = 0.20 + 0.05 * min(1.0, avg_delta_change / 0.20)

        # 3. IV change magnitude (0.15–0.20)
        # More negative IV change = stronger signal
        iv_conf = 0.15 + 0.05 * min(1.0, abs(avg_iv_change) / 0.10)

        # 4. Regime alignment (0.05–0.10)
        regime_conf = 0.10 if regime == "POSITIVE" else 0.05

        # 5. Net gamma context (0.0–0.10)
        gamma_conf = 0.10 if abs(net_gamma) > 500000 else 0.0

        # Normalize each component to [0,1] and average
        norm_strike = (strike_conf - 0.20) / (0.30 - 0.20) if 0.30 != 0.20 else 1.0
        norm_delta = (delta_conf - 0.20) / (0.25 - 0.20) if 0.25 != 0.20 else 1.0
        norm_iv = (iv_conf - 0.15) / (0.20 - 0.15) if 0.20 != 0.15 else 1.0
        norm_regime = (regime_conf - 0.05) / (0.10 - 0.05) if 0.10 != 0.05 else 1.0
        norm_gamma = gamma_conf / 0.10 if 0.10 != 0 else 0.0
        confidence = (norm_strike + norm_delta + norm_iv + norm_regime + norm_gamma) / 5.0
        return min(1.0, max(0.0, confidence))
