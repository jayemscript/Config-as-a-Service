"""Integration tests for API routes."""

import pytest
import json
from src.caas.db.models import EnvironmentType


class TestConfigurationAPI:
    """Integration tests for configuration endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_generate_token(self, client):
        """Test token generation endpoint."""
        response = client.post("/cass/auth/token")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_create_configuration(self, client, valid_token):
        """Test creating a configuration."""
        payload = {
            "app_name": "test_app",
            "environment_type": "DEVELOPMENT",
            "values": {"DB_NAME": "testdb", "DB_PASSWORD": "secret"}
        }
        
        response = client.post(
            "/cass/create",
            json=payload,
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["app_name"] == "test_app"
        assert data["environment_type"] == "DEVELOPMENT"
        assert data["version"] == 1
        assert data["values"]["DB_NAME"] == "testdb"
        assert data["values"]["DB_PASSWORD"] == "secret"

    def test_create_duplicate_configuration(self, client, valid_token):
        """Test creating duplicate configuration (should fail)."""
        payload = {
            "app_name": "test_app",
            "environment_type": "DEVELOPMENT",
            "values": {"KEY": "value"}
        }
        
        # Create first time
        response1 = client.post("/cass/create", json=payload)
        assert response1.status_code == 201
        
        # Try to create again (should fail)
        response2 = client.post("/cass/create", json=payload)
        assert response2.status_code == 409

    def test_get_configuration(self, client, valid_token):
        """Test retrieving a configuration."""
        # Create first
        create_payload = {
            "app_name": "my_app",
            "environment_type": "DEVELOPMENT",
            "values": {"KEY": "value"}
        }
        client.post("/cass/create", json=create_payload)
        
        # Retrieve
        response = client.get("/cass/get/my_app")
        assert response.status_code == 200
        data = response.json()
        assert data["app_name"] == "my_app"
        assert data["values"]["KEY"] == "value"

    def test_get_nonexistent_configuration(self, client):
        """Test retrieving non-existent configuration."""
        response = client.get("/cass/get/nonexistent")
        assert response.status_code == 404

    def test_update_configuration(self, client):
        """Test full update of configuration."""
        # Create
        create_payload = {
            "app_name": "test",
            "environment_type": "STAGING",
            "values": {"OLD_KEY": "old_value"}
        }
        client.post("/cass/create", json=create_payload)
        
        # Update
        update_payload = {
            "app_name": "test",
            "environment_type": "STAGING",
            "values": {"NEW_KEY": "new_value"}
        }
        response = client.put("/cass/update", json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 2
        assert "NEW_KEY" in data["values"]
        assert "OLD_KEY" not in data["values"]

    def test_partial_update_configuration(self, client):
        """Test partial update (merge) of configuration."""
        # Create
        create_payload = {
            "app_name": "test",
            "environment_type": "PRODUCTION",
            "values": {"KEY1": "value1", "KEY2": "value2"}
        }
        client.post("/cass/create", json=create_payload)
        
        # Partial update
        update_payload = {
            "app_name": "test",
            "environment_type": "PRODUCTION",
            "values": {"KEY2": "updated_value2"}
        }
        response = client.patch("/cass/update/partial", json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 2
        assert data["values"]["KEY1"] == "value1"
        assert data["values"]["KEY2"] == "updated_value2"

    def test_list_configurations_paginated(self, client):
        """Test paginated listing of configurations."""
        # Create multiple configurations
        for i in range(15):
            payload = {
                "app_name": f"app_{i:02d}",
                "environment_type": "DEVELOPMENT",
                "values": {"id": i}
            }
            client.post("/cass/create", json=payload)
        
        # Get first page
        response = client.get("/cass/get/paginated?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["pages"] == 2

    def test_list_with_search(self, client):
        """Test listing with search filter."""
        # Create configurations
        client.post("/cass/create", json={
            "app_name": "backend_api",
            "environment_type": "DEVELOPMENT",
            "values": {}
        })
        client.post("/cass/create", json={
            "app_name": "frontend_app",
            "environment_type": "DEVELOPMENT",
            "values": {}
        })
        
        # Search for backend
        response = client.get("/cass/get/paginated?search=backend")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["app_name"] == "backend_api"

    def test_list_with_environment_filter(self, client):
        """Test listing with environment filter."""
        # Create same app in different environments
        for env in ["DEVELOPMENT", "STAGING", "PRODUCTION"]:
            client.post("/cass/create", json={
                "app_name": "myapp",
                "environment_type": env,
                "values": {}
            })
        
        # Filter by STAGING
        response = client.get("/cass/get/paginated?environment_type=STAGING")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["environment_type"] == "STAGING"

    def test_delete_configuration(self, client):
        """Test deleting a configuration."""
        # Create
        create_payload = {
            "app_name": "to_delete",
            "environment_type": "DEVELOPMENT",
            "values": {}
        }
        client.post("/cass/create", json=create_payload)
        
        # Delete
        delete_payload = {
            "app_name": "to_delete",
            "environment_type": "DEVELOPMENT"
        }
        response = client.delete("/cass/delete", json=delete_payload)
        assert response.status_code == 200
        
        # Verify it's gone
        response = client.get("/cass/get/to_delete")
        assert response.status_code == 404

    def test_delete_nonexistent_configuration(self, client):
        """Test deleting non-existent configuration."""
        payload = {
            "app_name": "nonexistent",
            "environment_type": "DEVELOPMENT"
        }
        response = client.delete("/cass/delete", json=payload)
        assert response.status_code == 404

    def test_encryption_round_trip(self, client):
        """Test that values are encrypted then decrypted correctly."""
        sensitive_data = {
            "DB_PASSWORD": "super_secret_password_123!@#",
            "API_KEY": "api_key_xyzabc",
            "TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        }
        
        payload = {
            "app_name": "secure_app",
            "environment_type": "PRODUCTION",
            "values": sensitive_data
        }
        
        # Create
        response1 = client.post("/cass/create", json=payload)
        assert response1.status_code == 201
        
        # Retrieve
        response2 = client.get("/cass/get/secure_app")
        assert response2.status_code == 200
        data = response2.json()
        
        # Verify all values are intact
        for key, value in sensitive_data.items():
            assert data["values"][key] == value
