"""
Agent Delta — JSON Report Generator for Pinnacle Portal

Takes all upstream outputs and produces a structured JSON report
that can be consumed by the Pinnacle portal API.
"""
import json
import os
import uuid
from datetime import datetime, timezone

import requests
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import get_llm

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are Agent Delta. Extract structured data from research documents and return
a single valid JSON object matching EXACTLY this schema:

{{
  "summary": "string — one paragraph executive summary",
  "key_findings": ["string", ...],
  "clinical_insights": ["string", ...],
  "recommendations": ["string", ...],
  "emerging_trends": ["string", ...],
  "evidence_quality": "string",
  "sources_used": ["string description of each source", ...]
}}

Return ONLY the raw JSON object. No markdown, no code fences, no explanation.
"""),
    ("human", """
Topic: {topic}

Insights Report:
{insights}

Short Article:
{article}
"""),
])


def run_delta(
    topic: str,
    research_article: str,
    insights: str,
    article: str,
    llm_provider: str = "claude",
) -> dict:
    """
    Run Agent Delta: produce and optionally POST a Pinnacle JSON report.
    Returns the full report dict.
    """
    llm = get_llm(temperature=0.0)
    chain = _PROMPT | llm | JsonOutputParser()

    extracted = chain.invoke({
        "topic": topic,
        "insights": insights,
        "article": article,
    })

    report = {
        "report_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "summary": extracted.get("summary", ""),
        "key_findings": extracted.get("key_findings", []),
        "clinical_insights": extracted.get("clinical_insights", []),
        "recommendations": extracted.get("recommendations", []),
        "emerging_trends": extracted.get("emerging_trends", []),
        "short_article": article,
        "evidence_quality": extracted.get("evidence_quality", ""),
        "sources_used": extracted.get("sources_used", []),
        "full_research_article": research_article,
        "metadata": {
            "agent_version": "1.0.0",
            "llm_provider": llm_provider,
            "pipeline": "Alpha→Beta→Gamma→Delta",
        },
    }

    _post_to_portal(report)
    return report


def _post_to_portal(report: dict) -> None:
    """POST the report to the Pinnacle portal if configured."""
    url = os.getenv("PINNACLE_API_URL")
    api_key = os.getenv("PINNACLE_API_KEY")
    if not url:
        return

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        r = requests.post(url, json=report, headers=headers, timeout=30)
        r.raise_for_status()
        print(f"[Delta] Report posted to Pinnacle portal: {r.status_code}")
    except Exception as exc:
        print(f"[Delta] Warning — could not post to Pinnacle portal: {exc}")
