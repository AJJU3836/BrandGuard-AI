"""Drafts API — create, list, update status, and comment on drafts."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.comment import Comment
from app.models.draft import Draft
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.draft import DraftCreate, DraftResponse, DraftStatusUpdate

router = APIRouter(prefix="/api/workspaces/{workspace_id}/drafts", tags=["Drafts"])

VALID_STATUSES = {"draft", "in_review", "changes_requested", "approved"}


@router.post("/", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
def create_draft(
    workspace_id: UUID,
    payload: DraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new content draft for review."""
    draft = Draft(
        workspace_id=workspace_id,
        creator_id=current_user.id,
        title=payload.title,
        content=payload.content,
        content_type=payload.content_type,
    )
    db.add(draft)
    db.flush()

    # Audit log
    log = AuditLog(
        workspace_id=workspace_id,
        user_id=current_user.id,
        action="draft_created",
        entity_type="draft",
        entity_id=draft.id,
        details={"title": payload.title, "content_type": payload.content_type},
    )
    db.add(log)
    db.commit()
    db.refresh(draft)

    return draft


@router.get("/", response_model=List[DraftResponse])
def list_drafts(
    workspace_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List drafts in a workspace, optionally filtered by status."""
    query = db.query(Draft).filter(Draft.workspace_id == workspace_id)
    if status_filter:
        query = query.filter(Draft.status == status_filter)
    return query.order_by(Draft.updated_at.desc()).all()


@router.get("/{draft_id}", response_model=DraftResponse)
def get_draft(
    workspace_id: UUID,
    draft_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific draft."""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.workspace_id == workspace_id,
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")
    return draft


@router.put("/{draft_id}/status", response_model=DraftResponse)
def update_draft_status(
    workspace_id: UUID,
    draft_id: UUID,
    payload: DraftStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a draft's status (approval workflow)."""
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {VALID_STATUSES}")

    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.workspace_id == workspace_id,
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")

    # Only manager/reviewer/admin can approve or request changes
    if payload.status in ("approved", "changes_requested"):
        if current_user.role not in ("manager", "reviewer", "admin"):
            raise HTTPException(
                status_code=403,
                detail="Only managers, reviewers, or admins can approve or request changes.",
            )
        draft.reviewer_id = current_user.id

    old_status = draft.status
    draft.status = payload.status

    # Audit log
    log = AuditLog(
        workspace_id=workspace_id,
        user_id=current_user.id,
        action="draft_status_changed",
        entity_type="draft",
        entity_id=draft.id,
        details={"old_status": old_status, "new_status": payload.status},
    )
    db.add(log)
    db.commit()
    db.refresh(draft)

    return draft


@router.post("/{draft_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    workspace_id: UUID,
    draft_id: UUID,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a draft."""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.workspace_id == workspace_id,
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")

    comment = Comment(
        draft_id=draft_id,
        user_id=current_user.id,
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.get("/{draft_id}/comments", response_model=List[CommentResponse])
def list_comments(
    workspace_id: UUID,
    draft_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all comments on a draft."""
    return (
        db.query(Comment)
        .filter(Comment.draft_id == draft_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
