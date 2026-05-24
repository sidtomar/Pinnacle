"""
Document Ingestion Pipeline
===========================
Parse → Chunk → Upsert to Delta → Sync Databricks Vector Search index.

Supported file types: .txt  .pdf  .docx  .xlsx

Usage
-----
    from ingestion.ingest_docs import ingest_folder, ingest_file, ensure_schema

    # One-time schema bootstrap (safe to call multiple times)
    ensure_schema()

    # Ingest all documents in a folder
    result = ingest_folder(
        "Research/",
        division="Gravitas",
        specialty="Endocrinology",
        therapy_area="Diabetes",
    )
    print(result)
    # {"files_processed": 4, "chunks_upserted": 87, "errors": []}

    # Ingest a single file
    ingest_file(
        "Research/SGLT2_Empagliflozin_Clinical_Summary_Q4_2024.docx",
        division="Gravitas",
        specialty="Endocrinology",
        therapy_area="Diabetes",
    )

Demo / SQLite mode
------------------
When STORE_BACKEND=sqlite (or Databricks credentials are absent) this
module still parses and chunks documents but skips the Delta / VS write.
The ``search_vector_store`` tool handles the fallback to local keyword
search transparently, so the demo works with zero Databricks setup.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from .document_parser import parse_file
from .chunker import chunk_sections, Chunk

logger = logging.getLogger(__name__)

SUPPORTED_EXTS: frozenset[str] = frozenset({".txt", ".pdf", ".docx", ".xlsx"})

# ── Databricks configuration ───────────────────────────────────────────────────

def _cfg() -> dict:
    """Read all Databricks / Vector Search env vars."""
    return {
        "host":         os.getenv("DATABRICKS_HOST", ""),
        "token":        os.getenv("DATABRICKS_TOKEN", ""),
        "http_path":    os.getenv("DATABRICKS_HTTP_PATH", ""),
        # Delta source table that backs the VS index
        "source_table": os.getenv(
            "DATABRICKS_VS_SOURCE_TABLE",
            "pinnacleiq.medical_content.document_chunks",
        ),
        # Vector Search endpoint + index
        "vs_endpoint":  os.getenv("DATABRICKS_VS_ENDPOINT_NAME", "pinnacleiq_vs"),
        "vs_index":     os.getenv(
            "DATABRICKS_VS_INDEX_NAME",
            "pinnacleiq.medical_content.document_chunks_index",
        ),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "databricks-bge-large-en"),
    }


def _databricks_available() -> bool:
    c = _cfg()
    return bool(c["host"] and c["token"] and c["http_path"])


def _get_conn():
    """Open a Databricks SQL connector connection."""
    import databricks.sql as dbsql
    c = _cfg()
    return dbsql.connect(
        server_hostname=c["host"],
        http_path=c["http_path"],
        access_token=c["token"],
    )


# ── DDL ────────────────────────────────────────────────────────────────────────

_CHUNKS_TABLE_DDL = """\
CREATE TABLE IF NOT EXISTS {source_table} (
    chunk_id      STRING  NOT NULL,
    doc_id        STRING,
    filename      STRING,
    section       STRING,
    page          INT,
    chunk_index   INT,
    text          STRING,
    char_count    INT,
    division      STRING,
    specialty     STRING,
    therapy_area  STRING,
    source_type   STRING,
    ingested_at   TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true'
);
"""


# ── Public API ─────────────────────────────────────────────────────────────────

def ensure_schema() -> None:
    """
    Create the Delta chunks table if it doesn't exist.
    Must be called once during application bootstrap before any ingestion.
    Safe to call multiple times (CREATE TABLE IF NOT EXISTS).

    Raises:
        RuntimeError: If Databricks credentials are absent.
    """
    if not _databricks_available():
        logger.info("Databricks not configured — skipping schema creation (demo mode)")
        return

    c = _cfg()
    sql = _CHUNKS_TABLE_DDL.format(source_table=c["source_table"])
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        logger.info(f"Delta table ready: {c['source_table']}")
    finally:
        conn.close()


def ingest_folder(
    folder_path: str | Path,
    *,
    division:     str  = "",
    specialty:    str  = "",
    therapy_area: str  = "",
    recursive:    bool = True,
    dry_run:      bool = False,
) -> dict:
    """
    Ingest every supported document in *folder_path* into Vector Search.

    Args:
        folder_path:  Local path to the document folder.
        division:     Division tag for multi-tenant VS filtering.
        specialty:    Medical specialty tag.
        therapy_area: Therapy area tag.
        recursive:    Recurse into sub-folders.
        dry_run:      Parse + chunk but skip Databricks writes.

    Returns:
        Summary dict::

            {
                "files_processed": int,
                "chunks_upserted": int,
                "errors": [{"file": str, "error": str}, ...]
            }
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    glob_pattern = "**/*" if recursive else "*"
    files = sorted(
        f for f in folder.glob(glob_pattern)
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    )

    logger.info(
        f"Ingesting folder: {folder}  ({len(files)} supported files, "
        f"division={division or 'all'}, dry_run={dry_run})"
    )

    summary: dict = {"files_processed": 0, "chunks_upserted": 0, "errors": []}

    for f in files:
        try:
            r = ingest_file(
                f,
                division=division,
                specialty=specialty,
                therapy_area=therapy_area,
                dry_run=dry_run,
            )
            summary["files_processed"] += 1
            summary["chunks_upserted"] += r["chunks_upserted"]
        except Exception as exc:
            logger.error(f"Failed to ingest {f.name}: {exc}", exc_info=True)
            summary["errors"].append({"file": f.name, "error": str(exc)})

    logger.info(
        f"Folder ingest complete — "
        f"{summary['files_processed']} files, "
        f"{summary['chunks_upserted']} chunks"
    )
    return summary


def ingest_file(
    file_path: str | Path,
    *,
    division:     str  = "",
    specialty:    str  = "",
    therapy_area: str  = "",
    dry_run:      bool = False,
) -> dict:
    """
    Parse, chunk, and upsert a single document.

    Re-ingesting the same file is safe (idempotent MERGE on chunk_id).

    Returns:
        ::

            {
                "filename":       str,
                "sections":       int,
                "chunks":         int,
                "chunks_upserted": int,   # 0 if dry_run or Databricks absent
            }
    """
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")

    logger.info(f"  Parsing  : {p.name}")
    sections = parse_file(p)

    source_type = p.suffix.lstrip(".")
    chunks = chunk_sections(
        sections,
        filename=p.name,
        division=division,
        specialty=specialty,
        therapy_area=therapy_area,
        source_type=source_type,
    )
    logger.info(f"  Chunked  : {len(sections)} sections → {len(chunks)} chunks")

    upserted = 0
    if not dry_run and _databricks_available():
        upserted = _upsert_chunks(chunks)
        _trigger_vs_sync()
    elif not dry_run:
        logger.info(
            f"  Databricks not configured — skipping upsert for {p.name} (demo mode)"
        )

    return {
        "filename":        p.name,
        "sections":        len(sections),
        "chunks":          len(chunks),
        "chunks_upserted": upserted,
    }


# ── Delta upsert ───────────────────────────────────────────────────────────────

_BATCH_SIZE = 250   # rows per MERGE statement


def _upsert_chunks(chunks: list[Chunk]) -> int:
    """
    MERGE chunks into the Delta source table using chunk_id as the key.
    Re-ingesting the same document updates existing rows and inserts new ones.
    """
    if not chunks:
        return 0

    c = _cfg()
    table = c["source_table"]
    total_upserted = 0

    conn = _get_conn()
    try:
        for batch_start in range(0, len(chunks), _BATCH_SIZE):
            batch = chunks[batch_start : batch_start + _BATCH_SIZE]
            values_sql = ",\n".join(_chunk_to_values(ch) for ch in batch)

            merge_sql = f"""
            MERGE INTO {table} AS tgt
            USING (
                SELECT * FROM VALUES
                {values_sql}
                AS src(
                    chunk_id, doc_id, filename, section, page, chunk_index,
                    text, char_count, division, specialty, therapy_area, source_type
                )
            ) AS src ON tgt.chunk_id = src.chunk_id
            WHEN MATCHED THEN UPDATE SET
                tgt.doc_id       = src.doc_id,
                tgt.filename     = src.filename,
                tgt.section      = src.section,
                tgt.page         = src.page,
                tgt.chunk_index  = src.chunk_index,
                tgt.text         = src.text,
                tgt.char_count   = src.char_count,
                tgt.division     = src.division,
                tgt.specialty    = src.specialty,
                tgt.therapy_area = src.therapy_area,
                tgt.source_type  = src.source_type,
                tgt.ingested_at  = current_timestamp()
            WHEN NOT MATCHED THEN INSERT (
                chunk_id, doc_id, filename, section, page, chunk_index,
                text, char_count, division, specialty, therapy_area,
                source_type, ingested_at
            ) VALUES (
                src.chunk_id, src.doc_id, src.filename, src.section,
                src.page, src.chunk_index, src.text, src.char_count,
                src.division, src.specialty, src.therapy_area,
                src.source_type, current_timestamp()
            )
            """
            with conn.cursor() as cur:
                cur.execute(merge_sql)

            total_upserted += len(batch)
            logger.info(
                f"  Upserted batch {batch_start // _BATCH_SIZE + 1} "
                f"({len(batch)} rows)"
            )
    finally:
        conn.close()

    return total_upserted


def _chunk_to_values(c: Chunk) -> str:
    """Format a Chunk as a SQL VALUES row (single-quote-escaped)."""
    def q(s: str) -> str:
        return "'" + str(s).replace("'", "''") + "'"

    return (
        f"({q(c.chunk_id)}, {q(c.doc_id)}, {q(c.filename)}, {q(c.section)}, "
        f"{c.page}, {c.chunk_index}, {q(c.text)}, {c.char_count}, "
        f"{q(c.division)}, {q(c.specialty)}, {q(c.therapy_area)}, {q(c.source_type)})"
    )


# ── Vector Search incremental sync ─────────────────────────────────────────────

def _trigger_vs_sync() -> None:
    """
    Request an incremental sync of the Vector Search index.
    Non-fatal if databricks-vectorsearch is not installed.
    """
    try:
        from databricks.vector_search.client import VectorSearchClient
        c = _cfg()
        vsc = VectorSearchClient(
            workspace_url=f"https://{c['host']}",
            personal_access_token=c["token"],
        )
        vsc.get_index(
            endpoint_name=c["vs_endpoint"],
            index_name=c["vs_index"],
        ).sync()
        logger.info(f"  VS sync triggered: {c['vs_index']}")
    except ImportError:
        logger.debug("databricks-vectorsearch not installed — skipping VS sync")
    except Exception as exc:
        # Non-fatal: data is already in Delta; next scheduled sync will pick it up
        logger.warning(f"  VS sync skipped (non-fatal): {exc}")


# ── Bootstrap helper (create VS endpoint + index) ─────────────────────────────

def bootstrap_vector_search() -> bool:
    """
    Create the Databricks Vector Search endpoint and Delta-sync index if they
    don't already exist.  Call this once from a Databricks notebook or as
    part of the one-time environment setup script.

    Returns:
        True  — endpoint + index confirmed ready.
        False — Databricks VS not configured / not installed.
    """
    try:
        from databricks.vector_search.client import VectorSearchClient
    except ImportError:
        logger.info("databricks-vectorsearch not installed — bootstrap skipped")
        return False

    if not _databricks_available():
        logger.info("Databricks not configured — bootstrap skipped")
        return False

    c = _cfg()
    source_table = c["source_table"]
    vsc = VectorSearchClient(
        workspace_url=f"https://{c['host']}",
        personal_access_token=c["token"],
    )

    # 1. Endpoint
    try:
        existing_eps = {e["name"] for e in vsc.list_endpoints().get("endpoints", [])}
        if c["vs_endpoint"] not in existing_eps:
            logger.info(f"Creating VS endpoint: {c['vs_endpoint']}")
            vsc.create_endpoint(name=c["vs_endpoint"], endpoint_type="STANDARD")
            logger.info("Endpoint created — provisioning may take ~5 minutes")
        else:
            logger.info(f"VS endpoint already exists: {c['vs_endpoint']}")
    except Exception as exc:
        logger.error(f"VS endpoint bootstrap error: {exc}")
        return False

    # 2. Delta-sync index
    try:
        existing_idxs = {
            i["name"]
            for i in vsc.list_indexes(c["vs_endpoint"]).get("vector_indexes", [])
        }
        if c["vs_index"] not in existing_idxs:
            logger.info(f"Creating VS index: {c['vs_index']}")
            vsc.create_delta_sync_index(
                endpoint_name=c["vs_endpoint"],
                index_name=c["vs_index"],
                source_table_name=source_table,
                pipeline_type="TRIGGERED",        # batch sync; use "CONTINUOUS" if needed
                primary_key="chunk_id",
                embedding_source_column="text",
                embedding_model_endpoint_name=c["embedding_model"],
            )
            logger.info("VS index created — first sync will begin shortly")
        else:
            logger.info(f"VS index already exists: {c['vs_index']}")
    except Exception as exc:
        logger.error(f"VS index bootstrap error: {exc}")
        return False

    return True
