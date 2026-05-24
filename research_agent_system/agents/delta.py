"""
Agent Delta — Pinnacle Content Card Generator

Delta's ONLY job: take all pipeline outputs and produce a PinnacleContentCard
that maps exactly 1:1 to what the portal stores and displays.

Key design principle:
  Delta is the final formatter. Its output schema IS the portal schema.
  Zero transformation should be needed between Delta's output and the portal DB.

What Delta does NOT do:
  - It does not re-research or re-analyse (that's Alpha + Beta)
  - It does not write articles (that's Gamma)
  - It does not produce a generic "report" — it produces a portal content card

Flow:
  topic + specialty + therapy_area  (pipeline metadata)
  + Beta insights                   (structured findings)
  + Gamma article                   (short doctor article)
  ─────────────────────────────────────────────────────
  → PinnacleContentCard             (exactly what the portal stores)
  → POST to portal API              (optional, if PINNACLE_API_URL is set)
"""

import os
import uuid
from datetime import datetime, timezone
from typing import List

import requests
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from config import get_llm


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic model — this IS the portal content card schema.
# Every field here corresponds directly to a column in the portal's DB
# and a component in the portal UI.
# ─────────────────────────────────────────────────────────────────────────────

class PinnacleContentCard(BaseModel):
    """
    The exact data shape the Pinnacle portal stores and displays.
    MA reviews this card → approves → BU Head shares with doctors.
    """

    # ── Card header ──────────────────────────────────────────────────────────
    title: str = Field(
        description="Compelling article title (max 15 words). "
                    "E.g. 'GLP-1 Receptor Agonists in T2DM: 2025 Real-World Evidence Update'"
    )

    # ── Categorisation (for portal filters and search) ────────────────────────
    specialty: str = Field(
        description="Medical specialty. E.g. 'Diabetology', 'Cardiology', 'Gynaecology'"
    )
    therapy_area: str = Field(
        description="Specific therapy area. E.g. 'GLP-1 Therapy', 'Heart Failure', 'PCOS'"
    )
    sub_category: str = Field(
        description="Evidence type. One of: 'Meta-Analysis / Systematic Review', "
                    "'Clinical Trial / RCT', 'Observational Study', 'Review Article', "
                    "'Expert Opinion / Guidelines', 'Case Series'"
    )
    tags: List[str] = Field(
        description="3-7 short keyword tags shown as chips on the portal card. "
                    "E.g. ['GLP-1', 'Semaglutide', 'T2DM', 'Indian Population', '2025 Guidelines']"
    )

    # ── Content sections (rendered as UI components in the portal) ────────────
    summary: str = Field(
        description="2-3 sentence executive summary. Written for a busy doctor. "
                    "Include the most important statistic or finding."
    )
    key_findings: List[str] = Field(
        description="4-6 specific bullet-point findings. Each must include numbers/data "
                    "where available. E.g. 'Semaglutide 1mg weekly reduces HbA1c by 1.8% at 52 weeks'"
    )
    clinical_insights: str = Field(
        description="1-2 paragraph practical takeaway for the doctor's daily practice. "
                    "What should they DO differently after reading this?"
    )
    recommendations: List[str] = Field(
        description="3-5 specific, actionable clinical recommendations as bullet points. "
                    "Start each with a verb: 'Initiate...', 'Monitor...', 'Consider...'"
    )
    emerging_trends: List[str] = Field(
        description="2-4 bullet points on pipeline drugs, upcoming trials, or guideline changes "
                    "in this area. Gives doctors a 'what's coming next' view."
    )
    evidence_quality: str = Field(
        description="One sentence on evidence strength and recency. "
                    "E.g. 'High — 34 RCTs, 3 Indian cohort studies, 2025 ADA/EASD guidelines.'"
    )

    # ── Doctor-facing article (what gets sent via WhatsApp/email) ────────────
    # This comes directly from Gamma — Delta does NOT rewrite it.
    short_article: str = Field(
        description="The WhatsApp/email article written by Agent Gamma. "
                    "Passed through as-is — do not rewrite."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Prompt — asks the LLM to populate the card fields
# The short_article is NOT extracted by the LLM — it's passed in from Gamma
# ─────────────────────────────────────────────────────────────────────────────

_DELTA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are Agent Delta. Your job is to populate a Pinnacle portal content card
from the research pipeline outputs.

Return a single valid JSON object with EXACTLY these fields:

{{
  "title":             "string — compelling article title, max 15 words",
  "sub_category":      "string — one of: Meta-Analysis / Systematic Review | Clinical Trial / RCT | Observational Study | Review Article | Expert Opinion / Guidelines | Case Series",
  "tags":              ["string", ...],
  "summary":           "string — 2-3 sentence executive summary with key statistic",
  "key_findings":      ["string", ...],
  "clinical_insights": "string — practical takeaway paragraph for the doctor",
  "recommendations":   ["string", ...],
  "emerging_trends":   ["string", ...],
  "evidence_quality":  "string — one sentence on evidence strength and recency"
}}

RULES:
- Return ONLY raw JSON. No markdown fences, no explanation, nothing else.
- specialty and therapy_area are provided separately — do NOT include them in the JSON.
- short_article is provided separately — do NOT include it in the JSON.
- key_findings: include actual numbers and percentages from the research.
- recommendations: each must start with an action verb (Initiate, Monitor, Consider, etc.)
- tags: 3-7 short keywords relevant to the topic (drug names, conditions, study types).
"""),
    ("human", """\
Topic: {topic}
Specialty: {specialty}
Therapy Area: {therapy_area}

=== Agent Beta Insights Report ===
{insights}

=== Agent Gamma Short Article ===
{article}
"""),
])


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def run_delta(
    topic: str,
    specialty: str,
    therapy_area: str,
    insights: str,       # from Agent Beta
    article: str,        # from Agent Gamma — passed through unchanged
    llm_provider: str = "openrouter",
) -> dict:
    """
    Run Agent Delta: build a PinnacleContentCard and optionally POST to portal.

    Args:
        topic:        The research topic string.
        specialty:    Medical specialty (e.g. 'Diabetology').
        therapy_area: Therapy area (e.g. 'GLP-1 Therapy').
        insights:     Structured insights text from Agent Beta.
        article:      Short doctor article from Agent Gamma (passed through as-is).
        llm_provider: Which LLM was used (stored in metadata).

    Returns:
        dict matching PinnacleContentCard schema + portal metadata fields.
    """
    # Temperature = 0.0 — Delta must produce exact, consistent JSON
    llm = get_llm(temperature=0.0)
    chain = _DELTA_PROMPT | llm | JsonOutputParser()

    # LLM extracts/generates the content-specific fields
    extracted = chain.invoke({
        "topic":        topic,
        "specialty":    specialty,
        "therapy_area": therapy_area,
        "insights":     insights,
        "article":      article,
    })

    # Build the complete card — combining LLM output with pipeline metadata
    card = {
        # ── Portal metadata (not LLM-generated) ──────────────────────────────
        "id":           str(uuid.uuid4()),
        "created_at":   datetime.now(timezone.utc).isoformat(),
        "status":       "pending_review",    # MA must approve before sharing
        "source":       "ai_agent",
        "llm_provider": llm_provider,
        "pipeline":     "Alpha→Beta→Gamma→Delta",

        # ── Categorisation (specialty + therapy_area from pipeline input) ─────
        "topic":        topic,
        "specialty":    specialty,           # passed from pipeline, not LLM
        "therapy_area": therapy_area,        # passed from pipeline, not LLM
        "sub_category": extracted.get("sub_category", "Review Article"),
        "tags":         extracted.get("tags", []),

        # ── Content sections (LLM-extracted from Beta insights) ───────────────
        "title":             extracted.get("title", f"{topic}: 2025 Evidence Update"),
        "summary":           extracted.get("summary", ""),
        "key_findings":      extracted.get("key_findings", []),
        "clinical_insights": extracted.get("clinical_insights", ""),
        "recommendations":   extracted.get("recommendations", []),
        "emerging_trends":   extracted.get("emerging_trends", []),
        "evidence_quality":  extracted.get("evidence_quality", ""),

        # ── Doctor-facing article (from Gamma, untouched) ─────────────────────
        "short_article": article,
    }

    # Validate against Pydantic model (raises ValidationError if schema is wrong)
    try:
        PinnacleContentCard(**{k: card[k] for k in PinnacleContentCard.model_fields})
        print("[Delta] Card schema validated ✓")
    except Exception as exc:
        print(f"[Delta] Warning — card schema validation failed: {exc}")

    # ── Persist via store (SQLite for demo, Databricks for production) ───────
    _save_to_store(card)

    # ── Also POST to portal API if configured ─────────────────────────────────
    _post_to_portal(card)

    return card


# ─────────────────────────────────────────────────────────────────────────────
# Storage: Databricks Delta Lake
# ─────────────────────────────────────────────────────────────────────────────

def _save_to_store(card: dict) -> None:
    """
    Save the content card using whichever backend is configured.

    Reads STORE_BACKEND env var via get_store() factory:
      STORE_BACKEND=sqlite       → saves to local SQLite file (demo default)
      STORE_BACKEND=databricks   → saves to Azure Databricks Delta Lake (production)

    No code change needed when switching backends — just change the env var.
    """
    try:
        from store import get_store
        store = get_store()
        store.setup()                       # idempotent — creates tables if needed
        content_id = store.save_content_card(card)
        backend = __import__("os").getenv("STORE_BACKEND", "sqlite")
        print(f"[Delta] ✓ Content card saved to {backend.upper()} → id: {content_id}")
    except Exception as exc:
        # Non-fatal — pipeline output still returned even if storage fails
        print(f"[Delta] Warning — store save failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# Storage: Pinnacle Portal API (optional, secondary)
# ─────────────────────────────────────────────────────────────────────────────

def _post_to_portal(card: dict) -> None:
    """
    POST the content card to the Pinnacle portal API.
    If PINNACLE_API_URL is not set, skips silently (useful for local dev/testing).

    Note: When the production portal's .NET backend reads from Databricks directly,
    this POST becomes unnecessary. Keep it for now during the demo/transition phase.
    """
    url = os.getenv("PINNACLE_API_URL")
    api_key = os.getenv("PINNACLE_API_KEY")

    if not url:
        print("[Delta] PINNACLE_API_URL not set — skipping portal POST.")
        return

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        r = requests.post(url, json=card, headers=headers, timeout=30)
        r.raise_for_status()
        print(f"[Delta] Content card posted to Pinnacle portal. HTTP {r.status_code}")
    except Exception as exc:
        # Non-fatal — pipeline shouldn't crash just because the portal is unavailable
        print(f"[Delta] Warning — could not post to Pinnacle portal: {exc}")
