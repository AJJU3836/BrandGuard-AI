"""Dashboard API — aggregated stats and audit log."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.draft import Draft
from app.models.finding import Finding
from app.models.user import User

router = APIRouter(prefix="/api/workspaces/{workspace_id}/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregated workspace stats for the insights dashboard."""

    # Total drafts
    total_drafts = db.query(func.count(Draft.id)).filter(
        Draft.workspace_id == workspace_id
    ).scalar()

    # Drafts by status
    drafts_by_status = dict(
        db.query(Draft.status, func.count(Draft.id))
        .filter(Draft.workspace_id == workspace_id)
        .group_by(Draft.status)
        .all()
    )

    # Get all draft IDs in this workspace
    draft_ids = [
        d.id for d in
        db.query(Draft.id).filter(Draft.workspace_id == workspace_id).all()
    ]

    # Findings by category
    findings_by_category = {}
    findings_by_severity = {}
    top_recurring = []

    if draft_ids:
        findings_by_category = dict(
            db.query(Finding.category, func.count(Finding.id))
            .filter(Finding.draft_id.in_(draft_ids))
            .group_by(Finding.category)
            .all()
        )

        findings_by_severity = dict(
            db.query(Finding.severity, func.count(Finding.id))
            .filter(Finding.draft_id.in_(draft_ids))
            .group_by(Finding.severity)
            .all()
        )

        # Top recurring issues (most common explanations)
        top_recurring = [
            {"explanation": row[0], "count": row[1]}
            for row in (
                db.query(Finding.explanation, func.count(Finding.id).label("cnt"))
                .filter(Finding.draft_id.in_(draft_ids))
                .group_by(Finding.explanation)
                .order_by(func.count(Finding.id).desc())
                .limit(10)
                .all()
            )
        ]

    return {
        "total_drafts": total_drafts,
        "drafts_by_status": drafts_by_status,
        "findings_by_category": findings_by_category,
        "findings_by_severity": findings_by_severity,
        "top_recurring_issues": top_recurring,
    }


@router.get("/audit-log")
def get_audit_log(
    workspace_id: UUID,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent audit log entries for the workspace."""
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.workspace_id == workspace_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "details": log.details,
            "ai_service_used": log.ai_service_used,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
