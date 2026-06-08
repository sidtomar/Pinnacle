# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PinnacleIQ is a multi-agent medical research pipeline for Mankind Pharma. It has two parallel systems that work together:

1. **Python backend** (`research_agent_system/`, `demo/backend/`) — LangGraph 4-agent pipeline + FastAPI server
2. **React frontend** (`react-app/`) — Vite + React 18 SPA

## Common Commands

### Python Backend (demo API server)
```powershell
# Start the FastAPI demo server (port 8010)
cd demo/backend
uvicorn app:app --reload --port 8010

# Or use the one-click launcher from project root
START_DEMO.bat
```

### Python Agent Pipeline (real LLM runs)
```powershell
cd research_agent_system
pip install -r requirements.txt

# Run pipeline for a topic
python main.py "GLP-1 receptor agonists in Type 2 Diabetes"
```

### React Frontend
```powershell
cd react-app
npm install
npm run dev        # dev server on port 5173
npm run build      # production build to dist/
npm run test       # vitest
```

### Backend API health check
```
curl http://localhost:8010/
curl http://localhost:8010/topics
# Interactive docs:
http://localhost:8010/docs
```

## Architecture

### Agent Pipeline (`research_agent_system/`)

Four agents run sequentially per topic:

| Agent | Role |
|-------|------|
| **Alpha** | ReAct agent — PubMed search + OneDrive MA library; returns list of papers |
| **Beta** | LCEL chain — summarises each paper into key findings |
| **Gamma** | LCEL chain — writes 200–500 word article, submits for MA review |
| **Delta** | LCEL chain — generates portal content card (JSON), saves to store |

`orchestrator.py` drives the full flow. Each paper from Alpha gets its own Beta → Gamma → Delta pass. Results are stored as `PipelineResult` dataclass.

**LLM factory** (`config.py`): `get_llm()` reads `LLM_PROVIDER` env var. Default is OpenRouter (OpenAI-compatible, 100+ models). Switch models by changing `OPENROUTER_MODEL` in `.env` — no code changes needed.

### Storage Abstraction (`research_agent_system/store/`)

`STORE_BACKEND` env var switches between:
- `sqlite` (default for demo) — zero setup, local file `pinnacleiq_demo.db`
- `databricks` — production, requires `DATABRICKS_HOST` + `DATABRICKS_TOKEN`

The `factory.py` returns the right store via `get_store()`. `app.py` never touches the DB directly.

### Demo Backend (`demo/backend/app.py`)

FastAPI server exposing the full REST API. Key design: `mock_runner.py` simulates realistic agent delays without real LLM calls (for demos without API keys). Real LLM calls go through `research_agent_system/`.

The backend also has a scheduler (`scheduler.py`) that runs daily doctor sync and content generation jobs via APScheduler.

### React Frontend (`react-app/`)

**Routing**: Hash-based — URL pattern is `#<role>/<page>` (e.g. `#bu-head/today`, `#medical-affairs/library`).

**Two roles** with separate permissions:
- `medical-affairs` (MA): can run pipeline, approve/reject content
- `bu-head` (PMT): can export and share approved content with doctors

**Context tree** (wraps entire app):
- `AuthContext` — login state, role, role-based permission flags (`canExport`, `canRunPipeline`, `canApproveContent`)
- `AppContext` — current page/tab, sidebar state, notifications, sort/filter state
- `ContentContext` — fetched content papers, CRUD operations

**API client** (`src/services/api.js`): Axios instance pointing to `http://localhost:8010` (configurable via `VITE_API_URL`). Vite dev server proxies `/api` → backend.

**Styling**: CSS Modules (`.module.css` per component). Global variables in `src/styles/variables.css`.

## Environment Configuration

Copy `research_agent_system/.env.example` → `research_agent_system/.env` and fill in:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=...         # required for real pipeline runs
OPENROUTER_MODEL=anthropic/claude-sonnet-4-5
TAVILY_API_KEY=...             # required for web search (Alpha agent)
STORE_BACKEND=sqlite           # sqlite | databricks

# Optional — leave blank to skip
TWILIO_ACCOUNT_SID=            # WhatsApp delivery
SENDGRID_API_KEY=              # Email delivery
DATABRICKS_HOST=               # Production data store
```

The demo backend reads the same `.env` file via `python-dotenv`.

## Key Files

| File | Purpose |
|------|---------|
| `research_agent_system/orchestrator.py` | Main pipeline runner — entry point for understanding agent flow |
| `research_agent_system/config.py` | LLM factory — how models are instantiated |
| `demo/backend/app.py` | FastAPI routes — full REST API surface |
| `demo/backend/mock_runner.py` | Simulated pipeline for demos without API keys |
| `demo/topics.txt` | Research topics list (pipe-delimited: `topic | specialty | therapy_area`) |
| `demo/doctors.json` | 100-doctor training database |
| `react-app/src/context/AuthContext.jsx` | Auth + role state, permission flags |
| `react-app/src/context/AppContext.jsx` | Navigation + UI state |
| `react-app/src/services/api.js` | Axios client, API base URL |
