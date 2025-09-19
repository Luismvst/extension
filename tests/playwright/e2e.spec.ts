import { test, expect } from '@playwright/test';

test.describe('Mirakl-TIPSA Orchestrator E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to TIPSA demo website
    await page.goto('http://localhost:3001');
  });

  test('should load TIPSA demo website', async ({ page }) => {
    // Check if the page loads correctly
    await expect(page).toHaveTitle(/TIPSA Demo/);
    
    // Check if the main content is visible
    await expect(page.locator('h1')).toContainText('TIPSA Demo Website');
  });

  test('should load Mirakl demo website', async ({ page }) => {
    // Navigate to Mirakl demo
    await page.goto('http://localhost:3002');
    
    // Check if the page loads correctly
    await expect(page).toHaveTitle(/Mirakl Demo/);
    
    // Check if the main content is visible
    await expect(page.locator('h1')).toContainText('Mirakl Demo Portal');
  });

  test('should test backend API endpoints', async ({ page }) => {
    // Test health endpoint
    const healthResponse = await page.request.get('http://localhost:8080/api/v1/health/');
    expect(healthResponse.ok()).toBeTruthy();
    
    const healthData = await healthResponse.json();
    expect(healthData.status).toBe('healthy');
    expect(healthData.version).toBe('0.2.0');
  });

  test('should test Mirakl orders endpoint', async ({ page }) => {
    // Test Mirakl orders endpoint (this will use mock data)
    const ordersResponse = await page.request.get('http://localhost:8080/api/v1/marketplaces/mirakl/orders');
    expect(ordersResponse.ok()).toBeTruthy();
    
    const ordersData = await ordersResponse.json();
    expect(ordersData.orders).toBeDefined();
    expect(Array.isArray(ordersData.orders)).toBeTruthy();
  });

  test('should test TIPSA shipments endpoint', async ({ page }) => {
    // Test TIPSA shipments endpoint (this will use mock data)
    const shipmentsResponse = await page.request.post('http://localhost:8080/api/v1/carriers/tipsa/shipments/bulk', {
      data: {
        shipments: [
          {
            order_id: 'TEST-001',
            weight: 1.5,
            customer_name: 'Test Customer',
            customer_email: 'test@example.com'
          }
        ]
      }
    });
    expect(shipmentsResponse.ok()).toBeTruthy();
    
    const shipmentsData = await shipmentsResponse.json();
    expect(shipmentsData.shipments).toBeDefined();
    expect(Array.isArray(shipmentsData.shipments)).toBeTruthy();
    expect(shipmentsData.total_created).toBeGreaterThan(0);
  });

  test('should test orchestrator endpoints', async ({ page }) => {
    // Test load orders endpoint
    const loadOrdersResponse = await page.request.post('http://localhost:8080/api/v1/orchestrator/load-orders');
    expect(loadOrdersResponse.ok()).toBeTruthy();
    
    const loadOrdersData = await loadOrdersResponse.json();
    expect(loadOrdersData.success).toBeTruthy();
    expect(loadOrdersData.orders_processed).toBeGreaterThanOrEqual(0);
    
    // Test upload tracking endpoint
    const uploadTrackingResponse = await page.request.post('http://localhost:8080/api/v1/orchestrator/upload-tracking');
    expect(uploadTrackingResponse.ok()).toBeTruthy();
    
    const uploadTrackingData = await uploadTrackingResponse.json();
    expect(uploadTrackingData.success).toBeTruthy();
    expect(uploadTrackingData.orders_updated).toBeGreaterThanOrEqual(0);
  });
});