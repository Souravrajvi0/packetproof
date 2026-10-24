from unittest.mock import MagicMock, patch

import pytest

from core.openrouter_client import OpenRouterClient
from core.schemas import LLMError


@patch("core.openrouter_client.httpx.Client")
def test_openrouter_generate(mock_client_cls: MagicMock) -> None:
    mock_http = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_http
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"items": []}'}}],
    }
    mock_response.text = ""
    mock_http.post.return_value = mock_response

    client = OpenRouterClient(api_key="test-key")
    raw = client.generate_json("extract", system="sys")
    assert raw == {"items": []}
    call_kwargs = mock_http.post.call_args.kwargs
    assert call_kwargs["json"]["model"] == "google/gemma-3-4b-it"


def test_openrouter_missing_key() -> None:
    with pytest.raises(LLMError):
        OpenRouterClient(api_key="")
