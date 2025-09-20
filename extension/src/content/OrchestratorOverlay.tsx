/**
 * Orchestrator overlay component for TIPSA website.
 * 
 * This component provides the main interface for users to:
 * 1. Load orders from Mirakl
 * 2. Create shipments with TIPSA
 * 3. Upload tracking information back to Mirakl
 */

import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material'
import { apiClient } from '@/lib/api'
import { StorageManager } from '@/lib/storage'
import { Order, ShipmentResult, AppState } from '@/types'
import Logger from '@/lib/logger'

const OrchestratorOverlay: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    isAuthenticated: false,
    orders: [],
    shipments: [],
    isLoading: false
  })
  const [showOrders, setShowOrders] = useState(false)
  const [showShipments, setShowShipments] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load initial state
  useEffect(() => {
    loadInitialState()
  }, [])

  const loadInitialState = async () => {
    try {
      const state = await StorageManager.getAppState()
      setAppState(prev => ({ ...prev, ...state }))
      
      // Auto-authenticate with extension token if not already authenticated
      const isAuth = await apiClient.isAuthenticated()
      if (!isAuth) {
        try {
          await apiClient.getExtensionToken()
          setAppState(prev => ({ ...prev, isAuthenticated: true }))
          console.log('Auto-authenticated with extension token')
        } catch (err) {
          console.error('Failed to auto-authenticate:', err)
          setAppState(prev => ({ ...prev, isAuthenticated: false }))
        }
      } else {
        setAppState(prev => ({ ...prev, isAuthenticated: true }))
      }
    } catch (err) {
      console.error('Failed to load initial state:', err)
    }
  }

  const handleLoadOrders = async () => {
    Logger.section('🔄 LOADING MIRAKL ORDERS')
    Logger.step(1, 3, 'Starting order loading process')
    
    setAppState(prev => ({ ...prev, isLoading: true, error: undefined }))
    setError(null)

    try {
      // Check authentication
      Logger.info('Checking authentication status')
      const isAuth = await apiClient.isAuthenticated()
      if (!isAuth) {
        Logger.warning('User not authenticated, requesting login')
        setError('Please log in first using the extension popup')
        return
      }
      Logger.success('User is authenticated')

      // Fetch orders from Mirakl - only PENDING and PENDING_APPROVAL orders
      Logger.step(2, 3, 'Fetching orders from Mirakl API')
      const response = await apiClient.getMiraklOrders({
        status: 'PENDING',
        limit: 50
      })

      // Store orders
      Logger.step(3, 3, 'Storing orders in local storage')
      await StorageManager.setOrders(response.orders)
      setAppState(prev => ({ 
        ...prev, 
        orders: response.orders,
        isLoading: false 
      }))

      Logger.success(`Successfully loaded ${response.orders.length} orders`)
      setShowOrders(true)
    } catch (err: any) {
      Logger.error('Failed to load orders', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      })
      setError(err.message || 'Failed to load orders')
      setAppState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const handleCreateShipments = async () => {
    Logger.section('🚚 CREATING TIPSA SHIPMENTS')
    Logger.step(1, 4, 'Starting shipment creation process')
    
    if (appState.orders.length === 0) {
      Logger.warning('No orders available to create shipments')
      setError('No orders available to create shipments')
      return
    }

    setAppState(prev => ({ ...prev, isLoading: true, error: undefined }))
    setError(null)

    try {
      Logger.info(`Converting ${appState.orders.length} orders to shipment requests`)
      
      // Convert orders to shipment requests
      const shipmentRequests = appState.orders.map(order => ({
        order_id: order.order_id,
        service_type: order.service_type || 'standard',
        weight: order.weight,
        cod_amount: order.cod_amount,
        reference: order.order_id,
        notes: order.notes
      }))

      Logger.step(2, 4, 'Prepared shipment requests', shipmentRequests)

      // Create shipments
      Logger.step(3, 4, 'Sending shipment requests to TIPSA API')
      const response = await apiClient.createShipments({
        shipments: shipmentRequests
      })

      Logger.step(4, 4, 'Storing shipments in local storage')
      // Store shipments
      await StorageManager.setShipments(response.shipments)
      setAppState(prev => ({ 
        ...prev, 
        shipments: response.shipments,
        isLoading: false 
      }))

      Logger.success(`Successfully created ${response.shipments.length} shipments`)
      setShowShipments(true)
    } catch (err: any) {
      Logger.error('Failed to create shipments', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        orders: appState.orders
      })
      setError(err.message || 'Failed to create shipments')
      setAppState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const handleUploadTracking = async () => {
    Logger.section('📤 UPLOADING TRACKING TO MIRAKL')
    Logger.step(1, 3, 'Starting tracking upload process')
    
    if (appState.shipments.length === 0) {
      Logger.warning('No shipments available to upload tracking')
      setError('No shipments available to upload tracking')
      return
    }

    setAppState(prev => ({ ...prev, isLoading: true, error: undefined }))
    setError(null)

    try {
      let successCount = 0
      let errorCount = 0

      Logger.info(`Uploading tracking for ${appState.shipments.length} shipments`)

      // Upload tracking for each shipment
      for (const shipment of appState.shipments) {
        try {
          Logger.step(2, 3, `Uploading tracking for order ${shipment.order_id}`)
          await apiClient.uploadTrackingToMirakl(shipment.order_id, {
            tracking_number: shipment.tracking_number,
            carrier_code: 'tipsa',
            carrier_name: 'TIPSA',
            carrier_url: shipment.label_url
          })
          successCount++
          Logger.success(`Successfully uploaded tracking for order ${shipment.order_id}`)
        } catch (err: any) {
          Logger.error(`Failed to upload tracking for order ${shipment.order_id}`, {
            message: err.message,
            response: err.response?.data,
            status: err.response?.status,
            shipment
          })
          errorCount++
        }
      }

      Logger.step(3, 3, 'Tracking upload process completed')
      setAppState(prev => ({ ...prev, isLoading: false }))
      setError(`Tracking upload completed: ${successCount} successful, ${errorCount} failed`)
      
      if (successCount > 0) {
        Logger.success(`Successfully uploaded tracking for ${successCount} shipments`)
      }
      if (errorCount > 0) {
        Logger.warning(`Failed to upload tracking for ${errorCount} shipments`)
      }
    } catch (err: any) {
      Logger.error('Failed to upload tracking', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        shipments: appState.shipments
      })
      setError(err.message || 'Failed to upload tracking')
      setAppState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const handleDownloadLabel = async (shipment: ShipmentResult) => {
    try {
      const labelBlob = await apiClient.getShipmentLabel(shipment.shipment_id)
      const url = URL.createObjectURL(labelBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = `label_${shipment.tracking_number}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Failed to download label:', err)
      setError('Failed to download label')
    }
  }

  const handleCloseOverlay = () => {
    const overlay = document.getElementById('mirakl-tipsa-orchestrator')
    if (overlay) {
      overlay.remove()
    }
  }

  return (
    <Card sx={{ maxWidth: 400, maxHeight: '80vh', overflow: 'auto' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h2">
            Mirakl → TIPSA Orchestrator
          </Typography>
          <IconButton size="small" onClick={handleCloseOverlay}>
            <CloseIcon />
          </IconButton>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {appState.isLoading && <LinearProgress sx={{ mb: 2 }} />}

        <Box display="flex" flexDirection="column" gap={2}>
          {/* Step 1: Load Orders */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Step 1: Load Orders from Mirakl
            </Typography>
            <Button
              variant="contained"
              fullWidth
              onClick={handleLoadOrders}
              disabled={appState.isLoading}
              startIcon={<DownloadIcon />}
            >
              Load Orders ({appState.orders.length})
            </Button>
          </Box>

          {/* Step 2: Create Shipments */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Step 2: Create TIPSA Shipments
            </Typography>
            <Button
              variant="contained"
              fullWidth
              onClick={handleCreateShipments}
              disabled={appState.isLoading || appState.orders.length === 0}
              startIcon={<UploadIcon />}
              color="secondary"
            >
              Create Shipments ({appState.shipments.length})
            </Button>
          </Box>

          {/* Step 3: Upload Tracking */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Step 3: Upload Tracking to Mirakl
            </Typography>
            <Button
              variant="outlined"
              fullWidth
              onClick={handleUploadTracking}
              disabled={appState.isLoading || appState.shipments.length === 0}
              startIcon={<UploadIcon />}
            >
              Upload Tracking
            </Button>
          </Box>

          <Divider />

          {/* Orders Summary */}
          {appState.orders.length > 0 && (
            <Accordion expanded={showOrders} onChange={() => setShowOrders(!showOrders)}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle2">
                  Orders ({appState.orders.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List dense>
                  {appState.orders.slice(0, 5).map((order) => (
                    <ListItem key={order.order_id}>
                      <ListItemText
                        primary={order.order_id}
                        secondary={`${order.customer_name} - ${order.weight}kg`}
                      />
                      <ListItemSecondaryAction>
                        <Chip
                          label={order.status}
                          size="small"
                          color={order.status === 'SHIPPING' ? 'primary' : 'default'}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                  {appState.orders.length > 5 && (
                    <ListItem>
                      <ListItemText
                        primary={`... and ${appState.orders.length - 5} more`}
                      />
                    </ListItem>
                  )}
                </List>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Shipments Summary */}
          {appState.shipments.length > 0 && (
            <Accordion expanded={showShipments} onChange={() => setShowShipments(!showShipments)}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle2">
                  Shipments ({appState.shipments.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List dense>
                  {appState.shipments.slice(0, 5).map((shipment) => (
                    <ListItem key={shipment.shipment_id}>
                      <ListItemText
                        primary={shipment.tracking_number}
                        secondary={`${shipment.order_id} - ${shipment.status}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          size="small"
                          onClick={() => handleDownloadLabel(shipment)}
                        >
                          <DownloadIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                  {appState.shipments.length > 5 && (
                    <ListItem>
                      <ListItemText
                        primary={`... and ${appState.shipments.length - 5} more`}
                      />
                    </ListItem>
                  )}
                </List>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Status Info */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Chip
              icon={appState.isAuthenticated ? <CheckCircleIcon /> : <ErrorIcon />}
              label={appState.isAuthenticated ? 'Connected' : 'Not Connected'}
              color={appState.isAuthenticated ? 'success' : 'error'}
              size="small"
            />
            <Button
              size="small"
              onClick={loadInitialState}
              startIcon={<RefreshIcon />}
            >
              Refresh
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

export default OrchestratorOverlay
