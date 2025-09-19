import { CSVMapping, MARKETPLACES, ValidationError, NetworkError } from '@/common/types'
import { parseCSV } from '@/lib/csv'
import { sendMessage } from '@/common/messages'

/**
 * CSV export hook for intercepting Mirakl marketplace exports
 */
export class CSVExportHook {
  private isActive = false
  private marketplace: string = 'unknown'

  constructor() {
    this.detectMarketplace()
    this.setupExportHooks()
  }

  /**
   * Detect marketplace from current URL
   */
  private detectMarketplace(): void {
    const hostname = window.location.hostname.toLowerCase()
    
    if (hostname.includes('carrefour')) {
      this.marketplace = MARKETPLACES.CARREFOUR
    } else if (hostname.includes('leroy')) {
      this.marketplace = MARKETPLACES.LEROY
    } else if (hostname.includes('adeo')) {
      this.marketplace = MARKETPLACES.ADEO
    } else {
      this.marketplace = 'unknown'
    }
  }

  /**
   * Setup hooks for CSV export buttons/links
   */
  private setupExportHooks(): void {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.attachHooks())
    } else {
      this.attachHooks()
    }

    // Re-attach hooks when new content is loaded (SPA support)
    const observer = new MutationObserver(() => {
      this.attachHooks()
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true
    })
  }

  /**
   * Attach hooks to export elements
   */
  private attachHooks(): void {
    if (this.isActive) return

    // Common selectors for export buttons/links
    const selectors = [
      'a[href*="export"]',
      'a[href*="csv"]',
      'button[data-export]',
      'button[data-csv]',
      '.export-button',
      '.csv-export',
      '[data-testid*="export"]',
      '[data-testid*="csv"]'
    ]

    for (const selector of selectors) {
      const elements = document.querySelectorAll(selector)
      elements.forEach(element => this.attachHook(element))
    }

    this.isActive = true
  }

  /**
   * Attach hook to specific element
   */
  private attachHook(element: Element): void {
    if (element.hasAttribute('data-mirakl-hooked')) return

    element.setAttribute('data-mirakl-hooked', 'true')
    
    element.addEventListener('click', (event) => {
      this.handleExportClick(event, element)
    })
  }

  /**
   * Handle export button/link click
   */
  private async handleExportClick(event: Event, element: Element): Promise<void> {
    try {
      event.preventDefault()
      event.stopPropagation()

      console.log('CSV export intercepted:', element)

      // Show loading indicator
      this.showLoadingIndicator(element)

      // Extract CSV URL
      const csvUrl = this.extractCSVUrl(element)
      if (!csvUrl) {
        throw new ValidationError('Could not extract CSV URL from element')
      }

      // Fetch CSV data
      const csvData = await this.fetchCSVData(csvUrl)
      
      // Parse CSV
      const mapping = this.getCSVMapping()
      const orders = parseCSV(csvData, mapping)

      // Send to background script
      await sendMessage({
        type: 'ENQUEUE',
        payload: { orders }
      })

      // Show success notification
      this.showSuccessNotification(orders.length)

      // Allow original action to proceed (optional)
      // this.allowOriginalAction(element)

    } catch (error) {
      console.error('Error intercepting CSV export:', error)
      this.showErrorNotification(error instanceof Error ? error.message : 'Unknown error')
    } finally {
      this.hideLoadingIndicator(element)
    }
  }

  /**
   * Extract CSV URL from element
   */
  private extractCSVUrl(element: Element): string | null {
    // Try different methods to extract URL
    if (element instanceof HTMLAnchorElement) {
      return element.href
    }

    if (element instanceof HTMLButtonElement) {
      // Check data attributes
      const url = element.dataset.url || element.dataset.href || element.dataset.csvUrl
      if (url) return url

      // Check if button has onclick handler with URL
      const onclick = element.getAttribute('onclick')
      if (onclick) {
        const urlMatch = onclick.match(/['"]([^'"]*\.csv[^'"]*)['"]/)
        if (urlMatch) return urlMatch[1]
      }
    }

    // Look for nearby elements that might contain the URL
    const parent = element.closest('form, .export-container, .csv-container')
    if (parent) {
      const urlInput = parent.querySelector('input[type="hidden"][name*="url"], input[type="hidden"][name*="csv"]')
      if (urlInput instanceof HTMLInputElement) {
        return urlInput.value
      }
    }

    return null
  }

  /**
   * Fetch CSV data from URL
   */
  private async fetchCSVData(url: string): Promise<string> {
    try {
      // Make URL absolute if relative
      const absoluteUrl = url.startsWith('http') ? url : new URL(url, window.location.origin).href

      const response = await fetch(absoluteUrl, {
        method: 'GET',
        credentials: 'include', // Include cookies for authentication
        headers: {
          'Accept': 'text/csv,application/csv,text/plain,*/*',
          'User-Agent': navigator.userAgent
        }
      })

      if (!response.ok) {
        throw new NetworkError(`Failed to fetch CSV: ${response.status} ${response.statusText}`)
      }

      const csvData = await response.text()
      if (!csvData.trim()) {
        throw new ValidationError('CSV file is empty')
      }

      return csvData
    } catch (error) {
      if (error instanceof NetworkError || error instanceof ValidationError) {
        throw error
      }
      throw new NetworkError(`Failed to fetch CSV: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Get CSV mapping configuration for current marketplace
   */
  private getCSVMapping(): CSVMapping {
    const mappings: Record<string, CSVMapping> = {
      [MARKETPLACES.CARREFOUR]: {
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
      },
      [MARKETPLACES.LEROY]: {
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
      },
      [MARKETPLACES.ADEO]: {
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
    }

    return mappings[this.marketplace] || mappings[MARKETPLACES.CARREFOUR]
  }

  /**
   * Show loading indicator
   */
  private showLoadingIndicator(_element: Element): void {
    const indicator = document.createElement('div')
    indicator.className = 'mirakl-loading-indicator'
    indicator.innerHTML = '⏳ Processing CSV...'
    indicator.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #3b82f6;
      color: white;
      padding: 10px 15px;
      border-radius: 5px;
      z-index: 10000;
      font-family: Arial, sans-serif;
      font-size: 14px;
    `
    document.body.appendChild(indicator)
  }

  /**
   * Hide loading indicator
   */
  private hideLoadingIndicator(_element: Element): void {
    const indicator = document.querySelector('.mirakl-loading-indicator')
    if (indicator) {
      indicator.remove()
    }
  }

  /**
   * Show success notification
   */
  private showSuccessNotification(count: number): void {
    const notification = document.createElement('div')
    notification.className = 'mirakl-success-notification'
    notification.innerHTML = `✅ ${count} orders imported successfully!`
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #10b981;
      color: white;
      padding: 10px 15px;
      border-radius: 5px;
      z-index: 10000;
      font-family: Arial, sans-serif;
      font-size: 14px;
    `
    document.body.appendChild(notification)

    // Auto-remove after 3 seconds
    setTimeout(() => {
      notification.remove()
    }, 3000)
  }

  /**
   * Show error notification
   */
  private showErrorNotification(message: string): void {
    const notification = document.createElement('div')
    notification.className = 'mirakl-error-notification'
    notification.innerHTML = `❌ Error: ${message}`
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ef4444;
      color: white;
      padding: 10px 15px;
      border-radius: 5px;
      z-index: 10000;
      font-family: Arial, sans-serif;
      font-size: 14px;
    `
    document.body.appendChild(notification)

    // Auto-remove after 5 seconds
    setTimeout(() => {
      notification.remove()
    }, 5000)
  }

  /**
   * Allow original action to proceed (optional)
   */
  private allowOriginalAction(element: Element): void {
    // Remove our hook temporarily
    element.removeAttribute('data-mirakl-hooked')
    
    // Trigger original click
    if (element instanceof HTMLElement) {
      element.click()
    }
    
    // Re-attach hook
    setTimeout(() => {
      this.attachHook(element)
    }, 1000)
  }
}

// Initialize CSV export hook
const csvExportHook = new CSVExportHook()
