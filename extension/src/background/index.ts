/**
 * Background service worker for the Chrome extension.
 * 
 * This script handles background tasks, message passing between components,
 * and manages the extension's lifecycle.
 */

// Initialize the background script
console.log('Mirakl Tipsa MVP background script loaded')

// BG SENTINEL for build verification
declare const BUILD_INFO: { commit: string; buildTime: string; buildNumber: string }
console.log('BG SENTINEL', BUILD_INFO.commit, BUILD_INFO.buildTime, 'v' + chrome.runtime.getManifest().version)

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  console.log('Extension installed/updated:', details.reason)
  
  if (details.reason === 'install') {
    // Open options page on first install
    chrome.runtime.openOptionsPage()
  }
})

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((
  message: any,
  sender: chrome.runtime.MessageSender,
  sendResponse: (response: any) => void
) => {
  console.log('Background received message:', message)

  switch (message.type) {
    case 'FETCH_ORDERS':
      handleFetchOrders(message.payload, sendResponse)
      break

    case 'CREATE_SHIPMENTS':
      handleCreateShipments(message.payload, sendResponse)
      break

    case 'UPLOAD_TRACKING':
      handleUploadTracking(message.payload, sendResponse)
      break

    case 'GET_LOGS':
      handleGetLogs(sendResponse)
      break

    default:
      sendResponse({
        success: false,
        error: 'Unknown message type'
      })
  }

  return true // Keep message channel open for async response
})

// Handle fetch orders request
async function handleFetchOrders(payload: any, sendResponse: (response: any) => void) {
  try {
    // This would typically make an API call to the backend
    // For now, we'll just return a mock response
    const mockOrders = [
      {
        order_id: 'MIR-001',
        marketplace: 'mirakl',
        status: 'SHIPPING',
        customer_name: 'John Doe',
        weight: 2.5,
        total_amount: 45.99
      },
      {
        order_id: 'MIR-002',
        marketplace: 'mirakl',
        status: 'SHIPPING',
        customer_name: 'Jane Smith',
        weight: 1.8,
        total_amount: 32.50
      }
    ]

    sendResponse({
      success: true,
      data: mockOrders
    })
  } catch (error) {
    console.error('Error fetching orders:', error)
    sendResponse({
      success: false,
      error: 'Failed to fetch orders'
    })
  }
}

// Handle create shipments request
async function handleCreateShipments(payload: any, sendResponse: (response: any) => void) {
  try {
    // This would typically make an API call to create shipments
    // For now, we'll just return a mock response
    const mockShipments = [
      {
        order_id: 'MIR-001',
        shipment_id: 'TIPSA-001',
        tracking_number: '1Z123456789',
        status: 'CREATED',
        label_url: 'https://mock.tipsa.com/label/001'
      },
      {
        order_id: 'MIR-002',
        shipment_id: 'TIPSA-002',
        tracking_number: '1Z123456790',
        status: 'CREATED',
        label_url: 'https://mock.tipsa.com/label/002'
      }
    ]

    sendResponse({
      success: true,
      data: mockShipments
    })
  } catch (error) {
    console.error('Error creating shipments:', error)
    sendResponse({
      success: false,
      error: 'Failed to create shipments'
    })
  }
}

// Handle upload tracking request
async function handleUploadTracking(payload: any, sendResponse: (response: any) => void) {
  try {
    // This would typically make an API call to upload tracking
    // For now, we'll just return a success response
    sendResponse({
      success: true,
      data: { message: 'Tracking uploaded successfully' }
    })
  } catch (error) {
    console.error('Error uploading tracking:', error)
    sendResponse({
      success: false,
      error: 'Failed to upload tracking'
    })
  }
}

// Handle get logs request
async function handleGetLogs(sendResponse: (response: any) => void) {
  try {
    // This would typically fetch logs from the backend
    // For now, we'll return empty logs
    sendResponse({
      success: true,
      data: { logs: [] }
    })
  } catch (error) {
    console.error('Error getting logs:', error)
    sendResponse({
      success: false,
      error: 'Failed to get logs'
    })
  }
}

// Handle tab updates to inject content script on TIPSA websites
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    const url = new URL(tab.url)
    
    // Check if it's a TIPSA website
    if (url.hostname.includes('tip-sa.com') || url.hostname.includes('tipsa')) {
      console.log('TIPSA website detected, injecting content script')
      
      // Inject the content script
      chrome.scripting.executeScript({
        target: { tabId },
        files: ['content/index.js']
      }).catch((error) => {
        console.error('Failed to inject content script:', error)
      })
    }
  }
})

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'inject-orchestrator' && tab?.id) {
    // Send message to content script to inject overlay
    chrome.tabs.sendMessage(tab.id, {
      type: 'INJECT_OVERLAY'
    })
  }
})

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'inject-orchestrator',
    title: 'Inject Mirakl Tipsa MVP',
    contexts: ['page']
  })
})

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  if (tab.id) {
    // Send message to content script to toggle overlay
    chrome.tabs.sendMessage(tab.id, {
      type: 'INJECT_OVERLAY'
    }).catch((error) => {
      console.error('Failed to send message to content script:', error)
      // If content script is not available, open popup
      chrome.action.openPopup()
    })
  }
})

// Keep service worker alive
chrome.runtime.onStartup.addListener(() => {
  console.log('Extension startup')
})

// Handle extension suspension
chrome.runtime.onSuspend.addListener(() => {
  console.log('Extension suspended')
})