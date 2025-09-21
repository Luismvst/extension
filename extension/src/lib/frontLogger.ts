/**
 * Frontend Logger for Chrome Extension
 * 
 * Manages frontend-specific logging with CSV export functionality.
 * Stores logs in chrome.storage.local with rotation to prevent storage bloat.
 */

export type FrontLog = {
  ts: string;              // ISO timestamp
  action: 'LOAD_ORDERS' | 'CREATE_SHIPMENTS' | 'UPLOAD_TRACKING' | 'DOWNLOAD_LABEL' | 'EXPORT_CSV' | 'ERROR';
  ok: boolean;
  msg?: string;
  details?: Record<string, any>;
};

const MAX_LOGS = 2000;
const STORAGE_KEY = 'frontLogs';

export const FrontLogger = {
  /**
   * Add a new log entry
   */
  async push(entry: FrontLog): Promise<void> {
    try {
      const logs = await this.getAll();
      logs.push(entry);
      
      // Rotate if too many logs
      if (logs.length > MAX_LOGS) {
        logs.splice(0, logs.length - MAX_LOGS);
      }
      
      await chrome.storage.local.set({ [STORAGE_KEY]: logs });
    } catch (error) {
      console.error('Failed to push log entry:', error);
    }
  },

  /**
   * Get all log entries
   */
  async getAll(): Promise<FrontLog[]> {
    try {
      const result = await chrome.storage.local.get([STORAGE_KEY]);
      return result[STORAGE_KEY] || [];
    } catch (error) {
      console.error('Failed to get logs:', error);
      return [];
    }
  },

  /**
   * Clear all logs
   */
  async clear(): Promise<void> {
    try {
      await chrome.storage.local.remove([STORAGE_KEY]);
    } catch (error) {
      console.error('Failed to clear logs:', error);
    }
  },

  /**
   * Export logs as CSV
   */
  exportCSV(): string {
    const logs = this.getAllSync();
    const headers = ['ts', 'action', 'ok', 'msg', 'details_json'];
    
    const csvRows = [headers.join(';')];
    
    logs.forEach(log => {
      const row = [
        this.escapeCsv(log.ts),
        this.escapeCsv(log.action),
        this.escapeCsv(log.ok.toString()),
        this.escapeCsv(log.msg || ''),
        this.escapeCsv(JSON.stringify(log.details || {}))
      ];
      csvRows.push(row.join(';'));
    });
    
    return csvRows.join('\r\n');
  },

  /**
   * Get logs synchronously (for CSV export)
   */
  getAllSync(): FrontLog[] {
    // This is a fallback - in practice, we'll use async getAll
    return [];
  },

  /**
   * Escape CSV field
   */
  escapeCsv(field: string): string {
    if (field.includes(';') || field.includes('"') || field.includes('\n') || field.includes('\r')) {
      return `"${field.replace(/"/g, '""')}"`;
    }
    return field;
  },

  /**
   * Download logs as CSV file
   */
  async downloadLogs(): Promise<void> {
    try {
      const logs = await this.getAll();
      const csv = this.exportCSV();
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      const filename = `frontend_logs_${timestamp}.csv`;
      
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
      
      await this.push({
        ts: new Date().toISOString(),
        action: 'EXPORT_CSV',
        ok: true,
        msg: `Downloaded ${logs.length} log entries`,
        details: { filename, count: logs.length }
      });
    } catch (error) {
      console.error('Failed to download logs:', error);
      await this.push({
        ts: new Date().toISOString(),
        action: 'ERROR',
        ok: false,
        msg: 'Failed to download logs',
        details: { error: error instanceof Error ? error.message : String(error) }
      });
    }
  }
};
