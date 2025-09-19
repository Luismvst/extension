"""
TIPSA carrier adapter.

This module implements the TipsaAdapter for interacting with
TIPSA carrier APIs for shipment creation and tracking.
"""

import httpx
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..interfaces.carrier import CarrierAdapter
from ...core.settings import settings
from ...core.logging import csv_logger, json_dumper


class TipsaAdapter(CarrierAdapter):
    """TIPSA carrier adapter implementation."""
    
    def __init__(self):
        """Initialize TIPSA adapter."""
        self.api_key = settings.tipsa_api_key
        self.base_url = settings.tipsa_base_url
        self.mock_mode = settings.tipsa_mock_mode
        
        # API endpoints
        self.endpoints = {
            "shipments": f"{self.base_url}/api/shipments",
            "shipment": f"{self.base_url}/api/shipments/{{shipment_id}}",
            "label": f"{self.base_url}/api/shipments/{{shipment_id}}/label",
            "cancel": f"{self.base_url}/api/shipments/{{shipment_id}}/cancel"
        }
    
    @property
    def carrier_name(self) -> str:
        """Get carrier name."""
        return "TIPSA"
    
    @property
    def carrier_code(self) -> str:
        """Get carrier code."""
        return "tipsa"
    
    @property
    def is_mock_mode(self) -> bool:
        """Check if adapter is in mock mode."""
        return self.mock_mode
    
    async def create_shipment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single shipment."""
        if self.mock_mode:
            return await self._create_shipment_mock(order_data)
        
        return await self._create_shipment_real(order_data)
    
    async def _create_shipment_mock(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation of create_shipment."""
        order_id = order_data.get("order_id", "UNKNOWN")
        weight = order_data.get("weight", 1.0)
        
        # Generate mock shipment data
        shipment_id = f"TIPSA-{order_id[-8:].upper()}{hash(order_id) % 10000:04d}"
        tracking_number = f"1Z{order_id[-8:].upper()}{hash(order_id) % 10000:04d}"
        
        result = {
            "shipment_id": shipment_id,
            "tracking_number": tracking_number,
            "status": "CREATED",
            "label_url": f"https://mock.tipsa.com/labels/{shipment_id}",
            "estimated_delivery": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "cost": 15.50 + (weight * 2.0),
            "currency": "EUR",
            "carrier": "TIPSA",
            "service": "STANDARD",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Log operation
        csv_logger.log_operation(
            operation="create_shipment",
            order_id=order_id,
            status="SUCCESS",
            details=f"Created shipment {shipment_id}",
            duration_ms=100
        )
        
        return result
    
    async def _create_shipment_real(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Real implementation of create_shipment."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Transform order data to TIPSA format
        shipment_data = self._transform_order_to_shipment(order_data)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoints["shipments"],
                headers=headers,
                json=shipment_data
            )
            response.raise_for_status()
            return response.json()
    
    async def create_shipments_bulk(self, orders_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple shipments in bulk."""
        if self.mock_mode:
            return await self._create_shipments_bulk_mock(orders_data)
        
        return await self._create_shipments_bulk_real(orders_data)
    
    async def _create_shipments_bulk_mock(self, orders_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock implementation of create_shipments_bulk."""
        shipments = []
        total_cost = 0.0
        
        for i, order_data in enumerate(orders_data):
            order_id = order_data.get("order_id", f"ORDER-{i}")
            weight = order_data.get("weight", 1.0)
            
            # Generate mock shipment data
            shipment_id = f"TIPSA-{order_id[-8:].upper()}{i+1:04d}"
            tracking_number = f"1Z{order_id[-8:].upper()}{i+1:04d}"
            cost = 15.50 + (weight * 2.0)
            
            shipment = {
                "order_id": order_id,
                "shipment_id": shipment_id,
                "tracking_number": tracking_number,
                "status": "CREATED",
                "label_url": f"https://mock.tipsa.com/labels/{shipment_id}",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                "cost": cost,
                "currency": "EUR",
                "carrier": "TIPSA",
                "service": "STANDARD",
                "created_at": datetime.utcnow().isoformat()
            }
            
            shipments.append(shipment)
            total_cost += cost
        
        result = {
            "shipments": shipments,
            "total_created": len(shipments),
            "total_failed": 0,
            "total_cost": total_cost,
            "currency": "EUR"
        }
        
        # Log operation
        csv_logger.log_operation(
            operation="create_shipments_bulk",
            order_id="",
            status="SUCCESS",
            details=f"Created {len(shipments)} shipments",
            duration_ms=200
        )
        
        return result
    
    async def _create_shipments_bulk_real(self, orders_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Real implementation of create_shipments_bulk."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Transform orders data to TIPSA format
        shipments_data = [self._transform_order_to_shipment(order) for order in orders_data]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoints['shipments']}/bulk",
                headers=headers,
                json={"shipments": shipments_data}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_shipment_status(self, shipment_id: str) -> Dict[str, Any]:
        """Get shipment status and tracking information."""
        if self.mock_mode:
            return await self._get_shipment_status_mock(shipment_id)
        
        return await self._get_shipment_status_real(shipment_id)
    
    async def _get_shipment_status_mock(self, shipment_id: str) -> Dict[str, Any]:
        """Mock implementation of get_shipment_status."""
        # Mock status progression
        statuses = ["CREATED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"]
        status_index = hash(shipment_id) % len(statuses)
        
        result = {
            "shipment_id": shipment_id,
            "tracking_number": f"1Z{shipment_id[-8:].upper()}",
            "status": statuses[status_index],
            "status_description": f"Package is {statuses[status_index].lower().replace('_', ' ')}",
            "estimated_delivery": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "last_update": datetime.utcnow().isoformat(),
            "carrier": "TIPSA",
            "service": "STANDARD"
        }
        
        # Log operation
        csv_logger.log_operation(
            operation="get_shipment_status",
            order_id=shipment_id,
            status="SUCCESS",
            details=f"Retrieved status: {result['status']}",
            duration_ms=50
        )
        
        return result
    
    async def _get_shipment_status_real(self, shipment_id: str) -> Dict[str, Any]:
        """Real implementation of get_shipment_status."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = self.endpoints["shipment"].format(shipment_id=shipment_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def get_shipment_label(self, shipment_id: str) -> bytes:
        """Get shipment label as PDF bytes."""
        if self.mock_mode:
            return await self._get_shipment_label_mock(shipment_id)
        
        return await self._get_shipment_label_real(shipment_id)
    
    async def _get_shipment_label_mock(self, shipment_id: str) -> bytes:
        """Mock implementation of get_shipment_label."""
        # Return mock PDF content (simplified)
        mock_pdf_content = f"""
        TIPSA SHIPPING LABEL
        Shipment ID: {shipment_id}
        Tracking: 1Z{shipment_id[-8:].upper()}
        Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        """.encode('utf-8')
        
        # Log operation
        csv_logger.log_operation(
            operation="get_shipment_label",
            order_id=shipment_id,
            status="SUCCESS",
            details="Generated mock label",
            duration_ms=30
        )
        
        return mock_pdf_content
    
    async def _get_shipment_label_real(self, shipment_id: str) -> bytes:
        """Real implementation of get_shipment_label."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/pdf"
        }
        
        url = self.endpoints["label"].format(shipment_id=shipment_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
    
    async def cancel_shipment(self, shipment_id: str, 
                            reason: str = None) -> Dict[str, Any]:
        """Cancel a shipment."""
        if self.mock_mode:
            return await self._cancel_shipment_mock(shipment_id, reason)
        
        return await self._cancel_shipment_real(shipment_id, reason)
    
    async def _cancel_shipment_mock(self, shipment_id: str, 
                                  reason: str = None) -> Dict[str, Any]:
        """Mock implementation of cancel_shipment."""
        result = {
            "success": True,
            "message": f"Shipment {shipment_id} cancelled successfully",
            "shipment_id": shipment_id,
            "status": "CANCELLED",
            "reason": reason or "Cancelled by user",
            "cancelled_at": datetime.utcnow().isoformat()
        }
        
        # Log operation
        csv_logger.log_operation(
            operation="cancel_shipment",
            order_id=shipment_id,
            status="SUCCESS",
            details=f"Cancelled: {reason or 'No reason provided'}",
            duration_ms=40
        )
        
        return result
    
    async def _cancel_shipment_real(self, shipment_id: str, 
                                  reason: str = None) -> Dict[str, Any]:
        """Real implementation of cancel_shipment."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {"reason": reason} if reason else {}
        
        url = self.endpoints["cancel"].format(shipment_id=shipment_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    
    def _transform_order_to_shipment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform order data to TIPSA shipment format."""
        return {
            "order_id": order_data.get("order_id"),
            "weight": order_data.get("weight", 1.0),
            "value": order_data.get("total_amount", 0.0),
            "currency": order_data.get("currency", "EUR"),
            "recipient": {
                "name": order_data.get("customer_name"),
                "email": order_data.get("customer_email"),
                "address": order_data.get("shipping_address", {})
            },
            "service": "STANDARD"
        }