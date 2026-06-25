# ResumeForge AI

An AI-driven resume diagnosis and optimization platform with a hard anti-fabrication
guardrail. It tells you the truth about your resume first, then — only if you ask —
rewrites it using patterns learned from real, publicly available successful resumes
for your target role, **without ever inventing a skill, title, employer, or metric
you don't already have.**

```
resumeforge/
├── backend/                  FastAPI application
│   ├── main.py                Entrypoint — run with `uvicorn main:app`
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── api/                Route handlers (upload, diagnose, optimize, export)
│       ├── agents/              The 4 LLM agents + LLM client factory
│       ├── services/            Parsing, web search, diff engine, file export
│       ├── models/               Pydantic schemas (single source of truth for API shapes)
│       └── utils/                Config + in-memory session store
│
└── frontend/                 Next.js (App Router) application
    ├── app/
    │   ├── page.tsx             Input phase — upload, role, JD
    │   ├── dashboard/page.tsx    Diagnosis → optimize → reveal → export flow
    │   ├── components/           ScoreGauge, UploadZone, DiffViewer, etc.
    │   └── lib/                  Typed API client
    ├── tailwind.config.js
    └── package.json
```

## How it works (the 5 phases)

1. **Input** — upload a PDF/DOCX, give a target role, optionally paste a JD.
2. **Diagnosis** — an LLM scores ATS-compatibility, flags flaws, and lists missing
   keywords. This is deliberately blunt, not flattering.
3. **The Pivot** — the UI asks if you want an AI-optimized rewrite.
4. **Web-Augmented Optimization** — the backend searches the web for patterns in
   successful resumes for the role, synthesizes anonymized structural/style patterns
   (never copying anyone's actual content), then runs a **guardrailed rewrite agent**
   that may only rephrase/restructure/reformat — never fabricate.
5. **The Reveal + Roadmap** — a side-by-side diff shows exactly what changed and why,
   plus a legitimate skill-gap closure plan for anything that couldn't honestly be
   added to the resume.

## Quickstart

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set OPENAI_API_KEY or ANTHROPIC_API_KEY, and EXA_API_KEY or SERPER_API_KEY
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive OpenAPI explorer.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit `http://localhost:3000`.

The Next.js `next.config.js` proxies `/api/*` to the FastAPI backend, so no CORS
configuration is needed in development beyond what's already in `main.py`.

## Configuration notes

- **LLM provider**: toggle `LLM_PROVIDER=openai` or `anthropic` in `backend/.env`.
  Both clients are implemented in `app/agents/llm_client.py`.
- **Search provider**: toggle `SEARCH_PROVIDER=exa` or `serper`. If neither key is
  set, or the search call fails, the synthesizer agent gracefully falls back to a
  general ATS best-practice baseline rather than failing the whole pipeline.
- **Sessions**: the included `SessionStore` is in-memory and single-process — fine
  for local dev/demo. Swap `app/utils/session_store.py` for Redis or Postgres before
  deploying with multiple workers, since in-memory state won't be shared across them.

## The guardrail, in one sentence

Every agent prompt in `app/agents/` is written so the optimizer can only point to
something *already in the user's original resume* to justify a change — if it can't,
the instruction is to leave it out and route it to the skill-gap plan instead.
