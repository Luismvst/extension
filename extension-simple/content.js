// Content script for Mirakl CSV Extension
console.log('Mirakl CSV Extension content script loaded');

// Function to intercept CSV exports
function interceptCSVExports() {
  // Look for CSV export buttons/links
  const exportButtons = document.querySelectorAll('a[href*="export"], button[onclick*="export"], a[href*="csv"], button[onclick*="csv"]');
  
  exportButtons.forEach(button => {
    // Add click listener
    button.addEventListener('click', async (event) => {
      console.log('CSV export button clicked:', button);
      
      // Prevent default action
      event.preventDefault();
      
      // Try to get CSV data
      try {
        const csvData = await fetchCSVData(button);
        if (csvData) {
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
              // Show notification
              showNotification('CSV procesado correctamente. Ve al popup para generar el archivo TIPSA.');
            } else {
              console.error('Error processing CSV:', response?.error);
              showNotification('Error procesando CSV: ' + (response?.error || 'Error desconocido'));
            }
          });
        }
      } catch (error) {
        console.error('Error intercepting CSV:', error);
        showNotification('Error intercepting CSV: ' + error.message);
      }
    });
  });
}

// Function to fetch CSV data
async function fetchCSVData(button) {
  try {
    // Try to get href or onclick attribute
    let url = button.href || button.getAttribute('onclick');
    
    if (url && url.includes('export')) {
      // Clean up onclick URL
      if (url.includes('onclick')) {
        const match = url.match(/['"]([^'"]*export[^'"]*)['"]/);
        if (match) {
          url = match[1];
        }
      }
      
      // Make sure it's a full URL
      if (url.startsWith('/')) {
        url = window.location.origin + url;
      }
      
      console.log('Fetching CSV from:', url);
      const response = await fetch(url);
      const csvData = await response.text();
      return csvData;
    }
  } catch (error) {
    console.error('Error fetching CSV:', error);
  }
  
  return null;
}

// Function to show notification
function showNotification(message) {
  // Create notification element
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 15px 20px;
    border-radius: 5px;
    z-index: 10000;
    font-family: Arial, sans-serif;
    font-size: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    max-width: 300px;
  `;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
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
