"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class EnvironmentTypeEnum(str, Enum):
    """Environment type enum."""
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class ConfigurationCreate(BaseModel):
    """Schema for creating a new configuration."""
    app_name: str = Field(..., min_length=1, max_length=255, description="Application name (unique per environment)")
    environment_type: EnvironmentTypeEnum = Field(..., description="Environment type")
    values: Dict[str, Any] = Field(default_factory=dict, description="Configuration key-value pairs")

    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "my_app",
                "environment_type": "DEVELOPMENT",
                "values": {
                    "DB_NAME": "my_db",
                    "DB_PASSWORD": "secret",
                    "API_KEY": "key123"
                }
            }
        }


class ConfigurationUpdate(BaseModel):
    """Schema for updating an entire configuration."""
    app_name: str = Field(..., min_length=1, max_length=255)
    environment_type: EnvironmentTypeEnum
    values: Dict[str, Any] = Field(description="New configuration values (replaces entire values object)")

    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "my_app",
                "environment_type": "DEVELOPMENT",
                "values": {
                    "DB_NAME": "updated_db",
                    "DB_PASSWORD": "newsecret",
                    "API_KEY": "newkey123"
                }
            }
        }


class ConfigurationPartialUpdate(BaseModel):
    """Schema for partially updating a configuration."""
    app_name: str = Field(..., min_length=1, max_length=255)
    environment_type: EnvironmentTypeEnum
    values: Dict[str, Any] = Field(description="Partial configuration values (merges with existing)")

    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "my_app",
                "environment_type": "DEVELOPMENT",
                "values": {
                    "DB_PASSWORD": "newsecret"
                }
            }
        }


class ConfigurationDelete(BaseModel):
    """Schema for deleting a configuration."""
    app_name: str = Field(..., min_length=1, max_length=255)
    environment_type: EnvironmentTypeEnum


class ConfigurationResponse(BaseModel):
    """Schema for configuration response."""
    id: str
    app_name: str
    environment_type: EnvironmentTypeEnum
    values: Dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Schema for paginated response."""
    items: List[ConfigurationResponse]
    total: int
    page: int
    limit: int
    pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "limit": 10,
                "pages": 0
            }
        }


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str
    status_code: int
