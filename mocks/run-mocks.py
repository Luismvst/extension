#!/usr/bin/env python3
"""
Run Mock Servers

This script starts both TIPSA and Mirakl mock servers.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nShutting down mock servers...")
    sys.exit(0)

def main():
    """Start mock servers."""
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    print("Starting Mock Servers...")
    print("TIPSA Mock: http://localhost:3001")
    print("Mirakl Mock: http://localhost:3002")
    print("Press Ctrl+C to stop all servers")
    print("-" * 50)
    
    try:
        # Start TIPSA mock
        tipsa_process = subprocess.Popen([
            sys.executable, str(script_dir / "tipsa-mock.py")
        ])
        
        # Start Mirakl mock
        mirakl_process = subprocess.Popen([
            sys.executable, str(script_dir / "mirakl-mock.py")
        ])
        
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if tipsa_process.poll() is not None:
                print("TIPSA mock server stopped")
                break
            if mirakl_process.poll() is not None:
                print("Mirakl mock server stopped")
                break
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Terminate processes
        if 'tipsa_process' in locals():
            tipsa_process.terminate()
        if 'mirakl_process' in locals():
            mirakl_process.terminate()
        
        print("Mock servers stopped")

if __name__ == "__main__":
    main()
