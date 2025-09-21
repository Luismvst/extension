"""
Orchestrator API endpoints.

This module contains the main orchestration endpoints that coordinate
between marketplaces and carriers for the Mirakl-TIPSA Orchestrator.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import time
import json
from datetime import datetime

from ..adapters.marketplaces.mirakl import MiraklAdapter
from ..adapters.carriers.tipsa import TipsaAdapter
from ..adapters.carriers.ontime import OnTimeAdapter
from ..adapters.carriers.seur import SeurAdapter
from ..adapters.carriers.correosex import CorreosExAdapter
from ..adapters.carriers.dhl import DHLAdapter
from ..adapters.carriers.ups import UPSAdapter
from ..rules.selector import select_carrier, get_carrier_info
from ..core.auth import get_current_user
from ..core.logging import csv_logger, json_dumper
from ..core.unified_logger import unified_logger

# Create router
router = APIRouter(prefix="/api/v1/orchestrator", tags=["orchestrator"])

# Initialize adapters
mirakl_adapter = MiraklAdapter()
tipsa_adapter = TipsaAdapter()
ontime_adapter = OnTimeAdapter()
seur_adapter = SeurAdapter()
correosex_adapter = CorreosExAdapter()
dhl_adapter = DHLAdapter()
ups_adapter = UPSAdapter()

# Carrier mapping
CARRIER_ADAPTERS = {
    "tipsa": tipsa_adapter,
    "ontime": ontime_adapter,
    "seur": seur_adapter,
    "correosex": correosex_adapter,
    "dhl": dhl_adapter,
    "ups": ups_adapter
}


@router.post("/load-orders")
async def load_orders_and_create_shipments(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Load Mirakl orders and create shipments with appropriate carriers.
    
    This is the main orchestration endpoint that:
    1. Fetches orders from Mirakl
    2. Selects appropriate carrier for each order using rules engine
    3. Creates shipments with selected carriers
    4. Returns the results
    
    Args:
        current_user: Authenticated user (from JWT)
    
    Returns:
        Orchestration results with created shipments
    """
    start_time = time.time()
    
    try:
        # Step 1: Get orders from Mirakl
        mirakl_result = await mirakl_adapter.get_orders(status="PENDING", limit=100, offset=0) # TODO adaptar esto
        orders = mirakl_result.get("orders", [])
        
        if not orders:
            return {
                "success": True,
                "message": "No orders found to process",
                "orders_processed": 0,
                "shipments_created": 0,
                "shipments": [],
                "carrier_breakdown": {}
            }
        
        # Step 2: Group orders by selected carrier
        carriers_groups = {}
        for order in orders:
            carrier_code = select_carrier(order)
            carriers_groups.setdefault(carrier_code, []).append(order)
        
        # Step 3: Create shipments with each carrier
        all_shipments = []
        carrier_breakdown = {}
        
        for carrier_code, order_list in carriers_groups.items():
            if not order_list:
                continue
                
            try:
                adapter = CARRIER_ADAPTERS.get(carrier_code)
                if not adapter:
                    continue
                
                # Create shipments with this carrier
                result = await adapter.create_shipments_bulk(order_list)
                shipments = result.get("shipments", [])
                all_shipments.extend(shipments)
                
                # Track breakdown
                carrier_breakdown[carrier_code] = {
                    "orders": len(order_list),
                    "shipments": len(shipments),
                    "carrier_name": get_carrier_info(carrier_code)["name"]
                }
                
            except Exception as e:
                # Log error but continue with other carriers
                csv_logger.log_operation(
                    operation="create_shipments_bulk",
                    order_id="",
                    status="ERROR",
                    details=f"Error creating shipments for {carrier_code}: {e}",
                    duration_ms=0
                )
                carrier_breakdown[carrier_code] = {
                    "orders": len(order_list),
                    "shipments": 0,
                    "carrier_name": get_carrier_info(carrier_code)["name"],
                    "error": str(e)
                }
                continue
        
        # Step 4: Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        breakdown_str = ", ".join([f"{info['carrier_name']}:{info['shipments']}" 
                                 for info in carrier_breakdown.values() if info['shipments'] > 0])
        
        csv_logger.log_operation(
            operation="load_orders_and_create_shipments",
            order_id="",
            status="SUCCESS",
            details=f"Processed {len(orders)} orders, created {len(all_shipments)} shipments ({breakdown_str})",
            duration_ms=duration_ms
        )
        
        # Step 5: Dump request/response
        json_dumper.dump_request_response(
            operation="load_orders_and_create_shipments",
            order_id="",
            request_data={"orders_count": len(orders)},
            response_data={
                "orders_processed": len(orders),
                "shipments_created": len(all_shipments),
                "shipments": all_shipments,
                "carrier_breakdown": carrier_breakdown
            }
        )
        
        return {
            "success": True,
            "message": f"Successfully processed {len(orders)} orders and created {len(all_shipments)} shipments across carriers",
            "orders_processed": len(orders),
            "shipments_created": len(all_shipments),
            "shipments": all_shipments,
            "carrier_breakdown": carrier_breakdown
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="load_orders_and_create_shipments",
            order_id="",
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-tracking")
async def upload_tracking_to_mirakl(
    tracking_data: List[Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload tracking information to Mirakl using real tracking data.
    
    This endpoint:
    1. Receives list of tracking information from shipments
    2. Updates tracking in Mirakl for each order
    3. Updates order status to SHIPPED
    4. Returns the results
    
    Args:
        tracking_data: List of tracking information with order_id, tracking_number, carrier_code, carrier_name
        current_user: Authenticated user (from JWT)
    
    Returns:
        Tracking upload results
    """
    start_time = time.time()
    
    try:
        if not tracking_data:
            return {
                "success": True,
                "message": "No tracking data provided",
                "orders_updated": 0,
                "tracking_updates": []
            }
        
        # Process each tracking update
        tracking_updates = []
        orders_updated = 0
        
        for tracking_info in tracking_data:
            order_id = tracking_info.get("order_id")
            tracking_number = tracking_info.get("tracking_number")
            carrier_code = tracking_info.get("carrier_code")
            carrier_name = tracking_info.get("carrier_name")
            
            if not all([order_id, tracking_number, carrier_code, carrier_name]):
                tracking_updates.append({
                    "order_id": order_id,
                    "tracking_number": tracking_number,
                    "carrier_code": carrier_code,
                    "carrier_name": carrier_name,
                    "status": "ERROR",
                    "error": "Missing required fields"
                })
                continue
                
            try:
                # Update tracking in Mirakl
                await mirakl_adapter.update_order_tracking(
                    order_id, tracking_number, carrier_code, carrier_name
                )
                
                # Update order status to SHIPPED
                await mirakl_adapter.update_order_status(order_id, "SHIPPED")
                
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
                    "tracking_number": tracking_number,
                    "carrier_code": carrier_code,
                    "carrier_name": carrier_name,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="upload_tracking_to_mirakl",
            order_id="",
            status="SUCCESS",
            details=f"Updated tracking for {orders_updated} orders",
            duration_ms=duration_ms
        )
        
        # Dump request/response
        json_dumper.dump_request_response(
            operation="upload_tracking_to_mirakl",
            order_id="",
            request_data={"tracking_data": tracking_data},
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
        
        # Check all carriers status
        carriers_status = {}
        for carrier_code, adapter in CARRIER_ADAPTERS.items():
            carrier_info = get_carrier_info(carrier_code)
            carriers_status[carrier_code] = {
                "name": carrier_info["name"],
                "status": "healthy" if adapter.mock_mode else "unknown",
                "mode": "mock" if adapter.mock_mode else "real"
            }
        
        return {
            "status": "healthy",
            "mirakl": {
                "status": mirakl_status,
                "mode": "mock" if mirakl_adapter.is_mock_mode else "real"
            },
            "carriers": carriers_status,
            "rules_engine": {
                "status": "healthy",
                "supported_carriers": list(CARRIER_ADAPTERS.keys())
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-orders")
async def fetch_orders_from_mirakl(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Fetch orders from Mirakl and save to unified CSV.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Fetch results with orders saved to CSV
    """
    start_time = time.time()
    
    try:
        # Fetch orders from Mirakl
        mirakl_result = await mirakl_adapter.get_orders(status="PENDING", limit=100, offset=0)
        orders = mirakl_result.get("orders", [])
        
        if not orders:
            return {
                "success": True,
                "message": "No orders found to process",
                "orders_fetched": 0
            }
        
        # Save orders to unified CSV
        for order in orders:
            unified_logger.upsert_order({
                'mirakl_order_id': order.get('order_id'),
                'mirakl_status': order.get('status'),
                'mirakl_customer_name': order.get('customer_name'),
                'mirakl_customer_email': order.get('customer_email'),
                'mirakl_weight': order.get('weight'),
                'mirakl_total_amount': order.get('total_amount'),
                'mirakl_currency': order.get('currency'),
                'mirakl_created_at': order.get('created_at'),
                'mirakl_shipping_address': json.dumps(order.get('shipping_address', {})),
                'internal_state': 'PENDING_POST',
                'last_event': 'FETCHED_FROM_MIRAKL',
                'last_event_at': datetime.utcnow().isoformat()
            })
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="fetch_orders_from_mirakl",
            order_id="",
            status="SUCCESS",
            details=f"Fetched {len(orders)} orders from Mirakl",
            duration_ms=duration_ms
        )
        
        return {
            "success": True,
            "message": f"Successfully fetched {len(orders)} orders from Mirakl",
            "orders_fetched": len(orders),
            "orders": orders
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="fetch_orders_from_mirakl",
            order_id="",
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post-to-carrier")
async def post_to_carrier(
    carrier: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Post pending orders to specified carrier.
    
    Args:
        carrier: Carrier code
        current_user: Authenticated user
        
    Returns:
        Post results with created shipments
    """
    start_time = time.time()
    
    if carrier not in CARRIER_ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Unsupported carrier: {carrier}")
    
    try:
        # Get pending orders from unified CSV
        orders_result = unified_logger.get_orders(state="PENDING_POST", limit=50)
        orders = orders_result.get("orders", [])
        
        if not orders:
            return {
                "success": True,
                "message": "No pending orders found",
                "orders_processed": 0,
                "shipments_created": 0
            }
        
        # Transform to order format
        order_data = []
        for order in orders:
            order_data.append({
                "order_id": order.get("mirakl_order_id"),
                "customer_name": order.get("mirakl_customer_name"),
                "customer_email": order.get("mirakl_customer_email"),
                "weight": float(order.get("mirakl_weight", 0)),
                "total_amount": float(order.get("mirakl_total_amount", 0)),
                "currency": order.get("mirakl_currency", "EUR"),
                "shipping_address": json.loads(order.get("mirakl_shipping_address", "{}"))
            })
        
        # Create shipments with carrier
        adapter = CARRIER_ADAPTERS[carrier]
        result = await adapter.create_shipments_bulk(order_data)
        shipments = result.get("shipments", [])
        
        # Update orders in unified CSV
        for i, order in enumerate(orders):
            if i < len(shipments):
                shipment = shipments[i]
                unified_logger.upsert_order({
                    'mirakl_order_id': order.get('mirakl_order_id'),
                    'carrier_code': carrier,
                    'carrier_name': adapter.carrier_name,
                    'expedition_id': shipment.get('expedition_id'),
                    'tracking_number': shipment.get('tracking_number'),
                    'carrier_status': shipment.get('status'),
                    'label_url': shipment.get('label_url'),
                    'carrier_cost': shipment.get('cost'),
                    'carrier_created_at': shipment.get('created_at'),
                    'internal_state': 'POSTED',
                    'last_event': 'POSTED_TO_CARRIER',
                    'last_event_at': datetime.utcnow().isoformat()
                })
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="post_to_carrier",
            order_id="",
            status="SUCCESS",
            details=f"Posted {len(orders)} orders to {carrier}, created {len(shipments)} shipments",
            duration_ms=duration_ms
        )
        
        return {
            "success": True,
            "message": f"Successfully posted {len(orders)} orders to {carrier}",
            "orders_processed": len(orders),
            "shipments_created": len(shipments),
            "shipments": shipments
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="post_to_carrier",
            order_id="",
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push-tracking-to-mirakl")
async def push_tracking_to_mirakl(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Push tracking information to Mirakl for orders with tracking.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Push results with updated orders
    """
    start_time = time.time()
    
    try:
        # Get orders with tracking (AWAITING_TRACKING state)
        orders_result = unified_logger.get_orders(state="AWAITING_TRACKING", limit=50)
        orders = orders_result.get("orders", [])
        
        if not orders:
            return {
                "success": True,
                "message": "No orders with tracking found",
                "orders_updated": 0
            }
        
        # Update tracking in Mirakl
        updated_orders = 0
        for order in orders:
            try:
                order_id = order.get("mirakl_order_id")
                tracking_number = order.get("tracking_number")
                carrier_code = order.get("carrier_code")
                carrier_name = order.get("carrier_name")
                
                if not all([order_id, tracking_number, carrier_code, carrier_name]):
                    continue
                
                # Update tracking (OR23)
                await mirakl_adapter.update_order_tracking(
                    order_id, tracking_number, carrier_code, carrier_name
                )
                
                # Update order status to SHIPPED (OR24)
                await mirakl_adapter.update_order_ship(
                    order_id, carrier_code, carrier_name, tracking_number
                )
                
                # Update unified CSV
                unified_logger.upsert_order({
                    'mirakl_order_id': order_id,
                    'internal_state': 'MIRAKL_OK',
                    'last_event': 'TRACKING_PUSHED_TO_MIRAKL',
                    'last_event_at': datetime.utcnow().isoformat()
                })
                
                updated_orders += 1
                
            except Exception as e:
                # Log error but continue with other orders
                unified_logger.log_event(
                    order.get("mirakl_order_id"),
                    "FAILED_MIRAKL_UPDATE",
                    str(e)
                )
                continue
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="push_tracking_to_mirakl",
            order_id="",
            status="SUCCESS",
            details=f"Updated tracking for {updated_orders} orders in Mirakl",
            duration_ms=duration_ms
        )
        
        return {
            "success": True,
            "message": f"Successfully updated tracking for {updated_orders} orders in Mirakl",
            "orders_updated": updated_orders,
            "total_orders": len(orders)
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        csv_logger.log_operation(
            operation="push_tracking_to_mirakl",
            order_id="",
            status="ERROR",
            details=str(e),
            duration_ms=duration_ms
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders-view")
async def get_orders_view(
    state: str = None,
    carrier: str = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get unified orders view.
    
    Args:
        state: Filter by internal state
        carrier: Filter by carrier code
        limit: Maximum number of orders to return
        offset: Number of orders to skip
        current_user: Authenticated user
        
    Returns:
        Unified orders view with filtering and pagination
    """
    try:
        result = unified_logger.get_orders(
            state=state,
            carrier=carrier,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "orders": result.get("orders", []),
            "total": result.get("total", 0),
            "limit": limit,
            "offset": offset,
            "has_more": result.get("has_more", False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
