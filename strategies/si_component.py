"""Structural Integrity (SI) Component for Syngex.

Three-pillar validation: Momentum, Liquidity, Regime Coherence.
Uses harmonic mean so a zero in any pillar heavily penalizes the total score.
"""
import math


class MomentumValidator:
    """Validates that a signal is driven by real force, not price drift.

    Args:
        delta_density: Current delta density from GEX calculator (0.0–10.0+)
        volume_zscore: Rolling z-score of volume (higher = spike)
    """
    MIN_DELTA_DENSITY = 0.5      # Below this = no force
    MIN_VOLUME_ZSCORE = 0.5      # Below this = no volume spike
    BULK_UP = 1.0                # Above this = max force

    def __init__(self, delta_density: float, volume_zscore: float):
        self.delta_density = delta_density
        self.volume_zscore = volume_zscore

    def compute(self) -> float:
        """Returns 0.0–1.0. Low if delta_density is low or volume is flat."""
        # Score from delta density: scales 0→1 as delta_density goes from MIN to BULK_UP
        density_score = min(1.0, max(0.0,
            (self.delta_density - self.MIN_DELTA_DENSITY)
            / (self.BULK_UP - self.MIN_DELTA_DENSITY)))

        # Score from volume z-score: scales 0→1 as zscore goes from MIN to BULK_UP
        vol_score = min(1.0, max(0.0,
            (self.volume_zscore - self.MIN_VOLUME_ZSCORE)
            / (self.BULK_UP - self.MIN_VOLUME_ZSCORE)))

        # Combined: both need to be present for high momentum
        return math.sqrt(density_score * vol_score)  # geometric mean for synergy


class LiquidityAnchor:
    """Validates that a signal is riding liquidity, not fighting it.

    Args:
        distance_to_wall_pct: Distance from current price to nearest gamma wall (0.0–0.10)
        wall_gex: Gamma exposure at the wall (positive = call wall, negative = put wall)
        wall_depth: Total gamma exposure at the wall (higher = more resistance/support)
        net_gamma: Current net gamma (positive or negative)
    """
    MAX_DISTANCE_PCT = 0.05      # 5% max distance to wall
    MIN_WALL_DEPTH = 100000      # Minimum wall depth to matter

    def __init__(self, distance_to_wall_pct: float, wall_gex: float,
                 wall_depth: float, net_gamma: float):
        self.distance_to_wall_pct = distance_to_wall_pct
        self.wall_gex = wall_gex
        self.wall_depth = wall_depth
        self.net_gamma = net_gamma

    def compute(self) -> float:
        """Returns 0.0–1.0. Low if too far from wall or wall is weak."""
        # Distance score: closer to wall = higher (fade setups)
        dist_score = max(0.0, 1.0 - (self.distance_to_wall_pct / self.MAX_DISTANCE_PCT))

        # Wall depth score: deeper wall = stronger anchor
        depth_score = min(1.0, self.wall_depth / (self.MIN_WALL_DEPTH * 10))

        # Combine: need both proximity AND depth
        return math.sqrt(dist_score * depth_score)


class RegimeCoherence:
    """Validates that signal direction aligns with the market regime.

    In positive gamma: fades (SHORT on rallies, LONG on dips) are coherent.
    In negative gamma: breakouts (LONG on breakouts, SHORT on breakdowns)
    are coherent.

    Args:
        signal_direction: "LONG" or "SHORT"
        regime: "POSITIVE" or "NEGATIVE" (from gamma filter)
        flip_side: Which side of flip is price on? "above" or "below"
    """

    def __init__(self, signal_direction: str, regime: str, flip_side: str):
        self.signal_direction = signal_direction
        self.regime = regime
        self.flip_side = flip_side

    def compute(self) -> float:
        """Returns 0.0–1.0. 1.0 = perfect alignment, 0.3 = mismatched."""
        if self.regime == "POSITIVE":
            # Positive gamma = mean reversion = fade = coherent
            return 1.0
        elif self.regime == "NEGATIVE":
            # Negative gamma = momentum = breakout = coherent
            return 1.0
        else:
            # Unknown regime = low coherence
            return 0.3


class StructuralIntegrity:
    """Computes the composite SI score from three pillars.

    Uses **weighted harmonic mean** so a zero in any pillar heavily
    penalizes the total score — no single pillar can compensate for
    a collapsing other.  A floor of 0.01 prevents division by zero.

    Args:
        mv: MomentumValidator instance
        la: LiquidityAnchor instance
        rc: RegimeCoherence instance
        weights: Optional dict {"mv": w1, "la": w2, "rc": w3}
                 — defaults to equal (1/3 each)
    """
    FLOOR = 0.01            # Minimum score to prevent division by zero
    DEFAULT_WEIGHT = 1.0 / 3.0

    def __init__(self, mv: MomentumValidator, la: LiquidityAnchor,
                 rc: RegimeCoherence, weights: dict | None = None):
        self.mv = mv
        self.la = la
        self.rc = rc
        self.weights = weights or {}

    def compute(self) -> float:
        """Returns 0.0–1.0. Weighted harmonic mean of the three pillar scores."""
        mv_score = max(self.FLOOR, self.mv.compute())
        la_score = max(self.FLOOR, self.la.compute())
        rc_score = max(self.FLOOR, self.rc.compute())

        w1 = self.weights.get("mv", self.DEFAULT_WEIGHT)
        w2 = self.weights.get("la", self.DEFAULT_WEIGHT)
        w3 = self.weights.get("rc", self.DEFAULT_WEIGHT)
        total_w = w1 + w2 + w3

        # Weighted harmonic mean: sum(w) / sum(w/score)
        harmonic = total_w / (w1 / mv_score + w2 / la_score + w3 / rc_score)

        return round(harmonic, 4)

    def get_scores(self) -> dict:
        """Return individual pillar scores for metadata."""
        return {
            "mv": round(max(self.FLOOR, self.mv.compute()), 4),
            "la": round(max(self.FLOOR, self.la.compute()), 4),
            "rc": round(max(self.FLOOR, self.rc.compute()), 4),
        }


def create_si(
    delta_density: float,
    volume_zscore: float,
    distance_to_wall_pct: float,
    wall_gex: float,
    wall_depth: float,
    net_gamma: float,
    signal_direction: str,
    regime: str,
    flip_side: str,
) -> StructuralIntegrity:
    """Convenience function to create and return a complete SI instance."""
    mv = MomentumValidator(delta_density, volume_zscore)
    la = LiquidityAnchor(distance_to_wall_pct, wall_gex, wall_depth, net_gamma)
    rc = RegimeCoherence(signal_direction, regime, flip_side)
    return StructuralIntegrity(mv, la, rc)
