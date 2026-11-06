"""BrandKit model — an organisation's brand guidelines, terms, facts, and assets."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID


class BrandKit(Base):
    __tablename__ = "brand_kits"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    guidelines_raw = Column(Text, nullable=True)  # Raw uploaded guideline text
    terminology_approved = Column(JSON, default=list)  # ["BrandGuard", "AI-powered"]
    terminology_banned = Column(JSON, default=list)  # ["cheap", "guarantee"]
    tone_rules = Column(JSON, default=list)  # ["Professional", "Avoid slang"]
    approved_facts = Column(JSON, default=list)  # ["Founded in 2024", "500+ clients"]
    color_palette = Column(JSON, default=list)  # ["#1E40AF", "#F59E0B"]
    is_indexed = Column(Boolean, default=False)  # True once guideline vectors are built
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace = relationship("Workspace", back_populates="brand_kits")
    guideline_chunks = relationship("GuidelineChunk", back_populates="brand_kit", cascade="all, delete-orphan")
