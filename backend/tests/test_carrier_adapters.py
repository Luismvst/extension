"""
Unit tests for carrier adapters.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from app.adapters.carriers.ontime import OnTimeAdapter
from app.adapters.carriers.dhl import DHLAdapter
from app.adapters.carriers.ups import UPSAdapter


class TestOnTimeAdapter:
    """Test OnTime adapter."""
    
    @pytest.fixture
    def adapter(self):
        return OnTimeAdapter()
    
    @pytest.mark.asyncio
    async def test_create_shipment_mock(self, adapter):
        """Test create_shipment in mock mode."""
        order_data = {
            "order_id": "TEST-001",
            "weight": 2.5,
            "service_type": "standard"
        }
        
        result = await adapter._create_shipment_mock(order_data)
        
        assert "shipment_id" in result
        assert "tracking_number" in result
        assert "carrier" in result
        assert result["carrier"] == "ONTIME"
        assert result["shipment_id"].startswith("ONTIME-")
        assert result["tracking_number"].startswith("ONT")
    
    @pytest.mark.asyncio
    async def test_create_shipments_bulk_mock(self, adapter):
        """Test create_shipments_bulk in mock mode."""
        orders_data = [
            {"order_id": "TEST-001", "weight": 2.5},
            {"order_id": "TEST-002", "weight": 1.8}
        ]
        
        result = await adapter._create_shipments_bulk_mock(orders_data)
        
        assert "shipments" in result
        assert "total_created" in result
        assert "carrier" in result
        assert result["total_created"] == 2
        assert len(result["shipments"]) == 2
        assert result["carrier"] == "ONTIME"
    
    @pytest.mark.asyncio
    async def test_get_shipment_status_mock(self, adapter):
        """Test get_shipment_status in mock mode."""
        shipment_id = "ONTIME-12345"
        
        result = await adapter._get_shipment_status_mock(shipment_id)
        
        assert "shipment_id" in result
        assert "status" in result
        assert "carrier" in result
        assert result["shipment_id"] == shipment_id
        assert result["carrier"] == "ONTIME"
        assert result["status"] in ["CREATED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "EXCEPTION"]
    
    @pytest.mark.asyncio
    async def test_get_shipment_label_mock(self, adapter):
        """Test get_shipment_label in mock mode."""
        shipment_id = "ONTIME-12345"
        
        result = await adapter._get_shipment_label_mock(shipment_id)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        assert b"ONTIME SHIPPING LABEL" in result
        assert shipment_id.encode() in result


class TestDHLAdapter:
    """Test DHL adapter."""
    
    @pytest.fixture
    def adapter(self):
        return DHLAdapter()
    
    @pytest.mark.asyncio
    async def test_create_shipment_mock(self, adapter):
        """Test create_shipment in mock mode."""
        order_data = {
            "order_id": "TEST-001",
            "weight": 2.5,
            "service_type": "express"
        }
        
        result = await adapter._create_shipment_mock(order_data)
        
        assert "shipment_id" in result
        assert "tracking_number" in result
        assert "carrier" in result
        assert result["carrier"] == "DHL"
        assert result["shipment_id"].startswith("DHL-")
        assert result["tracking_number"].startswith("JD")
        assert result["service_type"] == "EXPRESS"
    
    @pytest.mark.asyncio
    async def test_create_shipments_bulk_mock(self, adapter):
        """Test create_shipments_bulk in mock mode."""
        orders_data = [
            {"order_id": "TEST-001", "weight": 2.5},
            {"order_id": "TEST-002", "weight": 1.8}
        ]
        
        result = await adapter._create_shipments_bulk_mock(orders_data)
        
        assert "shipments" in result
        assert "total_created" in result
        assert "carrier" in result
        assert result["total_created"] == 2
        assert len(result["shipments"]) == 2
        assert result["carrier"] == "DHL"
    
    @pytest.mark.asyncio
    async def test_get_shipment_status_mock(self, adapter):
        """Test get_shipment_status in mock mode."""
        shipment_id = "DHL-12345"
        
        result = await adapter._get_shipment_status_mock(shipment_id)
        
        assert "shipment_id" in result
        assert "status" in result
        assert "carrier" in result
        assert result["shipment_id"] == shipment_id
        assert result["carrier"] == "DHL"
        assert result["status"] in ["CREATED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "EXCEPTION"]
    
    @pytest.mark.asyncio
    async def test_get_shipment_label_mock(self, adapter):
        """Test get_shipment_label in mock mode."""
        shipment_id = "DHL-12345"
        
        result = await adapter._get_shipment_label_mock(shipment_id)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        assert b"DHL EXPRESS SHIPPING LABEL" in result
        assert shipment_id.encode() in result


class TestUPSAdapter:
    """Test UPS adapter."""
    
    @pytest.fixture
    def adapter(self):
        return UPSAdapter()
    
    @pytest.mark.asyncio
    async def test_create_shipment_mock(self, adapter):
        """Test create_shipment in mock mode."""
        order_data = {
            "order_id": "TEST-001",
            "weight": 2.5,
            "service_type": "ground"
        }
        
        result = await adapter._create_shipment_mock(order_data)
        
        assert "shipment_id" in result
        assert "tracking_number" in result
        assert "carrier" in result
        assert result["carrier"] == "UPS"
        assert result["shipment_id"].startswith("UPS-")
        assert result["tracking_number"].startswith("1Z")
        assert result["service_type"] == "GROUND"
    
    @pytest.mark.asyncio
    async def test_create_shipments_bulk_mock(self, adapter):
        """Test create_shipments_bulk in mock mode."""
        orders_data = [
            {"order_id": "TEST-001", "weight": 2.5},
            {"order_id": "TEST-002", "weight": 1.8}
        ]
        
        result = await adapter._create_shipments_bulk_mock(orders_data)
        
        assert "shipments" in result
        assert "total_created" in result
        assert "carrier" in result
        assert result["total_created"] == 2
        assert len(result["shipments"]) == 2
        assert result["carrier"] == "UPS"
    
    @pytest.mark.asyncio
    async def test_get_shipment_status_mock(self, adapter):
        """Test get_shipment_status in mock mode."""
        shipment_id = "UPS-12345"
        
        result = await adapter._get_shipment_status_mock(shipment_id)
        
        assert "shipment_id" in result
        assert "status" in result
        assert "carrier" in result
        assert result["shipment_id"] == shipment_id
        assert result["carrier"] == "UPS"
        assert result["status"] in ["CREATED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "EXCEPTION"]
    
    @pytest.mark.asyncio
    async def test_get_shipment_label_mock(self, adapter):
        """Test get_shipment_label in mock mode."""
        shipment_id = "UPS-12345"
        
        result = await adapter._get_shipment_label_mock(shipment_id)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        assert b"UPS SHIPPING LABEL" in result
        assert shipment_id.encode() in result
