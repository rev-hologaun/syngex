"""Structural Integrity module — three validators + orchestrator.

Three independent validators (MomentumValidator, LiquidityAnchor,
RegimeCoherence) feed into a StructuralIntegrity orchestrator that
combines their scores via a weighted harmonic mean.
"""


class MomentumValidator:
    """Validates momentum signal strength from volume/z-score and delta density."""

    DEFAULT_WEIGHT = 1.0
    FLOOR = 0.01

    def __init__(self, volume_zscore: float, delta_density: float, price: float, net_gamma: float = 0.0):
        self.volume_zscore = volume_zscore
        self.delta_density = delta_density
        self.price = price
        self.net_gamma = net_gamma

    def compute(self) -> float:
        """Returns 0.0–1.0 based on momentum signal."""
        # Primary: force_index from delta_density / volume_zscore
        force_index = self.delta_density / max(self.volume_zscore, 1.0)
        if force_index > 100:
            return 1.0
        if force_index < 0:
            return 0.0

        primary_score = min(1.0, force_index / 100.0)

        # Fallback: when delta_density is effectively zero, use |net_gamma| as momentum proxy
        if self.delta_density == 0.0:
            gamma_norm = min(1.0, abs(self.net_gamma) / 1_000_000)
            # Scale: >100K net_gamma = strong momentum, <1K = weak
            return max(0.01, gamma_norm)

        return primary_score


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
        """Returns 0.0–1.0 based on liquidity proximity.

        wall_depth = raw GEX magnitude (dollars), distance_to_wall_pct = % to wall.
        Score = proximity_score * depth_score, where proximity measures how close
        price is to the wall and depth measures wall strength relative to 50M reference.
        """
        if self.wall_depth <= 0:
            return 0.0
        proximity_score = max(0.0, 1.0 - self.distance_to_wall_pct * 10)
        depth_score = min(1.0, self.wall_depth / 50_000_000)
        return proximity_score * depth_score


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
        self._cached_scores = None
        self._cached_harmonic = None

    def compute(self) -> float:
        """Returns harmonic mean of three scores (0.0–1.0)."""
        if self._cached_harmonic is not None:
            return self._cached_harmonic
        scores = [self.mv.compute(), self.la.compute(), self.rc.compute()]
        scores = [max(s, self.FLOOR) for s in scores]
        weights = self.DEFAULT_WEIGHT
        self._cached_harmonic = sum(weights) / sum(w / s for w, s in zip(weights, scores))
        self._cached_scores = {
            "momentum": scores[0],
            "liquidity": scores[1],
            "regime": scores[2],
        }
        return self._cached_harmonic

    def get_scores(self) -> dict:
        """Returns individual component scores."""
        if self._cached_scores is not None:
            return self._cached_scores
        self._cached_scores = {
            "momentum": self.mv.compute(),
            "liquidity": self.la.compute(),
            "regime": self.rc.compute(),
        }
        return self._cached_scores

    def reset(self):
        """Clear cached scores for reusability."""
        self._cached_scores = None
        self._cached_harmonic = None


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
    """Convenience factory to create and return a StructuralIntegrity instance.

    Note: wall_gex is currently reserved for future use.
    """
    price = 0.0  # placeholder — not needed for current logic
    mv = MomentumValidator(volume_zscore, delta_density, price, net_gamma)
    la = LiquidityAnchor(distance_to_wall_pct, wall_depth, wall_depth, price)
    rc = RegimeCoherence(signal_direction, regime, net_gamma)
    return StructuralIntegrity(mv, la, rc)
