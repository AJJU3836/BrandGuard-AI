"""
BrandGuard AI — Demo Database Seeder

Seeds realistic workspace, team users, brand kit, and draft content with findings.
Run with:
    python sample-brand-kit/seed_demo.py
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)

# Default to SQLite for easy local test if DATABASE_URL is not set
os.environ.setdefault("DATABASE_URL", "sqlite:///./brandguard_demo.db")

from app.core.database import Base, engine, SessionLocal
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


def seed():
    print("🌱 Initializing BrandGuard AI database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create Workspace
        print("🏢 Creating workspace 'Innovex Governance'...")
        workspace = db.query(Workspace).filter(Workspace.name == "Innovex Governance").first()
        if not workspace:
            workspace = Workspace(
                name="Innovex Governance",
                description="Official Innovex workspace for intelligent brand governance."
            )
            db.add(workspace)
            db.flush()

        # 2. Create Team Users
        print("👥 Creating team accounts (password: 'password123')...")
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

        # 3. Create Brand Kit
        print("🎨 Creating 'Innovex Official Brand Kit'...")
        brand_kit = db.query(BrandKit).filter(BrandKit.workspace_id == workspace.id).first()
        guidelines_path = os.path.join(os.path.dirname(__file__), "brand_guidelines.txt")
        guidelines_content = ""
        if os.path.exists(guidelines_path):
            with open(guidelines_path, "r", encoding="utf-8") as f:
                guidelines_content = f.read()

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

        if not brand_kit:
            brand_kit = BrandKit(
                workspace_id=workspace.id,
                name="Innovex Official Brand Kit",
                guidelines_raw=guidelines_content,
                terminology_approved=approved_terms,
                terminology_banned=banned_terms,
                tone_rules=tone_rules,
                approved_facts=approved_facts,
                color_palette=color_palette,
                is_indexed=True,
            )
            db.add(brand_kit)
            db.flush()
            index_guidelines(brand_kit.id, guidelines_content, db)

        # 4. Create Sample Drafts
        print("📝 Creating demo drafts...")
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
            )
        ]

        creator_user = users["shrushti@innovex.com"]
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

                # Run rule checks
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

                # Add sample comment
                if status == "in_review":
                    comm = Comment(
                        draft_id=d.id,
                        user_id=users["asma@innovex.com"].id,
                        content="Flagged several ASCI-violative superlative claims. Please verify against approved facts before publishing."
                    )
                    db.add(comm)

                # Add audit log
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
        print("✅ Demo database successfully seeded!")
        print("\nLogin credentials for testing:")
        for email, name, role in team:
            print(f"  • {name} ({role}): {email} / password123")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
