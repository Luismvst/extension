"""
Unit tests for carrier selection rules.
"""

import pytest
from app.rules.selector import select_carrier, get_carrier_priority, validate_carrier_selection, get_carrier_info


class TestCarrierSelector:
    """Test carrier selection rules."""
    
    def test_select_carrier_heavy_package(self):
        """Test selection for heavy packages (>20kg)."""
        order = {
            "order_id": "TEST-001",
            "weight": 25.0,
            "shipping_address": {"country": "ES"}
        }
        
        result = select_carrier(order)
        assert result == "tipsa"
    
    def test_select_carrier_cod_payment(self):
        """Test selection for COD payment."""
        order = {
            "order_id": "TEST-002",
            "weight": 5.0,
            "payment_method": "COD",
            "shipping_address": {"country": "ES"}
        }
        
        result = select_carrier(order)
        assert result == "tipsa"
    
    def test_select_carrier_express_shipping(self):
        """Test selection for express shipping."""
        order = {
            "order_id": "TEST-003",
            "weight": 5.0,
            "shipping_speed": "EXPRESS",
            "shipping_address": {"country": "ES"}
        }
        
        result = select_carrier(order)
        assert result == "dhl"
    
    def test_select_carrier_international(self):
        """Test selection for international shipping."""
        order = {
            "order_id": "TEST-004",
            "weight": 5.0,
            "shipping_address": {"country": "FR"}
        }
        
        result = select_carrier(order)
        assert result == "dhl"
    
    def test_select_carrier_default_domestic(self):
        """Test default selection for domestic standard shipping."""
        order = {
            "order_id": "TEST-005",
            "weight": 5.0,
            "shipping_address": {"country": "ES"}
        }
        
        result = select_carrier(order)
        assert result == "tipsa"
    
    def test_select_carrier_empty_order(self):
        """Test selection with empty order data."""
        order = {}
        
        result = select_carrier(order)
        assert result == "tipsa"  # Default fallback
    
    def test_select_carrier_missing_fields(self):
        """Test selection with missing fields."""
        order = {
            "order_id": "TEST-006"
            # Missing weight, address, etc.
        }
        
        result = select_carrier(order)
        assert result == "tipsa"  # Default fallback
    
    def test_select_carrier_priority_order(self):
        """Test that rules are applied in correct priority order."""
        # Heavy package should override express shipping
        order = {
            "order_id": "TEST-007",
            "weight": 25.0,
            "shipping_speed": "EXPRESS",
            "shipping_address": {"country": "ES"}
        }
        
        result = select_carrier(order)
        assert result == "tipsa"  # Weight rule takes priority
    
    def test_get_carrier_priority(self):
        """Test carrier priority ordering."""
        assert get_carrier_priority("tipsa") == 1
        assert get_carrier_priority("dhl") == 2
        assert get_carrier_priority("ontime") == 3
        assert get_carrier_priority("ups") == 4
        assert get_carrier_priority("unknown") == 5
    
    def test_validate_carrier_selection_tipsa_domestic(self):
        """Test validation for TIPSA domestic selection."""
        order = {
            "weight": 10.0,
            "shipping_address": {"country": "ES"}
        }
        
        result = validate_carrier_selection(order, "tipsa")
        assert result is True
    
    def test_validate_carrier_selection_tipsa_international(self):
        """Test validation for TIPSA international selection (should be invalid)."""
        order = {
            "weight": 10.0,
            "shipping_address": {"country": "FR"}
        }
        
        result = validate_carrier_selection(order, "tipsa")
        assert result is False
    
    def test_validate_carrier_selection_dhl_international(self):
        """Test validation for DHL international selection."""
        order = {
            "weight": 10.0,
            "shipping_address": {"country": "FR"}
        }
        
        result = validate_carrier_selection(order, "dhl")
        assert result is True
    
    def test_validate_carrier_selection_dhl_express(self):
        """Test validation for DHL express selection."""
        order = {
            "weight": 10.0,
            "shipping_address": {"country": "ES"},
            "shipping_speed": "EXPRESS"
        }
        
        result = validate_carrier_selection(order, "dhl")
        assert result is True
    
    def test_validate_carrier_selection_ontime_domestic(self):
        """Test validation for OnTime domestic selection."""
        order = {
            "weight": 10.0,
            "shipping_address": {"country": "ES"}
        }
        
        result = validate_carrier_selection(order, "ontime")
        assert result is True
    
    def test_validate_carrier_selection_ups_international(self):
        """Test validation for UPS international selection."""
        order = {
            "weight": 10.0,
            "shipping_address": {"country": "FR"}
        }
        
        result = validate_carrier_selection(order, "ups")
        assert result is True
    
    def test_get_carrier_info_tipsa(self):
        """Test getting TIPSA carrier information."""
        info = get_carrier_info("tipsa")
        
        assert info["name"] == "TIPSA"
        assert "Spanish domestic carrier" in info["description"]
        assert "Heavy packages" in info["strengths"]
        assert info["max_weight"] == 30.0
        assert "ES" in info["countries"]
    
    def test_get_carrier_info_dhl(self):
        """Test getting DHL carrier information."""
        info = get_carrier_info("dhl")
        
        assert info["name"] == "DHL Express"
        assert "International express carrier" in info["description"]
        assert "International" in info["strengths"]
        assert info["max_weight"] == 70.0
        assert "*" in info["countries"]  # Worldwide
    
    def test_get_carrier_info_ontime(self):
        """Test getting OnTime carrier information."""
        info = get_carrier_info("ontime")
        
        assert info["name"] == "OnTime"
        assert "Alternative domestic carrier" in info["description"]
        assert "Cost-effective" in info["strengths"]
        assert info["max_weight"] == 25.0
        assert "ES" in info["countries"]
    
    def test_get_carrier_info_ups(self):
        """Test getting UPS carrier information."""
        info = get_carrier_info("ups")
        
        assert info["name"] == "UPS"
        assert "International and domestic carrier" in info["description"]
        assert "International" in info["strengths"]
        assert info["max_weight"] == 70.0
        assert "*" in info["countries"]  # Worldwide
    
    def test_get_carrier_info_unknown(self):
        """Test getting unknown carrier information."""
        info = get_carrier_info("unknown")
        
        assert info["name"] == "Unknown"
        assert info["description"] == "Unknown carrier"
        assert info["strengths"] == []
        assert info["max_weight"] == 0.0
        assert info["countries"] == []
