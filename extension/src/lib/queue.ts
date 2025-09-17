import { OrderStandard } from '@/common/types'
import { StorageManager } from './storage'

/**
 * Queue manager for handling orders
 */
export class QueueManager {
  private static instance: QueueManager
  private orders: OrderStandard[] = []
  private listeners: Array<(orders: OrderStandard[]) => void> = []

  private constructor() {
    this.loadOrders()
  }

  /**
   * Get singleton instance
   */
  static getInstance(): QueueManager {
    if (!QueueManager.instance) {
      QueueManager.instance = new QueueManager()
    }
    return QueueManager.instance
  }

  /**
   * Load orders from storage
   */
  private async loadOrders(): Promise<void> {
    try {
      this.orders = await StorageManager.getOrdersQueue()
      this.notifyListeners()
    } catch (error) {
      console.error('Failed to load orders from storage:', error)
    }
  }

  /**
   * Save orders to storage
   */
  private async saveOrders(): Promise<void> {
    try {
      await StorageManager.setOrdersQueue(this.orders)
    } catch (error) {
      console.error('Failed to save orders to storage:', error)
    }
  }

  /**
   * Add orders to queue
   */
  async addOrders(orders: OrderStandard[]): Promise<void> {
    try {
      // Filter out duplicates based on orderId
      const existingIds = new Set(this.orders.map(o => o.orderId))
      const newOrders = orders.filter(order => !existingIds.has(order.orderId))
      
      this.orders = [...this.orders, ...newOrders]
      await this.saveOrders()
      this.notifyListeners()
      
      console.log(`Added ${newOrders.length} new orders to queue`)
    } catch (error) {
      console.error('Failed to add orders to queue:', error)
      throw error
    }
  }

  /**
   * Get all orders in queue
   */
  getOrders(): OrderStandard[] {
    return [...this.orders]
  }

  /**
   * Get orders by status
   */
  getOrdersByStatus(status: OrderStandard['status']): OrderStandard[] {
    return this.orders.filter(order => order.status === status)
  }

  /**
   * Get order by ID
   */
  getOrderById(orderId: string): OrderStandard | undefined {
    return this.orders.find(order => order.orderId === orderId)
  }

  /**
   * Update order status
   */
  async updateOrderStatus(orderId: string, status: OrderStandard['status']): Promise<void> {
    try {
      const order = this.getOrderById(orderId)
      if (order) {
        order.status = status
        await this.saveOrders()
        this.notifyListeners()
      }
    } catch (error) {
      console.error('Failed to update order status:', error)
      throw error
    }
  }

  /**
   * Remove order from queue
   */
  async removeOrder(orderId: string): Promise<void> {
    try {
      this.orders = this.orders.filter(order => order.orderId !== orderId)
      await this.saveOrders()
      this.notifyListeners()
    } catch (error) {
      console.error('Failed to remove order from queue:', error)
      throw error
    }
  }

  /**
   * Clear all orders
   */
  async clearAll(): Promise<void> {
    try {
      this.orders = []
      await StorageManager.clearOrdersQueue()
      this.notifyListeners()
    } catch (error) {
      console.error('Failed to clear orders queue:', error)
      throw error
    }
  }

  /**
   * Get queue statistics
   */
  getStats(): {
    total: number
    byStatus: Record<OrderStandard['status'], number>
    oldestOrder?: Date
    newestOrder?: Date
  } {
    const stats = {
      total: this.orders.length,
      byStatus: {
        PENDING: 0,
        ACCEPTED: 0,
        SHIPPED: 0,
        DELIVERED: 0,
        CANCELLED: 0
      } as Record<OrderStandard['status'], number>,
      oldestOrder: undefined as Date | undefined,
      newestOrder: undefined as Date | undefined
    }

    if (this.orders.length === 0) {
      return stats
    }

    // Count by status
    this.orders.forEach(order => {
      stats.byStatus[order.status]++
    })

    // Find oldest and newest orders
    const dates = this.orders.map(order => new Date(order.createdAt))
    stats.oldestOrder = new Date(Math.min(...dates.map(d => d.getTime())))
    stats.newestOrder = new Date(Math.max(...dates.map(d => d.getTime())))

    return stats
  }

  /**
   * Add listener for queue changes
   */
  addListener(listener: (orders: OrderStandard[]) => void): void {
    this.listeners.push(listener)
  }

  /**
   * Remove listener
   */
  removeListener(listener: (orders: OrderStandard[]) => void): void {
    this.listeners = this.listeners.filter(l => l !== listener)
  }

  /**
   * Notify all listeners
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener([...this.orders])
      } catch (error) {
        console.error('Error in queue listener:', error)
      }
    })
  }

  /**
   * Export orders to JSON
   */
  exportToJSON(): string {
    return JSON.stringify(this.orders, null, 2)
  }

  /**
   * Import orders from JSON
   */
  async importFromJSON(jsonData: string): Promise<void> {
    try {
      const orders = JSON.parse(jsonData) as OrderStandard[]
      await this.addOrders(orders)
    } catch (error) {
      console.error('Failed to import orders from JSON:', error)
      throw error
    }
  }

  /**
   * Cleanup old orders (older than specified days)
   */
  async cleanupOldOrders(daysOld: number = 7): Promise<void> {
    try {
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - daysOld)
      
      const recentOrders = this.orders.filter(order => {
        const orderDate = new Date(order.createdAt)
        return orderDate > cutoffDate
      })
      
      if (recentOrders.length < this.orders.length) {
        this.orders = recentOrders
        await this.saveOrders()
        this.notifyListeners()
        console.log(`Cleaned up ${this.orders.length - recentOrders.length} old orders`)
      }
    } catch (error) {
      console.error('Failed to cleanup old orders:', error)
      throw error
    }
  }
}
