import { z } from 'zod'

/**
 * Standardized order model used across the extension and backend
 */
export const OrderItemSchema = z.object({
  sku: z.string().min(1, 'SKU is required'),
  name: z.string().min(1, 'Product name is required'),
  qty: z.number().int().positive('Quantity must be positive'),
  unitPrice: z.number().positive('Unit price must be positive')
})

export const BuyerSchema = z.object({
  name: z.string().min(1, 'Buyer name is required'),
  email: z.string().email('Invalid email format').optional(),
  phone: z.string().optional()
})

export const ShippingAddressSchema = z.object({
  name: z.string().min(1, 'Shipping name is required'),
  address1: z.string().min(1, 'Address line 1 is required'),
  address2: z.string().optional(),
  city: z.string().min(1, 'City is required'),
  postcode: z.string().min(1, 'Postal code is required'),
  country: z.string().min(2, 'Country code is required').max(2, 'Country code must be 2 characters')
})

export const OrderTotalsSchema = z.object({
  goods: z.number().nonnegative('Goods total must be non-negative'),
  shipping: z.number().nonnegative('Shipping cost must be non-negative').optional()
})

export const OrderStandardSchema = z.object({
  orderId: z.string().min(1, 'Order ID is required'),
  createdAt: z.string().datetime('Invalid date format'),
  status: z.enum(['PENDING', 'ACCEPTED', 'SHIPPED', 'DELIVERED', 'CANCELLED']),
  items: z.array(OrderItemSchema).min(1, 'At least one item is required'),
  buyer: BuyerSchema,
  shipping: ShippingAddressSchema,
  totals: OrderTotalsSchema
})

export type OrderItem = z.infer<typeof OrderItemSchema>
export type Buyer = z.infer<typeof BuyerSchema>
export type ShippingAddress = z.infer<typeof ShippingAddressSchema>
export type OrderTotals = z.infer<typeof OrderTotalsSchema>
export type OrderStandard = z.infer<typeof OrderStandardSchema>

/**
 * CSV mapping configuration for different marketplaces
 */
export interface CSVMapping {
  orderId: string
  orderDate: string
  status: string
  sku: string
  product: string
  qty: string
  price: string
  buyerName: string
  buyerEmail: string
  phone: string
  shipTo: string
  address1: string
  address2: string
  city: string
  postcode: string
  country: string
  total: string
}

/**
 * TIPSA CSV format
 */
export interface TIPSAOrder {
  destinatario: string
  direccion: string
  cp: string
  poblacion: string
  pais: string
  contacto: string
  telefono: string
  email: string
  referencia: string
  peso: string
  servicio: string
}

/**
 * Extension messages
 */
export interface ExtensionMessage {
  type: 'GET_QUEUE' | 'ENQUEUE' | 'CLEAR' | 'EXPORT_CSV' | 'GENERATE_TIPSA'
  payload?: any
}

export interface QueueResponse {
  orders: OrderStandard[]
  count: number
}

export interface ExportCSVPayload {
  url: string
  marketplace: string
}

export interface GenerateTIPSAPayload {
  orders: OrderStandard[]
  format: 'csv' | 'json'
}

/**
 * Storage keys
 */
export const STORAGE_KEYS = {
  ORDERS_QUEUE: 'orders_queue',
  SETTINGS: 'extension_settings',
  LAST_SYNC: 'last_sync'
} as const

/**
 * Marketplace configurations
 */
export const MARKETPLACES = {
  CARREFOUR: 'carrefour',
  LEROY: 'leroy',
  ADEO: 'adeo'
} as const

export type Marketplace = typeof MARKETPLACES[keyof typeof MARKETPLACES]

/**
 * Error types
 */
export class ExtensionError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: any
  ) {
    super(message)
    this.name = 'ExtensionError'
  }
}

export class ValidationError extends ExtensionError {
  constructor(message: string, details?: any) {
    super(message, 'VALIDATION_ERROR', details)
    this.name = 'ValidationError'
  }
}

export class NetworkError extends ExtensionError {
  constructor(message: string, details?: any) {
    super(message, 'NETWORK_ERROR', details)
    this.name = 'NetworkError'
  }
}
