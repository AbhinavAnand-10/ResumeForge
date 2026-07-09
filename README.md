# ResumeForge AI

> An AI-powered resume diagnosis and optimization platform that tells you the truth about your resume first — then rewrites it without ever fabricating a skill, title, or metric you don't already have.

🔗 **Live Demo:** https://resume-forge-five-beta.vercel.app

---

## The Problem

Most AI resume tools either hallucinate experience you don't have, or give you generic advice that doesn't match real hiring patterns. ResumeForge AI does neither.

It runs a brutally honest ATS diagnostic first. Then — only if you ask — it rewrites your resume using patterns learned from real, publicly available successful resumes for your target role, under a strict anti-fabrication guardrail enforced at the prompt level.

---

## How It Works

### Phase 1 — Diagnosis
Upload your resume (PDF or DOCX), enter a target role, and optionally paste a job description. The AI scores your resume across four dimensions and flags every flaw, fluffy phrase, and missing keyword — bluntly, not gently.

### Phase 2 — Web-Augmented Pattern Research
If you choose to optimize, the backend searches the web for publicly available resume examples for your target role. It extracts anonymized structural and linguistic patterns — never copying anyone's personal data or actual content.

### Phase 3 — Guardrailed Rewrite
The optimizer agent rewrites your resume to match those patterns. It may only rephrase, restructure, reformat, and surface implicit skills — it is explicitly forbidden from adding any skill, employer, title, metric, or credential that isn't already in your original resume. Every change must be traceable to something you already wrote.

### Phase 4 — The Reveal
A Git-style side-by-side diff shows exactly what changed and why, alongside a projected ATS score improvement.

### Phase 5 — Skill Gap Roadmap
Any keyword that mattered for the role but had no basis in your resume gets routed to a legitimate skill-gap closure plan — real projects, certifications, and resources to actually earn those skills, not fake them.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), React, Tailwind CSS, Framer Motion |
| Backend | Python, FastAPI, pdfplumber, python-docx |
| AI | Groq (Llama 3.3 70B) via OpenAI-compatible API |
| Web Search | Exa AI — neural search for resume pattern research |
| Deployment | Vercel (frontend) + Render (backend) |

---

## Project Structure
resumeforge/
├── backend/                   FastAPI application
│   ├── main.py                Entrypoint
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── api/               Route handlers (upload, diagnose, optimize, export)
│       ├── agents/            4 LLM agents + LLM client factory
│       ├── services/          PDF/DOCX parsing, web search, diff engine, export
│       ├── models/            Pydantic schemas — single source of truth
│       └── utils/             Config + session store
│
└── frontend/                  Next.js application
└── app/
├── page.tsx           Upload + input phase
├── dashboard/         Diagnosis → optimize → reveal → export
├── components/        ScoreGauge, DiffViewer, SkillGapRoadmap, etc.
└── lib/               Typed API client
---

## Running Locally

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys (see Environment Variables below)
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API explorer.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit `http://localhost:3000`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Value | Where to get it |
|----------|-------|-----------------|
| `GROQ_API_KEY` | `gsk_...` | Free at [console.groq.com](https://console.groq.com) |
| `EXA_API_KEY` | `exa-...` | Free at [exa.ai](https://exa.ai) |
| `LLM_PROVIDER` | `openai` | Leave as-is (Groq uses OpenAI-compatible API) |
| `OPENAI_MODEL` | `llama-3.3-70b-versatile` | Groq's fastest free model |
| `SEARCH_PROVIDER` | `exa` | Leave as-is |
| `ALLOWED_ORIGINS` | Your frontend URL | e.g. `http://localhost:3000` |

### Frontend (`frontend/.env.local`)

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Your backend URL, e.g. `http://localhost:8000` |

---

## The Guardrail — In One Sentence

Every agent prompt is written so the optimizer can only point to something *already in the user's original resume* to justify a change — if it can't, the instruction is to leave it out and route it to the skill-gap plan instead.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload resume file, extract text |
| `POST` | `/api/diagnose` | Run ATS diagnostic, return scores and flaws |
| `POST` | `/api/optimize` | Web search + guardrailed rewrite + diff |
| `POST` | `/api/export` | Download optimized resume as PDF or DOCX |

---

## Author

**Abhinav Anand** — [GitHub](https://github.com/AbhinavAnand-10)