import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CsvExporter } from './exportCsv';
import { Order, ShipmentResult } from '@/types';

// Mock chrome.storage.sync
const mockStorage = {
  get: vi.fn(),
  set: vi.fn()
};

// Mock chrome global
(global as any).chrome = {
  storage: {
    sync: mockStorage
  }
};

describe('CsvExporter', () => {
  const mockOrder: Order = {
    order_id: 'ORDER-123',
    marketplace: 'mirakl',
    customer_name: 'John Doe',
    customer_email: 'john@example.com',
    total_amount: 29.99,
    currency: 'EUR',
    weight: 1.5,
    status: 'PENDING',
    payment_method: 'COD',
    shipping_method: 'STANDARD',
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z',
    tax_id: '12345678A',
    packages_count: 1,
    volume: '0.001',
    notes: 'Handle with care',
    shipping_address: {
      name: 'John Doe',
      street: 'Calle Mayor 123',
      city: 'Madrid',
      postal_code: '28001',
      country: 'ES',
      phone: '+34123456789'
    },
    items: [],
    metadata: {}
  };

  const mockShipment: ShipmentResult = {
    order_id: 'ORDER-123',
    shipment_id: 'SHIP-456',
    tracking_number: 'TRK789',
    status: 'CREATED',
    carrier: 'tipsa',
    currency: 'EUR',
    metadata: {}
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('constructor', () => {
    it('should use default config when no config provided', () => {
      const exporter = new CsvExporter();
      expect(exporter).toBeDefined();
    });

    it('should merge provided config with defaults', () => {
      const customConfig = { 
        producto: '99',
        tipoBultos: 'CUSTOM',
        departamentoCliente: 'ventas',
        codigoCliente: '123'
      };
      const exporter = new CsvExporter(customConfig);
      expect(exporter).toBeDefined();
    });
  });

  describe('loadConfig', () => {
    it('should load config from chrome.storage.sync', async () => {
      const savedConfig = {
        producto: '99',
        tipoBultos: 'CUSTOM',
        departamentoCliente: 'ventas',
        codigoCliente: '123'
      };

      mockStorage.get.mockResolvedValue({ csvConfig: savedConfig });

      const config = await CsvExporter.loadConfig();

      expect(config).toEqual(savedConfig);
      expect(mockStorage.get).toHaveBeenCalledWith(['csvConfig']);
    });

    it('should return default config when no saved config exists', async () => {
      mockStorage.get.mockResolvedValue({});

      const config = await CsvExporter.loadConfig();

      expect(config).toEqual({
        producto: '48',
        tipoBultos: 'PTR180P',
        departamentoCliente: 'empresarial',
        codigoCliente: '89'
      });
    });

    it('should handle storage errors gracefully', async () => {
      mockStorage.get.mockRejectedValue(new Error('Storage error'));

      const config = await CsvExporter.loadConfig();

      expect(config).toEqual({
        producto: '48',
        tipoBultos: 'PTR180P',
        departamentoCliente: 'empresarial',
        codigoCliente: '89'
      });
    });
  });

  describe('saveConfig', () => {
    it('should save config to chrome.storage.sync', async () => {
      const config = {
        producto: '99',
        tipoBultos: 'CUSTOM',
        departamentoCliente: 'ventas',
        codigoCliente: '123'
      };

      await CsvExporter.saveConfig(config);

      expect(mockStorage.set).toHaveBeenCalledWith({ csvConfig: config });
    });

    it('should handle storage errors gracefully', async () => {
      mockStorage.set.mockRejectedValue(new Error('Storage error'));

      const config = { producto: '99' };

      // Should not throw
      await expect(CsvExporter.saveConfig(config)).resolves.toBeUndefined();
    });
  });

  describe('generateCsv', () => {
    it('should generate CSV with correct headers', () => {
      const exporter = new CsvExporter();
      const csv = exporter.generateCsv([mockOrder], [mockShipment]);

      const lines = csv.split('\r\n');
      const headers = lines[0].split(';');

      expect(headers).toEqual([
        'Referencia',
        'Nombre Consignatario',
        'Dirección Consignatario',
        'Poblacion Consignatario',
        'Código Postal Consignatario',
        'País del Consignatario',
        'Contacto Consignatario',
        'Teléfono Consignatario',
        'Bultos',
        'Kilos',
        'Volumen',
        'Portes',
        'Producto',
        'Reembolso',
        'Fecha Aplazada',
        'Observaciones1',
        'Email Destino',
        'Tipo Bultos',
        'Departamento Cliente',
        'Devolución Conforme',
        'Fecha',
        'Nif Consignatario',
        'Nombre Cliente',
        'Retorno',
        'Código Cliente',
        'Multireferencia'
      ]);
    });

    it('should map order data correctly', () => {
      const exporter = new CsvExporter();
      const csv = exporter.generateCsv([mockOrder], [mockShipment]);

      const lines = csv.split('\r\n');
      const dataRow = lines[1].split(';');

      expect(dataRow[0]).toBe('ORDER-123'); // Referencia
      expect(dataRow[1]).toBe('John Doe'); // Nombre Consignatario
      expect(dataRow[2]).toBe('Calle Mayor 123'); // Dirección Consignatario
      expect(dataRow[3]).toBe('Madrid'); // Poblacion Consignatario
      expect(dataRow[4]).toBe('28001'); // Código Postal Consignatario
      expect(dataRow[5]).toBe('ES'); // País del Consignatario
      expect(dataRow[6]).toBe('John Doe +34123456789'); // Contacto Consignatario
      expect(dataRow[7]).toBe('+34123456789'); // Teléfono Consignatario
      expect(dataRow[8]).toBe('1'); // Bultos
      expect(dataRow[9]).toBe('1.5'); // Kilos
      expect(dataRow[10]).toBe('0.001'); // Volumen
      expect(dataRow[11]).toBe(''); // Portes
      expect(dataRow[12]).toBe('48'); // Producto (default)
      expect(dataRow[13]).toBe('29.99'); // Reembolso (COD)
      expect(dataRow[14]).toBe(''); // Fecha Aplazada
      expect(dataRow[15]).toBe('Tracking: TRK789 | Handle with care'); // Observaciones1
      expect(dataRow[16]).toBe('john@example.com'); // Email Destino
      expect(dataRow[17]).toBe('PTR180P'); // Tipo Bultos (default)
      expect(dataRow[18]).toBe('empresarial'); // Departamento Cliente (default)
      expect(dataRow[19]).toBe('FALSE'); // Devolución Conforme
      expect(dataRow[20]).toBe('2024-01-01'); // Fecha
      expect(dataRow[21]).toBe('12345678A'); // Nif Consignatario
      expect(dataRow[22]).toBe('John Doe'); // Nombre Cliente
      expect(dataRow[23]).toBe('FALSE'); // Retorno
      expect(dataRow[24]).toBe('89'); // Código Cliente (default)
      expect(dataRow[25]).toBe('FALSE'); // Multireferencia
    });

    it('should normalize Spanish postal codes', () => {
      const orderWithShortPostalCode = {
        ...mockOrder,
        shipping_address: {
          ...mockOrder.shipping_address!,
          postal_code: '6186',
          country: 'ES'
        }
      };

      const exporter = new CsvExporter();
      const csv = exporter.generateCsv([orderWithShortPostalCode], []);

      const lines = csv.split('\r\n');
      const dataRow = lines[1].split(';');

      expect(dataRow[4]).toBe('06186'); // Should add leading zero
    });

    it('should handle missing fields gracefully', () => {
      const incompleteOrder: Order = {
        order_id: 'ORDER-456',
        marketplace: 'mirakl',
        customer_name: 'Jane Doe',
        total_amount: 19.99,
        currency: 'EUR',
        weight: 0.5,
        status: 'PENDING',
        payment_method: 'CARD',
        shipping_method: 'STANDARD',
        created_at: '2024-01-01T10:00:00Z',
        updated_at: '2024-01-01T10:00:00Z',
        shipping_address: {
          name: 'Jane Doe',
          street: '',
          city: '',
          postal_code: '',
          country: 'ES'
        },
        items: [],
        metadata: {}
      };

      const exporter = new CsvExporter();
      const csv = exporter.generateCsv([incompleteOrder], []);

      const lines = csv.split('\r\n');
      const dataRow = lines[1].split(';');

      expect(dataRow[0]).toBe('ORDER-456'); // Referencia
      expect(dataRow[1]).toBe('Jane Doe'); // Nombre Consignatario
      expect(dataRow[2]).toBe(''); // Dirección Consignatario (missing)
      expect(dataRow[3]).toBe(''); // Poblacion Consignatario (missing)
      expect(dataRow[4]).toBe(''); // Código Postal Consignatario (missing)
      expect(dataRow[5]).toBe('ES'); // País del Consignatario (default)
      expect(dataRow[13]).toBe(''); // Reembolso (not COD)
    });

    it('should escape CSV fields with special characters', () => {
      const orderWithSpecialChars = {
        ...mockOrder,
        customer_name: 'John "Doe"',
        shipping_address: {
          ...mockOrder.shipping_address!,
          street: 'Calle Mayor; 123',
          city: 'Madrid\nSpain'
        }
      };

      const exporter = new CsvExporter();
      const csv = exporter.generateCsv([orderWithSpecialChars], []);

      const lines = csv.split('\r\n');
      const dataRow = lines[1].split(';');

      expect(dataRow[1]).toBe('"John ""Doe"""'); // Should escape quotes
      expect(dataRow[2]).toBe('"Calle Mayor; 123"'); // Should escape semicolons
      expect(dataRow[3]).toBe('"Madrid\nSpain"'); // Should escape newlines
    });
  });

  describe('downloadCsv', () => {
    it('should create and trigger download', async () => {
      // Mock DOM methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      };
      const mockCreateElement = vi.fn().mockReturnValue(mockLink);
      const mockAppendChild = vi.fn();
      const mockRemoveChild = vi.fn();
      const mockCreateObjectURL = vi.fn().mockReturnValue('blob:url');
      const mockRevokeObjectURL = vi.fn();

      Object.defineProperty(document, 'createElement', {
        value: mockCreateElement,
        writable: true
      });
      Object.defineProperty(document.body, 'appendChild', {
        value: mockAppendChild,
        writable: true
      });
      Object.defineProperty(document.body, 'removeChild', {
        value: mockRemoveChild,
        writable: true
      });
      Object.defineProperty(URL, 'createObjectURL', {
        value: mockCreateObjectURL,
        writable: true
      });
      Object.defineProperty(URL, 'revokeObjectURL', {
        value: mockRevokeObjectURL,
        writable: true
      });

      const exporter = new CsvExporter();
      await exporter.downloadCsv([mockOrder], [mockShipment]);

      expect(mockCreateElement).toHaveBeenCalledWith('a');
      expect(mockLink.download).toMatch(/mirakl_tipsa_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.csv/);
      expect(mockLink.click).toHaveBeenCalled();
      expect(mockAppendChild).toHaveBeenCalledWith(mockLink);
      expect(mockRemoveChild).toHaveBeenCalledWith(mockLink);
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:url');
    });
  });
});
