import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material'
import { useAuth } from '../hooks/useAuth'

interface Order {
  mirakl_order_id: string
  mirakl_status: string
  mirakl_customer_name: string
  mirakl_customer_email: string
  mirakl_weight: number
  mirakl_total_amount: number
  mirakl_currency: string
  carrier_code: string
  carrier_name: string
  expedition_id: string
  tracking_number: string
  carrier_status: string
  internal_state: string
  last_event: string
  last_event_at: string
  updated_at: string
}

const Dashboard: React.FC = () => {
  const { token } = useAuth()
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    state: '',
    carrier: '',
  })
  const [stats, setStats] = useState({
    totalOrders: 0,
    byState: {} as Record<string, number>,
    byCarrier: {} as Record<string, number>,
  })

  const fetchOrders = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filters.state) params.append('state', filters.state)
      if (filters.carrier) params.append('carrier', filters.carrier)
      
      const response = await fetch(`/api/v1/logs/orders-view?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setOrders(data.orders || [])
      }
    } catch (error) {
      console.error('Error fetching orders:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v1/logs/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setStats(data.stats.orders)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const exportCSV = async () => {
    try {
      const response = await fetch('/api/v1/logs/exports/orders-view.csv', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `orders_view_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error exporting CSV:', error)
    }
  }

  useEffect(() => {
    fetchOrders()
    fetchStats()
  }, [filters])

  const getStateColor = (state: string) => {
    const colors: Record<string, string> = {
      'PENDING_POST': 'warning',
      'POSTED': 'info',
      'AWAITING_TRACKING': 'primary',
      'TRACKED': 'success',
      'MIRAKL_OK': 'success',
      'FAILED_*': 'error',
    }
    return colors[state] || 'default'
  }

  const getCarrierColor = (carrier: string) => {
    const colors: Record<string, string> = {
      'tipsa': 'primary',
      'ontime': 'secondary',
      'seur': 'success',
      'correosex': 'warning',
    }
    return colors[carrier] || 'default'
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={exportCSV}
            sx={{ mr: 1 }}
          >
            Exportar CSV
          </Button>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={fetchOrders}
            disabled={loading}
          >
            Actualizar
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Pedidos
              </Typography>
              <Typography variant="h4">
                {stats.totalOrders}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Por Estado
              </Typography>
              <Box>
                {Object.entries(stats.byState).map(([state, count]) => (
                  <Chip
                    key={state}
                    label={`${state}: ${count}`}
                    color={getStateColor(state) as any}
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Por Transportista
              </Typography>
              <Box>
                {Object.entries(stats.byCarrier).map(([carrier, count]) => (
                  <Chip
                    key={carrier}
                    label={`${carrier}: ${count}`}
                    color={getCarrierColor(carrier) as any}
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Última Actualización
              </Typography>
              <Typography variant="h6">
                {new Date().toLocaleTimeString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Filtros
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Estado</InputLabel>
                <Select
                  value={filters.state}
                  onChange={(e) => setFilters({ ...filters, state: e.target.value })}
                  label="Estado"
                >
                  <MenuItem value="">Todos</MenuItem>
                  <MenuItem value="PENDING_POST">Pendiente de Envío</MenuItem>
                  <MenuItem value="POSTED">Enviado</MenuItem>
                  <MenuItem value="AWAITING_TRACKING">Esperando Tracking</MenuItem>
                  <MenuItem value="TRACKED">Con Tracking</MenuItem>
                  <MenuItem value="MIRAKL_OK">Completado</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Transportista</InputLabel>
                <Select
                  value={filters.carrier}
                  onChange={(e) => setFilters({ ...filters, carrier: e.target.value })}
                  label="Transportista"
                >
                  <MenuItem value="">Todos</MenuItem>
                  <MenuItem value="tipsa">TIPSA</MenuItem>
                  <MenuItem value="ontime">OnTime</MenuItem>
                  <MenuItem value="seur">SEUR</MenuItem>
                  <MenuItem value="correosex">Correos Express</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Orders Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Pedidos
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID Pedido</TableCell>
                  <TableCell>Cliente</TableCell>
                  <TableCell>Peso</TableCell>
                  <TableCell>Importe</TableCell>
                  <TableCell>Transportista</TableCell>
                  <TableCell>Tracking</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Último Evento</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.mirakl_order_id}>
                    <TableCell>{order.mirakl_order_id}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {order.mirakl_customer_name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {order.mirakl_customer_email}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{order.mirakl_weight} kg</TableCell>
                    <TableCell>
                      {order.mirakl_total_amount} {order.mirakl_currency}
                    </TableCell>
                    <TableCell>
                      {order.carrier_name && (
                        <Chip
                          label={order.carrier_name}
                          color={getCarrierColor(order.carrier_code) as any}
                          size="small"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      {order.tracking_number && (
                        <Typography variant="body2" fontFamily="monospace">
                          {order.tracking_number}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={order.internal_state}
                        color={getStateColor(order.internal_state) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {order.last_event}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {new Date(order.last_event_at).toLocaleString()}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Ver detalles">
                        <IconButton size="small">
                          <FilterIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  )
}

export default Dashboard
