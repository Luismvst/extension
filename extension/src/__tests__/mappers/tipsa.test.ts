import { mapOrderToTIPSA, mapOrdersToTIPSA, generateTIPSACSV, validateTIPSAData } from '@/mappers/tipsa'
import { OrderStandard } from '@/common/types'

describe('TIPSA Mapper', () => {
  const sampleOrder: OrderStandard = {
    orderId: 'ORD-001',
    createdAt: '2024-01-15T10:00:00Z',
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
  }

  describe('mapOrderToTIPSA', () => {
    it('should map OrderStandard to TIPSA format', () => {
      const tipsaOrder = mapOrderToTIPSA(sampleOrder)
      
      expect(tipsaOrder).toEqual({
        destinatario: 'John Doe',
        direccion: '123 Main St, Apt 4B',
        cp: '28001',
        poblacion: 'Madrid',
        pais: 'ES',
        contacto: 'John Doe',
        telefono: '+34123456789',
        email: 'john@example.com',
        referencia: 'ORD-001',
        peso: '1.0',
        servicio: 'ESTANDAR'
      })
    })

    it('should handle missing optional fields', () => {
      const orderWithoutOptional = {
        ...sampleOrder,
        buyer: {
          name: 'John Doe',
          email: undefined,
          phone: undefined
        },
        shipping: {
          name: 'John Doe',
          address1: '123 Main St',
          address2: undefined,
          city: 'Madrid',
          postcode: '28001',
          country: 'ES'
        }
      }

      const tipsaOrder = mapOrderToTIPSA(orderWithoutOptional)
      
      expect(tipsaOrder.telefono).toBe('')
      expect(tipsaOrder.email).toBe('')
      expect(tipsaOrder.direccion).toBe('123 Main St')
    })
  })

  describe('mapOrdersToTIPSA', () => {
    it('should map multiple orders', () => {
      const orders = [sampleOrder, { ...sampleOrder, orderId: 'ORD-002' }]
      const tipsaOrders = mapOrdersToTIPSA(orders)
      
      expect(tipsaOrders).toHaveLength(2)
      expect(tipsaOrders[0].referencia).toBe('ORD-001')
      expect(tipsaOrders[1].referencia).toBe('ORD-002')
    })
  })

  describe('generateTIPSACSV', () => {
    it('should generate CSV with correct headers', () => {
      const csv = generateTIPSACSV([sampleOrder])
      
      expect(csv).toContain('destinatario;direccion;cp;poblacion;pais;contacto;telefono;email;referencia;peso;servicio')
      expect(csv).toContain('John Doe;123 Main St, Apt 4B;28001;Madrid;ES;John Doe;+34123456789;john@example.com;ORD-001;1.0;ESTANDAR')
    })

    it('should handle empty orders array', () => {
      const csv = generateTIPSACSV([])
      
      expect(csv).toContain('destinatario;direccion;cp;poblacion;pais;contacto;telefono;email;referencia;peso;servicio')
      expect(csv.split('\n')).toHaveLength(1) // Only header
    })
  })

  describe('validateTIPSAData', () => {
    it('should validate correct TIPSA data', () => {
      const tipsaOrder = mapOrderToTIPSA(sampleOrder)
      const result = validateTIPSAData(tipsaOrder)
      
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should detect missing required fields', () => {
      const invalidOrder = {
        destinatario: '',
        direccion: '123 Main St',
        cp: '28001',
        poblacion: 'Madrid',
        pais: 'ES',
        contacto: 'John Doe',
        telefono: '+34123456789',
        email: 'john@example.com',
        referencia: 'ORD-001',
        peso: '1.0',
        servicio: 'ESTANDAR'
      }

      const result = validateTIPSAData(invalidOrder)
      
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Destinatario is required')
    })

    it('should validate postal code format', () => {
      const tipsaOrder = {
        ...mapOrderToTIPSA(sampleOrder),
        cp: 'invalid'
      }

      const result = validateTIPSAData(tipsaOrder)
      
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid postal code format')
    })

    it('should validate country code format', () => {
      const tipsaOrder = {
        ...mapOrderToTIPSA(sampleOrder),
        pais: 'SPAIN'
      }

      const result = validateTIPSAData(tipsaOrder)
      
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid country code')
    })

    it('should validate email format', () => {
      const tipsaOrder = {
        ...mapOrderToTIPSA(sampleOrder),
        email: 'invalid-email'
      }

      const result = validateTIPSAData(tipsaOrder)
      
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid email format')
    })

    it('should validate phone format', () => {
      const tipsaOrder = {
        ...mapOrderToTIPSA(sampleOrder),
        telefono: 'invalid-phone'
      }

      const result = validateTIPSAData(tipsaOrder)
      
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid phone format')
    })

    it('should validate weight format', () => {
      const tipsaOrder = {
        ...mapOrderToTIPSA(sampleOrder),
        peso: 'invalid-weight'
      }

      const result = validateTIPSAData(tipsaOrder)
      
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid weight format')
    })
  })
})
