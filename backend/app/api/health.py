"""
Health check endpoints
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.core.settings import get_settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.version,
        "environment": settings.environment
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with system information"""
    try:
        import psutil
        import platform
        
        # System information
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent
        }
        
        # Application information
        app_info = {
            "name": settings.app_name,
            "version": settings.version,
            "environment": settings.environment,
            "debug": settings.debug,
            "log_level": settings.log_level
        }
        
        # Health status
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": "unknown",  # Would need to track start time
            "checks": {
                "database": "ok",  # Placeholder
                "external_apis": "ok",  # Placeholder
                "storage": "ok"  # Placeholder
            }
        }
        
        logger.log_business_event("health_check_detailed")
        
        return {
            **health_status,
            "system": system_info,
            "application": app_info
        }
        
    except ImportError:
        # psutil not available, return basic info
        logger.log_event("WARNING", "psutil not available for detailed health check")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version,
            "environment": settings.environment,
            "note": "Detailed system info not available"
        }
        
    except Exception as e:
        logger.log_error(e, "detailed_health_check")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/ready")
async def readiness_check():
    """Readiness check for load balancers"""
    try:
        # Check if application is ready to serve requests
        # This could include database connectivity, external API availability, etc.
        
        ready = True
        checks = {}
        
        # Add your readiness checks here
        # Example: database connectivity, external API availability
        
        if ready:
            return {
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": checks
            }
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        logger.log_error(e, "readiness_check")
        raise HTTPException(status_code=503, detail="Readiness check failed")


@router.get("/live")
async def liveness_check():
    """Liveness check for container orchestration"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
