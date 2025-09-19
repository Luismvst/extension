/**
 * Demo TIPSA website server.
 * 
 * This server provides a mock TIPSA website where users can test
 * the Chrome extension's orchestrator overlay.
 */

const express = require('express')
const cors = require('cors')
const path = require('path')

const app = express()
const PORT = process.env.PORT || 3000

// Middleware
app.use(cors())
app.use(express.json())
app.use(express.static('public'))

// Mock TIPSA website HTML
const tipsaHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TIPSA - Transporte Internacional</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .feature-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .feature-card h3 {
            color: #333;
            margin: 0 0 10px 0;
        }
        .feature-card p {
            color: #666;
            margin: 0;
        }
        .cta-button {
            background: #667eea;
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
            background: #5a6fd8;
        }
        .instructions {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
            margin-top: 20px;
        }
        .instructions h3 {
            color: #1976d2;
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
            <h1>🚚 TIPSA</h1>
            <p>Transporte Internacional de Paquetes S.A.</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Bienvenido al Portal TIPSA</h2>
                <p>Este es un sitio web de demostración para probar la extensión de Chrome "Mirakl-TIPSA Orchestrator".</p>
                
                <div class="instructions">
                    <h3>📋 Instrucciones para probar la extensión:</h3>
                    <ol>
                        <li>Asegúrate de que la extensión esté instalada y activa</li>
                        <li>La extensión debería detectar automáticamente que estás en un sitio TIPSA</li>
                        <li>Verás un overlay en la esquina superior derecha con botones para:</li>
                        <ul>
                            <li><strong>Cargar pedidos de Mirakl</strong> - Simula la carga de pedidos desde Mirakl</li>
                            <li><strong>Crear envíos TIPSA</strong> - Crea envíos con TIPSA</li>
                            <li><strong>Subir tracking a Mirakl</strong> - Sube la información de seguimiento</li>
                        </ul>
                        <li>Si no ves el overlay, haz clic en el icono de la extensión en la barra de herramientas</li>
                    </ol>
                </div>
            </div>
            
            <div class="section">
                <h2>Servicios TIPSA</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>🚛 Transporte Nacional</h3>
                        <p>Servicio de transporte terrestre para envíos nacionales con entrega en 24-48 horas.</p>
                    </div>
                    <div class="feature-card">
                        <h3>🌍 Transporte Internacional</h3>
                        <p>Servicios de transporte internacional con cobertura en toda Europa y América.</p>
                    </div>
                    <div class="feature-card">
                        <h3>📦 Paquetería Express</h3>
                        <p>Servicio express para envíos urgentes con entrega garantizada en 24 horas.</p>
                    </div>
                    <div class="feature-card">
                        <h3>💰 Pago Contra Reembolso</h3>
                        <p>Servicio de cobro contra reembolso para mayor seguridad en las transacciones.</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Acciones Rápidas</h2>
                <a href="#" class="cta-button">Crear Nuevo Envío</a>
                <a href="#" class="cta-button">Consultar Seguimiento</a>
                <a href="#" class="cta-button">Gestionar Envíos</a>
                <a href="#" class="cta-button">Descargar Etiquetas</a>
            </div>
            
            <div class="section">
                <h2>Estado del Sistema</h2>
                <p>✅ Sistema operativo</p>
                <p>✅ API de envíos disponible</p>
                <p>✅ Integración con Mirakl activa</p>
                <p>✅ Extensión de Chrome detectada</p>
            </div>
        </div>
    </div>
    
    <script>
        // Simulate some TIPSA functionality
        console.log('TIPSA Demo Website loaded');
        
        // Add some interactivity
        document.querySelectorAll('.cta-button').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                alert('Esta es una demostración. En un sitio real, esto abriría la funcionalidad correspondiente.');
            });
        });
        
        // Check if extension is available
        if (typeof chrome !== 'undefined' && chrome.runtime) {
            console.log('Chrome extension environment detected');
        }
    </script>
</body>
</html>
`

// Routes
app.get('/', (req, res) => {
  res.send(tipsaHTML)
})

app.get('/api/status', (req, res) => {
  res.json({
    status: 'operational',
    service: 'TIPSA Demo',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  })
})

app.get('/api/shipments', (req, res) => {
  res.json({
    shipments: [
      {
        id: 'TIPSA-001',
        tracking_number: '1Z123456789',
        status: 'IN_TRANSIT',
        created_at: new Date().toISOString()
      },
      {
        id: 'TIPSA-002',
        tracking_number: '1Z123456790',
        status: 'DELIVERED',
        created_at: new Date(Date.now() - 86400000).toISOString()
      }
    ]
  })
})

// Start server
app.listen(PORT, () => {
  console.log(`🚀 TIPSA Demo Website running on http://localhost:${PORT}`)
  console.log(`📊 This is a demo website for testing the Chrome extension`)
  console.log(`🔧 The extension should automatically detect this as a TIPSA website`)
})
