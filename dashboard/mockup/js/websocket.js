/**
 * WebSocket Client for Syngex Heatmap
 * Handles connection, reconnection, and real-time data updates
 * Preserved from dashboard - maintains broadcast subscription functionality
 */

class HeatmapWebSocket {
    constructor(url = 'ws://localhost:8202/ws') {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 2000; // 2 seconds
        this.subscribers = {
            signals: [],
            metrics: [],
            gex: [],
            gamma: [],
            positions: [],
            logs: []
        };
        this.isConnected = false;
    }

    connect() {
        console.log('[WebSocket] Connecting to:', this.url);
        
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('[WebSocket] Connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
            
            // Subscribe to all channels
            this.subscribeAll();
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('[WebSocket] Failed to parse message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('[WebSocket] Error:', error);
        };

        this.ws.onclose = () => {
            console.log('[WebSocket] Disconnected');
            this.isConnected = false;
            this.updateConnectionStatus(false);
            
            // Attempt reconnection
            this.attemptReconnect();
        };
    }

    subscribeAll() {
        const message = {
            type: 'subscribe',
            channels: ['signals', 'metrics', 'gex', 'gamma', 'positions', 'logs']
        };
        this.ws.send(JSON.stringify(message));
        console.log('[WebSocket] Subscribed to all channels');
    }

    subscribe(channel, callback) {
        if (this.subscribers[channel]) {
            this.subscribers[channel].push(callback);
        }
    }

    unsubscribe(channel, callback) {
        if (this.subscribers[channel]) {
            this.subscribers[channel] = this.subscribers[channel].filter(cb => cb !== callback);
        }
    }

    handleMessage(message) {
        const { type, channel, data } = message;
        
        // Notify all subscribers for this channel
        if (channel && this.subscribers[channel]) {
            this.subscribers[channel].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`[WebSocket] Subscriber error for ${channel}:`, error);
                }
            });
        }
        
        // Handle snapshot messages
        if (type === 'snapshot' && data) {
            if (data.signals) this.notify('signals', data.signals);
            if (data.metrics) this.notify('metrics', data.metrics);
            if (data.gex) this.notify('gex', data.gex);
            if (data.gamma) this.notify('gamma', data.gamma);
            if (data.logs) this.notify('logs', data.logs);
            if (data.positions) this.notify('positions', data.positions);
        }
    }

    notify(channel, data) {
        if (this.subscribers[channel]) {
            this.subscribers[channel].forEach(callback => callback(data));
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`[WebSocket] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
            
            // Exponential backoff
            this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000);
        } else {
            console.error('[WebSocket] Max reconnection attempts reached');
            this.updateConnectionStatus(false);
        }
    }

    updateConnectionStatus(connected) {
        // Update UI status indicators
        const statusElements = document.querySelectorAll('.ws-status');
        statusElements.forEach(el => {
            if (connected) {
                el.className = 'ws-status connected';
                el.textContent = '● WebSocket: Connected';
                el.style.color = '#22c55e'; // Green
            } else {
                el.className = 'ws-status disconnected';
                el.textContent = '● WebSocket: Disconnected';
                el.style.color = '#ef4444'; // Red
            }
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Global instance
const heatmapWs = new HeatmapWebSocket();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Heatmap] Initializing WebSocket client');
    heatmapWs.connect();
});
