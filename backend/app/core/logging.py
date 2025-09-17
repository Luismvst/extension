"""
Logging configuration
"""
import logging
import sys
from typing import Any, Dict

from pythonjsonlogger import jsonlogger
from app.core.settings import get_settings


def setup_logging() -> None:
    """Setup application logging"""
    settings = get_settings()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))
    
    # Set formatter based on log format
    if settings.log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


class StructuredLogger:
    """Structured logger for application events"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(
        self,
        level: str,
        message: str,
        **kwargs: Any
    ) -> None:
        """Log structured event"""
        log_data = {
            "event": message,
            "level": level,
            **kwargs
        }
        
        if level.upper() == "DEBUG":
            self.logger.debug(message, extra=log_data)
        elif level.upper() == "INFO":
            self.logger.info(message, extra=log_data)
        elif level.upper() == "WARNING":
            self.logger.warning(message, extra=log_data)
        elif level.upper() == "ERROR":
            self.logger.error(message, extra=log_data)
        elif level.upper() == "CRITICAL":
            self.logger.critical(message, extra=log_data)
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs: Any
    ) -> None:
        """Log HTTP request"""
        self.log_event(
            "INFO",
            "HTTP request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_error(
        self,
        error: Exception,
        context: str = "",
        **kwargs: Any
    ) -> None:
        """Log error with context"""
        self.log_event(
            "ERROR",
            f"Error in {context}: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )
    
    def log_business_event(
        self,
        event_type: str,
        **kwargs: Any
    ) -> None:
        """Log business event"""
        self.log_event(
            "INFO",
            f"Business event: {event_type}",
            event_type=event_type,
            **kwargs
        )


def get_logger(name: str) -> StructuredLogger:
    """Get structured logger instance"""
    return StructuredLogger(name)
