#!/usr/bin/env python3
"""
Script to verify CSV logging functionality.

This script checks that the backend is properly generating CSV logs
and that the log files contain the expected data.
"""

import os
import sys
import csv
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any


def check_logs_directory(logs_dir: Path) -> bool:
    """Check if logs directory exists and is accessible."""
    if not logs_dir.exists():
        print(f"❌ Logs directory does not exist: {logs_dir}")
        return False
    
    if not logs_dir.is_dir():
        print(f"❌ Logs path is not a directory: {logs_dir}")
        return False
    
    print(f"✅ Logs directory exists: {logs_dir}")
    return True


def check_operations_csv(logs_dir: Path) -> bool:
    """Check if operations.csv exists and has valid content."""
    operations_csv = logs_dir / "operations.csv"
    
    if not operations_csv.exists():
        print(f"❌ Operations CSV does not exist: {operations_csv}")
        return False
    
    if operations_csv.stat().st_size == 0:
        print(f"❌ Operations CSV is empty: {operations_csv}")
        return False
    
    # Read and validate CSV structure
    try:
        with open(operations_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if len(rows) == 0:
                print(f"❌ Operations CSV has no data rows")
                return False
            
            # Check required columns
            required_columns = [
                'timestamp', 'operation', 'order_id', 'status', 
                'details', 'duration_ms', 'dump_file'
            ]
            
            for row in rows:
                for col in required_columns:
                    if col not in row:
                        print(f"❌ Missing column '{col}' in operations CSV")
                        return False
            
            print(f"✅ Operations CSV is valid with {len(rows)} entries")
            return True
            
    except Exception as e:
        print(f"❌ Error reading operations CSV: {e}")
        return False


def check_dumps_directory(logs_dir: Path) -> bool:
    """Check if dumps directory exists and has JSON files."""
    dumps_dir = logs_dir / "dumps"
    
    if not dumps_dir.exists():
        print(f"❌ Dumps directory does not exist: {dumps_dir}")
        return False
    
    json_files = list(dumps_dir.glob("*.json"))
    
    if len(json_files) == 0:
        print(f"❌ No JSON dump files found in: {dumps_dir}")
        return False
    
    # Validate JSON files
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                required_fields = ['operation', 'order_id', 'request_data', 'response_data']
                for field in required_fields:
                    if field not in data:
                        print(f"❌ Missing field '{field}' in {json_file}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error reading JSON file {json_file}: {e}")
            return False
    
    print(f"✅ Dumps directory is valid with {len(json_files)} JSON files")
    return True


def trigger_api_calls(base_url: str) -> bool:
    """Trigger API calls to generate logs."""
    print("🔄 Triggering API calls to generate logs...")
    
    try:
        # Step 1: Load orders
        response = requests.get(f"{base_url}/api/v1/marketplaces/mirakl/orders?status=PENDING&limit=5")
        if response.status_code != 200:
            print(f"❌ Failed to load orders: {response.status_code}")
            return False
        
        orders = response.json().get("orders", [])
        print(f"✅ Loaded {len(orders)} orders")
        
        if len(orders) == 0:
            print("⚠️  No orders found, but API call succeeded")
            return True
        
        # Step 2: Create shipments
        shipments_response = requests.post(
            f"{base_url}/api/v1/carriers/tipsa/shipments/bulk",
            json={"shipments": orders}
        )
        if shipments_response.status_code != 200:
            print(f"❌ Failed to create shipments: {shipments_response.status_code}")
            return False
        
        shipments = shipments_response.json().get("shipments", [])
        print(f"✅ Created {len(shipments)} shipments")
        
        # Step 3: Upload tracking
        tracking_data = [
            {
                "order_id": shipment["order_id"],
                "tracking_number": shipment["tracking_number"],
                "carrier_code": "tipsa",
                "carrier_name": "TIPSA"
            }
            for shipment in shipments
        ]
        
        tracking_response = requests.post(
            f"{base_url}/api/v1/orchestrator/upload-tracking",
            json=tracking_data
        )
        if tracking_response.status_code != 200:
            print(f"❌ Failed to upload tracking: {tracking_response.status_code}")
            return False
        
        print(f"✅ Uploaded tracking for {len(tracking_data)} orders")
        return True
        
    except Exception as e:
        print(f"❌ Error triggering API calls: {e}")
        return False


def main():
    """Main verification function."""
    print("🔍 Verifying CSV logging functionality...")
    
    # Configuration
    base_url = "http://localhost:8080"
    logs_dir = Path("backend/logs")
    
    # Check if backend is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend is not running or not healthy: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to backend at {base_url}")
        print("   Make sure the backend is running with: docker-compose up -d backend")
        sys.exit(1)
    
    print(f"✅ Backend is running at {base_url}")
    
    # Trigger API calls to generate logs
    if not trigger_api_calls(base_url):
        print("❌ Failed to trigger API calls")
        sys.exit(1)
    
    # Wait a moment for logs to be written
    time.sleep(2)
    
    # Check logs directory
    if not check_logs_directory(logs_dir):
        sys.exit(1)
    
    # Check operations CSV
    if not check_operations_csv(logs_dir):
        sys.exit(1)
    
    # Check dumps directory
    if not check_dumps_directory(logs_dir):
        sys.exit(1)
    
    print("\n🎉 All logging checks passed!")
    print("✅ CSV logging is working correctly")
    print("✅ JSON dumps are being generated")
    print("✅ Log files are properly formatted")


if __name__ == "__main__":
    main()

