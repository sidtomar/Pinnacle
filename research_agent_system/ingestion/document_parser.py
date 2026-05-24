"""
Document Parser — extract clean text + section structure from medical documents.

Supported formats:  .txt  .pdf  .docx  .xlsx
Each format returns a list of Section objects:
    { "header": str, "content": str }

Section-awareness matters for medical content: a "Results" section should
never be merged with a "Methods" section when chunking, even if they're short.
"""

import io
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Section:
    """A logical section extracted from a document."""
    header: str          # e.g. "3. Indian Real-World Evidence" or "" for intro
    content: str         # raw text of the section
    page: int = 0        # page number (PDF only; 0 = unknown)
    row_range: str = ""  # Excel only: "Sheet: Drug Interactions, rows 1-12"


def parse_file(path: str | Path) -> list[Section]:
    """
    Parse a file into a list of Section objects.

    Args:
        path: Local filesystem path to the document.

    Returns:
        List of Section objects ordered as they appear in the document.
    """
    p = Path(path)
    ext = p.suffix.lower()

    if ext == ".txt":
        return _parse_txt(p)
    if ext == ".pdf":
        return _parse_pdf(p)
    if ext == ".docx":
        return _parse_docx(p)
    if ext == ".xlsx":
        return _parse_xlsx(p)

    raise ValueError(f"Unsupported file format: {ext}  (supported: .txt .pdf .docx .xlsx)")


# ─────────────────────────────────────────────────────────────────────────────
# TXT parser — split on blank lines; treat ALL-CAPS lines as headers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_txt(path: Path) -> list[Section]:
    text = path.read_text(encoding="utf-8", errors="replace")
    sections: list[Section] = []
    current_header = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        # Detect section header: ALL CAPS line ≥ 6 chars, or "---" underline blocks
        is_header = (
            len(stripped) >= 6
            and stripped == stripped.upper()
            and stripped.replace("-", "").replace("=", "").replace(" ", "")
        )
        if is_header and not stripped.startswith("-"):
            if current_lines:
                sections.append(Section(
                    header=current_header,
                    content="\n".join(current_lines).strip()
                ))
                current_lines = []
            current_header = stripped.title()
        else:
            if stripped:
                current_lines.append(line)

    if current_lines:
        sections.append(Section(header=current_header,
                                content="\n".join(current_lines).strip()))

    return sections or [Section(header="", content=text.strip())]


# ─────────────────────────────────────────────────────────────────────────────
# PDF parser — per-page sections; detect headings by font size (if available)
# ─────────────────────────────────────────────────────────────────────────────

def _parse_pdf(path: Path) -> list[Section]:
    import PyPDF2

    reader = PyPDF2.PdfReader(str(path))
    sections: list[Section] = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            sections.append(Section(
                header=f"Page {page_num}",
                content=text.strip(),
                page=page_num,
            ))

    return sections or [Section(header="", content="[PDF could not be parsed]")]


# ─────────────────────────────────────────────────────────────────────────────
# DOCX parser — use heading styles as section boundaries
# ─────────────────────────────────────────────────────────────────────────────

def _parse_docx(path: Path) -> list[Section]:
    from docx import Document

    doc = Document(str(path))
    sections: list[Section] = []
    current_header = ""
    current_paras: list[str] = []

    HEADING_STYLES = {"Heading 1", "Heading 2", "Heading 3",
                      "Title", "Subtitle"}

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Paragraph is a heading → flush current section, start new one
        if para.style.name in HEADING_STYLES:
            if current_paras:
                sections.append(Section(
                    header=current_header,
                    content="\n".join(current_paras)
                ))
                current_paras = []
            current_header = text
        else:
            current_paras.append(text)

    # Flush last section
    if current_paras:
        sections.append(Section(header=current_header,
                                content="\n".join(current_paras)))

    return sections or [Section(header="", content="[DOCX had no readable text]")]


# ─────────────────────────────────────────────────────────────────────────────
# XLSX parser — one section per worksheet; rows → structured text
# ─────────────────────────────────────────────────────────────────────────────

def _parse_xlsx(path: Path) -> list[Section]:
    import openpyxl

    wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    sections: list[Section] = []

    for ws in wb.worksheets:
        rows_text: list[str] = []
        all_rows = list(ws.iter_rows(values_only=True))

        if not all_rows:
            continue

        # Treat first non-empty row as column headers
        headers = [str(c).strip() if c is not None else "" for c in all_rows[0]]
        n_cols = len(headers)

        for row in all_rows[1:]:
            # Format as "ColumnName: Value | ColumnName: Value | ..."
            # This gives the LLM labelled context rather than a raw TSV dump
            cells = [str(c).strip() if c is not None else "" for c in row]
            # Skip completely empty rows
            if not any(cells):
                continue
            pairs = [f"{h}: {v}" for h, v in zip(headers, cells) if v]
            rows_text.append("  |  ".join(pairs))

        if rows_text:
            sections.append(Section(
                header=f"Sheet: {ws.title}",
                content="\n".join(rows_text),
                row_range=f"Sheet: {ws.title}, {len(rows_text)} data rows"
            ))

    wb.close()
    return sections or [Section(header="", content="[XLSX had no readable data]")]
