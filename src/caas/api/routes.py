"""API routes for Config-as-a-Service."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from src.caas.db.config import get_db
from src.caas.db.models import Configuration, EnvironmentType
from src.caas.api.schemas import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationPartialUpdate,
    ConfigurationDelete,
    ConfigurationResponse,
    PaginatedResponse,
    TokenResponse,
)
# ✅ Import from dependencies, NOT from src.caas.main (that caused the circular import)
from src.caas.dependencies import cipher_manager, token_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cass", tags=["configuration"])


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/auth/token", response_model=TokenResponse, tags=["auth"])
async def generate_token():
    """
    Generate a new JWT token for API access.

    Returns:
        TokenResponse with access token and expiration
    """
    try:
        token = token_manager.generate_token({"sub": "caas-client"})
        return TokenResponse(
            access_token=token,
            expires_in=token_manager.expiration_hours * 3600
        )
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate token")


# ============================================================================
# Configuration CRUD Endpoints
# ============================================================================

@router.post("/create", response_model=ConfigurationResponse, status_code=201)
async def create_configuration(
    config: ConfigurationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new configuration entry.

    - Validates app_name + environment_type uniqueness
    - Encrypts configuration values before storage
    - Initializes version to 1
    """
    try:
        existing = db.query(Configuration).filter(
            Configuration.app_name == config.app_name,
            Configuration.environment_type == config.environment_type
        ).first()

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Configuration for '{config.app_name}' in {config.environment_type} already exists"
            )

        encrypted_values = cipher_manager.encrypt_dict(config.values)

        new_config = Configuration(
            app_name=config.app_name,
            environment_type=config.environment_type,
            values=encrypted_values,
            version=1
        )

        db.add(new_config)
        db.commit()
        db.refresh(new_config)

        decrypted = cipher_manager.decrypt_dict(new_config.values)

        logger.info(f"Created configuration: {config.app_name} ({config.environment_type})")
        return ConfigurationResponse(
            id=new_config.id,
            app_name=new_config.app_name,
            environment_type=new_config.environment_type,
            values=decrypted,
            version=new_config.version,
            created_at=new_config.created_at,
            updated_at=new_config.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration creation failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{app_name}", response_model=ConfigurationResponse)
async def get_configuration(
    app_name: str,
    environment_type: Optional[EnvironmentType] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieve a configuration by app_name and optional environment_type.

    - If environment_type not specified, returns the first match
    - Automatically decrypts values before returning
    """
    try:
        query = db.query(Configuration).filter(Configuration.app_name == app_name)

        if environment_type:
            query = query.filter(Configuration.environment_type == environment_type)

        config = query.first()

        if not config:
            raise HTTPException(status_code=404, detail=f"Configuration '{app_name}' not found")

        decrypted = cipher_manager.decrypt_dict(config.values)

        logger.info(f"Retrieved configuration: {app_name}")
        return ConfigurationResponse(
            id=config.id,
            app_name=config.app_name,
            environment_type=config.environment_type,
            values=decrypted,
            version=config.version,
            created_at=config.created_at,
            updated_at=config.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=ConfigurationResponse)
async def update_configuration(
    config_update: ConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """
    Fully replace configuration values.

    - Replaces entire values object
    - Increments version number
    - Updates updated_at timestamp
    """
    try:
        config = db.query(Configuration).filter(
            Configuration.app_name == config_update.app_name,
            Configuration.environment_type == config_update.environment_type
        ).first()

        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")

        encrypted_values = cipher_manager.encrypt_dict(config_update.values)

        config.values = encrypted_values
        config.version += 1

        db.commit()
        db.refresh(config)

        decrypted = cipher_manager.decrypt_dict(config.values)

        logger.info(f"Updated configuration: {config_update.app_name} (v{config.version})")
        return ConfigurationResponse(
            id=config.id,
            app_name=config.app_name,
            environment_type=config.environment_type,
            values=decrypted,
            version=config.version,
            created_at=config.created_at,
            updated_at=config.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration update failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/update/partial", response_model=ConfigurationResponse)
async def partial_update_configuration(
    config_update: ConfigurationPartialUpdate,
    db: Session = Depends(get_db)
):
    """
    Partially update configuration values (merge).

    - Merges new values with existing (only updates specified keys)
    - Increments version number
    - Updates updated_at timestamp
    """
    try:
        config = db.query(Configuration).filter(
            Configuration.app_name == config_update.app_name,
            Configuration.environment_type == config_update.environment_type
        ).first()

        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")

        existing_values = cipher_manager.decrypt_dict(config.values)
        existing_values.update(config_update.values)
        encrypted_values = cipher_manager.encrypt_dict(existing_values)

        config.values = encrypted_values
        config.version += 1

        db.commit()
        db.refresh(config)

        decrypted = cipher_manager.decrypt_dict(config.values)

        logger.info(f"Partially updated configuration: {config_update.app_name} (v{config.version})")
        return ConfigurationResponse(
            id=config.id,
            app_name=config.app_name,
            environment_type=config.environment_type,
            values=decrypted,
            version=config.version,
            created_at=config.created_at,
            updated_at=config.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Partial configuration update failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/paginated", response_model=PaginatedResponse)
async def list_configurations_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    environment_type: Optional[EnvironmentType] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List all configurations with server-side pagination.

    - Supports pagination (page, limit)
    - Supports search by app_name
    - Supports filtering by environment_type
    - Returns paginated result with metadata
    """
    try:
        query = db.query(Configuration)

        if search:
            query = query.filter(Configuration.app_name.ilike(f"%{search}%"))

        if environment_type:
            query = query.filter(Configuration.environment_type == environment_type)

        total = query.count()
        offset = (page - 1) * limit
        pages = (total + limit - 1) // limit
        configs = query.offset(offset).limit(limit).all()

        items = []
        for config in configs:
            decrypted = cipher_manager.decrypt_dict(config.values)
            items.append(ConfigurationResponse(
                id=config.id,
                app_name=config.app_name,
                environment_type=config.environment_type,
                values=decrypted,
                version=config.version,
                created_at=config.created_at,
                updated_at=config.updated_at
            ))

        logger.info(f"Listed configurations: page {page}, limit {limit}, total {total}")
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

    except Exception as e:
        logger.error(f"Configuration listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_configuration(
    config_delete: ConfigurationDelete,
    db: Session = Depends(get_db)
):
    """
    Permanently delete a configuration.

    - Requires app_name and environment_type
    - Operation is irreversible
    """
    try:
        config = db.query(Configuration).filter(
            Configuration.app_name == config_delete.app_name,
            Configuration.environment_type == config_delete.environment_type
        ).first()

        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")

        db.delete(config)
        db.commit()

        logger.info(f"Deleted configuration: {config_delete.app_name}")
        return {
            "message": f"Configuration '{config_delete.app_name}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration deletion failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

