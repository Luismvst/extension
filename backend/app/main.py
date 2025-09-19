"""
Main FastAPI application.

This module creates and configures the FastAPI application
with all routes, middleware, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import routers
from .api import marketplaces, carriers, orchestrator, health

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Mirakl-TIPSA Orchestrator Backend")
    logger.info("Environment: development")
    logger.info("Log level: INFO")
    logger.info("Mirakl mode: mock")
    logger.info("TIPSA mode: mock")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mirakl-TIPSA Orchestrator Backend")


# Create FastAPI application
app = FastAPI(
    title="Mirakl-TIPSA Orchestrator",
    version="0.2.0",
    description="Orchestrator for Mirakl marketplace orders to TIPSA carrier",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mirakl-TIPSA Orchestrator Backend",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs"
    }


# Include routers
app.include_router(health.router)
app.include_router(marketplaces.router)
app.include_router(carriers.router)
app.include_router(orchestrator.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)