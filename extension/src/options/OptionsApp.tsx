import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Divider,
  Grid,
  Paper
} from '@mui/material';
import { Save as SaveIcon, Restore as RestoreIcon } from '@mui/icons-material';
import { CsvExporter } from '@/lib/exportCsv';

export default function OptionsApp() {
  const [config, setConfig] = useState({
    producto: '48',
    tipoBultos: 'PTR180P',
    departamentoCliente: 'empresarial',
    codigoCliente: '89'
  });
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const savedConfig = await CsvExporter.loadConfig();
      setConfig(savedConfig);
    } catch (err) {
      console.error('Failed to load config:', err);
      setError('Error al cargar configuración');
    }
  };

  const handleSave = async () => {
    try {
      await CsvExporter.saveConfig(config);
      setNotice('✅ Configuración guardada correctamente');
      setError(null);
    } catch (err) {
      setError('Error al guardar configuración');
    }
  };

  const handleReset = () => {
    setConfig({
      producto: '48',
      tipoBultos: 'PTR180P',
      departamentoCliente: 'empresarial',
      codigoCliente: '89'
    });
    setNotice('Configuración restablecida a valores por defecto');
  };

  const handleChange = (field: keyof typeof config) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setConfig(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  return (
    <Box sx={{ maxWidth: 800, margin: '0 auto', p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Configuración CSV - Mirakl ↔ TIPSA
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Configura los valores por defecto para la exportación de CSV a TIPSA.
      </Typography>

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

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Valores por Defecto CSV
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Producto"
                value={config.producto}
                onChange={handleChange('producto')}
                helperText="Código de producto por defecto"
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tipo Bultos"
                value={config.tipoBultos}
                onChange={handleChange('tipoBultos')}
                helperText="Tipo de bulto por defecto"
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Departamento Cliente"
                value={config.departamentoCliente}
                onChange={handleChange('departamentoCliente')}
                helperText="Departamento del cliente"
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Código Cliente"
                value={config.codigoCliente}
                onChange={handleChange('codigoCliente')}
                helperText="Código del cliente"
                variant="outlined"
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button
              variant="outlined"
              onClick={handleReset}
              startIcon={<RestoreIcon />}
            >
              Restablecer
            </Button>
            
            <Button
              variant="contained"
              onClick={handleSave}
              startIcon={<SaveIcon />}
            >
              Guardar Configuración
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Información sobre los Campos
          </Typography>
          
          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
            <Typography variant="body2" component="div">
              <strong>Producto:</strong> Código de producto que se asignará a todos los envíos.<br/>
              <strong>Tipo Bultos:</strong> Tipo de embalaje estándar para los envíos.<br/>
              <strong>Departamento Cliente:</strong> Departamento interno del cliente.<br/>
              <strong>Código Cliente:</strong> Código identificador del cliente en TIPSA.
            </Typography>
          </Paper>
        </CardContent>
      </Card>
    </Box>
  );
}