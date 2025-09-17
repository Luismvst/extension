import { ExtensionMessage, QueueResponse, ExportCSVPayload, GenerateTIPSAPayload } from './types'

/**
 * Message types for communication between extension components
 */
export const MESSAGE_TYPES = {
  GET_QUEUE: 'GET_QUEUE',
  ENQUEUE: 'ENQUEUE',
  CLEAR: 'CLEAR',
  EXPORT_CSV: 'EXPORT_CSV',
  GENERATE_TIPSA: 'GENERATE_TIPSA'
} as const

/**
 * Send message to background script
 */
export async function sendMessage<T = any>(
  message: ExtensionMessage
): Promise<T> {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(message, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message))
        return
      }
      resolve(response)
    })
  })
}

/**
 * Send message to content script
 */
export async function sendMessageToTab<T = any>(
  tabId: number,
  message: ExtensionMessage
): Promise<T> {
  return new Promise((resolve, reject) => {
    chrome.tabs.sendMessage(tabId, message, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message))
        return
      }
      resolve(response)
    })
  })
}

/**
 * Get orders queue from background script
 */
export async function getQueue(): Promise<QueueResponse> {
  return sendMessage<QueueResponse>({
    type: 'GET_QUEUE'
  })
}

/**
 * Add orders to queue
 */
export async function enqueueOrders(orders: any[]): Promise<void> {
  return sendMessage({
    type: 'ENQUEUE',
    payload: { orders }
  })
}

/**
 * Clear orders queue
 */
export async function clearQueue(): Promise<void> {
  return sendMessage({
    type: 'CLEAR'
  })
}

/**
 * Export CSV from current page
 */
export async function exportCSV(url: string, marketplace: string): Promise<void> {
  return sendMessage({
    type: 'EXPORT_CSV',
    payload: { url, marketplace } as ExportCSVPayload
  })
}

/**
 * Generate TIPSA CSV
 */
export async function generateTIPSA(
  orders: any[],
  format: 'csv' | 'json' = 'csv'
): Promise<string> {
  return sendMessage<string>({
    type: 'GENERATE_TIPSA',
    payload: { orders, format } as GenerateTIPSAPayload
  })
}

/**
 * Listen for messages from other parts of the extension
 */
export function addMessageListener(
  callback: (message: ExtensionMessage, sender: chrome.runtime.MessageSender) => void
): void {
  chrome.runtime.onMessage.addListener(callback)
}

/**
 * Remove message listener
 */
export function removeMessageListener(
  callback: (message: ExtensionMessage, sender: chrome.runtime.MessageSender) => void
): void {
  chrome.runtime.onMessage.removeListener(callback)
}
