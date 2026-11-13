"""Pydantic schemas for Draft endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, computed_field


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
    findings_count: Optional[int] = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        instance = super().model_validate(obj, *args, **kwargs)
        # Populate findings_count from relationship if available
        if hasattr(obj, "findings") and obj.findings is not None:
            instance.findings_count = len([f for f in obj.findings if f.status == "open"])
        return instance


class DraftStatusUpdate(BaseModel):
    status: str  # draft | in_review | changes_requested | approved

