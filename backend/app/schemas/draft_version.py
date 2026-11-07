"""Pydantic schemas for DraftVersion (revision history) endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DraftVersionResponse(BaseModel):
    id: UUID
    draft_id: UUID
    version_number: int
    content: str
    change_summary: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DraftContentUpdate(BaseModel):
    """Payload to update the draft content (triggers a new version snapshot)."""
    content: str
    change_summary: Optional[str] = None
