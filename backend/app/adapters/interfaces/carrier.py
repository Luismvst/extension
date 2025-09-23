"""
Carrier adapter interface.

This module defines the protocol for carrier adapters,
ensuring consistent interface across different carriers.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class CarrierAdapter(ABC):
    """Abstract base class for carrier adapters."""
    
    @abstractmethod
    async def create_shipment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a single shipment.
        
        Args:
            order_data: Order information
            
        Returns:
            Shipment details
        """
        pass
    
    @abstractmethod
    async def create_shipments_bulk(self, orders_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple shipments in bulk.
        
        Args:
            orders_data: List of order information
            
        Returns:
            Bulk shipment results
        """
        pass
    
    @abstractmethod
    async def get_shipment_status(self, shipment_id: str) -> Dict[str, Any]:
        """
        Get shipment status and tracking information.
        
        Args:
            shipment_id: Shipment identifier
            
        Returns:
            Shipment status and tracking info
        """
        pass
    
    @abstractmethod
    async def get_shipment_label(self, shipment_id: str) -> bytes:
        """
        Get shipment label as PDF bytes.
        
        Args:
            shipment_id: Shipment identifier
            
        Returns:
            Label PDF bytes
        """
        pass
    
    @abstractmethod
    async def cancel_shipment(self, shipment_id: str, 
                            reason: str = None) -> Dict[str, Any]:
        """
        Cancel a shipment.
        
        Args:
            shipment_id: Shipment identifier
            reason: Cancellation reason
            
        Returns:
            Cancellation result
        """
        pass
    
    @property
    @abstractmethod
    def carrier_name(self) -> str:
        """Get carrier name."""
        pass
    
    @property
    @abstractmethod
    def carrier_code(self) -> str:
        """Get carrier code."""
        pass
    
    @property
    @abstractmethod
    def is_mock_mode(self) -> bool:
        """Check if adapter is in mock mode."""
        pass
