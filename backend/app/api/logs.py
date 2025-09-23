"""
Logs API endpoints.

This module provides endpoints for accessing logs, exports,
and monitoring data.
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from ..core.auth import get_current_user
from ..utils.csv_ops_logger import csv_ops_logger
from ..core.unified_order_logger import unified_order_logger
from ..core.settings import settings
import logging

# Create logger for this module
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/logs", tags=["logs"])


@router.get("/operations")
async def get_operations_logs(
    limit: int = 100,
    offset: int = 0,
    scope: str = None,
    action: str = None,
    status: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get operations logs with filtering.
    
    Args:
        limit: Maximum number of logs to return
        offset: Number of logs to skip
        scope: Filter by scope (e.g., 'mirakl', 'carrier', 'orchestrator')
        action: Filter by action type
        status: Filter by status
        current_user: Authenticated user
        
    Returns:
        Operations logs with filtering and pagination
    """
    try:
        # Get operations from CSV logger
        operations = await csv_ops_logger.get_operations(
            scope=scope,
            action=action,
            status=status,
            limit=limit + offset  # Get more to handle pagination
        )
        
        # Apply pagination
        total = len(operations)
        operations = operations[offset:offset + limit]
        
        return {
            "success": True,
            "logs": operations,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        logger.error(f"Error getting operations logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders-view")
async def get_orders_view_logs(
    state: str = None,
    carrier: str = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get orders view logs with filtering.
    
    Args:
        state: Filter by internal state
        carrier: Filter by carrier code
        limit: Maximum number of orders to return
        offset: Number of orders to skip
        current_user: Authenticated user
        
    Returns:
        Orders view logs with filtering and pagination
    """
    try:
        # Get all orders from unified order logger
        all_orders = unified_order_logger.get_all_orders()
        
        # Apply filters
        filtered_orders = []
        for order in all_orders:
            if state and order.get('internal_state') != state:
                continue
            if carrier and order.get('carrier_code') != carrier:
                continue
            filtered_orders.append(order)
        
        # Apply pagination
        total = len(filtered_orders)
        orders = filtered_orders[offset:offset + limit]
        
        return {
            "success": True,
            "orders": orders,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        logger.error(f"Error getting orders view logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exports/operations.csv")
async def export_operations_csv(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export operations logs as CSV file.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        CSV file download
    """
    try:
        # Export CSV using the operations logger
        export_path = await csv_ops_logger.export_csv()
        
        return FileResponse(
            path=str(export_path),
            filename=f"operations_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
            media_type="text/csv"
        )
        
    except Exception as e:
        logger.error(f"Error exporting operations CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exports/orders-view.csv")
async def export_orders_view_csv(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export orders view as CSV file.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        CSV file download
    """
    try:
        # Export CSV using the unified order logger
        export_path = unified_order_logger.export_csv()
        
        return FileResponse(
            path=export_path,
            filename=f"orders_view_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
            media_type="text/csv"
        )
        
    except Exception as e:
        logger.error(f"Error exporting orders view CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exports/json-dumps")
async def list_json_dumps(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List available JSON dump files.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of JSON dump files
    """
    try:
        dumps_dir = settings.json_dumps_dir
        if not os.path.exists(dumps_dir):
            return {
                "success": True,
                "files": [],
                "total": 0
            }
        
        files = []
        for filename in os.listdir(dumps_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(dumps_dir, filename)
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by modified time (newest first)
        files.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return {
            "success": True,
            "files": files,
            "total": len(files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exports/json-dumps/{filename}")
async def download_json_dump(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download a specific JSON dump file.
    
    Args:
        filename: JSON dump filename
        current_user: Authenticated user
        
    Returns:
        JSON file download
    """
    try:
        dumps_dir = settings.json_dumps_dir
        file_path = os.path.join(dumps_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="JSON dump file not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_logs_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get logs statistics and metrics.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Logs statistics
    """
    try:
        stats = {
            "operations": {
                "total_logs": 0,
                "success_rate": 0.0,
                "error_rate": 0.0,
                "operations_count": {}
            },
            "orders": {
                "total_orders": 0,
                "by_state": {},
                "by_carrier": {},
                "recent_activity": 0
            },
            "files": {
                "operations_csv_size": 0,
                "orders_view_csv_size": 0,
                "json_dumps_count": 0
            }
        }
        
        # Operations stats
        csv_file = settings.csv_log_file
        if os.path.exists(csv_file):
            import csv
            total_logs = 0
            success_logs = 0
            error_logs = 0
            operations_count = {}
            
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_logs += 1
                    operation = row.get('operation', 'unknown')
                    status = row.get('status', 'unknown')
                    
                    if status == 'SUCCESS':
                        success_logs += 1
                    elif status == 'ERROR':
                        error_logs += 1
                    
                    operations_count[operation] = operations_count.get(operation, 0) + 1
            
            stats["operations"]["total_logs"] = total_logs
            stats["operations"]["success_rate"] = (success_logs / total_logs * 100) if total_logs > 0 else 0
            stats["operations"]["error_rate"] = (error_logs / total_logs * 100) if total_logs > 0 else 0
            stats["operations"]["operations_count"] = operations_count
            
            # File size
            stats["files"]["operations_csv_size"] = os.path.getsize(csv_file)
        
        # Orders stats
        orders_file = settings.csv_log_file.replace('operations.csv', 'orders_view.csv')
        if os.path.exists(orders_file):
            import csv
            total_orders = 0
            by_state = {}
            by_carrier = {}
            
            with open(orders_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_orders += 1
                    state = row.get('internal_state', 'unknown')
                    carrier = row.get('carrier_code', 'unknown')
                    
                    by_state[state] = by_state.get(state, 0) + 1
                    by_carrier[carrier] = by_carrier.get(carrier, 0) + 1
            
            stats["orders"]["total_orders"] = total_orders
            stats["orders"]["by_state"] = by_state
            stats["orders"]["by_carrier"] = by_carrier
            stats["files"]["orders_view_csv_size"] = os.path.getsize(orders_file)
        
        # JSON dumps count
        dumps_dir = settings.json_dumps_dir
        if os.path.exists(dumps_dir):
            json_files = [f for f in os.listdir(dumps_dir) if f.endswith('.json')]
            stats["files"]["json_dumps_count"] = len(json_files)
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
