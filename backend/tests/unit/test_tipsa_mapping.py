"""
Unit tests for TIPSA mapping service
"""
import pytest
from datetime import datetime
from app.models.order import OrderStandard, OrderItem, Buyer, ShippingAddress, OrderTotals
from app.services.tipsa import (
    map_order_to_tipsa,
    map_orders_to_tipsa,
    generate_tipsa_csv,
    validate_tipsa_data,
    process_orders_mapping
)


@pytest.fixture
def sample_order():
    """Create a sample order for testing"""
    return OrderStandard(
        order_id="ORD-001",
        created_at=datetime(2024, 1, 15, 10, 0, 0),
        status="PENDING",
        items=[
            OrderItem(
                sku="SKU-123",
                name="Product A",
                qty=2,
                unit_price=25.50
            )
        ],
        buyer=Buyer(
            name="John Doe",
            email="john@example.com",
            phone="+34123456789"
        ),
        shipping=ShippingAddress(
            name="John Doe",
            address1="123 Main St",
            address2="Apt 4B",
            city="Madrid",
            postcode="28001",
            country="ES"
        ),
        totals=OrderTotals(
            goods=51.00,
            shipping=0

class TestMapOrderToTIPSA:
    """Test order mapping to TIPSA format"""
    
    def test_map_order_to_tipsa(self, sample_order):
        """Test mapping a single order to TIPSA format"""
        tipsa_order = map_order_to_tipsa(sample_order)
        
        assert tipsa_order.destinatario == "John Doe"
        assert tipsa_order.direccion == "123 Main St, Apt 4B"
        assert tipsa_order.cp == "28001"
        assert tipsa_order.poblacion == "Madrid"
        assert tipsa_order.pais == "ES"
        assert tipsa_order.contacto == "John Doe"
        assert tipsa_order.telefono == "+34123456789"
        assert tipsa_order.email == "john@example.com"
        assert tipsa_order.referencia == "ORD-001"
        assert tipsa_order.peso == "1.0"
        assert tipsa_order.servicio == "ESTANDAR"
    
    def test_map_order_without_optional_fields(self, sample_order):
        """Test mapping order without optional fields"""
        # Remove optional fields
        sample_order.buyer.email = None
        sample_order.buyer.phone = None
        sample_order.shipping.address2 = None
        
        tipsa_order = map_order_to_tipsa(sample_order)
        
        assert tipsa_order.telefono == ""
        assert tipsa_order.email == ""
        assert tipsa_order.direccion == "123 Main St"
    
    def test_map_order_with_custom_service(self, sample_order):
        """Test mapping order with custom service"""
        tipsa_order = map_order_to_tipsa(sample_order, "URGENTE")
        
        assert tipsa_order.servicio == "URGENTE"


class TestMapOrdersToTIPSA:
    """Test mapping multiple orders to TIPSA format"""
    
    def test_map_multiple_orders(self, sample_order):
        """Test mapping multiple orders"""
        orders = [sample_order, sample_order]
        tipsa_orders = map_orders_to_tipsa(orders)
        
        assert len(tipsa_orders) == 2
        assert all(order.referencia == "ORD-001" for order in tipsa_orders)


class TestGenerateTIPSACSV:
    """Test TIPSA CSV generation"""
    
    def test_generate_csv_with_orders(self, sample_order):
        """Test generating CSV with orders"""
        csv_content = generate_tipsa_csv([sample_order])
        
        assert "destinatario;direccion;cp;poblacion;pais;contacto;telefono;email;referencia;peso;servicio" in csv_content
        assert "John Doe;123 Main St, Apt 4B;28001;Madrid;ES;John Doe;+34123456789;john@example.com;ORD-001;1.0;ESTANDAR" in csv_content
    
    def test_generate_csv_empty_orders(self):
        """Test generating CSV with empty orders list"""
        csv_content = generate_tipsa_csv([])
        
        assert csv_content == ""
    
    def test_generate_csv_with_custom_service(self, sample_order):
        """Test generating CSV with custom service"""
        csv_content = generate_tipsa_csv([sample_order], "URGENTE")
        
        assert "URGENTE" in csv_content


class TestValidateTIPSAData:
    """Test TIPSA data validation"""
    
    def test_validate_valid_data(self, sample_order):
        """Test validating valid TIPSA data"""
        tipsa_order = map_order_to_tipsa(sample_order)
        errors = validate_tipsa_data(tipsa_order)
        
        assert len(errors) == 0
    
    def test_validate_missing_required_fields(self):
        """Test validating data with missing required fields"""
        from app.models.order import TIPSAOrder
        
        tipsa_order = TIPSAOrder(
            destinatario="",
            direccion="123 Main St",
            cp="28001",
            poblacion="Madrid",
            pais="ES",
            contacto="John Doe",
            telefono="+34123456789",
            email="john@example.com",
            referencia="ORD-001",
            peso="1.0",
            servicio="ESTANDAR"
        )
        
        errors = validate_tipsa_data(tipsa_order)
        
        assert "Destinatario is required" in errors
    
    def test_validate_invalid_postal_code(self, sample_order):
        """Test validating invalid postal code"""
        tipsa_order = map_order_to_tipsa(sample_order)
        tipsa_order.cp = "invalid"
        
        errors = validate_tipsa_data(tipsa_order)
        
        assert "Invalid postal code format" in errors
    
    def test_validate_invalid_country_code(self, sample_order):
        """Test validating invalid country code"""
        tipsa_order = map_order_to_tipsa(sample_order)
        tipsa_order.pais = "SPAIN"
        
        errors = validate_tipsa_data(tipsa_order)
        
        assert "Invalid country code" in errors
    
    def test_validate_invalid_email(self, sample_order):
        """Test validating invalid email"""
        tipsa_order = map_order_to_tipsa(sample_order)
        tipsa_order.email = "invalid-email"
        
        errors = validate_tipsa_data(tipsa_order)
        
        assert "Invalid email format" in errors
    
    def test_validate_invalid_phone(self, sample_order):
        """Test validating invalid phone"""
        tipsa_order = map_order_to_tipsa(sample_order)
        tipsa_order.telefono = "invalid-phone"
        
        errors = validate_tipsa_data(tipsa_order)
        
        assert "Invalid phone format" in errors
    
    def test_validate_invalid_weight(self, sample_order):
        """Test validating invalid weight"""
        tipsa_order = map_order_to_tipsa(sample_order)
        tipsa_order.peso = "invalid-weight"
        
        errors = validate_tipsa_data(tipsa_order)
        
        assert "Invalid weight format" in errors


class TestProcessOrdersMapping:
    """Test order mapping processing"""
    
    def test_process_csv_mapping(self, sample_order):
        """Test processing CSV mapping"""
        response = process_orders_mapping([sample_order], "csv", "ESTANDAR")
        
        assert response.success is True
        assert response.format == "csv"
        assert response.count == 1
        assert len(response.errors) == 0
        assert "destinatario;direccion" in response.data
    
    def test_process_json_mapping(self, sample_order):
        """Test processing JSON mapping"""
        response = process_orders_mapping([sample_order], "json", "ESTANDAR")
        
        assert response.success is True
        assert response.format == "json"
        assert response.count == 1
        assert len(response.errors) == 0
        assert "destinatario" in response.data
    
    def test_process_invalid_format(self, sample_order):
        """Test processing with invalid format"""
        response = process_orders_mapping([sample_order], "invalid", "ESTANDAR")
        
        assert response.success is False
        assert "Unsupported format: invalid" in response.errors
    
    def test_process_empty_orders(self):
        """Test processing empty orders list"""
        response = process_orders_mapping([], "csv", "ESTANDAR")
        
        assert response.success is True
        assert response.data == ""
        assert response.count == 0
