"""
Orchestrator API endpoints.

This module contains the main orchestration endpoints that coordinate
between marketplaces and carriers for the Mirakl-TIPSA Orchestrator.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import time

from ..adapters.marketplaces.mirakl import MiraklAdapter
from ..adapters.carriers.tipsa import TipsaAdapter
from ..core.auth import get_current_user
from ..core.logging import csv_logger, json_dumper

# Create router
router = APIRouter(prefix="/api/v1/orchestrator", tags=["orchestrator"])

# Initialize adapters
mirakl_adapter = MiraklAdapter()
tipsa_adapter = TipsaAdapter()


@router.post("/load-orders")
async def load_orders_to_tipsa(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Load Mirakl orders and create TIPSA shipments.
    
    This is the main orchestration endpoint that:
    1. Fetches orders from Mirakl
    2. Creates shipments in TIPSA
    3. Returns the results
    
    Args:
        current_user: Authenticated user (from JWT)
    
    Returns:
        Orchestration results with created shipments
    """
    start_time = time.time()
    
    try:
        # Step 1: Get orders from Mirakl
        mirakl_result = await mirakl_adapter.get_orders(status="SHIPPING", limit=100, offset=0)
        orders = mirakl_result.get("orders", [])
        
        if not orders:
            return {
                "success": True,
                "message": "No orders found to process",
                "orders_processed": 0,
                "shipments_created": 0,
                "shipments": []
            }
        
        # Step 2: Create shipments in TIPSA
        tipsa_result = await tipsa_adapter.create_shipments_bulk(orders)
        shipments = tipsa_result.get("shipments", [])
        
        # Step 3: Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="load_orders_to_tipsa",
            order_id="",
            status="SUCCESS",
            details=f"Processed {len(orders)} orders, created {len(shipments)} shipments",
            duration_ms=duration_ms
        )
        
        # Step 4: Dump request/response
        json_dumper.dump_request_response(
            operation="load_orders_to_tipsa",
            order_id="",
            request_data={"orders_count": len(orders)},
            response_data={
                "orders_processed": len(orders),
                "shipments_created": len(shipments),
                "shipments": shipments
            }
        )
        
        return {
            "success": True,
            "message": f"Successfully processed {len(orders)} orders and created {len(shipments)} shipments",
            "orders_processed": len(orders),
            "shipments_created": len(shipments),
            "shipments": shipments
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="load_orders_to_tipsa",
            order_id="",
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-tracking")
async def upload_tracking_to_mirakl(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload TIPSA tracking information to Mirakl.
    
    This endpoint:
    1. Gets shipment statuses from TIPSA
    2. Updates tracking in Mirakl
    3. Returns the results
    
    Args:
        current_user: Authenticated user (from JWT)
    
    Returns:
        Tracking upload results
    """
    start_time = time.time()
    
    try:
        # Step 1: Get orders from Mirakl to find which ones need tracking updates
        mirakl_result = await mirakl_adapter.get_orders(status="SHIPPING", limit=100, offset=0)
        orders = mirakl_result.get("orders", [])
        
        if not orders:
            return {
                "success": True,
                "message": "No orders found to update tracking",
                "orders_updated": 0,
                "tracking_updates": []
            }
        
        # Step 2: For each order, get shipment status from TIPSA and update Mirakl
        tracking_updates = []
        orders_updated = 0
        
        for order in orders:
            order_id = order.get("order_id")
            if not order_id:
                continue
                
            try:
                # Get shipment status from TIPSA (mock: generate tracking number)
                tracking_number = f"1Z{order_id[-8:].upper()}{hash(order_id) % 10000:04d}"
                carrier_code = "tipsa"
                carrier_name = "TIPSA"
                
                # Update tracking in Mirakl
                mirakl_result = await mirakl_adapter.update_order_tracking(
                    order_id, tracking_number, carrier_code, carrier_name
                )
                
                tracking_updates.append({
                    "order_id": order_id,
                    "tracking_number": tracking_number,
                    "carrier_code": carrier_code,
                    "carrier_name": carrier_name,
                    "status": "SUCCESS"
                })
                orders_updated += 1
                
            except Exception as e:
                tracking_updates.append({
                    "order_id": order_id,
                    "tracking_number": None,
                    "carrier_code": None,
                    "carrier_name": None,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        # Step 3: Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="upload_tracking_to_mirakl",
            order_id="",
            status="SUCCESS",
            details=f"Updated tracking for {orders_updated} orders",
            duration_ms=duration_ms
        )
        
        # Step 4: Dump request/response
        json_dumper.dump_request_response(
            operation="upload_tracking_to_mirakl",
            order_id="",
            request_data={"orders_count": len(orders)},
            response_data={
                "orders_updated": orders_updated,
                "tracking_updates": tracking_updates
            }
        )
        
        return {
            "success": True,
            "message": f"Successfully updated tracking for {orders_updated} orders",
            "orders_updated": orders_updated,
            "tracking_updates": tracking_updates
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="upload_tracking_to_mirakl",
            order_id="",
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_orchestrator_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get orchestrator status and health.
    
    Args:
        current_user: Authenticated user (from JWT)
    
    Returns:
        Orchestrator status information
    """
    try:
        # Check Mirakl status
        mirakl_status = "healthy" if mirakl_adapter.is_mock_mode else "unknown"
        
        # Check TIPSA status
        tipsa_status = "healthy" if tipsa_adapter.is_mock_mode else "unknown"
        
        return {
            "status": "healthy",
            "mirakl": {
                "status": mirakl_status,
                "mode": "mock" if mirakl_adapter.is_mock_mode else "real"
            },
            "tipsa": {
                "status": tipsa_status,
                "mode": "mock" if tipsa_adapter.is_mock_mode else "real"
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
