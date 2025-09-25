"""
Order storage service for managing orders in memory.

This service provides a simple in-memory storage for orders with status tracking.
In a production environment, this would be replaced with a proper database.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from ..models.order import OrderStandard, OrderStorage, OrderUpdateRequest


class OrderStorageService:
    """In-memory order storage service"""
    
    def __init__(self, storage_file: str = "orders_storage.json"):
        self.storage_file = storage_file
        self.orders: Dict[str, OrderStorage] = {}
        self.load_from_file()
    
    def load_from_file(self):
        """Load orders from JSON file if it exists"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for order_id, order_data in data.items():
                        # Convert datetime strings back to datetime objects
                        order_data['created_at'] = datetime.fromisoformat(order_data['created_at'])
                        order_data['updated_at'] = datetime.fromisoformat(order_data['updated_at'])
                        if order_data.get('order_data', {}).get('created_at'):
                            order_data['order_data']['created_at'] = datetime.fromisoformat(
                                order_data['order_data']['created_at']
                            )
                        self.orders[order_id] = OrderStorage(**order_data)
            except Exception as e:
                print(f"Error loading orders from file: {e}")
    
    def save_to_file(self):
        """Save orders to JSON file"""
        try:
            data = {}
            for order_id, order in self.orders.items():
                # Build order dict manually to avoid Pydantic dict() issues
                order_dict = {
                    "order_id": order.order_id,
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat(),
                    "estado_mirakl": order.estado_mirakl,
                    "estado_tipsa": order.estado_tipsa,
                    "tracking_number": order.tracking_number,
                    "carrier_code": order.carrier_code,
                    "carrier_name": order.carrier_name,
                    "synced_to_mirakl": order.synced_to_mirakl,
                    "synced_to_carrier": order.synced_to_carrier,
                    "notes": order.notes,
                    "order_data": {
                        "order_id": order.order_data.order_id,
                        "created_at": order.order_data.created_at.isoformat(),
                        "status": order.order_data.status,
                        "buyer": order.order_data.buyer,
                        "shipping": order.order_data.shipping,
                        "totals": order.order_data.totals,
                        "items": order.order_data.items,
                        "estado_mirakl": order.order_data.estado_mirakl,
                        "estado_tipsa": order.order_data.estado_tipsa,
                        "tracking_number": order.order_data.tracking_number,
                        "carrier_code": order.order_data.carrier_code,
                        "carrier_name": order.order_data.carrier_name,
                        "synced_to_mirakl": order.order_data.synced_to_mirakl,
                        "synced_to_carrier": order.order_data.synced_to_carrier
                    }
                }
                data[order_id] = order_dict
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving orders to file: {e}")
    
    def store_order(self, order: OrderStandard) -> OrderStorage:
        """Store a new order or update existing one"""
        now = datetime.utcnow()
        
        if order.order_id in self.orders:
            # Update existing order
            existing = self.orders[order.order_id]
            existing.order_data = order
            existing.updated_at = now
            existing.estado_mirakl = order.estado_mirakl or existing.estado_mirakl
            existing.estado_tipsa = order.estado_tipsa or existing.estado_tipsa
            existing.tracking_number = order.tracking_number or existing.tracking_number
            existing.carrier_code = order.carrier_code or existing.carrier_code
            existing.carrier_name = order.carrier_name or existing.carrier_name
            existing.synced_to_mirakl = order.synced_to_mirakl or existing.synced_to_mirakl
            existing.synced_to_carrier = order.synced_to_carrier or existing.synced_to_carrier
        else:
            # Create new order
            self.orders[order.order_id] = OrderStorage(
                order_id=order.order_id,
                order_data=order,
                created_at=now,
                updated_at=now,
                estado_mirakl=order.estado_mirakl or "PENDING",
                estado_tipsa=order.estado_tipsa or "PENDING",
                tracking_number=order.tracking_number,
                carrier_code=order.carrier_code,
                carrier_name=order.carrier_name,
                synced_to_mirakl=order.synced_to_mirakl or False,
                synced_to_carrier=order.synced_to_carrier or False
            )
        
        # Temporarily disable auto-save to prevent blocking
        # self.save_to_file()
        return self.orders[order.order_id]
    
    def get_order(self, order_id: str) -> Optional[OrderStorage]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_all_orders(self) -> List[OrderStorage]:
        """Get all stored orders"""
        return list(self.orders.values())
    
    def get_orders_by_status(self, estado_mirakl: str = None, estado_tipsa: str = None) -> List[OrderStorage]:
        """Get orders filtered by status"""
        filtered = []
        for order in self.orders.values():
            if estado_mirakl and order.estado_mirakl != estado_mirakl:
                continue
            if estado_tipsa and order.estado_tipsa != estado_tipsa:
                continue
            filtered.append(order)
        return filtered
    
    def update_order_status(self, order_id: str, update_data: OrderUpdateRequest) -> Optional[OrderStorage]:
        """Update order status and tracking information"""
        if order_id not in self.orders:
            return None
        
        order = self.orders[order_id]
        order.updated_at = datetime.utcnow()
        
        if update_data.estado_mirakl is not None:
            order.estado_mirakl = update_data.estado_mirakl
        if update_data.estado_tipsa is not None:
            order.estado_tipsa = update_data.estado_tipsa
        if update_data.tracking_number is not None:
            order.tracking_number = update_data.tracking_number
        if update_data.carrier_code is not None:
            order.carrier_code = update_data.carrier_code
        if update_data.carrier_name is not None:
            order.carrier_name = update_data.carrier_name
        if update_data.synced_to_mirakl is not None:
            order.synced_to_mirakl = update_data.synced_to_mirakl
        if update_data.synced_to_carrier is not None:
            order.synced_to_carrier = update_data.synced_to_carrier
        if update_data.notes is not None:
            order.notes = update_data.notes
        
        self.save_to_file()
        return order
    
    def delete_order(self, order_id: str) -> bool:
        """Delete order by ID"""
        if order_id in self.orders:
            del self.orders[order_id]
            self.save_to_file()
            return True
        return False
    
    def get_orders_count(self) -> int:
        """Get total number of stored orders"""
        return len(self.orders)
    
    def get_orders_summary(self) -> Dict[str, int]:
        """Get summary of orders by status"""
        summary = {
            "total": len(self.orders),
            "estado_mirakl": {},
            "estado_tipsa": {}
        }
        
        for order in self.orders.values():
            # Count by Mirakl status
            mirakl_status = order.estado_mirakl
            summary["estado_mirakl"][mirakl_status] = summary["estado_mirakl"].get(mirakl_status, 0) + 1
            
            # Count by TIPSA status
            tipsa_status = order.estado_tipsa
            summary["estado_tipsa"][tipsa_status] = summary["estado_tipsa"].get(tipsa_status, 0) + 1
        
        return summary


# Global instance
order_storage = OrderStorageService()
order_storage_service = order_storage  # Alias for compatibility
