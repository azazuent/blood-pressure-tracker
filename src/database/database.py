import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


class Database:
    """Database connection and session management."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


# Global database instance
db_instance: Database = None


def init_database(database_url: str) -> Database:
    """Initialize global database instance."""
    global db_instance
    
    # Ensure directory exists for SQLite databases
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '', 1)
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    db_instance = Database(database_url)
    db_instance.create_tables()
    return db_instance


def get_database() -> Database:
    """Get the global database instance."""
    if db_instance is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db_instance
