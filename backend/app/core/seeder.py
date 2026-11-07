"""
BrandGuard AI — Embedded Auto-Seeder
Ensures demo workspace, team accounts, brand kit, and drafts exist on startup.
"""
import os
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.models.workspace import Workspace
from app.models.brand_kit import BrandKit
from app.models.draft import Draft
from app.models.finding import Finding
from app.models.comment import Comment
from app.models.audit_log import AuditLog
from app.services.rule_engine import run_all_checks
from app.services.brand_kit_service import index_guidelines

EMBEDDED_GUIDELINES = """
INNOVEX BRAND GOVERNANCE GUIDELINES (v2.4)
=========================================

1. BRAND IDENTITY & POSITIONING
- Brand Name: BrandGuard AI by Innovex.
- Core Promise: Intelligent pre-publication brand governance powered by explainable AI.
- Voice & Tone: Confident, professional, objective, clear. Never hyperbolic.

2. TERMINOLOGY STANDARDS
- Approved terms: "BrandGuard AI", "Innovex", "Inkloom", "enterprise-grade", "explainable AI".
- Prohibited terms: "cheap", "miracle", "magic software", "instant fix", "#1 in India", "100% safe", "guaranteed".

3. FACTUAL ACCURACY & CLAIM SUBSTANTIATION (ASCI COMPLIANCE)
- Superlative claims require verified third-party evidence.
- Approved Facts:
  * "Over 500+ enterprise clients onboarded"
  * "Founded in 2024"
  * "ASCI pre-publication guideline compliant"
  * "ISO-27001 certified architecture"

4. VISUAL IDENTITY
- Primary Palette: #1E40AF (Primary Blue), #2563EB (Accent Blue), #10B981 (Success Green), #F59E0B (Warning Amber), #E11D48 (Error Red).
"""

def seed_db_if_empty(db: Session):
    """Seed demo data if workspace or users don't exist yet."""
    try:
        existing_user = db.query(User).filter(User.email == "kaleajay626@gmail.com").first()
        if existing_user:
            return

        # 1. Workspace
        workspace = db.query(Workspace).filter(Workspace.name == "Innovex Governance").first()
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
            users[email] = u

        # 3. Brand Kit
        approved_terms = ["BrandGuard AI", "Innovex", "Inkloom", "enterprise-grade", "explainable AI"]
        banned_terms = ["cheap", "miracle", "magic software", "instant fix", "#1 in India", "100% safe", "guaranteed"]
        tone_rules = ["Professional", "Empathetic", "Objective", "Clear", "No hyperbole"]
        approved_facts = [
            "Over 500+ enterprise clients onboarded",
            "Founded in 2024",
            "ASCI pre-publication guideline compliant",
            "ISO-27001 certified architecture"
        ]
        color_palette = ["#1E40AF", "#2563EB", "#10B981", "#F59E0B", "#E11D48"]

        brand_kit = db.query(BrandKit).filter(BrandKit.workspace_id == workspace.id).first()
        if not brand_kit:
            brand_kit = BrandKit(
                workspace_id=workspace.id,
                name="Innovex Official Brand Kit",
                guidelines_raw=EMBEDDED_GUIDELINES,
                terminology_approved=approved_terms,
                terminology_banned=banned_terms,
                tone_rules=tone_rules,
                approved_facts=approved_facts,
                color_palette=color_palette,
                is_indexed=True,
            )
            db.add(brand_kit)
            db.flush()
            index_guidelines(brand_kit.id, EMBEDDED_GUIDELINES, db)

        # 4. Drafts
        creator_user = users["shrushti@innovex.com"]
        reviewer_user = users["asma@innovex.com"]
        manager_user = users["mahesh@innovex.com"]

        draft_samples = [
            (
                "Launch Campaign — Promotional Social Copy",
                (
                    "Introducing Brand Guard! We are the #1 in India brand protection tool. "
                    "Our software is 100% safe and guaranteed to stop every brand crisis. "
                    "Don't waste budget on expensive suites when you can get cheap software right here. "
                    "Primary highlight styled in #FF0055."
                ),
                "social_post",
                "in_review"
            ),
            (
                "Enterprise Welcome Email Template",
                (
                    "Welcome to BrandGuard AI! Founded in 2024, our enterprise-grade platform "
                    "empowers marketing teams with explainable AI findings and pre-publication governance. "
                    "Over 500+ enterprise clients onboarded trust our ISO-27001 certified architecture."
                ),
                "email",
                "approved"
            ),
            (
                "Instagram Ad Copy — Festive Season 2026",
                (
                    "This festive season, get the CHEAPEST brand safety solution in the market! "
                    "BrandGuard AI — the #1 in India AI-powered compliance tool that is 100% safe for your marketing team. "
                    "Guaranteed results or your money back! Don't miss this magic software deal. "
                    "Contact us now for an instant fix!"
                ),
                "social_post",
                "in_review"
            ),
            (
                "LinkedIn: Thought Leadership — AI in Brand Compliance",
                (
                    "At Innovex, we believe that explainable AI is the future of brand governance. "
                    "Our enterprise-grade BrandGuard AI platform has helped over 500+ enterprise clients maintain brand consistency "
                    "while remaining ASCI pre-publication guideline compliant. Founded in 2024, our mission is proactive protection."
                ),
                "social_post",
                "approved"
            )
        ]

        for title, content, ctype, status in draft_samples:
            d = db.query(Draft).filter(Draft.title == title).first()
            if not d:
                d = Draft(
                    workspace_id=workspace.id,
                    creator_id=creator_user.id,
                    title=title,
                    content=content,
                    content_type=ctype,
                    status=status,
                )
                db.add(d)
                db.flush()

                findings_data = run_all_checks(
                    content=content,
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

                if status == "in_review":
                    comm = Comment(
                        draft_id=d.id,
                        user_id=reviewer_user.id,
                        content="Flagged several banned terms and unverified superlative claims. Please rephrase."
                    )
                    db.add(comm)

                audit = AuditLog(
                    workspace_id=workspace.id,
                    user_id=creator_user.id,
                    action="draft_created",
                    entity_type="draft",
                    entity_id=d.id,
                    details={"title": title, "findings_count": len(findings_data)},
                    ai_service_used="rule_engine"
                )
                db.add(audit)

        db.commit()
        print("🌱 Seeding complete: Demo users, workspace, and brand kit created.")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Auto-seed error: {e}")
