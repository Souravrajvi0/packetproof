"""Construct the active LLM client (Ollama or OpenRouter)."""

from __future__ import annotations

import os
from typing import Literal, Union

from core.llm_client import DEFAULT_MODEL, OllamaClient
from core.openrouter_client import DEFAULT_OPENROUTER_MODEL, OpenRouterClient
from core.schemas import LLMError

Provider = Literal["ollama", "openrouter"]
LLMClient = Union[OllamaClient, OpenRouterClient]


def create_llm_client(
    provider: Provider,
    *,
    ollama_url: str = "http://127.0.0.1:11434",
    ollama_model: str = DEFAULT_MODEL,
    openrouter_api_key: str | None = None,
    openrouter_model: str = DEFAULT_OPENROUTER_MODEL,
    timeout: float = 300.0,
) -> LLMClient:
    if provider == "openrouter":
        key = (openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")).strip()
        return OpenRouterClient(api_key=key, model=openrouter_model, timeout=timeout)
    return OllamaClient(base_url=ollama_url, model=ollama_model, timeout=max(timeout, 1200.0))


def resolve_provider(preferred: Provider | None = None) -> Provider:
    if preferred:
        return preferred
    if os.environ.get("OPENROUTER_API_KEY", "").strip():
        return "openrouter"
    return "ollama"
