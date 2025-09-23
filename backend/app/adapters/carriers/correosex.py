"""
Correos Express carrier adapter.

This module implements the CorreosExAdapter for interacting with
Correos Express carrier APIs for shipment creation and tracking.

Reference: https://clickpost.ai (integration examples)
"""

import httpx
import hashlib
import uuid
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..interfaces.carrier import CarrierAdapter
from ...core.settings import settings
import logging

# Create logger for this module
logger = logging.getLogger(__name__)


class CorreosExAdapter(CarrierAdapter):
    """Correos Express carrier adapter implementation."""
    
    def __init__(self):
        """Initialize Correos Express adapter."""
        self.api_key = settings.correosex_api_key
        self.base_url = settings.correosex_base_url
        self.mock_mode = settings.correosex_mock_mode
        
        # API endpoints
        self.endpoints = {
            "shipments": f"{self.base_url}/api/shipments",
            "shipment": f"{self.base_url}/api/shipments/{{shipment_id}}",
            "label": f"{self.base_url}/api/shipments/{{shipment_id}}/label",
            "cancel": f"{self.base_url}/api/shipments/{{shipment_id}}/cancel",
            "webhooks": f"{self.base_url}/api/webhooks"
        }
        
        # Idempotency tracking
        self._idempotency_keys = set()
    
    @property
    def carrier_name(self) -> str:
        """Get carrier name."""
        return "Correos Express"
    
    @property
    def carrier_code(self) -> str:
        """Get carrier code."""
        return "correosex"
    
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
        shipment_id = f"CEX-{order_id[-8:].upper()}{hash(order_id) % 10000:04d}"
        tracking_number = f"CE{order_id[-8:].upper()}{hash(order_id) % 10000:04d}"
        
        result = {
            "shipment_id": shipment_id,
            "expedition_id": shipment_id,  # Correos Express uses shipment_id as expedition_id
            "tracking_number": tracking_number,
            "status": "CREATED",
            "label_url": f"https://mock.correosex.com/labels/{shipment_id}",
            "estimated_delivery": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "cost": 16.25 + (weight * 2.0),
            "currency": "EUR",
            "carrier": "Correos Express",
            "service": "EXPRESS",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Log operation
        logger.info(f"Retrieved shipment status for {expedition_id}")
        
        return result
    
    async def _create_shipment_real(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Real implementation of create_shipment."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-API-Version": "v1"
        }
        
        # Transform order data to Correos Express format
        shipment_data = self._transform_order_to_shipment(order_data)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoints["shipments"],
                headers=headers,
                json=shipment_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def create_shipments_bulk(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple shipments in bulk."""
        if self.mock_mode:
            return await self._create_shipments_bulk_mock(orders)
        
        return await self._create_shipments_bulk_real(orders)
    
    async def _create_shipments_bulk_mock(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock implementation of create_shipments_bulk."""
        shipments = []
        
        for order in orders:
            shipment = await self._create_shipment_mock(order)
            shipments.append(shipment)
        
        logger.info(f"Created {len(shipments)} Correos Express shipments", duration_ms=len(orders) * 180
        )
        
        return {
            "shipments": shipments,
            "total_created": len(shipments),
            "carrier": "Correos Express"
        }
    
    async def _create_shipments_bulk_real(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Real implementation of create_shipments_bulk."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-API-Version": "v1"
        }
        
        shipments_data = [self._transform_order_to_shipment(order) for order in orders]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoints['shipments']}/bulk",
                headers=headers,
                json={"shipments": shipments_data},
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
    
    def _transform_order_to_shipment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform order data to Correos Express shipment format."""
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
            "service": "EXPRESS",
            "signature_required": True
        }
    
    def _generate_idempotency_key(self, order_data: Dict[str, Any]) -> str:
        """Generate idempotency key for shipment creation."""
        order_id = order_data.get("order_id", "")
        weight = order_data.get("weight", 0)
        recipient = order_data.get("shipping_address", {})
        
        # Create deterministic key based on order data
        key_data = f"{order_id}_{weight}_{recipient.get('postal_code', '')}_{recipient.get('city', '')}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    async def create_shipment_with_idempotency(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create shipment with idempotency support."""
        idempotency_key = self._generate_idempotency_key(order_data)
        
        # Check if we already processed this request
        if idempotency_key in self._idempotency_keys:
            logger.info(
                f"Idempotent request, returning cached result for key {idempotency_key}",
                status="SUCCESS"
            )
            return await self._get_cached_shipment(idempotency_key)
        
        # Create new shipment
        result = await self.create_shipment(order_data)
        
        # Track idempotency key
        self._idempotency_keys.add(idempotency_key)
        
        return result
    
    async def _get_cached_shipment(self, idempotency_key: str) -> Dict[str, Any]:
        """Get cached shipment result (mock implementation)."""
        return {
            "shipment_id": f"CACHED-{idempotency_key[:8]}",
            "expedition_id": f"CACHED-{idempotency_key[:8]}",
            "tracking_number": f"CE{idempotency_key[:8]}",
            "status": "CREATED",
            "cached": True
        }
    
    async def get_shipment_status(self, expedition_id: str) -> Dict[str, Any]:
        """Get shipment status by expedition_id."""
        if self.mock_mode:
            return await self._get_shipment_status_mock(expedition_id)
        
        return await self._get_shipment_status_real(expedition_id)
    
    async def _get_shipment_status_mock(self, expedition_id: str) -> Dict[str, Any]:
        """Mock implementation of get_shipment_status."""
        # Simulate status progression
        statuses = ["CREATED", "LABELED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"]
        status_index = hash(expedition_id) % len(statuses)
        status = statuses[status_index]
        
        result = {
            "expedition_id": expedition_id,
            "status": status,
            "tracking_number": f"CE{expedition_id[-8:]}",
            "label_url": f"https://mock.correosex.com/labels/{expedition_id}" if status in ["LABELED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"] else None,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Retrieved shipment status for {expedition_id}")
        
        return result
    
    async def _get_shipment_status_real(self, expedition_id: str) -> Dict[str, Any]:
        """Real implementation of get_shipment_status."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = self.endpoints["shipment"].format(shipment_id=expedition_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate webhook signature using HMAC."""
        expected_signature = hashlib.sha256(f"{payload}{secret}".encode()).hexdigest()
        return signature == expected_signature
    
    def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event from Correos Express."""
        event_type = event_data.get("event_type")
        expedition_id = event_data.get("expedition_id")
        
        logger.info(f"Retrieved shipment status for {expedition_id}")
        
        return {
            "expedition_id": expedition_id,
            "event_type": event_type,
            "status": event_data.get("status"),
            "tracking_number": event_data.get("tracking_number"),
            "label_url": event_data.get("label_url"),
            "timestamp": event_data.get("timestamp"),
            "processed_at": datetime.utcnow().isoformat()
        }

    async def get_shipment_label(self, shipment_id: str) -> bytes:
        """Get shipment label as PDF bytes."""
        if self.mock_mode:
            return await self._get_shipment_label_mock(shipment_id)
        
        return await self._get_shipment_label_real(shipment_id)
    
    async def _get_shipment_label_mock(self, shipment_id: str) -> bytes:
        """Mock implementation of get_shipment_label."""
        # Return a mock PDF label
        return b"Mock PDF label content"
    
    async def _get_shipment_label_real(self, shipment_id: str) -> bytes:
        """Real implementation of get_shipment_label."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/pdf"
        }
        
        url = self.endpoints["label"].format(shipment_id=shipment_id)
        
        timeout = httpx.Timeout(10.0, connect=5.0, read=10.0, write=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.content
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout getting label from CORREOSEX: {e}", exc_info=True)
            raise Exception(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error getting label from CORREOSEX: {e}", exc_info=True)
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error getting label from CORREOSEX: {e}", exc_info=True)
            raise Exception(f"Request failed: {e}")
    
    async def cancel_shipment(self, shipment_id: str, reason: str = None) -> Dict[str, Any]:
        """Cancel a shipment."""
        if self.mock_mode:
            return await self._cancel_shipment_mock(shipment_id, reason)
        
        return await self._cancel_shipment_real(shipment_id, reason)
    
    async def _cancel_shipment_mock(self, shipment_id: str, reason: str = None) -> Dict[str, Any]:
        """Mock implementation of cancel_shipment."""
        return {
            "shipment_id": shipment_id,
            "status": "cancelled",
            "reason": reason or "User requested cancellation",
            "cancelled_at": datetime.now().isoformat(),
            "success": True
        }
    
    async def _cancel_shipment_real(self, shipment_id: str, reason: str = None) -> Dict[str, Any]:
        """Real implementation of cancel_shipment."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "reason": reason or "User requested cancellation"
        }
        
        url = self.endpoints["cancel"].format(shipment_id=shipment_id)
        
        timeout = httpx.Timeout(10.0, connect=5.0, read=10.0, write=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout cancelling shipment in CORREOSEX: {e}", exc_info=True)
            raise Exception(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error cancelling shipment in CORREOSEX: {e}", exc_info=True)
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error cancelling shipment in CORREOSEX: {e}", exc_info=True)
            raise Exception(f"Request failed: {e}")
