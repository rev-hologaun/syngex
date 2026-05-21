// Syngex Ultimate Control Center - Sample Data

const syngexData = {
    symbol: "TSLA",
    price: 418.57,
    netGamma: 7,
    activeStrikes: 32,
    strategyCount: 41,
    
    dominantLevels: [
        { 
            type: "PUT_WALL", 
            label: "PUT Wall",
            strike: 420, 
            gex: -25, 
            change: "+1.43 (0.34%)",
            changeValue: 1.43,
            className: "put-wall"
        },
        { 
            type: "CALL_WALL", 
            label: "CALL Wall",
            strike: 430, 
            gex: 45, 
            change: "+2.12 (0.41%)",
            changeValue: 2.12,
            className: "call-wall"
        },
        { 
            type: "MAGNET", 
            label: "Magnet",
            strike: 415, 
            gex: -12, 
            change: "-0.89 (0.21%)",
            changeValue: -0.89,
            className: "magnet"
        },
        { 
            type: "GEX_ZERO", 
            label: "GEX Zero",
            strike: 417.25, 
            gex: 0, 
            change: "Flip Point",
            changeValue: 0,
            className: "magnet"
        }
    ],
    
    // Extended heatmap strikes (all strikes with GEX)
    heatmapStrikes: [
        { strike: 410, gex: -8, type: "neutral" },
        { strike: 412, gex: -15, type: "put-wall" },
        { strike: 414, gex: -22, type: "put-wall" },
        { strike: 415, gex: -12, type: "magnet" },
        { strike: 416, gex: -5, type: "neutral" },
        { strike: 417, gex: 3, type: "neutral" },
        { strike: 418, gex: 12, type: "neutral" },
        { strike: 419, gex: 18, type: "neutral" },
        { strike: 420, gex: -25, type: "put-wall" },
        { strike: 421, gex: 8, type: "neutral" },
        { strike: 422, gex: 15, type: "neutral" },
        { strike: 423, gex: 22, type: "neutral" },
        { strike: 424, gex: 19, type: "neutral" },
        { strike: 425, gex: 28, type: "neutral" },
        { strike: 426, gex: 35, type: "neutral" },
        { strike: 427, gex: 41, type: "neutral" },
        { strike: 428, gex: 38, type: "neutral" },
        { strike: 429, gex: 43, type: "neutral" },
        { strike: 430, gex: 45, type: "call-wall" },
        { strike: 432, gex: 32, type: "neutral" },
        { strike: 434, gex: 25, type: "neutral" },
        { strike: 436, gex: 18, type: "neutral" },
        { strike: 438, gex: 12, type: "neutral" },
        { strike: 440, gex: 8, type: "neutral" }
    ],
    
    riskMetrics: {
        var1d: "2.3%",
        maxDrawdown: "8.1%",
        sharpe: 1.42,
        exposure: "POS",
        exposureFull: "Positive Gamma",
        // Extended metrics
        ohlc: { open: 415.20, high: 422.50, low: 414.80, close: 418.57 },
        volume: "2.4M",
        volumeChange: "+15%",
        delta: 1240,
        gamma: 7,
        theta: -340,
        vega: 890,
        openInterest: "32 strikes"
    },
    
    activePositions: [], // Removed - tracked in strategy boxes
    
    strategyGrid: [
        { name: "GEX_WALL", direction: "SELL", confidence: 31, entry: 418.57, stop: 421.68, target: 413.90, pnl: -705597, time: "10:55", active: true, layer: "L3" },
        { name: "MAGNET", direction: "BUY", confidence: 69, entry: 422.24, stop: 425.00, target: 430.00, pnl: -437029, time: "16:33", active: true, layer: "L2" },
        { name: "FLIP_BREAKOUT", direction: "BUY", confidence: 100, entry: 422.63, stop: 420.00, target: 425.00, pnl: 2413, time: "13:35", active: true, layer: "L1" },
        { name: "GAMMA_SQ", direction: "BUY", confidence: 65, entry: 427.71, stop: 430.00, target: 426.22, pnl: -1536, time: "11:18", active: true, layer: "L2" },
        { name: "OI_SPIKE", direction: "SELL", confidence: 45, entry: 425.00, stop: 427.00, target: 420.00, pnl: -12450, time: "10:22", active: true, layer: "L3" },
        { name: "VOLUME_WALL", direction: "BUY", confidence: 78, entry: 417.50, stop: 415.00, target: 422.00, pnl: 8920, time: "14:15", active: true, layer: "L1" },
        { name: "GEX_IMBAL", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L3" },
        { name: "IV_CRUSH", direction: "SELL", confidence: 55, entry: 420.00, stop: 423.00, target: 415.00, pnl: -3240, time: "15:45", active: true, layer: "L2" },
        { name: "GAMMA_FLIP", direction: "BUY", confidence: 91, entry: 417.25, stop: 415.00, target: 420.00, pnl: 4520, time: "11:00", active: true, layer: "L1" },
        { name: "DELTA_HEDGE", direction: "SELL", confidence: 38, entry: 421.00, stop: 424.00, target: 418.00, pnl: -890, time: "16:00", active: true, layer: "L3" },
        { name: "PIN_RISK", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L2" },
        { name: "WALL_BOUNCE", direction: "BUY", confidence: 73, entry: 415.00, stop: 412.00, target: 419.00, pnl: 6780, time: "10:45", active: true, layer: "L1" },
        { name: "GEX_MOMENTUM", direction: "BUY", confidence: 88, entry: 418.00, stop: 416.00, target: 425.00, pnl: 12340, time: "09:15", active: true, layer: "L2" },
        { name: "STOP_HUNT", direction: "SELL", confidence: 51, entry: 423.00, stop: 426.00, target: 417.00, pnl: -2100, time: "14:30", active: true, layer: "L3" },
        { name: "LIQUIDITY_SWEEP", direction: "BUY", confidence: 67, entry: 416.50, stop: 414.00, target: 421.00, pnl: 4560, time: "13:00", active: true, layer: "L1" },
        { name: "VWAP_REVERSION", direction: "SELL", confidence: 44, entry: 420.50, stop: 423.00, target: 418.00, pnl: -1890, time: "15:20", active: true, layer: "L2" },
        { name: "FLOW_SURGE", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L3" },
        { name: "GAMMA_EXPOSURE", direction: "SELL", confidence: 29, entry: 422.00, stop: 425.00, target: 419.00, pnl: -5670, time: "16:15", active: true, layer: "L1" },
        { name: "MEAN_REVERSION", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L2" },
        { name: "BREAKOUT_CONFIRM", direction: "BUY", confidence: 85, entry: 421.50, stop: 419.00, target: 428.00, pnl: 14560, time: "14:00", active: true, layer: "L3" },
        { name: "SUPPORT_TEST", direction: "BUY", confidence: 62, entry: 416.00, stop: 413.00, target: 420.00, pnl: 3450, time: "12:30", active: true, layer: "L1" },
        { name: "RESISTANCE_TEST", direction: "SELL", confidence: 58, entry: 423.50, stop: 426.00, target: 419.00, pnl: -2780, time: "15:00", active: true, layer: "L2" },
        { name: "OPTION_FLOW", direction: "BUY", confidence: 81, entry: 418.75, stop: 416.00, target: 423.00, pnl: 11230, time: "10:30", active: true, layer: "L3" },
        { name: "GEX_DIVERGENCE", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L1" },
        { name: "STRIKE_CONC", direction: "SELL", confidence: 58, entry: 428.18, stop: 431.29, target: 424.75, pnl: 83067, time: "11:28", active: true, layer: "L3" },
        { name: "VOL_SPIKE", direction: "BUY", confidence: 72, entry: 417.00, stop: 414.50, target: 422.50, pnl: 9850, time: "09:55", active: true, layer: "L2" },
        { name: "GEX_CLAMP", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L3" },
        { name: "DELTA_SKEW", direction: "SELL", confidence: 41, entry: 424.00, stop: 427.00, target: 420.00, pnl: -4320, time: "14:45", active: true, layer: "L1" },
        { name: "GAMMA_SLOPE", direction: "BUY", confidence: 66, entry: 419.50, stop: 417.00, target: 424.00, pnl: 7650, time: "12:15", active: true, layer: "L2" },
        { name: "FLOW_IMBAL", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L3" },
        { name: "OI_CONCENT", direction: "SELL", confidence: 53, entry: 421.50, stop: 424.50, target: 418.00, pnl: -3890, time: "15:30", active: true, layer: "L1" },
        { name: "WALL_BREAK", direction: "BUY", confidence: 79, entry: 420.00, stop: 417.50, target: 426.00, pnl: 18920, time: "10:10", active: true, layer: "L2" },
        { name: "GEX_REVERSAL", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L3" },
        { name: "THETA_DECAY", direction: "SELL", confidence: 47, entry: 422.50, stop: 425.50, target: 419.00, pnl: -2560, time: "16:20", active: true, layer: "L1" },
        { name: "VEGA_EXPAND", direction: "BUY", confidence: 61, entry: 418.25, stop: 415.50, target: 423.50, pnl: 5890, time: "11:40", active: true, layer: "L2" },
        { name: "LIQUIDITY_POOL", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L3" },
        { name: "STOP_CLUSTER", direction: "SELL", confidence: 36, entry: 423.75, stop: 426.50, target: 420.00, pnl: -1780, time: "14:50", active: true, layer: "L1" },
        { name: "GEX_ACCEL", direction: "BUY", confidence: 84, entry: 417.75, stop: 415.25, target: 422.00, pnl: 13450, time: "09:30", active: true, layer: "L2" },
        { name: "FLOW_WAVE", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L3" },
        { name: "GAMMA_RAIL", direction: "SELL", confidence: 49, entry: 421.25, stop: 424.25, target: 418.50, pnl: -3120, time: "15:55", active: true, layer: "L1" },
        { name: "VOL_MEAN", direction: "BUY", confidence: 68, entry: 416.75, stop: 414.00, target: 421.00, pnl: 8340, time: "12:45", active: true, layer: "L2" },
        { name: "PIN_ZONE", direction: null, confidence: 0, entry: null, stop: null, target: null, pnl: 0, time: "–", active: false, layer: "L3" }
    ],
    
    logs: [
        { type: "SIGNAL", msg: "gamma_wall_bounce SHORT conf:0.653 $418.57", timestamp: "10:28:45" },
        { type: "ALERT", msg: "Price突破 $420.00 — PUT Wall resistance", timestamp: "10:27:32" },
        { type: "GEX", msg: "Net gamma shifted POS → NEG at $417.25", timestamp: "10:26:18" },
        { type: "FLOW", msg: "Unusual call volume @ $430 exp 05/24", timestamp: "10:25:55" },
        { type: "SIGNAL", msg: "flip_breakout LONG conf:0.821 $422.63", timestamp: "10:24:12" },
        { type: "ALERT", msg: "Volume spike detected: 2.3x avg @ $418", timestamp: "10:23:48" },
        { type: "GEX", msg: "GEX zero flip confirmed at $417.25", timestamp: "10:22:30" },
        { type: "FLOW", msg: "Block trade: 500 calls $425 exp 05/31", timestamp: "10:21:15" },
        { type: "SIGNAL", msg: "magnet_pull SHORT conf:0.547 $422.24", timestamp: "10:20:02" },
        { type: "ALERT", msg: "OI concentration: $420 put wall +15%", timestamp: "10:18:45" },
        { type: "GEX", msg: "Dealer positioning: NET SHORT gamma", timestamp: "10:17:22" },
        { type: "FLOW", msg: "Unusual put activity @ $415 exp 05/17", timestamp: "10:16:08" }
    ],
    
    // Additional computed values
    totalPnL: 12400,
    activeSignals: 8,
    totalSignals: 52,
    wsConnected: true
};

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = syngexData;
}
