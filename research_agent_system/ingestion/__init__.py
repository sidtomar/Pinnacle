"""
PinnacleIQ — Medical Document Ingestion Pipeline
=================================================
Parse → Chunk → Embed → Upsert to Delta → Sync Databricks Vector Search

Supported file types: .txt  .pdf  .docx  .xlsx

Quick start
-----------
    from ingestion.ingest_docs import ensure_schema, ingest_folder

    # One-time setup (create Delta source table + VS index)
    ensure_schema()

    # Ingest all documents in the Research folder
    result = ingest_folder(
        "Research/",
        division="Gravitas",
        specialty="Cardiology",
        therapy_area="Heart Failure",
    )
    print(result)
    # {"files_processed": 4, "chunks_upserted": 87, "errors": []}

Demo mode
---------
When DATABRICKS_HOST is not set (STORE_BACKEND=sqlite), ingest_folder still
parses and chunks documents but skips the Databricks write.
Agent Alpha's search_vector_store tool automatically falls back to local
keyword search over the same Research/ folder — zero setup required.

One-time VS bootstrap
---------------------
    from ingestion.ingest_docs import bootstrap_vector_search
    bootstrap_vector_search()   # creates endpoint + Delta-sync index
"""

from .document_parser import parse_file, Section
from .chunker import chunk_sections, Chunk
from .ingest_docs import (
    ingest_file,
    ingest_folder,
    ensure_schema,
    bootstrap_vector_search,
)

__all__ = [
    "parse_file",
    "Section",
    "chunk_sections",
    "Chunk",
    "ingest_file",
    "ingest_folder",
    "ensure_schema",
    "bootstrap_vector_search",
]
