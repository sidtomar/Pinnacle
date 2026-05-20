import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import BaseTool


def build_tavily_tool() -> BaseTool:
    """Return a configured Tavily search tool."""
    max_results = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
    return TavilySearchResults(
        max_results=max_results,
        include_answer=True,
        include_raw_content=True,
        name="internet_search",
        description=(
            "Search the internet for recent information on a topic. "
            "Input: a search query string. "
            "Output: list of results with title, url, and content."
        ),
    )
