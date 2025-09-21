/**
 * CSV Export for Mirakl/TIPSA Integration
 * 
 * Generates CSV files with exact headers required for TIPSA integration.
 * Handles data mapping from orders and shipments to TIPSA format.
 */

import { Order } from '@/types';
import { ShipmentResult } from '@/types';

export interface CsvConfig {
  producto: string;
  tipoBultos: string;
  departamentoCliente: string;
  codigoCliente: string;
}

const DEFAULT_CONFIG: CsvConfig = {
  producto: '48',
  tipoBultos: 'PTR180P',
  departamentoCliente: 'empresarial',
  codigoCliente: '89'
};

export class CsvExporter {
  private config: CsvConfig;

  constructor(config?: Partial<CsvConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Load configuration from chrome.storage.sync
   */
  static async loadConfig(): Promise<CsvConfig> {
    try {
      const result = await chrome.storage.sync.get(['csvConfig']);
      return { ...DEFAULT_CONFIG, ...result.csvConfig };
    } catch (error) {
      console.error('Failed to load CSV config:', error);
      return DEFAULT_CONFIG;
    }
  }

  /**
   * Save configuration to chrome.storage.sync
   */
  static async saveConfig(config: CsvConfig): Promise<void> {
    try {
      await chrome.storage.sync.set({ csvConfig: config });
    } catch (error) {
      console.error('Failed to save CSV config:', error);
    }
  }

  /**
   * Generate CSV content from orders and shipments
   */
  generateCsv(orders: Order[], shipments: ShipmentResult[]): string {
    const headers = [
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
    ];

    const csvRows = [headers.join(';')];

    orders.forEach(order => {
      const shipment = shipments.find(s => s.order_id === order.order_id);
      const row = this.mapOrderToCsvRow(order, shipment);
      csvRows.push(row.join(';'));
    });

    return csvRows.join('\r\n');
  }

  /**
   * Map order and optional shipment to CSV row
   */
  private mapOrderToCsvRow(order: Order, shipment?: ShipmentResult): string[] {
    const shipping = order.shipping_address;
    const today = new Date().toISOString().slice(0, 10);

    return [
      this.escapeCsv(order.order_id), // Referencia
      this.escapeCsv(shipping?.name || order.customer_name || ''), // Nombre Consignatario
      this.escapeCsv(this.cleanAddress(shipping?.street || '')), // Dirección Consignatario
      this.escapeCsv(shipping?.city || ''), // Poblacion Consignatario
      this.normalizePostalCode(shipping?.postal_code || '', shipping?.country), // Código Postal Consignatario
      this.escapeCsv((shipping?.country || 'ES').toUpperCase()), // País del Consignatario
      this.escapeCsv(this.buildContact(shipping?.name, shipping?.phone)), // Contacto Consignatario
      this.escapeCsv(shipping?.phone || ''), // Teléfono Consignatario
      this.escapeCsv(String(order.packages_count || 1)), // Bultos
      this.escapeCsv(this.formatWeight(order.weight)), // Kilos
      this.escapeCsv(order.volume || ''), // Volumen
      this.escapeCsv(''), // Portes
      this.escapeCsv(this.config.producto), // Producto
      this.escapeCsv(order.payment_method === 'COD' ? String(order.total_amount || '') : ''), // Reembolso
      this.escapeCsv(''), // Fecha Aplazada
      this.escapeCsv(this.buildObservations(shipment, order.notes)), // Observaciones1
      this.escapeCsv(order.customer_email || ''), // Email Destino
      this.escapeCsv(this.config.tipoBultos), // Tipo Bultos
      this.escapeCsv(this.config.departamentoCliente), // Departamento Cliente
      this.escapeCsv('FALSE'), // Devolución Conforme
      this.escapeCsv(order.created_at?.slice(0, 10) || today), // Fecha
      this.escapeCsv(order.tax_id || ''), // Nif Consignatario
      this.escapeCsv(order.customer_name || shipping?.name || ''), // Nombre Cliente
      this.escapeCsv('FALSE'), // Retorno
      this.escapeCsv(this.config.codigoCliente), // Código Cliente
      this.escapeCsv('FALSE') // Multireferencia
    ];
  }

  /**
   * Clean address string
   */
  private cleanAddress(address: string): string {
    return address.replace(/\s+/g, ' ').trim();
  }

  /**
   * Normalize postal code for Spain
   */
  private normalizePostalCode(postalCode: string, country?: string): string {
    if (!postalCode) return '';
    
    if (country?.toUpperCase() === 'ES' && postalCode.length === 4) {
      return '0' + postalCode;
    }
    
    return postalCode;
  }

  /**
   * Build contact string
   */
  private buildContact(name?: string, phone?: string): string {
    const parts = [name || ''];
    if (phone) parts.push(phone);
    return parts.join(' ').trim();
  }

  /**
   * Format weight for CSV
   */
  private formatWeight(weight?: number): string {
    if (!weight) return '';
    return weight.toString().replace(',', '.');
  }

  /**
   * Build observations field
   */
  private buildObservations(shipment?: ShipmentResult, notes?: string): string {
    const parts = [];
    
    if (shipment?.tracking_number) {
      parts.push(`Tracking: ${shipment.tracking_number}`);
    }
    
    if (notes) {
      parts.push(notes);
    }
    
    return parts.join(' | ');
  }

  /**
   * Escape CSV field
   */
  private escapeCsv(field: string): string {
    if (field.includes(';') || field.includes('"') || field.includes('\n') || field.includes('\r')) {
      return `"${field.replace(/"/g, '""')}"`;
    }
    return field;
  }

  /**
   * Download CSV file
   */
  async downloadCsv(orders: Order[], shipments: ShipmentResult[]): Promise<void> {
    try {
      const csv = this.generateCsv(orders, shipments);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      const filename = `mirakl_tipsa_${timestamp}.csv`;
      
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download CSV:', error);
      throw error;
    }
  }
}

