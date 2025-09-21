import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Alert,
  CircularProgress,
  Tooltip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Badge
} from '@mui/material';
import {
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { ApiClient } from '@/lib/api';
import { FrontLogger } from '@/lib/frontLogger';
import { CsvExporter } from '@/lib/exportCsv';
import { Order, ShipmentResult } from '@/types';
import { BUILD_INFO } from '@/lib/buildInfo';

// Types
type LoadingAction = 'LOAD' | 'CREATE' | 'UPLOAD' | null;
type CarrierType = 'TIPSA' | 'DHL' | 'UPS' | 'ONTIME';

interface PredictedCarrier {
  carrier: CarrierType;
  reason: string;
}

// Carrier prediction function
function predictCarrier(order: Order): PredictedCarrier {
  const country = order?.shipping_address?.country?.toUpperCase?.() || 'ES';
  
  if ((order?.weight ?? 0) > 20) {
    return { carrier: 'TIPSA', reason: 'HEAVY>20kg' };
  }
  
  if (order?.payment_method?.toUpperCase?.() === 'COD') {
    return { carrier: 'TIPSA', reason: 'COD' };
  }
  
  if (order?.shipping_method?.toUpperCase?.() === 'EXPRESS') {
    return { carrier: 'DHL', reason: 'EXPRESS' };
  }
  
  if (country !== 'ES') {
    return { carrier: 'DHL', reason: 'INTERNATIONAL' };
  }
  
  return { carrier: 'TIPSA', reason: 'DEFAULT_STANDARD' };
}

// Carrier chip colors
const getCarrierColor = (carrier: CarrierType): 'success' | 'warning' | 'default' | 'primary' => {
  switch (carrier) {
    case 'TIPSA': return 'success';
    case 'DHL': return 'warning';
    case 'UPS': return 'default';
    case 'ONTIME': return 'primary';
    default: return 'default';
  }
};

// Status chip colors
const getStatusColor = (status: string): 'success' | 'warning' | 'error' | 'default' => {
  switch (status.toUpperCase()) {
    case 'SHIPPED': return 'success';
    case 'SHIPPING': return 'warning';
    case 'PENDING': return 'error';
    default: return 'default';
  }
};

export default function PopupApp() {
  // State
  const [selectedMarketplace] = useState<'Mirakl'>('Mirakl');
  const [selectedCarrier, setSelectedCarrier] = useState<CarrierType>('TIPSA');
  const [statusFilter, setStatusFilter] = useState<string[]>(['PENDING']);
  const [orders, setOrders] = useState<Order[]>([]);
  const [shipments, setShipments] = useState<ShipmentResult[]>([]);
  const [loadingAction, setLoadingAction] = useState<LoadingAction>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [csvConfig, setCsvConfig] = useState({
    producto: '48',
    tipoBultos: 'PTR180P',
    departamentoCliente: 'empresarial',
    codigoCliente: '89'
  });

  // API Client
  const apiClient = new ApiClient();

  // Load initial state
  useEffect(() => {
    loadInitialState();
  }, []);

  const loadInitialState = async () => {
    try {
      // Auto-authenticate
      await apiClient.getExtensionToken();
      
      // Load CSV config
      const config = await CsvExporter.loadConfig();
      setCsvConfig(config);
      
      // Load cached data
      const cachedOrders = await chrome.storage.local.get(['ordersCache']);
      if (cachedOrders.ordersCache) {
        setOrders(cachedOrders.ordersCache);
      }
      
      const cachedShipments = await chrome.storage.local.get(['shipmentsCache']);
      if (cachedShipments.shipmentsCache) {
        setShipments(cachedShipments.shipmentsCache);
      }
    } catch (err) {
      console.error('Failed to load initial state:', err);
    }
  };

  // Step 1: Load Orders
  const handleLoadOrders = async () => {
    setLoadingAction('LOAD');
    setError(null);
    setNotice(null);

    try {
      const statusParam = statusFilter.join(',');
      const response = await apiClient.getMiraklOrders({ status: statusParam, limit: 50 });
      
      setOrders(response.orders || []);
      
      // Cache orders
      await chrome.storage.local.set({ ordersCache: response.orders || [] });
      
      // Log action
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'LOAD_ORDERS',
        ok: true,
        msg: `Loaded ${response.orders?.length || 0} orders`,
        details: { 
          count: response.orders?.length || 0, 
          statusFilter: statusParam,
          hash: btoa(JSON.stringify(response.orders?.map((o: any) => o.order_id) || []))
        }
      });

      setNotice(`✅ Cargados ${response.orders?.length || 0} pedidos`);
    } catch (err: any) {
      const errorMsg = err.message || 'Error al cargar pedidos';
      setError(errorMsg);
      
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'ERROR',
        ok: false,
        msg: errorMsg,
        details: { action: 'LOAD_ORDERS', error: err.message }
      });
    } finally {
      setLoadingAction(null);
    }
  };

  // Step 2: Create Shipments
  const handleCreateShipments = async () => {
    if (orders.length === 0) {
      setError('No hay pedidos para crear envíos');
      return;
    }

    setLoadingAction('CREATE');
    setError(null);
    setNotice(null);

    try {
      const response = await apiClient.createShipments({ shipments: orders as any });
      
      setShipments(response.shipments || []);
      
      // Cache shipments
      await chrome.storage.local.set({ shipmentsCache: response.shipments || [] });
      
      // Log action
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'CREATE_SHIPMENTS',
        ok: true,
        msg: `Created ${response.shipments?.length || 0} shipments`,
        details: { 
          created: response.shipments?.length || 0,
          failed: 0,
          hash: btoa(JSON.stringify(response.shipments?.map((s: any) => s.shipment_id) || []))
        }
      });

      setNotice(`✅ Creados ${response.shipments?.length || 0} envíos`);
    } catch (err: any) {
      const errorMsg = err.message || 'Error al crear envíos';
      setError(errorMsg);
      
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'ERROR',
        ok: false,
        msg: errorMsg,
        details: { action: 'CREATE_SHIPMENTS', error: err.message }
      });
    } finally {
      setLoadingAction(null);
    }
  };

  // Step 3: Upload Tracking
  const handleUploadTracking = async () => {
    if (shipments.length === 0) {
      setError('No hay envíos para subir tracking');
      return;
    }

    setLoadingAction('UPLOAD');
    setError(null);
    setNotice(null);

    try {
      const trackingData = shipments.map(shipment => ({
        order_id: shipment.order_id,
        tracking_number: shipment.tracking_number,
        carrier_code: 'tipsa',
        carrier_name: 'TIPSA'
      }));

      const response = await apiClient.uploadTrackingToMirakl(trackingData);
      
      // Update orders status to SHIPPED
      setOrders(prevOrders => 
        prevOrders.map(order => {
          const hasTracking = trackingData.some(t => t.order_id === order.order_id);
          return hasTracking ? { ...order, status: 'SHIPPED', syncedToMirakl: true } : order;
        })
      );
      
      // Log action
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'UPLOAD_TRACKING',
        ok: true,
        msg: `Uploaded tracking for ${response.orders_updated || 0} orders`,
        details: { 
          updated: response.orders_updated || 0,
          errors: response.tracking_updates?.filter((u: any) => u.status === 'ERROR').length || 0,
          hash: btoa(JSON.stringify(trackingData.map(t => t.order_id)))
        }
      });

      setNotice(`✅ Subido tracking para ${response.orders_updated || 0} pedidos`);
    } catch (err: any) {
      const errorMsg = err.message || 'Error al subir tracking';
      setError(errorMsg);
      
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'ERROR',
        ok: false,
        msg: errorMsg,
        details: { action: 'UPLOAD_TRACKING', error: err.message }
      });
    } finally {
      setLoadingAction(null);
    }
  };

  // Download Label
  const handleDownloadLabel = async (shipment: ShipmentResult) => {
    try {
      const response = await apiClient.getShipmentLabel(shipment.shipment_id);
      
      const blob = new Blob([response as any], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `label_${shipment.tracking_number}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
      
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'DOWNLOAD_LABEL',
        ok: true,
        msg: `Downloaded label for ${shipment.tracking_number}`,
        details: { shipment_id: shipment.shipment_id, tracking_number: shipment.tracking_number }
      });
    } catch (err: any) {
      setError(`Error al descargar etiqueta: ${err.message}`);
      
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'ERROR',
        ok: false,
        msg: `Failed to download label for ${shipment.tracking_number}`,
        details: { error: err.message }
      });
    }
  };

  // Export CSV
  const handleExportCsv = async () => {
    try {
      const exporter = new CsvExporter(csvConfig);
      await exporter.downloadCsv(orders, shipments);
      
      await FrontLogger.push({
        ts: new Date().toISOString(),
        action: 'EXPORT_CSV',
        ok: true,
        msg: `Exported CSV with ${orders.length} orders`,
        details: { count: orders.length }
      });
      
      setNotice('✅ CSV exportado correctamente');
    } catch (err: any) {
      setError(`Error al exportar CSV: ${err.message}`);
    }
  };

  // Download Frontend Logs
  const handleDownloadLogs = async () => {
    try {
      await FrontLogger.downloadLogs();
      setNotice('✅ Logs descargados correctamente');
    } catch (err: any) {
      setError(`Error al descargar logs: ${err.message}`);
    }
  };

  // Get status breakdown
  const getStatusBreakdown = () => {
    const breakdown: Record<string, number> = {};
    statusFilter.forEach(status => {
      breakdown[status] = orders.filter(order => order.status === status).length;
    });
    return breakdown;
  };

  const statusBreakdown = getStatusBreakdown();
  const totalOrders = orders.length;
  const totalShipments = shipments.length;
  const shippedOrders = orders.filter(order => order.status === 'SHIPPED').length;

  return (
    <Box sx={{ width: '800px', maxWidth: '100vw', p: 2, minHeight: '600px' }}>
      {/* Header */}
      <Box sx={{ mb: 3, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🚀 MIRAKL TIPSA MVP - DOCKER BUILD 🚀
        </Typography>
        <Chip label="MVP Version" color="success" size="small" />
        <Typography variant="caption" display="block" sx={{ mt: 1, color: 'text.secondary' }}>
          Build: {BUILD_INFO.commit} @ {new Date(BUILD_INFO.buildTime).toLocaleString()}
        </Typography>
        {/* POPUP SENTINEL for build verification */}
        <div data-sentinel={`POPUP-${BUILD_INFO.commit}`} style={{ display: 'none' }} />
        <div style={{ display: 'block', fontSize: '12px', color: 'red', fontWeight: 'bold', marginTop: '10px' }}>
          ✅ EXTENSIÓN ACTUALIZADA - NUEVA UI MVP
        </div>
      </Box>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Marketplace</InputLabel>
              <Select value={selectedMarketplace} disabled>
                <MenuItem value="Mirakl">Mirakl</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Carrier</InputLabel>
              <Select value={selectedCarrier} onChange={(e) => setSelectedCarrier(e.target.value as CarrierType)}>
                <MenuItem value="TIPSA">TIPSA</MenuItem>
                <MenuItem value="DHL" disabled>DHL (No disponible)</MenuItem>
                <MenuItem value="UPS" disabled>UPS (No disponible)</MenuItem>
                <MenuItem value="ONTIME" disabled>OnTime (No disponible)</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Estados Mirakl</InputLabel>
              <Select
                multiple
                value={statusFilter}
                onChange={(e) => setStatusFilter(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
                renderValue={(selected) => (selected as string[]).join(', ')}
              >
                <MenuItem value="PENDING">PENDING</MenuItem>
                <MenuItem value="SHIPPING">SHIPPING</MenuItem>
                <MenuItem value="SHIPPED">SHIPPED</MenuItem>
              </Select>
            </FormControl>

            <Chip 
              label={`Status usado: ${statusFilter.join(', ')}`} 
              color="primary" 
              variant="outlined" 
              size="small" 
            />
          </Box>
        </CardContent>
      </Card>

      {/* Stepper */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stepper activeStep={shipments.length > 0 ? (shippedOrders > 0 ? 3 : 2) : (orders.length > 0 ? 1 : 0)}>
            <Step>
              <StepLabel>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Orders (Mirakl)
                  {totalOrders > 0 && <Badge badgeContent={totalOrders} color="primary" />}
                </Box>
              </StepLabel>
            </Step>
            <Step>
              <StepLabel>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Shipments (TIPSA)
                  {totalShipments > 0 && <Badge badgeContent={totalShipments} color="primary" />}
                </Box>
              </StepLabel>
            </Step>
            <Step>
              <StepLabel>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Tracking (Mirakl)
                  {shippedOrders > 0 && <CheckCircleIcon color="success" />}
                </Box>
              </StepLabel>
            </Step>
          </Stepper>
        </CardContent>
      </Card>

      {/* Notifications */}
      {notice && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setNotice(null)}>
          {notice}
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Step 1: Load Orders */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Paso 1: Cargar Pedidos (Mirakl)</Typography>
            <Button
              variant="contained"
              onClick={handleLoadOrders}
              disabled={loadingAction !== null}
              startIcon={loadingAction === 'LOAD' ? <CircularProgress size={20} /> : <RefreshIcon />}
            >
              {loadingAction === 'LOAD' ? 'Cargando...' : 'Cargar Pedidos'}
            </Button>
          </Box>

          {totalOrders > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Total: {totalOrders} pedidos | 
                {Object.entries(statusBreakdown).map(([status, count]) => (
                  <span key={status}> {status}: {count} |</span>
                ))}
              </Typography>
            </Box>
          )}

          {orders.length > 0 && (
            <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Order ID</TableCell>
                    <TableCell>Cliente</TableCell>
                    <TableCell>Peso (kg)</TableCell>
                    <TableCell>Importe</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Predicted Carrier</TableCell>
                    <TableCell>Motivo</TableCell>
                    <TableCell>País</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {orders.map((order) => {
                    const predicted = predictCarrier(order);
                    return (
                      <TableRow key={order.order_id}>
                        <TableCell>{order.order_id}</TableCell>
                        <TableCell>{order.customer_name}</TableCell>
                        <TableCell>{order.weight}</TableCell>
                        <TableCell>{order.total_amount} {order.currency}</TableCell>
                        <TableCell>
                          <Chip 
                            label={order.status} 
                            color={getStatusColor(order.status)} 
                            size="small"
                            icon={order.syncedToMirakl ? <CheckCircleIcon /> : undefined}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={predicted.carrier} 
                            color={getCarrierColor(predicted.carrier)} 
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title={predicted.reason}>
                            <Chip label={predicted.reason} size="small" variant="outlined" />
                          </Tooltip>
                        </TableCell>
                        <TableCell>{order.shipping_address?.country || 'ES'}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Step 2: Create Shipments */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Paso 2: Crear Envíos (TIPSA)</Typography>
            <Button
              variant="contained"
              onClick={handleCreateShipments}
              disabled={loadingAction !== null || orders.length === 0}
              startIcon={loadingAction === 'CREATE' ? <CircularProgress size={20} /> : undefined}
            >
              {loadingAction === 'CREATE' ? 'Creando...' : 'Crear Envíos'}
            </Button>
          </Box>

          {shipments.length > 0 && (
            <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Order ID</TableCell>
                    <TableCell>Shipment ID</TableCell>
                    <TableCell>Tracking</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {shipments.map((shipment) => (
                    <TableRow key={shipment.shipment_id}>
                      <TableCell>{shipment.order_id}</TableCell>
                      <TableCell>{shipment.shipment_id}</TableCell>
                      <TableCell>{shipment.tracking_number}</TableCell>
                      <TableCell>
                        <Chip 
                          label={shipment.status} 
                          color={getStatusColor(shipment.status)} 
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => handleDownloadLabel(shipment)}
                          title="Descargar etiqueta"
                        >
                          <DownloadIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Step 3: Upload Tracking */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Paso 3: Subir Tracking (Mirakl)</Typography>
            <Button
              variant="contained"
              onClick={handleUploadTracking}
              disabled={loadingAction !== null || shipments.length === 0}
              startIcon={loadingAction === 'UPLOAD' ? <CircularProgress size={20} /> : undefined}
            >
              {loadingAction === 'UPLOAD' ? 'Subiendo...' : 'Subir Tracking'}
            </Button>
          </Box>

          {shippedOrders > 0 && (
            <Alert severity="success" sx={{ mb: 2 }}>
              ✅ {shippedOrders} pedidos marcados como SHIPPED en Mirakl
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Auxiliary Actions */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Acciones Auxiliares</Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="outlined"
              onClick={handleExportCsv}
              disabled={orders.length === 0}
              startIcon={<DownloadIcon />}
            >
              Exportar CSV (Mirakl/TIPSA)
            </Button>
            
            <Button
              variant="outlined"
              onClick={handleDownloadLogs}
              startIcon={<DownloadIcon />}
            >
              Descargar LOGS (frontend)
            </Button>
            
            <Button
              variant="outlined"
              onClick={handleLoadOrders}
              disabled={loadingAction !== null}
              startIcon={<RefreshIcon />}
            >
              Refrescar Pedidos
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
