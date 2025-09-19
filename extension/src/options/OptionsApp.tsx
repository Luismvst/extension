/**
 * Options page application component.
 */

import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  Grid
} from '@mui/material'
import { StorageManager } from '@/lib/storage'

interface Settings {
  apiBaseUrl: string
  autoLoadOrders: boolean
  autoCreateShipments: boolean
  showNotifications: boolean
}

const OptionsApp: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({
    apiBaseUrl: 'http://localhost:8080',
    autoLoadOrders: false,
    autoCreateShipments: false,
    showNotifications: true
  })
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const storedSettings = await StorageManager.getSettings()
      setSettings(prev => ({ ...prev, ...storedSettings }))
    } catch (err) {
      console.error('Failed to load settings:', err)
    }
  }

  const handleSave = async () => {
    try {
      await StorageManager.setSettings(settings)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      setError('Failed to save settings')
    }
  }

  return (
    <Box sx={{ maxWidth: 800, margin: '0 auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Mirakl-TIPSA Orchestrator Settings
      </Typography>

      {saved && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Settings saved successfully!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Configuration
              </Typography>
              
              <TextField
                fullWidth
                label="API Base URL"
                value={settings.apiBaseUrl}
                onChange={(e) => setSettings(prev => ({ ...prev, apiBaseUrl: e.target.value }))}
                margin="normal"
                helperText="Base URL for the orchestrator backend API"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Behavior Settings
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoLoadOrders}
                    onChange={(e) => setSettings(prev => ({ ...prev, autoLoadOrders: e.target.checked }))}
                  />
                }
                label="Auto-load orders when opening TIPSA website"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoCreateShipments}
                    onChange={(e) => setSettings(prev => ({ ...prev, autoCreateShipments: e.target.checked }))}
                  />
                }
                label="Auto-create shipments after loading orders"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.showNotifications}
                    onChange={(e) => setSettings(prev => ({ ...prev, showNotifications: e.target.checked }))}
                  />
                }
                label="Show desktop notifications"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box display="flex" justifyContent="flex-end" mt={4}>
        <Button
          variant="contained"
          onClick={handleSave}
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  )
}

export default OptionsApp