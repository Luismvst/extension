import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Switch,
  Button,
  Divider,
  Alert,
} from '@mui/material'
import { Save as SaveIcon } from '@mui/icons-material'

const Configuration: React.FC = () => {
  const [config, setConfig] = useState({
    defaultCarrier: 'tipsa',
    autoPoll: true,
    logRetention: '30',
    webhookTimeout: '300',
    maxRetries: '3',
    notificationEmail: '',
    enableNotifications: false,
  })

  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    // Save configuration (in real app, this would call API)
    localStorage.setItem('dashboard_config', JSON.stringify(config))
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const handleChange = (field: string, value: any) => {
    setConfig({ ...config, [field]: value })
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Configuración
      </Typography>

      {saved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Configuración guardada correctamente
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Carrier Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Transportista por Defecto
              </Typography>
              <FormControl component="fieldset">
                <RadioGroup
                  value={config.defaultCarrier}
                  onChange={(e) => handleChange('defaultCarrier', e.target.value)}
                >
                  <FormControlLabel
                    value="tipsa"
                    control={<Radio />}
                    label="TIPSA"
                  />
                  <FormControlLabel
                    value="ontime"
                    control={<Radio />}
                    label="OnTime"
                  />
                  <FormControlLabel
                    value="seur"
                    control={<Radio />}
                    label="SEUR"
                  />
                  <FormControlLabel
                    value="correosex"
                    control={<Radio />}
                    label="Correos Express"
                  />
                </RadioGroup>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Polling Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Polling Automático
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.autoPoll}
                    onChange={(e) => handleChange('autoPoll', e.target.checked)}
                  />
                }
                label="Habilitar polling automático"
              />
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Actualiza automáticamente el estado de los pedidos cada 5 minutos
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Logging Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Retención de Logs
              </Typography>
              <TextField
                fullWidth
                label="Días de retención"
                type="number"
                value={config.logRetention}
                onChange={(e) => handleChange('logRetention', e.target.value)}
                helperText="Número de días para mantener los logs (mínimo 7, máximo 365)"
                inputProps={{ min: 7, max: 365 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Webhook Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuración de Webhooks
              </Typography>
              <TextField
                fullWidth
                label="Timeout (segundos)"
                type="number"
                value={config.webhookTimeout}
                onChange={(e) => handleChange('webhookTimeout', e.target.value)}
                helperText="Tiempo máximo de espera para webhooks"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Máximo reintentos"
                type="number"
                value={config.maxRetries}
                onChange={(e) => handleChange('maxRetries', e.target.value)}
                helperText="Número máximo de reintentos en caso de error"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Notifications */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notificaciones
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.enableNotifications}
                    onChange={(e) => handleChange('enableNotifications', e.target.checked)}
                  />
                }
                label="Habilitar notificaciones por email"
              />
              {config.enableNotifications && (
                <TextField
                  fullWidth
                  label="Email de notificaciones"
                  type="email"
                  value={config.notificationEmail}
                  onChange={(e) => handleChange('notificationEmail', e.target.value)}
                  helperText="Email para recibir notificaciones de errores y actualizaciones"
                  sx={{ mt: 2 }}
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Save Button */}
        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            size="large"
          >
            Guardar Configuración
          </Button>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Configuration
