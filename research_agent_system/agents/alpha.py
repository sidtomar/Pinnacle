"""
Agent Alpha — Research Agent

Searches the internet (Tavily) and OneDrive files for the given topic,
then consolidates everything into a structured research article.

Uses LangGraph's create_react_agent (LangChain 1.x / LangGraph 1.x API).
"""
from langgraph.prebuilt import create_react_agent

from config import get_llm
from tools import build_tavily_tool, read_onedrive_files

_SYSTEM_PROMPT = """\
You are Agent Alpha, a meticulous medical research assistant for Mankind Pharma.

Your job is to gather comprehensive information on the given topic from two sources:
1. The internet — use the internet_search tool (run at least 3 searches with different angles:
   latest news, clinical studies, expert opinions, Indian population data)
2. Internal documents — use the read_onedrive_files tool to find relevant internal papers

After gathering all information, produce a single consolidated research article in this format:

## Topic: <topic>

## Internet Findings
<summarised findings from each web search>

## Internal Document Findings
<content from any matching OneDrive files, or "No internal documents found" if none>

## Consolidated Research Article
<a comprehensive, readable article (500-800 words) merging all sources,
 with inline source citations, written for a medical professional audience>

Be thorough, accurate, and clinically focused.
"""


def run_alpha(topic: str) -> str:
    """Run Agent Alpha and return the consolidated research article."""
    llm = get_llm(temperature=0.1)
    tools = [build_tavily_tool(), read_onedrive_files]

    # LangGraph prebuilt ReAct agent (replaces langchain AgentExecutor)
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
