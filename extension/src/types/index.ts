/**
 * Type definitions for the Chrome extension.
 */

export interface Order {
  order_id: string
  marketplace: string
  status: string
  created_at: string
  updated_at: string
  customer_name: string
  customer_email?: string
  customer_phone?: string
  shipping_address: Address
  items: OrderItem[]
  total_amount: number
  currency: string
  weight: number
  cod_amount?: number
  service_type?: string
  notes?: string
  metadata: Record<string, any>
  // Additional fields for CSV export
  payment_method?: string
  shipping_method?: string
  packages_count?: number
  volume?: string
  tax_id?: string
  syncedToMirakl?: boolean
}

export interface Address {
  name: string
  company?: string
  street: string
  city: string
  postal_code: string
  state?: string
  country: string
  phone?: string
  email?: string
}

export interface OrderItem {
  sku: string
  name: string
  quantity: number
  price: number
  weight: number
  dimensions?: {
    length: number
    width: number
    height: number
  }
}

export interface ShipmentRequest {
  order_id: string
  service_type: string
  weight: number
  dimensions?: {
    length: number
    width: number
    height: number
  }
  cod_amount?: number
  reference?: string
  notes?: string
}

export interface ShipmentResult {
  order_id: string
  shipment_id: string
  tracking_number: string
  status: string
  label_url?: string
  estimated_delivery?: string
  carrier: string
  cost?: number
  currency: string
  metadata: Record<string, any>
}

export interface TrackingInfo {
  tracking_number: string
  status: string
  current_location?: string
  estimated_delivery?: string
  events: TrackingEvent[]
}

export interface TrackingEvent {
  timestamp: string
  status: string
  description: string
  location?: string
  metadata: Record<string, any>
}

export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: string
  status: number
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    username: string
    email?: string
    is_active: boolean
    scopes: string[]
  }
}

export interface OrdersResponse {
  orders: Order[]
  total: number
  limit: number
  offset: number
}

export interface CreateShipmentsRequest {
  shipments: ShipmentRequest[]
}

export interface CreateShipmentsResponse {
  shipments: ShipmentResult[]
  total_created: number
  total_failed: number
}

export interface TrackingUploadRequest {
  tracking_number: string
  carrier_code: string
  carrier_name: string
  carrier_url?: string
}

export interface TrackingUploadResponse {
  success: boolean
  message: string
}

export interface AppState {
  isAuthenticated: boolean
  user?: LoginResponse['user']
  orders: Order[]
  shipments: ShipmentResult[]
  isLoading: boolean
  error?: string
}

export interface ExtensionMessage {
  type: 'FETCH_ORDERS' | 'CREATE_SHIPMENTS' | 'UPLOAD_TRACKING' | 'GET_LOGS'
  payload?: any
}

export interface ExtensionResponse {
  success: boolean
  data?: any
  error?: string
}
