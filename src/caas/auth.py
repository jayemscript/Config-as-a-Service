"""JWT authentication utilities."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import logging

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages JWT token generation and validation."""

    def __init__(self, secret_key: str, algorithm: str = "HS256", expiration_hours: int = 24):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            expiration_hours: Token expiration time in hours
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours

    def generate_token(self, data: dict) -> str:
        """
        Generate a JWT token.
        
        Args:
            data: Payload data to encode in token
            
        Returns:
            Encoded JWT token
        """
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(hours=self.expiration_hours)
            to_encode.update({"exp": expire})
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise

    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
