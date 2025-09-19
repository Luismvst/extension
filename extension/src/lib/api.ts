/**
 * API client for communicating with the backend.
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { 
  LoginRequest, 
  LoginResponse, 
  OrdersResponse, 
  CreateShipmentsRequest, 
  CreateShipmentsResponse,
  TrackingUploadRequest,
  TrackingUploadResponse,
  ApiResponse
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
    this.client.interceptors.request.use((config) => {
      const token = this.getAuthToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearAuthToken()
          window.location.reload()
        }
        return Promise.reject(error)
      }
    )
  }

  private getAuthToken(): string | null {
    return localStorage.getItem('auth_token')
  }

  private setAuthToken(token: string): void {
    localStorage.setItem('auth_token', token)
  }

  private clearAuthToken(): void {
    localStorage.removeItem('auth_token')
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.client.post(
      '/api/v1/auth/login',
      credentials
    )
    
    this.setAuthToken(response.data.access_token)
    return response.data
  }

  async getCurrentUser(): Promise<any> {
    const response = await this.client.get('/api/v1/auth/me')
    return response.data
  }

  async validateToken(): Promise<boolean> {
    try {
      await this.client.post('/api/v1/auth/validate')
      return true
    } catch {
      return false
    }
  }

  // Marketplace operations
  async getMiraklOrders(params: {
    status?: string
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  } = {}): Promise<OrdersResponse> {
    const response: AxiosResponse<OrdersResponse> = await this.client.get(
      '/api/v1/marketplaces/mirakl/orders',
      { params }
    )
    return response.data
  }

  async getMiraklOrder(orderId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/marketplaces/mirakl/orders/${orderId}`)
    return response.data
  }

  async uploadTrackingToMirakl(
    orderId: string, 
    trackingData: TrackingUploadRequest
  ): Promise<TrackingUploadResponse> {
    const response: AxiosResponse<TrackingUploadResponse> = await this.client.put(
      `/api/v1/marketplaces/mirakl/orders/${orderId}/tracking`,
      trackingData
    )
    return response.data
  }

  // Carrier operations
  async createShipments(shipments: CreateShipmentsRequest): Promise<CreateShipmentsResponse> {
    const response: AxiosResponse<CreateShipmentsResponse> = await this.client.post(
      '/api/v1/carriers/tipsa/shipments/bulk',
      shipments
    )
    return response.data
  }

  async getShipment(shipmentId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/carriers/tipsa/shipments/${shipmentId}`)
    return response.data
  }

  async trackShipment(trackingNumber: string): Promise<any> {
    const response = await this.client.get(`/api/v1/carriers/tipsa/tracking/${trackingNumber}`)
    return response.data
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
