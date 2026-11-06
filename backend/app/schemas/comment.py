"""Pydantic schemas for Comment endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: UUID
    draft_id: UUID
    user_id: UUID
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
