"""
Test standalone de GLS ShipIT API con OAuth2.

Este script prueba directamente la API de GLS sin depender de Mirakl.
Usa el sandbox de GLS y OAuth2 authentication.
"""

import asyncio
import sys
import os
from pathlib import Path
import json

# Añadir el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar solo lo necesario
from app.adapters.carriers.gls import GlsAdapter


async def test_oauth_token():
    """Test 1: Obtener token OAuth2"""
    print("=" * 80)
    print("TEST 1: OAuth2 Token")
    print("=" * 80)
    
    gls = GlsAdapter()
    
    # Usar la configuración del settings (mock_mode)
    # Si tienes credenciales válidas de ShipIT, cambia gls_mock_mode a False en settings.py
    
    # Saltear si está en mock mode
    if gls.mock_mode:
        print("[MOCK] OAuth2 no se prueba en modo mock")
        return None
    
    try:
        token = await gls._get_oauth_token()
        print(f"[OK] Token OAuth2 obtenido exitosamente")
        print(f"  Token (primeros 50 chars): {token[:50]}...")
        print(f"  Expira en: {gls._token_expires_at}")
        return True
    except Exception as e:
        print(f"[ERROR] Error obteniendo token OAuth2: {e}")
        return False


async def test_validate_shipment():
    """Test 2: Validar envío"""
    print("\n" + "=" * 80)
    print("TEST 2: Validar Envío")
    print("=" * 80)
    
    gls = GlsAdapter()
    gls.mock_mode = False
    
    # Datos mínimos para validar un envío a España
    test_order = {
        "order_id": "TEST-001",
        "customer_name": "Juan Pérez",
        "customer_email": "test@example.com",
        "weight": 2.5,
        "shipping_address": {
            "name": "Juan Pérez",
            "address1": "Calle Test 123",
            "city": "Madrid",
            "postal_code": "28001",
            "country": "ES",
            "phone": "+34612345678"
        }
    }
    
    try:
        result = await gls.validate_shipment(test_order)
        
        success = result.get("Success", False)
        issues = result.get("ValidationResult", {}).get("Issues", [])
        
        if success:
            print(f"[OK] Envio valido")
            print(f"  Sin errores de validación")
        else:
            print(f"[WARN] Envio con problemas:")
            for issue in issues:
                print(f"    - {issue.get('Rule')}: {issue.get('Location')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error validando envio: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_get_allowed_services():
    """Test 3: Obtener servicios permitidos"""
    print("\n" + "=" * 80)
    print("TEST 3: Servicios Permitidos")
    print("=" * 80)
    
    gls = GlsAdapter()
    
    # Saltear si está en mock mode
    if gls.mock_mode:
        print("[MOCK] Allowed services se prueba en mock mode")
        result = await gls.get_allowed_services("ES", "28001", "ES", "08001")
        services = result.get("AllowedServices", [])
        print(f"[OK] Mock services: {len(services)} servicios")
        return True
    
    try:
        result = await gls.get_allowed_services(
            source_country="ES",
            source_zip="28001",
            dest_country="ES",
            dest_zip="08001"
        )
        
        services = result.get("AllowedServices", [])
        print(f"[OK] Servicios permitidos obtenidos: {len(services)}")
        
        for service in services:
            product = service.get("ProductName")
            service_name = service.get("ServiceName")
            if product:
                print(f"  - Producto: {product}")
            if service_name:
                print(f"  - Servicio: {service_name}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo servicios: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_create_shipment():
    """Test 4: Crear envío (con mock para no crear envío real)"""
    print("\n" + "=" * 80)
    print("TEST 4: Crear Envío (MOCK)")
    print("=" * 80)
    print("  (Usando mock para no crear envío real en sandbox)")
    
    gls = GlsAdapter()
    gls.mock_mode = True  # IMPORTANTE: mock para no crear envío real
    
    test_order = {
        "order_id": "TEST-001",
        "customer_name": "Juan Pérez",
        "customer_email": "test@example.com",
        "weight": 2.5,
        "shipping_address": {
            "name": "Juan Pérez",
            "address1": "Calle Test 123",
            "address2": "2º B",
            "city": "Madrid",
            "postal_code": "28001",
            "country": "ES",
            "phone": "+34612345678"
        }
    }
    
    try:
        result = await gls.create_shipment(test_order)
        
        track_id = result.get("track_id")
        status = result.get("status")
        has_label = "label" in result
        
        print(f"[OK] Envio creado (mock)")
        print(f"  TrackID: {track_id}")
        print(f"  Status: {status}")
        print(f"  Etiqueta: {'Si' if has_label else 'No'}")
        
        if has_label:
            label_format = result["label"].get("format")
            label_size = len(result["label"].get("bytes_b64", ""))
            print(f"  Formato etiqueta: {label_format}")
            print(f"  Tamaño etiqueta: {label_size} bytes (base64)")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creando envio: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_get_tracking():
    """Test 5: Consultar tracking (mock)"""
    print("\n" + "=" * 80)
    print("TEST 5: Consultar Tracking (MOCK)")
    print("=" * 80)
    
    gls = GlsAdapter()
    gls.mock_mode = True
    
    try:
        result = await gls.get_shipment_status("GLS1234567")
        
        status = result.get("status")
        events = result.get("events", [])
        
        print(f"[OK] Tracking consultado (mock)")
        print(f"  Status: {status}")
        print(f"  Eventos: {len(events)}")
        
        if events:
            for event in events:
                print(f"    - {event.get('date')}: {event.get('description')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error consultando tracking: {e}")
        return False


async def main():
    """Ejecutar todos los tests"""
    print("\nTEST STANDALONE DE GLS SHIPIT API")
    print("=" * 80)
    print()
    print("CONFIGURACIÓN:")
    
    gls = GlsAdapter()
    print(f"  Base URL: {gls.base_url}")
    print(f"  Auth URL: {gls.auth_url}")
    print(f"  Client ID: {gls.client_id or '(no configurado)'}")
    print(f"  Use OAuth: {gls.use_oauth}")
    print(f"  Mock Mode: {gls.mock_mode}")
    print()
    
    if not gls.client_id or not gls.client_secret:
        print("[WARN] No hay credenciales OAuth2 configuradas")
        print("  Configura GLS_CLIENT_ID y GLS_CLIENT_SECRET en .env")
        print("  Los tests de API real fallaran, pero los mocks funcionaran")
        print()
    
    results = []
    
    # Test 1: OAuth Token (solo si hay credenciales)
    if gls.client_id and gls.client_secret:
        results.append(("OAuth2 Token", await test_oauth_token()))
    else:
        print("=" * 80)
        print("TEST 1: OAuth2 Token - SALTADO (sin credenciales)")
        print("=" * 80)
        results.append(("OAuth2 Token", None))
    
    # Test 2: Validate (solo si hay credenciales)
    if gls.client_id and gls.client_secret:
        results.append(("Validate Shipment", await test_validate_shipment()))
    else:
        print("\n" + "=" * 80)
        print("TEST 2: Validate Shipment - SALTADO (sin credenciales)")
        print("=" * 80)
        results.append(("Validate Shipment", None))
    
    # Test 3: Allowed Services (solo si hay credenciales)
    if gls.client_id and gls.client_secret:
        results.append(("Allowed Services", await test_get_allowed_services()))
    else:
        print("\n" + "=" * 80)
        print("TEST 3: Allowed Services - SALTADO (sin credenciales)")
        print("=" * 80)
        results.append(("Allowed Services", None))
    
    # Test 4: Create Shipment (mock - siempre funciona)
    results.append(("Create Shipment (mock)", await test_create_shipment()))
    
    # Test 5: Get Tracking (mock - siempre funciona)
    results.append(("Get Tracking (mock)", await test_get_tracking()))
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE TESTS")
    print("=" * 80)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, result in results:
        if result is None:
            status = "[-] SALTADO"
            skipped += 1
        elif result:
            status = "[OK] PASO"
            passed += 1
        else:
            status = "[X] FALLO"
            failed += 1
        print(f"{status}: {name}")
    
    print()
    print(f"Total: {len(results)} tests")
    print(f"  Pasados: {passed}")
    print(f"  Fallados: {failed}")
    print(f"  Saltados: {skipped}")
    print()
    
    if failed == 0 and passed > 0:
        print("[OK] TODOS LOS TESTS DISPONIBLES PASARON")
    elif failed > 0:
        print("[ERROR] ALGUNOS TESTS FALLARON")
    else:
        print("[WARN] NO SE EJECUTARON TESTS (configurar credenciales)")
    
    print()
    
    # Guardar resultados
    output_file = Path(__file__).parent / "logs" / "gls_standalone_test_results.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": asyncio.get_event_loop().time(),
            "results": {name: result for name, result in results},
            "summary": {
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "skipped": skipped
            }
        }, f, indent=2)
    
    print(f"[INFO] Resultados guardados en: {output_file}")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n[ERROR] Error ejecutando tests: {e}")
        import traceback
        traceback.print_exc()

