"""
Marketplace adapter interface.

This module defines the protocol for marketplace adapters,
ensuring consistent interface across different marketplaces.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class MarketplaceAdapter(ABC):
    """Abstract base class for marketplace adapters."""
    
    @abstractmethod
    async def get_orders(self, status: str = "PENDING", 
                        limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get orders from marketplace.
        
        Args:
            status: Order status filter
            limit: Maximum number of orders to return
            offset: Number of orders to skip
            
        Returns:
            Dictionary with orders and metadata
        """
        pass
    
    @abstractmethod
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order details
        """
        pass
    
    @abstractmethod
    async def update_order_tracking(self, order_id: str, 
                                  tracking_number: str, 
                                  carrier_code: str,
                                  carrier_name: str) -> Dict[str, Any]:
        """
        Update order with tracking information.
        
        Args:
            order_id: Order identifier
            tracking_number: Tracking number
            carrier_code: Carrier code
            carrier_name: Carrier name
            
        Returns:
            Update result
        """
        pass
    
    @abstractmethod
    async def update_order_status(self, order_id: str, 
                                status: str, 
                                reason: str = None) -> Dict[str, Any]:
        """
        Update order status.
        
        Args:
            order_id: Order identifier
            status: New status
            reason: Reason for status change
            
        Returns:
            Update result
        """
        pass
    
    @property
    @abstractmethod
    def marketplace_name(self) -> str:
        """Get marketplace name."""
        pass
    
    @property
    @abstractmethod
    def is_mock_mode(self) -> bool:
        """Check if adapter is in mock mode."""
        pass
