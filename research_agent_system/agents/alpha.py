"""
Agent Alpha — PubMed Research & Paper Discovery Agent
======================================================
Responsibility:
  Given a topic (derived from a doctor's specialty/interests via Databricks),
  Agent Alpha scrapes PubMed for relevant research papers AND searches the
  internal MA Content Library (Databricks Vector Search or local fallback).

  It returns a STRUCTURED LIST of papers with full metadata so that:
    • Agent Beta can summarise each paper
    • Agent Gamma can format shareable content with the correct PubMed links

Sources searched (in priority order):
  1. PubMed  — peer-reviewed literature via NCBI E-utilities (primary source)
  2. MA Content Library — internal clinical summaries curated by Medical Affairs
                          (Databricks Vector Search → local keyword fallback)

Output format:
  A structured paper list with the following metadata per paper:
    Title · Authors · Journal · Publication Date
    PMID  · PubMed Link (for 'Read More') · DOI
    Abstract / Key Findings
    Source (PubMed or MA Library)
"""

from langgraph.prebuilt import create_react_agent

from config import get_llm
from tools import search_pubmed, search_vector_store

_SYSTEM_PROMPT = """\
You are Agent Alpha, a medical research discovery agent for Mankind Pharma (India).

Your ONLY job in this pipeline step is to FIND and LIST relevant research papers
on the given topic. You are NOT writing an article — you are building a paper list.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOOL USAGE RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP A — PubMed Search (PRIMARY SOURCE — run 3 or more searches)
  Use the search_pubmed tool at least 3 times with different query angles:
    1. Core topic + condition (e.g. "semaglutide type 2 diabetes")
    2. Topic + clinical outcome (e.g. "semaglutide cardiovascular outcomes RCT")
    3. Topic + India / Asian population (e.g. "GLP-1 India real world evidence")
    4. Topic + recent year if applicable (e.g. "SGLT2 inhibitors 2023 2024")
  Collect ALL unique papers found across all searches.

STEP B — MA Content Library Search (run 1–2 searches)
  Use the search_vector_store tool to check Mankind Pharma's internal
  clinical library for any internal documents, India-specific data, or
  MA-curated summaries on the topic.
  Mark papers from this source as "MA Library" (not PubMed).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (follow this EXACTLY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After all tool calls are complete, output the following:

═══════════════════════════════════════════════════════════════
AGENT ALPHA — PAPER DISCOVERY COMPLETE
Topic: <topic>
PubMed Papers Found: <N>
MA Library Documents: <M>
Total: <N+M>
═══════════════════════════════════════════════════════════════

## PAPERS FOUND

---
### PAPER 1
Title    : <full paper title>
Authors  : <Author1 LastName Initials, Author2 LastName Initials, et al.>
Journal  : <journal name>
Published: <YYYY-MM or YYYY>
PMID     : <PubMed ID>
Link     : https://pubmed.ncbi.nlm.nih.gov/<PMID>/
DOI      : <doi or N/A>
Source   : PubMed
Abstract : <first 400–500 words of abstract — include key statistics and findings>

---
### PAPER 2
[same structure]

---
[continue for all papers...]

## MA CONTENT LIBRARY

[List any internally found documents using the same structure above,
 with Source: MA Library instead of PubMed. If nothing found, write:
 "No relevant documents found in the MA Content Library for this topic."]

═══════════════════════════════════════════════════════════════
END OF ALPHA OUTPUT
═══════════════════════════════════════════════════════════════

IMPORTANT RULES:
- Deduplicate: if the same paper appears in both PubMed and MA Library, list it ONCE
- Include EVERY paper found — do not drop papers
- Keep abstracts concise but include key statistics (%, p-values, NNT, trial names)
- Do NOT write a narrative article — only list papers with their metadata
- Prioritise papers from India and Asian populations when available
- Include papers from last 5 years preferentially, but older landmark trials are fine
"""


def run_alpha(topic: str) -> str:
    """
    Run Agent Alpha: discover research papers from PubMed and MA Content Library.

    Args:
        topic: The research topic string (e.g. "SGLT2 inhibitors in heart failure").

    Returns:
        Structured paper list with metadata (title, authors, date, PMID,
        PubMed link, DOI, abstract) — ready for Agent Beta to summarise.
    """
    llm   = get_llm(temperature=0.1)
    tools = [
        search_pubmed,          # PRIMARY: PubMed E-utilities (NCBI)
        search_vector_store,    # SECONDARY: Mankind MA Content Library
    ]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=_SYSTEM_PROMPT,
    )

    result = agent.invoke({
        "messages": [("human", (
            f"Discover all research papers on this topic: {topic}\n\n"
            f"Run at least 3 PubMed searches with different query angles, "
            f"then search the MA Content Library. "
            f"Return the complete structured paper list."
        ))]
    })

    return result["messages"][-1].content
