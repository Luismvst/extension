"""
Standardized CSV operations logger.

This module provides a unified logging interface for all operations
with standardized headers and atomic writes.
"""

import csv
import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import aiofiles

from ..core.settings import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class CSVOpsLogger:
    """
    Standardized CSV operations logger with atomic writes.
    
    Headers: timestamp_iso, scope, action, order_id, carrier, marketplace, 
             status, message, duration_ms, meta_json
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """Initialize the CSV operations logger."""
        self.log_dir = Path(log_dir or settings.log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.csv_file = self.log_dir / "operations.csv"
        self._lock = asyncio.Lock()
        
        # Initialize CSV file with headers if it doesn't exist (sync version)
        self._initialize_csv_file_sync()
    
    def _initialize_csv_file_sync(self) -> None:
        """Initialize CSV file with headers synchronously."""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp_iso',
                    'scope',
                    'action',
                    'order_id',
                    'carrier',
                    'marketplace',
                    'status',
                    'message',
                    'duration_ms',
                    'meta_json'
                ])
    
    async def _initialize_csv_file(self) -> None:
        """Initialize CSV file with standardized headers."""
        if not self.csv_file.exists():
            async with self._lock:
                async with aiofiles.open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp_iso',
                        'scope',
                        'action',
                        'order_id',
                        'carrier',
                        'marketplace',
                        'status',
                        'message',
                        'duration_ms',
                        'meta_json'
                    ])
    
    async def log(
        self,
        scope: str,
        action: str,
        order_id: Optional[str] = None,
        carrier: Optional[str] = None,
        marketplace: Optional[str] = None,
        status: str = "OK",
        message: str = "",
        duration_ms: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an operation to CSV with standardized format.
        
        Args:
            scope: Operation scope (e.g., 'mirakl', 'carrier', 'orchestrator')
            action: Action performed (e.g., 'fetch_orders', 'create_shipment')
            order_id: Order identifier
            carrier: Carrier name
            marketplace: Marketplace name
            status: Operation status (OK, ERROR, WARNING)
            message: Additional message
            duration_ms: Operation duration in milliseconds
            meta: Additional metadata as dictionary
        """
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(meta or {}, separators=(',', ':'), ensure_ascii=False)
        
        # Prepare CSV row
        row = [
            timestamp_iso,
            scope,
            action,
            order_id or "",
            carrier or "",
            marketplace or "",
            status,
            message,
            duration_ms or "",
            meta_json
        ]
        
        # Atomic write to CSV
        async with self._lock:
            async with aiofiles.open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                # Convert row to CSV line
                csv_line = ','.join([f'"{str(item)}"' for item in row]) + '\n'
                await f.write(csv_line)
        
        logger.info(f"Logged operation: {scope}.{action} for order {order_id or 'N/A'} with status {status} (duration: {duration_ms or 'N/A'}ms)")
    
    async def get_operations(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        scope: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get operations from CSV log with filtering.
        
        Args:
            start_date: Filter operations after this date
            end_date: Filter operations before this date
            scope: Filter by scope
            action: Filter by action
            status: Filter by status
            limit: Maximum number of operations to return
            
        Returns:
            List of operation records
        """
        operations = []
        
        if not self.csv_file.exists():
            return operations
        
        async with aiofiles.open(self.csv_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            reader = csv.DictReader(content.splitlines())
            
            for row in reader:
                # Parse timestamp
                try:
                    op_timestamp = datetime.fromisoformat(row['timestamp_iso'].replace('Z', '+00:00'))
                except ValueError:
                    continue
                
                # Apply filters
                if start_date and op_timestamp < start_date:
                    continue
                
                if end_date and op_timestamp > end_date:
                    continue
                
                if scope and row['scope'] != scope:
                    continue
                
                if action and row['action'] != action:
                    continue
                
                if status and row['status'] != status:
                    continue
                
                operations.append(row)
                
                if len(operations) >= limit:
                    break
        
        return operations
    
    async def export_csv(self, output_path: Optional[Path] = None) -> Path:
        """
        Export the operations CSV to a specific location.
        
        Args:
            output_path: Path to export the CSV to
            
        Returns:
            Path to the exported CSV file
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.log_dir / f"operations_export_{timestamp}.csv"
        
        # Copy the CSV file
        async with aiofiles.open(self.csv_file, 'r', encoding='utf-8') as src:
            content = await src.read()
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as dst:
                await dst.write(content)
        
        logger.info(f"Exported operations CSV to {output_path}")
        return output_path


# Global CSV operations logger instance
csv_ops_logger = CSVOpsLogger()
