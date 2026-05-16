"""
data/stream_processor.py — Data Stream Processing

Handles all data stream processing for Syngex:
    - Message callback handler (_on_message)
    - RollingWindow updates for all metrics
    - Metrics computation (skew PSI, smile Ω, VAMP, depth decay, etc.)

This module is responsible for transforming raw market data into
rolling window metrics that strategies consume.

Functions:
    - process_underlying_update(): Handle underlying price updates
    - process_option_update(): Handle option chain updates
    - process_market_depth(): Handle L2 market depth updates
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict, Optional

from engine.gex_calculator import GEXCalculator
from strategies.rolling_window import RollingWindow

# Core rolling keys
from strategies.rolling_keys import (
    KEY_PRICE_5M,
    KEY_PRICE_30M,
    KEY_NET_GAMMA_5M,
    KEY_VOLUME_5M,
    KEY_VOLUME_DOWN_5M,
    KEY_VOLUME_UP_5M,
    KEY_TOTAL_DELTA_5M,
    KEY_WALL_DELTA_5M,
    KEY_TOTAL_GAMMA_5M,
    KEY_IV_SKEW_5M,
    KEY_ATM_DELTA_5M,
    KEY_ATM_IV_5M,
    KEY_DELTA_DENSITY_5M,
    KEY_VOLUME_ZSCORE_5M,
    KEY_ORDER_BOOK_DEPTH_5M,
    KEY_DEPTH_BID_SIZE_5M,
    KEY_DEPTH_ASK_SIZE_5M,
    KEY_DEPTH_SPREAD_5M,
    KEY_DEPTH_BID_LEVELS_5M,
    KEY_DEPTH_ASK_LEVELS_5M,
    KEY_DEPTH_BID_SIZE_ROLLING,
    KEY_DEPTH_ASK_SIZE_ROLLING,
    KEY_FLOW_RATIO_5M,
    KEY_EXTRINSIC_PROXY_5M,
    KEY_EXTRINSIC_ROC_5M,
    KEY_PROB_MOMENTUM_5M,
    KEY_SKEW_WIDTH_5M,
    KEY_IV_SKEW_GRADIENT_5M,
    KEY_GAMMA_DENSITY_5M,
    KEY_SKEW_ROC_5M,
    KEY_DELTA_ROC_5M,
    KEY_OTM_DELTA_5M,
    KEY_OTM_IV_5M,
    KEY_DELTA_IV_CORR_5M,
    KEY_CONSEC_LONG,
    KEY_CONSEC_SHORT,
    KEY_STRIKE_DELTA_5M,
    KEY_ATR_5M,
    KEY_MAGNET_DELTA_5M,
    KEY_MOMENTUM_ROC_5M,
    KEY_VAMP_5M,
    KEY_VAMP_MID_DEV_5M,
    KEY_VAMP_ROC_5M,
    KEY_VAMP_PARTICIPANTS_5M,
    KEY_VAMP_DEPTH_DENSITY_5M,
    KEY_OBI_5M,
    KEY_AGGRESSIVE_BUY_VOL_5M,
    KEY_AGGRESSIVE_SELL_VOL_5M,
    KEY_AF_5M,
    KEY_TRADE_SIZE_5M,
    KEY_PDR_5M,
    KEY_PDR_ROC_5M,
    KEY_DEPTH_DECAY_BID_5M,
    KEY_DEPTH_DECAY_ASK_5M,
    KEY_DEPTH_TOP5_BID_5M,
    KEY_DEPTH_TOP5_ASK_5M,
    KEY_DEPTH_VOL_RATIO_5M,
    KEY_IR_5M,
    KEY_IR_ROC_5M,
    KEY_IR_PARTICIPANTS_5M,
    KEY_VSI_COMBINED_5M,
    KEY_VSI_ROC_5M,
    KEY_IEX_INTENT_5M,
    KEY_BID_PARTICIPANTS_5M,
    KEY_ASK_PARTICIPANTS_5M,
    KEY_BID_EXCHANGES_5M,
    KEY_ASK_EXCHANGES_5M,
    KEY_CONVICT_SCORE_5M,
    KEY_FRAGILITY_BID_5M,
    KEY_FRAGILITY_ASK_5M,
    KEY_DECAY_VELOCITY_BID_5M,
    KEY_DECAY_VELOCITY_ASK_5M,
    KEY_TOP_WALL_BID_SIZE_5M,
    KEY_TOP_WALL_ASK_SIZE_5M,
    KEY_AGGRESSOR_VSI_5M,
    KEY_AGGRESSOR_VSI_ROC_5M,
    KEY_IEX_INTENT_SCORE_5M,
    KEY_MEMX_VSI_5M,
    KEY_BATS_VSI_5M,
    KEY_VENUE_CONCENTRATION_5M,
    KEY_ESI_MEMX_5M,
    KEY_ESI_MEMX_ROC_5M,
    KEY_ESI_BATS_5M,
    KEY_ESI_BATS_ROC_5M,
    KEY_MEMX_VOL_RATIO_5M,
    KEY_BATS_VOL_RATIO_5M,
    KEY_DEPTH_BID_LEVEL_AVG_5M,
    KEY_DEPTH_ASK_LEVEL_AVG_5M,
    KEY_SIS_BID_5M,
    KEY_SIS_ASK_5M,
    KEY_SIS_BID_ROC_5M,
    KEY_SIS_ASK_ROC_5M,
    KEY_SKEW_PSI_5M,
    KEY_SKEW_PSI_ROC_5M,
    KEY_SKEW_PSI_SIGMA_5M,
    KEY_CURVE_OMEGA_5M,
    KEY_CURVE_OMEGA_ROC_5M,
    KEY_CURVE_OMEGA_SIGMA_5M,
    KEY_PUT_SLOPE_5M,
    KEY_CALL_SLOPE_5M,
    KEY_PHI_CALL_5M,
    KEY_PHI_PUT_5M,
    KEY_PHI_RATIO_5M,
    KEY_PHI_TOTAL_5M,
    KEY_PHI_TOTAL_SIGMA_5M,
    KEY_WALL_DISTANCE_5M,
    KEY_WALL_GEX_5M,
    KEY_WALL_GEX_SIGMA_5M,
    KEY_PRICE_VELOCITY_5M,
    KEY_GAMMA_BREAK_INDEX_5M,
    KEY_CONFLUENCE_PROX_5M,
    KEY_CONFLUENCE_SIGNAL_5M,
    KEY_LIQUIDITY_WALL_SIZE_5M,
    KEY_LIQUIDITY_WALL_SIGMA_5M,
    KEY_SYNC_CORR_5M,
    KEY_SYNC_SIGMA_5M,
    KEY_SKEW_CHANGE_5M,
    KEY_VSI_MAGNITUDE_5M,
    KEY_BIGGEST_SIZE_5M,
    KEY_SMALLEST_SIZE_5M,
    KEY_CONCENTRATION_RATIO_5M,
    KEY_CONCENTRATION_SIGMA_5M,
    KEY_NUM_PARTICIPANTS_5M,
    KEY_SPREAD_ZSCORE_5M,
    KEY_LIQUIDITY_DENSITY_5M,
    KEY_PARTICIPANT_EQUILIBRIUM_5M,
    KEY_VOLUME_SPIKE_5M,
    KEY_MARKET_DEPTH_AGG,
    KEY_VAMP_LEVELS,
    MSG_TYPE_QUOTE_UPDATE,
    MSG_TYPE_OPTION_UPDATE,
    MSG_TYPE_UNDERLYING_UPDATE,
    MSG_TYPE_MARKET_DEPTH_QUOTES,
)

logger = logging.getLogger("Syngex")


def _compute_linear_slope(x_vals: list[float], y_vals: list[float]) -> float:
    """Compute slope using least-squares linear regression.
    
    Args:
        x_vals: X coordinates
        y_vals: Y coordinates
        
    Returns:
        Slope of the best-fit line, or 0.0 if insufficient data
    """
    n = len(x_vals)
    if n < 2:
        return 0.0
    x_mean = sum(x_vals) / n
    y_mean = sum(y_vals) / n
    numerator = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
    denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
    if denominator == 0:
        return 0.0
    return numerator / denominator


class StreamProcessor:
    """
    Processes market data streams and updates rolling window metrics.
    
    This class handles all the data processing logic from the original
    _on_message callback, extracting it into a maintainable module.
    
    Attributes:
        calculator: GEXCalculator for market data computations
        rolling_data: Dictionary of RollingWindow instances for metrics
        exchange_bid_sizes: Per-exchange bid size tracking
        exchange_ask_sizes: Per-exchange ask size tracking
    """

    def __init__(
        self,
        calculator: GEXCalculator,
        rolling_data: Dict[str, RollingWindow],
        exchange_bid_sizes: Dict[str, int],
        exchange_ask_sizes: Dict[str, int],
        phi_call_tick: float,
        phi_put_tick: float,
        call_update_count: int,
        put_update_count: int,
        data_dir: Any,
        symbol: str,
    ) -> None:
        """Initialize the stream processor.
        
        Args:
            calculator: GEXCalculator instance
            rolling_data: Dictionary of rolling window instances
            exchange_bid_sizes: Dict for exchange bid sizes (modified in place)
            exchange_ask_sizes: Dict for exchange ask sizes (modified in place)
            phi_call_tick: Current phi call accumulator
            phi_put_tick: Current phi put accumulator
            call_update_count: Call option update counter
            put_update_count: Put option update counter
            data_dir: Data directory path
            symbol: Trading symbol
        """
        self.calculator = calculator
        self.rolling_data = rolling_data
        self.exchange_bid_sizes = exchange_bid_sizes
        self.exchange_ask_sizes = exchange_ask_sizes
        self._phi_call_tick = phi_call_tick
        self._phi_put_tick = phi_put_tick
        self._call_update_count = call_update_count
        self._put_update_count = put_update_count
        self._data_dir = data_dir
        self._symbol = symbol
        self._phi_state_file = data_dir / f"phi_state_{symbol}.json"
        self._phi_last_write = 0.0
        self._PHI_WRITE_INTERVAL = 5.0

    def on_message(self, data: Dict[str, Any]) -> None:
        """Callback from TradeStationClient — process all message types.
        
        This is the main entry point for data processing. It routes
        messages to the appropriate handler based on message type.
        
        Args:
            data: Message data from the streaming client
        """
        try:
            self.calculator.process_message(data)
            ts = time.time()

            msg_type = data.get("type", "")

            # Route to appropriate handler
            if msg_type == MSG_TYPE_UNDERLYING_UPDATE:
                self._process_underlying_update(data, ts)
            elif msg_type == MSG_TYPE_OPTION_UPDATE:
                self._process_option_update(data, ts)
            elif msg_type in (MSG_TYPE_MARKET_DEPTH_QUOTES, KEY_MARKET_DEPTH_AGG):
                self._process_market_depth(data, ts)
            elif msg_type == MSG_TYPE_QUOTE_UPDATE:
                self._process_quote_update(data, ts)

        except Exception as exc:
            logger.error("Message processing failed (critical): %s", exc, exc_info=True)

    def _process_underlying_update(self, data: Dict[str, Any], ts: float) -> None:
        """Handle underlying price update messages.
        
        Args:
            data: Message data containing price info
            ts: Timestamp
        """
        price = data.get("price")
        if price and price > 0:
            self.rolling_data[KEY_PRICE_5M].push(price, ts)
            self.rolling_data[KEY_PRICE_30M].push(price, ts)

            # ATR: std_dev of price_5m * sqrt(5)
            if KEY_ATR_5M in self.rolling_data:
                price_vals = self.rolling_data[KEY_PRICE_5M].values
                if len(price_vals) >= 5:
                    mean_p = sum(price_vals) / len(price_vals)
                    var = sum((x - mean_p) ** 2 for x in price_vals) / len(price_vals)
                    atr = math.sqrt(var) * math.sqrt(5)
                    self.rolling_data[KEY_ATR_5M].push(atr, ts)

            # SI: delta_density
            try:
                delta_density = self.calculator.get_total_delta_activity()
                if delta_density is not None and KEY_DELTA_DENSITY_5M in self.rolling_data:
                    self.rolling_data[KEY_DELTA_DENSITY_5M].push(delta_density, ts)
            except Exception as e:
                logger.debug("Delta density tracking skipped: %s", e)

    def _process_option_update(self, data: Dict[str, Any], ts: float) -> None:
        """Handle option chain update messages.
        
        This is the most complex handler, computing all the advanced
        metrics like skew PSI, smile Ω, VAMP, etc.
        
        Args:
            data: Message data containing option info
            ts: Timestamp
        """
        # Track call/put option update counts
        side = data.get("side", "")
        if side == "call":
            self._call_update_count += 1
        elif side == "put":
            self._put_update_count += 1

        # Get greeks summary
        gex_summary = self.calculator.get_greeks_summary()
        atm_strike = self.calculator.get_atm_strike(self.calculator.underlying_price)

        # Push aggressive buy/sell volumes
        last = data.get("last", 0)
        bid = data.get("bid", 0)
        ask = data.get("ask", 0)
        last_size = data.get("last_size", 0)
        if isinstance(last_size, str):
            try:
                last_size = int(last_size)
            except (ValueError, TypeError):
                last_size = 0

        if last_size > 0:
            if last >= ask and ask > 0:
                if KEY_AGGRESSIVE_BUY_VOL_5M in self.rolling_data:
                    self.rolling_data[KEY_AGGRESSIVE_BUY_VOL_5M].push(last_size, ts)
            elif last <= bid and bid > 0:
                if KEY_AGGRESSIVE_SELL_VOL_5M in self.rolling_data:
                    self.rolling_data[KEY_AGGRESSIVE_SELL_VOL_5M].push(last_size, ts)

            if KEY_TRADE_SIZE_5M in self.rolling_data:
                self.rolling_data[KEY_TRADE_SIZE_5M].push(last_size, ts)

        # Compute Aggression Flow
        buy_vol_window = self.rolling_data.get(KEY_AGGRESSIVE_BUY_VOL_5M)
        sell_vol_window = self.rolling_data.get(KEY_AGGRESSIVE_SELL_VOL_5M)
        if buy_vol_window and sell_vol_window and buy_vol_window.count > 0 and sell_vol_window.count > 0:
            total_buy = sum(buy_vol_window.values)
            total_sell = sum(sell_vol_window.values)
            total_aggressive = total_buy + total_sell
            af = (total_buy - total_sell) / total_aggressive if total_aggressive > 0 else 0.0
        else:
            af = 0.0

        if KEY_AF_5M in self.rolling_data:
            self.rolling_data[KEY_AF_5M].push(af, ts)

        # Compute PDR (Premium Divergence Ratio)
        theoretical_value = data.get("theoretical_value", 0.0)
        mid = data.get("mid", 0.0)
        if theoretical_value and theoretical_value > 0.01:
            pdr = (mid - theoretical_value) / theoretical_value
            pdr_window = self.rolling_data.get(KEY_PDR_5M)
            if pdr_window:
                pdr_window.push(pdr, ts)

                # PDR ROC
                if pdr_window.count >= 5:
                    pdr_roc = (pdr - pdr_window.values[-5]) / abs(pdr_window.values[-5]) if abs(pdr_window.values[-5]) > 0 else 0.0
                    pdr_roc_window = self.rolling_data.get(KEY_PDR_ROC_5M)
                    if pdr_roc_window:
                        pdr_roc_window.push(pdr_roc, ts)

        # Push volume up/down proxies
        self.rolling_data[KEY_VOLUME_UP_5M].push(self._call_update_count)
        self.rolling_data[KEY_VOLUME_DOWN_5M].push(self._put_update_count)

        # Process option-specific metrics every 20 messages
        if self.calculator._msg_count % 20 == 0:
            self._process_option_metrics(data, ts, gex_summary, atm_strike)

    def _process_option_metrics(
        self,
        data: Dict[str, Any],
        ts: float,
        gex_summary: Dict[str, Any],
        atm_strike: Optional[float],
    ) -> None:
        """Process advanced option metrics.
        
        Args:
            data: Message data
            ts: Timestamp
            gex_summary: Greeks summary from calculator
            atm_strike: At-the-money strike
        """
        # Net gamma rolling window
        ng = self.calculator.get_net_gamma()
        self.rolling_data[KEY_NET_GAMMA_5M].push(ng)

        # Total delta
        call_delta = sum(d.get("call_delta_sum", 0) for d in gex_summary.values())
        put_delta = sum(d.get("put_delta_sum", 0) for d in gex_summary.values())
        net_delta = call_delta - put_delta

        # Volume z-score
        vol_window = self.rolling_data.get(KEY_VOLUME_5M)
        if vol_window and vol_window.count >= 5:
            vals = list(vol_window.values)
            mean_v = sum(vals) / len(vals)
            var_v = sum((x - mean_v) ** 2 for x in vals) / len(vals)
            std_v = math.sqrt(var_v) if var_v > 0 else 1.0
            current_vol = data.get("volume", 0)
            if isinstance(current_vol, str):
                try:
                    current_vol = int(current_vol)
                except (ValueError, TypeError):
                    current_vol = 0
            zscore = (current_vol - mean_v) / std_v if std_v > 0 else 0.0
            zscore_window = self.rolling_data.get(KEY_VOLUME_ZSCORE_5M)
            if zscore_window:
                zscore_window.push(zscore, ts)

        # Push total delta
        if KEY_TOTAL_DELTA_5M in self.rolling_data:
            self.rolling_data[KEY_TOTAL_DELTA_5M].push(net_delta)

        # Per-strike IV windows
        iv_by_strike = self.calculator.get_iv_by_strike_avg()
        for strike, avg_iv in iv_by_strike.items():
            key = f"iv_{strike}_5m"
            if key not in self.rolling_data:
                self.rolling_data[key] = RollingWindow(window_type="time", window_size=300)
            if avg_iv > 0:
                self.rolling_data[key].push(avg_iv)

        # Total gamma
        self.rolling_data[KEY_TOTAL_GAMMA_5M].push(ng)

        # IV skew
        try:
            iv_skew = self.calculator.get_iv_skew()
            if iv_skew is not None and KEY_IV_SKEW_5M in self.rolling_data:
                self.rolling_data[KEY_IV_SKEW_5M].push(iv_skew)

            # Skew ROC
            skew_window = self.rolling_data.get(KEY_IV_SKEW_5M)
            if (skew_window is not None and skew_window.count >= 2
                    and KEY_SKEW_ROC_5M in self.rolling_data):
                first_val = skew_window.values[0]
                if abs(first_val) > 0:
                    skew_roc = (iv_skew - first_val) / abs(first_val)
                    self.rolling_data[KEY_SKEW_ROC_5M].push(skew_roc)
        except Exception as e:
            logger.debug("IV skew calculation skipped: %s", e)

        # Skew PSI (Ψ) - IV Skew Dynamics
        self._compute_skew_psi(ts)

        # Smile Ω (Omega) - IV Smile Dynamics
        self._compute_smile_omega(ts, atm_strike)

        # Extrinsic proxy
        extrinsic_proxy = self._calculate_extrinsic_proxy(gex_summary)
        if extrinsic_proxy is not None:
            self.rolling_data[KEY_EXTRINSIC_PROXY_5M].push(extrinsic_proxy)

        # Extrinsic ROC
        self._compute_extrinsic_roc(ts)

        # Commit phi accumulators
        self._commit_phi_accumulators(ts)

        # Gamma Breaker
        self._compute_gamma_breaker(ts)

        # Magnet Delta
        self._compute_magnet_delta(ts, gex_summary)

        # Wall Delta (Theta Burn)
        self._compute_wall_delta(ts)

        # Skew Width (IV Band Breakout)
        self._compute_skew_width(ts, atm_strike)

        # OTM Delta/IV and Delta-IV Correlation
        self._compute_otm_metrics(ts, atm_strike)

        # Flow Ratio
        self._compute_flow_ratio(ts, gex_summary)

        # IV Skew Gradient (IV-GEX Divergence)
        self._compute_iv_skew_gradient(ts)

        # Gamma Density (IV-GEX Divergence)
        self._compute_gamma_density(ts)

        # Strike Delta
        self._compute_strike_delta(ts, gex_summary)

    def _compute_skew_psi(self, ts: float) -> None:
        """Compute Skew PSI (Ψ) - Skewness Coefficient.
        
        Ψ = (IV_Put_Wing - IV_Call_Wing) / IV_ATM
        """
        try:
            underlying_price = self.calculator.underlying_price
            iv_by_strike = self.calculator.get_iv_by_strike_avg()
            if iv_by_strike:
                strikes = sorted(iv_by_strike.keys())
                if len(strikes) >= 3:
                    atm_strike = min(strikes, key=lambda s: abs(s - underlying_price))
                    atm_iv = iv_by_strike[atm_strike]

                    call_ivs = [iv_by_strike[s] for s in strikes if s > atm_strike]
                    put_ivs = [iv_by_strike[s] for s in strikes if s < atm_strike]

                    if call_ivs and put_ivs and atm_iv > 0:
                        n_calls = max(1, len(call_ivs) // 4)
                        n_puts = max(1, len(put_ivs) // 4)
                        call_wing_iv = sum(sorted(call_ivs, reverse=True)[:n_calls]) / n_calls
                        put_wing_iv = sum(sorted(put_ivs)[:n_puts]) / n_puts

                        psi = (put_wing_iv - call_wing_iv) / atm_iv

                        psi_window = self.rolling_data.get(KEY_SKEW_PSI_5M)
                        if psi_window:
                            psi_window.push(psi, ts)

                            # Ψ ROC
                            psi_roc_window = self.rolling_data.get(KEY_SKEW_PSI_ROC_5M)
                            if psi_window and psi_roc_window and psi_window.count >= 2:
                                first_psi = psi_window.values[0]
                                if abs(first_psi) > 0.0001:
                                    psi_roc = (psi - first_psi) / abs(first_psi)
                                    psi_roc_window.push(psi_roc, ts)

                            # Ψ σ
                            psi_sigma_window = self.rolling_data.get(KEY_SKEW_PSI_SIGMA_5M)
                            if psi_window and psi_sigma_window and psi_window.count >= 5:
                                vals = list(psi_window.values)
                                mean_psi = sum(vals) / len(vals)
                                var = sum((x - mean_psi) ** 2 for x in vals) / len(vals)
                                std_psi = math.sqrt(var)
                                psi_sigma_window.push(std_psi, ts)
        except Exception as e:
            logger.debug("Skew PSI dynamics calculation skipped: %s", e)

    def _compute_smile_omega(self, ts: float, atm_strike: Optional[float]) -> None:
        """Compute Smile Ω (Omega) - Curvature Asymmetry Index.
        
        Ω = |Slope_Put_Wing| / |Slope_Call_Wing|
        """
        try:
            if atm_strike is None:
                return
                
            underlying_price = self.calculator.underlying_price
            iv_by_strike = self.calculator.get_iv_by_strike_avg()
            if iv_by_strike:
                strikes = sorted(iv_by_strike.keys())
                if len(strikes) >= 6:
                    put_strikes = [(s, iv_by_strike[s]) for s in strikes if s < atm_strike and iv_by_strike[s] > 0.01]
                    call_strikes = [(s, iv_by_strike[s]) for s in strikes if s > atm_strike and iv_by_strike[s] > 0.01]
                    
                    if len(put_strikes) >= 2 and len(call_strikes) >= 2:
                        put_x = [s / atm_strike for s, iv in put_strikes]
                        put_y = [iv for s, iv in put_strikes]
                        put_slope = _compute_linear_slope(put_x, put_y)

                        call_x = [s / atm_strike for s, iv in call_strikes]
                        call_y = [iv for s, iv in call_strikes]
                        call_slope = _compute_linear_slope(call_x, call_y)

                        if abs(call_slope) > 0.0001:
                            omega = abs(put_slope) / abs(call_slope)

                            omega_window = self.rolling_data.get(KEY_CURVE_OMEGA_5M)
                            if omega_window:
                                omega_window.push(omega, ts)

                                ps_window = self.rolling_data.get(KEY_PUT_SLOPE_5M)
                                if ps_window:
                                    ps_window.push(put_slope, ts)

                                cs_window = self.rolling_data.get(KEY_CALL_SLOPE_5M)
                                if cs_window:
                                    cs_window.push(call_slope, ts)

                                # Ω ROC
                                omega_roc_window = self.rolling_data.get(KEY_CURVE_OMEGA_ROC_5M)
                                if omega_window and omega_roc_window and omega_window.count >= 2:
                                    first_omega = omega_window.values[0]
                                    if abs(first_omega) > 0.0001:
                                        omega_roc = (omega - first_omega) / abs(first_omega)
                                        omega_roc_window.push(omega_roc, ts)

                                # Ω σ
                                omega_sigma_window = self.rolling_data.get(KEY_CURVE_OMEGA_SIGMA_5M)
                                if omega_window and omega_sigma_window and omega_window.count >= 5:
                                    vals = list(omega_window.values)
                                    mean_omega = sum(vals) / len(vals)
                                    var = sum((x - mean_omega) ** 2 for x in vals) / len(vals)
                                    std_omega = math.sqrt(var)
                                    omega_sigma_window.push(std_omega, ts)
        except Exception as e:
            logger.debug("Smile dynamics (Omega) calculation skipped: %s", e)

    def _calculate_extrinsic_proxy(self, gex_summary: Dict[str, Any]) -> Optional[float]:
        """Calculate aggregate extrinsic value proxy across all strikes.
        
        Uses abs(net_delta) * abs(net_gamma) as a proxy for extrinsic value.
        """
        try:
            total_proxy = 0.0
            strike_count = 0

            for strike_str, strike_data in gex_summary.items():
                try:
                    float(strike_str)
                except (ValueError, TypeError):
                    continue

                call_delta = strike_data.get("call_delta_sum", 0.0)
                put_delta = strike_data.get("put_delta_sum", 0.0)
                call_gamma = strike_data.get("call_gamma", 0.0)
                put_gamma = strike_data.get("put_gamma", 0.0)

                if call_delta == 0 and put_delta == 0:
                    continue

                net_delta = call_delta - put_delta
                net_gamma_val = call_gamma + put_gamma
                proxy = abs(net_delta) * abs(net_gamma_val)

                if proxy <= 0:
                    continue

                total_proxy += proxy
                strike_count += 1

            return total_proxy if strike_count >= 3 else None

        except Exception as e:
            logger.debug("Extrinsic proxy calculation skipped: %s", e)
            return None

    def _compute_extrinsic_roc(self, ts: float) -> None:
        """Compute Extrinsic ROC and acceleration."""
        try:
            ext_window = self.rolling_data.get(KEY_EXTRINSIC_PROXY_5M)
            if (ext_window is not None and ext_window.count >= 6
                    and KEY_EXTRINSIC_ROC_5M in self.rolling_data):
                vals = list(ext_window.values)
                current_ext = vals[-1]
                if len(vals) >= 6 and abs(vals[-6]) > 0:
                    ext_roc = (current_ext - vals[-6]) / abs(vals[-6])
                else:
                    ext_roc = 0.0
                if len(vals) >= 11 and abs(vals[-11]) > 0:
                    prev_roc = (vals[-6] - vals[-11]) / abs(vals[-11])
                    ext_accel = (ext_roc - prev_roc) / abs(prev_roc) if abs(prev_roc) > 0 else 0.0
                else:
                    ext_accel = 0.0
                self.rolling_data[KEY_EXTRINSIC_ROC_5M].push(ext_accel, time.time())
        except Exception as e:
            logger.debug("Extrinsic ROC calculation skipped: %s", e)

    def _commit_phi_accumulators(self, ts: float) -> None:
        """Commit per-tick phi accumulators to rolling windows."""
        if self._phi_call_tick > 0 or self._phi_put_tick > 0:
            phi_call_w = self.rolling_data.get(KEY_PHI_CALL_5M)
            if phi_call_w:
                phi_call_w.push(self._phi_call_tick, ts)
            phi_put_w = self.rolling_data.get(KEY_PHI_PUT_5M)
            if phi_put_w:
                phi_put_w.push(self._phi_put_tick, ts)
            total = self._phi_call_tick + self._phi_put_tick
            if total > 0:
                phi_total_w = self.rolling_data.get(KEY_PHI_TOTAL_5M)
                if phi_total_w:
                    phi_total_w.push(total, ts)
                phi_ratio_w = self.rolling_data.get(KEY_PHI_RATIO_5M)
                if phi_put_w and self._phi_put_tick > 0:
                    ratio = self._phi_call_tick / self._phi_put_tick
                    phi_ratio_w.push(ratio, ts)
                # Φ total σ
                phi_sig_w = self.rolling_data.get(KEY_PHI_TOTAL_SIGMA_5M)
                if phi_total_w and phi_sig_w and phi_total_w.count >= 5:
                    vals = list(phi_total_w.values)
                    mean_t = sum(vals) / len(vals)
                    var = sum((x - mean_t) ** 2 for x in vals) / len(vals)
                    phi_sig_w.push(math.sqrt(var), ts)
            # Reset per-tick accumulators
            self._phi_call_tick = 0.0
            self._phi_put_tick = 0.0
            # Persist state (crash recovery)
            self._persist_phi_accumulators()

    def _persist_phi_accumulators(self) -> None:
        """Write phi accumulators to disk for crash recovery."""
        now = time.time()
        if now - self._phi_last_write < self._PHI_WRITE_INTERVAL:
            return

        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            state = {
                "_phi_call_tick": self._phi_call_tick,
                "_phi_put_tick": self._phi_put_tick,
            }
            with open(self._phi_state_file, "w") as f:
                import json
                json.dump(state, f)
            self._phi_last_write = now
        except Exception as exc:
            logger.debug("Phi accumulator persistence failed: %s", exc)

    def _compute_gamma_breaker(self, ts: float) -> None:
        """Compute Gamma Breaker (Γ_break) - Gamma Breakout Index."""
        try:
            price = self.calculator.underlying_price
            if price > 0:
                walls = self.calculator.get_gamma_walls(threshold=100000)

                if walls:
                    nearest_wall = walls[0]
                    wall_strike = nearest_wall["strike"]
                    wall_gex = nearest_wall["gex"]

                    wall_dist_pct = abs(wall_strike - price) / price

                    all_gex = [abs(w["gex"]) for w in walls]
                    avg_gex = sum(all_gex) / len(all_gex) if all_gex else 1.0
                    gamma_concentration = abs(wall_gex) / avg_gex if avg_gex > 0 else 1.0

                    price_window = self.rolling_data.get(KEY_PRICE_5M)
                    price_velocity = 0.0
                    if price_window and price_window.count >= 5:
                        vals = list(price_window.values)
                        if len(vals) >= 5 and vals[0] > 0:
                            price_velocity = abs((vals[-1] - vals[0]) / vals[0])

                    gamma_break_index = price_velocity * gamma_concentration

                    if KEY_GAMMA_BREAK_INDEX_5M in self.rolling_data:
                        self.rolling_data[KEY_GAMMA_BREAK_INDEX_5M].push(gamma_break_index, ts)
        except Exception as e:
            logger.debug("Gamma Breaker calculation skipped: %s", e)

    def _compute_magnet_delta(self, ts: float, gex_summary: Dict[str, Any]) -> None:
        """Compute Magnet Delta ROC for Prob Weighted Magnet."""
        try:
            if not gex_summary:
                return

            price = self.calculator.underlying_price
            atm_strike = min(
                (float(s) for s in gex_summary.keys() if self._safe_float(s)),
                key=lambda s: abs(s - price),
                default=None,
            )

            if atm_strike is not None:
                magnet_strikes = [
                    atm_strike - 5, atm_strike - 2.5, atm_strike,
                    atm_strike + 2.5, atm_strike + 5
                ]

                best_strike = None
                best_oi = 0.0
                for ms in magnet_strikes:
                    sd = gex_summary.get(str(ms), {})
                    oi = sd.get("call_oi", 0) + sd.get("put_oi", 0)
                    if oi > best_oi:
                        best_oi = oi
                        best_strike = ms

                if best_strike is not None:
                    delta_data = self.calculator.get_delta_by_strike(best_strike)
                    current_delta = delta_data.get("net_delta", 0.0)
                    mag_window = self.rolling_data[KEY_MAGNET_DELTA_5M]
                    if mag_window.count >= 5:
                        delta_5_ago = mag_window.values[-5]
                        if abs(delta_5_ago) > 0:
                            delta_roc = (current_delta - delta_5_ago) / abs(delta_5_ago)
                            self.rolling_data[KEY_MAGNET_DELTA_5M].push(delta_roc, time.time())
                    else:
                        self.rolling_data[KEY_MAGNET_DELTA_5M].push(current_delta, time.time())
        except Exception as e:
            logger.debug("Prob weighted magnet (delta ROC) calculation skipped: %s", e)

    def _safe_float(self, s: str) -> bool:
        """Safely check if string can be converted to float."""
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False

    def _compute_wall_delta(self, ts: float) -> None:
        """Compute Wall Delta for Theta Burn."""
        try:
            if KEY_WALL_DELTA_5M in self.rolling_data:
                walls = self.calculator.get_gamma_walls(threshold=5000)
                if walls:
                    wall_deltas = []
                    for wall in walls:
                        try:
                            ws = wall.get("strike", 0)
                            if ws and ws > 0:
                                dd = self.calculator.get_delta_by_strike(ws)
                                nd = dd.get("net_delta", 0.0)
                                wall_deltas.append(nd)
                        except Exception:
                            pass
                    if wall_deltas:
                        avg_wall_delta = sum(wall_deltas) / len(wall_deltas)
                        self.rolling_data[KEY_WALL_DELTA_5M].push(avg_wall_delta)
        except Exception as e:
            logger.debug("Theta burn (wall delta) calculation skipped: %s", e)

    def _compute_skew_width(self, ts: float, atm_strike: Optional[float]) -> None:
        """Compute Skew Width for IV Band Breakout."""
        try:
            if atm_strike is not None and KEY_SKEW_WIDTH_5M in self.rolling_data:
                otm_put_strike = atm_strike * 0.95
                otm_call_strike = atm_strike * 1.05

                otm_put_iv = self.calculator.get_iv_by_strike(otm_put_strike)
                otm_call_iv = self.calculator.get_iv_by_strike(otm_call_strike)

                if otm_put_iv is not None and otm_put_iv > 0 and otm_call_iv is not None and otm_call_iv > 0:
                    skew_width = abs(otm_put_iv - otm_call_iv)
                    self.rolling_data[KEY_SKEW_WIDTH_5M].push(skew_width)
        except Exception as e:
            logger.debug("IV band breakout (skew width) calculation skipped: %s", e)

    def _compute_otm_metrics(self, ts: float, atm_strike: Optional[float]) -> None:
        """Compute OTM Delta, OTM IV, and Delta-IV Correlation."""
        try:
            price = self.calculator.underlying_price
            if price and price > 0 and atm_strike:
                otm_put_strike = atm_strike * 0.95
                otm_call_strike = atm_strike * 1.05

                # OTM Delta
                otm_delta = 0.0
                if otm_put_strike and otm_call_strike:
                    put_data = self.calculator.get_delta_by_strike(otm_put_strike)
                    call_data = self.calculator.get_delta_by_strike(otm_call_strike)
                    put_delta = put_data.get("net_delta", 0.0)
                    call_delta = call_data.get("net_delta", 0.0)
                    otm_delta = put_delta if abs(put_delta) >= abs(call_delta) else call_delta

                if KEY_OTM_DELTA_5M in self.rolling_data:
                    self.rolling_data[KEY_OTM_DELTA_5M].push(otm_delta)

                # OTM IV
                otm_iv = 0.0
                put_iv = self.calculator.get_iv_by_strike(otm_put_strike)
                call_iv = self.calculator.get_iv_by_strike(otm_call_strike)
                if put_iv is not None and call_iv is not None:
                    otm_iv = max(put_iv, call_iv) if put_iv > 0 and call_iv > 0 else (put_iv or call_iv or 0.0)
                elif put_iv is not None:
                    otm_iv = put_iv or 0.0
                elif call_iv is not None:
                    otm_iv = call_iv or 0.0

                if otm_iv > 0 and KEY_OTM_IV_5M in self.rolling_data:
                    self.rolling_data[KEY_OTM_IV_5M].push(otm_iv)

                # Delta-IV correlation
                if (KEY_ATM_DELTA_5M in self.rolling_data
                        and KEY_ATM_IV_5M in self.rolling_data):
                    delta_vals = self.rolling_data[KEY_ATM_DELTA_5M].values
                    iv_vals = self.rolling_data[KEY_ATM_IV_5M].values
                    n = min(len(delta_vals), len(iv_vals))
                    if n >= 10:
                        d = delta_vals[-10:]
                        v = iv_vals[-10:]
                        mean_d = sum(d) / 10.0
                        mean_v = sum(v) / 10.0
                        num = sum((di - mean_d) * (vi - mean_v) for di, vi in zip(d, v))
                        den_d = (sum((di - mean_d) ** 2 for di in d)) ** 0.5
                        den_v = (sum((vi - mean_v) ** 2 for vi in v)) ** 0.5
                        corr = num / (den_d * den_v) if den_d > 0 and den_v > 0 else 0.0
                        if KEY_DELTA_IV_CORR_5M in self.rolling_data:
                            self.rolling_data[KEY_DELTA_IV_CORR_5M].push(corr)
        except Exception as e:
            logger.debug("Delta-IV divergence calculation skipped: %s", e)

    def _compute_flow_ratio(self, ts: float, gex_summary: Dict[str, Any]) -> None:
        """Compute Call-Put Flow Ratio."""
        try:
            call_score = 0.0
            put_score = 0.0
            for strike_str, strike_data in gex_summary.items():
                call_oi = strike_data.get("call_oi", 0)
                call_gamma = strike_data.get("call_gamma", 0)
                call_delta = abs(strike_data.get("call_delta_sum", 0))
                if call_oi > 0 and call_gamma > 0 and call_delta > 0.01:
                    call_score += call_oi * call_gamma * call_delta

                put_oi = strike_data.get("put_oi", 0)
                put_gamma = strike_data.get("put_gamma", 0)
                put_delta = abs(strike_data.get("put_delta_sum", 0))
                if put_oi > 0 and put_gamma > 0 and put_delta > 0.01:
                    put_score += put_oi * put_gamma * put_delta

            if put_score > 0:
                flow_ratio = call_score / put_score
            elif call_score > 0:
                flow_ratio = float("inf")
            else:
                flow_ratio = 0.0

            if KEY_FLOW_RATIO_5M in self.rolling_data:
                self.rolling_data[KEY_FLOW_RATIO_5M].push(flow_ratio)
        except Exception as e:
            logger.debug("Call-put flow asymmetry calculation skipped: %s", e)

    def _compute_iv_skew_gradient(self, ts: float) -> None:
        """Compute IV Skew Gradient for IV-GEX Divergence."""
        try:
            atm_strike = self.calculator.get_atm_strike(self.calculator.underlying_price)
            if atm_strike is not None:
                atm_iv = self.calculator.get_iv_by_strike(atm_strike)
                if atm_iv is not None and atm_iv > 0:
                    otm_put_strike = atm_strike * 0.95
                    otm_put_iv = self.calculator.get_iv_by_strike(otm_put_strike)
                    if otm_put_iv is not None and otm_put_iv > 0:
                        iv_skew = otm_put_iv - atm_iv
                        if KEY_IV_SKEW_GRADIENT_5M in self.rolling_data:
                            self.rolling_data[KEY_IV_SKEW_GRADIENT_5M].push(iv_skew)
        except Exception as e:
            logger.debug("IV-GEX divergence (skew gradient) calculation skipped: %s", e)

    def _compute_gamma_density(self, ts: float) -> None:
        """Compute Gamma Density for IV-GEX Divergence."""
        try:
            price = self.calculator.underlying_price
            if price and price > 0:
                gamma_density = 0.0
                gex_summary = self.calculator.get_greeks_summary()
                for strike_str, strike_data in gex_summary.items():
                    try:
                        strike = float(strike_str)
                    except (ValueError, TypeError):
                        continue
                    distance = abs(strike - price) / price
                    if distance <= 0.01:  # 1% window
                        call_gamma = strike_data.get("call_gamma", 0.0)
                        put_gamma = strike_data.get("put_gamma", 0.0)
                        gamma_density += abs(call_gamma) + abs(put_gamma)
                if KEY_GAMMA_DENSITY_5M in self.rolling_data:
                    self.rolling_data[KEY_GAMMA_DENSITY_5M].push(gamma_density)
        except Exception as e:
            logger.debug("IV-GEX divergence (gamma density) calculation skipped: %s", e)

    def _compute_strike_delta(self, ts: float, gex_summary: Dict[str, Any]) -> None:
        """Compute Strike Delta for Strike Concentration."""
        try:
            if KEY_STRIKE_DELTA_5M in self.rolling_data and gex_summary:
                strike_oi_list = []
                for strike_str, strike_data in gex_summary.items():
                    try:
                        strike = float(strike_str)
                    except (ValueError, TypeError):
                        continue
                    call_oi = strike_data.get("call_oi", 0) or 0
                    put_oi = strike_data.get("put_oi", 0) or 0
                    total_oi = call_oi + put_oi
                    if total_oi > 0:
                        strike_oi_list.append((strike, total_oi))
                strike_oi_list.sort(key=lambda x: x[1], reverse=True)
                top_strikes = strike_oi_list[:3]

                total_net_delta = 0.0
                for strike, _ in top_strikes:
                    delta_data = self.calculator.get_delta_by_strike(strike)
                    total_net_delta += delta_data.get("net_delta", 0.0)
                self.rolling_data[KEY_STRIKE_DELTA_5M].push(total_net_delta)
        except Exception as e:
            logger.debug("Strike concentration (delta) calculation skipped: %s", e)

    def _process_market_depth(self, data: Dict[str, Any], ts: float) -> None:
        """Handle market depth (L2) update messages.
        
        Args:
            data: Message data containing depth info
            ts: Timestamp
        """
        bids = data.get("Bids", [])
        asks = data.get("Asks", [])

        msg_type = data.get("type", "")

        # Aggregate size from all bid/ask levels
        if msg_type == MSG_TYPE_MARKET_DEPTH_QUOTES:
            total_bid_size = sum(int(b.get("Size", 0)) for b in bids)
            total_ask_size = sum(int(a.get("Size", 0)) for a in asks)
        else:
            total_bid_size = sum(int(b.get("TotalSize", 0)) for b in bids)
            total_ask_size = sum(int(a.get("TotalSize", 0)) for a in asks)

        # SI: order_book_depth
        if KEY_ORDER_BOOK_DEPTH_5M in self.rolling_data:
            self.rolling_data[KEY_ORDER_BOOK_DEPTH_5M].push(
                total_bid_size + total_ask_size, ts
            )

        # Exchange Flow Concentration (quotes only)
        if msg_type == MSG_TYPE_MARKET_DEPTH_QUOTES:
            exchange_bid_sizes: Dict[str, int] = {}
            exchange_ask_sizes: Dict[str, int] = {}
            for b in bids:
                for venue, size_str in b.get("bid_exchanges", {}).items():
                    exchange_bid_sizes[venue] = exchange_bid_sizes.get(venue, 0) + int(size_str)
            for a in asks:
                for venue, size_str in a.get("ask_exchanges", {}).items():
                    exchange_ask_sizes[venue] = exchange_ask_sizes.get(venue, 0) + int(size_str)
            
            self.exchange_bid_sizes.update(exchange_bid_sizes)
            self.exchange_ask_sizes.update(exchange_ask_sizes)

            memx_bid = exchange_bid_sizes.get("MEMX", 0)
            memx_ask = exchange_ask_sizes.get("MEMX", 0)
            bats_bid = exchange_bid_sizes.get("BATS", 0)
            bats_ask = exchange_ask_sizes.get("BATS", 0)
            iex_bid = exchange_bid_sizes.get("IEX", 0)
            iex_ask = exchange_ask_sizes.get("IEX", 0)

            memx_vsi = memx_bid / memx_ask if memx_ask > 0 else 999.0
            bats_vsi = bats_bid / bats_ask if bats_ask > 0 else 999.0
            vsi_combined = max(memx_vsi, bats_vsi)

            total_depth = total_bid_size + total_ask_size
            iex_total = iex_bid + iex_ask
            iex_intent = iex_total / total_depth if total_depth > 0 else 0.0

            vsi_window = self.rolling_data.get(KEY_VSI_COMBINED_5M)
            vsi_roc = 0.0
            if vsi_window and vsi_window.count >= 5:
                past_vsi = vsi_window.values[-5]
                if past_vsi > 0:
                    vsi_roc = (vsi_combined - past_vsi) / past_vsi

            if KEY_VSI_COMBINED_5M in self.rolling_data:
                self.rolling_data[KEY_VSI_COMBINED_5M].push(vsi_combined, ts)
            if KEY_VSI_ROC_5M in self.rolling_data:
                self.rolling_data[KEY_VSI_ROC_5M].push(vsi_roc, ts)
            if KEY_IEX_INTENT_5M in self.rolling_data:
                self.rolling_data[KEY_IEX_INTENT_5M].push(iex_intent, ts)
            if KEY_MEMX_VSI_5M in self.rolling_data:
                self.rolling_data[KEY_MEMX_VSI_5M].push(memx_vsi, ts)
            if KEY_BATS_VSI_5M in self.rolling_data:
                self.rolling_data[KEY_BATS_VSI_5M].push(bats_vsi, ts)

        # Participant Diversity Conviction
        if bids and asks:
            max_participants = 50
            max_exchanges = 10

            avg_bid_participants = sum(int(b.get("NumParticipants", 1)) for b in bids) / len(bids)
            avg_ask_participants = sum(int(a.get("NumParticipants", 1)) for a in asks) / len(asks)

            top_bid_exchanges = max(len(b.get("bid_exchanges", {})) for b in bids) if bids else 0
            top_ask_exchanges = max(len(a.get("ask_exchanges", {})) for a in asks) if asks else 0

            bid_participant_score = min(1.0, avg_bid_participants / max_participants)
            bid_exchange_score = min(1.0, top_bid_exchanges / max_exchanges)
            bid_conviction_score = bid_participant_score * bid_exchange_score
            
            ask_participant_score = min(1.0, avg_ask_participants / max_participants)
            ask_exchange_score = min(1.0, top_ask_exchanges / max_exchanges)
            ask_conviction_score = ask_participant_score * ask_exchange_score
            
            avg_conviction_score = (bid_conviction_score + ask_conviction_score) / 2.0

            if KEY_CONVICT_SCORE_5M in self.rolling_data:
                self.rolling_data[KEY_CONVICT_SCORE_5M].push(avg_conviction_score, ts)

            # Participant Divergence Scalper: fragility + decay velocity
            def _compute_fragility(levels, side_key):
                if not levels:
                    return 0.0
                fragilities = []
                for lvl in levels[:5]:
                    n_part = max(1, int(lvl.get("NumParticipants", 0)))
                    exchanges = lvl.get(side_key, {})
                    n_exch = max(1, len(exchanges)) if exchanges else 1
                    fragilities.append(1.0 / (n_part * n_exch))
                return sum(fragilities) / len(fragilities)

            frag_bid = _compute_fragility(bids, "bid_exchanges")
            frag_ask = _compute_fragility(asks, "ask_exchanges")

            top_bid_level = max(bids, key=lambda b: int(b.get("Size", 0)), default=None)
            top_ask_level = max(asks, key=lambda a: int(a.get("Size", 0)), default=None)
            top_bid_wall_size = int(top_bid_level.get("Size", 0)) if top_bid_level else 0
            top_ask_wall_size = int(top_ask_level.get("Size", 0)) if top_ask_level else 0

            bid_decay = 0.0
            ask_decay = 0.0
            bid_wall_rw = self.rolling_data.get(KEY_TOP_WALL_BID_SIZE_5M)
            ask_wall_rw = self.rolling_data.get(KEY_TOP_WALL_ASK_SIZE_5M)
            if bid_wall_rw and bid_wall_rw.count >= 5 and top_bid_wall_size > 0:
                past = bid_wall_rw.values[-5] if bid_wall_rw.values[-5] > 0 else 1
                bid_decay = (top_bid_wall_size - past) / past
            if ask_wall_rw and ask_wall_rw.count >= 5 and top_ask_wall_size > 0:
                past = ask_wall_rw.values[-5] if ask_wall_rw.values[-5] > 0 else 1
                ask_decay = (top_ask_wall_size - past) / past

            if KEY_FRAGILITY_BID_5M in self.rolling_data:
                self.rolling_data[KEY_FRAGILITY_BID_5M].push(frag_bid, ts)
            if KEY_FRAGILITY_ASK_5M in self.rolling_data:
                self.rolling_data[KEY_FRAGILITY_ASK_5M].push(frag_ask, ts)
            if KEY_DECAY_VELOCITY_BID_5M in self.rolling_data:
                self.rolling_data[KEY_DECAY_VELOCITY_BID_5M].push(bid_decay, ts)
            if KEY_DECAY_VELOCITY_ASK_5M in self.rolling_data:
                self.rolling_data[KEY_DECAY_VELOCITY_ASK_5M].push(ask_decay, ts)
            if KEY_TOP_WALL_BID_SIZE_5M in self.rolling_data:
                self.rolling_data[KEY_TOP_WALL_BID_SIZE_5M].push(top_bid_wall_size, ts)
            if KEY_TOP_WALL_ASK_SIZE_5M in self.rolling_data:
                self.rolling_data[KEY_TOP_WALL_ASK_SIZE_5M].push(top_ask_wall_size, ts)

        # Depth metrics
        best_bid = float(bids[0].get("Price", 0)) if bids else 0.0
        best_ask = float(asks[0].get("Price", 0)) if asks else 0.0
        spread = best_ask - best_bid if best_bid > 0 and best_ask > 0 else 0.0

        if KEY_DEPTH_BID_SIZE_5M in self.rolling_data:
            self.rolling_data[KEY_DEPTH_BID_SIZE_5M].push(total_bid_size, ts)
        if KEY_DEPTH_ASK_SIZE_5M in self.rolling_data:
            self.rolling_data[KEY_DEPTH_ASK_SIZE_5M].push(total_ask_size, ts)
        if KEY_DEPTH_SPREAD_5M in self.rolling_data:
            self.rolling_data[KEY_DEPTH_SPREAD_5M].push(spread, ts)
        if KEY_DEPTH_BID_LEVELS_5M in self.rolling_data:
            self.rolling_data[KEY_DEPTH_BID_LEVELS_5M].push(len(bids), ts)
        if KEY_DEPTH_ASK_LEVELS_5M in self.rolling_data:
            self.rolling_data[KEY_DEPTH_ASK_LEVELS_5M].push(len(asks), ts)

        # Vortex Compression metrics
        if KEY_SPREAD_ZSCORE_5M in self.rolling_data:
            spread_window = self.rolling_data.get(KEY_DEPTH_SPREAD_5M)
            if spread_window and spread_window.count >= 10:
                mean_spread = spread_window.mean
                std_spread = spread_window.std
                current_spread = spread_window.latest
                if std_spread is not None and std_spread > 0 and mean_spread is not None and current_spread is not None:
                    spread_z = (current_spread - mean_spread) / std_spread
                else:
                    spread_z = 0.0
                self.rolling_data[KEY_SPREAD_ZSCORE_5M].push(spread_z, ts)

        if spread > 0:
            liquidity_density = (total_bid_size + total_ask_size) / spread
            if KEY_LIQUIDITY_DENSITY_5M in self.rolling_data:
                self.rolling_data[KEY_LIQUIDITY_DENSITY_5M].push(liquidity_density, ts)

        bid_avg_p = data.get("bid_avg_participants", 0)
        ask_avg_p = data.get("ask_avg_participants", 0)
        if ask_avg_p > 0:
            participant_equil = bid_avg_p / ask_avg_p
        else:
            participant_equil = 1.0
        if KEY_PARTICIPANT_EQUILIBRIUM_5M in self.rolling_data:
            self.rolling_data[KEY_PARTICIPANT_EQUILIBRIUM_5M].push(participant_equil, ts)

        volume_window = self.rolling_data.get(KEY_VOLUME_5M)
        if volume_window and volume_window.count > 0 and volume_window.mean and volume_window.mean > 0:
            current_vol = volume_window.latest if volume_window.latest else 0
            volume_spike = current_vol / volume_window.mean if current_vol > 0 else 0.0
        else:
            volume_spike = 1.0
        if KEY_VOLUME_SPIKE_5M in self.rolling_data:
            self.rolling_data[KEY_VOLUME_SPIKE_5M].push(volume_spike, ts)

        if KEY_DEPTH_BID_SIZE_ROLLING in self.rolling_data:
            self.rolling_data[KEY_DEPTH_BID_SIZE_ROLLING].push(total_bid_size, ts)
        if KEY_DEPTH_ASK_SIZE_ROLLING in self.rolling_data:
            self.rolling_data[KEY_DEPTH_ASK_SIZE_ROLLING].push(total_ask_size, ts)

        # Store raw depth levels for StrikeConcentration v2
        if msg_type == KEY_MARKET_DEPTH_AGG:
            bid_levels = [{"price": float(b.get("Price", 0)), "size": int(b.get("TotalSize", 0))} for b in bids]
            ask_levels = [{"price": float(a.get("Price", 0)), "size": int(a.get("TotalSize", 0))} for a in asks]
            self.rolling_data[KEY_MARKET_DEPTH_AGG] = {
                "bid_levels": bid_levels,
                "ask_levels": ask_levels,
            }

            # VAMP Momentum
            N_TOP_LEVELS = 10
            bid_levels_full = [
                {"price": float(b.get("Price", 0)), "size": int(b.get("TotalSize", 0)),
                 "participants": int(b.get("NumParticipants", 1))}
                for b in bids[:N_TOP_LEVELS]
            ]
            ask_levels_full = [
                {"price": float(a.get("Price", 0)), "size": int(a.get("TotalSize", 0)),
                 "participants": int(a.get("NumParticipants", 1))}
                for a in asks[:N_TOP_LEVELS]
            ]
            self.rolling_data[KEY_VAMP_LEVELS] = {
                "bid_levels": bid_levels_full,
                "ask_levels": ask_levels_full,
                "mid_price": data.get("mid_price", 0),
                "spread": spread,
                "bid_avg_participants": data.get("bid_avg_participants", 0),
                "ask_avg_participants": data.get("ask_avg_participants", 0),
            }

            bid_weighted = sum(l["price"] * l["size"] for l in bid_levels_full)
            bid_total = sum(l["size"] for l in bid_levels_full)
            ask_weighted = sum(l["price"] * l["size"] for l in ask_levels_full)
            ask_total = sum(l["size"] for l in ask_levels_full)
            total_weighted = bid_weighted + ask_weighted
            total_size = bid_total + ask_total
            mid_price = data.get("mid_price", 0)

            if total_size > 0 and mid_price > 0:
                vamp = total_weighted / total_size
                vamp_mid_dev = (vamp - mid_price) / mid_price
            else:
                vamp = mid_price
                vamp_mid_dev = 0

            if KEY_VAMP_5M in self.rolling_data:
                self.rolling_data[KEY_VAMP_5M].push(vamp, ts)
                vamp_history = self.rolling_data[KEY_VAMP_5M]
                if vamp_history.count >= 5:
                    past_vamp = vamp_history.values[-5]
                    vamp_roc = (vamp - past_vamp) / past_vamp if past_vamp != 0 else 0
                else:
                    vamp_roc = 0
            if KEY_VAMP_MID_DEV_5M in self.rolling_data:
                self.rolling_data[KEY_VAMP_MID_DEV_5M].push(vamp_mid_dev, ts)
            if KEY_VAMP_ROC_5M in self.rolling_data:
                self.rolling_data[KEY_VAMP_ROC_5M].push(vamp_roc, ts)

            # Depth Decay Momentum
            bid_size_window = self.rolling_data.get(KEY_DEPTH_BID_SIZE_5M)
            ask_size_window = self.rolling_data.get(KEY_DEPTH_ASK_SIZE_5M)

            bid_depth_roc = 0.0
            ask_depth_roc = 0.0

            if bid_size_window and bid_size_window.count >= 5:
                old_bid = bid_size_window.values[-5]
                if old_bid > 0:
                    bid_depth_roc = (total_bid_size - old_bid) / old_bid
            if ask_size_window and ask_size_window.count >= 5:
                old_ask = ask_size_window.values[-5]
                if old_ask > 0:
                    ask_depth_roc = (total_ask_size - old_ask) / old_ask

            if KEY_DEPTH_DECAY_BID_5M in self.rolling_data:
                self.rolling_data[KEY_DEPTH_DECAY_BID_5M].push(bid_depth_roc, ts)
            if KEY_DEPTH_DECAY_ASK_5M in self.rolling_data:
                self.rolling_data[KEY_DEPTH_DECAY_ASK_5M].push(ask_depth_roc, ts)

            # Top 5 depth
            top5_bid_size = sum(int(b.get("Size", 0)) for b in bids[:5])
            top5_ask_size = sum(int(a.get("Size", 0)) for a in asks[:5])
            if KEY_DEPTH_TOP5_BID_5M in self.rolling_data:
                self.rolling_data[KEY_DEPTH_TOP5_BID_5M].push(top5_bid_size, ts)
            if KEY_DEPTH_TOP5_ASK_5M in self.rolling_data:
                self.rolling_data[KEY_DEPTH_TOP5_ASK_5M].push(top5_ask_size, ts)

            # Depth Volume Ratio
            if total_bid_size > 0 and total_ask_size > 0:
                depth_vol_ratio = top5_bid_size / top5_ask_size if top5_ask_size > 0 else 0.0
                if KEY_DEPTH_VOL_RATIO_5M in self.rolling_data:
                    self.rolling_data[KEY_DEPTH_VOL_RATIO_5M].push(depth_vol_ratio, ts)

            # Imbalance Ratio
            if total_bid_size + total_ask_size > 0:
                ir = (total_bid_size - total_ask_size) / (total_bid_size + total_ask_size)
                if KEY_IR_5M in self.rolling_data:
                    self.rolling_data[KEY_IR_5M].push(ir, ts)
                    
                    if KEY_IR_ROC_5M in self.rolling_data:
                        ir_window = self.rolling_data[KEY_IR_5M]
                        if ir_window.count >= 5:
                            ir_roc = (ir - ir_window.values[-5]) / abs(ir_window.values[-5]) if abs(ir_window.values[-5]) > 0 else 0.0
                            self.rolling_data[KEY_IR_ROC_5M].push(ir_roc, ts)

            # Participant counts
            total_bid_participants = sum(int(b.get("NumParticipants", 1)) for b in bids)
            total_ask_participants = sum(int(a.get("NumParticipants", 1)) for a in asks)
            if KEY_BID_PARTICIPANTS_5M in self.rolling_data:
                self.rolling_data[KEY_BID_PARTICIPANTS_5M].push(total_bid_participants, ts)
            if KEY_ASK_PARTICIPANTS_5M in self.rolling_data:
                self.rolling_data[KEY_ASK_PARTICIPANTS_5M].push(total_ask_participants, ts)

            # Exchange counts
            unique_bid_exchanges = set()
            unique_ask_exchanges = set()
            for b in bids:
                unique_bid_exchanges.update(b.get("bid_exchanges", {}).keys())
            for a in asks:
                unique_ask_exchanges.update(a.get("ask_exchanges", {}).keys())
            if KEY_BID_EXCHANGES_5M in self.rolling_data:
                self.rolling_data[KEY_BID_EXCHANGES_5M].push(len(unique_bid_exchanges), ts)
            if KEY_ASK_EXCHANGES_5M in self.rolling_data:
                self.rolling_data[KEY_ASK_EXCHANGES_5M].push(len(unique_ask_exchanges), ts)

            # SIS (Size Imbalance Score)
            if total_bid_size + total_ask_size > 0:
                sis_bid = total_bid_size / (total_bid_size + total_ask_size)
                sis_ask = total_ask_size / (total_bid_size + total_ask_size)
                if KEY_SIS_BID_5M in self.rolling_data:
                    self.rolling_data[KEY_SIS_BID_5M].push(sis_bid, ts)
                if KEY_SIS_ASK_5M in self.rolling_data:
                    self.rolling_data[KEY_SIS_ASK_5M].push(sis_ask, ts)

                    if KEY_SIS_BID_ROC_5M in self.rolling_data:
                        sis_window = self.rolling_data[KEY_SIS_BID_5M]
                        if sis_window.count >= 5:
                            sis_roc = (sis_bid - sis_window.values[-5]) / abs(sis_window.values[-5]) if abs(sis_window.values[-5]) > 0 else 0.0
                            self.rolling_data[KEY_SIS_BID_ROC_5M].push(sis_roc, ts)

            # Depth level averages
            if bids:
                avg_bid_level = sum(float(b.get("Price", 0)) for b in bids) / len(bids)
                if KEY_DEPTH_BID_LEVEL_AVG_5M in self.rolling_data:
                    self.rolling_data[KEY_DEPTH_BID_LEVEL_AVG_5M].push(avg_bid_level, ts)
            if asks:
                avg_ask_level = sum(float(a.get("Price", 0)) for a in asks) / len(asks)
                if KEY_DEPTH_ASK_LEVEL_AVG_5M in self.rolling_data:
                    self.rolling_data[KEY_DEPTH_ASK_LEVEL_AVG_5M].push(avg_ask_level, ts)

    def _process_quote_update(self, data: Dict[str, Any], ts: float) -> None:
        """Handle quote update messages.
        
        Args:
            data: Message data containing quote info
            ts: Timestamp
        """
        # Aggression detection from quotes
        last = data.get("last", 0)
        bid = data.get("bid", 0)
        ask = data.get("ask", 0)
        last_size = data.get("last_size", 0)
        if isinstance(last_size, str):
            try:
                last_size = int(last_size)
            except (ValueError, TypeError):
                last_size = 0

        if last_size > 0:
            if last >= ask and ask > 0:
                if KEY_AGGRESSIVE_BUY_VOL_5M in self.rolling_data:
                    self.rolling_data[KEY_AGGRESSIVE_BUY_VOL_5M].push(last_size, ts)
            elif last <= bid and bid > 0:
                if KEY_AGGRESSIVE_SELL_VOL_5M in self.rolling_data:
                    self.rolling_data[KEY_AGGRESSIVE_SELL_VOL_5M].push(last_size, ts)

            if KEY_TRADE_SIZE_5M in self.rolling_data:
                self.rolling_data[KEY_TRADE_SIZE_5M].push(last_size, ts)

        # Compute AF from rolling aggressive volumes
        buy_vol_window = self.rolling_data.get(KEY_AGGRESSIVE_BUY_VOL_5M)
        sell_vol_window = self.rolling_data.get(KEY_AGGRESSIVE_SELL_VOL_5M)
        if buy_vol_window and sell_vol_window and buy_vol_window.count > 0 and sell_vol_window.count > 0:
            total_buy = sum(buy_vol_window.values)
            total_sell = sum(sell_vol_window.values)
            total_aggressive = total_buy + total_sell
            af = (total_buy - total_sell) / total_aggressive if total_aggressive > 0 else 0.0
        else:
            af = 0.0

        if KEY_AF_5M in self.rolling_data:
            self.rolling_data[KEY_AF_5M].push(af, ts)
