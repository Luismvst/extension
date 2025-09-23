"""
Unified order logger for business CSV tracking.

This module provides a UnifiedOrderLogger class that manages
a single CSV file tracking the state of orders through the
Mirakl -> Carrier -> Mirakl workflow.
"""

import csv
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class UnifiedOrderLogger:
    """
    Manages a unified CSV file for tracking order states through the workflow.
    
    The CSV contains columns for:
    - Order identification (id, marketplace, buyer)
    - Financial data (amounts, currency)
    - Carrier information (carrier_code, tracking_number, label_url)
    - Internal state tracking (internal_state, timestamps)
    - Error handling (error_message, retry_count)
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize the unified order logger.
        
        Args:
            csv_path: Path to the CSV file. Defaults to ORDERS_CSV_PATH env var.
        """
        self.csv_path = csv_path or os.getenv("ORDERS_CSV_PATH", "logs/orders_view.csv")
        self.ensure_csv_exists()
    
    def ensure_csv_exists(self):
        """Ensure the CSV file exists with proper headers."""
        if not os.path.exists(self.csv_path):
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            self._write_headers()
            logger.info(f"Created new orders CSV: {self.csv_path}")
    
    def _write_headers(self):
        """Write CSV headers with standardized format."""
        headers = [
            "order_id",
            "marketplace",
            "buyer_email",
            "buyer_name",
            "total_amount",
            "currency",
            "shipping_address",
            "carrier_code",
            "carrier_name",
            "tracking_number",
            "label_url",
            "internal_state",
            "created_at",
            "updated_at",
            "error_message",
            "retry_count",
            "mirakl_tracking_updated",
            "mirakl_ship_updated",
            # Additional standardized fields
            "reference",
            "consignee_name",
            "consignee_address",
            "consignee_city",
            "consignee_postal_code",
            "consignee_country",
            "consignee_contact",
            "consignee_phone",
            "packages",
            "weight_kg",
            "volume",
            "shipping_cost",
            "product_type",
            "cod_amount",
            "delayed_date",
            "observations",
            "destination_email",
            "package_type",
            "client_department",
            "return_conform",
            "order_date",
            "consignee_nif",
            "client_name",
            "return_flag",
            "client_code",
            "multi_reference"
        ]
        
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def upsert_order(self, order_id: str, fields: dict = None) -> None:
        """
        Insert or update an order in the CSV.
        
        Args:
            order_id: Unique identifier for the order
            fields: Additional fields to update
        """
        try:
            if fields is None:
                fields = {}
                
            # Read existing data
            orders = self._read_csv()
            
            # Update or create order
            now = datetime.now().isoformat()
            if order_id in orders:
                # Update existing order
                orders[order_id].update(fields)
                orders[order_id]['updated_at'] = now
                logger.info(f"Updated order {order_id} in CSV")
            else:
                # Create new order
                orders[order_id] = {
                    'order_id': order_id,
                    'created_at': now,
                    'updated_at': now,
                    **fields
                }
                logger.info(f"Created new order {order_id} in CSV")
            
            # Write back to CSV
            self._write_csv(orders)
            
        except Exception as e:
            logger.error(f"Error upserting order {order_id}: {e}", exc_info=True)
            raise
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an order by ID.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order data or None if not found
        """
        try:
            orders = self._read_csv()
            return orders.get(order_id)
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}", exc_info=True)
            return None
    
    def get_orders_by_state(self, state: str) -> List[Dict[str, Any]]:
        """
        Get all orders with a specific internal state.
        
        Args:
            state: Internal state to filter by
            
        Returns:
            List of orders with the specified state
        """
        try:
            orders = self._read_csv()
            return [order for order in orders.values() if order.get('internal_state') == state]
        except Exception as e:
            logger.error(f"Error getting orders by state {state}: {e}", exc_info=True)
            return []
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """
        Get all orders.
        
        Returns:
            List of all orders
        """
        try:
            orders = self._read_csv()
            return list(orders.values())
        except Exception as e:
            logger.error(f"Error getting all orders: {e}", exc_info=True)
            return []
    
    def _read_csv(self) -> Dict[str, Dict[str, Any]]:
        """Read CSV file and return as dictionary keyed by order_id."""
        orders = {}
        
        if not os.path.exists(self.csv_path):
            return orders
        
        try:
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('order_id'):
                        orders[row['order_id']] = row
        except Exception as e:
            logger.error(f"Error reading CSV: {e}", exc_info=True)
        
        return orders
    
    def _write_csv(self, orders: Dict[str, Dict[str, Any]]) -> None:
        """Write orders dictionary to CSV file."""
        if not orders:
            return
        
        try:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                if orders:
                    fieldnames = list(next(iter(orders.values())).keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(orders.values())
        except Exception as e:
            logger.error(f"Error writing CSV: {e}", exc_info=True)
            raise
    
    def export_csv(self, output_path: Optional[str] = None) -> str:
        """
        Export CSV to a timestamped file.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to the exported file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            output_path = f"/app/logs/orders_view_{timestamp}.csv"
        
        try:
            import shutil
            shutil.copy2(self.csv_path, output_path)
            logger.info(f"Exported CSV to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}", exc_info=True)
            raise


# Global instance
unified_order_logger = UnifiedOrderLogger()

