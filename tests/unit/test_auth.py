"""Unit tests for JWT authentication."""

import pytest
import jwt
from datetime import datetime, timezone, timedelta
from src.caas.auth import TokenManager


class TestTokenManager:
    """Test suite for TokenManager."""

    @pytest.fixture
    def token_manager_instance(self):
        """Create a token manager for testing."""
        return TokenManager(
            secret_key="test-secret-key",
            algorithm="HS256",
            expiration_hours=24
        )

    def test_generate_token(self, token_manager_instance):
        """Test token generation."""
        data = {"sub": "test-user"}
        token = token_manager_instance.generate_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self, token_manager_instance):
        """Test verification of valid token."""
        data = {"sub": "test-user"}
        token = token_manager_instance.generate_token(data)
        
        payload = token_manager_instance.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user"

    def test_verify_invalid_token(self, token_manager_instance):
        """Test verification of invalid token."""
        result = token_manager_instance.verify_token("invalid-token")
        assert result is None

    def test_verify_expired_token(self):
        """Test verification of expired token."""
        manager = TokenManager(
            secret_key="test-key",
            algorithm="HS256",
            expiration_hours=-1  # Already expired
        )
        
        data = {"sub": "test"}
        token = manager.generate_token(data)
        
        # Try to verify with the same manager
        result = manager.verify_token(token)
        assert result is None

    def test_token_contains_data(self, token_manager_instance):
        """Test that token contains provided data."""
        data = {"user_id": 123, "username": "testuser"}
        token = token_manager_instance.generate_token(data)
        
        payload = token_manager_instance.verify_token(token)
        assert payload["user_id"] == 123
        assert payload["username"] == "testuser"

    def test_token_expiration_claim(self, token_manager_instance):
        """Test that token includes expiration claim."""
        token = token_manager_instance.generate_token({})
        payload = token_manager_instance.verify_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)

    def test_different_secrets_cant_verify(self):
        """Test that tokens can't be verified with different secrets."""
        manager1 = TokenManager(secret_key="secret1")
        manager2 = TokenManager(secret_key="secret2")
        
        token = manager1.generate_token({"sub": "test"})
        result = manager2.verify_token(token)
        
        assert result is None
