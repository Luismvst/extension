import { sendMessage } from '@/common/messages'

/**
 * Inject floating button for CSV export
 */
export class FloatingExportButton {
  private button: HTMLButtonElement | null = null
  private isVisible = false

  constructor() {
    this.createButton()
    this.setupVisibilityToggle()
  }

  /**
   * Create floating export button
   */
  private createButton(): void {
    this.button = document.createElement('button')
    this.button.id = 'mirakl-export-button'
    this.button.innerHTML = '📊 Export CSV'
    this.button.title = 'Export CSV and send to Mirakl Extension'
    
    this.button.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #3b82f6;
      color: white;
      border: none;
      padding: 12px 20px;
      border-radius: 25px;
      cursor: pointer;
      font-family: Arial, sans-serif;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
      z-index: 10000;
      transition: all 0.2s ease;
      display: none;
    `

    // Add hover effects
    this.button.addEventListener('mouseenter', () => {
      if (this.button) {
        this.button.style.transform = 'translateY(-2px)'
        this.button.style.boxShadow = '0 6px 16px rgba(59, 130, 246, 0.4)'
      }
    })

    this.button.addEventListener('mouseleave', () => {
      if (this.button) {
        this.button.style.transform = 'translateY(0)'
        this.button.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)'
      }
    })

    // Add click handler
    this.button.addEventListener('click', () => {
      this.handleExportClick()
    })

    document.body.appendChild(this.button)
  }

  /**
   * Setup visibility toggle based on page content
   */
  private setupVisibilityToggle(): void {
    // Show button when export-related elements are found
    const observer = new MutationObserver(() => {
      this.checkForExportElements()
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true
    })

    // Initial check
    this.checkForExportElements()
  }

  /**
   * Check for export elements and show/hide button accordingly
   */
  private checkForExportElements(): void {
    const exportSelectors = [
      'a[href*="export"]',
      'a[href*="csv"]',
      'button[data-export]',
      'button[data-csv]',
      '.export-button',
      '.csv-export',
      '[data-testid*="export"]',
      '[data-testid*="csv"]'
    ]

    const hasExportElements = exportSelectors.some(selector => 
      document.querySelector(selector) !== null
    )

    if (hasExportElements && !this.isVisible) {
      this.show()
    } else if (!hasExportElements && this.isVisible) {
      this.hide()
    }
  }

  /**
   * Show floating button
   */
  private show(): void {
    if (this.button && !this.isVisible) {
      this.button.style.display = 'block'
      this.button.style.animation = 'slideIn 0.3s ease-out'
      this.isVisible = true
    }
  }

  /**
   * Hide floating button
   */
  private hide(): void {
    if (this.button && this.isVisible) {
      this.button.style.animation = 'slideOut 0.3s ease-in'
      setTimeout(() => {
        if (this.button) {
          this.button.style.display = 'none'
        }
        this.isVisible = false
      }, 300)
    }
  }

  /**
   * Handle export button click
   */
  private async handleExportClick(): Promise<void> {
    if (!this.button) return

    try {
      // Show loading state
      this.button.innerHTML = '⏳ Processing...'
      this.button.disabled = true

      // Find export elements and trigger them
      const exportElements = this.findExportElements()
      
      if (exportElements.length === 0) {
        throw new Error('No export elements found on this page')
      }

      // Trigger the first export element
      const firstElement = exportElements[0]
      firstElement.click()

      // Show success message
      this.button.innerHTML = '✅ Exported!'
      this.button.style.background = '#10b981'

      // Reset after 2 seconds
      setTimeout(() => {
        if (this.button) {
          this.button.innerHTML = '📊 Export CSV'
          this.button.style.background = '#3b82f6'
          this.button.disabled = false
        }
      }, 2000)

    } catch (error) {
      console.error('Error handling export click:', error)
      
      // Show error state
      this.button.innerHTML = '❌ Error'
      this.button.style.background = '#ef4444'

      // Reset after 3 seconds
      setTimeout(() => {
        if (this.button) {
          this.button.innerHTML = '📊 Export CSV'
          this.button.style.background = '#3b82f6'
          this.button.disabled = false
        }
      }, 3000)
    }
  }

  /**
   * Find export elements on the page
   */
  private findExportElements(): Element[] {
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

    const elements: Element[] = []
    
    for (const selector of selectors) {
      const found = document.querySelectorAll(selector)
      elements.push(...Array.from(found))
    }

    return elements
  }

  /**
   * Update button text
   */
  public updateText(text: string): void {
    if (this.button) {
      this.button.innerHTML = text
    }
  }

  /**
   * Update button style
   */
  public updateStyle(styles: Partial<CSSStyleDeclaration>): void {
    if (this.button) {
      Object.assign(this.button.style, styles)
    }
  }

  /**
   * Destroy button
   */
  public destroy(): void {
    if (this.button) {
      this.button.remove()
      this.button = null
    }
    this.isVisible = false
  }
}

// Add CSS animations
const style = document.createElement('style')
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100px);
      opacity: 0;
    }
  }
`
document.head.appendChild(style)

// Initialize floating button
const floatingButton = new FloatingExportButton()
