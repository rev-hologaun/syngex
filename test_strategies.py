#!/usr/bin/env python3
"""
test_strategies.py — Strategy Unit Test Harness

Runs all strategies with synthetic/mock data to verify they don't crash.
No live market data required.

Usage:
    python3 test_strategies.py
    python3 test_strategies.py --verbose  # Show all signals
    python3 test_strategies.py --strategy VAMP_MOMENTUM  # Test single strategy
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("StrategyTester")

# ---------------------------------------------------------------------------
# Mock Data Generator
# ---------------------------------------------------------------------------

def create_mock_rolling_window(count: int = 100, values: Optional[List[float]] = None):
    """Create a mock RollingWindow-like object."""
    from strategies.rolling_window import RollingWindow
    import time
    
    if values is None:
        values = [1.0] * count
    
    # Create a count-based RollingWindow and push values
    mock = RollingWindow(window_type="count", window_size=1000)
    now = time.time()
    for v in values:
        mock.push(v, timestamp=now)
    
    return mock


def create_mock_data(symbol: str = "TSLA"):
    """Create synthetic mock data for strategy testing."""
    import random
    import time
    
    # Mock GEXCalculator
    class MockGEXCalculator:
        regime = "POSITIVE"
        underlying_price = 250.0
        
        def get_total_gex_at_strike(self, strike: float) -> float:
            return random.uniform(-10000, 10000)
        
        def get_net_gex_at_strike(self, strike: float) -> float:
            return random.uniform(-5000, 5000)
        
        def get_atm_greeks(self) -> Dict[str, float]:
            return {"delta": 0.5, "gamma": 0.01, "vega": 10.0, "theta": -5.0}
        
        def get_wall_classifications(self, threshold: float = 0.01) -> List[Dict]:
            return [{"strike": 250.0, "type": "call", "gex": 10000}]
        
        class _MockBucket:
            def normalized_gamma(self) -> float:
                return 0.5
        
        @property
        def _ladder(self) -> Dict:
            return {250.0: self._MockBucket()}
        
        def get_gamma_walls(self, threshold: float = 0.01) -> List[Dict]:
            return [{"strike": 250.0, "gex": 10000, "side": "call"}]
        
        def get_summary(self) -> Dict:
            return {"total_gex": 50000, "net_gex": 10000}
        
        def get_greeks_summary(self) -> Dict:
            return {"atm_delta": 0.5, "atm_gamma": 0.01, "atm_iv": 0.3}
        
        def get_gamma_flip(self) -> float:
            return 245.0
        
        def get_delta_by_strike(self, strike: float) -> Dict:
            return {"delta": 0.5, "gamma": 0.01}
    
    # Mock rolling data
    rolling_data = {
        # Layer 1 keys
        "KEY_GAMMA_WALL_5M": create_mock_rolling_window(values=[5000.0] * 100),
        "KEY_WALL_DISTANCE_5M": create_mock_rolling_window(values=[0.02] * 100),
        "KEY_MOMENTUM_SCORE_5M": create_mock_rolling_window(values=[0.6] * 100),
        "KEY_PROB_SCORE_5M": create_mock_rolling_window(values=[0.55] * 100),
        "KEY_MAGNET_TARGET_5M": create_mock_rolling_window(values=[250.0] * 100),
        "KEY_DISTANCE_TO_WALL_5M": create_mock_rolling_window(values=[0.015] * 100),
        "KEY_FLIP_DELTA_5M": create_mock_rolling_window(values=[1000.0] * 100),
        "KEY_GEX_ROC_5M": create_mock_rolling_window(values=[0.05] * 100),
        "KEY_REGIME_INTENSITY_5M": create_mock_rolling_window(values=[0.7] * 100),
        "KEY_GEX_ACCEL_5M": create_mock_rolling_window(values=[500.0] * 100),
        "KEY_IV_ROC_BONUS_5M": create_mock_rolling_window(values=[0.1] * 100),
        
        # Layer 2 keys
        "KEY_OBI_5M": create_mock_rolling_window(values=[0.3] * 100),
        "KEY_AGGRESSIVE_BUY_VOL_5M": create_mock_rolling_window(values=[1000.0] * 100),
        "KEY_AGGRESSIVE_SELL_VOL_5M": create_mock_rolling_window(values=[800.0] * 100),
        "KEY_AF_5M": create_mock_rolling_window(values=[0.55] * 100),
        "KEY_TRADE_SIZE_5M": create_mock_rolling_window(values=[100.0] * 100),
        "KEY_ATM_DELTA_5M": create_mock_rolling_window(values=[0.5] * 100),
        "KEY_ATM_IV_5M": create_mock_rolling_window(values=[0.3] * 100),
        "KEY_VOLUME_5M": create_mock_rolling_window(values=[10000.0] * 100),
        "KEY_VOLUME_DOWN_5M": create_mock_rolling_window(values=[4000.0] * 100),
        "KEY_VOLUME_UP_5M": create_mock_rolling_window(values=[6000.0] * 100),
        "KEY_NET_GAMMA_5M": create_mock_rolling_window(values=[5000.0] * 100),
        "KEY_TOTAL_DELTA_5M": create_mock_rolling_window(values=[1000.0] * 100),
        "KEY_WALL_DELTA_5M": create_mock_rolling_window(values=[2000.0] * 100),
        "KEY_TOTAL_GAMMA_5M": create_mock_rolling_window(values=[10000.0] * 100),
        "KEY_IV_SKEW_5M": create_mock_rolling_window(values=[0.05] * 100),
        "KEY_SKEW_WIDTH_5M": create_mock_rolling_window(values=[0.1] * 100),
        "KEY_FLOW_RATIO_5M": create_mock_rolling_window(values=[1.2] * 100),
        "KEY_EXTRINSIC_PROXY_5M": create_mock_rolling_window(values=[50000.0] * 100),
        "KEY_EXTRINSIC_ROC_5M": create_mock_rolling_window(values=[0.02] * 100),
        "KEY_PROB_MOMENTUM_5M": create_mock_rolling_window(values=[0.6] * 100),
        "KEY_PHI_CALL_5M": create_mock_rolling_window(values=[30000.0] * 100),
        "KEY_PHI_PUT_5M": create_mock_rolling_window(values=[20000.0] * 100),
        "KEY_RPHI_5M": create_mock_rolling_window(values=[1.5] * 100),
        "KEY_DEPTH_IMBAL_5M": create_mock_rolling_window(values=[0.2] * 100),
        "KEY_DEPTH_DECAY_5M": create_mock_rolling_window(values=[0.1] * 100),
        "KEY_PARTICIPANT_DIV_5M": create_mock_rolling_window(values=[0.7] * 100),
        "KEY_CONCUSSION_RATIO_5M": create_mock_rolling_window(values=[1.3] * 100),
        "KEY_PARTICIPANT_CONV_5M": create_mock_rolling_window(values=[0.6] * 100),
        "KEY_EXCHANGE_IMBAL_5M": create_mock_rolling_window(values=[0.15] * 100),
        "KEY_OB_FRAGMENT_5M": create_mock_rolling_window(values=[0.25] * 100),
        "KEY_STACKING_5M": create_mock_rolling_window(values=[0.4] * 100),
        "KEY_VORTEX_5M": create_mock_rolling_window(values=[0.5] * 100),
        "KEY_DELTA_VOLUME_5M": create_mock_rolling_window(values=[500.0] * 100),
        "KEY_DELTA_IV_5M": create_mock_rolling_window(values=[0.03] * 100),
        
        # Layer 3 keys
        "KEY_GAMMA_VOL_5M": create_mock_rolling_window(values=[0.5] * 100),
        "KEY_IV_BAND_5M": create_mock_rolling_window(values=[0.2] * 100),
        "KEY_STRIKE_CONC_5M": create_mock_rolling_window(values=[0.8] * 100),
        "KEY_THETA_5M": create_mock_rolling_window(values=[-50.0] * 100),
        
        # Full data keys
        "KEY_SKEW_CHANGE_5M": create_mock_rolling_window(values=[0.01] * 100),
        "KEY_VSI_MAGNITUDE_5M": create_mock_rolling_window(values=[0.3] * 100),
        "KEY_SYNC_CORR_5M": create_mock_rolling_window(values=[-0.5] * 100),
        "KEY_SYNC_SIGMA_5M": create_mock_rolling_window(values=[0.02] * 100),
        "KEY_BIGGEST_SIZE_5M": create_mock_rolling_window(values=[500.0] * 100),
        "KEY_SMALLEST_SIZE_5M": create_mock_rolling_window(values=[50.0] * 100),
        "KEY_CONCENTRATION_RATIO_5M": create_mock_rolling_window(values=[10.0] * 100),
        "KEY_CONCENTRATION_SIGMA_5M": create_mock_rolling_window(values=[2.0] * 100),
        "KEY_NUM_PARTICIPANTS_5M": create_mock_rolling_window(values=[2.0] * 100),
        "KEY_IV_ROC_5M": create_mock_rolling_window(values=[0.05] * 100),
        "KEY_VOL_CONV_5M": create_mock_rolling_window(values=[0.6] * 100),
        
        # Market depth aggregate
        "KEY_MARKET_DEPTH_AGG": {
            "bid_levels": [
                {"strike": 250.0, "size": 500, "gex": 10000},
                {"strike": 249.5, "size": 200, "gex": 5000},
                {"strike": 249.0, "size": 100, "gex": 2000},
            ],
            "ask_levels": [
                {"strike": 250.5, "size": 300, "gex": 8000},
                {"strike": 251.0, "size": 150, "gex": 4000},
                {"strike": 251.5, "size": 80, "gex": 2000},
            ],
        },
        
        # Call/put ratio for some strategies
        "call_put_ratio": 1.2,
        "volume_5m": create_mock_rolling_window(values=[10000.0] * 100),
    }
    
    # Mock params
    params = {
        "vamp_momentum": {"min_data_points": 5, "min_confidence": 0.10},
        "gamma_wall_bounce": {"min_data_points": 5, "min_confidence": 0.10},
    }
    
    mock_data = {
        "underlying_price": 250.0,
        "gex_calculator": MockGEXCalculator(),
        "rolling_data": rolling_data,
        "timestamp": time.time(),
        "regime": "POSITIVE",
        "params": params,
        "symbol": symbol,
    }
    
    return mock_data


# ---------------------------------------------------------------------------
# Strategy Test Runner
# ---------------------------------------------------------------------------

from strategies.layer1 import (
    GammaWallBounce,
    MagnetAccelerate,
    GammaFlipBreakout,
    GammaSqueeze,
    GEXImbalance,
    ConfluenceReversal,
    VolCompressionRange,
    GEXDivergence,
)
from strategies.layer2 import (
    DeltaGammaSqueeze,
    DeltaVolumeExhaustion,
    CallPutFlowAsymmetry,
    IVGEXDivergence,
    VampMomentum,
    ObiAggressionFlow,
    DepthDecayMomentum,
    DepthImbalanceMomentum,
)
from strategies.layer2.exchange_flow_concentration import ExchangeFlowConcentration
from strategies.layer2.participant_diversity_conviction import ParticipantDiversityConviction
from strategies.layer2.participant_divergence_scalper import ParticipantDivergenceScalper
from strategies.layer2.delta_iv_divergence import DeltaIVDivergence
from strategies.layer2.exchange_flow_imbalance import ExchangeFlowImbalance
from strategies.layer2.exchange_flow_asymmetry import ExchangeFlowAsymmetry
from strategies.layer2.order_book_fragmentation import OrderBookFragmentation
from strategies.layer2.order_book_stacking import OrderBookStacking
from strategies.layer2.vortex_compression_breakout import VortexCompressionBreakout
from strategies.layer3 import (
    GammaVolumeConvergence,
    IVBandBreakout,
    StrikeConcentration,
    ThetaBurn,
)
from strategies.full_data import (
    IVSkewSqueeze,
    ProbWeightedMagnet,
    ProbDistributionShift,
    ExtrinsicIntrinsicFlow,
    GhostPremium,
    SkewDynamics,
    SmileDynamics,
    ExtrinsicFlow,
    GammaBreaker,
    IronAnchor,
    SentimentSync,
    WhaleTracker,
)

STRATEGY_CLASSES = [
    # Layer 1
    GammaWallBounce,
    MagnetAccelerate,
    GammaFlipBreakout,
    GammaSqueeze,
    GEXImbalance,
    ConfluenceReversal,
    VolCompressionRange,
    GEXDivergence,
    # Layer 2
    DeltaGammaSqueeze,
    DeltaVolumeExhaustion,
    CallPutFlowAsymmetry,
    IVGEXDivergence,
    VampMomentum,
    ObiAggressionFlow,
    DepthDecayMomentum,
    DepthImbalanceMomentum,
    ExchangeFlowConcentration,
    ParticipantDiversityConviction,
    ParticipantDivergenceScalper,
    DeltaIVDivergence,
    ExchangeFlowImbalance,
    ExchangeFlowAsymmetry,
    OrderBookFragmentation,
    OrderBookStacking,
    VortexCompressionBreakout,
    # Layer 3
    GammaVolumeConvergence,
    IVBandBreakout,
    StrikeConcentration,
    ThetaBurn,
    # Full Data
    IVSkewSqueeze,
    ProbWeightedMagnet,
    ProbDistributionShift,
    ExtrinsicIntrinsicFlow,
    GhostPremium,
    SkewDynamics,
    SmileDynamics,
    ExtrinsicFlow,
    GammaBreaker,
    IronAnchor,
    SentimentSync,
    WhaleTracker,
]


def test_strategy(strategy_class, mock_data, verbose=False):
    """Test a single strategy with mock data."""
    strategy_name = strategy_class.__name__
    
    try:
        # Instantiate strategy
        strategy = strategy_class()
        
        # Evaluate with mock data
        signals = strategy.evaluate(mock_data)
        
        # Count signals
        signal_count = len(signals)
        
        if verbose and signals:
            for sig in signals:
                logger.info(f"  → {sig.direction.value}: conf={sig.confidence:.3f}, entry={sig.entry}")
        
        return {
            "name": strategy_name,
            "status": "PASS",
            "signals": signal_count,
            "error": None,
        }
        
    except Exception as e:
        return {
            "name": strategy_name,
            "status": "FAIL",
            "signals": 0,
            "error": str(e),
        }


def main():
    """Run all strategy tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Syngex strategies with mock data")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all signals")
    parser.add_argument("--strategy", "-s", type=str, help="Test single strategy by name")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("🧪 Strategy Test Harness Starting")
    logger.info("=" * 60)
    
    # Create mock data
    logger.info("Creating mock data...")
    mock_data = create_mock_data("TSLA")
    logger.info("Mock data ready")
    
    # Filter strategies if requested
    if args.strategy:
        strategy_classes = [s for s in STRATEGY_CLASSES if args.strategy.lower() in s.__name__.lower()]
        if not strategy_classes:
            logger.error(f"No strategy found matching: {args.strategy}")
            sys.exit(1)
    else:
        strategy_classes = STRATEGY_CLASSES
    
    # Test all strategies
    results = []
    passed = 0
    failed = 0
    
    logger.info(f"\nTesting {len(strategy_classes)} strategies...\n")
    
    for strategy_class in strategy_classes:
        result = test_strategy(strategy_class, mock_data, args.verbose)
        results.append(result)
        
        if result["status"] == "PASS":
            passed += 1
            status_icon = "✅"
        else:
            failed += 1
            status_icon = "❌"
        
        # Log result
        if result["status"] == "PASS":
            logger.info(f"{status_icon} {result['name']}: PASS ({result['signals']} signals)")
        else:
            logger.error(f"{status_icon} {result['name']}: FAIL - {result['error']}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total: {len(results)} strategies")
    logger.info(f"Passed: {passed} ✅")
    logger.info(f"Failed: {failed} ❌")
    
    if failed > 0:
        logger.info("\nFailed strategies:")
        for r in results:
            if r["status"] == "FAIL":
                logger.error(f"  - {r['name']}: {r['error']}")
        sys.exit(1)
    else:
        logger.info("\n🎉 All strategies passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
