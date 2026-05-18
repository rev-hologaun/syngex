/**
 * Syngex Heatmap Dashboard - Main Application
 * Handles rendering and data management
 * Merged: newheatmap design + dashboard WebSocket broadcast integration
 */

// Global data store
const syngexData = {
    strategyGrid: [],
    riskMetrics: {},
    heatmapStrikes: [],
    activePositions: [],
    logs: [],
    gammaProfile: null,
    gammaChart: null,  // Chart.js instance
    symbol: 'TSLA',
    price: 245.67,
    strategyCount: 42
};

// Profile Charts - Multi-chart selection with conditional rendering
let selectedCharts = [];  // Track which charts selected
const chartColors = {
    gamma: '#06b6d4',
    oi: '#3b82f6',
    volume: '#f59e0b',
    flow: '#10b981',
    gex: '#06b6d4',
    iv: '#d946ef',
    greeks: '#8b5cf6'
};

// ========== WebSocket Integration ==========

// Subscribe to data updates (from dashboard - preserves broadcast functionality)
function initializeWebSocketSubscriptions() {
    // Strategy grid updates
    heatmapWs.subscribe('signals', (data) => {
        console.log('[Signals Update]', data);
        syngexData.strategyGrid = data;
        renderStrategyHeatmap();
    });

    // Risk metrics updates
    heatmapWs.subscribe('metrics', (data) => {
        console.log('[Metrics Update]', data);
        syngexData.riskMetrics = data;
        renderRiskMetricsExtended();
    });

    // GEX updates
    heatmapWs.subscribe('gex', (data) => {
        console.log('[GEX Update]', data);
        syngexData.heatmapStrikes = data.heatmapStrikes || [];
        renderDominantLevelsHeatmap();
    });

    // Positions updates
    heatmapWs.subscribe('positions', (data) => {
        console.log('[Positions Update]', data);
        syngexData.activePositions = data;
        renderActivePositions();
    });

    // Log updates
    heatmapWs.subscribe('logs', (data) => {
        console.log('[Logs Update]', data);
        // Append new logs
        data.forEach(log => {
            syngexData.logs.unshift(log);
            // Keep only last 10 messages
            if (syngexData.logs.length > 10) {
                syngexData.logs.pop();
            }
        });
        renderLogStream();
    });

    // Gamma profile updates
    heatmapWs.subscribe('gamma', (data) => {
        console.log('[Gamma Update]', data);
        syngexData.gammaProfile = data;
        // Note: Gamma chart rendering not in newheatmap design
    });

    // Initial snapshot request
    heatmapWs.ws?.send(JSON.stringify({ type: 'request_snapshot' }));
}

// ========== Initialization ==========

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize dashboard
        initTabs();
        initProfileCharts();
        renderDominantLevelsHeatmap();
        renderRiskMetricsExtended();
        renderStrategyHeatmap();
        renderLogStream();
        initInteractions();
        
        console.log('Syngex Ultimate Control Center initialized');
        console.log(`Loading ${syngexData.strategyCount} strategies for ${syngexData.symbol}`);
        
        // Initialize WebSocket subscriptions after rendering
        if (typeof heatmapWs !== 'undefined') {
            initializeWebSocketSubscriptions();
        }
    } catch (error) {
        console.error('Fatal error during dashboard initialization:', error);
        // Don't let one error crash the entire page
    }
});

// Initialize Tabs (placeholder - tabs are now handled by profile tabs)
function initTabs() {
    // Legacy function - tabs are now handled by profile-tabs
    console.log('Tabs initialized');
}

function initProfileCharts() {
    try {
        const profileTabs = document.querySelectorAll('.profile-tabs .tab');
        const singleChartContainer = document.getElementById('singleChartContainer');
        const dualChartContainer = document.getElementById('dualChartContainer');
        const chartSectionTitle = document.getElementById('chartSectionTitle');
        
        // Safety check - if elements not found, log error and return without crashing
        if (!profileTabs || profileTabs.length === 0) {
            console.error('Profile tabs not found');
            return;
        }
        if (!singleChartContainer || !dualChartContainer) {
            console.error('Chart containers not found');
            return;
        }
        if (!chartSectionTitle) {
            console.error('Chart section title not found');
            return;
        }
        
        // Initialize with first chart selected (Gamma)
        selectedCharts = ['gamma'];
        profileTabs[0].classList.add('active');
        
        // Render initial chart
        renderProfileCharts();
        
        // Setup tab click handlers
        profileTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const chartType = tab.dataset.chart;
                
                // Toggle selection
                const index = selectedCharts.indexOf(chartType);
                if (index > -1) {
                    // Deselect
                    selectedCharts.splice(index, 1);
                    tab.classList.remove('active');
                } else {
                    // Select (max 2)
                    if (selectedCharts.length < 2) {
                        selectedCharts.push(chartType);
                        tab.classList.add('active');
                    }
                }
                
                // Update title and render based on selection count
                if (selectedCharts.length === 1) {
                    chartSectionTitle.textContent = 'Profile Chart';
                } else if (selectedCharts.length === 2) {
                    chartSectionTitle.textContent = 'Profile Charts';
                }
                
                renderProfileCharts();
            });
        });
    } catch (error) {
        console.error('Error initializing profile charts:', error);
    }
}

function renderProfileCharts() {
    try {
        const singleChartContainer = document.getElementById('singleChartContainer');
        const dualChartContainer = document.getElementById('dualChartContainer');
        
        if (!singleChartContainer || !dualChartContainer) {
            console.error('Chart containers not found in renderProfileCharts');
            return;
        }
        
        if (selectedCharts.length === 1) {
            // Single chart mode
            singleChartContainer.style.display = 'flex';
            dualChartContainer.style.display = 'none';
            
            // Render single chart
            renderSingleChart(selectedCharts[0]);
            
        } else if (selectedCharts.length === 2) {
            // Dual chart mode
            singleChartContainer.style.display = 'none';
            dualChartContainer.style.display = 'flex';
            
            // Render two charts side-by-side
            renderChartInCanvas('profileChart1', selectedCharts[0]);
            renderChartInCanvas('profileChart2', selectedCharts[1]);
        }
    } catch (error) {
        console.error('Error rendering profile charts:', error);
    }
}

function renderSingleChart(chartType) {
    const canvas = document.getElementById('profileChart');
    if (!canvas) return;
    
    // Resize canvas for high DPI
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width / 2, canvas.height / 2);
    
    // Draw chart with X/Y axis labels
    drawChartWithLabels(ctx, chartType, true, rect.width);  // true = has Y label
}

function renderChartInCanvas(canvasId, chartType) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Resize canvas for high DPI
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width / 2, canvas.height / 2);
    
    // Draw chart with X/Y axis labels (no Y label for dual mode to save space)
    drawChartWithLabels(ctx, chartType, false, rect.width);
}

function drawChartWithLabels(ctx, chartType, showYLabel, displayWidth) {
    const actualWidth = displayWidth;
    const actualHeight = 300;
    const padding = { top: 20, right: 40, bottom: 30, left: showYLabel ? 50 : 20 };
    const chartWidth = actualWidth - padding.left - padding.right;
    const chartHeight = actualHeight - padding.top - padding.bottom;
    
    const color = chartColors[chartType] || '#06b6d4';
    
    // Draw grid lines
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    
    // Vertical grid lines (5 lines)
    for (let i = 0; i <= 4; i++) {
        const x = padding.left + (i * chartWidth / 4);
        ctx.beginPath();
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, actualHeight - padding.bottom);
        ctx.stroke();
    }
    
    // Horizontal grid lines (4 lines)
    for (let i = 0; i <= 3; i++) {
        const y = padding.top + (i * chartHeight / 3);
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(padding.left + chartWidth, y);
        ctx.stroke();
    }
    
    // Generate mock data based on chart type
    const strikePrices = [410, 415, 420, 425, 430, 435, 440];
    const dataPoints = generateChartData(chartType, strikePrices.length);
    
    // Draw chart line
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    dataPoints.forEach((value, i) => {
        const x = padding.left + (i / (dataPoints.length - 1)) * chartWidth;
        const y = padding.top + chartHeight - (value / 100) * chartHeight;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    
    // Draw filled area under line
    ctx.fillStyle = color + '33';  // 20% opacity
    ctx.beginPath();
    
    const firstX = padding.left;
    const lastX = padding.left + chartWidth;
    const bottomY = actualHeight - padding.bottom;
    
    ctx.moveTo(firstX, bottomY);
    
    dataPoints.forEach((value, i) => {
        const x = padding.left + (i / (dataPoints.length - 1)) * chartWidth;
        const y = padding.top + chartHeight - (value / 100) * chartHeight;
        ctx.lineTo(x, y);
    });
    
    ctx.lineTo(lastX, bottomY);
    ctx.closePath();
    ctx.fill();
    
    // Draw current price marker (center)
    const centerX = padding.left + chartWidth / 2;
    const centerY = padding.top + chartHeight / 2;
    
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(centerX, padding.top);
    ctx.lineTo(centerX, bottomY);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // X-axis label
    ctx.fillStyle = '#888';
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Strike Price', actualWidth / 2, actualHeight - 8);
    
    // Y-axis label (optional, for single chart)
    if (showYLabel) {
        ctx.save();
        ctx.translate(10, actualHeight / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.textAlign = 'center';
        ctx.fillText(getChartLabel(chartType), 0, 0);
        ctx.restore();
    }
    
    // X-axis tick labels (strike prices)
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    
    const numTicks = Math.min(strikePrices.length, 7);
    const tickStep = Math.floor(dataPoints.length / numTicks);
    
    strikePrices.forEach((strike, i) => {
        if (i < dataPoints.length) {
            const x = padding.left + (i / (dataPoints.length - 1)) * chartWidth;
            ctx.fillText('$' + strike, x, actualHeight - padding.bottom + 15);
        }
    });
    
    // Y-axis tick labels (if shown)
    if (showYLabel) {
        ctx.textAlign = 'right';
        const yValues = [0, 33, 66, 100];
        const yLabels = ['0', '25', '50', '75'];
        
        yValues.forEach((val, i) => {
            const y = padding.top + chartHeight - (val / 100) * chartHeight;
            ctx.fillText(yLabels[i], padding.left - 8, y + 4);
        });
    }
    
    // Draw data points
    ctx.fillStyle = color;
    dataPoints.forEach((value, i) => {
        const x = padding.left + (i / (dataPoints.length - 1)) * chartWidth;
        const y = padding.top + chartHeight - (value / 100) * chartHeight;
        
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    });
}

function generateChartData(chartType, numPoints) {
    // Generate different patterns based on chart type
    const data = [];
    
    switch(chartType) {
        case 'gamma':
            // Bell curve pattern
            for (let i = 0; i < numPoints; i++) {
                const center = (numPoints - 1) / 2;
                const dist = Math.abs(i - center) / center;
                data.push(Math.max(10, 100 - dist * 90));
            }
            break;
        case 'oi':
            // Skewed distribution
            for (let i = 0; i < numPoints; i++) {
                data.push(30 + Math.random() * 50 + i * 5);
            }
            break;
        case 'volume':
            // Spiky pattern
            for (let i = 0; i < numPoints; i++) {
                if (i === 2 || i === 4) {
                    data.push(80 + Math.random() * 20);
                } else {
                    data.push(20 + Math.random() * 30);
                }
            }
            break;
        case 'flow':
            // Trending pattern
            for (let i = 0; i < numPoints; i++) {
                data.push(40 + i * 8 + Math.random() * 15);
            }
            break;
        case 'gex':
            // Crosses zero
            for (let i = 0; i < numPoints; i++) {
                const center = (numPoints - 1) / 2;
                const val = (i - center) * 20;
                data.push(Math.abs(val) + Math.random() * 10);
            }
            break;
        case 'iv':
            // Volatility smile
            for (let i = 0; i < numPoints; i++) {
                const center = (numPoints - 1) / 2;
                const dist = Math.abs(i - center) / center;
                data.push(30 + dist * 50 + Math.random() * 10);
            }
            break;
        case 'greeks':
            // Mixed pattern
            for (let i = 0; i < numPoints; i++) {
                data.push(20 + Math.random() * 60);
            }
            break;
        default:
            for (let i = 0; i < numPoints; i++) {
                data.push(40 + Math.random() * 40);
            }
    }
    
    return data;
}

function getChartLabel(chartType) {
    const labels = {
        gamma: 'Gamma',
        oi: 'Open Interest',
        volume: 'Volume',
        flow: 'Order Flow',
        gex: 'Gamma Exposure',
        iv: 'Implied Volatility',
        greeks: 'Greeks Value'
    };
    return labels[chartType] || 'Value';
}

// Render Dominant Levels Heatmap (all strikes)
function renderDominantLevelsHeatmap() {
    const container = document.getElementById('dominantLevelsHeatmap');
    if (!container) return;
    
    // Show all heatmap strikes
    const heatmapData = syngexData.heatmapStrikes || syngexData.dominantLevels;
    
    container.innerHTML = heatmapData.map(strike => {
        const gexSign = strike.gex > 0 ? '+' : '';
        let typeClass = strike.type || 'neutral';
        
        // Determine type based on GEX value if not specified
        if (!strike.type) {
            if (strike.gex < -20) typeClass = 'put-wall';
            else if (strike.gex > 20) typeClass = 'call-wall';
            else if (Math.abs(strike.gex) < 5) typeClass = 'magnet';
        }
        
        const intensity = Math.min(Math.abs(strike.gex) / 50, 1); // Normalize for opacity
        
        return `
            <div class="heat-tile ${typeClass}" data-gex="${strike.gex}">
                <div class="strike-label">$${strike.strike}</div>
                <div class="gex-intensity">GEX: ${gexSign}${strike.gex}</div>
            </div>
        `;
    }).join('');
}

// Render Extended Risk Metrics with OHLC, Greeks, OI (3 rows)
function renderRiskMetricsExtended() {
    const container = document.getElementById('riskMetrics');
    if (!container) return;
    
    const r = syngexData.riskMetrics;
    
    // Target order: Row 1: OHLC, Volume, Exposure, OI | Row 2: Delta, Gamma, Theta, Vega | Row 3: Var, MaxDD, Sharpe
    const metrics = [
        // Row 1
        {
            label: 'OHLC',
            value: `O: $${r.ohlc.open.toFixed(2)} H: $${r.ohlc.high.toFixed(2)} L: $${r.ohlc.low.toFixed(2)} C: $${r.ohlc.close.toFixed(2)}`,
            positive: true
        },
        {
            label: 'VOLUME',
            value: `${r.volume} ${r.volumeChange}`,
            positive: r.volumeChange.includes('+')
        },
        {
            label: 'EXPOSURE',
            value: r.exposure,
            positive: true
        },
        {
            label: 'OI',
            value: r.openInterest,
            positive: true
        },
        // Row 2
        {
            label: 'DELTA',
            value: (r.delta > 0 ? '+' : '') + r.delta.toLocaleString(),
            positive: r.delta > 0
        },
        {
            label: 'GAMMA',
            value: (r.gamma > 0 ? '+' : '') + r.gamma,
            positive: r.gamma > 0
        },
        {
            label: 'THETA',
            value: (r.theta > 0 ? '+' : '') + r.theta.toLocaleString(),
            positive: r.theta > 0
        },
        {
            label: 'VEGA',
            value: (r.vega > 0 ? '+' : '') + r.vega.toLocaleString(),
            positive: r.vega > 0
        },
        // Row 3
        {
            label: 'VAR (1D)',
            value: r.var1d,
            positive: true
        },
        {
            label: 'MAX DD',
            value: r.maxDrawdown,
            positive: false
        },
        {
            label: 'SHARPE',
            value: r.sharpe.toFixed(2),
            positive: true
        }
    ];
    
    // Wrap in 3 rows (4, 4, 3 tiles)
    const row1 = metrics.slice(0, 4);
    const row2 = metrics.slice(4, 8);
    const row3 = metrics.slice(8, 11);
    
    const renderRow = (rowMetrics) => `
        <div class="metric-row">
            ${rowMetrics.map(metric => `
                <div class="metric-tile">
                    <label>${metric.label}</label>
                    <span class="${metric.positive ? 'positive' : 'negative'}">${metric.value}</span>
                </div>
            `).join('')}
        </div>
    `;
    
    container.innerHTML = `
        ${renderRow(row1)}
        ${renderRow(row2)}
        ${renderRow(row3)}
    `;
}

// Render Active Positions
function renderActivePositions() {
    const container = document.getElementById('activePositions');
    if (!container) return;
    
    if (!syngexData.activePositions || syngexData.activePositions.length === 0) {
        container.innerHTML = '<div class="no-positions">No active positions</div>';
        return;
    }
    
    container.innerHTML = syngexData.activePositions.map(pos => {
        const pnlClass = pos.pnl >= 0 ? 'positive' : 'negative';
        const pnlSign = pos.pnl >= 0 ? '+' : '';
        const formattedPnl = Math.abs(pos.pnl).toLocaleString();
        
        return `
            <div class="position-item">
                <div class="position-strategy">${pos.strategy}</div>
                <div class="position-entry">$${pos.entry.toFixed(2)} → $${pos.target.toFixed(2)}</div>
                <div class="position-pnl ${pnlClass}">${pnlSign}$${formattedPnl}</div>
                <div class="position-time">${pos.time}</div>
            </div>
        `;
    }).join('');
}

// Render Active Strategies Heatmap (6x7 grid = 42 cells with new layout)
function renderStrategyHeatmap() {
    const container = document.getElementById('strategyGrid');
    if (!container) return;
    
    // Fill to 42 cells (6x7 grid)
    const strategies = syngexData.strategyGrid;
    const totalCells = 42;
    
    let html = '';
    
    for (let i = 0; i < totalCells; i++) {
        const strategy = strategies[i] || { 
            name: `STRAT_${i+1}`, 
            direction: null, 
            confidence: 0, 
            entry: null, 
            stop: null, 
            target: null, 
            pnl: 0, 
            time: '–', 
            active: false,
            layer: 'L3'
        };
        
        if (!strategy.active || !strategy.direction) {
            // Inactive / NO SIGNAL state
            html += `
                <div class="strategy-cell inactive" data-index="${i}" data-strategy="${strategy.name}">
                    <div class="cell-header">
                        <span class="layer-badge">${strategy.layer || 'L3'}</span>
                        <span class="strategy-name">NO_SIGNAL</span>
                        <span class="status-dot inactive"></span>
                    </div>
                    <div class="no-signal">NO RECENT SIGNAL</div>
                    <div class="footer-row">
                        <span class="last">Last: –</span>
                    </div>
                </div>
            `;
        } else {
            // Active strategy
            const directionClass = strategy.direction.toLowerCase();
            const pnlClass = strategy.pnl >= 0 ? 'positive' : 'negative';
            const pnlSign = strategy.pnl >= 0 ? '+' : '';
            const formattedPnl = Math.abs(strategy.pnl).toLocaleString();
            
            html += `
                <div class="strategy-cell active ${directionClass}" data-index="${i}" data-strategy="${strategy.name}">
                    <div class="cell-header">
                        <span class="layer-badge">${strategy.layer || 'L3'}</span>
                        <span class="strategy-name">${strategy.name}</span>
                        <span class="status-dot"></span>
                    </div>
                    <div class="direction-row">
                        <span class="direction">${strategy.direction === 'BUY' ? '▲' : '▼'} ${strategy.direction}</span>
                        <span class="confidence-bar">
                            <div class="confidence-fill" style="width: ${strategy.confidence}%"></div>
                            <span class="confidence-value">${strategy.confidence}%</span>
                        </span>
                    </div>
                    <div class="price-row-1">
                        <span class="entry">@ $${strategy.entry.toFixed(2)}</span>
                        <span class="separator">|</span>
                        <span class="stop">S: $${strategy.stop.toFixed(2)}</span>
                    </div>
                    <div class="price-row-2">
                        <span class="target">T: $${strategy.target.toFixed(2)}</span>
                    </div>
                    <div class="footer-row">
                        <span class="last">Last: ${strategy.time}</span>
                        <span class="pnl ${pnlClass}">${pnlSign}$${formattedPnl}</span>
                    </div>
                </div>
            `;
        }
    }
    
    container.innerHTML = html;
}

// Render Log Stream - Limited to last 10 messages
function renderLogStream(filter = 'all') {
    const container = document.getElementById('logStream');
    if (!container) return;
    
    const filteredLogs = filter === 'all' 
        ? syngexData.logs 
        : syngexData.logs.filter(log => log.type === filter);
    
    // Take only the last 10 messages
    const last10Logs = filteredLogs.slice(-10);
    
    container.innerHTML = last10Logs.map(log => `
        <div class="log-entry ${log.type.toLowerCase()}">
            <span class="log-type">[${log.type}]</span>
            <span class="log-message">${log.msg}</span>
            <span class="log-time" style="color: var(--text-muted); font-size: 0.7rem; margin-left: 10px;">${log.timestamp}</span>
        </div>
    `).join('');
    
    // Auto-scroll to bottom (newest messages)
    container.scrollTop = container.scrollHeight;
}

// Legacy function - kept for compatibility, now handled by initProfileCharts
function initChart() {
    // Deprecated - use initProfileCharts instead
    console.log('initChart deprecated, use initProfileCharts');
}

// Initialize Interactions
function initInteractions() {
    // Strategy cell clicks
    const cells = document.querySelectorAll('.strategy-cell');
    cells.forEach(cell => {
        cell.addEventListener('click', function() {
            // Remove selected from all
            cells.forEach(c => c.classList.remove('selected'));
            // Add to clicked
            this.classList.add('selected');
            
            const strategyName = this.dataset.strategy;
            console.log(`Selected strategy: ${strategyName}`);
        });
    });
    
    // Log filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            renderLogStream(filter);
        });
    });
    
    // Panel hover effects (expand on active)
    const panels = document.querySelectorAll('.panel');
    panels.forEach(panel => {
        panel.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.995)';
        });
        
        panel.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
        });
        
        panel.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Simulate real-time updates (demo only)
    simulateRealTimeUpdates();
}

// Simulate Real-Time Updates (for demo purposes)
function simulateRealTimeUpdates() {
    // Add a new log entry every 10 seconds
    setInterval(() => {
        const newLog = {
            type: ['SIGNAL', 'ALERT', 'GEX', 'FLOW'][Math.floor(Math.random() * 4)],
            msg: `Auto-generated log entry ${Date.now().toString().slice(-4)}`,
            timestamp: new Date().toLocaleTimeString('en-US', { hour12: false })
        };
        
        syngexData.logs.unshift(newLog);
        // Keep only last 10 messages in data
        if (syngexData.logs.length > 10) {
            syngexData.logs.pop();
        }
        
        // Only update if "all" filter is active
        const activeFilter = document.querySelector('.filter-btn.active');
        if (activeFilter && activeFilter.dataset.filter === 'all') {
            renderLogStream('all');
        }
    }, 10000);
    
    // Update price every 5 seconds
    setInterval(() => {
        const priceEl = document.querySelector('.price');
        if (priceEl) {
            const currentPrice = syngexData.price;
            const change = (Math.random() - 0.5) * 0.5;
            syngexData.price = currentPrice + change;
            priceEl.textContent = `$${syngexData.price.toFixed(2)}`;
        }
    }, 5000);
}

// Utility: Format P&L
function formatPnL(value) {
    const sign = value >= 0 ? '+' : '';
    const formatted = Math.abs(value).toLocaleString();
    return `${sign}$${formatted}`;
}

// Utility: Format large numbers
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(2) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(2) + 'K';
    }
    return num.toString();
}
