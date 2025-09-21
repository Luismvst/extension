console.log('Mirakl Tipsa MVP background script loaded');
console.log('BG SENTINEL be482d9 2025-09-21T12:30:50Z v0.2.20250921124005');

chrome.runtime.onInstalled.addListener((details) => {
  console.log('Extension installed/updated:', details.reason);
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message);
  
  switch (message.type) {
    case 'FETCH_ORDERS':
      sendResponse({ success: true, data: [{ order_id: 'MIR-001', status: 'PENDING' }] });
      break;
    case 'CREATE_SHIPMENTS':
      sendResponse({ success: true, data: [{ shipment_id: 'TIPSA-001', tracking: '1Z123456789' }] });
      break;
    case 'UPLOAD_TRACKING':
      sendResponse({ success: true, data: { message: 'Tracking uploaded' } });
      break;
    default:
      sendResponse({ success: false, error: 'Unknown message type' });
  }
  
  return true;
});
