"""AuditLog model — immutable log of all actions for transparency."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g. draft_created, review_completed
    entity_type = Column(String(50), nullable=True)  # e.g. draft, brand_kit
    entity_id = Column(GUID, nullable=True)
    details = Column(JSON, nullable=True)  # Additional context
    ai_service_used = Column(String(100), nullable=True)  # Transparency: which AI was used
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace = relationship("Workspace", back_populates="audit_logs")
