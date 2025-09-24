"""
Pydantic models for orders and related data
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class OrderItem(BaseModel):
    """Order item model"""
    sku: str = Field(..., min_length=1, description="Product SKU")
    name: str = Field(..., min_length=1, description="Product name")
    qty: int = Field(..., gt=0, description="Quantity")
    unit_price: float = Field(..., gt=0, description="Unit price")
    
    @validator('unit_price')
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be positive')
        return round(v, 2)


class Buyer(BaseModel):
    """Buyer information model"""
    name: str = Field(..., min_length=1, description="Buyer name")
    email: Optional[str] = Field(None, description="Buyer email")
    phone: Optional[str] = Field(None, description="Buyer phone")
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class ShippingAddress(BaseModel):
    """Shipping address model"""
    name: str = Field(..., min_length=1, description="Shipping name")
    address1: str = Field(..., min_length=1, description="Address line 1")
    address2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., min_length=1, description="City")
    postcode: str = Field(..., min_length=1, description="Postal code")
    country: str = Field(..., min_length=2, max_length=2, description="Country code")
    
    @validator('country')
    def validate_country(cls, v):
        return v.upper()


class OrderTotals(BaseModel):
    """Order totals model"""
    goods: float = Field(..., ge=0, description="Goods total")
    shipping: Optional[float] = Field(0, ge=0, description="Shipping cost")
    
    @validator('goods', 'shipping')
    def validate_amounts(cls, v):
        return round(v, 2) if v is not None else v


class OrderStandard(BaseModel):
    """Standardized order model"""
    order_id: str = Field(..., min_length=1, description="Order ID")
    created_at: datetime = Field(..., description="Order creation date")
    status: str = Field(..., description="Order status")
    items: List[OrderItem] = Field(..., min_items=1, description="Order items")
    buyer: Buyer = Field(..., description="Buyer information")
    shipping: ShippingAddress = Field(..., description="Shipping address")
    totals: OrderTotals = Field(..., description="Order totals")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['PENDING', 'ACCEPTED', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        if v.upper() not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.upper()
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item is required')
        return v


class TIPSAOrder(BaseModel):
    """TIPSA order format model"""
    destinatario: str = Field(..., description="Recipient name")
    direccion: str = Field(..., description="Address")
    cp: str = Field(..., description="Postal code")
    poblacion: str = Field(..., description="City")
    pais: str = Field(..., description="Country code")
    contacto: str = Field(..., description="Contact name")
    telefono: str = Field("", description="Phone number")
    email: str = Field("", description="Email address")
    referencia: str = Field(..., description="Order reference")
    peso: str = Field(..., description="Weight")
    servicio: str = Field(..., description="Service type")
    
    @validator('pais')
    def validate_country(cls, v):
        return v.upper()


class OnTimeOrder(BaseModel):
    """OnTime order format model (placeholder)"""
    order_id: str = Field(..., description="Order ID")
    customer_name: str = Field(..., description="Customer name")
    address: str = Field(..., description="Full address")
    city: str = Field(..., description="City")
    postal_code: str = Field(..., description="Postal code")
    country: str = Field(..., description="Country code")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    weight: float = Field(..., gt=0, description="Weight in kg")
    service: str = Field(..., description="Service type")


class MappingRequest(BaseModel):
    """Request model for order mapping"""
    orders: List[OrderStandard] = Field(..., min_items=1, description="Orders to map")
    format: str = Field("csv", description="Output format")
    service: Optional[str] = Field(None, description="Default service type")


class MappingResponse(BaseModel):
    """Response model for order mapping"""
    success: bool = Field(..., description="Mapping success status")
    data: str = Field(..., description="Mapped data")
    format: str = Field(..., description="Output format")
    count: int = Field(..., description="Number of orders processed")
    errors: List[str] = Field(default_factory=list, description="Processing errors")


class ShipmentRequest(BaseModel):
    """Request model for shipment creation"""
    orders: List[OrderStandard] = Field(..., min_items=1, description="Orders to ship")
    carrier: str = Field(..., description="Carrier name")
    service: Optional[str] = Field(None, description="Service type")
    


class ShipmentResponse(BaseModel):
    """Response model for shipment creation"""
    success: bool = Field(..., description="Shipment creation success status")
    job_id: str = Field(..., description="Job ID")
    carrier: str = Field(..., description="Carrier name")
    count: int = Field(..., description="Number of orders processed")
    tracking_numbers: List[str] = Field(default_factory=list, description="Tracking numbers")
    errors: List[str] = Field(default_factory=list, description="Processing errors")


class TrackingRequest(BaseModel):
    """Request model for tracking update"""
    order_id: str = Field(..., description="Order ID")
    tracking_number: str = Field(..., description="Tracking number")
    status: str = Field(..., description="New status")
    carrier: str = Field(..., description="Carrier name")


class TrackingResponse(BaseModel):
    """Response model for tracking update"""
    success: bool = Field(..., description="Update success status")
    order_id: str = Field(..., description="Order ID")
    tracking_number: str = Field(..., description="Tracking number")
    status: str = Field(..., description="Updated status")
    updated_at: datetime = Field(..., description="Update timestamp")
