"""
Unit tests for Pydantic models
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models.order import (
    OrderItem, Buyer, ShippingAddress, OrderTotals, OrderStandard,
    TIPSAOrder, OnTimeOrder, MappingRequest, MappingResponse
)


class TestOrderItem:
    """Test OrderItem model"""
    
    def test_valid_order_item(self):
        """Test creating valid order item"""
        item = OrderItem(
            sku="SKU-123",
            name="Product A",
            qty=2,
            unit_price=25.50
        )
        
        assert item.sku == "SKU-123"
        assert item.name == "Product A"
        assert item.qty == 2
        assert item.unit_price == 25.50
    
    def test_invalid_quantity(self):
        """Test invalid quantity"""
        with pytest.raises(ValidationError) as exc_info:
            OrderItem(
                sku="SKU-123",
                name="Product A",
                qty=0,
                unit_price=25.50
            )
        
        assert "Quantity must be positive" in str(exc_info.value)
    
    def test_invalid_unit_price(self):
        """Test invalid unit price"""
        with pytest.raises(ValidationError) as exc_info:
            OrderItem(
                sku="SKU-123",
                name="Product A",
                qty=2,
                unit_price=-10.0
            )
        
        assert "Unit price must be positive" in str(exc_info.value)
    
    def test_price_rounding(self):
        """Test price rounding"""
        item = OrderItem(
            sku="SKU-123",
            name="Product A",
            qty=1,
            unit_price=25.555
        )
        
        assert item.unit_price == 25.56


class TestBuyer:
    """Test Buyer model"""
    
    def test_valid_buyer(self):
        """Test creating valid buyer"""
        buyer = Buyer(
            name="John Doe",
            email="john@example.com",
            phone="+34123456789"
        )
        
        assert buyer.name == "John Doe"
        assert buyer.email == "john@example.com"
        assert buyer.phone == "+34123456789"
    
    def test_buyer_without_optional_fields(self):
        """Test buyer without optional fields"""
        buyer = Buyer(name="John Doe")
        
        assert buyer.name == "John Doe"
        assert buyer.email is None
        assert buyer.phone is None
    
    def test_invalid_email(self):
        """Test invalid email format"""
        with pytest.raises(ValidationError) as exc_info:
            Buyer(
                name="John Doe",
                email="invalid-email"
            )
        
        assert "Invalid email format" in str(exc_info.value)


class TestShippingAddress:
    """Test ShippingAddress model"""
    
    def test_valid_shipping_address(self):
        """Test creating valid shipping address"""
        address = ShippingAddress(
            name="John Doe",
            address1="123 Main St",
            address2="Apt 4B",
            city="Madrid",
            postcode="28001",
            country="es"
        )
        
        assert address.name == "John Doe"
        assert address.address1 == "123 Main St"
        assert address.address2 == "Apt 4B"
        assert address.city == "Madrid"
        assert address.postcode == "28001"
        assert address.country == "ES"  # Should be uppercase
    
    def test_shipping_address_without_optional_fields(self):
        """Test shipping address without optional fields"""
        address = ShippingAddress(
            name="John Doe",
            address1="123 Main St",
            city="Madrid",
            postcode="28001",
            country="ES"
        )
        
        assert address.address2 is None


class TestOrderTotals:
    """Test OrderTotals model"""
    
    def test_valid_order_totals(self):
        """Test creating valid order totals"""
        totals = OrderTotals(
            goods=51.00,
            shipping=5.50
        )
        
        assert totals.goods == 51.00
        assert totals.shipping == 5.50
    
    def test_order_totals_without_shipping(self):
        """Test order totals without shipping"""
        totals = OrderTotals(goods=51.00)
        
        assert totals.goods == 51.00
        assert totals.shipping == 0
    
    def test_negative_goods_total(self):
        """Test negative goods total"""
        with pytest.raises(ValidationError) as exc_info:
            OrderTotals(goods=-10.0)
        
        assert "Goods total must be non-negative" in str(exc_info.value)
    
    def test_amount_rounding(self):
        """Test amount rounding"""
        totals = OrderTotals(goods=51.555, shipping=5.123)
        
        assert totals.goods == 51.56
        assert totals.shipping == 5.12


class TestOrderStandard:
    """Test OrderStandard model"""
    
    def test_valid_order_standard(self):
        """Test creating valid order standard"""
        order = OrderStandard(
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
            buyer=Buyer(name="John Doe"),
            shipping=ShippingAddress(
                name="John Doe",
                address1="123 Main St",
                city="Madrid",
                postcode="28001",
                country="ES"
            ),
            totals=OrderTotals(goods=51.00)
        )
        
        assert order.order_id == "ORD-001"
        assert order.status == "PENDING"
        assert len(order.items) == 1
    
    def test_invalid_status(self):
        """Test invalid status"""
        with pytest.raises(ValidationError) as exc_info:
            OrderStandard(
                order_id="ORD-001",
                created_at=datetime(2024, 1, 15, 10, 0, 0),
                status="INVALID",
                items=[
                    OrderItem(
                        sku="SKU-123",
                        name="Product A",
                        qty=2,
                        unit_price=25.50
                    )
                ],
                buyer=Buyer(name="John Doe"),
                shipping=ShippingAddress(
                    name="John Doe",
                    address1="123 Main St",
                    city="Madrid",
                    postcode="28001",
                    country="ES"
                ),
                totals=OrderTotals(goods=51.00)
            )
        
        assert "Status must be one of" in str(exc_info.value)
    
    def test_status_case_insensitive(self):
        """Test status case insensitive conversion"""
        order = OrderStandard(
            order_id="ORD-001",
            created_at=datetime(2024, 1, 15, 10, 0, 0),
            status="pending",
            items=[
                OrderItem(
                    sku="SKU-123",
                    name="Product A",
                    qty=2,
                    unit_price=25.50
                )
            ],
            buyer=Buyer(name="John Doe"),
            shipping=ShippingAddress(
                name="John Doe",
                address1="123 Main St",
                city="Madrid",
                postcode="28001",
                country="ES"
            ),
            totals=OrderTotals(goods=51.00)
        )
        
        assert order.status == "PENDING"
    
    def test_empty_items_list(self):
        """Test empty items list"""
        with pytest.raises(ValidationError) as exc_info:
            OrderStandard(
                order_id="ORD-001",
                created_at=datetime(2024, 1, 15, 10, 0, 0),
                status="PENDING",
                items=[],
                buyer=Buyer(name="John Doe"),
                shipping=ShippingAddress(
                    name="John Doe",
                    address1="123 Main St",
                    city="Madrid",
                    postcode="28001",
                    country="ES"
                ),
                totals=OrderTotals(goods=51.00)
            )
        
        assert "At least one item is required" in str(exc_info.value)


class TestTIPSAOrder:
    """Test TIPSAOrder model"""
    
    def test_valid_tipsa_order(self):
        """Test creating valid TIPSA order"""
        tipsa_order = TIPSAOrder(
            destinatario="John Doe",
            direccion="123 Main St",
            cp="28001",
            poblacion="Madrid",
            pais="es",
            contacto="John Doe",
            telefono="+34123456789",
            email="john@example.com",
            referencia="ORD-001",
            peso="1.0",
            servicio="ESTANDAR"
        )
        
        assert tipsa_order.destinatario == "John Doe"
        assert tipsa_order.pais == "ES"  # Should be uppercase


class TestMappingRequest:
    """Test MappingRequest model"""
    
    def test_valid_mapping_request(self):
        """Test creating valid mapping request"""
        order = OrderStandard(
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
            buyer=Buyer(name="John Doe"),
            shipping=ShippingAddress(
                name="John Doe",
                address1="123 Main St",
                city="Madrid",
                postcode="28001",
                country="ES"
            ),
            totals=OrderTotals(goods=51.00)
        )
        
        request = MappingRequest(
            orders=[order],
            format="csv",
            service="ESTANDAR"
        )
        
        assert len(request.orders) == 1
        assert request.format == "csv"
        assert request.service == "ESTANDAR"
    
    def test_empty_orders_list(self):
        """Test mapping request with empty orders list"""
        with pytest.raises(ValidationError) as exc_info:
            MappingRequest(orders=[])
        
        assert "At least one order is required" in str(exc_info.value)


class TestMappingResponse:
    """Test MappingResponse model"""
    
    def test_valid_mapping_response(self):
        """Test creating valid mapping response"""
        response = MappingResponse(
            success=True,
            data="destinatario;direccion\nJohn Doe;123 Main St",
            format="csv",
            count=1,
            errors=[]
        )
        
        assert response.success is True
        assert response.data == "destinatario;direccion\nJohn Doe;123 Main St"
        assert response.format == "csv"
        assert response.count == 1
        assert len(response.errors) == 0
