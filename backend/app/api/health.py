"""
Health check API endpoints.

This module contains health check and status endpoints
for the Mirakl-TIPSA Orchestrator.
"""

from fastapi import APIRouter
from typing import Dict, Any
import time

from ..adapters.marketplaces.mirakl import MiraklAdapter
from ..adapters.carriers.tipsa import TipsaAdapter

# Create router
router = APIRouter(prefix="/api/v1/health", tags=["health"])

# Initialize adapters
mirakl_adapter = MiraklAdapter()
tipsa_adapter = TipsaAdapter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.2.0",
        "message": "Backend is running",
        "timestamp": time.time()
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check endpoint."""
    try:
        # Check Mirakl adapter
        mirakl_status = "healthy" if mirakl_adapter.is_mock_mode else "unknown"
        
        # Check TIPSA adapter
        tipsa_status = "healthy" if tipsa_adapter.is_mock_mode else "unknown"
        
        return {
            "status": "healthy",
            "version": "0.2.0",
            "dependencies": {
                "mirakl": {
                    "status": mirakl_status,
                    "mode": "mock" if mirakl_adapter.is_mock_mode else "real"
                },
                "tipsa": {
                    "status": tipsa_status,
                    "mode": "mock" if tipsa_adapter.is_mock_mode else "real"
                }
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "version": "0.2.0",
            "error": str(e),
            "timestamp": time.time()
        }