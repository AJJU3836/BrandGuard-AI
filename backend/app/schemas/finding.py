"""Pydantic schemas for Finding endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FindingResponse(BaseModel):
    id: UUID
    draft_id: UUID
    severity: str
    category: str
    text_highlight: Optional[str] = None
    explanation: str
    guideline_source: Optional[str] = None
    suggestion: Optional[str] = None
    status: str
    is_ai_generated: bool
    confidence: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FindingStatusUpdate(BaseModel):
    status: str  # accepted | rejected
