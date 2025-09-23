"""
Unified logging system for orders view.

This module provides a unified CSV logger that merges data from
Mirakl, carriers, and internal operations into a single view.
"""

import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from .settings import settings


class UnifiedOrderLogger:
    """Unified logger for orders view CSV."""
    
    def __init__(self, file_path: str):
        """Initialize unified order logger."""
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
                    # Mirakl data
                    'mirakl_order_id',
                    'mirakl_status',
                    'mirakl_customer_name',
                    'mirakl_customer_email',
                    'mirakl_weight',
                    'mirakl_total_amount',
                    'mirakl_currency',
                    'mirakl_created_at',
                    'mirakl_shipping_address',
                    
                    # Carrier data
                    'carrier_code',
                    'carrier_name',
                    'expedition_id',
                    'tracking_number',
                    'carrier_status',
                    'label_url',
                    'carrier_cost',
                    'carrier_created_at',
                    
                    # Internal state
                    'internal_state',
                    'last_event',
                    'last_event_at',
                    'error_message',
                    'retry_count',
                    
                    # Timestamps
                    'updated_at'
                ])
    
    def upsert_order(self, order_data: Dict[str, Any]):
        """
        Upsert order data in the unified CSV.
        
        Args:
            order_data: Order data with Mirakl, carrier, and internal fields
        """
        try:
            # Read existing data
            existing_orders = self._read_existing_orders()
            
            # Find existing order by mirakl_order_id
            order_id = order_data.get('mirakl_order_id')
            existing_order = None
            for order in existing_orders:
                if order.get('mirakl_order_id') == order_id:
                    existing_order = order
                    break
            
            # Merge data
            if existing_order:
                # Update existing order
                merged_order = {**existing_order, **order_data}
                merged_order['updated_at'] = datetime.utcnow().isoformat()
                
                # Remove old order
                existing_orders = [o for o in existing_orders if o.get('mirakl_order_id') != order_id]
            else:
                # Create new order
                merged_order = order_data.copy()
                merged_order['updated_at'] = datetime.utcnow().isoformat()
            
            # Add to list
            existing_orders.append(merged_order)
            
            # Write back to file
            self._write_orders(existing_orders)
            
        except Exception as e:
            print(f"Error upserting order: {e}")
    
    def _read_existing_orders(self) -> List[Dict[str, Any]]:
        """Read existing orders from CSV."""
        orders = []
        if not os.path.exists(self.file_path):
            return orders
        
        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                orders = list(reader)
        except Exception as e:
            print(f"Error reading existing orders: {e}")
        
        return orders
    
    def _write_orders(self, orders: List[Dict[str, Any]]):
        """Write orders to CSV."""
        if not orders:
            return
        
        # Get headers from first order
        headers = list(orders[0].keys())
        
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(orders)
    
    def get_orders(self, 
                  state: Optional[str] = None,
                  carrier: Optional[str] = None,
                  limit: int = 100,
                  offset: int = 0) -> Dict[str, Any]:
        """
        Get orders with optional filtering.
        
        Args:
            state: Filter by internal state
            carrier: Filter by carrier code
            limit: Maximum number of orders to return
            offset: Number of orders to skip
            
        Returns:
            Dictionary with orders and metadata
        """
        try:
            orders = self._read_existing_orders()
            
            # Apply filters
            if state:
                orders = [o for o in orders if o.get('internal_state') == state]
            
            if carrier:
                orders = [o for o in orders if o.get('carrier_code') == carrier]
            
            # Apply pagination
            total = len(orders)
            orders = orders[offset:offset + limit]
            
            return {
                "orders": orders,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
            
        except Exception as e:
            print(f"Error getting orders: {e}")
            return {"orders": [], "total": 0, "limit": limit, "offset": offset, "has_more": False}
    
    def log_event(self, order_id: str, event_type: str, details: str = ""):
        """
        Log an event for an order.
        
        Args:
            order_id: Mirakl order ID
            event_type: Type of event (e.g., 'PENDING_POST', 'POSTED', 'AWAITING_TRACKING')
            details: Additional details
        """
        try:
            orders = self._read_existing_orders()
            
            for order in orders:
                if order.get('mirakl_order_id') == order_id:
                    order['last_event'] = event_type
                    order['last_event_at'] = datetime.utcnow().isoformat()
                    order['updated_at'] = datetime.utcnow().isoformat()
                    
                    if details:
                        order['error_message'] = details
                    
                    break
            
            self._write_orders(orders)
            
        except Exception as e:
            print(f"Error logging event: {e}")


# Global instance
unified_logger = UnifiedOrderLogger(settings.csv_log_file.replace('operations.csv', 'orders_view.csv'))
