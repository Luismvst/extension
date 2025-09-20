"""
Carrier API endpoints.

This module contains all carrier-related API endpoints
for the Mirakl-TIPSA Orchestrator.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import time

from ..adapters.carriers.tipsa import TipsaAdapter
from ..core.auth import get_current_user
from ..core.logging import csv_logger, json_dumper

# Create router
router = APIRouter(prefix="/api/v1/carriers", tags=["carriers"])

# Initialize adapter
tipsa_adapter = TipsaAdapter()


@router.post("/tipsa/shipments")
async def create_tipsa_shipment(
    order_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a single TIPSA shipment.
    
    Args:
        order_data: Order information
        current_user: Authenticated user (from JWT)
    
    Returns:
        Shipment details
    """
    start_time = time.time()
    
    try:
        # Create shipment in TIPSA
        result = await tipsa_adapter.create_shipment(order_data)
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="create_tipsa_shipment",
            order_id=order_data.get("order_id", "UNKNOWN"),
            status="SUCCESS",
            details=f"Created shipment {result.get('shipment_id')}",
            duration_ms=duration_ms
        )
        
        # Dump request/response
        json_dumper.dump_request_response(
            operation="create_tipsa_shipment",
            order_id=order_data.get("order_id", "UNKNOWN"),
            request_data=order_data,
            response_data=result
        )
        
        return result
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="create_tipsa_shipment",
            order_id=order_data.get("order_id", "UNKNOWN"),
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tipsa/shipments/bulk")
async def create_tipsa_shipments_bulk(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create multiple TIPSA shipments in bulk.
    
    Args:
        request_data: Request data containing shipments list
        current_user: Authenticated user (from JWT)
    
    Returns:
        Bulk shipment results
    """
    start_time = time.time()
    
    try:
        # Extract shipments from request data
        orders_data = request_data.get("shipments", [])
        
        # Create shipments in TIPSA
        result = await tipsa_adapter.create_shipments_bulk(orders_data)
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="create_tipsa_shipments_bulk",
            order_id="",
            status="SUCCESS",
            details=f"Created {result.get('total_created', 0)} shipments",
            duration_ms=duration_ms
        )
        
        # Dump request/response
        json_dumper.dump_request_response(
            operation="create_tipsa_shipments_bulk",
            order_id="",
            request_data=request_data,
            response_data=result
        )
        
        return result
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="create_tipsa_shipments_bulk",
            order_id="",
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tipsa/shipments/{shipment_id}")
async def get_tipsa_shipment_status(
    shipment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get TIPSA shipment status and tracking information.
    
    Args:
        shipment_id: Shipment identifier
        current_user: Authenticated user (from JWT)
    
    Returns:
        Shipment status and tracking info
    """
    start_time = time.time()
    
    try:
        # Get shipment status from TIPSA
        result = await tipsa_adapter.get_shipment_status(shipment_id)
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="get_tipsa_shipment_status",
            order_id=shipment_id,
            status="SUCCESS",
            details=f"Retrieved status: {result.get('status')}",
            duration_ms=duration_ms
        )
        
        return result
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="get_tipsa_shipment_status",
            order_id=shipment_id,
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tipsa/shipments/{shipment_id}/label")
async def get_tipsa_shipment_label(
    shipment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get TIPSA shipment label as PDF.
    
    Args:
        shipment_id: Shipment identifier
        current_user: Authenticated user (from JWT)
    
    Returns:
        Label PDF content
    """
    start_time = time.time()
    
    try:
        # Get shipment label from TIPSA
        label_content = await tipsa_adapter.get_shipment_label(shipment_id)
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="get_tipsa_shipment_label",
            order_id=shipment_id,
            status="SUCCESS",
            details="Retrieved label",
            duration_ms=duration_ms
        )
        
        return {"content": label_content.decode('utf-8')}
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="get_tipsa_shipment_label",
            order_id=shipment_id,
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tipsa/shipments/{shipment_id}/cancel")
async def cancel_tipsa_shipment(
    shipment_id: str,
    cancel_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Cancel a TIPSA shipment.
    
    Args:
        shipment_id: Shipment identifier
        cancel_data: Cancellation information (reason)
        current_user: Authenticated user (from JWT)
    
    Returns:
        Cancellation result
    """
    start_time = time.time()
    
    try:
        # Extract cancellation data
        reason = cancel_data.get("reason")
        
        # Cancel shipment in TIPSA
        result = await tipsa_adapter.cancel_shipment(shipment_id, reason)
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="cancel_tipsa_shipment",
            order_id=shipment_id,
            status="SUCCESS",
            details=f"Cancelled: {reason or 'No reason provided'}",
            duration_ms=duration_ms
        )
        
        # Dump request/response
        json_dumper.dump_request_response(
            operation="cancel_tipsa_shipment",
            order_id=shipment_id,
            request_data=cancel_data,
            response_data=result
        )
        
        return result
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="cancel_tipsa_shipment",
            order_id=shipment_id,
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))