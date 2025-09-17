import { parseCSV, generateCSV, downloadCSV, validateCSVHeaders, detectMarketplace } from '@/lib/csv'
import { CSVMapping } from '@/common/types'

describe('CSV Utils', () => {
  const sampleMapping: CSVMapping = {
    orderId: 'Order ID',
    orderDate: 'Order Date',
    status: 'Status',
    sku: 'SKU',
    product: 'Product',
    qty: 'Qty',
    price: 'Price',
    buyerName: 'Buyer Name',
    buyerEmail: 'Buyer Email',
    phone: 'Phone',
    shipTo: 'Ship To',
    address1: 'Address 1',
    address2: 'Address 2',
    city: 'City',
    postcode: 'Postal Code',
    country: 'Country',
    total: 'Total'
  }

  const sampleCSV = `Order ID,Order Date,Status,SKU,Product,Qty,Price,Buyer Name,Buyer Email,Phone,Ship To,Address 1,Address 2,City,Postal Code,Country,Total
ORD-001,2024-01-15,PENDING,SKU-123,Product A,2,25.50,John Doe,john@example.com,+34123456789,John Doe,123 Main St,Apt 4B,Madrid,28001,ES,51.00`

  describe('parseCSV', () => {
    it('should parse valid CSV correctly', () => {
      const orders = parseCSV(sampleCSV, sampleMapping)
      
      expect(orders).toHaveLength(1)
      expect(orders[0]).toMatchObject({
        orderId: 'ORD-001',
        status: 'PENDING',
        items: [{
          sku: 'SKU-123',
          name: 'Product A',
          qty: 2,
          unitPrice: 25.50
        }],
        buyer: {
          name: 'John Doe',
          email: 'john@example.com',
          phone: '+34123456789'
        },
        shipping: {
          name: 'John Doe',
          address1: '123 Main St',
          address2: 'Apt 4B',
          city: 'Madrid',
          postcode: '28001',
          country: 'ES'
        },
        totals: {
          goods: 51.00,
          shipping: 0
        }
      })
    })

    it('should handle missing columns gracefully', () => {
      const incompleteCSV = `Order ID,Status,SKU,Product,Qty,Price
ORD-001,PENDING,SKU-123,Product A,2,25.50`
      
      const orders = parseCSV(incompleteCSV, sampleMapping)
      expect(orders).toHaveLength(1)
      expect(orders[0].orderId).toBe('ORD-001')
    })

    it('should throw error for invalid CSV', () => {
      expect(() => {
        parseCSV('invalid csv data', sampleMapping)
      }).toThrow()
    })
  })

  describe('generateCSV', () => {
    it('should generate CSV from data', () => {
      const data = [
        { name: 'John', age: 30 },
        { name: 'Jane', age: 25 }
      ]
      const headers = ['name', 'age']
      
      const csv = generateCSV(data, headers)
      expect(csv).toContain('name,age')
      expect(csv).toContain('John,30')
      expect(csv).toContain('Jane,25')
    })
  })

  describe('validateCSVHeaders', () => {
    it('should validate required headers', () => {
      const headers = ['Order ID', 'Status', 'SKU']
      const required = ['Order ID', 'Status']
      
      expect(validateCSVHeaders(headers, required)).toBe(true)
    })

    it('should return false for missing headers', () => {
      const headers = ['Order ID', 'Status']
      const required = ['Order ID', 'Status', 'SKU']
      
      expect(validateCSVHeaders(headers, required)).toBe(false)
    })
  })

  describe('detectMarketplace', () => {
    it('should detect Carrefour from headers', () => {
      const headers = ['Order ID', 'Carrefour Status', 'SKU']
      expect(detectMarketplace(headers)).toBe('carrefour')
    })

    it('should detect marketplace from URL', () => {
      expect(detectMarketplace([], 'https://carrefour.mirakl.net')).toBe('carrefour')
      expect(detectMarketplace([], 'https://leroy.mirakl.net')).toBe('leroy')
      expect(detectMarketplace([], 'https://adeo.mirakl.net')).toBe('adeo')
    })

    it('should return unknown for unrecognized marketplace', () => {
      expect(detectMarketplace(['Order ID'], 'https://unknown.com')).toBe('unknown')
    })
  })
})
