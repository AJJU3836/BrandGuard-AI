# 🛡️ BrandGuard AI

> **Intelligent Pre-Publication Brand Governance Platform** — Catch brand inconsistencies, regulatory violations, and accessibility issues *before* content is published.

[![Live App](https://img.shields.io/badge/Live_App-Render-success)](https://brandguard-frontend-6swq.onrender.com)
[![API Status](https://img.shields.io/badge/API-Live-blue)](https://brandguard-api-zfcd.onrender.com)
[![Documentation](https://img.shields.io/badge/Round_3_PDF-Delivered-purple)](docs/BrandGuard_AI_Round_3_Submission.pdf)
[![Team](https://img.shields.io/badge/Team-Innovex-blue)]()
[![Event](https://img.shields.io/badge/Event-We%20Code%20Coders-purple)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 🌐 Live Production Deployment & Submission Links

| Service | Access Link | Production Status |
|---|---|---|
| **Frontend Application** | [brandguard-frontend-6swq.onrender.com](https://brandguard-frontend-6swq.onrender.com) | 🟢 Live (SPA Rewrite Enabled) |
| **Backend REST API** | [brandguard-api-zfcd.onrender.com](https://brandguard-api-zfcd.onrender.com) | 🟢 Live (FastAPI ASGI Engine) |
| **Interactive API Documentation** | [brandguard-api-zfcd.onrender.com/docs](https://brandguard-api-zfcd.onrender.com/docs) | 🟢 Live (OpenAPI 3.1 Swagger UI) |
| **Final Product PDF (Round 3)** | [docs/BrandGuard_AI_Round_3_Submission.pdf](docs/BrandGuard_AI_Round_3_Submission.pdf) | 📄 Complete Final Submission |
| **Product Document (DOCX)** | [docs/BrandGuard_AI_Round_3_Submission.docx](docs/BrandGuard_AI_Round_3_Submission.docx) | 📄 Source Submission File |
| **Source Code Repository** | [github.com/AJJU3836/BrandGuard-AI](https://github.com/AJJU3836/BrandGuard-AI) | 🟢 Live on GitHub |

### 🔑 Pre-Seeded Demo Accounts (Universal Password: `password123`)

Our platform features **1-Click Instant Sign-In** directly on the login page and an in-app **1-Click Role Switcher** in the sidebar. Evaluators can explore different personas without manual typing:

| Persona Role | Account Email | Governance Scope & Capabilities |
|---|---|---|
| 👑 **Admin** | `kaleajay626@gmail.com` | Full governance administration, workspace management & audit logs |
| 👔 **Manager** | `mahesh@innovex.com` | Brand kit policies, guideline-gap intelligence & risk matrices |
| 🔍 **Reviewer** | `asma@innovex.com` | Content verification, draft approval & requesting changes |
| ✍️ **Creator** | `shrushti@innovex.com` | Content drafting, visual diff review & 1-click suggestion fixes |

---

## What is BrandGuard AI?

BrandGuard AI is a **pre-publication governance platform** that checks marketing content (social posts, emails, blogs, press releases, and creative graphics) against your organization's own brand kit — terminology, claims, tone rules, approved facts, and visual palettes — and returns **explainable, source-cited findings** with 1-click corrections.

**Core Principle: "AI suggests, humans decide."** Nothing is silently modified or auto-published. Every recommendation cites exact brand clauses and regulatory standards.

---

## 🏆 Round 3 Delivered Commitments (All 3 Built & Verified)

In Round 2, Team Innovex committed to 3 specific improvements for Round 3. All three are 100% delivered, integrated, and verified in production:

### 1. 👁️ Gemini Vision Multimodal & WCAG Accessibility Engine
* **Visual Palette Compliance**: Extracts dominant colors and checks compliance with brand hex palettes.
* **WCAG 2.1 AA Contrast Ratios**: Calculates relative luminance ($L = 0.2126R + 0.7152G + 0.0722B$) and contrast ratios ($(L_1 + 0.05)/(L_2 + 0.05)$) using Pillow to guarantee enterprise inclusivity.
* **Alt-Text Audit**: Evaluates image accessibility and generates AI-assisted alt-text descriptions.
* **API Endpoint**: `POST /api/workspaces/{ws}/drafts/{draft_id}/review/image`

### 2. 📝 Interactive Visual Diff & 1-Click Suggestion Application
* **1-Click Suggestion Apply**: Clicking "Accept Suggestion" on any finding automatically replaces the violative phrase in the draft, marks the finding `accepted`, records an `AuditLog` entry, and increments the draft version.
* **Side-by-Side & Unified Diff View**: Compares draft versions word-by-word with green additions (`+word`) and red strike-through deletions (`~word~`).
* **In-Editor Clickable Highlights**: Clicking any colored flag in the text editor auto-scrolls to and highlights the corresponding finding card.
* **API Endpoint**: `POST /api/workspaces/{ws}/drafts/{draft_id}/review/findings/{id}/apply`

### 3. 📊 Guideline-Gap Intelligence & Root-Cause Analytics Dashboard
* **Governance Health Score**: Real-time score (0–100%) synthesizing severity, resolution rates, and drafting volume.
* **Guideline-Gap Root-Cause Diagnostics**: Clusters recurring violations and identifies which brand kit guidelines need clarification, complete with direct 1-click shortcuts to update brand kits.
* **Format Risk Heatmap Matrix**: Identifies governance risks across Social Posts, Emails, Blogs, and Press Releases.
* **Dual-Engine Telemetry**: Visualizes distribution between Rule Engine catches vs. AI reasoning.
* **API Endpoint**: `GET /api/workspaces/{ws}/dashboard/stats`

---

## 🛠️ Complete Feature Inventory

* ✅ **Brand Kit Ingestion**: Upload guidelines, approved terms, banned terms, tone rules, approved facts, and color palettes.
* ✅ **Semantic Guideline Indexing**: Chunked TF-IDF vector retrieval for sub-second clause grounding.
* ✅ **Deterministic Rule Engine**: High-speed regex checks (<50ms) for prohibited terms (`cheap`, `magic`, `miracle`, `#1 in India`, `100% safe`).
* ✅ **ASCI Regulatory Check**: Cross-checks claims against verified corporate facts under ASCI Chapter 1 truthfulness standards.
* ✅ **Zero-Walkthrough Evaluator Experience**:
  * 1-Click Instant Sign-In on login page.
  * Sidebar 1-Click Role Switcher.
  * Dual Sample Loaders: **"Load Violative Sample (Demo)"** (red violations) vs. **"Load Compliant Sample (Green Pass)"** (green 100% pass).
* ✅ **Export Findings**: 1-click audit reports exported in structured CSV or JSON.
* ✅ **Tamper-Evident Audit Ledger**: Append-only log tracking every creation, edit, suggestion acceptance, and status change.

---

## 🏗️ Technical Architecture

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 React 18 SPA (Vite)                   │
                  │  • Visual Diff Workspace   • Demo Role Switcher        │
                  │  • Image Audit Card        • Dual Sample Loaders       │
                  └──────────────────────────┬─────────────────────────────┘
                                             │ HTTPS / JWT
                                             ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                 FastAPI ASGI Gateway                   │
                  │     /auth  •  /workspaces  •  /drafts  •  /dashboard   │
                  └──────────────┬──────────────────────────┬──────────────┘
                                 │                          │
                 ┌───────────────▼──────────────┐   ┌───────▼──────────────────────┐
                 │    Deterministic Rule Engine │   │      Explainable AI Engine   │
                 │ • Banned terms regex         │   │ • Semantic TF-IDF Retrieval  │
                 │ • Hex palette check          │   │ • Gemini Grounded Review     │
                 │ • ASCI fact verification     │   │ • WCAG 2.1 AA Luminance Math │
                 └───────────────┬──────────────┘   └───────┬──────────────────────┘
                                 │                          │
                                 └───────────┬──────────────┘
                                             │
                                             ▼
                  ┌────────────────────────────────────────────────────────┐
                  │        Resilient Dual-Strategy Persistence             │
                  │ • Primary: PostgreSQL 16 on Render                     │
                  │ • Automated Fallback: Zero-Downtime SQLite Engine       │
                  │ • Lifespan Auto-Seeder (Demo Team, Kit & Drafts)       │
                  └────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started (Clone & Run Locally)

The repository is built to run out-of-the-box. When run locally without environment variables, the backend automatically uses **SQLite** and **seeds all demo data, users, and brand kits automatically**.

### Prerequisites
* **Node.js** (v18+) & **npm**
* **Python** (3.10+)

### 1. Clone the Repository
```bash
git clone https://github.com/AJJU3836/BrandGuard-AI.git
cd BrandGuard-AI
```

### 2. Launch the Backend API
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
* Backend starts at `http://localhost:8000`
* Interactive OpenAPI Swagger docs at `http://localhost:8000/docs`
* Database and demo team are auto-seeded on startup!

### 3. Launch the Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
* Frontend starts at `http://localhost:5173`
* Use any of the 1-click demo buttons on the sign-in screen to begin testing!

---

## 🧪 Running Automated Tests

To execute the automated end-to-end integration and regression suite:

```bash
# From repository root with backend venv active:
# Windows:
$env:PYTHONPATH='backend'; python scripts/test_e2e_polish.py

# Linux/macOS:
PYTHONPATH=backend python scripts/test_e2e_polish.py
```

### Test Suite Output:
```
✅ Creator login successful, ws_id: cc4cfa1a...
✅ New user registration auto-linked to workspace
✅ Violative draft created & audited (4 violations detected)
✅ 1-Click suggestion applied, new version: 2
✅ Compliant draft audited: 0 open violations (Expected 0)
✅ Dashboard stats loaded, Health Score: 100%
✅ Guideline gaps analyzed & indexed

🎉 ALL END-TO-END AUDIT & POLISH TESTS PASSED!
```

---

## 👥 Team Innovex

| Team Member | Role | Key Contributions |
|---|---|---|
| **Ajay Kale** (Lead) | Backend & AI Lead | Vision engine, WCAG math, 1-click suggestion endpoint, dual-DB fallback, Render deployment, E2E test harness |
| **Mahesh Gadekar** | Frontend & UI/UX Lead | Interactive visual diff, version comparison modal, demo role switcher, sample loaders, UI polish |
| **Asma Inamdar** | Research & Governance | ASCI advertising standards, WCAG 2.1 AA accessibility guidelines, multi-persona RBAC validation |
| **Shrushti Kharadkar** | Documentation & QA | Round 3 Final Product Document, README verification, edge-case testing, cross-browser audits |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
