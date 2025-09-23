"""
Test API endpoints for debugging.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..core.auth import get_current_user
from ..utils.csv_ops_logger import csv_ops_logger

# Create router
router = APIRouter(prefix="/test", tags=["test"])

@router.post("/simple-log")
async def test_simple_log(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Test simple logging without complex parameters."""
    try:
        await csv_ops_logger.log(
            scope="test",
            action="simple_test",
            status="OK",
            message="Simple test message"
        )
        return {"success": True, "message": "Log entry created successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/complex-log")
async def test_complex_log(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Test complex logging with all parameters."""
    try:
        await csv_ops_logger.log(
            scope="test",
            action="complex_test",
            order_id="TEST-123",
            carrier="TEST-CARRIER",
            marketplace="TEST-MARKETPLACE",
            status="OK",
            message="Complex test message",
            duration_ms=100,
            meta={"test": "data"}
        )
        return {"success": True, "message": "Complex log entry created successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}
