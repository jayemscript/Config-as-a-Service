"""Application settings and configuration for Config-as-a-Service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server Configuration
    port: int = 12500
    host: str = "127.0.0.1"
    
    # Database Configuration
    database_url: str = "sqlite:///./caas_data.db"
    
    # Encryption Configuration
    encryption_key: str  # Must be set in .env
    
    # JWT Configuration
    jwt_secret_key: str  # Must be set in .env
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Logging Configuration
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
