"""Finding model — an issue detected during brand review."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID


class Finding(Base):
    __tablename__ = "findings"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    draft_id = Column(GUID, ForeignKey("drafts.id"), nullable=False)
    severity = Column(String(20), nullable=False)  # error | warning | info
    category = Column(String(50), nullable=False)  # tone | terminology | claim | visual | accessibility | factual
    text_highlight = Column(Text, nullable=True)  # The flagged text snippet
    explanation = Column(Text, nullable=False)  # Why it was flagged
    guideline_source = Column(Text, nullable=True)  # The cited guideline clause
    suggestion = Column(Text, nullable=True)  # Suggested fix
    status = Column(String(20), default="open")  # open | accepted | rejected
    is_ai_generated = Column(Boolean, default=True)
    confidence = Column(Float, nullable=True)  # 0.0 - 1.0
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    draft = relationship("Draft", back_populates="findings")
