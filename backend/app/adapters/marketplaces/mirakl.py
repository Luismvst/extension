"""
Mirakl marketplace adapter.

This module implements the MiraklAdapter for interacting with
Mirakl marketplace APIs (OR12, ST11, ST12, OR23).
"""

import httpx
from typing import Dict, Any, List
from datetime import datetime

from ..interfaces.marketplace import MarketplaceAdapter
from ...core.settings import settings
import logging

# Create logger for this module
logger = logging.getLogger(__name__)


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
            "orders": f"{self.base_url}/api/orders",
            "order_details": f"{self.base_url}/api/orders/{{order_id}}",
            "tracking": f"{self.base_url}/api/orders/{{order_id}}/tracking",
            "ship": f"{self.base_url}/api/orders/{{order_id}}/ship",
            "status": f"{self.base_url}/api/orders/{{order_id}}/status",
            "shipments_tracking": f"{self.base_url}/api/shipments/tracking"
        }
    
    @property
    def marketplace_name(self) -> str:
        """Get marketplace name."""
        return "mirakl"
    
    @property
    def is_mock_mode(self) -> bool:
        """Check if adapter is in mock mode."""
        return self.mock_mode
    
    async def get_orders(self, status: str = "PENDING",  # TODO adaptar esto
                        limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get orders from Mirakl (OR12)."""
        if self.mock_mode:
            return await self._get_orders_mock(status, limit, offset)
        
        return await self._get_orders_real(status, limit, offset)
    
    async def _get_orders_mock(self, status: str, limit: int, offset: int) -> Dict[str, Any]:
        """Mock implementation of get_orders."""
        # Mock orders data with different statuses
        mock_orders = [
            {
                "order_id": "MIR-001",
                "marketplace": "mirakl",
                "status": "SHIPPED",
                "created_at": "2025-09-19T20:00:00Z",
                "items": [
                    {
                        "sku": "SKU-001",
                        "name": "Producto Test 1",
                        "qty": 2,
                        "unit_price": 22.99,
                        "weight_kg": 1.5
                    }
                ],
                "buyer": {
                    "name": "Juan Pérez",
                    "email": "juan.perez@email.com",
                    "phone": "+34612345678"
                },
                "shipping": {
                    "name": "Juan Pérez",
                    "address1": "Calle Mayor 123",
                    "city": "Madrid",
                    "postal_code": "28001",
                    "country": "ES"
                },
                "totals": {
                    "goods": 45.98,
                    "shipping": 0.0,
                    "total": 45.98,
                    "currency": "EUR"
                }
            },
            {
                "order_id": "MIR-002",
                "marketplace": "mirakl",
                "status": "SHIPPED",
                "created_at": "2025-09-19T21:00:00Z",
                "items": [
                    {
                        "sku": "SKU-002",
                        "name": "Producto Test 2",
                        "qty": 1,
                        "unit_price": 32.50,
                        "weight_kg": 0.8
                    }
                ],
                "buyer": {
                    "name": "María García",
                    "email": "maria.garcia@email.com",
                    "phone": "+34687654321"
                },
                "shipping": {
                    "name": "María García",
                    "address1": "Avenida de la Paz 456",
                    "city": "Barcelona",
                    "postal_code": "08001",
                    "country": "ES"
                },
                "totals": {
                    "goods": 32.50,
                    "shipping": 0.0,
                    "total": 32.50,
                    "currency": "EUR"
                }
            },
            {
                "order_id": "MIR-003",
                "marketplace": "mirakl",
                "status": "SHIPPED",
                "created_at": "2025-09-19T18:00:00Z",
                "items": [
                    {
                        "sku": "SKU-003",
                        "name": "Producto Test 3",
                        "qty": 3,
                        "unit_price": 22.60,
                        "weight_kg": 2.0
                    }
                ],
                "buyer": {
                    "name": "Carlos López",
                    "email": "carlos.lopez@email.com",
                    "phone": "+34987654321"
                },
                "shipping": {
                    "name": "Carlos López",
                    "address1": "Plaza España 789",
                    "city": "Valencia",
                    "postal_code": "46001",
                    "country": "ES"
                },
                "totals": {
                    "goods": 67.80,
                    "shipping": 0.0,
                    "total": 67.80,
                    "currency": "EUR"
                }
            },
            {
                "order_id": "MIR-004",
                "marketplace": "mirakl",
                "status": "SHIPPED",
                "customer_name": "Ana Martín",
                "customer_email": "ana.martin@email.com",
                "weight": 1.5,
                "total_amount": 28.90,
                "currency": "EUR",
                "created_at": "2025-09-19T16:00:00Z",
                "shipping_address": {
                    "name": "Ana Martín",
                    "street": "Calle del Sol 321",
                    "city": "Sevilla",
                    "postal_code": "41001",
                    "country": "ES"
                }
            }
        ]
        
        # Filter by status - only show PENDING and PENDING_APPROVAL orders
        if status in ["PENDING", "PENDING_APPROVAL"]:
            filtered_orders = [order for order in mock_orders if order["status"] in ["PENDING", "PENDING_APPROVAL"]]
        else:
            filtered_orders = [order for order in mock_orders if order["status"] == status]
        
        # Apply pagination
        paginated_orders = filtered_orders[offset:offset + limit]
        
        result = {
            "orders": paginated_orders,
            "total": len(filtered_orders),
            "limit": limit,
            "offset": offset
        }
        
        # Log operation
        logger.info(f"get_orders: Retrieved {len(result.get('orders', []))} orders")
        
        return result
    
    async def _get_orders_real(self, status: str, limit: int, offset: int) -> Dict[str, Any]:
        """Real implementation of get_orders."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
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
            "status": "SHIPPING",
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = self.endpoints["order_details"].format(order_id=order_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def update_order_tracking(self, order_id: str, 
                                  tracking_number: str, 
                                  carrier_code: str,
                                  carrier_name: str) -> Dict[str, Any]:
        """Update order with tracking information (OR23)."""
        if self.mock_mode:
            return await self._update_order_tracking_mock(
                order_id, tracking_number, carrier_code, carrier_name
            )
        
        return await self._update_order_tracking_real(
            order_id, tracking_number, carrier_code, carrier_name
        )
    
    async def _update_order_tracking_mock(self, order_id: str, 
                                        tracking_number: str, 
                                        carrier_code: str,
                                        carrier_name: str) -> Dict[str, Any]:
        """Mock implementation of update_order_tracking."""
        result = {
            "success": True,
            "message": f"Tracking updated successfully for order {order_id}",
            "tracking_number": tracking_number,
            "carrier_code": carrier_code,
            "carrier_name": carrier_name,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Log operation
        logger.info(f"Operation completed")
        
        return result
    
    async def _update_order_tracking_real(self, order_id: str, 
                                        tracking_number: str, 
                                        carrier_code: str,
                                        carrier_name: str) -> Dict[str, Any]:
        """Real implementation of update_order_tracking."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "tracking_number": tracking_number,
            "carrier_code": carrier_code,
            "carrier_name": carrier_name
        }
        
        url = self.endpoints["tracking"].format(order_id=order_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "status": status,
            "reason": reason
        }
        
        url = self.endpoints["status"].format(order_id=order_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "carrier_code": carrier_code,
            "carrier_name": carrier_name,
            "tracking_number": tracking_number,
            "shipped_at": datetime.utcnow().isoformat()
        }
        
        url = self.endpoints["ship"].format(order_id=order_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=data)
            response.raise_for_status()
            # OR24 returns 204 No Content, so no JSON response
            if response.status_code == 204:
                return {"status": "success", "order_id": order_id}
            return response.json()
    
    async def update_shipments_tracking(self, shipments: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        
        return await self._update_shipments_tracking_real(shipments)
    
    async def _update_shipments_tracking_mock(self, shipments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock implementation of update_shipments_tracking."""
        logger.info(f"update_shipments_tracking: Updated {len(shipments)} shipments")
        
        return {
            "updated_shipments": len(shipments),
            "shipments": [
                {
                    "shipment_id": shipment.get("shipment_id"),
                    "order_id": shipment.get("order_id"),
                    "status": "TRACKING_UPDATED",
                    "carrier_code": shipment.get("carrier_code"),
                    "carrier_name": shipment.get("carrier_name"),
                    "tracking_number": shipment.get("tracking_number")
                }
                for shipment in shipments
            ]
        }
    
    async def _update_shipments_tracking_real(self, shipments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Real implementation of update_shipments_tracking."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "shipments": [
                {
                    "shipment_id": shipment.get("shipment_id"),
                    "order_id": shipment.get("order_id"),
                    "carrier_code": shipment.get("carrier_code"),
                    "carrier_name": shipment.get("carrier_name"),
                    "carrier_url": shipment.get("carrier_url"),
                    "carrier_standard_code": shipment.get("carrier_standard_code"),
                    "tracking_number": shipment.get("tracking_number")
                }
                for shipment in shipments
            ]
        }
        
        url = self.endpoints["shipments_tracking"]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            # ST23 returns 200 OK with response data
            return response.json()
