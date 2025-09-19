/**
 * Chrome storage utilities for the extension.
 */

import { AppState, Order, ShipmentResult } from '@/types'

export class StorageManager {
  private static readonly KEYS = {
    AUTH_TOKEN: 'auth_token',
    USER_DATA: 'user_data',
    ORDERS: 'orders',
    SHIPMENTS: 'shipments',
    SETTINGS: 'settings'
  } as const

  // Authentication
  static async getAuthToken(): Promise<string | null> {
    const result = await chrome.storage.local.get([this.KEYS.AUTH_TOKEN])
    return result[this.KEYS.AUTH_TOKEN] || null
  }

  static async setAuthToken(token: string): Promise<void> {
    await chrome.storage.local.set({ [this.KEYS.AUTH_TOKEN]: token })
  }

  static async clearAuthToken(): Promise<void> {
    await chrome.storage.local.remove([this.KEYS.AUTH_TOKEN])
  }

  // User data
  static async getUserData(): Promise<any | null> {
    const result = await chrome.storage.local.get([this.KEYS.USER_DATA])
    return result[this.KEYS.USER_DATA] || null
  }

  static async setUserData(userData: any): Promise<void> {
    await chrome.storage.local.set({ [this.KEYS.USER_DATA]: userData })
  }

  static async clearUserData(): Promise<void> {
    await chrome.storage.local.remove([this.KEYS.USER_DATA])
  }

  // Orders
  static async getOrders(): Promise<Order[]> {
    const result = await chrome.storage.local.get([this.KEYS.ORDERS])
    return result[this.KEYS.ORDERS] || []
  }

  static async setOrders(orders: Order[]): Promise<void> {
    await chrome.storage.local.set({ [this.KEYS.ORDERS]: orders })
  }

  static async addOrder(order: Order): Promise<void> {
    const orders = await this.getOrders()
    const existingIndex = orders.findIndex(o => o.order_id === order.order_id)
    
    if (existingIndex >= 0) {
      orders[existingIndex] = order
    } else {
      orders.push(order)
    }
    
    await this.setOrders(orders)
  }

  static async removeOrder(orderId: string): Promise<void> {
    const orders = await this.getOrders()
    const filteredOrders = orders.filter(o => o.order_id !== orderId)
    await this.setOrders(filteredOrders)
  }

  static async clearOrders(): Promise<void> {
    await chrome.storage.local.remove([this.KEYS.ORDERS])
  }

  // Shipments
  static async getShipments(): Promise<ShipmentResult[]> {
    const result = await chrome.storage.local.get([this.KEYS.SHIPMENTS])
    return result[this.KEYS.SHIPMENTS] || []
  }

  static async setShipments(shipments: ShipmentResult[]): Promise<void> {
    await chrome.storage.local.set({ [this.KEYS.SHIPMENTS]: shipments })
  }

  static async addShipment(shipment: ShipmentResult): Promise<void> {
    const shipments = await this.getShipments()
    const existingIndex = shipments.findIndex(s => s.shipment_id === shipment.shipment_id)
    
    if (existingIndex >= 0) {
      shipments[existingIndex] = shipment
    } else {
      shipments.push(shipment)
    }
    
    await this.setShipments(shipments)
  }

  static async removeShipment(shipmentId: string): Promise<void> {
    const shipments = await this.getShipments()
    const filteredShipments = shipments.filter(s => s.shipment_id !== shipmentId)
    await this.setShipments(filteredShipments)
  }

  static async clearShipments(): Promise<void> {
    await chrome.storage.local.remove([this.KEYS.SHIPMENTS])
  }

  // Settings
  static async getSettings(): Promise<Record<string, any>> {
    const result = await chrome.storage.local.get([this.KEYS.SETTINGS])
    return result[this.KEYS.SETTINGS] || {}
  }

  static async setSettings(settings: Record<string, any>): Promise<void> {
    await chrome.storage.local.set({ [this.KEYS.SETTINGS]: settings })
  }

  static async updateSetting(key: string, value: any): Promise<void> {
    const settings = await this.getSettings()
    settings[key] = value
    await this.setSettings(settings)
  }

  // App state
  static async getAppState(): Promise<Partial<AppState>> {
    const [authToken, userData, orders, shipments] = await Promise.all([
      this.getAuthToken(),
      this.getUserData(),
      this.getOrders(),
      this.getShipments()
    ])

    return {
      isAuthenticated: !!authToken,
      user: userData,
      orders,
      shipments
    }
  }

  static async clearAll(): Promise<void> {
    await chrome.storage.local.clear()
  }

  // Queue management
  static async getOrdersQueue(): Promise<any[]> {
    const result = await chrome.storage.local.get(['ordersQueue'])
    return result.ordersQueue || []
  }

  static async setOrdersQueue(orders: any[]): Promise<void> {
    await chrome.storage.local.set({ ordersQueue: orders })
  }

  static async clearOrdersQueue(): Promise<void> {
    await chrome.storage.local.remove(['ordersQueue'])
  }

  // Storage info
  static async getStorageInfo(): Promise<number> {
    return await chrome.storage.local.getBytesInUse()
  }

  static async isStorageQuotaExceeded(): Promise<boolean> {
    const quota = await chrome.storage.local.getBytesInUse()
    return quota > (chrome.storage.local.QUOTA_BYTES * 0.9)
  }
}