import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
} from '@mui/material'
import {
  Check as CheckIcon,
  Star as StarIcon,
  CreditCard as CreditCardIcon,
  Security as SecurityIcon,
} from '@mui/icons-material'

const Payment: React.FC = () => {
  const currentPlan = 'FREE'
  const features = [
    'Hasta 100 pedidos por mes',
    'Soporte para TIPSA y OnTime',
    'Dashboard básico',
    'Logs de operaciones',
    'Webhooks básicos',
  ]

  const premiumFeatures = [
    'Pedidos ilimitados',
    'Todos los transportistas',
    'Dashboard avanzado',
    'Logs detallados',
    'Webhooks avanzados',
    'Soporte prioritario',
    'API personalizada',
  ]

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Método de Pago
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Actualmente estás en el plan <strong>GRATUITO</strong>. 
        Actualiza a Premium para desbloquear todas las funcionalidades.
      </Alert>

      <Grid container spacing={3}>
        {/* Current Plan */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="h5" component="h2" sx={{ mr: 2 }}>
                  Plan Actual
                </Typography>
                <Chip
                  label={currentPlan}
                  color="primary"
                  icon={<StarIcon />}
                />
              </Box>
              
              <Typography variant="h3" color="primary" gutterBottom>
                €0/mes
              </Typography>
              
              <Typography variant="body1" color="textSecondary" paragraph>
                Plan gratuito con funcionalidades básicas
              </Typography>

              <List>
                {features.map((feature, index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemIcon>
                      <CheckIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText primary={feature} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Premium Plan */}
        <Grid item xs={12} md={6}>
          <Card sx={{ border: '2px solid', borderColor: 'primary.main' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="h5" component="h2" sx={{ mr: 2 }}>
                  Plan Premium
                </Typography>
                <Chip
                  label="RECOMENDADO"
                  color="secondary"
                  icon={<StarIcon />}
                />
              </Box>
              
              <Typography variant="h3" color="primary" gutterBottom>
                €29/mes
              </Typography>
              
              <Typography variant="body1" color="textSecondary" paragraph>
                Acceso completo a todas las funcionalidades
              </Typography>

              <List>
                {premiumFeatures.map((feature, index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemIcon>
                      <CheckIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText primary={feature} />
                  </ListItem>
                ))}
              </List>

              <Divider sx={{ my: 2 }} />

              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={<CreditCardIcon />}
                disabled
              >
                Actualizar a Premium
              </Button>

              <Typography variant="caption" color="textSecondary" display="block" textAlign="center" sx={{ mt: 1 }}>
                Próximamente disponible
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Payment Methods */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Métodos de Pago
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                    <CreditCardIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                    <Typography variant="body2" gutterBottom>
                      Tarjeta de Crédito
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Visa, Mastercard, American Express
                    </Typography>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                    <SecurityIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                    <Typography variant="body2" gutterBottom>
                      Transferencia Bancaria
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      SEPA, Transferencia internacional
                    </Typography>
                  </Card>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Billing Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Información de Facturación
              </Typography>
              
              <Typography variant="body2" color="textSecondary" paragraph>
                <strong>Plan actual:</strong> Gratuito
              </Typography>
              
              <Typography variant="body2" color="textSecondary" paragraph>
                <strong>Próxima facturación:</strong> No aplicable
              </Typography>
              
              <Typography variant="body2" color="textSecondary" paragraph>
                <strong>Límite de pedidos:</strong> 100 pedidos/mes
              </Typography>
              
              <Typography variant="body2" color="textSecondary">
                <strong>Pedidos utilizados este mes:</strong> 0/100
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Payment
