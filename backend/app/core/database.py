"""
BrandGuard AI — Database Setup

Supports PostgreSQL (production & vector search) and SQLite (offline dev & rapid testing).
Run `alembic init alembic` and `alembic revision --autogenerate` to set up migrations.
"""

import uuid
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import TypeDecorator, CHAR, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.config import get_settings

settings = get_settings()

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Ensure SSL mode for Render PostgreSQL if not already specified
if db_url.startswith("postgresql://") and "sslmode" not in db_url:
    separator = "&" if "?" in db_url else "?"
    db_url = f"{db_url}{separator}sslmode=require"

is_sqlite = db_url.startswith("sqlite")

engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True

try:
    engine = create_engine(db_url, **engine_kwargs)
    # Quick connectivity test
    if not is_sqlite:
        with engine.connect() as conn:
            print(" Connected to PostgreSQL database successfully.")
except Exception as e:
    print(f" Failed to initialize PostgreSQL ({e}). Falling back to SQLite.")
    from pathlib import Path
    _fallback_db = Path(__file__).resolve().parent.parent.parent / "brandguard_demo.db"
    db_url = f"sqlite:///{_fallback_db}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(str(value))
        return value


def get_db() -> Generator:
    """Yield a database session, closing it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
