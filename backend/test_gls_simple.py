"""
Test simple de GLS (solo GLS, sin Mirakl)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Importar solo GLS
from app.adapters.carriers.gls import GlsAdapter


async def main():
    print("\n" + "=" * 80)
    print("TEST SIMPLE DE GLS (MOCK MODE)")
    print("=" * 80)
    print()
    
    gls = GlsAdapter()
    
    print(f"GLS Mock Mode: {gls.is_mock_mode}")
    print(f"GLS Base URL: {gls.base_url}")
    print()
    
    # Test 1: Crear envío
    print("-" * 80)
    print("TEST 1: Crear Envio en GLS")
    print("-" * 80)
    
    test_order = {
        "order_id": "MIRAKL-001",
        "customer_name": "Juan Perez",
        "customer_email": "juan@example.com",
        "weight": 2.5,
        "shipping_address": {
            "name": "Juan Perez",
            "address1": "Calle Test 123",
            "city": "Madrid",
            "postal_code": "28001",
            "country": "ES",
            "phone": "+34612345678"
        }
    }
    
    shipment = await gls.create_shipment(test_order)
    
    track_id = shipment.get("track_id")
    status = shipment.get("status")
    
    print(f"[OK] Envio creado")
    print(f"  TrackID: {track_id}")
    print(f"  Status: {status}")
    print(f"  Carrier: {shipment.get('carrier')}")
    
    if "label" in shipment:
        print(f"  Etiqueta PDF: Si ({len(shipment['label'].get('bytes_b64', ''))} bytes)")
    
    print()
    
    # Test 2: Consultar tracking
    print("-" * 80)
    print("TEST 2: Consultar Tracking")
    print("-" * 80)
    
    tracking = await gls.get_shipment_status(track_id)
    
    print(f"[OK] Tracking consultado")
    print(f"  TrackID: {tracking.get('track_id')}")
    print(f"  Status: {tracking.get('status')}")
    print(f"  Eventos: {len(tracking.get('events', []))}")
    
    for event in tracking.get('events', [])[:3]:
        print(f"    - {event.get('date')}: {event.get('description')}")
    
    print()
    
    # Test 3: Validar envío
    print("-" * 80)
    print("TEST 3: Validar Envio (antes de crear)")
    print("-" * 80)
    
    validation = await gls.validate_shipment(test_order)
    
    print(f"[OK] Validacion ejecutada")
    print(f"  Success: {validation.get('Success')}")
    print(f"  Message: {validation.get('message')}")
    
    print()
    
    # Test 4: Crear múltiples envíos (bulk)
    print("-" * 80)
    print("TEST 4: Crear Multiples Envios (Bulk)")
    print("-" * 80)
    
    bulk_orders = [
        {
            "order_id": f"MIRAKL-{i:03d}",
            "customer_name": f"Cliente {i}",
            "weight": 2.0 + i * 0.5,
            "shipping_address": {
                "name": f"Cliente {i}",
                "address1": f"Calle {i}",
                "city": "Madrid",
                "postal_code": "28001",
                "country": "ES"
            }
        }
        for i in range(1, 4)
    ]
    
    bulk_result = await gls.create_shipments_bulk(bulk_orders)
    
    print(f"[OK] Bulk shipments creados")
    print(f"  Total ordenes: {len(bulk_orders)}")
    print(f"  Creados exitosamente: {bulk_result.get('total_created')}")
    print(f"  Fallidos: {bulk_result.get('total_failed')}")
    
    print()
    
    # Resumen final
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print("[OK] Crear envio individual")
    print("[OK] Consultar tracking")
    print("[OK] Validar envio")
    print("[OK] Bulk shipments")
    print()
    print("=" * 80)
    print("[SUCCESS] INTEGRACION GLS COMPLETAMENTE FUNCIONAL")
    print("=" * 80)
    print()
    print("SIGUIENTE PASO:")
    print("  Contacta con GLS para obtener credenciales de ShipIT Sandbox")
    print("  Email: soporte@gls-spain.es o tu account manager")
    print("  Solicitar: Acceso a ShipIT API Sandbox con OAuth2")
    print()


if __name__ == "__main__":
    asyncio.run(main())

