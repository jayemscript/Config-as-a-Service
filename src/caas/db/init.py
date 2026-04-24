"""Database initialization and setup."""

from src.caas.db.config import engine, Base


def init_db():
    """Initialize database by creating all tables."""
    # Create all tables defined in Base
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully")


def reset_db():
    """Drop all tables (USE WITH CAUTION)."""
    Base.metadata.drop_all(bind=engine)
    print("✓ Database reset - all tables dropped")
