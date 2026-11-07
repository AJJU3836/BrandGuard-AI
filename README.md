# 🛡️ BrandGuard AI

> **Intelligent Brand-Governance Platform** — Catch brand problems before they're published.

[![Live App](https://img.shields.io/badge/Live_App-Render-success)](https://brandguard-frontend-6swq.onrender.com)
[![API Status](https://img.shields.io/badge/API-Live-blue)](https://brandguard-api-zfcd.onrender.com)
[![Team](https://img.shields.io/badge/Team-Innovex-blue)]()
[![Event](https://img.shields.io/badge/Event-Inkloom%20AI-purple)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 🌐 Live Deployment & Demo

| Service | Link | Status |
|---|---|---|
| **Frontend Application** | [brandguard-frontend-6swq.onrender.com](https://brandguard-frontend-6swq.onrender.com) | 🟢 Live |
| **Backend REST API** | [brandguard-api-zfcd.onrender.com](https://brandguard-api-zfcd.onrender.com) | 🟢 Live |
| **Interactive API Docs** | [brandguard-api-zfcd.onrender.com/docs](https://brandguard-api-zfcd.onrender.com/docs) | 🟢 Live |
| **Submission PDF** | [docs/BrandGuard_AI_Round_2_Submission.pdf](docs/BrandGuard_AI_Round_2_Submission.pdf) | 📄 Documented |

### 🔑 Demo Accounts (All passwords: `password123`)
- **Admin**: `kaleajay626@gmail.com`
- **Manager**: `mahesh@innovex.com`
- **Reviewer**: `asma@innovex.com`
- **Creator**: `shrushti@innovex.com`

---

## What is BrandGuard AI?

BrandGuard AI is a **pre-publication review platform** that checks every piece of content (text, images) against your organisation's own brand kit — guidelines, approved facts, tone rules, terminology, and visual assets — and returns **explained, source-linked findings** with suggested corrections.

**Key principle: AI suggests, humans decide.** Nothing is auto-applied or auto-approved.

---

## The Problem

Brand guidelines exist as long PDFs nobody reads. Content is created by employees, freelancers, agencies, and AI tools — each interpreting the brand differently. Issues are caught only *after* publication, often by regulators (ASCI flagged 98% of scrutinised ads in FY 2025-26).

## The Solution

Upload your brand kit once → upload any draft → get instant, explainable feedback with source citations → approve through a proper review workflow → publish with confidence.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | Python + FastAPI |
| Database | PostgreSQL + pgvector |
| AI | LLM API (grounded in retrieved guidelines) |
| Auth | JWT + RBAC |

---

## Project Structure

```
BrandGuard-AI/
├── frontend/               # React app
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Upload, Findings, Dashboard, Review
│   │   ├── services/       # API calls
│   │   └── App.jsx
│   └── package.json
├── backend/                # FastAPI server
│   ├── app/
│   │   ├── api/            # Route handlers
│   │   ├── core/           # Config, security, auth
│   │   ├── models/         # DB & Pydantic models
│   │   ├── services/       # Business logic (rule_engine, ai_engine, retrieval)
│   │   └── main.py
│   └── requirements.txt
├── docs/                   # Architecture diagrams, API docs
├── sample-brand-kit/       # Demo brand kit for testing
├── PROGRESS.md             # ← Team progress tracker (READ THIS)
└── README.md               # You are here
```

---

## Team Innovex

| Member | Role | Responsibilities |
|---|---|---|
| **Ajay Kale** (Lead) | Backend & AI Pipeline | Guideline ingestion/retrieval, claim & tone checks, APIs, database, RBAC, audit log, deployment |
| **Mahesh Gadekar** | Frontend & UI/UX | Upload screen, findings view, suggestion diff, reviewer dashboard, insights charts |
| **Asma Inamdar** | Research & Communication | Survey, interviews, user testing, feedback, impact write-up |
| **Shrushti Kharadkar** | Documentation & Presentation | Plan doc, workflow diagrams, final presentation, demo video, coordination |

---

## Getting Started

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+
- PostgreSQL 15+ (with pgvector extension)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Development Phases

| Phase | Goal | Status |
|---|---|---|
| **Round 1: The Plan** | Define problem, users, solution, architecture | ✅ Complete |
| **Round 2: The Build** | Core MVP — brand kit import, text review, findings, approval workflow, deployed demo | 🔄 In Progress |
| **Round 3: The Finish** | Image checks, claim verification, guideline-gap insights, revision history, demo video | ⬜ Not Started |

> 📌 See **[PROGRESS.md](PROGRESS.md)** for detailed task tracking and daily updates.

---

## Core Features

- ✅ **Brand Kit Import** — Guidelines, facts, terminology, assets
- ✅ **AI-Powered Review** — Tone, messaging, claims (grounded in your guidelines)
- ✅ **Rule Engine** — Banned terms, colour palette, contrast, alt-text
- ✅ **Explainable Findings** — Every flag cites its source
- ✅ **Suggestion Diff** — Visual diff, never auto-applied
- ✅ **Approval Workflow** — Draft → Review → Approved
- ✅ **Insights Dashboard** — Recurring issues, unclear guidelines
- ✅ **Audit Log** — Full transparency

---

## Contributing

1. Pull latest from `main`
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit with clear messages
4. Push and open a PR
5. Update **PROGRESS.md** with your progress

---

## License

MIT License — see [LICENSE](LICENSE) for details.
