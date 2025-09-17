import { OrderStandard, TIPSAOrder } from '@/common/types'

/**
 * TIPSA CSV mapper configuration
 */
export const TIPSA_CONFIG = {
  headers: [
    'destinatario',
    'direccion', 
    'cp',
    'poblacion',
    'pais',
    'contacto',
    'telefono',
    'email',
    'referencia',
    'peso',
    'servicio'
  ],
  defaultService: 'ESTANDAR',
  defaultWeight: '1.0',
  separator: ';'
} as const

/**
 * Map OrderStandard to TIPSA format
 */
export function mapOrderToTIPSA(order: OrderStandard): TIPSAOrder {
  return {
    destinatario: order.shipping.name,
    direccion: formatAddress(order.shipping),
    cp: order.shipping.postcode,
    poblacion: order.shipping.city,
    pais: order.shipping.country,
    contacto: order.buyer.name,
    telefono: order.buyer.phone || '',
    email: order.buyer.email || '',
    referencia: order.orderId,
    peso: calculateWeight(order),
    servicio: TIPSA_CONFIG.defaultService
  }
}

/**
 * Map multiple orders to TIPSA format
 */
export function mapOrdersToTIPSA(orders: OrderStandard[]): TIPSAOrder[] {
  return orders.map(mapOrderToTIPSA)
}

/**
 * Generate TIPSA CSV content
 */
export function generateTIPSACSV(orders: OrderStandard[]): string {
  const tipsaOrders = mapOrdersToTIPSA(orders)
  
  // Generate CSV header
  const header = TIPSA_CONFIG.headers.join(TIPSA_CONFIG.separator)
  
  // Generate CSV rows
  const rows = tipsaOrders.map(order => 
    TIPSA_CONFIG.headers.map(header => order[header as keyof TIPSAOrder]).join(TIPSA_CONFIG.separator)
  )
  
  return [header, ...rows].join('\n')
}

/**
 * Format shipping address for TIPSA
 */
function formatAddress(shipping: OrderStandard['shipping']): string {
  const parts = [shipping.address1]
  
  if (shipping.address2) {
    parts.push(shipping.address2)
  }
  
  return parts.join(', ')
}

/**
 * Calculate package weight (simplified)
 */
function calculateWeight(order: OrderStandard): string {
  // Simple weight calculation based on number of items
  // In a real implementation, this would use actual product weights
  const totalItems = order.items.reduce((sum, item) => sum + item.qty, 0)
  const baseWeight = 0.5 // Base weight per item in kg
  const totalWeight = totalItems * baseWeight
  
  return Math.max(totalWeight, 0.1).toFixed(1) // Minimum 0.1kg
}

/**
 * Validate TIPSA order data
 */
export function validateTIPSAData(order: TIPSAOrder): { isValid: boolean; errors: string[] } {
  const errors: string[] = []
  
  // Required fields validation
  if (!order.destinatario?.trim()) {
    errors.push('Destinatario is required')
  }
  
  if (!order.direccion?.trim()) {
    errors.push('Dirección is required')
  }
  
  if (!order.cp?.trim()) {
    errors.push('Código postal is required')
  }
  
  if (!order.poblacion?.trim()) {
    errors.push('Población is required')
  }
  
  if (!order.pais?.trim()) {
    errors.push('País is required')
  }
  
  if (!order.referencia?.trim()) {
    errors.push('Referencia is required')
  }
  
  // Format validation
  if (order.cp && !isValidPostalCode(order.cp)) {
    errors.push('Invalid postal code format')
  }
  
  if (order.pais && !isValidCountryCode(order.pais)) {
    errors.push('Invalid country code')
  }
  
  if (order.email && !isValidEmail(order.email)) {
    errors.push('Invalid email format')
  }
  
  if (order.telefono && !isValidPhone(order.telefono)) {
    errors.push('Invalid phone format')
  }
  
  if (order.peso && !isValidWeight(order.peso)) {
    errors.push('Invalid weight format')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Validate postal code format
 */
function isValidPostalCode(cp: string): boolean {
  // Spanish postal code format: 5 digits
  const spanishCPRegex = /^\d{5}$/
  return spanishCPRegex.test(cp.trim())
}

/**
 * Validate country code format
 */
function isValidCountryCode(country: string): boolean {
  // ISO 3166-1 alpha-2 country codes
  const countryCodeRegex = /^[A-Z]{2}$/
  return countryCodeRegex.test(country.trim().toUpperCase())
}

/**
 * Validate email format
 */
function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email.trim())
}

/**
 * Validate phone format
 */
function isValidPhone(phone: string): boolean {
  // Spanish phone format: +34XXXXXXXXX or 9 digits
  const phoneRegex = /^(\+34|0034)?[6-9]\d{8}$/
  return phoneRegex.test(phone.trim().replace(/\s/g, ''))
}

/**
 * Validate weight format
 */
function isValidWeight(weight: string): boolean {
  const weightNum = parseFloat(weight)
  return !isNaN(weightNum) && weightNum > 0 && weightNum <= 1000 // Max 1000kg
}

/**
 * Get TIPSA service options
 */
export function getTIPSAServices(): Array<{ value: string; label: string }> {
  return [
    { value: 'ESTANDAR', label: 'Estándar' },
    { value: 'URGENTE', label: 'Urgente' },
    { value: 'EXPRESS', label: 'Express' },
    { value: 'ECONOMICO', label: 'Económico' }
  ]
}

/**
 * Get TIPSA service label
 */
export function getTIPSAServiceLabel(service: string): string {
  const services = getTIPSAServices()
  const found = services.find(s => s.value === service)
  return found?.label || service
}

/**
 * Export TIPSA CSV to file
 */
export function exportTIPSACSV(orders: OrderStandard[], filename?: string): void {
  const csvContent = generateTIPSACSV(orders)
  const defaultFilename = `tipsa_orders_${new Date().toISOString().split('T')[0]}.csv`
  
  // Create and download file
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename || defaultFilename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } else {
    throw new Error('Download not supported in this browser')
  }
}
