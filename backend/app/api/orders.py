"""
Orders API endpoints.

This module provides endpoints for managing orders with status tracking.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

from ..core.auth import get_current_user
from ..services.order_storage import order_storage
from ..models.order import OrderStandard, OrderUpdateRequest, OrderStorage
from ..adapters.marketplaces.mirakl import MiraklAdapter
import logging

# Create logger for this module
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

# Initialize adapter
mirakl_adapter = MiraklAdapter()


@router.get("/")
async def get_orders(
    estado_mirakl: Optional[str] = None,
    estado_tipsa: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get orders with optional filtering by status.
    
    Args:
        estado_mirakl: Filter by Mirakl status
        estado_tipsa: Filter by TIPSA status
        limit: Maximum number of orders to return
        offset: Number of orders to skip
        current_user: Authenticated user
    
    Returns:
        List of orders with pagination
    """
    try:
        # Get filtered orders
        if estado_mirakl or estado_tipsa:
            orders = order_storage.get_orders_by_status(estado_mirakl, estado_tipsa)
        else:
            orders = order_storage.get_all_orders()
        
        # Apply pagination
        total = len(orders)
        start = offset
        end = offset + limit
        paginated_orders = orders[start:end]
        
        # Convert orders to dict format safely
        orders_data = []
        for order in paginated_orders:
            order_dict = {
                "order_id": order.order_id,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat(),
                "estado_mirakl": order.estado_mirakl,
                "estado_tipsa": order.estado_tipsa,
                "tracking_number": order.tracking_number,
                "carrier_code": order.carrier_code,
                "carrier_name": order.carrier_name,
                "synced_to_mirakl": order.synced_to_mirakl,
                "synced_to_carrier": order.synced_to_carrier,
                "notes": order.notes,
                "order_data": {
                    "order_id": order.order_data.order_id,
                    "created_at": order.order_data.created_at.isoformat(),
                    "status": order.order_data.status,
                    "buyer": order.order_data.buyer,
                    "shipping": order.order_data.shipping,
                    "totals": order.order_data.totals,
                    "items": order.order_data.items
                }
            }
            orders_data.append(order_dict)
        
        return {
            "success": True,
            "orders": orders_data,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": end < total
        }
        
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get specific order by ID.
    
    Args:
        order_id: Order identifier
        current_user: Authenticated user
    
    Returns:
        Order details
    """
    try:
        order = order_storage.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "success": True,
            "order": order.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_order(
    order: OrderStandard,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create or update an order.
    
    Args:
        order: Order data
        current_user: Authenticated user
    
    Returns:
        Created/updated order
    """
    try:
        stored_order = order_storage.store_order(order)
        
        logger.info(f"Order {order.order_id} stored successfully")
        
        return {
            "success": True,
            "order": stored_order.dict(),
            "message": "Order stored successfully"
        }
        
    except Exception as e:
        logger.error(f"Error storing order {order.order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}")
async def update_order(
    order_id: str,
    update_data: OrderUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update order status and tracking information.
    
    Args:
        order_id: Order identifier
        update_data: Update data
        current_user: Authenticated user
    
    Returns:
        Updated order
    """
    try:
        # Ensure order_id matches
        update_data.order_id = order_id
        
        updated_order = order_storage.update_order_status(order_id, update_data)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        logger.info(f"Order {order_id} updated successfully")
        
        return {
            "success": True,
            "order": updated_order.dict(),
            "message": "Order updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete an order.
    
    Args:
        order_id: Order identifier
        current_user: Authenticated user
    
    Returns:
        Deletion result
    """
    try:
        success = order_storage.delete_order(order_id)
        if not success:
            raise HTTPException(status_code=404, detail="Order not found")
        
        logger.info(f"Order {order_id} deleted successfully")
        
        return {
            "success": True,
            "message": "Order deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/stats")
async def get_orders_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get orders summary statistics.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Orders summary statistics
    """
    try:
        summary = order_storage.get_orders_summary()
        
        return {
            "success": True,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting orders summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-from-mirakl")
async def fetch_orders_from_mirakl(
    status: str = "PENDING",
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Fetch orders from Mirakl and store them locally.
    
    Args:
        status: Order status to fetch
        limit: Maximum number of orders to fetch
        current_user: Authenticated user
    
    Returns:
        Fetch results
    """
    start_time = time.time()
    
    try:
        # Fetch orders from Mirakl
        mirakl_result = await mirakl_adapter.get_orders(status, limit, 0)
        orders = mirakl_result.get("orders", [])
        
        if not orders:
            return {
                "success": True,
                "message": "No orders found in Mirakl",
                "orders_fetched": 0,
                "orders_stored": 0
            }
        
        # Store orders locally
        stored_count = 0
        for order_data in orders:
            try:
                # Convert to OrderStandard format
                order = OrderStandard(
                    order_id=order_data.get("order_id"),
                    created_at=datetime.fromisoformat(order_data.get("created_at", datetime.utcnow().isoformat())),
                    status=order_data.get("status", "PENDING"),
                    items=[],  # TODO: Parse items from order_data
                    buyer={
                        "name": order_data.get("customer_name", ""),
                        "email": order_data.get("customer_email"),
                        "phone": order_data.get("customer_phone")
                    },
                    shipping={
                        "name": order_data.get("customer_name", ""),
                        "address1": order_data.get("shipping_address", {}).get("address1", ""),
                        "address2": order_data.get("shipping_address", {}).get("address2"),
                        "city": order_data.get("shipping_address", {}).get("city", ""),
                        "postcode": order_data.get("shipping_address", {}).get("postcode", ""),
                        "country": order_data.get("shipping_address", {}).get("country", "ES")
                    },
                    totals={
                        "goods": order_data.get("total_amount", 0),
                        "shipping": order_data.get("shipping_cost", 0)
                    },
                    estado_mirakl=order_data.get("status", "PENDING"),
                    estado_tipsa="PENDING"
                )
                
                order_storage.store_order(order)
                stored_count += 1
                
            except Exception as e:
                logger.error(f"Error storing order {order_data.get('order_id')}: {e}")
                continue
        
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Fetched {len(orders)} orders from Mirakl, stored {stored_count}, duration: {duration_ms}ms")
        
        return {
            "success": True,
            "message": f"Successfully fetched and stored {stored_count} orders from Mirakl",
            "orders_fetched": len(orders),
            "orders_stored": stored_count,
            "duration_ms": duration_ms
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Error fetching orders from Mirakl: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv")
async def export_orders_csv(
    estado_mirakl: Optional[str] = None,
    estado_tipsa: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export orders to CSV format.
    
    Args:
        estado_mirakl: Filter by Mirakl status
        estado_tipsa: Filter by TIPSA status
        current_user: Authenticated user
    
    Returns:
        CSV file download
    """
    try:
        # Get filtered orders
        if estado_mirakl or estado_tipsa:
            orders = order_storage.get_orders_by_status(estado_mirakl, estado_tipsa)
        else:
            orders = order_storage.get_all_orders()
        
        # Generate CSV content
        csv_lines = [
            "order_id,created_at,estado_mirakl,estado_tipsa,tracking_number,carrier_code,carrier_name,synced_to_mirakl,synced_to_carrier,customer_name,total_amount,currency,shipping_city,shipping_country"
        ]
        
        for order in orders:
            order_data = order.order_data
            csv_lines.append(
                f"{order.order_id},"
                f"{order.created_at.isoformat()},"
                f"{order.estado_mirakl},"
                f"{order.estado_tipsa},"
                f"{order.tracking_number or ''},"
                f"{order.carrier_code or ''},"
                f"{order.carrier_name or ''},"
                f"{order.synced_to_mirakl},"
                f"{order.synced_to_carrier},"
                f"{order_data.buyer.name},"
                f"{order_data.totals.goods},"
                f"{order_data.totals.currency or 'EUR'},"
                f"{order_data.shipping.city},"
                f"{order_data.shipping.country}"
            )
        
        csv_content = "\n".join(csv_lines)
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=orders_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting orders CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))
