"""Draft model — content submitted for brand review."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id"), nullable=False)
    creator_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="other")  # social_post | blog | email | ad | other
    status = Column(String(50), default="draft")  # draft | in_review | changes_requested | approved
    reviewer_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace = relationship("Workspace", back_populates="drafts")
    creator = relationship("User", back_populates="drafts", foreign_keys=[creator_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    findings = relationship("Finding", back_populates="draft", cascade="all, delete-orphan")
    versions = relationship("DraftVersion", back_populates="draft", cascade="all, delete-orphan", order_by="DraftVersion.version_number")
    comments = relationship("Comment", back_populates="draft", cascade="all, delete-orphan")
