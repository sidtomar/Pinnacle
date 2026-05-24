"""
Pipeline Orchestrator

Chains Alpha → Beta → Gamma → Delta in sequence,
passing outputs downstream at each stage.

Each agent receives exactly what it needs:
  Alpha  : topic
  Beta   : Alpha's research article
  Gamma  : topic + Beta's insights
  Delta  : topic + specialty + therapy_area + Beta's insights + Gamma's article
"""
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime

from agents import run_alpha, run_beta, run_gamma, run_delta


@dataclass
class PipelineResult:
    """Holds all outputs from a complete pipeline run."""
    topic:            str
    specialty:        str = ""
    therapy_area:     str = ""
    research_article: str = ""    # Alpha output
    insights:         str = ""    # Beta output
    article:          str = ""    # Gamma output
    content_card:     dict = field(default_factory=dict)   # Delta output (portal card)
    whatsapp_status:  dict = field(default_factory=dict)
    email_status:     dict = field(default_factory=dict)
    duration_seconds: float = 0.0
    errors:           list = field(default_factory=list)


def run_pipeline(
    topic: str,
    specialty: str = "General Medicine",
    therapy_area: str = "General",
    save_outputs: bool = True,
) -> PipelineResult:
    """
    Execute the full 4-agent research pipeline for the given topic.

    Args:
        topic:        The research topic or keywords to investigate.
        specialty:    Medical specialty (e.g. 'Diabetology'). Used by Delta
                      to correctly categorise the portal content card.
        therapy_area: Therapy area (e.g. 'GLP-1 Therapy'). Used by Delta.
        save_outputs: If True, save each agent's output to ./outputs/.

    Returns:
        PipelineResult with all agent outputs and delivery status.
    """
    start = time.time()
    result = PipelineResult(topic=topic, specialty=specialty, therapy_area=therapy_area)
    provider = os.getenv("LLM_PROVIDER", "openrouter")

    print(f"\n{'='*60}")
    print(f"  PINNACLE RESEARCH PIPELINE")
    print(f"  Topic        : {topic}")
    print(f"  Specialty    : {specialty}")
    print(f"  Therapy Area : {therapy_area}")
    print(f"  LLM Provider : {provider.upper()}")
    print(f"  Start        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # ── Agent Alpha — Research ────────────────────────────────────────────────
    # Input : topic string
    # Output: structured markdown research article (~1000 words)
    print("[1/4] Agent Alpha — Researching...")
    try:
        result.research_article = run_alpha(topic)
        print("[1/4] Alpha complete.\n")
        _save(result.research_article, "alpha_research.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Alpha: {exc}")
        print(f"[1/4] Alpha ERROR: {exc}\n")
        result.duration_seconds = time.time() - start
        return result   # Alpha failure is fatal — nothing to pass downstream

    # ── Agent Beta — Insights ─────────────────────────────────────────────────
    # Input : Alpha's research article
    # Output: structured insights (Executive Summary, Key Findings, Recommendations...)
    print("[2/4] Agent Beta — Generating insights...")
    try:
        result.insights = run_beta(result.research_article)
        print("[2/4] Beta complete.\n")
        _save(result.insights, "beta_insights.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Beta: {exc}")
        print(f"[2/4] Beta ERROR: {exc}\n")
        result.duration_seconds = time.time() - start
        return result   # Beta failure is fatal — no insights for Gamma/Delta

    # ── Agent Gamma — Article Writing & Delivery ──────────────────────────────
    # Input : topic + Beta's insights
    # Output: short plain-text article + HTML version → sent via WhatsApp + email
    print("[3/4] Agent Gamma — Writing article and delivering...")
    try:
        gamma_out = run_gamma(topic=topic, insights=result.insights)
        result.article         = gamma_out["article"]
        result.whatsapp_status = gamma_out["whatsapp_status"]
        result.email_status    = gamma_out["email_status"]
        print("[3/4] Gamma complete.\n")
        _save(result.article, "gamma_article.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Gamma: {exc}")
        print(f"[3/4] Gamma ERROR: {exc}\n")
        # Non-fatal: Delta can still produce the portal card without the article

    # ── Agent Delta — Portal Content Card ────────────────────────────────────
    # Input : topic + specialty + therapy_area + Beta insights + Gamma article
    # Output: PinnacleContentCard dict (1:1 with portal DB schema)
    print("[4/4] Agent Delta — Building Pinnacle content card...")
    try:
        result.content_card = run_delta(
            topic=topic,
            specialty=specialty,
            therapy_area=therapy_area,
            insights=result.insights,
            article=result.article,
            llm_provider=provider,
        )
        print("[4/4] Delta complete.\n")
        _save(json.dumps(result.content_card, indent=2), "delta_content_card.json", save_outputs)
    except Exception as exc:
        result.errors.append(f"Delta: {exc}")
        print(f"[4/4] Delta ERROR: {exc}\n")

    result.duration_seconds = round(time.time() - start, 1)

    print(f"{'='*60}")
    print(f"  Pipeline complete in {result.duration_seconds}s")
    if result.errors:
        print(f"  Errors: {result.errors}")
    print(f"{'='*60}\n")

    return result


def _save(content: str, filename: str, enabled: bool) -> None:
    """Save content to ./outputs/<filename>. No-op if enabled=False."""
    if not enabled:
        return
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    Saved → {path}")
