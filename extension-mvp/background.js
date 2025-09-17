// Background script for Mirakl CSV Extension MVP
console.log('Mirakl CSV Extension MVP background script loaded');

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request);
  
  if (request.action === 'processCSV') {
    try {
      // Process CSV data
      const processedData = processMiraklCSV(request.csvData);
      sendResponse({ success: true, data: processedData });
    } catch (error) {
      console.error('Error processing CSV:', error);
      sendResponse({ success: false, error: error.message });
    }
  }
  
  if (request.action === 'generateTipsaCSV') {
    try {
      const tipsaCSV = generateTipsaCSV(request.orders);
      sendResponse({ success: true, csv: tipsaCSV });
    } catch (error) {
      console.error('Error generating TIPSA CSV:', error);
      sendResponse({ success: false, error: error.message });
    }
  }
  
  if (request.action === 'getOrders') {
    chrome.storage.local.get(['processedOrders'], (result) => {
      sendResponse({ success: true, orders: result.processedOrders || [] });
    });
    return true; // Keep message channel open
  }
  
  return true; // Keep message channel open for async response
});

// Process Mirakl CSV data
function processMiraklCSV(csvData) {
  const lines = csvData.split('\n');
  const headers = lines[0].split(',');
  const orders = [];
  
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim()) {
      const values = lines[i].split(',');
      const order = {
        orderId: values[0] || '',
        orderDate: values[1] || '',
        status: values[2] || '',
        sku: values[3] || '',
        product: values[4] || '',
        qty: parseInt(values[5]) || 0,
        price: parseFloat(values[6]) || 0,
        buyerName: values[7] || '',
        buyerEmail: values[8] || '',
        phone: values[9] || '',
        shipTo: values[10] || '',
        address1: values[11] || '',
        address2: values[12] || '',
        city: values[13] || '',
        postalCode: values[14] || '',
        country: values[15] || '',
        total: parseFloat(values[16]) || 0
      };
      orders.push(order);
    }
  }
  
  return orders;
}

// Generate TIPSA CSV format
function generateTipsaCSV(orders) {
  const headers = 'destinatario;direccion;cp;poblacion;pais;contacto;telefono;email;referencia;peso;servicio';
  const rows = orders.map(order => {
    const address = `${order.address1}${order.address2 ? ', ' + order.address2 : ''}`;
    const peso = Math.max(0.5, order.qty * 0.3); // Estimate weight
    
    return [
      order.shipTo || order.buyerName,
      address,
      order.postalCode,
      order.city,
      order.country,
      order.buyerName,
      order.phone,
      order.buyerEmail,
      order.orderId,
      peso.toFixed(1),
      'ESTANDAR'
    ].join(';');
  });
  
  return [headers, ...rows].join('\n');
}
