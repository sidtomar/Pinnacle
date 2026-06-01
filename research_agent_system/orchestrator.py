"""
Pipeline Orchestrator
=====================
Chains the 3-agent research pipeline in sequence:

  Input (Pre-pipeline)  : Topic from topics.txt (demo) or Databricks (production)
                            → keyword based on doctor specialization / interests

  Step 1 (Agent Alpha)  : Search PubMed for the BEST paper matching the topic
                            → Also checks local MA Content Library (Azure/Databricks)
                            → Returns single best paper with metadata + PubMed link

  Step 2 (Agent Beta)   : Summarise the paper into a presentable article
                            → Key findings, statistics, clinical relevance
                            → Includes "Read More" link to original PubMed article

  Step 3 (Agent Gamma)  : Write a 200-500 word article from the summary
                            → Polished, doctor-ready content
                            → Submitted for Medical Affairs team review
                            → Status: "Pending Review" until MA approves

  Post (Agent Delta)    : Generate portal content card (auto)
                            → Stored in SQLite / Databricks for the portal

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

    # Alpha output — raw text + parsed list of paper dicts
    paper_list:       str  = ""    # Alpha raw output
    papers:           list = field(default_factory=list)  # parsed list of paper dicts

    # Per-paper outputs (parallel lists — index-matched)
    summaries:        list = field(default_factory=list)   # Beta outputs (one per paper)
    articles:         list = field(default_factory=list)   # Gamma outputs (one per paper)
    content_cards:    list = field(default_factory=list)   # Delta outputs (one per paper)

    # Legacy single-card field (last card, for backward compatibility)
    shareable_content: str  = ""
    content_card:      dict = field(default_factory=dict)

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

    from agents.alpha import parse_alpha_papers

    # ── Agent Alpha — Find ALL papers for topic ──────────────────────────────
    _print_agent_start(1, 3, "Alpha", "PubMed search → Find ALL papers for topic")
    try:
        result.paper_list = run_alpha(topic)
        result.papers     = parse_alpha_papers(result.paper_list)
        _print_agent_complete(1, 3, "Alpha")
        _print_agent_output(
            result.paper_list,
            label=f"ALPHA — {len(result.papers)} PAPER(S) FOUND"
        )
        _save(result.paper_list, "alpha_papers.txt", save_outputs)
        if not result.papers:
            result.errors.append("Alpha: no papers parsed from output")
            result.duration_seconds = round(time.time() - start, 1)
            return result
    except Exception as exc:
        result.errors.append(f"Alpha: {exc}")
        _print_agent_error(1, "Alpha", exc)
        result.duration_seconds = round(time.time() - start, 1)
        return result

    n_papers = len(result.papers)
    print(f"  {_C['cyan']}Processing {n_papers} paper(s) individually through Beta → Gamma → Delta{_C['reset']}\n")

    # ── Per-Paper Loop: Beta → Gamma → Delta ─────────────────────────────────
    for idx, paper in enumerate(result.papers, 1):
        paper_label = f"Paper {idx}/{n_papers}: {paper.get('title','')[:60]}..."
        print(f"\n{_C['bold']}{'─'*70}{_C['reset']}")
        print(f"  {_C['bold']}{_C['yellow']}PROCESSING {paper_label}{_C['reset']}\n")

        # Format this paper as text for Beta/Gamma
        paper_text = "\n".join([
            f"Title    : {paper.get('title', '')}",
            f"Authors  : {paper.get('authors', '')}",
            f"Journal  : {paper.get('journal', '')}",
            f"Published: {paper.get('published', '')}",
            f"PMID     : {paper.get('pmid', '')}",
            f"Link     : {paper.get('pubmed_link', paper.get('link', ''))}",
            f"DOI      : {paper.get('doi', 'N/A')}",
            f"Source   : {paper.get('source', 'PubMed')}",
            f"Abstract : {paper.get('abstract', '')}",
        ])

        # ── Beta: Summarise this paper (with retry) ─────────────────────────
        _print_agent_start(2, 3, "Beta", f"Summarising paper {idx}/{n_papers}")
        beta_out = ""
        beta_ok = False
        for attempt in range(3):
            try:
                beta_out = run_beta(paper_list=paper_text, topic=topic)
                beta_ok = True
                break
            except Exception as exc:
                print(f"  {_C['yellow']}Beta attempt {attempt+1}/3 failed: {exc}{_C['reset']}")
                if attempt < 2:
                    time.sleep(3)
        if beta_ok:
            result.summaries.append(beta_out)
            _print_agent_complete(2, 3, "Beta")
            _print_agent_output(beta_out, label=f"BETA — SUMMARY {idx}/{n_papers}")
            _save(beta_out, f"beta_summary_paper{idx}.txt", save_outputs)
        else:
            result.errors.append(f"Beta[paper {idx}]: failed after 3 attempts")
            _print_agent_error(2, "Beta", Exception("failed after 3 attempts"))
            result.summaries.append("")
            result.articles.append("")
            result.content_cards.append({})
            continue   # skip Gamma + Delta for this paper if Beta fails

        # ── Gamma: Write article for this paper (with retry) ────────────────
        _print_agent_start(3, 3, "Gamma", f"Writing article for paper {idx}/{n_papers}")
        gamma_out = {}
        gamma_ok = False
        for attempt in range(3):
            try:
                gamma_out = run_gamma(
                    topic=topic,
                    paper_list=paper_text,
                    summaries=beta_out,
                )
                gamma_ok = True
                break
            except Exception as exc:
                print(f"  {_C['yellow']}Gamma attempt {attempt+1}/3 failed: {exc}{_C['reset']}")
                if attempt < 2:
                    time.sleep(3)
        if gamma_ok:
            result.articles.append(gamma_out["content"])
            result.shareable_content = gamma_out["content"]   # keep last for legacy
            _print_agent_complete(3, 3, "Gamma")
            _print_agent_output(gamma_out["content"], label=f"GAMMA — ARTICLE {idx}/{n_papers}")
            _print_review_status(gamma_out)
            _save(gamma_out["content"], f"gamma_article_paper{idx}.txt", save_outputs)
        else:
            result.errors.append(f"Gamma[paper {idx}]: failed after 3 attempts")
            _print_agent_error(3, "Gamma", Exception("failed after 3 attempts"))
            result.articles.append("")
            result.content_cards.append({})
            continue  # skip Delta for this paper if Gamma fails

        # ── Delta: Save one content card for this paper ──────────────────────
        # Delta already has internal retry (3 attempts + fallback) in delta.py
        _print_step("DELTA", f"Saving content card for paper {idx}/{n_papers}...", "blue")
        try:
            card = run_delta(
                topic=topic,
                specialty=specialty,
                therapy_area=therapy_area,
                insights=beta_out,
                article=gamma_out["content"],
                llm_provider=provider,
                authors=paper.get("authors", ""),
                pubmed_link=paper.get("pubmed_link", paper.get("link", "")),
            )
            result.content_cards.append(card)
            result.content_card = card   # keep last for legacy
            _print_step("DELTA", f"Content card {idx}/{n_papers} saved", "green")
            _print_delta_output(card)
            _save(
                json.dumps(card, indent=2),
                f"delta_card_paper{idx}.json",
                save_outputs,
            )
        except Exception as exc:
            result.errors.append(f"Delta[paper {idx}]: {exc}")
            _print_agent_error(4, "Delta", exc)
            result.content_cards.append({})

    print(f"\n{_C['bold']}{_C['green']}All {n_papers} paper(s) processed{_C['reset']}")
    print(f"  Content cards saved: {len([c for c in result.content_cards if c])}/{n_papers}")

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


def _print_review_status(gamma_out: dict) -> None:
    """Print MA review submission status from Gamma's output."""
    status     = gamma_out.get("status", "Unknown")
    word_count = gamma_out.get("word_count", 0)
    pubmed_link = gamma_out.get("pubmed_link", "")
    review_note = gamma_out.get("review_note", "")

    print(f"  {_C['yellow']}Article Status : {status}{_C['reset']}")
    print(f"  Word Count   : {word_count} words")
    if pubmed_link:
        print(f"  Read More    : {pubmed_link}")
    if review_note:
        print(f"  {_C['grey']}{review_note}{_C['reset']}")
    print()


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
    n_papers   = len(result.papers)
    n_articles = len([a for a in result.articles if a])
    n_cards    = len([c for c in result.content_cards if c])

    print(f"{'═' * w}")
    print(f"  {_C['bold']}{_C['green']}Pipeline complete in {result.duration_seconds}s{_C['reset']}")
    print(f"  Topic            : {result.topic}")
    print(f"  Papers Found     : {n_papers} (Alpha)")
    print(f"  Summaries        : {len(result.summaries)} (Beta — one per paper)")
    print(f"  Articles Written : {n_articles} (Gamma — one per paper)")
    print(f"  Content Cards    : {n_cards} (Delta — one per paper → Pending MA Review)")
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
