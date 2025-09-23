"""
Tests for logs API endpoints.

This module tests the logs API endpoints to ensure proper
CSV export and data retrieval functionality.
"""

import pytest
import tempfile
import os
import csv
import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.utils.csv_ops_logger import CSVOpsLogger
from app.core.unified_order_logger import UnifiedOrderLogger


class TestLogsEndpoints:
    """Test logs API endpoints."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers for testing."""
        return {"Authorization": "Bearer test-token"}
    
    @pytest.mark.asyncio
    async def test_get_operations_logs(self, client, auth_headers, temp_dir):
        """Test getting operations logs."""
        # Create mock CSV operations logger
        csv_logger = CSVOpsLogger(log_dir=temp_dir)
        
        # Add some test operations
        await csv_logger.log(
            scope="mirakl",
            action="fetch_order",
            order_id="ORDER-001",
            marketplace="mirakl",
            status="OK",
            message="Order fetched successfully"
        )
        
        await csv_logger.log(
            scope="carrier",
            action="create_shipment",
            order_id="ORDER-002",
            carrier="tipsa",
            status="OK",
            message="Shipment created successfully"
        )
        
        with patch('app.api.logs.csv_ops_logger', csv_logger):
            response = client.get(
                "/api/v1/logs/operations",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["logs"]) == 2
            assert data["total"] == 2
            
            # Check first log entry
            first_log = data["logs"][0]
            assert first_log["scope"] == "mirakl"
            assert first_log["action"] == "fetch_order"
            assert first_log["order_id"] == "ORDER-001"
            assert first_log["marketplace"] == "mirakl"
            assert first_log["status"] == "OK"
    
    @pytest.mark.asyncio
    async def test_get_operations_logs_with_filters(self, client, auth_headers, temp_dir):
        """Test getting operations logs with filters."""
        # Create mock CSV operations logger
        csv_logger = CSVOpsLogger(log_dir=temp_dir)
        
        # Add test operations
        await csv_logger.log(
            scope="mirakl",
            action="fetch_order",
            order_id="ORDER-001",
            marketplace="mirakl",
            status="OK"
        )
        
        await csv_logger.log(
            scope="carrier",
            action="create_shipment",
            order_id="ORDER-002",
            carrier="tipsa",
            status="ERROR"
        )
        
        with patch('app.api.logs.csv_ops_logger', csv_logger):
            # Test filtering by scope
            response = client.get(
                "/api/v1/logs/operations?scope=mirakl",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["logs"]) == 1
            assert data["logs"][0]["scope"] == "mirakl"
            
            # Test filtering by status
            response = client.get(
                "/api/v1/logs/operations?status=ERROR",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["logs"]) == 1
            assert data["logs"][0]["status"] == "ERROR"
    
    @pytest.mark.asyncio
    async def test_get_orders_view_logs(self, client, auth_headers, temp_dir):
        """Test getting orders view logs."""
        # Create mock unified order logger
        csv_path = os.path.join(temp_dir, "orders_view.csv")
        order_logger = UnifiedOrderLogger(csv_path=csv_path)
        
        # Add test orders
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'buyer_name': 'Juan Pérez',
            'buyer_email': 'juan@example.com',
            'total_amount': 45.99,
            'currency': 'EUR',
            'carrier_code': 'tipsa',
            'carrier_name': 'TIPSA',
            'tracking_number': 'TRK123456789',
            'internal_state': 'POSTED'
        })
        
        order_logger.upsert_order("ORDER-002", {
            'marketplace': 'mirakl',
            'buyer_name': 'María García',
            'buyer_email': 'maria@example.com',
            'total_amount': 89.50,
            'currency': 'EUR',
            'carrier_code': 'seur',
            'carrier_name': 'SEUR',
            'internal_state': 'PENDING_POST'
        })
        
        with patch('app.api.logs.unified_order_logger', order_logger):
            response = client.get(
                "/api/v1/logs/orders-view",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["orders"]) == 2
            assert data["total"] == 2
            
            # Check first order
            first_order = data["orders"][0]
            assert first_order["order_id"] == "ORDER-001"
            assert first_order["marketplace"] == "mirakl"
            assert first_order["buyer_name"] == "Juan Pérez"
            assert first_order["carrier_code"] == "tipsa"
            assert first_order["internal_state"] == "POSTED"
    
    @pytest.mark.asyncio
    async def test_get_orders_view_logs_with_filters(self, client, auth_headers, temp_dir):
        """Test getting orders view logs with filters."""
        # Create mock unified order logger
        csv_path = os.path.join(temp_dir, "orders_view.csv")
        order_logger = UnifiedOrderLogger(csv_path=csv_path)
        
        # Add test orders
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'carrier_code': 'tipsa',
            'internal_state': 'POSTED'
        })
        
        order_logger.upsert_order("ORDER-002", {
            'marketplace': 'mirakl',
            'carrier_code': 'seur',
            'internal_state': 'PENDING_POST'
        })
        
        with patch('app.api.logs.unified_order_logger', order_logger):
            # Test filtering by state
            response = client.get(
                "/api/v1/logs/orders-view?state=POSTED",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["orders"]) == 1
            assert data["orders"][0]["order_id"] == "ORDER-001"
            assert data["orders"][0]["internal_state"] == "POSTED"
            
            # Test filtering by carrier
            response = client.get(
                "/api/v1/logs/orders-view?carrier=tipsa",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["orders"]) == 1
            assert data["orders"][0]["order_id"] == "ORDER-001"
            assert data["orders"][0]["carrier_code"] == "tipsa"
    
    @pytest.mark.asyncio
    async def test_export_operations_csv(self, client, auth_headers, temp_dir):
        """Test exporting operations CSV."""
        # Create mock CSV operations logger
        csv_logger = CSVOpsLogger(log_dir=temp_dir)
        
        # Add test operations
        await csv_logger.log(
            scope="mirakl",
            action="fetch_order",
            order_id="ORDER-001",
            marketplace="mirakl",
            status="OK",
            message="Order fetched successfully"
        )
        
        with patch('app.api.logs.csv_ops_logger', csv_logger):
            response = client.get(
                "/api/v1/logs/exports/operations.csv",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            
            # Check CSV content
            content = response.text
            lines = content.strip().split('\n')
            
            # Should have header + 1 data row
            assert len(lines) == 2
            
            # Check header
            header = lines[0].split(',')
            expected_headers = [
                'timestamp_iso', 'scope', 'action', 'order_id', 'carrier',
                'marketplace', 'status', 'message', 'duration_ms', 'meta_json'
            ]
            assert header == expected_headers
            
            # Check data row
            data_row = lines[1].split(',')
            assert data_row[1] == "mirakl"  # scope
            assert data_row[2] == "fetch_order"  # action
            assert data_row[3] == "ORDER-001"  # order_id
            assert data_row[5] == "mirakl"  # marketplace
            assert data_row[6] == "OK"  # status
    
    @pytest.mark.asyncio
    async def test_export_orders_view_csv(self, client, auth_headers, temp_dir):
        """Test exporting orders view CSV."""
        # Create mock unified order logger
        csv_path = os.path.join(temp_dir, "orders_view.csv")
        order_logger = UnifiedOrderLogger(csv_path=csv_path)
        
        # Add test order
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'buyer_name': 'Juan Pérez',
            'buyer_email': 'juan@example.com',
            'total_amount': 45.99,
            'currency': 'EUR',
            'carrier_code': 'tipsa',
            'carrier_name': 'TIPSA',
            'tracking_number': 'TRK123456789',
            'internal_state': 'POSTED'
        })
        
        with patch('app.api.logs.unified_order_logger', order_logger):
            response = client.get(
                "/api/v1/logs/exports/orders-view.csv",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            
            # Check CSV content
            content = response.text
            lines = content.strip().split('\n')
            
            # Should have header + 1 data row
            assert len(lines) == 2
            
            # Check header
            header = lines[0].split(',')
            assert "order_id" in header
            assert "marketplace" in header
            assert "buyer_name" in header
            assert "carrier_code" in header
            assert "internal_state" in header
            
            # Check data row
            data_row = lines[1].split(',')
            assert data_row[0] == "ORDER-001"  # order_id
    
    @pytest.mark.asyncio
    async def test_get_logs_stats(self, client, auth_headers, temp_dir):
        """Test getting logs statistics."""
        # Create mock CSV operations logger
        csv_logger = CSVOpsLogger(log_dir=temp_dir)
        
        # Add test operations
        await csv_logger.log(
            scope="mirakl",
            action="fetch_order",
            order_id="ORDER-001",
            marketplace="mirakl",
            status="OK"
        )
        
        await csv_logger.log(
            scope="carrier",
            action="create_shipment",
            order_id="ORDER-002",
            carrier="tipsa",
            status="ERROR"
        )
        
        # Create mock unified order logger
        csv_path = os.path.join(temp_dir, "orders_view.csv")
        order_logger = UnifiedOrderLogger(csv_path=csv_path)
        
        # Add test orders
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'carrier_code': 'tipsa',
            'internal_state': 'POSTED'
        })
        
        order_logger.upsert_order("ORDER-002", {
            'marketplace': 'mirakl',
            'carrier_code': 'seur',
            'internal_state': 'PENDING_POST'
        })
        
        with patch('app.api.logs.csv_ops_logger', csv_logger), \
             patch('app.api.logs.unified_order_logger', order_logger):
            
            response = client.get(
                "/api/v1/logs/stats",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert "stats" in data
            assert "operations" in data["stats"]
            assert "orders" in data["stats"]
            assert "files" in data["stats"]
            
            # Check operations stats
            ops_stats = data["stats"]["operations"]
            assert ops_stats["total_logs"] == 2
            assert ops_stats["success_rate"] == 50.0
            assert ops_stats["error_rate"] == 50.0
            
            # Check orders stats
            orders_stats = data["stats"]["orders"]
            assert orders_stats["total_orders"] == 2
            assert "POSTED" in orders_stats["by_state"]
            assert "PENDING_POST" in orders_stats["by_state"]
            assert "tipsa" in orders_stats["by_carrier"]
            assert "seur" in orders_stats["by_carrier"]
