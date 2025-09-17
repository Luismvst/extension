"""
API routers
"""
from fastapi import APIRouter
from app.api import health, map_router, ship_router, tracking_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(map_router.router, prefix="/map", tags=["mapping"])
router.include_router(ship_router.router, prefix="/ship", tags=["shipping"])
router.include_router(tracking_router.router, prefix="/tracking", tags=["tracking"])
