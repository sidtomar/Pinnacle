"""
PubMed Search Tool
==================
Queries NCBI's PubMed via the Entrez E-utilities API (free, no API key required).

E-utilities endpoints used:
  esearch   — search for article PMIDs matching a query
  efetch    — fetch full records with abstracts, authors, journal, DOI

Rate limits:
  Without NCBI_API_KEY: 3 requests/second
  With    NCBI_API_KEY: 10 requests/second  (set in .env)

Set NCBI_API_KEY in .env for higher limits and production use.
"""

from __future__ import annotations

import logging
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

PUBMED_BASE  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
_RATE_DELAY  = 0.12 if NCBI_API_KEY else 0.35   # seconds between requests


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class PubMedPaper:
    pmid:        str
    title:       str
    authors:     List[str]       = field(default_factory=list)
    journal:     str             = ""
    pub_date:    str             = ""
    abstract:    str             = ""
    pubmed_link: str             = ""
    doi:         Optional[str]   = None

    def __post_init__(self):
        if self.pmid and not self.pubmed_link:
            self.pubmed_link = f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


# ── Internal HTTP helpers ─────────────────────────────────────────────────────

def _build_url(endpoint: str, params: dict) -> str:
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    params["tool"]  = "pinnacleiq"
    params["email"] = os.getenv("NCBI_EMAIL", "pinnacle@mankindpharma.com")
    return f"{PUBMED_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"


def _fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "PinnacleIQ-Research/1.0 (Mankind Pharma)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


# ── Core PubMed query ─────────────────────────────────────────────────────────

def search_pubmed_papers(query: str, max_results: int = 10) -> List[PubMedPaper]:
    """
    Search PubMed and return a list of PubMedPaper objects.

    Two API calls:
      1. esearch — get PMID list for the query
      2. efetch  — get full records (title, authors, abstract, journal, date, DOI)
    """
    max_results = max(1, min(max_results, 25))

    # ── 1. esearch ────────────────────────────────────────────────────────────
    esearch_url = _build_url("esearch.fcgi", {
        "db":      "pubmed",
        "term":    query,
        "retmax":  max_results,
        "sort":    "relevance",
        "retmode": "xml",
    })

    try:
        esearch_xml = _fetch(esearch_url)
    except Exception as exc:
        logger.error(f"PubMed esearch failed: {exc}")
        return []

    root = ET.fromstring(esearch_xml)
    pmids = [elem.text for elem in root.findall(".//Id") if elem.text]
    if not pmids:
        return []

    time.sleep(_RATE_DELAY)

    # ── 2. efetch ─────────────────────────────────────────────────────────────
    efetch_url = _build_url("efetch.fcgi", {
        "db":      "pubmed",
        "id":      ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    })

    try:
        efetch_xml = _fetch(efetch_url)
    except Exception as exc:
        logger.error(f"PubMed efetch failed: {exc}")
        return []

    return _parse_efetch(efetch_xml)


def _parse_efetch(xml_str: str) -> List[PubMedPaper]:
    """Parse PubMed efetch XML into a list of PubMedPaper objects."""
    papers: List[PubMedPaper] = []

    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as exc:
        logger.error(f"PubMed XML parse error: {exc}")
        return []

    for article in root.findall(".//PubmedArticle"):
        try:
            pmid  = article.findtext(".//PMID", "").strip()
            title = article.findtext(".//ArticleTitle", "").strip()
            # Strip XML tags from title (e.g. <i>, <sub>)
            title = ET.tostring(article.find(".//ArticleTitle"), encoding="unicode", method="text") \
                    if article.find(".//ArticleTitle") is not None else title

            # Authors
            authors: List[str] = []
            for auth in article.findall(".//Author"):
                last  = auth.findtext("LastName", "").strip()
                first = (auth.findtext("ForeName", "") or auth.findtext("Initials", "")).strip()
                if last:
                    authors.append(f"{last} {first}".strip())
            if len(authors) > 6:
                authors = authors[:6] + ["et al."]

            # Journal
            journal = (
                article.findtext(".//Journal/Title", "") or
                article.findtext(".//MedlineTA", "")
            ).strip()

            # Publication date
            year  = article.findtext(".//PubDate/Year", "") or article.findtext(".//PubDate/MedlineDate", "")[:4]
            month = article.findtext(".//PubDate/Month", "")
            day   = article.findtext(".//PubDate/Day", "")
            parts = [p for p in [year, month, day] if p]
            pub_date = "-".join(parts)

            # Abstract (may be structured with labeled sections)
            abstract_parts: List[str] = []
            for abs_elem in article.findall(".//Abstract/AbstractText"):
                label = abs_elem.get("Label", "")
                text  = (abs_elem.text or "").strip()
                if not text:
                    # Some sections have children — flatten
                    text = ET.tostring(abs_elem, encoding="unicode", method="text").strip()
                if label and text:
                    abstract_parts.append(f"{label}: {text}")
                elif text:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts).strip()

            # DOI
            doi: Optional[str] = None
            for eid in article.findall(".//ELocationID"):
                if eid.get("EIdType") == "doi" and eid.text:
                    doi = eid.text.strip()
                    break

            if pmid and title:
                papers.append(PubMedPaper(
                    pmid=pmid,
                    title=title,
                    authors=authors,
                    journal=journal,
                    pub_date=pub_date,
                    abstract=abstract,
                    doi=doi,
                ))

        except Exception as exc:
            logger.warning(f"Skipping malformed PubMed record: {exc}")
            continue

    return papers


# ── LangChain tool ────────────────────────────────────────────────────────────

@tool
def search_pubmed(query: str, max_results: int = 8) -> str:
    """
    Search PubMed for peer-reviewed research papers on a medical topic.

    Returns a structured list of papers with:
    - Title, Authors, Journal, Publication Date
    - PMID and direct PubMed link (for 'Read More')
    - DOI
    - Abstract (first 600 characters)

    Use this as the PRIMARY research tool. Run at least 3 queries with
    different angles (e.g. drug name + condition, clinical trial, India data).

    Args:
        query:       Medical topic or keywords.
                     Examples:
                       "SGLT2 inhibitors heart failure outcomes 2023"
                       "semaglutide type 2 diabetes HbA1c India"
                       "GLP-1 receptor agonists cardiovascular meta-analysis"
        max_results: Number of papers to return (default 8, max 20).

    Returns:
        Structured text with all papers and their metadata.
    """
    max_results = max(1, min(int(max_results), 20))

    try:
        papers = search_pubmed_papers(query, max_results)
    except Exception as exc:
        return f'[PubMed search error for "{query}": {exc}]'

    if not papers:
        return f'[No PubMed papers found for query: "{query}". Try broader terms.]'

    return _format_papers_for_agent(papers, query)


def _format_papers_for_agent(papers: List[PubMedPaper], query: str) -> str:
    """Format paper list as structured text for the LLM agent."""
    lines = [
        f"## PubMed Search Results — {len(papers)} paper(s) found",
        f'Query: "{query}"',
        "",
    ]

    for i, p in enumerate(papers, 1):
        authors_str = ", ".join(p.authors) if p.authors else "Authors not listed"
        lines += [
            f"### [{i}] {p.title}",
            f"  Authors   : {authors_str}",
            f"  Journal   : {p.journal or 'N/A'}",
            f"  Published : {p.pub_date or 'N/A'}",
            f"  PMID      : {p.pmid}",
            f"  PubMed    : {p.pubmed_link}",
        ]
        if p.doi:
            lines.append(f"  DOI       : https://doi.org/{p.doi}")
        if p.abstract:
            preview = p.abstract[:600] + ("..." if len(p.abstract) > 600 else "")
            lines.append(f"  Abstract  : {preview}")
        lines += ["", "─" * 70, ""]

    return "\n".join(lines)


# ── Utility: format paper list as human-readable output ──────────────────────

def format_paper_list(papers_text: str) -> str:
    """Pass-through — the agent's output already includes formatted paper data."""
    return papers_text
