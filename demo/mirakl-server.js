/**
 * Demo Mirakl portal server.
 * 
 * This server provides a mock Mirakl marketplace portal where users can test
 * the Chrome extension's order fetching functionality.
 */

const express = require('express')
const cors = require('cors')

const app = express()
const PORT = process.env.PORT || 3000

// Middleware
app.use(cors())
app.use(express.json())

// Mock Mirakl portal HTML
const miraklHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mirakl Marketplace Portal</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .header h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #666;
            margin: 10px 0 0 0;
        }
        .content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #ff6b6b;
            padding-bottom: 10px;
        }
        .orders-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .order-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ff6b6b;
        }
        .order-card h3 {
            color: #333;
            margin: 0 0 10px 0;
        }
        .order-card p {
            color: #666;
            margin: 5px 0;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-shipping {
            background: #e3f2fd;
            color: #1976d2;
        }
        .status-pending {
            background: #fff3e0;
            color: #f57c00;
        }
        .status-delivered {
            background: #e8f5e8;
            color: #2e7d32;
        }
        .cta-button {
            background: #ff6b6b;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px 10px 10px 0;
            transition: background 0.3s;
        }
        .cta-button:hover {
            background: #ff5252;
        }
        .instructions {
            background: #ffebee;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #f44336;
            margin-top: 20px;
        }
        .instructions h3 {
            color: #d32f2f;
            margin: 0 0 10px 0;
        }
        .instructions ol {
            color: #333;
            margin: 0;
        }
        .instructions li {
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛒 Mirakl Marketplace</h1>
            <p>Portal de Gestión de Pedidos</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Panel de Control</h2>
                <p>Bienvenido al portal de gestión de pedidos de Mirakl. Desde aquí puedes gestionar todos tus pedidos y envíos.</p>
                
                <div class="instructions">
                    <h3>📋 Instrucciones para probar la extensión:</h3>
                    <ol>
                        <li>Este portal simula un marketplace de Mirakl</li>
                        <li>Los pedidos mostrados son datos de demostración</li>
                        <li>La extensión puede cargar estos pedidos para crear envíos en TIPSA</li>
                        <li>Usa el botón "Exportar CSV" para simular la descarga de pedidos</li>
                        <li>La extensión interceptará esta acción y procesará los pedidos</li>
                    </ol>
                </div>
            </div>
            
            <div class="section">
                <h2>Pedidos Recientes</h2>
                <div class="orders-grid">
                    <div class="order-card">
                        <h3>Pedido #MIR-001</h3>
                        <p><strong>Cliente:</strong> Juan Pérez</p>
                        <p><strong>Producto:</strong> Producto A</p>
                        <p><strong>Peso:</strong> 2.5 kg</p>
                        <p><strong>Total:</strong> 45.99€</p>
                        <span class="status-badge status-shipping">Enviando</span>
                    </div>
                    
                    <div class="order-card">
                        <h3>Pedido #MIR-002</h3>
                        <p><strong>Cliente:</strong> María García</p>
                        <p><strong>Producto:</strong> Producto B</p>
                        <p><strong>Peso:</strong> 1.8 kg</p>
                        <p><strong>Total:</strong> 32.50€</p>
                        <span class="status-badge status-pending">Pendiente</span>
                    </div>
                    
                    <div class="order-card">
                        <h3>Pedido #MIR-003</h3>
                        <p><strong>Cliente:</strong> Carlos López</p>
                        <p><strong>Producto:</strong> Producto C</p>
                        <p><strong>Peso:</strong> 3.2 kg</p>
                        <p><strong>Total:</strong> 67.99€</p>
                        <span class="status-badge status-shipping">Enviando</span>
                    </div>
                    
                    <div class="order-card">
                        <h3>Pedido #MIR-004</h3>
                        <p><strong>Cliente:</strong> Ana Martín</p>
                        <p><strong>Producto:</strong> Producto D</p>
                        <p><strong>Peso:</strong> 0.8 kg</p>
                        <p><strong>Total:</strong> 19.99€</p>
                        <span class="status-badge status-delivered">Entregado</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Acciones de Pedidos</h2>
                <button class="cta-button" onclick="exportOrders()">📊 Exportar CSV</button>
                <button class="cta-button" onclick="refreshOrders()">🔄 Actualizar</button>
                <button class="cta-button" onclick="createShipment()">🚚 Crear Envío</button>
                <button class="cta-button" onclick="trackOrders()">📦 Seguimiento</button>
            </div>
            
            <div class="section">
                <h2>Estadísticas</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <h3 style="margin: 0; color: #333;">15</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">Pedidos Hoy</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <h3 style="margin: 0; color: #333;">8</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">En Envío</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <h3 style="margin: 0; color: #333;">1,247€</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">Ventas Hoy</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <h3 style="margin: 0; color: #333;">98%</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">Tasa de Entrega</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Simulate Mirakl functionality
        console.log('Mirakl Demo Portal loaded');
        
        function exportOrders() {
            alert('Exportando pedidos a CSV...\\n\\nEn un escenario real, la extensión interceptaría esta acción y procesaría los pedidos automáticamente.');
            
            // Simulate CSV download
            const csvData = \`order_id,customer_name,product,weight,total,status
MIR-001,Juan Pérez,Producto A,2.5,45.99,SHIPPING
MIR-002,María García,Producto B,1.8,32.50,PENDING
MIR-003,Carlos López,Producto C,3.2,67.99,SHIPPING
MIR-004,Ana Martín,Producto D,0.8,19.99,DELIVERED\`;
            
            const blob = new Blob([csvData], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mirakl_orders.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }
        
        function refreshOrders() {
            alert('Actualizando pedidos...');
            location.reload();
        }
        
        function createShipment() {
            alert('Creando envío...\\n\\nEn un escenario real, esto abriría el formulario de creación de envíos.');
        }
        
        function trackOrders() {
            alert('Consultando seguimiento...\\n\\nEn un escenario real, esto mostraría el estado de los envíos.');
        }
        
        // Add some interactivity to order cards
        document.querySelectorAll('.order-card').forEach(card => {
            card.addEventListener('click', () => {
                const orderId = card.querySelector('h3').textContent;
                alert(\`Detalles del pedido: \${orderId}\\n\\nEn un escenario real, esto abriría los detalles completos del pedido.\`);
            });
        });
    </script>
</body>
</html>
`

// Mock orders data
const mockOrders = [
  {
    order_id: 'MIR-001',
    customer_name: 'Juan Pérez',
    customer_email: 'juan.perez@email.com',
    product: 'Producto A',
    weight: 2.5,
    total: 45.99,
    status: 'SHIPPING',
    created_at: new Date().toISOString()
  },
  {
    order_id: 'MIR-002',
    customer_name: 'María García',
    customer_email: 'maria.garcia@email.com',
    product: 'Producto B',
    weight: 1.8,
    total: 32.50,
    status: 'PENDING',
    created_at: new Date(Date.now() - 3600000).toISOString()
  },
  {
    order_id: 'MIR-003',
    customer_name: 'Carlos López',
    customer_email: 'carlos.lopez@email.com',
    product: 'Producto C',
    weight: 3.2,
    total: 67.99,
    status: 'SHIPPING',
    created_at: new Date(Date.now() - 7200000).toISOString()
  },
  {
    order_id: 'MIR-004',
    customer_name: 'Ana Martín',
    customer_email: 'ana.martin@email.com',
    product: 'Producto D',
    weight: 0.8,
    total: 19.99,
    status: 'DELIVERED',
    created_at: new Date(Date.now() - 86400000).toISOString()
  }
]

// Routes
app.get('/', (req, res) => {
  res.send(miraklHTML)
})

app.get('/api/orders', (req, res) => {
  res.json({
    orders: mockOrders,
    total: mockOrders.length,
    page: 1,
    limit: 50
  })
})

app.get('/api/orders/export', (req, res) => {
  const csvData = mockOrders.map(order => 
    `${order.order_id},${order.customer_name},${order.product},${order.weight},${order.total},${order.status}`
  ).join('\\n')
  
  const csv = `order_id,customer_name,product,weight,total,status\\n${csvData}`
  
  res.setHeader('Content-Type', 'text/csv')
  res.setHeader('Content-Disposition', 'attachment; filename=mirakl_orders.csv')
  res.send(csv)
})

app.get('/api/orders/:id', (req, res) => {
  const order = mockOrders.find(o => o.order_id === req.params.id)
  if (order) {
    res.json(order)
  } else {
    res.status(404).json({ error: 'Order not found' })
  }
})

app.put('/api/orders/:id/tracking', (req, res) => {
  const { tracking_number, carrier_code, carrier_name } = req.body
  const order = mockOrders.find(o => o.order_id === req.params.id)
  
  if (order) {
    order.tracking_number = tracking_number
    order.carrier_code = carrier_code
    order.carrier_name = carrier_name
    order.updated_at = new Date().toISOString()
    
    res.json({ 
      success: true, 
      message: 'Tracking information updated successfully',
      order 
    })
  } else {
    res.status(404).json({ error: 'Order not found' })
  }
})

// Start server
app.listen(PORT, () => {
  console.log(`🛒 Mirakl Demo Portal running on http://localhost:${PORT}`)
  console.log(`📊 This is a demo portal for testing the Chrome extension`)
  console.log(`🔧 The extension can fetch orders from this portal`)
})
