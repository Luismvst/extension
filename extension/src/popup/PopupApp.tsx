/**
 * Main popup application component.
 * 
 * This component provides the main interface for the Chrome extension popup,
 * including authentication, order management, and shipment tracking.
 */

import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  LinearProgress,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Paper
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  Login as LoginIcon,
  Logout as LogoutIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material'
import { apiClient } from '@/lib/api'
import { StorageManager } from '@/lib/storage'
import { Order, ShipmentResult, AppState, LoginRequest } from '@/types'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const PopupApp: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    isAuthenticated: false,
    orders: [],
    shipments: [],
    isLoading: false
  })
  const [tabValue, setTabValue] = useState(0)
  const [loginForm, setLoginForm] = useState<LoginRequest>({
    username: 'admin',
    password: 'admin123'
  })
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Load initial state
  useEffect(() => {
    loadInitialState()
  }, [])

  const loadInitialState = async () => {
    try {
      const state = await StorageManager.getAppState()
      setAppState(prev => ({ ...prev, ...state }))
    } catch (err) {
      console.error('Failed to load initial state:', err)
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    try {
      const response = await apiClient.login(loginForm)
      await StorageManager.setUserData(response.user)
      
      setAppState(prev => ({
        ...prev,
        isAuthenticated: true,
        user: response.user
      }))
      
      setSuccess('Login successful!')
      setLoginForm({ username: '', password: '' })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  const handleLogout = async () => {
    try {
      apiClient.logout()
      await StorageManager.clearAll()
      
      setAppState({
        isAuthenticated: false,
        orders: [],
        shipments: [],
        isLoading: false
      })
      
      setSuccess('Logged out successfully!')
    } catch (err) {
      console.error('Logout error:', err)
    }
  }

  const handleLoadOrders = async () => {
    setAppState(prev => ({ ...prev, isLoading: true, error: undefined }))
    setError(null)

    try {
      const response = await apiClient.getMiraklOrders({
        status: 'SHIPPING',
        limit: 50
      })

      await StorageManager.setOrders(response.orders)
      setAppState(prev => ({ 
        ...prev, 
        orders: response.orders,
        isLoading: false 
      }))

      setSuccess(`Loaded ${response.orders.length} orders`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load orders')
      setAppState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const handleCreateShipments = async () => {
    if (appState.orders.length === 0) {
      setError('No orders available to create shipments')
      return
    }

    setAppState(prev => ({ ...prev, isLoading: true, error: undefined }))
    setError(null)

    try {
      const shipmentRequests = appState.orders.map(order => ({
        order_id: order.order_id,
        service_type: order.service_type || 'standard',
        weight: order.weight,
        cod_amount: order.cod_amount,
        reference: order.order_id,
        notes: order.notes
      }))

      const response = await apiClient.createShipments({
        shipments: shipmentRequests
      })

      await StorageManager.setShipments(response.shipments)
      setAppState(prev => ({ 
        ...prev, 
        shipments: response.shipments,
        isLoading: false 
      }))

      setSuccess(`Created ${response.total_created} shipments`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create shipments')
      setAppState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const handleUploadTracking = async () => {
    if (appState.shipments.length === 0) {
      setError('No shipments available to upload tracking')
      return
    }

    setAppState(prev => ({ ...prev, isLoading: true, error: undefined }))
    setError(null)

    try {
      let successCount = 0
      let errorCount = 0

      for (const shipment of appState.shipments) {
        try {
          await apiClient.uploadTrackingToMiraklSingle(shipment.order_id, {
            tracking_number: shipment.tracking_number,
            carrier_code: 'tipsa',
            carrier_name: 'TIPSA',
            carrier_url: shipment.label_url
          })
          successCount++
        } catch (err) {
          console.error(`Failed to upload tracking for order ${shipment.order_id}:`, err)
          errorCount++
        }
      }

      setAppState(prev => ({ ...prev, isLoading: false }))
      setSuccess(`Tracking upload completed: ${successCount} successful, ${errorCount} failed`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload tracking')
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
      setError('Failed to download label')
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  if (!appState.isAuthenticated) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Mirakl-TIPSA Orchestrator
        </Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <form onSubmit={handleLogin}>
          <TextField
            fullWidth
            label="Username"
            placeholder="admin (for testing)"
            value={loginForm.username}
            onChange={(e) => setLoginForm(prev => ({ ...prev, username: e.target.value }))}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            placeholder="admin123 (for testing)"
            value={loginForm.password}
            onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
            margin="normal"
            required
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 2 }}
            startIcon={<LoginIcon />}
          >
            Login
          </Button>
        </form>

        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Default credentials: admin / admin123
          </Typography>
        </Box>
      </Box>
    )
  }

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Dashboard" />
          <Tab label="Orders" />
          <Tab label="Shipments" />
          <Tab label="Settings" />
        </Tabs>
      </Box>

      {error && <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ m: 2 }}>{success}</Alert>}
      {appState.isLoading && <LinearProgress />}

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Button
                  variant="contained"
                  onClick={handleLoadOrders}
                  disabled={appState.isLoading}
                  startIcon={<DownloadIcon />}
                >
                  Load Orders ({appState.orders.length})
                </Button>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={handleCreateShipments}
                  disabled={appState.isLoading || appState.orders.length === 0}
                  startIcon={<UploadIcon />}
                >
                  Create Shipments ({appState.shipments.length})
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleUploadTracking}
                  disabled={appState.isLoading || appState.shipments.length === 0}
                  startIcon={<UploadIcon />}
                >
                  Upload Tracking
                </Button>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Status
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Authentication:</Typography>
                  <Chip
                    icon={<CheckCircleIcon />}
                    label="Connected"
                    color="success"
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Orders:</Typography>
                  <Chip
                    label={`${appState.orders.length} loaded`}
                    color="primary"
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Shipments:</Typography>
                  <Chip
                    label={`${appState.shipments.length} created`}
                    color="secondary"
                    size="small"
                  />
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Orders</Typography>
          <Button
            variant="outlined"
            onClick={handleLoadOrders}
            disabled={appState.isLoading}
            startIcon={<RefreshIcon />}
          >
            Refresh
          </Button>
        </Box>

        <List>
          {appState.orders.map((order) => (
            <ListItem key={order.order_id} divider>
              <ListItemText
                primary={order.order_id}
                secondary={`${order.customer_name} - ${order.weight}kg - ${order.total_amount}€`}
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
          {appState.orders.length === 0 && (
            <ListItem>
              <ListItemText
                primary="No orders loaded"
                secondary="Click 'Load Orders' to fetch orders from Mirakl"
              />
            </ListItem>
          )}
        </List>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Shipments</Typography>
          <Button
            variant="outlined"
            onClick={handleCreateShipments}
            disabled={appState.isLoading || appState.orders.length === 0}
            startIcon={<UploadIcon />}
          >
            Create All
          </Button>
        </Box>

        <List>
          {appState.shipments.map((shipment) => (
            <ListItem key={shipment.shipment_id} divider>
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
          {appState.shipments.length === 0 && (
            <ListItem>
              <ListItemText
                primary="No shipments created"
                secondary="Click 'Create Shipments' to create shipments with TIPSA"
              />
            </ListItem>
          )}
        </List>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Typography variant="h6" gutterBottom>
          Settings
        </Typography>
        
        <Box display="flex" flexDirection="column" gap={2}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Account
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Logged in as: {appState.user?.username}
            </Typography>
            <Button
              variant="outlined"
              onClick={handleLogout}
              startIcon={<LogoutIcon />}
            >
              Logout
            </Button>
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Data Management
            </Typography>
            <Button
              variant="outlined"
              onClick={() => {
                StorageManager.clearAll()
                setAppState({
                  isAuthenticated: false,
                  orders: [],
                  shipments: [],
                  isLoading: false
                })
                setSuccess('Data cleared successfully')
              }}
            >
              Clear All Data
            </Button>
          </Paper>
        </Box>
      </TabPanel>
    </Box>
  )
}

export default PopupApp
