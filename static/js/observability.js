/**
 * Observability Dashboard JavaScript
 */

let allRecords = [];
let filteredRecords = [];

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadData();
    });
    
    // Search input
    document.getElementById('searchQuery').addEventListener('input', (e) => {
        filterRecords();
    });
    
    // Status filter
    document.getElementById('filterStatus').addEventListener('change', (e) => {
        filterRecords();
    });
}

// Load data from API
async function loadData() {
    try {
        // Show loading
        showLoading();
        
        // Fetch data
        const response = await fetch('/api/observability/data');
        if (!response.ok) {
            throw new Error('Failed to fetch observability data');
        }
        
        const data = await response.json();
        
        // Store records
        allRecords = data.records || [];
        filteredRecords = [...allRecords];
        
        // Update UI
        updateSummaryStats(data.summary);
        updateTable();
        
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load observability data');
    }
}

// Show loading state
function showLoading() {
    const tbody = document.getElementById('recordsTableBody');
    tbody.innerHTML = `
        <tr class="loading-row">
            <td colspan="9">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i> Loading records...
                </div>
            </td>
        </tr>
    `;
}

// Show error message
function showError(message) {
    const tbody = document.getElementById('recordsTableBody');
    tbody.innerHTML = `
        <tr class="loading-row">
            <td colspan="9">
                <div class="no-records">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </div>
            </td>
        </tr>
    `;
}

// Update summary statistics
function updateSummaryStats(summary) {
    if (!summary) return;
    
    document.getElementById('statTotalRequests').textContent = summary.total_requests || 0;
    document.getElementById('statSuccessful').textContent = summary.successful_requests || 0;
    document.getElementById('statTotalTokens').textContent = (summary.total_tokens || 0).toLocaleString();
    document.getElementById('statTotalCost').textContent = `$${(summary.total_cost_usd || 0).toFixed(6)}`;
    document.getElementById('statAvgLatency').textContent = `${(summary.avg_latency_ms || 0).toFixed(0)}ms`;
    document.getElementById('statAgents').textContent = summary.total_agents_used || 0;
}

// Filter records based on search and status
function filterRecords() {
    const searchQuery = document.getElementById('searchQuery').value.toLowerCase();
    const statusFilter = document.getElementById('filterStatus').value;
    
    filteredRecords = allRecords.filter(record => {
        // Filter by search query
        const matchesSearch = !searchQuery || 
            record.query.toLowerCase().includes(searchQuery);
        
        // Filter by status
        const matchesStatus = statusFilter === 'all' ||
            (statusFilter === 'success' && record.success) ||
            (statusFilter === 'failed' && !record.success);
        
        return matchesSearch && matchesStatus;
    });
    
    updateTable();
}

// Update records table
function updateTable() {
    const tbody = document.getElementById('recordsTableBody');
    const tableInfo = document.getElementById('tableInfo');
    
    // Update table info
    tableInfo.textContent = `Showing ${filteredRecords.length} record${filteredRecords.length !== 1 ? 's' : ''}`;
    
    // No records
    if (filteredRecords.length === 0) {
        tbody.innerHTML = `
            <tr class="loading-row">
                <td colspan="9">
                    <div class="no-records">
                        <i class="fas fa-inbox"></i> No records found
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Build table rows
    tbody.innerHTML = filteredRecords.map(record => {
        const timestamp = new Date(record.timestamp).toLocaleString();
        const status = record.success 
            ? '<span class="badge badge-success"><i class="fas fa-check"></i> Success</span>'
            : '<span class="badge badge-error"><i class="fas fa-times"></i> Failed</span>';
        
        // Agent names
        const agents = record.agents.map(a => 
            `<span class="badge badge-agent">${a.name}</span>`
        ).join(' ');
        
        // Tool names (unique)
        const toolNames = [...new Set(record.tools.map(t => t.name))];
        const tools = toolNames.map(name => 
            `<span class="badge badge-tool">${name}</span>`
        ).join(' ');
        
        return `
            <tr>
                <td>${timestamp}</td>
                <td><div class="query-cell" title="${escapeHtml(record.query)}">${escapeHtml(record.query)}</div></td>
                <td>${agents || '-'}</td>
                <td>${tools || '-'}</td>
                <td>${record.total_tokens.toLocaleString()}</td>
                <td>$${record.total_cost_usd.toFixed(6)}</td>
                <td>${record.total_latency_ms.toFixed(0)}ms</td>
                <td>${status}</td>
                <td>
                    <button class="btn-view-details" onclick="showDetails('${record.id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Show detail modal
function showDetails(recordId) {
    const record = allRecords.find(r => r.id === recordId);
    if (!record) return;
    
    const modal = document.getElementById('detailModal');
    const modalBody = document.getElementById('modalBody');
    
    // Build detail content
    modalBody.innerHTML = `
        <!-- Overview Section -->
        <div class="detail-section">
            <h4><i class="fas fa-info-circle"></i> Overview</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Query</div>
                    <div class="detail-value">${escapeHtml(record.query)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Status</div>
                    <div class="detail-value">
                        ${record.success 
                            ? '<span class="badge badge-success"><i class="fas fa-check"></i> Success</span>'
                            : '<span class="badge badge-error"><i class="fas fa-times"></i> Failed</span>'}
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Timestamp</div>
                    <div class="detail-value">${new Date(record.timestamp).toLocaleString()}</div>
                </div>
            </div>
        </div>
        
        <!-- Metrics Section -->
        <div class="detail-section">
            <h4><i class="fas fa-chart-bar"></i> Metrics</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Total Tokens</div>
                    <div class="detail-value">${record.total_tokens.toLocaleString()}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Total Cost</div>
                    <div class="detail-value">$${record.total_cost_usd.toFixed(6)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Total Latency</div>
                    <div class="detail-value">${record.total_latency_ms.toFixed(0)}ms</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Agents Used</div>
                    <div class="detail-value">${record.agents.length}</div>
                </div>
            </div>
        </div>
        
        <!-- Agent Timeline -->
        <div class="detail-section">
            <h4><i class="fas fa-robot"></i> Agent Execution Timeline</h4>
            <div class="timeline">
                ${record.agents.map((agent, idx) => `
                    <div class="timeline-item">
                        <div class="timeline-header">
                            <span class="timeline-title">
                                ${idx + 1}. ${agent.name} (${agent.stage})
                            </span>
                            <span class="timeline-latency">
                                <i class="fas fa-clock"></i> ${agent.latency_ms.toFixed(0)}ms
                            </span>
                        </div>
                        <div class="timeline-meta">
                            <strong>Tools:</strong> ${agent.tools_used.join(', ') || 'None'} 
                            | <strong>Tokens:</strong> ${agent.tokens} 
                            | <strong>Status:</strong> ${agent.success ? '✓ Success' : '✗ Failed'}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <!-- Tool Usage -->
        <div class="detail-section">
            <h4><i class="fas fa-tools"></i> Tool Usage (Execution Order)</h4>
            <div class="timeline">
                ${record.tools.map(tool => `
                    <div class="timeline-item">
                        <div class="timeline-header">
                            <span class="timeline-title">
                                #${tool.order} - ${tool.name}
                            </span>
                            <span class="timeline-latency">
                                <i class="fas fa-clock"></i> ${tool.latency_ms.toFixed(0)}ms
                            </span>
                        </div>
                        <div class="timeline-meta">
                            <strong>Input:</strong> ${tool.input_length.toLocaleString()} chars 
                            | <strong>Output:</strong> ${tool.output_length.toLocaleString()} chars 
                            | <strong>Tokens:</strong> ${tool.tokens}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        ${record.error ? `
            <div class="detail-section">
                <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
                <div class="detail-item">
                    <div class="detail-value" style="color: var(--error);">${escapeHtml(record.error)}</div>
                </div>
            </div>
        ` : ''}
    `;
    
    // Show modal
    modal.classList.add('active');
}

// Close detail modal
function closeDetailModal() {
    const modal = document.getElementById('detailModal');
    modal.classList.remove('active');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh every 30 seconds
setInterval(() => {
    loadData();
}, 30000);
