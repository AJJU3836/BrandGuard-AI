"""
BrandGuard AI — Embedded Auto-Seeder
Ensures demo workspace, team accounts, brand kit, research-grounded guidelines, and realistic drafts exist on startup.
"""
import os
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.core.security import hash_password
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

EMBEDDED_GUIDELINES = """
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

def seed_db_if_empty(db: Session):
    """Seed demo data if workspace or users don't exist yet, or enrich drafts if count < 6."""
    try:
        # 1. Workspace
        workspace = db.query(Workspace).filter(Workspace.name == "Innovex Governance").first()
        if not workspace:
            workspace = db.query(Workspace).first()
        if not workspace:
            workspace = Workspace(
                name="Innovex Governance",
                description="Official Innovex workspace for intelligent brand governance."
            )
            db.add(workspace)
            db.flush()

        # 2. Team Users
        team = [
            ("kaleajay626@gmail.com", "Ajay Kale", "admin"),
            ("mahesh@innovex.com", "Mahesh Gadekar", "manager"),
            ("asma@innovex.com", "Asma Inamdar", "reviewer"),
            ("shrushti@innovex.com", "Shrushti Kharadkar", "creator"),
        ]

        users = {}
        for email, name, role in team:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    email=email,
                    full_name=name,
                    password_hash=hash_password("password123"),
                    role=role,
                    workspace_id=workspace.id,
                )
                db.add(u)
                db.flush()
            elif not u.workspace_id:
                u.workspace_id = workspace.id
                db.flush()
            users[email] = u

        # 3. Brand Kits (Multi-Industry Governance Kits)
        initial_kits = [
            {
                "name": "Innovex Official Brand Kit",
                "guidelines": EMBEDDED_GUIDELINES,
                "approved_terms": ["BrandGuard AI", "Innovex", "Inkloom", "enterprise-grade", "explainable AI", "pre-publication governance"],
                "banned_terms": ["cheap", "miracle", "magic software", "instant fix", "#1 in India", "100% safe", "guaranteed", "unbeatable"],
                "tone_rules": ["Professional", "Empathetic", "Objective", "Clear", "No hyperbole"],
                "approved_facts": [
                    "Over 500+ enterprise clients onboarded",
                    "Founded in 2024",
                    "ASCI pre-publication guideline compliant",
                    "ISO-27001 certified architecture"
                ],
                "color_palette": ["#1E40AF", "#2563EB", "#10B981", "#F59E0B", "#E11D48"],
            },
            {
                "name": "Apex Wealth & FinTech Governance Kit",
                "guidelines": """APEX FINANCIAL TECHNOLOGIES — REGULATORY & BRAND GOVERNANCE POLICY (v3.1)
========================================================================
SEBI & RBI Compliant Advertising & Communications Guidelines

1. BRAND POSITIONING & VOICE
- Brand Identity: Apex Wealth by Apex Financial Technologies.
- Tone Principles: Prudent, disciplined, transparent, fiduciary. No speculative excitement or FOMO marketing.

2. TERMINOLOGY & DISCLAIMER MANDATES
- Approved Terms: "Apex Wealth", "SEBI-registered portfolio manager", "institutional-grade custody", "risk-adjusted returns", "asset allocation", "algorithmic rebalancing".
- Banned Terms: "guaranteed returns", "risk-free", "100% profit", "get rich", "instant payout", "double your money", "can't lose".
- Regulatory Rule: Never promise fixed percentage returns on equity or mutual fund products.

3. STATUTORY FACTS & DISCLOSURES
- Approved Facts:
  * "SEBI Registration Number: INP000007890"
  * "Over ₹2,400 Crores in Assets Under Management (AUM)"
  * "Custody backed by top-tier custodian institutions"
  * "Audited by Big 4 statutory auditors"

4. VISUAL IDENTITY & ACCESSIBILITY
- Approved Hex Palette: #0F172A (Deep Slate Navy), #0D9488 (Teal Green), #D97706 (Regulatory Gold), #64748B (Muted Slate).
- Strict Rule: High-contrast disclaimers must satisfy WCAG 2.1 AA (minimum 4.5:1 ratio against background).""",
                "approved_terms": ["Apex Wealth", "SEBI-registered", "institutional custody", "risk-adjusted returns", "algorithmic rebalancing", "fiduciary"],
                "banned_terms": ["guaranteed returns", "risk-free", "100% profit", "get rich", "instant payout", "double your money", "can't lose"],
                "tone_rules": ["Prudent", "Disciplined", "Transparent", "Fiduciary", "No FOMO"],
                "approved_facts": ["SEBI Registration Number INP000007890", "Over 2400 Crores AUM", "Custody backed by top-tier institutions", "Audited by Big 4"],
                "color_palette": ["#0F172A", "#0D9488", "#D97706", "#64748B"],
            },
            {
                "name": "Aura BioHealth & Wellness Brand Kit",
                "guidelines": """AURA BIOHEALTH & LIFE SCIENCES — CLINICAL GOVERNANCE GUIDELINES (v1.8)
======================================================================
CDSCO & Consumer Protection Advertising Code Compliance

1. BRAND IDENTITY & ETHOS
- Brand Identity: Aura BioHealth Solutions.
- Tone Principles: Empathetic, clinically accurate, modest, scientifically grounded. Never sensationalist.

2. CLINICAL TERMINOLOGY & MEDICAL CLAIMS
- Approved Terms: "Aura BioHealth", "clinically evaluated", "dermatologist tested", "evidence-backed formulation", "cellular hydration", "standardized bio-extracts".
- Banned Terms: "miracle cure", "instant weight loss", "100% cure", "reverse aging overnight", "cancer preventive", "magical healing", "permanent relief".
- Regulatory Rule: Do not make disease cure claims for nutraceutical or cosmeceutical products.

3. CERTIFIED CLAIMS & CLINICAL PRECEDENTS
- Approved Facts:
  * "Clinically evaluated across 1,200 participants in double-blind trials"
  * "Manufactured in WHO-GMP certified facilities"
  * "ISO-22000 and FSSAI approved formulation"
  * "Published research in Peer-Reviewed Phytomedicine Journals"

4. VISUAL IDENTITY & GRAPHICS
- Approved Hex Palette: #065F46 (Forest Emerald), #0284C7 (Clinical Blue), #10B981 (Organic Mint), #F3F4F6 (Clean White/Grey).
- Medical Imagery Rule: Avoid graphic medical imagery or before/after photos with deceptive lighting or digital retouching.""",
                "approved_terms": ["Aura BioHealth", "clinically evaluated", "dermatologist tested", "evidence-backed formulation", "cellular hydration", "standardized bio-extracts"],
                "banned_terms": ["miracle cure", "instant weight loss", "100% cure", "reverse aging overnight", "cancer preventive", "magical healing", "permanent relief"],
                "tone_rules": ["Empathetic", "Clinically Accurate", "Modest", "Scientifically Grounded"],
                "approved_facts": ["Clinically evaluated across 1200 participants", "WHO-GMP certified facilities", "ISO-22000 and FSSAI approved", "Published in Peer-Reviewed Journals"],
                "color_palette": ["#065F46", "#0284C7", "#10B981", "#F3F4F6"],
            }
        ]

        for kit_meta in initial_kits:
            bk = db.query(BrandKit).filter(BrandKit.workspace_id == workspace.id, BrandKit.name == kit_meta["name"]).first()
            if not bk:
                bk = BrandKit(
                    workspace_id=workspace.id,
                    name=kit_meta["name"],
                    guidelines_raw=kit_meta["guidelines"],
                    terminology_approved=kit_meta["approved_terms"],
                    terminology_banned=kit_meta["banned_terms"],
                    tone_rules=kit_meta["tone_rules"],
                    approved_facts=kit_meta["approved_facts"],
                    color_palette=kit_meta["color_palette"],
                    is_indexed=True,
                )
                db.add(bk)
                db.flush()
                index_guidelines(bk.id, kit_meta["guidelines"], db)
            else:
                bk.guidelines_raw = kit_meta["guidelines"]
                db.flush()

        # 4. Drafts & Research Scenarios
        creator_user = users.get("shrushti@innovex.com")
        reviewer_user = users.get("asma@innovex.com")
        manager_user = users.get("mahesh@innovex.com")
        admin_user = users.get("kaleajay626@gmail.com")

        if not creator_user or not reviewer_user:
            db.commit()
            return

        existing_drafts_count = db.query(Draft).filter(Draft.workspace_id == workspace.id).count()
        if existing_drafts_count >= 6:
            db.commit()
            return

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
                    workspace_id=workspace.id,
                    creator_id=item["creator"].id,
                    title=item["title"],
                    content=item["content"],
                    content_type=item["content_type"],
                    status=item["status"],
                )
                db.add(d)
                db.flush()

                # Add version history
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
                    db.add(DraftVersion(
                        draft_id=d.id,
                        version_number=len(item["history"]) + 1,
                        content=item["content"],
                        change_summary="Current working draft (Audited)",
                        created_at=datetime.now(timezone.utc)
                    ))
                else:
                    db.add(DraftVersion(
                        draft_id=d.id,
                        version_number=1,
                        content=item["content"],
                        change_summary="Initial submission",
                        created_at=datetime.now(timezone.utc)
                    ))

                # Run checks
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

                # Add comments
                for author, comment_text in item.get("comments", []):
                    comm = Comment(
                        draft_id=d.id,
                        user_id=author.id,
                        content=comment_text,
                        created_at=datetime.now(timezone.utc) - timedelta(minutes=20)
                    )
                    db.add(comm)

                # Add AuditLog
                audit = AuditLog(
                    workspace_id=workspace.id,
                    user_id=item["creator"].id,
                    action="draft_created",
                    entity_type="draft",
                    entity_id=d.id,
                    details={"title": item["title"], "findings_count": len(findings_data), "status": item["status"]},
                    ai_service_used="rule_engine"
                )
                db.add(audit)

        db.commit()
        print("🌱 Seeding complete: Research-backed guidelines, team accounts, and drafts loaded.")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Auto-seed error: {e}")
