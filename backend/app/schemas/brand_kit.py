"""Pydantic schemas for BrandKit endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class BrandKitCreate(BaseModel):
    name: str
    guidelines_raw: Optional[str] = None
    terminology_approved: List[str] = []
    terminology_banned: List[str] = []
    tone_rules: List[str] = []
    approved_facts: List[str] = []
    color_palette: List[str] = []


class BrandKitUpdate(BaseModel):
    name: Optional[str] = None
    guidelines_raw: Optional[str] = None
    terminology_approved: Optional[List[str]] = None
    terminology_banned: Optional[List[str]] = None
    tone_rules: Optional[List[str]] = None
    approved_facts: Optional[List[str]] = None
    color_palette: Optional[List[str]] = None


class BrandKitResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    guidelines_raw: Optional[str] = None
    terminology_approved: List[str] = []
    terminology_banned: List[str] = []
    tone_rules: List[str] = []
    approved_facts: List[str] = []
    color_palette: List[str] = []
    is_indexed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
