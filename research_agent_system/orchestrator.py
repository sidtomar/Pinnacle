"""
Pipeline Orchestrator

Chains Alpha → Beta → Gamma → Delta in sequence,
passing outputs downstream at each stage.
"""
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime

from agents import run_alpha, run_beta, run_gamma, run_delta


@dataclass
class PipelineResult:
    topic: str
    research_article: str = ""
    insights: str = ""
    article: str = ""
    report: dict = field(default_factory=dict)
    whatsapp_status: dict = field(default_factory=dict)
    email_status: dict = field(default_factory=dict)
    duration_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)


def run_pipeline(topic: str, save_outputs: bool = True) -> PipelineResult:
    """
    Execute the full 4-agent research pipeline for the given topic.

    Args:
        topic: The research topic or keywords to investigate.
        save_outputs: If True, save each agent's output to ./outputs/.

    Returns:
        PipelineResult with all agent outputs and delivery status.
    """
    start = time.time()
    result = PipelineResult(topic=topic)
    provider = os.getenv("LLM_PROVIDER", "claude")

    print(f"\n{'='*60}")
    print(f"  PINNACLE RESEARCH PIPELINE")
    print(f"  Topic : {topic}")
    print(f"  LLM   : {provider.upper()}")
    print(f"  Start : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # ── Agent Alpha ───────────────────────────────────────────────
    print("[1/4] Agent Alpha — Researching...")
    try:
        result.research_article = run_alpha(topic)
        print("[1/4] Alpha complete.\n")
        _save(result.research_article, "alpha_research.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Alpha: {exc}")
        print(f"[1/4] Alpha ERROR: {exc}\n")
        result.duration_seconds = time.time() - start
        return result

    # ── Agent Beta ────────────────────────────────────────────────
    print("[2/4] Agent Beta — Generating insights...")
    try:
        result.insights = run_beta(result.research_article)
        print("[2/4] Beta complete.\n")
        _save(result.insights, "beta_insights.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Beta: {exc}")
        print(f"[2/4] Beta ERROR: {exc}\n")
        result.duration_seconds = time.time() - start
        return result

    # ── Agent Gamma ───────────────────────────────────────────────
    print("[3/4] Agent Gamma — Writing article and delivering...")
    try:
        gamma_out = run_gamma(topic=topic, insights=result.insights)
        result.article = gamma_out["article"]
        result.whatsapp_status = gamma_out["whatsapp_status"]
        result.email_status = gamma_out["email_status"]
        print("[3/4] Gamma complete.\n")
        _save(result.article, "gamma_article.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Gamma: {exc}")
        print(f"[3/4] Gamma ERROR: {exc}\n")

    # ── Agent Delta ───────────────────────────────────────────────
    print("[4/4] Agent Delta — Generating JSON report...")
    try:
        result.report = run_delta(
            topic=topic,
            research_article=result.research_article,
            insights=result.insights,
            article=result.article,
            llm_provider=provider,
        )
        print("[4/4] Delta complete.\n")
        _save(json.dumps(result.report, indent=2), "delta_report.json", save_outputs)
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
    if not enabled:
        return
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    Saved → {path}")
