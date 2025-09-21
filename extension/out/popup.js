console.log('Mirakl Tipsa MVP popup loaded');

document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('root');
  
  root.innerHTML = \
    <div style="padding: 20px; font-family: Arial, sans-serif;">
      <h1 style="color: #1976d2;">ðŸš€ MIRAKL TIPSA MVP - DOCKER BUILD ðŸš€</h1>
      <p>Build: be482d9 @ 2025-09-21 12:40:05</p>
      <div data-sentinel="POPUP-be482d9" style="display: none;"></div>
      
      <div style="margin: 20px 0;">
        <button id="load-orders" style="background: #1976d2; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer;">Cargar Pedidos</button>
        <button id="create-shipments" style="background: #4caf50; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer;">Crear EnvÃ­os</button>
        <button id="upload-tracking" style="background: #ff9800; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer;">Subir Tracking</button>
      </div>
      
      <div id="status" style="padding: 10px; background: #f5f5f5; border-radius: 4px; margin: 10px 0;">
        Ready to start workflow
      </div>
    </div>
  \;
  
  // Event listeners
  document.getElementById('load-orders').addEventListener('click', () => {
    document.getElementById('status').textContent = 'Cargando pedidos...';
    chrome.runtime.sendMessage({ type: 'FETCH_ORDERS' }, (response) => {
      document.getElementById('status').textContent = \Cargados \ pedidos\;
    });
  });
  
  document.getElementById('create-shipments').addEventListener('click', () => {
    document.getElementById('status').textContent = 'Creando envÃ­os...';
    chrome.runtime.sendMessage({ type: 'CREATE_SHIPMENTS' }, (response) => {
      document.getElementById('status').textContent = \Creados \ envÃ­os\;
    });
  });
  
  document.getElementById('upload-tracking').addEventListener('click', () => {
    document.getElementById('status').textContent = 'Subiendo tracking...';
    chrome.runtime.sendMessage({ type: 'UPLOAD_TRACKING' }, (response) => {
      document.getElementById('status').textContent = response.data.message;
    });
  });
});
