import { test, expect } from '@playwright/test'

test.describe('Chrome Extension E2E', () => {
  test('should load extension and show sentinels', async ({ page }) => {
    // Navigate to chrome://extensions
    await page.goto('chrome://extensions/')
    
    // Wait for extensions to load
    await page.waitForTimeout(2000)
    
    // Look for our extension
    const extensionCard = page.locator('extensions-item').filter({ hasText: 'Mirakl Tipsa MVP' })
    await expect(extensionCard).toBeVisible()
    
    // Check if extension is enabled
    const toggle = extensionCard.locator('cr-toggle')
    await expect(toggle).toBeVisible()
  })

  test('should open popup and show build info', async ({ page, context }) => {
    // This test would need the extension to be loaded
    // In a real scenario, you'd load the extension first
    
    // Navigate to popup
    await page.goto('chrome-extension://temp-extension-id/popup/index.html')
    
    // Check for build info
    await expect(page.locator('text=/Build:/')).toBeVisible()
    
    // Check for sentinel
    const sentinel = page.locator('[data-sentinel]')
    await expect(sentinel).toBeVisible()
    
    // Check for main UI elements
    await expect(page.locator('text=Mirakl Tipsa MVP')).toBeVisible()
  })

  test('should handle extension workflow', async ({ page }) => {
    // This would test the actual workflow
    await page.goto('chrome-extension://temp-extension-id/popup/index.html')
    
    // Check for main buttons
    const loadOrdersBtn = page.locator('button:has-text("Cargar Pedidos")')
    await expect(loadOrdersBtn).toBeVisible()
    
    const createShipmentsBtn = page.locator('button:has-text("Crear Envíos")')
    await expect(createShipmentsBtn).toBeVisible()
    
    const uploadTrackingBtn = page.locator('button:has-text("Subir Tracking")')
    await expect(uploadTrackingBtn).toBeVisible()
  })
})
