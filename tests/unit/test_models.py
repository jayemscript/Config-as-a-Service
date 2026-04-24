"""Unit tests for database models."""

import pytest
from datetime import datetime
from src.caas.db.models import Configuration, EnvironmentType


class TestConfigurationModel:
    """Test suite for Configuration model."""

    def test_create_configuration(self, test_db):
        """Test creating a configuration."""
        config = Configuration(
            app_name="test_app",
            environment_type=EnvironmentType.DEVELOPMENT,
            values='{"key": "value"}',
            version=1
        )
        
        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)
        
        assert config.id is not None
        assert config.app_name == "test_app"
        assert config.environment_type == EnvironmentType.DEVELOPMENT
        assert config.version == 1
        assert isinstance(config.created_at, datetime)
        assert isinstance(config.updated_at, datetime)

    def test_configuration_defaults(self, test_db):
        """Test default values for configuration."""
        config = Configuration(
            app_name="test",
            environment_type=EnvironmentType.PRODUCTION,
            values="{}"
        )
        
        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)
        
        assert config.version == 1
        assert config.values == "{}"
        assert config.created_at == config.updated_at

    def test_environment_type_enum(self):
        """Test EnvironmentType enum values."""
        assert EnvironmentType.DEVELOPMENT.value == "DEVELOPMENT"
        assert EnvironmentType.STAGING.value == "STAGING"
        assert EnvironmentType.PRODUCTION.value == "PRODUCTION"

    def test_configuration_query_by_app_name(self, test_db):
        """Test querying configuration by app_name."""
        config1 = Configuration(
            app_name="app1",
            environment_type=EnvironmentType.DEVELOPMENT,
            values="{}"
        )
        config2 = Configuration(
            app_name="app2",
            environment_type=EnvironmentType.DEVELOPMENT,
            values="{}"
        )
        
        test_db.add_all([config1, config2])
        test_db.commit()
        
        result = test_db.query(Configuration).filter_by(app_name="app1").first()
        assert result.app_name == "app1"

    def test_unique_constraint_by_env(self, test_db):
        """Test that same app can exist in different environments."""
        config1 = Configuration(
            app_name="app",
            environment_type=EnvironmentType.DEVELOPMENT,
            values="{}"
        )
        config2 = Configuration(
            app_name="app",
            environment_type=EnvironmentType.PRODUCTION,
            values="{}"
        )
        
        test_db.add_all([config1, config2])
        test_db.commit()
        
        dev = test_db.query(Configuration).filter_by(
            app_name="app",
            environment_type=EnvironmentType.DEVELOPMENT
        ).first()
        prod = test_db.query(Configuration).filter_by(
            app_name="app",
            environment_type=EnvironmentType.PRODUCTION
        ).first()
        
        assert dev is not None
        assert prod is not None
        assert dev.id != prod.id
