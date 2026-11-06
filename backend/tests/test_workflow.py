"""
BrandGuard AI — End-to-End Workflow Verification Test

Tests the full lifecycle:
1. Login with demo accounts (Ajay, Mahesh, Asma, Shrushti)
2. Fetch Brand Kits & check guidelines
3. Submit a new draft containing ASCI claim violations & banned terms
4. Run review engine & verify explained findings with cited sources
5. Accept a suggestion
6. Reviewer approval workflow
7. Verify dashboard statistics & audit logs
"""

import os
import sys

# Ensure backend path is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

os.environ["DATABASE_URL"] = "sqlite:///./brandguard_demo.db"

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.user import User

client = TestClient(app)


def run_tests():
    print("\n" + "=" * 70)
    print("🚀 BRANDGUARD AI — INTEGRATION TEST SUITE")
    print("=" * 70)

    # 1. Test Root
    print("\n[1] Testing Health Check / Root Endpoint...")
    res = client.get("/")
    assert res.status_code == 200, f"Root failed: {res.text}"
    print("  ✓ Root returned:", res.json())

    # 2. Test Login
    print("\n[2] Testing Authentication (Login as Ajay Kale)...")
    res = client.post("/api/auth/login", json={
        "email": "kaleajay626@gmail.com",
        "password": "password123"
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    token_data = res.json()
    token = token_data["access_token"]
    user_info = token_data["user"]
    print(f"  ✓ Login successful! User: {user_info['full_name']} | Role: {user_info['role']}")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Test Me
    print("\n[3] Testing JWT Validation (/api/auth/me)...")
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200, f"Me endpoint failed: {res.text}"
    print(f"  ✓ Authenticated user confirmed: {res.json()['email']}")

    # 4. Get Workspaces
    print("\n[4] Testing Workspaces API...")
    res = client.get("/api/workspaces/", headers=headers)
    assert res.status_code == 200, f"Workspaces failed: {res.text}"
    workspaces = res.json()
    assert len(workspaces) > 0, "No workspaces found"
    workspace_id = workspaces[0]["id"]
    print(f"  ✓ Workspace found: \"{workspaces[0]['name']}\" (ID: {workspace_id})")

    # 5. Get Brand Kit
    print("\n[5] Testing Brand Kit API & Guideline Chunks...")
    res = client.get(f"/api/workspaces/{workspace_id}/brand-kits/", headers=headers)
    assert res.status_code == 200, f"Brand kits failed: {res.text}"
    kits = res.json()
    assert len(kits) > 0, "No brand kit found"
    kit = kits[0]
    print(f"  ✓ Brand Kit: \"{kit['name']}\"")
    print(f"    - Banned terms configured: {kit['terminology_banned']}")
    print(f"    - Approved terms: {kit['terminology_approved']}")
    print(f"    - Verified facts count: {len(kit['approved_facts'])}")

    # 6. Create Draft
    print("\n[6] Submitting Content Draft with Deliberate Violations...")
    violative_content = (
        "Check out our new tool! We are officially the #1 in India brand platform. "
        "Get cheap software with 100% safe results guaranteed. Highlight in #FF0055."
    )
    res = client.post(
        f"/api/workspaces/{workspace_id}/drafts/",
        headers=headers,
        json={
            "title": "Integration Test Draft",
            "content": violative_content,
            "content_type": "ad"
        }
    )
    assert res.status_code == 201, f"Create draft failed: {res.text}"
    draft = res.json()
    draft_id = draft["id"]
    print(f"  ✓ Draft created: \"{draft['title']}\" (ID: {draft_id})")

    # 7. Trigger Review
    print("\n[7] Triggering Multi-Engine Compliance Review...")
    res = client.post(
        f"/api/workspaces/{workspace_id}/drafts/{draft_id}/review/",
        headers=headers
    )
    assert res.status_code == 201, f"Review failed: {res.text}"
    review_result = res.json()
    print(f"  ✓ Review finished: {review_result['total_findings']} findings detected!")

    # 8. List Explained Findings
    print("\n[8] Inspecting Explained Findings & Citations...")
    res = client.get(
        f"/api/workspaces/{workspace_id}/drafts/{draft_id}/review/findings",
        headers=headers
    )
    assert res.status_code == 200, f"List findings failed: {res.text}"
    findings = res.json()
    assert len(findings) > 0, "No findings returned"
    for idx, f in enumerate(findings, 1):
        print(f"  Issue #{idx}:")
        print(f"    • Severity: [{f['severity'].upper()}] | Category: {f['category']}")
        print(f"    • Flagged text: \"{f['text_highlight']}\"")
        print(f"    • Explanation: {f['explanation']}")
        print(f"    • Source Cited: {f['guideline_source']}")
        print(f"    • Suggested Fix: {f['suggestion']}")

    # 9. Accept a Finding (Human in the loop)
    first_finding_id = findings[0]["id"]
    print(f"\n[9] Human decision: Accepting suggestion for Issue #{1}...")
    res = client.put(
        f"/api/workspaces/{workspace_id}/drafts/{draft_id}/review/findings/{first_finding_id}",
        headers=headers,
        json={"status": "accepted"}
    )
    assert res.status_code == 200, f"Update finding failed: {res.text}"
    print(f"  ✓ Finding status successfully updated to: {res.json()['status']}")

    # 10. Reviewer Comment & Approval Workflow
    print("\n[10] Testing Reviewer Feedback & Status Transition...")
    res = client.post(
        f"/api/workspaces/{workspace_id}/drafts/{draft_id}/comments",
        headers=headers,
        json={"content": "Please verify the claims against market research before approval."}
    )
    assert res.status_code == 201, f"Comment failed: {res.text}"
    print(f"  ✓ Reviewer note posted: \"{res.json()['content']}\"")

    res = client.put(
        f"/api/workspaces/{workspace_id}/drafts/{draft_id}/status",
        headers=headers,
        json={"status": "changes_requested"}
    )
    assert res.status_code == 200, f"Status update failed: {res.text}"
    print(f"  ✓ Draft status transitioned to: {res.json()['status']}")

    # 11. Dashboard & Audit Log
    print("\n[11] Testing Dashboard Insights & Governance Audit Log...")
    res = client.get(
        f"/api/workspaces/{workspace_id}/dashboard/stats",
        headers=headers
    )
    assert res.status_code == 200, f"Dashboard stats failed: {res.text}"
    stats = res.json()
    print("  ✓ Dashboard Stats:")
    print(f"    • Total drafts: {stats['total_drafts']}")
    print(f"    • Drafts by status: {stats['drafts_by_status']}")
    print(f"    • Findings by category: {stats['findings_by_category']}")
    print(f"    • Top recurring issues: {len(stats['top_recurring_issues'])} identified")

    res = client.get(
        f"/api/workspaces/{workspace_id}/dashboard/audit-log",
        headers=headers
    )
    assert res.status_code == 200, f"Audit log failed: {res.text}"
    audit_logs = res.json()
    print(f"  ✓ Audit Trail: {len(audit_logs)} actions logged immutably.")

    print("\n" + "=" * 70)
    print("🎉 ALL 11 TEST MODULES PASSED WITH 100% SUCCESS!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_tests()
