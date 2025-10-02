"""
TIPSA mapping service
"""
from typing import List
from app.models.order import OrderStandard, TIPSAOrder, MappingResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


def map_order_to_tipsa(order: OrderStandard, default_service: str = "ESTANDAR") -> TIPSAOrder:
    """
    Map OrderStandard to TIPSA format
    
    Args:
        order: Standardized order
        default_service: Default service type
        
    Returns:
        TIPSA formatted order
    """
    return TIPSAOrder(
        destinatario=order.recipient_name,
        direccion=order.recipient_address,
        cp=order.recipient_postal_code,
        poblacion=order.recipient_city,
        pais=order.recipient_country,
        contacto=order.recipient_contact or order.recipient_name,
        telefono=order.recipient_phone or "",
        email=order.recipient_email or "",
        referencia=order.reference,
        peso=order.weight_kg,
        servicio=default_service,
        bultos=order.packages or "1",
        observaciones=order.observations or "",
        reembolso=order.cash_on_delivery or "0.00",
        nif_consignatario=order.recipient_tax_id or "",
        codigo_cliente=order.customer_code or "",
        multireferencia=order.multi_reference or ""
    )


def map_orders_to_tipsa(orders: List[OrderStandard], default_service: str = "ESTANDAR") -> List[TIPSAOrder]:
    """
    Map multiple orders to TIPSA format
    
    Args:
        orders: List of standardized orders
        default_service: Default service type
        
    Returns:
        List of TIPSA formatted orders
    """
    return [map_order_to_tipsa(order, default_service) for order in orders]


def generate_tipsa_csv(orders: List[OrderStandard], default_service: str = "ESTANDAR") -> str:
    """
    Generate TIPSA CSV content from OrderStandard (legacy method)
    
    Args:
        orders: List of standardized orders
        default_service: Default service type
        
    Returns:
        CSV content as string
    """
    if not orders:
        return ""
    
    tipsa_orders = map_orders_to_tipsa(orders, default_service)
    
    # Extended CSV headers for new fields
    headers = [
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
        "servicio",
        "bultos",
        "observaciones",
        "reembolso",
        "nif_consignatario",
        "codigo_cliente",
        "multireferencia"
    ]
    
    # Generate CSV content
    csv_lines = [";".join(headers)]
    
    for order in tipsa_orders:
        row = [
            order.destinatario,
            order.direccion,
            order.cp,
            order.poblacion,
            order.pais,
            order.contacto,
            order.telefono,
            order.email,
            order.referencia,
            order.peso,
            order.servicio,
            order.bultos,
            order.observaciones,
            order.reembolso,
            order.nif_consignatario,
            order.codigo_cliente,
            order.multireferencia
        ]
        csv_lines.append(";".join(row))
    
    return "\n".join(csv_lines)


def validate_tipsa_data(order: TIPSAOrder) -> List[str]:
    """
    Validate TIPSA order data
    
    Args:
        order: TIPSA order to validate
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields validation
    if not order.destinatario.strip():
        errors.append("Destinatario is required")
    
    if not order.direccion.strip():
        errors.append("Dirección is required")
    
    if not order.cp.strip():
        errors.append("Código postal is required")
    
    if not order.poblacion.strip():
        errors.append("Población is required")
    
    if not order.pais.strip():
        errors.append("País is required")
    
    if not order.referencia.strip():
        errors.append("Referencia is required")
    
    # Format validation
    if order.cp and not _is_valid_postal_code(order.cp):
        errors.append("Invalid postal code format")
    
    if order.pais and not _is_valid_country_code(order.pais):
        errors.append("Invalid country code")
    
    if order.email and not _is_valid_email(order.email):
        errors.append("Invalid email format")
    
    if order.telefono and not _is_valid_phone(order.telefono):
        errors.append("Invalid phone format")
    
    if order.peso and not _is_valid_weight(order.peso):
        errors.append("Invalid weight format")
    
    return errors


def process_orders_mapping(orders: List[OrderStandard], format_type: str = "csv", service: str = "ESTANDAR") -> MappingResponse:
    """
    Process orders mapping with error handling
    
    Args:
        orders: List of orders to process
        format_type: Output format (csv, json)
        service: Service type
        
    Returns:
        Mapping response with results
    """
    errors = []
    processed_count = 0
    
    try:
        if format_type == "csv":
            data = generate_tipsa_csv(orders, service)
        elif format_type == "json":
            tipsa_orders = map_orders_to_tipsa(orders, service)
            data = "\n".join([order.model_dump_json() for order in tipsa_orders])
        else:
            errors.append(f"Unsupported format: {format_type}")
            return MappingResponse(
                success=False,
                data="",
                format=format_type,
                count=0,
                errors=errors
            )
        
        processed_count = len(orders)
        
        logger.log_business_event(
            "orders_mapped",
            count=processed_count,
            format=format_type,
            service=service
        )
        
        return MappingResponse(
            success=True,
            data=data,
            format=format_type,
            count=processed_count,
            errors=errors
        )
        
    except Exception as e:
        logger.log_error(e, "process_orders_mapping")
        errors.append(f"Processing error: {str(e)}")
        
        return MappingResponse(
            success=False,
            data="",
            format=format_type,
            count=processed_count,
            errors=errors
        )




def _is_valid_postal_code(cp: str) -> bool:
    """Validate Spanish postal code format"""
    import re
    return bool(re.match(r'^\d{5}$', cp.strip()))


def _is_valid_country_code(country: str) -> bool:
    """Validate ISO country code format"""
    import re
    return bool(re.match(r'^[A-Z]{2}$', country.strip().upper()))


def _is_valid_email(email: str) -> bool:
    """Validate email format"""
    import re
    return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email.strip()))


def _is_valid_phone(phone: str) -> bool:
    """Validate Spanish phone format"""
    import re
    cleaned = phone.strip().replace(" ", "")
    return bool(re.match(r'^(\+34|0034)?[6-9]\d{8}$', cleaned))


def _is_valid_weight(weight: str) -> bool:
    """Validate weight format"""
    try:
        weight_num = float(weight)
        return 0 < weight_num <= 1000  # Max 1000kg
    except ValueError:
        return False
