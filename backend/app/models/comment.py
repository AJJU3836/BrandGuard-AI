"""Comment model — reviewer/creator comments on a draft."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID


class Comment(Base):
    __tablename__ = "comments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    draft_id = Column(GUID, ForeignKey("drafts.id"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    draft = relationship("Draft", back_populates="comments")
    user = relationship("User", back_populates="comments")
