"""DraftVersion model — stores immutable content snapshots for revision history."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID


class DraftVersion(Base):
    __tablename__ = "draft_versions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    draft_id = Column(GUID, ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    change_summary = Column(Text, nullable=True)  # Optional: what changed (e.g., "Initial draft", "Post-review edit")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    draft = relationship("Draft", back_populates="versions")
