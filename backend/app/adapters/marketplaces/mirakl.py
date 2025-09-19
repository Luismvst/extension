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
from ...core.logging import csv_logger, json_dumper


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
            "status": f"{self.base_url}/api/orders/{{order_id}}/status"
        }
    
    @property
    def marketplace_name(self) -> str:
        """Get marketplace name."""
        return "mirakl"
    
    @property
    def is_mock_mode(self) -> bool:
        """Check if adapter is in mock mode."""
        return self.mock_mode
    
    async def get_orders(self, status: str = "SHIPPING", 
                        limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get orders from Mirakl (OR12)."""
        if self.mock_mode:
            return await self._get_orders_mock(status, limit, offset)
        
        return await self._get_orders_real(status, limit, offset)
    
    async def _get_orders_mock(self, status: str, limit: int, offset: int) -> Dict[str, Any]:
        """Mock implementation of get_orders."""
        # Mock orders data
        mock_orders = [
            {
                "order_id": "MIR-001",
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
                }
            },
            {
                "order_id": "MIR-002",
                "marketplace": "mirakl",
                "status": "SHIPPING",
                "customer_name": "María García",
                "customer_email": "maria.garcia@email.com",
                "weight": 1.8,
                "total_amount": 32.50,
                "currency": "EUR",
                "created_at": "2025-09-19T21:00:00Z",
                "shipping_address": {
                    "name": "María García",
                    "street": "Avenida de la Paz 456",
                    "city": "Barcelona",
                    "postal_code": "08001",
                    "country": "ES"
                }
            }
        ]
        
        # Filter by status
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
        csv_logger.log_operation(
            operation="get_orders",
            order_id="",
            status="SUCCESS",
            details=f"Retrieved {len(paginated_orders)} orders",
            duration_ms=50
        )
        
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
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.endpoints["orders"],
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
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
        csv_logger.log_operation(
            operation="get_order_details",
            order_id=order_id,
            status="SUCCESS",
            details="Retrieved order details",
            duration_ms=30
        )
        
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
        csv_logger.log_operation(
            operation="update_order_tracking",
            order_id=order_id,
            status="SUCCESS",
            details=f"Updated tracking: {tracking_number}",
            duration_ms=40
        )
        
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
        csv_logger.log_operation(
            operation="update_order_status",
            order_id=order_id,
            status="SUCCESS",
            details=f"Updated status to {status}",
            duration_ms=35
        )
        
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