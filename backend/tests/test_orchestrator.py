"""
Unit tests for orchestrator endpoints.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app


class TestOrchestratorEndpoints:
    """Test orchestrator API endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth(self):
        with patch("app.core.auth.get_current_user") as mock:
            mock.return_value = {"user_id": "test_user", "username": "test"}
            yield mock
    
    @pytest.fixture
    def mock_adapters(self):
        with patch("app.api.orchestrator.mirakl_adapter") as mock_mirakl, \
             patch("app.api.orchestrator.CARRIER_ADAPTERS") as mock_carriers:
            
            # Mock Mirakl adapter
            mock_mirakl.get_orders.return_value = {
                "orders": [
                    {
                        "order_id": "MIR-001",
                        "weight": 2.5,
                        "shipping_address": {"country": "ES"},
                        "status": "PENDING"
                    },
                    {
                        "order_id": "MIR-002",
                        "weight": 25.0,
                        "shipping_address": {"country": "ES"},
                        "status": "PENDING"
                    }
                ]
            }
            
            # Mock carrier adapters
            mock_tipsa = AsyncMock()
            mock_tipsa.create_shipments_bulk.return_value = {
                "shipments": [
                    {
                        "shipment_id": "TIPSA-001",
                        "tracking_number": "1Z123456789",
                        "carrier": "TIPSA",
                        "order_id": "MIR-002"
                    }
                ]
            }
            
            mock_dhl = AsyncMock()
            mock_dhl.create_shipments_bulk.return_value = {
                "shipments": [
                    {
                        "shipment_id": "DHL-001",
                        "tracking_number": "JD123456789",
                        "carrier": "DHL",
                        "order_id": "MIR-001"
                    }
                ]
            }
            
            mock_carriers.return_value = {
                "tipsa": mock_tipsa,
                "dhl": mock_dhl
            }
            
            yield {
                "mirakl": mock_mirakl,
                "tipsa": mock_tipsa,
                "dhl": mock_dhl
            }
    
    def test_load_orders_endpoint(self, client, mock_auth, mock_adapters):
        """Test load orders endpoint."""
        response = client.post("/api/v1/orchestrator/load-orders")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["orders_processed"] == 2
        assert data["shipments_created"] == 2
        assert len(data["shipments"]) == 2
        assert "carrier_breakdown" in data
        
        # Verify Mirakl was called
        mock_adapters["mirakl"].get_orders.assert_called_once_with(
            status="PENDING", limit=100, offset=0
        )
        
        # Verify carriers were called
        mock_adapters["tipsa"].create_shipments_bulk.assert_called_once()
        mock_adapters["dhl"].create_shipments_bulk.assert_called_once()
    
    def test_upload_tracking_endpoint(self, client, mock_auth):
        """Test upload tracking endpoint."""
        tracking_data = [
            {
                "order_id": "MIR-001",
                "tracking_number": "JD123456789",
                "carrier_code": "dhl",
                "carrier_name": "DHL"
            },
            {
                "order_id": "MIR-002",
                "tracking_number": "1Z123456789",
                "carrier_code": "tipsa",
                "carrier_name": "TIPSA"
            }
        ]
        
        with patch("app.api.orchestrator.mirakl_adapter") as mock_mirakl:
            mock_mirakl.update_order_tracking = AsyncMock()
            mock_mirakl.update_order_status = AsyncMock()
            
            response = client.post(
                "/api/v1/orchestrator/upload-tracking",
                json=tracking_data
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["orders_updated"] == 2
            assert len(data["tracking_updates"]) == 2
            
            # Verify Mirakl was called for each order
            assert mock_mirakl.update_order_tracking.call_count == 2
            assert mock_mirakl.update_order_status.call_count == 2
    
    def test_upload_tracking_missing_fields(self, client, mock_auth):
        """Test upload tracking with missing fields."""
        tracking_data = [
            {
                "order_id": "MIR-001",
                "tracking_number": "JD123456789"
                # Missing carrier_code and carrier_name
            }
        ]
        
        response = client.post(
            "/api/v1/orchestrator/upload-tracking",
            json=tracking_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["orders_updated"] == 0
        assert len(data["tracking_updates"]) == 1
        assert data["tracking_updates"][0]["status"] == "ERROR"
        assert "Missing required fields" in data["tracking_updates"][0]["error"]
    
    def test_upload_tracking_empty_data(self, client, mock_auth):
        """Test upload tracking with empty data."""
        response = client.post(
            "/api/v1/orchestrator/upload-tracking",
            json=[]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["orders_updated"] == 0
        assert data["message"] == "No tracking data provided"
    
    def test_orchestrator_status_endpoint(self, client, mock_auth):
        """Test orchestrator status endpoint."""
        with patch("app.api.orchestrator.CARRIER_ADAPTERS") as mock_carriers:
            mock_tipsa = AsyncMock()
            mock_tipsa.mock_mode = True
            
            mock_dhl = AsyncMock()
            mock_dhl.mock_mode = True
            
            mock_carriers.items.return_value = [
                ("tipsa", mock_tipsa),
                ("dhl", mock_dhl)
            ]
            
            response = client.get("/api/v1/orchestrator/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "healthy"
            assert "mirakl" in data
            assert "carriers" in data
            assert "rules_engine" in data
            assert "tipsa" in data["carriers"]
            assert "dhl" in data["carriers"]
