"""
Agent Gamma — Article Writer & Medical Affairs Review Submission
=================================================================
Responsibility:
  Takes Beta's paper summary and Alpha's paper data (for PubMed link)
  and writes a polished 200-500 word ARTICLE suitable for sharing with
  doctors. The article is then submitted for Medical Affairs (MA) team
  review before it can be shared with doctors by the PMT/BU Head.

Input:
  • topic         — research topic
  • paper_list    — Alpha's output (contains PubMed link for "Read More")
  • summaries     — Beta's output (detailed paper summary with key findings)

Output:
  • A 200-500 word article with key points and "Read More" link
  • Article status set to "Pending Review" for MA team approval
"""

import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import get_llm

# ── Prompt: Write 200-500 word article ────────────────────────────────────────

_ARTICLE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are Agent Gamma, a medical content writer for Mankind Pharma (India).

You receive:
  1. A research paper with its PubMed link (from Agent Alpha)
  2. A detailed summary of the paper (from Agent Beta)

Your job is to write a POLISHED ARTICLE of 200-500 words that:
  • Can be shared with specialist doctors by the BU Head / PMT team
  • Captures the most important findings from the research paper
  • Is written in clear, professional medical language
  • Includes a "Read More" link to the original PubMed article
  • Will be sent for review to the Medical Affairs team before sharing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARTICLE FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# <Compelling article title — max 15 words>

<Opening paragraph: 2-3 sentences introducing the topic and why this research
matters for clinical practice. Hook the reader immediately.>

## Key Findings

<3-5 bullet points with the most important findings. Each bullet should
include specific data — percentages, p-values, patient numbers, trial names.
These are the points a busy doctor needs to know.>

• <Finding 1 with specific numbers>
• <Finding 2 with specific numbers>
• <Finding 3 with specific numbers>
• <Finding 4 if applicable>
• <Finding 5 if applicable>

## Clinical Significance

<1-2 paragraphs explaining what this means for doctors in practice.
How can they apply these findings? What changes in patient management?
Include India-specific relevance if applicable.>

## Study Details

<1-2 sentences: Study type, sample size, duration, journal, publication date.
Just enough for the doctor to assess evidence quality.>

---

📖 **Read the full article:** <EXACT PubMed URL from Alpha's output>

*Source: <Journal Name>, <Publication Date>*
*— Pinnacle Research Team | Mankind Pharma*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL RULES:
- Article MUST be 200-500 words (not shorter, not longer)
- The "Read More" PubMed URL MUST be EXACTLY as provided by Alpha — do NOT fabricate links
- Include specific statistics from Beta's summary — no vague claims
- Write for specialist doctors — professional tone, not promotional
- Tone: evidence-based, collegial — "the study demonstrates" not "our product shows"
- Do NOT include any drug branding or promotional language
- This article will go to Medical Affairs for review — it must be scientifically accurate
"""),
    ("human", """\
Topic: {topic}

=== Agent Alpha's Selected Paper (contains PubMed link) ===
{paper_list}

=== Agent Beta's Detailed Summary ===
{summaries}
"""),
])


# ── Main runner ───────────────────────────────────────────────────────────────

def run_gamma(topic: str, paper_list: str, summaries: str) -> dict:
    """
    Run Agent Gamma: write a 200-500 word article and submit for MA review.

    Args:
        topic:      The research topic.
        paper_list: Agent Alpha's selected paper (includes PubMed URL).
        summaries:  Agent Beta's detailed paper summary.

    Returns:
        dict with:
          'content'  — the 200-500 word article ready for MA review
          'status'   — "Pending Review" (awaiting Medical Affairs approval)
          'word_count' — word count of the article
    """
    llm = get_llm(temperature=0.25)

    # Generate the article
    article_chain = _ARTICLE_PROMPT | llm | StrOutputParser()
    article = article_chain.invoke({
        "topic":      topic,
        "paper_list": paper_list,
        "summaries":  summaries,
    })

    # Count words
    word_count = len(article.split())

    # Extract PubMed link from article for metadata
    pubmed_link = _extract_pubmed_link(article) or _extract_pubmed_link(paper_list)

    return {
        "content":      article,
        "status":       "Pending Review",
        "word_count":   word_count,
        "pubmed_link":  pubmed_link,
        "review_note":  "Submitted to Medical Affairs team for review and approval before sharing with doctors.",
    }


def _extract_pubmed_link(text: str) -> str:
    """Extract PubMed URL from text."""
    match = re.search(r"https://pubmed\.ncbi\.nlm\.nih\.gov/\d+/?", text)
    return match.group(0) if match else ""
