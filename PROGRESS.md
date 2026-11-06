# 📊 BrandGuard AI — Progress Tracker

> **Last Updated:** 2026-11-06
> **Team:** Innovex (Ajay, Mahesh, Asma, Shrushti)
> **Repo:** https://github.com/AJJU3836/BrandGuard-AI

---

## 🎯 Project Goal

Build a **pre-publication, AI-powered brand-governance platform** that:
1. Lets organisations upload their brand kit (guidelines, facts, terms, assets)
2. Checks any draft content against that kit using AI + rule engine
3. Returns **explained, source-cited findings** with visual diff suggestions
4. Supports a **Creator → Manager → Reviewer** approval workflow
5. Provides an **insights dashboard** showing recurring issues & unclear guidelines
6. Maintains a full **audit log** with AI-use transparency

**One-liner:** *"Catch brand problems before they're published — explain every flag — keep humans in charge."*

---

## 👥 Team Roles & Ownership

| Member | Role | Owns |
|---|---|---|
| **Ajay Kale** 🟢 | Backend & AI Pipeline Lead | `backend/`, database, AI engine, retrieval, auth, deployment |
| **Mahesh Gadekar** 🔵 | Frontend & UI/UX Lead | `frontend/`, all UI pages, components, API integration |
| **Asma Inamdar** 🟡 | Research & Communication Lead | User research, testing, feedback collection, impact write-up |
| **Shrushti Kharadkar** 🟣 | Documentation & Presentation Lead | `docs/`, diagrams, demo video, presentation, coordination |

---

## 📅 Round 2: The Build (Current Phase)

> **Goal:** Core workflow runs end-to-end. Deployed demo.

### Backend Tasks (Ajay 🟢)

| # | Task | Status | Notes |
|---|---|---|---|
| B1 | Project scaffolding — FastAPI app structure, config, `.env` | ⬜ Not Started | |
| B2 | Database schema — Users, Workspaces, BrandKits, Drafts, Versions, Findings, Comments, AuditLog | ⬜ Not Started | |
| B3 | Auth — JWT login/register, RBAC middleware (Creator/Manager/Reviewer) | ⬜ Not Started | |
| B4 | Brand Kit Upload API — Accept PDF/text, store files | ⬜ Not Started | |
| B5 | Guideline Indexing — PDF parsing, clause splitting, vectorize with pgvector | ⬜ Not Started | |
| B6 | Rule Engine — Banned terms check, colour validation | ⬜ Not Started | |
| B7 | AI Review Engine — LLM-based tone/claim/messaging check, grounded in retrieved guidelines | ⬜ Not Started | |
| B8 | Findings API — Return findings with severity, explanation, source citation | ⬜ Not Started | |
| B9 | Suggestion API — Generate diff-based suggestions | ⬜ Not Started | |
| B10 | Approval Workflow API — Status transitions, comments | ⬜ Not Started | |
| B11 | Audit Log — Immutable log of all actions | ⬜ Not Started | |
| B12 | Deployment — Cloud deploy (Render/Railway), env setup | ⬜ Not Started | |

### Frontend Tasks (Mahesh 🔵)

| # | Task | Status | Notes |
|---|---|---|---|
| F1 | Project scaffolding — React + Vite, routing, folder structure | ⬜ Not Started | |
| F2 | Auth Pages — Login, Register, role selection | ⬜ Not Started | |
| F3 | Brand Kit Upload Page — Drag-drop for guidelines, facts, terms, assets | ⬜ Not Started | |
| F4 | Draft Upload Page — Text/image upload, content type selection | ⬜ Not Started | |
| F5 | Findings View — Annotated content with severity badges, source citations | ⬜ Not Started | |
| F6 | Suggestion Diff View — Visual diff with accept/reject per suggestion | ⬜ Not Started | |
| F7 | Reviewer Dashboard — Drafts pending review, comment thread, approve/reject | ⬜ Not Started | |
| F8 | Insights Dashboard — Charts: issues by type, by team, by guideline clause | ⬜ Not Started | |
| F9 | Responsive & accessible design | ⬜ Not Started | |
| F10 | API Integration — Connect all pages to backend APIs | ⬜ Not Started | |

### Research Tasks (Asma 🟡)

| # | Task | Status | Notes |
|---|---|---|---|
| R1 | User survey — students, club social-media, small-business marketers | ⬜ Not Started | |
| R2 | 2-3 short interviews — people who manage social media / marketing content | ⬜ Not Started | |
| R3 | Collect off-brand examples — wrong logo colour, tone mismatch, etc. | ⬜ Not Started | |
| R4 | Create sample brand kit — realistic guidelines, facts, terms for demo | ⬜ Not Started | |
| R5 | User testing — test MVP with 3-5 users, collect feedback | ⬜ Not Started | |
| R6 | Document feedback and improvement suggestions | ⬜ Not Started | |

### Documentation Tasks (Shrushti 🟣)

| # | Task | Status | Notes |
|---|---|---|---|
| D1 | Architecture diagram — system overview, data flow | ⬜ Not Started | |
| D2 | API documentation — endpoints, request/response schemas | ⬜ Not Started | |
| D3 | Setup guide — how to run the project locally | ⬜ Not Started | |
| D4 | Architecture notes — design decisions and trade-offs | ⬜ Not Started | |

---

## 📅 Round 3: The Finish (Upcoming)

> **Goal:** Complete, polish, and present.

| # | Task | Owner | Status |
|---|---|---|---|
| R3-1 | Image & accessibility checks (logo, palette, alt-text, contrast) | Ajay 🟢 | ⬜ Not Started |
| R3-2 | Claim verification against approved facts list | Ajay 🟢 | ⬜ Not Started |
| R3-3 | Guideline-gap insights — dashboard shows unclear rules | Ajay 🟢 + Mahesh 🔵 | ⬜ Not Started |
| R3-4 | Revision history — visual diff between versions + reviewer comments | Mahesh 🔵 | ⬜ Not Started |
| R3-5 | AI-use disclosure UI | Mahesh 🔵 | ⬜ Not Started |
| R3-6 | Testing evidence — compile user feedback, test results | Asma 🟡 | ⬜ Not Started |
| R3-7 | Privacy & responsible-design explanation | Asma 🟡 | ⬜ Not Started |
| R3-8 | Demo video script & recording | Shrushti 🟣 | ⬜ Not Started |
| R3-9 | Final presentation | Shrushti 🟣 | ⬜ Not Started |
| R3-10 | Final report & roadmap | Shrushti 🟣 + Asma 🟡 | ⬜ Not Started |

---

## 📝 Daily Updates

> Each team member should add a brief entry here at the end of each work session.

### 2026-11-06

| Member | What I did | What I'll do next | Blockers |
|---|---|---|---|
| Ajay | Project setup, plan created, repo initialized | Backend scaffolding (B1), DB schema (B2) | None |
| Mahesh | — | — | — |
| Asma | — | — | — |
| Shrushti | — | — | — |

---

## 🔗 Quick Links

| Resource | Link |
|---|---|
| GitHub Repo | https://github.com/AJJU3836/BrandGuard-AI |
| Google Drive | https://drive.google.com/drive/folders/1ybSTBQjKro8z8dBaycZW9Flvnrpbdp3r?usp=sharing |
| Team Lead Email | Kaleajay626@gmail.com |

---

## How to Update This File

1. **Status values:** ⬜ Not Started → 🔄 In Progress → ✅ Done → ❌ Blocked
2. Add notes in the **Notes** column for context
3. Add your daily update row in the **Daily Updates** section
4. Commit this file with your code changes

---

> [!TIP]
> **For new team members:** Start by reading the [README.md](README.md) for the overview, then this file for detailed tasks. Check which tasks are assigned to you and start with the ones marked "Not Started".
