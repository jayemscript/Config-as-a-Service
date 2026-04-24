"""SQLAlchemy models for Config-as-a-Service."""

from sqlalchemy import Column, String, Integer, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from datetime import datetime
import uuid
from enum import Enum

from src.caas.db.config import Base


class EnvironmentType(str, Enum):
    """Enum for environment types."""
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class Configuration(Base):
    """Configuration table model."""
    __tablename__ = "configurations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    app_name = Column(String(255), nullable=False, index=True)
    environment_type = Column(SQLEnum(EnvironmentType), nullable=False, index=True)
    values = Column(SQLITE_JSON, nullable=False, default={})
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Configuration(id={self.id}, app_name={self.app_name}, env={self.environment_type})>"
