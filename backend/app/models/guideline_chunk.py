"""GuidelineChunk model — vectorized chunks of brand guidelines for RAG retrieval."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID


class GuidelineChunk(Base):
    __tablename__ = "guideline_chunks"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    brand_kit_id = Column(GUID, ForeignKey("brand_kits.id"), nullable=False)
    content = Column(Text, nullable=False)  # The chunk text
    chunk_index = Column(Integer, nullable=False)
    source_section = Column(String(255), nullable=True)  # Which section this came from
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    brand_kit = relationship("BrandKit", back_populates="guideline_chunks")
