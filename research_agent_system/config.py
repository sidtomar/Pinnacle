import os
from enum import Enum
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel

load_dotenv()


class LLMProvider(str, Enum):
    CLAUDE = "claude"
    OPENAI = "openai"


def get_llm(
    provider: LLMProvider | None = None,
    temperature: float = 0.2,
    **kwargs,
) -> BaseChatModel:
    """Return a chat model for the configured (or given) provider."""
    if provider is None:
        provider = LLMProvider(os.getenv("LLM_PROVIDER", "claude").lower())

    if provider == LLMProvider.CLAUDE:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=temperature,
            **kwargs,
        )

    if provider == LLMProvider.OPENAI:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature,
            **kwargs,
        )

    raise ValueError(f"Unknown LLM provider: {provider}")
