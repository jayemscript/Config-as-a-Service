"""Pytest configuration and shared fixtures."""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.caas.db.config import Base, get_db
from src.caas.main import app, cipher_manager, token_manager
from src.caas.encryption.cipher import CipherManager
from src.caas.auth import TokenManager


# Create in-memory SQLite database for tests
@pytest.fixture(scope="function")
def test_db():
    """Create a fresh in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield SessionLocal()
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with in-memory database."""
    return TestClient(app)


@pytest.fixture(scope="function")
def valid_token():
    """Generate a valid JWT token for testing."""
    return token_manager.generate_token({"sub": "test-user"})


@pytest.fixture(scope="function")
def test_cipher():
    """Create a cipher manager for testing."""
    key = CipherManager.generate_key()
    return CipherManager(key)
