"""
Carrier API endpoints.

This module contains REST endpoints for carrier operations including
shipment creation, status checking, and webhook handling.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Dict, Any, List, Optional
import time
import hashlib
import hmac
from datetime import datetime, timedelta

from ..adapters.carriers.tipsa import TipsaAdapter
from ..adapters.carriers.ontime import OnTimeAdapter
from ..adapters.carriers.seur import SeurAdapter
from ..adapters.carriers.correosex import CorreosExAdapter
from ..core.auth import get_current_user
from ..models.order import ShipmentRequest
import logging

# Create logger for this module
logger = logging.getLogger(__name__)
from ..core.settings import settings

# Create router
router = APIRouter(prefix="/api/v1/carriers", tags=["carriers"])

# Initialize adapters
tipsa_adapter = TipsaAdapter()
ontime_adapter = OnTimeAdapter()
seur_adapter = SeurAdapter()
correosex_adapter = CorreosExAdapter()

# Carrier mapping
CARRIER_ADAPTERS = {
    "tipsa": tipsa_adapter,
    "ontime": ontime_adapter,
    "seur": seur_adapter,
    "correosex": correosex_adapter
}

# Webhook secrets (in production, these should be in environment variables)
WEBHOOK_SECRETS = {
    "tipsa": "tipsa_webhook_secret_2025",
    "ontime": "ontime_webhook_secret_2025",
    "seur": "seur_webhook_secret_2025",
    "correosex": "correosex_webhook_secret_2025"
}


@router.post("/{carrier}/shipments")
async def create_shipments(
    carrier: str,
    request: ShipmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create shipments with specified carrier (batch).
    
    Args:
        carrier: Carrier code (tipsa, ontime, seur, correosex)
        request: Shipment request with orders and parameters
        current_user: Authenticated user
        
    Returns:
        Jobs array with expedition_id for each shipment
    """
    start_time = time.time()
    
    if carrier not in CARRIER_ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Unsupported carrier: {carrier}")
    
    adapter = CARRIER_ADAPTERS[carrier]
    
    try:
        # Create shipments with idempotency
        jobs = []
        for order in request.orders:
            try:
                # Convert OrderStandard to dict
                order_dict = order.dict()
                result = await adapter.create_shipment_with_idempotency(order_dict)
                jobs.append({
                    "order_id": order.order_id,
                    "expedition_id": result.get("expedition_id") if isinstance(result, dict) else getattr(result, "expedition_id", None),
                    "status": "CREATED",
                    "carrier": carrier,
                    "created_at": datetime.utcnow().isoformat()
                })
            except Exception as e:
                jobs.append({
                    "order_id": order.order_id,
                    "expedition_id": None,
                    "status": "ERROR",
                    "error": str(e),
                    "carrier": carrier,
                    "created_at": datetime.utcnow().isoformat()
                })
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        successful_jobs = [job for job in jobs if job["status"] == "CREATED"]
        
        logger.info(f"Created {len(successful_jobs)}/{len(jobs)} shipments with {carrier}, duration_ms={duration_ms}")
        
        return {
            "success": True,
            "carrier": carrier,
            "total_orders": len(request.orders),
            "successful_shipments": len(successful_jobs),
            "failed_shipments": len(jobs) - len(successful_jobs),
            "jobs": jobs
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Error creating shipments with {carrier}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{carrier}/shipments/{expedition_id}")
async def get_shipment_status(
    carrier: str,
    expedition_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get shipment status and label (fallback).
    
    Args:
        carrier: Carrier code
        expedition_id: Expedition/shipment ID
        current_user: Authenticated user
        
    Returns:
        Status data with tracking_number and label_url if available
    """
    if carrier not in CARRIER_ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Unsupported carrier: {carrier}")
    
    adapter = CARRIER_ADAPTERS[carrier]
    
    try:
        result = await adapter.get_shipment_status(expedition_id)
        
        logger.info(f"Retrieved shipment status for {expedition_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting shipment status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/{carrier}")
async def receive_webhook(
    carrier: str,
    request: Request,
    x_signature: Optional[str] = Header(None),
    x_timestamp: Optional[str] = Header(None)
):
    """
    Receive webhook events from carriers.
    
    Args:
        carrier: Carrier code
        request: FastAPI request object
        x_signature: X-Signature header for HMAC validation
        x_timestamp: X-Timestamp header for replay protection
        
    Returns:
        202 Accepted (always)
    """
    if carrier not in CARRIER_ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Unsupported carrier: {carrier}")
    
    adapter = CARRIER_ADAPTERS[carrier]
    secret = WEBHOOK_SECRETS.get(carrier)
    
    if not secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    try:
        # Get raw payload
        payload = await request.body()
        payload_str = payload.decode('utf-8')
        
        # Validate timestamp (reject if > 5 minutes old)
        if x_timestamp:
            try:
                timestamp = datetime.fromisoformat(x_timestamp.replace('Z', '+00:00'))
                if datetime.utcnow() - timestamp > timedelta(minutes=5):
                    raise HTTPException(status_code=400, detail="Webhook timestamp too old")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid timestamp format")
        
        # Validate signature
        if x_signature:
            if not adapter.validate_webhook_signature(payload_str, x_signature, secret):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse JSON payload
        import json
        event_data = json.loads(payload_str)
        
        # Process webhook event
        processed_event = adapter.process_webhook_event(event_data)
        
        # Log webhook reception
        logger.info(
            f"Processed {carrier} webhook: {processed_event.get('event_type', 'unknown')}"
        )
        
        # TODO: In production, this would trigger background processing
        # to update Mirakl with tracking information
        
        return {"status": "accepted", "carrier": carrier, "processed_at": datetime.utcnow().isoformat()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing {carrier} webhook: {str(e)}")
        # Always return 202 to prevent carrier retries
        return {"status": "accepted", "error": "Processing failed", "carrier": carrier}


@router.get("/{carrier}/health")
async def get_carrier_health(
    carrier: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get carrier health status.
    
    Args:
        carrier: Carrier code
        current_user: Authenticated user
        
    Returns:
        Carrier health information
    """
    if carrier not in CARRIER_ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Unsupported carrier: {carrier}")
    
    adapter = CARRIER_ADAPTERS[carrier]
    
    return {
        "carrier": carrier,
        "name": adapter.carrier_name,
        "status": "healthy" if adapter.is_mock_mode else "unknown",
        "mode": "mock" if adapter.is_mock_mode else "real",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health")
async def get_all_carriers_health(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get health status for all carriers.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Health status for all carriers
    """
    health_status = {}
    
    for carrier_code, adapter in CARRIER_ADAPTERS.items():
        health_status[carrier_code] = {
            "name": adapter.carrier_name,
            "status": "healthy" if adapter.is_mock_mode else "unknown",
            "mode": "mock" if adapter.is_mock_mode else "real"
        }
    
    return {
        "carriers": health_status,
        "timestamp": datetime.utcnow().isoformat()
    }
