"""Review API — trigger review, list findings, accept/reject findings."""

import csv
import io
import re
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.brand_kit import BrandKit
from app.models.draft import Draft
from app.models.draft_version import DraftVersion
from app.models.finding import Finding
from app.models.user import User
from app.schemas.finding import (
    FindingResponse,
    FindingStatusUpdate,
    ApplySuggestionRequest,
    ApplySuggestionResponse,
)
from app.services.ai_engine import ai_review, ai_image_review
from app.services.brand_kit_service import get_guideline_chunks, retrieve_relevant_chunks
from app.services.rule_engine import run_all_checks
from app.core.config import get_settings

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

    # --- 2. AI Engine (RAG retrieval & LLM/Semantic checks) ---
    relevant_chunks = retrieve_relevant_chunks(
        query=draft.content,
        brand_kit_id=brand_kit.id,
        db=db,
        top_k=6,
    )
    # If no indexed chunks returned by retriever, fallback to raw guideline chunks
    chunks_for_ai = relevant_chunks if relevant_chunks else get_guideline_chunks(brand_kit.id, db)

    ai_findings = await ai_review(
        content=draft.content,
        guideline_chunks=chunks_for_ai,
        tone_rules=brand_kit.tone_rules or [],
        approved_facts=brand_kit.approved_facts or [],
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

    # Identify AI service used
    settings = get_settings()
    if settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY:
        ai_provider = "gemini-flash"
    elif settings.OPENAI_API_KEY:
        ai_provider = "openai-gpt4o"
    else:
        ai_provider = "brandguard_semantic_engine"

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
        ai_service_used=f"rule_engine + {ai_provider}",
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


def extract_clean_replacement(suggestion: str, text_highlight: Optional[str] = None) -> str:
    """Extract clean replacement text from a suggestion string."""
    if not suggestion:
        return ""
    s = suggestion.strip()

    # Pattern 1: Replace "X" with "Y" / Replace 'X' with 'Y'
    m1 = re.search(r'replace\s+[\'"][^\'"]*[\'"]\s+with\s+[\'"]([^\'"]+)[\'"]', s, re.IGNORECASE)
    if m1:
        return m1.group(1).strip()

    # Pattern 2: Replace with "Y"
    m2 = re.search(r'replace\s+(?:.*?\s+)?with\s+[\'"]([^\'"]+)[\'"]', s, re.IGNORECASE)
    if m2:
        return m2.group(1).strip()

    # Pattern 3: Use "Y" instead / Consider using "Y"
    m3 = re.search(r'(?:use|consider\s+using)\s+[\'"]([^\'"]+)[\'"]', s, re.IGNORECASE)
    if m3:
        return m3.group(1).strip()

    # Pattern 4: Change to "Y" / Switch to "Y"
    m4 = re.search(r'(?:change\s+to|switch\s+to)\s+[\'"]([^\'"]+)[\'"]', s, re.IGNORECASE)
    if m4:
        return m4.group(1).strip()

    # Pattern 5: Entire string wrapped in quotes
    m5 = re.match(r'^[\'"]([^\'"]+)[\'"]$', s)
    if m5:
        return m5.group(1).strip()

    # Pattern 6: Multiple quotes: check if text_highlight is in quote 0, and quote 1 has replacement
    quotes = re.findall(r'[\'"]([^\'"]+)[\'"]', s)
    if quotes:
        if len(quotes) > 1 and text_highlight and text_highlight.lower() in quotes[0].lower():
            return quotes[1].strip()
        if text_highlight and quotes[0].strip().lower() != text_highlight.strip().lower():
            return quotes[0].strip()

    # Pattern 7: If suggestion starts with instructional words like remove or delete
    if s.lower().startswith(("remove", "avoid", "delete", "omit", "do not")):
        return ""

    # Fallback: remove trailing period
    return s.rstrip(".")


@router.post("/findings/{finding_id}/apply", response_model=ApplySuggestionResponse)
def apply_finding_suggestion(
    workspace_id: UUID,
    draft_id: UUID,
    finding_id: UUID,
    payload: Optional[ApplySuggestionRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    1-Click Suggestion Application:
    Applies the suggested fix or custom replacement to the draft content,
    creates a new version in DraftVersion with a clear audit change summary,
    marks the finding as accepted, logs the audit trail, and returns the updated state.
    """
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.workspace_id == workspace_id,
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")

    finding = db.query(Finding).filter(
        Finding.id == finding_id,
        Finding.draft_id == draft_id,
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")

    replacement = ""
    if payload and payload.custom_replacement is not None:
        replacement = payload.custom_replacement
    else:
        replacement = extract_clean_replacement(finding.suggestion or "", finding.text_highlight)

    # Apply replacement into draft content if text_highlight exists
    if finding.text_highlight:
        if finding.text_highlight in draft.content:
            draft.content = draft.content.replace(finding.text_highlight, replacement, 1)
        else:
            # Case-insensitive replace fallback
            pattern = re.compile(re.escape(finding.text_highlight), re.IGNORECASE)
            draft.content = pattern.sub(replacement, draft.content, count=1)

    # Determine next version number
    max_ver = (
        db.query(DraftVersion.version_number)
        .filter(DraftVersion.draft_id == draft_id)
        .order_by(DraftVersion.version_number.desc())
        .first()
    )
    next_ver = (max_ver[0] + 1) if max_ver else 1

    summary_desc = (
        f"Applied {finding.category} fix: '{finding.text_highlight}' → '{replacement}'"
        if finding.text_highlight
        else f"Applied fix for {finding.category}: '{replacement}'"
    )

    new_version = DraftVersion(
        draft_id=draft_id,
        version_number=next_ver,
        content=draft.content,
        change_summary=summary_desc,
    )
    db.add(new_version)

    # Mark finding as accepted
    finding.status = "accepted"

    # Audit log
    log = AuditLog(
        workspace_id=workspace_id,
        user_id=current_user.id,
        action="finding_applied_to_draft",
        entity_type="draft",
        entity_id=draft_id,
        details={
            "finding_id": str(finding.id),
            "category": finding.category,
            "text_highlight": finding.text_highlight,
            "applied_replacement": replacement,
            "version_number": next_ver,
        },
    )
    db.add(log)
    db.commit()
    db.refresh(draft)
    db.refresh(finding)

    return ApplySuggestionResponse(
        finding=finding,
        applied_replacement=replacement,
        version_number=next_ver,
        draft_id=draft.id,
        updated_content=draft.content,
    )


# ── Image Review & Visual Compliance ────────────────────────────────────


@router.post("/image", response_model=List[FindingResponse], status_code=status.HTTP_201_CREATED)
async def review_image(
    workspace_id: UUID,
    draft_id: UUID,
    file: Optional[UploadFile] = File(None),
    image_name: Optional[str] = Form(None),
    alt_text: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run visual and accessibility compliance checks on an image asset.
    Stores visual & accessibility findings alongside text findings.
    """
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.workspace_id == workspace_id,
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")

    brand_kit = db.query(BrandKit).filter(BrandKit.workspace_id == workspace_id).first()
    brand_palette = brand_kit.color_palette if brand_kit else []
    brand_name = brand_kit.name if brand_kit else "BrandGuard AI"
    visual_rules = brand_kit.tone_rules if brand_kit else None

    target_name = (file.filename if file and file.filename else None) or image_name or "Uploaded-Asset.png"

    # Extract image binary data and mime-type if uploaded
    image_bytes = None
    mime_type = "image/png"
    if file:
        image_bytes = await file.read()
        mime_type = file.content_type or "image/png"

    # Execute Multimodal Gemini Vision + WCAG Accessibility Review
    visual_findings_raw = await ai_image_review(
        image_url_or_name=target_name,
        image_bytes=image_bytes,
        mime_type=mime_type,
        brand_palette=brand_palette,
        alt_text=alt_text,
        visual_rules=visual_rules,
        brand_name=brand_name,
    )

    stored = []
    for f_dict in visual_findings_raw:
        finding = Finding(
            draft_id=draft_id,
            severity=f_dict["severity"],
            category=f_dict["category"],
            text_highlight=f_dict.get("text_highlight"),
            explanation=f_dict["explanation"],
            guideline_source=f_dict.get("guideline_source"),
            suggestion=f_dict.get("suggestion"),
            is_ai_generated=f_dict.get("is_ai_generated", True),
            confidence=f_dict.get("confidence", 0.9),
        )
        db.add(finding)
        stored.append(finding)

    # Audit log
    log = AuditLog(
        workspace_id=workspace_id,
        user_id=current_user.id,
        action="image_review_executed",
        entity_type="draft",
        entity_id=draft_id,
        details={
            "asset_name": target_name,
            "file_size_bytes": len(image_bytes) if image_bytes else 0,
            "mime_type": mime_type,
            "alt_text_provided": bool(alt_text),
            "findings_count": len(stored),
        },
        ai_service_used="gemini_vision_multimodal_accessibility_engine",
    )
    db.add(log)
    db.commit()

    for item in stored:
        db.refresh(item)

    return stored


# ── Findings Report & Audit Export ──────────────────────────────────────


@router.get("/export")
def export_findings(
    workspace_id: UUID,
    draft_id: UUID,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export draft findings as downloadable CSV or structured JSON report.
    """
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.workspace_id == workspace_id,
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")

    findings = (
        db.query(Finding)
        .filter(Finding.draft_id == draft_id)
        .order_by(Finding.severity.desc())
        .all()
    )

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Finding ID",
            "Severity",
            "Category",
            "Status",
            "Source Engine",
            "Flagged Text",
            "Explanation",
            "Guideline Source",
            "Suggested Fix",
            "Created At",
        ])
        for f in findings:
            writer.writerow([
                str(f.id),
                f.severity,
                f.category,
                f.status,
                "AI Review Engine" if f.is_ai_generated else "Rule Engine",
                f.text_highlight or "",
                f.explanation or "",
                f.guideline_source or "",
                f.suggestion or "",
                f.created_at.isoformat() if f.created_at else "",
            ])
        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="brandguard_report_{draft_id}.csv"'
            },
        )

    # Default to JSON format
    return {
        "draft_id": str(draft.id),
        "title": draft.title,
        "content_type": draft.content_type,
        "status": draft.status,
        "total_findings": len(findings),
        "summary": {
            "error": len([f for f in findings if f.severity == "error"]),
            "warning": len([f for f in findings if f.severity == "warning"]),
            "info": len([f for f in findings if f.severity == "info"]),
            "ai_generated": len([f for f in findings if f.is_ai_generated]),
            "rule_based": len([f for f in findings if not f.is_ai_generated]),
        },
        "findings": [
            {
                "id": str(f.id),
                "severity": f.severity,
                "category": f.category,
                "status": f.status,
                "source_engine": "AI Review Engine" if f.is_ai_generated else "Rule Engine",
                "text_highlight": f.text_highlight,
                "explanation": f.explanation,
                "guideline_source": f.guideline_source,
                "suggestion": f.suggestion,
                "confidence": f.confidence,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in findings
        ],
    }
