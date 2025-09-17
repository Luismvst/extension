/**
 * Fake Mirakl portal server for E2E testing
 */
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('playwright/fixtures'));

// Sample CSV data
const carrefourCSV = `Order ID,Order Date,Status,SKU,Product,Qty,Price,Buyer Name,Buyer Email,Phone,Ship To,Address 1,Address 2,City,Postal Code,Country,Total
ORD-001,2024-01-15,PENDING,SKU-123,Product A,2,25.50,John Doe,john@example.com,+34123456789,John Doe,123 Main St,Apt 4B,Madrid,28001,ES,51.00
ORD-002,2024-01-15,ACCEPTED,SKU-456,Product B,1,45.00,Jane Smith,jane@example.com,+34987654321,Jane Smith,456 Oak Ave,,Barcelona,08001,ES,45.00`;

const leroyCSV = `Order ID,Order Date,Status,SKU,Product,Qty,Price,Buyer Name,Buyer Email,Phone,Ship To,Address 1,Address 2,City,Postal Code,Country,Total
ORD-003,2024-01-15,SHIPPED,SKU-789,Product C,3,15.75,Bob Johnson,bob@example.com,+34111222333,Bob Johnson,789 Pine St,Floor 2,Valencia,46001,ES,47.25`;

const adeoCSV = `Order ID,Order Date,Status,SKU,Product,Qty,Price,Buyer Name,Buyer Email,Phone,Ship To,Address 1,Address 2,City,Postal Code,Country,Total
ORD-004,2024-01-15,PENDING,SKU-101,Product D,1,89.99,Alice Brown,alice@example.com,+34444555666,Alice Brown,101 Elm St,,Seville,41001,ES,89.99`;

// Routes
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mirakl Test Portal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }
            .marketplace {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .marketplace h3 {
                color: #333;
                margin-top: 0;
            }
            .export-button {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 5px;
                transition: background-color 0.3s;
                text-decoration: none;
                display: inline-block;
            }
            .export-button:hover {
                background: #45a049;
            }
            .export-button:disabled {
                background: #cccccc;
                cursor: not-allowed;
            }
            .status {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin-left: 10px;
            }
            .status.pending { background: #fff3cd; color: #856404; }
            .status.accepted { background: #d4edda; color: #155724; }
            .status.shipped { background: #cce5ff; color: #004085; }
            .info {
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
            }
            .instructions {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛒 Mirakl Test Portal</h1>
            <p>Simulated marketplace for testing the CSV Extension</p>
        </div>

        <div class="info">
            <h3>ℹ️ Test Information</h3>
            <p>This is a fake Mirakl portal for testing the CSV Extension. Click the export buttons below to simulate CSV downloads.</p>
        </div>

        <div class="instructions">
            <h3>📋 Testing Instructions</h3>
            <ol>
                <li>Load the Mirakl CSV Extension in Chrome</li>
                <li>Click any "Export CSV" button below</li>
                <li>The extension should intercept the download</li>
                <li>Check the extension popup for imported orders</li>
                <li>Generate TIPSA CSV from the popup</li>
            </ol>
        </div>

        <div class="marketplace">
            <h3>🏪 Carrefour Marketplace</h3>
            <p>Sample orders: 2 orders (1 PENDING, 1 ACCEPTED)</p>
            <a href="/api/export/carrefour" class="export-button" data-export-csv>
                📊 Export CSV
            </a>
            <button class="export-button" data-csv data-href="/api/export/carrefour">
                📈 Download Orders
            </button>
        </div>

        <div class="marketplace">
            <h3>🔨 Leroy Merlin Marketplace</h3>
            <p>Sample orders: 1 order (1 SHIPPED)</p>
            <a href="/api/export/leroy" class="export-button" data-export-csv>
                📊 Export CSV
            </a>
            <button class="export-button" data-csv data-href="/api/export/leroy">
                📈 Download Orders
            </button>
        </div>

        <div class="marketplace">
            <h3>🏠 Adeo Marketplace</h3>
            <p>Sample orders: 1 order (1 PENDING)</p>
            <a href="/api/export/adeo" class="export-button" data-export-csv>
                📊 Export CSV
            </a>
            <button class="export-button" data-csv data-href="/api/export/adeo">
                📈 Download Orders
            </button>
        </div>

        <div class="marketplace">
            <h3>🧪 Test Scenarios</h3>
            <p>Various test cases for different scenarios</p>
            <button class="export-button" data-export-csv data-url="/api/export/empty">
                📊 Empty CSV
            </button>
            <button class="export-button" data-export-csv data-url="/api/export/invalid">
                📊 Invalid CSV
            </button>
            <button class="export-button" data-export-csv data-url="/api/export/large">
                📊 Large CSV (100 orders)
            </button>
        </div>

        <script>
            // Add click handlers for export buttons
            document.querySelectorAll('[data-export-csv]').forEach(button => {
                button.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const url = button.dataset.url;
                    const originalText = button.textContent;
                    
                    button.textContent = '⏳ Processing...';
                    button.disabled = true;
                    
                    try {
                        const response = await fetch(url);
                        if (response.ok) {
                            const blob = await response.blob();
                            const downloadUrl = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = downloadUrl;
                            a.download = 'orders.csv';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            window.URL.revokeObjectURL(downloadUrl);
                            
                            button.textContent = '✅ Downloaded!';
                            setTimeout(() => {
                                button.textContent = originalText;
                                button.disabled = false;
                            }, 2000);
                        } else {
                            throw new Error('Export failed');
                        }
                    } catch (error) {
                        button.textContent = '❌ Error';
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.disabled = false;
                        }, 2000);
                    }
                });
            });

            // Add click handlers for CSV buttons
            document.querySelectorAll('[data-csv]').forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    const href = button.dataset.href;
                    window.location.href = href;
                });
            });
        </script>
    </body>
    </html>
  `);
});

// CSV export endpoints
app.get('/api/export/carrefour', (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="carrefour_orders.csv"');
  res.send(carrefourCSV);
});

app.get('/api/export/leroy', (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="leroy_orders.csv"');
  res.send(leroyCSV);
});

app.get('/api/export/adeo', (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="adeo_orders.csv"');
  res.send(adeoCSV);
});

app.get('/api/export/empty', (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="empty_orders.csv"');
  res.send('Order ID,Order Date,Status\n');
});

app.get('/api/export/invalid', (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="invalid_orders.csv"');
  res.send('This is not a valid CSV file');
});

app.get('/api/export/large', (req, res) => {
  // Generate large CSV with 100 orders
  let largeCSV = 'Order ID,Order Date,Status,SKU,Product,Qty,Price,Buyer Name,Buyer Email,Phone,Ship To,Address 1,Address 2,City,Postal Code,Country,Total\n';
  
  for (let i = 1; i <= 100; i++) {
    const orderId = `ORD-${i.toString().padStart(3, '0')}`;
    const status = ['PENDING', 'ACCEPTED', 'SHIPPED', 'DELIVERED', 'CANCELLED'][Math.floor(Math.random() * 5)];
    const sku = `SKU-${i.toString().padStart(3, '0')}`;
    const product = `Product ${i}`;
    const qty = Math.floor(Math.random() * 5) + 1;
    const price = (Math.random() * 100 + 10).toFixed(2);
    const buyerName = `Customer ${i}`;
    const email = `customer${i}@example.com`;
    const phone = `+34${Math.floor(Math.random() * 900000000) + 100000000}`;
    const city = ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Bilbao'][Math.floor(Math.random() * 5)];
    const postcode = Math.floor(Math.random() * 90000) + 10000;
    const total = (qty * parseFloat(price)).toFixed(2);
    
    largeCSV += `${orderId},2024-01-15,${status},${sku},${product},${qty},${price},${buyerName},${email},${phone},${buyerName},${i} Main St,,${city},${postcode},ES,${total}\n`;
  }
  
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="large_orders.csv"');
  res.send(largeCSV);
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Mirakl Test Portal running on http://localhost:${PORT}`);
  console.log(`📊 Available CSV exports:`);
  console.log(`   - Carrefour: http://localhost:${PORT}/api/export/carrefour`);
  console.log(`   - Leroy: http://localhost:${PORT}/api/export/leroy`);
  console.log(`   - Adeo: http://localhost:${PORT}/api/export/adeo`);
  console.log(`   - Empty: http://localhost:${PORT}/api/export/empty`);
  console.log(`   - Invalid: http://localhost:${PORT}/api/export/invalid`);
  console.log(`   - Large: http://localhost:${PORT}/api/export/large`);
});
