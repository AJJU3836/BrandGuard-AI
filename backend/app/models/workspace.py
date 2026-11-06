"""Workspace model — isolated tenant for a brand / organisation."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    members = relationship("User", back_populates="workspace")
    brand_kits = relationship("BrandKit", back_populates="workspace", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="workspace", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="workspace", cascade="all, delete-orphan")
