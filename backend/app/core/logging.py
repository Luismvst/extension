"""
Logging configuration and utilities.

This module provides centralized logging configuration and utilities
for the application, including CSV logging and JSON dumps.
"""

import logging
import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from .settings import settings


class CSVLogger:
    """CSV logger for operations tracking."""
    
    def __init__(self, file_path: str):
        """Initialize CSV logger."""
        self.file_path = file_path
        self._ensure_directory()
        self._ensure_header()
    
    def _ensure_directory(self):
        """Ensure log directory exists."""
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _ensure_header(self):
        """Ensure CSV file has proper header."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'operation',
                    'order_id',
                    'status',
                    'details',
                    'duration_ms'
                ])
    
    def log_operation(self, operation: str, order_id: str = None, 
                     status: str = "SUCCESS", details: str = "", 
                     duration_ms: int = 0):
        """Log an operation to CSV."""
        try:
            with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.utcnow().isoformat(),
                    operation,
                    order_id or "",
                    status,
                    details,
                    duration_ms
                ])
        except Exception as e:
            logging.error(f"Failed to log to CSV: {e}")


class JSONDumper:
    """JSON dumper for request/response payloads."""
    
    def __init__(self, dumps_dir: str):
        """Initialize JSON dumper."""
        self.dumps_dir = dumps_dir
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure dumps directory exists."""
        Path(self.dumps_dir).mkdir(parents=True, exist_ok=True)
    
    def dump_request_response(self, operation: str, order_id: str, 
                            request_data: Dict[str, Any], 
                            response_data: Dict[str, Any]):
        """Dump request/response data to JSON file."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{operation}_{order_id}_{timestamp}.json"
            filepath = os.path.join(self.dumps_dir, filename)
            
            dump_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "order_id": order_id,
                "request": request_data,
                "response": response_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dump_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logging.error(f"Failed to dump JSON: {e}")


def setup_logging():
    """Setup application logging."""
    # Create logs directory
    Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )
    
    # Create loggers
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    
    return logger

def get_logger(name: str):
    """Get a logger instance."""
    return logging.getLogger(name)

# Global instances
# csv_logger = CSVLogger(settings.csv_log_file)  # Disabled - using csv_ops_logger instead
json_dumper = JSONDumper(settings.json_dumps_dir)
