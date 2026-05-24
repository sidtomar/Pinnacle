"""
Agent Alpha — Research Agent
============================
Gathers comprehensive information on a medical topic from four sources:

  1. Internet       — Tavily web search (≥3 queries, different angles)
  2. OneDrive       — Internal documents via Microsoft Graph API
  3. Vector Store   — Semantic search over the MA document library
                      (Databricks Vector Search in production;
                       local keyword fallback in demo / SQLite mode)
  4. Local Research — Fallback keyword search over Research/ folder
                      (always available, even offline)

Uses LangGraph's create_react_agent (LangChain 1.x / LangGraph 1.x API).
"""
from langgraph.prebuilt import create_react_agent

from config import get_llm
from tools import build_tavily_tool, read_onedrive_files, search_vector_store, read_local_docs

_SYSTEM_PROMPT = """\
You are Agent Alpha, a meticulous medical research assistant for Mankind Pharma.

Your job is to gather comprehensive information on the given topic from FOUR sources:

1. Internet search — use the internet_search tool.
   Run at least 3 searches with different angles:
   latest clinical news, randomised trials, expert guidelines, Indian population data.

2. OneDrive internal documents — use the read_onedrive_files tool to search for
   internal papers, MA briefs, and brand documents.

3. MA document library (vector search) — use the search_vector_store tool.
   This searches Mankind Pharma's curated library of clinical summaries,
   drug-interaction tables, real-world India evidence, and internal protocols.
   Always run at least one vector store search for the topic.
   Also search for India-specific angles (e.g. "India real world evidence <topic>").

4. Local Research folder — use the read_local_docs tool as an additional
   check for any documents not yet indexed in the vector store.

After gathering all information, produce a consolidated research article in this format:

## Topic: <topic>

## Internet Findings
<summarised findings from each web search, with source URLs>

## Internal Document Findings
### From MA Document Library (Vector Search)
<relevant chunks retrieved, with source filenames and sections>

### From OneDrive / Local Research Folder
<content from OneDrive and/or local Research folder files, or "No additional internal documents found">

## Consolidated Research Article
<a comprehensive, readable article (600-900 words) merging all sources,
 with inline citations, written for a medical professional audience>

Be thorough, accurate, and clinically focused. Prioritise India-specific evidence
wherever available, as Mankind Pharma primarily serves the Indian market.
"""


def run_alpha(topic: str) -> str:
    """
    Run Agent Alpha and return the consolidated research article.

    Tool priority:
        internet_search        — always runs (≥3 queries)
        search_vector_store    — semantic search over MA library (+ fallback)
        read_onedrive_files    — internal OneDrive documents
        read_local_docs        — local Research/ folder keyword search
    """
    llm   = get_llm(temperature=0.1)
    tools = [
        build_tavily_tool(),
        search_vector_store,      # ← Databricks VS (or local keyword fallback)
        read_onedrive_files,
        read_local_docs,          # ← keyword fallback always available
    ]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=_SYSTEM_PROMPT,
    )

    result = agent.invoke({
        "messages": [("human", f"Research this topic thoroughly: {topic}")]
    })

    # The final answer is the last AI message in the messages list
    return result["messages"][-1].content
