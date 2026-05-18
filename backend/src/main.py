"""
Main FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.core.config import Config
from src.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI app."""
    # Startup
    logger.info("HDR Blender Backend Starting...")
    logger.info(f"Configuration: {Config.__dict__}")
    yield
    # Shutdown
    logger.info("HDR Blender Backend Shutting Down...")


# Create FastAPI app
app = FastAPI(
    title="HDR Blender API",
    description="Professional exposure fusion for photographers",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware for Tauri frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "HDR Blender API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        workers=Config.API_WORKERS,
        log_level=Config.LOG_LEVEL.lower(),
    )
