# Script simple para build de extensión
Write-Host "🚀 Building extension..." -ForegroundColor Cyan

# Limpiar dist
if (Test-Path "extension/dist") {
    Remove-Item -Recurse -Force "extension/dist"
    Write-Host "✅ Cleaned extension/dist" -ForegroundColor Green
}

# Crear dist
New-Item -ItemType Directory -Path "extension/dist" -Force | Out-Null

# Copiar archivos básicos
Copy-Item "extension/src/popup/index.html" "extension/dist/popup.html" -Force
Write-Host "✅ Copied popup.html" -ForegroundColor Green

# Crear manifest simple
$manifest = @{
    name = "Mirakl Tipsa MVP"
    description = "Chrome extension for orchestrating Mirakl marketplace orders to TIPSA carrier - MVP Version"
    version = "0.2.$(Get-Date -Format 'yyyyMMddHHmmss')"
    manifest_version = 3
    action = @{
        default_popup = "popup.html"
        default_title = "Mirakl Tipsa MVP"
    }
    background = @{
        service_worker = "background.js"
        type = "module"
    }
    permissions = @("storage", "activeTab", "scripting", "tabs", "contextMenus")
    host_permissions = @("*://*.tipsa.com/*", "*://*.tip-sa.com/*", "http://localhost:8080/*")
} | ConvertTo-Json -Depth 3

$manifest | Out-File -FilePath "extension/dist/manifest.json" -Encoding UTF8
Write-Host "✅ Created manifest.json" -ForegroundColor Green

# Crear background.js simple
$background = @"
console.log('Mirakl Tipsa MVP background script loaded');
console.log('BG SENTINEL be482d9 2025-09-21T12:30:50Z v0.2.$(Get-Date -Format 'yyyyMMddHHmmss')');

chrome.runtime.onInstalled.addListener((details) => {
  console.log('Extension installed/updated:', details.reason);
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message);
  
  switch (message.type) {
    case 'FETCH_ORDERS':
      sendResponse({ success: true, data: [{ order_id: 'MIR-001', status: 'PENDING' }] });
      break;
    case 'CREATE_SHIPMENTS':
      sendResponse({ success: true, data: [{ shipment_id: 'TIPSA-001', tracking: '1Z123456789' }] });
      break;
    case 'UPLOAD_TRACKING':
      sendResponse({ success: true, data: { message: 'Tracking uploaded' } });
      break;
    default:
      sendResponse({ success: false, error: 'Unknown message type' });
  }
  
  return true;
});
"@

$background | Out-File -FilePath "extension/dist/background.js" -Encoding UTF8
Write-Host "✅ Created background.js" -ForegroundColor Green

# Crear popup.js simple
$popup = @"
console.log('Mirakl Tipsa MVP popup loaded');

document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('root');
  
  root.innerHTML = \`
    <div style="padding: 20px; font-family: Arial, sans-serif;">
      <h1 style="color: #1976d2;">🚀 MIRAKL TIPSA MVP - DOCKER BUILD 🚀</h1>
      <p>Build: be482d9 @ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
      <div data-sentinel="POPUP-be482d9" style="display: none;"></div>
      
      <div style="margin: 20px 0;">
        <button id="load-orders" style="background: #1976d2; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer;">Cargar Pedidos</button>
        <button id="create-shipments" style="background: #4caf50; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer;">Crear Envíos</button>
        <button id="upload-tracking" style="background: #ff9800; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer;">Subir Tracking</button>
      </div>
      
      <div id="status" style="padding: 10px; background: #f5f5f5; border-radius: 4px; margin: 10px 0;">
        Ready to start workflow
      </div>
    </div>
  \`;
  
  // Event listeners
  document.getElementById('load-orders').addEventListener('click', () => {
    document.getElementById('status').textContent = 'Cargando pedidos...';
    chrome.runtime.sendMessage({ type: 'FETCH_ORDERS' }, (response) => {
      document.getElementById('status').textContent = \`Cargados \${response.data.length} pedidos\`;
    });
  });
  
  document.getElementById('create-shipments').addEventListener('click', () => {
    document.getElementById('status').textContent = 'Creando envíos...';
    chrome.runtime.sendMessage({ type: 'CREATE_SHIPMENTS' }, (response) => {
      document.getElementById('status').textContent = \`Creados \${response.data.length} envíos\`;
    });
  });
  
  document.getElementById('upload-tracking').addEventListener('click', () => {
    document.getElementById('status').textContent = 'Subiendo tracking...';
    chrome.runtime.sendMessage({ type: 'UPLOAD_TRACKING' }, (response) => {
      document.getElementById('status').textContent = response.data.message;
    });
  });
});
"@

$popup | Out-File -FilePath "extension/dist/popup.js" -Encoding UTF8
Write-Host "✅ Created popup.js" -ForegroundColor Green

Write-Host "`n🎉 Build completed!" -ForegroundColor Green
Write-Host "📁 Extension ready in extension/dist/" -ForegroundColor White
Write-Host "🔍 Load extension/dist/ in Chrome to test" -ForegroundColor Yellow
