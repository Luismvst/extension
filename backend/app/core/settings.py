"""
Application settings and configuration.

This module contains all configuration settings for the application,
including environment variables, API endpoints, and feature flags.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = {
        "extra": "allow",
        "env_file": ".env",
        "case_sensitive": False
    }
    
    # Application
    app_name: str = "Mirakl-TIPSA Orchestrator"
    app_version: str = "0.2.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Mirakl API
    mirakl_api_key: Optional[str] = None
    mirakl_shop_id: Optional[str] = None
    mirakl_base_url: str = "https://marketplace.mirakl.net" # https://sandbox.mirakl.net
    mirakl_mock_mode: bool = True
    
    # TIPSA API
    tipsa_api_key: Optional[str] = None
    tipsa_base_url: str = "https://api.tipsa.com"
    tipsa_mock_mode: bool = True
    
    # OnTime API
    ontime_api_key: Optional[str] = None
    ontime_base_url: str = "https://api.ontime.com"
    ontime_mock_mode: bool = True
    
    # DHL API
    dhl_api_key: Optional[str] = None
    dhl_api_secret: Optional[str] = None
    dhl_account: Optional[str] = None
    dhl_base_url: str = "https://api-eu.dhl.com"
    dhl_mock_mode: bool = True
    
    # UPS API
    ups_access_key: Optional[str] = None
    ups_username: Optional[str] = None
    ups_password: Optional[str] = None
    ups_account_number: Optional[str] = None
    ups_base_url: str = "https://onlinetools.ups.com"
    ups_mock_mode: bool = True
    
    # SEUR API
    seur_api_key: Optional[str] = None
    seur_base_url: str = "https://api.seur.com"
    seur_mock_mode: bool = True
    
    # Correos Express API
    correosex_api_key: Optional[str] = None
    correosex_base_url: str = "https://api.correosex.com"
    correosex_mock_mode: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "/app/logs/orchestrator.log"
    csv_log_file: str = "/app/logs/operations.csv"
    json_dumps_dir: str = "/app/logs/dumps"
    
    # Business Rules
    default_carrier: str = "tipsa"
    max_weight_kg: float = 30.0
    min_weight_kg: float = 0.1
    
    # Configuration moved to model_config above


# Global settings instance
settings = Settings()