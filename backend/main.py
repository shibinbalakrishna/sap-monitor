#!/usr/bin/env python3
"""
SAP Infrastructure Monitoring Platform - FastAPI Backend
Main entry point for the monitoring backend API.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import Settings
from config.database import engine, get_db_session
from models.database import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = Settings()

# Startup/Shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("Starting SAP Infrastructure Monitoring Platform")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SAP Infrastructure Monitoring Platform")
    await engine.dispose()

# Create FastAPI application
app = FastAPI(
    title="SAP Infrastructure Monitoring Platform",
    description="AI-driven monitoring for SAP systems with predictive analytics",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring platform.
    
    Returns:
        dict: Status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "sap-monitor-backend",
        "version": "1.0.0"
    }

# API root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    API root endpoint with documentation links.
    
    Returns:
        dict: Welcome message and API documentation links
    """
    return {
        "message": "SAP Infrastructure Monitoring Platform API",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
        "version": "1.0.0"
    }

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: HTTP request
        exc: Exception object
        
    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Include routers (to be implemented)
# from routes import servers, metrics, alerts, ai
# app.include_router(servers.router, prefix="/api/servers", tags=["Servers"])
# app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
# app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
# app.include_router(ai.router, prefix="/api/ai", tags=["AI Analytics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.FAST_API_HOST,
        port=settings.FAST_API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
