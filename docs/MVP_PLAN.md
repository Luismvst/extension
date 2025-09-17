# Plan MVP - Mirakl CSV Extension

## 🎯 Objetivos del MVP

Construir un MVP funcional que demuestre la viabilidad del flujo CSV-first para interceptar exportaciones de Mirakl y generar archivos compatibles con transportistas.

## ✅ Criterios de Aceptación

### Funcionalidad Core
- [x] **Interceptación CSV**: Captura exitosa de exportaciones en portales Mirakl
- [x] **Parseo y Validación**: Conversión CSV → OrderStandard con validación Zod
- [x] **Mapper TIPSA**: Generación de CSV TIPSA con formato correcto
- [x] **UI Popup**: Interfaz para visualizar pedidos y generar CSV
- [x] **Storage Local**: Persistencia de pedidos en chrome.storage

### Calidad y Testing
- [x] **Tests Unitarios**: Cobertura > 80% en parsers y mappers
- [x] **Tests E2E**: Flujo completo con Playwright
- [x] **Validación de Datos**: Manejo de CSVs malformados y datos faltantes
- [x] **Error Handling**: Mensajes de error claros y recuperación graceful

### Infraestructura
- [x] **Docker**: Containerización de backend y build de extensión
- [x] **CI/CD**: GitHub Actions con tests automáticos
- [x] **Documentación**: README, arquitectura y guías de desarrollo
- [x] **Versionado**: SemVer con tags de release

## 📋 Checklist de Implementación

### ETAPA A: Inicialización ✅
- [x] Estructura de carpetas creada
- [x] Documentos base (README, ARCHITECTURE, MVP_PLAN)
- [x] .gitignore configurado
- [x] env.example creado
- [x] LICENSE MIT añadido

### ETAPA B: Extensión MV3 🔄
- [ ] Configuración Vite + React + TypeScript + Tailwind
- [ ] Manifest MV3 con permisos correctos
- [ ] Content script para interceptación CSV
- [ ] Background service worker para cola
- [ ] Popup UI con lista de pedidos
- [ ] Mapper TIPSA funcional
- [ ] Tests unitarios con Jest
- [ ] Configuración Tailwind y estilos

### ETAPA C: Backend FastAPI 🔄
- [ ] FastAPI app con endpoints básicos
- [ ] Modelos Pydantic (OrderStandard, OrderItem)
- [ ] Servicio de mapeo TIPSA
- [ ] Logging estructurado
- [ ] Tests unitarios con pytest
- [ ] Configuración con Pydantic Settings

### ETAPA D: Docker & Compose 🔄
- [ ] Dockerfile para backend Python
- [ ] Dockerfile para build de extensión
- [ ] docker-compose.yml con servicios
- [ ] Health checks configurados
- [ ] Volúmenes para artifacts

### ETAPA E: CI/CD 🔄
- [ ] GitHub Actions workflow
- [ ] Tests automáticos en PR
- [ ] Build y artifacts en push
- [ ] Notificaciones de estado

### ETAPA F: Testing E2E 🔄
- [ ] Portal fake con Playwright
- [ ] Fixtures de CSV realistas
- [ ] Tests de flujo completo
- [ ] Validación de generación CSV

### ETAPA G: Documentación 🔄
- [ ] README completo con instrucciones
- [ ] Guía de desarrollo
- [ ] Documentación de API
- [ ] CHANGELOG actualizado

### ETAPA H: Deploy 🔄
- [ ] Repositorio GitHub configurado
- [ ] Push inicial con CI activo
- [ ] Tags de release creados
- [ ] Verificación final

## 🧪 Plan de Testing

### Tests Unitarios

#### Extension
```typescript
// lib/csv.test.ts
describe('CSV Parser', () => {
  it('should parse Carrefour CSV correctly')
  it('should handle missing columns gracefully')
  it('should validate OrderStandard schema')
})

// mappers/tipsa.test.ts
describe('TIPSA Mapper', () => {
  it('should generate correct CSV headers')
  it('should map OrderStandard to TIPSA format')
  it('should handle invalid postal codes')
})
```

#### Backend
```python
# tests/unit/test_mapping.py
def test_tipsa_mapping():
    """Test TIPSA CSV generation"""
    orders = [create_test_order()]
    csv = map_orders_to_tipsa_csv(orders)
    assert "destinatario;direccion;cp" in csv

def test_invalid_data():
    """Test error handling for invalid data"""
    with pytest.raises(ValidationError):
        OrderStandard(**invalid_data)
```

### Tests E2E

#### Portal Fake
```typescript
// tests/playwright/e2e.spec.ts
test('complete CSV flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('[data-export-csv]');
  await expect(page.locator('#popup')).toBeVisible();
  await page.click('#generate-tipsa');
  await expect(page.locator('#download-csv')).toBeVisible();
});
```

### Fixtures de Datos

#### Carrefour Sample
```csv
Order ID,Order Date,Status,SKU,Product,Qty,Price,Buyer Name,Buyer Email,Phone,Ship To,Address 1,Address 2,City,Postal Code,Country,Total
ORD-001,2024-01-15,PENDING,SKU-123,Product A,2,25.50,John Doe,john@example.com,+34123456789,John Doe,123 Main St,Apt 4B,Madrid,28001,ES,51.00
```

#### Leroy Sample
```csv
Order ID,Order Date,Status,SKU,Product,Qty,Price,Buyer Name,Buyer Email,Phone,Ship To,Address 1,Address 2,City,Postal Code,Country,Total
ORD-002,2024-01-15,ACCEPTED,SKU-456,Product B,1,45.00,Jane Smith,jane@example.com,+34987654321,Jane Smith,456 Oak Ave,,Barcelona,08001,ES,45.00
```

## 🚀 Criterios de Calidad

### Código
- **TypeScript**: Tipado estricto, sin `any`
- **ESLint**: Configuración estricta, 0 warnings
- **Prettier**: Formato consistente
- **Husky**: Pre-commit hooks

### Testing
- **Cobertura**: > 80% en código crítico
- **E2E**: Flujo completo funcional
- **Performance**: < 2s para parse de 100 pedidos
- **Accessibility**: WCAG 2.1 AA básico

### Seguridad
- **PII**: Minimización y ofuscación
- **Storage**: Datos efímeros únicamente
- **Logs**: Sin información sensible
- **Dependencies**: Auditoría de vulnerabilidades

## 📊 Métricas de Éxito

### Funcionalidad
- **Tasa de Interceptación**: > 95% en portales de prueba
- **Tiempo de Procesamiento**: < 1s para 50 pedidos
- **Tasa de Error**: < 2% en datos válidos
- **Compatibilidad**: Funciona en Chrome 120+

### Usabilidad
- **Tiempo de Setup**: < 5 min para usuario nuevo
- **Curva de Aprendizaje**: < 10 min para uso básico
- **Satisfacción**: Feedback positivo en testing

### Técnico
- **Build Time**: < 2 min en CI
- **Bundle Size**: < 1MB para extensión
- **Memory Usage**: < 50MB en runtime
- **Uptime**: > 99% en servicios críticos

## 🔄 Proceso de Release

### Versionado
- **SemVer**: 0.1.0 para MVP
- **Conventional Commits**: feat:, fix:, chore:, docs:
- **Changelog**: Automático con cambios significativos

### Release Process
1. **Feature Complete**: Todas las funcionalidades implementadas
2. **Testing**: Tests unitarios y E2E pasando
3. **Documentation**: README y docs actualizados
4. **Build**: Artefactos generados correctamente
5. **Tag**: `git tag v0.1.0`
6. **Push**: `git push origin v0.1.0`
7. **Release**: GitHub release con notas

### Rollback Plan
- **Detección**: Monitoreo de errores en CI
- **Identificación**: Logs y métricas de fallo
- **Rollback**: Revert a commit estable
- **Comunicación**: Notificación a stakeholders

## 🎯 Post-MVP Roadmap

### Fase 2: API Integration
- Integración Mirakl Seller API
- Mapper OnTime completo
- Dashboard de monitoreo
- Alertas y notificaciones

### Fase 3: Production Scale
- Autenticación y autorización
- Rate limiting y throttling
- Backup y recovery
- Observabilidad avanzada

### Fase 4: Business Features
- Pricing y billing
- Onboarding UX
- Customer support
- Analytics y reporting
