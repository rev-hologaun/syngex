"""Structural Integrity module — three validators + orchestrator.

Three independent validators (MomentumValidator, LiquidityAnchor,
RegimeCoherence) feed into a StructuralIntegrity orchestrator that
combines their scores via a weighted harmonic mean.
"""


class MomentumValidator:
    """Validates momentum signal strength from volume/z-score and delta density."""

    DEFAULT_WEIGHT = 1.0
    FLOOR = 0.01

    def __init__(self, volume_zscore: float, delta_density: float, price: float):
        self.volume_zscore = volume_zscore
        self.delta_density = delta_density
        self.price = price

    def compute(self) -> float:
        """Returns 0.0–1.0 based on momentum signal."""
        force_index = self.delta_density / max(self.volume_zscore, 1.0)
        # Thresholds tunable via class constants
        if force_index > 100:
            return 1.0
        if force_index < 0:
            return 0.0
        return min(1.0, force_index / 100.0)


class LiquidityAnchor:
    """Validates liquidity proximity — how close price is to a meaningful wall."""

    DEFAULT_WEIGHT = 1.0
    FLOOR = 0.01

    def __init__(self, distance_to_wall_pct: float, wall_depth: float, book_depth: float, price: float):
        self.distance_to_wall_pct = distance_to_wall_pct
        self.wall_depth = wall_depth
        self.book_depth = book_depth
        self.price = price

    def compute(self) -> float:
        """Returns 0.0–1.0 based on liquidity proximity."""
        if self.wall_depth <= 0:
            return 0.0
        wall_interaction = self.distance_to_wall_pct / max(self.wall_depth, 1.0)
        # Near wall with depth = high integrity
        if wall_interaction < 0.1:
            return min(1.0, 1.0 - wall_interaction)
        return max(0.0, 1.0 - wall_interaction * 0.5)


class RegimeCoherence:
    """Validates alignment between signal direction and market regime."""

    DEFAULT_WEIGHT = 1.0
    FLOOR = 0.01

    def __init__(self, signal_direction: str, regime: str, net_gamma: float):
        self.signal_direction = signal_direction  # "long" or "short"
        self.regime = regime  # "POSITIVE" or "NEGATIVE"
        self.net_gamma = net_gamma

    def compute(self) -> float:
        """Returns 0.0–1.0 based on signal × regime alignment."""
        if self.regime == "POSITIVE":
            # Positive regime + long signal = coherent (breakout)
            return 1.0 if self.signal_direction == "long" else 0.3
        elif self.regime == "NEGATIVE":
            # Negative regime + short signal = coherent (fade)
            return 1.0 if self.signal_direction == "short" else 0.3
        return 0.5  # Unknown regime = neutral


class StructuralIntegrity:
    """Orchestrator — harmonic mean of three validator scores."""

    DEFAULT_WEIGHT = [1.0, 1.0, 1.0]  # equal weights for harmonic mean
    FLOOR = 0.01

    def __init__(self, mv: MomentumValidator, la: LiquidityAnchor, rc: RegimeCoherence):
        self.mv = mv
        self.la = la
        self.rc = rc

    def compute(self) -> float:
        """Returns harmonic mean of three scores (0.0–1.0)."""
        scores = [self.mv.compute(), self.la.compute(), self.rc.compute()]
        scores = [max(s, self.FLOOR) for s in scores]
        weights = self.DEFAULT_WEIGHT
        # Weighted harmonic mean: sum(w) / sum(w/score)
        return sum(weights) / sum(w / s for w, s in zip(weights, scores))

    def get_scores(self) -> dict:
        """Returns individual component scores."""
        return {
            "momentum": self.mv.compute(),
            "liquidity": self.la.compute(),
            "regime": self.rc.compute(),
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
    """Convenience factory to create and return a StructuralIntegrity instance."""
    price = 0.0  # placeholder — not needed for current logic
    mv = MomentumValidator(volume_zscore, delta_density, price)
    la = LiquidityAnchor(distance_to_wall_pct, wall_gex, wall_depth, price)
    rc = RegimeCoherence(signal_direction, regime, net_gamma)
    return StructuralIntegrity(mv, la, rc)
