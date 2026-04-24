"""Encryption utilities using Fernet symmetric encryption."""

from cryptography.fernet import Fernet, InvalidToken
from typing import Any, Dict
import json
import logging

logger = logging.getLogger(__name__)


class CipherManager:
    """Manages encryption and decryption of configuration values."""

    def __init__(self, key: str):
        """
        Initialize cipher manager with encryption key.
        
        Args:
            key: Fernet encryption key (base64-encoded)
        """
        try:
            self.cipher_suite = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            logger.error(f"Failed to initialize cipher: {e}")
            raise ValueError("Invalid encryption key format. Must be a valid Fernet key.")

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt a dictionary of configuration values.
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Encrypted string (base64-encoded)
        """
        try:
            json_str = json.dumps(data)
            encrypted = self.cipher_suite.encrypt(json_str.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt an encrypted configuration value.
        
        Args:
            encrypted_data: Encrypted string to decrypt
            
        Returns:
            Decrypted dictionary
        """
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
            return json.loads(decrypted.decode())
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or corrupted data")
            raise ValueError("Failed to decrypt configuration. Token may be invalid or corrupted.")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Base64-encoded Fernet key
        """
        return Fernet.generate_key().decode()
