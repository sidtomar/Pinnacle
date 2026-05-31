"""
Agent Alpha — Research Paper Discovery Agent
=============================================
Responsibility:
  Given a topic (derived from a doctor's specialty/interests via Databricks,
  or read from topics.txt for demo), Agent Alpha finds the BEST matching
  research paper/article from:

    1. PubMed  — peer-reviewed literature via NCBI E-utilities (primary)
    2. MA Content Library — internal documents curated by Medical Affairs
       (Databricks Vector Search or local Azure repo fallback)

  Alpha returns a SINGLE best-match paper with full metadata so that:
    • Agent Beta can create a presentable summary article
    • Agent Gamma can produce the final 200-500 word article for MA review

Output:
  One paper with: Title, Authors, Journal, Date, PMID, PubMed Link, DOI, Abstract
"""

import logging
import os
from pathlib import Path

import yaml
from langgraph.prebuilt import create_react_agent

from config import get_llm

logger = logging.getLogger(__name__)

# ── Source configuration loader ──────────────────────────────────────────────

_SOURCES_CONFIG_PATH = Path(__file__).resolve().parent.parent / "alpha_sources.yaml"

# Tool registry — maps config tool names to actual tool objects (lazy loaded)
_TOOL_REGISTRY = {}


def _load_tool(tool_name: str):
    """Lazy-load a tool by its config name."""
    if tool_name == "search_pubmed":
        from tools import search_pubmed
        return search_pubmed
    elif tool_name == "read_local_docs":
        from tools import read_local_docs
        return read_local_docs
    elif tool_name == "search_vector_store":
        from tools import search_vector_store
        return search_vector_store
    elif tool_name == "build_tavily_tool":
        from tools import build_tavily_tool
        return build_tavily_tool()
    elif tool_name == "read_onedrive_files":
        from tools import read_onedrive_files
        return read_onedrive_files
    else:
        logger.warning(f"Unknown tool in alpha_sources.yaml: {tool_name}")
        return None


def _get_enabled_sources() -> list[dict]:
    """
    Read alpha_sources.yaml and return a list of enabled sources,
    sorted by priority (lowest number first).

    Modes:
      "demo"       → ALL sources are enabled (showcase full capabilities)
      "production" → Only sources with production_enabled=true are active

    Each item: {"name": str, "description": str, "tool_name": str, "priority": int}
    """
    if not _SOURCES_CONFIG_PATH.exists():
        logger.warning(
            f"alpha_sources.yaml not found at {_SOURCES_CONFIG_PATH}. "
            f"Falling back to PubMed + Local Content Repo."
        )
        return [
            {"name": "pubmed", "description": "PubMed", "tool_name": "search_pubmed", "priority": 1},
            {"name": "local_content_repo", "description": "Local content repo", "tool_name": "read_local_docs", "priority": 2},
        ]

    with open(_SOURCES_CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    mode = cfg.get("mode", "production").lower().strip()
    sources = cfg.get("sources", {})
    enabled = []

    for name, src in sources.items():
        # In demo mode: ALL sources enabled
        # In production mode: only production_enabled=true
        if mode == "demo":
            is_enabled = True
        else:
            is_enabled = src.get("production_enabled", False)

        if is_enabled:
            # Check if required env vars are set (skip source if creds missing)
            requires = src.get("requires", [])
            missing = [r for r in requires if not os.getenv(r, "")]
            if missing and mode != "demo":
                logger.warning(
                    f"Source '{name}' enabled but missing env vars: {missing} — skipping"
                )
                continue
            elif missing and mode == "demo":
                logger.info(
                    f"Source '{name}' (demo mode): missing env vars {missing} — "
                    f"will attempt anyway, may return empty results"
                )

            enabled.append({
                "name": name,
                "description": src.get("description", name),
                "tool_name": src.get("tool", ""),
                "priority": src.get("priority", 99),
            })

    enabled.sort(key=lambda s: s["priority"])

    if not enabled:
        logger.warning("No sources enabled in alpha_sources.yaml! Falling back to PubMed.")
        return [{"name": "pubmed", "description": "PubMed", "tool_name": "search_pubmed", "priority": 1}]

    logger.info(f"Alpha mode: {mode.upper()} — {len(enabled)} source(s) active")
    return enabled


def _get_tools_and_source_list() -> tuple[list, str]:
    """
    Load enabled sources from config, resolve their tools, and return:
      - list of LangChain tool objects
      - formatted source list string for the prompt
    """
    sources = _get_enabled_sources()
    tools = []
    source_names = []

    for src in sources:
        tool_obj = _load_tool(src["tool_name"])
        if tool_obj:
            tools.append(tool_obj)
            source_names.append(src["description"])
            logger.info(f"Alpha source ENABLED: {src['name']} ({src['description']})")
        else:
            logger.warning(f"Alpha source {src['name']}: tool '{src['tool_name']}' could not be loaded — skipping")

    source_list = ", ".join(source_names)
    return tools, source_list

_SYSTEM_PROMPT_TEMPLATE = """\
You are Agent Alpha, a medical research discovery agent for Mankind Pharma (India).

Your job is to find ALL relevant research papers on the given topic.
Each paper found will be individually summarised and turned into a separate article.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALLOWED SOURCES (STRICTLY ONLY THESE — NO EXCEPTIONS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{source_instructions}

⚠️ DO NOT search any source that is NOT listed above.
   You have access ONLY to the tools listed. Use each enabled tool once.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (follow this EXACTLY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══════════════════════════════════════════════════════════════
AGENT ALPHA — PAPERS FOUND
Topic: <topic>
Sources Searched: {source_list}
Total Papers: <N>
═══════════════════════════════════════════════════════════════

<<PAPER_START>>
Paper#   : 1
Title    : <full paper title>
Authors  : <Author1 LastName Initials, Author2 LastName Initials, et al.>
Journal  : <journal name>
Published: <YYYY-MM or YYYY>
PMID     : <PubMed ID>
Link     : https://pubmed.ncbi.nlm.nih.gov/<PMID>/
DOI      : <doi or N/A>
Source   : PubMed
Abstract : <full abstract — include ALL key statistics and findings>
<<PAPER_END>>

<<PAPER_START>>
Paper#   : 2
Title    : <next paper title>
Authors  : <authors>
Journal  : <journal>
Published: <date>
PMID     : <PMID>
Link     : https://pubmed.ncbi.nlm.nih.gov/<PMID>/
DOI      : <doi or N/A>
Source   : PubMed
Abstract : <full abstract>
<<PAPER_END>>

[Continue for ALL papers found — each wrapped in <<PAPER_START>> / <<PAPER_END>>]

### LOCAL CONTENT REPOSITORY
[List any internal documents found, OR write:
 "No matching document found in local content repository."]

═══════════════════════════════════════════════════════════════
END OF ALPHA OUTPUT
═══════════════════════════════════════════════════════════════

IMPORTANT RULES:
- ONLY use the tools provided to you — no other sources
- Return EVERY paper found — do not filter or drop any
- Target 3-5 papers; include all if fewer are found
- Include the COMPLETE abstract for each paper with key statistics (%, p-values, trial names)
- Each PubMed Link MUST be: https://pubmed.ncbi.nlm.nih.gov/<PMID>/
- These links will be used as "Read More" links in each paper's final article
- Prefer recent papers (2023-2026) with strong evidence
- Prefer India/Asian population studies when available
- NEVER combine papers — each paper must be in its own <<PAPER_START>>...<<PAPER_END>> block
"""

# Source-specific instruction templates
_SOURCE_INSTRUCTIONS = {
    "pubmed": (
        "SOURCE: PubMed (PRIMARY)\n"
        "  Use the search_pubmed tool ONCE with a focused query.\n"
        "  Select the SINGLE BEST paper: most relevant, most recent,\n"
        "  strongest evidence (RCT > observational > case report).\n"
        "  Prefer India/Asian population data when available."
    ),
    "local_content_repo": (
        "SOURCE: Local Content Repository\n"
        "  Use the read_local_docs tool to check the local content repository\n"
        "  for any internal documents created by the Medical Affairs team.\n"
        "  Contains MA-curated clinical summaries, India-specific data,\n"
        "  and internal research documents (.txt, .pdf, .docx, .xlsx files)."
    ),
    "databricks_vector_search": (
        "SOURCE: Databricks Vector Search\n"
        "  Use the search_vector_store tool for semantic search over the\n"
        "  MA document library stored in Databricks. Returns relevant\n"
        "  text chunks from internal clinical documents."
    ),
    "tavily_web_search": (
        "SOURCE: Tavily Web Search\n"
        "  Use the tavily web search tool for real-time web search.\n"
        "  Searches the open web for recent medical articles and clinical data."
    ),
    "onedrive": (
        "SOURCE: OneDrive (Microsoft Graph)\n"
        "  Use the read_onedrive_files tool to read documents from\n"
        "  the shared OneDrive/SharePoint folder maintained by the MA team."
    ),
}


def run_alpha(topic: str) -> str:
    """
    Run Agent Alpha: find the best research paper using ONLY the sources
    enabled in alpha_sources.yaml.

    Sources are configurable — edit alpha_sources.yaml to enable/disable:
      - pubmed (PubMed NCBI)
      - local_content_repo (local Research/ folder)
      - databricks_vector_search (Databricks VS)
      - tavily_web_search (Tavily web API)
      - onedrive (Microsoft OneDrive/SharePoint)

    Args:
        topic: The research topic string (e.g. "SGLT2 inhibitors in heart failure").

    Returns:
        Raw text output from Alpha with all papers in <<PAPER_START>>...<<PAPER_END>> blocks.
        Use parse_alpha_papers() to extract individual paper records.
    """
    # Load enabled sources from config
    tools, source_list = _get_tools_and_source_list()
    enabled_sources = _get_enabled_sources()

    # Build source-specific instructions for the prompt
    instructions = []
    for i, src in enumerate(enabled_sources, 1):
        instr = _SOURCE_INSTRUCTIONS.get(src["name"], f"SOURCE: {src['description']}")
        instructions.append(f"{i}. {instr}")
    source_instructions = "\n\n".join(instructions)

    # Build the prompt with enabled sources
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
        source_instructions=source_instructions,
        source_list=source_list,
    )

    logger.info(f"Alpha using {len(tools)} source(s): {source_list}")

    llm   = get_llm(temperature=0.1)
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )

    result = agent.invoke({
        "messages": [("human", (
            f"Find ALL relevant research papers on this topic: {topic}\n\n"
            f"Use each of your available tools. Find 3-5 papers on this topic. "
            f"Return EVERY paper found — each in its own <<PAPER_START>>...<<PAPER_END>> block. "
            f"Include the complete abstract for each paper. "
            f"Only use the tools provided — no other sources."
        ))]
    })

    return result["messages"][-1].content


def parse_alpha_papers(alpha_output: str) -> list[dict]:
    """
    Parse Alpha's raw text output into a list of paper dicts.
    Each dict has: title, authors, journal, published, pmid, link, doi, source, abstract.

    Papers are delimited by <<PAPER_START>> / <<PAPER_END>> tags.
    Falls back to simple field parsing if tags are not present.
    """
    import re

    papers = []

    # Try structured parsing with <<PAPER_START>> / <<PAPER_END>> tags
    blocks = re.findall(r"<<PAPER_START>>(.*?)<<PAPER_END>>", alpha_output, re.DOTALL)

    if not blocks:
        # Fallback: treat the whole output as one paper
        blocks = [alpha_output]

    for block in blocks:
        paper = {}
        field_map = {
            "Title":     "title",
            "Authors":   "authors",
            "Journal":   "journal",
            "Published": "published",
            "PMID":      "pmid",
            "Link":      "link",
            "DOI":       "doi",
            "Source":    "source",
            "Abstract":  "abstract",
        }
        for label, key in field_map.items():
            # Match "Label : value" or "Label: value" — abstract may be multi-line
            if key == "abstract":
                m = re.search(rf"Abstract\s*:\s*(.+?)(?=\n[A-Z][a-zA-Z]+\s*:|<<PAPER_END>>|$)",
                              block, re.DOTALL | re.IGNORECASE)
            else:
                m = re.search(rf"^{label}\s*:\s*(.+)$", block, re.MULTILINE | re.IGNORECASE)
            if m:
                paper[key] = m.group(1).strip()

        # Derive pubmed_link from link field
        if "link" in paper:
            paper["pubmed_link"] = paper["link"]
        elif "pmid" in paper and paper["pmid"]:
            paper["pubmed_link"] = f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/"

        # Only include if we have at least a title
        if paper.get("title"):
            papers.append(paper)

    logger.info(f"Alpha parsed {len(papers)} paper(s) from output")
    return papers
