"""
Agent Beta — Insights & Summarization Agent

Takes the consolidated research article from Agent Alpha and produces:
- Executive summary
- Key findings (bullet points)
- Clinical/practical insights
- Recommendations
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import get_llm

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are Agent Beta, an expert medical research analyst.
You receive a raw research article compiled by a research agent and produce a structured insight report.

Your output MUST follow this exact structure:

---
## EXECUTIVE SUMMARY
<2-3 sentence high-level summary for a busy doctor>

## KEY FINDINGS
- <Finding 1>
- <Finding 2>
- <Finding 3>
- <add more as needed>

## CLINICAL INSIGHTS
<Practical takeaways relevant to clinical practice>

## EMERGING TRENDS
<What's new or changing in this area>

## RECOMMENDATIONS
- <Actionable recommendation 1>
- <Actionable recommendation 2>
- <add more as needed>

## EVIDENCE QUALITY
<Brief note on the strength and recency of the sources>
---

Be precise, evidence-based, and clinically relevant. Avoid speculation.
"""),
    ("human", "Research Article:\n\n{research_article}"),
])


def run_beta(research_article: str) -> str:
    """Run Agent Beta and return structured insights."""
    llm = get_llm(temperature=0.15)
    chain = _PROMPT | llm | StrOutputParser()
    return chain.invoke({"research_article": research_article})
