// Popup script for Mirakl CSV Extension MVP
console.log('Mirakl CSV Extension MVP popup script loaded');

let processedOrders = [];
let tipsaCSV = '';

// DOM elements
const statusText = document.getElementById('status-text');
const lastProcessed = document.getElementById('last-processed');
const ordersSection = document.getElementById('orders-section');
const noOrdersSection = document.getElementById('no-orders-section');
const ordersList = document.getElementById('orders-list');
const generateTipsaBtn = document.getElementById('generate-tipsa');
const downloadTipsaBtn = document.getElementById('download-tipsa');

// Initialize popup
document.addEventListener('DOMContentLoaded', () => {
    loadProcessedOrders();
    setupEventListeners();
});

// Load processed orders from storage
function loadProcessedOrders() {
    chrome.storage.local.get(['processedOrders', 'lastProcessed'], (result) => {
        if (result.processedOrders && result.processedOrders.length > 0) {
            processedOrders = result.processedOrders;
            updateUI();
        } else {
            showNoOrders();
        }
    });
}

// Update UI based on current state
function updateUI() {
    if (processedOrders.length > 0) {
        showOrders();
        updateOrdersList();
        updateStatus(`✅ ${processedOrders.length} pedidos procesados`);
    } else {
        showNoOrders();
    }
}

// Show orders section
function showOrders() {
    ordersSection.style.display = 'block';
    noOrdersSection.style.display = 'none';
}

// Show no orders section
function showNoOrders() {
    ordersSection.style.display = 'none';
    noOrdersSection.style.display = 'block';
    updateStatus('❌ No hay pedidos procesados');
}

// Update orders list
function updateOrdersList() {
    ordersList.innerHTML = '';
    
    processedOrders.forEach((order, index) => {
        const orderDiv = document.createElement('div');
        orderDiv.className = 'order-item';
        orderDiv.innerHTML = `
            <div class="order-id">${order.orderId}</div>
            <div>${order.buyerName} - ${order.city}</div>
            <div>Total: €${order.total.toFixed(2)}</div>
        `;
        ordersList.appendChild(orderDiv);
    });
}

// Update status text
function updateStatus(text) {
    statusText.textContent = text;
}

// Setup event listeners
function setupEventListeners() {
    generateTipsaBtn.addEventListener('click', generateTipsaCSV);
    downloadTipsaBtn.addEventListener('click', downloadTipsaCSV);
}

// Generate TIPSA CSV
function generateTipsaCSV() {
    generateTipsaBtn.disabled = true;
    generateTipsaBtn.textContent = '⏳ Generando...';
    
    // Send to background script
    chrome.runtime.sendMessage({
        action: 'generateTipsaCSV',
        orders: processedOrders
    }, (response) => {
        if (response && response.success) {
            tipsaCSV = response.csv;
            generateTipsaBtn.textContent = '✅ CSV TIPSA Generado';
            downloadTipsaBtn.disabled = false;
            updateStatus('✅ CSV TIPSA generado correctamente');
        } else {
            generateTipsaBtn.textContent = '❌ Error';
            updateStatus('❌ Error generando CSV TIPSA: ' + (response?.error || 'Error desconocido'));
        }
    });
}

// Download TIPSA CSV
function downloadTipsaCSV() {
    if (!tipsaCSV) {
        updateStatus('❌ No hay CSV TIPSA generado');
        return;
    }
    
    // Create blob and download
    const blob = new Blob([tipsaCSV], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `tipsa_orders_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    updateStatus('✅ CSV TIPSA descargado');
}
