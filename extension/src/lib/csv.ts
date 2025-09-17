import Papa from 'papaparse'
import { OrderStandard, OrderStandardSchema, CSVMapping, ValidationError } from '@/common/types'

/**
 * Parse CSV data and convert to OrderStandard format
 */
export function parseCSV(csvData: string, mapping: CSVMapping): OrderStandard[] {
  try {
    const result = Papa.parse(csvData, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (header) => header.trim()
    })

    if (result.errors.length > 0) {
      console.warn('CSV parsing warnings:', result.errors)
    }

    const orders: OrderStandard[] = []
    
    for (const row of result.data as any[]) {
      try {
        const order = parseOrderRow(row, mapping)
        const validatedOrder = OrderStandardSchema.parse(order)
        orders.push(validatedOrder)
      } catch (error) {
        console.error('Failed to parse order row:', row, error)
        // Continue processing other rows
      }
    }

    return orders
  } catch (error) {
    throw new ValidationError(`Failed to parse CSV: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

/**
 * Parse a single CSV row into OrderStandard format
 */
function parseOrderRow(row: any, mapping: CSVMapping): OrderStandard {
  // Extract basic order info
  const orderId = row[mapping.orderId]?.toString().trim()
  const orderDate = row[mapping.orderDate]?.toString().trim()
  const status = row[mapping.status]?.toString().trim().toUpperCase()
  const total = parseFloat(row[mapping.total]?.toString().replace(',', '.') || '0')

  // Extract buyer info
  const buyerName = row[mapping.buyerName]?.toString().trim()
  const buyerEmail = row[mapping.buyerEmail]?.toString().trim()
  const phone = row[mapping.phone]?.toString().trim()

  // Extract shipping info
  const shipTo = row[mapping.shipTo]?.toString().trim()
  const address1 = row[mapping.address1]?.toString().trim()
  const address2 = row[mapping.address2]?.toString().trim()
  const city = row[mapping.city]?.toString().trim()
  const postcode = row[mapping.postcode]?.toString().trim()
  const country = row[mapping.country]?.toString().trim().toUpperCase()

  // Extract items (assuming one item per row for now)
  const sku = row[mapping.sku]?.toString().trim()
  const product = row[mapping.product]?.toString().trim()
  const qty = parseInt(row[mapping.qty]?.toString() || '1')
  const unitPrice = parseFloat(row[mapping.price]?.toString().replace(',', '.') || '0')

  return {
    orderId,
    createdAt: parseDate(orderDate),
    status: mapStatus(status),
    items: [{
      sku,
      name: product,
      qty,
      unitPrice
    }],
    buyer: {
      name: buyerName,
      email: buyerEmail || undefined,
      phone: phone || undefined
    },
    shipping: {
      name: shipTo,
      address1,
      address2: address2 || undefined,
      city,
      postcode,
      country: country || 'ES'
    },
    totals: {
      goods: total,
      shipping: 0 // Default to 0, can be enhanced later
    }
  }
}

/**
 * Parse date string to ISO format
 */
function parseDate(dateStr: string): string {
  try {
    // Try different date formats
    const formats = [
      'YYYY-MM-DD',
      'DD/MM/YYYY',
      'MM/DD/YYYY',
      'DD-MM-YYYY',
      'MM-DD-YYYY'
    ]

    for (const format of formats) {
      try {
        const date = new Date(dateStr)
        if (!isNaN(date.getTime())) {
          return date.toISOString()
        }
      } catch {
        // Try next format
      }
    }

    // Fallback to current date
    return new Date().toISOString()
  } catch {
    return new Date().toISOString()
  }
}

/**
 * Map marketplace status to standard status
 */
function mapStatus(status: string): 'PENDING' | 'ACCEPTED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED' {
  const statusMap: Record<string, 'PENDING' | 'ACCEPTED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED'> = {
    'PENDING': 'PENDING',
    'PENDIENTE': 'PENDING',
    'ACCEPTED': 'ACCEPTED',
    'ACEPTADO': 'ACCEPTED',
    'SHIPPED': 'SHIPPED',
    'ENVIADO': 'SHIPPED',
    'DELIVERED': 'DELIVERED',
    'ENTREGADO': 'DELIVERED',
    'CANCELLED': 'CANCELLED',
    'CANCELADO': 'CANCELLED'
  }

  return statusMap[status] || 'PENDING'
}

/**
 * Generate CSV content from data
 */
export function generateCSV(data: any[], headers: string[]): string {
  try {
    const csv = Papa.unparse({
      fields: headers,
      data: data
    })
    return csv
  } catch (error) {
    throw new ValidationError(`Failed to generate CSV: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

/**
 * Download CSV file
 */
export function downloadCSV(csvContent: string, filename: string): void {
  try {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', filename)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } else {
      throw new Error('Download not supported in this browser')
    }
  } catch (error) {
    throw new ValidationError(`Failed to download CSV: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

/**
 * Validate CSV headers
 */
export function validateCSVHeaders(headers: string[], requiredHeaders: string[]): boolean {
  const normalizedHeaders = headers.map(h => h.trim().toLowerCase())
  const normalizedRequired = requiredHeaders.map(h => h.trim().toLowerCase())
  
  return normalizedRequired.every(required => 
    normalizedHeaders.some(header => header.includes(required))
  )
}

/**
 * Detect marketplace from CSV headers or URL
 */
export function detectMarketplace(headers: string[], url?: string): string {
  const headerStr = headers.join(' ').toLowerCase()
  
  if (headerStr.includes('carrefour') || url?.includes('carrefour')) {
    return 'carrefour'
  }
  if (headerStr.includes('leroy') || url?.includes('leroy')) {
    return 'leroy'
  }
  if (headerStr.includes('adeo') || url?.includes('adeo')) {
    return 'adeo'
  }
  
  return 'unknown'
}
