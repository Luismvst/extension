#!/usr/bin/env python3
"""
TIPSA Mock Server

This server simulates TIPSA API responses for testing purposes.
Runs on port 3001.
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import time
import hashlib
import hmac
import json
from datetime import datetime, timedelta

app = FastAPI(title="TIPSA Mock API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for shipments
shipments_db: Dict[str, Dict[str, Any]] = {}
webhook_secret = "tipsa_webhook_secret_2025"

# Request/Response models
class ShipmentRequest(BaseModel):
    order_id: str
    weight: float
    value: float
    currency: str
    recipient: Dict[str, Any]
    service: str = "STANDARD"

class ShipmentResponse(BaseModel):
    shipment_id: str
    expedition_id: str
    tracking_number: str
    status: str
    label_url: Optional[str] = None
    estimated_delivery: str
    cost: float
    currency: str
    carrier: str
    service: str
    created_at: str

class ShipmentStatus(BaseModel):
    expedition_id: str
    status: str
    tracking_number: str
    label_url: Optional[str] = None
    updated_at: str

class WebhookEvent(BaseModel):
    event_id: str
    event_type: str
    expedition_id: str
    status: str
    tracking_number: Optional[str] = None
    label_url: Optional[str] = None
    timestamp: str

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TIPSA Mock API",
        "version": "1.0.0",
        "endpoints": {
            "shipments": "POST /api/shipments",
            "shipment_status": "GET /api/shipments/{expedition_id}",
            "webhook": "POST /webhook"
        }
    }

@app.post("/api/shipments", response_model=List[ShipmentResponse])
async def create_shipments(
    shipments: List[ShipmentRequest],
    idempotency_key: Optional[str] = Header(None)
):
    """Create shipments (batch)."""
    responses = []
    
    for shipment in shipments:
        # Generate expedition ID
        expedition_id = f"TIPSA-{shipment.order_id[-8:].upper()}{hash(shipment.order_id) % 10000:04d}"
        tracking_number = f"1Z{shipment.order_id[-8:].upper()}{hash(shipment.order_id) % 10000:04d}"
        
        # Check idempotency
        if idempotency_key and expedition_id in shipments_db:
            existing = shipments_db[expedition_id]
            responses.append(ShipmentResponse(**existing))
            continue
        
        # Create shipment
        shipment_data = {
            "shipment_id": expedition_id,
            "expedition_id": expedition_id,
            "tracking_number": tracking_number,
            "status": "CREATED",
            "label_url": None,
            "estimated_delivery": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "cost": 15.50 + (shipment.weight * 2.0),
            "currency": shipment.currency,
            "carrier": "TIPSA",
            "service": shipment.service,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store in database
        shipments_db[expedition_id] = shipment_data
        responses.append(ShipmentResponse(**shipment_data))
        
        # Simulate webhook after 2 seconds
        await simulate_webhook(expedition_id, "LABELED")
    
    return responses

@app.get("/api/shipments/{expedition_id}", response_model=ShipmentStatus)
async def get_shipment_status(expedition_id: str):
    """Get shipment status."""
    if expedition_id not in shipments_db:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    shipment = shipments_db[expedition_id]
    
    # Simulate status progression
    statuses = ["CREATED", "LABELED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"]
    current_status = shipment["status"]
    status_index = statuses.index(current_status) if current_status in statuses else 0
    
    # Progress status based on time elapsed
    created_time = datetime.fromisoformat(shipment["created_at"])
    elapsed_minutes = (datetime.utcnow() - created_time).total_seconds() / 60
    
    if elapsed_minutes > 10 and status_index < 1:
        shipment["status"] = "LABELED"
        shipment["label_url"] = f"https://mock.tipsa.com/labels/{expedition_id}"
        await simulate_webhook(expedition_id, "LABELED")
    elif elapsed_minutes > 30 and status_index < 2:
        shipment["status"] = "IN_TRANSIT"
        await simulate_webhook(expedition_id, "IN_TRANSIT")
    elif elapsed_minutes > 60 and status_index < 3:
        shipment["status"] = "OUT_FOR_DELIVERY"
        await simulate_webhook(expedition_id, "OUT_FOR_DELIVERY")
    elif elapsed_minutes > 90 and status_index < 4:
        shipment["status"] = "DELIVERED"
        await simulate_webhook(expedition_id, "DELIVERED")
    
    return ShipmentStatus(
        expedition_id=expedition_id,
        status=shipment["status"],
        tracking_number=shipment["tracking_number"],
        label_url=shipment.get("label_url"),
        updated_at=datetime.utcnow().isoformat()
    )

@app.post("/webhook")
async def receive_webhook(
    event: WebhookEvent,
    x_signature: str = Header(...),
    x_timestamp: str = Header(...)
):
    """Receive webhook events (for testing)."""
    # Validate signature
    payload = json.dumps(event.dict(), sort_keys=True)
    expected_signature = hmac.new(
        webhook_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(x_signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Update shipment status
    if event.expedition_id in shipments_db:
        shipments_db[event.expedition_id]["status"] = event.status
        if event.tracking_number:
            shipments_db[event.expedition_id]["tracking_number"] = event.tracking_number
        if event.label_url:
            shipments_db[event.expedition_id]["label_url"] = event.label_url
    
    return {"status": "accepted"}

async def simulate_webhook(expedition_id: str, event_type: str):
    """Simulate webhook call to orchestrator."""
    import asyncio
    
    async def send_webhook():
        await asyncio.sleep(2)  # Wait 2 seconds
        
        event_data = {
            "event_id": f"evt_{int(time.time())}_{expedition_id}",
            "event_type": event_type,
            "expedition_id": expedition_id,
            "status": event_type,
            "tracking_number": shipments_db[expedition_id]["tracking_number"],
            "label_url": shipments_db[expedition_id].get("label_url"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = json.dumps(event_data, sort_keys=True)
        signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://localhost:8080/api/v1/carriers/webhooks/tipsa",
                    json=event_data,
                    headers={
                        "X-Signature": signature,
                        "X-Timestamp": datetime.utcnow().isoformat(),
                        "Content-Type": "application/json"
                    },
                    timeout=5.0
                )
        except Exception as e:
            print(f"Failed to send webhook: {e}")
    
    # Run webhook in background
    asyncio.create_task(send_webhook())

@app.get("/api/shipments")
async def list_shipments():
    """List all shipments (for debugging)."""
    return {
        "shipments": list(shipments_db.values()),
        "total": len(shipments_db)
    }

if __name__ == "__main__":
    print("Starting TIPSA Mock Server on port 3001...")
    uvicorn.run(app, host="0.0.0.0", port=3001)
