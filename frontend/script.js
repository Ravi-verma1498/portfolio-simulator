const API_URL = 'http://localhost:5000';

let currentStrategy = 'equal_weight';
let currentSize = 'standard';
let currentFilename = null;
let portfolioData = null;
let pieChart = null;

// DOM elements
const generateBtn = document.getElementById('generateBtn');
const statusDiv = document.getElementById('status');
const statusText = document.getElementById('statusText');
const resultsDiv = document.getElementById('results');
const tableBody = document.getElementById('tableBody');
const totalValue = document.getElementById('totalValue');
const totalStocks = document.getElementById('totalStocks');
const strategyName = document.getElementById('strategyName');
const topHolding = document.getElementById('topHolding');
const downloadBtn = document.getElementById('downloadBtn');
const downloadJsonBtn = document.getElementById('downloadJsonBtn');
const printBtn = document.getElementById('printBtn');
const themeBtn = document.getElementById('themeBtn');

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(this.dataset.tab).classList.add('active');
    });
});

// Strategy selection
document.querySelectorAll('.strategy-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.strategy-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentStrategy = this.dataset.strategy;
    });
});

// Size selection
document.querySelectorAll('.size-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentSize = this.dataset.size;
    });
});

// Theme toggle
let darkMode = false;
themeBtn.addEventListener('click', function() {
    darkMode = !darkMode;
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    this.textContent = darkMode ? '☀️' : '🌙';
});

// Generate portfolio
generateBtn.addEventListener('click', async function() {
    this.disabled = true;
    this.innerHTML = '<span class="spinner"></span> Generating...';
    setStatus('⏳ Generating portfolio... This takes 2-3 minutes', 'loading');
    resultsDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                strategy: currentStrategy,
                portfolio_size: currentSize
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentFilename = data.filename;
            portfolioData = data;
            displayResults(data);
            setStatus('✅ Portfolio generated successfully!', 'success');
        } else {
            setStatus('❌ Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        setStatus('❌ Error: Could not connect to server. Make sure the backend is running.', 'error');
        console.error('Error:', error);
    } finally {
        this.disabled = false;
        this.innerHTML = '🚀 Generate Portfolio';
    }
});

// Download Excel
downloadBtn.addEventListener('click', function() {
    if (!currentFilename) return;
    window.location.href = `${API_URL}/api/download/${currentFilename}`;
});

// Download JSON
downloadJsonBtn.addEventListener('click', function() {
    if (!portfolioData) return;
    const json = JSON.stringify(portfolioData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio_${currentStrategy}_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
});

// Print report
printBtn.addEventListener('click', function() {
    window.print();
});

// Display results
function displayResults(data) {
    const portfolio = data.portfolio;
    
    resultsDiv.style.display = 'block';
    
    // Update summary
    totalValue.textContent = `$${data.total_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    totalStocks.textContent = data.total_stocks;
    strategyName.textContent = data.strategy_name;
    topHolding.textContent = data.top_holding ? `${data.top_holding.symbol} (${(data.top_holding.allocation * 100).toFixed(1)}%)` : '-';
    
    // Update table
    tableBody.innerHTML = '';
    
    portfolio.forEach((stock, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${stock.symbol}</strong></td>
            <td>$${stock.price.toFixed(2)}</td>
            <td>${stock.shares.toLocaleString()}</td>
            <td>${(stock.allocation * 100).toFixed(2)}%</td>
            <td>$${stock.position_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            <td><button class="trade-btn" data-symbol="${stock.symbol}">Trade</button></td>
        `;
        tableBody.appendChild(row);
    });
    
    // Add trade button listeners
    document.querySelectorAll('.trade-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            alert(`🚀 Trading ${this.dataset.symbol} - Feature coming soon!`);
        });
    });
    
    // Create pie chart
    createPieChart(portfolio);
}

// Create pie chart
function createPieChart(portfolio) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    
    if (pieChart) {
        pieChart.destroy();
    }
    
    const labels = portfolio.slice(0, 10).map(s => s.symbol);
    const data = portfolio.slice(0, 10).map(s => s.position_value);
    const colors = [
        '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
        '#00f2fe', '#43e97b', '#38f9d7', '#f9ca24', '#f0932b'
    ];
    
    pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: 'white'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 16,
                        font: { size: 12, weight: '500' }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: $${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Set status
function setStatus(message, type = 'info') {
    statusText.innerHTML = message;
    statusDiv.className = 'status-box';
    if (type) {
        statusDiv.classList.add(type);
    }
}

// Check health
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/api/health`);
        if (response.ok) {
            setStatus('✅ Connected to server. Ready to generate portfolios.', 'success');
        } else {
            setStatus('⚠️ Server is running but returned unexpected response.', 'error');
        }
    } catch (error) {
        setStatus('❌ Cannot connect to server. Please start the backend with: python app.py', 'error');
    }
}

checkHealth();