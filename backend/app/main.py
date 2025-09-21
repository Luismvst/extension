"""
Main FastAPI application.

This module creates and configures the FastAPI application
with all routes, middleware, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

# Import routers
from .api import marketplaces, carriers, orchestrator, health, auth, logs

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)
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
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging."""
    logger.error(f"Validation error on {request.method} {request.url}: {exc.errors()}")
    try:
        body = await request.body()
        logger.error(f"Request body: {body}")
    except Exception as e:
        logger.error(f"Could not read request body: {e}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

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
app.include_router(auth.router)
app.include_router(marketplaces.router)
app.include_router(carriers.router)
app.include_router(orchestrator.router)
app.include_router(logs.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)