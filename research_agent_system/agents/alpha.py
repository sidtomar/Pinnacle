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

Your job is to find the SINGLE BEST research paper on the given topic.

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
AGENT ALPHA — PAPER FOUND
Topic: <topic>
Sources Searched: {source_list}
═══════════════════════════════════════════════════════════════

### SELECTED PAPER
Title    : <full paper title>
Authors  : <Author1 LastName Initials, Author2 LastName Initials, et al.>
Journal  : <journal name>
Published: <YYYY-MM or YYYY>
PMID     : <PubMed ID>
Link     : https://pubmed.ncbi.nlm.nih.gov/<PMID>/
DOI      : <doi or N/A>
Source   : PubMed
Abstract : <full abstract — include all key statistics and findings>

### ADDITIONAL SOURCES CHECKED
[For each non-PubMed source that was searched, report what was found.
 If nothing found, write: "No matching document found in <source name>."]

═══════════════════════════════════════════════════════════════
END OF ALPHA OUTPUT
═══════════════════════════════════════════════════════════════

IMPORTANT RULES:
- ONLY use the tools provided to you — no other sources
- Return only the SINGLE BEST paper — not a list of many papers
- Include the COMPLETE abstract with key statistics (%, p-values, trial names)
- The PubMed Link MUST be correct: https://pubmed.ncbi.nlm.nih.gov/<PMID>/
- This link will be used as "Read More" in the final article
- Prefer recent papers (2023-2026) with strong evidence
- Prefer India/Asian population studies when available
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
        Single best paper with full metadata — ready for Agent Beta.
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
            f"Find the single best research paper on this topic: {topic}\n\n"
            f"Use each of your available tools once. Pick the BEST paper "
            f"(most relevant, recent, strongest evidence). "
            f"Return the selected paper with full metadata. "
            f"Only use the tools provided — no other sources."
        ))]
    })

    return result["messages"][-1].content
