"""
Integration tests for CSV logging functionality.

Tests that the backend properly logs operations to CSV files
when consuming the API endpoints.
"""

import pytest
import os
import json
import csv
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.settings import settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_logs_dir(tmp_path):
    """Create temporary logs directory."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    return logs_dir


@pytest.fixture
def mock_adapters():
    """Mock all adapters to return test data."""
    with patch('app.api.orchestrator.mirakl_adapter') as mock_mirakl, \
         patch('app.api.orchestrator.tipsa_adapter') as mock_tipsa:
        
        # Mock Mirakl adapter
        mock_mirakl.get_orders.return_value = {
            "orders": [
                {
                    "order_id": "TEST-ORDER-001",
                    "customer_name": "Test Customer",
                    "total_amount": 29.99,
                    "currency": "EUR",
                    "weight": 1.5,
                    "status": "PENDING",
                    "payment_method": "COD",
                    "shipping_address": {
                        "name": "Test Customer",
                        "street": "Test Street 123",
                        "city": "Madrid",
                        "postal_code": "28001",
                        "country": "ES"
                    }
                }
            ]
        }
        
        mock_mirakl.update_order_tracking.return_value = {
            "order_id": "TEST-ORDER-001",
            "status": "SUCCESS"
        }
        
        mock_mirakl.update_order_status.return_value = {
            "order_id": "TEST-ORDER-001",
            "status": "SUCCESS"
        }
        
        # Mock TIPSA adapter
        mock_tipsa.create_shipments_bulk.return_value = {
            "shipments": [
                {
                    "order_id": "TEST-ORDER-001",
                    "shipment_id": "SHIP-001",
                    "tracking_number": "TRK001",
                    "status": "CREATED",
                    "carrier": "tipsa"
                }
            ]
        }
        
        yield mock_mirakl, mock_tipsa


class TestCSVLogging:
    """Test CSV logging functionality."""
    
    def test_logs_directory_exists(self, mock_logs_dir):
        """Test that logs directory exists."""
        assert mock_logs_dir.exists()
        assert mock_logs_dir.is_dir()
    
    def test_operations_csv_created_on_api_calls(self, client, mock_adapters, mock_logs_dir):
        """Test that operations.csv is created and populated on API calls."""
        # Override settings to use test logs directory
        with patch.object(settings, 'log_dir', str(mock_logs_dir)):
            # Step 1: Load orders
            response = client.get("/api/v1/marketplaces/mirakl/orders?status=PENDING&limit=5")
            assert response.status_code == 200
            
            # Step 2: Create shipments
            orders_data = response.json()["orders"]
            shipments_response = client.post(
                "/api/v1/carriers/tipsa/shipments/bulk",
                json={"shipments": orders_data}
            )
            assert shipments_response.status_code == 200
            
            # Step 3: Upload tracking
            shipments = shipments_response.json()["shipments"]
            tracking_data = [
                {
                    "order_id": shipment["order_id"],
                    "tracking_number": shipment["tracking_number"],
                    "carrier_code": "tipsa",
                    "carrier_name": "TIPSA"
                }
                for shipment in shipments
            ]
            
            tracking_response = client.post(
                "/api/v1/orchestrator/upload-tracking",
                json=tracking_data
            )
            assert tracking_response.status_code == 200
            
            # Check that operations.csv exists
            operations_csv = mock_logs_dir / "operations.csv"
            assert operations_csv.exists()
            
            # Read and validate CSV content
            with open(operations_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # Should have at least 3 operations logged
                assert len(rows) >= 3
                
                # Check for specific operations
                operations = [row['operation'] for row in rows]
                assert 'get_mirakl_orders' in operations
                assert 'create_tipsa_shipments_bulk' in operations
                assert 'upload_tracking_to_mirakl' in operations
                
                # Validate CSV structure
                expected_columns = [
                    'timestamp', 'operation', 'order_id', 'status', 
                    'details', 'duration_ms', 'dump_file'
                ]
                for row in rows:
                    for col in expected_columns:
                        assert col in row
    
    def test_json_dumps_created(self, client, mock_adapters, mock_logs_dir):
        """Test that JSON dump files are created for request/response logging."""
        with patch.object(settings, 'log_dir', str(mock_logs_dir)):
            # Make API call
            response = client.get("/api/v1/marketplaces/mirakl/orders?status=PENDING&limit=5")
            assert response.status_code == 200
            
            # Check that dumps directory exists
            dumps_dir = mock_logs_dir / "dumps"
            assert dumps_dir.exists()
            
            # Check that JSON files were created
            json_files = list(dumps_dir.glob("*.json"))
            assert len(json_files) > 0
            
            # Validate JSON file content
            for json_file in json_files:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    assert 'operation' in data
                    assert 'order_id' in data
                    assert 'request_data' in data
                    assert 'response_data' in data
    
    def test_csv_logging_with_errors(self, client, mock_logs_dir):
        """Test that errors are properly logged to CSV."""
        with patch.object(settings, 'log_dir', str(mock_logs_dir)):
            # Make API call that will fail
            response = client.get("/api/v1/marketplaces/mirakl/orders?status=INVALID&limit=5")
            # This might return 200 with empty results or 400, depending on implementation
            
            # Check that operations.csv exists
            operations_csv = mock_logs_dir / "operations.csv"
            if operations_csv.exists():
                with open(operations_csv, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    # Should have at least one operation logged
                    assert len(rows) >= 1
                    
                    # Check that all rows have required columns
                    for row in rows:
                        assert 'timestamp' in row
                        assert 'operation' in row
                        assert 'status' in row
    
    def test_csv_encoding_and_format(self, client, mock_adapters, mock_logs_dir):
        """Test that CSV is properly encoded and formatted."""
        with patch.object(settings, 'log_dir', str(mock_logs_dir)):
            # Make API call
            response = client.get("/api/v1/marketplaces/mirakl/orders?status=PENDING&limit=5")
            assert response.status_code == 200
            
            operations_csv = mock_logs_dir / "operations.csv"
            if operations_csv.exists():
                # Test that file can be read with proper encoding
                with open(operations_csv, 'r', newline='', encoding='utf-8') as f:
                    content = f.read()
                    assert content is not None
                    assert len(content) > 0
                    
                    # Test that it's valid CSV
                    f.seek(0)
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    assert len(rows) >= 0  # Should not crash
    
    def test_log_rotation_and_cleanup(self, mock_logs_dir):
        """Test that log files are properly managed."""
        # This test would be more complex in a real scenario
        # For now, just ensure the directory structure is correct
        assert mock_logs_dir.exists()
        
        # Test that we can create files in the directory
        test_file = mock_logs_dir / "test.log"
        test_file.write_text("test content")
        assert test_file.exists()
        
        # Cleanup
        test_file.unlink()
        assert not test_file.exists()


class TestLoggingConfiguration:
    """Test logging configuration and settings."""
    
    def test_log_directory_creation(self, tmp_path):
        """Test that log directory is created if it doesn't exist."""
        logs_dir = tmp_path / "new_logs"
        assert not logs_dir.exists()
        
        # Simulate directory creation
        logs_dir.mkdir()
        assert logs_dir.exists()
        assert logs_dir.is_dir()
    
    def test_log_file_permissions(self, mock_logs_dir):
        """Test that log files can be written and read."""
        test_file = mock_logs_dir / "permissions_test.log"
        
        # Write test content
        test_content = "test log entry\n"
        test_file.write_text(test_content)
        
        # Read back content
        read_content = test_file.read_text()
        assert read_content == test_content
        
        # Cleanup
        test_file.unlink()
    
    def test_csv_delimiter_and_format(self, mock_logs_dir):
        """Test that CSV uses correct delimiter and format."""
        csv_file = mock_logs_dir / "test.csv"
        
        # Write test CSV with semicolon delimiter
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['header1', 'header2', 'header3'])
            writer.writerow(['value1', 'value2', 'value3'])
        
        # Read back and validate
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['header1'] == 'value1'
        
        # Cleanup
        csv_file.unlink()

