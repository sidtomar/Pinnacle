"""
Vector Store Tool — Semantic Search over MA Document Library
============================================================
Wraps Databricks Vector Search for use as a LangChain tool inside Agent Alpha.

Architecture
------------
Production (STORE_BACKEND=databricks):
    Agent Alpha calls ``search_vector_store(query, division, specialty)``
    → Databricks Vector Search runs ANN retrieval on BGE-Large embeddings
    → Results are pre-filtered by division / specialty (Unity Catalog governance)
    → Top-k chunks returned with source filename, section, and page metadata

Demo / SQLite mode (DATABRICKS_HOST not set, or VS SDK not installed):
    Same tool transparently falls back to keyword search over the local
    Research/ folder.  Zero setup required — the demo works out of the box.

Environment variables
---------------------
    DATABRICKS_HOST               — workspace hostname (no https://)
    DATABRICKS_TOKEN              — PAT or service-principal token
    DATABRICKS_VS_ENDPOINT_NAME   — e.g. "pinnacleiq_vs"
    DATABRICKS_VS_INDEX_NAME      — e.g. "pinnacleiq.medical_content.document_chunks_index"
    EMBEDDING_MODEL               — e.g. "databricks-bge-large-en"
    LOCAL_DOCS_PATH               — override local Research/ path (optional)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


# ── Config helpers ─────────────────────────────────────────────────────────────

def _vs_cfg() -> dict:
    return {
        "host":            os.getenv("DATABRICKS_HOST", ""),
        "token":           os.getenv("DATABRICKS_TOKEN", ""),
        "vs_endpoint":     os.getenv("DATABRICKS_VS_ENDPOINT_NAME", "pinnacleiq_vs"),
        "vs_index":        os.getenv(
            "DATABRICKS_VS_INDEX_NAME",
            "pinnacleiq.medical_content.document_chunks_index",
        ),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "databricks-bge-large-en"),
    }


def _vs_available() -> bool:
    """Return True iff both Databricks credentials are present AND the
    ``databricks-vectorsearch`` package is installed."""
    c = _vs_cfg()
    if not (c["host"] and c["token"]):
        return False
    try:
        import databricks.vector_search  # noqa: F401
        return True
    except ImportError:
        return False


# ── Main tool ──────────────────────────────────────────────────────────────────

@tool
def search_vector_store(
    query: str,
    division: str = "",
    specialty: str = "",
    num_results: int = 5,
) -> str:
    """
    Semantic search over the Pinnacle MA internal document library.

    Use this tool to retrieve relevant text from internal medical documents
    including clinical summaries, drug-interaction tables, real-world India
    evidence, protocols, and PCOS / diabetes / cardiology research.

    Prefer this tool over internet search for:
    - Mankind Pharma's proprietary clinical data
    - India-specific real-world evidence (RWE) reports
    - Internal treatment guidelines and protocols
    - Drug interaction tables maintained by the MA team

    Args:
        query:       Natural-language search query.
                     Examples: "SGLT2 cardiovascular outcomes India",
                               "empagliflozin dose adjustment renal",
                               "GLP-1 weight loss real world evidence"
        division:    Optional division filter (e.g. "Gravitas").
                     Leave blank to search across all divisions.
        specialty:   Optional specialty filter (e.g. "Cardiology").
                     Leave blank to search across all specialties.
        num_results: Number of text chunks to return (1–20, default 5).

    Returns:
        Formatted text with retrieved chunks, their source filenames,
        sections, and page numbers.
    """
    num_results = max(1, min(num_results, 20))

    try:
        if _vs_available():
            return _search_databricks(query, division, specialty, num_results)
        else:
            logger.info(
                "Databricks Vector Search not configured — "
                "using local keyword fallback"
            )
            return _search_local_fallback(query, num_results)
    except Exception as exc:
        logger.error(f"search_vector_store error: {exc}", exc_info=True)
        # Non-fatal: return a helpful message so the agent can continue
        return (
            f"[Vector store search encountered an error: {exc}.\n"
            f"Check DATABRICKS_HOST / DATABRICKS_TOKEN / "
            f"DATABRICKS_VS_ENDPOINT_NAME / DATABRICKS_VS_INDEX_NAME.]"
        )


# ── Databricks Vector Search path ──────────────────────────────────────────────

def _search_databricks(
    query: str,
    division: str,
    specialty: str,
    num_results: int,
) -> str:
    from databricks.vector_search.client import VectorSearchClient

    c = _vs_cfg()
    vsc = VectorSearchClient(
        workspace_url=f"https://{c['host']}",
        personal_access_token=c["token"],
    )
    index = vsc.get_index(
        endpoint_name=c["vs_endpoint"],
        index_name=c["vs_index"],
    )

    # Build pre-filters for multi-tenant isolation
    filters: dict = {}
    if division:
        filters["division"] = division
    if specialty:
        filters["specialty"] = specialty

    response = index.similarity_search(
        query_text=query,
        columns=[
            "chunk_id", "filename", "section", "page",
            "chunk_index", "text", "division", "specialty", "therapy_area",
        ],
        filters=filters if filters else None,
        num_results=num_results,
    )

    data = response.get("result", {})
    rows = data.get("data_array", [])

    if not rows:
        scope = f"division={division}" if division else "all divisions"
        return (
            f"[No relevant documents found in the MA library for query: "
            f'"{query}" ({scope})]'
        )

    cols = [c_["name"] for c_ in data.get("manifest", {}).get("columns", [])]

    lines = [
        f"## Internal Document Search Results  "
        f"({len(rows)} chunks · Databricks Vector Search)\n"
        f'Query: "{query}"'
    ]
    if division:
        lines.append(f"Division filter: {division}")
    if specialty:
        lines.append(f"Specialty filter: {specialty}")
    lines.append("")

    for i, row in enumerate(rows, 1):
        r = dict(zip(cols, row))
        section_label = r.get("section") or "Main body"
        page_label    = f"p.{r['page']}" if r.get("page") else "n/a"
        lines += [
            f"### [{i}] {r.get('filename', 'Unknown document')}",
            f"Section: {section_label}  |  Page: {page_label}  |  "
            f"Division: {r.get('division') or 'All'}  |  "
            f"Specialty: {r.get('specialty') or 'General'}",
            "",
            r.get("text", ""),
            "─" * 60,
        ]

    return "\n".join(lines)


# ── Local keyword-search fallback (demo / no-VS) ───────────────────────────────

def _search_local_fallback(query: str, num_results: int) -> str:
    """
    Keyword overlap search over the local Research/ folder.
    Used when Databricks VS is not configured (demo / SQLite mode).
    Consistent output format so the agent sees the same structure.
    """
    SUPPORTED_EXTS = {".txt", ".pdf", ".docx", ".xlsx"}

    # Locate Research folder
    candidates = [
        Path(os.getenv("LOCAL_DOCS_PATH", "")),
        Path(__file__).resolve().parent.parent.parent / "Research",
        Path(__file__).resolve().parent.parent.parent / "demo" / "Research",
    ]
    docs_path: Path | None = next(
        (d for d in candidates if d.is_dir()), None
    )
    if not docs_path:
        return (
            "[Local Research folder not found. "
            "Set LOCAL_DOCS_PATH env var or place documents in Research/.]"
        )

    files = [
        f for f in docs_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    ]
    if not files:
        return "[No supported documents found in Research folder.]"

    # Score files by keyword overlap with query
    query_words = set(query.lower().split())

    def _score(f: Path) -> int:
        name_tokens = set(f.stem.lower().replace("_", " ").split())
        return len(query_words & name_tokens)

    ranked = sorted(files, key=_score, reverse=True)
    top = ranked[:num_results] if _score(ranked[0]) > 0 else ranked[:3]

    # Parse + extract preview text
    from ingestion.document_parser import parse_file  # lazy import

    lines = [
        f"## Internal Document Search Results  "
        f"({len(top)} files · local keyword fallback)\n"
        f'Query: "{query}"  '
        f"[Note: Databricks Vector Search not configured — "
        f"using keyword matching]",
        "",
    ]

    for i, f in enumerate(top, 1):
        try:
            sections = parse_file(f)
            # Gather up to 800 chars of preview from the most relevant sections
            preview_parts: list[str] = []
            budget = 800
            for sec in sections:
                if budget <= 0:
                    break
                snippet = sec.content[:budget].strip()
                if snippet:
                    preview_parts.append(
                        f"[{sec.header or 'Main'}]\n{snippet}" if sec.header else snippet
                    )
                    budget -= len(snippet)
            preview = "\n\n".join(preview_parts)
        except Exception as exc:
            preview = f"[Could not read file: {exc}]"

        lines += [
            f"### [{i}] {f.name}",
            f"Source type: {f.suffix.lstrip('.')}  |  "
            f"Path: Research/{f.name}",
            "",
            preview,
            "─" * 60,
        ]

    return "\n".join(lines)


# ── VS index provisioning helper (call once from setup script) ─────────────────

def ensure_vs_index() -> bool:
    """
    Create the Vector Search endpoint and Delta-sync index if they don't exist.
    Call this once from a setup script or Databricks notebook — NOT at agent
    startup (provisioning takes several minutes).

    Returns:
        True  — endpoint + index are confirmed ready.
        False — VS SDK not installed or credentials absent (non-fatal).
    """
    try:
        from databricks.vector_search.client import VectorSearchClient
    except ImportError:
        logger.info("databricks-vectorsearch not installed — ensure_vs_index skipped")
        return False

    if not _vs_available():
        logger.info("Databricks not configured — ensure_vs_index skipped")
        return False

    c = _vs_cfg()
    source_table = os.getenv(
        "DATABRICKS_VS_SOURCE_TABLE",
        "pinnacleiq.medical_content.document_chunks",
    )
    vsc = VectorSearchClient(
        workspace_url=f"https://{c['host']}",
        personal_access_token=c["token"],
    )

    # ── 1. Endpoint ────────────────────────────────────────────────────────────
    try:
        existing_eps = {ep["name"] for ep in vsc.list_endpoints().get("endpoints", [])}
        if c["vs_endpoint"] not in existing_eps:
            logger.info(f"Creating VS endpoint: {c['vs_endpoint']}")
            vsc.create_endpoint(name=c["vs_endpoint"], endpoint_type="STANDARD")
            logger.info("Endpoint created — provisioning may take ~5 minutes")
        else:
            logger.info(f"VS endpoint already exists: {c['vs_endpoint']}")
    except Exception as exc:
        logger.error(f"VS endpoint error: {exc}")
        return False

    # ── 2. Delta-sync index ────────────────────────────────────────────────────
    try:
        existing_idxs = {
            idx["name"]
            for idx in vsc.list_indexes(c["vs_endpoint"]).get("vector_indexes", [])
        }
        if c["vs_index"] not in existing_idxs:
            logger.info(f"Creating VS index: {c['vs_index']}")
            vsc.create_delta_sync_index(
                endpoint_name=c["vs_endpoint"],
                index_name=c["vs_index"],
                source_table_name=source_table,
                pipeline_type="TRIGGERED",
                primary_key="chunk_id",
                embedding_source_column="text",
                embedding_model_endpoint_name=c["embedding_model"],
            )
            logger.info("VS index created — first sync begins shortly")
        else:
            logger.info(f"VS index already exists: {c['vs_index']}")
    except Exception as exc:
        logger.error(f"VS index error: {exc}")
        return False

    return True
