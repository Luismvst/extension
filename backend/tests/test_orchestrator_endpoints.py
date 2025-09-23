"""
Tests for orchestrator API endpoints.

This module tests the main orchestration endpoints with mocks
and validates CSV logging integration.
"""

import pytest
import asyncio
import tempfile
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.utils.csv_ops_logger import CSVOpsLogger
from app.core.unified_order_logger import UnifiedOrderLogger


class TestOrchestratorEndpoints:
    """Test orchestrator API endpoints."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_csv_logger(self, temp_dir):
        """Create a mock CSV logger."""
        return CSVOpsLogger(log_dir=temp_dir)
    
    @pytest.fixture
    def mock_order_logger(self, temp_dir):
        """Create a mock unified order logger."""
        csv_path = os.path.join(temp_dir, "orders_view.csv")
        return UnifiedOrderLogger(csv_path=csv_path)
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers for testing."""
        return {"Authorization": "Bearer test-token"}
    
    @pytest.mark.asyncio
    async def test_fetch_orders_from_mirakl_success(self, client, auth_headers, temp_dir):
        """Test successful fetch orders from Mirakl."""
        # Mock Mirakl adapter response
        mock_mirakl_response = {
            "orders": [
                {
                    "order_id": "MIR-001",
                    "status": "PENDING",
                    "customer_name": "Juan Pérez",
                    "customer_email": "juan@example.com",
                    "weight": 1.5,
                    "total_amount": 45.99,
                    "currency": "EUR",
                    "created_at": "2025-01-01T10:00:00Z",
                    "shipping_address": {
                        "street": "Calle Test 123",
                        "city": "Madrid",
                        "postal_code": "28001",
                        "country": "ES"
                    }
                },
                {
                    "order_id": "MIR-002",
                    "status": "PENDING",
                    "customer_name": "María García",
                    "customer_email": "maria@example.com",
                    "weight": 2.1,
                    "total_amount": 89.50,
                    "currency": "EUR",
                    "created_at": "2025-01-01T11:00:00Z",
                    "shipping_address": {
                        "street": "Avenida Test 456",
                        "city": "Barcelona",
                        "postal_code": "08001",
                        "country": "ES"
                    }
                }
            ]
        }
        
        with patch('app.api.orchestrator.mirakl_adapter.get_orders', 
                   return_value=mock_mirakl_response) as mock_get_orders, \
             patch('app.api.orchestrator.csv_ops_logger') as mock_csv_logger, \
             patch('app.api.orchestrator.unified_order_logger') as mock_order_logger:
            
            # Mock the CSV logger methods
            mock_csv_logger.log = AsyncMock()
            mock_order_logger.upsert_order = MagicMock()
            
            response = client.post(
                "/api/v1/orchestrator/fetch-orders",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["orders_fetched"] == 2
            assert "Fetched 2 orders from Mirakl" in data["message"]
            
            # Verify Mirakl adapter was called
            mock_get_orders.assert_called_once_with(status="PENDING", limit=100, offset=0)
            
            # Verify CSV logging was called
            assert mock_csv_logger.log.call_count == 3  # 2 individual + 1 overall
            assert mock_order_logger.upsert_order.call_count == 2
    
    @pytest.mark.asyncio
    async def test_fetch_orders_no_orders(self, client, auth_headers):
        """Test fetch orders when no orders are available."""
        mock_mirakl_response = {"orders": []}
        
        with patch('app.api.orchestrator.mirakl_adapter.get_orders', 
                   return_value=mock_mirakl_response) as mock_get_orders:
            
            response = client.post(
                "/api/v1/orchestrator/fetch-orders",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["orders_fetched"] == 0
            assert "No orders found to process" in data["message"]
    
    @pytest.mark.asyncio
    async def test_post_to_carrier_success(self, client, auth_headers, temp_dir):
        """Test successful post to carrier."""
        # Mock unified order logger to return pending orders
        mock_orders = [
            {
                "order_id": "MIR-001",
                "buyer_name": "Juan Pérez",
                "buyer_email": "juan@example.com",
                "weight_kg": 1.5,
                "total_amount": 45.99,
                "currency": "EUR",
                "shipping_address": json.dumps({
                    "street": "Calle Test 123",
                    "city": "Madrid",
                    "postal_code": "28001",
                    "country": "ES"
                }),
                "internal_state": "PENDING_POST"
            }
        ]
        
        # Mock carrier adapter response
        mock_carrier_response = {
            "shipments": [
                {
                    "expedition_id": "EXP-001",
                    "tracking_number": "TRK123456789",
                    "status": "CREATED",
                    "label_url": "https://example.com/label.pdf",
                    "cost": 5.99,
                    "created_at": "2025-01-01T12:00:00Z"
                }
            ]
        }
        
        with patch('app.api.orchestrator.unified_order_logger.get_all_orders', 
                   return_value=mock_orders) as mock_get_orders, \
             patch('app.api.orchestrator.CARRIER_ADAPTERS') as mock_adapters, \
             patch('app.api.orchestrator.csv_ops_logger') as mock_csv_logger, \
             patch('app.api.orchestrator.unified_order_logger') as mock_order_logger:
            
            # Mock carrier adapter
            mock_adapter = AsyncMock()
            mock_adapter.create_shipments_bulk = AsyncMock(return_value=mock_carrier_response)
            mock_adapter.carrier_name = "TIPSA"
            mock_adapters.__getitem__.return_value = mock_adapter
            
            # Mock CSV logger methods
            mock_csv_logger.log = AsyncMock()
            mock_order_logger.upsert_order = MagicMock()
            
            response = client.post(
                "/api/v1/orchestrator/post-to-carrier",
                json={"carrier": "tipsa"},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["orders_processed"] == 1
            assert data["shipments_created"] == 1
            assert "Successfully posted 1 orders to tipsa" in data["message"]
            
            # Verify carrier adapter was called
            mock_adapter.create_shipments_bulk.assert_called_once()
            
            # Verify CSV logging was called
            assert mock_csv_logger.log.call_count == 2  # 1 individual + 1 overall
            assert mock_order_logger.upsert_order.call_count == 1
    
    @pytest.mark.asyncio
    async def test_post_to_carrier_no_orders(self, client, auth_headers):
        """Test post to carrier when no pending orders are available."""
        with patch('app.api.orchestrator.unified_order_logger.get_all_orders', 
                   return_value=[]) as mock_get_orders:
            
            response = client.post(
                "/api/v1/orchestrator/post-to-carrier",
                json={"carrier": "tipsa"},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["orders_processed"] == 0
            assert data["shipments_created"] == 0
            assert "No pending orders found" in data["message"]
    
    @pytest.mark.asyncio
    async def test_post_to_carrier_unsupported_carrier(self, client, auth_headers):
        """Test post to carrier with unsupported carrier."""
        response = client.post(
            "/api/v1/orchestrator/post-to-carrier",
            json={"carrier": "unsupported"},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported carrier: unsupported" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_push_tracking_to_mirakl_success(self, client, auth_headers):
        """Test successful push tracking to Mirakl."""
        # Mock Mirakl adapter response
        mock_mirakl_response = {
            "updated_orders": [
                {
                    "order_id": "MIR-001",
                    "tracking_number": "TRK123456789",
                    "status": "SHIPPED"
                }
            ]
        }
        
        with patch('app.api.orchestrator.mirakl_adapter.update_tracking_bulk', 
                   return_value=mock_mirakl_response) as mock_update_tracking, \
             patch('app.api.orchestrator.csv_ops_logger') as mock_csv_logger, \
             patch('app.api.orchestrator.unified_order_logger') as mock_order_logger:
            
            # Mock CSV logger methods
            mock_csv_logger.log = AsyncMock()
            mock_order_logger.get_all_orders = MagicMock(return_value=[
                {
                    "order_id": "MIR-001",
                    "tracking_number": "TRK123456789",
                    "internal_state": "POSTED"
                }
            ])
            mock_order_logger.upsert_order = MagicMock()
            
            response = client.post(
                "/api/v1/orchestrator/push-tracking-to-mirakl",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["orders_updated"] == 1
            assert "Successfully updated 1 orders in Mirakl" in data["message"]
            
            # Verify Mirakl adapter was called
            mock_update_tracking.assert_called_once()
            
            # Verify CSV logging was called
            assert mock_csv_logger.log.call_count == 2  # 1 individual + 1 overall
    
    @pytest.mark.asyncio
    async def test_get_orders_view(self, client, auth_headers):
        """Test getting orders view."""
        mock_orders = [
            {
                "order_id": "MIR-001",
                "marketplace": "mirakl",
                "buyer_name": "Juan Pérez",
                "buyer_email": "juan@example.com",
                "total_amount": 45.99,
                "currency": "EUR",
                "carrier_code": "tipsa",
                "carrier_name": "TIPSA",
                "tracking_number": "TRK123456789",
                "internal_state": "POSTED",
                "created_at": "2025-01-01T10:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        ]
        
        with patch('app.api.orchestrator.unified_order_logger.get_all_orders', 
                   return_value=mock_orders) as mock_get_orders:
            
            response = client.get(
                "/api/v1/orchestrator/orders-view",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["orders"]) == 1
            assert data["orders"][0]["order_id"] == "MIR-001"
            assert data["orders"][0]["marketplace"] == "mirakl"
            assert data["orders"][0]["buyer_name"] == "Juan Pérez"
    
    @pytest.mark.asyncio
    async def test_get_orders_view_with_filters(self, client, auth_headers):
        """Test getting orders view with filters."""
        mock_orders = [
            {
                "order_id": "MIR-001",
                "marketplace": "mirakl",
                "carrier_code": "tipsa",
                "internal_state": "POSTED"
            },
            {
                "order_id": "MIR-002",
                "marketplace": "mirakl",
                "carrier_code": "seur",
                "internal_state": "PENDING_POST"
            }
        ]
        
        with patch('app.api.orchestrator.unified_order_logger.get_all_orders', 
                   return_value=mock_orders) as mock_get_orders:
            
            # Test filtering by state
            response = client.get(
                "/api/v1/orchestrator/orders-view?state=POSTED",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["orders"]) == 1
            assert data["orders"][0]["order_id"] == "MIR-001"
            
            # Test filtering by carrier
            response = client.get(
                "/api/v1/orchestrator/orders-view?carrier=tipsa",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["orders"]) == 1
            assert data["orders"][0]["order_id"] == "MIR-001"
