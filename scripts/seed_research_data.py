"""
Seed realistic, research-backed marketing drafts, guidelines, and audit trails.
Reflects Innovex's Q3 2026 Creative Compliance Survey (N = 42 Marketing Teams) and ASCI regulatory standards.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.workspace import Workspace
from app.models.brand_kit import BrandKit
from app.models.draft import Draft
from app.models.draft_version import DraftVersion
from app.models.finding import Finding
from app.models.comment import Comment
from app.models.audit_log import AuditLog
from app.services.rule_engine import run_all_checks
from app.services.brand_kit_service import index_guidelines
from datetime import datetime, timezone, timedelta

RESEARCH_GUIDELINES = """
INNOVEX ENTERPRISE BRAND GOVERNANCE POLICY (v2.4)
=================================================
Empirically formulated from Innovex's Q3 2026 Creative Compliance Survey (N = 42 Marketing Teams) & ASCI Regulatory Standards

1. BRAND IDENTITY & POSITIONING
- Brand Name: "BrandGuard AI by Innovex". (Never write "Brand Guard" as two words or lowercase "brandguard").
- Core Promise: Intelligent pre-publication brand governance powered by explainable AI.
- Voice & Tone: Confident, professional, objective, and clear. Avoid sensationalist hyperbole or colloquial slang.

2. TERMINOLOGY STANDARDS (Survey-Backed Standards)
- Approved Terms: "BrandGuard AI", "Innovex", "Inkloom", "enterprise-grade", "explainable AI", "pre-publication governance".
- Prohibited Terms: "cheap", "miracle", "magic software", "instant fix", "#1 in India", "100% safe", "guaranteed", "unbeatable".
- Empirical Justification: In our survey of 42 agency creative directors, 74% of enterprise buyers associated words like "cheap" and "magic" with scam utilities, reducing B2B contract conversion by 31%.

3. FACTUAL ACCURACY & CLAIM SUBSTANTIATION (ASCI Chapter 1 Compliance)
- Superlative claims require verified third-party empirical evidence prior to publication.
- Do not state "#1 in India" or "unbeatable" without quoting certified market share data.
- Approved Facts Registry:
  * "Over 500+ enterprise clients onboarded"
  * "Founded in 2024"
  * "ASCI pre-publication guideline compliant"
  * "ISO-27001 certified architecture"

4. VISUAL IDENTITY & ACCESSIBILITY (WCAG 2.1 AA Standards)
- Primary Palette: #1E40AF (Primary Blue), #2563EB (Accent Blue), #10B981 (Success Green), #F59E0B (Warning Amber), #E11D48 (Error Red).
- Prohibited Visual Hues: Neon pink (#FF0055), high-saturation purples, or unapproved gradients.
- Accessibility: All published visual graphics must maintain a minimum 4.5:1 WCAG 2.1 AA contrast ratio for standard text and include descriptive alt-text.
"""

def seed_research_data():
    db = SessionLocal()
    try:
        # 1. Get or create Workspace
        ws = db.query(Workspace).filter(Workspace.name == "Innovex Governance").first()
        if not ws:
            ws = db.query(Workspace).first()
        if not ws:
            ws = Workspace(
                name="Innovex Governance",
                description="Official Innovex workspace for intelligent brand governance."
            )
            db.add(ws)
            db.flush()

        # 2. Get team users
        users = {u.email: u for u in db.query(User).all()}
        admin_user = users.get("kaleajay626@gmail.com")
        manager_user = users.get("mahesh@innovex.com")
        reviewer_user = users.get("asma@innovex.com")
        creator_user = users.get("shrushti@innovex.com")

        if not creator_user or not reviewer_user:
            print("⚠️ Users missing, please run base seeder first.")
            return

        # 3. Update Brand Kit with rich guidelines
        brand_kit = db.query(BrandKit).filter(BrandKit.workspace_id == ws.id).first()
        approved_terms = ["BrandGuard AI", "Innovex", "Inkloom", "enterprise-grade", "explainable AI", "pre-publication governance"]
        banned_terms = ["cheap", "miracle", "magic software", "instant fix", "#1 in India", "100% safe", "guaranteed", "unbeatable"]
        tone_rules = ["Professional", "Empathetic", "Objective", "Clear", "No hyperbole"]
        approved_facts = [
            "Over 500+ enterprise clients onboarded",
            "Founded in 2024",
            "ASCI pre-publication guideline compliant",
            "ISO-27001 certified architecture"
        ]
        color_palette = ["#1E40AF", "#2563EB", "#10B981", "#F59E0B", "#E11D48"]

        if brand_kit:
            brand_kit.guidelines_raw = RESEARCH_GUIDELINES
            brand_kit.terminology_approved = approved_terms
            brand_kit.terminology_banned = banned_terms
            brand_kit.tone_rules = tone_rules
            brand_kit.approved_facts = approved_facts
            brand_kit.color_palette = color_palette
            db.flush()
            index_guidelines(brand_kit.id, RESEARCH_GUIDELINES, db)

        # 4. Rich, Research-Backed Draft Portfolio
        research_drafts = [
            {
                "title": "Q4 Global Product Launch — Social Announcement",
                "content": (
                    "Introducing Brand Guard. We are recognized as the #1 in India brand protection solution. "
                    "Our software is 100% safe, completely guaranteed, and unbeatable across the sector. "
                    "Don't waste money on overpriced legacy alternatives when you can get cheap software right here. "
                    "Brand accent styled in #FF0055."
                ),
                "content_type": "social_post",
                "status": "in_review",
                "creator": creator_user,
                "history": [
                    ("v1 (Initial submission from creative agency)", "Introducing Brand Guard! We are #1 in India cheap software with 100% safe magic."),
                ],
                "comments": [
                    (reviewer_user, "As per our ASCI Chapter 1 compliance audit, the claim '#1 in India' cannot be published without third-party market research citations. Please accept the approved rewrite to reference our 500+ verified enterprise client milestone instead."),
                    (creator_user, "Understood. Applying the suggested terminology fix and updating the color hex to #1E40AF.")
                ]
            },
            {
                "title": "Enterprise Customer Onboarding & Welcome Series",
                "content": (
                    "Welcome to BrandGuard AI by Innovex. Founded in 2024, our enterprise-grade platform "
                    "empowers marketing teams with explainable AI findings and pre-publication governance. "
                    "Over 500+ enterprise clients onboarded trust our ISO-27001 certified architecture. "
                    "Primary palette: #1E40AF."
                ),
                "content_type": "email",
                "status": "approved",
                "creator": creator_user,
                "comments": [
                    (manager_user, "Approved by compliance. All claims match our verified corporate fact registry and adhere to WCAG 2.1 contrast rules.")
                ]
            },
            {
                "title": "Q3 Performance Marketing Ad Copy (Search & Social)",
                "content": (
                    "This festive season, get the cheapest brand safety solution in the market! "
                    "BrandGuard AI is guaranteed to deliver results or your money back. "
                    "Don't miss this miracle software deal. Contact us for an instant fix!"
                ),
                "content_type": "social_post",
                "status": "changes_requested",
                "creator": creator_user,
                "comments": [
                    (reviewer_user, "Our Q3 creative survey found that hyperbolic promises ('miracle software', 'instant fix') erode enterprise buyer trust by 74%. Rephrasing required to maintain our objective, authoritative tone standard.")
                ]
            },
            {
                "title": "Industry Survey Report: AI Governance & Advertising Standards",
                "content": (
                    "At Innovex, we believe explainable AI is the future of brand governance. "
                    "In our recent survey of 42 marketing teams, 83% of content creators reported that manual compliance reviews take over 4 business days. "
                    "BrandGuard AI resolves this with pre-publication verification, keeping enterprises ASCI compliant."
                ),
                "content_type": "blog_post",
                "status": "approved",
                "creator": creator_user,
                "comments": [
                    (admin_user, "Published on official company blog. Excellent incorporation of our primary survey findings.")
                ]
            },
            {
                "title": "Agency Partner Campaign — Festive Promotional Copy",
                "content": (
                    "Looking for unbeatable marketing compliance? BrandGuard AI gives you 100% safe protection with instant setup. "
                    "Brand accent styled in #FF0055."
                ),
                "content_type": "social_post",
                "status": "in_review",
                "creator": creator_user,
                "comments": [
                    (creator_user, "External agency draft received. Flagged non-brand hex #FF0055 and superlative claim 'unbeatable' before client sign-off.")
                ]
            },
            {
                "title": "Investor & Media Briefing — Q3 Operational Milestones",
                "content": (
                    "Innovex today released its Q3 governance report, noting that over 500+ enterprise clients onboarded "
                    "have automated pre-publication compliance. BrandGuard AI continues to maintain ISO-27001 certified architecture "
                    "while delivering explainable AI oversight across all digital creative channels."
                ),
                "content_type": "press_release",
                "status": "approved",
                "creator": creator_user,
                "comments": [
                    (manager_user, "Executive sign-off complete. All operational metrics cross-verified against corporate audited filings.")
                ]
            }
        ]

        for item in research_drafts:
            d = db.query(Draft).filter(Draft.title == item["title"]).first()
            if not d:
                d = Draft(
                    workspace_id=ws.id,
                    creator_id=item["creator"].id,
                    title=item["title"],
                    content=item["content"],
                    content_type=item["content_type"],
                    status=item["status"],
                )
                db.add(d)
                db.flush()

                # Add version history if specified
                if "history" in item:
                    for v_num, (v_summary, v_content) in enumerate(item["history"], 1):
                        dv = DraftVersion(
                            draft_id=d.id,
                            version_number=v_num,
                            content=v_content,
                            change_summary=v_summary,
                            created_at=datetime.now(timezone.utc) - timedelta(hours=2)
                        )
                        db.add(dv)
                    # Add current version
                    db.add(DraftVersion(
                        draft_id=d.id,
                        version_number=len(item["history"]) + 1,
                        content=item["content"],
                        change_summary="Current working draft (Audited)",
                        created_at=datetime.now(timezone.utc)
                    ))
                else:
                    # Single baseline version
                    db.add(DraftVersion(
                        draft_id=d.id,
                        version_number=1,
                        content=item["content"],
                        change_summary="Initial submission",
                        created_at=datetime.now(timezone.utc)
                    ))

                # Run checks and generate findings
                findings_data = run_all_checks(
                    content=item["content"],
                    banned_terms=banned_terms,
                    approved_terms=approved_terms,
                    approved_facts=approved_facts,
                    color_palette=color_palette,
                )

                for fd in findings_data:
                    finding = Finding(
                        draft_id=d.id,
                        severity=fd["severity"],
                        category=fd["category"],
                        text_highlight=fd.get("text_highlight"),
                        explanation=fd["explanation"],
                        guideline_source=fd.get("guideline_source"),
                        suggestion=fd.get("suggestion"),
                        is_ai_generated=fd.get("is_ai_generated", False),
                        confidence=fd.get("confidence", 1.0),
                    )
                    db.add(finding)

                # Add reviewer & creator comments
                for author, comment_text in item.get("comments", []):
                    comm = Comment(
                        draft_id=d.id,
                        user_id=author.id,
                        content=comment_text,
                        created_at=datetime.now(timezone.utc) - timedelta(minutes=15)
                    )
                    db.add(comm)

                # Add AuditLog
                audit = AuditLog(
                    workspace_id=ws.id,
                    user_id=item["creator"].id,
                    action="draft_created",
                    entity_type="draft",
                    entity_id=d.id,
                    details={"title": item["title"], "findings_count": len(findings_data), "status": item["status"]},
                    ai_service_used="rule_engine"
                )
                db.add(audit)

        db.commit()
        print(f"✅ Successfully seeded research-backed drafts and guidelines into workspace '{ws.name}'!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding research data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_research_data()
