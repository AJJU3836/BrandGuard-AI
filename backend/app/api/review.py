"""Review API — trigger review, list findings, accept/reject findings."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.brand_kit import BrandKit
from app.models.draft import Draft
from app.models.finding import Finding
from app.models.user import User
from app.schemas.finding import FindingResponse, FindingStatusUpdate
from app.services.ai_engine import ai_review
from app.services.brand_kit_service import get_guideline_chunks
from app.services.rule_engine import run_all_checks

router = APIRouter(
    prefix="/api/workspaces/{workspace_id}/drafts/{draft_id}/review",
    tags=["Review"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def trigger_review(
    workspace_id: UUID,
    draft_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger a brand review on a draft.

    Runs the rule engine (deterministic checks) and AI engine (LLM-based checks),
    then stores all findings.
    """
    # Get the draft
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.workspace_id == workspace_id,
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")

    # Get the brand kit for this workspace
    brand_kit = db.query(BrandKit).filter(
        BrandKit.workspace_id == workspace_id
    ).first()
    if not brand_kit:
        raise HTTPException(
            status_code=400,
            detail="No brand kit found for this workspace. Create a brand kit first.",
        )

    # Clear existing findings for this draft (re-review)
    db.query(Finding).filter(Finding.draft_id == draft_id).delete()

    # --- 1. Rule Engine (deterministic checks) ---
    rule_findings = run_all_checks(
        content=draft.content,
        banned_terms=brand_kit.terminology_banned or [],
        approved_terms=brand_kit.terminology_approved or [],
        approved_facts=brand_kit.approved_facts or [],
        color_palette=brand_kit.color_palette or [],
    )

    # --- 2. AI Engine (LLM-based checks) ---
    guideline_chunks = get_guideline_chunks(brand_kit.id, db)
    ai_findings = await ai_review(
        content=draft.content,
        guideline_chunks=guideline_chunks,
        tone_rules=brand_kit.tone_rules or [],
        content_type=draft.content_type,
    )

    # --- 3. Store all findings ---
    all_finding_dicts = rule_findings + ai_findings
    stored_findings = []

    for f_dict in all_finding_dicts:
        finding = Finding(
            draft_id=draft_id,
            severity=f_dict["severity"],
            category=f_dict["category"],
            text_highlight=f_dict.get("text_highlight"),
            explanation=f_dict["explanation"],
            guideline_source=f_dict.get("guideline_source"),
            suggestion=f_dict.get("suggestion"),
            is_ai_generated=f_dict.get("is_ai_generated", False),
            confidence=f_dict.get("confidence"),
        )
        db.add(finding)
        stored_findings.append(finding)

    # Update draft status to in_review
    draft.status = "in_review"

    # Audit log
    log = AuditLog(
        workspace_id=workspace_id,
        user_id=current_user.id,
        action="review_triggered",
        entity_type="draft",
        entity_id=draft_id,
        details={
            "rule_findings": len(rule_findings),
            "ai_findings": len(ai_findings),
            "total_findings": len(all_finding_dicts),
        },
        ai_service_used="rule_engine" + (", openai_stub" if ai_findings else ""),
    )
    db.add(log)
    db.commit()

    return {
        "message": "Review completed.",
        "total_findings": len(all_finding_dicts),
        "rule_engine_findings": len(rule_findings),
        "ai_findings": len(ai_findings),
    }


@router.get("/findings", response_model=List[FindingResponse])
def list_findings(
    workspace_id: UUID,
    draft_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all findings for a draft."""
    return (
        db.query(Finding)
        .filter(Finding.draft_id == draft_id)
        .order_by(Finding.severity.desc(), Finding.created_at.asc())
        .all()
    )


@router.put("/findings/{finding_id}", response_model=FindingResponse)
def update_finding_status(
    workspace_id: UUID,
    draft_id: UUID,
    finding_id: UUID,
    payload: FindingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept or reject a finding."""
    if payload.status not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be 'accepted' or 'rejected'.")

    finding = db.query(Finding).filter(
        Finding.id == finding_id,
        Finding.draft_id == draft_id,
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")

    finding.status = payload.status

    # Audit log
    log = AuditLog(
        workspace_id=workspace_id,
        user_id=current_user.id,
        action=f"finding_{payload.status}",
        entity_type="finding",
        entity_id=finding_id,
        details={"draft_id": str(draft_id), "category": finding.category},
    )
    db.add(log)
    db.commit()
    db.refresh(finding)

    return finding
