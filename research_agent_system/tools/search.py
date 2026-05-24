import os
from langchain_tavily import TavilySearch
from langchain_core.tools import BaseTool


def build_tavily_tool() -> BaseTool:
    """Return a configured Tavily search tool."""
    max_results = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
    return TavilySearch(
        max_results=max_results,
        name="internet_search",
        description=(
            "Search the internet for recent information on a topic. "
            "Input: a search query string. "
            "Output: list of results with title, url, and content."
        ),
    )
