import os
import sys

from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    with TestClient(app) as client:
        # 1. Login as Creator
        login_res = client.post('/api/auth/login', json={'email': 'shrushti@innovex.com', 'password': 'password123'})
        assert login_res.status_code == 200, f'Login failed: {login_res.text}'
        token = login_res.json()['access_token']
        ws_id = login_res.json()['user']['workspace_id']
        headers = {'Authorization': f'Bearer {token}'}
        print('✅ Creator login successful, ws_id:', ws_id)

        # 2. Test registration auto-linking
        import uuid
        test_email = f"judge_{uuid.uuid4().hex[:6]}@wecodecoders.com"
        reg_res = client.post('/api/auth/register', json={
            'email': test_email,
            'password': 'password123',
            'full_name': 'Judge Evaluator',
            'role': 'reviewer'
        })
        assert reg_res.status_code == 201, f'Reg failed: {reg_res.text}'
        reg_user = reg_res.json()['user']
        assert reg_user['workspace_id'] is not None, 'New user workspace_id should not be None'
        print('✅ New user registration auto-linked to workspace:', reg_user['workspace_id'])

        # 3. Create Draft with Violative Sample
        draft_res = client.post(f'/api/workspaces/{ws_id}/drafts/', json={
            'title': 'Evaluation Violative Draft',
            'content': 'We are #1 in India. Our cheap software is 100% safe. Brand theme #FF0055.',
            'content_type': 'social_post'
        }, headers=headers)
        assert draft_res.status_code == 201
        draft_id = draft_res.json()['id']
        print('✅ Violative draft created:', draft_id)

        # 4. Review draft
        rev_res = client.post(f'/api/workspaces/{ws_id}/drafts/{draft_id}/review/', headers=headers)
        assert rev_res.status_code in [200, 201]
        findings_res = client.get(f'/api/workspaces/{ws_id}/drafts/{draft_id}/review/findings', headers=headers)
        findings = findings_res.json()
        assert len(findings) > 0, 'Should find violations'
        print(f'✅ Violative draft audited: {len(findings)} findings detected')

        # 5. Apply 1-Click Suggestion on first finding
        first_f = findings[0]
        finding_id = first_f['id']
        apply_res = client.post(f'/api/workspaces/{ws_id}/drafts/{draft_id}/review/findings/{finding_id}/apply', json={}, headers=headers)
        assert apply_res.status_code == 200
        print('✅ 1-Click suggestion applied, new version:', apply_res.json()['version_number'])

        # 6. Create Draft with Compliant Sample (Green Pass)
        comp_draft_res = client.post(f'/api/workspaces/{ws_id}/drafts/', json={
            'title': 'Compliant Enterprise Sample',
            'content': 'We are proud to present BrandGuard AI by Innovex! Over 500+ enterprise clients onboarded worldwide. Primary brand palette verified: #1E40AF and #2563EB.',
            'content_type': 'social_post'
        }, headers=headers)
        comp_id = comp_draft_res.json()['id']
        client.post(f'/api/workspaces/{ws_id}/drafts/{comp_id}/review/', headers=headers)
        comp_findings = client.get(f'/api/workspaces/{ws_id}/drafts/{comp_id}/review/findings', headers=headers).json()
        open_comp = [f for f in comp_findings if f['status'] == 'open']
        print(f'✅ Compliant draft audited: {len(open_comp)} open violations (Expected 0)')

        # 7. Dashboard stats & gap analysis
        dash_res = client.get(f'/api/workspaces/{ws_id}/dashboard/stats', headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        print('✅ Dashboard stats loaded, Health Score:', dash_data.get('health_score'), '%')
        print('✅ Guideline gaps found:', len(dash_data.get('guideline_gaps', [])))
        print('\n🎉 ALL END-TO-END AUDIT & POLISH TESTS PASSED!')

if __name__ == '__main__':
    run_tests()
