import { OrderStandard, STORAGE_KEYS } from '@/common/types'

/**
 * Light obfuscation for sensitive data
 */
function obfuscateData(data: any): any {
  if (typeof data === 'string') {
    // Simple obfuscation - replace middle characters with *
    if (data.length > 4) {
      const start = data.substring(0, 2)
      const end = data.substring(data.length - 2)
      const middle = '*'.repeat(Math.max(0, data.length - 4))
      return `${start}${middle}${end}`
    }
    return data
  }
  
  if (typeof data === 'object' && data !== null) {
    const obfuscated = { ...data }
    // Obfuscate specific fields
    if (obfuscated.email) {
      obfuscated.email = obfuscateData(obfuscated.email)
    }
    if (obfuscated.phone) {
      obfuscated.phone = obfuscateData(obfuscated.phone)
    }
    if (obfuscated.name) {
      obfuscated.name = obfuscateData(obfuscated.name)
    }
    return obfuscated
  }
  
  return data
}

/**
 * Deobfuscate data (for display purposes)
 */
function deobfuscateData(data: any): any {
  // In a real implementation, you'd store the original data
  // For now, we'll just return the obfuscated data
  return data
}

/**
 * Storage wrapper with obfuscation
 */
export class StorageManager {
  /**
   * Get data from Chrome storage
   */
  static async get<T = any>(key: string): Promise<T | null> {
    try {
      const result = await chrome.storage.local.get([key])
      return result[key] || null
    } catch (error) {
      console.error('Failed to get data from storage:', error)
      return null
    }
  }

  /**
   * Set data in Chrome storage
   */
  static async set(key: string, value: any): Promise<void> {
    try {
      await chrome.storage.local.set({ [key]: value })
    } catch (error) {
      console.error('Failed to set data in storage:', error)
      throw error
    }
  }

  /**
   * Remove data from Chrome storage
   */
  static async remove(key: string): Promise<void> {
    try {
      await chrome.storage.local.remove([key])
    } catch (error) {
      console.error('Failed to remove data from storage:', error)
      throw error
    }
  }

  /**
   * Clear all storage
   */
  static async clear(): Promise<void> {
    try {
      await chrome.storage.local.clear()
    } catch (error) {
      console.error('Failed to clear storage:', error)
      throw error
    }
  }

  /**
   * Get orders queue
   */
  static async getOrdersQueue(): Promise<OrderStandard[]> {
    const orders = await this.get<OrderStandard[]>(STORAGE_KEYS.ORDERS_QUEUE)
    return orders || []
  }

  /**
   * Set orders queue
   */
  static async setOrdersQueue(orders: OrderStandard[]): Promise<void> {
    // Obfuscate sensitive data before storing
    const obfuscatedOrders = orders.map(order => ({
      ...order,
      buyer: obfuscateData(order.buyer),
      shipping: obfuscateData(order.shipping)
    }))
    
    await this.set(STORAGE_KEYS.ORDERS_QUEUE, obfuscatedOrders)
  }

  /**
   * Add orders to queue
   */
  static async addOrdersToQueue(newOrders: OrderStandard[]): Promise<void> {
    const existingOrders = await this.getOrdersQueue()
    const allOrders = [...existingOrders, ...newOrders]
    await this.setOrdersQueue(allOrders)
  }

  /**
   * Clear orders queue
   */
  static async clearOrdersQueue(): Promise<void> {
    await this.remove(STORAGE_KEYS.ORDERS_QUEUE)
  }

  /**
   * Get extension settings
   */
  static async getSettings(): Promise<Record<string, any>> {
    const settings = await this.get<Record<string, any>>(STORAGE_KEYS.SETTINGS)
    return settings || {}
  }

  /**
   * Set extension settings
   */
  static async setSettings(settings: Record<string, any>): Promise<void> {
    await this.set(STORAGE_KEYS.SETTINGS, settings)
  }

  /**
   * Get last sync timestamp
   */
  static async getLastSync(): Promise<number | null> {
    return await this.get<number>(STORAGE_KEYS.LAST_SYNC)
  }

  /**
   * Set last sync timestamp
   */
  static async setLastSync(timestamp: number): Promise<void> {
    await this.set(STORAGE_KEYS.LAST_SYNC, timestamp)
  }

  /**
   * Get storage usage info
   */
  static async getStorageInfo(): Promise<chrome.storage.StorageArea> {
    try {
      return await chrome.storage.local.getBytesInUse()
    } catch (error) {
      console.error('Failed to get storage info:', error)
      return 0
    }
  }

  /**
   * Check if storage quota is exceeded
   */
  static async isStorageQuotaExceeded(): Promise<boolean> {
    try {
      const quota = chrome.storage.local.QUOTA_BYTES || 5242880 // 5MB default
      const used = await this.getStorageInfo()
      return used > quota * 0.9 // 90% threshold
    } catch (error) {
      console.error('Failed to check storage quota:', error)
      return false
    }
  }

  /**
   * Cleanup old data to free space
   */
  static async cleanupOldData(): Promise<void> {
    try {
      const orders = await this.getOrdersQueue()
      const lastSync = await this.getLastSync()
      const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000)
      
      // Remove orders older than 1 week
      const recentOrders = orders.filter(order => {
        const orderDate = new Date(order.createdAt).getTime()
        return orderDate > oneWeekAgo
      })
      
      if (recentOrders.length < orders.length) {
        await this.setOrdersQueue(recentOrders)
        console.log(`Cleaned up ${orders.length - recentOrders.length} old orders`)
      }
    } catch (error) {
      console.error('Failed to cleanup old data:', error)
    }
  }
}
