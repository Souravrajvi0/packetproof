"""Local Ollama client for Gemma inference."""

from __future__ import annotations

import base64
import json
import re
from typing import Any, Optional

import httpx

from core.schemas import LLMError

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "gemma3:4b"
DEFAULT_TIMEOUT = 1200.0


class OllamaClient:
    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except httpx.HTTPError:
            return False

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 4096},
        }
        if system:
            payload["system"] = system
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/api/generate", json=payload)
        except httpx.ConnectError as exc:
            raise LLMError(
                "Cannot connect to Ollama. Start Ollama and pull gemma3:4b locally."
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMError("Ollama request timed out.") from exc

        if response.status_code != 200:
            raise LLMError(f"Ollama returned HTTP {response.status_code}: {response.text[:500]}")

        data = response.json()
        text = data.get("response", "")
        if not text.strip():
            raise LLMError("Ollama returned an empty response.")
        return text.strip()

    def generate_from_image(self, prompt: str, image_bytes: bytes, filename: str = "image.png") -> str:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "images": [b64],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 4096},
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/api/generate", json=payload)
        except httpx.ConnectError as exc:
            raise LLMError("Cannot connect to Ollama for image transcription.") from exc
        except httpx.TimeoutException as exc:
            raise LLMError("Ollama image request timed out.") from exc
        if response.status_code != 200:
            raise LLMError(f"Ollama image HTTP {response.status_code}: {response.text[:400]}")
        text = (response.json().get("response") or "").strip()
        if not text:
            raise LLMError(f"No text transcribed from {filename}.")
        return text

    def generate_json(self, prompt: str, system: Optional[str] = None) -> Any:
        raw = self.generate(prompt, system=system)
        return parse_json_from_text(raw)


def parse_json_from_text(text: str) -> Any:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    for opener, closer in [("{", "}"), ("[", "]")]:
        start = text.find(opener)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == opener:
                depth += 1
            elif text[i] == closer:
                depth -= 1
                if depth == 0:
                    snippet = text[start : i + 1]
                    try:
                        return json.loads(snippet)
                    except json.JSONDecodeError:
                        break
    raise LLMError("Could not parse JSON from model response.")
