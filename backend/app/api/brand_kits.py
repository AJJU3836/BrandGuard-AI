"""Brand Kits API — CRUD and indexing for brand guidelines."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.brand_kit import BrandKit
from app.models.user import User
from app.schemas.brand_kit import BrandKitCreate, BrandKitResponse, BrandKitUpdate
from app.services.brand_kit_service import index_guidelines

router = APIRouter(prefix="/api/workspaces/{workspace_id}/brand-kits", tags=["Brand Kits"])


@router.post("/", response_model=BrandKitResponse, status_code=status.HTTP_201_CREATED)
def create_brand_kit(
    workspace_id: UUID,
    payload: BrandKitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new brand kit for a workspace."""
    if current_user.role not in ("manager", "admin"):
        raise HTTPException(status_code=403, detail="Only managers and admins can create brand kits.")

    brand_kit = BrandKit(
        workspace_id=workspace_id,
        name=payload.name,
        guidelines_raw=payload.guidelines_raw,
        terminology_approved=payload.terminology_approved,
        terminology_banned=payload.terminology_banned,
        tone_rules=payload.tone_rules,
        approved_facts=payload.approved_facts,
        color_palette=payload.color_palette,
    )
    db.add(brand_kit)
    db.commit()
    db.refresh(brand_kit)

    return brand_kit


@router.get("/", response_model=List[BrandKitResponse])
def list_brand_kits(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all brand kits in a workspace."""
    return db.query(BrandKit).filter(BrandKit.workspace_id == workspace_id).all()


@router.get("/{kit_id}", response_model=BrandKitResponse)
def get_brand_kit(
    workspace_id: UUID,
    kit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific brand kit."""
    kit = db.query(BrandKit).filter(
        BrandKit.id == kit_id,
        BrandKit.workspace_id == workspace_id,
    ).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Brand kit not found.")
    return kit


@router.put("/{kit_id}", response_model=BrandKitResponse)
def update_brand_kit(
    workspace_id: UUID,
    kit_id: UUID,
    payload: BrandKitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a brand kit (partial update)."""
    if current_user.role not in ("manager", "admin"):
        raise HTTPException(status_code=403, detail="Only managers and admins can update brand kits.")

    kit = db.query(BrandKit).filter(
        BrandKit.id == kit_id,
        BrandKit.workspace_id == workspace_id,
    ).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Brand kit not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kit, key, value)

    db.commit()
    db.refresh(kit)
    return kit


@router.post("/{kit_id}/index")
def index_brand_kit(
    workspace_id: UUID,
    kit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger guideline indexing — splits text into chunks for retrieval."""
    kit = db.query(BrandKit).filter(
        BrandKit.id == kit_id,
        BrandKit.workspace_id == workspace_id,
    ).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Brand kit not found.")

    if not kit.guidelines_raw:
        raise HTTPException(status_code=400, detail="No guidelines text to index. Upload guidelines first.")

    num_chunks = index_guidelines(kit.id, kit.guidelines_raw, db)

    return {
        "message": f"Guidelines indexed successfully. Created {num_chunks} chunks.",
        "chunks_created": num_chunks,
    }
