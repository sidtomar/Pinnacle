# 🏥 PinnacleIQ — Multi-Agent Medical Research Pipeline
### Mankind Pharma · AI-Powered Content Engine

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sidtomar/Pinnacle/blob/main/PinnacleIQ_Research_Pipeline.ipynb)

---

## 📁 Repository Structure

```
Pinnacle/
│
├── 📓 PinnacleIQ_Research_Pipeline.ipynb   ← Annotated Colab notebook (start here)
├── 📄 generate_notebook.py                 ← Script that builds the notebook
├── 🌐 pinnacleiq_v13.html                  ← Portal UI design (open in browser)
│
├── research_agent_system/                  ← ✅ Production 4-agent pipeline
│   ├── config.py                           ← LLM factory (OpenRouter / Claude / OpenAI)
│   ├── orchestrator.py                     ← Chains Alpha → Beta → Gamma → Delta
│   ├── main.py                             ← CLI entry point
│   ├── run.bat                             ← Windows launcher
│   ├── requirements.txt                    ← Python dependencies
│   ├── .env.example                        ← Copy to .env and fill in your keys
│   ├── agents/
│   │   ├── alpha.py                        ← ReAct agent: web search + OneDrive
│   │   ├── beta.py                         ← LCEL chain: insights extractor
│   │   ├── gamma.py                        ← LCEL chain: article writer + delivery
│   │   └── delta.py                        ← LCEL chain: JSON report generator
│   └── tools/
│       ├── search.py                       ← Tavily internet search
│       ├── onedrive.py                     ← Microsoft Graph API file reader
│       ├── whatsapp.py                     ← Twilio WhatsApp sender
│       └── email_tool.py                   ← SendGrid email sender
│
└── demo/                                   ← 🎬 Management demo (no API keys needed)
    ├── topics.txt                           ← Edit to add research topics
    ├── run_demo.bat                         ← Double-click to start demo
    ├── pipeline_ui.html                     ← Browser UI
    └── backend/
        ├── app.py                           ← FastAPI REST server
        └── mock_runner.py                   ← Pre-built content, simulated delays
```

---

## 🗺️ System Architecture

```
topics.txt  →  Orchestrator  →  Agent Alpha  (search web + OneDrive)
                                     ↓
                               Agent Beta   (extract insights)
                                     ↓
                               Agent Gamma  (write article + send WA/email)
                                     ↓
                               Agent Delta  (JSON report → Pinnacle Portal)
```

---

## ⚡ Quick Start

### Option A — Colab (no setup needed)
Click the **Open in Colab** badge above. Jump to **Part 7** for a live demo with no API keys.

### Option B — VS Code (local)

#### 1. Clone the repo
```bash
git clone https://github.com/sidtomar/Pinnacle.git
cd Pinnacle
```

#### 2. Create & activate virtual environment
```bash
# Windows
python -m venv D:\venv\pinnacle
D:\venv\pinnacle\Scripts\activate.bat

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r research_agent_system/requirements.txt
```

#### 4. Configure API keys
```bash
cd research_agent_system
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
```
Open `.env` and fill in at minimum:
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here       # https://openrouter.ai/keys
OPENROUTER_MODEL=anthropic/claude-sonnet-4-5
TAVILY_API_KEY=your_key_here           # https://app.tavily.com
```

#### 5. Run the pipeline
```bash
python main.py "GLP-1 receptor agonists in Type 2 Diabetes"
```

---

## 🎬 Management Demo (No API Keys)

```bash
cd demo
run_demo.bat          # starts FastAPI server on http://localhost:8000
```
Then open `demo/pipeline_ui.html` in Chrome.

---

## 🔑 API Keys Reference

| Key | Required | Get it at |
|-----|----------|-----------|
| `OPENROUTER_API_KEY` | ✅ Yes | https://openrouter.ai/keys |
| `TAVILY_API_KEY` | ✅ Yes | https://app.tavily.com |
| `ONEDRIVE_CLIENT_ID/SECRET/TENANT_ID` | Optional | Azure App Registration |
| `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` | Optional | https://console.twilio.com |
| `SENDGRID_API_KEY` | Optional | https://app.sendgrid.com |

---

## 🤖 Switching Models (OpenRouter)

Change one line in `.env` — no code changes needed:

```env
OPENROUTER_MODEL=anthropic/claude-sonnet-4-5    # Claude (default)
OPENROUTER_MODEL=openai/gpt-4o                  # GPT-4o
OPENROUTER_MODEL=google/gemini-pro-1.5           # Gemini Pro
OPENROUTER_MODEL=google/gemini-flash-1.5         # Gemini Flash (fast + cheap)
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct  # Llama 3.1
OPENROUTER_MODEL=deepseek/deepseek-r1            # DeepSeek R1
OPENROUTER_MODEL=mistralai/mistral-large         # Mistral Large
```

Full model list: https://openrouter.ai/models

---

## 🧪 Testing

```bash
# Verify backend is live
curl http://localhost:8000/

# List research topics
curl http://localhost:8000/topics

# Interactive API docs (test approve/reject/share in browser)
open http://localhost:8000/docs
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent framework | LangGraph 1.x (`create_react_agent`) |
| LLM routing | OpenRouter (OpenAI-compatible API) |
| Web search | Tavily |
| Document reading | Microsoft Graph API + MSAL |
| WhatsApp | Twilio |
| Email | SendGrid |
| Demo API | FastAPI + SQLite |
| Demo UI | Vanilla HTML/CSS/JS |

---

## 👥 Roles in the Portal

| Role | Responsibility |
|------|----------------|
| **Medical Affairs (MA)** | Reviews AI-generated content → Approve / Reject |
| **BU Head (PMT)** | Shares approved content with Pinnacle doctors via WhatsApp/email |
