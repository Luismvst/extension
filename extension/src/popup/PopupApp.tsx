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
  Paper,
  Container,
  AppBar,
  Toolbar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Badge,
  Avatar
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
  Warning as WarningIcon,
  Store as StoreIcon,
  LocalShipping as ShippingIcon,
  Assignment as AssignmentIcon,
  Person as PersonIcon,
  Business as BusinessIcon
} from '@mui/icons-material'
import { apiClient } from '@/lib/api'
import { StorageManager } from '@/lib/storage'
import { Order, ShipmentResult, AppState, LoginRequest } from '@/types'
import { theme } from '@/theme'

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
  const [selectedMarketplace, setSelectedMarketplace] = useState('Mirakl')
  const [selectedCarrier, setSelectedCarrier] = useState('TIPSA')

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

  const handleRefreshMarketplace = async () => {
    setAppState(prev => ({ ...prev, isLoading: true }))
    try {
      const result = await apiClient.refreshMarketplace(selectedMarketplace.toLowerCase())
      setAppState(prev => ({ ...prev, isLoading: false }))
      setSuccess(`Refreshed ${result.orders_updated} orders from ${selectedMarketplace}`)
      // Reload orders after refresh
      await handleLoadOrders()
    } catch (error) {
      setAppState(prev => ({ ...prev, isLoading: false }))
      setError(`Failed to refresh marketplace: ${error}`)
    }
  }

  const handleDownloadCSV = async () => {
    try {
      const csvData = await apiClient.exportOrdersCSV()
      const blob = new Blob([csvData], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `orders_export_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      setSuccess('CSV exported successfully')
    } catch (error) {
      setError(`Failed to export CSV: ${error}`)
    }
  }

  const handleSendToCarrier = async () => {
    if (appState.orders.length === 0) {
      setError('No orders available to send')
      return
    }

    setAppState(prev => ({ ...prev, isLoading: true }))
    try {
      const orderIds = appState.orders.map(order => order.order_id)
      const result = await apiClient.postToCarrier(selectedCarrier.toLowerCase(), orderIds)
      setAppState(prev => ({ ...prev, isLoading: false }))
      setSuccess(`Sent ${result.orders_processed} orders to ${selectedCarrier}`)
      // Reload orders to see updated status
      await handleLoadOrders()
    } catch (error) {
      setAppState(prev => ({ ...prev, isLoading: false }))
      setError(`Failed to send orders to carrier: ${error}`)
    }
  }

  if (!appState.isAuthenticated) {
    return (
      <Box sx={{ 
        minHeight: '400px',
        background: 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)',
        p: 3
      }}>
        <Card sx={{ maxWidth: 400, mx: 'auto', mt: 2 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Avatar sx={{ 
                bgcolor: 'primary.main', 
                width: 64, 
                height: 64, 
                mx: 'auto', 
                mb: 2 
              }}>
                <BusinessIcon sx={{ fontSize: 32 }} />
              </Avatar>
              <Typography variant="h5" component="h1" gutterBottom>
                Mirakl-TIPSA
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Orchestrator Extension
              </Typography>
            </Box>
            
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
                InputProps={{
                  startAdornment: <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
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
                size="large"
                sx={{ mt: 3, py: 1.5 }}
                startIcon={<LoginIcon />}
              >
                Login
              </Button>
            </form>

            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Default credentials: admin / admin123
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    )
  }

  return (
    <Box sx={{ width: '100%', minHeight: '500px' }}>
      {/* Header with AppBar */}
      <AppBar position="static" elevation={0} sx={{ bgcolor: 'primary.main' }}>
        <Toolbar sx={{ minHeight: 64 }}>
          <Avatar sx={{ mr: 2, bgcolor: 'white', color: 'primary.main' }}>
            <BusinessIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" component="div" sx={{ color: 'white' }}>
              Mirakl-TIPSA Orchestrator
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              Extension v0.2.0
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }} />
          <Chip
            icon={<CheckCircleIcon />}
            label="Connected"
            color="success"
            size="small"
            sx={{ bgcolor: 'white', color: 'success.main' }}
          />
        </Toolbar>
      </AppBar>

      {/* Navigation Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ 
            '& .MuiTab-root': {
              minHeight: 48,
              fontWeight: 500
            }
          }}
        >
          <Tab 
            label="Dashboard" 
            icon={<AssignmentIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Orders" 
            icon={<StoreIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Shipments" 
            icon={<ShippingIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Settings" 
            icon={<SettingsIcon />} 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Alerts */}
      {error && <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ m: 2 }}>{success}</Alert>}
      {appState.isLoading && <LinearProgress />}

      <TabPanel value={tabValue} index={0}>
        <Container maxWidth="lg" sx={{ py: 3 }}>
          {/* Quick Actions Section */}
          <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 100%)' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AssignmentIcon color="primary" />
                Quick Actions
              </Typography>
              
              {/* Marketplace and Carrier Selection */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Marketplace</InputLabel>
                    <Select
                      value={selectedMarketplace}
                      label="Marketplace"
                      onChange={(e) => setSelectedMarketplace(e.target.value)}
                      startAdornment={<StoreIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                    >
                      <MenuItem value="Mirakl">Mirakl (Active)</MenuItem>
                      <MenuItem value="Amazon" disabled>Amazon (Coming Soon)</MenuItem>
                      <MenuItem value="eBay" disabled>eBay (Coming Soon)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Carrier</InputLabel>
                    <Select
                      value={selectedCarrier}
                      label="Carrier"
                      onChange={(e) => setSelectedCarrier(e.target.value)}
                      startAdornment={<ShippingIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                    >
                      <MenuItem value="TIPSA">TIPSA</MenuItem>
                      <MenuItem value="DHL">DHL</MenuItem>
                      <MenuItem value="UPS">UPS</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              {/* Action Buttons */}
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<DownloadIcon />}
                  onClick={handleLoadOrders}
                  disabled={appState.isLoading}
                  sx={{ minWidth: 140 }}
                >
                  Get Orders ({appState.orders.length})
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<UploadIcon />}
                  onClick={handleSendToCarrier}
                  disabled={appState.isLoading || appState.orders.length === 0}
                  sx={{ minWidth: 140 }}
                >
                  Enviar a {selectedCarrier}
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownloadCSV}
                  disabled={appState.isLoading || appState.orders.length === 0}
                  sx={{ minWidth: 140 }}
                >
                  Download CSV
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<RefreshIcon />}
                  onClick={handleRefreshMarketplace}
                  disabled={appState.isLoading}
                  sx={{ minWidth: 140 }}
                >
                  Actualizar Marketplace
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Statistics Cards */}
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center', p: 2 }}>
                <Badge badgeContent={appState.orders.length} color="primary" max={999}>
                  <AssignmentIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                </Badge>
                <Typography variant="h4" component="div" color="primary">
                  {appState.orders.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Orders
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center', p: 2 }}>
                <Badge badgeContent={appState.orders.filter(o => o.status === 'PENDING').length} color="warning" max={999}>
                  <WarningIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                </Badge>
                <Typography variant="h4" component="div" color="warning.main">
                  {appState.orders.filter(o => o.status === 'PENDING').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center', p: 2 }}>
                <Badge badgeContent={appState.orders.filter(o => o.status === 'PROCESSED').length} color="success" max={999}>
                  <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                </Badge>
                <Typography variant="h4" component="div" color="success.main">
                  {appState.orders.filter(o => o.status === 'PROCESSED').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Processed
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center', p: 2 }}>
                <Badge badgeContent={appState.shipments.length} color="info" max={999}>
                  <ShippingIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                </Badge>
                <Typography variant="h4" component="div" color="info.main">
                  {appState.shipments.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Shipments
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Container maxWidth="lg" sx={{ py: 3 }}>
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
        </Container>
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
        <Container maxWidth="md" sx={{ py: 3 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon color="primary" />
            Settings & Configuration
          </Typography>
          
          <Grid container spacing={3}>
            {/* Account Section */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PersonIcon color="primary" />
                    Account Information
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Username
                    </Typography>
                    <Typography variant="body1">
                      {appState.user?.username || 'Unknown'}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Status
                    </Typography>
                    <Chip
                      icon={<CheckCircleIcon />}
                      label="Connected"
                      color="success"
                      size="small"
                    />
                  </Box>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={handleLogout}
                    startIcon={<LogoutIcon />}
                    sx={{ mt: 1 }}
                  >
                    Logout
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            {/* API Configuration */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <BusinessIcon color="primary" />
                    API Configuration
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Backend URL
                    </Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                      http://localhost:8080
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Selected Marketplace
                    </Typography>
                    <Chip
                      label={selectedMarketplace}
                      color="primary"
                      size="small"
                    />
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Selected Carrier
                    </Typography>
                    <Chip
                      label={selectedCarrier}
                      color="secondary"
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Statistics */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AssignmentIcon color="primary" />
                    Order Statistics
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Total Orders:</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {appState.orders.length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Pending:</Typography>
                      <Typography variant="body2" color="warning.main">
                        {appState.orders.filter(o => o.status === 'PENDING').length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Processed:</Typography>
                      <Typography variant="body2" color="success.main">
                        {appState.orders.filter(o => o.status === 'PROCESSED').length}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Build Information */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <InfoIcon color="primary" />
                    Build Information
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Version:</Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {BUILD_INFO.version}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Build:</Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {BUILD_INFO.build}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Date:</Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {BUILD_INFO.date}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Actions */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Actions
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Button
                      variant="outlined"
                      startIcon={<RefreshIcon />}
                      onClick={handleRefreshMarketplace}
                      disabled={appState.isLoading}
                    >
                      Refresh Marketplace
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={handleDownloadCSV}
                      disabled={appState.orders.length === 0}
                    >
                      Export CSV
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
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
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </TabPanel>
    </Box>
  )
}

export default PopupApp
