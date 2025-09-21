#!/usr/bin/env python3
"""
Mirakl Mock Server

This server simulates Mirakl API responses for testing purposes.
Runs on port 3002.
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import time
from datetime import datetime, timedelta

app = FastAPI(title="Mirakl Mock API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for orders
orders_db: Dict[str, Dict[str, Any]] = {}

# Request/Response models
class Order(BaseModel):
    order_id: str
    status: str
    customer_name: str
    customer_email: str
    weight: float
    total_amount: float
    currency: str
    created_at: str
    shipping_address: Dict[str, Any]

class TrackingUpdate(BaseModel):
    carrier_code: str
    carrier_name: str
    tracking_number: str
    shipped_at: Optional[str] = None

class ShipUpdate(BaseModel):
    carrier_code: str
    carrier_name: str
    tracking_number: str
    shipped_at: str

class ShipmentTracking(BaseModel):
    shipment_id: str
    order_id: str
    carrier_code: str
    carrier_name: str
    carrier_url: Optional[str] = None
    carrier_standard_code: Optional[str] = None
    tracking_number: str

class ShipmentsTrackingRequest(BaseModel):
    shipments: List[ShipmentTracking]

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mirakl Mock API",
        "version": "1.0.0",
        "endpoints": {
            "orders": "GET /api/orders",
            "order_tracking": "PUT /api/orders/{order_id}/tracking",
            "order_ship": "PUT /api/orders/{order_id}/ship",
            "shipments_tracking": "POST /api/shipments/tracking"
        }
    }

@app.get("/api/orders")
async def get_orders(
    status: str = "PENDING",
    limit: int = 100,
    offset: int = 0
):
    """Get orders (OR12)."""
    # Generate mock orders if none exist
    if not orders_db:
        mock_orders = [
            {
                "order_id": "MIR-001",
                "status": "PENDING",
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
                "status": "PENDING_APPROVAL",
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
            },
            {
                "order_id": "MIR-003",
                "status": "SHIPPING",
                "customer_name": "Carlos López",
                "customer_email": "carlos.lopez@email.com",
                "weight": 3.2,
                "total_amount": 67.80,
                "currency": "EUR",
                "created_at": "2025-09-19T22:00:00Z",
                "shipping_address": {
                    "name": "Carlos López",
                    "street": "Plaza España 789",
                    "city": "Valencia",
                    "postal_code": "46001",
                    "country": "ES"
                }
            }
        ]
        
        for order in mock_orders:
            orders_db[order["order_id"]] = order
    
    # Filter orders by status
    filtered_orders = [
        order for order in orders_db.values()
        if order["status"] == status
    ]
    
    # Apply pagination
    start = offset
    end = offset + limit
    paginated_orders = filtered_orders[start:end]
    
    return {
        "orders": paginated_orders,
        "total": len(filtered_orders),
        "limit": limit,
        "offset": offset
    }

@app.put("/api/orders/{order_id}/tracking")
async def update_order_tracking(
    order_id: str,
    tracking: TrackingUpdate
):
    """Update order tracking (OR23)."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Update order with tracking info
    order["tracking_number"] = tracking.tracking_number
    order["carrier_code"] = tracking.carrier_code
    order["carrier_name"] = tracking.carrier_name
    order["tracked_at"] = datetime.utcnow().isoformat()
    
    # Return 200 OK with response data
    return {
        "order_id": order_id,
        "status": "success",
        "tracking_updated": True,
        "tracking_number": tracking.tracking_number,
        "carrier": tracking.carrier_name,
        "updated_at": datetime.utcnow().isoformat()
    }

@app.put("/api/orders/{order_id}/ship")
async def update_order_ship(
    order_id: str,
    ship: ShipUpdate
):
    """Update order status to SHIPPED (OR24)."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Update order status
    order["status"] = "SHIPPED"
    order["tracking_number"] = ship.tracking_number
    order["carrier_code"] = ship.carrier_code
    order["carrier_name"] = ship.carrier_name
    order["shipped_at"] = ship.shipped_at
    order["updated_at"] = datetime.utcnow().isoformat()
    
    # Return 204 No Content (as per OR24 spec)
    from fastapi.responses import Response
    return Response(status_code=204)

@app.post("/api/shipments/tracking")
async def update_shipments_tracking(
    request: ShipmentsTrackingRequest
):
    """Update tracking for multiple shipments (ST23)."""
    updated_shipments = []
    
    for shipment in request.shipments:
        order_id = shipment.order_id
        
        if order_id in orders_db:
            order = orders_db[order_id]
            
            # Update order with tracking info
            order["tracking_number"] = shipment.tracking_number
            order["carrier_code"] = shipment.carrier_code
            order["carrier_name"] = shipment.carrier_name
            order["tracked_at"] = datetime.utcnow().isoformat()
            
            updated_shipments.append({
                "shipment_id": shipment.shipment_id,
                "order_id": order_id,
                "status": "TRACKING_UPDATED",
                "carrier_code": shipment.carrier_code,
                "carrier_name": shipment.carrier_name,
                "tracking_number": shipment.tracking_number,
                "updated_at": datetime.utcnow().isoformat()
            })
    
    return {
        "updated_shipments": len(updated_shipments),
        "shipments": updated_shipments,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/orders/{order_id}")
async def get_order_details(order_id: str):
    """Get order details."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return orders_db[order_id]

@app.get("/api/orders/{order_id}/status")
async def get_order_status(order_id: str):
    """Get order status."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    return {
        "order_id": order_id,
        "status": order["status"],
        "updated_at": order.get("updated_at", order["created_at"])
    }

@app.get("/api/orders")
async def list_orders():
    """List all orders (for debugging)."""
    return {
        "orders": list(orders_db.values()),
        "total": len(orders_db)
    }

if __name__ == "__main__":
    print("Starting Mirakl Mock Server on port 3002...")
    uvicorn.run(app, host="0.0.0.0", port=3002)
