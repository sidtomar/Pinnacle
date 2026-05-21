"""
LLM Factory — config.py

Default provider: OpenRouter (single API key → 100+ models).
Legacy direct providers (claude, openai) kept for backward compatibility.

Set LLM_PROVIDER=openrouter in your .env and pick any model via OPENROUTER_MODEL.
"""
import os
from enum import Enum

from langchain_core.language_models import BaseChatModel


class LLMProvider(str, Enum):
    OPENROUTER = "openrouter"   # ← default: one key, any model
    CLAUDE     = "claude"       # direct Anthropic API
    OPENAI     = "openai"       # direct OpenAI API


# ── Handy model shortcuts for OpenRouter ──────────────────────────────────────
# Use any of these as the value for OPENROUTER_MODEL in your .env
OPENROUTER_MODELS = {
    # ── Anthropic ────────────────────────────────────────────────────────────
    "claude-sonnet":  "anthropic/claude-sonnet-4-5",
    "claude-opus":    "anthropic/claude-opus-4",
    "claude-haiku":   "anthropic/claude-haiku-3-5",
    # ── OpenAI ───────────────────────────────────────────────────────────────
    "gpt-4o":         "openai/gpt-4o",
    "gpt-4o-mini":    "openai/gpt-4o-mini",
    "o3-mini":        "openai/o3-mini",
    # ── Google ────────────────────────────────────────────────────────────────
    "gemini-pro":     "google/gemini-pro-1.5",
    "gemini-flash":   "google/gemini-flash-1.5",
    # ── Meta ─────────────────────────────────────────────────────────────────
    "llama-3.1-405b": "meta-llama/llama-3.1-405b-instruct",
    "llama-3.1-70b":  "meta-llama/llama-3.1-70b-instruct",
    # ── Mistral ───────────────────────────────────────────────────────────────
    "mistral-large":  "mistralai/mistral-large",
    "mixtral-8x7b":   "mistralai/mixtral-8x7b-instruct",
    # ── DeepSeek ─────────────────────────────────────────────────────────────
    "deepseek-r1":    "deepseek/deepseek-r1",
    "deepseek-v3":    "deepseek/deepseek-chat",
}


def get_llm(
    provider: LLMProvider | None = None,
    temperature: float = 0.2,
    model: str | None = None,
    **kwargs,
) -> BaseChatModel:
    """
    Return a chat model instance for the requested provider.

    Args:
        provider   : 'openrouter' | 'claude' | 'openai'.
                     Reads LLM_PROVIDER env var if None. Defaults to 'openrouter'.
        temperature: 0.0 = deterministic, 1.0 = very creative.
        model      : Override the model (OpenRouter model slug or native model name).
                     If None, reads OPENROUTER_MODEL / CLAUDE_MODEL / OPENAI_MODEL env var.

    Returns:
        A LangChain BaseChatModel — identical interface regardless of provider.
    """
    if provider is None:
        provider = LLMProvider(os.getenv("LLM_PROVIDER", "openrouter").lower())

    # ── OpenRouter (recommended) ───────────────────────────────────────────────
    if provider == LLMProvider.OPENROUTER:
        from langchain_openai import ChatOpenAI  # OpenRouter is OpenAI-API-compatible

        model_name = (
            model
            or os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5")
        )

        return ChatOpenAI(
            model=model_name,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
            # These headers are recommended by OpenRouter for analytics/ranking
            default_headers={
                "HTTP-Referer": "https://pinnacleiq.mankind.com",
                "X-Title": "PinnacleIQ Research Pipeline",
            },
            **kwargs,
        )

    # ── Direct Anthropic (legacy) ──────────────────────────────────────────────
    if provider == LLMProvider.CLAUDE:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=temperature,
            **kwargs,
        )

    # ── Direct OpenAI (legacy) ─────────────────────────────────────────────────
    if provider == LLMProvider.OPENAI:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model or os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature,
            **kwargs,
        )

    raise ValueError(f"Unknown LLM provider: {provider}")
