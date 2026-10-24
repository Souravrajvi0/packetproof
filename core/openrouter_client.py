"""OpenRouter API client (OpenAI-compatible) for Gemma 3 4B."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

from core.llm_client import parse_json_from_text
from core.schemas import LLMError

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "google/gemma-3-4b-it"
DEFAULT_TIMEOUT = 300.0


class OpenRouterClient:
    """Hosted Gemma via OpenRouter. Document text is sent to OpenRouter providers."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_OPENROUTER_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
        app_title: str = "PacketProof",
        app_url: str = "https://github.com/Souravrajvi0/packetproof",
    ) -> None:
        if not api_key or not api_key.strip():
            raise LLMError(
                "OpenRouter API key missing. Set OPENROUTER_API_KEY or enter it in the sidebar."
            )
        self.api_key = api_key.strip()
        self.model = model
        self.timeout = timeout
        self.app_title = app_title
        self.app_url = app_url

    @classmethod
    def from_env(cls, model: str = DEFAULT_OPENROUTER_MODEL) -> "OpenRouterClient":
        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        return cls(api_key=key, model=model)

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 4096,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.app_url,
            "X-Title": self.app_title,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(OPENROUTER_API_URL, json=payload, headers=headers)
        except httpx.TimeoutException as exc:
            raise LLMError("OpenRouter request timed out.") from exc
        except httpx.HTTPError as exc:
            raise LLMError(f"OpenRouter HTTP error: {exc}") from exc

        if response.status_code != 200:
            raise LLMError(
                f"OpenRouter returned HTTP {response.status_code}: {response.text[:500]}"
            )

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise LLMError("OpenRouter returned no choices.")
        message = choices[0].get("message") or {}
        text = (message.get("content") or "").strip()
        if not text:
            raise LLMError("OpenRouter returned empty content.")
        return text

    def generate_json(self, prompt: str, system: Optional[str] = None) -> Any:
        raw = self.generate(prompt, system=system)
        return parse_json_from_text(raw)
