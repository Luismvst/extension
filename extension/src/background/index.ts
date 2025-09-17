import { ExtensionMessage, OrderStandard } from '@/common/types'
import { QueueManager } from '@/lib/queue'
import { StorageManager } from '@/lib/storage'

/**
 * Background service worker for Chrome extension
 */
class BackgroundService {
  private queueManager: QueueManager

  constructor() {
    this.queueManager = QueueManager.getInstance()
    this.setupMessageHandlers()
    this.setupAlarms()
  }

  /**
   * Setup message handlers for communication with other parts of the extension
   */
  private setupMessageHandlers(): void {
    chrome.runtime.onMessage.addListener((message: ExtensionMessage, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse)
      return true // Keep message channel open for async response
    })
  }

  /**
   * Handle incoming messages
   */
  private async handleMessage(
    message: ExtensionMessage,
    sender: chrome.runtime.MessageSender,
    sendResponse: (response?: any) => void
  ): Promise<void> {
    try {
      switch (message.type) {
        case 'GET_QUEUE':
          await this.handleGetQueue(sendResponse)
          break

        case 'ENQUEUE':
          await this.handleEnqueue(message.payload, sendResponse)
          break

        case 'CLEAR':
          await this.handleClear(sendResponse)
          break

        case 'EXPORT_CSV':
          await this.handleExportCSV(message.payload, sendResponse)
          break

        case 'GENERATE_TIPSA':
          await this.handleGenerateTIPSA(message.payload, sendResponse)
          break

        default:
          sendResponse({ error: 'Unknown message type' })
      }
    } catch (error) {
      console.error('Error handling message:', error)
      sendResponse({ error: error instanceof Error ? error.message : 'Unknown error' })
    }
  }

  /**
   * Handle GET_QUEUE message
   */
  private async handleGetQueue(sendResponse: (response: any) => void): Promise<void> {
    try {
      const orders = this.queueManager.getOrders()
      const stats = this.queueManager.getStats()
      
      sendResponse({
        orders,
        count: orders.length,
        stats
      })
    } catch (error) {
      sendResponse({ error: 'Failed to get queue' })
    }
  }

  /**
   * Handle ENQUEUE message
   */
  private async handleEnqueue(payload: any, sendResponse: (response: any) => void): Promise<void> {
    try {
      const { orders } = payload
      if (!Array.isArray(orders)) {
        sendResponse({ error: 'Invalid orders data' })
        return
      }

      await this.queueManager.addOrders(orders)
      sendResponse({ success: true, count: orders.length })
    } catch (error) {
      sendResponse({ error: 'Failed to enqueue orders' })
    }
  }

  /**
   * Handle CLEAR message
   */
  private async handleClear(sendResponse: (response: any) => void): Promise<void> {
    try {
      await this.queueManager.clearAll()
      sendResponse({ success: true })
    } catch (error) {
      sendResponse({ error: 'Failed to clear queue' })
    }
  }

  /**
   * Handle EXPORT_CSV message
   */
  private async handleExportCSV(payload: any, sendResponse: (response: any) => void): Promise<void> {
    try {
      const { url, marketplace } = payload
      
      // This would typically involve fetching the CSV from the URL
      // For now, we'll just acknowledge the request
      console.log(`Export CSV requested for ${marketplace} from ${url}`)
      
      sendResponse({ success: true, message: 'CSV export initiated' })
    } catch (error) {
      sendResponse({ error: 'Failed to export CSV' })
    }
  }

  /**
   * Handle GENERATE_TIPSA message
   */
  private async handleGenerateTIPSA(payload: any, sendResponse: (response: any) => void): Promise<void> {
    try {
      const { orders, format = 'csv' } = payload
      
      if (!Array.isArray(orders)) {
        sendResponse({ error: 'Invalid orders data' })
        return
      }

      // Import TIPSA mapper dynamically to avoid circular dependencies
      const { generateTIPSACSV } = await import('@/mappers/tipsa')
      
      if (format === 'csv') {
        const csvContent = generateTIPSACSV(orders)
        sendResponse({ success: true, data: csvContent, format: 'csv' })
      } else {
        sendResponse({ error: 'Unsupported format' })
      }
    } catch (error) {
      sendResponse({ error: 'Failed to generate TIPSA CSV' })
    }
  }

  /**
   * Setup periodic alarms for maintenance tasks
   */
  private setupAlarms(): void {
    // Cleanup old data every 24 hours
    chrome.alarms.create('cleanup', { periodInMinutes: 24 * 60 })
    
    chrome.alarms.onAlarm.addListener((alarm) => {
      if (alarm.name === 'cleanup') {
        this.performCleanup()
      }
    })
  }

  /**
   * Perform periodic cleanup tasks
   */
  private async performCleanup(): Promise<void> {
    try {
      // Cleanup old orders (older than 7 days)
      await this.queueManager.cleanupOldOrders(7)
      
      // Check storage quota
      const isQuotaExceeded = await StorageManager.isStorageQuotaExceeded()
      if (isQuotaExceeded) {
        console.warn('Storage quota exceeded, performing cleanup')
        await StorageManager.cleanupOldData()
      }
      
      console.log('Background cleanup completed')
    } catch (error) {
      console.error('Error during background cleanup:', error)
    }
  }

  /**
   * Handle extension installation
   */
  private handleInstall(): void {
    chrome.runtime.onInstalled.addListener((details) => {
      if (details.reason === 'install') {
        console.log('Extension installed')
        // Initialize default settings
        this.initializeDefaultSettings()
      } else if (details.reason === 'update') {
        console.log('Extension updated')
        // Handle update logic if needed
      }
    })
  }

  /**
   * Initialize default settings
   */
  private async initializeDefaultSettings(): Promise<void> {
    try {
      const defaultSettings = {
        autoExport: false,
        defaultService: 'ESTANDAR',
        cleanupDays: 7,
        notifications: true
      }
      
      await StorageManager.setSettings(defaultSettings)
      console.log('Default settings initialized')
    } catch (error) {
      console.error('Failed to initialize default settings:', error)
    }
  }
}

// Initialize background service
const backgroundService = new BackgroundService()

// Handle extension lifecycle events
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Extension installed')
  } else if (details.reason === 'update') {
    console.log('Extension updated')
  }
})

// Handle extension startup
chrome.runtime.onStartup.addListener(() => {
  console.log('Extension started')
})

// Handle extension suspend
chrome.runtime.onSuspend.addListener(() => {
  console.log('Extension suspended')
})
