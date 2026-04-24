"""FastAPI application setup and initialization."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Callable

from src.caas.config import settings
from src.caas.db.init import init_db
from src.caas.encryption.cipher import CipherManager
from src.caas.auth import TokenManager

# Import routes (must be after cipher_manager and token_manager are initialized)
# This import registers all routes with the app
import src.caas.api.routes  # noqa: F401

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize global instances
cipher_manager = CipherManager(settings.encryption_key)
token_manager = TokenManager(
    settings.jwt_secret_key,
    settings.jwt_algorithm,
    settings.jwt_expiration_hours
)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title="Config-as-a-Service",
        description="Centralized configuration management API",
        version="0.1.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize database on application startup."""
        logger.info("Initializing database...")
        init_db()
        logger.info(f"✓ Application started on {settings.host}:{settings.port}")

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

    return app


# Create app instance
app = create_app()
