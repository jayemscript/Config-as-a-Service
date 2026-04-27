"""
Shared application dependencies — cipher_manager and token_manager.

Kept in a separate module so both main.py and routes.py can import
from here without creating a circular dependency.
"""

from src.caas.config import settings
from src.caas.encryption.cipher import CipherManager
from src.caas.auth import TokenManager

cipher_manager = CipherManager(settings.encryption_key)

token_manager = TokenManager(
    settings.jwt_secret_key,
    settings.jwt_algorithm,
    settings.jwt_expiration_hours,
)