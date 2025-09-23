"""
Tests for CSV logging functionality.

This module tests the CSV operations logger and unified order logger
to ensure proper logging and data integrity.
"""

import pytest
import asyncio
import tempfile
import os
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from app.utils.csv_ops_logger import CSVOpsLogger
from app.core.unified_order_logger import UnifiedOrderLogger


class TestCSVOpsLogger:
    """Test the CSV operations logger."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def csv_logger(self, temp_dir):
        """Create a CSV logger instance for testing."""
        return CSVOpsLogger(log_dir=temp_dir)
    
    @pytest.mark.asyncio
    async def test_csv_file_initialization(self, csv_logger, temp_dir):
        """Test that CSV file is initialized with correct headers."""
        csv_file = Path(temp_dir) / "operations.csv"
        
        # Wait for async initialization
        await asyncio.sleep(0.1)
        
        assert csv_file.exists()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected_headers = [
                'timestamp_iso', 'scope', 'action', 'order_id', 'carrier',
                'marketplace', 'status', 'message', 'duration_ms', 'meta_json'
            ]
            assert headers == expected_headers
    
    @pytest.mark.asyncio
    async def test_log_operation(self, csv_logger, temp_dir):
        """Test logging a single operation."""
        await csv_logger.log(
            scope="test",
            action="test_action",
            order_id="TEST-001",
            carrier="tipsa",
            marketplace="mirakl",
            status="OK",
            message="Test operation",
            duration_ms=100,
            meta={"test": "data"}
        )
        
        csv_file = Path(temp_dir) / "operations.csv"
        assert csv_file.exists()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            row = rows[0]
            
            assert row['scope'] == "test"
            assert row['action'] == "test_action"
            assert row['order_id'] == "TEST-001"
            assert row['carrier'] == "tipsa"
            assert row['marketplace'] == "mirakl"
            assert row['status'] == "OK"
            assert row['message'] == "Test operation"
            assert row['duration_ms'] == "100"
            
            # Check meta_json
            meta = json.loads(row['meta_json'])
            assert meta == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_get_operations_with_filters(self, csv_logger, temp_dir):
        """Test getting operations with various filters."""
        # Log multiple operations
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
            status="OK"
        )
        
        await csv_logger.log(
            scope="mirakl",
            action="fetch_order",
            order_id="ORDER-003",
            marketplace="mirakl",
            status="ERROR"
        )
        
        # Test filtering by scope
        mirakl_ops = await csv_logger.get_operations(scope="mirakl")
        assert len(mirakl_ops) == 2
        
        # Test filtering by action
        fetch_ops = await csv_logger.get_operations(action="fetch_order")
        assert len(fetch_ops) == 2
        
        # Test filtering by status
        error_ops = await csv_logger.get_operations(status="ERROR")
        assert len(error_ops) == 1
        
        # Test filtering by scope and action
        mirakl_fetch_ops = await csv_logger.get_operations(scope="mirakl", action="fetch_order")
        assert len(mirakl_fetch_ops) == 2
    
    @pytest.mark.asyncio
    async def test_export_csv(self, csv_logger, temp_dir):
        """Test CSV export functionality."""
        # Log some operations
        await csv_logger.log(
            scope="test",
            action="test_action",
            order_id="TEST-001",
            status="OK"
        )
        
        # Export CSV
        export_path = await csv_logger.export_csv()
        
        assert export_path.exists()
        assert export_path != Path(temp_dir) / "operations.csv"  # Different file
        
        # Check content
        with open(export_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['order_id'] == "TEST-001"


class TestUnifiedOrderLogger:
    """Test the unified order logger."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def order_logger(self, temp_dir):
        """Create a unified order logger instance for testing."""
        csv_path = os.path.join(temp_dir, "orders_view.csv")
        return UnifiedOrderLogger(csv_path=csv_path)
    
    def test_csv_file_initialization(self, order_logger, temp_dir):
        """Test that CSV file is initialized with correct headers."""
        csv_file = Path(temp_dir) / "orders_view.csv"
        
        assert csv_file.exists()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            # Check that all expected headers are present
            expected_headers = [
                "order_id", "marketplace", "buyer_email", "buyer_name",
                "total_amount", "currency", "shipping_address", "carrier_code",
                "carrier_name", "tracking_number", "label_url", "internal_state",
                "created_at", "updated_at", "error_message", "retry_count",
                "mirakl_tracking_updated", "mirakl_ship_updated", "reference",
                "consignee_name", "consignee_address", "consignee_city",
                "consignee_postal_code", "consignee_country", "consignee_contact",
                "consignee_phone", "packages", "weight_kg", "volume",
                "shipping_cost", "product_type", "cod_amount", "delayed_date",
                "observations", "destination_email", "package_type",
                "client_department", "return_conform", "order_date",
                "consignee_nif", "client_name", "return_flag", "client_code",
                "multi_reference"
            ]
            
            assert headers == expected_headers
    
    def test_upsert_order_new(self, order_logger, temp_dir):
        """Test creating a new order."""
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'buyer_email': 'test@example.com',
            'buyer_name': 'Test User',
            'total_amount': 50.0,
            'currency': 'EUR',
            'internal_state': 'PENDING_POST'
        })
        
        csv_file = Path(temp_dir) / "orders_view.csv"
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            row = rows[0]
            
            assert row['order_id'] == "ORDER-001"
            assert row['marketplace'] == "mirakl"
            assert row['buyer_email'] == "test@example.com"
            assert row['buyer_name'] == "Test User"
            assert row['total_amount'] == "50.0"
            assert row['currency'] == "EUR"
            assert row['internal_state'] == "PENDING_POST"
            assert row['created_at'] == row['updated_at']  # Should be the same for new orders
    
    def test_upsert_order_update(self, order_logger, temp_dir):
        """Test updating an existing order."""
        # Create initial order
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'buyer_email': 'test@example.com',
            'buyer_name': 'Test User',
            'internal_state': 'PENDING_POST'
        })
        
        # Update order
        order_logger.upsert_order("ORDER-001", {
            'carrier_code': 'tipsa',
            'carrier_name': 'TIPSA',
            'tracking_number': 'TRK123456',
            'internal_state': 'POSTED'
        })
        
        csv_file = Path(temp_dir) / "orders_view.csv"
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            row = rows[0]
            
            assert row['order_id'] == "ORDER-001"
            assert row['marketplace'] == "mirakl"  # Should remain
            assert row['buyer_email'] == "test@example.com"  # Should remain
            assert row['carrier_code'] == "tipsa"  # Should be updated
            assert row['carrier_name'] == "TIPSA"  # Should be updated
            assert row['tracking_number'] == "TRK123456"  # Should be updated
            assert row['internal_state'] == "POSTED"  # Should be updated
            assert row['created_at'] != row['updated_at']  # Should be different
    
    def test_get_order(self, order_logger, temp_dir):
        """Test getting a specific order."""
        # Create an order
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'buyer_email': 'test@example.com',
            'internal_state': 'PENDING_POST'
        })
        
        # Get the order
        order = order_logger.get_order("ORDER-001")
        
        assert order is not None
        assert order['order_id'] == "ORDER-001"
        assert order['marketplace'] == "mirakl"
        assert order['buyer_email'] == "test@example.com"
        assert order['internal_state'] == "PENDING_POST"
        
        # Get non-existent order
        non_existent = order_logger.get_order("ORDER-999")
        assert non_existent is None
    
    def test_get_orders_by_state(self, order_logger, temp_dir):
        """Test getting orders by internal state."""
        # Create orders with different states
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'internal_state': 'PENDING_POST'
        })
        
        order_logger.upsert_order("ORDER-002", {
            'marketplace': 'mirakl',
            'internal_state': 'POSTED'
        })
        
        order_logger.upsert_order("ORDER-003", {
            'marketplace': 'mirakl',
            'internal_state': 'PENDING_POST'
        })
        
        # Get orders by state
        pending_orders = order_logger.get_orders_by_state('PENDING_POST')
        assert len(pending_orders) == 2
        
        posted_orders = order_logger.get_orders_by_state('POSTED')
        assert len(posted_orders) == 1
        
        # Check order IDs
        pending_ids = [order['order_id'] for order in pending_orders]
        assert "ORDER-001" in pending_ids
        assert "ORDER-003" in pending_ids
        
        posted_ids = [order['order_id'] for order in posted_orders]
        assert "ORDER-002" in posted_ids
    
    def test_get_all_orders(self, order_logger, temp_dir):
        """Test getting all orders."""
        # Create multiple orders
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'internal_state': 'PENDING_POST'
        })
        
        order_logger.upsert_order("ORDER-002", {
            'marketplace': 'mirakl',
            'internal_state': 'POSTED'
        })
        
        # Get all orders
        all_orders = order_logger.get_all_orders()
        assert len(all_orders) == 2
        
        # Check that all orders are returned
        order_ids = [order['order_id'] for order in all_orders]
        assert "ORDER-001" in order_ids
        assert "ORDER-002" in order_ids
    
    def test_export_csv(self, order_logger, temp_dir):
        """Test CSV export functionality."""
        # Create an order
        order_logger.upsert_order("ORDER-001", {
            'marketplace': 'mirakl',
            'buyer_email': 'test@example.com',
            'internal_state': 'PENDING_POST'
        })
        
        # Export CSV
        export_path = order_logger.export_csv()
        
        assert os.path.exists(export_path)
        assert export_path != os.path.join(temp_dir, "orders_view.csv")  # Different file
        
        # Check content
        with open(export_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['order_id'] == "ORDER-001"
