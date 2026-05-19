"""Sample strategy configurations and outputs for testing."""

from typing import Any, Dict, List


# =============================================================================
# Sample Strategy Configurations
# =============================================================================

SAMPLE_STRATEGY_CONFIG: Dict[str, Any] = {
    "global": {
        "min_confidence": 0.35,
        "max_signals_per_tick": 10,
        "signal_log_path": "log/signals.jsonl",
        "dedup_window_seconds": 60.0,
    },
    "filter": {
        "net_gamma": {
            "enabled": True,
            "params": {
                "flip_buffer": 0.50,
            },
        },
    },
    "layer1": {
        "gamma_wall_bounce": {
            "enabled": True,
            "params": {
                "min_wall_gex": 100000,
                "price_distance_threshold": 2.0,
            },
            "tracker": {
                "max_hold_seconds": 300,
            },
        },
        "gamma_flip_breakout": {
            "enabled": True,
            "params": {
                "breakout_threshold": 0.25,
            },
            "tracker": {
                "max_hold_seconds": 600,
            },
        },
        "gamma_squeeze": {
            "enabled": True,
            "params": {
                "squeeze_threshold": 0.70,
            },
            "tracker": {
                "max_hold_seconds": 450,
            },
        },
        "gamma_squeeze": {
            "enabled": True,
            "params": {
                "squeeze_threshold": 0.70,
            },
            "tracker": {
                "max_hold_seconds": 450,
            },
        },
        "gex_imbalance": {
            "enabled": True,
            "params": {
                "imbalance_ratio": 2.0,
            },
            "tracker": {
                "max_hold_seconds": 300,
            },
        },
        "confluence_reversal": {
            "enabled": True,
            "params": {
                "min_confluence_count": 3,
            },
            "tracker": {
                "max_hold_seconds": 400,
            },
        },
        "vol_compression_range": {
            "enabled": True,
            "params": {
                "compression_threshold": 0.30,
            },
            "tracker": {
                "max_hold_seconds": 500,
            },
        },
        "gex_divergence": {
            "enabled": True,
            "params": {
                "divergence_threshold": 0.15,
            },
            "tracker": {
                "max_hold_seconds": 350,
            },
        },
        "magnet_accelerate": {
            "enabled": True,
            "params": {
                "magnet_distance": 1.5,
            },
            "tracker": {
                "max_hold_seconds": 250,
            },
        },
    },
    "layer2": {
        "delta_gamma_squeeze": {
            "enabled": True,
            "params": {
                "squeeze_threshold": 0.75,
            },
            "tracker": {
                "max_hold_seconds": 600,
            },
        },
        "delta_volume_exhaustion": {
            "enabled": True,
            "params": {
                "exhaustion_threshold": 0.80,
            },
            "tracker": {
                "max_hold_seconds": 450,
            },
        },
        "call_put_flow_asymmetry": {
            "enabled": True,
            "params": {
                "asymmetry_ratio": 1.5,
            },
            "tracker": {
                "max_hold_seconds": 400,
            },
        },
        "iv_gex_divergence": {
            "enabled": True,
            "params": {
                "divergence_threshold": 0.20,
            },
            "tracker": {
                "max_hold_seconds": 500,
            },
        },
        "delta_iv_divergence": {
            "enabled": True,
            "params": {
                "divergence_threshold": 0.25,
            },
            "tracker": {
                "max_hold_seconds": 550,
            },
        },
    },
    "layer3": {
        "gamma_volume_convergence": {
            "enabled": True,
            "params": {
                "convergence_threshold": 0.65,
            },
            "tracker": {
                "max_hold_seconds": 700,
            },
        },
        "iv_band_breakout": {
            "enabled": True,
            "params": {
                "breakout_multiplier": 2.0,
            },
            "tracker": {
                "max_hold_seconds": 800,
            },
        },
        "strike_concentration": {
            "enabled": True,
            "params": {
                "concentration_threshold": 0.30,
            },
            "tracker": {
                "max_hold_seconds": 450,
            },
        },
        "theta_burn": {
            "enabled": True,
            "params": {
                "theta_threshold": 0.10,
            },
            "tracker": {
                "max_hold_seconds": 300,
            },
        },
    },
    "full_data": {
        "iv_skew_squeeze": {
            "enabled": True,
            "params": {
                "skew_threshold": 0.15,
            },
            "tracker": {
                "max_hold_seconds": 900,
            },
        },
        "prob_weighted_magnet": {
            "enabled": True,
            "params": {
                "magnet_weight": 0.60,
            },
            "tracker": {
                "max_hold_seconds": 600,
            },
        },
        "prob_distribution_shift": {
            "enabled": True,
            "params": {
                "shift_threshold": 0.10,
            },
            "tracker": {
                "max_hold_seconds": 700,
            },
        },
        "extrinsic_intrinsic_flow": {
            "enabled": True,
            "params": {
                "flow_ratio": 1.8,
            },
            "tracker": {
                "max_hold_seconds": 500,
            },
        },
    },
}


# =============================================================================
# Sample Strategy Outputs
# =============================================================================

SAMPLE_STRATEGY_OUTPUT_LAYER1: Dict[str, Any] = {
    "gamma_wall_bounce": {
        "signals_generated": 25,
        "avg_confidence": 0.72,
        "last_signal_time": 1716072180.0,
        "params_used": {
            "min_wall_gex": 100000,
            "price_distance_threshold": 2.0,
        },
    },
    "gamma_flip_breakout": {
        "signals_generated": 18,
        "avg_confidence": 0.68,
        "last_signal_time": 1716072120.0,
        "params_used": {
            "breakout_threshold": 0.25,
        },
    },
    "gamma_squeeze": {
        "signals_generated": 12,
        "avg_confidence": 0.75,
        "last_signal_time": 1716072060.0,
        "params_used": {
            "squeeze_threshold": 0.70,
        },
    },
}

SAMPLE_STRATEGY_OUTPUT_LAYER2: Dict[str, Any] = {
    "delta_gamma_squeeze": {
        "signals_generated": 15,
        "avg_confidence": 0.78,
        "last_signal_time": 1716072180.0,
    },
    "delta_volume_exhaustion": {
        "signals_generated": 10,
        "avg_confidence": 0.71,
        "last_signal_time": 1716072120.0,
    },
    "call_put_flow_asymmetry": {
        "signals_generated": 8,
        "avg_confidence": 0.69,
        "last_signal_time": 1716072060.0,
    },
}

SAMPLE_STRATEGY_OUTPUT_LAYER3: Dict[str, Any] = {
    "gamma_volume_convergence": {
        "signals_generated": 12,
        "avg_confidence": 0.74,
        "last_signal_time": 1716072180.0,
    },
    "iv_band_breakout": {
        "signals_generated": 6,
        "avg_confidence": 0.76,
        "last_signal_time": 1716072120.0,
    },
}

SAMPLE_STRATEGY_OUTPUT_FULL_DATA: Dict[str, Any] = {
    "iv_skew_squeeze": {
        "signals_generated": 8,
        "avg_confidence": 0.73,
        "last_signal_time": 1716072180.0,
    },
    "prob_weighted_magnet": {
        "signals_generated": 10,
        "avg_confidence": 0.70,
        "last_signal_time": 1716072120.0,
    },
}


# =============================================================================
# Sample Data for Strategy Evaluation
# =============================================================================

SAMPLE_EVALUATION_DATA: Dict[str, Any] = {
    "underlying_price": 195.50,
    "timestamp": 1716072180.0,
    "regime": "POSITIVE",
    "symbol": "TSLA",
    "params": {
        "gamma_wall_bounce": {
            "min_wall_gex": 100000,
            "price_distance_threshold": 2.0,
        },
    },
    # Mock references (would be actual objects in real usage)
    "gex_calculator": "mock_gex_calculator",
    "rolling_data": {
        "price_5m": "mock_rolling_window",
        "net_gamma_5m": "mock_rolling_window",
        "volume_5m": "mock_rolling_window",
    },
}

SAMPLE_EVALUATION_DATA_NEGATIVE_REGIME: Dict[str, Any] = {
    "underlying_price": 193.50,
    "timestamp": 1716072180.0,
    "regime": "NEGATIVE",
    "symbol": "TSLA",
    "gex_calculator": "mock_gex_calculator",
    "rolling_data": {},
}


# =============================================================================
# Strategy Layer Statistics
# =============================================================================

SAMPLE_LAYER_STATS: Dict[str, Any] = {
    "layer1": {
        "total_strategies": 9,
        "enabled_strategies": 9,
        "total_signals": 120,
        "avg_confidence": 0.71,
    },
    "layer2": {
        "total_strategies": 5,
        "enabled_strategies": 5,
        "total_signals": 55,
        "avg_confidence": 0.73,
    },
    "layer3": {
        "total_strategies": 4,
        "enabled_strategies": 4,
        "total_signals": 30,
        "avg_confidence": 0.75,
    },
    "full_data": {
        "total_strategies": 4,
        "enabled_strategies": 4,
        "total_signals": 35,
        "avg_confidence": 0.72,
    },
}


# =============================================================================
# Conflict Resolution Test Data
# =============================================================================

SAMPLE_CONFLICT_SCENARIOS: List[Dict[str, Any]] = [
    {
        "name": "Extreme confidence gap",
        "signals": [
            {"strategy": "layer1_a", "direction": "LONG", "confidence": 0.65, "layer": "layer1"},
            {"strategy": "layer2_a", "direction": "SHORT", "confidence": 0.92, "layer": "layer2"},
        ],
        "expected_suppressed": ["layer1_a"],
        "reason": "Extreme confidence gap (0.92 vs 0.65)",
    },
    {
        "name": "Layer priority",
        "signals": [
            {"strategy": "layer1_b", "direction": "LONG", "confidence": 0.75, "layer": "layer1"},
            {"strategy": "layer2_b", "direction": "SHORT", "confidence": 0.72, "layer": "layer2"},
        ],
        "expected_suppressed": ["layer1_b"],
        "reason": "Layer 2 priority over Layer 1",
    },
    {
        "name": "Same layer similar confidence",
        "signals": [
            {"strategy": "layer1_c", "direction": "LONG", "confidence": 0.70, "layer": "layer1"},
            {"strategy": "layer1_d", "direction": "SHORT", "confidence": 0.68, "layer": "layer1"},
        ],
        "expected_suppressed": [],
        "reason": "Same layer, similar confidence - keep both",
    },
]
