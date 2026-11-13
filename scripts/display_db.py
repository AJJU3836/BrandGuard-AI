import httpx
import json

def fetch_and_print():
    client = httpx.Client(base_url='https://brandguard-api-zfcd.onrender.com', timeout=30.0)
    
    # 1. Login
    r_login = client.post('/api/auth/login', json={'email': 'kaleajay626@gmail.com', 'password': 'password123'})
    token = r_login.json()['access_token']
    current_user = r_login.json()['user']
    ws_id = current_user['workspace_id']
    headers = {'Authorization': f'Bearer {token}'}

    # Fetch data
    workspaces = client.get('/api/workspaces/', headers=headers).json()
    brand_kits = client.get(f'/api/workspaces/{ws_id}/brand-kits/', headers=headers).json()
    drafts = client.get(f'/api/workspaces/{ws_id}/drafts/', headers=headers).json()
    audit_logs = client.get(f'/api/workspaces/{ws_id}/dashboard/audit-log?limit=20', headers=headers).json()

    print("=" * 80)
    print("🛡️ BRANDGUARD AI — LIVE DATABASE RECORDS INVENTORY")
    print("=" * 80)
    print()

    # Workspaces
    print("### 1. Workspaces Table")
    print("| Workspace ID | Workspace Name | Description | Created At |")
    print("|---|---|---|---|")
    for ws in workspaces:
        print(f"| `{ws['id']}` | **{ws['name']}** | {ws['description']} | {ws.get('created_at', 'N/A')[:19]} |")
    print()

    # Brand Kits
    print("### 2. Brand Kits Table (3 Active Kits)")
    print("| Kit ID | Name | Approved Terms | Banned Terms | Tone Rules | Approved Facts | Palette |")
    print("|---|---|---|---|---|---|---|")
    for bk in brand_kits:
        app_terms = ", ".join(bk.get('terminology_approved') or [])
        ban_terms = ", ".join(bk.get('terminology_banned') or [])
        tones = ", ".join(bk.get('tone_rules') or [])
        facts = f"{len(bk.get('approved_facts') or [])} facts"
        colors = ", ".join(bk.get('color_palette') or [])
        print(f"| `{bk['id'][:8]}...` | **{bk['name']}** | {app_terms} | `{ban_terms}` | {tones} | {facts} | `{colors}` |")
    print()

    # Drafts
    print("### 3. Content Drafts Table (6 Live Drafts)")
    print("| Draft ID | Title | Format | Status | Word Count |")
    print("|---|---|---|---|---|")
    for d in drafts:
        words = len(d['content'].split())
        print(f"| `{d['id'][:8]}...` | **{d['title']}** | `{d['content_type']}` | `{d['status']}` | {words} words |")
    print()

    # Findings
    print("### 4. Explained Governance Findings Table")
    print("| Draft Title | Severity | Category | Highlighted Text | Guideline Violation | Engine |")
    print("|---|---|---|---|---|---|")
    for d in drafts:
        f_res = client.get(f"/api/workspaces/{ws_id}/drafts/{d['id']}/review/findings", headers=headers)
        if f_res.status_code == 200:
            for f in f_res.json():
                engine_badge = "Gemini AI" if f.get('is_ai_generated') else "Rule Engine"
                text_hl = (f.get('text_highlight') or "")[:35].replace('\n', ' ')
                sugg = (f.get('suggestion') or "")[:40].replace('\n', ' ')
                print(f"| {d['title'][:25]} | `{f['severity']}` | `{f['category']}` | \"{text_hl}...\" | {f.get('guideline_source', 'N/A')} | {engine_badge} |")
    print()

    # Audit Logs
    print("### 5. Governance Audit Trail Table (Recent 10 Records)")
    print("| Log ID | Action | Entity Type | User / Actor | Service Engine | Recorded Timestamp |")
    print("|---|---|---|---|---|---|")
    for a in audit_logs[:10]:
        print(f"| `{a['id'][:8]}...` | `{a['action']}` | `{a['entity_type']}` | `{a['user_id'][:8]}...` | `{a.get('ai_service_used', 'system')}` | {a.get('created_at', 'N/A')[:19]} |")

if __name__ == '__main__':
    fetch_and_print()
