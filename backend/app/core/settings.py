"""
Application settings using Pydantic Settings
"""
from typing import List, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Mirakl CSV Backend"
    version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = Field(default=8080, ge=1, le=65535)
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: str = "json"
    
    # CORS
    allowed_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "chrome-extension://*"
        ]
    )
    
    # External APIs (for future use)
    tipsa_api_url: str = ""
    tipsa_api_token: str = ""
    ontime_api_url: str = ""
    ontime_api_token: str = ""
    
    # Mirakl API (for future use)
    mirakl_api_url: str = ""
    mirakl_api_token: str = ""
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Data retention
    cleanup_days: int = 7
    max_orders_per_request: int = 1000


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
