import { describe, it, expect } from 'vitest'
import { CsvExporter } from '@/lib/exportCsv'

describe('CsvExporter', () => {
  const mockOrders = [
    {
      order_id: 'MIR-001',
      marketplace: 'mirakl',
      status: 'SHIPPING',
      customer_name: 'John Doe',
      weight: 2.5,
      total_amount: 45.99,
      shipping_address: {
        name: 'John Doe',
        street: 'Calle Test 123',
        city: 'Madrid',
        postal_code: '6186',
        country: 'ES'
      },
      payment_method: 'CREDIT_CARD',
      shipping_method: 'STANDARD'
    }
  ]

  const mockShipments = [
    {
      order_id: 'MIR-001',
      shipment_id: 'TIPSA-001',
      tracking_number: '1Z123456789',
      status: 'CREATED'
    }
  ]

  it('should export CSV with correct headers', () => {
    const exporter = new CsvExporter()
    const csv = exporter.exportOrders(mockOrders, mockShipments)

    const lines = csv.split('\n')
    const headers = lines[0].split(';')

    expect(headers).toContain('Número de Pedido')
    expect(headers).toContain('Cliente')
    expect(headers).toContain('Peso')
    expect(headers).toContain('Importe')
    expect(headers).toContain('Observaciones1')
  })

  it('should normalize Spanish postal codes', () => {
    const exporter = new CsvExporter()
    const csv = exporter.exportOrders(mockOrders, mockShipments)

    expect(csv).toContain('06186') // 6186 should become 06186
  })

  it('should include tracking number in observations', () => {
    const exporter = new CsvExporter()
    const csv = exporter.exportOrders(mockOrders, mockShipments)

    expect(csv).toContain('1Z123456789')
  })

  it('should escape CSV values correctly', () => {
    const ordersWithSpecialChars = [
      {
        ...mockOrders[0],
        customer_name: 'Test "Company" Ltd.',
        shipping_address: {
          ...mockOrders[0].shipping_address,
          street: 'Calle "Especial" 123'
        }
      }
    ]

    const exporter = new CsvExporter()
    const csv = exporter.exportOrders(ordersWithSpecialChars, mockShipments)

    // Should not break CSV format with quotes
    expect(csv).toContain('"Test ""Company"" Ltd."')
  })

  it('should handle empty orders array', () => {
    const exporter = new CsvExporter()
    const csv = exporter.exportOrders([], [])

    const lines = csv.split('\n')
    expect(lines).toHaveLength(2) // Headers + empty line
  })

  it('should use default values for missing fields', () => {
    const exporter = new CsvExporter()
    const csv = exporter.exportOrders(mockOrders, mockShipments)

    expect(csv).toContain('Producto') // Default product
    expect(csv).toContain('Paquete') // Default package type
  })
})
