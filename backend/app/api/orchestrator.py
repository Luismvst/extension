"""
Orchestrator API endpoints.

This module contains the main orchestration endpoints that coordinate
between marketplaces and carriers for the Mirakl-TIPSA Orchestrator.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
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
from ..adapters.carriers.gls import GlsAdapter
from ..rules.selector import select_carrier, get_carrier_info
from ..core.auth import get_current_user
from ..utils.csv_ops_logger import csv_ops_logger
from ..core.unified_order_logger import unified_order_logger
from ..services.gls_tracking_poller import gls_tracking_poller
import logging

# Create logger for this module
logger = logging.getLogger(__name__)

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
gls_adapter = GlsAdapter()

# Carrier mapping
CARRIER_ADAPTERS = {
    "tipsa": tipsa_adapter,
    "ontime": ontime_adapter,
    "seur": seur_adapter,
    "correosex": correosex_adapter,
    "dhl": dhl_adapter,
    "ups": ups_adapter,
    "gls": gls_adapter
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
        mirakl_result = await mirakl_adapter.get_orders(order_state_codes="SHIPPING", limit=100, offset=0) # TODO adaptar esto
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
                logger.error(f"Error creating shipments for carrier {carrier_code}: {e}")
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
        
        logger.info(f"load_orders_and_create_shipments: Processed {len(orders)} orders, created {len(all_shipments)} shipments ({breakdown_str})")
        
        # Step 5: Dump request/response (disabled for now)
        # # json_dumper.dump_request_response(
        #     operation="load_orders_and_create_shipments",
        #     order_id="",
        #     request_data={"orders_count": len(orders)},
        #     response_data={
        #         "orders_processed": len(orders),
        #         "shipments_created": len(all_shipments),
        #         "shipments": all_shipments,
        #         "carrier_breakdown": carrier_breakdown
        #     }
        # )
        
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
        logger.error(f"load_orders_and_create_shipments: Error - {str(e)}")
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
        logger.info(f"upload_tracking_to_mirakl: SUCCESS, Updated tracking for {orders_updated} orders, duration_ms={duration_ms}")
        
        # Dump request/response
        # json_dumper.dump_request_response(
        #     operation="upload_tracking_to_mirakl",
        #     order_id="",
        #     request_data={"tracking_data": tracking_data},
        #     response_data={
        #         "orders_updated": orders_updated,
        #         "tracking_updates": tracking_updates
        #     }
        # )
        
        return {
            "success": True,
            "message": f"Successfully updated tracking for {orders_updated} orders",
            "orders_updated": orders_updated,
            "tracking_updates": tracking_updates
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"upload_tracking_to_mirakl: ERROR, {str(e)}, duration_ms={duration_ms}")
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
        
        # Save orders to unified CSV and log operations
        for order in orders:
            order_id = order.get('order_id')
            
            # Save to unified order logger
            unified_order_logger.upsert_order(order_id, {
                'marketplace': 'mirakl',
                'buyer_email': order.get('customer_email'),
                'buyer_name': order.get('customer_name'),
                'total_amount': order.get('total_amount'),
                'currency': order.get('currency'),
                'shipping_address': json.dumps(order.get('shipping_address', {})),
                'internal_state': 'PENDING_POST',
                'created_at': order.get('created_at'),
                'updated_at': datetime.utcnow().isoformat(),
                'reference': order_id,
                'consignee_name': order.get('customer_name'),
                'consignee_address': json.dumps(order.get('shipping_address', {})),
                'weight_kg': order.get('weight'),
                'order_date': order.get('created_at'),
                'client_name': order.get('customer_name'),
                'destination_email': order.get('customer_email')
            })
            
            # Log individual order fetch operation
            try:
                await csv_ops_logger.log(
                    scope="mirakl",
                    action="fetch_order",
                    order_id=order_id,
                    marketplace="mirakl",
                    status="OK",
                    message=f"Order {order_id} fetched from Mirakl",
                    meta={"order_data": order}
                )
                logger.debug(f"Individual order {order_id} logged successfully")
            except Exception as e:
                logger.error(f"Individual order {order_id} logging failed: {e}", exc_info=True)
                raise
        
        # Log overall operation
        duration_ms = int((time.time() - start_time) * 1000)
        try:
            await csv_ops_logger.log(
                scope="orchestrator",
                action="fetch_orders_from_mirakl",
                marketplace="mirakl",
                status="OK",
                message=f"Fetched {len(orders)} orders from Mirakl",
                duration_ms=duration_ms,
                meta={"orders_count": len(orders)}
            )
            logger.debug("CSV operations logger completed successfully")
        except Exception as e:
            logger.error(f"CSV operations logging failed: {e}", exc_info=True)
            raise
        
        logger.info(f"fetch_orders_from_mirakl: SUCCESS, Fetched {len(orders)} orders from Mirakl, duration_ms={duration_ms}")
        
        return {
            "success": True,
            "message": f"Successfully fetched {len(orders)} orders from Mirakl",
            "orders_fetched": len(orders),
            "orders": orders
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"fetch_orders_from_mirakl: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-marketplace")
async def refresh_marketplace(
    marketplace: str = "mirakl",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Refresh orders from marketplace and update local storage.
    
    Args:
        marketplace: Marketplace name (default: mirakl)
        current_user: Authenticated user
        
    Returns:
        Refresh results with updated order count
    """
    start_time = time.time()
    
    if marketplace.lower() != "mirakl":
        raise HTTPException(status_code=400, detail=f"Only Mirakl marketplace is currently supported")
    
    try:
        # Import order storage service
        from ..services.order_storage import order_storage_service
        from ..models.order import OrderStandard
        
        # Fetch orders from Mirakl
        logger.info(f"refresh_marketplace: Fetching orders from {marketplace}")
        orders_data = await mirakl_adapter.get_orders(status="SHIPPED")
        
        if not orders_data or not orders_data.get("orders"):
            return {
                "success": True,
                "message": "No orders found in marketplace",
                "orders_processed": 0,
                "orders_updated": 0
            }
        
        orders = orders_data["orders"]
        processed_count = 0
        updated_count = 0
        
        # Process each order
        for order_data in orders:
            try:
                # Data is already in standard format from mock
                standard_order = OrderStandard(**order_data)
                
                # Add to storage (will update if exists)
                order_storage_service.store_order(standard_order)
                updated_count += 1
                processed_count += 1
                
            except Exception as e:
                logger.warning(f"refresh_marketplace: Error processing order {order_data.get('order_id', 'unknown')}: {str(e)}")
                continue
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        await csv_ops_logger.log(
            scope="orchestrator",
            action="refresh_marketplace",
            marketplace=marketplace,
            status="OK",
            message=f"Refreshed {processed_count} orders from {marketplace}",
            duration_ms=duration_ms,
            meta={"orders_processed": processed_count, "orders_updated": updated_count}
        )
        
        logger.info(f"refresh_marketplace: Refreshed {processed_count} orders from {marketplace}")
        
        return {
            "success": True,
            "message": f"Successfully refreshed {processed_count} orders from {marketplace}",
            "orders_processed": processed_count,
            "orders_updated": updated_count,
            "duration_ms": duration_ms
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"refresh_marketplace: Error - {str(e)}")
        
        await csv_ops_logger.log(
            scope="orchestrator",
            action="refresh_marketplace",
            marketplace=marketplace,
            status="ERROR",
            message=f"Error refreshing marketplace: {str(e)}",
            duration_ms=duration_ms
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post-to-carrier")
async def post_to_carrier(
    carrier: str,
    order_ids: List[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Post selected orders to specified carrier.
    
    Args:
        carrier: Carrier code
        order_ids: List of order IDs to send (optional, sends all pending if not provided)
        current_user: Authenticated user
        
    Returns:
        Post results with created shipments
    """
    start_time = time.time()
    
    if carrier not in CARRIER_ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Unsupported carrier: {carrier}")
    
    try:
        # Import order storage service
        from ..services.order_storage import order_storage_service
        
        # Get orders from storage
        if order_ids:
            # Get specific orders
            orders = []
            for order_id in order_ids:
                order = order_storage_service.get_order(order_id)
                if order and order.estado_tipsa == 'PENDING':
                    orders.append(order)
        else:
            # Get all pending orders
            orders = order_storage_service.get_orders_by_status(estado_tipsa='PENDING')
            # Apply limit
            orders = orders[:50]
        
        if not orders:
            return {
                "success": True,
                "message": "No pending orders found",
                "orders_processed": 0,
                "shipments_created": 0
            }
        
        # Transform to order format for carrier
        order_data = []
        for order_storage in orders:
            order = order_storage.order_data
            order_data.append({
                "order_id": order.order_id,
                "customer_name": order.recipient_name,
                "customer_email": order.recipient_email,
                "weight": float(order.weight_kg or 0.1),
                "total_amount": float(order.cash_on_delivery or 0),
                "currency": "EUR",
                "shipping_address": {
                    "name": order.recipient_name,
                    "address1": order.recipient_address,
                    "address2": "",
                    "city": order.recipient_city,
                    "state": "",
                    "postal_code": order.recipient_postal_code,
                    "country": order.recipient_country
                }
            })
        
        # Create shipments with carrier
        adapter = CARRIER_ADAPTERS[carrier]
        result = await adapter.create_shipments_bulk(order_data)
        shipments = result.get("shipments", [])
        
        # Update orders in storage and log operations
        for i, order_storage in enumerate(orders):
            if i < len(shipments):
                shipment = shipments[i]
                order_id = order_storage.order_id
                
                # Update order status in storage
                from ..models.order import OrderUpdateRequest
                update_data = OrderUpdateRequest(
                    order_id=order_id,
                    estado_tipsa='SENT',
                    tracking_number=shipment.get('tracking_number'),
                    carrier_code=carrier,
                    carrier_name=adapter.carrier_name,
                    synced_to_carrier=True
                )
                order_storage_service.update_order_status(order_id, update_data)
                
                # Log individual shipment creation
                await csv_ops_logger.log(
                    scope="carrier",
                    action="create_shipment",
                    order_id=order_id,
                    carrier=carrier,
                    status="OK",
                    message=f"Shipment created for order {order_id}",
                    meta={"shipment_data": shipment}
                )
        
        # Log overall operation
        duration_ms = int((time.time() - start_time) * 1000)
        await csv_ops_logger.log(
            scope="orchestrator",
            action="post_to_carrier",
            carrier=carrier,
            status="OK",
            message=f"Posted {len(orders)} orders to {carrier}, created {len(shipments)} shipments",
            duration_ms=duration_ms,
            meta={"orders_count": len(orders), "shipments_count": len(shipments)}
        )
        
        logger.info(f"post_to_carrier: Posted {len(orders)} orders to {carrier}, created {len(shipments)} shipments")
        
        return {
            "success": True,
            "message": f"Successfully posted {len(orders)} orders to {carrier}",
            "orders_processed": len(orders),
            "shipments_created": len(shipments),
            "shipments": shipments
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"post_to_carrier operation failed: {str(e)}")
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
        orders = unified_order_logger.get_orders_by_state("AWAITING_TRACKING")
        
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
                unified_order_logger.upsert_order(order_id, {
                    'internal_state': 'MIRAKL_OK',
                    'last_event': 'TRACKING_PUSHED_TO_MIRAKL',
                    'last_event_at': datetime.utcnow().isoformat()
                })
                
                updated_orders += 1
                
            except Exception as e:
                # Log error but continue with other orders
                await csv_ops_logger.log(
                    scope="orchestrator",
                    action="push_tracking_to_mirakl",
                    order_id=order.get("mirakl_order_id"),
                    status="ERROR",
                    message=f"Failed to update Mirakl: {str(e)}"
                )
                continue
        
        # Log operation
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"push_tracking_to_mirakl: Updated tracking for {updated_orders} orders in Mirakl")
        
        return {
            "success": True,
            "message": f"Successfully updated tracking for {updated_orders} orders in Mirakl",
            "orders_updated": updated_orders,
            "total_orders": len(orders)
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"push_tracking_to_mirakl operation failed: {str(e)}")
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
        # Get all orders and filter manually for now
        all_orders = unified_order_logger.get_all_orders()
        
        # Apply filters
        filtered_orders = all_orders
        if state:
            filtered_orders = [order for order in filtered_orders if order.get('internal_state') == state]
        if carrier:
            filtered_orders = [order for order in filtered_orders if order.get('carrier_code') == carrier]
        
        # Apply pagination
        total = len(filtered_orders)
        start = offset
        end = offset + limit
        paginated_orders = filtered_orders[start:end]
        
        result = {
            "orders": paginated_orders,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": end < total
        }
        
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


@router.post("/test-correosex-shipment")
async def test_correosex_shipment(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a test shipment with Correos Express API.
    
    This endpoint creates a fictional order to test the Correos Express integration
    with OAuth 2.0 authentication.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Shipment creation result
    """
    start_time = time.time()
    
    # Create a fictional order for testing
    test_order = {
        "order_id": f"TEST-CORREOS-{int(time.time())}",
        "customer_name": "Juan Pérez García",
        "customer_email": "juan.perez@example.com",
        "customer_phone": "+34612345678",
        "total_amount": 45.99,
        "currency": "EUR",
        "weight": 2.5,
        "shipping_address": {
            "name": "Juan Pérez García",
            "street": "Calle Mayor 123, 2º B",
            "city": "Madrid",
            "postal_code": "28001",
            "province": "Madrid",
            "country": "ES",
            "phone": "+34612345678",
            "email": "juan.perez@example.com"
        },
        "observations": "Pedido de prueba - Correos Express API"
    }
    
    try:
        # Create shipment with Correos Express
        result = await correosex_adapter.create_shipment(test_order)
        
        # Log the operation
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Test shipment created with Correos Express, duration_ms={duration_ms}")
        
        return {
            "success": True,
            "message": "Test shipment created successfully",
            "order_id": test_order["order_id"],
            "shipment": result,
            "carrier": "correosex",
            "duration_ms": duration_ms,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Error creating test shipment with Correos Express: {str(e)}")
        
        return {
            "success": False,
            "message": f"Error creating test shipment: {str(e)}",
            "order_id": test_order["order_id"],
            "carrier": "correosex",
            "duration_ms": duration_ms,
            "error": str(e),
            "created_at": datetime.utcnow().isoformat()
        }


def _order_to_gls_payload(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intenta mapear tanto el mock de Mirakl (OrderStandard)
    como una respuesta real simplificada a lo que espera GlsAdapter.create_shipment.
    """
    # intentamos campos "standard"
    order_id = order.get("order_id") or order.get("id") or order.get("Referencia")
    customer_name = order.get("customer_name") or order.get("recipient_name") or order.get("Nombre Consignatario")
    customer_email = order.get("customer_email") or order.get("recipient_email") or order.get("Email Destino")
    weight = (
        order.get("weight")
        or order.get("weight_kg")
        or order.get("Kilos")
        or 0.5
    )
    cod_amount = (
        order.get("cash_on_delivery")
        or order.get("Reembolso")
        or 0.0
    )
    currency = order.get("currency") or "EUR"

    addr = order.get("shipping_address") or {}
    if not addr and all(order.get(k) for k in ["recipient_address","recipient_city","recipient_postal_code","recipient_country"]):
        # OrderStandard mock
        addr = {
            "address1": order.get("recipient_address"),
            "city": order.get("recipient_city"),
            "postal_code": order.get("recipient_postal_code"),
            "country": order.get("recipient_country"),
            "name": order.get("recipient_name"),
            "phone": order.get("recipient_phone"),
            "email": order.get("recipient_email"),
        }

    payload = {
        "order_id": str(order_id),
        "customer_name": customer_name,
        "customer_email": customer_email,
        "weight": float(weight),
        "cash_on_delivery": float(cod_amount) if cod_amount else 0.0,
        "currency": currency,
        "shipping_address": {
            "name": customer_name,
            "address1": addr.get("address1") or addr.get("street") or "",
            "address2": addr.get("address2") or "",
            "city": addr.get("city") or "",
            "postal_code": addr.get("postal_code") or addr.get("zip") or "",
            "country": addr.get("country") or addr.get("country_code") or "ES",
            "phone": addr.get("phone"),
            "email": addr.get("email") or customer_email,
            # opcionales que el adapter de GLS sabe leer:
            "street_number": addr.get("street_number"),
        },
        # Señal para flex delivery si quieres; comentalo si no aplica:
        # "delivery_flex": True,
        # "service": "PARCEL" | "EXPRESS"
    }
    return payload


@router.post("/mirakl-to-gls")
async def mirakl_to_gls_simple(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Orquestador mínimo: coge órdenes de Mirakl y crea envíos en GLS ShipIT.
    - Lee órdenes en estado SHIPPING (ajusta si hace falta).
    - Mapea campos mínimos obligatorios.
    - Crea envío en GLS (etiqueta mediante ReturnLabels).
    """
    t0 = time.time()

    try:
        # 1) Traer pedidos de Mirakl
        mirakl_res = await mirakl_adapter.get_orders(order_state_codes="SHIPPING", limit=limit, offset=0)
        orders = mirakl_res.get("orders", [])
        if not orders:
            return {
                "success": True,
                "message": "No hay pedidos en Mirakl para procesar",
                "orders_processed": 0,
                "shipments_created": 0,
                "shipments": [],
            }

        # 2) Transformar a payload de GLS
        gls_payloads: List[Dict[str, Any]] = []
        for o in orders:
            try:
                gls_payloads.append(_order_to_gls_payload(o))
            except Exception as ex:
                logger.warning(f"No se pudo transformar pedido {o.get('order_id')}: {ex}")

        if not gls_payloads:
            return {
                "success": True,
                "message": "Pedidos obtenidos pero ninguno transformable a GLS",
                "orders_processed": len(orders),
                "shipments_created": 0,
                "shipments": [],
            }

        # 3) Crear envíos en GLS (loop interno)
        bulk_res = await gls_adapter.create_shipments_bulk(gls_payloads)
        shipments = bulk_res.get("shipments", [])
        
        # 4) Actualizar Mirakl con tracking info (OR23 + OR24)
        mirakl_updates = []
        for i, shipment in enumerate(shipments):
            if i >= len(orders):
                break
                
            order = orders[i]
            order_id = order.get("order_id") or order.get("id")
            track_id = shipment.get("track_id")
            
            if not order_id or not track_id:
                logger.warning(f"Missing order_id or track_id for shipment {i}")
                continue
                
            try:
                # Actualizar tracking en Mirakl (OR23 + OR24)
                mirakl_result = await mirakl_adapter.update_order_tracking(
                    order_id=str(order_id),
                    tracking_number=track_id,
                    carrier_code="gls",
                    carrier_name="GLS",
                    validate_shipment=True  # También ejecuta OR24
                )
                
                mirakl_updates.append({
                    "order_id": order_id,
                    "tracking_number": track_id,
                    "status": "updated",
                    "mirakl_response": mirakl_result
                })
                
                # Log en unified logger
                unified_order_logger.upsert_order(
                    str(order_id),
                    {
                        "marketplace": "mirakl",
                        "carrier": "gls",
                        "carrier_code": "gls",
                        "tracking_number": track_id,
                        "internal_state": "MIRAKL_OK",
                        "carrier_status": "CREATED",
                        "last_event": "GLS_SHIPMENT_CREATED",
                        "last_event_at": datetime.utcnow().isoformat()
                    }
                )
                
                logger.info(f"[MIRAKL-GLS] Updated Mirakl for order {order_id} with tracking {track_id}")
                
            except Exception as e:
                logger.error(f"[MIRAKL-GLS] Failed to update Mirakl for order {order_id}: {e}", exc_info=True)
                mirakl_updates.append({
                    "order_id": order_id,
                    "tracking_number": track_id,
                    "status": "error",
                    "error": str(e)
                })
        
        duration_ms = int((time.time() - t0) * 1000)

        # 5) Respuesta
        return {
            "success": True,
            "message": f"Procesadas {len(orders)} órdenes de Mirakl; creados {len(shipments)} envíos en GLS; {len(mirakl_updates)} actualizaciones a Mirakl",
            "orders_processed": len(orders),
            "shipments_created": len(shipments),
            "mirakl_updates": mirakl_updates,
            "shipments": shipments,
            "duration_ms": duration_ms,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

    except Exception as e:
        logger.exception("Fallo en mirakl_to_gls_simple")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-gls-direct")
async def test_gls_direct(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Función de prueba directa para GLS ShipIT API.
    Envía datos hardcodeados para probar la conectividad y respuesta de la API.
    """
    t0 = time.time()
    
    # Datos de prueba hardcodeados para GLS
    test_order = {
        "order_id": f"TEST-GLS-{int(time.time())}",
        "customer_name": "Juan Pérez García",
        "customer_email": "juan.perez@example.com",
        "customer_phone": "+34612345678",
        "weight": 2.5,
        "cash_on_delivery": 0.0,
        "currency": "EUR",
        "shipping_address": {
            "name": "Juan Pérez García",
            "address1": "Calle Mayor 123",
            "address2": "2º B",  # StreetNumber para GLS
            "city": "Madrid",
            "postal_code": "28001",
            "country": "ES",
            "phone": "+34612345678",
            "email": "juan.perez@example.com",
            "street_number": "123"  # Campo específico para GLS
        },
        "service": "PARCEL",  # PARCEL o EXPRESS
        "delivery_flex": False,
        "observations": "Pedido de prueba - GLS ShipIT API"
    }
    
    try:
        logger.info(f"[TEST-GLS] Iniciando prueba directa con orden: {test_order['order_id']}")
        
        # Crear envío directamente con GLS
        result = await gls_adapter.create_shipment(test_order)
        
        duration_ms = int((time.time() - t0) * 1000)
        
        logger.info(f"[TEST-GLS] Prueba completada exitosamente, duration_ms={duration_ms}")
        
        return {
            "success": True,
            "message": "Prueba directa de GLS completada exitosamente",
            "test_order": test_order,
            "gls_response": result,
            "carrier": "gls",
            "duration_ms": duration_ms,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "debug_info": {
                "adapter_mode": "mock" if gls_adapter.is_mock_mode else "real",
                "base_url": gls_adapter.base_url,
                "endpoint_used": gls_adapter.endpoints["shipments"]
            }
        }
        
    except Exception as e:
        duration_ms = int((time.time() - t0) * 1000)
        logger.error(f"[TEST-GLS] Error en prueba directa: {str(e)}", exc_info=True)
        
        return {
            "success": False,
            "message": f"Error en prueba directa de GLS: {str(e)}",
            "test_order": test_order,
            "carrier": "gls",
            "duration_ms": duration_ms,
            "error": str(e),
            "error_type": type(e).__name__,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "debug_info": {
                "adapter_mode": "mock" if gls_adapter.is_mock_mode else "real",
                "base_url": gls_adapter.base_url,
                "endpoint_used": gls_adapter.endpoints["shipments"]
            }
        }


@router.post("/gls/tracking-poller/start")
async def start_gls_tracking_poller(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Inicia el servicio de polling de tracking de GLS.
    
    El poller consulta periódicamente el estado de envíos GLS activos
    y actualiza Mirakl cuando detecta cambios.
    """
    try:
        await gls_tracking_poller.start()
        return {
            "success": True,
            "message": "GLS tracking poller started",
            "poll_interval_seconds": gls_tracking_poller.poll_interval,
            "status": "running"
        }
    except Exception as e:
        logger.error(f"Error starting GLS tracking poller: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gls/tracking-poller/stop")
async def stop_gls_tracking_poller(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Detiene el servicio de polling de tracking de GLS.
    """
    try:
        await gls_tracking_poller.stop()
        return {
            "success": True,
            "message": "GLS tracking poller stopped",
            "status": "stopped"
        }
    except Exception as e:
        logger.error(f"Error stopping GLS tracking poller: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gls/tracking-poller/status")
async def get_gls_tracking_poller_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtiene el estado actual del servicio de polling de GLS.
    """
    return {
        "success": True,
        "running": gls_tracking_poller.running,
        "poll_interval_seconds": gls_tracking_poller.poll_interval,
        "adapter_mode": "mock" if gls_adapter.is_mock_mode else "real"
    }


@router.post("/gls/tracking-poller/poll-once")
async def poll_gls_tracking_once(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Ejecuta un ciclo de polling manualmente (útil para testing).
    """
    try:
        result = await gls_tracking_poller.poll_once()
        return {
            "success": True,
            "message": "Manual polling completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error in manual GLS tracking poll: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gls/tracking-poller/poll-order/{order_id}")
async def poll_gls_tracking_for_order(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Consulta tracking de una orden específica y actualiza Mirakl.
    
    Args:
        order_id: ID de la orden en Mirakl
    """
    try:
        result = await gls_tracking_poller.poll_specific_order(order_id)
        return {
            "success": True,
            "message": f"Tracking polled for order {order_id}",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error polling tracking for order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gls/webhook/tracking-update")
async def gls_tracking_webhook(
    webhook_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Webhook para recibir actualizaciones de tracking de GLS (o agregadores como AfterShip/TrackingMore).
    
    Este endpoint está preparado para uso futuro cuando se integre con un servicio
    de webhooks de terceros que monitoree GLS.
    
    Formato esperado del webhook_data:
    {
        "tracking_number": "GLS1234567",
        "status": "DELIVERED",
        "events": [...],
        "order_reference": "order_id_mirakl"
    }
    """
    try:
        tracking_number = webhook_data.get("tracking_number")
        status = webhook_data.get("status")
        order_reference = webhook_data.get("order_reference")
        
        if not tracking_number or not status:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: tracking_number, status"
            )
        
        logger.info(f"[GLS WEBHOOK] Received tracking update: {tracking_number} -> {status}")
        
        # Buscar orden por tracking number o referencia
        order = None
        if order_reference:
            order = unified_order_logger.get_order_by_id(order_reference)
        
        if not order:
            # Buscar por tracking number en todos los pedidos
            all_orders = unified_order_logger.get_all_orders()
            for o in all_orders:
                if o.get("tracking_number") == tracking_number:
                    order = o
                    break
        
        if not order:
            logger.warning(f"[GLS WEBHOOK] Order not found for tracking {tracking_number}")
            return {
                "success": False,
                "message": f"Order not found for tracking number {tracking_number}"
            }
        
        # Actualizar estado en unified logger
        order_id = order.get("mirakl_order_id")
        unified_order_logger.upsert_order(
            order_id,
            {
                "carrier_status": status,
                "last_event": f"GLS_WEBHOOK:{status}",
                "last_event_at": datetime.utcnow().isoformat(),
                "tracking_events": webhook_data.get("events", [])
            }
        )
        
        # Actualizar Mirakl si corresponde
        try:
            await mirakl_adapter.update_order_tracking(
                order_id=order_id,
                tracking_number=tracking_number,
                carrier_code="gls",
                carrier_name="GLS",
                validate_shipment=False
            )
            
            logger.info(f"[GLS WEBHOOK] Updated Mirakl for order {order_id}")
        except Exception as e:
            logger.error(f"[GLS WEBHOOK] Failed to update Mirakl: {e}", exc_info=True)
        
        # Log webhook event
        await csv_ops_logger.log(
            scope="gls_webhook",
            action="tracking_update",
            order_id=order_id,
            carrier="gls",
            status="OK",
            message=f"Webhook tracking update: {status}",
            meta={"tracking_number": tracking_number, "status": status}
        )
        
        return {
            "success": True,
            "message": "Tracking update processed",
            "order_id": order_id,
            "tracking_number": tracking_number,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[GLS WEBHOOK] Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
