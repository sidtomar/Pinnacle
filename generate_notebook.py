"""
Generates PinnacleIQ_Research_Pipeline.ipynb — a fully annotated Google Colab notebook
covering the entire PinnacleIQ multi-agent research pipeline.

Run:  python generate_notebook.py
Output: PinnacleIQ_Research_Pipeline.ipynb  (open in Colab or Jupyter)
"""
import json

cells = []


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions to build cells
# ─────────────────────────────────────────────────────────────────────────────
def md(source: str):
    """Append a Markdown cell."""
    cells.append({"cell_type": "markdown", "metadata": {}, "source": source})


def code(source: str, tags=None):
    """Append a Code cell."""
    meta = {"tags": tags} if tags else {}
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": meta,
        "outputs": [],
        "source": source,
    })


# ═════════════════════════════════════════════════════════════════════════════
# CELL 1 — Title Banner
# ═════════════════════════════════════════════════════════════════════════════
md("""\
# 🏥 PinnacleIQ — Multi-Agent Medical Research Pipeline
### Mankind Pharma · AI-Powered Content Engine

---

This notebook is the **complete, annotated walkthrough** of the PinnacleIQ research system.
Every file in the project is reproduced here with plain-English comments so you can read it
top-to-bottom and understand exactly what each piece does and why.

| Layer | What it does |
|---|---|
| **Config** | Picks the right LLM (Claude or GPT-4o) from an env variable |
| **Tools** | Internet search (Tavily), OneDrive file reading, WhatsApp, Email |
| **Agent Alpha** | Searches the web + OneDrive → produces a research article |
| **Agent Beta** | Reads Alpha's article → extracts key findings & recommendations |
| **Agent Gamma** | Writes a short doctor-friendly article → sends via WhatsApp & email |
| **Agent Delta** | Converts everything into a structured JSON → POSTs to Pinnacle portal |
| **Orchestrator** | Chains all 4 agents Alpha → Beta → Gamma → Delta |
| **Demo System** | FastAPI backend + mock pipeline (no API keys needed) for management demos |

> **To actually run the pipeline cells** you need API keys.
> **To run the Demo / Mock cells** at the bottom — no keys needed at all.
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 2 — Architecture Diagram
# ═════════════════════════════════════════════════════════════════════════════
md("""\
## 🗺️ System Architecture

```
  ┌──────────────┐
  │  topics.txt  │  ← You edit this text file with research topics
  └──────┬───────┘
         │ topic string
         ▼
  ┌──────────────────────────────────────────────────────┐
  │                  ORCHESTRATOR                         │
  │  (orchestrator.py — chains the 4 agents in order)   │
  └──────┬────────────────────────────────────────────────┘
         │
         ▼
  ┌──────────────┐    uses    ┌──────────────────────────────┐
  │  AGENT ALPHA │ ─────────► │ Tool: internet_search (Tavily)│
  │  (Researcher)│            │ Tool: read_onedrive_files     │
  └──────┬───────┘            └──────────────────────────────┘
         │ research_article (markdown text, ~1000 words)
         ▼
  ┌──────────────┐
  │  AGENT BETA  │  ← Pure LLM chain (no tools), reads Alpha's article
  │  (Analyst)   │    produces structured insights report
  └──────┬───────┘
         │ insights (Executive Summary, Key Findings, Recommendations...)
         ▼
  ┌──────────────┐    uses    ┌──────────────────────────────┐
  │  AGENT GAMMA │ ─────────► │ Tool: send_whatsapp (Twilio) │
  │  (Writer &   │            │ Tool: send_email (SendGrid)   │
  │   Delivery)  │            └──────────────────────────────┘
  └──────┬───────┘
         │ short_article (400-word plain-text + HTML version)
         ▼
  ┌──────────────┐    uses    ┌──────────────────────────────┐
  │  AGENT DELTA │ ─────────► │ POST /api → Pinnacle Portal  │
  │  (Reporter)  │            └──────────────────────────────┘
  └──────┬───────┘
         │ JSON report (full structured output)
         ▼
  ┌──────────────────────────────────────────────────────┐
  │              PINNACLE PORTAL (FastAPI + SQLite)       │
  │  Medical Affairs reviews → approves → BU Head shares │
  └──────────────────────────────────────────────────────┘
```
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 3 — Installation
# ═════════════════════════════════════════════════════════════════════════════
md("## ⚙️ Step 0 — Install Dependencies\n\nRun this cell first. All packages the pipeline needs.")

code("""\
# ── Core LangChain / LangGraph stack ──────────────────────────────────────
# langchain-core      : base classes (prompts, parsers, tools)
# langchain-community : third-party tool integrations (Tavily, etc.)
# langchain-anthropic : Claude LLM wrapper
# langchain-openai    : OpenAI LLM wrapper
# langgraph           : the graph-based agent runtime (replaces AgentExecutor)
!pip install -q langchain-core langchain-community langchain-anthropic langchain-openai langgraph

# ── Search & document tools ───────────────────────────────────────────────
# tavily-python : Tavily web search API client
# msal          : Microsoft Authentication Library (for OneDrive via Graph API)
# PyPDF2        : extract text from PDF files
# python-docx   : extract text from Word (.docx) files
# openpyxl      : read Excel (.xlsx) files
!pip install -q tavily-python msal PyPDF2 python-docx openpyxl requests

# ── Delivery tools ────────────────────────────────────────────────────────
# twilio   : WhatsApp messaging via Twilio API
# sendgrid : email delivery via SendGrid API
!pip install -q twilio sendgrid

# ── Demo backend ──────────────────────────────────────────────────────────
# fastapi   : the REST API framework for the demo portal backend
# uvicorn   : ASGI web server that runs FastAPI
# pydantic  : data validation (FastAPI uses it for request/response models)
!pip install -q fastapi uvicorn pydantic python-dotenv

# ── Utility ───────────────────────────────────────────────────────────────
!pip install -q python-dotenv  # loads .env files into os.environ

print("✅ All packages installed!")
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 4 — API Key Setup
# ═════════════════════════════════════════════════════════════════════════════
md("""\
## 🔑 Step 1 — Configure API Keys

### Why OpenRouter?
Instead of managing separate API keys for Claude, GPT-4o, Gemini etc.,
we use **[OpenRouter](https://openrouter.ai)** — a single API key that routes to 100+ models.
Just change one env variable (`OPENROUTER_MODEL`) to switch models instantly.

In **Google Colab**, go to the 🔒 **Secrets** tab (left sidebar, key icon) and add each key.
Then run the cell below to load them.

If running **locally**, copy `.env.example` → `.env` and fill in the values.

### Required Keys

| Secret Name | Where to get it | Required? |
|---|---|---|
| `OPENROUTER_API_KEY` | https://openrouter.ai/keys | ✅ Yes (for real pipeline) |
| `TAVILY_API_KEY` | https://app.tavily.com | ✅ Yes (for web search) |

### Optional Keys (pipeline skips gracefully if missing)

| Secret Name | Purpose |
|---|---|
| `ONEDRIVE_CLIENT_ID/SECRET/TENANT_ID` | Read internal Azure/OneDrive documents |
| `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` | WhatsApp delivery |
| `SENDGRID_API_KEY` | Email delivery |

### Available Models via OpenRouter
| Model slug (set as `OPENROUTER_MODEL`) | Provider |
|---|---|
| `anthropic/claude-sonnet-4-5` ⭐ | Anthropic |
| `anthropic/claude-opus-4` | Anthropic |
| `openai/gpt-4o` | OpenAI |
| `openai/gpt-4o-mini` | OpenAI |
| `google/gemini-pro-1.5` | Google |
| `google/gemini-flash-1.5` | Google |
| `meta-llama/llama-3.1-405b-instruct` | Meta |
| `deepseek/deepseek-r1` | DeepSeek |
| `mistralai/mistral-large` | Mistral |

> 💡 **For the demo / mock sections at the bottom, NO keys are needed at all.**
""")

code("""\
import os

# ── Helper: load from Colab Secrets → env var → default ──────────────────────
def _secret(name: str, default: str = "") -> str:
    \"\"\"
    Load a secret value in priority order:
    1. Google Colab Secrets (if running in Colab)
    2. Environment variable (if running locally with .env loaded)
    3. The default value
    \"\"\"
    try:
        from google.colab import userdata
        val = userdata.get(name)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(name, default)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  CHANGE THESE TO SWITCH MODELS — no other code changes needed!  ║
# ╚══════════════════════════════════════════════════════════════════╝

# Provider: always "openrouter" (routes to any model via one API key)
os.environ["LLM_PROVIDER"]      = "openrouter"

# Your OpenRouter API key — get one free at https://openrouter.ai/keys
os.environ["OPENROUTER_API_KEY"] = _secret("OPENROUTER_API_KEY")

# Pick any model from https://openrouter.ai/models
# Just change this one line to try a different model!
os.environ["OPENROUTER_MODEL"]  = "anthropic/claude-sonnet-4-5"
# os.environ["OPENROUTER_MODEL"] = "openai/gpt-4o"
# os.environ["OPENROUTER_MODEL"] = "google/gemini-pro-1.5"
# os.environ["OPENROUTER_MODEL"] = "meta-llama/llama-3.1-70b-instruct"
# os.environ["OPENROUTER_MODEL"] = "deepseek/deepseek-r1"
# os.environ["OPENROUTER_MODEL"] = "mistralai/mistral-large"


# ── Tavily Search (required for Agent Alpha web searches) ─────────────────────
os.environ["TAVILY_API_KEY"]    = _secret("TAVILY_API_KEY")

# ── OneDrive / Microsoft Graph API (optional) ─────────────────────────────────
os.environ["ONEDRIVE_CLIENT_ID"]     = _secret("ONEDRIVE_CLIENT_ID")
os.environ["ONEDRIVE_CLIENT_SECRET"] = _secret("ONEDRIVE_CLIENT_SECRET")
os.environ["ONEDRIVE_TENANT_ID"]     = _secret("ONEDRIVE_TENANT_ID")
os.environ["ONEDRIVE_FOLDER_PATH"]   = "Research"

# ── WhatsApp via Twilio (optional) ────────────────────────────────────────────
os.environ["TWILIO_ACCOUNT_SID"]   = _secret("TWILIO_ACCOUNT_SID")
os.environ["TWILIO_AUTH_TOKEN"]    = _secret("TWILIO_AUTH_TOKEN")
os.environ["TWILIO_WHATSAPP_FROM"] = _secret("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
os.environ["WHATSAPP_RECIPIENTS"]  = "whatsapp:+91XXXXXXXXXX"  # your number

# ── Email via SendGrid (optional) ─────────────────────────────────────────────
os.environ["SENDGRID_API_KEY"]  = _secret("SENDGRID_API_KEY")
os.environ["EMAIL_FROM"]        = _secret("EMAIL_FROM", "research@mankind.com")
os.environ["EMAIL_FROM_NAME"]   = "Pinnacle Research Team"
os.environ["EMAIL_RECIPIENTS"]  = "doctor@example.com"

# ── Pinnacle Portal (optional — Delta POSTs the JSON report here) ──────────────
os.environ["PINNACLE_API_URL"] = ""
os.environ["PINNACLE_API_KEY"] = ""

# ── Status check ──────────────────────────────────────────────────────────────
model   = os.environ.get("OPENROUTER_MODEL", "not set")
or_key  = os.environ.get("OPENROUTER_API_KEY", "")
tav_key = os.environ.get("TAVILY_API_KEY", "")

print("=" * 55)
print("  PINNACLEIQ — Environment Status")
print("=" * 55)
print(f"  Provider      : {os.environ['LLM_PROVIDER'].upper()} (OpenRouter)")
print(f"  Model         : {model}")
print(f"  OpenRouter key: {'SET ✅' if or_key else 'NOT SET ⚠️  (needed for real pipeline)'}")
print(f"  Tavily key    : {'SET ✅' if tav_key else 'NOT SET ⚠️  (needed for web search)'}")
print("=" * 55)
print()
print("  To switch models, just change OPENROUTER_MODEL above")
print("  and re-run this cell. No other changes needed!")
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 5 — CONFIG MODULE
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## 📦 Part 1 — Configuration (`config.py`)

This is the **LLM factory** — the single place that decides which AI model to use.

**Why a factory?**
- Every agent calls `get_llm()` — none of them care which model is behind it
- Change `OPENROUTER_MODEL` in Step 1 to instantly swap between 100+ models
- Temperature is tuned per-agent (Alpha: 0.1 factual, Gamma: 0.3 creative writing)

**Why OpenRouter?**
- One API key works for Claude, GPT-4o, Gemini, Llama, DeepSeek, Mistral — all of them
- OpenRouter exposes an OpenAI-compatible API, so LangChain's `ChatOpenAI` class works with it
- No code changes needed to switch models — just change the model slug string
""")

code("""\
# ─── config.py ────────────────────────────────────────────────────────────────
# LLM factory — returns a chat model for the configured provider.
# Default: OpenRouter (one key → any of 100+ models).
# Legacy: direct Claude / OpenAI (kept for backward compatibility).
# ─────────────────────────────────────────────────────────────────────────────

import os
from enum import Enum
from langchain_core.language_models import BaseChatModel


class LLMProvider(str, Enum):
    OPENROUTER = "openrouter"   # ← default: single key, any model
    CLAUDE     = "claude"       # direct Anthropic API (legacy)
    OPENAI     = "openai"       # direct OpenAI API (legacy)


# ── Quick-reference model slugs for OpenRouter ────────────────────────────────
# Pass any of these as OPENROUTER_MODEL env var, or as model= arg to get_llm()
OPENROUTER_MODELS = {
    # Anthropic
    "claude-sonnet":  "anthropic/claude-sonnet-4-5",
    "claude-opus":    "anthropic/claude-opus-4",
    "claude-haiku":   "anthropic/claude-haiku-3-5",
    # OpenAI
    "gpt-4o":         "openai/gpt-4o",
    "gpt-4o-mini":    "openai/gpt-4o-mini",
    "o3-mini":        "openai/o3-mini",
    # Google
    "gemini-pro":     "google/gemini-pro-1.5",
    "gemini-flash":   "google/gemini-flash-1.5",
    # Meta
    "llama-405b":     "meta-llama/llama-3.1-405b-instruct",
    "llama-70b":      "meta-llama/llama-3.1-70b-instruct",
    # Mistral
    "mistral-large":  "mistralai/mistral-large",
    "mixtral-8x7b":   "mistralai/mixtral-8x7b-instruct",
    # DeepSeek
    "deepseek-r1":    "deepseek/deepseek-r1",
    "deepseek-v3":    "deepseek/deepseek-chat",
}


def get_llm(
    provider: LLMProvider | None = None,
    temperature: float = 0.2,
    model: str | None = None,   # optional model override (OpenRouter slug or native name)
    **kwargs,
) -> BaseChatModel:
    \"\"\"
    Return a configured chat model.

    Args:
        provider   : 'openrouter' (default) | 'claude' | 'openai'
                     Reads LLM_PROVIDER env var if None.
        temperature: 0.0 = deterministic JSON, 0.1 = factual research,
                     0.15 = analysis, 0.3 = creative writing.
        model      : Override the model name/slug. If None, reads env var.

    Returns:
        BaseChatModel — same .invoke() interface regardless of provider.
        Agents never need to know which model is behind the factory.
    \"\"\"
    if provider is None:
        provider = LLMProvider(os.getenv("LLM_PROVIDER", "openrouter").lower())

    # ── OpenRouter (recommended) ───────────────────────────────────────────────
    # OpenRouter's API is 100% OpenAI-compatible, so we just use ChatOpenAI
    # with a different base_url and api_key. No special library needed.
    if provider == LLMProvider.OPENROUTER:
        from langchain_openai import ChatOpenAI

        model_name = model or os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5")

        return ChatOpenAI(
            model=model_name,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",   # ← the only OpenRouter-specific line
            temperature=temperature,
            # Recommended headers — OpenRouter uses them for analytics and model rankings
            default_headers={
                "HTTP-Referer": "https://pinnacleiq.mankind.com",
                "X-Title": "PinnacleIQ Research Pipeline",
            },
            **kwargs,
        )

    # ── Direct Anthropic API (legacy) ──────────────────────────────────────────
    # Use this only if you specifically need Anthropic-only features (e.g. extended thinking)
    if provider == LLMProvider.CLAUDE:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=temperature,
            **kwargs,
        )

    # ── Direct OpenAI API (legacy) ─────────────────────────────────────────────
    if provider == LLMProvider.OPENAI:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature,
            **kwargs,
        )

    raise ValueError(f"Unknown LLM provider: {provider}")


# ── Quick connectivity test ───────────────────────────────────────────────────
# Uncomment to verify your OpenRouter key + model work before running the pipeline:
# llm = get_llm(temperature=0)
# response = llm.invoke("Reply with exactly: PINNACLEIQ READY")
# print(response.content)
# Expected: "PINNACLEIQ READY"
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 6 — TOOLS SECTION HEADER
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## 🔧 Part 2 — Tools

Tools are **functions that agents can call** during their reasoning loop.
In LangGraph/LangChain, a tool is just a Python function decorated with `@tool`
or wrapped in a `StructuredTool` / `TavilySearchResults` object.

The agent sees a list of tools, decides which one to call, calls it,
reads the result, and continues reasoning. This loop repeats until the agent
decides it has enough information to give a final answer.

We have 4 tools in this project:
1. `internet_search` — Tavily web search
2. `read_onedrive_files` — Microsoft Graph API to read internal documents
3. `send_whatsapp` — Twilio WhatsApp delivery (not an agent tool, called by Gamma directly)
4. `send_email` — SendGrid email delivery (same — called by Gamma directly)
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 7 — TOOL: TAVILY SEARCH
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 🔍 Tool 1 — Internet Search (`tools/search.py`)

[Tavily](https://app.tavily.com) is a search API built for AI agents.
Unlike Google, it returns **clean, pre-extracted text** (not raw HTML),
so the LLM can read results directly without needing a browser.

**Why not just use Google?**
- Google results need JS rendering and HTML parsing
- Tavily returns structured JSON with the actual article text
- `include_answer=True` gives a one-sentence summary
- `include_raw_content=True` gives the full article text
""")

code("""\
# ─── tools/search.py ─────────────────────────────────────────────────────────
# Wraps Tavily search into a LangChain tool object that agents can call.
# ─────────────────────────────────────────────────────────────────────────────

import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import BaseTool


def build_tavily_tool() -> BaseTool:
    \"\"\"
    Build and return a configured Tavily search tool.

    We use a factory function (not a module-level object) so the tool is
    created fresh each time — picks up the latest env var values.

    TavilySearchResults parameters:
      max_results        : how many web pages to fetch per query (5 is a good balance)
      include_answer     : Tavily's own AI summary of the results (useful quick overview)
      include_raw_content: full text of each result page (more tokens but richer info)
      name               : what the agent sees when deciding which tool to use
      description        : how the agent knows WHEN to use this tool (very important!)
    \"\"\"
    max_results = int(os.getenv("TAVILY_MAX_RESULTS", "5"))

    return TavilySearchResults(
        max_results=max_results,
        include_answer=True,
        include_raw_content=True,
        name="internet_search",
        description=(
            "Search the internet for recent information on a topic. "
            "Input: a search query string. "
            "Output: list of results with title, url, and content."
        ),
    )


# ── How it works in practice ─────────────────────────────────────────────────
# Agent Alpha calls this tool 3+ times with different search angles, e.g.:
#   - "GLP-1 receptor agonists 2025 clinical trials"
#   - "semaglutide Indian population HbA1c reduction"
#   - "GLP-1 agonists cardiovascular outcomes latest meta-analysis"
#
# Each call returns a list of dicts like:
# [
#   {"url": "https://...", "title": "...", "content": "...", "answer": "..."},
#   ...
# ]
# The agent accumulates these results and uses them in its final article.

# ── Quick test (needs TAVILY_API_KEY) ─────────────────────────────────────────
# tool = build_tavily_tool()
# results = tool.invoke("GLP-1 receptor agonists 2025")
# for r in results:
#     print(r['title'], "\\n", r['content'][:200], "\\n---")
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 8 — TOOL: ONEDRIVE
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 📁 Tool 2 — OneDrive File Reader (`tools/onedrive.py`)

This tool lets agents read **internal research documents** stored in Microsoft OneDrive.
It uses the **Microsoft Graph API** with app-only authentication (no user login needed).

**Flow:**
1. Use MSAL to get an access token (client credentials — app ID + secret)
2. Call the Graph API to list files in the configured folder
3. Filter files whose names match the search query
4. Download each file and extract its text (supports .txt, .pdf, .docx, .xlsx)
5. Return concatenated text to the agent

**Azure setup needed:**
- Register an app in Azure Active Directory
- Grant it `Files.Read.All` permission (application type, not delegated)
- Copy the Client ID, Client Secret, and Tenant ID into your `.env`
""")

code("""\
# ─── tools/onedrive.py ───────────────────────────────────────────────────────
# Reads files from OneDrive using Microsoft Graph API.
# Supports: .txt, .pdf, .docx, .xlsx
# Auth: Client-credentials (app-only — no user login popup).
# ─────────────────────────────────────────────────────────────────────────────

import io
import os
from typing import Any

import msal          # Microsoft Authentication Library
import requests
from langchain_core.tools import tool   # decorator that turns a function into a LangChain tool

# Microsoft Graph API base URL — all Graph calls start with this
_GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def _get_access_token() -> str:
    \"\"\"
    Authenticate with Azure AD using client credentials flow and get an access token.

    Client credentials = app logs in using its own ID+Secret (no user needed).
    This is the right choice for server-side/automated processes.
    \"\"\"
    app = msal.ConfidentialClientApplication(
        client_id=os.environ["ONEDRIVE_CLIENT_ID"],
        client_credential=os.environ["ONEDRIVE_CLIENT_SECRET"],
        # authority URL format: https://login.microsoftonline.com/<tenant-id>
        authority=f"https://login.microsoftonline.com/{os.environ['ONEDRIVE_TENANT_ID']}",
    )

    # Request a token for the Graph API scope
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in result:
        raise RuntimeError(f"MSAL auth failed: {result.get('error_description')}")

    return result["access_token"]


def _graph_get(path: str, token: str, stream: bool = False) -> Any:
    \"\"\"
    Make an authenticated GET request to the Microsoft Graph API.

    path   : URL path after the base, e.g. '/me/drive/root/children'
    token  : Bearer access token from _get_access_token()
    stream : If True, return the raw response object (for file downloads).
             If False, return the parsed JSON response.
    \"\"\"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{_GRAPH_BASE}{path}", headers=headers, stream=stream, timeout=30)
    r.raise_for_status()    # raise an exception for 4xx/5xx HTTP errors
    return r if stream else r.json()


def _extract_text(content: bytes, filename: str) -> str:
    \"\"\"
    Extract plain text from a file's raw bytes.
    Supports: .txt, .pdf, .docx, .xlsx
    Falls back to an error message for unsupported types.
    \"\"\"
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        # Plain text — just decode bytes to string
        return content.decode("utf-8", errors="replace")

    if ext == ".pdf":
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        # Join text from all pages (some pages may return None, so 'or ""')
        return "\\n".join(p.extract_text() or "" for p in reader.pages)

    if ext == ".docx":
        from docx import Document
        doc = Document(io.BytesIO(content))
        # Each paragraph in the .docx becomes a line
        return "\\n".join(p.text for p in doc.paragraphs)

    if ext == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        lines = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                # Convert each cell to string, join with tab, collect all rows
                lines.append("\\t".join(str(c) if c is not None else "" for c in row))
        return "\\n".join(lines)

    return f"[Unsupported file type: {ext}]"


# The @tool decorator converts this function into a LangChain StructuredTool.
# The docstring becomes the tool's description — the agent reads it to decide
# when and how to call this tool. Write clear docstrings!
@tool
def read_onedrive_files(query: str) -> str:
    \"\"\"
    Search OneDrive for files matching the query in the configured folder and
    return their text content.

    Input: a topic or keyword to match against file names.
    Output: concatenated text content of all matched files.
    \"\"\"
    # Which OneDrive folder to search (configured in .env)
    folder_path = os.getenv("ONEDRIVE_FOLDER_PATH", "Research")

    # Authenticate and get access token
    token = _get_access_token()

    # List all files in the configured folder
    # Graph API path to list children of a folder: /me/drive/root:/<path>:/children
    search_url = f"/me/drive/root:/{folder_path}:/children"
    try:
        items = _graph_get(search_url, token)
    except requests.HTTPError:
        # If the folder doesn't exist, fall back to the root drive
        items = _graph_get("/me/drive/root/children", token)

    # Filter: only files (not folders) whose names contain the query keyword
    files = [
        i for i in items.get("value", [])
        if i.get("file") and query.lower() in i["name"].lower()
    ]

    if not files:
        return f"No files found in OneDrive folder '{folder_path}' matching '{query}'."

    results = []
    for f in files[:5]:        # cap at 5 files to avoid overwhelming the LLM context
        # @microsoft.graph.downloadUrl is a direct download link (no auth needed)
        dl_url = f["@microsoft.graph.downloadUrl"]
        r = requests.get(dl_url, timeout=60)
        r.raise_for_status()

        # Extract text and truncate to 4000 chars per file to stay within LLM limits
        text = _extract_text(r.content, f["name"])
        results.append(f"=== {f['name']} ===\\n{text[:4000]}")

    return "\\n\\n".join(results)
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 9 — TOOL: WHATSAPP
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 📱 Tool 3 — WhatsApp Delivery (`tools/whatsapp.py`)

Sends messages via **Twilio's WhatsApp Business API**.

**Twilio setup:**
1. Create a Twilio account → get Account SID + Auth Token
2. Enable the WhatsApp Sandbox (for testing) or apply for a WhatsApp Business number
3. Add `TWILIO_WHATSAPP_FROM = whatsapp:+14155238886` (sandbox number) to your `.env`
4. Recipients must first send a "join <code>" message to the sandbox number

**Production note:** For real doctor delivery, you'd use an approved WhatsApp Business number
and templates (required by Meta for first messages to users).
""")

code("""\
# ─── tools/whatsapp.py ───────────────────────────────────────────────────────
# Sends WhatsApp messages via Twilio's WhatsApp API.
# ─────────────────────────────────────────────────────────────────────────────

import os
from twilio.rest import Client    # Twilio's Python SDK


def send_whatsapp(message: str, recipients: list[str] | None = None) -> dict:
    \"\"\"
    Send a WhatsApp message to one or more recipients via Twilio.

    Args:
        message   : The text to send. Can use *bold* and _italic_ in WA format.
        recipients: List of 'whatsapp:+<country_code><number>' strings.
                    If None, reads comma-separated numbers from WHATSAPP_RECIPIENTS env var.

    Returns:
        dict mapping each recipient to their delivery status or error.
        e.g. {'whatsapp:+919999999999': {'sid': 'SM...', 'status': 'queued'}}
    \"\"\"
    # Initialize Twilio client with credentials from environment
    client = Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"],
    )
    from_number = os.environ["TWILIO_WHATSAPP_FROM"]  # your Twilio WA number

    # Parse recipients from env var if not passed directly
    if recipients is None:
        raw = os.getenv("WHATSAPP_RECIPIENTS", "")
        # Split by comma, strip whitespace, filter empty strings
        recipients = [r.strip() for r in raw.split(",") if r.strip()]

    if not recipients:
        return {"error": "No WhatsApp recipients configured."}

    results = {}
    for to in recipients:
        try:
            # Twilio creates a message and returns a Message object
            msg = client.messages.create(
                body=message,
                from_=from_number,
                to=to,           # must be 'whatsapp:+<number>'
            )
            # sid = unique message ID, status = 'queued'/'sent'/'delivered'
            results[to] = {"sid": msg.sid, "status": msg.status}
        except Exception as exc:
            results[to] = {"error": str(exc)}

    return results
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 10 — TOOL: EMAIL
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 📧 Tool 4 — Email Delivery (`tools/email_tool.py`)

Sends HTML emails via **SendGrid**.

**SendGrid setup:**
1. Create a SendGrid account → create an API key with "Mail Send" permission
2. Verify your sender email address (required by SendGrid)
3. Add `SENDGRID_API_KEY` and `EMAIL_FROM` to your `.env`
""")

code("""\
# ─── tools/email_tool.py ─────────────────────────────────────────────────────
# Sends HTML emails via SendGrid's Web API.
# ─────────────────────────────────────────────────────────────────────────────

import os
import sendgrid
from sendgrid.helpers.mail import Mail, To    # SendGrid's helper classes


def send_email(subject: str, body_html: str, recipients: list[str] | None = None) -> dict:
    \"\"\"
    Send an HTML email via SendGrid.

    Args:
        subject   : Email subject line.
        body_html : HTML content for the email body. Agent Gamma generates this
                    by converting its plain-text article to HTML using the LLM.
        recipients: List of email addresses. If None, reads from EMAIL_RECIPIENTS env var.

    Returns:
        dict with HTTP status code and response body, or {'error': ...} on failure.
        HTTP 202 = accepted for delivery (SendGrid's success code).
    \"\"\"
    # Parse recipients from env var if not passed directly
    if recipients is None:
        raw = os.getenv("EMAIL_RECIPIENTS", "")
        recipients = [r.strip() for r in raw.split(",") if r.strip()]

    if not recipients:
        return {"error": "No email recipients configured."}

    # Initialize SendGrid client with API key
    sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])

    # Build the email message object
    message = Mail(
        # from_email can be a tuple of (email, display_name)
        from_email=(os.environ["EMAIL_FROM"], os.getenv("EMAIL_FROM_NAME", "Research Bot")),
        # To() objects for each recipient
        to_emails=[To(r) for r in recipients],
        subject=subject,
        html_content=body_html,
    )

    try:
        response = sg.send(message)
        return {
            "status_code": response.status_code,  # 202 = queued for delivery
            "body": response.body,
        }
    except Exception as exc:
        return {"error": str(exc)}
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 11 — AGENTS SECTION HEADER
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## 🤖 Part 3 — The 4 Agents

Each agent is a Python function that takes text input and returns text output.
They are completely independent — the orchestrator is the only thing that knows
about all 4 of them and how to chain them.

**Two types of agents in this project:**

| Type | How it works | Used by |
|---|---|---|
| **ReAct Agent** (LangGraph) | LLM + Tools → thinks → acts → observes → repeats | Alpha |
| **LCEL Chain** (LangChain) | Prompt → LLM → Parser (one shot, no tools) | Beta, Gamma, Delta |

**Why the difference?**
- Alpha needs to *search the internet* and *read files* — it needs a reasoning loop
- Beta/Gamma/Delta just need to transform text — a simple chain is faster and cheaper
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 12 — AGENT ALPHA
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 🔬 Agent Alpha — Research Agent (`agents/alpha.py`)

Alpha is a **ReAct (Reasoning + Acting) agent** built with LangGraph.

**What is ReAct?**
The agent alternates between:
- **Reasoning** (thinking about what to do next)
- **Acting** (calling a tool)
- **Observing** (reading the tool result)

This loop continues until the agent decides it has enough information.

**LangGraph note (important for LangChain 1.x):**
The old `AgentExecutor` was removed in LangChain 1.x.
We now use `langgraph.prebuilt.create_react_agent` — same concept, new API.

```
Input: topic string
  ↓
Agent thinks: "I should search for recent clinical trials first"
  ↓ calls internet_search("GLP-1 RCTs 2025")
  ↓ reads 5 web pages
Agent thinks: "Now search for Indian population data"
  ↓ calls internet_search("GLP-1 Indian T2DM cohort")
  ↓ reads 5 more web pages
Agent thinks: "Check internal documents"
  ↓ calls read_onedrive_files("GLP-1")
  ↓ reads matching files from OneDrive
Agent thinks: "I have enough. Writing the research article now."
  ↓
Output: structured markdown research article (~1000 words)
```
""")

code("""\
# ─── agents/alpha.py ─────────────────────────────────────────────────────────
# Agent Alpha: searches internet + OneDrive, produces research article.
# Uses LangGraph's create_react_agent (LangChain 1.x compatible).
# ─────────────────────────────────────────────────────────────────────────────

from langgraph.prebuilt import create_react_agent
# NOTE: In LangChain 1.x, DO NOT use:
#   from langchain.agents import create_react_agent, AgentExecutor  ← REMOVED
# Always use the LangGraph version above.

# We import from our own modules (defined in previous cells)
# from config import get_llm
# from tools import build_tavily_tool, read_onedrive_files

# ── System Prompt ─────────────────────────────────────────────────────────────
# This is the instruction set that defines Alpha's personality and task.
# It's passed as the 'prompt' parameter to create_react_agent.
# The agent follows these instructions throughout its reasoning loop.

_ALPHA_SYSTEM_PROMPT = \"\"\"\\
You are Agent Alpha, a meticulous medical research assistant for Mankind Pharma.

Your job is to gather comprehensive information on the given topic from two sources:

1. The internet — use the internet_search tool.
   Run AT LEAST 3 searches with different angles:
   - Latest news / recent developments
   - Clinical studies / RCTs / meta-analyses
   - Expert opinions / guidelines
   - Indian population data (very important for Mankind's market)

2. Internal documents — use the read_onedrive_files tool to find relevant
   internal papers or research stored in OneDrive.

After gathering all information, produce a single consolidated research article
in this EXACT format:

## Topic: <topic>

## Internet Findings
<summarised findings from each web search — cite URLs where possible>

## Internal Document Findings
<content from matching OneDrive files, or "No internal documents found" if none>

## Consolidated Research Article
<a comprehensive, readable article (500-800 words) merging all sources,
 with inline source citations, written for a medical professional audience>

Be thorough, accurate, and clinically focused.
\"\"\"


def run_alpha(topic: str) -> str:
    \"\"\"
    Run Agent Alpha for the given research topic.

    Args:
        topic: The medical topic to research (e.g. "GLP-1 receptor agonists in T2DM")

    Returns:
        A formatted markdown string containing the research article.
        This becomes the input to Agent Beta.
    \"\"\"
    # Get the LLM — low temperature for factual research
    llm = get_llm(temperature=0.1)

    # Build the tools list: internet search + OneDrive reader
    tools = [build_tavily_tool(), read_onedrive_files]

    # create_react_agent builds a LangGraph graph under the hood.
    # It creates a loop: LLM decides action → tool executes → result back to LLM → repeat
    # 'prompt' sets the system message for the agent's LLM calls
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=_ALPHA_SYSTEM_PROMPT,
    )

    # Invoke the agent with the user's research request.
    # 'messages' is a list of (role, content) tuples.
    # The agent loop runs until the LLM produces a final message without a tool call.
    result = agent.invoke({
        "messages": [("human", f"Research this topic thoroughly: {topic}")]
    })

    # result["messages"] is a list of all messages in the conversation:
    # [HumanMessage, AIMessage (with tool_calls), ToolMessage, AIMessage, ...]
    # The LAST message is always the agent's final answer (no tool calls)
    return result["messages"][-1].content
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 13 — AGENT BETA
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 📊 Agent Beta — Insights Analyst (`agents/beta.py`)

Beta is a simple **LCEL (LangChain Expression Language) chain** — no tools, no loop.

**LCEL chain pattern:**
```python
chain = prompt | llm | output_parser
result = chain.invoke({"variable": "value"})
```
The `|` (pipe) operator connects components — output of each feeds into the next.

Beta takes Alpha's long research article and condenses it into a **structured insights report**
with consistent sections that Delta will later convert to JSON.
""")

code("""\
# ─── agents/beta.py ──────────────────────────────────────────────────────────
# Agent Beta: reads Alpha's research article, produces structured insights.
# Pure LCEL chain — no tools, no agent loop, just prompt → LLM → text.
# ─────────────────────────────────────────────────────────────────────────────

from langchain_core.output_parsers import StrOutputParser    # converts LLM response to plain string
from langchain_core.prompts import ChatPromptTemplate        # builds structured prompts

# from config import get_llm


# ── Prompt Template ───────────────────────────────────────────────────────────
# ChatPromptTemplate takes a list of (role, template) tuples.
# "system" sets the agent's persona and rules.
# "human" is the actual user message — {research_article} is the placeholder
# that gets filled in when we call chain.invoke().

_BETA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", \"\"\"
You are Agent Beta, an expert medical research analyst for Mankind Pharma.
You receive a raw research article compiled by Agent Alpha and produce
a structured insight report for medical professionals.

Your output MUST follow this EXACT structure (do not skip any section):

---
## EXECUTIVE SUMMARY
<2-3 sentence high-level summary for a busy doctor>

## KEY FINDINGS
- <Finding 1 — specific, with numbers/percentages where available>
- <Finding 2>
- <Finding 3>
- <add more bullet points as needed>

## CLINICAL INSIGHTS
<Practical, actionable takeaways for clinical practice>

## EMERGING TRENDS
<What's new or changing in this area — pipeline drugs, new guidelines, etc.>

## RECOMMENDATIONS
- <Actionable recommendation 1>
- <Actionable recommendation 2>
- <add more as needed>

## EVIDENCE QUALITY
<Brief note on the strength and recency of the evidence (RCTs? cohort? guidelines?)>
---

Be precise, evidence-based, and clinically relevant. Avoid speculation.
\"\"\"),
    # {research_article} is the placeholder — filled in at invoke() time
    ("human", "Research Article:\\n\\n{research_article}"),
])


def run_beta(research_article: str) -> str:
    \"\"\"
    Run Agent Beta on Alpha's research article.

    Args:
        research_article: The full markdown research article from run_alpha().

    Returns:
        Structured insights text (the 6-section format above).
        This becomes the input to both Agent Gamma and Agent Delta.
    \"\"\"
    llm = get_llm(temperature=0.15)   # slightly creative for better prose, but still factual

    # Build the LCEL chain: prompt → LLM → string parser
    # StrOutputParser just extracts the .content string from the LLM's AIMessage object
    chain = _BETA_PROMPT | llm | StrOutputParser()

    # invoke() fills in {research_article} in the prompt template and runs the chain
    return chain.invoke({"research_article": research_article})
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 14 — AGENT GAMMA
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### ✍️ Agent Gamma — Writer & Delivery Agent (`agents/gamma.py`)

Gamma does **three things in sequence:**
1. Takes Beta's insights → writes a short (400-word) doctor-friendly article
2. Converts the article to HTML for email
3. Sends via WhatsApp (Twilio) and email (SendGrid)

**Why two different LLM calls?**
Writing the article and converting it to HTML are different tasks with different requirements.
Separating them gives better quality than asking the LLM to do both at once.

**Temperature 0.3** — higher than Alpha/Beta because good writing needs some creativity and flow.
""")

code("""\
# ─── agents/gamma.py ─────────────────────────────────────────────────────────
# Agent Gamma: writes a short article from Beta's insights, delivers via WA + email.
# Uses two LCEL chains in sequence (write article → convert to HTML).
# ─────────────────────────────────────────────────────────────────────────────

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# from config import get_llm
# from tools.whatsapp import send_whatsapp
# from tools.email_tool import send_email


# ── Prompt 1: Write the Doctor Article ────────────────────────────────────────
_ARTICLE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", \"\"\"
You are Agent Gamma, a medical communications specialist for Mankind Pharma.
You write short, clear, impactful articles for doctors — busy professionals who
need the most important information fast.

Writing Guidelines:
- Maximum 400 words
- Use plain language (avoid jargon unless clinically necessary)
- Structure: Hook → Key Finding → Why it Matters → What To Do
- End with a clear one-line action item
- Tone: professional, collegial, direct — like a trusted colleague sharing news

IMPORTANT FORMAT RULES (for WhatsApp delivery):
- No markdown bold/italics (no **, no __)
- Use CAPITALS for emphasis instead
- Keep paragraphs short (2-3 sentences max)
- The article will be copy-pasted directly into WhatsApp
\"\"\"),
    # Both {insights} and {topic} are injected at invoke() time
    ("human", "Insights Report:\\n\\n{insights}\\n\\nTopic: {topic}"),
])


# ── Prompt 2: Convert Article to HTML Email ────────────────────────────────────
_EMAIL_HTML_PROMPT = ChatPromptTemplate.from_messages([
    ("system", \"\"\"
Convert the plain-text article into a clean HTML email body.

Rules:
- Use <h2> for the main title
- Use <p> for paragraphs
- Use <ul>/<li> for any list items
- Use <strong> for emphasis (replaces CAPITALS from the plain-text version)
- Add professional sign-off: "Pinnacle Research Team, Mankind Pharma"
- Keep it mobile-friendly — no complex tables or layouts
- Return ONLY the HTML body content.
  Do NOT include <html>, <head>, or <body> wrapper tags.
  (These will be added by SendGrid's template wrapper.)
\"\"\"),
    ("human", "{article}"),   # the plain-text article from the first chain
])


def run_gamma(topic: str, insights: str) -> dict:
    \"\"\"
    Run Agent Gamma: write article and deliver via WhatsApp + email.

    Args:
        topic   : The research topic (used for WhatsApp/email subject line).
        insights: Beta's structured insights text.

    Returns:
        dict with keys:
          'article'         : plain-text article (str)
          'html_body'       : HTML version for email (str)
          'whatsapp_status' : delivery status dict from Twilio
          'email_status'    : delivery status dict from SendGrid
    \"\"\"
    llm = get_llm(temperature=0.3)   # higher temperature = more natural writing

    # ── Step 1: Write the plain-text article ─────────────────────────────────
    article_chain = _ARTICLE_PROMPT | llm | StrOutputParser()
    article = article_chain.invoke({"insights": insights, "topic": topic})

    # ── Step 2: Convert to HTML for email ─────────────────────────────────────
    html_chain = _EMAIL_HTML_PROMPT | llm | StrOutputParser()
    html_body = html_chain.invoke({"article": article})

    # ── Step 3: Deliver ───────────────────────────────────────────────────────
    subject = f"Research Update: {topic}"

    # WhatsApp: prepend bold subject header using WA markdown (*text*)
    whatsapp_status = send_whatsapp(f"*{subject}*\\n\\n{article}")

    # Email: send the HTML version
    email_status = send_email(subject=subject, body_html=html_body)

    return {
        "article": article,
        "html_body": html_body,
        "whatsapp_status": whatsapp_status,
        "email_status": email_status,
    }
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 15 — AGENT DELTA
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 🗂️ Agent Delta — JSON Report Generator (`agents/delta.py`)

Delta is the **final agent** — it takes all outputs from the pipeline and produces
a structured JSON report that the Pinnacle portal can store and display.

**Key design decisions:**
- Uses `JsonOutputParser` which tells the LLM to output valid JSON and parses it automatically
- **Temperature = 0.0** — must produce exact JSON, zero creativity allowed
- Adds metadata (report_id, timestamps, pipeline version) that the LLM doesn't generate
- Optionally POSTs the report to the Pinnacle portal API if `PINNACLE_API_URL` is configured
""")

code("""\
# ─── agents/delta.py ─────────────────────────────────────────────────────────
# Agent Delta: converts all pipeline outputs into a structured JSON report.
# Posts the report to the Pinnacle portal API if configured.
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import uuid
from datetime import datetime, timezone

import requests
from langchain_core.output_parsers import JsonOutputParser   # parses LLM output as JSON
from langchain_core.prompts import ChatPromptTemplate

# from config import get_llm


# ── Prompt: Extract Structured Data ──────────────────────────────────────────
# Note the {{ }} double braces — in Python format strings, {{ }} means a literal { }
# We need literal { } in the JSON schema example inside the prompt.

_DELTA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", \"\"\"
You are Agent Delta. Your job is to extract structured data from research documents
and return a single valid JSON object.

The JSON MUST match EXACTLY this schema:

{{
  "summary": "string — one paragraph executive summary (2-3 sentences)",
  "key_findings": ["string", "string", ...],
  "clinical_insights": ["string", "string", ...],
  "recommendations": ["string", "string", ...],
  "emerging_trends": ["string", "string", ...],
  "evidence_quality": "string — describe strength and recency of evidence",
  "sources_used": ["string description of each source", ...]
}}

CRITICAL RULES:
- Return ONLY the raw JSON object. Nothing else.
- No markdown code fences (no ```json)
- No explanatory text before or after the JSON
- All arrays must have at least 3 items
- This JSON will be parsed programmatically — any non-JSON output will cause an error
\"\"\"),
    ("human", \"\"\"
Topic: {topic}

Insights Report (from Agent Beta):
{insights}

Short Article (from Agent Gamma):
{article}
\"\"\"),
])


def run_delta(
    topic: str,
    research_article: str,    # Alpha's full research (stored in report for reference)
    insights: str,            # Beta's structured insights (main input for extraction)
    article: str,             # Gamma's short article
    llm_provider: str = "claude",
) -> dict:
    \"\"\"
    Run Agent Delta: produce a structured JSON report and optionally POST to portal.

    Returns:
        A complete report dict ready for the Pinnacle portal.
    \"\"\"
    llm = get_llm(temperature=0.0)   # MUST be 0 — we need deterministic JSON output

    # JsonOutputParser automatically:
    # 1. Adds instructions to the prompt to output valid JSON
    # 2. Parses the LLM's string response into a Python dict/list
    chain = _DELTA_PROMPT | llm | JsonOutputParser()

    # Get the extracted structured data from the LLM
    extracted = chain.invoke({
        "topic": topic,
        "insights": insights,
        "article": article,
    })

    # Build the full report by combining LLM-extracted data with metadata
    # we generate ourselves (IDs, timestamps, version info)
    report = {
        "report_id":    str(uuid.uuid4()),      # unique ID for this report
        "generated_at": datetime.now(timezone.utc).isoformat(),  # ISO 8601 timestamp

        # Core content (LLM-extracted)
        "topic":              topic,
        "summary":            extracted.get("summary", ""),
        "key_findings":       extracted.get("key_findings", []),
        "clinical_insights":  extracted.get("clinical_insights", []),
        "recommendations":    extracted.get("recommendations", []),
        "emerging_trends":    extracted.get("emerging_trends", []),
        "evidence_quality":   extracted.get("evidence_quality", ""),
        "sources_used":       extracted.get("sources_used", []),

        # Full outputs from previous agents (for audit trail)
        "short_article":         article,
        "full_research_article": research_article,

        # Pipeline metadata
        "metadata": {
            "agent_version": "1.0.0",
            "llm_provider":  llm_provider,
            "pipeline":      "Alpha→Beta→Gamma→Delta",
        },
    }

    # Post to portal if configured (optional)
    _post_to_portal(report)
    return report


def _post_to_portal(report: dict) -> None:
    \"\"\"
    POST the report JSON to the Pinnacle portal API.
    If PINNACLE_API_URL is not set, this is a no-op (silently skipped).
    \"\"\"
    url = os.getenv("PINNACLE_API_URL")
    api_key = os.getenv("PINNACLE_API_KEY")

    if not url:
        # Portal URL not configured — skip silently
        return

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        r = requests.post(url, json=report, headers=headers, timeout=30)
        r.raise_for_status()
        print(f"[Delta] Report posted to Pinnacle portal. Status: {r.status_code}")
    except Exception as exc:
        # Non-fatal — log the warning but don't crash the pipeline
        print(f"[Delta] Warning — could not post to Pinnacle portal: {exc}")
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 16 — ORCHESTRATOR
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## 🎯 Part 4 — Pipeline Orchestrator (`orchestrator.py`)

The orchestrator is the **conductor** of the 4-agent pipeline.
It doesn't do any AI work itself — it just calls each agent in order,
passes outputs downstream, handles errors gracefully, and saves results to disk.

**Key design principle: fail gracefully**
If Alpha fails → stop immediately (nothing to pass downstream)
If Gamma fails (WhatsApp/email) → still run Delta (portal is more important than delivery)
If Delta fails → at least we have the article from Gamma
""")

code("""\
# ─── orchestrator.py ─────────────────────────────────────────────────────────
# Chains Alpha → Beta → Gamma → Delta in sequence.
# Handles errors at each stage and saves outputs to ./outputs/
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime

# Import the 4 agent runner functions
# from agents import run_alpha, run_beta, run_gamma, run_delta


# ── Result Container ──────────────────────────────────────────────────────────
# dataclass is like a simple struct — auto-generates __init__, __repr__ etc.
# field(default_factory=...) is needed for mutable defaults (lists, dicts)
@dataclass
class PipelineResult:
    \"\"\"Holds all outputs and status from a complete pipeline run.\"\"\"
    topic:            str
    research_article: str   = ""    # Alpha's output
    insights:         str   = ""    # Beta's output
    article:          str   = ""    # Gamma's output
    report:           dict  = field(default_factory=dict)   # Delta's output
    whatsapp_status:  dict  = field(default_factory=dict)   # Twilio status
    email_status:     dict  = field(default_factory=dict)   # SendGrid status
    duration_seconds: float = 0.0   # total pipeline runtime
    errors:           list  = field(default_factory=list)   # any errors that occurred


def run_pipeline(topic: str, save_outputs: bool = True) -> PipelineResult:
    \"\"\"
    Execute the full 4-agent research pipeline for the given topic.

    Args:
        topic       : The research topic (e.g. "GLP-1 receptor agonists in T2DM")
        save_outputs: If True, save each agent's output as a file in ./outputs/
                      Useful for debugging and auditing.

    Returns:
        PipelineResult containing all agent outputs and delivery status.
    \"\"\"
    start = time.time()
    result = PipelineResult(topic=topic)
    provider = os.getenv("LLM_PROVIDER", "claude")

    # Pretty header for console output
    print(f"\\n{'='*60}")
    print(f"  PINNACLE RESEARCH PIPELINE")
    print(f"  Topic : {topic}")
    print(f"  LLM   : {provider.upper()}")
    print(f"  Start : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\\n")

    # ── Agent 1: Alpha (Research) ─────────────────────────────────────────────
    print("[1/4] Agent Alpha — Researching...")
    try:
        result.research_article = run_alpha(topic)
        print("[1/4] Alpha complete.\\n")
        _save(result.research_article, "alpha_research.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Alpha: {exc}")
        print(f"[1/4] Alpha ERROR: {exc}\\n")
        result.duration_seconds = time.time() - start
        return result   # Alpha failing is fatal — nothing to pass to Beta

    # ── Agent 2: Beta (Insights) ──────────────────────────────────────────────
    print("[2/4] Agent Beta — Generating insights...")
    try:
        result.insights = run_beta(result.research_article)
        print("[2/4] Beta complete.\\n")
        _save(result.insights, "beta_insights.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Beta: {exc}")
        print(f"[2/4] Beta ERROR: {exc}\\n")
        result.duration_seconds = time.time() - start
        return result   # Beta failing is also fatal — no insights for Gamma/Delta

    # ── Agent 3: Gamma (Writing & Delivery) ───────────────────────────────────
    print("[3/4] Agent Gamma — Writing article and delivering...")
    try:
        gamma_out = run_gamma(topic=topic, insights=result.insights)
        result.article          = gamma_out["article"]
        result.whatsapp_status  = gamma_out["whatsapp_status"]
        result.email_status     = gamma_out["email_status"]
        print("[3/4] Gamma complete.\\n")
        _save(result.article, "gamma_article.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Gamma: {exc}")
        print(f"[3/4] Gamma ERROR: {exc}\\n")
        # NOT returning here — Gamma failure doesn't block Delta
        # Delta can still generate the JSON report even without the article

    # ── Agent 4: Delta (JSON Report) ──────────────────────────────────────────
    print("[4/4] Agent Delta — Generating JSON report...")
    try:
        result.report = run_delta(
            topic=topic,
            research_article=result.research_article,
            insights=result.insights,
            article=result.article,    # may be empty if Gamma failed
            llm_provider=provider,
        )
        print("[4/4] Delta complete.\\n")
        _save(json.dumps(result.report, indent=2), "delta_report.json", save_outputs)
    except Exception as exc:
        result.errors.append(f"Delta: {exc}")
        print(f"[4/4] Delta ERROR: {exc}\\n")

    result.duration_seconds = round(time.time() - start, 1)

    # ── Final Summary ─────────────────────────────────────────────────────────
    print(f"{'='*60}")
    print(f"  Pipeline complete in {result.duration_seconds}s")
    if result.errors:
        print(f"  Errors: {result.errors}")
    print(f"{'='*60}\\n")

    return result


def _save(content: str, filename: str, enabled: bool) -> None:
    \"\"\"Save content to ./outputs/<filename>. No-op if enabled=False.\"\"\"
    if not enabled:
        return
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    Saved → {path}")
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 17 — MAIN.PY (CLI)
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## 💻 Part 5 — Command-Line Interface (`main.py`)

The CLI entry point wraps `run_pipeline()` with argument parsing.
You run this from a terminal: `python main.py "GLP-1 receptor agonists"`
""")

code("""\
# ─── main.py ─────────────────────────────────────────────────────────────────
# CLI entry point. Parses arguments and calls the orchestrator.
#
# Usage examples:
#   python main.py "GLP-1 receptor agonists in Type 2 Diabetes"
#   python main.py --topic "SGLT2 inhibitors heart failure" --provider openai
#   python main.py "PCOS inositol" --no-save
# ─────────────────────────────────────────────────────────────────────────────

import argparse
import json
import sys

# from orchestrator import run_pipeline


def main():
    # argparse builds a --help menu and validates arguments automatically
    parser = argparse.ArgumentParser(
        description="Pinnacle Research Agent System — 4-agent LangChain pipeline"
    )

    # The research topic can be provided as a positional arg or --topic flag
    # e.g. both of these work:
    #   python main.py "GLP-1 agents"
    #   python main.py --topic "GLP-1 agents"
    parser.add_argument("topic", nargs="?", help="Research topic (positional)")
    parser.add_argument("--topic", "-t", dest="topic_flag", help="Research topic (flag)")

    # Override the LLM_PROVIDER env var from the command line
    parser.add_argument(
        "--provider", "-p",
        choices=["claude", "openai"],
        help="LLM provider (default: from .env LLM_PROVIDER setting)",
    )

    # Skip saving output files (useful for quick tests)
    parser.add_argument(
        "--no-save",
        action="store_true",    # presence of flag = True, absence = False
        help="Don't save intermediate outputs to ./outputs/",
    )

    args = parser.parse_args()

    # Combine positional and flag versions of the topic argument
    topic = args.topic or args.topic_flag
    if not topic:
        print("Error: please provide a research topic.")
        print("  Example: python main.py \\"GLP-1 receptor agonists\\"")
        sys.exit(1)

    # Override LLM provider if specified (sets env var so get_llm() picks it up)
    if args.provider:
        import os
        os.environ["LLM_PROVIDER"] = args.provider

    # Run the full pipeline
    result = run_pipeline(topic=topic, save_outputs=not args.no_save)

    # Exit with error code if any agent failed (useful for CI/CD pipelines)
    if result.errors:
        print("\\nPipeline completed with errors:")
        for e in result.errors:
            print(f"  - {e}")
        sys.exit(1)

    # Print a preview of the JSON report to the terminal
    print("\\n── FINAL JSON REPORT (preview) ──")
    preview = {
        k: result.report[k]
        for k in ["report_id", "topic", "summary", "key_findings"]
        if k in result.report
    }
    print(json.dumps(preview, indent=2))


if __name__ == "__main__":
    main()
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 18 — DEMO SYSTEM HEADER
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## 🎬 Part 6 — Management Demo System

The demo system lets you **show the pipeline to management without any API keys**.
It uses pre-built mock content that simulates realistic agent outputs with
timed delays (so the animation looks natural).

### Files:
| File | Purpose |
|---|---|
| `demo/topics.txt` | Research topics, editable by hand |
| `demo/backend/mock_runner.py` | Pre-built content + simulated agent delays |
| `demo/backend/app.py` | FastAPI REST API (topics, pipeline, review, share) |
| `demo/pipeline_ui.html` | The browser UI that calls the API |

### How to run the demo:
```
cd D:\\Codebase\\Pinnacle\\demo
run_demo.bat
```
Then open `demo/pipeline_ui.html` in your browser.
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 19 — TOPICS.TXT FORMAT
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 📋 Topics File (`demo/topics.txt`)

A plain text file — one topic per line — that non-technical users can edit.
Lines starting with `#` are comments (ignored).
Format: `Topic | Specialty | Therapy Area`
""")

code("""\
# ─── demo/topics.txt (content shown as Python string for reference) ────────────
# Edit this file to add your own research topics for the demo.
# Format: Topic | Specialty | Therapy Area
# Lines starting with # are treated as comments and ignored.

TOPICS_FILE_CONTENT = \"\"\"
# PinnacleIQ Research Topics
# Format: Topic | Specialty | Therapy Area
# Edit this file and refresh the demo to update the topic list.

GLP-1 Receptor Agonists in Type 2 Diabetes Management | Diabetology | GLP-1 Therapy
SGLT2 Inhibitors and Cardiovascular Outcomes in Heart Failure | Cardiology | Heart Failure
PCOS Management: Latest Evidence on Inositol vs Metformin | Gynaecology | PCOS
Hypertension Management in Indian Patients: ARBs vs ACE Inhibitors | Cardiology | Hypertension
Vitamin D Deficiency in Indian Population: Prevalence and Treatment | General Medicine | Micronutrient Deficiency
Antibiotic Stewardship in Community-Acquired Pneumonia | Pulmonology | Respiratory Infections
Iron Deficiency Anaemia in Women: IV vs Oral Iron Therapy | Haematology | Anaemia
Diabetic Kidney Disease: SGLT2i and GLP-1 RA Combination Therapy | Nephrology | CKD
\"\"\"

# How the FastAPI backend reads this file:
# GET /topics → reads topics.txt → returns list of {topic, specialty, therapy_area}
def parse_topics(text: str) -> list:
    \"\"\"Parse topics.txt format into a list of dicts.\"\"\"
    topics = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue    # skip empty lines and comments
        parts = [p.strip() for p in line.split("|")]
        topics.append({
            "topic":        parts[0] if len(parts) > 0 else line,
            "specialty":    parts[1] if len(parts) > 1 else "General Medicine",
            "therapy_area": parts[2] if len(parts) > 2 else "General",
        })
    return topics

# Test the parser
parsed = parse_topics(TOPICS_FILE_CONTENT)
for t in parsed:
    print(f"  {t['topic'][:50]:<50} | {t['specialty']:<20} | {t['therapy_area']}")
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 20 — MOCK RUNNER
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 🎭 Mock Pipeline Runner (`demo/backend/mock_runner.py`)

This simulates the 4-agent pipeline with:
- **Pre-built content** for GLP-1, SGLT2, and PCOS topics (rich, realistic data)
- **Generic fallback** for any other topic (uses the topic/specialty/therapy_area to fill templates)
- **Realistic delays** (~2 seconds per agent step) so the progress animation looks natural

The `run_store` dict is updated at each step — the FastAPI polling endpoint reads it
to return live progress to the browser.
""")

code("""\
# ─── demo/backend/mock_runner.py ─────────────────────────────────────────────
# Simulates the real 4-agent pipeline instantly (no API keys needed).
# Pre-built content for 3 medical topics + generic fallback for anything else.
# ─────────────────────────────────────────────────────────────────────────────

import time
import random

# ── Pre-built content library ─────────────────────────────────────────────────
# Each entry is a dict matching exactly the structure Delta would produce.
# Keys correspond to the DB columns in content_items.
# The key (e.g. "GLP-1") is matched against the topic string (case-insensitive).

MOCK_LIBRARY = {
    # ── GLP-1 content ─────────────────────────────────────────────────────────
    "GLP-1": {
        "title": "GLP-1 Receptor Agonists in Type 2 Diabetes: 2025 Real-World Evidence Update",
        "summary": (
            "A landmark 2025 meta-analysis of 34 RCTs (n=87,420) confirms GLP-1 receptor agonists "
            "deliver superior glycaemic control (HbA1c reduction: −1.8% vs −1.1% for DPP-4i) alongside "
            "significant cardiovascular and renal protection benefits. Semaglutide leads the class with "
            "the strongest evidence in South Asian T2DM populations, including three Indian cohort studies."
        ),
        "key_findings": [
            "Semaglutide 1 mg weekly reduces HbA1c by 1.8% and body weight by 6.2 kg at 52 weeks",
            "SUSTAIN-6 extension: 33% reduction in MACE vs placebo sustained at 5 years",
            "Dulaglutide shows superiority in patients with eGFR 30-60 (renal protection confirmed)",
            "Once-weekly formulations achieve 94% patient adherence vs 71% for daily injections",
            "Indian cohort (n=2,840): GLP-1 RAs reduce HbA1c by 1.6% in patients with BMI 23-27",
            "Combination with SGLT2 inhibitors provides additive CV and renal benefit",
        ],
        "clinical_insights": (
            "For Pinnacle Diabetologists: GLP-1 RAs are now first-line alongside metformin for T2DM "
            "patients with established ASCVD, heart failure, or CKD. The 2025 ADA/EASD consensus "
            "recommends semaglutide as preferred agent when weight reduction is also a goal."
        ),
        "recommendations": [
            "Initiate GLP-1 RA in T2DM patients with HbA1c >7.5% and established CVD",
            "Prefer semaglutide SC for maximum HbA1c lowering; oral for injection-averse patients",
            "Combine with SGLT2i in heart failure or CKD patients for synergistic benefit",
            "Monitor for GI side effects in first 4 weeks; consider anti-emetics initially",
            "Re-assess glycaemic targets every 3 months for the first year",
        ],
        "emerging_trends": [
            "Oral semaglutide 50 mg (PIONEER-PLUS) — superior to injectable liraglutide",
            "Tirzepatide (GIP+GLP-1): -2.4% HbA1c, -11.2 kg weight — SURPASS programme results",
            "Retatrutide (triple agonist GIP/GLP-1/glucagon): Phase 3 data expected Q3 2025",
        ],
        "evidence_quality": "High — 34 RCTs, 3 Indian cohort studies, 2025 ADA/EASD guidelines.",
        "short_article": (
            "RESEARCH UPDATE: GLP-1 Receptor Agonists — What's New in 2025\\n\\n"
            "A major 2025 meta-analysis of 87,420 patients reaffirms GLP-1 receptor agonists as the "
            "preferred add-on in Type 2 Diabetes with cardiovascular risk. Semaglutide continues to lead "
            "with a 1.8% HbA1c reduction and 6.2 kg weight loss at one year.\\n\\n"
            "KEY FINDING: For your Indian patients (BMI 23-27), GLP-1 RAs deliver a 1.6% HbA1c drop.\\n\\n"
            "ACTION: Consider initiating semaglutide in your next eligible patient."
        ),
        "tags": ["GLP-1", "Semaglutide", "T2DM", "Cardiovascular", "HbA1c", "Indian Population"],
        "sub_category": "Meta-Analysis / Systematic Review",
    },

    # ── SGLT2 content ─────────────────────────────────────────────────────────
    "SGLT2": {
        "title": "SGLT2 Inhibitors and Cardiovascular Outcomes in Heart Failure: 3-Year Follow-Up",
        "summary": (
            "Three-year follow-up data from EMPEROR-Reduced and DAPA-HF confirm SGLT2 inhibitors "
            "reduce hospitalisation for heart failure by 30% and CV mortality by 18% in both HFrEF "
            "and HFpEF patients, regardless of diabetes status."
        ),
        "key_findings": [
            "Empagliflozin reduces HF hospitalisation by 30% at 3 years",
            "Dapagliflozin effect consistent in HFpEF (EF >40%) — opens new treatment frontier",
            "SGLT2i benefit independent of baseline HbA1c or diabetes status",
            "eGFR decline slowed by 1.6 mL/min/year vs placebo",
            "Indian HF registry data: SGLT2i reduces 30-day readmission by 27%",
        ],
        "clinical_insights": (
            "SGLT2 inhibitors are now standard of care for ALL heart failure patients. "
            "The 2025 ESC HF guidelines give Class I recommendation regardless of EF or diabetes."
        ),
        "recommendations": [
            "Add SGLT2 inhibitor to all HFrEF patients on optimised GDMT regardless of diabetes",
            "Consider dapagliflozin for HFpEF — first evidence-based option in this population",
            "Initiate in-hospital at the time of HF admission when haemodynamically stable",
            "Monitor renal function at week 4; transient eGFR dip is expected",
        ],
        "emerging_trends": [
            "Sotagliflozin (SGLT1+2 dual inhibitor): Phase 3 SOLOIST data in acute HF",
            "SGLT2i in cardiac amyloidosis — exploratory signals in ATTR-HF patients",
        ],
        "evidence_quality": "High — Class I ESC 2025 guidelines, two landmark RCTs with 3-year follow-up.",
        "short_article": (
            "RESEARCH UPDATE: SGLT2 Inhibitors — Now for ALL Heart Failure Patients\\n\\n"
            "The 3-year follow-up settles the debate: SGLT2 inhibitors reduce HF hospitalisation by 30% "
            "regardless of whether the patient has diabetes.\\n\\n"
            "ACTION: Initiate empagliflozin or dapagliflozin in your next HF admission."
        ),
        "tags": ["SGLT2", "Heart Failure", "Empagliflozin", "Dapagliflozin", "ESC 2025"],
        "sub_category": "Clinical Trial / RCT",
    },

    # ── PCOS content ──────────────────────────────────────────────────────────
    "PCOS": {
        "title": "Inositol vs Metformin in PCOS: 2025 Systematic Review",
        "summary": (
            "A 2025 systematic review of 22 RCTs (n=3,180) demonstrates myo-inositol achieves "
            "comparable insulin sensitisation to metformin with significantly fewer GI adverse effects "
            "(12% vs 34%)."
        ),
        "key_findings": [
            "Myo-inositol 4g/day: comparable HbA1c reduction to metformin 1500mg/day at 6 months",
            "GI adverse events: 12% (inositol) vs 34% (metformin) — p<0.001",
            "Menstrual regularity at 6 months: 78% (combined inositol) vs 64% (metformin)",
            "Indian cohort (n=420): inositol effective in lean PCOS (BMI <23)",
        ],
        "clinical_insights": (
            "For Indian Gynaecologists: myo-inositol is now a strong alternative to metformin, "
            "particularly for lean PCOS patients (BMI <23) common in Indian practice."
        ),
        "recommendations": [
            "First-line inositol (40:1 ratio, 4g/day) for lean PCOS or metformin-intolerant patients",
            "Combine with lifestyle intervention — synergistic benefit documented",
            "For conception-seeking patients: prefer inositol as first-line",
        ],
        "emerging_trends": [
            "Inositol + NAC (N-acetylcysteine) combination: Phase 3 Indian trial ongoing",
            "Gut microbiome modulation as adjunct to inositol",
        ],
        "evidence_quality": "Moderate-High — 22 RCTs, Indian cohort data, 2025 ESHRE/ASRM position statement.",
        "short_article": (
            "RESEARCH UPDATE: Inositol Overtakes Metformin in PCOS?\\n\\n"
            "A 2025 meta-analysis of 3,180 PCOS patients finds myo-inositol matches metformin — "
            "with only 12% GI side effects vs 34% for metformin.\\n\\n"
            "ACTION: Consider switching metformin-intolerant PCOS patients to myo-inositol 4g/day."
        ),
        "tags": ["PCOS", "Inositol", "Metformin", "Fertility", "Indian Population"],
        "sub_category": "Meta-Analysis / Systematic Review",
    },
}


def _generic_content(topic: str, specialty: str, therapy_area: str) -> dict:
    \"\"\"
    Fallback content generator for topics not in MOCK_LIBRARY.
    Uses f-strings to produce realistic-looking content for any topic.
    \"\"\"
    return {
        "title": f"{topic}: 2025 Evidence Update and Clinical Practice Implications",
        "summary": (
            f"A comprehensive 2025 review consolidates the latest evidence on {topic}, drawing from "
            f"14 randomised controlled trials and 8 observational studies. The evidence supports a "
            f"paradigm shift in {specialty} practice relevant to Indian patient populations."
        ),
        "key_findings": [
            f"Updated 2025 guidelines recommend earlier initiation in {therapy_area}",
            f"Real-world data from Indian cohorts (n=1,840) confirms global efficacy",
            f"Combination approaches show 40% improvement vs monotherapy",
            f"Safety profile consistent across South Asian populations",
            f"Patient adherence improved with once-daily regimens",
        ],
        "clinical_insights": (
            f"For {specialty} specialists: proactive management in {therapy_area} is supported by "
            f"the 2025 evidence base. Indian population-specific data now available."
        ),
        "recommendations": [
            f"Screen high-risk patients for {therapy_area} at every encounter",
            f"Initiate evidence-based therapy without delay once diagnosis confirmed",
            f"Follow 2025 guidelines for combination therapy selection",
        ],
        "emerging_trends": [
            f"Novel targeted agents in Phase 3 trials for {therapy_area}",
            f"Digital health tools improving adherence in {specialty} practice",
        ],
        "evidence_quality": "Moderate — 14 RCTs, 8 observational studies, 2025 guidelines.",
        "short_article": (
            f"RESEARCH UPDATE: {topic}\\n\\n"
            f"New 2025 evidence consolidates treatment in {therapy_area}. Indian cohort data (n=1,840) "
            f"confirms efficacy matching global trials.\\n\\n"
            f"ACTION: Review your {therapy_area} patients against 2025 guidelines."
        ),
        "tags": [topic.split()[0], specialty, therapy_area, "2025 Guidelines"],
        "sub_category": "Review Article",
    }


def run_mock_pipeline(topic: str, specialty: str, therapy_area: str,
                      run_store: dict, run_id: str) -> None:
    \"\"\"
    Simulate the 4-agent pipeline with realistic timing.

    Updates run_store[run_id] at each step so the FastAPI polling endpoint
    can return live progress to the browser.

    The sleep() calls make the agent animation look realistic in the UI.
    In production, these would be actual LLM API call durations.
    \"\"\"

    def update(agent: str, pct: int, msg: str):
        \"\"\"Update the run's status and wait a bit (simulating agent thinking time).\"\"\"
        run_store[run_id].update({
            "current_agent": agent,
            "progress": pct,
            "status_msg": msg,
        })
        time.sleep(random.uniform(1.8, 2.8))   # 1.8-2.8 seconds per step

    # ── Simulate Agent Alpha (Research) ───────────────────────────────────────
    update("alpha", 10, "🔍 Agent Alpha: Searching PubMed and web sources...")
    update("alpha", 25, "📄 Agent Alpha: Reading relevant papers...")
    update("alpha", 40, "📝 Agent Alpha: Consolidating research article...")

    # ── Simulate Agent Beta (Analysis) ────────────────────────────────────────
    update("beta",  55, "🧠 Agent Beta: Extracting insights and key findings...")
    update("beta",  65, "📊 Agent Beta: Preparing clinical recommendations...")

    # ── Simulate Agent Gamma (Writing & Delivery) ─────────────────────────────
    update("gamma", 75, "✍️  Agent Gamma: Writing doctor-friendly article...")
    update("gamma", 85, "📱 Agent Gamma: Formatting for WhatsApp & email delivery...")

    # ── Simulate Agent Delta (JSON Report) ────────────────────────────────────
    update("delta", 92, "🗂️  Agent Delta: Generating structured JSON report...")
    update("delta", 98, "✅ Agent Delta: Finalising for Pinnacle portal...")

    # ── Select content ────────────────────────────────────────────────────────
    # Check if the topic matches any pre-built content (case-insensitive keyword match)
    key = next((k for k in MOCK_LIBRARY if k.upper() in topic.upper()), None)
    content = MOCK_LIBRARY[key] if key else _generic_content(topic, specialty, therapy_area)

    # ── Mark pipeline as complete ─────────────────────────────────────────────
    run_store[run_id].update({
        "status":       "completed",
        "progress":     100,
        "current_agent": "done",
        "status_msg":   "Pipeline complete. Content ready for MA review.",
        "content": {
            "topic":        topic,
            "specialty":    specialty,
            "therapy_area": therapy_area,
            **content,      # unpack all the content fields
        },
    })
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 21 — FASTAPI BACKEND
# ═════════════════════════════════════════════════════════════════════════════
md("""\
### 🌐 FastAPI Backend (`demo/backend/app.py`)

The REST API that the browser UI calls. All endpoints explained below.

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Health check |
| `/topics` | GET | Read topics.txt, return list |
| `/pipeline/run` | POST | Start pipeline in background thread, return run_id |
| `/pipeline/status/{run_id}` | GET | Poll for pipeline progress (0-100%) |
| `/content` | GET | List all content items (filterable by status) |
| `/content/{id}` | GET | Single content item |
| `/content/{id}/approve` | POST | MA approves → status = 'approved' |
| `/content/{id}/reject` | POST | MA rejects with reason |
| `/content/{id}/share` | POST | BU Head shares with a doctor (logs it) |
| `/share-logs` | GET | All sharing history |

**Database:** SQLite (`pinnacleiq.db`) — no setup needed, file auto-created.
**CORS:** All origins allowed (needed because the HTML file opens from `file://`)
""")

code("""\
# ─── demo/backend/app.py ─────────────────────────────────────────────────────
# FastAPI backend for the PinnacleIQ demo portal.
# Uses SQLite for persistence and in-memory dict for pipeline run status.
# ─────────────────────────────────────────────────────────────────────────────

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# from mock_runner import run_mock_pipeline   # the fake pipeline above


# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="PinnacleIQ Research API", version="1.0.0")

# CORS (Cross-Origin Resource Sharing) — allows the HTML file (file://) to
# call this API (http://localhost:8000). In production, restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow all origins for local demo
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE       = Path(__file__).parent
DB_PATH    = BASE / "pinnacleiq.db"
TOPICS_FILE = BASE.parent / "topics.txt"

# In-memory store for pipeline run status.
# Key: run_id (UUID string)  Value: dict with status/progress/content
# We use a threading.Lock() to prevent race conditions when multiple
# pipeline runs update this dict simultaneously.
pipeline_runs: dict = {}
_lock = threading.Lock()


# ── Database Setup ────────────────────────────────────────────────────────────
def get_db():
    \"\"\"Get a database connection with dict-like row access.\"\"\"
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row   # rows accessible as row['column_name']
    return conn


def init_db():
    \"\"\"Create tables if they don't exist. Called once on startup.\"\"\"
    conn = get_db()
    conn.executescript(\"\"\"
        -- content_items: stores all AI-generated research content
        CREATE TABLE IF NOT EXISTS content_items (
            id               TEXT PRIMARY KEY,      -- UUID
            topic            TEXT NOT NULL,
            title            TEXT NOT NULL,
            specialty        TEXT,
            therapy_area     TEXT,
            sub_category     TEXT,
            tags             TEXT,                  -- stored as JSON array string
            summary          TEXT,
            key_findings     TEXT,                  -- stored as JSON array string
            clinical_insights TEXT,
            recommendations  TEXT,                  -- stored as JSON array string
            emerging_trends  TEXT,                  -- stored as JSON array string
            short_article    TEXT,
            full_research    TEXT,
            evidence_quality TEXT,
            status           TEXT DEFAULT 'pending_review',  -- pending/approved/rejected
            rejection_reason TEXT,
            created_at       TEXT,
            reviewed_at      TEXT,
            source           TEXT DEFAULT 'ai_agent'
        );

        -- share_logs: records every time content is shared with a doctor
        CREATE TABLE IF NOT EXISTS share_logs (
            id          TEXT PRIMARY KEY,
            content_id  TEXT NOT NULL,
            doctor_id   TEXT,
            doctor_name TEXT,
            channel     TEXT,           -- 'whatsapp', 'email', etc.
            shared_at   TEXT,
            shared_by   TEXT
        );
    \"\"\")
    conn.commit()
    conn.close()

init_db()   # run on module import (i.e., when app starts)


# ── Helpers ───────────────────────────────────────────────────────────────────
def row_to_dict(row) -> dict:
    \"\"\"Convert a sqlite3.Row to a dict, parsing JSON array fields.\"\"\"
    d = dict(row)
    # These fields are stored as JSON strings in SQLite, convert back to lists
    for field in ("tags", "key_findings", "recommendations", "emerging_trends"):
        if d.get(field) and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
    return d

def now_iso() -> str:
    \"\"\"Current UTC time in ISO 8601 format.\"\"\"
    return datetime.now(timezone.utc).isoformat()


# ── Pydantic Request/Response Schemas ─────────────────────────────────────────
# FastAPI uses these for automatic request validation and API documentation.
# If a request body doesn't match the schema, FastAPI returns a 422 error automatically.

class RunRequest(BaseModel):
    topic: str
    specialty: str
    therapy_area: str

class ApproveRequest(BaseModel):
    reviewer: Optional[str] = "Dr. Prashant Agarwal (MA)"

class RejectRequest(BaseModel):
    reason: str
    reviewer: Optional[str] = "Dr. Prashant Agarwal (MA)"

class ShareRequest(BaseModel):
    doctor_id:   Optional[str] = "doc_001"
    doctor_name: Optional[str] = "Demo Doctor"
    channel:     Optional[str] = "whatsapp"
    shared_by:   Optional[str] = "Jijo (BU Head)"


# ── API Routes ────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    \"\"\"Health check — confirms the server is running.\"\"\"
    return {"status": "ok", "service": "PinnacleIQ Research API"}


@app.get("/topics")
def get_topics():
    \"\"\"Read research topics from topics.txt and return as a list.\"\"\"
    if not TOPICS_FILE.exists():
        raise HTTPException(404, f"topics.txt not found at {TOPICS_FILE}")
    topics = []
    for line in TOPICS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue    # skip comments and blank lines
        parts = [p.strip() for p in line.split("|")]
        topics.append({
            "topic":        parts[0] if len(parts) > 0 else line,
            "specialty":    parts[1] if len(parts) > 1 else "General Medicine",
            "therapy_area": parts[2] if len(parts) > 2 else "General",
        })
    return {"topics": topics, "count": len(topics)}


@app.post("/pipeline/run")
def start_pipeline(req: RunRequest, bg: BackgroundTasks):
    \"\"\"
    Start the research pipeline for a topic.
    Returns immediately with a run_id — poll /pipeline/status/{run_id} for progress.

    BackgroundTasks: FastAPI runs the pipeline in a background thread after returning
    the 200 response. The browser can poll for status while it runs.
    \"\"\"
    run_id = str(uuid.uuid4())

    # Initialize the run's status in the in-memory store
    with _lock:
        pipeline_runs[run_id] = {
            "status":        "running",
            "topic":         req.topic,
            "specialty":     req.specialty,
            "therapy_area":  req.therapy_area,
            "progress":      0,
            "current_agent": "alpha",
            "status_msg":    "Starting pipeline...",
            "content":       None,
            "content_id":    None,
            "started_at":    now_iso(),
        }

    def _run():
        \"\"\"The actual pipeline run — executes in a background thread.\"\"\"
        run_mock_pipeline(
            topic=req.topic,
            specialty=req.specialty,
            therapy_area=req.therapy_area,
            run_store=pipeline_runs,
            run_id=run_id,
        )
        # Persist completed content to SQLite database
        run = pipeline_runs.get(run_id, {})
        if run.get("status") == "completed" and run.get("content"):
            c = run["content"]
            cid = str(uuid.uuid4())
            conn = get_db()
            conn.execute(
                \"\"\"INSERT INTO content_items
                   (id, topic, title, specialty, therapy_area, sub_category,
                    tags, summary, key_findings, clinical_insights,
                    recommendations, emerging_trends, short_article,
                    evidence_quality, status, created_at, source)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)\"\"\",
                (
                    cid,
                    c.get("topic", req.topic),
                    c.get("title", ""),
                    c.get("specialty", req.specialty),
                    c.get("therapy_area", req.therapy_area),
                    c.get("sub_category", "Review Article"),
                    json.dumps(c.get("tags", [])),              # list → JSON string
                    c.get("summary", ""),
                    json.dumps(c.get("key_findings", [])),
                    c.get("clinical_insights", ""),
                    json.dumps(c.get("recommendations", [])),
                    json.dumps(c.get("emerging_trends", [])),
                    c.get("short_article", ""),
                    c.get("evidence_quality", ""),
                    "pending_review",
                    now_iso(),
                    "ai_agent",
                ),
            )
            conn.commit()
            conn.close()
            pipeline_runs[run_id]["content_id"] = cid

    bg.add_task(_run)   # schedule _run() to execute after this function returns
    return {"run_id": run_id, "status": "running"}


@app.get("/pipeline/status/{run_id}")
def pipeline_status(run_id: str):
    \"\"\"Poll for pipeline progress. Browser calls this every 1 second.\"\"\"
    run = pipeline_runs.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return {
        "run_id":        run_id,
        "status":        run["status"],          # 'running' or 'completed'
        "progress":      run["progress"],         # 0-100
        "current_agent": run["current_agent"],    # 'alpha'/'beta'/'gamma'/'delta'/'done'
        "status_msg":    run["status_msg"],       # human-readable progress message
        "content_id":    run.get("content_id"),  # DB ID once saved (None while running)
    }


@app.get("/content")
def list_content(status: Optional[str] = None):
    \"\"\"
    List content items. Optional ?status=pending_review / approved / rejected filter.
    Also returns counts per status for the dashboard header.
    \"\"\"
    conn = get_db()
    if status:
        rows = conn.execute(
            "SELECT * FROM content_items WHERE status=? ORDER BY created_at DESC", (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM content_items ORDER BY created_at DESC"
        ).fetchall()
    conn.close()

    items = [row_to_dict(r) for r in rows]
    return {
        "items": items,
        "counts": {
            "total":    len(items),
            "pending":  sum(1 for i in items if i["status"] == "pending_review"),
            "approved": sum(1 for i in items if i["status"] == "approved"),
            "rejected": sum(1 for i in items if i["status"] == "rejected"),
        }
    }


@app.post("/content/{content_id}/approve")
def approve_content(content_id: str, req: ApproveRequest):
    \"\"\"Medical Affairs approves content → status changes to 'approved'.\"\"\"
    conn = get_db()
    row = conn.execute("SELECT status FROM content_items WHERE id=?", (content_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Content not found")
    if row["status"] != "pending_review":
        conn.close()
        raise HTTPException(400, f"Content is already '{row['status']}'")

    conn.execute(
        "UPDATE content_items SET status='approved', reviewed_at=? WHERE id=?",
        (now_iso(), content_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Content approved. Now available for BU Head to share.", "content_id": content_id}


@app.post("/content/{content_id}/reject")
def reject_content(content_id: str, req: RejectRequest):
    \"\"\"Medical Affairs rejects content with a reason.\"\"\"
    if not req.reason.strip():
        raise HTTPException(400, "Rejection reason is required")

    conn = get_db()
    row = conn.execute("SELECT status FROM content_items WHERE id=?", (content_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Content not found")

    conn.execute(
        "UPDATE content_items SET status='rejected', rejection_reason=?, reviewed_at=? WHERE id=?",
        (req.reason, now_iso(), content_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Content rejected.", "content_id": content_id}


@app.post("/content/{content_id}/share")
def share_content(content_id: str, req: ShareRequest):
    \"\"\"
    BU Head shares approved content with a doctor.
    Includes a 30-day frequency warning (does not block — just warns).
    \"\"\"
    conn = get_db()

    # Verify content exists and is approved
    row = conn.execute("SELECT status, title FROM content_items WHERE id=?", (content_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Content not found")
    if row["status"] != "approved":
        conn.close()
        raise HTTPException(400, "Content must be approved before sharing")

    # Check 30-day frequency: how many times has this doctor received content recently?
    recent = conn.execute(
        \"\"\"SELECT COUNT(*) as cnt FROM share_logs
           WHERE doctor_id=? AND shared_at > datetime('now','-30 days')\"\"\",
        (req.doctor_id,)
    ).fetchone()

    warning = None
    if recent and recent["cnt"] > 0:
        warning = (
            f"You have already shared {recent['cnt']} article(s) with this doctor "
            f"in the last 30 days. Recommended frequency is 1-2/month."
        )

    # Log the share event
    log_id = str(uuid.uuid4())
    conn.execute(
        \"\"\"INSERT INTO share_logs (id, content_id, doctor_id, doctor_name, channel, shared_at, shared_by)
           VALUES (?,?,?,?,?,?,?)\"\"\",
        (log_id, content_id, req.doctor_id, req.doctor_name, req.channel, now_iso(), req.shared_by)
    )
    conn.commit()
    conn.close()

    return {
        "message": f"Content shared via {req.channel} with {req.doctor_name}.",
        "log_id":  log_id,
        "warning": warning,    # None if within frequency limit
    }


@app.get("/share-logs")
def get_share_logs():
    \"\"\"Return full sharing history.\"\"\"
    conn = get_db()
    rows = conn.execute("SELECT * FROM share_logs ORDER BY shared_at DESC").fetchall()
    conn.close()
    return {"logs": [dict(r) for r in rows]}


# ── Entry point ───────────────────────────────────────────────────────────────
# Run with: python app.py
# Or from the demo bat file: cd demo && run_demo.bat
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 22 — RUNNABLE MOCK TEST (NO API KEYS)
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## ✅ Part 7 — Live Demo (Run This Right Now — No API Keys Needed!)

The cells below run the mock pipeline **completely in-memory** — no server, no API keys.
This is the same logic the demo system uses, just run directly in the notebook.
""")

code("""\
# ── Standalone mock demo — runs entirely in-memory ───────────────────────────
# Paste or import the functions from earlier cells, then run the full mock pipeline.

import time
import random
import json

# ── Paste the MOCK_LIBRARY and helper functions here ─────────────────────────
# (or run the mock_runner.py cell above first)

# ── In-memory run store (mimics what FastAPI uses) ────────────────────────────
demo_run_store = {}
demo_run_id = "demo-run-001"

# Initialize the run entry
demo_run_store[demo_run_id] = {
    "status": "running",
    "progress": 0,
    "current_agent": "alpha",
    "status_msg": "Starting...",
    "content": None,
}

print("=" * 60)
print("  PINNACLEIQ MOCK PIPELINE DEMO")
print("=" * 60)

# ── Run the mock pipeline ─────────────────────────────────────────────────────
# We define a fast version here (no sleeps) so Colab doesn't time out.
# The real demo uses sleeps for the animated UI effect.

def run_mock_pipeline_fast(topic, specialty, therapy_area, run_store, run_id):
    \"\"\"Fast version of mock pipeline — no sleep delays (for notebook demo).\"\"\"

    steps = [
        ("alpha", 10,  "🔍 Agent Alpha: Searching PubMed and web sources..."),
        ("alpha", 25,  "📄 Agent Alpha: Reading relevant papers..."),
        ("alpha", 40,  "📝 Agent Alpha: Consolidating research article..."),
        ("beta",  55,  "🧠 Agent Beta: Extracting insights and key findings..."),
        ("beta",  65,  "📊 Agent Beta: Preparing clinical recommendations..."),
        ("gamma", 75,  "✍️  Agent Gamma: Writing doctor-friendly article..."),
        ("gamma", 85,  "📱 Agent Gamma: Formatting for WhatsApp & email..."),
        ("delta", 92,  "🗂️  Agent Delta: Generating structured JSON report..."),
        ("delta", 98,  "✅ Agent Delta: Finalising for Pinnacle portal..."),
    ]

    for agent, pct, msg in steps:
        run_store[run_id].update({"current_agent": agent, "progress": pct, "status_msg": msg})
        print(f"  [{pct:>3}%] {msg}")

    # Select content from library or generate generic
    key = next((k for k in MOCK_LIBRARY if k.upper() in topic.upper()), None)

    if key:
        content = MOCK_LIBRARY[key]
        print(f"\\n  ✓ Found pre-built content for: {key}")
    else:
        content = _generic_content(topic, specialty, therapy_area)
        print(f"\\n  ✓ Generated generic content for: {topic}")

    run_store[run_id].update({
        "status":        "completed",
        "progress":      100,
        "current_agent": "done",
        "status_msg":    "Pipeline complete!",
        "content": {"topic": topic, "specialty": specialty, "therapy_area": therapy_area, **content},
    })

# ── Run it ────────────────────────────────────────────────────────────────────
run_mock_pipeline_fast(
    topic       = "GLP-1 Receptor Agonists in Type 2 Diabetes Management",
    specialty   = "Diabetology",
    therapy_area= "GLP-1 Therapy",
    run_store   = demo_run_store,
    run_id      = demo_run_id,
)

print("\\n" + "=" * 60)
print("  PIPELINE COMPLETE ✅")
print("=" * 60)
""")

code("""\
# ── Display the results ───────────────────────────────────────────────────────
content = demo_run_store[demo_run_id]["content"]

print("\\n📋 TITLE")
print(f"  {content['title']}")

print("\\n📝 SUMMARY")
print(f"  {content['summary']}")

print("\\n🔑 KEY FINDINGS")
for i, finding in enumerate(content["key_findings"], 1):
    print(f"  {i}. {finding}")

print("\\n💡 CLINICAL INSIGHTS")
print(f"  {content['clinical_insights']}")

print("\\n📌 RECOMMENDATIONS")
for i, rec in enumerate(content["recommendations"], 1):
    print(f"  {i}. {rec}")

print("\\n🚀 EMERGING TRENDS")
for trend in content["emerging_trends"]:
    print(f"  • {trend}")

print("\\n📱 SHORT ARTICLE (for WhatsApp/Email):")
print("-" * 50)
print(content["short_article"])
print("-" * 50)

print("\\n🏷️  TAGS:", ", ".join(content["tags"]))
print(f"📊 EVIDENCE QUALITY: {content['evidence_quality']}")
""")

code("""\
# ── Show the full JSON structure (what Delta sends to the portal) ─────────────
import uuid
from datetime import datetime, timezone

# Build the complete JSON report (as Delta would)
full_report = {
    "report_id":          str(uuid.uuid4()),
    "generated_at":       datetime.now(timezone.utc).isoformat(),
    "topic":              content["topic"],
    "specialty":          content["specialty"],
    "therapy_area":       content["therapy_area"],
    "title":              content["title"],
    "summary":            content["summary"],
    "key_findings":       content["key_findings"],
    "clinical_insights":  content["clinical_insights"],
    "recommendations":    content["recommendations"],
    "emerging_trends":    content["emerging_trends"],
    "evidence_quality":   content["evidence_quality"],
    "short_article":      content["short_article"],
    "tags":               content["tags"],
    "metadata": {
        "agent_version": "1.0.0",
        "llm_provider":  "mock",
        "pipeline":      "Alpha→Beta→Gamma→Delta",
    }
}

print("\\n📦 COMPLETE JSON REPORT (what gets sent to Pinnacle Portal):")
print("=" * 60)
print(json.dumps(full_report, indent=2))
""")

code("""\
# ── Simulate the MA Review + BU Head Share workflow ───────────────────────────
# This shows the full end-to-end flow without a running server.

print("\\n🏥 SIMULATING MA REVIEW WORKFLOW")
print("=" * 60)

# Step 1: Content arrives as pending_review
status = "pending_review"
print(f"\\n[1] Content created → Status: {status}")

# Step 2: Medical Affairs reviews and approves
reviewer = "Dr. Prashant Agarwal (MA Head)"
status = "approved"
reviewed_at = datetime.now(timezone.utc).isoformat()
print(f"[2] MA Approval by {reviewer} → Status: {status}")

# Step 3: BU Head shares with a doctor
doctor = {"id": "doc_001", "name": "Dr. Rajesh Sharma", "specialty": "Diabetology"}
channel = "whatsapp"
share_log = {
    "log_id":     str(uuid.uuid4()),
    "content_id": full_report["report_id"],
    "doctor_id":  doctor["id"],
    "doctor_name":doctor["name"],
    "channel":    channel,
    "shared_at":  datetime.now(timezone.utc).isoformat(),
    "shared_by":  "Jijo (BU Head · PMT)",
}
print(f"[3] Shared via {channel.upper()} with {doctor['name']}")
print(f"    Share Log ID: {share_log['log_id']}")

# Step 4: 30-day frequency check simulation
shares_this_month = 1
warning = None
if shares_this_month > 2:
    warning = f"⚠️ {shares_this_month} articles shared with this doctor in 30 days (limit: 2)"

print(f"\\n[4] Frequency Check: {shares_this_month} share(s) this month")
if warning:
    print(f"     {warning}")
else:
    print(f"     ✅ Within recommended frequency (1-2/month)")

print("\\n✅ Complete workflow simulated successfully!")
print("   In production: each step calls a FastAPI endpoint")
print("   which reads/writes the SQLite database.")
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 23 — RUNNING FOR REAL
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## 🚀 Part 8 — Running the Real Pipeline

Once you have API keys, run the full pipeline like this:
""")

code("""\
# ── Full pipeline run (requires API keys set in Step 1) ──────────────────────
#
# Uncomment and run this cell once you have:
#   - OPENROUTER_API_KEY  (get free at https://openrouter.ai/keys)
#   - TAVILY_API_KEY      (get free at https://app.tavily.com)
#
# Optional (pipeline skips gracefully if missing):
#   - ONEDRIVE keys (reads internal documents from OneDrive)
#   - TWILIO keys   (WhatsApp delivery)
#   - SENDGRID key  (email delivery)
#
# To try a different model — just change OPENROUTER_MODEL in Step 1
# and re-run. No other code changes needed!

# import os
# # Make sure keys are loaded (from Step 1)
# assert os.environ.get("OPENROUTER_API_KEY"), "Set OPENROUTER_API_KEY in Step 1 first!"
# assert os.environ.get("TAVILY_API_KEY"), "Set TAVILY_API_KEY in Step 1 first!"

# # Run the full pipeline
# result = run_pipeline(
#     topic="GLP-1 receptor agonists in Type 2 Diabetes management 2025",
#     save_outputs=True     # saves to ./outputs/ folder
# )

# # Print results
# print("\\n── Research Article (Alpha) ──")
# print(result.research_article[:500], "...\\n")

# print("── Insights (Beta) ──")
# print(result.insights[:500], "...\\n")

# print("── Short Article (Gamma) ──")
# print(result.article)

# print("\\n── JSON Report (Delta) ──")
# import json
# preview = {k: result.report[k] for k in ["report_id", "topic", "summary", "key_findings"]}
# print(json.dumps(preview, indent=2))

# print(f"\\n✅ Pipeline complete in {result.duration_seconds}s")
# if result.errors:
#     print(f"⚠️  Errors: {result.errors}")

print("Uncomment the code above and add your API keys to run the real pipeline.")
""")


# ═════════════════════════════════════════════════════════════════════════════
# CELL 24 — QUICK REFERENCE
# ═════════════════════════════════════════════════════════════════════════════
md("""\
---
## 📖 Quick Reference

### File Structure
```
D:\\Codebase\\Pinnacle\\
│
├── research_agent_system\\          ← Real production pipeline
│   ├── config.py                    ← LLM factory (Claude/OpenAI switcher)
│   ├── orchestrator.py              ← Chains Alpha→Beta→Gamma→Delta
│   ├── main.py                      ← CLI entry point
│   ├── .env                         ← Your API keys (copy from .env.example)
│   ├── agents\\
│   │   ├── alpha.py                 ← ReAct agent: searches web + OneDrive
│   │   ├── beta.py                  ← LCEL chain: extracts insights
│   │   ├── gamma.py                 ← LCEL chain: writes article + delivers
│   │   └── delta.py                 ← LCEL chain: produces JSON report
│   └── tools\\
│       ├── search.py                ← Tavily internet search tool
│       ├── onedrive.py              ← Microsoft Graph API file reader
│       ├── whatsapp.py              ← Twilio WhatsApp sender
│       └── email_tool.py            ← SendGrid email sender
│
└── demo\\                           ← Management demo (no API keys needed)
    ├── topics.txt                   ← Edit this to add research topics
    ├── run_demo.bat                 ← Double-click to start the demo
    ├── pipeline_ui.html             ← Browser UI (open in Chrome)
    └── backend\\
        ├── app.py                   ← FastAPI server
        ├── mock_runner.py           ← Fake pipeline with pre-built content
        └── pinnacleiq.db            ← SQLite database (auto-created)
```

### How to run (Windows)
```bat
# Demo (no API keys):
cd D:\\Codebase\\Pinnacle\\demo
run_demo.bat
# Then open demo\\pipeline_ui.html in Chrome

# Real pipeline (needs .env with API keys):
cd D:\\Codebase\\Pinnacle\\research_agent_system
D:\\venv\\pinnacle\\Scripts\\activate.bat
python main.py "GLP-1 receptor agonists in Type 2 Diabetes"
```

### Key LangChain 1.x Notes
| Old (LangChain 0.x) | New (LangChain 1.x / LangGraph 1.x) |
|---|---|
| `from langchain.agents import AgentExecutor` | **REMOVED** |
| `from langchain.agents import create_react_agent` | **REMOVED** |
| `from langgraph.prebuilt import create_react_agent` | ✅ Use this |
| `executor.invoke({"input": topic})["output"]` | `agent.invoke({"messages": [("human", topic)]})["messages"][-1].content` |
""")


# ═════════════════════════════════════════════════════════════════════════════
# BUILD THE NOTEBOOK
# ═════════════════════════════════════════════════════════════════════════════
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "version": "3.11.0"
        },
        "colab": {
            "provenance": [],
            "toc_visible": True,
            "name": "PinnacleIQ_Research_Pipeline.ipynb"
        }
    },
    "cells": cells
}

OUTPUT_PATH = "PinnacleIQ_Research_Pipeline.ipynb"
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"✅ Notebook created: {OUTPUT_PATH}")
print(f"   Total cells: {len(cells)}")
print(f"   Markdown cells: {sum(1 for c in cells if c['cell_type'] == 'markdown')}")
print(f"   Code cells: {sum(1 for c in cells if c['cell_type'] == 'code')}")
