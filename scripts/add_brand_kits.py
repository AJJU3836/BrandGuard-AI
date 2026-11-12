import httpx

def main():
    client = httpx.Client(base_url='https://brandguard-api-zfcd.onrender.com', timeout=30.0)

    # Login as admin
    r_login = client.post('/api/auth/login', json={'email': 'kaleajay626@gmail.com', 'password': 'password123'})
    print('Admin Login:', r_login.status_code)
    token = r_login.json()['access_token']
    ws_id = r_login.json()['user']['workspace_id']
    headers = {'Authorization': f'Bearer {token}'}

    existing_kits = [k['name'] for k in client.get(f'/api/workspaces/{ws_id}/brand-kits/', headers=headers).json()]
    print('Existing Kits:', existing_kits)

    kits_to_add = [
        {
            'name': 'Apex Wealth & FinTech Governance Kit',
            'guidelines_raw': '''APEX FINANCIAL TECHNOLOGIES — REGULATORY & BRAND GOVERNANCE POLICY (v3.1)
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
- Strict Rule: High-contrast disclaimers must satisfy WCAG 2.1 AA (minimum 4.5:1 ratio against background).''',
            'terminology_approved': ['Apex Wealth', 'SEBI-registered', 'institutional custody', 'risk-adjusted returns', 'algorithmic rebalancing', 'fiduciary'],
            'terminology_banned': ['guaranteed returns', 'risk-free', '100% profit', 'get rich', 'instant payout', 'double your money', 'can\'t lose'],
            'tone_rules': ['Prudent', 'Disciplined', 'Transparent', 'Fiduciary', 'No FOMO'],
            'approved_facts': ['SEBI Registration Number INP000007890', 'Over 2400 Crores AUM', 'Custody backed by top-tier institutions', 'Audited by Big 4'],
            'color_palette': ['#0F172A', '#0D9488', '#D97706', '#64748B']
        },
        {
            'name': 'Aura BioHealth & Wellness Brand Kit',
            'guidelines_raw': '''AURA BIOHEALTH & LIFE SCIENCES — CLINICAL GOVERNANCE GUIDELINES (v1.8)
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
- Medical Imagery Rule: Avoid graphic medical imagery or before/after photos with deceptive lighting or digital retouching.''',
            'terminology_approved': ['Aura BioHealth', 'clinically evaluated', 'dermatologist tested', 'evidence-backed formulation', 'cellular hydration', 'standardized bio-extracts'],
            'terminology_banned': ['miracle cure', 'instant weight loss', '100% cure', 'reverse aging overnight', 'cancer preventive', 'magical healing', 'permanent relief'],
            'tone_rules': ['Empathetic', 'Clinically Accurate', 'Modest', 'Scientifically Grounded'],
            'approved_facts': ['Clinically evaluated across 1200 participants', 'WHO-GMP certified facilities', 'ISO-22000 and FSSAI approved', 'Published in Peer-Reviewed Journals'],
            'color_palette': ['#065F46', '#0284C7', '#10B981', '#F3F4F6']
        }
    ]

    for k in kits_to_add:
        if k['name'] not in existing_kits:
            r = client.post(f'/api/workspaces/{ws_id}/brand-kits/', json=k, headers=headers)
            if r.status_code == 201:
                kit_id = r.json()['id']
                client.post(f'/api/workspaces/{ws_id}/brand-kits/{kit_id}/index', headers=headers)
                print('✅ Added & indexed brand kit:', k['name'])

    updated_kits = client.get(f'/api/workspaces/{ws_id}/brand-kits/', headers=headers).json()
    print('\nTotal Brand Kits on Live Server Now:', len(updated_kits))
    for uk in updated_kits:
        app_len = len(uk.get('terminology_approved') or [])
        ban_len = len(uk.get('terminology_banned') or [])
        print(f"  • {uk['name']} ({app_len} approved, {ban_len} banned terms)")

if __name__ == '__main__':
    main()
