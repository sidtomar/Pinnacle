"""
Agent Beta — Research Paper Summarisation Agent
================================================
Responsibility:
  Takes the structured paper list from Agent Alpha and produces a
  clinical summary for EACH paper, giving the PMT/BU Head team a
  quick understanding of every paper's relevance and findings.

Input:  Alpha's structured paper list (title, authors, abstract, PMID, etc.)
Output: Per-paper summaries with executive summary, key findings,
        clinical relevance, and evidence level for each paper.

This output feeds into:
  • Agent Gamma — which formats shareable WhatsApp/email messages per paper
  • Agent Delta — which builds the overall portal content card
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import get_llm

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are Agent Beta, a senior medical research analyst for Mankind Pharma (India).

You receive a structured list of research papers discovered by Agent Alpha.
Your job is to write a concise clinical summary for EACH paper.

For EVERY paper in the list, produce the following (use the paper's PMID and title
as the identifier):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### SUMMARY — PAPER <N>: <TITLE> (PMID: <PMID>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**EXECUTIVE SUMMARY** (2–3 sentences)
What did this study do? What was the main result? Why does it matter for Indian doctors?

**KEY FINDINGS**
• <Specific finding 1 with numbers/statistics, e.g. "HbA1c reduced by 1.8% vs 0.7% placebo (p<0.001)">
• <Specific finding 2>
• <Specific finding 3>
• <Add more as needed>

**STUDY TYPE & EVIDENCE LEVEL**
<e.g. "Phase 3 RCT — High quality evidence" or "Meta-analysis of 12 RCTs — Very high evidence">

**CLINICAL RELEVANCE FOR INDIA**
<1–2 sentences on practical application for Indian doctors/patients.
 Note any India-specific data if present, or how findings apply to Indian population.>

**LIMITATIONS**
<1 sentence on any notable limitations (sample size, duration, population studied)>

---

After summarising ALL papers, add:

═══════════════════════════════════════════════════════════════
AGENT BETA — SUMMARY COMPLETE
Papers Summarised: <N>
Overall Evidence Strength: <e.g. "Strong — majority are RCTs and meta-analyses">
Key Consistent Finding: <1 sentence on the most consistent finding across papers>
═══════════════════════════════════════════════════════════════

RULES:
- Summarise EVERY paper in the input list — do not skip any
- Always include specific numbers, percentages, and p-values where available
- If a paper lacks an abstract, note it and summarise from the title and journal context
- Keep each summary focused and clinically actionable
- Highlight India-specific evidence wherever present
"""),
    ("human", """\
Topic: {topic}

Agent Alpha's Paper List:
{paper_list}
"""),
])


def run_beta(paper_list: str, topic: str = "") -> str:
    """
    Run Agent Beta: summarise each paper from Alpha's discovery list.

    Args:
        paper_list: Structured paper list from Agent Alpha (titles, abstracts, PMIDs).
        topic:      The original research topic (for context).

    Returns:
        Per-paper clinical summaries with key findings and evidence levels.
    """
    llm   = get_llm(temperature=0.15)
    chain = _PROMPT | llm | StrOutputParser()
    return chain.invoke({"paper_list": paper_list, "topic": topic})
