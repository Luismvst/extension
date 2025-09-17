// Content script for Mirakl CSV Extension MVP
console.log('Mirakl CSV Extension MVP content script loaded');

// Function to intercept CSV exports
function interceptCSVExports() {
  // Look for CSV export buttons/links
  const exportSelectors = [
    'a[href*="export"]',
    'a[href*="csv"]',
    'button[data-export]',
    'button[data-csv]',
    'button[data-export-csv]',
    'a[data-export-csv]',
    '.export-button',
    '.csv-export'
  ];
  
  exportSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
      if (!element.hasAttribute('data-mirakl-hooked')) {
        element.setAttribute('data-mirakl-hooked', 'true');
        element.addEventListener('click', handleExportClick);
      }
    });
  });
}

// Handle export button/link click
async function handleExportClick(event) {
  try {
    console.log('CSV export intercepted:', event.target);
    
    // Prevent default action
    event.preventDefault();
    event.stopPropagation();
    
    // Show loading indicator
    showLoadingIndicator();
    
    // Extract CSV URL
    const csvUrl = extractCSVUrl(event.target);
    if (!csvUrl) {
      throw new Error('Could not extract CSV URL from element');
    }
    
    // Fetch CSV data
    const csvData = await fetchCSVData(csvUrl);
    if (!csvData) {
      throw new Error('Failed to fetch CSV data');
    }
    
    // Send to background script
    chrome.runtime.sendMessage({
      action: 'processCSV',
      csvData: csvData
    }, (response) => {
      if (response && response.success) {
        console.log('CSV processed successfully:', response.data);
        // Store processed data
        chrome.storage.local.set({ 
          processedOrders: response.data,
          lastProcessed: new Date().toISOString()
        });
        // Show success notification
        showSuccessNotification(response.data.length);
      } else {
        console.error('Error processing CSV:', response?.error);
        showErrorNotification('Error procesando CSV: ' + (response?.error || 'Error desconocido'));
      }
    });
    
  } catch (error) {
    console.error('Error intercepting CSV:', error);
    showErrorNotification('Error intercepting CSV: ' + error.message);
  } finally {
    hideLoadingIndicator();
  }
}

// Extract CSV URL from element
function extractCSVUrl(element) {
  // Try different methods to extract URL
  if (element instanceof HTMLAnchorElement) {
    return element.href;
  }
  
  if (element instanceof HTMLButtonElement) {
    // Check data attributes
    const url = element.dataset.url || element.dataset.href || element.dataset.csvUrl;
    if (url) return url;
    
    // Check if button has onclick handler with URL
    const onclick = element.getAttribute('onclick');
    if (onclick) {
      const urlMatch = onclick.match(/['"]([^'"]*\.csv[^'"]*)['"]/);
      if (urlMatch) return urlMatch[1];
    }
  }
  
  // Look for nearby elements that might contain the URL
  const parent = element.closest('form, .export-container, .csv-container');
  if (parent) {
    const urlInput = parent.querySelector('input[type="hidden"][name*="url"], input[type="hidden"][name*="csv"]');
    if (urlInput instanceof HTMLInputElement) {
      return urlInput.value;
    }
  }
  
  return null;
}

// Fetch CSV data from URL
async function fetchCSVData(url) {
  try {
    // Make URL absolute if relative
    const absoluteUrl = url.startsWith('http') ? url : new URL(url, window.location.origin).href;
    
    console.log('Fetching CSV from:', absoluteUrl);
    const response = await fetch(absoluteUrl, {
      method: 'GET',
      credentials: 'include', // Include cookies for authentication
      headers: {
        'Accept': 'text/csv,application/csv,text/plain,*/*',
        'User-Agent': navigator.userAgent
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch CSV: ${response.status} ${response.statusText}`);
    }
    
    const csvData = await response.text();
    if (!csvData.trim()) {
      throw new Error('CSV file is empty');
    }
    
    return csvData;
  } catch (error) {
    console.error('Error fetching CSV:', error);
    throw error;
  }
}

// Show loading indicator
function showLoadingIndicator() {
  const indicator = document.createElement('div');
  indicator.className = 'mirakl-loading-indicator';
  indicator.innerHTML = '⏳ Processing CSV...';
  indicator.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #3b82f6;
    color: white;
    padding: 10px 15px;
    border-radius: 5px;
    z-index: 10000;
    font-family: Arial, sans-serif;
    font-size: 14px;
  `;
  document.body.appendChild(indicator);
}

// Hide loading indicator
function hideLoadingIndicator() {
  const indicator = document.querySelector('.mirakl-loading-indicator');
  if (indicator) {
    indicator.remove();
  }
}

// Show success notification
function showSuccessNotification(count) {
  const notification = document.createElement('div');
  notification.className = 'mirakl-success-notification';
  notification.innerHTML = `✅ ${count} orders imported successfully!`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #10b981;
    color: white;
    padding: 10px 15px;
    border-radius: 5px;
    z-index: 10000;
    font-family: Arial, sans-serif;
    font-size: 14px;
  `;
  document.body.appendChild(notification);
  
  // Auto-remove after 3 seconds
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

// Show error notification
function showErrorNotification(message) {
  const notification = document.createElement('div');
  notification.className = 'mirakl-error-notification';
  notification.innerHTML = `❌ Error: ${message}`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #ef4444;
    color: white;
    padding: 10px 15px;
    border-radius: 5px;
    z-index: 10000;
    font-family: Arial, sans-serif;
    font-size: 14px;
  `;
  document.body.appendChild(notification);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', interceptCSVExports);
} else {
  interceptCSVExports();
}

// Also run on page changes (for SPAs)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    setTimeout(interceptCSVExports, 1000);
  }
}).observe(document, { subtree: true, childList: true });
