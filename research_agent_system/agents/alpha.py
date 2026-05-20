"""
Agent Alpha — Research Agent

Searches the internet (Tavily) and OneDrive files for the given topic,
then consolidates everything into a structured research article.
"""
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

from config import get_llm
from tools import build_tavily_tool, read_onedrive_files

_SYSTEM_PROMPT = PromptTemplate.from_template("""
You are Agent Alpha, a meticulous research assistant.
Your job is to gather comprehensive information on the given topic from two sources:
1. The internet (use the internet_search tool)
2. Internal documents on OneDrive (use the read_onedrive_files tool)

For every topic/keyword:
- Run at least 3 internet searches with different angles (latest news, clinical studies, expert opinions)
- Search OneDrive for relevant internal documents
- Combine all findings into one coherent, well-structured research article

Output format:
## Topic: <topic>
## Internet Findings
<findings from web searches>

## Internal Document Findings
<findings from OneDrive files>

## Consolidated Research Article
<a comprehensive, readable article merging all sources, citing them inline>

Tools available: {tools}
Tool names: {tool_names}

Use the ReAct format:
Thought: <reasoning>
Action: <tool name>
Action Input: <input>
Observation: <result>
... (repeat as needed)
Thought: I have enough information.
Final Answer: <the consolidated research article>

Begin!

Topic/Keywords: {input}
{agent_scratchpad}
""")


def run_alpha(topic: str) -> str:
    """Run Agent Alpha and return the consolidated research article."""
    llm = get_llm(temperature=0.1)
    tools = [build_tavily_tool(), read_onedrive_files]

    agent = create_react_agent(llm=llm, tools=tools, prompt=_SYSTEM_PROMPT)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=12,
        handle_parsing_errors=True,
    )

    result = executor.invoke({"input": topic})
    return result["output"]
