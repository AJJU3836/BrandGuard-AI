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
    """Return aggregated workspace stats and root-cause guideline intelligence."""

    # Total drafts
    total_drafts = db.query(func.count(Draft.id)).filter(
        Draft.workspace_id == workspace_id
    ).scalar() or 0

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

    findings_by_category = {}
    findings_by_severity = {}
    findings_by_status = {}
    top_recurring = []
    guideline_gaps = []
    content_type_matrix = []
    engine_breakdown = {"ai_count": 0, "rule_count": 0}
    health_score = 100
    acceptance_rate = 100.0
    open_issues_count = 0
    resolved_issues_count = 0

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

        findings_by_status = dict(
            db.query(Finding.status, func.count(Finding.id))
            .filter(Finding.draft_id.in_(draft_ids))
            .group_by(Finding.status)
            .all()
        )

        open_issues_count = findings_by_status.get("open", 0)
        accepted_count = findings_by_status.get("accepted", 0)
        rejected_count = findings_by_status.get("rejected", 0)
        resolved_issues_count = accepted_count + rejected_count

        if resolved_issues_count > 0:
            acceptance_rate = round((accepted_count / resolved_issues_count) * 100, 1)

        # AI vs Deterministic Engine Breakdown
        ai_cnt = (
            db.query(func.count(Finding.id))
            .filter(Finding.draft_id.in_(draft_ids), Finding.is_ai_generated == True)
            .scalar() or 0
        )
        rule_cnt = (
            db.query(func.count(Finding.id))
            .filter(Finding.draft_id.in_(draft_ids), Finding.is_ai_generated == False)
            .scalar() or 0
        )
        engine_breakdown = {"ai_count": ai_cnt, "rule_count": rule_cnt}

        # Compliance Health Score (0-100)
        open_errors = (
            db.query(func.count(Finding.id))
            .filter(Finding.draft_id.in_(draft_ids), Finding.severity == "error", Finding.status == "open")
            .scalar() or 0
        )
        open_warnings = (
            db.query(func.count(Finding.id))
            .filter(Finding.draft_id.in_(draft_ids), Finding.severity == "warning", Finding.status == "open")
            .scalar() or 0
        )
        deduction = (open_errors * 12) + (open_warnings * 4)
        health_score = max(25, min(100, 100 - deduction))

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

        # Content-Type Risk Breakdown
        drafts_by_type = (
            db.query(Draft.content_type, func.count(Draft.id))
            .filter(Draft.workspace_id == workspace_id)
            .group_by(Draft.content_type)
            .all()
        )
        for c_type, d_count in drafts_by_type:
            c_draft_ids = [
                d.id for d in db.query(Draft.id)
                .filter(Draft.workspace_id == workspace_id, Draft.content_type == c_type)
                .all()
            ]
            f_count = (
                db.query(func.count(Finding.id))
                .filter(Finding.draft_id.in_(c_draft_ids))
                .scalar() or 0
            ) if c_draft_ids else 0
            top_cat = (
                db.query(Finding.category)
                .filter(Finding.draft_id.in_(c_draft_ids))
                .group_by(Finding.category)
                .order_by(func.count(Finding.id).desc())
                .first()
            )
            content_type_matrix.append({
                "content_type": c_type,
                "drafts_count": d_count,
                "findings_count": f_count,
                "density": round(f_count / max(1, d_count), 1),
                "primary_risk": top_cat[0] if top_cat else "None"
            })

        # Guideline-Gap Intelligence & Root-Cause Diagnosis
        gap_rows = (
            db.query(
                Finding.guideline_source,
                Finding.category,
                func.count(Finding.id).label("cnt"),
                func.min(Finding.explanation).label("sample_exp"),
                func.min(Finding.text_highlight).label("sample_hl")
            )
            .filter(Finding.draft_id.in_(draft_ids))
            .group_by(Finding.guideline_source, Finding.category)
            .order_by(func.count(Finding.id).desc())
            .limit(6)
            .all()
        )
        for g_source, cat, count, sample_exp, sample_hl in gap_rows:
            if cat == "terminology":
                root_cause = "Creators repeatedly use non-approved vocabulary due to lack of prominent in-context synonyms."
                rec = f"Add approved alternatives for '{sample_hl or 'flagged terms'}' to the Brand Kit."
                action_type = "terminology"
            elif cat == "claim":
                root_cause = "Marketing copy frequently introduces superlatives or statistics without referencing the verified fact sheet."
                rec = "Expand Approved Facts repository with verified performance benchmarks."
                action_type = "facts"
            elif cat == "tone":
                root_cause = "Draft voice drifts towards aggressive sales rhetoric or passive phrasing, deviating from authoritative brand voice."
                rec = "Provide explicit 'Say This, Not That' examples in Tone & Voice rules."
                action_type = "tone"
            elif cat == "accessibility":
                root_cause = "Visual assets regularly lack WCAG 2.1 AA descriptive alt-text or fail minimum 4.5:1 color contrast standards."
                rec = "Incorporate mandatory contrast checking and alt-text templates into creative asset pipelines."
                action_type = "visual"
            else:
                root_cause = "Inconsistencies detected against core enterprise guidelines."
                rec = "Clarify guideline rules to eliminate creator ambiguity."
                action_type = "general"

            guideline_gaps.append({
                "guideline_source": g_source or f"{cat.capitalize()} Standards",
                "category": cat,
                "violation_count": count,
                "sample_highlight": sample_hl,
                "sample_explanation": sample_exp,
                "root_cause": root_cause,
                "ai_recommendation": rec,
                "action_type": action_type,
                "friction_severity": "High" if count >= 3 else "Medium"
            })

    return {
        "total_drafts": total_drafts,
        "drafts_by_status": drafts_by_status,
        "findings_by_category": findings_by_category,
        "findings_by_severity": findings_by_severity,
        "findings_by_status": findings_by_status,
        "top_recurring_issues": top_recurring,
        "health_score": health_score,
        "acceptance_rate": acceptance_rate,
        "open_issues_count": open_issues_count,
        "resolved_issues_count": resolved_issues_count,
        "engine_breakdown": engine_breakdown,
        "content_type_matrix": content_type_matrix,
        "guideline_gaps": guideline_gaps,
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
