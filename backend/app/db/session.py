"""
Database session and base model configuration.

Provides SQLAlchemy engine, session factory, and declarative base.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
