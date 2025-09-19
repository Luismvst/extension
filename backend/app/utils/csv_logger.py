"""
CSV logging utility for operations tracking.

This module provides atomic CSV logging for all operations,
ensuring data integrity and easy analysis.
"""

import csv
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import aiofiles
import asyncio

from ..core.settings import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class CSVLogger:
    """
    Atomic CSV logger for operations tracking.
    
    This logger ensures that all operations are recorded in a CSV file
    with proper atomic writes and data integrity.
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """Initialize the CSV logger."""
        self.log_dir = Path(log_dir or settings.log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.csv_file = self.log_dir / "operations.csv"
        self.dumps_dir = self.log_dir / "dumps"
        self.dumps_dir.mkdir(exist_ok=True)
        
        # Lock for atomic writes
        self._lock = asyncio.Lock()
        
        # Initialize CSV file with headers if it doesn't exist
        asyncio.create_task(self._initialize_csv_file())
    
    async def _initialize_csv_file(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_file.exists():
            async with self._lock:
                async with aiofiles.open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp',
                        'action',
                        'order_id',
                        'marketplace',
                        'carrier',
                        'request_payload_hash',
                        'request_dump_path',
                        'response_status',
                        'response_dump_path',
                        'result',
                        'message',
                        'duration_ms'
                    ])
    
    async def log_operation(
        self,
        action: str,
        order_id: str,
        marketplace: str = "mirakl",
        carrier: str = "tipsa",
        request_payload: Optional[Dict[str, Any]] = None,
        response_payload: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        result: str = "OK",
        message: str = "",
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Log an operation to CSV.
        
        Args:
            action: The action performed (e.g., 'fetch_orders', 'create_shipment')
            order_id: The order identifier
            marketplace: The marketplace name
            carrier: The carrier name
            request_payload: The request payload data
            response_payload: The response payload data
            response_status: HTTP response status code
            result: Result status (OK, ERROR, WARNING)
            message: Additional message
            duration_ms: Operation duration in milliseconds
        """
        timestamp = datetime.now()
        
        # Generate payload hashes and dump paths
        request_hash = ""
        request_dump_path = ""
        response_dump_path = ""
        
        if request_payload:
            request_hash = self._hash_payload(request_payload)
            request_dump_path = await self._dump_payload(
                timestamp, action, order_id, "request", request_payload
            )
        
        if response_payload:
            response_dump_path = await self._dump_payload(
                timestamp, action, order_id, "response", response_payload
            )
        
        # Prepare CSV row
        row = [
            timestamp.isoformat(),
            action,
            order_id,
            marketplace,
            carrier,
            request_hash,
            request_dump_path,
            response_status or "",
            response_dump_path,
            result,
            message,
            duration_ms or ""
        ]
        
        # Atomic write to CSV
        async with self._lock:
            async with aiofiles.open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        
        logger.info(
            f"Logged operation: {action} for order {order_id}",
            action=action,
            order_id=order_id,
            result=result,
            duration_ms=duration_ms
        )
    
    async def _dump_payload(
        self,
        timestamp: datetime,
        action: str,
        order_id: str,
        payload_type: str,
        payload: Dict[str, Any]
    ) -> str:
        """Dump payload to JSON file and return the path."""
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{action}_{order_id}_{payload_type}.json"
        filepath = self.dumps_dir / filename
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        
        return str(filepath.relative_to(self.log_dir))
    
    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        """Generate a hash for the payload."""
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(payload_str.encode()).hexdigest()[:16]
    
    async def get_operations(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
        limit: int = 1000
    ) -> list[Dict[str, Any]]:
        """
        Get operations from CSV log.
        
        Args:
            start_date: Filter operations after this date
            end_date: Filter operations before this date
            action: Filter by action
            result: Filter by result
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
                    op_timestamp = datetime.fromisoformat(row['timestamp'])
                except ValueError:
                    continue
                
                # Apply filters
                if start_date and op_timestamp < start_date:
                    continue
                
                if end_date and op_timestamp > end_date:
                    continue
                
                if action and row['action'] != action:
                    continue
                
                if result and row['result'] != result:
                    continue
                
                operations.append(row)
                
                if len(operations) >= limit:
                    break
        
        return operations
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from the operations log."""
        if not self.csv_file.exists():
            return {
                "total_operations": 0,
                "by_action": {},
                "by_result": {},
                "by_marketplace": {},
                "by_carrier": {}
            }
        
        stats = {
            "total_operations": 0,
            "by_action": {},
            "by_result": {},
            "by_marketplace": {},
            "by_carrier": {}
        }
        
        async with aiofiles.open(self.csv_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            reader = csv.DictReader(content.splitlines())
            
            for row in reader:
                stats["total_operations"] += 1
                
                # Count by action
                action = row['action']
                stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
                
                # Count by result
                result = row['result']
                stats["by_result"][result] = stats["by_result"].get(result, 0) + 1
                
                # Count by marketplace
                marketplace = row['marketplace']
                stats["by_marketplace"][marketplace] = stats["by_marketplace"].get(marketplace, 0) + 1
                
                # Count by carrier
                carrier = row['carrier']
                stats["by_carrier"][carrier] = stats["by_carrier"].get(carrier, 0) + 1
        
        return stats
    
    async def export_csv(self, output_path: Optional[Path] = None) -> Path:
        """
        Export the operations CSV to a specific location.
        
        Args:
            output_path: Path to export the CSV to
            
        Returns:
            Path to the exported CSV file
        """
        if output_path is None:
            output_path = self.log_dir / f"operations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Copy the CSV file
        async with aiofiles.open(self.csv_file, 'r', encoding='utf-8') as src:
            content = await src.read()
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as dst:
                await dst.write(content)
        
        logger.info(f"Exported operations CSV to {output_path}")
        return output_path


# Global CSV logger instance
csv_logger = CSVLogger()
