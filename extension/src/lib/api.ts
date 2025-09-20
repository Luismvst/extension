/**
 * API client for communicating with the backend.
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios'
import Logger from './logger'
import { 
  LoginRequest, 
  LoginResponse, 
  OrdersResponse, 
  CreateShipmentsRequest, 
  CreateShipmentsResponse,
  TrackingUploadRequest,
  TrackingUploadResponse,
  ApiResponse,
  ShipmentResult
} from '@/types'

class ApiClient {
  private client: AxiosInstance
  private baseURL: string

  constructor(baseURL: string = 'http://localhost:8080') {
    this.baseURL = baseURL
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config: any) => {
      // We'll handle token injection in each method call
      return config
    })

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response: any) => response,
      async (error: any) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          await this.clearAuthToken()
          window.location.reload()
        }
        return Promise.reject(error)
      }
    )
  }

  private async getAuthToken(): Promise<string | null> {
    const result = await chrome.storage.local.get(['auth_token'])
    return result.auth_token || null
  }

  private async setAuthToken(token: string): Promise<void> {
    await chrome.storage.local.set({
      auth_token: token,
      auth_token_timestamp: Date.now().toString()
    })
  }

  private async clearAuthToken(): Promise<void> {
    await chrome.storage.local.remove(['auth_token', 'auth_token_timestamp'])
  }

  private async isTokenExpired(): Promise<boolean> {
    const result = await chrome.storage.local.get(['auth_token_timestamp'])
    const timestamp = result.auth_token_timestamp
    if (!timestamp) return true
    
    const tokenAge = Date.now() - parseInt(timestamp)
    const fifteenMinutes = 15 * 60 * 1000 // 15 minutes in milliseconds
    
    return tokenAge > fifteenMinutes
  }

  private async ensureValidToken(): Promise<void> {
    const token = await this.getAuthToken()
    const expired = await this.isTokenExpired()
    if (!token || expired) {
      console.log('Token expired or missing, refreshing...')
      await this.getExtensionToken()
    }
  }

  private async addAuthHeader(config: any): Promise<any> {
    await this.ensureValidToken()
    const token = await this.getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.client.post(
      '/auth/login',
      credentials
    )
    
    await this.setAuthToken(response.data.access_token)
    return response.data
  }

  async getCurrentUser(): Promise<any> {
    const config = await this.addAuthHeader({ headers: {} })
    const response = await this.client.get('/auth/me', config)
    return response.data
  }

  async validateToken(): Promise<boolean> {
    try {
      const config = await this.addAuthHeader({ headers: {} })
      await this.client.post('/auth/validate', {}, config)
      return true
    } catch {
      return false
    }
  }

  async getExtensionToken(): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.client.post(
      '/auth/extension-token'
    )
    
    await this.setAuthToken(response.data.access_token)
    return response.data
  }

  // Marketplace operations
  async getMiraklOrders(params: {
    status?: string
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  } = {}): Promise<OrdersResponse> {
    Logger.section('🛒 MIRAKL ORDERS REQUEST')
    Logger.apiRequest('GET', '/api/v1/marketplaces/mirakl/orders', params)
    
    try {
      const config = await this.addAuthHeader({ headers: {} })
      const response: AxiosResponse<OrdersResponse> = await this.client.get(
        '/api/v1/marketplaces/mirakl/orders',
        { ...config, params }
      )
      
      Logger.apiResponse(response.status, response.data)
      Logger.success(`Retrieved ${response.data.orders?.length || 0} orders from Mirakl`)
      
      return response.data
    } catch (error: any) {
      Logger.error('Failed to get Mirakl orders', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        params
      })
      throw error
    }
  }

  async getMiraklOrder(orderId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/marketplaces/mirakl/orders/${orderId}`)
    return response.data
  }

  async uploadTrackingToMiraklSingle(
    orderId: string, 
    trackingData: TrackingUploadRequest
  ): Promise<TrackingUploadResponse> {
    Logger.section('📤 UPLOAD TRACKING TO MIRAKL (SINGLE)')
    Logger.apiRequest('PUT', `/api/v1/marketplaces/mirakl/orders/${orderId}/tracking`, trackingData)
    
    try {
      const config = await this.addAuthHeader({ headers: {} })
      const response: AxiosResponse<TrackingUploadResponse> = await this.client.put(
        `/api/v1/marketplaces/mirakl/orders/${orderId}/tracking`,
        trackingData,
        config
      )
      
      Logger.apiResponse(response.status, response.data)
      Logger.success(`Uploaded tracking for order ${orderId} to Mirakl`)
      
      return response.data
    } catch (error: any) {
      Logger.error('Failed to upload tracking to Mirakl', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        orderId,
        trackingData
      })
      throw error
    }
  }

  // Orchestrator operations
  async loadOrdersAndCreateShipments(): Promise<{
    success: boolean
    message: string
    orders_processed: number
    shipments_created: number
    shipments: ShipmentResult[]
    carrier_breakdown: Record<string, any>
  }> {
    Logger.section('🔄 LOAD ORDERS AND CREATE SHIPMENTS')
    Logger.apiRequest('POST', '/api/v1/orchestrator/load-orders', {})
    
    try {
      const config = await this.addAuthHeader({ headers: {} })
      const response: AxiosResponse<any> = await this.client.post(
        '/api/v1/orchestrator/load-orders',
        {},
        config
      )
      
      Logger.apiResponse(response.status, response.data)
      Logger.success(`Processed ${response.data.orders_processed || 0} orders and created ${response.data.shipments_created || 0} shipments`)
      
      // Map shipments to ensure proper typing
      const mappedShipments: ShipmentResult[] = (response.data.shipments || []).map((shipment: any) => ({
        order_id: shipment.order_id,
        shipment_id: shipment.shipment_id,
        tracking_number: shipment.tracking_number,
        status: shipment.status,
        label_url: shipment.label_url,
        estimated_delivery: shipment.estimated_delivery,
        carrier: shipment.carrier || 'TIPSA',
        cost: shipment.cost,
        currency: shipment.currency || 'EUR',
        metadata: shipment.metadata || {}
      }))
      
      return {
        ...response.data,
        shipments: mappedShipments
      }
    } catch (error: any) {
      Logger.error('Failed to load orders and create shipments', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      })
      throw error
    }
  }

  async uploadTrackingToMirakl(trackingData: any[]): Promise<any> {
    Logger.section('📤 UPLOAD TRACKING TO MIRAKL')
    Logger.apiRequest('POST', '/api/v1/orchestrator/upload-tracking', trackingData)
    
    try {
      const config = await this.addAuthHeader({ headers: {} })
      const response: AxiosResponse<any> = await this.client.post(
        '/api/v1/orchestrator/upload-tracking',
        trackingData,
        config
      )
      
      Logger.apiResponse(response.status, response.data)
      Logger.success(`Uploaded tracking for ${response.data.orders_updated || 0} orders to Mirakl`)
      
      return response.data
    } catch (error: any) {
      Logger.error('Failed to upload tracking to Mirakl', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        trackingData
      })
      throw error
    }
  }

  // Legacy carrier operations (kept for backward compatibility)
  async createShipments(shipments: CreateShipmentsRequest): Promise<CreateShipmentsResponse> {
    Logger.section('🚚 TIPSA SHIPMENTS CREATION')
    Logger.apiRequest('POST', '/api/v1/carriers/tipsa/shipments/bulk', shipments)
    
    try {
      const config = await this.addAuthHeader({ headers: {} })
      const response: AxiosResponse<CreateShipmentsResponse> = await this.client.post(
        '/api/v1/carriers/tipsa/shipments/bulk',
        shipments,
        config
      )
      
      Logger.apiResponse(response.status, response.data)
      Logger.success(`Created ${response.data.shipments?.length || 0} shipments in TIPSA`)
      
      return response.data
    } catch (error: any) {
      Logger.error('Failed to create TIPSA shipments', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        shipments
      })
      throw error
    }
  }

  async getShipment(shipmentId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/carriers/tipsa/shipments/${shipmentId}`)
    return response.data
  }

  async trackShipment(trackingNumber: string): Promise<any> {
    Logger.section('🔍 TIPSA SHIPMENT TRACKING')
    Logger.apiRequest('GET', `/api/v1/carriers/tipsa/tracking/${trackingNumber}`)
    
    try {
      const config = await this.addAuthHeader({ headers: {} })
      const response = await this.client.get(
        `/api/v1/carriers/tipsa/tracking/${trackingNumber}`,
        config
      )
      
      Logger.apiResponse(response.status, response.data)
      Logger.success(`Retrieved tracking info for ${trackingNumber}`)
      
      return response.data
    } catch (error: any) {
      Logger.error('Failed to track shipment', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        trackingNumber
      })
      throw error
    }
  }

  async getShipmentLabel(shipmentId: string): Promise<Blob> {
    const response = await this.client.get(
      `/api/v1/carriers/tipsa/shipments/${shipmentId}/label`,
      { responseType: 'blob' }
    )
    return response.data
  }

  async getAvailableServices(): Promise<any[]> {
    const response = await this.client.get('/api/v1/carriers/tipsa/services')
    return response.data.services
  }

  // Health checks
  async checkHealth(): Promise<any> {
    const response = await this.client.get('/api/v1/health/')
    return response.data
  }

  async checkDetailedHealth(): Promise<any> {
    const response = await this.client.get('/api/v1/health/detailed')
    return response.data
  }

  // Logs
  async getLogsInfo(): Promise<any> {
    const response = await this.client.get('/api/v1/health/logs')
    return response.data
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.getAuthToken()
  }

  logout(): void {
    this.clearAuthToken()
  }
}

// Create singleton instance
export const apiClient = new ApiClient()

// Export types for convenience
export type { LoginRequest, LoginResponse, OrdersResponse, CreateShipmentsRequest, CreateShipmentsResponse }
