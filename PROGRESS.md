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
| B1 | Project scaffolding — FastAPI app structure, config, `.env` | ✅ Done | `backend/app/main.py`, `core/config.py`, `requirements.txt` |
| B2 | Database schema — Users, Workspaces, BrandKits, Drafts, Findings, Comments, AuditLog | ✅ Done | Platform-independent GUID & JSON supporting Postgres + SQLite |
| B3 | Auth — JWT login/register, RBAC middleware (Creator/Manager/Reviewer) | ✅ Done | Passlib bcrypt + python-jose JWT + OAuth2PasswordBearer |
| B4 | Brand Kit Upload API — Accept text/clauses, store rules | ✅ Done | Full CRUD in `/api/workspaces/{id}/brand-kits/` |
| B5 | Guideline Indexing — Splitting into clauses for retrieval | ✅ Done | RecursiveCharacterTextSplitter in `brand_kit_service.py` |
| B6 | Rule Engine — Banned terms, approved terms variants, unsupported claims, color palette | ✅ Done | Tested & working: regex word boundaries + ASCI claims matching |
| B7 | AI Review Engine — LLM-based tone/claim check, grounded in retrieved guidelines | 🔄 In Progress | Scaffolding & prompt interface created; ready for live API key |
| B8 | Findings API — Return findings with severity, explanation, source citation | ✅ Done | Returns structured findings with citation & suggestion |
| B9 | Suggestion API — Generate diff-based suggestions & acceptance | ✅ Done | Creators/reviewers can accept or reject per finding |
| B10 | Approval Workflow API — Status transitions, comments | ✅ Done | Draft → In Review → Changes Requested → Approved |
| B11 | Audit Log — Immutable log of all actions | ✅ Done | Every draft creation, status update, and review logged |
| B12 | Deployment — Cloud deploy, env setup | 🔄 In Progress | Ready for Render / Railway / Vercel deployment |

### Frontend Tasks (Mahesh 🔵)

| # | Task | Status | Notes |
|---|---|---|---|
| F1 | Project scaffolding — React + Vite, routing, TailwindCSS | ✅ Done | `frontend/package.json`, `vite.config.js`, `tailwind.config.js` |
| F2 | Auth Pages — Login, Register with role picker | ✅ Done | `Login.jsx` & `Register.jsx` connected to AuthContext |
| F3 | Brand Kit Page — Rules, terms, facts, color palette | ✅ Done | `BrandKits.jsx` with modal & one-click sample loader |
| F4 | Draft Creation Page — Text input, format selection | ✅ Done | `CreateDraft.jsx` with one-click violative sample loader |
| F5 | Findings View — Annotated issues with citations | ✅ Done | `DraftReview.jsx` side-by-side inspect panel |
| F6 | Suggestion Diff & Actions — Accept / Reject | ✅ Done | Interactive buttons updating finding status in real-time |
| F7 | Reviewer Controls — Status transitions, comments | ✅ Done | Approve / Request changes buttons & discussion feed |
| F8 | Insights Dashboard — Charts & recurring issues | ✅ Done | `Dashboard.jsx` stats, category breakdown, guideline gaps |
| F9 | Responsive & accessible design | ✅ Done | Responsive sidebar layout with WCAG contrast |
| F10 | API Integration — Connect all pages to backend APIs | ✅ Done | Centralized Axios service with JWT interceptor |

### Research & Assets Tasks (Asma 🟡)

| # | Task | Status | Notes |
|---|---|---|---|
| R1 | User survey — students, club social-media, small-business marketers | ⬜ Not Started | Survey questions to be formulated |
| R2 | 2-3 short interviews — people who manage social media / marketing content | ⬜ Not Started | Scheduled for Round 2 user feedback |
| R3 | Collect off-brand examples — wrong logo colour, tone mismatch, etc. | 🔄 In Progress | ASCI and brand mismatch examples documented |
| R4 | Create sample brand kit — realistic guidelines, facts, terms for demo | ✅ Done | `sample-brand-kit/brand_guidelines.txt` & seeder script |
| R5 | User testing — test MVP with 3-5 users, collect feedback | ⬜ Not Started | |
| R6 | Document feedback and improvement suggestions | ⬜ Not Started | |

### Documentation Tasks (Shrushti 🟣)

| # | Task | Status | Notes |
|---|---|---|---|
| D1 | Architecture diagram — system overview, data flow | ✅ Done | Visualized in master project plan artifact |
| D2 | API documentation — endpoints, request/response schemas | ✅ Done | Built into FastAPI `/docs` (Swagger UI) |
| D3 | Setup guide — how to run the project locally | ✅ Done | Documented in `README.md` |
| D4 | Architecture notes — design decisions and trade-offs | 🔄 In Progress | Detailed in PROJECT_PLAN.md |

---

## 📅 Round 3: The Finish (Upcoming)

> **Goal:** Complete, polish, and present.

| # | Task | Owner | Status |
|---|---|---|---|
| R3-1 | Image & accessibility checks (logo, palette, alt-text, contrast) | Ajay 🟢 | ⬜ Not Started |
| R3-2 | Claim verification against approved facts list | Ajay 🟢 | 🔄 In Progress (Rule regex ready; LLM expansion next) |
| R3-3 | Guideline-gap insights — dashboard shows unclear rules | Ajay 🟢 + Mahesh 🔵 | ✅ Done (Aggregated in Dashboard API & UI) |
| R3-4 | Revision history — visual diff between versions + reviewer comments | Mahesh 🔵 | 🔄 In Progress (Comments & status history active) |
| R3-5 | AI-use disclosure UI | Mahesh 🔵 | ✅ Done (Audit log & finding badges state AI/Rule attribution) |
| R3-6 | Testing evidence — compile user feedback, test results | Asma 🟡 | ⬜ Not Started |
| R3-7 | Privacy & responsible-design explanation | Asma 🟡 | ✅ Done (Documented in Plan & Readme) |
| R3-8 | Demo video script & recording | Shrushti 🟣 | ⬜ Not Started |
| R3-9 | Final presentation | Shrushti 🟣 | ⬜ Not Started |
| R3-10 | Final report & roadmap | Shrushti 🟣 + Asma 🟡 | ⬜ Not Started |

---

## 📝 Daily Updates

### 2026-11-06

| Member | What I did | What I'll do next | Blockers |
|---|---|---|---|
| Ajay | Built complete FastAPI backend (auth, database, models, rule engine, brand kit service, review & dashboard APIs) | Connect live LLM API for advanced tone check & RAG | None |
| Mahesh | Built complete React frontend (Vite, Tailwind, AuthContext, Layout, Dashboard, BrandKits, Drafts, CreateDraft, DraftReview) | Fine-tune visual diff component and test responsive layouts | None |
| Asma | Created realistic enterprise brand guidelines & ASCI compliant test cases | Conduct initial user testing on review flow | None |
| Shrushti | Project plan, README, and seeder script for automated testing | Coordinate presentation outline & demo workflow | None |

---

## 🔗 Quick Links

| Resource | Link |
|---|---|
| GitHub Repo | https://github.com/AJJU3836/BrandGuard-AI |
| Google Drive | https://drive.google.com/drive/folders/1ybSTBQjKro8z8dBaycZW9Flvnrpbdp3r?usp=sharing |
| Team Lead Email | Kaleajay626@gmail.com |
