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

from langgraph.prebuilt import create_react_agent

from config import get_llm
from tools import search_pubmed
from tools import read_local_docs

_SYSTEM_PROMPT = """\
You are Agent Alpha, a medical research discovery agent for Mankind Pharma (India).

Your job is to find the SINGLE BEST research paper on the given topic.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALLOWED SOURCES (STRICTLY ONLY THESE TWO — NO EXCEPTIONS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE 1 — PubMed (PRIMARY)
  Use the search_pubmed tool ONCE with a focused query for the topic.
  From the results, select the SINGLE BEST paper based on:
    • Most relevant to the topic
    • Most recent (prefer last 2-3 years)
    • Strongest evidence (RCT > observational > case report)
    • India/Asian population data preferred when available

SOURCE 2 — Local Content Repository (SECONDARY)
  Use the read_local_docs tool to check the local content repository
  for any internal documents created by the Medical Affairs team.
  This contains MA-curated clinical summaries, India-specific data,
  and internal research documents (.txt, .pdf, .docx, .xlsx files).

⚠️ DO NOT search any other source. No web search, no Tavily, no Google,
   no Wikipedia, no other APIs. ONLY PubMed and local content repo.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (follow this EXACTLY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══════════════════════════════════════════════════════════════
AGENT ALPHA — PAPER FOUND
Topic: <topic>
Sources Searched: PubMed, Local Content Repository
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

### LOCAL CONTENT REPOSITORY CHECK
[If a matching internal document was found, list the filename and a brief
 summary of its content. If nothing found, write:
 "No matching document found in local content repository."]

═══════════════════════════════════════════════════════════════
END OF ALPHA OUTPUT
═══════════════════════════════════════════════════════════════

IMPORTANT RULES:
- ONLY search PubMed and local content repository — NO other sources allowed
- Return only the SINGLE BEST paper — not a list of many papers
- Include the COMPLETE abstract with key statistics (%, p-values, trial names)
- The PubMed Link MUST be correct: https://pubmed.ncbi.nlm.nih.gov/<PMID>/
- This link will be used as "Read More" in the final article
- Prefer recent papers (2023-2026) with strong evidence
- Prefer India/Asian population studies when available
"""


def run_alpha(topic: str) -> str:
    """
    Run Agent Alpha: find the best research paper from ONLY two sources:
      1. PubMed (NCBI E-utilities)
      2. Local content repository (MA team documents)

    No other sources are searched — strictly business requirement.

    Args:
        topic: The research topic string (e.g. "SGLT2 inhibitors in heart failure").

    Returns:
        Single best paper with full metadata (title, authors, date, PMID,
        PubMed link, DOI, abstract) — ready for Agent Beta to summarise.
    """
    llm   = get_llm(temperature=0.1)
    tools = [
        search_pubmed,      # SOURCE 1: PubMed (NCBI E-utilities)
        read_local_docs,    # SOURCE 2: Local content repo (MA team documents)
    ]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=_SYSTEM_PROMPT,
    )

    result = agent.invoke({
        "messages": [("human", (
            f"Find the single best research paper on this topic: {topic}\n\n"
            f"Search PubMed once with a focused query. Pick the BEST paper "
            f"(most relevant, recent, strongest evidence). "
            f"Also check the local content repository for any internal MA documents. "
            f"Return the selected paper with full metadata. "
            f"Do NOT use any source other than PubMed and the local content repo."
        ))]
    })

    return result["messages"][-1].content
