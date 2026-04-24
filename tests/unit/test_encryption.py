"""Unit tests for encryption utilities."""

import pytest
import json
from src.caas.encryption.cipher import CipherManager


class TestCipherManager:
    """Test suite for CipherManager."""

    def test_generate_key(self):
        """Test key generation."""
        key = CipherManager.generate_key()
        assert key is not None
        assert isinstance(key, str)
        assert len(key) > 0

    def test_encrypt_decrypt_dict(self, test_cipher):
        """Test encryption and decryption of dictionaries."""
        original = {
            "DB_NAME": "mydb",
            "DB_PASSWORD": "secret",
            "API_KEY": "key123"
        }
        
        # Encrypt
        encrypted = test_cipher.encrypt_dict(original)
        assert isinstance(encrypted, str)
        assert encrypted != json.dumps(original)
        
        # Decrypt
        decrypted = test_cipher.decrypt_dict(encrypted)
        assert decrypted == original

    def test_encrypt_empty_dict(self, test_cipher):
        """Test encryption of empty dictionary."""
        original = {}
        encrypted = test_cipher.encrypt_dict(original)
        decrypted = test_cipher.decrypt_dict(encrypted)
        assert decrypted == original

    def test_encrypt_complex_values(self, test_cipher):
        """Test encryption of complex data types."""
        original = {
            "string": "value",
            "number": 123,
            "float": 45.67,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        encrypted = test_cipher.encrypt_dict(original)
        decrypted = test_cipher.decrypt_dict(encrypted)
        assert decrypted == original

    def test_invalid_key(self):
        """Test cipher manager with invalid key."""
        with pytest.raises(ValueError):
            CipherManager("invalid-key")

    def test_decrypt_invalid_token(self, test_cipher):
        """Test decryption of invalid token."""
        with pytest.raises(ValueError):
            test_cipher.decrypt_dict("invalid-encrypted-data")

    def test_different_keys_cant_decrypt(self):
        """Test that data encrypted with one key can't be decrypted with another."""
        from src.caas.encryption.cipher import CipherManager
        
        key1 = CipherManager.generate_key()
        key2 = CipherManager.generate_key()
        
        cipher1 = CipherManager(key1)
        cipher2 = CipherManager(key2)
        
        data = {"secret": "value"}
        encrypted = cipher1.encrypt_dict(data)
        
        with pytest.raises(ValueError):
            cipher2.decrypt_dict(encrypted)
