"""
Webhook service for secure webhook processing.

This module provides secure webhook processing with HMAC validation,
replay protection, and idempotency.
"""

import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
from pathlib import Path

from ..core.settings import settings
from ..core.logging import csv_logger


class WebhookService:
    """Secure webhook processing service."""
    
    def __init__(self):
        """Initialize webhook service."""
        self.processed_events: Set[str] = set()
        self.webhook_secrets = {
            "tipsa": "tipsa_webhook_secret_2025",
            "ontime": "ontime_webhook_secret_2025", 
            "seur": "seur_webhook_secret_2025",
            "correosex": "correosex_webhook_secret_2025"
        }
        self.max_timestamp_age = 300  # 5 minutes
    
    def validate_webhook(self, 
                        payload: str, 
                        signature: str, 
                        timestamp: str, 
                        carrier: str) -> bool:
        """
        Validate webhook signature and timestamp.
        
        Args:
            payload: Raw webhook payload
            signature: X-Signature header value
            timestamp: X-Timestamp header value
            carrier: Carrier code
            
        Returns:
            True if webhook is valid
        """
        try:
            # Check timestamp age
            if timestamp:
                try:
                    webhook_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    age_seconds = (datetime.utcnow() - webhook_time).total_seconds()
                    if age_seconds > self.max_timestamp_age:
                        csv_logger.log_operation(
                            operation="webhook_validation",
                            order_id="",
                            status="ERROR",
                            details=f"Webhook timestamp too old: {age_seconds}s"
                        )
                        return False
                except ValueError:
                    csv_logger.log_operation(
                        operation="webhook_validation",
                        order_id="",
                        status="ERROR",
                        details="Invalid timestamp format"
                    )
                    return False
            
            # Get secret
            secret = self.webhook_secrets.get(carrier)
            if not secret:
                csv_logger.log_operation(
                    operation="webhook_validation",
                    order_id="",
                    status="ERROR",
                    details=f"No secret configured for carrier: {carrier}"
                )
                return False
            
            # Validate signature
            expected_signature = self._generate_signature(payload, secret)
            if not hmac.compare_digest(signature, expected_signature):
                csv_logger.log_operation(
                    operation="webhook_validation",
                    order_id="",
                    status="ERROR",
                    details="Invalid webhook signature"
                )
                return False
            
            return True
            
        except Exception as e:
            csv_logger.log_operation(
                operation="webhook_validation",
                order_id="",
                status="ERROR",
                details=f"Webhook validation error: {str(e)}"
            )
            return False
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def is_duplicate_event(self, event_id: str) -> bool:
        """
        Check if event has already been processed.
        
        Args:
            event_id: Unique event identifier
            
        Returns:
            True if event is duplicate
        """
        return event_id in self.processed_events
    
    def mark_event_processed(self, event_id: str):
        """
        Mark event as processed.
        
        Args:
            event_id: Unique event identifier
        """
        self.processed_events.add(event_id)
    
    def process_webhook_event(self, 
                             carrier: str, 
                             event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook event with idempotency.
        
        Args:
            carrier: Carrier code
            event_data: Webhook event data
            
        Returns:
            Processed event data
        """
        try:
            # Extract event ID for idempotency
            event_id = event_data.get("event_id") or event_data.get("id")
            if not event_id:
                # Generate event ID from data
                event_id = hashlib.sha256(
                    json.dumps(event_data, sort_keys=True).encode()
                ).hexdigest()[:16]
            
            # Check for duplicates
            if self.is_duplicate_event(event_id):
                csv_logger.log_operation(
                    operation="process_webhook_event",
                    order_id=event_data.get("expedition_id", ""),
                    status="SUCCESS",
                    details=f"Duplicate event ignored: {event_id}"
                )
                return {
                    "status": "duplicate",
                    "event_id": event_id,
                    "message": "Event already processed"
                }
            
            # Process event
            expedition_id = event_data.get("expedition_id")
            event_type = event_data.get("event_type", "unknown")
            
            # Log event processing
            csv_logger.log_operation(
                operation="process_webhook_event",
                order_id=expedition_id,
                status="SUCCESS",
                details=f"Processed {carrier} {event_type} event for {expedition_id}"
            )
            
            # Mark as processed
            self.mark_event_processed(event_id)
            
            # Return processed event
            return {
                "status": "processed",
                "event_id": event_id,
                "carrier": carrier,
                "expedition_id": expedition_id,
                "event_type": event_type,
                "processed_at": datetime.utcnow().isoformat(),
                "data": event_data
            }
            
        except Exception as e:
            csv_logger.log_operation(
                operation="process_webhook_event",
                order_id=event_data.get("expedition_id", ""),
                status="ERROR",
                details=f"Webhook processing error: {str(e)}"
            )
            raise
    
    def get_webhook_stats(self) -> Dict[str, Any]:
        """
        Get webhook processing statistics.
        
        Returns:
            Webhook statistics
        """
        return {
            "processed_events": len(self.processed_events),
            "max_timestamp_age": self.max_timestamp_age,
            "configured_carriers": list(self.webhook_secrets.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
webhook_service = WebhookService()
