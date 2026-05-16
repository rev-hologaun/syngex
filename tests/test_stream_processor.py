"""
tests/test_stream_processor.py — Unit tests for data/stream_processor.py

Basic unit tests for the StreamProcessor module.
"""

import pytest
import math
from unittest.mock import MagicMock, patch
from data.stream_processor import StreamProcessor, _compute_linear_slope


class TestComputeLinearSlope:
    """Tests for the _compute_linear_slope helper function."""

    def test_perfect_positive_correlation(self):
        """Test slope with perfect positive correlation."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        slope = _compute_linear_slope(x, y)
        assert abs(slope - 2.0) < 0.0001

    def test_perfect_negative_correlation(self):
        """Test slope with perfect negative correlation."""
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]
        slope = _compute_linear_slope(x, y)
        assert abs(slope - (-2.0)) < 0.0001

    def test_no_correlation(self):
        """Test slope with no correlation (flat line)."""
        x = [1, 2, 3, 4, 5]
        y = [5, 5, 5, 5, 5]
        slope = _compute_linear_slope(x, y)
        assert abs(slope) < 0.0001

    def test_insufficient_data(self):
        """Test slope with insufficient data points."""
        x = [1]
        y = [2]
        slope = _compute_linear_slope(x, y)
        assert slope == 0.0

    def test_empty_data(self):
        """Test slope with empty data."""
        x = []
        y = []
        slope = _compute_linear_slope(x, y)
        assert slope == 0.0


class TestStreamProcessor:
    """Tests for the StreamProcessor class."""

    @pytest.fixture
    def mock_calculator(self):
        """Create a mock GEXCalculator."""
        mock = MagicMock()
        mock._msg_count = 20
        mock.underlying_price = 100.0
        mock.get_greeks_summary.return_value = {}
        mock.get_total_delta_activity.return_value = 1000.0
        mock.get_net_gamma.return_value = 50000.0
        mock.get_iv_skew.return_value = 0.05
        mock.get_atm_strike.return_value = 100.0
        mock.get_iv_by_strike_avg.return_value = {}
        mock.get_iv_by_strike.return_value = None
        mock.get_delta_by_strike.return_value = {"net_delta": 0.0}
        mock.get_gamma_walls.return_value = []
        return mock

    @pytest.fixture
    def mock_rolling_data(self):
        """Create mock rolling windows."""
        from strategies.rolling_window import RollingWindow
        return {
            "price_5m": RollingWindow(window_type="time", window_size=300),
            "price_30m": RollingWindow(window_type="time", window_size=1800),
            "net_gamma_5m": RollingWindow(window_type="time", window_size=300),
            "volume_5m": RollingWindow(window_type="time", window_size=300),
            "volume_up_5m": RollingWindow(window_type="time", window_size=300),
            "volume_down_5m": RollingWindow(window_type="time", window_size=300),
            "total_delta_5m": RollingWindow(window_type="time", window_size=300),
            "total_gamma_5m": RollingWindow(window_type="time", window_size=300),
            "iv_skew_5m": RollingWindow(window_type="time", window_size=300),
            "atm_delta_5m": RollingWindow(window_type="time", window_size=300),
            "atm_iv_5m": RollingWindow(window_type="time", window_size=300),
            "delta_density_5m": RollingWindow(window_type="time", window_size=300),
            "volume_zscore_5m": RollingWindow(window_type="time", window_size=300),
            "order_book_depth_5m": RollingWindow(window_type="time", window_size=300),
            "aggressive_buy_vol_5m": RollingWindow(window_type="time", window_size=300),
            "aggressive_sell_vol_5m": RollingWindow(window_type="time", window_size=300),
            "trade_size_5m": RollingWindow(window_type="time", window_size=300),
            "aggression_flow_5m": RollingWindow(window_type="time", window_size=300),
            "pdr_5m": RollingWindow(window_type="time", window_size=300),
            "pdr_roc_5m": RollingWindow(window_type="time", window_size=300),
            "vsi_combined_5m": RollingWindow(window_type="time", window_size=300),
            "vsi_roc_5m": RollingWindow(window_type="time", window_size=300),
            "iex_intent_5m": RollingWindow(window_type="time", window_size=300),
            "memx_vsi_5m": RollingWindow(window_type="time", window_size=300),
            "bats_vsi_5m": RollingWindow(window_type="time", window_size=300),
            "conviction_score_5m": RollingWindow(window_type="time", window_size=300),
            "fragility_bid_5m": RollingWindow(window_type="time", window_size=300),
            "fragility_ask_5m": RollingWindow(window_type="time", window_size=300),
            "decay_velocity_bid_5m": RollingWindow(window_type="time", window_size=300),
            "decay_velocity_ask_5m": RollingWindow(window_type="time", window_size=300),
            "top_wall_bid_size_5m": RollingWindow(window_type="time", window_size=300),
            "top_wall_ask_size_5m": RollingWindow(window_type="time", window_size=300),
            "depth_bid_size_5m": RollingWindow(window_type="time", window_size=300),
            "depth_ask_size_5m": RollingWindow(window_type="time", window_size=300),
            "depth_spread_5m": RollingWindow(window_type="time", window_size=300),
            "depth_bid_levels_5m": RollingWindow(window_type="time", window_size=300),
            "depth_ask_levels_5m": RollingWindow(window_type="time", window_size=300),
            "spread_zscore_5m": RollingWindow(window_type="time", window_size=300),
            "liquidity_density_5m": RollingWindow(window_type="time", window_size=300),
            "participant_equilibrium_5m": RollingWindow(window_type="time", window_size=300),
            "volume_spike_5m": RollingWindow(window_type="time", window_size=300),
            "depth_bid_size_rolling": RollingWindow(window_type="time", window_size=60),
            "depth_ask_size_rolling": RollingWindow(window_type="time", window_size=60),
            "vamp_5m": RollingWindow(window_type="time", window_size=300),
            "vamp_mid_dev_5m": RollingWindow(window_type="time", window_size=300),
            "vamp_roc_5m": RollingWindow(window_type="time", window_size=300),
            "depth_decay_bid_5m": RollingWindow(window_type="time", window_size=300),
            "depth_decay_ask_5m": RollingWindow(window_type="time", window_size=300),
            "depth_top5_bid_5m": RollingWindow(window_type="time", window_size=300),
            "depth_top5_ask_5m": RollingWindow(window_type="time", window_size=300),
            "depth_vol_ratio_5m": RollingWindow(window_type="time", window_size=300),
            "imbalance_ratio_5m": RollingWindow(window_type="time", window_size=300),
            "imbalance_ratio_roc_5m": RollingWindow(window_type="time", window_size=300),
            "bid_participants_5m": RollingWindow(window_type="time", window_size=300),
            "ask_participants_5m": RollingWindow(window_type="time", window_size=300),
            "bid_exchanges_5m": RollingWindow(window_type="time", window_size=300),
            "ask_exchanges_5m": RollingWindow(window_type="time", window_size=300),
            "sis_bid_5m": RollingWindow(window_type="time", window_size=300),
            "sis_ask_5m": RollingWindow(window_type="time", window_size=300),
            "sis_bid_roc_5m": RollingWindow(window_type="time", window_size=300),
            "depth_bid_level_avg_5m": RollingWindow(window_type="time", window_size=300),
            "depth_ask_level_avg_5m": RollingWindow(window_type="time", window_size=300),
            "flow_ratio_5m": RollingWindow(window_type="time", window_size=300),
            "extrinsic_proxy_5m": RollingWindow(window_type="time", window_size=300),
            "extrinsic_roc_5m": RollingWindow(window_type="time", window_size=300),
            "skew_psi_5m": RollingWindow(window_type="time", window_size=900),
            "skew_psi_roc_5m": RollingWindow(window_type="time", window_size=900),
            "skew_psi_sigma_5m": RollingWindow(window_type="time", window_size=900),
            "curve_omega_5m": RollingWindow(window_type="time", window_size=900),
            "curve_omega_roc_5m": RollingWindow(window_type="time", window_size=900),
            "curve_omega_sigma_5m": RollingWindow(window_type="time", window_size=900),
            "put_slope_5m": RollingWindow(window_type="time", window_size=900),
            "call_slope_5m": RollingWindow(window_type="time", window_size=900),
            "phi_call_5m": RollingWindow(window_type="time", window_size=900),
            "phi_put_5m": RollingWindow(window_type="time", window_size=900),
            "phi_ratio_5m": RollingWindow(window_type="time", window_size=900),
            "phi_total_5m": RollingWindow(window_type="time", window_size=900),
            "phi_total_sigma_5m": RollingWindow(window_type="time", window_size=900),
            "gamma_break_index_5m": RollingWindow(window_type="time", window_size=300),
            "wall_delta_5m": RollingWindow(window_type="time", window_size=300),
            "skew_width_5m": RollingWindow(window_type="time", window_size=300),
            "otm_delta_5m": RollingWindow(window_type="time", window_size=300),
            "otm_iv_5m": RollingWindow(window_type="time", window_size=300),
            "delta_iv_corr_5m": RollingWindow(window_type="time", window_size=300),
            "iv_skew_gradient_5m": RollingWindow(window_type="time", window_size=300),
            "gamma_density_5m": RollingWindow(window_type="time", window_size=300),
            "strike_delta_5m": RollingWindow(window_type="time", window_size=300),
            "magnet_delta_5m": RollingWindow(window_type="time", window_size=300),
            "market_depth_agg": {},
            "vamp_levels": {},
        }

    @pytest.fixture
    def stream_processor(self, mock_calculator, mock_rolling_data, tmp_path):
        """Create a StreamProcessor instance for testing."""
        return StreamProcessor(
            calculator=mock_calculator,
            rolling_data=mock_rolling_data,
            exchange_bid_sizes={},
            exchange_ask_sizes={},
            phi_call_tick=0.0,
            phi_put_tick=0.0,
            call_update_count=0,
            put_update_count=0,
            data_dir=tmp_path,
            symbol="TEST",
        )

    def test_underlying_update(self, stream_processor):
        """Test processing underlying price update."""
        data = {
            "type": "underlying_update",
            "price": 100.5,
        }
        stream_processor.on_message(data)
        
        # Check that price was pushed to rolling windows
        assert stream_processor.rolling_data["price_5m"].count >= 1
        assert stream_processor.rolling_data["price_30m"].count >= 1

    def test_quote_update_aggression(self, stream_processor):
        """Test processing quote update with aggressive buy."""
        data = {
            "type": "quote_update",
            "last": 101.0,  # Must be >= ask to be aggressive buy
            "bid": 100.0,
            "ask": 101.0,
            "last_size": 100,
        }
        stream_processor.on_message(data)
        
        # Check aggressive buy volume was recorded
        assert stream_processor.rolling_data["aggressive_buy_vol_5m"].count >= 1

    def test_quote_update_aggressive_sell(self, stream_processor):
        """Test processing quote update with aggressive sell."""
        data = {
            "type": "quote_update",
            "last": 99.5,
            "bid": 100.0,
            "ask": 101.0,
            "last_size": 50,
        }
        stream_processor.on_message(data)
        
        # Check aggressive sell volume was recorded
        assert stream_processor.rolling_data["aggressive_sell_vol_5m"].count >= 1

    def test_market_depth_quotes(self, stream_processor):
        """Test processing market depth quotes."""
        data = {
            "type": "market_depth_quotes",
            "Bids": [
                {"Price": 100.0, "Size": 1000, "NumParticipants": 3, "bid_exchanges": {"MEMX": 500, "BATS": 500}},
                {"Price": 99.9, "Size": 500, "NumParticipants": 2, "bid_exchanges": {"MEMX": 500}},
            ],
            "Asks": [
                {"Price": 100.1, "Size": 800, "NumParticipants": 2, "ask_exchanges": {"MEMX": 800}},
                {"Price": 100.2, "Size": 600, "NumParticipants": 1, "ask_exchanges": {"BATS": 600}},
            ],
        }
        stream_processor.on_message(data)
        
        # Check depth metrics were updated
        assert stream_processor.rolling_data["depth_bid_size_5m"].count >= 1
        assert stream_processor.rolling_data["depth_ask_size_5m"].count >= 1
        assert stream_processor.rolling_data["depth_spread_5m"].count >= 1
