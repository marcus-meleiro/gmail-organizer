from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(settings.database_url, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

# Ensure the model classes are registered with SQLAlchemy metadata.
from app import models  # noqa: F401


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
