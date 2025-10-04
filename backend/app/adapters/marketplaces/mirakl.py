"""
Mirakl marketplace adapter.

This module implements the MiraklAdapter for interacting with
Mirakl marketplace APIs (OR12, ST11, ST12, OR23).
"""

import httpx
from typing import Dict, Any, List
from datetime import datetime
from typing import Optional, Iterable

from ..interfaces.marketplace import MarketplaceAdapter
from ...core.settings import settings
from ...models.order import OrderStandard
# from ...core.utils.http_client import put_with_retry
from ...core.utils.utils import _csv, _bool_to_str
import logging

# Create logger for this module
logger = logging.getLogger(__name__)

VALID_STATES = {
    "STAGING","WAITING_ACCEPTANCE","WAITING_DEBIT","WAITING_DEBIT_PAYMENT",
    "SHIPPING","SHIPPED","TO_COLLECT","RECEIVED","CLOSED","REFUSED","CANCELED"
}


class MiraklAdapter(MarketplaceAdapter):
    """Mirakl marketplace adapter implementation."""
    
    def __init__(self):
        """Initialize Mirakl adapter."""
        self.api_key = settings.mirakl_api_key
        self.shop_id = settings.mirakl_shop_id
        self.base_url = settings.mirakl_base_url
        self.mock_mode = settings.mirakl_mock_mode
        
        # API endpoints
        self.endpoints = {
            "orders": f"{self.base_url}/api/orders", # OR11
            "order_details": f"{self.base_url}/api/orders/{{order_id}}",
            "tracking": f"{self.base_url}/api/orders/{{order_id}}/tracking", # OR23
            "ship": f"{self.base_url}/api/orders/{{order_id}}/ship", # OR24
            "status": f"{self.base_url}/api/orders/{{order_id}}/status",
            "shipments_tracking": f"{self.base_url}/api/shipments/tracking",
            "available_carriers": f"{self.base_url}/api/carriers",
            "shipment_lines": f"{self.base_url}/api/shipments/{{shipment_id}}/lines"
        }
    
    @property
    def marketplace_name(self) -> str:
        """Get marketplace name."""
        return "mirakl"
    
    @property
    def is_mock_mode(self) -> bool:
        """Check if adapter is in mock mode."""
        return self.mock_mode
    
    async def get_orders(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        order_state_codes: Optional[Iterable[str] | str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_update_date: Optional[str] = None,
        end_update_date: Optional[str] = None,
        order_ids: Optional[Iterable[str] | str] = None,
        channel_codes: Optional[Iterable[str] | str] = None,
        only_null_channel: Optional[bool] = None,
        order_tax_mode: Optional[str] = None,  # "TAX_INCLUDED" | "TAX_EXCLUDED"
        payment_workflow: Optional[str] = None,  # enum de OR11
        customer_debited: Optional[bool] = None,
        has_incident: Optional[bool] = None,
        shop_id: Optional[int] = None,
        locale: Optional[str] = None,  # p.ej. "es_ES"
        sort: Optional[str] = None,    # por defecto dateCreated asc (según OR11)
    ) -> Dict[str, Any]:
        """
        OR11: List orders with pagination (GET /api/orders).
        Devuelve la respuesta de Mirakl con normalización mínima (mapeo limit->max y total_count).
        """

        if self.mock_mode:
            logger.info("🔍 DEBUG: Using mock mode, calling _get_orders_mock")
            result = await self._get_orders_mock(status, limit, offset)
            return result

        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json"
        }

        params = {"max": limit, "offset": offset}

        # CSV
        if (v := _csv(order_state_codes)) is not None:           params["order_state_codes"] = v
        if (v := _csv(order_ids)) is not None:                   params["order_ids"] = v
        if (v := _csv(channel_codes)) is not None:               params["channel_codes"] = v

        # Booleans
        if (v := _bool_to_str(only_null_channel)) is not None:   params["only_null_channel"] = v
        if (v := _bool_to_str(customer_debited)) is not None:    params["customer_debited"] = v
        if (v := _bool_to_str(has_incident)) is not None:        params["has_incident"] = v

        # Strings directas
        if start_date:        params["start_date"] = start_date
        if end_date:          params["end_date"] = end_date
        if start_update_date: params["start_update_date"] = start_update_date
        if end_update_date:   params["end_update_date"] = end_update_date
        if payment_workflow:  params["payment_workflow"] = payment_workflow
        if order_tax_mode:    params["order_tax_mode"] = order_tax_mode
        if shop_id is not None: params["shop_id"] = shop_id
        if locale:            params["locale"] = locale
        if sort:              params["sort"] = sort

        url = self.endpoints["orders"]  # "/api/orders"

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(url, headers=headers, params=params)
                r.raise_for_status()
                data = r.json()
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout get orders from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error get orders from Mirakl: {e}", exc_info=True)
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error get orders from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request failed: {e}")

        data.setdefault("orders", [])
        data.setdefault("total_count", 0)
        data["limit"] = limit
        data["offset"] = offset

        return data

    async def get_all_orders(
        self,
        *,
        batch_size: int = 200,
        order_state_codes: Optional[Iterable[str] | str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_update_date: Optional[str] = None,
        end_update_date: Optional[str] = None,
        order_ids: Optional[Iterable[str] | str] = None,
        order_references_for_customer: Optional[Iterable[str] | str] = None,
        order_references_for_seller: Optional[Iterable[str] | str] = None,
        channel_codes: Optional[Iterable[str] | str] = None,
        only_null_channel: Optional[bool] = None,
        customer_debited: Optional[bool] = None,
        payment_workflow: Optional[str] = None,
        has_incident: Optional[bool] = None,
        fulfillment_center_code: Optional[Iterable[str] | str] = None,
        order_tax_mode: Optional[str] = None,
        shop_id: Optional[int] = None,
        locale: Optional[str] = None,
        sort: Optional[str] = None,
        extra_filters: Optional[Dict[str, Any]] = None,
        max_pages: int = 1000,     # cortafuegos para evitar bucles infinitos
    ) -> list[dict]:
        """
        Trae *todas* las órdenes iterando por páginas hasta que una página venga vacía.
        No usa total_count como condición de parada.
        Aplica los mismos filtros que get_orders.
        """

        all_orders: list[dict] = []
        offset = 0
        pages = 0

        while True:
            data = await self.get_orders(
                limit=batch_size,
                offset=offset,
                order_state_codes=order_state_codes,
                start_date=start_date,
                end_date=end_date,
                start_update_date=start_update_date,
                end_update_date=end_update_date,
                order_ids=order_ids,
                order_references_for_customer=order_references_for_customer,
                order_references_for_seller=order_references_for_seller,
                channel_codes=channel_codes,
                only_null_channel=only_null_channel,
                customer_debited=customer_debited,
                payment_workflow=payment_workflow,
                has_incident=has_incident,
                fulfillment_center_code=fulfillment_center_code,
                order_tax_mode=order_tax_mode,
                shop_id=shop_id,
                locale=locale,
                sort=sort,
                extra_filters=extra_filters,
            )

            batch = data.get("orders", [])
            all_orders.extend(batch)

            if len(batch) < batch_size:
                break  # no hay más páginas

            # condición de parada: página vacía
            if not batch:
                break

            offset += batch_size
            pages += 1
            if pages >= max_pages:
                logger.warning("get_all_orders: alcanzado max_pages=%s; deteniendo iteración", max_pages)
                break

        return all_orders

    def _convert_mirakl_to_order_standard(self, mirakl_product: Dict[str, Any]) -> OrderStandard:
        """
        Convert Mirakl product data to OrderStandard format
        
        Args:
            mirakl_product: Raw Mirakl product data
            
        Returns:
            OrderStandard object
        """
        logger.info(f"🔍 DEBUG: _convert_mirakl_to_order_standard called with product: {mirakl_product.get('Referencia', 'UNKNOWN')}")
        
        order_standard = OrderStandard(
            # Core identification
            order_id=mirakl_product.get("Referencia", ""),  # Use reference as order_id for now
            reference=mirakl_product.get("Referencia", ""),
            created_at=datetime.now(),
            status="PENDING",
            
            # Recipient information
            recipient_name=mirakl_product.get("Nombre Consignatario", ""),
            recipient_address=mirakl_product.get("Dirección Consignatario", ""),
            recipient_city=mirakl_product.get("Poblacion Consignatario", ""),
            recipient_postal_code=mirakl_product.get("Código Postal Consignatario", ""),
            recipient_country=mirakl_product.get("País del Consignatario", "ES"),
            recipient_contact=mirakl_product.get("Contacto Consignatario", ""),
            recipient_phone=mirakl_product.get("Teléfono Consignatario", ""),
            recipient_email=mirakl_product.get("Email Destino", ""),
            recipient_tax_id=mirakl_product.get("Nif Consignatario", ""),
            
            # Package information
            packages=mirakl_product.get("Bultos", "1"),
            weight_kg=mirakl_product.get("Kilos", "0.1"),
            volume=mirakl_product.get("Volumen", ""),
            package_type=mirakl_product.get("Tipo Bultos", ""),
            
            # Product information
            product_name=mirakl_product.get("Producto", ""),
            shipping_cost=mirakl_product.get("Portes", "0.00"),
            cash_on_delivery=mirakl_product.get("Reembolso", "0.00"),
            
            # Customer information
            customer_name=mirakl_product.get("Nombre Cliente", ""),
            customer_code=mirakl_product.get("Código Cliente", ""),
            customer_department=mirakl_product.get("Departamento Cliente", ""),
            
            # Additional fields
            observations=mirakl_product.get("Observaciones1", ""),
            deferred_date=mirakl_product.get("Fecha Aplazada", ""),
            return_flag=mirakl_product.get("Retorno", "N"),
            return_confirmation=mirakl_product.get("Devolución Conforme", "N"),
            multi_reference=mirakl_product.get("Multireferencia", ""),
            date=mirakl_product.get("Fecha", "")
        )
        
        logger.info(f"🔍 DEBUG: Created OrderStandard with order_id={order_standard.order_id}")
        logger.info(f"🔍 DEBUG: OrderStandard has recipient_name: {order_standard.recipient_name}")
        logger.info(f"🔍 DEBUG: OrderStandard dict keys: {list(order_standard.dict().keys())}")
        
        return order_standard
    
    async def get_available_carriers(self) -> List[Dict[str, Any]]:
        """
        Get list of available carriers in Mirakl instance.
        
        Returns:
            List of carriers with codes and names.
        """
        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json"
        }

        url = self.endpoints["available_carriers"]

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching carriers from Mirakl: {e}", exc_info=True)
            raise Exception(f"Could not retrieve carriers: {e}")

    async def _get_orders_mock(self, status: str, limit: int, offset: int) -> Dict[str, Any]:
        """Mock implementation of get_orders with Mirakl product columns."""
        logger.info(f"🔍 DEBUG: _get_orders_mock called with status={status}, limit={limit}, offset={offset}")
        
        # Valores posibles de order state codes 
        if status not in ["STAGING", "WAITING_ACCEPTANCE", "WAITING_DEBIT", "WAITING_DEBIT_PAYMENT", "SHIPPING", "SHIPPED", "TO_COLLECT", "RECEIVED", "CLOSED", "REFUSED", "CANCELED"]:
            raise ValueError(f"Invalid status in Mirakl get_orders: {status}")

        # Mock Mirakl product data with specific columns
        mock_mirakl_products = [
            {
                "Referencia": "MIR-001",
                "Nombre Consignatario": "Juan Pérez",
                "Dirección Consignatario": "Calle Mayor 123",
                "Poblacion Consignatario": "Madrid",
                "Código Postal Consignatario": "28001",
                "País del Consignatario": "ES",
                "Contacto Consignatario": "Juan Pérez",
                "Teléfono Consignatario": "+34612345678",
                "Bultos": "1",
                "Kilos": "1.5",
                "Volumen": "0.01",
                "Portes": "0.00",
                "Producto": "Producto Test 1",
                "Reembolso": "0.00",
                "Fecha Aplazada": "",
                "Observaciones1": "Envío estándar",
                "Email Destino": "juan.perez@email.com",
                "Tipo Bultos": "Paquete",
                "Departamento Cliente": "Ventas",
                "Devolución Conforme": "N",
                "Fecha": "2025-09-19",
                "Nif Consignatario": "",
                "Nombre Cliente": "Juan Pérez",
                "Retorno": "N",
                "Código Cliente": "CLI-001",
                "Multireferencia": "MIR-001-REF"
            },
            {
                "Referencia": "MIR-002",
                "Nombre Consignatario": "María García",
                "Dirección Consignatario": "Avenida de la Paz 456",
                "Poblacion Consignatario": "Barcelona",
                "Código Postal Consignatario": "08001",
                "País del Consignatario": "ES",
                "Contacto Consignatario": "María García",
                "Teléfono Consignatario": "+34687654321",
                "Bultos": "1",
                "Kilos": "0.8",
                "Volumen": "0.005",
                "Portes": "0.00",
                "Producto": "Producto Test 2",
                "Reembolso": "0.00",
                "Fecha Aplazada": "",
                "Observaciones1": "Entrega urgente",
                "Email Destino": "maria.garcia@email.com",
                "Tipo Bultos": "Sobre",
                "Departamento Cliente": "Ventas",
                "Devolución Conforme": "N",
                "Fecha": "2025-09-19",
                "Nif Consignatario": "",
                "Nombre Cliente": "María García",
                "Retorno": "N",
                "Código Cliente": "CLI-002",
                "Multireferencia": "MIR-002-REF"
            },
            {
                "Referencia": "MIR-003",
                "Nombre Consignatario": "Carlos López",
                "Dirección Consignatario": "Plaza España 789",
                "Poblacion Consignatario": "Valencia",
                "Código Postal Consignatario": "46001",
                "País del Consignatario": "ES",
                "Contacto Consignatario": "Carlos López",
                "Teléfono Consignatario": "+34987654321",
                "Bultos": "3",
                "Kilos": "2.0",
                "Volumen": "0.02",
                "Portes": "0.00",
                "Producto": "Producto Test 3",
                "Reembolso": "0.00",
                "Fecha Aplazada": "",
                "Observaciones1": "Múltiples unidades",
                "Email Destino": "carlos.lopez@email.com",
                "Tipo Bultos": "Caja",
                "Departamento Cliente": "Ventas",
                "Devolución Conforme": "N",
                "Fecha": "2025-09-19",
                "Nif Consignatario": "",
                "Nombre Cliente": "Carlos López",
                "Retorno": "N",
                "Código Cliente": "CLI-003",
                "Multireferencia": "MIR-003-REF"
            },
            {
                "Referencia": "MIR-004",
                "Nombre Consignatario": "Ana Martín",
                "Dirección Consignatario": "Calle del Sol 321",
                "Poblacion Consignatario": "Sevilla",
                "Código Postal Consignatario": "41001",
                "País del Consignatario": "ES",
                "Contacto Consignatario": "Ana Martín",
                "Teléfono Consignatario": "+34654321098",
                "Bultos": "1",
                "Kilos": "1.5",
                "Volumen": "0.008",
                "Portes": "0.00",
                "Producto": "Producto Test 4",
                "Reembolso": "28.90",
                "Fecha Aplazada": "",
                "Observaciones1": "Reembolso incluido",
                "Email Destino": "ana.martin@email.com",
                "Tipo Bultos": "Paquete",
                "Departamento Cliente": "Ventas",
                "Devolución Conforme": "N",
                "Fecha": "2025-09-19",
                "Nif Consignatario": "12345678A",
                "Nombre Cliente": "Ana Martín",
                "Retorno": "N",
                "Código Cliente": "CLI-004",
                "Multireferencia": "MIR-004-REF"
            }
        ]
        
        # Convert Mirakl products to OrderStandard format
        logger.info(f"🔍 DEBUG: Converting {len(mock_mirakl_products)} mock products to OrderStandard")
        orders = []
        for i, mirakl_product in enumerate(mock_mirakl_products):
            logger.info(f"🔍 DEBUG: Converting product {i+1}: {mirakl_product.get('Referencia', 'UNKNOWN')}")
            order_standard = self._convert_mirakl_to_order_standard(mirakl_product)
            order_dict = order_standard.dict()
            logger.info(f"🔍 DEBUG: Converted order dict keys: {list(order_dict.keys())}")
            logger.info(f"🔍 DEBUG: Converted order has recipient_name: {'recipient_name' in order_dict}")
            logger.info(f"🔍 DEBUG: Converted order has buyer: {'buyer' in order_dict}")
            orders.append(order_dict)
        
        # Apply pagination
        paginated_orders = orders[offset:offset + limit]
        logger.info(f"🔍 DEBUG: Paginated orders: {len(paginated_orders)} orders")
        
        result = {
            "orders": paginated_orders,
            "total": len(orders),
            "limit": limit,
            "offset": offset
        }
        
        # Log operation
        logger.info(f"🔍 DEBUG: _get_orders_mock returning {len(result.get('orders', []))} orders")
        if result.get('orders'):
            first_order = result['orders'][0]
            logger.info(f"🔍 DEBUG: Final first order keys: {list(first_order.keys())}")
        
        return result
    
    async def _get_orders_real(self, status: str, limit: int, offset: int) -> Dict[str, Any]:
        """Real implementation of get_orders."""
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Valores posibles de order state codes 
        if status not in ["STAGING", "WAITING_ACCEPTANCE", "WAITING_DEBIT", "WAITING_DEBIT_PAYMENT", "SHIPPING", "SHIPPED", "TO_COLLECT", "RECEIVED", "CLOSED", "REFUSED", "CANCELED"]:
            raise ValueError(f"Invalid status in Mirakl get_orders: {status}")
        
        params = {
            "order_state_codes": status,
            "limit": limit,
            "offset": offset
        }
        
        timeout = httpx.Timeout(10.0, connect=5.0, read=10.0, write=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    self.endpoints["orders"],
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout getting orders from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error getting orders from Mirakl: {e}", exc_info=True)
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error getting orders from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request failed: {e}")
    
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific order."""
        if self.mock_mode:
            return await self._get_order_details_mock(order_id)
        
        return await self._get_order_details_real(order_id)
    
    async def _get_order_details_mock(self, order_id: str) -> Dict[str, Any]:
        """Mock implementation of get_order_details."""
        # Mock order details
        mock_details = {
            "order_id": order_id,
            "marketplace": "mirakl",
            "status": "PENDING",
            "customer_name": "Juan Pérez",
            "customer_email": "juan.perez@email.com",
            "weight": 2.5,
            "total_amount": 45.99,
            "currency": "EUR",
            "created_at": "2025-09-19T20:00:00Z",
            "shipping_address": {
                "name": "Juan Pérez",
                "street": "Calle Mayor 123",
                "city": "Madrid",
                "postal_code": "28001",
                "country": "ES"
            },
            "items": [
                {
                    "sku": "PROD-001",
                    "name": "Producto de ejemplo",
                    "quantity": 1,
                    "price": 45.99
                }
            ]
        }
        
        # Log operation
        logger.info(f"Operation completed")
        
        return mock_details
    
    async def _get_order_details_real(self, order_id: str) -> Dict[str, Any]:
        """Real implementation of get_order_details."""
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        url = self.endpoints["order_details"].format(order_id=order_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def update_order_tracking(
        self,
        order_id: str,
        tracking_number: str,
        *,
        carrier_code: Optional[str] = None,
        carrier_url: Optional[str] = None,
        carrier_standard_code: Optional[str] = None,
        carrier_name: Optional[str] = None,
        shop_id: Optional[int] = None,
        validate_shipment: bool = True,
    ) -> Dict[str, Any]:
        """OR23: update tracking; opcionalmente lanza OR24 (ship)."""

        if self.mock_mode:
            return await self._update_order_tracking_mock(
                order_id=order_id,
                tracking_number=tracking_number,
                carrier_code=carrier_code,
                carrier_name=carrier_name,
                carrier_url=carrier_url,
                carrier_standard_code=carrier_standard_code,
                shop_id=shop_id,
                validate_shipment=validate_shipment,
            )
        
         # 1) Validación de inputs (uno de los dos)
        if not carrier_code and not carrier_name:
            raise ValueError("Debes indicar 'carrier_code' (registrado) o 'carrier_name' (no registrado).")

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload: Dict[str, Any] = {
            **({"carrier_code": carrier_code} if carrier_code else {}),
            **({"carrier_name": carrier_name} if carrier_name else {}),
            **({"carrier_standard_code": carrier_standard_code} if carrier_standard_code else {}),
            **({"carrier_url": carrier_url} if carrier_url else {}),
            "tracking_number": tracking_number,
        }

        url = self.endpoints["tracking"].format(order_id=order_id)

        if shop_id is not None:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}shop_id={shop_id}"

        result: Dict[str, Any]

        # TODO: añadir esto a futuro para el endpoint. sustituir el put por put_with_retry
        # r1 = await put_with_retry(url, headers=headers, json=payload)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r1 = await client.put(url, headers=headers, json=payload)

                if r1.status_code == 204:
                    result = {
                        "success": True,
                        "order_id": order_id,
                        "endpoint": "OR23",
                        "status_code": r1.status_code,
                        "message": "Tracking info updated successfully (204 No Content)",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }
                else:
                    # raise_for_status() cubrirá los 4xx/5xx
                    if 400 <= r1.status_code:
                        r1.raise_for_status()
                    # 2xx distinto de 204 = inesperado pero no fatal
                    result = {
                        "success": False,
                        "order_id": order_id,
                        "endpoint": "OR23",
                        "status_code": r1.status_code,
                        "message": f"Unexpected success status (expected 204). Body preview: {r1.text[:200]}",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }

                if validate_shipment and result.get("success"):
                    ship_url = self.endpoints["ship"].format(order_id=order_id)  # /api/orders/{order_id}/ship

                    if shop_id is not None:
                        sep = "&" if "?" in ship_url else "?"
                        ship_url = f"{ship_url}{sep}shop_id={shop_id}"
                    r2 = await client.put(ship_url, headers=headers)
                    if r2.status_code == 204:
                        result["shipment_validated"] = True
                        result["shipment_validation"] = {
                            "success": True,
                            "status_code": 204,
                            "endpoint": "OR24",
                            "message": "Shipment validated (204 No Content)",
                        }
                    else:
                        if 400 <= r2.status_code:
                            r2.raise_for_status()
                        result["shipment_validated"] = False
                        result["shipment_validation"] = {
                            "success": False,
                            "status_code": r2.status_code,
                            "message": f"Unexpected status in OR24: {r2.text[:200]}",
                        }
            return result
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout update order tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error update order tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error update order tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request failed: {e}")
        
    
    async def _update_order_tracking_mock(
        self,
        order_id: str,
        tracking_number: str,
        carrier_code: Optional[str] = None,
        carrier_name: Optional[str] = None,
        *,
        carrier_url: Optional[str] = None,
        carrier_standard_code: Optional[str] = None,
        shop_id: Optional[int] = None,
        validate_shipment: bool = True,
    ) -> Dict[str, Any]:
        """Mock de OR23 + OR24 con preview de request y cabeceras correctas."""
        if not carrier_code and not carrier_name:
            raise ValueError("[MOCK] Falta 'carrier_code' o 'carrier_name'.")

        headers = {
            "Authorization": self.api_key,  # sin 'Bearer'
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload: Dict[str, Any] = {
            **({"carrier_code": carrier_code} if carrier_code else {}),
            **({"carrier_name": carrier_name} if carrier_name else {}),
            **({"carrier_standard_code": carrier_standard_code} if carrier_standard_code else {}),
            **({"carrier_url": carrier_url} if carrier_url else {}),
            "tracking_number": tracking_number,
        }

        url = self.endpoints["tracking"].format(order_id=order_id)
        if shop_id is not None:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}shop_id={shop_id}"

        result: Dict[str, Any] = {
            "success": True,
            "order_id": order_id,
            "endpoint": "OR23",
            "status_code": 204,
            "message": "[MOCK] Tracking info updated (simulated 204)",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_preview": {"method": "PUT", "url": url, "headers": headers, "payload": payload},
            "mock": True,
        }

        if validate_shipment:
            ship_url = self.endpoints["ship"].format(order_id=order_id)
            if shop_id is not None:
                sep = "&" if "?" in ship_url else "?"
                ship_url = f"{ship_url}{sep}shop_id={shop_id}"

            result["shipment_validated"] = True
            result["shipment_validation"] = {
                "success": True,
                "status_code": 204,
                "endpoint": "OR24",
                "message": "[MOCK] Shipment validated (simulated 204)",
                "request_preview": {"method": "PUT", "url": ship_url, "headers": headers, "payload": None},
            }

        logger.info("[MOCK] OR23%s completado para order_id=%s",
                    " + OR24" if validate_shipment else "", order_id)
        return result

    async def update_order_status(self, order_id: str, 
                                status: str, 
                                reason: str = None) -> Dict[str, Any]:
        """Update order status."""
        if self.mock_mode:
            return await self._update_order_status_mock(order_id, status, reason)
        
        return await self._update_order_status_real(order_id, status, reason)
    
    async def _update_order_status_mock(self, order_id: str, 
                                      status: str, 
                                      reason: str = None) -> Dict[str, Any]:
        """Mock implementation of update_order_status."""
        result = {
            "success": True,
            "message": f"Order status updated to {status}",
            "order_id": order_id,
            "status": status,
            "reason": reason,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Log operation
        logger.info(f"Operation completed")
        
        return result
    
    async def _update_order_status_real(self, order_id: str, 
                                      status: str, 
                                      reason: str = None) -> Dict[str, Any]:
        """Real implementation of update_order_status."""
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "status": status,
            "reason": reason
        }
        
        url = self.endpoints["status"].format(order_id=order_id)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout update order status from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error update order status from Mirakl: {e}", exc_info=True)
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error update order status from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request failed: {e}")
    
    async def update_order_ship(self, order_id: str, carrier_code: str, 
                               carrier_name: str, tracking_number: str) -> Dict[str, Any]:
        """
        Update order status to SHIPPED (OR24).
        
        Reference: https://developer.mirakl.net/api-reference/order-management-api/order-management-api/orders/put-orders-order-id-ship
        
        Args:
            order_id: Order ID
            carrier_code: Carrier code (e.g., 'tipsa', 'dhl')
            carrier_name: Carrier name (e.g., 'TIPSA', 'DHL')
            tracking_number: Tracking number
            
        Returns:
            Response data
        """
        if self.mock_mode:
            return await self._update_order_ship_mock(order_id, carrier_code, carrier_name, tracking_number)
        
        return await self._update_order_ship_real(order_id, carrier_code, carrier_name, tracking_number)
    
    async def _update_order_ship_mock(self, order_id: str, carrier_code: str, 
                                    carrier_name: str, tracking_number: str) -> Dict[str, Any]:
        """Mock implementation of update_order_ship."""
        logger.info(f"Operation completed")
        
        return {
            "order_id": order_id,
            "status": "SHIPPED",
            "carrier_code": carrier_code,
            "carrier_name": carrier_name,
            "tracking_number": tracking_number,
            "shipped_at": datetime.utcnow().isoformat()
        }
    
    async def _update_order_ship_real(self, order_id: str, carrier_code: str, 
                                    carrier_name: str, tracking_number: str) -> Dict[str, Any]:
        """Real implementation of update_order_ship."""
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "carrier_code": carrier_code,
            "carrier_name": carrier_name,
            "tracking_number": tracking_number,
            "shipped_at": datetime.utcnow().isoformat()
        }
        
        url = self.endpoints["ship"].format(order_id=order_id)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(url, headers=headers, json=data)
                response.raise_for_status()
                # OR24 returns 204 No Content, so no JSON response
                if response.status_code == 204:
                    return {"status": "success", "order_id": order_id}
                return response.json()
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout update shipments tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error update shipments tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected update shipments tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request failed: {e}")
    
    async def update_shipments_tracking(
        self, 
        shipments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update tracking for multiple shipments (ST23).
        
        Reference: https://developer.mirakl.net/api-reference/order-management-api/shipment-management-api/shipments/post-shipments-tracking
        
        Args:
            shipments: List of shipment tracking data
            
        Returns:
            Response data
        """
        if self.mock_mode:
            return await self._update_shipments_tracking_mock(shipments)

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "shipments": []
        }

        for shipment in shipments:
            shipment_entry = {
                "id": shipment["shipment_id"],  # debe ser el shipment ID de Mirakl, no el order_id
                "tracking": {
                    "carrier_code": shipment.get("carrier_code"),
                    "carrier_name": shipment.get("carrier_name"),
                    "carrier_standard_code": shipment.get("carrier_standard_code", shipment.get("carrier_code")),
                    "tracking_number": shipment.get("tracking_number")
                }
            }

            if shipment.get("tracking_url"):
                shipment_entry["tracking"]["tracking_url"] = shipment["tracking_url"].replace("{trackingId}", shipment["tracking_number"])

            payload["shipments"].append(shipment_entry)

        url = self.endpoints["shipments_tracking"]
        params = {}

        if self.shop_id:
            params["shop_id"] = self.shop_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout update shipments tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error update shipments tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error update shipments tracking from Mirakl: {e}", exc_info=True)
            raise Exception(f"Request failed: {e}")
    
    async def _update_shipments_tracking_mock(self, shipments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock implementation of update_shipments_tracking aligned with ST23."""
        logger.info(f"[MOCK] update_shipments_tracking: Processing {len(shipments)} shipments")

        shipment_success = []
        shipment_errors = []

        for shipment in shipments:
            shipment_id = shipment.get("shipment_id")
            
            if shipment_id and shipment.get("tracking_number"):
                shipment_success.append({"id": shipment_id})
            else:
                shipment_errors.append({
                    "id": shipment_id or "unknown",
                    "message": "Missing shipment_id or tracking_number in mock input"
                })

        return {
            "updated_shipments": len(shipment_success),
            "shipments": shipment_success
        }

    async def get_shipment_lines(
        self, 
        shipment_id: str
    ) -> List[Dict[str, Any]]:
        """
        OR25: Get shipment lines for a given shipment ID.
        
        Args:
            shipment_id: The shipment ID in Mirakl
            
        Returns:
            List of shipment lines
        """
        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json"
        }

        url = self.endpoints["shipment_lines"].format(shipment_id=shipment_id)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching shipment lines for {shipment_id}: {e}", exc_info=True)
            raise Exception(f"Failed to fetch shipment lines for {shipment_id}: {e}")
