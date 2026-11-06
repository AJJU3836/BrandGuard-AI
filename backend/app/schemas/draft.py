"""Pydantic schemas for Draft endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DraftCreate(BaseModel):
    title: str
    content: str
    content_type: str = "other"  # social_post | blog | email | ad | other


class DraftResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    creator_id: UUID
    title: str
    content: str
    content_type: str
    status: str
    reviewer_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DraftStatusUpdate(BaseModel):
    status: str  # draft | in_review | changes_requested | approved
