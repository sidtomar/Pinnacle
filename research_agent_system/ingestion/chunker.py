"""
Medical Document Chunker
========================
Converts Section objects (from document_parser.py) into fixed-size,
semantically meaningful chunks suitable for embedding and indexing in
Databricks Vector Search.

Design decisions
----------------
- Section boundaries are NEVER crossed.
  A "Results" section is never merged with a "Methods" section even if
  both are short.  Medical context must be preserved.
- Target chunk size : ~500 tokens  (~2 000 chars at 4 chars/token)
- Hard ceiling      : ~625 tokens  (~2 500 chars) before forced split
- Overlap           : ~100 tokens  (~400 chars) of trailing context
  carried into the next sibling chunk within the same section.
  This prevents an answer straddling a chunk boundary from being missed.
- Split hierarchy:
    1. Paragraph boundary (double newline)
    2. Sentence boundary (. ! ? followed by whitespace)
    3. Hard character cut (last resort)
- Each Chunk carries full metadata (division, specialty, page …) so
  Vector Search multi-tenant pre-filtering works without post-filtering.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .document_parser import Section


# ── Tuning knobs (chars, not tokens) ──────────────────────────────────────────
TARGET_CHUNK_CHARS = 2_000   # ~500 tokens  — aim for this size
MAX_CHUNK_CHARS    = 2_500   # ~625 tokens  — hard ceiling before forced split
OVERLAP_CHARS      = 400     # ~100 tokens  — trailing overlap between siblings


# ── Data model ─────────────────────────────────────────────────────────────────

@dataclass
class Chunk:
    """
    A single text chunk ready to be embedded and upserted into the
    Databricks Delta source table that backs the Vector Search index.
    """
    chunk_id:      str   # UUID — primary key in Delta / VS
    doc_id:        str   # filename stem (e.g. "SGLT2_Empagliflozin_Clinical_Summary")
    filename:      str   # original filename with extension
    section:       str   # section header from the document parser
    page:          int   # PDF page number; 0 = unknown / not applicable
    chunk_index:   int   # 0-based position within the *document* (not the section)
    text:          str   # chunk text — this is what gets embedded
    char_count:    int   # len(text) — stored for analytics / cost tracking

    # Multi-tenant / retrieval-time filter columns
    division:      str = ""   # e.g. "Gravitas", "Oncology"
    specialty:     str = ""   # e.g. "Cardiology", "Endocrinology"
    therapy_area:  str = ""   # e.g. "Diabetes", "HFrEF"
    source_type:   str = ""   # docx | xlsx | txt | pdf


# ── Public API ─────────────────────────────────────────────────────────────────

def chunk_sections(
    sections: list[Section],
    filename: str,
    *,
    division:     str = "",
    specialty:    str = "",
    therapy_area: str = "",
    source_type:  str = "",
) -> list[Chunk]:
    """
    Convert a document's list of Sections into a flat list of Chunks.

    Sections are processed independently; no text ever crosses a section
    boundary.  Each section's text is then split into overlapping sub-chunks
    of roughly TARGET_CHUNK_CHARS characters.

    Args:
        sections:     Output of ``document_parser.parse_file()``.
        filename:     Original filename (e.g. "SGLT2_Summary.docx").
        division:     Business division tag for multi-tenant VS filtering.
        specialty:    Medical specialty tag.
        therapy_area: Therapy area tag.
        source_type:  File extension hint ("docx", "xlsx", "txt", "pdf").

    Returns:
        List of Chunk objects ordered by chunk_index (document order).
    """
    doc_id  = Path(filename).stem
    chunks:  list[Chunk] = []
    g_index = 0   # global chunk_index across all sections

    for section in sections:
        text = section.content.strip()
        if not text:
            continue

        sub_texts = _split_text(text)

        for sub in sub_texts:
            chunks.append(Chunk(
                chunk_id    = str(uuid.uuid4()),
                doc_id      = doc_id,
                filename    = filename,
                section     = section.header,
                page        = section.page,
                chunk_index = g_index,
                text        = sub,
                char_count  = len(sub),
                division    = division,
                specialty   = specialty,
                therapy_area= therapy_area,
                source_type = source_type,
            ))
            g_index += 1

    return chunks


# ── Splitting logic ────────────────────────────────────────────────────────────

def _split_text(text: str) -> list[str]:
    """
    Split a single section's text into overlapping sub-chunks.

    Strategy:
        If len(text) ≤ MAX_CHUNK_CHARS  → return as a single chunk.
        Otherwise, split on paragraph boundaries (double newline) while
        accumulating up to TARGET_CHUNK_CHARS chars; when the limit is
        reached, flush the chunk and start the next with an overlap seed.
        Oversized individual paragraphs are recursively hard-split.
    """
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return _hard_split(text)

    result:       list[str]  = []
    current_parts: list[str] = []
    current_len:   int       = 0

    for para in paragraphs:
        # Paragraph itself too big — hard-split first
        if len(para) > MAX_CHUNK_CHARS:
            if current_parts:
                result.append(_join(current_parts))
                current_parts = _tail_overlap(current_parts, OVERLAP_CHARS)
                current_len   = _total_len(current_parts)
            result.extend(_hard_split(para))
            continue

        # Would this paragraph overflow the current chunk?
        if current_len + len(para) + 2 > TARGET_CHUNK_CHARS and current_parts:
            result.append(_join(current_parts))
            # Seed next chunk with overlapping tail
            current_parts = _tail_overlap(current_parts, OVERLAP_CHARS)
            current_len   = _total_len(current_parts)

        current_parts.append(para)
        current_len += len(para) + 2   # +2 for the "\n\n" separator

    if current_parts:
        result.append(_join(current_parts))

    return result or [text]


def _hard_split(text: str) -> list[str]:
    """
    Split at sentence boundaries when paragraph splitting is insufficient.
    Falls back to a hard character cut as absolute last resort.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result:       list[str]  = []
    current_parts: list[str] = []
    current_len:   int       = 0

    for sent in sentences:
        # Sentence itself exceeds max — hard character cut
        if len(sent) > MAX_CHUNK_CHARS:
            if current_parts:
                result.append(" ".join(current_parts))
                current_parts = []
                current_len   = 0
            for i in range(0, len(sent), TARGET_CHUNK_CHARS):
                result.append(sent[i : i + TARGET_CHUNK_CHARS])
            continue

        if current_len + len(sent) + 1 > TARGET_CHUNK_CHARS and current_parts:
            result.append(" ".join(current_parts))
            current_parts = []
            current_len   = 0

        current_parts.append(sent)
        current_len += len(sent) + 1

    if current_parts:
        result.append(" ".join(current_parts))

    return result or [text[:TARGET_CHUNK_CHARS]]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _tail_overlap(parts: list[str], max_chars: int) -> list[str]:
    """
    Return the trailing paragraphs of *parts* whose total length is at
    most max_chars — used as the overlap seed for the next chunk.
    """
    result: list[str] = []
    total   = 0
    for p in reversed(parts):
        if total + len(p) > max_chars:
            break
        result.insert(0, p)
        total += len(p)
    return result


def _join(parts: list[str]) -> str:
    return "\n\n".join(parts)


def _total_len(parts: list[str]) -> int:
    return sum(len(p) + 2 for p in parts)
