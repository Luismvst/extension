"""
Mapping endpoints for order conversion
"""
from fastapi import APIRouter, HTTPException, Response
from typing import List
from app.models.order import MappingRequest, MappingResponse, OrderStandard
from app.services.tipsa import process_orders_mapping, validate_tipsa_data, map_orders_to_tipsa
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/tipsa", response_model=MappingResponse)
async def map_to_tipsa(request: MappingRequest):
    """
    Map orders to TIPSA format
    
    Args:
        request: Mapping request with orders and parameters
        
    Returns:
        Mapping response with TIPSA CSV or JSON
    """
    try:
        logger.log_business_event(
            "tipsa_mapping_request",
            order_count=len(request.orders),
            format=request.format,
            service=request.service
        )
        
        # Process mapping
        response = process_orders_mapping(
            orders=request.orders,
            format_type=request.format,
            service=request.service or "ESTANDAR"
        )
        
        if not response.success:
            logger.log_event(
                "WARNING",
                "TIPSA mapping failed",
                errors=response.errors,
                count=response.count
            )
        
        return response
        
    except Exception as e:
        logger.log_error(e, "map_to_tipsa")
        raise HTTPException(status_code=500, detail=f"Mapping failed: {str(e)}")


@router.post("/tipsa/csv")
async def map_to_tipsa_csv(request: MappingRequest):
    """
    Map orders to TIPSA CSV format and return as downloadable file
    
    Args:
        request: Mapping request with orders
        
    Returns:
        CSV file response
    """
    try:
        # Process mapping
        response = process_orders_mapping(
            orders=request.orders,
            format_type="csv",
            service=request.service or "ESTANDAR"
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=f"Mapping failed: {', '.join(response.errors)}")
        
        # Return CSV file
        return Response(
            content=response.data,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=tipsa_orders.csv"
            }
        )
        
    except Exception as e:
        logger.log_error(e, "map_to_tipsa_csv")
        raise HTTPException(status_code=500, detail=f"CSV generation failed: {str(e)}")


@router.post("/tipsa/validate")
async def validate_tipsa_orders(orders: List[OrderStandard]):
    """
    Validate orders for TIPSA mapping
    
    Args:
        orders: List of orders to validate
        
    Returns:
        Validation results
    """
    try:
        validation_results = []
        
        # Map to TIPSA format
        tipsa_orders = map_orders_to_tipsa(orders)
        
        # Validate each order
        for i, tipsa_order in enumerate(tipsa_orders):
            errors = validate_tipsa_data(tipsa_order)
            validation_results.append({
                "order_id": orders[i].order_id,
                "valid": len(errors) == 0,
                "errors": errors
            })
        
        # Summary
        valid_count = sum(1 for result in validation_results if result["valid"])
        total_count = len(validation_results)
        
        logger.log_business_event(
            "tipsa_validation",
            total_count=total_count,
            valid_count=valid_count,
            invalid_count=total_count - valid_count
        )
        
        return {
            "summary": {
                "total": total_count,
                "valid": valid_count,
                "invalid": total_count - valid_count
            },
            "results": validation_results
        }
        
    except Exception as e:
        logger.log_error(e, "validate_tipsa_orders")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/tipsa/schema")
async def get_tipsa_schema():
    """
    Get TIPSA CSV schema information
    
    Returns:
        Schema definition
    """
    return {
        "format": "csv",
        "separator": ";",
        "headers": [
            "destinatario",
            "direccion", 
            "cp",
            "poblacion",
            "pais",
            "contacto",
            "telefono",
            "email",
            "referencia",
            "peso",
            "servicio"
        ],
        "description": {
            "destinatario": "Recipient name",
            "direccion": "Full address",
            "cp": "Postal code (5 digits)",
            "poblacion": "City name",
            "pais": "Country code (2 letters)",
            "contacto": "Contact person name",
            "telefono": "Phone number (optional)",
            "email": "Email address (optional)",
            "referencia": "Order reference",
            "peso": "Package weight in kg",
            "servicio": "Service type (ESTANDAR, URGENTE, EXPRESS, ECONOMICO)"
        },
        "validation_rules": {
            "cp": "Must be 5 digits",
            "pais": "Must be 2-letter country code",
            "email": "Must be valid email format",
            "telefono": "Must be valid Spanish phone format",
            "peso": "Must be positive number <= 1000kg"
        }
    }
