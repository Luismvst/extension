"""
Carrier selection rules engine.

This module implements the business rules for automatically selecting
the appropriate carrier based on order characteristics.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def select_carrier(order: Dict[str, Any]) -> str:
    """
    Select the appropriate carrier based on order characteristics.
    
    Rules:
    1. If weight > 20kg → TIPSA (handles heavy packages)
    2. If payment_method == "COD" → TIPSA (cash on delivery)
    3. If shipping_speed == "EXPRESS" → DHL (express delivery)
    4. If country != "ES" → DHL (international shipping)
    5. Default → TIPSA (standard domestic shipping)
    
    Args:
        order: Order data dictionary
        
    Returns:
        Carrier code: "tipsa", "dhl", "ontime", or "ups"
    """
    try:
        # Rule 1: Heavy packages (>20kg) go to TIPSA
        weight = order.get("weight", 0)
        if weight > 20:
            logger.debug(f"Order {order.get('order_id', 'unknown')} → TIPSA (weight: {weight}kg)")
            return "tipsa"
        
        # Rule 2: Cash on delivery goes to TIPSA
        payment_method = order.get("payment_method", "")
        if payment_method == "COD":
            logger.debug(f"Order {order.get('order_id', 'unknown')} → TIPSA (COD)")
            return "tipsa"
        
        # Rule 3: Express shipping goes to DHL
        shipping_speed = order.get("shipping_speed", "")
        if shipping_speed == "EXPRESS":
            logger.debug(f"Order {order.get('order_id', 'unknown')} → DHL (express)")
            return "dhl"
        
        # Rule 4: International shipping goes to DHL
        shipping_address = order.get("shipping_address", {})
        country = shipping_address.get("country", "ES")
        if country != "ES":
            logger.debug(f"Order {order.get('order_id', 'unknown')} → DHL (international: {country})")
            return "dhl"
        
        # Rule 5: Default to TIPSA for standard domestic shipping
        logger.debug(f"Order {order.get('order_id', 'unknown')} → TIPSA (default)")
        return "tipsa"
        
    except Exception as e:
        logger.error(f"Error selecting carrier for order {order.get('order_id', 'unknown')}: {e}")
        # Fallback to TIPSA in case of error
        return "tipsa"


def get_carrier_priority(carrier: str) -> int:
    """
    Get priority order for carrier selection (lower number = higher priority).
    
    Args:
        carrier: Carrier code
        
    Returns:
        Priority number (1-4)
    """
    priorities = {
        "tipsa": 1,    # Highest priority (default)
        "dhl": 2,      # International/express
        "ontime": 3,   # Alternative domestic
        "ups": 4       # Alternative international
    }
    return priorities.get(carrier, 5)


def validate_carrier_selection(order: Dict[str, Any], selected_carrier: str) -> bool:
    """
    Validate that the selected carrier is appropriate for the order.
    
    Args:
        order: Order data dictionary
        selected_carrier: Selected carrier code
        
    Returns:
        True if selection is valid, False otherwise
    """
    try:
        weight = order.get("weight", 0)
        country = order.get("shipping_address", {}).get("country", "ES")
        shipping_speed = order.get("shipping_speed", "")
        payment_method = order.get("payment_method", "")
        
        # Validation rules
        if selected_carrier == "tipsa":
            # TIPSA can handle any domestic order
            return country == "ES"
        
        elif selected_carrier == "dhl":
            # DHL is good for international or express
            return country != "ES" or shipping_speed == "EXPRESS"
        
        elif selected_carrier == "ontime":
            # OnTime for domestic standard
            return country == "ES" and shipping_speed != "EXPRESS"
        
        elif selected_carrier == "ups":
            # UPS for international or heavy domestic
            return country != "ES" or weight > 15
        
        return False
        
    except Exception as e:
        logger.error(f"Error validating carrier selection: {e}")
        return False


def get_carrier_info(carrier: str) -> Dict[str, Any]:
    """
    Get information about a carrier.
    
    Args:
        carrier: Carrier code
        
    Returns:
        Dictionary with carrier information
    """
    carrier_info = {
        "tipsa": {
            "name": "TIPSA",
            "description": "Spanish domestic carrier",
            "strengths": ["Heavy packages", "COD", "Domestic"],
            "max_weight": 30.0,
            "countries": ["ES"],
            "services": ["standard", "express"]
        },
        "dhl": {
            "name": "DHL Express",
            "description": "International express carrier",
            "strengths": ["International", "Express", "Reliability"],
            "max_weight": 70.0,
            "countries": ["*"],  # Worldwide
            "services": ["express", "international"]
        },
        "ontime": {
            "name": "OnTime",
            "description": "Alternative domestic carrier",
            "strengths": ["Cost-effective", "Domestic", "Reliability"],
            "max_weight": 25.0,
            "countries": ["ES"],
            "services": ["standard"]
        },
        "ups": {
            "name": "UPS",
            "description": "International and domestic carrier",
            "strengths": ["International", "Heavy packages", "Tracking"],
            "max_weight": 70.0,
            "countries": ["*"],  # Worldwide
            "services": ["ground", "express", "international"]
        }
    }
    
    return carrier_info.get(carrier, {
        "name": "Unknown",
        "description": "Unknown carrier",
        "strengths": [],
        "max_weight": 0.0,
        "countries": [],
        "services": []
    })
