"""
Pipeline Orchestrator
=====================
Chains the agent pipeline in sequence:

  Step 1 (Pre-pipeline) : get_topics_for_doctor()
                            → fetch topic from Databricks based on doctor
                              specialty / interests (falls back to passed topic)

  Step 2 (Agent Alpha)  : PubMed scraping + MA Content Library search
                            → Structured paper list with metadata
                              (title, authors, date, PMID, PubMed link, DOI, abstract)

  Step 3 (Agent Beta)   : Per-paper clinical summaries
                            → Executive summary, key findings, evidence level,
                              clinical relevance for each paper

  Step 4 (Agent Gamma)  : Shareable content writer + delivery
                            → WhatsApp/email message per paper with key points
                              and 'Read More' PubMed link

  Step 5 (Agent Delta)  : Portal content card generator
                            → Structured card stored in SQLite / Databricks
                              (awaits MA review before BU Head can share)

Each agent's FULL output is printed to console immediately after it completes.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from agents import run_alpha, run_beta, run_gamma, run_delta

logger = logging.getLogger(__name__)

# ANSI colour codes for console output (auto-disabled if not a TTY)
_USE_COLOUR = os.isatty(1) if hasattr(os, "isatty") else False
_C = {
    "reset":  "\033[0m"  if _USE_COLOUR else "",
    "bold":   "\033[1m"  if _USE_COLOUR else "",
    "cyan":   "\033[96m" if _USE_COLOUR else "",
    "green":  "\033[92m" if _USE_COLOUR else "",
    "yellow": "\033[93m" if _USE_COLOUR else "",
    "blue":   "\033[94m" if _USE_COLOUR else "",
    "red":    "\033[91m" if _USE_COLOUR else "",
    "grey":   "\033[90m" if _USE_COLOUR else "",
}


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class PipelineResult:
    """Holds all outputs from a complete pipeline run."""
    topic:            str
    specialty:        str  = ""
    therapy_area:     str  = ""
    doctor_id:        str  = ""

    # Per-agent outputs
    paper_list:       str  = ""    # Alpha  — structured paper list (PubMed + MA Library)
    summaries:        str  = ""    # Beta   — per-paper clinical summaries
    shareable_content: str = ""    # Gamma  — WhatsApp/email messages per paper
    content_card:     dict = field(default_factory=dict)   # Delta — portal card

    # Delivery status
    whatsapp_status:  dict = field(default_factory=dict)
    email_status:     dict = field(default_factory=dict)

    # Run metadata
    duration_seconds: float = 0.0
    errors:           list  = field(default_factory=list)


# ── Step 1: Topic retrieval from Databricks ───────────────────────────────────

def get_topics_for_doctor(
    specialty: str,
    doctor_id: str = "",
    therapy_area: str = "",
) -> list[str]:
    """
    Step 1: Retrieve research topics for a doctor based on their specialty
    and interests from the Databricks Unity Catalog.

    Production (DATABRICKS_HOST configured):
        Queries the `pinnacleiq.doctor_profiles.interests` table for the
        doctor's top topics ranked by relevance score.

    Demo / Databricks not configured:
        Returns the passed specialty + therapy_area as a single topic string.
        This ensures the pipeline works end-to-end without Databricks credentials.

    Args:
        specialty:    Doctor's medical specialty (e.g. "Cardiology").
        doctor_id:    Doctor's unique ID in the Databricks doctor table (optional).
        therapy_area: Therapy area of interest (e.g. "Heart Failure").

    Returns:
        List of topic strings ordered by relevance (highest first).
        Typically 1–3 topics. The orchestrator runs the pipeline for each.
    """
    # ── Try Databricks first ──────────────────────────────────────────────────
    host  = os.getenv("DATABRICKS_HOST", "")
    token = os.getenv("DATABRICKS_TOKEN", "")

    if host and token:
        try:
            topics = _fetch_topics_from_databricks(
                host, token, specialty, doctor_id, therapy_area
            )
            if topics:
                _print_step("PRE-PIPELINE", f"Retrieved {len(topics)} topic(s) from Databricks", "cyan")
                return topics
        except Exception as exc:
            logger.warning(f"Databricks topic fetch failed — using fallback: {exc}")

    # ── Fallback: build topic from specialty + therapy_area ───────────────────
    _print_step("PRE-PIPELINE", "Databricks not configured — using specialty/therapy_area as topic", "yellow")

    if specialty and therapy_area:
        topic = f"{therapy_area} in {specialty}"
    elif specialty:
        topic = specialty
    else:
        topic = "General Medicine Evidence Update"

    return [topic]


def _fetch_topics_from_databricks(
    host: str,
    token: str,
    specialty: str,
    doctor_id: str,
    therapy_area: str,
) -> list[str]:
    """
    Query the Databricks doctor_profiles table for topics matching the
    doctor's specialty/interests.

    Table schema expected:
      pinnacleiq.doctor_profiles.interests
        doctor_id    STRING
        specialty    STRING
        topic        STRING
        relevance    DOUBLE
        therapy_area STRING
    """
    try:
        from databricks import sql as dbsql  # type: ignore
    except ImportError:
        raise ImportError("databricks-sql-connector not installed")

    with dbsql.connect(
        server_hostname=host,
        http_path=os.getenv("DATABRICKS_HTTP_PATH", "/sql/1.0/warehouses/pinnacleiq"),
        access_token=token,
    ) as conn:
        with conn.cursor() as cur:
            if doctor_id:
                cur.execute(
                    """
                    SELECT topic FROM pinnacleiq.doctor_profiles.interests
                    WHERE doctor_id = ?
                    ORDER BY relevance DESC
                    LIMIT 3
                    """,
                    [doctor_id],
                )
            else:
                cur.execute(
                    """
                    SELECT DISTINCT topic FROM pinnacleiq.doctor_profiles.interests
                    WHERE specialty = ?
                    ORDER BY relevance DESC
                    LIMIT 3
                    """,
                    [specialty],
                )
            rows = cur.fetchall()
            return [row[0] for row in rows if row[0]]


# ── Main pipeline runner ──────────────────────────────────────────────────────

def run_pipeline(
    topic: str,
    specialty: str         = "General Medicine",
    therapy_area: str      = "General",
    doctor_id: str         = "",
    save_outputs: bool     = True,
    use_databricks_topics: bool = False,
) -> PipelineResult:
    """
    Execute the full research pipeline for the given topic.

    Flow:
      [Pre]  get_topics_for_doctor()       — optional Databricks topic lookup
      [1/4]  Agent Alpha  — PubMed + MA Library → paper list with metadata
      [2/4]  Agent Beta   — per-paper summaries
      [3/4]  Agent Gamma  — shareable content + WhatsApp/email delivery
      [4/4]  Agent Delta  — portal content card

    Args:
        topic:                 Research topic (used if use_databricks_topics=False).
        specialty:             Medical specialty for context + Delta categorisation.
        therapy_area:          Therapy area for context + Delta categorisation.
        doctor_id:             Doctor ID for Databricks profile lookup (optional).
        save_outputs:          Save each agent's output to ./outputs/.
        use_databricks_topics: If True, override topic with Databricks lookup.

    Returns:
        PipelineResult with all agent outputs, delivery status, and timing.
    """
    start  = time.time()
    result = PipelineResult(
        topic=topic,
        specialty=specialty,
        therapy_area=therapy_area,
        doctor_id=doctor_id,
    )
    provider = os.getenv("LLM_PROVIDER", "openrouter")

    _print_header(topic, specialty, therapy_area, provider)

    # ── Pre-pipeline: Topic retrieval from Databricks ─────────────────────────
    if use_databricks_topics:
        topics = get_topics_for_doctor(
            specialty=specialty,
            doctor_id=doctor_id,
            therapy_area=therapy_area,
        )
        # Use the top-ranked topic; future version can loop over all
        result.topic = topics[0]
        topic = result.topic
        print(f"  Topic (from Databricks): {topic}\n")
    else:
        print(f"  Topic (provided)       : {topic}\n")

    # ── Agent Alpha — Paper Discovery ─────────────────────────────────────────
    _print_agent_start(1, 4, "Alpha", "PubMed + MA Content Library → Paper List")
    try:
        result.paper_list = run_alpha(topic)
        _print_agent_complete(1, 4, "Alpha")
        _print_agent_output(result.paper_list, label="ALPHA — PAPERS FOUND")
        _save(result.paper_list, "alpha_paper_list.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Alpha: {exc}")
        _print_agent_error(1, "Alpha", exc)
        result.duration_seconds = round(time.time() - start, 1)
        return result   # Alpha is fatal — nothing to summarise without papers

    # ── Agent Beta — Per-Paper Summaries ──────────────────────────────────────
    _print_agent_start(2, 4, "Beta", "Per-paper clinical summaries")
    try:
        result.summaries = run_beta(paper_list=result.paper_list, topic=topic)
        _print_agent_complete(2, 4, "Beta")
        _print_agent_output(result.summaries, label="BETA — PAPER SUMMARIES")
        _save(result.summaries, "beta_summaries.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Beta: {exc}")
        _print_agent_error(2, "Beta", exc)
        result.duration_seconds = round(time.time() - start, 1)
        return result   # Beta is fatal — no summaries to format or share

    # ── Agent Gamma — Shareable Content + Delivery ────────────────────────────
    _print_agent_start(3, 4, "Gamma", "Shareable content per paper + WhatsApp/Email delivery")
    try:
        gamma_out = run_gamma(
            topic=topic,
            paper_list=result.paper_list,
            summaries=result.summaries,
        )
        result.shareable_content  = gamma_out["content"]
        result.whatsapp_status    = gamma_out["whatsapp_status"]
        result.email_status       = gamma_out["email_status"]
        _print_agent_complete(3, 4, "Gamma")
        _print_agent_output(result.shareable_content, label="GAMMA — SHAREABLE CONTENT")
        _print_delivery_status(result.whatsapp_status, result.email_status)
        _save(result.shareable_content, "gamma_shareable_content.txt", save_outputs)
    except Exception as exc:
        result.errors.append(f"Gamma: {exc}")
        _print_agent_error(3, "Gamma", exc)
        # Non-fatal — Delta can still produce the portal card

    # ── Agent Delta — Portal Content Card ─────────────────────────────────────
    _print_agent_start(4, 4, "Delta", "Portal content card for Pinnacle")
    try:
        result.content_card = run_delta(
            topic=topic,
            specialty=specialty,
            therapy_area=therapy_area,
            insights=result.summaries,          # Beta's summaries feed Delta
            article=result.shareable_content,   # Gamma's content feeds Delta
            llm_provider=provider,
        )
        _print_agent_complete(4, 4, "Delta")
        _print_delta_output(result.content_card)
        _save(
            json.dumps(result.content_card, indent=2),
            "delta_content_card.json",
            save_outputs,
        )
    except Exception as exc:
        result.errors.append(f"Delta: {exc}")
        _print_agent_error(4, "Delta", exc)

    result.duration_seconds = round(time.time() - start, 1)
    _print_footer(result)
    return result


# ── Console output helpers ─────────────────────────────────────────────────────

def _print_header(topic: str, specialty: str, therapy_area: str, provider: str) -> None:
    w = 70
    print(f"\n{'═' * w}")
    print(f"  {_C['bold']}{_C['cyan']}PINNACLE RESEARCH PIPELINE{_C['reset']}")
    print(f"  Topic        : {topic}")
    print(f"  Specialty    : {specialty}")
    print(f"  Therapy Area : {therapy_area}")
    print(f"  LLM Provider : {provider.upper()}")
    print(f"  Start        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'═' * w}\n")


def _print_agent_start(step: int, total: int, name: str, desc: str) -> None:
    print(f"{_C['bold']}{_C['blue']}[{step}/{total}] Agent {name}{_C['reset']} — {desc}")
    print(f"       Running...\n")


def _print_agent_complete(step: int, total: int, name: str) -> None:
    print(f"  {_C['green']}✓ Agent {name} complete{_C['reset']}\n")


def _print_agent_error(step: int, name: str, exc: Exception) -> None:
    print(f"  {_C['red']}✗ Agent {name} ERROR: {exc}{_C['reset']}\n")


def _print_step(label: str, msg: str, colour: str = "grey") -> None:
    c = _C.get(colour, "")
    print(f"  {c}[{label}]{_C['reset']} {msg}")


def _print_agent_output(content: str, label: str = "OUTPUT") -> None:
    """Print an agent's full output with clear section boundaries."""
    w   = 70
    sep = "─" * w
    print(f"\n{sep}")
    print(f"  {_C['bold']}{_C['yellow']}◀ {label} ▶{_C['reset']}")
    print(sep)
    print(content)
    print(f"{sep}\n")


def _print_delivery_status(wa: dict, email: dict) -> None:
    wa_ok    = wa.get("status") not in (None, "error", "failed")
    email_ok = email.get("status") not in (None, "error", "failed")
    wa_icon    = "✓" if wa_ok    else "✗ (check Twilio credentials)"
    email_icon = "✓" if email_ok else "✗ (check SendGrid credentials)"
    print(f"  Delivery → WhatsApp: {_C['green'] if wa_ok else _C['red']}{wa_icon}{_C['reset']}  "
          f"Email: {_C['green'] if email_ok else _C['red']}{email_icon}{_C['reset']}\n")


def _print_delta_output(card: dict) -> None:
    """Print a compact preview of the Delta portal content card."""
    if not card:
        return
    preview_keys = ["id", "title", "specialty", "therapy_area", "sub_category",
                    "tags", "summary", "evidence_quality", "status"]
    preview = {k: card[k] for k in preview_keys if k in card}
    w = 70
    sep = "─" * w
    print(f"\n{sep}")
    print(f"  {_C['bold']}{_C['yellow']}◀ DELTA — PORTAL CONTENT CARD ▶{_C['reset']}")
    print(sep)
    print(json.dumps(preview, indent=2))
    print(f"{sep}\n")


def _print_footer(result: PipelineResult) -> None:
    w = 70
    papers_line = ""
    if result.paper_list:
        # Count papers by looking for "### PAPER" headers in Alpha's output
        import re
        count = len(re.findall(r"###\s+PAPER\s+\d+", result.paper_list))
        papers_line = f"\n  Papers Discovered : {count}" if count else ""

    print(f"{'═' * w}")
    print(f"  {_C['bold']}{_C['green']}Pipeline complete in {result.duration_seconds}s{_C['reset']}")
    print(f"  Topic            : {result.topic}{papers_line}")
    if result.errors:
        print(f"  {_C['red']}Errors            : {result.errors}{_C['reset']}")
    print(f"{'═' * w}\n")


# ── File output ───────────────────────────────────────────────────────────────

def _save(content: str, filename: str, enabled: bool) -> None:
    """Save content to ./outputs/<filename>. No-op if enabled=False."""
    if not enabled:
        return
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    {_C['grey']}Saved → {path}{_C['reset']}")
