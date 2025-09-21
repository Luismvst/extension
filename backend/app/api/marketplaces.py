"""
Marketplace API endpoints.

This module contains all marketplace-related API endpoints
for the Mirakl-TIPSA Orchestrator.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import time

from ..adapters.marketplaces.mirakl import MiraklAdapter
from ..core.auth import get_current_user
from ..core.logging import csv_logger, json_dumper

# Create router
router = APIRouter(prefix="/api/v1/marketplaces", tags=["marketplaces"])

# Initialize adapter
mirakl_adapter = MiraklAdapter()


@router.get("/mirakl/orders")
async def get_mirakl_orders(
    status: str = "SHIPPING", # pendientes de aceptación -> TODO adaptar esto
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get orders from Mirakl marketplace.
    
    Args:
        status: Order status filter (default: SHIPPING)
        limit: Maximum number of orders to return (default: 100)
        offset: Number of orders to skip (default: 0)
        current_user: Authenticated user (from JWT)
    
    Returns:
        List of orders with metadata
    """
    start_time = time.time()
    
    try:
        # Get orders from Mirakl
        result = await mirakl_adapter.get_orders(status, limit, offset)
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="get_mirakl_orders",
            order_id="",
            status="SUCCESS",
            details=f"Retrieved {len(result.get('orders', []))} orders",
            duration_ms=duration_ms
        )
        
        return result
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="get_mirakl_orders",
            order_id="",
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mirakl/orders/{order_id}")
async def get_mirakl_order_details(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed information for a specific Mirakl order.
    
    Args:
        order_id: Order identifier
        current_user: Authenticated user (from JWT)
    
    Returns:
        Order details
    """
    start_time = time.time()
    
    try:
        # Get order details from Mirakl
        result = await mirakl_adapter.get_order_details(order_id)
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="get_mirakl_order_details",
            order_id=order_id,
            status="SUCCESS",
            details="Retrieved order details",
            duration_ms=duration_ms
        )
        
        return result
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="get_mirakl_order_details",
            order_id=order_id,
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/mirakl/orders/{order_id}/tracking")
async def update_mirakl_order_tracking(
    order_id: str,
    tracking_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update Mirakl order with tracking information.
    
    Args:
        order_id: Order identifier
        tracking_data: Tracking information (tracking_number, carrier_code, carrier_name)
        current_user: Authenticated user (from JWT)
    
    Returns:
        Update result
    """
    start_time = time.time()
    
    try:
        # Extract tracking data
        tracking_number = tracking_data.get("tracking_number")
        carrier_code = tracking_data.get("carrier_code")
        carrier_name = tracking_data.get("carrier_name")
        
        if not all([tracking_number, carrier_code, carrier_name]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: tracking_number, carrier_code, carrier_name"
            )
        
        # Update tracking in Mirakl
        result = await mirakl_adapter.update_order_tracking(
            order_id, tracking_number, carrier_code, carrier_name
        )
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="update_mirakl_order_tracking",
            order_id=order_id,
            status="SUCCESS",
            details=f"Updated tracking: {tracking_number}",
            duration_ms=duration_ms
        )
        
        # Dump request/response
        json_dumper.dump_request_response(
            operation="update_mirakl_order_tracking",
            order_id=order_id,
            request_data=tracking_data,
            response_data=result
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="update_mirakl_order_tracking",
            order_id=order_id,
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/mirakl/orders/{order_id}/status")
async def update_mirakl_order_status(
    order_id: str,
    status_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update Mirakl order status.
    
    Args:
        order_id: Order identifier
        status_data: Status information (status, reason)
        current_user: Authenticated user (from JWT)
    
    Returns:
        Update result
    """
    start_time = time.time()
    
    try:
        # Extract status data
        status = status_data.get("status")
        reason = status_data.get("reason")
        
        if not status:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: status"
            )
        
        # Update status in Mirakl
        result = await mirakl_adapter.update_order_status(order_id, status, reason)
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="update_mirakl_order_status",
            order_id=order_id,
            status="SUCCESS",
            details=f"Updated status to {status}",
            duration_ms=duration_ms
        )
        
        # Dump request/response
        json_dumper.dump_request_response(
            operation="update_mirakl_order_status",
            order_id=order_id,
            request_data=status_data,
            response_data=result
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="update_mirakl_order_status",
            order_id=order_id,
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))