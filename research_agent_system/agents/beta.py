"""
Agent Beta — Per-Paper Research Summary
=========================================
Responsibility:
  Takes ONE paper from Agent Alpha's list and produces a PRESENTABLE SUMMARY
  with all important points. Called once per paper found by Alpha.

  For N papers found by Alpha → Beta is called N times → N summaries produced.
  Each summary then feeds independently into Gamma → Delta.

Input:  ONE paper's metadata (title, authors, abstract, PMID, PubMed link)
Output: A well-structured summary with key findings and "Read More" link
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import get_llm

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are Agent Beta, a senior medical research analyst for Mankind Pharma (India).

You receive ONE research paper from Agent Alpha (title, abstract, authors, journal, PMID, PubMed link).
Your job is to create a PRESENTABLE SUMMARY of THIS SPECIFIC PAPER.

This summary feeds into Agent Gamma which will write a 200-500 word article
specifically about this paper. Agent Gamma is then called separately for each
paper, so each paper gets its own independent article and content card.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══════════════════════════════════════════════════════════════
AGENT BETA — PAPER SUMMARY
═══════════════════════════════════════════════════════════════

**Title:** <paper title>
**Authors:** <authors>
**Journal:** <journal>, <publication date>
**PubMed Link:** <exact PubMed URL from Alpha's output — this becomes the "Read More" link>

---

**WHAT THIS STUDY IS ABOUT**
<2-3 sentences: What was the objective? What question did it try to answer?>

**KEY FINDINGS**
• <Finding 1 — include specific numbers, percentages, p-values>
• <Finding 2 — include specific data points>
• <Finding 3 — include statistical significance>
• <Finding 4 — if applicable>
• <Finding 5 — if applicable>

**STUDY DESIGN & EVIDENCE QUALITY**
<1-2 sentences: What type of study? (RCT, meta-analysis, cohort, etc.)
 How many patients? Duration? This helps doctors assess the strength of evidence.>

**WHY THIS MATTERS FOR CLINICAL PRACTICE**
<2-3 sentences: How can Indian doctors apply these findings?
 What's the practical takeaway for patient care?>

**IMPORTANT LIMITATIONS**
<1-2 sentences: Any caveats doctors should know about?>

📖 **Read the full paper:** <exact PubMed URL>

═══════════════════════════════════════════════════════════════
END OF BETA SUMMARY
═══════════════════════════════════════════════════════════════

RULES:
- Extract ALL important data points from the abstract — do not miss key statistics
- Always include specific numbers (%, p-values, confidence intervals, NNT)
- The PubMed link MUST be copied EXACTLY from Alpha's output — do not fabricate links
- Write in clear, professional language that a specialist doctor would appreciate
- Highlight India-specific or Asian population data if present
- This summary must contain enough detail for Gamma to write a 200-500 word article
"""),
    ("human", """\
Topic: {topic}

Agent Alpha's Selected Paper:
{paper_list}
"""),
])


def run_beta(paper_list: str, topic: str = "") -> str:
    """
    Run Agent Beta: create a presentable summary of ONE paper from Alpha.

    Called once per paper found by Alpha. For N papers → called N times.

    Args:
        paper_list: One paper's metadata from Agent Alpha
                    (title, authors, abstract, PMID, PubMed link).
        topic:      The original research topic (for context).

    Returns:
        A presentable summary with key findings and "Read More" link,
        ready for Agent Gamma to write a full article from.
    """
    llm   = get_llm(temperature=0.15)
    chain = _PROMPT | llm | StrOutputParser()
    return chain.invoke({"paper_list": paper_list, "topic": topic})
