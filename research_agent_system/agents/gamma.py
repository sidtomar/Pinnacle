"""
Agent Gamma — Per-Paper Article Writer & MA Review Submission
==============================================================
Responsibility:
  Takes Beta's summary for ONE paper and writes a polished 200-500 word
  ARTICLE about that specific paper. Called once per paper (N papers → N articles).

  Each article is independently submitted for Medical Affairs (MA) team
  review before the BU Head/PMT can share it with doctors.

Input:
  • topic         — research topic
  • paper_list    — ONE paper's metadata from Alpha (PubMed link for "Read More")
  • summaries     — Beta's summary for this specific paper

Output:
  • One 200-500 word article for this paper with "Read More" link
  • Status: "Pending Review" — awaiting MA approval
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

📖 **Read the full article:** [<Paper Title>](<EXACT PubMed URL from Alpha's output>)

For example: [Effect of SGLT2 inhibitors on heart failure outcomes](https://pubmed.ncbi.nlm.nih.gov/38768620/)
The link MUST be a proper markdown hyperlink with the paper title as display text and PubMed URL as the link.

**Authors:** <Author names from Alpha's paper data>
**Published:** <Publication date> | **Journal:** <Journal name>

**#<Specialty> #<TherapyArea> #<KeyTopic1> #<KeyTopic2> #<KeyTopic3> ...**

Example hashtags: #Cardiology #HeartFailure #SGLT2Inhibitors #CardiovascularOutcomes #MetaAnalysis #RCT #EvidenceBased

Generate 5-8 relevant hashtags from:
  - The medical specialty (e.g. #Cardiology, #Diabetology, #Gynaecology)
  - The therapy area (e.g. #HeartFailure, #PCOS, #Hypertension)
  - Key topics/drugs from the paper (e.g. #SGLT2Inhibitors, #Semaglutide, #GLP1)
  - Study type (e.g. #MetaAnalysis, #RCT, #SystematicReview)
  - Relevant clinical terms (e.g. #CardiovascularOutcomes, #HbA1c, #RenalProtection)

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
- MUST include article metadata: author names, publication date, journal name
- MUST include the original article link as a CLICKABLE HYPERLINK in markdown format:
  [Paper Title](https://pubmed.ncbi.nlm.nih.gov/PMID/) — NOT a raw URL
- MUST include 5-8 hashtags at the end covering specialty, therapy area, key topics, and study type
- Hashtags should be in CamelCase format (e.g. #HeartFailure not #heart-failure)
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

    # Extract PubMed link — prefer from article text, fallback to Alpha's paper data
    pubmed_link = _extract_pubmed_link(article) or _extract_pubmed_link(paper_list)

    # ── Safety net: if the LLM didn't include Read More, append it ────────
    has_read_more = bool(re.search(
        r"Read the full|Read More|View on PubMed",
        article, re.IGNORECASE
    ))
    if not has_read_more and pubmed_link:
        # Extract title from Alpha's paper data
        title_match = re.search(r"Title\s*:\s*(.+)", paper_list)
        title_text = title_match.group(1).strip() if title_match else topic
        article += f"\n\n---\n\n📖 **Read the full article:** [{title_text}]({pubmed_link})"

    # Count words
    word_count = len(article.split())

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
