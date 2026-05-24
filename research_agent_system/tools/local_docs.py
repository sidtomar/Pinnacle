"""
Local document reader tool for Agent Alpha.

Reads files from the local Research/ folder — used as the primary internal-document
source in demo mode and as a fallback in production when OneDrive is not configured.

Supports: .txt  .pdf  .docx  .xlsx  (same formats as onedrive.py)

Configuration:
  LOCAL_DOCS_PATH env var  — absolute path to the folder (default: <project_root>/Research/)

Drop any .txt / .docx / .xlsx / .pdf files into that folder and Alpha will
automatically find and read them on the next pipeline run.
"""
import io
import os
from pathlib import Path

from langchain_core.tools import tool

SUPPORTED_EXTS = {".txt", ".pdf", ".docx", ".xlsx"}


def _get_docs_path() -> Path:
    env = os.getenv("LOCAL_DOCS_PATH")
    if env:
        return Path(env)
    # Default: Research/ at the project root
    # This file lives at research_agent_system/tools/local_docs.py
    # → go up 3 levels: tools/ → research_agent_system/ → project_root/
    return Path(__file__).resolve().parent.parent.parent / "Research"


def _extract_text(content: bytes, filename: str) -> str:
    """Return plain text from supported file types."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return content.decode("utf-8", errors="replace")

    if ext == ".pdf":
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "\n".join(p.extract_text() or "" for p in reader.pages)

    if ext == ".docx":
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if ext == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        lines = []
        for ws in wb.worksheets:
            lines.append(f"--- Sheet: {ws.title} ---")
            for row in ws.iter_rows(values_only=True):
                lines.append("\t".join(str(c) if c is not None else "" for c in row))
        return "\n".join(lines)

    return f"[Unsupported file type: {ext}]"


@tool
def read_local_docs(query: str) -> str:
    """
    Search the local Research folder for internal company documents that match
    the query keyword and return their full text content.

    This tool is the primary internal-document source in demo mode and a fallback
    in production when OneDrive credentials are not configured.

    To add more internal documents: drop .txt / .docx / .xlsx / .pdf files into
    the Research/ folder at the project root.

    Input : a topic or keyword (e.g. "SGLT2", "PCOS", "GLP-1")
    Output: concatenated text content of all matched files (up to 5 files)
    """
    docs_path = _get_docs_path()

    if not docs_path.exists():
        return (
            f"Local Research folder not found at '{docs_path}'. "
            "Run demo/create_research_docs.py to generate the demo documents, "
            "or create the folder and drop your own files in."
        )

    all_files = [
        f for f in docs_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    ]

    if not all_files:
        return f"No supported documents found in '{docs_path}/'."

    # Match: full query string in filename
    q = query.lower()
    matched = [f for f in all_files if q in f.name.lower()]

    # Fallback: any significant word (≥4 chars) in filename
    if not matched:
        words = [w for w in q.split() if len(w) >= 4]
        matched = [f for f in all_files if any(w in f.name.lower() for w in words)]

    # Last resort: return all files
    if not matched:
        matched = all_files

    results = []
    for f in matched[:5]:
        try:
            text = _extract_text(f.read_bytes(), f.name)
            results.append(f"=== {f.name} (internal document) ===\n{text[:4000]}")
        except Exception as exc:
            results.append(f"=== {f.name} === [Could not read: {exc}]")

    return "\n\n".join(results)


def list_local_docs() -> list[dict]:
    """
    Return a list of dicts describing all files in the Research folder.
    Used by mock_runner to populate the internal_docs section of alpha output.
    """
    docs_path = _get_docs_path()
    if not docs_path.exists():
        return []
    return [
        {
            "filename": f.name,
            "type": f.suffix.lstrip(".").lower(),
            "size_kb": f.stat().st_size // 1024,
            "path": str(f),
        }
        for f in sorted(docs_path.iterdir())
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    ]
