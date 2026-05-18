// dashboard/mockup/js/websocket.js — WebSocket client for real-time data

/**
 * WebSocket client for connecting to the Syngex WebSocket server.
 * Handles connection, reconnection, subscription, and message handling.
 */

// Configuration
const WS_CONFIG = {
    url: 'ws://localhost:8202/ws',
    reconnectDelay: 2000,        // Initial reconnect delay (ms)
    maxReconnectDelay: 30000,    // Maximum reconnect delay (ms)
    reconnectMultiplier: 1.5,    // Multiplier for exponential backoff
    maxReconnectAttempts: 10,    // Maximum reconnection attempts
    pingInterval: 20000          // Ping interval (ms)
};

// State
let ws = null;
let reconnectAttempts = 0;
let reconnectTimer = null;
let pingTimer = null;
let isConnected = false;

// Callbacks
const callbacks = {
    onConnect: null,
    onDisconnect: null,
    onError: null,
    onSnapshot: null,
    onSignalsUpdate: null,
    onMetricsUpdate: null,
    onGexUpdate: null,
    onPositionsUpdate: null,
    onMessage: null  // Generic message handler
};

/**
 * Set callback handlers
 */
function setCallback(event, handler) {
    if (callbacks.hasOwnProperty(event)) {
        callbacks[event] = handler;
    }
}

/**
 * Connect to WebSocket server
 */
function connect() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('[WebSocket] Already connected');
        return;
    }
    
    console.log(`[WebSocket] Connecting to ${WS_CONFIG.url}`);
    
    try {
        ws = new WebSocket(WS_CONFIG.url);
        
        ws.onopen = onOpen;
        ws.onmessage = onMessage;
        ws.onerror = onError;
        ws.onclose = onClose;
        
    } catch (error) {
        console.error('[WebSocket] Connection error:', error);
        handleReconnect();
    }
}

/**
 * Handle WebSocket open event
 */
function onOpen() {
    console.log('[WebSocket] Connected');
    isConnected = true;
    reconnectAttempts = 0;
    
    // Clear any existing ping timer
    if (pingTimer) {
        clearInterval(pingTimer);
    }
    
    // Start ping timer
    pingTimer = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
        }
    }, WS_CONFIG.pingInterval);
    
    // Subscribe to all channels
    subscribe(['signals', 'metrics', 'gex', 'positions']);
    
    // Call callback
    if (callbacks.onConnect) {
        callbacks.onConnect();
    }
    
    updateConnectionStatus(true);
}

/**
 * Handle WebSocket message
 */
function onMessage(event) {
    try {
        const message = JSON.parse(event.data);
        const { type, data, timestamp } = message;
        
        // Call generic handler
        if (callbacks.onMessage) {
            callbacks.onMessage(message);
        }
        
        // Route to specific handlers
        switch (type) {
            case 'snapshot':
                console.log('[WebSocket] Received snapshot');
                if (callbacks.onSnapshot) {
                    callbacks.onSnapshot(data);
                }
                break;
                
            case 'signals_update':
                if (callbacks.onSignalsUpdate) {
                    callbacks.onSignalsUpdate(data);
                }
                break;
                
            case 'metrics_update':
                if (callbacks.onMetricsUpdate) {
                    callbacks.onMetricsUpdate(data);
                }
                break;
                
            case 'gex_update':
                if (callbacks.onGexUpdate) {
                    callbacks.onGexUpdate(data);
                }
                break;
                
            case 'positions_update':
                if (callbacks.onPositionsUpdate) {
                    callbacks.onPositionsUpdate(data);
                }
                break;
                
            case 'ping':
                // Keep-alive ping from server
                break;
                
            case 'subscribed':
                console.log('[WebSocket] Subscribed to:', data.channels);
                break;
                
            default:
                console.log('[WebSocket] Unknown message type:', type);
        }
        
    } catch (error) {
        console.error('[WebSocket] Message parse error:', error);
    }
}

/**
 * Handle WebSocket error
 */
function onError(error) {
    console.error('[WebSocket] Error:', error);
    
    if (callbacks.onError) {
        callbacks.onError(error);
    }
}

/**
 * Handle WebSocket close
 */
function onClose(event) {
    console.log('[WebSocket] Disconnected (code:', event.code, 'reason:', event.reason + ')');
    isConnected = false;
    
    // Clear ping timer
    if (pingTimer) {
        clearInterval(pingTimer);
        pingTimer = null;
    }
    
    // Call callback
    if (callbacks.onDisconnect) {
        callbacks.onDisconnect(event);
    }
    
    updateConnectionStatus(false);
    
    // Attempt reconnection
    handleReconnect();
}

/**
 * Handle reconnection with exponential backoff
 */
function handleReconnect() {
    if (reconnectTimer) {
        clearTimeout(reconnectTimer);
    }
    
    if (reconnectAttempts >= WS_CONFIG.maxReconnectAttempts) {
        console.error('[WebSocket] Max reconnection attempts reached');
        return;
    }
    
    // Calculate delay with exponential backoff
    const delay = Math.min(
        WS_CONFIG.reconnectDelay * Math.pow(WS_CONFIG.reconnectMultiplier, reconnectAttempts),
        WS_CONFIG.maxReconnectDelay
    );
    
    reconnectAttempts++;
    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttempts})...`);
    
    reconnectTimer = setTimeout(() => {
        reconnectTimer = null;
        connect();
    }, delay);
}

/**
 * Subscribe to channels
 */
function subscribe(channels) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn('[WebSocket] Cannot subscribe: not connected');
        return;
    }
    
    const message = {
        type: 'subscribe',
        channels: channels
    };
    
    ws.send(JSON.stringify(message));
    console.log('[WebSocket] Subscribing to:', channels);
}

/**
 * Unsubscribe from channels
 */
function unsubscribe(channels) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn('[WebSocket] Cannot unsubscribe: not connected');
        return;
    }
    
    const message = {
        type: 'unsubscribe',
        channels: channels
    };
    
    ws.send(JSON.stringify(message));
    console.log('[WebSocket] Unsubscribing from:', channels);
}

/**
 * Disconnect from WebSocket server
 */
function disconnect() {
    // Clear reconnect timer
    if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
    }
    
    // Clear ping timer
    if (pingTimer) {
        clearInterval(pingTimer);
        pingTimer = null;
    }
    
    // Close connection
    if (ws) {
        ws.close();
        ws = null;
    }
    
    isConnected = false;
    updateConnectionStatus(false);
    console.log('[WebSocket] Manually disconnected');
}

/**
 * Update connection status UI
 */
function updateConnectionStatus(connected) {
    const statusElements = document.querySelectorAll('.ws-status');
    
    statusElements.forEach(el => {
        if (connected) {
            el.className = 'ws-status connected';
            el.textContent = '● WebSocket: Connected';
        } else {
            el.className = 'ws-status disconnected';
            el.textContent = '● WebSocket: Disconnected';
        }
    });
}

/**
 * Get connection status
 */
function getConnectionStatus() {
    return {
        connected: isConnected,
        attempts: reconnectAttempts,
        url: WS_CONFIG.url
    };
}

/**
 * Initialize WebSocket client with default handlers
 */
function initWebSocket() {
    console.log('[WebSocket] Initializing...');
    
    // Set up default handlers for dashboard
    setCallback('onSnapshot', handleSnapshot);
    setCallback('onSignalsUpdate', handleSignalsUpdate);
    setCallback('onMetricsUpdate', handleMetricsUpdate);
    setCallback('onGexUpdate', handleGexUpdate);
    setCallback('onConnect', handleConnect);
    setCallback('onDisconnect', handleDisconnect);
    
    // Connect
    connect();
}

/**
 * Default snapshot handler
 */
function handleSnapshot(data) {
    console.log('[WebSocket] Snapshot data:', data);
    
    // Update global data if available
    if (typeof syngexData !== 'undefined') {
        if (data.signals) syngexData.strategyGrid = data.signals;
        if (data.metrics) syngexData.riskMetrics = { ...syngexData.riskMetrics, ...data.metrics };
        if (data.gex && data.gex.heatmapStrikes) syngexData.heatmapStrikes = data.gex.heatmapStrikes;
        if (data.logs) syngexData.logs = data.logs;
        
        // Re-render components
        if (typeof renderStrategyHeatmap === 'function') renderStrategyHeatmap();
        if (typeof renderRiskMetricsExtended === 'function') renderRiskMetricsExtended();
        if (typeof renderDominantLevelsHeatmap === 'function') renderDominantLevelsHeatmap();
        if (typeof renderLogStream === 'function') renderLogStream();
    }
}

/**
 * Default signals update handler
 */
function handleSignalsUpdate(data) {
    console.log('[WebSocket] Signals update:', data);
    
    if (typeof syngexData !== 'undefined' && data.signals) {
        syngexData.strategyGrid = data.signals;
        if (typeof renderStrategyHeatmap === 'function') renderStrategyHeatmap();
    }
}

/**
 * Default metrics update handler
 */
function handleMetricsUpdate(data) {
    console.log('[WebSocket] Metrics update:', data);
    
    if (typeof syngexData !== 'undefined') {
        syngexData.riskMetrics = { ...syngexData.riskMetrics, ...data };
        if (typeof renderRiskMetricsExtended === 'function') renderRiskMetricsExtended();
    }
}

/**
 * Default GEX update handler
 */
function handleGexUpdate(data) {
    console.log('[WebSocket] GEX update:', data);
    
    if (typeof syngexData !== 'undefined' && data.heatmapStrikes) {
        syngexData.heatmapStrikes = data.heatmapStrikes;
        if (typeof renderDominantLevelsHeatmap === 'function') renderDominantLevelsHeatmap();
    }
}

/**
 * Default connect handler
 */
function handleConnect() {
    console.log('[WebSocket] Connected to server');
    
    // Update UI
    const statusElements = document.querySelectorAll('.ws-status');
    statusElements.forEach(el => {
        el.className = 'ws-status connected';
        el.textContent = '● WebSocket: Connected';
    });
}

/**
 * Default disconnect handler
 */
function handleDisconnect() {
    console.log('[WebSocket] Disconnected from server');
    
    // Update UI
    const statusElements = document.querySelectorAll('.ws-status');
    statusElements.forEach(el => {
        el.className = 'ws-status disconnected';
        el.textContent = '● WebSocket: Disconnected';
    });
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWebSocket);
} else {
    initWebSocket();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        connect,
        disconnect,
        subscribe,
        unsubscribe,
        setCallback,
        getConnectionStatus
    };
}
