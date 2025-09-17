import { test, expect } from '@playwright/test';

test.describe('Mirakl CSV Extension E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the test portal
    await page.goto('/');
    
    // Wait for the page to load
    await expect(page.locator('h1')).toContainText('Mirakl Test Portal');
  });

  test('should display test portal correctly', async ({ page }) => {
    // Check that the portal loads with all marketplaces
    await expect(page.locator('h1')).toContainText('Mirakl Test Portal');
    await expect(page.locator('h3')).toContainText('Carrefour Marketplace');
    await expect(page.locator('h3')).toContainText('Leroy Merlin Marketplace');
    await expect(page.locator('h3')).toContainText('Adeo Marketplace');
    
    // Check that export buttons are present
    const exportButtons = page.locator('[data-export-csv]');
    await expect(exportButtons).toHaveCount(6); // 3 marketplaces + 3 test scenarios
  });

  test('should handle Carrefour CSV export', async ({ page }) => {
    // Click Carrefour export button
    const carrefourButton = page.locator('[data-export-csv][data-url="/api/export/carrefour"]');
    await carrefourButton.click();
    
    // Wait for download to start
    await expect(carrefourButton).toContainText('✅ Downloaded!');
    
    // Wait for button to reset
    await expect(carrefourButton).toContainText('📊 Export CSV');
  });

  test('should handle Leroy CSV export', async ({ page }) => {
    // Click Leroy export button
    const leroyButton = page.locator('[data-export-csv][data-url="/api/export/leroy"]');
    await leroyButton.click();
    
    // Wait for download to start
    await expect(leroyButton).toContainText('✅ Downloaded!');
    
    // Wait for button to reset
    await expect(leroyButton).toContainText('📊 Export CSV');
  });

  test('should handle Adeo CSV export', async ({ page }) => {
    // Click Adeo export button
    const adeoButton = page.locator('[data-export-csv][data-url="/api/export/adeo"]');
    await adeoButton.click();
    
    // Wait for download to start
    await expect(adeoButton).toContainText('✅ Downloaded!');
    
    // Wait for button to reset
    await expect(adeoButton).toContainText('📊 Export CSV');
  });

  test('should handle empty CSV export', async ({ page }) => {
    // Click empty CSV export button
    const emptyButton = page.locator('[data-export-csv][data-url="/api/export/empty"]');
    await emptyButton.click();
    
    // Wait for download to start
    await expect(emptyButton).toContainText('✅ Downloaded!');
    
    // Wait for button to reset
    await expect(emptyButton).toContainText('📊 Empty CSV');
  });

  test('should handle invalid CSV export', async ({ page }) => {
    // Click invalid CSV export button
    const invalidButton = page.locator('[data-export-csv][data-url="/api/export/invalid"]');
    await invalidButton.click();
    
    // Wait for download to start
    await expect(invalidButton).toContainText('✅ Downloaded!');
    
    // Wait for button to reset
    await expect(invalidButton).toContainText('📊 Invalid CSV');
  });

  test('should handle large CSV export', async ({ page }) => {
    // Click large CSV export button
    const largeButton = page.locator('[data-export-csv][data-url="/api/export/large"]');
    await largeButton.click();
    
    // Wait for download to start (may take longer for large file)
    await expect(largeButton).toContainText('✅ Downloaded!');
    
    // Wait for button to reset
    await expect(largeButton).toContainText('📊 Large CSV (100 orders)');
  });

  test('should handle CSV download via href', async ({ page }) => {
    // Click CSV download button (uses href instead of fetch)
    const downloadButton = page.locator('[data-csv][data-href="/api/export/carrefour"]');
    await downloadButton.click();
    
    // The page should navigate to the CSV endpoint
    await expect(page).toHaveURL(/.*carrefour/);
  });

  test('should display test instructions', async ({ page }) => {
    // Check that test instructions are visible
    await expect(page.locator('.instructions')).toBeVisible();
    await expect(page.locator('.instructions h3')).toContainText('Testing Instructions');
    
    // Check that the instructions contain expected steps
    const instructions = page.locator('.instructions ol li');
    await expect(instructions.nth(0)).toContainText('Load the Mirakl CSV Extension in Chrome');
    await expect(instructions.nth(1)).toContainText('Click any "Export CSV" button below');
    await expect(instructions.nth(2)).toContainText('The extension should intercept the download');
  });

  test('should display marketplace information', async ({ page }) => {
    // Check Carrefour marketplace info
    const carrefourSection = page.locator('.marketplace').filter({ hasText: 'Carrefour' });
    await expect(carrefourSection.locator('p')).toContainText('Sample orders: 2 orders (1 PENDING, 1 ACCEPTED)');
    
    // Check Leroy marketplace info
    const leroySection = page.locator('.marketplace').filter({ hasText: 'Leroy' });
    await expect(leroySection.locator('p')).toContainText('Sample orders: 1 order (1 SHIPPED)');
    
    // Check Adeo marketplace info
    const adeoSection = page.locator('.marketplace').filter({ hasText: 'Adeo' });
    await expect(adeoSection.locator('p')).toContainText('Sample orders: 1 order (1 PENDING)');
  });

  test('should handle multiple rapid clicks', async ({ page }) => {
    // Click multiple export buttons rapidly
    const buttons = page.locator('[data-export-csv]');
    const buttonCount = await buttons.count();
    
    // Click all buttons in quick succession
    for (let i = 0; i < buttonCount; i++) {
      await buttons.nth(i).click();
    }
    
    // Wait a bit for all downloads to process
    await page.waitForTimeout(2000);
    
    // All buttons should eventually reset
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      await expect(button).not.toContainText('⏳ Processing...');
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that the page is still usable on mobile
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('[data-export-csv]').first()).toBeVisible();
    
    // Try clicking a button on mobile
    const firstButton = page.locator('[data-export-csv]').first();
    await firstButton.click();
    
    // Should still work on mobile
    await expect(firstButton).toContainText('✅ Downloaded!');
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Mock network failure for one of the endpoints
    await page.route('/api/export/carrefour', route => {
      route.abort('failed');
    });
    
    // Click the button that will fail
    const carrefourButton = page.locator('[data-export-csv][data-url="/api/export/carrefour"]');
    await carrefourButton.click();
    
    // Should show error state
    await expect(carrefourButton).toContainText('❌ Error');
    
    // Should reset after timeout
    await expect(carrefourButton).toContainText('📊 Export CSV');
  });
});

test.describe('Extension Integration Tests', () => {
  test('should work with extension loaded', async ({ page, context }) => {
    // This test would require the extension to be loaded
    // For now, we'll just test the portal functionality
    
    await page.goto('/');
    
    // Simulate extension behavior by checking for extension-specific elements
    // In a real test, you would load the extension and test the actual integration
    
    // Test that the portal is ready for extension interaction
    await expect(page.locator('[data-export-csv]')).toBeVisible();
    
    // Test that CSV data is accessible
    const response = await page.request.get('/api/export/carrefour');
    expect(response.status()).toBe(200);
    
    const csvContent = await response.text();
    expect(csvContent).toContain('Order ID,Order Date,Status');
    expect(csvContent).toContain('ORD-001');
  });
});
